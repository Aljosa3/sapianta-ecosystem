from __future__ import annotations

from copy import deepcopy
import ast
import inspect
import json
from pathlib import Path

from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.provider.provider_registry import AVAILABLE, ProviderMetadata, ProviderRegistry
from aigol.provider.providers.openai_provider import OpenAIProviderAdapter
from aigol.runtime import conversation_interpreter_epp_assistance_runtime_v1 as adapter_v1
from aigol.runtime import platform_core_conversation_interpreter_proposal_runtime_v2 as proposal_v2
from aigol.runtime import platform_core_conversation_proposal_commit_runtime_v2 as commit_v2
from aigol.runtime import platform_core_conversation_working_memory_runtime_v2 as cwm_v2
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


WORKSPACE = "/workspace/sapianta"
SESSION = "G61-03-CENTRAL-LLM-ADAPTER"
CREATED = "2026-08-01T12:00:00Z"
OBSERVED = "2026-08-01T12:01:00Z"
PROVIDER_TIME = "2026-08-01T12:00:30Z"
INTERPRETER = "conversation-existing-epp-interpreter-v1"
PROVIDER_ID = "openai"
PROVIDER_VERSION = "openai-responses-v1"
MODEL = "gpt-test"


def _participants() -> list[dict]:
    return [
        {
            "participant_role": cwm_v2.HUMAN_ORIGINATOR,
            "asserted_identity": "local-human",
            "identity_source": cwm_v2.LOCAL_ASSERTION,
            "binding_disposition": cwm_v2.ASSERTED_NOT_AUTHENTICATED,
            "first_bound_revision": 0,
            "last_confirmed_revision": 0,
        }
    ]


def _state(tmp_path: Path) -> dict:
    return cwm_v2.create_conversation_working_memory_state_v2(
        runtime_root=tmp_path / "cwm",
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        created_at=CREATED,
        ttl_seconds=3600,
        participants=_participants(),
    )


def _profile(**overrides: str) -> dict:
    values = {
        "interpreter_identity": INTERPRETER,
        "interpreter_version": "1.0.0",
        "resource_id": "OPENAI",
        "provider_id": PROVIDER_ID,
        "provider_version": PROVIDER_VERSION,
        "model_id": MODEL,
    }
    values.update(overrides)
    return adapter_v1.create_conversation_interpreter_epp_selection_and_binding_profile_v1(**values)


def _provider_registry(*, version: str = PROVIDER_VERSION) -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register_provider(
        ProviderMetadata(
            provider_id=PROVIDER_ID,
            provider_type="llm",
            provider_version=version,
            provider_status=AVAILABLE,
            domain="governance",
            capability="proposal_generation",
        )
    )
    return registry


def _interpreter_registry() -> list[dict]:
    return [
        {
            "interpreter_identity": INTERPRETER,
            "interpreter_class": proposal_v2.EXTERNAL_LANGUAGE_MODEL,
            "interpreter_version": "1.0.0",
            "enabled": True,
        }
    ]


def _normalized_response(text: str = "implement adapter runtime") -> dict:
    value = "implement"
    start = text.index(value)
    return {
        "response_schema_version": adapter_v1.CONVERSATION_INTERPRETER_EPP_RESPONSE_V1,
        "operations": [
            {
                "operation_type": proposal_v2.PROPOSE_SLOT_CREATION,
                "slot_class": cwm_v2.OPERATIVE_ACTION,
                "slot_role": cwm_v2.PRIMARY,
                "cardinality_key": cwm_v2.PRIMARY,
                "surface_value": value,
                "canonical_value": value,
                "source_spans": [
                    {"start_offset": start, "end_offset": start + len(value)}
                ],
                "target_slot_id": None,
                "depends_on_slot_ids": [],
                "evidence_reference_keys": ["turn"],
                "clarification_reason": None,
            }
        ],
        "evidence_references": [
            {
                "reference_key": "turn",
                "reference_kind": "SOURCE_TURN",
                "reference_digest": cwm_v2._checksum(text),
                "verification_status": "SOURCE_BOUND",
            }
        ],
        "advisory_confidence": {
            "scale_id": "PROVIDER_REPORTED_V1",
            "reported_value": "HIGH",
            "limitations": ["NON_AUTHORITATIVE"],
            "authority_effect": False,
        },
        "ambiguity_operation_indexes": [],
        "conflict_operation_indexes": [],
    }


class FakeExistingProviderAdapter:
    provider_id = PROVIDER_ID
    provider_version = PROVIDER_VERSION
    model = MODEL

    def __init__(self, response: dict | None = None) -> None:
        self.response = response or _normalized_response()
        self.calls: list[dict] = []

    def generate_proposal(self, request, *, proposal_id: str, timestamp: str):
        self.calls.append(deepcopy(request))
        return create_provider_proposal_envelope(
            proposal_id=proposal_id,
            provider_id=self.provider_id,
            provider_version=self.provider_version,
            request=request,
            response={
                "provider": self.provider_id,
                "provider_version": self.provider_version,
                "model": self.model,
                "response_text": json.dumps(self.response, sort_keys=True),
                "raw_response_hash": replay_hash(self.response),
            },
            timestamp=timestamp,
        )


class TimeoutExistingProviderAdapter(FakeExistingProviderAdapter):
    def generate_proposal(self, request, *, proposal_id: str, timestamp: str):
        self.calls.append(deepcopy(request))
        try:
            raise TimeoutError("existing provider timeout")
        except TimeoutError as exc:
            raise FailClosedRuntimeError("existing provider unavailable") from exc


def _invoke(tmp_path: Path, *, state: dict | None = None, provider=None, registry=None, profile=None) -> dict:
    return adapter_v1.run_conversation_interpreter_epp_assistance_v1(
        current_state=state or _state(tmp_path),
        source_turn_text="implement adapter runtime",
        observed_at=OBSERVED,
        binding_profile=profile or _profile(),
        interpreter_registry=_interpreter_registry(),
        provider_registry=registry or _provider_registry(),
        provider_adapter=provider or FakeExistingProviderAdapter(),
        selection_replay_dir=tmp_path / "selection",
    )


def test_existing_epp_response_normalizes_and_validates_without_authority(tmp_path: Path) -> None:
    provider = FakeExistingProviderAdapter()
    state = _state(tmp_path)
    original = deepcopy(state)

    result = _invoke(tmp_path, state=state, provider=provider)

    assert result["adapter_status"] == adapter_v1.NORMALIZED_AND_VALIDATED
    assert result["validation_result"]["validation_disposition"] == proposal_v2.ADMISSIBLE
    assert result["candidate_operation_set"] is not None
    assert len(provider.calls) == 1
    assert provider.calls[0]["request"]["request_type"] == adapter_v1.CONVERSATION_INTERPRETER_EPP_REQUEST_V1
    assert provider.calls[0]["request"]["model_id"] == MODEL
    assert result["selected_resource_id"] == "OPENAI"
    assert result["selected_provider_role"] == "PROVIDER_ROLE"
    assert result["provider_proposal_hash"].startswith("sha256:")
    assert result["integrity_binding"].startswith("sha256:")
    assert result["result_hash"].startswith("sha256:")
    assert state == original
    replay_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((tmp_path / "selection").glob("*.json"))
    )
    assert "implement adapter runtime" not in replay_text
    assert "response_text" not in replay_text
    assert "proposed_semantic_operations" not in replay_text
    for flag in (
        "semantic_cwm_mutated",
        "proposal_commit_performed",
        "objective_created",
        "platform_core_invoked",
        "authorization_created",
        "worker_invoked",
        "execution_invoked",
        "provider_content_replay_written",
    ):
        assert result[flag] is False


def test_validated_candidate_remains_compatible_with_separate_g59_commit(tmp_path: Path) -> None:
    state = _state(tmp_path)
    result = _invoke(tmp_path, state=state)

    committed = commit_v2.commit_proposal_candidate_operations_v2(
        runtime_root=tmp_path / "cwm",
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        candidate_operation_set=result["candidate_operation_set"],
        expected_revision=0,
        committed_at=OBSERVED,
    )

    assert result["proposal_commit_performed"] is False
    assert committed["disposition"] == commit_v2.COMMITTED
    assert committed["semantic_cwm_mutated"] is True
    assert committed["objective_created"] is False
    assert committed["execution_invoked"] is False


def test_existing_openai_adapter_composition_is_reused_without_network(tmp_path: Path) -> None:
    response = _normalized_response()
    calls: list[dict] = []

    def client(payload, *, api_key: str, endpoint: str, timeout_seconds: int):
        calls.append(
            {
                "payload": deepcopy(payload),
                "api_key": api_key,
                "endpoint": endpoint,
                "timeout_seconds": timeout_seconds,
            }
        )
        return {"output_text": json.dumps(response, sort_keys=True)}

    provider = OpenAIProviderAdapter(
        api_key="test-secret",
        model=MODEL,
        timeout_seconds=20,
        client=client,
    )
    profile = adapter_v1.create_conversation_interpreter_epp_selection_and_binding_profile_v1(
        interpreter_identity=INTERPRETER,
        interpreter_version="1.0.0",
        resource_id="OPENAI",
        provider_id=PROVIDER_ID,
        provider_version=PROVIDER_VERSION,
        model_id=MODEL,
        timeout_seconds=20,
    )

    result = _invoke(tmp_path, provider=provider, profile=profile)

    assert result["adapter_status"] == adapter_v1.NORMALIZED_AND_VALIDATED
    assert result["validation_result"]["validation_disposition"] == proposal_v2.ADMISSIBLE
    assert len(calls) == 1
    assert calls[0]["payload"]["stream"] is False
    assert calls[0]["timeout_seconds"] == 20
    assert "test-secret" not in json.dumps(result, sort_keys=True)


def test_identical_inputs_produce_identical_semantic_and_integrity_bindings(tmp_path: Path) -> None:
    first = _invoke(tmp_path / "first")
    second = _invoke(tmp_path / "second")

    assert first["request_integrity"] == second["request_integrity"]
    assert first["normalized_proposal"] == second["normalized_proposal"]
    assert first["candidate_operation_set"] == second["candidate_operation_set"]
    assert first["provider_proposal_hash"] == second["provider_proposal_hash"]
    assert first["integrity_binding"] == second["integrity_binding"]


def test_timeout_propagates_as_fail_closed_without_retry_or_candidate(tmp_path: Path) -> None:
    provider = TimeoutExistingProviderAdapter()

    result = _invoke(tmp_path, provider=provider)

    assert result["adapter_status"] == adapter_v1.FAILED_CLOSED
    assert result["failure_code"] == "PROVIDER_TIMEOUT"
    assert result["candidate_operation_set"] is None
    assert result["provider_invoked"] is True
    assert len(provider.calls) == 1
    assert result["execution_invoked"] is False


def test_registry_mismatch_fails_before_selection_and_provider_invocation(tmp_path: Path) -> None:
    provider = FakeExistingProviderAdapter()

    result = _invoke(
        tmp_path,
        provider=provider,
        registry=_provider_registry(version="wrong-provider-version"),
    )

    assert result["adapter_status"] == adapter_v1.FAILED_CLOSED
    assert result["failure_code"] == "ADAPTER_INPUT_REJECTED"
    assert result["candidate_operation_set"] is None
    assert result["provider_invoked"] is False
    assert provider.calls == []
    assert not (tmp_path / "selection").exists()


def test_malformed_or_authority_shaped_response_is_rejected_before_validation(tmp_path: Path) -> None:
    response = _normalized_response()
    response["objective"] = {"execute": True}
    provider = FakeExistingProviderAdapter(response)

    result = _invoke(tmp_path, provider=provider)

    assert result["adapter_status"] == adapter_v1.FAILED_CLOSED
    assert result["failure_code"] == "PROVIDER_RESPONSE_REJECTED"
    assert result["normalized_proposal"] is None
    assert result["candidate_operation_set"] is None
    assert result["execution_invoked"] is False


def test_adapter_has_no_provider_specific_or_execution_owner_imports() -> None:
    source = inspect.getsource(adapter_v1)
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imports.update(
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    )

    assert not any("openai_provider" in item or "anthropic" in item for item in imports)
    assert not any(
        token in item
        for item in imports
        for token in (
            "authorization",
            "worker",
            "platform_core_objective_commitment",
            "platform_core_execution",
            "development_governance",
        )
    )
    assert "ProviderAdapter" in source
    assert "ProviderRegistry" in source
    assert "select_unified_resource" in source
