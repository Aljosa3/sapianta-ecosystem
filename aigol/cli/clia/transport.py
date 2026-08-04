"""CHE-only exact Human-act transport for the development CLIA skeleton."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable

from aigol.runtime.human_interface_runtime_entry_service import (
    run_human_interface_runtime_entry,
)
from aigol.runtime.models import FailClosedRuntimeError

from .presentation import (
    render_clia_che_response_v1,
    validate_clia_che_response_v1,
)
from .session import (
    CLIA_ADAPTER_IDENTITY,
    CLIA_CHANNEL_IDENTITY,
    CLIA_DEVELOPMENT_STATUS,
    CLIA_INTERFACE_NAME,
    CLIA_MAX_HUMAN_ACT_CHARACTERS,
    CLIA_TRANSPORT_VERSION,
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
        "CLIA development-only thin Human Interaction Channel transport.",
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
    presentation: str
    development_status: str = CLIA_DEVELOPMENT_STATUS


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
    submission_identity = begin_clia_submission_v1(session)
    transport_presentation = {
        "clia_transport_version": CLIA_TRANSPORT_VERSION,
        "clia_adapter_identity": CLIA_ADAPTER_IDENTITY,
        "clia_channel_identity": CLIA_CHANNEL_IDENTITY,
        "clia_transport_session_identity": session.transport_session_identity,
        "clia_submission_identity": submission_identity,
        "clia_development_status": CLIA_DEVELOPMENT_STATUS,
    }
    try:
        response = run_human_interface_runtime_entry(
            interface_name=CLIA_INTERFACE_NAME,
            session_id=session.transport_session_identity,
            human_requests=[exact_act],
            created_at=session.created_at,
            runtime_root=session.runtime_root_reference,
            workspace=session.workspace_reference,
            governed_runtime_runner=_development_only_governed_runtime_runner,
            presentation=transport_presentation,
            g31_human_actor_id=session.human_actor_reference,
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
        validated_response = validate_clia_che_response_v1(
            response,
            transport_session_identity=session.transport_session_identity,
            submission_identity=submission_identity,
        )
        presentation = render_clia_che_response_v1(validated_response)
    except FailClosedRuntimeError:
        fail_clia_transport_session_v1(
            session,
            f"CHE response is malformed for {submission_identity}",
        )
        raise
    acknowledge_clia_submission_v1(
        session,
        submission_identity=submission_identity,
        che_correlation_reference=validated_response[
            "canonical_runtime_entry_session_id"
        ],
    )
    return CliaSubmissionResult(
        submission_identity=submission_identity,
        che_response=deepcopy(validated_response),
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


def _development_only_governed_runtime_runner(*_args: Any, **_kwargs: Any) -> dict:
    raise FailClosedRuntimeError(
        "CLIA development skeleton has no production runtime-runner binding"
    )


def _require_exact_human_act(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError("CLIA cannot submit an empty Human act")
    if len(value) > CLIA_MAX_HUMAN_ACT_CHARACTERS:
        raise FailClosedRuntimeError("CLIA Human act character limit exceeded")
    return value
