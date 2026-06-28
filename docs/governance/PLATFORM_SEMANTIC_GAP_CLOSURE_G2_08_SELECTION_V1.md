# Platform Semantic Gap Closure G2-08 Selection V1

Status: batch selection governance artifact.

Scope: next implementation batch selection after G2-07 Native Development Semantics.

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

Current validation baseline:

```text
5417 passed
4 skipped
0 failed
```

This artifact re-evaluates the remaining semantic migration inventory after G2-07 and
selects the next highest-priority Generation 2 implementation batch.

## 2. Updated Remaining Inventory

| Area | Semantic Duplication Reduction | Dependency Readiness | Certification Impact | Replay Visibility | Regression Risk | Rollback Complexity | Architectural Importance |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Specialized Product/domain/provider/similarity routes | High | Ready after G2-07 native source stability; execute as sub-batches | High for Product 1 and domain activation; medium for provider and similarity | Good for route-level decisions; mixed for family-specific subflows | Medium | Medium; route-family compatibility fallbacks stay active | Very high; this is the largest remaining ACLI route-marker cluster |
| OCS/PPP annotation | Medium | Partially ready, but should follow specialized route source certification | Medium | Good after G2-01 and migrated route source fields | Medium | Low; annotation-only rollback is simple | High for downstream lineage, but lower direct semantic duplication reduction |
| Command boundary certification | Low | Ready in parallel because exact commands remain structured authority | High | Good | Low | Low | High for certification hardening; not a primary semantic migration |
| Explanation rendering | Medium | Should follow stable route, OCS, and PPP provenance | Medium | Good once upstream source fields are stable | Medium | Low; compatibility renderer remains fallback | Medium-high for operator clarity |
| Replay/hardening classifiers | Medium | Depends on more migrated structured provenance and legacy classification inventory | Medium | Good for new sessions; mixed for legacy replay | Medium | Medium; legacy scan fallback remains required | High for retirement readiness |
| Provider-assisted/legacy closure | High | Not ready until deterministic CSA failure evidence covers specialized routes | High | Mixed; legacy entrypoints need explicit source inventory | High | Medium | High, but late-stage after primary route migrations |
| Compatibility retirement | High | Not ready until all prior migration and closure batches certify | Very high | Must cover migrated and legacy replay | High | High | Final Generation 2 completion step |

Remaining worker/domain lifecycle detector families stay on compatibility fallback unless
a later hardening or closure batch finds additional parity evidence. They do not outrank
the specialized route cluster after G2-07 because G2-06 already certified the lifecycle
pattern and G2-07 resolved the native-development prerequisite.

## 3. Updated Dependency Graph

The existing dependency graph remains optimal.

```text
G2-07 Native Development Semantics
  -> G2-08 Specialized Product, Domain, Provider, Similarity Routes
      -> G2-08A Domain Proposal And Unknown-Domain Clarification
      -> G2-08B Provider Onboarding
      -> G2-08C Product 1 Decision Validation Routing
      -> G2-08D Semantic Similarity And Broad OCS Cognition Route Subsets
  -> G2-09 OCS Semantic Lineage And PPP Annotation
  -> G2-10 Command Boundary And Recommendation Prose Certification
  -> G2-11 Explanation Rendering Migration
  -> G2-12 Replay, Hardening, And Replay-Derived Classifiers
  -> G2-13 Provider-Assisted And Legacy Classifier Closure
  -> G2-14 Compatibility Retirement Certification
```

Parallel measurement remains permissible for command boundary certification and
explanation parity. Those workstreams must remain observational until the specialized
route family source fields are certified.

## 4. Selected Batch

Recommended next implementation batch:

```text
Batch G2-08: Specialized Product, Domain, Provider, And Similarity Routes
```

Recommended first implementation sub-batch:

```text
G2-08A: Domain Proposal And Unknown-Domain Clarification
```

## 5. Selection Rationale

G2-08 is selected because it is the next dependency-ready semantic cluster after native
development certification.

The specialized route cluster now has the best combined score:

- It is the next batch in the approved Platform Semantic Gap Closure Program.
- It removes a broad ACLI compatibility-marker family without touching runtime authority.
- G2-05, G2-06, and G2-07 provide prerequisite execution, lifecycle, and native boundary
  provenance.
- It prepares the ground for OCS/PPP annotation by stabilizing more upstream route source
  fields.
- It keeps Product 1, domain, provider, and similarity semantics bounded inside
  independently certifiable sub-batches.
- Compatibility fallback remains straightforward because each route family already has a
  local compatibility detector or structured runtime boundary.

G2-09 OCS/PPP annotation is not selected yet because downstream annotation should follow
the specialized route source fields. Command boundary certification is lower risk and can
be measured in parallel, but it does not reduce as much duplicated natural-language route
interpretation. Explanation, hardening, provider-assisted closure, and compatibility
retirement remain later-stage dependencies.

## 6. Expected G2-08 Runtime Scope

Expected future implementation scope:

- add CSA-primary gates for parity-proven specialized route families only;
- record previous compatibility route evidence for every migrated family;
- preserve compatibility fallback for every divergent, ambiguous, low-confidence, or
  unsupported case;
- keep Product 1 framed as AI Decision Validator;
- keep domain activation approval-gated;
- keep provider ownership and credential governance separate;
- keep semantic similarity and domain reference adaptation bounded and non-authorizing;
- prevent broad OCS cognition migration from bypassing OCS authority.

No runtime changes are made by this selection artifact.

## 7. Expected Regression Requirements

Expected G2-08 regression coverage:

- domain proposal and unknown-domain clarification tests;
- provider onboarding and unsupported provider route tests;
- Product 1 packet, enterprise demo, and decision validation tests;
- semantic similarity and domain reference adaptation tests;
- broad OCS cognition routing tests;
- ACLI route replay comparison tests;
- governance, approval, provider, worker, and execution boundary negatives;
- full pytest suite.

## 8. Certification Impact

G2-08 certification should prove:

- each specialized family migrates independently and only under deterministic parity;
- Product 1 remains AI Decision Validator and does not drift into generic chatbot or
  unrestricted autonomy framing;
- unknown-domain and domain proposal flows do not activate domains before approval;
- provider onboarding does not grant credential or provider execution authority;
- similarity/adaptation remains proposal and validation bounded;
- OCS cognition routes remain OCS-owned where cognition is required;
- compatibility fallback stays active and replay-visible.

This certification is high impact because specialized ACLI route markers are the largest
remaining route-level semantic duplication cluster after native development.

## 9. Rollback Strategy

Rollback strategy for the future G2-08 implementation:

- keep each specialized compatibility detector active;
- gate CSA-primary selection per family, not across the whole cluster;
- record CSA hash, previous compatibility interpretation, parity evidence, divergence
  reason, and fallback status;
- fall back to compatibility when CSA is absent, divergent, ambiguous, low confidence, or
  outside the certified family;
- never allow CSA to mutate governance, activate domains, approve execution, select
  providers, invoke workers, or expand Product 1 messaging.

## 10. Final Selection

Selected next batch:

```text
Batch G2-08: Specialized Product, Domain, Provider, And Similarity Routes
```

Selection verdict:

```text
PLATFORM_SEMANTIC_GAP_CLOSURE_G2_08_SELECTED
```
