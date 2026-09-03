#!/usr/bin/env python3
"""Focused repository-only proofs for G77-256HE post-HD readiness."""

from __future__ import annotations

from copy import deepcopy
import ast
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
HE = ROOT / ".github/governance/evidence/g77_256he_post_hd_live_binding_readiness_v1"
BINDER_PATH = HE / "binding/G77_256HE_POST_HD_LIVE_BINDING_V1.py"
LIVE = HE / "live_binding"
CANDIDATE = LIVE / "candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
RUNTIME = LIVE / "runtime_projection/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
EB_RECEIPT = LIVE / "bindings/G77_256GY_EB_RECEIPT_V1.json"
EE_RECEIPT = LIVE / "bindings/G77_256GY_EE_RECEIPT_V1.json"
CONTEXT = LIVE / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
TERMINAL = HE / "G77_256HE_SPCE_FINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = ROOT / (
    "docs/governance/G77_256HE_POST_HD_LIVE_BINDING_AND_WRONG_INPUT_"
    "PREOPERATIONAL_READINESS_CERTIFICATION_V1.md"
)


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


BINDER = load_module(BINDER_PATH, "g77_256he_focused_binder")


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"DUPLICATE_JSON_KEY__{key}")
        result[key] = value
    return result


def load_unique(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    assert isinstance(value, dict)
    assert raw == BINDER.canonical_bytes(value)
    return value


def test_exact_committed_hd_material_and_entry_are_authenticated() -> None:
    observed = BINDER.authenticate_committed_hd(ROOT)
    assert observed["head"] == BINDER.EXPECTED_HEAD
    assert observed["tree"] == BINDER.EXPECTED_TREE
    assert observed["branch"] == BINDER.EXPECTED_BRANCH
    assert observed["tracked_status"] == observed["index"] == ""
    assert observed["material_count"] == 6


def test_current_candidate_is_exact_permitted_post_hd_rebind() -> None:
    candidate = BINDER.build_post_hd_candidate(ROOT)
    reference = BINDER._load_canonical(ROOT / BINDER.HB_REFERENCE)
    BINDER.validate_explicit_hd_rebind(reference, candidate)
    assert BINDER.canonical_bytes(candidate) == CANDIDATE.read_bytes()
    assert CANDIDATE.read_bytes() == RUNTIME.read_bytes()
    assert candidate["manifest"]["required_head"] == BINDER.EXPECTED_HEAD
    assert candidate["manifest"]["source_tree"] == BINDER.EXPECTED_TREE
    assert candidate["manifest"]["selected_case"]["case_class"] == BINDER.CASE_CLASS


@pytest.mark.parametrize("mutation", ("HEAD", "TREE", "FM", "CASE", "EXTRA"))
def test_exact_rebind_firewall_rejects_unexpected_drift(mutation: str) -> None:
    reference = BINDER._load_canonical(ROOT / BINDER.HB_REFERENCE)
    candidate = deepcopy(BINDER.build_post_hd_candidate(ROOT))
    if mutation == "HEAD":
        candidate["manifest"]["required_head"] = "0" * 40
    elif mutation == "TREE":
        candidate["manifest"]["source_tree"] = "0" * 40
    elif mutation == "FM":
        candidate["manifest"]["extension_bindings"][5]["sha256"] = "0" * 64
    elif mutation == "CASE":
        candidate["manifest"]["selected_case"]["case_class"] = (
            "E05_NEGATIVE_AUTHORITY_WRONG_ATTEMPT"
        )
    else:
        candidate["manifest"]["unexpected"] = True
    candidate["manifest_sha256"] = hashlib.sha256(
        BINDER.canonical_bytes(candidate["manifest"])
    ).hexdigest()
    with pytest.raises(
        BINDER.PostHDBindingError,
        match="CANDIDATE_SEMANTICS_CHANGED_OUTSIDE_EXPLICIT_HD_REBIND",
    ):
        BINDER.validate_explicit_hd_rebind(reference, candidate)


def test_persisted_du_eb_ee_and_context_bind_exact_hd_identity() -> None:
    context = load_unique(CONTEXT)
    candidate = load_unique(CANDIDATE)
    assert context["repository_head"] == candidate["manifest"]["required_head"]
    assert context["repository_tree"] == candidate["manifest"]["source_tree"]
    assert context["repository_head"] == BINDER.EXPECTED_HEAD
    assert context["repository_tree"] == BINDER.EXPECTED_TREE
    assert context["candidate_manifest_sha256"] == BINDER.sha256_path(CANDIDATE)

    gy = load_module(ROOT / BINDER.GY_BINDER, "g77_256he_persisted_gy_owner")
    du = load_module(ROOT / gy.DU_PATH, "g77_256he_persisted_du_owner")
    eb = load_module(ROOT / gy.EB_PATH, "g77_256he_persisted_eb_owner")
    ee = load_module(ROOT / gy.EE_PATH, "g77_256he_persisted_ee_owner")
    assert set(
        du.validate_file(CANDIDATE, ROOT, expected_head=BINDER.EXPECTED_HEAD).values()
    ) == {"PASS"}
    assert eb.verify_receipt_file(ROOT, EB_RECEIPT)["overall_result"] == "PASS"
    assert ee.verify_receipt_file(ROOT, EE_RECEIPT)[
        "pre_materialization_runtime_path_binding_result"
    ] == "PASS"


def test_committed_hd_static_readiness_and_failure_class_block(tmp_path: Path) -> None:
    context = BINDER.build_post_hd_context(
        repository_root=ROOT,
        candidate_path=CANDIDATE,
        operation_root=tmp_path / "operation_state",
        transient_root=tmp_path / "transient",
    )
    launcher = load_module(ROOT / BINDER.FM_LAUNCHER, "g77_256he_static_fm_owner")
    context_path = tmp_path / "context.json"
    context_path.write_bytes(launcher.fresh_context.canonical_bytes(context))
    materialization = launcher.materialize_operation_state(
        repository_root=ROOT,
        context=context,
        context_source_path=context_path,
        candidate_source_path=CANDIDATE.relative_to(ROOT),
    )
    assert materialization["qemu_execution_count"] == 0
    observations = launcher.observe_context_assets(
        ROOT, context, CANDIDATE.relative_to(ROOT)
    )
    readiness = launcher.authority_free_static_readiness(
        repository_root=ROOT,
        context=context,
        observed_head=BINDER.EXPECTED_HEAD,
        observed_tree=BINDER.EXPECTED_TREE,
        repository_clean=True,
        observed_asset_sha256=observations,
        candidate_source_path=CANDIDATE.relative_to(ROOT),
    )
    owner = readiness["checkout_readiness"][
        "preauth_guest_fm_context_owner_binding"
    ]
    assert readiness["result"] == "STATIC_READINESS_PASS"
    assert readiness["human_operational_authorization_count"] == 0
    assert readiness["qemu_execution_count"] == 0
    assert owner["host_checkout_guest_byte_identity"] == "PASS"
    assert owner["host_checkout_guest_hash_identity"] == "PASS"
    assert owner["checkout_sha256"] == BINDER.FM_CONTEXT_OWNER_SHA256


def test_semantic_firewall_single_route_and_zero_operation() -> None:
    launcher_source = (ROOT / BINDER.FM_LAUNCHER).read_text(encoding="utf-8")
    tree = ast.parse(launcher_source)
    mains = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "main"
    ]
    qemu_calls = [
        node
        for node in ast.walk(mains[0])
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "subprocess"
        and node.func.attr == "run"
    ]
    assert len(mains) == len(qemu_calls) == 1
    assert "input_identity" not in launcher_source
    assert subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True
    ).strip() == ""


def test_terminal_reduction_and_g48_structure() -> None:
    envelope = load_unique(TERMINAL)
    reduction = envelope["reduction"]
    assert hashlib.sha256(BINDER.canonical_bytes(reduction)).hexdigest() == (
        envelope["reduction_sha256"]
    )
    assert reduction["readiness_reduction"]["terminal_branch"] == (
        "BRANCH_A__REPOSITORY_READY"
    )
    assert reduction["readiness_reduction"]["preoperational_readiness_status"] == (
        "VERIFIED"
    )
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"]["before"] == reduction["e05"]["after"] == "7/18"

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
    assert report.count(
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?"
    ) == 1
    assert report.count("| `PREVIOUS_WORKER_CONVERSATION_REQUIRED` |") == 1
