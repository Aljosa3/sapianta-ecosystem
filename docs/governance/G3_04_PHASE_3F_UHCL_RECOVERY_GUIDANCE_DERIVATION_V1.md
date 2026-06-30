# G3-04 Phase 3F UHCL Recovery Guidance Derivation V1

Status: runtime extension implemented.

Final verdict: G3_04_PHASE_3F_READY

## 1. Executive Summary

The Universal Human Communication Layer now includes canonical communication
artifacts, typed communication sections, source evidence binding, progressive
explanation derivation, the shared confirmation model, and Provider/Worker/
Product communication bindings.

This phase implements canonical Recovery Guidance inside UHCL. Recovery
guidance explains why an operation cannot continue, which prerequisites are
missing, which recovery actions are available, and which human action is
recommended next.

The model is deterministic, replay-visible, evidence-bound, interface-neutral,
and non-authoritative. It does not perform recovery and does not introduce
provider invocation, worker execution, approval, authorization, deployment, or
repository mutation.

## 2. Files Changed

Runtime:

- `aigol/runtime/ubtr_human_communication_model_runtime.py`

Tests:

- `tests/test_ubtr_human_communication_model_runtime_v1.py`

Documentation:

- `docs/governance/G3_04_PHASE_3F_UHCL_RECOVERY_GUIDANCE_DERIVATION_V1.md`

## 3. Recovery Guidance Model

The runtime now creates a replay-visible recovery guidance artifact with:

- recovery id;
- source component;
- target human context;
- communication level;
- blocked operation;
- reason the operation cannot continue;
- missing prerequisites;
- available recovery actions;
- recommended next action;
- embedded typed `RECOVERY` section;
- recovery section hash;
- recovery section replay reference;
- evidence references;
- source evidence binding;
- recovery lineage;
- recovery policy;
- replay lineage;
- rollback reference;
- non-authority notices;
- authority denial.

Every recovery action explicitly denies automatic execution, provider
invocation, worker execution, and repository mutation. The recommended next
action must reference one of the available recovery actions.

## 4. Evidence Lineage

The recovery evidence lineage model is:

```text
blocking evidence
  -> evidence reference/hash
  -> source evidence binding
  -> typed RECOVERY section artifact
  -> recovery guidance artifact
  -> replay wrapper hash
```

UHCL may explain blocking conditions and available recovery paths, but the
underlying evidence remains owned by its source component.

## 5. Replay Impact

Recovery guidance artifacts are replay-visible standalone artifacts using:

- replay index: `0`;
- replay step: `uhcl_recovery_guidance_model_recorded`;
- event type: `UBTR_HUMAN_COMMUNICATION_MODEL_RUNTIME_V1`;
- artifact type: `UHCL_RECOVERY_GUIDANCE_MODEL_ARTIFACT_V1`;
- schema version: `UHCL_RECOVERY_GUIDANCE_DERIVATION_V1`.

Replay reconstruction verifies:

- wrapper ordering;
- wrapper replay hash;
- artifact type;
- schema version;
- source component;
- communication level;
- blocked operation;
- cannot-continue reason;
- missing prerequisites;
- available recovery actions;
- recommended next action;
- recovery section hash;
- source evidence binding hash;
- evidence hash;
- recovery lineage;
- recovery policy;
- replay lineage hash;
- non-authority notices;
- authority denial;
- artifact hash.

Tampering with recommendations, recovery policy, evidence binding, replay
lineage, authority flags, or artifact hashes fails closed.

## 6. Certification Impact

This phase completes the last core UHCL communication capability before adapter
rendering and parity certification.

Preserved boundaries:

- UBTR owns recovery communication meaning.
- Source components own the blocking evidence.
- Governance, approval, authorization, provider, worker, and Product authority
  remain separate.
- Replay owns reconstruction and evidence continuity.
- Interface adapters own presentation only.

No automatic recovery, provider invocation, worker execution, approval,
authorization, deployment, repository mutation, or interface rendering is
introduced.

## 7. Rollback Impact

Rollback is low-risk.

The change adds a new recovery guidance artifact and uses existing typed
section/source evidence binding primitives. Existing communication artifacts,
typed sections, progressive explanation, shared confirmation, and Provider/
Worker/Product binding behavior remains compatible.

Rollback consists of removing:

- recovery guidance constants;
- recovery guidance creation and reconstruction functions;
- recovery validation helpers;
- recovery guidance regression tests;
- this governance document.

## 8. Remaining UHCL Capabilities

Remaining UHCL work:

1. ACLI adapter rendering over UHCL artifacts;
2. compatibility comparison and parity certification;
3. final UHCL certification.

## 9. Next Implementation Batch

Recommended next batch:

`G3_04_PHASE_3G_UHCL_ACLI_ADAPTER_RENDERING_ALIGNMENT_V1`

Scope:

- align ACLI rendering with UHCL artifacts;
- keep ACLI as a presentation adapter only;
- preserve replay-visible communication artifacts;
- remove duplicated reusable communication semantics from ACLI;
- do not invoke providers;
- do not execute workers;
- do not mutate repositories;
- do not add interface-specific communication meaning.

## 10. Final Determination

UHCL recovery guidance derivation is implemented and validated as a
deterministic UBTR-owned runtime extension.

Final verdict: G3_04_PHASE_3F_READY
