# PROVIDER_ASSISTED_INTENT_CLASSIFICATION_ADR_V1

## Decision

Implement provider-assisted intent classification as a conditional fallback
around the existing deterministic classifier.

## Context

`INTENT_CLASSIFIER_V1` intentionally uses deterministic bounded marker rules.
This preserves replay-safe behavior but fails closed on semantically clear
natural-language prompts outside the marker set, including:

```text
Kaj je namen AiGOL?
Kaj zna AiGOL?
Kako deluje AiGOL?
```

`HUMAN_PROMPT_PROVIDER_GOVERNANCE_ALIGNMENT_REVIEW_V1` certified AiGOL-first
self-resolution followed by provider-assisted semantics as the correct
constitutional model.

## Decision Rationale

The smallest safe implementation is:

```text
Deterministic Classifier
↓
Provider suggestion only if deterministic classifier fails closed
↓
AiGOL validation
↓
Final classification artifact
```

This preserves the existing deterministic classifier and prevents provider
suggestions from becoming authority.

## Rejected Alternatives

### Provider-First Classification

Rejected.

Provider-first classification would bypass deterministic self-resolution and
weaken the AiGOL-first model.

### Replacing Deterministic Classifier

Rejected.

`INTENT_CLASSIFIER_V1` remains useful and replay-safe. The provider-assisted
runtime wraps it instead of replacing it.

### Provider Routing

Rejected.

Provider output is a suggestion only. Routing remains a separate AiGOL artifact
created by the existing routing attachment.

### Provider Execution Or Authorization

Rejected.

Intent classification cannot authorize execution or invoke workers.

## Consequences

Natural-language prompts outside deterministic keyword coverage can now be
classified when a provider returns a valid suggestion and AiGOL validates it.

Provider failure, invalid suggestion, ambiguity, malformed response, or
authority-bearing output fails closed.

## Status

`PROVIDER_ASSISTED_INTENT_CLASSIFICATION_STATUS = READY`
