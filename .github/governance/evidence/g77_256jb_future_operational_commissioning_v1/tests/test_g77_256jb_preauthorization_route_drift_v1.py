#!/usr/bin/env python3
"""Focused fail-closed validation for G77-256JB Phase A."""

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
JB = ROOT / ".github/governance/evidence/g77_256jb_future_operational_commissioning_v1"
MATERIALIZER = JB / "orchestration/G77_256JB_PREAUTHORIZATION_MATERIALIZER_V1.py"
REDUCER = JB / "analysis/G77_256JB_PREAUTHORIZATION_ROUTE_DRIFT_REDUCER_V1.py"
TERMINAL = JB / "G77_256JB_SPCE_TERMINAL_PREAUTHORIZATION_ROUTE_DRIFT_V1.json"
REPORT = JB / "G77_256JB_G48_PREAUTHORIZATION_ROUTE_DRIFT_REPORT_V1.md"


def load(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


M = load(MATERIALIZER, "g77_256jb_test_materializer")
R = load(REDUCER, "g77_256jb_test_reducer")


def canonical(path: Path) -> dict:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=M.unique_object)
    assert isinstance(value, dict)
    assert raw == M.canonical_bytes(value)
    return value


def test_exact_ratified_ja_entry_nested_authority_and_terminal() -> None:
    entry = M.authenticate_entry(M.HEAD, M.NESTED_HEAD)
    assert (entry["head"], entry["tree"], entry["subject"]) == (M.HEAD, M.TREE, M.SUBJECT)
    assert entry["local_remote_equality"] == "VERIFIED"
    assert entry["nested_authority"]["clean"] is True
    assert entry["nested_authority"]["detached"] is True
    ja = M.reconstruct_ja()
    assert ja["terminal"] == "A__FUTURE_POST_COMMIT_LIVE_BINDING_AND_OPERATIONAL_READINESS_VERIFIED"
    assert ja["ex_reused"] == "VERIFIED__17_OF_17"
    assert ja["ex_reconstructed"] == "VERIFIED__0"


def test_fresh_identity_semantics_v2_roles_and_no_network() -> None:
    identity = M.derive_identity()
    assert identity["operation_generation"] == M.GENERATION
    assert identity["operation_identity"] == M.OPERATION
    future = M.authenticate_future_semantics()
    assert (future["evaluation"], future["valid_from"], future["valid_until"]) == (500, 600, 1000)
    context = canonical(JB / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json")
    assert context["repository_head"] == M.HEAD
    assert context["repository_tree"] == M.TREE
    assert all(value != "-net" and not value.startswith("-netdev") for value in context["canonical_argv"])
    eb = canonical(JB / "live_binding/v2_readiness/bindings/G77_256JB_EB_RECEIPT_V2.json")["receipt"]
    ee = canonical(JB / "live_binding/v2_readiness/bindings/G77_256JB_EE_RECEIPT_V2.json")["receipt"]
    assert eb["certification_baseline"] == {"head": M.HEAD, "tree": M.TREE}
    assert (eb["runtime_target_selection_binding"]["head"], eb["runtime_target_selection_binding"]["tree"]) == (M.IF_HEAD, M.IF_TREE)
    assert ee["certification_baseline"] == eb["certification_baseline"]
    assert ee["runtime_target_selection_binding"] == eb["runtime_target_selection_binding"]


def test_exact_fm_guest_context_owner_drift_is_present_and_fail_closed() -> None:
    context = canonical(JB / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json")
    checkout = Path(context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["path"])
    owner = checkout / R.FM_OWNER
    assert hashlib.sha256(owner.read_bytes()).hexdigest() == R.OBSERVED_OWNER_SHA256
    assert context["wrapper_fc_er_che_schema_hashes"]["fresh_operation_context_owner"] == R.EXPECTED_OWNER_SHA256
    assert R.OBSERVED_OWNER_SHA256 != R.EXPECTED_OWNER_SHA256
    candidate = JB / "live_binding/candidate/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json"
    observed = M.FM.observe_context_assets(ROOT, context, candidate.relative_to(ROOT))
    candidate_relative, _ = M.FM.resolve_candidate_source(ROOT, candidate.relative_to(ROOT))
    expected = M.FM.context_asset_expectations(context, Path(candidate_relative))
    assert observed != expected
    assert observed[str(owner)] == R.OBSERVED_OWNER_SHA256
    assert expected[str(owner)] == R.EXPECTED_OWNER_SHA256


def test_terminal_seal_zero_counters_and_no_human_artifacts() -> None:
    envelope = canonical(TERMINAL)
    reduction = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(M.canonical_bytes(reduction)).hexdigest()
    assert reduction["terminal"] == "M__CERTIFIED_ROUTE_DRIFT_DETECTED"
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["authority_boundary"]["human_authority_present"] is False
    assert reduction["authority_boundary"]["phase_b_started"] is False
    assert reduction["e05"] == {
        "before": "VERIFIED__10_OF_18", "after": "VERIFIED__10_OF_18", "credit": "VERIFIED__0"
    }
    for name in (
        "G77_256JB_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json",
        "G77_256JB_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json",
        "G77_256JB_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt",
        "G77_256JB_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt",
        "G77_256JB_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json",
    ):
        assert not (JB / name).exists()


def test_canonical_json_ast_production_and_index_firewalls() -> None:
    for path in sorted(JB.rglob("*.json")):
        canonical(path)
    for path in sorted(JB.rglob("*.py")):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    assert subprocess.check_output(
        ["git", "diff", "--name-only", M.HEAD, "--", "aigol/runtime", "sapianta_system",
         ".github/governance/evidence/g77_256ec_p11_operational_v1"], cwd=ROOT, text=True
    ).strip() == ""
    assert subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True).strip() == ""


def test_historical_firewall_count_and_failure_classification() -> None:
    reduction = canonical(TERMINAL)["reduction"]
    firewall = reduction["historical_failure_firewall"]
    assert len(firewall["checked_failure_classes"]) == 59
    assert firewall["checked_failure_class_count"] == "VERIFIED__59"
    assert firewall["reintroduced_historical_failure_count"].startswith("VERIFIED__1__")
    assert reduction["reuse"]["production_route_delta"] == "VERIFIED__0"
    assert reduction["reuse"]["p11_mutation_count"] == "VERIFIED__0"


def test_g48_exact_six_h1_headings_and_required_metrics() -> None:
    text = REPORT.read_text(encoding="utf-8")
    assert [line for line in text.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    required = (
        "Reuse Impact Assessment", "Constitutional Health Evidence", "Shadow Automation",
        "CONSTITUTIONAL_FRONTIER_DISTANCE", "CONSTITUTIONAL_FRONTIER_DISTANCe",
        "GOVERNANCE_EFFICIENCE", "Cognition-Assisted Handoff", "Cognition Provenance",
        "CCWIM_MATURITY_LEVEL", "AIGOL_CODEX_WORK_SHARE", "PROMPT_CONTEXT_REUSE_RATIO",
        "TOKEN_BENCHMARK", "LCRR", "OVERENGINEERING_RISK", "CANDIDATE_CAPABILITY",
        "SHADOW_DESIGN_TARGET", "CONSTITUTIONAL_CONTINUATION_PROGRESS",
        "Infrastructure Amortization", "Historical Failure Firewall",
        "CHECKED_FAILURE_CLASS_COUNT", "LAST_VERIFIED_EDGE", "FIRST_BROKEN_EDGE",
    )
    assert all(token in text for token in required)
