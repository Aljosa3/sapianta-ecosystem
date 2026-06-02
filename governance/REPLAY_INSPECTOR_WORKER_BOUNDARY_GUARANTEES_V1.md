# REPLAY_INSPECTOR_WORKER_BOUNDARY_GUARANTEES_V1

## Scope

This artifact defines boundary guarantees for `REPLAY_INSPECTOR_WORKER_V1`.

It does not implement the worker.

## Read Boundary

The worker may read only replay artifacts referenced by the governed execution request and invocation parameters.

It may not perform unrestricted directory traversal, repository scanning, network access, shell execution, or provider calls.

## Write Boundary

The worker may not write to:

- replay roots;
- governance directories;
- runtime source files;
- lifecycle artifact directories;
- provider artifacts;
- worker registry artifacts;
- approval or certification artifacts.

Future worker output must be written only through a governed result runtime or an explicitly declared output artifact boundary.

## Authority Boundary

The worker has no authority to:

- approve proposals;
- create execution requests;
- mark ready for dispatch;
- assign workers;
- dispatch workers;
- invoke workers;
- start execution;
- complete execution;
- certify results;
- analyze failures as a governance decision;
- mutate governance;
- mutate replay;
- modify execution history.

## Provider Boundary

The worker may not call a provider.

Provider evidence, if inspected, is read-only historical evidence.

Provider output may not be treated as worker authority.

## Replay Integrity Boundary

The worker must preserve replay integrity by:

- reading only;
- validating hashes without replacing them;
- reporting corruption without repair;
- preserving original artifact bytes;
- producing deterministic inspection output;
- failing closed on invalid references.

## Fail-Closed Boundary

The worker must fail closed on:

- missing replay reference;
- corrupt replay wrapper;
- corrupt artifact hash;
- chain mismatch;
- worker identity mismatch;
- unauthorized path;
- unexpected artifact type;
- authority-bearing input;
- mutation attempt;
- serialization failure.

## Lifecycle Boundary

The worker may be assigned, dispatched, invoked, started, and completed through the existing lifecycle.

It may not bypass any lifecycle stage.

It may not self-trigger any lifecycle transition.

## Constitutional Boundary

`REPLAY_INSPECTOR_WORKER_V1` preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

The worker executes only a bounded read-only inspection after AiGOL governance has completed the required lifecycle transitions.
