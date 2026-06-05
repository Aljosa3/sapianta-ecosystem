"""Replay-visible governed domain lifecycle runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_DOMAIN_RUNTIME_VERSION = "AIGOL_DOMAIN_RUNTIME_V1"

DOMAIN_IDENTITY_ARTIFACT_V1 = "DOMAIN_IDENTITY_ARTIFACT_V1"
DOMAIN_MANIFEST_ARTIFACT_V1 = "DOMAIN_MANIFEST_ARTIFACT_V1"
DOMAIN_CAPABILITY_DECLARATION_ARTIFACT_V1 = "DOMAIN_CAPABILITY_DECLARATION_ARTIFACT_V1"
DOMAIN_GOVERNANCE_BINDING_ARTIFACT_V1 = "DOMAIN_GOVERNANCE_BINDING_ARTIFACT_V1"
DOMAIN_LIFECYCLE_ARTIFACT_V1 = "DOMAIN_LIFECYCLE_ARTIFACT_V1"

CREATED = "CREATED"
VALIDATED = "VALIDATED"
ACTIVE = "ACTIVE"
SUSPENDED = "SUSPENDED"
RETIRED = "RETIRED"

DOMAIN_CREATED = "DOMAIN_CREATED"
DOMAIN_VALIDATED = "DOMAIN_VALIDATED"
DOMAIN_ACTIVATED = "DOMAIN_ACTIVATED"
DOMAIN_SUSPENDED = "DOMAIN_SUSPENDED"
DOMAIN_RETIRED = "DOMAIN_RETIRED"

REPLAY_STEPS = (
    "domain_created",
    "domain_validated",
    "domain_activated",
    "domain_suspended",
    "domain_retired",
)

EVENTS_BY_STATE = {
    CREATED: DOMAIN_CREATED,
    VALIDATED: DOMAIN_VALIDATED,
    ACTIVE: DOMAIN_ACTIVATED,
    SUSPENDED: DOMAIN_SUSPENDED,
    RETIRED: DOMAIN_RETIRED,
}

STATE_TRANSITIONS = {
    CREATED: {VALIDATED},
    VALIDATED: {ACTIVE},
    ACTIVE: {SUSPENDED, RETIRED},
    SUSPENDED: {ACTIVE, RETIRED},
    RETIRED: set(),
}

_TOKEN_RE = re.compile(r"^[A-Z0-9][A-Z0-9_-]*$")


def create_domain(
    *,
    domain_id: str,
    display_name: str,
    domain_version: str,
    capabilities: list[str],
    governance_scope: str,
    governance_policy_refs: list[str],
    actor_id: str,
    timestamp: str,
    replay_reference: str,
    replay_dir: str | Path,
    known_gaps: list[str] | None = None,
) -> dict[str, Any]:
    """Create a governed domain identity and record DOMAIN_CREATED replay."""

    replay_path = Path(replay_dir)
    _ensure_replay_available(replay_path)
    identity = _identity_artifact(domain_id, display_name, domain_version)
    manifest = _manifest_artifact(identity, known_gaps or [])
    capability_declaration = _capability_declaration_artifact(identity, capabilities)
    governance_binding = _governance_binding_artifact(identity, governance_scope, governance_policy_refs)
    artifact = _lifecycle_artifact(
        identity=identity,
        manifest=manifest,
        capability_declaration=capability_declaration,
        governance_binding=governance_binding,
        lifecycle_state=CREATED,
        previous_artifact=None,
        actor_id=actor_id,
        timestamp=timestamp,
        replay_reference=replay_reference,
        transition_reason="domain registration created",
    )
    _persist_step(replay_path, 0, DOMAIN_CREATED, artifact)
    return _capture(artifact)


def validate_domain(
    *,
    domain_artifact: dict[str, Any],
    actor_id: str,
    timestamp: str,
    replay_reference: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Validate a CREATED domain under its governance binding."""

    previous = _validate_domain_artifact(domain_artifact)
    artifact = _transition_artifact(
        previous_artifact=previous,
        lifecycle_state=VALIDATED,
        actor_id=actor_id,
        timestamp=timestamp,
        replay_reference=replay_reference,
        transition_reason="domain manifest and governance binding validated",
    )
    _persist_step(Path(replay_dir), 1, DOMAIN_VALIDATED, artifact)
    return _capture(artifact)


def activate_domain(
    *,
    domain_artifact: dict[str, Any],
    actor_id: str,
    timestamp: str,
    replay_reference: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Activate a VALIDATED governed domain."""

    previous = _validate_domain_artifact(domain_artifact)
    artifact = _transition_artifact(
        previous_artifact=previous,
        lifecycle_state=ACTIVE,
        actor_id=actor_id,
        timestamp=timestamp,
        replay_reference=replay_reference,
        transition_reason="domain activated for governed runtime availability",
    )
    _persist_step(Path(replay_dir), 2, DOMAIN_ACTIVATED, artifact)
    return _capture(artifact)


def suspend_domain(
    *,
    domain_artifact: dict[str, Any],
    actor_id: str,
    timestamp: str,
    replay_reference: str,
    replay_dir: str | Path,
    reason: str,
) -> dict[str, Any]:
    """Suspend an ACTIVE governed domain without deleting lineage."""

    previous = _validate_domain_artifact(domain_artifact)
    artifact = _transition_artifact(
        previous_artifact=previous,
        lifecycle_state=SUSPENDED,
        actor_id=actor_id,
        timestamp=timestamp,
        replay_reference=replay_reference,
        transition_reason=reason,
    )
    _persist_step(Path(replay_dir), 3, DOMAIN_SUSPENDED, artifact)
    return _capture(artifact)


def retire_domain(
    *,
    domain_artifact: dict[str, Any],
    actor_id: str,
    timestamp: str,
    replay_reference: str,
    replay_dir: str | Path,
    reason: str,
) -> dict[str, Any]:
    """Retire an ACTIVE or SUSPENDED governed domain."""

    previous = _validate_domain_artifact(domain_artifact)
    artifact = _transition_artifact(
        previous_artifact=previous,
        lifecycle_state=RETIRED,
        actor_id=actor_id,
        timestamp=timestamp,
        replay_reference=replay_reference,
        transition_reason=reason,
    )
    _persist_step(Path(replay_dir), 4, DOMAIN_RETIRED, artifact)
    return _capture(artifact)


def reconstruct_domain_lifecycle_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate a complete domain lifecycle replay chain."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    previous: dict[str, Any] | None = None
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("domain runtime replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("domain runtime replay artifact must be a JSON object")
        artifact = _validate_domain_artifact(artifact)
        expected_event = EVENTS_BY_STATE[artifact["lifecycle_state"]]
        if wrapper.get("event_type") != expected_event or artifact.get("lifecycle_event") != expected_event:
            raise FailClosedRuntimeError("domain runtime replay event mismatch")
        _validate_replay_continuity(previous, artifact)
        wrappers.append(wrapper)
        previous = artifact
    final_artifact = wrappers[-1]["artifact"]
    return {
        "domain_id": final_artifact["domain_id"],
        "domain_replay_id": final_artifact["domain_replay_id"],
        "lifecycle_state": final_artifact["lifecycle_state"],
        "lifecycle_events": [wrapper["event_type"] for wrapper in wrappers],
        "capabilities": tuple(final_artifact["domain_capability_declaration"]["capabilities"]),
        "governance_scope": final_artifact["domain_governance_binding"]["governance_scope"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        "certification_ready": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "dispatch_requested": False,
        "execution_performed": False,
        "governance_mutated": False,
    }


def _identity_artifact(domain_id: str, display_name: str, domain_version: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": DOMAIN_IDENTITY_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_RUNTIME_VERSION,
        "domain_id": _normalize_token(domain_id, "domain_id"),
        "display_name": _require_string(display_name, "display_name"),
        "domain_version": _require_string(domain_version, "domain_version"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _manifest_artifact(identity: dict[str, Any], known_gaps: list[str]) -> dict[str, Any]:
    _verify_artifact_hash(identity, "domain identity")
    artifact = {
        "artifact_type": DOMAIN_MANIFEST_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_RUNTIME_VERSION,
        "domain_id": identity["domain_id"],
        "domain_identity_hash": identity["artifact_hash"],
        "lifecycle_states": [CREATED, VALIDATED, ACTIVE, SUSPENDED, RETIRED],
        "replay_events": [DOMAIN_CREATED, DOMAIN_VALIDATED, DOMAIN_ACTIVATED, DOMAIN_SUSPENDED, DOMAIN_RETIRED],
        "known_gaps": _normalize_string_list(known_gaps, "known_gaps", allow_empty=True),
        "replay_visible": True,
        "execution_authority": False,
        "governance_mutation_authority": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capability_declaration_artifact(identity: dict[str, Any], capabilities: list[str]) -> dict[str, Any]:
    normalized = _normalize_string_list(capabilities, "capabilities")
    if len(normalized) != len(set(normalized)):
        raise FailClosedRuntimeError("domain runtime failed closed: duplicate capability declaration")
    artifact = {
        "artifact_type": DOMAIN_CAPABILITY_DECLARATION_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_RUNTIME_VERSION,
        "domain_id": identity["domain_id"],
        "domain_identity_hash": identity["artifact_hash"],
        "capabilities": normalized,
        "declaration_status": "DECLARED",
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _governance_binding_artifact(
    identity: dict[str, Any],
    governance_scope: str,
    governance_policy_refs: list[str],
) -> dict[str, Any]:
    artifact = {
        "artifact_type": DOMAIN_GOVERNANCE_BINDING_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_RUNTIME_VERSION,
        "domain_id": identity["domain_id"],
        "domain_identity_hash": identity["artifact_hash"],
        "governance_scope": _require_string(governance_scope, "governance_scope"),
        "governance_policy_refs": _normalize_string_list(governance_policy_refs, "governance_policy_refs"),
        "binding_status": "BOUND",
        "human_authority_required": True,
        "replay_visible": True,
        "provider_authority": False,
        "worker_authority": False,
        "self_authorization": False,
        "execution_authority": False,
        "governance_mutation_authority": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _transition_artifact(
    *,
    previous_artifact: dict[str, Any],
    lifecycle_state: str,
    actor_id: str,
    timestamp: str,
    replay_reference: str,
    transition_reason: str,
) -> dict[str, Any]:
    if lifecycle_state not in STATE_TRANSITIONS.get(previous_artifact["lifecycle_state"], set()):
        raise FailClosedRuntimeError("domain runtime failed closed: unauthorized lifecycle transition")
    return _lifecycle_artifact(
        identity=previous_artifact["domain_identity"],
        manifest=previous_artifact["domain_manifest"],
        capability_declaration=previous_artifact["domain_capability_declaration"],
        governance_binding=previous_artifact["domain_governance_binding"],
        lifecycle_state=lifecycle_state,
        previous_artifact=previous_artifact,
        actor_id=actor_id,
        timestamp=timestamp,
        replay_reference=replay_reference,
        transition_reason=transition_reason,
    )


def _lifecycle_artifact(
    *,
    identity: dict[str, Any],
    manifest: dict[str, Any],
    capability_declaration: dict[str, Any],
    governance_binding: dict[str, Any],
    lifecycle_state: str,
    previous_artifact: dict[str, Any] | None,
    actor_id: str,
    timestamp: str,
    replay_reference: str,
    transition_reason: str,
) -> dict[str, Any]:
    _verify_domain_components(identity, manifest, capability_declaration, governance_binding)
    previous_state = previous_artifact["lifecycle_state"] if previous_artifact is not None else None
    previous_hash = previous_artifact["artifact_hash"] if previous_artifact is not None else None
    chain_input = {
        "domain_id": identity["domain_id"],
        "domain_replay_id": _domain_replay_id(identity),
        "previous_artifact_hash": previous_hash,
        "lifecycle_state": lifecycle_state,
        "lifecycle_event": EVENTS_BY_STATE[lifecycle_state],
    }
    artifact = {
        "artifact_type": DOMAIN_LIFECYCLE_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_RUNTIME_VERSION,
        "domain_id": identity["domain_id"],
        "domain_replay_id": _domain_replay_id(identity),
        "domain_identity": deepcopy(identity),
        "domain_identity_hash": identity["artifact_hash"],
        "domain_manifest": deepcopy(manifest),
        "domain_manifest_hash": manifest["artifact_hash"],
        "domain_capability_declaration": deepcopy(capability_declaration),
        "domain_capability_declaration_hash": capability_declaration["artifact_hash"],
        "domain_governance_binding": deepcopy(governance_binding),
        "domain_governance_binding_hash": governance_binding["artifact_hash"],
        "previous_lifecycle_state": previous_state,
        "lifecycle_state": lifecycle_state,
        "lifecycle_event": EVENTS_BY_STATE[lifecycle_state],
        "previous_artifact_hash": previous_hash,
        "chain_hash": replay_hash(chain_input),
        "actor_id": _normalize_token(actor_id, "actor_id"),
        "timestamp": _require_string(timestamp, "timestamp"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "transition_reason": _require_string(transition_reason, "transition_reason"),
        "replay_visible": True,
        "human_authority_required": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "dispatch_requested": False,
        "execution_performed": False,
        "self_authorization": False,
        "governance_mutated": False,
        "governance_mutation_authority": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_domain_artifact(artifact)
    return artifact


def _validate_domain_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("domain runtime failed closed: domain artifact is required")
    _verify_artifact_hash(artifact, "domain lifecycle artifact")
    if artifact.get("artifact_type") != DOMAIN_LIFECYCLE_ARTIFACT_V1:
        raise FailClosedRuntimeError("domain runtime failed closed: invalid domain lifecycle artifact")
    if artifact.get("runtime_version") != AIGOL_DOMAIN_RUNTIME_VERSION:
        raise FailClosedRuntimeError("domain runtime failed closed: invalid runtime version")
    state = artifact.get("lifecycle_state")
    if state not in EVENTS_BY_STATE:
        raise FailClosedRuntimeError("domain runtime failed closed: invalid lifecycle state")
    if artifact.get("lifecycle_event") != EVENTS_BY_STATE[state]:
        raise FailClosedRuntimeError("domain runtime failed closed: lifecycle event mismatch")
    if artifact.get("replay_visible") is not True:
        raise FailClosedRuntimeError("domain runtime failed closed: replay visibility missing")
    for flag in (
        "provider_invoked",
        "worker_invoked",
        "dispatch_requested",
        "execution_performed",
        "self_authorization",
        "governance_mutated",
        "governance_mutation_authority",
    ):
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"domain runtime failed closed: {flag} introduced")
    if artifact.get("human_authority_required") is not True:
        raise FailClosedRuntimeError("domain runtime failed closed: human authority boundary missing")
    identity = artifact.get("domain_identity")
    manifest = artifact.get("domain_manifest")
    capability_declaration = artifact.get("domain_capability_declaration")
    governance_binding = artifact.get("domain_governance_binding")
    _verify_domain_components(identity, manifest, capability_declaration, governance_binding)
    if artifact.get("domain_id") != identity["domain_id"]:
        raise FailClosedRuntimeError("domain runtime failed closed: domain identity mismatch")
    if artifact.get("domain_replay_id") != _domain_replay_id(identity):
        raise FailClosedRuntimeError("domain runtime failed closed: domain replay id mismatch")
    if artifact.get("domain_identity_hash") != identity["artifact_hash"]:
        raise FailClosedRuntimeError("domain runtime failed closed: domain identity hash mismatch")
    if artifact.get("domain_manifest_hash") != manifest["artifact_hash"]:
        raise FailClosedRuntimeError("domain runtime failed closed: domain manifest hash mismatch")
    if artifact.get("domain_capability_declaration_hash") != capability_declaration["artifact_hash"]:
        raise FailClosedRuntimeError("domain runtime failed closed: domain capability hash mismatch")
    if artifact.get("domain_governance_binding_hash") != governance_binding["artifact_hash"]:
        raise FailClosedRuntimeError("domain runtime failed closed: domain governance binding hash mismatch")
    expected_chain = replay_hash(
        {
            "domain_id": identity["domain_id"],
            "domain_replay_id": artifact["domain_replay_id"],
            "previous_artifact_hash": artifact.get("previous_artifact_hash"),
            "lifecycle_state": state,
            "lifecycle_event": artifact["lifecycle_event"],
        }
    )
    if artifact.get("chain_hash") != expected_chain:
        raise FailClosedRuntimeError("domain runtime failed closed: chain hash mismatch")
    _require_string(artifact.get("actor_id"), "actor_id")
    _require_string(artifact.get("timestamp"), "timestamp")
    _require_string(artifact.get("replay_reference"), "replay_reference")
    _require_string(artifact.get("transition_reason"), "transition_reason")
    return deepcopy(artifact)


def _verify_domain_components(
    identity: dict[str, Any],
    manifest: dict[str, Any],
    capability_declaration: dict[str, Any],
    governance_binding: dict[str, Any],
) -> None:
    for artifact, artifact_type, label in (
        (identity, DOMAIN_IDENTITY_ARTIFACT_V1, "domain identity"),
        (manifest, DOMAIN_MANIFEST_ARTIFACT_V1, "domain manifest"),
        (capability_declaration, DOMAIN_CAPABILITY_DECLARATION_ARTIFACT_V1, "domain capability declaration"),
        (governance_binding, DOMAIN_GOVERNANCE_BINDING_ARTIFACT_V1, "domain governance binding"),
    ):
        if not isinstance(artifact, dict) or artifact.get("artifact_type") != artifact_type:
            raise FailClosedRuntimeError(f"domain runtime failed closed: invalid {label}")
        _verify_artifact_hash(artifact, label)
    domain_id = identity["domain_id"]
    if manifest.get("domain_id") != domain_id:
        raise FailClosedRuntimeError("domain runtime failed closed: manifest domain mismatch")
    if capability_declaration.get("domain_id") != domain_id:
        raise FailClosedRuntimeError("domain runtime failed closed: capability domain mismatch")
    if governance_binding.get("domain_id") != domain_id:
        raise FailClosedRuntimeError("domain runtime failed closed: governance binding domain mismatch")
    for artifact, label in (
        (manifest, "manifest"),
        (capability_declaration, "capability declaration"),
        (governance_binding, "governance binding"),
    ):
        if artifact.get("domain_identity_hash") != identity["artifact_hash"]:
            raise FailClosedRuntimeError(f"domain runtime failed closed: {label} identity hash mismatch")
    capabilities = capability_declaration.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities:
        raise FailClosedRuntimeError("domain runtime failed closed: capabilities are required")
    if len(capabilities) != len(set(capabilities)):
        raise FailClosedRuntimeError("domain runtime failed closed: duplicate capability declaration")
    if not isinstance(governance_binding.get("governance_policy_refs"), list) or not governance_binding[
        "governance_policy_refs"
    ]:
        raise FailClosedRuntimeError("domain runtime failed closed: governance policy refs are required")
    if governance_binding.get("binding_status") != "BOUND":
        raise FailClosedRuntimeError("domain runtime failed closed: governance binding is not bound")
    for flag in (
        "provider_authority",
        "worker_authority",
        "self_authorization",
        "execution_authority",
        "governance_mutation_authority",
    ):
        if governance_binding.get(flag) is not False:
            raise FailClosedRuntimeError(f"domain runtime failed closed: governance binding {flag} introduced")


def _validate_replay_continuity(previous: dict[str, Any] | None, artifact: dict[str, Any]) -> None:
    if previous is None:
        if artifact["lifecycle_state"] != CREATED:
            raise FailClosedRuntimeError("domain runtime replay continuity mismatch")
        if artifact.get("previous_artifact_hash") is not None or artifact.get("previous_lifecycle_state") is not None:
            raise FailClosedRuntimeError("domain runtime replay parent mismatch")
        return
    if artifact["domain_replay_id"] != previous["domain_replay_id"]:
        raise FailClosedRuntimeError("domain runtime replay id continuity mismatch")
    if artifact.get("previous_artifact_hash") != previous["artifact_hash"]:
        raise FailClosedRuntimeError("domain runtime replay hash continuity mismatch")
    if artifact.get("previous_lifecycle_state") != previous["lifecycle_state"]:
        raise FailClosedRuntimeError("domain runtime replay lineage continuity mismatch")
    if artifact["lifecycle_state"] not in STATE_TRANSITIONS[previous["lifecycle_state"]]:
        raise FailClosedRuntimeError("domain runtime replay unauthorized transition")


def _persist_step(replay_dir: Path, index: int, event_type: str, artifact: dict[str, Any]) -> None:
    if index < 0 or index >= len(REPLAY_STEPS):
        raise FailClosedRuntimeError("domain runtime replay step ordering mismatch")
    _verify_artifact_hash(artifact, "domain lifecycle artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": REPLAY_STEPS[index],
        "artifact": deepcopy(artifact),
        "event_type": event_type,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{REPLAY_STEPS[index]}.json", wrapper)


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _capture(artifact: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "domain_artifact": deepcopy(artifact),
        "domain_lifecycle_state": artifact["lifecycle_state"],
        "domain_lifecycle_event": artifact["lifecycle_event"],
        "domain_replay_id": artifact["domain_replay_id"],
        "domain_artifact_hash": artifact["artifact_hash"],
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "dispatch_requested": False,
        "execution_performed": False,
        "governance_mutated": False,
    }
    capture["domain_capture_hash"] = replay_hash(capture)
    return capture


def _domain_replay_id(identity: dict[str, Any]) -> str:
    _verify_artifact_hash(identity, "domain identity")
    return "DOMAIN-REPLAY-" + identity["artifact_hash"].removeprefix("sha256:")[:16].upper()


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("domain runtime replay hash missing")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    expected = replay_hash(expected_input)
    if actual != expected:
        raise FailClosedRuntimeError("domain runtime replay hash mismatch")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict) or "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash missing")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    expected = replay_hash(expected_input)
    if actual != expected:
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _normalize_token(value: Any, field_name: str) -> str:
    normalized = _require_string(value, field_name).strip().upper().replace(" ", "_")
    if not _TOKEN_RE.fullmatch(normalized):
        raise FailClosedRuntimeError(f"{field_name} must be an uppercase governance token")
    return normalized


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _normalize_string_list(values: list[str], field_name: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(values, list):
        raise FailClosedRuntimeError(f"{field_name} must be a list")
    normalized: list[str] = []
    for value in values:
        normalized.append(_require_string(value, field_name))
    if not allow_empty and not normalized:
        raise FailClosedRuntimeError(f"{field_name} are required")
    return normalized
