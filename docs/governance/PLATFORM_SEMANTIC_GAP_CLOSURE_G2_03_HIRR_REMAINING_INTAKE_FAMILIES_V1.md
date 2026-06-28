# Platform Semantic Gap Closure G2-03 HIRR Remaining Intake Families V1

Status: implementation certification artifact.

Scope: Batch G2-03 HIRR remaining intake family migration.

This artifact documents the third Platform Semantic Gap Closure implementation batch after G2-01 Replay Comparison Substrate and G2-02 Proposal-Only OCS Routing.

## 1. Selected Batch

Selected batch from the approved dependency graph:

```text
Batch G2-03: HIRR Remaining Intake Families
```

The migrated consumer is:

```text
HIRR clarification-first intake family classification
```

## 2. Objective

Make CSA primary for HIRR remaining intake families where deterministic compatibility parity is proven.

HIRR continues to own:

- clarification lifecycle;
- HIRR artifact shape;
- clarification questions;
- expected workflow targets;
- one-active-clarification invariant;
- reply binding;
- downstream lifecycle orchestration.

UBTR/CSA owns the semantic family source only for migrated parity-proven intake families.

## 3. Migrated Decisions

G2-03 migrates these HIRR intake families:

- `BUSINESS_GOAL_INTENT`;
- `PROBLEM_STATEMENT_INTENT`;
- `AUTOMATION_INTENT`;
- `COMPLIANCE_INTENT`;
- `GENERAL_IMPROVEMENT_INTENT`;
- `CONTINUATION_INTENT`;
- `BOUNDED_FILE_WRITE_PROOF_INTENT`.

Batch 02 remains responsible for:

- `AMBIGUOUS_INTENT` clarification intake.

## 4. Migration Rule

CSA becomes primary only when all conditions are true:

1. CSA workflow id is `HUMAN_INTENT_CLARIFICATION_INTAKE`.
2. CSA intent family is one of the G2-03 remaining HIRR families.
3. CSA domain is `UNKNOWN_DOMAIN`.
4. CSA requested actions are empty.
5. CSA clarification required is true.
6. CSA ambiguity status is `MATERIAL_AMBIGUITY`.
7. CSA confidence matches previous HIRR compatibility confidence.
8. Previous HIRR compatibility intake selected the same intent family.
9. Previous HIRR compatibility intake selected the same HIRR workflow.
10. Previous HIRR compatibility intake required clarification.

If any condition fails, compatibility remains authoritative.

## 5. Runtime Change Summary

Runtime changes:

- Human -> Governance translation now emits canonical HIRR intake family semantics for the G2-03 family set.
- HIRR CSA consumption now accepts G2-03 families only when CSA and compatibility family parity is exact.
- HIRR parity evidence now records the migration batch id and parity scope.
- ACLI routing continues to invoke HIRR CSA consumption through the existing Batch 02 handoff path.
- G2-01 replay comparison evidence continues to be emitted and hash-bound for migrated decisions.

The implementation does not modify:

- clarification lifecycle rules;
- clarification questions;
- workflow target selection after clarification;
- provider selection;
- worker invocation;
- approval;
- execution authorization;
- PPP;
- governance authority;
- replay mutation semantics.

## 6. Replay Comparison Evidence

For migrated G2-03 decisions, replay records:

- CSA semantic interpretation;
- compatibility semantic interpretation;
- semantic equivalence result;
- confidence comparison;
- parity status;
- semantic comparison hash;
- CSA reference and hash;
- previous compatibility interpretation;
- semantic parity evidence;
- parity hash;
- migration batch id.

Expected G2-03 replay identifiers:

```text
semantic_routing_source: CANONICAL_SEMANTIC_ARTIFACT
migration_batch_id: PLATFORM_SEMANTIC_GAP_CLOSURE_G2_03_HIRR_REMAINING_INTAKE_FAMILIES_V1
parity_scope: HIRR_REMAINING_INTAKE_FAMILY
```

## 7. Regression Coverage

Regression tests cover:

- Business-goal intake migration.
- Problem-statement intake migration.
- Automation intake migration.
- Compliance intake migration.
- Continuation intake migration.
- Batch 02 ambiguous-intent behavior remains unchanged.
- CSA/compatibility comparison remains equivalent for migrated intake.
- Previous compatibility interpretation remains visible.
- Provider, worker, approval, execution, governance, and replay mutation flags remain false.

Translation tests cover CSA source semantics for the migrated family set before HIRR consumes it.

## 8. Rollback Strategy

Rollback can disable the G2-03 CSA-family predicate and retain HIRR local compatibility family markers as authoritative.

Rollback preserves:

- CSA artifacts as replay evidence;
- G2-01 comparison evidence;
- previous compatibility interpretation;
- Batch 02 ambiguous-intent migration;
- HIRR clarification lifecycle;
- historical replay read-only semantics.

No compatibility family is retired by this batch.

## 9. Certification Impact

G2-03 certifies CSA-primary HIRR intake semantics for the remaining deterministic family set.

Certification impact:

- HIRR local marker families are now compatibility fallback for the migrated G2-03 intake families;
- HIRR remains the owner of clarification lifecycle;
- UBTR/CSA becomes the semantic source for parity-proven HIRR intake family identity;
- Platform Core still remains "UBTR canonical with active compatibility layers" until later batches and retirement certification complete.

## 10. Remaining Migration Inventory

Remaining after G2-03:

1. HIRR clarification continuity and reply refinement.
2. Execution intent and authorization entry semantics.
3. Worker and domain lifecycle entry semantics.
4. Native development semantics.
5. Specialized Product, domain, provider, and similarity routes.
6. OCS semantic lineage and PPP annotation.
7. Command boundary and recommendation prose certification.
8. Explanation rendering migration.
9. Replay, hardening, and replay-derived classifiers.
10. Provider-assisted and legacy classifier closure.
11. Compatibility retirement certification.

## 11. Final Verdict

PLATFORM_SEMANTIC_GAP_CLOSURE_G2_03_READY
