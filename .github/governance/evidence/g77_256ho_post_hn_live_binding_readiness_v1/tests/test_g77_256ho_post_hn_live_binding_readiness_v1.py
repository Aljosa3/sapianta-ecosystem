#!/usr/bin/env python3
"""Focused authority-free proofs for G77-256HO post-HN readiness."""

from __future__ import annotations

import ast
from copy import deepcopy
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
HO = ROOT / ".github/governance/evidence/g77_256ho_post_hn_live_binding_readiness_v1"
BINDER_PATH = HO / "binding/G77_256HO_POST_HN_LIVE_BINDING_V1.py"
LIVE = HO / "live_binding"
CANDIDATE = LIVE / "candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
RUNTIME = LIVE / "runtime_projection/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
CONTEXT = LIVE / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
EB_RECEIPT = LIVE / "bindings/G77_256GY_EB_RECEIPT_V1.json"
EE_RECEIPT = LIVE / "bindings/G77_256GY_EE_RECEIPT_V1.json"
REPORT = ROOT / "docs/governance/G77_256HO_POST_HN_COMMITTED_IDENTITY_LIVE_BINDING_AND_WRONG_INPUT_PREOPERATIONAL_READINESS_REAUTHENTICATION_V1.md"
TERMINAL = HO / "G77_256HO_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


BINDER = load_module(BINDER_PATH, "g77_256ho_focused_binder")
LAUNCHER = load_module(ROOT / BINDER.FM_LAUNCHER, "g77_256ho_focused_launcher")


def load_unique(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=BINDER._unique_object)
    assert isinstance(value, dict)
    assert raw == BINDER.canonical_bytes(value)
    return value


def reseal_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    value = deepcopy(candidate)
    value["manifest_sha256"] = BINDER.sha256_bytes(BINDER.canonical_bytes(value["manifest"]))
    return value


def reseal_context(context: dict[str, Any]) -> dict[str, Any]:
    value = deepcopy(context)
    value.pop("context_sha256", None)
    return LAUNCHER.fresh_context.seal_context(value)


def rejects(call: Callable[[], Any]) -> bool:
    try:
        call()
    except Exception:
        return True
    return False


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
        ["git", "clone", "--quiet", "--no-local", "--no-checkout", "--", str(ROOT), str(checkout)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, env=environment,
    )
    subprocess.run(
        ["git", "update-ref", "--no-deref", "HEAD", BINDER.EXPECTED_HG_HEAD],
        cwd=checkout, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, env=environment,
    )
    subprocess.run(
        ["git", "read-tree", "--reset", "-u", BINDER.EXPECTED_HG_HEAD],
        cwd=checkout, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, env=environment,
    )


def prepare_static_projection(context: dict[str, Any]) -> None:
    checkout = Path(context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["path"])
    materialize_hg_without_checkout_command(checkout)
    binding = context["guest_adapter_binding"]
    projection_root = Path(binding["projection_root"])
    projection_root.mkdir(mode=0o700, parents=True)
    source = ROOT / binding["source_path"]
    Path(binding["projected_path"]).write_bytes(source.read_bytes())
    Path(binding["bootstrap_projected_path"]).write_bytes(source.read_bytes())
    runtime_export = Path(context["runtime_export_root"])
    runtime_export.mkdir(mode=0o700, parents=False)
    Path(context["runtime_manifest_path"]).write_bytes(CANDIDATE.read_bytes())
    (runtime_export / LAUNCHER.fresh_context.GUEST_CONTEXT_FILENAME).write_bytes(
        LAUNCHER.fresh_context.canonical_bytes(context)
    )
    Path(context["overlay_path"]).write_bytes(b"STATIC_TEST_OVERLAY_PLACEHOLDER\n")


def test_exact_hn_entry_hm_terminal_and_nested_authority_authenticate() -> None:
    observed = BINDER.authenticate_committed_hn(ROOT)
    assert observed["head"] == BINDER.EXPECTED_HEAD
    assert observed["tree"] == BINDER.EXPECTED_TREE
    assert observed["subject"] == BINDER.EXPECTED_SUBJECT
    assert observed["parent"] == BINDER.EXPECTED_HM_HEAD
    assert observed["nested"]["head"] == BINDER.NESTED_HEAD
    assert subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True).strip() == ""


def test_current_candidate_runtime_and_fresh_du_eb_ee_bind_exact_hn() -> None:
    candidate = BINDER.build_post_hn_candidate(ROOT)
    BINDER.validate_exact_hn_rebind(load_unique(ROOT / BINDER.HM_CANDIDATE), candidate)
    assert BINDER.canonical_bytes(candidate) == CANDIDATE.read_bytes()
    assert CANDIDATE.read_bytes() == RUNTIME.read_bytes()
    assert candidate["manifest"]["required_head"] == BINDER.EXPECTED_HEAD
    assert candidate["manifest"]["source_tree"] == BINDER.EXPECTED_TREE
    gy = load_module(ROOT / BINDER.GY_BINDER, "g77_256ho_receipt_gy")
    du = load_module(ROOT / gy.DU_PATH, "g77_256ho_receipt_du")
    eb = load_module(ROOT / gy.EB_PATH, "g77_256ho_receipt_eb")
    ee = load_module(ROOT / gy.EE_PATH, "g77_256ho_receipt_ee")
    assert set(du.validate_file(CANDIDATE, ROOT, expected_head=BINDER.EXPECTED_HEAD).values()) == {"PASS"}
    assert eb.verify_receipt_file(ROOT, EB_RECEIPT)["overall_result"] == "PASS"
    assert ee.verify_receipt_file(ROOT, EE_RECEIPT)["pre_materialization_runtime_path_binding_result"] == "PASS"


def test_current_context_binds_hn_hg_fm_ha_and_corrected_bootstrap() -> None:
    context = load_unique(CONTEXT)
    BINDER.validate_current_hn_context(ROOT, context, CANDIDATE.relative_to(ROOT))
    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    assert (checkout["head"], checkout["tree"]) == (BINDER.EXPECTED_HG_HEAD, BINDER.EXPECTED_HG_TREE)
    assert context["wrapper_fc_er_che_schema_hashes"]["cloud_init"] == BINDER.HN_CLOUD_INIT_SHA256
    assert context["qemu_executable_base_seed_checkout_bindings"]["seed"]["sha256"] == BINDER.HN_SEED_SHA256
    assert context["guest_adapter_binding"]["source_sha256"] == BINDER.ACTIVE_ADAPTER_SHA256
    assert context["candidate_manifest_sha256"] == BINDER.sha256_path(CANDIDATE)


@pytest.mark.parametrize(
    "mutation",
    ("HM_HEAD", "HM_TREE", "STALE_FM", "MALFORMED_IDENTITY", "MISSING_IDENTITY", "AMBIGUOUS_IDENTITY"),
)
def test_candidate_stale_wrong_missing_malformed_and_ambiguous_identities_reject(mutation: str) -> None:
    reference = load_unique(ROOT / BINDER.HM_CANDIDATE)
    candidate = deepcopy(BINDER.build_post_hn_candidate(ROOT))
    if mutation == "HM_HEAD":
        candidate["manifest"]["required_head"] = BINDER.EXPECTED_HM_HEAD
    elif mutation == "HM_TREE":
        candidate["manifest"]["source_tree"] = BINDER.EXPECTED_HM_TREE
    elif mutation == "STALE_FM":
        candidate["manifest"]["extension_bindings"][5]["sha256"] = reference["manifest"]["extension_bindings"][5]["sha256"]
    elif mutation == "MALFORMED_IDENTITY":
        candidate["manifest"]["required_head"] = "malformed"
    elif mutation == "MISSING_IDENTITY":
        candidate["manifest"].pop("required_head")
    else:
        candidate["manifest"]["ambiguous_identity"] = BINDER.EXPECTED_HEAD
    candidate = reseal_candidate(candidate)
    assert rejects(lambda: BINDER.validate_exact_hn_rebind(reference, candidate))


@pytest.mark.parametrize(
    "mutation",
    ("HEAD", "TREE", "CLOUD_INIT", "SEED", "ADAPTER", "CONTEXT_OWNER", "CHECKOUT_HEAD", "CHECKOUT_TREE", "CANDIDATE"),
)
def test_context_stale_wrong_and_mismatched_bindings_reject(mutation: str) -> None:
    context = deepcopy(load_unique(CONTEXT))
    if mutation == "HEAD":
        context["repository_head"] = BINDER.EXPECTED_HM_HEAD
    elif mutation == "TREE":
        context["repository_tree"] = BINDER.EXPECTED_HM_TREE
    elif mutation == "CLOUD_INIT":
        context["wrapper_fc_er_che_schema_hashes"]["cloud_init"] = "0" * 64
    elif mutation == "SEED":
        context["qemu_executable_base_seed_checkout_bindings"]["seed"]["sha256"] = "0" * 64
    elif mutation == "ADAPTER":
        context["guest_adapter_binding"]["source_sha256"] = "0" * 64
    elif mutation == "CONTEXT_OWNER":
        context["wrapper_fc_er_che_schema_hashes"][LAUNCHER.FRESH_OPERATION_CONTEXT_OWNER_HASH_KEY] = "0" * 64
    elif mutation == "CHECKOUT_HEAD":
        context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["head"] = BINDER.EXPECTED_HM_HEAD
    elif mutation == "CHECKOUT_TREE":
        context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["tree"] = BINDER.EXPECTED_HM_TREE
    else:
        context["candidate_manifest_sha256"] = "0" * 64
    context = reseal_context(context)
    assert rejects(lambda: BINDER.validate_current_hn_context(ROOT, context, CANDIDATE.relative_to(ROOT)))


def test_candidate_runtime_and_bootstrap_adapter_mismatch_reject() -> None:
    runtime = bytearray(RUNTIME.read_bytes())
    runtime[-2] = ord(" ")
    assert bytes(runtime) != CANDIDATE.read_bytes()
    cloud = (ROOT / BINDER.HN_CLOUD_INIT).read_text(encoding="utf-8")
    binding = load_unique(CONTEXT)["guest_adapter_binding"]
    arguments = LAUNCHER.bootstrap_guest_command_arguments(cloud, binding["bootstrap_guest_path"])
    assert arguments[0] == BINDER.ACTIVE_ADAPTER_SHA256
    assert arguments[0] != BINDER.HISTORICAL_FM_WRAPPER_SHA256
    stale = cloud.replace(BINDER.ACTIVE_ADAPTER_SHA256, BINDER.HISTORICAL_FM_WRAPPER_SHA256)
    assert LAUNCHER.bootstrap_guest_command_arguments(stale, binding["bootstrap_guest_path"])[0] != binding["source_sha256"]


def test_active_projected_adapter_and_hn_seed_binding_passes_before_authority(tmp_path: Path) -> None:
    context = BINDER.build_post_hn_context(
        repository_root=ROOT, candidate_path=CANDIDATE,
        operation_root=tmp_path / "operation_state", transient_root=tmp_path / "transient",
    )
    prepare_static_projection(context)
    observations = LAUNCHER.observe_context_assets(ROOT, context, CANDIDATE.relative_to(ROOT))
    result = LAUNCHER.authority_free_static_readiness(
        repository_root=ROOT, context=context, observed_head=BINDER.EXPECTED_HEAD,
        observed_tree=BINDER.EXPECTED_TREE, repository_clean=True,
        observed_asset_sha256=observations, candidate_source_path=CANDIDATE.relative_to(ROOT),
    )
    assert result["result"] == "STATIC_READINESS_PASS"
    assert result["human_operational_authorization_count"] == 0
    assert result["qemu_execution_count"] == 0
    assert result["guest_adapter_binding"]["result"] == "PREAUTHORITY_GUEST_ADAPTER_BINDING_PASS"
    assert result["guest_adapter_binding"]["source_sha256"] == BINDER.ACTIVE_ADAPTER_SHA256


def test_wrong_attempt_pair_and_wrong_input_semantic_firewall_are_preserved() -> None:
    assert LAUNCHER.current_bootstrap_asset_bindings(LAUNCHER.fresh_context.WRONG_INPUT) == {
        "cloud_init_path": BINDER.HN_CLOUD_INIT.as_posix(),
        "cloud_init_sha256": BINDER.HN_CLOUD_INIT_SHA256,
        "seed_path": str((ROOT / BINDER.HN_SEED).resolve()),
        "seed_sha256": BINDER.HN_SEED_SHA256,
    }
    wrong_attempt = LAUNCHER.current_bootstrap_asset_bindings(LAUNCHER.fresh_context.WRONG_ATTEMPT)
    assert "g77_256hk_current_hg_bootstrap_binding_v1" in wrong_attempt["cloud_init_path"]
    assert BINDER.sha256_path(ROOT / BINDER.GY_PRODUCER) == BINDER.GY_PRODUCER_SHA256
    assert BINDER.sha256_path(ROOT / BINDER.GY_REDUCER) == BINDER.GY_REDUCER_SHA256
    assert BINDER.TARGET_MUTATION == "input_identity"
    assert BINDER.DEPENDENT_RECOMPUTATION == "record_identity"
    assert BINDER.SEMANTIC_MUTATION_COUNT == 1


def test_single_fm_route_and_no_operational_entrypoint_or_authority_construction() -> None:
    tree = ast.parse(BINDER_PATH.read_text(encoding="utf-8"))
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
    prohibited = {"Popen", "run_qemu_once", "launch_once", "invoke_pre", "request_authority", "consume_authority"}
    assert not any(isinstance(call.func, ast.Name) and call.func.id in prohibited for call in calls)
    assert sum(path.name == "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py" for path in ROOT.rglob("G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py")) == 1
    source = BINDER_PATH.read_text(encoding="utf-8")
    assert "qemu-system" not in source
    assert "subprocess.Popen" not in source


def test_terminal_reduction_and_g48_report_are_canonical_and_exactly_six_sections() -> None:
    terminal = load_unique(TERMINAL)["reduction"]
    assert terminal["readiness"]["terminal_branch"] == "BRANCH_A__READINESS_VERIFIED"
    assert terminal["du_eb_ee"] == {"current_du_status": "PASS", "current_eb_status": "PASS", "current_ee_status": "PASS"}
    assert set(terminal["operational_counters"].values()) == {0}
    headings = [line for line in REPORT.read_text(encoding="utf-8").splitlines() if line.startswith("# ")]
    assert headings == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
