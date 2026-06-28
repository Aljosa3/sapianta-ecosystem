# Platform Semantic Gap Closure G2-12 Replay Hardening And Replay-Derived Classifiers V1

Status: implementation certification artifact.

Scope: CSA-primary semantic provenance for replay-derived and hardening classifiers where
deterministic parity is proven.

This batch does not modify governance authority, OCS authority, PPP authority, approval
authority, provider ownership, worker ownership, execution authorization, replay authority,
or compatibility fallback.

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

The approved dependency graph selected:

```text
G2-12 Replay, Hardening, And Replay-Derived Classifiers
```

## 2. Objective

G2-12 migrates replay-derived semantic classifier evidence to consume CSA semantic
lineage where parity is proven, while preserving compatibility classification and
historical replay interpretation.

The migration is evidence-first and classifier-scoped. It does not authorize routing,
approval, provider selection, worker dispatch, execution, governance mutation, or replay
mutation.

## 3. Runtime Changes

Implemented runtime surfaces:

- `aigol/runtime/acli_hardening_runtime.py`
- `aigol/runtime/replay_gap_detection_runtime.py`
- `aigol/runtime/replay_to_improvement_intent_runtime.py`

The ACLI hardening runtime now accepts optional canonical semantic lineage and records:

- replay-derived classifier source;
- previous compatibility hardening classifier interpretation;
- canonical semantic classifier interpretation;
- CSA reference and hash;
- semantic comparison artifact and hash;
- semantic parity evidence;
- G2-12 migration batch id;
- fallback status;
- replay lineage.

The replay gap detection runtime now records structured semantic classifier provenance
for replay-derived gap classifications:

- CSA references and hashes from evidence items;
- previous compatibility classifier interpretation;
- canonical semantic classifier interpretation;
- semantic comparison artifact and hash;
- parity status;
- fallback status;
- replay lineage.

The replay-to-improvement-intent runtime now preserves upstream G2-12 classifier lineage
inside improvement intent evidence, classification, and returned capture summaries.

## 4. Migrated Classifiers

Migrated replay-derived classifiers:

| Classifier | CSA-Primary Scope | Compatibility Fallback |
| --- | --- | --- |
| ACLI hardening scenario classifier | CSA lineage can select hardening scenario identifiers when parity with compatibility output is proven | Existing token-scan hardening classifier remains authoritative when CSA lineage is absent or divergent |
| Replay gap classifier | CSA lineage is recorded as the classifier source for structured replay evidence that carries CSA hash-bound lineage | Existing deterministic replay evidence type and threshold rules remain authoritative when CSA lineage is absent |
| Replay-to-improvement intent classifier lineage | Preserves upstream CSA classifier source and comparison hash | Existing replay gap classification remains required before any improvement intent can be created |

Hardening and replay-derived improvement outputs remain non-authoritative and proposal-only.

## 5. Replay Evidence

G2-12 replay-visible evidence includes:

- `canonical_semantic_artifact_reference`;
- `canonical_semantic_artifact_hash`;
- `replay_derived_classifier_source`;
- `previous_compatibility_classifier_interpretation`;
- `canonical_semantic_classifier_interpretation`;
- `semantic_comparison_artifact`;
- `semantic_comparison_hash`;
- `semantic_comparison_parity_status`;
- `semantic_parity_evidence`;
- `migration_batch_id`;
- `fallback_status`;
- `replay_lineage`.

The semantic comparison artifacts are hash-bound and non-authoritative. They explicitly
record that historical replay is not reinterpreted.

## 6. Compatibility And Rollback

Compatibility fallback remains active and observable.

Rollback impact is low to medium:

- remove or omit CSA lineage inputs to return classifiers to compatibility source;
- existing compatibility token-scan hardening classification remains present;
- replay gap detection still uses deterministic evidence type and threshold rules;
- historical replay artifacts are not rewritten or reinterpreted;
- no authority surface changes are required for rollback.

## 7. Certification Impact

G2-12 certification proves:

- replay-derived classifiers can record CSA semantic lineage where available;
- compatibility interpretations remain replay-visible;
- parity evidence is hash-bound and deterministic;
- fallback status is explicit for non-parity or missing-CSA cases;
- replay-derived outputs remain non-authoritative;
- governance, OCS, PPP, provider, worker, approval, execution, and replay authorities are preserved.

This batch is required before G2-13 Provider-Assisted And Legacy Classifier Closure and
G2-14 Compatibility Retirement Certification.

## 8. Updated Remaining Generation 2 Inventory

Remaining implementation inventory:

```text
G2-13 Provider-Assisted And Legacy Classifier Closure
G2-14 Compatibility Retirement Certification
```

G2-13 can now consume G2-12 classifier source provenance to classify legacy and
provider-assisted paths as CSA-parity migrated, advisory-only, compatibility-only, or
unsupported.

G2-14 remains blocked until G2-13 is complete.

## 9. Validation Scope

Required validation:

```text
git diff --check
python -m py_compile ...
targeted replay/hardening classifier tests
targeted UBTR integration tests
full pytest
```

Generated replay artifacts from validation must be cleaned before completion.

## 10. Final Verdict

```text
PLATFORM_SEMANTIC_GAP_CLOSURE_G2_12_READY
```
