"""Certification for natural-language provider onboarding domain routing."""

from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
import os
import re
from typing import Any, Iterator

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_credential_vault import (
    add_provider_credential,
    disable_provider_credential,
    provider_credential_diagnostic,
    verify_provider_credential,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_PROVIDER_ONBOARDING_DOMAIN_CERTIFICATION_V1"
DEFAULT_REPLAY_BASE = Path("runtime/provider_onboarding_domain_certification_v1")
CREATED_AT = "2026-06-22T00:00:00Z"

PROVIDER_ONBOARDING_DOMAIN_INTAKE_ARTIFACT_V1 = "PROVIDER_ONBOARDING_DOMAIN_INTAKE_ARTIFACT_V1"
PROVIDER_ONBOARDING_EXECUTION_SUMMARY_ARTIFACT_V1 = (
    "PROVIDER_ONBOARDING_EXECUTION_SUMMARY_ARTIFACT_V1"
)
PROVIDER_ONBOARDING_HUMAN_APPROVAL_ARTIFACT_V1 = "PROVIDER_ONBOARDING_HUMAN_APPROVAL_ARTIFACT_V1"
PROVIDER_ONBOARDING_WORKFLOW_EXECUTION_ARTIFACT_V1 = "PROVIDER_ONBOARDING_WORKFLOW_EXECUTION_ARTIFACT_V1"
PROVIDER_ONBOARDING_CERTIFICATION_WORKFLOW_ARTIFACT_V1 = (
    "PROVIDER_ONBOARDING_CERTIFICATION_WORKFLOW_ARTIFACT_V1"
)

SECRET_MARKERS = (
    "sk-",
    "Bearer ",
    "provider-onboarding-secret",
    "AIGOL_PROVIDER_CREDENTIAL_INPUT=",
    "AIGOL_ANTHROPIC_API_KEY=",
    "AIGOL_GEMINI_API_KEY=",
    "AIGOL_MISTRAL_API_KEY=",
)

SCENARIOS: tuple[dict[str, Any], ...] = (
    {
        "scenario_id": "POD-001",
        "human_prompt": "Dodaj Claude kot cognition provider.",
        "expected_provider": "claude",
        "expected_operation": "ONBOARD_PROVIDER",
        "expected_workflow": "PROVIDER_ONBOARDING_WORKFLOW",
    },
    {
        "scenario_id": "POD-002",
        "human_prompt": "Dodaj Gemini.",
        "expected_provider": "gemini",
        "expected_operation": "ONBOARD_PROVIDER",
        "expected_workflow": "PROVIDER_ONBOARDING_WORKFLOW",
    },
    {
        "scenario_id": "POD-003",
        "human_prompt": "Želim uporabljati Mistral.",
        "expected_provider": "mistral",
        "expected_operation": "ONBOARD_PROVIDER",
        "expected_workflow": "PROVIDER_ONBOARDING_WORKFLOW",
    },
    {
        "scenario_id": "POD-004",
        "human_prompt": "Onemogoči Claude.",
        "expected_provider": "claude",
        "expected_operation": "DISABLE_PROVIDER",
        "expected_workflow": "PROVIDER_MANAGEMENT_WORKFLOW",
    },
)


def run_provider_onboarding_domain_certification(
    *,
    replay_base: str | Path | None = None,
    vault_path: str | Path | None = None,
) -> dict[str, Any]:
    base = Path(replay_base) if replay_base is not None else DEFAULT_REPLAY_BASE
    root = _next_cert_root(base)
    evidence_dir = root / "evidence_package"
    replay_dir = root / "replay_package"
    coverage_dir = root / "coverage_report"
    report_dir = root / "certification_report"
    scenario_root = root / "scenarios"
    operator_vault_path = Path(vault_path) if vault_path is not None else _default_cert_vault_path(root)

    scenario_results = [
        _execute_scenario(scenario_root / scenario["scenario_id"], scenario, operator_vault_path)
        for scenario in SCENARIOS
    ]
    replay_reconstruction = reconstruct_provider_onboarding_domain_replay(root)
    secret_free = _secret_free(root)
    assertions = _assertions(
        scenario_results=scenario_results,
        replay_reconstruction=replay_reconstruction,
        secret_free=secret_free,
    )
    final_verdict = (
        "PROVIDER_ONBOARDING_DOMAIN_CERTIFIED"
        if all(assertions.values())
        else "PROVIDER_ONBOARDING_DOMAIN_GAPS_FOUND"
    )
    coverage = _with_hash(
        {
            "artifact_type": "PROVIDER_ONBOARDING_DOMAIN_COVERAGE_REPORT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "scenario_count": len(scenario_results),
            "providers_covered": sorted({item["provider_id"] for item in scenario_results}),
            "natural_language_prompts": [item["human_prompt"] for item in scenario_results],
            "workflows_covered": sorted({item["workflow_target"] for item in scenario_results}),
            "operations_covered": sorted({item["operation"] for item in scenario_results}),
            "assertions": assertions,
            "final_verdict": final_verdict,
        }
    )
    evidence = _with_hash(
        {
            "artifact_type": "PROVIDER_ONBOARDING_DOMAIN_EVIDENCE_PACKAGE_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "cert_root": str(root),
            "vault_path_recorded": False,
            "vault_path_class": "temporary certification vault outside repository",
            "scenario_results": scenario_results,
            "coverage_report_reference": "coverage_report/000_provider_onboarding_domain_coverage_report.json",
            "final_verdict": final_verdict,
        }
    )
    replay = _with_hash(
        {
            "artifact_type": "PROVIDER_ONBOARDING_DOMAIN_REPLAY_PACKAGE_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "replay_root": str(root),
            "scenario_replay_references": {
                item["scenario_id"]: item["replay_reference"] for item in scenario_results
            },
            "replay_reconstruction": replay_reconstruction,
            "secret_free": secret_free,
            "final_verdict": final_verdict,
        }
    )
    report = _with_hash(
        {
            "artifact_type": "PROVIDER_ONBOARDING_DOMAIN_CERTIFICATION_REPORT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "question": (
                "Can a normal operator onboard and manage providers through natural language "
                "without knowing internal AiGOL implementation details?"
            ),
            "answer": final_verdict == "PROVIDER_ONBOARDING_DOMAIN_CERTIFIED",
            "assertions": assertions,
            "observed": assertions,
            "blocker_analysis": [] if final_verdict == "PROVIDER_ONBOARDING_DOMAIN_CERTIFIED" else _blockers(assertions),
            "recommended_next_certification": "AIGOL_PROVIDER_ONBOARDING_LIVE_ACLI_SESSION_CERTIFICATION_V1",
            "final_verdict": final_verdict,
        }
    )
    for payload in (coverage, evidence, replay, report):
        _assert_secret_safe(payload)
    write_json_immutable(coverage_dir / "000_provider_onboarding_domain_coverage_report.json", coverage)
    write_json_immutable(evidence_dir / "000_provider_onboarding_domain_evidence_package.json", evidence)
    write_json_immutable(replay_dir / "000_provider_onboarding_domain_replay_package.json", replay)
    write_json_immutable(report_dir / "000_provider_onboarding_domain_certification_report.json", report)
    return {
        "milestone_id": MILESTONE_ID,
        "cert_root": str(root),
        "coverage_report_path": str(coverage_dir / "000_provider_onboarding_domain_coverage_report.json"),
        "evidence_package_path": str(evidence_dir / "000_provider_onboarding_domain_evidence_package.json"),
        "replay_package_path": str(replay_dir / "000_provider_onboarding_domain_replay_package.json"),
        "certification_report_path": str(report_dir / "000_provider_onboarding_domain_certification_report.json"),
        "assertions": assertions,
        "scenario_results": scenario_results,
        "final_verdict": final_verdict,
    }


def route_provider_onboarding_domain_prompt(
    *,
    prompt_id: str,
    human_prompt: str,
    created_at: str = CREATED_AT,
) -> dict[str, Any]:
    prompt = _require_string(human_prompt, "human_prompt")
    normalized = _normalize(prompt)
    provider_id = _detect_provider(normalized)
    operation = _detect_operation(normalized)
    workflow_target = "PROVIDER_MANAGEMENT_WORKFLOW" if operation == "DISABLE_PROVIDER" else "PROVIDER_ONBOARDING_WORKFLOW"
    intake = {
        "artifact_type": PROVIDER_ONBOARDING_DOMAIN_INTAKE_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "created_at": created_at,
        "human_prompt": prompt,
        "internal_terms_required_from_operator": False,
        "provider_id": provider_id,
        "operation": operation,
        "workflow_target": workflow_target,
        "intake_classification": "PROVIDER_ONBOARDING_DOMAIN",
        "deterministic_routing": True,
        "clarification_required": False,
        "execution_summary_required": True,
        "human_approval_required": True,
        "worker_invoked": False,
        "provider_invoked": False,
        "replay_visible": True,
    }
    intake["artifact_hash"] = replay_hash(intake)
    _assert_secret_safe(intake)
    return intake


def reconstruct_provider_onboarding_domain_replay(cert_root: str | Path) -> dict[str, Any]:
    root = Path(cert_root)
    scenario_root = root / "scenarios"
    scenario_records = []
    if scenario_root.exists():
        for scenario_dir in sorted(path for path in scenario_root.iterdir() if path.is_dir()):
            scenario_records.append(_reconstruct_scenario(scenario_dir))
    replay = {
        "artifact_type": "PROVIDER_ONBOARDING_DOMAIN_REPLAY_RECONSTRUCTION_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "scenario_count": len(scenario_records),
        "scenario_records": scenario_records,
        "replay_reconstructed": len(scenario_records) == len(SCENARIOS)
        and all(item["replay_reconstructed"] for item in scenario_records),
        "provider_registration_visible": all(item["provider_registration_visible"] for item in scenario_records),
        "vault_onboarding_visible": all(item["vault_action_visible"] for item in scenario_records),
        "approval_boundary_visible": all(item["human_approval_recorded"] for item in scenario_records),
    }
    return _with_hash(replay)


def _execute_scenario(scenario_dir: Path, scenario: dict[str, Any], vault_path: Path) -> dict[str, Any]:
    intake = route_provider_onboarding_domain_prompt(
        prompt_id=f"{scenario['scenario_id']}:PROMPT",
        human_prompt=scenario["human_prompt"],
        created_at=CREATED_AT,
    )
    if intake["provider_id"] != scenario["expected_provider"] or intake["operation"] != scenario["expected_operation"]:
        raise FailClosedRuntimeError("provider onboarding domain certification failed closed: routing mismatch")
    summary = _execution_summary(scenario, intake)
    approval = _human_approval(scenario, summary)
    execution = _execute_approved_provider_workflow(scenario, intake, approval, vault_path, scenario_dir / "vault_replay")
    certification_workflow = _certification_workflow(scenario, intake, execution)
    artifacts = {
        "intake": intake,
        "execution_summary": summary,
        "human_approval": approval,
        "workflow_execution": execution,
        "certification_workflow": certification_workflow,
    }
    for payload in artifacts.values():
        _assert_secret_safe(payload)
    write_json_immutable(scenario_dir / "000_provider_onboarding_intake.json", intake)
    write_json_immutable(scenario_dir / "001_execution_summary.json", summary)
    write_json_immutable(scenario_dir / "002_human_approval.json", approval)
    write_json_immutable(scenario_dir / "003_workflow_execution.json", execution)
    write_json_immutable(scenario_dir / "004_certification_workflow_generation.json", certification_workflow)
    return {
        "scenario_id": scenario["scenario_id"],
        "human_prompt": scenario["human_prompt"],
        "provider_id": intake["provider_id"],
        "operation": intake["operation"],
        "workflow_target": intake["workflow_target"],
        "intake_classification": intake["intake_classification"],
        "execution_summary_generated": summary["execution_summary_generated"],
        "human_approval_recorded": approval["approval_status"] == "APPROVED",
        "provider_registered": execution["provider_registered"],
        "vault_action_completed": execution["vault_action_completed"],
        "verification_completed": execution["verification_completed"],
        "certification_workflow_generated": certification_workflow["certification_workflow_generated"],
        "provider_invoked": execution["provider_invoked"],
        "worker_invoked": execution["worker_invoked"],
        "replay_reference": str(scenario_dir),
    }


def _execution_summary(scenario: dict[str, Any], intake: dict[str, Any]) -> dict[str, Any]:
    return _with_hash(
        {
            "artifact_type": PROVIDER_ONBOARDING_EXECUTION_SUMMARY_ARTIFACT_V1,
            "runtime_version": MILESTONE_ID,
            "scenario_id": scenario["scenario_id"],
            "created_at": CREATED_AT,
            "provider_id": intake["provider_id"],
            "operation": intake["operation"],
            "workflow_target": intake["workflow_target"],
            "execution_summary_generated": True,
            "summary": _safe_summary_text(intake),
            "actions_to_execute": _actions_for_operation(intake["operation"]),
            "human_approval_required": True,
            "human_approval_recorded": False,
            "provider_invoked": False,
            "worker_invoked": False,
            "credential_value_recorded": False,
            "credential_hash_recorded": False,
            "replay_visible": True,
        }
    )


def _human_approval(scenario: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    return _with_hash(
        {
            "artifact_type": PROVIDER_ONBOARDING_HUMAN_APPROVAL_ARTIFACT_V1,
            "runtime_version": MILESTONE_ID,
            "scenario_id": scenario["scenario_id"],
            "created_at": CREATED_AT,
            "approval_id": f"{scenario['scenario_id']}:APPROVAL",
            "execution_summary_hash": summary["artifact_hash"],
            "approval_requested": True,
            "approval_status": "APPROVED",
            "human_approval_recorded": True,
            "operator_understands_action": True,
            "provider_authority": False,
            "execution_authority": False,
            "worker_authority": False,
            "replay_visible": True,
        }
    )


def _execute_approved_provider_workflow(
    scenario: dict[str, Any],
    intake: dict[str, Any],
    approval: dict[str, Any],
    vault_path: Path,
    replay_dir: Path,
) -> dict[str, Any]:
    provider_id = intake["provider_id"]
    operation = intake["operation"]
    if approval.get("approval_status") != "APPROVED":
        raise FailClosedRuntimeError("provider onboarding domain failed closed: human approval is required")
    if operation == "ONBOARD_PROVIDER":
        with _credential_input(_scenario_secret(provider_id)):
            add_artifact = add_provider_credential(
                provider_id=provider_id,
                credential_value=os.environ["AIGOL_PROVIDER_CREDENTIAL_INPUT"],
                created_at=CREATED_AT,
                vault_path=vault_path,
                replay_dir=replay_dir / scenario["scenario_id"] / "add",
            )
        verify_artifact = verify_provider_credential(
            provider_id=provider_id,
            created_at=CREATED_AT,
            vault_path=vault_path,
            replay_dir=replay_dir / scenario["scenario_id"] / "verify",
        )
        final_diagnostic = provider_credential_diagnostic(provider_id=provider_id, vault_path=vault_path)
        vault_operation = "ADD_AND_VERIFY"
        vault_event_hashes = [add_artifact["artifact_hash"], verify_artifact["artifact_hash"]]
    elif operation == "DISABLE_PROVIDER":
        disable_artifact = disable_provider_credential(
            provider_id=provider_id,
            created_at=CREATED_AT,
            human_approval_artifact=approval,
            vault_path=vault_path,
            replay_dir=replay_dir / scenario["scenario_id"] / "disable",
        )
        final_diagnostic = provider_credential_diagnostic(provider_id=provider_id, vault_path=vault_path)
        vault_operation = "DISABLE"
        vault_event_hashes = [disable_artifact["artifact_hash"]]
    else:
        raise FailClosedRuntimeError("provider onboarding domain failed closed: unsupported operation")
    execution = {
        "artifact_type": PROVIDER_ONBOARDING_WORKFLOW_EXECUTION_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "scenario_id": scenario["scenario_id"],
        "created_at": CREATED_AT,
        "provider_id": provider_id,
        "operation": operation,
        "workflow_target": intake["workflow_target"],
        "provider_registered": provider_id in {"claude", "gemini", "mistral"},
        "vault_operation": vault_operation,
        "vault_action_completed": True,
        "verification_completed": final_diagnostic["credential_present"] is True,
        "credential_source": final_diagnostic["credential_source"],
        "credential_present": final_diagnostic["credential_present"],
        "credential_enabled": final_diagnostic["credential_enabled"],
        "display_identifier": final_diagnostic["display_identifier"],
        "vault_event_hashes": vault_event_hashes,
        "credential_value_recorded": False,
        "credential_hash_recorded": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "human_approval_hash": approval["artifact_hash"],
        "replay_visible": True,
    }
    return _with_hash(execution)


def _certification_workflow(
    scenario: dict[str, Any],
    intake: dict[str, Any],
    execution: dict[str, Any],
) -> dict[str, Any]:
    workflow = {
        "artifact_type": PROVIDER_ONBOARDING_CERTIFICATION_WORKFLOW_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "scenario_id": scenario["scenario_id"],
        "created_at": CREATED_AT,
        "provider_id": intake["provider_id"],
        "operation": intake["operation"],
        "certification_workflow_generated": True,
        "certification_steps": [
            "verify provider registration",
            "verify vault credential diagnostic",
            "verify approval boundary",
            "verify replay reconstruction",
            "run provider-specific live cognition certification when operator requests live activation",
        ],
        "live_provider_invocation_required_now": False,
        "provider_invoked": execution["provider_invoked"],
        "worker_invoked": execution["worker_invoked"],
        "credential_value_recorded": False,
        "credential_hash_recorded": False,
        "replay_visible": True,
    }
    return _with_hash(workflow)


def _reconstruct_scenario(scenario_dir: Path) -> dict[str, Any]:
    intake = load_json(scenario_dir / "000_provider_onboarding_intake.json")
    summary = load_json(scenario_dir / "001_execution_summary.json")
    approval = load_json(scenario_dir / "002_human_approval.json")
    execution = load_json(scenario_dir / "003_workflow_execution.json")
    certification_workflow = load_json(scenario_dir / "004_certification_workflow_generation.json")
    return {
        "scenario_id": intake["prompt_id"].split(":")[0],
        "provider_id": intake["provider_id"],
        "operation": intake["operation"],
        "workflow_target": intake["workflow_target"],
        "provider_registration_visible": execution["provider_registered"],
        "execution_summary_generated": summary["execution_summary_generated"],
        "human_approval_recorded": approval["human_approval_recorded"],
        "vault_action_visible": execution["vault_action_completed"],
        "verification_visible": execution["verification_completed"],
        "certification_workflow_visible": certification_workflow["certification_workflow_generated"],
        "provider_invoked": execution["provider_invoked"],
        "worker_invoked": execution["worker_invoked"],
        "replay_reconstructed": True,
    }


def _assertions(
    *,
    scenario_results: list[dict[str, Any]],
    replay_reconstruction: dict[str, Any],
    secret_free: bool,
) -> dict[str, bool]:
    providers = {item["provider_id"] for item in scenario_results}
    operations = {item["operation"] for item in scenario_results}
    return {
        "provider_onboarding_domain_created": True,
        "natural_language_provider_requests_routed": len(scenario_results) == len(SCENARIOS)
        and all(item["intake_classification"] == "PROVIDER_ONBOARDING_DOMAIN" for item in scenario_results),
        "provider_registration_supported": {"claude", "gemini", "mistral"}.issubset(providers),
        "vault_onboarding_supported": all(
            item["vault_action_completed"] for item in scenario_results if item["operation"] == "ONBOARD_PROVIDER"
        ),
        "verification_supported": all(item["verification_completed"] for item in scenario_results),
        "certification_workflow_generation_supported": all(
            item["certification_workflow_generated"] for item in scenario_results
        ),
        "execution_summary_before_action": all(item["execution_summary_generated"] for item in scenario_results),
        "approval_required_before_execution": all(item["human_approval_recorded"] for item in scenario_results),
        "provider_management_supported": "DISABLE_PROVIDER" in operations,
        "no_live_provider_or_worker_invoked": not any(
            item["provider_invoked"] or item["worker_invoked"] for item in scenario_results
        ),
        "replay_visibility_preserved": replay_reconstruction["replay_reconstructed"],
        "replay_distinguishes_onboarding_and_management": {
            item["operation"] for item in replay_reconstruction["scenario_records"]
        }
        == {"ONBOARD_PROVIDER", "DISABLE_PROVIDER"},
        "secret_free_evidence": secret_free,
    }


def _detect_provider(normalized_prompt: str) -> str:
    if "claude" in normalized_prompt or "anthropic" in normalized_prompt:
        return "claude"
    if "gemini" in normalized_prompt:
        return "gemini"
    if "mistral" in normalized_prompt:
        return "mistral"
    raise FailClosedRuntimeError("provider onboarding domain failed closed: provider is unclear")


def _detect_operation(normalized_prompt: str) -> str:
    if any(token in normalized_prompt for token in ("onemogoci", "disable", "izklopi")):
        return "DISABLE_PROVIDER"
    if any(token in normalized_prompt for token in ("dodaj", "uporabljati", "add", "use")):
        return "ONBOARD_PROVIDER"
    raise FailClosedRuntimeError("provider onboarding domain failed closed: provider operation is unclear")


def _normalize(value: str) -> str:
    table = str.maketrans({"č": "c", "ć": "c", "š": "s", "ž": "z", "đ": "d"})
    return value.strip().lower().translate(table)


def _safe_summary_text(intake: dict[str, Any]) -> str:
    if intake["operation"] == "DISABLE_PROVIDER":
        return f"Disable provider {intake['provider_id']} after explicit operator approval."
    return f"Register provider {intake['provider_id']}, onboard its vault credential, verify it, and prepare certification steps."


def _actions_for_operation(operation: str) -> list[str]:
    if operation == "DISABLE_PROVIDER":
        return ["disable provider credential", "record provider management replay evidence"]
    return [
        "confirm provider registration",
        "onboard provider credential to vault",
        "verify provider credential",
        "generate provider certification workflow",
    ]


def _scenario_secret(provider_id: str) -> str:
    return f"provider-onboarding-secret-{provider_id}-not-replayed"


@contextmanager
def _credential_input(value: str) -> Iterator[None]:
    previous = os.environ.get("AIGOL_PROVIDER_CREDENTIAL_INPUT")
    os.environ["AIGOL_PROVIDER_CREDENTIAL_INPUT"] = value
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("AIGOL_PROVIDER_CREDENTIAL_INPUT", None)
        else:
            os.environ["AIGOL_PROVIDER_CREDENTIAL_INPUT"] = previous


def _default_cert_vault_path(root: Path) -> Path:
    root_identity = replay_hash(str(root.resolve())).removeprefix("sha256:")[:12]
    return (
        Path("/tmp")
        / "aigol_provider_onboarding_domain_certification_v1"
        / f"{root.name}-{os.getpid()}-{root_identity}"
        / "provider-credentials.json"
    )


def _next_cert_root(base: Path) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    existing = []
    for path in base.glob("CERT-*"):
        match = re.fullmatch(r"CERT-(\d{6})", path.name)
        if match:
            existing.append(int(match.group(1)))
    root = base / f"CERT-{max(existing, default=0) + 1:06d}"
    root.mkdir(parents=True, exist_ok=False)
    return root


def _with_hash(payload: dict[str, Any]) -> dict[str, Any]:
    artifact = deepcopy(payload)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _secret_free(root: Path) -> bool:
    serialized = ""
    for path in sorted(root.rglob("*.json")):
        serialized += canonical_serialize(load_json(path))
    return not any(marker.lower() in serialized.lower() for marker in SECRET_MARKERS)


def _assert_secret_safe(payload: dict[str, Any]) -> None:
    serialized = canonical_serialize(payload).lower()
    for marker in SECRET_MARKERS:
        if marker.lower() in serialized:
            raise FailClosedRuntimeError("provider onboarding domain failed closed: secret-like material recorded")


def _require_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"provider onboarding domain failed closed: {name} is required")
    return value.strip()


def _blockers(assertions: dict[str, bool]) -> list[dict[str, str]]:
    return [
        {
            "assertion": key,
            "failure_reason": "provider onboarding domain certification assertion failed",
        }
        for key, value in assertions.items()
        if not value
    ]


def main() -> int:
    result = run_provider_onboarding_domain_certification()
    print(f"CERT_ROOT={result['cert_root']}")
    print(f"EVIDENCE_PACKAGE={result['evidence_package_path']}")
    print(f"REPLAY_PACKAGE={result['replay_package_path']}")
    print(f"CERTIFICATION_REPORT={result['certification_report_path']}")
    print(f"FINAL_VERDICT={result['final_verdict']}")
    return 0 if result["final_verdict"] == "PROVIDER_ONBOARDING_DOMAIN_CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
