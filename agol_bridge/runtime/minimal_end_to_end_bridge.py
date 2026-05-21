"""Minimal end-to-end governed bridge lifecycle runtime.

This module composes existing bounded primitives into the first operational
bridge lifecycle. It performs no IO, no provider calls, and no real execution.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from agol_bridge.chat_first.chat_first_normalization import prepare_chat_first_transport_envelope
from agol_bridge.schema_validator import validate_result_package, validate_task_package
from agol_bridge.transport.local_governed_transport import (
    TRANSPORT_ACCEPTED,
    canonical_hash,
    handle_local_governed_transport,
)

BRIDGE_ACCEPTED = "BRIDGE_ACCEPTED"
BRIDGE_REJECTED = "BRIDGE_REJECTED"
MOCK_CODEX_RESULT_STATUS = "MOCK_CODEX_RESULT_RETURNED"
RESULT_VALIDATED = "RESULT_VALIDATED"
RESULT_REJECTED = "RESULT_REJECTED"
SESSION_ID_MIN_LENGTH = 3
BRIDGE_RESULT_ARTIFACT_TYPE = "MINIMAL_END_TO_END_BRIDGE_RESULT"
BRIDGE_RESULT_ARTIFACT_SCHEMA_VERSION = 1
BRIDGE_RESULT_ARTIFACT_AUTHORITY = "NON_EXECUTING_NON_AUTHORITATIVE"

NON_AUTHORITY_GUARANTEES = (
    "CHATGPT_SEMANTIC_COGNITION_ADVISORY_ONLY",
    "AIGOL_VALIDATION_REQUIRED",
    "SEMANTIC_TRANSPORT_ONLY",
    "MOCK_CODEX_ONLY_NO_PROVIDER_EXECUTION",
    "NO_DISPATCH_AUTHORITY",
    "NO_APPROVAL_AUTHORITY",
    "NO_EXECUTION_AUTHORITY",
    "NO_ORCHESTRATION",
    "NO_AUTONOMOUS_CONTINUATION",
    "NO_DURABLE_PERSISTENCE",
)

UNSAFE_MODE_TOKENS = (
    "EXECUTE",
    "AUTO_EXECUTE",
    "AUTONOMOUS",
    "PROVIDER_RUNTIME",
    "ORCHESTRATION",
)


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _session_registry(session_id: str) -> dict:
    session_text = str(session_id or "").strip()
    if len(session_text) < SESSION_ID_MIN_LENGTH or session_text in {"UNKNOWN", "AMBIGUOUS", "INVALID"}:
        return {}
    return {
        session_text: {
            "operator_visible": True,
            "ambiguous": False,
            "continuation_requested": False,
            "cross_session_mutation": False,
        }
    }


def _unsafe_requested_mode_from_text(human_request: str) -> str | None:
    request_text = str(human_request or "").upper()
    for token in UNSAFE_MODE_TOKENS:
        if token in request_text:
            return token
    return None


def _replay_event(*, event_type: str, status: str, session_id: str, proposal_id: str, payload: dict) -> dict:
    seed = {
        "event_type": event_type,
        "payload": payload,
        "proposal_id": proposal_id,
        "session_id": session_id,
        "status": status,
    }
    return {
        "replay_event_id": f"BRIDGE-REPLAY-{canonical_hash(seed)[7:31]}",
        "event_type": event_type,
        "status": status,
        "session_id": session_id,
        "proposal_id": proposal_id,
        "payload_hash": canonical_hash(payload),
        "visibility": "SESSION_LOCAL_REPLAY_VISIBLE",
        "mutation": False,
        "durable_persistence": False,
    }


def _rejected_result(*, session_id: str, proposal_id: str, transport_status: str, reason: str, replay_events: list[dict]) -> dict:
    governed_return = {
        "status": "REJECTED",
        "reason": reason,
        "replay_visibility": "SESSION_LOCAL_REPLAY_VISIBLE",
        "next_recommended_step": "Revise the request or session binding and rerun the governed bridge.",
        "non_authority_reminder": "No execution occurred. No provider was invoked. No approval, dispatch, or continuation authority was created.",
    }
    return {
        "status": BRIDGE_REJECTED,
        "session_id": session_id or "UNKNOWN",
        "proposal_id": proposal_id or "UNKNOWN",
        "transport_status": transport_status,
        "task_package": {},
        "mock_codex_result": {},
        "result_validation": {"status": RESULT_REJECTED, "valid": False, "errors": [reason]},
        "governed_chat_return": governed_return,
        "replay_events": replay_events,
        "operator_visibility": {
            "runtime_state_visible": True,
            "transport_status_visible": True,
            "task_package_visible": False,
            "mock_result_visible": False,
            "result_validation_visible": True,
            "chat_return_visible": True,
            "replay_visible": True,
        },
        "non_authority_guarantees": list(NON_AUTHORITY_GUARANTEES),
    }


def _task_package(*, proposal: dict, session_id: str, transport_report: dict) -> dict:
    task_seed = {
        "proposal_id": proposal["proposal_id"],
        "session_id": session_id,
        "transport_id": transport_report["transport_id"],
    }
    return {
        "task_id": f"BRIDGE-TASK-{canonical_hash(task_seed)[7:31]}",
        "governance_mode": "governed_execution_bridge_mock_only",
        "risk_class": proposal.get("risk_class", "LOW"),
        "approval_required": False,
        "codex_prompt": f"MOCK ONLY: summarize bounded review for proposal {proposal['proposal_id']}.",
        "constraints": [
            "mock Codex result only",
            "no provider call",
            "no dispatch",
            "no approval",
            "no execution authority",
            "no orchestration",
            "no autonomous continuation",
            "session-local replay visibility only",
        ],
        "expected_outputs": [
            "mock bounded result artifact",
            "result validation report",
            "ChatGPT-facing governed return summary",
        ],
        "metadata": {
            "session_id": session_id,
            "proposal_id": proposal["proposal_id"],
            "transport_status": transport_report["status"],
            "transport_replay_event_id": transport_report["replay_event_id"],
            "lifecycle_state": "TASK_PACKAGED",
            "approved": False,
            "execution_provider": "MOCK_CODEX_ONLY",
            "authority": "NO_EXECUTION_AUTHORITY",
        },
    }


def _mock_codex_result(*, task_package: dict, proposal: dict, session_id: str) -> dict:
    result_seed = {
        "proposal_id": proposal["proposal_id"],
        "session_id": session_id,
        "task_id": task_package["task_id"],
    }
    return {
        "result_id": f"MOCK-CODEX-RESULT-{canonical_hash(result_seed)[7:31]}",
        "task_id": task_package["task_id"],
        "proposal_id": proposal["proposal_id"],
        "session_id": session_id,
        "status": MOCK_CODEX_RESULT_STATUS,
        "tests": [
            {
                "name": "mock_bounded_codex_lifecycle",
                "status": "PASS",
                "execution": "MOCK_ONLY",
            }
        ],
        "files_changed": [],
        "artifacts": [
            {
                "artifact_id": f"MOCK-ARTIFACT-{canonical_hash(result_seed)[7:23]}",
                "artifact_type": "bounded_mock_codex_summary",
                "proposal_id": proposal["proposal_id"],
            }
        ],
        "summary": f"Mock bounded Codex result for: {proposal['human_request']}",
        "requires_human_review": True,
        "provider_invoked": False,
        "execution_authority_created": False,
        "orchestration_created": False,
    }


def _result_package(mock_result: dict) -> dict:
    return {
        "status": mock_result["status"],
        "tests": _canonical_copy(mock_result["tests"]),
        "files_changed": _canonical_copy(mock_result["files_changed"]),
        "artifacts": _canonical_copy(mock_result["artifacts"]),
        "summary": mock_result["summary"],
        "requires_human_review": mock_result["requires_human_review"],
    }


def _validate_bridge_result(*, result_package: dict, mock_result: dict, task_package: dict, session_id: str, proposal_id: str) -> dict:
    schema_validation = validate_result_package(result_package)
    errors = list(schema_validation["errors"])
    if mock_result.get("task_id") != task_package.get("task_id"):
        errors.append({"field": "task_id", "error": "result task lineage mismatch"})
    if mock_result.get("session_id") != session_id:
        errors.append({"field": "session_id", "error": "result session mismatch"})
    if mock_result.get("proposal_id") != proposal_id:
        errors.append({"field": "proposal_id", "error": "result proposal mismatch"})
    if mock_result.get("provider_invoked") is not False:
        errors.append({"field": "provider_invoked", "error": "provider invocation is forbidden"})
    if mock_result.get("execution_authority_created") is not False:
        errors.append({"field": "execution_authority_created", "error": "execution authority is forbidden"})
    if mock_result.get("orchestration_created") is not False:
        errors.append({"field": "orchestration_created", "error": "orchestration is forbidden"})
    valid = schema_validation["valid"] and not errors
    return {
        "status": RESULT_VALIDATED if valid else RESULT_REJECTED,
        "valid": valid,
        "errors": errors,
        "checks": {
            "schema_valid": schema_validation["valid"],
            "result_lineage": mock_result.get("task_id") == task_package.get("task_id"),
            "session_match": mock_result.get("session_id") == session_id,
            "proposal_linkage": mock_result.get("proposal_id") == proposal_id,
            "bounded_lifecycle": task_package.get("metadata", {}).get("lifecycle_state") == "TASK_PACKAGED",
            "replay_visibility": True,
            "non_authority_semantics": (
                mock_result.get("provider_invoked") is False
                and mock_result.get("execution_authority_created") is False
                and mock_result.get("orchestration_created") is False
            ),
        },
    }


def _governed_chat_return(*, accepted: bool, reason: str, task_package: dict | None = None) -> dict:
    return {
        "status": "ACCEPTED" if accepted else "REJECTED",
        "reason": reason,
        "replay_visibility": "SESSION_LOCAL_REPLAY_VISIBLE",
        "next_recommended_step": (
            "Review the bounded task and mock result evidence before any separate governed action."
            if accepted
            else "Revise the request or session binding and rerun the governed bridge."
        ),
        "task_id": (task_package or {}).get("task_id", "NONE"),
        "non_authority_reminder": "No execution occurred. No provider was invoked. No approval, dispatch, or continuation authority was created.",
    }


def _artifact_hash_input(artifact: dict) -> dict:
    artifact_copy = _canonical_copy(artifact)
    artifact_copy.pop("artifact_hash", None)
    return artifact_copy


def export_minimal_bridge_result_artifact(result: dict) -> dict:
    """Create a canonical in-memory artifact for sidepanel import.

    The helper performs no filesystem writes. The returned artifact is the
    canonical Python runtime result handoff object; its hash excludes the
    ``artifact_hash`` field itself.
    """

    result_copy = _canonical_copy(result or {})
    artifact = {
        "artifact_type": BRIDGE_RESULT_ARTIFACT_TYPE,
        "schema_version": BRIDGE_RESULT_ARTIFACT_SCHEMA_VERSION,
        "authority": BRIDGE_RESULT_ARTIFACT_AUTHORITY,
        "canonical_source": "PYTHON_MINIMAL_END_TO_END_BRIDGE_RUNTIME_V1",
        "status": result_copy.get("status", "UNKNOWN"),
        "session_id": result_copy.get("session_id", "UNKNOWN"),
        "proposal_id": result_copy.get("proposal_id", "UNKNOWN"),
        "transport_status": result_copy.get("transport_status", "UNKNOWN"),
        "replay_events": _canonical_copy(result_copy.get("replay_events", [])),
        "task_package": _canonical_copy(result_copy.get("task_package", {})),
        "mock_codex_result": _canonical_copy(result_copy.get("mock_codex_result", {})),
        "result_validation": _canonical_copy(result_copy.get("result_validation", {})),
        "governed_chat_return": _canonical_copy(result_copy.get("governed_chat_return", {})),
        "operator_visibility": _canonical_copy(result_copy.get("operator_visibility", {})),
        "non_authority_guarantees": _canonical_copy(result_copy.get("non_authority_guarantees", [])),
    }
    artifact["artifact_hash"] = canonical_hash(_artifact_hash_input(artifact))
    return artifact


def run_minimal_end_to_end_bridge(*, human_request: str, session_id: str) -> dict:
    """Run the first bounded local governed bridge lifecycle."""

    request_text = str(human_request or "").strip()
    session_text = str(session_id or "").strip()
    replay_events: list[dict] = []

    unsafe_mode = _unsafe_requested_mode_from_text(request_text)
    if unsafe_mode is not None:
        replay_events.append(
            _replay_event(
                event_type="SEMANTIC_PROPOSAL_REJECTED",
                status=BRIDGE_REJECTED,
                session_id=session_text or "UNKNOWN",
                proposal_id="UNKNOWN",
                payload={"reason": f"unsupported or unsafe requested mode: {unsafe_mode}"},
            )
        )
        return _rejected_result(
            session_id=session_text,
            proposal_id="UNKNOWN",
            transport_status="NOT_PREPARED",
            reason=f"unsupported or unsafe requested mode: {unsafe_mode}",
            replay_events=replay_events,
        )

    try:
        envelope = prepare_chat_first_transport_envelope(
            human_request=request_text,
            session_id=session_text,
            requested_mode="REVIEW_ONLY",
        )
    except ValueError as error:
        replay_events.append(
            _replay_event(
                event_type="SEMANTIC_PROPOSAL_REJECTED",
                status=BRIDGE_REJECTED,
                session_id=session_text or "UNKNOWN",
                proposal_id="UNKNOWN",
                payload={"reason": str(error)},
            )
        )
        return _rejected_result(
            session_id=session_text,
            proposal_id="UNKNOWN",
            transport_status="NOT_PREPARED",
            reason=str(error),
            replay_events=replay_events,
        )

    proposal = envelope["semantic_proposal"]
    replay_events.append(
        _replay_event(
            event_type="SEMANTIC_PROPOSAL_NORMALIZED",
            status="NORMALIZED",
            session_id=session_text,
            proposal_id=proposal["proposal_id"],
            payload=proposal,
        )
    )

    transport_report = handle_local_governed_transport(
        envelope=envelope,
        session_registry=_session_registry(session_text),
    )
    replay_events.append(
        _replay_event(
            event_type="LOCAL_GOVERNED_TRANSPORT_VALIDATED",
            status=transport_report["status"],
            session_id=session_text or "UNKNOWN",
            proposal_id=proposal["proposal_id"],
            payload=transport_report,
        )
    )
    if transport_report["status"] != TRANSPORT_ACCEPTED:
        return _rejected_result(
            session_id=session_text,
            proposal_id=proposal["proposal_id"],
            transport_status=transport_report["status"],
            reason=transport_report["rejection_reason"],
            replay_events=replay_events,
        )

    task_package = _task_package(proposal=proposal, session_id=session_text, transport_report=transport_report)
    task_validation = validate_task_package(task_package)
    replay_events.append(
        _replay_event(
            event_type="GOVERNED_TASK_PACKAGE_CREATED",
            status="TASK_PACKAGE_VALID" if task_validation["valid"] else "TASK_PACKAGE_REJECTED",
            session_id=session_text,
            proposal_id=proposal["proposal_id"],
            payload={"task_package": task_package, "validation": task_validation},
        )
    )
    if not task_validation["valid"]:
        return _rejected_result(
            session_id=session_text,
            proposal_id=proposal["proposal_id"],
            transport_status=transport_report["status"],
            reason="task package validation failed",
            replay_events=replay_events,
        )

    mock_result = _mock_codex_result(task_package=task_package, proposal=proposal, session_id=session_text)
    replay_events.append(
        _replay_event(
            event_type="MOCK_CODEX_RESULT_CREATED",
            status=mock_result["status"],
            session_id=session_text,
            proposal_id=proposal["proposal_id"],
            payload=mock_result,
        )
    )

    result_package = _result_package(mock_result)
    result_validation = _validate_bridge_result(
        result_package=result_package,
        mock_result=mock_result,
        task_package=task_package,
        session_id=session_text,
        proposal_id=proposal["proposal_id"],
    )
    replay_events.append(
        _replay_event(
            event_type="GOVERNED_RESULT_VALIDATED",
            status=result_validation["status"],
            session_id=session_text,
            proposal_id=proposal["proposal_id"],
            payload=result_validation,
        )
    )

    if not result_validation["valid"]:
        return _rejected_result(
            session_id=session_text,
            proposal_id=proposal["proposal_id"],
            transport_status=transport_report["status"],
            reason="result validation failed",
            replay_events=replay_events,
        )

    return {
        "status": BRIDGE_ACCEPTED,
        "session_id": session_text,
        "proposal_id": proposal["proposal_id"],
        "transport_status": transport_report["status"],
        "task_package": task_package,
        "mock_codex_result": mock_result,
        "result_validation": result_validation,
        "governed_chat_return": _governed_chat_return(
            accepted=True,
            reason="governed bridge lifecycle accepted with mocked bounded Codex result",
            task_package=task_package,
        ),
        "replay_events": replay_events,
        "operator_visibility": {
            "runtime_state_visible": True,
            "transport_status_visible": True,
            "task_package_visible": True,
            "mock_result_visible": True,
            "result_validation_visible": True,
            "chat_return_visible": True,
            "replay_visible": True,
        },
        "non_authority_guarantees": list(NON_AUTHORITY_GUARANTEES),
    }


__all__ = [
    "BRIDGE_ACCEPTED",
    "BRIDGE_REJECTED",
    "BRIDGE_RESULT_ARTIFACT_AUTHORITY",
    "BRIDGE_RESULT_ARTIFACT_SCHEMA_VERSION",
    "BRIDGE_RESULT_ARTIFACT_TYPE",
    "MOCK_CODEX_RESULT_STATUS",
    "RESULT_REJECTED",
    "RESULT_VALIDATED",
    "export_minimal_bridge_result_artifact",
    "run_minimal_end_to_end_bridge",
]
