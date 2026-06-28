# Platform Semantic Gap Closure G2-02 Proposal-Only OCS Routing V1

Status: implementation certification artifact.

Scope: Batch G2-02 proposal-only OCS consumer migration.

This artifact documents the second Platform Semantic Gap Closure implementation batch after G2-01 Replay Comparison Substrate.

## 1. Objective

Migrate the next highest-priority consumer from the approved dependency graph:

```text
Batch G2-02: Proposal-Only OCS Routing
```

The migrated decision is narrow:

- proposal-only OCS routing;
- no execution requested;
- provider relevance required for cognition only;
- worker invocation not requested;
- compatibility marker route already selected the same OCS proposal-only behavior.

## 2. Migrated Consumer

Migrated consumer:

```text
ACLI proposal-only OCS routing
```

Affected runtime surfaces:

- Human -> Governance translation;
- Canonical Semantic Artifact generation;
- ACLI conversational route selection;
- routing decision replay;
- workflow selection replay;
- routing returned replay;
- replay reconstruction.

## 3. Migration Rule

CSA becomes primary only when all conditions are true:

1. CSA workflow id is `OCS_LLM_COGNITION`.
2. CSA intent family is `OCS_PROPOSAL_ONLY_INTENT`.
3. CSA requested action is `REVIEW`.
4. CSA execution requested is false.
5. CSA approval required is false.
6. CSA provider relevance is `PROVIDER_REQUIRED`.
7. CSA worker relevance is `NONE`.
8. Compatibility route selected `OCS_LLM_COGNITION`.
9. Compatibility route marked proposal-only cognition.
10. Compatibility provider selection remains `OCS_PROVIDER_REGISTRY_DETERMINISTIC_ORDER`.
11. CSA proposal-only reason matches the previous compatibility escalation reason.

If any condition fails, compatibility remains authoritative.

## 4. Runtime Change Summary

Runtime changes:

- Human -> Governance translation now emits canonical proposal-only OCS semantics for the certified prompt family.
- ACLI routing now consumes CSA for proposal-only OCS only when compatibility parity is deterministic.
- Previous compatibility proposal-only interpretation is recorded.
- Semantic parity evidence is recorded with a hash.
- Replay comparison evidence from G2-01 remains present and hash-bound.
- Provider, worker, approval, execution, governance, and replay mutation authority remain false.

The migration does not invoke OCS providers directly.

OCS still owns cognition and provider selection after the routing handoff.

## 5. Replay Comparison Evidence

The existing G2-01 comparison substrate records:

- CSA semantic interpretation;
- compatibility semantic interpretation;
- semantic equivalence result;
- semantic differences;
- confidence comparison;
- parity status;
- replay lineage.

For migrated G2-02 proposal-only OCS routes, replay also records:

- `semantic_routing_source: CANONICAL_SEMANTIC_ARTIFACT`;
- `migration_batch_id: PLATFORM_SEMANTIC_GAP_CLOSURE_G2_02_PROPOSAL_ONLY_OCS_ROUTING_V1`;
- previous compatibility workflow id;
- previous compatibility proposal-only escalation reason;
- previous compatibility provider-selection source;
- semantic parity evidence;
- parity hash.

## 6. Regression Coverage

Regression tests cover:

- English proposal-only governance document prompts;
- English explanation and analysis prompts;
- provider comparison prompts;
- Slovenian proposal-only governance document prompts;
- CSA primary routing source after parity;
- previous compatibility interpretation visibility;
- semantic comparison equivalence;
- no provider invocation;
- no worker invocation;
- no execution request.

Translation tests also cover:

- canonical proposal-only OCS CSA source fields;
- no execution authority;
- no approval requirement;
- provider relevance only;
- worker relevance `NONE`;
- ordinary governance artifact creation remains executable governed development, not proposal-only OCS.

## 7. Rollback Strategy

Rollback can disable the CSA proposal-only OCS branch and retain local compatibility marker routing.

Rollback preserves:

- previous compatibility route evidence;
- CSA artifacts as observational replay evidence;
- G2-01 comparison evidence;
- OCS provider ownership;
- no-worker/no-execution guarantees;
- historical replay read-only semantics.

No compatibility layer is retired by this batch.

## 8. Certification Impact

G2-02 certifies the first post-comparison-substrate consumer migration.

Certification impact:

- proposal-only OCS routing has a CSA-primary parity-proven subset;
- compatibility fallback remains active;
- replay proves CSA/compatibility equivalence;
- OCS cognition and provider authority remain unchanged;
- Platform Core still remains "UBTR canonical with active compatibility layers" until later batches and retirement certification complete.

## 9. Final Verdict

PLATFORM_SEMANTIC_GAP_CLOSURE_G2_02_READY
