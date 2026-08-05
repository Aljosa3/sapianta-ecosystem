"""Transport-local session state for the canonical production CLIA."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from aigol.runtime.canonical_hic_conformance_runtime_v1 import (
    CLIA_CONFORMANCE_PROFILE_V1,
    CLIA_PRODUCTION_PROFILE_V1,
)
from aigol.runtime.canonical_human_entry_contract_v1 import (
    CanonicalContinuationEnvelopeV1,
    validate_canonical_che_continuation_envelope_v1,
)
from aigol.runtime.models import FailClosedRuntimeError


CLIA_TRANSPORT_VERSION = (
    "G69_13_COMPLETE_HIC_CONFORMANCE_AND_HISTORICAL_INDEPENDENCE_V1"
)
CLIA_ADAPTER_IDENTITY = CLIA_CONFORMANCE_PROFILE_V1.adapter_identity
CLIA_PRODUCTION_ADAPTER_IDENTITY = CLIA_PRODUCTION_PROFILE_V1.adapter_identity
CLIA_CHANNEL_IDENTITY = "CLI"
CLIA_INTERFACE_NAME = "CLIA"
CLIA_DEVELOPMENT_STATUS = (
    "CLIA_IMPLEMENTED_AS_DEVELOPMENT_HIC_NOT_PRODUCTION_CUTOVER"
)
CLIA_PRODUCTION_STATUS = "CLIA_CANONICAL_PRODUCTION_HIC_G69_19"
CLIA_MAX_INPUT_LINES = 128
CLIA_MAX_HUMAN_ACT_CHARACTERS = 65_536


class CliaTransportStatus(str, Enum):
    CREATED = "CREATED"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    TRANSPORT_FAILED_CLOSED = "TRANSPORT_FAILED_CLOSED"
    INTERRUPTED = "INTERRUPTED"


@dataclass(slots=True)
class CliaTransportSession:
    """Mutable transport state with no semantic or workflow fields."""

    transport_session_identity: str
    human_actor_reference: str
    workspace_reference: str
    runtime_root_reference: str
    created_at: str
    adapter_identity: str = CLIA_ADAPTER_IDENTITY
    channel_identity: str = CLIA_CHANNEL_IDENTITY
    status: CliaTransportStatus = CliaTransportStatus.CREATED
    next_submission_sequence: int = 1
    pending_input_lines: list[str] = field(default_factory=list)
    active_submission_identity: str | None = None
    last_submission_identity: str | None = None
    last_acknowledged_che_correlation_reference: str | None = None
    last_che_continuation_envelope: CanonicalContinuationEnvelopeV1 | None = None
    transport_failure_reason: str | None = None


def create_clia_transport_session_v1(
    *,
    transport_session_identity: str,
    human_actor_reference: str,
    workspace_reference: str,
    runtime_root_reference: str,
    created_at: str,
    production: bool = False,
) -> CliaTransportSession:
    session = CliaTransportSession(
        transport_session_identity=_require_identity(
            transport_session_identity, "transport_session_identity"
        ),
        human_actor_reference=_require_identity(
            human_actor_reference, "human_actor_reference"
        ),
        workspace_reference=_require_identity(
            workspace_reference, "workspace_reference"
        ),
        runtime_root_reference=_require_identity(
            runtime_root_reference, "runtime_root_reference"
        ),
        created_at=_require_identity(created_at, "created_at"),
        adapter_identity=(
            CLIA_PRODUCTION_ADAPTER_IDENTITY if production else CLIA_ADAPTER_IDENTITY
        ),
    )
    validate_clia_transport_session_v1(session)
    return session


def validate_clia_transport_session_v1(session: Any) -> CliaTransportSession:
    if not isinstance(session, CliaTransportSession):
        raise FailClosedRuntimeError("CLIA transport session is malformed")
    for field_name in (
        "transport_session_identity",
        "human_actor_reference",
        "workspace_reference",
        "runtime_root_reference",
        "created_at",
        "adapter_identity",
        "channel_identity",
    ):
        _require_identity(getattr(session, field_name), field_name)
    if session.adapter_identity not in {
        CLIA_ADAPTER_IDENTITY,
        CLIA_PRODUCTION_ADAPTER_IDENTITY,
    }:
        raise FailClosedRuntimeError("CLIA adapter identity is invalid")
    if session.channel_identity != CLIA_CHANNEL_IDENTITY:
        raise FailClosedRuntimeError("CLIA channel identity is invalid")
    if not isinstance(session.status, CliaTransportStatus):
        raise FailClosedRuntimeError("CLIA transport status is invalid")
    if not isinstance(session.next_submission_sequence, int) or isinstance(
        session.next_submission_sequence, bool
    ) or session.next_submission_sequence < 1:
        raise FailClosedRuntimeError("CLIA submission sequence is invalid")
    if not isinstance(session.pending_input_lines, list) or any(
        not isinstance(line, str) for line in session.pending_input_lines
    ):
        raise FailClosedRuntimeError("CLIA pending input buffer is malformed")
    if len(session.pending_input_lines) > CLIA_MAX_INPUT_LINES:
        raise FailClosedRuntimeError("CLIA pending input line limit exceeded")
    if len("\n".join(session.pending_input_lines)) > CLIA_MAX_HUMAN_ACT_CHARACTERS:
        raise FailClosedRuntimeError("CLIA pending input character limit exceeded")
    for field_name in (
        "active_submission_identity",
        "last_submission_identity",
        "last_acknowledged_che_correlation_reference",
        "transport_failure_reason",
    ):
        value = getattr(session, field_name)
        if value is not None:
            _require_identity(value, field_name)
    if session.last_che_continuation_envelope is not None:
        continuation = validate_canonical_che_continuation_envelope_v1(
            session.last_che_continuation_envelope
        )
        if any(
            (
                continuation.actor_identity != session.human_actor_reference,
                continuation.session_identity
                != session.transport_session_identity,
                continuation.workspace_identity != session.workspace_reference,
                continuation.runtime_scope_identity
                != session.runtime_root_reference,
            )
        ):
            raise FailClosedRuntimeError(
                "CLIA Continuation transport binding is invalid"
            )
    return session


def open_clia_transport_session_v1(
    session: CliaTransportSession,
) -> CliaTransportSession:
    validate_clia_transport_session_v1(session)
    if session.status is not CliaTransportStatus.CREATED:
        return _fail_transition(session, "CLIA session can open only from CREATED")
    session.status = CliaTransportStatus.OPEN
    return session


def append_clia_input_line_v1(
    session: CliaTransportSession,
    line: str,
) -> CliaTransportSession:
    _require_open_session(session)
    if not isinstance(line, str):
        return _fail_transition(session, "CLIA terminal input must be text")
    candidate = [*session.pending_input_lines, line]
    if len(candidate) > CLIA_MAX_INPUT_LINES:
        return _fail_transition(session, "CLIA pending input line limit exceeded")
    if len("\n".join(candidate)) > CLIA_MAX_HUMAN_ACT_CHARACTERS:
        return _fail_transition(
            session, "CLIA pending input character limit exceeded"
        )
    session.pending_input_lines.append(line)
    return session


def pending_clia_human_act_v1(session: CliaTransportSession) -> str:
    _require_open_session(session)
    human_act = "\n".join(session.pending_input_lines)
    if not human_act.strip():
        raise FailClosedRuntimeError("CLIA cannot submit an empty Human act")
    return human_act


def cancel_clia_pending_input_v1(
    session: CliaTransportSession,
) -> CliaTransportSession:
    _require_open_session(session)
    if session.active_submission_identity is not None:
        return _fail_transition(session, "CLIA cannot cancel an active submission")
    session.pending_input_lines.clear()
    return session


def begin_clia_submission_v1(session: CliaTransportSession) -> str:
    _require_open_session(session)
    if session.active_submission_identity is not None:
        return _fail_transition(session, "CLIA duplicate delivery is forbidden")
    submission_identity = (
        f"{session.transport_session_identity}:CLIA-SUBMISSION:"
        f"{session.next_submission_sequence:06d}"
    )
    session.active_submission_identity = submission_identity
    return submission_identity


def acknowledge_clia_submission_v1(
    session: CliaTransportSession,
    *,
    submission_identity: str,
    che_correlation_reference: str,
    che_continuation_envelope: CanonicalContinuationEnvelopeV1 | None = None,
) -> CliaTransportSession:
    _require_open_session(session)
    if session.active_submission_identity != submission_identity:
        return _fail_transition(session, "CLIA submission acknowledgement is stale")
    session.last_submission_identity = _require_identity(
        submission_identity, "submission_identity"
    )
    session.last_acknowledged_che_correlation_reference = _require_identity(
        che_correlation_reference, "che_correlation_reference"
    )
    session.last_che_continuation_envelope = (
        validate_canonical_che_continuation_envelope_v1(
            che_continuation_envelope
        )
        if che_continuation_envelope is not None
        else None
    )
    session.next_submission_sequence += 1
    session.active_submission_identity = None
    session.pending_input_lines.clear()
    return session


def close_clia_transport_session_v1(
    session: CliaTransportSession,
) -> CliaTransportSession:
    validate_clia_transport_session_v1(session)
    if session.status not in {
        CliaTransportStatus.CREATED,
        CliaTransportStatus.OPEN,
    }:
        return _fail_transition(session, "CLIA session cannot close from its current state")
    if session.active_submission_identity is not None:
        return _fail_transition(session, "CLIA cannot close during delivery")
    session.pending_input_lines.clear()
    session.status = CliaTransportStatus.CLOSED
    return session


def interrupt_clia_transport_session_v1(
    session: CliaTransportSession,
) -> CliaTransportSession:
    validate_clia_transport_session_v1(session)
    if session.status not in {
        CliaTransportStatus.CREATED,
        CliaTransportStatus.OPEN,
    }:
        return _fail_transition(
            session, "CLIA session cannot be interrupted from its current state"
        )
    session.pending_input_lines.clear()
    session.status = CliaTransportStatus.INTERRUPTED
    return session


def fail_clia_transport_session_v1(
    session: CliaTransportSession,
    reason: str,
) -> CliaTransportSession:
    if not isinstance(session, CliaTransportSession):
        raise FailClosedRuntimeError("CLIA transport session is malformed")
    session.status = CliaTransportStatus.TRANSPORT_FAILED_CLOSED
    session.transport_failure_reason = _require_identity(reason, "failure_reason")
    return session


def _require_open_session(session: CliaTransportSession) -> CliaTransportSession:
    try:
        validate_clia_transport_session_v1(session)
    except FailClosedRuntimeError as exc:
        if isinstance(session, CliaTransportSession):
            fail_clia_transport_session_v1(session, str(exc))
        raise
    if session.status is not CliaTransportStatus.OPEN:
        return _fail_transition(session, "CLIA transport session is not OPEN")
    return session


def _fail_transition(
    session: CliaTransportSession,
    message: str,
) -> Any:
    fail_clia_transport_session_v1(session, message)
    raise FailClosedRuntimeError(message)


def _require_identity(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
