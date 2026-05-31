# GOVERNED_WORKER_AUTHORIZATION_ADR_V1

## Status

Accepted.

## Context

`PROVIDER_WORKER_DOMAIN_COMPATIBILITY_V1` certified that provider proposals can
approach worker domains only through governance and authorization boundaries.

The remaining question is where execution authority begins.

## Decision

Execution authority begins only at a governed authorization boundary that emits
replay-visible `AUTHORIZED` evidence for a specific worker target, execution
scope, and capability binding.

## Rationale

Provider output, proposal evidence, cognition, replay, memory response, and
worker identity are all non-authorizing surfaces.

Only governance can authorize worker execution.

Replay records authorization but does not create authorization.

Worker execution begins only downstream of authorization.

## Consequences

Authorization requires replay-visible evidence.

Missing, malformed, expired, mismatched, or ambiguous authorization fails
closed.

Worker self-authorization remains forbidden.

Provider authority cannot become worker authority.

## Non-Goals

This ADR does not implement:

- execution runtime
- worker runtime
- dispatch runtime
- orchestration
- planning
- reflection
- autonomous behavior

## Certification

GOVERNED_WORKER_AUTHORIZATION_STATUS = CERTIFIED
