# First Useful AiGOL V1 Guarantees

Status: frozen baseline guarantee record.

## Core Guarantee

The first useful AiGOL baseline guarantees:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

## Proposal-Only Guarantee

LLM or cognition output remains untrusted proposal input.

It does not authorize execution, execute directly, mutate governance, bypass replay, create hidden continuation, or delegate authority.

## Governance Authority Guarantee

AiGOL remains the governance authority for validation, authorization, rejection, replay recording, and governed return construction.

The baseline does not permit worker self-authorization or LLM authorization.

## Authorization Guarantee

Execution occurs only after deterministic validation and authorization.

Invalid authorization, missing authorization, unsupported capability requests, ambiguous requests, and authority escalation attempts fail closed.

## Worker Execution Guarantee

The worker/runtime executes only bounded authorized read-only tasks.

The frozen supported capabilities are:

- `READ_ONLY_RUNTIME_INSPECTION`
- `FILESYSTEM_READ_ONLY_INSPECTION`

## Replay Guarantee

Replay remains mandatory and central.

Replay evidence remains the source of truth. Governed result summaries and replay summaries are operator-facing views derived from replay evidence; they do not replace replay or create authority.

## Boundary Guarantee

The first useful baseline remains read-only.

It does not allow filesystem writes, deletes, moves, shell execution, network execution, API execution, orchestration, agents, persistent memory, or autonomous continuation.

## Pressure Stability Guarantee

The frozen epoch pressure validation confirmed fail-closed handling for malformed requests, unsupported capabilities, replay corruption attempts, authorization failures, invalid proposal structures, replay ordering violations, repeated successful runs, repeated failed runs, replay reconstruction pressure, and filesystem boundary pressure.

## Future Evolution Guarantee

Future evolution must preserve the frozen invariant, replay centrality, authority separation, read-only baseline clarity, and fail-closed behavior before adding any new capability or domain.
