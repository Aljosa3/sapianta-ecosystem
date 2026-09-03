#!/usr/bin/env python3
"""Focused authority-free proofs for G77-256HL post-HK readiness."""

from __future__ import annotations

from copy import deepcopy
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
HL = ROOT / ".github/governance/evidence/g77_256hl_post_hk_live_binding_readiness_v1"
BINDER_PATH = HL / "binding/G77_256HL_POST_HK_LIVE_BINDING_V1.py"
LIVE = HL / "live_binding"
CANDIDATE = LIVE / "candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
RUNTIME = LIVE / "runtime_projection/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
EB_RECEIPT = LIVE / "bindings/G77_256GY_EB_RECEIPT_V1.json"
EE_RECEIPT = LIVE / "bindings/G77_256GY_EE_RECEIPT_V1.json"
EE_HARNESS = LIVE / "bindings/G77_256GY_EE_PATH_PROJECTION_FIXTURE_V1.py"
CONTEXT = LIVE / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
TERMINAL = HL / "G77_256HL_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = ROOT / (
    "docs/governance/G77_256HL_POST_HK_COMMITTED_IDENTITY_LIVE_BINDING_AND_"
    "PREOPERATIONAL_READINESS_REAUTHENTICATION_V1.md"
)
HJ_LIVE = ROOT / ".github/governance/evidence/g77_256hj_post_hi_live_binding_readiness_v1/live_binding"
HJ_CANDIDATE = HJ_LIVE / "candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
HJ_EB = HJ_LIVE / "bindings/G77_256GY_EB_RECEIPT_V1.json"
HJ_EE = HJ_LIVE / "bindings/G77_256GY_EE_RECEIPT_V1.json"
HD_SEED = ROOT / (
    ".github/governance/evidence/g77_256hd_guest_context_owner_binding_v1/static/"
    "SAPIANTA_WRONG_ATTEMPT_NOCLOUD_SEED_V1.img"
)
HD_CLOUD_INIT = ROOT / (
    ".github/governance/evidence/g77_256hd_guest_context_owner_binding_v1/static/"
    "G77_256HD_CLOUD_INIT_USER_DATA_V1.yaml"
)


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


BINDER = load_module(BINDER_PATH, "g77_256hl_focused_binder")
LAUNCHER = load_module(ROOT / BINDER.FM_LAUNCHER, "g77_256hl_focused_launcher")
OWNER = LAUNCHER.fresh_context


def load_unique(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=BINDER._unique_object)
    assert isinstance(value, dict)
    assert raw == BINDER.canonical_bytes(value)
    return value


def reseal(context: dict[str, Any]) -> dict[str, Any]:
    value = deepcopy(context)
    value.pop("context_sha256", None)
    return OWNER.seal_context(value)


def build_context(tmp_path: Path) -> dict[str, Any]:
    return BINDER.build_post_hk_context(
        repository_root=ROOT,
        candidate_path=CANDIDATE,
        operation_root=tmp_path / "operation_state",
        transient_root=tmp_path / "transient",
    )


def project_adapter(context: dict[str, Any]) -> None:
    binding = context["guest_adapter_binding"]
    projection_root = Path(binding["projection_root"])
    projection_root.mkdir(mode=0o700, parents=True, exist_ok=True)
    source_bytes = (ROOT / binding["source_path"]).read_bytes()
    Path(binding["projected_path"]).write_bytes(source_bytes)
    Path(binding["bootstrap_projected_path"]).write_bytes(source_bytes)


def materialize_hg_without_checkout_command(checkout: Path) -> None:
    """Create a detached static fixture without invoking prohibited checkout."""

    checkout.parent.mkdir(mode=0o700, parents=True)
    environment = os.environ.copy()
    for name in tuple(environment):
        if name.startswith("GIT_"):
            environment.pop(name)
    environment["GIT_CONFIG_NOSYSTEM"] = "1"
    environment["GIT_CONFIG_GLOBAL"] = os.devnull
    subprocess.run(
        [
            "git", "clone", "--quiet", "--no-local", "--no-checkout", "--",
            str(ROOT), str(checkout),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        env=environment,
    )
    subprocess.run(
        ["git", "update-ref", "--no-deref", "HEAD", BINDER.EXPECTED_HG_HEAD],
        cwd=checkout,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        env=environment,
    )
    subprocess.run(
        ["git", "read-tree", "--reset", "-u", BINDER.EXPECTED_HG_HEAD],
        cwd=checkout,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        env=environment,
    )


def prepare_static_projection(context: dict[str, Any]) -> None:
    checkout = Path(
        context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["path"]
    )
    materialize_hg_without_checkout_command(checkout)
    project_adapter(context)
    runtime_export = Path(context["runtime_export_root"])
    runtime_export.mkdir(mode=0o700, parents=False)
    Path(context["runtime_manifest_path"]).write_bytes(CANDIDATE.read_bytes())
    (runtime_export / OWNER.GUEST_CONTEXT_FILENAME).write_bytes(
        OWNER.canonical_bytes(context)
    )
    Path(context["overlay_path"]).write_bytes(b"STATIC_TEST_OVERLAY_PLACEHOLDER\n")


def rejects(call: Callable[[], Any]) -> bool:
    try:
        call()
    except Exception:
        return True
    return False


def test_exact_committed_hk_branch_a_and_assets_are_authenticated() -> None:
    observed = BINDER.authenticate_committed_hk(ROOT)
    assert observed["head"] == BINDER.EXPECTED_HEAD
    assert observed["tree"] == BINDER.EXPECTED_TREE
    assert observed["subject"] == BINDER.EXPECTED_SUBJECT
    assert observed["fm_launcher_sha256"] == BINDER.FM_LAUNCHER_SHA256
    assert observed["cloud_init_sha256"] == BINDER.HK_CLOUD_INIT_SHA256
    assert observed["seed_sha256"] == BINDER.HK_SEED_SHA256
    assert subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True
    ).strip() == ""


def test_current_candidate_runtime_context_and_receipts_bind_exact_hk() -> None:
    candidate = BINDER.build_post_hk_candidate(ROOT)
    BINDER.validate_exact_hk_rebind(BINDER.load_canonical(HJ_CANDIDATE), candidate)
    assert BINDER.canonical_bytes(candidate) == CANDIDATE.read_bytes()
    assert CANDIDATE.read_bytes() == RUNTIME.read_bytes()
    assert candidate["manifest"]["required_head"] == BINDER.EXPECTED_HEAD
    assert candidate["manifest"]["source_tree"] == BINDER.EXPECTED_TREE
    context = load_unique(CONTEXT)
    assert context["repository_head"] == BINDER.EXPECTED_HEAD
    assert context["repository_tree"] == BINDER.EXPECTED_TREE
    assert context["candidate_manifest_sha256"] == BINDER.sha256_path(CANDIDATE)
    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    assert (checkout["head"], checkout["tree"]) == (
        BINDER.EXPECTED_HG_HEAD, BINDER.EXPECTED_HG_TREE
    )
    assert context["qemu_executable_base_seed_checkout_bindings"]["seed"]["sha256"] == BINDER.HK_SEED_SHA256
    assert context["wrapper_fc_er_che_schema_hashes"]["cloud_init"] == BINDER.HK_CLOUD_INIT_SHA256
    gy = load_module(ROOT / BINDER.GY_BINDER, "g77_256hl_receipt_gy")
    du = load_module(ROOT / gy.DU_PATH, "g77_256hl_receipt_du")
    eb = load_module(ROOT / gy.EB_PATH, "g77_256hl_receipt_eb")
    ee = load_module(ROOT / gy.EE_PATH, "g77_256hl_receipt_ee")
    assert set(du.validate_file(CANDIDATE, ROOT, expected_head=BINDER.EXPECTED_HEAD).values()) == {"PASS"}
    assert eb.verify_receipt_file(ROOT, EB_RECEIPT)["overall_result"] == "PASS"
    assert ee.verify_receipt_file(ROOT, EE_RECEIPT)["pre_materialization_runtime_path_binding_result"] == "PASS"


@pytest.mark.parametrize("mutation", ("HEAD", "TREE", "LAUNCHER", "CASE", "EXTRA", "BAD_SEAL"))
def test_exact_hk_rebind_firewall_rejects_all_other_drift(mutation: str) -> None:
    reference = BINDER.load_canonical(HJ_CANDIDATE)
    candidate = deepcopy(BINDER.build_post_hk_candidate(ROOT))
    if mutation == "HEAD":
        candidate["manifest"]["required_head"] = "0" * 40
    elif mutation == "TREE":
        candidate["manifest"]["source_tree"] = "0" * 40
    elif mutation == "LAUNCHER":
        candidate["manifest"]["extension_bindings"][5]["sha256"] = "0" * 64
    elif mutation == "CASE":
        candidate["manifest"]["selected_case"]["case_class"] = "E05_NEGATIVE_AUTHORITY_WRONG_ATTEMPT"
    elif mutation == "EXTRA":
        candidate["manifest"]["unexpected"] = True
    else:
        candidate["manifest_sha256"] = "0" * 64
    if mutation != "BAD_SEAL":
        candidate["manifest_sha256"] = hashlib.sha256(
            BINDER.canonical_bytes(candidate["manifest"])
        ).hexdigest()
    with pytest.raises(BINDER.PostHKBindingError):
        BINDER.validate_exact_hk_rebind(reference, candidate)


def test_full_authority_free_static_readiness_passes(tmp_path: Path) -> None:
    context = build_context(tmp_path)
    prepare_static_projection(context)
    observations = LAUNCHER.observe_context_assets(
        ROOT, context, CANDIDATE.relative_to(ROOT)
    )
    result = LAUNCHER.authority_free_static_readiness(
        repository_root=ROOT,
        context=context,
        observed_head=BINDER.EXPECTED_HEAD,
        observed_tree=BINDER.EXPECTED_TREE,
        repository_clean=True,
        observed_asset_sha256=observations,
        candidate_source_path=CANDIDATE.relative_to(ROOT),
    )
    assert result["result"] == "STATIC_READINESS_PASS"
    assert result["human_operational_authorization_count"] == 0
    assert result["qemu_execution_count"] == 0
    assert result["guest_adapter_binding"]["result"] == "PREAUTHORITY_GUEST_ADAPTER_BINDING_PASS"
    assert result["guest_adapter_binding"]["nocloud_seed_sha256"] == BINDER.HK_SEED_SHA256


def test_complete_current_preauthorization_negative_matrix(tmp_path: Path) -> None:
    context = load_unique(CONTEXT)
    candidate_relative = CANDIDATE.relative_to(ROOT)
    reference = BINDER.load_canonical(HJ_CANDIDATE)
    gy = load_module(ROOT / BINDER.GY_BINDER, "g77_256hl_negative_gy")
    du = load_module(ROOT / gy.DU_PATH, "g77_256hl_negative_du")
    eb = load_module(ROOT / gy.EB_PATH, "g77_256hl_negative_eb")
    ee = load_module(ROOT / gy.EE_PATH, "g77_256hl_negative_ee")
    results: dict[str, bool] = {}

    results["MISSING_CURRENT_CANDIDATE"] = rejects(lambda: LAUNCHER.validate_immutable_context_bindings(ROOT, context, Path("missing/current/candidate.json")))
    wrong_candidate = reseal(context | {"candidate_manifest_sha256": "0" * 64})
    results["WRONG_CANDIDATE_IDENTITY"] = rejects(lambda: LAUNCHER.validate_immutable_context_bindings(ROOT, wrong_candidate, candidate_relative))

    for label, launcher_hash in (("STALE_LAUNCHER_IDENTITY", reference["manifest"]["extension_bindings"][5]["sha256"]), ("WRONG_LAUNCHER_IDENTITY", "0" * 64)):
        value = deepcopy(BINDER.build_post_hk_candidate(ROOT))
        value["manifest"]["extension_bindings"][5]["sha256"] = launcher_hash
        value["manifest_sha256"] = hashlib.sha256(BINDER.canonical_bytes(value["manifest"])).hexdigest()
        results[label] = rejects(lambda value=value: BINDER.validate_exact_hk_rebind(reference, value))

    results["MISSING_CURRENT_CONTEXT"] = rejects(lambda: OWNER.load_context(tmp_path / "missing-context.json", repository_root=ROOT))
    wrong_context = deepcopy(context)
    wrong_context["repository_head"] = "0" * 40
    wrong_context = reseal(wrong_context)
    results["WRONG_CONTEXT_IDENTITY"] = rejects(lambda: BINDER.validate_current_hk_context(ROOT, wrong_context, candidate_relative))

    mixed_checkout = deepcopy(context)
    mixed_checkout["qemu_executable_base_seed_checkout_bindings"]["checkout"]["tree"] = "0" * 40
    mixed_checkout = reseal(mixed_checkout)
    results["MIXED_CHECKOUT_HEAD_TREE"] = rejects(lambda: LAUNCHER.validate_immutable_context_bindings(ROOT, mixed_checkout, candidate_relative))

    for label, seed_path, seed_hash, cloud_hash in (
        ("STALE_BOOTSTRAP_PAIR", HD_SEED, hashlib.sha256(HD_SEED.read_bytes()).hexdigest(), hashlib.sha256(HD_CLOUD_INIT.read_bytes()).hexdigest()),
        ("WRONG_BOOTSTRAP_PAIR", ROOT / "wrong-seed.img", "0" * 64, "1" * 64),
    ):
        value = deepcopy(context)
        value["qemu_executable_base_seed_checkout_bindings"]["seed"] = {"path": str(seed_path), "sha256": seed_hash}
        value["wrapper_fc_er_che_schema_hashes"]["cloud_init"] = cloud_hash
        value = reseal(value)
        results[label] = rejects(lambda value=value: LAUNCHER.validate_immutable_context_bindings(ROOT, value, candidate_relative))

    mixed_bootstrap = deepcopy(context)
    mixed_bootstrap["qemu_executable_base_seed_checkout_bindings"]["checkout"]["head"] = BINDER.EXPECTED_HG_HEAD
    mixed_bootstrap["qemu_executable_base_seed_checkout_bindings"]["checkout"]["tree"] = "1" * 40
    mixed_bootstrap = reseal(mixed_bootstrap)
    project_adapter(mixed_bootstrap)
    results["MIXED_BOOTSTRAP_HEAD_TREE"] = rejects(lambda: LAUNCHER.prove_guest_adapter_binding(ROOT, mixed_bootstrap))

    invalid_projection = deepcopy(context)
    invalid_projection["qemu_executable_base_seed_checkout_bindings"]["checkout"]["path"] = str(tmp_path / "wrong-checkout")
    invalid_projection = reseal(invalid_projection)
    results["INVALID_GUEST_PROJECTION"] = rejects(lambda: LAUNCHER.validate_immutable_context_bindings(ROOT, invalid_projection, candidate_relative))

    results["MISSING_DU"] = rejects(lambda: du.validate_file(tmp_path / "missing-du.json", ROOT, expected_head=BINDER.EXPECTED_HEAD))
    results["STALE_DU"] = rejects(lambda: du.validate_file(HJ_CANDIDATE, ROOT, expected_head=BINDER.EXPECTED_HEAD))
    results["MISSING_EB"] = rejects(lambda: eb.verify_receipt_file(ROOT, tmp_path / "missing-eb.json"))
    results["STALE_EB"] = rejects(lambda: eb.validate_candidate(ROOT, HJ_CANDIDATE, required_head=BINDER.EXPECTED_HEAD, required_tree=BINDER.EXPECTED_TREE))
    results["MISSING_EE"] = rejects(lambda: ee.verify_receipt_file(ROOT, tmp_path / "missing-ee.json"))
    results["STALE_EE"] = rejects(lambda: ee.validate_binding(ROOT, CANDIDATE, HJ_EB, EE_HARNESS, RUNTIME.parent, "/mnt/g77-evidence", required_head=BINDER.EXPECTED_HEAD, required_tree=BINDER.EXPECTED_TREE))

    scratch = HL / f"negative_matrix_{tmp_path.name}"
    scratch.mkdir()
    try:
        runtime_root = scratch / "runtime"
        runtime_root.mkdir()
        bad_runtime = runtime_root / CANDIDATE.name
        bad_runtime.write_bytes(CANDIDATE.read_bytes() + b"\n")
        results["CANDIDATE_RUNTIME_MISMATCH"] = rejects(lambda: ee.validate_binding(ROOT, CANDIDATE, EB_RECEIPT, EE_HARNESS, runtime_root, "/mnt/g77-evidence", required_head=BINDER.EXPECTED_HEAD, required_tree=BINDER.EXPECTED_TREE))
    finally:
        bad_runtime.unlink(missing_ok=True)
        runtime_root.rmdir()
        scratch.rmdir()

    authority_substitution = deepcopy(context)
    authority_substitution["authorization"] = {"checkout_head": "2" * 40, "checkout_tree": "3" * 40}
    results["AUTHORITY_SUBSTITUTION_ATTEMPT"] = rejects(lambda: OWNER.validate_context(authority_substitution, repository_root=ROOT))

    duplicate = tmp_path / "duplicate.json"
    duplicate.write_bytes(b'{"owner":"a","owner":"b"}\n')
    results["DUPLICATE_JSON_KEY"] = rejects(lambda: BINDER.load_canonical(duplicate))

    owner_context = build_context(tmp_path / "owners")
    prepare_static_projection(owner_context)
    projected_owner = Path(owner_context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["path"]) / BINDER.FM_CONTEXT_OWNER
    correct = projected_owner.read_bytes()
    projected_owner.write_bytes(b"wrong owner\n")
    results["WRONG_CHECKOUT_OWNER"] = rejects(lambda: LAUNCHER.prove_guest_fresh_operation_context_owner_binding(ROOT, owner_context))
    stale = subprocess.check_output(["git", "show", "a5fde262c8833922375a10e79c745c0ff19e698e:" + BINDER.FM_CONTEXT_OWNER.as_posix()], cwd=ROOT)
    projected_owner.write_bytes(stale)
    results["STALE_CHECKOUT_OWNER"] = rejects(lambda: LAUNCHER.prove_guest_fresh_operation_context_owner_binding(ROOT, owner_context))
    projected_owner.write_bytes(correct)

    expected = set(load_unique(TERMINAL)["reduction"]["preauthorization_negative_matrix"]["cases"])
    assert set(results) == expected
    assert len(results) == 22
    assert {label for label, rejected in results.items() if not rejected} == set()


def test_projection_semantic_firewall_single_route_and_terminal_reduction() -> None:
    launcher_source = (ROOT / BINDER.FM_LAUNCHER).read_text(encoding="utf-8")
    tree = ast.parse(launcher_source)
    mains = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main"]
    qemu_calls = [node for node in ast.walk(mains[0]) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == "subprocess" and node.func.attr == "run"]
    assert len(mains) == len(qemu_calls) == 1
    assert "input_identity" not in launcher_source
    assert BINDER.sha256_path(ROOT / BINDER.GY_REDUCER) == "8a6e6081118a2c1d305260555ba1ad5a11d97a5d66516f9810beb87c5c39fbf7"
    envelope = load_unique(TERMINAL)
    reduction = envelope["reduction"]
    assert hashlib.sha256(BINDER.canonical_bytes(reduction)).hexdigest() == envelope["reduction_sha256"]
    assert reduction["readiness"]["terminal_branch"] == "BRANCH_A__FULL_POST_HK_PREOPERATIONAL_READINESS_VERIFIED"
    assert reduction["readiness"]["next_operational_generation_eligible"] == "VERIFIED"
    assert reduction["capability_boundary"]["wrong_input_operational_capability"] == "NOT_PROVEN"
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"]["before"] == reduction["e05"]["after"] == "7/18"


def test_g48_exact_six_headings_and_terminal_control() -> None:
    reduction = load_unique(TERMINAL)["reduction"]
    report = REPORT.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    assert report.rstrip().endswith(reduction["terminal_control"]["verdict"])
    assert report.count("Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?") == 1
    assert report.count("| `PREVIOUS_WORKER_CONVERSATION_REQUIRED` |") == 1
    assert "AUTO_CONTINUABLE = NO" in report
    assert "HUMAN_REVIEW_REQUIRED = YES" in report
