# UBTR Generation 2 Vision Audit V1

Status: architecture vision audit.

Scope: Platform evolution after Platform Core Generation 1 formal certification.

This artifact does not implement code, modify tests, change Platform Core Generation 1, alter governance, alter replay, change routing, change HIRR, change PPP, change approval, change providers, or remove compatibility layers.

## 1. Executive Summary

Platform Core Generation 1 is formally certified with limitations:

```text
PLATFORM_CORE_GENERATION1_CERTIFIED_WITH_LIMITATIONS
```

The most important remaining architectural limitation is:

```text
UBTR is canonical semantic authority, but not yet exclusive semantic authority.
```

This audit determines whether completing exclusive UBTR semantic authority should become a primary architectural objective of the next platform generation.

Conclusion:

```text
Yes.
```

Generation 2 should establish the intended semantic architecture:

```text
Human
-> Universal Bidirectional Translation Runtime
-> Canonical Semantic Artifact
-> Entire Platform
-> Replay
-> Human-friendly explanation
```

The migration should be treated as a primary Generation 2 objective because it reduces duplicated semantic interpretation, improves replay clarity, strengthens governance explainability, and creates a single platform-wide semantic contract for future domains and products.

## 2. Review Inputs

Primary input artifacts:

- `PLATFORM_CORE_GENERATION1_FORMAL_CERTIFICATION_V1`
- `CANONICAL_SEMANTIC_AUTHORITY_ARCHITECTURE_AUDIT_V1`
- `UBTR_CONSUMER_MIGRATION_AUDIT_V1`
- `UBTR_CONSUMER_MIGRATION_PLAN_V1`
- `UBTR_EXCLUSIVE_SEMANTIC_AUTHORITY_MIGRATION_PROGRAM_V1`
- `UNIVERSAL_BIDIRECTIONAL_TRANSLATION_RUNTIME_V1`
- `UNIVERSAL_TRANSLATION_ARTIFACT_SCHEMA_V1`
- `HUMAN_TO_GOVERNANCE_TRANSLATION_RUNTIME_V1`
- `GOVERNANCE_TO_HUMAN_TRANSLATION_RUNTIME_V1`

Current certification evidence:

```text
5388 passed
4 skipped
0 failed
```

## 3. Current UBTR Architecture

Current UBTR capabilities:

- Human -> Governance translation exists.
- Governance -> Human translation exists.
- Universal Translation Artifact Schema exists.
- Adaptive Translation Escalation Runtime exists.
- Replay-Derived Translation Learning Runtime exists.
- deterministic explanations exist.
- optional LLM-assisted explanation exists.
- translation artifacts are replay-visible.
- translation artifacts explicitly deny authority.

Current architecture is certification-safe because UBTR is canonical and non-authoritative.

Current limitation:

```text
Several Platform Core consumers still derive semantic meaning locally.
```

Examples include:

- ACLI conversational routing;
- HIRR intake;
- HIRR continuity;
- proposal-only OCS escalation;
- human execution intent detection;
- native development intent routing;
- hardening scenario classification;
- some OCS/provider-assisted semantic paths.

## 4. Compatibility Layers

Generation 1 intentionally preserves compatibility layers.

Current compatibility layers include:

| Compatibility Layer | Current Role | Gen2 Treatment |
| --- | --- | --- |
| ACLI `_classify_workflow()` prompt markers | certified routing compatibility | migrate to UBTR semantic artifact consumption |
| proposal-only OCS markers | proposal-only cognition routing | replace with UBTR provider relevance and execution flags |
| HIRR intake markers | intent-family classification | generate HIRR-compatible artifacts from UBTR |
| HIRR continuity markers | clarification refinement | use linked UBTR artifacts for original and clarification turns |
| execution-intent markers | create/execute/governed artifact detection | consume UBTR action, approval, worker, and entity fields |
| native-development markers | development workflow routing | consume UBTR semantic annotation plus structured context |
| hardening token scans | scenario classification | consume structured replay and UBTR semantic identity |
| approval/lifecycle command grammar | deterministic workflow commands | retain as command grammar, not semantic translation |

The last row is intentionally not a migration target for semantic ownership. Exact commands such as `APPROVE`, `REJECT`, `REQUEST_MODIFICATION`, `continue`, and `resume` are workflow-control grammar, not human-language semantic interpretation.

## 5. Remaining Semantic Duplication

Current semantic duplication exists when more than one component can interpret the same human prompt.

Duplicated interpretation points:

- UBTR Human -> Governance translation.
- ACLI workflow selection.
- HIRR clarification intake.
- HIRR clarification continuity.
- governed development detection.
- proposal-only OCS escalation.
- native development classification.
- generic execution intent detection.
- hardening scenario detection.

Long-term risks of duplication:

- route drift;
- vocabulary inconsistency;
- multilingual gaps;
- harder regression coverage;
- harder replay reconstruction;
- inconsistent operator explanations;
- duplicated marker maintenance;
- unclear semantic provenance;
- divergent behavior across future domains.

Generation 2 should remove these risks by making UBTR the exclusive semantic translation source.

## 6. Consumer Migration Status

| Consumer | Current Status | Gen2 Goal |
| --- | --- | --- |
| UBTR schema | migrated | remain canonical |
| Human -> Governance Translation | migrated | remain canonical producer |
| Governance -> Human Translation | migrated | remain canonical producer |
| Adaptive Translation Escalation | migrated | remain optional non-authoritative escalation |
| Replay-Derived Translation Learning | migrated | remain proposal-only improvement source |
| ACLI | partially migrated | consume Canonical Semantic Artifact before any semantic consumer |
| Conversational Routing | partially migrated | route from UBTR fields with governance validation |
| HIRR Intake | not migrated | produce HIRR artifacts from UBTR ambiguity and intent fields |
| HIRR Continuity | not migrated | consume linked turn translations |
| Proposal-Only OCS Escalation | partially migrated | consume UBTR provider relevance and no-execution semantics |
| Human Execution Intent Detection | not migrated | consume UBTR action/execution/approval fields |
| Native Development Routing | not migrated | consume UBTR action/domain/entity annotation |
| PPP | partially migrated | consume structured context plus UBTR semantic references |
| Approval Runtime | compatibility grammar | keep deterministic command grammar; use UBTR for ambiguous prose/explanation |
| Resume Runtime | compatibility grammar | keep deterministic command grammar; use Governance -> Human translation for summaries |
| Replay Runtime | migrated as store | reconstruct semantic source and decision source |
| Hardening Runtime | partially migrated | classify new sessions from UBTR and structured replay |
| Explanation Runtimes | downstream renderers | remain renderers only |

## 7. Long-Term Maintainability

Exclusive UBTR authority should improve maintainability by:

- centralizing vocabulary and multilingual normalization;
- reducing marker duplication;
- making new domain onboarding use one semantic contract;
- making regression suites smaller and more invariant-driven;
- allowing compatibility layers to retire in governed batches;
- making semantic behavior easier to audit;
- reducing route-specific phrase expansion churn.

Without exclusive UBTR authority, each new domain or workflow risks adding another local marker system. That would increase semantic drift and make future product expansion more expensive.

## 8. Replay Implications

Generation 2 should make replay answer a single semantic provenance question:

```text
Which UBTR artifact produced the semantic meaning consumed by this workflow?
```

Replay should preserve:

- original human prompt;
- Human -> Governance translation artifact;
- canonical semantic artifact hash;
- workflow candidate;
- governed workflow selection;
- local compatibility fallback, if any;
- approval state;
- execution state;
- Governance -> Human explanation artifact;
- hardening evidence;
- migration mode.

Replay should not reinterpret semantics. Replay should prove which semantic artifact was consumed.

Exclusive UBTR migration strengthens replay because semantic source and workflow source become separately visible:

```text
semantic source: UBTR
governance decision source: ACLI / workflow governance
execution source: worker after approval
evidence source: Replay
```

## 9. Governance Implications

Exclusive UBTR authority does not change governance authority.

Governance implications are positive if boundaries remain explicit:

- UBTR translates, but does not approve.
- UBTR proposes semantic candidates, but does not select authoritative workflow alone.
- ACLI/governance validates semantic artifacts before workflow action.
- approval remains explicit.
- workers remain gated.
- replay remains source of truth.

The primary governance benefit is clearer separation:

```text
UBTR owns meaning translation.
Governance owns admissibility.
Human owns authority.
Workers own bounded execution.
Replay owns evidence.
```

## 10. Explainability Implications

Exclusive UBTR authority should improve explainability because operator-facing explanations can reference one canonical semantic source.

Current explanation challenge:

- ACLI may record UBTR evidence but route using local markers.
- operator explanations must explain both technical routing and compatibility behavior.

Generation 2 target:

- "what I understood" comes from the UBTR semantic artifact;
- "why this workflow was selected" comes from governance consuming that artifact;
- "what happens next" comes from workflow state;
- "what requires approval" comes from approval runtime;
- "what was recorded" comes from replay.

This reduces operator confusion and makes both deterministic and optional LLM-assisted explanations safer.

## 11. Generation 2 Architectural Objective

Generation 2 should establish:

```text
Human
-> UBTR
-> Canonical Semantic Artifact
-> Entire Platform
```

as a primary architectural objective.

This objective should include:

1. Canonical semantic artifact completeness.

2. ACLI/HIRR consumer migration.

3. Routing from UBTR fields with governance validation.

4. Proposal-only OCS escalation from UBTR fields.

5. PPP handoff with UBTR semantic references.

6. Approval and resume command boundary preservation.

7. Replay semantic provenance.

8. Hardening metrics from UBTR and structured replay.

9. Compatibility-layer retirement certification.

## 12. Risks

Primary risks:

- migrating too quickly could change certified routing behavior;
- UBTR fields may not yet encode every compatibility marker;
- multilingual local markers may temporarily outperform UBTR;
- tests may need staged semantic equivalence coverage;
- exact lifecycle commands must not be accidentally treated as ambiguous natural language;
- replay readers must remain backward-compatible with Generation 1 evidence.

Risk mitigation:

- begin with replay-only comparison;
- retain compatibility fallback until parity is proven;
- migrate one consumer family at a time;
- preserve rollback mode;
- run certified prompt corpus after every phase;
- never allow translation artifacts to grant authority.

## 13. Recommended Generation 2 Migration Sequence

Recommended sequence:

1. Replay-only semantic comparison.

2. ACLI semantic ingress.

3. Conversational routing read-through.

4. Proposal-only OCS migration.

5. HIRR intake migration.

6. HIRR continuity migration.

7. execution-intent and governance-artifact detection migration.

8. native-development and PPP semantic reference migration.

9. approval/resume explanation boundary migration.

10. replay semantic-source canonicalization.

11. hardening semantic-source migration.

12. compatibility-layer retirement certification.

This follows `UBTR_EXCLUSIVE_SEMANTIC_AUTHORITY_MIGRATION_PROGRAM_V1`.

## 14. Certification Impact

Exclusive UBTR semantic authority was not required for Platform Core Generation 1 formal certification.

It should become a primary Generation 2 objective because:

- it removes the largest visible architectural limitation from Gen1;
- it improves long-term platform consistency;
- it supports universal domain expansion;
- it strengthens replay provenance;
- it simplifies future operator explanation;
- it reduces semantic drift.

Generation 2 certification should not claim completion until:

- all natural-language semantic consumers consume UBTR artifacts;
- local marker systems are fallback-only or retired;
- replay can prove semantic source for every workflow;
- regression suite validates semantic parity and rollback;
- approval/lifecycle command grammar remains protected.

## 15. Non-Goals

Generation 2 UBTR migration should not:

- redesign governance;
- redesign replay;
- redesign HIRR;
- redesign PPP;
- redesign approval;
- redesign workers;
- make UBTR execution authority;
- make providers authority;
- make explanation layers authority;
- remove compatibility layers before parity;
- reinterpret historical Generation 1 replay;
- hide Generation 1 limitations.

## 16. Recommendation

Exclusive UBTR semantic authority should be one of the primary architectural objectives of Platform Core Generation 2.

Recommended Generation 2 theme:

```text
Canonical Semantic Authority Consolidation
```

Recommended target architecture:

```text
Human
-> Universal Bidirectional Translation Runtime
-> Canonical Semantic Artifact
-> ACLI / HIRR / Routing / OCS / PPP / Approval / Resume / Replay / Hardening
-> Governance-controlled workflow outcomes
-> Replay
-> Human-friendly explanation
```

## Final Verdict

UBTR_GENERATION2_VISION_READY
