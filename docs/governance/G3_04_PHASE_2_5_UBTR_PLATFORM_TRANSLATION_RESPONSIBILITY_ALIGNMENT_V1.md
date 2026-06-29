# G3-04 Phase 2.5 UBTR Platform Translation Responsibility Alignment V1

Status: architectural responsibility alignment.

Final verdict: UBTR_TRANSLATION_ALIGNMENT_REQUIRED

## 1. Executive Summary

Platform Core Generation 2 is certified.

Recent Generation 3 audits established:

- Generation 3 responsibility restructuring is required;
- existing Provider Services must be reused and extended, not duplicated;
- UBTR / Universal Translation is the canonical bidirectional translation layer;
- ACLI is the first human interface adapter and must remain an adapter only.

This alignment audit verifies the ownership of reusable human-facing
translation, explanation, confirmation, rendering, and shared view-model
responsibilities.

The result is nuanced:

- Core Human -> Platform translation is already correctly owned by UBTR.
- Core Platform -> Human translation is already correctly owned by UBTR.
- CSA remains representation and lineage, not translation ownership.
- OCS remains cognition and governance orchestration, not interface translation.
- ACLI correctly owns terminal input/output adaptation.
- Several reusable presentation responsibilities are currently implemented in
  ACLI-named modules and should be realigned into Shared Platform Services while
  preserving ACLI as the first adapter.

No runtime relocation is performed by this artifact.

## 2. Canonical Translation Responsibility Model

### 2.1 Human -> Platform Translation

Canonical flow:

```text
Human interface adapter
  ACLI / Web / Mobile / REST / Voice / future adapter
    |
    v
UBTR / Universal Translation
  Human -> Governance translation
    |
    v
Universal Translation Artifact
    |
    v
CSA semantic representation
    |
    v
HIRR / OCS / PPP / Product / Replay consumers
```

Permanent ownership:

| Responsibility | Canonical owner |
| --- | --- |
| human input capture | Interface adapter |
| natural-language semantic interpretation | UBTR |
| normalized intent | UBTR |
| ambiguity and confidence translation | UBTR |
| canonical semantic representation | CSA |
| semantic lineage | UBTR / CSA / Replay |
| workflow/lifecycle orchestration | HIRR / lifecycle runtimes |
| cognition orchestration | OCS |

### 2.2 Platform -> Human Translation

Canonical flow:

```text
Governance / Replay / OCS / PPP / Provider / Worker / Product evidence
    |
    v
UBTR / Universal Translation
  Governance -> Human translation
    |
    v
Shared Platform View Model
    |
    v
Interface adapter rendering
  ACLI / Web / Mobile / REST / Voice / future adapter
```

Permanent ownership:

| Responsibility | Canonical owner |
| --- | --- |
| governance-state-to-human translation | UBTR |
| human-readable platform explanation payload | UBTR / Shared Platform Translation Service |
| reusable response sections and view model | Shared Platform Services |
| terminal formatting | ACLI |
| web layout | Web adapter |
| mobile layout | Mobile adapter |
| REST serialization | REST adapter |
| voice capture/output adaptation | Voice adapter |

### 2.3 Compatibility Rule

Existing ACLI-named translation-adjacent modules may remain as compatibility
wrappers or first-adapter implementations while shared Platform Services are
introduced.

They must not become permanent owners of reusable translation, explanation,
confirmation, provider rendering, worker rendering, replay presentation, or
governance presentation models.

## 3. Responsibility Matrix

| Responsibility | Current implementation owner | Canonical owner | Evidence | Correctness assessment |
| --- | --- | --- | --- | --- |
| Human-to-platform translation | UBTR runtime invoked from ACLI routing | UBTR | `human_to_governance_translation_runtime.py`; `conversational_cli_runtime.py`; Universal Translation integration docs | CORRECT |
| Platform-to-human translation | Governance-to-Human translation runtime | UBTR | `governance_to_human_translation_runtime.py`; `universal_translation_runtime_integration.py` | CORRECT |
| CSA semantic representation | CSA / G2 semantic platform core | CSA | G2 final certification; UBTR/HIRR boundary | CORRECT |
| Explanation rendering source | ACLI human-friendly explanation runtime consumes UBTR Governance -> Human output | UBTR for translation; Shared Platform Services for reusable rendering model; ACLI for terminal rendering | `acli_human_friendly_explanation_runtime.py`; G2-11 explanation migration | PLATFORM_ALIGNMENT_REQUIRED |
| Compatibility explanation sections | ACLI human-friendly explanation runtime | Compatibility-only until shared view model parity exists | G2-11 fallback-visible compatibility fields | COMPATIBILITY_ONLY |
| Optional provider-assisted explanation | ACLI-named LLM-assisted explanation runtime | Shared advisory explanation service under OCS / Provider governance | `acli_llm_assisted_explanation_runtime.py`; Universal Translation integration imports it | PLATFORM_ALIGNMENT_REQUIRED |
| Operator response lines | ACLI operator rendering runtime | Shared Platform View Model for reusable content; ACLI for terminal formatting | `acli_operator_rendering_and_confirmation.py` | PLATFORM_ALIGNMENT_REQUIRED |
| Confirmation classification | ACLI operator confirmation runtime | Shared Human Confirmation service; UBTR if semantic prose interpretation is needed | `classify_operator_confirmation`; G3 responsibility audit | PLATFORM_ALIGNMENT_REQUIRED |
| Confirmation rendering | ACLI operator rendering runtime | Shared Platform View Model plus ACLI adapter | `render_operator_response` sections and required action lines | PLATFORM_ALIGNMENT_REQUIRED |
| Proposal rendering | ACLI bridge / CLI rendering surfaces | Shared proposal view model plus ACLI adapter | G3 responsibility audit; ACLI proposal approval bridge | PLATFORM_ALIGNMENT_REQUIRED |
| Approval rendering | ACLI bridge / CLI rendering surfaces | Shared approval view model plus ACLI adapter | G3-02 certification; approval bridge evidence | PLATFORM_ALIGNMENT_REQUIRED |
| Authorization rendering | ACLI authorization bridge / CLI surfaces | Shared authorization view model plus ACLI adapter | `acli_authorization_bridge.py`; G3-02 certification | PLATFORM_ALIGNMENT_REQUIRED |
| Authorization readiness evidence | ACLI authorization bridge runtime | Authorization service / Platform Core | G3 responsibility audit identifies shared authorization readiness candidate | PLATFORM_ALIGNMENT_REQUIRED |
| Human-readable summaries | Mixed: governance translation, ACLI renderers, Product 1 summaries | UBTR for translation; Shared View Model for reusable summaries; products for product-specific evidence | Governance-to-Human runtime; Product 1 decision/audit packet runtimes | PLATFORM_ALIGNMENT_REQUIRED |
| Replay presentation | ACLI / operator-facing renderers | Replay service plus Shared View Model; adapters render | G2 final replay guarantees; G3 platform-service refactor | PLATFORM_ALIGNMENT_REQUIRED |
| Governance presentation | Governance-to-Human translation plus ACLI renderers | UBTR / Governance / Shared View Model | `governance_to_human_translation_runtime.py`; ACLI explanation runtime | PLATFORM_ALIGNMENT_REQUIRED |
| Shared conversation presentation model | ACLI conversational/session runtimes | Shared Platform conversation/view model plus ACLI adapter | G3 responsibility placement audit | PLATFORM_ALIGNMENT_REQUIRED |
| ACLI terminal formatting | ACLI | ACLI | ACLI adapter responsibility in G3 refactor | ACLI_SPECIFIC |
| ACLI command transport | ACLI | ACLI | G2 command boundary certification; G3 refactor | ACLI_SPECIFIC |
| ACLI local session reference display | ACLI | ACLI adapter over shared session model | G3-02 certification | ACLI_SPECIFIC with future shared model dependency |
| Product 1 Decision Packet summaries | Product 1 | Product 1 artifact; shared view model for cross-interface display | Product 1 decision packet runtime | CORRECT |
| Product 1 Audit Packet summaries | Product 1 | Product 1 artifact; shared view model for cross-interface display | Product 1 audit packet runtime | CORRECT |
| Provider status rendering planned for G3-04 | Not yet canonical; ACLI rendering risk | Shared Provider Services view model plus adapters | G3 responsibility audit; G3-04 reuse audit | PLATFORM_ALIGNMENT_REQUIRED |
| Worker status rendering planned for G3-05 | Not yet canonical; ACLI rendering risk | Shared Worker Services view model plus adapters | G3 responsibility audit | PLATFORM_ALIGNMENT_REQUIRED |

## 4. Alignment Assessment

| Responsibility | Alignment classification | Reason |
| --- | --- | --- |
| Human-to-platform translation | CORRECT | UBTR runtime already produces replay-visible Universal Translation artifacts. |
| Platform-to-human translation | CORRECT | Governance -> Human translation runtime already produces human-readable payloads and hashes. |
| CSA representation | CORRECT | CSA represents canonical semantics but does not translate. |
| OCS cognition explanation context | CORRECT | OCS evidence may be translated, but OCS does not own translation. |
| ACLI terminal input capture | ACLI_SPECIFIC | Terminal adapter concern. |
| ACLI terminal output formatting | ACLI_SPECIFIC | Formatting is adapter-specific if it consumes shared content. |
| Explanation section model | PLATFORM_ALIGNMENT_REQUIRED | Reusable across interfaces and currently ACLI-named. |
| Operator response model | PLATFORM_ALIGNMENT_REQUIRED | Reusable session/turn/action content should not be terminal-specific. |
| Confirmation classification | PLATFORM_ALIGNMENT_REQUIRED | Future interfaces need the same classification semantics. |
| Proposal rendering model | PLATFORM_ALIGNMENT_REQUIRED | Proposal evidence is reusable and should render from shared model. |
| Approval rendering model | PLATFORM_ALIGNMENT_REQUIRED | Approval evidence is reusable and should render from shared model. |
| Authorization rendering model | PLATFORM_ALIGNMENT_REQUIRED | Authorization readiness is platform evidence, not ACLI-owned. |
| Replay presentation model | PLATFORM_ALIGNMENT_REQUIRED | Replay presentation must be shared and adapter-rendered. |
| Governance presentation model | PLATFORM_ALIGNMENT_REQUIRED | Governance explanation should use UBTR and shared view models. |
| Provider rendering model | PLATFORM_ALIGNMENT_REQUIRED | Provider evidence belongs to Provider Services; adapters render. |
| Worker rendering model | PLATFORM_ALIGNMENT_REQUIRED | Worker evidence belongs to Worker Services; adapters render. |
| ACLI compatibility explanation fallback | COMPATIBILITY_ONLY | Keep visible until shared parity is certified. |
| Product 1 internal evidence summaries | CORRECT | Product-specific artifacts may own product evidence summaries. |

## 5. Architectural Corrections

### 5.1 Platform Translation Service Facade

Why:

The implementation already has Human -> Governance and Governance -> Human
translation runtimes, but future interfaces need a single canonical Platform
Translation entrypoint rather than importing ACLI-adjacent integration paths.

Target owner:

UBTR / Shared Platform Translation Service.

Implementation strategy:

- create a thin facade over existing Universal Translation runtimes;
- preserve existing artifact schemas and replay hashes;
- expose interface-neutral request and response contracts;
- keep ACLI as one adapter caller.

Replay impact:

- add facade replay lineage references while preserving current Universal
  Translation artifact references and hashes.

Governance impact:

- no authority transfer; translation remains non-authoritative.

Compatibility impact:

- existing ACLI routing integration remains as compatibility wrapper during
  migration.

### 5.2 Shared Platform View Model Service

Why:

Operator response lines, explanation sections, replay summaries, governance
summaries, proposal status, approval state, authorization readiness, provider
state, and worker state are reusable by Web, Mobile, REST, Voice, and future
interfaces.

Target owner:

Shared Platform Services.

Implementation strategy:

- define hash-bound view-model artifacts generated from existing governance,
  replay, proposal, approval, authorization, provider, worker, Product 1, and
  UBTR translation artifacts;
- make ACLI render terminal output from the shared view model;
- preserve adapter-specific formatting outside the shared model.

Replay impact:

- add shared view-model reference/hash before adapter-rendered output hash.

Governance impact:

- no new authority; view models are presentation evidence only.

Compatibility impact:

- ACLI current output remains a parity target and compatibility fallback.

### 5.3 Shared Human Confirmation Service

Why:

Confirmation classes such as confirm, reject, clarify, modify, continue, and
unknown are not terminal-specific. Future interfaces must not reimplement them.

Target owner:

Shared Platform Services, with UBTR involvement for natural-language semantic
confirmation where deterministic command matching is insufficient.

Implementation strategy:

- extract the confirmation class set and deterministic classifier into a shared
  service;
- record interface source, input hash, classifier source, CSA/translation
  reference where available, and non-authority flags;
- ACLI calls the shared classifier and renders the result.

Replay impact:

- existing ACLI confirmation replay remains compatibility evidence;
- new shared classifier artifact becomes primary after parity certification.

Governance impact:

- classification does not grant approval or authorization.

Compatibility impact:

- ACLI classifier remains rollback path until shared classifier parity is proven.

### 5.4 Shared Advisory Explanation Service

Why:

Optional provider-assisted explanation is currently ACLI-named, but provider
wording over deterministic translation is reusable by all human interfaces.

Target owner:

Shared advisory explanation service under OCS / Provider governance.

Implementation strategy:

- preserve deterministic UBTR Governance -> Human translation as the required
  source;
- treat provider wording as advisory only;
- expose shared provider explanation transparency artifacts;
- have ACLI render the shared advisory explanation.

Replay impact:

- preserve provider explanation request/response hashes and non-authority flags;
- add shared advisory explanation identity.

Governance impact:

- provider output remains advisory and cannot approve, authorize, execute, or
  mutate.

Compatibility impact:

- ACLI LLM-assisted explanation runtime can wrap the shared service until
  callsites migrate.

### 5.5 Shared Proposal, Approval, And Authorization View Models

Why:

Proposal, approval, and authorization evidence are shared Platform Core concerns
exercised first through ACLI. They must be reusable by future interfaces.

Target owner:

Proposal / Approval / Authorization Platform Services plus Shared View Model
service.

Implementation strategy:

- define interface-neutral proposal, approval, and authorization view-model
  artifacts;
- preserve existing ACLI bridge artifacts as source evidence;
- adapters render only.

Replay impact:

- add view-model reference/hash linked to existing bridge artifact hashes.

Governance impact:

- no approval or authorization authority changes.

Compatibility impact:

- ACLI bridge rendering remains compatibility output.

## 6. Roadmap Impact

Roadmap classification:

```text
minor-to-moderate Platform Core alignment required
```

No significant semantic restructuring is required because UBTR already owns
canonical bidirectional translation.

No runtime change is required by this audit itself.

Required roadmap changes before additional interface or provider rendering work:

1. introduce a Platform Translation Service facade over existing UBTR /
   Universal Translation runtimes;
2. introduce shared platform-to-human view-model artifacts;
3. classify existing ACLI rendering/explanation modules as adapter or
   compatibility wrappers;
4. migrate confirmation classification into a shared Human Confirmation service
   after parity evidence;
5. require G3-04 provider rendering to consume shared Provider Services view
   models;
6. require G3-05 worker rendering to consume shared Worker Services view models;
7. prevent future Web, Mobile, REST, Voice, or Product interfaces from
   implementing local translation logic.

## 7. Recommended Next Implementation Batch

Recommended next batch:

`G3_04_PHASE_2_6_PLATFORM_TRANSLATION_FACADE_AND_SHARED_VIEW_MODELS_V1`

Scope:

- implement a thin Platform Translation facade over existing Human -> Governance
  and Governance -> Human runtimes;
- implement shared, hash-bound platform-to-human view-model artifacts for
  explanation, governance, replay, proposal, approval, and authorization state;
- keep ACLI as a terminal adapter over those artifacts;
- preserve existing ACLI replay and compatibility output;
- do not invoke providers;
- do not execute workers;
- do not mutate repositories;
- do not change approval or authorization authority.

Certification criteria:

- UBTR remains the canonical translation owner;
- shared view-model artifacts are interface-neutral;
- ACLI-specific rendering is adapter-only;
- compatibility output remains replay-visible;
- all artifacts deny provider, worker, approval, execution, governance mutation,
  and replay mutation authority.

## 8. Final Determination

The current architecture confirms UBTR as the canonical translation layer.

Architectural alignment is still required because reusable explanation,
confirmation, rendering, replay presentation, governance presentation, proposal,
approval, authorization, provider, and worker view-model responsibilities must
belong to Platform Core rather than ACLI-named modules.

This is an alignment program, not a semantic rewrite.

Final verdict: UBTR_TRANSLATION_ALIGNMENT_REQUIRED
