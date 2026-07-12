# G21-06 — Lifecycle-Aware Runtime Selection Precedence Implementation

Status: implemented and validated

Date: 2026-07-12

## Executive Summary

G21-06 corrects the deterministic routing-policy defect identified by the root-cause inspection. Existing route scores remain unchanged. Before ambiguity evaluation, the Unified Platform Query Router now recognizes that:

- `PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_RUNTIME` is the canonical entry runtime;
- `PLATFORM_DURABLE_GOVERNED_WORK_RUNTIME` is its automatic downstream lifecycle transition.

When both receive the same top score, the downstream route is removed only from ambiguity evaluation and the canonical entry runtime is selected. The downstream transition remains available after plan execution through existing Platform Core project services.

## Deterministic Transition

The router emits `PLATFORM_QUERY_LIFECYCLE_PRECEDENCE_DECISION_V1` metadata containing:

- whether precedence was applied;
- the canonical entry runtime;
- suppressed downstream lifecycle routes;
- the shared top score;
- deterministic selection reasoning;
- Platform Core and Human Interface authority boundaries.

Unrelated equal-score routes remain ambiguous and continue to return `ROUTE_CLARIFICATION_REQUIRED`.

## Boundaries

The implementation changes only Unified Platform Query Router selection policy. It does not modify scoring, presentation mapping, Development Composition Plan behavior, Durable Governed Work behavior, Approval, Authorization, Workers, Replay, Certification, or Human Interfaces.

## Behavioral Result

The previously recorded request now produces:

- `route_status: ROUTE_READY`;
- `selected_service: PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_RUNTIME`;
- `service_invoked: true`;
- Development Composition Plan service response;
- `PRESENTATION_READY` for a valid plan;
- the existing automatic Durable Governed Work transition in project services.

## Final Verdict

`LIFECYCLE_AWARE_RUNTIME_SELECTION_PRECEDENCE_BOUND_WITHOUT_ARCHITECTURAL_OWNERSHIP_CHANGE`

