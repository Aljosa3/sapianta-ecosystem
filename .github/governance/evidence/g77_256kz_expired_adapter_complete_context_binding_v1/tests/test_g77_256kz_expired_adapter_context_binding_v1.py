#!/usr/bin/env python3
"""Focused repository-only proof for the KZ EXPIRED adapter repair."""

from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KZ = ROOT / (
    ".github/governance/evidence/"
    "g77_256kz_expired_adapter_complete_context_binding_v1"
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
FORMALIZER = KZ / "analysis/G77_256KZ_EXPIRED_ADAPTER_CONTEXT_BINDING_FORMALIZER_V1.py"
REDUCTION = KZ / "G77_256KZ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = KZ / "G77_256KZ_G48_IMPLEMENTATION_REPORT_V1.md"

sys.path.insert(0, str(ROOT / "tests"))
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash
from p11_da_custody_process_v1 import FixedPrincipalBindings
from p11_da_operational_consumer_v1 import P11BoundedConsumerV1


def load(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


F = load(FORMALIZER, "g77_256kz_formalizer")
JR = load(JR_PATH, "g77_256kz_jr_adapter")
ER = load(ER_PATH, "g77_256kz_er_harness")
JM = load(JM_TESTS, "g77_256kz_jm_precedent")


def expired_context(root: Path) -> dict:
    prefix = "G77_256KZTEST"
    return JM.LAUNCHER.build_operation_context(
        repository_root=ROOT,
        repository_head=F.ENTRY_HEAD,
        repository_tree=F.ENTRY_TREE,
        generation_identity=(
            prefix
            + "_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
        ),
        operation_identity=prefix + "_EXPIRED_OPERATION_001",
        identity_namespace_prefix=prefix,
        operation_evidence_root=root / "operation_state",
        transient_root=root / "transient",
    )


def constructed_path(tmp_path: Path):
    context = expired_context(tmp_path)
    store = JM.store_for(tmp_path)
    bindings = FixedPrincipalBindings(
        os.getuid() + 1, os.getuid() + 2, os.getuid()
    )
    gate = JM.gate_for(context, store, bindings)
    source = JR.specialize_fc_runtime_source(
        repository_root=ROOT,
        identity_namespace_prefix="G77_256KZTEST",
    )
    namespace = {
        "__name__": "g77_256kz_expired_specialization",
        "__file__": str(F.FC_ADAPTER),
        "__package__": None,
        "SUBMISSION_TIME_UNIX_NS": JR.SUBMISSION_TIME_UNIX_NS,
    }
    exec(compile(source, namespace["__file__"], "exec"), namespace)
    er = JR.specialize_er_harness(ROOT)
    er.CHECKOUT = ROOT
    input_bytes, input_record, act, correlation = namespace[
        "create_fc_input_and_authority"
    ](er, gate, bindings, store)
    del input_bytes
    consumer = P11BoundedConsumerV1(
        store=store,
        principal_bindings=bindings,
        commissioning_gate=gate,
        fresh_operation_context=context,
    )
    return context, gate, consumer, input_record, act, correlation, namespace, source


def rebound_act_and_correlation(namespace, act, correlation, metadata: dict):
    from aigol.runtime.canonical_human_authority_act_contract_v1 import (
        CanonicalHumanAuthorityActV1,
    )

    value = act.to_dict()
    value["metadata"] = metadata
    changed_act = CanonicalHumanAuthorityActV1.from_dict(value)
    changed_correlation = namespace["rebind_canonical_correlation"](
        correlation,
        {"source_act_digest": replay_hash(changed_act.to_dict())},
    )
    return changed_act, changed_correlation


def test_authenticated_source_to_gate_to_act_trace_is_exact(tmp_path: Path) -> None:
    context, gate, consumer, input_record, act, correlation, _, _ = constructed_path(
        tmp_path
    )
    expected = context["context_sha256"]
    assert gate.operation_context_sha256 == expected
    assert act.metadata["authorized_context_sha256"] == expected
    assert act.metadata["authorized_context_sha256"] == gate.operation_context_sha256
    assert act.metadata["non_reusable"] is True
    assert act.metadata["non_transferable"] is True
    assert act.metadata["selected_vector"].endswith("/EXPIRED")
    with pytest.raises(
        FailClosedRuntimeError, match="P11 input authorization reference is invalid"
    ) as later_failure:
        consumer._validate_authority_sources(
            act,
            correlation,
            input_record,
            owner_revision=0,
            now_unix_ns=500,
        )
    assert "complete sealed context" not in str(later_failure.value)


@pytest.mark.parametrize(
    ("case", "replacement"),
    [
        ("missing", None),
        ("wrong", "0" * 64),
        ("different_context", "1" * 64),
        ("stale_context", "2" * 64),
        ("malformed", "not-a-sha256-digest"),
    ],
)
def test_missing_wrong_different_stale_and_malformed_fail_closed(
    tmp_path: Path, case: str, replacement: str | None
) -> None:
    _, _, consumer, input_record, act, correlation, namespace, _ = constructed_path(
        tmp_path
    )
    metadata = dict(act.metadata)
    if case == "missing":
        metadata.pop("authorized_context_sha256")
    else:
        metadata["authorized_context_sha256"] = replacement
    changed_act, changed_correlation = rebound_act_and_correlation(
        namespace, act, correlation, metadata
    )
    with pytest.raises(
        FailClosedRuntimeError,
        match="Human authorization does not bind the complete sealed context",
    ):
        consumer._validate_authority_sources(
            changed_act,
            changed_correlation,
            input_record,
            owner_revision=0,
            now_unix_ns=500,
        )


def test_specialization_uses_exact_gate_value_without_substitute_digest(
    tmp_path: Path,
) -> None:
    _, _, _, _, _, _, _, source = constructed_path(tmp_path)
    assert source.count(
        '"authorized_context_sha256": gate.operation_context_sha256'
    ) == 1
    tree = ast.parse(source)
    matches = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        for key, value in zip(node.keys, node.values):
            if isinstance(key, ast.Constant) and key.value == "authorized_context_sha256":
                matches.append(value)
    assert len(matches) == 1
    value = matches[0]
    assert isinstance(value, ast.Attribute)
    assert value.attr == "operation_context_sha256"
    assert isinstance(value.value, ast.Name) and value.value.id == "gate"


def test_fc_p11_and_nonexpired_vector_owners_are_unchanged() -> None:
    trace = F.authenticate_trace()
    assert trace["minimum_repair_owner"] == (
        "EXISTING_JR_EXPIRED_SPECIALIZATION_AND_EXISTING_FM_EXPIRED_"
        "ADMISSION_HASH_BINDING"
    )
    assert trace["independent_substitute_digest_count"] == 0
    assert F.sha256(F.FC_ADAPTER) == F.FC_SHA256
    assert F.sha256(F.FM_LAUNCHER) == F.FM_SHA256
    assert F.sha256(F.P11) == F.P11_SHA256
    changed = set(
        subprocess.check_output(
            ["git", "diff", "--name-only"], cwd=ROOT, text=True
        ).splitlines()
    )
    assert changed == {
        JR_PATH.relative_to(ROOT).as_posix(),
        F.FM_LAUNCHER.relative_to(ROOT).as_posix(),
    }


def test_ky_classification_and_cross_vector_scope_remain_bounded() -> None:
    reduction = F.build_reduction()
    classification = reduction["failure_novelty_and_convergence_check"]
    assert classification["failure_class"] == "HARNESS_OR_TEST_ARTIFACT"
    assert classification["classification_confidence"] == "VERIFIED__HIGH"
    reuse = reduction["cross_vector_reuse_assessment"]
    assert reuse["affected_vectors"] == [
        "EXPIRED", "FUTURE", "WRONG_ATTEMPT", "WRONG_CONTRACT",
        "WRONG_INPUT", "WRONG_PROVENANCE",
    ]
    assert reuse["shared_owner_is_shared_defect"] is False
    assert reuse["shared_defect_is_shared_required_delta"] is False
    architecture = reduction["architecture"]
    assert architecture == {
        "p11_mutation": 0,
        "production_mutation": 2,
        "production_files_changed": [
            JR_PATH.relative_to(ROOT).as_posix(),
            F.FM_LAUNCHER.relative_to(ROOT).as_posix(),
        ],
        "new_owner": 0,
        "new_route": 0,
        "new_registry": 0,
        "new_generic_abstraction": 0,
        "new_constitutional_concept": 0,
        "parallel_flow": "NO",
        "production_route": "1_TO_1",
    }


def test_terminal_reduction_is_canonical_inner_sealed_and_zero_operation() -> None:
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
    assert reduction["e05"] == {
        "state": "VERIFIED__11_OF_18",
        "frontier": "VERIFIED__7_UNSATISFIED_OF_18",
        "kz_credit": "VERIFIED__0",
        "expired_status": "NOT_PROVEN_OPERATIONALLY",
    }
    assert reduction["reuse"] == {
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
    }


def test_g48_has_exactly_six_h1_and_exactly_five_reuse_questions() -> None:
    report = REPORT.read_text(encoding="utf-8")
    assert re.findall(r"^# .+$", report, re.MULTILINE) == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    questions = re.findall(r"^\d\. (?:Katere|Ali).+\?$", report, re.MULTILINE)
    assert questions == [
        "1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "2. Katere nove zmogljivosti (če sploh) nastanejo?",
        "3. Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "4. Ali implementacija ustvarja vzporedni tok?",
        "5. Ali zmanjšuje ali povečuje število produkcijskih poti?",
    ]
    assert "OPERATIONAL PROOF = NOT_PERFORMED" in report
    assert "E05 ACCEPTANCE PROOF = NOT_CREATED" in report
    assert report.rstrip().endswith(F.TERMINAL)


def test_no_operational_or_authority_surface_was_added() -> None:
    source = FORMALIZER.read_text(encoding="utf-8") + REPORT.read_text(
        encoding="utf-8"
    )
    assert "subprocess" not in FORMALIZER.read_text(encoding="utf-8")
    reduction = F.build_reduction()
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["auto_continuable"] is False
    assert reduction["human_review_required"] is True
    assert "QEMU_START_COUNT = 0" in source
