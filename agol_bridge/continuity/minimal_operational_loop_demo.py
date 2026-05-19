"""Minimal governed operational continuity demo using pure primitives only."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .continuity_report_synthesis import synthesize_continuity_report
from .envelope_validator import canonical_envelope_hash, canonical_hash, validate_envelope
from .validator_composition import compose_validators


def _task_package(user_request: str) -> dict:
    return {
        "task_id": "DEMO-TASK-1",
        "governance_mode": "governed_operational_continuity_demo",
        "risk_class": "read_only_demo",
        "approval_required": False,
        "codex_prompt": f"Demonstrate governed continuity for: {user_request}",
        "constraints": [
            "read-only observability only",
            "no provider calls",
            "no execution authority",
        ],
        "expected_outputs": [
            "envelope validation report",
            "validator composition report",
            "continuity report",
        ],
        "metadata": {"lifecycle_state": "RETURNED", "demo_layer": "MINIMAL_GOVERNED_OPERATIONAL_LOOP_RUNTIME_V1"},
    }


def _result_package() -> dict:
    return {
        "status": "DEMO_CONTINUITY_RENDERED",
        "tests": [],
        "files_changed": [],
        "artifacts": [],
        "summary": "Read-only governed operational continuity demo rendered.",
        "requires_human_review": True,
    }


def _replay_references() -> list[dict]:
    return [
        {"replay_id": "DEMO-REPLAY-ENVELOPE", "reference_status": "REFERENCED_NOT_MUTATED"},
        {"replay_id": "DEMO-REPLAY-COMPOSITION", "reference_status": "REFERENCED_NOT_MUTATED"},
        {"replay_id": "DEMO-REPLAY-CONTINUITY", "reference_status": "REFERENCED_NOT_MUTATED"},
    ]


def _replay_records() -> dict:
    return {
        "DEMO-REPLAY-ENVELOPE": {"event_type": "ENVELOPE_VALIDATED"},
        "DEMO-REPLAY-COMPOSITION": {"event_type": "VALIDATORS_COMPOSED"},
        "DEMO-REPLAY-CONTINUITY": {"event_type": "CONTINUITY_SYNTHESIZED"},
    }


def _lifecycle_references() -> list[dict]:
    return [
        {
            "previous_state": "CREATED",
            "next_state": "NORMALIZED",
            "reference_status": "VISIBLE_APPEND_ONLY_REFERENCE",
        },
        {
            "previous_state": "NORMALIZED",
            "next_state": "RETURNED",
            "reference_status": "VISIBLE_APPEND_ONLY_REFERENCE",
        },
    ]


def _lifecycle_records() -> list[dict]:
    return [
        {"previous_state": "CREATED", "next_state": "NORMALIZED"},
        {"previous_state": "NORMALIZED", "next_state": "RETURNED"},
    ]


def _authority_boundary_statement() -> str:
    return (
        "ChatGPT / LLMs provide semantic cognition only; AiGOL / AGOL governs admissibility, "
        "lifecycle, replay, and boundaries; Codex/providers execute only through governed transport; "
        "sidepanel observes only. VALID and CONTINUITY_VALID are not approval, dispatch, execution, "
        "or continuation authority."
    )


def _semantic_boundary_statement() -> dict:
    return {
        "statement": "Semantic direction is context only and remains non-authoritative.",
        "interpretation_status": "NON_AUTHORITATIVE",
        "semantic_replay_determinism": False,
        "semantic_authority": False,
    }


def _lineage_references(user_request: str) -> list[dict]:
    return [
        {
            "lineage_id": f"DEMO-LINEAGE-{canonical_hash({'request': user_request})[7:19]}",
            "demo_id": "MINIMAL_GOVERNED_OPERATIONAL_LOOP_RUNTIME_V1",
        }
    ]


def _envelope(user_request: str, task_package: dict, result_package: dict) -> dict:
    envelope = {
        "loop_id": "DEMO-LOOP-1",
        "originating_human_request_ref": {"request_text": user_request, "authority": "context_only"},
        "semantic_context_ref": {
            "source": "explicit local demo input",
            "reasoning_determinism": "NON_DETERMINISTIC_MODEL_NATIVE",
        },
        "task_package_ref": {"task_id": task_package["task_id"], "package_hash": canonical_hash(task_package)},
        "result_package_ref": {
            "result_id": "DEMO-RESULT-1",
            "originating_task_id": task_package["task_id"],
            "package_hash": canonical_hash(result_package),
        },
        "lineage_id": _lineage_references(user_request)[0]["lineage_id"],
        "execution_provider_ref": {
            "provider_id": "none",
            "provider_role": "EXECUTION_ONLY",
            "governance_authority": False,
            "approval_authority": False,
            "replay_mutation_authority": False,
            "transport_requirement": "governed transport only; no provider called in demo",
        },
        "governance_state_ref": {
            "lifecycle_state": "RETURNED",
            "approval_required": False,
            "demo_only": True,
        },
        "replay_refs": _replay_references(),
        "lifecycle_refs": _lifecycle_references(),
        "semantic_interpretation_boundary": _semantic_boundary_statement(),
        "next_step_ref": {"status": "PROPOSED_NOT_APPROVED", "approval_granted": False},
        "authority_boundary_statement": _authority_boundary_statement(),
        "created_at": "DETERMINISTIC-DEMO-TIME",
    }
    envelope["envelope_hash"] = canonical_envelope_hash(envelope)
    return envelope


def _artifact_map(task_package: dict, result_package: dict) -> dict:
    return {
        "task_packages": {task_package["task_id"]: deepcopy(task_package)},
        "result_packages": {"DEMO-RESULT-1": deepcopy(result_package)},
        "replay_records": _replay_records(),
        "lifecycle_records": _lifecycle_records(),
    }


def _render_sidepanel_sections(continuity_report: dict) -> dict:
    return {
        "continuity_findings": deepcopy(continuity_report["continuity_findings"]),
        "replay_lifecycle_visibility": {
            "replay": deepcopy(continuity_report["replay_visibility_summary"]),
            "lifecycle": deepcopy(continuity_report["lifecycle_visibility_summary"]),
        },
        "authority_boundary_visibility": deepcopy(continuity_report["authority_boundary_summary"]),
        "semantic_boundary_visibility": deepcopy(continuity_report["semantic_boundary_summary"]),
        "lineage_summary": deepcopy(continuity_report["lineage_summary"]),
        "observability_label": "Read-only sidepanel observability; no provider calls, approval, execution, or continuation.",
    }


def run_minimal_governed_operational_loop_demo(user_request: str) -> dict:
    request_text = str(user_request)
    task_package = _task_package(request_text)
    result_package = _result_package()
    envelope = _envelope(request_text, task_package, result_package)
    artifact_map = _artifact_map(task_package, result_package)

    envelope_validation_report = validate_envelope(envelope, artifact_map)
    validator_composition_report = compose_validators(
        envelope=envelope,
        artifact_map=artifact_map,
        validator_registry={"envelope_validation": validate_envelope},
        validator_ids=["envelope_validation"],
    )
    continuity_report = synthesize_continuity_report(
        envelope_validation_report=envelope_validation_report,
        validator_composition_report=validator_composition_report,
        replay_references=envelope["replay_refs"],
        lifecycle_references=envelope["lifecycle_refs"],
        semantic_boundary_statements=[envelope["semantic_interpretation_boundary"]],
        authority_boundary_statements=[envelope["authority_boundary_statement"]],
        lineage_references=_lineage_references(request_text),
        continuity_findings=[],
        continuity_risks=[],
    )

    return {
        "demo_id": "MINIMAL_GOVERNED_OPERATIONAL_LOOP_RUNTIME_V1",
        "operational_flow": [
            "User Request",
            "Envelope Validation",
            "Validator Composition",
            "Continuity Report Synthesis",
            "Replay/Lifecycle Visibility",
            "Sidepanel Observability",
        ],
        "input_boundary": {
            "explicit_local_input_only": True,
            "hidden_persistence": False,
            "provider_calls": False,
        },
        "artifacts": {
            "envelope": deepcopy(envelope),
            "artifact_map": deepcopy(artifact_map),
        },
        "envelope_validation_report": deepcopy(envelope_validation_report),
        "validator_composition_report": deepcopy(validator_composition_report),
        "continuity_report": deepcopy(continuity_report),
        "sidepanel_rendering": _render_sidepanel_sections(continuity_report),
        "authority_guarantees": {
            "provider_calls": False,
            "dispatch": False,
            "approval": False,
            "execution": False,
            "lifecycle_mutation": False,
            "replay_mutation": False,
            "persistence": False,
            "orchestration": False,
            "autonomous_continuation": False,
            "hidden_authority": False,
        },
    }


__all__ = ["run_minimal_governed_operational_loop_demo"]
