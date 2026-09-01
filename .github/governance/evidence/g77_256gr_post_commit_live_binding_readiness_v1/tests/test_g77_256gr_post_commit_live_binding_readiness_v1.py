#!/usr/bin/env python3
"""Focused repository-only proof for the exact GQ -> GF/GD GR binding."""

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
EXPECTED_HEAD = "99d8e889ae36d75af9f64e3db977aa452d83dd1e"
EXPECTED_TREE = "7278822cf1883b125e0789c10fa668d40a43c1c3"
EXPECTED_GQ_SEAL = "2c46a847854b566d33a679ed8bfd0b3897c3dec2c586f0b3c17bb7b14e1c62a4"
EXPECTED_GP_SEAL = "f8948b4ecc0a07b865d06d404e830ba216b8aa4fd841e54cae18883561d3269b"
EVIDENCE_ROOT = REPOSITORY_ROOT / (
    ".github/governance/evidence/"
    "g77_256gr_post_commit_live_binding_readiness_v1"
)
LIVE_ROOT = EVIDENCE_ROOT / "live_binding"
CANDIDATE = LIVE_ROOT / "candidate/G77_256GR_CONTINUATION_MANIFEST_V1.json"
RUNTIME_CANDIDATE = (
    LIVE_ROOT / "ee_runtime_projection/G77_256GR_CONTINUATION_MANIFEST_V1.json"
)
CONTEXT = LIVE_ROOT / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
EB_RECEIPT = LIVE_ROOT / "bindings/CANDIDATE_BOUND_EB_RECEIPT_V1.json"
EE_RECEIPT = LIVE_ROOT / "bindings/RUNTIME_CONSUMER_EE_RECEIPT_V1.json"
GQ_REDUCTION = REPOSITORY_ROOT / (
    ".github/governance/evidence/g77_256gq_guest_self_contained_checkout_v1/"
    "G77_256GQ_SPCE_FINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)
GP_REDUCTION = REPOSITORY_ROOT / (
    ".github/governance/evidence/g77_256gp_guest_checkout_tree_precondition_v1/"
    "G77_256GP_SPCE_FINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)
GF_PATH = REPOSITORY_ROOT / (
    ".github/governance/evidence/g77_256gf_post_commit_live_binding_v1/binding/"
    "G77_256GF_POST_COMMIT_LIVE_EXECUTION_BINDING_V1.py"
)


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


GF = load_module(GF_PATH, "g77_256gr_existing_gf_owner")


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


def test_gq_gp_seals_and_exact_bounded_properties_are_preserved():
    assert reduction_seal(GQ_REDUCTION) == (EXPECTED_GQ_SEAL, EXPECTED_GQ_SEAL)
    assert reduction_seal(GP_REDUCTION) == (EXPECTED_GP_SEAL, EXPECTED_GP_SEAL)
    gq = load_unique(GQ_REDUCTION)["reduction"]
    proof = gq["self_contained_checkout_proof"]
    assert proof["result"] == (
        "VERIFIED_WITHIN_REPOSITORY_ONLY_MATERIALIZATION_AND_EXACT_"
        "GP_PREAUTHORIZATION_BOUNDARY"
    )
    for field in (
        "self_contained_presented_checkout",
        "expected_head_resolves",
        "expected_tree_resolves",
        "tree_equals_expected_committed_tree",
        "no_external_git_metadata_dependency",
        "no_external_object_database_dependency",
        "exact_presentation_root_bound",
        "exact_guest_destination_bound",
        "gp_preauthorization_owner_accepts",
        "unchanged_er_consumer_semantics",
    ):
        assert proof[field] is True
    assert proof["full_qemu_transport_behavior"] == "NOT_PROVEN"
    assert gq["gp_reauthentication"]["preauth_guest_checkout_tree_equivalence"] == (
        "VERIFIED_WITHIN_EXACT_REVIEWED_BOUNDARY"
    )


def test_current_gq_identity_is_bound_through_existing_gf_gd_du_eb_ee_owners():
    assert subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPOSITORY_ROOT, text=True
    ).strip() == EXPECTED_HEAD
    assert subprocess.check_output(
        ["git", "rev-parse", "HEAD^{tree}"], cwd=REPOSITORY_ROOT, text=True
    ).strip() == EXPECTED_TREE

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

    launcher = load_module(
        REPOSITORY_ROOT / GF.LAUNCHER_PATH, "g77_256gr_existing_fm_owner"
    )
    assert launcher.fresh_context.load_context(
        CONTEXT, repository_root=REPOSITORY_ROOT
    ) == context
    launcher.validate_immutable_context_bindings(
        REPOSITORY_ROOT,
        context,
        candidate_source_path=CANDIDATE.relative_to(REPOSITORY_ROOT),
    )
    du = load_module(REPOSITORY_ROOT / GF.DU_PATH, "g77_256gr_existing_du_owner")
    eb = load_module(REPOSITORY_ROOT / GF.EB_PATH, "g77_256gr_existing_eb_owner")
    ee = load_module(REPOSITORY_ROOT / GF.EE_PATH, "g77_256gr_existing_ee_owner")
    assert set(du.validate_file(CANDIDATE, REPOSITORY_ROOT, expected_head=EXPECTED_HEAD).values()) == {"PASS"}
    assert eb.verify_receipt_file(REPOSITORY_ROOT, EB_RECEIPT)["overall_result"] == "PASS"
    assert ee.verify_receipt_file(REPOSITORY_ROOT, EE_RECEIPT)[
        "pre_materialization_runtime_path_binding_result"
    ] == "PASS"


def test_readiness_is_nonoperational_fresh_and_has_no_stale_candidate_binding():
    context = load_unique(CONTEXT)
    operation_root = Path(context["operation_evidence_root"])
    transient_root = Path(context["transient_root"])
    receipt_parent = Path(context["receipt_parent"])
    assert operation_root == EVIDENCE_ROOT / "future_operation_state"
    assert receipt_parent == operation_root / "receipts"
    assert not operation_root.exists()
    assert not transient_root.exists()
    assert not receipt_parent.exists()

    stale_values = {
        "e2933f3ce86e722b0f1241142267541df6807bc3",
        "ec879d8809d373809f412de526cad76bf18de3c6",
        "1357c5194fefadfdbcb4fb633f5d2bdf9aec3945",
        "7107d884cad6cb9c67ba3dd81f7d885b4c01b824",
    }
    for path in (CANDIDATE, RUNTIME_CANDIDATE, CONTEXT, EB_RECEIPT, EE_RECEIPT):
        text = path.read_text(encoding="utf-8")
        assert not any(value in text for value in stale_values)

    source = GF_PATH.read_text(encoding="utf-8")
    assert source.count("def instantiate_live_binding(") == 1
    assert "subprocess.run(argv" not in source
