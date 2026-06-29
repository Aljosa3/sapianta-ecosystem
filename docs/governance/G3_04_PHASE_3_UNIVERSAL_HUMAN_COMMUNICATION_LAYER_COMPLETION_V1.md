# G3-04 Phase 3 Universal Human Communication Layer Completion V1

Status: UHCL completion program defined.

Final verdict: UHCL_EXTENSION_REQUIRED

## 1. Executive Summary

Generation 3 established that UBTR owns Human Communication, ACLI is an
interface adapter, interface adapters consume communication, and the canonical
Human Communication Runtime exists.

This phase defines completion of the Universal Human Communication Layer
(UHCL) inside UBTR.

The correct next step is not a parallel communication stack. Existing runtime
evidence already covers much of the required source material:

- UBTR translation owns Human -> Governance and Governance -> Human translation.
- The UBTR communication runtime owns deterministic communication artifacts,
  domains, levels, sections, lineage, and non-authority notices.
- Product 1 records assumptions, risks, uncertainties, recommendation summaries,
  OCS advisories, and audit evidence.
- OCS / multi-provider cognition records advisory findings, alternatives, risks,
  uncertainties, confidence, and provider participation.
- Worker runtimes record lifecycle, dispatch, invocation, result capture, and
  validation evidence.
- ACLI retains compatibility confirmation and rendering evidence until parity
  migration is certified.

UHCL therefore requires extension and canonicalization, not redesign.

## 2. UHCL Capability Inventory

| Capability | Current evidence source | Current status | Required action |
| --- | --- | --- | --- |
| Reasoning transparency | `governance_to_human_translation_runtime.py`, Product 1, OCS advisory | Partial | Extend UBTR transparency sections |
| Assumptions | Product 1 Decision Packet, Product 1 OCS Advisory, provider cognition | Partial | Normalize into UHCL transparency/recommendation fields |
| Risks | Product 1 Decision Packet, OCS Advisory, provider cognition, governance docs | Partial | Normalize into UHCL risk model |
| Uncertainties | Product 1 Decision Packet, OCS Advisory, provider cognition | Partial | Normalize into UHCL uncertainty model |
| Alternatives | Multi-provider cognition and OCS/Product evidence | Partial | Normalize into UHCL recommendation alternatives |
| Trade-offs | Governance docs and limited ACLI/OCS prose | Missing canonical runtime shape | Add UHCL trade-off model |
| Adaptive explanation | Communication levels exist; source-specific depth selection is not complete | Partial | Add level-aware section derivation |
| Recovery guidance | Fail-closed runtimes and ACLI docs | Partial | Add canonical recovery guidance section |
| Richer confirmation | ACLI classifier, G3-02 confirmation docs | Partial / misplaced | Add shared UBTR confirmation model and keep ACLI classifier as compatibility |
| Provider communication | Provider identity, attachment, raw response, multi-provider cognition | Partial | Add provider communication binding |
| Worker communication | Worker lifecycle, dispatch, invocation, result, validation | Partial | Add worker communication binding |
| Product communication | Product 1 workflow, Decision Packet, OCS Advisory, Audit Packet | Partial | Add Product communication binding |
| Progressive explanation | Communication levels and Governance -> Human summaries | Partial | Add progressive disclosure model |
| Conversational refinement | ACLI conversation turns, CSA continuity, HIRR clarification | Partial | Add platform-owned refinement model over turn lineage |

## 3. Extension Roadmap

UHCL completion should proceed in bounded runtime phases:

1. UHCL Section Schema Extensions.
   Add typed section models for transparency, recommendation, recovery,
   confirmation, provider, worker, product, and progressive explanation.
2. UHCL Source Evidence Binding.
   Create deterministic builders that bind existing Product 1, OCS, provider,
   worker, replay, governance, approval, and authorization evidence into UBTR
   communication artifacts.
3. UHCL Confirmation Model.
   Move reusable confirmation class semantics into UBTR / Shared Platform Core
   while preserving ACLI classification as rollback evidence.
4. UHCL Adaptive Explanation.
   Implement level-aware communication derivation for concise, standard,
   detailed, beginner, technical, auditor, and executive views without changing
   meaning.
5. UHCL Recovery Guidance.
   Normalize fail-closed, missing evidence, stale approval, provider failure,
   worker failure, replay mismatch, and ambiguity recovery paths.
6. UHCL Provider / Worker / Product Bindings.
   Bind specialized provider, worker, and Product 1 evidence to reusable
   communication sections.
7. UHCL Certification.
   Certify replay integrity, authority preservation, adapter neutrality,
   compatibility fallback, and deterministic reconstruction.

## 4. Runtime Extension Plan

Runtime extensions should build on:

- `aigol/runtime/ubtr_human_communication_model_runtime.py`;
- `aigol/runtime/human_to_governance_translation_runtime.py`;
- `aigol/runtime/governance_to_human_translation_runtime.py`;
- `aigol/runtime/product1_decision_packet.py`;
- `aigol/runtime/product1_ocs_advisory.py`;
- `aigol/runtime/product1_audit_packet.py`;
- `aigol/runtime/multi_provider_cognition_runtime.py`;
- provider identity / registry / attachment / response capture runtimes;
- worker lifecycle / dispatch / invocation / result / validation runtimes;
- ACLI rendering and confirmation runtimes as compatibility evidence only.

Required runtime additions:

| Runtime extension | Purpose | Authority impact |
| --- | --- | --- |
| `UHCL_TRANSPARENCY_SECTION_V1` | Normalize assumptions, risks, uncertainties, limitations, provenance, evidence quality | No authority transfer |
| `UHCL_RECOMMENDATION_SECTION_V1` | Normalize recommendation, alternatives, trade-offs, consequences, advisory-only status | No approval or execution |
| `UHCL_RECOVERY_GUIDANCE_SECTION_V1` | Normalize fail-closed reason, blocked actions, required evidence, recovery path | Governance boundaries preserved |
| `UHCL_CONFIRMATION_SECTION_V1` | Normalize confirmation class, scope, freshness, active object, and evidence-only status | Does not approve |
| `UHCL_PROVIDER_COMMUNICATION_SECTION_V1` | Normalize provider identity, provenance, cost/rate-limit status, comparison, failure, advisory output | Provider remains advisory |
| `UHCL_WORKER_COMMUNICATION_SECTION_V1` | Normalize worker lifecycle, dispatch, execution, result, validation, failure | Worker authority unchanged |
| `UHCL_PRODUCT_COMMUNICATION_SECTION_V1` | Normalize Product 1 workflow, Decision Packet, OCS Advisory, Audit Packet status | Product remains consumer |
| `UHCL_PROGRESSIVE_EXPLANATION_SECTION_V1` | Derive stable level-specific depth without changing meaning | Adapter-neutral |
| `UHCL_CONVERSATIONAL_REFINEMENT_SECTION_V1` | Bind turn lineage, clarification, proposal, confirmation, continuation state | Conversation meaning stays in UBTR |

Each extension must remain deterministic, hash-bound, replay-visible, and
interface-neutral.

## 5. Communication Domain Extensions

The existing communication domains remain canonical:

- Understanding;
- Explanation;
- Recommendation;
- Guidance;
- Human Confirmation;
- Transparency;
- Conversation.

Required domain extensions:

| Domain | Extension |
| --- | --- |
| Understanding | Include missing information, assumptions, ambiguity source, and confidence source |
| Explanation | Add because/reason taxonomy, limitation model, and source evidence quality |
| Recommendation | Add alternatives, trade-offs, consequences, advisory-only flag, approval/authorization requirement |
| Guidance | Add blocked action taxonomy, recovery path, required evidence, safe next options |
| Human Confirmation | Add active object, class, scope, freshness, stale confirmation detection, non-approval flag |
| Transparency | Add normalized assumptions, risks, uncertainties, provenance, provider/worker evidence quality |
| Conversation | Add refinement intent, parent turn context, unresolved question, and continuation boundary |

## 6. Replay Impact

UHCL replay must continue the existing model:

- communication artifact hash;
- source evidence hashes;
- CSA reference/hash;
- OCS reference/hash where available;
- provider / worker / product evidence references where available;
- communication domain and level;
- section hashes;
- compatibility fallback status;
- adapter render reference/hash when rendered;
- rollback reference.

Replay reconstruction must verify:

- source evidence hashes;
- section hashes;
- artifact hash;
- wrapper hash;
- authority denial;
- fallback status;
- adapter neutrality.

UHCL should simplify replay by separating platform communication meaning from
adapter presentation.

## 7. Governance Impact

UHCL completion preserves all certified authority boundaries:

- UBTR owns communication meaning.
- CSA owns canonical semantic representation.
- OCS owns cognition orchestration.
- Governance owns governance decision authority.
- Approval owns approval authority.
- Authorization owns authorization readiness and execution gate evidence.
- Provider Layer owns provider identity and invocation boundaries.
- Worker Layer owns worker lifecycle and execution boundaries.
- Replay owns reconstruction and evidence continuity.
- Product 1 owns product artifacts and consumes communication.
- ACLI/Web/Mobile/REST/Voice own presentation only.

UHCL artifacts remain non-authoritative and must explicitly deny approval,
authorization, execution, provider, worker, governance, mutation, and replay
mutation authority.

## 8. Compatibility Strategy

Compatibility remains required until parity is certified.

Compatibility sources:

- ACLI human-friendly explanation runtime;
- ACLI operator rendering and confirmation classifier;
- ACLI proposal / approval / authorization bridge wording;
- Product 1 summary fields;
- Governance -> Human translation summaries;
- provider and worker legacy summaries.

Migration strategy:

1. Generate UHCL communication artifact from existing source evidence.
2. Generate existing compatibility output.
3. Record comparison artifact with source hashes and parity status.
4. Prefer UHCL output only where deterministic parity is proven.
5. Retain compatibility fallback where parity is incomplete.
6. Retire duplicated ACLI communication meaning only after certification.

## 9. Certification Plan

UHCL certification requires:

- section schema validation tests;
- deterministic reconstruction tests;
- tamper/fail-closed tests;
- communication level parity tests;
- ACLI compatibility comparison tests;
- Product 1 communication binding tests;
- provider communication binding tests;
- worker communication binding tests;
- replay reconstruction tests;
- authority denial tests;
- full pytest.

Certification gates:

| Gate | Requirement |
| --- | --- |
| Determinism | Same source evidence produces same communication artifact except replay path |
| Replay | Artifact and wrapper hashes reconstruct and detect tampering |
| Authority | No UHCL artifact grants approval, authorization, execution, mutation, provider, worker, or governance authority |
| Compatibility | Existing ACLI/Product/provider/worker communication remains fallback until parity |
| Adapter neutrality | No terminal/Web/Mobile/REST/Voice-specific rendering enters UHCL meaning |
| Reuse | ACLI and future adapters consume the same communication artifact contract |

## 10. Remaining UHCL Capabilities

Remaining capabilities to implement:

1. typed transparency section;
2. normalized assumptions / risks / uncertainties model;
3. alternatives and trade-offs model;
4. recovery guidance model;
5. richer confirmation model;
6. provider communication binding;
7. worker communication binding;
8. product communication binding;
9. progressive explanation model;
10. conversational refinement model;
11. compatibility comparison artifacts;
12. final UHCL certification.

## 11. Next Implementation Batch

Recommended next batch:

`G3_04_PHASE_3A_UHCL_SECTION_SCHEMA_EXTENSIONS_V1`

Scope:

- extend the existing UBTR communication runtime with typed section builders for
  transparency, recommendation, guidance/recovery, confirmation, provider,
  worker, product, progressive explanation, and conversational refinement;
- reuse existing source evidence and hashes;
- do not invoke providers;
- do not execute workers;
- do not mutate repositories;
- do not add interface-specific rendering;
- preserve ACLI compatibility fallback.

## 12. Final Determination

The Universal Human Communication Layer is architecturally ready for completion,
but extension is still required before adapter integration can proceed safely.

Final verdict: UHCL_EXTENSION_REQUIRED
