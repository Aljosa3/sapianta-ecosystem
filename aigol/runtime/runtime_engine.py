"""Mock-first bounded AiGOL runtime engine foundation."""

from __future__ import annotations

from copy import deepcopy

from .models import (
    FailClosedRuntimeError,
    GovernedReturnArtifact,
    ProviderResponse,
    RuntimePackage,
    boundary_guarantees,
    replay_hash,
)
from .provider_interface import ProviderInterface
from .sandbox import SandboxContext, SandboxExecutor, SandboxValidator
from .transport.runtime_store import RuntimeStore
from .worker_lifecycle import CLOSED, DISPATCHED, PREPARED, RETURNED, RUNNING, WorkerLifecycle


class RuntimeEngine:
    """Coordinates bounded mock execution after governance-visible dispatch."""

    def __init__(
        self,
        providers: dict[str, ProviderInterface] | None = None,
        runtime_store: RuntimeStore | None = None,
    ) -> None:
        self.providers = dict(providers or {})
        self.runtime_store = runtime_store

    def register_provider(self, provider: ProviderInterface) -> None:
        self.providers[provider.provider_name()] = provider

    def dispatch(self, runtime_package: RuntimePackage) -> GovernedReturnArtifact:
        lifecycle = WorkerLifecycle(worker_id=runtime_package.worker_id)
        try:
            runtime_package.validate()
            provider = self.providers.get(runtime_package.provider)
            if provider is None:
                raise FailClosedRuntimeError("provider must be registered explicitly")
            lifecycle.transition_to(PREPARED)
            lifecycle.transition_to(DISPATCHED)
            dispatch_artifact = self._dispatch_artifact(runtime_package, lifecycle)
            if self.runtime_store is not None:
                self.runtime_store.persist_dispatch(runtime_package, dispatch_artifact)
            lifecycle.transition_to(RUNNING)
            if self._requires_sandbox(runtime_package):
                response = self._execute_sandbox(runtime_package)
            elif hasattr(provider, "execute_governed"):
                response = provider.execute_governed(
                    runtime_package,
                    runtime_store=self.runtime_store,
                    registered_providers=set(self.providers),
                )
            else:
                response = provider.execute(runtime_package)
            if not isinstance(response, ProviderResponse):
                raise FailClosedRuntimeError("provider must return ProviderResponse")
            if response.provider != provider.provider_name():
                raise FailClosedRuntimeError("provider response identity mismatch")
            lifecycle.transition_to(RETURNED)
            lifecycle.transition_to(CLOSED)
            return_artifact = self._return_artifact(runtime_package, lifecycle, response, dispatch_artifact, "RETURNED")
            if self.runtime_store is not None:
                self.runtime_store.persist_lifecycle_transitions(runtime_package.runtime_id, lifecycle.transitions)
                self.runtime_store.persist_result(runtime_package, return_artifact)
            return return_artifact
        except FailClosedRuntimeError as exc:
            dispatch_artifact = self._dispatch_artifact(runtime_package, lifecycle, fail_closed_reason=str(exc))
            return self._return_artifact(runtime_package, lifecycle, None, dispatch_artifact, "FAIL_CLOSED")

    def _requires_sandbox(self, runtime_package: RuntimePackage) -> bool:
        return isinstance(runtime_package.payload, dict) and bool(runtime_package.payload.get("requires_sandbox"))

    def _execute_sandbox(self, runtime_package: RuntimePackage) -> ProviderResponse:
        context = SandboxContext.from_runtime_package(runtime_package)
        validator = SandboxValidator()
        validation = validator.validate(context)
        if self.runtime_store is not None:
            self.runtime_store.persist_sandbox_context(runtime_package.runtime_id, context.to_dict())
            self.runtime_store.persist_sandbox_validation(runtime_package.runtime_id, validation)
        result = SandboxExecutor(validator=validator).execute(context, runtime_package.payload)
        result_dict = result.to_dict()
        if self.runtime_store is not None:
            self.runtime_store.persist_sandbox_result(runtime_package.runtime_id, result_dict)
        return ProviderResponse(
            provider=runtime_package.provider,
            status="SANDBOX_RETURNED",
            output=result_dict,
            metadata={
                "sandbox_id": context.sandbox_id,
                "sandbox_replay_hash": result_dict["replay_hash"],
                "shell_execution": False,
                "subprocess_execution": False,
                "filesystem_write": False,
                "unrestricted_network": False,
                "worker_spawn": False,
            },
        )

    def _dispatch_artifact(
        self,
        runtime_package: RuntimePackage,
        lifecycle: WorkerLifecycle,
        fail_closed_reason: str = "",
    ) -> dict:
        artifact = {
            "artifact_type": "RUNTIME_ENGINE_FOUNDATION_DISPATCH",
            "runtime_id": runtime_package.runtime_id,
            "package_id": runtime_package.package_id,
            "worker_id": runtime_package.worker_id,
            "provider": runtime_package.provider,
            "lifecycle_state": lifecycle.state,
            "lineage_refs": deepcopy(runtime_package.lineage_refs),
            "governance_state": runtime_package.governance_state,
            "fail_closed": bool(fail_closed_reason),
            "fail_closed_reason": fail_closed_reason,
            "boundary_guarantees": boundary_guarantees(),
        }
        artifact["dispatch_replay_hash"] = replay_hash(artifact)
        return artifact

    def _return_artifact(
        self,
        runtime_package: RuntimePackage,
        lifecycle: WorkerLifecycle,
        provider_response: ProviderResponse | None,
        dispatch_artifact: dict,
        status: str,
    ) -> GovernedReturnArtifact:
        artifact = GovernedReturnArtifact(
            runtime_id=runtime_package.runtime_id,
            package_id=runtime_package.package_id,
            worker_id=runtime_package.worker_id,
            provider=runtime_package.provider,
            lifecycle_state=lifecycle.state,
            status=status,
            provider_response=provider_response,
            lineage_refs=deepcopy(runtime_package.lineage_refs),
            lifecycle_transitions=deepcopy(lifecycle.transitions),
            runtime_dispatch_artifact=deepcopy(dispatch_artifact),
            boundary_guarantees=boundary_guarantees(),
        )
        replay_input = artifact.to_dict()
        replay_input.pop("replay_hash", None)
        return GovernedReturnArtifact(
            runtime_id=artifact.runtime_id,
            package_id=artifact.package_id,
            worker_id=artifact.worker_id,
            provider=artifact.provider,
            lifecycle_state=artifact.lifecycle_state,
            status=artifact.status,
            provider_response=artifact.provider_response,
            lineage_refs=artifact.lineage_refs,
            lifecycle_transitions=artifact.lifecycle_transitions,
            runtime_dispatch_artifact=artifact.runtime_dispatch_artifact,
            boundary_guarantees=artifact.boundary_guarantees,
            replay_hash=replay_hash(replay_input),
        )
