# Resolution Strategy ADR V1

Status: accepted with gaps.

## Context

AiGOL can now answer conversational prompts through deterministic self-resolution and provider-assisted responses.

The missing foundation is an explicit replay-safe model for deciding which source of truth should be used for a prompt.

## Decision

Adopt a provider-neutral Resolution Strategy foundation with these source categories:

```text
SELF_RESOLUTION
CONSTITUTIONAL_MEMORY
GOVERNANCE
REPLAY
PROVIDER
WORKER
COMBINED
```

Final foundation status:

```text
RESOLUTION_STRATEGY_FOUNDATION_STATUS = READY_WITH_GAPS
```

## Rationale

The strategy model makes source choice explicit before AiGOL answers, escalates, or creates proposal candidates.

It preserves AiGOL-first resolution while allowing provider assistance only when deterministic or evidence-backed sources are insufficient.

It also prepares clean integration with Proposal Lifecycle by identifying when a prompt requires future governed action rather than a conversational response.

## Source Precedence

Default precedence is:

```text
REPLAY
GOVERNANCE
CONSTITUTIONAL_MEMORY
SELF_RESOLUTION
PROVIDER
WORKER
COMBINED
```

The precedence is safety-oriented. Direct evidence and governance records are preferred before semantic assistance.

## Provider Decision

Provider assistance is allowed for semantic interpretation and response synthesis.

Provider assistance is rejected as a source of authority for:

- replay truth;
- governance truth;
- constitutional authority;
- approval;
- authorization;
- worker execution permission.

## Proposal Lifecycle Integration

When strategy selection detects future action, worker evidence need, or approval-sensitive capability, it should defer to Proposal Lifecycle.

Resolution Strategy does not approve proposals or create execution requests.

## Rejected Alternatives

Provider-first resolution is rejected because it would bypass AiGOL-first evidence handling.

Implicit source selection is rejected because replay would not show why a source was trusted.

Direct conversation-to-worker execution is rejected because Proposal Lifecycle and governed execution request handling must mediate future execution.

## Consequences

Future implementation must create replay-visible strategy selection evidence.

Future routing must preserve source precedence, provider boundaries, and fail-closed behavior.

Future proposal integration must treat strategy selection as evidence, not approval.

This ADR does not implement runtime behavior.
