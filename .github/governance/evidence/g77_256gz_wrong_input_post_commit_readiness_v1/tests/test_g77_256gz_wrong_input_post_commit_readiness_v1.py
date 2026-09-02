#!/usr/bin/env python3
"""Focused repository-only GZ post-commit binding/readiness proofs."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
GZ = ROOT / ".github/governance/evidence/g77_256gz_wrong_input_post_commit_readiness_v1"
GY = ROOT / ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1"
LIVE = GZ / "live_binding"
CANDIDATE = LIVE / "candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
RUNTIME = LIVE / "runtime_projection/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
EB_RECEIPT = LIVE / "bindings/G77_256GY_EB_RECEIPT_V1.json"
EE_RECEIPT = LIVE / "bindings/G77_256GY_EE_RECEIPT_V1.json"
CHECKPOINT = GZ / "G77_256GZ_POST_COMMIT_BINDING_AND_READINESS_CHECKPOINT_V1.json"
NEXT_SPEC = GZ / "G77_256GZ_NEXT_DEVELOPMENT_SPECIFICATION_V1.json"
TERMINAL = GZ / "G77_256GZ_SPCE_TERMINAL_REDUCTION_V1.json"
REPORT = ROOT / "docs/governance/G77_256GZ_POST_GY_WRONG_INPUT_LIVE_BINDING_READINESS_V1.md"
BINDER_PATH = GY / "binding/G77_256GY_WRONG_INPUT_POST_COMMIT_BINDING_V1.py"
DU_PATH = ROOT / (
    ".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/"
    "validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V1.py"
)
EB_PATH = ROOT / (
    ".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1/"
    "validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V1.py"
)
EE_PATH = ROOT / (
    ".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1/"
    "validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V1.py"
)
GN_PATH = ROOT / (
    ".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/"
    "presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
)
FM_PATH = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
P11_PATH = ROOT / "tests/p11_da_operational_consumer_v1.py"
GW_PATH = ROOT / (
    ".github/governance/evidence/g77_256gw_host_checkpoint_serialization_boundary_v1/"
    "G77_256GW_FUTURE_HOST_CHECKPOINT_OWNER_BINDING_V1.md"
)
EXPECTED_HEAD = "2b6f904ca93c980f6c6078333cdf61c49fa54e87"
EXPECTED_TREE = "09e68a5bb4e6c7fda4aeab73d0fccf2f24d3ff52"
EXPECTED_GY_HASHES = {
    GY / "G77_256GY_WRONG_INPUT_FORMAL_SPECIFICATION_V1.json": "b9c153963f9042642c28cb748547ee2aef3dbb87dedc583ad9703cbc135bb50b",
    GY / "producer/G77_256GY_WRONG_INPUT_REQUEST_AND_CANDIDATE_PRODUCER_V1.py": "643de4aa38264410c445107dfdd71b02334871021dd0b7d5ef8886a62e80cd22",
    GY / "candidate/G77_256GY_WRONG_INPUT_CANONICAL_CANDIDATE_TEMPLATE_V1.json": "26fa2f3a4ea4c4683c2ccde4288a39760b89c8d0329eca01502425941c03b041",
    GY / "reducer/G77_256GY_WRONG_INPUT_TERMINAL_ACCEPTANCE_REDUCER_V1.py": "8a6e6081118a2c1d305260555ba1ad5a11d97a5d66516f9810beb87c5c39fbf7",
    BINDER_PATH: "bc4f4d9c4a9492a9e0d83b2b837b4e722d985f813cb9d365f7b6b9183c3b5c00",
    GY / "G77_256GY_SPCE_TERMINAL_REDUCTION_V1.json": "2ea71df7b670a44a24786720464752f536c85703765f25901d778ddce405d9b4",
}


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise AssertionError(f"DUPLICATE_JSON_KEY__{key}")
        value[key] = item
    return value


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_bytes(), object_pairs_hook=reject_duplicate_pairs)
    assert isinstance(value, dict)
    return value


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


BINDER = load_module(BINDER_PATH, "g77_256gz_binder_test")
DU = load_module(DU_PATH, "g77_256gz_du_test")
EB = load_module(EB_PATH, "g77_256gz_eb_test")
EE = load_module(EE_PATH, "g77_256gz_ee_test")


def assert_sealed(path: Path, inner: str, seal: str) -> dict[str, Any]:
    envelope = load_json(path)
    assert path.read_bytes() == canonical_bytes(envelope)
    assert hashlib.sha256(canonical_bytes(envelope[inner])).hexdigest() == envelope[seal]
    return envelope


def test_exact_committed_and_pushed_gy_entry() -> None:
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() == EXPECTED_HEAD
    assert subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True).strip() == EXPECTED_TREE
    assert subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip() == "g77-256fl-wrong-attempt-preboot-blocker"
    assert subprocess.check_output(["git", "log", "-1", "--format=%s"], cwd=ROOT, text=True).strip() == "G77-256GY formalize WRONG_INPUT repository capability"
    assert subprocess.check_output(["git", "rev-parse", "origin/g77-256fl-wrong-attempt-preboot-blocker"], cwd=ROOT, text=True).strip() == EXPECTED_HEAD
    assert subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True).strip() == ""
    assert subprocess.run(["git", "merge-base", "--is-ancestor", "d9a243a0e47decf02f4f1fce7ade627bafc42e61", "HEAD"], cwd=ROOT).returncode == 0
    assert subprocess.run(["git", "merge-base", "--is-ancestor", "5c972e9960987ab27420395b54ace693df097e7b", "HEAD"], cwd=ROOT).returncode == 0
    nested = ROOT / "sapianta_system"
    assert subprocess.check_output(["git", "status", "--porcelain=v1"], cwd=nested, text=True).strip() == ""
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=nested, text=True).strip() == "3183bab71f8f30397c0309dd2e6d846d14a11f66"
    assert subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=nested, text=True).strip() == "7c32ec05efc2be43297849bc38ec8766514a523d"
    assert subprocess.run(["git", "symbolic-ref", "-q", "HEAD"], cwd=nested).returncode != 0


def test_committed_gy_artifact_hashes_and_semantics_authenticate() -> None:
    for path, expected in EXPECTED_GY_HASHES.items():
        assert sha256_path(path) == expected
    formal = assert_sealed(
        GY / "G77_256GY_WRONG_INPUT_FORMAL_SPECIFICATION_V1.json",
        "specification",
        "specification_sha256",
    )["specification"]
    assert formal["target_e05_obligation"].endswith("/WRONG_INPUT")
    assert formal["mutation_rule"]["target_mutated_coordinate"] == "input_identity"
    assert formal["mutation_rule"]["dependent_recomputations"] == ["record_identity"]
    assert formal["mutation_rule"]["semantic_mutation_count"] == 1
    assert formal["mutation_rule"]["dependent_recomputation_is_second_semantic_mutation"] is False


def test_live_candidate_is_exact_head_tree_semantic_rebinding() -> None:
    candidate = load_json(CANDIDATE)
    template = BINDER.authenticate_template(ROOT)
    assert CANDIDATE.read_bytes() == canonical_bytes(candidate) == RUNTIME.read_bytes()
    assert sha256_path(CANDIDATE) == "ab94e3f000a43da75fe7f4791bf38a13b0babed7673f4e21ff248c27df353ee9"
    assert candidate["manifest"]["required_head"] == EXPECTED_HEAD
    assert candidate["manifest"]["source_tree"] == EXPECTED_TREE
    assert candidate["manifest"]["selected_case"]["case_class"] == "E05_NEGATIVE_AUTHORITY_WRONG_INPUT"
    assert BINDER.semantic_sha256(candidate) == BINDER.semantic_sha256(template) == BINDER.TEMPLATE_SEMANTIC_SHA256
    assert BINDER.build_post_commit_candidate(ROOT) == candidate
    changed = deepcopy(candidate)
    changed["manifest"]["selected_case"]["case_class"] = "E05_NEGATIVE_AUTHORITY_WRONG_ATTEMPT"
    changed["manifest_sha256"] = BINDER.sha256_bytes(BINDER.canonical_bytes(changed["manifest"]))
    with pytest.raises(BINDER.WrongInputBindingError, match="CANDIDATE_SEMANTICS_CHANGED"):
        BINDER.validate_candidate_semantics(changed, template)


def test_du_eb_ee_reauthenticate_generated_binding() -> None:
    assert set(DU.validate_file(CANDIDATE, ROOT, expected_head=EXPECTED_HEAD).values()) == {"PASS"}
    assert EB.verify_receipt_file(ROOT, EB_RECEIPT)["overall_result"] == "PASS"
    assert EE.verify_receipt_file(ROOT, EE_RECEIPT)["pre_materialization_runtime_path_binding_result"] == "PASS"
    eb = assert_sealed(EB_RECEIPT, "receipt", "receipt_inner_sha256")["receipt"]
    ee = assert_sealed(EE_RECEIPT, "receipt", "receipt_inner_sha256")["receipt"]
    assert eb["required_head"] == ee["git_binding"]["required_head"] == EXPECTED_HEAD
    assert eb["required_tree"] == ee["git_binding"]["required_tree"] == EXPECTED_TREE


def test_gn_and_fm_are_not_yet_wrong_input_compatible() -> None:
    gn = GN_PATH.read_text(encoding="utf-8")
    fm = FM_PATH.read_text(encoding="utf-8")
    assert 'request["authorized_vector_requested"] != "WRONG_ATTEMPT"' in gn
    assert 'WRAPPER = f"{FM_ROOT}/harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"' in fm
    assert 'authorized_vector": "WRONG_ATTEMPT"' in fm
    assert "G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py" in fm
    assert not (LIVE / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json").exists()


def test_common_p11_and_gw_owners_remain_compatible_without_execution() -> None:
    p11 = P11_PATH.read_text(encoding="utf-8")
    gw = GW_PATH.read_text(encoding="utf-8")
    assert '"input_record_identity": input_record["record_identity"]' in p11
    assert '"input_payload_identity": input_record["input_identity"]' in p11
    assert '_fail(f"operational Human act {field_name} binding is invalid")' in p11
    assert "HOST_PRE_TEARDOWN" in gw and "HOST_TEARDOWN" in gw
    assert "G77_256ER_ATOMIC_CHECKPOINT_WRITER_V1.py" in gw
    assert "persist" in gw and "authenticate_path" in gw


def test_wrong_attempt_historical_paths_are_unchanged_by_gy() -> None:
    paths = (
        ".github/governance/evidence/g77_256gv_wrong_attempt_operational_v1",
        ".github/governance/evidence/g77_256gd_fresh_operation_context_v1",
        ".github/governance/evidence/g77_256gf_post_commit_live_binding_v1",
    )
    assert subprocess.check_output(
        ["git", "diff", "--name-only", "d9a243a0e47decf02f4f1fce7ade627bafc42e61..HEAD", "--", *paths],
        cwd=ROOT,
        text=True,
    ).strip() == ""


def test_binding_checkpoint_and_next_development_spec_are_sealed_branch_b() -> None:
    checkpoint = assert_sealed(CHECKPOINT, "checkpoint", "checkpoint_sha256")["checkpoint"]
    recovery = checkpoint["fresh_worker_recovery"]
    assert recovery["status"] == "VERIFIED"
    assert recovery["material_delta_count"] == 10
    assert len(recovery["authenticated_gz_delta"]) == 10
    assert len(recovery["generated_non_material_cache"]) == 1
    assert recovery["untrusted_gz_delta"] == recovery["unrelated_delta"] == []
    assert recovery["previous_worker_conversation_required"] is False
    readiness = checkpoint["readiness_reduction"]
    assert readiness["post_commit_live_binding_status"] == "VERIFIED"
    assert (readiness["du_status"], readiness["eb_status"], readiness["ee_status"]) == ("PASS", "PASS", "PASS")
    assert readiness["preoperational_readiness_status"] == "NOT_PROVEN"
    assert readiness["first_broken_edge"].startswith("WRONG_INPUT_OPERATION_CONTEXT")
    assert set(checkpoint["operational_counters"].values()) == {0}
    specification = assert_sealed(NEXT_SPEC, "specification", "specification_sha256")["specification"]
    assert specification["classification"] == "TERMINAL_BRANCH_B__NOT_READY"
    assert specification["production_route_delta_target"] == 0
    assert specification["auto_continuable"] is False
    assert specification["execution_authority"] is False


def test_gz_artifacts_do_not_contain_an_operational_entrypoint() -> None:
    harness = (LIVE / "bindings/G77_256GY_EE_PATH_PROJECTION_FIXTURE_V1.py").read_text(encoding="utf-8")
    assert "TEST_ONLY__NON_AUTHORITY__NON_OPERATIONAL__NON_EXECUTABLE" in harness
    assert "subprocess.run" not in harness
    assert "qemu-system" not in harness
    assert "claim_and_invoke_once" not in harness


def test_terminal_reduction_and_g48_report_are_sealed_and_consistent() -> None:
    reduction = assert_sealed(TERMINAL, "reduction", "reduction_sha256")["reduction"]
    assert reduction["readiness_branch"]["branch"] == "TERMINAL_BRANCH_B__NOT_READY"
    assert reduction["capability_status"]["post_commit_live_binding_status"] == "VERIFIED"
    assert reduction["capability_status"]["preoperational_readiness_status"] == "NOT_PROVEN"
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"]["before"] == reduction["e05"]["after"] == "7/18"
    assert reduction["repository_entry"]["worktree_state"] == "DIRTY__TEN_AUTHENTICATED_GZ_MATERIAL_FILES_ONLY"
    assert reduction["ccwim"]["intra_task_cross_worker_continuation"]["status"] == "VERIFIED"
    assert reduction["ccwim"]["uncommitted_delta_recovery"]["status"] == "VERIFIED"
    assert reduction["ccwim"]["cross_worker_constitutional_drift"]["status"] == "VERIFIED"
    assert reduction["ccwim"]["same_worker_provider_reset_resume"]["status"] == "NOT_APPLICABLE"
    report = REPORT.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    assert report.rstrip().endswith(reduction["terminal_control"]["verdict"])
    assert "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?" in report
    assert report.count("| PREVIOUS_WORKER_CONVERSATION_REQUIRED |") == 1
