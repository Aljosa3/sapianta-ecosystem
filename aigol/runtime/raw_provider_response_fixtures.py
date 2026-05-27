"""Deterministic raw provider response fixtures for replay-safe normalization tests.

These fixtures are provider-agnostic raw response strings - they may be fed
into any provider adapter that wraps the live governed cognition runtime.
They are append-only, deterministic, contain only constant literal payloads,
no runtime-generated timestamps, and require no network access.

Each fixture is registered in `RAW_PROVIDER_RESPONSE_FIXTURES`. The
accompanying `EXPECTED_OUTCOMES` annotation describes the deterministic
classification the bounded extraction layer must emit for each fixture.
"""

from __future__ import annotations

import json
from types import MappingProxyType
from typing import Any

from aigol.runtime.bounded_extraction_layer import (
    NORMALIZATION_FAILURE_EMPTY_RESPONSE,
    NORMALIZATION_FAILURE_INVALID_JSON,
    NORMALIZATION_FAILURE_MIXED_CONTENT,
    NORMALIZATION_FAILURE_NONE,
    NORMALIZED,
    REJECTED,
    SCHEMA_FAILURE_EXTRA_FIELDS,
    SCHEMA_FAILURE_MISSING_FIELDS,
    SCHEMA_FAILURE_NONE,
    SCHEMA_FAILURE_UNAUTHORIZED_CAPABILITY,
    STAGE_BOUNDED_NORMALIZATION,
    STAGE_JSON_PARSE,
    STAGE_RAW_INPUT,
    STAGE_SCHEMA_VALIDATION,
)


FIXTURE_CREATED_AT = "2026-01-01T00:00:00+00:00"


# Names are sortable, deterministic, and append-only.
FIXTURE_VALID_BOUNDED_PROPOSAL = "valid_bounded_proposal"
FIXTURE_MALFORMED_JSON = "malformed_json"
FIXTURE_MIXED_PROSE_AND_JSON = "mixed_prose_and_json"
FIXTURE_SCHEMA_DRIFT = "schema_drift"
FIXTURE_PARTIAL_PROPOSAL = "partial_bounded_proposal"
FIXTURE_INVALID_CAPABILITY_ESCALATION = "invalid_capability_escalation"
FIXTURE_EMPTY_RESPONSE = "empty_response"
FIXTURE_NON_JSON_OBJECT = "non_json_object"


def _canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


_VALID_BOUNDED_PROPOSAL_PAYLOAD = {
    "proposal_id": "FIXTURE-PROPOSAL-VALID",
    "natural_language_input": "Inspect bounded runtime metadata.",
    "proposal_type": "CONTRACT_PROPOSAL",
    "requested_capabilities": ["metadata_inspection_provider"],
    "proposed_contract_reference": "contract:FIXTURE-CONTRACT-VALID",
    "created_at": FIXTURE_CREATED_AT,
}

_SCHEMA_DRIFT_PAYLOAD = {
    "proposal_id": "FIXTURE-PROPOSAL-DRIFT",
    "natural_language_input": "Inspect bounded runtime metadata.",
    "proposal_type": "CONTRACT_PROPOSAL",
    "requested_capabilities": ["metadata_inspection_provider"],
    "proposed_contract_reference": "contract:FIXTURE-CONTRACT-DRIFT",
    "created_at": FIXTURE_CREATED_AT,
    "unexpected_drift_field": "should not be present",
}

_PARTIAL_PAYLOAD = {
    "proposal_id": "FIXTURE-PROPOSAL-PARTIAL",
    "natural_language_input": "Inspect bounded runtime metadata.",
    # proposal_type intentionally missing
    "requested_capabilities": ["metadata_inspection_provider"],
    "proposed_contract_reference": "contract:FIXTURE-CONTRACT-PARTIAL",
    # created_at intentionally missing
}

_CAPABILITY_ESCALATION_PAYLOAD = {
    "proposal_id": "FIXTURE-PROPOSAL-ESCALATION",
    "natural_language_input": "Escalate capability beyond readonly inspection.",
    "proposal_type": "CONTRACT_PROPOSAL",
    "requested_capabilities": ["readonly_http_get_provider", "metadata_inspection_provider"],
    "proposed_contract_reference": "contract:FIXTURE-CONTRACT-ESCALATION",
    "created_at": FIXTURE_CREATED_AT,
}


RAW_VALID_BOUNDED_PROPOSAL: str = _canonical_json(_VALID_BOUNDED_PROPOSAL_PAYLOAD)
# Starts with { and ends with } but is not valid JSON (unquoted token).
RAW_MALFORMED_JSON: str = '{"proposal_id": malformed-token-without-quotes}'
RAW_MIXED_PROSE_AND_JSON: str = (
    "Sure! Here's the JSON: "
    + _canonical_json(
        {
            "proposal_id": "FIXTURE-PROPOSAL-MIXED",
            "natural_language_input": "Inspect bounded runtime metadata.",
            "proposal_type": "CONTRACT_PROPOSAL",
            "requested_capabilities": ["metadata_inspection_provider"],
            "proposed_contract_reference": "contract:FIXTURE-CONTRACT-MIXED",
            "created_at": FIXTURE_CREATED_AT,
        }
    )
)
RAW_SCHEMA_DRIFT: str = _canonical_json(_SCHEMA_DRIFT_PAYLOAD)
RAW_PARTIAL_PROPOSAL: str = _canonical_json(_PARTIAL_PAYLOAD)
RAW_INVALID_CAPABILITY_ESCALATION: str = _canonical_json(_CAPABILITY_ESCALATION_PAYLOAD)
RAW_EMPTY_RESPONSE: str = ""
RAW_NON_JSON_OBJECT: str = "42"


# Outcome annotations document the deterministic classification the bounded
# extraction layer must produce for each fixture. They are used by tests; not
# by the extraction layer itself.
EXPECTED_OUTCOMES: MappingProxyType[str, MappingProxyType[str, str]] = MappingProxyType(
    {
        FIXTURE_VALID_BOUNDED_PROPOSAL: MappingProxyType(
            {
                "extraction_status": NORMALIZED,
                "extraction_stage": STAGE_BOUNDED_NORMALIZATION,
                "normalization_failure_type": NORMALIZATION_FAILURE_NONE,
                "schema_failure_type": SCHEMA_FAILURE_NONE,
            }
        ),
        FIXTURE_MALFORMED_JSON: MappingProxyType(
            {
                "extraction_status": REJECTED,
                "extraction_stage": STAGE_JSON_PARSE,
                "normalization_failure_type": NORMALIZATION_FAILURE_INVALID_JSON,
                "schema_failure_type": SCHEMA_FAILURE_NONE,
            }
        ),
        FIXTURE_MIXED_PROSE_AND_JSON: MappingProxyType(
            {
                "extraction_status": REJECTED,
                "extraction_stage": STAGE_JSON_PARSE,
                "normalization_failure_type": NORMALIZATION_FAILURE_MIXED_CONTENT,
                "schema_failure_type": SCHEMA_FAILURE_NONE,
            }
        ),
        FIXTURE_SCHEMA_DRIFT: MappingProxyType(
            {
                "extraction_status": REJECTED,
                "extraction_stage": STAGE_SCHEMA_VALIDATION,
                "normalization_failure_type": NORMALIZATION_FAILURE_NONE,
                "schema_failure_type": SCHEMA_FAILURE_EXTRA_FIELDS,
            }
        ),
        FIXTURE_PARTIAL_PROPOSAL: MappingProxyType(
            {
                "extraction_status": REJECTED,
                "extraction_stage": STAGE_SCHEMA_VALIDATION,
                "normalization_failure_type": NORMALIZATION_FAILURE_NONE,
                "schema_failure_type": SCHEMA_FAILURE_MISSING_FIELDS,
            }
        ),
        FIXTURE_INVALID_CAPABILITY_ESCALATION: MappingProxyType(
            {
                "extraction_status": REJECTED,
                "extraction_stage": STAGE_SCHEMA_VALIDATION,
                "normalization_failure_type": NORMALIZATION_FAILURE_NONE,
                "schema_failure_type": SCHEMA_FAILURE_UNAUTHORIZED_CAPABILITY,
            }
        ),
        FIXTURE_EMPTY_RESPONSE: MappingProxyType(
            {
                "extraction_status": REJECTED,
                "extraction_stage": STAGE_RAW_INPUT,
                "normalization_failure_type": NORMALIZATION_FAILURE_EMPTY_RESPONSE,
                "schema_failure_type": SCHEMA_FAILURE_NONE,
            }
        ),
        FIXTURE_NON_JSON_OBJECT: MappingProxyType(
            {
                "extraction_status": REJECTED,
                "extraction_stage": STAGE_JSON_PARSE,
                "normalization_failure_type": NORMALIZATION_FAILURE_MIXED_CONTENT,
                "schema_failure_type": SCHEMA_FAILURE_NONE,
            }
        ),
    }
)


RAW_PROVIDER_RESPONSE_FIXTURES: MappingProxyType[str, str] = MappingProxyType(
    {
        FIXTURE_VALID_BOUNDED_PROPOSAL: RAW_VALID_BOUNDED_PROPOSAL,
        FIXTURE_MALFORMED_JSON: RAW_MALFORMED_JSON,
        FIXTURE_MIXED_PROSE_AND_JSON: RAW_MIXED_PROSE_AND_JSON,
        FIXTURE_SCHEMA_DRIFT: RAW_SCHEMA_DRIFT,
        FIXTURE_PARTIAL_PROPOSAL: RAW_PARTIAL_PROPOSAL,
        FIXTURE_INVALID_CAPABILITY_ESCALATION: RAW_INVALID_CAPABILITY_ESCALATION,
        FIXTURE_EMPTY_RESPONSE: RAW_EMPTY_RESPONSE,
        FIXTURE_NON_JSON_OBJECT: RAW_NON_JSON_OBJECT,
    }
)


def fixture_names() -> tuple[str, ...]:
    """Return the deterministic, sorted fixture name list."""

    return tuple(sorted(RAW_PROVIDER_RESPONSE_FIXTURES))
