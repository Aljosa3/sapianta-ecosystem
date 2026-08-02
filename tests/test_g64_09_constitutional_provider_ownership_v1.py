"""Focused G64-09 regression coverage for authenticated provider ownership."""

from __future__ import annotations

import json

import pytest

from aigol.runtime.authenticated_provider_selection_runtime import (
    AUTHENTICATED_PROVIDER_SELECTION_OWNER,
    SELECTION_REPLAY_DIRECTORY,
)
from aigol.runtime.llm_cognition_provider_runtime import (
    reconstruct_llm_cognition_provider_replay,
    create_default_openai_cognition_provider_contract,
    run_llm_cognition_provider_runtime,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.native_provider_execution_runtime import (
    invoke_provider_once,
    reconstruct_native_provider_execution_replay,
    run_native_provider_execution,
)
from aigol.runtime.ocs_context_assembly_runtime import assemble_ocs_context
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-08-02T00:00:00Z"


def _transport(payload: dict, metadata: dict) -> dict:
    assert payload["stream"] is False
    assert metadata["provider_id"] == "openai"
    return {"id": "g64-09-response", "output_text": "Bounded provider result."}


def _context(tmp_path) -> dict:
    source = {
        "artifact_type": "HUMAN_REQUEST_ARTIFACT_V1",
        "artifact_id": "G64-09-HUMAN-REQUEST",
        "status": "REPLAY_VISIBLE",
        "summary": "Provider ownership regression request.",
        "replay_visible": True,
        "authority": False,
        "execution_requested": False,
        "worker_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    source["artifact_hash"] = replay_hash(source)
    capture = assemble_ocs_context(
        context_assembly_id="G64-09-OCS-CONTEXT",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "context",
        source_context={"conversation_context": [source]},
        source_chain_id="G64-09-CHAIN",
        source_request_reference=source["artifact_id"],
    )
    return capture["ocs_context_assembly_artifact"]


def test_both_formerly_direct_provider_paths_bind_to_unified_selection_owner(tmp_path, monkeypatch):
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "g64-09-test-key")
    native_root = tmp_path / "native"
    cognition_root = tmp_path / "cognition"

    native = run_native_provider_execution(
        execution_id="G64-09-NATIVE",
        human_request="Return bounded provider evidence.",
        created_at=CREATED_AT,
        replay_dir=native_root,
        human_approved=True,
        transport=_transport,
    )
    cognition = run_llm_cognition_provider_runtime(
        cognition_provider_request_id="G64-09-COGNITION",
        human_request="Return bounded cognition evidence.",
        ocs_context_artifact=_context(tmp_path),
        provider_contract=create_default_openai_cognition_provider_contract(created_at=CREATED_AT),
        created_at=CREATED_AT,
        replay_dir=cognition_root,
        human_approved=True,
        transport=_transport,
    )

    native_selection = native["provider_request"]["provider_selection"]
    cognition_selection = cognition["llm_cognition_provider_request_artifact"]["provider_selection"]
    for root, selection in ((native_root, native_selection), (cognition_root, cognition_selection)):
        assert selection["selection_owner"] == AUTHENTICATED_PROVIDER_SELECTION_OWNER
        assert selection["selected_resource_id"] == "OPENAI"
        assert selection["provider_id"] == "openai"
        assert (root / SELECTION_REPLAY_DIRECTORY / "000_resource_selection_recorded.json").is_file()
        assert (root / SELECTION_REPLAY_DIRECTORY / "001_resource_selection_returned.json").is_file()

    assert reconstruct_native_provider_execution_replay(native_root)["provider_selection_owner"] == (
        AUTHENTICATED_PROVIDER_SELECTION_OWNER
    )
    assert reconstruct_llm_cognition_provider_replay(cognition_root)["provider_selection_owner"] == (
        AUTHENTICATED_PROVIDER_SELECTION_OWNER
    )


def test_selection_replay_tampering_invalidates_native_provider_reconstruction(tmp_path, monkeypatch):
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "g64-09-test-key")
    replay_root = tmp_path / "native"
    run_native_provider_execution(
        execution_id="G64-09-NATIVE-TAMPER",
        human_request="Return bounded provider evidence.",
        created_at=CREATED_AT,
        replay_dir=replay_root,
        human_approved=True,
        transport=_transport,
    )
    selection_path = replay_root / SELECTION_REPLAY_DIRECTORY / "000_resource_selection_recorded.json"
    wrapper = json.loads(selection_path.read_text(encoding="utf-8"))
    wrapper["artifact"]["selected_resource_id"] = "TAMPERED"
    selection_path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="resource selection.*hash mismatch"):
        reconstruct_native_provider_execution_replay(replay_root)


def test_native_invocation_refuses_a_request_without_authenticated_selection(tmp_path, monkeypatch):
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "g64-09-test-key")
    result = run_native_provider_execution(
        execution_id="G64-09-NATIVE-REQUEST-VALIDATION",
        human_request="Return bounded provider evidence.",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "native",
        human_approved=True,
        transport=_transport,
    )
    request = dict(result["provider_request"])
    request.pop("provider_selection")
    request.pop("artifact_hash")
    request["artifact_hash"] = replay_hash(request)
    called = False

    def transport(_payload, _metadata):
        nonlocal called
        called = True
        return {"output_text": "must not run"}

    with pytest.raises(FailClosedRuntimeError, match="selection binding is required"):
        invoke_provider_once(
            provider_request=request,
            credential_secret="g64-09-test-key",
            transport=transport,
        )
    assert called is False
