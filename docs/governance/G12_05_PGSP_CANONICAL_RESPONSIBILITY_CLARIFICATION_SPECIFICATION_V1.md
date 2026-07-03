# G12-05 PGSP Canonical Responsibility Clarification Specification V1

Status: PGSP canonical responsibility specified.

Final verdict: PGSP_CANONICAL_RESPONSIBILITY_SPECIFIED

## 1. Executive Summary

G12-04 confirmed that the canonical `aigol next` entry pipeline already exists in substance, but one terminology gap remained:

```text
PGSP is certified as the Platform Core session protocol and adapter invocation boundary,
but it is not yet consistently named as the universal governed interface attachment boundary.
```

This specification closes that ambiguity without redesigning Platform Core, PGSP, UBTR, ACLI Next, Governance, Replay, Worker Platform, Provider Platform, Platform Digital Twin, or Architectural Health.

Canonical wording:

```text
PGSP is the universal governed interface attachment and session invocation boundary for all present and future interfaces.
```

This wording is a responsibility clarification only. It does not make PGSP a semantic interpreter, orchestration engine, governance authority, execution authority, replay authority, provider authority, or rendering system.

## 2. Capability Audit

| Capability | Certified owner | Clarification |
| --- | --- | --- |
| `aigol next` command | ACLI Next / AiGOL Next | Starts the CLI adapter and conversational UX. |
| Interface capture | Interface adapters | Adapters capture modality-specific input. |
| Universal governed interface attachment | PGSP | PGSP binds adapter-captured interaction to a governed Platform Core session. |
| Adapter invocation boundary | PGSP | PGSP is the adapter-to-Platform-Core session invocation boundary. |
| Interface independence | PGSP plus adapter contract | All adapters use the same session protocol boundary. |
| Semantic interpretation | UBTR | UBTR owns canonical interpretation of human meaning. |
| Intent normalization | UBTR / CSA | UBTR translates; CSA records deterministic structured intent. |
| Proposal and advisory reasoning | OCS | OCS prepares proposals, alternatives, risks, and advisory execution intent. |
| Workflow coordination | Platform Core | Platform Core coordinates certified services. |
| Governance decisions | Governance | Governance owns approvals, authorization, and policy gates. |
| Evidence and reconstruction | Replay | Replay owns deterministic evidence continuity. |
| Execution | Worker Platform | Workers execute authorized work only. |
| Provider cognition | Provider Platform under OCS/Governance constraints | Providers remain non-authoritative. |
| Canonical evidence projection | Platform Digital Twin | PDT projects evidence without becoming authority. |
| Advisory architectural review | Architectural Health | Architectural Health remains deterministic and advisory only. |

## 3. Canonical Entry Pipeline

The canonical conversational entry pipeline is:

```text
Terminal
-> aigol next
-> ACLI / AiGOL Next
-> PGSP
-> UBTR
-> CSA
-> Platform Core / OCS
-> Governance
-> Worker Platform
-> Replay
```

Expanded lifecycle:

```text
Human
-> Interface Adapter
-> PGSP session attachment
-> UBTR semantic interpretation
-> CSA structured intent
-> Platform Core coordination
-> OCS proposal / advisory execution-intent preparation
-> Governance approval and authorization checks
-> Worker Platform execution when authorized
-> Replay evidence and reconstruction
-> Platform communication output
-> Interface Adapter rendering
```

This pipeline applies to:

- `aigol next`;
- Web;
- REST API;
- Voice;
- Mobile;
- future interface adapters.

No certified documentation reviewed in G12-04 establishes a competing canonical entry pipeline. Existing PGSP artifacts already define the session protocol and adapter contract; this specification clarifies the terminology.

## 4. PGSP Responsibility Definition

PGSP canonically owns:

- universal governed interface attachment;
- adapter-to-Platform-Core invocation boundary;
- interface-neutral session protocol;
- neutral governed session identity;
- session lifecycle state and evidence envelope;
- session specialization selection and declaration;
- canonical service sequence binding;
- adapter lifecycle boundary for session intake and response capture;
- response lineage continuity;
- replay-visible session summary;
- explicit non-authority flags for provider, worker, approval, authorization, mutation, deployment, and replay boundaries;
- interface independence across CLI, Web, REST API, Voice, Mobile, and future adapters.

PGSP does not own:

- semantic interpretation;
- natural-language understanding;
- intent resolution;
- canonical semantic representation;
- OCS proposal semantics;
- Platform Core orchestration;
- Governance approval or authorization;
- Worker execution;
- Provider execution or cognition selection outside governed boundaries;
- Replay reconstruction authority;
- repository mutation;
- deployment;
- interface rendering;
- reusable human communication semantics.

Canonical definition:

```text
PGSP is the universal governed interface attachment and session invocation boundary for all present and future interfaces. PGSP attaches adapter-captured interaction to a governed Platform Core session, preserves session lineage and invocation evidence, and binds the interaction to certified Platform Services without absorbing their responsibilities.
```

## 5. Ownership Matrix

| Responsibility | Owner | PGSP relationship |
| --- | --- | --- |
| CLI command entry | ACLI Next / AiGOL Next | Invokes PGSP-compatible session path. |
| Web entry | Web adapter | Invokes PGSP-compatible session path. |
| REST API entry | REST adapter | Invokes PGSP-compatible session path. |
| Voice entry | Voice adapter | Invokes PGSP-compatible session path. |
| Mobile entry | Mobile adapter | Invokes PGSP-compatible session path. |
| Future interfaces | Future adapters | Must invoke PGSP-compatible session path. |
| Universal interface attachment | PGSP | Owns governed session attachment boundary. |
| Interface abstraction | PGSP | Provides interface-neutral session protocol and specialization model. |
| Semantic interpretation | UBTR | PGSP hands off to UBTR; it does not translate. |
| Intent normalization | UBTR / CSA | PGSP references artifacts; it does not own meaning. |
| Governed reasoning | Platform Core / OCS / Governance | PGSP binds sequence; it does not decide. |
| Orchestration | Platform Core | PGSP invokes/binds; Platform Core coordinates. |
| Proposal preparation | OCS | PGSP records references; OCS owns proposal semantics. |
| Authorization | Governance | PGSP preserves gates; Governance decides. |
| Execution | Worker Platform | PGSP records execution-intent boundaries; Workers execute authorized actions. |
| Provider cognition | Provider Platform through OCS/Governance | PGSP records non-authority boundaries; Providers remain non-authoritative. |
| Replay evidence | Replay | PGSP emits replay-visible session evidence; Replay owns reconstruction. |
| Evidence projection | Platform Digital Twin | PGSP may be projected; PDT remains projection-only. |
| Architectural review | Architectural Health | PGSP may be reviewed; Architectural Health remains advisory. |

## 6. UBTR Responsibility Audit

UBTR remains the canonical owner of:

- semantic interpretation;
- natural-language understanding;
- Human -> Governance translation;
- Governance -> Human translation;
- semantic normalization;
- ambiguity detection;
- confidence and escalation signals;
- semantic lineage;
- canonical semantic artifacts for Platform Core consumers.

UBTR does not own:

- interface attachment;
- adapter invocation;
- session protocol;
- adapter lifecycle;
- interface rendering;
- Governance decisions;
- Worker execution;
- Replay mutation;
- Platform Core orchestration.

PGSP and UBTR are therefore complementary:

```text
PGSP attaches the interaction to a governed session.
UBTR determines what the interaction means.
```

## 7. AiGOL Next Responsibility Audit

AiGOL Next / ACLI Next remains:

- CLI adapter;
- conversational UX;
- operator interaction layer;
- prompt and message composition surface;
- presentation and guidance layer;
- local adapter evidence producer.

AiGOL Next / ACLI Next must delegate into PGSP and must not assume:

- PGSP session protocol ownership;
- UBTR semantic interpretation ownership;
- CSA structured-intent ownership;
- Platform Core orchestration ownership;
- OCS proposal ownership;
- Governance authority;
- Replay authority;
- Worker execution authority;
- Provider authority;
- Platform Digital Twin projection authority;
- Architectural Health advisory reasoning.

Adapter-local commands such as message composition, preview, clear, cancel, send, and exit are UX controls only. They must not become governed intent interpretation.

## 8. Future Interface Verification

The canonical PGSP definition applies uniformly:

| Interface | Required entry behavior |
| --- | --- |
| `aigol next` | Capture terminal interaction and invoke PGSP-compatible session attachment. |
| Web | Capture browser interaction and invoke PGSP-compatible session attachment. |
| REST API | Map API request into PGSP-compatible session attachment. |
| Voice | Capture speech interaction and invoke PGSP-compatible session attachment. |
| Mobile | Capture mobile interaction and invoke PGSP-compatible session attachment. |
| Future interfaces | Capture modality-specific interaction and invoke PGSP-compatible session attachment. |

No interface may introduce a parallel:

- semantic interpreter;
- session protocol;
- Governance authority;
- Replay authority;
- Worker execution path;
- Provider execution path;
- Platform Core orchestration path.

## 9. Terminology Clarification

Existing certified terminology:

| Existing wording | Status | Clarification |
| --- | --- | --- |
| PGSP is the canonical Platform Core session protocol. | Correct | Retain. |
| PGSP is the adapter-to-Platform-Core invocation boundary. | Correct | Retain. |
| PGSP owns neutral governed session identity. | Correct | Retain. |
| Interface adapters invoke PGSP. | Correct | Retain. |
| PGSP is the public API contract for future adapters. | Correct | Retain. |
| PGSP is the universal governed interface attachment boundary. | Incomplete / implicit | Add as canonical wording. |

Recommended canonical wording for future artifacts:

```text
PGSP is the universal governed interface attachment and session invocation boundary for all present and future interfaces. Interface adapters capture and render modality-specific interaction, then invoke PGSP. PGSP binds adapter-captured interaction to a governed Platform Core session and hands semantic interpretation to UBTR. PGSP does not own semantics, orchestration, governance, replay, provider execution, worker execution, mutation, deployment, or rendering.
```

## 10. Documentation Update Recommendations

Future documentation should use this clarification when discussing:

- `aigol next`;
- ACLI Next conversational UX;
- Web adapter work;
- REST API adapter work;
- Voice adapter work;
- Mobile adapter work;
- future interface adapters;
- governed conversational entry;
- Platform Core entry pipeline reviews.

Recommended update targets:

| Artifact family | Recommendation |
| --- | --- |
| PGSP architecture docs | Add the canonical interface attachment wording. |
| ACLI Next architecture docs | State that ACLI Next delegates interface attachment to PGSP. |
| UBTR docs | State that UBTR does not own interface attachment. |
| Future interface specifications | Require explicit PGSP attachment evidence. |
| Architecture reviews | Verify PGSP handoff before UBTR and Platform Core processing. |

No runtime implementation is required by this specification.

## 11. Responsibility Verification

| Boundary | Responsibility movement? | Finding |
| --- | --- | --- |
| AiGOL Next -> PGSP | No | AiGOL Next remains adapter; PGSP owns session attachment. |
| PGSP -> UBTR | No | PGSP attaches; UBTR interprets. |
| PGSP -> CSA | No | PGSP references structured intent; CSA owns it. |
| PGSP -> Platform Core / OCS | No | PGSP binds session; Platform Core coordinates and OCS proposes. |
| PGSP -> Governance | No | PGSP preserves checkpoints; Governance authorizes. |
| PGSP -> Replay | No | PGSP emits session evidence; Replay owns reconstruction. |
| PGSP -> Worker Platform | No | PGSP records boundaries; Workers execute authorized actions. |
| PGSP -> Provider Platform | No | PGSP preserves provider non-authority; Providers remain governed inputs. |
| PGSP -> Platform Digital Twin | No | PDT projects PGSP evidence only. |
| PGSP -> Architectural Health | No | Architectural Health reviews and advises only. |

## 12. Certification Summary

This specification confirms:

- the canonical conversational entry pipeline is already certified in substance;
- PGSP is the universal governed interface attachment and session invocation boundary;
- UBTR remains the semantic interpretation layer;
- CSA remains the structured intent layer;
- Platform Core / OCS remain coordination and proposal layers;
- Governance remains authorization authority;
- Replay remains evidence authority;
- Worker Platform remains execution authority;
- Provider Platform remains non-authoritative;
- Platform Digital Twin remains projection-only;
- Architectural Health remains advisory-only;
- AiGOL Next remains a thin CLI adapter and conversational UX layer.

No new architectural concept is introduced. No certified responsibility is moved. The specification only canonicalizes terminology that was already implied by certified PGSP architecture and confirmed by G12-04.

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: PGSP_CANONICAL_RESPONSIBILITY_SPECIFIED
