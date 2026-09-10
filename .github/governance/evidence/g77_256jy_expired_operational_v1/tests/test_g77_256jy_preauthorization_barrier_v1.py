from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[5]
JY = ROOT / ".github/governance/evidence/g77_256jy_expired_operational_v1"
MATERIALIZER = JY / "orchestration/G77_256JY_PREAUTHORIZATION_MATERIALIZER_V1.py"
REQUEST = JY / "G77_256JY_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
PRESENTATION = JY / "G77_256JY_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
READINESS = JY / "G77_256JY_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json"
SAFE_STOP = JY / "G77_256JY_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
EQUIVALENCE = JY / "G77_256JY_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json"
REDUCTION = JY / "G77_256JY_PREHUMAN_PHASE_A_REDUCTION_V1.json"
CONTEXT = JY / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
CANDIDATE = JY / (
    "live_binding/candidate/"
    "G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
)
REPORT = JY / "G77_256JY_G48_IMPLEMENTATION_REPORT_V1.md"


def load(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


M = load(MATERIALIZER, "g77_256jy_test_materializer")


def canonical(path: Path) -> dict:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=M.M.unique_object)
    assert raw == M.M.canonical_bytes(value)
    return value


def test_exact_remote_ratified_jx_entry_and_nested_authority() -> None:
    entry = M.M.authenticate_entry(M.HEAD, M.M.NESTED_HEAD)
    assert entry["branch"] == M.BRANCH
    assert entry["head"] == M.HEAD
    assert entry["tree"] == M.TREE
    assert entry["subject"] == M.SUBJECT
    assert entry["remote_head"] == M.HEAD
    assert entry["index_empty"] is True
    assert entry["nested_authority"]["head"] == M.M.NESTED_HEAD
    assert entry["nested_authority"]["tree"] == M.M.NESTED_TREE
    assert entry["nested_authority"]["clean"] is True
    assert entry["nested_authority"]["detached"] is True


def test_committed_jx_repair_ex_and_fresh_jy_identity_authenticate() -> None:
    jx = M.authenticate_jx()
    ex = M.M.authenticate_ex()
    fresh = M.M.authenticate_fresh_identity()
    assert jx["terminal"] == M.JX_TERMINAL
    assert jx["stable_checkout"] == {"head": M.JR_HEAD, "tree": M.JR_TREE}
    assert jx["p11_implementation_sha256"] == M.JX_HASHES[M.P11]
    assert jx["production_route"] == "VERIFIED__1_TO_1"
    assert ex["ex_reused"] == "VERIFIED__17_OF_17"
    assert ex["ex_reconstructed"] == "VERIFIED__0"
    assert fresh["committed_history_collision"] == "VERIFIED__NO"
    assert fresh["prior_authorization_reuse"] == "VERIFIED__NO"


def test_fresh_context_preserves_distinct_admission_and_runtime_roles() -> None:
    context = canonical(CONTEXT)
    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    seed = context["qemu_executable_base_seed_checkout_bindings"]["seed"]
    assert context["generation_identity"] == M.M.GENERATION
    assert context["operation_identity"] == M.M.OPERATION
    assert (context["repository_head"], context["repository_tree"]) == (
        M.HEAD,
        M.TREE,
    )
    assert (checkout["head"], checkout["tree"]) == (M.JR_HEAD, M.JR_TREE)
    assert checkout["head"] != context["repository_head"]
    assert seed["path"] == str(ROOT / M.JX_SEED)
    assert context["guest_adapter_binding"]["source_sha256"] == M.JX_HASHES[M.ADAPTER]
    assert context["preclaim_temporal_binding"]["coordinate_unix_ns"] == 1000
    M.M.FM.validate_immutable_context_bindings(
        ROOT, context, CANDIDATE.relative_to(ROOT)
    )


def test_exact_expired_contract_and_gn_v1_request_projection() -> None:
    expired = M.M.authenticate_expired_semantics()
    assert expired["truth_table"] == {
        "999": "CURRENT",
        "1000": "EXPIRED",
        "1001": "EXPIRED",
    }
    assert expired["expected_denial_reason"] == (
        "one-use Human act expired before PRECLAIM"
    )
    envelope = M.M.GN.load_validated_sealed_request(REQUEST)
    request = envelope["request"]
    assert set(request) == M.M.GN.REQUEST_FIELDS
    assert set(request["live_binding"]) == M.M.GN.LIVE_BINDING_FIELDS
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


def test_presentation_is_deterministic_nonauthority_and_request_equivalent() -> None:
    presentation = PRESENTATION.read_bytes()
    assert presentation == M.M.GN.render_human_authorization_presentation(REQUEST)
    result = M.M.GN.validate_human_authorization_presentation(
        REQUEST, presentation
    )
    assert result["human_presentation_request_equivalence"] == (
        "VERIFIED_WITHIN_EXACT_REVIEWED_AUTHORIZATION_BINDING_BOUNDARY"
    )
    assert result["human_constitutional_authorization_count"] == 0


def test_safe_stop_binds_exact_package_and_all_counters_are_zero() -> None:
    request = canonical(REQUEST)
    readiness = canonical(READINESS)
    equivalence = canonical(EQUIVALENCE)
    safe_stop = canonical(SAFE_STOP)
    checkpoint = safe_stop["checkpoint"]
    assert safe_stop["checkpoint_sha256"] == hashlib.sha256(
        M.M.canonical_bytes(checkpoint)
    ).hexdigest()
    assert checkpoint["terminal"] == M.M.PHASE_A_TERMINAL
    assert checkpoint["request_identity"] == request["request_sha256"]
    assert checkpoint["request_file_sha256"] == M.M.sha256_path(REQUEST)
    assert checkpoint["presentation_identity"] == M.M.sha256_path(PRESENTATION)
    assert checkpoint["equivalence_file_sha256"] == M.M.sha256_path(EQUIVALENCE)
    assert checkpoint["equivalence_inner_sha256"] == equivalence["proof_sha256"]
    assert checkpoint["readiness_checkpoint_file_sha256"] == M.M.sha256_path(READINESS)
    assert checkpoint["readiness_checkpoint_inner_sha256"] == readiness["checkpoint_sha256"]
    assert set(checkpoint["operational_counters"].values()) == {0}
    assert checkpoint["authority_boundary"]["human_authority_present"] is False
    assert checkpoint["authority_boundary"]["auto_continuable"] is False
    assert checkpoint["authority_boundary"]["human_review_required"] is True


def test_phase_a_reduction_is_narrow_and_sealed() -> None:
    envelope = canonical(REDUCTION)
    reduction = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(
        M.M.canonical_bytes(reduction)
    ).hexdigest()
    assert reduction["terminal"] == M.M.PHASE_A_TERMINAL
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"] == {
        "before": "VERIFIED__11_OF_18",
        "current": "VERIFIED__11_OF_18",
        "credit": "VERIFIED__0",
        "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
        "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
    }
    assert reduction["architecture"] == {
        "p11_implementation_mutation_count": 0,
        "production_mutation_count": 0,
        "new_owner_count": 0,
        "new_route_count": 0,
        "new_registry_count": 0,
        "new_generic_abstraction_count": 0,
        "new_constitutional_concept_count": 0,
        "production_route_before": 1,
        "production_route_after": 1,
        "production_route_delta": 0,
    }
    assert reduction["governance_dashboard"][
        "constitutional_continuation_progress"
    ] == "VERIFIED__JX_TO_JY_PREAUTHORIZATION_STOP"


def test_all_jy_json_is_unique_key_canonical_and_outer_sealed() -> None:
    for path in sorted(JY.rglob("*.json")):
        envelope = canonical(path)
        for inner_name, inner in envelope.items():
            seal_name = f"{inner_name}_sha256"
            if isinstance(inner, dict) and seal_name in envelope:
                assert envelope[seal_name] == hashlib.sha256(
                    M.M.canonical_bytes(inner)
                ).hexdigest(), path


def test_phase_a_has_no_authority_consumption_or_operational_launch() -> None:
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
    assert not list((JY / "operation_state").rglob("*RECEIPT*.json"))
    assert subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True
    ).strip() == ""


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
