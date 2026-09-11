from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KK = Path(
    ".github/governance/evidence/"
    "g77_256kk_kj_phase_a_harness_path_binding_correction_v1"
)
VERIFIER_PATH = KK / "analysis/G77_256KK_KJ_PHASE_A_HARNESS_PATH_BINDING_VERIFIER_V1.py"
REDUCTION_PATH = KK / "G77_256KK_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT_PATH = KK / "G77_256KK_G48_IMPLEMENTATION_REPORT_V1.md"


def load_verifier():
    specification = importlib.util.spec_from_file_location(
        "g77_256kk_path_binding_verifier", ROOT / VERIFIER_PATH
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


V = load_verifier()


def load_reduction() -> tuple[dict, dict]:
    raw = (ROOT / REDUCTION_PATH).read_bytes()
    envelope = json.loads(raw)
    assert raw == V.canonical_bytes(envelope)
    reduction = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(
        V.canonical_bytes(reduction)
    ).hexdigest()
    return envelope, reduction


def test_reduction_is_deterministic_and_sealed() -> None:
    observed, _ = load_reduction()
    assert observed == V.envelope(V.build_reduction(V.HEAD, V.NESTED_TAG))


def test_exactly_one_authenticated_owner_wrapper_binding_exists() -> None:
    _, reduction = load_reduction()
    binding = reduction["binding"]
    assert binding["authenticated_owner_expected_path"] == V.NEW_WRAPPER.as_posix()
    assert binding["corrected_path"] == V.NEW_WRAPPER.as_posix()
    assert binding["accepted_wrapper_location_count"] == 1
    assert binding["wrapper_bytes_equal_committed_kj_candidate"] is True
    assert binding["kj_phase_a_harness_path_binding"] == "VERIFIED"
    assert not (ROOT / V.OLD_WRAPPER).exists()
    assert (ROOT / V.NEW_WRAPPER).is_file()
    ast.parse((ROOT / V.NEW_WRAPPER).read_text(encoding="utf-8"))


def test_no_phase_a_authority_operation_or_retry_occurred() -> None:
    _, reduction = load_reduction()
    assert not any(reduction["operational_counters"].values())
    assert reduction["fresh_kj_phase_a_presentation_ready"] == "NOT_PROVEN"
    assert reduction["human_authority_present"] is False
    assert reduction["phase_b_started"] is False
    assert reduction["auto_continuable"] is False
    assert reduction["human_review_required"] is True
    assert reduction["authenticated_kj_failure"]["phase_a_outputs_present"] == 0


def test_ex_e05_architecture_and_proof_yield_remain_bounded() -> None:
    _, reduction = load_reduction()
    baseline = reduction["baseline"]
    assert baseline["ex_reused"] == "VERIFIED__17_OF_17"
    assert baseline["ex_reconstructed"] == "VERIFIED__0"
    assert baseline["successor_reauthentication"] == (
        "VERIFIED__JP_ONE_REQUIRES_HARDENING_ER_DELTA__17_CERTIFIED_COMPONENTS_UNCHANGED"
    )
    assert baseline["e05_state"] == "VERIFIED__11_OF_18"
    assert baseline["e05_frontier"] == "VERIFIED__7_UNSATISFIED_OF_18"
    assert baseline["e05_credit"] == "VERIFIED__0"
    assert baseline["kk_e05_credit"] == "VERIFIED__0"
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
    assert reduction["proof_yield"]["new_operational_capability_count"] == "VERIFIED__0"


def test_g48_has_exactly_six_h1_and_exactly_five_ria_questions() -> None:
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
