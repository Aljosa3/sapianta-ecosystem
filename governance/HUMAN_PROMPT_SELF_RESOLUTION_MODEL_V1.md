# HUMAN_PROMPT_SELF_RESOLUTION_MODEL_V1

## Status

`HUMAN_PROMPT_SELF_RESOLUTION_MODEL_STATUS = CERTIFIED`

## Purpose

This model defines the reviewed position of AiGOL-first self-resolution for
Human Prompt processing.

It is review-only and introduces no runtime behavior.

## Definition

Self-resolution is AiGOL's attempt to answer or classify a Human Prompt using
existing replay-visible and governance-visible evidence before requesting LLM
provider assistance.

Self-resolution may consult:

- replay evidence;
- replay reports;
- replay-backed explanations;
- Constitutional Memory;
- governance artifacts;
- existing cognition artifacts;
- deterministic system knowledge.

Self-resolution may not invent facts, invoke providers silently, invoke workers,
authorize execution, or mutate governance.

## Resolution Order

The certified model is:

```text
Human Prompt
↓
Prompt Artifact
↓
Self-Resolution Review
↓
Deterministic answer, deterministic intent, or fail-closed unresolved status
↓
Provider assistance only when unresolved or semantically ambiguous
```

## Legitimate Self-Resolution Cases

AiGOL may resolve directly when the prompt asks for:

- current replay status;
- operation replay explanation;
- governance artifact summary;
- Constitutional Memory citation;
- deterministic system capability description;
- existing operation report;
- explicit bounded operation using known parameters.

## Provider-Required Cases

Provider assistance may be required when the prompt asks for:

- semantic interpretation not covered by deterministic rules;
- ambiguous intent resolution;
- open-ended drafting;
- response synthesis beyond cited evidence;
- natural-language classification in unsupported languages or phrasings.

Examples currently likely to fail closed under deterministic keyword matching:

- `Kaj je namen AiGOL?`
- `Kaj zna AiGOL?`
- `Kako deluje AiGOL?`

These are not invalid prompts. They are evidence that semantic assistance is
missing.

## Authority Boundary

Self-resolution does not grant authority.

It may produce:

- direct evidence response;
- deterministic classification;
- unresolved status;
- provider assistance request recommendation.

It may not produce:

- authorization;
- worker request;
- execution request;
- governance decision beyond existing validation boundaries.

## Replay Requirements

Future implementation should record:

- prompt artifact;
- self-resolution scope;
- evidence sources checked;
- self-resolution result;
- unresolved reason when applicable;
- whether provider assistance was requested;
- downstream semantic suggestion or fail-closed result.

## Final Certification

AiGOL-first self-resolution is constitutionally valid and should precede
provider semantic assistance.
