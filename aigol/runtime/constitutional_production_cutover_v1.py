"""Atomic Constitutional production cutover and certification for B10.

The release record activates the already-certified G69-15 through G69-18
owner chain.  It creates no workflow, semantic capability, owner, route, or
execution authority.  CLIA remains transport-only and has only the existing
Canonical Human Entry as its runtime successor.
"""

from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Mapping

from aigol.runtime.constitutional_full_branch_replay_cro_coverage_v1 import (
    FULL_BRANCH_REPLAY_AND_CRO_COVERAGE_ESTABLISHED,
    observe_constitutional_full_branch_coverage_for_cro_v1,
    read_constitutional_full_branch_replay_correlation_v1,
    validate_constitutional_full_branch_cro_observation_v1,
    validate_constitutional_full_branch_replay_correlation_v1,
)
from aigol.runtime.constitutional_g64_completion_branch_composition_v1 import (
    COMPLETION_BRANCH_ESTABLISHED,
    compose_constitutional_g64_completion_branch_v1,
)
from aigol.runtime.constitutional_natural_conversation_branch_composition_v1 import (
    NATURAL_CONVERSATION_COMMITTED,
    compose_constitutional_natural_conversation_branch_v1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CONSTITUTIONAL_PRODUCTION_CUTOVER_CERTIFICATION_V1 = (
    "G69_19_CONSTITUTIONAL_PRODUCTION_CUTOVER_CERTIFICATION_V1"
)
CONSTITUTIONAL_PRODUCTION_CUTOVER_STATE_V1 = (
    "G69_19_CONSTITUTIONAL_PRODUCTION_CUTOVER_STATE_V1"
)
CONSTITUTIONAL_PRODUCTION_CUTOVER_ESTABLISHED = (
    "CONSTITUTIONAL_PRODUCTION_CUTOVER_ESTABLISHED"
)
CONSTITUTIONAL_PRODUCTION_CUTOVER_ROLLED_BACK = (
    "CONSTITUTIONAL_PRODUCTION_CUTOVER_ROLLED_BACK"
)

CLIA_PRODUCTION_HIC_FAMILY = "CLIA_PRODUCTION_HIC_FAMILY"
LEGACY_AICLI_HIC_FAMILY = "LEGACY_AICLI_HIC_FAMILY"
CANONICAL = "CANONICAL"
DEPRECATED = "DEPRECATED"
COMPATIBILITY = "COMPATIBILITY"
HISTORICAL = "HISTORICAL"
DEVELOPMENT = "DEVELOPMENT"
INTERNAL = "INTERNAL"
PASSIVE_OBSERVATION = "PASSIVE_OBSERVATION"

_CERTIFICATION_FIELDS = {
    "certification_version",
    "certification_identity",
    "certification_status",
    "release_decision_identity",
    "hic_certification_reference",
    "consumer_audit_reference",
    "rollback_proof_reference",
    "fail_closed_proof_reference",
    "full_branch_replay_reference",
    "full_branch_correlation",
    "full_branch_cro_observation",
    "surface_dispositions",
    "canonical_hic_family",
    "canonical_entry_identity",
    "canonical_production_caller",
    "che_definition_count",
    "production_hic_family_count",
    "production_owner_chain_count",
    "production_path_count",
    "parallel_production_path_count",
    "hic_responsibility",
    "hic_semantic_capability",
    "exact_human_act_transport_certified",
    "continuation_and_delivery_resolution_certified",
    "natural_conversation_branch_certified",
    "g64_completion_branch_certified",
    "full_replay_and_cro_coverage_certified",
    "consumer_closure_certified",
    "rollback_certified",
    "fail_closed_cutover_certified",
    "compatibility_forwarding_created",
    "new_constitutional_capability_created",
    "activated_at",
}
_STATE_FIELDS = {
    "state_version",
    "state_status",
    "certification",
    "canonical_hic_family",
    "surface_dispositions",
    "rollback_decision_identity",
    "state_hash",
}


def _fail(message: str) -> None:
    raise FailClosedRuntimeError(message)


def _text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        _fail(f"production cutover {field_name} is absent or malformed")
    return value


def _surfaces(*, rolled_back: bool = False) -> list[dict[str, Any]]:
    active = [
        ("clia", "CLIA", DEVELOPMENT, CANONICAL, CLIA_PRODUCTION_HIC_FAMILY),
        ("aicli-default", "./aicli", CANONICAL, DEPRECATED, LEGACY_AICLI_HIC_FAMILY),
        ("aicli-submit", "./aicli submit", CANONICAL, DEPRECATED, LEGACY_AICLI_HIC_FAMILY),
        ("aigol-next-default", "aigol next", CANONICAL, DEPRECATED, LEGACY_AICLI_HIC_FAMILY),
        ("aicli-conversation-v2", "aicli conversation-v2", COMPATIBILITY, COMPATIBILITY, None),
        ("aicli-execute", "aicli execute", COMPATIBILITY, COMPATIBILITY, None),
        ("aigol-next-session", "aigol next session", DEVELOPMENT, DEPRECATED, None),
        ("aigol-next-interactive", "aigol next interactive", DEVELOPMENT, DEPRECATED, None),
        ("acli-next-conversational", "acli_next_conversational", DEVELOPMENT, DEPRECATED, None),
        ("historical-aigol", "historical aigol modes", HISTORICAL, HISTORICAL, None),
        ("internal-cli", "internal inspection CLI", INTERNAL, INTERNAL, None),
        ("cro-cli", "CRO CLI", PASSIVE_OBSERVATION, PASSIVE_OBSERVATION, None),
    ]
    if rolled_back:
        active = [
            (
                identity,
                launcher,
                before,
                (
                    DEVELOPMENT
                    if identity == "clia"
                    else CANONICAL
                    if identity in {
                        "aicli-default",
                        "aicli-submit",
                        "aigol-next-default",
                    }
                    else after
                ),
                family,
            )
            for identity, launcher, before, after, family in active
        ]
    return [
        {
            "surface_identity": identity,
            "launcher_identity": launcher,
            "pre_cutover_status": before,
            "current_status": after,
            "hic_family": family,
            "forwarding_alias": False,
            "removed": False,
        }
        for identity, launcher, before, after, family in active
    ]


def _validate_surface_dispositions(value: Any, *, rolled_back: bool = False) -> list[dict[str, Any]]:
    expected = _surfaces(rolled_back=rolled_back)
    if value != expected:
        _fail("production cutover surface disposition is invalid")
    canonical_families = {
        item["hic_family"]
        for item in expected
        if item["current_status"] == CANONICAL
    }
    if canonical_families != {
        LEGACY_AICLI_HIC_FAMILY if rolled_back else CLIA_PRODUCTION_HIC_FAMILY
    }:
        _fail("production cutover creates a parallel canonical HIC family")
    return deepcopy(expected)


def _certification_identity(value: Mapping[str, Any]) -> str:
    body = deepcopy(dict(value))
    body.pop("certification_identity", None)
    return "production-cutover-sha256:" + replay_hash(body).split(":", 1)[1]


def create_constitutional_production_cutover_certification_v1(
    *,
    full_branch_correlation: Mapping[str, Any],
    full_branch_cro_observation: Mapping[str, Any],
    release_decision_identity: str,
    hic_certification_reference: str,
    consumer_audit_reference: str,
    rollback_proof_reference: str,
    fail_closed_proof_reference: str,
    full_branch_replay_reference: str,
    activated_at: str,
) -> dict[str, Any]:
    """Create terminal B10 certification from the complete certified lineage."""

    correlation = validate_constitutional_full_branch_replay_correlation_v1(
        full_branch_correlation
    )
    observation = validate_constitutional_full_branch_cro_observation_v1(
        full_branch_cro_observation
    )
    model = correlation["workflow_model"]
    value = {
        "certification_version": CONSTITUTIONAL_PRODUCTION_CUTOVER_CERTIFICATION_V1,
        "certification_identity": "",
        "certification_status": CONSTITUTIONAL_PRODUCTION_CUTOVER_ESTABLISHED,
        "release_decision_identity": _text(release_decision_identity, "release decision identity"),
        "hic_certification_reference": _text(hic_certification_reference, "HIC certification reference"),
        "consumer_audit_reference": _text(consumer_audit_reference, "consumer audit reference"),
        "rollback_proof_reference": _text(rollback_proof_reference, "rollback proof reference"),
        "fail_closed_proof_reference": _text(fail_closed_proof_reference, "fail-closed proof reference"),
        "full_branch_replay_reference": _text(full_branch_replay_reference, "full branch Replay reference"),
        "full_branch_correlation": correlation,
        "full_branch_cro_observation": observation,
        "surface_dispositions": _surfaces(),
        "canonical_hic_family": CLIA_PRODUCTION_HIC_FAMILY,
        "canonical_entry_identity": model["canonical_entry_identity"],
        "canonical_production_caller": "CLIA_SUBMIT_TO_SOLE_CANONICAL_HUMAN_ENTRY",
        "che_definition_count": model["che_definition_count"],
        "production_hic_family_count": model["production_hic_family_count"],
        "production_owner_chain_count": model["production_owner_chain_count"],
        "production_path_count": model["production_path_count"],
        "parallel_production_path_count": model["parallel_production_path_count"],
        "hic_responsibility": model["hic_responsibility"],
        "hic_semantic_capability": model["hic_semantic_capability"],
        "exact_human_act_transport_certified": True,
        "continuation_and_delivery_resolution_certified": True,
        "natural_conversation_branch_certified": correlation["natural_conversation_result"]["composition_status"] == NATURAL_CONVERSATION_COMMITTED,
        "g64_completion_branch_certified": correlation["g64_completion_result"]["composition_status"] == COMPLETION_BRANCH_ESTABLISHED,
        "full_replay_and_cro_coverage_certified": correlation["coverage_status"] == FULL_BRANCH_REPLAY_AND_CRO_COVERAGE_ESTABLISHED,
        "consumer_closure_certified": True,
        "rollback_certified": True,
        "fail_closed_cutover_certified": True,
        "compatibility_forwarding_created": False,
        "new_constitutional_capability_created": False,
        "activated_at": _text(activated_at, "activation time"),
    }
    value["certification_identity"] = _certification_identity(value)
    return validate_constitutional_production_cutover_certification_v1(value)


def validate_constitutional_production_cutover_certification_v1(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != _CERTIFICATION_FIELDS:
        _fail("production cutover certification is malformed")
    candidate = deepcopy(dict(value))
    if candidate["certification_version"] != CONSTITUTIONAL_PRODUCTION_CUTOVER_CERTIFICATION_V1:
        _fail("production cutover certification version is invalid")
    correlation = validate_constitutional_full_branch_replay_correlation_v1(
        candidate["full_branch_correlation"]
    )
    observation = validate_constitutional_full_branch_cro_observation_v1(
        candidate["full_branch_cro_observation"]
    )
    model = correlation["workflow_model"]
    if observation["correlation_identity"] != correlation["correlation_identity"]:
        _fail("production cutover Replay/CRO binding is invalid")
    _validate_surface_dispositions(candidate["surface_dispositions"])
    expected = (
        candidate["certification_status"],
        candidate["canonical_hic_family"],
        candidate["canonical_entry_identity"],
        candidate["canonical_production_caller"],
        candidate["che_definition_count"],
        candidate["production_hic_family_count"],
        candidate["production_owner_chain_count"],
        candidate["production_path_count"],
        candidate["parallel_production_path_count"],
        candidate["hic_responsibility"],
        candidate["hic_semantic_capability"],
    )
    canonical = (
        CONSTITUTIONAL_PRODUCTION_CUTOVER_ESTABLISHED,
        CLIA_PRODUCTION_HIC_FAMILY,
        model["canonical_entry_identity"],
        "CLIA_SUBMIT_TO_SOLE_CANONICAL_HUMAN_ENTRY",
        1, 1, 1, 1, 0, "TRANSPORT_ONLY", "NO_SEMANTIC_CAPABILITY",
    )
    if expected != canonical:
        _fail("production cutover one-lineage invariant is invalid")
    if any(
        candidate[field] is not True
        for field in (
            "exact_human_act_transport_certified",
            "continuation_and_delivery_resolution_certified",
            "natural_conversation_branch_certified",
            "g64_completion_branch_certified",
            "full_replay_and_cro_coverage_certified",
            "consumer_closure_certified",
            "rollback_certified",
            "fail_closed_cutover_certified",
        )
    ) or candidate["compatibility_forwarding_created"] is not False or candidate["new_constitutional_capability_created"] is not False:
        _fail("production cutover readiness evidence is incomplete")
    if correlation["natural_conversation_result"]["composition_status"] != NATURAL_CONVERSATION_COMMITTED or correlation["g64_completion_result"]["composition_status"] != COMPLETION_BRANCH_ESTABLISHED:
        _fail("production cutover owner composition evidence is incomplete")
    for field in (
        "release_decision_identity", "hic_certification_reference",
        "consumer_audit_reference", "rollback_proof_reference",
        "fail_closed_proof_reference", "full_branch_replay_reference", "activated_at",
    ):
        _text(candidate[field], field)
    replay_path = Path(candidate["full_branch_replay_reference"])
    if (
        read_constitutional_full_branch_replay_correlation_v1(replay_path)
        != correlation
        or observe_constitutional_full_branch_coverage_for_cro_v1(replay_path)
        != observation
    ):
        _fail("production cutover persisted Replay/CRO evidence is invalid")
    if candidate["certification_identity"] != _certification_identity(candidate):
        _fail("production cutover certification integrity is invalid")
    canonical_serialize(candidate)
    return candidate


def constitutional_production_cutover_state_path_v1(runtime_root: str | Path) -> Path:
    return Path(runtime_root) / "constitutional_production_cutover_v1" / "active-cutover.json"


def _atomic_write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = canonical_serialize(value) + "\n"
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, prefix=".cutover-", delete=False
        ) as handle:
            temporary_name = handle.name
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    finally:
        if temporary_name is not None and os.path.exists(temporary_name):
            os.unlink(temporary_name)


def _acquire_cutover_lock(path: Path) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        return os.open(path.parent / ".cutover.lock", os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise FailClosedRuntimeError("production cutover transition is already active") from exc


def _release_cutover_lock(path: Path, descriptor: int) -> None:
    os.close(descriptor)
    try:
        (path.parent / ".cutover.lock").unlink()
    except FileNotFoundError:
        pass


def activate_constitutional_production_cutover_v1(*, runtime_root: str | Path, certification: Mapping[str, Any]) -> Path:
    validated = validate_constitutional_production_cutover_certification_v1(certification)
    state = {
        "state_version": CONSTITUTIONAL_PRODUCTION_CUTOVER_STATE_V1,
        "state_status": CONSTITUTIONAL_PRODUCTION_CUTOVER_ESTABLISHED,
        "certification": validated,
        "canonical_hic_family": CLIA_PRODUCTION_HIC_FAMILY,
        "surface_dispositions": _surfaces(),
        "rollback_decision_identity": None,
        "state_hash": "",
    }
    state["state_hash"] = replay_hash({key: item for key, item in state.items() if key != "state_hash"})
    path = constitutional_production_cutover_state_path_v1(runtime_root)
    lock = _acquire_cutover_lock(path)
    try:
        if path.exists():
            current = read_constitutional_production_cutover_state_v1(path)
            if current != state:
                _fail("production cutover state already exists with different content")
            return path
        _atomic_write(path, state)
        read_constitutional_production_cutover_state_v1(path)
    finally:
        _release_cutover_lock(path, lock)
    return path


def read_constitutional_production_cutover_state_v1(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FailClosedRuntimeError("production cutover state is unreadable") from exc
    if not isinstance(value, Mapping) or set(value) != _STATE_FIELDS:
        _fail("production cutover state is malformed")
    candidate = deepcopy(dict(value))
    body = {key: item for key, item in candidate.items() if key != "state_hash"}
    if candidate["state_version"] != CONSTITUTIONAL_PRODUCTION_CUTOVER_STATE_V1 or candidate["state_hash"] != replay_hash(body):
        _fail("production cutover state integrity is invalid")
    certification = validate_constitutional_production_cutover_certification_v1(candidate["certification"])
    rolled_back = candidate["state_status"] == CONSTITUTIONAL_PRODUCTION_CUTOVER_ROLLED_BACK
    if candidate["state_status"] not in {CONSTITUTIONAL_PRODUCTION_CUTOVER_ESTABLISHED, CONSTITUTIONAL_PRODUCTION_CUTOVER_ROLLED_BACK}:
        _fail("production cutover state status is invalid")
    _validate_surface_dispositions(candidate["surface_dispositions"], rolled_back=rolled_back)
    expected_family = LEGACY_AICLI_HIC_FAMILY if rolled_back else CLIA_PRODUCTION_HIC_FAMILY
    if rolled_back:
        _text(candidate["rollback_decision_identity"], "rollback decision identity")
    elif candidate["rollback_decision_identity"] is not None:
        _fail("active production cutover carries rollback provenance")
    if candidate["canonical_hic_family"] != expected_family or candidate["certification"] != certification:
        _fail("production cutover state binding is invalid")
    return candidate


def validate_active_constitutional_production_cutover_v1(runtime_root: str | Path) -> dict[str, Any]:
    path = constitutional_production_cutover_state_path_v1(runtime_root)
    if not path.is_file():
        _fail("constitutional production cutover is not active")
    state = read_constitutional_production_cutover_state_v1(path)
    if state["state_status"] != CONSTITUTIONAL_PRODUCTION_CUTOVER_ESTABLISHED:
        _fail("constitutional production cutover is not active")
    return state


def rollback_constitutional_production_cutover_v1(*, runtime_root: str | Path, rollback_decision_identity: str) -> Path:
    path = constitutional_production_cutover_state_path_v1(runtime_root)
    state = validate_active_constitutional_production_cutover_v1(runtime_root)
    _text(rollback_decision_identity, "rollback decision identity")
    if not state["certification"]["rollback_certified"]:
        _fail("production cutover rollback is not certified")
    replacement = {
        **state,
        "state_status": CONSTITUTIONAL_PRODUCTION_CUTOVER_ROLLED_BACK,
        "canonical_hic_family": LEGACY_AICLI_HIC_FAMILY,
        "surface_dispositions": _surfaces(rolled_back=True),
        "rollback_decision_identity": rollback_decision_identity,
        "state_hash": "",
    }
    replacement["state_hash"] = replay_hash({key: item for key, item in replacement.items() if key != "state_hash"})
    lock = _acquire_cutover_lock(path)
    try:
        # Re-read under the exclusive transition lock so rollback cannot race
        # a competing activation or rollback decision.
        validate_active_constitutional_production_cutover_v1(runtime_root)
        _atomic_write(path, replacement)
        read_constitutional_production_cutover_state_v1(path)
    finally:
        _release_cutover_lock(path, lock)
    return path


def run_production_natural_conversation_branch_v1(*, cutover_runtime_root: str | Path, **owner_inputs: Any) -> dict[str, Any]:
    """Gated non-HIC production caller for the certified B7 owner branch."""

    validate_active_constitutional_production_cutover_v1(cutover_runtime_root)
    return compose_constitutional_natural_conversation_branch_v1(**owner_inputs)


def run_production_g64_completion_branch_v1(*, cutover_runtime_root: str | Path, **owner_inputs: Any) -> dict[str, Any]:
    """Gated non-HIC production caller for the certified B8 owner branch."""

    validate_active_constitutional_production_cutover_v1(cutover_runtime_root)
    return compose_constitutional_g64_completion_branch_v1(**owner_inputs)


__all__ = [
    "CANONICAL",
    "CLIA_PRODUCTION_HIC_FAMILY",
    "COMPATIBILITY",
    "CONSTITUTIONAL_PRODUCTION_CUTOVER_CERTIFICATION_V1",
    "CONSTITUTIONAL_PRODUCTION_CUTOVER_ESTABLISHED",
    "CONSTITUTIONAL_PRODUCTION_CUTOVER_ROLLED_BACK",
    "CONSTITUTIONAL_PRODUCTION_CUTOVER_STATE_V1",
    "DEPRECATED",
    "activate_constitutional_production_cutover_v1",
    "constitutional_production_cutover_state_path_v1",
    "create_constitutional_production_cutover_certification_v1",
    "read_constitutional_production_cutover_state_v1",
    "rollback_constitutional_production_cutover_v1",
    "run_production_g64_completion_branch_v1",
    "run_production_natural_conversation_branch_v1",
    "validate_active_constitutional_production_cutover_v1",
    "validate_constitutional_production_cutover_certification_v1",
]
