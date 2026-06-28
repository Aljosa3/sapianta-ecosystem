# Platform Semantic Gap Closure G2-11 Selection V1

Status: batch selection governance artifact.

Scope: next implementation batch selection after G2-10 Command Boundary And
Recommendation Prose Certification.

This artifact does not implement runtime code, modify tests, change explanation
behavior, retire compatibility layers, alter governance authority, or change replay
semantics.

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
- G2-09: OCS Semantic Lineage And PPP Annotation.
- G2-10: Command Boundary And Recommendation Prose Certification.

Current validation baseline:

```text
5432 passed
4 skipped
0 failed
```

This artifact reviews the remaining Generation 2 roadmap and confirms the next
implementation batch.

## 2. Post-G2-10 Architectural Review

G2-10 froze the boundary between deterministic command authority and natural-language
recommendation prose. Exact commands remain structured authority outside UBTR, while CSA
evidence can be observed only after deterministic parser non-match.

The remaining roadmap is now:

- explanation rendering migration;
- replay, hardening, and replay-derived classifiers;
- provider-assisted and legacy classifier closure;
- compatibility retirement certification.

The approved dependency graph remains optimal. Explanation rendering should proceed next
because renderers consume OCS/PPP semantic lineage from G2-09 and command-vs-prose
boundary evidence from G2-10.

## 3. Updated Remaining Inventory

| Area | Dependency Readiness | Certification Impact | Replay Impact | Rollback Complexity | Contribution Toward Exclusive UBTR Semantic Authority |
| --- | --- | --- | --- | --- | --- |
| Explanation rendering migration | Ready after G2-09 provenance and G2-10 command-boundary certification | Medium-high; operator-facing semantic projection must preserve section requirements and non-authority | High; renderer source, CSA section parity, compatibility fallback, and advisory-only wording should be replay-visible | Low; compatibility renderer can remain fallback | Medium-high; moves human-facing semantic projection toward UBTR where section parity is proven |
| Replay, hardening, and replay-derived classifiers | Partially ready; should follow G2-11 renderer source fields so classifiers consume structured replay evidence | Medium-high; must avoid historical replay reinterpretation while improving new-session classification | High; changes new-session classification source from token scans toward structured CSA/replay provenance | Medium; legacy scan fallback remains required | High; removes duplicate semantic scans from new replay/hardening paths |
| Provider-assisted and legacy classifier closure | Not ready until explanation and replay classifier sources are certified | High; closes provider-assisted semantic authority risk and inventories legacy entrypoints | Medium-high; must record deterministic CSA failure before advisory provider assistance | Medium; provider-assisted fallback remains only after certified CSA failure | High; closes remaining non-UBTR semantic authority paths |
| Compatibility retirement certification | Final step only after G2-11 through G2-13 complete | Very high; retirement cannot weaken rollback, replay, governance, or known limitation visibility | Very high; must prove every compatibility path is retired, diagnostic fallback, or permanent structured authority | High; final retirement is the most constrained rollback surface | Final; completes Generation 2 semantic authority only after every compatibility path is classified |

## 4. Confirmed Dependency Graph

The current dependency graph remains optimal.

```text
G2-10 Command Boundary And Recommendation Prose Certification
  -> G2-11 Explanation Rendering Migration
  -> G2-12 Replay, Hardening, And Replay-Derived Classifiers
  -> G2-13 Provider-Assisted And Legacy Classifier Closure
  -> G2-14 Compatibility Retirement Certification
```

G2-11 should precede replay/hardening classifier migration because classifiers need stable
renderer source fields and explanation parity evidence rather than deriving semantic
meaning from rendered text.

G2-11 should precede provider-assisted and legacy closure because operator-facing
explanations must already distinguish CSA-primary projection, compatibility fallback, and
advisory provider wording.

## 5. Selected Batch

Selected next implementation batch:

```text
Batch G2-11: Explanation Rendering Migration
```

## 6. Confirmed G2-11 Scope

G2-11 should migrate explanation rendering only where Governance -> Human UBTR output has
deterministic section parity with compatibility rendering.

Expected implementation scope:

- capture section-level parity evidence;
- make UBTR output primary for parity-proven explanation sections;
- keep compatibility explanation sections fallback-visible;
- preserve required operator guidance sections;
- preserve provider wording as advisory-only;
- expose renderer source and fallback status in replay;
- preserve non-authority flags for all renderers.

Out of scope for G2-11:

- changing OCS cognition authority;
- changing PPP structured authority;
- changing approval, provider, worker, replay, or execution authority;
- allowing explanation text to become command authority;
- retiring compatibility renderers;
- changing Product 1 framing as AI Decision Validator.

## 7. Selection Rationale

G2-11 is selected because it is the next batch in the approved Platform Semantic Gap
Closure Program and all direct prerequisites are complete.

Selection rationale:

- G2-09 provides OCS/PPP semantic lineage for explanation source attribution.
- G2-10 provides command-vs-prose boundary evidence so explanation text cannot blur into
  command authority.
- Explanation rendering is operator-facing and should be migrated before replay/hardening
  classifiers consume rendered or summarized evidence.
- Compatibility fallback can remain available, keeping rollback complexity low.
- Provider wording remains advisory-only, preserving provider ownership boundaries.

## 8. Expected Regression Requirements

Expected G2-11 regression coverage:

- explanation section parity tests;
- human-friendly explanation runtime tests;
- LLM-assisted explanation runtime tests;
- universal translation explanation integration tests;
- routing visibility tests;
- provider failure/advisory-only tests;
- command-boundary non-authority tests;
- replay reconstruction tests for renderer source and fallback;
- full pytest suite.

## 9. Certification Impact

G2-11 certification should prove:

- UBTR/Governance -> Human output can become primary only for parity-proven sections;
- compatibility rendering remains fallback-visible;
- required operator guidance sections remain present;
- renderers remain non-authoritative;
- provider wording remains advisory-only;
- explanation text does not become approval, command, execution, provider, worker,
  governance, or replay authority;
- Product 1 remains framed as AI Decision Validator.

This certification is required before replay/hardening classifier migration,
provider-assisted and legacy closure, and compatibility retirement.

## 10. Estimated Remaining Effort To Generation 2 Completion

Remaining implementation batches after G2-11 selection:

```text
G2-11 Explanation Rendering Migration
G2-12 Replay, Hardening, And Replay-Derived Classifiers
G2-13 Provider-Assisted And Legacy Classifier Closure
G2-14 Compatibility Retirement Certification
```

Estimated completion shape:

- One explanation rendering migration batch.
- One replay/hardening structured classification batch.
- One provider-assisted and legacy closure batch.
- One final compatibility retirement certification batch.

Generation 2 should be considered complete only after G2-14 classifies every remaining
compatibility path as retired, diagnostic fallback, or permanent structured authority.

## 11. Final Selection

Selected next batch:

```text
Batch G2-11: Explanation Rendering Migration
```

Selection verdict:

```text
PLATFORM_SEMANTIC_GAP_CLOSURE_G2_11_SELECTED
```
