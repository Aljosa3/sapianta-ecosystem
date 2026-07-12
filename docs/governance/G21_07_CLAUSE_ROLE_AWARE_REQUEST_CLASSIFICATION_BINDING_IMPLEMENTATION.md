# G21-07 — Clause-Role-Aware Request Classification Binding Implementation

Status: implemented and validated

Date: 2026-07-12

## Executive Summary

G21-07 corrects deterministic request classification without introducing a semantic engine, NLP, probabilistic interpretation, a new governed work type, or a new Platform Core subsystem. The existing Platform Core interpretation pipeline now records bounded clause-role evidence before governed work-type resolution and capability discovery.

Explicit non-mutating validation requests using `validate`, `verify`, or `confirm` bind to the existing `AUDIT_ONLY` work type. Capability names appearing only in quoted evidence, tool/interface references, architectural references, or lifecycle observations are excluded from capability-target discovery. Explicit requests to inspect, implement, modify, extend, evaluate, or reuse a capability remain eligible targets.

## Root Cause

The previous classifier treated the request as nearly one lexical corpus. Keyword presence could therefore override the semantic role of the clause containing the keyword:

- validation verbs did not contribute read-only audit intent;
- prohibitions were observed separately from validation operations;
- passive references to `./aicli`, Human Interfaces, Providers, and Workers could become capability targets;
- inferred reuse evidence could produce a `reuse_delta` clarification despite a non-mutating inspection objective.

The defect was owned by Platform Core work-type interpretation, Project Objective Inference, capability discovery, and clarification planning. Human Interfaces, Approval, Worker Runtime, Replay, and Certification were not ownership points.

## Minimal Deterministic Implementation

The implementation reuses the existing deterministic interpretation pipeline:

1. `platform_project_objective_inference.py` composes stable lexical clause-role evidence for requested actions, prohibitions, safety constraints, quoted runtime evidence, architectural references, tool/interface references, and capability-target eligibility.
2. `resolve_governed_work_type()` binds a validation or inspection action plus an explicit non-mutation constraint to canonical `AUDIT_ONLY`, unless an existing explicit canonical work-type declaration already has precedence.
3. `discover_candidate_capabilities()` matches catalog terms only inside capability-target-eligible clauses.
4. Clarification planning suppresses `reuse_delta` and `reuse_goal` for a non-mutating audit, analysis, inspection, or existing-capability discovery objective where no changed outcome is requested.
5. Project Objective Inference recognizes validation actions as audit/analysis outcomes and preserves deterministic replay hashing.

The clause grammar is bounded and explicit. It does not infer intent probabilistically, invoke a Provider, invoke a Worker, authorize execution, or mutate the repository during runtime validation.

## Before / After Behaviour

| Scenario | Before | After |
| --- | --- | --- |
| `Validate implementation. Do not implement.` | Defaulted to `IMPLEMENTATION`; approval preparation could become admissible. | Binds to `AUDIT_ONLY`; summary and approval preparation are inadmissible; read-only binding is admissible. |
| Root-cause audit mentioning `./aicli`, Human Interface, Providers, and Workers as evidence or boundaries | Reference keywords could become capability targets and generate artificial clarification. | Passive reference clauses are not capability-target eligible; no Human Interface target or artificial `reuse_delta` is produced. |
| Implementation request containing `validate` without a non-mutation constraint | Risk of over-correction. | Remains `IMPLEMENTATION` with mutation and summary semantics unchanged. |
| Explicit canonical work-type declaration | Existing precedence required preservation. | Explicit declaration retains precedence, including existing conflicting-declaration fail-closed evidence. |

## Architectural Boundaries

- Platform Core remains the sole authority for semantic interpretation, work-type determination, capability discovery, and clarification planning.
- `./aicli` and other Human Interfaces remain thin adapters and were not modified.
- No Provider or Worker selection, invocation, or execution path was added.
- No replay, certification, approval, governance constitution, canonical artifact schema, or lifecycle ownership changed.
- No new canonical work type or inference subsystem was introduced.
- Replay-visible artifacts retain deterministic hashing and stable ordering.
- Existing fail-closed ambiguity behavior and explicit governed work-type precedence remain intact.

## Regression Evidence

Validation executed on 2026-07-12:

- focused G21-07 regressions: `5 passed`;
- combined Project Objective Inference, Human Interface, capability discovery, clarification, and read-only binding regressions: `28 passed`;
- compatibility regressions discovered during the first full run and corrected: `7 passed` with the G21-07 set;
- final full regression suite: `5984 passed, 4 skipped`;
- governance conformance tests: `5 passed`;
- governance conformance engine: `PARTIALLY_CONFORMANT`, `18` checks passed, `2` known hook-drift checks failed, `0` critical violations, deterministic, fail-closed, and read-only;
- `py_compile`: passed for both changed runtime modules and the G21-07 regression module;
- `git diff --check`: passed.

The conformance result is not reframed as full conformance. The existing root and system pre-commit hook drift remains visible. Runtime regression artifacts confirm `provider_invoked: false`, `worker_invoked: false`, and `repository_mutated: false` for the governed read-only reference scenario.

## Final Verdict

`CLAUSE_ROLE_AWARE_REQUEST_CLASSIFICATION_BOUND_WITHOUT_ARCHITECTURAL_OWNERSHIP_CHANGE`
