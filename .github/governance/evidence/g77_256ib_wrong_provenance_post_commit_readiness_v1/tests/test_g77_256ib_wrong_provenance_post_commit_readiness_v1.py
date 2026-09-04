#!/usr/bin/env python3
"""Focused repository-only proof for G77-256IB."""

from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
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
IB = ROOT / (
    ".github/governance/evidence/"
    "g77_256ib_wrong_provenance_post_commit_readiness_v1"
)
BINDER_PATH = IB / "binding/G77_256IB_POST_IA_LIVE_BINDING_V1.py"
LIVE = IB / "live_binding"
CANDIDATE = LIVE / "candidate/G77_256IB_WRONG_PROVENANCE_CURRENT_CANDIDATE_V1.json"
RUNTIME = LIVE / "runtime_projection/G77_256IB_WRONG_PROVENANCE_CURRENT_CANDIDATE_V1.json"
CONTEXT = LIVE / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
EB_RECEIPT = LIVE / "bindings/G77_256IB_EB_RECEIPT_V1.json"
EE_RECEIPT = LIVE / "bindings/G77_256IB_EE_RECEIPT_V1.json"
TERMINAL = IB / "G77_256IB_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = IB / "G77_256IB_G48_IMPLEMENTATION_REPORT_V1.md"
HP_REQUEST = ROOT / (
    ".github/governance/evidence/g77_256hp_wrong_input_operational_v1/"
    "G77_256HP_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
)


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


BINDER = load_module(BINDER_PATH, "g77_256ib_test_binder")
LAUNCHER = load_module(ROOT / BINDER.FM_LAUNCHER, "g77_256ib_test_launcher")


def rejects(call) -> bool:
    try:
        call()
    except Exception:
        return True
    return False


def archive_ia_checkout(destination: Path) -> Path:
    paths = (
        BINDER.FM_CONTEXT,
        BINDER.ADAPTER,
        BINDER.HZ_SPEC,
        BINDER.HZ_PRODUCER,
        BINDER.HZ_REDUCER,
        BINDER.P11_OWNER,
        Path("tests/p11_da_disposable_substrate_v1.py"),
        Path(
            ".github/governance/evidence/g77_256fc_wrong_attempt_operational_v1/"
            "harness/G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
        ),
        Path(
            ".github/governance/evidence/g77_256hx_wrong_contract_operational_v1/"
            "operation_state/runtime_export/G77_256HX_RAW_EXECUTION_EVIDENCE_V1.jsonl"
        ),
    )
    archive = subprocess.check_output(
        ["git", "archive", "--format=tar", BINDER.IA_HEAD, "--", *(p.as_posix() for p in paths)],
        cwd=ROOT,
    )
    destination.mkdir(parents=True)
    with tarfile.open(fileobj=BytesIO(archive), mode="r:") as value:
        for member in value.getmembers():
            assert not member.name.startswith("/") and ".." not in Path(member.name).parts
        value.extractall(destination, filter="data")
    return destination


def test_exact_ia_checkpoint_remote_ancestry_and_nested_authority() -> None:
    observed = BINDER.authenticate_entry(ROOT)
    assert observed["head"] == BINDER.IA_HEAD
    assert observed["tree"] == BINDER.IA_TREE
    assert observed["subject"] == BINDER.IA_SUBJECT
    assert observed["remote_tracking_head"] == BINDER.IA_HEAD
    assert observed["index"] == ""
    assert observed["nested"]["head"] == BINDER.NESTED_HEAD
    assert observed["nested"]["tree"] == BINDER.NESTED_TREE
    assert observed["nested"]["branch"] == observed["nested"]["status"] == ""


def test_committed_ia_hz_identity_map_and_terminal_claims() -> None:
    identities = BINDER.committed_identity_map(ROOT)
    assert set(identities) == set(BINDER.COMMITTED_IA_PATHS)
    assert all(item["committed_identity_status"] == "VERIFIED" for item in identities.values())
    reduction = BINDER.reconstruct_ia_terminal(ROOT)
    assert reduction["route_extension"]["production_route_before"] == 1
    assert reduction["route_extension"]["production_route_after"] == 1
    assert reduction["route_extension"]["production_route_delta"] == 0
    assert reduction["readiness_reduction"]["wrong_provenance_route_support"] == "VERIFIED"
    assert reduction["readiness_reduction"]["wrong_provenance_binding_status"] == (
        "VERIFIED__REPOSITORY_STATIC_BINDING_ONLY"
    )
    assert reduction["e05"] == {
        "after": "9/18", "before": "9/18", "credit": 0,
        "remaining": 9, "required": 18, "satisfied": 9,
    }


def test_checkout_bootstrap_nocloud_and_hash_bindings_are_current_ia() -> None:
    result = BINDER.verify_checkout_bootstrap(ROOT)
    assert result["checkout_head"] == BINDER.IA_HEAD
    assert result["checkout_tree"] == BINDER.IA_TREE
    assert result["checkout_bootstrap_coherence_status"] == "VERIFIED"
    assert result["nocloud_projection_status"] == "VERIFIED"
    assert result["expected_harness_sha256"] == BINDER.ADAPTER_SHA256
    assert LAUNCHER.CHECKOUT_HEAD == BINDER.IA_HEAD
    assert LAUNCHER.CHECKOUT_TREE == BINDER.IA_TREE


def test_ia_checkout_contains_route_assets_and_exact_hz_semantics(tmp_path: Path) -> None:
    checkout = archive_ia_checkout(tmp_path / "checkout")
    adapter = load_module(checkout / BINDER.ADAPTER, "g77_256ib_guest_adapter")
    payload = adapter.construct_wrong_provenance_payload(
        repository_root=checkout,
        wrong_provenance_identity=BINDER.WRONG_PROVENANCE_IDENTITY,
        request_identity="G77_256IB_REPOSITORY_ONLY_FIXTURE_001",
    )
    binding = payload["semantic_binding"]
    assert binding["independent_mutated_coordinate"] == "provenance_identity"
    assert binding["independent_mutation_count"] == 1
    assert binding["dependent_recomputed_coordinate"] == "record_identity"
    assert binding["dependent_recomputation_count"] == 1
    assert binding["differing_input_fields"] == ["provenance_identity", "record_identity"]
    assert binding["expected_error_reason"] == (
        "operational Human act input_record_identity binding is invalid"
    )
    assert binding["provenance_specific_comparison_reached"] is False
    assert payload["request_is_authority"] is False
    assert payload["adapter_invoked_p11"] is False


def test_candidate_runtime_context_presentation_and_du_eb_ee() -> None:
    candidate = BINDER.load_canonical(CANDIDATE)
    assert BINDER.canonical_bytes(BINDER.build_candidate(ROOT)) == CANDIDATE.read_bytes()
    assert CANDIDATE.read_bytes() == RUNTIME.read_bytes()
    assert candidate["manifest"]["required_head"] == BINDER.IA_HEAD
    assert candidate["manifest"]["source_tree"] == BINDER.IA_TREE
    assert candidate["manifest"]["selected_case"] == {
        "case_class": BINDER.CASE_CLASS, "case_id": BINDER.CASE_ID,
    }
    context = BINDER.load_canonical(CONTEXT)
    BINDER.validate_context(ROOT, context, CANDIDATE)
    presentation = BINDER.validate_presentation_binding(
        ROOT, CANDIDATE.read_bytes(), context
    )
    assert presentation["presentation_binding_status"] == "VERIFIED"
    assert presentation["presentation_is_human_authorization"] is False
    du = load_module(ROOT / BINDER.DU_OWNER, "g77_256ib_test_du")
    eb = load_module(ROOT / BINDER.EB_OWNER, "g77_256ib_test_eb")
    ee = load_module(ROOT / BINDER.EE_OWNER, "g77_256ib_test_ee")
    assert set(du.validate_file(CANDIDATE, ROOT, expected_head=BINDER.IA_HEAD).values()) == {"PASS"}
    assert eb.verify_receipt_file(ROOT, EB_RECEIPT)["overall_result"] == "PASS"
    assert ee.verify_receipt_file(ROOT, EE_RECEIPT)["pre_materialization_runtime_path_binding_result"] == "PASS"


def test_gn_deterministically_renders_exact_current_chain(tmp_path: Path) -> None:
    gn = load_module(ROOT / BINDER.GN_OWNER, "g77_256ib_test_gn_current")
    envelope = json.loads(HP_REQUEST.read_bytes())
    request = envelope["request"]
    context = BINDER.load_canonical(CONTEXT)
    request["generation_identity"] = BINDER.GENERATION
    request["operation_identity"] = BINDER.OPERATION_IDENTITY
    request["authorized_vector_requested"] = BINDER.VECTOR
    request["repository"].update({
        "head": BINDER.IA_HEAD,
        "tree": BINDER.IA_TREE,
        "remote_head": BINDER.IA_HEAD,
    })
    request["live_binding"].update({
        "candidate_sha256": BINDER.sha256_path(CANDIDATE),
        "context_sha256": context["context_sha256"],
        "context_file_sha256": BINDER.sha256_path(CONTEXT),
        "canonical_argv_sha256": context["canonical_argv_sha256"],
        "du": "PASS", "eb": "PASS", "ee": "PASS",
        "candidate_semantics_changed": False,
        "candidate_binding_regeneration_required": False,
        "receipt_parent": str(LIVE / "bindings"),
    })
    envelope["request_sha256"] = hashlib.sha256(
        gn._canonical_bytes(request)
    ).hexdigest()
    path = tmp_path / "NON_AUTHORITY_CURRENT_PRESENTATION_FIXTURE.json"
    path.write_bytes(gn._canonical_bytes(envelope))
    presentation = gn.render_human_authorization_presentation(path)
    result = gn.validate_human_authorization_presentation(path, presentation)
    assert f'HEAD "{BINDER.IA_HEAD}"'.encode() in presentation
    assert f'TREE "{BINDER.IA_TREE}"'.encode() in presentation
    assert f'CANDIDATE_SHA256 "{BINDER.sha256_path(CANDIDATE)}"'.encode() in presentation
    assert f'CONTEXT_SHA256 "{context["context_sha256"]}"'.encode() in presentation
    assert f'CANONICAL_ARGV_SHA256 "{context["canonical_argv_sha256"]}"'.encode() in presentation
    assert b'AUTHORIZED_VECTOR_REQUESTED "WRONG_PROVENANCE"' in presentation
    assert result["human_constitutional_authorization_count"] == 0


@pytest.mark.parametrize(
    "field",
    (
        "vector", "candidate", "operation_context", "adapter",
        "checkout_head", "checkout_tree", "cloud_init", "nocloud_projection",
        "canonical_argv", "presentation_binding", "ia_head", "ia_tree",
        "hz_producer", "hz_reducer", "provenance_owner", "fm_launcher",
        "fm_context_owner", "runtime_projection", "context_candidate",
        "du", "eb", "ee",
    ),
)
def test_preauthorization_negative_matrix_rejects_wrong_binding(field: str) -> None:
    chain = deepcopy(BINDER.current_chain(ROOT, LIVE))
    chain[field] = "MALFORMED_STALE_MISSING_OR_CONFLICTING"
    assert rejects(lambda: BINDER.validate_chain(ROOT, LIVE, chain))


@pytest.mark.parametrize("vector", ("WRONG_ATTEMPT", "WRONG_INPUT", "WRONG_CONTRACT", "UNKNOWN", "wrong_provenance", ""))
def test_wrong_unknown_malformed_and_cross_vector_substitution_reject(vector: str) -> None:
    chain = deepcopy(BINDER.current_chain(ROOT, LIVE))
    chain["vector"] = vector
    assert rejects(lambda: BINDER.validate_chain(ROOT, LIVE, chain))


def test_stale_ht_and_conflicting_provenance_owner_fail_closed() -> None:
    for field, stale in (
        ("checkout_head", BINDER.HT_HEAD),
        ("checkout_tree", BINDER.HT_TREE),
        ("provenance_owner", ""),
        ("provenance_owner", "CONFLICTING_PROTECTED_OWNER"),
    ):
        chain = deepcopy(BINDER.current_chain(ROOT, LIVE))
        chain[field] = stale
        assert rejects(lambda chain=chain: BINDER.validate_chain(ROOT, LIVE, chain))


def test_historical_failure_class_firewall_and_four_vector_nonregression() -> None:
    chain = BINDER.current_chain(ROOT, LIVE)
    BINDER.validate_chain(ROOT, LIVE, chain)
    candidate = BINDER.load_canonical(CANDIDATE)
    context = BINDER.load_canonical(CONTEXT)
    assert candidate["manifest"]["required_head"] == BINDER.IA_HEAD
    assert candidate["manifest"]["required_head"] != "FUTURE_IB_COMMIT"
    assert chain["checkout_head"] != BINDER.HT_HEAD
    assert chain["checkout_tree"] != BINDER.HT_TREE
    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    assert Path(checkout["path"]) == Path(context["transient_root"]) / "checkout"
    assert LAUNCHER.fresh_context.checkout_lifecycle_binding(context) == (
        LAUNCHER.fresh_context.OPERATION_SCOPED_CHECKOUT_LIFECYCLE
    )
    for vector in BINDER.SUPPORTED_VECTORS:
        assert LAUNCHER.fresh_context.operation_vector(BINDER.generation(vector)) == vector
        assert LAUNCHER.current_bootstrap_asset_bindings(vector)


def test_one_production_route_ex_reuse_and_no_operational_entrypoint() -> None:
    assert BINDER.authenticate_ex(ROOT) == {
        "ex_reused": "17/17", "ex_reconstructed": 0, "status": "VERIFIED",
    }
    launcher_tree = ast.parse((ROOT / BINDER.FM_LAUNCHER).read_text(encoding="utf-8"))
    assert sum(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "main"
        for node in launcher_tree.body
    ) == 1
    binder_source = BINDER_PATH.read_text(encoding="utf-8")
    binder_tree = ast.parse(binder_source)
    assert not any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "main"
        for node in ast.walk(binder_tree)
    )
    prohibited = (
        "subprocess.Popen", "run_qemu_once(", "launch_once(", "invoke_pre(",
        "request_authority(", "consume_authority(", "CLAIM_AND_INVOKE_ONCE",
    )
    assert not any(token in binder_source for token in prohibited)
    assert list(IB.rglob("*LAUNCHER*.py")) == []


def test_terminal_reduction_canonical_sealed_and_zero_operation() -> None:
    envelope = BINDER.load_canonical(TERMINAL)
    assert envelope["reduction_sha256"] == BINDER.sha256_bytes(
        BINDER.canonical_bytes(envelope["reduction"])
    )
    reduction = envelope["reduction"]
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"] == {
        "before": "9/18", "after": "9/18", "credit": 0,
        "required": 18, "satisfied": 9, "remaining": 9,
    }
    assert reduction["readiness"]["preoperational_readiness_status"] == "VERIFIED"
    assert reduction["readiness"]["next_operational_generation_eligible"] == "VERIFIED"
    assert reduction["readiness"]["wrong_provenance_operational_capability"] == "NOT_PROVEN"
    assert reduction["terminal_control"]["auto_continuable"] is False
    assert reduction["terminal_control"]["human_authorization_required"] is False
    assert reduction["terminal_control"]["human_review_required"] is True


def test_g48_report_has_exactly_six_top_level_headings() -> None:
    report = REPORT.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    required = (
        "CURRENT_IA_COMMIT_IDENTITY_STATUS = VERIFIED",
        "POST_COMMIT_LIVE_BINDING_STATUS = VERIFIED",
        "CURRENT_DU_STATUS = PASS", "CURRENT_EB_STATUS = PASS",
        "CURRENT_EE_STATUS = PASS",
        "PREOPERATIONAL_READINESS_STATUS = VERIFIED",
        "NEXT_OPERATIONAL_GENERATION_ELIGIBLE = VERIFIED",
        "WRONG_PROVENANCE_OPERATIONAL_CAPABILITY = NOT_PROVEN",
        "E05_AFTER_IB = 9/18", "AUTO_CONTINUABLE = NO",
        "HUMAN_AUTHORIZATION_REQUIRED = NO", "HUMAN_REVIEW_REQUIRED = YES",
    )
    assert all(token in report for token in required)
