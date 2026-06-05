"""First real provider-proposed implementation generation epoch."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.provider.provider_registry import AVAILABLE, ProviderMetadata, ProviderRegistry
from aigol.provider.provider_runtime import (
    PROVIDER_PROPOSAL_RETURNED,
    run_provider_attachment,
)
from aigol.runtime.filesystem_mutation_authorization_runtime import (
    AUTHORIZATION_DECISION,
    AUTHORIZATION_SCOPE,
    AUTHORIZATION_STATEMENT,
    authorize_filesystem_mutation,
)
from aigol.runtime.filesystem_mutation_runtime import apply_filesystem_mutation
from aigol.runtime.generated_content_acceptance_runtime import (
    ACCEPTANCE_DECISION,
    ACCEPTANCE_SCOPE,
    ACCEPTANCE_STATEMENT,
    accept_generated_content,
)
from aigol.runtime.generated_content_validation_runtime import validate_generated_content
from aigol.runtime.generated_test_validation_runtime import validate_generated_tests
from aigol.runtime.implementation_certification_runtime import certify_implementation
from aigol.runtime.implementation_manifest_runtime import CREATE_ONLY, create_implementation_manifest
from aigol.runtime.implementation_summary_runtime import create_implementation_summary
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash, write_json_immutable


AIGOL_FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH_VERSION = (
    "AIGOL_FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH_V1"
)
AIGOL_FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH_STATUS = "CERTIFIED"
COMMAND = "aigol implementation real-epoch"
REAL_PROVIDER_ID = "AIGOL_REAL_IMPLEMENTATION_PROVIDER"
REAL_PROVIDER_VERSION = "1.0.0"
APPROVE = "APPROVE"
REJECT = "REJECT"
ABORT = "ABORT"
ALLOWED_OPERATOR_DECISIONS = frozenset({APPROVE, REJECT, ABORT})


class _GateStop(Exception):
    def __init__(self, status: str, fail_closed: bool, reason: str) -> None:
        super().__init__(reason)
        self.status = status
        self.fail_closed = fail_closed
        self.reason = reason


class LocalRealImplementationProviderAdapter:
    """Bounded provider adapter that proposes implementation content only."""

    provider_id = REAL_PROVIDER_ID
    provider_version = REAL_PROVIDER_VERSION

    def generate_proposal(self, request: Any, *, proposal_id: str, timestamp: str) -> Any:
        if not isinstance(request, dict):
            raise FailClosedRuntimeError("real implementation provider request must be an object")
        human_request = _require_string(request.get("human_request"), "human_request")
        response = _provider_response(human_request)
        return create_provider_proposal_envelope(
            proposal_id=proposal_id,
            provider_id=self.provider_id,
            provider_version=self.provider_version,
            request=deepcopy(request),
            response=response,
            timestamp=timestamp,
        )


def run_first_real_implementation_generation_epoch(
    *,
    human_request: str,
    runtime_root: str | Path,
    workspace: str | Path,
    created_at: str,
    actor_id: str = "human.operator",
    provider_adapter: Any | None = None,
    operator_decision: str | None = None,
    decision_reason: str | None = None,
    operator_decision_callback: Any | None = None,
) -> dict[str, Any]:
    """Run a provider-proposed implementation through the certified lifecycle."""

    runtime_path = Path(runtime_root)
    workspace_path = Path(workspace)
    epoch_id = "AIGOL-FIRST-REAL-IMPLEMENTATION-GENERATION-EPOCH-000001"
    chain_id = "CHAIN-FIRST-REAL-IMPLEMENTATION-GENERATION-EPOCH-000001"
    bundle_id = "FIRST_REAL_IMPLEMENTATION_GENERATION_BUNDLE_V1"
    request_text = _require_string(human_request, "human_request")
    adapter = provider_adapter or LocalRealImplementationProviderAdapter()

    try:
        ocs = _ocs_request_preparation(
            epoch_id=epoch_id,
            chain_id=chain_id,
            human_request=request_text,
            created_at=created_at,
        )
        _persist(runtime_path / "000_ocs_semantic_request_preparation.json", ocs)
        provider_capture = _invoke_provider(
            request=ocs["provider_request"],
            adapter=adapter,
            created_at=created_at,
            replay_dir=runtime_path / "real_provider_proposal",
        )
        _require_stage_status(provider_capture["provider_proposal_returned"], "event_type", PROVIDER_PROPOSAL_RETURNED)
        _persist(runtime_path / "001_real_provider_proposal_envelope.json", provider_capture["provider_proposal_envelope"])
        candidate = _candidate_from_provider(
            epoch_id=epoch_id,
            chain_id=chain_id,
            bundle_id=bundle_id,
            ocs=ocs,
            provider_capture=provider_capture,
            created_at=created_at,
        )
        _persist(runtime_path / "002_provider_generated_implementation_candidate.json", candidate)
        manifest = create_implementation_manifest(
            manifest_id="IMPLEMENTATION-MANIFEST-FIRST-REAL-EPOCH-000001",
            canonical_chain_id=chain_id,
            implementation_bundle_id=bundle_id,
            source_candidate_reference=candidate["candidate_id"],
            source_candidate_hash=candidate["candidate_hash"],
            implementation_handoff_reference=candidate["implementation_handoff_reference"],
            implementation_handoff_hash=candidate["implementation_handoff_hash"],
            provider_generation_authorization_reference=candidate["provider_generation_authorization_reference"],
            provider_generation_authorization_hash=candidate["provider_generation_authorization_hash"],
            provider_response_reference=candidate["provider_response_reference"],
            provider_response_hash=candidate["provider_response_hash"],
            target_domain="GOVERNANCE",
            target_resource="RUNTIME",
            target_worker="FIRST_REAL_EPOCH_PROVIDER_WORKER",
            generated_files=deepcopy(candidate["generated_files"]),
            generated_tests=deepcopy(candidate["generated_tests"]),
            validation_requirements=deepcopy(candidate["validation_requirements"]),
            known_gaps=deepcopy(candidate["known_gaps"]),
            created_at=created_at,
            replay_dir=runtime_path / "implementation_manifest",
        )["implementation_manifest_artifact"]
        _require_stage_status(manifest, "manifest_status", "IMPLEMENTATION_MANIFEST_CREATED")
        _persist(runtime_path / "003_implementation_manifest_artifact.json", manifest)
        content_validation = validate_generated_content(
            validation_id="GENERATED-CONTENT-VALIDATION-FIRST-REAL-EPOCH-000001",
            implementation_manifest_artifact=manifest,
            created_at=created_at,
        )["generated_content_validation_artifact"]
        _require_stage_status(content_validation, "validation_status", "GENERATED_CONTENT_VALIDATED")
        _persist(runtime_path / "004_generated_content_validation_artifact.json", content_validation)
        test_validation = validate_generated_tests(
            validation_id="GENERATED-TEST-VALIDATION-FIRST-REAL-EPOCH-000001",
            implementation_manifest_artifact=manifest,
            generated_test_bundle=manifest["test_entries"],
            created_at=created_at,
        )["generated_test_validation_artifact"]
        _require_stage_status(test_validation, "validation_status", "GENERATED_TEST_VALIDATED")
        _persist(runtime_path / "005_generated_test_validation_artifact.json", test_validation)
        summary = create_implementation_summary(
            summary_id="IMPLEMENTATION-SUMMARY-FIRST-REAL-EPOCH-000001",
            implementation_manifest_artifact=manifest,
            generated_content_validation_artifact=content_validation,
            generated_test_validation_artifact=test_validation,
            created_at=created_at,
        )["implementation_summary_artifact"]
        _require_stage_status(summary, "summary_status", "IMPLEMENTATION_SUMMARY_CREATED")
        _persist(runtime_path / "006_implementation_summary_artifact.json", summary)
        checkpoint = _operator_checkpoint(
            human_request=request_text,
            candidate=candidate,
            manifest=manifest,
            summary=summary,
            content_validation=content_validation,
            test_validation=test_validation,
        )
        decision = _operator_decision_artifact(
            checkpoint=checkpoint,
            actor_id=actor_id,
            decided_at=created_at,
            operator_decision=operator_decision,
            decision_reason=decision_reason,
            operator_decision_callback=operator_decision_callback,
        )
        _persist(runtime_path / "007_interactive_operator_decision_artifact.json", decision)
        _require_approval(decision)
        acceptance = accept_generated_content(
            acceptance_id="GENERATED-CONTENT-ACCEPTANCE-FIRST-REAL-EPOCH-000001",
            implementation_manifest_artifact=manifest,
            generated_content_validation_artifact=content_validation,
            generated_test_validation_artifact=test_validation,
            human_acceptance_evidence=_acceptance_evidence(decision),
            created_at=created_at,
        )["generated_content_acceptance_artifact"]
        _require_stage_status(acceptance, "acceptance_status", "GENERATED_CONTENT_ACCEPTED")
        _persist(runtime_path / "008_generated_content_acceptance_artifact.json", acceptance)
        authorization = authorize_filesystem_mutation(
            authorization_id="FILESYSTEM-MUTATION-AUTHORIZATION-FIRST-REAL-EPOCH-000001",
            implementation_manifest_artifact=manifest,
            generated_content_validation_artifact=content_validation,
            generated_test_validation_artifact=test_validation,
            generated_content_acceptance_artifact=acceptance,
            human_authorization_evidence=_authorization_evidence(actor_id=actor_id, created_at=created_at),
            created_at=created_at,
        )["filesystem_mutation_authorization_artifact"]
        _require_stage_status(authorization, "authorization_status", "FILESYSTEM_MUTATION_AUTHORIZED")
        _persist(runtime_path / "009_filesystem_mutation_authorization_artifact.json", authorization)
        mutation = apply_filesystem_mutation(
            mutation_id="FILESYSTEM-MUTATION-FIRST-REAL-EPOCH-000001",
            implementation_manifest_artifact=manifest,
            filesystem_mutation_authorization_artifact=authorization,
            target_root=workspace_path,
            created_at=created_at,
            target_root_reference="OPERATOR_SUPPLIED_WORKSPACE",
        )["filesystem_mutation_artifact"]
        _require_stage_status(mutation, "mutation_status", "FILESYSTEM_MUTATION_COMPLETED")
        _persist(runtime_path / "010_filesystem_mutation_artifact.json", mutation)
        certification = certify_implementation(
            certification_id="IMPLEMENTATION-CERTIFICATION-FIRST-REAL-EPOCH-000001",
            implementation_manifest_artifact=manifest,
            filesystem_mutation_authorization_artifact=authorization,
            generated_content_acceptance_artifact=acceptance,
            filesystem_mutation_artifact=mutation,
            created_at=created_at,
        )["implementation_certification_artifact"]
        _require_stage_status(certification, "certification_status", "IMPLEMENTATION_CERTIFIED")
        _persist(runtime_path / "011_implementation_certification_artifact.json", certification)
        replay_report = _replay_report(
            runtime_path=runtime_path,
            workspace_path=workspace_path,
            provider_capture=provider_capture,
            candidate=candidate,
            manifest=manifest,
            summary=summary,
            operator_decision=decision,
            certification=certification,
        )
        _persist(runtime_path / "012_replay_inspection_report.json", replay_report)
        status = "REAL_EPOCH_CERTIFIED"
        fail_closed = False
        failure_reason = None
    except _GateStop as exc:
        replay_report = _failed_replay_report(runtime_path=runtime_path, workspace_path=workspace_path, exc=exc)
        status = exc.status
        fail_closed = exc.fail_closed
        failure_reason = exc.reason
    except Exception as exc:
        replay_report = _failed_replay_report(runtime_path=runtime_path, workspace_path=workspace_path, exc=exc)
        status = "REAL_EPOCH_FAILED_CLOSED"
        fail_closed = True
        failure_reason = _failure_reason(exc)

    result = {
        "command": COMMAND,
        "milestone": AIGOL_FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH_VERSION,
        "epoch_status": status,
        "final_classification": (
            "AIGOL_FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH_STATUS = "
            f"{AIGOL_FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH_STATUS}"
        ),
        "human_request": request_text,
        "runtime_root": str(runtime_path),
        "workspace": str(workspace_path),
        "replay_files": _replay_files(runtime_path),
        "workspace_files": _workspace_files(workspace_path),
        "replay_report": replay_report,
        "fail_closed": fail_closed,
        "failure_reason": failure_reason,
    }
    result["epoch_hash"] = replay_hash(result)
    return result


def render_first_real_implementation_generation_epoch(result: dict[str, Any]) -> str:
    lines = [
        "AIGOL FIRST REAL IMPLEMENTATION GENERATION EPOCH",
        f"milestone: {result.get('milestone')}",
        f"epoch_status: {result.get('epoch_status')}",
        f"epoch_hash: {result.get('epoch_hash')}",
        f"runtime_root: {result.get('runtime_root')}",
        f"workspace: {result.get('workspace')}",
        f"replay_files: {len(result.get('replay_files', []))}",
        f"workspace_files: {len(result.get('workspace_files', []))}",
        f"final_classification: {result.get('final_classification')}",
    ]
    if result.get("failure_reason"):
        lines.append(f"failure_reason: {result.get('failure_reason')}")
    return "\n".join(lines)


def _invoke_provider(*, request: dict[str, Any], adapter: Any, created_at: str, replay_dir: Path) -> dict[str, Any]:
    registry = ProviderRegistry()
    registry.register_provider(
        ProviderMetadata(
            provider_id=REAL_PROVIDER_ID,
            provider_type="implementation_generation_provider",
            provider_version=REAL_PROVIDER_VERSION,
            provider_status=AVAILABLE,
            domain="governance",
            capability="implementation_generation",
            resource_type="provider",
        )
    )
    return run_provider_attachment(
        provider_id=REAL_PROVIDER_ID,
        request=request,
        proposal_id="REAL-PROVIDER-PROPOSAL-FIRST-REAL-EPOCH-000001",
        timestamp=created_at,
        registry=registry,
        adapter=adapter,
        replay_dir=replay_dir,
    )


def _ocs_request_preparation(*, epoch_id: str, chain_id: str, human_request: str, created_at: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": "OCS_SEMANTIC_REQUEST_PREPARATION_V1",
        "epoch_id": epoch_id,
        "canonical_chain_id": chain_id,
        "human_request": human_request,
        "semantic_intent": "REAL_IMPLEMENTATION_GENERATION",
        "provider_request": {
            "request_type": "REAL_IMPLEMENTATION_GENERATION_REQUEST_V1",
            "human_request": human_request,
            "required_operation": CREATE_ONLY,
            "required_outputs": [
                "PYTHON_RUNTIME_MODULE",
                "PYTEST_TEST",
                "GOVERNANCE_DOCUMENT_MARKDOWN",
            ],
            "forbidden_operations": ["OVERWRITE", "DELETE", "RENAME", "MOVE", "IMPLICIT_MUTATION"],
        },
        "created_at": created_at,
        "replay_visible": True,
    }
    artifact["ocs_preparation_hash"] = replay_hash(artifact)
    return artifact


def _provider_response(human_request: str) -> dict[str, Any]:
    runtime_content = (
        "\"\"\"Provider-proposed utility for the first real implementation epoch.\"\"\"\n\n"
        "def normalize_epoch_label(value: str) -> str:\n"
        "    \"\"\"Normalize operator labels for replay-safe reporting.\"\"\"\n"
        "    if not isinstance(value, str):\n"
        "        raise TypeError('value must be a string')\n"
        "    return '_'.join(value.strip().upper().split())\n\n\n"
        "def describe_provider_candidate() -> dict:\n"
        "    return {\n"
        "        'status': 'provider_generated_candidate_ready',\n"
        "        'operation': 'CREATE_ONLY',\n"
        "        'request_bound': True,\n"
        "    }\n"
    )
    test_content = (
        "import pytest\n\n"
        "from aigol.runtime.first_real_epoch_provider_worker import (\n"
        "    describe_provider_candidate,\n"
        "    normalize_epoch_label,\n"
        ")\n\n\n"
        "def test_normalize_epoch_label():\n"
        "    assert normalize_epoch_label(' real epoch ') == 'REAL_EPOCH'\n\n\n"
        "def test_normalize_epoch_label_rejects_non_string():\n"
        "    with pytest.raises(TypeError):\n"
        "        normalize_epoch_label(123)\n\n\n"
        "def test_describe_provider_candidate():\n"
        "    result = describe_provider_candidate()\n"
        "    assert result['status'] == 'provider_generated_candidate_ready'\n"
        "    assert result['operation'] == 'CREATE_ONLY'\n"
    )
    governance_content = (
        "# FIRST_REAL_EPOCH_PROVIDER_WORKER_V1\n\n"
        "Status: provider-proposed implementation candidate.\n\n"
        f"Bound request: {human_request}\n"
    )
    return {
        "response_type": "REAL_PROVIDER_IMPLEMENTATION_CANDIDATE_V1",
        "implementation_purpose": "Provide a small replay-safe runtime utility proposed by a provider.",
        "planned_functionality": [
            "normalize operator labels for reports",
            "return candidate status metadata",
        ],
        "generated_files": [
            {
                "file_entry_id": "FILE-FIRST-REAL-EPOCH-RUNTIME-000001",
                "target_path": "aigol/runtime/first_real_epoch_provider_worker.py",
                "artifact_type": "PYTHON_RUNTIME_MODULE",
                "operation": CREATE_ONLY,
                "content": runtime_content,
                "source_segment_reference": "REAL-PROVIDER-SEGMENT-RUNTIME",
                "validation_requirements": ["python -m pytest tests/test_first_real_epoch_provider_worker.py"],
            },
            {
                "file_entry_id": "FILE-FIRST-REAL-EPOCH-GOVERNANCE-000001",
                "target_path": "governance/FIRST_REAL_EPOCH_PROVIDER_WORKER_V1.md",
                "artifact_type": "GOVERNANCE_DOCUMENT_MARKDOWN",
                "operation": CREATE_ONLY,
                "content": governance_content,
                "source_segment_reference": "REAL-PROVIDER-SEGMENT-GOVERNANCE",
                "validation_requirements": ["git diff --check"],
            },
        ],
        "generated_tests": [
            {
                "test_entry_id": "TEST-FIRST-REAL-EPOCH-RUNTIME-000001",
                "target_path": "tests/test_first_real_epoch_provider_worker.py",
                "artifact_type": "PYTEST_TEST",
                "operation": CREATE_ONLY,
                "content": test_content,
                "tests_file_entries": ["FILE-FIRST-REAL-EPOCH-RUNTIME-000001"],
                "validation_command": "python -m pytest tests/test_first_real_epoch_provider_worker.py",
                "expected_coverage_target": "aigol/runtime/first_real_epoch_provider_worker.py",
                "negative_case_requirement": "rejects non-string labels",
                "fixture_references": [],
            }
        ],
        "validation_requirements": ["python -m pytest tests/test_first_real_epoch_provider_worker.py", "git diff --check"],
        "known_gaps": [
            "provider proposal is untrusted until AiGOL validation succeeds",
            "generated test execution is documented but not run by the epoch runtime",
        ],
        "summary": "Provider proposed a useful Python normalization helper with tests and governance documentation.",
    }


def _candidate_from_provider(
    *,
    epoch_id: str,
    chain_id: str,
    bundle_id: str,
    ocs: dict[str, Any],
    provider_capture: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    envelope = deepcopy(provider_capture["provider_proposal_envelope"])
    response = _validate_provider_candidate_response(envelope.get("response"))
    artifact = {
        "artifact_type": "PROVIDER_GENERATED_IMPLEMENTATION_CANDIDATE_V1",
        "candidate_id": "PROVIDER-GENERATED-IMPLEMENTATION-CANDIDATE-FIRST-REAL-EPOCH-000001",
        "epoch_id": epoch_id,
        "canonical_chain_id": chain_id,
        "implementation_bundle_id": bundle_id,
        "created_at": created_at,
        "ocs_preparation_reference": ocs["epoch_id"],
        "ocs_preparation_hash": ocs["ocs_preparation_hash"],
        "provider_proposal_reference": envelope["proposal_id"],
        "provider_proposal_hash": envelope["proposal_hash"],
        "provider_invoked": True,
        "provider_output_trusted": False,
        "implementation_handoff_reference": "IMPLEMENTATION-HANDOFF-FIRST-REAL-EPOCH-000001",
        "implementation_handoff_hash": replay_hash({"handoff": ocs["ocs_preparation_hash"], "chain": chain_id}),
        "provider_generation_authorization_reference": provider_capture["provider_proposal_created"]["proposal_id"],
        "provider_generation_authorization_hash": provider_capture["provider_proposal_created"]["artifact_hash"],
        "provider_response_reference": envelope["proposal_id"],
        "provider_response_hash": envelope["proposal_hash"],
        "implementation_purpose": response["implementation_purpose"],
        "planned_functionality": deepcopy(response["planned_functionality"]),
        "generated_files": deepcopy(response["generated_files"]),
        "generated_tests": deepcopy(response["generated_tests"]),
        "validation_requirements": deepcopy(response["validation_requirements"]),
        "known_gaps": deepcopy(response["known_gaps"]),
        "provider_summary": response["summary"],
        "worker_invoked": False,
        "filesystem_mutated": False,
        "execution_authorized": False,
    }
    artifact["candidate_hash"] = replay_hash(artifact)
    return artifact


def _validate_provider_candidate_response(response: Any) -> dict[str, Any]:
    if not isinstance(response, dict):
        raise FailClosedRuntimeError("provider response must be an object")
    if response.get("response_type") != "REAL_PROVIDER_IMPLEMENTATION_CANDIDATE_V1":
        raise FailClosedRuntimeError("provider response type mismatch")
    for field in ("implementation_purpose", "summary"):
        _require_string(response.get(field), field)
    _require_string_list(response.get("planned_functionality"), "planned_functionality", allow_empty=False)
    _validate_entries(response.get("generated_files"), "generated_files", id_field="file_entry_id")
    _validate_entries(response.get("generated_tests"), "generated_tests", id_field="test_entry_id")
    _require_string_list(response.get("validation_requirements"), "validation_requirements", allow_empty=False)
    _require_string_list(response.get("known_gaps"), "known_gaps", allow_empty=True)
    return deepcopy(response)


def _validate_entries(value: Any, label: str, *, id_field: str) -> None:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError(f"{label} must be a non-empty list")
    for entry in value:
        if not isinstance(entry, dict):
            raise FailClosedRuntimeError(f"{label} entries must be objects")
        _require_string(entry.get(id_field), id_field)
        _require_string(entry.get("target_path"), "target_path")
        _require_string(entry.get("artifact_type"), "artifact_type")
        if entry.get("operation") != CREATE_ONLY:
            raise FailClosedRuntimeError("provider response must be CREATE_ONLY")
        _require_string(entry.get("content"), "content")


def _replay_report(
    *,
    runtime_path: Path,
    workspace_path: Path,
    provider_capture: dict[str, Any],
    candidate: dict[str, Any],
    manifest: dict[str, Any],
    summary: dict[str, Any],
    operator_decision: dict[str, Any],
    certification: dict[str, Any],
) -> dict[str, Any]:
    report = {
        "artifact_type": "AIGOL_FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH_REPLAY_REPORT",
        "provider_proposal_hash": provider_capture["provider_proposal_envelope"]["proposal_hash"],
        "candidate_hash": candidate["candidate_hash"],
        "implementation_manifest_hash": manifest["implementation_manifest_hash"],
        "implementation_summary_hash": summary["implementation_summary_hash"],
        "interactive_operator_decision_hash": operator_decision["interactive_operator_decision_hash"],
        "operator_decision": operator_decision["decision"],
        "implementation_certification_hash": certification["implementation_certification_hash"],
        "certification_status": certification["certification_status"],
        "certified_path_count": certification["certified_path_count"],
        "replay_files": _replay_files(runtime_path),
        "workspace_files": _workspace_files(workspace_path),
        "provider_output_trusted_before_validation": False,
        "materialization_without_approval": False,
        "authorization_without_approval": False,
        "replay_visible": True,
    }
    report["replay_report_hash"] = replay_hash(report)
    return report


def _failed_replay_report(*, runtime_path: Path, workspace_path: Path, exc: Exception) -> dict[str, Any]:
    report = {
        "artifact_type": "AIGOL_FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH_REPLAY_REPORT",
        "certification_status": "FAILED_CLOSED",
        "replay_files": _replay_files(runtime_path),
        "workspace_files": _workspace_files(workspace_path),
        "failure_reason": _failure_reason(exc),
        "replay_visible": True,
    }
    report["replay_report_hash"] = replay_hash(report)
    return report


def _acceptance_evidence(decision: dict[str, Any]) -> dict[str, str]:
    return {
        "actor_id": decision["actor_id"],
        "decision": ACCEPTANCE_DECISION,
        "accepted_at": decision["decided_at"],
        "acceptance_scope": ACCEPTANCE_SCOPE,
        "acceptance_statement": ACCEPTANCE_STATEMENT,
    }


def _authorization_evidence(*, actor_id: str, created_at: str) -> dict[str, str]:
    return {
        "actor_id": actor_id,
        "decision": AUTHORIZATION_DECISION,
        "authorized_at": created_at,
        "authorization_scope": AUTHORIZATION_SCOPE,
        "authorization_statement": AUTHORIZATION_STATEMENT,
    }


def _operator_checkpoint(
    *,
    human_request: str,
    candidate: dict[str, Any],
    manifest: dict[str, Any],
    summary: dict[str, Any],
    content_validation: dict[str, Any],
    test_validation: dict[str, Any],
) -> dict[str, Any]:
    affected_paths = [
        entry["target_path"]
        for entry in list(manifest.get("file_entries", [])) + list(manifest.get("test_entries", []))
    ]
    checkpoint = {
        "artifact_type": "INTERACTIVE_ACCEPTANCE_AUTHORIZATION_CHECKPOINT_V1",
        "request_summary": human_request,
        "generated_implementation_summary": {
            "purpose": summary["implementation_purpose"],
            "planned_functionality": deepcopy(summary["planned_functionality"]),
            "validation_outcomes": deepcopy(summary["validation_outcomes"]),
        },
        "manifest_summary": {
            "manifest_id": manifest["manifest_id"],
            "implementation_manifest_hash": manifest["implementation_manifest_hash"],
            "file_count": manifest["file_count"],
            "test_count": manifest["test_count"],
            "operation_mode": manifest["operation_mode"],
        },
        "affected_paths": affected_paths,
        "content_validation_hash": content_validation["generated_content_validation_hash"],
        "test_validation_hash": test_validation["generated_test_validation_hash"],
        "candidate_hash": candidate["candidate_hash"],
        "choices": [APPROVE, REJECT, ABORT],
        "replay_visible": True,
    }
    checkpoint["checkpoint_hash"] = replay_hash(checkpoint)
    return checkpoint


def _operator_decision_artifact(
    *,
    checkpoint: dict[str, Any],
    actor_id: str,
    decided_at: str,
    operator_decision: str | None,
    decision_reason: str | None,
    operator_decision_callback: Any | None,
) -> dict[str, Any]:
    raw_decision = operator_decision
    raw_reason = decision_reason
    if raw_decision is None and operator_decision_callback is not None:
        callback_result = operator_decision_callback(deepcopy(checkpoint))
        if isinstance(callback_result, dict):
            raw_decision = callback_result.get("decision")
            raw_reason = callback_result.get("decision_reason", raw_reason)
        else:
            raw_decision = callback_result
    decision = _normalize_decision(raw_decision)
    reason = _require_string(raw_reason or f"Operator selected {decision}.", "decision_reason")
    artifact = {
        "artifact_type": "INTERACTIVE_OPERATOR_DECISION_ARTIFACT_V1",
        "checkpoint_hash": checkpoint["checkpoint_hash"],
        "checkpoint": deepcopy(checkpoint),
        "actor_id": _require_string(actor_id, "actor_id"),
        "decision": decision,
        "decided_at": _require_string(decided_at, "decided_at"),
        "decision_reason": reason,
        "approval_granted": decision == APPROVE,
        "authorization_allowed": decision == APPROVE,
        "materialization_allowed": decision == APPROVE,
        "rejection_recorded": decision == REJECT,
        "abort_recorded": decision == ABORT,
        "filesystem_mutated": False,
        "filesystem_mutation_authorized": False,
        "execution_authorized": False,
        "replay_visible": True,
    }
    artifact["interactive_operator_decision_hash"] = replay_hash(artifact)
    return artifact


def _require_approval(decision: dict[str, Any]) -> None:
    if decision["decision"] == APPROVE:
        return
    if decision["decision"] == REJECT:
        raise _GateStop(
            "REAL_EPOCH_REJECTED_FAILED_CLOSED",
            True,
            f"interactive operator rejected implementation: {decision['decision_reason']}",
        )
    raise _GateStop(
        "REAL_EPOCH_ABORTED",
        False,
        f"interactive operator aborted implementation: {decision['decision_reason']}",
    )


def _normalize_decision(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError("operator decision is required")
    decision = value.strip().upper()
    if decision not in ALLOWED_OPERATOR_DECISIONS:
        raise FailClosedRuntimeError("operator decision must be APPROVE, REJECT, or ABORT")
    return decision


def _persist(path: Path, artifact: dict[str, Any]) -> None:
    write_json_immutable(path, artifact)


def _replay_files(runtime_root: Path) -> list[str]:
    if not runtime_root.exists():
        return []
    return sorted(str(path.relative_to(runtime_root)) for path in runtime_root.rglob("*") if path.is_file())


def _workspace_files(workspace: Path) -> list[str]:
    if not workspace.exists():
        return []
    return sorted(str(path.relative_to(workspace)) for path in workspace.rglob("*") if path.is_file())


def _require_stage_status(artifact: dict[str, Any], field: str, expected: str) -> None:
    actual = artifact.get(field)
    if actual != expected:
        failure = artifact.get("failure_reason") or f"{field} expected {expected}, got {actual}"
        raise FailClosedRuntimeError(str(failure))


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{label} is required")
    return value.strip()


def _require_string_list(value: Any, label: str, *, allow_empty: bool) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise FailClosedRuntimeError(f"{label} must be a list")
    return [_require_string(item, label) for item in value]


def _failure_reason(exc: Exception) -> str:
    reason = str(exc)
    return reason or "first real implementation generation epoch failed closed"


__all__ = [
    "AIGOL_FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH_STATUS",
    "AIGOL_FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH_VERSION",
    "LocalRealImplementationProviderAdapter",
    "render_first_real_implementation_generation_epoch",
    "run_first_real_implementation_generation_epoch",
]
