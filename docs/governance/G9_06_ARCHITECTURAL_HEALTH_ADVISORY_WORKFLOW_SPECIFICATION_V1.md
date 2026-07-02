# G9-06 Architectural Health Advisory Workflow Specification V1

Status: architectural health advisory workflow specified.

Final verdict: ARCHITECTURAL_HEALTH_ADVISORY_WORKFLOW_SPECIFIED

## 1. Executive Summary

G9-06 specifies how the certified Architectural Health projection participates in governed AiGOL development.

G8-17 certified that Architectural Health already emerges as a deterministic Platform Digital Twin projection. G9-05 certified that Architectural Health is ready for advisory participation in governed development. This specification defines the workflow contract for that participation.

Architectural Health remains:

- deterministic;
- replay-visible;
- advisory only;
- derived entirely from existing certified Platform Core evidence;
- non-authoritative;
- non-mutating;
- subordinate to Human and Governance authority;
- a Platform Digital Twin projection, not a subsystem.

Canonical workflow:

```text
Human Intent
-> Implementation
-> Platform Digital Twin
-> Architectural Health Projection
-> Advisory Findings
-> Human Review
-> Architecture Review
-> Certification
```

Architectural Health may identify risks, contradictions, missing evidence, responsibility leakage, boundary drift, and certification regressions. It must never approve execution, reject execution, modify implementation, certify artifacts, override Governance, override Replay, or override Human decisions.

## 2. Advisory Workflow

The Architectural Health advisory workflow is a deterministic evidence projection step inserted after implementation evidence exists and before formal architecture review.

Workflow sequence:

| Step | Owner | Purpose |
| --- | --- | --- |
| Human intent | Human / ACLI Next | Capture the requested development objective. |
| Implementation | Platform Core / Worker Platform / Codex hybrid where applicable | Produce implementation or documentation evidence. |
| Evidence capture | Replay / governance docs / validation records | Preserve implementation, validation, and boundary evidence. |
| Platform Digital Twin projection | Platform Digital Twin | Expose deterministic state from certified records. |
| Architectural Health projection | Architectural Health projection | Derive advisory findings from Digital Twin evidence. |
| Advisory findings | Architectural Health projection | Present deterministic warnings or confirmations. |
| Human review | Human | Decide how to treat advisory findings. |
| Architecture review | Governance review process | Evaluate ownership boundaries and unresolved findings. |
| Certification | Governance | Issue final verdict or require realignment. |

Architectural Health does not add a runtime authority. It adds an advisory evidence projection before architecture review.

## 3. Execution Timing

Architectural Health should be projected when implementation or specification evidence is available and before architecture review or certification closes the milestone.

Recommended execution points:

| Timing | Required? | Purpose |
| --- | --- | --- |
| After specification | Optional | Detect proposed ownership drift before implementation. |
| After implementation | Required for runtime capability reviews | Detect responsibility leakage or missing evidence before architecture review. |
| Before architecture review | Required when available | Provide advisory findings to reviewers. |
| After realignment | Recommended | Confirm whether previously detected warnings were resolved. |
| Before certification | Recommended | Surface unresolved advisory findings for Governance review. |

The canonical first operational placement is:

```text
Implementation
-> Platform Digital Twin
-> Architectural Health Projection
-> Advisory Findings
-> Human Review
-> Architecture Review
```

This placement is preferred because Architectural Health requires evidence to project. Running it before implementation may help specifications, but post-implementation projection is the first point where ownership, Replay, validation, and runtime surfaces are observable.

## 4. Input Evidence Model

Architectural Health consumes existing certified Platform Core evidence. It must not create new source authority.

Required input families:

| Input Family | Evidence Examples |
| --- | --- |
| Governance evidence | Final verdicts, certification reviews, authorization records, governance checkpoints. |
| Replay evidence | Replay references, reconstruction results, runtime evidence wrappers, fail-closed records. |
| Platform Digital Twin projections | Component state, ownership state, capability state, known gaps, lineage. |
| Ownership records | Certified owner matrices, architecture review ownership tables, boundary declarations. |
| Implementation artifacts | Runtime modules, Worker modules, coordinators, tests, implementation docs. |
| Validation evidence | `git diff --check`, py_compile, targeted pytest, validation Worker results. |
| Canonical mappings | Canonical projection records, source mappings, component-to-owner mappings. |
| Extension lineage | Specification, implementation, architecture review, realignment, certification chains. |
| Certification history | Prior final verdicts, leakage verdicts, realignment verdicts, closure verdicts. |

Required deterministic source fields:

- source path;
- source title;
- milestone id;
- source class;
- status;
- final verdict;
- component scope;
- expected owner;
- observed owner;
- evidence type;
- replay reference or documentation-only classification;
- validation evidence;
- known gaps;
- conflicting or stale evidence indicator.

If a required input is missing, Architectural Health must emit an advisory finding rather than synthesize evidence.

## 5. Platform Digital Twin Inputs

Architectural Health uses Platform Digital Twin projections as its aggregate evidence source.

Relevant Digital Twin slices:

| Digital Twin Slice | Architectural Health Use |
| --- | --- |
| Component ownership projection | Compare expected owner and observed implementation responsibility. |
| Capability lineage projection | Verify specification, implementation, review, and certification continuity. |
| Replay continuity projection | Detect missing, stale, or conflicting evidence. |
| Governance verdict projection | Identify final verdict chain and unresolved review routes. |
| Worker boundary projection | Detect execution logic escaping Worker Platform or policy entering Workers. |
| Interface boundary projection | Detect ACLI Next or other interfaces becoming orchestration owners. |
| Canonical mapping projection | Detect inconsistent or missing canonical mappings. |
| Known gap projection | Preserve deferred or partial capability visibility. |

Architectural Health must not become a second Digital Twin. It is a derived health view of Digital Twin data.

## 6. Advisory Output Model

Architectural Health output is a projection envelope, not an authority record.

Required output fields:

| Field | Requirement |
| --- | --- |
| `projection_id` | Stable replay-visible identifier. |
| `projection_type` | Must equal `ARCHITECTURAL_HEALTH_ADVISORY_PROJECTION_V1`. |
| `projection_version` | Workflow version. |
| `source_scope` | Milestones, paths, or runtime surfaces included. |
| `component_scope` | Component or capability under review. |
| `generated_from` | Platform Digital Twin source references. |
| `finding_count` | Number of advisory findings. |
| `findings` | Deterministic finding records. |
| `overall_advisory_status` | Derived advisory status. |
| `replay_references` | Replay references consumed or produced. |
| `governance_references` | Governance records and verdicts consumed. |
| `non_authority_statement` | Explicit statement that output does not certify or authorize. |
| `recommended_human_review` | Human-review guidance. |

Allowed `overall_advisory_status` values:

| Status | Meaning |
| --- | --- |
| `NO_ADVISORY_FINDINGS` | No deterministic warnings found in the input scope. |
| `ADVISORY_FINDINGS_PRESENT` | One or more non-blocking findings require human review. |
| `GOVERNANCE_REVIEW_RECOMMENDED` | Findings may affect certification or authority boundaries. |
| `ARCHITECTURE_REVIEW_REQUIRED` | Evidence indicates likely boundary or ownership issue requiring formal review. |
| `INSUFFICIENT_EVIDENCE` | Required evidence is missing, stale, partial, or conflicting. |

These statuses are advisory. Governance decides certification effect.

## 7. Finding Model

Each finding must include deterministic evidence and recommended human review.

Required finding fields:

| Field | Requirement |
| --- | --- |
| `finding_id` | Stable deterministic identifier. |
| `finding_type` | Controlled vocabulary finding type. |
| `severity` | Severity classification. |
| `affected_owner` | Certified Platform Core owner or boundary affected. |
| `affected_component` | Runtime, document, Worker, coordinator, interface, or projection affected. |
| `evidence` | Source-bound deterministic evidence. |
| `replay_references` | Replay references if available. |
| `governance_references` | Governance verdicts or checkpoints if available. |
| `canonical_mapping_references` | Mapping evidence if relevant. |
| `explanation` | Deterministic human-readable explanation. |
| `recommended_human_review` | Suggested review action for the Human or reviewer. |
| `authority_boundary_statement` | Statement that the finding is advisory only. |

Allowed finding types:

| Finding Type | Meaning |
| --- | --- |
| `responsibility_leakage` | Observed implementation responsibility appears owned by the wrong layer. |
| `ownership_inconsistency` | Expected owner and observed owner conflict. |
| `duplicated_responsibility` | A local component appears to duplicate certified owner behavior. |
| `architectural_boundary_violation` | A certified boundary appears crossed or weakened. |
| `certification_regression` | Current evidence conflicts with a prior certified verdict. |
| `architectural_drift_indicator` | Scope expanded beyond certified intent or roadmap. |
| `missing_replay_evidence` | Required Replay evidence or reference is absent. |
| `missing_governance_evidence` | Required Governance evidence or final verdict is absent. |
| `inconsistent_canonical_mapping` | Mapping evidence is missing, stale, or contradictory. |
| `known_gap_visibility` | Known limitation is at risk of being hidden or reframed. |

## 8. Severity Model

Severity classification is deterministic and advisory.

| Severity | Meaning | Required Human Review |
| --- | --- | --- |
| `info` | Evidence confirms expected boundary or records a non-risk observation. | Optional acknowledgement. |
| `low` | Minor documentation or traceability issue with no apparent authority impact. | Review during normal architecture review. |
| `medium` | Possible ownership, evidence, or boundary issue requiring explicit review. | Human review before certification. |
| `high` | Likely responsibility leakage, missing authority evidence, or Replay continuity gap. | Formal architecture review and Governance visibility recommended. |
| `critical` | Evidence suggests execution authority, Governance, Replay, or Human authority may be bypassed. | Certification should not proceed until Governance reviews. |

Severity does not approve or block execution by itself. It informs Human and Governance review.

## 9. Human Interaction Model

Architectural Health findings must be presented to the Human in a deterministic, evidence-backed form.

Presentation requirements:

- explain every finding;
- reference supporting source paths, verdicts, replay references, or mappings;
- identify affected Platform Core owner;
- classify severity;
- describe recommended human review;
- state that the finding is advisory;
- state that Human and Governance remain the decision authorities.

The Human may choose to:

- acknowledge findings and proceed to architecture review;
- request implementation realignment;
- request additional evidence;
- defer certification;
- ask Governance to review conflicting evidence;
- reject the milestone.

Architectural Health must never:

- approve execution;
- reject execution;
- modify implementation;
- create patches;
- dispatch Workers;
- certify artifacts;
- override Governance;
- override Replay;
- override Human decisions;
- hide or collapse findings into an opaque score.

## 10. Replay Integration

Architectural Health must be replay-visible.

Documentation-only projections may be replay-visible through:

- source document path;
- final verdict text;
- validation evidence;
- advisory finding references.

Runtime-produced projections, if implemented later, must record:

- projection input source list;
- source hashes where available;
- deterministic source ordering;
- generated advisory envelope;
- finding records;
- non-authority statement;
- replay reference for the advisory output.

Replay remains the evidence and reconstruction authority.

Architectural Health must not:

- reconstruct Replay independently;
- synthesize missing Replay evidence;
- mutate Replay history;
- claim completion when Replay evidence is missing;
- convert documentation-only evidence into runtime execution evidence.

## 11. Governance Relationship

Governance remains the authority for certification, authorization, admissibility, and final verdicts.

Architectural Health may expose:

- missing Governance evidence;
- conflicting final verdicts;
- unresolved responsibility leakage;
- realignment not yet certified;
- certification chain discontinuity;
- recommended Governance review routes.

Architectural Health must not:

- issue final verdicts;
- certify implementation;
- authorize mutation;
- authorize validation;
- authorize Git;
- authorize rollback;
- override a Governance finding;
- mark a milestone certified.

If the advisory projection detects a high or critical finding, the recommended output is:

```text
GOVERNANCE_REVIEW_RECOMMENDED
```

not an automatic block or automatic correction.

## 12. Architecture Review Relationship

Architectural Health supports architecture review but does not replace it.

Architecture reviews should consume the advisory projection by:

- listing whether Architectural Health findings were available;
- summarizing unresolved medium, high, or critical findings;
- deciding whether each finding represents actual responsibility leakage;
- recording any required realignment;
- confirming or rejecting boundary preservation;
- preserving all findings in the certification chain.

Architecture review remains the human-readable evaluative process. Governance remains the certification authority.

## 13. Canonical Workflow Recommendation

The canonical governed development workflow should become:

```text
Human Intent
-> Implementation
-> Platform Digital Twin
-> Architectural Health Projection
-> Advisory Findings
-> Human Review
-> Architecture Review
-> Certification
```

Justification:

- Architectural Health requires implementation and evidence to produce useful findings.
- Platform Digital Twin is the certified aggregate projection source.
- Advisory findings should be visible to the Human before architecture review.
- Architecture review can evaluate findings without giving the projection authority.
- Governance can certify only after evidence and review are complete.

Alternative placement before implementation may be useful for specifications, but it should remain optional because many findings require implementation evidence.

## 14. Implementation Readiness Assessment

| Area | Readiness | Notes |
| --- | --- | --- |
| Projection concept | Ready | G8-17 certified Architectural Health as a Digital Twin projection. |
| Advisory integration | Ready | G9-05 certified advisory participation. |
| Input evidence families | Ready enough | Governance docs, Replay references, ownership records, implementation docs, and validation evidence already exist. |
| Output envelope | Specified | This document defines advisory projection and finding fields. |
| Severity model | Specified | Deterministic advisory severities are defined. |
| Human presentation | Specified | Findings must be explained with evidence and remain advisory. |
| Replay integration | Ready enough | Documentation-only visibility is available; runtime projection should be replay-bound later. |
| Governance relationship | Ready | Governance remains the only certification authority. |
| Runtime implementation | Not part of this task | Future implementation must reuse Platform Digital Twin and Replay patterns. |

Implementation readiness:

```text
ready for minimal implementation of advisory projection workflow
```

No new subsystem or authority layer is required.

## 15. Acceptance Criteria

Architectural Health advisory workflow is acceptable when:

1. Projection timing is deterministic.
2. Input evidence is derived from certified Platform Core assets and Platform Digital Twin projections.
3. Advisory outputs use a deterministic envelope.
4. Every finding includes evidence, affected owner, severity, replay references when available, and recommended human review.
5. Findings are presented to the Human before architecture review.
6. Replay visibility is preserved.
7. Governance evidence remains visible.
8. Architecture review consumes findings without being replaced by them.
9. Architectural Health does not approve, reject, authorize, execute, mutate, certify, or override decisions.
10. Human and Governance authority remain intact.

## 16. Validation Strategy

Documentation-only workflow specification validation:

```text
git diff --check
```

Future implementation validation:

- `git diff --check`;
- targeted projection envelope tests;
- deterministic source ordering tests;
- finding severity classification tests;
- Replay visibility tests;
- non-authority assertion tests;
- architecture review consumption tests.

## 17. Final Determination

The Architectural Health advisory workflow is specified.

Architectural Health should participate in governed development after implementation evidence is available and before architecture review. It should produce deterministic, replay-visible advisory findings derived from Platform Digital Twin evidence and presented to the Human for review.

Architectural Health remains advisory only and does not become a subsystem, authority layer, repair engine, or certification authority.

Final verdict: ARCHITECTURAL_HEALTH_ADVISORY_WORKFLOW_SPECIFIED

## 18. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: ARCHITECTURAL_HEALTH_ADVISORY_WORKFLOW_SPECIFIED
