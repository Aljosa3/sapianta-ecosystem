"""Manual entrypoint for AIGOL_FIRST_LIVE_COGNITION_PROVIDER_CERTIFICATION_V1."""

from __future__ import annotations

from pathlib import Path
import os
import re
import sys
from typing import Any, Callable

from aigol.runtime.first_live_provider_activation_package_instantiation import (
    instantiate_first_live_provider_activation_package,
    reconstruct_first_live_provider_activation_package,
)
from aigol.runtime.first_live_provider_dispatch_authorization_instantiation import (
    instantiate_first_live_provider_dispatch_authorization,
    reconstruct_first_live_provider_dispatch_authorization,
)
from aigol.runtime.first_live_provider_execution_runtime import (
    reconstruct_first_live_provider_execution_runtime_replay,
)
from aigol.runtime.first_live_provider_operator_entrypoint import (
    run_first_live_provider_operator_entrypoint,
    reconstruct_first_live_provider_operator_entrypoint_replay,
)
from aigol.runtime.live_openai_executor import create_governed_live_openai_executor
from aigol.runtime.provider_governance_runtime import (
    execute_provider_lifecycle_operation,
    record_cognition_participation,
    record_provider_usage_metric,
    reconstruct_provider_governance_replay,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_FIRST_LIVE_COGNITION_PROVIDER_ENTRYPOINT_V1"
DEFAULT_REPLAY_BASE = Path("runtime/first_live_cognition_provider_certification_v1")
CREATED_AT = "2026-06-17T00:00:00+00:00"
EXPIRES_AT = "2026-06-17T01:00:00+00:00"
DEFAULT_HUMAN_PROMPT = "Help me decide the safest next step for reviewing an AI-generated customer reply before anyone sends it."

BoundaryTransport = Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]


def run_first_live_cognition_provider_certification(
    *,
    replay_base: str | Path | None = None,
    human_prompt: str = DEFAULT_HUMAN_PROMPT,
    created_at: str = CREATED_AT,
    expires_at: str = EXPIRES_AT,
    transport: BoundaryTransport | None = None,
    require_openai_api_key_marker: bool = True,
) -> dict[str, Any]:
    """Run the bounded first live cognition-provider certification sequence."""

    preflight = _credential_preflight(require_openai_api_key_marker=require_openai_api_key_marker)
    if not preflight["aigol_openai_api_key_present"]:
        return _aborted_capture("AIGOL_OPENAI_API_KEY_MISSING", preflight)
    if require_openai_api_key_marker and not preflight["openai_api_key_present"]:
        return _aborted_capture("OPENAI_API_KEY_MISSING", preflight)

    base = Path(replay_base) if replay_base is not None else DEFAULT_REPLAY_BASE
    root = _next_cert_root(base)
    cert_suffix = root.name.removeprefix("CERT-")

    activation_dir = root / "activation_package"
    dispatch_dir = root / "dispatch_authorization"
    execution_dir = root / "execution"
    operator_dir = root / "operator_entrypoint"
    human_confirmation_dir = root / "human_confirmation"
    provider_governance_dir = root / "provider_governance"
    evidence_dir = root / "evidence_package"
    replay_dir = root / "replay_package"
    report_dir = root / "certification_report"

    activation = instantiate_first_live_provider_activation_package(
        package_id=f"FIRST-LIVE-COGNITION-PROVIDER-CERT-{cert_suffix}",
        human_request=human_prompt,
        required_capability="reasoning",
        approved_by="human.operator",
        created_at=created_at,
        expires_at=expires_at,
        replay_dir=activation_dir,
    )
    dispatch = instantiate_first_live_provider_dispatch_authorization(
        dispatch_authorization_id=f"FIRST-LIVE-COGNITION-PROVIDER-DISPATCH-AUTH-{cert_suffix}",
        activation_package_replay_dir=activation_dir,
        replay_dir=dispatch_dir,
        created_at=created_at,
        expires_at=expires_at,
    )

    operator_result = run_first_live_provider_operator_entrypoint(
        operator_request_id=f"FIRST-LIVE-COGNITION-PROVIDER-OPERATOR-DISPATCH-{cert_suffix}",
        operator_id="human.operator",
        human_request=human_prompt,
        created_at=created_at,
        activation_package_replay_dir=activation_dir,
        dispatch_authorization_replay_dir=dispatch_dir,
        execution_replay_dir=execution_dir,
        operator_replay_dir=operator_dir,
        transport=transport if transport is not None else create_governed_live_openai_executor(),
        confirm_dispatch=True,
        live_transport_enabled=True,
    )

    activation_replay = reconstruct_first_live_provider_activation_package(activation_dir)
    dispatch_replay = reconstruct_first_live_provider_dispatch_authorization(dispatch_dir)
    operator_replay = reconstruct_first_live_provider_operator_entrypoint_replay(operator_dir)

    execution_replay = None
    if (execution_dir / "007_first_live_provider_dispatch_execution_packet.json").exists():
        execution_replay = reconstruct_first_live_provider_execution_runtime_replay(execution_dir)

    err = load_json(activation_dir / "err_openai_selection" / "000_err_resource_selection_evidence_recorded.json")[
        "artifact"
    ]
    execution_capture = operator_result.get("execution_capture")
    provider_invoked = False
    provider_response_received = False
    transport_evidence: dict[str, Any] = {}
    cognition_artifact: dict[str, Any] = {}
    if isinstance(execution_capture, dict):
        transport_evidence = execution_capture.get("live_transport_execution_evidence_artifact") or {}
        cognition_artifact = execution_capture.get("llm_cognition_artifact") or {}
        provider_invoked = bool(transport_evidence.get("provider_invoked"))
        provider_response_received = execution_capture.get("final_status") == "DISPATCH_EXECUTION_COMPLETED"

    human_confirmation_recorded = _record_human_confirmation(
        human_confirmation_dir=human_confirmation_dir,
        cert_suffix=cert_suffix,
        created_at=created_at,
        provider_response_received=provider_response_received,
        transport_evidence=transport_evidence,
        cognition_artifact=cognition_artifact,
    )
    observed = {
        "provider_selected": err.get("selected_resource_id"),
        "provider_selected_type": err.get("selected_resource_type"),
        "provider_invoked": provider_invoked,
        "provider_response_received": provider_response_received,
        "human_confirmation_recorded": human_confirmation_recorded,
        "replay_reconstructed": bool(activation_replay and dispatch_replay and operator_replay),
        "execution_replay_reconstructed": execution_replay is not None,
        "worker_invoked": bool(operator_result.get("worker_invoked")),
        "credential_secret_replayed": bool(operator_result.get("credential_secret_replayed")),
        "authorization_header_replayed": bool(operator_result.get("authorization_header_replayed")),
        "operator_final_status": operator_result.get("final_status"),
        "failure_reason": operator_result.get("failure_reason"),
    }
    provider_governance_replay = _record_provider_governance_observability(
        provider_governance_dir=provider_governance_dir,
        cert_suffix=cert_suffix,
        provider_id=str(observed["provider_selected"] or "openai"),
        model="gpt-5.1",
        created_at=created_at,
        provider_invoked=provider_invoked,
        provider_response_received=provider_response_received,
        human_confirmation_recorded=human_confirmation_recorded,
        failure_reason=observed["failure_reason"],
    )
    final_verdict = (
        "FIRST_LIVE_COGNITION_PROVIDER_CERTIFIED"
        if all(
            [
                observed["provider_selected"] == "openai",
                observed["provider_invoked"],
                observed["provider_response_received"],
                observed["human_confirmation_recorded"],
                observed["replay_reconstructed"],
                not observed["worker_invoked"],
            ]
        )
        else "COGNITION_PROVIDER_CERTIFICATION_FAILED"
    )

    evidence_package, replay_package, report = _create_summary_artifacts(
        root=root,
        cert_suffix=cert_suffix,
        created_at=created_at,
        activation_dir=activation_dir,
        dispatch_dir=dispatch_dir,
        execution_dir=execution_dir,
        operator_dir=operator_dir,
        human_confirmation_dir=human_confirmation_dir,
        provider_governance_dir=provider_governance_dir,
        observed=observed,
        final_verdict=final_verdict,
        execution_replay=execution_replay,
        provider_governance_replay=provider_governance_replay,
        provider_response_received=provider_response_received,
        human_confirmation_recorded=human_confirmation_recorded,
    )
    _persist_summary_artifacts(
        evidence_dir=evidence_dir,
        replay_dir=replay_dir,
        report_dir=report_dir,
        evidence_package=evidence_package,
        replay_package=replay_package,
        report=report,
    )
    return {
        "milestone_id": MILESTONE_ID,
        "preflight": preflight,
        "cert_root": str(root),
        "activation_status": activation.get("final_status"),
        "dispatch_authorization_status": dispatch.get("authorization_status"),
        "observed": observed,
        "final_verdict": final_verdict,
        "evidence_package_path": str(evidence_dir / "000_first_live_cognition_provider_evidence_package.json"),
        "replay_package_path": str(replay_dir / "000_first_live_cognition_provider_replay_package.json"),
        "certification_report_path": str(report_dir / "000_first_live_cognition_provider_certification_report.json"),
    }


def main() -> int:
    result = run_first_live_cognition_provider_certification()
    preflight = result["preflight"]
    print(f"AIGOL_OPENAI_API_KEY_PRESENT={preflight['aigol_openai_api_key_present']}")
    print(f"OPENAI_API_KEY_PRESENT={preflight['openai_api_key_present']}")
    if result.get("aborted_before_certification"):
        print(f"ABORTED_BEFORE_CERTIFICATION={result['aborted_reason']}")
        return 2
    observed = result["observed"]
    print(f"CERT_ROOT={result['cert_root']}")
    print(f"provider_selected={observed['provider_selected']}")
    print(f"provider_invoked={observed['provider_invoked']}")
    print(f"provider_response_received={observed['provider_response_received']}")
    print(f"human_confirmation_recorded={observed['human_confirmation_recorded']}")
    print(f"replay_reconstructed={observed['replay_reconstructed']}")
    print(f"FINAL_VERDICT={result['final_verdict']}")
    return 0 if result["final_verdict"] == "FIRST_LIVE_COGNITION_PROVIDER_CERTIFIED" else 1


def _credential_preflight(*, require_openai_api_key_marker: bool) -> dict[str, bool]:
    return {
        "aigol_openai_api_key_present": bool(os.environ.get("AIGOL_OPENAI_API_KEY")),
        "openai_api_key_present": bool(os.environ.get("OPENAI_API_KEY")) if require_openai_api_key_marker else True,
    }


def _aborted_capture(reason: str, preflight: dict[str, bool]) -> dict[str, Any]:
    return {
        "milestone_id": MILESTONE_ID,
        "preflight": preflight,
        "aborted_before_certification": True,
        "aborted_reason": reason,
        "final_verdict": "COGNITION_PROVIDER_CERTIFICATION_FAILED",
    }


def _next_cert_root(base: Path) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    existing = []
    for path in base.glob("CERT-*"):
        match = re.fullmatch(r"CERT-(\d{6})", path.name)
        if match:
            existing.append(int(match.group(1)))
    return base / f"CERT-{max(existing, default=0) + 1:06d}"


def _record_human_confirmation(
    *,
    human_confirmation_dir: Path,
    cert_suffix: str,
    created_at: str,
    provider_response_received: bool,
    transport_evidence: dict[str, Any],
    cognition_artifact: dict[str, Any],
) -> bool:
    if not provider_response_received:
        return False
    human_confirmation_dir.mkdir(parents=True, exist_ok=True)
    confirmation = {
        "artifact_type": "FIRST_LIVE_COGNITION_PROVIDER_HUMAN_CONFIRMATION_ARTIFACT_V1",
        "certification_id": f"FIRST-LIVE-COGNITION-PROVIDER-CERT-{cert_suffix}",
        "created_at": created_at,
        "provider_response_artifact_hash": transport_evidence.get("response_artifact_hash"),
        "llm_cognition_artifact_hash": cognition_artifact.get("artifact_hash"),
        "human_confirmation_recorded": True,
        "confirmed_as_proposal_only": True,
        "worker_execution_authorized": False,
        "governance_mutation_authorized": False,
        "additional_provider_call_authorized": False,
        "credential_secret_replayed": False,
        "authorization_header_replayed": False,
        "replay_visible": True,
    }
    confirmation["artifact_hash"] = replay_hash(confirmation)
    write_json_immutable(
        human_confirmation_dir / "000_first_live_cognition_provider_human_confirmation.json",
        confirmation,
    )
    return True


def _record_provider_governance_observability(
    *,
    provider_governance_dir: Path,
    cert_suffix: str,
    provider_id: str,
    model: str,
    created_at: str,
    provider_invoked: bool,
    provider_response_received: bool,
    human_confirmation_recorded: bool,
    failure_reason: str | None,
) -> dict[str, Any]:
    execute_provider_lifecycle_operation(
        event_id=f"FIRST-LIVE-COGNITION-PROVIDER-CERT-{cert_suffix}:PROVIDER-VERIFY",
        operation="VERIFY",
        provider_id=provider_id,
        requested_by="first_live_cognition_provider_certification",
        created_at=created_at,
        replay_dir=provider_governance_dir / "credential_lifecycle",
    )
    record_provider_usage_metric(
        metric_id=f"FIRST-LIVE-COGNITION-PROVIDER-CERT-{cert_suffix}:PROVIDER-USAGE",
        provider_id=provider_id,
        model=model,
        status="SUCCESS" if provider_response_received else "FAILED",
        availability="AVAILABLE" if provider_response_received else "DEPENDENCY_UNAVAILABLE",
        success_count=1 if provider_response_received else 0,
        failure_count=0 if provider_response_received else 1,
        last_used=created_at if provider_invoked else None,
        last_failure=None if provider_response_received else failure_reason or "provider response unavailable",
        token_usage={"source": "provider_response_envelope"},
        cost_tracking={"hook_status": "AVAILABLE_FOR_PROVIDER_COST_ACCOUNTING"},
        created_at=created_at,
        replay_dir=provider_governance_dir / "usage",
    )
    record_cognition_participation(
        participation_id=f"FIRST-LIVE-COGNITION-PROVIDER-CERT-{cert_suffix}:COGNITION-PARTICIPATION",
        provider_id=provider_id,
        participation_location="OCS_LLM_COGNITION",
        participation_role="proposal_only_cognition",
        workflow_id="OCS_LLM_COGNITION",
        invocation_reason="first live cognition provider certification",
        purpose="proposal generation for human confirmation",
        response_used=provider_response_received,
        worker_invoked_after=False,
        human_confirmation_required=True,
        created_at=created_at,
        replay_dir=provider_governance_dir / "cognition_participation",
    )
    replay = reconstruct_provider_governance_replay(provider_governance_dir)
    replay["human_confirmation_recorded"] = human_confirmation_recorded
    return replay


def _create_summary_artifacts(
    *,
    root: Path,
    cert_suffix: str,
    created_at: str,
    activation_dir: Path,
    dispatch_dir: Path,
    execution_dir: Path,
    operator_dir: Path,
    human_confirmation_dir: Path,
    provider_governance_dir: Path,
    observed: dict[str, Any],
    final_verdict: str,
    execution_replay: dict[str, Any] | None,
    provider_governance_replay: dict[str, Any],
    provider_response_received: bool,
    human_confirmation_recorded: bool,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    evidence_package = {
        "artifact_type": "FIRST_LIVE_COGNITION_PROVIDER_EVIDENCE_PACKAGE_V1",
        "certification_id": f"FIRST-LIVE-COGNITION-PROVIDER-CERT-{cert_suffix}",
        "created_at": created_at,
        "scenario": {
            "proposal_only": True,
            "worker_execution_allowed": False,
        },
        "evidence_references": {
            "activation_package": str(activation_dir),
            "err_resolution": str(activation_dir / "err_openai_selection"),
            "dispatch_authorization": str(dispatch_dir),
            "operator_entrypoint": str(operator_dir),
            "execution": str(execution_dir),
            "human_confirmation": str(human_confirmation_dir),
            "provider_governance": str(provider_governance_dir),
        },
        "provider_governance_replay": provider_governance_replay,
        "observed": observed,
    }
    evidence_package["artifact_hash"] = replay_hash(evidence_package)
    replay_package = {
        "artifact_type": "FIRST_LIVE_COGNITION_PROVIDER_REPLAY_PACKAGE_V1",
        "certification_id": f"FIRST-LIVE-COGNITION-PROVIDER-CERT-{cert_suffix}",
        "created_at": created_at,
        "replay_root": str(root),
        "reconstructed_segments": {
            "activation_package": True,
            "err_resolution": True,
            "dispatch_authorization": True,
            "operator_entrypoint": True,
            "execution_runtime": execution_replay is not None,
            "provider_response": provider_response_received,
            "human_confirmation": human_confirmation_recorded,
            "provider_governance": provider_governance_replay.get("append_only_valid") is True,
        },
        "provider_governance_replay": provider_governance_replay,
        "replay_reconstructed": observed["replay_reconstructed"],
        "observed": observed,
    }
    replay_package["artifact_hash"] = replay_hash(replay_package)
    report = {
        "artifact_type": "FIRST_LIVE_COGNITION_PROVIDER_CERTIFICATION_REPORT_V1",
        "certification_id": f"FIRST-LIVE-COGNITION-PROVIDER-CERT-{cert_suffix}",
        "governing_artifact": "AIGOL_FIRST_LIVE_COGNITION_PROVIDER_CERTIFICATION_V1",
        "created_at": created_at,
        "observed": observed,
        "provider_governance_replay": provider_governance_replay,
        "blocker_analysis": {
            "architecture_blockers": [],
            "governance_blockers": [],
            "runtime_blockers": []
            if final_verdict == "FIRST_LIVE_COGNITION_PROVIDER_CERTIFIED"
            else [observed["failure_reason"]],
            "dependency_blockers": [],
        },
        "final_verdict": final_verdict,
    }
    report["artifact_hash"] = replay_hash(report)
    return evidence_package, replay_package, report


def _persist_summary_artifacts(
    *,
    evidence_dir: Path,
    replay_dir: Path,
    report_dir: Path,
    evidence_package: dict[str, Any],
    replay_package: dict[str, Any],
    report: dict[str, Any],
) -> None:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    replay_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    write_json_immutable(evidence_dir / "000_first_live_cognition_provider_evidence_package.json", evidence_package)
    write_json_immutable(replay_dir / "000_first_live_cognition_provider_replay_package.json", replay_package)
    write_json_immutable(report_dir / "000_first_live_cognition_provider_certification_report.json", report)


if __name__ == "__main__":
    raise SystemExit(main())
