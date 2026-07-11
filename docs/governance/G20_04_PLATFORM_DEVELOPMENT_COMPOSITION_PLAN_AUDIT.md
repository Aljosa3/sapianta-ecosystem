# G20-04 Platform Development Composition Plan Audit

Status: AUDIT COMPLETE

Date: 2026-07-11

Scope: `AUDIT_ONLY` architectural review of whether Platform Core can compose
a canonical governed development plan from existing deterministic services and
evidence. This audit does not modify code, tests, runtime behavior, Human
Interfaces, replay, governance, certification, Providers, Workers, or existing
documentation other than this report.

## Executive Summary

Platform Core already contains nearly all deterministic information required
to construct a canonical governed Development Composition Plan.

Existing services already provide:

- capability and service discovery;
- certified capability ownership and evidence;
- multi-capability coverage and residual gaps;
- known certified compositions;
- minimal Platform extension classification;
- project knowledge reuse and implementation history;
- advisory execution-plan structures;
- governance checkpoints and risk previews;
- replay plans and replay-visible planning artifacts;
- improvement implementation-plan structures;
- implementation manifests and validation targets;
- certification and supersession dependencies;
- approval and execution-request boundaries.

No new planning subsystem, capability registry, certification engine,
governance authority, replay system, Provider runtime, Worker runtime, or Human
Interface planning authority is required.

The remaining gap is one deterministic transformation:

```text
Platform capability composition coverage
-> ordered governed development composition plan
```

Current planning runtimes require callers to supply the worker sequence,
requested capabilities, expected artifacts, repository impacts, plan text,
scope, constraints, targets, and validation. They validate and record those
inputs, but they do not derive them from capability coverage, residual gaps,
certified composition metadata, governance dependencies, certification
dependencies, and replay dependencies.

The exact missing capability is:

`CANONICAL_CAPABILITY_COVERAGE_TO_GOVERNED_DEVELOPMENT_PLAN_COMPOSITION`

This should be implemented, if authorized in a future milestone, as another
bounded read-only Platform Core composition service.

Final verdict:

`PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_REUSE_WITH_MINIMAL_CANONICAL_COMPOSITION_BINDING`

## Existing Reusable Platform Capabilities

| Existing capability | Current responsibility | Development-plan contribution | Reuse readiness |
| --- | --- | --- | --- |
| Platform Knowledge Runtime | Capability existence, ownership, certification, implementation owner, evidence, reuse advice | Canonical reusable-capability context | High |
| Platform Capability Composition Coverage Runtime | Request facets, certified capability coverage, known compositions, residual gaps, minimal extension | Canonical planning input and scope boundary | High |
| Platform Capability Certification Registry | Certification state, scope, milestone, implementation owner, evidence, supersession | Certification prerequisites and authoritative component identity | High |
| Generation Certification Composition Service | Evidence profiles, capability requirements, governance/runtime/replay dependencies, completeness policy | Certified precedent for explicit dependency composition | High |
| Unified Platform Query Router | Service descriptors, query classes, required inputs, implementation owners, response types | Service-binding and required-input metadata | High |
| Canonical Platform Presentation Layer | Stable presentation model over heterogeneous Platform artifacts | Human Interface rendering target | High |
| Project Knowledge Reuse | Known targets, certified artifacts, milestones, implementation history, reuse classification | Existing-work and duplicate-work avoidance | High |
| Project Guidance | Active objective, pending clarification/approval, recommended next governed action | Current lifecycle and next-action context | High |
| Platform Core Execution Planning Service | Advisory requested capabilities, worker sequence, expected artifacts, repository impact, governance checkpoints, replay plan, risk summary | Existing plan structure and planning boundary | High as downstream artifact pattern; derivation is incomplete |
| OCS Execution Preview | Advisory execution plan and descriptive mutation preview | Non-authorizing sequence and impact representation | High |
| Governance Preview | Governance checkpoints, confirmation validation, risk classification | Governance dependency and approval-boundary representation | High |
| Replay Preview | Replay plan and append-only preview persistence | Replay dependencies and evidence expectations | High |
| Improvement Implementation Planning Runtime | Plan scope, constraints, artifact targets, validation, approval lineage | Detailed implementation-plan structure | High for approved improvement chains; not a general composition planner |
| Implementation Manifest Runtime | Exact paths, operations, content hashes, tests, deterministic manifest | Later exact mutation boundary | High downstream; too late and too concrete for initial composition planning |
| Implementation Summary Runtime | Planned functionality, files, tests, limitations, lineage | Human-readable implementation summary | High downstream |
| Implementation Plan to Execution Request | Converts an approved plan into a non-executing request with explicit authorization separation | Planning-to-execution boundary | High downstream; must remain separate |
| Replay Observation and Replay Certification | Deterministic replay observations and validated execution certification | Replay and certification dependencies | High within existing contracts |
| Governance evidence | Constitutional boundaries, lifecycle rules, reports, validation and known limitations | Governance constraints and evidence references | High |

## Development Planning Analysis

### Information already available

Platform Core can already determine, without Providers, Workers, or Human
Interface authority:

1. Which request facets exist.
2. Which certified capabilities cover each facet.
3. Which certified compositions already cover multiple facets.
4. Which facets remain uncovered.
5. Whether the smallest extension is no change, reuse of one capability, reuse
   of a certified composition, a minimal new composition, or genuinely new
   capability work.
6. Which components own and implement the reusable capabilities.
7. Which governance evidence certifies those capabilities.
8. Which route descriptors and inputs bind the relevant Platform services.
9. Which generation evidence profile dependencies apply to Generation
   Certification.
10. Which project milestones, artifacts, and implementation-history records
    already exist.
11. Which governance checkpoints, replay expectations, approval boundaries,
    and validation structures existing planning artifacts use.

This is sufficient source information for deterministic plan composition.

### Existing advisory execution planning

`run_platform_core_execution_plan_preview(...)` already produces a
replay-visible advisory plan containing:

- selected worker sequence;
- requested capabilities;
- expected artifacts;
- potential repository impact;
- replay plan;
- governance checkpoints;
- execution risk summary;
- descriptive mutation preview;
- explicit non-execution and non-mutation flags.

Its architecture is correctly decomposed across Platform Core, OCS,
Governance, Replay, capability lookup, and Worker preview owners.

However, the service accepts caller-provided `worker_sequence`,
`requested_capabilities`, `expected_artifacts`, and
`potential_repository_impacts`. Defaults remain G8 preview defaults. The
service does not consume G20 capability coverage and cannot derive a minimal
implementation order from residual gaps.

### Existing improvement implementation planning

`create_improvement_implementation_plan(...)` already records:

- approved improvement lineage;
- plan source and plan text;
- scope and constraints;
- planned artifact targets;
- planned validation;
- replay reference;
- non-mutation and non-execution boundaries.

It correctly requires a prior approved improvement chain. The caller supplies
the substantive plan content. It is not a general pre-implementation
composition planner and should not be broadened to infer capability coverage.

### Existing implementation manifests

Implementation Manifest, validation, mutation authorization, summary, and
certification runtimes provide deterministic downstream contracts for exact
file operations, tests, content hashes, authorization continuity, and final
certification.

These contracts are reusable plan targets and dependencies. They should not be
used as the initial planning service because they assume an already concrete
implementation bundle and, in some paths, CREATE_ONLY mutation semantics.

## Composition Analysis

A canonical Development Composition Plan can be composed entirely from
existing Platform services.

Recommended source precedence:

1. Platform Capability Composition Coverage artifact for request facets,
   reusable capabilities, certified compositions, residual gaps, and minimal
   extension.
2. Capability Certification Registry for canonical ownership,
   implementation, certification, evidence, and supersession.
3. Platform Knowledge and Project Knowledge Reuse for existing work,
   implementation history, milestones, and duplicate-work avoidance.
4. Query Router descriptors for service bindings, required inputs, and result
   artifact types.
5. Generation Evidence Profiles and certification reports for explicit
   certification dependencies.
6. Constitutional and governance evidence for mutation, approval, validation,
   release, and authority constraints.
7. Replay Preview, Replay Observation, and Replay Certification contracts for
   replay dependencies.
8. Execution Planning and OCS preview structures for ordered advisory work and
   impact representation.
9. Improvement Plan, Manifest, Summary, Authorization, Validation, Mutation,
   and Certification contracts for downstream artifact sequencing.

### Deterministic implementation ordering

The plan should derive an order from dependency classes rather than inventing
an unconstrained task list. A governance-preserving canonical order is already
implicit in existing contracts:

```text
1. reuse and existing-capability bindings
2. residual semantic or composition gap
3. canonical service artifact contract
4. Query Router binding, when required
5. Canonical Presentation binding, when required
6. capability certification metadata and governance evidence
7. focused fail-closed regression coverage
8. governance conformance and broader validation
9. replay-visible certification evidence
10. later approval/authorization before any execution or mutation
```

This ordering must remain advisory. It does not authorize repository mutation,
Provider use, Worker dispatch, certification issuance, deployment, or server
mutation.

## Gap Analysis

### Existing capabilities that must not be duplicated

- capability discovery and coverage;
- certification registry and supersession validation;
- known composition discovery;
- Platform service routing;
- canonical presentation;
- project knowledge reuse;
- governance checkpoint and risk previews;
- replay planning and persistence;
- improvement-plan recording;
- implementation manifests and summaries;
- approval, authorization, mutation, validation, and certification chains.

### Exact missing capability

The precise missing capability is:

`CANONICAL_CAPABILITY_COVERAGE_TO_GOVERNED_DEVELOPMENT_PLAN_COMPOSITION`

It must transform an existing coverage artifact and governance context into one
canonical development-plan artifact containing:

- source request and coverage artifact reference/hash;
- reusable capabilities and certification evidence;
- reusable certified compositions;
- uncovered residual gaps;
- required implementation work limited to residual gaps;
- ordered implementation stages and dependency edges;
- governance dependencies and checkpoints;
- certification dependencies and expected evidence;
- replay dependencies and expected replay artifacts;
- router and presentation bindings, only when needed;
- expected implementation files or artifact classes at an advisory level;
- required focused and conformance validation;
- known limitations and unresolved ambiguity;
- minimal implementation boundary;
- human approval and execution-authorization separation;
- deterministic artifact hash.

### First deterministic stopping point

The first stopping point is after capability coverage and before development
sequence derivation.

The G20-03 coverage runtime returns the correct reusable capabilities,
compositions, residual gaps, and minimal extension. Existing execution planning
can represent an ordered plan, governance checkpoints, replay plan, and risk
summary. No canonical binding converts the former into the latter.

Consequently, a caller still has to choose:

- which residual gaps become implementation stages;
- their dependency order;
- which governance and certification evidence is required;
- which replay artifacts are expected;
- which router or presentation bindings are necessary;
- which validations prove completion.

That manual transition is the minimal canonical composition gap.

### Not missing

The audit does not find a need for:

- a new semantic planning engine;
- an LLM planning subsystem;
- a new capability or certification registry;
- a new governance authority;
- a new replay subsystem;
- a new execution runtime;
- a new Worker or Provider selection system;
- Human Interface planning logic;
- autonomous implementation or mutation.

## Minimal Canonical Composition Recommendation

If implementation is authorized in a future milestone, add one bounded,
read-only Platform Core Development Composition Plan service.

Its responsibilities should be limited to:

1. Accept a validated capability-composition coverage artifact and optional
   workspace context.
2. Validate the coverage artifact hash and fail closed on ambiguity or
   contradiction.
3. Reuse certification records and governance evidence for every selected
   capability and composition.
4. Convert residual gaps into bounded implementation work items.
5. Derive deterministic ordering from explicit dependency classes.
6. Reuse existing governance checkpoint, replay plan, risk, validation,
   manifest, summary, and certification contracts as referenced downstream
   stages.
7. Return one canonical hash-bound advisory Development Composition Plan.
8. Expose the plan through the Unified Query Router.
9. Normalize it through the Canonical Presentation Layer.

The service should not record durable execution authority or invoke downstream
mutation runtimes. It should describe required future artifacts and approvals,
not create or satisfy them.

Recommended conceptual flow:

```text
development request
-> Platform Capability Composition Coverage
-> certified capability and composition evidence
-> residual implementation gaps
-> governance/certification/replay dependency composition
-> deterministic implementation ordering
-> canonical advisory Development Composition Plan
-> Canonical Platform Presentation
-> Human Interface rendering
```

This gap is comparable in size to the G19 Platform Knowledge, Query Router, and
Presentation bindings and the G20 Generation Certification and Capability
Coverage composition services.

## Canonical Human Interface Consumption

The resulting plan can become the canonical planning artifact consumed by all
Human Interfaces, subject to strict ownership separation.

Human Interfaces may:

- submit the development request;
- receive the canonical plan through Platform Core;
- render reusable capabilities, gaps, order, dependencies, boundaries, and
  required approvals;
- collect explicit human approval through existing governed paths.

Human Interfaces must not:

- construct or reorder the plan;
- select capabilities or services;
- infer governance, certification, or replay dependencies;
- authorize execution from plan presentation alone;
- invoke Providers or Workers;
- mutate repository or governance state;
- treat the advisory plan as certification or execution evidence.

The Canonical Platform Presentation Layer should remain the normalized output
surface. No `aicli`-specific planning semantics are required.

## Architectural Boundaries

A future Development Composition Plan service must preserve:

- Platform Core ownership of planning composition;
- OCS ownership of orchestration and advisory execution preview semantics;
- Governance ownership of policy, approval, and authorization;
- Replay ownership of replay planning and reconstruction;
- Certification owners and evidence authority;
- Worker Platform ownership of Worker capabilities and execution;
- Provider Platform ownership of Provider invocation;
- Human Interfaces as thin adapters;
- explicit planning, approval, authorization, execution, mutation, validation,
  and certification separation;
- deterministic hashes and fail-closed behavior;
- replay-visible evidence without source replay mutation;
- known limitation visibility;
- release discipline and no direct server mutation.

It must not:

- duplicate existing planning or execution runtimes;
- convert a plan directly into execution authority;
- fabricate files, tests, capability coverage, or certification state;
- broaden Improvement Implementation Planning beyond its approved chain;
- weaken implementation manifest or mutation authorization contracts;
- invoke Providers or Workers during deterministic plan composition;
- introduce autonomous constitutional or governance mutation;
- move planning ownership into `aicli` or any other Human Interface.

## Implementation Readiness

Implementation readiness is high because the required source and downstream
contracts already exist.

A minimal future implementation should add only:

- one canonical Development Composition Plan artifact;
- one deterministic coverage-to-plan composition function;
- explicit dependency classes and ordering rules;
- one Query Router descriptor and adapter;
- one Canonical Presentation normalization adapter;
- focused fail-closed regression coverage;
- implementation-scope certification metadata after validation.

This audit does not implement that recommendation.

## Final Verdict

`PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_REUSE_WITH_MINIMAL_CANONICAL_COMPOSITION_BINDING`

Platform Core already contains the deterministic capability, composition,
governance, certification, replay, planning, manifest, validation, and
authorization contracts needed for a canonical governed development plan. The
only missing capability is the bounded composition that transforms capability
coverage into an ordered, dependency-complete, advisory development plan.
