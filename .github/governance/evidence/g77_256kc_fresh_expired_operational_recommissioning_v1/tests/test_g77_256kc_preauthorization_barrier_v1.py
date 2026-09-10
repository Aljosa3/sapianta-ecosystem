from __future__ import annotations

import ast
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import subprocess
import sys

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KC = ROOT / (
    ".github/governance/evidence/"
    "g77_256kc_fresh_expired_operational_recommissioning_v1"
)
REDUCTION = KC / "G77_256KC_PREHUMAN_PHASE_A_REDUCTION_V1.json"
READINESS = KC / "G77_256KC_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json"
SAFE_STOP = KC / "G77_256KC_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
REQUEST = KC / "G77_256KC_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
PRESENTATION = KC / "G77_256KC_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
JZ_READINESS = KC / "G77_256KC_JZ_PRECONSUMPTION_INVOCATION_READINESS_V1.json"
KB_PREFLIGHT = KC / "G77_256KC_KB_NAMESPACE_PREFLIGHT_V1.json"
CONTEXT = KC / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
BINDER = KC / "orchestration/G77_256KC_POSTHUMAN_INVOCATION_BINDER_V1.py"
MATERIALIZER = KC / "orchestration/G77_256KC_PREAUTHORIZATION_MATERIALIZER_V1.py"
REPORT = KC / "G77_256KC_G48_IMPLEMENTATION_REPORT_V1.md"
FM = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
OWNER = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "sapianta_fresh_operation_context_v1.py"
)
GN = ROOT / (
    ".github/governance/evidence/"
    "g77_256gn_human_authorization_presentation_binding_v1/presentation/"
    "G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
)
KA_REDUCTION = ROOT / (
    ".github/governance/evidence/"
    "g77_256ka_fresh_expired_operational_recommissioning_v1/"
    "G77_256KA_SPCE_TERMINAL_FAILURE_REDUCTION_V2.json"
)

HEAD = "2b0a1ff1d7bc3e071392a786dfb64c2eac392df3"
TREE = "2b7e42af265f20404ad467c6f1069df56cc388f8"
TERMINAL = "A__FRESH_KC_EXPIRED_PREAUTHORIZATION_PRESENTATION_READY_FOR_HUMAN_DECISION"
GENERATION = "G77_256KC_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256KC_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"
NAMESPACE = "g77_256kc_fresh_expired_operational_recommissioning_v1"
OWNER_SHA256 = "337aa8d19f519bd0873ff9d688c16fc6b914e70ef1b03504813d2f4fdf8d899b"
LAUNCHER_SHA256 = "662cce2458300c12cb6dfb18d8c836db7867c4400430a8081acbb4e285a60a36"


def load_module(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


GN_MODULE = load_module(GN, "g77_256kc_test_gn")
BINDER_MODULE = load_module(BINDER, "g77_256kc_test_binder")
OWNER_MODULE = load_module(OWNER, "g77_256kc_test_owner")


def canonical_bytes(value) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode()


def canonical(path: Path) -> dict:
    raw = path.read_bytes()

    def unique_object(pairs):
        value = {}
        for key, item in pairs:
            assert key not in value
            value[key] = item
        return value

    value = json.loads(raw, object_pairs_hook=unique_object)
    assert raw == canonical_bytes(value)
    return value


def sealed(path: Path, inner: str) -> dict:
    envelope = canonical(path)
    value = envelope[inner]
    assert envelope[f"{inner}_sha256"] == hashlib.sha256(canonical_bytes(value)).hexdigest()
    return value


def test_entry_cross_account_and_nested_authority_are_exact() -> None:
    reduction = sealed(REDUCTION, "reduction")
    entry = reduction["entry"]
    assert (entry["head"], entry["tree"], entry["remote_head"]) == (HEAD, TREE, HEAD)
    assert entry["branch"] == "g77-256fl-wrong-attempt-preboot-blocker"
    assert entry["subject"] == "G77-256KB verify EXPIRED guest namespace binding repair"
    assert entry["origin"] == "git@github.com:Aljosa3/sapianta-ecosystem.git"
    assert entry["direct_remote_equality"] == "VERIFIED"
    assert entry["worktree_clean_before_first_mutation"] is True
    assert entry["index_empty"] is True
    assert entry["nested_authority"] == {
        "clean": True,
        "detached": True,
        "head": "3183bab71f8f30397c0309dd2e6d846d14a11f66",
        "origin": "git@github.com:Aljosa3/sapianta-core.git",
        "remote_tag": "3183bab71f8f30397c0309dd2e6d846d14a11f66",
        "tag": "sapianta-system-nested-authority-3183bab-v1",
        "tree": "7c32ec05efc2be43297849bc38ec8766514a523d",
    }


def test_ka_terminal_and_kb_repair_are_historical_and_authenticated() -> None:
    reduction = sealed(REDUCTION, "reduction")
    kb = reduction["kb_authentication"]
    assert kb["terminal"] == "A__EXPIRED_GUEST_CONTEXT_NAMESPACE_BINDING_REPOSITORY_VERIFIED"
    assert kb["ka_terminal"] == (
        "M__KA_AUTHORIZED_EXPIRED_OPERATION_FAILED_AT_GUEST_CONTEXT_"
        "NAMESPACE_BINDING_BEFORE_REQUEST"
    )
    assert kb["ka_authority"] == "CONSUMED__NONREUSABLE__NONTRANSFERABLE"
    assert kb["owner_sha256"] == OWNER_SHA256
    assert kb["launcher_sha256"] == LAUNCHER_SHA256
    ka = sealed(KA_REDUCTION, "reduction")
    assert ka["terminal"] == kb["ka_terminal"]
    assert ka["human_authority"]["state"] == (
        "VERIFIED__CONSUMED_EXACTLY_ONCE__NONREUSABLE__NONTRANSFERABLE"
    )


def test_exact_kc_namespace_passes_current_kb_repaired_owner() -> None:
    proof = sealed(KB_PREFLIGHT, "proof")
    context = canonical(CONTEXT)
    assert proof["actual_namespace"] == NAMESPACE
    assert Path(proof["operation_evidence_root"]) == KC / "operation_state"
    assert proof["current_owner_sha256"] == OWNER_SHA256
    assert proof["current_launcher_sha256"] == LAUNCHER_SHA256
    assert proof["exact_kc_result"]["projection_status"] == "EXACT_GUEST_PROJECTION"
    assert proof["same_owner_relation_to_ka"] == (
        "VERIFIED__CURRENT_KB_REPAIRED_OWNER_SUCCEEDS_OWNER_THAT_REJECTED_KA"
    )
    assert proof["proof_scope"] == "REPOSITORY_PREFLIGHT_ONLY__NOT_OPERATIONAL_EXPIRED_PROOF"
    observed = OWNER_MODULE.validate_sealed_canonical_argv(
        context, validation_repository_root=OWNER_MODULE.GUEST_REPOSITORY_ROOT
    )
    assert observed == proof["exact_kc_result"]


def test_namespace_positive_history_and_negative_matrix_are_exact() -> None:
    proof = sealed(KB_PREFLIGHT, "proof")
    assert proof["historical_accepted_namespace"] == "g77_256kc_expired_operational_v1"
    assert proof["historical_accepted_result"] == "VERIFIED__ACCEPTED"
    assert set(proof["negative_rejections"]) == {
        "wrong_vector", "wrong_generation", "malformed_namespace", "empty_namespace",
        "prefix_only", "projection_root_mismatch", "runtime_role_confusion",
    }
    assert proof["negative_rejection_count"] == 7
    assert all(proof["negative_rejections"].values())


def test_fresh_identity_temporal_contract_and_runtime_roles() -> None:
    reduction = sealed(REDUCTION, "reduction")
    assert reduction["generation_identity"] == GENERATION
    assert reduction["operation_identity"] == OPERATION
    assert reduction["expired_semantics"] == {
        "caller_provider_human_selectable_coordinate_count": 0,
        "expected_denial_boundary": "BEFORE_P11_DA_OPERATIONAL_PRECLAIM_APPEND",
        "expected_denial_reason": "one-use Human act expired before PRECLAIM",
        "expected_owner_transition": "AVAILABLE_TO_EXPIRED",
        "governed_preclaim_coordinate_unix_ns": 1000,
        "submission_time_unix_ns": 500,
        "truth_table": {"999": "CURRENT", "1000": "EXPIRED", "1001": "EXPIRED"},
        "valid_from_unix_ns": 100,
        "valid_until_unix_ns": 1000,
        "vector": "EXPIRED",
        "wall_clock_is_governed_preclaim_authority": False,
    }
    assert reduction["jx_reconstruction"]["stable_checkout"] == {
        "head": "304b342e26e92f226afa01db4b4203acfa51f532",
        "tree": "fc0c50e4dd79e900d85d48c5c0aeb53fe9d0c937",
    }


def test_jz_route_is_ready_without_fabricating_authority() -> None:
    proof = sealed(JZ_READINESS, "proof")
    assert proof["future_execution_authority_state"] == "ABSENT__EXPLICIT_HUMAN_ACT_NOT_YET_SUPPLIED"
    assert proof["digest_equality_phase_a_status"] == "NOT_APPLICABLE__NO_FRESH_HUMAN_AUTHORITY_DIGEST_EXISTS"
    assert proof["authority_digest_slot"] == "UNMATERIALIZED__DERIVE_FROM_EXACT_CANONICAL_HANDOFF_BYTES_POST_HUMAN"
    assert proof["final_fm_argv_state"] == "NOT_MATERIALIZED__NO_HUMAN_AUTHORITY_EXISTS"
    assert proof["caller_digest_input_count"] == proof["provider_digest_input_count"] == 0
    assert proof["authority_consumption_count"] == proof["fm_operational_invocation_count"] == 0
    assert proof["process_started"] is False
    assert not (ROOT / proof["future_execution_authority_path"]).exists()
    assert list(inspect.signature(BINDER_MODULE.bind_posthuman_invocation).parameters) == [
        "operation_context", "live_candidate_binding", "execution_authority"
    ]
    source = BINDER.read_text(encoding="utf-8")
    assert "FM.build_preconsumption_invocation_binding" in source
    assert "FM.validate_preconsumption_invocation_binding" in source
    assert "subprocess.run" not in source


def test_request_presentation_and_human_barrier_are_exact() -> None:
    request = sealed(REQUEST, "request")
    assert request["generation_identity"] == GENERATION
    assert request["operation_identity"] == OPERATION
    assert request["authorized_vector_requested"] == "EXPIRED"
    assert request["request_is_authority"] is False
    assert request["checkpoint_is_authority"] is False
    assert request["auto_continuable"] is False
    assert request["human_review_required"] is True
    assert GN_MODULE.render_human_authorization_presentation(REQUEST) == PRESENTATION.read_bytes()
    result = GN_MODULE.validate_human_authorization_presentation(REQUEST, PRESENTATION.read_bytes())
    assert result["human_presentation_request_equivalence"] == (
        "VERIFIED_WITHIN_EXACT_REVIEWED_AUTHORIZATION_BINDING_BOUNDARY"
    )


def test_zero_operation_e05_ex_architecture_and_frontier() -> None:
    reduction = sealed(REDUCTION, "reduction")
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"] == {
        "before": "VERIFIED__11_OF_18",
        "current": "VERIFIED__11_OF_18",
        "credit": "VERIFIED__0",
        "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
        "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
    }
    assert reduction["ex_reuse"]["ex_reused"] == "VERIFIED__17_OF_17"
    assert reduction["ex_reuse"]["ex_reconstructed"] == "VERIFIED__0"
    assert set(reduction["architecture"].values()) <= {0, 1}
    assert reduction["architecture"]["production_route_before"] == 1
    assert reduction["architecture"]["production_route_after"] == 1
    assert reduction["terminal"] == TERMINAL
    assert reduction["frontier"] == {
        "last_verified_edge": "FRESH_KC_EXPIRED_PREAUTHORIZATION_AND_KB_NAMESPACE_PREFLIGHT_READY",
        "first_broken_edge": "EXACT_FRESH_KC_HUMAN_AUTHORIZATION_NOT_YET_SUPPLIED",
        "minimum_missing_capability": "EXACT_FRESH_HUMAN_AUTHORIZATION_FOR_BOUND_KC_EXPIRED_OPERATION",
        "minimum_legal_next_delta": "SAME_GENERATION_SPCE_PHASE_B_ONLY_AFTER_EXPLICIT_HUMAN_ACT",
    }
    for forbidden in (
        "G77_256KC_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt",
        "G77_256KC_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
        "G77_256KC_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json",
    ):
        assert not (KC / forbidden).exists()


def test_all_json_is_canonical_inner_sealed_and_identity_bound() -> None:
    for path in KC.rglob("*.json"):
        envelope = canonical(path)
        for key, value in envelope.items():
            if key.endswith("_sha256"):
                inner = key[:-7]
                if inner in envelope and isinstance(envelope[inner], dict):
                    assert value == hashlib.sha256(canonical_bytes(envelope[inner])).hexdigest()
    identities = sealed(REDUCTION, "reduction")["identities"]
    paths = {
        "request_file_sha256": REQUEST,
        "presentation_sha256": PRESENTATION,
        "readiness_checkpoint_file_sha256": READINESS,
        "checkpoint_file_sha256": SAFE_STOP,
        "jz_invocation_readiness_file_sha256": JZ_READINESS,
        "kb_namespace_preflight_file_sha256": KB_PREFLIGHT,
    }
    for field, path in paths.items():
        assert identities[field] == hashlib.sha256(path.read_bytes()).hexdigest()


def test_single_route_ast_p11_g48_and_index_empty() -> None:
    for path in (FM, OWNER, BINDER, MATERIALIZER):
        ast.parse(path.read_text(encoding="utf-8"))
    tree = ast.parse(FM.read_text(encoding="utf-8"))
    run_calls = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "subprocess"
        and node.func.attr == "run"
        and node.args
        and isinstance(node.args[0], ast.Name)
        and node.args[0].id == "argv"
    ]
    assert len(run_calls) == 1
    assert hashlib.sha256((ROOT / "tests/p11_da_operational_consumer_v1.py").read_bytes()).hexdigest() == (
        "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5"
    )
    report = REPORT.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    questions = (
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
    )
    assert all(report.count(question) == 1 for question in questions)
    assert subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True
    ).strip() == ""
