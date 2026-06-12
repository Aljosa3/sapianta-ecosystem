"""ACLI pilot validation for PROVIDER_CAPABILITY_CATALOG_V1."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from aigol.runtime.external_worker_adapter_runtime import (
    accept_external_worker_result_package,
    create_external_worker_task_package,
    reconstruct_external_worker_adapter_replay,
)
from aigol.runtime.governed_implementation_request_runtime import APPROVED, HUMAN_APPROVAL_ARTIFACT_V1
from aigol.runtime.openai_external_worker_provider_adapter import (
    reconstruct_openai_external_worker_provider_adapter_replay,
    run_openai_external_worker_provider_adapter,
)
from aigol.runtime.replay_certification_runtime import REPLAY_CERTIFICATION_COMPLETED, certify_validated_replay
from aigol.runtime.repository_mutation_worker_runtime import (
    REPOSITORY_MUTATION_COMPLETED,
    apply_repository_mutation,
    create_patch_proposal_artifact,
    reconstruct_repository_mutation_replay,
)
from aigol.runtime.result_validation_runtime import RESULT_VALIDATION_COMPLETED, validate_governed_execution_result
from aigol.runtime.transport.serialization import load_json, replay_hash
from aigol.runtime.validation_command_runner_runtime import (
    VALIDATION_COMMAND_COMPLETED,
    create_validation_command_request,
    execute_validation_command,
    reconstruct_validation_command_replay,
)


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "docs/governance/PROVIDER_CAPABILITY_CATALOG_V1.json"
REPORT = ROOT / ".github/governance/review/ACLI_PRODUCTION_PILOT_REPORT_V1.json"
CREATED_AT = "2026-06-12T00:00:00Z"
REQUIRED_PROVIDER_FIELDS = {
    "provider_name",
    "provider_type",
    "worker_capable",
    "cognition_capable",
    "function_calling_support",
    "replay_compatible",
    "certification_status",
    "notes",
}


def _load_execution_candidate_helper():
    helper_path = Path(__file__).with_name("test_governed_worker_execution_runtime_v1.py")
    spec = importlib.util.spec_from_file_location("governed_worker_execution_helper", helper_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("governed worker execution helper could not be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module._execution_candidate


_execution_candidate = _load_execution_candidate_helper()


def _task_approval(execution_candidate: dict) -> dict:
    artifact = {
        "artifact_type": HUMAN_APPROVAL_ARTIFACT_V1,
        "approval_id": "HUMAN-APPROVAL-ACLI-PROVIDER-CATALOG-000001",
        "approval_status": APPROVED,
        "approval_granted": True,
        "source_execution_candidate": execution_candidate["execution_candidate_id"],
        "source_execution_candidate_hash": execution_candidate["artifact_hash"],
        "approval_scope": "CREATE_EXTERNAL_WORKER_TASK_PACKAGE_ONLY",
        "external_worker_task_allowed": True,
        "implementation_result_creation_allowed": False,
        "approved_by": "HUMAN_OPERATOR",
        "approved_at": CREATED_AT,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capability() -> dict:
    return {
        "worker_interface": "OPENAI_EXTERNAL_WORKER_PROVIDER_ADAPTER_V1",
        "worker_family": "REAL_PROVIDER_EXTERNAL_LLM_WORKER",
        "capabilities": [
            "EXECUTE_EXTERNAL_WORKER_TASK_PACKAGE_V1",
            "RETURN_EXTERNAL_WORKER_RESULT_PACKAGE_V1",
        ],
        "provider_neutral_contract": True,
    }


def _openai_client():
    text = (
        "Proposal only: create a bounded provider capability catalog with OpenAI, Claude, and Mistral."
    )

    def call(request_metadata):
        assert request_metadata["provider_identity"] == "OPENAI"
        assert request_metadata["tool_use"] is False
        assert request_metadata["function_calling"] is False
        assert request_metadata["streaming"] is False
        assert request_metadata["automatic_retries"] is False
        return {"id": "acli-provider-capability-catalog-response-001", "output_text": text}

    return call


def test_provider_capability_catalog_json_parses_and_contains_required_providers() -> None:
    catalog = load_json(CATALOG)
    providers = catalog["providers"]
    names = {provider["provider_name"] for provider in providers}

    assert catalog["artifact_type"] == "PROVIDER_CAPABILITY_CATALOG_V1"
    assert catalog["catalog_id"] == "AIGOL_PROVIDER_CAPABILITY_CATALOG_V1"
    assert isinstance(providers, list)
    assert {"OpenAI", "Claude", "Mistral"}.issubset(names)
    for provider in providers:
        assert REQUIRED_PROVIDER_FIELDS.issubset(provider)
        assert isinstance(provider["provider_name"], str) and provider["provider_name"]
        assert isinstance(provider["provider_type"], str) and provider["provider_type"]
        assert isinstance(provider["worker_capable"], bool)
        assert isinstance(provider["cognition_capable"], bool)
        assert isinstance(provider["function_calling_support"], bool)
        assert isinstance(provider["replay_compatible"], bool)
        assert isinstance(provider["certification_status"], str) and provider["certification_status"]
        assert isinstance(provider["notes"], str) and provider["notes"]

    by_name = {provider["provider_name"]: provider for provider in providers}
    assert by_name["OpenAI"]["worker_capable"] is True
    assert by_name["OpenAI"]["replay_compatible"] is True
    assert by_name["Claude"]["worker_capable"] is False
    assert by_name["Mistral"]["worker_capable"] is False


def test_acli_pilot_routes_catalog_task_through_existing_openai_worker_lifecycle(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    catalog_content = CATALOG.read_text(encoding="utf-8")
    target_path = "docs/governance/PROVIDER_CAPABILITY_CATALOG_V1.json"
    execution_candidate = _execution_candidate(tmp_path)
    task_capture = create_external_worker_task_package(
        task_id="ACLI-PROVIDER-CAPABILITY-CATALOG-TASK-000001",
        execution_candidate_artifact=execution_candidate,
        human_approval_artifact=_task_approval(execution_candidate),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "acli_provider_catalog_external_adapter",
        worker_capability_declaration=_capability(),
    )
    openai_worker = run_openai_external_worker_provider_adapter(
        result_id="ACLI-PROVIDER-CAPABILITY-CATALOG-RESULT-PACKAGE-000001",
        task_package_artifact=task_capture["external_worker_task_package"],
        completed_at=CREATED_AT,
        replay_dir=tmp_path / "acli_provider_catalog_openai_worker",
        openai_client=_openai_client(),
        api_key="test-openai-key",
    )
    adapter_capture = accept_external_worker_result_package(
        result_package=openai_worker["external_worker_result_package"],
        task_package_artifact=task_capture["external_worker_task_package"],
        accepted_by="HUMAN_OPERATOR",
        accepted_at=CREATED_AT,
        replay_dir=tmp_path / "acli_provider_catalog_external_adapter",
    )
    worker_result = adapter_capture["worker_execution_result_artifact"]
    proposal = create_patch_proposal_artifact(
        proposal_id="PATCH-PROPOSAL-ACLI-PROVIDER-CAPABILITY-CATALOG-000001",
        file_mutations=[
            {
                "target_path": target_path,
                "operation": "CREATE_OR_REPLACE",
                "new_content": catalog_content,
                "new_content_hash": replay_hash(catalog_content),
                "approved": True,
            }
        ],
        replay_references=[
            openai_worker["openai_external_worker_replay_reference"],
            adapter_capture["external_worker_replay_reference"],
            worker_result["worker_execution_id"],
        ],
        replay_hashes=[
            openai_worker["external_worker_result_package"]["artifact_hash"],
            worker_result["artifact_hash"],
        ],
        authorization_references=["HUMAN-AUTHORIZATION-ACLI-PROVIDER-CATALOG-PATCH-000001"],
        created_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
    )
    mutation_capture = apply_repository_mutation(
        mutation_id="REPOSITORY-MUTATION-ACLI-PROVIDER-CAPABILITY-CATALOG-000001",
        source_artifact=proposal,
        target_root=repo,
        mutated_by="AIGOL_REPOSITORY_MUTATION_WORKER",
        mutated_at=CREATED_AT,
        replay_dir=tmp_path / "acli_provider_catalog_mutation",
    )
    validation_request = create_validation_command_request(
        request_id="VALIDATION-COMMAND-ACLI-PROVIDER-CAPABILITY-CATALOG-000001",
        command=["python", "-m", "json.tool", str(repo / target_path)],
        cwd=str(repo),
        requested_by="HUMAN_OPERATOR",
        requested_at=CREATED_AT,
        replay_references=[mutation_capture["repository_mutation_replay_reference"]],
        replay_hashes=[mutation_capture["repository_mutation_artifact"]["artifact_hash"]],
        timeout_seconds=30,
    )
    validation_command = execute_validation_command(
        request_artifact=validation_request,
        executed_by="AIGOL_VALIDATION_COMMAND_RUNNER",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "acli_provider_catalog_validation_command",
    )
    result_validation = validate_governed_execution_result(
        validation_id="RESULT-VALIDATION-ACLI-PROVIDER-CAPABILITY-CATALOG-000001",
        worker_execution_result_artifact=worker_result,
        validated_by="HUMAN_OPERATOR",
        validated_at=CREATED_AT,
        replay_dir=tmp_path / "acli_provider_catalog_result_validation",
    )
    replay_certification = certify_validated_replay(
        certification_id="REPLAY-CERTIFICATION-ACLI-PROVIDER-CAPABILITY-CATALOG-000001",
        result_validation_artifact=result_validation["result_validation_artifact"],
        certified_by="HUMAN_OPERATOR",
        certified_at=CREATED_AT,
        replay_dir=tmp_path / "acli_provider_catalog_replay_certification",
    )
    openai_replay = reconstruct_openai_external_worker_provider_adapter_replay(
        tmp_path / "acli_provider_catalog_openai_worker"
    )
    external_replay = reconstruct_external_worker_adapter_replay(tmp_path / "acli_provider_catalog_external_adapter")
    mutation_replay = reconstruct_repository_mutation_replay(tmp_path / "acli_provider_catalog_mutation")
    validation_replay = reconstruct_validation_command_replay(tmp_path / "acli_provider_catalog_validation_command")

    assert task_capture["task_package_generated"] is True
    assert openai_worker["openai_provider_connected"] is True
    assert openai_worker["task_package_consumed"] is True
    assert openai_worker["result_package_generated"] is True
    assert adapter_capture["result_package_accepted"] is True
    assert mutation_capture["mutation_status"] == REPOSITORY_MUTATION_COMPLETED
    assert load_json(repo / target_path)["catalog_id"] == "AIGOL_PROVIDER_CAPABILITY_CATALOG_V1"
    assert validation_command["command_status"] == VALIDATION_COMMAND_COMPLETED
    assert validation_command["validation_command_result_artifact"]["exit_code"] == 0
    assert result_validation["validation_status"] == RESULT_VALIDATION_COMPLETED
    assert replay_certification["certification_status"] == REPLAY_CERTIFICATION_COMPLETED
    assert openai_replay["replay_lineage_preserved"] is True
    assert external_replay["replay_lineage_preserved"] is True
    assert mutation_replay["replay_lineage_preserved"] is True
    assert validation_replay["replay_lineage_preserved"] is True


def test_acli_pilot_report_records_final_outputs() -> None:
    report = load_json(REPORT)
    outputs = report["final_outputs"]
    measurement = report["measurement"]

    assert report["artifact_type"] == "ACLI_PRODUCTION_PILOT_REPORT_V1"
    assert outputs["ACLI_PILOT_COMPLETED"] == "YES"
    assert outputs["OPENAI_WORKER_USED"] == "YES"
    assert outputs["REPOSITORY_MUTATION_USED"] == "YES"
    assert outputs["VALIDATION_USED"] == "YES"
    assert outputs["REPLAY_CERTIFICATION_USED"] == "YES"
    assert outputs["OPERATOR_ACTIONS"] == 5
    assert outputs["COPY_PASTE_ACTIONS"] == 0
    assert outputs["READY_FOR_LARGER_ACLI_MILESTONE"] == "YES_SUPERVISED_NON_CRITICAL_TASKS"
    assert measurement["validation_success"] is True
    assert measurement["replay_preservation"] is True
