#!/usr/bin/env python3
"""Focused repository-only LA reference and static-readiness proof."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import re
import subprocess
import sys

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
LA = ROOT / (
    ".github/governance/evidence/"
    "g77_256la_expired_input_authorization_reference_alignment_v1"
)
JR_PATH = ROOT / (
    ".github/governance/evidence/"
    "g77_256jr_expired_human_authority_materialization_and_presentation_binding_v1/"
    "adapter/G77_256JR_EXPIRED_VECTOR_ADAPTER_V1.py"
)
ER_PATH = ROOT / (
    ".github/governance/evidence/g77_256er_p11_operational_v1/harness/"
    "G77_256ER_P11_OPERATIONAL_HARNESS_V1.py"
)
JM_TESTS = ROOT / (
    ".github/governance/evidence/"
    "g77_256jm_option_a_deterministic_preclaim_temporal_binding_implementation_v1/"
    "tests/test_g77_256jm_option_a_temporal_binding_v1.py"
)
FORMALIZER = LA / "analysis/G77_256LA_INPUT_AUTHORIZATION_REFERENCE_FORMALIZER_V1.py"
REDUCTION = LA / "G77_256LA_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = LA / "G77_256LA_G48_IMPLEMENTATION_REPORT_V1.md"

sys.path.insert(0, str(ROOT / "tests"))
from aigol.runtime.models import FailClosedRuntimeError
from p11_da_custody_process_v1 import FixedPrincipalBindings
from p11_da_disposable_substrate_v1 import (
    bind_record_identity,
    validate_input_record_bytes,
)
from p11_da_operational_consumer_v1 import P11BoundedConsumerV1


def load(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


F = load(FORMALIZER, "g77_256la_formalizer")
JR = load(JR_PATH, "g77_256la_jr_adapter")
JM = load(JM_TESTS, "g77_256la_jm_precedent")


def construct(tmp_path: Path):
    prefix = "G77_256LATEST"
    context = JM.LAUNCHER.build_operation_context(
        repository_root=ROOT,
        repository_head=F.ENTRY_HEAD,
        repository_tree=F.ENTRY_TREE,
        generation_identity=(
            prefix
            + "_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
        ),
        operation_identity=prefix + "_EXPIRED_OPERATION_001",
        identity_namespace_prefix=prefix,
        operation_evidence_root=tmp_path / "operation_state",
        transient_root=tmp_path / "transient",
    )
    store = JM.store_for(tmp_path)
    bindings = FixedPrincipalBindings(
        os.getuid() + 1, os.getuid() + 2, os.getuid()
    )
    gate = JM.gate_for(context, store, bindings)
    source = JR.specialize_fc_runtime_source(
        repository_root=ROOT,
        identity_namespace_prefix=prefix,
    )
    namespace = {
        "__name__": "g77_256la_expired_specialization",
        "__file__": str(F.FC),
        "__package__": None,
        "SUBMISSION_TIME_UNIX_NS": JR.SUBMISSION_TIME_UNIX_NS,
    }
    exec(compile(source, namespace["__file__"], "exec"), namespace)
    er = JR.specialize_er_harness(ROOT)
    er.CHECKOUT = ROOT
    input_bytes, input_record, act, correlation = namespace[
        "create_fc_input_and_authority"
    ](er, gate, bindings, store)
    consumer = P11BoundedConsumerV1(
        store=store,
        principal_bindings=bindings,
        commissioning_gate=gate,
        fresh_operation_context=context,
    )
    return (
        context, gate, consumer, input_bytes, input_record, act, correlation,
        source,
    )


def test_reference_target_is_derived_act_and_exact_guard_passes(tmp_path: Path) -> None:
    context, gate, consumer, _, record, act, correlation, _ = construct(tmp_path)
    assert record["authorization_reference"] == act.authority_act_identity
    assert record["authorization_reference"] != (
        "G77_256ER_EXACT_CURRENT_ONE_USE_HUMAN_OPERATIONAL_ACT_001"
    )
    binding = consumer._validate_authority_sources(
        act, correlation, record, owner_revision=0, now_unix_ns=500
    )
    assert binding.authority_act_identity == act.authority_act_identity
    assert act.metadata["authorized_context_sha256"] == (
        gate.operation_context_sha256
    ) == context["context_sha256"]
    assert act.metadata["non_reusable"] is True
    assert act.metadata["non_transferable"] is True
    assert act.metadata["selected_vector"].endswith("/EXPIRED")


@pytest.mark.parametrize(
    ("case", "reference"),
    [
        ("wrong", "WRONG_ACT_IDENTITY"),
        ("different_act", "G77_256OTHER_ACT_001"),
        ("stale_er", "G77_256ER_EXACT_CURRENT_ONE_USE_HUMAN_OPERATIONAL_ACT_001"),
    ],
)
def test_wrong_different_and_stale_reference_fail_exact_guard(
    tmp_path: Path, case: str, reference: str
) -> None:
    _, _, consumer, _, record, act, correlation, _ = construct(tmp_path)
    changed = dict(record)
    changed["authorization_reference"] = reference
    with pytest.raises(
        FailClosedRuntimeError, match="P11 input authorization reference is invalid"
    ):
        consumer._validate_authority_sources(
            act, correlation, changed, owner_revision=0, now_unix_ns=500
        )


@pytest.mark.parametrize(("case", "value"), [("missing", None), ("malformed", "")])
def test_missing_and_schema_malformed_reference_fail_closed(
    tmp_path: Path, case: str, value: str | None
) -> None:
    _, _, _, _, record, _, _, _ = construct(tmp_path)
    changed = dict(record)
    changed["record_identity"] = ""
    if case == "missing":
        changed.pop("authorization_reference")
        message = "field set"
    else:
        changed["authorization_reference"] = value
        message = "non-empty string"
    with pytest.raises(FailClosedRuntimeError, match=message):
        validate_input_record_bytes(bind_record_identity(changed))


def test_specialization_has_one_owner_value_and_no_alternate_reference(
    tmp_path: Path,
) -> None:
    *_, source = construct(tmp_path)
    assert source.count('"authorization_reference": ACT_ID') == 1
    tree = ast.parse(source)
    values = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if isinstance(key, ast.Constant) and key.value == "authorization_reference":
                    values.append(value)
    assert len(values) == 1
    assert isinstance(values[0], ast.Name) and values[0].id == "ACT_ID"


def test_static_chain_reaches_temporal_boundary_without_operation(tmp_path: Path) -> None:
    _, _, consumer, _, record, act, correlation, _ = construct(tmp_path)
    consumer._validate_authority_sources(
        act, correlation, record, owner_revision=0, now_unix_ns=500
    )
    submit = inspect.getsource(P11BoundedConsumerV1.submit_human_act)
    claim = inspect.getsource(P11BoundedConsumerV1.claim_and_invoke_once)
    assert "now_unix_ns" in submit
    assert "preclaim_temporal_decision" in claim
    assert 'temporal_decision == "EXPIRED"' in claim
    assert "one-use Human act expired before PRECLAIM" in claim
    assert claim.index('temporal_decision == "EXPIRED"') < claim.index(
        "_append_operational_event"
    )


def test_kz_context_binding_and_shared_owners_remain_unchanged() -> None:
    trace = F.authenticate_trace()
    assert trace["expected_reference_target"] == "DERIVED_ACT.AUTHORITY_ACT_IDENTITY"
    assert trace["alternate_reference_count"] == 0
    assert F.sha256(F.FC) == F.FC_SHA256
    assert F.sha256(F.P11) == F.P11_SHA256
    assert subprocess.check_output(
        ["git", "diff", "--name-only", "HEAD", "--", F.FC.relative_to(ROOT)],
        cwd=ROOT,
        text=True,
    ).strip() == ""
    assert subprocess.check_output(
        ["git", "diff", "--name-only", "HEAD", "--", F.P11.relative_to(ROOT)],
        cwd=ROOT,
        text=True,
    ).strip() == ""


def test_terminal_reduction_is_canonical_sealed_zero_operation_and_ready() -> None:
    raw = REDUCTION.read_bytes()
    envelope = json.loads(raw)
    assert raw == F.canonical_bytes(envelope)
    reduction = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(
        F.canonical_bytes(reduction)
    ).hexdigest()
    assert reduction == F.build_reduction()
    assert reduction["terminal"] == F.TERMINAL
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["static_readiness"] == {
        "static_pre_operational_chain_complete": "VERIFIED",
        "fresh_operational_attempt_readiness": "READY__REPOSITORY_ONLY",
        "readiness_blocker": "NONE_KNOWN_AT_STATIC_TEMPORAL_BOUNDARY",
        "next_static_edge": "NONE_KNOWN",
        "readiness_is_operational_proof": False,
    }
    assert reduction["e05"]["current_generation_credit"] == "VERIFIED__0"


def test_g48_structure_and_proof_separation() -> None:
    report = REPORT.read_text()
    assert re.findall(r"^# .+$", report, re.MULTILINE) == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    assert len(re.findall(r"^\d\. (?:Katere|Ali).+\?$", report, re.MULTILINE)) == 5
    assert "OPERATIONAL PROOF = NOT_PERFORMED" in report
    assert "E05 ACCEPTANCE PROOF = NOT_CREATED" in report
    assert report.rstrip().endswith(F.TERMINAL)


def test_exact_bounded_production_diff() -> None:
    assert set(
        subprocess.check_output(
            ["git", "diff", "--name-only"], cwd=ROOT, text=True
        ).splitlines()
    ) == {F.JR.relative_to(ROOT).as_posix(), F.FM.relative_to(ROOT).as_posix()}
    reduction = F.build_reduction()
    assert reduction["architecture"]["production_mutation"] == 2
    assert reduction["architecture"]["p11_mutation"] == 0
    assert reduction["architecture"]["production_route"] == "1_TO_1"
