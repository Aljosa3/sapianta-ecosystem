# G3-04 Phase 2.9 Interface Adapter Communication Alignment V1

Status: adapter alignment assessment complete.

Final verdict: INTERFACE_ADAPTER_ALIGNMENT_REQUIRED

## 1. Executive Summary

Platform Core Generation 2 is certified.

The UBTR Canonical Human Communication Runtime is implemented. The permanent
architecture is now:

```text
UBTR owns communication meaning.
Platform Core owns Platform UX.
Interface adapters own presentation only.
Products consume communication models.
```

This phase reviews ACLI as the first interface adapter and defines the canonical
adapter consumption architecture for ACLI, Web, Mobile, REST, Voice, and future
interfaces.

Primary finding:

- ACLI already preserves governance, replay, approval, authorization, provider,
  worker, and execution boundaries.
- ACLI still contains compatibility-era reusable communication behavior in
  explanation rendering, confirmation classification, operator summaries, and
  proposal / approval / authorization wording.
- These behaviors must be realigned so ACLI consumes UBTR communication
  artifacts and only performs terminal-specific presentation.

No runtime changes are made by this artifact.

## 2. Canonical Adapter Consumption Architecture

Canonical flow:

```text
Human
  |
  v
Interface Adapter
  ACLI / Web / Mobile / REST / Voice / future adapter
  |
  v
UBTR Human Communication Runtime
  communication domain
  communication level
  communication sections
  CSA / OCS / replay lineage
  required human action
  non-authority notices
  |
  v
Interface Adapter Presentation
  terminal lines / web cards / mobile views / REST payloads / voice turns
  |
  v
Human
```

Adapter rules:

1. The adapter may collect human input.
2. The adapter may select or request a communication level.
3. The adapter may pass platform evidence to UBTR communication.
4. The adapter may render a UBTR communication artifact in its modality.
5. The adapter may record adapter rendering replay evidence.
6. The adapter must not redefine explanation, confirmation, proposal, approval,
   authorization, replay, provider, worker, or product communication meaning.
7. The adapter must not grant approval, authorization, execution, provider,
   worker, mutation, governance, or replay authority.

## 3. ACLI Alignment Assessment

| ACLI module / surface | Current responsibility | Canonical role | Assessment |
| --- | --- | --- | --- |
| `acli_human_friendly_explanation_runtime.py` | Builds compatibility explanation sections, calls Governance -> Human UBTR translation, composes operator output, records parity evidence | Consumer of UBTR communication artifacts plus terminal rendering wrapper | Alignment required |
| `acli_operator_rendering_and_confirmation.py` | Renders operator session/turn state and classifies confirmation input | Terminal renderer plus temporary compatibility classifier | Alignment required |
| `acli_conversational_development_session.py` | Records conversation, turn lineage, CSA continuity, clarification/proposal/confirmation/continuation state | Adapter session capture and platform conversation evidence source | Mostly correct |
| `acli_development_session_lifecycle.py` | Records ACLI session lifecycle, replay lineage, governance checkpoints, recovery status | Adapter session identity and lifecycle source evidence | Correct |
| `acli_proposal_approval_bridge.py` | Creates proposal and approval-request evidence from conversational sessions | Platform workflow bridge; communication wording should be UBTR-sourced | Partial alignment required |
| `acli_authorization_bridge.py` | Creates authorization-readiness evidence without execution | Platform workflow bridge; human-facing readiness wording should be UBTR-sourced | Partial alignment required |
| ACLI dogfood/operator certification surfaces | Certify operational usability, approval observation, correction, and daily operator readiness | Certification consumers of adapter and UBTR communication artifacts | Alignment required in future certification |

## 4. Modules Becoming UBTR Communication Consumers

The following ACLI surfaces should consume
`UBTR_CANONICAL_HUMAN_COMMUNICATION_ARTIFACT_V1`:

- human-friendly explanation output;
- operator session state rendering;
- turn state rendering;
- clarification request presentation;
- proposal summary presentation;
- approval request presentation;
- authorization-readiness presentation;
- rejection / recovery presentation;
- replay and governance summary presentation;
- provider and worker status presentation once G3-04/G3-05 bindings exist.

They should not create reusable communication meaning locally.

## 5. Adapter-Specific Wrappers That Remain in ACLI

ACLI legitimately owns:

- command history;
- terminal input capture;
- multiline editing;
- terminal prompt state;
- terminal-safe output line wrapping;
- ANSI color decisions if introduced later;
- paging / scrolling decisions if introduced later;
- shell process boundaries;
- ACLI session identity as an adapter session;
- adapter rendering replay evidence;
- adapter-level failure display.

These are interface UX responsibilities and should not move into UBTR.

## 6. Reusable Logic to Remove or Isolate from ACLI

The following ACLI compatibility behaviors should be removed from reusable
ownership or isolated as rollback-only compatibility paths after parity is
certified:

| Reusable behavior | Current ACLI location | Canonical owner | Alignment strategy |
| --- | --- | --- | --- |
| Explanation section meaning | `acli_human_friendly_explanation_runtime.py` | UBTR communication runtime | Generate UBTR `EXPLANATION` / `TRANSPARENCY` sections and have ACLI render them |
| Required operator action wording | `acli_operator_rendering_and_confirmation.py` | UBTR `GUIDANCE` section | ACLI renders `required_human_action` and does not derive action meaning |
| Confirmation class semantics | `acli_operator_rendering_and_confirmation.py` | UBTR / shared Human Confirmation communication | Extract deterministic classifier or route classification evidence into UBTR communication |
| Proposal summary wording | `acli_proposal_approval_bridge.py` and ACLI renderers | UBTR over proposal evidence | Proposal artifact remains source evidence; UBTR communicates it |
| Approval wording | `acli_proposal_approval_bridge.py` and ApprovalRequest surfaces | UBTR over approval evidence | Approval remains authority; UBTR explains state |
| Authorization-readiness wording | `acli_authorization_bridge.py` | UBTR over authorization evidence | Authorization bridge remains evidence; UBTR communicates readiness |
| Replay/governance summaries | ACLI explanation/rendering wrappers | UBTR over Replay/Governance evidence | ACLI renders replay/governance communication sections |

## 7. Reusable Adapter Pattern

Every interface adapter should implement the same pattern:

1. Capture interface-local input.
2. Record adapter-local input evidence if persistence is required.
3. Submit human intent or platform evidence to UBTR / Platform Core.
4. Receive a canonical UBTR communication artifact.
5. Render or serialize the artifact according to modality.
6. Record adapter rendering evidence with a reference to the UBTR artifact hash.
7. Return human response through UBTR or a shared confirmation path.

Adapter output must include or preserve:

- communication id;
- communication domain;
- communication level;
- CSA reference/hash when available;
- OCS reference/hash when available;
- sections rendered;
- required human action;
- non-authority notices;
- replay lineage;
- rollback reference;
- adapter render hash where persisted.

## 8. Interface Responsibility Matrix

| Responsibility | UBTR / Platform Core | ACLI | Web | Mobile | REST | Voice |
| --- | --- | --- | --- | --- | --- | --- |
| Communication meaning | Owns | Consumes | Consumes | Consumes | Consumes | Consumes |
| Communication domains and levels | Owns | Selects/requests | Selects/requests | Selects/requests | Requests | Selects/requests |
| Explanation / guidance wording | Owns | Renders | Renders | Renders | Serializes | Speaks |
| Confirmation semantics | Owns | Captures input | Captures UI action | Captures gesture/action | Captures field | Captures utterance |
| Presentation layout | Provides model only | Terminal | Browser | Native mobile | JSON schema | Speech turn |
| Replay source artifact | Owns communication artifact | Records adapter render reference | Records adapter render reference | Records adapter render reference | Records response reference | Records speech response reference |
| Governance boundaries | Preserved by Platform Core | Must not alter | Must not alter | Must not alter | Must not alter | Must not alter |
| Execution/provider/worker authority | Not granted by communication | None | None | None | None | None |

## 9. Compatibility Strategy

Compatibility wrappers remain active until parity is certified:

- ACLI explanation compatibility output remains rollback evidence.
- ACLI operator rendering remains a terminal adapter surface.
- ACLI confirmation classification remains compatibility evidence until moved or
  wrapped by UBTR communication.
- Proposal, approval, and authorization bridge artifacts remain source evidence.

Migration rule:

```text
UBTR communication artifact first.
ACLI compatibility output second.
Adapter rendering evidence third.
```

Fallback rule:

- If UBTR communication artifact creation fails, ACLI must fail closed or use
  explicitly recorded compatibility fallback evidence.
- Fallback must be replay-visible.
- Fallback must not grant authority.

## 10. Replay Impact

Replay should become simpler and more reusable:

- UBTR records communication artifact and artifact hash.
- Adapter records render artifact and references UBTR communication hash.
- Compatibility comparison records previous ACLI output while migration remains
  incomplete.
- Replay reconstruction can compare platform communication meaning separately
  from interface presentation.

Required future replay evidence:

- UBTR communication artifact reference/hash;
- adapter render artifact reference/hash;
- compatibility output reference/hash where active;
- communication domain and level;
- required human action;
- non-authority notice preservation;
- fallback status.

## 11. Governance Impact

Governance boundaries are preserved.

The alignment does not change:

- governance authority;
- approval authority;
- authorization authority;
- replay authority;
- OCS authority;
- CSA authority;
- provider ownership;
- worker ownership;
- Product 1 ownership.

The alignment strengthens governance by preventing each interface from inventing
its own human-facing interpretation of governance evidence.

## 12. Implementation Roadmap

Recommended implementation order:

1. Add ACLI adapter rendering over UBTR communication artifacts.
2. Preserve current ACLI explanation/rendering output as comparison evidence.
3. Route ACLI required-action wording through UBTR `GUIDANCE`.
4. Route explanation and transparency output through UBTR `EXPLANATION` and
   `TRANSPARENCY`.
5. Add UBTR-backed confirmation communication while retaining ACLI classifier
   compatibility evidence.
6. Bind proposal, approval, and authorization bridge evidence to UBTR
   communication sections.
7. Certify parity and retire duplicated ACLI communication meaning.
8. Reuse the same adapter consumption contract for Web, Mobile, REST, and Voice.

## 13. Next Implementation Batch

Recommended next batch:

`G3_04_PHASE_3_ACLI_UBTR_COMMUNICATION_ADAPTER_RUNTIME_V1`

Scope:

- implement ACLI rendering from UBTR communication artifacts;
- record adapter rendering evidence referencing UBTR communication hashes;
- preserve terminal-specific rendering inside ACLI;
- keep existing ACLI compatibility wrappers as rollback evidence;
- do not invoke providers;
- do not execute workers;
- do not mutate repositories;
- do not change approval, authorization, governance, replay, OCS, CSA, provider,
  worker, or Product authority.

## 14. Final Determination

The canonical adapter consumption architecture is established, but ACLI still
contains reusable compatibility communication behavior that must be aligned with
the UBTR Canonical Human Communication Runtime.

Final verdict: INTERFACE_ADAPTER_ALIGNMENT_REQUIRED
