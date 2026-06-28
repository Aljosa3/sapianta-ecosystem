# Platform Semantic Gap Closure Batch Selection V1

Status: batch selection governance artifact.

Scope: next implementation batch selection from Platform Semantic Gap Closure Program V1.

This artifact does not implement runtime code, modify tests, change routing behavior, retire compatibility layers, or alter governance authority.

## 1. Purpose

Platform Core Generation 1 is certified.

UBTR architecture is complete.

UBTR implementation is beta ready.

The approved planning artifacts are:

- UBTR Consumer Migration Master Plan V1;
- Platform Wide Semantic Responsibility Audit V1;
- Platform Semantic Gap Closure Program V1.

This artifact selects the next implementation batch from the closure program.

## 2. Selection Criteria

The next batch was selected by evaluating:

1. highest remaining semantic gap priority;
2. satisfied dependencies;
3. greatest reduction in duplicated semantic responsibility;
4. lowest certification risk;
5. preservation of Generation 1 behavior;
6. replay and rollback value for later batches.

## 3. Selected Next Batch

Selected next batch:

```text
Batch G2-01: Replay Comparison Substrate
```

Program objective:

```text
Create replay-visible comparison evidence for every remaining semantic consumer without changing selected behavior.
```

Final selection:

```text
PLATFORM_SEMANTIC_GAP_CLOSURE_BATCH_G2_01_REPLAY_COMPARISON_SUBSTRATE
```

## 4. Rationale

Batch G2-01 is the correct next implementation batch because it is the first dependency for the rest of the closure program.

It provides the highest platform value without changing runtime decisions:

- records CSA/UBTR evidence beside current compatibility interpretation;
- exposes agreement, divergence, and fallback reasons;
- creates the evidence substrate required by later CSA-primary migrations;
- reduces hidden duplicated semantic responsibility by making every local semantic consumer observable;
- preserves Generation 1 behavior because selected workflow outcomes remain unchanged;
- preserves rollback because compatibility remains authoritative during this batch.

Other high-value batches depend on G2-01:

- proposal-only OCS migration needs previous marker evidence and CSA comparison fields;
- remaining HIRR intake migration needs family-level parity evidence;
- HIRR continuity migration needs linked original and reply-turn CSA evidence;
- execution, worker, native development, Product 1, domain, provider, explanation, hardening, and legacy closure batches all require stable semantic-source provenance.

Therefore G2-01 has all dependencies satisfied and unlocks the rest of the implementation sequence.

## 5. Highest Priority Gap

Highest priority gap:

```text
Unobservable duplicated semantic responsibility across remaining natural-language consumers.
```

Owning components:

- ACLI conversational routing;
- proposal-only OCS route detection;
- HIRR intake;
- HIRR continuity;
- execution-intent detection;
- native development routing and context intake;
- Product 1, domain, provider, and semantic similarity route surfaces;
- provider-assisted intent classification;
- replay/hardening/replay-derived classifiers.

Why it is highest priority:

- later migrations cannot safely make CSA primary without prior compatibility evidence;
- replay must prove both the CSA semantic source and previous compatibility interpretation;
- current duplicate classifiers remain bounded but not uniformly visible;
- the closure program requires comparison evidence before semantic retirement or CSA-primary expansion.

## 6. Dependencies Satisfied

Batch G2-01 dependencies are satisfied:

| Dependency | Status |
| --- | --- |
| Platform Core Generation 1 certification | Satisfied |
| UBTR architecture complete | Satisfied |
| UBTR beta ready | Satisfied |
| Batch 01 ACLI CSA subset certified | Satisfied |
| Batch 02 HIRR CSA subset certified | Satisfied |
| UBTR/HIRR boundary frozen | Satisfied |
| Platform-wide semantic responsibility audit complete | Satisfied |
| Closure program complete | Satisfied |

Batch G2-01 does not depend on future primary-route migration.

It is a behavior-preserving evidence batch.

## 7. Reduction In Duplicated Semantic Responsibility

G2-01 does not retire duplicated semantic responsibility.

It reduces duplicated semantic responsibility operationally by making duplication explicit, replay-visible, and comparable.

The batch converts opaque duplicate interpretation into auditable parity evidence for:

- CSA versus ACLI local workflow classification;
- CSA versus ACLI proposal-only marker detection;
- CSA versus HIRR intake markers;
- CSA versus HIRR continuity markers;
- CSA versus execution-intent detectors;
- CSA versus worker/domain lifecycle entry detectors;
- CSA versus native development classifiers;
- CSA versus Product 1/domain/provider/similarity route markers;
- CSA deterministic failure versus provider-assisted intent classification;
- structured replay/CSA fields versus hardening and replay-derived token scans.

This is the greatest immediate reduction available because it prepares all remaining duplicate semantic owners for measured migration instead of migrating one isolated route family without common evidence.

## 8. Certification Risk

G2-01 has the lowest certification risk among the remaining implementation batches.

Risk is low relative to later batches because:

- no selected workflow should change;
- no compatibility path is retired;
- no CSA branch becomes newly authoritative;
- no approval, PPP, provider, worker, OCS, governance, replay, or execution authority changes;
- evidence additions are observable and testable;
- rollback is simply ignoring the comparison evidence and retaining existing compatibility decisions.

Residual risk:

- evidence shape could drift across consumers if not centralized or consistently documented;
- replay payload growth could affect assertions that compare exact artifacts;
- consumers with partial CSA availability need explicit `CSA_UNAVAILABLE` or equivalent fallback evidence;
- tests must prove non-interference, not only field presence.

## 9. Affected Components

Expected affected components for the implementation batch:

- ACLI conversational routing;
- routing replay capture;
- canonical semantic artifact integration points;
- proposal-only OCS detection evidence;
- HIRR intake evidence;
- HIRR continuity evidence;
- human execution intent detection evidence;
- native development intent and context evidence;
- Product 1/domain/provider/similarity route evidence;
- provider-assisted intent classification evidence;
- replay/hardening/replay-derived evidence consumers, where comparison source fields are surfaced.

Components that must not change authority:

- approval;
- resume;
- lifecycle exact command parsing;
- PPP structured validation;
- provider selection and credentials;
- worker dispatch, invocation, execution, and result validation;
- OCS cognition authority;
- replay read-only reconstruction;
- governance authority.

## 10. Expected Runtime Changes

Expected future runtime changes for G2-01:

1. Add a common replay comparison evidence shape for semantic consumers.
2. Record CSA/UBTR availability, reference, hash, and semantic summary where available.
3. Record previous compatibility source, classifier name, decision, confidence, matched terms, and fallback reason where available.
4. Record parity status as one of:

```text
CSA_COMPATIBILITY_AGREEMENT
CSA_COMPATIBILITY_DIVERGENCE
CSA_UNAVAILABLE
CSA_UNSUPPORTED_FOR_CONSUMER
COMPATIBILITY_FALLBACK_SELECTED
COMPARISON_ONLY_NO_BEHAVIOR_CHANGE
```

5. Attach evidence to replay without changing selected workflow or lifecycle outcome.
6. Preserve existing output shapes except for additive replay-visible evidence fields.
7. Preserve all compatibility fallbacks as authoritative for this batch.

No runtime changes are implemented by this selection artifact.

## 11. Replay Impact

Expected replay impact:

- replay records the semantic comparison source for every covered natural-language consumer;
- CSA reference and hash are recorded when available;
- previous compatibility interpretation is recorded when available;
- divergence and fallback reasons are explicit;
- migration batch id identifies comparison-only evidence;
- replay reconstruction can distinguish selected route from observed CSA candidate;
- historical replay is not reinterpreted.

Required replay fields:

- `semantic_comparison_source`;
- `canonical_semantic_artifact_reference`;
- `canonical_semantic_artifact_hash`;
- `canonical_semantic_candidate`;
- `previous_compatibility_source`;
- `previous_compatibility_interpretation`;
- `semantic_parity_status`;
- `semantic_divergence_reason`;
- `compatibility_fallback_reason`;
- `migration_batch_id`;
- `authority_preservation_flags`.

## 12. Regression Requirements

Required regression coverage:

- selected workflow is unchanged for every covered prompt;
- compatibility fallback remains authoritative;
- CSA agreement is recorded where present;
- CSA divergence is recorded without changing behavior;
- CSA unavailable is recorded without failure unless the existing path would fail;
- replay evidence includes previous compatibility source;
- authority flags remain false for approval, execution, worker, provider, governance, and replay mutation;
- existing Batch 01 and Batch 02 CSA-primary paths remain certified;
- full suite remains green.

Targeted test groups expected for implementation:

- ACLI routing tests;
- UBTR runtime integration tests;
- HIRR intake and HIRR integration tests;
- proposal-only OCS tests;
- execution-intent detection tests;
- native development routing tests;
- Product 1/domain/provider/specialized route tests where present;
- replay visibility tests.

Expected validation:

```text
git diff --check
py_compile
targeted replay and routing tests
targeted UBTR/HIRR integration tests
python -m pytest -q
```

## 13. Rollback Strategy

Rollback strategy:

- ignore or disable comparison evidence emission;
- keep compatibility classifiers authoritative;
- preserve existing CSA-primary Batch 01 and Batch 02 certified behavior unless the batch specifically touches their evidence plumbing;
- do not delete CSA artifacts already written to replay;
- do not reinterpret historical replay;
- restore prior replay payload shape only if additive evidence fields cause compatibility issues.

Rollback does not require route re-selection because G2-01 must not change selected runtime decisions.

## 14. Certification Criteria

G2-01 can be certified when:

1. every covered semantic consumer records comparison evidence;
2. selected workflow and lifecycle outcomes remain unchanged;
3. previous compatibility interpretation remains visible;
4. CSA reference/hash is recorded when available;
5. divergence and fallback reasons are explicit;
6. no authority boundary changes;
7. compatibility fallback remains authoritative;
8. Batch 01 and Batch 02 behavior remains green;
9. targeted tests and full pytest pass;
10. documentation records remaining gaps and next eligible batches.

## 15. Next Eligible Batches After Certification

After G2-01 certification, the next eligible primary-migration batches are:

1. G2-02 Proposal-Only OCS Routing.
2. G2-03 HIRR Remaining Intake Families.

G2-02 should be preferred if proposal-only parity evidence is decisive because it is medium complexity and narrows a high-visibility duplicate ACLI/OCS semantic path.

G2-03 should follow when HIRR family parity evidence is sufficiently complete.

## 16. Selection Conclusion

Selected next implementation batch:

```text
Batch G2-01: Replay Comparison Substrate
```

This batch has all dependencies satisfied, provides the broadest reduction in hidden duplicated semantic responsibility, preserves Generation 1 behavior, and carries the lowest certification risk among remaining closure-program batches.

Final verdict:

PLATFORM_SEMANTIC_GAP_CLOSURE_BATCH_SELECTED
