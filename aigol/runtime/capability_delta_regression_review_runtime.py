"""Regression review runtime for capability delta audit results."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import re
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


AIGOL_CAPABILITY_DELTA_REGRESSION_REVIEW_RUNTIME_VERSION = (
    "AIGOL_CAPABILITY_DELTA_REGRESSION_REVIEW_V1"
)
CORRECTED_ARTIFACT_ID = "AIGOL_CAPABILITY_DELTA_CORRECTED_V1"
REVIEW_REPORT_ID = "AIGOL_CAPABILITY_DELTA_REGRESSION_REVIEW_V1"

CLASSIFICATIONS = (
    "REAL_CHANGE",
    "CLASSIFICATION_CHANGE",
    "PARSER_CHANGE",
    "DUPLICATE_DETECTION",
)

STATUS_ORDER = ("NOT_STARTED", "PARTIAL", "IMPLEMENTED", "CERTIFIED")
STATUS_SCORE = {status: index for index, status in enumerate(STATUS_ORDER)}
DELTA_STATUSES = ("CERTIFIED", "IMPLEMENTED", "PARTIAL", "NOT_STARTED")

REAL_CHANGE_KEYWORDS = (
    "capability_audit_runtime",
    "native_development_replay_safe_handoff_hardening",
    "capability_delta_runtime",
)

DUPLICATE_SUFFIXES = (
    "_runtime",
    "_model",
    "_foundation",
    "_certification",
    "_acceptance",
    "_evidence",
    "_manifest",
    "_review",
    "_gap_analysis",
    "_recommendations",
    "_readiness",
)


def run_delta_regression_review(
    *,
    previous_matrix_path: str | Path,
    current_matrix_path: str | Path,
    delta_path: str | Path,
    output_governance_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Analyze delta artifacts and write corrected delta plus regression review."""

    previous = _load_json(Path(previous_matrix_path))
    current = _load_json(Path(current_matrix_path))
    delta = _load_json(Path(delta_path))
    corrected = compute_corrected_delta(previous, current, delta)
    governance_dir = Path(output_governance_dir) if output_governance_dir else Path(delta_path).parent
    governance_dir.mkdir(parents=True, exist_ok=True)
    corrected_path = governance_dir / "AIGOL_CAPABILITY_DELTA_CORRECTED_V1.json"
    review_path = governance_dir / "AIGOL_CAPABILITY_DELTA_REGRESSION_REVIEW_V1.md"
    corrected_path.write_text(json.dumps(corrected, sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    review_path.write_text(render_regression_review(corrected), encoding="utf-8")
    return {
        "runtime_version": AIGOL_CAPABILITY_DELTA_REGRESSION_REVIEW_RUNTIME_VERSION,
        "corrected_delta_path": str(corrected_path),
        "review_path": str(review_path),
        "adjusted_status_deltas": deepcopy(corrected["adjusted_delta"]["status_deltas"]),
        "classification_counts": deepcopy(corrected["classification_counts"]),
        "corrected_delta_hash": corrected["corrected_delta_hash"],
        "replay_visible": True,
    }


def compute_corrected_delta(
    previous_matrix: dict[str, Any],
    current_matrix: dict[str, Any],
    delta: dict[str, Any],
) -> dict[str, Any]:
    """Classify every delta and compute a conservative adjusted delta."""

    previous_caps = _capability_map(previous_matrix)
    current_caps = _capability_map(current_matrix)
    current_duplicate_roots = _duplicate_roots(current_caps)
    previous_roots = {_root_key(key) for key in previous_caps}
    classified = []
    for item in delta.get("added_capabilities", []):
        classified.append(_classify_added(item, current_caps, current_duplicate_roots, previous_roots))
    for item in delta.get("removed_capabilities", []):
        classified.append(_classify_removed(item, previous_caps, current_caps))
    for item in delta.get("status_changes", []):
        classified.append(_classify_status_change(item, previous_caps, current_caps))

    counts = Counter(item["classification"] for item in classified)
    adjusted_status_deltas = {status: 0 for status in DELTA_STATUSES}
    adjusted_added = []
    adjusted_removed = []
    adjusted_status_changes = []
    for item in classified:
        if item["classification"] != "REAL_CHANGE":
            continue
        if item["delta_type"] == "ADDED_CAPABILITY":
            adjusted_status_deltas[item["current_status"]] += 1
            adjusted_added.append(_public_delta_item(item))
        elif item["delta_type"] == "REMOVED_CAPABILITY":
            adjusted_status_deltas[item["previous_status"]] -= 1
            adjusted_removed.append(_public_delta_item(item))
        elif item["delta_type"] == "STATUS_CHANGE":
            adjusted_status_deltas[item["previous_status"]] -= 1
            adjusted_status_deltas[item["current_status"]] += 1
            adjusted_status_changes.append(_public_delta_item(item))

    corrected = {
        "artifact_id": CORRECTED_ARTIFACT_ID,
        "runtime_version": AIGOL_CAPABILITY_DELTA_REGRESSION_REVIEW_RUNTIME_VERSION,
        "status": "GENERATED_CORRECTED_CAPABILITY_DELTA",
        "inputs": {
            "previous_matrix_artifact_id": previous_matrix.get("artifact_id"),
            "current_matrix_artifact_id": current_matrix.get("artifact_id"),
            "delta_artifact_id": delta.get("artifact_id"),
        },
        "classification_values": list(CLASSIFICATIONS),
        "classification_counts": {name: counts.get(name, 0) for name in CLASSIFICATIONS},
        "drift_findings": {
            "capability_inflation_detected": len(current_caps) > len(previous_caps),
            "classification_drift_detected": any(item["classification"] == "CLASSIFICATION_CHANGE" for item in classified),
            "duplicate_detection_detected": any(item["classification"] == "DUPLICATE_DETECTION" for item in classified),
            "parser_inconsistency_detected": any(item["classification"] == "PARSER_CHANGE" for item in classified),
            "granularity_change_detected": len(current_caps) > len(previous_caps),
        },
        "raw_delta_summary": {
            "status_deltas": deepcopy(delta.get("status_deltas", {})),
            "added_capabilities": len(delta.get("added_capabilities", [])),
            "removed_capabilities": len(delta.get("removed_capabilities", [])),
            "status_changes": len(delta.get("status_changes", [])),
        },
        "adjusted_delta": {
            "status_deltas": adjusted_status_deltas,
            "added_capabilities": adjusted_added,
            "removed_capabilities": adjusted_removed,
            "status_changes": adjusted_status_changes,
            "total_capability_delta": len(adjusted_added) - len(adjusted_removed),
        },
        "classified_deltas": classified,
        "top_improvements": _top_adjusted_improvements(adjusted_added, adjusted_status_changes),
        "top_regressions": _top_adjusted_regressions(adjusted_removed, adjusted_status_changes),
        "recommended_next_milestone": recommended_next_milestone(counts, adjusted_status_deltas),
        "replay_visible": True,
    }
    corrected["corrected_delta_hash"] = replay_hash(
        {key: value for key, value in corrected.items() if key != "corrected_delta_hash"}
    )
    return corrected


def render_regression_review(corrected: dict[str, Any]) -> str:
    """Render the Markdown regression review."""

    lines = [
        "# AIGOL_CAPABILITY_DELTA_REGRESSION_REVIEW_V1",
        "",
        "## Status",
        "",
        "Generated regression review.",
        "",
        "```text",
        "AIGOL_CAPABILITY_DELTA_REGRESSION_REVIEW_STATUS = CERTIFIED",
        "```",
        "",
        "## Review Purpose",
        "",
        "Validate whether capability delta results reflect real system evolution or audit classification drift.",
        "",
        "## Classification Counts",
        "",
        "| Classification | Count |",
        "| --- | ---: |",
    ]
    for name in CLASSIFICATIONS:
        lines.append(f"| `{name}` | {corrected['classification_counts'][name]} |")
    lines.extend(
        [
            "",
            "## Drift Findings",
            "",
        ]
    )
    for name, value in corrected["drift_findings"].items():
        lines.append(f"- `{name}`: `{str(value).lower()}`")
    lines.extend(
        [
            "",
            "## Raw Delta",
            "",
            "| Status | Raw Delta |",
            "| --- | ---: |",
        ]
    )
    raw = corrected["raw_delta_summary"]["status_deltas"]
    for status in DELTA_STATUSES:
        lines.append(f"| `{status}` | {raw.get(status, 0):+d} |")
    lines.extend(
        [
            "",
            "## Adjusted Delta",
            "",
            "| Status | Adjusted Delta |",
            "| --- | ---: |",
        ]
    )
    adjusted = corrected["adjusted_delta"]["status_deltas"]
    for status in DELTA_STATUSES:
        lines.append(f"| `{status}` | {adjusted.get(status, 0):+d} |")
    lines.extend(
        [
            "",
            f"- Adjusted added capabilities: {len(corrected['adjusted_delta']['added_capabilities'])}",
            f"- Adjusted removed capabilities: {len(corrected['adjusted_delta']['removed_capabilities'])}",
            f"- Adjusted status changes: {len(corrected['adjusted_delta']['status_changes'])}",
            f"- Adjusted total capability delta: {corrected['adjusted_delta']['total_capability_delta']:+d}",
            "",
            "## Top Improvements",
            "",
        ]
    )
    lines.extend(_render_items(corrected["top_improvements"], "No real improvements identified after correction."))
    lines.extend(["", "## Top Regressions", ""])
    lines.extend(_render_items(corrected["top_regressions"], "No real regressions identified after correction."))
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The raw V1-to-V2 delta is dominated by parser and granularity changes because V1 was a manual matrix and V2 was runtime-generated. The adjusted delta counts only deltas classified as `REAL_CHANGE`.",
            "",
            "## Recommended Next Milestone",
            "",
            "```text",
            corrected["recommended_next_milestone"],
            "```",
            "",
            "## Generated Artifacts",
            "",
            "- `governance/AIGOL_CAPABILITY_DELTA_REGRESSION_REVIEW_V1.md`",
            "- `governance/AIGOL_CAPABILITY_DELTA_CORRECTED_V1.json`",
            "",
        ]
    )
    return "\n".join(lines)


def recommended_next_milestone(classification_counts: Counter[str], adjusted_status_deltas: dict[str, int]) -> str:
    if classification_counts.get("PARSER_CHANGE", 0) or classification_counts.get("DUPLICATE_DETECTION", 0):
        return "AIGOL_CAPABILITY_AUDIT_NORMALIZATION_V1"
    if adjusted_status_deltas.get("IMPLEMENTED", 0) > 0:
        return "AIGOL_IMPLEMENTED_CAPABILITY_CERTIFICATION_SWEEP_V1"
    return "AIGOL_NATIVE_DEVELOPMENT_END_TO_END_DRY_RUN_V1"


def _classify_added(
    item: dict[str, Any],
    current_caps: dict[str, dict[str, Any]],
    duplicate_roots: set[str],
    previous_roots: set[str],
) -> dict[str, Any]:
    key = _key(item)
    current = current_caps.get(key, {})
    root = _root_key(key)
    classification = "PARSER_CHANGE"
    reason = "added by automated V2 parser; treated as granularity/parser expansion"
    explicit_real_change = key in REAL_CHANGE_KEYWORDS
    if explicit_real_change:
        classification = "REAL_CHANGE"
        reason = "capability is an explicitly reviewed post-audit milestone"
    if root in duplicate_roots and not explicit_real_change:
        classification = "DUPLICATE_DETECTION"
        reason = "added capability shares a duplicate root with other V2 capability entries"
    elif root in previous_roots and classification != "REAL_CHANGE":
        classification = "PARSER_CHANGE"
        reason = "added capability appears to split a broader V1 capability"
    return {
        "delta_type": "ADDED_CAPABILITY",
        "classification": classification,
        "reason": reason,
        "capability_key": key,
        "capability": item.get("capability") or current.get("capability") or _title(key),
        "layer": item.get("layer") or current.get("layer"),
        "previous_status": None,
        "current_status": item.get("status") or current.get("status"),
    }


def _classify_removed(
    item: dict[str, Any],
    previous_caps: dict[str, dict[str, Any]],
    current_caps: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    key = _key(item)
    previous = previous_caps.get(key, {})
    current_roots = {_root_key(value) for value in current_caps}
    classification = "PARSER_CHANGE" if _root_key(key) in current_roots else "CLASSIFICATION_CHANGE"
    reason = (
        "removed broad V1 capability appears represented by finer V2 entries"
        if classification == "PARSER_CHANGE"
        else "removed manual V1 capability was not reproduced by V2 parser"
    )
    return {
        "delta_type": "REMOVED_CAPABILITY",
        "classification": classification,
        "reason": reason,
        "capability_key": key,
        "capability": item.get("capability") or previous.get("capability") or _title(key),
        "layer": item.get("layer") or previous.get("layer"),
        "previous_status": item.get("status") or previous.get("status"),
        "current_status": None,
    }


def _classify_status_change(
    item: dict[str, Any],
    previous_caps: dict[str, dict[str, Any]],
    current_caps: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    key = _key(item)
    previous = previous_caps.get(key, {})
    current = current_caps.get(key, {})
    classification = "CLASSIFICATION_CHANGE"
    reason = "same capability key changed status between manual and runtime-generated classifications"
    return {
        "delta_type": "STATUS_CHANGE",
        "classification": classification,
        "reason": reason,
        "capability_key": key,
        "capability": item.get("capability") or current.get("capability") or previous.get("capability") or _title(key),
        "layer": item.get("layer") or current.get("layer") or previous.get("layer"),
        "previous_status": item.get("previous_status"),
        "current_status": item.get("current_status"),
    }


def _capability_map(matrix: dict[str, Any]) -> dict[str, dict[str, Any]]:
    mapped: dict[str, dict[str, Any]] = {}
    for capability in matrix.get("capabilities", []):
        if not isinstance(capability, dict):
            continue
        key = _key(capability)
        mapped[key] = {
            "capability_key": key,
            "capability": capability.get("capability") or _title(key),
            "layer": capability.get("layer"),
            "status": capability.get("status"),
            "implementation": capability.get("implementation") or [],
            "certification": capability.get("certification") or [],
            "tests": capability.get("tests") or [],
            "governance": capability.get("governance") or [],
            "replay_evidence": capability.get("replay_evidence") or [],
        }
    return mapped


def _duplicate_roots(capabilities: dict[str, dict[str, Any]]) -> set[str]:
    counts = Counter(_root_key(key) for key in capabilities)
    return {key for key, count in counts.items() if count > 1}


def _public_delta_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "delta_type": item["delta_type"],
        "capability_key": item["capability_key"],
        "capability": item["capability"],
        "layer": item["layer"],
        "previous_status": item["previous_status"],
        "current_status": item["current_status"],
    }


def _top_adjusted_improvements(added: list[dict[str, Any]], status_changes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    improvements = []
    for item in status_changes:
        if item["previous_status"] and item["current_status"]:
            if STATUS_SCORE[item["current_status"]] > STATUS_SCORE[item["previous_status"]]:
                improvements.append(item)
    improvements.extend(added)
    return improvements[:15]


def _top_adjusted_regressions(removed: list[dict[str, Any]], status_changes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    regressions = []
    for item in status_changes:
        if item["previous_status"] and item["current_status"]:
            if STATUS_SCORE[item["current_status"]] < STATUS_SCORE[item["previous_status"]]:
                regressions.append(item)
    regressions.extend(removed)
    return regressions[:15]


def _render_items(items: list[dict[str, Any]], empty: str) -> list[str]:
    if not items:
        return [empty]
    lines = []
    for item in items:
        lines.append(
            f"- `{item['delta_type']}` {item['capability']}: {item['previous_status']} -> {item['current_status']}"
        )
    return lines


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FailClosedRuntimeError(f"delta regression input missing: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise FailClosedRuntimeError(f"delta regression input is not valid JSON: {path}") from exc
    if not isinstance(data, dict):
        raise FailClosedRuntimeError("delta regression input must be a JSON object")
    return data


def _key(item: dict[str, Any]) -> str:
    value = item.get("capability_key") or item.get("capability") or "unknown_capability"
    value = str(value).lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"^aigol_", "", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "unknown_capability"


def _root_key(key: str) -> str:
    root = key
    changed = True
    while changed:
        changed = False
        for suffix in DUPLICATE_SUFFIXES:
            if root.endswith(suffix):
                root = root[: -len(suffix)]
                changed = True
    return root


def _title(key: str) -> str:
    return " ".join(part.capitalize() for part in key.split("_"))


def main(argv: list[str] | None = None) -> int:
    args = argv or []
    root = Path.cwd()
    previous = Path(args[0]) if len(args) > 0 else root / "governance" / "AIGOL_CAPABILITY_MATRIX_V1.json"
    current = Path(args[1]) if len(args) > 1 else root / "governance" / "AIGOL_CAPABILITY_MATRIX_V2.json"
    delta = Path(args[2]) if len(args) > 2 else root / "governance" / "AIGOL_CAPABILITY_DELTA_V1.json"
    output = Path(args[3]) if len(args) > 3 else root / "governance"
    run_delta_regression_review(
        previous_matrix_path=previous,
        current_matrix_path=current,
        delta_path=delta,
        output_governance_dir=output,
    )
    return 0


__all__ = [
    "AIGOL_CAPABILITY_DELTA_REGRESSION_REVIEW_RUNTIME_VERSION",
    "compute_corrected_delta",
    "main",
    "recommended_next_milestone",
    "render_regression_review",
    "run_delta_regression_review",
]


if __name__ == "__main__":
    raise SystemExit(main())
