# IMPROVEMENT_APPROVAL_RUNTIME_V1

IMPROVEMENT_APPROVAL_RUNTIME_STATUS = CERTIFIED

## Purpose

`IMPROVEMENT_APPROVAL_RUNTIME_V1` implements deterministic, replay-visible improvement approval decisions.

It creates:

```text
IMPROVEMENT_APPROVAL_ARTIFACT_V1
```

The runtime records explicit human-authorized `APPROVED` or `REJECTED` decisions for reviewed improvement proposals. It may authorize future implementation planning for approved decisions, but it does not implement improvements, create execution requests, modify governance, modify replay, or self-apply changes.

## Runtime Boundary

The implemented boundary is:

```text
IMPROVEMENT_REVIEW_ARTIFACT_V1
-> IMPROVEMENT_APPROVAL_ARTIFACT_V1
```

Improvement approval records:

- improvement review reference and hash;
- improvement proposal reference and hash;
- evaluation reference and hash;
- result reference and hash;
- canonical chain id;
- human authorization reference;
- decision reason;
- `APPROVED` or `REJECTED` status;
- future implementation planning authorization for `APPROVED`;
- implementation-not-performed state.

## Replay Events

The runtime persists append-only replay events:

```text
000_improvement_approval_recorded.json
001_improvement_approval_returned.json
```

Replay reconstruction validates event ordering, replay wrapper hashes, approval artifact hash, review reference continuity, proposal reference continuity, canonical chain continuity, and forbidden implementation or mutation flags.

## Fail-Closed Behavior

The runtime fails closed on:

- invalid review artifact;
- invalid proposal artifact;
- invalid decision;
- missing human authorization;
- duplicate approval replay;
- canonical chain mismatch;
- corrupt review references;
- corrupt proposal references;
- review authority leakage;
- replay wrapper corruption;
- replay ordering mismatch;
- replay chain mismatch.

## Explicit Non-Goals

`IMPROVEMENT_APPROVAL_RUNTIME_V1` does not implement:

- implementation planning;
- implementation execution;
- execution request creation;
- worker dispatch;
- worker invocation;
- governance mutation;
- replay mutation;
- reflection;
- self-modification;
- self-improvement;
- self-application.

## Validation

Focused validation passed:

```bash
python -m pytest tests/test_improvement_approval_runtime_v1.py
```

Result:

```text
15 passed
```

Lifecycle validation passed:

```bash
python -m pytest tests/test_improvement_approval_runtime_v1.py tests/test_improvement_review_runtime_v1.py tests/test_improvement_proposal_runtime_v1.py tests/test_result_evaluation_runtime_v1.py tests/test_result_runtime_v1.py tests/test_replay_inspector_worker_v1.py tests/test_completion_runtime_v1.py tests/test_execution_runtime_v1.py tests/test_worker_invocation_runtime_v1.py tests/test_dispatch_runtime_v1.py tests/test_worker_runtime_v1.py
```

Result:

```text
164 passed
```

## Final Classification

```text
IMPROVEMENT_APPROVAL_RUNTIME_STATUS = CERTIFIED
```
