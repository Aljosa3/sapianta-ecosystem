#!/usr/bin/env python3
"""Repository-only proof of the current-HG WRONG_INPUT bootstrap binding."""

from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
HK = ROOT / (
    ".github/governance/evidence/"
    "g77_256hk_current_hg_bootstrap_binding_v1"
)
HK_CLOUD_INIT = HK / "static/G77_256HK_CLOUD_INIT_USER_DATA_V1.yaml"
HK_SEED = HK / "static/SAPIANTA_WRONG_ATTEMPT_NOCLOUD_SEED_V1.img"
HD = ROOT / ".github/governance/evidence/g77_256hd_guest_context_owner_binding_v1"
HD_CLOUD_INIT = HD / "static/G77_256HD_CLOUD_INIT_USER_DATA_V1.yaml"
HD_SEED = HD / "static/SAPIANTA_WRONG_ATTEMPT_NOCLOUD_SEED_V1.img"
FM = ROOT / ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1"
LAUNCHER_PATH = FM / "launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
OWNER_PATH = FM / "launcher/sapianta_fresh_operation_context_v1.py"
META_DATA = FM / "raw/G77_256FM_CLOUD_INIT_META_DATA_V1.yaml"
NETWORK_CONFIG = FM / "raw/G77_256FM_CLOUD_INIT_NETWORK_CONFIG_V1.yaml"
HJ = ROOT / ".github/governance/evidence/g77_256hj_post_hi_live_binding_readiness_v1"
HJ_CANDIDATE = HJ / (
    "live_binding/candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
)
HJ_REDUCTION = HJ / "G77_256HJ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
HK_REDUCTION = HK / "G77_256HK_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
HK_REPORT = ROOT / (
    "docs/governance/G77_256HK_CURRENT_HG_WRONG_INPUT_GUEST_BOOTSTRAP_"
    "CHECKOUT_ARGUMENT_BINDING_CORRECTION_V1.md"
)
GY_REDUCER = ROOT / (
    ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/"
    "reducer/G77_256GY_WRONG_INPUT_TERMINAL_ACCEPTANCE_REDUCER_V1.py"
)
HA_ADAPTER = ROOT / (
    ".github/governance/evidence/g77_256ha_wrong_input_route_binding_v1/"
    "adapter/G77_256HA_WRONG_INPUT_VECTOR_ADAPTER_V1.py"
)

HJ_HEAD = "0977c05efaab001eb5d3f15e17c3f180158b722c"
HJ_TREE = "35197458a1a5cba0fdbfe32d1ee6e54bdd0cf862"
STALE_HEAD = "a5fde262c8833922375a10e79c745c0ff19e698e"
STALE_TREE = "c265719bc048a9ab686e290d1952280d5584a43e"
HG_HEAD = "842a0f2cccd53222d11daa698bdeab17f0aac043"
HG_TREE = "414a5f940e3b5027b6dd86c38d7a134f5c8ab0c4"
HK_CLOUD_INIT_SHA256 = (
    "f10425de141e2f790b4b57fe00aa59c345aeb4e2c0e58e3a2b57cbaf602ff666"
)
HK_SEED_SHA256 = (
    "6346b9f02b236d71f2698b01a0d607549ad4d9d779a72b5168658994c519913d"
)
HD_CLOUD_INIT_SHA256 = (
    "95038a31879b3654607ae82533e9b043fee47e7cc157efdad1b7654a11664421"
)
HD_SEED_SHA256 = (
    "15910599577a84545d79d49383747ce22e630d1cb3f1228509b307487a2261cf"
)


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


LAUNCHER = load_module(LAUNCHER_PATH, "g77_256hk_fm_launcher")
OWNER = LAUNCHER.fresh_context


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


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
        repository_head=HJ_HEAD,
        repository_tree=HJ_TREE,
        generation_identity=(
            "G77_256HK_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_"
            "OPERATIONAL_COMMISSIONING_V1"
        ),
        operation_identity="G77_256HK_E05_WRONG_INPUT_DENIAL_BEFORE_ENTRY_001",
        identity_namespace_prefix="G77_256HK",
        operation_evidence_root=tmp_path / "operation_state",
        transient_root=tmp_path / "transient",
        candidate_source_path=HJ_CANDIDATE.relative_to(ROOT),
    )


def reseal(context: dict[str, Any]) -> dict[str, Any]:
    value = deepcopy(context)
    value.pop("context_sha256", None)
    return OWNER.seal_context(value)


def project_adapter(context: dict[str, Any]) -> None:
    binding = context["guest_adapter_binding"]
    projection_root = Path(binding["projection_root"])
    projection_root.mkdir(mode=0o700, parents=True)
    source_bytes = (ROOT / binding["source_path"]).read_bytes()
    Path(binding["projected_path"]).write_bytes(source_bytes)
    Path(binding["bootstrap_projected_path"]).write_bytes(source_bytes)


def materialize_hg_without_checkout_command(checkout: Path) -> None:
    """Create a detached test checkout without invoking prohibited git checkout."""

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
        ["git", "update-ref", "--no-deref", "HEAD", HG_HEAD],
        cwd=checkout,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        env=environment,
    )
    subprocess.run(
        ["git", "read-tree", "--reset", "-u", HG_HEAD],
        cwd=checkout,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        env=environment,
    )
    assert git("rev-parse", "HEAD", cwd=checkout) == HG_HEAD
    assert git("rev-parse", "HEAD^{tree}", cwd=checkout) == HG_TREE
    assert git("status", "--porcelain", cwd=checkout) == ""


def prepare_static_projection(context: dict[str, Any]) -> None:
    checkout = Path(
        context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["path"]
    )
    materialize_hg_without_checkout_command(checkout)
    project_adapter(context)
    runtime_export = Path(context["runtime_export_root"])
    runtime_export.mkdir(mode=0o700, parents=False)
    Path(context["runtime_manifest_path"]).write_bytes(HJ_CANDIDATE.read_bytes())
    (runtime_export / OWNER.GUEST_CONTEXT_FILENAME).write_bytes(
        OWNER.canonical_bytes(context)
    )
    Path(context["overlay_path"]).write_bytes(b"STATIC_TEST_OVERLAY_PLACEHOLDER\n")


def test_hj_frontier_and_all_four_checkout_identities_authenticate() -> None:
    assert git("rev-parse", HJ_HEAD + "^{tree}") == HJ_TREE
    assert git("rev-parse", STALE_HEAD + "^{tree}") == STALE_TREE
    assert git("rev-parse", HG_HEAD + "^{tree}") == HG_TREE
    reduction = load_unique(HJ_REDUCTION)["reduction"]
    assert reduction["readiness"]["terminal_branch"] == (
        "BRANCH_B__READINESS_NOT_PROVEN"
    )
    assert reduction["readiness"]["last_verified_edge"] == (
        "POST_HI_CANDIDATE_CONTEXT_DU_EB_EE_AND_EXACT_HG_CHECKOUT_OWNER_BINDING"
    )
    assert reduction["readiness"]["first_broken_edge"] == (
        "WRONG_INPUT_AUTHORITY_FREE_STATIC_READINESS_REJECTS_HD_CLOUD_INIT_"
        "PRE_HG_CHECKOUT_ARGUMENT_BINDING"
    )


def test_current_bootstrap_pair_is_exact_and_historical_hd_is_immutable() -> None:
    assert sha256_path(HK_CLOUD_INIT) == LAUNCHER.CLOUD_INIT_SHA256 == (
        HK_CLOUD_INIT_SHA256
    )
    assert sha256_path(HK_SEED) == LAUNCHER.EXPECTED_ASSET_SHA256[LAUNCHER.SEED] == (
        HK_SEED_SHA256
    )
    assert sha256_path(HD_CLOUD_INIT) == HD_CLOUD_INIT_SHA256
    assert sha256_path(HD_SEED) == HD_SEED_SHA256
    assert git("diff", "--name-only", "HEAD", "--", str(HD.relative_to(ROOT))) == ""
    current = HK_CLOUD_INIT.read_text(encoding="utf-8")
    historical = HD_CLOUD_INIT.read_text(encoding="utf-8")
    assert current.replace(HG_HEAD, STALE_HEAD).replace(HG_TREE, STALE_TREE) == (
        historical
    )
    assert current.count(HG_HEAD) == current.count(HG_TREE) == 1
    assert STALE_HEAD not in current and STALE_TREE not in current


def test_nocloud_seed_projects_exact_current_sources() -> None:
    for member, source in {
        "/user-data": HK_CLOUD_INIT,
        "/meta-data": META_DATA,
        "/network-config": NETWORK_CONFIG,
    }.items():
        projected = subprocess.check_output(
            ["isoinfo", "-i", str(HK_SEED), "-R", "-x", member]
        )
        assert projected == source.read_bytes()


def test_exact_current_hg_bootstrap_binding_is_accepted(tmp_path: Path) -> None:
    context = build_context(tmp_path)
    project_adapter(context)
    result = LAUNCHER.prove_guest_adapter_binding(ROOT, context)
    assert result["result"] == "PREAUTHORITY_GUEST_ADAPTER_BINDING_PASS"
    assert result["nocloud_seed_sha256"] == HK_SEED_SHA256
    assert result["nocloud_source_projection_identity"] == "PASS"
    assert context["qemu_executable_base_seed_checkout_bindings"]["checkout"][
        "head"
    ] == HG_HEAD
    assert context["qemu_executable_base_seed_checkout_bindings"]["checkout"][
        "tree"
    ] == HG_TREE


@pytest.mark.parametrize(
    ("mutation", "value"),
    (
        ("head", STALE_HEAD),
        ("tree", STALE_TREE),
        ("both", None),
        ("head", "0" * 40),
        ("tree", "1" * 40),
        ("missing_head", None),
        ("missing_tree", None),
        ("head", "malformed"),
        ("tree", "malformed"),
    ),
)
def test_wrong_missing_and_malformed_bootstrap_bindings_are_rejected(
    tmp_path: Path, mutation: str, value: str | None
) -> None:
    context = build_context(tmp_path)
    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    if mutation == "both":
        checkout["head"], checkout["tree"] = STALE_HEAD, STALE_TREE
    elif mutation == "missing_head":
        checkout.pop("head")
    elif mutation == "missing_tree":
        checkout.pop("tree")
    else:
        checkout[mutation] = value
    context = reseal(context)
    project_adapter(context)
    with pytest.raises((RuntimeError, OWNER.ContextError)):
        LAUNCHER.prove_guest_adapter_binding(ROOT, context)


def test_ambiguous_multiple_bootstrap_binding_is_rejected(tmp_path: Path) -> None:
    context = build_context(tmp_path)
    raw = OWNER.canonical_bytes(context)
    needle = b'"head":"' + HG_HEAD.encode() + b'",'
    assert raw.count(needle) == 1
    path = tmp_path / "ambiguous-context.json"
    path.write_bytes(raw.replace(needle, needle + needle))
    with pytest.raises(OWNER.ContextError, match="duplicate keys"):
        OWNER.load_context(path, repository_root=ROOT)


def test_candidate_runtime_and_authority_cannot_substitute_bootstrap_identity(
    tmp_path: Path,
) -> None:
    for label, head, tree in (
        ("candidate_runtime", HJ_HEAD, HJ_TREE),
        ("authority", "2" * 40, "3" * 40),
    ):
        context = build_context(tmp_path / label)
        checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
        checkout["head"], checkout["tree"] = head, tree
        context = reseal(context)
        project_adapter(context)
        with pytest.raises((RuntimeError, OWNER.ContextError)):
            LAUNCHER.prove_guest_adapter_binding(ROOT, context)
    assert list(inspect.signature(LAUNCHER.prove_guest_adapter_binding).parameters) == [
        "repository_root", "context"
    ]


def test_hj_failure_class_is_blocked_in_authority_free_static_readiness(
    tmp_path: Path,
) -> None:
    context = build_context(tmp_path)
    prepare_static_projection(context)
    observations = LAUNCHER.observe_context_assets(
        ROOT, context, HJ_CANDIDATE.relative_to(ROOT)
    )
    result = LAUNCHER.authority_free_static_readiness(
        repository_root=ROOT,
        context=context,
        observed_head=HJ_HEAD,
        observed_tree=HJ_TREE,
        repository_clean=True,
        observed_asset_sha256=observations,
        candidate_source_path=HJ_CANDIDATE.relative_to(ROOT),
    )
    assert result["result"] == "STATIC_READINESS_PASS"
    assert result["human_operational_authorization_count"] == 0
    assert result["qemu_execution_count"] == 0
    assert result["guest_adapter_binding"]["result"] == (
        "PREAUTHORITY_GUEST_ADAPTER_BINDING_PASS"
    )


def test_projection_wrong_input_firewall_and_single_route_are_unchanged() -> None:
    launcher_source = LAUNCHER_PATH.read_text(encoding="utf-8")
    launcher_tree = ast.parse(launcher_source)
    main = [
        node for node in launcher_tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "main"
    ]
    qemu_calls = [
        node for node in ast.walk(main[0])
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "subprocess"
        and node.func.attr == "run"
    ]
    assert len(main) == len(qemu_calls) == 1
    owner_source = OWNER_PATH.read_text(encoding="utf-8")
    assert "VALID_PATH_PROJECTION" not in launcher_source
    assert hashlib.sha256(GY_REDUCER.read_bytes()).hexdigest() == (
        "8a6e6081118a2c1d305260555ba1ad5a11d97a5d66516f9810beb87c5c39fbf7"
    )
    ha_source = HA_ADAPTER.read_text(encoding="utf-8")
    assert 'TARGET_MUTATION = "input_identity"' in ha_source
    assert 'DEPENDENT_RECOMPUTATION = "record_identity"' in ha_source
    assert "SEMANTIC_MUTATION_COUNT = 1" in ha_source
    assert 'EXPECTED_DIFFERING_FIELDS = ["input_identity", "record_identity"]' in (
        ha_source
    )
    assert "validate_sealed_canonical_argv" in owner_source


def test_no_operational_or_authority_expansion_in_changed_launcher_lines() -> None:
    changed = subprocess.check_output(
        ["git", "diff", "--unified=0", "HEAD", "--", str(LAUNCHER_PATH.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
    )
    additions = "\n".join(
        line[1:] for line in changed.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ).lower()
    assert "authority" not in additions
    assert "request" not in additions
    assert "qemu-system" not in additions
    assert "subprocess" not in additions
    assert "retry" not in additions


def test_terminal_reduction_is_canonical_sealed_and_zero_operation() -> None:
    envelope = load_unique(HK_REDUCTION)
    reduction = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(
        OWNER.canonical_bytes(reduction)
    ).hexdigest()
    assert reduction["readiness"]["terminal_branch"] == (
        "BRANCH_A__BOOTSTRAP_CORRECTION_VERIFIED"
    )
    assert reduction["readiness"]["post_commit_live_binding_status"] == (
        "NOT_PROVEN"
    )
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"] == {
        "after": "7/18", "before": "7/18", "credit": 0, "remaining": 11
    }
    assert reduction["terminal_control"] == {
        "auto_continuable": False,
        "human_review_required": True,
        "verdict": (
            "PASS__G77_256HK_CURRENT_HG_WRONG_INPUT_GUEST_BOOTSTRAP_"
            "CHECKOUT_ARGUMENT_BINDING_CORRECTION_VERIFIED__POST_COMMIT_LIVE_"
            "BINDING_NOT_PROVEN__ZERO_OPERATION__E05_7_OF_18__HUMAN_REVIEW_"
            "REQUIRED"
        ),
    }


def test_g48_report_has_exact_structure_and_terminal_control() -> None:
    report = HK_REPORT.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    required = (
        "HJ_LAST_VERIFIED_EDGE",
        "HJ_FIRST_BROKEN_EDGE",
        "STALE_BOOTSTRAP_HEAD",
        "REQUIRED_BOOTSTRAP_HEAD",
        "BOOTSTRAP_ARGUMENT_OWNER",
        "REUSE_SEARCH_STATUS",
        "CURRENT_HG_BOOTSTRAP_BINDING_ACCEPTANCE_STATUS",
        "HG_PROJECTION_CORRECTION_PRESERVATION_STATUS",
        "WRONG_INPUT_SEMANTIC_FIREWALL_STATUS",
        "HJ_LIVE_BINDING_PRESERVATION_STATUS",
        "CHANGED_OWNER_SET",
        "EX_REUSED = 17/17",
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "CCWIM_MATURITY_LEVEL",
        "HUMAN_OPERATIONAL_AUTHORITY",
        "E05_AFTER = 7/18",
        "MINIMUM_LEGAL_NEXT_DEVELOPMENT_DELTA",
        "AUTO_CONTINUABLE = NO",
        "HUMAN_REVIEW_REQUIRED = YES",
    )
    assert all(token in report for token in required)
    assert report.rstrip().endswith(
        "PASS__G77_256HK_CURRENT_HG_WRONG_INPUT_GUEST_BOOTSTRAP_CHECKOUT_"
        "ARGUMENT_BINDING_CORRECTION_VERIFIED__POST_COMMIT_LIVE_BINDING_NOT_"
        "PROVEN__ZERO_OPERATION__E05_7_OF_18__HUMAN_REVIEW_REQUIRED"
    )
