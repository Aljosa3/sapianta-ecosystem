from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from aigol.cli import aicli
from aigol.runtime import human_decision_runtime as decision
from aigol.runtime import human_interface_runtime_entry_service as entry
from aigol.runtime import platform_core_existing_file_governance as governance
from aigol.runtime.human_interface_runtime_entry_service import run_human_interface_runtime_entry
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, with_replay_hash
from aigol.runtime.unified_resource_selection_runtime import (
    RESOURCE_SELECTION_SUCCEEDED,
    _registry_hash_input,
    reconstruct_unified_resource_selection_replay,
)
from aigol.workers import filesystem_replace_worker as worker
from test_g31_24g_r04_r04_r02_existing_replace_owner_hardening import _public_evidence
from test_g31_24g_r04_r04_r04_r01_common_entry_adapter_repair import (
    ACTOR,
    CREATED,
    InMemoryAdapter,
    _pending_state,
)


WORKER_ID = "FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER"
WORKER_VERSION = "G8_12_EXISTING_FILE_MUTATION_IMPLEMENTATION_V1"
CAPABILITY = "REPLACE_EXISTING_TEXT_FILE"


def _consumed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str):
    common, authorization, actor, target = _public_evidence(tmp_path, monkeypatch)
    request = governance.create_g31_authenticated_replace_request(
        actor_replay_capture=actor,
        authorization_capture=authorization,
        **common,
    )
    request_stage = worker.record_authenticated_replace_request_v2(request)
    consumption = worker.consume_authenticated_replace_authorization_v2(request)
    authorization_reconstruction = (
        governance.reconstruct_g31_mutation_authorization_actor_and_replay(
            actor_replay_capture=actor,
            authorization_capture=authorization,
            **common,
        )
    )
    return request, request_stage, consumption, authorization_reconstruction, target


def _select(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str = "R08C"):
    request, stage, consumption, authorization, target = _consumed(
        tmp_path, monkeypatch, name
    )
    selection_root = Path(request["session_root"]) / f"{name}-SELECTION"
    capture = governance.bind_consumed_g31_authenticated_replace_worker_selection(
        authenticated_request=request,
        authorization_reconstruction=authorization,
        consumption_reconstruction=consumption,
        replay_dir=selection_root,
    )
    return capture, request, stage, consumption, authorization, target, selection_root


def _transport(root: Path, state: dict) -> dict:
    return run_human_interface_runtime_entry(
        interface_name="in_memory_r08c_adapter",
        session_id=root.name,
        human_requests=[],
        created_at=CREATED,
        runtime_root=root.parent,
        workspace="/isolated/repository",
        governed_runtime_runner=lambda *_args, **_kwargs: {},
        g31_application_state=state,
        g31_human_action=decision.MUTATION_APPROVED,
        g31_human_actor_id=ACTOR,
    )


def _forbid_downstream(monkeypatch: pytest.MonkeyPatch) -> dict[str, int]:
    calls: dict[str, int] = {}
    targets = (
        (entry.worker_request, "create_worker_invocation_request"),
        (entry.worker_assignment, "assign_worker_from_invocation_request"),
        (entry.worker_dispatch, "dispatch_assigned_worker"),
        (entry.worker_invocation, "invoke_dispatched_worker"),
        (governance, "execute_g31_authenticated_replace"),
        (governance, "recover_g31_authenticated_replace"),
        (worker, "execute_filesystem_replace_request"),
        (worker, "_execute_authenticated_replace_v2"),
        (worker, "_recover_authenticated_replace_v2"),
        (worker, "_open_v2_target"),
        (worker, "_atomic_restore_v2"),
    )
    for owner, symbol in targets:
        calls[symbol] = 0

        def forbidden(*_args, _symbol=symbol, **_kwargs):
            calls[_symbol] += 1
            raise AssertionError(f"forbidden R08C downstream call: {_symbol}")

        monkeypatch.setattr(owner, symbol, forbidden)
    return calls


def test_common_entry_selects_exact_consumed_worker_and_stops(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R08C-COMMON")
    state.update({"terminal_prompt": "choose CODEX", "slash_command": "/assign"})
    forbidden = _forbid_downstream(monkeypatch)

    result = InMemoryAdapter(root).transport(state, decision.MUTATION_APPROVED)
    request = result["authenticated_replacement_request"]
    consumption = result["authorization_consumption_reconstruction"]
    capture = result["consumed_replacement_worker_selection_capture"]
    artifact = capture["resource_selection_artifact"]
    context = result["consumed_replacement_selection_context"]

    assert result["worker_selection_status"] == RESOURCE_SELECTION_SUCCEEDED
    assert result["selected_resource_id"] == WORKER_ID
    assert result["selected_role_type"] == "WORKER_ROLE"
    assert result["worker_selected"] is True
    assert artifact["selected_resource_version"] == WORKER_VERSION
    assert artifact["required_capability"] == CAPABILITY
    assert artifact["registry_hash"] == governance.R08B_REGISTRY_HASH
    assert artifact["context_reference"] == context["context_identity"]
    assert artifact["context_hash"] == replay_hash(context)
    assert context["authenticated_request_hash"] == request["request_hash"]
    assert context["authorization_hash"] == request["authorization_hash"]
    assert context["consumption_identity"] == consumption["consumption_identity"]
    assert context["consumption_hash"] == consumption["last_wrapper_hash"]
    assert context["consumption_replay_hash"] == consumption["replay_hash"]
    assert context["predecessor_ordering"] == ["request", "consumption"]
    assert context["certified_registry_hash"] == governance.R08B_REGISTRY_HASH
    assert context["certification_report_hash"] == governance.R08B_CERTIFICATION_HASH
    assert "terminal_prompt" not in context
    assert "slash_command" not in context
    for field in (
        "worker_assigned", "worker_dispatched", "provider_invoked", "worker_invoked",
        "execution_requested", "command_executed", "target_opened",
        "repository_mutated", "restoration_started", "rollback_started",
        "recovery_started",
    ):
        assert capture[field] is False
    assert all(value == 0 for value in forbidden.values())
    assert worker.reconstruct_authenticated_replace_replay_v2(request)["event_keys"] == [
        "request", "consumption"
    ]
    assert capture["certified_selection_reconstruction"]["replay_artifact_count"] == 2
    rendered = "\n".join(result["g31_canonical_presentations"])
    assert "Worker Selection Reached: True" in rendered
    assert f"selected_resource_id: {WORKER_ID}" in rendered
    assert "worker_assigned: False" in rendered


def test_aicli_and_in_memory_adapters_receive_same_canonical_selection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    memory_root, memory_state = _pending_state(tmp_path, monkeypatch, "R08C-MEMORY")
    memory = _transport(memory_root, memory_state)
    cli_root, cli_state = _pending_state(tmp_path, monkeypatch, "R08C-AICLI")
    cli_state.update({"terminal_prompt": "CLAUDE_CODE", "display_worker": "CODEX"})
    cli = aicli._continue_g31_application_action(
        runtime_result=cli_state,
        action=decision.MUTATION_APPROVED,
        session=cli_root.name,
        root=cli_root.parent,
        workspace_path="/isolated/repository",
        created=CREATED,
        worker_process_runner=None,
    )

    for result in (memory, cli):
        capture = result["consumed_replacement_worker_selection_capture"]
        assert capture["selection_status"] == RESOURCE_SELECTION_SUCCEEDED
        assert capture["selected_resource_id"] == WORKER_ID
        assert capture["selected_role_type"] == "WORKER_ROLE"
        assert capture["resource_selection_artifact"]["required_capability"] == CAPABILITY
        assert capture["worker_assigned"] is False
        assert capture["worker_dispatched"] is False
        assert capture["worker_invoked"] is False
    assert memory["g31_application_interface_transport"] == "in_memory_r08c_adapter"
    assert cli["g31_application_interface_transport"] == "aicli"
    assert "terminal_prompt" not in cli["consumed_replacement_selection_context"]
    assert "display_worker" not in cli["consumed_replacement_selection_context"]


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("worker_id", "CODEX"),
        ("worker_id", "CLAUDE_CODE"),
        ("worker_id", "FILESYSTEM_REPLACE_WORKER_ALIAS"),
        ("worker_operation", "IMPLEMENTATION_ASSISTANCE"),
        ("worker_operation", "FILESYSTEM_INSPECTION"),
        ("mutation_decision_hash", "SUBSTITUTED"),
        ("authorization_hash", "sha256:" + "0" * 64),
        ("repository_identity", "OTHER_REPOSITORY"),
        ("session_id", "OTHER_SESSION"),
        ("target_path", "other/file.txt"),
        ("replacement_content_hash", "SUBSTITUTED"),
        ("replacement_bytes_b64", "c3Vic3RpdHV0ZWQ="),
    ),
)
def test_changed_request_identity_or_payload_fails_before_selection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, field: str, value: str
) -> None:
    request, _, consumption, authorization, target = _consumed(
        tmp_path, monkeypatch, f"R08C-{field}"
    )
    changed = deepcopy(request)
    changed[field] = value
    changed["request_hash"] = replay_hash(
        {key: item for key, item in changed.items() if key != "request_hash"}
    )
    destination = Path(request["session_root"]) / f"SELECTION-{field}"

    with pytest.raises(FailClosedRuntimeError):
        governance.bind_consumed_g31_authenticated_replace_worker_selection(
            authenticated_request=changed,
            authorization_reconstruction=authorization,
            consumption_reconstruction=consumption,
            replay_dir=destination,
        )
    assert not destination.exists()
    assert target.read_text(encoding="utf-8") != "replacement bytes\n"


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("consumption_identity", "SUBSTITUTED"),
        ("authorization_hash", "SUBSTITUTED"),
        ("request_hash", "SUBSTITUTED"),
        ("request_stage_replay_hash", "SUBSTITUTED"),
        ("replay_hash", "SUBSTITUTED"),
        ("authorization_consumed", False),
        ("worker_selected", True),
    ),
)
def test_changed_consumption_evidence_fails_before_selection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, field: str, value
) -> None:
    request, _, consumption, authorization, _, = _consumed(
        tmp_path, monkeypatch, f"R08C-CONSUMPTION-{field}"
    )
    changed = {**deepcopy(consumption), field: value}
    destination = Path(request["session_root"]) / f"SELECTION-{field}"
    with pytest.raises(FailClosedRuntimeError, match="lineage mismatch"):
        governance.bind_consumed_g31_authenticated_replace_worker_selection(
            authenticated_request=request,
            authorization_reconstruction=authorization,
            consumption_reconstruction=changed,
            replay_dir=destination,
        )
    assert not destination.exists()


def test_missing_or_stale_authorization_fails_before_selection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    request, _, consumption, authorization, _ = _consumed(
        tmp_path, monkeypatch, "R08C-AUTHORIZATION"
    )
    destination = Path(request["session_root"]) / "SELECTION"
    for changed in ({}, {**authorization, "authorization_hash": "SUBSTITUTED"}):
        with pytest.raises(FailClosedRuntimeError):
            governance.bind_consumed_g31_authenticated_replace_worker_selection(
                authenticated_request=request,
                authorization_reconstruction=changed,
                consumption_reconstruction=consumption,
                replay_dir=destination,
            )
        assert not destination.exists()


def test_missing_or_duplicated_consumption_fails_before_selection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    request, _, consumption, authorization, _ = _consumed(
        tmp_path, monkeypatch, "R08C-DUPLICATE-CONSUMPTION"
    )
    destination = Path(request["session_root"]) / "SELECTION"
    with pytest.raises(FailClosedRuntimeError):
        governance.bind_consumed_g31_authenticated_replace_worker_selection(
            authenticated_request=request,
            authorization_reconstruction=authorization,
            consumption_reconstruction={},
            replay_dir=destination,
        )
    lifecycle = Path(request["destinations"]["consumption"]).parent
    duplicate = lifecycle / "duplicate_consumption.json"
    duplicate.write_bytes(Path(request["destinations"]["consumption"]).read_bytes())
    with pytest.raises(FailClosedRuntimeError):
        governance.bind_consumed_g31_authenticated_replace_worker_selection(
            authenticated_request=request,
            authorization_reconstruction=authorization,
            consumption_reconstruction=consumption,
            replay_dir=destination,
        )
    assert not destination.exists()


@pytest.mark.parametrize("mode", ("version", "stale_hash", "duplicate"))
def test_substituted_or_ambiguous_registry_fails_before_selector(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    request, _, consumption, authorization, _ = _consumed(
        tmp_path, monkeypatch, "R08C-REGISTRY"
    )
    registry = governance.default_resource_registry()
    resource = next(value for value in registry["resources"] if value["resource_id"] == WORKER_ID)
    if mode == "version":
        resource["resource_version"] = "SUBSTITUTED"
        registry["registry_hash"] = replay_hash(_registry_hash_input(registry))
    elif mode == "stale_hash":
        registry["registry_hash"] = "sha256:" + "0" * 64
    else:
        registry["resources"] = (*registry["resources"], deepcopy(resource))
        registry["registry_hash"] = replay_hash(_registry_hash_input(registry))
    monkeypatch.setattr(governance, "default_resource_registry", lambda: deepcopy(registry))
    destination = Path(request["session_root"]) / "SELECTION"

    with pytest.raises(FailClosedRuntimeError):
        governance.bind_consumed_g31_authenticated_replace_worker_selection(
            authenticated_request=request,
            authorization_reconstruction=authorization,
            consumption_reconstruction=consumption,
            replay_dir=destination,
        )
    assert not destination.exists()


@pytest.mark.parametrize("mode", ("missing", "false", "lineage", "hash"))
def test_invalid_r08b_certification_fails_before_selector(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    request, _, consumption, authorization, _ = _consumed(
        tmp_path, monkeypatch, f"R08C-CERT-{mode}"
    )
    report = load_json(governance.R08B_CERTIFICATION_PATH)
    if mode == "missing":
        path = tmp_path / "missing-certification.json"
    elif mode == "false":
        report["final_verdict"] = "WORKER_SELECTION_GAPS_FOUND"
        report = with_replay_hash(report, hash_field="artifact_hash")
    elif mode == "lineage":
        report["certified_resource"]["certification_evidence"][0] = "substituted"
        report["certified_resource_hash"] = replay_hash(report["certified_resource"])
        report = with_replay_hash(report, hash_field="artifact_hash")
    else:
        report["artifact_hash"] = "sha256:" + "0" * 64
    if mode != "missing":
        path = tmp_path / f"certification-{mode}.json"
        path.write_text(json.dumps(report), encoding="utf-8")
    monkeypatch.setattr(governance, "R08B_CERTIFICATION_PATH", path)
    destination = Path(request["session_root"]) / "SELECTION"

    with pytest.raises(FailClosedRuntimeError):
        governance.bind_consumed_g31_authenticated_replace_worker_selection(
            authenticated_request=request,
            authorization_reconstruction=authorization,
            consumption_reconstruction=consumption,
            replay_dir=destination,
        )
    assert not destination.exists()


@pytest.mark.parametrize("mode", ("removed", "duplicated", "reordered", "substituted"))
def test_selection_replay_tamper_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    _, _, _, _, _, _, root = _select(tmp_path, monkeypatch, f"R08C-REPLAY-{mode}")
    recorded = root / "000_resource_selection_recorded.json"
    returned = root / "001_resource_selection_returned.json"
    if mode == "removed":
        returned.unlink()
    elif mode == "duplicated":
        (root / "002_resource_selection_returned.json").write_bytes(returned.read_bytes())
    elif mode == "reordered":
        wrapper = load_json(returned)
        wrapper["replay_index"] = 0
        returned.write_text(
            json.dumps(with_replay_hash(wrapper, hash_field="replay_hash")), encoding="utf-8"
        )
    else:
        wrapper = load_json(recorded)
        wrapper["artifact"]["context_hash"] = "sha256:" + "0" * 64
        wrapper["artifact"] = with_replay_hash(wrapper["artifact"], hash_field="artifact_hash")
        recorded.write_text(
            json.dumps(with_replay_hash(wrapper, hash_field="replay_hash")), encoding="utf-8"
        )
    with pytest.raises(FailClosedRuntimeError):
        reconstruct_unified_resource_selection_replay(root)


def test_aicli_owns_no_r08c_selection_semantics() -> None:
    source = Path("aigol/cli/aicli.py").read_text(encoding="utf-8")
    for symbol in (
        "bind_consumed_g31_authenticated_replace_worker_selection(",
        "select_unified_resource(",
        "default_resource_registry(",
        "validate_worker_selection_certification_v1(",
        "reconstruct_authenticated_replace_replay_v2(",
    ):
        assert symbol not in source
    assert "run_human_interface_runtime_entry(" in source
