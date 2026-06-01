# FIRST_REAL_WORKER_READINESS_RECOMMENDATIONS_V1

## Recommendation 1: Attach A Replay Inspector First

The safest first real worker is:

```text
REPLAY_INSPECTOR_WORKER_V1
```

Initial capability:

```text
Read replay artifacts for a declared canonical chain id and return a deterministic summary.
```

Allowed behavior:

- read replay artifacts;
- validate expected file presence;
- summarize stage status;
- report missing references;
- report corrupt evidence;
- return deterministic JSON.

Forbidden behavior:

- write files;
- call network APIs;
- execute shell commands;
- invoke providers;
- mutate governance;
- mutate replay;
- claim completion without completion runtime;
- continue autonomously after invocation.

## Recommendation 2: Treat First Worker As Integration Probe

The first worker should prove:

- worker registration works with real identity;
- worker assignment works with real capability metadata;
- dispatch can target real worker identity;
- invocation parameters can be delivered in bounded form;
- replay can record the handoff;
- result-shape expectations can be discovered.

It should not prove full execution completion.

## Recommendation 3: Define Execution Runtime Immediately After First Probe

Execution Runtime should follow the first read-only worker probe.

Required scope:

```text
INVOKED
  -> EXECUTING
```

No completion should be included in Execution Runtime unless separately defined.

## Recommendation 4: Define Result And Completion Separately

Keep these as separate boundaries:

```text
EXECUTING
  -> RESULT_RECORDED
  -> COMPLETED or FAILED
  -> TERMINATED
```

This preserves auditability and prevents invocation from silently becoming completion.

## Recommendation 5: Avoid External APIs For First Worker

External APIs should wait until:

- execution runtime exists;
- result runtime exists;
- failure runtime exists;
- timeout behavior exists;
- operator review behavior exists;
- credential handling is explicitly governed.

## Recommendation 6: Use Strict Capability Metadata

The first worker should declare:

- worker id;
- worker type;
- worker version;
- supported request type;
- capability id;
- allowed effects;
- forbidden effects;
- trust boundary;
- replay reference.

Any unstated effect should be forbidden.

## Recommendation 7: Preserve Provider Isolation

The first worker must not call providers or accept provider commands as authority.

Provider evidence may remain upstream proposal context only.

## Recommendation 8: Add A First Worker Acceptance Suite

Before certifying the first real worker, tests should cover:

- valid chain invocation;
- missing invocation parameters;
- unsupported capability;
- chain mismatch;
- worker unavailable;
- replay corruption;
- forbidden write attempt;
- forbidden provider command;
- deterministic result serialization;
- no completion claim.

## Recommended Decision

Proceed with a first real read-only worker only as a bounded integration probe.

Recommended first worker:

```text
REPLAY_INSPECTOR_WORKER_V1
```

Alternative:

```text
STATUS_REPORTER_WORKER_V1
```

Avoid mutable workers until execution, result, completion, failure, and termination runtimes are implemented.

```text
FIRST_REAL_WORKER_READINESS_STATUS = READY_WITH_GAPS
```
