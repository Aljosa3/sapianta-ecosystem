"""Read-only bounded cognition state envelope construction.

The envelope consolidates existing governed artifacts into an inspectable
cognition state. It does not execute, authorize, dispatch, repair, infer hidden
context, or mutate governance state.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

ARTIFACT_TYPE = "BOUNDED_COGNITION_STATE_ENVELOPE_V1"
SCHEMA_VERSION = "1.0"
UNKNOWN = "UNKNOWN"
GENERATED_AT = "1970-01-01T00:00:00Z"

FORBIDDEN_BASE = (
    "execution",
    "orchestration",
    "autonomous_continuation",
    "hidden_continuation",
    "hidden_context_ingestion",
    "provider_routing",
    "self_modifying_governance",
    "runtime_mutation",
    "retries",
)

AUTHORITY_NAMES = (
    "ChatGPT semantic authority",
    "governance authority",
    "human approval authority",
    "dispatch authority",
    "execution authority",
    "provider authority",
    "replay authority",
    "reflection authority",
    "mutation authority",
)


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _artifact_type(artifact: dict[str, Any]) -> str:
    return str(artifact.get("artifact_type") or artifact.get("gate_type") or UNKNOWN)


def _as_artifacts(artifacts: Any) -> list[dict[str, Any]]:
    if artifacts is None:
        return []
    if isinstance(artifacts, dict):
        return [artifacts]
    if isinstance(artifacts, list):
        return [item for item in artifacts if isinstance(item, dict)]
    return []


def _find(artifacts: list[dict[str, Any]], *types: str) -> dict[str, Any] | None:
    wanted = set(types)
    for artifact in artifacts:
        if _artifact_type(artifact) in wanted:
            return artifact
    return None


def _first_str(*values: Any) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value
    return UNKNOWN


def _source_ref(artifact: dict[str, Any] | None, hash_fields: tuple[str, ...]) -> dict[str, str]:
    if not isinstance(artifact, dict):
        return {"artifact_type": UNKNOWN, "hash": UNKNOWN}
    hashes = artifact.get("hashes", {}) if isinstance(artifact.get("hashes"), dict) else {}
    for field in hash_fields:
        value = artifact.get(field, hashes.get(field))
        if isinstance(value, str) and value.strip():
            return {"artifact_type": _artifact_type(artifact), "hash": value}
    return {"artifact_type": _artifact_type(artifact), "hash": UNKNOWN}


def _replay_identity(artifacts: list[dict[str, Any]]) -> str:
    for artifact in artifacts:
        value = artifact.get("replay_identity")
        if isinstance(value, str) and value.strip():
            return value
    return UNKNOWN


def _semantic_input_ref(artifacts: list[dict[str, Any]]) -> dict[str, str]:
    ingress = _find(artifacts, "CHATGPT_INGRESS_ARTIFACT_V1")
    proposal = _find(artifacts, "CHATGPT_SEMANTIC_PROPOSAL_CANDIDATE_V1")
    artifact = ingress or proposal
    return _source_ref(artifact, ("artifact_hash", "proposal_candidate_hash", "semantic_output_hash"))


def _semantic_contract_ref(artifacts: list[dict[str, Any]]) -> dict[str, str]:
    contract = _find(
        artifacts,
        "SEMANTIC_CONTRACT_CANDIDATE_V1",
        "SEMANTIC_CONTRACT_V1",
    )
    return _source_ref(contract, ("artifact_hash", "contract_candidate_hash"))


def _normalized_intent(artifacts: list[dict[str, Any]]) -> str:
    for artifact in artifacts:
        value = artifact.get("normalized_intent")
        if isinstance(value, str) and value.strip():
            return value
    return UNKNOWN


def _admissibility_state(artifacts: list[dict[str, Any]]) -> str:
    gate = _find(artifacts, "CHATGPT_INGRESS_ACCEPTANCE_GATE_V1")
    if isinstance(gate, dict):
        return _first_str(gate.get("gate_status"), gate.get("status"))
    for artifact in artifacts:
        for field in ("gate_status", "governance_status", "validation_status", "status"):
            value = artifact.get(field)
            if isinstance(value, str) and (
                "ACCEPT" in value or "REJECT" in value or "PASS" in value or "FAIL" in value
            ):
                return value
    return UNKNOWN


def _current_boundary_state(artifacts: list[dict[str, Any]]) -> str:
    boundary_fields = (
        "execution_status",
        "execution_continuity_status",
        "provider_boundary_state",
        "dispatch_authorization_status",
        "handoff_boundary_state",
        "approval_status",
        "execution_boundary_state",
        "governance_status",
    )
    for artifact in reversed(artifacts):
        for field in boundary_fields:
            value = artifact.get(field)
            if isinstance(value, str) and value.strip():
                return value
    return UNKNOWN


def _ambiguity_state(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    ambiguities: list[Any] = []
    for artifact in artifacts:
        value = artifact.get("ambiguities")
        if isinstance(value, list):
            ambiguities.extend(value)
        if isinstance(artifact.get("semantic_contract_candidate"), dict):
            child = artifact["semantic_contract_candidate"].get("ambiguities")
            if isinstance(child, list):
                ambiguities.extend(child)
    if not ambiguities:
        return {"status": UNKNOWN, "ambiguities": []}
    blocking = [item for item in ambiguities if item != "NO_BLOCKING_AMBIGUITY_DETECTED"]
    return {
        "status": "AMBIGUITY_PRESENT" if blocking else "NO_BLOCKING_AMBIGUITY_DETECTED",
        "ambiguities": ambiguities,
    }


def _evidence_refs(artifacts: list[dict[str, Any]]) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for artifact in artifacts:
        refs.append(
            {
                "artifact_type": _artifact_type(artifact),
                "hash": _source_ref(
                    artifact,
                    (
                        "artifact_hash",
                        "decision_hash",
                        "preview_hash",
                        "approval_hash",
                        "handoff_preview_hash",
                        "dispatch_authorization_hash",
                        "continuity_preview_hash",
                        "execution_governance_hash",
                        "governed_return_hash",
                    ),
                )["hash"],
            }
        )
    return refs


def _lineage_refs(artifacts: list[dict[str, Any]]) -> dict[str, str]:
    lineage: dict[str, str] = {
        "ingress_artifact_hash": UNKNOWN,
        "proposal_candidate_hash": UNKNOWN,
        "contract_candidate_hash": UNKNOWN,
        "acceptance_gate_hash": UNKNOWN,
        "task_package_preview_hash": UNKNOWN,
        "human_approval_hash": UNKNOWN,
        "handoff_preview_hash": UNKNOWN,
        "dispatch_authorization_hash": UNKNOWN,
        "continuity_preview_hash": UNKNOWN,
        "execution_governance_hash": UNKNOWN,
        "governed_return_hash": UNKNOWN,
    }
    for artifact in artifacts:
        child = artifact.get("lineage")
        if isinstance(child, dict):
            for key in lineage:
                if isinstance(child.get(key), str) and child[key]:
                    lineage[key] = child[key]
        hashes = artifact.get("hashes", {}) if isinstance(artifact.get("hashes"), dict) else {}
        mapping = {
            "ingress_artifact_hash": artifact.get("source_ingress_artifact_hash") or hashes.get("artifact_hash"),
            "proposal_candidate_hash": artifact.get("semantic_proposal_candidate_hash") or artifact.get("proposal_candidate_hash"),
            "contract_candidate_hash": artifact.get("semantic_contract_candidate_hash") or artifact.get("contract_candidate_hash"),
            "acceptance_gate_hash": artifact.get("admissibility_gate_hash") or artifact.get("decision_hash"),
            "task_package_preview_hash": artifact.get("governed_task_package_preview_hash") or artifact.get("preview_hash"),
            "human_approval_hash": artifact.get("human_approval_hash") or artifact.get("approval_hash"),
            "handoff_preview_hash": artifact.get("source_handoff_preview_hash") or artifact.get("handoff_preview_hash"),
            "dispatch_authorization_hash": artifact.get("source_dispatch_authorization_hash") or artifact.get("dispatch_authorization_hash"),
            "continuity_preview_hash": artifact.get("source_continuity_preview_hash") or artifact.get("continuity_preview_hash"),
            "execution_governance_hash": artifact.get("execution_governance_hash"),
            "governed_return_hash": artifact.get("governed_return_hash"),
        }
        for key, value in mapping.items():
            if isinstance(value, str) and value.strip():
                lineage[key] = value
    return lineage


def _reflection_refs(artifacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    refs = []
    for artifact in artifacts:
        if "reflection_id" in artifact or _artifact_type(artifact).startswith("REFLECTION"):
            refs.append(
                {
                    "reflection_id": _first_str(artifact.get("reflection_id")),
                    "advisory_only": artifact.get("advisory_only", UNKNOWN),
                    "allowed_to_execute_automatically": artifact.get(
                        "allowed_to_execute_automatically",
                        UNKNOWN,
                    ),
                }
            )
    return refs


def _authority_entry(
    *,
    authority_name: str,
    status: str,
    source_evidence: str,
    allowed: list[str] | None = None,
    forbidden: list[str] | None = None,
    notes: str = "",
) -> dict[str, Any]:
    return {
        "authority_name": authority_name,
        "status": status,
        "source_evidence": source_evidence,
        "allowed": list(allowed or []),
        "forbidden": list(forbidden or []),
        "notes": notes,
    }


def _authority_matrix(artifacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    has_ingress = _find(artifacts, "CHATGPT_INGRESS_ARTIFACT_V1") is not None
    has_human_approval = any(artifact.get("approval_status") == "APPROVED_FOR_GOVERNED_HANDOFF" for artifact in artifacts)
    has_dispatch = any(artifact.get("dispatch_authorized") is True for artifact in artifacts)
    has_execution = any(artifact.get("execution_performed") is True for artifact in artifacts)
    has_provider = any(artifact.get("provider_invoked") is True for artifact in artifacts)
    has_replay = _replay_identity(artifacts) != UNKNOWN
    has_reflection = bool(_reflection_refs(artifacts))
    return [
        _authority_entry(
            authority_name="ChatGPT semantic authority",
            status="SEMANTIC_INPUT_PRESENT" if has_ingress else UNKNOWN,
            source_evidence="CHATGPT_INGRESS_ARTIFACT_V1" if has_ingress else UNKNOWN,
            allowed=["semantic input"] if has_ingress else [],
            forbidden=["approval", "dispatch", "execution", "governance authority"],
            notes="ChatGPT-style input is semantic input only.",
        ),
        _authority_entry(
            authority_name="governance authority",
            status="GOVERNANCE_MEDIATION_VISIBLE" if _admissibility_state(artifacts) != UNKNOWN else UNKNOWN,
            source_evidence="admissibility evidence" if _admissibility_state(artifacts) != UNKNOWN else UNKNOWN,
            allowed=["validate", "block", "escalate"],
            forbidden=["self-modifying governance", "hidden authority issuance"],
            notes="Governance authority is reported from existing evidence only.",
        ),
        _authority_entry(
            authority_name="human approval authority",
            status="APPROVAL_EVIDENCE_PRESENT" if has_human_approval else UNKNOWN,
            source_evidence="HUMAN_APPROVAL_GATE_V1" if has_human_approval else UNKNOWN,
            allowed=["approve preview evidence"] if has_human_approval else [],
            forbidden=["execution", "provider invocation", "autonomous continuation"],
            notes="Human approval evidence is not dispatch authorization.",
        ),
        _authority_entry(
            authority_name="dispatch authority",
            status="DISPATCH_AUTHORIZED_EVIDENCE_PRESENT" if has_dispatch else UNKNOWN,
            source_evidence="EXPLICIT_DISPATCH_AUTHORIZATION_V1" if has_dispatch else UNKNOWN,
            allowed=["dispatch authorization evidence"] if has_dispatch else [],
            forbidden=["execution", "provider execution", "retries", "orchestration"],
            notes="The matrix reports dispatch evidence but does not issue dispatch authority.",
        ),
        _authority_entry(
            authority_name="execution authority",
            status="EXECUTION_EVIDENCE_PRESENT" if has_execution else "NOT_GRANTED_BY_ENVELOPE",
            source_evidence="CONTROLLED_EXECUTION_HANDOFF_V1" if has_execution else UNKNOWN,
            allowed=[],
            forbidden=["execution authorization by cognition envelope", "automatic execution"],
            notes="The cognition envelope never grants execution authority.",
        ),
        _authority_entry(
            authority_name="provider authority",
            status="PROVIDER_EVIDENCE_PRESENT" if has_provider else UNKNOWN,
            source_evidence="BOUNDED_CODEX_CLI_PROVIDER" if has_provider else UNKNOWN,
            allowed=["single bounded provider evidence"] if has_provider else [],
            forbidden=["provider routing", "fallback providers", "adaptive provider selection"],
            notes="Provider state is observational.",
        ),
        _authority_entry(
            authority_name="replay authority",
            status="REPLAY_IDENTITY_PRESENT" if has_replay else UNKNOWN,
            source_evidence=_replay_identity(artifacts) if has_replay else UNKNOWN,
            allowed=["read-only verification", "lineage inspection"] if has_replay else [],
            forbidden=["replay mutation", "replay repair", "history rewrite"],
            notes="Replay authority is verification-only.",
        ),
        _authority_entry(
            authority_name="reflection authority",
            status="REFLECTION_EVIDENCE_PRESENT" if has_reflection else UNKNOWN,
            source_evidence="reflection artifact" if has_reflection else UNKNOWN,
            allowed=["advisory proposal"] if has_reflection else [],
            forbidden=["automatic execution", "automatic approval", "runtime mutation"],
            notes="Reflection is advisory-only.",
        ),
        _authority_entry(
            authority_name="mutation authority",
            status="NOT_GRANTED_BY_ENVELOPE",
            source_evidence=UNKNOWN,
            allowed=[],
            forbidden=["governance mutation", "runtime mutation", "self-modifying governance"],
            notes="The cognition envelope never grants mutation authority.",
        ),
    ]


def _allowed_next_transitions(artifacts: list[dict[str, Any]], boundary_state: str) -> list[str]:
    allowed = ["inspect_cognition_state", "verify_replay_evidence"]
    if boundary_state == "ACCEPTED_FOR_GOVERNED_PREVIEW":
        allowed.append("create_governed_task_package_preview")
    if boundary_state == "READY_FOR_HUMAN_APPROVAL":
        allowed.append("human_approval_gate")
    if boundary_state == "APPROVED_FOR_GOVERNED_HANDOFF":
        allowed.append("governed_handoff_package_preview")
    if boundary_state == "READY_FOR_EXPLICIT_DISPATCH_AUTHORIZATION":
        allowed.append("explicit_dispatch_authorization")
    if any(artifact.get("dispatch_authorized") is True for artifact in artifacts):
        allowed.append("controlled_execution_continuity_preview")
    if any(artifact.get("execution_status") in {"EXECUTION_COMPLETED", "EXECUTION_FAILED", "EXECUTION_BLOCKED"} for artifact in artifacts):
        allowed.append("inspect_governed_return")
    return sorted(set(allowed))


def _forbidden_transitions(artifacts: list[dict[str, Any]]) -> list[str]:
    forbidden = set(FORBIDDEN_BASE)
    if not any(artifact.get("dispatch_authorized") is True for artifact in artifacts):
        forbidden.add("dispatch")
    if not any(artifact.get("approval_status") == "APPROVED_FOR_GOVERNED_HANDOFF" for artifact in artifacts):
        forbidden.add("governed_handoff")
    return sorted(forbidden)


def _continuity_status(artifacts: list[dict[str, Any]], lineage: dict[str, str]) -> str:
    if not artifacts:
        return UNKNOWN
    if any(artifact.get("continuity_verified") is True for artifact in artifacts):
        return "VERIFIED"
    if all(value == UNKNOWN for value in lineage.values()):
        return UNKNOWN
    if any(value == UNKNOWN for value in lineage.values()):
        return "PARTIAL"
    return "VISIBLE"


def _envelope_hash_input(envelope: dict[str, Any]) -> dict[str, Any]:
    safe = _canonical_copy(envelope)
    safe.pop("envelope_hash", None)
    return safe


def build_cognition_state_envelope(
    artifacts: Any = None,
    *,
    generated_at: str = GENERATED_AT,
) -> dict[str, Any]:
    safe_artifacts = _as_artifacts(artifacts)
    lineage = _lineage_refs(safe_artifacts)
    boundary_state = _current_boundary_state(safe_artifacts)
    envelope = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "generated_at": str(generated_at),
        "replay_identity": _replay_identity(safe_artifacts),
        "semantic_input_ref": _semantic_input_ref(safe_artifacts),
        "normalized_intent": _normalized_intent(safe_artifacts),
        "semantic_contract_ref": _semantic_contract_ref(safe_artifacts),
        "admissibility_state": _admissibility_state(safe_artifacts),
        "authority_matrix": _authority_matrix(safe_artifacts),
        "current_boundary_state": boundary_state,
        "ambiguity_state": _ambiguity_state(safe_artifacts),
        "allowed_next_transitions": _allowed_next_transitions(safe_artifacts, boundary_state),
        "forbidden_transitions": _forbidden_transitions(safe_artifacts),
        "lineage_refs": lineage,
        "evidence_refs": _evidence_refs(safe_artifacts),
        "reflection_refs": _reflection_refs(safe_artifacts),
        "continuity_status": _continuity_status(safe_artifacts, lineage),
        "execution_authority": False,
        "orchestration_authority": False,
        "autonomous_continuation": False,
        "mutation_authority": False,
        "read_only": True,
        "fail_closed_unknown_handling": True,
        "semantic_truth_certified": False,
        "hidden_context_ingestion": False,
        "provider_invocation_performed": False,
    }
    envelope["envelope_hash"] = canonical_hash(_envelope_hash_input(envelope))
    return envelope


def _load_json_file(path: Path) -> list[dict[str, Any]]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if isinstance(parsed, dict):
        return [parsed]
    if isinstance(parsed, list):
        return [item for item in parsed if isinstance(item, dict)]
    return []


def _load_jsonl_file(path: Path) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return artifacts
    for line in lines:
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            artifacts.append(parsed)
    return artifacts


def load_cognition_artifacts(input_path: str | Path | None = None) -> list[dict[str, Any]]:
    """Load existing JSON/JSONL artifacts from a file or directory.

    Invalid files are ignored and represented by UNKNOWN in the generated
    envelope rather than guessed or repaired.
    """

    if input_path is None or not str(input_path).strip():
        return []
    path = Path(input_path)
    if path.is_file():
        if path.suffix == ".jsonl":
            return _load_jsonl_file(path)
        return _load_json_file(path)
    if path.is_dir():
        artifacts: list[dict[str, Any]] = []
        for candidate in sorted(path.rglob("*")):
            if candidate.is_file() and candidate.suffix in {".json", ".jsonl"}:
                artifacts.extend(_load_jsonl_file(candidate) if candidate.suffix == ".jsonl" else _load_json_file(candidate))
        return artifacts
    return []


def write_cognition_envelope(envelope: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(envelope, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return {"written": True, "output_path": str(path)}


def inspect_cognition_input(
    *,
    input_path: str | Path | None = None,
    output_path: str | Path | None = None,
    artifacts: Any = None,
) -> dict[str, Any]:
    loaded = _as_artifacts(artifacts)
    if not loaded:
        loaded = load_cognition_artifacts(input_path)
    envelope = build_cognition_state_envelope(loaded)
    result = {
        "command": "aigol cognition inspect",
        "input_path": str(input_path or ""),
        "artifact_count": len(loaded),
        "cognition_state_envelope": envelope,
        "read_only": True,
        "execution_authority_added": False,
        "orchestration_authority_added": False,
        "autonomous_continuation_added": False,
        "mutation_authority_added": False,
    }
    if output_path:
        result["output"] = write_cognition_envelope(envelope, output_path)
    return result


def render_cognition_summary(envelope: dict[str, Any]) -> str:
    matrix_lines = [
        f"  {entry.get('authority_name')}: {entry.get('status')}"
        for entry in envelope.get("authority_matrix", [])
    ]
    sections = [
        "Semantic State",
        f"  replay_identity: {envelope.get('replay_identity')}",
        f"  normalized_intent: {envelope.get('normalized_intent')}",
        f"  semantic_input_ref: {json.dumps(envelope.get('semantic_input_ref', {}), sort_keys=True)}",
        "Admissibility State",
        f"  {envelope.get('admissibility_state')}",
        "Authority Matrix",
        *matrix_lines,
        "Replay / Lineage State",
        f"  continuity_status: {envelope.get('continuity_status')}",
        f"  lineage_refs: {json.dumps(envelope.get('lineage_refs', {}), sort_keys=True)}",
        "Boundary State",
        f"  {envelope.get('current_boundary_state')}",
        "Reflection / Advisory State",
        f"  reflection_refs: {json.dumps(envelope.get('reflection_refs', []), sort_keys=True)}",
        "Allowed Next Transitions",
        f"  {', '.join(envelope.get('allowed_next_transitions', []))}",
        "Forbidden Transitions",
        f"  {', '.join(envelope.get('forbidden_transitions', []))}",
        "Continuity Status",
        f"  {envelope.get('continuity_status')}",
        "Authority Guarantees",
        "  execution_authority: false",
        "  orchestration_authority: false",
        "  autonomous_continuation: false",
        "  mutation_authority: false",
    ]
    return "\n".join(sections)


__all__ = [
    "ARTIFACT_TYPE",
    "SCHEMA_VERSION",
    "UNKNOWN",
    "build_cognition_state_envelope",
    "inspect_cognition_input",
    "load_cognition_artifacts",
    "render_cognition_summary",
    "write_cognition_envelope",
]
