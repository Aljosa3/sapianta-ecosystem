# G22-09 — Durable Governed Work Canonical Lifecycle Binding Implementation

Status: implemented and validated

Date: 2026-07-12

## Executive Summary

G22-09 corrects the direct `PLATFORM_DURABLE_GOVERNED_WORK_RUNTIME` lifecycle binding identified by the G22-08 audit. The direct route now consumes an existing Development Composition Plan artifact and, when available, the existing Project Objective artifact. It no longer regenerates a Development Composition Plan from the current query.

The existing Durable Governed Work runtime, validation rules, fail-closed guard, and Platform Core Project Services automatic plan-to-durable transition remain unchanged.

## Root Cause

The direct durable route declared only `query` as required evidence and called `compose_platform_development_plan_for_query()` internally. A request naming Durable Governed Work could therefore select the correct downstream runtime while supplying a query that was not independently sufficient to regenerate Capability Coverage and a Development Composition Plan.

Durable Governed Work then correctly rejected the regenerated failed plan. The defect belonged to the direct router lifecycle contract, not to Durable Governed Work validation.

## Minimal Deterministic Implementation

The direct durable route now:

1. declares `development_plan_artifact` as required route evidence;
2. accepts the existing plan through `route_platform_query()`;
3. accepts an optional existing `project_objective_artifact`;
4. passes both artifacts directly to `compose_durable_governed_work()`;
5. returns `REQUIRED_EVIDENCE_MISSING` without service invocation when no upstream plan is supplied;
6. preserves Durable Governed Work's canonical failed artifact when a validated upstream plan has a failed status.

No plan-generation fallback remains in the direct durable adapter.

## Lifecycle and Lineage Behaviour

For a valid upstream plan, the durable artifact records the exact `source_development_plan_hash`. When a Project Objective is supplied, it records the exact `source_project_objective_hash`. This preserves the deterministic planning and objective lineage rather than deriving new lineage from a second query interpretation.

The existing Platform Core Project Services transition continues to pass its selected Development Composition Plan service response directly into Durable Governed Work. That path was not modified.

## Fail-Closed Preservation

- Missing upstream plan: router returns `REQUIRED_EVIDENCE_MISSING` with `development_plan_artifact` identified and does not invoke the service.
- Failed upstream plan: existing Durable Governed Work validation accepts the canonical artifact shape, detects `DEVELOPMENT_COMPOSITION_PLAN_FAILED_CLOSED`, and returns `DURABLE_GOVERNED_WORK_FAILED_CLOSED`.
- Corrupt plan artifacts continue to fail validation through the existing runtime.
- No Provider, Worker, repository, governance, replay, approval, authorization, or certification semantics changed.

## Architectural Boundaries

Platform Core Development Lifecycle remains the owner of the route and lifecycle handoff. Development Composition Plan remains the plan producer. Durable Governed Work remains the plan consumer and reviewable-artifact owner.

The implementation does not modify:

- Durable Governed Work validation;
- Approval or authorization;
- Worker or Provider execution;
- Replay or Certification;
- Human Interfaces;
- Platform Core Project Services automatic transition.

## Regression Evidence

Validation executed on 2026-07-12:

- focused G22-09, Development Plan, Durable Work, router, and lifecycle regressions: `28 passed`;
- final full regression suite: `5989 passed, 4 skipped`;
- governance conformance tests: `5 passed`;
- governance conformance engine: `PARTIALLY_CONFORMANT`, with `18` checks passed, `2` known hook-drift checks failed, and `0` critical violations;
- governance conformance remained deterministic, fail-closed, and read-only;
- `py_compile`: passed for the changed runtime and regression modules;
- `git diff --check`: passed.

The focused regressions prove that plan generation is not called by the direct durable route, valid plan and objective hashes are preserved, missing plans stop at the route evidence boundary, failed plans remain failed closed, and Provider, Worker, and repository mutation flags remain false.

The partial governance conformance result is not represented as full conformance. Existing root and system pre-commit hook drift remains visible.

## Final Verdict

`DURABLE_GOVERNED_WORK_CANONICAL_LIFECYCLE_BINDING_COMPLETED_WITHOUT_ARCHITECTURAL_OWNERSHIP_CHANGE`
