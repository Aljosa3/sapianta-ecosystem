# Intent Classifier Gaps V1

Status: gap analysis before classifier implementation.

## Critical Gaps

Before implementation, AiGOL needs:

- executable `INTENT_CLASSIFICATION_ARTIFACT` schema
- deterministic classification vocabulary
- runtime fail-closed ambiguity handling
- replay persistence contract
- routing handoff contract
- proof classifier output cannot authorize or execute

## Important Gaps

Important but not strictly part of model definition:

- conversation-only lifecycle completion
- operator-facing classification summary
- classification pressure validation
- deterministic examples catalog
- invalid-input test suite

## Optional Gaps

Should not drive implementation early:

- confidence scoring
- classifier tuning
- memory-assisted classification
- provider-assisted classification
- bounded correction loop

## Readiness

`INTENT_CLASSIFIER_MODEL_STATUS`: `READY_WITH_GAPS`

The model is ready for implementation review, not runtime implementation.

