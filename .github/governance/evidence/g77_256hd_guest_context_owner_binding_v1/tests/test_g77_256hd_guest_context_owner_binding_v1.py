#!/usr/bin/env python3
"""Repository-only proof for the post-HC guest context-owner correction."""

from __future__ import annotations

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
LAUNCHER_PATH = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
HC = ROOT / ".github/governance/evidence/g77_256hc_wrong_input_operational_v1"
CANDIDATE = ROOT / (
    ".github/governance/evidence/g77_256hb_post_ha_live_binding_readiness_v1/"
    "live_binding/candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
)
EXPECTED_HEAD = "a5fde262c8833922375a10e79c745c0ff19e698e"
EXPECTED_TREE = "c265719bc048a9ab686e290d1952280d5584a43e"
HISTORICAL_CHECKOUT_HEAD = "7dce67ec18696ba0bad73130f3f7a84168f25277"
HISTORICAL_CHECKOUT_TREE = "3cb61ec34e9593efb711dce61014dc8fdf0f6dd9"
OWNER_SHA256 = "45b97e99122146ec3aa95f45fe5ac71381ca1a11e83b7355438b988608f52fca"


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


LAUNCHER = load_module(LAUNCHER_PATH, "g77_256hd_existing_fm_owner")


def git(*arguments: str) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=ROOT, text=True
    ).strip()


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def load_unique(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_bytes(), object_pairs_hook=unique_object)
    assert isinstance(value, dict)
    return value


def reseal_context(context: dict[str, Any]) -> dict[str, Any]:
    unsealed = {key: value for key, value in context.items() if key != "context_sha256"}
    context["context_sha256"] = hashlib.sha256(
        LAUNCHER.canonical_bytes(unsealed)
    ).hexdigest()
    return context


def build_context(root: Path) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    return LAUNCHER.build_operation_context(
        repository_root=ROOT,
        repository_head=EXPECTED_HEAD,
        repository_tree=EXPECTED_TREE,
        generation_identity=(
            "G77_256HD_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_"
            "OPERATIONAL_COMMISSIONING_V1"
        ),
        operation_identity="G77_256HD_REPOSITORY_ONLY_PROOF_001",
        identity_namespace_prefix="G77_256HD",
        operation_evidence_root=root / "operation_state",
        transient_root=root / "transient",
        candidate_source_path=CANDIDATE.relative_to(ROOT),
    )


def materialize_bound_checkout(context: dict[str, Any]) -> Path:
    binding = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    checkout = Path(binding["path"])
    LAUNCHER.materialize_guest_self_contained_checkout(
        source_repository=ROOT,
        checkout_path=checkout,
        expected_head=binding["head"],
        expected_tree=binding["tree"],
    )
    return checkout


def test_exact_hc_broken_edge_is_reproduced_from_objects_serial_and_reduction() -> None:
    assert git("rev-parse", "HEAD") == EXPECTED_HEAD
    assert git("rev-parse", "HEAD^{tree}") == EXPECTED_TREE
    historical_paths = git(
        "ls-tree", "-r", "--name-only", HISTORICAL_CHECKOUT_HEAD, "--",
        LAUNCHER.FRESH_OPERATION_CONTEXT_OWNER,
    )
    current_paths = git(
        "ls-tree", "-r", "--name-only", EXPECTED_HEAD, "--",
        LAUNCHER.FRESH_OPERATION_CONTEXT_OWNER,
    )
    assert historical_paths == ""
    assert current_paths == LAUNCHER.FRESH_OPERATION_CONTEXT_OWNER
    assert git("rev-parse", f"{HISTORICAL_CHECKOUT_HEAD}^{{tree}}") == (
        HISTORICAL_CHECKOUT_TREE
    )

    serial = (HC / "G77_256HC_SERIAL_CONSOLE_V1.log").read_bytes()
    assert hashlib.sha256(serial).hexdigest() == (
        "7c49bb08c3cb49c18aca5936f7c31c9a669c3bcbbc012f79154626f28eff6192"
    )
    assert b"G77_256FM_BOOT_MARKER=PASS" in serial
    assert LAUNCHER.FRESH_OPERATION_CONTEXT_OWNER.encode() in serial
    assert b"FileNotFoundError" in serial
    assert b"G77_256FM_HARNESS_EXIT_STATUS=1" in serial

    terminal = load_unique(HC / "G77_256HC_SPCE_TERMINAL_REDUCTION_V1.json")
    counters = terminal["reduction"]["operational_counters"]
    assert counters["request"] == counters["p11_entry"] == 0
    assert counters["protected_invocation"] == counters["protected_effect"] == 0
    assert terminal["reduction"]["e05"] == {
        "after": "7/18", "before": "7/18", "credit": 0
    }


def test_existing_context_owner_builds_one_exact_owner_bound_checkout(tmp_path: Path) -> None:
    context = build_context(tmp_path)
    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    hashes = context["wrapper_fc_er_che_schema_hashes"]
    assert checkout["head"] == LAUNCHER.CHECKOUT_HEAD == EXPECTED_HEAD
    assert checkout["tree"] == LAUNCHER.CHECKOUT_TREE == EXPECTED_TREE
    assert hashes[LAUNCHER.FRESH_OPERATION_CONTEXT_OWNER_HASH_KEY] == OWNER_SHA256
    assert LAUNCHER.sha256_path(
        ROOT / LAUNCHER.FRESH_OPERATION_CONTEXT_OWNER
    ) == OWNER_SHA256
    LAUNCHER.validate_immutable_context_bindings(
        ROOT, context, CANDIDATE.relative_to(ROOT)
    )


def test_host_checkout_guest_path_byte_and_hash_identity(tmp_path: Path) -> None:
    context = build_context(tmp_path)
    context_path = tmp_path / "context.json"
    context_path.write_bytes(LAUNCHER.canonical_bytes(context))
    materialization = LAUNCHER.materialize_operation_state(
        repository_root=ROOT,
        context=context,
        context_source_path=context_path,
        candidate_source_path=CANDIDATE.relative_to(ROOT),
    )
    assert materialization["qemu_execution_count"] == 0
    checkout = Path(
        context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["path"]
    )
    proof = LAUNCHER.prove_guest_fresh_operation_context_owner_binding(ROOT, context)
    projected = checkout / LAUNCHER.FRESH_OPERATION_CONTEXT_OWNER
    assert projected.read_bytes() == (
        ROOT / LAUNCHER.FRESH_OPERATION_CONTEXT_OWNER
    ).read_bytes()
    assert proof["authoritative_source_sha256"] == OWNER_SHA256
    assert proof["checkout_sha256"] == OWNER_SHA256
    assert proof["guest_expected_owner_sha256"] == OWNER_SHA256
    assert proof["guest_visible_path"] == (
        "/mnt/aigol/" + LAUNCHER.FRESH_OPERATION_CONTEXT_OWNER
    )
    assert proof["host_checkout_guest_byte_identity"] == "PASS"
    assert proof["host_checkout_guest_hash_identity"] == "PASS"
    readiness = LAUNCHER.validate_checkout_preboot_readiness(context)
    assert readiness["preauth_guest_fm_context_owner_binding"] == proof
    assert LAUNCHER.prove_guest_adapter_binding(ROOT, context)["result"] == (
        "PREAUTHORITY_GUEST_ADAPTER_BINDING_PASS"
    )
    observed_assets = LAUNCHER.observe_context_assets(
        ROOT, context, CANDIDATE.relative_to(ROOT)
    )
    static_readiness = LAUNCHER.authority_free_static_readiness(
        repository_root=ROOT,
        context=context,
        observed_head=EXPECTED_HEAD,
        observed_tree=EXPECTED_TREE,
        repository_clean=True,
        observed_asset_sha256=observed_assets,
        candidate_source_path=CANDIDATE.relative_to(ROOT),
    )
    assert static_readiness["result"] == "STATIC_READINESS_PASS"
    assert static_readiness["human_operational_authorization_count"] == 0
    assert static_readiness["qemu_execution_count"] == 0


def test_current_context_without_owner_binding_fails_before_authority(tmp_path: Path) -> None:
    context = build_context(tmp_path)
    del context["wrapper_fc_er_che_schema_hashes"][
        LAUNCHER.FRESH_OPERATION_CONTEXT_OWNER_HASH_KEY
    ]
    reseal_context(context)
    with pytest.raises(RuntimeError, match="current context omits FM context owner binding"):
        LAUNCHER.validate_immutable_context_bindings(
            ROOT, context, CANDIDATE.relative_to(ROOT)
        )


def test_owner_negative_matrix_rejects_missing_wrong_stale_and_unbound_state(
    tmp_path: Path,
) -> None:
    host_only = build_context(tmp_path / "host-only")
    with pytest.raises(RuntimeError, match="checkout root is not canonical"):
        LAUNCHER.prove_guest_fresh_operation_context_owner_binding(ROOT, host_only)

    wrong_hash = build_context(tmp_path / "wrong-hash")
    wrong_hash["wrapper_fc_er_che_schema_hashes"][
        LAUNCHER.FRESH_OPERATION_CONTEXT_OWNER_HASH_KEY
    ] = "0" * 64
    reseal_context(wrong_hash)
    with pytest.raises(RuntimeError, match="hash binding missing or invalid"):
        LAUNCHER.prove_guest_fresh_operation_context_owner_binding(ROOT, wrong_hash)

    wrong_bytes = build_context(tmp_path / "wrong-bytes")
    checkout = materialize_bound_checkout(wrong_bytes)
    owner = checkout / LAUNCHER.FRESH_OPERATION_CONTEXT_OWNER
    owner.write_bytes(b"not-the-authoritative-owner\n")
    with pytest.raises(RuntimeError, match="identity mismatch"):
        LAUNCHER.prove_guest_fresh_operation_context_owner_binding(ROOT, wrong_bytes)
    with pytest.raises(RuntimeError, match="checkout dirty"):
        LAUNCHER.validate_checkout_preboot_readiness(wrong_bytes)

    historical_root = tmp_path / "historical" / "checkout"
    LAUNCHER.materialize_guest_self_contained_checkout(
        source_repository=ROOT,
        checkout_path=historical_root,
        expected_head=HISTORICAL_CHECKOUT_HEAD,
        expected_tree=HISTORICAL_CHECKOUT_TREE,
    )
    historical_context = {
        "wrapper_fc_er_che_schema_hashes": {
            LAUNCHER.FRESH_OPERATION_CONTEXT_OWNER_HASH_KEY: OWNER_SHA256,
        },
        "qemu_executable_base_seed_checkout_bindings": {
            "checkout": {"path": str(historical_root)},
        },
        "canonical_argv": [
            "qemu-system-x86_64",
            "-virtfs",
            (
                f"local,path={historical_root},mount_tag=aigol_checkout,"
                "security_model=none,readonly=on"
            ),
        ],
    }
    with pytest.raises(RuntimeError, match="owner absent or unsafe"):
        LAUNCHER.prove_guest_fresh_operation_context_owner_binding(
            ROOT, historical_context
        )


def test_context_adapter_disagreement_and_wrong_guest_projection_fail_closed(
    tmp_path: Path,
) -> None:
    context = build_context(tmp_path / "adapter")
    context["guest_adapter_binding"]["source_sha256"] = "0" * 64
    reseal_context(context)
    with pytest.raises(
        LAUNCHER.fresh_context.ContextError,
        match="guest adapter binding is not canonically derived",
    ):
        LAUNCHER.fresh_context.validate_context(context, repository_root=ROOT)

    wrong_projection = build_context(tmp_path / "projection")
    materialize_bound_checkout(wrong_projection)
    argv = wrong_projection["canonical_argv"]
    index = next(
        index for index, value in enumerate(argv)
        if value == "-virtfs" and "mount_tag=aigol_checkout" in argv[index + 1]
    )
    argv[index + 1] = argv[index + 1].replace(
        "mount_tag=aigol_checkout", "mount_tag=wrong_checkout"
    )
    with pytest.raises(RuntimeError, match="guest presentation binding mismatch"):
        LAUNCHER.prove_guest_fresh_operation_context_owner_binding(
            ROOT, wrong_projection
        )


def test_same_class_dependencies_are_already_self_contained_and_bound(
    tmp_path: Path,
) -> None:
    context = build_context(tmp_path)
    checkout = materialize_bound_checkout(context)
    dependencies = {
        LAUNCHER.FRESH_OPERATION_CONTEXT_OWNER: OWNER_SHA256,
        (
            ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/"
            "producer/G77_256GY_WRONG_INPUT_REQUEST_AND_CANDIDATE_PRODUCER_V1.py"
        ): "643de4aa38264410c445107dfdd71b02334871021dd0b7d5ef8886a62e80cd22",
        LAUNCHER.FK_ADAPTER: LAUNCHER.FK_ADAPTER_SHA256,
        LAUNCHER.ER_HARNESS_RELATIVE: LAUNCHER.ER_HARNESS_SHA256,
        LAUNCHER.CANONICAL_CHE: (
            "75801995214e81419aab9a02326499c771ec0039658fb49598aa54bd033e13c5"
        ),
    }
    for relative, expected_sha256 in dependencies.items():
        path = checkout / relative
        assert not path.is_symlink() and path.is_file()
        assert LAUNCHER.sha256_path(path) == expected_sha256
    bootstrap = LAUNCHER.bootstrap_asset_bindings(context)
    assert bootstrap == {
        "cloud_init_path": LAUNCHER.CLOUD_INIT,
        "cloud_init_sha256": LAUNCHER.CLOUD_INIT_SHA256,
        "seed_path": LAUNCHER.SEED,
        "seed_sha256": LAUNCHER.EXPECTED_ASSET_SHA256[LAUNCHER.SEED],
    }
    assert LAUNCHER.sha256_path(ROOT / LAUNCHER.CLOUD_INIT) == (
        bootstrap["cloud_init_sha256"]
    )
    assert LAUNCHER.sha256_path(Path(LAUNCHER.SEED)) == bootstrap["seed_sha256"]
    legacy_paths = (
        LAUNCHER.LEGACY_CLOUD_INIT,
        str(Path(LAUNCHER.LEGACY_SEED).relative_to(ROOT)),
    )
    assert git("diff", "--name-only", "HEAD", "--", *legacy_paths) == ""
    assert git("rev-parse", f"{EXPECTED_HEAD}^{{tree}}") == EXPECTED_TREE


def test_semantic_firewall_single_route_and_zero_operation_are_preserved() -> None:
    gy = ROOT / (
        ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/"
        "producer/G77_256GY_WRONG_INPUT_REQUEST_AND_CANDIDATE_PRODUCER_V1.py"
    )
    ha = ROOT / (
        ".github/governance/evidence/g77_256ha_wrong_input_route_binding_v1/"
        "adapter/G77_256HA_WRONG_INPUT_VECTOR_ADAPTER_V1.py"
    )
    assert LAUNCHER.sha256_path(gy) == (
        "643de4aa38264410c445107dfdd71b02334871021dd0b7d5ef8886a62e80cd22"
    )
    assert LAUNCHER.sha256_path(ha) == (
        "fb83002e5567c2a109bfb977270865e6fb085e39f551d1068d03537a3b1d6230"
    )
    tree = ast.parse(LAUNCHER_PATH.read_text(encoding="utf-8"))
    mains = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "main"
    ]
    assert len(mains) == 1
    qemu_calls = [
        node for node in ast.walk(mains[0])
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "subprocess"
        and node.func.attr == "run"
    ]
    assert len(qemu_calls) == 1
    assert "input_identity" not in LAUNCHER_PATH.read_text(encoding="utf-8")
