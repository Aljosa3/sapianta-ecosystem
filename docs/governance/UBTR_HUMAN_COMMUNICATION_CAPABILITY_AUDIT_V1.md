# UBTR Human Communication Capability Audit V1

Status: architectural communication capability audit.

Final verdict: UBTR_HUMAN_COMMUNICATION_EXTENSION_REQUIRED

## 1. Executive Summary

Platform Core Generation 2 is certified.

Generation 3 architectural audits established:

- UBTR is the canonical bidirectional Human <-> Platform translation layer;
- UBTR owns reusable Platform UX;
- UBTR owns shared Platform View Models;
- Platform Services are implemented once and reused everywhere;
- ACLI, Web, Mobile, REST, Voice, and future interfaces are adapters only;
- products consume Platform Services.

This audit verifies communication capability, not ownership and not LLM quality.

Conclusion:

- UBTR already provides a substantial deterministic human communication
  substrate through Human -> Governance translation, Governance -> Human
  translation, Universal Translation artifacts, ambiguity flags, confidence,
  replay lineage, human-readable payloads, explanation sections, required next
  action wording, approval explanations, proposal summaries, worker/validation
  summaries, replay summaries, ERR summaries, authoritative references, and
  non-authority notices.
- UBTR is sufficient as the canonical base for governed natural-language
  development through ACLI.
- UBTR is not yet sufficient as a rich human-first communication layer for every
  future interface because audience levels, alternatives, trade-offs, explicit
  assumptions/risks/uncertainties, recovery guidance, provider/worker/Product UX
  wording, and shared conversation guidance are only partial or implemented in
  adjacent Product/ACLI/OCS artifacts.
- The correct next step is an extension of UBTR and Shared Platform View Models,
  not interface-local communication logic and not a new independent UX system.

## 2. Human Communication Capability Inventory

Reusable communication capabilities currently implemented inside UBTR or its
certified integration surface:

| Capability | Existing implementation | Communication value |
| --- | --- | --- |
| Human request normalization | `human_to_governance_translation_runtime.py` | Communicates what the platform understood as normalized intent. |
| Ambiguity detection | `human_to_governance_translation_runtime.py`, `governance_to_human_translation_runtime.py` | Communicates unclear or missing governance evidence. |
| Confidence | Universal Translation artifact confidence fields | Communicates semantic confidence at translation level. |
| Clarification questions | Human -> Governance ambiguity flags | Supports asking for missing or safer input. |
| Governance summary | Governance -> Human translation payload | Communicates current workflow and state. |
| Governance decision summary | Governance -> Human translation payload | Communicates governance decision state. |
| Proposal summary | Governance -> Human translation payload | Communicates proposal identity and target paths. |
| Approval explanation | Governance -> Human translation payload | Communicates whether approval is required or recorded. |
| Worker execution summary | Governance -> Human translation payload | Communicates worker execution status when supplied. |
| Validation summary | Governance -> Human translation payload | Communicates validation status when supplied. |
| Replay summary | Governance -> Human translation payload | Communicates replay status and replay reference. |
| ERR summary | Governance -> Human translation payload | Communicates ERR evidence status when supplied. |
| Required next action | Governance -> Human translation payload | Communicates what the human should do next. |
| Authoritative state references | Governance -> Human translation payload | Communicates source hashes and references. |
| Non-authority notice | Governance -> Human translation payload and artifacts | Communicates that explanation does not approve or execute. |
| Universal Translation replay | Universal Translation integration | Communicates translation source, hash, direction, and replay lineage. |
| Compatibility fallback visibility | G2 explanation migration and ACLI explanation runtime | Communicates prior deterministic output while migration proceeds. |

## 3. Capability Matrix

| Capability | Implementation status | Evidence | Current owner | Canonical owner | Reuse assessment |
| --- | --- | --- | --- | --- | --- |
| Why something happened | PARTIALLY_SUPPORTED | Governance summary, decision summary, replay summary | UBTR | UBTR / Shared View Model | Existing explanation says what state exists; causal why needs richer evidence mapping. |
| Why a recommendation exists | PARTIALLY_SUPPORTED | Product 1 Decision Packet recommendation summary; OCS advisory evidence | Product 1 / OCS | UBTR over Product/OCS evidence | Recommendation rationale exists adjacent to UBTR, but not yet canonical UBTR communication. |
| Why approval is required | FULLY_SUPPORTED | `approval_explanation`; approval-required ambiguity handling | UBTR | UBTR / Approval View Model | Deterministic approval wording exists. |
| Why execution is blocked | PARTIALLY_SUPPORTED | approval rejection wording, no execution wording, non-authority notices | UBTR / ACLI / authorization artifacts | UBTR over Authorization View Model | Common block reasons exist, but not complete as shared blocker taxonomy. |
| Why clarification is needed | FULLY_SUPPORTED | ambiguity flags and clarification questions | UBTR | UBTR | Material ambiguity and missing evidence are communicated. |
| Assumptions | PARTIALLY_SUPPORTED | Product 1 Decision Packet and OCS Advisory assumptions | Product 1 / OCS | UBTR over Product/OCS evidence | Recorded outside UBTR; UBTR needs shared rendering support. |
| Uncertainty | PARTIALLY_SUPPORTED | ambiguity flags, OCS advisory uncertainties | UBTR / OCS / Product 1 | UBTR over OCS/Product evidence | Translation ambiguity exists; broader uncertainty communication needs extension. |
| Confidence | FULLY_SUPPORTED | Universal Translation confidence; OCS advisory confidence | UBTR / OCS | UBTR for translation; OCS for cognition evidence | Translation confidence exists and is reusable. |
| Evidence | FULLY_SUPPORTED | authoritative references and replay hashes | UBTR / Replay | UBTR / Replay / Shared View Model | Strong hash-bound evidence references exist. |
| Risks | PARTIALLY_SUPPORTED | Product 1 risk records; OCS advisory risks | Product 1 / OCS | UBTR over Product/OCS evidence | Risk records exist but need canonical human wording. |
| Alternatives | PLATFORM_EXTENSION_REQUIRED | Some provider/OCS dogfood evidence includes alternatives, not canonical UBTR | Mixed | UBTR / OCS View Model | No stable UBTR alternatives model. |
| Trade-offs | PLATFORM_EXTENSION_REQUIRED | No canonical UBTR trade-off communication model found | None canonical | UBTR / OCS View Model | Requires extension. |
| Limitations | PARTIALLY_SUPPORTED | non-authority notices, known limitation docs | UBTR / governance docs | UBTR / Governance View Model | Authority limits are clear; capability limitations need richer model. |
| Natural follow-up | PARTIALLY_SUPPORTED | ACLI conversational turn lineage and continuation status | ACLI runtime | Shared conversation model / UBTR | Conversation continuity exists in ACLI; needs UBTR/shared model integration. |
| Conversational continuation | PARTIALLY_SUPPORTED | turn parent linkage, continuation status, CSA continuity | ACLI runtime | Shared conversation model / UBTR | Deterministic continuity exists; not yet fully UBTR-owned communication. |
| Clarification questions | FULLY_SUPPORTED | ambiguity flags and clarification questions | UBTR | UBTR | Implemented. |
| Contextual memory inside governed session | PARTIALLY_SUPPORTED | ACLI session/conversation artifacts and CSA continuity | ACLI runtime | Shared session/conversation service / UBTR | Exists as first-interface runtime; needs platform extraction. |
| Proposal refinement | PARTIALLY_SUPPORTED | ACLI proposal/approval bridge and modification classification | ACLI / proposal runtimes | Proposal service + UBTR View Model | Supports refinement evidence, but shared communication model incomplete. |
| Progressive understanding | PARTIALLY_SUPPORTED | CSA continuity, clarification continuity, turn lineage | UBTR / ACLI / HIRR | UBTR + shared conversation model | Existing lineage supports it; communication model needs extension. |
| Concise communication level | IMPLEMENTED_UNDER_ANOTHER_NAME | summaries and next action | UBTR | UBTR View Model | Summaries can act as concise level. |
| Standard communication level | IMPLEMENTED_UNDER_ANOTHER_NAME | rendered explanation sections | UBTR | UBTR View Model | Sectioned explanation acts as standard level. |
| Detailed communication level | PLATFORM_EXTENSION_REQUIRED | no canonical detail level selector | None canonical | UBTR View Model | Needs explicit level support. |
| Beginner communication level | GENUINELY_MISSING | no canonical beginner audience model found | None | UBTR View Model | Needs new audience-level model. |
| Technical communication level | PARTIALLY_SUPPORTED | source hashes, replay references, artifact ids | UBTR / Replay | UBTR View Model | Technical evidence exists; explicit technical mode needed. |
| Auditor communication level | PARTIALLY_SUPPORTED | replay hashes, authoritative references, certification docs | UBTR / Replay / Governance | UBTR View Model / Replay | Evidence exists; auditor communication model needed. |
| Executive communication level | PARTIALLY_SUPPORTED | Product 1 and executive review docs | Product docs | UBTR View Model / Product | Not canonical UBTR communication yet. |
| Recommended next action | FULLY_SUPPORTED | `operator_action_required`; `WHAT TO DO NEXT` | UBTR | UBTR | Implemented. |
| Available options | PLATFORM_EXTENSION_REQUIRED | no canonical options model found | None canonical | UBTR View Model | Needs extension. |
| Blocked actions | PARTIALLY_SUPPORTED | approval rejection, no execution wording, non-authority flags | UBTR / authorization | UBTR over Authorization View Model | Needs shared blocker taxonomy. |
| Required confirmations | PARTIALLY_SUPPORTED | ACLI confirmation model; approval wording | ACLI / UBTR | Shared Human Confirmation service + UBTR | Confirmation classes exist in ACLI, not yet shared. |
| Suggested workflow | PARTIALLY_SUPPORTED | Human -> Governance workflow candidate and routing evidence | UBTR / routing | UBTR View Model | Workflow candidate exists; human guidance needs model. |
| Recovery guidance | PLATFORM_EXTENSION_REQUIRED | fail-closed messages exist across runtimes, no canonical UBTR recovery guidance | Mixed | UBTR / Governance View Model | Needs extension. |
| What UBTR understood | FULLY_SUPPORTED | normalized intent, domain, actions, entities | UBTR | UBTR | Implemented. |
| What remains ambiguous | FULLY_SUPPORTED | ambiguity flags and questions | UBTR | UBTR | Implemented. |
| Missing information | FULLY_SUPPORTED | clarification questions and Governance -> Human ambiguity explanation | UBTR | UBTR | Implemented. |
| Current assumptions | PARTIALLY_SUPPORTED | Product/OCS assumptions, not canonical UBTR | Product 1 / OCS | UBTR over evidence | Needs shared rendering. |
| Confirmation prompts | PARTIALLY_SUPPORTED | ACLI confirmation rendering and approval next action | ACLI / UBTR | Shared Human Confirmation service | Needs platform extraction. |
| Modification requests | PARTIALLY_SUPPORTED | ACLI classifier and approval modification wording | ACLI / UBTR | Shared Human Confirmation/Approval model | Needs shared model. |
| Clarification loops | FULLY_SUPPORTED | UBTR/HIRR clarification lifecycle and CSA lineage | UBTR / HIRR | UBTR / HIRR | Implemented with lifecycle split. |
| Rejection handling | PARTIALLY_SUPPORTED | approval rejected wording and ACLI reject class | UBTR / ACLI | Shared Approval/Human Confirmation model | Needs shared model. |
| Iterative refinement | PARTIALLY_SUPPORTED | conversation turn lineage, proposal modification, clarification continuity | ACLI / UBTR / proposal | Shared conversation + UBTR | Needs shared communication model. |
| Cross-interface consistency | PARTIALLY_SUPPORTED | UBTR and shared view model architecture docs | UBTR / Platform Core | UBTR / Shared View Model | Architecture defined; runtime model implementation pending. |

## 4. Communication Gap Analysis

### 4.1 Missing Communication Abilities

Capabilities requiring UBTR or Platform Core extension:

- audience/presentation levels: detailed, beginner, technical, auditor,
  executive;
- explicit alternatives;
- explicit trade-offs;
- reusable recovery guidance;
- available options;
- shared blocker taxonomy;
- canonical provider communication model;
- canonical worker communication model;
- canonical Product 1 communication model over Product evidence;
- shared conversation communication model for follow-up and refinement.

### 4.2 Duplicated Communication Logic

Duplicated or at-risk communication logic:

- ACLI confirmation classification duplicates a reusable human confirmation
  capability;
- ACLI operator response lines duplicate reusable response-model content;
- ACLI human-friendly explanation sections duplicate UBTR explanation structure
  as compatibility output;
- ACLI provider-assisted explanation wrapper duplicates a reusable advisory
  explanation capability that should be shared;
- future provider/worker rendering would duplicate Platform UX if implemented in
  ACLI.

### 4.3 Reusable Communication Services

Reusable services already present:

- Human -> Governance Translation Runtime;
- Governance -> Human Translation Runtime;
- Universal Translation Artifact Schema;
- Universal Translation Runtime Integration;
- G2 explanation rendering comparison substrate;
- HIRR clarification lifecycle consuming CSA semantics;
- Product 1 Decision Packet, OCS Advisory, and Audit Packet evidence;
- replay and authoritative hash references.

### 4.4 Required Platform Core Extensions

Required extensions:

1. Shared Platform View Model runtime over UBTR Governance -> Human output.
2. Shared Human Confirmation service with UBTR support for natural-language
   confirmations.
3. Communication level model.
4. Reasoning transparency model for assumptions, uncertainty, risks,
   alternatives, trade-offs, and limitations.
5. Recovery and blocked-action guidance model.
6. Provider, worker, and Product communication models over their canonical
   Platform Services evidence.

## 5. Human-First Readiness Assessment

| Target | Readiness | Assessment |
| --- | --- | --- |
| Governed natural-language development through ACLI | PARTIALLY_READY | UBTR supports semantic intake, clarification, explanation, approval wording, replay evidence, and next action. Rich conversational communication still needs extension. |
| Replacement of ChatGPT/Codex copy-paste workflows | NOT_YET_READY | The communication substrate exists, but human-first guidance, iterative refinement, alternatives, recovery, and provider/worker communication need platform-level extension. |
| Future Web interface | ARCHITECTURALLY_READY_NOT_RUNTIME_COMPLETE | Shared view-model architecture supports Web, but communication models must be implemented before avoiding duplication. |
| Future Mobile interface | ARCHITECTURALLY_READY_NOT_RUNTIME_COMPLETE | Same as Web; mobile should consume shared UBTR communication models. |
| Future Voice interface | NEEDS_EXTENSION | Voice requires concise, turn-aware, interruption-safe communication levels and recovery guidance. |
| Future REST interface | ARCHITECTURALLY_READY_NOT_RUNTIME_COMPLETE | REST can serialize shared models once they exist. |

Overall:

UBTR is communication-capable enough to be the canonical base, but not yet rich
enough to complete the human-first Generation 3 objective without extension.

## 6. Recommended Extensions

| Capability | Rationale | Canonical owner | Replay impact | Governance impact | Compatibility impact |
| --- | --- | --- | --- | --- | --- |
| Shared Platform View Model runtime | Expose UBTR communication consistently across interfaces | UBTR / Shared Platform Services | Record view-model id/hash and source translation hash | No authority transfer | ACLI rendering remains compatibility output |
| Communication level model | Support concise, standard, detailed, beginner, technical, auditor, executive outputs | UBTR View Model | Record requested and rendered level | No authority transfer | Default to standard for compatibility |
| Reasoning transparency model | Communicate assumptions, uncertainty, risks, alternatives, trade-offs, limitations | UBTR over OCS/Product/Governance evidence | Record source evidence hashes | Provider/OCS remains advisory | Existing Product/OCS evidence remains source |
| Shared Human Confirmation service | Avoid interface-local confirmation semantics | Shared Platform Services with UBTR support | Record classifier source and input hash | Does not approve | ACLI classifier remains fallback |
| Recovery guidance model | Help humans recover from blocked, ambiguous, or failed-closed states | UBTR / Governance View Model | Record blocker and recovery guidance hashes | Fail-closed preserved | Existing error text remains fallback |
| Provider communication model | Explain provider status, advisory output, cost, failure, comparison | UBTR over Provider Services / OCS | Record provider evidence hashes | Provider remains advisory | ACLI provider wording remains adapter/fallback |
| Worker communication model | Explain worker lifecycle, selection, dispatch, execution, results | UBTR over Worker Services | Record worker evidence hashes | Worker authority unchanged | Existing worker summaries remain fallback |
| Product communication model | Explain Product 1 decisions, risks, assumptions, audit packets | UBTR over Product artifacts | Record Product artifact hashes | Product remains consumer | Existing Product summaries remain source |

## 7. Roadmap Impact

Generation 3 should extend UBTR communication capabilities before expanding to
additional interfaces or relying on ACLI-specific communication wrappers.

Roadmap disposition:

| Area | Disposition |
| --- | --- |
| Existing UBTR translation | Continue unchanged; reuse as canonical source. |
| Shared Platform View Models | Implement next. |
| Communication levels | Add as Platform Core extension. |
| Reasoning transparency | Add over existing OCS/Product/Governance evidence. |
| ACLI communication wrappers | Reclassify as adapters or compatibility fallbacks. |
| Provider/worker UX | Build only after shared communication model foundation. |
| Web/Mobile/Voice | Postpone runtime work until shared communication models exist. |

Estimated impact:

- architectural impact: medium, because ownership is already settled but
  reusable communication contracts must be added;
- implementation effort: moderate, because existing UBTR output and Product/OCS
  evidence can be reused;
- conversational quality improvement: high;
- impact on primary objective: high, because richer UBTR communication is
  necessary for natural-language ACLI development without copy-paste workflows.

## 8. Revised Generation 3 Roadmap

Recommended order:

1. G3-04 Phase 2.7: UBTR Human Communication Model Extension.
   Define and implement communication levels, reasoning transparency, options,
   blocker/recovery guidance, and shared confirmation guidance over existing
   UBTR outputs.
2. G3-04 Phase 2.8: Shared Human Confirmation Service.
   Extract ACLI confirmation classes into Platform Core and bind them to UBTR
   when semantic prose confirmation is needed.
3. G3-04 Phase 3: Provider Services Canonical Registry And Policy Facade.
   Continue provider-service alignment after communication foundations are
   reusable.
4. G3-04 Phase 4: Provider Communication View Model Binding.
   Add provider status, comparison, cost, failure, and advisory explanation
   communication over Provider Services evidence.
5. G3-05 Phase 1: Worker Communication And Services Reuse Alignment.
   Add worker lifecycle and execution communication over Worker Services
   evidence.
6. Later interface work: Web, Mobile, REST, Voice.
   Consume shared UBTR communication models only.

## 9. Recommended Next Implementation Batch

Recommended next batch:

`G3_04_PHASE_2_7_UBTR_HUMAN_COMMUNICATION_MODEL_EXTENSION_V1`

Scope:

- extend UBTR/shared view models with communication levels;
- add reasoning transparency fields for assumptions, uncertainty, confidence,
  evidence, risks, alternatives, trade-offs, and limitations;
- add available-options and blocked-action guidance;
- add recovery guidance for ambiguity, missing evidence, failed-closed state,
  rejected approval, and unavailable provider/worker paths;
- preserve existing UBTR translation output as canonical source;
- keep ACLI as an adapter and compatibility renderer;
- do not evaluate LLM quality;
- do not invoke providers;
- do not execute workers;
- do not mutate repositories;
- do not transfer approval, authorization, governance, replay, provider, or
  worker authority.

Certification criteria:

- all communication artifacts are deterministic and hash-bound;
- communication models consume UBTR and Platform Services evidence;
- ACLI renders without owning reusable communication meaning;
- future interfaces can consume the same communication artifacts;
- replay records communication source, level, evidence, fallback, and adapter
  rendering hashes;
- authority flags remain denied.

## 10. Final Determination

UBTR is the correct canonical human communication layer and already implements a
strong deterministic communication foundation.

Extension is required before UBTR can fully support rich human-first
conversation across ACLI, Web, Mobile, REST, Voice, and future interfaces.

Final verdict: UBTR_HUMAN_COMMUNICATION_EXTENSION_REQUIRED
