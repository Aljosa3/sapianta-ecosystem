#!/usr/bin/env python3
"""Focused reconstruction of the G77-256IC preauthorization barrier."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
IC = ROOT / ".github/governance/evidence/g77_256ic_wrong_provenance_operational_v1"
LIVE = IC / "live_binding"
CANDIDATE = LIVE / "candidate/G77_256IB_WRONG_PROVENANCE_CURRENT_CANDIDATE_V1.json"
RUNTIME = LIVE / "runtime_projection/G77_256IB_WRONG_PROVENANCE_CURRENT_CANDIDATE_V1.json"
CONTEXT = LIVE / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
CHECKPOINT = IC / "G77_256IC_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
REQUEST = IC / "G77_256IC_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
PRESENTATION = IC / "G77_256IC_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
GN_PROOF = IC / "G77_256IC_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json"
PREHUMAN = IC / "G77_256IC_PREHUMAN_PHASE_ABC_REDUCTION_V1.json"
VALIDATION = IC / "G77_256IC_PREHUMAN_VALIDATION_AND_BARRIER_ADMISSION_V1.json"
FM_PATH = ROOT / ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
GN_PATH = ROOT / ".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
HEAD = "ec2c4997ba62fbaa5e774fc9ba010f6319926c73"
TREE = "887f329b030582f01a49f6c0c97f54ed4f55a818"
GENERATION = "G77_256IC_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_PROVENANCE_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256IC_E05_WRONG_PROVENANCE_DENIAL_BEFORE_ENTRY_001"


def load_module(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


FM = load_module(FM_PATH, "g77_256ic_test_fm")
GN = load_module(GN_PATH, "g77_256ic_test_gn")


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        assert key not in result, f"duplicate JSON key: {key}"
        result[key] = value
    return result


def load_unique(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    assert isinstance(value, dict)
    assert raw == FM.canonical_bytes(value)
    return value


def verify_envelope(path: Path, inner: str) -> dict[str, Any]:
    envelope = load_unique(path)
    assert envelope[f"{inner}_sha256"] == hashlib.sha256(
        FM.canonical_bytes(envelope[inner])
    ).hexdigest()
    return envelope


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def test_exact_committed_ib_entry_and_nested_authority() -> None:
    assert git("branch", "--show-current") == "g77-256fl-wrong-attempt-preboot-blocker"
    assert git("rev-parse", "HEAD") == HEAD
    assert git("rev-parse", "HEAD^{tree}") == TREE
    assert git("show", "-s", "--format=%s", "HEAD") == "G77-256IB certify WRONG_PROVENANCE preoperational readiness"
    assert git("rev-parse", "origin/g77-256fl-wrong-attempt-preboot-blocker") == HEAD
    assert git("status", "--porcelain", "--untracked-files=no") == ""
    assert git("diff", "--cached", "--name-only") == ""
    nested = ROOT / "sapianta_system"
    assert git("rev-parse", "HEAD", cwd=nested) == "3183bab71f8f30397c0309dd2e6d846d14a11f66"
    assert git("rev-parse", "HEAD^{tree}", cwd=nested) == "7c32ec05efc2be43297849bc38ec8766514a523d"
    assert git("branch", "--show-current", cwd=nested) == ""
    assert git("status", "--porcelain", cwd=nested) == ""


def test_fresh_candidate_runtime_and_context_bind_exact_ic() -> None:
    candidate = load_unique(CANDIDATE)
    assert CANDIDATE.read_bytes() == RUNTIME.read_bytes()
    assert candidate["manifest"]["required_head"] == HEAD
    assert candidate["manifest"]["source_tree"] == TREE
    assert candidate["manifest"]["selected_case"] == {
        "case_class": "E05_NEGATIVE_AUTHORITY_WRONG_PROVENANCE",
        "case_id": "G77_256IB_E05_WRONG_PROVENANCE_DENIAL_BEFORE_ENTRY_001",
    }
    assert candidate["manifest_sha256"] == hashlib.sha256(
        FM.canonical_bytes(candidate["manifest"])
    ).hexdigest()
    context = FM.fresh_context.load_context(CONTEXT, repository_root=ROOT)
    assert context["generation_identity"] == GENERATION
    assert context["operation_identity"] == OPERATION
    assert context["repository_head"] == HEAD
    assert context["repository_tree"] == TREE
    assert context["candidate_manifest_sha256"] == hashlib.sha256(CANDIDATE.read_bytes()).hexdigest()
    assert context["wrapper_fc_er_che_schema_hashes"]["wrapper"] == "e547af9b68f77fda94962abb6031445df5faba9ec43c68f40966473f83db8b23"
    assert context["wrapper_fc_er_che_schema_hashes"]["cloud_init"] == "4725543bab299d1e153b2c40f9fcd0791ce9c2af318e88c41deeba9e6c69ed84"
    assert context["qemu_executable_base_seed_checkout_bindings"]["seed"]["sha256"] == "4154ec58b7ebf46299ccc495a0a1232b7e31f67221f987b6fe7959f8d5593c7c"
    assert context["canonical_argv"].count("-nic") == 1
    assert context["canonical_argv"][context["canonical_argv"].index("-nic") + 1] == "none"


def test_checkpoint_request_and_gn_presentation_are_bound_and_nonauthority() -> None:
    checkpoint = verify_envelope(CHECKPOINT, "checkpoint")["checkpoint"]
    assert checkpoint["authority_boundary"]["authority_state"] == "NOT_GRANTED"
    assert checkpoint["e05"] == {"before": "9/18", "current": "9/18", "maximum_credit": 1}
    assert set(checkpoint["operational_counters"].values()) == {0}
    maxima = checkpoint["one_shot_maxima"]
    assert maxima["authority_consumption"] == maxima["pre"] == 1
    assert maxima["fm_operational_launcher_invocation"] == maxima["qemu"] == 1
    assert maxima["retry"] == maxima["repair_and_continue"] == maxima["operational_replay"] == 0
    semantics = checkpoint["semantic_firewall"]
    assert semantics["independent_mutation_count"] == 1
    assert semantics["independent_mutated_coordinate"] == "provenance_identity"
    assert semantics["dependent_recomputation_count"] == 1
    assert semantics["dependent_recomputed_coordinate"] == "record_identity"
    assert semantics["unrelated_mutation_count"] == 0
    assert semantics["authoritative_provenance"] == "existing protected custody owner-state"
    assert semantics["expected_denial_reason"] == "operational Human act input_record_identity binding is invalid"
    assert semantics["provenance_specific_comparison_reached"] is False
    request = GN.load_validated_sealed_request(REQUEST)
    assert request["request"]["generation_identity"] == GENERATION
    assert request["request"]["operation_identity"] == OPERATION
    assert request["request"]["authorized_vector_requested"] == "WRONG_PROVENANCE"
    assert request["request"]["preauthorization"]["checkpoint_inner_sha256"] == verify_envelope(CHECKPOINT, "checkpoint")["checkpoint_sha256"]
    result = GN.validate_human_authorization_presentation(REQUEST, PRESENTATION.read_bytes())
    assert result["human_presentation_request_equivalence"].startswith("VERIFIED")
    proof = verify_envelope(GN_PROOF, "proof")["proof"]
    assert proof["authority_present"] is False
    assert proof["request_sha256"] == request["request_sha256"]


def test_barrier_has_no_grant_receipt_execution_or_guest_result() -> None:
    reduction = verify_envelope(PREHUMAN, "reduction")["reduction"]
    assert reduction["authority_boundary"]["human_authorization_status"] == "NOT_GRANTED"
    assert reduction["authority_boundary"]["operation_execution_status"] == "NOT_STARTED"
    assert set(reduction["operational_counters"].values()) == {0}
    # After the separately authorized operation, authenticate the preserved
    # pre-grant snapshot rather than requiring the later artifacts to vanish.
    if (IC / "G77_256IC_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt").exists():
        return
    context = load_unique(CONTEXT)
    forbidden = [
        IC / "G77_256IC_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt",
        IC / "G77_256IC_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
        Path(context["pre_receipt_path"]),
        Path(context["post_receipt_path"]),
        Path(context["serial_path"]),
        *(
            Path(context["runtime_export_root"]) / relative
            for relative in context["guest_output_relative_paths"]
        ),
    ]
    assert all(not path.exists() and not path.is_symlink() for path in forbidden)


def test_one_fm_launcher_and_one_qemu_call_site_remain() -> None:
    tree = ast.parse(FM_PATH.read_text(encoding="utf-8"))
    mains = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "main"
    ]
    qemu_calls = [
        node for node in ast.walk(mains[0])
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "subprocess"
        and node.func.attr == "run"
    ]
    assert len(mains) == len(qemu_calls) == 1


def test_all_ic_json_is_unique_key_canonical_and_sealed_where_applicable() -> None:
    for path in sorted(IC.rglob("*.json")):
        load_unique(path)
    for path, inner in (
        (IC / "G77_256IC_PREAUTHORITY_STATIC_READINESS_V1.json", "proof"),
        (IC / "G77_256IC_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1.json", "proof"),
        (CHECKPOINT, "checkpoint"),
        (GN_PROOF, "proof"),
        (PREHUMAN, "reduction"),
    ):
        verify_envelope(path, inner)
    admission = verify_envelope(VALIDATION, "validation")["validation"]
    assert admission["barrier_admission_status"] == "VERIFIED__PRESENT_EXACT_REQUEST_AND_STOP"
    assert admission["authority_state"] == "NOT_GRANTED"
