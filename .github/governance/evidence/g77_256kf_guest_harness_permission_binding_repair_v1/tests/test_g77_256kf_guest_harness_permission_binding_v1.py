from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KF = ROOT / ".github/governance/evidence/g77_256kf_guest_harness_permission_binding_repair_v1"
FORMALIZER = KF / "analysis/G77_256KF_GUEST_HARNESS_PERMISSION_BINDING_FORMALIZER_V1.py"
REDUCTION = KF / "G77_256KF_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = KF / "G77_256KF_G48_IMPLEMENTATION_REPORT_V1.md"


def load(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


F = load(FORMALIZER, "g77_256kf_test_formalizer")


def custody_bits(mode: int) -> int:
    return F.permission_bits(
        mode,
        owner_uid=F.HOST_UID,
        owner_gid=F.HOST_GID,
        actor_uid=F.CUSTODY_UID,
        actor_gid=F.CUSTODY_GID,
    )


def test_interrupted_delta_is_exact_bounded_kf_continuation() -> None:
    proof = F.authenticate_delta()
    assert proof["interrupted_delta_reconstruction"].startswith("VERIFIED__")
    assert proof["interrupted_launcher_delta"] == "VERIFIED__14_INSERTIONS_1_DELETION"
    assert proof["interrupted_formalizer_line_count"] == 521
    assert proof["unrelated_or_unexplained_mutation_count"] == 0
    assert all(proof[key] is True for key in (
        "minimum", "owner_correct", "no_bypass", "no_new_route", "no_new_owner",
        "no_unnecessary_permission_expansion",
    ))


def test_committed_ke_terminal_blocker_and_authority_are_immutable() -> None:
    proof = F.authenticate_ke_terminal()
    assert proof["terminal"] == (
        "M__KE_AUTHORIZED_EXPIRED_OPERATION_FAILED_AT_GUEST_CUSTODY_IMPORT_BEFORE_OPERATION_REQUEST"
    )
    assert proof["exact_exception"] == (
        "PermissionError: [Errno 13] Permission denied: "
        "/mnt/dp-harness/sapianta_fresh_operation_context_v1.py"
    )
    assert proof["blocker"]["host_projection_root_mode"] == "0700"
    assert proof["blocker"]["guest_custody_uid"] == 3
    assert proof["blocker"]["guest_custody_gid"] == 3
    assert proof["authority"]["state"] == (
        "VERIFIED__CONSUMED_EXACTLY_ONCE__NONREUSABLE__NONTRANSFERABLE"
    )
    assert set(proof["terminality"].values()) == {False}


def test_pre_repair_denies_first_parent_traversal_predicate() -> None:
    assert custody_bits(F.PRE_ROOT_MODE) == 0
    assert not F.permits(custody_bits(F.PRE_ROOT_MODE), os.X_OK)
    assert F.permits(custody_bits(F.CONTEXT_OWNER_MODE), os.R_OK)
    assert not F.permits(custody_bits(F.CONTEXT_OWNER_MODE), os.W_OK)
    assert not F.permits(custody_bits(F.CONTEXT_OWNER_MODE), os.X_OK)


def test_post_repair_is_exact_one_bit_search_only_binding() -> None:
    contract = F.authenticate_owner_and_contract()
    assert F.PRE_ROOT_MODE ^ F.POST_ROOT_MODE == 0o001
    assert custody_bits(F.POST_ROOT_MODE) == os.X_OK
    assert F.permits(custody_bits(F.POST_ROOT_MODE), os.X_OK)
    assert not F.permits(custody_bits(F.POST_ROOT_MODE), os.R_OK)
    assert not F.permits(custody_bits(F.POST_ROOT_MODE), os.W_OK)
    assert contract["minimum_permission_delta"] == (
        "VERIFIED__ONE_BIT__OTHER_EXECUTE__0700_TO_0701"
    )
    assert contract["first_failed_permission_predicate"] == (
        "VERIFIED__PARENT_DIRECTORY_SEARCH_TRAVERSAL"
    )


def test_source_loading_is_importlib_not_direct_execution() -> None:
    tree = ast.parse(F.KE_ADAPTER.read_text(encoding="utf-8"))
    attributes = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    assert {"spec_from_file_location", "module_from_spec", "exec_module"} <= attributes
    assert F.authenticate_owner_and_contract()["file_execute_permission_required"] is False
    assert F.authenticate_owner_and_contract()["committed_source_git_modes"] == {
        "adapter": "100644", "context_owner": "100644",
    }


def test_owner_private_construction_precedes_final_presentation() -> None:
    source = F.LAUNCHER.read_text(encoding="utf-8")
    mkdir_at = source.index("mode=GUEST_HARNESS_PROJECTION_ROOT_CONSTRUCTION_MODE,")
    adapter_at = source.index('Path(adapter_binding["projected_path"]).write_bytes(adapter_bytes)')
    context_at = source.index(
        "context_owner_projection.write_bytes(context_owner_source.read_bytes())"
    )
    chmod_at = source.index("adapter_projection_root.chmod(")
    assert mkdir_at < adapter_at < context_at < chmod_at
    assert source.count("def materialize_operation_state(") == 1


def test_permission_widening_substitutions_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(F, "POST_ROOT_MODE", 0o703)
    with pytest.raises(RuntimeError, match="search-only|one-bit"):
        F.authenticate_owner_and_contract()


def test_read_only_projection_p11_identity_and_one_route_are_preserved() -> None:
    contract = F.authenticate_owner_and_contract()
    assert contract["read_only_projection"] == "VERIFIED__PRESERVED"
    assert contract["negative_permission_regressions"]["guest_projection_write"] == (
        "DENIED__READ_ONLY_MOUNT"
    )
    assert contract["p11_sha256"] == F.P11_SHA256
    assert contract["production_route_before"] == 1
    assert contract["production_route_after"] == 1


def test_ex_common_proof_reuse_assumptions_remain_valid() -> None:
    proof = F.authenticate_ex_reuse()
    assert proof["ex_reused"] == "VERIFIED__17_OF_17"
    assert proof["ex_reconstructed"] == "VERIFIED__0"
    assert proof["assumption_invalidation_count"] == 0


def test_terminal_reduction_is_canonical_sealed_and_replayable() -> None:
    raw = REDUCTION.read_bytes()
    envelope = json.loads(raw)
    assert raw == F.canonical_bytes(envelope)
    reduction = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(
        F.canonical_bytes(reduction)
    ).hexdigest()
    assert reduction == F.build_reduction(F.HEAD, F.NESTED_HEAD)
    assert set(reduction["operational_counters"].values()) == {0}
    assert set(reduction["recovery_operational_counters"].values()) == {0}


def test_g48_ria_and_empty_index() -> None:
    report = REPORT.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
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
    assert all(report.count(question) == 1 for question in questions)
    section_six = report.split("# 6. Certification Verdict\n", 1)[1].strip().splitlines()
    assert section_six == ["`A__GUEST_HARNESS_PERMISSION_BINDING_REPOSITORY_VERIFIED`"]
    assert subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True
    ).strip() == ""
