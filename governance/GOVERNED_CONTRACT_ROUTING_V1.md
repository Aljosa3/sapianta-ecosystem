# GOVERNED_CONTRACT_ROUTING_V1

## Scope

This milestone implements minimal deterministic governed contract routing for AiGOL.

The router connects:

`contract -> authorization -> lineage attachment -> session continuity`

It exposes only:

- `route_authorized_contract(...)`

## Routing Result

Routing evidence contains:

- `routing_id`
- `contract_id`
- `session_id`
- `authorization_id`
- `status`
- `reason`
- `attached`
- `evidence_hash`
- `created_at`

Allowed statuses are:

- `ROUTED`
- `REJECTED`

## Guarantees

- Routing only.
- No provider execution introduced.
- No orchestration introduced.
- No autonomous runtime introduced.
- No LLM integration introduced.
- Deterministic contract to authorization to session lineage binding.
- Fail-closed routing validation.
- Replay-visible routing evidence.
- Rejected routes remain visible.

## Non-Goals

- Orchestration.
- Autonomous execution.
- Provider execution.
- Workflow engine.
- LLM integration.
- Semantic reasoning.
- Planning system.
- Retries.
- Async execution.
- Provider state mutation.
- Authorization issuance.

## Boundary

The router validates an already-authorized contract and records routing evidence. It does not authorize, execute, infer intent, invoke providers, create workflows, schedule work, or mutate provider state.

## Certification

`GOVERNED_CONTRACT_ROUTING_V1` certifies deterministic routing evidence and fail-closed routing validation for governed contract, authorization, and session lineage binding without adding execution authority or provider capability.
