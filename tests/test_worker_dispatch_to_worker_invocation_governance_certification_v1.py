"""Certification checks for AIGOL_WORKER_DISPATCH_TO_WORKER_INVOCATION_GOVERNANCE_CERTIFICATION_V1."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CERTIFICATION = (
    ROOT
    / ".github/governance/finalize/AIGOL_WORKER_DISPATCH_TO_WORKER_INVOCATION_GOVERNANCE_CERTIFICATION_V1.json"
)


def _load() -> dict:
    return json.loads(CERTIFICATION.read_text(encoding="utf-8"))


def test_worker_dispatch_to_invocation_governance_certification_flags_are_true() -> None:
    certification = _load()
    outputs = certification["certified_outputs"]

    assert certification["artifact_type"] == "AIGOL_WORKER_DISPATCH_TO_WORKER_INVOCATION_GOVERNANCE_CERTIFICATION_V1"
    assert certification["certification_status"] == "CERTIFIED"
    assert outputs["WORKER_INVOCATION_CANDIDATE_GENERATED"] is True
    assert outputs["REPLAY_LINEAGE_PRESERVED"] is True
    assert outputs["HUMAN_APPROVAL_REQUIRED"] is True
    assert outputs["INVOCATION_PREVENTED"] is True
    assert outputs["EXECUTION_PREVENTED"] is True
    assert outputs["CODE_MODIFICATION_PREVENTED"] is True
    assert outputs["CERTIFICATION_STATUS"] == "CERTIFIED"
    assert outputs["READY_FOR_WORKER_EXECUTION_GOVERNANCE"] is True


def test_worker_dispatch_to_invocation_governance_certification_preserves_no_execution_boundary() -> None:
    certification = _load()
    constraints = certification["governance_constraints"]
    guarantees = certification["boundary_guarantees"]

    assert constraints["explicit_human_approval_required"] is True
    assert constraints["worker_invocation_allowed"] is False
    assert constraints["implementation_execution_allowed"] is False
    assert constraints["code_modification_allowed"] is False
    assert constraints["governance_modification_allowed"] is False
    assert guarantees["worker_invoked"] is False
    assert guarantees["implementation_executed"] is False
    assert guarantees["code_modified"] is False
    assert guarantees["governance_modified"] is False
    assert guarantees["authorization_artifact_created"] is False
    assert guarantees["execution_requested"] is False
