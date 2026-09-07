"""Focused repository-only regression proof for G77-256IX."""

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
IX = ROOT / ".github/governance/evidence/g77_256ix_post_commit_future_import_root_readiness_v1"
FORMALIZER = IX / "analysis/G77_256IX_POST_COMMIT_FUTURE_IMPORT_ROOT_READINESS_FORMALIZER_V1.py"
TERMINAL = IX / "G77_256IX_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = IX / "G77_256IX_G48_IMPLEMENTATION_REPORT_V1.md"


def load_module():
    specification = importlib.util.spec_from_file_location("g77_256ix_formalizer", FORMALIZER)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


IXF = load_module()
RUN = IXF.build_envelope()


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
    assert raw == IXF.canonical_bytes(value)
    return value


def test_exact_ratified_iw_entry_remote_identity_nested_and_scope() -> None:
    entry = RUN["reduction"]["entry"]
    assert (entry["head"], entry["tree"], entry["subject"]) == (
        IXF.IW_HEAD, IXF.IW_TREE, IXF.IW_SUBJECT,
    )
    assert entry["remote_head"] == IXF.IW_HEAD
    assert entry["index"] == "" and entry["tracked_delta"] == ""
    assert entry["worktree_scope"] == "VERIFIED__IX_EVIDENCE_ONLY"
    assert entry["nested_authority"]["clean"] is True
    assert entry["nested_authority"]["detached"] is True
    assert entry["nested_authority"]["remote_tag"] == IXF.NESTED_HEAD


def test_iw_reconstructed_from_committed_objects_without_owner_drift() -> None:
    result = RUN["reduction"]["iw_reconstruction"]
    assert result["status"] == "VERIFIED__COMMITTED_OBJECT_RECONSTRUCTION"
    assert result["iw_committed_object_binding"] == "VERIFIED"
    assert result["iw_selector_committed_binding"] == "VERIFIED"
    assert result["iw_cloud_init_committed_binding"] == "VERIFIED"
    assert result["iw_nocloud_seed_committed_binding"] == "VERIFIED"
    assert result["uncommitted_owner_dependency"] == "VERIFIED__0"
    assert result["artifact_count"] == 7 and result["inner_seal"] == "VERIFIED"


def test_iv_terminal_and_one_shot_cardinalities_are_reconstructed() -> None:
    iv = RUN["reduction"]["iv_iw_continuation"]["iv_terminal"]
    assert iv["terminal"] == "E__AUTHORIZED_OPERATION_FAILED_BEFORE_REQUEST"
    assert iv["exact_failure"] == "ModuleNotFoundError: No module named 'aigol'"
    counters = iv["operational_counters"]
    assert counters["human_operational_authority"] == 1
    assert counters["authority_consumption"] == counters["operation_attempt"] == 1
    assert counters["request"] == counters["retry"] == counters["replay"] == 0


def test_source_seed_selector_mount_environment_consumer_projection() -> None:
    owner = RUN["reduction"]["iv_iw_continuation"]["owner_graph"]
    assert owner["checkout_exists"] == "VERIFIED__MOUNTED_AT_/mnt/aigol_BEFORE_ADAPTER"
    assert owner["checkout_is_python_import_root"] == "VERIFIED__PYTHONPATH_EXACTLY_/mnt/aigol_BEFORE_ADAPTER"
    assert owner["source_to_projection_to_consumer"] == "VERIFIED"
    assert owner["ordering"] == "CHECKOUT_MOUNT__IMPORT_ROOT_EXPORT__BOOT_MARKER__ADAPTER_EXECUTION"
    assert owner["seed_projection"]["repository_bootstrap_to_nocloud_user_data"] == "VERIFIED__EXACT_BYTES"
    assert owner["seed_projection"]["nocloud_common_members_to_repository_sources"] == "VERIFIED__EXACT_BYTES"


def test_isolated_import_root_proof_depends_only_on_authenticated_if_checkout() -> None:
    proof = RUN["reduction"]["iv_iw_continuation"]["import_root"]
    assert proof["runtime_target"] == {"role": "IF", "head": IXF.IF_HEAD, "tree": IXF.IF_TREE}
    assert proof["without_guest_import_root"] == "EXPECTED_FAIL__ModuleNotFoundError_NO_MODULE_NAMED_AIGOL"
    assert proof["with_governed_guest_import_root"] == "PASS"
    assert proof["host_sys_path_false_positive"] == "VERIFIED__0"
    assert proof["verified_imports"] == [
        "aigol.runtime.canonical_che_evidence_correlation_contract_v1",
        "aigol.runtime.canonical_human_authority_act_contract_v1",
        "aigol.runtime.transport.serialization",
    ]


def test_du_eb_ee_post_commit_gate_now_passes_with_iw_baseline_and_if_target() -> None:
    readiness = RUN["reduction"]["readiness"]
    assert readiness["prior_worktree_drift_condition_removed"] == "VERIFIED"
    assert readiness["du_v2_post_commit_readiness"] == "VERIFIED"
    assert readiness["eb_v2_post_commit_readiness"] == "VERIFIED"
    assert readiness["ee_v2_post_commit_readiness"] == "VERIFIED"
    assert readiness["runtime_target"] == {"head": IXF.IF_HEAD, "tree": IXF.IF_TREE}
    assert readiness["certification_baseline"] == {"head": IXF.IW_HEAD, "tree": IXF.IW_TREE}
    assert readiness["runtime_target_equals_certification_baseline"] == "VERIFIED__NO"
    assert readiness["role_collapse"] == "VERIFIED__NO"


def test_full_authority_free_static_readiness_closes() -> None:
    readiness = RUN["reduction"]["readiness"]
    assert readiness["materialization"] == "FRESH_OPERATION_STATE_MATERIALIZED_WITHOUT_QEMU"
    assert readiness["static_readiness_result"] == "STATIC_READINESS_PASS"
    assert readiness["fm_authority_free_static_readiness"] == "VERIFIED"
    assert readiness["post_commit_import_root_readiness"] == "VERIFIED"
    assert readiness["full_static_preoperational_readiness"] == "VERIFIED"
    assert readiness["human_authorization_created"] == "VERIFIED__0"


def test_future_semantics_roles_ex_route_and_historical_firewalls() -> None:
    reduction = RUN["reduction"]
    future = reduction["future_semantics"]
    assert (future["evaluation"], future["valid_from"], future["valid_until"]) == (500, 600, 1000)
    assert future["future_semantic_mutation_count"] == future["wall_clock_dependency_count"] == "VERIFIED__0"
    assert reduction["identity_roles"]["role_collapse"] == "VERIFIED__NO"
    assert reduction["proof_reuse"]["ex_reused"] == "VERIFIED__17_OF_17"
    assert reduction["proof_reuse"]["ex_reconstructed"] == "VERIFIED__0"
    assert reduction["route_firewall"]["production_route_delta"] == "VERIFIED__0"
    assert reduction["route_firewall"]["parallel_flow_created"] == "VERIFIED__NO"
    assert reduction["historical_failure_firewall"]["reintroduced_historical_failure_count"] == "VERIFIED__0"
    assert reduction["historical_failure_firewall"]["iv_import_root_failure_successor_static_recurrence_count"] == "VERIFIED__0"


def test_ix_operational_cardinality_is_zero_e05_unchanged_and_shadow_automation_absent() -> None:
    reduction = RUN["reduction"]
    assert set(reduction["operational_counters"].values()) == {"VERIFIED__0"}
    assert reduction["e05"] == {"before": "10/18", "after": "10/18", "credit": 0, "remaining": 8}
    assert reduction["boundary_firewalls"]["shadow_automation_status"] == "VERIFIED__ABSENT"
    assert reduction["boundary_firewalls"]["p11_mutation_count"] == "VERIFIED__0"


def test_success_terminal_stops_before_fresh_human_operational_authorization() -> None:
    reduction = RUN["reduction"]
    assert reduction["terminal"] == "A__FUTURE_POST_COMMIT_IMPORT_ROOT_FULL_STATIC_READINESS_VERIFIED"
    frontier = reduction["terminal_frontier"]
    assert frontier["last_verified_edge"] == "FUTURE_POST_COMMIT_IMPORT_ROOT_FULL_STATIC_PREOPERATIONAL_READINESS"
    assert frontier["first_broken_edge"] == "FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_NOT_YET_ISSUED"
    assert frontier["auto_continuable"] == "NO"
    assert frontier["human_review_required"] == "YES"
    assert frontier["next_generation_started"] == "NO"


def test_terminal_is_canonical_duplicate_safe_inner_sealed_and_reproducible() -> None:
    terminal = load_unique(TERMINAL)
    assert terminal == RUN
    assert terminal["reduction_sha256"] == hashlib.sha256(IXF.canonical_bytes(terminal["reduction"])).hexdigest()
    with pytest.raises(IXF.IXReadinessError, match="DUPLICATE_JSON_KEY"):
        IXF.unique_object([("a", 1), ("a", 2)])


def test_formalizer_ast_and_operational_invocation_tokens_absent() -> None:
    source = FORMALIZER.read_text(encoding="utf-8")
    ast.parse(source, filename=str(FORMALIZER))
    prohibited = (
        "render_human_authorization_presentation(", "validate_execution_admission(",
        "validate_final_admission(", "qemu-system-x86_64\",", "subprocess.Popen(",
        "subprocess.call(", "os.exec",
    )
    assert all(token not in source for token in prohibited)


def test_exact_six_g48_headings_and_required_metrics() -> None:
    text = REPORT.read_text(encoding="utf-8")
    headings = [line for line in text.splitlines() if line.startswith("# ")]
    assert headings == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    required = {
        "Reuse Impact Assessment", "Infrastructure Amortization", "CCWIM",
        "COGNITION_PROVENANCE", "COGNITION_ASSISTED_HANDOFF", "PROMPT_CONTEXT_REUSE_RATIO",
        "REPOSITORY_DERIVED_EXECUTION_CONTEXT_RATIO", "CONSTITUTIONAL_PROMPT_EXTERNALIZATION_RATIO",
        "TOKEN_BENCHMARK", "LLM_COST_REDUCTION_RATIO", "LCRR", "AIGOL_CODEX_WORK_SHARE",
        "PROJECT_PROGRESS_ESTIMATE", "CONSTITUTIONAL_HEALTH_EVIDENCE", "SHADOW_AUTOMATION_STATUS",
        "CONSTITUTIONAL_FRONTIER_DISTANCE", "E05_FRONTIER_DISTANCE", "SELECTED_E05_LOCAL_FRONTIER_DISTANCE",
        "GOVERNANCE_EFFICIENCE", "ARCHITECTURAL_GOVERNANCE_EFFICIENCE", "PROOF_REUSE_EFFICIENCY",
        "OVERENGINEERING_RISK", "PROOF_PROCESS_OVERHEAD_RISK", "CANDIDATE_CAPABILITY",
        "SHADOW_DESIGN_TARGET", "CONSTITUTIONAL_CONTINUATION_PROGRESS", "Historical Failure Firewall",
        "EX_REUSED", "E05_GENERATIONS_PER_CREDIT", "OPERATIONAL_ATTEMPTS_PER_CREDIT",
        "MARGINAL_E05_GENERATION_COST", "MARGINAL_NEW_INFRASTRUCTURE_PER_E05_CREDIT",
        "INFRASTRUCTURE_AMORTIZATION_SIGNAL", "EXPECTED_NEXT_CREDIT_GENERATION_COUNT",
    }
    assert all(token in text for token in required)


def test_only_ix_evidence_is_uncommitted_and_index_is_empty() -> None:
    assert subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True).strip() == ""
    assert subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, text=True).strip() == ""
    lines = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=all"], cwd=ROOT, text=True).splitlines()
    assert all(line.startswith("?? " + IXF.IX_ROOT.as_posix() + "/") for line in lines)
