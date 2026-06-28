# Platform Semantic Gap Closure G2-13 Provider-Assisted And Legacy Classifier Closure V1

Status: implementation certification artifact.

Scope: provider-assisted and legacy semantic classifier closure where deterministic parity
or CSA-gated advisory fallback is certified.

This batch does not retire all compatibility layers. Final compatibility retirement remains
G2-14.

## 1. Background

Platform Core Generation 1 is certified.

Completed Generation 2 migration work:

- UBTR Phase 1 through Phase 5.
- Consumer Migration Batch 01 through Batch 02.
- G2-01 Replay Comparison Substrate.
- G2-02 Proposal-Only OCS Routing.
- G2-03 Remaining HIRR Intake Families.
- G2-04 HIRR Clarification Continuity.
- G2-05 Execution Intent And Authorization Entry Semantics.
- G2-06 Worker And Domain Lifecycle Entry Semantics.
- G2-07 Native Development Semantics.
- G2-08 Specialized Product, Domain, Provider, And Similarity Routes.
- G2-09 OCS Semantic Lineage And PPP Annotation.
- G2-10 Command Boundary And Recommendation Prose Certification.
- G2-11 Explanation Rendering Migration.
- G2-12 Replay, Hardening, And Replay-Derived Classifiers.

The approved dependency graph selected:

```text
G2-13 Provider-Assisted And Legacy Classifier Closure
```

## 2. Objective

G2-13 closes provider-assisted and legacy semantic classifiers as hidden primary semantic
authority risks.

The implementation records CSA references, compatibility interpretation, semantic
comparison artifacts, parity evidence, migration batch id, replay lineage, and fallback
status while preserving compatibility fallback until G2-14.

## 3. Runtime Changes

Implemented runtime surfaces:

- `aigol/runtime/intent_classifier.py`
- `aigol/runtime/provider_assisted_intent_classification.py`

The legacy intent classifier now records:

- legacy classifier status;
- provider-assisted classifier status as not applicable;
- CSA reference and hash when supplied;
- previous compatibility interpretation;
- semantic comparison artifact and hash;
- semantic parity evidence;
- G2-13 migration batch id;
- fallback status;
- replay lineage.

The provider-assisted classifier now records:

- provider-assisted classifier status;
- legacy deterministic classifier status;
- CSA reference and hash when supplied;
- deterministic failure or deterministic success status;
- provider suggestion advisory status;
- previous compatibility interpretation;
- semantic comparison artifact and hash;
- semantic parity evidence;
- G2-13 migration batch id;
- fallback status;
- replay lineage.

## 4. Provider-Assisted Classifiers Closed

Provider-assisted classification remains available only as an advisory fallback.

Certified statuses:

| Status | Meaning |
| --- | --- |
| `PROVIDER_ASSISTED_CLASSIFIER_ISOLATED_NOT_REQUIRED` | Deterministic or CSA-compatible classification completed before provider use; provider assistance is not invoked. |
| `PROVIDER_ASSISTED_CLASSIFIER_CSA_GATED_ADVISORY_ONLY` | Deterministic failure and CSA lineage are recorded before provider suggestion; provider output remains advisory only. |
| `PROVIDER_ASSISTED_CLASSIFIER_COMPATIBILITY_FALLBACK_ACTIVE` | CSA lineage is unavailable; provider-assisted compatibility fallback remains visible and non-authoritative. |

Provider suggestions do not authorize routing, approval, provider ownership, worker
ownership, execution, governance mutation, or replay mutation.

## 5. Legacy Classifiers Closed

Legacy deterministic intent classification remains visible until final compatibility
retirement.

Certified statuses:

| Status | Meaning |
| --- | --- |
| `CSA_PARITY_MIGRATED_LEGACY_COMPATIBILITY_VISIBLE` | CSA destination matches the legacy classifier destination; legacy output is recorded as compatibility evidence. |
| `LEGACY_COMPATIBILITY_FALLBACK_ACTIVE` | CSA lineage exists but does not match the compatibility classifier; legacy fallback remains authoritative for that path. |
| `LEGACY_COMPATIBILITY_ONLY_CSA_UNAVAILABLE` | CSA lineage is unavailable; legacy compatibility remains active and replay-visible. |

Legacy classifiers cannot silently override CSA authority after G2-13 because replay now
records semantic source, parity status, fallback status, and compatibility interpretation.

## 6. Replay Evidence

G2-13 replay-visible evidence includes:

- `canonical_semantic_artifact_reference`;
- `canonical_semantic_artifact_hash`;
- `provider_assisted_classifier_status`;
- `legacy_classifier_status`;
- `previous_compatibility_interpretation`;
- `semantic_comparison_artifact`;
- `semantic_comparison_hash`;
- `semantic_comparison_parity_status`;
- `semantic_parity_evidence`;
- `migration_batch_id`;
- `replay_lineage`;
- `fallback_status`.

The comparison artifacts are hash-bound and explicitly non-authoritative.

## 7. Compatibility And Rollback

Compatibility fallback remains active.

Rollback impact is low to medium:

- omit CSA lineage to keep legacy and provider-assisted compatibility fallbacks active;
- deterministic legacy classification remains replay-visible;
- provider-assisted classification remains advisory-only after deterministic failure;
- historical replay is not rewritten or reinterpreted;
- no authority surface changes are required for rollback.

## 8. Certification Impact

G2-13 certification proves:

- provider-assisted classification cannot run as primary semantic authority;
- deterministic failure or CSA lineage is recorded before provider suggestion;
- provider output remains advisory-only;
- legacy classifier outputs carry explicit compatibility status;
- compatibility interpretation remains visible until G2-14;
- governance, replay, OCS, PPP, provider, worker, approval, and execution authority remain
  unchanged.

This batch is the final prerequisite for G2-14 Compatibility Retirement Certification.

## 9. Updated Remaining Generation 2 Inventory

Remaining implementation inventory:

```text
G2-14 Compatibility Retirement Certification
```

Generation 2 completion is now blocked only on final compatibility retirement
certification.

## 10. Validation Scope

Required validation:

```text
git diff --check
python -m py_compile ...
targeted provider-assisted/legacy tests
targeted UBTR integration tests
full pytest
```

Generated replay artifacts from validation must be cleaned before completion.

## 11. Final Verdict

```text
PLATFORM_SEMANTIC_GAP_CLOSURE_G2_13_READY
```
