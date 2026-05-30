# Intent Classifier Model V1

Status: constitutional model for the future Intent Classifier.

This milestone defines the role of `INTENT_CLASSIFIER` and `INTENT_CLASSIFICATION_ARTIFACT`.

It does not implement classifier runtime, classifier engine, classifier worker, classifier orchestration, autonomous routing, automatic execution, automatic provider invocation, automatic worker invocation, or correction loops.

## Core Definition

The Intent Classifier is a non-authoritative classification boundary.

It determines which canonical intent destination a Human Prompt appears to request.

It does not route by itself, and it does not perform the destination action.

## Constitutional Position

The classifier sits between:

```text
Human Prompt Evidence
```

and:

```text
Intent Routing Artifact
```

Its output is evidence for routing, not routing authority.

## Not A Governance Layer

The classifier is not:

- governance
- authorization
- execution
- worker
- provider
- memory retrieval
- proposal generation

## Valid Destination Labels

The classifier may classify into:

- `CONVERSATION`
- `CONSTITUTIONAL_MEMORY_CONSULTATION`
- `PROVIDER_PROPOSAL`
- `EXECUTION_REQUEST`

It may also fail closed when intent cannot be classified safely.

## Identity Classification

`INTENT_CLASSIFIER_IDENTITY`: `DEFINED`

Evidence:

- intent routing model defines valid destinations
- conversation position defines conversation as partial destination
- memory, provider, and execution destinations already have bounded downstream surfaces
- classifier role is now defined as non-authoritative classification evidence

## Final Classification

`INTENT_CLASSIFIER_MODEL_STATUS`: `READY_WITH_GAPS`

`INTENT_CLASSIFIER_AUTHORITY_IMPACT`: `LOW`

`INTENT_CLASSIFIER_REPLAY_VISIBILITY`: `MANDATORY`

