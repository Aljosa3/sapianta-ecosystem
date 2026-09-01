#!/usr/bin/env python3
"""Focused repository-only proof for the exact GT -> GF/GD GU binding."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True
REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
EXPECTED_HEAD = "49061f145736c9cdddbe7a54c5d8d3e7a5711729"
EXPECTED_TREE = "daf415fbcedf6f973097927c376406e23d7dc026"
EXPECTED_SEALS = {
    "GP": "f8948b4ecc0a07b865d06d404e830ba216b8aa4fd841e54cae18883561d3269b",
    "GQ": "2c46a847854b566d33a679ed8bfd0b3897c3dec2c586f0b3c17bb7b14e1c62a4",
    "GR": "9f1c9d04e693a57cf494ee3bd30bd6a040a2a5b13e0fd624d3cd15e5b9debbc3",
    "GS": "76b1a282d3abcd6055cb100a6279d67cb01e3e206e86b77470be5fb98ba79f51",
    "GT": "fe28c8dedaf4afb2df0d68fd45693c162a61645d83a23e2c044d9c0ce1c3c572",
    "GU": "2bbe4a255c872a4541d111d7503c032dd964a225be4bbd696ab589404665181b",
}
REDUCTIONS = {
    "GP": REPOSITORY_ROOT / ".github/governance/evidence/g77_256gp_guest_checkout_tree_precondition_v1/G77_256GP_SPCE_FINAL_REPOSITORY_ONLY_REDUCTION_V1.json",
    "GQ": REPOSITORY_ROOT / ".github/governance/evidence/g77_256gq_guest_self_contained_checkout_v1/G77_256GQ_SPCE_FINAL_REPOSITORY_ONLY_REDUCTION_V1.json",
    "GR": REPOSITORY_ROOT / ".github/governance/evidence/g77_256gr_post_commit_live_binding_readiness_v1/G77_256GR_SPCE_FINAL_REPOSITORY_ONLY_REDUCTION_V1.json",
    "GS": REPOSITORY_ROOT / ".github/governance/evidence/g77_256gs_wrong_attempt_operational_v1/G77_256GS_SPCE_FINAL_FAIL_CLOSED_REDUCTION_V1.json",
    "GT": REPOSITORY_ROOT / ".github/governance/evidence/g77_256gt_checkout_lifecycle_correction_v1/G77_256GT_SPCE_FINAL_REPOSITORY_ONLY_REDUCTION_V1.json",
    "GU": REPOSITORY_ROOT / ".github/governance/evidence/g77_256gu_post_commit_live_binding_readiness_v1/G77_256GU_SPCE_FINAL_REPOSITORY_ONLY_REDUCTION_V1.json",
}
EVIDENCE_ROOT = REPOSITORY_ROOT / ".github/governance/evidence/g77_256gu_post_commit_live_binding_readiness_v1"
LIVE_ROOT = EVIDENCE_ROOT / "live_binding"
CANDIDATE = LIVE_ROOT / "candidate/G77_256GU_CONTINUATION_MANIFEST_V1.json"
RUNTIME_CANDIDATE = LIVE_ROOT / "ee_runtime_projection/G77_256GU_CONTINUATION_MANIFEST_V1.json"
CONTEXT = LIVE_ROOT / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
EB_RECEIPT = LIVE_ROOT / "bindings/CANDIDATE_BOUND_EB_RECEIPT_V1.json"
EE_RECEIPT = LIVE_ROOT / "bindings/RUNTIME_CONSUMER_EE_RECEIPT_V1.json"
GF_PATH = REPOSITORY_ROOT / ".github/governance/evidence/g77_256gf_post_commit_live_binding_v1/binding/G77_256GF_POST_COMMIT_LIVE_EXECUTION_BINDING_V1.py"


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


GF = load_module(GF_PATH, "g77_256gu_existing_gf_owner")


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"DUPLICATE_JSON_KEY__{key}")
        result[key] = value
    return result


def load_unique(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def reduction_seal(path: Path) -> tuple[str, str]:
    envelope = load_unique(path)
    canonical = (
        json.dumps(
            envelope["reduction"],
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    return envelope["reduction_sha256"], hashlib.sha256(canonical).hexdigest()


def test_gp_through_gu_sealed_lineage_and_exact_properties_are_preserved():
    for identity, path in REDUCTIONS.items():
        assert reduction_seal(path) == (EXPECTED_SEALS[identity], EXPECTED_SEALS[identity])

    gt = load_unique(REDUCTIONS["GT"])["reduction"]
    assert gt["cross_worker_recovery"]["previous_worker_candidate_hypothesis"] == "CONFIRMED"
    assert gt["root_cause"]["historical_checkout"] == "/tmp/g77_256fm/checkout"
    assert gt["minimum_correction"]["new_context_checkout_binding"] == "transient_root/checkout"
    assert gt["minimum_correction"]["historical_replay_preserved"] is True
    assert gt["minimum_correction"]["post_commit_live_binding_regeneration_required"] is True
    assert gt["ex"]["reused"] == "17/17"
    assert gt["e05"]["after"] == "6/18"


def test_exact_gt_identity_is_bound_through_existing_gf_gd_du_eb_ee_owners():
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPOSITORY_ROOT, text=True).strip() == EXPECTED_HEAD
    assert subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=REPOSITORY_ROOT, text=True).strip() == EXPECTED_TREE

    template = GF.authenticate_certified_template(REPOSITORY_ROOT)
    candidate = load_unique(CANDIDATE)
    context = load_unique(CONTEXT)
    assert candidate["manifest"]["required_head"] == EXPECTED_HEAD
    assert candidate["manifest"]["source_tree"] == EXPECTED_TREE
    assert GF.semantic_sha256(candidate) == GF.semantic_sha256(template)
    assert CANDIDATE.read_bytes() == RUNTIME_CANDIDATE.read_bytes()
    assert context["repository_head"] == EXPECTED_HEAD
    assert context["repository_tree"] == EXPECTED_TREE
    assert context["candidate_manifest_sha256"] == GF.sha256_path(CANDIDATE)

    launcher = load_module(REPOSITORY_ROOT / GF.LAUNCHER_PATH, "g77_256gu_existing_fm_owner")
    assert launcher.fresh_context.load_context(CONTEXT, repository_root=REPOSITORY_ROOT) == context
    launcher.validate_immutable_context_bindings(
        REPOSITORY_ROOT,
        context,
        candidate_source_path=CANDIDATE.relative_to(REPOSITORY_ROOT),
    )
    du = load_module(REPOSITORY_ROOT / GF.DU_PATH, "g77_256gu_existing_du_owner")
    eb = load_module(REPOSITORY_ROOT / GF.EB_PATH, "g77_256gu_existing_eb_owner")
    ee = load_module(REPOSITORY_ROOT / GF.EE_PATH, "g77_256gu_existing_ee_owner")
    assert set(du.validate_file(CANDIDATE, REPOSITORY_ROOT, expected_head=EXPECTED_HEAD).values()) == {"PASS"}
    assert eb.verify_receipt_file(REPOSITORY_ROOT, EB_RECEIPT)["overall_result"] == "PASS"
    assert ee.verify_receipt_file(REPOSITORY_ROOT, EE_RECEIPT)["pre_materialization_runtime_path_binding_result"] == "PASS"


def test_gt_checkout_lifecycle_and_preauthorization_readiness_are_current_and_nonoperational():
    context = load_unique(CONTEXT)
    launcher = load_module(REPOSITORY_ROOT / GF.LAUNCHER_PATH, "g77_256gu_checkout_owner")
    transient_root = Path(context["transient_root"])
    operation_root = Path(context["operation_evidence_root"])
    receipt_parent = Path(context["receipt_parent"])
    checkout = Path(context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["path"])

    assert checkout == transient_root / "checkout"
    assert launcher.fresh_context.checkout_lifecycle_binding(context) == launcher.fresh_context.OPERATION_SCOPED_CHECKOUT_LIFECYCLE
    readiness = launcher.preauth_fresh_checkout_destination_readiness(REPOSITORY_ROOT, context)
    assert readiness["result"] == "PREAUTH_FRESH_CHECKOUT_DESTINATION_READINESS_PASS"
    assert Path(readiness["checkout_path"]) == checkout
    assert readiness["destination_absence_alone_sufficient"] is False
    assert not operation_root.exists()
    assert not transient_root.exists()
    assert not receipt_parent.exists()

    gq = load_unique(REDUCTIONS["GQ"])["reduction"]
    assert gq["self_contained_checkout_proof"]["result"] == (
        "VERIFIED_WITHIN_REPOSITORY_ONLY_MATERIALIZATION_AND_EXACT_"
        "GP_PREAUTHORIZATION_BOUNDARY"
    )
    assert gq["gp_reauthentication"]["preauth_guest_checkout_tree_equivalence"] == "VERIFIED_WITHIN_EXACT_REVIEWED_BOUNDARY"


def test_same_class_owner_and_zero_authority_boundary_are_preserved():
    source = GF_PATH.read_text(encoding="utf-8")
    assert source.count("def instantiate_live_binding(") == 1
    assert "subprocess.run(argv" not in source
    context = load_unique(CONTEXT)
    policy = context["authorization_binding_policy"]
    assert policy["authorization_artifact_hash_in_context"] is False
    assert policy["authorization_reusable"] is False
    assert policy["network_authorized"] is False
    assert policy["one_shot"] is True
    assert policy["retry_limit"] == 0
    assert policy["repair_limit"] == 0
    assert policy["replay_limit"] == 0
