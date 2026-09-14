from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[5]
VERIFIER = ROOT / (
    ".github/governance/evidence/"
    "g77_256lu_lt_fm_static_integration_readiness_v1/analysis/"
    "G77_256LU_LT_FM_STATIC_INTEGRATION_VERIFIER_V1.py"
)
SPEC = importlib.util.spec_from_file_location("g77_256lu_static_integration", VERIFIER)
assert SPEC is not None and SPEC.loader is not None
LU = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = LU
SPEC.loader.exec_module(LU)


def rejected(candidate: dict, reason: str) -> None:
    with pytest.raises(LU.StaticBindingError, match=reason):
        LU.validate_static_candidate(candidate)


def test_case_a_exact_valid_future_invocation_binding_is_ready() -> None:
    assert LU.validate_static_candidate(LU.synthetic_candidate()) == "STATIC_INTEGRATION_READY"


def test_case_b_mismatched_invocation_binding_rejected() -> None:
    rejected(
        LU.mutated_candidate(lt_invocation_binding_identity="FM_BINDING_SHA256:" + "9" * 64),
        "MISMATCHED_INVOCATION_BINDING",
    )


def test_case_c_mismatched_admission_head_tree_rejected() -> None:
    rejected(
        LU.mutated_candidate(admission_identity="HEAD:" + "8" * 40 + "__TREE:" + "4" * 40),
        "MISMATCHED_ADMISSION_HEAD_TREE",
    )


def test_case_d_mismatched_argv_hash_rejected() -> None:
    rejected(LU.mutated_candidate(argv_sha256="9" * 64), "MISMATCHED_ARGV_HASH")


def test_case_e_wrong_working_directory_rejected() -> None:
    rejected(LU.mutated_candidate(working_directory="/tmp"), "WRONG_WORKING_DIRECTORY")


def test_case_f_duplicate_supervisor_reservation_rejected() -> None:
    rejected(
        LU.mutated_candidate(reservation_exists=True),
        "DUPLICATE_SUPERVISOR_RESERVATION",
    )


@pytest.mark.parametrize("state", ["STARTED", "RUNNING"])
def test_case_g_existing_started_or_running_state_never_relaunches(state: str) -> None:
    rejected(LU.mutated_candidate(supervision_state=state), "NO_RELAUNCH")


def test_case_h_existing_terminated_state_never_relaunches() -> None:
    rejected(
        LU.mutated_candidate(supervision_state="TERMINATED_WITH_STATUS"),
        "NO_RELAUNCH",
    )


def test_case_i_existing_unknown_state_never_relaunches() -> None:
    rejected(
        LU.mutated_candidate(supervision_state="INTERRUPTED_OR_LOST__UNKNOWN"),
        "NO_RELAUNCH",
    )


def test_case_j_substituted_fm_executable_or_route_rejected() -> None:
    candidate = LU.synthetic_candidate()
    candidate["argv"][1] = "SYNTHETIC_REPLACEMENT_ROUTE.py"
    candidate["argv_sha256"] = LU.digest(candidate["argv"])
    rejected(candidate, "FM_EXECUTABLE_OR_ROUTE_SUBSTITUTION")


@pytest.mark.parametrize(
    ("change", "value"),
    [
        ("pre_owner", "LT_SUPERVISOR"),
        ("post_owner", "LT_SUPERVISOR"),
        ("supervisor_writes_pre", True),
        ("supervisor_writes_post", True),
    ],
)
def test_case_k_supervisor_cannot_fabricate_pre_or_post(change: str, value: object) -> None:
    rejected(LU.mutated_candidate(**{change: value}), "FM_PRE_POST_OWNERSHIP_SUBSTITUTION")


def test_case_l_host_terminal_state_cannot_prove_wrong_scope() -> None:
    rejected(
        LU.mutated_candidate(wrong_scope_inference_from_supervision=True),
        "HOST_SUPERVISION_PROOF_INFLATION",
    )


def test_case_m_integration_metadata_cannot_broaden_scope() -> None:
    rejected(
        LU.mutated_candidate(scope_metadata_delta=1),
        "SCOPE_BROADENING_THROUGH_INTEGRATION_METADATA",
    )


def test_case_n_lr_authority_or_lifecycle_reuse_rejected() -> None:
    rejected(
        LU.mutated_candidate(lr_authority_or_lifecycle_reused=True),
        "LR_TERMINAL_LIFECYCLE_REUSE_FORBIDDEN",
    )


@pytest.mark.parametrize(
    ("change", "value"),
    [
        ("authority_created_by_supervisor", True),
        ("authority_consumed_by_supervisor", True),
        ("authority_consumed_before_supervisor_reservation", False),
    ],
)
def test_authority_boundary_and_fail_closed_order(change: str, value: object) -> None:
    rejected(LU.mutated_candidate(**{change: value}), "AUTHORITY_BOUNDARY_OR_ORDER_CONFLICT")


@pytest.mark.parametrize(
    ("state", "reservation"),
    [
        ("UNRESERVED", True),
        ("STARTED", False),
        ("RUNNING", False),
        ("TERMINATED_WITH_STATUS", False),
        ("INTERRUPTED_OR_LOST__UNKNOWN", False),
    ],
)
def test_all_ambiguous_or_spent_states_forbid_relaunch(
    state: str, reservation: bool
) -> None:
    rejected(
        LU.mutated_candidate(supervision_state=state, reservation_exists=reservation),
        "NO_RELAUNCH|DUPLICATE_SUPERVISOR_RESERVATION",
    )


def test_authenticated_sources_and_static_relation() -> None:
    LU.authenticate_predecessors()
    LU.authenticate_code_relation()
