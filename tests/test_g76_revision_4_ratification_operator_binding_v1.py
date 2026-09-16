"""NONAUTHORITY TEST FIXTURES for the Step 9 operator binding."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from aigol.runtime import operator_cli
from aigol.runtime.operator_cli import build_parser
from aigol.runtime.canonical_hic_conformance_runtime_v1 import (
    CLIA_CONFORMANCE_PROFILE_V1,
    create_canonical_hic_human_authority_act_request_v1,
)
from aigol.runtime.canonical_human_authority_act_contract_v1 import (
    HUMAN_AUTHORITY_OWNER,
)
from aigol.runtime.canonical_human_entry_contract_v1 import HUMAN_ACTOR
from aigol.runtime.constitutional_human_ratification_contract_v1 import (
    CONSTITUTIONAL_AMENDMENT_RATIFICATION_SCOPE,
    CONSTITUTIONAL_GOVERNANCE_OWNER,
    RATIFY_CONSTITUTIONAL_AMENDMENT,
)
from aigol.runtime.g76_revision_4_ratification_operator_binding_v1 import (
    G76_REVISION_4_OPERATOR_EXITED,
    G76_REVISION_4_OPERATOR_INPUT_REJECTED,
    G76_REVISION_4_OPERATOR_PRESENTED,
    G76_REVISION_4_OPERATOR_RATIFICATION_RECORDED,
    _presentation_request_v1,
    create_explicit_g76_revision_4_human_act_v1,
    run_g76_revision_4_ratification_operator_binding_v1,
)
from aigol.runtime.g76_revision_4_ratification_owner_composition_v1 import (
    materialize_g76_revision_4_ratification_package_v1,
    present_g76_revision_4_ratification_boundary_v1,
    submit_g76_revision_4_human_ratification_v1,
)
from aigol.runtime.models import FailClosedRuntimeError


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
NONAUTHORITY_TEST_FIXTURE_EXPLICIT_POSITIVE_INPUT = (
    RATIFY_CONSTITUTIONAL_AMENDMENT
)


def _run(tmp_path: Path, human_input=StopIteration):
    output: list[str] = []

    def reader(_prompt: str) -> str:
        if human_input is StopIteration:
            raise StopIteration
        return human_input

    result = run_g76_revision_4_ratification_operator_binding_v1(
        repository_root=REPOSITORY_ROOT,
        session_identity="G76-R4-OPERATOR-TEST-SESSION",
        human_actor_identity="G76-R4-OPERATOR-TEST-HUMAN",
        workspace_identity=tmp_path / "workspace",
        runtime_scope_identity=tmp_path / "runtime",
        created_at="2026-09-16T12:00:00Z",
        input_reader=reader,
        output_writer=output.append,
    )
    return result, output


def test_registered_operator_entry_reuses_existing_identity_arguments() -> None:
    args = build_parser().parse_args(
        [
            "--g76-r4-ratification",
            "--cli-id",
            "SESSION",
            "--operator-id",
            "HUMAN",
            "--workspace",
            "WORKSPACE",
            "--runtime-root",
            "RUNTIME",
        ]
    )

    assert args.g76_r4_ratification is True
    assert args.cli_id == "SESSION"
    assert args.operator_id == "HUMAN"
    assert args.workspace == "WORKSPACE"
    assert args.runtime_root == "RUNTIME"


def test_registered_operator_entry_dispatches_only_the_g76_binding(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def binding(**kwargs):
        captured.update(kwargs)
        return {"operator_status": G76_REVISION_4_OPERATOR_PRESENTED}

    monkeypatch.setattr(
        operator_cli,
        "run_g76_revision_4_ratification_operator_binding_v1",
        binding,
    )

    assert operator_cli.main(
        [
            "--g76-r4-ratification",
            "--cli-id",
            "SESSION",
            "--operator-id",
            "HUMAN",
            "--workspace",
            ".",
            "--runtime-root",
            "RUNTIME",
            "--created-at",
            "2026-09-16T12:00:00Z",
        ]
    ) == 0
    assert captured["session_identity"] == "SESSION"
    assert captured["human_actor_identity"] == "HUMAN"
    assert captured["runtime_scope_identity"] == "RUNTIME"


def test_presentation_uses_canonical_hic_and_creates_zero_authority(
    tmp_path: Path,
) -> None:
    result, output = _run(tmp_path)

    request = result["request"]
    summary = result["decision_summary"]
    assert result["operator_status"] == G76_REVISION_4_OPERATOR_PRESENTED
    assert request["interface_identity"] == (
        CLIA_CONFORMANCE_PROFILE_V1.interface_identity
    )
    assert request["adapter_identity"] == (
        CLIA_CONFORMANCE_PROFILE_V1.adapter_identity
    )
    assert request["source_modality"] == "TEXT"
    assert request["actor_class"] == HUMAN_ACTOR
    assert result["continuation"]["continuation_state"] == "ACTIVE"
    assert summary == {
        **summary,
        "decision_type": CONSTITUTIONAL_AMENDMENT_RATIFICATION_SCOPE,
        "target": (
            "CONSTITUTIONAL-IMPACT-ASSESSMENT-"
            "1a8f9c018cf1e36491e125f081f47d1fc213ce52f075581eedcf68e58c219981"
        ),
        "target_digest": (
            "sha256:1a8f9c018cf1e36491e125f081f47d1fc213ce52f075581eedcf68e58c219981"
        ),
        "revision": 4,
        "proposal_identity": (
            "CONSTITUTIONAL-AMENDMENT-PROPOSAL-"
            "b6821f60f69b234d904cfb4bb1093f5ff0dffbecf4152206acce5b88296c799c"
        ),
        "constitutional_gap_identity": (
            "CONSTITUTIONAL-GAP-"
            "6af1e7ad5f996dd841e2ff4c5cc73e8ff8d0776a422184fa00925160805ef70a"
        ),
        "current_active_predecessor": (
            "AI_GOL_CONSTITUTIONAL_CORE_BASELINE_V1_ESTABLISHED@V1"
        ),
        "proposed_successor": "V1.1-RELEASE-DECISION-ARTIFACT-R4",
        "authority_owner": HUMAN_AUTHORITY_OWNER,
        "ratification_processor": CONSTITUTIONAL_GOVERNANCE_OWNER,
        "positive_human_action": RATIFY_CONSTITUTIONAL_AMENDMENT,
    }
    assert result["human_authority_acts_created"] == 0
    assert result["human_authority_acts_consumed"] == 0
    assert result["ratification_artifacts_created"] == 0
    assert result["g70_05_executed"] is False
    assert result["g70_06_executed"] is False
    rendered = "\n".join(output)
    assert "SILENCE != APPROVAL" in rendered
    assert "NO_POSITIVE_ACT != RATIFICATION" in rendered
    assert "would NOT implement CDP" in rendered


@pytest.mark.parametrize("human_input", ("", "/exit", "/decline"))
def test_silence_exit_or_decline_creates_no_reject_or_positive_act(
    tmp_path: Path, human_input: str
) -> None:
    result, output = _run(tmp_path, human_input)

    assert result["operator_status"] == G76_REVISION_4_OPERATOR_EXITED
    assert result["human_authority_acts_created"] == 0
    assert result["human_authority_acts_consumed"] == 0
    assert result["ratification_artifacts_created"] == 0
    assert "no constitutional REJECT artifact" in output[-1]


@pytest.mark.parametrize(
    "human_input",
    (
        "/send",
        "approve",
        "APPROVAL",
        "I approve this change",
        f" {RATIFY_CONSTITUTIONAL_AMENDMENT}",
    ),
)
def test_arbitrary_or_inexact_text_is_not_authority(
    tmp_path: Path, human_input: str
) -> None:
    result, _ = _run(tmp_path, human_input)

    assert result["operator_status"] == G76_REVISION_4_OPERATOR_INPUT_REJECTED
    assert result["human_authority_acts_created"] == 0
    assert result["human_authority_acts_consumed"] == 0
    assert result["ratification_artifacts_created"] == 0


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("session_identity", ""),
        ("session_identity", "BAD SESSION"),
        ("human_actor_identity", ""),
        ("human_actor_identity", "BAD ACTOR"),
    ),
)
def test_missing_or_malformed_actor_and_session_fail_closed(
    tmp_path: Path, field: str, value: str
) -> None:
    arguments = {
        "repository_root": REPOSITORY_ROOT,
        "session_identity": "SESSION",
        "human_actor_identity": "HUMAN",
        "workspace_identity": tmp_path / "workspace",
        "runtime_scope_identity": tmp_path / "runtime",
        "created_at": "2026-09-16T12:00:00Z",
        "input_reader": lambda _prompt: "/exit",
        "output_writer": lambda _message: None,
    }
    arguments[field] = value

    with pytest.raises(FailClosedRuntimeError, match="invalid"):
        run_g76_revision_4_ratification_operator_binding_v1(**arguments)


def test_exact_positive_input_builds_existing_structured_act_and_g70_04_fixture(
    tmp_path: Path,
) -> None:
    """This is a NONAUTHORITY TEST FIXTURE, not an operational Human act."""

    result, output = _run(
        tmp_path, NONAUTHORITY_TEST_FIXTURE_EXPLICIT_POSITIVE_INPUT
    )

    assert result["operator_status"] == G76_REVISION_4_OPERATOR_RATIFICATION_RECORDED
    assert result["human_authority_acts_created"] == 1
    assert result["human_authority_acts_consumed"] == 1
    assert result["ratification_artifacts_created"] == 1
    terminal = result["terminal_response"]
    ratification = terminal["owner_projection"]["owner_result_projection"]
    assert terminal["owner_status"] == (
        "G76_REVISION_4_HUMAN_RATIFICATION_RECORDED_NOT_CERTIFIED"
    )
    assert terminal["response_type"] == "TERMINAL"
    assert ratification["owner_status"] == terminal["owner_status"]
    assert result["g70_05_executed"] is False
    assert result["g70_06_executed"] is False
    assert "STOP before G70-05" in output[-1]


def test_actor_session_and_owner_contract_mismatches_fail_closed(
    tmp_path: Path,
) -> None:
    """Use only NONAUTHORITY TEST FIXTURES to pressure the future ingress."""

    package = materialize_g76_revision_4_ratification_package_v1(REPOSITORY_ROOT)
    request = _presentation_request_v1(
        actor_identity="G76-R4-OPERATOR-TEST-HUMAN",
        session_identity="G76-R4-OPERATOR-TEST-SESSION",
        workspace_identity=str((tmp_path / "workspace").resolve()),
        runtime_scope_identity=str((tmp_path / "runtime").resolve()),
        created_at="2026-09-16T12:00:00Z",
    )
    response = present_g76_revision_4_ratification_boundary_v1(
        package=package,
        request=request,
    )
    act = create_explicit_g76_revision_4_human_act_v1(
        exact_human_input=NONAUTHORITY_TEST_FIXTURE_EXPLICIT_POSITIVE_INPUT,
        response=response,
    )
    continuation = response.continuation_envelope
    assert continuation is not None

    with pytest.raises(FailClosedRuntimeError, match="Continuation binding"):
        create_canonical_hic_human_authority_act_request_v1(
            profile=CLIA_CONFORMANCE_PROFILE_V1,
            human_authority_act=replace(act, actor_identity="WRONG-ACTOR"),
            continuation=continuation,
            request_identity=act.request_identity,
            order_identity="WRONG-ACTOR-ORDER",
            idempotency_identity="WRONG-ACTOR-IDEMPOTENCY",
            created_at="2026-09-16T12:01:00Z",
        )

    for changed_act in (
        replace(act, expected_owner="WRONG-OWNER"),
        replace(act, authority_scope="WRONG-SCOPE"),
        replace(act, target_identity="WRONG-TARGET"),
        replace(act, target_revision=3),
        replace(act, authority_kind="CONFIRMATION"),
    ):
        structured = create_canonical_hic_human_authority_act_request_v1(
            profile=CLIA_CONFORMANCE_PROFILE_V1,
            human_authority_act=changed_act,
            continuation=continuation,
            request_identity=changed_act.request_identity,
            order_identity="MISMATCH-ORDER-" + changed_act.authority_kind,
            idempotency_identity=(
                "MISMATCH-IDEMPOTENCY-" + changed_act.authority_kind
            ),
            created_at="2026-09-16T12:01:00Z",
        )
        with pytest.raises(FailClosedRuntimeError):
            submit_g76_revision_4_human_ratification_v1(
                package=package,
                request=structured,
                continuation=continuation,
            )


def test_operator_binding_has_no_parallel_che_or_post_g70_04_imports() -> None:
    source = (
        REPOSITORY_ROOT
        / "aigol/runtime/g76_revision_4_ratification_operator_binding_v1.py"
    ).read_text(encoding="utf-8")

    assert "_execute_canonical_che_request_v1" not in source
    assert "constitutional_amendment_certification_contract_v1" not in source
    assert "constitutional_successor_publication_activation_contract_v1" not in source
    assert "activate_constitutional_production_cutover" not in source
    assert "from aigol.runtime.e05" not in source.lower()
    assert "submit_g76_revision_4_human_ratification_v1" in source
    assert "present_g76_revision_4_ratification_boundary_v1" in source
