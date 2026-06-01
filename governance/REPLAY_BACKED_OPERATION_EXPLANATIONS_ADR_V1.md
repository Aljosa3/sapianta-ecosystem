# REPLAY_BACKED_OPERATION_EXPLANATIONS_ADR_V1

## Decision

Add deterministic replay-backed operation explanations to the existing replay CLI.

## Context

AiGOL can execute, inspect, verify, and report governed operations.

The operator still had to interpret mostly raw replay status and statistics.

## Decision Rationale

The next useful step is not new execution capability.

It is the ability to explain replay evidence clearly enough for an operator to understand:

- what happened;
- why it happened;
- why it was authorized;
- why the result should be trusted.

## Implementation Boundary

The explanation command is:

```text
aigol replay explain --operation-id <id>
```

It uses existing replay reconstruction and verification only.

## Rejected Alternatives

### Human Prompt CLI

Rejected for this milestone.

The explanation output is designed to be reusable by a future Human Prompt CLI, but no such CLI is introduced.

### Provider-Assisted Explanation

Rejected.

Explanations must be deterministic and replay-backed.

### New Replay Model

Rejected.

Existing replay evidence is sufficient for successful operation explanations.

## Consequence

AiGOL can now provide an operator-facing natural-language explanation for verified governed operations without manual replay inspection.
