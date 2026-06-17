# AIGOL First Live Provider Operator Entrypoint V1

Status: implemented operator entrypoint milestone.

Purpose: provide the smallest governed operator-facing entrypoint for one authorized OpenAI dispatch attempt.

This milestone does not redesign architecture.

It does not expand ERR.

It does not authorize retries.

It does not authorize fallback.

It does not authorize workers.

It does not disclose credentials.

## Implementation

Runtime:

```text
AIGOL_FIRST_LIVE_PROVIDER_OPERATOR_ENTRYPOINT_V1
```

File:

```text
aigol/runtime/first_live_provider_operator_entrypoint.py
```

Focused tests:

```text
tests/test_first_live_provider_operator_entrypoint_v1.py
```

## Entrypoint Path

The operator entrypoint performs:

```text
operator dispatch request
-> load dispatch authorization replay
-> verify authorization freshness
-> verify single-attempt constraint
-> verify operator confirmation
-> verify AIGOL_OPENAI_API_KEY presence
-> invoke AIGOL_FIRST_LIVE_PROVIDER_EXECUTION_RUNTIME_V1
-> return execution status
-> return execution replay location
-> record operator replay evidence
```

## Replay Evidence

Operator entrypoint replay:

```text
000_first_live_provider_operator_dispatch_request.json
001_first_live_provider_operator_dispatch_result.json
```

Execution runtime replay remains under the execution replay directory provided to the entrypoint.

## Operator Usage Example

Python usage:

```python
from aigol.runtime.first_live_provider_operator_entrypoint import (
    run_first_live_provider_operator_entrypoint,
)

result = run_first_live_provider_operator_entrypoint(
    operator_request_id="FIRST-LIVE-PROVIDER-OPERATOR-DISPATCH-000001",
    operator_id="human.operator",
    human_request="Validate one governed OpenAI dispatch attempt.",
    created_at="2026-06-17T00:00:00+00:00",
    activation_package_replay_dir="runtime/first_live_provider/activation",
    dispatch_authorization_replay_dir="runtime/first_live_provider/dispatch_authorization",
    execution_replay_dir="runtime/first_live_provider/execution",
    operator_replay_dir="runtime/first_live_provider/operator_entrypoint",
    transport=governed_transport,
    confirm_dispatch=True,
)

print(result["final_status"])
print(result["execution_replay_reference"])
```

Required environment:

```text
AIGOL_OPENAI_API_KEY
```

The credential value must not be written to the repository or replay.

## Fail-Closed Conditions

The entrypoint fails closed if:

- operator confirmation is missing;
- dispatch authorization replay is missing;
- dispatch authorization replay hash is invalid;
- dispatch authorization artifact is invalid;
- authorization is expired;
- authorization is not bound to `openai`;
- authorization is not single-attempt;
- authorization was already attempted or performed;
- `AIGOL_OPENAI_API_KEY` is unavailable;
- operator replay already exists;
- execution runtime fails closed.

## Governance Invariants

Preserved:

```text
ERR_PASSIVE = true
DISPATCH_ATTEMPT_LIMIT = 1
PROVIDER = openai
PROVIDER_RESOURCE_TYPE = COGNITION_PROVIDER
SECRET_REPLAY = false
AUTHORIZATION_HEADER_REPLAY = false
WORKER_INVOCATION = false
PROVIDER_ROUTING = false
FALLBACK = false
AUTOMATIC_RETRY = false
GOVERNANCE_MUTATION = false
REPLAY_MUTATION = false
```

## Validation Results

Focused validation:

```text
python -m pytest tests/test_first_live_provider_operator_entrypoint_v1.py
6 passed
```

Validated behaviors:

- operator request is accepted;
- dispatch authorization artifact is loaded from replay;
- authorization freshness and single-attempt constraints are checked;
- credential availability is checked;
- execution runtime is invoked;
- execution status is returned;
- execution replay location is returned;
- operator replay evidence is recorded;
- missing confirmation fails closed;
- missing credential fails closed;
- replay reuse fails closed;
- secret material is not replayed.

## Remaining Non-Scope

This entrypoint is a runtime function, not a broad CLI command group.

Live external transport activation remains governed by the provider transport boundary.
