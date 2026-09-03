#!/usr/bin/env python3
"""Repository-only proof of the exact current-HG FM checkout-owner binding."""

from __future__ import annotations

import ast
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
FM_ROOT = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher"
)
LAUNCHER_PATH = FM_ROOT / "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
OWNER_PATH = FM_ROOT / "sapianta_fresh_operation_context_v1.py"
HH_ROOT = ROOT / (
    ".github/governance/evidence/g77_256hh_post_hg_live_binding_readiness_v1"
)
HH_CANDIDATE = HH_ROOT / (
    "live_binding/candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
)
HH_RUNTIME = HH_ROOT / (
    "live_binding/runtime_projection/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
)
HH_REDUCTION = HH_ROOT / "G77_256HH_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
HH_REPORT = ROOT / (
    "docs/governance/G77_256HH_POST_HG_LIVE_BINDING_AND_DU_EB_EE_"
    "PREOPERATIONAL_READINESS_REAUTHENTICATION_V1.md"
)
HI_REDUCTION = ROOT / (
    ".github/governance/evidence/g77_256hi_current_hg_checkout_owner_binding_v1/"
    "G77_256HI_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)
HI_REPORT = ROOT / (
    "docs/governance/G77_256HI_CURRENT_HG_FM_CHECKOUT_OWNER_BINDING_"
    "CORRECTION_V1.md"
)
GY_REDUCER = ROOT / (
    ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/reducer/"
    "G77_256GY_WRONG_INPUT_TERMINAL_ACCEPTANCE_REDUCER_V1.py"
)

HH_HEAD = "f784bb7afe1d1f8279ba9d58edbda92dc26329c8"
HH_TREE = "32bd68a38962f1b0e0d73dd40cb988ef398455f0"
HG_HEAD = "842a0f2cccd53222d11daa698bdeab17f0aac043"
HG_TREE = "414a5f940e3b5027b6dd86c38d7a134f5c8ab0c4"
STALE_HEAD = "a5fde262c8833922375a10e79c745c0ff19e698e"
STALE_TREE = "c265719bc048a9ab686e290d1952280d5584a43e"
HG_OWNER_SHA256 = "db8257ab2e693edf842ba8224792910eb77a32116bf61cd60290d6ca535c73bf"
STALE_OWNER_SHA256 = "45b97e99122146ec3aa95f45fe5ac71381ca1a11e83b7355438b988608f52fca"


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


LAUNCHER = load_module(LAUNCHER_PATH, "g77_256hi_fm_launcher")
OWNER = LAUNCHER.fresh_context


def git_bytes(revision: str, path: Path) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{revision}:{path.relative_to(ROOT).as_posix()}"],
        cwd=ROOT,
    )


def git_text(*arguments: str) -> str:
    return subprocess.check_output(["git", *arguments], cwd=ROOT, text=True).strip()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_unique(path: Path) -> dict[str, Any]:
    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"duplicate JSON key: {key}")
            value[key] = item
        return value

    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    assert isinstance(value, dict)
    assert raw == OWNER.canonical_bytes(value)
    return value


def build_context(tmp_path: Path) -> dict[str, Any]:
    return LAUNCHER.build_operation_context(
        repository_root=ROOT,
        repository_head=HG_HEAD,
        repository_tree=HG_TREE,
        generation_identity=(
            "G77_256HITEST_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_"
            "OPERATIONAL_COMMISSIONING_V1"
        ),
        operation_identity="G77_256HITEST_E05_WRONG_INPUT_DENIAL_BEFORE_ENTRY_001",
        identity_namespace_prefix="G77_256HITEST",
        operation_evidence_root=tmp_path / "operation_state",
        transient_root=tmp_path / "transient",
        candidate_source_path=HH_CANDIDATE.relative_to(ROOT),
    )


def materialize(context: dict[str, Any], *, head: str, tree: str) -> Path:
    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    destination = Path(checkout["path"])
    LAUNCHER.materialize_guest_self_contained_checkout(
        source_repository=ROOT,
        checkout_path=destination,
        expected_head=head,
        expected_tree=tree,
    )
    return destination


def test_hh_terminal_frontier_and_exact_owner_identities_authenticate() -> None:
    assert git_text("rev-parse", HH_HEAD + "^{tree}") == HH_TREE
    assert sha256_bytes(HH_REPORT.read_bytes()) == (
        "1aceef11dc64eaf254c52349cbf416212206afc0b8e839d2bbd51c4cb2f07948"
    )
    terminal = load_unique(HH_REDUCTION)["reduction"]
    assert terminal["terminal_branch"] == "BRANCH_B__READINESS_NOT_PROVEN"
    assert terminal["result"]["checkout_owner_sha256"] == STALE_OWNER_SHA256
    assert terminal["result"]["fm_context_owner_sha256"] == HG_OWNER_SHA256
    assert terminal["result"]["du_status"] == "PASS"
    assert terminal["result"]["eb_status"] == "PASS"
    assert terminal["result"]["ee_status"] == "PASS"
    hi = load_unique(HI_REDUCTION)
    assert hi["reduction_sha256"] == sha256_bytes(
        OWNER.canonical_bytes(hi["reduction"])
    )
    assert hi["reduction"]["terminal_control"]["terminal_branch"] == (
        "BRANCH_A__STALE_BINDING_CORRECTION_VERIFIED"
    )
    report = HI_REPORT.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    assert report.rstrip().endswith(
        "PASS__G77_256HI_CURRENT_HG_FM_CHECKOUT_OWNER_BINDING_CORRECTION_"
        "VERIFIED__POST_COMMIT_LIVE_BINDING_NOT_PROVEN__ZERO_OPERATION__"
        "E05_7_OF_18__HUMAN_REVIEW_REQUIRED"
    )


def test_exact_hg_owner_is_recomputed_from_committed_bytes() -> None:
    assert git_text("rev-parse", HG_HEAD + "^{tree}") == HG_TREE
    assert sha256_bytes(git_bytes(HG_HEAD, OWNER_PATH)) == HG_OWNER_SHA256
    assert sha256_bytes(git_bytes(STALE_HEAD, OWNER_PATH)) == STALE_OWNER_SHA256
    assert git_text("rev-parse", STALE_HEAD + "^{tree}") == STALE_TREE
    assert OWNER_PATH.read_bytes() == git_bytes(HG_HEAD, OWNER_PATH)


def test_existing_fm_context_binds_exact_hg_checkout_owner(tmp_path: Path) -> None:
    context = build_context(tmp_path)
    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    assert (checkout["head"], checkout["tree"]) == (HG_HEAD, HG_TREE)
    assert context["wrapper_fc_er_che_schema_hashes"][
        LAUNCHER.FRESH_OPERATION_CONTEXT_OWNER_HASH_KEY
    ] == HG_OWNER_SHA256
    materialize(context, head=HG_HEAD, tree=HG_TREE)
    result = LAUNCHER.prove_guest_fresh_operation_context_owner_binding(ROOT, context)
    assert result["result"] == "PREAUTH_GUEST_FM_CONTEXT_OWNER_BINDING_PASS"
    assert result["checkout_sha256"] == HG_OWNER_SHA256
    assert result["host_checkout_guest_byte_identity"] == "PASS"
    assert result["host_checkout_guest_hash_identity"] == "PASS"


def test_stale_checkout_owner_is_rejected(tmp_path: Path) -> None:
    context = build_context(tmp_path)
    materialize(context, head=STALE_HEAD, tree=STALE_TREE)
    with pytest.raises(RuntimeError, match="context owner identity mismatch"):
        LAUNCHER.prove_guest_fresh_operation_context_owner_binding(ROOT, context)


@pytest.mark.parametrize("mutation", ["wrong", "missing"])
def test_wrong_and_missing_checkout_owners_are_rejected(
    tmp_path: Path, mutation: str
) -> None:
    context = build_context(tmp_path)
    checkout = materialize(context, head=HG_HEAD, tree=HG_TREE)
    projected = checkout / LAUNCHER.FRESH_OPERATION_CONTEXT_OWNER
    if mutation == "wrong":
        projected.write_bytes(b"arbitrary-wrong-owner\n")
        pattern = "identity mismatch"
    else:
        projected.unlink()
        pattern = "absent or unsafe"
    with pytest.raises(RuntimeError, match=pattern):
        LAUNCHER.prove_guest_fresh_operation_context_owner_binding(ROOT, context)


@pytest.mark.parametrize("owner", ["z" * 64, "0" * 64, None])
def test_malformed_wrong_and_missing_context_owner_bindings_are_rejected(
    tmp_path: Path, owner: str | None
) -> None:
    context = build_context(tmp_path)
    hashes = context["wrapper_fc_er_che_schema_hashes"]
    if owner is None:
        hashes.pop(LAUNCHER.FRESH_OPERATION_CONTEXT_OWNER_HASH_KEY)
    else:
        hashes[LAUNCHER.FRESH_OPERATION_CONTEXT_OWNER_HASH_KEY] = owner
    context = OWNER.seal_context(
        {key: value for key, value in context.items() if key != "context_sha256"}
    )
    with pytest.raises(
        (RuntimeError, OWNER.ContextError),
        match="omits|immutable wrapper|SHA-256 malformed",
    ):
        LAUNCHER.validate_immutable_context_bindings(
            ROOT,
            context,
            candidate_source_path=HH_CANDIDATE.relative_to(ROOT),
        )


def test_ambiguous_multiple_owner_binding_is_structurally_rejected(
    tmp_path: Path,
) -> None:
    context = build_context(tmp_path)
    raw = OWNER.canonical_bytes(context)
    needle = (
        b'"fresh_operation_context_owner":"' + HG_OWNER_SHA256.encode() + b'",'
    )
    assert raw.count(needle) == 1
    ambiguous = raw.replace(needle, needle + needle)
    path = tmp_path / "ambiguous-context.json"
    path.write_bytes(ambiguous)
    with pytest.raises(OWNER.ContextError, match="duplicate keys"):
        OWNER.load_context(path, repository_root=ROOT)


def test_candidate_runtime_cannot_substitute_checkout_owner(tmp_path: Path) -> None:
    assert HH_CANDIDATE.read_bytes() == HH_RUNTIME.read_bytes()
    context = build_context(tmp_path)
    expectations = LAUNCHER.context_asset_expectations(
        context, HH_CANDIDATE.relative_to(ROOT)
    )
    checkout = Path(
        context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["path"]
    )
    owner_key = str(checkout / LAUNCHER.FRESH_OPERATION_CONTEXT_OWNER)
    assert expectations[owner_key] == HG_OWNER_SHA256
    assert owner_key != HH_CANDIDATE.relative_to(ROOT).as_posix()
    substituted = deepcopy(context)
    substituted["candidate_manifest_sha256"] = "0" * 64
    substituted = OWNER.seal_context(
        {key: value for key, value in substituted.items() if key != "context_sha256"}
    )
    with pytest.raises(RuntimeError, match="candidate binding mismatch"):
        LAUNCHER.validate_immutable_context_bindings(
            ROOT,
            substituted,
            candidate_source_path=HH_CANDIDATE.relative_to(ROOT),
        )


def test_wrong_input_semantics_one_route_and_zero_operation_surface() -> None:
    candidate = load_unique(HH_CANDIDATE)
    assert candidate["manifest"]["selected_case"] == {
        "case_class": "E05_NEGATIVE_AUTHORITY_WRONG_INPUT",
        "case_id": "G77_256GY_E05_WRONG_INPUT_DENIAL_BEFORE_ENTRY_001",
    }
    assert sha256_bytes(GY_REDUCER.read_bytes()) == (
        "8a6e6081118a2c1d305260555ba1ad5a11d97a5d66516f9810beb87c5c39fbf7"
    )
    tree = ast.parse(LAUNCHER_PATH.read_text(encoding="utf-8"))
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
    assert LAUNCHER.CHECKOUT_HEAD == HG_HEAD
    assert LAUNCHER.CHECKOUT_TREE == HG_TREE
