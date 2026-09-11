from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[5]
KG = ROOT / ".github/governance/evidence/g77_256kg_fresh_expired_operational_recommissioning_v1"
REDUCTION = KG / "G77_256KG_PREHUMAN_PHASE_A_REDUCTION_V1.json"
READINESS = KG / "G77_256KG_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json"
SAFE_STOP = KG / "G77_256KG_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
REQUEST = KG / "G77_256KG_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
PRESENTATION = KG / "G77_256KG_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
DECISION = KG / "G77_256KG_HUMAN_DECISION_PRESENTATION_V1.txt"
KF_PREFLIGHT = KG / "G77_256KG_KF_PERMISSION_BINDING_PREFLIGHT_V1.json"
MATERIALIZER = KG / "orchestration/G77_256KG_PREAUTHORIZATION_MATERIALIZER_V1.py"
BINDER = KG / "orchestration/G77_256KG_POSTHUMAN_INVOCATION_BINDER_V1.py"
REPORT = KG / "G77_256KG_G48_IMPLEMENTATION_REPORT_V1.md"

HEAD = "3bcc78deaeb6821dd71ecdbc9de18628d3ff07de"
TREE = "eb06ab5d18fc99d648b7ba20d40269ccf3d0de40"
TERMINAL = "A__FRESH_KG_EXPIRED_PREAUTHORIZATION_PRESENTATION_READY_FOR_HUMAN_DECISION"
GENERATION = "G77_256KG_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256KG_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode()


def load(path: Path) -> dict:
    raw = path.read_bytes()
    value = json.loads(raw)
    assert raw == canonical_bytes(value)
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reduction() -> dict:
    envelope = load(REDUCTION)
    value = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(
        canonical_bytes(value)
    ).hexdigest()
    return value


def test_exact_committed_entry_nested_authority_and_recovery() -> None:
    value = reduction()
    entry = value["entry"]
    assert entry["head"] == entry["remote_head"] == HEAD
    assert entry["tree"] == TREE
    assert entry["subject"] == "G77-256KF verify guest harness permission binding repair"
    assert entry["direct_remote_equality"] == "VERIFIED"
    nested = entry["nested_authority"]
    assert nested["head"] == nested["remote_tag"] == (
        "3183bab71f8f30397c0309dd2e6d846d14a11f66"
    )
    assert nested["clean"] and nested["detached"]
    assert value["existing_kg_delta_reconstruction"] == (
        "VERIFIED__NONE__CLEAN_COMMITTED_KF_ENTRY"
    )
    assert set(value["recovery_operational_counters"].values()) == {0}


def test_terminal_identity_e05_and_operational_firewall() -> None:
    value = reduction()
    assert value["terminal"] == TERMINAL
    assert value["generation_identity"] == GENERATION
    assert value["operation_identity"] == OPERATION
    assert set(value["operational_counters"].values()) == {0}
    assert value["e05"] == {
        "before": "VERIFIED__11_OF_18",
        "credit": "VERIFIED__0",
        "current": "VERIFIED__11_OF_18",
        "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
        "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
    }
    assert value["human_authority_present"] is False
    assert value["auto_continuable"] is False
    assert value["human_review_required"] is True


def test_kf_permission_contract_is_exact_and_repository_only() -> None:
    value = reduction()
    kf = value["kf_authentication"]
    assert kf["terminal"] == "A__GUEST_HARNESS_PERMISSION_BINDING_REPOSITORY_VERIFIED"
    assert kf["construction_mode"] == "0700"
    assert kf["presentation_mode"] == "0701"
    assert kf["context_owner_mode"] == "0644"
    assert kf["one_bit_delta"] == "VERIFIED"
    assert kf["source_execute_required"] == "NO"
    assert kf["read_only_projection"] == "VERIFIED__PRESERVED"
    assert kf["new_route"] == kf["new_owner"] == "VERIFIED__NO"
    proof = load(KF_PREFLIGHT)["proof"]
    assert proof["observed_presentation_mode"] == "0701"
    assert proof["committed_context_owner_mode"] == "0644"
    assert proof["custody_effective_context_owner_mode"] == "0004"
    assert proof["operational_guest_success"] == "NOT_PROVEN"
    assert set(proof["operational_counters"].values()) == {0}


def test_ex_reuse_and_deterministic_expired_contract() -> None:
    value = reduction()
    assert value["ex_reuse"]["ex_reused"] == "VERIFIED__17_OF_17"
    assert value["ex_reuse"]["ex_reconstructed"] == "VERIFIED__0"
    expired = value["expired_semantics"]
    assert expired["valid_from_unix_ns"] == 100
    assert expired["valid_until_unix_ns"] == 1000
    assert expired["governed_preclaim_coordinate_unix_ns"] == 1000
    assert expired["truth_table"] == {
        "999": "CURRENT", "1000": "EXPIRED", "1001": "EXPIRED",
    }
    assert expired["expected_denial_reason"] == (
        "one-use Human act expired before PRECLAIM"
    )
    assert expired["wall_clock_is_governed_preclaim_authority"] is False


def test_request_presentation_readiness_and_safe_stop_are_cross_bound() -> None:
    value = reduction()
    identities = value["identities"]
    request = load(REQUEST)
    readiness = load(READINESS)
    safe_stop = load(SAFE_STOP)
    assert request["request_sha256"] == identities["request_sha256"]
    assert sha256(REQUEST) == identities["request_file_sha256"]
    assert request["request"]["preauthorization"]["checkpoint_inner_sha256"] == (
        identities["readiness_checkpoint_sha256"]
    )
    assert readiness["checkpoint_sha256"] == identities["readiness_checkpoint_sha256"]
    assert safe_stop["checkpoint_sha256"] == identities["checkpoint_sha256"]
    assert safe_stop["checkpoint"]["request_identity"] == identities["request_sha256"]
    assert sha256(PRESENTATION) == identities["presentation_sha256"]
    assert safe_stop["checkpoint"]["presentation_identity"] == sha256(PRESENTATION)
    for token in (
        GENERATION, OPERATION, identities["candidate_sha256"],
        identities["context_sha256"], identities["context_file_sha256"],
        identities["canonical_argv_sha256"], identities["temporal_binding_sha256"],
        identities["request_sha256"], identities["request_file_sha256"],
        identities["presentation_sha256"], identities["readiness_checkpoint_sha256"],
        identities["checkpoint_sha256"],
    ):
        assert token in DECISION.read_text(encoding="utf-8")


def test_freshness_firewall_preserves_canonical_candidate_only() -> None:
    current = reduction()["identities"]
    fresh_required = (
        "context_sha256", "context_file_sha256", "canonical_argv_sha256",
        "temporal_binding_sha256", "request_sha256", "request_file_sha256",
        "presentation_sha256", "readiness_checkpoint_sha256", "checkpoint_sha256",
    )
    for predecessor in ("kc", "ke"):
        path = ROOT / (
            ".github/governance/evidence/"
            f"g77_256{predecessor}_fresh_expired_operational_recommissioning_v1/"
            f"G77_256{predecessor.upper()}_PREHUMAN_PHASE_A_REDUCTION_V1.json"
        )
        prior = load(path)["reduction"]["identities"]
        assert all(current[key] != prior[key] for key in fresh_required)
        assert current["candidate_sha256"] == prior["candidate_sha256"]
    assert load(REQUEST)["request"]["live_binding"][
        "candidate_binding_regeneration_required"
    ] is True


def test_jz_phase_a_is_structural_only() -> None:
    value = reduction()["jz_preconsumption_invocation_readiness"]
    assert value["phase_a_digest_equality"] == (
        "NOT_APPLICABLE__NO_FRESH_HUMAN_AUTHORITY_DIGEST_EXISTS"
    )
    assert value["posthuman_digest_equality"] == (
        "AUTHENTICATED_CANONICAL_AUTHORITY_DIGEST_EQUALS_SEALED_INVOCATION_"
        "AUTHORITY_DIGEST_EQUALS_FINAL_FM_ARGV_AUTHORITY_DIGEST"
    )
    proof = load(KG / "G77_256KG_JZ_PRECONSUMPTION_INVOCATION_READINESS_V1.json")["proof"]
    assert ROOT / proof["posthuman_binding_adapter_path"] == BINDER
    tree = ast.parse(BINDER.read_text(encoding="utf-8"))
    binding = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "bind_posthuman_invocation"
    )
    assert [argument.arg for argument in binding.args.kwonlyargs] == [
        "operation_context", "live_candidate_binding", "execution_authority",
    ]
    assert "authority_digest" not in BINDER.read_text(encoding="utf-8")


def test_architecture_proof_yield_ccwim_and_reuse_impact() -> None:
    value = reduction()
    architecture = value["architecture"]
    assert all(architecture[key] == 0 for key in (
        "production_mutation_count", "p11_implementation_mutation_count",
        "new_owner_count", "new_route_count", "new_registry_count",
        "new_generic_abstraction_count", "new_constitutional_concept_count",
    ))
    assert architecture["production_route_before"] == 1
    assert architecture["production_route_after"] == 1
    assert value["proof_yield"]["proof_reuse_count"] == "VERIFIED__17"
    assert value["proof_yield"]["e05_credit"] == "VERIFIED__0"
    assert value["reuse_impact_assessment"]["parallel_flow_created"] is False
    assert value["ccwim"]["handoff_ambiguity_count"] == "VERIFIED__0"


def test_materializer_has_no_operational_entry_and_artifacts_are_canonical() -> None:
    tree = ast.parse(MATERIALIZER.read_text(encoding="utf-8"))
    calls = {
        node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, (ast.Attribute, ast.Name))
    }
    assert not ({"Popen", "execv", "execve"} & calls)
    for path in KG.rglob("*.json"):
        load(path)


def test_g48_exactly_six_h1_and_ria_exactly_five_questions() -> None:
    text = REPORT.read_text(encoding="utf-8")
    assert re.findall(r"^# .+$", text, flags=re.MULTILINE) == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    questions = re.findall(r"^\d+\. .+\?$", text, flags=re.MULTILINE)
    assert len(questions) == 5
