# HUMAN_PROMPT_INTERFACE_ADR_V1

## Decision

Certify the Human Prompt Interface as ready for implementation review.

## Context

AiGOL can now execute, inspect replay, verify replay, report replay statistics, and produce replay-backed explanations.

The missing operator-facing boundary is a direct Human Prompt interface.

## Decision Rationale

The Human Prompt Interface does not require new constitutional architecture.

Existing certified components already provide:

- intent classification;
- routing model;
- provider proposal boundary;
- authorization boundary;
- worker execution boundary;
- replay verification;
- replay-backed explanations.

The implementation should create a replay-visible prompt artifact and connect it to these paths.

## Rejected Alternatives

### Provider-First Prompt Handling

Rejected.

Many prompts can be answered from replay, Constitutional Memory, or deterministic operation parameters without a provider.

### Direct Human-To-Worker Path

Rejected.

Workers may receive only governed authorized worker requests.

### Human Prompt As Authorization

Rejected.

Human Prompt expresses intent; it does not authorize execution by itself.

## Consequence

The next implementation can focus narrowly on:

```text
Human Prompt
↓
Prompt Artifact
↓
Intent Classification
↓
Existing governed paths
↓
Replay
↓
Explanation
```

without adding providers, workers, authority models, or replay models.
