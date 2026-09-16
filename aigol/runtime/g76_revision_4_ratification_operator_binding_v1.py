"""Operator binding for the existing G76 Revision 4 G70-04 boundary.

This module adds reachability only.  It reuses the certified development CLIA
HIC profile, the sole CHE, the Constitutional Governance owner composition,
and the existing structured Human Authority Act ingress.  Presentation never
creates authority.  Only an exact, later Human command can create the
structured act that the existing G70-04 consumer validates and consumes.
"""

from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.canonical_hic_conformance_runtime_v1 import (
    CLIA_CONFORMANCE_PROFILE_V1,
    create_canonical_hic_human_authority_act_request_v1,
    create_canonical_hic_text_request_v1,
)
from aigol.runtime.canonical_human_authority_act_contract_v1 import (
    CANONICAL_HUMAN_AUTHORITY_ACT_CONTRACT_VERSION,
    HUMAN_AUTHORITY_OWNER,
    CanonicalHumanAuthorityActV1,
    canonical_human_authority_payload_digest_v1,
)
from aigol.runtime.constitutional_human_ratification_contract_v1 import (
    CONSTITUTIONAL_AMENDMENT_RATIFICATION_SCOPE,
    CONSTITUTIONAL_GOVERNANCE_OWNER,
    RATIFY_CONSTITUTIONAL_AMENDMENT,
)
from aigol.runtime.g76_revision_4_ratification_owner_composition_v1 import (
    G76_REVISION_4_PRESENTATION_COMMAND,
    G76_REVISION_4_RATIFICATION_RECORDED_STATUS,
    materialize_g76_revision_4_ratification_package_v1,
    present_g76_revision_4_ratification_boundary_v1,
    submit_g76_revision_4_human_ratification_v1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


G76_REVISION_4_OPERATOR_BINDING_VERSION = (
    "G76_REVISION_4_G70_RATIFICATION_OPERATOR_BINDING_V1"
)
G76_REVISION_4_OPERATOR_PRESENTED = (
    "G76_REVISION_4_OPERATOR_PRESENTED_NO_HUMAN_ACT"
)
G76_REVISION_4_OPERATOR_EXITED = "G76_REVISION_4_OPERATOR_EXITED_NO_HUMAN_ACT"
G76_REVISION_4_OPERATOR_INPUT_REJECTED = (
    "G76_REVISION_4_OPERATOR_INPUT_REJECTED_NO_HUMAN_ACT"
)
G76_REVISION_4_OPERATOR_RATIFICATION_RECORDED = (
    "G76_REVISION_4_OPERATOR_HUMAN_RATIFICATION_RECORDED_NOT_CERTIFIED"
)
G76_REVISION_4_OPERATOR_ACT_PROMPT = (
    "Enter exact RATIFY_CONSTITUTIONAL_AMENDMENT to issue the positive Human "
    "act, or /exit to leave without a constitutional REJECT artifact: "
)


def _require_identity(value: Any, field_name: str) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or value != value.strip()
        or any(character.isspace() for character in value)
    ):
        raise FailClosedRuntimeError(f"{field_name} is invalid")
    return value


def _identity(prefix: str, seed: dict[str, Any]) -> str:
    return prefix + replay_hash(seed).removeprefix("sha256:")


def _presentation_request_v1(
    *,
    actor_identity: str,
    session_identity: str,
    workspace_identity: str,
    runtime_scope_identity: str,
    created_at: str,
):
    seed = {
        "binding_version": G76_REVISION_4_OPERATOR_BINDING_VERSION,
        "phase": "PRESENTATION",
        "actor_identity": actor_identity,
        "session_identity": session_identity,
        "workspace_identity": workspace_identity,
        "runtime_scope_identity": runtime_scope_identity,
    }
    return create_canonical_hic_text_request_v1(
        profile=CLIA_CONFORMANCE_PROFILE_V1,
        actor_identity=actor_identity,
        session_identity=session_identity,
        workspace_identity=workspace_identity,
        runtime_scope_identity=runtime_scope_identity,
        request_identity=_identity("G76-R4-OPERATOR-PRESENTATION-REQUEST-", seed),
        source_act_identity=_identity("G76-R4-OPERATOR-PRESENTATION-ACT-", seed),
        order_identity=_identity("G76-R4-OPERATOR-PRESENTATION-ORDER-", seed),
        idempotency_identity=_identity(
            "G76-R4-OPERATOR-PRESENTATION-IDEMPOTENCY-", seed
        ),
        exact_text=G76_REVISION_4_PRESENTATION_COMMAND,
        created_at=created_at,
    )


def g76_revision_4_operator_decision_summary_v1(
    *, package: Any, response: Any
) -> dict[str, Any]:
    """Derive the operator decision summary from validated machine objects."""

    transition = response.owner_transition
    continuation = response.continuation_envelope
    if continuation is None or transition.exact_human_act_required is not True:
        raise FailClosedRuntimeError(
            "G76 Revision 4 operator presentation lacks an active Human boundary"
        )
    payload = deepcopy(
        transition.to_dict()["payload_constraints"]["ratification_payload"]
    )
    proposal = package.amendment_proposal
    bindings = transition.to_dict()["payload_constraints"][
        "canonical_authority_act_binding"
    ]
    if (
        payload.get("ratification_command") != RATIFY_CONSTITUTIONAL_AMENDMENT
        or bindings.get("authority_scope")
        != CONSTITUTIONAL_AMENDMENT_RATIFICATION_SCOPE
        or bindings.get("expected_owner") != CONSTITUTIONAL_GOVERNANCE_OWNER
        or bindings.get("producing_owner") != HUMAN_AUTHORITY_OWNER
    ):
        raise FailClosedRuntimeError(
            "G76 Revision 4 operator decision contract is invalid"
        )
    return {
        "decision_type": CONSTITUTIONAL_AMENDMENT_RATIFICATION_SCOPE,
        "target": payload["impact_assessment_identity"],
        "target_digest": payload["impact_assessment_digest"],
        "revision": transition.next_act_expected_owner_revision,
        "proposal_identity": payload["amendment_proposal_identity"],
        "constitutional_gap_identity": payload["constitutional_gap_identity"],
        "current_active_predecessor": (
            f"{proposal.target_constitutional_artifact_identity}"
            f"@{proposal.target_constitutional_artifact_version}"
        ),
        "proposed_successor": proposal.proposed_successor_version,
        "authority_owner": bindings["producing_owner"],
        "ratification_processor": bindings["expected_owner"],
        "positive_human_action": payload["ratification_command"],
        "continuation_identity": continuation.continuation_identity,
        "continuation_state": continuation.continuation_state,
        "ratification_payload": payload,
    }


def render_g76_revision_4_operator_decision_v1(summary: dict[str, Any]) -> str:
    """Render a neutral exact decision surface with explicit non-effects."""

    return "\n".join(
        [
            "=== G76 REVISION 4 CONSTITUTIONAL HUMAN DECISION ===",
            f"DECISION_TYPE = {summary['decision_type']}",
            f"TARGET = {summary['target']}",
            f"TARGET_DIGEST = {summary['target_digest']}",
            f"REVISION = {summary['revision']}",
            f"PROPOSAL_IDENTITY = {summary['proposal_identity']}",
            (
                "CONSTITUTIONAL_GAP_IDENTITY = "
                f"{summary['constitutional_gap_identity']}"
            ),
            (
                "CURRENT_ACTIVE_PREDECESSOR = "
                f"{summary['current_active_predecessor']}"
            ),
            f"PROPOSED_SUCCESSOR = {summary['proposed_successor']}",
            f"AUTHORITY_OWNER = {summary['authority_owner']}",
            f"RATIFICATION_PROCESSOR = {summary['ratification_processor']}",
            f"ACTIVE_CONTINUATION = {summary['continuation_identity']}",
            "",
            (
                "Ratification would authorize continuation toward G70-05/G70-06 "
                "only under their separate contracts."
            ),
            (
                "Ratification would NOT implement CDP, issue a release decision, "
                "activate Production Cutover, retry MA, or grant E05 credit."
            ),
            "NO_POSITIVE_ACT != RATIFICATION",
            "SILENCE != APPROVAL",
            (
                "The presentation itself creates zero Human Authority acts. "
                "Arbitrary text and /send are not ratification."
            ),
            (
                "Lawful positive action requires the exact command: "
                f"{summary['positive_human_action']}"
            ),
        ]
    )


def create_explicit_g76_revision_4_human_act_v1(
    *,
    exact_human_input: str,
    response: Any,
) -> CanonicalHumanAuthorityActV1:
    """Translate only the exact explicit Human command into the existing act."""

    if exact_human_input != RATIFY_CONSTITUTIONAL_AMENDMENT:
        raise FailClosedRuntimeError(
            "G76 Revision 4 positive Human act requires the exact command"
        )
    continuation = response.continuation_envelope
    if continuation is None:
        raise FailClosedRuntimeError(
            "G76 Revision 4 positive Human act requires an active Continuation"
        )
    transition = response.owner_transition.to_dict()
    bindings = transition["payload_constraints"]["canonical_authority_act_binding"]
    payload = deepcopy(transition["payload_constraints"]["ratification_payload"])
    seed = {
        "binding_version": G76_REVISION_4_OPERATOR_BINDING_VERSION,
        "phase": "EXPLICIT_POSITIVE_HUMAN_ACT",
        "exact_human_input": exact_human_input,
        "continuation_identity": continuation.continuation_identity,
        "actor_identity": continuation.actor_identity,
        "session_identity": continuation.session_identity,
        "payload": payload,
    }
    return CanonicalHumanAuthorityActV1(
        contract_version=CANONICAL_HUMAN_AUTHORITY_ACT_CONTRACT_VERSION,
        authority_act_identity=_identity("HUMAN-AUTHORITY-ACT-G76-R4-", seed),
        authority_kind=bindings["authority_kind"],
        interaction_identity=continuation.interaction_identity,
        conversation_identity=continuation.conversation_identity,
        session_identity=continuation.session_identity,
        actor_identity=continuation.actor_identity,
        request_identity=_identity("G76-R4-HUMAN-ACT-REQUEST-", seed),
        continuation_identity=continuation.continuation_identity,
        target_identity=bindings["target_identity"],
        target_revision=bindings["target_revision"],
        producing_owner=bindings["producing_owner"],
        expected_owner=bindings["expected_owner"],
        authority_scope=bindings["authority_scope"],
        payload=payload,
        payload_digest=canonical_human_authority_payload_digest_v1(payload),
        metadata={
            "operator_binding_version": G76_REVISION_4_OPERATOR_BINDING_VERSION,
            "explicit_human_command": RATIFY_CONSTITUTIONAL_AMENDMENT,
        },
    )


def _submit_explicit_human_act_v1(
    *,
    package: Any,
    response: Any,
    human_act: CanonicalHumanAuthorityActV1,
    created_at: str,
):
    continuation = response.continuation_envelope
    if continuation is None:
        raise FailClosedRuntimeError(
            "G76 Revision 4 Human act submission requires a Continuation"
        )
    seed = {
        "binding_version": G76_REVISION_4_OPERATOR_BINDING_VERSION,
        "phase": "STRUCTURED_HUMAN_ACT_INGRESS",
        "authority_act_identity": human_act.authority_act_identity,
        "continuation_identity": continuation.continuation_identity,
    }
    request = create_canonical_hic_human_authority_act_request_v1(
        profile=CLIA_CONFORMANCE_PROFILE_V1,
        human_authority_act=human_act,
        continuation=continuation,
        request_identity=human_act.request_identity,
        order_identity=_identity("G76-R4-HUMAN-ACT-ORDER-", seed),
        idempotency_identity=_identity("G76-R4-HUMAN-ACT-IDEMPOTENCY-", seed),
        created_at=created_at,
    )
    return submit_g76_revision_4_human_ratification_v1(
        package=package,
        request=request,
        continuation=continuation,
    )


def run_g76_revision_4_ratification_operator_binding_v1(
    *,
    repository_root: str | Path,
    session_identity: str,
    human_actor_identity: str,
    workspace_identity: str | Path,
    runtime_scope_identity: str | Path,
    created_at: str,
    input_reader: Callable[[str], str] = input,
    output_writer: Callable[[str], None] = print,
) -> dict[str, Any]:
    """Present, then stop unless the Human supplies the exact positive act."""

    bound_session_identity = _require_identity(session_identity, "session_identity")
    bound_actor_identity = _require_identity(
        human_actor_identity, "human_actor_identity"
    )
    bound_workspace_identity = str(Path(workspace_identity).resolve())
    bound_runtime_scope_identity = str(Path(runtime_scope_identity).resolve())
    bound_created_at = _require_identity(created_at, "created_at")
    package = materialize_g76_revision_4_ratification_package_v1(repository_root)
    request = _presentation_request_v1(
        actor_identity=bound_actor_identity,
        session_identity=bound_session_identity,
        workspace_identity=bound_workspace_identity,
        runtime_scope_identity=bound_runtime_scope_identity,
        created_at=bound_created_at,
    )
    response = present_g76_revision_4_ratification_boundary_v1(
        package=package,
        request=request,
    )
    summary = g76_revision_4_operator_decision_summary_v1(
        package=package,
        response=response,
    )
    output_writer(render_g76_revision_4_operator_decision_v1(summary))

    base_result = {
        "binding_version": G76_REVISION_4_OPERATOR_BINDING_VERSION,
        "operator_status": G76_REVISION_4_OPERATOR_PRESENTED,
        "operator_surface": "RUNTIME_OPERATOR_CLI",
        "hic_profile": CLIA_CONFORMANCE_PROFILE_V1.adapter_identity,
        "request": request.to_dict(),
        "continuation": response.continuation_envelope.to_dict(),
        "decision_summary": summary,
        "human_authority_acts_created": 0,
        "human_authority_acts_consumed": 0,
        "ratification_artifacts_created": 0,
        "g70_05_executed": False,
        "g70_06_executed": False,
    }
    try:
        human_input = input_reader(G76_REVISION_4_OPERATOR_ACT_PROMPT)
    except (EOFError, StopIteration, KeyboardInterrupt):
        output_writer(
            "No positive Human act received; the active Continuation remains awaiting Human Authority."
        )
        return base_result
    if not isinstance(human_input, str):
        raise FailClosedRuntimeError("G76 Revision 4 operator input must be text")
    if not human_input.strip() or human_input.strip() in {"/exit", "/decline"}:
        output_writer(
            "Exited without ratification; no constitutional REJECT artifact was created."
        )
        return {**base_result, "operator_status": G76_REVISION_4_OPERATOR_EXITED}
    if human_input != RATIFY_CONSTITUTIONAL_AMENDMENT:
        output_writer(
            "Input rejected: no Human Authority act or ratification artifact was created."
        )
        return {
            **base_result,
            "operator_status": G76_REVISION_4_OPERATOR_INPUT_REJECTED,
        }

    human_act = create_explicit_g76_revision_4_human_act_v1(
        exact_human_input=human_input,
        response=response,
    )
    terminal = _submit_explicit_human_act_v1(
        package=package,
        response=response,
        human_act=human_act,
        created_at=bound_created_at,
    )
    if terminal.owner_status != G76_REVISION_4_RATIFICATION_RECORDED_STATUS:
        raise FailClosedRuntimeError(
            "G76 Revision 4 operator ratification did not reach the exact owner state"
        )
    output_writer(
        "Human ratification was recorded and remains not certified. STOP before G70-05."
    )
    return {
        **base_result,
        "operator_status": G76_REVISION_4_OPERATOR_RATIFICATION_RECORDED,
        "human_authority_act_identity": human_act.authority_act_identity,
        "human_authority_acts_created": 1,
        "human_authority_acts_consumed": 1,
        "ratification_artifacts_created": 1,
        "terminal_response": terminal.to_dict(),
    }


__all__ = [
    "G76_REVISION_4_OPERATOR_ACT_PROMPT",
    "G76_REVISION_4_OPERATOR_BINDING_VERSION",
    "G76_REVISION_4_OPERATOR_EXITED",
    "G76_REVISION_4_OPERATOR_INPUT_REJECTED",
    "G76_REVISION_4_OPERATOR_PRESENTED",
    "G76_REVISION_4_OPERATOR_RATIFICATION_RECORDED",
    "create_explicit_g76_revision_4_human_act_v1",
    "g76_revision_4_operator_decision_summary_v1",
    "render_g76_revision_4_operator_decision_v1",
    "run_g76_revision_4_ratification_operator_binding_v1",
]
