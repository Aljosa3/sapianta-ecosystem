# REPLAY_INSPECTOR_WORKER_ADR_V1

## Status

Accepted.

## Context

AiGOL now has lifecycle coverage from proposal through completion. The first real worker should validate worker attachment with minimal risk.

Prior readiness review identified `REPLAY_INSPECTOR_WORKER_V1` as the safest first worker candidate because it is read-only, replay-native, deterministic, and locally bounded.

## Decision

Define `REPLAY_INSPECTOR_WORKER_V1` as the first real worker foundation.

The worker will inspect replay evidence only after the existing lifecycle authorizes and invokes it.

The worker may produce deterministic inspection observations.

The worker may not mutate replay, certify results, analyze failures as governance, call providers, or create lifecycle transitions.

## Rationale

Replay inspection is the lowest-risk useful worker capability because:

- the input domain is AiGOL's own replay evidence;
- read-only operation avoids mutation risk;
- deterministic output is feasible;
- lifecycle continuity can be validated directly;
- missing or corrupt replay can be surfaced safely;
- no external provider or network dependency is required.

## Consequences

AiGOL may proceed toward a first real worker implementation using `REPLAY_INSPECTOR_WORKER_V1` as the bounded worker type.

Implementation remains future work.

Result runtime remains future work.

The worker foundation is ready, but it does not certify unrestricted worker execution or result certification.

## Non-Goals

This ADR does not implement:

- worker code;
- result runtime;
- failure runtime;
- reflection runtime;
- self-improvement runtime;
- replay repair;
- governance mutation;
- provider integration.

## Final Classification

```text
REPLAY_INSPECTOR_WORKER_FOUNDATION_STATUS = READY
```
