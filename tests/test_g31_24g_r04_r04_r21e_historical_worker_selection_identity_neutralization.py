from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from aigol.runtime import worker_assignment_runtime as assignment
from aigol.runtime import worker_invocation_request_runtime as invocation
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash
from test_g31_09_distinct_human_execution_decision_binding import CREATED_AT
from test_g31_11b_authorized_existing_worker_selection_binding import _selected
from test_g31_12b_g31_selection_to_g24_worker_assignment_binding import (
    _request_and_assignment,
)


NEUTRAL_WORKER_ID = "REPLAY_CAPABLE_WORKER"


def _rehash_artifact(artifact: dict) -> dict:
    changed = deepcopy(artifact)
    changed.pop("artifact_hash", None)
    changed["artifact_hash"] = replay_hash(changed)
    return changed


def _neutralized_request(request: dict) -> dict:
    changed = deepcopy(request)
    selection = changed["g31_lineage"]["resource_selection_artifact"]
    selection["selected_resource_id"] = NEUTRAL_WORKER_ID
    selection["selected_resource_category"] = "WORKER"
    changed["g31_lineage"]["resource_selection_artifact"] = _rehash_artifact(
        selection
    )
    changed["target_worker_family"] = NEUTRAL_WORKER_ID
    changed["request_hash"] = invocation._request_hash(changed)
    return _rehash_artifact(changed)


def test_historical_codex_lifecycle_and_replay_formats_remain_unchanged(
    tmp_path: Path,
) -> None:
    request, capture, _, root = _request_and_assignment(
        tmp_path,
        "R21E-HISTORICAL",
    )

    assert request["request_status"] == invocation.WORKER_INVOCATION_REQUEST_CREATED
    assert capture["assignment_status"] == assignment.WORKER_ASSIGNED
    assert request["target_worker_family"] == capture["worker_id"] == "CODEX"
    assert sorted(
        path.name for path in (root / "worker-request").glob("*.json")
    ) == [
        f"{index:03d}_{step}.json"
        for index, step in enumerate(invocation.REPLAY_STEPS)
    ]
    assert sorted(
        path.name for path in (root / "worker-assignment").glob("*.json")
    ) == [
        f"{index:03d}_{step}.json"
        for index, step in enumerate(assignment.REPLAY_STEPS)
    ]


def test_generic_request_and_assignment_consume_worker_neutral_identity(
    tmp_path: Path,
) -> None:
    request, _, _, _ = _request_and_assignment(
        tmp_path,
        "R21E-NEUTRAL",
        assign=False,
    )
    artifact = _neutralized_request(
        request["worker_invocation_request_artifact"]
    )

    invocation._validate_request_artifact(artifact)
    worker = assignment.default_worker_registry_for_request(
        artifact,
        created_at=CREATED_AT,
    )[0]

    assert worker["worker_id"] == NEUTRAL_WORKER_ID
    assert worker["worker_family"] == NEUTRAL_WORKER_ID
    assert worker["selected_resource_category"] == "WORKER"
    assert worker["selected_role_type"] == invocation.CANONICAL_WORKER_ROLE
    assert worker["selected_authority_profile"] == (
        invocation.NON_AUTHORITATIVE_WORKER_PROFILE
    )
    assert worker["provider_authority"] is False


@pytest.mark.parametrize(
    ("field", "value", "target"),
    (
        ("selected_resource_id", "", NEUTRAL_WORKER_ID),
        ("selected_resource_id", "OTHER_WORKER", NEUTRAL_WORKER_ID),
        ("selected_resource_category", "PROVIDER", NEUTRAL_WORKER_ID),
        ("selected_role_type", "PROVIDER_ROLE", NEUTRAL_WORKER_ID),
        (
            "selected_authority_profile",
            "PROVIDER_PROPOSAL_ONLY",
            NEUTRAL_WORKER_ID,
        ),
    ),
)
def test_unsupported_or_substituted_historical_identity_fails_closed(
    tmp_path: Path,
    field: str,
    value: str,
    target: str,
) -> None:
    request, _, _, _ = _request_and_assignment(
        tmp_path,
        f"R21E-INVALID-{field}-{value}",
        assign=False,
    )
    selection = deepcopy(
        request["worker_invocation_request_artifact"]["g31_lineage"][
            "resource_selection_artifact"
        ]
    )
    selection["selected_resource_id"] = NEUTRAL_WORKER_ID
    selection["selected_resource_category"] = "WORKER"
    selection[field] = value

    with pytest.raises(FailClosedRuntimeError):
        invocation.validate_historical_worker_selection_identity(
            selection,
            target_worker_family=target,
        )


def test_cross_family_substitution_fails_before_request_evidence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    selection, authorization, _, root = _selected(
        tmp_path,
        "R21E-CROSS-FAMILY",
    )
    original = invocation._classification_artifact

    def substituted_classification(*args, **kwargs) -> dict:
        classification = original(*args, **kwargs)
        classification["target_worker_family"] = "SUBSTITUTED_WORKER"
        return _rehash_artifact(classification)

    monkeypatch.setattr(
        invocation,
        "_classification_artifact",
        substituted_classification,
    )
    replay_dir = root / "failed-request"
    capture = invocation.create_worker_invocation_request(
        invocation_request_id="R21E-CROSS-FAMILY:REQUEST",
        execution_authorization_replay_reference=authorization[
            "execution_authorization_replay_reference"
        ],
        resource_selection_replay_reference=selection[
            "resource_selection_replay_reference"
        ],
        requested_by="G31_R21E_TEST",
        requested_at=CREATED_AT,
        replay_dir=replay_dir,
    )

    assert capture["request_status"] == invocation.FAILED_CLOSED
    assert capture["worker_invocation_request_artifact"] is None
    assert not (replay_dir / "000_invocation_request_evidence_recorded.json").exists()
    assert not (
        replay_dir / "001_invocation_request_classification_recorded.json"
    ).exists()
    assert not (
        replay_dir / "002_invocation_request_artifact_recorded.json"
    ).exists()


def test_cross_session_selection_fails_before_request_evidence(
    tmp_path: Path,
) -> None:
    _, authorization, _, root = _selected(tmp_path, "R21E-SESSION-A")
    other_selection, _, _, _ = _selected(tmp_path, "R21E-SESSION-B")
    replay_dir = root / "failed-request"

    capture = invocation.create_worker_invocation_request(
        invocation_request_id="R21E-CROSS-SESSION:REQUEST",
        execution_authorization_replay_reference=authorization[
            "execution_authorization_replay_reference"
        ],
        resource_selection_replay_reference=other_selection[
            "resource_selection_replay_reference"
        ],
        requested_by="G31_R21E_TEST",
        requested_at=CREATED_AT,
        replay_dir=replay_dir,
    )

    assert capture["request_status"] == invocation.FAILED_CLOSED
    assert capture["worker_invocation_request_artifact"] is None
    assert "cross-session" in capture["failure_reason"]
    assert not (replay_dir / "000_invocation_request_evidence_recorded.json").exists()


def test_generic_platform_core_contains_no_literal_worker_identity_or_router() -> None:
    sources = [
        Path(
            "aigol/runtime/worker_invocation_request_runtime.py"
        ).read_text(encoding="utf-8"),
        Path("aigol/runtime/worker_assignment_runtime.py").read_text(
            encoding="utf-8"
        ),
    ]
    combined = "\n".join(sources)

    assert '"CODEX"' not in combined
    assert "registry = {}" not in combined
    assert "contextvar" not in combined.lower()
    assert "contextmanager" not in combined.lower()
    assert "routing_state" not in combined.lower()
