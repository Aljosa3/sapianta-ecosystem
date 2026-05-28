# Orchestration Fail-Closed Rules V1

Status: orchestration governance failure semantics only.

## Fail-Closed Principle

Orchestration ambiguity must terminate the orchestration boundary before it becomes runtime behavior.

The correct response to unclear coordination semantics is deterministic rejection, not autonomous repair.

## Fail-Closed Conditions

An orchestration boundary must fail closed if:

- the orchestration request is not explicit
- the request implies execution authority
- the request implies autonomous dispatch
- the request implies worker activation
- the request implies recursive coordination
- the request implies hidden retry behavior
- the request implies implicit continuation
- the request attempts governance mutation
- the request attempts replay mutation
- the lineage is missing or ambiguous
- the termination condition is missing
- authority separation cannot be verified

## Failure Artifact Expectations

A fail-closed orchestration disposition should remain replay-visible and include:

- failure status
- failed boundary reason
- replay lineage reference if available
- explicit non-execution statement
- explicit non-continuation statement

Failure artifacts are governance evidence. They are not retry instructions.

## Prohibited Recovery Behavior

Fail-closed orchestration must not:

- retry automatically
- dispatch a worker
- infer missing lineage
- repair governance ambiguity
- continue recursively
- create hidden execution chains
- persist orchestration memory

## Boundary Certification

Fail-closed orchestration governance preserves constitutional boundedness by stopping ambiguous coordination before it becomes runtime behavior.

