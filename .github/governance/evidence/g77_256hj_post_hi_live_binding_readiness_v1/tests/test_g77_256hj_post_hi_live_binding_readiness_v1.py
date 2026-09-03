#!/usr/bin/env python3
"""Focused repository-only proofs for G77-256HJ post-HI readiness."""

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
HJ = ROOT / ".github/governance/evidence/g77_256hj_post_hi_live_binding_readiness_v1"
BINDER_PATH = HJ / "binding/G77_256HJ_POST_HI_LIVE_BINDING_V1.py"
LIVE = HJ / "live_binding"
CANDIDATE = LIVE / "candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
RUNTIME = LIVE / "runtime_projection/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
EB_RECEIPT = LIVE / "bindings/G77_256GY_EB_RECEIPT_V1.json"
EE_RECEIPT = LIVE / "bindings/G77_256GY_EE_RECEIPT_V1.json"
CONTEXT = LIVE / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
TERMINAL = HJ / "G77_256HJ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = ROOT / (
    "docs/governance/G77_256HJ_POST_HI_LIVE_BINDING_AND_PREOPERATIONAL_"
    "READINESS_REAUTHENTICATION_V1.md"
)


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


BINDER = load_module(BINDER_PATH, "g77_256hj_focused_binder")


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


def reseal_context(owner: Any, context: dict[str, Any]) -> dict[str, Any]:
    value = deepcopy(context)
    value.pop("context_sha256", None)
    return owner.seal_context(value)


def test_exact_committed_hi_and_historical_frontier_are_authenticated() -> None:
    observed = BINDER.authenticate_committed_hi(ROOT)
    assert observed["head"] == BINDER.EXPECTED_HEAD
    assert observed["tree"] == BINDER.EXPECTED_TREE
    assert observed["subject"] == BINDER.EXPECTED_SUBJECT
    assert observed["fm_launcher_sha256"] == BINDER.FM_LAUNCHER_SHA256
    assert observed["fm_context_owner_sha256"] == BINDER.FM_CONTEXT_OWNER_SHA256
    assert subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True
    ).strip() == ""


def test_current_candidate_runtime_and_du_eb_ee_bind_exact_hi() -> None:
    candidate = BINDER.build_post_hi_candidate(ROOT)
    reference = BINDER.load_canonical(ROOT / BINDER.HH_REFERENCE)
    BINDER.validate_exact_hi_rebind(reference, candidate)
    assert BINDER.canonical_bytes(candidate) == CANDIDATE.read_bytes()
    assert CANDIDATE.read_bytes() == RUNTIME.read_bytes()
    assert candidate["manifest"]["required_head"] == BINDER.EXPECTED_HEAD
    assert candidate["manifest"]["source_tree"] == BINDER.EXPECTED_TREE
    gy = load_module(ROOT / BINDER.GY_BINDER, "g77_256hj_persisted_gy")
    du = load_module(ROOT / gy.DU_PATH, "g77_256hj_persisted_du")
    eb = load_module(ROOT / gy.EB_PATH, "g77_256hj_persisted_eb")
    ee = load_module(ROOT / gy.EE_PATH, "g77_256hj_persisted_ee")
    assert set(
        du.validate_file(CANDIDATE, ROOT, expected_head=BINDER.EXPECTED_HEAD).values()
    ) == {"PASS"}
    assert eb.verify_receipt_file(ROOT, EB_RECEIPT)["overall_result"] == "PASS"
    assert ee.verify_receipt_file(ROOT, EE_RECEIPT)[
        "pre_materialization_runtime_path_binding_result"
    ] == "PASS"


@pytest.mark.parametrize(
    "mutation", ("HEAD", "TREE", "LAUNCHER", "CASE", "EXTRA", "BAD_SEAL")
)
def test_exact_hi_rebind_firewall_rejects_all_other_drift(mutation: str) -> None:
    reference = BINDER.load_canonical(ROOT / BINDER.HH_REFERENCE)
    candidate = deepcopy(BINDER.build_post_hi_candidate(ROOT))
    if mutation == "HEAD":
        candidate["manifest"]["required_head"] = "0" * 40
    elif mutation == "TREE":
        candidate["manifest"]["source_tree"] = "0" * 40
    elif mutation == "LAUNCHER":
        candidate["manifest"]["extension_bindings"][5]["sha256"] = "0" * 64
    elif mutation == "CASE":
        candidate["manifest"]["selected_case"]["case_class"] = (
            "E05_NEGATIVE_AUTHORITY_WRONG_ATTEMPT"
        )
    elif mutation == "EXTRA":
        candidate["manifest"]["unexpected"] = True
    else:
        candidate["manifest_sha256"] = "0" * 64
    if mutation != "BAD_SEAL":
        candidate["manifest_sha256"] = hashlib.sha256(
            BINDER.canonical_bytes(candidate["manifest"])
        ).hexdigest()
    with pytest.raises(BINDER.PostHIBindingError):
        BINDER.validate_exact_hi_rebind(reference, candidate)


def test_persisted_context_binds_hi_candidate_and_committed_hg_owner() -> None:
    context = load_unique(CONTEXT)
    assert context["repository_head"] == BINDER.EXPECTED_HEAD
    assert context["repository_tree"] == BINDER.EXPECTED_TREE
    assert context["candidate_manifest_sha256"] == BINDER.sha256_path(CANDIDATE)
    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    assert checkout["head"] == BINDER.EXPECTED_HG_HEAD
    assert checkout["tree"] == BINDER.EXPECTED_HG_TREE
    assert context["wrapper_fc_er_che_schema_hashes"][
        "fresh_operation_context_owner"
    ] == BINDER.FM_CONTEXT_OWNER_SHA256
    committed_owner = subprocess.check_output(
        [
            "git",
            "show",
            f"{BINDER.EXPECTED_HG_HEAD}:{BINDER.FM_CONTEXT_OWNER.as_posix()}",
        ],
        cwd=ROOT,
    )
    assert hashlib.sha256(committed_owner).hexdigest() == BINDER.FM_CONTEXT_OWNER_SHA256


def test_current_wrong_input_static_readiness_fails_closed_before_authority(
    tmp_path: Path,
) -> None:
    operation_root = tmp_path / "operation_state"
    transient_root = tmp_path / "transient"
    context = BINDER.build_post_hi_context(
        repository_root=ROOT,
        candidate_path=CANDIDATE,
        operation_root=operation_root,
        transient_root=transient_root,
    )
    launcher = load_module(ROOT / BINDER.FM_LAUNCHER, "g77_256hj_static_launcher")
    context_path = tmp_path / "context.json"
    context_path.write_bytes(launcher.fresh_context.canonical_bytes(context))
    materialization = launcher.materialize_operation_state(
        repository_root=ROOT,
        context=context,
        context_source_path=context_path,
        candidate_source_path=CANDIDATE.relative_to(ROOT),
    )
    observations = launcher.observe_context_assets(
        ROOT, context, CANDIDATE.relative_to(ROOT)
    )
    assert materialization["qemu_execution_count"] == 0
    checkout = launcher.validate_checkout_preboot_readiness(context)
    owner = checkout["preauth_guest_fm_context_owner_binding"]
    assert owner["host_checkout_guest_byte_identity"] == "PASS"
    assert owner["host_checkout_guest_hash_identity"] == "PASS"
    assert owner["checkout_sha256"] == BINDER.FM_CONTEXT_OWNER_SHA256
    with pytest.raises(
        RuntimeError,
        match="cloud-init pre-request argument binding missing or ambiguous",
    ):
        launcher.authority_free_static_readiness(
            repository_root=ROOT,
            context=context,
            observed_head=BINDER.EXPECTED_HEAD,
            observed_tree=BINDER.EXPECTED_TREE,
            repository_clean=True,
            observed_asset_sha256=observations,
            candidate_source_path=CANDIDATE.relative_to(ROOT),
        )


def test_preauthorization_negative_matrix_fails_closed(tmp_path: Path) -> None:
    context = load_unique(CONTEXT)
    launcher = load_module(ROOT / BINDER.FM_LAUNCHER, "g77_256hj_negative_launcher")
    owner = launcher.fresh_context
    candidate_relative = CANDIDATE.relative_to(ROOT)

    with pytest.raises(RuntimeError):
        launcher.validate_immutable_context_bindings(
            ROOT, context, candidate_source_path=Path("missing/current/candidate.json")
        )

    wrong_candidate = deepcopy(context)
    wrong_candidate["candidate_manifest_sha256"] = "0" * 64
    wrong_candidate = reseal_context(owner, wrong_candidate)
    with pytest.raises(RuntimeError):
        launcher.validate_immutable_context_bindings(
            ROOT, wrong_candidate, candidate_source_path=candidate_relative
        )

    reference = BINDER.load_canonical(ROOT / BINDER.HH_REFERENCE)
    stale_launcher = deepcopy(BINDER.build_post_hi_candidate(ROOT))
    stale_launcher["manifest"]["extension_bindings"][5]["sha256"] = (
        reference["manifest"]["extension_bindings"][5]["sha256"]
    )
    stale_launcher["manifest_sha256"] = hashlib.sha256(
        BINDER.canonical_bytes(stale_launcher["manifest"])
    ).hexdigest()
    with pytest.raises(BINDER.PostHIBindingError):
        BINDER.validate_exact_hi_rebind(reference, stale_launcher)

    wrong_hash = deepcopy(context)
    wrong_hash["wrapper_fc_er_che_schema_hashes"][
        "fresh_operation_context_owner"
    ] = "0" * 64
    wrong_hash = reseal_context(owner, wrong_hash)
    with pytest.raises(RuntimeError):
        launcher.validate_immutable_context_bindings(
            ROOT, wrong_hash, candidate_source_path=candidate_relative
        )

    malformed_hash = deepcopy(context)
    malformed_hash["wrapper_fc_er_che_schema_hashes"][
        "fresh_operation_context_owner"
    ] = "malformed"
    malformed_hash = reseal_context(owner, malformed_hash)
    with pytest.raises(owner.ContextError):
        owner.validate_context(malformed_hash, repository_root=ROOT)

    invalid_projection = deepcopy(context)
    invalid_projection["qemu_executable_base_seed_checkout_bindings"]["checkout"][
        "path"
    ] = "/tmp/wrong-checkout"
    invalid_projection = reseal_context(owner, invalid_projection)
    with pytest.raises((RuntimeError, owner.ContextError)):
        launcher.validate_immutable_context_bindings(
            ROOT, invalid_projection, candidate_source_path=candidate_relative
        )

    gy = load_module(ROOT / BINDER.GY_BINDER, "g77_256hj_negative_gy")
    eb = load_module(ROOT / gy.EB_PATH, "g77_256hj_negative_eb")
    ee = load_module(ROOT / gy.EE_PATH, "g77_256hj_negative_ee")
    with pytest.raises((FileNotFoundError, ee.BindingError)):
        ee.verify_receipt_file(ROOT, HJ / "missing-ee-receipt.json")
    stale_receipt = (
        ROOT
        / ".github/governance/evidence/g77_256hh_post_hg_live_binding_readiness_v1/"
        "live_binding/bindings/G77_256GY_EB_RECEIPT_V1.json"
    )
    with pytest.raises(eb.ReceiptError):
        eb.verify_receipt_file(ROOT, stale_receipt)

    scratch = HJ / f"negative_matrix_{tmp_path.name}"
    scratch.mkdir()
    try:
        runtime_root = scratch / "runtime"
        runtime_root.mkdir()
        bad_runtime = runtime_root / CANDIDATE.name
        bad_runtime.write_bytes(CANDIDATE.read_bytes() + b"\n")
        with pytest.raises(ee.BindingError):
            ee.validate_binding(
                ROOT,
                CANDIDATE,
                EB_RECEIPT,
                LIVE / "bindings/G77_256GY_EE_PATH_PROJECTION_FIXTURE_V1.py",
                runtime_root,
                "/mnt/g77-evidence",
                required_head=BINDER.EXPECTED_HEAD,
                required_tree=BINDER.EXPECTED_TREE,
            )
    finally:
        bad_runtime.unlink(missing_ok=True)
        runtime_root.rmdir()
        scratch.rmdir()

    materialized_context = BINDER.build_post_hi_context(
        repository_root=ROOT,
        candidate_path=CANDIDATE,
        operation_root=tmp_path / "owner_operation",
        transient_root=tmp_path / "owner_transient",
    )
    context_path = tmp_path / "owner-context.json"
    context_path.write_bytes(owner.canonical_bytes(materialized_context))
    launcher.materialize_operation_state(
        repository_root=ROOT,
        context=materialized_context,
        context_source_path=context_path,
        candidate_source_path=candidate_relative,
    )
    projected_owner = (
        Path(
            materialized_context["qemu_executable_base_seed_checkout_bindings"]
            ["checkout"]["path"]
        )
        / BINDER.FM_CONTEXT_OWNER
    )
    correct_bytes = projected_owner.read_bytes()
    projected_owner.write_bytes(b"wrong owner\n")
    with pytest.raises(RuntimeError, match="context owner identity mismatch"):
        launcher.prove_guest_fresh_operation_context_owner_binding(
            ROOT, materialized_context
        )
    stale_bytes = subprocess.check_output(
        [
            "git",
            "show",
            "a5fde262c8833922375a10e79c745c0ff19e698e:"
            + BINDER.FM_CONTEXT_OWNER.as_posix(),
        ],
        cwd=ROOT,
    )
    projected_owner.write_bytes(stale_bytes)
    with pytest.raises(RuntimeError, match="context owner identity mismatch"):
        launcher.prove_guest_fresh_operation_context_owner_binding(
            ROOT, materialized_context
        )
    projected_owner.unlink()
    with pytest.raises(RuntimeError, match="context owner absent"):
        launcher.prove_guest_fresh_operation_context_owner_binding(
            ROOT, materialized_context
        )
    projected_owner.write_bytes(correct_bytes)

    duplicate = tmp_path / "duplicate.json"
    duplicate.write_bytes(b'{"owner":"a","owner":"b"}\n')
    with pytest.raises(BINDER.PostHIBindingError, match="DUPLICATE_JSON_KEY"):
        BINDER.load_canonical(duplicate)


def test_projection_semantic_firewall_single_route_and_terminal_reduction() -> None:
    launcher_source = (ROOT / BINDER.FM_LAUNCHER).read_text(encoding="utf-8")
    tree = ast.parse(launcher_source)
    mains = [
        node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main"
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
    assert BINDER.sha256_path(ROOT / BINDER.GY_REDUCER) == (
        "8a6e6081118a2c1d305260555ba1ad5a11d97a5d66516f9810beb87c5c39fbf7"
    )
    envelope = load_unique(TERMINAL)
    reduction = envelope["reduction"]
    assert hashlib.sha256(BINDER.canonical_bytes(reduction)).hexdigest() == (
        envelope["reduction_sha256"]
    )
    assert reduction["readiness"]["terminal_branch"] == (
        "BRANCH_B__READINESS_NOT_PROVEN"
    )
    assert reduction["readiness"]["next_operational_generation_eligible"] == (
        "NOT_PROVEN"
    )
    assert reduction["capability_boundary"][
        "wrong_input_operational_capability"
    ] == "NOT_PROVEN"
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"]["before"] == reduction["e05"]["after"] == "7/18"


def test_g48_exact_six_headings_and_terminal_control() -> None:
    reduction = load_unique(TERMINAL)["reduction"]
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
    assert "AUTO_CONTINUABLE = NO" in report
    assert "HUMAN_REVIEW_REQUIRED = YES" in report
