#!/usr/bin/env python3
"""Focused repository/static validation for G77-256IT."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
IT = ROOT / ".github/governance/evidence/g77_256it_future_bootstrap_seed_binding_v1"
FORMALIZER_PATH = IT / "analysis/G77_256IT_FUTURE_BOOTSTRAP_SEED_BINDING_FORMALIZER_V1.py"
TERMINAL = IT / "G77_256IT_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = IT / "G77_256IT_G48_IMPLEMENTATION_REPORT_V1.md"


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


ITF = load_module(FORMALIZER_PATH, "g77_256it_test_formalizer")
DU_V2_PATH = ROOT / (
    ".github/governance/evidence/g77_256du_continuation_manifest_contract_v2/"
    "validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V2.py"
)
DU_V2 = load_module(DU_V2_PATH, "g77_256it_test_du_v2")


def load_unique(path: Path) -> dict:
    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"duplicate JSON key: {key}")
            value[key] = item
        return value

    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique)
    assert isinstance(value, dict)
    assert raw == ITF.canonical_bytes(value)
    return value


def test_exact_is_checkpoint_lineage_and_nested_authority() -> None:
    entry = ITF.authenticate_entry()
    assert entry["head"] == ITF.IS_HEAD
    assert entry["tree"] == ITF.IS_TREE
    assert entry["subject"] == ITF.IS_SUBJECT
    assert entry["remote_tracking_head"] == ITF.IS_HEAD
    assert entry["index"] == ""
    assert set(entry["lineage"]) == set(ITF.LINEAGE)
    assert set(entry["lineage"].values()) == {"VERIFIED"}
    assert entry["nested"] == entry["nested"] | {
        "head": ITF.NESTED_HEAD,
        "tree": ITF.NESTED_TREE,
        "branch": "",
        "status": "",
    }


def test_committed_is_terminal_and_exact_blocker_reconstruct() -> None:
    blocker = ITF.reconstruct_is()
    assert blocker["terminal"] == "E__CONSTITUTIONAL_REGRESSION"
    assert blocker["last_verified_edge"] == (
        "IF_CANDIDATE_AND_IR_BASELINE_V2_ROLE_SEPARATION__"
        "FM_OPERATION_STATE_MATERIALIZED_WITHOUT_QEMU"
    )
    assert blocker["first_broken_edge"] == (
        "FM_AUTHORITY_FREE_STATIC_READINESS__"
        "FUTURE_CLOUD_INIT_ADAPTER_BOOTSTRAP_CONSUMER"
    )
    assert blocker["exact_failure"] == (
        "RuntimeError: cloud-init adapter bootstrap consumer mismatch"
    )


def test_historical_if_blocker_is_immutable_and_successor_owner_is_unique() -> None:
    assert subprocess.check_output(
        ["git", "diff", "--name-only", "HEAD", "--", ITF.IF_CLOUD_INIT, ITF.IF_SEED],
        cwd=ROOT,
        text=True,
    ).strip() == ""
    graph = ITF.audit_binding()
    assert graph["authoritative_historical_owner"] == ITF.IF_CLOUD_INIT.as_posix()
    assert graph["authoritative_successor_owner"] == ITF.CLOUD_INIT.as_posix()
    assert graph["authoritative_seed_owner"] == ITF.SEED.as_posix()
    assert graph["authoritative_selector_owner"] == ITF.FM_LAUNCHER.as_posix()


def test_current_bootstrap_binds_exact_existing_fm_consumer_and_arguments() -> None:
    launcher = ITF.load_module(ROOT / ITF.FM_LAUNCHER, "g77_256it_test_launcher")
    cloud_text = (ROOT / ITF.CLOUD_INIT).read_text(encoding="utf-8")
    assert cloud_text.count(ITF.BOOTSTRAP_GUEST_PATH) == 1
    assert ITF.PROHIBITION not in cloud_text
    assert launcher.bootstrap_guest_command_arguments(
        cloud_text, ITF.BOOTSTRAP_GUEST_PATH
    ) == (
        ITF.ADAPTER_SHA256,
        ITF.RAW_SCHEMA_SHA256,
        ITF.IF_HEAD,
        ITF.IF_TREE,
        ITF.DN_HARNESS_SHA256,
    )


def test_nocloud_seed_projects_exact_current_bootstrap_and_common_inputs() -> None:
    assert ITF.seed_projection() == {
        "builder_mechanism": "GENISOIMAGE_CIDATA_JOLIET_ROCK__STATIC_CONTENT_HASH_IDENTITY",
        "source_projection": "VERIFIED",
        "bootstrap_bytes_identity": "VERIFIED",
        "nocloud_seed_bootstrap_binding": "VERIFIED",
        "wall_clock_freshness_dependency": "VERIFIED__0",
    }
    assert ITF.sha256_path(ROOT / ITF.CLOUD_INIT) == ITF.NEW_CLOUD_SHA256
    assert ITF.sha256_path(ROOT / ITF.SEED) == ITF.NEW_SEED_SHA256


def test_existing_fm_authority_free_bootstrap_binding_passes() -> None:
    graph = ITF.audit_binding()
    assert graph["static_fm_binding_proof"] == "PREAUTHORITY_GUEST_ADAPTER_BINDING_PASS"
    assert graph["existing_fm_bootstrap_consumer_bound"] == "VERIFIED"
    assert graph["is_bootstrap_consumer_blocker"] == (
        "VERIFIED__REMOVED_BY_IT_REPOSITORY_DELTA"
    )
    assert graph["stale_bootstrap_projection"] == "VERIFIED__NO"


def test_only_deterministically_dependent_identities_change() -> None:
    reduction = ITF.build_reduction()
    assert reduction["dependent_identity_recomputation"] == [
        {
            "owner": ITF.CLOUD_INIT.as_posix(),
            "old_identity": ITF.OLD_CLOUD_SHA256,
            "new_identity": ITF.NEW_CLOUD_SHA256,
            "dependency_reason": "FUTURE_BOOTSTRAP_CONSUMER_BYTES",
        },
        {
            "owner": ITF.SEED.as_posix(),
            "old_identity": ITF.OLD_SEED_SHA256,
            "new_identity": ITF.NEW_SEED_SHA256,
            "dependency_reason": "NOCLOUD_USER_DATA_PROJECTION",
        },
        {
            "owner": ITF.FM_LAUNCHER.as_posix(),
            "old_identity": ITF.OLD_LAUNCHER_SHA256,
            "new_identity": ITF.NEW_LAUNCHER_SHA256,
            "dependency_reason": "EXISTING_FUTURE_ASSET_SELECTOR_BINDING",
        },
    ]
    assert reduction["independent_identities"] == {
        "future_payload": ITF.FUTURE_PAYLOAD,
        "source_act": ITF.FUTURE_SOURCE_ACT,
        "che_correlation": ITF.FUTURE_CHE,
        "if_runtime_candidate_sha256": (
            "ad5d204ec6ace09f18b83fd5f868e73dac5e36dad81149f9f335c87f68cf42f7"
        ),
    }


def test_future_semantics_and_v2_roles_are_unchanged() -> None:
    reduction = ITF.build_reduction()
    assert reduction["future_semantics"] == {
        "evaluation": 500,
        "valid_from": 600,
        "valid_until": 1000,
        "relation": "500 < 600 < 1000",
        "future_semantic_mutation_count": "VERIFIED__0",
        "wall_clock_dependency_count": "VERIFIED__0",
    }
    roles = reduction["v2_role_separation"]
    assert roles["runtime_target"] == {"head": ITF.IF_HEAD, "tree": ITF.IF_TREE}
    assert roles["certification_baseline"] == {"head": ITF.IR_HEAD, "tree": ITF.IR_TREE}
    assert roles["runtime_certification_role_collapse"] == "VERIFIED__NO"


def test_single_route_p11_and_authority_firewalls() -> None:
    reduction = ITF.build_reduction()
    assert set(reduction["route_firewall"].values()) == {
        "VERIFIED__NO", "VERIFIED__1", "VERIFIED__0"
    }
    assert reduction["authority_firewall"]["p11_mutation_count"] == "VERIFIED__0"
    assert all(
        value == "VERIFIED__0"
        for key, value in reduction["authority_firewall"].items()
        if key not in {"e05", "p11_mutation_count"}
    )
    assert subprocess.check_output(
        ["git", "diff", "--name-only", "HEAD", "--", "aigol/runtime", "sapianta_system"],
        cwd=ROOT,
        text=True,
    ).strip() == ""
    launcher_tree = ast.parse((ROOT / ITF.FM_LAUNCHER).read_text(encoding="utf-8"))
    assert sum(
        isinstance(node, ast.FunctionDef) and node.name == "main"
        for node in launcher_tree.body
    ) == 1


def test_ex_is_reused_without_reconstruction() -> None:
    assert ITF.ex_reuse() == {
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
    }


def test_post_commit_v2_readiness_gate_fails_closed_on_uncommitted_owner() -> None:
    with pytest.raises(
        DU_V2.CompatibilityError,
        match="RUNTIME_TARGET_SELECTION_WORKTREE_DRIFT",
    ):
        DU_V2.build_du_fixture(ROOT)


def test_terminal_is_canonical_uniquely_keyed_and_inner_sealed() -> None:
    terminal = load_unique(TERMINAL)
    assert terminal == ITF.build_envelope()
    assert terminal["reduction_sha256"] == hashlib.sha256(
        ITF.canonical_bytes(terminal["reduction"])
    ).hexdigest()
    assert terminal["reduction"]["terminal"] == (
        "A__FUTURE_BOOTSTRAP_AND_NOCLOUD_SEED_BINDING_REPOSITORY_IMPLEMENTED"
    )


def test_python_ast_and_exact_six_g48_headings() -> None:
    ast.parse(FORMALIZER_PATH.read_text(encoding="utf-8"))
    ast.parse(Path(__file__).read_text(encoding="utf-8"))
    headings = [
        line for line in REPORT.read_text(encoding="utf-8").splitlines()
        if line.startswith("# ")
    ]
    assert headings == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]


def test_g48_contains_reuse_answers_and_all_commissioned_metrics() -> None:
    text = REPORT.read_text(encoding="utf-8")
    required = {
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
        "PROJECT_PROGRESS_ESTIMATE",
        "CONSTITUTIONAL_HEALTH_EVIDENCE",
        "SHADOW_AUTOMATION_STATUS",
        "CONSTITUTIONAL_FRONTIER_DISTANCE",
        "E05_FRONTIER_DISTANCE",
        "SELECTED_E05_LOCAL_FRONTIER_DISTANCE",
        "GOVERNANCE_EFFICIENCE",
        "ARCHITECTURAL_GOVERNANCE_EFFICIENCE",
        "PROOF_REUSE_EFFICIENCY",
        "COGNITION_ASSISTED_HANDOFF",
        "AIGOL_CODEX_WORK_SHARE",
        "OVERENGINEERING_RISK",
        "PROOF_PROCESS_OVERHEAD_RISK",
        "COGNITION_PROVENANCE",
        "CANDIDATE_CAPABILITY",
        "SHADOW_DESIGN_TARGET",
        "CONSTITUTIONAL_CONTINUATION_PROGRESS",
        "PROMPT_CONTEXT_REUSE_RATIO",
        "REPOSITORY_DERIVED_EXECUTION_CONTEXT_RATIO",
        "CONSTITUTIONAL_PROMPT_EXTERNALIZATION_RATIO",
        "TOKEN_BENCHMARK",
        "LLM_COST_REDUCTION_RATIO",
        "LCRR",
        "E05_GENERATIONS_PER_CREDIT",
        "OPERATIONAL_ATTEMPTS_PER_CREDIT",
        "MARGINAL_E05_GENERATION_COST",
        "MARGINAL_NEW_INFRASTRUCTURE_PER_E05_CREDIT",
        "INFRASTRUCTURE_AMORTIZATION_SIGNAL",
        "EXPECTED_NEXT_CREDIT_GENERATION_COUNT",
    }
    assert all(token in text for token in required)
