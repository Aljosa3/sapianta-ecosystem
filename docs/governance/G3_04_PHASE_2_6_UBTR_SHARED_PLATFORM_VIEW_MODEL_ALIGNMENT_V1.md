# G3-04 Phase 2.6 UBTR Shared Platform View Model Alignment V1

Status: architectural alignment specification.

Final verdict: UBTR_SHARED_VIEW_MODEL_ALIGNMENT_READY

## 1. Executive Summary

Platform Core Generation 2 is certified.

Generation 3 audits confirmed:

- Provider Services are reused and extended;
- UBTR is the canonical bidirectional translation layer;
- Platform UX belongs to Platform Core;
- ACLI is an interface adapter only;
- UBTR already provides substantial reusable Platform UX through Governance ->
  Human translation.

The remaining architectural gap is a canonical Shared Platform View Model layer.

This layer does not redesign Platform UX and does not duplicate UBTR. It
formalizes reusable, interface-neutral human-facing models on top of existing
UBTR Platform UX so ACLI, Web, Mobile, REST, Voice, and future adapters consume
the same semantic presentation contract.

## 2. Shared Platform View Model Architecture

Canonical architecture:

```text
Platform evidence
  Governance / Replay / OCS / PPP / Provider / Worker / Product / Approval
    |
    v
UBTR Platform UX
  Governance -> Human translation
  Human-readable payload
  Sections
  Required action
  Source references
  Non-authority notice
    |
    v
Shared Platform View Model Layer
  explanation model
  response model
  confirmation model
  proposal model
  approval model
  authorization model
  replay/governance model
  provider/worker model
    |
    v
Interface adapters
  ACLI terminal rendering
  Web layout
  Mobile layout
  REST serialization
  Voice rendering
```

The Shared Platform View Model layer is:

- deterministic;
- replay-visible where persisted;
- hash-bound;
- interface-neutral;
- non-authoritative;
- derived from existing UBTR Platform UX and Platform Services evidence;
- consumed by adapters without semantic reinterpretation.

## 3. Ownership Matrix

| Capability | Canonical owner | ACLI role | Future interface role | Notes |
| --- | --- | --- | --- | --- |
| Human -> Platform translation | UBTR | Submit operator input | Submit user input | Already implemented. |
| Platform -> Human translation | UBTR | Consume translated payload | Consume translated payload | Already implemented. |
| Canonical human-readable payload | UBTR Platform UX | Consume | Consume | Source for view models. |
| Shared response model | Shared Platform View Model layer | Render terminal output | Render interface-specific output | New alignment layer. |
| Explanation model | Shared Platform View Model layer over UBTR | Render terminal explanation | Render UI/API/voice explanation | Reuses UBTR sections. |
| Confirmation model | Shared Platform View Model / Human Confirmation service | Render prompt and submit input | Render prompt and submit input | Classifier extracted later. |
| Proposal model | Proposal service + Shared Platform View Model | Render terminal proposal | Render proposal view/API | Uses proposal evidence plus UBTR wording. |
| Approval model | Approval service + Shared Platform View Model | Render approval state | Render approval state | Does not grant approval. |
| Authorization model | Authorization service + Shared Platform View Model | Render readiness | Render readiness | Does not authorize execution. |
| Replay/governance model | Replay/Governance + UBTR + Shared View Model | Render evidence summary | Render evidence summary | Replay remains read-only. |
| Provider presentation model | Provider Services + UBTR + Shared View Model | Render provider evidence | Render provider evidence | Provider output remains advisory. |
| Worker presentation model | Worker Services + UBTR + Shared View Model | Render worker evidence | Render worker evidence | Worker authority unchanged. |
| Product 1 presentation model | Product 1 + Shared View Model | Render Product 1 evidence | Render Product 1 evidence | Product remains consumer. |
| Terminal formatting | ACLI | Own | None | Interface UX only. |
| Web layout | Web adapter | None | Own | Interface UX only. |
| Mobile layout | Mobile adapter | None | Own | Interface UX only. |
| REST envelope | REST adapter | None | Own | Interface UX only. |
| Voice synthesis/capture | Voice adapter | None | Own | Interface UX only. |

## 4. Reusable Model Definitions

### 4.1 Shared Response Model

Purpose:

Provide a single interface-neutral summary of the current human-facing platform
state.

Required fields:

- `view_model_id`;
- `view_model_type`;
- `source_translation_reference`;
- `source_translation_hash`;
- `source_evidence_references`;
- `summary`;
- `required_action`;
- `sections`;
- `non_authority_notice`;
- `fallback_status`;
- `compatibility_references`;
- `replay_lineage`;
- `view_model_hash`.

Source:

- UBTR Governance -> Human translation output;
- platform evidence references supplied to UBTR;
- compatibility evidence where parity is still being certified.

### 4.2 Explanation Model

Purpose:

Expose explanation sections consistently across interfaces.

Required sections:

- summary;
- proposal or current object;
- approval state;
- execution or worker state;
- validation state;
- replay state;
- governance state;
- what to do next;
- non-authority notice.

Source:

- `human_readable_payload.sections`;
- `rendered_explanation`;
- authoritative state references;
- compatibility explanation sections as fallback evidence.

### 4.3 Confirmation Model

Purpose:

Represent required human confirmation consistently.

Required fields:

- confirmation prompt;
- permitted confirmation classes;
- required action;
- current state reference;
- source translation reference/hash;
- confirmation evidence-only flag;
- authority denial flags.

Minimum confirmation classes:

- confirm;
- reject;
- clarify;
- modify;
- continue;
- unknown.

The classifier can remain in ACLI as compatibility evidence until a shared Human
Confirmation service is implemented and parity-certified.

### 4.4 Proposal Model

Purpose:

Represent proposal information consistently across interfaces.

Required fields:

- proposal reference/hash;
- proposal summary from UBTR;
- target paths or objects;
- proposal version where available;
- rollback reference;
- approval requirement;
- compatibility proposal rendering hash;
- non-execution notice.

### 4.5 Approval Model

Purpose:

Represent approval state consistently without granting approval.

Required fields:

- approval reference/hash;
- approval status;
- approval explanation from UBTR;
- required decision;
- proposal binding hash;
- replay lineage;
- non-authority flags.

### 4.6 Authorization Model

Purpose:

Represent authorization readiness consistently without authorizing execution.

Required fields:

- authorization bridge reference/hash;
- proposal reference/hash;
- approval request reference/hash;
- approval decision reference/hash;
- readiness status;
- precondition status;
- rollback reference;
- non-execution notice.

### 4.7 Replay / Governance Model

Purpose:

Represent replay and governance state in a shared human-facing model.

Required fields:

- replay reference/hash;
- replay summary from UBTR;
- governance summary from UBTR;
- authoritative state references;
- artifact count or evidence count where available;
- tamper/fail-closed status where available;
- read-only replay notice.

### 4.8 Provider Presentation Model

Purpose:

Represent provider status, provider evidence, advisory output, comparison, cost,
rate-limit, and failure state without granting provider authority.

Required fields:

- provider identity reference/hash;
- provider role;
- capability;
- activation status;
- invocation status;
- advisory-only status;
- comparison reference/hash where applicable;
- cost/rate-limit evidence where applicable;
- fallback status;
- provider non-authority notice.

### 4.9 Worker Presentation Model

Purpose:

Represent worker lifecycle, selection, dispatch, execution, result, and failure
state without changing worker authority.

Required fields:

- worker identity reference/hash;
- worker role;
- lifecycle status;
- selection status;
- dispatch reference/hash;
- invocation reference/hash;
- result reference/hash;
- validation reference/hash;
- authorization reference/hash;
- worker non-authority notice.

## 5. Adapter Consumption Model

Adapters consume Shared Platform View Models through a stable contract:

```text
Adapter input
  user input / command / event
    |
    v
Platform services
  UBTR / CSA / OCS / Replay / Governance / Product / Provider / Worker
    |
    v
Shared Platform View Model
    |
    v
Adapter rendering
```

Adapter rules:

1. Adapters may render, serialize, paginate, speak, or arrange view models.
2. Adapters may not change view-model semantics.
3. Adapters may not create parallel explanation, confirmation, replay,
   governance, provider, worker, proposal, approval, or authorization meaning.
4. Adapters must preserve source view-model reference/hash in replay-visible
   render artifacts when rendering is persisted.
5. Adapter-specific render hashes must be separate from shared view-model hashes.

ACLI wrappers that become consumers:

| Current ACLI wrapper | Future role |
| --- | --- |
| `acli_human_friendly_explanation_runtime.py` | Terminal renderer / compatibility wrapper over Explanation Model |
| `acli_operator_rendering_and_confirmation.py` | Terminal renderer over Response and Confirmation Models; classifier compatibility path |
| `acli_llm_assisted_explanation_runtime.py` | Compatibility wrapper until shared advisory explanation model exists |
| `acli_proposal_approval_bridge.py` | Source evidence producer and terminal renderer over Proposal/Approval Models |
| `acli_authorization_bridge.py` | Source evidence producer and terminal renderer over Authorization Model |

## 6. Compatibility Strategy

Compatibility remains active intentionally.

Compatibility rules:

- existing ACLI output remains replay-visible;
- existing ACLI explanation sections remain parity evidence;
- existing ACLI confirmation classification remains rollback evidence until the
  shared classifier is certified;
- existing proposal, approval, and authorization bridge artifacts remain source
  evidence;
- no compatibility path may become hidden primary authority;
- all compatibility fallback must record source, hash, fallback reason, and
  migration status.

Compatibility states:

| State | Meaning |
| --- | --- |
| `SHARED_VIEW_MODEL_PRIMARY` | Shared model is primary and adapter output is render-only. |
| `COMPATIBILITY_PARITY_VISIBLE` | Shared model exists but compatibility output remains visible for parity. |
| `COMPATIBILITY_FALLBACK_ACTIVE` | Shared model cannot yet cover the case; old output remains fallback. |
| `ADAPTER_ONLY` | Responsibility is genuinely interface-specific. |

## 7. Replay Impact

Replay must record:

- shared view-model id;
- shared view-model type;
- UBTR translation reference/hash;
- source platform evidence references/hashes;
- compatibility source references/hashes;
- fallback status;
- adapter id;
- adapter render hash where rendering is persisted;
- non-authority flags;
- replay lineage.

Replay must distinguish:

```text
semantic translation hash
view-model hash
adapter-render hash
```

This preserves auditability and prevents terminal output from becoming the
source of platform meaning.

## 8. Governance Impact

The Shared Platform View Model layer does not own governance authority.

It must preserve:

- UBTR semantic authority;
- CSA representation authority;
- OCS cognition authority;
- Replay read-only authority;
- Governance policy authority;
- Proposal ownership;
- Approval authority;
- Authorization authority;
- Provider ownership;
- Worker ownership;
- Product ownership;
- interface adapter boundaries.

All view-model artifacts must deny:

- approval authority;
- execution authority;
- mutation authority;
- provider authority;
- worker authority;
- replay mutation authority;
- governance mutation authority.

## 9. Certification Impact

The alignment is certifiable when:

1. shared view-model artifacts derive from existing UBTR Platform UX and platform
   evidence;
2. each view model is deterministic and hash-bound;
3. ACLI renders from the shared model without changing meaning;
4. compatibility output remains visible;
5. future interfaces can consume the same model without local translation;
6. authority flags remain denied;
7. replay reconstruction can distinguish translation, view model, and adapter
   render hashes.

Certification does not require:

- new semantic translation logic;
- provider invocation;
- worker execution;
- repository mutation;
- approval automation;
- deployment.

## 10. Rollback Impact

Rollback is bounded.

Rollback strategy:

- keep existing ACLI explanation/rendering as compatibility output;
- keep existing UBTR translation artifacts as canonical source;
- keep bridge artifacts for proposal, approval, and authorization;
- allow adapters to return to direct compatibility rendering if a shared model is
  incomplete;
- preserve all source references and hashes so rollback remains replay-visible.

Rollback must not:

- bypass UBTR translation for semantic meaning;
- hide compatibility output;
- delete historical replay;
- transfer authority to adapters.

## 11. Implementation Roadmap

Recommended implementation sequence:

1. Define shared view-model schema and validator.
2. Implement Explanation and Response models over existing Governance -> Human
   translation output.
3. Add replay reconstruction for shared view-model artifacts.
4. Convert ACLI human-friendly explanation rendering to consume the shared
   Explanation model while preserving compatibility output.
5. Implement Confirmation model and retain ACLI classifier as compatibility
   evidence.
6. Implement Proposal, Approval, and Authorization models over existing bridge
   artifacts.
7. Implement Replay and Governance models over existing replay/governance
   evidence.
8. Implement Provider and Worker presentation models after Provider Services and
   Worker Services alignment.
9. Certify ACLI as adapter-only over shared view models.
10. Use the same models for future Web, Mobile, REST, Voice, and future
    adapters.

## 12. Final Determination

The canonical Shared Platform View Model layer can be designed and certified on
top of existing UBTR Platform UX.

The layer is an alignment and formalization step, not a Platform UX redesign.

Final verdict: UBTR_SHARED_VIEW_MODEL_ALIGNMENT_READY
