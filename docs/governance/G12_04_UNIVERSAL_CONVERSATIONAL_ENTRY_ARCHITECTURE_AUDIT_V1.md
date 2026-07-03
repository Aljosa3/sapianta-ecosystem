# G12-04 Universal Conversational Entry Architecture Audit V1

Status: architectural responsibility clarification required.

Final verdict: ARCHITECTURAL_RESPONSIBILITY_CLARIFICATION_REQUIRED

## 1. Executive Summary

Generation 12 restored the operational behavior of the ACLI Next Message Composer. The restored behavior raised an architectural ownership question:

```text
Which certified component owns governed conversational reasoning?
```

This audit confirms that the certified architecture already separates the required responsibilities:

- interface adapters capture and render human interaction;
- PGSP owns the neutral governed session protocol and adapter-to-Platform-Core invocation boundary;
- UBTR owns natural-language semantic interpretation and bidirectional semantic translation;
- CSA owns structured semantic intent representation;
- Platform Core coordinates certified workflow progression;
- OCS prepares proposals, options, risks, and advisory execution intent;
- Governance authorizes;
- Replay records evidence and reconstruction;
- Worker Platform executes only after authorization;
- Provider Platform may provide non-authoritative cognition under governed boundaries;
- Platform Digital Twin projects canonical evidence;
- Architectural Health remains deterministic and advisory only.

The universal architecture is therefore already present in substance:

```text
CLI / Web / REST API / Voice / Mobile / Future Interfaces
-> Interface Adapter
-> PGSP
-> UBTR
-> CSA
-> Platform Core / OCS
-> Governance
-> Worker Platform
-> Replay
```

However, one terminology gap remains. Certified artifacts define PGSP as the canonical Platform Core session protocol, public API contract, session lifecycle owner, and adapter-to-Platform-Core invocation boundary. They do not consistently name PGSP as the universal "interface attachment layer." This is a clarification requirement, not an architecture redesign.

## 2. Capability Audit

| Capability | Certified owner | Audit finding |
| --- | --- | --- |
| Interface capture | Interface adapters, including ACLI Next | Existing adapters capture modality-specific input only. |
| Interface rendering | Interface adapters | Rendering remains adapter-local and must consume Platform-owned communication output. |
| Session protocol | PGSP | PGSP is certified as the canonical Platform Core session protocol. |
| Adapter invocation boundary | PGSP | PGSP owns the adapter-to-Platform-Core invocation boundary. |
| Natural-language semantic interpretation | UBTR | UBTR is the only semantic translation layer. |
| Canonical semantic artifact | CSA | CSA represents UBTR translation as deterministic structured intent. |
| Governed workflow coordination | Platform Core | Platform Core coordinates certified service interaction. |
| Proposal and advisory execution intent | OCS | OCS prepares proposals and advisory execution intent without authorization authority. |
| Authorization and approvals | Governance | Governance remains the authorization and approval authority. |
| Evidence and reconstruction | Replay | Replay remains append-only evidence and reconstruction authority. |
| Execution | Worker Platform | Workers execute authorized work only. |
| External cognition | Provider Platform / OCS boundary | Providers remain non-authoritative cognition sources. |
| Canonical architectural evidence projection | Platform Digital Twin | PDT projects evidence without becoming source authority. |
| Architectural health review | Architectural Health | Architectural Health remains deterministic, advisory, and non-authoritative. |

## 3. Ownership Matrix

| Responsibility | Canonical owner | Non-owners |
| --- | --- | --- |
| Conversational understanding | UBTR for semantic meaning; OCS may consume semantics for proposal cognition | ACLI Next, PGSP, Governance, Replay, Workers, Providers |
| Natural-language interpretation | UBTR | ACLI Next, PGSP, Platform Core, Governance, Replay, Workers |
| Intent resolution | UBTR produces meaning; CSA represents structured intent; OCS may prepare advisory proposal paths | ACLI Next, Providers, Workers |
| Governed conversational reasoning | Platform Core coordinates; OCS proposes; Governance constrains and authorizes | ACLI Next, interface adapters, Workers, Providers |
| Interface attachment | PGSP session protocol and adapter invocation boundary | UBTR, ACLI Next, Governance, Replay, Workers |
| Interface abstraction | PGSP for session envelope; UBTR/UHCL or Platform UX for semantic communication content | Individual adapters, Providers, Workers |
| CLI integration | ACLI Next adapter invoking PGSP-compatible workflow | Platform Core does not become CLI; ACLI Next does not become Platform Core |
| Web integration | Future Web adapter invoking PGSP-compatible workflow | Web must not own semantics, governance, replay, or execution |
| REST API integration | Future REST adapter invoking PGSP-compatible workflow | REST must not own semantics, governance, replay, or execution |
| Voice integration | Future Voice adapter invoking PGSP-compatible workflow | Voice must not own semantics, governance, replay, or execution |
| Mobile integration | Future Mobile adapter invoking PGSP-compatible workflow | Mobile must not own semantics, governance, replay, or execution |
| Future interface integration | Future adapter plus PGSP-compatible session attachment | No future interface may introduce a parallel semantic or governance authority |

## 4. Interface Attachment Audit

Certified PGSP artifacts establish:

- PGSP is the interface-neutral Platform Core session protocol between interface adapters and Platform Services.
- PGSP receives adapter-captured interaction and binds it to a governed session.
- PGSP owns neutral session identity, lifecycle state, evidence envelope, specialization declaration, and adapter-to-Platform-Core invocation boundary.
- Interface adapters invoke PGSP; they do not implement PGSP.
- ACLI is the first adapter, while Web, REST, Voice, Mobile, and future adapters should call PGSP through adapter-specific capture and render surfaces.

This is functionally an interface attachment model.

The audit finding is that the certified role exists, but the exact canonical phrase "universal interface attachment layer" is not yet consistently used. The minimum correction is a governance clarification that PGSP is the canonical universal session attachment and adapter invocation boundary, while still not becoming a semantic translator, renderer, governance authority, replay authority, provider authority, worker authority, or execution engine.

## 5. UBTR Responsibility Audit

UBTR is certified as the canonical semantic authority.

UBTR owns:

- semantic interpretation;
- deterministic Human -> Governance translation;
- deterministic Governance -> Human translation;
- ambiguity detection;
- confidence and escalation signals;
- semantic translation lineage;
- canonical semantic artifacts supplied to downstream Platform Core consumers.

UBTR does not own:

- governance authority;
- approval authority;
- authorization authority;
- replay mutation;
- worker dispatch;
- provider invocation outside OCS governance;
- repository mutation;
- deployment;
- interface rendering.

Therefore Platform Core should not receive raw adapter text as if Platform Core itself owns natural-language interpretation. Platform Core should receive UBTR/CSA-normalized semantic intent, plus replay-visible references to source interaction and translation evidence.

## 6. PGSP Responsibility Audit

PGSP is certified as the canonical Platform Core session protocol.

PGSP owns:

- neutral governed session identity;
- session lifecycle envelope;
- adapter-to-Platform-Core invocation boundary;
- specialization selection and declaration;
- canonical service sequence binding;
- response lineage continuity;
- replay-visible session summaries;
- explicit non-authority flags.

PGSP does not own:

- semantic translation;
- canonical semantic representation;
- reusable human communication semantics;
- interface rendering;
- OCS proposal semantics;
- Governance decisions;
- Replay reconstruction;
- provider execution;
- worker execution;
- mutation;
- deployment.

Conclusion: PGSP is the correct certified component for universal interface attachment, provided "attachment" is understood as session/protocol attachment and not semantic interpretation.

## 7. Platform Core Responsibility Audit

Platform Core remains the orchestration and coordination authority for certified Platform Services.

Platform Core owns:

- workflow coordination;
- service sequencing;
- capability composition;
- operational state production;
- integration of Governance, Replay, Worker Platform, Platform Digital Twin, Architectural Health, OCS, UBTR, PGSP, and certified runtimes.

Platform Core does not become:

- an interface adapter;
- a natural-language parser;
- a provider cognition engine;
- a governance substitute;
- replay authority;
- worker executor.

For universal conversational entry, Platform Core should coordinate after PGSP session attachment and UBTR semantic normalization. This preserves certified semantic ownership and prevents Platform Core from becoming a hidden conversational interpretation layer.

## 8. Universal Interface Verification

The certified architecture supports the following universal flow:

```text
Human
-> CLI / Web / REST API / Voice / Mobile / Future Interface
-> Interface Adapter
-> PGSP
-> UBTR
-> CSA
-> Platform Core / OCS
-> Governance
-> Worker Platform
-> Replay
-> Human-facing response through Platform communication output
-> Interface Adapter rendering
```

This flow is consistent with:

- G4 execution principles preserving UBTR as the only semantic translation layer;
- G4 governed self-development use case routing ACLI-captured intent through UBTR;
- G4 PGSP canonical protocol and session specialization;
- G4 PGSP public API and adapter contract;
- G6 Platform canonical projection architecture;
- UBTR responsibility boundary specification;
- UBTR Platform UX reuse audit;
- G11 ACLI Next conversational architecture reviews;
- G12 Message Composer architecture review.

The audit does not find evidence for a different certified universal architecture.

## 9. Architecture Consistency Assessment

The current ACLI Next Message Composer is architecturally consistent when treated as pre-turn operator UX:

```text
operator text composition
-> one submitted message
-> existing conversational path
```

The composer does not own semantic interpretation, workflow routing, Governance, Replay, Worker execution, Platform Digital Twin projection, or Architectural Health reasoning.

The architectural risk is not the composer itself. The risk is future conversational functionality accidentally treating ACLI Next as the place where natural-language meaning, intent classification, workflow progression, or governed reasoning is decided. Certified architecture requires those responsibilities to remain outside ACLI Next:

- PGSP attaches the interface interaction to a governed session.
- UBTR interprets conversational meaning.
- CSA represents structured intent.
- Platform Core coordinates the certified workflow.
- OCS proposes.
- Governance authorizes.
- Replay records.
- Worker Platform executes.

## 10. Responsibility Overlap Assessment

| Boundary | Overlap detected? | Assessment |
| --- | --- | --- |
| ACLI Next vs UBTR | Potential future risk only | ACLI Next must not classify semantic meaning beyond adapter-local commands. |
| ACLI Next vs PGSP | Potential terminology risk | ACLI Next may manage terminal UX, but PGSP owns governed session attachment. |
| PGSP vs UBTR | No | PGSP owns session envelope; UBTR owns semantic translation. |
| Platform Core vs UBTR | Potential clarification needed | Platform Core coordinates; UBTR/CSA should supply normalized semantic intent. |
| Platform Core vs Governance | No | Platform Core coordinates; Governance authorizes. |
| Replay vs ACLI Next | No current authority leakage | ACLI Next may write presentation artifacts but Replay remains evidence authority. |
| Worker Platform vs ACLI Next | No | ACLI Next does not execute Workers. |
| Provider Platform vs UBTR/OCS | No if governed | Providers may inform cognition but remain non-authoritative. |
| Architectural Health vs ACLI Next | No | ACLI Next presents findings only. |

## 11. Recommendations

1. Canonicalize PGSP wording as:

```text
PGSP is the universal governed session attachment and adapter invocation boundary.
```

This wording must explicitly preserve that PGSP is not a semantic, governance, replay, provider, worker, execution, or rendering authority.

2. Canonicalize UBTR wording for conversational interfaces as:

```text
UBTR is the universal semantic interpretation and bidirectional translation layer for conversational Platform Core interaction.
```

3. Clarify that Platform Core should receive UBTR/CSA-normalized semantic intent for governed conversational reasoning, not interpret raw natural-language requests as a Platform Core responsibility.

4. Require future ACLI Next, Web, REST, Voice, Mobile, and future interface work to document the handoff:

```text
Adapter capture -> PGSP session attachment -> UBTR semantic translation -> Platform Core coordination
```

5. Treat current ACLI Next message composition as valid adapter-local UX, but prohibit expansion from local command handling into semantic intent ownership.

## 12. Certification Summary

This audit finds no need for:

- a new conversational reasoning subsystem;
- a new interface attachment runtime;
- a new Platform Core orchestration engine;
- a new authority layer;
- a redesign of ACLI Next;
- a redesign of UBTR or PGSP.

The certified architecture already contains the universal conversational entry model in substance. The only required action is architectural clarification: explicitly name PGSP as the universal governed session attachment and adapter invocation boundary, and reaffirm UBTR as the universal conversational semantic interpretation layer.

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: ARCHITECTURAL_RESPONSIBILITY_CLARIFICATION_REQUIRED
