# Intent Classifier V1

Status: first minimal implemented Intent Classifier.

This milestone implements the approved minimal scope:

```text
Human Prompt
-> Intent Classifier
-> Intent Classification Artifact
-> Replay
```

It does not implement routing, provider invocation, worker invocation, execution, memory retrieval, governance decisions, authorization decisions, autonomous routing, autonomous execution, or correction loops.

## Runtime Surface

Implemented runtime file:

```text
aigol/runtime/intent_classifier.py
```

Implemented tests:

```text
tests/test_intent_classifier_v1.py
```

## Supported Destinations

The classifier supports only:

- `CONVERSATION`
- `CONSTITUTIONAL_MEMORY_CONSULTATION`
- `PROVIDER_PROPOSAL`
- `EXECUTION_REQUEST`

No additional destination exists in V1.

## Classification Method

V1 uses deterministic bounded marker rules.

It does not use:

- LLM classification
- provider classification
- worker classification
- memory-based classification
- hidden context

## Output

V1 emits `INTENT_CLASSIFICATION_ARTIFACT` with:

- artifact id
- human request reference
- classification destination
- classification reason
- classifier version
- classification timestamp
- replay reference
- ambiguity status
- artifact hash

Invalid or ambiguous cases emit `FAILED_CLOSED` evidence.

## Final Classification

`INTENT_CLASSIFIER_STATUS`: `READY_WITH_CONSTRAINTS`

`INTENT_CLASSIFIER_AUTHORITY_STATUS`: `PRESERVED`

`INTENT_CLASSIFIER_REPLAY_STATUS`: `READY`

