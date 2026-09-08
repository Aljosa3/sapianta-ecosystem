"""Focused repository-only regression proof for G77-256JA."""

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
JA = ROOT / ".github/governance/evidence/g77_256ja_future_post_commit_readiness_v1"
FORMALIZER = JA / "analysis/G77_256JA_POST_COMMIT_READINESS_FORMALIZER_V1.py"
TERMINAL = JA / "G77_256JA_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = JA / "G77_256JA_G48_IMPLEMENTATION_REPORT_V1.md"


def load_module():
    specification = importlib.util.spec_from_file_location("g77_256ja_formalizer", FORMALIZER)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


JAF = load_module()
RUN = JAF.build_envelope()


def load_unique(path: Path) -> dict:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            assert key not in result
            result[key] = value
        return result

    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique)
    assert raw == JAF.canonical_bytes(value)
    return value


def test_exact_ratified_iz_entry_remote_identity_nested_and_scope() -> None:
    entry = RUN["reduction"]["entry"]
    assert (entry["head"], entry["tree"], entry["subject"]) == (
        JAF.IZ_HEAD, JAF.IZ_TREE, JAF.IZ_SUBJECT,
    )
    assert entry["remote_head"] == JAF.IZ_HEAD
    assert entry["index"] == entry["tracked_delta"] == ""
    assert entry["worktree_scope"] == "VERIFIED__JA_EVIDENCE_ONLY"
    assert entry["nested_authority"]["clean"] is True
    assert entry["nested_authority"]["detached"] is True
    assert entry["nested_authority"]["remote_tag"] == JAF.NESTED_HEAD


def test_iz_reconstructed_from_committed_objects_and_inner_seal() -> None:
    iz = RUN["reduction"]["iz_reconstruction"]
    assert iz["iz_committed_binding"] == iz["iz_remote_ratification"] == "VERIFIED"
    assert iz["artifact_count"] == 6
    assert iz["inner_seal"] == "VERIFIED"
    assert iz["iz_terminal"].endswith("REPOSITORY_ONLY_STATIC_READINESS_VERIFIED")


def test_exact_two_owner_future_only_rebind_and_one_route() -> None:
    owner = RUN["reduction"]["production_owner_binding"]
    assert owner["production_owner_mutation_count"] == "VERIFIED__2"
    assert owner["non_future_mappings_unchanged"] == "VERIFIED"
    assert owner["future_selector_binding"] == owner["future_bootstrap_binding"] == "VERIFIED"
    assert owner["production_route_before"] == owner["production_route_after"] == "VERIFIED__1"
    assert owner["production_route_delta"] == "VERIFIED__0"
    assert owner["parallel_flow_created"] == "VERIFIED__NO"


def test_former_worktree_drift_barrier_is_closed_without_role_collapse() -> None:
    live = RUN["reduction"]["live_binding"]
    assert live["former_worktree_drift_barrier"] == "VERIFIED__CLOSED"
    assert live["du_v2"] == "VERIFIED__CURRENT_APPLICABLE_PASS"
    assert live["eb_v2"] == live["ee_v2"] == "VERIFIED__POST_COMMIT_POSITIVE_PATH"
    assert live["runtime_target"]["head"] == JAF.IF_HEAD
    assert live["runtime_target"]["tree"] == JAF.IF_TREE
    assert live["certification_baseline"] == {"head": JAF.IZ_HEAD, "tree": JAF.IZ_TREE}
    assert live["runtime_certification_role_separation"] == "VERIFIED__PRESERVED"
    assert live["runtime_target"] != live["certification_baseline"]


def test_family_local_v2_option_b_dispatch_remains_fail_closed() -> None:
    live = RUN["reduction"]["live_binding"]
    assert live["nested_certification_baseline_option_b"] == "VERIFIED"
    assert live["family_local_fail_closed_major_dispatch"] == "VERIFIED"
    assert live["v1_reinterpretation"] == "VERIFIED__0"
    assert live["caller_selected_version"] == "VERIFIED__0"
    assert live["mixed_major_acceptance"] == live["downgrade"] == "VERIFIED__0"


def test_exact_future_semantics_and_existing_p11_route_are_static_only() -> None:
    future = RUN["reduction"]["adapter_and_future_semantics"]
    assert (
        future["evaluation_time_unix_ns"], future["baseline_valid_from_unix_ns"],
        future["future_valid_from_unix_ns"], future["valid_until_unix_ns"],
    ) == (500, 100, 600, 1000)
    assert future["relation"] == "500 < 600 < 1000"
    assert future["independent_mutation_count"] == 1
    assert future["independent_mutated_coordinate"] == "valid_from_unix_ns"
    assert future["payload_digest"] == "9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547"
    assert future["expected_denial_reason"] == "operational Human act is not current"
    assert future["wall_clock_dependency"] is False
    assert future["adapter_main_invoked"] == "VERIFIED__NO"
    assert future["duplicate_p11_currentness_logic"] == "VERIFIED__0"


def test_nocloud_exact_projection_import_root_entrypoint_and_no_network() -> None:
    projection = RUN["reduction"]["nocloud_and_guest_import_root"]
    assert projection["exact_projection"] == "VERIFIED"
    assert projection["guest_checkout_import_root"] == "/mnt/aigol"
    assert projection["five_argument_fm_guest_contract"] == "VERIFIED"
    assert projection["network_dependency"] == "VERIFIED__0"
    assert projection["iv_import_root_failure_reintroduced"] == "VERIFIED__NO"
    assert projection["iy_entrypoint_absence_reintroduced"] == "VERIFIED__NO"


def test_ex_reuse_p11_and_historical_failure_firewalls() -> None:
    reduction = RUN["reduction"]
    assert reduction["proof_reuse"]["ex_reused"] == "VERIFIED__17_OF_17"
    assert reduction["proof_reuse"]["ex_reconstructed"] == "VERIFIED__0"
    firewall = reduction["historical_failure_firewall"]
    assert firewall["checked_failure_class_count"] == "VERIFIED__43"
    assert firewall["reintroduced_historical_failure_count"] == "VERIFIED__0"
    assert firewall["p11_mutation_count"] == "VERIFIED__0"
    assert firewall["shadow_automation_status"] == "VERIFIED__ABSENT"


def test_ja_operational_cardinality_zero_and_e05_unchanged() -> None:
    reduction = RUN["reduction"]
    assert set(reduction["operational_counters"].values()) == {"VERIFIED__0"}
    assert reduction["e05"] == {
        "before": "VERIFIED__10_OF_18", "after": "VERIFIED__10_OF_18", "credit": "VERIFIED__0",
    }


def test_success_terminal_stops_for_human_review() -> None:
    reduction = RUN["reduction"]
    assert reduction["terminal"] == "A__FUTURE_POST_COMMIT_LIVE_BINDING_AND_OPERATIONAL_READINESS_VERIFIED"
    frontier = reduction["terminal_frontier"]
    assert frontier["first_broken_edge"] == "FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_NOT_PRESENT"
    assert frontier["auto_continuable"] == "NO"
    assert frontier["human_review_required"] == "YES"
    assert frontier["next_generation_started"] == "NO"


def test_terminal_is_canonical_duplicate_safe_inner_sealed_and_reproducible() -> None:
    terminal = load_unique(TERMINAL)
    assert terminal == RUN
    assert terminal["reduction_sha256"] == hashlib.sha256(
        JAF.canonical_bytes(terminal["reduction"])
    ).hexdigest()
    with pytest.raises(JAF.JAReadinessError, match="DUPLICATE_JSON_KEY"):
        JAF.unique_object([("a", 1), ("a", 2)])


def test_formalizer_ast_and_operational_invocations_absent() -> None:
    source = FORMALIZER.read_text(encoding="utf-8")
    ast.parse(source, filename=str(FORMALIZER))
    prohibited = (
        ".main()", "render_human_authorization_presentation(", "validate_execution_admission(",
        "validate_final_admission(", "materialize_operation_state(", "authority_free_static_readiness(",
        "subprocess.Popen(", "subprocess.call(", "os.exec",
    )
    assert all(token not in source for token in prohibited)


def test_exact_six_g48_headings_and_all_commission_metrics() -> None:
    text = REPORT.read_text(encoding="utf-8")
    headings = [line for line in text.splitlines() if line.startswith("# ")]
    assert headings == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    required = {
        "Reuse Impact Assessment", "Constitutional Health Evidence", "Shadow Automation",
        "Constitutional Frontier Distance", "Governance Efficiency", "Cognition-Assisted Handoff",
        "CCWIM", "Attribution / Prompt / Token / Cost", "Overengineering Risk",
        "Candidate Capability / Shadow Design Target", "Constitutional Continuation Progress",
        "Infrastructure Amortization", "Historical Failure Firewall",
        "CONSTITUTIONAL_FRONTIER_DISTANCE", "CONSTITUTIONAL_FRONTIER_DISTANCe",
        "PROJECT_PROGRESS", "E05_BEFORE", "E05_AFTER", "EX_REUSED", "EX_RECONSTRUCTED",
        "PRODUCTION_OWNER_MUTATION_COUNT", "PRODUCTION_ROUTE_DELTA", "P11_MUTATION_COUNT",
        "COGNITION_ASSISTED_HANDOFF", "COGNITION_PROVENANCE", "AIGOL_CODEX_WORK_SHARE",
        "PROMPT_CONTEXT_REUSE_RATIO", "REPOSITORY_DERIVED_EXECUTION_CONTEXT_RATIO",
        "CONSTITUTIONAL_PROMPT_EXTERNALIZATION_RATIO", "TOKEN_BENCHMARK",
        "LLM_COST_REDUCTION_RATIO", "LCRR", "AUTO_CONTINUABLE", "HUMAN_REVIEW_REQUIRED",
    }
    assert all(token in text for token in required)


def test_only_ja_evidence_is_uncommitted_and_index_is_empty() -> None:
    assert subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True
    ).strip() == ""
    assert subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, text=True
    ).strip() == ""
    lines = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=all"], cwd=ROOT, text=True
    ).splitlines()
    assert all(line.startswith("?? " + JAF.JA_ROOT.as_posix() + "/") for line in lines)
