"""Repeatable capability audit runtime for AiGOL."""

from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any

from aigol.runtime.capability_normalization_runtime import (
    load_normalization_rules,
    normalize_capability_identity,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


AIGOL_CAPABILITY_AUDIT_RUNTIME_VERSION = "AIGOL_CAPABILITY_AUDIT_RUNTIME_V1"
MATRIX_ARTIFACT_ID = "AIGOL_CAPABILITY_MATRIX_V2"
AUDIT_DOCUMENT_ID = "AIGOL_CAPABILITY_AUDIT_V2"
ROADMAP_DOCUMENT_ID = "AIGOL_ROADMAP_POST_AUDIT_V2"
SUMMARY_DOCUMENT_ID = "AIGOL_CAPABILITY_AUDIT_REPORT_SUMMARY_V1"

STATUS_ORDER = ("CERTIFIED", "IMPLEMENTED", "PARTIAL", "NOT_STARTED")
STATUS_SCORE = {"CERTIFIED": 100, "IMPLEMENTED": 75, "PARTIAL": 45, "NOT_STARTED": 0}

CANONICAL_LAYERS = (
    "L1 Governance",
    "L2 Cognition (OCS)",
    "L3 Provider/Worker",
    "L4 Execution",
    "L5 Implementation Generation",
    "L6 Domain Runtime",
    "L7 Marketplace / Ecosystem",
)

OPERATOR_LAYER_LABELS = {
    "L1 Governance": "Governance",
    "L2 Cognition (OCS)": "OCS / Cognition",
    "L3 Provider/Worker": "Provider / Worker",
    "L4 Execution": "Execution",
    "L5 Implementation Generation": "Implementation Generation",
    "L6 Domain Runtime": "Domain Runtime",
    "L7 Marketplace / Ecosystem": "Marketplace / Ecosystem",
}

SCANNED_DIRECTORIES = (
    "governance/",
    "aigol/runtime/",
    "tests/",
)

KNOWN_NOT_STARTED = {
    "autonomous_code_mutation_without_human_authority": {
        "capability": "Autonomous code mutation without human authority",
        "layer": "L5 Implementation Generation",
        "reason": "Constitutionally forbidden; preserved as explicit non-goal rather than implemented capability.",
        "evidence_keywords": ("ANTI_AGENTIC", "EXECUTION_AUTHORITY", "NATIVE_DEVELOPMENT_FAILURE"),
    },
    "marketplace_discovery_packaging_and_commercial_listing": {
        "capability": "Marketplace discovery, packaging, and commercial listing",
        "layer": "L7 Marketplace / Ecosystem",
        "reason": "Marketplace ecosystem artifacts are readiness/planning only; no marketplace runtime was detected.",
        "evidence_keywords": ("MARKETPLACE", "WORKER_ECOSYSTEM", "PROVIDER_ECOSYSTEM"),
    },
    "enterprise_tenant_organization_and_billing_governance": {
        "capability": "Enterprise tenant, organization, and billing governance",
        "layer": "L7 Marketplace / Ecosystem",
        "reason": "Semantic exposure and capability governance exist, but no tenant, billing, or entitlement runtime was detected.",
        "evidence_keywords": ("SEMANTIC_EXPOSURE", "CAPABILITY_GOVERNANCE_MATRIX"),
    },
    "external_partner_onboarding_and_certification_workflow": {
        "capability": "External partner onboarding and certification workflow",
        "layer": "L7 Marketplace / Ecosystem",
        "reason": "External attachment evidence exists, but no complete partner onboarding workflow runtime was detected.",
        "evidence_keywords": ("EXTERNAL_LLM", "EXTERNAL_WORKER"),
    },
}

PARTIAL_HINTS = (
    "GAP",
    "READINESS",
    "RECOMMENDATION",
    "RECOMMENDED",
    "FINDINGS",
    "REVIEW",
    "FAILURE",
    "PARTIAL",
    "MISSING",
)

CERTIFICATION_HINTS = ("CERTIFICATION", "CERTIFIED")
EVIDENCE_HINTS = ("EVIDENCE", "ACCEPTANCE", "REPLAY", "MANIFEST", "REPORT")


def run_capability_audit(
    *,
    repository_root: str | Path,
    output_governance_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Scan repository evidence and write V2 capability audit artifacts."""

    root = Path(repository_root)
    if not root.exists():
        raise FailClosedRuntimeError("capability audit repository root missing")
    governance_dir = Path(output_governance_dir) if output_governance_dir is not None else root / "governance"
    governance_dir.mkdir(parents=True, exist_ok=True)

    detected = detect_capabilities(root)
    matrix = build_capability_matrix(detected, normalization_rules=load_normalization_rules(root))
    audit_md = render_audit_document(matrix)
    roadmap_md = render_roadmap_document(matrix)
    summary = build_audit_report_summary(matrix, repository_root=root)
    summary_md = render_audit_report_summary(summary)

    matrix_path = governance_dir / "AIGOL_CAPABILITY_MATRIX_V2.json"
    audit_path = governance_dir / "AIGOL_CAPABILITY_AUDIT_V2.md"
    roadmap_path = governance_dir / "AIGOL_ROADMAP_POST_AUDIT_V2.md"
    summary_path = governance_dir / "AIGOL_CAPABILITY_AUDIT_REPORT_SUMMARY_V1.md"
    matrix_path.write_text(json.dumps(matrix, sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    audit_path.write_text(audit_md, encoding="utf-8")
    roadmap_path.write_text(roadmap_md, encoding="utf-8")
    summary_path.write_text(summary_md, encoding="utf-8")

    return {
        "runtime_version": AIGOL_CAPABILITY_AUDIT_RUNTIME_VERSION,
        "matrix_path": str(matrix_path),
        "audit_path": str(audit_path),
        "roadmap_path": str(roadmap_path),
        "summary_path": str(summary_path),
        "capability_counts": deepcopy(matrix["capability_counts"]),
        "normalized_capability_counts": deepcopy(summary["normalized_capability_counts"]),
        "layer_maturity_scores": deepcopy(matrix["layer_maturity_scores"]),
        "overall_maturity": summary["overall_maturity"],
        "recommended_next_milestone": deepcopy(summary["recommended_next_milestone"]),
        "generated_artifacts": [
            "governance/AIGOL_CAPABILITY_AUDIT_V2.md",
            "governance/AIGOL_CAPABILITY_MATRIX_V2.json",
            "governance/AIGOL_ROADMAP_POST_AUDIT_V2.md",
            "governance/AIGOL_CAPABILITY_AUDIT_REPORT_SUMMARY_V1.md",
        ],
        "operator_summary": deepcopy(summary),
        "audit_hash": replay_hash(matrix),
        "replay_visible": True,
    }


def detect_capabilities(repository_root: str | Path) -> dict[str, dict[str, Any]]:
    """Detect capabilities from governance, runtime, and test artifacts."""

    root = Path(repository_root)
    entries: dict[str, dict[str, Any]] = {}
    runtime_files = _files(root / "aigol" / "runtime", "*.py")
    test_files = _files(root / "tests", "test_*.py")
    governance_files = _files(root / "governance", "*")

    for path in runtime_files:
        if path.name == "__init__.py":
            continue
        key = _key_from_runtime(path)
        _entry(entries, key)["implementation"].append(_rel(root, path))

    for path in test_files:
        key = _key_from_test(path)
        _entry(entries, key)["tests"].append(_rel(root, path))

    for path in governance_files:
        if path.is_dir():
            continue
        key = _key_from_governance(path)
        entry = _entry(entries, key)
        rel = _rel(root, path)
        name = path.name.upper()
        if any(hint in name for hint in CERTIFICATION_HINTS):
            entry["certification"].append(rel)
        elif any(hint in name for hint in EVIDENCE_HINTS):
            entry["replay_evidence"].append(rel)
        else:
            entry["governance"].append(rel)

    for key, missing in KNOWN_NOT_STARTED.items():
        entry = _entry(entries, key)
        entry["capability"] = missing["capability"]
        entry["layer"] = missing["layer"]
        entry["missing_reason"] = missing["reason"]
        for path in governance_files:
            name = path.name.upper()
            if any(keyword in name for keyword in missing["evidence_keywords"]):
                rel = _rel(root, path)
                if rel not in entry["governance"] and rel not in entry["certification"] and rel not in entry["replay_evidence"]:
                    entry["governance"].append(rel)

    for entry in entries.values():
        _dedupe_entry(entry)
        if entry.get("capability") is None:
            entry["capability"] = _title_from_key(entry["key"])
        if entry.get("layer") is None:
            entry["layer"] = infer_layer(entry["key"], entry)
        entry["status"] = classify_capability(entry)
    return entries


def build_capability_matrix(
    entries: dict[str, dict[str, Any]],
    *,
    normalization_rules: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the machine-readable V2 matrix from detected entries."""

    capabilities = []
    rules = normalization_rules or load_normalization_rules()
    for entry in sorted(entries.values(), key=lambda item: (item["layer"], item["capability"])):
        identity = normalize_capability_identity(entry["key"], rules)
        capabilities.append(
            {
                "layer": entry["layer"],
                "capability": entry["capability"],
                "capability_id": identity["capability_id"],
                "capability_key": entry["key"],
                "canonical_capability_key": identity["canonical_key"],
                "implementation": entry["implementation"],
                "tests": entry["tests"],
                "governance": entry["governance"],
                "certification": entry["certification"],
                "replay_evidence": entry["replay_evidence"],
                "status": entry["status"],
                "classification_reason": _classification_reason(entry),
                "normalization": identity,
            }
        )

    counts = Counter(item["status"] for item in capabilities)
    capability_counts = {status: counts.get(status, 0) for status in STATUS_ORDER}
    capability_counts["total"] = len(capabilities)
    matrix = {
        "artifact_id": MATRIX_ARTIFACT_ID,
        "runtime_version": AIGOL_CAPABILITY_AUDIT_RUNTIME_VERSION,
        "status": "GENERATED_CAPABILITY_AUDIT",
        "scope": {
            "scanned_directories": list(SCANNED_DIRECTORIES),
            "classification_rule": (
                "CERTIFIED requires certification evidence. IMPLEMENTED requires runtime implementation and tests. "
                "PARTIAL requires at least one governance, runtime, test, replay, or certification signal but does not "
                "meet stronger criteria. NOT_STARTED is reserved for explicit planned or missing capabilities."
            ),
            "status_values": list(STATUS_ORDER),
            "normalization_rules_artifact": rules.get("artifact_id", "BUILT_IN_CAPABILITY_NORMALIZATION_RULES"),
        },
        "capability_counts": capability_counts,
        "normalized_capability_counts": _normalized_capability_counts(capabilities),
        "layer_maturity_scores": _layer_scores(capabilities),
        "capabilities": capabilities,
    }
    matrix["matrix_hash"] = replay_hash({key: value for key, value in matrix.items() if key != "matrix_hash"})
    return matrix


def classify_capability(entry: dict[str, Any]) -> str:
    """Classify a capability according to evidence strength."""

    if entry["key"] in KNOWN_NOT_STARTED:
        return "NOT_STARTED"
    if entry["certification"]:
        return "CERTIFIED"
    if entry["implementation"] and entry["tests"]:
        return "IMPLEMENTED"
    if entry["implementation"] or entry["tests"] or entry["governance"] or entry["replay_evidence"]:
        return "PARTIAL"
    return "NOT_STARTED"


def infer_layer(key: str, entry: dict[str, Any]) -> str:
    """Infer audit layer from capability key and evidence names."""

    text = " ".join([key] + entry["implementation"]).lower()
    if any(token in text for token in ("cognition", "ocs", "intent", "conversation", "prompt", "memory", "clarification")):
        return "L2 Cognition (OCS)"
    if any(token in text for token in ("provider", "worker", "llm", "openai", "attachment")):
        return "L3 Provider/Worker"
    if any(token in text for token in ("execution", "dispatch", "result", "transport", "runtime_engine", "operation")):
        return "L4 Execution"
    if any(token in text for token in ("implementation", "generated", "manifest", "materialization", "filesystem_mutation")):
        return "L5 Implementation Generation"
    if any(token in text for token in ("domain", "trading", "healthcare", "marketing", "server_management")):
        return "L6 Domain Runtime"
    if any(token in text for token in ("marketplace", "ecosystem", "resource_selection", "local_node")):
        return "L7 Marketplace / Ecosystem"
    if any(token in text for token in ("governance", "policy", "approval", "authorization", "capability", "replay")):
        return "L1 Governance"
    return "L1 Governance"


def render_audit_document(matrix: dict[str, Any]) -> str:
    counts = matrix["capability_counts"]
    lines = [
        "# AIGOL_CAPABILITY_AUDIT_V2",
        "",
        "## Status",
        "",
        "Generated by `AIGOL_CAPABILITY_AUDIT_RUNTIME_V1`.",
        "",
        "```text",
        "AIGOL_CAPABILITY_AUDIT_V2_STATUS = GENERATED",
        "```",
        "",
        "## Scope",
        "",
        "Scanned directories:",
        "",
    ]
    lines.extend(f"- `{directory}`" for directory in matrix["scope"]["scanned_directories"])
    lines.extend(
        [
            "",
            "## Capability Counts",
            "",
            "| Status | Count |",
            "| --- | ---: |",
        ]
    )
    for status in STATUS_ORDER:
        lines.append(f"| `{status}` | {counts[status]} |")
    lines.extend(
        [
            f"| Total | {counts['total']} |",
            "",
            "## Layer Maturity Scores",
            "",
            "| Layer | Score |",
            "| --- | ---: |",
        ]
    )
    for layer, score in matrix["layer_maturity_scores"].items():
        lines.append(f"| {layer} | {score} |")
    lines.extend(["", "## Capability Matrix Summary", ""])
    by_layer: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for capability in matrix["capabilities"]:
        by_layer[capability["layer"]].append(capability)
    for layer in sorted(by_layer):
        lines.extend([f"### {layer}", ""])
        layer_counts = Counter(capability["status"] for capability in by_layer[layer])
        for status in STATUS_ORDER:
            lines.append(f"- `{status}`: {layer_counts.get(status, 0)}")
        lines.append("")
        for status in STATUS_ORDER:
            examples = [capability for capability in by_layer[layer] if capability["status"] == status][:10]
            if examples:
                lines.append(f"Representative `{status}` capabilities:")
                for capability in examples:
                    lines.append(f"- {capability['capability']}")
                lines.append("")
    lines.extend(
        [
            "## Generated Artifacts",
            "",
            "- `governance/AIGOL_CAPABILITY_AUDIT_V2.md`",
            "- `governance/AIGOL_CAPABILITY_MATRIX_V2.json`",
            "- `governance/AIGOL_ROADMAP_POST_AUDIT_V2.md`",
            "",
            "## Evidence Rule",
            "",
            "The runtime classifies only from local governance, runtime, and test evidence. `CERTIFIED` requires certification evidence.",
            "",
        ]
    )
    return "\n".join(lines)


def render_roadmap_document(matrix: dict[str, Any]) -> str:
    by_status: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for capability in matrix["capabilities"]:
        by_status[capability["status"]].append(capability)
    lines = [
        "# AIGOL_ROADMAP_POST_AUDIT_V2",
        "",
        "## Status",
        "",
        "Generated by `AIGOL_CAPABILITY_AUDIT_RUNTIME_V1`.",
        "",
        "## Completed Capabilities",
        "",
    ]
    lines.extend(_capability_lines(by_status["CERTIFIED"], empty="No certified capabilities detected."))
    lines.extend(["", "## Implemented But Not Certified", ""])
    lines.extend(_capability_lines(by_status["IMPLEMENTED"], empty="No implemented-only capabilities detected."))
    lines.extend(["", "## Partially Completed Capabilities", ""])
    lines.extend(_capability_lines(by_status["PARTIAL"], empty="No partial capabilities detected."))
    lines.extend(["", "## Missing Capabilities", ""])
    lines.extend(_capability_lines(by_status["NOT_STARTED"], empty="No explicit missing capabilities detected."))
    lines.extend(
        [
            "",
            "## Recommended Execution Order",
            "",
            "1. Certify implemented-only capabilities before expanding new runtime surface.",
            "2. Harden partial native development and implementation-generation capabilities.",
            "3. Extend domain runtime coverage from certified trading seeds toward repeatable domain bundles.",
            "4. Expand provider and worker ecosystem certification only after metadata and replay contracts remain stable.",
            "5. Defer marketplace, tenant, billing, and partner-onboarding work until ecosystem evidence is stronger.",
            "",
            "## Recommended Next Milestone",
            "",
            "```text",
            "AIGOL_NATIVE_DEVELOPMENT_END_TO_END_DRY_RUN_V1",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def build_audit_report_summary(
    matrix: dict[str, Any],
    *,
    repository_root: str | Path,
    audit_timestamp: str | None = None,
) -> dict[str, Any]:
    """Build the operator-focused capability audit summary model."""

    timestamp = audit_timestamp or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    layer_scores = _complete_layer_scores(matrix.get("layer_maturity_scores", {}))
    ranked_strongest = _rank_layers(layer_scores, reverse=True)[:5]
    ranked_weakest = _rank_layers(layer_scores, reverse=False)[:5]
    growth_areas = _top_growth_areas(matrix["capabilities"])
    stagnating_areas = _top_stagnating_areas(matrix["capabilities"])
    recommendation = _recommended_next_milestone(layer_scores, growth_areas, stagnating_areas)
    return {
        "artifact_id": SUMMARY_DOCUMENT_ID,
        "runtime_version": AIGOL_CAPABILITY_AUDIT_RUNTIME_VERSION,
        "repository": str(Path(repository_root).resolve()),
        "audit_timestamp": timestamp,
        "capability_counts": deepcopy(matrix["capability_counts"]),
        "normalized_capability_counts": _normalized_capability_counts(matrix["capabilities"]),
        "layer_scores": layer_scores,
        "overall_maturity": _overall_maturity(layer_scores),
        "top_strongest_layers": ranked_strongest,
        "top_weakest_layers": ranked_weakest,
        "top_capability_growth_areas": growth_areas,
        "top_stagnating_areas": stagnating_areas,
        "recommended_next_milestone": recommendation,
        "status": "SUCCESS",
    }


def render_audit_report_summary(summary: dict[str, Any]) -> str:
    """Render the operator-focused audit summary markdown report."""

    counts = summary["capability_counts"]
    normalized_counts = summary["normalized_capability_counts"]
    lines = [
        "# AIGOL_CAPABILITY_AUDIT_REPORT_SUMMARY_V1",
        "",
        "## Status",
        "",
        "Operator-focused summary generated by `AIGOL_CAPABILITY_AUDIT_RUNTIME_V1`.",
        "",
        "```text",
        "AIGOL_CAPABILITY_AUDIT_REPORT_SUMMARY_STATUS = CERTIFIED",
        "```",
        "",
        "## Repository",
        "",
        f"`{summary['repository']}`",
        "",
        "## Audit Timestamp",
        "",
        f"`{summary['audit_timestamp']}`",
        "",
        "## Overall Maturity",
        "",
        f"`{summary['overall_maturity']}`",
        "",
        "## Capability Counts",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]
    for status in STATUS_ORDER:
        lines.append(f"| `{status}` | {counts.get(status, 0)} |")
    lines.extend(
        [
            f"| Total | {counts.get('total', 0)} |",
            "",
            "## Normalized Capability Counts",
            "",
            "| Status | Count |",
            "| --- | ---: |",
        ]
    )
    for status in STATUS_ORDER:
        lines.append(f"| `{status}` | {normalized_counts.get(status, 0)} |")
    lines.extend(
        [
            f"| Total | {normalized_counts.get('total', 0)} |",
            "",
            "## Layer Scores",
            "",
            "| Layer | Score |",
            "| --- | ---: |",
        ]
    )
    for layer in CANONICAL_LAYERS:
        lines.append(f"| {OPERATOR_LAYER_LABELS[layer]} | {summary['layer_scores'][layer]} |")
    lines.extend(["", "## Top 5 Strongest Layers", ""])
    lines.extend(_ranked_layer_lines(summary["top_strongest_layers"]))
    lines.extend(["", "## Top 5 Weakest Layers", ""])
    lines.extend(_ranked_layer_lines(summary["top_weakest_layers"]))
    lines.extend(["", "## Top Capability Growth Areas", ""])
    lines.extend(_area_lines(summary["top_capability_growth_areas"]))
    lines.extend(["", "## Top Stagnating Areas", ""])
    lines.extend(_area_lines(summary["top_stagnating_areas"]))
    recommendation = summary["recommended_next_milestone"]
    lines.extend(
        [
            "",
            "## Recommended Next Milestone",
            "",
            "```text",
            recommendation["milestone"],
            "```",
            "",
            recommendation["reasoning"],
            "",
            "## CLI Summary Contract",
            "",
            "After successful audit execution the CLI prints `AIGOL CAPABILITY AUDIT SUMMARY` with repository, overall maturity, top strengths, top weaknesses, recommended next milestone, and success status.",
            "",
        ]
    )
    return "\n".join(lines)


def render_cli_summary(summary: dict[str, Any]) -> str:
    """Render the successful audit CLI summary."""

    recommendation = summary["recommended_next_milestone"]
    lines = [
        "AIGOL CAPABILITY AUDIT SUMMARY",
        "",
        f"Repository: {summary['repository']}",
        f"Overall Maturity: {summary['overall_maturity']}",
        "",
        "Top Strengths:",
    ]
    lines.extend(_cli_layer_lines(summary["top_strongest_layers"]))
    lines.extend(["", "Top Weaknesses:"])
    lines.extend(_cli_layer_lines(summary["top_weakest_layers"]))
    lines.extend(
        [
            "",
            "Recommended Next Milestone:",
            f"{recommendation['milestone']}",
            f"Reasoning: {recommendation['reasoning']}",
            "",
            "Status: SUCCESS",
        ]
    )
    return "\n".join(lines)


def _files(root: Path, pattern: str) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.rglob(pattern) if path.is_file() and "__pycache__" not in path.parts)


def _entry(entries: dict[str, dict[str, Any]], key: str) -> dict[str, Any]:
    if key not in entries:
        entries[key] = {
            "key": key,
            "capability": None,
            "layer": None,
            "implementation": [],
            "tests": [],
            "governance": [],
            "certification": [],
            "replay_evidence": [],
            "missing_reason": None,
        }
    return entries[key]


def _key_from_runtime(path: Path) -> str:
    parts = list(path.with_suffix("").parts)
    try:
        index = parts.index("runtime")
        parts = parts[index + 1 :]
    except ValueError:
        parts = [path.stem]
    return _normalize_key("_".join(parts))


def _key_from_test(path: Path) -> str:
    name = path.stem
    if name.startswith("test_"):
        name = name[5:]
    return _normalize_key(name)


def _key_from_governance(path: Path) -> str:
    name = path.stem
    name = re.sub(r"_V\d+$", "", name, flags=re.IGNORECASE)
    name = re.sub(r"_(CERTIFICATION|CERTIFIED|ACCEPTANCE|EVIDENCE|MANIFEST|REPORT|MODEL|RUNTIME|FOUNDATION|REVIEW|GAP_ANALYSIS|RECOMMENDATIONS|ADR|BOUNDARY_GUARANTEES)$", "", name, flags=re.IGNORECASE)
    return _normalize_key(name)


def _normalize_key(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"^aigol_", "", value)
    value = re.sub(r"(_v\d+|_runtime|_model|_foundation|_certification|_acceptance|_evidence|_manifest)$", "", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "unknown_capability"


def _title_from_key(key: str) -> str:
    acronyms = {"aigol": "AiGOL", "ocs": "OCS", "llm": "LLM", "cli": "CLI", "api": "API"}
    words = []
    for word in key.split("_"):
        words.append(acronyms.get(word, word.capitalize()))
    return " ".join(words)


def _rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _dedupe_entry(entry: dict[str, Any]) -> None:
    for field in ("implementation", "tests", "governance", "certification", "replay_evidence"):
        entry[field] = sorted(dict.fromkeys(entry[field]))


def _classification_reason(entry: dict[str, Any]) -> str:
    if entry["status"] == "CERTIFIED":
        return "certification evidence detected"
    if entry["status"] == "IMPLEMENTED":
        return "runtime implementation and tests detected without certification evidence"
    if entry["status"] == "PARTIAL":
        return "local evidence detected but implementation, tests, or certification are incomplete"
    return entry.get("missing_reason") or "explicit missing capability"


def _layer_scores(capabilities: list[dict[str, Any]]) -> dict[str, int]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for capability in capabilities:
        grouped[capability["layer"]].append(capability)
    scores: dict[str, int] = {}
    for layer in sorted(grouped):
        values = [STATUS_SCORE[item["status"]] for item in grouped[layer]]
        scores[layer] = round(sum(values) / len(values)) if values else 0
    return scores


def _normalized_capability_counts(capabilities: list[dict[str, Any]]) -> dict[str, int]:
    strongest_by_id: dict[str, str] = {}
    strength = {status: index for index, status in enumerate(reversed(STATUS_ORDER))}
    for capability in capabilities:
        capability_id = capability.get("capability_id") or capability.get("capability_key")
        status = capability["status"]
        previous = strongest_by_id.get(capability_id)
        if previous is None or strength[status] > strength[previous]:
            strongest_by_id[capability_id] = status
    counts = Counter(strongest_by_id.values())
    normalized_counts = {status: counts.get(status, 0) for status in STATUS_ORDER}
    normalized_counts["total"] = len(strongest_by_id)
    return normalized_counts


def _complete_layer_scores(scores: dict[str, int]) -> dict[str, int]:
    return {layer: int(scores.get(layer, 0)) for layer in CANONICAL_LAYERS}


def _overall_maturity(layer_scores: dict[str, int]) -> int:
    values = [layer_scores[layer] for layer in CANONICAL_LAYERS]
    return round(sum(values) / len(values)) if values else 0


def _rank_layers(layer_scores: dict[str, int], *, reverse: bool) -> list[dict[str, Any]]:
    return [
        {
            "layer": layer,
            "label": OPERATOR_LAYER_LABELS[layer],
            "score": score,
        }
        for layer, score in sorted(layer_scores.items(), key=lambda item: (-item[1], item[0]) if reverse else (item[1], item[0]))
    ]


def _top_growth_areas(capabilities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped = _status_counts_by_layer(capabilities)
    areas = []
    for layer in CANONICAL_LAYERS:
        counts = grouped[layer]
        growth_signal = counts["IMPLEMENTED"] + counts["PARTIAL"]
        areas.append(
            {
                "layer": layer,
                "label": OPERATOR_LAYER_LABELS[layer],
                "score": growth_signal,
                "reason": f"{growth_signal} capabilities are implemented or partial and can be moved toward certification.",
            }
        )
    return sorted(areas, key=lambda item: (-item["score"], item["layer"]))[:5]


def _top_stagnating_areas(capabilities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped = _status_counts_by_layer(capabilities)
    areas = []
    for layer in CANONICAL_LAYERS:
        counts = grouped[layer]
        stagnation_signal = counts["NOT_STARTED"] + counts["PARTIAL"]
        areas.append(
            {
                "layer": layer,
                "label": OPERATOR_LAYER_LABELS[layer],
                "score": stagnation_signal,
                "reason": f"{stagnation_signal} capabilities are partial or not started.",
            }
        )
    return sorted(areas, key=lambda item: (-item["score"], item["layer"]))[:5]


def _status_counts_by_layer(capabilities: list[dict[str, Any]]) -> dict[str, Counter]:
    grouped: dict[str, Counter] = {layer: Counter() for layer in CANONICAL_LAYERS}
    for capability in capabilities:
        layer = capability.get("layer")
        if layer not in grouped:
            grouped[layer] = Counter()
        grouped[layer][capability["status"]] += 1
    return grouped


def _recommended_next_milestone(
    layer_scores: dict[str, int],
    growth_areas: list[dict[str, Any]],
    stagnating_areas: list[dict[str, Any]],
) -> dict[str, str]:
    weakest_priority = {
        "L7 Marketplace / Ecosystem": 0,
        "L5 Implementation Generation": 1,
        "L6 Domain Runtime": 2,
        "L3 Provider/Worker": 3,
        "L4 Execution": 4,
        "L2 Cognition (OCS)": 5,
        "L1 Governance": 6,
    }
    weakest_layer = min(layer_scores.items(), key=lambda item: (item[1], weakest_priority.get(item[0], 99)))[0]
    if weakest_layer == "L7 Marketplace / Ecosystem":
        milestone = "AIGOL_MARKETPLACE_ECOSYSTEM_FOUNDATION_V1"
        reason = "Marketplace / Ecosystem is the weakest canonical layer; move from planning evidence toward a bounded ecosystem foundation before commercial expansion."
    elif weakest_layer == "L6 Domain Runtime":
        milestone = "AIGOL_DOMAIN_EXECUTION_BINDING_V1"
        reason = "Domain Runtime needs stronger operational execution evidence; bind governed domains to certified execution replay."
    elif weakest_layer == "L5 Implementation Generation":
        milestone = "AIGOL_NATIVE_DEVELOPMENT_END_TO_END_DRY_RUN_V1"
        reason = "Implementation Generation remains weak relative to governance; prioritize a replay-safe native development dry run."
    elif weakest_layer == "L3 Provider/Worker":
        milestone = "AIGOL_PROVIDER_WORKER_CERTIFICATION_EXPANSION_V1"
        reason = "Provider / Worker evidence should be expanded and certified before broader ecosystem work."
    else:
        milestone = "AIGOL_CAPABILITY_AUDIT_REPORT_SUMMARY_V1"
        reason = "Operator visibility is the safest next improvement because it strengthens planning without changing execution authority."
    if growth_areas:
        reason += f" Highest growth signal is {growth_areas[0]['label']}."
    if stagnating_areas:
        reason += f" Highest stagnation signal is {stagnating_areas[0]['label']}."
    return {"milestone": milestone, "reasoning": reason}


def _ranked_layer_lines(layers: list[dict[str, Any]]) -> list[str]:
    return [f"{index}. {item['label']}: {item['score']}" for index, item in enumerate(layers, start=1)]


def _cli_layer_lines(layers: list[dict[str, Any]]) -> list[str]:
    return [f"- {item['label']}: {item['score']}" for item in layers]


def _area_lines(areas: list[dict[str, Any]]) -> list[str]:
    if not areas:
        return ["No areas detected."]
    return [f"- {item['label']}: {item['reason']}" for item in areas]


def _capability_lines(capabilities: list[dict[str, Any]], *, empty: str, limit: int = 50) -> list[str]:
    if not capabilities:
        return [empty]
    ordered = sorted(capabilities, key=lambda item: item["capability"])
    lines = [f"- {capability['capability']} ({capability['layer']})" for capability in ordered[:limit]]
    if len(ordered) > limit:
        lines.append(f"- ... {len(ordered) - limit} additional capabilities recorded in `AIGOL_CAPABILITY_MATRIX_V2.json`")
    return lines


def main(argv: list[str] | None = None) -> int:
    args = argv or []
    root = Path(args[0]) if args else Path.cwd()
    capture = run_capability_audit(repository_root=root)
    print(render_cli_summary(capture["operator_summary"]))
    return 0


__all__ = [
    "AIGOL_CAPABILITY_AUDIT_RUNTIME_VERSION",
    "build_capability_matrix",
    "classify_capability",
    "detect_capabilities",
    "infer_layer",
    "main",
    "build_audit_report_summary",
    "render_audit_document",
    "render_audit_report_summary",
    "render_cli_summary",
    "render_roadmap_document",
    "run_capability_audit",
]


if __name__ == "__main__":
    raise SystemExit(main())
