# PROVIDER_ASSISTED_INTENT_CLASSIFICATION_REVIEW_V1

## Status

`PROVIDER_ASSISTED_INTENT_CLASSIFICATION_STATUS = READY_WITH_GAPS`

## Purpose

This review determines whether an LLM provider may assist intent classification
without becoming the intent authority.

This milestone is review-only.

## Current Baseline

`INTENT_CLASSIFIER_V1` supports four destinations:

- `CONVERSATION`
- `CONSTITUTIONAL_MEMORY_CONSULTATION`
- `PROVIDER_PROPOSAL`
- `EXECUTION_REQUEST`

V1 uses deterministic bounded marker rules and explicitly does not use LLM,
provider, worker, or memory-based classification.

## Reviewed Model

The compatible future model is:

```text
Human Prompt
↓
Deterministic Intent Classifier
↓
If unresolved or ambiguous, provider semantic assistance request
↓
Provider returns classification suggestion
↓
AiGOL validates suggestion against allowed destinations and boundaries
↓
AiGOL emits accepted classification artifact or fail-closed evidence
```

## Provider Role

Provider may return:

- destination suggestion;
- confidence or ambiguity note;
- natural-language interpretation;
- reason summary;
- evidence-free semantic proposal.

Provider may not return:

- binding classification;
- routing command;
- governance decision;
- authorization;
- worker instruction;
- execution request.

## AiGOL Role

AiGOL must:

- validate destination is one of the canonical destinations;
- reject multiple conflicting destinations unless a future artifact explicitly
  supports bounded ambiguity;
- reject unsupported or provider-specific destinations;
- record provider request and response;
- record accepted or rejected classification evidence;
- fail closed on unresolved ambiguity.

## Boundary Assessment

Provider-assisted classification is compatible with:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

because the provider proposes semantic interpretation while AiGOL governs
admissibility.

## Implementation Gaps

Before implementation, AiGOL needs:

- provider classification suggestion artifact;
- semantic assistance replay model;
- validation rules for provider-suggested destinations;
- fail-closed rules for ambiguous, unsupported, malformed, or conflicting
  suggestions;
- replay reconstruction for accepted and rejected suggestions.

## Final Classification

```text
PROVIDER_ASSISTED_INTENT_CLASSIFICATION_STATUS = READY_WITH_GAPS
```

Provider-assisted intent classification is constitutionally compatible but not
yet implementation-ready without suggestion artifacts and replay validation.
