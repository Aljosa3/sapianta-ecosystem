# Intent Classification Reconstruction V1

Status: reconstructed current intent architecture.

## Current Intent Destinations

AiGOL currently has evidence for four destination concepts.

### Conversation

`Conversation` is not yet a clearly defined constitutional destination.

Evidence exists for operator-facing result presentation and usage guidance, but there is no explicit conversation-only lifecycle, no conversation replay contract, and no defined boundary separating conversational answer from provider proposal or memory consultation.

Classification: `PARTIAL`

### Constitutional Memory Consultation

`Memory Consultation` is now explicitly defined and minimally implemented.

Evidence:

- `CONSTITUTIONAL_MEMORY_RETRIEVAL_MODEL_V1`
- `CONSTITUTIONAL_MEMORY_ACCESS_PATH_V1`
- `CONSTITUTIONAL_MEMORY_ACCESS_BOUNDARY_V1`

It returns `REFERENCE_RESULT` citation bundles and replay-visible retrieval evidence.

Classification: `DEFINED`

### Provider Proposal

`Provider Proposal` is explicitly defined.

Evidence:

- provider is proposal source only
- raw provider output is captured
- normalized proposal artifacts enter AiGOL governance
- provider never receives execution, authorization, governance, or replay authority

Classification: `DEFINED`

### Execution Request

`Execution Request` is explicitly defined for bounded read-only execution.

Evidence:

- cognition output is untrusted execution request input
- proposal normalization validates supported capability targets
- authorization is mandatory
- worker executes only authorized bounded requests

Classification: `DEFINED`

## Current Missing Piece

The missing piece is:

```text
Human Prompt
-> deterministic intent classification artifact
-> selected governed destination
```

No current artifact defines this classifier as a first-class replay-visible stage.

## Existence Classification

`INTENT_CLASSIFICATION_EXISTENCE`: `PARTIAL`

Intent destinations exist. Classification into those destinations remains undefined.

