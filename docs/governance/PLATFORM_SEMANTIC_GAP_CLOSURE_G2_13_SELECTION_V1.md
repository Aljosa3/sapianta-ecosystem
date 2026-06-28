# Platform Semantic Gap Closure G2-13 Selection V1

Status: batch selection governance artifact.

Scope: next implementation batch selection after G2-12 Replay, Hardening, And
Replay-Derived Classifiers.

This artifact does not implement runtime code, modify tests, retire compatibility layers,
alter governance authority, alter replay authority, or reinterpret historical replay.

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
- G2-12: Replay, Hardening, And Replay-Derived Classifiers.

Current validation baseline:

```text
5436 passed
4 skipped
0 failed
```

This artifact reviews the remaining Generation 2 roadmap and confirms the implementation
scope for Batch G2-13.

## 2. Post-G2-12 Architectural Review

G2-12 established replay-visible classifier source provenance for replay-derived and
hardening classifiers. It also preserved compatibility interpretation, fallback status,
semantic comparison artifacts, parity evidence, and explicit non-reinterpretation of
historical replay.

The remaining roadmap is now:

- provider-assisted classifier closure;
- legacy classifier closure;
- compatibility retirement certification.

The approved dependency graph remains optimal. Provider-assisted and legacy closure should
proceed next because G2-12 now provides the structured classifier source provenance needed
to prove that provider-assisted and legacy paths are not hidden primary semantic authority.

## 3. Updated Remaining Inventory

| Area | Dependency Readiness | Certification Impact | Replay Impact | Rollback Complexity | Remaining Semantic Duplication | Readiness For Final Compatibility Retirement |
| --- | --- | --- | --- | --- | --- | --- |
| Provider-assisted classifier closure | Ready after G2-12 classifier provenance; CSA deterministic failure and advisory escalation can now be recorded before provider assistance | High; must prove providers remain advisory and cannot become primary semantic authority | High; replay must distinguish CSA failure, provider suggestion, advisory status, fallback status, and authority denial | Medium; provider-assisted fallback may remain after deterministic CSA failure | Medium-high until provider-assisted semantic suggestions are marked CSA-gated and advisory-only | Required before G2-14; provider-assisted paths must be classified as CSA-gated advisory fallback or unsupported |
| Legacy classifier closure | Ready after G2-12 provenance and prior CSA-primary routing migrations; legacy entrypoints can now be inventoried by semantic source | High; must prove older classifiers cannot silently override UBTR/CSA semantics | Medium-high; replay must mark legacy source, compatibility-only status, parity state, and retirement candidate status | Medium; legacy fallback remains only for certified historical or unsupported entrypoints | Medium-high until old deterministic classifiers and older conversation entrypoints are classified | Required before G2-14; every legacy classifier must be migrated, compatibility-only, diagnostic-only, or retired candidate |
| Compatibility retirement certification | Not ready until provider-assisted and legacy closure complete | Very high; final retirement must preserve replay, rollback evidence, governance boundaries, and known limitation visibility | Very high; final audit must prove every compatibility path has explicit disposition | High; retirement has the narrowest rollback surface and must be evidence-led | Medium until G2-13 classifies final provider-assisted and legacy paths | Final batch only; G2-14 begins after G2-13 closure evidence exists |

## 4. Confirmed Dependency Graph

The remaining dependency graph is confirmed:

```text
G2-13 Provider-Assisted And Legacy Classifier Closure
  -> G2-14 Compatibility Retirement Certification
```

G2-13 must precede G2-14 because compatibility retirement cannot certify final semantic
authority until provider-assisted and legacy classifiers have explicit dispositions.

G2-14 must remain final because it depends on the complete migration evidence set from
G2-01 through G2-13.

## 5. Selected Batch

Selected next implementation batch:

```text
Batch G2-13: Provider-Assisted And Legacy Classifier Closure
```

## 6. Confirmed G2-13 Scope

G2-13 should close provider-assisted and legacy classifier paths as hidden semantic
authority risks.

Expected implementation scope:

- add CSA-first guard evidence for provider-assisted classification paths;
- require deterministic CSA failure or explicit advisory escalation before provider
  suggestions are considered;
- mark provider-assisted outputs advisory-only and non-authoritative;
- inventory legacy classifier entrypoints still capable of semantic interpretation;
- mark each legacy path as CSA-parity migrated, compatibility-only, diagnostic-only,
  unsupported, or retirement candidate;
- record replay-visible classifier source, fallback status, parity evidence, and authority
  denial;
- preserve compatibility fallback for certified historical replay and unsupported paths.

Out of scope for G2-13:

- final compatibility layer retirement;
- deleting historical compatibility evidence;
- changing governance, OCS, PPP, approval, provider, worker, execution, or replay
  authority;
- reinterpreting historical replay.

## 7. Selection Rationale

G2-13 is selected because it is the next batch in the approved dependency graph and its
direct prerequisite, G2-12 classifier source provenance, is complete.

Selection rationale:

- G2-12 supplies structured classifier source provenance and fallback status.
- Provider-assisted paths are the remaining semantic authority risk where advisory output
  could be confused with primary interpretation unless CSA failure is recorded first.
- Legacy classifiers and older entrypoints are the remaining compatibility-era sources that
  must be inventoried before retirement.
- G2-13 provides the final classification evidence required for G2-14 compatibility
  retirement certification.

## 8. Expected Regression Requirements

Expected G2-13 regression coverage:

- provider-assisted classifier tests;
- provider unavailable and malformed provider output tests;
- advisory-only provider boundary tests;
- legacy classifier entrypoint tests;
- prompt-to-conversation and older conversation runtime tests;
- CSA deterministic failure evidence tests;
- replay comparison and fallback status tests;
- provider, worker, approval, execution, governance, and replay non-authority negatives;
- full pytest suite.

## 9. Certification Impact

G2-13 certification should prove:

- provider-assisted classification cannot run as primary semantic authority;
- CSA deterministic failure or explicit advisory escalation is recorded before provider
  suggestion;
- provider output remains advisory and non-authoritative;
- legacy classifier paths are inventoried and classified by disposition;
- compatibility fallback remains observable for certified historical and unsupported paths;
- no governance, OCS, PPP, approval, provider, worker, execution, or replay authority is
  transferred to provider-assisted or legacy classifiers.

This certification is the final prerequisite for G2-14 Compatibility Retirement
Certification.

## 10. Estimated Remaining Effort To Generation 2 Completion

Remaining implementation batches after G2-13 selection:

```text
G2-13 Provider-Assisted And Legacy Classifier Closure
G2-14 Compatibility Retirement Certification
```

Estimated completion shape:

- One provider-assisted and legacy classifier closure batch.
- One final compatibility retirement certification batch.

Generation 2 should be considered complete only after G2-14 certifies every remaining
compatibility path as retired, diagnostic fallback, permanent structured authority, or
explicitly preserved compatibility for historical replay.

## 11. Final Selection

Selected next batch:

```text
Batch G2-13: Provider-Assisted And Legacy Classifier Closure
```

Selection verdict:

```text
PLATFORM_SEMANTIC_GAP_CLOSURE_G2_13_SELECTED
```
