"""Canonical Platform Core capability lookup helpers for G8 previews."""

from __future__ import annotations

from copy import deepcopy

from aigol.runtime.models import FailClosedRuntimeError


PLATFORM_CORE_CAPABILITY_LOOKUP_VERSION = "G8_06D_PLATFORM_CORE_CAPABILITY_LOOKUP_V1"

SUPPORTED_READONLY_CAPABILITIES: dict[str, dict[str, str]] = {
    "replay_inspection": {
        "worker_id": "ACLI_NEXT_REPLAY_INSPECTION_WORKER",
        "worker_type": "READONLY_REPLAY_INSPECTION_SUMMARY",
        "description": "Summarize replay references without mutation.",
    },
    "validation_summary": {
        "worker_id": "ACLI_NEXT_VALIDATION_SUMMARY_WORKER",
        "worker_type": "READONLY_VALIDATION_SUMMARY",
        "description": "Summarize validation evidence already present in replay.",
    },
    "canonical_mapping_lookup": {
        "worker_id": "ACLI_NEXT_CANONICAL_MAPPING_LOOKUP_WORKER",
        "worker_type": "READONLY_CANONICAL_MAPPING_LOOKUP",
        "description": "Summarize canonical mapping evidence already present in replay.",
    },
}


def lookup_readonly_worker_capability(capability_id: str) -> dict[str, str]:
    """Return a read-only Worker capability description from canonical lookup evidence."""

    capability = SUPPORTED_READONLY_CAPABILITIES.get(capability_id)
    if capability is None:
        raise FailClosedRuntimeError(
            f"Platform Core read-only Worker failed closed: unsupported capability {capability_id}"
        )
    return deepcopy(capability)
