#!/usr/bin/env python3
"""Focused repository-only validation for continued G77-256IG."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
IG = ROOT / ".github/governance/evidence/g77_256ig_future_post_if_commit_rebind_v1"
VALIDATOR_PATH = IG / "validator/G77_256IG_POST_IF_COMMIT_READINESS_VALIDATOR_V1.py"
TERMINAL = IG / "G77_256IG_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = IG / "G77_256IG_G48_IMPLEMENTATION_REPORT_V1.md"


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def load_unique(path: Path) -> dict:
    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"duplicate JSON key: {key}")
            value[key] = item
        return value
    value = json.loads(path.read_bytes(), object_pairs_hook=unique)
    assert isinstance(value, dict)
    return value


VALIDATOR = load_module(VALIDATOR_PATH, "g77_256ig_test_validator")


def test_exact_committed_if_entry_and_nested_authority() -> None:
    observed = VALIDATOR.authenticate_entry(ROOT)
    assert observed["head"] == VALIDATOR.IF_HEAD
    assert observed["tree"] == VALIDATOR.IF_TREE
    assert observed["subject"] == VALIDATOR.IF_SUBJECT
    assert observed["remote_tracking_head"] == VALIDATOR.IF_HEAD
    assert observed["index"] == ""
    assert observed["nested"]["head"] == VALIDATOR.NESTED_HEAD
    assert observed["nested"]["tree"] == VALIDATOR.NESTED_TREE
    assert observed["nested"]["branch"] == observed["nested"]["status"] == ""


def test_all_required_if_objects_are_committed_and_hash_authenticated() -> None:
    identities = VALIDATOR.committed_identity_map(ROOT)
    assert set(identities) == set(VALIDATOR.COMMITTED_IF_PATHS)
    assert len(identities) == 16
    assert all(item["status"] == "VERIFIED" for item in identities.values())
    assert all(len(item["git_blob"]) == 40 for item in identities.values())


def test_if_terminal_act_che_and_future_semantics_reconstruct_exactly() -> None:
    value = VALIDATOR.reconstruct_if(ROOT)
    reduction = value["terminal"]
    binding = value["act_che"]
    assert reduction["readiness"]["future_repository_formalization"] == "VERIFIED"
    assert reduction["readiness"]["future_live_binding"] == "NOT_PROVEN"
    assert reduction["e05"]["after"] == "10/18" and reduction["e05"]["credit"] == 0
    act = binding["human_authority_act_representation"]
    che = binding["che_correlation"]
    assert act["payload_digest"] == VALIDATOR.FUTURE_PAYLOAD_DIGEST
    assert act["payload"]["valid_from_unix_ns"] == 600
    assert act["payload"]["valid_until_unix_ns"] == 1000
    assert binding["evaluation_time_unix_ns"] == 500
    assert che["source_act_digest"] == VALIDATOR.SOURCE_ACT_DIGEST
    assert che["correlation_identity"] == VALIDATOR.CORRELATION_IDENTITY
    assert binding["human_operational_authority"] == 0


def test_committed_if_contains_static_capabilities_but_selects_ie_checkout() -> None:
    closure = VALIDATOR.committed_checkout_closure(ROOT)
    for key in (
        "committed_if_route_membership", "committed_if_adapter_binding",
        "committed_if_nocloud_binding", "committed_if_act_che_binding",
    ):
        assert closure[key].startswith("VERIFIED")
    assert closure["launcher_selected_head"] == VALIDATOR.IE_HEAD
    assert closure["launcher_selected_tree"] == VALIDATOR.IE_TREE
    assert closure["candidate_required_head"] == VALIDATOR.IE_HEAD
    assert closure["context_repository_head"] == VALIDATOR.IE_HEAD
    assert closure["exact_if_head"] == VALIDATOR.IF_HEAD
    assert closure["committed_if_checkout_closure_status"] == "NOT_PROVEN__SOLE_LAUNCHER_SELECTS_IE_NOT_IF"
    assert closure["context_to_committed_if_binding"] == "NOT_PROVEN__CONTEXT_BINDS_IE"


def test_candidate_runtime_context_and_deterministic_time_statuses() -> None:
    closure = VALIDATOR.committed_checkout_closure(ROOT)
    assert closure["candidate_identity"] == closure["runtime_identity"] == "eafb6dcfe4593872b140aa4de44529b3c60d66bb6bcee5441932090ca32b64da"
    assert closure["candidate_runtime_byte_identity_status"] == "VERIFIED"
    assert closure["context_identity"] == "a71c6a2d74553787f6fbea7359e0f60912774ae8107fb6e078d0ebb888977015"
    assert closure["deterministic_time_fixture_status"] == "VERIFIED"
    assert closure["deterministic_time_adapter_status"] == "VERIFIED__REPOSITORY_FUNCTION_ONLY"
    assert closure["deterministic_time_guest_projection_status"].startswith("NOT_PROVEN")
    assert closure["wall_clock_dependency_count_on_future_path"] == 0
    assert closure["new_clock_infrastructure_count"] == 0
    assert closure["future_guest_command_count"] == 0


def test_checkout_bootstrap_nocloud_and_base_image_firewall() -> None:
    closure = VALIDATOR.committed_checkout_closure(ROOT)
    assert closure["bootstrap_binding"] == "VERIFIED__STATIC_NONOPERATIONAL"
    assert closure["adapter_binding"] == "VERIFIED__COMMITTED_FILE"
    assert closure["cloud_init_binding"] == "VERIFIED__COMMITTED_STATIC_TEMPLATE"
    assert closure["nocloud_binding"] == "VERIFIED__EXACT_BYTE_PROJECTION"
    assert closure["base_image_binding"] == "VERIFIED"
    assert closure["host_guest_equivalence"].startswith("NOT_PROVEN")


def test_stale_if_receipts_are_not_promoted_to_current_if_proof() -> None:
    owners = VALIDATOR.readiness_owners(ROOT)
    assert owners["du"] == "VERIFIED__MANIFEST_CONTRACT_ONLY__CANDIDATE_REMAINS_IE_BOUND"
    assert owners["eb"] == "NOT_PROVEN__REQUIRED_HEAD_IE_DIFFERS_CURRENT_IF"
    assert owners["ee"] == "NOT_PROVEN__REQUIRED_HEAD_IE_DIFFERS_CURRENT_IF"
    assert owners["gn"] == "NOT_PROVEN__NO_COMMITTED_IF_BOUND_HUMAN_PRESENTATION"
    assert owners["gl"] == "NOT_APPLICABLE__NO_AUTHORITY_OR_RECEIPT_PARENT_CREATED"


def test_interruption_recovery_is_same_generation_without_replay_claim() -> None:
    reduction = VALIDATOR.terminal_reduction(ROOT)
    recovery = reduction["ig_interruption_recovery"]
    assert recovery["ig_existing_delta_status"] == "VERIFIED__PARTIALLY_COMPLETED_BEFORE_INTERRUPTION"
    assert recovery["ig_replay_required"] == "VERIFIED__NO"
    ccwim = reduction["ccwim"]
    assert ccwim["provider_usage_interruption_recovery"] == "VERIFIED__BOUNDED_IG_DELTA_RECOVERED_WITHOUT_REPLAY"
    assert ccwim["same_generation_continuation_status"] == "VERIFIED__G77_256IG_CONTINUED"
    assert ccwim["same_account_continuation_status"].startswith("NOT_PROVEN")
    assert ccwim["uncommitted_delta_recovery"] == "VERIFIED__ONE_AUTHENTIC_IG_VALIDATOR_RECOVERED"
    assert ccwim["cross_worker_state_recovery_level"].startswith("NOT_APPLICABLE")


def test_terminal_reduction_is_canonical_sealed_and_fail_closed() -> None:
    envelope = load_unique(TERMINAL)
    assert TERMINAL.read_bytes() == VALIDATOR.canonical_bytes(envelope)
    reduction = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(VALIDATOR.canonical_bytes(reduction)).hexdigest()
    assert reduction["readiness"]["future_preoperational_readiness"] == "NOT_PROVEN"
    assert reduction["readiness"]["next_operational_generation_eligible"] == "NOT_PROVEN"
    assert reduction["terminal_control"]["first_broken_edge"] == VALIDATOR.FIRST_BROKEN_EDGE
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"]["after"] == "10/18" and reduction["e05"]["credit"] == 0
    assert reduction["ex"] == {"ex_reused": "17/17", "ex_reconstructed": 0, "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED"}


def test_validator_has_no_operational_entry_and_report_has_six_headings() -> None:
    tree = ast.parse(VALIDATOR_PATH.read_text(encoding="utf-8"))
    calls = {
        node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, (ast.Attribute, ast.Name))
    }
    assert not calls.intersection({"submit_human_act", "claim_and_invoke_once", "main", "time", "time_ns", "sleep"})
    report = REPORT.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]

