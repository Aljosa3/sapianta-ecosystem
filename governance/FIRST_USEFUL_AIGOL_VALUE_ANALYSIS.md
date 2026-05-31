# FIRST_USEFUL_AIGOL_VALUE_ANALYSIS

## Summary

The first useful operation is a governed configuration/repository marker creation.

The provider-alone path can produce intent and content. The AiGOL path produces intent, bounded authorization, authorized execution, and replay evidence.

## Value Matrix

| Value Area | Direct Provider Call | AiGOL-Governed Operation |
| --- | --- | --- |
| Real user request | Can answer or suggest | Preserves request as replay-visible input |
| Governance value | None inherent | Proposal must pass governed authorization |
| Authorization value | None inherent | Worker execution requires explicit authorization artifact |
| Replay value | Provider transcript only, if captured externally | Reconstructs provider, proposal, authorization, request, worker, and result |
| Worker value | No bounded worker contract | Worker receives only `AUTHORIZED_WORKER_REQUEST_V1` |
| Evidence value | Low auditability | Deterministic hashes, append-only replay, corruption detection |
| Failure behavior | Provider-dependent | Fail-closed on unresolved execution states |

## Measurable Evidence

Current validated evidence from `FIRST_END_TO_END_GOVERNED_OPERATION_V1`:

- `10 passed` focused acceptance tests;
- full replay reconstruction succeeds;
- successful file creation succeeds;
- missing proposal fails closed;
- missing authorization fails closed;
- invalid request fails closed;
- unknown worker fails closed;
- scope mismatch fails closed;
- append-only replay violation fails closed;
- replay corruption is detected.

## Useful Difference

The useful difference is:

```text
Provider says what could happen.
AiGOL proves what was allowed to happen, what did happen, and why it was bounded.
```

## Scope Boundary

This usefulness proof does not introduce:

- code generation;
- API invocation;
- shell execution;
- orchestration;
- planning;
- autonomous behavior;
- multi-worker execution.

The value is intentionally narrow: a single governed filesystem mutation with full audit evidence.

