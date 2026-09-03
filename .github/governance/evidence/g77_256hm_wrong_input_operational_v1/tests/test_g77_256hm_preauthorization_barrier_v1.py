#!/usr/bin/env python3
"""Focused reconstruction of the G77-256HM Human authorization barrier."""

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
HM = ROOT / ".github/governance/evidence/g77_256hm_wrong_input_operational_v1"
LIVE = HM / "live_binding"
CANDIDATE = LIVE / "candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
RUNTIME = LIVE / "runtime_projection/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
CONTEXT = LIVE / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
EB = LIVE / "bindings/G77_256GY_EB_RECEIPT_V1.json"
EE = LIVE / "bindings/G77_256GY_EE_RECEIPT_V1.json"
STATIC = HM / "G77_256HM_PREAUTHORITY_STATIC_READINESS_V1.json"
GL_OBSERVATION = HM / "G77_256HM_GL_RECEIPT_PARENT_OBSERVATION_V1.json"
GL_EQUIVALENCE = HM / "G77_256HM_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1.json"
CHECKPOINT = HM / "G77_256HM_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
REQUEST = HM / "G77_256HM_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
PRESENTATION = HM / "G77_256HM_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
GN_EQUIVALENCE = HM / "G77_256HM_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json"
PREHUMAN = HM / "G77_256HM_PREHUMAN_PHASE_ABCDEFG_REDUCTION_V1.json"
GRANT_SOURCE = HM / "G77_256HM_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
POSTGRANT_SAFE_STOP = HM / "G77_256HM_POSTGRANT_PRECONSUMPTION_CAPACITY_SAFE_STOP_CHECKPOINT_V1.json"
FM_PATH = ROOT / ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
GL_PATH = ROOT / ".github/governance/evidence/g77_256gl_receipt_parent_equivalence_v1/orchestration/G77_256GL_RECEIPT_PARENT_PREAUTHORIZATION_BINDING_V1.py"
GN_PATH = ROOT / ".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
GY_PATH = ROOT / ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/binding/G77_256GY_WRONG_INPUT_POST_COMMIT_BINDING_V1.py"
HEAD = "45495c09edf55cc201e3d146ea77e713f579166b"
TREE = "37ba96de335ee91851ff682f8cd97cf4e49ab5f5"
GENERATION = "G77_256HM_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256HM_E05_WRONG_INPUT_DENIAL_BEFORE_ENTRY_001"


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


FM = load_module(FM_PATH, "g77_256hm_test_fm")
GL = load_module(GL_PATH, "g77_256hm_test_gl")
GN = load_module(GN_PATH, "g77_256hm_test_gn")
GY = load_module(GY_PATH, "g77_256hm_test_gy")


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        assert key not in value, f"duplicate JSON key: {key}"
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


def verify_envelope(path: Path, inner: str) -> dict[str, Any]:
    envelope = load_unique(path)
    seal = f"{inner}_sha256"
    assert envelope[seal] == hashlib.sha256(
        FM.canonical_bytes(envelope[inner])
    ).hexdigest()
    return envelope


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def test_exact_hl_entry_and_nested_authority_reconstruct() -> None:
    assert git("branch", "--show-current") == "g77-256fl-wrong-attempt-preboot-blocker"
    assert git("rev-parse", "HEAD") == HEAD
    assert git("rev-parse", "HEAD^{tree}") == TREE
    assert git("log", "-1", "--format=%s") == "G77-256HL certify WRONG_INPUT preoperational readiness"
    assert git("rev-parse", "origin/g77-256fl-wrong-attempt-preboot-blocker") == HEAD
    assert git("diff", "--cached", "--name-only") == ""
    assert git("status", "--porcelain", "--untracked-files=no") == ""
    nested = ROOT / "sapianta_system"
    assert git("rev-parse", "HEAD", cwd=nested) == "3183bab71f8f30397c0309dd2e6d846d14a11f66"
    assert git("rev-parse", "HEAD^{tree}", cwd=nested) == "7c32ec05efc2be43297849bc38ec8766514a523d"
    assert git("branch", "--show-current", cwd=nested) == ""
    assert git("status", "--porcelain", cwd=nested) == ""


def test_current_hm_candidate_runtime_du_eb_ee_and_semantics() -> None:
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
    du = load_module(ROOT / GY.DU_PATH, "g77_256hm_test_du")
    eb = load_module(ROOT / GY.EB_PATH, "g77_256hm_test_eb")
    ee = load_module(ROOT / GY.EE_PATH, "g77_256hm_test_ee")
    assert set(du.validate_file(CANDIDATE, ROOT, expected_head=HEAD).values()) == {"PASS"}
    assert eb.verify_receipt_file(ROOT, EB)["overall_result"] == "PASS"
    assert ee.verify_receipt_file(ROOT, EE)["pre_materialization_runtime_path_binding_result"] == "PASS"


def test_fm_context_static_admission_and_no_network_route() -> None:
    context = FM.fresh_context.load_context(CONTEXT, repository_root=ROOT)
    assert context["generation_identity"] == GENERATION
    assert context["operation_identity"] == OPERATION
    assert context["repository_head"] == HEAD
    assert context["repository_tree"] == TREE
    assert context["candidate_manifest_sha256"] == sha256(CANDIDATE)
    assert context["guest_adapter_binding"]["source_path"].endswith(
        "G77_256HA_WRONG_INPUT_VECTOR_ADAPTER_V1.py"
    )
    assert context["canonical_argv"].count("-nic") == 1
    nic = context["canonical_argv"].index("-nic")
    assert context["canonical_argv"][nic + 1] == "none"
    observations = FM.observe_context_assets(ROOT, context, CANDIDATE.relative_to(ROOT))
    result = FM.authority_free_static_readiness(
        repository_root=ROOT,
        context=context,
        observed_head=HEAD,
        observed_tree=TREE,
        repository_clean=True,
        observed_asset_sha256=observations,
        candidate_source_path=CANDIDATE.relative_to(ROOT),
    )
    assert result["result"] == "STATIC_READINESS_PASS"
    assert result["human_operational_authorization_count"] == 0
    assert result["qemu_execution_count"] == 0


def test_gl_checkpoint_request_and_gn_presentation_are_exactly_bound() -> None:
    context = load_unique(CONTEXT)
    claim = load_unique(GL_OBSERVATION)
    GL.validate_bound_observation(ROOT, context, claim)
    gl_checkpoint = GL.reduce_preauthorization_checkpoint(ROOT, context, claim)
    observed = GL.validate_preauth_final_admission_equivalence(
        ROOT, context, claim, gl_checkpoint
    )
    persisted = verify_envelope(GL_EQUIVALENCE, "proof")["proof"]
    assert persisted["preauth_final_admission_equivalence"] == observed[
        "preauth_final_admission_equivalence"
    ]
    checkpoint = verify_envelope(CHECKPOINT, "checkpoint")
    request = GN.load_validated_sealed_request(REQUEST)
    preauth = request["request"]["preauthorization"]
    assert preauth["checkpoint_file_sha256"] == sha256(CHECKPOINT)
    assert preauth["checkpoint_inner_sha256"] == checkpoint["checkpoint_sha256"]
    assert request["request"]["authorized_vector_requested"] == "WRONG_INPUT"
    result = GN.validate_human_authorization_presentation(
        REQUEST, PRESENTATION.read_bytes()
    )
    proof = verify_envelope(GN_EQUIVALENCE, "proof")["proof"]
    assert result["request_sha256"] == proof["request_sha256"]
    assert result["presentation_sha256"] == proof["presentation_sha256"]


def test_human_barrier_has_zero_operational_counters_and_no_authority() -> None:
    checkpoint = verify_envelope(CHECKPOINT, "checkpoint")["checkpoint"]
    assert checkpoint["handoff_sufficiency"]["handoff_sufficiency_status"] == "VERIFIED"
    assert checkpoint["preauthorization"]["pre_authorization_static_admission_status"] == "VERIFIED"
    assert set(checkpoint["operational_counters"].values()) == {0}
    reduction = verify_envelope(PREHUMAN, "reduction")["reduction"]
    assert reduction["authority_boundary"]["human_authorization_status"] == "NOT_GRANTED"
    assert reduction["authority_boundary"]["operation_execution_status"] == "NOT_STARTED"
    assert set(reduction["operational_counters"].values()) == {0}
    context = load_unique(CONTEXT)
    forbidden = [
        HM / "G77_256HM_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
        Path(context["pre_receipt_path"]),
        Path(context["post_receipt_path"]),
        Path(context["serial_path"]),
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


def test_all_hm_json_is_unique_key_canonical() -> None:
    paths = sorted(HM.rglob("*.json"))
    assert paths
    for path in paths:
        load_unique(path)
    verify_envelope(STATIC, "proof")
    verify_envelope(CHECKPOINT, "checkpoint")
    verify_envelope(GN_EQUIVALENCE, "proof")
    verify_envelope(PREHUMAN, "reduction")


def test_exact_grant_is_preserved_but_unconsumed_at_capacity_safe_stop() -> None:
    assert sha256(GRANT_SOURCE) == "e21c8ea41df3c0bcc37bb5d80b64a8a648ac2725fdab9712ab0086cf097ac4b5"
    checkpoint = verify_envelope(POSTGRANT_SAFE_STOP, "checkpoint")["checkpoint"]
    grant = checkpoint["grant_authentication"]
    assert grant["human_grant_binding_status"] == "VERIFIED"
    assert grant["sealed_authorization_request_sha256"] == "fa99566594f5efba7eb1c428a8551e74514f32797ee93343778f39b8a94749b6"
    assert grant["authority_consumed"] is False
    assert grant["execution_authority_handoff_created"] is False
    assert checkpoint["provider_capacity"]["decision"] == "SAFE_STOP_BEFORE_AUTHORITY_CONSUMPTION"
    assert checkpoint["provider_capacity"]["telemetry_read_status"] == "FAILED__SERVICE_404_NOT_FOUND"
    counters = checkpoint["operational_counters"]
    assert counters["human_operational_authority"] == 1
    assert set(
        value for key, value in counters.items()
        if key != "human_operational_authority"
    ) == {0}
