# Platform UX vs Interface UX Architecture Audit V1

Status: architectural UX responsibility audit.

Final verdict: PLATFORM_UX_ALIGNMENT_REQUIRED

## 1. Executive Summary

Platform Core Generation 2 is certified.

Recent Generation 3 audits established:

- UBTR is the canonical bidirectional translation layer;
- Platform Services are implemented once and reused everywhere;
- ACLI is the first human interface adapter;
- reusable translation and platform representation responsibilities must not
  become ACLI-owned merely because ACLI was the first operational interface.

This audit defines the permanent boundary between Platform UX and Interface UX.

Conclusion:

- Platform UX exists and must be owned by Platform Core.
- Interface UX exists and must remain owned by interface adapters.
- UBTR owns bidirectional semantic translation and human-facing semantic
  projection.
- Shared Platform Services own reusable view models, reusable presentation
  models, and cross-interface human-facing evidence structures.
- ACLI legitimately owns terminal input/output adaptation, command transport,
  terminal formatting, prompts, progress indicators, and local terminal
  interaction behavior.
- Several reusable Platform UX responsibilities are currently implemented in
  ACLI-named modules and require architectural alignment before Web, Mobile,
  REST, Voice, or future interfaces are added.

No runtime code is changed by this audit.

## 2. Canonical UX Architecture

Permanent architecture:

```text
Human
  |
  v
Interface Adapter
  ACLI / Web / Mobile / REST / Voice / future adapter
  |
  v
UBTR Platform UX
  Human -> Platform translation
  Platform -> Human translation
  canonical human-facing semantic projection
  |
  v
CSA
  canonical semantic representation and lineage
  |
  v
OCS
  cognition and governance orchestration
  |
  v
Platform Services
  replay, governance, provider, worker, proposal, approval,
  authorization, Product services, shared view models
```

## 3. Canonical Platform UX

Platform UX is reusable human-facing communication independent of interface
technology.

Platform UX belongs to Platform Core when:

- the same meaning must be presented consistently across ACLI, Web, Mobile,
  REST, Voice, or future interfaces;
- the content explains governance, replay, approval, authorization, provider,
  worker, Product 1, or semantic state;
- the content is generated from UBTR, CSA, OCS, replay, governance, or other
  Platform Services evidence;
- the content affects human understanding of platform state, required action,
  limitations, fallback, or authority boundaries.

Canonical Platform UX owners:

| Platform UX capability | Canonical owner |
| --- | --- |
| human-to-platform semantic translation | UBTR |
| platform-to-human semantic translation | UBTR |
| canonical explanation payload | UBTR / Platform Translation Service |
| reusable explanation sections | Shared Platform UX / View Model service |
| confirmation semantics | Shared Human Confirmation service, UBTR-backed where needed |
| proposal wording model | Proposal service / Shared Platform UX |
| approval wording model | Approval service / Shared Platform UX |
| authorization wording model | Authorization service / Shared Platform UX |
| replay explanation model | Replay service / Shared Platform UX |
| governance explanation model | Governance service / UBTR / Shared Platform UX |
| provider status and failure wording model | Provider Services / Shared Platform UX |
| worker status and execution wording model | Worker Services / Shared Platform UX |
| Product 1 presentation model | Product 1 artifacts / Shared Platform UX |
| shared conversation presentation model | Shared Platform conversation/view model |

## 4. Canonical Interface UX

Interface UX is technology-specific interaction and presentation.

Interface UX belongs to adapters when:

- it depends on the input/output modality;
- it controls layout, formatting, pacing, navigation, or device interaction;
- it does not reinterpret platform meaning;
- it renders a shared Platform UX artifact without changing its semantic
  content.

Canonical Interface UX owners:

| Interface UX capability | Canonical owner |
| --- | --- |
| ACLI command history | ACLI |
| ACLI autocomplete | ACLI |
| ACLI multiline editing | ACLI |
| ACLI terminal formatting | ACLI |
| ACLI ANSI colors | ACLI |
| ACLI keyboard shortcuts | ACLI |
| ACLI progress indicators | ACLI |
| ACLI paging | ACLI |
| ACLI prompt rendering | ACLI |
| Web buttons/dialogs/cards/layout | Web adapter |
| Mobile gestures/native navigation/notifications | Mobile adapter |
| REST serialization/status envelopes | REST adapter |
| Voice speech recognition/synthesis/interruption handling | Voice adapter |

## 5. Responsibility Matrix

| Capability | Current owner | Canonical owner | Evidence | Justification |
| --- | --- | --- | --- | --- |
| Human-to-platform translation | UBTR runtime invoked by ACLI routing | UBTR | `human_to_governance_translation_runtime.py`; Universal Translation integration | Same semantic interpretation is required by every interface. |
| Platform-to-human translation | Governance-to-Human translation runtime | UBTR | `governance_to_human_translation_runtime.py` | Same platform meaning must be projected consistently to humans. |
| Explanation generation | UBTR translation plus ACLI explanation runtime | UBTR / Shared Platform UX | G2-11 explanation migration; ACLI human-friendly explanation runtime | Explanation content is cross-interface; terminal formatting is ACLI-specific. |
| Compatibility explanation sections | ACLI human-friendly explanation runtime | Compatibility-only until shared parity | G2-11 fallback evidence | Keep visible for replay and rollback, not permanent ownership. |
| Optional provider-assisted explanation | ACLI-named LLM-assisted explanation runtime | Shared advisory explanation service under OCS / Provider governance | ACLI LLM-assisted explanation runtime; translation audit | Provider wording can be useful across interfaces and must remain advisory. |
| Confirmation wording | ACLI operator rendering runtime | Shared Platform UX / Human Confirmation service | `acli_operator_rendering_and_confirmation.py` | The required action and confirmation meaning are reusable. |
| Confirmation classification | ACLI operator confirmation runtime | Shared Human Confirmation service | `classify_operator_confirmation` | Confirm/reject/clarify/modify/continue/unknown are not terminal-specific. |
| Proposal wording | ACLI proposal/approval bridge and CLI surfaces | Proposal service / Shared Platform UX | G3 responsibility audit; ACLI proposal approval bridge | Proposal meaning should be identical across interfaces. |
| Approval wording | ACLI approval bridge and CLI surfaces | Approval service / Shared Platform UX | G3-02 certification; approval runtime surfaces | Approval state must be consistently explained. |
| Authorization wording | ACLI authorization bridge and CLI surfaces | Authorization service / Shared Platform UX | `acli_authorization_bridge.py`; G3-02 certification | Authorization readiness is platform evidence. |
| Human-readable summaries | Mixed: UBTR, ACLI, Product 1 | UBTR / Shared Platform UX / Product-specific artifacts | Governance-to-Human runtime; Product 1 packets | Reusable summaries need shared models; product summaries remain product evidence. |
| Shared conversation model | ACLI conversational development session | Shared Platform Services | G3 responsibility placement audit | Web/Mobile/Voice need the same conversation semantics. |
| Shared presentation model | ACLI rendering modules | Shared Platform UX | UBTR translation alignment audit | Presentation meaning is reusable; rendering mechanics are adapter-specific. |
| Replay explanations | ACLI/operator renderers and replay runtimes | Replay service / Shared Platform UX | G2 final replay guarantees; replay command/runtime surfaces | Replay meaning must be consistent across all interfaces. |
| Governance explanations | Governance-to-Human translation plus ACLI renderers | UBTR / Governance / Shared Platform UX | Governance-to-Human translation runtime | Governance meaning is platform-owned. |
| Provider status rendering | Planned ACLI provider rendering risk | Provider Services / Shared Platform UX | G3 responsibility audit; Provider Services reuse audit | Provider evidence belongs to Provider Services; adapters render it. |
| Worker status rendering | Planned ACLI worker rendering risk | Worker Services / Shared Platform UX | G3 responsibility audit | Worker evidence belongs to Worker Services; adapters render it. |
| Product 1 evidence rendering | Product 1 artifacts and ACLI displays | Product 1 / Shared Platform UX / adapter rendering | Product 1 packet and audit runtimes | Product owns artifacts; reusable display model should be shared. |
| ACLI terminal formatting | ACLI | ACLI | G3 platform service ownership refactor | Terminal formatting is interface-specific. |
| ACLI prompt rendering | ACLI | ACLI | ACLI interface role | Prompt shape is terminal interaction. |
| ACLI progress indicators | ACLI / CLI rendering | ACLI | CLI interaction tests and renderers | Progress display mechanics are terminal-specific. |
| ACLI command history/autocomplete/paging | ACLI or future ACLI implementation | ACLI | Interface UX definition | These are terminal affordances, not Platform UX. |
| Web cards/dialogs/buttons | Not implemented | Web adapter | Interface UX definition | Device/layout-specific. |
| Mobile gestures/navigation | Not implemented | Mobile adapter | Interface UX definition | Device-specific. |
| REST status envelope | Not implemented | REST adapter | Interface UX definition | Transport-specific serialization. |
| Voice speech and interruption handling | Not implemented | Voice adapter | Interface UX definition | Modality-specific. |

## 6. Platform UX Inventory

Reusable human-facing Platform UX capabilities that belong to Platform Core:

1. Human -> Platform semantic translation.
2. Platform -> Human semantic translation.
3. Canonical explanation payloads.
4. Explanation section model.
5. Required-action wording.
6. Confirmation semantic classes and classifier evidence.
7. Proposal presentation model.
8. Approval presentation model.
9. Authorization readiness presentation model.
10. Replay explanation model.
11. Governance explanation model.
12. Provider status, comparison, cost, rate-limit, and failure explanation model.
13. Worker status, lifecycle, selection, execution, and result explanation model.
14. Shared conversation state presentation model.
15. Shared session state presentation model.
16. Product 1 evidence presentation model.
17. Non-authority and boundary explanation model.
18. Fallback and compatibility explanation model.

These capabilities must be deterministic, replay-visible where they produce
artifacts, hash-bound where persisted, and non-authoritative.

## 7. Interface UX Inventory

Interface-specific capabilities that belong to adapters:

### 7.1 ACLI

- command input transport;
- command history;
- autocomplete;
- multiline editing;
- terminal formatting;
- ANSI colors;
- keyboard shortcuts;
- progress indicators;
- paging;
- prompt rendering;
- terminal-specific error layout;
- terminal-specific rendering of shared Platform UX artifacts.

### 7.2 Web

- buttons;
- dialogs;
- cards;
- responsive layout;
- browser navigation;
- pointer and keyboard UI affordances;
- web-specific rendering of shared Platform UX artifacts.

### 7.3 Mobile

- gestures;
- native navigation;
- notifications;
- mobile layout;
- offline/foreground/background presentation behavior;
- mobile-specific rendering of shared Platform UX artifacts.

### 7.4 REST

- request/response serialization;
- status envelopes;
- pagination envelopes;
- error-code mapping;
- machine-readable transport of shared Platform UX artifacts.

### 7.5 Voice

- speech recognition;
- speech synthesis;
- interruption handling;
- turn-taking;
- voice-specific rendering of shared Platform UX artifacts.

## 8. Architectural Corrections

| Misplaced / at-risk responsibility | Current owner | Canonical owner | Justification | Compatibility impact | Replay impact | Governance impact |
| --- | --- | --- | --- | --- | --- | --- |
| Explanation section model | ACLI human-friendly explanation runtime | Shared Platform UX with UBTR translation input | Reusable by every interface | Keep ACLI output as parity fallback | Add shared view-model hash before adapter render hash | No authority change |
| Operator response model | ACLI operator rendering runtime | Shared Platform UX | Session, turn, CSA, required action, and non-authority flags are cross-interface | ACLI lines remain terminal rendering | Record shared model reference/hash | No authority change |
| Confirmation classification | ACLI operator confirmation runtime | Shared Human Confirmation service | Confirmation semantics are cross-interface | ACLI classifier remains compatibility fallback until parity | Record classifier source, input hash, interface id | Does not grant approval |
| Provider-assisted explanation | ACLI-named LLM-assisted explanation runtime | Shared advisory explanation service under OCS / Provider governance | Advisory explanation is reusable and provider-governed | ACLI wrapper may remain | Preserve provider explanation replay and add shared service identity | Provider output remains advisory |
| Proposal/approval/authorization wording | ACLI bridge/rendering surfaces | Proposal, Approval, Authorization services plus Shared Platform UX | These are platform states rendered by many interfaces | ACLI rendering remains adapter | Add shared view-model lineage | No approval/authorization transfer |
| Replay explanation | ACLI/operator renderers | Replay service plus Shared Platform UX | Replay meaning is platform-owned | Existing CLI replay output remains adapter | Shared replay view-model hash | Replay remains read-only |
| Governance explanation | ACLI explanation/renderers | UBTR / Governance / Shared Platform UX | Governance meaning is constitutional platform state | Existing ACLI explanation remains fallback | Link to Governance -> Human translation hash | No governance authority transfer |
| Provider rendering | Planned ACLI-specific path | Provider Services plus Shared Platform UX | Provider state must be reusable by Product 1 and future interfaces | ACLI provider rendering becomes adapter-only | Provider view-model hash becomes source | Provider governance remains Platform Core |
| Worker rendering | Planned ACLI-specific path | Worker Services plus Shared Platform UX | Worker state must be reusable by future interfaces | ACLI worker rendering becomes adapter-only | Worker view-model hash becomes source | Worker authority unchanged |
| Product 1 display model | Product/ACLI displays | Product 1 artifacts plus Shared Platform UX | Product evidence should render consistently across interfaces | Product summaries remain source evidence | Product view-model hash added | Product remains consumer |

## 9. Future Interface Impact

### 9.1 ACLI

ACLI remains the first human interface adapter.

It should:

- capture terminal input;
- invoke UBTR / Platform UX services;
- render shared Platform UX artifacts in terminal form;
- preserve replay references and adapter render hashes.

It should not:

- own reusable explanation meaning;
- own confirmation semantics;
- own provider or worker presentation models;
- reinterpret Platform UX artifacts.

### 9.2 Web

Web can be introduced without duplicating UX logic if it consumes shared Platform
UX artifacts and implements only layout and interaction affordances.

### 9.3 Mobile

Mobile can consume the same Platform UX artifacts and render them through native
navigation, notifications, and mobile layouts without reimplementing meaning.

### 9.4 REST

REST can expose shared Platform UX artifacts directly as machine-readable
payloads, using transport-specific status envelopes without local translation.

### 9.5 Voice

Voice can use speech recognition and speech synthesis as modality adapters while
consuming the same UBTR translation and shared Platform UX response models.

### 9.6 Future Interfaces

Future interfaces inherit the same rule:

```text
Adapters may render, serialize, speak, paginate, or arrange Platform UX.
Adapters may not redefine Platform UX meaning.
```

## 10. Roadmap Impact

Roadmap classification:

```text
Platform UX alignment required before additional interface expansion.
```

No semantic rewrite is required.

No runtime change is required by this audit itself.

Required roadmap adjustments:

1. Introduce a shared Platform UX / View Model service.
2. Keep UBTR as the canonical source of platform-to-human semantic content.
3. Treat ACLI explanation and rendering modules as first-adapter or
   compatibility wrappers.
4. Move confirmation semantics into a shared Human Confirmation service after
   parity certification.
5. Require G3-04 provider rendering to consume shared Provider UX models.
6. Require G3-05 worker rendering to consume shared Worker UX models.
7. Require Web, Mobile, REST, Voice, and future interfaces to consume Platform
   UX artifacts instead of recreating explanation, confirmation, replay,
   governance, provider, worker, or Product UX logic.

## 11. Recommended Next Implementation Batch

Recommended next batch:

`G3_04_PHASE_2_6_PLATFORM_UX_VIEW_MODEL_FOUNDATION_V1`

Scope:

- define deterministic shared Platform UX view-model artifacts;
- wrap existing UBTR Governance -> Human translation output as the semantic
  source for human-facing platform explanations;
- create view models for explanation, required action, governance, replay,
  proposal, approval, authorization, and non-authority boundaries;
- keep ACLI terminal rendering as an adapter over the shared view model;
- preserve existing ACLI output as compatibility evidence;
- do not invoke providers;
- do not invoke workers;
- do not mutate repositories;
- do not change approval, authorization, governance, replay, provider, or worker
  authority.

Certification criteria:

- Platform UX artifacts are interface-neutral;
- ACLI renders without owning reusable meaning;
- replay records shared view-model hashes and ACLI render hashes separately;
- future interfaces can consume the same artifacts;
- all Platform UX artifacts deny authority transfer.

## 12. Final Determination

The architecture supports a permanent Platform UX vs Interface UX boundary, but
current implementation placement requires alignment because several reusable
human-facing capabilities remain in ACLI-named modules.

Final verdict: PLATFORM_UX_ALIGNMENT_REQUIRED
