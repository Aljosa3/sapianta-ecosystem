# Platform Semantic Gap Closure G2-04 Selection V1

Status: batch selection governance artifact.

Scope: next implementation batch selection after G2-03 HIRR Remaining Intake Families.

This artifact does not implement runtime code, modify tests, change routing behavior, retire compatibility layers, or alter governance authority.

## 1. Purpose

Platform Core Generation 1 is certified.

UBTR implementation is beta ready.

Completed Generation 2 semantic migration work:

- Consumer Migration Batch 01: ACLI CSA-primary routing subset.
- Consumer Migration Batch 02: HIRR ambiguous-intent clarification intake.
- G2-01: Replay Comparison Substrate.
- G2-02: Proposal-Only OCS Routing.
- G2-03: HIRR Remaining Intake Families.

Current validation baseline:

```text
5410 passed, 4 skipped
```

This artifact selects the next implementation batch from the approved Platform Semantic Gap Closure Program.

## 2. Selection Criteria

The next batch was selected using:

- dependency readiness;
- lowest certification risk;
- highest semantic duplication reduction;
- replay comparison support;
- parity evidence availability;
- preservation of Generation 1 behavior;
- preservation of governance, replay, approval, PPP, execution, provider, and worker boundaries.

## 3. Selected Batch

Selected next implementation batch:

```text
Batch G2-04: HIRR Clarification Continuity
```

Final batch identifier:

```text
PLATFORM_SEMANTIC_GAP_CLOSURE_G2_04_HIRR_CLARIFICATION_CONTINUITY
```

## 4. Rationale

G2-04 is selected because it is the next batch in the approved dependency graph.

The dependency graph states:

```text
G2-03 HIRR Remaining Intake Families
  -> G2-04 HIRR Clarification Continuity
```

G2-04 is now dependency-ready because:

- G2-01 provides replay-visible CSA versus compatibility comparison evidence.
- Batch 02 proves HIRR can consume CSA for ambiguous-intent clarification intake.
- G2-03 proves HIRR can consume CSA for remaining deterministic intake families.
- HIRR final boundaries are frozen: UBTR owns meaning, HIRR owns lifecycle.
- The next unresolved HIRR semantic duplication is clarification reply interpretation and target refinement.

Selecting a later batch would skip a required HIRR dependency.

## 5. Selected Gap

Selected semantic gap:

```text
HIRR clarification continuity and reply refinement
```

Owning component:

```text
HIRR continuity runtime
```

Current semantic source:

- local clarification reply markers;
- local target refinement rules;
- local proposal-only-after-clarification markers;
- compatibility clarification state.

Target semantic source:

- linked original CSA;
- clarification-turn CSA;
- G2-01 comparison evidence;
- HIRR lifecycle state remains authoritative.

## 6. Dependency Readiness

| Dependency | Status |
| --- | --- |
| Platform Core Gen1 certification | Satisfied |
| UBTR beta ready | Satisfied |
| G2-01 replay comparison substrate | Satisfied |
| Batch 02 ambiguous HIRR intake CSA path | Satisfied |
| G2-03 remaining HIRR intake families | Satisfied |
| UBTR/HIRR boundary frozen | Satisfied |
| HIRR lifecycle remains authoritative | Satisfied |

No later batch is required before G2-04 begins.

## 7. Certification Risk

Certification risk: Medium.

Risk is higher than G2-03 because clarification continuity depends on multi-turn state and target preservation.

Risk remains acceptable because:

- HIRR lifecycle state remains authoritative;
- CSA is used only for reply semantics where parity is proven;
- compatibility reply refinement remains fallback;
- replay comparison substrate can expose CSA/local divergence before CSA becomes primary;
- no provider, worker, approval, execution, PPP, OCS, governance, or replay mutation authority changes.

Primary certification risks:

- target refinement could change incorrectly;
- clarification reply could reduce ambiguity too aggressively;
- proposal-only-after-clarification could bypass OCS ownership;
- multilingual reply parity may be partial;
- unsafe escalation must still fail closed.

## 8. Semantic Duplication Reduction

G2-04 reduces duplication in the remaining HIRR layer:

- clarification reply semantic interpretation moves toward UBTR/CSA;
- local HIRR reply markers become compatibility fallback;
- target refinement can be compared against linked original and reply-turn CSA;
- proposal-only-after-clarification can reuse the G2-02 OCS no-execution model where parity is proven.

This is the highest-priority duplication reduction available because G2-03 completed HIRR intake-family semantics, leaving clarification continuity as the next HIRR semantic owner.

## 9. Replay Comparison Support

Replay comparison support is available through G2-01.

G2-04 should record:

- original CSA reference and hash;
- clarification-turn CSA reference and hash;
- previous compatibility reply interpretation;
- CSA reply interpretation;
- ambiguity reduction evidence;
- target preservation evidence;
- semantic equivalence result;
- field differences;
- confidence comparison;
- parity status;
- migration batch id;
- rollback lineage.

Replay must distinguish:

- semantic reply interpretation, owned by UBTR/CSA where parity is proven;
- clarification lifecycle state, permanently owned by HIRR.

## 10. Parity Evidence Availability

Parity evidence is partially available and sufficient to begin G2-04 as a narrow implementation batch.

Available evidence:

- HIRR intake artifacts are now CSA-primary for deterministic families.
- Existing clarification continuity tests cover target preservation and workflow selection.
- Existing replay reconstruction can bind HIRR and conversational routing evidence.
- G2-01 comparison substrate can record CSA/local agreement or divergence.

Parity evidence still required during implementation:

- original CSA to reply-turn CSA linkage;
- reply interpretation parity;
- ambiguity reduction parity;
- target preservation parity;
- proposal-only-after-clarification no-execution parity;
- negative tests for unsafe escalation and unsupported reply classes.

## 11. Expected Runtime Scope

Expected future runtime implementation scope:

- add replay-visible original CSA and reply-turn CSA linkage to HIRR clarification continuity;
- compare CSA reply semantics with existing local reply refinement;
- make CSA primary only for parity-proven clarification reply classes;
- preserve local compatibility fallback for all non-parity replies;
- preserve HIRR lifecycle state, active clarification reconstruction, reply binding, and target allowlists;
- preserve OCS ownership for proposal-only continuation.

No runtime changes are made by this selection artifact.

## 12. Expected Regression Requirements

Expected G2-04 regression coverage:

- clarification promotion;
- target preservation;
- ambiguity reduction;
- multilingual clarification reply behavior;
- proposal-only after clarification;
- unsafe escalation fail-closed;
- reply binding to original clarification request;
- replay reconstruction with original and reply-turn CSA hashes;
- compatibility fallback for non-parity replies;
- no provider, worker, approval, execution, PPP, OCS, governance, or replay mutation authority changes.

Expected validation for implementation:

```text
git diff --check
python -m py_compile
targeted HIRR continuity tests
targeted replay comparison tests
targeted UBTR/HIRR integration tests
full python -m pytest -q
```

## 13. Rollback Strategy

Rollback strategy for the future G2-04 implementation:

- disable CSA-primary clarification reply refinement;
- keep local HIRR continuity refinement authoritative;
- preserve CSA comparison artifacts as observational replay evidence;
- preserve original and reply-turn CSA lineage if already recorded;
- do not reinterpret historical replay;
- preserve HIRR lifecycle state and reply binding.

Rollback must not:

- erase CSA lineage;
- retire compatibility markers;
- alter approval, provider, worker, execution, PPP, OCS, governance, or replay authority.

## 14. Non-Selected Batches

The following batches are not selected now because they depend on G2-04 or are lower in the approved sequence:

- execution intent;
- worker/domain lifecycle entry semantics;
- native development;
- specialized Product/domain/provider/similarity routes;
- OCS/PPP annotation;
- command boundary certification;
- explanation rendering;
- replay/hardening classifiers;
- provider-assisted/legacy closure;
- compatibility retirement.

Command boundary certification has low risk, but selecting it now would skip the approved HIRR dependency chain.

## 15. Selection Conclusion

The next implementation batch is:

```text
Batch G2-04: HIRR Clarification Continuity
```

This selection follows the approved dependency graph exactly, is dependency-ready after G2-03, and addresses the next remaining HIRR semantic duplication while preserving HIRR lifecycle ownership.

Final verdict:

PLATFORM_SEMANTIC_GAP_CLOSURE_G2_04_SELECTED
