# G23-05B Constitutional Certification Misrouting Root Cause Audit

Status: completed

Date: 2026-07-12

## Executive Summary

The operational evidence confirms three bounded conditions:

1. Both observed requests executed against a router surface that did not expose
   `ARCHITECTURAL_META_AUDIT` or
   `PLATFORM_ARCHITECTURAL_META_AUDIT_COMPOSITION` at all.
2. Current source correctly routes the original constitutional-completion
   request to Architectural Meta-Audit, but the current composition contract
   concludes only that certified capabilities satisfy a requested composition.
   It does not apply constitutional completion criteria or issue the requested
   substantive constitutional verdict.
3. The follow-up was a new independent top-level request, not a clarification
   continuation. It scored Platform Knowledge at 95 and Root Cause Trace at 60.
   Root Cause Trace also lacked bound runtime/replay result evidence, so the
   response became an isolated certification-registry lookup.

No new cognition subsystem is missing. Immediate operational revalidation
requires a newly started process that loads the current route descriptors. The
smallest substantive correction is a bounded constitutional assessment-rule
binding inside the existing Architectural Meta-Audit composition.

## Operational Evidence Sources

The authoritative persisted sources are:

- `.runtime/aicli/AICLI-REFERENCE-SESSION/uhi_project_services/209_uhi_project_context_recorded.json`;
- `.runtime/aicli/AICLI-REFERENCE-SESSION/uhi_project_services/210_uhi_project_context_recorded.json`.

Both artifacts contain the original router query, development intent, Project
Objective, full candidate list, selected route, service response, and canonical
presentation. Neither contains a clarification-continuity artifact.

## Exact Request Reproduction

### Constitutional completion request

The persisted original and normalized router query are identical apart from
the router's ordinary required-string boundary trimming. Its canonical request
was titled:

`G23-05 — Platform Core Constitutional Completion Certification Audit`

Its operative instruction was:

`Perform an AUDIT_ONLY constitutional certification audit.`

It asked whether Platform Core could be constitutionally regarded as the
stable deterministic cognition and governance infrastructure for AiGOL, with
future generations primarily focused on governed execution.

Recorded state:

- clarification history: none;
- requested/prepared work type: `AUDIT_ONLY` / `AUDIT_ONLY`;
- Project Objective: resolve the G23-04B continuation through reuse analysis,
  governed development planning, and audit/analysis;
- selected query class: `DEVELOPMENT_COMPOSITION_PLAN`;
- selected service: `PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_RUNTIME`;
- route status: `ROUTE_READY`;
- service invoked: true;
- presentation status: `PRESENTATION_READY`;
- presentation summary: `Existing certified Platform capabilities satisfy the requested composition.`

Recorded candidate scores:

| Candidate | Query class | Score | Evidence available |
|---|---|---:|---|
| `PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_RUNTIME` | `DEVELOPMENT_COMPOSITION_PLAN` | 100 | true |
| `PLATFORM_DURABLE_GOVERNED_WORK_RUNTIME` | `DURABLE_GOVERNED_WORK` | 100 | true |
| `PLATFORM_KNOWLEDGE_RUNTIME` | `ARCHITECTURAL_KNOWLEDGE` | 95 | true |
| `PLATFORM_PROJECT_OBJECTIVE_INFERENCE_RUNTIME` | `PROJECT_OBJECTIVE_INFERENCE` | 35 | true |
| `DETERMINISTIC_ROOT_CAUSE_TRACE_RUNTIME` | `RUNTIME_CAUSALITY` | 0 | false |
| `GENERATION_CERTIFICATION_COMPOSITION_SERVICE` | `GENERATION_CERTIFICATION` | 0 | true |
| `GOVERNED_DEVELOPMENT_RUNTIME` | `GOVERNED_DEVELOPMENT_INTENT` | 0 | true |
| `PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_RUNTIME` | `CAPABILITY_COMPOSITION_DISCOVERY` | 0 | true |

Architectural Meta-Audit did not participate in the recorded candidate set.

### Follow-up root-cause request

The persisted original and normalized router query are likewise identical
apart from boundary trimming. It was titled:

`G23-05A — Constitutional Certification Composition Audit`

Its operative instruction was:

`Perform an AUDIT_ONLY deterministic root cause audit.`

It asked why capability sufficiency was returned instead of the requested
constitutional certification assessment.

Recorded state:

- clarification history: none;
- requested/prepared work type: `AUDIT_ONLY` / `AUDIT_ONLY`;
- Project Objective: resolve the prior operational result through reuse
  analysis, certified composition discovery, and audit/analysis;
- selected query class: `ARCHITECTURAL_KNOWLEDGE`;
- selected service: `PLATFORM_KNOWLEDGE_RUNTIME`;
- route status: `ROUTE_READY`;
- service invoked: true;
- presentation status: `PRESENTATION_READY`;
- presentation summary: `DETERMINISTIC_ROOT_CAUSE_TRACE_BINDING exists as a certified Platform capability.`

Recorded candidate scores:

| Candidate | Query class | Score | Evidence available |
|---|---|---:|---|
| `PLATFORM_KNOWLEDGE_RUNTIME` | `ARCHITECTURAL_KNOWLEDGE` | 95 | true |
| `DETERMINISTIC_ROOT_CAUSE_TRACE_RUNTIME` | `RUNTIME_CAUSALITY` | 60 | false |
| `GOVERNED_DEVELOPMENT_RUNTIME` | `GOVERNED_DEVELOPMENT_INTENT` | 39 | true |
| `GENERATION_CERTIFICATION_COMPOSITION_SERVICE` | `GENERATION_CERTIFICATION` | 0 | true |
| `PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_RUNTIME` | `CAPABILITY_COMPOSITION_DISCOVERY` | 0 | true |
| `PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_RUNTIME` | `DEVELOPMENT_COMPOSITION_PLAN` | 0 | true |
| `PLATFORM_DURABLE_GOVERNED_WORK_RUNTIME` | `DURABLE_GOVERNED_WORK` | 0 | true |
| `PLATFORM_PROJECT_OBJECTIVE_INFERENCE_RUNTIME` | `PROJECT_OBJECTIVE_INFERENCE` | 0 | true |

Architectural Meta-Audit again did not participate in the recorded candidate
set.

## Active Route Availability Analysis

Both recorded `route_descriptors` arrays contain eight services and omit:

- `ARCHITECTURAL_META_AUDIT`;
- `PLATFORM_ARCHITECTURAL_META_AUDIT_COMPOSITION`;
- the G23-03B Architectural Certification descriptor and synonyms.

This proves that the actual process producing artifacts 209 and 210 did not
have those bindings loaded. The evidence cannot determine whether that process
was started before the source update or used another stale deployment surface,
because the router version constant remained
`G19_04_UNIFIED_PLATFORM_QUERY_ROUTER_V1` across the bounded additions.

Current source exposes the missing descriptor. Replaying request 209 through a
new current-source process produces:

- Architectural Meta-Audit: 100;
- Platform Knowledge: 95;
- Project Objective Inference: 35;
- all planning and durable-work candidates: 0.

It selects `PLATFORM_ARCHITECTURAL_META_AUDIT_COMPOSITION`. Therefore a
long-lived `aicli` process started before G23-02B/G23-03B must be restarted for
new Python descriptors and classifier code to become active. A new process is
also required when the operational command is using a stale installed or
deployed source tree.

## Constitutional Certification Route Analysis

The operational surface first diverged during candidate construction. It
treated inventory references to Development Composition Planning and Durable
Governed Work as routing targets, giving both 100, while no Architectural
Meta-Audit candidate existed. The first sorted candidate was Development
Composition Plan.

Current clause-role-aware scoring excludes architectural inventory and
criteria clauses from planning scores. Current G23-03B matching also finds the
phrase `Architectural Certification` in the request and gives Architectural
Meta-Audit 100. Thus the original operational misroute is a stale loaded-route
condition, not a current-source synonym defect.

The exact phrase `constitutional certification audit` is not itself one of the
G23-03B synonyms. The current request nevertheless routes correctly because it
also contains `Architectural Certification`. A shorter request containing only
constitutional-certification wording remains an uncovered variant, but it did
not cause this recorded current-source reproduction to fail.

## Follow-Up Root-Cause Route Analysis

The follow-up contains `root cause`, `cause`, and explanatory language, giving
Root Cause Trace 60. It also repeatedly contains `certified`, `capability`, and
composition/capability references. Platform Knowledge resolves
`DETERMINISTIC_ROOT_CAUSE_TRACE_BINDING` from the certification registry and
reaches its capped score of 95.

Root Cause Trace requires explicit runtime or replay evidence. The governed
read-only binding calls the router with only `query`, `workspace_state`, and
`created_at`; it does not bind the immediately preceding read-only result as
`runtime_result`, `user_visible_result`, `artifact_reference`, or
`replay_reference`. The Root Cause candidate therefore records
`runtime_or_replay_evidence` as missing.

The first deterministic transition to isolated knowledge lookup is candidate
selection after these scores are constructed: Knowledge is first at 95 and is
invoked, returning the one certified capability that best matches the query.
Architectural Meta-Audit cannot win on the current source either, because the
follow-up wording contains none of its architectural-completion or
architectural-certification synonyms.

## Query-Class Continuity Analysis

Artifacts 209 and 210 both have `clarification_continuity: null`. Request 209
completed as a governed read-only result. Request 210 then entered as a new
top-level request.

G23-04B clarification continuity must not be extended across this boundary.
Preserving the prior Architectural Meta-Audit class automatically would
incorrectly make a completed request control an independent later request.
The follow-up must be independently classified, while prior completed-result
evidence may be explicitly bound as causal evidence when its replay identity
matches the new request.

## Architectural Meta-Audit Capability Assessment

The current Architectural Meta-Audit composes:

- Platform Knowledge;
- Capability Certification Registry records;
- governance evidence references;
- workspace replay reference/hash when supplied;
- Project Objective evidence;
- optional Architectural Health Advisory.

It produces an integrated, replay-hashed architectural certification
assessment. It is more than presentation-only evidence readiness. However, its
ready verdict is currently fixed to:

`EXISTING_CERTIFIED_PLATFORM_CAPABILITIES_SATISFY_REQUESTED_COMPOSITION`

The corresponding summary states that existing certified capabilities provide
the required read-only architectural certification composition.

## Constitutional Assessment Capability Assessment

The current composition does not encode or evaluate constitutional completion
rules such as:

- complete ownership of every required Platform Core cognition responsibility;
- deterministic artifact coverage;
- governance, replay, and certification lineage continuity;
- Human Interface, Provider, Worker, approval, and authorization boundaries;
- whether remaining gaps are bounded stabilization rather than missing
  foundations;
- whether responsibility may transition toward governed execution.

The presentation faithfully projects the assessment supplied by the
composition. It cannot manufacture a substantive constitutional verdict while
its `semantic_content_invented` boundary remains false. This is therefore not
a presentation-only gap.

Selecting the correct route today answers that evidence and certified
capabilities are sufficient for composition. It does not deterministically
answer whether Platform Core may be constitutionally certified as AiGOL's
stable cognition and governance infrastructure.

## Exact First Divergence

For request 209, the first divergence is the stale operational router's
candidate construction: Architectural Meta-Audit is absent and architectural
inventory terms score planning/durable routes at 100.

For request 210, the first divergence is independent root-cause classification
without bound prior-result evidence: Root Cause scores 60 and is evidence
ineligible, while the knowledge probe resolves a certified capability and
scores 95. Candidate selection then invokes Platform Knowledge.

After route correction, the first remaining semantic divergence is inside the
Architectural Meta-Audit assessment builder: evidence sufficiency is converted
directly into composition sufficiency, with no constitutional assessment-rule
evaluation between them.

## Architectural Ownership

- Route descriptors, clause-aware scoring, and single-route selection:
  Unified Platform Query Router.
- Operational module/process freshness: operational process and deployment
  boundary, not `aicli` semantic ownership.
- Completed-result/replay evidence binding for root-cause queries: Platform
  Core Project Services and the existing router input contract.
- Architectural evidence composition: Architectural Meta-Audit composition.
- Constitutional assessment rules: Architectural Meta-Audit composition under
  existing governance and constitutional evidence authority.
- Isolated capability facts: Platform Knowledge.
- Replay-backed causal analysis: Deterministic Root Cause Trace.
- Projection of supplied semantic results: Canonical Platform Presentation
  Layer.
- Transport/rendering only: `aicli`.

No evidence assigns semantic, governance, execution, replay, or certification
authority to the Human Interface, Provider, or Worker.

## Minimal Canonical Recommendation

Immediate operational action requires no code correction: terminate any stale
long-lived `aicli` process and revalidate request 209 through a newly started
process that exposes `PLATFORM_ARCHITECTURAL_META_AUDIT_COMPOSITION`.

The single minimal substantive correction category is:

`constitutional assessment-rule binding`

The existing Architectural Meta-Audit should deterministically map canonical
constitutional criteria to its already-composed registry, governance, replay,
Project Objective, and advisory evidence; fail closed on missing required
evidence; and emit a bounded constitutional verdict. The existing presentation
can then project that verdict without gaining semantic authority.

Separately, a later bounded root-cause refinement may bind an explicitly
referenced prior completed read-only result and replay identity into the
existing Root Cause Trace input contract. That is not clarification continuity
and is not a prerequisite for the constitutional assessment itself.

No new cognition subsystem, peer multi-route router, Provider path, Worker
path, or `aicli` semantic behavior is required.

## Final Deterministic Verdict

`CONSTITUTIONAL_CERTIFICATION_MISROUTED_BY_STALE_OPERATIONAL_ROUTE_SURFACE_AND_BLOCKED_BY_MISSING_CONSTITUTIONAL_ASSESSMENT_RULE_BINDING`

The stale route surface explains the recorded Development Composition Plan and
Platform Knowledge results. Current source corrects the primary route after
process restart, but deterministic constitutional certification remains
unavailable until the existing meta-audit receives a bounded constitutional
assessment-rule binding.
