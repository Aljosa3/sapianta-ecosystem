from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[5]
KQ = ROOT / ".github/governance/evidence/g77_256kq_human_provenance_capability_discovery_v1"
CLASSIFIER = KQ / "analysis/G77_256KQ_PROVENANCE_CAPABILITY_CLASSIFIER_V1.py"
REDUCTION = KQ / "G77_256KQ_SPCE_TERMINAL_CLASSIFICATION_V1.json"
REPORT = KQ / "G77_256KQ_G48_IMPLEMENTATION_REPORT_V1.md"
SOURCE = ROOT / ".github/governance/evidence/g77_256kn_fresh_expired_operational_recommissioning_v1/G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"


def load_classifier():
    spec = importlib.util.spec_from_file_location("g77_256kq_classifier", CLASSIFIER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_classifier_authenticates_inputs_and_exact_case_d_result() -> None:
    module = load_classifier()
    module.authenticate_inputs()
    result = module.build_classification()
    assert result["terminal"] == module.TERMINAL
    assert result["failure_novelty_and_convergence_check"]["failure_class"] == "EVIDENCE_OR_REPORTING_DEFECT"
    assert result["provenance_capability"]["status"] == "CURRENT_REQUIREMENT_NOT_AUTHENTICATED"
    assert result["historical_success_comparator"]["how_was_human_actor_identity_proven"] == "WEAKER_HISTORICAL_ASSUMPTION"
    assert result["failure_novelty_and_convergence_check"]["new_capability_required"].startswith("NOT_PROVEN")
    assert result["auto_continuable"] is False
    assert result["human_review_required"] is True


def test_sealed_classification_is_canonical_and_exact() -> None:
    module = load_classifier()
    raw = REDUCTION.read_bytes()
    envelope = json.loads(raw)
    assert raw == module.canonical_bytes(envelope)
    classification = envelope["classification"]
    assert envelope["classification_sha256"] == hashlib.sha256(module.canonical_bytes(classification)).hexdigest()
    assert classification == module.build_classification()
    assert set(classification["operational_counters"].values()) == {0}
    assert len(classification["operational_counters"]) == 15
    assert classification["phase_b_started"] is False


def test_source_is_exact_and_immutable() -> None:
    module = load_classifier()
    raw = SOURCE.read_bytes()
    assert len(raw) == 1213
    assert raw.count(b"\n") == 14
    assert hashlib.sha256(raw).hexdigest() == module.SOURCE_SHA256
    assert raw == module.exact_human_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf")
    assert raw.endswith(b"\n")
    raw.decode("utf-8")


def test_discovery_leads_remain_non_promotable() -> None:
    result = load_classifier().build_classification()
    assert "NOT_CERTIFIED" in result["profile_b"]["status"]
    assert "NOT_ACTIVE" in result["profile_b"]["activation_status"]
    assert "NOT_LEGAL_FOR_KN" in result["profile_b"]["reuse_legality"]
    assert "FIXTURE" in result["candidate_h"]["fixture_dependency"]
    assert "KN_SOURCE_BYTES_NOT_SIGNED" in result["candidate_h"]["source_bytes_binding"]
    assert "LOCAL_ONLY" == result["peer_credentials"]["remote_or_local_scope"]
    assert "NOT_PROVEN" in result["peer_credentials"]["human_identity_binding"]


def test_architecture_e05_and_reuse_remain_unchanged() -> None:
    result = load_classifier().build_classification()
    architecture = result["architecture"]
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
    assert result["e05"]["state"] == "VERIFIED__11_OF_18"
    assert result["e05"]["frontier"] == "VERIFIED__7_UNSATISFIED_OF_18"
    assert result["e05"]["credit"] == "VERIFIED__0"
    assert result["ex"] == {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0"}


def test_python_ast_g48_and_ria_structure() -> None:
    ast.parse(CLASSIFIER.read_text(encoding="utf-8"))
    ast.parse(Path(__file__).read_text(encoding="utf-8"))
    report = REPORT.read_text(encoding="utf-8")
    headings = re.findall(r"^# (.+)$", report, flags=re.MULTILINE)
    assert headings == [
        "1. Implementation Summary",
        "2. Code Evidence",
        "3. Constitutional Self-Assessment",
        "4. Validation Matrix",
        "5. Repository Mutation Summary",
        "6. Certification Verdict",
    ]
    questions = re.findall(r"^[1-5]\. (.+\?)$", report, flags=re.MULTILINE)
    assert questions == [
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
    ]
