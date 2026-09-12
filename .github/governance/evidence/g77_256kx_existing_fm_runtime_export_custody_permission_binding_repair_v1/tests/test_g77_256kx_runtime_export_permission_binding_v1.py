from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KX = ROOT / ".github/governance/evidence/g77_256kx_existing_fm_runtime_export_custody_permission_binding_repair_v1"
FORMALIZER = KX / "analysis/G77_256KX_EXISTING_FM_RUNTIME_EXPORT_PERMISSION_BINDING_FORMALIZER_V1.py"
REDUCTION = KX / "G77_256KX_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = KX / "G77_256KX_G48_IMPLEMENTATION_REPORT_V1.md"


def load(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


F = load(FORMALIZER, "g77_256kx_test_formalizer")


def custody_bits(mode: int) -> int:
    return F.permission_bits(
        mode,
        owner_uid=F.HOST_UID,
        owner_gid=F.HOST_GID,
        actor_uid=F.CUSTODY_UID,
        actor_gid=F.CUSTODY_GID,
    )


def test_kw_terminal_authority_attempt_and_failure_are_authenticated() -> None:
    proof = F.authenticate_kw_terminal()
    assert proof["terminal"] == F.KW_TERMINAL_VALUE
    assert proof["authority"]["state"] == (
        "VERIFIED__CONSUMED_EXACTLY_ONCE__NONREUSABLE__NONTRANSFERABLE"
    )
    assert proof["operational_counters"] == {
        "authority_consumption_count": 1,
        "expired_denial_count": 0,
        "fm_operational_invocation_count": 1,
        "operation_attempt_count": 1,
        "operation_request_count": 0,
        "operational_authorization_count": 1,
        "p11_entry_count": 0,
        "pre_operational_invocation_count": 1,
        "protected_effect_count": 0,
        "protected_invocation_count": 0,
        "qemu_start_count": 1,
        "repair_retry_count": 0,
        "replay_count": 0,
        "retry_count": 0,
        "vm_start_count": 1,
    }
    assert proof["commissioning"] == (
        "VERIFIED__P01_THROUGH_P12_PASS_BEFORE_CONTEXT_LOAD_FAILURE"
    )
    assert proof["failure"]["exact_exception_path"] == (
        "/mnt/g77-evidence/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    )


def test_actual_existing_fm_owner_and_mount_are_unique() -> None:
    contract = F.authenticate_owner_and_contract()
    assert contract["actual_owner"].endswith(
        "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py:materialize_operation_state"
    )
    assert contract["mount_semantics"] == (
        "EXISTING_SINGLE_G77_EVIDENCE_9P_EXPORT_TO_/mnt/g77-evidence"
    )
    assert contract["complete_pre_request_traversal_contract"] == [
        "KF_GUEST_HARNESS_ROOT_0701__UNCHANGED",
        "FM_RUNTIME_EXPORT_ROOT_0701__KX_REPAIRED",
    ]
    assert contract["production_route_before"] == 1
    assert contract["production_route_after"] == 1


def test_private_construction_precedes_complete_final_presentation() -> None:
    source = F.LAUNCHER.read_text(encoding="utf-8")
    mkdir_at = source.index("mode=RUNTIME_EXPORT_ROOT_CONSTRUCTION_MODE,")
    manifest_at = source.index("runtime_manifest.write_bytes(candidate.read_bytes())")
    context_at = source.index(
        "context_projection.write_bytes(context_source_path.read_bytes())"
    )
    chmod_at = source.index(
        "runtime_export.chmod(RUNTIME_EXPORT_ROOT_PRESENTATION_MODE)"
    )
    assert mkdir_at < manifest_at < context_at < chmod_at
    assert source.count("def materialize_operation_state(") == 1


def test_posix_permission_contract_is_exact_one_bit_search_only() -> None:
    assert F.PRE_ROOT_MODE ^ F.POST_ROOT_MODE == 0o001
    assert custody_bits(F.PRE_ROOT_MODE) == 0
    assert custody_bits(F.POST_ROOT_MODE) == os.X_OK
    assert not F.permits(custody_bits(F.POST_ROOT_MODE), os.R_OK)
    assert not F.permits(custody_bits(F.POST_ROOT_MODE), os.W_OK)
    context_bits = custody_bits(F.CONTEXT_MODE)
    assert F.permits(context_bits, os.R_OK)
    assert not F.permits(context_bits, os.W_OK)


def test_deterministic_filesystem_modes_match_presentation_contract(tmp_path: Path) -> None:
    runtime_export = tmp_path / "runtime_export"
    runtime_export.mkdir(mode=F.PRE_ROOT_MODE)
    context = runtime_export / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    context.write_bytes(b"{}\n")
    context.chmod(F.CONTEXT_MODE)
    assert stat.S_IMODE(runtime_export.stat().st_mode) == F.PRE_ROOT_MODE
    assert stat.S_IMODE(context.stat().st_mode) == F.CONTEXT_MODE
    runtime_export.chmod(F.POST_ROOT_MODE)
    assert stat.S_IMODE(runtime_export.stat().st_mode) == F.POST_ROOT_MODE
    assert custody_bits(stat.S_IMODE(runtime_export.stat().st_mode)) == os.X_OK
    assert F.permits(custody_bits(stat.S_IMODE(context.stat().st_mode)), os.R_OK)
    assert not F.permits(custody_bits(stat.S_IMODE(context.stat().st_mode)), os.W_OK)


def test_permission_widening_substitutions_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(F, "POST_ROOT_MODE", 0o703)
    with pytest.raises(RuntimeError, match="search-only|one-bit"):
        F.authenticate_owner_and_contract()


def test_kf_p11_authority_and_ex_reuse_remain_unchanged() -> None:
    contract = F.authenticate_owner_and_contract()
    assert contract["kf_repair"] == "VERIFIED__INTACT"
    assert contract["p11_sha256"] == F.P11_SHA256
    assert contract["authority_expansion"] == "ABSENT"
    assert F.authenticate_ex_reuse() == {
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
        "assumption_invalidation_count": 0,
    }


def test_delta_inventory_is_bounded_and_index_empty() -> None:
    delta = F.authenticate_delta()
    assert delta["production_mutation_count"] == 1
    assert delta["new_owner_count"] == 0
    assert delta["new_route_count"] == 0
    assert delta["p11_implementation_mutation_count"] == 0
    assert delta["unrelated_mutation_count"] == 0
    assert subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True
    ).strip() == ""


def test_terminal_reduction_is_canonical_sealed_and_replayable() -> None:
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
    assert reduction["e05"]["kx_credit"] == "VERIFIED__0"


def test_g48_has_exact_required_structure_and_reuse_questions() -> None:
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
    assert report.count("REPOSITORY_ONLY_PROOF != OPERATIONAL_PROOF") == 1
    verdict = report.split("# 6. Certification Verdict\n", 1)[1].strip().splitlines()
    assert verdict == [f"`{F.TERMINAL}`"]
