# G4-01 ACLI Governed Natural-Language Development Loop V1

Status: DEVELOPMENT LOOP DESIGN CERTIFICATION COMPLETE

Final verdict: G4_01_READY

## 1. Purpose

Generation 4 begins from the certified Generation 3 Platform Core architecture
and the Generation 4 execution principles.

This document defines the complete governed natural-language development loop
for ACLI as the first interface adapter. It is a design and certification
artifact. It does not introduce runtime behavior, provider invocation, worker
execution, approval, authorization, deployment, or repository mutation.

The objective is to demonstrate the intended end-to-end path for replacing the
current ChatGPT/Codex copy-paste workflow with governed natural-language AiGOL
development mediated through ACLI and owned by Platform Core.

Execution may remain advisory-only until Provider Services, Worker Services, and
mutation boundaries are certified for operational activation.

## 2. End-To-End Interaction Sequence

| Step | Interaction | Canonical owner | Evidence produced | Authority impact |
| --- | --- | --- | --- | --- |
| 1 | Human expresses development intent in natural language through ACLI. | Human / ACLI adapter | Raw input text, session reference, interface adapter reference | No authority created |
| 2 | ACLI captures the input and submits it to Platform Core. | ACLI adapter | Input capture artifact, adapter metadata, capture timestamp or deterministic ordering reference | ACLI remains adapter-only |
| 3 | UBTR performs canonical semantic translation. | UBTR | UBTR semantic artifact, translation lineage, source input hash | No execution authority |
| 4 | CSA creates or updates the structured intent representation. | CSA | CSA structured intent artifact, canonical representation hash, semantic lineage | No execution authority |
| 5 | OCS assembles context and prepares governed proposal candidates. | OCS | OCS context bundle, proposal candidate bundle, assumptions, risks, alternatives | Advisory only |
| 6 | Provider Services may supply reusable cognition evidence when available. | Provider Services / OCS boundary | Provider cognition summary, provider provenance, credential-reference-only evidence | No provider invocation unless separately authorized |
| 7 | Worker Services may identify eligible execution paths when available. | Worker Services / OCS boundary | Worker capability summary, lifecycle status, execution-readiness evidence | No worker execution |
| 8 | Governance evaluates the proposal path against policy, conformance, approval, authorization, and mutation boundaries. | Governance | Governance checkpoint evidence, policy result, fail-closed reason when blocked | Authority remains governed |
| 9 | UHCL renders explanation, alternatives, risks, recovery guidance, and confirmation choices. | UHCL | UHCL communication artifact, typed section lineage, source evidence binding | Communication does not grant authority |
| 10 | ACLI formats the UHCL artifact for terminal presentation. | ACLI adapter | Adapter render evidence, selected communication level, terminal formatting reference | Adapter-only |
| 11 | Human confirms, modifies, rejects, requests clarification, or continues. | Human / UHCL response model via ACLI capture | Raw response input, canonical UHCL response class, response evidence binding | Human response may request next step but does not bypass gates |
| 12 | Confirmed development intent is prepared for the appropriate execution path. | OCS / Governance / Provider Services / Worker Services | Execution-intent artifact, required approval or authorization references, readiness or blockage evidence | Execution remains blocked unless governance permits |
| 13 | Replay records deterministic reconstruction evidence for the full loop. | Replay | Replay packet, artifact hashes, lineage graph, reconstruction references | Replay is evidence only |
| 14 | Validation or certification records the outcome of the advisory or executable loop. | Governance / Replay | Validation result, known limitations, rollback reference | No hidden mutation |

## 3. Responsibility Matrix

| Component | Responsibility in G4-01 | Explicit non-responsibility |
| --- | --- | --- |
| Human | Express intent, evaluate presented alternatives, choose confirmation response, retain final constitutional authority where applicable. | Does not bypass governance checkpoints through natural-language phrasing. |
| ACLI | Capture raw input, submit it to Platform Core, select communication level, render UHCL artifacts, capture raw responses, map input to canonical UHCL response classes. | Does not translate semantics, generate reusable explanations, own confirmation logic, invoke providers, execute workers, authorize execution, mutate repositories, or own replay. |
| UBTR | Own canonical semantic translation from natural language into Platform Core meaning. | Does not render interface-specific output or grant execution authority. |
| CSA | Own structured intent representation and deterministic semantic hashes. | Does not decide execution or communicate directly to humans outside UHCL-bound artifacts. |
| OCS | Own cognition orchestration, context assembly, proposal preparation, alternatives, and advisory execution-intent preparation. | Does not bypass governance, approval, authorization, provider boundaries, worker boundaries, or mutation controls. |
| UHCL | Own reusable human communication, typed sections, explanations, confirmation model, recovery guidance, and Provider/Worker/Product communication bindings. | Does not capture terminal input directly, grant approval, authorize execution, invoke providers, execute workers, or own replay. |
| Provider Services | Provide reusable cognition evidence, provider identity, provenance, governance status, and credential-reference-only evidence where available. | Do not become ACLI-owned and do not perform invocation in G4-01. |
| Worker Services | Provide worker capability, lifecycle, readiness, and advisory execution-path evidence where available. | Do not execute workers or mutate repositories in G4-01. |
| Governance | Own policy, approval, authorization, conformance, fail-closed checks, mutation boundaries, and certification gates. | Does not delegate authority to communication artifacts or adapter output. |
| Replay | Own deterministic reconstruction, replay packets, hashes, lineage, and evidence continuity. | Does not own semantic translation, communication meaning, or governance decisions. |
| Product 1 | May consume resulting Platform Core evidence as AI Decision Validator context. | Does not own the development loop, provider activation, worker execution, governance, replay, UBTR, or UHCL. |

## 4. Required Platform Services

The governed natural-language development loop requires:

- ACLI adapter capture and rendering;
- UBTR semantic translation;
- CSA structured intent representation and hash lineage;
- OCS cognition orchestration and proposal preparation;
- UHCL reusable communication artifacts and response classes;
- Provider Services for optional cognition summaries and provenance;
- Worker Services for optional execution-path summaries and lifecycle evidence;
- Governance policy, approval, authorization, conformance, and fail-closed
  checks;
- Replay deterministic reconstruction and evidence lineage;
- deterministic serialization for artifact comparison and replay visibility.

G4-01 does not require live provider invocation, live worker execution, repository
mutation, deployment, or autonomous recovery.

## 5. Governance Checkpoints

| Checkpoint | Required verification | Fail-closed behavior |
| --- | --- | --- |
| Input boundary | ACLI must record raw input and adapter metadata before Platform Core processing. | Reject untraceable input. |
| Semantic ownership | UBTR must be the source of canonical semantic translation. | Reject interface-owned or product-owned semantic interpretation. |
| Structured intent | CSA must produce deterministic structured representation and lineage. | Block proposal preparation when representation is missing or inconsistent. |
| Proposal preparation | OCS must produce advisory proposals with assumptions, alternatives, risks, and evidence references. | Return recovery guidance when proposal evidence is incomplete. |
| Communication ownership | UHCL must produce reusable human-facing communication. | Block reusable ACLI-local explanation or confirmation semantics. |
| Human response classification | Captured input must map to canonical UHCL confirmation classes. | Continue as clarification or recovery guidance when response is ambiguous. |
| Provider boundary | Provider evidence must use canonical Provider Services and credential references only. | Block hidden provider invocation. |
| Worker boundary | Worker evidence must use canonical Worker Services readiness and lifecycle evidence. | Block hidden worker execution. |
| Approval boundary | Any approval requirement must be represented by approval evidence, not by UHCL text. | Block execution intent when approval is missing. |
| Authorization boundary | Any executable action must pass authorization readiness checks. | Block execution and present recovery guidance. |
| Mutation boundary | Repository mutation must remain unavailable unless a certified governed mutation path exists. | Preserve advisory-only result. |
| Replay boundary | All artifacts must be deterministically reconstructable. | Mark loop uncertified when replay lineage is incomplete. |

## 6. Replay Evidence

The loop is replay-visible when the following evidence can be reconstructed:

| Evidence class | Required content | Replay purpose |
| --- | --- | --- |
| ACLI input capture | Raw natural-language intent, adapter id, session or turn reference | Reconstruct the human-originating request |
| UBTR semantic artifact | Semantic translation, source input hash, translation lineage | Prove canonical semantic ownership |
| CSA representation | Structured intent, canonical hash, semantic lineage reference | Reconstruct the intent object used by OCS |
| OCS proposal bundle | Context, assumptions, alternatives, risks, recommendations, blocked actions | Reconstruct advisory reasoning and proposal options |
| Provider evidence | Provider summary, provenance, identity references, credential-reference-only lineage | Reconstruct optional cognition evidence without exposing secrets |
| Worker evidence | Worker capability, lifecycle, readiness, and blocked execution references | Reconstruct optional execution-path evidence |
| Governance checkpoint evidence | Policy result, approval requirements, authorization requirements, conformance result | Prove authority boundaries were preserved |
| UHCL communication artifact | Typed sections, explanation level, confirmation model, recovery guidance, source evidence binding | Reconstruct what reusable communication meant |
| ACLI render evidence | Terminal formatting, communication level selection, adapter render reference | Reconstruct interface presentation without making ACLI canonical |
| Human response artifact | Raw response input, canonical UHCL response class, response lineage | Reconstruct the human decision point |
| Execution-intent artifact | Advisory execution intent, required gates, readiness or blockage state | Reconstruct why execution did or did not proceed |
| Final validation record | Outcome, known gaps, rollback reference | Preserve certification and rollback continuity |

## 7. Success Criteria

G4-01 succeeds when the designed loop proves that:

1. A human can express development intent in natural language through ACLI.
2. ACLI remains an adapter and does not own semantic translation or reusable
   communication.
3. UBTR owns all semantic translation.
4. CSA owns deterministic structured intent representation.
5. OCS prepares governed advisory proposals and execution intent.
6. UHCL presents explanations, alternatives, confirmations, and recovery
   guidance without granting authority.
7. Human responses are captured and classified into canonical UHCL response
   classes.
8. Provider and Worker evidence can be referenced without invocation or
   execution.
9. Governance checkpoints preserve approval, authorization, conformance, and
   mutation boundaries.
10. Replay can reconstruct the full natural-language development loop.
11. The path directly advances replacement of ChatGPT/Codex copy-paste with a
    governed ACLI-mediated workflow.

## 8. Certification Criteria

The loop is certifiable when:

- no duplicate semantic layer is introduced outside UBTR;
- no duplicate reusable communication layer is introduced outside UHCL;
- no ACLI-owned provider invocation or worker execution path is introduced;
- no Product 1 platform ownership is introduced;
- OCS remains the proposal and cognition orchestration owner;
- Provider Services and Worker Services remain reusable Platform Services;
- approval and authorization remain Governance-owned;
- replay owns deterministic reconstruction;
- repository mutation remains blocked unless a separately certified governed
  mutation path exists;
- advisory-only behavior is explicit wherever activation is not yet certified.

## 9. Remaining Implementation Gaps

The following gaps remain before the loop can become executable end to end:

| Gap | Required future work | Blocking impact |
| --- | --- | --- |
| ACLI command entrypoint | Implement a command path that captures natural-language development intent and submits it to UBTR. | Blocks operational use through ACLI. |
| UBTR-to-CSA loop wiring | Ensure captured intent produces deterministic CSA artifacts for development actions. | Blocks structured proposal preparation. |
| OCS proposal path | Bind development intent to OCS proposal generation, alternatives, risks, and advisory execution intent. | Blocks complete governed proposal flow. |
| UHCL render path | Ensure ACLI renders UHCL artifacts for each loop state and maps responses back to canonical classes. | Blocks adapter-only communication parity in the loop. |
| Provider Services binding | Optional cognition evidence must flow through canonical Provider Services and OCS boundaries. | Blocks provider-assisted advisory evidence. |
| Worker Services binding | Worker readiness and execution-path evidence must be canonicalized before real execution. | Blocks governed worker activation. |
| Replay fixtures | Add deterministic fixtures for raw input, UBTR, CSA, OCS, UHCL, response, and governance evidence. | Blocks runtime certification. |
| Governance test gates | Add tests for fail-closed approval, authorization, mutation, provider, and worker boundaries. | Blocks executable certification. |

These gaps do not block G4-01 as a design certification artifact. They define the
next implementation work.

## 10. Recommended Next Implementation Batch

Recommended next batch:

`G4_02_ACLI_GOVERNED_DEVELOPMENT_LOOP_REPLAY_SCAFFOLD_V1`

Scope:

- implement the ACLI natural-language development command scaffold;
- capture raw input and adapter metadata;
- route semantic translation through UBTR;
- produce CSA intent artifacts;
- prepare OCS advisory proposal bundles;
- render UHCL communication artifacts through ACLI;
- capture human responses as canonical UHCL response classes;
- record deterministic replay and governance checkpoint evidence;
- preserve advisory-only behavior where Provider Services, Worker Services, or
  repository mutation are not yet certified.

The batch must not introduce provider invocation, worker execution, approval
ownership, authorization ownership, deployment, repository mutation, or
interface-owned semantic or communication logic.

## 11. Final Determination

The G4-01 development loop design is aligned with the Generation 4 execution
principles and the certified Generation 3 Platform Core ownership model.

ACLI is the first interface adapter, UBTR owns semantic translation, CSA owns the
structured intent representation, OCS owns proposal orchestration, UHCL owns
human communication, Governance owns authority boundaries, and Replay owns
deterministic reconstruction.

The loop is ready to proceed to a replay-visible advisory implementation
scaffold.

Final verdict: G4_01_READY
