"""CHE-only exact Human-act transport for the canonical production CLIA."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable

from aigol.runtime.canonical_hic_conformance_runtime_v1 import (
    CLIA_CONFORMANCE_PROFILE_V1,
    CLIA_PRODUCTION_PROFILE_V1,
    create_canonical_hic_text_request_v1,
    reject_hic_owned_workflow_v1,
    validate_production_hic_activation_v1,
)
from aigol.runtime.canonical_human_entry_contract_v1 import (
    CanonicalHumanEntryResponseEnvelopeV1,
    validate_canonical_che_response_envelope_v1,
)
from aigol.runtime.human_interface_runtime_entry_service import (
    run_human_interface_runtime_entry,
)
from aigol.runtime.models import FailClosedRuntimeError

from .presentation import (
    render_clia_che_response_v1,
    validate_clia_che_response_v1,
)
from .session import (
    CLIA_DEVELOPMENT_STATUS,
    CLIA_PRODUCTION_ADAPTER_IDENTITY,
    CLIA_PRODUCTION_STATUS,
    CLIA_MAX_HUMAN_ACT_CHARACTERS,
    CliaTransportSession,
    acknowledge_clia_submission_v1,
    append_clia_input_line_v1,
    begin_clia_submission_v1,
    cancel_clia_pending_input_v1,
    close_clia_transport_session_v1,
    fail_clia_transport_session_v1,
    interrupt_clia_transport_session_v1,
    open_clia_transport_session_v1,
    pending_clia_human_act_v1,
    validate_clia_transport_session_v1,
)


CLIA_LOCAL_HELP = "\n".join(
    [
        "CLIA canonical thin Human Interaction Channel transport.",
        "Enter exact text lines, then use one transport control:",
        "/send   submit the exact buffered Human act to Canonical Human Entry",
        "/cancel clear only the unsent local buffer",
        "/exit   close the local transport session without runtime invocation",
        "/help   show this transport-only help",
    ]
)


class CliaDeliveryUncertainError(FailClosedRuntimeError):
    """Raised after a CHE invocation begins but delivery cannot be acknowledged."""


@dataclass(frozen=True, slots=True)
class CliaSubmissionResult:
    submission_identity: str
    che_response: dict[str, Any]
    canonical_response: CanonicalHumanEntryResponseEnvelopeV1
    presentation: str
    production_status: str = CLIA_PRODUCTION_STATUS


def submit_clia_human_act_v1(
    *,
    session: CliaTransportSession,
    human_act: str,
) -> CliaSubmissionResult:
    validate_clia_transport_session_v1(session)
    exact_act = _require_exact_human_act(human_act)
    if session.pending_input_lines:
        buffered_act = pending_clia_human_act_v1(session)
        if exact_act != buffered_act:
            fail_clia_transport_session_v1(
                session, "CLIA submitted act does not match the exact local buffer"
            )
            raise FailClosedRuntimeError(
                "CLIA submitted act does not match the exact local buffer"
            )
    # This is a release-status gate only. It supplies no workflow, branch,
    # semantic, or owner behavior to the HIC.
    production = session.adapter_identity == CLIA_PRODUCTION_ADAPTER_IDENTITY
    if production:
        try:
            validate_production_hic_activation_v1(session.runtime_root_reference)
        except FailClosedRuntimeError as exc:
            fail_clia_transport_session_v1(session, str(exc))
            raise
    submission_identity = begin_clia_submission_v1(session)
    request_identity = f"{submission_identity}:CHE-REQUEST"
    source_act_identity = (
        session.last_che_continuation_envelope.expected_next_act_identity
        if session.last_che_continuation_envelope is not None
        else f"{submission_identity}:SOURCE-ACT"
    )
    request = create_canonical_hic_text_request_v1(
        profile=(
            CLIA_PRODUCTION_PROFILE_V1
            if production
            else CLIA_CONFORMANCE_PROFILE_V1
        ),
        actor_identity=session.human_actor_reference,
        session_identity=session.transport_session_identity,
        workspace_identity=session.workspace_reference,
        runtime_scope_identity=session.runtime_root_reference,
        request_identity=request_identity,
        source_act_identity=source_act_identity,
        order_identity=f"{submission_identity}:ORDER",
        idempotency_identity=f"{submission_identity}:IDEMPOTENCY",
        exact_text=exact_act,
        created_at=session.created_at,
    )
    try:
        response = run_human_interface_runtime_entry(
            request_envelope=request,
            continuation_envelope=session.last_che_continuation_envelope,
            governed_runtime_runner=reject_hic_owned_workflow_v1,
        )
    except BaseException as exc:
        fail_clia_transport_session_v1(
            session,
            f"CHE delivery outcome is unknown for {submission_identity}",
        )
        raise CliaDeliveryUncertainError(
            "CLIA failed closed because CHE delivery could not be acknowledged"
        ) from exc
    try:
        canonical_response = validate_canonical_che_response_envelope_v1(response)
        validated_response = validate_clia_che_response_v1(
            canonical_response,
            transport_session_identity=session.transport_session_identity,
            submission_identity=submission_identity,
        )
        presentation = render_clia_che_response_v1(canonical_response)
    except FailClosedRuntimeError:
        fail_clia_transport_session_v1(
            session,
            f"CHE response is malformed for {submission_identity}",
        )
        raise
    acknowledge_clia_submission_v1(
        session,
        submission_identity=submission_identity,
        che_correlation_reference=canonical_response.correlation_identity,
        che_continuation_envelope=canonical_response.continuation_envelope,
    )
    return CliaSubmissionResult(
        submission_identity=submission_identity,
        che_response=deepcopy(validated_response),
        canonical_response=canonical_response,
        presentation=presentation,
    )


def run_clia_interactive_session_v1(
    *,
    session: CliaTransportSession,
    input_reader: Callable[[str], str] = input,
    output_writer: Callable[[str], None] = print,
) -> CliaTransportSession:
    validate_clia_transport_session_v1(session)
    if session.status.value == "CREATED":
        open_clia_transport_session_v1(session)
    elif session.status.value != "OPEN":
        fail_clia_transport_session_v1(
            session, "CLIA interactive session requires CREATED or OPEN state"
        )
        raise FailClosedRuntimeError(
            "CLIA interactive session requires CREATED or OPEN state"
        )
    output_writer(CLIA_LOCAL_HELP)
    while session.status.value == "OPEN":
        try:
            line = input_reader("... " if session.pending_input_lines else "clia> ")
        except KeyboardInterrupt:
            interrupt_clia_transport_session_v1(session)
            output_writer("CLIA transport interrupted; no Human act was submitted.")
            return session
        except (EOFError, StopIteration):
            close_clia_transport_session_v1(session)
            output_writer("CLIA transport closed on end-of-file; unsent input was discarded.")
            return session
        if not isinstance(line, str):
            fail_clia_transport_session_v1(
                session, "CLIA terminal input must be text"
            )
            raise FailClosedRuntimeError("CLIA terminal input must be text")
        if line == "/help":
            output_writer(CLIA_LOCAL_HELP)
            continue
        if line == "/cancel":
            cancel_clia_pending_input_v1(session)
            output_writer("CLIA unsent local buffer canceled.")
            continue
        if line == "/exit":
            close_clia_transport_session_v1(session)
            output_writer("CLIA transport session closed.")
            return session
        if line == "/send":
            try:
                human_act = pending_clia_human_act_v1(session)
            except FailClosedRuntimeError:
                output_writer("CLIA empty submission rejected; Canonical Human Entry was not invoked.")
                continue
            try:
                result = submit_clia_human_act_v1(
                    session=session,
                    human_act=human_act,
                )
            except FailClosedRuntimeError as exc:
                output_writer(f"CLIA transport failed closed: {exc}")
                return session
            output_writer(result.presentation)
            continue
        append_clia_input_line_v1(session, line)
    return session


def _require_exact_human_act(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError("CLIA cannot submit an empty Human act")
    if len(value) > CLIA_MAX_HUMAN_ACT_CHARACTERS:
        raise FailClosedRuntimeError("CLIA Human act character limit exceeded")
    return value
