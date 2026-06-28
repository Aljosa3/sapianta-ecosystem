# Platform Semantic Gap Closure G2-05 Selection V1

Status: batch selection governance artifact.

Scope: next implementation batch selection after G2-04 HIRR Clarification Continuity.

This artifact does not implement runtime code, modify tests, change routing behavior,
retire compatibility layers, or alter governance authority.

## 1. Purpose

Platform Core Generation 1 is certified.

UBTR implementation is beta ready.

Completed Generation 2 semantic migration work:

- Consumer Migration Batch 01: ACLI CSA-primary routing subset.
- Consumer Migration Batch 02: HIRR ambiguous-intent clarification intake.
- G2-01: Replay Comparison Substrate.
- G2-02: Proposal-Only OCS Routing.
- G2-03: HIRR Remaining Intake Families.
- G2-04: HIRR Clarification Continuity.

Current validation baseline:

```text
5412 passed, 4 skipped
```

This artifact re-evaluates the remaining semantic migration inventory and selects the
next implementation batch from the approved Platform Semantic Gap Closure Program.

## 2. Selection Criteria

The next batch is selected using:

- dependency readiness;
- adherence to the approved dependency graph;
- highest semantic duplication reduction;
- lowest certification risk among dependency-ready batches;
- replay comparison support;
- parity evidence availability;
- preservation of Generation 1 behavior;
- preservation of governance, replay, approval, PPP, execution, provider, and worker
  boundaries.

## 3. Original Dependency Order

The original dependency order still holds.

The approved graph states:

```text
G2-04 HIRR Clarification Continuity
  -> G2-05 Execution Intent And Authorization Entry Semantics
  -> G2-06 Worker And Domain Lifecycle Entry Semantics
  -> G2-07 Native Development Semantics
  -> G2-08 Specialized Product, Domain, Provider, Similarity Routes
  -> G2-09 OCS Semantic Lineage And PPP Annotation
  -> G2-10 Command Boundary And Recommendation Prose Certification
  -> G2-11 Explanation Rendering Migration
  -> G2-12 Replay, Hardening, And Replay-Derived Classifiers
  -> G2-13 Provider-Assisted And Legacy Classifier Closure
  -> G2-14 Compatibility Retirement Certification
```

G2-04 satisfied the HIRR clarification-continuity prerequisite. It did not remove the
need to certify execution-intent semantics before worker/domain lifecycle, native
development, specialized routes, OCS/PPP annotation, explanation rendering, hardening,
provider-assisted closure, or compatibility retirement.

## 4. Selected Batch

Selected next implementation batch:

```text
Batch G2-05: Execution Intent And Authorization Entry Semantics
```

Final batch identifier:

```text
PLATFORM_SEMANTIC_GAP_CLOSURE_G2_05_EXECUTION_INTENT_AUTHORIZATION_ENTRY_SEMANTICS
```

## 5. Selected Gap

Selected semantic gap:

```text
execution intent
```

Owning components:

- human execution intent detection;
- execution authorization entry surfaces;
- approval boundary evidence;
- governed execution handoff surfaces.

Current semantic source:

- prompt-level compatibility execution-intent markers;
- local artifact-creation and generic execution detectors;
- entry-surface fail-closed rules;
- approval boundary checks.

Target semantic source:

- CSA execution intent;
- CSA requested actions;
- CSA approval-required state;
- CSA worker relevance and entity fields;
- existing structured authorization state remains authoritative.

## 6. Dependency Readiness

| Dependency | Status |
| --- | --- |
| Platform Core Gen1 certification | Satisfied |
| UBTR beta ready | Satisfied |
| G2-01 replay comparison substrate | Satisfied |
| G2-02 proposal-only no-execution model | Satisfied |
| G2-03 HIRR remaining intake families | Satisfied |
| G2-04 HIRR clarification continuity | Satisfied |
| CSA execution intent, requested action, approval-required fields | Available for parity comparison |
| Compatibility fallback and rollback model | Satisfied |

G2-05 is dependency-ready.

## 7. New Dependencies Resolved By G2-04

G2-04 resolved the remaining HIRR semantic prerequisite before execution-intent
migration:

- HIRR no longer blocks the execution-intent batch with unresolved clarification
  continuity ownership.
- Replay now has a proven pattern for CSA reference/hash plus previous compatibility
  interpretation inside multi-turn HIRR flows.
- Compatibility fallback remains active and observable after a CSA-primary migration.
- The platform can now move from intake/clarification semantics toward execution-intent
  semantics without skipping HIRR boundary certification.

No later-batch dependency was newly resolved enough to bypass G2-05.

## 8. Candidate Evaluation

| Candidate | Dependency Readiness | Duplication Reduction | Certification Risk | Selection Result |
| --- | --- | --- | --- | --- |
| execution intent | Ready | High | Medium | Selected |
| worker/domain lifecycle entry semantics | Blocked by execution-intent source certification | High | Medium | Not selected |
| native development | Depends on execution and lifecycle boundary clarity | High | Medium | Not selected |
| specialized Product/domain/provider/similarity routes | Depends on execution/lifecycle/native route source stability | Medium | Medium | Not selected |
| OCS/PPP annotation | Can be prototyped, but should follow execution/lifecycle source certification | Medium | Medium | Not selected |
| command boundary certification | Low risk, but exact commands are structured authority and lower duplication | Low | Low | Not selected |
| explanation rendering | Depends on stable authoritative route provenance | Medium | Medium | Not selected |
| replay/hardening classifiers | Depends on more migrated structured provenance | Medium | Medium | Not selected |
| provider-assisted/legacy closure | Depends on deterministic CSA failure evidence from earlier batches | High | High | Not selected |
| compatibility retirement | Depends on all prior certified migrations | High | High | Not selected |

## 9. Rationale

G2-05 offers the best balance after G2-04:

- It is the next batch in the approved dependency graph.
- It removes a high-value duplicate semantic owner: local execution-intent
  interpretation.
- It is narrower than worker/domain lifecycle or native development migration.
- It can use CSA execution intent, requested actions, approval-required fields, and
  worker relevance as parity evidence.
- It preserves the permanent boundary that CSA may identify execution intent but must
  never authorize execution.
- It provides prerequisite evidence for worker/domain lifecycle entry semantics.

Selecting G2-06 or G2-07 now would risk migrating lifecycle or native-development
semantics before the platform has certified how CSA execution-intent fields interact with
approval and authorization entry boundaries.

## 10. Expected Runtime Scope

Expected future G2-05 implementation scope:

- add CSA comparison evidence to human execution-intent detector outputs;
- record CSA execution intent, requested actions, approval-required state, worker
  relevance, and entity fields;
- record previous compatibility detector result and fail-closed reason;
- make CSA primary only for parity-proven detector classes;
- keep execution authorization structured and fail-closed;
- keep approval authority outside UBTR;
- keep compatibility detector fallback available.

No runtime changes are made by this selection artifact.

## 11. Replay Impact

G2-05 should record:

- semantic execution-intent source;
- CSA reference and hash;
- compatibility execution-intent detector result;
- semantic comparison artifact;
- field differences;
- confidence comparison;
- parity status;
- migration batch id;
- fail-closed reason source;
- approval-required source;
- rollback lineage.

Replay must distinguish:

- semantic execution-intent detection, owned by UBTR/CSA where parity is proven;
- execution authorization, permanently owned by structured governance and approval
  surfaces.

## 12. Regression Requirements

Expected G2-05 regression coverage:

- execution-intent detector tests;
- governed artifact creation and execution-intent tests;
- generic execution fail-closed tests;
- approval-required negative tests;
- authorization boundary tests;
- worker relevance no-authority tests;
- replay comparison tests;
- rollback/fallback tests;
- full pytest suite.

## 13. Rollback Strategy

Rollback strategy for the future G2-05 implementation:

- keep compatibility execution-intent detector outputs computed;
- keep previous detector result replay-visible;
- gate CSA-primary selection behind exact parity;
- fall back to compatibility when CSA is absent, divergent, ambiguous, or indicates
  authority it cannot own;
- never allow CSA to create authorization or approve execution;
- preserve fail-closed behavior for generic execution requests.

## 14. Certification Criteria

G2-05 is certifiable only if:

- CSA never grants execution authority;
- CSA never grants approval authority;
- approval-required state remains explicit and replay-visible;
- generic execution requests still fail closed unless a certified structured path exists;
- parity-proven execution-intent classes route identically to compatibility behavior;
- prior detector result remains replay-visible;
- compatibility fallback remains active;
- full validation succeeds.

## 15. Remaining Inventory After Selected G2-05

Remaining candidates after the selected batch:

- worker/domain lifecycle entry semantics;
- native development;
- specialized Product/domain/provider/similarity routes;
- OCS/PPP annotation;
- command boundary certification;
- explanation rendering;
- replay/hardening classifiers;
- provider-assisted/legacy closure;
- compatibility retirement.

Recommended next dependency after G2-05 certification:

```text
G2-06: Worker And Domain Lifecycle Entry Semantics
```

## 16. Final Selection

Selected next batch:

```text
Batch G2-05: Execution Intent And Authorization Entry Semantics
```

Selection verdict:

```text
PLATFORM_SEMANTIC_GAP_CLOSURE_G2_05_SELECTED
```
