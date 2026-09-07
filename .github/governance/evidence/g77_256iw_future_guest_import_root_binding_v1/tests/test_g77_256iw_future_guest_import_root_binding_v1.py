#!/usr/bin/env python3
"""Focused repository-only regression proof for G77-256IW."""

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
IW = ROOT / ".github/governance/evidence/g77_256iw_future_guest_import_root_binding_v1"
FORMALIZER_PATH = IW / "analysis/G77_256IW_FUTURE_GUEST_IMPORT_ROOT_BINDING_FORMALIZER_V1.py"
TERMINAL = IW / "G77_256IW_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = IW / "G77_256IW_G48_IMPLEMENTATION_REPORT_V1.md"


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


IWF = load_module(FORMALIZER_PATH, "g77_256iw_test_formalizer")


def load_unique_canonical(path: Path) -> dict:
    def unique(pairs):
        value = {}
        for key, item in pairs:
            assert key not in value, f"duplicate JSON key: {key}"
            value[key] = item
        return value

    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique)
    assert raw == IWF.canonical_bytes(value)
    return value


def test_exact_ratified_iv_entry_and_pinned_nested_authority() -> None:
    entry = IWF.authenticate_entry()
    assert entry == entry | {
        "branch": IWF.BRANCH,
        "head": IWF.IV_HEAD,
        "tree": IWF.IV_TREE,
        "subject": IWF.IV_SUBJECT,
        "origin": IWF.ORIGIN,
        "remote_tracking_head": IWF.IV_HEAD,
        "index": "",
    }
    assert entry["nested"] == entry["nested"] | {
        "origin": IWF.NESTED_ORIGIN,
        "head": IWF.NESTED_HEAD,
        "tree": IWF.NESTED_TREE,
        "branch": "",
        "status": "",
        "tag": IWF.NESTED_TAG,
    }


def test_ratified_iv_terminal_receipts_serial_and_cardinalities() -> None:
    iv = IWF.reconstruct_iv_terminal()
    assert iv["terminal"] == "E__AUTHORIZED_OPERATION_FAILED_BEFORE_REQUEST"
    assert iv["exact_failure"] == "ModuleNotFoundError: No module named 'aigol'"
    assert iv["serial_sequence"] == "VERIFIED"
    assert iv["receipt_pair"] == "VERIFIED"
    counters = iv["operational_counters"]
    assert counters["human_operational_authority"] == 1
    assert counters["authority_consumption"] == 1
    assert counters["operation_attempt"] == 1
    assert counters["request"] == counters["future_denial"] == counters["p11_entry"] == 0
    assert counters["retry"] == counters["repair_retry"] == counters["replay"] == 0


def test_checkout_exists_is_distinct_from_checkout_is_import_root() -> None:
    binding = IWF.audit_binding()
    assert binding["checkout_exists"].startswith("VERIFIED__MOUNTED_AT_")
    assert binding["checkout_is_python_import_root"] == (
        "VERIFIED__PYTHONPATH_EXACTLY_/mnt/aigol_BEFORE_ADAPTER"
    )
    assert binding["ordering"] == (
        "CHECKOUT_MOUNT__IMPORT_ROOT_EXPORT__BOOT_MARKER__ADAPTER_EXECUTION"
    )


def test_source_to_nocloud_to_consumer_exact_byte_binding() -> None:
    graph = IWF.audit_binding()
    assert graph["source_to_projection_to_consumer"] == "VERIFIED"
    assert graph["seed_projection"] == {
        "repository_bootstrap_to_nocloud_user_data": "VERIFIED__EXACT_BYTES",
        "nocloud_common_members_to_repository_sources": "VERIFIED__EXACT_BYTES",
        "seed_sha256": IWF.SEED_SHA256,
        "wall_clock_dependency_count": "VERIFIED__0",
    }
    assert graph["selector_binding"] == {
        "cloud_init_path": IWF.CLOUD_INIT.as_posix(),
        "cloud_init_sha256": IWF.CLOUD_SHA256,
        "seed_path": str(ROOT / IWF.SEED),
        "seed_sha256": IWF.SEED_SHA256,
    }


def test_exact_adapter_top_level_imports_are_statically_resolvable() -> None:
    assert IWF.top_level_imports() == IWF.TOP_LEVEL_AIGOL_IMPORTS
    proof = IWF.isolated_import_proof()
    assert proof["runtime_target"] == {
        "role": "IF", "head": IWF.IF_HEAD, "tree": IWF.IF_TREE,
    }
    assert proof["without_guest_import_root"].startswith("EXPECTED_FAIL__")
    assert proof["with_governed_guest_import_root"] == "PASS"
    assert proof["host_sys_path_false_positive"] == "VERIFIED__0"
    assert proof["verified_imports"] == IWF.TOP_LEVEL_AIGOL_IMPORTS


def test_future_semantics_and_runtime_baseline_roles_are_preserved() -> None:
    reduction = IWF.build_reduction()
    assert reduction["future_semantics"] == {
        "evaluation": 500,
        "valid_from": 600,
        "valid_until": 1000,
        "relation": "500 < 600 < 1000",
        "payload_digest": IWF.FUTURE_PAYLOAD,
        "source_act": IWF.FUTURE_SOURCE_ACT,
        "che_correlation": IWF.FUTURE_CHE,
        "future_semantic_mutation_count": "VERIFIED__0",
        "wall_clock_dependency_count": "VERIFIED__0",
    }
    roles = reduction["v2_role_separation"]
    assert roles["runtime_target"]["head"] == IWF.IF_HEAD
    assert roles["certification_baseline"] == {
        "role": "REPOSITORY_DERIVED", "head": IWF.IV_HEAD, "tree": IWF.IV_TREE,
    }
    assert roles["role_collapse"] == "VERIFIED__NO"


def test_authority_route_p11_and_historical_firewalls() -> None:
    reduction = IWF.build_reduction()
    assert set(reduction["authority_firewall"].values()) == {"VERIFIED__0"}
    route = reduction["route_firewall"]
    assert route["production_route_before"] == route["production_route_after"] == "VERIFIED__1"
    assert route["production_route_delta"] == route["p11_mutation_count"] == "VERIFIED__0"
    assert route["parallel_flow_created"] == "VERIFIED__NO"
    firewall = reduction["historical_failure_firewall"]
    assert firewall["checked_failure_class_count"] == "VERIFIED__30"
    assert firewall["reintroduced_failure_count"] == "VERIFIED__0"
    assert firewall["host_sys_path_false_positive_count"] == "VERIFIED__0"
    assert subprocess.check_output(
        ["git", "diff", "--name-only", "HEAD", "--", str(IWF.IT_ROOT), str(IWF.IV_ROOT)],
        cwd=ROOT, text=True,
    ).strip() == ""


def test_du_v2_post_commit_readiness_fails_closed_on_uncommitted_selector() -> None:
    assert IWF.post_commit_readiness_gate() == (
        "EXPECTED_FAIL_CLOSED__RUNTIME_TARGET_SELECTION_WORKTREE_DRIFT"
    )
    assert subprocess.check_output(
        ["git", "diff", "--name-only", "HEAD", "--", "aigol/runtime", "sapianta_system", "tests/p11_da_custody_process_v1.py"],
        cwd=ROOT, text=True,
    ).strip() == ""


def test_ex_17_of_17_is_reused_and_not_reconstructed() -> None:
    assert IWF.ex_reuse() == {
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
        "ex_is_authority": "VERIFIED__NO",
    }


def test_terminal_is_canonical_unique_inner_sealed_and_matches_formalizer() -> None:
    terminal = load_unique_canonical(TERMINAL)
    assert terminal == IWF.build_envelope()
    assert terminal["reduction_sha256"] == hashlib.sha256(
        IWF.canonical_bytes(terminal["reduction"])
    ).hexdigest()
    assert terminal["reduction"]["terminal"] == (
        "A__FUTURE_GUEST_IMPORT_ROOT_BINDING_REPOSITORY_IMPLEMENTED"
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


def test_g48_contains_reuse_answers_metrics_and_terminal_frontier() -> None:
    text = REPORT.read_text(encoding="utf-8")
    required = {
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
        "FUTURE_GENERATIONS_SO_FAR",
        "CCWIM_MATURITY_LEVEL",
        "COGNITION_PROVENANCE",
        "PROMPT_CONTEXT_REUSE_RATIO",
        "TOKEN_BENCHMARK",
        "LLM_COST_REDUCTION_RATIO",
        "LCRR",
        "CONSTITUTIONAL_HEALTH_EVIDENCE",
        "SHADOW_AUTOMATION_STATUS",
        "GOVERNANCE_EFFICIENCE",
        "ARCHITECTURAL_GOVERNANCE_EFFICIENCE",
        "OVERENGINEERING_RISK",
        "PROOF_PROCESS_OVERHEAD_RISK",
        "CANDIDATE_CAPABILITY",
        "SHADOW_DESIGN_TARGET",
        "CONSTITUTIONAL_CONTINUATION_PROGRESS",
        "CURRENT_APPLICABLE_ASSERTIONS",
        "HISTORICAL_OR_SUPERSEDED_SNAPSHOT_ASSERTIONS",
        "A__FUTURE_GUEST_IMPORT_ROOT_BINDING_REPOSITORY_IMPLEMENTED",
        "POST_COMMIT_IMPORT_ROOT_BINDING_AND_FULL_STATIC_READINESS_NOT_YET_AUTHENTICATED",
    }
    assert not sorted(item for item in required if item not in text)
