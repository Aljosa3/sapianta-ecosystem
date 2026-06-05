"""Stable capability identity normalization for AiGOL audits."""

from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
import json
from pathlib import Path
import re
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


AIGOL_CAPABILITY_AUDIT_NORMALIZATION_VERSION = "AIGOL_CAPABILITY_AUDIT_NORMALIZATION_V1"
NORMALIZED_MATRIX_ARTIFACT_ID = "AIGOL_CAPABILITY_NORMALIZED_MATRIX_V1"
DEFAULT_RULES_PATH = Path("governance/AIGOL_CAPABILITY_NORMALIZATION_RULES_V1.json")

STATUS_RANK = {
    "NOT_STARTED": 0,
    "PARTIAL": 1,
    "IMPLEMENTED": 2,
    "CERTIFIED": 3,
}
STATUS_ORDER = ("CERTIFIED", "IMPLEMENTED", "PARTIAL", "NOT_STARTED")


def load_normalization_rules(repository_root: str | Path | None = None) -> dict[str, Any]:
    """Load normalization rules, falling back to built-in defaults when absent."""

    if repository_root is not None:
        path = Path(repository_root) / DEFAULT_RULES_PATH
        if path.exists():
            return _load_json(path)
    return _default_rules()


def normalize_capability_identity(
    value: str,
    rules: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Normalize a raw capability key/name into stable CAPABILITY_ID."""

    active_rules = rules or _default_rules()
    raw = _require_string(value, "capability identity value")
    normalized = raw.lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    if active_rules.get("normalization_rules", {}).get("strip_aigol_prefix", True):
        normalized = re.sub(r"^aigol_", "", normalized)
    before_version = normalized
    normalized = _strip_version_suffixes(normalized, active_rules)
    version_collapsed = before_version != normalized
    before_suffix = normalized
    normalized = _strip_terminal_suffixes(normalized, active_rules)
    suffix_collapsed = before_suffix != normalized
    aliases = active_rules.get("aliases", {})
    canonical_key = aliases.get(normalized, normalized)
    capability_id = f"{active_rules.get('capability_id_prefix', 'CAPABILITY')}::{canonical_key.upper()}"
    return {
        "raw_key": raw,
        "normalized_key": normalized,
        "canonical_key": canonical_key,
        "capability_id": capability_id,
        "version_collapsed": str(version_collapsed).lower(),
        "suffix_collapsed": str(suffix_collapsed).lower(),
    }


def normalize_capability_matrix(
    matrix: dict[str, Any],
    *,
    rules: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Collapse a capability matrix onto stable capability identities."""

    active_rules = rules or _default_rules()
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for capability in matrix.get("capabilities", []):
        if not isinstance(capability, dict):
            continue
        raw_key = capability.get("capability_key") or capability.get("capability")
        identity = normalize_capability_identity(str(raw_key), active_rules)
        item = deepcopy(capability)
        item["capability_id"] = identity["capability_id"]
        item["canonical_key"] = identity["canonical_key"]
        item["normalization"] = identity
        groups[identity["capability_id"]].append(item)

    normalized_capabilities = [_merge_group(capability_id, items) for capability_id, items in groups.items()]
    normalized_capabilities.sort(key=lambda item: (item["layer"], item["canonical_name"]))
    duplicate_groups = [item for item in normalized_capabilities if item["source_count"] > 1]
    renamed = [
        {
            "capability_id": item["capability_id"],
            "canonical_name": item["canonical_name"],
            "source_names": item["source_capability_names"],
        }
        for item in duplicate_groups
        if len(item["source_capability_names"]) > 1
    ]
    version_only = [
        {
            "capability_id": item["capability_id"],
            "canonical_name": item["canonical_name"],
            "source_keys": item["source_capability_keys"],
        }
        for item in duplicate_groups
        if any(source.get("normalization", {}).get("version_collapsed") == "true" for source in item["sources"])
    ]
    counts = Counter(item["status"] for item in normalized_capabilities)
    capability_counts = {status: counts.get(status, 0) for status in STATUS_ORDER}
    capability_counts["total"] = len(normalized_capabilities)
    normalized = {
        "artifact_id": NORMALIZED_MATRIX_ARTIFACT_ID,
        "runtime_version": AIGOL_CAPABILITY_AUDIT_NORMALIZATION_VERSION,
        "source_artifact_id": matrix.get("artifact_id"),
        "status": "GENERATED_NORMALIZED_CAPABILITY_MATRIX",
        "normalization_rules_artifact": active_rules.get("artifact_id", "BUILT_IN_NORMALIZATION_RULES"),
        "capability_counts": capability_counts,
        "normalization_summary": {
            "source_capability_count": len(matrix.get("capabilities", [])),
            "normalized_capability_count": len(normalized_capabilities),
            "duplicate_groups": len(duplicate_groups),
            "renamed_capabilities": len(renamed),
            "version_only_changes": len(version_only),
            "collapsed_capabilities": len(matrix.get("capabilities", [])) - len(normalized_capabilities),
        },
        "duplicate_capability_names": [
            {
                "capability_id": item["capability_id"],
                "canonical_name": item["canonical_name"],
                "source_capability_keys": item["source_capability_keys"],
                "source_count": item["source_count"],
            }
            for item in duplicate_groups
        ],
        "renamed_capabilities": renamed,
        "version_only_changes": version_only,
        "capabilities": normalized_capabilities,
        "replay_visible": True,
    }
    normalized["normalized_matrix_hash"] = replay_hash(
        {key: value for key, value in normalized.items() if key != "normalized_matrix_hash"}
    )
    return normalized


def run_capability_normalization(
    *,
    repository_root: str | Path,
    source_matrix_path: str | Path | None = None,
    output_governance_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Generate normalized capability matrix artifact."""

    root = Path(repository_root)
    source_path = Path(source_matrix_path) if source_matrix_path is not None else root / "governance" / "AIGOL_CAPABILITY_MATRIX_V2.json"
    output_dir = Path(output_governance_dir) if output_governance_dir is not None else root / "governance"
    source_matrix = _load_json(source_path)
    rules = load_normalization_rules(root)
    normalized = normalize_capability_matrix(source_matrix, rules=rules)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "AIGOL_CAPABILITY_NORMALIZED_MATRIX_V1.json"
    output_path.write_text(json.dumps(normalized, sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return {
        "runtime_version": AIGOL_CAPABILITY_AUDIT_NORMALIZATION_VERSION,
        "normalized_matrix_path": str(output_path),
        "capability_counts": deepcopy(normalized["capability_counts"]),
        "normalization_summary": deepcopy(normalized["normalization_summary"]),
        "normalized_matrix_hash": normalized["normalized_matrix_hash"],
        "replay_visible": True,
    }


def _merge_group(capability_id: str, items: list[dict[str, Any]]) -> dict[str, Any]:
    best = max(items, key=lambda item: STATUS_RANK.get(item.get("status"), -1))
    source_keys = sorted({str(item.get("capability_key") or item.get("capability")) for item in items})
    source_names = sorted({str(item.get("capability")) for item in items if item.get("capability")})
    merged = {
        "capability_id": capability_id,
        "canonical_key": best.get("canonical_key"),
        "canonical_name": _title_from_key(str(best.get("canonical_key") or "")),
        "layer": best.get("layer"),
        "status": best.get("status"),
        "source_count": len(items),
        "source_capability_keys": source_keys,
        "source_capability_names": source_names,
        "implementation": _merge_list(items, "implementation"),
        "tests": _merge_list(items, "tests"),
        "governance": _merge_list(items, "governance"),
        "certification": _merge_list(items, "certification"),
        "replay_evidence": _merge_list(items, "replay_evidence"),
        "sources": [
            {
                "capability_key": item.get("capability_key"),
                "capability": item.get("capability"),
                "status": item.get("status"),
                "normalization": item.get("normalization"),
            }
            for item in sorted(items, key=lambda item: str(item.get("capability_key") or item.get("capability")))
        ],
    }
    merged["classification_reason"] = (
        "normalized duplicate capability group"
        if len(items) > 1
        else best.get("classification_reason", "normalized capability identity")
    )
    return merged


def _merge_list(items: list[dict[str, Any]], field: str) -> list[str]:
    values: list[str] = []
    for item in items:
        field_value = item.get(field)
        if isinstance(field_value, list):
            values.extend(str(value) for value in field_value)
    return sorted(dict.fromkeys(values))


def _strip_version_suffixes(value: str, rules: dict[str, Any]) -> str:
    result = value
    for pattern in rules.get("version_patterns", []):
        result = re.sub(pattern, "", result)
    return result


def _strip_terminal_suffixes(value: str, rules: dict[str, Any]) -> str:
    result = value
    changed = True
    suffixes = sorted(rules.get("terminal_suffixes", []), key=len, reverse=True)
    while changed:
        changed = False
        for suffix in suffixes:
            if result.endswith(suffix):
                result = result[: -len(suffix)]
                changed = True
    return result


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FailClosedRuntimeError(f"capability normalization input missing: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise FailClosedRuntimeError(f"capability normalization input is not valid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise FailClosedRuntimeError("capability normalization input must be a JSON object")
    return value


def _default_rules() -> dict[str, Any]:
    return {
        "artifact_id": "BUILT_IN_CAPABILITY_NORMALIZATION_RULES",
        "capability_id_prefix": "CAPABILITY",
        "normalization_rules": {
            "strip_aigol_prefix": True,
        },
        "version_patterns": [r"_v[0-9]+$", r"_v[0-9]+_[0-9]+$"],
        "terminal_suffixes": [
            "_runtime",
            "_model",
            "_foundation",
            "_certification",
            "_acceptance",
            "_acceptance_evidence",
            "_evidence",
            "_manifest",
            "_report",
            "_review",
            "_gap_analysis",
            "_recommendations",
            "_readiness",
            "_adr",
            "_boundary_guarantees",
        ],
        "aliases": {},
    }


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _title_from_key(key: str) -> str:
    acronyms = {"aigol": "AiGOL", "ocs": "OCS", "llm": "LLM", "cli": "CLI", "api": "API"}
    return " ".join(acronyms.get(word, word.capitalize()) for word in key.split("_") if word)


def main(argv: list[str] | None = None) -> int:
    args = argv or []
    root = Path(args[0]) if args else Path.cwd()
    matrix = Path(args[1]) if len(args) > 1 else root / "governance" / "AIGOL_CAPABILITY_MATRIX_V2.json"
    output = Path(args[2]) if len(args) > 2 else root / "governance"
    run_capability_normalization(repository_root=root, source_matrix_path=matrix, output_governance_dir=output)
    return 0


__all__ = [
    "AIGOL_CAPABILITY_AUDIT_NORMALIZATION_VERSION",
    "NORMALIZED_MATRIX_ARTIFACT_ID",
    "load_normalization_rules",
    "main",
    "normalize_capability_identity",
    "normalize_capability_matrix",
    "run_capability_normalization",
]


if __name__ == "__main__":
    raise SystemExit(main())
