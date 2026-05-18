# GOVERNED_INTENT_INTERPRETATION_LAYER_V1

This milestone introduces the first bounded natural-language ingress layer for
the governed runtime.

## Scope

- supports only:
  - `GOVERNANCE_ARTIFACT_CREATION`
  - `RUNTIME_VALIDATION_REQUEST`
  - `REPLAY_INSPECTION_REQUEST`
- generates deterministic artifact candidates
- returns explicit replay-visible previews
- requires human confirmation before any invocation handoff

## Boundaries

- no autonomous planning or execution
- no hidden reasoning, continuation, orchestration, or retries
- no prompt-to-shell path
- no direct Codex invocation
- no governance rewrite

Unknown, ambiguous, escalatory, or multi-step requests fail closed.
