# GOVERNED_EXECUTION_CONTRACT_V1

## Scope

This milestone introduces the first minimal governed execution contract model for AiGOL.

The contract model supports only:

- declarative requested provider operations;
- bounded execution intent structure;
- deterministic provider authorization;
- session lineage binding;
- replay-visible contract and attachment evidence.

## Contract Fields

The execution contract contains only:

- `contract_id`
- `created_at`
- `requested_operations`
- `allowed_providers`
- `session_id`
- `status`
- `evidence_hash`

Allowed statuses are:

- `CREATED`
- `VALIDATED`
- `REJECTED`
- `ATTACHED`

## Requested Operations

Each requested operation contains only:

- `provider`
- `operation`
- `operation_id`
- `created_at`

Operation ordering is deterministic and append-only by operation identity and creation order.

## Allowed Providers

Contracts may authorize only:

- `readonly_filesystem_provider`
- `readonly_http_get_provider`
- `metadata_inspection_provider`

## Guarantees

- Execution contract only.
- No execution authority introduced.
- Deterministic contract validation.
- Fail-closed provider authorization.
- Fail-closed unsupported operation handling.
- Replay-visible contract evidence.
- Replay-visible attachment evidence.
- Immutable attachment semantics.
- Deterministic lineage reconstruction.
- Local-only validation.

## Non-Goals

- LLM integration.
- Semantic reasoning.
- Orchestration.
- Planning.
- Async runtime.
- Concurrent execution.
- Autonomous recovery.
- Workflow graphs.
- Memory systems.
- Distributed execution.
- Tool autonomy.
- Retries.
- Provider execution.
- Execution scheduling.

## Boundary

Execution contracts are intent declarations, governance artifacts, and replay-visible lineage objects. They are not planners, executors, workflows, autonomous agents, provider invokers, or execution authority.

## Certification

`GOVERNED_EXECUTION_CONTRACT_V1` certifies deterministic execution contract validation, replay-visible contract evidence, fail-closed provider authorization, immutable attachment semantics, and no orchestration or autonomous runtime.
