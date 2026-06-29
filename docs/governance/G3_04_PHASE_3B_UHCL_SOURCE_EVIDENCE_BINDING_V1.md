# G3-04 Phase 3B UHCL Source Evidence Binding V1

Status: runtime extension implemented.

Final verdict: G3_04_PHASE_3B_READY

## 1. Executive Summary

G3-04 Phase 3A implemented UHCL typed communication sections.

This phase extends those typed sections with canonical source-evidence binding.
Every evidence-bound communication section can now link human-facing
communication meaning to platform evidence without becoming authoritative.

The implementation extends the existing UBTR Human Communication Runtime. It
does not introduce a parallel communication layer.

## 2. Files Changed

Runtime:

- `aigol/runtime/ubtr_human_communication_model_runtime.py`

Tests:

- `tests/test_ubtr_human_communication_model_runtime_v1.py`

Documentation:

- `docs/governance/G3_04_PHASE_3B_UHCL_SOURCE_EVIDENCE_BINDING_V1.md`

## 3. Evidence Binding Model

Typed UHCL sections now record:

- section id;
- section type;
- communication level;
- source component;
- source evidence references;
- source evidence hashes;
- source evidence reference count;
- source evidence reference hash;
- optional CSA reference/hash;
- optional OCS reference/hash;
- optional replay reference/hash;
- optional governance reference/hash;
- optional provider reference/hash;
- optional worker reference/hash;
- optional Product reference/hash;
- optional approval reference/hash;
- optional authorization reference/hash;
- replay lineage;
- rollback reference;
- non-authority notices;
- source evidence binding hash.

Supported source components:

- `CSA`
- `OCS`
- `REPLAY`
- `GOVERNANCE`
- `PROVIDER`
- `WORKER`
- `PRODUCT`
- `APPROVAL`
- `AUTHORIZATION`
- `UBTR`

## 4. Section Lineage Model

The section lineage model is:

```text
source evidence
  -> evidence reference/hash
  -> source evidence binding hash
  -> typed communication section artifact hash
  -> replay wrapper hash
  -> optional canonical communication artifact section hash
```

This keeps evidence provenance separate from authority. Human-facing
communication can explain source evidence, but it cannot approve, authorize,
execute, invoke providers, invoke workers, mutate repositories, or mutate replay.

## 5. Replay Evidence

Replay reconstruction verifies:

- typed section replay wrapper ordering;
- wrapper replay hash;
- section artifact hash;
- section type;
- communication level;
- source component;
- evidence references;
- evidence hash list;
- source evidence reference count;
- source evidence reference hash;
- specific source references and hashes;
- specific source hash rollup;
- source evidence binding hash;
- replay lineage hash;
- non-authority notices;
- authority denial.

Tampering with source evidence hash lists or source binding fields fails closed.

## 6. Certification Impact

This phase strengthens UHCL certification by making source evidence binding
explicit and deterministic.

Preserved authority boundaries:

- UBTR owns communication meaning.
- CSA owns canonical semantic representation.
- OCS owns cognition orchestration.
- Governance owns governance decision authority.
- Approval owns approval authority.
- Authorization owns authorization readiness and gate evidence.
- Provider Layer owns provider boundaries.
- Worker Layer owns worker boundaries.
- Product 1 owns product artifacts and consumes communication.
- Replay owns reconstruction and evidence continuity.
- Interface adapters own presentation only.

No provider invocation, worker execution, repository mutation, deployment,
ACLI rendering, Web/Mobile/Voice adapter behavior, approval creation, or
authorization creation is introduced.

## 7. Rollback Impact

Rollback is low-risk.

The source evidence binding model extends typed section artifacts while keeping
existing communication artifact behavior intact. No existing call site is forced
to supply source bindings yet.

Rollback consists of removing:

- source component constants;
- source binding normalization and validation;
- source binding fields from typed section artifacts;
- source binding regression tests;
- this governance document.

## 8. Remaining UHCL Capabilities

Remaining UHCL work:

1. progressive explanation derivation;
2. shared confirmation alignment;
3. provider communication binding over live Provider Services;
4. worker communication binding over Worker Services;
5. Product 1 communication binding;
6. ACLI adapter rendering over UHCL artifacts;
7. compatibility comparison and parity certification;
8. final UHCL certification.

## 9. Next Implementation Batch

Recommended next batch:

`G3_04_PHASE_3C_UHCL_PROGRESSIVE_EXPLANATION_AND_RECOVERY_GUIDANCE_V1`

Scope:

- derive progressive explanation views from typed UHCL sections;
- derive canonical recovery guidance from evidence-bound sections;
- preserve communication level semantics;
- preserve source evidence hashes and lineage;
- keep compatibility fallback active;
- do not invoke providers;
- do not execute workers;
- do not mutate repositories;
- do not add interface-specific rendering.

## 10. Final Determination

UHCL source evidence binding is implemented and validated.

Final verdict: G3_04_PHASE_3B_READY
