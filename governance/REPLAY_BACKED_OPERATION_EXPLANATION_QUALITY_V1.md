# REPLAY_BACKED_OPERATION_EXPLANATION_QUALITY_V1

## Quality Standard

An explanation is high quality when a human can understand:

- what occurred;
- why it occurred;
- why it was authorized;
- which worker executed;
- what result was produced;
- why the result is trustworthy.

## Current Quality Classification

`EXPLANATION_READINESS = HIGH`

for successful operator runtime operations with verified replay.

## Trust Basis

Trust is based on:

- replay verification status;
- provider replay hash presence;
- authorization replay hash presence;
- worker replay hash presence;
- lineage continuity;
- worker content hash;
- six replay events spanning proposal, authorization, and worker execution.

## Successful Explanation Shape

The explanation follows this structure:

```text
What happened: ...
Why it happened: ...
Why it was authorized: ...
Why to trust it: ...
```

## Quality Boundaries

The explanation does not claim:

- semantic correctness of artifact contents;
- external provider reliability;
- human intent beyond replay-visible request evidence;
- safety beyond the governed operation boundary.

## Future Quality Improvements

Explanation quality would improve with:

- operation ledger context;
- semantic artifact validation evidence;
- explicit human intent evidence;
- fail-closed replay persistence for early rejected operations.
