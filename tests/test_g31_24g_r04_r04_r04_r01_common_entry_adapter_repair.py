from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path

import pytest

from aigol.runtime import human_decision_runtime as decision
from aigol.runtime import codex_worker_activation_binding_runtime as activation
from aigol.runtime import platform_core_existing_file_governance as governance
from aigol.runtime import platform_core_existing_file_mutation_candidate as candidate
from aigol.runtime.human_interface_runtime_entry_service import (
    G31_APPLICATION_TRANSITION_VERSION,
    G31_MUTATION_DECISION,
    run_human_interface_runtime_entry,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash
from aigol.workers import filesystem_replace_worker


CREATED = "2026-07-21T00:00:00Z"
ACTOR = "HUMAN_OPERATOR"


class InMemoryAdapter:
    """Test transport: no AiCLI import and no low-level sequencing."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def transport(self, state: dict, value: str, *, actor: str = ACTOR) -> dict:
        return run_human_interface_runtime_entry(
            interface_name="in_memory_test_adapter",
            session_id=self.root.name,
            human_requests=[],
            created_at=CREATED,
            runtime_root=self.root.parent,
            workspace="/isolated/repository",
            governed_runtime_runner=lambda *_args, **_kwargs: {},
            g31_application_state=state,
            g31_human_action=value,
            g31_human_actor_id=actor,
        )


def _pending_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str
) -> tuple[Path, dict]:
    root = tmp_path / name
    source = "before\n"
    replacement = "after\n"
    grounding = {
        "grounding_evidence_hash": "grounding-hash",
        "workspace_root": "/isolated/repository",
    }
    provenance = {
        "session_id": root.name,
        "repository_identity": "repo-identity",
        "repository_root": "/isolated/repository",
        "repository_grounding_hash": "grounding-hash",
        "accepted_result_hash": "accepted-hash",
        "acceptance_hash": "acceptance-hash",
        "content_decision_hash": "content-decision-hash",
        "prerequisite_hash": "prerequisite-hash",
        "manifest_hash": "manifest-hash",
        "target_path": "aigol/runtime/human_interface.py",
        "preimage_sha256": "sha256:" + sha256(source.encode()).hexdigest(),
        "postimage_sha256": "sha256:" + sha256(replacement.encode()).hexdigest(),
        "source_mode": "0o100644",
        "replacement_mode": "0o100644",
        "content_validation_hash": "content-validation-hash",
        "test_validation_hash": "test-validation-hash",
        "disposable_validation_hash": "disposable-validation-hash",
        "operation": "REPLACE_CONTENT",
    }
    provenance["binding_hash"] = replay_hash(provenance)
    artifact = {
        "artifact_type": candidate.EXISTING_FILE_MUTATION_CANDIDATE_ARTIFACT_V2,
        "runtime_version": candidate.G31_EXISTING_FILE_MUTATION_CANDIDATE_VERSION,
        "candidate_id": f"{name}-CANDIDATE",
        "session_id": root.name,
        "operation": "REPLACE_CONTENT",
        "target_path": provenance["target_path"],
        "file_count": 1,
        "candidate_provenance": provenance,
        "candidate_provenance_binding_hash": provenance["binding_hash"],
        "created_by": ACTOR,
        "created_at": CREATED,
        "human_mutation_decision_recorded": False,
        "mutation_authorized": False,
        "main_repository_mutated": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "command_executed": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    candidate_capture = {
        "existing_file_mutation_candidate_artifact": artifact,
        "candidate_replay_reference": str(root / "CANDIDATE"),
        "candidate_replay_hash": "candidate-replay-hash",
        "existing_file_mutation_candidate_created": True,
        "result_accepted": True,
        "human_mutation_decision_recorded": False,
        "mutation_authorized": False,
        "main_repository_mutated": False,
    }

    def reconstruct_candidate(**_kwargs):
        return {
            "candidate_id": artifact["candidate_id"],
            "candidate_hash": artifact["artifact_hash"],
            "candidate_provenance_binding_hash": provenance["binding_hash"],
            "replay_artifact_count": 3,
            "replay_hash": "candidate-replay-hash",
            "result_accepted": True,
            "human_mutation_decision_recorded": False,
            "mutation_authorized": False,
            "main_repository_mutated": False,
        }

    monkeypatch.setattr(
        candidate,
        "reconstruct_g31_accepted_existing_file_mutation_candidate_replay",
        reconstruct_candidate,
    )
    candidate_reconstruction = reconstruct_candidate()
    activation_binding = {
        "lineage": {"grounding": grounding},
        "activation_replay_reference": str(root / "ACTIVATION"),
        "activation_replay_hash": "activation-replay-hash",
        "activation_approval_artifact": {
            "approval_id": f"{name}-ACTIVATION",
            "artifact_hash": "activation-approval-hash",
        },
    }
    monkeypatch.setattr(
        activation,
        "reconstruct_codex_worker_activation_binding",
        lambda **_kwargs: deepcopy(activation_binding),
    )
    acceptance: dict = {}
    content: dict = {}
    binding: dict = {
        "implementation_manifest_capture": {
            "implementation_manifest_artifact": {
                "artifact_hash": provenance["manifest_hash"],
                "file_entries": [
                    {
                        "operation": "REPLACE_CONTENT",
                        "target_path": provenance["target_path"],
                        "preimage_content": source,
                        "postimage_content": replacement,
                        "preimage_sha256": provenance["preimage_sha256"],
                        "postimage_sha256": provenance["postimage_sha256"],
                        "file_mode": provenance["source_mode"],
                        "postimage_file_mode": provenance["replacement_mode"],
                    }
                ],
            }
        }
    }
    context = decision.prepare_existing_file_mutation_decision_context(
        context_id=f"{name}-DECISION",
        candidate_capture=candidate_capture,
        acceptance_capture=acceptance,
        content_decision_capture=content,
        binding_capture=binding,
        repository_grounding_artifact=grounding,
        human_actor_id=ACTOR,
        presented_at=CREATED,
        session_root=root,
        replay_dir=root / "DECISION",
    )
    return root, {
        "existing_file_mutation_candidate_capture": candidate_capture,
        "existing_file_mutation_candidate_reconstruction": candidate_reconstruction,
        "generated_content_acceptance_capture": acceptance,
        "human_content_acceptance_decision_capture": content,
        "codex_replacement_acceptance_prerequisite_binding_capture": binding,
        "repository_grounding_artifact": grounding,
        "codex_worker_activation_capture": {
            "activation_replay_reference": str(root / "ACTIVATION")
        },
        "codex_worker_activation_binding_reconstruction": activation_binding,
        "governed_worker_execution_capture": {},
        "worker_execution_candidate_capture": {},
        "result_accepted": True,
        "g31_pending_action": {
            "action_type": G31_MUTATION_DECISION,
            "valid_values": [decision.MUTATION_APPROVED, decision.REJECTED],
            "context": context,
        },
    }


@pytest.mark.parametrize(
    ("outcome", "approved"),
    ((decision.MUTATION_APPROVED, True), (decision.REJECTED, False)),
)
def test_in_memory_adapter_uses_common_entry_for_exact_v3_decision(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    outcome: str,
    approved: bool,
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, f"COMMON-{outcome}")
    calls: dict[str, int] = {}
    original_authorize = governance.authorize_g31_approved_existing_file_mutation
    original_bind = governance.bind_g31_mutation_authorization_actor_and_replay
    for symbol, original in (
        ("authorize_g31_approved_existing_file_mutation", original_authorize),
        ("bind_g31_mutation_authorization_actor_and_replay", original_bind),
    ):
        calls[symbol] = 0

        def observed(*args, _symbol=symbol, _original=original, **kwargs):
            calls[_symbol] += 1
            return _original(*args, **kwargs)

        monkeypatch.setattr(governance, symbol, observed)
    for owner, symbol in (
        (governance, "create_g31_authenticated_replace_request"),
        (filesystem_replace_worker, "record_authenticated_replace_request_v2"),
    ):
        original = getattr(owner, symbol)
        calls[symbol] = 0

        def observed(*args, _symbol=symbol, _original=original, **kwargs):
            calls[_symbol] += 1
            return _original(*args, **kwargs)

        monkeypatch.setattr(owner, symbol, observed)
    for owner, symbol in (
        (governance, "execute_g31_authenticated_replace"),
        (filesystem_replace_worker, "execute_filesystem_replace_request"),
        (filesystem_replace_worker, "_execute_authenticated_replace_v2"),
        (filesystem_replace_worker, "_recover_authenticated_replace_v2"),
    ):
        calls[symbol] = 0

        def forbidden(*_args, _symbol=symbol, **_kwargs):
            calls[_symbol] += 1
            raise AssertionError(f"forbidden downstream call: {_symbol}")

        monkeypatch.setattr(owner, symbol, forbidden)

    result = InMemoryAdapter(root).transport(state, outcome)
    artifact = result["human_mutation_decision_capture"][
        "human_mutation_decision_artifact"
    ]
    assert result["g31_application_transition_version"] == G31_APPLICATION_TRANSITION_VERSION
    assert result["g31_application_state_authority"] == (
        "CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY"
    )
    assert result["g31_application_interface_transport"] == "in_memory_test_adapter"
    assert result["g31_pending_action"] is None
    assert artifact["decision_outcome"] == outcome
    assert artifact["decided_by"] == ACTOR
    assert result["human_mutation_decision_reconstruction"]["replay_artifact_count"] == 4
    assert result["mutation_decision_approved"] is approved
    assert result["mutation_authorized"] is approved
    assert result["authorization_actor_bound"] is approved
    assert result["authorization_replay_recorded"] is approved
    assert result["replace_request_created"] is approved
    assert result["authorization_consumed"] is approved
    assert result["repository_mutated"] is False
    assert calls["authorize_g31_approved_existing_file_mutation"] == int(approved)
    assert calls["bind_g31_mutation_authorization_actor_and_replay"] == int(approved)
    assert calls["create_g31_authenticated_replace_request"] == int(approved)
    assert calls["record_authenticated_replace_request_v2"] == int(approved)
    assert all(
        calls[symbol] == 0
        for symbol in (
            "execute_g31_authenticated_replace",
            "execute_filesystem_replace_request",
            "_execute_authenticated_replace_v2",
            "_recover_authenticated_replace_v2",
        )
    )
    assert "aicli" not in InMemoryAdapter.transport.__code__.co_names


def test_common_entry_fails_closed_on_invalid_actor_duplicate_and_ui_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "COMMON-FAIL-CLOSED")
    adapter = InMemoryAdapter(root)
    unchanged = deepcopy(state)
    unchanged["terminal_prompt"] = "APPROVED?"
    unchanged["slash_command"] = "/approve"

    for invalid in ("APPROVE", "ACCEPTED", "YES", "/approve"):
        with pytest.raises(FailClosedRuntimeError, match="invalid"):
            adapter.transport(unchanged, invalid)
    with pytest.raises(FailClosedRuntimeError):
        adapter.transport(unchanged, decision.MUTATION_APPROVED, actor="OTHER_ACTOR")

    result = adapter.transport(unchanged, decision.MUTATION_APPROVED)
    artifact = result["human_mutation_decision_capture"][
        "human_mutation_decision_artifact"
    ]
    assert "terminal_prompt" not in artifact
    assert "slash_command" not in artifact
    with pytest.raises(FailClosedRuntimeError):
        adapter.transport(state, decision.MUTATION_APPROVED)


def test_static_adapter_and_import_boundaries() -> None:
    repository = Path(__file__).resolve().parents[1]
    aicli_source = (repository / "aigol/cli/aicli.py").read_text(encoding="utf-8")
    forbidden = (
        "record_existing_file_mutation_decision(",
        "reconstruct_existing_file_mutation_decision_replay(",
        "prepare_existing_file_mutation_decision_context(",
        "create_g31_accepted_existing_file_mutation_candidate(",
        "accept_generated_content_from_content_acceptance_decision(",
        "_record_contextual_execution_decision(",
    )
    assert all(symbol not in aicli_source for symbol in forbidden)
    assert "run_human_interface_runtime_entry(" in aicli_source
    canonical_runtime_paths = (
        repository / "aigol/runtime/human_interface_runtime_entry_service.py",
        repository / "aigol/runtime/human_decision_runtime.py",
        repository / "aigol/runtime/platform_core_existing_file_mutation_candidate.py",
        repository / "aigol/runtime/generated_content_acceptance_runtime.py",
    )
    for path in canonical_runtime_paths:
        assert "aigol.cli" not in path.read_text(encoding="utf-8")
