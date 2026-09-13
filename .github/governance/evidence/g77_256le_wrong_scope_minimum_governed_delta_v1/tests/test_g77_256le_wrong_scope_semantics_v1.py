#!/usr/bin/env python3
"""Focused non-operational repository proof for G77-256LE WRONG_SCOPE."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import subprocess
import sys

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
LE = ROOT / (
    ".github/governance/evidence/"
    "g77_256le_wrong_scope_minimum_governed_delta_v1"
)
FORMALIZER = LE / "analysis/G77_256LE_WRONG_SCOPE_SEMANTIC_FORMALIZER_V1.py"
SELECTION = LE / "G77_256LE_HUMAN_FRONTIER_SELECTION_BINDING_V1.json"
REDUCTION = LE / "G77_256LE_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = LE / "G77_256LE_G48_IMPLEMENTATION_REPORT_V1.md"

sys.path.insert(0, str(ROOT / "tests"))
from aigol.runtime.canonical_human_authority_act_contract_v1 import (
    AUTHORIZATION,
    CANONICAL_HUMAN_AUTHORITY_ACT_CONTRACT_VERSION,
    HUMAN_AUTHORITY_OWNER,
    CanonicalHumanAuthorityActV1,
    canonical_human_authority_payload_digest_v1,
)
from aigol.runtime.models import FailClosedRuntimeError
from p11_da_disposable_substrate_v1 import P11CaptureReplayAdapter
from p11_da_operational_consumer_v1 import (
    OPERATIONAL_AUTHORITY_SCOPE,
    P11BoundedConsumerV1,
)


def load_formalizer():
    specification = importlib.util.spec_from_file_location(
        "g77_256le_wrong_scope_formalizer", FORMALIZER
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


F = load_formalizer()


def canonical_act(scope: str) -> CanonicalHumanAuthorityActV1:
    payload = {"bounded_repository_test": True}
    return CanonicalHumanAuthorityActV1(
        contract_version=CANONICAL_HUMAN_AUTHORITY_ACT_CONTRACT_VERSION,
        authority_act_identity="G77_256LE_SYNTHETIC_CANONICAL_ACT_001",
        authority_kind=AUTHORIZATION,
        interaction_identity="G77_256LE_SYNTHETIC_INTERACTION_001",
        conversation_identity="G77_256LE_SYNTHETIC_CONVERSATION_001",
        session_identity="G77_256LE_SYNTHETIC_SESSION_001",
        actor_identity="HUMAN_CONSTITUTIONAL_AUTHORITY",
        request_identity="G77_256LE_SYNTHETIC_REQUEST_001",
        continuation_identity="G77_256LE_SYNTHETIC_CONTINUATION_001",
        target_identity="G77_256LE_SYNTHETIC_TARGET_001",
        target_revision=0,
        producing_owner=HUMAN_AUTHORITY_OWNER,
        expected_owner="WRONG_EXPECTED_OWNER_AFTER_SCOPE_BRANCH",
        authority_scope=scope,
        payload=payload,
        payload_digest=canonical_human_authority_payload_digest_v1(payload),
        metadata={"repository_only": True, "operational_authority": False},
    )


def isolated_validate(act, monkeypatch: pytest.MonkeyPatch) -> None:
    correlation = object()
    monkeypatch.setattr(
        P11CaptureReplayAdapter,
        "validate_existing_authority_sources",
        staticmethod(lambda supplied_act, supplied_correlation: (
            supplied_act, supplied_correlation
        )),
    )
    consumer = object.__new__(P11BoundedConsumerV1)
    consumer._validate_authority_sources(
        act, correlation, {}, owner_revision=0, now_unix_ns=500
    )


def test_interrupted_selection_is_canonical_inner_sealed_and_nonoperational() -> None:
    raw = SELECTION.read_bytes()
    envelope = F.load_json(SELECTION)
    assert raw == F.canonical_bytes(envelope)
    assert envelope["selection_sha256"] == hashlib.sha256(
        F.canonical_bytes(envelope["selection"])
    ).hexdigest()
    selection = envelope["selection"]
    assert selection["selection_class"] == "HUMAN_FRONTIER_DEVELOPMENT_SELECTION"
    assert selection["selected_e05_vector"].endswith("/WRONG_SCOPE")
    assert selection["operational_authority_granted"] == "NO"
    assert selection["operation_granted"] == "NO"
    assert selection["authority_consumption_granted"] == "NO"


def test_formal_model_changes_only_scope_and_preserves_other_dimensions() -> None:
    model = F.formalize_wrong_scope()
    assert model["independent_semantic_mutation_count"] == 1
    assert model["independent_semantic_mutation_set"] == [
        "authority_scope:P11_DA_ONE_BOUNDED_OPERATIONAL_ATTEMPT_V1->"
        "P11_DA_DIFFERENT_OPERATIONAL_SCOPE_V1"
    ]
    baseline = model["baseline"]
    presented = model["presented"]
    differing_inputs = {
        key for key in baseline if baseline[key] != presented[key]
    }
    assert differing_inputs == {"authority_scope", "scope_admissible"}
    assert model["repository_behavior_is_operational_acceptance"] is False


def test_canonical_contract_accepts_nonempty_scope_as_valid_act_data() -> None:
    act = canonical_act(F.PRESENTED_WRONG_SCOPE)
    assert act.authority_kind == AUTHORIZATION
    assert act.authority_scope == F.PRESENTED_WRONG_SCOPE
    assert act.to_dict()["authority_scope"] == F.PRESENTED_WRONG_SCOPE


def test_p11_wrong_scope_branch_fails_with_exact_reason(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(
        FailClosedRuntimeError, match="^operational Human act scope is invalid$"
    ):
        isolated_validate(canonical_act(F.PRESENTED_WRONG_SCOPE), monkeypatch)


def test_p11_exact_scope_passes_scope_branch_before_next_guard(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(
        FailClosedRuntimeError,
        match="^operational Human act expected owner is invalid$",
    ):
        isolated_validate(canonical_act(OPERATIONAL_AUTHORITY_SCOPE), monkeypatch)


def test_scope_checks_precede_owner_initialization_ledger_and_effect() -> None:
    source = inspect.getsource(P11BoundedConsumerV1)
    validate = source[
        source.index("    def _validate_authority_sources("):
        source.index("    def submit_human_act(")
    ]
    submit = source[
        source.index("    def submit_human_act("):
        source.index("    def terminate_human_act(")
    ]
    claim = source[source.index("    def claim_and_invoke_once("):]
    assert validate.index("authority_scope") < validate.index(
        "self._gate.owner_state_root_identity"
    )
    assert submit.index("self._validate_authority_sources(") < submit.index(
        "self._store.initialize_available(binding)"
    )
    ordered = (
        "self._validate_authority_sources(",
        '"P11_DA_OPERATIONAL_PRECLAIM"',
        "self._store.claim(",
        "self._build_one_output(",
        '"P11_DA_OPERATIONAL_INVOCATION"',
        "terminal_bind_and_permanently_exhaust(",
    )
    positions = tuple(claim.index(marker) for marker in ordered)
    assert positions == tuple(sorted(positions))


def test_existing_capability_categories_remain_separate() -> None:
    capability = F.authenticate_scope_owners(ROOT)
    assert capability["code_exists"] is True
    assert capability["static_semantics_verified"] is True
    assert capability["behavioral_repository_proof_present"] is True
    assert capability["materialized_preflight_present"] is False
    assert capability["operational_acceptance_present"] is False


def test_failure_class_and_cross_vector_edges_are_distinct() -> None:
    reduction = F.build_reduction(ROOT)
    novelty = reduction["failure_novelty_and_convergence_check"]
    assert novelty["failure_class"] == "PROOF_GAP"
    assert novelty["new_capability_required"] == "NO"
    matrix = reduction["cross_vector_reuse_assessment"]
    assert len(matrix) == 8
    assert len({row["semantic_edge"] for row in matrix}) == 8
    assert next(row for row in matrix if row["vector"] == "WRONG_SCOPE")[
        "current_e05_status"
    ] == "UNSATISFIED__REPOSITORY_PROOF_ONLY"
    assert all(row["vector_specific_proof_required"] for row in matrix)
    assert not any(row["requires_new_production_capability"] for row in matrix)


def test_ex_is_reused_without_reconstruction_or_credit_transfer() -> None:
    ex = F.authenticate_ex(ROOT)
    assert ex == {
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
        "fresh_wrong_scope_operational_evidence_transferred": False,
        "e05_credit_transferred": False,
    }


def test_reduction_is_canonical_inner_sealed_and_reproducible() -> None:
    raw = REDUCTION.read_bytes()
    envelope = F.load_json(REDUCTION)
    assert raw == F.canonical_bytes(envelope)
    assert envelope["reduction_sha256"] == hashlib.sha256(
        F.canonical_bytes(envelope["reduction"])
    ).hexdigest()
    assert envelope == F.envelope(F.build_reduction(ROOT))
    reduction = envelope["reduction"]
    assert reduction["terminal"] == F.TERMINAL
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["frontier"]["current"] == "VERIFIED__12_OF_18"
    assert reduction["architectural_delta_budget"]["production_mutation"] == 0
    assert reduction["architectural_delta_budget"]["p11_mutation"] == 0


def test_formalizer_has_no_operational_or_process_execution_path() -> None:
    tree = ast.parse(FORMALIZER.read_text())
    called_names = {
        node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, (ast.Attribute, ast.Name))
    }
    assert not ({
        "submit_human_act", "claim_and_invoke_once", "Popen", "run_once",
        "execv", "system",
    } & called_names)
    assert "qemu-system" not in FORMALIZER.read_text()


def test_g48_report_has_exactly_six_h1_headings_and_exact_terminal() -> None:
    report = REPORT.read_text()
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    assert report.rstrip().endswith(F.TERMINAL)
    assert "repository-only evidence is not operational proof" in report


def test_delta_is_exactly_bounded_to_le_namespace() -> None:
    status = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=ROOT, text=True,
    ).splitlines()
    assert status
    assert all(line[3:].startswith(f"{F.NAMESPACE}/") for line in status)
    assert subprocess.check_output(
        ["git", "diff", "--name-only", "HEAD", "--", "tests/p11_da_operational_consumer_v1.py"],
        cwd=ROOT, text=True,
    ).strip() == ""
