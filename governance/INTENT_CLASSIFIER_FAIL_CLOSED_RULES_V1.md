# Intent Classifier Fail-Closed Rules V1

Status: fail-closed rules for implemented Intent Classifier V1.

## Fail-Closed Conditions

The classifier fails closed on:

- unknown intent
- ambiguous intent
- multiple destination matches
- missing prompt
- invalid destination
- missing destination
- artifact corruption
- replay corruption
- append-only replay collision
- replay ordering mismatch

## Failure Artifact

Failure emits an `INTENT_CLASSIFICATION_ARTIFACT` with:

- `classification_status`: `FAILED_CLOSED`
- `classification_destination`: null
- failure reason
- classifier version
- replay reference
- artifact hash

## No Fallback

The classifier does not:

- default unknown prompts to conversation
- guess between destinations
- retry automatically
- route after failure
- invoke downstream destinations after failure

## Invalid Output Protection

Artifacts containing authority-bearing or execution-bearing fields are invalid and fail closed during validation.

