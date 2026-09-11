from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[5]
KI = Path(
    ".github/governance/evidence/"
    "g77_256ki_expired_operational_frontier_assessment_v1"
)
ASSESSOR_PATH = KI / (
    "analysis/G77_256KI_EXPIRED_OPERATIONAL_FRONTIER_ASSESSOR_V1.py"
)
ASSESSMENT_PATH = KI / (
    "G77_256KI_SPCE_TERMINAL_REPOSITORY_ONLY_ASSESSMENT_V1.json"
)
REPORT_PATH = KI / "G77_256KI_G48_IMPLEMENTATION_REPORT_V1.md"


def load_assessor():
    specification = importlib.util.spec_from_file_location(
        "g77_256ki_assessor", ROOT / ASSESSOR_PATH
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


KI_MODULE = load_assessor()


def load_assessment() -> tuple[dict, dict]:
    raw = (ROOT / ASSESSMENT_PATH).read_bytes()
    envelope = json.loads(raw)
    assert raw == KI_MODULE.canonical_bytes(envelope)
    assessment = envelope["assessment"]
    assert envelope["assessment_sha256"] == hashlib.sha256(
        KI_MODULE.canonical_bytes(assessment)
    ).hexdigest()
    return envelope, assessment


def test_assessment_is_deterministically_replayable_and_sealed() -> None:
    observed, _ = load_assessment()
    assert observed == KI_MODULE.envelope(KI_MODULE.build_assessment())


def test_lineage_is_complete_generation_local_and_zero_credit() -> None:
    _, assessment = load_assessment()
    lineage = assessment["lineage"]
    assert [item["generation"] for item in lineage] == [
        f"J{letter}" for letter in "IJKLMNOPQRSTUVWXYZ"
    ] + [f"K{letter}" for letter in "ABCDEFGH"]
    assert len(lineage) == 26
    assert all(item["e05_credit"] == "VERIFIED__0" for item in lineage)
    by_generation = {item["generation"]: item for item in lineage}
    assert by_generation["KE"]["operational_counters"] == {
        "operational_authorization_count": 1,
        "authority_consumption_count": 1,
        "pre_operational_count": 1,
        "fm_operational_invocation_count": 1,
        "qemu_count": 1,
        "vm_count": 1,
        "operation_attempt_count": 1,
        "operational_request_count": 0,
        "expired_denial_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
    }
    assert by_generation["KG"]["authority_state"] == (
        "AUTHENTICATED__UNCONSUMED__TERMINAL__UNAVAILABLE_TO_KI"
    )
    assert by_generation["KG"]["operational_counters"][
        "authority_consumption_count"
    ] == 0


def test_real_frontier_removes_false_kg_blocker_without_inventing_one() -> None:
    _, assessment = load_assessment()
    frontier = assessment["frontier"]
    assert frontier == {
        "last_verified_operational_edge": KI_MODULE.LAST_OPERATIONAL_EDGE,
        "first_unverified_operational_edge": (
            KI_MODULE.FIRST_UNVERIFIED_OPERATIONAL_EDGE
        ),
        "last_verified_edge": KI_MODULE.LAST_VERIFIED_EDGE,
        "first_broken_edge": KI_MODULE.FIRST_BROKEN_EDGE,
        "current_real_blocker": (
            "NOT_PROVEN__NO_GENUINE_CURRENT_BLOCKER_LOCALIZED"
        ),
    }
    classification = assessment["failure_novelty_and_convergence_check"]
    assert classification["failure_class"] == "PROOF_GAP"
    assert classification["gap_classification"] == "OPERATIONAL_OBSERVATION_GAP"
    assert classification["new_capability_required"] == "NOT_PROVEN"
    assert classification["new_proof_required"] == (
        "VERIFIED__FRESH_OPERATIONAL_OBSERVATION_ONLY__NO_NEW_REPOSITORY_PROOF"
    )


def test_minimum_delta_is_one_fresh_human_authorized_observation() -> None:
    _, assessment = load_assessment()
    gap = assessment["gap_decision"]
    assert gap["minimum_missing_capability"] == (
        KI_MODULE.MINIMUM_MISSING_CAPABILITY
    )
    assert gap["minimum_legal_next_delta"] == KI_MODULE.MINIMUM_LEGAL_NEXT_DELTA
    assert gap["is_new_production_capability_required"] == "NOT_PROVEN"
    assert gap["is_new_repository_capability_required"] == "NOT_PROVEN"
    assert gap["is_new_repository_proof_required"] == "NOT_PROVEN"
    assert gap["is_existing_owner_repair_required"] == "NOT_PROVEN"
    assert gap["is_fresh_operational_observation_required"] == "VERIFIED"
    assert gap["is_fresh_human_authority_required_for_successor"] == "VERIFIED"
    successor = assessment["successor_spce_structure_only"]
    assert successor["ki_created_successor_artifacts"] is False
    assert successor["ki_started_successor_generation"] is False


def test_ki_is_zero_operation_zero_mutation_and_e05_unchanged() -> None:
    _, assessment = load_assessment()
    assert not any(assessment["operational_counters"].values())
    assert assessment["architecture"] == {
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
    assert assessment["baseline"] == {
        "e05_state": "VERIFIED__11_OF_18",
        "e05_frontier": "VERIFIED__7_UNSATISFIED_OF_18",
        "e05_credit": "VERIFIED__0",
        "ki_e05_credit": "VERIFIED__0",
        "expired": "NOT_PROVEN_OPERATIONALLY",
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
    }
    assert assessment["auto_continuable"] is False
    assert assessment["human_review_required"] is True


def test_g48_has_exactly_six_h1_and_ria_has_exactly_five_questions() -> None:
    report = (ROOT / REPORT_PATH).read_text(encoding="utf-8")
    headings = re.findall(r"^# .+$", report, flags=re.MULTILINE)
    assert headings == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    questions = re.findall(r"^\d+\. .+\?$", report, flags=re.MULTILINE)
    assert questions == [
        "1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "2. Katere nove zmogljivosti (če sploh) nastanejo?",
        "3. Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "4. Ali implementacija ustvarja vzporedni tok?",
        "5. Ali zmanjšuje ali povečuje število produkcijskih poti?",
    ]


def test_python_artifacts_are_syntax_valid() -> None:
    for relative in (ASSESSOR_PATH, Path(__file__).relative_to(ROOT)):
        ast.parse((ROOT / relative).read_text(encoding="utf-8"))
