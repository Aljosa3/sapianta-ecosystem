#!/usr/bin/env python3
"""Focused deterministic repository-only regression matrix for G77-256KB."""

from __future__ import annotations

from copy import deepcopy
import ast
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import sys

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KB = ROOT / (
    ".github/governance/evidence/"
    "g77_256kb_expired_guest_context_namespace_binding_repair_v1"
)
FORMALIZER = KB / "analysis/G77_256KB_NAMESPACE_BINDING_FORMALIZER_V1.py"


def load(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


F = load(FORMALIZER, "g77_256kb_formalizer")
OWNER = load(ROOT / F.FM_OWNER, "g77_256kb_owner")


def context() -> dict:
    return F.load_canonical(F.KA_CONTEXT)


def root(namespace: str) -> Path:
    return F.operation_root(namespace)


def derive(namespace: str) -> Path:
    return OWNER._derive_sealed_host_repository_root(context(), root(namespace))


def test_authenticated_entry_and_nested_authority() -> None:
    result = F.authenticate_entry_local()
    assert (
        result["branch"], result["head"], result["tree"], result["subject"],
        result["origin"], result["index_empty"],
    ) == (
        F.ENTRY_BRANCH, F.ENTRY_HEAD, F.ENTRY_TREE, F.ENTRY_SUBJECT,
        F.ENTRY_ORIGIN, True,
    )
    assert result["nested"] == {
        "origin": F.NESTED_ORIGIN,
        "head": F.NESTED_HEAD,
        "tree": F.NESTED_TREE,
        "detached": True,
        "clean": True,
        "tag": F.NESTED_TAG,
    }


def test_ka_corrected_v2_terminal_and_serial_are_authenticated() -> None:
    result = F.authenticate_ka_terminal()
    assert result["reduction"]["terminal"].startswith("M__KA_AUTHORIZED_EXPIRED")
    assert result["observation"]["operation_namespace_observed"] == F.KA_NAMESPACE


def test_exact_ka_failure_is_reproduced_from_entry_owner() -> None:
    assert F.reproduce_entry_failure() == (
        "sealed operation projection is not namespace-bound"
    )


def test_exact_ka_namespace_now_passes_current_owner_and_full_projection() -> None:
    result = F.prove_current_repair()
    assert result["owner_sha256"] == F.POST_REPAIR_OWNER_SHA256
    assert result["ka_namespace"] == F.KA_NAMESPACE
    assert result["ka_projection"]["projection_status"] == "EXACT_GUEST_PROJECTION"
    assert result["ka_projection"]["host_canonical_identity"] == str(ROOT)


def test_historically_accepted_expired_namespace_form_remains_accepted() -> None:
    assert derive(F.HISTORICAL_EXPIRED_NAMESPACE) == ROOT


@pytest.mark.parametrize(
    ("namespace", "error"),
    (
        ("g77_256ka_unrelated_operational_v1", "not namespace-bound"),
        ("g77_256ka_future_operational_v1", "not namespace-bound"),
        ("g77_256kb_expired_operational_v1", "not namespace-bound"),
        ("", "noncanonical shape"),
        ("g77_256ka", "noncanonical"),
        ("g77_256ka_fresh_unexpired_operational_v1", "not namespace-bound"),
        ("g77_256ka_expiredness_operational_v1", "not namespace-bound"),
        ("g77_256ka_fresh_expired_v1", "schema is unknown"),
    ),
)
def test_unrelated_wrong_empty_prefix_and_substitution_namespaces_reject(
    namespace: str, error: str,
) -> None:
    with pytest.raises(OWNER.ContextError, match=error):
        derive(namespace)


@pytest.mark.parametrize(
    "operation_root",
    (
        ROOT / ".github/governance/evidence" / F.KA_NAMESPACE / "runtime_export",
        ROOT / ".github/governance/evidence" / F.KA_NAMESPACE / "operation_state" / "extra",
        ROOT / ".github/governance" / F.KA_NAMESPACE / "operation_state",
    ),
)
def test_projection_root_mismatch_and_runtime_role_confusion_reject(
    operation_root: Path,
) -> None:
    with pytest.raises(OWNER.ContextError):
        OWNER._derive_sealed_host_repository_root(context(), operation_root)


def test_full_context_rejects_operation_root_substitution_after_seal() -> None:
    mutated = deepcopy(context())
    mutated["operation_evidence_root"] = str(
        root(F.HISTORICAL_EXPIRED_NAMESPACE)
    )
    with pytest.raises(OWNER.ContextError, match="context seal mismatch"):
        OWNER.validate_context(mutated, repository_root=ROOT)


def test_post_repair_rule_is_two_bounded_forms_without_generation_exception() -> None:
    source = inspect.getsource(OWNER._derive_sealed_host_repository_root)
    assert 'f"{prefix}_{vector}_"' in source
    assert 'f"{prefix}_fresh_{vector}_"' in source
    assert "G77_256KA" not in source
    assert "g77_256ka" not in source
    assert "registry" not in source.lower()
    assert "matched_leads" in source


def test_stable_jr_checkout_and_existing_expired_projection_remain_bound() -> None:
    value = context()
    checkout = value["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    assert (checkout["head"], checkout["tree"], checkout["detached"], checkout["clean"]) == (
        "304b342e26e92f226afa01db4b4203acfa51f532",
        "fc0c50e4dd79e900d85d48c5c0aeb53fe9d0c937",
        True,
        True,
    )
    assert hashlib.sha256((ROOT / F.JR_ADAPTER).read_bytes()).hexdigest() == (
        F.JR_ADAPTER_SHA256
    )
    assert hashlib.sha256((ROOT / F.JX_SEED).read_bytes()).hexdigest() == F.JX_SEED_SHA256


def test_launcher_binds_repaired_owner_and_sole_route_is_preserved() -> None:
    result = F.prove_reuse_and_route()
    assert result["production_route_before"] == result["production_route_after"] == 1
    assert result["p11_sha256"] == F.P11_SHA256
    launcher = (ROOT / F.FM_LAUNCHER).read_text(encoding="utf-8")
    assert launcher.count(F.POST_REPAIR_OWNER_SHA256) == 1


def test_no_operation_and_no_ka_rewrite() -> None:
    assert F.ZERO_COUNTERS == {key: 0 for key in F.ZERO_COUNTERS}
    assert hashlib.sha256(F.KA_REDUCTION_V2.read_bytes()).hexdigest() == (
        F.KA_REDUCTION_V2_SHA256
    )
    assert hashlib.sha256(F.KA_OBSERVATION_V2.read_bytes()).hexdigest() == (
        F.KA_OBSERVATION_V2_SHA256
    )
    assert hashlib.sha256(F.KA_SERIAL.read_bytes()).hexdigest() == F.KA_SERIAL_SHA256
    formalizer_tree = ast.parse(FORMALIZER.read_text(encoding="utf-8"))
    forbidden_calls = {
        "materialize_operation_state", "consume", "invoke", "qemu", "run_operation"
    }
    observed = {
        node.func.id
        for node in ast.walk(formalizer_tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert not observed.intersection(forbidden_calls)


def test_complete_spce_formalization() -> None:
    result = F.formalize()
    assert result["terminal"] == (
        "A__EXPIRED_GUEST_CONTEXT_NAMESPACE_BINDING_REPOSITORY_VERIFIED"
    )
    assert result["pre_repair"]["exact_ka_result"] == (
        "sealed operation projection is not namespace-bound"
    )
    assert result["reuse"]["ex_reused"] == "VERIFIED__17_OF_17"
    assert result["reuse"]["ex_reconstructed"] == "VERIFIED__0"
    assert result["operational_counters"] == F.ZERO_COUNTERS


def test_terminal_reduction_is_canonical_and_inner_sealed() -> None:
    path = KB / "G77_256KB_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
    reduction = F.authenticate_envelope(path, "reduction", "reduction_sha256")
    assert reduction["terminal"] == (
        "A__EXPIRED_GUEST_CONTEXT_NAMESPACE_BINDING_REPOSITORY_VERIFIED"
    )
    assert reduction["operational_counters"] == F.ZERO_COUNTERS


def test_g48_has_exactly_six_h1_and_exactly_five_ria_questions() -> None:
    report = (KB / "G77_256KB_G48_IMPLEMENTATION_REPORT_V1.md").read_text(
        encoding="utf-8"
    )
    headings = [line for line in report.splitlines() if line.startswith("# ")]
    assert headings == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    questions = (
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
    )
    assert sum(report.count(question) for question in questions) == 5
    assert all(report.count(question) == 1 for question in questions)
