#!/usr/bin/env python3
"""Focused repository-only tests for G77-256JF Option A."""

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
JF = ROOT / ".github/governance/evidence/g77_256jf_future_current_fm_context_owner_exact_governed_operation_namespace_binding_v1"
FORMALIZER = JF / "analysis/G77_256JF_OPERATION_NAMESPACE_BINDING_FORMALIZER_V1.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


F = load(FORMALIZER, "g77_256jf_formalizer")
OWNER = load(ROOT / F.FM_OWNER, "g77_256jf_current_fm_owner")
LAUNCHER = load(ROOT / F.FM_LAUNCHER, "g77_256jf_current_fm_launcher")


def context() -> dict:
    return F.load_canonical(F.CONTEXT)


def projection(value: dict):
    return OWNER.validate_sealed_canonical_argv(
        value, validation_repository_root=OWNER.GUEST_REPOSITORY_ROOT
    )


def test_selection_checkpoint_and_pinned_authority() -> None:
    result = F.authenticate_selection_checkpoint()
    assert (result["head"], result["tree"], result["subject"]) == (
        F.ENTRY_HEAD, F.ENTRY_TREE, F.ENTRY_SUBJECT,
    )
    assert result["index_empty"] is True
    assert result["nested_detached"] is result["nested_clean"] is True


def test_option_a_end_to_end_proof_gate() -> None:
    result = F.option_a_proof_gate()
    assert result["result"] == "VERIFIED__OPTION_A_PROOF_GATE_PASS"
    assert result["namespace_authority_owner"] == "SEALED_CONTEXT_OPERATION_EVIDENCE_ROOT"
    assert result["exact_root"] == F.EXACT_ROOT
    assert result["caller_override"].endswith("AUTHENTICATED_IDENTITY_CHANGE")
    assert result["vector_only_substitution_identity"] != F.CONTEXT_SHA256
    assert result["cross_generation_substitution_identity"] != F.CONTEXT_SHA256
    assert result["cross_operation_substitution_identity"] != F.CONTEXT_SHA256


def test_exact_je_namespace_is_accepted_by_current_owner_repository_only() -> None:
    result = projection(context())
    assert result["projection_status"] == "EXACT_GUEST_PROJECTION"
    assert result["host_canonical_identity"] == str(ROOT)


@pytest.mark.parametrize("replacement", (
    "/home/pisarna/work/sapianta-fl/.github/governance/evidence/g77_256jd_future_fresh_human_authorized_operational_denial_v1/operation_state",
    "/home/pisarna/work/sapianta-fl/.github/governance/evidence/g77_256je_wrong_input_operational_v1/operation_state",
    "/home/pisarna/work/sapianta-fl/.github/governance/evidence/g77_256je_future_v1/operation_state",
    "/home/pisarna/work/sapianta-fl/.github/governance/evidence/G77_256JE_FUTURE_OPERATIONAL_V1/operation_state",
    "/home/pisarna/work/sapianta-fl/.github/governance/evidence/g77_256je_future_operational_v2/operation_state",
    "/home/pisarna/work/sapianta-fl/.github/governance/evidence/g77_256je_future_operational_v1/wrong_terminal",
    "/home/pisarna/work/sapianta-fl/.github/governance/evidence/g77_256je_future_operational_v1/extra/operation_state",
    "/home/pisarna/work/sapianta-fl/outside/g77_256je_future_operational_v1/operation_state",
    "/home/pisarna/work/sapianta-fl/.github/governance/evidence/g77_256fm_future_operational_v1/operation_state",
))
def test_foreign_or_noncanonical_namespace_shapes_reject(replacement: str) -> None:
    mutated = deepcopy(context())
    mutated["operation_evidence_root"] = replacement
    with pytest.raises(OWNER.ContextError):
        projection(mutated)


@pytest.mark.parametrize("value", (
    "relative/operation_state",
    "/home/pisarna/work/../escape/operation_state",
    "/home/pisarna/work/./sapianta-fl/operation_state",
    "/home//pisarna/work/sapianta-fl/operation_state",
    "/home/pisarna/work/sapianta-fl/operation_state/",
))
def test_path_normalization_ambiguity_rejects(value: str) -> None:
    with pytest.raises(OWNER.ContextError, match="canonical safe absolute path"):
        OWNER._absolute_canonical_path(value, "operation_evidence_root")


def test_symlink_escape_rejects(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    alias = tmp_path / "alias"
    alias.symlink_to(target, target_is_directory=True)
    with pytest.raises(OWNER.ContextError, match="symlink-sensitive"):
        OWNER._assert_no_symlink_components(alias / "operation_state", allow_missing=True)


def test_missing_and_unsealed_roots_reject() -> None:
    missing = context()
    del missing["operation_evidence_root"]
    with pytest.raises(OWNER.ContextError, match="fields missing"):
        OWNER.validate_context(missing, repository_root=ROOT)
    unsealed = context()
    unsealed["operation_evidence_root"] = F.VECTOR_ONLY_ROOT
    with pytest.raises(OWNER.ContextError):
        OWNER.validate_context(unsealed, repository_root=ROOT)


def test_vector_only_and_cross_identity_substitution_lose_authorized_identity() -> None:
    original = context()
    for replacement in (
        F.VECTOR_ONLY_ROOT,
        F.EXACT_ROOT.replace("g77_256je_", "g77_256jd_"),
        F.EXACT_ROOT.replace("operational_denial", "operational_request"),
    ):
        assert F.reject_root_substitution(original, replacement) != F.CONTEXT_SHA256


def test_no_caller_namespace_override_and_no_generation_exception_table() -> None:
    source = inspect.getsource(OWNER._derive_sealed_host_repository_root)
    assert "caller" not in source.lower()
    assert "G77_256JE" not in source
    assert "g77_256je" not in source
    assert "expected_suffix" not in source
    assert "operation_namespace.startswith" in source
    assert "GOVERNED_OPERATION_NAMESPACE.fullmatch" in source


def test_existing_owner_hash_binding_and_single_route_are_preserved() -> None:
    owner_hash = hashlib.sha256((ROOT / F.FM_OWNER).read_bytes()).hexdigest()
    launcher = (ROOT / F.FM_LAUNCHER).read_text(encoding="utf-8")
    assert owner_hash in launcher
    tree = ast.parse(launcher)
    mains = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main"]
    assert len(mains) == 1
    qemu_calls = [
        node for node in ast.walk(mains[0])
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "subprocess"
        and node.func.attr == "run"
    ]
    assert len(qemu_calls) == 1


def test_current_jc_jd_projection_contract_remains_three_member_and_read_only(
    tmp_path: Path,
) -> None:
    operation_root = tmp_path / "evidence" / "operation_state"
    transient_root = tmp_path / "transient"
    operation_root.parent.mkdir()
    context_value = LAUNCHER.build_operation_context(
        repository_root=ROOT,
        repository_head=F.ENTRY_HEAD,
        repository_tree=F.ENTRY_TREE,
        generation_identity="G77_256JF_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING_V1",
        operation_identity="G77_256JF_E05_FUTURE_DENIAL_BEFORE_ENTRY_001",
        identity_namespace_prefix="G77_256JF",
        operation_evidence_root=operation_root,
        transient_root=transient_root,
        candidate_source_path=Path(
            ".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/"
            "live_binding/candidate/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json"
        ),
    )
    context_source = tmp_path / "context.json"
    context_source.write_bytes(F.canonical_bytes(context_value))
    materialized = LAUNCHER.materialize_operation_state(
        repository_root=ROOT,
        context=context_value,
        context_source_path=context_source,
        candidate_source_path=Path(
            ".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/"
            "live_binding/candidate/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json"
        ),
    )
    observed = LAUNCHER.observe_context_assets(
        ROOT,
        context_value,
        Path(
            ".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/"
            "live_binding/candidate/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json"
        ),
    )
    readiness = LAUNCHER.authority_free_static_readiness(
        repository_root=ROOT,
        context=context_value,
        observed_head=F.ENTRY_HEAD,
        observed_tree=F.ENTRY_TREE,
        repository_clean=True,
        observed_asset_sha256=observed,
        candidate_source_path=Path(
            ".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/"
            "live_binding/candidate/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json"
        ),
    )
    projection = Path(context_value["guest_adapter_binding"]["projection_root"])
    assert materialized["qemu_execution_count"] == 0
    assert readiness["result"] == "STATIC_READINESS_PASS"
    assert len(list(projection.iterdir())) == 3
    assert (projection / LAUNCHER.FRESH_OPERATION_CONTEXT_OWNER_PROJECTION_FILENAME).read_bytes() == (ROOT / F.FM_OWNER).read_bytes()
    assert context_value["wrapper_fc_er_che_schema_hashes"]["fresh_operation_context_owner"] == hashlib.sha256((ROOT / F.FM_OWNER).read_bytes()).hexdigest()


def test_du_eb_ee_v2_remain_unchanged_and_fail_closed_on_uncommitted_owner() -> None:
    for family in (
        ".github/governance/evidence/g77_256du_continuation_manifest_contract_v2",
        ".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v2",
        ".github/governance/evidence/g77_256ee_runtime_consumer_binding_v2",
    ):
        assert F.git("diff", "--name-only", "HEAD", "--", family) == ""
    du = load(
        ROOT / ".github/governance/evidence/g77_256du_continuation_manifest_contract_v2/validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V2.py",
        "g77_256jf_du_v2",
    )
    with pytest.raises(du.CompatibilityError, match="RUNTIME_TARGET_SELECTION_WORKTREE_DRIFT"):
        du.build_du_fixture(ROOT)


def test_historical_je_evidence_and_p11_are_unmodified() -> None:
    assert F.git("diff", "--name-only", "HEAD", "--", str(F.JE.relative_to(ROOT))) == ""
    assert F.git("diff", "--name-only", "HEAD", "--", ".github/governance/evidence/g77_256er_p11_operational_v1") == ""


def test_future_semantics_are_unchanged() -> None:
    adapter = (ROOT / ".github/governance/evidence/g77_256jc_future_guest_context_owner_projection_v1/adapter/G77_256JC_FUTURE_VECTOR_ADAPTER_V1.py").read_text(encoding="utf-8")
    for value in (
        "EVALUATION_TIME_UNIX_NS = 500", "BASELINE_VALID_FROM_UNIX_NS = 100",
        "FUTURE_VALID_FROM_UNIX_NS = 600", "VALID_UNTIL_UNIX_NS = 1000",
        "9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547",
        "operational Human act is not current",
    ):
        assert value in adapter


def test_terminal_is_canonical_and_sealed() -> None:
    envelope = F.load_canonical(F.TERMINAL)
    assert envelope == F.terminal_envelope()
    assert envelope["reduction_sha256"] == hashlib.sha256(
        F.canonical_bytes(envelope["reduction"])
    ).hexdigest()
    assert envelope["reduction"]["terminal"] == F.TERMINAL_ID
    reduction = envelope["reduction"]
    assert reduction["recovery"]["type"] == (
        "SAME_GENERATION_CROSS_WORKER_PROVIDER_LIMIT_RECOVERY"
    )
    assert reduction["recovery"]["uncommitted_delta_recovery"] == "VERIFIED__YES"
    assert reduction["implementation"]["current_fm_owner_hash_before"] == (
        F.CURRENT_FM_OWNER_HASH_BEFORE
    )
    assert reduction["implementation"]["current_fm_owner_hash_after"] == (
        F.CURRENT_FM_OWNER_HASH_AFTER
    )
    assert reduction["ccwim"]["human_architectural_selection_status"] == (
        "VERIFIED__OPTION_A"
    )


def test_report_has_exactly_six_g48_h1_sections() -> None:
    report = F.REPORT.read_text(encoding="utf-8")
    headings = [line for line in report.splitlines() if line.startswith("# ")]
    assert headings == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    for label in (
        "RECOVERY_TYPE = SAME_GENERATION_CROSS_WORKER_PROVIDER_LIMIT_RECOVERY",
        "UNCOMMITTED_DELTA_RECOVERY | `VERIFIED__YES`",
        "HUMAN_ARCHITECTURAL_SELECTION_STATUS | `VERIFIED__OPTION_A`",
        "CONSTITUTIONAL_FRONTIER_DISTANCE =",
        "CONSTITUTIONAL_FRONTIER_DISTANCe =",
        "PREEXISTING_RECOVERED_JF_DELTA =",
        "RECOVERY_WORKER_ADDITIONAL_DELTA =",
    ):
        assert label in report
