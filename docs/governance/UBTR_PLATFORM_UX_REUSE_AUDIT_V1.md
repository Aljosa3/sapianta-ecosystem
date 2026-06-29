# UBTR Platform UX Reuse Audit V1

Status: architectural reuse audit.

Final verdict: UBTR_PLATFORM_UX_EXTENSION_REQUIRED

## 1. Executive Summary

Platform Core Generation 2 is certified.

Recent Generation 3 audits established:

- UBTR is the canonical bidirectional translation layer;
- Platform Services are implemented once and reused everywhere;
- ACLI is an interface adapter only;
- Platform UX belongs to Platform Core;
- Interface UX belongs to interface adapters.

This audit verifies whether reusable Platform UX already exists inside the
certified UBTR implementation.

Conclusion:

- UBTR already implements substantial reusable Platform UX through the
  Governance -> Human translation runtime.
- UBTR already provides human-readable explanation payloads, sectioned
  explanations, governance summaries, proposal summaries, approval explanations,
  worker execution status wording, validation summaries, replay summaries, ERR
  summaries, next-action wording, authoritative state references, replay hashes,
  and non-authority notices.
- ACLI already calls UBTR for explanation rendering in the human-friendly
  explanation runtime, but ACLI still contains compatibility explanation
  sections, terminal operator response models, confirmation classification, and
  provider-assisted explanation wrappers.
- Shared Platform UX view models are not yet fully formalized as reusable
  Platform Core artifacts.
- The correct next step is not a new Platform UX system. It is a UBTR-centered
  Platform UX extension and de-duplication program that reuses existing
  Governance -> Human translation output and aligns ACLI wrappers into adapter
  or compatibility status.

## 2. Existing UBTR Platform UX Inventory

Reusable Platform UX already implemented inside UBTR / Universal Translation:

| UBTR Platform UX capability | Existing runtime | Status | Notes |
| --- | --- | --- | --- |
| Platform -> Human translation | `aigol/runtime/governance_to_human_translation_runtime.py` | IMPLEMENTED_IN_UBTR | Canonical Governance -> Human translation. |
| Human-readable payload | `governance_to_human_translation_runtime.py` | IMPLEMENTED_IN_UBTR | Emits `human_readable_payload`. |
| Sectioned explanation | `governance_to_human_translation_runtime.py` | IMPLEMENTED_IN_UBTR | Emits `sections` and `rendered_explanation`. |
| Governance summary | `governance_to_human_translation_runtime.py` | IMPLEMENTED_IN_UBTR | Emits `summary` and `governance_decision_summary`. |
| Proposal wording | `governance_to_human_translation_runtime.py` | PARTIALLY_IMPLEMENTED_IN_UBTR | Emits `proposal_summary`; detailed proposal preview remains ACLI/product-specific compatibility. |
| Approval wording | `governance_to_human_translation_runtime.py` | IMPLEMENTED_IN_UBTR | Emits `approval_explanation`. |
| Authorization wording | None dedicated in UBTR | PLATFORM_EXTENSION_REQUIRED | Authorization state can be represented through governance state, but no dedicated authorization UX model exists. |
| Worker wording | `governance_to_human_translation_runtime.py` | PARTIALLY_IMPLEMENTED_IN_UBTR | Emits `worker_execution_status`; worker lifecycle view model is not complete. |
| Replay wording | `governance_to_human_translation_runtime.py` | IMPLEMENTED_IN_UBTR | Emits `replay_summary`. |
| ERR wording | `governance_to_human_translation_runtime.py` | IMPLEMENTED_IN_UBTR | Emits `err_summary`. |
| Validation wording | `governance_to_human_translation_runtime.py` | IMPLEMENTED_IN_UBTR | Emits `validation_summary`. |
| Required next action wording | `governance_to_human_translation_runtime.py` | IMPLEMENTED_IN_UBTR | Emits `operator_action_required` and `WHAT TO DO NEXT`. |
| Authoritative state references | `governance_to_human_translation_runtime.py` | IMPLEMENTED_IN_UBTR | Emits source hashes and references. |
| Non-authority notice | `governance_to_human_translation_runtime.py` | IMPLEMENTED_IN_UBTR | States explanation does not approve or execute. |
| Optional advisory explanation integration | `universal_translation_runtime_integration.py` | PARTIALLY_IMPLEMENTED_IN_UBTR | Uses ACLI-named LLM-assisted explanation wrapper after deterministic translation. |
| Human -> Platform translation | `aigol/runtime/human_to_governance_translation_runtime.py` | IMPLEMENTED_IN_UBTR | Semantic input side of Platform UX. |
| Universal Translation schema | `aigol/runtime/universal_translation_artifact_schema.py` | IMPLEMENTED_IN_UBTR | Hash-bound artifact, directions, confidence, authority denial. |
| Universal Translation integration | `aigol/runtime/universal_translation_runtime_integration.py` | IMPLEMENTED_IN_UBTR | Canonical integration before HIRR routing and operator explanation. |

## 3. Capability Mapping

| Reviewed capability | UBTR runtime | ACLI runtime | Shared Platform Core | Governance artifacts | Classification |
| --- | --- | --- | --- | --- | --- |
| Explanation generation | `governance_to_human_translation_runtime.py` | `acli_human_friendly_explanation_runtime.py` | Platform UX / View Model service needed | G2-11 explanation rendering migration | PARTIALLY_IMPLEMENTED_IN_UBTR |
| Confirmation wording | `governance_to_human_translation_runtime.py` can express next action | `acli_operator_rendering_and_confirmation.py` | Shared Human Confirmation service needed | Platform UX audit | PARTIALLY_IMPLEMENTED_IN_UBTR |
| Confirmation classification | Human -> Governance translation detects some confirmation signals | `classify_operator_confirmation` in ACLI runtime | Shared Human Confirmation service needed | Translation alignment audit | ACLI_DUPLICATION |
| Proposal wording | `proposal_summary` in Governance -> Human translation | ACLI explanation section builder and bridge renderers | Proposal view model needed | G3-02 Phase 4 docs | PARTIALLY_IMPLEMENTED_IN_UBTR |
| Approval wording | `approval_explanation` in Governance -> Human translation | ACLI explanation sections and approval bridge renderers | Approval view model needed | G3-02 certification | PARTIALLY_IMPLEMENTED_IN_UBTR |
| Authorization wording | No dedicated UBTR authorization summary | `acli_authorization_bridge.py` | Authorization view model needed | G3-02 Phase 5 docs | PLATFORM_EXTENSION_REQUIRED |
| Replay wording | `replay_summary` in Governance -> Human translation | CLI replay/operator renderers | Replay view model needed | G2 final replay guarantees | PARTIALLY_IMPLEMENTED_IN_UBTR |
| Governance wording | `summary`, `governance_decision_summary`, sections | ACLI explanation compatibility sections | Governance view model needed | Universal Translation docs | IMPLEMENTED_IN_UBTR |
| Product UX wording | Not generic in UBTR | Product 1 decision/audit packet summaries | Product view model needed | G3-03 docs | PLATFORM_EXTENSION_REQUIRED |
| Provider wording | Provider metadata exists in translation schema; provider explanation wrapper is ACLI-named | `acli_llm_assisted_explanation_runtime.py`, planned provider rendering | Provider UX view model needed | Provider reuse audit | PLATFORM_EXTENSION_REQUIRED |
| Worker wording | `worker_execution_status` exists | Worker/operator renderers and execution summaries | Worker UX view model needed | G3-05 future scope | PARTIALLY_IMPLEMENTED_IN_UBTR |
| Platform-to-human rendering | `rendered_explanation` and section rendering | ACLI compose/render functions | Shared view-model rendering source needed | G2-11 | PARTIALLY_IMPLEMENTED_IN_UBTR |
| Semantic explanation rendering | Governance -> Human translation | ACLI human-friendly explanation combines UBTR and compatibility text | Shared Platform UX view model needed | G2-11 | PARTIALLY_IMPLEMENTED_IN_UBTR |
| Conversation presentation model | No complete UBTR conversation view model | ACLI conversational/session/rendering runtimes | Shared conversation view model needed | G3 responsibility audit | PLATFORM_EXTENSION_REQUIRED |
| Reusable response model | Translation payload exists but no dedicated response model | ACLI operator response lines | Shared response model needed | Platform UX audit | PARTIALLY_IMPLEMENTED_IN_UBTR |
| Operator summaries | Governance -> Human summaries exist | `operator_summary_runtime.py`, ACLI renderers | Shared summary view model needed | ACLI operator docs | PARTIALLY_IMPLEMENTED_IN_UBTR |
| Semantic summaries | UBTR normalized intent and translation payloads | memory/semantic summary and ACLI visibility | Shared semantic summary model may reuse UBTR | G2 certification | PARTIALLY_IMPLEMENTED_IN_UBTR |

## 4. Required Classification

| Capability | Exact classification |
| --- | --- |
| Human-facing explanation generation | PARTIALLY_IMPLEMENTED_IN_UBTR |
| Governance wording | IMPLEMENTED_IN_UBTR |
| Replay wording | PARTIALLY_IMPLEMENTED_IN_UBTR |
| Approval wording | PARTIALLY_IMPLEMENTED_IN_UBTR |
| Proposal wording | PARTIALLY_IMPLEMENTED_IN_UBTR |
| Authorization wording | PLATFORM_EXTENSION_REQUIRED |
| Confirmation wording | PARTIALLY_IMPLEMENTED_IN_UBTR |
| Confirmation classification | ACLI_DUPLICATION |
| Product UX wording | PLATFORM_EXTENSION_REQUIRED |
| Provider wording | PLATFORM_EXTENSION_REQUIRED |
| Worker wording | PARTIALLY_IMPLEMENTED_IN_UBTR |
| Platform-to-human rendering | PARTIALLY_IMPLEMENTED_IN_UBTR |
| Semantic explanation rendering | PARTIALLY_IMPLEMENTED_IN_UBTR |
| Confirmation rendering | ACLI_DUPLICATION |
| Proposal rendering | ACLI_DUPLICATION |
| Approval rendering | ACLI_DUPLICATION |
| Authorization rendering | ACLI_DUPLICATION |
| Replay presentation | PARTIALLY_IMPLEMENTED_IN_UBTR |
| Governance presentation | IMPLEMENTED_IN_UBTR |
| Shared platform view models | PLATFORM_EXTENSION_REQUIRED |
| Conversation models | PLATFORM_EXTENSION_REQUIRED |
| Presentation models | PLATFORM_EXTENSION_REQUIRED |
| Reusable response models | PLATFORM_EXTENSION_REQUIRED |
| Reusable operator summaries | PARTIALLY_IMPLEMENTED_IN_UBTR |
| Reusable semantic summaries | PARTIALLY_IMPLEMENTED_IN_UBTR |

No reviewed Platform UX capability is classified as `GENUINELY_MISSING` because
the certified UBTR translation implementation already provides the canonical
translation substrate. Missing pieces are extensions, view-model formalization,
or de-duplication, not a new Platform UX architecture.

## 5. Reuse Matrix

| Capability | Reuse action | Rationale |
| --- | --- | --- |
| Governance wording | REUSE | Already implemented in Governance -> Human translation. |
| Governance summary | REUSE | Existing `summary` and `governance_decision_summary` are canonical inputs. |
| Approval explanation | EXTEND | Existing UBTR wording exists; shared approval view model is needed. |
| Proposal summary | EXTEND | Existing UBTR summary exists; proposal preview/details require shared model. |
| Replay summary | EXTEND | Existing UBTR wording exists; full replay presentation model is needed. |
| Worker status wording | EXTEND | Existing UBTR status exists; lifecycle and result view model is needed. |
| Required next action | REUSE | Existing `operator_action_required` and `WHAT TO DO NEXT` sections are reusable. |
| Non-authority notice | REUSE | Existing UBTR notice should become shared Platform UX source. |
| Explanation sections | REMOVE_DUPLICATION | ACLI compatibility sections duplicate UBTR explanation structure. |
| Confirmation classification | REMOVE_DUPLICATION | ACLI classifier should become shared Human Confirmation service. |
| ACLI operator response lines | REMOVE_DUPLICATION | Terminal lines should render a shared response model. |
| Provider-assisted explanation | EXTEND | Existing advisory wrapper exists but is ACLI-named and should become shared. |
| Provider wording | NEW_IMPLEMENTATION | A shared provider UX model is not complete, but must be built on Provider Services and UBTR output. |
| Authorization wording | NEW_IMPLEMENTATION | Dedicated authorization UX model is not complete. |
| Product UX view model | NEW_IMPLEMENTATION | Product artifacts exist; shared display model is not complete. |
| Shared platform view model | NEW_IMPLEMENTATION | Required as a thin model over existing UBTR translation and platform evidence. |
| Conversation presentation model | NEW_IMPLEMENTATION | ACLI models exist; platform-neutral model is not complete. |

## 6. Duplicate Analysis

### 6.1 Explanation Generation And Rendering

Existing UBTR implementation:

- `governance_to_human_translation_runtime.py` creates the human-readable payload,
  sections, rendered explanation, replay summary, proposal summary, approval
  explanation, validation summary, and next action.

ACLI implementation:

- `acli_human_friendly_explanation_runtime.py` builds compatibility sections,
  invokes Governance -> Human translation, composes operator output, records
  rendering comparison, and preserves compatibility fallback.

Reuse opportunity:

- Treat UBTR Governance -> Human output as the canonical Platform UX source.
- Keep ACLI compatibility sections only as fallback/parity evidence.
- Move reusable section/view-model composition to Shared Platform UX.

Architectural impact:

- avoids separate ACLI explanation meaning;
- allows Web/Mobile/REST/Voice to reuse the same Platform UX.

### 6.2 Confirmation Classification

Existing UBTR implementation:

- Human -> Governance translation already detects confirmation-like signals in
  some semantic contexts.

ACLI implementation:

- `acli_operator_rendering_and_confirmation.py` implements confirm, reject,
  clarify, modify, continue, and unknown classification.

Reuse opportunity:

- Create a shared Human Confirmation service that uses deterministic command
  matching for exact confirmations and UBTR when natural-language semantic
  confirmation is needed.

Architectural impact:

- prevents each future interface from implementing its own confirmation
  semantics.

### 6.3 Proposal, Approval, And Authorization Wording

Existing UBTR implementation:

- Governance -> Human translation accepts proposal and approval state and emits
  proposal and approval summaries.

ACLI implementation:

- ACLI bridge and explanation modules render proposal/approval/authorization
  state for terminal use.

Reuse opportunity:

- Reuse UBTR summaries as semantic content.
- Add shared proposal, approval, and authorization view models.
- Keep ACLI terminal output as adapter rendering.

Architectural impact:

- preserves approval and authorization authority while reducing rendering
  duplication.

### 6.4 Replay And Governance Presentation

Existing UBTR implementation:

- Governance -> Human translation emits replay and governance summaries with
  authoritative state references.

ACLI implementation:

- CLI replay/operator renderers and summaries present replay/governance evidence.

Reuse opportunity:

- Use UBTR summaries as canonical Platform UX content.
- Add replay/governance view models for structured display.

Architectural impact:

- keeps replay read-only and avoids interface-specific replay meaning.

### 6.5 Provider And Worker Wording

Existing UBTR implementation:

- Translation schema includes provider metadata.
- Governance -> Human translation can include worker result summaries.

ACLI implementation:

- ACLI provider explanation runtime and planned provider/worker rendering are
  ACLI-facing.

Reuse opportunity:

- Extend UBTR/Platform UX with Provider Services and Worker Services view models.
- Keep provider output advisory and worker output execution-evidence only.

Architectural impact:

- avoids provider/worker UX becoming ACLI-specific.

## 7. Required Architectural Corrections

| Duplicated responsibility | Current owner | Canonical owner | Reuse strategy | Compatibility impact | Replay impact | Governance impact |
| --- | --- | --- | --- | --- | --- | --- |
| Explanation section composition | ACLI human-friendly explanation runtime | UBTR + Shared Platform UX | Reuse Governance -> Human sections; move shared section model to Platform UX | ACLI sections remain fallback | Add shared view-model hash | No authority change |
| Terminal operator response content | ACLI operator rendering runtime | Shared Platform UX; ACLI renders terminal format | Reuse UBTR required-action and summary payloads | Existing lines remain parity target | Record shared response model before render hash | No authority change |
| Confirmation classification | ACLI operator confirmation runtime | Shared Human Confirmation service with UBTR support | Extract class set and deterministic logic; use UBTR for semantic prose | ACLI classifier remains rollback | Record classifier source and input hash | Does not approve |
| Proposal/approval wording | ACLI explanation and bridge renderers | UBTR + Proposal/Approval view models | Reuse UBTR proposal/approval summaries; extend structured model | ACLI rendering remains adapter | Link to UBTR and bridge hashes | Approval authority unchanged |
| Authorization wording | ACLI authorization bridge | Authorization service + Shared Platform UX | Add authorization UX view model using bridge evidence | ACLI output remains adapter | Link view-model hash to authorization bridge | Authorization authority unchanged |
| Provider-assisted explanation | ACLI LLM-assisted explanation runtime | Shared advisory explanation service | Re-home wrapper under OCS/Provider governance, seeded by UBTR output | ACLI wrapper remains compatibility entry | Preserve provider request/response hashes | Provider remains advisory |
| Replay/governance presentation | CLI/operator renderers | UBTR + Replay/Governance view models | Reuse UBTR summaries and authoritative references | Existing CLI output remains adapter | Add platform view-model lineage | Replay/governance authority unchanged |
| Provider/worker presentation | Planned ACLI UX | Provider/Worker Services + Shared Platform UX | Build view models over existing provider/worker evidence and UBTR translation | ACLI renders only | Add view-model hashes | Provider/worker authority unchanged |

## 8. Roadmap Impact

Planned Generation 3 work should not be cancelled wholesale because UBTR does not
yet provide complete shared Platform UX view-model artifacts.

The roadmap should be changed as follows:

| Planned work | Roadmap disposition |
| --- | --- |
| New Platform UX architecture | Cancel as greenfield. UBTR already provides the canonical substrate. |
| Platform UX view-model foundation | Keep as small Platform Core extension over UBTR output. |
| ACLI explanation rendering expansion | Convert to adapter rendering over shared Platform UX. |
| ACLI confirmation expansion | Convert to shared Human Confirmation service plus ACLI adapter. |
| Provider UX rendering | Keep, but implement as Provider Services + UBTR Platform UX extension. |
| Worker UX rendering | Keep, but implement as Worker Services + UBTR Platform UX extension. |
| Product UX rendering | Keep, but implement as Product artifact + shared Platform UX view model. |

Estimated impact:

- duplicated implementation avoided: high for explanation, confirmation, replay,
  governance, proposal, and approval wording;
- roadmap simplification: medium-high because Platform UX becomes an extension of
  existing UBTR output;
- architectural complexity reduction: high because future interfaces consume one
  Platform UX source;
- future maintenance reduction: high because wording and semantic presentation
  changes are centralized.

## 9. Revised Generation 3 Implementation Order

Recommended order:

1. G3-04 Phase 2.6: UBTR Platform UX View Model Foundation.
   Build shared view-model artifacts over existing UBTR Governance -> Human
   translation output. No provider invocation and no worker execution.
2. G3-04 Phase 2.7: Shared Human Confirmation Service.
   Extract ACLI confirmation classification into a platform service, with UBTR
   support for natural-language semantic confirmation.
3. G3-04 Phase 3: Provider Services Canonical Registry And Policy Facade.
   Continue provider-service consolidation using the already approved reuse
   audit.
4. G3-04 Phase 4: Provider UX View Model Binding.
   Bind provider status, comparison, cost, failure, and advisory explanation
   evidence into shared Platform UX.
5. G3-04 Phase 5: OCS Provider Invocation Integration.
   Extend existing OCS/provider invocation paths after identity, registry,
   policy, and UX evidence models are aligned.
6. G3-05 Phase 1: Worker Services Existing Infrastructure Reuse Audit And UX
   Binding.
   Apply the same reuse-first model to worker presentation and execution
   evidence.

## 10. Recommended Next Implementation Batch

Recommended next batch:

`G3_04_PHASE_2_6_UBTR_PLATFORM_UX_VIEW_MODEL_FOUNDATION_V1`

Scope:

- define shared Platform UX view-model artifacts using existing UBTR
  Governance -> Human translation output;
- include explanation, governance, replay, proposal, approval, required action,
  non-authority, and compatibility/fallback sections;
- record source UBTR translation reference/hash and view-model hash;
- keep ACLI rendering as adapter output over the shared model;
- preserve existing ACLI explanation as compatibility evidence;
- do not create new semantic translation logic;
- do not invoke providers;
- do not invoke workers;
- do not change approval, authorization, governance, replay, provider, or worker
  authority.

Certification criteria:

- UBTR output is the canonical Platform UX source;
- shared view models are interface-neutral;
- ACLI output is adapter rendering only;
- compatibility output remains replay-visible;
- future interfaces can consume the same view-model artifacts;
- all authority flags remain denied.

## 11. Final Determination

Reusable Platform UX already exists inside UBTR, but it is incomplete as a
formal shared view-model layer.

Generation 3 should reuse and extend UBTR rather than implement a new Platform UX
system.

Final verdict: UBTR_PLATFORM_UX_EXTENSION_REQUIRED
