# HUMAN_PROMPT_INTERFACE_REVIEW_V1

## Status

`HUMAN_PROMPT_INTERFACE_STATUS = READY_FOR_IMPLEMENTATION`

## Purpose

This milestone reviews how a human should interact with AiGOL directly.

The long-term goal is to move from:

```text
Human
↓
ChatGPT
↓
Prompt
↓
Copy/Paste
↓
AiGOL
```

to:

```text
Human
↓
AiGOL
↓
Governed Cognition
↓
Governed Execution
↓
Replay
↓
Explanation
```

This milestone is review and certification only.

It does not implement a Human Prompt CLI, new runtime, provider, worker, replay model, governance layer, or authority model.

## Reviewed Baseline

Reviewed current capabilities:

- `INTENT_CLASSIFIER_V1`;
- `INTENT_ROUTING_MODEL_V1`;
- `CONVERSATION_POSITION_REVIEW_V1`;
- `HUMAN_REQUEST_PROVIDER_INDEPENDENCE_V1`;
- `CONSTITUTIONAL_MEMORY_ACCESS_PATH_V1`;
- `AIGOL_OPERATOR_INTERFACE_EXTENSION_V1`;
- `OPERATION_REPLAY_LEDGER_AND_REPORTING_V1`;
- `REPLAY_BACKED_OPERATION_EXPLANATIONS_V1`.

## Answers

### 1. What Is A Human Prompt?

A Human Prompt is operator-originated intent expressed in natural language or bounded command-like text.

It is not:

- provider output;
- worker command;
- authorization;
- governance decision;
- execution request by itself.

### 2. What Enters AiGOL From The Operator?

The operator should submit:

- prompt text;
- optional explicit target or scope;
- optional mode hint;
- optional workspace or runtime root;
- operator-visible metadata for replay.

The initial input must become replay-visible before provider, worker, or authorization boundaries are crossed.

### 3. How Is Intent Determined?

Intent should be determined by the existing deterministic intent classification model first.

Current destinations are:

- `CONVERSATION`;
- `CONSTITUTIONAL_MEMORY_CONSULTATION`;
- `PROVIDER_PROPOSAL`;
- `EXECUTION_REQUEST`.

Ambiguous or unknown intent must fail closed or request clarification in a future review.

### 4. When Is A Provider Required?

A provider is required when the prompt needs proposal generation beyond deterministic AiGOL knowledge.

Examples:

- generating a new proposal from open-ended human language;
- transforming ambiguous user goals into a candidate proposal;
- drafting content not already available from replay or Constitutional Memory.

The provider remains proposal-only.

### 5. When Is A Provider Unnecessary?

A provider is unnecessary when AiGOL can answer or act from existing deterministic evidence.

Examples:

- replay report;
- replay verification;
- replay-backed explanation;
- Constitutional Memory citation lookup;
- deterministic governed operation with explicit worker, operation, target, and content.

### 6. How Does Human Prompt Become A Governed Proposal?

The reviewed path is:

```text
Human Prompt
↓
Prompt Artifact
↓
Intent Classification
↓
Provider Proposal if required
↓
Proposal Envelope
↓
Governance/Authorization Boundary
```

The Human Prompt does not itself authorize execution.

### 7. How Does Human Prompt Remain Replay-Visible?

The prompt should be persisted as a replay-visible prompt artifact with:

- prompt id;
- prompt text hash;
- operator metadata;
- classification result;
- routing result;
- provider requirement decision;
- downstream operation id or explanation id.

### 8. How Does Human Prompt Connect To Explanations?

The prompt should link to:

- intent artifact;
- routing artifact;
- proposal id when a provider is used;
- authorization id when execution occurs;
- operation id;
- replay verification;
- replay-backed explanation.

This allows AiGOL to answer:

```text
What happened?
Why did it happen?
Why was it authorized?
Why should the result be trusted?
```

## Review Conclusion

Human Prompt Interface is ready for implementation review.

The missing piece is not constitutional architecture. The missing piece is a bounded CLI surface that creates a replay-visible Human Prompt artifact and routes it into already-certified paths.

## Final Classification

```text
HUMAN_PROMPT_INTERFACE_STATUS = READY_FOR_IMPLEMENTATION
```
