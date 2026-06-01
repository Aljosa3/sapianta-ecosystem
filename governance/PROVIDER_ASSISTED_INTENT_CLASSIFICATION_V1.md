# PROVIDER_ASSISTED_INTENT_CLASSIFICATION_V1

## Status

`PROVIDER_ASSISTED_INTENT_CLASSIFICATION_STATUS = READY`

## Purpose

This milestone implements the first provider-assisted intent classification
path.

Provider assistance is conditional. It is used only after deterministic intent
classification fails closed.

## Constitutional Invariant

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

This milestone preserves the invariant by treating provider output as semantic
suggestion evidence only.

## Runtime Surface

Implemented:

```text
aigol/runtime/provider_assisted_intent_classification.py
```

Primary runtime function:

```text
classify_intent_with_provider_assistance(...)
```

Focused validation:

```text
tests/test_provider_assisted_intent_classification_v1.py
```

## Operational Flow

```text
Human Prompt
↓
Deterministic Intent Classification
↓
If classified: use deterministic classification
↓
If failed: request provider semantic suggestion
↓
Provider returns suggested destination, reasoning, confidence
↓
AiGOL validates destination and boundaries
↓
Final Intent Classification Artifact
↓
Replay
```

## Supported Destination Validation

Provider suggestions are valid only when the suggested destination is one of:

- `CONVERSATION`
- `CONSTITUTIONAL_MEMORY_CONSULTATION`
- `PROVIDER_PROPOSAL`
- `EXECUTION_REQUEST`

Invalid, missing, ambiguous, multiple, or authority-bearing suggestions fail
closed.

## Replay Evidence

Replay records:

- deterministic classification attempt;
- deterministic failure reason when fallback is required;
- provider semantic assistance request;
- provider semantic assistance response;
- provider proposal hash;
- AiGOL governance validation artifact;
- final classification artifact;
- provider-assisted classification replay artifact.

## Boundary Guarantees

Provider suggestion is not:

- authority;
- routing;
- execution;
- authorization;
- governance;
- worker instruction.

The final classification artifact remains non-authoritative and can feed the
existing routing attachment only after AiGOL validates the provider suggestion.

## Demonstrated Case

Prompt:

```text
Kaj je namen AiGOL?
```

Current deterministic classifier:

```text
FAILED_CLOSED
```

Provider-assisted classifier with valid semantic suggestion:

```text
classification_destination = CONVERSATION
classifier_version = PROVIDER_ASSISTED_INTENT_CLASSIFICATION_V1
```

## Fail-Closed Cases

The implementation fails closed on:

- provider unavailable;
- malformed provider response;
- invalid suggested destination;
- ambiguous suggestion;
- authority-bearing provider response;
- corrupt replay evidence;
- append-only replay violation.

## Final Classification

```text
PROVIDER_ASSISTED_INTENT_CLASSIFICATION_STATUS = READY
```
