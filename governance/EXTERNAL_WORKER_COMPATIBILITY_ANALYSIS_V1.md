# External Worker Compatibility Analysis V1

Status: external Worker compatibility review.

## Constitutional Compatibility

Classification: `COMPATIBLE`

An external Worker can operate under:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

Evidence:

- Worker is already defined as execution-only.
- Worker receives only authorized, bounded, replay-linked execution requests.
- Worker cannot authorize, govern, propose, mutate replay, mutate governance, or expand capability scope.

## Worker Boundary Compatibility

Classification: `COMPATIBLE`

An external Worker can attach through `WORKER_ATTACHMENT_BOUNDARY_V1` without architectural modification.

Evidence:

- Worker attachment boundary already defines `AUTHORIZED_REQUEST -> WORKER_EXECUTION_REQUEST`.
- Boundary requires AiGOL authorization evidence, intact replay lineage, explicit worker identity, deterministic capability binding, and no mutation surface.

## Replay Compatibility

Classification: `COMPATIBLE`

Replay can already model:

```text
worker_identity
authorized_execution_request
worker_execution_evidence
worker_termination_record
governed_result
```

without replay redesign.

Evidence:

- `WORKER_REPLAY_MAPPING_V1` defines required append-only Worker replay stages.
- Existing read-only capability execution records request, validation, authorization, execution, and termination evidence.
- Existing replay reconstruction validates ordering and hashes.

## Authorization Compatibility

Classification: `COMPATIBLE`

An external Worker can receive only AiGOL-authorized execution requests without architectural modification.

Evidence:

- `WORKER_ATTACHMENT_BOUNDARY_V1` begins after AiGOL authorization.
- `minimal_cognition_to_execution_bridge` requires validation and authorization before execution.
- Read-only capabilities require explicit authorization artifacts before execution evidence is accepted.

## Capability Compatibility

Classification: `COMPATIBLE`

The first external Worker can operate using existing:

```text
READ_ONLY
INSPECTION
```

capability classes.

Evidence:

- `FIRST_READ_ONLY_CAPABILITY_ATTACHMENT_V1` attaches `READ_ONLY_RUNTIME_INSPECTION`.
- `SECOND_READ_ONLY_CAPABILITY_ATTACHMENT_V1` attaches `FILESYSTEM_READ_ONLY_INSPECTION`.
- `CAPABILITY_AUTHORIZATION_MAPPING_V1` requires explicit authorization and fail-closed escalation handling.

## Pressure Validation Reusability

Classification: `REUSABLE`

Existing pressure categories are reusable:

- authorization failures
- replay corruption
- replay ordering
- identity corruption
- authority escalation
- repeated operations
- boundary violations

External Worker pressure tests should mirror existing replay, authorization, and fail-closed validation patterns while adding worker identity and termination evidence checks.

