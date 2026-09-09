#!/usr/bin/env python3
"""Repository-only G77-256JO sole-route binding tests."""

from __future__ import annotations

from copy import deepcopy
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
JO = ROOT / (
    ".github/governance/evidence/"
    "g77_256jo_bind_sole_er_fm_route_to_committed_jm_p11_and_sealed_context_v1"
)
FORMALIZER = JO / "analysis/G77_256JO_SOLE_ROUTE_BINDING_FORMALIZER_V1.py"
REPORT = JO / "G77_256JO_G48_IMPLEMENTATION_REPORT_V1.md"
REDUCTION = JO / "G77_256JO_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
LAUNCHER_PATH = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
P11_PATH = ROOT / "tests/p11_da_operational_consumer_v1.py"
ER_PATH = ROOT / (
    ".github/governance/evidence/g77_256er_p11_operational_v1/harness/"
    "G77_256ER_P11_OPERATIONAL_HARNESS_V1.py"
)
FM_OWNER_PATH = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "sapianta_fresh_operation_context_v1.py"
)
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


F = load(FORMALIZER, "g77_256jo_formalizer")
LAUNCHER = load(LAUNCHER_PATH, "g77_256jo_launcher")
P11 = load(P11_PATH, "g77_256jo_p11")
ER = load(ER_PATH, "g77_256jo_er")
JM = load(JM_TEST_PATH, "g77_256jo_jm_fixture")


def test_authenticated_jn_entry_scope_and_nested_authority() -> None:
    result = F.authenticate_entry()
    assert result["branch"] == F.BRANCH
    assert result["head"] == result["remote_tracking_head"] == F.ENTRY_HEAD
    assert result["tree"] == F.ENTRY_TREE
    assert result["subject"] == F.ENTRY_SUBJECT
    assert result["origin"] == F.ORIGIN
    assert result["index_empty"] is True
    assert result["entry_clean_before_first_write"] == "VERIFIED__YES"
    assert result["nested_origin"] == F.NESTED_ORIGIN
    assert result["nested_head"] == F.NESTED_HEAD
    assert result["nested_tree"] == F.NESTED_TREE
    assert result["nested_detached"] is result["nested_clean"] is True
    assert result["nested_tag"] == F.NESTED_TAG


def test_jn_and_jm_reconstruct_with_ex_17_of_17_reused() -> None:
    result = F.reconstruct_lineage()
    assert result["jn_terminal"] == F.JN_TERMINAL
    assert result["jm_terminal"] == F.JM_TERMINAL
    assert result["jm_head"] == F.JM_HEAD
    assert result["jm_tree"] == F.JM_TREE
    assert result["ex_reused"] == "VERIFIED__17_OF_17"
    assert result["ex_reconstructed"] == "VERIFIED__0"
    assert result["e05_before"] == "VERIFIED__11_OF_18"
    assert result["e05_credit"] == "VERIFIED__0"


def test_sole_route_uses_current_repository_and_exact_jm_p11() -> None:
    result = F.verify_route()
    assert result["sole_route"] == "VERIFIED__ONE_LAUNCHER_ONE_QEMU_CALL_SITE"
    assert result["runtime_target_source"] == "VERIFIED__SEALED_CURRENT_REPOSITORY_HEAD_TREE"
    assert result["runtime_target_p11_sha256"] == F.JM_P11_SHA256
    assert result["historical_if_satisfies_current_route"] == "VERIFIED__NO__FAIL_CLOSED"
    head = F.git("rev-parse", "HEAD")
    tree = F.git("rev-parse", "HEAD^{tree}")
    LAUNCHER.authenticate_current_committed_jm_route(ROOT, head, tree)


@pytest.mark.parametrize(
    ("head", "tree"),
    [
        (F.HISTORICAL_IF_HEAD, "7c773d4b2acdf013f1b8238eabfc8eced4dd6866"),
        ("0" * 40, "0" * 40),
    ],
)
def test_stale_or_arbitrary_runtime_target_fails_closed(head: str, tree: str) -> None:
    with pytest.raises(RuntimeError, match="current repository identity"):
        LAUNCHER.authenticate_current_committed_jm_route(ROOT, head, tree)


def test_sealed_context_reaches_both_existing_construction_sites() -> None:
    result = F.verify_route()
    assert result["base_er_context_handoff"] == "VERIFIED__GATE_AND_CONSUMER"
    assert result["fc_specialized_context_handoff"] == "VERIFIED__GATE_AND_CONSUMER"
    assert result["context_source"].startswith("VERIFIED__EXISTING_PROJECTED_FM_OWNER")
    assert result["post_seal_substitution"].startswith("VERIFIED__FAIL_CLOSED")


def test_er_authenticates_exact_sealed_context_and_rejects_substitution(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    head = F.git("rev-parse", "HEAD")
    tree = F.git("rev-parse", "HEAD^{tree}")

    def context_for(operation: str) -> dict:
        return LAUNCHER.build_operation_context(
            repository_root=ROOT,
            repository_head=head,
            repository_tree=tree,
            generation_identity=(
                "G77_256JOTEST_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_"
                "OPERATIONAL_COMMISSIONING_V1"
            ),
            operation_identity=operation,
            identity_namespace_prefix="G77_256JOTEST",
            operation_evidence_root=tmp_path / "operation_state",
            transient_root=tmp_path / "transient",
        )

    context_path = tmp_path / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    first = context_for("G77_256JOTEST_OPERATION_001")
    LAUNCHER.validate_immutable_context_bindings(ROOT, first)
    context_path.write_bytes(JM.FM.canonical_bytes(first))
    monkeypatch.setattr(ER, "FRESH_OPERATION_CONTEXT_PATH", context_path)
    monkeypatch.setattr(ER, "FRESH_OPERATION_CONTEXT_OWNER_PATH", FM_OWNER_PATH)
    monkeypatch.setattr(ER, "CHECKOUT", ROOT)
    monkeypatch.setattr(ER, "P11_CONSUMER_PATH", P11_PATH)
    monkeypatch.setattr(ER, "_AUTHENTICATED_FRESH_OPERATION_CONTEXT", None)
    assert ER.load_authenticated_fresh_operation_context() == first

    second = context_for("G77_256JOTEST_OPERATION_002")
    context_path.write_bytes(JM.FM.canonical_bytes(second))
    with pytest.raises(RuntimeError, match="changed after authentication"):
        ER.load_authenticated_fresh_operation_context()


def test_context_gate_and_consumer_reject_mutation_and_mismatch(tmp_path: Path) -> None:
    context = JM.context_for(tmp_path)
    store = JM.store_for(tmp_path)
    bindings = JM.FixedPrincipalBindings(os.getuid() + 1, os.getuid() + 2, os.getuid())
    gate = JM.gate_for(context, store, bindings)
    JM.P11BoundedConsumerV1(
        store=store,
        principal_bindings=bindings,
        commissioning_gate=gate,
        fresh_operation_context=context,
    )
    changed = deepcopy(context)
    changed["preclaim_temporal_binding"]["coordinate_unix_ns"] = 999
    with pytest.raises(Exception, match="context|temporal"):
        JM.P11BoundedConsumerV1(
            store=store,
            principal_bindings=bindings,
            commissioning_gate=gate,
            fresh_operation_context=changed,
        )


@pytest.mark.parametrize(
    "field",
    [
        "operation_context_sha256",
        "preclaim_temporal_binding_identity",
    ],
)
def test_missing_gate_handoff_fails_closed(tmp_path: Path, field: str) -> None:
    context = JM.context_for(tmp_path)
    store = JM.store_for(tmp_path)
    bindings = JM.FixedPrincipalBindings(os.getuid() + 1, os.getuid() + 2, os.getuid())
    gate = JM.gate_for(context, store, bindings)
    facts = gate.identity_preimage()
    facts.pop("schema_id")
    facts.pop(field)
    with pytest.raises(KeyError):
        P11.create_commissioning_gate_v1(**facts)


def test_missing_fresh_context_consumer_handoff_fails_closed(tmp_path: Path) -> None:
    context = JM.context_for(tmp_path)
    store = JM.store_for(tmp_path)
    bindings = JM.FixedPrincipalBindings(os.getuid() + 1, os.getuid() + 2, os.getuid())
    gate = JM.gate_for(context, store, bindings)
    with pytest.raises(TypeError, match="fresh_operation_context"):
        P11.P11BoundedConsumerV1(
            store=store,
            principal_bindings=bindings,
            commissioning_gate=gate,
        )


def test_temporal_boundary_and_no_preclaim_wall_clock_fallback(tmp_path: Path) -> None:
    binding, _ = JM.authenticate_preclaim_temporal_binding(JM.context_for(tmp_path))
    decisions = [
        P11.preclaim_temporal_decision(
            dict(binding, coordinate_unix_ns=value),
            valid_from_unix_ns=100,
            valid_until_unix_ns=1000,
        )
        for value in (999, 1000, 1001)
    ]
    assert decisions == ["CURRENT", "EXPIRED", "EXPIRED"]
    claim = inspect.getsource(P11.P11BoundedConsumerV1.claim_and_invoke_once)
    assert "time.time_ns()" not in claim
    assert 'preclaim_time = temporal_binding["coordinate_unix_ns"]' in claim


def test_time_authority_is_not_selectable() -> None:
    materializer = inspect.signature(JM.FM.materialize_preclaim_temporal_binding)
    assert set(materializer.parameters) == {
        "repository_root", "generation_identity", "operation_identity"
    }
    source = inspect.getsource(JM.FM.materialize_preclaim_temporal_binding)
    assert "caller" not in source.lower()
    assert "provider" not in source.lower()
    assert "human" not in source.lower()


def test_er_is_only_additional_ex_bound_delta_and_ex_is_reused() -> None:
    result = F.verify_ex_delta()
    assert result["ex_reused"] == "VERIFIED__17_OF_17"
    assert result["ex_reconstructed"] == "VERIFIED__0"
    assert result["changed_ex_bound_component_count"] == "VERIFIED__1"
    assert result["changed_component"] == "ER_OPERATIONAL_HARNESS"
    assert result["classification"] == "REQUIRES_HARDENING"
    assert result["new_certificate_count"] == "VERIFIED__0"


def test_g48_six_h1_reuse_impact_and_compact_ccwim() -> None:
    report = REPORT.read_text(encoding="utf-8")
    headings = [line for line in report.splitlines() if line.startswith("# ")]
    assert headings == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    for text in (
        "## Reuse Impact Assessment",
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
        "## Constitutional Continuity & Worker Independence Metrics — CCWIM",
    ):
        assert text in report


def test_terminal_reduction_is_canonical_sealed_and_zero_operation() -> None:
    envelope = json.loads(REDUCTION.read_bytes())
    reduction = envelope["reduction"]
    assert REDUCTION.read_bytes() == F.canonical_bytes(envelope)
    assert envelope["reduction_sha256"] == hashlib.sha256(
        F.canonical_bytes(reduction)
    ).hexdigest()
    assert reduction == F.build_reduction()
    assert reduction["terminal"] == F.TERMINAL
    assert set(reduction["operational_counters"].values()) == {"VERIFIED__0"}
    assert reduction["e05"] == {
        "before": "VERIFIED__11_OF_18",
        "after": "VERIFIED__11_OF_18",
        "credit": "VERIFIED__0",
        "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
        "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
    }
    assert reduction["auto_continuable"] is False
    assert reduction["human_review_required"] is True


def test_no_layer_zero_nested_or_p11_mutation_and_index_empty() -> None:
    changed = set(F.git("diff", "--name-only").splitlines())
    assert "tests/p11_da_operational_consumer_v1.py" not in changed
    assert not any(path.startswith("sapianta_system/") for path in changed)
    assert not any(path.startswith("docs/governance/CONSTITUTIONAL_") for path in changed)
    assert F.git("diff", "--cached", "--name-only") == ""
