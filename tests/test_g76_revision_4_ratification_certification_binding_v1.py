"""NONAUTHORITY fixtures for the G70-04 to G70-05 evidence binding."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aigol.runtime.constitutional_amendment_certification_contract_v1 import (
    CONSTITUTIONAL_AMENDMENT_CERTIFIED_NOT_ACTIVATED,
)
from aigol.runtime.constitutional_human_ratification_contract_v1 import (
    RATIFY_CONSTITUTIONAL_AMENDMENT,
)
from aigol.runtime.g76_revision_4_ratification_certification_binding_v1 import (
    certify_g76_revision_4_ratification_v1,
    recover_g76_revision_4_human_ratification_v1,
)
from aigol.runtime.g76_revision_4_ratification_operator_binding_v1 import (
    run_g76_revision_4_ratification_operator_binding_v1,
)
from aigol.runtime.models import FailClosedRuntimeError


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
RATIFIED_AT = "2026-09-16T12:00:00Z"
CERTIFIED_AT = "2026-09-16T12:05:00Z"


def _materialize_nonauthority_fixture(tmp_path: Path) -> dict[str, str | Path]:
    runtime = tmp_path / "runtime"
    result = run_g76_revision_4_ratification_operator_binding_v1(
        repository_root=REPOSITORY_ROOT,
        session_identity="G76-R4-G70-05-NONAUTHORITY-SESSION",
        human_actor_identity="G76-R4-G70-05-NONAUTHORITY-HUMAN",
        workspace_identity=tmp_path / "workspace",
        runtime_scope_identity=runtime,
        created_at=RATIFIED_AT,
        input_reader=lambda _prompt: RATIFY_CONSTITUTIONAL_AMENDMENT,
        output_writer=lambda _message: None,
    )
    terminal = result["terminal_response"]
    ratification_identity = terminal["owner_projection"]["owner_terminal_state"][
        "terminal_identity"
    ]
    delivery_records = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(
            (
                runtime
                / "canonical_human_entry_delivery_resolution_v1"
            ).glob("*.json")
        )
    ]
    authority_record = next(
        record
        for record in delivery_records
        if record["authority_act_identity"] != "NOT_APPLICABLE"
    )
    return {
        "runtime": runtime,
        "act_identity": result["human_authority_act_identity"],
        "act_digest": authority_record["authority_act_digest"],
        "ratification_identity": ratification_identity,
        "ratification_digest": "sha256:"
        + ratification_identity.rsplit("-", 1)[-1],
        "response_identity": terminal["response_identity"],
        "terminal_continuation_identity": terminal["continuation_envelope"][
            "continuation_identity"
        ],
    }


def _arguments(fixture: dict[str, str | Path]) -> dict[str, str | Path]:
    return {
        "repository_root": REPOSITORY_ROOT,
        "runtime_root": fixture["runtime"],
        "ratified_at": RATIFIED_AT,
        "expected_human_authority_act_identity": fixture["act_identity"],
        "expected_human_authority_act_digest": fixture["act_digest"],
        "expected_ratification_identity": fixture["ratification_identity"],
        "expected_ratification_digest": fixture["ratification_digest"],
        "expected_terminal_response_identity": fixture["response_identity"],
        "expected_terminal_continuation_identity": fixture[
            "terminal_continuation_identity"
        ],
    }


def test_exact_runtime_evidence_recovers_same_complete_ratification(
    tmp_path: Path,
) -> None:
    fixture = _materialize_nonauthority_fixture(tmp_path)
    before = tuple(sorted(Path(fixture["runtime"]).rglob("*.json")))

    ratification = recover_g76_revision_4_human_ratification_v1(
        **_arguments(fixture)
    )

    assert ratification.ratification_identity == fixture["ratification_identity"]
    assert ratification.artifact_digest == fixture["ratification_digest"]
    assert ratification.human_authority_act.authority_act_identity == (
        fixture["act_identity"]
    )
    assert ratification.che_request.created_at == RATIFIED_AT
    assert tuple(sorted(Path(fixture["runtime"]).rglob("*.json"))) == before


def test_exact_recovered_ratification_reaches_existing_g70_05_once(
    tmp_path: Path,
) -> None:
    fixture = _materialize_nonauthority_fixture(tmp_path)
    before = tuple(sorted(Path(fixture["runtime"]).rglob("*.json")))

    certification = certify_g76_revision_4_ratification_v1(
        **_arguments(fixture),
        certified_at=CERTIFIED_AT,
    )

    assert certification.certification_status == (
        CONSTITUTIONAL_AMENDMENT_CERTIFIED_NOT_ACTIVATED
    )
    assert certification.human_ratification.ratification_identity == (
        fixture["ratification_identity"]
    )
    assert certification.amendment_certification_performed is True
    assert certification.amendment_publication_performed is False
    assert certification.amendment_activation_performed is False
    assert certification.replay_mutation_performed is False
    assert certification.cro_mutation_performed is False
    assert tuple(sorted(Path(fixture["runtime"]).rglob("*.json"))) == before


def test_same_evidence_and_times_are_deterministic(tmp_path: Path) -> None:
    fixture = _materialize_nonauthority_fixture(tmp_path)
    first = certify_g76_revision_4_ratification_v1(
        **_arguments(fixture),
        certified_at=CERTIFIED_AT,
    )
    second = certify_g76_revision_4_ratification_v1(
        **_arguments(fixture),
        certified_at=CERTIFIED_AT,
    )
    assert first == second


@pytest.mark.parametrize(
    ("field", "wrong_value"),
    (
        ("ratified_at", "2026-09-16T12:00:01Z"),
        (
            "expected_human_authority_act_identity",
            "HUMAN-AUTHORITY-ACT-G76-R4-WRONG",
        ),
        ("expected_human_authority_act_digest", "sha256:" + ("0" * 64)),
        (
            "expected_ratification_identity",
            "CONSTITUTIONAL-HUMAN-RATIFICATION-WRONG",
        ),
        ("expected_ratification_digest", "sha256:" + ("0" * 64)),
        ("expected_terminal_response_identity", "CHE-RESPONSE-WRONG"),
        (
            "expected_terminal_continuation_identity",
            "CHE-CONTINUATION-WRONG",
        ),
    ),
)
def test_wrong_reconstruction_binding_fails_closed(
    tmp_path: Path,
    field: str,
    wrong_value: str,
) -> None:
    fixture = _materialize_nonauthority_fixture(tmp_path)
    arguments = _arguments(fixture)
    arguments[field] = wrong_value
    with pytest.raises(FailClosedRuntimeError):
        recover_g76_revision_4_human_ratification_v1(**arguments)


def test_tampered_runtime_record_fails_closed(tmp_path: Path) -> None:
    fixture = _materialize_nonauthority_fixture(tmp_path)
    correlation = next(
        (
            Path(fixture["runtime"])
            / "canonical_che_evidence_correlations_v1"
        ).glob("*.json")
    )
    record = json.loads(correlation.read_text(encoding="utf-8"))
    record["correlation"]["owner_revision_after"] = 99
    correlation.write_text(json.dumps(record), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="integrity"):
        recover_g76_revision_4_human_ratification_v1(**_arguments(fixture))


def test_binding_has_no_che_submission_persistence_or_g70_06_path() -> None:
    source = (
        REPOSITORY_ROOT
        / "aigol/runtime/g76_revision_4_ratification_certification_binding_v1.py"
    ).read_text(encoding="utf-8")
    assert "submit_g76_revision_4_human_ratification_v1" not in source
    assert "_execute_canonical_che_request_v1" not in source
    assert "constitutional_successor_publication_activation" not in source
    assert "persist_canonical_che" not in source
    assert "certify_constitutional_amendment_v1" in source
