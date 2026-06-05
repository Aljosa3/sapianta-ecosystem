"""Capability delta runtime for comparing AiGOL capability audit matrices."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import re
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


AIGOL_CAPABILITY_DELTA_RUNTIME_VERSION = "AIGOL_CAPABILITY_DELTA_RUNTIME_V1"
DELTA_ARTIFACT_ID = "AIGOL_CAPABILITY_DELTA_V1"
DELTA_REPORT_ID = "AIGOL_CAPABILITY_DELTA_REPORT_V1"

STATUS_ORDER = ("NOT_STARTED", "PARTIAL", "IMPLEMENTED", "CERTIFIED")
STATUS_SCORE = {status: index for index, status in enumerate(STATUS_ORDER)}
DELTA_STATUSES = ("CERTIFIED", "IMPLEMENTED", "PARTIAL", "NOT_STARTED")

LAYER_ORDER = (
    "L1 Governance",
    "L2 Cognition",
    "L3 Provider/Worker",
    "L4 Execution",
    "L5 Implementation",
    "L6 Domain Runtime",
    "L7 Marketplace",
)

LAYER_ALIASES = {
    "L2 Cognition (OCS)": "L2 Cognition",
    "L5 Implementation Generation": "L5 Implementation",
    "L7 Marketplace / Ecosystem": "L7 Marketplace",
}


def run_capability_delta(
    *,
    previous_matrix_path: str | Path,
    current_matrix_path: str | Path,
    output_governance_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Compute and write capability delta artifacts."""

    previous_path = Path(previous_matrix_path)
    current_path = Path(current_matrix_path)
    previous = _load_matrix(previous_path)
    current = _load_matrix(current_path)
    delta = compute_capability_delta(previous, current)
    governance_dir = Path(output_governance_dir) if output_governance_dir else current_path.parent
    governance_dir.mkdir(parents=True, exist_ok=True)
    delta_path = governance_dir / "AIGOL_CAPABILITY_DELTA_V1.json"
    report_path = governance_dir / "AIGOL_CAPABILITY_DELTA_REPORT_V1.md"
    delta_path.write_text(json.dumps(delta, sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    report_path.write_text(render_delta_report(delta), encoding="utf-8")
    return {
        "runtime_version": AIGOL_CAPABILITY_DELTA_RUNTIME_VERSION,
        "delta_path": str(delta_path),
        "report_path": str(report_path),
        "status_deltas": deepcopy(delta["status_deltas"]),
        "added_count": len(delta["added_capabilities"]),
        "removed_count": len(delta["removed_capabilities"]),
        "status_change_count": len(delta["status_changes"]),
        "delta_hash": delta["delta_hash"],
        "replay_visible": True,
    }


def compute_capability_delta(previous_matrix: dict[str, Any], current_matrix: dict[str, Any]) -> dict[str, Any]:
    """Compute added, removed, status, maturity, and layer score deltas."""

    previous_caps = _capability_map(previous_matrix)
    current_caps = _capability_map(current_matrix)
    previous_keys = set(previous_caps)
    current_keys = set(current_caps)
    added_keys = sorted(current_keys - previous_keys)
    removed_keys = sorted(previous_keys - current_keys)
    shared_keys = sorted(previous_keys & current_keys)

    added = [_capability_summary(current_caps[key]) for key in added_keys]
    removed = [_capability_summary(previous_caps[key]) for key in removed_keys]
    status_changes = []
    for key in shared_keys:
        before = previous_caps[key]
        after = current_caps[key]
        if before["status"] != after["status"]:
            before_score = STATUS_SCORE[before["status"]]
            after_score = STATUS_SCORE[after["status"]]
            status_changes.append(
                {
                    "capability_key": key,
                    "capability": after["capability"],
                    "layer": after["layer"],
                    "previous_status": before["status"],
                    "current_status": after["status"],
                    "status_delta": after_score - before_score,
                    "direction": "IMPROVED" if after_score > before_score else "REGRESSED",
                }
            )
    status_changes.sort(key=lambda item: (item["direction"], -abs(item["status_delta"]), item["capability"]))

    previous_counts = _counts(previous_matrix, previous_caps)
    current_counts = _counts(current_matrix, current_caps)
    status_deltas = {
        status: current_counts.get(status, 0) - previous_counts.get(status, 0)
        for status in DELTA_STATUSES
    }
    previous_scores = _normalized_layer_scores(previous_matrix)
    current_scores = _normalized_layer_scores(current_matrix)
    layer_score_deltas = {
        layer: {
            "previous_score": previous_scores.get(layer, 0),
            "current_score": current_scores.get(layer, 0),
            "delta": current_scores.get(layer, 0) - previous_scores.get(layer, 0),
        }
        for layer in LAYER_ORDER
    }
    maturity_changes = {
        "previous_total": previous_counts.get("total", len(previous_caps)),
        "current_total": current_counts.get("total", len(current_caps)),
        "total_delta": current_counts.get("total", len(current_caps)) - previous_counts.get("total", len(previous_caps)),
        "previous_certified_ratio": _ratio(previous_counts.get("CERTIFIED", 0), previous_counts.get("total", len(previous_caps))),
        "current_certified_ratio": _ratio(current_counts.get("CERTIFIED", 0), current_counts.get("total", len(current_caps))),
    }
    maturity_changes["certified_ratio_delta"] = round(
        maturity_changes["current_certified_ratio"] - maturity_changes["previous_certified_ratio"], 4
    )
    improvements = _top_improvements(added, status_changes, layer_score_deltas)
    regressions = _top_regressions(removed, status_changes, layer_score_deltas)
    delta = {
        "artifact_id": DELTA_ARTIFACT_ID,
        "runtime_version": AIGOL_CAPABILITY_DELTA_RUNTIME_VERSION,
        "status": "GENERATED_CAPABILITY_DELTA",
        "inputs": {
            "previous_artifact_id": previous_matrix.get("artifact_id"),
            "current_artifact_id": current_matrix.get("artifact_id"),
        },
        "status_deltas": status_deltas,
        "added_capabilities": added,
        "removed_capabilities": removed,
        "status_changes": status_changes,
        "maturity_changes": maturity_changes,
        "layer_score_deltas": layer_score_deltas,
        "top_improvements": improvements,
        "top_regressions": regressions,
        "recommended_next_milestone": recommended_next_milestone(status_deltas, layer_score_deltas, regressions),
        "replay_visible": True,
    }
    delta["delta_hash"] = replay_hash({key: value for key, value in delta.items() if key != "delta_hash"})
    return delta


def render_delta_report(delta: dict[str, Any]) -> str:
    """Render a concise Markdown delta report."""

    lines = [
        "# AIGOL_CAPABILITY_DELTA_REPORT_V1",
        "",
        "## Status",
        "",
        "Generated by `AIGOL_CAPABILITY_DELTA_RUNTIME_V1`.",
        "",
        "```text",
        "AIGOL_CAPABILITY_DELTA_REPORT_STATUS = GENERATED",
        "```",
        "",
        "## Status Deltas",
        "",
        "| Status | Delta |",
        "| --- | ---: |",
    ]
    for status in DELTA_STATUSES:
        lines.append(f"| `{status}` | {delta['status_deltas'][status]:+d} |")
    lines.extend(
        [
            "",
            "## Capability Movement",
            "",
            f"- Added capabilities: {len(delta['added_capabilities'])}",
            f"- Removed capabilities: {len(delta['removed_capabilities'])}",
            f"- Status changes: {len(delta['status_changes'])}",
            f"- Total capability delta: {delta['maturity_changes']['total_delta']:+d}",
            f"- Certified ratio delta: {delta['maturity_changes']['certified_ratio_delta']:+.4f}",
            "",
            "## Layer Score Deltas",
            "",
            "| Layer | Previous | Current | Delta |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for layer in LAYER_ORDER:
        item = delta["layer_score_deltas"][layer]
        lines.append(f"| {layer} | {item['previous_score']} | {item['current_score']} | {item['delta']:+d} |")
    lines.extend(["", "## Top Improvements", ""])
    lines.extend(_report_items(delta["top_improvements"], empty="No improvements detected."))
    lines.extend(["", "## Top Regressions", ""])
    lines.extend(_report_items(delta["top_regressions"], empty="No regressions detected."))
    lines.extend(
        [
            "",
            "## Recommended Next Milestone",
            "",
            "```text",
            delta["recommended_next_milestone"],
            "```",
            "",
            "## Generated Artifacts",
            "",
            "- `governance/AIGOL_CAPABILITY_DELTA_REPORT_V1.md`",
            "- `governance/AIGOL_CAPABILITY_DELTA_V1.json`",
            "",
        ]
    )
    return "\n".join(lines)


def recommended_next_milestone(
    status_deltas: dict[str, int],
    layer_score_deltas: dict[str, dict[str, int]],
    regressions: list[dict[str, Any]],
) -> str:
    """Select a conservative next milestone from delta signals."""

    if regressions:
        return "AIGOL_CAPABILITY_DELTA_REGRESSION_REVIEW_V1"
    if status_deltas.get("IMPLEMENTED", 0) > 0:
        return "AIGOL_IMPLEMENTED_CAPABILITY_CERTIFICATION_SWEEP_V1"
    weakest_layer = min(layer_score_deltas.items(), key=lambda item: item[1]["current_score"])[0]
    if weakest_layer == "L7 Marketplace":
        return "AIGOL_MARKETPLACE_ECOSYSTEM_READINESS_HARDENING_V1"
    return "AIGOL_NATIVE_DEVELOPMENT_END_TO_END_DRY_RUN_V1"


def _load_matrix(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FailClosedRuntimeError(f"capability matrix missing: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise FailClosedRuntimeError(f"capability matrix is not valid JSON: {path}") from exc
    if not isinstance(value, dict) or not isinstance(value.get("capabilities"), list):
        raise FailClosedRuntimeError("capability matrix must contain capabilities list")
    return value


def _capability_map(matrix: dict[str, Any]) -> dict[str, dict[str, Any]]:
    mapped = {}
    for capability in matrix.get("capabilities", []):
        if not isinstance(capability, dict):
            continue
        key = _capability_key(capability)
        status = capability.get("status")
        if status not in STATUS_SCORE:
            continue
        mapped[key] = {
            "capability_key": key,
            "capability": capability.get("capability") or _title_from_key(key),
            "layer": _normalize_layer(capability.get("layer")),
            "status": status,
        }
    return mapped


def _counts(matrix: dict[str, Any], capabilities: dict[str, dict[str, Any]]) -> dict[str, int]:
    counts = {status: 0 for status in DELTA_STATUSES}
    for capability in capabilities.values():
        counts[capability["status"]] += 1
    counts["total"] = len(capabilities)
    return counts


def _normalized_layer_scores(matrix: dict[str, Any]) -> dict[str, int]:
    raw = matrix.get("layer_maturity_scores", {})
    scores = {layer: 0 for layer in LAYER_ORDER}
    if isinstance(raw, dict):
        for layer, score in raw.items():
            normalized = _normalize_layer(layer)
            if normalized in scores and isinstance(score, int):
                scores[normalized] = score
    return scores


def _capability_summary(capability: dict[str, Any]) -> dict[str, str]:
    return {
        "capability_key": capability["capability_key"],
        "capability": capability["capability"],
        "layer": capability["layer"],
        "status": capability["status"],
    }


def _top_improvements(
    added: list[dict[str, str]],
    status_changes: list[dict[str, Any]],
    layer_score_deltas: dict[str, dict[str, int]],
) -> list[dict[str, Any]]:
    improvements: list[dict[str, Any]] = []
    for change in status_changes:
        if change["direction"] == "IMPROVED":
            improvements.append({"type": "STATUS_IMPROVEMENT", **change})
    for capability in added[:20]:
        improvements.append({"type": "ADDED_CAPABILITY", **capability})
    for layer, item in layer_score_deltas.items():
        if item["delta"] > 0:
            improvements.append({"type": "LAYER_SCORE_IMPROVEMENT", "layer": layer, "delta": item["delta"]})
    return sorted(improvements, key=lambda item: (-abs(item.get("status_delta", item.get("delta", 1))), item.get("capability", item.get("layer", ""))))[:15]


def _top_regressions(
    removed: list[dict[str, str]],
    status_changes: list[dict[str, Any]],
    layer_score_deltas: dict[str, dict[str, int]],
) -> list[dict[str, Any]]:
    regressions: list[dict[str, Any]] = []
    for change in status_changes:
        if change["direction"] == "REGRESSED":
            regressions.append({"type": "STATUS_REGRESSION", **change})
    for capability in removed[:20]:
        regressions.append({"type": "REMOVED_CAPABILITY", **capability})
    for layer, item in layer_score_deltas.items():
        if item["delta"] < 0:
            regressions.append({"type": "LAYER_SCORE_REGRESSION", "layer": layer, "delta": item["delta"]})
    return sorted(regressions, key=lambda item: (item.get("status_delta", item.get("delta", -1)), item.get("capability", item.get("layer", ""))))[:15]


def _report_items(items: list[dict[str, Any]], *, empty: str) -> list[str]:
    if not items:
        return [empty]
    lines = []
    for item in items:
        if item["type"].startswith("LAYER_SCORE"):
            lines.append(f"- `{item['type']}` {item['layer']}: {item['delta']:+d}")
        elif "previous_status" in item:
            lines.append(
                f"- `{item['type']}` {item['capability']}: {item['previous_status']} -> {item['current_status']}"
            )
        else:
            lines.append(f"- `{item['type']}` {item['capability']} ({item['status']})")
    return lines


def _capability_key(capability: dict[str, Any]) -> str:
    if isinstance(capability.get("capability_key"), str) and capability["capability_key"].strip():
        return _normalize_key(capability["capability_key"])
    return _normalize_key(str(capability.get("capability", "unknown_capability")))


def _normalize_key(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"^aigol_", "", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "unknown_capability"


def _normalize_layer(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        return "L1 Governance"
    return LAYER_ALIASES.get(value, value)


def _title_from_key(key: str) -> str:
    return " ".join(word.capitalize() for word in key.split("_"))


def _ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 4)


def main(argv: list[str] | None = None) -> int:
    args = argv or []
    root = Path.cwd()
    previous = Path(args[0]) if len(args) > 0 else root / "governance" / "AIGOL_CAPABILITY_MATRIX_V1.json"
    current = Path(args[1]) if len(args) > 1 else root / "governance" / "AIGOL_CAPABILITY_MATRIX_V2.json"
    output = Path(args[2]) if len(args) > 2 else root / "governance"
    run_capability_delta(previous_matrix_path=previous, current_matrix_path=current, output_governance_dir=output)
    return 0


__all__ = [
    "AIGOL_CAPABILITY_DELTA_RUNTIME_VERSION",
    "compute_capability_delta",
    "main",
    "recommended_next_milestone",
    "render_delta_report",
    "run_capability_delta",
]


if __name__ == "__main__":
    raise SystemExit(main())
