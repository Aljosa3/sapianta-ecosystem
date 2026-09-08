#!/usr/bin/env python3
"""Focused repository-only checks for the G77-256JH Human barrier."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
JH = ROOT / ".github/governance/evidence/g77_256jh_future_fresh_human_authorized_operational_denial_v1"
MATERIALIZER = JH / "orchestration/G77_256JH_PREAUTHORIZATION_MATERIALIZER_V1.py"
CONTROLLER = JH / "orchestration/G77_256JH_AUTHORITY_CONSUMPTION_CONTROLLER_V1.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


M = load(MATERIALIZER, "g77_256jh_test_materializer")
C = load(CONTROLLER, "g77_256jh_test_controller")


def canonical(path: Path) -> dict:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=M.unique_object)
    assert isinstance(value, dict)
    assert raw == M.canonical_bytes(value)
    return value


def test_exact_jg_entry_nested_authority_and_terminal_reconstruction() -> None:
    entry = M.authenticate_entry(M.HEAD, M.NESTED_HEAD)
    assert (entry["head"], entry["tree"], entry["subject"]) == (
        "7d33c6fb31f90514d590e39d5d410d81ee0f51b0",
        "b020731686b4fe47a6f2d0ec0d850ad293d1bb97",
        "G77-256JG certify FUTURE post-JF live-binding readiness",
    )
    assert entry["local_remote_equality"] == "VERIFIED"
    assert {"IV", "IW", "IX", "IY", "IZ", "JA", "JB", "JC", "JD", "JE", "JF", "JG"} <= set(entry["lineage"])
    assert set(entry["lineage"].values()) == {"VERIFIED"}
    assert entry["nested_authority"]["clean"] is True
    assert entry["nested_authority"]["detached"] is True
    jg = M.reconstruct_jg()
    assert jg["terminal"] == "A__FUTURE_POST_JF_COMMIT_LIVE_BINDING_AND_OPERATIONAL_READINESS_VERIFIED"
    assert jg["inner_seal"] == "VERIFIED"
    assert jg["option_a_authority"] == "VERIFIED__SEALED_CONTEXT_OPERATION_EVIDENCE_ROOT"
    assert jg["ex_reused"] == "VERIFIED__17_OF_17"
    assert jg["ex_reconstructed"] == "VERIFIED__0"


def test_future_binding_namespace_harness_and_no_network() -> None:
    future = M.authenticate_future_semantics()
    assert (future["evaluation"], future["valid_from"], future["valid_until"]) == (500, 600, 1000)
    assert future["payload_digest"] == "sha256:9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547"
    assert future["wall_clock_dependency_count"] == 0
    context = M.FM.fresh_context.load_context(
        JH / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json", repository_root=ROOT
    )
    assert context["repository_head"] == M.HEAD
    assert context["repository_tree"] == M.TREE
    assert context["generation_identity"] == M.GENERATION
    assert context["operation_identity"] == M.OPERATION
    assert context["operation_evidence_root"] == str((JH / "operation_state").resolve())
    assert context["canonical_argv"].count("-nic") == 1
    assert context["canonical_argv"][context["canonical_argv"].index("-nic") + 1] == "none"
    projection = M.FM.fresh_context.validate_sealed_canonical_argv(
        context, validation_repository_root=M.FM.fresh_context.GUEST_REPOSITORY_ROOT
    )
    assert projection["projection_status"] == "EXACT_GUEST_PROJECTION"
    assert {path.name for path in (JH / "operation_state/guest_harness").iterdir()} == {
        "G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py",
        "G77_256JH_FUTURE_VECTOR_ADAPTER_V1.py",
        "sapianta_fresh_operation_context_v1.py",
    }
    eb = canonical(JH / "live_binding/v2_readiness/bindings/G77_256JH_EB_RECEIPT_V2.json")["receipt"]
    ee = canonical(JH / "live_binding/v2_readiness/bindings/G77_256JH_EE_RECEIPT_V2.json")["receipt"]
    assert eb["certification_baseline"] == {"head": M.HEAD, "tree": M.TREE}
    assert (eb["runtime_target_selection_binding"]["head"], eb["runtime_target_selection_binding"]["tree"]) == (M.IF_HEAD, M.IF_TREE)
    assert ee["certification_baseline"] == eb["certification_baseline"]
    assert ee["runtime_target_selection_binding"] == eb["runtime_target_selection_binding"]


def test_gn_gl_exact_identities_and_zero_operational_boundary() -> None:
    request_path = JH / "G77_256JH_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
    presentation_path = JH / "G77_256JH_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
    request = canonical(request_path)
    checkpoint = canonical(JH / "G77_256JH_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json")
    reduction = canonical(JH / "G77_256JH_PREHUMAN_PHASE_A_REDUCTION_V1.json")["reduction"]
    result = M.GN.validate_human_authorization_presentation(request_path, presentation_path.read_bytes())
    assert result["human_presentation_request_equivalence"] == "VERIFIED_WITHIN_EXACT_REVIEWED_AUTHORIZATION_BINDING_BOUNDARY"
    equivalence = canonical(JH / "G77_256JH_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1.json")["proof"]
    assert equivalence["preauth_final_admission_equivalence"] == "VERIFIED_WITHIN_EXACT_REVIEWED_RECEIPT_PARENT_BOUNDARY"
    assert request["request_sha256"] == C.REQUEST_SHA256
    assert checkpoint["checkpoint_sha256"] == reduction["identities"]["checkpoint_sha256"]
    assert hashlib.sha256(presentation_path.read_bytes()).hexdigest() == reduction["identities"]["presentation_sha256"]
    assert reduction["terminal"] == "HUMAN_AUTHORIZATION_REQUIRED"
    assert reduction["operational_counters"]["authorization_presentation"] == 1
    assert all(value == 0 for key, value in reduction["operational_counters"].items() if key != "authorization_presentation")


def test_consumption_compatibility_is_static_and_authority_state_is_clean() -> None:
    expected = (
        "I explicitly authorize G77-256JH request " + C.REQUEST_SHA256
        + " for operation " + C.OPERATION + ", candidate " + C.CANDIDATE_SHA256
        + ", context " + C.CONTEXT_SHA256 + ", and canonical argv " + C.ARGV_SHA256
        + ", starting from E05 10/18, subject to exactly one authority consumption, "
          "PRE, FM invocation, no-network QEMU, VM boot, and operation attempt, "
          "with zero retry, repair, replay, or protected effect.\n"
    )
    assert C.EXPECTED_NORMALIZED_GRANT == expected
    for name in (
        "G77_256JH_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt",
        "G77_256JH_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
        "G77_256JH_POSTGRANT_PRECONSUMPTION_SAFE_STOP_CHECKPOINT_V1.json",
        "G77_256JH_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json",
    ):
        assert not (JH / name).exists()
    for source_path in (MATERIALIZER, CONTROLLER):
        source = source_path.read_text(encoding="utf-8")
        ast.parse(source, filename=str(source_path))
        assert "FM.main(" not in source
        assert "subprocess.run(argv" not in source
    assert subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True).strip() == ""
    assert subprocess.check_output(["git", "diff", "--name-only", M.HEAD], cwd=ROOT, text=True).strip() == ""
