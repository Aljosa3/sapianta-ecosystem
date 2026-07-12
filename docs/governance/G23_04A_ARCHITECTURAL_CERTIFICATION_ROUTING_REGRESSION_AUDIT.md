# G23-04A Architectural Certification Routing Regression Audit

Status: completed

Date: 2026-07-12

## Executive Summary

The observed `PLATFORM_KNOWLEDGE_RUNTIME` selection is not evidence that the
G23-03B synonym scoring regressed. Replay shows a two-turn operational path:

1. the original G23-04 request contained the implemented phrase
   `architectural certification audit`, but its recorded router candidate set
   did not contain `PLATFORM_ARCHITECTURAL_META_AUDIT_COMPOSITION`; and
2. Platform Core requested clarification, after which the clarification reply
   was routed as a new query. That reply no longer contained any contiguous
   G23-03B synonym and deterministically selected Platform Knowledge.

The behavior is therefore a combination of an operational route-availability
condition and an uncovered clarification wording/continuity variant. It is not
a need for a new architectural certification runtime or a peer multi-route
router.

## Execution Trace

### Original request

Replay artifact:

`.runtime/aicli/AICLI-REFERENCE-SESSION/uhi_project_services/207_uhi_project_context_recorded.json`

The request was titled `G23-04 — Platform Core Transition-to-Execution
Certification Audit` and explicitly requested:

`Perform an AUDIT_ONLY architectural certification audit.`

The recorded result selected:

- service: `PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_RUNTIME`;
- query class: `DEVELOPMENT_COMPOSITION_PLAN`.

The recorded candidate scores were:

| Candidate route | Query class | Score |
|---|---|---:|
| `PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_RUNTIME` | `DEVELOPMENT_COMPOSITION_PLAN` | 100 |
| `PLATFORM_DURABLE_GOVERNED_WORK_RUNTIME` | `DURABLE_GOVERNED_WORK` | 100 |
| `PLATFORM_KNOWLEDGE_RUNTIME` | `ARCHITECTURAL_KNOWLEDGE` | 95 |
| `PLATFORM_PROJECT_OBJECTIVE_INFERENCE_RUNTIME` | `PROJECT_OBJECTIVE_INFERENCE` | 35 |
| `DETERMINISTIC_ROOT_CAUSE_TRACE_RUNTIME` | `RUNTIME_CAUSALITY` | 0 |
| `GENERATION_CERTIFICATION_COMPOSITION_SERVICE` | `GENERATION_CERTIFICATION` | 0 |
| `GOVERNED_DEVELOPMENT_RUNTIME` | `GOVERNED_DEVELOPMENT_INTENT` | 0 |
| `PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_RUNTIME` | `CAPABILITY_COMPOSITION_DISCOVERY` | 0 |

`ARCHITECTURAL_META_AUDIT` did not participate. It is absent from both the
recorded candidates and recorded route descriptors. Therefore the original
request could not select the G23-03B route despite containing an implemented
synonym.

### Clarification reply

Replay artifact:

`.runtime/aicli/AICLI-REFERENCE-SESSION/uhi_project_services/208_uhi_project_context_recorded.json`

The operational query that selected Platform Knowledge began:

`The certification workflow architecture decision shall determine ...`

It requested a `canonical certification verdict`, but did not contain any of
the G23-03B contiguous bindings:

- `architectural certification audit`;
- `platform certification audit`;
- `platform architectural certification`;
- `platform certification assessment`;
- `architectural certification`.

Its recorded classification was:

- service: `PLATFORM_KNOWLEDGE_RUNTIME`;
- query class: `ARCHITECTURAL_KNOWLEDGE`;
- Platform Knowledge classification:
  `CERTIFIED_CAPABILITY_WITH_PROJECT_REUSE_CONTEXT`.

The recorded candidate scores were:

| Candidate route | Query class | Score |
|---|---|---:|
| `PLATFORM_KNOWLEDGE_RUNTIME` | `ARCHITECTURAL_KNOWLEDGE` | 85 |
| `GOVERNED_DEVELOPMENT_RUNTIME` | `GOVERNED_DEVELOPMENT_INTENT` | 39 |
| `DETERMINISTIC_ROOT_CAUSE_TRACE_RUNTIME` | `RUNTIME_CAUSALITY` | 0 |
| `GENERATION_CERTIFICATION_COMPOSITION_SERVICE` | `GENERATION_CERTIFICATION` | 0 |
| `PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_RUNTIME` | `CAPABILITY_COMPOSITION_DISCOVERY` | 0 |
| `PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_RUNTIME` | `DEVELOPMENT_COMPOSITION_PLAN` | 0 |
| `PLATFORM_DURABLE_GOVERNED_WORK_RUNTIME` | `DURABLE_GOVERNED_WORK` | 0 |
| `PLATFORM_PROJECT_OBJECTIVE_INFERENCE_RUNTIME` | `PROJECT_OBJECTIVE_INFERENCE` | 0 |

Again, the recorded operational candidate set did not include Architectural
Meta Audit.

## Current-Source Reproduction

Routing the exact clarification reply through the current source produces:

| Candidate route | Query class | Score |
|---|---|---:|
| `PLATFORM_KNOWLEDGE_RUNTIME` | `ARCHITECTURAL_KNOWLEDGE` | 75 |
| `GOVERNED_DEVELOPMENT_RUNTIME` | `GOVERNED_DEVELOPMENT_INTENT` | 39 |
| `DETERMINISTIC_ROOT_CAUSE_TRACE_RUNTIME` | `RUNTIME_CAUSALITY` | 0 |
| `GENERATION_CERTIFICATION_COMPOSITION_SERVICE` | `GENERATION_CERTIFICATION` | 0 |
| `PLATFORM_ARCHITECTURAL_META_AUDIT_COMPOSITION` | `ARCHITECTURAL_META_AUDIT` | 0 |
| `PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_RUNTIME` | `CAPABILITY_COMPOSITION_DISCOVERY` | 0 |
| `PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_RUNTIME` | `DEVELOPMENT_COMPOSITION_PLAN` | 0 |
| `PLATFORM_DURABLE_GOVERNED_WORK_RUNTIME` | `DURABLE_GOVERNED_WORK` | 0 |
| `PLATFORM_PROJECT_OBJECTIVE_INFERENCE_RUNTIME` | `PROJECT_OBJECTIVE_INFERENCE` | 0 |

The current implementation does include Architectural Meta Audit in candidate
evaluation, but it scores zero because the clarification wording falls outside
the canonical synonyms. Platform Knowledge wins deterministically.

The recorded Knowledge score is ten points higher than the isolated
current-source reproduction because the operational workspace supplied project
capability context. This affects the winning score, not the route conclusion.

## Root Cause

The first operational condition is route availability: the replayed router
descriptor set predates or otherwise does not expose the G23-03B
Architectural Meta-Audit route. The unchanged historical router version string
does not distinguish these source states, so the replay artifacts themselves
are the authoritative evidence of availability.

The second condition is clarification continuity. The original canonical
phrase was replaced by semantically related wording:

- original: `architectural certification audit`;
- clarification: `certification workflow architecture decision` and
  `canonical certification verdict`.

Those word orders are not G23-03B synonyms. When the clarification reply is
routed independently, the original canonical query class is not preserved as
an authoritative routing constraint.

## Architectural Ownership

- Original and clarification semantic continuity: Platform Core.
- Candidate classification and single-route selection: Unified Platform Query
  Router.
- Architectural certification composition: existing Architectural Meta-Audit
  adapter.
- Workspace and clarification lineage: Platform Core replay/workspace services.
- Human Interface: thin transport and rendering adapter only.
- Provider: not invoked by this audit.
- Worker: not invoked by this audit.

No ownership belongs in `aicli`, and no router redesign is indicated.

## Minimal Recommendation

Before changing classification, ensure the operational `aicli` execution path
loads a route descriptor set containing
`PLATFORM_ARCHITECTURAL_META_AUDIT_COMPOSITION`. A source implementation cannot
bind a route that is absent from the executing process or deployed runtime.

After route availability is confirmed, the smallest canonical correction is
to preserve the original `ARCHITECTURAL_META_AUDIT` query class across
clarification continuity when the clarification answers the same governed
request. This is narrower and more semantically stable than continually adding
word-order aliases.

If continuity preservation is conclusively unavailable, the bounded fallback
is to add the observed variants `certification workflow architecture decision`
and `canonical certification verdict` to the existing Architectural Meta-Audit
classifier. No new runtime or peer multi-route execution is required.

## Final Deterministic Verdict

`ARCHITECTURAL_CERTIFICATION_ROUTING_VARIANCE_CAUSED_BY_OPERATIONAL_ROUTE_ABSENCE_AND_UNCOVERED_CLARIFICATION_CONTINUITY`

G23-03B remains correct for its implemented canonical synonyms. The observed
Platform Knowledge result is reproducible for the clarification wording, but
the operational replay also proves that the G23-03B route was unavailable to
that execution. The required remediation, if authorized later, is bounded
route exposure and clarification-class continuity—not architectural expansion.
