# G3-04 Phase 3D UHCL Shared Confirmation Alignment V1

Status: runtime extension implemented.

Final verdict: G3_04_PHASE_3D_READY

## 1. Executive Summary

The Universal Human Communication Layer now includes canonical communication
artifacts, typed communication sections, source evidence binding, and
progressive explanation derivation.

This phase implements a Shared Confirmation Model inside UBTR/UHCL. The model
defines one reusable confirmation section and one reusable response model for
confirmation, clarification, modification, rejection, and continuation.

The model integrates with approval and authorization evidence by reference and
hash only. It does not create approval, authorization, execution authority,
provider invocation, worker execution, repository mutation, deployment, or
interface-specific presentation semantics.

## 2. Files Changed

Runtime:

- `aigol/runtime/ubtr_human_communication_model_runtime.py`

Tests:

- `tests/test_ubtr_human_communication_model_runtime_v1.py`

Documentation:

- `docs/governance/G3_04_PHASE_3D_UHCL_SHARED_CONFIRMATION_ALIGNMENT_V1.md`

## 3. Shared Confirmation Model

The runtime now creates a replay-visible shared confirmation artifact with:

- confirmation id;
- source component;
- target human context;
- communication level;
- confirmation prompt;
- required human action;
- confirmation section;
- supported response types;
- response models;
- evidence references;
- source evidence binding;
- confirmation lineage;
- replay lineage;
- rollback reference;
- non-authority notices;
- authority denial.

Canonical response types:

- `CONFIRMATION`
- `CLARIFICATION`
- `MODIFICATION`
- `REJECTION`
- `CONTINUATION`

Each response model records its meaning and required payload fields while
explicitly denying approval creation, authorization creation, execution
authority, provider invocation, worker invocation, and repository mutation.

## 4. Evidence Binding

The confirmation model reuses the UHCL source evidence binding pattern.

Every shared confirmation artifact records:

- source evidence references;
- source evidence hashes;
- source evidence reference count;
- source evidence reference hash;
- source component;
- optional CSA reference/hash;
- optional OCS reference/hash;
- optional approval reference/hash;
- optional authorization reference/hash;
- optional governance, replay, provider, worker, and product references when
  supplied through source evidence bindings;
- source evidence binding hash.

Approval and authorization evidence are integration inputs only. Confirmation
does not create approval or authorization outcomes.

## 5. Replay Impact

Shared confirmation artifacts are replay-visible standalone artifacts using:

- replay index: `0`;
- replay step: `uhcl_shared_confirmation_model_recorded`;
- event type: `UBTR_HUMAN_COMMUNICATION_MODEL_RUNTIME_V1`;
- artifact type: `UHCL_SHARED_CONFIRMATION_MODEL_ARTIFACT_V1`;
- schema version: `UHCL_SHARED_CONFIRMATION_ALIGNMENT_V1`.

Replay reconstruction verifies:

- wrapper ordering;
- wrapper replay hash;
- artifact type;
- schema version;
- source component;
- communication level;
- supported response types;
- response model non-authority flags;
- evidence references and evidence hash;
- source evidence binding hash;
- confirmation section hash;
- approval and authorization evidence references;
- replay lineage hash;
- non-authority notices;
- authority denial;
- artifact hash.

Tampering with response authority flags, evidence binding, confirmation section
hash, replay lineage, or artifact hash fails closed.

## 6. Certification Impact

This phase unifies confirmation semantics across Platform Core.

Preserved boundaries:

- UBTR owns confirmation communication meaning.
- Interface adapters render confirmation choices only.
- Approval remains the approval authority.
- Authorization remains the authorization authority.
- Governance remains the governance authority.
- Replay remains the reconstruction authority.
- Provider and worker layers remain non-invoked.
- Product 1 consumes confirmation artifacts and does not own reusable
  confirmation semantics.

The model supports ACLI, Web, Mobile, REST, Voice, and future interfaces because
the confirmation response model is interface-neutral.

## 7. Rollback Impact

Rollback is low-risk.

The change adds a new UHCL confirmation artifact and does not alter existing
communication artifact behavior. Existing typed section, source evidence
binding, and progressive explanation derivation behavior remains compatible.

Rollback consists of removing:

- shared confirmation constants;
- shared confirmation creation and reconstruction functions;
- confirmation response model helpers;
- shared confirmation validation helpers;
- shared confirmation regression tests;
- this governance document.

## 8. Remaining UHCL Capabilities

Remaining UHCL work:

1. provider communication binding over Provider Services;
2. worker communication binding over Worker Services;
3. Product 1 communication binding;
4. recovery guidance derivation from evidence-bound recovery sections;
5. ACLI adapter rendering over UHCL artifacts;
6. compatibility comparison and parity certification;
7. final UHCL certification.

## 9. Next Implementation Batch

Recommended next batch:

`G3_04_PHASE_3E_UHCL_PROVIDER_WORKER_PRODUCT_COMMUNICATION_BINDINGS_V1`

Scope:

- bind provider communication to Provider Services evidence;
- bind worker communication to Worker Services evidence;
- bind Product 1 communication to product decision evidence;
- preserve non-authority and replay-visible lineage;
- do not invoke providers;
- do not execute workers;
- do not mutate repositories;
- do not add interface-specific communication meaning.

## 10. Final Determination

UHCL shared confirmation alignment is implemented and validated as a
deterministic UBTR-owned runtime extension.

Final verdict: G3_04_PHASE_3D_READY
