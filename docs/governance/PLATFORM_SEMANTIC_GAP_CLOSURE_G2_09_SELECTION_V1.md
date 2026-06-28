# Platform Semantic Gap Closure G2-09 Selection V1

Status: batch selection governance artifact.

Scope: next implementation batch selection after G2-08 Specialized Product, Domain,
Provider, And Similarity Routes.

This artifact does not implement runtime code, modify tests, change routing behavior,
retire compatibility layers, or alter governance authority.

## 1. Purpose

Platform Core Generation 1 is certified.

Completed Generation 2 semantic migration work:

- UBTR Phase 1 through Phase 5.
- Consumer Migration Batch 01: ACLI CSA-primary routing subset.
- Consumer Migration Batch 02: HIRR clarification intake.
- G2-01: Replay Comparison Substrate.
- G2-02: Proposal-Only OCS Routing.
- G2-03: Remaining HIRR Intake Families.
- G2-04: HIRR Clarification Continuity.
- G2-05: Execution Intent And Authorization Entry Semantics.
- G2-06: Worker And Domain Lifecycle Entry Semantics.
- G2-07: Native Development Semantics.
- G2-08: Specialized Product, Domain, Provider, And Similarity Routes.

Current validation baseline:

```text
5427 passed
4 skipped
0 failed
```

This artifact performs the post-G2-08 architectural review and selects the next
Generation 2 implementation batch.

## 2. Post-G2-08 Architectural Review

G2-08 completed the major remaining ACLI route-level semantic migration cluster. The
remaining semantic responsibilities are no longer primarily broad route selection. They
are source-lineage propagation, command-boundary certification, human-facing projection,
structured replay classification, provider-assisted closure, and final retirement
certification.

The current dependency graph remains optimal. OCS semantic lineage and PPP annotation are
now the highest-priority next step because they consume the upstream route provenance
created by G2-01 through G2-08 without transferring authority away from OCS or PPP.

## 3. Updated Remaining Inventory

| Area | Architectural Necessity | Semantic Duplication | Dependency Readiness | Certification Impact | Replay Impact | Rollback Complexity | Contribution Toward UBTR Semantic Authority |
| --- | --- | --- | --- | --- | --- | --- | --- |
| OCS semantic lineage and PPP annotation | High; downstream OCS and PPP flows need upstream CSA provenance to avoid semantic source gaps | Medium; OCS/PPP should not reinterpret upstream semantics but should expose their source lineage | Ready after G2-08 stabilized ACLI specialized route source fields | Medium-high; must prove OCS cognition and PPP structured authority remain owned by their runtimes | High positive impact; links CSA hashes to OCS result and PPP/resource-selection evidence | Low; annotation can be disabled while structured OCS/PPP artifacts remain authoritative | High; extends UBTR source visibility beyond routing into downstream orchestration without authority transfer |
| Command boundary certification | High for constitutional safety; exact commands must remain structured authority | Low; exact commands are intentionally not UBTR semantic interpretation | Ready in parallel, but lower semantic-closure value than OCS/PPP lineage | High; certifies approval/resume/recommendation command invariants | Medium; records command-vs-prose source evidence | Low; command parsers remain unchanged | Medium; proves permanent non-UBTR structured authority boundary |
| Explanation rendering | Medium-high for operator clarity and Governance -> Human projection | Medium; compatibility renderers still duplicate human-facing semantic projection | Partially ready, but should follow OCS/PPP provenance so explanations can cite stable source lineage | Medium; renderers are non-authoritative but operator-visible | Medium-high; records renderer source and fallback | Low; compatibility renderer remains fallback | Medium; migrates human-facing projection after source lineage stabilizes |
| Replay/hardening classifiers | High for retirement readiness and audit continuity | Medium; token scans duplicate semantic classification for new sessions | Depends on more structured provenance from G2-09 through G2-11 | Medium; must preserve legacy replay scans and avoid reinterpretation | High; changes classification source for new replay evidence | Medium; legacy scan fallback remains required | Medium-high; moves new-session replay classification toward structured CSA/replay evidence |
| Provider-assisted and legacy classifier closure | High; prevents hidden semantic authority after primary migrations | High in legacy/provider-assisted paths | Not ready until deterministic CSA failure and structured provenance cover downstream paths | High; must prove providers remain advisory and legacy entrypoints are inventoried | Medium; must mark source and deterministic failure before provider assistance | Medium; legacy fallbacks remain until retirement audit | High; closes remaining non-UBTR semantic authority risks |
| Compatibility retirement certification | Final architectural closure requirement | High until all retirement candidates are certified | Not ready until G2-09 through G2-13 complete | Very high; retirement must not weaken rollback, replay, or governance evidence | Very high; must cover migrated and legacy replay reconstruction | High; removal is only allowed after exercised rollback and parity evidence | Final completion step for Generation 2 semantic authority |

## 4. Updated Dependency Graph

The existing dependency graph remains optimal.

```text
G2-08 Specialized Product, Domain, Provider, And Similarity Routes
  -> G2-09 OCS Semantic Lineage And PPP Annotation
  -> G2-10 Command Boundary And Recommendation Prose Certification
  -> G2-11 Explanation Rendering Migration
  -> G2-12 Replay, Hardening, And Replay-Derived Classifiers
  -> G2-13 Provider-Assisted And Legacy Classifier Closure
  -> G2-14 Compatibility Retirement Certification
```

Parallel measurement remains permissible for command boundary and explanation section
parity. Primary implementation should still proceed through G2-09 first because OCS/PPP
lineage supplies source context required by later explanation, replay, and retirement
certification.

## 5. Selected Batch

Recommended next implementation batch:

```text
Batch G2-09: OCS Semantic Lineage And PPP Annotation
```

## 6. Selection Rationale

G2-09 is selected because G2-08 completed the upstream specialized route source fields
needed for downstream lineage annotation.

G2-09 has the best combined score across the selection criteria:

- It is the next batch in the approved Platform Semantic Gap Closure Program.
- It has all dependencies satisfied by G2-01 through G2-08.
- It does not require authority transfer from OCS or PPP to UBTR.
- It improves replay continuity by linking CSA source hashes to OCS semantic result and
  PPP/resource-selection artifacts.
- It prepares the evidence substrate for explanation rendering, replay/hardening
  classifiers, provider-assisted closure, and compatibility retirement.
- It has lower rollback complexity than command, explanation, replay, or provider-assisted
  closure because annotation can remain non-authoritative.

Command boundary certification is important but lower in semantic duplication reduction.
Explanation rendering should follow OCS/PPP lineage so operator-facing text can identify
stable semantic sources. Replay/hardening, provider-assisted closure, and compatibility
retirement remain dependent on more complete structured provenance.

## 7. Expected G2-09 Runtime Scope

Expected future implementation scope:

- attach CSA lineage references to OCS semantic resolution and cognition result flows;
- annotate PPP and resource-selection captures with upstream CSA references where present;
- preserve OCS ownership of cognition/result semantics;
- preserve PPP ownership of structured resource-selection authority;
- keep CSA annotation non-authoritative unless a later batch separately certifies primary
  semantic consumption;
- record rollback-visible absence or divergence when upstream CSA lineage is unavailable.

No runtime changes are made by this selection artifact.

## 8. Expected Regression Requirements

Expected G2-09 regression coverage:

- OCS semantic resolution tests;
- OCS end-to-end cognition tests;
- OCS-to-PPP binding and continuation tests;
- PPP routing tests;
- resource-selection tests;
- replay lineage reconstruction tests;
- provider, worker, approval, execution, and governance non-authority negatives;
- full pytest suite.

## 9. Certification Impact

G2-09 certification should prove:

- CSA lineage can propagate into OCS and PPP evidence without changing selected behavior;
- OCS cognition result semantics remain OCS-owned;
- PPP structured authority remains PPP-owned;
- provider selection, worker invocation, approval, execution authorization, governance, and
  replay ownership are unchanged;
- downstream replay can identify the upstream semantic source for migrated and fallback
  routes;
- annotation rollback is available because structured OCS/PPP artifacts remain sufficient.

This certification is architecturally necessary before explanation rendering, replay
classifier migration, provider-assisted closure, and compatibility retirement.

## 10. Remaining Work Estimate To Generation 2 Completion

Remaining implementation batches after G2-09 selection:

```text
G2-09 OCS Semantic Lineage And PPP Annotation
G2-10 Command Boundary And Recommendation Prose Certification
G2-11 Explanation Rendering Migration
G2-12 Replay, Hardening, And Replay-Derived Classifiers
G2-13 Provider-Assisted And Legacy Classifier Closure
G2-14 Compatibility Retirement Certification
```

Estimated completion shape:

- One downstream lineage/annotation batch.
- One command-boundary certification batch.
- One human-facing projection migration batch.
- One replay/hardening structured classification batch.
- One provider-assisted and legacy closure batch.
- One final retirement certification batch.

Generation 2 should be considered complete only after G2-14 classifies every remaining
compatibility path as retired, diagnostic fallback, or permanent structured authority.

## 11. Final Selection

Selected next batch:

```text
Batch G2-09: OCS Semantic Lineage And PPP Annotation
```

Selection verdict:

```text
PLATFORM_SEMANTIC_GAP_CLOSURE_G2_09_SELECTED
```
