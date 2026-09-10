from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KE = ROOT / (
    ".github/governance/evidence/"
    "g77_256ke_fresh_expired_operational_recommissioning_v1"
)
REDUCTION = KE / "G77_256KE_PREHUMAN_PHASE_A_REDUCTION_V1.json"
READINESS = KE / "G77_256KE_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json"
SAFE_STOP = KE / "G77_256KE_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
REQUEST = KE / "G77_256KE_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
PRESENTATION = KE / "G77_256KE_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
DECISION_PRESENTATION = KE / "G77_256KE_HUMAN_DECISION_PRESENTATION_V1.txt"
KB_PREFLIGHT = KE / "G77_256KE_KB_NAMESPACE_PREFLIGHT_V1.json"
KD_PREFLIGHT = KE / "G77_256KE_KD_INTERFACE_PREFLIGHT_V1.json"
JZ_READINESS = KE / "G77_256KE_JZ_PRECONSUMPTION_INVOCATION_READINESS_V1.json"
CONTEXT = KE / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
MATERIALIZER = KE / "orchestration/G77_256KE_PREAUTHORIZATION_MATERIALIZER_V1.py"
BINDER = KE / "orchestration/G77_256KE_POSTHUMAN_INVOCATION_BINDER_V1.py"
REPORT = KE / "G77_256KE_G48_IMPLEMENTATION_REPORT_V1.md"
GN = ROOT / (
    ".github/governance/evidence/"
    "g77_256gn_human_authorization_presentation_binding_v1/presentation/"
    "G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
)

HEAD = "ed4acdc4c132754d857d623e54783e54e4c96d52"
TREE = "be8967cad28c9149fb5e17b895e5c58ac119ef13"
TERMINAL = "A__FRESH_KE_EXPIRED_PREAUTHORIZATION_PRESENTATION_READY_FOR_HUMAN_DECISION"
GENERATION = "G77_256KE_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256KE_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"


def canonical_bytes(value) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode()


def canonical(path: Path) -> dict:
    raw = path.read_bytes()
    value = json.loads(raw)
    assert raw == canonical_bytes(value)
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inner(path: Path, key: str) -> dict:
    envelope = canonical(path)
    assert envelope[f"{key}_sha256"] == hashlib.sha256(
        canonical_bytes(envelope[key])
    ).hexdigest()
    return envelope[key]


def load_module(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def test_entry_and_nested_authority_are_exact() -> None:
    reduction = inner(REDUCTION, "reduction")
    entry = reduction["entry"]
    assert (entry["branch"], entry["head"], entry["tree"], entry["subject"]) == (
        "g77-256fl-wrong-attempt-preboot-blocker",
        HEAD,
        TREE,
        "G77-256KD verify KC Phase-B entry owner interface binding",
    )
    assert entry["origin"] == "git@github.com:Aljosa3/sapianta-ecosystem.git"
    assert entry["remote_head"] == HEAD
    assert entry["remote_head"] == entry["head"]
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() == HEAD
    nested = entry["nested_authority"]
    assert nested == {
        "clean": True,
        "detached": True,
        "head": "3183bab71f8f30397c0309dd2e6d846d14a11f66",
        "origin": "git@github.com:Aljosa3/sapianta-core.git",
        "remote_tag": "3183bab71f8f30397c0309dd2e6d846d14a11f66",
        "tag": "sapianta-system-nested-authority-3183bab-v1",
        "tree": "7c32ec05efc2be43297849bc38ec8766514a523d",
    }


def test_all_json_is_canonical_and_sealed() -> None:
    keys = {
        "G77_256KE_PREHUMAN_PHASE_A_REDUCTION_V1.json": "reduction",
        "G77_256KE_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json": "checkpoint",
        "G77_256KE_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json": "checkpoint",
        "G77_256KE_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json": "request",
        "G77_256KE_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json": "proof",
        "G77_256KE_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1.json": "proof",
        "G77_256KE_PREAUTHORITY_STATIC_READINESS_V1.json": "proof",
        "G77_256KE_KB_NAMESPACE_PREFLIGHT_V1.json": "proof",
        "G77_256KE_KD_INTERFACE_PREFLIGHT_V1.json": "proof",
        "G77_256KE_JZ_PRECONSUMPTION_INVOCATION_READINESS_V1.json": "proof",
    }
    for name, key in keys.items():
        inner(KE / name, key)


def test_fresh_identities_temporal_contract_and_cross_hashes() -> None:
    reduction = inner(REDUCTION, "reduction")
    identities = reduction["identities"]
    assert reduction["generation_identity"] == GENERATION
    assert reduction["operation_identity"] == OPERATION
    assert identities["candidate_sha256"] == "8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a"
    assert identities["context_file_sha256"] == sha256(CONTEXT)
    assert identities["request_file_sha256"] == sha256(REQUEST)
    assert identities["presentation_sha256"] == sha256(PRESENTATION)
    assert identities["readiness_checkpoint_file_sha256"] == sha256(READINESS)
    assert identities["checkpoint_file_sha256"] == sha256(SAFE_STOP)
    assert identities["kb_namespace_preflight_file_sha256"] == sha256(KB_PREFLIGHT)
    assert identities["kd_interface_preflight_file_sha256"] == sha256(KD_PREFLIGHT)
    assert identities["jz_invocation_readiness_file_sha256"] == sha256(JZ_READINESS)
    expired = reduction["expired_semantics"]
    assert (expired["valid_from_unix_ns"], expired["valid_until_unix_ns"]) == (100, 1000)
    assert expired["truth_table"] == {"999": "CURRENT", "1000": "EXPIRED", "1001": "EXPIRED"}
    assert expired["governed_preclaim_coordinate_unix_ns"] == 1000
    assert expired["wall_clock_is_governed_preclaim_authority"] is False
    assert expired["expected_denial_reason"] == "one-use Human act expired before PRECLAIM"


def test_kb_namespace_preflight_has_exact_positive_and_eight_negatives() -> None:
    proof = inner(KB_PREFLIGHT, "proof")
    assert proof["actual_namespace"] == "g77_256ke_fresh_expired_operational_recommissioning_v1"
    assert proof["exact_ke_result"]["projection_status"] == "EXACT_GUEST_PROJECTION"
    assert proof["negative_rejection_count"] == 8
    assert set(proof["negative_rejections"]) == {
        "wrong_vector", "wrong_generation", "malformed_namespace", "unrelated_namespace",
        "empty_namespace", "prefix_only", "projection_root_mismatch", "runtime_role_confusion",
    }
    assert all(proof["negative_rejections"].values())
    assert set(proof["operational_counters"].values()) == {0}


def test_kd_interface_preflight_preserves_repaired_owner_contract() -> None:
    proof = inner(KD_PREFLIGHT, "proof")
    assert proof["kd_terminal"] == "A__KC_PHASE_B_PRECONSUMPTION_ENTRY_OWNER_INTERFACE_BINDING_REPOSITORY_VERIFIED"
    assert proof["controller_materializer_binding"] == "VERIFIED__CONTROLLER_MATERIALIZER_IS_K"
    assert proof["resolved_interface"] == "K.A.authenticate_entry(remote_head, nested_remote_tag)"
    assert proof["argument_names"] == ["remote_head", "nested_remote_tag"]
    assert proof["required_reused_interfaces"] == {
        "authenticate_e05_frontier": [], "authenticate_jz": []
    }
    assert proof["fallback_selector_parallel_owner"] == "VERIFIED__ABSENT"
    assert proof["preflight_order"] == "VERIFIED__BEFORE_MATERIALIZE_AND_HUMAN_PRESENTATION"
    assert proof["wrapper_file_sha256"] == sha256(MATERIALIZER)


def test_jz_is_structurally_ready_without_human_digest() -> None:
    proof = inner(JZ_READINESS, "proof")
    assert proof["future_execution_authority_state"] == "ABSENT__EXPLICIT_HUMAN_ACT_NOT_YET_SUPPLIED"
    assert proof["authority_digest_slot"] == "UNMATERIALIZED__DERIVE_FROM_EXACT_CANONICAL_HANDOFF_BYTES_POST_HUMAN"
    assert proof["caller_digest_input_count"] == 0
    assert proof["provider_digest_input_count"] == 0
    assert proof["binding_is_authority"] is False
    assert proof["execution_authorized"] is False
    assert proof["process_started"] is False


def test_phase_a_firewall_e05_reuse_and_architecture() -> None:
    reduction = inner(REDUCTION, "reduction")
    assert reduction["terminal"] == TERMINAL
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["authority_boundary"]["human_operational_authority"] == "VERIFIED__0"
    assert reduction["authority_boundary"]["authority_consumption"] == "VERIFIED__0"
    assert reduction["authority_boundary"]["fresh_human_authority_digest"] == "NOT_MATERIALIZED"
    assert reduction["auto_continuable"] is False
    assert reduction["human_review_required"] is True
    assert reduction["e05"] == {
        "before": "VERIFIED__11_OF_18", "current": "VERIFIED__11_OF_18",
        "credit": "VERIFIED__0", "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
        "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
    }
    assert reduction["ex_reuse"]["ex_reused"] == "VERIFIED__17_OF_17"
    assert reduction["ex_reuse"]["ex_reconstructed"] == "VERIFIED__0"
    assert reduction["architecture"] == {
        "new_constitutional_concept_count": 0, "new_generic_abstraction_count": 0,
        "new_owner_count": 0, "new_registry_count": 0, "new_route_count": 0,
        "p11_implementation_mutation_count": 0, "production_mutation_count": 0,
        "production_route_after": 1, "production_route_before": 1,
        "production_route_delta": 0,
    }
    forbidden = [
        KE / "G77_256KE_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt",
        KE / "G77_256KE_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
        KE / "G77_256KE_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json",
        KE / "G77_256KE_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1.json",
    ]
    assert all(not path.exists() for path in forbidden)


def test_gn_presentation_equivalence_and_inert_sources() -> None:
    gn = load_module(GN, "g77_256ke_test_gn")
    presentation = PRESENTATION.read_bytes()
    result = gn.validate_human_authorization_presentation(REQUEST, presentation)
    assert result["human_presentation_request_equivalence"] == (
        "VERIFIED_WITHIN_EXACT_REVIEWED_AUTHORIZATION_BINDING_BOUNDARY"
    )
    assert b"EXPIRED" in presentation and b"AUTO_CONTINUABLE false" in presentation
    decision = DECISION_PRESENTATION.read_text(encoding="utf-8")
    reduction = inner(REDUCTION, "reduction")
    assert "EXPECTED_RESULT EXPIRED denial before P11 entry" in decision
    assert "OPERATIONAL_STATUS NOT_PROVEN until operationally observed" in decision
    for key in (
        "candidate_sha256", "context_sha256", "context_file_sha256",
        "canonical_argv_sha256", "temporal_binding_sha256", "request_sha256",
        "request_file_sha256", "presentation_sha256",
        "readiness_checkpoint_sha256", "checkpoint_sha256",
    ):
        assert reduction["identities"][key] in decision
    for path in (MATERIALIZER, BINDER):
        ast.parse(path.read_text(encoding="utf-8"))
    materializer_source = MATERIALIZER.read_text(encoding="utf-8")
    assert "subprocess.run(" not in materializer_source
    assert "consume_and_operate" not in materializer_source


def test_g48_exactly_six_h1_and_ria_exact_five_questions() -> None:
    text = REPORT.read_text(encoding="utf-8")
    headings = [line for line in text.splitlines() if line.startswith("# ")]
    assert headings == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    questions = [
        "1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "2. Katere nove zmogljivosti (če sploh) nastanejo?",
        "3. Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "4. Ali implementacija ustvarja vzporedni tok?",
        "5. Ali zmanjšuje ali povečuje število produkcijskih poti?",
    ]
    assert all(text.count(question) == 1 for question in questions)
    reduction = inner(REDUCTION, "reduction")
    for key in (
        "candidate_sha256", "context_sha256", "context_file_sha256",
        "canonical_argv_sha256", "temporal_binding_sha256", "request_sha256",
        "request_file_sha256", "presentation_sha256",
        "readiness_checkpoint_sha256", "checkpoint_sha256",
    ):
        assert reduction["identities"][key] in text
