from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[5]
KJ = Path(
    ".github/governance/evidence/"
    "g77_256kj_fresh_expired_operational_commissioning_v1"
)
REDUCER_PATH = KJ / "analysis/G77_256KJ_PHASE_A_FAILURE_REDUCER_V1.py"
WRAPPER_PATH = KJ / "orchestration/G77_256KJ_PREAUTHORIZATION_MATERIALIZER_V1.py"
REDUCTION_PATH = KJ / "G77_256KJ_SPCE_PHASE_A_TERMINAL_FAIL_CLOSED_REDUCTION_V1.json"
REPORT_PATH = KJ / "G77_256KJ_G48_IMPLEMENTATION_REPORT_V1.md"


def load_reducer():
    specification = importlib.util.spec_from_file_location(
        "g77_256kj_failure_reducer", ROOT / REDUCER_PATH
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


R = load_reducer()


def load_reduction() -> tuple[dict, dict]:
    raw = (ROOT / REDUCTION_PATH).read_bytes()
    envelope = json.loads(raw)
    assert raw == R.canonical_bytes(envelope)
    reduction = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(
        R.canonical_bytes(reduction)
    ).hexdigest()
    return envelope, reduction


def test_failure_reduction_is_deterministic_and_sealed() -> None:
    observed, _ = load_reduction()
    assert observed == R.envelope(R.build_reduction())


def test_exact_path_failure_is_localized_before_materialization() -> None:
    _, reduction = load_reduction()
    failure = reduction["failure"]
    assert failure["failure_class"] == "HARNESS_OR_TEST_ARTIFACT"
    assert failure["failure_boundary"] == (
        "PHASE_A_KD_INTERFACE_PREFLIGHT_BEFORE_MATERIALIZATION_OR_"
        "HUMAN_PRESENTATION"
    )
    assert failure["first_broken_edge"] == (
        "ADAPTED_OWNER_EXPECTED_KJ_WRAPPER_UNDER_OPERATIONAL_"
        "RECOMMISSIONING_DIRECTORY_BUT_WRAPPER_EXISTS_UNDER_OPERATIONAL_"
        "COMMISSIONING_DIRECTORY"
    )
    entry = reduction["entry"]
    assert Path(ROOT / entry["wrapper_path"]).is_file()
    assert not Path(ROOT / entry["expected_wrapper_path"]).exists()
    assert entry["phase_a_outputs_created_before_failure"] == 0


def test_no_authority_operation_presentation_or_retry_occurred() -> None:
    _, reduction = load_reduction()
    assert not any(reduction["operational_counters"].values())
    phase_a = reduction["phase_a_result"]
    assert phase_a == {
        "fresh_kj_phase_a_presentation_ready": "NOT_PROVEN",
        "human_decision_presentation": (
            "NOT_CREATED__FAIL_CLOSED_BEFORE_PRESENTATION"
        ),
        "safe_stop_checkpoint": (
            "NOT_CREATED__FAIL_CLOSED_BEFORE_MATERIALIZATION"
        ),
        "human_authority_present": False,
        "phase_b_started": False,
        "auto_continuable": False,
        "human_review_required": True,
        "repair_performed": False,
        "retry_performed": False,
    }
    for name in (
        "G77_256KJ_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json",
        "G77_256KJ_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json",
        "G77_256KJ_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json",
        "G77_256KJ_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt",
        "G77_256KJ_HUMAN_DECISION_PRESENTATION_V1.txt",
        "G77_256KJ_PREHUMAN_PHASE_A_REDUCTION_V1.json",
    ):
        assert not (ROOT / KJ / name).exists()


def test_e05_ex_architecture_and_control_state_are_unchanged() -> None:
    _, reduction = load_reduction()
    assert reduction["baseline"] == {
        "e05_state": "VERIFIED__11_OF_18",
        "e05_frontier": "VERIFIED__7_UNSATISFIED_OF_18",
        "e05_credit": "VERIFIED__0",
        "kj_phase_a_e05_credit": "VERIFIED__0",
        "expired": "NOT_PROVEN_OPERATIONALLY",
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
    }
    assert reduction["architecture"] == {
        "production_mutation_count": 0,
        "p11_implementation_mutation_count": 0,
        "new_owner_count": 0,
        "new_route_count": 0,
        "new_registry_count": 0,
        "new_generic_abstraction_count": 0,
        "new_constitutional_concept_count": 0,
        "production_route_before": 1,
        "production_route_after": 1,
        "parallel_flow": "NO",
    }
    assert reduction["auto_continuable"] is False
    assert reduction["human_review_required"] is True


def test_g48_has_exactly_six_h1_and_ria_has_exactly_five_questions() -> None:
    report = (ROOT / REPORT_PATH).read_text(encoding="utf-8")
    assert re.findall(r"^# .+$", report, flags=re.MULTILINE) == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    assert re.findall(r"^\d+\. .+\?$", report, flags=re.MULTILINE) == [
        "1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "2. Katere nove zmogljivosti (če sploh) nastanejo?",
        "3. Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "4. Ali implementacija ustvarja vzporedni tok?",
        "5. Ali zmanjšuje ali povečuje število produkcijskih poti?",
    ]


def test_python_artifacts_are_syntax_valid() -> None:
    for relative in (REDUCER_PATH, WRAPPER_PATH, Path(__file__).relative_to(ROOT)):
        ast.parse((ROOT / relative).read_text(encoding="utf-8"))
