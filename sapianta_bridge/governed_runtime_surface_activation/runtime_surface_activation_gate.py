"""Deterministic governed activation transition gate."""

ACTIVATION_STATES = (
    "SURFACE_REGISTERED",
    "SURFACE_BOUND",
    "SURFACE_VALIDATED",
    "SURFACE_ACTIVATION_REQUESTED",
    "SURFACE_ACTIVATION_APPROVED",
    "SURFACE_ACTIVATED",
    "SURFACE_OPERATIONAL",
    "BLOCKED",
    "FAILED",
)
TRANSITIONS = {
    "SURFACE_REGISTERED": "SURFACE_BOUND",
    "SURFACE_BOUND": "SURFACE_VALIDATED",
    "SURFACE_VALIDATED": "SURFACE_ACTIVATION_REQUESTED",
    "SURFACE_ACTIVATION_REQUESTED": "SURFACE_ACTIVATION_APPROVED",
    "SURFACE_ACTIVATION_APPROVED": "SURFACE_ACTIVATED",
    "SURFACE_ACTIVATED": "SURFACE_OPERATIONAL",
}
OPERATIONAL_PATH = tuple(TRANSITIONS) + ("SURFACE_OPERATIONAL",)


def validate_activation_transitions(states: tuple[str, ...]) -> dict:
    errors = []
    if not states:
        errors.append({"field": "states", "reason": "activation transition missing"})
    for current, following in zip(states, states[1:]):
        if TRANSITIONS.get(current) != following:
            errors.append({"field": "states", "reason": "invalid activation transition"})
    return {"valid": not errors, "errors": errors}
