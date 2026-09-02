#!/usr/bin/env python3
"""Focused repository-only proofs for G77-256HB terminal readiness."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
HB = ROOT / ".github/governance/evidence/g77_256hb_post_ha_live_binding_readiness_v1"
BINDER_PATH = HB / "binding/G77_256HB_POST_HA_LIVE_BINDING_V1.py"
CANDIDATE = HB / "live_binding/candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
RUNTIME = HB / "live_binding/runtime_projection/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
EB_RECEIPT = HB / "live_binding/bindings/G77_256GY_EB_RECEIPT_V1.json"
EE_RECEIPT = HB / "live_binding/bindings/G77_256GY_EE_RECEIPT_V1.json"
CHECKPOINT = HB / "G77_256HB_POST_HA_BINDING_AND_READINESS_CHECKPOINT_V1.json"
NEXT_SPEC = HB / "G77_256HB_NEXT_OPERATION_SPECIFICATION_V1.json"
TERMINAL = HB / "G77_256HB_SPCE_TERMINAL_REDUCTION_V1.json"
REPORT = ROOT / "docs/governance/G77_256HB_POST_HA_LIVE_BINDING_AND_WRONG_INPUT_PREOPERATIONAL_READINESS_CERTIFICATION_V1.md"


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


BINDER = load_module(BINDER_PATH, "g77_256hb_focused_binder")


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"DUPLICATE_JSON_KEY__{key}")
        result[key] = value
    return result


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def load_unique(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_bytes(), object_pairs_hook=unique_object)
    assert isinstance(value, dict)
    assert path.read_bytes() == canonical_bytes(value)
    return value


def assert_sealed(path: Path, inner: str, seal: str) -> dict[str, Any]:
    envelope = load_unique(path)
    assert hashlib.sha256(canonical_bytes(envelope[inner])).hexdigest() == envelope[seal]
    return envelope


def test_exact_committed_ha_and_current_candidate_binding() -> None:
    observed = BINDER.authenticate_committed_ha(ROOT)
    assert observed["head"] == "f7d732edb822163d9fb8da2578ac7e79d3ab5398"
    assert observed["tree"] == "53b1ab0c7de92c7355234a3d99d455a113db74c4"
    assert subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True).strip() == ""
    assert BINDER.canonical_bytes(BINDER.build_post_ha_candidate(ROOT)) == CANDIDATE.read_bytes()
    assert CANDIDATE.read_bytes() == RUNTIME.read_bytes()


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("required_head", "0" * 40),
        ("source_tree", "0" * 40),
    ),
)
def test_exact_rebind_firewall_rejects_head_or_tree_drift(field: str, value: str) -> None:
    reference = BINDER._load_canonical(ROOT / BINDER.GZ_CANDIDATE)
    candidate = BINDER.build_post_ha_candidate(ROOT)
    candidate["manifest"][field] = value
    candidate["manifest_sha256"] = hashlib.sha256(BINDER.canonical_bytes(candidate["manifest"])).hexdigest()
    with pytest.raises(BINDER.PostHABindingError, match="CANDIDATE_SEMANTICS_CHANGED_OUTSIDE_EXPLICIT_HA_REBIND"):
        BINDER.validate_explicit_ha_owner_rebind(reference, candidate)


def test_exact_rebind_firewall_rejects_semantic_or_owner_drift() -> None:
    reference = BINDER._load_canonical(ROOT / BINDER.GZ_CANDIDATE)
    for mutation in ("CASE", "GN", "FM", "EXTRA"):
        candidate = deepcopy(BINDER.build_post_ha_candidate(ROOT))
        if mutation == "CASE":
            candidate["manifest"]["selected_case"]["case_class"] = "E05_NEGATIVE_AUTHORITY_WRONG_ATTEMPT"
        elif mutation == "GN":
            candidate["manifest"]["extension_bindings"][4]["sha256"] = "0" * 64
        elif mutation == "FM":
            candidate["manifest"]["extension_bindings"][5]["sha256"] = "0" * 64
        else:
            candidate["manifest"]["unexpected"] = True
        candidate["manifest_sha256"] = hashlib.sha256(BINDER.canonical_bytes(candidate["manifest"])).hexdigest()
        with pytest.raises(BINDER.PostHABindingError, match="CANDIDATE_SEMANTICS_CHANGED_OUTSIDE_EXPLICIT_HA_REBIND"):
            BINDER.validate_explicit_ha_owner_rebind(reference, candidate)


def test_current_ha_du_eb_ee_reauthenticate() -> None:
    checkpoint = assert_sealed(CHECKPOINT, "checkpoint", "checkpoint_sha256")["checkpoint"]
    assert checkpoint["du_eb_ee"]["current_ha_committed_binding_proof"] is True
    assert (checkpoint["du_eb_ee"]["du_status"], checkpoint["du_eb_ee"]["eb_status"], checkpoint["du_eb_ee"]["ee_status"]) == ("PASS", "PASS", "PASS")
    eb = assert_sealed(EB_RECEIPT, "receipt", "receipt_inner_sha256")["receipt"]
    ee = assert_sealed(EE_RECEIPT, "receipt", "receipt_inner_sha256")["receipt"]
    assert eb["overall_result"] == "PASS"
    assert ee["pre_materialization_runtime_path_binding_result"] == "PASS"
    assert eb["required_head"] == ee["git_binding"]["required_head"] == BINDER.EXPECTED_HEAD
    assert eb["required_tree"] == ee["git_binding"]["required_tree"] == BINDER.EXPECTED_TREE


def test_terminal_branch_a_next_spec_and_zero_operation() -> None:
    reduction = assert_sealed(TERMINAL, "reduction", "reduction_sha256")["reduction"]
    specification = assert_sealed(NEXT_SPEC, "specification", "specification_sha256")["specification"]
    assert reduction["readiness_reduction"]["terminal_branch"] == "BRANCH_A__REPOSITORY_READY"
    assert reduction["readiness_reduction"]["preoperational_readiness_status"] == "VERIFIED"
    assert reduction["readiness_reduction"]["next_operational_generation_eligible"] == "VERIFIED"
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"]["before"] == reduction["e05"]["after"] == "7/18"
    assert specification["execution_authority"] is False
    assert specification["auto_continuable"] is False
    assert specification["future_generation_identity"].startswith("UNASSIGNED")


def test_g48_exact_six_headings_and_terminal_verdict() -> None:
    reduction = load_unique(TERMINAL)["reduction"]
    report = REPORT.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    assert report.rstrip().endswith(reduction["terminal_control"]["verdict"])
    assert report.count("Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?") == 1
    assert report.count("| `PREVIOUS_WORKER_CONVERSATION_REQUIRED` |") == 1
