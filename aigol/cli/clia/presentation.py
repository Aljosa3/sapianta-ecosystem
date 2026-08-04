"""Deterministic presentation of exact Canonical Human Entry responses."""

from __future__ import annotations

from copy import deepcopy
import json
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError

from .session import (
    CLIA_ADAPTER_IDENTITY,
    CLIA_CHANNEL_IDENTITY,
    CLIA_INTERFACE_NAME,
    CLIA_TRANSPORT_VERSION,
)


CLIA_RESPONSE_HEADING = "=== CLIA CANONICAL HUMAN ENTRY RESPONSE ==="


def validate_clia_che_response_v1(
    response: Any,
    *,
    transport_session_identity: str,
    submission_identity: str,
) -> dict[str, Any]:
    if not isinstance(response, dict):
        raise FailClosedRuntimeError("CLIA received a malformed CHE response")
    required_strings = {
        "canonical_runtime_entry_service_version": None,
        "canonical_runtime_entry_interface": CLIA_INTERFACE_NAME,
        "canonical_runtime_entry_session_id": transport_session_identity,
        "canonical_runtime_entry_status": None,
        "clia_transport_version": CLIA_TRANSPORT_VERSION,
        "clia_adapter_identity": CLIA_ADAPTER_IDENTITY,
        "clia_channel_identity": CLIA_CHANNEL_IDENTITY,
        "clia_transport_session_identity": transport_session_identity,
        "clia_submission_identity": submission_identity,
    }
    for field_name, expected in required_strings.items():
        value = response.get(field_name)
        if not isinstance(value, str) or not value.strip():
            raise FailClosedRuntimeError(
                f"CLIA CHE response field {field_name} is absent or malformed"
            )
        if expected is not None and value != expected:
            raise FailClosedRuntimeError(
                f"CLIA CHE response field {field_name} does not match transport state"
            )
    try:
        json.dumps(response, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    except (TypeError, ValueError) as exc:
        raise FailClosedRuntimeError(
            "CLIA CHE response is not deterministically presentable"
        ) from exc
    return deepcopy(response)


def render_clia_che_response_v1(response: dict[str, Any]) -> str:
    if not isinstance(response, dict):
        raise FailClosedRuntimeError("CLIA presentation requires a CHE response object")
    try:
        body = json.dumps(
            response,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
    except (TypeError, ValueError) as exc:
        raise FailClosedRuntimeError(
            "CLIA CHE response is not deterministically presentable"
        ) from exc
    return f"{CLIA_RESPONSE_HEADING}\n{body}"
