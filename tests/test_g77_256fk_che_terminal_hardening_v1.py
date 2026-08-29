"""Repository-only regressions for the two committed G77-256FJ defects."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest

from aigol.runtime.canonical_che_evidence_correlation_contract_v1 import (
    CanonicalCHEEvidenceCorrelationV1,
    validate_canonical_che_evidence_correlation_v1,
)
from aigol.runtime.models import FailClosedRuntimeError


ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PATH = ROOT / (
    ".github/governance/evidence/g77_256fc_wrong_attempt_operational_v1/"
    "harness/G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
)
FA_AUTHORITY_PATH = ROOT / (
    ".github/governance/evidence/g77_256fa_consumed_operational_v1/raw/"
    "G77_256FA_AUTHORITY_CHECKPOINT_V1.json"
)
FJ_FAILURE = (
    "RuntimeError: custody failed creating act: "
    "{'error': 'CHE evidence correlation identity is invalid', "
    "'error_type': 'FailClosedRuntimeError', 'message_type': 'CUSTODY_FAILURE'}"
)


def _adapter() -> ModuleType:
    spec = importlib.util.spec_from_file_location("g77_256fk_adapter", ADAPTER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _valid_correlation() -> CanonicalCHEEvidenceCorrelationV1:
    authority = json.loads(FA_AUTHORITY_PATH.read_text(encoding="utf-8"))
    return CanonicalCHEEvidenceCorrelationV1.from_dict(
        authority["che_correlation_preimage"]
    )


def _counters(*, act_created: int = 0, premature_e05: int = 1) -> dict[str, int]:
    return {
        "human_operational_act_creation_count": act_created,
        "human_operational_act_claimed_count": 0,
        "human_operational_act_invoked_count": 0,
        "human_operational_act_terminally_bound_count": 0,
        "human_operational_act_permanently_exhausted_count": 0,
        "p11_entry_count": 0,
        "p11_operational_invocation_count": 0,
        "e01_e12_execution_count": 0,
        "e05_case_execution_count": premature_e05,
        "protected_effect_count": 0,
    }


def _authority_checkpoint() -> dict[str, object]:
    return {
        "schema_id": "G77_256FC_AUTHORITY_CHECKPOINT_V1",
        "execution_counters": {"human_operational_act_creation_count": 1},
    }


def _execution_seal() -> dict[str, object]:
    return {
        "schema_id": "G77_256FC_GUEST_EXECUTION_SEAL_V1",
        "case_id": "G77_256FC_E05_WRONG_ATTEMPT_DENIAL_BEFORE_ENTRY_001",
        "first_failure": None,
        "operational_result": (
            "PASS__WRONG_ATTEMPT_DENIED_AT_D2_BEFORE_PRECLAIM_AND_ENTRY_"
            "WITH_ZERO_EFFECT"
        ),
        "completed_gates": [
            "ONE_WRONG_ATTEMPT_D2_PRECLAIM_DENIAL",
            "ZERO_ENTRY_INVOCATION_EFFECT",
        ],
        "execution_counters": {"e05_case_execution_count": 1},
    }


def _reduce(
    *,
    current: str | None = "PASS__OPTIMISTIC_DERIVED_SUMMARY",
    first_failure: str | None = None,
    authority: dict[str, object] | None = None,
    seal: dict[str, object] | None = None,
    counters: dict[str, int] | None = None,
) -> dict[str, object]:
    return _adapter().reduce_wrong_attempt_terminal_state(
        phase="PHASE_D_GUEST_TEARDOWN_COMPLETE_PENDING_HOST_FINALIZATION",
        counters=counters or _counters(),
        first_failure_or_current_result=current,
        first_failure=first_failure,
        authority_checkpoint=authority,
        execution_seal=seal,
    )


def test_canonical_che_rebinding_recomputes_identity_deterministically() -> None:
    adapter = _adapter()
    original = _valid_correlation()
    updates = {
        "runtime_scope_identity": "G77_256FK_REPOSITORY_TEST_SCOPE",
        "request_identity": "G77_256FK_REPOSITORY_TEST_REQUEST",
        "metadata": {"generation_identity": "G77_256FK"},
    }

    first = adapter.rebind_canonical_correlation(original, updates)
    second = adapter.rebind_canonical_correlation(original, updates)

    assert first.to_dict() == second.to_dict()
    assert first.correlation_identity != original.correlation_identity
    assert validate_canonical_che_evidence_correlation_v1(first) is first


def test_stale_or_malformed_che_identity_remains_fail_closed() -> None:
    original = _valid_correlation()
    stale = original.to_dict()
    stale["runtime_scope_identity"] = "G77_256FK_STALE_IDENTITY_SCOPE"

    with pytest.raises(
        FailClosedRuntimeError,
        match="CHE evidence correlation identity is invalid",
    ):
        CanonicalCHEEvidenceCorrelationV1.from_dict(stale)


def test_setup_pass_act_creation_failure_reproduces_fj_fail_closed() -> None:
    reduced = _reduce(first_failure=FJ_FAILURE)

    assert reduced["success_evidence_complete"] is False
    assert reduced["first_failure_or_current_result"].startswith("FAIL_CLOSED__")
    assert reduced["execution_counters"]["e05_case_execution_count"] == 0
    assert reduced["execution_counters"]["p11_entry_count"] == 0
    assert reduced["execution_counters"]["p11_operational_invocation_count"] == 0
    assert reduced["execution_counters"]["protected_effect_count"] == 0
    assert reduced["e05_credit"] == 0


def test_raw_first_failure_dominates_complete_optimistic_summary() -> None:
    reduced = _reduce(
        first_failure=FJ_FAILURE,
        authority=_authority_checkpoint(),
        seal=_execution_seal(),
        counters=_counters(act_created=1),
    )

    assert reduced["success_evidence_complete"] is False
    assert reduced["first_failure_or_current_result"].startswith("FAIL_CLOSED__")
    assert reduced["e05_credit"] == 0


@pytest.mark.parametrize(
    ("authority", "seal"),
    [
        (None, _execution_seal()),
        (_authority_checkpoint(), None),
    ],
)
def test_missing_required_success_seal_cannot_pass(
    authority: dict[str, object] | None,
    seal: dict[str, object] | None,
) -> None:
    reduced = _reduce(
        authority=authority,
        seal=seal,
        counters=_counters(act_created=1),
    )

    assert reduced["success_evidence_complete"] is False
    assert reduced["execution_counters"]["e05_case_execution_count"] == 0
    assert reduced["e05_credit"] == 0


def test_missing_vector_request_evidence_cannot_increment_execution() -> None:
    seal = _execution_seal()
    seal["completed_gates"] = ["ZERO_ENTRY_INVOCATION_EFFECT"]

    reduced = _reduce(
        authority=_authority_checkpoint(),
        seal=seal,
        counters=_counters(act_created=1),
    )

    assert reduced["success_evidence_complete"] is False
    assert reduced["execution_counters"]["e05_case_execution_count"] == 0


def test_zero_act_creation_count_cannot_increment_execution() -> None:
    reduced = _reduce(
        authority=_authority_checkpoint(),
        seal=_execution_seal(),
        counters=_counters(act_created=0),
    )

    assert reduced["success_evidence_complete"] is False
    assert reduced["execution_counters"]["e05_case_execution_count"] == 0
    assert reduced["e05_credit"] == 0


def test_missing_explicit_execution_failure_field_cannot_pass() -> None:
    seal = _execution_seal()
    seal.pop("first_failure")

    reduced = _reduce(
        authority=_authority_checkpoint(),
        seal=seal,
        counters=_counters(act_created=1),
    )

    assert reduced["success_evidence_complete"] is False
    assert reduced["e05_credit"] == 0


def test_unknown_state_cannot_pass() -> None:
    reduced = _reduce(current=None)

    assert reduced["first_failure_or_current_result"].startswith("FAIL_CLOSED__")
    assert reduced["e05_credit"] == 0


def test_complete_positive_evidence_is_required_for_repository_acceptance() -> None:
    reduced = _reduce(
        authority=_authority_checkpoint(),
        seal=_execution_seal(),
        counters=_counters(act_created=1),
    )

    assert reduced["success_evidence_complete"] is True
    assert reduced["first_failure_or_current_result"].startswith("PASS__")
    assert reduced["execution_counters"]["e05_case_execution_count"] == 1
    assert reduced["e05_credit"] == 1
