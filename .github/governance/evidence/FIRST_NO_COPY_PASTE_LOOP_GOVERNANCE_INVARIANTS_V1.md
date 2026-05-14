# First No-Copy/Paste Loop Governance Invariants v1

## Frozen Governance Invariants

`CHATGPT != GOVERNANCE`

ChatGPT-facing input remains an interaction surface. It does not become governance authority.

`NATURAL_LANGUAGE != EXECUTION_AUTHORITY`

Natural language remains governance input. It does not grant runtime authority or provider authority.

`PROPOSAL != EXECUTION`

Envelope proposals remain bounded governance artifacts. They are not executed actions by themselves.

`PROVIDER != GOVERNANCE`

Providers remain bounded execution workers. They do not mutate governance decisions or replay semantics.

`LOOP != ORCHESTRATION`

The loop transports one governed request through one bounded pass and returns one response payload. It does not plan, route, retry, fallback, schedule, recurse, or continue autonomously.

## Frozen Operational Invariants

- no autonomous continuation
- no recursive execution
- no orchestration
- no retries
- no adaptive routing
- no hidden execution
- no scheduling
- no provider self-selection
- no hidden capability escalation
- no memory mutation

## Fail-Closed Requirement

If request lineage, bridge binding, session binding, provider identity, invocation identity, result lineage, replay identity, response delivery, or evidence completeness is invalid, the loop must block completion and emit deterministic evidence.
