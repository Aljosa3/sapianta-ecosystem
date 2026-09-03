#!/usr/bin/env python3
"""Focused proof for the G77-256HF preauthorization Human barrier."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
HF = ROOT / ".github/governance/evidence/g77_256hf_wrong_input_operational_v1"
LIVE = HF / "live_binding"
CANDIDATE = LIVE / "candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
RUNTIME = LIVE / "runtime_projection/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
CONTEXT = LIVE / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
EB = LIVE / "bindings/G77_256GY_EB_RECEIPT_V1.json"
EE = LIVE / "bindings/G77_256GY_EE_RECEIPT_V1.json"
FM_PATH = ROOT / ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
GL_PATH = ROOT / ".github/governance/evidence/g77_256gl_receipt_parent_equivalence_v1/orchestration/G77_256GL_RECEIPT_PARENT_PREAUTHORIZATION_BINDING_V1.py"
GN_PATH = ROOT / ".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
HEAD = "161f3eedff5398b8fac2eafb828344058427fc63"
TREE = "b53580d7af9d01cd56ddcc37d240664addecad32"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
GENERATION = "G77_256HF_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256HF_E05_WRONG_INPUT_DENIAL_BEFORE_ENTRY_001"


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


FM = load_module(FM_PATH, "g77_256hf_test_existing_fm")
GL = load_module(GL_PATH, "g77_256hf_test_existing_gl")
GN = load_module(GN_PATH, "g77_256hf_test_existing_gn")


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"DUPLICATE_JSON_KEY__{key}")
        value[key] = item
    return value


def load_unique(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    assert isinstance(value, dict)
    assert raw == FM.canonical_bytes(value)
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_envelope(path: Path, inner: str, seal: str) -> dict[str, Any]:
    envelope = load_unique(path)
    assert envelope[seal] == hashlib.sha256(
        FM.canonical_bytes(envelope[inner])
    ).hexdigest()
    return envelope


def test_exact_he_entry_and_nested_authority_are_authenticated() -> None:
    assert git("rev-parse", "HEAD") == HEAD
    assert git("rev-parse", "HEAD^{tree}") == TREE
    assert git("branch", "--show-current") == BRANCH
    assert git("status", "--porcelain", "--untracked-files=no") == ""
    assert git("diff", "--cached", "--name-only") == ""
    nested = ROOT / "sapianta_system"
    assert git("rev-parse", "HEAD", cwd=nested) == "3183bab71f8f30397c0309dd2e6d846d14a11f66"
    assert git("rev-parse", "HEAD^{tree}", cwd=nested) == "7c32ec05efc2be43297849bc38ec8766514a523d"
    assert git("status", "--porcelain", cwd=nested) == ""
    assert git("show-ref", "--verify", "refs/tags/sapianta-system-nested-authority-3183bab-v1", cwd=nested).split()[0] == "3183bab71f8f30397c0309dd2e6d846d14a11f66"


def test_current_live_binding_is_exact_he_bound_du_eb_ee_pass() -> None:
    candidate = load_unique(CANDIDATE)
    assert CANDIDATE.read_bytes() == RUNTIME.read_bytes()
    assert candidate["manifest"]["required_head"] == HEAD
    assert candidate["manifest"]["source_tree"] == TREE
    assert candidate["manifest"]["selected_case"] == {
        "case_class": "E05_NEGATIVE_AUTHORITY_WRONG_INPUT",
        "case_id": "G77_256GY_E05_WRONG_INPUT_DENIAL_BEFORE_ENTRY_001",
    }
    assert candidate["manifest_sha256"] == hashlib.sha256(
        FM.canonical_bytes(candidate["manifest"])
    ).hexdigest()
    gy = load_module(
        ROOT / ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/binding/G77_256GY_WRONG_INPUT_POST_COMMIT_BINDING_V1.py",
        "g77_256hf_test_gy",
    )
    du = load_module(ROOT / gy.DU_PATH, "g77_256hf_test_du")
    eb = load_module(ROOT / gy.EB_PATH, "g77_256hf_test_eb")
    ee = load_module(ROOT / gy.EE_PATH, "g77_256hf_test_ee")
    assert set(du.validate_file(CANDIDATE, ROOT, expected_head=HEAD).values()) == {"PASS"}
    assert eb.verify_receipt_file(ROOT, EB)["overall_result"] == "PASS"
    assert ee.verify_receipt_file(ROOT, EE)["pre_materialization_runtime_path_binding_result"] == "PASS"


def test_hf_context_materialization_and_hd_owner_binding_are_ready() -> None:
    context = FM.fresh_context.load_context(CONTEXT, repository_root=ROOT)
    assert context["repository_head"] == HEAD
    assert context["repository_tree"] == TREE
    assert context["generation_identity"] == GENERATION
    assert context["operation_identity"] == OPERATION
    assert context["candidate_manifest_sha256"] == sha256(CANDIDATE)
    assert context["authorization_binding_policy"]["network_authorized"] is False
    assert context["authorization_binding_policy"]["retry_limit"] == 0
    owner = FM.prove_guest_fresh_operation_context_owner_binding(ROOT, context)
    assert owner["result"] == "PREAUTH_GUEST_FM_CONTEXT_OWNER_BINDING_PASS"
    assert owner["host_checkout_guest_byte_identity"] == "PASS"
    assert owner["host_checkout_guest_hash_identity"] == "PASS"
    observations = FM.observe_context_assets(ROOT, context, CANDIDATE.relative_to(ROOT))
    readiness = FM.authority_free_static_readiness(
        repository_root=ROOT,
        context=context,
        observed_head=HEAD,
        observed_tree=TREE,
        repository_clean=True,
        observed_asset_sha256=observations,
        candidate_source_path=CANDIDATE.relative_to(ROOT),
    )
    assert readiness["result"] == "STATIC_READINESS_PASS"
    assert readiness["human_operational_authorization_count"] == 0
    assert readiness["qemu_execution_count"] == 0


def test_sealed_static_readiness_and_gl_equivalence_reauthenticate() -> None:
    static = verify_envelope(
        HF / "G77_256HF_PREAUTHORITY_STATIC_READINESS_V1.json",
        "proof", "proof_sha256",
    )["proof"]
    assert static["readiness"]["result"] == "STATIC_READINESS_PASS"
    assert static["human_constitutional_authorization_count"] == 0
    context = load_unique(CONTEXT)
    claim = load_unique(HF / "G77_256HF_GL_RECEIPT_PARENT_OBSERVATION_V1.json")
    GL.validate_bound_observation(ROOT, context, claim)
    gl_checkpoint = GL.reduce_preauthorization_checkpoint(ROOT, context, claim)
    observed = GL.validate_preauth_final_admission_equivalence(
        ROOT, context, claim, gl_checkpoint
    )
    persisted = verify_envelope(
        HF / "G77_256HF_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1.json",
        "proof", "proof_sha256",
    )["proof"]
    assert persisted["preauth_final_admission_equivalence"] == observed[
        "preauth_final_admission_equivalence"
    ]
    assert persisted["receipt_parent_observation_sha256"] == claim[
        "observation_sha256"
    ]


def test_checkpoint_request_and_gn_presentation_are_exactly_bound() -> None:
    checkpoint_path = HF / "G77_256HF_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
    checkpoint = verify_envelope(checkpoint_path, "checkpoint", "checkpoint_sha256")
    request_path = HF / "G77_256HF_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
    request = GN.load_validated_sealed_request(request_path)
    assert request["request"]["preauthorization"]["checkpoint_file_sha256"] == sha256(checkpoint_path)
    assert request["request"]["preauthorization"]["checkpoint_inner_sha256"] == checkpoint["checkpoint_sha256"]
    assert request["request"]["authorized_vector_requested"] == "WRONG_INPUT"
    presentation_path = HF / "G77_256HF_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
    result = GN.validate_human_authorization_presentation(
        request_path, presentation_path.read_bytes()
    )
    assert result["human_presentation_request_equivalence"] == "VERIFIED_WITHIN_EXACT_REVIEWED_AUTHORIZATION_BINDING_BOUNDARY"
    proof = verify_envelope(
        HF / "G77_256HF_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json",
        "proof", "proof_sha256",
    )["proof"]
    assert proof["request_sha256"] == request["request_sha256"]
    assert proof["presentation_sha256"] == result["presentation_sha256"]


def test_handoff_is_complete_but_human_authority_and_operation_are_absent() -> None:
    checkpoint = verify_envelope(
        HF / "G77_256HF_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json",
        "checkpoint", "checkpoint_sha256",
    )["checkpoint"]
    handoff = checkpoint["handoff_sufficiency"]
    assert handoff["handoff_sufficiency_status"] == "SUFFICIENT"
    assert handoff["handoff_state_completeness"] == "COMPLETE"
    assert handoff["handoff_ambiguity_count"] == 0
    assert handoff["unauthenticated_handoff_assumption_count"] == 0
    assert set(checkpoint["operational_counters"].values()) == {0}
    prehuman = verify_envelope(
        HF / "G77_256HF_PREHUMAN_PHASE_ABCDE_REDUCTION_V1.json",
        "reduction", "reduction_sha256",
    )["reduction"]
    assert prehuman["handoff_sufficiency"]["authorization_request_count"] == 1
    assert prehuman["authority_boundary"] == {
        "auto_continuable": False,
        "checkpoint_is_authority": False,
        "human_authorization_required": "YES",
        "human_authorization_status": "NOT_GRANTED",
        "human_review_required": True,
        "next_legal_action": "PRESENT_EXACT_GN_DETERMINISTIC_TEXT_AND_STOP_FOR_ONE_HUMAN_DECISION",
        "operation_execution_status": "NOT_STARTED",
        "provider_capacity_is_authority": False,
        "request_is_authority": False,
        "authority_disposition": "NONE",
    }
    assert set(prehuman["operational_counters"].values()) == {0}
    context = load_unique(CONTEXT)
    forbidden = [
        HF / "G77_256HF_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
        Path(context["pre_receipt_path"]), Path(context["post_receipt_path"]),
        Path(context["serial_path"]),
    ]
    assert all(not path.exists() and not path.is_symlink() for path in forbidden)


def test_single_route_and_wrong_input_semantic_firewall_are_preserved() -> None:
    tree = ast.parse(FM_PATH.read_text(encoding="utf-8"))
    mains = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main"]
    qemu_calls = [
        node for node in ast.walk(mains[0])
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "subprocess"
        and node.func.attr == "run"
    ]
    assert len(mains) == len(qemu_calls) == 1
    assert "input_identity" not in FM_PATH.read_text(encoding="utf-8")
    context = load_unique(CONTEXT)
    assert context["guest_adapter_binding"]["source_path"].endswith(
        "G77_256HA_WRONG_INPUT_VECTOR_ADAPTER_V1.py"
    )
    assert context["canonical_argv"].count("-nic") == 1
    index = context["canonical_argv"].index("-nic")
    assert context["canonical_argv"][index + 1] == "none"


def test_all_hf_json_is_unique_key_canonical_and_validation_is_sealed() -> None:
    paths = sorted(HF.rglob("*.json"))
    assert paths
    for path in paths:
        load_unique(path)
    validation = verify_envelope(
        HF / "G77_256HF_PREAUTHORIZATION_VALIDATION_V1.json",
        "validation", "validation_sha256",
    )["validation"]
    assert validation["hf_focused"] == "PASS__8_OF_8"
    assert validation["git_diff_check"] == "PASS"
    assert validation["human_operational_authority_count"] == 0
    assert validation["qemu_execution_count"] == 0


def test_postgrant_capacity_safe_stop_preserves_unconsumed_authority() -> None:
    source = HF / "G77_256HF_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
    assert sha256(source) == "af185e2ff2e53596500c7720f42e566b7a1b177a74081db1665283d348c01cdc"
    checkpoint = verify_envelope(
        HF / "G77_256HF_POSTGRANT_PRECONSUMPTION_CAPACITY_SAFE_STOP_CHECKPOINT_V1.json",
        "checkpoint", "checkpoint_sha256",
    )["checkpoint"]
    assert checkpoint["grant_authentication"]["human_grant_binding_status"] == "VERIFIED"
    assert checkpoint["grant_authentication"]["authority_consumed"] is False
    assert checkpoint["grant_authentication"]["execution_authority_handoff_created"] is False
    assert checkpoint["provider_capacity"]["primary_remaining_percent"] == 27
    assert checkpoint["provider_capacity"]["decision"] == "SAFE_STOP_BEFORE_AUTHORITY_CONSUMPTION"
    counters = checkpoint["operational_counters"]
    assert counters["human_operational_authority"] == 1
    assert set(value for key, value in counters.items() if key != "human_operational_authority") == {0}
