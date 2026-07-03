# G12-04 AiGOL Next Canonical Entry Pipeline Architecture Audit V1

Status: canonical entry pipeline clarification required.

Final verdict: CANONICAL_ENTRY_PIPELINE_CLARIFICATION_REQUIRED

## 1. Executive Summary

This audit reviews the certified architecture to determine the canonical processing path initiated by:

```text
aigol next
```

The certified architecture supports the following canonical pipeline in substance:

```text
Terminal
-> aigol next
-> ACLI Next / AiGOL Next interface adapter
-> PGSP
-> UBTR
-> CSA
-> Platform Core / OCS
-> Governance
-> Worker Platform
-> Replay
```

The audit confirms:

- `aigol next` is an interface command, not an orchestration authority.
- ACLI Next / AiGOL Next is the human interaction and conversational UX adapter.
- PGSP is the certified Platform Core session protocol and adapter-to-Platform-Core invocation boundary.
- UBTR is the certified semantic interpretation and translation authority.
- Platform Core coordinates certified workflow progression.
- Governance authorizes.
- Worker Platform executes only authorized work.
- Replay records deterministic evidence and reconstruction.
- Provider Platform remains non-authoritative.
- Platform Digital Twin and Architectural Health remain evidence projection and advisory layers.

The proposed pipeline is therefore architecturally correct if PGSP is understood as the session attachment and invocation boundary, and UBTR is understood as the semantic interpretation layer.

One clarification is required: certified artifacts consistently define `PGSP` as the canonical session protocol, public API contract, and adapter invocation boundary, but they do not consistently use the phrase "interface attachment layer." This review recommends a documentation clarification, not a new subsystem or redesign.

## 2. Capability Audit

| Reviewed capability | Certified source of responsibility | Audit finding |
| --- | --- | --- |
| `aigol next` command | ACLI Next / AiGOL Next adapter | CLI command starts the human-facing conversational adapter. |
| Conversational UX | ACLI Next / AiGOL Next | Adapter-local presentation, message composition, prompts, guidance, and display. |
| Session attachment | PGSP | PGSP binds adapter-captured interaction to a governed Platform Core session. |
| Interface abstraction | PGSP plus adapter contract | Adapters invoke PGSP and must not duplicate Platform Services. |
| Semantic interpretation | UBTR | UBTR owns canonical interpretation of human meaning. |
| Intent normalization | UBTR / CSA | UBTR translates; CSA represents structured semantic intent. |
| Governed conversational reasoning | Platform Core / OCS / Governance composition | Platform Core coordinates; OCS proposes; Governance constrains and authorizes. |
| Governance | Governance | Governance owns approvals, authorization, and policy decisions. |
| Execution | Worker Platform | Workers execute authorized work only. |
| Provider cognition | Provider Platform through OCS/Governance boundary | Providers may inform cognition but remain non-authoritative. |
| Replay generation | Replay | Replay owns deterministic evidence and reconstruction. |
| Canonical evidence projection | Platform Digital Twin | PDT projects certified evidence without becoming authority. |
| Architectural review | Architectural Health | Architectural Health remains deterministic and advisory only. |

## 3. Canonical Entry Pipeline

The canonical path after the operator starts `aigol next` should be:

```text
Terminal
-> aigol next
-> ACLI Next / AiGOL Next interface adapter
-> PGSP session attachment
-> UBTR semantic interpretation
-> CSA structured intent
-> Platform Core coordination
-> OCS proposal / advisory execution-intent preparation
-> Governance approval and authorization checks
-> Worker Platform execution when authorized
-> Replay evidence and reconstruction
-> Platform communication output
-> ACLI Next / AiGOL Next rendering
```

This pipeline is supported by certified architecture:

- PGSP is defined as the interface-neutral Platform Core session protocol between interface adapters and canonical Platform Services.
- Interface adapters invoke PGSP; they do not implement PGSP.
- The PGSP lifecycle places semantic translation after session intake and assigns that stage to UBTR.
- UBTR owns canonical semantic interpretation and deterministic Human -> Governance / Governance -> Human translation.
- UBTR produces canonical semantic artifacts for Platform Core consumers.
- Platform Core coordinates certified services and does not become a CLI, parser, Governance authority, Replay authority, or Worker executor.

The simpler proposed pipeline:

```text
Terminal
-> aigol next
-> AiGOL Next
-> PGSP
-> UBTR
-> Platform Core
-> Governance
-> Workers
```

is directionally correct but incomplete because it omits CSA, OCS, Replay, Platform communication output, Platform Digital Twin evidence projection, Architectural Health advisory visibility, and Provider Platform boundaries.

## 4. Ownership Matrix

| Responsibility | Canonical owner | Notes |
| --- | --- | --- |
| Interface attachment | PGSP | Certified as session protocol and adapter invocation boundary; naming should be clarified as interface attachment. |
| Interface abstraction | PGSP | PGSP provides interface-neutral session envelope and specialization model. |
| Conversational UX | ACLI Next / AiGOL Next | Local prompt, composer, preview, clear, cancel, send, and display behavior. |
| Conversational state | PGSP for governed session; ACLI Next for adapter-local UX state | Message buffer and prompt state are adapter-local; governed session identity and evidence envelope belong to PGSP. |
| Natural-language understanding | UBTR | UBTR owns semantic interpretation. |
| Semantic normalization | UBTR / CSA | UBTR translates; CSA records structured intent. |
| Intent interpretation | UBTR / CSA with OCS consuming for proposals | ACLI Next must not infer governed intent beyond local commands. |
| Governed conversational reasoning | Platform Core / OCS / Governance | Platform Core coordinates, OCS proposes, Governance authorizes. |
| Orchestration | Platform Core | Platform Core remains orchestration authority. |
| Governance | Governance | Approval and authorization authority remains unchanged. |
| Worker delegation | Platform Core / Governance / Worker Platform boundary | Workers execute only authorized requests. |
| Replay generation | Replay | Adapters may write presentation artifacts but do not own Replay. |
| Provider cognition | Provider Platform under OCS/Governance constraints | Providers are non-authoritative and cannot decide, authorize, or execute. |
| Architectural evidence projection | Platform Digital Twin | Projection only; no source authority transfer. |
| Architectural advisory review | Architectural Health | Advisory only; no repair or authorization authority. |

## 5. AiGOL Next Assessment

This audit treats `AiGOL Next` and `ACLI Next` as the same operational interface lineage unless a future certified naming artifact distinguishes them.

AiGOL Next owns:

- terminal command entry;
- operator prompt lifecycle;
- message composition and local UX commands;
- display of Platform-owned results;
- guidance about current workflow state;
- adapter-local session interaction evidence.

AiGOL Next does not own:

- PGSP session protocol;
- semantic translation;
- intent normalization;
- Platform Core workflow progression;
- OCS proposal semantics;
- Governance approval or authorization;
- Replay reconstruction;
- Worker execution;
- Provider invocation as an adapter capability;
- Platform Digital Twin projection authority;
- Architectural Health reasoning.

Current `aigol next` behavior is architecturally valid only when it remains a thin show -> guide -> delegate layer.

## 6. PGSP Assessment

PGSP owns the canonical governed session boundary.

Certified PGSP responsibilities include:

- neutral governed session identity;
- session lifecycle state and evidence envelope;
- adapter-to-Platform-Core invocation boundary;
- specialization selection and declaration;
- canonical service sequence binding;
- response lineage continuity;
- replay-visible session summary;
- explicit non-authority flags.

For `aigol next`, PGSP should be the component that turns adapter-captured interaction into a governed Platform Core session attachment.

PGSP must not become:

- a semantic interpreter;
- a conversational reasoning engine;
- a renderer;
- a Governance authority;
- a Replay authority;
- a Worker executor;
- a Provider caller outside governed boundaries.

## 7. UBTR Assessment

UBTR is the canonical semantic interpretation layer.

UBTR owns:

- semantic interpretation;
- deterministic translation;
- ambiguity detection;
- confidence and escalation evidence;
- Human -> Governance translation;
- Governance -> Human translation;
- semantic lineage.

For `aigol next`, UBTR should receive the PGSP-bound human request and produce the canonical semantic meaning consumed by CSA, OCS, Platform Core, Governance, Replay, and downstream services.

UBTR must not become:

- Governance;
- Platform Core orchestration;
- Worker execution;
- Replay mutation;
- direct Provider invocation outside OCS;
- interface rendering.

## 8. Platform Core Assessment

Platform Core remains the orchestration and coordination authority after session attachment and semantic normalization.

Platform Core owns:

- workflow coordination;
- certified service composition;
- operational state production;
- sequencing of governed development capabilities;
- integration of PGSP, UBTR, CSA, OCS, Governance, Replay, Worker Platform, Platform Digital Twin, and Architectural Health.

Platform Core should receive already-normalized semantic intent from UBTR/CSA, plus replay-visible session and source references. Platform Core should not become the natural-language interpretation layer for raw `aigol next` input.

## 9. Interface Audit

| Interface | Canonical attachment owner | Adapter role |
| --- | --- | --- |
| `aigol next` | PGSP | ACLI Next / AiGOL Next captures and renders terminal interaction. |
| Web | PGSP | Web adapter captures and renders browser interaction. |
| REST API | PGSP | REST adapter maps requests/responses to PGSP-compatible sessions. |
| Voice | PGSP | Voice adapter captures and renders speech modality without owning semantics. |
| Mobile | PGSP | Mobile adapter captures and renders mobile interaction. |
| Future interfaces | PGSP | Future adapters must invoke PGSP and preserve certified ownership boundaries. |

The audit confirms PGSP as the certified owner in substance. It recommends explicitly canonicalizing the phrase:

```text
PGSP is the universal governed interface attachment and session invocation boundary.
```

This phrase must preserve that PGSP is not a semantic or authority layer.

## 10. Architecture Consistency Assessment

Implemented `aigol next` behavior is consistent with the certified architecture where it:

- captures operator input;
- supports local message composition;
- submits one completed request;
- delegates to existing governed conversational/session paths;
- displays execution-plan, dashboard, Replay, Governance, and Architectural Health information;
- records presentation evidence without claiming Replay ownership.

Potential inconsistency exists if future `aigol next` behavior:

- interprets natural language inside ACLI Next;
- decides governed intent without UBTR/CSA;
- advances workflow without Platform Core;
- treats dashboard state as Governance;
- invokes Workers or Providers directly;
- generates Replay-owned evidence outside Replay boundaries.

No redesign is required. The required response is clarification and enforcement of the entry pipeline.

## 11. Recommendations

1. Clarify the canonical `aigol next` entry pipeline as:

```text
aigol next -> ACLI Next adapter -> PGSP -> UBTR -> CSA -> Platform Core / OCS -> Governance -> Worker Platform -> Replay
```

2. Canonicalize PGSP wording as:

```text
PGSP is the universal governed interface attachment and session invocation boundary.
```

3. Canonicalize the `aigol next` adapter rule:

```text
ACLI Next / AiGOL Next captures, presents, guides, and delegates only.
```

4. Require future conversational implementation and architecture reviews to show evidence of:

- PGSP session attachment;
- UBTR semantic interpretation;
- CSA structured intent;
- Platform Core coordination;
- Governance authorization;
- Replay evidence;
- Worker-only execution.

5. Treat any direct ACLI Next semantic reasoning, worker execution, authorization, or replay reconstruction as responsibility leakage.

## 12. Certification Summary

The certified architecture already defines the canonical entry pipeline in substance. The proposed `Terminal -> aigol next -> AiGOL Next -> PGSP -> UBTR -> Platform Core -> Governance -> Workers` path is correct as a simplified view, but it should be expanded to include CSA, OCS, Replay, Provider boundaries, Platform Digital Twin, and Architectural Health visibility.

The only required action is architectural clarification:

- PGSP should be explicitly named as the universal governed interface attachment and session invocation boundary.
- UBTR should remain explicitly named as the canonical semantic interpretation layer.
- `aigol next` should remain explicitly named as an adapter-only interface.

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: CANONICAL_ENTRY_PIPELINE_CLARIFICATION_REQUIRED
