# G22-10B — Lifecycle-State-Aware Routing Precedence Implementation

Status: implemented and validated

Date: 2026-07-12

## Executive Summary

G22-10B refines the existing Platform Query Router lifecycle precedence decision so a validated upstream Development Composition Plan and an explicit Durable Governed Work to Approval target continue through the downstream Durable Governed Work runtime. Unbound lifecycle requests and requests without a valid upstream plan continue to enter Development Composition Plan.

The correction reuses the existing route candidates, lifecycle precedence map, clause-role interpretation, Development Composition Plan validation, and replay-visible precedence artifact. It introduces no new routing subsystem or lifecycle authority.

## Root Cause

The prior precedence rule treated every top-score tie between Development Composition Plan and Durable Governed Work as a new lifecycle entry. Historical references to Development Composition Plan could therefore force re-entry even when:

- a valid upstream plan was already supplied;
- the request explicitly targeted Durable Governed Work or its downstream Approval transition;
- the Durable route had all required evidence.

The selected Development Composition Plan then correctly failed closed when the downstream audit request did not independently provide planning facets.

## Minimal Deterministic Implementation

`_apply_lifecycle_precedence()` now receives the current query and optional upstream plan artifact. It:

1. validates the supplied plan through the existing Development Composition Plan validator;
2. rejects corrupt or failed plans as lifecycle state;
3. reuses existing clause-role interpretation to inspect requested-action clauses;
4. recognizes an explicit Durable Governed Work to Approval target;
5. selects Durable Governed Work only when both valid plan state and downstream target evidence exist;
6. otherwise preserves canonical Development Composition Plan entry precedence.

The route-status tie calculation now respects either a suppressed downstream route or a suppressed entry route. Unrelated ties retain existing clarification behavior.

## Replay-Visible Lifecycle Evidence

The existing `PLATFORM_QUERY_LIFECYCLE_PRECEDENCE_DECISION_V1` artifact now records:

- `selected_lifecycle_runtime`;
- `lifecycle_stage`;
- `upstream_plan_hash`;
- `precedence_reason`;
- `suppressed_entry_routes` where downstream continuation applies;
- confirmation that clause-role interpretation was reused.

For downstream continuation, the durable artifact records the same source Development Composition Plan hash, preserving lineage from precedence decision through durable work creation.

## Before / After Behaviour

| Scenario | Result |
| --- | --- |
| New lifecycle request, no upstream plan | Development Composition Plan remains the canonical entry runtime. |
| Plan/Durable tie, no valid upstream plan | Development Composition Plan retains precedence. |
| Valid upstream plan plus explicit Durable Work to Approval target | Durable Governed Work is selected and the entry route is suppressed for this decision. |
| Historical Development Plan reference plus explicit downstream target | Historical reference no longer forces lifecycle re-entry. |
| Invalid or failed upstream plan | It is not accepted as valid lifecycle state; existing fail-closed behavior remains. |
| Unrelated equal-score routes | Existing clarification behavior remains unchanged. |

## Architectural Boundaries

- Platform Query Router remains the owner of deterministic route and precedence selection.
- Development Composition Plan remains the canonical lifecycle entry and plan validator.
- Durable Governed Work remains the downstream plan consumer.
- Clause-role interpretation remains owned by existing Platform Core interpretation services.
- No Durable validation, Approval, Worker, Provider, Replay, Certification, or Human Interface behavior changed.
- Provider invocation, Worker invocation, and repository mutation remain false on the tested path.

## Regression Evidence

Validation executed on 2026-07-12:

- focused G22-10B, router, G22-09 durable binding, and lifecycle regressions: `18 passed`;
- final full regression suite: `5992 passed, 4 skipped`;
- governance conformance tests: `5 passed`;
- governance conformance engine: `PARTIALLY_CONFORMANT`, with `18` checks passed, `2` known hook-drift checks failed, and `0` critical violations;
- governance conformance remained deterministic, fail-closed, and read-only;
- `py_compile`: passed for the changed router and focused regression module;
- `git diff --check`: passed.

The partial conformance result is not represented as full conformance. Existing root and system pre-commit hook drift remains visible.

## Final Verdict

`LIFECYCLE_STATE_AWARE_ROUTING_PRECEDENCE_COMPLETED_WITHOUT_ARCHITECTURAL_OWNERSHIP_CHANGE`
