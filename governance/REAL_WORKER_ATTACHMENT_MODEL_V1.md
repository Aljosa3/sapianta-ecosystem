# Real Worker Attachment Model V1

Status: model-only real worker attachment definition.

This milestone defines how a real worker may connect to AiGOL while preserving the frozen invariant:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

This milestone does not implement a real worker, filesystem mutation, shell execution, API execution, network execution, orchestration, memory, capability expansion, execution expansion, or runtime mutation.

## Worker Role

A real worker is an execution-only participant.

It may receive an authorized execution request and return bounded execution evidence. It may not authorize, govern, expand capability scope, mutate replay, mutate governance, or continue implicitly.

## Attachment Flow

The model-only flow is:

```text
AUTHORIZED_REQUEST
-> Worker identity envelope
-> Worker attachment boundary validation
-> WORKER_EXECUTION_REQUEST
-> Worker executes bounded authorized capability
-> Worker result evidence
-> Worker termination evidence
-> Replay-visible governed result
```

## Boundary Definition

The worker attachment boundary begins after AiGOL authorization.

The worker never receives raw LLM proposal authority. It receives only a governed execution request that is already validated, authorized, bounded, and replay-linked.

## Required Model Components

The real worker attachment model requires:

- worker identity model
- worker attachment boundary
- capability binding model
- replay mapping
- isolation model
- fail-closed failure handling

## Capability Constraint

The first real worker attachment may bind only frozen read-only capabilities:

- `READ_ONLY_RUNTIME_INSPECTION`
- `FILESYSTEM_READ_ONLY_INSPECTION`

No mutation, shell, network, API, orchestration, agent, memory, or new capability surface is introduced by this model.

## Success Definition

Success for the model is a clear worker attachment contract for future implementation.

Success is not a working external worker.
