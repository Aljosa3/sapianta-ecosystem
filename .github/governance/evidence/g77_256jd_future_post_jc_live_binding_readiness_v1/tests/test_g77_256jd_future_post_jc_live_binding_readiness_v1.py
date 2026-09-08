#!/usr/bin/env python3
"""Focused repository-only verification for G77-256JD."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
JD = ROOT / ".github/governance/evidence/g77_256jd_future_post_jc_live_binding_readiness_v1"
FORMALIZER = JD / "analysis/G77_256JD_POST_JC_LIVE_BINDING_FORMALIZER_V1.py"
REPORT = JD / "G77_256JD_G48_IMPLEMENTATION_REPORT_V1.md"
TERMINAL = JD / "G77_256JD_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"


def load(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


F = load(FORMALIZER, "g77_256jd_formalizer")
FM = F.load_module("g77_256jd_test_fm", F.FM_LAUNCHER)


def fixture_context(root: Path, launcher=FM) -> dict:
    return F.build_context(root, launcher)


@pytest.fixture(scope="module")
def static_fixture(tmp_path_factory):
    root = tmp_path_factory.mktemp("jd_static_non_authority")
    (root / "evidence").mkdir()
    (root / "transient").mkdir()
    context = fixture_context(root)
    source = root / "context.json"
    source.write_bytes(F.canonical_bytes(context))
    result = FM.materialize_operation_state(
        repository_root=ROOT,
        context=context,
        context_source_path=source,
        candidate_source_path=F.IH_CANDIDATE,
    )
    assert result["qemu_execution_count"] == 0
    return root, context


def canonical(path: Path) -> dict:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=F.unique_object)
    assert isinstance(value, dict)
    assert raw == F.canonical_bytes(value)
    return value


def test_exact_jc_baseline_nested_authority_and_jd_scope() -> None:
    entry = F.authenticate_baseline()
    assert (entry["head"], entry["tree"], entry["subject"]) == (
        F.JC_HEAD, F.JC_TREE, F.JC_SUBJECT,
    )
    assert entry["entry_worktree"] == "AUTHENTICATED_CLEAN_BEFORE_JD"
    assert entry["current_worktree_scope"] == "VERIFIED__JD_EVIDENCE_ONLY"
    assert entry["nested_authority"]["clean"] is True
    assert entry["nested_authority"]["detached"] is True


def test_committed_jc_owner_hashes_and_terminal_are_authenticated() -> None:
    result = F.authenticate_committed_jc()
    assert result["inner_seal"] == "VERIFIED"
    assert result["historical_jc_immutable"] == "VERIFIED"
    assert result["precommit_limitation"] == "NOT_PROVEN__JC_OWNERS_UNCOMMITTED"
    assert set(result["identities"]) == {path.as_posix() for path in F.EXPECTED_SHA256}
    assert {item["worktree_equals_committed"] for item in result["identities"].values()} == {"VERIFIED"}


def test_role_model_preserves_all_required_equalities_and_inequalities() -> None:
    roles = F.role_model()
    assert roles["target_runtime_identity"] == {"head": F.IF_HEAD, "tree": F.IF_TREE}
    assert roles["current_repository_identity"] == {"head": F.JC_HEAD, "tree": F.JC_TREE}
    assert roles["certification_baseline_identity"] == roles["current_repository_identity"]
    assert roles["target_runtime_identity"] != roles["current_repository_identity"]
    assert roles["target_runtime_identity"] == roles["candidate_required_identity"]
    assert roles["target_runtime_identity"] == roles["checkout_identity"]
    assert roles["fm_context_owner_identity"]["sha256"] == roles["guest_projected_context_owner_identity"]["sha256"]
    assert set(roles["relations"].values()) == {"VERIFIED"}


def test_du_eb_ee_v2_post_commit_live_binding_closes_drift() -> None:
    result = F.validate_v2_post_commit_binding()
    assert result["former_worktree_drift_barrier"] == "VERIFIED__CLOSED_BY_COMMITTED_OWNER_BYTES"
    assert result["runtime_target"]["head"] == F.IF_HEAD
    assert result["runtime_target"]["tree"] == F.IF_TREE
    assert result["certification_baseline"] == {"head": F.JC_HEAD, "tree": F.JC_TREE}
    assert result["runtime_target"] != result["certification_baseline"]
    assert result["du_v2"] == "VERIFIED__CURRENT_APPLICABLE_PASS"
    assert result["eb_v2"] == result["ee_v2"] == "VERIFIED__POST_COMMIT_POSITIVE_PATH"
    assert (result["major"], result["semver"], result["suffix"]) == (2, "2.0.0", "V2")


def test_fm_committed_authority_free_static_readiness_passes() -> None:
    result = F.validate_fm_post_commit_binding()
    assert result["result"] == "VERIFIED__STATIC_READINESS_PASS"
    assert result["harness_member_count"] == "VERIFIED__3"
    assert result["guest_owner_projection_cardinality"] == "VERIFIED__1"
    assert result["caller_selected_owner_identity"] == "VERIFIED__NO"
    assert result["qemu_execution_count"] == 0


def test_former_drift_closes_only_through_committed_owner_equality() -> None:
    for relative in (F.FM_LAUNCHER, F.FM_CONTEXT):
        committed = F.committed_bytes(F.JC_HEAD, relative)
        assert (ROOT / relative).read_bytes() == committed
        assert hashlib.sha256(committed).hexdigest() == F.EXPECTED_SHA256[relative]
    assert subprocess.check_output(
        ["git", "diff", "--name-only"], cwd=ROOT, text=True
    ).strip() == ""


def test_actual_committed_jb_negative_gate_remains_fail_closed(
    static_fixture, monkeypatch,
) -> None:
    root, current = static_fixture
    owner_raw = F.committed_bytes(F.JB_HEAD, F.FM_CONTEXT)
    owner = ModuleType("g77_256jd_committed_jb_context")
    owner.__file__ = str(ROOT / F.FM_CONTEXT)
    exec(compile(owner_raw, owner.__file__, "exec"), owner.__dict__)
    historical = ModuleType("g77_256jd_committed_jb_launcher")
    historical.__file__ = str(ROOT / F.FM_LAUNCHER)
    with monkeypatch.context() as imports:
        imports.setitem(sys.modules, "sapianta_fresh_operation_context_v1", owner)
        exec(
            compile(
                F.committed_bytes(F.JB_HEAD, F.FM_LAUNCHER),
                historical.__file__, "exec",
            ),
            historical.__dict__,
        )
    open_path = Path.open

    def committed_view(path, mode="r", *args, **kwargs):
        if path == ROOT / F.FM_CONTEXT:
            assert mode == "rb"
            return io.BytesIO(owner_raw)
        return open_path(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", committed_view)
    context = historical.build_operation_context(
        repository_root=ROOT,
        repository_head=F.JB_HEAD,
        repository_tree="29957cb3f48fe4045978b4b779269b89d186fd20",
        generation_identity="G77_256JB_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING_V1",
        operation_identity="G77_256JB_E05_FUTURE_DENIAL_BEFORE_ENTRY_001",
        identity_namespace_prefix="G77_256JB",
        operation_evidence_root=root / "evidence" / "operation_state",
        transient_root=root / "transient" / "g77_256jd",
        candidate_source_path=F.IH_CANDIDATE,
    )
    assert (
        context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
        == current["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    )
    expected = historical.context_asset_expectations(context, F.IH_CANDIDATE)
    observed = historical.observe_context_assets(ROOT, context, F.IH_CANDIDATE)
    checkout = Path(
        context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["path"]
    )
    mismatch = {
        key: (observed[key], value)
        for key, value in expected.items()
        if observed[key] != value
    }
    assert mismatch == {
        str(checkout / F.FM_CONTEXT): (
            "fdfa04349529d70bc97820a1848f8afc22b81071859d5456550799e0f9476237",
            "da09342d92f2a8d8310987aa0104bd6bd6ad7a3d009b51b8d710443c4884e9c7",
        )
    }
    with pytest.raises(
        RuntimeError,
        match="^authority-free immutable asset or candidate binding mismatch$",
    ):
        historical.authority_free_static_readiness(
            repository_root=ROOT,
            context=context,
            observed_head=F.JB_HEAD,
            observed_tree="29957cb3f48fe4045978b4b779269b89d186fd20",
            repository_clean=True,
            observed_asset_sha256=observed,
            candidate_source_path=F.IH_CANDIDATE,
        )


def test_sealed_harness_positive_path_is_exactly_three(static_fixture) -> None:
    _, context = static_fixture
    projection = Path(context["guest_adapter_binding"]["projection_root"])
    assert len(list(projection.iterdir())) == 3
    FM.prove_guest_adapter_binding(ROOT, context)
    FM.fresh_context.validate_freshness(context, overlay_materialized=True)


@pytest.mark.parametrize(
    "fault",
    F.REQUIRED_HARNESS_REJECTIONS + ("symlink_context_owner",),
)
def test_sealed_harness_rejects_all_required_faults(
    tmp_path: Path, fault: str,
) -> None:
    context = fixture_context(tmp_path)
    binding = context["guest_adapter_binding"]
    projection = Path(binding["projection_root"])
    projection.mkdir(parents=True)
    adapter = Path(binding["projected_path"])
    bootstrap = Path(binding["bootstrap_projected_path"])
    owner = projection / FM.FRESH_OPERATION_CONTEXT_OWNER_PROJECTION_FILENAME
    adapter.write_bytes((ROOT / F.JC_ADAPTER).read_bytes())
    bootstrap.write_bytes(adapter.read_bytes())
    owner.write_bytes((ROOT / F.FM_CONTEXT).read_bytes())
    assert len(list(projection.iterdir())) == 3
    FM.prove_guest_adapter_binding(ROOT, context)
    FM.fresh_context.validate_freshness(context)
    if fault == "missing_context_owner":
        owner.unlink()
    elif fault == "wrong_context_owner":
        owner.write_bytes(b"# incorrect owner\n")
    elif fault == "extra_harness_member":
        (projection / "fourth.py").write_bytes(b"# undeclared\n")
    elif fault == "historical_if_context_owner":
        owner.write_bytes(F.committed_bytes(F.IF_HEAD, F.FM_CONTEXT))
    elif fault == "wrong_adapter":
        adapter.write_bytes(b"# incorrect adapter\n")
    elif fault == "wrong_bootstrap_alias":
        bootstrap.write_bytes(b"# incorrect bootstrap\n")
    else:
        owner.unlink()
        owner.symlink_to(ROOT / F.FM_CONTEXT)
    with pytest.raises(RuntimeError):
        FM.prove_guest_adapter_binding(ROOT, context)


def test_future_semantics_and_nocloud_projection_are_exact() -> None:
    result = F.validate_adapter_nocloud_and_semantics()
    assert result["relation"] == "500 < 600 < 1000"
    assert result["independent_mutated_coordinate"] == "valid_from_unix_ns"
    assert result["wall_clock_dependency_count"] == 0
    assert result["operational_denial"] == "NOT_PROVEN"
    assert set(result["nocloud_projection"]) == {
        "/user-data", "/meta-data", "/network-config",
    }


def test_single_route_ex_p11_history_and_shadow_firewalls() -> None:
    reuse, firewall = F.authenticate_reuse_and_firewalls()
    assert reuse["production_route_before"] == reuse["production_route_after"] == "VERIFIED__1"
    assert reuse["production_route_delta"] == "VERIFIED__0"
    assert reuse["production_owner_mutation_count"] == "VERIFIED__0"
    assert reuse["p11_mutation_count"] == "VERIFIED__0"
    assert reuse["ex_reused"] == "VERIFIED__17_OF_17"
    assert reuse["ex_reconstructed"] == "VERIFIED__0"
    assert firewall["checked_failure_class_count"] == "VERIFIED__32"
    assert firewall["reintroduced_historical_failure_count"] == "VERIFIED__0"
    assert firewall["shadow_automation_status"] == "VERIFIED__ABSENT"


def test_duplicate_json_keys_are_rejected() -> None:
    with pytest.raises(F.JDReadinessError, match="DUPLICATE_JSON_KEY:owner"):
        json.loads('{"owner":1,"owner":2}', object_pairs_hook=F.unique_object)


def test_terminal_is_canonical_inner_sealed_and_operationally_zero() -> None:
    envelope = canonical(TERMINAL)
    reduction = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(
        F.canonical_bytes(reduction)
    ).hexdigest()
    assert envelope == F.terminal_envelope()
    assert reduction["terminal"] == "A__FUTURE_POST_JC_COMMIT_LIVE_BINDING_AND_OPERATIONAL_READINESS_VERIFIED"
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"]["after"] == "VERIFIED__10_OF_18"
    assert reduction["e05"]["credit"] == "VERIFIED__0"


def test_ast_g48_six_headings_required_metrics_and_empty_index() -> None:
    ast.parse(FORMALIZER.read_text(encoding="utf-8"), filename=str(FORMALIZER))
    ast.parse(Path(__file__).read_text(encoding="utf-8"), filename=__file__)
    text = REPORT.read_text(encoding="utf-8")
    assert [line for line in text.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    required = (
        "Reuse Impact Assessment", "CONSTITUTIONAL_HEALTH_EVIDENCE",
        "SHADOW_AUTOMATION_STATUS", "CONSTITUTIONAL_FRONTIER_DISTANCE",
        "CONSTITUTIONAL_FRONTIER_DISTANCe", "GOVERNANCE_EFFICIENCE",
        "COGNITION_ASSISTED_HANDOFF", "COGNITION_PROVENANCE",
        "AIGOL_CODEX_WORK_SHARE", "PROMPT_CONTEXT_REUSE_RATIO",
        "OVERENGINEERING_RISK", "CANDIDATE_CAPABILITY",
        "SHADOW_DESIGN_TARGET", "CONSTITUTIONAL_CONTINUATION_PROGRESS",
        "CCWIM_MATURITY_LEVEL", "Infrastructure Amortization",
        "Historical Failure Firewall",
    )
    assert all(value in text for value in required)
    assert subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True
    ).strip() == ""
