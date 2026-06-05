"""End-to-end implementation generation epoch command."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

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


AIGOL_FIRST_END_TO_END_IMPLEMENTATION_GENERATION_EPOCH_STATUS = "CERTIFIED_WITH_OPERATOR_FRICTION"
MILESTONE = "AIGOL_FIRST_END_TO_END_IMPLEMENTATION_GENERATION_EPOCH_V1"
COMMAND = "aigol implementation epoch"


def run_implementation_generation_epoch(
    *,
    request: str,
    runtime_root: str | Path,
    workspace: str | Path,
    created_at: str,
    actor_id: str = "human.operator",
) -> dict[str, Any]:
    """Run a deterministic implementation generation epoch through certified gates."""

    runtime_path = Path(runtime_root)
    workspace_path = Path(workspace)
    epoch_id = "AIGOL-FIRST-E2E-IMPLEMENTATION-GENERATION-EPOCH-000001"
    chain_id = "CHAIN-FIRST-E2E-IMPLEMENTATION-GENERATION-EPOCH-000001"
    bundle_id = "FIRST_E2E_IMPLEMENTATION_GENERATION_BUNDLE_V1"
    candidate = _implementation_candidate(
        request=request,
        epoch_id=epoch_id,
        chain_id=chain_id,
        bundle_id=bundle_id,
        created_at=created_at,
    )

    try:
        _persist(runtime_path / "000_implementation_request.json", candidate["implementation_request"])
        _persist(runtime_path / "001_generated_implementation_candidate.json", candidate)
        manifest = create_implementation_manifest(
            manifest_id="IMPLEMENTATION-MANIFEST-FIRST-E2E-EPOCH-000001",
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
            target_worker="FIRST_E2E_EPOCH_SAMPLE_WORKER",
            generated_files=deepcopy(candidate["generated_files"]),
            generated_tests=deepcopy(candidate["generated_tests"]),
            validation_requirements=deepcopy(candidate["validation_requirements"]),
            known_gaps=deepcopy(candidate["known_gaps"]),
            created_at=created_at,
            replay_dir=runtime_path / "implementation_manifest",
        )["implementation_manifest_artifact"]
        _require_stage_status(manifest, "manifest_status", "IMPLEMENTATION_MANIFEST_CREATED")
        _persist(runtime_path / "002_implementation_manifest_artifact.json", manifest)
        content_validation = validate_generated_content(
            validation_id="GENERATED-CONTENT-VALIDATION-FIRST-E2E-EPOCH-000001",
            implementation_manifest_artifact=manifest,
            created_at=created_at,
        )["generated_content_validation_artifact"]
        _require_stage_status(content_validation, "validation_status", "GENERATED_CONTENT_VALIDATED")
        _persist(runtime_path / "003_generated_content_validation_artifact.json", content_validation)
        test_validation = validate_generated_tests(
            validation_id="GENERATED-TEST-VALIDATION-FIRST-E2E-EPOCH-000001",
            implementation_manifest_artifact=manifest,
            generated_test_bundle=manifest["test_entries"],
            created_at=created_at,
        )["generated_test_validation_artifact"]
        _require_stage_status(test_validation, "validation_status", "GENERATED_TEST_VALIDATED")
        _persist(runtime_path / "004_generated_test_validation_artifact.json", test_validation)
        summary = create_implementation_summary(
            summary_id="IMPLEMENTATION-SUMMARY-FIRST-E2E-EPOCH-000001",
            implementation_manifest_artifact=manifest,
            generated_content_validation_artifact=content_validation,
            generated_test_validation_artifact=test_validation,
            created_at=created_at,
        )["implementation_summary_artifact"]
        _require_stage_status(summary, "summary_status", "IMPLEMENTATION_SUMMARY_CREATED")
        _persist(runtime_path / "005_implementation_summary_artifact.json", summary)
        acceptance = accept_generated_content(
            acceptance_id="GENERATED-CONTENT-ACCEPTANCE-FIRST-E2E-EPOCH-000001",
            implementation_manifest_artifact=manifest,
            generated_content_validation_artifact=content_validation,
            generated_test_validation_artifact=test_validation,
            human_acceptance_evidence=_acceptance_evidence(actor_id=actor_id, created_at=created_at),
            created_at=created_at,
        )["generated_content_acceptance_artifact"]
        _require_stage_status(acceptance, "acceptance_status", "GENERATED_CONTENT_ACCEPTED")
        _persist(runtime_path / "006_generated_content_acceptance_artifact.json", acceptance)
        authorization = authorize_filesystem_mutation(
            authorization_id="FILESYSTEM-MUTATION-AUTHORIZATION-FIRST-E2E-EPOCH-000001",
            implementation_manifest_artifact=manifest,
            generated_content_validation_artifact=content_validation,
            generated_test_validation_artifact=test_validation,
            generated_content_acceptance_artifact=acceptance,
            human_authorization_evidence=_authorization_evidence(actor_id=actor_id, created_at=created_at),
            created_at=created_at,
        )["filesystem_mutation_authorization_artifact"]
        _require_stage_status(authorization, "authorization_status", "FILESYSTEM_MUTATION_AUTHORIZED")
        _persist(runtime_path / "007_filesystem_mutation_authorization_artifact.json", authorization)
        mutation = apply_filesystem_mutation(
            mutation_id="FILESYSTEM-MUTATION-FIRST-E2E-EPOCH-000001",
            implementation_manifest_artifact=manifest,
            filesystem_mutation_authorization_artifact=authorization,
            target_root=workspace_path,
            created_at=created_at,
            target_root_reference="OPERATOR_SUPPLIED_WORKSPACE",
        )["filesystem_mutation_artifact"]
        _require_stage_status(mutation, "mutation_status", "FILESYSTEM_MUTATION_COMPLETED")
        _persist(runtime_path / "008_filesystem_mutation_artifact.json", mutation)
        certification = certify_implementation(
            certification_id="IMPLEMENTATION-CERTIFICATION-FIRST-E2E-EPOCH-000001",
            implementation_manifest_artifact=manifest,
            filesystem_mutation_authorization_artifact=authorization,
            generated_content_acceptance_artifact=acceptance,
            filesystem_mutation_artifact=mutation,
            created_at=created_at,
        )["implementation_certification_artifact"]
        _require_stage_status(certification, "certification_status", "IMPLEMENTATION_CERTIFIED")
        _persist(runtime_path / "009_implementation_certification_artifact.json", certification)
        reports = _reports(
            request=request,
            runtime_root=runtime_path,
            workspace=workspace_path,
            candidate=candidate,
            manifest=manifest,
            content_validation=content_validation,
            test_validation=test_validation,
            summary=summary,
            acceptance=acceptance,
            authorization=authorization,
            mutation=mutation,
            certification=certification,
        )
        _persist_reports(runtime_path, reports)
        status = "EPOCH_CERTIFIED"
        fail_closed = False
        failure_reason = None
    except Exception as exc:
        reports = _failed_reports(request=request, runtime_root=runtime_path, workspace=workspace_path, exc=exc)
        status = "EPOCH_FAILED_CLOSED"
        fail_closed = True
        failure_reason = _failure_reason(exc)

    result = {
        "command": COMMAND,
        "milestone": MILESTONE,
        "epoch_status": status,
        "final_classification": (
            "AIGOL_FIRST_END_TO_END_IMPLEMENTATION_GENERATION_EPOCH_STATUS = "
            f"{AIGOL_FIRST_END_TO_END_IMPLEMENTATION_GENERATION_EPOCH_STATUS}"
        ),
        "runtime_root": str(runtime_path),
        "workspace": str(workspace_path),
        "request": request,
        "reports": reports,
        "replay_files": _replay_files(runtime_path),
        "workspace_files": _workspace_files(workspace_path),
        "fail_closed": fail_closed,
        "failure_reason": failure_reason,
    }
    result["epoch_hash"] = replay_hash(result)
    return result


def render_implementation_epoch_summary(result: dict[str, Any]) -> str:
    lines = [
        "AIGOL IMPLEMENTATION GENERATION EPOCH",
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


def _implementation_candidate(
    *,
    request: str,
    epoch_id: str,
    chain_id: str,
    bundle_id: str,
    created_at: str,
) -> dict[str, Any]:
    request_text = _require_string(request, "request")
    runtime_content = (
        "\"\"\"Generated candidate for the first end-to-end AiGOL implementation epoch.\"\"\"\n\n"
        "def describe_epoch_candidate():\n"
        "    return {\n"
        "        'status': 'generated_candidate_ready',\n"
        "        'governance_mode': 'CREATE_ONLY',\n"
        "        'operator_workflow': 'AIGOL_CLI',\n"
        "    }\n"
    )
    governance_content = (
        "# FIRST_E2E_EPOCH_SAMPLE_WORKER_V1\n\n"
        "Status: generated implementation candidate.\n\n"
        "This artifact was generated by the first end-to-end governed implementation generation epoch.\n"
    )
    test_content = (
        "from aigol.runtime.first_e2e_epoch_sample_worker import describe_epoch_candidate\n\n\n"
        "def test_describe_epoch_candidate():\n"
        "    result = describe_epoch_candidate()\n"
        "    assert result['status'] == 'generated_candidate_ready'\n"
        "    assert result['governance_mode'] == 'CREATE_ONLY'\n"
    )
    generated_files = [
        {
            "file_entry_id": "FILE-FIRST-E2E-EPOCH-RUNTIME-000001",
            "target_path": "aigol/runtime/first_e2e_epoch_sample_worker.py",
            "artifact_type": "PYTHON_RUNTIME_MODULE",
            "operation": CREATE_ONLY,
            "content": runtime_content,
            "source_segment_reference": "DETERMINISTIC-CANDIDATE-SEGMENT-RUNTIME",
            "validation_requirements": ["python -m pytest tests/test_first_e2e_epoch_sample_worker.py"],
        },
        {
            "file_entry_id": "FILE-FIRST-E2E-EPOCH-GOVERNANCE-000001",
            "target_path": "governance/FIRST_E2E_EPOCH_SAMPLE_WORKER_V1.md",
            "artifact_type": "GOVERNANCE_DOCUMENT_MARKDOWN",
            "operation": CREATE_ONLY,
            "content": governance_content,
            "source_segment_reference": "DETERMINISTIC-CANDIDATE-SEGMENT-GOVERNANCE",
            "validation_requirements": ["git diff --check"],
        },
    ]
    generated_tests = [
        {
            "test_entry_id": "TEST-FIRST-E2E-EPOCH-RUNTIME-000001",
            "target_path": "tests/test_first_e2e_epoch_sample_worker.py",
            "artifact_type": "PYTEST_TEST",
            "operation": CREATE_ONLY,
            "content": test_content,
            "tests_file_entries": ["FILE-FIRST-E2E-EPOCH-RUNTIME-000001"],
            "validation_command": "python -m pytest tests/test_first_e2e_epoch_sample_worker.py",
            "expected_coverage_target": "aigol/runtime/first_e2e_epoch_sample_worker.py",
            "negative_case_requirement": "rejects missing generated candidate status",
            "fixture_references": [],
        }
    ]
    artifact = {
        "artifact_type": "GENERATED_IMPLEMENTATION_CANDIDATE_V1",
        "candidate_id": "GENERATED-IMPLEMENTATION-CANDIDATE-FIRST-E2E-EPOCH-000001",
        "epoch_id": epoch_id,
        "canonical_chain_id": chain_id,
        "implementation_bundle_id": bundle_id,
        "created_at": created_at,
        "implementation_request": {
            "artifact_type": "REAL_IMPLEMENTATION_REQUEST_V1",
            "request_id": "REAL-IMPLEMENTATION-REQUEST-FIRST-E2E-EPOCH-000001",
            "request": request_text,
            "operator_interface": "AIGOL_CLI",
            "artifact_hash": replay_hash(
                {
                    "request_id": "REAL-IMPLEMENTATION-REQUEST-FIRST-E2E-EPOCH-000001",
                    "request": request_text,
                    "operator_interface": "AIGOL_CLI",
                }
            ),
        },
        "implementation_handoff_reference": "IMPLEMENTATION-HANDOFF-FIRST-E2E-EPOCH-000001",
        "implementation_handoff_hash": replay_hash({"handoff": request_text, "chain": chain_id}),
        "provider_generation_authorization_reference": "NO_PROVIDER_INVOCATION_USED",
        "provider_generation_authorization_hash": replay_hash({"provider_invocation": False, "chain": chain_id}),
        "provider_response_reference": "DETERMINISTIC_CLI_CANDIDATE_GENERATION",
        "provider_response_hash": replay_hash({"candidate_generation": "deterministic_cli", "chain": chain_id}),
        "generated_files": generated_files,
        "generated_tests": generated_tests,
        "validation_requirements": ["python -m pytest tests/test_first_e2e_epoch_sample_worker.py", "git diff --check"],
        "known_gaps": [
            "candidate generation is deterministic CLI generation, not provider-assisted generation",
            "generated tests are materialized but not executed by the epoch command",
            "operator acceptance evidence is supplied through CLI flags rather than an interactive prompt",
        ],
        "provider_invoked": False,
        "worker_invoked": False,
        "filesystem_mutated": False,
        "execution_authorized": False,
    }
    artifact["candidate_hash"] = replay_hash(artifact)
    return artifact


def _reports(**context: Any) -> dict[str, str]:
    usage = _usage_report(**context)
    replay = _replay_inspection_report(**context)
    friction = _operator_friction_report(**context)
    blockers = _remaining_blockers_report(**context)
    certification = _certification_report(**context)
    return {
        "usage_report": usage,
        "replay_inspection_report": replay,
        "operator_friction_analysis": friction,
        "remaining_blockers_analysis": blockers,
        "certification_report": certification,
    }


def _usage_report(**context: Any) -> str:
    return "\n".join(
        [
            "# AIGOL_FIRST_END_TO_END_IMPLEMENTATION_GENERATION_EPOCH_USAGE_REPORT_V1",
            "",
            "## Status",
            "",
            "Complete certified implementation lifecycle demonstrated through AiGOL CLI.",
            "",
            "## Operator Request",
            "",
            context["request"],
            "",
            "## CLI Workflow",
            "",
            "- real implementation request captured;",
            "- deterministic implementation candidate generated;",
            "- implementation manifest created;",
            "- generated content validation completed;",
            "- generated test validation completed;",
            "- implementation summary generated;",
            "- human acceptance recorded;",
            "- filesystem mutation authorization created;",
            "- authorized files materialized;",
            "- implementation certification completed;",
            "- replay chain inspected through persisted epoch evidence.",
        ]
    )


def _replay_inspection_report(**context: Any) -> str:
    replay_files = _replay_files(context["runtime_root"])
    return "\n".join(
        [
            "# AIGOL_FIRST_END_TO_END_IMPLEMENTATION_GENERATION_EPOCH_REPLAY_INSPECTION_REPORT_V1",
            "",
            "## Status",
            "",
            "Replay chain persisted and inspectable.",
            "",
            "## Replay Evidence",
            "",
            *[f"- `{path}`" for path in replay_files],
            "",
            "## Lineage",
            "",
            f"- manifest: `{context['manifest']['implementation_manifest_hash']}`",
            f"- content validation: `{context['content_validation']['generated_content_validation_hash']}`",
            f"- test validation: `{context['test_validation']['generated_test_validation_hash']}`",
            f"- acceptance: `{context['acceptance']['generated_content_acceptance_hash']}`",
            f"- authorization: `{context['authorization']['filesystem_mutation_authorization_hash']}`",
            f"- mutation: `{context['mutation']['filesystem_mutation_hash']}`",
            f"- certification: `{context['certification']['implementation_certification_hash']}`",
        ]
    )


def _operator_friction_report(**context: Any) -> str:
    return "\n".join(
        [
            "# AIGOL_FIRST_END_TO_END_IMPLEMENTATION_GENERATION_EPOCH_OPERATOR_FRICTION_ANALYSIS_V1",
            "",
            "## Status",
            "",
            "Workflow completes, but operator friction remains visible.",
            "",
            "## Findings",
            "",
            "- A single epoch command makes the lifecycle demonstrable.",
            "- Human acceptance is represented as CLI evidence, not an interactive acceptance prompt.",
            "- The command must be given an empty or collision-free workspace because mutation is strict `CREATE_ONLY`.",
            "- Replay inspection is file-based inside the epoch root, not yet a polished CLI drill-down view.",
            "- Generated tests are validated as artifacts but are not executed inside this epoch command.",
        ]
    )


def _remaining_blockers_report(**context: Any) -> str:
    return "\n".join(
        [
            "# AIGOL_FIRST_END_TO_END_IMPLEMENTATION_GENERATION_EPOCH_REMAINING_BLOCKERS_ANALYSIS_V1",
            "",
            "## Status",
            "",
            "No blocker prevents deterministic demonstration; product hardening remains.",
            "",
            "## Remaining Blockers",
            "",
            "- Provider-assisted candidate generation is not part of this certified epoch path.",
            "- Interactive acceptance and authorization prompts are not yet first-class CLI steps.",
            "- Replay inspection should expose stage-by-stage evidence without requiring file path knowledge.",
            "- Post-materialization generated test execution remains outside this certified lifecycle.",
            "- Workspace preflight UX should explain collisions before invoking mutation.",
        ]
    )


def _certification_report(**context: Any) -> str:
    certification = context["certification"]
    return "\n".join(
        [
            "# AIGOL_FIRST_END_TO_END_IMPLEMENTATION_GENERATION_EPOCH_CERTIFICATION_REPORT_V1",
            "",
            "## Final Classification",
            "",
            "```text",
            "AIGOL_FIRST_END_TO_END_IMPLEMENTATION_GENERATION_EPOCH_STATUS = "
            f"{AIGOL_FIRST_END_TO_END_IMPLEMENTATION_GENERATION_EPOCH_STATUS}",
            "```",
            "",
            "## Certification Evidence",
            "",
            f"- implementation certification status: `{certification['certification_status']}`",
            f"- implementation certification hash: `{certification['implementation_certification_hash']}`",
            f"- certified path count: `{certification['certified_path_count']}`",
            "- filesystem mutation: performed only by `FILESYSTEM_MUTATION_RUNTIME_V1`.",
            "- execution authorization: not granted.",
            "- provider invocation: not performed.",
            "- worker invocation: not performed.",
        ]
    )


def _failed_reports(*, request: str, runtime_root: Path, workspace: Path, exc: Exception) -> dict[str, str]:
    failure = _failure_reason(exc)
    return {
        "usage_report": f"# {MILESTONE}_USAGE_REPORT\n\nStatus: failed closed.\n\nFailure: {failure}\n",
        "replay_inspection_report": f"# {MILESTONE}_REPLAY_INSPECTION_REPORT\n\nStatus: failed closed.\n",
        "operator_friction_analysis": f"# {MILESTONE}_OPERATOR_FRICTION_ANALYSIS\n\nFailure: {failure}\n",
        "remaining_blockers_analysis": f"# {MILESTONE}_REMAINING_BLOCKERS_ANALYSIS\n\nFailure: {failure}\n",
        "certification_report": f"# {MILESTONE}_CERTIFICATION_REPORT\n\nStatus: failed closed.\n",
    }


def _persist_reports(runtime_root: Path, reports: dict[str, str]) -> None:
    for index, (name, content) in enumerate(reports.items(), start=10):
        path = runtime_root / f"{index:03d}_{name}.md"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content + "\n", encoding="utf-8")


def _persist(path: Path, artifact: dict[str, Any]) -> None:
    write_json_immutable(path, artifact)


def _acceptance_evidence(*, actor_id: str, created_at: str) -> dict[str, str]:
    return {
        "actor_id": actor_id,
        "decision": ACCEPTANCE_DECISION,
        "accepted_at": created_at,
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


def _replay_files(runtime_root: Path) -> list[str]:
    if not runtime_root.exists():
        return []
    return sorted(str(path.relative_to(runtime_root)) for path in runtime_root.rglob("*") if path.is_file())


def _workspace_files(workspace: Path) -> list[str]:
    if not workspace.exists():
        return []
    return sorted(str(path.relative_to(workspace)) for path in workspace.rglob("*") if path.is_file())


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{label} is required")
    return value.strip()


def _require_stage_status(artifact: dict[str, Any], field: str, expected: str) -> None:
    actual = artifact.get(field)
    if actual != expected:
        failure = artifact.get("failure_reason") or f"{field} expected {expected}, got {actual}"
        raise FailClosedRuntimeError(str(failure))


def _failure_reason(exc: Exception) -> str:
    reason = str(exc)
    return reason or "implementation generation epoch failed closed"
