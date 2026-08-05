from __future__ import annotations

import ast
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

import pytest

from aigol.runtime import constitutional_g64_completion_branch_composition_v1 as b8_v1
from aigol.runtime.constitutional_certification_completion_gate import (
    reconstruct_constitutional_completion_replay,
)
from aigol.runtime.constitutional_governance_certification import (
    certify_constitutional_governance,
)
from aigol.runtime.constitutional_production_workflow_branch_contract_v1 import (
    CONTENT_OR_REPOSITORY_MUTATION,
    GOVERNED_ACTION,
    GOVERNED_DEVELOPMENT,
    CanonicalWorkflowEvidenceReferenceV1,
    bind_canonical_workflow_branch_provenance_v1,
    create_canonical_production_workflow_branch_model_v1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash
from test_g64_07_constitutional_certification_completion_gate import (
    _assessment,
    _evidence,
    _pending_capture,
    _promotion,
)


MODULE = Path(
    "aigol/runtime/constitutional_g64_completion_branch_composition_v1.py"
)
G69_16_MODULE = Path(
    "aigol/runtime/constitutional_natural_conversation_branch_composition_v1.py"
)
OBSERVED_AT = "2026-08-05T15:00:00+00:00"


def _definition(model, branch_kind):
    return next(
        item for item in model.branch_definitions if item.branch_kind == branch_kind
    )


def _digest(label: str) -> str:
    return "sha256:" + sha256(label.encode("utf-8")).hexdigest()


def _references(model, branch_kind, overrides=None):
    overrides = overrides or {}
    return tuple(
        CanonicalWorkflowEvidenceReferenceV1(
            evidence_role=item.evidence_role,
            producing_owner=item.producing_owner,
            artifact_identity=f"{branch_kind}:{item.evidence_role}",
            artifact_digest=overrides.get(
                item.evidence_role,
                _digest(f"{branch_kind}:{item.evidence_role}"),
            ),
        )
        for item in _definition(model, branch_kind).required_evidence
    )


def _bind(model, branch_kind, sequence, previous, references):
    definition = _definition(model, branch_kind)
    return bind_canonical_workflow_branch_provenance_v1(
        model=model,
        source_request_identity="request-G69-17",
        source_interaction_identity="interaction-G69-17",
        branch_sequence=sequence,
        branch_kind=branch_kind,
        predecessor_branch_kind=None if previous is None else previous.branch_kind,
        previous_provenance_identity=(
            None if previous is None else previous.provenance_identity
        ),
        predicate_facts={
            definition.predicate.fact_name: definition.predicate.expected_value
        },
        evidence_references=references,
        observed_at=OBSERVED_AT,
    )


def _prefix(pending, *, override_role=None, override_digest=None):
    model = create_canonical_production_workflow_branch_model_v1()
    governed = _bind(
        model,
        GOVERNED_ACTION,
        1,
        None,
        _references(model, GOVERNED_ACTION),
    )
    development = _bind(
        model,
        GOVERNED_DEVELOPMENT,
        2,
        governed,
        _references(model, GOVERNED_DEVELOPMENT),
    )
    repository_outcome = pending["governed_repository_mutation_capture"][
        "governed_repository_mutation_outcome"
    ]
    overrides = {
        "VALIDATED_RESULT": repository_outcome["validation_hash"],
        "MUTATION_AUTHORIZATION": repository_outcome["approval_hash"],
        "REPLACEMENT_WORKER_RESULT": repository_outcome["worker_mutation_hash"],
    }
    if override_role:
        overrides[override_role] = override_digest
    mutation = _bind(
        model,
        CONTENT_OR_REPOSITORY_MUTATION,
        3,
        development,
        _references(model, CONTENT_OR_REPOSITORY_MUTATION, overrides),
    )
    return model, (governed, development, mutation)


def _completion_inputs(tmp_path, monkeypatch):
    pending = _pending_capture(tmp_path, monkeypatch)
    assessment = _assessment()
    certification = certify_constitutional_governance(assessment)
    promotion = _promotion(pending["execution_id"])
    evidence = _evidence(
        tmp_path / "G64_07_EXTERNAL_REPORT.md",
        pending,
        assessment,
        certification,
        promotion,
    )
    model, prefix = _prefix(pending)
    return pending, assessment, certification, promotion, evidence, model, prefix


def _compose(tmp_path, monkeypatch):
    (
        pending,
        assessment,
        certification,
        promotion,
        evidence,
        model,
        prefix,
    ) = _completion_inputs(tmp_path, monkeypatch)
    replay_dir = tmp_path / "g69-17-completion-replay"
    result = b8_v1.compose_constitutional_g64_completion_branch_v1(
        workflow_model=model,
        pre_completion_journey=prefix,
        governed_development_capture=pending,
        g48_report_evidence=evidence,
        governance_assessment=assessment,
        constitutional_certification=certification,
        promotion_evidence=promotion,
        finalization_id="G69-17-FINALIZATION",
        finalized_by="CONSTITUTIONAL_CERTIFICATION_OWNER",
        finalized_at=OBSERVED_AT,
        completion_replay_dir=replay_dir,
    )
    return result, replay_dir


def test_accepted_mutation_hands_off_to_g64_and_returns_one_terminal_journey(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result, replay_dir = _compose(tmp_path, monkeypatch)

    assert result["composition_status"] == b8_v1.COMPLETION_BRANCH_ESTABLISHED
    assert result["failure_code"] is None
    assert result["g64_finalizer_invoked"] is True
    assert [item["branch_kind"] for item in result["branch_journey"]] == [
        "GOVERNED_ACTION",
        "GOVERNED_DEVELOPMENT",
        "CONTENT_OR_REPOSITORY_MUTATION",
        "CONSTITUTIONAL_COMPLETION",
        "HUMAN_RETURN",
    ]
    assert result["completion_capture"]["constitutional_completion_reached"] is True
    assert result["canonical_presentation"]["presentation_state"] == "TERMINAL"
    assert result["canonical_presentation"]["presentation_kind"] == "TERMINAL_OUTCOME"
    assert result["branch_replay_coverage_created"] is False
    assert result["cro_observation_performed"] is False
    assert result["production_cutover_performed"] is False
    assert b8_v1.validate_constitutional_g64_completion_branch_composition_result_v1(
        result
    ) == result
    reconstructed = reconstruct_constitutional_completion_replay(replay_dir)
    assert reconstructed["completion_status"] == "GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED"
    assert reconstructed["replay_artifact_count"] == 6


@pytest.mark.parametrize(
    "role",
    ("VALIDATED_RESULT", "MUTATION_AUTHORIZATION", "REPLACEMENT_WORKER_RESULT"),
)
def test_unbound_accepted_mutation_stops_before_g64(
    role: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pending = _pending_capture(tmp_path, monkeypatch)
    model, prefix = _prefix(
        pending,
        override_role=role,
        override_digest=_digest(f"wrong:{role}"),
    )
    invoked = False

    def forbidden_finalizer(**_kwargs):
        nonlocal invoked
        invoked = True
        raise AssertionError("G64 must not be invoked")

    monkeypatch.setattr(
        b8_v1.g64_v1,
        "finalize_governed_development_completion",
        forbidden_finalizer,
    )
    result = b8_v1.compose_constitutional_g64_completion_branch_v1(
        workflow_model=model,
        pre_completion_journey=prefix,
        governed_development_capture=pending,
        g48_report_evidence={},
        governance_assessment=_assessment(),
        constitutional_certification=certify_constitutional_governance(_assessment()),
        promotion_evidence=_promotion(pending["execution_id"]),
        finalization_id="G69-17-REJECTED",
        finalized_by="CONSTITUTIONAL_CERTIFICATION_OWNER",
        finalized_at=OBSERVED_AT,
        completion_replay_dir=tmp_path / "must-not-exist",
    )

    assert result["composition_status"] == b8_v1.COMPLETION_BRANCH_FAILED_CLOSED
    assert role in result["failure_code"]
    assert result["g64_finalizer_invoked"] is False
    assert invoked is False
    assert not (tmp_path / "must-not-exist").exists()


def test_tampered_or_non_governed_prefix_stops_before_g64(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pending = _pending_capture(tmp_path, monkeypatch)
    model, prefix = _prefix(pending)
    tampered = list(prefix)
    value = tampered[-1].to_dict()
    value["source_interaction_identity"] = "different-interaction"
    tampered[-1] = value
    result = b8_v1.compose_constitutional_g64_completion_branch_v1(
        workflow_model=model,
        pre_completion_journey=tuple(tampered),
        governed_development_capture=pending,
        g48_report_evidence={},
        governance_assessment=_assessment(),
        constitutional_certification=certify_constitutional_governance(_assessment()),
        promotion_evidence=_promotion(pending["execution_id"]),
        finalization_id="G69-17-TAMPERED",
        finalized_by="CONSTITUTIONAL_CERTIFICATION_OWNER",
        finalized_at=OBSERVED_AT,
        completion_replay_dir=tmp_path / "tampered-replay",
    )

    assert result["composition_status"] == b8_v1.COMPLETION_BRANCH_FAILED_CLOSED
    assert result["g64_finalizer_invoked"] is False
    assert result["canonical_presentation"] is None


def test_missing_external_completion_evidence_fails_before_g64(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pending = _pending_capture(tmp_path, monkeypatch)
    model, prefix = _prefix(pending)
    assessment = _assessment()
    result = b8_v1.compose_constitutional_g64_completion_branch_v1(
        workflow_model=model,
        pre_completion_journey=prefix,
        governed_development_capture=pending,
        g48_report_evidence={},
        governance_assessment=assessment,
        constitutional_certification=certify_constitutional_governance(assessment),
        promotion_evidence=_promotion(pending["execution_id"]),
        finalization_id="G69-17-NO-REPORT",
        finalized_by="CONSTITUTIONAL_CERTIFICATION_OWNER",
        finalized_at=OBSERVED_AT,
        completion_replay_dir=tmp_path / "no-report-replay",
    )

    assert result["composition_status"] == b8_v1.COMPLETION_BRANCH_FAILED_CLOSED
    assert result["g64_finalizer_invoked"] is False
    assert result["completion_capture"] is None


def test_failed_g64_owner_result_never_creates_completion_or_human_return(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (
        pending,
        assessment,
        certification,
        promotion,
        evidence,
        model,
        prefix,
    ) = _completion_inputs(tmp_path, monkeypatch)

    def failed_finalizer(**_kwargs):
        capture = {
            "runtime_version": "CONSTITUTIONAL_CERTIFICATION_COMPLETION_GATE_V1",
            "finalization_id": "G69-17-FAILED",
            "related_change_id": pending["execution_id"],
            "completion_status": "CONSTITUTIONAL_COMPLETION_FAILED_CLOSED",
            "constitutional_completion_reached": False,
            "promotion_eligible": False,
            "repository_mutated": False,
            "worker_invoked": False,
            "authorization_created": False,
            "constitutional_completion_artifact": {},
            "replay_reference": str(tmp_path / "failed"),
            "fail_closed": True,
            "failure_reason": "CERTIFICATION_MISMATCH",
        }
        capture["capture_hash"] = replay_hash(capture)
        return capture

    monkeypatch.setattr(
        b8_v1.g64_v1,
        "finalize_governed_development_completion",
        failed_finalizer,
    )
    result = b8_v1.compose_constitutional_g64_completion_branch_v1(
        workflow_model=model,
        pre_completion_journey=prefix,
        governed_development_capture=pending,
        g48_report_evidence=evidence,
        governance_assessment=assessment,
        constitutional_certification=certification,
        promotion_evidence=promotion,
        finalization_id="G69-17-FAILED",
        finalized_by="CONSTITUTIONAL_CERTIFICATION_OWNER",
        finalized_at=OBSERVED_AT,
        completion_replay_dir=tmp_path / "failed",
    )

    assert result["composition_status"] == b8_v1.COMPLETION_BRANCH_FAILED_CLOSED
    assert result["g64_finalizer_invoked"] is True
    assert result["branch_journey"] == []
    assert result["canonical_presentation"] is None


def test_result_and_completion_provenance_tamper_fail_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result, _ = _compose(tmp_path, monkeypatch)
    tampered = deepcopy(result)
    tampered["completion_provenance"]["g64_completion_artifact_digest"] = _digest(
        "tampered"
    )
    tampered["completion_provenance"]["provenance_hash"] = replay_hash(
        {
            key: value
            for key, value in tampered["completion_provenance"].items()
            if key != "provenance_hash"
        }
    )
    tampered["result_hash"] = replay_hash(
        {key: value for key, value in tampered.items() if key != "result_hash"}
    )

    with pytest.raises(FailClosedRuntimeError, match="provenance is invalid"):
        b8_v1.validate_constitutional_g64_completion_branch_composition_result_v1(
            tampered
        )


def test_b8_has_no_b9_b10_hic_or_historical_dependency() -> None:
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    imports = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    source = MODULE.read_text(encoding="utf-8")
    g69_16_source = G69_16_MODULE.read_text(encoding="utf-8")

    assert "constitutional_runtime_observatory" not in " ".join(imports)
    assert "human_interface_runtime_entry_service" not in " ".join(imports)
    assert "production_conversation_flow_binding" not in " ".join(imports)
    assert "historical" not in " ".join(imports).lower()
    assert "branch_replay_coverage_created\": False" in source
    assert "cro_observation_performed\": False" in source
    assert "production_cutover_performed\": False" in source
    assert '"g64_completion_invoked": False' in g69_16_source
