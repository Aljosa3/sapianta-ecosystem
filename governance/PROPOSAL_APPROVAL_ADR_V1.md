# Proposal Approval ADR V1

Status: accepted with gaps.

## Context

AiGOL has foundations for conversation, resolution strategy, proposal runtime, proposal lifecycle, and conversation-to-proposal flow.

The remaining boundary is approval between proposal creation and future execution.

## Decision

Adopt a minimal human-only approval model:

```text
INSPECTED
-> PENDING_APPROVAL
-> APPROVED or REJECTED or EXPIRED
```

Only a human operator may approve a proposal.

Final foundation status:

```text
PROPOSAL_APPROVAL_FOUNDATION_STATUS = READY_WITH_GAPS
```

## Rationale

Approval is the explicit human boundary between proposal evidence and future execution eligibility.

Providers cannot approve because provider output is proposal evidence only.

Workers cannot approve because workers execute only authorized future requests.

Replay cannot approve because replay records and reconstructs evidence.

## Accepted Claims

AiGOL may claim:

```text
The minimal proposal approval boundary is architecturally defined.
```

AiGOL may also claim:

```text
Proposal approval is human-only, replay-visible, non-executing evidence.
```

## Rejected Claims

AiGOL must not claim:

- approval runtime implementation;
- execution approval by provider;
- execution approval by worker;
- approval inferred from replay;
- approval without inspection;
- approval that directly dispatches execution;
- approval that mutates governance.

## Consequences

Future implementation must preserve:

- proposal inspection before approval;
- explicit human decision;
- proposal hash continuity;
- inspection hash continuity;
- non-execution flags;
- replay reconstruction;
- fail-closed missing approval handling.

Execution request derivation and worker execution remain separate future certifications.
