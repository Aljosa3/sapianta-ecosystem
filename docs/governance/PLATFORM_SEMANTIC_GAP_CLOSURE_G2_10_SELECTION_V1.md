# Platform Semantic Gap Closure G2-10 Selection V1

Status: batch selection governance artifact.

Scope: next implementation batch selection after G2-09 OCS Semantic Lineage And PPP
Annotation.

This artifact does not implement runtime code, modify tests, change command behavior,
retire compatibility layers, alter governance authority, or change replay semantics.

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

Current validation baseline:

```text
5430 passed
4 skipped
0 failed
```

This artifact reviews the remaining Generation 2 roadmap and confirms the implementation
scope for Batch G2-10.

## 2. Post-G2-09 Architectural Review

G2-09 completed downstream CSA provenance propagation into OCS and PPP evidence without
transferring OCS cognition authority or PPP structured authority to UBTR.

The remaining roadmap is now primarily certification of permanent non-UBTR boundaries,
operator-facing semantic projection, replay/hardening classification migration,
provider-assisted closure, and final compatibility retirement.

The approved dependency graph remains optimal. Command boundary certification is the
correct next batch because it freezes exact command authority before later explanation and
replay migrations consume richer CSA lineage.

## 3. Updated Remaining Inventory

| Area | Dependency Readiness | Certification Impact | Replay Impact | Rollback Complexity | Contribution Toward Exclusive UBTR Semantic Authority |
| --- | --- | --- | --- | --- | --- |
| Command boundary and recommendation prose certification | Ready after G2-09; upstream CSA lineage and PPP/OCS provenance are available, and exact command parsers already exist | High; certifies that exact approval, reject, modify, resume, retry, cancel, lifecycle, and recommendation commands remain structured authority outside UBTR | Medium-high; should record command-vs-prose source and parser non-match evidence where ambiguous prose is evaluated | Low; command parsers remain unchanged and compatibility prose fallback remains available | High boundary value; proves exact commands are permanent structured authority while ambiguous prose can be CSA-observed after parser non-match |
| Explanation rendering migration | Ready only after command boundary certification; explanations must not blur commands with recommendations or prose | Medium-high; operator-facing but non-authoritative renderers need section parity and source transparency | Medium-high; should record renderer source, CSA section parity, and compatibility fallback | Low; compatibility renderer can remain fallback | Medium; migrates human-facing semantic projection after command boundaries are frozen |
| Replay, hardening, and replay-derived classifiers | Partially ready; should follow command and explanation source fields so replay classifiers can consume structured evidence | Medium-high; must avoid reinterpretation of historical replay while improving new-session classification | High; changes new classification source from token scans toward structured CSA/replay evidence | Medium; legacy scan fallback must remain for old artifacts | High; removes duplicate semantic scans from new replay/hardening paths |
| Provider-assisted and legacy classifier closure | Not ready until command, explanation, and replay classifier sources are certified | High; closes provider-assisted semantic authority risk and inventories legacy entrypoints | Medium-high; must record deterministic CSA failure before advisory provider assistance | Medium; provider-assisted fallback remains only after certified CSA failure | High; closes remaining non-UBTR semantic authority paths |
| Compatibility retirement certification | Final step only after G2-10 through G2-13 complete | Very high; retirement cannot weaken rollback, replay, governance, or known limitation visibility | Very high; must prove all compatibility paths are retired, diagnostic fallback, or permanent structured authority | High; final retirement is irreversible except through compatibility restoration | Final; completes Generation 2 semantic authority only after every compatibility path is classified |

## 4. Confirmed Dependency Graph

The current dependency graph remains optimal.

```text
G2-09 OCS Semantic Lineage And PPP Annotation
  -> G2-10 Command Boundary And Recommendation Prose Certification
  -> G2-11 Explanation Rendering Migration
  -> G2-12 Replay, Hardening, And Replay-Derived Classifiers
  -> G2-13 Provider-Assisted And Legacy Classifier Closure
  -> G2-14 Compatibility Retirement Certification
```

G2-10 should proceed before explanation rendering because command text, recommendation
prose, and operator guidance must have frozen source boundaries before renderer migration.

G2-10 should proceed before replay/hardening classifier migration because replay
classifiers need deterministic command-vs-prose evidence rather than token-derived
inference.

## 5. Selected Batch

Selected next implementation batch:

```text
Batch G2-10: Command Boundary And Recommendation Prose Certification
```

## 6. Confirmed G2-10 Scope

G2-10 should certify command boundaries rather than migrate exact commands into UBTR.

Expected implementation scope:

- preserve exact approval command parsing;
- preserve exact rejection and modification command parsing;
- preserve exact resume, retry, cancel, and lifecycle command parsing;
- preserve exact recommendation approval and follow-up command parsing;
- record command parser match, parser non-match, and command-vs-prose source where
  replay evidence needs that distinction;
- permit CSA consumption only for ambiguous prose after deterministic command parser
  non-match;
- keep compatibility prose fallback available where CSA parity is not certified;
- prove no command parser behavior changes.

Out of scope for G2-10:

- replacing exact command parsers with UBTR;
- changing approval, resume, lifecycle, or recommendation state machines;
- changing execution authorization;
- changing worker/provider ownership;
- changing replay ownership;
- retiring compatibility layers.

## 7. Selection Rationale

G2-10 is selected because it provides the highest architectural boundary value among the
remaining ready batches.

Selection rationale:

- It is the next batch in the approved Platform Semantic Gap Closure Program.
- All dependencies are satisfied by G2-09 lineage and annotation evidence.
- It has low rollback complexity because exact command parsers remain unchanged.
- It reduces semantic ambiguity by separating structured commands from ambiguous prose.
- It prepares explanation rendering to cite stable command/prose source boundaries.
- It prepares replay and hardening classifiers to consume structured source evidence.
- It prevents later UBTR migration work from accidentally absorbing permanent structured
  command authority.

## 8. Expected Regression Requirements

Expected G2-10 regression coverage:

- same-session approval command tests;
- restart approval restoration tests;
- reject and modification command tests;
- resume, retry, cancel, and lifecycle command tests;
- recommendation approval and follow-up tests;
- command parser non-match and ambiguous prose tests;
- replay restoration tests;
- provider, worker, execution, governance, and replay non-authority negatives;
- full pytest suite.

## 9. Certification Impact

G2-10 certification should prove:

- exact commands are permanent structured authority outside UBTR;
- CSA is not used before deterministic command parser non-match;
- ambiguous prose can be CSA-observed only where parity is proven;
- compatibility fallback remains available for non-parity prose;
- approval, resume, lifecycle, and recommendation state remain replay-restored and
  structured;
- no governance, approval, execution, provider, worker, or replay authority is transferred
  to UBTR.

This certification is required before explanation rendering, replay/hardening
classifiers, provider-assisted closure, and compatibility retirement.

## 10. Estimated Remaining Effort To Generation 2 Completion

Remaining implementation batches after G2-10 selection:

```text
G2-10 Command Boundary And Recommendation Prose Certification
G2-11 Explanation Rendering Migration
G2-12 Replay, Hardening, And Replay-Derived Classifiers
G2-13 Provider-Assisted And Legacy Classifier Closure
G2-14 Compatibility Retirement Certification
```

Estimated completion shape:

- One command-boundary certification batch.
- One human-facing explanation migration batch.
- One replay/hardening structured classification batch.
- One provider-assisted and legacy closure batch.
- One final compatibility retirement certification batch.

Generation 2 should be considered complete only after G2-14 classifies every remaining
compatibility path as retired, diagnostic fallback, or permanent structured authority.

## 11. Final Selection

Selected next batch:

```text
Batch G2-10: Command Boundary And Recommendation Prose Certification
```

Selection verdict:

```text
PLATFORM_SEMANTIC_GAP_CLOSURE_G2_10_SELECTED
```
