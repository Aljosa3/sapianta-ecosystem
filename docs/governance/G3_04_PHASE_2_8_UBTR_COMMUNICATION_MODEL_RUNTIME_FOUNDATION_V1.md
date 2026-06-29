# G3-04 Phase 2.8 UBTR Communication Model Runtime Foundation V1

Status: runtime foundation implemented.

Final verdict: G3_04_PHASE_2_8_READY

## 1. Executive Summary

Platform Core Generation 2 is certified.

G3-04 Phase 2.7 defined the canonical Human Communication Model. This phase
implements the deterministic runtime foundation for that model inside UBTR /
Platform Core.

The implementation creates replay-visible, hash-bound, interface-neutral
communication artifacts. It does not invoke providers, execute workers, mutate
repositories, deploy, or perform interface-specific rendering.

## 2. Files Changed

Runtime:

- `aigol/runtime/ubtr_human_communication_model_runtime.py`

Tests:

- `tests/test_ubtr_human_communication_model_runtime_v1.py`

Documentation:

- `docs/governance/G3_04_PHASE_2_8_UBTR_COMMUNICATION_MODEL_RUNTIME_FOUNDATION_V1.md`

## 3. Communication Artifact Model

The runtime introduces:

- `UBTR_CANONICAL_HUMAN_COMMUNICATION_ARTIFACT_V1`
- `UBTR_CANONICAL_HUMAN_COMMUNICATION_MODEL_V1`
- `UBTR_HUMAN_COMMUNICATION_MODEL_RUNTIME_V1`

Every artifact records:

- communication id;
- source component;
- target human context;
- CSA reference/hash where supplied;
- OCS reference/hash where supplied;
- communication domain;
- communication level;
- rendered section keys;
- required human action;
- non-authority notices;
- replay lineage;
- rollback reference;
- artifact hash;
- immutable replay wrapper hash.

The artifact is explicitly non-authoritative. It grants no semantic,
governance, approval, authorization, execution, mutation, provider, worker, or
replay mutation authority.

## 4. Communication Domains Implemented

The runtime supports the canonical Phase 2.7 domains:

| Domain | Runtime value | Scope |
| --- | --- | --- |
| Understanding | `UNDERSTANDING` | Human request understanding, normalized intent, ambiguity, missing context, CSA lineage |
| Explanation | `EXPLANATION` | Platform evidence explanation and limitation visibility |
| Recommendation | `RECOMMENDATION` | Advisory-only options, alternatives, trade-offs, risks |
| Guidance | `GUIDANCE` | Safe next action, blocked actions, recovery path |
| Human Confirmation | `HUMAN_CONFIRMATION` | Confirmation semantics and supported response classes |
| Transparency | `TRANSPARENCY` | Assumptions, risks, uncertainties, provenance, evidence quality |
| Conversation | `CONVERSATION` | Session, turn, parent turn, continuation, CSA continuity |

## 5. Communication Levels Implemented

The runtime supports the canonical Phase 2.7 levels:

| Level | Runtime value |
| --- | --- |
| Concise | `CONCISE` |
| Standard | `STANDARD` |
| Detailed | `DETAILED` |
| Beginner | `BEGINNER` |
| Technical | `TECHNICAL` |
| Auditor | `AUDITOR` |
| Executive | `EXECUTIVE` |

Level selection is replay-visible and hash-bound. Levels do not grant adapters
permission to reinterpret communication meaning.

## 6. Section Model

The runtime accepts deterministic section payloads for:

- understanding;
- explanation;
- recommendation;
- guidance;
- confirmation;
- transparency;
- conversation continuation.

At least one section is required. Section contents are preserved as source
meaning, hashed through the artifact, and exposed through the `sections` and
`sections_rendered` fields.

## 7. Replay Evidence

Replay evidence is recorded as a single immutable wrapper:

- replay index: `0`;
- replay step: `ubtr_human_communication_artifact_recorded`;
- event type: `UBTR_HUMAN_COMMUNICATION_MODEL_RUNTIME_V1`;
- artifact hash;
- wrapper replay hash.

Replay reconstruction verifies:

- wrapper ordering;
- wrapper hash;
- artifact type;
- schema version;
- domain and level validity;
- section consistency;
- replay lineage;
- non-authority notices;
- authority denial;
- artifact hash.

Tampering fails closed.

## 8. Certification Impact

This phase advances Generation 3 by making UBTR communication meaning reusable
outside ACLI.

Certified boundaries preserved:

- UBTR owns communication meaning.
- Interface adapters own presentation only.
- Product 1 consumes communication artifacts.
- Provider output remains advisory.
- Worker execution remains outside this runtime.
- Governance, approval, authorization, replay, provider, worker, OCS, and CSA
  authority are unchanged.

## 9. Rollback Impact

Rollback is low-risk.

The runtime is additive and does not alter existing ACLI, UBTR translation,
Product 1, Provider, Worker, Governance, Approval, Authorization, or Replay
paths. Removing the new runtime and tests restores the previous state.

Existing ACLI compatibility wrappers remain available until future parity
alignment is certified.

## 10. Remaining Limitations

This phase does not yet:

- extract ACLI confirmation classification into a shared UBTR service;
- bind existing ACLI rendering to the shared communication artifacts;
- provide provider/worker/Product 1 specialized communication bindings;
- provide Web, Mobile, REST, or Voice adapters;
- invoke real providers;
- execute workers.

## 11. Next Implementation Batch

Recommended next batch:

`G3_04_PHASE_2_9_ACLI_COMMUNICATION_MODEL_ADAPTER_ALIGNMENT_V1`

Scope:

- make ACLI consume UBTR communication artifacts as an adapter;
- preserve terminal-specific presentation inside ACLI;
- keep communication meaning in UBTR;
- retain compatibility wrappers until parity is certified;
- add replay evidence for adapter rendering without changing platform meaning.

## 12. Final Determination

The UBTR Canonical Human Communication Model now has a deterministic runtime
foundation.

Final verdict: G3_04_PHASE_2_8_READY
