from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent))
from test_g31_24g_r04_r04_r04_r01_common_entry_adapter_repair import (  # noqa: E402
    ACTOR,
    CREATED,
    InMemoryAdapter,
    _pending_state,
)
import test_g31_24g_r04_r04_r02_existing_replace_owner_hardening as r02  # noqa: E402

from aigol.runtime import human_decision_runtime as decision
from aigol.runtime import human_interface_runtime_entry_service as entry
from aigol.runtime import platform_core_existing_file_governance as governance
from aigol.runtime.human_interface_runtime_entry_service import (
    run_human_interface_runtime_entry,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash
from aigol.workers import filesystem_replace_worker as worker


def _transport(root: Path, state: dict, value: str) -> dict:
    return run_human_interface_runtime_entry(
        interface_name="in_memory_r07_adapter",
        session_id=root.name,
        human_requests=[],
        created_at=CREATED,
        runtime_root=root.parent,
        workspace="/isolated/repository",
        governed_runtime_runner=lambda *_args, **_kwargs: {},
        g31_application_state=state,
        g31_human_action=value,
        g31_human_actor_id=ACTOR,
    )


def _full_request(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[dict, Path]:
    common, authorization, actor, target = r02._public_evidence(tmp_path, monkeypatch)
    request = governance.create_g31_authenticated_replace_request(
        actor_replay_capture=actor,
        authorization_capture=authorization,
        **common,
    )
    worker.record_authenticated_replace_request_v2(request)
    return request, target


def _rehash(value: dict) -> dict:
    value["request_hash"] = replay_hash(
        {key: item for key, item in value.items() if key != "request_hash"}
    )
    return value


def _rewrite_wrapper(path: Path, change) -> None:
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    change(wrapper)
    artifact = wrapper["artifact"]
    artifact["artifact_hash"] = replay_hash(
        {key: value for key, value in artifact.items() if key != "artifact_hash"}
    )
    wrapper["replay_hash"] = replay_hash(
        {key: value for key, value in wrapper.items() if key != "replay_hash"}
    )
    path.write_text(json.dumps(wrapper), encoding="utf-8")


def _forbid_downstream(monkeypatch: pytest.MonkeyPatch) -> dict[str, int]:
    calls: dict[str, int] = {}
    targets = (
        (governance, "execute_g31_authenticated_replace"),
        (governance, "recover_g31_authenticated_replace"),
        (worker, "execute_filesystem_replace_request"),
        (worker, "_execute_authenticated_replace_v2"),
        (worker, "_recover_authenticated_replace_v2"),
        (worker, "_open_v2_target"),
        (worker, "_atomic_restore_v2"),
        (entry, "select_authorized_grounded_worker"),
    )
    for owner, symbol in targets:
        calls[symbol] = 0

        def forbidden(*_args, _symbol=symbol, **_kwargs):
            calls[_symbol] += 1
            raise AssertionError(f"forbidden R07 downstream call: {_symbol}")

        monkeypatch.setattr(owner, symbol, forbidden)
    return calls


def test_common_entry_consumes_exact_request_once_and_stops_before_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R07-CONSUME")
    state.update({"terminal_prompt": "APPROVED?", "slash_command": "/approve"})
    forbidden = _forbid_downstream(monkeypatch)
    calls = {"consume": 0, "events": []}
    original_consume = worker.consume_authenticated_replace_authorization_v2
    original_event = worker._persist_v2_event

    def consume(request):
        calls["consume"] += 1
        return original_consume(request)

    def event(request, key, event_type, payload, previous):
        calls["events"].append(key)
        return original_event(request, key, event_type, payload, previous)

    monkeypatch.setattr(
        worker, "consume_authenticated_replace_authorization_v2", consume
    )
    monkeypatch.setattr(worker, "_persist_v2_event", event)
    result = InMemoryAdapter(root).transport(state, decision.MUTATION_APPROVED)
    request = result["authenticated_replacement_request"]
    request_stage = result["authenticated_replacement_request_reconstruction"]
    consumption = result["authorization_consumption_reconstruction"]

    assert calls == {"consume": 1, "events": ["request", "consumption"]}
    assert request_stage["event_keys"] == ["request"]
    assert consumption["event_keys"] == ["request", "consumption"]
    assert consumption["latest_event"] == "AUTHORIZATION_CONSUMPTION_CLAIMED"
    assert consumption["request_hash"] == request["request_hash"]
    assert consumption["authorization_id"] == request["authorization_id"]
    assert consumption["authorization_hash"] == request["authorization_hash"]
    assert consumption["consumption_identity"] == request["authorization_hash"]
    assert consumption["request_stage_replay_hash"] == request_stage["replay_hash"]
    assert consumption["latest_artifact"]["payload"] == {
        "consumption_identity": request["authorization_hash"]
    }
    assert result["authorization_consumed"] is True
    assert result["replace_request_created"] is True
    assert result["worker_selected"] is True
    assert result["selected_resource_id"] == "FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER"
    assert result["worker_selection_status"] == "RESOURCE_SELECTION_SUCCEEDED"
    assert result["worker_assigned"] is True
    assert result["worker_dispatched"] is True
    assert result["worker_invoked"] is True
    assert result["provider_invoked"] is False
    assert result["command_executed"] is False
    assert result["repository_mutated"] is False
    assert result["main_repository_mutated"] is False
    assert all(count == 0 for count in forbidden.values())
    assert sorted(
        path.name
        for path in Path(consumption["request_replay_reference"]).glob("*.json")
    ) == ["000_request.json", "001_consumption.json"]
    rendered = "\n".join(result["g31_canonical_presentations"])
    assert "Authorization Consumed: True" in rendered
    assert "Authorization Consumption Reached: True" in rendered
    assert "Worker Selection Reached: True" in rendered
    assert "selected_resource_id: FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER" in rendered
    assert "terminal_prompt" not in request
    assert "slash_command" not in request


def test_rejected_missing_and_unreconstructible_request_consume_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = {"consume": 0}
    original_consume = worker.consume_authenticated_replace_authorization_v2

    def consume(request):
        calls["consume"] += 1
        return original_consume(request)

    monkeypatch.setattr(
        worker, "consume_authenticated_replace_authorization_v2", consume
    )
    rejected_root, rejected = _pending_state(tmp_path, monkeypatch, "R07-REJECTED")
    rejected_result = _transport(rejected_root, rejected, decision.REJECTED)
    assert rejected_result["authorization_consumed"] is False
    assert calls["consume"] == 0

    missing_root, missing = _pending_state(tmp_path, monkeypatch, "R07-MISSING")
    original_record = worker.record_authenticated_replace_request_v2

    def omit_record(request):
        validated = worker.validate_authenticated_replace_request_v2(request)
        return {
            "request_id": validated["request_id"],
            "request_hash": validated["request_hash"],
            "request_replay_reference": str(
                Path(validated["destinations"]["request"]).parent
            ),
            "replay_hash": "ABSENT",
        }

    monkeypatch.setattr(worker, "record_authenticated_replace_request_v2", omit_record)
    with pytest.raises(FailClosedRuntimeError, match="Replay is unavailable"):
        _transport(missing_root, missing, decision.MUTATION_APPROVED)
    assert calls["consume"] == 1
    assert not (missing_root / "G31_EXISTING_FILE_REPLACE_V2").exists()

    stale_root, stale = _pending_state(tmp_path, monkeypatch, "R07-STALE")

    def corrupt_record(request):
        reconstruction = original_record(request)
        Path(request["destinations"]["request"]).write_text("{}", encoding="utf-8")
        return reconstruction

    monkeypatch.setattr(worker, "record_authenticated_replace_request_v2", corrupt_record)
    with pytest.raises(FailClosedRuntimeError):
        _transport(stale_root, stale, decision.MUTATION_APPROVED)
    assert calls["consume"] == 2
    request_root = stale_root / "G31_EXISTING_FILE_REPLACE_V2"
    assert not list(request_root.rglob("001_consumption.json"))


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("authorization_id", "SUBSTITUTED"),
        ("authorization_hash", "SUBSTITUTED"),
        ("authorization_status", "REJECTED"),
        ("authorization_replay_hash", "SUBSTITUTED"),
        ("canonical_authorization_actor", "OTHER_ACTOR"),
        ("repository_identity", "OTHER_REPOSITORY"),
        ("session_id", "OTHER_SESSION"),
        ("mutation_decision_hash", "SUBSTITUTED"),
        ("mutation_decision_replay_hash", "SUBSTITUTED"),
        ("candidate_hash", "SUBSTITUTED"),
        ("candidate_replay_hash", "SUBSTITUTED"),
        ("repository_grounding_hash", "SUBSTITUTED"),
        ("candidate_provenance_binding_hash", "SUBSTITUTED"),
        ("target_path", "other/target.txt"),
        ("preimage_sha256", "sha256:" + "0" * 64),
        ("postimage_sha256", "sha256:" + "1" * 64),
        ("replacement_content", "substituted replacement\n"),
        ("replacement_content_hash", "SUBSTITUTED"),
        ("source_mode", "0o100755"),
        ("replacement_mode", "0o100755"),
        ("worker_id", "SUBSTITUTED_WORKER"),
    ),
)
def test_changed_request_identity_or_evidence_fails_before_consumption(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    value: str,
) -> None:
    request, target = _full_request(tmp_path, monkeypatch)
    changed = _rehash({**deepcopy(request), field: value})
    with pytest.raises(FailClosedRuntimeError):
        worker.consume_authenticated_replace_authorization_v2(changed)
    assert not Path(request["destinations"]["consumption"]).exists()
    assert target.read_text(encoding="utf-8") != "replacement bytes\n"


def test_changed_destination_and_request_hash_fail_before_consumption(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    request, _ = _full_request(tmp_path, monkeypatch)
    changed_destination = deepcopy(request)
    changed_destination["destinations"]["consumption"] += ".substituted"
    _rehash(changed_destination)
    with pytest.raises(FailClosedRuntimeError):
        worker.consume_authenticated_replace_authorization_v2(changed_destination)
    changed_hash = {**request, "request_hash": "SUBSTITUTED"}
    with pytest.raises(FailClosedRuntimeError):
        worker.consume_authenticated_replace_authorization_v2(changed_hash)
    assert not Path(request["destinations"]["consumption"]).exists()


def test_sequential_duplicate_consumption_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    request, target = _full_request(tmp_path, monkeypatch)
    first = worker.consume_authenticated_replace_authorization_v2(request)
    with pytest.raises(FailClosedRuntimeError, match="request-only Replay"):
        worker.consume_authenticated_replace_authorization_v2(request)
    assert first["authorization_consumed"] is True
    assert worker.reconstruct_authenticated_replace_replay_v2(request)[
        "event_keys"
    ] == ["request", "consumption"]
    assert target.read_text(encoding="utf-8") != "replacement bytes\n"


def test_concurrent_consumption_has_exactly_one_immutable_winner(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    request, target = _full_request(tmp_path, monkeypatch)

    def consume() -> dict:
        return worker.consume_authenticated_replace_authorization_v2(request)

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(consume) for _ in range(2)]
    successes = [future.result() for future in futures if future.exception() is None]
    failures = [future.exception() for future in futures if future.exception() is not None]
    assert len(successes) == 1
    assert len(failures) == 1
    assert isinstance(failures[0], FailClosedRuntimeError)
    assert successes[0]["consumption_identity"] == request["authorization_hash"]
    assert worker.reconstruct_authenticated_replace_replay_v2(request)[
        "event_keys"
    ] == ["request", "consumption"]
    assert target.read_text(encoding="utf-8") != "replacement bytes\n"


@pytest.mark.parametrize(
    "case",
    ("removed", "unexpected", "reordered", "request_substituted", "consumption_substituted"),
)
def test_request_and_consumption_replay_tamper_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, case: str
) -> None:
    request, _ = _full_request(tmp_path, monkeypatch)
    request_path = Path(request["destinations"]["request"])
    consumption_path = Path(request["destinations"]["consumption"])
    if case == "removed":
        request_path.unlink()
        with pytest.raises(FailClosedRuntimeError):
            worker.consume_authenticated_replace_authorization_v2(request)
        assert not consumption_path.exists()
        return
    if case == "unexpected":
        request_path.parent.joinpath("unexpected.json").write_text("{}", encoding="utf-8")
        with pytest.raises(FailClosedRuntimeError):
            worker.consume_authenticated_replace_authorization_v2(request)
        assert not consumption_path.exists()
        return
    consumption = worker.consume_authenticated_replace_authorization_v2(request)
    if case == "reordered":
        _rewrite_wrapper(
            consumption_path,
            lambda wrapper: wrapper.update({"previous_replay_hash": None}),
        )
    elif case == "request_substituted":
        _rewrite_wrapper(
            request_path,
            lambda wrapper: wrapper["artifact"].update(
                {"event_type": "REQUEST_SUBSTITUTED"}
            ),
        )
    else:
        _rewrite_wrapper(
            consumption_path,
            lambda wrapper: wrapper["artifact"].update(
                {"payload": {"consumption_identity": "SUBSTITUTED"}}
            ),
        )
    with pytest.raises(FailClosedRuntimeError):
        worker.reconstruct_authenticated_replace_replay_v2(request)
    assert consumption["authorization_consumed"] is True


def test_conflicting_lifecycle_state_fails_before_consumption(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    request, _ = _full_request(tmp_path, monkeypatch)
    request_replay = worker.reconstruct_authenticated_replace_replay_v2(request)
    worker._persist_v2_event(
        request,
        "journal",
        "PRE_WRITE_JOURNAL_PERSISTED",
        {"conflicting": True},
        request_replay["last_wrapper_hash"],
    )
    with pytest.raises(FailClosedRuntimeError, match="request-only Replay"):
        worker.consume_authenticated_replace_authorization_v2(request)
    assert not Path(request["destinations"]["consumption"]).exists()


def test_aicli_and_canonical_import_boundaries() -> None:
    repository = Path(__file__).resolve().parents[1]
    aicli = (repository / "aigol/cli/aicli.py").read_text(encoding="utf-8")
    service = (
        repository / "aigol/runtime/human_interface_runtime_entry_service.py"
    ).read_text(encoding="utf-8")
    owner = (
        repository / "aigol/workers/filesystem_replace_worker.py"
    ).read_text(encoding="utf-8")
    assert "run_human_interface_runtime_entry(" in aicli
    for symbol in (
        "consume_authenticated_replace_authorization_v2(",
        "_persist_v2_event(",
        "_execute_authenticated_replace_v2(",
        "_recover_authenticated_replace_v2(",
    ):
        assert symbol not in aicli
    assert "consume_authenticated_replace_authorization_v2(" in service
    assert "_persist_v2_event(" not in service
    assert "_execute_authenticated_replace_v2(" not in service
    assert "_recover_authenticated_replace_v2(" not in service
    assert "aigol.cli" not in service
    assert "aigol.cli" not in owner
    assert "aicli" not in InMemoryAdapter.transport.__code__.co_names
