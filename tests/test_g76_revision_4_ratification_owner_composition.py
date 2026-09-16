from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import shutil

import pytest

from aigol.runtime.canonical_hic_conformance_runtime_v1 import (
    CLIA_CONFORMANCE_PROFILE_V1,
    create_canonical_hic_human_authority_act_request_v1,
    create_canonical_hic_text_request_v1,
)
from aigol.runtime.canonical_human_authority_act_contract_v1 import (
    APPROVAL,
    CANONICAL_HUMAN_AUTHORITY_ACT_CONTRACT_VERSION,
    HUMAN_AUTHORITY_OWNER,
    CanonicalHumanAuthorityActV1,
    canonical_human_authority_act_from_request_v1,
    canonical_human_authority_payload_digest_v1,
)
from aigol.runtime.canonical_human_entry_contract_v1 import (
    ACTIVE_CONTINUATION,
    ELIGIBLE_SOURCE_ACTOR,
    HUMAN_ACTOR,
)
from aigol.runtime.constitutional_human_ratification_contract_v1 import (
    CONSTITUTIONAL_AMENDMENT_RATIFICATION_SCOPE,
    CONSTITUTIONAL_GOVERNANCE_OWNER,
    HUMAN_RATIFICATION_EVIDENCE_ORDER,
    HUMAN_RATIFICATION_RECORDED_NOT_CERTIFIED,
    constitutional_ratification_payload_v1,
)
from aigol.runtime.constitutional_impact_assessment_contract_v1 import (
    CROSS_CONSTITUTIONAL_IMPACT,
    IMPACT_ASSESSED_NOT_RATIFIED,
)
from aigol.runtime.g76_revision_4_ratification_owner_composition_v1 import (
    G76_REVISION_4_PRESENTATION_COMMAND,
    G76_REVISION_4_RATIFICATION_OWNER_STATUS,
    G76Revision4RatificationPackageV1,
    compose_g76_revision_4_human_ratification_v1,
    materialize_g76_revision_4_ratification_package_v1,
    present_g76_revision_4_ratification_boundary_v1,
    submit_g76_revision_4_human_ratification_v1,
    validate_g76_revision_4_ratification_package_v1,
)
from aigol.runtime.models import FailClosedRuntimeError


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATHS = (
    "docs/governance/G76_07_CONSTITUTIONAL_AMENDMENT_PROPOSAL_"
    "REVISION_4_RELEASE_DECISION_ARTIFACT_V1.md",
    "docs/governance/G76_08_CONSTITUTIONAL_IMPACT_ASSESSMENT_"
    "RELEASE_DECISION_ARTIFACT_REVISION_4_V1.md",
    "docs/governance/G76_09_CONSTITUTIONAL_HUMAN_RATIFICATION_"
    "RELEASE_DECISION_ARTIFACT_REVISION_4_V1.md",
    "docs/governance/G76_04_CONSTITUTIONAL_AMENDMENT_PROPOSAL_"
    "REVISION_3_RELEASE_DECISION_ARTIFACT_V1.md",
    "docs/governance/G76_06_CONSTITUTIONAL_ARTIFACT_IDENTITY_"
    "MODEL_RECONSTRUCTION_REPORT_V1.md",
    "docs/governance/G72_00_CONSTITUTIONAL_CORE_CLOSURE_AND_"
    "OPERATIONAL_READINESS_CERTIFICATION_REPORT_V1.md",
    "docs/governance/G69_19_CONSTITUTIONAL_PRODUCTION_CUTOVER_"
    "CERTIFICATION_REPORT_V1.md",
)


@pytest.fixture(scope="module")
def package() -> G76Revision4RatificationPackageV1:
    return materialize_g76_revision_4_ratification_package_v1(REPOSITORY_ROOT)


def _copy_sources(root: Path) -> None:
    for relative in SOURCE_PATHS:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPOSITORY_ROOT / relative, target)


def _presentation_request(runtime_root: Path, *, actor_class: str = HUMAN_ACTOR):
    request = create_canonical_hic_text_request_v1(
        profile=CLIA_CONFORMANCE_PROFILE_V1,
        actor_identity="G76-R4-HUMAN",
        session_identity="G76-R4-SESSION",
        workspace_identity="G76-R4-WORKSPACE",
        runtime_scope_identity=str(runtime_root),
        request_identity="G76-R4-PRESENTATION-REQUEST",
        source_act_identity="G76-R4-PRESENTATION-ACT",
        order_identity="G76-R4-PRESENTATION-ORDER",
        idempotency_identity="G76-R4-PRESENTATION-IDEMPOTENCY",
        exact_text=G76_REVISION_4_PRESENTATION_COMMAND,
        created_at="2026-09-16T10:00:00Z",
    )
    return replace(request, actor_class=actor_class)


def _presentation(package, runtime_root: Path):
    request = _presentation_request(runtime_root)
    response = present_g76_revision_4_ratification_boundary_v1(
        package=package, request=request
    )
    continuation = response.continuation_envelope
    assert continuation is not None
    return request, response, continuation


def _human_act_and_request(
    package,
    continuation,
    *,
    actor_identity="G76-R4-HUMAN",
    expected_owner=CONSTITUTIONAL_GOVERNANCE_OWNER,
    scope=CONSTITUTIONAL_AMENDMENT_RATIFICATION_SCOPE,
    target_identity=None,
    target_revision=4,
    authority_kind=APPROVAL,
):
    assessment = package.impact_assessment
    payload = constitutional_ratification_payload_v1(assessment)
    act = CanonicalHumanAuthorityActV1(
        contract_version=CANONICAL_HUMAN_AUTHORITY_ACT_CONTRACT_VERSION,
        authority_act_identity="G76-R4-TEST-HUMAN-ACT",
        authority_kind=authority_kind,
        interaction_identity=continuation.interaction_identity,
        conversation_identity=continuation.conversation_identity,
        session_identity=continuation.session_identity,
        actor_identity=actor_identity,
        request_identity="G76-R4-HUMAN-REQUEST",
        continuation_identity=continuation.continuation_identity,
        target_identity=target_identity or assessment.assessment_identity,
        target_revision=target_revision,
        producing_owner=HUMAN_AUTHORITY_OWNER,
        expected_owner=expected_owner,
        authority_scope=scope,
        payload=payload,
        payload_digest=canonical_human_authority_payload_digest_v1(payload),
        metadata={},
    )
    request = create_canonical_hic_human_authority_act_request_v1(
        profile=CLIA_CONFORMANCE_PROFILE_V1,
        human_authority_act=act,
        continuation=continuation,
        request_identity=act.request_identity,
        order_identity="G76-R4-HUMAN-ORDER",
        idempotency_identity="G76-R4-HUMAN-IDEMPOTENCY",
        created_at="2026-09-16T10:01:00Z",
    )
    return act, request


@pytest.mark.parametrize("relative", SOURCE_PATHS[:2])
def test_authenticated_g76_source_digest_mismatch_fails_closed(
    tmp_path: Path, relative: str
) -> None:
    _copy_sources(tmp_path)
    path = tmp_path / relative
    path.write_bytes(path.read_bytes() + b"\nTAMPERED\n")

    with pytest.raises(FailClosedRuntimeError, match="source digest mismatch"):
        materialize_g76_revision_4_ratification_package_v1(tmp_path)


def test_materialization_is_validator_accepted_deterministic_and_resolved(
    package,
) -> None:
    second = materialize_g76_revision_4_ratification_package_v1(REPOSITORY_ROOT)

    assert validate_g76_revision_4_ratification_package_v1(package) == package
    assert package == second
    assert package.amendment_proposal.proposal_revision == 4
    assert package.impact_assessment.assessment_status == IMPACT_ASSESSED_NOT_RATIFIED
    assert package.impact_assessment.impact_classification == (
        CROSS_CONSTITUTIONAL_IMPACT
    )
    assert package.amendment_proposal.proposal_identity == (
        second.amendment_proposal.proposal_identity
    )
    assert package.impact_assessment.artifact_digest == (
        second.impact_assessment.artifact_digest
    )
    assert package.impact_assessment.human_ratification_performed is False
    assert package.impact_assessment.amendment_certification_performed is False
    assert package.impact_assessment.amendment_activation_performed is False
    assert package.impact_assessment.production_path_count == 1
    assert package.impact_assessment.parallel_production_path_count == 0


@pytest.mark.parametrize(
    "proposal_mutation",
    (
        lambda proposal: replace(
            proposal,
            previous_proposal_identity="WRONG-PREDECESSOR",
        ),
        lambda proposal: replace(proposal, proposal_revision=3),
    ),
)
def test_wrong_predecessor_identity_or_revision_fails_closed(
    package, proposal_mutation
) -> None:
    bad_proposal = proposal_mutation(package.amendment_proposal)
    bad = replace(package, amendment_proposal=bad_proposal)

    with pytest.raises(FailClosedRuntimeError):
        validate_g76_revision_4_ratification_package_v1(bad)


def test_governance_owner_presents_validated_package_through_existing_che(
    package, tmp_path: Path
) -> None:
    request, response, continuation = _presentation(package, tmp_path)

    assert request.source_modality == "TEXT"
    assert response.owner_status == G76_REVISION_4_RATIFICATION_OWNER_STATUS
    assert response.owner_transition.producing_owner == CONSTITUTIONAL_GOVERNANCE_OWNER
    assert response.owner_transition.exact_human_act_required is True
    assert response.owner_transition.permitted_controls == (APPROVAL,)
    assert continuation.continuation_state == ACTIVE_CONTINUATION
    assert continuation.expected_next_act_identity == (
        package.impact_assessment.assessment_identity
    )
    assert continuation.expected_owner_revision == 4


def test_invalid_package_is_rejected_before_governance_owner_presentation(
    package, tmp_path: Path
) -> None:
    invalid_assessment = replace(
        package.impact_assessment,
        artifact_digest="sha256:" + ("0" * 64),
    )
    invalid = replace(package, impact_assessment=invalid_assessment)

    with pytest.raises(FailClosedRuntimeError, match="assessment identity"):
        present_g76_revision_4_ratification_boundary_v1(
            package=invalid,
            request=_presentation_request(tmp_path),
        )


def test_absent_or_arbitrary_text_human_act_cannot_create_ratification(
    package, tmp_path: Path
) -> None:
    _, _, continuation = _presentation(package, tmp_path)
    arbitrary = create_canonical_hic_text_request_v1(
        profile=CLIA_CONFORMANCE_PROFILE_V1,
        actor_identity=continuation.actor_identity,
        session_identity=continuation.session_identity,
        workspace_identity=continuation.workspace_identity,
        runtime_scope_identity=continuation.runtime_scope_identity,
        request_identity="G76-R4-ARBITRARY-REQUEST",
        source_act_identity="G76-R4-ARBITRARY-ACT",
        order_identity="G76-R4-ARBITRARY-ORDER",
        idempotency_identity="G76-R4-ARBITRARY-IDEMPOTENCY",
        exact_text="I approve this change",
        created_at="2026-09-16T10:01:00Z",
    )

    assert canonical_human_authority_act_from_request_v1(arbitrary) is None
    with pytest.raises(FailClosedRuntimeError):
        compose_g76_revision_4_human_ratification_v1(
            package=package,
            human_authority_act=None,
            che_request=arbitrary,
            che_continuation=continuation,
        )


def test_owner_issued_continuation_and_four_ordered_evidence_compose_g70_04(
    package, tmp_path: Path
) -> None:
    _, _, continuation = _presentation(package, tmp_path)
    act, request = _human_act_and_request(package, continuation)

    ratification = compose_g76_revision_4_human_ratification_v1(
        package=package,
        human_authority_act=act,
        che_request=request,
        che_continuation=continuation,
    )

    assert ratification.ratification_status == HUMAN_RATIFICATION_RECORDED_NOT_CERTIFIED
    assert tuple(item.evidence_role for item in ratification.evidence_references) == (
        HUMAN_RATIFICATION_EVIDENCE_ORDER
    )
    assert ratification.amendment_certification_performed is False
    assert ratification.amendment_activation_performed is False
    assert ratification.production_path_count == 1
    assert ratification.parallel_production_path_count == 0


def test_test_only_structured_act_reaches_g70_04_through_same_che(
    package, tmp_path: Path
) -> None:
    _, _, continuation = _presentation(package, tmp_path)
    _, request = _human_act_and_request(package, continuation)

    response = submit_g76_revision_4_human_ratification_v1(
        package=package,
        request=request,
        continuation=continuation,
    )

    assert response.owner_status == (
        "G76_REVISION_4_HUMAN_RATIFICATION_RECORDED_NOT_CERTIFIED"
    )
    assert response.response_type == "TERMINAL"
    assert response.continuation_envelope is not None
    assert response.continuation_envelope.continuation_state == "TERMINAL"


@pytest.mark.parametrize(
    "act_overrides",
    (
        {"actor_identity": "WRONG-HUMAN"},
        {"expected_owner": "WRONG-OWNER"},
        {"scope": "WRONG-SCOPE"},
        {"target_identity": "WRONG-TARGET"},
        {"target_revision": 3},
    ),
)
def test_wrong_actor_owner_scope_target_or_revision_fails_closed(
    package, tmp_path: Path, act_overrides
) -> None:
    _, _, continuation = _presentation(package, tmp_path)

    if "actor_identity" in act_overrides:
        with pytest.raises(FailClosedRuntimeError, match="Continuation binding"):
            _human_act_and_request(package, continuation, **act_overrides)
        return
    act, request = _human_act_and_request(
        package, continuation, **act_overrides
    )
    with pytest.raises(FailClosedRuntimeError):
        compose_g76_revision_4_human_ratification_v1(
            package=package,
            human_authority_act=act,
            che_request=request,
            che_continuation=continuation,
        )


def test_wrong_modality_and_guessed_continuation_fail_closed(
    package, tmp_path: Path
) -> None:
    _, _, continuation = _presentation(package, tmp_path)
    act, request = _human_act_and_request(package, continuation)

    with pytest.raises(FailClosedRuntimeError, match="STRUCTURED modality"):
        compose_g76_revision_4_human_ratification_v1(
            package=package,
            human_authority_act=act,
            che_request=replace(request, source_modality="TEXT"),
            che_continuation=continuation,
        )
    with pytest.raises(FailClosedRuntimeError):
        compose_g76_revision_4_human_ratification_v1(
            package=package,
            human_authority_act=act,
            che_request=request,
            che_continuation=replace(
                continuation,
                continuation_identity="GUESSED-CONTINUATION",
            ),
        )


def test_non_human_actor_cannot_open_ratification_presentation(
    package, tmp_path: Path
) -> None:
    with pytest.raises(FailClosedRuntimeError, match="Human actor"):
        present_g76_revision_4_ratification_boundary_v1(
            package=package,
            request=_presentation_request(
                tmp_path, actor_class=ELIGIBLE_SOURCE_ACTOR
            ),
        )


def test_step7_owner_module_does_not_import_g70_05_or_g70_06() -> None:
    source = (
        REPOSITORY_ROOT
        / "aigol/runtime/g76_revision_4_ratification_owner_composition_v1.py"
    ).read_text(encoding="utf-8")

    assert "constitutional_amendment_certification_contract_v1" not in source
    assert "constitutional_successor_publication_activation_contract_v1" not in source
    assert "activate_constitutional_production_cutover" not in source
    assert "e05" not in source.lower()
