# G3-04 Phase 3C UHCL Progressive Explanation Derivation V1

Status: runtime extension implemented.

Final verdict: G3_04_PHASE_3C_READY

## 1. Executive Summary

G3-04 Phase 3B implemented source evidence binding for UHCL typed
communication sections.

This phase extends the existing UBTR Human Communication Runtime with
progressive explanation derivation. A single canonical communication artifact
can now produce deterministic explanation variants at multiple communication
levels without changing semantic meaning, evidence binding, replay lineage, or
authority boundaries.

The implementation extends UBTR. It does not introduce a parallel communication
layer and does not move communication meaning into ACLI or any other interface
adapter.

## 2. Files Changed

Runtime:

- `aigol/runtime/ubtr_human_communication_model_runtime.py`

Tests:

- `tests/test_ubtr_human_communication_model_runtime_v1.py`

Documentation:

- `docs/governance/G3_04_PHASE_3C_UHCL_PROGRESSIVE_EXPLANATION_DERIVATION_V1.md`

## 3. Progressive Explanation Model

The runtime now creates a replay-visible progressive explanation derivation
artifact with:

- derivation id;
- source communication reference;
- source communication hash;
- source communication domain;
- source communication level;
- requested target levels;
- source section hashes;
- source evidence hashes;
- source evidence binding hashes;
- semantic meaning hash;
- evidence lineage hash;
- per-level derived explanations;
- replay lineage;
- rollback reference;
- non-authority notices;
- authority denial.

The model derives explanation content only from the source communication
artifact and its embedded typed section communication level variants.

## 4. Communication Level Derivation

Supported communication levels:

- `CONCISE`
- `STANDARD`
- `DETAILED`
- `BEGINNER`
- `TECHNICAL`
- `AUDITOR`
- `EXECUTIVE`

For each target level, UHCL records:

- communication level;
- semantic meaning hash;
- evidence lineage hash;
- section derivations;
- source section hash;
- source evidence hashes;
- source evidence binding hash;
- variant hash;
- derivation mode;
- explicit `new_facts_introduced: false`;
- explicit authority denial.

If a source typed section already declares a variant for the requested level,
UHCL uses that explicit variant. If no variant exists, UHCL falls back to the
base section level. In both cases, the derived explanation remains traceable to
the same source section hash and evidence lineage.

## 5. Replay Impact

Progressive explanation derivations are replay-visible standalone artifacts
using:

- replay index: `0`;
- replay step: `uhcl_progressive_explanation_derivation_recorded`;
- event type: `UBTR_HUMAN_COMMUNICATION_MODEL_RUNTIME_V1`;
- artifact type: `UHCL_PROGRESSIVE_EXPLANATION_DERIVATION_ARTIFACT_V1`;
- schema version: `UHCL_PROGRESSIVE_EXPLANATION_DERIVATION_V1`.

Replay reconstruction verifies:

- wrapper ordering;
- wrapper replay hash;
- artifact type;
- schema version;
- supported target levels;
- source communication hash;
- source section hash list;
- semantic meaning hash;
- evidence lineage hash;
- per-level semantic consistency;
- per-level evidence consistency;
- per-section variant hash;
- no new facts introduced;
- replay lineage hash;
- non-authority notices;
- authority denial;
- artifact hash.

Tampering with derived fact status, source hashes, evidence lineage, policy, or
authority flags fails closed.

## 6. Certification Impact

This phase advances UHCL certification by proving that one canonical UBTR
communication artifact can support multiple human communication levels without
duplicating meaning in adapters.

Preserved boundaries:

- UBTR owns communication meaning.
- Interface adapters own presentation only.
- CSA remains the semantic representation authority.
- OCS remains the cognition orchestration authority.
- Replay owns reconstruction and evidence continuity.
- Governance, approval, and authorization retain their authority boundaries.
- Provider Layer and Worker Layer remain non-invoked.
- Product 1 consumes communication artifacts and does not own reusable
  communication meaning.

No provider invocation, worker execution, repository mutation, deployment,
ACLI rendering, Web/Mobile/Voice adapter behavior, approval creation, or
authorization creation is introduced.

## 7. Rollback Impact

Rollback is low-risk.

The change adds a new derivation artifact over existing communication artifacts
and typed section variants. Existing communication and typed section creation
remain compatible.

Rollback consists of removing:

- progressive explanation constants;
- progressive derivation and reconstruction functions;
- progressive derivation validation helpers;
- progressive derivation regression tests;
- this governance document.

## 8. Remaining UHCL Capabilities

Remaining UHCL work:

1. shared confirmation alignment;
2. provider communication binding over Provider Services;
3. worker communication binding over Worker Services;
4. Product 1 communication binding;
5. recovery guidance derivation from evidence-bound recovery sections;
6. ACLI adapter rendering over UHCL artifacts;
7. compatibility comparison and parity certification;
8. final UHCL certification.

## 9. Next Implementation Batch

Recommended next batch:

`G3_04_PHASE_3D_UHCL_SHARED_CONFIRMATION_ALIGNMENT_V1`

Scope:

- align confirmation semantics with the UHCL communication artifact model;
- bind confirmations to evidence and non-authority notices;
- preserve replay-visible confirmation lineage;
- keep ACLI as a presentation adapter only;
- do not invoke providers;
- do not execute workers;
- do not mutate repositories;
- do not add interface-specific communication meaning.

## 10. Final Determination

UHCL progressive explanation derivation is implemented and validated as a
deterministic UBTR-owned runtime extension.

Final verdict: G3_04_PHASE_3C_READY
