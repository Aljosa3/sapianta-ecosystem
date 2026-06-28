# Platform Semantic Gap Closure G2-07 Selection V1

Status: batch selection governance artifact.

Scope: next implementation batch selection after G2-06 Worker And Domain Lifecycle Entry
Semantics.

This artifact does not implement runtime code, modify tests, change routing behavior,
retire compatibility layers, or alter governance authority.

## 1. Purpose

Platform Core Generation 1 is certified.

Completed Generation 2 semantic migration work:

- Consumer Migration Batch 01: ACLI CSA-primary routing subset.
- Consumer Migration Batch 02: HIRR ambiguous-intent clarification intake.
- G2-01: Replay Comparison Substrate.
- G2-02: Proposal-Only OCS Routing.
- G2-03: Remaining HIRR Intake Families.
- G2-04: HIRR Clarification Continuity.
- G2-05: Execution Intent And Authorization Entry Semantics.
- G2-06: Worker And Domain Lifecycle Entry Semantics.

Current validation baseline:

```text
5415 passed
4 skipped
0 failed
```

This artifact re-evaluates the remaining semantic migration inventory after G2-06 and
selects the next highest-priority Generation 2 implementation batch.

## 2. Updated Dependency Graph

The previously planned ordering still represents the optimal implementation sequence.

```text
G2-06 Worker And Domain Lifecycle Entry Semantics
  -> G2-07 Native Development Semantics
  -> G2-08 Specialized Product, Domain, Provider, Similarity Routes
  -> G2-09 OCS Semantic Lineage And PPP Annotation
  -> G2-10 Command Boundary And Recommendation Prose Certification
  -> G2-11 Explanation Rendering Migration
  -> G2-12 Replay, Hardening, And Replay-Derived Classifiers
  -> G2-13 Provider-Assisted And Legacy Classifier Closure
  -> G2-14 Compatibility Retirement Certification
```

Parallel measurement remains permissible for explanation parity, PPP annotation, and
command-boundary analysis, but none should become the next primary migration before
native development semantics are certified.

## 3. G2-06 Dependency Impact

G2-06 resolved the lifecycle provenance prerequisite for native development by proving:

- lifecycle entry CSA comparisons can be replay-visible and hash-bound;
- worker/domain authority boundaries can remain unchanged while CSA supplies semantics;
- compatibility lifecycle detectors can remain rollback-visible;
- CSA can be rejected cleanly for non-certified lifecycle classes;
- no approval, authorization, worker, provider, PPP, lifecycle, replay, or governance
  authority transfer is required.

G2-06 did not fully retire lifecycle compatibility detectors. Remaining detector families
stay in the migration inventory, but they do not block G2-07 because compatibility fallback
remains active and the dependency graph now advances to native development.

## 4. Remaining Semantic Inventory

| Area | Semantic Duplication Reduction | Certification Impact | Dependency Readiness | Regression Risk | Rollback Complexity | Replay Visibility | Architectural Importance |
| --- | --- | --- | --- | --- | --- | --- | --- |
| remaining worker/domain lifecycle detector families | Medium | Medium | Partially ready; G2-06 pattern exists, but CSA parity remains uneven | Medium | Low; compatibility detectors remain active | Good after G2-06 fields | Important, but incremental after G2-06 |
| native development | High | High | Ready after execution-intent and lifecycle provenance batches | Medium | Medium; native catalog fallback must stay active | Good through G2-01/G2-06 routing evidence | Very high because native development is a major remaining ACLI semantic owner |
| specialized Product/domain/provider/similarity routes | Medium | High for Product 1; medium for provider/domain/similarity | Depends on native development source stability | Medium | Medium; route-family fallbacks remain available | Good for routing, mixed for specialized subflows | High, but sequenced after native development |
| OCS/PPP annotation | Medium | Medium | Annotation can be prototyped, primary migration should follow native/specialized route provenance | Medium | Low; annotation-only fallback is simple | Good | High for downstream lineage, lower semantic-duplication reduction |
| command boundary certification | Low | High | Ready in parallel because exact commands remain structured authority | Low | Low | Good | Important as certification hardening, not highest semantic migration value |
| explanation rendering | Medium | Medium | Depends on stable route and lifecycle provenance | Medium | Low; compatibility renderer can remain primary | Good once source provenance is stable | Medium-high for operator clarity |
| replay/hardening classifiers | Medium | Medium | Depends on more migrated structured provenance | Medium | Medium; legacy scan fallback must remain | Good for new sessions, mixed for legacy | High for retirement readiness |
| provider-assisted/legacy closure | High | High | Not ready until deterministic CSA failure evidence and native/specialized routes mature | High | Medium | Mixed; legacy entrypoints need inventory | High, but late-stage |
| compatibility retirement | High | Very high | Not ready until all prior migrations certify | High | High | Must cover migrated and legacy replay | Final Generation 2 closure step |

## 5. Selected Batch

Recommended next implementation batch:

```text
Batch G2-07: Native Development Semantics
```

Final batch identifier:

```text
PLATFORM_SEMANTIC_GAP_CLOSURE_G2_07_NATIVE_DEVELOPMENT_SEMANTICS
```

## 6. Selection Rationale

Native development is selected because it now has the best combined score across the
selection criteria:

- It is the next batch in the approved dependency graph.
- It offers high semantic duplication reduction across native development routing,
  native development task intake, development context assembly, and PPP handoff.
- G2-05 and G2-06 resolved the key prerequisites: execution-intent provenance and
  lifecycle boundary provenance.
- It preserves the crucial architectural distinction between native development,
  governed development, and HIRR clarification.
- It provides prerequisite source stability for specialized Product/domain/provider/
  similarity routes.
- It can keep native catalog and structured context fallbacks active during migration.

Remaining worker/domain lifecycle detector families are not selected because G2-06 already
established the lifecycle migration pattern and left non-certified detector families on
safe compatibility fallback. Continuing the lifecycle family now would produce incremental
duplication reduction, while native development removes a larger remaining semantic owner.

## 7. Expected G2-07 Runtime Scope

Expected future implementation scope:

- add CSA catalog comparison to native development routing decisions;
- compare CSA development domain/resource/action fields against native catalog markers;
- make CSA primary only for parity-proven native development targets;
- preserve native catalog fallback for non-parity prompts;
- preserve native development context assembly as structured context authority;
- preserve PPP handoff ownership and structured PPP artifacts;
- prevent collapse of native development into governed development or HIRR clarification.

No runtime changes are made by this selection artifact.

## 8. Expected Regression Requirements

Expected G2-07 regression coverage:

- native development intent routing tests;
- native development task intake tests;
- development context assembly tests;
- PPP handoff and continuation tests;
- provider/resource unsupported route tests;
- governed-development boundary tests;
- HIRR clarification boundary tests;
- replay comparison tests;
- rollback/fallback tests;
- full pytest suite.

## 9. Certification Impact

G2-07 certification should prove:

- native development route parity is CSA-primary only where certified;
- native development does not collapse into governed development;
- native development context assembly remains structured and replay-safe;
- PPP handoff remains PPP-owned;
- unsupported provider/resource requests still fail closed;
- compatibility fallback remains active and replay-visible.

This certification is important because native development is one of the largest remaining
compatibility-era semantic owners in ACLI.

## 10. Rollback Strategy

Rollback strategy for the future G2-07 implementation:

- keep native development catalog markers active;
- compute and record previous native catalog output for every migrated decision;
- gate CSA-primary selection behind exact route, resource, and context parity;
- fall back to native catalog markers when CSA is absent, divergent, ambiguous, or
  outside a certified native target;
- never let CSA mutate context, PPP artifacts, worker state, approval, execution, or
  governance.

## 11. Remaining Inventory After Selected G2-07

Remaining candidates after the selected batch:

- remaining worker/domain lifecycle detector families;
- specialized Product/domain/provider/similarity routes;
- OCS/PPP annotation;
- command boundary certification;
- explanation rendering;
- replay/hardening classifiers;
- provider-assisted/legacy closure;
- compatibility retirement.

Recommended next dependency after G2-07 certification:

```text
G2-08: Specialized Product, Domain, Provider, And Similarity Routes
```

## 12. Final Selection

Selected next batch:

```text
Batch G2-07: Native Development Semantics
```

Selection verdict:

```text
PLATFORM_SEMANTIC_GAP_CLOSURE_G2_07_SELECTED
```
