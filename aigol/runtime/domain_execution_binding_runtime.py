"""Governed domain execution binding through existing provider and worker runtimes."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.authorization.authorization_runtime import authorize_worker_request, reconstruct_authorization_replay
from aigol.provider.provider_adapter import ProviderAdapter
from aigol.provider.provider_proposal_envelope import ProviderProposalEnvelope, create_provider_proposal_envelope
from aigol.provider.provider_registry import AVAILABLE, ProviderMetadata, ProviderRegistry
from aigol.provider.provider_runtime import run_provider_attachment, reconstruct_provider_attachment_replay
from aigol.runtime.domain_runtime import ACTIVE, DOMAIN_LIFECYCLE_ARTIFACT_V1
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.workers.filesystem_worker import (
    AUTHORIZED_SCOPE,
    FILESYSTEM_WORKER_EXECUTED,
    FILESYSTEM_WORKER_ID,
    create_authorized_worker_request,
    execute_filesystem_create_request,
    reconstruct_filesystem_worker_replay,
)


AIGOL_DOMAIN_EXECUTION_BINDING_RUNTIME_VERSION = "AIGOL_DOMAIN_EXECUTION_BINDING_V1"
DOMAIN_EXECUTION_CONTRACT_ARTIFACT_V1 = "DOMAIN_EXECUTION_CONTRACT_ARTIFACT_V1"
DOMAIN_PROVIDER_BINDING_ARTIFACT_V1 = "DOMAIN_PROVIDER_BINDING_ARTIFACT_V1"
DOMAIN_WORKER_BINDING_ARTIFACT_V1 = "DOMAIN_WORKER_BINDING_ARTIFACT_V1"
DOMAIN_EXECUTION_EVIDENCE_ARTIFACT_V1 = "DOMAIN_EXECUTION_EVIDENCE_ARTIFACT_V1"

DOMAIN_EXECUTION_REQUESTED = "DOMAIN_EXECUTION_REQUESTED"
DOMAIN_EXECUTION_AUTHORIZED = "DOMAIN_EXECUTION_AUTHORIZED"
DOMAIN_EXECUTION_DISPATCHED = "DOMAIN_EXECUTION_DISPATCHED"
DOMAIN_EXECUTION_COMPLETED = "DOMAIN_EXECUTION_COMPLETED"
DOMAIN_EXECUTION_REJECTED = "DOMAIN_EXECUTION_REJECTED"

DOMAIN_EXECUTION_COMPLETED_STATUS = "DOMAIN_EXECUTION_COMPLETED"
DOMAIN_EXECUTION_REJECTED_STATUS = "DOMAIN_EXECUTION_REJECTED"

REPLAY_STEPS = (
    "domain_execution_requested",
    "domain_execution_authorized",
    "domain_execution_dispatched",
    "domain_execution_completed",
    "domain_execution_rejected",
)

DOMAIN_PROVIDER_ID = "domain-static-provider"
DOMAIN_PROVIDER_VERSION = "AIGOL_DOMAIN_EXECUTION_BINDING_V1"
DEFAULT_OUTPUT_FILE = "domain_execution_evidence.txt"
DEFAULT_OUTPUT_CONTENT = "AIGOL_DOMAIN_EXECUTION_BINDING_V1 certified domain execution evidence"


class DomainExecutionProviderAdapter:
    """Deterministic proposal-only provider for domain execution binding tests."""

    provider_id = DOMAIN_PROVIDER_ID
    provider_version = DOMAIN_PROVIDER_VERSION

    def generate_proposal(self, request: Any, *, proposal_id: str, timestamp: str) -> ProviderProposalEnvelope:
        if not isinstance(request, dict):
            raise FailClosedRuntimeError("domain execution provider failed closed: request must be a JSON object")
        file_path = _require_string(request.get("file_path"), "file_path")
        content = _require_string(request.get("content"), "content")
        return create_provider_proposal_envelope(
            proposal_id=proposal_id,
            provider_id=self.provider_id,
            provider_version=self.provider_version,
            request=deepcopy(request),
            response={
                "proposal_kind": "DOMAIN_FILESYSTEM_CREATE_FILE",
                "reason": "Create one governed domain execution evidence file.",
                "target_worker": FILESYSTEM_WORKER_ID,
                "file_path": file_path,
                "content": content,
            },
            timestamp=timestamp,
        )


def execute_domain_request(
    *,
    domain_artifact: dict[str, Any],
    domain_execution_id: str,
    workspace_root: str | Path,
    actor_id: str,
    timestamp: str,
    replay_dir: str | Path,
    file_path: str = DEFAULT_OUTPUT_FILE,
    content: str = DEFAULT_OUTPUT_CONTENT,
    provider_registry: ProviderRegistry | None = None,
    provider_adapter: ProviderAdapter | None = None,
) -> dict[str, Any]:
    """Execute one governed domain request through provider proposal and worker execution runtimes."""

    replay_path = Path(replay_dir)
    requested: dict[str, Any] | None = None
    try:
        _ensure_replay_available(replay_path)
        domain = _validate_active_domain(domain_artifact)
        contract = _contract_artifact(
            domain=domain,
            domain_execution_id=domain_execution_id,
            actor_id=actor_id,
            timestamp=timestamp,
            file_path=file_path,
            content=content,
        )
        requested = _evidence_artifact(
            event_type=DOMAIN_EXECUTION_REQUESTED,
            domain=domain,
            contract=contract,
            previous_artifact=None,
            actor_id=actor_id,
            timestamp=timestamp,
            provider_binding=None,
            worker_binding=None,
            authorization_capture=None,
            worker_capture=None,
            rejection_reason=None,
        )
        _persist_step(replay_path, 0, DOMAIN_EXECUTION_REQUESTED, requested)
        registry = provider_registry or default_domain_execution_provider_registry()
        adapter = provider_adapter or DomainExecutionProviderAdapter()
        provider_capture = run_provider_attachment(
            provider_id=DOMAIN_PROVIDER_ID,
            request=contract["execution_request"],
            proposal_id=f"{contract['domain_execution_id']}:PROVIDER-PROPOSAL",
            timestamp=timestamp,
            registry=registry,
            adapter=adapter,
            replay_dir=replay_path / "provider",
        )
        provider_binding = _provider_binding_artifact(contract=contract, provider_capture=provider_capture)
        authorization_capture = authorize_worker_request(
            authorization_id=f"{contract['domain_execution_id']}:AUTHORIZATION",
            proposal=_proposal_for_authorization(provider_capture),
            worker_target=_worker_target(),
            authorization_scope=AUTHORIZED_SCOPE,
            authorization_timestamp=timestamp,
            replay_dir=replay_path / "authorization",
        )
        authorized = _evidence_artifact(
            event_type=DOMAIN_EXECUTION_AUTHORIZED,
            domain=domain,
            contract=contract,
            previous_artifact=requested,
            actor_id=actor_id,
            timestamp=timestamp,
            provider_binding=provider_binding,
            worker_binding=None,
            authorization_capture=authorization_capture,
            worker_capture=None,
            rejection_reason=None,
        )
        _persist_step(replay_path, 1, DOMAIN_EXECUTION_AUTHORIZED, authorized)
        worker_request = create_authorized_worker_request(
            authorization_record=authorization_capture["authorization_record"],
            request_id=f"{contract['domain_execution_id']}:AUTHORIZED-WORKER-REQUEST",
            file_path=provider_binding["proposed_file_path"],
            content=provider_binding["proposed_content"],
            request_timestamp=timestamp,
            proposal_reference={
                "proposal_id": provider_capture["provider_proposal_envelope"]["proposal_id"],
                "proposal_hash": provider_capture["provider_proposal_envelope"]["proposal_hash"],
            },
            replay_reference=authorization_capture["authorization_record"]["authorization_hash"],
        )
        worker_binding = _worker_binding_artifact(contract=contract, worker_request=worker_request)
        dispatched = _evidence_artifact(
            event_type=DOMAIN_EXECUTION_DISPATCHED,
            domain=domain,
            contract=contract,
            previous_artifact=authorized,
            actor_id=actor_id,
            timestamp=timestamp,
            provider_binding=provider_binding,
            worker_binding=worker_binding,
            authorization_capture=authorization_capture,
            worker_capture=None,
            rejection_reason=None,
        )
        _persist_step(replay_path, 2, DOMAIN_EXECUTION_DISPATCHED, dispatched)
        worker_capture = execute_filesystem_create_request(
            authorized_request=worker_request,
            base_dir=workspace_root,
            replay_dir=replay_path / "worker",
        )
        _validate_worker_success(worker_capture)
        completed = _evidence_artifact(
            event_type=DOMAIN_EXECUTION_COMPLETED,
            domain=domain,
            contract=contract,
            previous_artifact=dispatched,
            actor_id=actor_id,
            timestamp=timestamp,
            provider_binding=provider_binding,
            worker_binding=worker_binding,
            authorization_capture=authorization_capture,
            worker_capture=worker_capture,
            rejection_reason=None,
        )
        _persist_step(replay_path, 3, DOMAIN_EXECUTION_COMPLETED, completed)
        reconstructed = reconstruct_domain_execution_binding_replay(replay_path)
        return {
            "domain_execution_status": reconstructed["domain_execution_status"],
            "domain_execution_evidence": deepcopy(completed),
            "domain_execution_contract": deepcopy(contract),
            "domain_provider_binding": deepcopy(provider_binding),
            "domain_worker_binding": deepcopy(worker_binding),
            "provider_capture": deepcopy(provider_capture),
            "authorization_capture": deepcopy(authorization_capture),
            "worker_capture": deepcopy(worker_capture),
            "domain_evidence_replay": reconstructed,
            "replay_visible": True,
        }
    except Exception as exc:
        rejection = _rejection_artifact(
            requested=requested,
            domain_artifact=domain_artifact,
            domain_execution_id=domain_execution_id,
            actor_id=actor_id,
            timestamp=timestamp,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 4, DOMAIN_EXECUTION_REJECTED, rejection)
        return {
            "domain_execution_status": DOMAIN_EXECUTION_REJECTED_STATUS,
            "domain_execution_rejection": deepcopy(rejection),
            "failure_reason": rejection["failure_reason"],
            "replay_visible": True,
        }


def reconstruct_domain_execution_binding_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct domain execution binding replay and downstream provider/worker evidence."""

    replay_path = Path(replay_dir)
    if (replay_path / "004_domain_execution_rejected.json").exists():
        requested = _load_optional_wrapper(replay_path, 0)
        rejected_wrapper = _load_wrapper(replay_path, 4)
        rejected = _validate_evidence_artifact(rejected_wrapper["artifact"], expected_event=DOMAIN_EXECUTION_REJECTED)
        if requested is not None:
            requested_artifact = _validate_evidence_artifact(requested["artifact"], expected_event=DOMAIN_EXECUTION_REQUESTED)
            if rejected.get("previous_artifact_hash") != requested_artifact["artifact_hash"]:
                raise FailClosedRuntimeError("domain execution binding replay rejection lineage mismatch")
        return {
            "domain_execution_status": DOMAIN_EXECUTION_REJECTED_STATUS,
            "domain_execution_id": rejected["domain_execution_id"],
            "domain_id": rejected["domain_id"],
            "lifecycle_events": [DOMAIN_EXECUTION_REQUESTED, DOMAIN_EXECUTION_REJECTED] if requested else [DOMAIN_EXECUTION_REJECTED],
            "failure_reason": rejected["failure_reason"],
            "replay_visible": True,
            "replay_artifact_count": 2 if requested else 1,
            "replay_hash": replay_hash([wrapper for wrapper in (requested, rejected_wrapper) if wrapper is not None]),
        }

    wrappers = [_load_wrapper(replay_path, index) for index in range(4)]
    previous: dict[str, Any] | None = None
    for wrapper, event_type in zip(
        wrappers,
        (DOMAIN_EXECUTION_REQUESTED, DOMAIN_EXECUTION_AUTHORIZED, DOMAIN_EXECUTION_DISPATCHED, DOMAIN_EXECUTION_COMPLETED),
    ):
        artifact = _validate_evidence_artifact(wrapper["artifact"], expected_event=event_type)
        _validate_continuity(previous, artifact)
        previous = artifact
    completed = wrappers[-1]["artifact"]
    provider_replay = reconstruct_provider_attachment_replay(replay_path / "provider")
    authorization_replay = reconstruct_authorization_replay(replay_path / "authorization")
    worker_replay = reconstruct_filesystem_worker_replay(replay_path / "worker")
    if worker_replay["execution_status"] != "SUCCEEDED":
        raise FailClosedRuntimeError("domain execution binding replay worker execution mismatch")
    if authorization_replay["authorization_status"] != "AUTHORIZED":
        raise FailClosedRuntimeError("domain execution binding replay authorization mismatch")
    return {
        "domain_execution_status": DOMAIN_EXECUTION_COMPLETED_STATUS,
        "domain_execution_id": completed["domain_execution_id"],
        "domain_id": completed["domain_id"],
        "lifecycle_events": [wrapper["event_type"] for wrapper in wrappers],
        "provider_id": provider_replay["provider_id"],
        "provider_invoked": provider_replay["provider_invoked"],
        "worker_id": worker_replay["worker_id"],
        "worker_invoked": worker_replay["worker_invoked"],
        "worker_execution_status": worker_replay["execution_status"],
        "domain_evidence_hash": completed["artifact_hash"],
        "output_file": worker_replay["file_path"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def default_domain_execution_provider_registry() -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register_provider(
        ProviderMetadata(
            provider_id=DOMAIN_PROVIDER_ID,
            provider_type="static",
            provider_version=DOMAIN_PROVIDER_VERSION,
            provider_status=AVAILABLE,
            domain="domain_execution",
            capability="execution_proposal",
            resource_type="provider",
        )
    )
    return registry


def _contract_artifact(
    *,
    domain: dict[str, Any],
    domain_execution_id: str,
    actor_id: str,
    timestamp: str,
    file_path: str,
    content: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": DOMAIN_EXECUTION_CONTRACT_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_EXECUTION_BINDING_RUNTIME_VERSION,
        "domain_execution_id": _require_string(domain_execution_id, "domain_execution_id"),
        "domain_id": domain["domain_id"],
        "domain_artifact_hash": domain["artifact_hash"],
        "domain_replay_id": domain["domain_replay_id"],
        "domain_lifecycle_state": domain["lifecycle_state"],
        "execution_request": {
            "domain_execution_id": _require_string(domain_execution_id, "domain_execution_id"),
            "domain_id": domain["domain_id"],
            "file_path": _require_string(file_path, "file_path"),
            "content": _require_string(content, "content"),
            "requested_by": _require_string(actor_id, "actor_id"),
            "requested_at": _require_string(timestamp, "timestamp"),
        },
        "provider_binding_required": True,
        "worker_binding_required": True,
        "execution_authorization_required": True,
        "target_provider_id": DOMAIN_PROVIDER_ID,
        "target_worker_id": FILESYSTEM_WORKER_ID,
        "authorized_scope": AUTHORIZED_SCOPE,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _provider_binding_artifact(*, contract: dict[str, Any], provider_capture: dict[str, Any]) -> dict[str, Any]:
    envelope = provider_capture["provider_proposal_envelope"]
    returned = provider_capture["provider_proposal_returned"]
    if returned.get("event_type") != "PROVIDER_PROPOSAL_RETURNED":
        raise FailClosedRuntimeError("domain execution binding failed closed: provider proposal not returned")
    response = envelope["response"]
    if response.get("target_worker") != FILESYSTEM_WORKER_ID:
        raise FailClosedRuntimeError("domain execution binding failed closed: provider worker mismatch")
    artifact = {
        "artifact_type": DOMAIN_PROVIDER_BINDING_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_EXECUTION_BINDING_RUNTIME_VERSION,
        "domain_execution_id": contract["domain_execution_id"],
        "domain_execution_contract_hash": contract["artifact_hash"],
        "provider_id": envelope["provider_id"],
        "provider_version": envelope["provider_version"],
        "provider_proposal_reference": envelope["proposal_id"],
        "provider_proposal_hash": envelope["proposal_hash"],
        "provider_replay_hash": returned["artifact_hash"],
        "proposed_file_path": _require_string(response.get("file_path"), "file_path"),
        "proposed_content": _require_string(response.get("content"), "content"),
        "provider_invoked": True,
        "provider_authority": False,
        "execution_authority": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _worker_binding_artifact(*, contract: dict[str, Any], worker_request: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "artifact_type": DOMAIN_WORKER_BINDING_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_EXECUTION_BINDING_RUNTIME_VERSION,
        "domain_execution_id": contract["domain_execution_id"],
        "domain_execution_contract_hash": contract["artifact_hash"],
        "worker_id": worker_request["worker_id"],
        "authorized_scope": worker_request["authorized_scope"],
        "authorized_worker_request_id": worker_request["request_id"],
        "authorized_worker_request_hash": worker_request["request_hash"],
        "authorization_id": worker_request["authorization_id"],
        "authorization_hash": worker_request["authorization_hash"],
        "worker_dispatched": True,
        "worker_self_authorized": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _evidence_artifact(
    *,
    event_type: str,
    domain: dict[str, Any],
    contract: dict[str, Any],
    previous_artifact: dict[str, Any] | None,
    actor_id: str,
    timestamp: str,
    provider_binding: dict[str, Any] | None,
    worker_binding: dict[str, Any] | None,
    authorization_capture: dict[str, Any] | None,
    worker_capture: dict[str, Any] | None,
    rejection_reason: str | None,
) -> dict[str, Any]:
    previous_hash = previous_artifact["artifact_hash"] if previous_artifact else None
    artifact = {
        "artifact_type": DOMAIN_EXECUTION_EVIDENCE_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_EXECUTION_BINDING_RUNTIME_VERSION,
        "event_type": event_type,
        "domain_execution_id": contract["domain_execution_id"],
        "domain_id": domain["domain_id"],
        "domain_replay_id": domain["domain_replay_id"],
        "domain_artifact_hash": domain["artifact_hash"],
        "domain_execution_contract_hash": contract["artifact_hash"],
        "previous_artifact_hash": previous_hash,
        "chain_hash": replay_hash(
            {
                "event_type": event_type,
                "domain_execution_id": contract["domain_execution_id"],
                "previous_artifact_hash": previous_hash,
            }
        ),
        "actor_id": _require_string(actor_id, "actor_id"),
        "timestamp": _require_string(timestamp, "timestamp"),
        "provider_binding_hash": provider_binding["artifact_hash"] if provider_binding else None,
        "worker_binding_hash": worker_binding["artifact_hash"] if worker_binding else None,
        "authorization_hash": (
            authorization_capture["authorization_record"]["authorization_hash"] if authorization_capture else None
        ),
        "worker_execution_hash": (
            worker_capture["filesystem_worker_execution"]["artifact_hash"] if worker_capture else None
        ),
        "execution_completed": event_type == DOMAIN_EXECUTION_COMPLETED,
        "execution_rejected": event_type == DOMAIN_EXECUTION_REJECTED,
        "failure_reason": rejection_reason,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _rejection_artifact(
    *,
    requested: dict[str, Any] | None,
    domain_artifact: dict[str, Any],
    domain_execution_id: str,
    actor_id: str,
    timestamp: str,
    failure_reason: str,
) -> dict[str, Any]:
    domain_id = domain_artifact.get("domain_id") if isinstance(domain_artifact, dict) else "INVALID_DOMAIN"
    domain_replay_id = domain_artifact.get("domain_replay_id") if isinstance(domain_artifact, dict) else "INVALID_REPLAY"
    domain_hash = domain_artifact.get("artifact_hash") if isinstance(domain_artifact, dict) else "FAILED_CLOSED"
    previous_hash = requested["artifact_hash"] if requested else None
    artifact = {
        "artifact_type": DOMAIN_EXECUTION_EVIDENCE_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_EXECUTION_BINDING_RUNTIME_VERSION,
        "event_type": DOMAIN_EXECUTION_REJECTED,
        "domain_execution_id": domain_execution_id if isinstance(domain_execution_id, str) and domain_execution_id.strip() else "INVALID_EXECUTION",
        "domain_id": domain_id,
        "domain_replay_id": domain_replay_id,
        "domain_artifact_hash": domain_hash,
        "domain_execution_contract_hash": requested["domain_execution_contract_hash"] if requested else None,
        "previous_artifact_hash": previous_hash,
        "chain_hash": replay_hash(
            {
                "event_type": DOMAIN_EXECUTION_REJECTED,
                "domain_execution_id": domain_execution_id,
                "previous_artifact_hash": previous_hash,
            }
        ),
        "actor_id": actor_id if isinstance(actor_id, str) and actor_id.strip() else "INVALID_ACTOR",
        "timestamp": timestamp if isinstance(timestamp, str) and timestamp.strip() else "INVALID_TIMESTAMP",
        "provider_binding_hash": None,
        "worker_binding_hash": None,
        "authorization_hash": None,
        "worker_execution_hash": None,
        "execution_completed": False,
        "execution_rejected": True,
        "failure_reason": failure_reason,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _proposal_for_authorization(provider_capture: dict[str, Any]) -> dict[str, Any]:
    envelope = provider_capture["provider_proposal_envelope"]
    return {
        "proposal_id": envelope["proposal_id"],
        "proposal_hash": envelope["proposal_hash"],
        "proposal_lineage": {
            "provider_id": envelope["provider_id"],
            "provider_version": envelope["provider_version"],
            "proposal_hash": envelope["proposal_hash"],
        },
        "governance_review": "DOMAIN_EXECUTION_BINDING_GOVERNANCE_REVIEW_V1",
    }


def _worker_target() -> dict[str, str]:
    return {
        "worker_id": FILESYSTEM_WORKER_ID,
        "domain": "filesystem",
        "capability": "filesystem_create_file",
    }


def _validate_active_domain(domain_artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(domain_artifact, dict):
        raise FailClosedRuntimeError("domain execution binding failed closed: domain artifact is required")
    _verify_artifact_hash(domain_artifact, "domain artifact")
    if domain_artifact.get("artifact_type") != DOMAIN_LIFECYCLE_ARTIFACT_V1:
        raise FailClosedRuntimeError("domain execution binding failed closed: invalid domain artifact")
    if domain_artifact.get("lifecycle_state") != ACTIVE:
        raise FailClosedRuntimeError("domain execution binding failed closed: domain must be ACTIVE")
    if domain_artifact.get("replay_visible") is not True:
        raise FailClosedRuntimeError("domain execution binding failed closed: domain replay visibility missing")
    return deepcopy(domain_artifact)


def _validate_worker_success(worker_capture: dict[str, Any]) -> None:
    execution = worker_capture.get("filesystem_worker_execution") if isinstance(worker_capture, dict) else None
    if not isinstance(execution, dict):
        raise FailClosedRuntimeError("domain execution binding failed closed: worker execution missing")
    if execution.get("event_type") != FILESYSTEM_WORKER_EXECUTED:
        raise FailClosedRuntimeError(execution.get("failure_reason") or "domain execution binding failed closed: worker execution failed")
    if execution.get("execution_status") != "SUCCEEDED":
        raise FailClosedRuntimeError("domain execution binding failed closed: worker execution failed")


def _validate_evidence_artifact(artifact: dict[str, Any], *, expected_event: str) -> dict[str, Any]:
    _verify_artifact_hash(artifact, "domain execution evidence artifact")
    if artifact.get("artifact_type") != DOMAIN_EXECUTION_EVIDENCE_ARTIFACT_V1:
        raise FailClosedRuntimeError("domain execution binding replay invalid evidence artifact")
    if artifact.get("event_type") != expected_event:
        raise FailClosedRuntimeError("domain execution binding replay event mismatch")
    expected_chain = replay_hash(
        {
            "event_type": artifact["event_type"],
            "domain_execution_id": artifact["domain_execution_id"],
            "previous_artifact_hash": artifact.get("previous_artifact_hash"),
        }
    )
    if artifact.get("chain_hash") != expected_chain:
        raise FailClosedRuntimeError("domain execution binding replay chain hash mismatch")
    if artifact.get("replay_visible") is not True:
        raise FailClosedRuntimeError("domain execution binding replay visibility missing")
    return deepcopy(artifact)


def _validate_continuity(previous: dict[str, Any] | None, artifact: dict[str, Any]) -> None:
    if previous is None:
        if artifact.get("previous_artifact_hash") is not None:
            raise FailClosedRuntimeError("domain execution binding replay parent mismatch")
        return
    if artifact["domain_execution_id"] != previous["domain_execution_id"]:
        raise FailClosedRuntimeError("domain execution binding replay execution id mismatch")
    if artifact["domain_replay_id"] != previous["domain_replay_id"]:
        raise FailClosedRuntimeError("domain execution binding replay domain continuity mismatch")
    if artifact.get("previous_artifact_hash") != previous["artifact_hash"]:
        raise FailClosedRuntimeError("domain execution binding replay hash continuity mismatch")


def _load_optional_wrapper(replay_path: Path, index: int) -> dict[str, Any] | None:
    path = replay_path / f"{index:03d}_{REPLAY_STEPS[index]}.json"
    return _load_wrapper(replay_path, index) if path.exists() else None


def _load_wrapper(replay_path: Path, index: int) -> dict[str, Any]:
    step = REPLAY_STEPS[index]
    wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
    if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
        raise FailClosedRuntimeError("domain execution binding replay ordering mismatch")
    _verify_wrapper_hash(wrapper)
    return wrapper


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, event_type: str, artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact, "domain execution evidence artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": REPLAY_STEPS[index],
        "event_type": event_type,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{REPLAY_STEPS[index]}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, event_type: str, artifact: dict[str, Any]) -> None:
    path = replay_dir / f"{index:03d}_{REPLAY_STEPS[index]}.json"
    if not path.exists():
        try:
            _persist_step(replay_dir, index, event_type, artifact)
        except FailClosedRuntimeError:
            return


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("domain execution binding replay hash missing")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("domain execution binding replay hash mismatch")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict) or "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash missing")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "domain execution binding failed closed"
