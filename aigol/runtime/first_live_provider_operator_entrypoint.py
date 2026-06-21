"""Operator entrypoint for AIGOL_FIRST_LIVE_PROVIDER_OPERATOR_ENTRYPOINT_V1."""

from __future__ import annotations

from copy import deepcopy
import os
from pathlib import Path
from typing import Any, Callable

from aigol.runtime.external_resource_registry_runtime import COGNITION_PROVIDER, OPENAI_PROVIDER_ID
from aigol.runtime.first_live_provider_dispatch_authorization_instantiation import (
    DISPATCH_AUTHORIZED,
    FIRST_LIVE_PROVIDER_DISPATCH_AUTHORIZATION_ARTIFACT_V1,
    REPLAY_STEPS as DISPATCH_AUTHORIZATION_REPLAY_STEPS,
)
from aigol.runtime.first_live_provider_execution_runtime import (
    STATUS_COMPLETED,
    run_first_live_provider_execution_runtime,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_credential_vault import retrieve_provider_credential
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_FIRST_LIVE_PROVIDER_OPERATOR_ENTRYPOINT_V1"

FIRST_LIVE_PROVIDER_OPERATOR_DISPATCH_REQUEST_ARTIFACT_V1 = (
    "FIRST_LIVE_PROVIDER_OPERATOR_DISPATCH_REQUEST_ARTIFACT_V1"
)
FIRST_LIVE_PROVIDER_OPERATOR_DISPATCH_RESULT_ARTIFACT_V1 = (
    "FIRST_LIVE_PROVIDER_OPERATOR_DISPATCH_RESULT_ARTIFACT_V1"
)

STATUS_OPERATOR_DISPATCH_COMPLETED = "OPERATOR_DISPATCH_COMPLETED"
STATUS_FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "first_live_provider_operator_dispatch_request",
    "first_live_provider_operator_dispatch_result",
)

BoundaryTransport = Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]


def run_first_live_provider_operator_entrypoint(
    *,
    operator_request_id: str,
    operator_id: str,
    human_request: str,
    created_at: str,
    activation_package_replay_dir: str | Path,
    dispatch_authorization_replay_dir: str | Path,
    execution_replay_dir: str | Path,
    operator_replay_dir: str | Path,
    transport: BoundaryTransport | None,
    confirm_dispatch: bool,
    model: str = "gpt-5.1",
    timeout_seconds: int = 20,
    live_transport_enabled: bool = False,
    vault_path: str | Path | None = None,
) -> dict[str, Any]:
    """Run one operator-confirmed OpenAI dispatch through the governed execution runtime."""

    operator_replay_path = Path(operator_replay_dir)
    request_id = operator_request_id if isinstance(operator_request_id, str) and operator_request_id.strip() else "INVALID"
    request_artifact: dict[str, Any] | None = None
    try:
        request_id = _require_string(operator_request_id, "operator_request_id")
        _ensure_replay_available(operator_replay_path)
        dispatch_authorization = load_dispatch_authorization_artifact(dispatch_authorization_replay_dir)
        _validate_operator_dispatch_request(
            dispatch_authorization_artifact=dispatch_authorization,
            created_at=created_at,
            confirm_dispatch=confirm_dispatch,
        )
        credential_reference = "vault://provider/openai" if vault_path is not None else "env:AIGOL_OPENAI_API_KEY"
        _verify_credential_available(credential_reference, vault_path=vault_path)
        request_artifact = create_operator_dispatch_request_artifact(
            operator_request_id=request_id,
            operator_id=operator_id,
            human_request=human_request,
            activation_package_replay_dir=activation_package_replay_dir,
            dispatch_authorization_replay_dir=dispatch_authorization_replay_dir,
            execution_replay_dir=execution_replay_dir,
            dispatch_authorization_artifact=dispatch_authorization,
            credential_reference=credential_reference,
            created_at=created_at,
        )
        execution = run_first_live_provider_execution_runtime(
            execution_id=f"{request_id}:EXECUTION",
            human_request=human_request,
            created_at=created_at,
            replay_dir=execution_replay_dir,
            activation_package_replay_dir=activation_package_replay_dir,
            dispatch_authorization_artifact=dispatch_authorization,
            transport=transport,
            model=model,
            timeout_seconds=timeout_seconds,
            live_transport_enabled=live_transport_enabled,
            vault_path=vault_path,
        )
        result_artifact = create_operator_dispatch_result_artifact(
            operator_request_artifact=request_artifact,
            execution_capture=execution,
            failure_reason=execution["failure_reason"],
            created_at=created_at,
        )
        _persist_sequence(operator_replay_path, (request_artifact, result_artifact))
        return _capture(
            operator_request_id=request_id,
            final_status=(
                STATUS_OPERATOR_DISPATCH_COMPLETED if execution["final_status"] == STATUS_COMPLETED else STATUS_FAILED_CLOSED
            ),
            failure_reason=execution["failure_reason"],
            operator_replay_path=operator_replay_path,
            execution_replay_path=Path(execution_replay_dir),
            request_artifact=request_artifact,
            result_artifact=result_artifact,
            execution_capture=execution,
        )
    except Exception as exc:
        reason = str(exc) if isinstance(exc, FailClosedRuntimeError) else "first live provider operator entrypoint failed closed"
        if request_artifact is None:
            request_artifact = create_failed_operator_dispatch_request_artifact(
                operator_request_id=request_id,
                failure_reason=reason,
                created_at=created_at,
            )
        result_artifact = create_failed_operator_dispatch_result_artifact(
            operator_request_artifact=request_artifact,
            failure_reason=reason,
            execution_replay_dir=execution_replay_dir,
            created_at=created_at,
        )
        if not _replay_exists(operator_replay_path):
            _persist_sequence(operator_replay_path, (request_artifact, result_artifact))
        return _capture(
            operator_request_id=request_id,
            final_status=STATUS_FAILED_CLOSED,
            failure_reason=reason,
            operator_replay_path=operator_replay_path,
            execution_replay_path=Path(execution_replay_dir),
            request_artifact=request_artifact,
            result_artifact=result_artifact,
            execution_capture=None,
        )


def load_dispatch_authorization_artifact(dispatch_authorization_replay_dir: str | Path) -> dict[str, Any]:
    replay_path = Path(dispatch_authorization_replay_dir)
    index = len(DISPATCH_AUTHORIZATION_REPLAY_STEPS) - 1
    step = DISPATCH_AUTHORIZATION_REPLAY_STEPS[index]
    wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
    if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
        raise FailClosedRuntimeError("first live provider operator entrypoint failed closed: authorization replay mismatch")
    _verify_wrapper_hash(wrapper)
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("first live provider operator entrypoint failed closed: authorization artifact missing")
    _verify_artifact_hash(artifact, "dispatch authorization")
    return deepcopy(artifact)


def create_operator_dispatch_request_artifact(
    *,
    operator_request_id: str,
    operator_id: str,
    human_request: str,
    activation_package_replay_dir: str | Path,
    dispatch_authorization_replay_dir: str | Path,
    execution_replay_dir: str | Path,
    dispatch_authorization_artifact: dict[str, Any],
    credential_reference: str,
    created_at: str,
) -> dict[str, Any]:
    _verify_artifact_hash(dispatch_authorization_artifact, "dispatch authorization")
    artifact = {
        "artifact_type": FIRST_LIVE_PROVIDER_OPERATOR_DISPATCH_REQUEST_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "operator_request_id": _require_string(operator_request_id, "operator_request_id"),
        "operator_id": _require_string(operator_id, "operator_id"),
        "human_request_hash": replay_hash(_require_string(human_request, "human_request")),
        "provider_id": OPENAI_PROVIDER_ID,
        "provider_resource_type": COGNITION_PROVIDER,
        "dispatch_authorization_artifact_hash": dispatch_authorization_artifact["artifact_hash"],
        "dispatch_attempt_limit": 1,
        "dispatch_attempt_number": 1,
        "operator_confirmed_dispatch": True,
        "credential_reference": _require_string(credential_reference, "credential_reference"),
        "credential_available": True,
        "credential_secret_replayed": False,
        "authorization_header_replayed": False,
        "activation_package_replay_reference": str(Path(activation_package_replay_dir)),
        "dispatch_authorization_replay_reference": str(Path(dispatch_authorization_replay_dir)),
        "execution_replay_reference": str(Path(execution_replay_dir)),
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "provider_routing_performed": False,
        "fallback_performed": False,
        "automatic_retry_performed": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def create_operator_dispatch_result_artifact(
    *,
    operator_request_artifact: dict[str, Any],
    execution_capture: dict[str, Any],
    failure_reason: str,
    created_at: str,
) -> dict[str, Any]:
    _verify_artifact_hash(operator_request_artifact, "operator request")
    artifact = {
        "artifact_type": FIRST_LIVE_PROVIDER_OPERATOR_DISPATCH_RESULT_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "operator_request_id": operator_request_artifact["operator_request_id"],
        "operator_request_artifact_hash": operator_request_artifact["artifact_hash"],
        "execution_runtime": execution_capture["milestone_id"],
        "execution_status": execution_capture["final_status"],
        "failure_reason": _redact_failure_reason(failure_reason),
        "execution_replay_reference": execution_capture["replay_reference"],
        "execution_runtime_hash": execution_capture["runtime_hash"],
        "dispatch_attempt_limit": 1,
        "dispatch_attempt_number": 1,
        "credential_secret_replayed": False,
        "authorization_header_replayed": False,
        "worker_invoked": execution_capture["worker_invoked"],
        "provider_routing_performed": False,
        "fallback_performed": False,
        "automatic_retry_performed": False,
        "governance_modified": execution_capture["governance_modified"],
        "replay_modified": execution_capture["replay_modified"],
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def create_failed_operator_dispatch_request_artifact(
    *, operator_request_id: str, failure_reason: str, created_at: str
) -> dict[str, Any]:
    artifact = {
        "artifact_type": FIRST_LIVE_PROVIDER_OPERATOR_DISPATCH_REQUEST_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "operator_request_id": _require_string(operator_request_id, "operator_request_id"),
        "request_status": STATUS_FAILED_CLOSED,
        "failure_reason": _redact_failure_reason(failure_reason),
        "provider_id": OPENAI_PROVIDER_ID,
        "dispatch_attempt_limit": 1,
        "credential_secret_replayed": False,
        "authorization_header_replayed": False,
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def create_failed_operator_dispatch_result_artifact(
    *,
    operator_request_artifact: dict[str, Any],
    failure_reason: str,
    execution_replay_dir: str | Path,
    created_at: str,
) -> dict[str, Any]:
    _verify_artifact_hash(operator_request_artifact, "operator request")
    artifact = {
        "artifact_type": FIRST_LIVE_PROVIDER_OPERATOR_DISPATCH_RESULT_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "operator_request_id": operator_request_artifact["operator_request_id"],
        "operator_request_artifact_hash": operator_request_artifact["artifact_hash"],
        "execution_status": STATUS_FAILED_CLOSED,
        "failure_reason": _redact_failure_reason(failure_reason),
        "execution_replay_reference": str(Path(execution_replay_dir)),
        "dispatch_attempt_limit": 1,
        "dispatch_attempt_number": 0,
        "credential_secret_replayed": False,
        "authorization_header_replayed": False,
        "worker_invoked": False,
        "provider_routing_performed": False,
        "fallback_performed": False,
        "automatic_retry_performed": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def reconstruct_first_live_provider_operator_entrypoint_replay(replay_dir: str | Path) -> dict[str, Any]:
    replay_path = Path(replay_dir)
    wrappers = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("first live provider operator entrypoint replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("first live provider operator entrypoint replay artifact missing")
        _verify_artifact_hash(artifact, f"operator entrypoint {step}")
        wrappers.append(wrapper)
    result = wrappers[1]["artifact"]
    return {
        "milestone_id": MILESTONE_ID,
        "operator_request_id": result["operator_request_id"],
        "final_status": result["execution_status"],
        "execution_replay_reference": result["execution_replay_reference"],
        "credential_secret_replayed": result["credential_secret_replayed"],
        "authorization_header_replayed": result["authorization_header_replayed"],
        "worker_invoked": result["worker_invoked"],
        "governance_modified": result["governance_modified"],
        "replay_modified": result["replay_modified"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_operator_dispatch_request(
    *,
    dispatch_authorization_artifact: dict[str, Any],
    created_at: str,
    confirm_dispatch: bool,
) -> None:
    if confirm_dispatch is not True:
        raise FailClosedRuntimeError("first live provider operator entrypoint failed closed: operator confirmation missing")
    _verify_artifact_hash(dispatch_authorization_artifact, "dispatch authorization")
    if dispatch_authorization_artifact.get("artifact_type") != FIRST_LIVE_PROVIDER_DISPATCH_AUTHORIZATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("first live provider operator entrypoint failed closed: invalid dispatch authorization")
    if dispatch_authorization_artifact.get("authorization_status") != DISPATCH_AUTHORIZED:
        raise FailClosedRuntimeError("first live provider operator entrypoint failed closed: dispatch not authorized")
    if dispatch_authorization_artifact.get("provider_id") != OPENAI_PROVIDER_ID:
        raise FailClosedRuntimeError("first live provider operator entrypoint failed closed: unauthorized provider")
    if dispatch_authorization_artifact.get("provider_resource_type") != COGNITION_PROVIDER:
        raise FailClosedRuntimeError("first live provider operator entrypoint failed closed: invalid resource type")
    if dispatch_authorization_artifact.get("dispatch_count") != 1:
        raise FailClosedRuntimeError("first live provider operator entrypoint failed closed: invalid dispatch count")
    if dispatch_authorization_artifact.get("dispatch_attempt_limit") != 1:
        raise FailClosedRuntimeError("first live provider operator entrypoint failed closed: invalid attempt limit")
    if dispatch_authorization_artifact.get("live_dispatch_attempted") is not False:
        raise FailClosedRuntimeError("first live provider operator entrypoint failed closed: authorization already attempted")
    if dispatch_authorization_artifact.get("live_dispatch_performed") is not False:
        raise FailClosedRuntimeError("first live provider operator entrypoint failed closed: authorization already performed")
    if _require_string(created_at, "created_at") > _require_string(dispatch_authorization_artifact.get("expires_at"), "expires_at"):
        raise FailClosedRuntimeError("first live provider operator entrypoint failed closed: authorization expired")
    _reject_forbidden_flags(dispatch_authorization_artifact)


def _verify_credential_available(credential_reference: str, *, vault_path: str | Path | None = None) -> None:
    reference = _require_string(credential_reference, "credential_reference")
    if reference == "vault://provider/openai":
        retrieve_provider_credential(
            provider_id="openai",
            authorization_context={"runtime": MILESTONE_ID},
            vault_path=vault_path,
            allow_env_fallback=False,
        )
        return
    if reference != "env:AIGOL_OPENAI_API_KEY":
        raise FailClosedRuntimeError("first live provider operator entrypoint failed closed: unsupported credential reference")
    value = os.environ.get("AIGOL_OPENAI_API_KEY")
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError("first live provider operator entrypoint failed closed: credential unavailable")


def _persist_sequence(replay_path: Path, artifacts: tuple[dict[str, Any], ...]) -> None:
    for index, (step, artifact) in enumerate(zip(REPLAY_STEPS, artifacts, strict=True)):
        _verify_artifact_hash(artifact, step)
        wrapper = {
            "replay_index": index,
            "replay_step": step,
            "artifact": deepcopy(artifact),
        }
        wrapper["replay_hash"] = replay_hash(wrapper)
        write_json_immutable(replay_path / f"{index:03d}_{step}.json", wrapper)


def _capture(
    *,
    operator_request_id: str,
    final_status: str,
    failure_reason: str,
    operator_replay_path: Path,
    execution_replay_path: Path,
    request_artifact: dict[str, Any],
    result_artifact: dict[str, Any],
    execution_capture: dict[str, Any] | None,
) -> dict[str, Any]:
    capture = {
        "milestone_id": MILESTONE_ID,
        "operator_request_id": operator_request_id,
        "final_status": final_status,
        "failure_reason": _redact_failure_reason(failure_reason),
        "operator_dispatch_request_artifact": deepcopy(request_artifact),
        "operator_dispatch_result_artifact": deepcopy(result_artifact),
        "execution_capture": deepcopy(execution_capture),
        "operator_replay_reference": str(operator_replay_path),
        "execution_replay_reference": str(execution_replay_path),
        "credential_secret_replayed": False,
        "authorization_header_replayed": False,
        "worker_invoked": False,
        "provider_routing_performed": False,
        "fallback_performed": False,
        "automatic_retry_performed": False,
        "governance_modified": False,
        "replay_modified": False,
        "fail_closed": final_status == STATUS_FAILED_CLOSED,
        "replay_visible": True,
    }
    capture["runtime_hash"] = replay_hash(capture)
    return capture


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("first live provider operator entrypoint failed closed: replay artifact already exists")


def _replay_exists(replay_path: Path) -> bool:
    return any((replay_path / f"{index:03d}_{step}.json").exists() for index, step in enumerate(REPLAY_STEPS))


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError(f"{label} artifact hash is required")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError(f"{label} artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("first live provider operator entrypoint replay hash is required")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("first live provider operator entrypoint replay hash mismatch")


def _reject_forbidden_flags(artifact: dict[str, Any]) -> None:
    for key in (
        "credential_secret_replayed",
        "authorization_header_replayed",
        "worker_invoked",
        "governance_modified",
        "replay_modified",
        "worker_invocation_allowed",
        "provider_routing_allowed",
        "fallback_allowed",
        "automatic_retry_allowed",
        "tool_use_allowed",
        "governance_mutation_allowed",
        "replay_mutation_allowed",
    ):
        if artifact.get(key) is True:
            raise FailClosedRuntimeError(f"first live provider operator entrypoint failed closed: forbidden flag {key}")


def _assert_no_secret_material(artifact: dict[str, Any]) -> None:
    serialized = repr(artifact).lower()
    if "sk-" in serialized or "bearer " in serialized:
        raise FailClosedRuntimeError("first live provider operator entrypoint failed closed: credential secret replay detected")


def _redact_failure_reason(value: Any) -> str:
    reason = value if isinstance(value, str) else ""
    if "sk-" in reason.lower() or "bearer " in reason.lower():
        return "redacted credential-bearing failure"
    return reason


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"first live provider operator entrypoint failed closed: {field_name} is required")
    return value
