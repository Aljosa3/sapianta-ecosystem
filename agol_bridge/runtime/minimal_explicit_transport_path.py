"""Explicit file-based governed transport path for the minimal bridge.

This module provides an operator-visible local handoff path only. It performs
no networking, no orchestration, and no autonomous continuation. Execution,
when accepted by the canonical bridge runtime, is bounded to the Codex CLI
provider contract.
"""

from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from agol_bridge.runtime.minimal_end_to_end_bridge import (
    BRIDGE_ACCEPTED,
    export_minimal_bridge_result_artifact,
    run_minimal_end_to_end_bridge,
)
from agol_bridge.transport.local_governed_transport import canonical_hash

REQUEST_ARTIFACT_TYPE = "CHATGPT_PREPARED_GOVERNED_REQUEST"
REQUEST_SCHEMA_VERSION = 1
REQUEST_AUTHORITY_BOUNDARY = "SEMANTIC_TRANSPORT_ONLY_NO_APPROVAL_NO_DISPATCH_NO_EXECUTION"

TRANSPORT_PATH_EXPORTED = "TRANSPORT_PATH_EXPORTED"
TRANSPORT_PATH_REJECTED_SCHEMA = "TRANSPORT_PATH_REJECTED_SCHEMA"
TRANSPORT_PATH_REJECTED_HASH = "TRANSPORT_PATH_REJECTED_HASH"
TRANSPORT_PATH_REJECTED_AUTHORITY = "TRANSPORT_PATH_REJECTED_AUTHORITY"
TRANSPORT_PATH_REJECTED_RUNTIME = "TRANSPORT_PATH_REJECTED_RUNTIME"

ALLOWED_REQUESTED_MODES = {"READ_ONLY", "REVIEW_ONLY", "DEMO_ONLY"}
REJECTED_REQUESTED_MODES = {
    "EXECUTE",
    "AUTO_EXECUTE",
    "AUTONOMOUS",
    "PROVIDER_RUNTIME",
    "ORCHESTRATION",
}
HASH_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _hash_input(artifact: dict) -> dict:
    artifact_copy = _canonical_copy(artifact)
    artifact_copy.pop("artifact_hash", None)
    return artifact_copy


def create_minimal_governed_request_artifact(
    *,
    human_request: str,
    session_id: str,
    requested_mode: str = "REVIEW_ONLY",
) -> dict:
    """Create a deterministic governed request artifact for explicit handoff."""

    artifact = {
        "artifact_type": REQUEST_ARTIFACT_TYPE,
        "schema_version": REQUEST_SCHEMA_VERSION,
        "human_request": str(human_request or "").strip(),
        "session_id": str(session_id or "").strip(),
        "requested_mode": str(requested_mode or "").strip().upper(),
        "authority_boundary_statement": REQUEST_AUTHORITY_BOUNDARY,
        "created_by": "CHATGPT_PREPARED_ARTIFACT",
    }
    artifact["artifact_hash"] = canonical_hash(_hash_input(artifact))
    return artifact


def validate_minimal_governed_request_artifact(artifact: dict) -> dict:
    """Validate a ChatGPT-prepared governed request artifact fail-closed."""

    errors: list[str] = []
    if not isinstance(artifact, dict) or isinstance(artifact, list):
        return {
            "status": TRANSPORT_PATH_REJECTED_SCHEMA,
            "valid": False,
            "errors": ["governed request artifact must be a JSON object"],
            "hash_verified": False,
        }

    safe_artifact = _canonical_copy(artifact)
    if safe_artifact.get("artifact_type") != REQUEST_ARTIFACT_TYPE:
        errors.append("artifact_type must be CHATGPT_PREPARED_GOVERNED_REQUEST")
    if safe_artifact.get("schema_version") != REQUEST_SCHEMA_VERSION:
        errors.append("schema_version must be 1")
    if not isinstance(safe_artifact.get("human_request"), str) or not safe_artifact.get("human_request", "").strip():
        errors.append("human_request is required")
    if not isinstance(safe_artifact.get("session_id"), str) or not safe_artifact.get("session_id", "").strip():
        errors.append("session_id is required")

    requested_mode = str(safe_artifact.get("requested_mode", "")).strip().upper()
    if requested_mode in REJECTED_REQUESTED_MODES or requested_mode not in ALLOWED_REQUESTED_MODES:
        errors.append(f"unsupported requested_mode: {requested_mode or 'UNKNOWN'}")

    authority = str(safe_artifact.get("authority_boundary_statement", ""))
    normalized_authority = authority.lower().replace("_", " ")
    if not all(token in normalized_authority for token in ("semantic transport only", "no approval", "no dispatch", "no execution")):
        return {
            "status": TRANSPORT_PATH_REJECTED_AUTHORITY,
            "valid": False,
            "errors": ["authority boundary statement must preserve semantic transport only with no approval, dispatch, or execution"],
            "hash_verified": False,
        }

    if errors:
        return {
            "status": TRANSPORT_PATH_REJECTED_SCHEMA,
            "valid": False,
            "errors": errors,
            "hash_verified": False,
        }

    artifact_hash = safe_artifact.get("artifact_hash")
    if not isinstance(artifact_hash, str) or not HASH_PATTERN.match(artifact_hash):
        return {
            "status": TRANSPORT_PATH_REJECTED_HASH,
            "valid": False,
            "errors": ["artifact_hash is missing or malformed"],
            "hash_verified": False,
        }
    computed_hash = canonical_hash(_hash_input(safe_artifact))
    if computed_hash != artifact_hash:
        return {
            "status": TRANSPORT_PATH_REJECTED_HASH,
            "valid": False,
            "errors": ["artifact_hash mismatch"],
            "hash_verified": False,
            "computed_hash": computed_hash,
            "artifact_hash": artifact_hash,
        }

    return {
        "status": "REQUEST_ARTIFACT_VALID",
        "valid": True,
        "errors": [],
        "hash_verified": True,
        "computed_hash": computed_hash,
        "artifact_hash": artifact_hash,
    }


def run_minimal_explicit_governed_transport_path(*, request_artifact: dict) -> dict:
    """Run the explicit governed request artifact through the canonical bridge."""

    safe_request = _canonical_copy(request_artifact or {})
    validation = validate_minimal_governed_request_artifact(safe_request)
    if not validation["valid"]:
        return {
            "status": validation["status"],
            "request_validation": validation,
            "bridge_result": {},
            "result_artifact": {},
            "output_artifact_created": False,
            "governed_return_artifact": {
                "status": "REJECTED",
                "reason": "; ".join(validation["errors"]),
                "non_authority_reminder": "No approval, dispatch, orchestration, or autonomous continuation authority was created.",
            },
            "authority_guarantees": _authority_guarantees(),
        }

    bridge_result = run_minimal_end_to_end_bridge(
        human_request=safe_request["human_request"],
        session_id=safe_request["session_id"],
    )
    if bridge_result.get("status") != BRIDGE_ACCEPTED:
        return {
            "status": TRANSPORT_PATH_REJECTED_RUNTIME,
            "request_validation": validation,
            "bridge_result": bridge_result,
            "result_artifact": {},
            "output_artifact_created": False,
            "governed_return_artifact": bridge_result.get("governed_chat_return", {}),
            "authority_guarantees": _authority_guarantees(),
        }

    result_artifact = export_minimal_bridge_result_artifact(bridge_result)
    return {
        "status": TRANSPORT_PATH_EXPORTED,
        "request_validation": validation,
        "bridge_result": bridge_result,
        "result_artifact": result_artifact,
        "output_artifact_created": True,
        "governed_return_artifact": bridge_result["governed_chat_return"],
        "authority_guarantees": _authority_guarantees(),
    }


def run_minimal_explicit_governed_transport_path_file(*, input_path: str | Path, output_path: str | Path) -> dict:
    """Read an explicit request file and write an explicit result artifact file."""

    input_file = Path(input_path)
    output_file = Path(output_path)
    try:
        request_artifact = json.loads(input_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {
            "status": TRANSPORT_PATH_REJECTED_SCHEMA,
            "request_validation": {
                "status": TRANSPORT_PATH_REJECTED_SCHEMA,
                "valid": False,
                "errors": [f"could not read governed request artifact: {error}"],
                "hash_verified": False,
            },
            "bridge_result": {},
            "result_artifact": {},
            "output_path": str(output_file),
            "output_artifact_created": False,
            "governed_return_artifact": {
                "status": "REJECTED",
                "reason": "could not read governed request artifact",
                "non_authority_reminder": "No approval, dispatch, orchestration, or autonomous continuation authority was created.",
            },
            "authority_guarantees": _authority_guarantees(),
        }

    report = run_minimal_explicit_governed_transport_path(request_artifact=request_artifact)
    report["output_path"] = str(output_file)
    if report["status"] == TRANSPORT_PATH_EXPORTED:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(f"{_canonical_json(report['result_artifact'])}\n", encoding="utf-8")
    return report


def _authority_guarantees() -> dict:
    return {
        "provider_calls": "CODEX_CLI_ONLY",
        "dispatch": False,
        "approval": False,
        "execution": "BOUNDED_CODEX_CLI_ONLY",
        "endpoint": False,
        "server_listener": False,
        "orchestration": False,
        "autonomous_continuation": False,
        "durable_replay_backend": False,
    }


__all__ = [
    "REQUEST_ARTIFACT_TYPE",
    "REQUEST_AUTHORITY_BOUNDARY",
    "REQUEST_SCHEMA_VERSION",
    "TRANSPORT_PATH_EXPORTED",
    "TRANSPORT_PATH_REJECTED_AUTHORITY",
    "TRANSPORT_PATH_REJECTED_HASH",
    "TRANSPORT_PATH_REJECTED_RUNTIME",
    "TRANSPORT_PATH_REJECTED_SCHEMA",
    "create_minimal_governed_request_artifact",
    "run_minimal_explicit_governed_transport_path",
    "run_minimal_explicit_governed_transport_path_file",
    "validate_minimal_governed_request_artifact",
]
