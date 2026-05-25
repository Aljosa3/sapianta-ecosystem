"""Mock-first bounded AiGOL runtime engine foundation."""

from __future__ import annotations

from copy import deepcopy

from .capabilities import CapabilityExecutor, CapabilityRequest, CapabilityValidator
from .continuity import ContinuationContract, RuntimeContinuityEngine
from .goals import GoalContract, GoalContinuityEngine, GoalSequence
from .models import (
    FailClosedRuntimeError,
    GovernedReturnArtifact,
    ProviderResponse,
    RuntimePackage,
    boundary_guarantees,
    replay_hash,
)
from .observability import RuntimeSnapshot
from .policy import PolicyContract, RuntimePolicyEngine
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
            if self._requires_goal_sequence(runtime_package):
                response = self._evaluate_goal_sequence(runtime_package)
            elif self._requires_capability(runtime_package):
                response = self._execute_capability(runtime_package)
            elif self._requires_sandbox(runtime_package):
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
                self._evaluate_continuity(runtime_package, return_artifact)
                self._persist_runtime_snapshot(runtime_package.runtime_id)
            return return_artifact
        except FailClosedRuntimeError as exc:
            dispatch_artifact = self._dispatch_artifact(runtime_package, lifecycle, fail_closed_reason=str(exc))
            return self._return_artifact(runtime_package, lifecycle, None, dispatch_artifact, "FAIL_CLOSED")

    def _requires_sandbox(self, runtime_package: RuntimePackage) -> bool:
        return isinstance(runtime_package.payload, dict) and bool(runtime_package.payload.get("requires_sandbox"))

    def _requires_capability(self, runtime_package: RuntimePackage) -> bool:
        return isinstance(runtime_package.payload, dict) and isinstance(runtime_package.payload.get("capability_request"), dict)

    def _requires_goal_sequence(self, runtime_package: RuntimePackage) -> bool:
        return isinstance(runtime_package.payload, dict) and isinstance(runtime_package.payload.get("goal_sequence"), dict)

    def _evaluate_goal_sequence(self, runtime_package: RuntimePackage) -> ProviderResponse:
        contract = GoalContract.from_runtime_package(runtime_package)
        sequence = GoalSequence.from_runtime_package(runtime_package, contract)
        result, validation = GoalContinuityEngine().evaluate(contract, sequence)
        if self.runtime_store is not None:
            self.runtime_store.persist_goal_contract(runtime_package.runtime_id, contract.to_dict())
            self.runtime_store.persist_goal_sequence(runtime_package.runtime_id, sequence.to_dict())
            self.runtime_store.persist_goal_validation(runtime_package.runtime_id, validation)
            self.runtime_store.persist_goal_result(runtime_package.runtime_id, result)
        return ProviderResponse(
            provider=runtime_package.provider,
            status="GOAL_CONTINUITY_EVALUATED",
            output=result,
            metadata={
                "goal_id": contract.goal_id,
                "goal_replay_hash": result["replay_hash"],
                "sequencing_only": True,
                "orchestration": False,
                "recursive_execution": False,
                "hidden_continuation": False,
            },
        )

    def _execute_capability(self, runtime_package: RuntimePackage) -> ProviderResponse:
        context = SandboxContext.from_runtime_package(runtime_package)
        sandbox_validator = SandboxValidator()
        sandbox_validation = sandbox_validator.validate(context)
        request = CapabilityRequest.from_runtime_package(runtime_package, context.sandbox_id)
        capability_validator = CapabilityValidator()
        capability_validation = capability_validator.validate(request, context)
        policy_contract = PolicyContract.from_capability_request(request, context)
        policy_result, policy_validation = RuntimePolicyEngine().evaluate(policy_contract, sandbox_context=context)
        if policy_result.decision != "ALLOW":
            raise FailClosedRuntimeError(f"capability blocked by runtime policy: {policy_result.decision_reason}")
        if self.runtime_store is not None:
            self.runtime_store.persist_sandbox_context(runtime_package.runtime_id, context.to_dict())
            self.runtime_store.persist_sandbox_validation(runtime_package.runtime_id, sandbox_validation)
            self.runtime_store.persist_policy_contract(runtime_package.runtime_id, policy_contract.to_dict())
            self.runtime_store.persist_policy_validation(runtime_package.runtime_id, policy_validation)
            self.runtime_store.persist_policy_result(runtime_package.runtime_id, policy_result.to_dict())
            self.runtime_store.persist_capability_request(runtime_package.runtime_id, request.to_dict())
            self.runtime_store.persist_capability_validation(runtime_package.runtime_id, capability_validation)
        result = CapabilityExecutor(validator=capability_validator).execute(request, context)
        result_dict = result.to_dict()
        if self.runtime_store is not None:
            self.runtime_store.persist_capability_result(runtime_package.runtime_id, result_dict)
        return ProviderResponse(
            provider=runtime_package.provider,
            status="CAPABILITY_RETURNED",
            output=result_dict,
            metadata={
                "capability_request_id": request.capability_request_id,
                "capability_replay_hash": result_dict["replay_hash"],
                "shell_execution": False,
                "subprocess_execution": False,
                "filesystem_mutation": False,
                "unrestricted_network": False,
                "worker_spawn": False,
                "orchestration": False,
            },
        )

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

    def _evaluate_continuity(
        self,
        runtime_package: RuntimePackage,
        return_artifact: GovernedReturnArtifact,
    ) -> None:
        if self.runtime_store is None:
            return
        contract = ContinuationContract.from_runtime_return(runtime_package, return_artifact)
        result, validation, retry_evaluation = RuntimeContinuityEngine().evaluate(contract)
        self.runtime_store.persist_continuity_contract(runtime_package.runtime_id, contract.to_dict())
        self.runtime_store.persist_retry_evaluation(runtime_package.runtime_id, retry_evaluation)
        self.runtime_store.persist_continuity_result(runtime_package.runtime_id, result.to_dict())

    def _persist_runtime_snapshot(self, runtime_id: str) -> None:
        if self.runtime_store is None:
            return
        dispatch = self.runtime_store.load_dispatch(runtime_id)
        result = self.runtime_store.load_result(runtime_id)
        snapshot = RuntimeSnapshot.from_artifacts(runtime_id, dispatch, result, self.runtime_store)
        self.runtime_store.persist_runtime_snapshot(runtime_id, snapshot.to_dict())

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
