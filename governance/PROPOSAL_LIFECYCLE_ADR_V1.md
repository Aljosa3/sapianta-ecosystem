# Proposal Lifecycle ADR V1

Status: accepted with gaps.

## Context

The conversational runtime is certified as an operational human conversational entry point with gaps.

The next major boundary is the transition from conversation into a governed proposal lifecycle that can later support worker execution without granting providers authority.

Existing constitutional framing already preserves:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

This ADR defines the minimal lifecycle foundation required before runtime implementation.

## Decision

Adopt a minimal replay-safe proposal lifecycle with these states:

```text
CREATED
INSPECTED
APPROVED
REJECTED
EXPIRED
EXECUTED
REPLAY_RECONSTRUCTED
```

Final foundation status:

```text
PROPOSAL_LIFECYCLE_FOUNDATION_STATUS = READY_WITH_GAPS
```

## Rationale

The lifecycle creates a clean bridge between conversational intent and future governed execution.

It separates:

- conversation responses from proposal artifacts;
- proposal artifacts from execution requests;
- execution requests from worker tasks;
- governance artifacts from operational lifecycle evidence.

This separation prevents provider output from becoming authority.

## Actor Model

AiGOL creates, inspects, rejects, expires, and derives governed execution request candidates.

Human explicitly approves inspected proposals.

Provider contributes proposal evidence only.

Worker executes only authorized future execution requests.

Replay records and reconstructs lifecycle evidence only.

## Accepted Claims

AiGOL may claim:

```text
A minimal replay-safe proposal lifecycle foundation is defined.
```

AiGOL may also claim:

```text
The lifecycle preserves provider isolation and prepares a governed bridge toward future worker execution.
```

## Rejected Claims

AiGOL must not claim:

- proposal lifecycle runtime implementation;
- worker execution implementation;
- execution authorization implementation;
- provider authority;
- automatic proposal approval;
- direct conversation-to-worker execution;
- replay mutation authority.

## Consequences

Future implementation work must preserve this state model, actor model, approval boundary, fail-closed behavior, and replay reconstruction discipline.

Any runtime implementation must be separately certified.

Any worker execution integration must be separately certified.

Any expansion of proposal types, risk classes, or transition authority must be separately governed.
