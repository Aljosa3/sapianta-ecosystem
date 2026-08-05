"""Deterministic presentation of exact Canonical Human Entry responses."""

from __future__ import annotations

from copy import deepcopy
import json
from typing import Any

from aigol.runtime.canonical_human_entry_contract_v1 import (
    CanonicalHumanEntryResponseEnvelopeV1,
    validate_canonical_che_response_envelope_v1,
)
from aigol.runtime.models import FailClosedRuntimeError

CLIA_RESPONSE_HEADING = "=== CLIA CANONICAL HUMAN ENTRY RESPONSE ==="


def validate_clia_che_response_v1(
    response: Any,
    *,
    transport_session_identity: str,
    submission_identity: str,
) -> dict[str, Any]:
    canonical = validate_canonical_che_response_envelope_v1(response)
    expected_request_identity = f"{submission_identity}:CHE-REQUEST"
    if canonical.request_identity != expected_request_identity:
        raise FailClosedRuntimeError(
            "CLIA CHE Response does not match the submitted Request"
        )
    continuation = canonical.continuation_envelope
    if continuation is not None and (
        continuation.session_identity != transport_session_identity
    ):
        raise FailClosedRuntimeError(
            "CLIA CHE Continuation does not match the transport session"
        )
    response_dict = canonical.to_dict()
    try:
        json.dumps(
            response_dict,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
    except (TypeError, ValueError) as exc:
        raise FailClosedRuntimeError(
            "CLIA CHE response is not deterministically presentable"
        ) from exc
    return deepcopy(response_dict)


def render_clia_che_response_v1(
    response: CanonicalHumanEntryResponseEnvelopeV1 | dict[str, Any],
) -> str:
    canonical = validate_canonical_che_response_envelope_v1(response)
    try:
        body = json.dumps(
            canonical.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
    except (TypeError, ValueError) as exc:
        raise FailClosedRuntimeError(
            "CLIA CHE response is not deterministically presentable"
        ) from exc
    return f"{CLIA_RESPONSE_HEADING}\n{body}"
