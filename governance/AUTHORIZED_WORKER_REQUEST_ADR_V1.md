# AUTHORIZED_WORKER_REQUEST_ADR_V1

## Status

Accepted.

## Context

`MINIMAL_GOVERNED_WORKER_AUTHORIZATION_RUNTIME_V1` creates governed
authorization artifacts but intentionally does not execute, dispatch, or invoke
workers.

The next model boundary is the legal handoff object that a worker may receive.

## Decision

Define `AUTHORIZED_WORKER_REQUEST` as the minimal governed object a worker may
legally receive.

The request is derived from a valid authorization artifact but is not the raw
authorization artifact itself.

## Rationale

Workers must not receive raw provider output, raw proposals, or raw
authorization artifacts.

A separate authorized request object prevents authority confusion and makes the
handoff replay-visible.

## Consequences

Worker execution remains impossible at this milestone.

The next runtime milestone may implement the request object only if it preserves
the certified schema, replay, and boundary guarantees.

## Non-Goals

This ADR does not implement:

- worker execution
- execution runtime
- dispatch runtime
- orchestration
- planning
- reflection

## Certification

AUTHORIZED_WORKER_REQUEST_STATUS = CERTIFIED
