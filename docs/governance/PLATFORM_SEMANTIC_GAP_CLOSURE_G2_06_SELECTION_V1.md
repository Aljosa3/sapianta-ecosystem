# Platform Semantic Gap Closure G2-06 Selection V1

Status: batch selection governance artifact.

Scope: next implementation batch selection after G2-05 Execution Intent And Authorization Entry Semantics.

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
- G2-05: Execution Intent And Authorization Entry Semantics.

Current validation baseline:

```text
5415 passed, 4 skipped
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
- preservation of governance, replay, approval, PPP, execution, provider, worker, and
  lifecycle boundaries.

## 3. Dependency Order

The dependency order has not changed.

The approved graph states:

```text
G2-05 Execution Intent And Authorization Entry Semantics
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

G2-05 satisfied the execution-intent provenance prerequisite. It did not remove the need
to certify worker/domain lifecycle entry semantics before native development, specialized
routes, OCS/PPP annotation, explanation rendering, replay/hardening classifiers,
provider-assisted closure, or compatibility retirement.

## 4. Selected Batch

Selected next implementation batch:

```text
Batch G2-06: Worker And Domain Lifecycle Entry Semantics
```

Final batch identifier:

```text
PLATFORM_SEMANTIC_GAP_CLOSURE_G2_06_WORKER_DOMAIN_LIFECYCLE_ENTRY_SEMANTICS
```

## 5. Selected Gap

Selected semantic gap:

```text
worker/domain lifecycle entry semantics
```

Owning components:

- worker request entry detectors;
- worker assignment entry detectors;
- worker dispatch entry detectors;
- worker invocation entry detectors;
- worker execution entry detectors;
- worker result capture entry detectors;
- worker result validation entry detectors;
- post-execution replay review entry detectors;
- domain approval entry detectors;
- domain execution-ready entry detectors;
- domain execution authorization entry detectors;
- domain handoff and governed termination entry detectors.

Current semantic source:

- `detect_domain_*_entry_intent()` compatibility functions;
- worker/domain prompt markers;
- lifecycle entry phrases;
- structured lifecycle state where already available.

Target semantic source:

- structured lifecycle state first where available;
- CSA requested action and lifecycle target fields for natural-language entry requests;
- compatibility detector output remains fallback and rollback evidence.

## 6. Dependency Readiness

| Dependency | Status |
| --- | --- |
| Platform Core Gen1 certification | Satisfied |
| UBTR beta ready | Satisfied |
| G2-01 replay comparison substrate | Satisfied |
| G2-05 execution-intent source provenance | Satisfied |
| CSA requested action fields | Available for parity comparison |
| CSA worker relevance fields | Available for parity comparison |
| Structured authorization and approval boundaries | Preserved by G2-05 |
| Compatibility fallback and rollback model | Satisfied |

G2-06 is dependency-ready.

## 7. New Dependencies Resolved By G2-05

G2-05 resolved the blocking execution-intent dependency for lifecycle entry migration:

- execution-intent source provenance is now replay-visible;
- CSA can identify execution-related semantics without granting execution authority;
- compatibility execution-intent detector output remains recorded for rollback;
- no-authority evidence is explicit for approval, authorization, provider, worker, and
  execution boundaries;
- generic execution requests remain fail-closed unless a certified structured path exists.

These outcomes allow lifecycle entry detectors to migrate next without conflating
semantic lifecycle intent with approval, authorization, or execution authority.

## 8. Candidate Evaluation

| Candidate | Dependency Readiness | Duplication Reduction | Certification Risk | Selection Result |
| --- | --- | --- | --- | --- |
| worker/domain lifecycle entry semantics | Ready | High | Medium | Selected |
| native development | Depends on lifecycle boundary clarity | High | Medium | Not selected |
| specialized Product/domain/provider/similarity routes | Depends on lifecycle/native source stability | Medium | Medium | Not selected |
| OCS/PPP annotation | Can be annotated, but should follow lifecycle source certification | Medium | Medium | Not selected |
| command boundary certification | Low risk, but exact commands are structured authority and lower duplication | Low | Low | Not selected |
| explanation rendering | Depends on stable route and lifecycle provenance | Medium | Medium | Not selected |
| replay/hardening classifiers | Depends on more migrated structured provenance | Medium | Medium | Not selected |
| provider-assisted/legacy closure | Depends on deterministic CSA and lifecycle failure evidence | High | High | Not selected |
| compatibility retirement | Depends on all prior certified migrations | High | High | Not selected |

## 9. Rationale

G2-06 offers the best balance after G2-05:

- It is the next batch in the approved dependency graph.
- It removes high-value duplicated semantic interpretation across worker and domain
  lifecycle entry detectors.
- It builds directly on G2-05 no-authority execution-intent evidence.
- It keeps structured lifecycle state authoritative where already present.
- It can migrate detector families incrementally by lifecycle stage.
- It creates prerequisite lifecycle source provenance for native development and OCS/PPP
  annotation.

Selecting native development now would risk migrating development-context semantics before
the platform has certified worker/domain lifecycle entry boundaries. Selecting OCS/PPP
annotation now would provide useful provenance but would not reduce as much duplicate
semantic interpretation as G2-06.

## 10. Expected Runtime Scope

Expected future G2-06 implementation scope:

- inventory worker and domain lifecycle entry detector prompt classes;
- add CSA and structured-state comparison evidence to detector outputs;
- record lifecycle detector source, CSA match status, prior compatibility result, and
  no-execution authority evidence;
- make CSA or structured lifecycle state primary only for parity-proven detector classes;
- keep worker execution boundaries unchanged;
- keep approval and execution authorization unchanged;
- preserve all compatibility detector fallbacks.

No runtime changes are made by this selection artifact.

## 11. Replay Impact

G2-06 should record:

- lifecycle entry semantic source;
- CSA reference and hash where CSA participates;
- structured lifecycle state reference where structured state participates;
- previous compatibility detector result;
- semantic comparison artifact;
- lifecycle stage parity evidence;
- requested action parity evidence;
- field differences;
- confidence comparison where applicable;
- migration batch id;
- replay lineage;
- rollback lineage.

Replay must distinguish:

- lifecycle entry semantic interpretation, migrated only where parity is proven;
- approval authority, permanently owned by approval runtimes;
- execution authorization, permanently owned by authorization runtimes;
- worker execution boundaries, permanently owned by worker/governance runtimes.

## 12. Regression Requirements

Expected G2-06 regression coverage:

- worker request tests;
- worker assignment tests;
- worker dispatch tests;
- worker invocation tests;
- worker execution tests;
- worker result capture tests;
- worker result validation tests;
- post-execution replay review tests;
- domain approval entry tests;
- domain execution-ready tests;
- domain execution authorization tests;
- domain handoff and termination tests;
- replay lineage tests;
- rollback/fallback tests;
- full pytest suite.

## 13. Rollback Strategy

Rollback strategy for the future G2-06 implementation:

- keep every `detect_domain_*_entry_intent()` compatibility function active;
- compute and record previous compatibility detector output for every migrated decision;
- prefer structured lifecycle state only where it already exists and passes parity;
- gate CSA-primary selection behind exact lifecycle stage and requested-action parity;
- fall back to compatibility when CSA is absent, divergent, ambiguous, or outside a
  certified lifecycle stage;
- never let CSA or detector output create approval, authorization, dispatch, invocation,
  execution, or result acceptance authority.

## 14. Certification Criteria

G2-06 is certifiable only if:

- lifecycle stage matches the previous detector output;
- requested action matches the previous detector output;
- worker execution boundaries remain unchanged;
- no detector grants execution authority;
- structured lifecycle state is preferred where available;
- CSA is primary only for parity-proven natural-language entry requests;
- compatibility fallback remains active and replay-visible;
- full validation succeeds.

## 15. Remaining Inventory After Selected G2-06

Remaining candidates after the selected batch:

- native development;
- specialized Product/domain/provider/similarity routes;
- OCS/PPP annotation;
- command boundary certification;
- explanation rendering;
- replay/hardening classifiers;
- provider-assisted/legacy closure;
- compatibility retirement.

Recommended next dependency after G2-06 certification:

```text
G2-07: Native Development Semantics
```

## 16. Final Selection

Selected next batch:

```text
Batch G2-06: Worker And Domain Lifecycle Entry Semantics
```

Selection verdict:

```text
PLATFORM_SEMANTIC_GAP_CLOSURE_G2_06_SELECTED
```
