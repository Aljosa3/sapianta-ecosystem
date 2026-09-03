#!/usr/bin/env python3
"""Focused repository-only checks for G77-256HH Branch B reduction."""

from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
HH_ROOT = ROOT / ".github/governance/evidence/g77_256hh_post_hg_live_binding_readiness_v1"
BINDER_PATH = HH_ROOT / "binding/G77_256HH_POST_HG_LIVE_BINDING_V1.py"
LIVE = HH_ROOT / "live_binding"
TERMINAL = HH_ROOT / "G77_256HH_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = ROOT / (
    "docs/governance/G77_256HH_POST_HG_LIVE_BINDING_AND_DU_EB_EE_"
    "PREOPERATIONAL_READINESS_REAUTHENTICATION_V1.md"
)
HF_CONTEXT = ROOT / (
    ".github/governance/evidence/g77_256hf_wrong_input_operational_v1/"
    "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
)


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


BINDER = load_module(BINDER_PATH, "g77_256hh_binder_test")
LAUNCHER = load_module(ROOT / BINDER.FM_LAUNCHER, "g77_256hh_launcher_test")
OWNER = LAUNCHER.fresh_context
FIXTURE = load_module(ROOT / BINDER.HG_FIXTURE, "g77_256hh_fixture_test")


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    assert isinstance(value, dict)
    assert raw == BINDER.canonical_bytes(value)
    return value


def reseal(context: dict[str, Any]) -> dict[str, Any]:
    context.pop("context_sha256", None)
    return OWNER.seal_context(context)


def build_context(tmp_path: Path) -> dict[str, Any]:
    candidate = LIVE / "candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
    return LAUNCHER.build_operation_context(
        repository_root=ROOT,
        repository_head=BINDER.EXPECTED_HEAD,
        repository_tree=BINDER.EXPECTED_TREE,
        generation_identity=(
            "G77_256HH_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_"
            "OPERATIONAL_COMMISSIONING_V1"
        ),
        operation_identity="G77_256HH_E05_WRONG_INPUT_DENIAL_BEFORE_ENTRY_001",
        identity_namespace_prefix="G77_256HH",
        operation_evidence_root=tmp_path / "operation_state",
        transient_root=tmp_path / "transient",
        candidate_source_path=candidate.relative_to(ROOT),
    )


def test_exact_committed_hg_identity_and_changed_owners() -> None:
    observed = BINDER.authenticate_committed_hg(ROOT)
    assert observed["head"] == BINDER.EXPECTED_HEAD
    assert observed["tree"] == BINDER.EXPECTED_TREE
    assert hashlib.sha256((ROOT / BINDER.FM_CONTEXT_OWNER).read_bytes()).hexdigest() == (
        BINDER.FM_CONTEXT_OWNER_SHA256
    )
    assert hashlib.sha256((ROOT / BINDER.FM_LAUNCHER).read_bytes()).hexdigest() == (
        BINDER.FM_LAUNCHER_SHA256
    )


def test_exact_candidate_rebind_and_current_du_eb_ee() -> None:
    candidate = load_canonical(
        LIVE / "candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
    )
    reference = load_canonical(ROOT / BINDER.HE_REFERENCE)
    BINDER.validate_exact_hg_rebind(reference, candidate)
    assert BINDER.sha256_path(
        LIVE / "candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
    ) == "7ab5997938bbb618b949930e1cd2e3be2f145175110a8ef6bccc0571eb39e194"
    assert candidate["manifest_sha256"] == (
        "e49d0735ad19402f4a912b54a4f7207d1edcca6eccf702aaa496eac0c0a6d4f5"
    )
    runtime = LIVE / "runtime_projection/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
    assert (LIVE / "candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json").read_bytes() == runtime.read_bytes()
    eb = load_module(ROOT / BINDER.EB, "g77_256hh_eb_test")
    ee = load_module(ROOT / BINDER.EE, "g77_256hh_ee_test")
    assert eb.verify_receipt_file(ROOT, LIVE / "bindings/G77_256GY_EB_RECEIPT_V1.json")["overall_result"] == "PASS"
    assert ee.verify_receipt_file(ROOT, LIVE / "bindings/G77_256GY_EE_RECEIPT_V1.json")["pre_materialization_runtime_path_binding_result"] == "PASS"


def test_context_binds_current_owner_but_checkout_projects_pre_hg_owner() -> None:
    context = load_canonical(LIVE / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json")
    assert context["wrapper_fc_er_che_schema_hashes"][
        LAUNCHER.FRESH_OPERATION_CONTEXT_OWNER_HASH_KEY
    ] == BINDER.FM_CONTEXT_OWNER_SHA256
    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    assert (checkout["head"], checkout["tree"]) == (
        "a5fde262c8833922375a10e79c745c0ff19e698e",
        "c265719bc048a9ab686e290d1952280d5584a43e",
    )
    assert BINDER.sha256_bytes(
        BINDER._git_bytes(ROOT, f"{checkout['head']}:{BINDER.FM_CONTEXT_OWNER.as_posix()}")
    ) == "45b97e99122146ec3aa95f45fe5ac71381ca1a11e83b7355438b988608f52fca"
    assert BINDER.FM_CONTEXT_OWNER_SHA256 != (
        "45b97e99122146ec3aa95f45fe5ac71381ca1a11e83b7355438b988608f52fca"
    )


def test_stale_checkout_is_rejected_before_authority(tmp_path: Path) -> None:
    context = build_context(tmp_path)
    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    LAUNCHER.materialize_guest_self_contained_checkout(
        source_repository=ROOT,
        checkout_path=Path(checkout["path"]),
        expected_head=checkout["head"],
        expected_tree=checkout["tree"],
    )
    with pytest.raises(RuntimeError, match="context owner identity mismatch"):
        LAUNCHER.prove_guest_fresh_operation_context_owner_binding(ROOT, context)


def test_missing_and_wrong_owner_hash_are_rejected_before_authority(tmp_path: Path) -> None:
    missing = build_context(tmp_path / "missing")
    missing["wrapper_fc_er_che_schema_hashes"].pop(
        LAUNCHER.FRESH_OPERATION_CONTEXT_OWNER_HASH_KEY
    )
    with pytest.raises(RuntimeError, match="omits FM context owner binding"):
        LAUNCHER.validate_immutable_context_bindings(
            ROOT, reseal(missing),
            candidate_source_path=(LIVE / "candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json").relative_to(ROOT),
        )
    wrong = build_context(tmp_path / "wrong")
    wrong["wrapper_fc_er_che_schema_hashes"][
        LAUNCHER.FRESH_OPERATION_CONTEXT_OWNER_HASH_KEY
    ] = "0" * 64
    with pytest.raises(RuntimeError, match="immutable wrapper"):
        LAUNCHER.validate_immutable_context_bindings(
            ROOT, reseal(wrong),
            candidate_source_path=(LIVE / "candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json").relative_to(ROOT),
        )


def test_projection_and_canonical_argv_rejections_remain_fail_closed() -> None:
    hf = load_canonical(HF_CONTEXT)
    result = OWNER.validate_sealed_canonical_argv(
        hf, validation_repository_root=FIXTURE.GUEST_PROJECTED_PATH
    )
    assert result["projection_status"] == "EXACT_GUEST_PROJECTION"
    with pytest.raises(OWNER.ContextError, match="validation view is not projection-bound"):
        OWNER.validate_sealed_canonical_argv(
            hf, validation_repository_root=Path("/mnt/not-aigol")
        )
    mutated = deepcopy(hf)
    index = next(
        index + 1
        for index, value in enumerate(mutated["canonical_argv"][:-1])
        if value == "-virtfs"
        and "mount_tag=g77_harness" in mutated["canonical_argv"][index + 1]
    )
    mutated["canonical_argv"][index] = mutated["canonical_argv"][index].replace(
        str(FIXTURE.HOST_CANONICAL_IDENTITY), "/srv/unauthorized-repository"
    )
    mutated["canonical_argv_sha256"] = OWNER.argv_sha256(mutated["canonical_argv"])
    mutated = reseal(mutated)
    with pytest.raises(OWNER.ContextError, match="canonical argv changed"):
        OWNER.validate_sealed_canonical_argv(
            mutated, validation_repository_root=FIXTURE.GUEST_PROJECTED_PATH
        )


def test_same_class_firewall_reducer_and_single_route_are_unchanged() -> None:
    candidate = load_canonical(
        LIVE / "candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
    )
    assert candidate["manifest"]["selected_case"] == {
        "case_class": BINDER.CASE_CLASS,
        "case_id": "G77_256GY_E05_WRONG_INPUT_DENIAL_BEFORE_ENTRY_001",
    }
    reducer_sha = hashlib.sha256((ROOT / BINDER.GY_REDUCER).read_bytes()).hexdigest()
    assert reducer_sha == "8a6e6081118a2c1d305260555ba1ad5a11d97a5d66516f9810beb87c5c39fbf7"
    tree = ast.parse((ROOT / BINDER.FM_LAUNCHER).read_text(encoding="utf-8"))
    mains = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main"]
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


def test_terminal_reduction_and_g48_fail_closed_structure() -> None:
    terminal = load_canonical(TERMINAL)["reduction"]
    assert terminal["terminal_branch"] == "BRANCH_B__READINESS_NOT_PROVEN"
    assert terminal["result"]["du_status"] == "PASS"
    assert terminal["result"]["eb_status"] == "PASS"
    assert terminal["result"]["ee_status"] == "PASS"
    assert terminal["result"]["preoperational_readiness_status"] == "NOT_PROVEN"
    report = REPORT.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    assert report.rstrip().endswith(
        "FAIL_CLOSED__G77_256HH_POST_HG_PREOPERATIONAL_READINESS_NOT_PROVEN__"
        "STALE_PRE_HG_CHECKOUT_OWNER_BINDING__ZERO_OPERATION__E05_7_OF_18__"
        "HUMAN_REVIEW_REQUIRED"
    )
