#!/usr/bin/env python3
"""Focused authority-free validation for G77-256HW."""

from __future__ import annotations

import ast
from copy import deepcopy
import importlib.util
from io import BytesIO
import json
from pathlib import Path
import subprocess
import sys
import tarfile

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
HW = ROOT / ".github/governance/evidence/g77_256hw_post_hv_live_binding_readiness_v1"
BINDER_PATH = HW / "binding/G77_256HW_POST_HV_LIVE_BINDING_V1.py"
LIVE = HW / "live_binding"
CANDIDATE = LIVE / "candidate/G77_256HW_WRONG_CONTRACT_CURRENT_CANDIDATE_V1.json"
RUNTIME = LIVE / "runtime_projection/G77_256HW_WRONG_CONTRACT_CURRENT_CANDIDATE_V1.json"
CONTEXT = LIVE / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
EB_RECEIPT = LIVE / "bindings/G77_256HW_EB_RECEIPT_V1.json"
EE_RECEIPT = LIVE / "bindings/G77_256HW_EE_RECEIPT_V1.json"
TERMINAL = HW / "G77_256HW_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = ROOT / "docs/governance/G77_256HW_POST_HV_WRONG_CONTRACT_COMMITTED_IDENTITY_LIVE_BINDING_AND_PREOPERATIONAL_READINESS_CERTIFICATION_V1.md"


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


BINDER = load_module(BINDER_PATH, "g77_256hw_focused_binder")
LAUNCHER = load_module(ROOT / BINDER.FM_LAUNCHER, "g77_256hw_focused_launcher")


def rejects(call) -> bool:
    try:
        call()
    except Exception:
        return True
    return False


def archive_selected_checkout(destination: Path) -> Path:
    dependencies = (
        BINDER.FM_CONTEXT,
        BINDER.ADAPTER,
        BINDER.HR_PRODUCER,
        BINDER.HR_SPEC,
        Path("tests/p11_da_disposable_substrate_v1.py"),
        Path(".github/governance/evidence/g77_256fc_wrong_attempt_operational_v1/harness/G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"),
        Path(".github/governance/evidence/g77_256hp_wrong_input_operational_v1/operation_state/runtime_export/G77_256HP_RAW_EXECUTION_EVIDENCE_V1.jsonl"),
    )
    archive = subprocess.check_output(["git", "archive", "--format=tar", BINDER.HT_HEAD, "--", *(path.as_posix() for path in dependencies)], cwd=ROOT)
    destination.mkdir(parents=True)
    with tarfile.open(fileobj=BytesIO(archive), mode="r:") as value:
        for member in value.getmembers():
            assert not member.name.startswith("/") and ".." not in Path(member.name).parts
        value.extractall(destination, filter="data")
    return destination


def test_exact_hv_entry_remote_tracking_ancestry_and_nested_authority() -> None:
    observed = BINDER.authenticate_entry(ROOT)
    assert observed["head"] == BINDER.HV_HEAD
    assert observed["tree"] == BINDER.HV_TREE
    assert observed["subject"] == BINDER.HV_SUBJECT
    assert observed["remote_tracking_head"] == BINDER.HV_HEAD
    assert observed["index"] == ""
    assert observed["nested"]["head"] == BINDER.NESTED_HEAD
    assert observed["nested"]["tree"] == BINDER.NESTED_TREE
    assert observed["nested"]["branch"] == observed["nested"]["status"] == ""


def test_committed_identity_map_recomputes_git_blobs_and_sha256() -> None:
    identities = BINDER.committed_identity_map(ROOT)
    assert set(identities) == set(BINDER.IDENTITY_PATHS)
    assert all(item["committed_identity_status"] == "VERIFIED" for item in identities.values())
    for item in identities.values():
        committed = subprocess.check_output(["git", "show", f"{BINDER.HV_HEAD}:{item['path']}"], cwd=ROOT)
        assert BINDER.sha256_bytes(committed) == item["sha256"]
        assert subprocess.check_output(["git", "rev-parse", f"{BINDER.HV_HEAD}:{item['path']}"], cwd=ROOT, text=True).strip() == item["git_blob"]


def test_hv_terminal_and_hu_frontier_are_reconstructed() -> None:
    reduction = BINDER.reconstruct_hv_terminal(ROOT)
    assert reduction["hu_blocker_reconstruction"]["status"] == "VERIFIED"
    assert reduction["checkout_selection"]["selected_checkout_head"] == BINDER.HT_HEAD
    assert reduction["checkout_selection"]["selected_checkout_tree"] == BINDER.HT_TREE
    assert reduction["checkout_selection"]["selection_reason"] == "HT_IS_THE_FIRST_LINEAGE_COMMIT_WITH_WRONG_CONTRACT_FM_CONTEXT_SUPPORT_AND_CONTAINS_THE_COMPLETE_GUEST_DEPENDENCY_SET"
    assert reduction["readiness"]["post_commit_live_binding_status"] == "NOT_PROVEN"


def test_committed_checkout_bootstrap_nocloud_and_expected_harness() -> None:
    result = BINDER.verify_committed_checkout_bootstrap(ROOT)
    assert set(result.values()) == {"VERIFIED", BINDER.ADAPTER_SHA256}
    assert LAUNCHER.CHECKOUT_HEAD == BINDER.HT_HEAD
    assert LAUNCHER.CHECKOUT_TREE == BINDER.HT_TREE
    assert result["expected_harness_sha256"] == BINDER.ADAPTER_SHA256


def test_selected_checkout_host_guest_semantics_and_adapter_dependencies(tmp_path: Path) -> None:
    assert BINDER.verify_host_guest_semantics(ROOT) == {
        "host_guest_context_vector_semantic_equivalence": "VERIFIED",
        "guest_adapter_dependency_closure_status": "VERIFIED",
    }
    checkout = archive_selected_checkout(tmp_path / "guest")
    guest = load_module(checkout / BINDER.ADAPTER, "g77_256hw_guest_adapter")
    payload = guest.construct_wrong_contract_payload(repository_root=checkout, wrong_contract_identity=BINDER.WRONG_CONTRACT_IDENTITY, request_identity="G77_256HW_TEST_ONLY_REQUEST_001")
    assert payload["semantic_binding"]["target_mutated_coordinate"] == "contract_identity"
    assert payload["semantic_binding"]["dependent_recomputation_fields"] == ["record_identity"]
    assert payload["semantic_binding"]["semantic_mutation_count"] == 1
    assert payload["request_is_authority"] is False
    assert payload["adapter_invoked_p11"] is False


def test_current_candidate_semantics_runtime_context_and_du_eb_ee() -> None:
    candidate = BINDER.load_canonical(CANDIDATE)
    assert BINDER.canonical_bytes(BINDER.build_candidate(ROOT)) == CANDIDATE.read_bytes()
    assert CANDIDATE.read_bytes() == RUNTIME.read_bytes()
    assert candidate["manifest"]["required_head"] == BINDER.HV_HEAD
    assert candidate["manifest"]["source_tree"] == BINDER.HV_TREE
    assert candidate["manifest"]["selected_case"] == {"case_class": BINDER.CASE_CLASS, "case_id": BINDER.CASE_ID}
    semantics = BINDER.candidate_semantics(ROOT)
    assert semantics["differing_input_fields"] == ["contract_identity", "record_identity"]
    assert all(semantics["preserved_dimension_proof"].values())
    context = BINDER.load_canonical(CONTEXT)
    BINDER.validate_context(ROOT, context, CANDIDATE)
    assert context["candidate_manifest_sha256"] == BINDER.sha256_path(CANDIDATE)
    assert BINDER.validate_preauthorization_coherence(ROOT, CANDIDATE.read_bytes(), context)["candidate_context_argv_presentation_chain"] == "VERIFIED"
    du = load_module(ROOT / BINDER.DU_OWNER, "g77_256hw_test_du")
    eb = load_module(ROOT / BINDER.EB_OWNER, "g77_256hw_test_eb")
    ee = load_module(ROOT / BINDER.EE_OWNER, "g77_256hw_test_ee")
    assert set(du.validate_file(CANDIDATE, ROOT, expected_head=BINDER.HV_HEAD).values()) == {"PASS"}
    assert eb.verify_receipt_file(ROOT, EB_RECEIPT)["overall_result"] == "PASS"
    assert ee.verify_receipt_file(ROOT, EE_RECEIPT)["pre_materialization_runtime_path_binding_result"] == "PASS"


@pytest.mark.parametrize("field", (
    "hv_head", "hv_tree", "fm_launcher", "fm_context_owner", "adapter",
    "cloud_init", "nocloud_seed", "checkout_head", "checkout_tree", "projection",
    "candidate", "runtime_projection", "operation_context", "context_candidate",
    "gn_presentation", "du", "eb", "ee", "vector",
))
def test_negative_matrix_rejects_each_stale_or_substituted_binding(field: str) -> None:
    chain = deepcopy(BINDER.current_chain(ROOT, LIVE))
    chain[field] = "MALFORMED_OR_STALE"
    assert rejects(lambda: BINDER.validate_chain(ROOT, LIVE, chain))


@pytest.mark.parametrize("vector", ("WRONG_ATTEMPT", "WRONG_INPUT", "UNKNOWN", "MALFORMED"))
def test_cross_vector_unknown_and_malformed_substitution_reject(vector: str) -> None:
    chain = deepcopy(BINDER.current_chain(ROOT, LIVE))
    chain["vector"] = vector
    assert rejects(lambda: BINDER.validate_chain(ROOT, LIVE, chain))


def test_historical_failure_firewall_and_regressions() -> None:
    chain = BINDER.current_chain(ROOT, LIVE)
    BINDER.validate_chain(ROOT, LIVE, chain)
    assert chain["checkout_head"] != "842a0f2cccd53222d11daa698bdeab17f0aac043"
    assert chain["adapter"] == BINDER.ADAPTER_SHA256
    assert chain["cloud_init"] == BINDER.CLOUD_INIT_SHA256
    assert chain["nocloud_seed"] == BINDER.SEED_SHA256
    for vector in ("WRONG_ATTEMPT", "WRONG_INPUT", "WRONG_CONTRACT"):
        assert LAUNCHER.current_bootstrap_asset_bindings(vector)
        assert LAUNCHER.fresh_context.operation_vector(BINDER.generation(vector)) == vector


def test_ex_reused_and_no_parallel_route_or_operational_entrypoint() -> None:
    assert BINDER.authenticate_ex(ROOT) == {"ex_reused": "17/17", "ex_reconstructed": 0, "status": "VERIFIED"}
    source = BINDER_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    prohibited = ("subprocess.Popen", "run_qemu_once(", "launch_once(", "invoke_pre(", "request_authority(", "consume_authority(")
    assert not any(token in source for token in prohibited)
    assert not any(isinstance(node, ast.FunctionDef) and node.name == "main" for node in ast.walk(tree))
    assert sum(path.name == "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py" for path in ROOT.rglob("G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py")) == 1


def test_terminal_reduction_canonical_sealed_success_and_zero_operation() -> None:
    envelope = BINDER.load_canonical(TERMINAL)
    assert envelope["reduction_sha256"] == BINDER.sha256_bytes(BINDER.canonical_bytes(envelope["reduction"]))
    reduction = envelope["reduction"]
    assert reduction["readiness"] == {
        "preoperational_readiness_status": "VERIFIED",
        "next_operational_generation_eligible": "VERIFIED",
        "wrong_contract_operational_capability": "NOT_PROVEN",
    }
    assert reduction["du_eb_ee"] == {"current_du_status": "PASS", "current_eb_status": "PASS", "current_ee_status": "PASS"}
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"] == {"before": "8/18", "credit": 0, "after": "8/18"}
    assert reduction["terminal_control"]["auto_continuable"] is False
    assert reduction["terminal_control"]["human_review_required"] is True


def test_g48_report_exactly_six_headings_and_required_content() -> None:
    report = REPORT.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    required = (
        "CURRENT_HV_COMMIT_IDENTITY_STATUS = VERIFIED",
        "POST_COMMIT_LIVE_BINDING_STATUS = VERIFIED",
        "CURRENT_DU_STATUS = PASS", "CURRENT_EB_STATUS = PASS", "CURRENT_EE_STATUS = PASS",
        "PREOPERATIONAL_READINESS_STATUS = VERIFIED",
        "WRONG_CONTRACT_OPERATIONAL_CAPABILITY = NOT_PROVEN",
        "E05_AFTER_HW = 8/18", "AUTO_CONTINUABLE = NO", "HUMAN_REVIEW_REQUIRED = YES",
    )
    assert all(token in report for token in required)
