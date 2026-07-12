# G23-06A Constitutional Certification Routing Verification Audit

Status: completed

Date: 2026-07-12

## Executive Summary

The observed Development Composition Plan result was produced by a stale
operational execution surface. Persisted artifact 211 proves that the executing
router did not expose Architectural Meta-Audit or the G23-05C constitutional
assessment rule. The rule was therefore unreachable, not entered and then
rejected.

Replaying the exact request through a newly imported current-source router
selects `PLATFORM_ARCHITECTURAL_META_AUDIT_COMPOSITION` with score 100,
reduces Development Composition Plan to 0, and reaches
`PLATFORM_CORE_CONSTITUTIONAL_ASSESSMENT_RULE_V1`.

With persisted workspace replay evidence, the rule produces the substantive
constitutional verdict and `PRESENTATION_READY`. Without replay evidence it
fails closed as designed. Restarting the operational `aicli` process and
revalidating with its existing workspace state is sufficient. No bounded code
correction is indicated.

## Operational Evidence Source

The authoritative evidence is:

`.runtime/aicli/AICLI-REFERENCE-SESSION/uhi_project_services/211_uhi_project_context_recorded.json`

It records the complete G23-06 request, Project Objective, work type, route
descriptors, candidate scores, selected service, invoked service response and
canonical presentation.

The request was a new top-level `AUDIT_ONLY` request. It had no clarification
continuity artifact.

## Route Classification

The operational process assigned:

- requested work type: `AUDIT_ONLY`;
- prepared work type: `AUDIT_ONLY`;
- canonical query class: `DEVELOPMENT_COMPOSITION_PLAN`;
- selected service: `PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_RUNTIME`;
- route status: `ROUTE_READY`;
- service invoked: true;
- presentation status: `PRESENTATION_READY`.

The presentation summary was:

`Existing certified Platform capabilities satisfy the requested composition.`

The recorded Project Objective was:

`Resolve report through reuse analysis, governed development plan, audit or analysis as AUDIT_ONLY.`

## Candidate Scores

The operational candidate set was:

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

`ARCHITECTURAL_META_AUDIT` did not participate. It is absent from both the
recorded candidate list and recorded route descriptors.

The Development Composition Plan route therefore won deterministically inside
that loaded process, but it did not legitimately represent the current
canonical routing contract. Its score came from an older classifier that
treated inventory and expected-deliverable planning language as route targets.

## Current-Source Route Verification

Replaying the exact persisted query in a newly imported current-source process
produces:

| Candidate | Score | Evidence available |
|---|---:|---|
| `PLATFORM_ARCHITECTURAL_META_AUDIT_COMPOSITION` | 100 | true |
| `PLATFORM_KNOWLEDGE_RUNTIME` | 95 | true |
| `PLATFORM_PROJECT_OBJECTIVE_INFERENCE_RUNTIME` | 35 | true |
| `DETERMINISTIC_ROOT_CAUSE_TRACE_RUNTIME` | 0 | false |
| `GENERATION_CERTIFICATION_COMPOSITION_SERVICE` | 0 | true |
| `GOVERNED_DEVELOPMENT_RUNTIME` | 0 | true |
| `PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_RUNTIME` | 0 | true |
| `PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_RUNTIME` | 0 | true |
| `PLATFORM_DURABLE_GOVERNED_WORK_RUNTIME` | 0 | false |

Current source classifies the request as `ARCHITECTURAL_META_AUDIT` because it
contains canonical constitutional-certification and constitutional-completion
wording. Clause-role-aware scoring excludes the capability inventory and
deliverable criteria from Development Composition Plan scoring.

No uncovered wording variant remains for this exact request.

## Composition Entry Verification

The operational service response is a
`PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_ARTIFACT_V1`. It contains planning,
coverage, residual-gap and durable-work preparation fields. It contains no:

- `architectural_meta_audit_status`;
- `architectural_certification_assessment`;
- `constitutional_assessment`;
- `constitutional_assessment_hash`.

Thus the observed execution never entered the Architectural Meta-Audit
composition.

The current-source replay enters
`PLATFORM_ARCHITECTURAL_META_AUDIT_COMPOSITION`, composes existing registry,
governance, replay and Project Objective evidence, and creates the
constitutional assessment artifact.

## Constitutional Rule Reachability

The operational descriptor set proves that G23-05C was not loaded. The rule
could not be reached from artifact 211.

Current-source behavior is:

- without workspace replay evidence:
  - `CONSTITUTIONAL_ASSESSMENT_FAILED_CLOSED`;
  - `CONSTITUTIONAL_CERTIFICATION_NOT_DETERMINED`;
  - missing evidence: `replay lineage evidence`;
  - presentation: `PRESENTATION_FAILED_CLOSED`;
- with existing persisted workspace replay reference and artifact hash:
  - `CONSTITUTIONAL_ASSESSMENT_READY`;
  - verdict:
    `PLATFORM_CORE_CONSTITUTIONALLY_READY_AS_STABLE_DETERMINISTIC_COGNITION_AND_GOVERNANCE_INFRASTRUCTURE_WITH_BOUNDED_STABILIZATION_REMAINING`;
  - presentation: `PRESENTATION_READY`.

This verifies both reachability and fail-closed behavior. The rule does not
require a new Provider, Worker, discovery service or peer route.

## First Divergence

The first deterministic divergence is route descriptor and candidate
construction inside the already-running operational Python process.
Architectural Meta-Audit is absent before scoring and selection occur. The
process then applies its older planning/durable scoring behavior, sorts those
candidates at 100 and selects Development Composition Plan.

The divergence occurs before:

- Architectural Meta-Audit service invocation;
- constitutional evidence composition;
- G23-05C rule application;
- constitutional verdict creation;
- constitutional presentation.

## Architectural Ownership

- Source route descriptors, clause-role scoring and route selection: Unified
  Platform Query Router.
- Constitutional evidence composition and decision rule: existing
  Architectural Meta-Audit composition.
- Replay evidence: Platform Core workspace/replay services.
- Canonical verdict projection: Platform Presentation Layer.
- Process/module freshness: operational process and deployment boundary.
- `aicli`: transport and rendering only; it does not own classification.

No evidence assigns responsibility to a Provider or Worker. Neither was
invoked by this audit.

## Minimal Recommendation

No code correction is required.

1. Exit the currently running `aicli` process completely.
2. Confirm the new invocation uses the current repository/environment rather
   than a stale installed source tree.
3. Start a new `./aicli` process so Python imports the current route descriptors,
   G23-05C rule and presentation binding.
4. Resubmit the G23-06 request in the existing replay-backed workspace session.
5. Verify that the result records:
   - selected service `PLATFORM_ARCHITECTURAL_META_AUDIT_COMPOSITION`;
   - query class `ARCHITECTURAL_META_AUDIT`;
   - `constitutional_assessment_rule` equal to
     `PLATFORM_CORE_CONSTITUTIONAL_ASSESSMENT_RULE_V1`;
   - a replay-backed constitutional verdict.

If a newly started process still exposes only the eight recorded descriptors,
the executable or environment is loading a stale installed source tree; that
operational path must be corrected before further architectural changes are
considered.

## Final Deterministic Verdict

`CONSTITUTIONAL_CERTIFICATION_CURRENT_SOURCE_VERIFIED_OPERATIONAL_PROCESS_RESTART_REQUIRED`

The current Platform Core implementation routes and evaluates the exact
request correctly. The observed Development Composition Plan result is stale
operational execution, not an uncovered wording variant, composition-entry
defect or missing constitutional rule binding.
