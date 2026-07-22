from __future__ import annotations

from copy import deepcopy
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

from aigol.runtime import human_decision_runtime as decision
from aigol.runtime import platform_core_existing_file_governance as governance
from aigol.runtime.human_interface_runtime_entry_service import (
    run_human_interface_runtime_entry,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash
from aigol.workers import filesystem_replace_worker as worker


def _transport(
    root: Path,
    state: dict,
    value: str,
    *,
    actor: str = ACTOR,
    session: str | None = None,
    workspace: str = "/isolated/repository",
) -> dict:
    return run_human_interface_runtime_entry(
        interface_name="in_memory_r06_adapter",
        session_id=session or root.name,
        human_requests=[],
        created_at=CREATED,
        runtime_root=root.parent,
        workspace=workspace,
        governed_runtime_runner=lambda *_args, **_kwargs: {},
        g31_application_state=state,
        g31_human_action=value,
        g31_human_actor_id=actor,
    )


def _request_evidence(state: dict, root: Path) -> dict:
    return {
        "candidate_capture": state["existing_file_mutation_candidate_capture"],
        "candidate_reconstruction": state[
            "existing_file_mutation_candidate_reconstruction"
        ],
        "mutation_decision_capture": state["human_mutation_decision_capture"],
        "mutation_decision_reconstruction": state[
            "human_mutation_decision_reconstruction"
        ],
        "acceptance_capture": state["generated_content_acceptance_capture"],
        "content_decision_capture": state[
            "human_content_acceptance_decision_capture"
        ],
        "binding_capture": state[
            "codex_replacement_acceptance_prerequisite_binding_capture"
        ],
        "repository_grounding_artifact": state["repository_grounding_artifact"],
        "activation_capture": state["codex_worker_activation_capture"],
        "activation_binding": state[
            "codex_worker_activation_binding_reconstruction"
        ],
        "governed_execution_capture": state["governed_worker_execution_capture"],
        "execution_candidate_capture": state["worker_execution_candidate_capture"],
        "session_root": root,
        "workspace": "/isolated/repository",
    }


def _forbid_execution(monkeypatch: pytest.MonkeyPatch) -> dict[str, int]:
    calls: dict[str, int] = {}
    targets = (
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
            raise AssertionError(f"forbidden R06 downstream call: {_symbol}")

        monkeypatch.setattr(owner, symbol, forbidden)
    return calls


def _contains_key(value: object, names: set[str]) -> bool:
    if isinstance(value, dict):
        return bool(names.intersection(value)) or any(
            _contains_key(item, names) for item in value.values()
        )
    if isinstance(value, list):
        return any(_contains_key(item, names) for item in value)
    return False


def test_common_entry_retains_one_authenticated_request_before_consumption_stage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R06-APPROVED")
    state.update({"terminal_prompt": "APPROVED?", "slash_command": "/approve"})
    forbidden = _forbid_execution(monkeypatch)
    calls = {"create": 0, "record": 0, "events": []}
    original_create = governance.create_g31_authenticated_replace_request
    original_record = worker.record_authenticated_replace_request_v2
    original_event = worker._persist_v2_event

    def create(*args, **kwargs):
        calls["create"] += 1
        return original_create(*args, **kwargs)

    def record(*args, **kwargs):
        calls["record"] += 1
        return original_record(*args, **kwargs)

    def event(request, key, event_type, payload, previous):
        calls["events"].append(key)
        return original_event(request, key, event_type, payload, previous)

    monkeypatch.setattr(governance, "create_g31_authenticated_replace_request", create)
    monkeypatch.setattr(worker, "record_authenticated_replace_request_v2", record)
    monkeypatch.setattr(worker, "_persist_v2_event", event)

    result = InMemoryAdapter(root).transport(state, decision.MUTATION_APPROVED)
    request = result["authenticated_replacement_request"]
    reconstruction = result["authenticated_replacement_request_reconstruction"]
    authorization = result["mutation_authorization_actor_replay_reconstruction"]
    candidate = result["existing_file_mutation_candidate_capture"][
        "existing_file_mutation_candidate_artifact"
    ]
    provenance = candidate["candidate_provenance"]

    assert calls == {"create": 1, "record": 1, "events": ["request", "consumption"]}
    assert request["authorization_id"] == authorization["authorization_id"]
    assert request["authorization_hash"] == authorization["authorization_hash"]
    assert request["authorization_replay_hash"] == authorization[
        "authorization_replay_hash"
    ]
    assert request["canonical_authorization_actor"] == authorization[
        "canonical_authorization_actor"
    ]
    assert request["candidate_id"] == candidate["candidate_id"]
    assert request["candidate_hash"] == candidate["artifact_hash"]
    assert request["candidate_replay_hash"] == result[
        "existing_file_mutation_candidate_capture"
    ]["candidate_replay_hash"]
    assert request["repository_identity"] == provenance["repository_identity"]
    assert request["repository_grounding_hash"] == provenance[
        "repository_grounding_hash"
    ]
    assert request["target_path"] == provenance["target_path"]
    assert request["preimage_sha256"] == provenance["preimage_sha256"]
    assert request["postimage_sha256"] == provenance["postimage_sha256"]
    assert request["mutation_decision_outcome"] == decision.MUTATION_APPROVED
    assert reconstruction["request_id"] == request["request_id"]
    assert reconstruction["request_hash"] == request["request_hash"]
    assert reconstruction["event_keys"] == ["request"]
    assert reconstruction["latest_event"] == "REQUEST_VALIDATED"
    assert reconstruction["latest_artifact"]["request_hash"] == request[
        "request_hash"
    ]
    assert result["replace_request_created"] is True
    assert result["authorization_consumed"] is True
    assert result["worker_invoked"] is False
    assert result["provider_invoked"] is False
    assert result["command_executed"] is False
    assert result["repository_mutated"] is False
    assert result["main_repository_mutated"] is False
    assert all(count == 0 for count in forbidden.values())
    assert len(list(Path(reconstruction["request_replay_reference"]).glob("*.json"))) == 2
    assert Path(request["destinations"]["consumption"]).exists()
    assert "Authorization Consumption Reached: True" in "\n".join(
        result["g31_canonical_presentations"]
    )
    assert not _contains_key(
        request, {"terminal_prompt", "slash_command", "interface_name"}
    )

    recreated = governance.create_g31_authenticated_replace_request(
        actor_replay_capture=result["mutation_authorization_actor_replay_capture"],
        authorization_capture=result["mutation_authorization_capture"],
        **_request_evidence(result, root),
    )
    assert recreated == request


def test_rejected_and_missing_authorization_create_zero_requests(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = {"create": 0, "record": 0}

    def forbidden_create(*_args, **_kwargs):
        calls["create"] += 1
        raise AssertionError("unauthorized path cannot construct a request")

    def forbidden_record(*_args, **_kwargs):
        calls["record"] += 1
        raise AssertionError("unauthorized path cannot record a request")

    monkeypatch.setattr(
        governance, "create_g31_authenticated_replace_request", forbidden_create
    )
    monkeypatch.setattr(worker, "record_authenticated_replace_request_v2", forbidden_record)
    rejected_root, rejected = _pending_state(tmp_path, monkeypatch, "R06-REJECTED")
    result = _transport(rejected_root, rejected, decision.REJECTED)
    assert result["mutation_authorized"] is False
    assert result["replace_request_created"] is False
    assert calls == {"create": 0, "record": 0}

    missing_root, missing = _pending_state(tmp_path, monkeypatch, "R06-MISSING-AUTH")
    monkeypatch.setattr(
        governance,
        "authorize_g31_approved_existing_file_mutation",
        lambda **_kwargs: {},
    )
    with pytest.raises(FailClosedRuntimeError):
        _transport(missing_root, missing, decision.MUTATION_APPROVED)
    assert calls == {"create": 0, "record": 0}
    assert not (missing_root / "G31_EXISTING_FILE_REPLACE_V2").exists()


@pytest.mark.parametrize("change", ("actor", "repository", "session"))
def test_actor_repository_and_session_mismatch_create_zero_request(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, change: str
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, f"R06-{change}")
    calls = {"create": 0}
    original = governance.create_g31_authenticated_replace_request

    def observed(*args, **kwargs):
        calls["create"] += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(governance, "create_g31_authenticated_replace_request", observed)
    kwargs = {}
    if change == "actor":
        kwargs["actor"] = "OTHER_ACTOR"
    elif change == "repository":
        kwargs["workspace"] = "/other/repository"
    else:
        kwargs["session"] = "OTHER-SESSION"
    with pytest.raises(FailClosedRuntimeError):
        _transport(root, state, decision.MUTATION_APPROVED, **kwargs)
    assert calls["create"] == 0
    assert not (root / "G31_EXISTING_FILE_REPLACE_V2").exists()


@pytest.mark.parametrize(
    "change",
    (
        "authorization",
        "authorization_replay",
        "decision",
        "decision_replay",
        "candidate",
        "candidate_replay",
        "grounding",
        "provenance",
        "target",
        "expected_state",
        "replacement",
    ),
)
def test_request_lineage_or_content_substitution_fails_before_recording(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, change: str
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, f"R06-TAMPER-{change}")
    original = governance.create_g31_authenticated_replace_request
    record_calls = {"count": 0}
    original_record = worker.record_authenticated_replace_request_v2

    def record(*args, **kwargs):
        record_calls["count"] += 1
        return original_record(*args, **kwargs)

    def tampered(*, actor_replay_capture, **evidence):
        actor_replay_capture = deepcopy(actor_replay_capture)
        evidence = deepcopy(evidence)
        if change == "authorization":
            actor_replay_capture["authorization_id"] = "SUBSTITUTED"
        elif change == "authorization_replay":
            actor_replay_capture["authorization_replay_hash"] = "SUBSTITUTED"
        elif change == "decision":
            evidence["mutation_decision_capture"][
                "human_mutation_decision_artifact"
            ]["decision_outcome"] = decision.REJECTED
        elif change == "decision_replay":
            evidence["mutation_decision_reconstruction"]["replay_hash"] = "SUBSTITUTED"
        elif change == "candidate":
            evidence["candidate_capture"][
                "existing_file_mutation_candidate_artifact"
            ]["candidate_id"] = "SUBSTITUTED"
        elif change == "candidate_replay":
            evidence["candidate_capture"]["candidate_replay_hash"] = "SUBSTITUTED"
        elif change == "grounding":
            evidence["repository_grounding_artifact"][
                "grounding_evidence_hash"
            ] = "SUBSTITUTED"
        elif change == "provenance":
            evidence["candidate_capture"][
                "existing_file_mutation_candidate_artifact"
            ]["candidate_provenance"]["repository_identity"] = "SUBSTITUTED"
        else:
            entry = evidence["binding_capture"]["implementation_manifest_capture"][
                "implementation_manifest_artifact"
            ]["file_entries"][0]
            if change == "target":
                entry["target_path"] = "other/target.py"
            elif change == "expected_state":
                entry["preimage_content"] = "substituted-before\n"
            else:
                entry["postimage_content"] = "substituted-after\n"
        return original(actor_replay_capture=actor_replay_capture, **evidence)

    monkeypatch.setattr(governance, "create_g31_authenticated_replace_request", tampered)
    monkeypatch.setattr(worker, "record_authenticated_replace_request_v2", record)
    with pytest.raises(FailClosedRuntimeError):
        _transport(root, state, decision.MUTATION_APPROVED)
    assert record_calls["count"] == 0
    assert not (root / "G31_EXISTING_FILE_REPLACE_V2").exists()


def test_duplicate_and_conflicting_request_replay_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R06-DUPLICATE")
    result = _transport(root, state, decision.MUTATION_APPROVED)
    request = result["authenticated_replacement_request"]
    before = sorted(
        Path(result["authenticated_replacement_request_replay_reference"]).glob("*.json")
    )
    with pytest.raises(FailClosedRuntimeError, match="already exists or conflicts"):
        worker.record_authenticated_replace_request_v2(request)
    conflicting = deepcopy(request)
    conflicting["request_id"] = request["request_id"] + ":CONFLICT"
    conflicting["request_hash"] = replay_hash(
        {key: value for key, value in conflicting.items() if key != "request_hash"}
    )
    with pytest.raises(FailClosedRuntimeError, match="already exists or conflicts"):
        worker.record_authenticated_replace_request_v2(conflicting)
    assert before == sorted(
        Path(result["authenticated_replacement_request_replay_reference"]).glob("*.json")
    )
    assert Path(request["destinations"]["consumption"]).exists()


def test_request_replay_tamper_fails_reconstruction(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R06-REPLAY-TAMPER")
    result = _transport(root, state, decision.MUTATION_APPROVED)
    request = result["authenticated_replacement_request"]
    replay_path = Path(request["destinations"]["request"])
    replay_path.write_text(
        replay_path.read_text(encoding="utf-8").replace(
            "REQUEST_VALIDATED", "REQUEST_SUBSTITUTED"
        ),
        encoding="utf-8",
    )
    with pytest.raises(FailClosedRuntimeError):
        worker.reconstruct_authenticated_replace_replay_v2(request)
    assert Path(request["destinations"]["consumption"]).exists()


def test_common_entry_and_adapter_import_boundaries() -> None:
    repository = Path(__file__).resolve().parents[1]
    aicli = (repository / "aigol/cli/aicli.py").read_text(encoding="utf-8")
    service = (
        repository / "aigol/runtime/human_interface_runtime_entry_service.py"
    ).read_text(encoding="utf-8")
    canonical = (
        repository / "aigol/runtime/platform_core_existing_file_governance.py"
    ).read_text(encoding="utf-8")
    request_owner = (
        repository / "aigol/workers/filesystem_replace_worker.py"
    ).read_text(encoding="utf-8")

    assert "run_human_interface_runtime_entry(" in aicli
    for symbol in (
        "create_g31_authenticated_replace_request(",
        "record_authenticated_replace_request_v2(",
        "consume_authenticated_replace_authorization_v2(",
        "reconstruct_authenticated_replace_replay_v2(",
        "_execute_authenticated_replace_v2(",
        "_recover_authenticated_replace_v2(",
    ):
        assert symbol not in aicli
    assert "create_g31_authenticated_replace_request(" in service
    assert "record_authenticated_replace_request_v2(" in service
    assert "consume_authenticated_replace_authorization_v2(" in service
    assert "_execute_authenticated_replace_v2(" not in service
    assert "_recover_authenticated_replace_v2(" not in service
    assert "aigol.cli" not in service
    assert "aigol.cli" not in canonical
    assert "aigol.cli" not in request_owner
    assert "aicli" not in InMemoryAdapter.transport.__code__.co_names
