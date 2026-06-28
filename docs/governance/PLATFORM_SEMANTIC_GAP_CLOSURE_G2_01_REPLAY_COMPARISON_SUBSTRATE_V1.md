# Platform Semantic Gap Closure G2-01 Replay Comparison Substrate V1

Status: implementation certification artifact.

Scope: Batch G2-01 replay-visible semantic comparison substrate.

This artifact documents runtime changes, replay evidence, non-authority boundaries, rollback, and certification impact for the first Platform Semantic Gap Closure implementation batch.

## 1. Objective

Implement a deterministic replay-visible comparison substrate that records semantic equivalence between:

- compatibility-layer interpretation;
- Canonical Semantic Artifact interpretation.

The substrate is observational only.

It does not influence routing, governance, approval, provider selection, execution, workers, lifecycle, OCS authority, PPP, or replay mutation.

## 2. Implemented Scope

Batch G2-01 adds comparison evidence at the central ACLI conversational routing point where both semantic sources already coexist:

```text
Human prompt
  -> UBTR Human -> Governance translation
  -> Canonical Semantic Artifact
  -> local compatibility route evidence
  -> semantic replay comparison artifact
  -> existing certified routing decision
```

Routing behavior remains unchanged:

- certified Batch 01 CSA-primary ACLI routes remain CSA-primary;
- certified Batch 02 CSA-primary HIRR intake routes remain CSA-primary;
- all non-certified routes remain compatibility fallback;
- compatibility routing remains authoritative wherever CSA migration is not certified.

## 3. Runtime Change Summary

Runtime changes:

- added `SEMANTIC_REPLAY_COMPARISON_ARTIFACT_V1`;
- added deterministic comparison generation in `route_conversational_cli_intent(...)`;
- added CSA semantic interpretation projection;
- added compatibility semantic interpretation projection;
- added deterministic semantic difference detection;
- added parity status and equivalence result;
- embedded the comparison artifact and comparison hash in routing decision, selection, returned, capture, and replay reconstruction outputs;
- added reconstruction-time hash verification for the embedded comparison artifact.

The comparison artifact is additive replay evidence.

It is not used as input to workflow selection.

## 4. Comparison Model

The comparison model records:

| Field | Meaning |
| --- | --- |
| `compatibility_semantic_interpretation` | Local compatibility classifier interpretation. |
| `csa_semantic_interpretation` | CSA-derived semantic projection. |
| `semantic_equivalence_result` | `EQUIVALENT`, `NOT_EQUIVALENT`, or `NOT_EVALUATED`. |
| `semantic_differences` | Deterministic field-level differences. |
| `confidence_comparison` | CSA confidence, compatibility confidence, and equivalence flag. |
| `migration_batch_id` | `PLATFORM_SEMANTIC_GAP_CLOSURE_G2_01_REPLAY_COMPARISON_SUBSTRATE_V1`. |
| `replay_lineage` | Routing replay reference, chain id, prompt id, and comparison source. |
| `parity_status` | CSA/compatibility comparison status. |
| `artifact_hash` | Hash over the complete comparison artifact. |

Parity statuses:

- `CSA_COMPATIBILITY_EQUIVALENT`;
- `CSA_COMPATIBILITY_DIVERGENT`;
- `CSA_UNAVAILABLE`;
- `COMPATIBILITY_UNAVAILABLE`.

## 5. Replay Artifacts Added

The following replay-visible fields are now embedded in existing routing replay artifacts:

- `semantic_comparison_artifact`;
- `semantic_comparison_hash`;
- `semantic_equivalence_result`;
- `semantic_comparison_parity_status`;
- `semantic_comparison_non_authoritative`.

These fields appear in:

- conversational routing decision artifact;
- conversational workflow selection artifact;
- conversational routing returned artifact;
- runtime capture;
- replay reconstruction output.

The replay artifact count is unchanged.

The comparison artifact is hash-bound inside the existing hashed routing artifacts.

## 6. Non-Authority Guarantees

The comparison artifact records:

- `non_authoritative: true`;
- `routing_influence: false`;
- `governance_influence: false`;
- `approval_influence: false`;
- `provider_selection_influence: false`;
- `execution_influence: false`;
- `worker_influence: false`;
- `lifecycle_influence: false`.

The implementation does not grant:

- approval authority;
- execution authority;
- provider authority;
- worker authority;
- OCS authority;
- PPP authority;
- governance mutation authority;
- replay mutation authority.

## 7. Regression Coverage

Regression tests cover:

- certified Batch 01 CSA-primary route records equivalent CSA/compatibility comparison;
- certified Batch 02 HIRR CSA-primary route records equivalent CSA/compatibility comparison;
- non-certified compatibility fallback route records divergent comparison while preserving the selected compatibility workflow;
- reconstruction verifies the embedded comparison hash.

## 8. Rollback Strategy

Rollback can disable or ignore comparison evidence emission while retaining existing routing behavior.

Rollback does not require route re-selection because G2-01 does not change selected workflow outcomes.

Rollback must preserve:

- existing compatibility routing;
- certified Batch 01 behavior;
- certified Batch 02 behavior;
- historical replay read-only semantics;
- authority boundary flags.

## 9. Certification Impact

Batch G2-01 does not certify new CSA-primary routing.

It certifies the evidence substrate required for later migrations.

Certification impact:

- duplicate semantic responsibility becomes replay-visible;
- CSA/compatibility agreement and divergence become deterministic evidence;
- later batches can use recorded comparison evidence to justify narrow CSA-primary migration;
- Platform Core remains "UBTR canonical with active compatibility layers."

Final certification statement:

```text
G2-01 adds non-authoritative semantic comparison replay evidence without changing Generation 1 behavior.
```

## 10. Final Verdict

PLATFORM_SEMANTIC_GAP_CLOSURE_G2_01_READY
