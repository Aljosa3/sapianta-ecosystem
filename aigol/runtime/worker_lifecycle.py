"""Bounded worker lifecycle state machine for the runtime engine foundation."""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import FailClosedRuntimeError


CREATED = "CREATED"
PREPARED = "PREPARED"
DISPATCHED = "DISPATCHED"
RUNNING = "RUNNING"
RETURNED = "RETURNED"
CLOSED = "CLOSED"
BLOCKED = "BLOCKED"

ALLOWED_TRANSITIONS = {
    CREATED: PREPARED,
    PREPARED: DISPATCHED,
    DISPATCHED: RUNNING,
    RUNNING: RETURNED,
    RETURNED: CLOSED,
}


@dataclass
class WorkerLifecycle:
    worker_id: str
    state: str = CREATED
    transitions: list[dict[str, str]] = field(default_factory=list)

    def transition_to(self, next_state: str) -> None:
        expected = ALLOWED_TRANSITIONS.get(self.state)
        if expected != next_state:
            previous = self.state
            self.state = BLOCKED
            self.transitions.append(
                {
                    "from": previous,
                    "to": next_state,
                    "status": "BLOCKED",
                }
            )
            raise FailClosedRuntimeError(f"invalid lifecycle transition: {previous} -> {next_state}")
        self.transitions.append(
            {
                "from": self.state,
                "to": next_state,
                "status": "OK",
            }
        )
        self.state = next_state
