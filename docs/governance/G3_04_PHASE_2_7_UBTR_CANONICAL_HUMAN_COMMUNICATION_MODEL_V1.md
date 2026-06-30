# G3-04 Phase 2.7 UBTR Canonical Human Communication Model V1

Status: canonical communication model.

Final verdict: UBTR_CANONICAL_HUMAN_COMMUNICATION_MODEL_READY

## 1. Executive Summary

Platform Core Generation 2 is certified.

Generation 3 audits established that UBTR is the canonical Human <-> Platform
translation layer, owns Platform UX, owns Shared Platform View Models, and must
be the reusable communication source for ACLI, Web, Mobile, REST, Voice, Product
1, Provider Services, Worker Services, Replay, Governance, and future adapters.

This artifact defines the canonical Human Communication Model for AiGOL.

Core rule:

```text
Platform Core owns communication meaning.
Interface adapters own communication presentation.
Products consume communication.
Interfaces never redefine communication.
```

This model does not introduce runtime changes. It defines the permanent
communication architecture that future runtime phases must implement.

## 2. Canonical Human Communication Architecture

Every Platform Core component communicates with humans through UBTR and Shared
Platform View Models.

Canonical flow:

```text
Human
  |
  v
Interface Adapter
  ACLI / Web / Mobile / REST / Voice / future adapter
  |
  v
UBTR Communication
  Human -> Platform translation
  understanding model
  ambiguity model
  confirmation model
  |
  v
CSA
  canonical semantic representation and lineage
  |
  v
OCS
  cognition orchestration and advisory evidence
  |
  v
Platform Services
  Governance / Replay / Provider / Worker / Approval /
  Authorization / Product / Policy / Routing
  |
  v
UBTR Communication
  Platform -> Human translation
  explanation model
  recommendation model
  guidance model
  transparency model
  shared view model
  |
  v
Interface Adapter
  modality-specific rendering only
  |
  v
Human
```

Communication artifacts are:

- deterministic;
- replay-visible when persisted;
- hash-bound;
- non-authoritative;
- source-linked to UBTR, CSA, OCS, Replay, Governance, Provider, Worker, Product,
  Approval, or Authorization evidence;
- reusable across every interface.

## 3. Communication Capability Inventory

Reusable communication capabilities already present or partially present:

| Capability | Existing source | Status |
| --- | --- | --- |
| Human request normalization | `human_to_governance_translation_runtime.py` | Present |
| Ambiguity detection | UBTR translation ambiguity flags | Present |
| Clarification questions | UBTR ambiguity flags and HIRR lifecycle | Present |
| Translation confidence | Universal Translation artifacts | Present |
| Governance summary | `governance_to_human_translation_runtime.py` | Present |
| Proposal summary | Governance -> Human translation, proposal artifacts | Partial |
| Approval explanation | Governance -> Human translation | Present |
| Worker status summary | Governance -> Human translation and worker artifacts | Partial |
| Validation summary | Governance -> Human translation | Present |
| Replay summary | Governance -> Human translation and replay artifacts | Present |
| Required next action | Governance -> Human translation | Present |
| Authoritative references | Governance -> Human translation | Present |
| Non-authority notice | Governance -> Human translation and G2/G3 artifacts | Present |
| Assumptions | Product 1 / OCS evidence | Partial |
| Risks | Product 1 / OCS evidence | Partial |
| Uncertainties | Product 1 / OCS evidence | Partial |
| Alternatives | OCS/Product evidence in limited paths | Partial |
| Trade-offs | No canonical model | Missing |
| Recovery guidance | Fail-closed texts and scattered docs | Partial |
| Communication levels | Summaries and sections imply concise/standard | Partial |
| Shared view models | G3-04 Phase 2.6 model alignment | Designed |
| Confirmation classification | ACLI compatibility runtime | Needs platform extraction |
| Conversation continuity | ACLI conversation artifacts and CSA lineage | Partial |

## 4. Canonical Communication Domains

### 4.1 Understanding

Purpose:

Communicate what the platform understood before governance, cognition, approval,
or execution decisions proceed.

Required fields:

- understood request summary;
- normalized intent;
- domain;
- requested actions;
- detected entities;
- CSA reference/hash;
- ambiguity status;
- missing information;
- current assumptions;
- confidence;
- replay lineage.

Canonical owner:

UBTR.

Consumers:

HIRR, OCS, ACLI, Web, Mobile, REST, Voice, Product 1, Replay.

### 4.2 Explanation

Purpose:

Communicate why platform state, recommendations, approvals, blocks,
clarifications, or next actions exist.

Required fields:

- explanation summary;
- because/reason fields;
- evidence references;
- source hashes;
- confidence;
- limitations;
- non-authority notice;
- fallback status;
- replay lineage.

Canonical owner:

UBTR Platform -> Human communication over Platform Services evidence.

### 4.3 Recommendation

Purpose:

Communicate advisory recommendations without granting authority.

Required fields:

- recommendation;
- recommendation source;
- evidence references;
- alternatives;
- trade-offs;
- consequences;
- assumptions;
- risks;
- uncertainties;
- advisory-only flag;
- approval/authorization requirement if action follows.

Canonical owner:

UBTR over OCS/Product/Governance evidence.

### 4.4 Guidance

Purpose:

Tell the human what can happen next without bypassing governance.

Required fields:

- next action;
- available options;
- blocked actions;
- recovery path;
- required confirmations;
- required approval;
- suggested workflow;
- fail-closed reason where applicable;
- compatibility fallback status.

Canonical owner:

UBTR / Governance / Shared Platform View Models.

### 4.5 Human Confirmation

Purpose:

Represent human feedback consistently across interfaces.

Supported communication intents:

- proposal;
- confirmation;
- modification;
- rejection;
- clarification;
- continuation.

Minimum classes:

- confirm;
- reject;
- clarify;
- modify;
- continue;
- unknown.

Canonical owner:

Shared Human Confirmation service under UBTR communication semantics.

Current compatibility:

ACLI confirmation classification remains compatibility evidence until extracted
and parity-certified.

### 4.6 Transparency

Purpose:

Make reasoning conditions and evidence limits visible.

Required fields:

- assumptions;
- risks;
- uncertainties;
- limitations;
- confidence;
- provider provenance;
- worker provenance;
- evidence quality;
- source references;
- advisory-only status;
- human approval boundary.

Canonical owner:

UBTR over OCS, Provider, Worker, Replay, Governance, and Product evidence.

### 4.7 Conversation

Purpose:

Support governed natural conversation without giving interfaces semantic
ownership.

Required fields:

- conversation id;
- session id;
- turn id;
- parent turn;
- CSA continuity;
- clarification state;
- proposal state;
- confirmation state;
- continuation state;
- context preservation references;
- replay lineage;
- current communication domain;
- required next communication step.

Canonical owner:

Shared conversation model with UBTR semantic communication ownership.

Interfaces own only modality-specific turn capture and rendering.

### 4.8 Communication Levels

Purpose:

Allow different presentation depths without changing semantic meaning.

Supported levels:

- concise;
- standard;
- detailed;
- beginner;
- technical;
- auditor;
- executive.

Rules:

- all levels derive from the same source evidence;
- levels may omit or expand presentation detail;
- levels may not alter meaning;
- level selection must be replay-visible when persisted;
- adapter formatting is separate from communication level.

Canonical owner:

UBTR / Shared Platform View Models.

## 5. Communication Lifecycle

Lifecycle:

```text
1. Human expresses intent through an interface adapter.
2. Adapter records modality-local input and submits it to UBTR.
3. UBTR produces Understanding communication and CSA lineage.
4. HIRR/OCS/Platform Services consume CSA and evidence.
5. Platform Services produce governance, replay, provider, worker, approval,
   authorization, product, and policy evidence.
6. UBTR converts platform evidence into Explanation, Recommendation, Guidance,
   Confirmation, Transparency, and Conversation communication models.
7. Shared Platform View Models bind communication to source hashes.
8. Interface adapter renders or serializes the model.
9. Human responds.
10. The next turn repeats through UBTR with replay-visible continuity.
```

Lifecycle invariants:

- no interface bypasses UBTR for reusable meaning;
- no product owns platform communication;
- provider output remains advisory;
- worker output remains execution evidence;
- approval and authorization remain distinct authorities;
- replay remains read-only evidence;
- all communication artifacts deny authority transfer.

## 6. Responsibility Matrix

| Communication capability | Owner | Consumers | Evidence | Replay impact | Governance impact |
| --- | --- | --- | --- | --- | --- |
| Understanding | UBTR | All interfaces, HIRR, OCS, Product, Replay | Human -> Governance translation, CSA | Records translation and CSA hashes | No authority transfer |
| Ambiguity and missing information | UBTR / HIRR lifecycle | Interfaces, HIRR | ambiguity flags, clarification questions | Records ambiguity and clarification lineage | Clarification-first preserved |
| Explanation | UBTR | All interfaces, Product, Replay | Governance -> Human translation | Records source evidence and explanation hash | No approval/execution authority |
| Recommendation | UBTR over OCS/Product evidence | Interfaces, Product | OCS advisory, Decision Packet | Records recommendation source hashes | Advisory only |
| Guidance | UBTR / Governance | Interfaces, operators | next action, blocked action, recovery fields | Records guidance hash and source evidence | Governance boundaries preserved |
| Human confirmation | Shared Human Confirmation service / UBTR | Interfaces, Approval, Authorization | confirmation artifact and input hash | Records classifier source and input hash | Does not approve by itself |
| Transparency | UBTR over Platform evidence | Interfaces, audit, Product | assumptions, risks, uncertainties, provenance | Records source evidence hashes | Keeps limits visible |
| Conversation | Shared conversation model / UBTR | Interfaces, HIRR, OCS | turn lineage, CSA continuity | Records turn and CSA hashes | Lifecycle ownership preserved |
| Communication levels | UBTR View Models | Interfaces | selected level and source model | Records level when persisted | Meaning unchanged |
| Provider communication | UBTR over Provider Services / OCS | Interfaces, Product | provider identity, response, comparison, cost | Records provider evidence hashes | Provider remains advisory |
| Worker communication | UBTR over Worker Services | Interfaces, Product | worker lifecycle, dispatch, result | Records worker evidence hashes | Worker authority unchanged |
| Product communication | UBTR over Product artifacts | Interfaces, Product | Decision/Audit Packet evidence | Records product artifact hashes | Product remains consumer |
| Adapter rendering | Interface adapters | Humans/API clients | render artifact/hash | Records adapter render hash separately | No semantic authority |

## 7. Extension Requirements

| Missing / partial capability | Rationale | Canonical owner | Compatibility impact | Implementation priority |
| --- | --- | --- | --- | --- |
| Communication level model | Human-first interaction needs audience/depth control | UBTR View Models | Default to standard; existing output remains fallback | High |
| Reasoning transparency model | Assumptions, risks, uncertainties, alternatives, and trade-offs need consistent wording | UBTR over OCS/Product/Governance evidence | Existing Product/OCS fields remain source | High |
| Available options model | Humans need safe choices instead of only next action | UBTR / Governance | Existing next action remains fallback | High |
| Blocked action taxonomy | Blocks need consistent explanation and recovery | UBTR / Governance / Authorization | Existing fail-closed wording remains fallback | High |
| Recovery guidance model | Natural development needs recovery from ambiguity, rejection, missing evidence, and unavailable resources | UBTR / Governance | Existing error text remains fallback | High |
| Shared Human Confirmation service | Confirmation semantics must not remain ACLI-local | Shared Platform Services / UBTR | ACLI classifier remains rollback | High |
| Provider communication model | Provider status, cost, failure, provenance, and advisory output need shared wording | UBTR over Provider Services | ACLI provider wording remains adapter output | Medium |
| Worker communication model | Worker lifecycle/execution needs shared human wording | UBTR over Worker Services | Existing worker summaries remain fallback | Medium |
| Product communication model | Product 1 evidence needs reusable presentation | UBTR over Product artifacts | Product summaries remain source | Medium |
| Conversation communication model | Follow-up and refinement need platform-owned meaning | UBTR + shared conversation service | ACLI conversation artifacts remain source | High |

## 8. Roadmap Impact

Required UBTR extensions:

- communication levels;
- reasoning transparency;
- options and alternatives;
- trade-offs and consequences;
- blocked action and recovery guidance;
- shared confirmation semantics;
- provider/worker/product communication bindings;
- conversation communication state.

Required Platform Core changes:

- implement shared communication/view-model schemas;
- bind communication artifacts to replay;
- extract ACLI confirmation semantics into shared service;
- define adapter rendering contracts.

ACLI simplifications:

- ACLI renders canonical communication models;
- ACLI no longer owns reusable explanation, confirmation, proposal, approval,
  authorization, replay, provider, worker, or product communication;
- ACLI compatibility wrappers remain until parity is certified.

Product impact:

- Product 1 keeps owning product artifacts;
- UBTR communicates product evidence through shared models;
- Product-specific summaries become source evidence, not interface-local UX.

Provider impact:

- Provider communication remains advisory;
- provider provenance, cost, comparison, failure, and fallback become shared
  communication inputs.

Worker impact:

- worker lifecycle, selection, dispatch, execution, result, and validation become
  shared communication inputs;
- worker authority remains unchanged.

Future interface impact:

- Web, Mobile, REST, Voice, and future adapters consume the same communication
  model;
- no future interface implements reusable communication meaning.

## 9. Primary Project Objective Assessment

Primary objective:

```text
Develop AiGOL through ACLI using natural language without ChatGPT/Codex copy-paste.
```

Assessment:

The canonical model is sufficient as an architecture for the objective, but
runtime implementation is still required before the objective is realistically
complete.

Remaining communication capabilities needed:

1. shared communication/view-model runtime;
2. communication levels;
3. reasoning transparency;
4. options, alternatives, trade-offs, and consequences;
5. recovery guidance;
6. shared confirmation service;
7. provider communication binding;
8. worker communication binding;
9. Product 1 communication binding;
10. ACLI adapter simplification over the shared model.

Once these are implemented, ACLI can become a natural-language development
interface over Platform Core rather than a terminal path that relies on external
ChatGPT/Codex copy-paste.

## 10. Recommended Next Implementation Batch

Recommended next batch:

`G3_04_PHASE_2_8_UBTR_COMMUNICATION_MODEL_RUNTIME_FOUNDATION_V1`

Scope:

- implement deterministic communication model schemas;
- implement Understanding, Explanation, Guidance, Transparency, and
  Communication Level artifacts over existing UBTR outputs;
- record source translation, CSA, replay, and evidence hashes;
- keep ACLI as adapter renderer only;
- preserve compatibility wrappers;
- do not invoke providers;
- do not execute workers;
- do not mutate repositories;
- do not change approval, authorization, governance, replay, provider, worker,
  OCS, PPP, or Product authority.

Certification criteria:

- communication artifacts are deterministic and hash-bound;
- communication meaning is reusable across interfaces;
- adapters render without redefining meaning;
- compatibility output remains replay-visible;
- authority flags remain denied;
- primary objective readiness can proceed to ACLI runtime integration.

## 11. Final Determination

The canonical Human Communication Model is now defined as a permanent Platform
Core invariant.

Runtime implementation remains a follow-on batch, but the model is ready.

Final verdict: UBTR_CANONICAL_HUMAN_COMMUNICATION_MODEL_READY
