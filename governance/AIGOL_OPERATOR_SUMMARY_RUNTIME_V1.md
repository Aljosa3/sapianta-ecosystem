# AIGOL_OPERATOR_SUMMARY_RUNTIME_V1

## Status

Runtime certification.

## Final Classification

```text
AIGOL_OPERATOR_SUMMARY_RUNTIME_STATUS = CERTIFIED
```

## Problem

AiGOL lifecycle evidence is replay-visible and technically correct, but
operator-facing output exposes too much internal lifecycle detail.

Operators see statuses such as:

```text
WORKER_ASSIGNED
WORKER_DISPATCHED
WORKER_INVOKED
WORKER_RESULT_CAPTURED
RESULT_VALIDATED
REVIEW_COMPLETED
TERMINATED
```

These statuses are useful for audit replay, but they are too verbose and can
blur the distinction between governed lifecycle evidence and real-world
implementation execution.

## Runtime Component

Implemented:

```text
aigol/runtime/operator_summary_runtime.py
```

Defined artifact:

```text
OPERATOR_SUMMARY_ARTIFACT_V1
```

## Runtime Model

The runtime accepts an existing lifecycle capture dictionary and creates a
read-only, replay-visible operator summary artifact.

It translates technical lifecycle evidence into concise operator-facing
messages.

Examples:

```text
WORKER_ASSIGNED
WORKER_DISPATCHED
WORKER_INVOKED
WORKER_RESULT_CAPTURED
```

becomes:

```text
Provider selected and proposal processed successfully.
```

and:

```text
RESULT_VALIDATED
REVIEW_COMPLETED
TERMINATED
```

becomes:

```text
Operation completed and verified.
```

When executable domain bundle verification is present, the summary becomes:

```text
Domain bundle created and verified.
```

## Replay Model

Replay persists:

```text
000_operator_summary_recorded.json
001_operator_summary_returned.json
```

Replay reconstruction verifies:

- replay step ordering;
- replay wrapper hashes;
- summary artifact hash;
- returned artifact hash;
- returned summary reference;
- deterministic `operator_summary_hash`.

## Artifact Fields

`OPERATOR_SUMMARY_ARTIFACT_V1` records:

- operator summary id;
- source lifecycle hash;
- optional source replay reference;
- summary status;
- headline;
- details;
- operator next steps;
- technical stage groups;
- read-only marker;
- replay-visible marker;
- source replay mutation marker set to false;
- lifecycle modification marker set to false;
- authority flags all set to false;
- failure reason when fail-closed.

## Authority Boundaries

The runtime does not:

- authorize execution;
- authorize dispatch;
- authorize worker invocation;
- authorize provider invocation;
- create approvals;
- create implementation;
- mutate governance;
- mutate source replay;
- modify lifecycle state.

The runtime only records summary evidence in its own append-only replay
directory.

## Fail-Closed Behavior

The runtime fails closed when:

- lifecycle input is not a JSON object;
- lifecycle input is not JSON serializable;
- replay output artifacts already exist;
- replay reconstruction detects wrapper tampering;
- replay reconstruction detects summary hash mismatch;
- replay reconstruction detects returned-reference mismatch.

## Validation

Focused validation passed:

```bash
python -m pytest tests/test_operator_summary_runtime_v1.py
```

Result:

```text
7 passed
```

## Acceptance Evidence

Acceptance evidence is recorded in:

```text
governance/AIGOL_OPERATOR_SUMMARY_RUNTIME_ACCEPTANCE_EVIDENCE.json
```

## Commit Message

```text
Certify operator summary runtime
```

