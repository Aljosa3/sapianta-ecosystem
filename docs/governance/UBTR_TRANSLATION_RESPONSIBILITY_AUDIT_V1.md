# UBTR Translation Responsibility Audit V1

Status: architectural responsibility audit.

Final verdict: TRANSLATION_RESPONSIBILITY_RESTRUCTURING_REQUIRED

## 1. Executive Summary

Platform Core Generation 2 is certified.

Generation 3 responsibility restructuring established that interfaces are adapters,
shared Platform capabilities are implemented once, products consume Platform Services,
UBTR remains the canonical semantic entry point, CSA remains the canonical semantic
representation, and OCS remains the canonical governance and cognition orchestration
layer.

This audit verifies translation responsibility as implemented.

The current architecture already establishes UBTR / Universal Translation as the
canonical translation layer for:

- Human -> Governance translation;
- Governance -> Human translation;
- replay-visible translation artifacts;
- CSA-linked semantic lineage;
- deterministic operator explanation input.

However, reusable platform-to-human presentation responsibilities still exist in
ACLI-named runtimes. These ACLI runtimes often consume UBTR translation correctly,
but their placement and names risk making ACLI the owner of shared explanation,
rendering, confirmation, and operator-response models. That would force future Web,
Mobile, REST, Voice, and other adapters to duplicate translation-adjacent logic.

The correct conclusion is:

- UBTR is the canonical translation layer.
- CSA is the canonical semantic representation, not a translator.
- OCS is the cognition and governance orchestration layer, not a human-facing
  translation owner.
- ACLI is currently the first adapter and contains some reusable rendering and
  explanation compatibility code that should be extracted into shared Platform
  translation/view-model services.
- Product 1 consumes structured platform evidence and does not currently own
  canonical translation.

## 2. Evidence Reviewed

Primary runtime evidence:

| Area | Evidence |
| --- | --- |
| Human -> Governance translation | `aigol/runtime/human_to_governance_translation_runtime.py` |
| Governance -> Human translation | `aigol/runtime/governance_to_human_translation_runtime.py` |
| Universal Translation integration | `aigol/runtime/universal_translation_runtime_integration.py` |
| Universal Translation artifact schema | `aigol/runtime/universal_translation_artifact_schema.py` |
| ACLI conversational routing integration | `aigol/runtime/conversational_cli_runtime.py` |
| ACLI operator rendering / confirmation | `aigol/runtime/acli_operator_rendering_and_confirmation.py` |
| ACLI human-friendly explanation | `aigol/runtime/acli_human_friendly_explanation_runtime.py` |
| ACLI LLM-assisted explanation | `aigol/runtime/acli_llm_assisted_explanation_runtime.py` |
| Product 1 workflow foundation | `aigol/runtime/product1_workflow_foundation.py` |
| Product 1 Decision Packet | `aigol/runtime/product1_decision_packet.py` |
| Product 1 OCS advisory | `aigol/runtime/product1_ocs_advisory.py` |
| Product 1 Audit Packet | `aigol/runtime/product1_audit_packet.py` |

Primary governance evidence:

| Area | Evidence |
| --- | --- |
| Universal Translation integration | `docs/governance/UNIVERSAL_TRANSLATION_RUNTIME_INTEGRATION_V1.md` |
| UBTR / HIRR boundary | `docs/governance/UBTR_HIRR_FINAL_BOUNDARY_SPECIFICATION_V1.md` |
| G2 explanation rendering migration | `docs/governance/PLATFORM_SEMANTIC_GAP_CLOSURE_G2_11_EXPLANATION_RENDERING_MIGRATION_V1.md` |
| G2 final certification | `docs/governance/PLATFORM_CORE_GENERATION_2_FINAL_CERTIFICATION_V1.md` |
| G3 responsibility placement audit | `docs/governance/GENERATION_3_RESPONSIBILITY_PLACEMENT_AUDIT_V1.md` |
| G3 platform service ownership refactor | `docs/governance/G3_04_PHASE_1_5_PLATFORM_SERVICE_OWNERSHIP_REFACTOR_PROGRAM_V3.md` |

## 3. Required Questions

| Question | Answer | Evidence | Assessment |
| --- | --- | --- | --- |
| Is UBTR currently the canonical Human -> Platform translator? | Yes. | `human_to_governance_translation_runtime.py` creates Universal Translation artifacts; `conversational_cli_runtime.py` invokes `translate_human_to_governance`; `UNIVERSAL_TRANSLATION_RUNTIME_INTEGRATION_V1.md` declares Human -> Universal Translation -> HIRR as canonical. | Correct. |
| Is UBTR currently the canonical Platform -> Human translator? | Yes, for Governance -> Human translation and explanation input. | `governance_to_human_translation_runtime.py`; `universal_translation_runtime_integration.py`; G2-11 explanation migration; G2 final certification. | Correct, but presentation ownership needs cleanup. |
| Does ACLI currently own reusable translation responsibility? | Partially, by placement and naming, not by authority. | `acli_operator_rendering_and_confirmation.py`, `acli_human_friendly_explanation_runtime.py`, and `acli_llm_assisted_explanation_runtime.py`. | Misplaced shared presentation/translation-adjacent responsibility. |
| Does Product 1 own reusable translation responsibility? | No. | Product 1 workflow, packet, advisory, and audit runtimes consume CSA, OCS, governance, replay, and evidence structures. | Correct. |
| Are explanation rendering and semantic translation clearly separated? | Partially. | G2-11 separates CSA/UBTR explanation source from compatibility rendering; ACLI explanation runtime still mixes ACLI naming with canonical UBTR output and compatibility sections. | Separation exists, but needs platform-level contract cleanup. |
| Is human-facing explanation generation already centralized? | Partially. | Governance -> Human translation is centralized; ACLI explanation and optional provider explanation are still ACLI-named compatibility/advisory layers. | Central translation exists; rendering/view model centralization incomplete. |
| Would a future Web interface need its own translator? | It should not, but current placement risks that. | G3 platform-service refactor says shared rendering/view models belong to Platform Core, while current reusable rendering logic is ACLI-named. | Requires correction before Web implementation. |
| Would a future Mobile interface need its own translator? | It should not, but current placement risks duplication. | Same evidence as Web. | Requires correction. |
| Would a future Voice interface need its own translator? | Voice needs modality capture/output adaptation, not semantic translation ownership. | UBTR owns translation; interfaces are adapters. | Requires shared platform view/speech model boundary before Voice. |
| Does the current architecture violate implement-once for translation? | Not for core UBTR translation; partially for translation-adjacent presentation responsibilities. | Universal Translation is canonical, but ACLI-named rendering/explanation modules contain reusable logic. | Responsibility restructuring required. |

## 4. Current Translation Responsibility Matrix

| Responsibility | Current owner | Evidence | Implementation status | Correctness assessment |
| --- | --- | --- | --- | --- |
| Natural-language semantic intake | UBTR / Universal Translation, invoked from ACLI routing | `translate_human_to_governance`; `conversational_cli_runtime.py` import and call | Implemented | Correct. ACLI initiates but does not own semantic intake. |
| Human -> Governance translation | UBTR / Universal Translation | `human_to_governance_translation_runtime.py`; Universal Translation integration docs | Implemented | Correct canonical ownership. |
| Semantic normalization | UBTR / Universal Translation | normalized intent in Universal Translation artifact | Implemented | Correct. |
| CSA generation / semantic lineage | UBTR / CSA | G2 final certification; UBTR / HIRR boundary | Implemented in G2 | Correct. CSA represents semantics; UBTR produces/links semantic meaning. |
| Platform technical representation | Platform runtimes / CSA / governance artifacts | Universal Translation artifact schema; Product 1 artifacts; replay artifacts | Implemented across runtimes | Correct when technical structure is not treated as natural-language translation. |
| Governance -> Human translation | UBTR / Universal Translation | `governance_to_human_translation_runtime.py`; integration docs | Implemented | Correct canonical ownership. |
| Technical -> Human explanation projection | UBTR / Universal Translation plus shared rendering model needed | `governance_to_human_translation_runtime.py`; `acli_human_friendly_explanation_runtime.py` | Partially implemented | Translation source is correct; shared rendering ownership is incomplete. |
| Human-facing explanation rendering | Currently ACLI compatibility/explanation runtime with UBTR primary input | `acli_human_friendly_explanation_runtime.py`; G2-11 doc | Implemented | Needs extraction of shared renderer/view model outside ACLI. |
| Optional provider-assisted explanation | ACLI-named advisory runtime | `acli_llm_assisted_explanation_runtime.py` | Implemented as advisory prototype | Misplaced naming/ownership risk; should become shared advisory explanation service consumed by adapters. |
| Conversation translation | UBTR for semantic turns; ACLI for terminal conversation lifecycle | `conversational_cli_runtime.py`; G3-02 certification | Partially implemented | Semantic translation correct; shared conversation model should move to Platform Core before new interfaces. |
| Replay translation | UBTR / Replay | Universal Translation replay references and hashes; replay reconstruction functions | Implemented | Correct. |
| Evidence translation | UBTR / Universal Translation, with product/evidence consumers | Governance -> Human translation accepts governance, replay, proposal, approval, worker, validation, ERR evidence | Implemented | Correct source, but presentation should be shared. |
| Confirmation classification | Currently ACLI runtime | `acli_operator_rendering_and_confirmation.py` | Implemented | Translation-adjacent and reusable; should move to shared human confirmation service. |
| Product 1 summary / audit wording | Product 1 artifacts | Product 1 decision/audit packet runtimes | Implemented as structured summaries | Correct as product-specific evidence, not canonical translation. |
| Future interface rendering | Not implemented | G3 service ownership refactor | Planned | Must consume shared translation/view models; no interface-local translators. |

## 5. UBTR Responsibility Assessment

UBTR currently owns the canonical translation responsibilities that matter most:

- Human -> Governance translation;
- normalized intent;
- ambiguity and confidence fields;
- deterministic fallback status;
- replay-visible translation references and hashes;
- Governance -> Human translation;
- authority-denial flags for translation artifacts;
- provider non-authority metadata;
- deterministic explanation input.

Evidence:

- `human_to_governance_translation_runtime.py` creates a hash-bound Universal
  Translation artifact with direction `HUMAN_TO_GOVERNANCE`, normalized intent,
  translated governance payload, ambiguity, confidence, provider metadata,
  deterministic fallback status, replay reference, and authority denial.
- `governance_to_human_translation_runtime.py` creates direction
  `GOVERNANCE_TO_HUMAN`, human-readable payload, rendered explanation sections,
  authoritative state references, replay hashes, and non-authority notice.
- `universal_translation_artifact_schema.py` restricts translation directions to
  Human -> Governance and Governance -> Human and denies governance, approval,
  execution, mutation, replay mutation, provider, and worker authority.
- `UNIVERSAL_TRANSLATION_RUNTIME_INTEGRATION_V1.md` explicitly marks Human ->
  Universal Translation -> HIRR and Governance -> Universal Translation ->
  Operator Explanation as canonical flows.

Assessment:

UBTR is canonical for translation, but the boundary should be made clearer by
renaming or wrapping reusable ACLI explanation/rendering modules as shared
Platform Translation or Platform View Model services.

## 6. CSA Responsibility Assessment

CSA does not own translation.

CSA owns canonical semantic representation and hash-bound lineage after UBTR has
translated human language or projected platform state. CSA is consumed by HIRR,
OCS, Product 1, explanation rendering, replay, and other Platform Core services.

Correct permanent responsibility:

- represent canonical semantics;
- carry semantic identity and lineage;
- support deterministic replay references and hashes;
- serve as the semantic input for downstream consumers.

Incorrect responsibility:

- interpreting natural language;
- generating human explanation prose;
- owning interface-specific rendering.

Assessment:

CSA ownership is correct.

## 7. OCS Responsibility Assessment

OCS does not own canonical human-facing translation.

OCS owns cognition orchestration and governance-mediated advisory cognition. It
may consume CSA and provider evidence, and Product 1 may consume OCS advisory
evidence, but OCS must not become a translation layer for human interfaces.

Correct permanent responsibility:

- determine cognition orchestration;
- assemble and consume context;
- preserve governance and provider boundaries;
- emit cognition/advisory evidence.

Incorrect responsibility:

- replacing UBTR Human -> Governance translation;
- replacing UBTR Governance -> Human projection;
- producing interface-specific translator logic.

Assessment:

OCS ownership remains correct. Human-facing explanation may include OCS evidence,
but the translation of governance/cognition state into human-facing explanation
belongs to UBTR / shared translation services, then adapter rendering.

## 8. ACLI Responsibility Assessment

ACLI is the first human interface to AiGOL. It is not the permanent owner of
shared translation capabilities.

Correct ACLI responsibilities:

- terminal input capture;
- command transport;
- adapter-local session references;
- adapter-specific rendering of shared platform view models;
- displaying translation, proposal, approval, provider, worker, replay, and
  Product 1 evidence;
- collecting explicit operator input.

Current ACLI-owned or ACLI-named responsibilities that are reusable:

| ACLI surface | Current behavior | Required correction |
| --- | --- | --- |
| `acli_operator_rendering_and_confirmation.py` | Renders session/turn state and classifies confirmations | Extract shared operator response model and confirmation classifier to Platform Core; keep terminal rendering in ACLI. |
| `acli_human_friendly_explanation_runtime.py` | Builds compatibility explanation sections, invokes Governance -> Human translation, composes operator output | Keep terminal adapter in ACLI; move shared explanation composition and section parity model to Platform Translation/View Model service. |
| `acli_llm_assisted_explanation_runtime.py` | Optional advisory provider wording over deterministic explanation | Move provider-assisted explanation service to shared advisory explanation platform capability; ACLI renders it. |
| ACLI proposal/approval/authorization renderers | Display proposal and approval evidence | Keep rendering adapter; shared proposal/approval/authorization view models belong to Platform Core. |
| ACLI provider rendering planned in G3-04 | Would display provider status and evidence | Must consume shared Provider Services view model, not own provider translation. |
| ACLI Product 1 rendering | Displays Product 1 evidence | Must consume Product 1 and shared translation/view-model outputs. |

Assessment:

ACLI is not currently the canonical translator, but it does contain reusable
translation-adjacent presentation logic. This requires responsibility
restructuring before future interfaces are implemented.

## 9. Product 1 Responsibility Assessment

Product 1 is correctly implemented as a consumer of Platform Services.

Product 1 owns:

- AI Decision Validator workflow;
- Decision Packet;
- OCS advisory attachment as product evidence;
- Audit Packet;
- Product 1 certification evidence.

Product 1 does not own:

- Human -> Governance translation;
- Governance -> Human translation;
- provider invocation;
- worker execution;
- interface rendering;
- shared explanation services.

Product 1 runtimes record product-specific summaries, assumptions, risks,
uncertainties, recommendations, audit summaries, OCS advisory references, replay
lineage, and non-authority flags. These are structured product artifacts, not
canonical translation services.

Assessment:

Product 1 ownership is correct. Future Product 1 UI or ACLI displays must consume
shared translation/view-model services rather than adding product-local
translator logic.

## 10. Architectural Gap Analysis

### 10.1 Duplicated Translation Logic

Core UBTR translation is not duplicated.

Translation-adjacent duplication risk exists in:

- ACLI human-friendly explanation compatibility sections;
- ACLI operator response lines;
- ACLI confirmation classification;
- ACLI LLM-assisted explanation wording;
- future provider rendering if implemented inside ACLI;
- future Product 1 rendering if implemented per-interface.

### 10.2 Misplaced Responsibilities

| Responsibility | Current owner / placement | Correct owner |
| --- | --- | --- |
| Shared explanation section model | ACLI human-friendly explanation runtime | Platform Translation / Shared View Model service |
| Shared operator response model | ACLI operator rendering runtime | Shared Platform View Model service |
| Confirmation classification | ACLI operator confirmation runtime | Shared Human Confirmation service, backed by UBTR where semantic prose is required |
| Provider-assisted explanation | ACLI LLM-assisted explanation runtime | Shared advisory explanation service under Provider/OCS governance |
| Provider evidence rendering model | Planned as ACLI rendering | Shared Provider Services view model plus interface adapters |
| Product evidence rendering model | Product and ACLI display surfaces | Product 1 artifact plus shared view model; adapters render only |

### 10.3 Missing Translation Capabilities

Missing or incomplete shared capabilities:

1. Platform Translation Service facade around existing Human -> Governance and
   Governance -> Human runtimes.
2. Shared Platform View Model service for translated governance, replay, provider,
   approval, worker, and Product 1 evidence.
3. Shared Confirmation Classification service usable by ACLI, Web, Mobile, REST,
   Voice, and future adapters.
4. Shared advisory explanation service that is not ACLI-named.
5. Interface adapter contract that forbids local semantic translation while
   allowing modality-specific rendering.

### 10.4 Reusable Translation Services

Reusable services already exist:

- Human -> Governance Translation Runtime;
- Governance -> Human Translation Runtime;
- Universal Translation Artifact Schema;
- Universal Translation Runtime Integration;
- G2-11 explanation rendering comparison evidence;
- replay reconstruction for translation artifacts.

### 10.5 Interface-Specific Translation

No future interface should implement its own semantic translator.

Allowed interface-specific behavior:

- terminal formatting;
- web layout;
- mobile layout;
- REST response serialization;
- voice capture and speech output;
- accessibility-specific presentation.

Forbidden interface-specific behavior:

- independent natural-language interpretation;
- independent platform-to-human semantic projection;
- independent confirmation semantics;
- independent explanation generation that bypasses UBTR;
- independent provider/worker summary meaning.

## 11. Canonical Translation Model

Canonical Human -> Platform flow:

```text
Human Interface
  ACLI / Web / Mobile / REST / Voice
    |
    v
Platform Translation Service
  UBTR Human -> Governance Translation
    |
    v
Universal Translation Artifact
    |
    v
CSA
    |
    v
HIRR / OCS / PPP / Product / Replay consumers
```

Canonical Platform -> Human flow:

```text
Governance / Replay / OCS / PPP / Product / Worker / Provider evidence
    |
    v
Platform Translation Service
  UBTR Governance -> Human Translation
    |
    v
Shared Platform View Model
    |
    v
Interface Adapter Rendering
  ACLI / Web / Mobile / REST / Voice
```

Canonical optional advisory wording flow:

```text
Authoritative deterministic translation
    |
    v
Optional OCS / Provider advisory explanation service
    |
    v
Shared transparency and non-authority evidence
    |
    v
Interface Adapter Rendering
```

Canonical ownership:

| Layer | Owns |
| --- | --- |
| UBTR / Platform Translation Service | Bidirectional semantic translation and canonical translation artifacts |
| CSA | Canonical semantic representation and lineage |
| OCS | Cognition orchestration and advisory evidence |
| Replay | Hash-bound evidence and reconstruction |
| Shared View Model service | Reusable translated presentation model |
| Interface adapters | Modality-specific rendering and input capture |
| Product 1 | Product-specific evidence artifacts |

## 12. Roadmap Impact

Roadmap status:

```text
Small-to-moderate responsibility corrections are required before future interfaces.
```

No major semantic restructuring is required because UBTR / Universal Translation
is already implemented and integrated.

However, future G3 work must not continue adding ACLI-named reusable
translation, explanation, provider rendering, Product 1 rendering, or
confirmation logic.

Roadmap impact:

- G3-04 provider rendering must use shared Provider Services view models.
- G3-05 worker rendering must use shared Worker Services view models.
- Future Web/Mobile/REST/Voice work must consume Platform Translation and shared
  view models.
- ACLI rendering modules should be treated as adapter implementations or
  compatibility wrappers, not permanent Platform Core owners.

## 13. Recommended Corrections

| Current owner | Correct owner | Migration strategy | Replay impact | Governance impact | Compatibility impact |
| --- | --- | --- | --- | --- | --- |
| ACLI human-friendly explanation compatibility model | Platform Translation / Shared View Model service | Create shared explanation/view-model service that wraps existing Governance -> Human translation and section parity logic; keep ACLI adapter as renderer. | Preserve current ACLI replay; add shared view-model reference/hash. | No authority transfer. | Keep ACLI compatibility renderer as fallback. |
| ACLI operator response model | Shared Platform View Model service | Extract session/turn/operator-action model; ACLI renders terminal lines from it. | Add shared view-model lineage before ACLI render hash. | No authority transfer. | Existing ACLI lines remain parity fallback. |
| ACLI confirmation classification | Shared Human Confirmation service | Move deterministic class set and classifier to Platform Core; interfaces submit operator input references. | Record classifier source, input hash, and interface adapter. | No approval authority transfer. | ACLI classifier remains compatibility adapter until parity certified. |
| ACLI LLM-assisted explanation | Shared advisory explanation service | Rename/re-home as provider advisory explanation under OCS/Provider governance; ACLI consumes output. | Preserve provider explanation evidence and non-authority flags. | Provider output remains advisory. | Existing ACLI runtime can wrap shared service during migration. |
| Planned ACLI provider rendering | Shared Provider Services view model | Implement provider status/comparison/cost/failure view model once. | Provider view-model hash becomes interface-independent replay evidence. | Provider governance remains Platform Core. | ACLI-specific terminal rendering remains adapter-only. |
| Product 1 display summaries in interfaces | Product 1 artifact + shared view model | Product 1 emits structured artifacts; shared view model translates for interface rendering. | Product artifact hashes remain source; view-model hash added. | Product remains consumer. | Existing Product 1 summaries remain product evidence. |

## 14. Future Interface Impact

| Future interface | Translator required? | Correct model |
| --- | --- | --- |
| Web | No semantic translator. | Web consumes UBTR translation artifacts and shared view models; renders web UI. |
| Mobile | No semantic translator. | Mobile consumes shared translated view models; renders mobile UI. |
| REST | No semantic translator. | REST serializes shared platform translation/view-model artifacts. |
| Voice | No semantic translator. | Voice performs modality capture/output, then uses UBTR for semantics and shared view models for response content. |
| Future adapters | No semantic translator. | Adapters may format, localize, or transport shared outputs but must not reinterpret meaning. |

## 15. Recommended Next Implementation Batch

Recommended next batch:

`G3_04_PHASE_2_5_PLATFORM_TRANSLATION_AND_VIEW_MODEL_OWNERSHIP_REFACTOR_V1`

Scope:

- define a shared Platform Translation Service facade over existing Universal
  Translation runtimes;
- define shared platform-to-human view-model artifacts;
- reclassify ACLI explanation/rendering runtimes as adapter or compatibility
  wrappers;
- create migration criteria for moving confirmation classification to a shared
  Human Confirmation service;
- ensure G3-04 provider rendering consumes shared Provider Services view models;
- preserve all existing replay artifacts, hashes, compatibility fallbacks, and
  non-authority flags.

Do not implement:

- new semantic translation logic;
- new CSA semantics;
- provider invocation;
- worker execution;
- Product 1 behavior changes;
- Web/Mobile/Voice adapters.

## 16. Final Determination

UBTR / Universal Translation is already the canonical bidirectional translation
layer for Human -> Governance and Governance -> Human paths.

The architecture is not inconclusive.

The remaining issue is responsibility placement: reusable human-facing
translation, explanation, confirmation, and view-model capabilities must be
centralized as Platform Services instead of remaining ACLI-owned by name or
implementation placement.

Final verdict: TRANSLATION_RESPONSIBILITY_RESTRUCTURING_REQUIRED
