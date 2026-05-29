# Execution Fail-Closed Rules V1

Status: execution failure semantics only.

## Fail-Closed Principle

Execution ambiguity must stop the lifecycle.

The correct response to unclear execution semantics is deterministic failure, not autonomous recovery or continuation.

## Fail-Closed Conditions

Execution must fail closed on:

- ambiguous execution request
- invalid lifecycle transition
- authority escalation attempt
- replay discontinuity
- hidden continuation
- invalid execution lineage
- missing authorization reference
- governance bypass attempt
- constitutional baseline mutation attempt
- orchestration dispatch implication
- filesystem authority implication
- network authority implication
- autonomous planning implication

## Failure Artifact Expectations

A fail-closed execution artifact should remain replay-visible and include:

- failure status
- failed boundary reason
- lifecycle state at failure
- lineage reference if available
- explicit non-continuation statement
- explicit non-authority statement

Failure artifacts are evidence, not retry instructions.

## Prohibited Recovery Behavior

Fail-closed execution must not:

- retry automatically
- infer missing lineage
- repair authorization ambiguity
- continue implicitly
- dispatch workers
- invoke orchestration
- mutate constitutional baseline
- persist hidden state

## Freeze Compatibility

Fail-closed execution preserves the frozen constitutional baseline by preventing execution semantics from becoming authority, orchestration, persistence, or autonomous planning.

