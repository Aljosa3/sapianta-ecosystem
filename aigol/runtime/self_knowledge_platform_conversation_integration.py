"""Platform Core and Conversation integration for certified Self Knowledge.

Only explicit bounded request forms are accepted. The integration loads the
single checked-in manifest, composes and validates one snapshot, invokes the
G65-05 query owner, and transports its validated response without creating
authority or execution state.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.self_knowledge_evidence_manifest import (
    SELF_KNOWLEDGE_EVIDENCE_MANIFEST_PATH,
    validate_self_knowledge_evidence_manifest,
)
from aigol.runtime.self_knowledge_query_runtime import (
    SELF_KNOWLEDGE_QUERY_RESPONSE_V1,
    SUPPORTED_QUERY_SUBJECTS,
    create_self_knowledge_query_request,
    execute_self_knowledge_query,
    validate_self_knowledge_query_response,
)
from aigol.runtime.self_knowledge_snapshot_runtime import (
    build_self_knowledge_snapshot,
)
from aigol.runtime.self_knowledge_snapshot_validation_runtime import (
    validate_authenticated_self_knowledge_snapshot,
)
from aigol.runtime.transport.serialization import replay_hash


SELF_KNOWLEDGE_PLATFORM_CONVERSATION_INTEGRATION_VERSION = (
    "G65_06_SELF_KNOWLEDGE_PLATFORM_CONVERSATION_INTEGRATION_V1"
)
SELF_KNOWLEDGE_PLATFORM_CORE_RESPONSE_V1 = "SELF_KNOWLEDGE_PLATFORM_CORE_RESPONSE_V1"
SELF_KNOWLEDGE_CONVERSATION_REQUEST_V1 = "SELF_KNOWLEDGE_CONVERSATION_REQUEST_V1"
SELF_KNOWLEDGE_CONVERSATION_REQUEST_VERSION = (
    "G65_06_SELF_KNOWLEDGE_CONVERSATION_REQUEST_V1"
)

EXPLICIT_REQUEST_PREFIX = "/self-knowledge "
EXPLICIT_TOKEN_PREFIX = "SELF_KNOWLEDGE:"

SELF_KNOWLEDGE_INTEGRATION_BOUNDARY_FLAGS = {
    "read_only": True,
    "platform_core_knowledge_surface": True,
    "platform_knowledge_replaced": False,
    "conversation_request_render_only": True,
    "conversation_authority": False,
    "semantic_inference_performed": False,
    "objective_created": False,
    "commitment_created": False,
    "reuse_proof_created": False,
    "g47_evidence_created": False,
    "authorization_created": False,
    "worker_invoked": False,
    "provider_invoked": False,
    "execution_evidence_created": False,
    "replay_modified": False,
    "governance_modified": False,
}

_CONVERSATION_REQUEST_FIELDS = frozenset(
    {
        "artifact_type",
        "request_version",
        "request_text",
        "mapping_rule",
        "query_subject",
        "explicit_bounded_request",
        "conversation_authority",
        "request_hash",
    }
)
_INTEGRATION_RESPONSE_FIELDS = frozenset(
    {
        "artifact_type",
        "integration_version",
        "request_text",
        "conversation_request",
        "query_subject",
        "projection_status",
        "unavailable_reason",
        "snapshot_artifact_type",
        "snapshot_version",
        "snapshot_hash",
        "manifest_artifact_type",
        "manifest_version",
        "manifest_hash",
        "snapshot_validation_hash",
        "query_request_hash",
        "query_response",
        "source_references",
        "boundary_flags",
        "artifact_hash",
    }
)
_SOURCE_REFERENCE_FIELDS = frozenset(
    {
        "source_id",
        "source_class",
        "path",
        "sha256",
        "authority_class",
        "schema_or_section_identifier",
        "evidence_record_hash",
    }
)


def create_explicit_self_knowledge_conversation_request(request_text: str) -> dict[str, Any]:
    """Map one exact bounded interface form to one G65-05 subject."""

    if not isinstance(request_text, str) or not request_text:
        _fail("conversation request must be a non-empty string")
    subject, mapping_rule = _subject_from_explicit_request(request_text)
    request = {
        "artifact_type": SELF_KNOWLEDGE_CONVERSATION_REQUEST_V1,
        "request_version": SELF_KNOWLEDGE_CONVERSATION_REQUEST_VERSION,
        "request_text": request_text,
        "mapping_rule": mapping_rule,
        "query_subject": subject,
        "explicit_bounded_request": True,
        "conversation_authority": False,
    }
    request["request_hash"] = replay_hash(request)
    return request


def validate_explicit_self_knowledge_conversation_request(
    request: dict[str, Any],
) -> dict[str, Any]:
    """Validate exact request form, subject, non-authority, and identity."""

    if not isinstance(request, dict) or set(request) != _CONVERSATION_REQUEST_FIELDS:
        _fail("conversation request schema is invalid")
    expected = create_explicit_self_knowledge_conversation_request(request.get("request_text"))
    if request != expected:
        _fail("conversation request deterministic reconstruction mismatch")
    return deepcopy(request)


def run_platform_core_self_knowledge_query(
    *,
    request_text: str,
    repository_root: str | Path,
) -> dict[str, Any]:
    """Run one explicit read-only Self Knowledge request through Platform Core."""

    root = _repository_root(repository_root)
    conversation_request = create_explicit_self_knowledge_conversation_request(request_text)
    manifest = _load_authenticated_manifest(root)
    snapshot = build_self_knowledge_snapshot(
        manifest=manifest,
        repository_root=root,
    )
    snapshot_validation = validate_authenticated_self_knowledge_snapshot(
        snapshot=snapshot,
        manifest=manifest,
        repository_root=root,
    )
    query_request = create_self_knowledge_query_request(
        query_subject=conversation_request["query_subject"],
        snapshot=snapshot,
        snapshot_validation=snapshot_validation,
    )
    query_response = execute_self_knowledge_query(
        request=query_request,
        snapshot=snapshot,
        snapshot_validation=snapshot_validation,
    )
    validated_query_response = validate_self_knowledge_query_response(
        query_response,
        request=query_request,
        snapshot=snapshot,
        snapshot_validation=snapshot_validation,
    )
    response = {
        "artifact_type": SELF_KNOWLEDGE_PLATFORM_CORE_RESPONSE_V1,
        "integration_version": SELF_KNOWLEDGE_PLATFORM_CONVERSATION_INTEGRATION_VERSION,
        "request_text": request_text,
        "conversation_request": conversation_request,
        "query_subject": conversation_request["query_subject"],
        "projection_status": validated_query_response["projection_status"],
        "unavailable_reason": validated_query_response["unavailable_reason"],
        "snapshot_artifact_type": validated_query_response["snapshot_artifact_type"],
        "snapshot_version": validated_query_response["snapshot_version"],
        "snapshot_hash": validated_query_response["snapshot_hash"],
        "manifest_artifact_type": validated_query_response["manifest_artifact_type"],
        "manifest_version": validated_query_response["manifest_version"],
        "manifest_hash": validated_query_response["manifest_hash"],
        "snapshot_validation_hash": validated_query_response["snapshot_validation_hash"],
        "query_request_hash": validated_query_response["request_hash"],
        "query_response": validated_query_response,
        "source_references": _source_references(validated_query_response["facts"]),
        "boundary_flags": deepcopy(SELF_KNOWLEDGE_INTEGRATION_BOUNDARY_FLAGS),
    }
    response["artifact_hash"] = replay_hash(response)
    return response


def validate_platform_core_self_knowledge_response(
    response: dict[str, Any],
) -> dict[str, Any]:
    """Validate the transport envelope presented to Conversation."""

    if not isinstance(response, dict) or set(response) != _INTEGRATION_RESPONSE_FIELDS:
        _fail("Platform Core response schema is invalid")
    if response.get("artifact_type") != SELF_KNOWLEDGE_PLATFORM_CORE_RESPONSE_V1:
        _fail("Platform Core response artifact type is invalid")
    if response.get("integration_version") != (
        SELF_KNOWLEDGE_PLATFORM_CONVERSATION_INTEGRATION_VERSION
    ):
        _fail("Platform Core response version is invalid")
    conversation_request = validate_explicit_self_knowledge_conversation_request(
        response.get("conversation_request")
    )
    if response.get("request_text") != conversation_request["request_text"]:
        _fail("Platform Core response request text binding is invalid")
    if response.get("query_subject") != conversation_request["query_subject"]:
        _fail("Platform Core response subject binding is invalid")
    query_response = response.get("query_response")
    if not isinstance(query_response, dict) or query_response.get("artifact_type") != (
        SELF_KNOWLEDGE_QUERY_RESPONSE_V1
    ):
        _fail("Platform Core response query response is invalid")
    expected_bindings = {
        "projection_status": query_response.get("projection_status"),
        "unavailable_reason": query_response.get("unavailable_reason"),
        "snapshot_artifact_type": query_response.get("snapshot_artifact_type"),
        "snapshot_version": query_response.get("snapshot_version"),
        "snapshot_hash": query_response.get("snapshot_hash"),
        "manifest_artifact_type": query_response.get("manifest_artifact_type"),
        "manifest_version": query_response.get("manifest_version"),
        "manifest_hash": query_response.get("manifest_hash"),
        "snapshot_validation_hash": query_response.get("snapshot_validation_hash"),
        "query_request_hash": query_response.get("request_hash"),
    }
    for field, expected_value in expected_bindings.items():
        if response.get(field) != expected_value:
            _fail(f"Platform Core response {field} binding is invalid")
    query_body = deepcopy(query_response)
    query_hash = query_body.pop("response_hash", None)
    if query_hash != replay_hash(query_body):
        _fail("Platform Core query response hash mismatch")
    expected_references = _source_references(query_response.get("facts"))
    if response.get("source_references") != expected_references:
        _fail("Platform Core response source references are invalid")
    if response.get("boundary_flags") != SELF_KNOWLEDGE_INTEGRATION_BOUNDARY_FLAGS:
        _fail("Platform Core response boundary flags are invalid")
    body = deepcopy(response)
    artifact_hash = body.pop("artifact_hash", None)
    if artifact_hash != replay_hash(body):
        _fail("Platform Core response hash mismatch")
    return deepcopy(response)


def _load_authenticated_manifest(root: Path) -> dict[str, Any]:
    manifest_path = root / SELF_KNOWLEDGE_EVIDENCE_MANIFEST_PATH
    try:
        value = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FailClosedRuntimeError(
            "SELF_KNOWLEDGE_PLATFORM_INTEGRATION_INVALID: manifest cannot be loaded"
        ) from exc
    return validate_self_knowledge_evidence_manifest(value, root)


def _source_references(facts: Any) -> list[dict[str, Any]]:
    if not isinstance(facts, list):
        _fail("query response facts are invalid")
    references: list[dict[str, Any]] = []
    for fact in facts:
        if not isinstance(fact, dict):
            _fail("query response fact is invalid")
        reference = {
            "source_id": fact.get("source_id"),
            "source_class": fact.get("source_class"),
            "path": fact.get("path"),
            "sha256": fact.get("sha256"),
            "authority_class": fact.get("authority_class"),
            "schema_or_section_identifier": fact.get("schema_or_section_identifier"),
            "evidence_record_hash": fact.get("evidence_record_hash"),
        }
        if set(reference) != _SOURCE_REFERENCE_FIELDS or not all(
            isinstance(value, str) and value for value in reference.values()
        ):
            _fail("query response source reference is invalid")
        references.append(reference)
    return references


def _subject_from_explicit_request(request_text: str) -> tuple[str, str]:
    if request_text.startswith(EXPLICIT_REQUEST_PREFIX):
        subject = request_text.removeprefix(EXPLICIT_REQUEST_PREFIX)
        mapping_rule = "EXPLICIT_SLASH_COMMAND"
    elif request_text.startswith(EXPLICIT_TOKEN_PREFIX):
        subject = request_text.removeprefix(EXPLICIT_TOKEN_PREFIX)
        mapping_rule = "EXPLICIT_TOKEN_BINDING"
    else:
        _fail("request is not an explicit bounded Self Knowledge form")
    if subject not in SUPPORTED_QUERY_SUBJECTS:
        _fail("request subject is unknown, ambiguous, multi-subject, or unsupported")
    return subject, mapping_rule


def _repository_root(repository_root: str | Path) -> Path:
    root = Path(repository_root)
    if not root.is_dir():
        _fail("repository root is invalid")
    return root.resolve()


def _fail(message: str) -> None:
    raise FailClosedRuntimeError(f"SELF_KNOWLEDGE_PLATFORM_INTEGRATION_INVALID: {message}")


__all__ = [
    "EXPLICIT_REQUEST_PREFIX",
    "EXPLICIT_TOKEN_PREFIX",
    "SELF_KNOWLEDGE_CONVERSATION_REQUEST_V1",
    "SELF_KNOWLEDGE_CONVERSATION_REQUEST_VERSION",
    "SELF_KNOWLEDGE_INTEGRATION_BOUNDARY_FLAGS",
    "SELF_KNOWLEDGE_PLATFORM_CONVERSATION_INTEGRATION_VERSION",
    "SELF_KNOWLEDGE_PLATFORM_CORE_RESPONSE_V1",
    "create_explicit_self_knowledge_conversation_request",
    "run_platform_core_self_knowledge_query",
    "validate_explicit_self_knowledge_conversation_request",
    "validate_platform_core_self_knowledge_response",
]
