# UBTR Consumer Migration Batch 02 HIRR V1

## Status

Implemented.

Final verdict:

UBTR_CONSUMER_MIGRATION_BATCH_02_READY

## Objective

Perform the second certified UBTR consumer migration for HIRR, the Human Intent Resolution Runtime.

This batch moves a narrow HIRR intake decision to Canonical Semantic Artifact consumption where deterministic parity with the existing HIRR compatibility classifier is proven.

## Scope

Migrated HIRR decisions:

1. Ambiguous human-intent clarification intake where the CSA records:
   - workflow candidate `HUMAN_INTENT_CLARIFICATION_INTAKE`;
   - semantic intent family `CLARIFICATION_REQUIRED`;
   - domain `UNKNOWN_DOMAIN`;
   - no requested action;
   - `MATERIAL_AMBIGUITY`;
   - low semantic confidence;
   - clarification required.
2. The previous HIRR compatibility interpretation must simultaneously resolve to:
   - `HUMAN_INTENT_CLARIFICATION_INTAKE`;
   - `AMBIGUOUS_INTENT`;
   - low confidence;
   - clarification required;
   - `HUMAN_INTENT_CLARIFICATION_REQUIRED`.

Not migrated:

- business-goal HIRR family classification;
- problem-statement HIRR family classification;
- automation HIRR family classification;
- compliance HIRR family classification;
- general-improvement HIRR family classification;
- continuation HIRR family classification;
- bounded file-write proof HIRR family classification;
- development-intent HIRR routing;
- HIRR clarification continuity and refinement;
- multilingual HIRR parity beyond existing compatibility fallback;
- broad ACLI workflow classification.

## Runtime Changes

Updated:

`aigol/runtime/human_intent_clarification_intake_runtime.py`

Changes:

- added `classify_human_intent_for_clarification_from_canonical_semantic_artifact(...)`;
- consumes CSA fields for HIRR only when CSA and compatibility HIRR intake satisfy the Batch 02 parity gate;
- emits HIRR-compatible intake artifacts preserving the existing artifact shape and clarification-first behavior;
- records semantic source, migration batch id, previous compatibility interpretation, and parity evidence;
- preserves provider, worker, approval, execution, governance, and replay non-authority flags.

Updated:

`aigol/runtime/conversational_cli_runtime.py`

Changes:

- invokes the CSA-to-HIRR parity gate after Batch 01 CSA routing and before compatibility fallback;
- preserves compatibility fallback whenever CSA/HIRR parity is absent;
- records Batch 02 fields in routing decision, workflow selection, returned artifact, capture, and replay reconstruction.

## Replay Evidence

For migrated HIRR route decisions, ACLI now records:

- `semantic_routing_source`;
- `canonical_semantic_artifact_reference`;
- `canonical_semantic_artifact_hash`;
- `migration_batch_id`;
- `previous_routing_source`;
- `previous_compatibility_workflow_id`;
- `previous_compatibility_routing_status`;
- `previous_compatibility_confidence`;
- `previous_compatibility_matched_terms`;
- `previous_compatibility_interpretation`;
- `semantic_parity_evidence`;
- `new_csa_routing_source`;
- UBTR semantic cognition lineage.

The parity evidence records:

- CSA workflow id;
- CSA intent family;
- CSA ambiguity status;
- CSA clarification-required state;
- CSA semantic confidence;
- compatibility workflow id;
- compatibility intent family;
- compatibility clarification-required state;
- compatibility confidence;
- no-provider, no-worker, no-authorization, no-execution, and no-approval-bypass assertions;
- parity hash.

## Previous Compatibility Source

Previous source:

`LOCAL_HIRR_COMPATIBILITY_MARKERS`

The previous compatibility interpretation remains replay-visible and is used as the parity gate before CSA becomes primary.

If compatibility does not resolve to the same HIRR ambiguous-intent clarification behavior, CSA does not become primary and the route remains compatibility fallback.

## New CSA Source

New source:

`CANONICAL_SEMANTIC_ARTIFACT`

CSA becomes primary only for the migrated ambiguous HIRR intake case.

CSA does not:

- approve;
- authorize execution;
- invoke providers;
- invoke workers;
- mutate governance;
- mutate replay;
- replace clarification continuity;
- replace HIRR family classifiers without parity.

## Compatibility Fallback

Compatibility fallback remains active for all HIRR paths outside this batch.

Rollback options:

- disable the CSA-to-HIRR branch;
- continue using `classify_human_intent_for_clarification(...)`;
- preserve CSA/UBTR replay artifacts as non-authoritative evidence;
- preserve previous compatibility interpretation fields for audit.

No replay schema migration is required for rollback.

## Governance Impact

No governance authority changed.

HIRR remains clarification-first. UBTR/CSA supplies semantic evidence only for parity-proven intake.

## Approval Impact

No approval boundary changed.

Clarification intake does not grant approval or bypass downstream approval requirements.

## OCS Impact

No OCS authority changed.

OCS remains responsible for cognition and provider necessity where a later route invokes OCS. This batch does not move OCS cognition routing.

## Provider Impact

No provider boundary changed.

CSA-to-HIRR intake does not invoke providers.

## Worker Impact

No worker boundary changed.

CSA-to-HIRR intake does not invoke workers or dispatch execution.

## Regression Coverage

Updated:

`tests/test_universal_translation_runtime_integration_v1.py`

Coverage verifies:

- ambiguous HIRR intake routes through CSA when CSA and compatibility parity are proven;
- Batch 02 migration id is recorded;
- previous compatibility HIRR interpretation is recorded;
- semantic parity evidence is recorded and hash-bound;
- replay reconstruction preserves Batch 02 evidence;
- non-parity HIRR prompts retain compatibility fallback;
- providers are not invoked;
- workers are not invoked;
- execution is not requested.

Existing HIRR and ACLI routing tests remain compatible with Generation 1 behavior.

## Remaining HIRR Migration Work

Remaining HIRR migration work:

1. business-goal intent family parity;
2. problem-statement intent family parity;
3. automation intent family parity;
4. compliance intent family parity;
5. general-improvement intent family parity;
6. continuation intent parity;
7. bounded file-write proof intent parity;
8. development-intent HIRR parity outside Batch 01 ACLI routing;
9. clarification continuity and refinement through linked CSA artifacts;
10. compatibility fallback retirement certification.

## Certification Impact

Batch 02 certifies the first HIRR CSA-primary intake subset.

Certification language must remain bounded:

- HIRR is partially migrated to CSA;
- CSA is primary only for the migrated ambiguous-intent parity subset;
- active HIRR compatibility classifiers remain required;
- partial conformance remains visible.

## Final Verdict

UBTR_CONSUMER_MIGRATION_BATCH_02_READY
