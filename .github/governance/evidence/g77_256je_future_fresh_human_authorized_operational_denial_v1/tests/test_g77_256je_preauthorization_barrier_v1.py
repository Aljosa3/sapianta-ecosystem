#!/usr/bin/env python3
"""Focused preauthorization verification for the G77-256JE Human barrier."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
JE = ROOT / (
    ".github/governance/evidence/"
    "g77_256je_future_fresh_human_authorized_operational_denial_v1"
)
MATERIALIZER = JE / "orchestration/G77_256JE_PREAUTHORIZATION_MATERIALIZER_V1.py"
CONTROLLER = JE / "orchestration/G77_256JE_AUTHORITY_CONSUMPTION_CONTROLLER_V1.py"


def load_module(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


M = load_module(MATERIALIZER, "g77_256je_test_materializer")
C = load_module(CONTROLLER, "g77_256je_test_controller")


def load_unique(path: Path) -> dict:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=M.unique_object)
    assert isinstance(value, dict)
    assert raw == M.canonical_bytes(value)
    return value


def test_exact_jd_entry_lineage_nested_authority_and_reconstruction() -> None:
    entry = M.authenticate_entry(M.HEAD, M.NESTED_HEAD)
    assert (entry["head"], entry["tree"], entry["subject"]) == (
        "393f887f62d56811092ff6ee5aacb273f3c10d83",
        "d304bb2b5543ba04e8b8b1e8fdf96f9cb9067ea5",
        "G77-256JD certify FUTURE post-JC live-binding readiness",
    )
    assert entry["local_remote_equality"] == "VERIFIED"
    assert {"IE", "IF", "IV", "IW", "IX", "IY", "IZ", "JA", "JB", "JC", "JD"} <= set(
        entry["lineage"]
    )
    assert set(entry["lineage"].values()) == {"VERIFIED"}
    assert entry["nested_authority"]["clean"] is True
    assert entry["nested_authority"]["detached"] is True
    jd = M.reconstruct_jd()
    assert jd["terminal"] == (
        "A__FUTURE_POST_JC_COMMIT_LIVE_BINDING_AND_OPERATIONAL_READINESS_VERIFIED"
    )
    assert jd["inner_seal"] == "VERIFIED"
    assert jd["ex_reused"] == "VERIFIED__17_OF_17"
    assert jd["ex_reconstructed"] == "VERIFIED__0"


def test_future_semantics_runtime_certification_roles_and_context() -> None:
    future = M.authenticate_future_semantics()
    assert (future["evaluation"], future["valid_from"], future["valid_until"]) == (
        500,
        600,
        1000,
    )
    assert future["payload_digest"] == (
        "sha256:9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547"
    )
    assert future["wall_clock_dependency_count"] == 0
    context = M.FM.fresh_context.load_context(
        JE / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json",
        repository_root=ROOT,
    )
    assert (context["repository_head"], context["repository_tree"]) == (M.HEAD, M.TREE)
    assert context["generation_identity"] == M.GENERATION
    assert context["operation_identity"] == M.OPERATION
    eb = load_unique(
        JE / "live_binding/v2_readiness/bindings/G77_256JE_EB_RECEIPT_V2.json"
    )["receipt"]
    ee = load_unique(
        JE / "live_binding/v2_readiness/bindings/G77_256JE_EE_RECEIPT_V2.json"
    )["receipt"]
    assert eb["certification_baseline"] == {"head": M.HEAD, "tree": M.TREE}
    runtime_target = eb["runtime_target_selection_binding"]
    assert (runtime_target["head"], runtime_target["tree"]) == (M.IF_HEAD, M.IF_TREE)
    assert runtime_target["context_binding"]["identity"] == (
        "G77_256IH_AUTHENTICATED_IF_RUNTIME_TARGET_CONTEXT_V1"
    )
    assert ee["certification_baseline"] == eb["certification_baseline"]
    assert ee["runtime_target_selection_binding"] == eb["runtime_target_selection_binding"]


def test_current_three_member_harness_nocloud_import_root_and_no_network() -> None:
    context = load_unique(JE / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json")
    harness = JE / "operation_state/guest_harness"
    assert {path.name for path in harness.iterdir()} == {
        "G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py",
        "G77_256JE_FUTURE_VECTOR_ADAPTER_V1.py",
        "sapianta_fresh_operation_context_v1.py",
    }
    binding = context["guest_adapter_binding"]
    assert binding["source_path"].endswith(
        "g77_256jc_future_guest_context_owner_projection_v1/adapter/"
        "G77_256JC_FUTURE_VECTOR_ADAPTER_V1.py"
    )
    assert binding["source_sha256"] == (
        "fb3cf7976447cb624b57f804b70d042513e24671f5f350e509c6006f0efabcdc"
    )
    seed = context["qemu_executable_base_seed_checkout_bindings"]["seed"]
    assert seed["sha256"] == (
        "6998d4cdaff3617b9e2c29f17318a220619fc718d0d9f9168b08e614cfdf0418"
    )
    assert "g77_256jc_future_guest_context_owner_projection_v1" in seed["path"]
    assert all(
        argument != "-net" and not argument.startswith("-netdev")
        for argument in context["canonical_argv"]
    )
    M.FM.prove_guest_adapter_binding(ROOT, context)


def test_gn_gl_preauthorization_and_exact_zero_operation_boundary() -> None:
    request_path = JE / "G77_256JE_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
    presentation_path = (
        JE / "G77_256JE_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
    )
    result = M.GN.validate_human_authorization_presentation(
        request_path, presentation_path.read_bytes()
    )
    assert result["human_presentation_request_equivalence"] == (
        "VERIFIED_WITHIN_EXACT_REVIEWED_AUTHORIZATION_BINDING_BOUNDARY"
    )
    equivalence = load_unique(
        JE / "G77_256JE_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1.json"
    )["proof"]
    assert equivalence["preauth_final_admission_equivalence"] == (
        "VERIFIED_WITHIN_EXACT_REVIEWED_RECEIPT_PARENT_BOUNDARY"
    )
    reduction = load_unique(JE / "G77_256JE_PREHUMAN_PHASE_A_REDUCTION_V1.json")[
        "reduction"
    ]
    assert reduction["terminal"] == "HUMAN_AUTHORIZATION_REQUIRED"
    counters = reduction["operational_counters"]
    assert counters["authorization_presentation"] == 1
    assert all(value == 0 for key, value in counters.items() if key != "authorization_presentation")
    assert reduction["e05"] == {
        "before": "10/18",
        "current": "10/18",
        "credit": 0,
        "remaining": 8,
    }
    assert hashlib.sha256(request_path.read_bytes()).hexdigest() == (
        "b141fee69177af9d79357f871820fa7c0858afb04afa9786794a1425d795748d"
    )
    assert load_unique(request_path)["request_sha256"] == (
        "e90d59c6bbe3ff401102bc50c1c55bc926b246058a94dc1f4e6a666e687b6e8c"
    )
    assert hashlib.sha256(presentation_path.read_bytes()).hexdigest() == (
        "1fb0c91fc6eb367df4fc99d455651ffdc1ca6b80d89a87dd3bca0518bb7f9f30"
    )


def test_canonical_seals_consumed_authority_and_no_production_mutation() -> None:
    for path in sorted(JE.rglob("*.json")):
        value = load_unique(path)
        for inner, seal in (
            ("reduction", "reduction_sha256"),
            ("proof", "proof_sha256"),
            ("checkpoint", "checkpoint_sha256"),
            ("request", "request_sha256"),
            ("observation", "observation_sha256"),
        ):
            if inner in value and seal in value:
                assert value[seal] == hashlib.sha256(M.canonical_bytes(value[inner])).hexdigest()
    for path in JE.rglob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    source = MATERIALIZER.read_text(encoding="utf-8")
    controller = CONTROLLER.read_text(encoding="utf-8")
    assert "FM.main(" not in source
    assert "subprocess.run(argv" not in source
    assert "FM.main(" not in controller
    assert "subprocess.run(argv" not in controller
    assert C.REQUEST_SHA256 == (
        "e90d59c6bbe3ff401102bc50c1c55bc926b246058a94dc1f4e6a666e687b6e8c"
    )
    assert C.EXPECTED_NORMALIZED_GRANT == (
        "I explicitly authorize G77-256JE request "
        "e90d59c6bbe3ff401102bc50c1c55bc926b246058a94dc1f4e6a666e687b6e8c "
        "for operation G77_256JE_E05_FUTURE_DENIAL_BEFORE_ENTRY_001, candidate "
        "ad5d204ec6ace09f18b83fd5f868e73dac5e36dad81149f9f335c87f68cf42f7, "
        "context 1e04e1d34e77dd0605eb03e21c2c8f51dc99b3c68fbe60b01f539f9ad0b590c3, "
        "and canonical argv 92256e675832e3a43b39cf3bf7e3699d418707da2d22a0c0ff9d1a7d5a72afb3, "
        "starting from E05 10/18, subject to exactly one authority consumption, "
        "PRE, FM invocation, no-network QEMU, VM boot, and operation attempt, "
        "with zero retry, repair, replay, or protected effect.\n"
    )
    grant = JE / "G77_256JE_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
    handoff = JE / "G77_256JE_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
    consumption = JE / "G77_256JE_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json"
    assert hashlib.sha256(grant.read_bytes()).hexdigest() == (
        "86f6f6448950468a4e688451e7d823b7b5dfce14fde387ae40c304ee6eb21e1c"
    )
    handoff_value = load_unique(handoff)
    assert handoff_value["authorization_sha256"] == (
        "242fb3c5e24251ebafce12904d6ca96930d90ca1b09b8fd7c2d3719343f7ac33"
    )
    consumed = load_unique(consumption)["checkpoint"]
    assert consumed["authority_state_before"] == "GRANTED_UNCONSUMED"
    assert consumed["authority_state_after"] == "CONSUMED"
    assert consumed["authority_consumed"] == 1
    assert consumed["authority_reusable"] is False
    assert subprocess.check_output(
        [
            "git",
            "diff",
            "--name-only",
            M.HEAD,
            "--",
            "aigol/runtime",
            "sapianta_system",
            ".github/governance/evidence/g77_256ec_p11_operational_v1",
            ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1",
        ],
        cwd=ROOT,
        text=True,
    ).strip() == ""
    assert subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True
    ).strip() == ""
