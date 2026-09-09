from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[5]
JW = ROOT / ".github/governance/evidence/g77_256jw_expired_operational_v1"
MATERIALIZER = JW / "orchestration/G77_256JW_PREAUTHORIZATION_MATERIALIZER_V1.py"
REQUEST = JW / "G77_256JW_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
PRESENTATION = JW / "G77_256JW_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
READINESS = JW / "G77_256JW_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json"
SAFE_STOP = JW / "G77_256JW_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
EQUIVALENCE = JW / "G77_256JW_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json"
REDUCTION = JW / "G77_256JW_PREHUMAN_PHASE_A_REDUCTION_V1.json"
CONTEXT = JW / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
REPORT = JW / "G77_256JW_G48_IMPLEMENTATION_REPORT_V1.md"


def load(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


M = load(MATERIALIZER, "g77_256jw_test_materializer")


def canonical(path: Path) -> dict:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=M.unique_object)
    assert raw == M.canonical_bytes(value)
    return value


def test_exact_remote_ratified_jv_entry_and_nested_authority() -> None:
    entry = M.authenticate_entry(M.HEAD, M.NESTED_HEAD)
    assert entry["branch"] == M.BRANCH
    assert entry["head"] == "98206cab55fb4201c3b60de48eb032cca196de7c"
    assert entry["tree"] == "ab1a39d41553fc0296e65287782a36b1f20fb22b"
    assert entry["subject"] == "G77-256JV verify EXPIRED GN request projection"
    assert entry["remote_head"] == M.HEAD
    assert entry["index_empty"] is True
    assert entry["nested_authority"]["head"] == M.NESTED_HEAD
    assert entry["nested_authority"]["tree"] == M.NESTED_TREE
    assert entry["nested_authority"]["clean"] is True
    assert entry["nested_authority"]["detached"] is True


def test_jv_jt_ex_and_fresh_identity_authenticate() -> None:
    jv = M.authenticate_jv()
    jt = M.authenticate_jt()
    ex = M.authenticate_ex()
    fresh = M.authenticate_fresh_identity()
    assert jv["terminal"] == M.JV_TERMINAL
    assert jv["gn_contract_conclusion"] == (
        "A_AND_D__GN_V1_IS_VECTOR_INDEPENDENT__JU_USED_WRONG_PROJECTION"
    )
    assert jv["canonical_counter_slot"] == "wrong_attempt_execution_count"
    assert jv["canonical_live_binding_slots"] == ["du", "eb", "ee"]
    assert jt["terminal"] == M.JT_TERMINAL
    assert jt["recurrence_hazard"] == "VERIFIED__ELIMINATED"
    assert jt["stable_checkout"] == {"head": M.JR_HEAD, "tree": M.JR_TREE}
    assert ex["ex_reused"] == "VERIFIED__17_OF_17"
    assert ex["ex_reconstructed"] == "VERIFIED__0"
    assert fresh["committed_history_collision"] == "VERIFIED__NO"
    assert fresh["prior_authorization_reuse"] == "VERIFIED__NO"


def test_fresh_context_preserves_expired_temporal_and_stable_checkout_roles() -> None:
    context = canonical(CONTEXT)
    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    assert context["generation_identity"] == M.GENERATION
    assert context["operation_identity"] == M.OPERATION
    assert context["repository_head"] == M.HEAD
    assert context["repository_tree"] == M.TREE
    assert (checkout["head"], checkout["tree"]) == (M.JR_HEAD, M.JR_TREE)
    assert context["preclaim_temporal_binding"]["coordinate_unix_ns"] == 1000
    assert M.authenticate_expired_semantics()["truth_table"] == {
        "999": "CURRENT",
        "1000": "EXPIRED",
        "1001": "EXPIRED",
    }


def test_request_is_exact_gn_v1_projection_and_presentation_is_deterministic() -> None:
    envelope = M.GN.load_validated_sealed_request(REQUEST)
    request = envelope["request"]
    assert set(request) == M.GN.REQUEST_FIELDS
    assert set(request["live_binding"]) == M.GN.LIVE_BINDING_FIELDS
    assert request["authorized_vector_requested"] == "EXPIRED"
    assert request["wrong_attempt_execution_count"] == 0
    assert "expired_execution_count" not in request
    assert "expired_adapter_sha256" not in request["live_binding"]
    assert "temporal_binding_sha256" not in request["live_binding"]
    assert {key: request["live_binding"][key] for key in ("du", "eb", "ee")} == {
        "du": "PASS",
        "eb": "PASS",
        "ee": "PASS",
    }
    presentation = PRESENTATION.read_bytes()
    assert presentation == M.GN.render_human_authorization_presentation(REQUEST)
    result = M.GN.validate_human_authorization_presentation(REQUEST, presentation)
    assert result["human_presentation_request_equivalence"] == (
        "VERIFIED_WITHIN_EXACT_REVIEWED_AUTHORIZATION_BINDING_BOUNDARY"
    )
    assert result["human_constitutional_authorization_count"] == 0


def test_safe_stop_binds_exact_request_presentation_equivalence_and_readiness() -> None:
    request = canonical(REQUEST)
    readiness = canonical(READINESS)
    equivalence = canonical(EQUIVALENCE)
    safe_stop = canonical(SAFE_STOP)
    checkpoint = safe_stop["checkpoint"]
    assert safe_stop["checkpoint_sha256"] == hashlib.sha256(
        M.canonical_bytes(checkpoint)
    ).hexdigest()
    assert checkpoint["terminal"] == M.PHASE_A_TERMINAL
    assert checkpoint["request_identity"] == request["request_sha256"]
    assert checkpoint["request_file_sha256"] == M.sha256_path(REQUEST)
    assert checkpoint["presentation_identity"] == M.sha256_path(PRESENTATION)
    assert checkpoint["equivalence_file_sha256"] == M.sha256_path(EQUIVALENCE)
    assert checkpoint["equivalence_inner_sha256"] == equivalence["proof_sha256"]
    assert checkpoint["readiness_checkpoint_file_sha256"] == M.sha256_path(READINESS)
    assert checkpoint["readiness_checkpoint_inner_sha256"] == readiness["checkpoint_sha256"]
    assert set(checkpoint["operational_counters"].values()) == {0}
    assert checkpoint["authority_boundary"]["human_authority_present"] is False
    assert checkpoint["authority_boundary"]["auto_continuable"] is False
    assert checkpoint["authority_boundary"]["human_review_required"] is True


def test_phase_a_reduction_counters_e05_architecture_and_frontier_are_exact() -> None:
    reduction = canonical(REDUCTION)["reduction"]
    assert reduction["terminal"] == M.PHASE_A_TERMINAL
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"] == {
        "before": "VERIFIED__11_OF_18",
        "current": "VERIFIED__11_OF_18",
        "credit": "VERIFIED__0",
        "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
        "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
    }
    assert set(reduction["architecture"].values()) == {0, 1}
    assert reduction["architecture"]["production_route_before"] == 1
    assert reduction["architecture"]["production_route_after"] == 1
    assert reduction["architecture"]["production_route_delta"] == 0
    assert reduction["frontier"] == {
        "last_verified_edge": "FRESH_JW_EXPIRED_PREAUTHORIZATION_CHECKPOINT_AND_HUMAN_PRESENTATION_MATERIALIZED",
        "first_broken_edge": "EXACT_HUMAN_AUTHORIZATION_NOT_YET_SUPPLIED",
        "minimum_missing_capability": "EXACT_HUMAN_AUTHORIZATION_FOR_BOUND_JW_EXPIRED_OPERATION",
        "minimum_legal_next_delta": "SAME_GENERATION_JW_HUMAN_AUTHORIZATION_CONSUMPTION_AND_ONE_OPERATION",
    }


def test_all_generation_json_is_unique_key_and_canonical_with_valid_outer_seals() -> None:
    for path in sorted(JW.rglob("*.json")):
        envelope = canonical(path)
        for inner_name, inner in envelope.items():
            seal_name = f"{inner_name}_sha256"
            if isinstance(inner, dict) and seal_name in envelope:
                assert envelope[seal_name] == hashlib.sha256(
                    M.canonical_bytes(inner)
                ).hexdigest(), path


def test_materializer_cannot_consume_authority_or_launch_operation() -> None:
    source = MATERIALIZER.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(MATERIALIZER))
    called_attributes = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert not {
        "write_authority_handoff",
        "validate_final_admission",
        "claim_and_invoke_once",
        "Popen",
    }.intersection(called_attributes)
    assert "qemu-system-x86_64" not in source
    assert "G77_256JW_AUTHORITY_CONSUMPTION_CONTROLLER_V1.py" not in source


def test_g48_has_exact_six_h1_and_five_slovenian_questions() -> None:
    text = REPORT.read_text(encoding="utf-8")
    assert [line for line in text.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    for question in (
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
    ):
        assert text.count(question) == 1
    assert subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True
    ).strip() == ""
