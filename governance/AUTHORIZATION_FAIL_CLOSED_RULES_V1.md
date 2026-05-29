# Authorization Fail-Closed Rules V1

Status: authorization failure semantics only.

## Fail-Closed Principle

Authorization ambiguity must stop the authorization lifecycle.

The correct response to unclear authority is deterministic failure, not implicit approval.

## Rejection Conditions

Authorization should be `REJECTED` when the request is understandable but constitutionally inadmissible.

Examples:

- request exceeds bounded scope
- request lacks required admissibility criteria
- request conflicts with orchestration containment
- request conflicts with constitutional isolation
- request conflicts with frozen baseline guarantees

## Failure Conditions

Authorization must become `FAILED` when trust in the disposition cannot be preserved.

Failure conditions include:

- ambiguous authorization request
- invalid authorization lineage
- replay discontinuity
- authority escalation attempt
- self-authorization attempt
- recursive authorization attempt
- hidden authority chain
- governance bypass attempt
- missing validation evidence
- invalid lifecycle transition

## Prohibited Authorization Behavior

Authorization must not:

- self-authorize
- recursively authorize
- infer missing approval
- create hidden authority chains
- bypass governance
- repair ambiguity autonomously
- retry automatically
- delegate constitutional authority

## Failure Artifact Expectations

A failed authorization artifact should preserve:

- failure status
- failure reason
- lifecycle state
- lineage reference if available
- explicit non-authorization statement
- explicit non-execution statement

Failure artifacts are replay evidence, not retry instructions.

