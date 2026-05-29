# Cognition Execution Fail-Closed Rules V1

Status: bridge fail-closed rules.

## Fail-Closed Principle

Cognition ambiguity must not become execution authority.

The bridge must reject unclear, unsupported, unauthorized, or boundary-violating cognition output.

## Fail-Closed Conditions

The bridge fails closed on:

- ambiguous intent
- missing capability target
- unsupported capability
- unauthorized request
- boundary violation
- malformed cognition output
- replay discontinuity
- hidden continuation attempt
- mutation intent
- cognition self-authorization

## Prohibited Recovery

The bridge must not:

- infer missing capability
- infer authorization
- retry automatically
- select a different capability
- escalate to broader execution
- create hidden continuation
- execute directly

