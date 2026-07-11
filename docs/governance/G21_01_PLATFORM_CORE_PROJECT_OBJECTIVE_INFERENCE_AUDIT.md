# G21-01 — Platform Core Project Objective Inference Audit

Status: `AUDIT_ONLY`

Date: 2026-07-11

## Executive Summary

Platform Core already contains enough deterministic information to infer the project objective in the observed request. The request identifies the subject (deterministic dependency impact analysis), the work type (audit only), the required analysis (existing capability, reuse, certified compositions, and residual gap), the requested output (a governed development plan), and the execution boundary (no implementation). No material architectural choice is left to human interpretation before read-only preparation can begin.

The observed question—`What outcome should the active project objective architecture decision enable?`—does not prove genuine ambiguity. It is produced by a conservative clarification policy. Candidate discovery falls back to the replay-backed `active_objective` candidate, architecture-language detection creates an `architecture_outcome` slot, and first-pass sufficiency accepts that slot only when the request contains all three configured lexical categories: reusable Platform Core behavior, Human Interface neutrality, and an observable user-visible outcome. The request states a complete governance outcome, but it does not state Human Interface neutrality or use the narrow outcome vocabulary required by that slot predicate.

The missing capability is therefore not a new inference engine. It is a bounded canonical composition that turns the complete request, restored project context, capability discovery, coverage, and work-type evidence into a first-class project-objective inference artifact before clarification necessity is decided.

## Observed Request and Deterministic Objective

The audited request is:

> Audit the current Platform Core capabilities for implementing deterministic dependency impact analysis. Do not implement anything. Determine what already exists, what can be reused, what certified compositions already exist, what is missing and prepare a governed development plan.

Its deterministically inferable objective is:

> Determine whether existing certified Platform Core capabilities and compositions cover deterministic dependency impact analysis; identify any residual gap; and, without implementation or mutation, produce the minimal governed development composition plan needed to close that gap.

This inference preserves every explicit constraint. It does not decide an unstated product behavior, authorize execution, select a Provider or Worker, or invent a new subsystem.

## Existing Reusable Platform Capabilities

| Existing capability | Deterministic evidence already available | Reuse in objective inference |
|---|---|---|
| Persistent project workspace and guidance | `prepare_unified_human_interface_project_context(...)` restores the latest workspace state and derives project guidance before resolving the request (`aigol/runtime/platform_core_project_services.py:191`). | Supplies the active objective, replay continuity, implementation history, and project authority. |
| Candidate capability discovery | `discover_candidate_capabilities(...)` emits a replay-visible discovery artifact with the raw prompt, extracted human objective, candidates, selected target, reuse decision, and ambiguity flag (`aigol/runtime/platform_core_project_services.py:1843`). | Supplies deterministic subject candidates and distinguishes actual tied candidates from a selected target. |
| Development intent and work-type preservation | `resolve_development_intent(...)` binds candidate discovery, goal mapping, governed request, requested/prepared work type, mutation allowance, and read-only admissibility (`aigol/runtime/platform_core_project_services.py:2091`). | Establishes that `AUDIT_ONLY` is non-mutating and eligible for governed read-only work. |
| First-pass context sufficiency | `clarification_context_sufficiency_evaluation(...)` evaluates candidate missing slots against the original request and emits accepted, unresolved, and remaining requirements (`aigol/runtime/platform_core_project_services.py:3141`). | Provides the correct fail-closed gate once it consumes a canonical objective rather than lexical fragments alone. |
| Capability composition coverage | `PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_RUNTIME` is registered in the Unified Platform Query Router (`aigol/runtime/platform_query_router.py:53`, `aigol/runtime/platform_query_router.py:132`). | Answers what exists, what composes, and what remains uncovered. |
| Development composition planning | `compose_platform_development_plan(...)` validates coverage and produces reusable capabilities, residual gaps, ordered work, dependencies, validation, and implementation boundary (`aigol/runtime/platform_development_composition_plan.py:55`). | Already supplies the requested governed plan after a coverage artifact exists. |
| Query and presentation composition | The Unified Platform Query Router exposes coverage and development-plan routes, and the Canonical Platform Presentation Layer recognizes the development-plan artifact. | Keeps discovery and planning independent of Human Interface semantics. |
| Certification, governance, and replay evidence | The coverage and plan compositions reuse certification registry, generation certification, governance preview, replay preview, and immutable hashes. | Supplies deterministic provenance and fail-closed evidence without Providers or Workers. |

## Objective Inference Analysis

### Information sufficiency

The request answers the objective questions that materially affect safe read-only preparation:

- **Subject:** deterministic dependency impact analysis.
- **Action:** audit current Platform Core capability coverage.
- **Decision sought:** existing, reusable, certified, and missing capability.
- **Deliverable:** governed development plan.
- **Work type:** `AUDIT_ONLY`.
- **Mutation boundary:** no implementation.
- **Architectural default:** reuse certified Platform Core compositions before proposing a residual extension.

There is only one safe semantic interpretation consistent with all of those statements. “Prepare a governed development plan” does not conflict with `AUDIT_ONLY`: the existing G20-05 plan is explicitly read-only, advisory, non-authorizing, and separately approval-gated.

### Exact clarification path

The current transition is:

1. `prepare_unified_human_interface_project_context(...)` restores workspace guidance and calls `resolve_development_intent(...)`.
2. `discover_candidate_capabilities(...)` scans the bounded `CAPABILITY_CATALOG`. That catalog contains broad targets such as governance validation, replay, certification, development experience, and human-intent resolution, but no dependency-impact-analysis target.
3. When no catalog candidate matches and the request is associated with the restored project, `_active_objective_candidate(...)` represents the target as `active_objective`, displayed as `active project objective` (`aigol/runtime/platform_core_project_services.py:1997`).
4. `deterministic_clarification_plan(...)` calls `_clarification_missing_slots(...)` before question selection (`aigol/runtime/platform_core_project_services.py:3008`).
5. Architecture-language detection adds `architecture_outcome` whenever a candidate exists, with the reason that ownership needs an outcome (`aigol/runtime/platform_core_project_services.py:3288`).
6. `clarification_context_sufficiency_evaluation(...)` tests the complete request, but `_required_semantic_requirements("architecture_outcome")` requires all of: reusable Platform Core behavior, Human Interface neutrality, and observable user-visible outcome (`aigol/runtime/platform_core_project_services.py:1058`).
7. `_accepted_semantic_requirements(...)` recognizes those requirements through fixed phrases. The observed request contains `Platform Core`, but not a Human Interface-neutrality signal and not the configured outcome terms (`aigol/runtime/platform_core_project_services.py:1091`).
8. The slot remains open. `_clarification_question_for_slot(...)` combines the selected candidate display name with the architecture template, producing the observed question (`aigol/runtime/platform_core_project_services.py:3364`).

This is deterministic and fail-closed, but its semantic conclusion is too conservative for this complete request.

## Clarification Necessity Assessment

### Genuine ambiguity

No genuine ambiguity was found that would change the audit boundary, coverage query, plan artifact, governance authority, certification dependency, replay dependency, or authorization state.

A clarification would be justified if, for example:

- two capability targets had equal deterministic evidence and led to different coverage calculations;
- “dependency impact” could refer to materially different governed artifact domains not bounded by the request;
- the user requested both implementation and non-mutation;
- a required coverage input could not be derived or validated;
- the requested plan would authorize execution rather than remain advisory.

None of those conditions is present in the observed request.

### Conservative policy trigger

The clarification is caused by two policy limitations:

1. **Target vocabulary limitation.** Candidate discovery uses a bounded keyword catalog and falls back to the active objective instead of representing the request's complete subject as a canonical project objective.
2. **Slot-schema mismatch.** `architecture_outcome` is defined around reusable behavior, Human Interface neutrality, and a user-visible outcome. That schema is suitable for interface-placement questions, but it is over-applied to a governance audit whose desired outcome is an evidence-backed coverage decision and plan.

The planner itself exposes the architectural symptom: its deterministic-input metadata sets `canonical_semantic_artifact_available` to `False` (`aigol/runtime/platform_core_project_services.py:3101`).

## Composition Analysis

No new Platform subsystem is required. Existing services already provide all substantive computations:

1. Human intent resolution preserves request and work type.
2. Project workspace supplies replay-backed context.
3. Candidate discovery supplies capability hypotheses and genuine-ambiguity evidence.
4. Capability composition coverage supplies reusable and residual capability results.
5. Development composition planning supplies ordered governed work and boundaries.
6. Certification, governance, replay, routing, and presentation supply evidence and normalization.

What is absent is an authoritative transition that composes these facts into one objective before the generic clarification-slot policy runs. This is orchestration over established authorities, not a new reasoning authority.

## Gap Analysis

The exact missing capability is:

`CANONICAL_COMPLETE_REQUEST_TO_PROJECT_OBJECTIVE_INFERENCE_AND_SUFFICIENCY_BINDING`

The gap consists of four bounded responsibilities:

- derive one normalized objective from the complete request and restored project context;
- bind explicit outcomes, work type, non-goals, mutation boundary, and requested downstream artifacts;
- distinguish a genuine competing-objective ambiguity from a vocabulary or slot-schema miss;
- make clarification necessity consume that objective artifact before generating a question.

The gap does **not** include natural-language generation, probabilistic inference, implementation planning logic, dependency analysis logic, execution authorization, provider selection, worker invocation, or Human Interface ownership.

## First-Class Objective Artifact

The inferred objective should become a first-class replay-visible Platform Core artifact because it is an authority-bearing input shared by capability coverage, development planning, clarification necessity, approval preparation, and every Human Interface.

Recommended artifact identity:

`PLATFORM_CORE_PROJECT_OBJECTIVE_INFERENCE_ARTIFACT_V1`

Minimal canonical fields:

- source request and hash;
- restored project-objective reference and hash, if present;
- normalized inferred objective;
- requested outcome artifacts;
- requested and prepared work type;
- mutation and implementation boundaries;
- selected capability subjects and evidence;
- alternative objective candidates, if any;
- objective ambiguity status and exact competing interpretation evidence;
- objective sufficiency status and unresolved material fields;
- coverage and plan composition eligibility;
- Provider, Worker, Human Interface, authorization, and mutation boundary flags;
- deterministic artifact hash and supersession/replay references.

The artifact must record inference evidence rather than a confidence-only assertion. A single inferred objective is admissible only when all alternatives either preserve the same governed action or are eliminated deterministically.

## Corrected Lifecycle

The minimal corrected lifecycle is:

1. **Complete request analysis** — preserve the full request, work type, constraints, deliverables, restored objective, and replay evidence.
2. **Project objective inference** — compose one or more objective candidates from intent, workspace, capability discovery, and requested output artifacts.
3. **Objective sufficiency evaluation** — determine whether any unresolved difference would change routing, coverage, planning, governance, certification, replay, mutation, or authorization.
4. **Preparation composition** — when sufficient, route read-only capability coverage and compose the governed development plan.
5. **Clarification only on inference failure** — ask one highest-value question only when a material competing objective or missing input remains, and bind the answer to the objective artifact.

This ordering preserves fail-closed behavior. It changes the meaning of “missing”: absence of a literal phrase is no longer enough; the unresolved information must be material to the governed transition.

## Minimal Canonical Composition Recommendation

Implement, in a future authorized generation, one bounded read-only Platform Core composition service that:

- consumes existing project guidance, development-intent resolution, candidate discovery, work-type metadata, certification metadata, and replay context;
- emits `PLATFORM_CORE_PROJECT_OBJECTIVE_INFERENCE_ARTIFACT_V1`;
- validates the artifact deterministically and fails closed on conflicting objectives or invalid lineage;
- supplies the validated objective to clarification context sufficiency, capability composition coverage, and development composition planning;
- is registered as a reusable Platform capability and exposed through existing routing and presentation layers only if independent query access is required.

The composition should not replace Human Intent Resolution, the coverage runtime, the planning runtime, or the clarification planner. It should bind their existing evidence at the missing transition point.

## Architectural Boundaries

The recommended composition must remain:

- read-only and advisory;
- Platform Core-owned;
- deterministic and replay-visible;
- fail-closed on material ambiguity;
- incapable of authorizing implementation;
- incapable of invoking Providers or Workers;
- independent of Human Interface-specific wording or state ownership;
- incapable of repository, governance, replay, deployment, or constitutional mutation;
- subordinate to existing certification and governance authorities.

All Human Interfaces may consume and render the same validated objective artifact, but they must not infer, amend, approve, or execute the objective independently.

## Audit Conclusion

Platform Core can already infer the observed project objective from existing deterministic evidence. The redundant clarification is a conservative policy outcome caused by a missing first-class objective composition and an over-specific architecture-outcome slot schema. Existing coverage and planning compositions already provide the downstream audit and plan computations.

The smallest safe correction is one canonical composition binding between complete-request interpretation and clarification necessity. No new inference engine, planning engine, or Platform subsystem is justified.

## Final Verdict

`PLATFORM_CORE_PROJECT_OBJECTIVE_INFERENCE_REUSE_WITH_MINIMAL_CANONICAL_COMPOSITION_BINDING`
