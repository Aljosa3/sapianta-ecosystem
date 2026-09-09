#!/usr/bin/env python3
"""Repository-only G77-256JN committed binding and readiness tests."""

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
JN = ROOT / (
    ".github/governance/evidence/"
    "g77_256jn_post_jm_live_binding_ex_successor_reauthentication_and_"
    "expired_operational_readiness_v1"
)
FORMALIZER = JN / "analysis/G77_256JN_POST_JM_READINESS_FORMALIZER_V1.py"
REPORT = JN / "G77_256JN_G48_IMPLEMENTATION_REPORT_V1.md"
REDUCTION = JN / "G77_256JN_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
JM_TEST = ROOT / (
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


F = load(FORMALIZER, "g77_256jn_formalizer")
JM = load(JM_TEST, "g77_256jn_committed_jm_tests")


def test_exact_committed_remote_ratified_jm_entry_and_nested_authority() -> None:
    result = F.authenticate_entry()
    assert result["branch"] == F.BRANCH
    assert result["head"] == result["remote_tracking_head"] == F.ENTRY_HEAD
    assert result["tree"] == F.ENTRY_TREE
    assert result["subject"] == F.ENTRY_SUBJECT
    assert result["index_empty"] is True
    assert result["tracked_delta"] == []
    assert set(result["untracked_jn_files"]) == F.EXPECTED_JN_FILES
    assert result["nested_origin"] == F.NESTED_ORIGIN
    assert result["nested_head"] == F.NESTED_HEAD
    assert result["nested_tree"] == F.NESTED_TREE
    assert result["nested_detached"] is result["nested_clean"] is True


def test_committed_jm_reconstructs_exactly_from_nine_objects() -> None:
    result = F.reconstruct_jm()
    assert result["terminal"] == F.JM_TERMINAL
    assert result["inner_seal"] == "VERIFIED"
    assert result["artifact_count"] == 9
    assert result["committed_delta"].startswith("VERIFIED__9_FILES")
    for identity in result["identities"].values():
        path = Path(identity["path"])
        assert (ROOT / path).read_bytes() == F.committed_bytes(path)
        assert hashlib.sha256(F.committed_bytes(path)).hexdigest() == identity["sha256"]


def test_ex_successor_reauthenticates_only_committed_p11_hardening() -> None:
    result = F.verify_ex_successor_reauthentication()
    assert result["historical_parent_validation"]["regression_pass"] == 12
    assert result["required_component_count"] == 29
    assert result["unchanged_required_component_count"] == 28
    assert result["changed_required_component_count"] == 1
    assert result["changed_component"] == {
        "identity": "P11_OPERATIONAL_CONSUMER",
        "path": "tests/p11_da_operational_consumer_v1.py",
        "classification": "REQUIRES_HARDENING",
        "historical_sha256": F.TARGET_P11_SHA256,
        "successor_sha256": F.CURRENT_P11_SHA256,
    }
    assert result["ex_reused"] == "VERIFIED__17_OF_17"
    assert result["ex_reconstructed"] == "VERIFIED__0"
    assert result["new_certificate_created"] == "VERIFIED__NO"
    assert result["parallel_proof_owner_created"] == "VERIFIED__NO"


@pytest.mark.parametrize("wrong", ["0" * 64, F.TARGET_P11_SHA256])
def test_wrong_or_stale_ex_successor_p11_binding_fails_closed(wrong: str) -> None:
    with pytest.raises(F.JNError, match="EX_SUCCESSOR_P11_BINDING_MISMATCH"):
        F.verify_ex_successor_reauthentication(wrong)


def test_committed_option_a_root_binding_is_intact_but_route_not_ready() -> None:
    result = F.verify_committed_live_binding_and_route()
    assert result["committed_root_option_a_binding"] == "VERIFIED"
    assert result["committed_p11_preclaim_source"].startswith("VERIFIED")
    assert result["runtime_target"] == {
        "head": F.TARGET_HEAD, "tree": F.TARGET_TREE
    }
    assert result["runtime_target_p11_sha256"] == F.TARGET_P11_SHA256
    assert result["committed_jm_p11_sha256"] == F.CURRENT_P11_SHA256
    assert result["runtime_target_uses_committed_jm_p11"] == "VERIFIED__NO"
    assert result["er_gate_missing_required_keywords"] == [
        "operation_context_sha256", "preclaim_temporal_binding_identity"
    ]
    assert result["er_consumer_missing_required_keywords"] == [
        "fresh_operation_context"
    ]
    assert result["expired_operational_readiness"].startswith("NOT_PROVEN")


def test_existing_route_remains_exactly_one_without_jn_mutation() -> None:
    result = F.verify_committed_live_binding_and_route()
    assert result["production_route_before"] == "VERIFIED__1"
    assert result["production_route_after"] == "VERIFIED__1"
    assert result["production_route_delta"] == "VERIFIED__0"
    assert F.git("diff", "--name-only", "HEAD") == ""
    assert F.git("diff", "--cached", "--name-only") == ""


def test_committed_context_materializes_and_authenticates_coordinate(tmp_path: Path) -> None:
    context = JM.context_for(tmp_path)
    assert context["preclaim_temporal_binding"]["coordinate_unix_ns"] == 1000
    assert JM.FM.validate_context(context, repository_root=ROOT) == context
    binding, context_sha256 = JM.authenticate_preclaim_temporal_binding(context)
    assert context_sha256 == context["context_sha256"]
    assert binding["operation_identity"] == context["operation_identity"]


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value.pop("preclaim_temporal_binding"),
        lambda value: value["preclaim_temporal_binding"].update(
            {"coordinate_unix_ns": "1000"}
        ),
        lambda value: value["preclaim_temporal_binding"].update(
            {"coordinate_unix_ns": 999}
        ),
        lambda value: value["preclaim_temporal_binding"].update(
            {"operation_identity": "G77_256JN_OTHER_OPERATION_001"}
        ),
        lambda value: value["preclaim_temporal_binding"].update(
            {"provider_coordinate_unix_ns": 1000}
        ),
        lambda value: value["preclaim_temporal_binding"].update(
            {"caller_coordinate_unix_ns": 1000}
        ),
    ],
)
def test_missing_malformed_substituted_operation_and_selection_fail_closed(
    tmp_path: Path, mutation
) -> None:
    context = JM.context_for(tmp_path)
    mutation(context)
    JM.reseal(context)
    with pytest.raises(JM.FM.ContextError):
        JM.FM.validate_context(context, repository_root=ROOT)


def test_coordinate_mutation_after_sealing_fails_before_p11(tmp_path: Path) -> None:
    context = JM.context_for(tmp_path)
    context["preclaim_temporal_binding"]["coordinate_unix_ns"] = 999
    with pytest.raises(JM.FM.ContextError, match="context seal mismatch"):
        JM.FM.validate_context(context, repository_root=ROOT)


def test_human_and_gate_correlation_reject_post_correlation_mutation(
    tmp_path: Path,
) -> None:
    context = JM.context_for(tmp_path)
    human = JM.LAUNCHER.preauthority_serialization_fixture(context)
    store = JM.store_for(tmp_path)
    bindings = JM.FixedPrincipalBindings(
        os.getuid() + 1, os.getuid() + 2, os.getuid()
    )
    gate = JM.gate_for(context, store, bindings)
    context["preclaim_temporal_binding"]["coordinate_unix_ns"] = 999
    JM.reseal(context)
    assert human["authorized_context_sha256"] != context["context_sha256"]
    with pytest.raises(Exception, match="temporal binding|commissioning gate"):
        JM.P11BoundedConsumerV1(
            store=store,
            principal_bindings=bindings,
            commissioning_gate=gate,
            fresh_operation_context=context,
        )


def test_temporal_boundary_and_wall_clock_disagreement_are_deterministic(
    tmp_path: Path,
) -> None:
    binding, _ = JM.authenticate_preclaim_temporal_binding(JM.context_for(tmp_path))
    decisions = [
        JM.preclaim_temporal_decision(
            dict(binding, coordinate_unix_ns=value),
            valid_from_unix_ns=100,
            valid_until_unix_ns=1000,
        )
        for value in (999, 1000, 1001)
    ]
    assert decisions == ["CURRENT", "EXPIRED", "EXPIRED"]
    assert decisions == [
        JM.preclaim_temporal_decision(
            dict(binding, coordinate_unix_ns=value),
            valid_from_unix_ns=100,
            valid_until_unix_ns=1000,
        )
        for value in (999, 1000, 1001)
    ]


def test_claim_has_no_temporal_selection_or_wall_clock_fallback() -> None:
    signature = inspect.signature(JM.P11BoundedConsumerV1.claim_and_invoke_once)
    assert not ({"now", "time", "clock", "provider", "preclaim_time"} & set(
        signature.parameters
    ))
    source = inspect.getsource(JM.P11BoundedConsumerV1.claim_and_invoke_once)
    assert "time.time_ns" not in source
    assert 'temporal_binding["coordinate_unix_ns"]' in source
    assert source.index("authenticate_preclaim_temporal_binding") < source.index(
        "preclaim_temporal_decision"
    ) < source.index('"P11_DA_OPERATIONAL_PRECLAIM"')


def test_jn_suite_contains_no_operational_entry_call() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    forbidden = tuple("." + name + "(" for name in (
        "submit_human_act", "claim_and_invoke_once", "main"
    ))
    assert all(token not in source for token in forbidden)


def test_reduction_is_unique_key_canonical_inner_sealed_and_blocked() -> None:
    def unique(pairs):
        value = {}
        for key, item in pairs:
            assert key not in value
            value[key] = item
        return value

    envelope = json.loads(REDUCTION.read_bytes(), object_pairs_hook=unique)
    reduction = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(
        F.canonical_bytes(reduction)
    ).hexdigest()
    assert reduction["terminal"] == F.TERMINAL
    assert set(reduction["operational_counters"].values()) == {"VERIFIED__0"}
    assert reduction["architecture"]["p11_implementation_mutation_count"] == "VERIFIED__0"
    assert reduction["architecture"]["production_mutation_count"] == "VERIFIED__0"
    assert reduction["auto_continuable"] is False
    assert reduction["human_review_required"] is True


def test_g48_report_has_exact_six_h1_and_required_sections() -> None:
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
    assert "## Reuse Impact Assessment" in report
    assert "## Constitutional Continuity & Worker Independence Metrics — CCWIM" in report
    for question in (
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
    ):
        assert question in report
    assert report.split("# 6. Certification Verdict", 1)[1].strip() == F.TERMINAL


def test_jn_delta_is_evidence_only_and_layer_zero_untouched() -> None:
    assert subprocess.check_output(
        ["git", "diff", "--name-only"], cwd=ROOT, text=True
    ).strip() == ""
    status = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT,
        text=True,
    ).splitlines()
    paths = {
        line[3:] for line in status
        if "__pycache__" not in line
    }
    assert paths == F.EXPECTED_JN_FILES
    assert all(path.startswith(F.JN.as_posix() + "/") for path in paths)
