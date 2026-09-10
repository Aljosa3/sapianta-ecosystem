from __future__ import annotations

import ast
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[5]
KA = ROOT / (
    ".github/governance/evidence/"
    "g77_256ka_fresh_expired_operational_recommissioning_v1"
)
REDUCTION = KA / "G77_256KA_PREHUMAN_PHASE_A_REDUCTION_V1.json"
READINESS = KA / "G77_256KA_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json"
SAFE_STOP = KA / "G77_256KA_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
REQUEST = KA / "G77_256KA_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
PRESENTATION = KA / "G77_256KA_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
JZ_READINESS = KA / "G77_256KA_JZ_PRECONSUMPTION_INVOCATION_READINESS_V1.json"
BINDER = KA / "orchestration/G77_256KA_POSTHUMAN_INVOCATION_BINDER_V1.py"
MATERIALIZER = KA / "orchestration/G77_256KA_PREAUTHORIZATION_MATERIALIZER_V1.py"
REPORT = KA / "G77_256KA_G48_IMPLEMENTATION_REPORT_V1.md"
FM = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
GN = ROOT / (
    ".github/governance/evidence/"
    "g77_256gn_human_authorization_presentation_binding_v1/presentation/"
    "G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
)

HEAD = "128bb145969a7b9ccebb8812b24216e00c7db04c"
TREE = "47d09bc1d2ecf0529601ba65085651d01c325a7c"
TERMINAL = "A__FRESH_KA_EXPIRED_PREAUTHORIZATION_PRESENTATION_READY_FOR_HUMAN_DECISION"
GENERATION = "G77_256KA_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256KA_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"
JR_HEAD = "304b342e26e92f226afa01db4b4203acfa51f532"
JR_TREE = "fc0c50e4dd79e900d85d48c5c0aeb53fe9d0c937"


def load_module(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


GN_MODULE = load_module(GN, "g77_256ka_test_gn")
BINDER_MODULE = load_module(BINDER, "g77_256ka_test_binder")


def canonical_bytes(value) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


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
    assert entry["subject"] == "G77-256JZ verify FM authority digest preconsumption binding"
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
    assert reduction["ccwim"]["cross_account_recovery"] == "VERIFIED__YES"
    assert reduction["ccwim"]["cross_account_recovery_source"] == "AUTHENTICATED_REPOSITORY_ONLY"


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
    stable = reduction["jx_reconstruction"]["stable_checkout"]
    assert stable == {"head": JR_HEAD, "tree": JR_TREE}
    assert (entry := reduction["entry"])["head"] != stable["head"]
    assert entry["tree"] != stable["tree"]


def test_jz_route_is_bound_without_fabricating_authority() -> None:
    proof = sealed(JZ_READINESS, "proof")
    assert proof["future_execution_authority_state"] == "ABSENT__EXPLICIT_HUMAN_ACT_NOT_YET_SUPPLIED"
    assert proof["authority_digest_slot"] == "UNMATERIALIZED__DERIVE_FROM_EXACT_CANONICAL_HANDOFF_BYTES_POST_HUMAN"
    assert proof["final_fm_argv_state"] == "NOT_MATERIALIZED__NO_HUMAN_AUTHORITY_EXISTS"
    assert proof["digest_equality_phase_a_status"] == "NOT_APPLICABLE__NO_FRESH_HUMAN_AUTHORITY_DIGEST_EXISTS"
    assert proof["caller_digest_input_count"] == 0
    assert proof["provider_digest_input_count"] == 0
    assert proof["authority_consumption_count"] == 0
    assert proof["fm_operational_invocation_count"] == 0
    assert proof["process_started"] is False
    assert not (ROOT / proof["future_execution_authority_path"]).exists()
    parameters = inspect.signature(BINDER_MODULE.bind_posthuman_invocation).parameters
    assert list(parameters) == ["operation_context", "live_candidate_binding", "execution_authority"]
    assert "digest" not in parameters
    binder_source = BINDER.read_text(encoding="utf-8")
    assert "FM.build_preconsumption_invocation_binding" in binder_source
    assert "FM.validate_preconsumption_invocation_binding" in binder_source
    assert "subprocess.run" not in binder_source


def test_gn_request_presentation_and_requested_semantics_are_exact() -> None:
    request = sealed(REQUEST, "request")
    assert request["request_class"] == "NON_AUTHORITY__ONE_EXPLICIT_HUMAN_DECISION_REQUIRED"
    assert request["generation_identity"] == GENERATION
    assert request["operation_identity"] == OPERATION
    assert request["authorized_vector_requested"] == "EXPIRED"
    assert request["request_is_authority"] is False
    assert request["checkpoint_is_authority"] is False
    assert request["auto_continuable"] is False
    assert request["human_review_required"] is True
    semantics = request["requested_authority_semantics"]
    for field in (
        "explicit", "fresh", "one_shot", "generation_bound", "operation_bound",
        "head_bound", "tree_bound", "candidate_bound", "context_bound",
        "canonical_argv_bound", "checkpoint_bound", "authorization_request_bound",
    ):
        assert semantics[field] is True
    assert semantics["reusable"] is False
    assert semantics["transferable"] is False
    assert semantics["network_authorized"] is False
    assert semantics["retry_limit"] == semantics["repair_limit"] == semantics["replay_limit"] == 0
    assert GN_MODULE.render_human_authorization_presentation(REQUEST) == PRESENTATION.read_bytes()
    result = GN_MODULE.validate_human_authorization_presentation(REQUEST, PRESENTATION.read_bytes())
    assert result["human_presentation_request_equivalence"] == "VERIFIED_WITHIN_EXACT_REVIEWED_AUTHORIZATION_BINDING_BOUNDARY"


def test_zero_counters_e05_ex_and_architecture() -> None:
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
    assert reduction["e05_frontier_authentication"]["remaining_set"] == [
        "AMBIGUOUS", "STALE", "EXPIRED", "REVOKED", "SUPERSEDED",
        "WRONG_SCOPE", "COHERENT_COPY",
    ]
    assert reduction["e05_frontier_authentication"]["selected_vector"] == "EXPIRED"
    assert reduction["architecture"] == {
        "new_constitutional_concept_count": 0,
        "new_generic_abstraction_count": 0,
        "new_owner_count": 0,
        "new_registry_count": 0,
        "new_route_count": 0,
        "p11_implementation_mutation_count": 0,
        "production_mutation_count": 0,
        "production_route_after": 1,
        "production_route_before": 1,
        "production_route_delta": 0,
    }
    assert reduction["terminal"] == TERMINAL
    assert reduction["auto_continuable"] is False
    assert reduction["human_review_required"] is True
    for forbidden in (
        "G77_256KA_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt",
        "G77_256KA_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
        "G77_256KA_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json",
    ):
        assert not (KA / forbidden).exists()


def test_all_json_is_canonical_all_inner_seals_and_identity_chain_hold() -> None:
    for path in KA.rglob("*.json"):
        envelope = canonical(path)
        for key, value in envelope.items():
            if key.endswith("_sha256"):
                inner = key[:-7]
                if inner in envelope and isinstance(envelope[inner], dict):
                    assert value == hashlib.sha256(canonical_bytes(envelope[inner])).hexdigest()
    reduction = sealed(REDUCTION, "reduction")
    identities = reduction["identities"]
    assert identities["request_file_sha256"] == hashlib.sha256(REQUEST.read_bytes()).hexdigest()
    assert identities["presentation_sha256"] == hashlib.sha256(PRESENTATION.read_bytes()).hexdigest()
    assert identities["readiness_checkpoint_file_sha256"] == hashlib.sha256(READINESS.read_bytes()).hexdigest()
    assert identities["checkpoint_file_sha256"] == hashlib.sha256(SAFE_STOP.read_bytes()).hexdigest()
    assert identities["jz_invocation_readiness_file_sha256"] == hashlib.sha256(JZ_READINESS.read_bytes()).hexdigest()


def test_single_route_python_ast_g48_and_index_empty() -> None:
    ast.parse(FM.read_text(encoding="utf-8"))
    ast.parse(BINDER.read_text(encoding="utf-8"))
    ast.parse(MATERIALIZER.read_text(encoding="utf-8"))
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
    report = REPORT.read_text(encoding="utf-8")
    identities = sealed(REDUCTION, "reduction")["identities"]
    for field in (
        "candidate_sha256", "context_sha256", "context_file_sha256",
        "canonical_argv_sha256", "request_sha256", "request_file_sha256",
        "presentation_sha256", "readiness_checkpoint_sha256",
        "readiness_checkpoint_file_sha256", "checkpoint_sha256",
        "checkpoint_file_sha256", "expired_adapter_sha256",
        "temporal_binding_sha256", "jz_invocation_readiness_sha256",
    ):
        assert identities[field] in report
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
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
        assert report.count(question) == 1
    assert subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True).strip() == ""
