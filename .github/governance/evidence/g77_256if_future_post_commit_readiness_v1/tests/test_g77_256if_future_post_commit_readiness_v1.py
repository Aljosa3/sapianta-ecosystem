#!/usr/bin/env python3
"""Focused repository-only validation for G77-256IF."""

from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
IF = ROOT / ".github/governance/evidence/g77_256if_future_post_commit_readiness_v1"
BINDER_PATH = IF / "binding/G77_256IF_POST_IE_FUTURE_BINDING_V1.py"
ADAPTER_PATH = IF / "adapter/G77_256IF_FUTURE_VECTOR_ADAPTER_V1.py"
LIVE = IF / "live_binding"
ACT_CHE = LIVE / "G77_256IF_FUTURE_ACT_CHE_BINDING_V1.json"
CANDIDATE = LIVE / "candidate/G77_256IF_FUTURE_CURRENT_CANDIDATE_V1.json"
RUNTIME = LIVE / "runtime_projection/G77_256IF_FUTURE_CURRENT_CANDIDATE_V1.json"
CONTEXT = LIVE / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
EB = LIVE / "bindings/G77_256IF_EB_RECEIPT_V1.json"
EE = LIVE / "bindings/G77_256IF_EE_RECEIPT_V1.json"
TERMINAL = IF / "G77_256IF_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = IF / "G77_256IF_G48_IMPLEMENTATION_REPORT_V1.md"


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


BINDER = load_module(BINDER_PATH, "g77_256if_test_binder")
ADAPTER = load_module(ADAPTER_PATH, "g77_256if_test_adapter")


def test_exact_ie_checkpoint_ancestry_and_nested_authority() -> None:
    observed = BINDER.authenticate_entry(ROOT)
    assert observed["head"] == BINDER.IE_HEAD
    assert observed["tree"] == BINDER.IE_TREE
    assert observed["subject"] == BINDER.IE_SUBJECT
    assert observed["remote_tracking_head"] == BINDER.IE_HEAD
    assert observed["index"] == ""
    assert observed["nested"]["head"] == BINDER.NESTED_HEAD
    assert observed["nested"]["tree"] == BINDER.NESTED_TREE
    assert observed["nested"]["branch"] == observed["nested"]["status"] == ""


def test_ie_reconstruction_and_exact_future_semantics() -> None:
    ie = BINDER.reconstruct_ie(ROOT)
    packet = ie["packet"]
    assert ie["result"]["future_repository_formalization"] == "VERIFIED"
    assert packet["evaluation_time_unix_ns"] == 500
    assert packet["baseline_payload"]["valid_from_unix_ns"] == 100
    assert packet["future_payload"]["valid_from_unix_ns"] == 600
    assert packet["future_payload"]["valid_until_unix_ns"] == 1000
    assert packet["differing_payload_fields"] == ["valid_from_unix_ns"]
    assert packet["independent_mutation_count"] == 1
    assert packet["dependent_recomputed_coordinates"] == ["human_authority_act.payload_digest"]
    assert packet["future_payload_digest"] == "sha256:9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547"


def test_one_fresh_nonauthorizing_act_and_exact_che_dependencies() -> None:
    envelope = load_unique(ACT_CHE)
    assert ACT_CHE.read_bytes() == BINDER.canonical_bytes(envelope)
    assert envelope["binding_sha256"] == hashlib.sha256(BINDER.canonical_bytes(envelope["binding"])).hexdigest()
    binding = envelope["binding"]
    act = binding["human_authority_act_representation"]
    che = binding["che_correlation"]
    assert act["authority_act_identity"] == ADAPTER.ACT_IDENTITY
    assert act["metadata"]["human_authority_present"] is False
    assert act["payload_digest"] == "sha256:9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547"
    assert che["authority_payload_digest"] == act["payload_digest"]
    assert che["source_act_digest"] == "sha256:7167b0725d2c84bafde1d0060f512b0fa358d777ec1beff8b7c68d22ee6502e8"
    assert che["correlation_identity"] == "CHE-CORRELATION-15b2680b5577da169cecf9efb3231e2e6f6467e6f409fa2594b04128f998e454"
    assert binding["semantic_independent_mutation_count"] == 1
    assert binding["live_binding_dependent_recomputation_count"] == 3
    assert binding["human_operational_authority"] == 0
    assert binding["request_count"] == binding["operation_attempt_count"] == 0


def test_che_recomputes_for_outer_act_change_without_payload_mutation() -> None:
    act = ADAPTER.construct_repository_only_future_act(ROOT)
    original = ADAPTER.construct_repository_only_che(ROOT, act)
    value = act.to_dict()
    value["authority_act_identity"] = "G77_256IF_REPOSITORY_ONLY_FUTURE_ACT_REPRESENTATION_002"
    from aigol.runtime.canonical_human_authority_act_contract_v1 import CanonicalHumanAuthorityActV1
    changed = CanonicalHumanAuthorityActV1.from_dict(value)
    updated = ADAPTER.construct_repository_only_che(ROOT, changed)
    assert updated.authority_payload_digest == original.authority_payload_digest
    assert updated.source_act_digest != original.source_act_digest
    assert updated.correlation_identity != original.correlation_identity


def test_existing_single_route_extended_statically_but_committed_ie_rejects_future() -> None:
    route = BINDER.route_state(ROOT)
    assert route["production_route_before"] == route["production_route_after"] == "VERIFIED__1"
    assert route["production_route_delta"] == "VERIFIED__0"
    assert route["new_production_route_count"] == "VERIFIED__0"
    assert route["future_route_membership_after"] == "VERIFIED__REPOSITORY_STATIC_BINDING_ONLY"
    assert route["committed_ie_checkout_contains_future_membership"] is False
    assert route["checkout_host_guest_equivalence"] == "NOT_PROVEN"


def test_deterministic_time_projection_is_explicit_and_has_no_clock_call() -> None:
    assert ADAPTER.deterministic_submission_kwargs(ROOT) == {"now_unix_ns": 500}
    tree = ast.parse(ADAPTER_PATH.read_text(encoding="utf-8"))
    calls = {
        node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, (ast.Attribute, ast.Name))
    }
    assert not calls.intersection({"time", "time_ns", "now", "sleep", "submit_human_act", "claim_and_invoke_once", "main"})


def test_candidate_runtime_context_and_du_eb_ee_bind_committed_ie() -> None:
    assert CANDIDATE.read_bytes() == RUNTIME.read_bytes()
    candidate = load_unique(CANDIDATE)
    context = load_unique(CONTEXT)
    assert candidate["manifest"]["required_head"] == BINDER.IE_HEAD
    assert candidate["manifest"]["source_tree"] == BINDER.IE_TREE
    assert candidate["manifest"]["authority_state"]["lifecycle_state"] == "NOT_CREATED"
    assert hashlib.sha256(CANDIDATE.read_bytes()).hexdigest() == context["candidate_manifest_sha256"]
    assert context["repository_head"] == BINDER.IE_HEAD
    assert context["repository_tree"] == BINDER.IE_TREE
    assert context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["head"] == BINDER.IE_HEAD
    assert context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["tree"] == BINDER.IE_TREE
    eb = load_unique(EB)["receipt"]
    ee = load_unique(EE)["receipt"]
    assert eb["overall_result"] == "PASS"
    assert ee["pre_materialization_runtime_path_binding_result"] == "PASS"
    assert ee["identity_results"]["candidate_runtime_byte_identity"] == "PASS"


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value["binding"]["human_authority_act_representation"]["payload"].__setitem__("valid_until_unix_ns", 1001),
        lambda value: value["binding"]["che_correlation"].__setitem__("authority_payload_digest", "sha256:" + "0" * 64),
        lambda value: value["binding"].__setitem__("human_operational_authority", 1),
    ],
)
def test_binding_tampering_is_detectable(mutation) -> None:
    value = deepcopy(load_unique(ACT_CHE))
    mutation(value)
    assert value["binding_sha256"] != hashlib.sha256(BINDER.canonical_bytes(value["binding"])).hexdigest()


def test_terminal_reduction_is_canonical_sealed_and_fail_closed() -> None:
    envelope = load_unique(TERMINAL)
    assert TERMINAL.read_bytes() == BINDER.canonical_bytes(envelope)
    reduction = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(BINDER.canonical_bytes(reduction)).hexdigest()
    assert reduction["readiness"] == {
        "first_broken_edge": "COMMITTED_IE_CHECKOUT_DOES_NOT_CONTAIN_IF_FUTURE_ROUTE_AND_DETERMINISTIC_TIME_PROJECTION",
        "future_live_binding": "NOT_PROVEN",
        "future_operational_capability": "NOT_PROVEN",
        "future_preoperational_readiness": "NOT_PROVEN",
        "future_repository_formalization": "VERIFIED",
        "future_route_binding": "VERIFIED__REPOSITORY_STATIC_BINDING_ONLY",
        "next_operational_generation_eligible": "NOT_PROVEN",
    }
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"] == {"before": "10/18", "after": "10/18", "credit": 0, "required": 18, "satisfied": 10, "remaining": 8}
    assert reduction["historical_failure_firewall"]["reintroduced_historical_failure_count"] == 0
    assert reduction["ex"] == {"status": "VERIFIED", "ex_reused": "17/17", "ex_reconstructed": 0}


def test_no_operational_entrypoint_and_exact_six_heading_report() -> None:
    for path in (BINDER_PATH, ADAPTER_PATH):
        source = path.read_text(encoding="utf-8")
        assert "qemu-system" not in source
        assert "subprocess.run([\"qemu" not in source
    report = REPORT.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]

