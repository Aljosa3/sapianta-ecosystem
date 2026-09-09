#!/usr/bin/env python3
"""Focused repository-only tests for G77-256JP."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import ast
import hashlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
JP_ROOT = ROOT / (
    ".github/governance/evidence/"
    "g77_256jp_post_jo_committed_live_binding_and_expired_operational_"
    "readiness_reauthentication_v1"
)
FORMALIZER = JP_ROOT / "analysis/G77_256JP_POST_JO_READINESS_FORMALIZER_V1.py"
REPORT = JP_ROOT / "G77_256JP_G48_IMPLEMENTATION_REPORT_V1.md"
REDUCTION = JP_ROOT / "G77_256JP_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
LAUNCHER_PATH = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
FM_OWNER_PATH = LAUNCHER_PATH.parent / "sapianta_fresh_operation_context_v1.py"
ER_PATH = ROOT / (
    ".github/governance/evidence/g77_256er_p11_operational_v1/harness/"
    "G77_256ER_P11_OPERATIONAL_HARNESS_V1.py"
)
P11_PATH = ROOT / "tests/p11_da_operational_consumer_v1.py"
JM_TEST_PATH = ROOT / (
    ".github/governance/evidence/"
    "g77_256jm_option_a_deterministic_preclaim_temporal_binding_implementation_v1/"
    "tests/test_g77_256jm_option_a_temporal_binding_v1.py"
)


def load(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


F = load(FORMALIZER, "g77_256jp_formalizer")
sys.path.insert(0, str(LAUNCHER_PATH.parent))
LAUNCHER = load(LAUNCHER_PATH, "g77_256jp_launcher")
P11 = load(P11_PATH, "g77_256jp_p11")
ER = load(ER_PATH, "g77_256jp_er")
JM = load(JM_TEST_PATH, "g77_256jp_jm_fixture")


def test_entry_and_nested_authority_are_exact() -> None:
    value = F.authenticate_entry()
    assert value["head"] == value["remote_tracking_head"] == F.ENTRY_HEAD
    assert value["tree"] == F.ENTRY_TREE
    assert value["subject"] == F.ENTRY_SUBJECT
    assert value["index_empty"] is True
    assert value["nested_authority"] == {
        "origin": F.NESTED_ORIGIN, "head": F.NESTED_HEAD,
        "tree": F.NESTED_TREE, "clean": True, "detached": True,
        "tag": F.NESTED_TAG,
    }


def test_all_requested_jo_objects_are_committed_blob_and_sha256_exact() -> None:
    identities = F.authenticate_committed_jo_identities()
    assert len(identities) == 12
    assert {item["path"] for item in identities} == {
        path.as_posix() for path in F.JO_COMMITTED_IDENTITIES
    }
    assert {item["worktree_equals_committed"] for item in identities} == {
        "VERIFIED__YES"
    }


def test_jo_terminal_facts_counters_and_frontier_reconstruct() -> None:
    value = F.reconstruct_jo()
    assert value["terminal"] == F.JO_TERMINAL
    assert value["architecture"]["production_mutation_count"] == "VERIFIED__8"
    assert value["architecture"]["p11_implementation_mutation_count"] == "VERIFIED__0"
    assert set(value["operational_counters"].values()) == {"VERIFIED__0"}
    assert value["e05"]["after"] == "VERIFIED__11_OF_18"
    assert value["e05"]["credit"] == "VERIFIED__0"


def test_minimum_jm_jn_lineage_reconstructs() -> None:
    value = F.reconstruct_minimum_lineage()
    assert value["jm_head"] == F.JM_HEAD
    assert value["jm_tree"] == F.JM_TREE
    assert value["jm_terminal"] == F.JM_TERMINAL
    assert value["jn_head"] == F.JN_HEAD
    assert value["jn_tree"] == F.JN_TREE
    assert value["jn_terminal"] == F.JN_TERMINAL


def test_committed_route_is_single_current_jm_and_exact_dependency_closed() -> None:
    value = F.verify_committed_route()
    assert value["production_route_count"] == "VERIFIED__1"
    assert value["parallel_runtime_route_count"] == "VERIFIED__0"
    assert value["compatibility_bypass_count"] == "VERIFIED__0"
    assert value["alternate_p11_path_count"] == "VERIFIED__0"
    assert value["current_jm_p11_sha256"] == F.JM_P11_SHA256
    assert value["historical_if_is_current_authority"] == "VERIFIED__NO__FAIL_CLOSED"
    assert value["exact_byte_dependency_closure"].startswith("VERIFIED__COMMITTED_JO")


def test_historical_and_wrong_repository_identity_fail_closed() -> None:
    historical_tree = F.git("rev-parse", f"{F.HISTORICAL_IF_HEAD}^{{tree}}")
    with pytest.raises(RuntimeError, match="current repository identity"):
        LAUNCHER.authenticate_current_committed_jm_route(
            ROOT, F.HISTORICAL_IF_HEAD, historical_tree
        )
    with pytest.raises(RuntimeError, match="current repository identity"):
        LAUNCHER.authenticate_current_committed_jm_route(ROOT, "0" * 40, "0" * 40)


def test_arbitrary_committed_p11_bytes_fail_closed(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    (repository / "tests").mkdir(parents=True)
    (repository / "tests/p11_da_operational_consumer_v1.py").write_text(
        "ARBITRARY_P11_BYTES = True\n", encoding="utf-8"
    )
    subprocess.check_call(["git", "init", "-q"], cwd=repository)
    subprocess.check_call(["git", "add", "tests/p11_da_operational_consumer_v1.py"], cwd=repository)
    subprocess.check_call(
        ["git", "-c", "user.name=JP Test", "-c", "user.email=jp@example.invalid",
         "commit", "-q", "-m", "arbitrary fixture"],
        cwd=repository,
    )
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repository, text=True).strip()
    tree = subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=repository, text=True).strip()
    with pytest.raises(RuntimeError, match="does not contain committed JM P11"):
        LAUNCHER.authenticate_current_committed_jm_route(repository, head, tree)


def test_authenticated_context_change_and_checkout_mismatch_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    head = F.ENTRY_HEAD
    tree = F.ENTRY_TREE

    def context_for(operation: str) -> dict:
        return LAUNCHER.build_operation_context(
            repository_root=ROOT, repository_head=head, repository_tree=tree,
            generation_identity=(
                "G77_256JPTEST_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_"
                "OPERATIONAL_COMMISSIONING_V1"
            ),
            operation_identity=operation, identity_namespace_prefix="G77_256JPTEST",
            operation_evidence_root=tmp_path / "operation_state",
            transient_root=tmp_path / "transient",
        )

    context_path = tmp_path / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    first = context_for("G77_256JPTEST_OPERATION_001")
    context_path.write_bytes(JM.FM.canonical_bytes(first))
    monkeypatch.setattr(ER, "FRESH_OPERATION_CONTEXT_PATH", context_path)
    monkeypatch.setattr(ER, "FRESH_OPERATION_CONTEXT_OWNER_PATH", FM_OWNER_PATH)
    monkeypatch.setattr(ER, "CHECKOUT", ROOT)
    monkeypatch.setattr(ER, "P11_CONSUMER_PATH", P11_PATH)
    monkeypatch.setattr(ER, "_AUTHENTICATED_FRESH_OPERATION_CONTEXT", None)
    assert ER.load_authenticated_fresh_operation_context() == first
    second = context_for("G77_256JPTEST_OPERATION_002")
    context_path.write_bytes(JM.FM.canonical_bytes(second))
    with pytest.raises(RuntimeError, match="changed after authentication"):
        ER.load_authenticated_fresh_operation_context()

    wrong_checkout = deepcopy(first)
    wrong_checkout["repository_tree"] = "0" * 40
    unsealed = {
        key: value for key, value in wrong_checkout.items() if key != "context_sha256"
    }
    wrong_checkout["context_sha256"] = JM.FM.sha256_bytes(
        JM.FM.canonical_bytes(unsealed)
    )
    context_path.write_bytes(JM.FM.canonical_bytes(wrong_checkout))
    monkeypatch.setattr(ER, "_AUTHENTICATED_FRESH_OPERATION_CONTEXT", None)
    with pytest.raises(Exception, match="context|checkout|repository"):
        ER.load_authenticated_fresh_operation_context()


def test_gate_and_consumer_reject_wrong_context_correlations(tmp_path: Path) -> None:
    context = JM.context_for(tmp_path)
    store = JM.store_for(tmp_path)
    bindings = JM.FixedPrincipalBindings(os.getuid() + 1, os.getuid() + 2, os.getuid())
    gate = JM.gate_for(context, store, bindings)
    JM.P11BoundedConsumerV1(
        store=store, principal_bindings=bindings, commissioning_gate=gate,
        fresh_operation_context=context,
    )
    changed = deepcopy(context)
    changed["preclaim_temporal_binding"]["coordinate_unix_ns"] = 999
    with pytest.raises(Exception, match="context|temporal"):
        JM.P11BoundedConsumerV1(
            store=store, principal_bindings=bindings, commissioning_gate=gate,
            fresh_operation_context=changed,
        )
    for changes in (
        {"operation_context_sha256": "0" * 64},
        {"preclaim_temporal_binding_identity": "0" * 64},
    ):
        with pytest.raises(Exception, match="context|temporal|gate"):
            replace(gate, **changes)


def test_required_context_handoff_fields_cannot_be_omitted(tmp_path: Path) -> None:
    context = JM.context_for(tmp_path)
    store = JM.store_for(tmp_path)
    bindings = JM.FixedPrincipalBindings(os.getuid() + 1, os.getuid() + 2, os.getuid())
    gate = JM.gate_for(context, store, bindings)
    for field in ("operation_context_sha256", "preclaim_temporal_binding_identity"):
        facts = gate.identity_preimage()
        facts.pop("schema_id")
        facts.pop(field)
        with pytest.raises(KeyError):
            P11.create_commissioning_gate_v1(**facts)
    with pytest.raises(TypeError, match="fresh_operation_context"):
        P11.P11BoundedConsumerV1(
            store=store, principal_bindings=bindings, commissioning_gate=gate
        )


def test_temporal_boundaries_and_no_governed_wall_clock_fallback(tmp_path: Path) -> None:
    binding, _ = JM.authenticate_preclaim_temporal_binding(JM.context_for(tmp_path))
    decisions = [
        P11.preclaim_temporal_decision(
            dict(binding, coordinate_unix_ns=value),
            valid_from_unix_ns=100, valid_until_unix_ns=1000,
        )
        for value in (999, 1000, 1001)
    ]
    assert decisions == ["CURRENT", "EXPIRED", "EXPIRED"]
    claim = inspect.getsource(P11.P11BoundedConsumerV1.claim_and_invoke_once)
    assert "time.time_ns()" not in claim
    assert 'preclaim_time = temporal_binding["coordinate_unix_ns"]' in claim
    assert F.verify_temporal_contract()["governed_wall_clock_fallback"] == "VERIFIED__ABSENT"


def test_temporal_coordinate_is_not_caller_provider_or_human_selectable() -> None:
    materializer = inspect.signature(JM.FM.materialize_preclaim_temporal_binding)
    assert set(materializer.parameters) == {
        "repository_root", "generation_identity", "operation_identity"
    }
    source = inspect.getsource(JM.FM.materialize_preclaim_temporal_binding).lower()
    assert "caller" not in source and "provider" not in source and "human" not in source


def test_ex_successor_delta_is_exactly_er_and_reuses_17_of_17() -> None:
    value = F.verify_ex_successor_delta()
    assert value["ex_reused"] == "VERIFIED__17_OF_17"
    assert value["ex_reconstructed"] == "VERIFIED__0"
    assert value["changed_ex_bound_component_count"] == "VERIFIED__1"
    assert value["changed_component"] == "ER_OPERATIONAL_HARNESS"
    assert value["additional_ex_bound_component_change_count"] == "VERIFIED__0"


def test_g48_has_exactly_six_h1_reuse_questions_and_compact_ccwim() -> None:
    report = REPORT.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    for required in (
        "## Reuse Impact Assessment",
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
        "## Compact CCWIM", "AUTO_CONTINUABLE = NO", "HUMAN_REVIEW_REQUIRED = YES",
    ):
        assert required in report
    assert report.rstrip().endswith(F.TERMINAL)


def test_terminal_reduction_is_canonical_sealed_and_exact() -> None:
    envelope = json.loads(REDUCTION.read_bytes())
    reduction = envelope["reduction"]
    assert REDUCTION.read_bytes() == F.canonical_bytes(envelope)
    assert envelope["reduction_sha256"] == hashlib.sha256(
        F.canonical_bytes(reduction)
    ).hexdigest()
    assert reduction == F.build_reduction()
    assert reduction["terminal"] == F.TERMINAL
    assert set(reduction["operational_counters"].values()) == {"VERIFIED__0"}
    assert reduction["auto_continuable"] is False
    assert reduction["human_review_required"] is True


def test_formalizer_is_static_and_mutation_scope_is_evidence_only() -> None:
    tree = ast.parse(FORMALIZER.read_text(encoding="utf-8"))
    imports = {
        alias.name for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom)) for alias in node.names
    }
    assert "time" not in imports and "datetime" not in imports
    calls = {
        ast.unparse(node.func) for node in ast.walk(tree) if isinstance(node, ast.Call)
    }
    assert not {"subprocess.run", "subprocess.Popen", "os.system"} & calls
    status = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT, text=True,
    ).splitlines()
    assert all(line.startswith("?? ") and line[3:].startswith(f"{F.JP}/") for line in status)
    assert subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True
    ) == ""
