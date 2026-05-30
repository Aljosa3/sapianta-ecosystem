# Intent Classifier Fail-Closed Rules V1

Status: fail-closed rules for Intent Classifier.

## Required Fail-Closed Conditions

The classifier must fail closed on:

- unknown intent
- ambiguous intent
- multiple valid intents
- missing destination
- invalid destination
- classification failure
- missing prompt reference
- hidden context
- non-replay-visible input
- authority-bearing output
- execution-bearing output

## Ambiguity

Ambiguity must not be resolved by guessing.

Ambiguity produces:

- `FAILED_CLOSED`
- ambiguity evidence
- no destination action
- no provider invocation
- no memory retrieval
- no execution request
- no authorization

## Multiple Valid Intents

If a prompt could classify into multiple destinations and no deterministic tie-breaker exists, the classifier must fail closed.

## No Silent Fallback

The classifier must not silently fallback to:

- conversation
- provider proposal
- memory consultation
- execution request

## No Correction Loop

Classifier failure does not introduce correction loops.

A correction loop requires a separate governed model.

