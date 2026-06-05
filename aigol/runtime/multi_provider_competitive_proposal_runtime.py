"""Competitive multi-provider implementation proposal runtime."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.provider.provider_registry import AVAILABLE, ProviderMetadata, ProviderRegistry
from aigol.provider.provider_runtime import PROVIDER_PROPOSAL_RETURNED, run_provider_attachment
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
from aigol.runtime.generated_content_validation_runtime import GENERATED_CONTENT_VALIDATED, validate_generated_content
from aigol.runtime.generated_test_validation_runtime import GENERATED_TEST_VALIDATED, validate_generated_tests
from aigol.runtime.implementation_certification_runtime import certify_implementation
from aigol.runtime.implementation_manifest_runtime import CREATE_ONLY, create_implementation_manifest
from aigol.runtime.implementation_summary_runtime import create_implementation_summary
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash, write_json_immutable


AIGOL_MULTI_PROVIDER_COMPETITIVE_PROPOSAL_RUNTIME_VERSION = (
    "AIGOL_MULTI_PROVIDER_COMPETITIVE_PROPOSAL_RUNTIME_V1"
)
AIGOL_MULTI_PROVIDER_COMPETITIVE_PROPOSAL_RUNTIME_STATUS = "CERTIFIED"
COMMAND = "aigol implementation compete"
SELECT_PROVIDER = "SELECT_PROVIDER"
REJECT_ALL = "REJECT_ALL"
ABORT = "ABORT"
PROVIDER_IDS = ("PROVIDER_A", "PROVIDER_B", "PROVIDER_C")


class CompetitiveImplementationProviderAdapter:
    """Bounded provider adapter that proposes implementation content only."""

    provider_version = "1.0.0"

    def __init__(self, provider_id: str, label: str, *, invalid_tests: bool = False) -> None:
        self.provider_id = _require_provider_id(provider_id)
        self.label = _require_string(label, "label")
        self.invalid_tests = invalid_tests

    def generate_proposal(self, request: Any, *, proposal_id: str, timestamp: str) -> Any:
        if not isinstance(request, dict):
            raise FailClosedRuntimeError("competitive provider request must be an object")
        human_request = _require_string(request.get("human_request"), "human_request")
        return create_provider_proposal_envelope(
            proposal_id=proposal_id,
            provider_id=self.provider_id,
            provider_version=self.provider_version,
            request=deepcopy(request),
            response=_provider_response(
                human_request=human_request,
                provider_id=self.provider_id,
                label=self.label,
                invalid_tests=self.invalid_tests,
            ),
            timestamp=timestamp,
        )


def run_multi_provider_competitive_proposal_runtime(
    *,
    human_request: str,
    runtime_root: str | Path,
    workspace: str | Path,
    created_at: str,
    actor_id: str = "human.operator",
    selection: str | None = None,
    decision_reason: str | None = None,
    provider_adapters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run competitive provider proposals and materialize only the selected winner."""

    runtime_path = Path(runtime_root)
    workspace_path = Path(workspace)
    request_text = _require_string(human_request, "human_request")
    decision_value = selection or ABORT
    adapters = provider_adapters or _default_provider_adapters()
    try:
        ocs = _ocs_request(request_text=request_text, created_at=created_at)
        _persist(runtime_path / "000_ocs_semantic_request_preparation.json", ocs)
        provider_results = []
        for provider_id in PROVIDER_IDS:
            provider_results.append(
                _provider_pipeline(
                    provider_id=provider_id,
                    adapter=adapters[provider_id],
                    ocs=ocs,
                    runtime_root=runtime_path,
                    created_at=created_at,
                )
            )
        competition = _competition_artifact(
            request_text=request_text,
            provider_results=provider_results,
            created_at=created_at,
        )
        _persist(runtime_path / "010_comparative_validation_artifact.json", competition)
        decision = _selection_decision_artifact(
            competition=competition,
            selection=decision_value,
            actor_id=actor_id,
            decided_at=created_at,
            decision_reason=decision_reason,
        )
        _persist(runtime_path / "011_competitive_selection_decision_artifact.json", decision)
        selected = _selected_provider_result(decision=decision, provider_results=provider_results)
        acceptance = accept_generated_content(
            acceptance_id="MULTI-PROVIDER-CONTENT-ACCEPTANCE-000001",
            implementation_manifest_artifact=selected["manifest"],
            generated_content_validation_artifact=selected["content_validation"],
            generated_test_validation_artifact=selected["test_validation"],
            human_acceptance_evidence=_acceptance_evidence(decision),
            created_at=created_at,
        )["generated_content_acceptance_artifact"]
        _require_stage_status(acceptance, "acceptance_status", "GENERATED_CONTENT_ACCEPTED")
        _persist(runtime_path / "012_selected_content_acceptance_artifact.json", acceptance)
        authorization = authorize_filesystem_mutation(
            authorization_id="MULTI-PROVIDER-FILESYSTEM-MUTATION-AUTHORIZATION-000001",
            implementation_manifest_artifact=selected["manifest"],
            generated_content_validation_artifact=selected["content_validation"],
            generated_test_validation_artifact=selected["test_validation"],
            generated_content_acceptance_artifact=acceptance,
            human_authorization_evidence=_authorization_evidence(actor_id=actor_id, created_at=created_at),
            created_at=created_at,
        )["filesystem_mutation_authorization_artifact"]
        _require_stage_status(authorization, "authorization_status", "FILESYSTEM_MUTATION_AUTHORIZED")
        _persist(runtime_path / "013_selected_filesystem_mutation_authorization_artifact.json", authorization)
        mutation = apply_filesystem_mutation(
            mutation_id="MULTI-PROVIDER-FILESYSTEM-MUTATION-000001",
            implementation_manifest_artifact=selected["manifest"],
            filesystem_mutation_authorization_artifact=authorization,
            target_root=workspace_path,
            created_at=created_at,
            target_root_reference="OPERATOR_SUPPLIED_WORKSPACE",
        )["filesystem_mutation_artifact"]
        _require_stage_status(mutation, "mutation_status", "FILESYSTEM_MUTATION_COMPLETED")
        _persist(runtime_path / "014_selected_filesystem_mutation_artifact.json", mutation)
        certification = certify_implementation(
            certification_id="MULTI-PROVIDER-IMPLEMENTATION-CERTIFICATION-000001",
            implementation_manifest_artifact=selected["manifest"],
            filesystem_mutation_authorization_artifact=authorization,
            generated_content_acceptance_artifact=acceptance,
            filesystem_mutation_artifact=mutation,
            created_at=created_at,
        )["implementation_certification_artifact"]
        _require_stage_status(certification, "certification_status", "IMPLEMENTATION_CERTIFIED")
        _persist(runtime_path / "015_selected_implementation_certification_artifact.json", certification)
        replay = _replay_artifact(
            runtime_path=runtime_path,
            workspace_path=workspace_path,
            competition=competition,
            decision=decision,
            certification=certification,
        )
        _persist(runtime_path / "016_competitive_replay_artifact.json", replay)
        status = "MULTI_PROVIDER_COMPETITION_CERTIFIED"
        fail_closed = False
        failure_reason = None
    except _CompetitionStop as exc:
        replay = _failed_replay_artifact(runtime_path, workspace_path, exc.reason)
        status = exc.status
        fail_closed = exc.fail_closed
        failure_reason = exc.reason
    except Exception as exc:
        replay = _failed_replay_artifact(runtime_path, workspace_path, _failure_reason(exc))
        status = "MULTI_PROVIDER_COMPETITION_FAILED_CLOSED"
        fail_closed = True
        failure_reason = _failure_reason(exc)

    result = {
        "command": COMMAND,
        "milestone": AIGOL_MULTI_PROVIDER_COMPETITIVE_PROPOSAL_RUNTIME_VERSION,
        "competition_status": status,
        "final_classification": (
            "AIGOL_MULTI_PROVIDER_COMPETITIVE_PROPOSAL_RUNTIME_STATUS = "
            f"{AIGOL_MULTI_PROVIDER_COMPETITIVE_PROPOSAL_RUNTIME_STATUS}"
        ),
        "human_request": request_text,
        "runtime_root": str(runtime_path),
        "workspace": str(workspace_path),
        "replay_files": _replay_files(runtime_path),
        "workspace_files": _workspace_files(workspace_path),
        "competitive_replay": replay,
        "fail_closed": fail_closed,
        "failure_reason": failure_reason,
    }
    result["competition_hash"] = replay_hash(result)
    return result


def render_multi_provider_competitive_review(result: dict[str, Any]) -> str:
    lines = [
        "AIGOL MULTI PROVIDER COMPETITIVE PROPOSAL",
        f"status: {result.get('competition_status')}",
        f"competition_hash: {result.get('competition_hash')}",
        f"runtime_root: {result.get('runtime_root')}",
        f"workspace: {result.get('workspace')}",
        f"replay_files: {len(result.get('replay_files', []))}",
        f"workspace_files: {len(result.get('workspace_files', []))}",
    ]
    replay = result.get("competitive_replay", {})
    for proposal in replay.get("proposal_summaries", []):
        lines.append(
            "provider: "
            f"{proposal.get('provider_id')} | "
            f"{proposal.get('validation_status')} | "
            f"{proposal.get('proposal_summary')} | "
            f"{proposal.get('affected_paths')}"
        )
    if result.get("failure_reason"):
        lines.append(f"failure_reason: {result['failure_reason']}")
    lines.append(str(result.get("final_classification")))
    return "\n".join(lines)


class _CompetitionStop(Exception):
    def __init__(self, status: str, fail_closed: bool, reason: str) -> None:
        super().__init__(reason)
        self.status = status
        self.fail_closed = fail_closed
        self.reason = reason


def _provider_pipeline(
    *,
    provider_id: str,
    adapter: Any,
    ocs: dict[str, Any],
    runtime_root: Path,
    created_at: str,
) -> dict[str, Any]:
    provider_dir = runtime_root / provider_id.lower()
    try:
        capture = _invoke_provider(provider_id=provider_id, adapter=adapter, request=ocs["provider_request"], created_at=created_at, replay_dir=provider_dir / "proposal")
        _require_stage_status(capture["provider_proposal_returned"], "event_type", PROVIDER_PROPOSAL_RETURNED)
        candidate = _candidate_from_provider(provider_id=provider_id, ocs=ocs, provider_capture=capture, created_at=created_at)
        _persist(provider_dir / "002_provider_generated_candidate.json", candidate)
        manifest = create_implementation_manifest(
            manifest_id=f"IMPLEMENTATION-MANIFEST-{provider_id}-000001",
            canonical_chain_id=ocs["canonical_chain_id"],
            implementation_bundle_id=f"MULTI_PROVIDER_{provider_id}_BUNDLE_V1",
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
            target_worker=f"MULTI_PROVIDER_{provider_id}_WORKER",
            generated_files=deepcopy(candidate["generated_files"]),
            generated_tests=deepcopy(candidate["generated_tests"]),
            validation_requirements=deepcopy(candidate["validation_requirements"]),
            known_gaps=deepcopy(candidate["known_gaps"]),
            created_at=created_at,
            replay_dir=provider_dir / "implementation_manifest",
        )["implementation_manifest_artifact"]
        _require_stage_status(manifest, "manifest_status", "IMPLEMENTATION_MANIFEST_CREATED")
        _persist(provider_dir / "003_implementation_manifest_artifact.json", manifest)
        content_validation = validate_generated_content(
            validation_id=f"GENERATED-CONTENT-VALIDATION-{provider_id}-000001",
            implementation_manifest_artifact=manifest,
            created_at=created_at,
        )["generated_content_validation_artifact"]
        _persist(provider_dir / "004_generated_content_validation_artifact.json", content_validation)
        test_validation = validate_generated_tests(
            validation_id=f"GENERATED-TEST-VALIDATION-{provider_id}-000001",
            implementation_manifest_artifact=manifest,
            generated_test_bundle=manifest["test_entries"],
            created_at=created_at,
        )["generated_test_validation_artifact"]
        _persist(provider_dir / "005_generated_test_validation_artifact.json", test_validation)
        summary = create_implementation_summary(
            summary_id=f"IMPLEMENTATION-SUMMARY-{provider_id}-000001",
            implementation_manifest_artifact=manifest,
            generated_content_validation_artifact=content_validation,
            generated_test_validation_artifact=test_validation,
            created_at=created_at,
        )["implementation_summary_artifact"]
        _persist(provider_dir / "006_implementation_summary_artifact.json", summary)
        validation_status = (
            "VALIDATED"
            if content_validation["validation_status"] == GENERATED_CONTENT_VALIDATED
            and test_validation["validation_status"] == GENERATED_TEST_VALIDATED
            and summary["summary_status"] == "IMPLEMENTATION_SUMMARY_CREATED"
            else "FAILED_VALIDATION"
        )
        failure_reason = None if validation_status == "VALIDATED" else (
            content_validation.get("failure_reason")
            or test_validation.get("failure_reason")
            or summary.get("failure_reason")
        )
        result = {
            "provider_id": provider_id,
            "provider_capture": capture,
            "candidate": candidate,
            "manifest": manifest,
            "content_validation": content_validation,
            "test_validation": test_validation,
            "summary": summary,
            "validation_status": validation_status,
            "failure_reason": failure_reason,
            "affected_paths": _affected_paths(manifest),
        }
    except Exception as exc:
        result = {
            "provider_id": provider_id,
            "provider_capture": None,
            "candidate": None,
            "manifest": None,
            "content_validation": None,
            "test_validation": None,
            "summary": None,
            "validation_status": "FAILED_VALIDATION",
            "failure_reason": _failure_reason(exc),
            "affected_paths": [],
        }
    _persist(provider_dir / "provider_pipeline_result.json", _safe_provider_result(result))
    return result


def _invoke_provider(*, provider_id: str, adapter: Any, request: dict[str, Any], created_at: str, replay_dir: Path) -> dict[str, Any]:
    registry = ProviderRegistry()
    registry.register_provider(
        ProviderMetadata(
            provider_id=provider_id,
            provider_type="implementation_generation_provider",
            provider_version=adapter.provider_version,
            provider_status=AVAILABLE,
            domain="governance",
            capability="implementation_generation",
            resource_type="provider",
        )
    )
    return run_provider_attachment(
        provider_id=provider_id,
        request=request,
        proposal_id=f"REAL-PROVIDER-PROPOSAL-{provider_id}-000001",
        timestamp=created_at,
        registry=registry,
        adapter=adapter,
        replay_dir=replay_dir,
    )


def _ocs_request(*, request_text: str, created_at: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": "MULTI_PROVIDER_OCS_REQUEST_PREPARATION_V1",
        "canonical_chain_id": "CHAIN-MULTI-PROVIDER-COMPETITIVE-PROPOSAL-000001",
        "human_request": request_text,
        "semantic_intent": "MULTI_PROVIDER_IMPLEMENTATION_COMPETITION",
        "provider_request": {
            "request_type": "MULTI_PROVIDER_IMPLEMENTATION_REQUEST_V1",
            "human_request": request_text,
            "required_operation": CREATE_ONLY,
            "required_outputs": ["PYTHON_RUNTIME_MODULE", "PYTEST_TEST", "GOVERNANCE_DOCUMENT_MARKDOWN"],
            "forbidden_operations": ["OVERWRITE", "DELETE", "RENAME", "MOVE", "IMPLICIT_MUTATION"],
        },
        "created_at": created_at,
        "replay_visible": True,
    }
    artifact["ocs_preparation_hash"] = replay_hash(artifact)
    return artifact


def _provider_response(*, human_request: str, provider_id: str, label: str, invalid_tests: bool) -> dict[str, Any]:
    module_path = "aigol/runtime/multi_provider_selected_worker.py"
    test_path = "tests/test_multi_provider_selected_worker.py"
    content = (
        f'"""Provider {provider_id} proposal for competitive implementation."""\n\n'
        "def selected_provider_summary():\n"
        "    return {\n"
        f"        'provider': '{provider_id}',\n"
        f"        'label': '{label}',\n"
        "        'status': 'competitive_candidate_ready',\n"
        "    }\n"
    )
    test_content = (
        "from aigol.runtime.multi_provider_selected_worker import selected_provider_summary\n\n\n"
        "def test_selected_provider_summary():\n"
        "    result = selected_provider_summary()\n"
        f"    assert result['provider'] == '{provider_id}'\n"
        "    assert result['status'] == 'competitive_candidate_ready'\n"
    )
    tests = [] if invalid_tests else [
        {
            "test_entry_id": f"TEST-{provider_id}-RUNTIME-000001",
            "target_path": test_path,
            "artifact_type": "PYTEST_TEST",
            "operation": CREATE_ONLY,
            "content": test_content,
            "tests_file_entries": [f"FILE-{provider_id}-RUNTIME-000001"],
            "validation_command": "python -m pytest tests/test_multi_provider_selected_worker.py",
            "expected_coverage_target": module_path,
            "negative_case_requirement": "rejects incorrect provider selection",
            "fixture_references": [],
        }
    ]
    return {
        "response_type": "COMPETITIVE_PROVIDER_IMPLEMENTATION_CANDIDATE_V1",
        "proposal_summary": f"{provider_id} proposes {label}.",
        "generated_files": [
            {
                "file_entry_id": f"FILE-{provider_id}-RUNTIME-000001",
                "target_path": module_path,
                "artifact_type": "PYTHON_RUNTIME_MODULE",
                "operation": CREATE_ONLY,
                "content": content,
                "source_segment_reference": f"{provider_id}-SEGMENT-RUNTIME",
                "validation_requirements": ["python -m pytest tests/test_multi_provider_selected_worker.py"],
            },
            {
                "file_entry_id": f"FILE-{provider_id}-GOVERNANCE-000001",
                "target_path": "governance/MULTI_PROVIDER_SELECTED_WORKER_V1.md",
                "artifact_type": "GOVERNANCE_DOCUMENT_MARKDOWN",
                "operation": CREATE_ONLY,
                "content": f"# MULTI_PROVIDER_SELECTED_WORKER_V1\n\nSelected provider candidate: {provider_id}.\n",
                "source_segment_reference": f"{provider_id}-SEGMENT-GOVERNANCE",
                "validation_requirements": ["git diff --check"],
            },
        ],
        "generated_tests": tests,
        "validation_requirements": ["python -m pytest tests/test_multi_provider_selected_worker.py", "git diff --check"],
        "known_gaps": ["provider proposals remain untrusted until validation and selection"],
    }


def _candidate_from_provider(*, provider_id: str, ocs: dict[str, Any], provider_capture: dict[str, Any], created_at: str) -> dict[str, Any]:
    envelope = deepcopy(provider_capture["provider_proposal_envelope"])
    response = _validate_provider_response(envelope.get("response"))
    artifact = {
        "artifact_type": "COMPETITIVE_PROVIDER_IMPLEMENTATION_CANDIDATE_V1",
        "candidate_id": f"COMPETITIVE-CANDIDATE-{provider_id}-000001",
        "provider_id": provider_id,
        "canonical_chain_id": ocs["canonical_chain_id"],
        "implementation_handoff_reference": f"IMPLEMENTATION-HANDOFF-{provider_id}-000001",
        "implementation_handoff_hash": replay_hash({"provider": provider_id, "ocs": ocs["ocs_preparation_hash"]}),
        "provider_generation_authorization_reference": provider_capture["provider_proposal_created"]["proposal_id"],
        "provider_generation_authorization_hash": provider_capture["provider_proposal_created"]["artifact_hash"],
        "provider_response_reference": envelope["proposal_id"],
        "provider_response_hash": envelope["proposal_hash"],
        "provider_output_trusted": False,
        "proposal_summary": response["proposal_summary"],
        "generated_files": deepcopy(response["generated_files"]),
        "generated_tests": deepcopy(response["generated_tests"]),
        "validation_requirements": deepcopy(response["validation_requirements"]),
        "known_gaps": deepcopy(response["known_gaps"]),
        "created_at": created_at,
    }
    artifact["candidate_hash"] = replay_hash(artifact)
    return artifact


def _validate_provider_response(response: Any) -> dict[str, Any]:
    if not isinstance(response, dict):
        raise FailClosedRuntimeError("provider response must be an object")
    if response.get("response_type") != "COMPETITIVE_PROVIDER_IMPLEMENTATION_CANDIDATE_V1":
        raise FailClosedRuntimeError("provider response type mismatch")
    _require_string(response.get("proposal_summary"), "proposal_summary")
    _validate_entries(response.get("generated_files"), "generated_files", "file_entry_id")
    _validate_entries(response.get("generated_tests"), "generated_tests", "test_entry_id")
    return deepcopy(response)


def _validate_entries(value: Any, label: str, id_field: str) -> None:
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


def _competition_artifact(*, request_text: str, provider_results: list[dict[str, Any]], created_at: str) -> dict[str, Any]:
    summaries = [_provider_summary(result) for result in provider_results]
    artifact = {
        "artifact_type": "MULTI_PROVIDER_COMPARATIVE_VALIDATION_ARTIFACT_V1",
        "request_summary": request_text,
        "proposal_summaries": summaries,
        "validated_provider_count": sum(1 for item in summaries if item["validation_status"] == "VALIDATED"),
        "choices": [f"SELECT {provider_id}" for provider_id in PROVIDER_IDS] + [REJECT_ALL, ABORT],
        "created_at": created_at,
        "replay_visible": True,
    }
    artifact["comparative_validation_hash"] = replay_hash(artifact)
    return artifact


def _selection_decision_artifact(*, competition: dict[str, Any], selection: str, actor_id: str, decided_at: str, decision_reason: str | None) -> dict[str, Any]:
    normalized = _normalize_selection(selection)
    artifact = {
        "artifact_type": "MULTI_PROVIDER_SELECTION_DECISION_ARTIFACT_V1",
        "comparative_validation_hash": competition["comparative_validation_hash"],
        "actor_id": _require_string(actor_id, "actor_id"),
        "decision": normalized["decision"],
        "selected_provider_id": normalized["selected_provider_id"],
        "decided_at": _require_string(decided_at, "decided_at"),
        "decision_reason": _require_string(decision_reason or f"Operator selected {selection}.", "decision_reason"),
        "authorization_allowed_provider_id": normalized["selected_provider_id"],
        "materialization_allowed_provider_id": normalized["selected_provider_id"],
        "replay_visible": True,
    }
    artifact["selection_decision_hash"] = replay_hash(artifact)
    return artifact


def _selected_provider_result(*, decision: dict[str, Any], provider_results: list[dict[str, Any]]) -> dict[str, Any]:
    if decision["decision"] == REJECT_ALL:
        raise _CompetitionStop("MULTI_PROVIDER_REJECTED_FAILED_CLOSED", True, decision["decision_reason"])
    if decision["decision"] == ABORT:
        raise _CompetitionStop("MULTI_PROVIDER_ABORTED", False, decision["decision_reason"])
    selected_id = decision["selected_provider_id"]
    for result in provider_results:
        if result["provider_id"] == selected_id:
            if result["validation_status"] != "VALIDATED":
                raise FailClosedRuntimeError("selected provider did not pass validation")
            return result
    raise FailClosedRuntimeError("selected provider is unavailable")


def _normalize_selection(selection: str) -> dict[str, str | None]:
    text = _require_string(selection, "selection").strip().upper().replace("-", "_")
    if text in {REJECT_ALL, "REJECT"}:
        return {"decision": REJECT_ALL, "selected_provider_id": None}
    if text == ABORT:
        return {"decision": ABORT, "selected_provider_id": None}
    if text.startswith("SELECT "):
        provider_id = text.split(" ", 1)[1].strip().replace("-", "_")
    elif text.startswith("SELECT_"):
        provider_id = text.removeprefix("SELECT_")
    else:
        provider_id = text
    if provider_id in PROVIDER_IDS:
        return {"decision": SELECT_PROVIDER, "selected_provider_id": provider_id}
    raise FailClosedRuntimeError("selection must select PROVIDER_A, PROVIDER_B, PROVIDER_C, REJECT_ALL, or ABORT")


def _provider_summary(result: dict[str, Any]) -> dict[str, Any]:
    candidate = result.get("candidate") or {}
    return {
        "provider_id": result["provider_id"],
        "proposal_summary": candidate.get("proposal_summary", "Proposal unavailable."),
        "validation_status": result["validation_status"],
        "affected_paths": deepcopy(result["affected_paths"]),
        "manifest_hash": (result.get("manifest") or {}).get("implementation_manifest_hash"),
        "content_validation_hash": (result.get("content_validation") or {}).get("generated_content_validation_hash"),
        "test_validation_hash": (result.get("test_validation") or {}).get("generated_test_validation_hash"),
        "failure_reason": result.get("failure_reason"),
    }


def _safe_provider_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "provider_id": result["provider_id"],
        "validation_status": result["validation_status"],
        "affected_paths": deepcopy(result["affected_paths"]),
        "proposal_summary": (result.get("candidate") or {}).get("proposal_summary"),
        "failure_reason": result.get("failure_reason"),
        "replay_visible": True,
        "provider_pipeline_hash": replay_hash(
            {
                "provider_id": result["provider_id"],
                "validation_status": result["validation_status"],
                "affected_paths": result["affected_paths"],
                "failure_reason": result.get("failure_reason"),
            }
        ),
    }


def _affected_paths(manifest: dict[str, Any]) -> list[str]:
    return [
        entry["target_path"]
        for entry in list(manifest.get("file_entries", [])) + list(manifest.get("test_entries", []))
    ]


def _replay_artifact(*, runtime_path: Path, workspace_path: Path, competition: dict[str, Any], decision: dict[str, Any], certification: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "artifact_type": "MULTI_PROVIDER_COMPETITIVE_REPLAY_ARTIFACT_V1",
        "proposal_summaries": deepcopy(competition["proposal_summaries"]),
        "selection_decision_hash": decision["selection_decision_hash"],
        "selected_provider_id": decision["selected_provider_id"],
        "implementation_certification_hash": certification["implementation_certification_hash"],
        "certification_status": certification["certification_status"],
        "authorization_only_for_selected_provider": True,
        "materialization_only_for_selected_provider": True,
        "replay_files": _replay_files(runtime_path),
        "workspace_files": _workspace_files(workspace_path),
        "replay_visible": True,
    }
    artifact["competitive_replay_hash"] = replay_hash(artifact)
    return artifact


def _failed_replay_artifact(runtime_path: Path, workspace_path: Path, reason: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": "MULTI_PROVIDER_COMPETITIVE_REPLAY_ARTIFACT_V1",
        "proposal_summaries": _proposal_summaries_from_files(runtime_path),
        "certification_status": "FAILED_CLOSED",
        "failure_reason": reason,
        "replay_files": _replay_files(runtime_path),
        "workspace_files": _workspace_files(workspace_path),
        "replay_visible": True,
    }
    artifact["competitive_replay_hash"] = replay_hash(artifact)
    return artifact


def _proposal_summaries_from_files(runtime_path: Path) -> list[dict[str, Any]]:
    summaries = []
    for provider_id in PROVIDER_IDS:
        path = runtime_path / provider_id.lower() / "provider_pipeline_result.json"
        if path.exists():
            # Avoid importing load_json just for best-effort failed replay summaries.
            import json

            summaries.append(json.loads(path.read_text(encoding="utf-8")))
    return summaries


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


def _default_provider_adapters() -> dict[str, CompetitiveImplementationProviderAdapter]:
    return {
        "PROVIDER_A": CompetitiveImplementationProviderAdapter("PROVIDER_A", "conservative replay helper"),
        "PROVIDER_B": CompetitiveImplementationProviderAdapter("PROVIDER_B", "operator-facing summary helper"),
        "PROVIDER_C": CompetitiveImplementationProviderAdapter("PROVIDER_C", "audit-friendly metadata helper"),
    }


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


def _require_provider_id(value: Any) -> str:
    provider_id = _require_string(value, "provider_id").upper().replace("-", "_")
    if provider_id not in PROVIDER_IDS:
        raise FailClosedRuntimeError("provider id must be PROVIDER_A, PROVIDER_B, or PROVIDER_C")
    return provider_id


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{label} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    reason = str(exc)
    return reason or "multi-provider competitive proposal runtime failed closed"


__all__ = [
    "AIGOL_MULTI_PROVIDER_COMPETITIVE_PROPOSAL_RUNTIME_STATUS",
    "AIGOL_MULTI_PROVIDER_COMPETITIVE_PROPOSAL_RUNTIME_VERSION",
    "CompetitiveImplementationProviderAdapter",
    "render_multi_provider_competitive_review",
    "run_multi_provider_competitive_proposal_runtime",
]
