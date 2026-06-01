# HUMAN_PROMPT_PROVIDER_GOVERNANCE_ALIGNMENT_ADR_V1

## Decision

Certify AiGOL-first self-resolution followed by provider-assisted semantics as
the correct constitutional model for Human Prompt processing.

## Context

Operational testing showed that the Human Prompt Interface accepts prompts and
enters the existing intent path, but `INTENT_CLASSIFIER_V1` relies on
deterministic keyword matching.

Natural-language prompts such as:

- `Kaj je namen AiGOL?`
- `Kaj zna AiGOL?`
- `Kako deluje AiGOL?`

can fail closed because semantic interpretation is intentionally absent from V1.

## Decision Rationale

AiGOL should first attempt to resolve prompts from existing deterministic and
replay-visible sources:

- replay;
- Constitutional Memory;
- governance artifacts;
- existing cognition artifacts;
- deterministic system knowledge.

If those sources are insufficient, AiGOL may request semantic assistance from a
provider. The provider may return proposal-like semantic evidence:

- interpretation suggestion;
- classification suggestion;
- response suggestion;
- proposal.

AiGOL must validate admissibility and preserve replay.

## Rejected Alternatives

### Provider-First Prompt Handling

Rejected.

Provider-first handling would weaken AiGOL's ability to answer from existing
governance evidence and could obscure when provider assistance was unnecessary.

### Human-Selected Binding Provider

Rejected.

The human may express preference, but AiGOL must govern provider selection to
preserve substitutability, replay, fail-closed semantics, and boundary
guarantees.

### Provider As Intent Authority

Rejected.

Provider output may suggest intent but cannot classify authoritatively.

### Provider As Conversation Authority

Rejected.

Provider output may suggest language, but AiGOL must validate and emit the
governed response artifact.

## Consequences

Future semantic assistance work should create suggestion artifacts and replay
evidence rather than provider authority.

The correct future flow is:

```text
Human Prompt
↓
AiGOL self-resolution
↓
Provider semantic assistance when needed
↓
AiGOL validation
↓
Replay-visible outcome
```

## Status

`HUMAN_PROMPT_PROVIDER_GOVERNANCE_ALIGNMENT_STATUS = CERTIFIED`
