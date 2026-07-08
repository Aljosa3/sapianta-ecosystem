from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aigol.cli import aicli, aigol_cli
from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.provider.providers.openai_provider import openai_provider_metadata
from aigol.runtime.replay_certification_runtime import REPLAY_CERTIFICATION_COMPLETED
from aigol.runtime.worker_invocation_runtime import WORKER_INVOKED


CREATED_AT = "2026-07-08T00:00:00Z"


class FakeProviderAdapter:
    provider_id = "openai"
    provider_version = openai_provider_metadata().provider_version

    def __init__(self) -> None:
        self.calls = 0

    def generate_proposal(self, request: Any, *, proposal_id: str, timestamp: str):
        self.calls += 1
        return create_provider_proposal_envelope(
            proposal_id=proposal_id,
            provider_id=self.provider_id,
            provider_version=self.provider_version,
            request=request,
            response={
                "proposal_summary": "Continue the governed bridge into certified runtime.",
                "proposed_outputs": ["governance/G15_RUNTIME_06_CERTIFICATION.json"],
                "constraints_acknowledged": ["NO_BYPASS", "REPLAY_CERTIFICATION_REQUIRED"],
                "assumptions": ["Existing certified runtime continuation is reused."],
                "known_gaps": [],
            },
            timestamp=timestamp,
        )


def _reader(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def _install_fake_providers(monkeypatch) -> FakeProviderAdapter:
    proposal_adapter = FakeProviderAdapter()

    def fake_external_worker_client(request_metadata: dict[str, Any]) -> dict[str, Any]:
        assert request_metadata["provider_identity"] == "OPENAI"
        return {
            "id": "resp-g15-runtime-06-external-worker",
            "output_text": "Bounded certified runtime continuation completed.",
        }

    monkeypatch.setattr(aigol_cli, "_post_context_continuation_provider_adapter", lambda: proposal_adapter)
    monkeypatch.setattr(aigol_cli, "_external_worker_openai_client", lambda: fake_external_worker_client)
    return proposal_adapter


def _wrapped_artifact(replay_reference: str, filename: str) -> dict[str, Any]:
    with (Path(replay_reference) / filename).open(encoding="utf-8") as handle:
        wrapper = json.load(handle)
    artifact = wrapper["artifact"]
    assert isinstance(artifact, dict)
    return artifact


def test_approved_aicli_governed_development_bridge_continues_to_replay_certified(
    tmp_path: Path,
    monkeypatch,
) -> None:
    proposal_adapter = _install_fake_providers(monkeypatch)
    output: list[str] = []

    result = aicli.run_reference_uhi_submit_session(
        session_id="G15-RUNTIME-06-UHI-BRIDGE-CONTINUATION",
        created_at=CREATED_AT,
        runtime_root=tmp_path / "aicli",
        workspace=tmp_path,
        stdin_reader=lambda: (
            "Implement G15_RUNTIME_06_GOVERNED_DEVELOPMENT_RUNTIME_CONTINUATION. "
            "Goal: continue approved governed development requests from the execution bridge "
            "into certified Platform Core runtime."
        ),
        input_reader=_reader(["/approve"]),
        output_writer=output.append,
    )

    runtime_result = result["runtime_result"]

    assert result["runtime_status"] == aicli.REFERENCE_UHI_BOUND
    assert result["aicli_authorizes"] is False
    assert result["aicli_executes"] is False
    assert result["aicli_owns_replay"] is False
    assert runtime_result["runtime_response_source"] == "ACLI_GOVERNED_DEVELOPMENT_EXECUTION_BRIDGE"
    assert runtime_result["runtime_response_status"] == "GOVERNED_DEVELOPMENT_BRIDGE_CERTIFIED_RUNTIME_COMPLETED"
    assert runtime_result["worker_execution_reached"] is True
    assert runtime_result["worker_invocation_status"] == WORKER_INVOKED
    assert runtime_result["external_task_package_reached"] is True
    assert runtime_result["replay_certification_reached"] is True
    assert runtime_result["replay_certification_status"] == REPLAY_CERTIFICATION_COMPLETED
    assert runtime_result["auto_continue_enabled"] is True
    assert runtime_result["auto_continue_stop_reason"] == "WORKFLOW_COMPLETE"
    assert runtime_result["manual_chatgpt_codex_transfer_required"] is False
    assert proposal_adapter.calls == 1

    replay_certification = _wrapped_artifact(
        runtime_result["replay_certification_replay_reference"],
        "000_replay_certification_artifact_recorded.json",
    )
    assert replay_certification["certification_status"] == REPLAY_CERTIFICATION_COMPLETED
    assert replay_certification["replay_lineage_preserved"] is True
