# Platform Semantic Gap Closure G2-12 Selection V1

Status: batch selection governance artifact.

Scope: next implementation batch selection after G2-11 Explanation Rendering Migration.

This artifact does not implement runtime code, modify tests, change replay classification,
retire compatibility layers, alter governance authority, or reinterpret historical replay.

## 1. Purpose

Platform Core Generation 1 is certified.

Completed Generation 2 semantic migration work:

- UBTR Phase 1 through Phase 5.
- Consumer Migration Batch 01 through Batch 02.
- G2-01: Replay Comparison Substrate.
- G2-02: Proposal-Only OCS Routing.
- G2-03: Remaining HIRR Intake Families.
- G2-04: HIRR Clarification Continuity.
- G2-05: Execution Intent And Authorization Entry Semantics.
- G2-06: Worker And Domain Lifecycle Entry Semantics.
- G2-07: Native Development Semantics.
- G2-08: Specialized Product, Domain, Provider, And Similarity Routes.
- G2-09: OCS Semantic Lineage And PPP Annotation.
- G2-10: Command Boundary And Recommendation Prose Certification.
- G2-11: Explanation Rendering Migration.

Current validation baseline:

```text
5433 passed
4 skipped
0 failed
```

This artifact reviews the remaining Generation 2 roadmap and selects the next
implementation batch.

## 2. Post-G2-11 Architectural Review

G2-11 made explanation rendering source provenance replay-visible and established
CSA-primary rendering only for parity-proven sections while preserving compatibility
fallback.

The remaining roadmap is now:

- replay, hardening, and replay-derived classifiers;
- provider-assisted and legacy classifier closure;
- compatibility retirement certification.

The approved dependency graph remains optimal. Replay and hardening classifiers should
proceed next because they can now consume structured G2-09 lineage, G2-10 command
boundary evidence, and G2-11 explanation rendering provenance instead of deriving
semantic meaning from token scans.

## 3. Updated Remaining Inventory

| Area | Dependency Readiness | Certification Impact | Replay Impact | Rollback Complexity | Architectural Necessity | Remaining Semantic Duplication |
| --- | --- | --- | --- | --- | --- | --- |
| Replay, hardening, and replay-derived classifiers | Ready after G2-09 lineage, G2-10 command boundary evidence, and G2-11 renderer source fields | High; must prove new-session classifiers consume structured CSA/replay provenance while preserving legacy replay compatibility | Very high; classification source becomes explicit and replay-visible for new evidence | Medium; legacy token-scan fallback remains required for historical artifacts | High; replay/hardening is the audit substrate for final compatibility closure | Medium-high; token scans still duplicate semantic classification for new sessions |
| Provider-assisted and legacy classifier closure | Not ready until replay/hardening classifiers expose structured source provenance | High; closes hidden semantic authority risk in provider-assisted and older classifier paths | Medium-high; must record deterministic CSA failure before advisory provider assistance and legacy fallback | Medium; legacy entrypoints need inventory and compatibility-only markings before retirement | High; provider-assisted and legacy entrypoints are the last semantic authority risk cluster | High; legacy/provider-assisted classifiers can still duplicate UBTR semantics |
| Compatibility retirement certification | Not ready until G2-12 and G2-13 complete | Very high; final retirement must not weaken rollback, replay, governance, or known limitation visibility | Very high; must prove every compatibility path is retired, diagnostic fallback, or permanent structured authority | High; final retirement has the narrowest rollback surface | Final architectural closure requirement | High until every compatibility path is classified and certified |

## 4. Confirmed Dependency Graph

The current dependency graph remains optimal.

```text
G2-12 Replay, Hardening, And Replay-Derived Classifiers
  -> G2-13 Provider-Assisted And Legacy Classifier Closure
  -> G2-14 Compatibility Retirement Certification
```

G2-12 must precede G2-13 because provider-assisted and legacy closure needs structured
classification source evidence before those paths can be marked CSA-parity migrated,
compatibility-only, advisory-only, or unsupported.

G2-12 must precede G2-14 because compatibility retirement depends on replay evidence that
distinguishes new structured classification from historical compatibility scans without
reinterpreting old replay.

## 5. Selected Batch

Selected next implementation batch:

```text
Batch G2-12: Replay, Hardening, And Replay-Derived Classifiers
```

## 6. Confirmed G2-12 Scope

G2-12 should migrate new-session replay and hardening classification to structured
CSA/replay provenance where parity is proven.

Expected implementation scope:

- define structured classification input fields for new sessions;
- consume CSA lineage, command-boundary source, explanation rendering source, and replay
  comparison evidence where available;
- emit classification source provenance for new replay evidence;
- preserve legacy token-scan compatibility fallback for historical replay artifacts;
- certify that historical replay is not reinterpreted;
- keep hardening and replay-derived improvement outputs non-authoritative until governed
  approval.

Out of scope for G2-12:

- provider-assisted classifier closure;
- legacy entrypoint retirement;
- compatibility layer retirement;
- changing governance, approval, provider, worker, execution, or replay authority.

## 7. Selection Rationale

G2-12 is selected because it is the next batch in the approved Platform Semantic Gap
Closure Program and all direct prerequisites are complete.

Selection rationale:

- G2-09 supplies OCS/PPP semantic lineage.
- G2-10 supplies command-vs-prose boundary evidence.
- G2-11 supplies explanation rendering source and section-parity evidence.
- Replay and hardening classifiers are now able to consume structured provenance instead
  of token-derived semantic scans for new sessions.
- G2-12 directly reduces duplicate semantic responsibility while preserving legacy replay
  compatibility.
- G2-13 and G2-14 depend on G2-12 classification source provenance.

## 8. Expected Regression Requirements

Expected G2-12 regression coverage:

- hardening classifier tests;
- replay gap detection tests;
- replay-derived improvement tests;
- replay summary tests;
- legacy replay compatibility tests;
- new-session structured source provenance tests;
- historical replay non-reinterpretation tests;
- provider, worker, approval, execution, governance, and replay non-authority negatives;
- full pytest suite.

## 9. Certification Impact

G2-12 certification should prove:

- new-session replay and hardening classifiers classify from structured CSA/replay
  provenance where available;
- compatibility token scans remain available only for legacy replay and non-parity inputs;
- historical replay is not reinterpreted;
- semantic-source provenance is replay-visible;
- replay-derived improvement remains proposal-only and governed;
- no governance, approval, provider, worker, execution, or replay authority is transferred
  to classifiers.

This certification is required before provider-assisted and legacy classifier closure and
compatibility retirement certification.

## 10. Estimated Remaining Effort To Generation 2 Completion

Remaining implementation batches after G2-12 selection:

```text
G2-12 Replay, Hardening, And Replay-Derived Classifiers
G2-13 Provider-Assisted And Legacy Classifier Closure
G2-14 Compatibility Retirement Certification
```

Estimated completion shape:

- One replay/hardening structured classification batch.
- One provider-assisted and legacy closure batch.
- One final compatibility retirement certification batch.

Generation 2 should be considered complete only after G2-14 classifies every remaining
compatibility path as retired, diagnostic fallback, or permanent structured authority.

## 11. Final Selection

Selected next batch:

```text
Batch G2-12: Replay, Hardening, And Replay-Derived Classifiers
```

Selection verdict:

```text
PLATFORM_SEMANTIC_GAP_CLOSURE_G2_12_SELECTED
```
