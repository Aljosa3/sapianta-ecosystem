from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[5]
KH = Path(
    ".github/governance/evidence/"
    "g77_256kh_jz_digest_semantics_assessment_v1"
)
ASSESSOR_PATH = KH / (
    "analysis/G77_256KH_JZ_DIGEST_SEMANTICS_ASSESSOR_V1.py"
)
ASSESSMENT_PATH = KH / (
    "G77_256KH_SPCE_TERMINAL_REPOSITORY_ONLY_ASSESSMENT_V1.json"
)
REPORT_PATH = KH / "G77_256KH_G48_IMPLEMENTATION_REPORT_V1.md"


def load_assessor():
    specification = importlib.util.spec_from_file_location(
        "g77_256kh_assessor", ROOT / ASSESSOR_PATH
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


KH_MODULE = load_assessor()


def load_assessment() -> tuple[dict, dict]:
    raw = (ROOT / ASSESSMENT_PATH).read_bytes()
    envelope = json.loads(raw)
    assert raw == KH_MODULE.canonical_bytes(envelope)
    assessment = envelope["assessment"]
    assert envelope["assessment_sha256"] == hashlib.sha256(
        KH_MODULE.canonical_bytes(assessment)
    ).hexdigest()
    return envelope, assessment


def test_assessment_is_deterministically_replayable_and_sealed() -> None:
    observed_envelope, _ = load_assessment()
    expected_envelope = KH_MODULE.envelope(KH_MODULE.build_assessment())
    assert observed_envelope == expected_envelope


def test_exact_kg_byte_domains_are_distinct_and_correct() -> None:
    _, assessment = load_assessment()
    domains = assessment["exact_kg_byte_domains"]
    assert domains == {
        "human_source_byte_domain": "EXACT_HUMAN_SOURCE_FILE_BYTES",
        "human_source_byte_length": 1390,
        "human_source_sha256": KH_MODULE.HUMAN_SOURCE_SHA256,
        "handoff_digest_byte_domain": (
            "EXACT_UNIQUE_KEY_CANONICAL_HANDOFF_JSON_ENVELOPE_BYTES_PLUS_LF"
        ),
        "handoff_digest_byte_length": 1715,
        "handoff_digest_sha256": KH_MODULE.HANDOFF_SHA256,
        "relationship": (
            "VERIFIED__BOTH_DIGESTS_CORRECTLY_HASH_DIFFERENT_SEMANTIC_OBJECTS"
        ),
        "governance_requires_cross_domain_equality": (
            "NOT_PROVEN__AUTHENTICATED_JZ_REQUIRES_FIELD_BINDING_AND_"
            "ENVELOPE_DIGEST_PRESERVATION_NOT_NUMERICAL_CROSS_DOMAIN_EQUALITY"
        ),
    }


def test_jz_contract_and_ka_ke_kg_controls_agree() -> None:
    _, assessment = load_assessment()
    jz = assessment["authenticated_jz_semantics"]
    assert jz["terminal"] == KH_MODULE.JZ_TERMINAL
    assert jz["authenticated_jz_requirement"] == (
        "CANONICAL_HANDOFF_FILE_DIGEST_EQUALS_SEALED_INVOCATION_DIGEST_"
        "EQUALS_FINAL_FM_ARGV_DIGEST"
    )
    assert jz["contract_difference"] == (
        "KG_ADDED_SOURCE_TO_ENVELOPE_FILE_DIGEST_EQUALITY_NOT_PRESENT_IN_JZ"
    )
    for generation in ("KA", "KE", "KG"):
        comparison = assessment["historical_comparison"][generation]
        assert comparison["source_digest_carried_as_authorization_field"] == (
            "VERIFIED"
        )
        assert comparison["source_digest_equals_handoff_digest"] is False
        assert comparison["handoff_invocation_argv_equality"] == "VERIFIED"
        assert comparison["authority_digest_derivation"] == (
            "SHA256_EXACT_CANONICAL_HANDOFF_BYTES"
        )


def test_classification_decision_is_consistent_and_no_repair_is_created() -> None:
    _, assessment = load_assessment()
    classification = assessment["failure_novelty_and_convergence_check"]
    decision = assessment["decision"]
    gap = assessment["proof_gap_vs_implementation_gap"]
    assert classification["failure_class"] == "EVIDENCE_OR_REPORTING_DEFECT"
    assert classification["new_capability_required"] == "NOT_PROVEN"
    assert classification["new_proof_required"] == "NOT_PROVEN"
    assert decision["selected_case"] == "CASE_E__EVIDENCE_OR_REPORTING_DEFECT"
    assert decision["minimum_missing_capability"] == (
        "NOT_PROVEN__NO_NEW_CAPABILITY_GAP_ESTABLISHED"
    )
    assert decision["minimum_legal_next_delta"] == "STOP_OR_REUSE_EXISTING_PROOF"
    assert gap["is_jz_implementation_wrong"] == "NOT_PROVEN"
    assert gap["is_kg_binder_implementation_wrong"] == "NOT_PROVEN"
    assert gap["is_kg_phase_b_commission_overstrong"] == "VERIFIED"
    assert gap["is_existing_proof_insufficient"] == "NOT_PROVEN"


def test_operational_firewall_architecture_and_baseline_are_unchanged() -> None:
    _, assessment = load_assessment()
    assert not any(assessment["operational_counters"].values())
    architecture = assessment["architecture"]
    assert architecture == {
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
