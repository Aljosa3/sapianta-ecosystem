# IMPROVEMENT_PROPOSAL_RUNTIME_V1

IMPROVEMENT_PROPOSAL_RUNTIME_STATUS = CERTIFIED

## Purpose

`IMPROVEMENT_PROPOSAL_RUNTIME_V1` implements deterministic, replay-visible improvement proposal creation.

It creates:

```text
IMPROVEMENT_PROPOSAL_ARTIFACT_V1
```

The runtime converts valid result evaluation evidence into a proposal-only artifact. It does not approve, review, implement, create execution requests, modify governance, modify replay, self-improve, or self-apply changes.

## Runtime Boundary

The implemented boundary is:

```text
RESULT_EVALUATION_ARTIFACT_V1
-> IMPROVEMENT_PROPOSAL_ARTIFACT_V1
```

Improvement proposal creation records:

- evaluation reference and hash;
- result reference and hash;
- canonical chain id;
- execution reference;
- completion reference;
- worker identity;
- proposal source;
- proposal text and reason;
- proposal scope and constraints;
- approval-required state;
- implementation-not-authorized state.

## Replay Events

The runtime persists append-only replay events:

```text
000_improvement_proposal_created.json
001_improvement_proposal_returned.json
```

Replay reconstruction validates event ordering, replay wrapper hashes, proposal artifact hash, evaluation reference continuity, evaluation hash continuity, canonical chain continuity, and forbidden authority flags.

## Fail-Closed Behavior

The runtime fails closed on:

- invalid evaluation artifact;
- evaluation without improvement recommendation;
- canonical chain mismatch;
- corrupt evaluation references;
- duplicate proposal replay;
- invalid proposal source;
- authority-bearing proposal scope or constraints;
- authority-bearing proposal text;
- replay wrapper corruption;
- replay ordering mismatch;
- replay chain mismatch.

## Explicit Non-Goals

`IMPROVEMENT_PROPOSAL_RUNTIME_V1` does not implement:

- improvement review;
- improvement approval;
- implementation planning;
- implementation execution;
- execution request creation;
- worker dispatch;
- worker invocation;
- governance mutation;
- replay mutation;
- reflection;
- self-improvement;
- self-application.

## Validation

Focused validation passed:

```bash
python -m pytest tests/test_improvement_proposal_runtime_v1.py
```

Result:

```text
14 passed
```

Lifecycle validation passed:

```bash
python -m pytest tests/test_improvement_proposal_runtime_v1.py tests/test_result_evaluation_runtime_v1.py tests/test_result_runtime_v1.py tests/test_replay_inspector_worker_v1.py tests/test_completion_runtime_v1.py tests/test_execution_runtime_v1.py tests/test_worker_invocation_runtime_v1.py tests/test_dispatch_runtime_v1.py tests/test_worker_runtime_v1.py
```

Result:

```text
135 passed
```

## Final Classification

```text
IMPROVEMENT_PROPOSAL_RUNTIME_STATUS = CERTIFIED
```
