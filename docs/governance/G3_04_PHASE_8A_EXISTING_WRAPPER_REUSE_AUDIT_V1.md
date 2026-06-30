# G3-04 Phase 8A Existing Wrapper Reuse Audit V1

Status: EXISTING WRAPPER REUSE AUDIT COMPLETE

Final verdict: WRAPPER_REUSE_CONFIRMED

## 1. Executive Summary

This audit reviews the remaining communication compatibility wrappers before
runtime migration begins.

The audit confirms that the reusable communication capabilities provided by the
remaining wrappers are already represented inside UHCL through existing
communication artifacts, typed sections, progressive explanations, shared
confirmation, source evidence binding, recovery guidance, and Provider/Worker/
Product communication bindings.

The wrappers still contain useful adapter wiring, legacy replay fields, and
source evidence production, but they do not require new UHCL communication
semantics before migration.

Primary conclusion:

- No genuinely missing UHCL communication capability was found.
- Most wrappers require adapter wiring to existing UHCL artifacts.
- Some wrappers require partial migration to separate source evidence from
  reusable human-facing wording.
- Legacy wrappers should remain compatibility-only until parity snapshots pass.

## 2. Audit Scope

Reviewed wrapper families:

- `aigol/runtime/acli_human_friendly_explanation_runtime.py`;
- `aigol/runtime/acli_llm_assisted_explanation_runtime.py`;
- `aigol/runtime/acli_proposal_approval_bridge.py`;
- `aigol/runtime/acli_authorization_bridge.py`;
- remaining operator rendering compatibility fields;
- Provider summary wrappers;
- Worker summary wrappers;
- Product 1 summary wrappers;
- Governance-to-Human wording wrappers;
- Replay summary wording wrappers.

This audit introduces no runtime changes.

## 3. Wrapper Inventory

| Wrapper / surface | Existing function | UHCL equivalent | Reuse finding |
| --- | --- | --- | --- |
| `acli_human_friendly_explanation_runtime.py` | Builds deterministic operator explanation sections, compatibility rendered output, transparency notices, and UBTR translation fallback. | Typed explanation/transparency sections, progressive explanation derivation, source evidence binding, non-authority notices. | Functionality already exists in UHCL; adapter wiring and parity snapshots required. |
| `acli_llm_assisted_explanation_runtime.py` | Captures optional provider-assisted explanation evidence, deterministic fallback, provider transparency, and advisory-only flags. | Source evidence binding, transparency sections, progressive explanation derivation, Provider provenance binding, non-authority notices. | UHCL covers communication; partial migration required to keep provider output as source evidence only. |
| `acli_proposal_approval_bridge.py` | Records proposal versions, approval requests, approval decisions, rollback references, and non-authority flags. | Recommendation, guidance, alternatives, trade-offs, risks, assumptions, confirmation sections, shared confirmation, approval evidence binding. | Proposal/approval communication exists in UHCL; approval source evidence remains outside UHCL. |
| `acli_authorization_bridge.py` | Records authorization readiness, precondition evidence, approval-to-authorization lineage, blocked status, and non-execution flags. | Recovery guidance, guidance sections, transparency sections, source evidence binding, approval/authorization evidence bindings. | UHCL covers communication; authorization authority remains external. |
| Operator rendering compatibility fields | Preserves legacy lines, legacy confirmation classes, and migrated UHCL consumption evidence. | ACLI UHCL adapter rendering and canonical UHCL response classes. | Already migrated; remaining fields are compatibility-only. |
| Provider proposal / diagnostic summaries | Records provider proposal, retry, governance, attachment, provenance, and response evidence. | Provider cognition summary and Provider provenance communication bindings. | UHCL covers summary communication; provider runtimes remain source evidence producers. |
| Worker lifecycle / execution summaries | Records worker assignment, dispatch, invocation, lifecycle, result, and validation evidence. | Worker execution summary and Worker lifecycle summary communication bindings. | UHCL covers summary communication; worker runtimes remain source evidence producers. |
| Product 1 workflow summaries | Records Product 1 workflow and operational status evidence. | Product 1 workflow summary communication binding. | UHCL covers summary communication; Product 1 remains source evidence producer. |
| Product 1 decision packet summaries | Records decision packet evidence and validation summary. | Product 1 decision packet summary communication binding. | UHCL covers summary communication; packet authority remains Product 1. |
| Product 1 audit packet summaries | Records audit packet and audit summary evidence. | Product 1 audit packet summary communication binding. | UHCL covers summary communication; audit evidence remains Product 1. |
| Governance-to-Human wording wrappers | Translates governance, proposal, approval, worker, validation, replay, and ERR evidence into rendered explanation sections. | Typed explanation, transparency, guidance, recovery sections, source evidence binding, progressive explanation derivation. | UHCL covers communication; governance translation can become source evidence or compatibility evidence. |
| Replay summary wording wrappers | Renders replay status, capability, authorization, verification, result summary, and ordering. | Transparency/explanation sections, source evidence binding, replay evidence references. | UHCL covers communication; Replay remains reconstruction authority. |

## 4. Capability Reuse Matrix

| Capability | Already in UHCL | Wrapper migration type | Missing UHCL capability |
| --- | --- | --- | --- |
| Deterministic explanation | yes | adapter wiring | none |
| Multi-level explanation | yes | adapter wiring | none |
| Explanation transparency | yes | adapter wiring | none |
| Optional provider explanation provenance | yes | partial migration | none |
| Proposal summary communication | yes | partial migration | none |
| Approval request communication | yes | partial migration | none |
| Approval decision communication | yes | partial migration | none |
| Authorization readiness communication | yes | partial migration | none |
| Blocked authorization recovery guidance | yes | adapter wiring | none |
| Human confirmation classes | yes | already migrated / compatibility cleanup | none |
| Provider cognition summary | yes | source evidence binding | none |
| Provider provenance | yes | source evidence binding | none |
| Worker execution summary | yes | source evidence binding | none |
| Worker lifecycle summary | yes | source evidence binding | none |
| Product 1 workflow summary | yes | source evidence binding | none |
| Product 1 decision packet summary | yes | source evidence binding | none |
| Product 1 audit packet summary | yes | source evidence binding | none |
| Governance explanation | yes | partial migration | none |
| Replay summary explanation | yes | partial migration | none |
| Non-authority notices | yes | adapter wiring | none |
| Replay-visible lineage | yes | adapter wiring | none |
| Rollback references | yes | adapter wiring | none |

## 5. Duplication Assessment

The remaining wrappers duplicate UHCL communication responsibilities only in
legacy presentation and wording fields.

Duplicate categories:

1. explanation prose duplicated by UHCL progressive explanation derivation;
2. transparency prose duplicated by UHCL transparency sections and non-authority
   notices;
3. proposal and approval wording duplicated by UHCL recommendation, guidance,
   confirmation, and evidence-bound sections;
4. authorization readiness wording duplicated by UHCL recovery guidance and
   evidence-bound transparency sections;
5. Provider/Worker/Product summaries duplicated by UHCL communication bindings;
6. governance explanation sections duplicated by UHCL typed sections;
7. replay rendered summary wording duplicated by UHCL transparency and
   explanation sections.

The wrappers still provide important compatibility and source evidence value,
but they should no longer be interpreted as canonical communication owners.

## 6. Missing Capability Assessment

No missing UHCL capability was identified.

Capabilities that might appear unique in wrappers are already covered:

- provider-assisted explanation transparency is covered by source evidence
  binding, transparency sections, Provider provenance binding, and non-authority
  notices;
- approval request and decision visibility is covered by shared confirmation and
  source evidence binding;
- authorization precondition failure is covered by recovery guidance;
- replay summary wording is covered by transparency/explanation sections over
  replay evidence;
- Product 1 summaries are covered by Product 1 communication bindings.

Remaining work is integration work, not UHCL semantic expansion.

## 7. Migration Recommendations

Recommended migration order:

1. Migrate ACLI deterministic and LLM-assisted explanation wrappers to consume
   UHCL progressive explanation and transparency artifacts.
2. Migrate proposal and approval bridge communication to UHCL typed sections and
   shared confirmation while retaining approval evidence ownership.
3. Migrate authorization bridge communication to UHCL recovery guidance and
   evidence-bound transparency while retaining authorization evidence ownership.
4. Migrate Provider summaries to UHCL Provider cognition and provenance
   bindings.
5. Migrate Worker summaries to UHCL Worker execution and lifecycle bindings.
6. Migrate Product 1 summaries to UHCL Product 1 workflow, decision packet, and
   audit packet bindings.
7. Migrate Governance-to-Human and Replay summary wording to UHCL source-bound
   explanation/transparency sections.
8. Capture parity snapshots and retire compatibility-only wording fields.

## 8. Remaining Unique Functionality

Remaining unique functionality is not reusable communication meaning.

Unique wrapper responsibilities to preserve:

- legacy replay compatibility;
- existing caller contracts during migration;
- source evidence production;
- approval and authorization boundary evidence;
- provider advisory evidence capture;
- worker execution evidence capture;
- Product 1 packet evidence;
- replay reconstruction evidence;
- ACLI terminal adapter behavior.

These responsibilities must be retained or relocated carefully, but they do not
require new UHCL communication semantics.

## 9. Next Implementation Batch

Recommended next batch:

`G3_04_PHASE_8B_ACLI_EXPLANATION_WRAPPER_UHCL_WIRING_V1`

Scope:

- wire `acli_human_friendly_explanation_runtime.py` to UHCL progressive
  explanation artifacts;
- wire `acli_llm_assisted_explanation_runtime.py` to UHCL source evidence and
  transparency artifacts;
- preserve deterministic fallback and provider advisory boundaries;
- record parity snapshots;
- retain wrappers as compatibility-only until parity passes.

## 10. Final Determination

The audit confirms wrapper reuse: existing UHCL capabilities are sufficient for
the remaining wrapper migration. No new UHCL communication capability is needed
before migration begins.

Final verdict: WRAPPER_REUSE_CONFIRMED
