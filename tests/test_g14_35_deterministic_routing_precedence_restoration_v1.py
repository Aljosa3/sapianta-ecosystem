from __future__ import annotations

import pytest

from aigol.runtime.conversational_cli_runtime import (
    AI_DECISION_VALIDATOR_CAPABILITY_MODEL,
    CAPABILITY_LIFECYCLE_GOVERNANCE,
    CREATE_DOMAIN_COMPLIANCE_CLARIFICATION,
    CLARIFICATION_REQUIRED,
    DOMAIN_LIFECYCLE_GOVERNANCE,
    GOVERNED_DEVELOPMENT_WORKFLOW,
    NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION,
    OCS_LLM_COGNITION,
    WORKFLOW_SELECTED,
    route_conversational_cli_intent,
)


CREATED_AT = "2026-07-05T00:00:00Z"


def _route(tmp_path, prompt: str) -> dict:
    return route_conversational_cli_intent(
        routing_id="G14-35-ROUTING-PRECEDENCE",
        prompt_id="PROMPT-000001",
        human_prompt=prompt,
        canonical_chain_id="CHAIN-G14-35",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "routing",
    )


@pytest.mark.parametrize(
    ("prompt", "workflow_id"),
    [
        (
            "Create Product 1 AI Decision Validator capability model.",
            AI_DECISION_VALIDATOR_CAPABILITY_MODEL,
        ),
        (
            "I want to create the first real commercial Sapianta product. "
            "Use the current AiGOL architecture and repository state. "
            "Assume existing product domains remain read-only evidence.",
            OCS_LLM_COGNITION,
        ),
        (
            "Create a domain activation candidate for Product 1 AI Decision Validator.",
            DOMAIN_LIFECYCLE_GOVERNANCE,
        ),
        (
            "Create a capability activation candidate for Product 1 AI Decision Validator.",
            CAPABILITY_LIFECYCLE_GOVERNANCE,
        ),
        (
            "Prepare the foundation for the first AI Decision Validator domain, "
            "but do not implement production execution yet.",
            CREATE_DOMAIN_COMPLIANCE_CLARIFICATION,
        ),
        (
            "Add replay evidence validation",
            GOVERNED_DEVELOPMENT_WORKFLOW,
        ),
        (
            "Implement governance validation utility.",
            NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION,
        ),
    ],
)
def test_specific_deterministic_routes_precede_generic_native_development(tmp_path, prompt: str, workflow_id: str) -> None:
    capture = _route(tmp_path, prompt)

    assert capture["routing_status"] in {WORKFLOW_SELECTED, CLARIFICATION_REQUIRED}
    assert capture["workflow_id"] == workflow_id
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert capture["approval_bypassed"] is False
