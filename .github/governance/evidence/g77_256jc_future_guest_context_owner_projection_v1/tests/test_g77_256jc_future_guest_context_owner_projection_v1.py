#!/usr/bin/env python3
"""Focused repository-only verification for G77-256JC."""

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
JC = ROOT / ".github/governance/evidence/g77_256jc_future_guest_context_owner_projection_v1"
FORMALIZER = JC / "analysis/G77_256JC_GUEST_CONTEXT_OWNER_PROJECTION_FORMALIZER_V1.py"
REPORT = JC / "G77_256JC_G48_IMPLEMENTATION_REPORT_V1.md"
TERMINAL = JC / "G77_256JC_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"


def load(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


F = load(FORMALIZER, "g77_256jc_formalizer")
FM = load(ROOT / F.FM_LAUNCHER, "g77_256jc_fm")


def fixture_context(tmp_path: Path, launcher=FM, *, operation_root=None) -> dict:
    return launcher.build_operation_context(
        repository_root=ROOT,
        repository_head=F.HEAD,
        repository_tree=F.TREE,
        generation_identity="G77_256JB_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING_V1",
        operation_identity="G77_256JB_E05_FUTURE_DENIAL_BEFORE_ENTRY_001",
        identity_namespace_prefix="G77_256JB",
        operation_evidence_root=operation_root or tmp_path / "evidence" / "operation_state",
        transient_root=tmp_path / "transient" / "g77_256jc",
        candidate_source_path=F.IH_CANDIDATE,
    )


@pytest.fixture(scope="module")
def static_fixture(tmp_path_factory):
    """Disposable static input only; never invoke launcher/adapter main or PRE."""
    root = tmp_path_factory.mktemp("jc_static_non_authority")
    (root / "evidence").mkdir()
    (root / "transient").mkdir()
    context = fixture_context(root)
    source = root / "context.json"
    source.write_bytes(F.canonical_bytes(context))
    result = FM.materialize_operation_state(
        repository_root=ROOT, context=context, context_source_path=source,
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


def test_exact_jb_baseline_nested_authority_and_index() -> None:
    entry = F.authenticate_baseline()
    assert (entry["head"], entry["tree"], entry["subject"]) == (F.HEAD, F.TREE, F.SUBJECT)
    assert entry["index_empty"] is True
    assert entry["nested_authority"]["clean"] is True
    assert entry["nested_authority"]["detached"] is True


def test_pre_correction_exact_jb_failure_is_reproduced_from_committed_objects() -> None:
    result = F.reconstruct_jb_failure()
    assert result == {
        "terminal": "M__CERTIFIED_ROUTE_DRIFT_DETECTED",
        "jb_owner_sha256": F.JB_OWNER_SHA256,
        "if_owner_sha256": F.IF_OWNER_SHA256,
        "exact_mismatch_reproduced": True,
    }


def test_identity_roles_preserve_runtime_certification_separation() -> None:
    roles = F.role_model()
    assert roles["target_runtime_identity"] == {"head": F.IF_HEAD, "tree": F.IF_TREE}
    assert roles["current_repository_identity"] == {"head": F.HEAD, "tree": F.TREE}
    assert roles["target_runtime_identity"] != roles["current_repository_identity"]
    assert roles["candidate_required_identity"] == roles["checkout_identity"]
    assert roles["fm_context_owner_identity"]["sha256"] == roles["guest_projected_context_owner_identity"]["sha256"]
    assert set(roles["equalities"].values()) == {"VERIFIED"}


def test_unique_existing_projection_mechanism_and_exact_owner_hashes() -> None:
    result = F.authenticate_unique_projection_mechanism()
    assert result["class"].startswith("C__AUTHENTICATED_CURRENT_OWNER_PROJECTED_SEPARATELY")
    assert result["runtime_certification_role_collapse"] is False
    assert result["caller_selected_owner_identity"] is False
    assert result["generic_framework"] is False


def test_post_correction_authority_free_static_readiness(static_fixture) -> None:
    _, context = static_fixture
    observed = FM.observe_context_assets(ROOT, context, F.IH_CANDIDATE)
    readiness = FM.authority_free_static_readiness(
        repository_root=ROOT,
        context=context,
        observed_head=F.HEAD,
        observed_tree=F.TREE,
        repository_clean=True,
        observed_asset_sha256=observed,
        candidate_source_path=F.IH_CANDIDATE,
    )
    proof = readiness["checkout_readiness"]["preauth_guest_fm_context_owner_binding"]
    assert readiness["result"] == "STATIC_READINESS_PASS"
    assert proof["projection_sha256"] == F.JC_OWNER_SHA256
    assert proof["guest_visible_path"] == F.GUEST_OWNER_PATH
    assert proof["detached_checkout_owner_identity"] == "PRESERVED_AS_RUNTIME_PROVENANCE"
    assert set(
        Path(context["guest_adapter_binding"]["projection_root"]).iterdir()
    ) == {
        Path(context["guest_adapter_binding"]["projected_path"]),
        Path(context["guest_adapter_binding"]["bootstrap_projected_path"]),
        Path(context["guest_adapter_binding"]["projection_root"])
        / FM.FRESH_OPERATION_CONTEXT_OWNER_PROJECTION_FILENAME,
    }
    checkout = Path(context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["path"])
    assert F.git("rev-parse", "HEAD", cwd=checkout) == F.IF_HEAD
    assert F.git("rev-parse", "HEAD^{tree}", cwd=checkout) == F.IF_TREE
    assert F.git("status", "--porcelain=v1", "--untracked-files=all", cwd=checkout) == ""
    assert F.git("branch", "--show-current", cwd=checkout) == ""
    assert F.sha256(checkout / F.FM_CONTEXT_OWNER) == F.IF_OWNER_SHA256


def test_uncorrected_committed_jb_gate_rejects_exact_owner_mismatch(
    static_fixture, monkeypatch,
) -> None:
    # Execute both committed JB owners. Only the one modified source-file read
    # is mapped to its authenticated JB blob; no gate or hash is mocked.
    root, current = static_fixture
    owner_raw = F.committed_bytes(F.HEAD, F.FM_CONTEXT_OWNER)
    owner = ModuleType("jc_committed_jb_context")
    owner.__file__ = str(ROOT / F.FM_CONTEXT_OWNER)
    exec(compile(owner_raw, owner.__file__, "exec"), owner.__dict__)
    historical = ModuleType("jc_committed_jb_launcher")
    historical.__file__ = str(ROOT / F.FM_LAUNCHER)
    with monkeypatch.context() as imports:
        imports.setitem(sys.modules, "sapianta_fresh_operation_context_v1", owner)
        exec(compile(F.committed_bytes(F.HEAD, F.FM_LAUNCHER), historical.__file__, "exec"), historical.__dict__)
    assert historical.fresh_context is owner
    open_path = Path.open

    def committed_view(path, mode="r", *args, **kwargs):
        if path == ROOT / F.FM_CONTEXT_OWNER:
            assert mode == "rb"
            return io.BytesIO(owner_raw)
        return open_path(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", committed_view)
    context = fixture_context(root, historical)
    assert context["qemu_executable_base_seed_checkout_bindings"]["checkout"] == current["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    expected = historical.context_asset_expectations(context, F.IH_CANDIDATE)
    observed = historical.observe_context_assets(ROOT, context, F.IH_CANDIDATE)
    mismatch = {key: (observed[key], value) for key, value in expected.items() if observed[key] != value}
    checkout = Path(context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["path"])
    assert mismatch == {str(checkout / F.FM_CONTEXT_OWNER): (F.IF_OWNER_SHA256, F.JB_OWNER_SHA256)}
    with pytest.raises(RuntimeError, match="^authority-free immutable asset or candidate binding mismatch$"):
        historical.authority_free_static_readiness(
            repository_root=ROOT, context=context,
            observed_head=F.HEAD, observed_tree=F.TREE,
            repository_clean=True, observed_asset_sha256=observed,
            candidate_source_path=F.IH_CANDIDATE,
        )


def test_dirty_worktree_is_still_a_live_readiness_barrier(static_fixture) -> None:
    _, context = static_fixture
    assert F.git("diff", "--name-only")
    with pytest.raises(RuntimeError, match="^static readiness repository is dirty$"):
        FM.authority_free_static_readiness(
            repository_root=ROOT, context=context,
            observed_head=F.HEAD, observed_tree=F.TREE,
            repository_clean=False,
            observed_asset_sha256=FM.observe_context_assets(ROOT, context, F.IH_CANDIDATE),
            candidate_source_path=F.IH_CANDIDATE,
        )


@pytest.mark.parametrize("fault", (
    "missing_context_owner", "wrong_context_owner", "extra_harness_member",
    "historical_if_context_owner", "wrong_adapter", "wrong_bootstrap_alias",
    "symlink_context_owner",
))
def test_sealed_harness_rejects_each_projection_fault(tmp_path: Path, fault: str) -> None:
    context = fixture_context(tmp_path)
    binding = context["guest_adapter_binding"]
    projection = Path(binding["projection_root"])
    projection.mkdir(parents=True)
    adapter = Path(binding["projected_path"])
    bootstrap = Path(binding["bootstrap_projected_path"])
    owner = projection / FM.FRESH_OPERATION_CONTEXT_OWNER_PROJECTION_FILENAME
    adapter.write_bytes((ROOT / F.JC_ADAPTER).read_bytes())
    bootstrap.write_bytes(adapter.read_bytes())
    owner.write_bytes((ROOT / F.FM_CONTEXT_OWNER).read_bytes())
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
        owner.write_bytes(F.committed_bytes(F.IF_HEAD, F.FM_CONTEXT_OWNER))
    elif fault == "wrong_adapter":
        adapter.write_bytes(b"# incorrect adapter\n")
    elif fault == "wrong_bootstrap_alias":
        bootstrap.write_bytes(b"# incorrect bootstrap\n")
    else:
        owner.unlink()
        owner.symlink_to(ROOT / F.FM_CONTEXT_OWNER)
    with pytest.raises(RuntimeError):
        FM.prove_guest_adapter_binding(ROOT, context)
    if fault in {"missing_context_owner", "extra_harness_member"}:
        with pytest.raises(FM.fresh_context.ContextError, match="stale, duplicate, or ambiguous"):
            FM.fresh_context.validate_freshness(context)


def test_guest_validation_uses_projected_current_adapter_and_context_owner(
    static_fixture, monkeypatch,
) -> None:
    root, materialized = static_fixture
    # No files are created at this sealed host path. Its repository marker is
    # required by the inherited HG host/guest identity contract.
    context = fixture_context(
        root,
        operation_root=ROOT / ".github/governance/evidence/g77_256jb_future_operational_v1/operation_state",
    )
    adapter = load(ROOT / F.JC_ADAPTER, "jc_projection_guest_adapter")
    owner = FM.fresh_context
    open_path = Path.open
    is_file = Path.is_file
    reads = []

    def guest_view(path, mode="r", *args, **kwargs):
        reads.append(path)
        if path == Path(context["guest_adapter_binding"]["bootstrap_guest_path"]):
            return open_path(Path(materialized["guest_adapter_binding"]["bootstrap_projected_path"]), mode, *args, **kwargs)
        if path == adapter.GUEST_CONTEXT_PATH:
            assert mode == "rb"
            return io.BytesIO(F.canonical_bytes(context))
        return open_path(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", guest_view)
    monkeypatch.setattr(
        Path, "is_file",
        lambda path: path == adapter.GUEST_CONTEXT_PATH or is_file(path),
    )
    assert owner.validate_context(context, repository_root=Path("/mnt/aigol")) == context
    assert Path(context["guest_adapter_binding"]["bootstrap_guest_path"]) in reads
    assert Path("/mnt/aigol") / F.JC_ADAPTER not in reads

    class StopBeforeRuntime(Exception):
        pass

    selected = []

    def load_projected_owner(path, name):
        selected.append(path)
        assert path == Path(F.GUEST_OWNER_PATH)
        return owner

    def stop_before_runtime(**kwargs):
        raise StopBeforeRuntime

    monkeypatch.setattr(adapter, "_load", load_projected_owner)
    monkeypatch.setattr(adapter, "specialize_fc_runtime_source", stop_before_runtime)
    with pytest.raises(StopBeforeRuntime):
        adapter.load_guest_runtime_namespace(
            repository_root=Path("/mnt/aigol"),
            context_path=adapter.GUEST_CONTEXT_PATH,
        )
    assert selected == [Path(F.GUEST_OWNER_PATH)]


def test_duplicate_keys_are_rejected() -> None:
    with pytest.raises(F.JCError, match="DUPLICATE_KEY:owner"):
        json.loads('{"owner":1,"owner":2}', object_pairs_hook=F.unique_object)


def test_nocloud_projection_and_future_semantic_firewall() -> None:
    for member, source in {
        "/user-data": ROOT / F.JC_CLOUD_INIT,
        "/meta-data": ROOT / ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/raw/G77_256FM_CLOUD_INIT_META_DATA_V1.yaml",
        "/network-config": ROOT / ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/raw/G77_256FM_CLOUD_INIT_NETWORK_CONFIG_V1.yaml",
    }.items():
        projected = subprocess.check_output(["isoinfo", "-i", str(ROOT / F.JC_SEED), "-R", "-x", member])
        assert projected == source.read_bytes()
    adapter = (ROOT / F.JC_ADAPTER).read_text(encoding="utf-8")
    assert "EVALUATION_TIME_UNIX_NS = 500" in adapter
    assert "BASELINE_VALID_FROM_UNIX_NS = 100" in adapter
    assert "FUTURE_VALID_FROM_UNIX_NS = 600" in adapter
    assert "VALID_UNTIL_UNIX_NS = 1000" in adapter
    assert "operational Human act is not current" in adapter
    assert "9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547" in adapter


def test_single_route_p11_and_no_shadow_automation_firewall() -> None:
    changed = set(subprocess.check_output(["git", "diff", "--name-only"], cwd=ROOT, text=True).splitlines())
    assert not any(path.startswith("aigol/runtime/") for path in changed)
    assert not any("g77_256ec_p11_operational_v1" in path for path in changed)
    launcher = (ROOT / F.FM_LAUNCHER).read_text(encoding="utf-8")
    assert launcher.count("result = subprocess.run(argv, check=False)") == 1
    assert "automatic owner rebinding" not in launcher.lower()


def test_terminal_is_canonical_sealed_and_operationally_zero() -> None:
    envelope = canonical(TERMINAL)
    reduction = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(F.canonical_bytes(reduction)).hexdigest()
    assert reduction == F.terminal_reduction()
    assert reduction["terminal"] == "A__FUTURE_GUEST_FM_CONTEXT_OWNER_PROJECTION_REPOSITORY_ONLY_RECONCILED_AND_STATICALLY_VERIFIED"
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"] == {"after": "VERIFIED__10_OF_18", "before": "VERIFIED__10_OF_18", "credit": "VERIFIED__0"}
    assert reduction["reuse"]["production_route_delta"] == "VERIFIED__0"
    assert reduction["reuse"]["p11_mutation_count"] == "VERIFIED__0"


def test_ast_json_report_and_index_firewalls() -> None:
    for path in sorted(JC.rglob("*.py")):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    canonical(TERMINAL)
    text = REPORT.read_text(encoding="utf-8")
    assert [line for line in text.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    required = (
        "Reuse Impact Assessment", "CONSTITUTIONAL_HEALTH_EVIDENCE",
        "SHADOW_AUTOMATION_STATUS", "CONSTITUTIONAL_FRONTIER_DISTANCE",
        "CONSTITUTIONAL_FRONTIER_DISTANCe", "GOVERNANCE_EFFICIENCE",
        "COGNITION_ASSISTED_HANDOFF", "AIGOL_CODEX_WORK_SHARE",
        "OVERENGINEERING_RISK", "COGNITION_PROVENANCE", "CANDIDATE_CAPABILITY",
        "SHADOW_DESIGN_TARGET", "CONSTITUTIONAL_CONTINUATION_PROGRESS",
        "PROMPT_CONTEXT_REUSE_RATIO", "CCWIM_MATURITY_LEVEL",
        "Infrastructure Amortization", "Historical Failure Firewall",
    )
    assert all(value in text for value in required)
    assert subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True).strip() == ""
