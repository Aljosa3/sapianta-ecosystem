# FIRST_REAL_CONVERSATIONAL_USAGE_ADR_V1

## Decision

Record the first real conversational usage epoch as evidence that prompt ingress
is operational, but full conversational use is not yet complete through the CLI.

## Context

The operator used:

```text
aigol prompt submit
```

against 12 real prompts across capability, governance, replay, recent-operation,
ambiguous, incomplete, misleading, and unsupported categories.

## Observed Reality

Prompt ingress works.

Replay references are produced.

Provider, worker, and execution boundaries are preserved.

Conversational response is not returned.

## Decision Rationale

This milestone should not introduce architecture changes.

The correct outcome is evidence-based prioritization rather than more design.

## Rejected Alternatives

### Add A New Conversational CLI

Rejected for this milestone.

The evidence points to extending the existing prompt surface, not creating a new
operator interface.

### Add New Workers

Rejected.

The bottleneck is response activation, not worker capability.

### Add New Providers

Rejected.

The bottleneck is connecting existing provider-assisted conversation behavior to
operator prompt flow, not provider diversity.

### Expand Governance

Rejected.

The existing invariant remains sufficient.

## Consequence

Future work should focus on:

```text
Human Prompt
↓
Provider-Assisted Conversation Runtime
↓
Replay-Backed Response
```

without changing authority or execution boundaries.
