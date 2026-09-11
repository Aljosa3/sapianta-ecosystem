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
KM = Path(
    ".github/governance/evidence/"
    "g77_256km_gn_exact_preauthorization_schema_preserving_ki_preflight_binding_v1"
)
VERIFIER = KM / "analysis/G77_256KM_GN_SCHEMA_PRESERVING_KI_PREFLIGHT_BINDING_VERIFIER_V1.py"
REDUCTION = KM / "G77_256KM_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = KM / "G77_256KM_G48_IMPLEMENTATION_REPORT_V1.md"


def load_verifier():
    specification = importlib.util.spec_from_file_location(
        "g77_256km_schema_binding_verifier", ROOT / VERIFIER
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


V = load_verifier()


def load_reduction() -> tuple[dict, dict]:
    raw = (ROOT / REDUCTION).read_bytes()
    envelope = json.loads(raw)
    assert raw == V.canonical_bytes(envelope)
    reduction = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(
        V.canonical_bytes(reduction)
    ).hexdigest()
    return envelope, reduction


def test_reduction_is_deterministic_and_sealed() -> None:
    observed, _ = load_reduction()
    assert observed == V.envelope(V.build_reduction(V.HEAD, V.NESTED_HEAD))


def test_exact_two_field_correction_preserves_one_gn_schema() -> None:
    _, reduction = load_reduction()
    correction = reduction["correction"]
    binding = reduction["binding"]
    assert correction["removed_fields"] == [
        "ki_frontier_preflight_file_sha256",
        "ki_frontier_preflight_inner_sha256",
    ]
    assert correction["added_fields"] == []
    assert correction["gn_owner_changed"] is False
    assert correction["gn_validation_weakened"] == "VERIFIED__NO"
    assert correction["second_accepted_gn_schema"] == "VERIFIED__NO"
    assert correction["fallback"] == "VERIFIED__ABSENT"
    assert correction["alias"] == "VERIFIED__ABSENT"
    assert correction["parallel_authority_path"] == "VERIFIED__NO"
    assert binding["gn_exact_preauthorization_field_count"] == 10
    assert binding["gn_exact_preauthorization_schema"] == "VERIFIED__UNCHANGED"
    assert binding["ki_preflight_binding"] == "VERIFIED__SCHEMA_PRESERVING"
    assert binding["synthetic_schema_preserving_projection"] == (
        "VERIFIED__GN_SEMANTIC_VALIDATOR_ACCEPTED"
    )
    assert binding["strict_negative_checks"] == (
        "VERIFIED__UNKNOWN_AND_MISSING_FIELD_REJECTED_WITH_EXACT_GN_TOKEN"
    )


def test_ki_evidence_is_bound_through_the_sealed_readiness_checkpoint() -> None:
    _, reduction = load_reduction()
    binding = reduction["binding"]
    chain = binding["binding_chain"]
    assert binding["ki_digest_semantics"] == (
        "EVIDENCE_PROOF_METADATA__NONAUTHORITY__NONOPERATIONAL"
    )
    assert binding["ki_digest_required_inside_gn_object"] is False
    assert chain["gn_existing_binding_fields"] == [
        "checkpoint_file_sha256",
        "checkpoint_inner_sha256",
    ]
    assert chain["result"] == (
        "VERIFIED__DETERMINISTIC_TRANSITIVE_BINDING_OUTSIDE_GN_OWNER_OBJECT"
    )
    assert binding["reused_pattern"].startswith("VERIFIED__KC_NAMESPACE_PREFLIGHT")


def test_kl_failure_history_frontier_and_zero_operation_remain_preserved() -> None:
    _, reduction = load_reduction()
    assert reduction["authenticated_kl_failure"]["failure_class"] == (
        "EVIDENCE_OR_REPORTING_DEFECT"
    )
    assert reduction["authenticated_kl_failure"]["fresh_kl_phase_a_presentation_ready"] == (
        "NOT_PROVEN"
    )
    assert reduction["baseline"]["e05_state"] == "VERIFIED__11_OF_18"
    assert reduction["baseline"]["e05_frontier"] == "VERIFIED__7_UNSATISFIED_OF_18"
    assert reduction["baseline"]["e05_credit"] == "VERIFIED__0"
    assert reduction["baseline"]["km_e05_credit"] == "VERIFIED__0"
    assert reduction["baseline"]["expired"] == "NOT_PROVEN_OPERATIONALLY"
    assert reduction["baseline"]["ex_reused"] == "VERIFIED__17_OF_17"
    assert reduction["baseline"]["ex_reconstructed"] == "VERIFIED__0"
    assert not any(reduction["operational_counters"].values())
    assert reduction["kl_retry_performed"] is False
    assert reduction["fresh_phase_a_commission_created"] is False
    assert reduction["human_authority_present"] is False
    assert reduction["phase_b_started"] is False
    assert reduction["auto_continuable"] is False
    assert reduction["human_review_required"] is True


def test_architecture_and_proof_yield_remain_bounded() -> None:
    _, reduction = load_reduction()
    architecture = reduction["architecture"]
    for field in (
        "production_mutation_count",
        "p11_implementation_mutation_count",
        "new_owner_count",
        "new_route_count",
        "new_registry_count",
        "new_generic_abstraction_count",
        "new_constitutional_concept_count",
    ):
        assert architecture[field] == 0
    assert architecture["production_route_before"] == 1
    assert architecture["production_route_after"] == 1
    assert architecture["parallel_flow"] == "NO"
    assert reduction["proof_yield"]["new_operational_capability_count"] == "VERIFIED__0"


def test_verifier_and_corrected_binder_parse_without_operational_execution() -> None:
    ast.parse((ROOT / VERIFIER).read_text(encoding="utf-8"))
    ast.parse((ROOT / V.KJ_WRAPPER).read_text(encoding="utf-8"))
    source = (ROOT / VERIFIER).read_text(encoding="utf-8")
    assert "qemu-system" not in source
    assert "P.M.materialize(arguments)" not in source
    assert "render_human_authorization_presentation" not in source


def test_g48_has_exactly_six_h1_and_exactly_five_ria_questions() -> None:
    report = (ROOT / REPORT).read_text(encoding="utf-8")
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
