# G4-03 First Governed Self-Development Use Case V1

Status: FIRST SELF-DEVELOPMENT USE CASE DEFINED

Final verdict: G4_03_READY

## 1. Purpose

Generation 4 now contains an executable governed development scaffold.

The next objective is to validate the primary project vision:

> AiGOL evolves itself through natural-language interaction mediated by ACLI and
> governed by certified Platform Core services.

This document defines the first complete governed self-development use case. It
is a scenario and certification artifact only. It does not introduce runtime
changes, provider execution, worker execution, repository mutation, deployment,
approval, or authorization.

Execution may remain advisory-only.

## 2. Use Case Summary

Use case name:

`FIRST_GOVERNED_SELF_DEVELOPMENT_REPLAY_EVIDENCE_REQUEST`

Example human request:

> Add replay evidence for X.

Scenario-specific request:

> Add replay evidence for the G4 governed development scaffold.

Expected result:

AiGOL processes the request through ACLI, UBTR, CSA, OCS, UHCL, human
confirmation, governed execution intent, and replay evidence without mutating
the repository.

The use case proves the governed development loop can transform a natural
language self-development request into replay-visible advisory execution intent.

## 3. Interaction Sequence

| Step | Actor / component | Interaction | Evidence |
| --- | --- | --- | --- |
| 1 | Human | Enters: "Add replay evidence for the G4 governed development scaffold." | Raw natural-language intent |
| 2 | ACLI | Captures the request as adapter input. | ACLI input artifact, adapter metadata, input hash |
| 3 | UBTR | Translates the human request into canonical governance/development meaning. | UBTR translation artifact, source hash, translation lineage |
| 4 | CSA | Creates the structured intent representation. | CSA structured intent artifact, canonical semantic hash |
| 5 | OCS | Prepares an advisory proposal for replay evidence addition. | OCS proposal artifact, assumptions, risks, alternatives, recommended next step |
| 6 | Governance | Evaluates execution prerequisites and authority boundaries. | Governance checkpoint artifact |
| 7 | UHCL | Presents explanation, risks, assumptions, alternatives, and confirmation prompt. | UHCL communication artifact, shared confirmation artifact |
| 8 | ACLI | Renders UHCL artifact in terminal form. | ACLI render artifact |
| 9 | Human | Confirms, modifies, rejects, clarifies, or continues. | Human response artifact mapped to canonical UHCL response class |
| 10 | OCS / Governance | Prepares advisory execution intent. | Advisory execution intent artifact |
| 11 | Replay | Reconstructs the complete loop. | Replay package, artifact hashes, lineage graph |

No repository mutation occurs in G4-03.

## 4. Responsibility Boundaries

| Component | Responsibility | Boundary |
| --- | --- | --- |
| Human | Express self-development intent and choose a response. | Human response does not bypass governance. |
| ACLI | Capture input, render UHCL output, capture response, map response class. | No semantic translation or reusable communication meaning. |
| UBTR | Own natural-language semantic translation. | No execution authority. |
| CSA | Own structured intent representation. | No proposal or execution authority. |
| OCS | Own advisory proposal and execution-intent preparation. | No repository mutation, provider invocation, or worker execution. |
| UHCL | Own reusable human-facing explanation and confirmation. | No approval, authorization, or execution authority. |
| Governance | Own checkpoints, policy boundaries, approval requirements, authorization requirements, and fail-closed state. | Does not delegate authority to ACLI or UHCL. |
| Replay | Own deterministic reconstruction and evidence continuity. | Does not mutate governance or authorize execution. |

## 5. Governance Checkpoints

| Checkpoint | Required result |
| --- | --- |
| Adapter boundary | ACLI remains adapter-only. |
| Semantic boundary | UBTR is the only semantic translation authority. |
| Structured intent boundary | CSA produces the canonical structured intent. |
| OCS boundary | OCS prepares advisory proposal and execution intent only. |
| Communication boundary | UHCL owns explanations and confirmation model. |
| Provider boundary | Provider execution is not invoked. |
| Worker boundary | Worker execution is not invoked. |
| Approval boundary | Any future mutation requires explicit approval evidence. |
| Authorization boundary | Any future executable action requires authorization evidence. |
| Mutation boundary | Repository mutation is unavailable in this use case. |
| Replay boundary | All artifacts are reconstructable and hash-bound. |

Expected governance status:

`ADVISORY_ONLY_CHECKPOINT_PASSED`

Expected execution intent status:

`BLOCKED_PENDING_GOVERNANCE`

## 6. Replay Checkpoints

The use case requires replay evidence for:

1. ACLI natural-language input capture.
2. UBTR translation artifact.
3. CSA structured intent artifact.
4. UBTR to OCS handoff artifact.
5. OCS advisory proposal artifact.
6. Governance checkpoint artifact.
7. UHCL shared confirmation artifact.
8. UHCL communication artifact.
9. ACLI render artifact.
10. Human response artifact.
11. Advisory execution intent artifact.
12. Scaffold summary artifact.

Replay must prove:

- artifact ordering;
- artifact hash integrity;
- source evidence lineage;
- non-authority flags;
- provider and worker non-invocation;
- repository non-mutation;
- deterministic reconstruction.

## 7. Evidence Model

| Evidence class | Required fields | Certification purpose |
| --- | --- | --- |
| Input evidence | request text, request hash, adapter id, session context | Proves human-originating self-development intent |
| Translation evidence | UBTR translation id, source direction, normalized intent, governance payload, hash | Proves semantic ownership |
| CSA evidence | semantic artifact id, workflow identity, confidence, ambiguity, hash | Proves structured intent representation |
| OCS evidence | proposal id, summary, assumptions, risks, alternatives, recommended next step, hash | Proves advisory proposal preparation |
| Governance evidence | checkpoint id, missing prerequisites, boundary flags, hash | Proves execution remains governed |
| UHCL evidence | communication id, confirmation prompt, sections, source bindings, hash | Proves reusable human communication |
| ACLI render evidence | render id, source artifact hash, communication level, render hash | Proves adapter-only rendering |
| Human response evidence | raw response hash, canonical UHCL response class, response hash | Proves confirmation path |
| Execution intent evidence | advisory intent id, blocked status, required prerequisites, hash | Proves no execution occurs without governance |
| Replay evidence | wrapper hashes, artifact hashes, reconstruction result | Proves deterministic replay |

## 8. Human Interaction

The human-facing sequence shall be:

1. Human enters the self-development request.
2. ACLI displays UHCL explanation of what AiGOL understood.
3. ACLI displays the OCS advisory proposal, including:
   - what replay evidence would be added;
   - why execution cannot proceed yet;
   - what prerequisites are missing;
   - what alternatives are available.
4. UHCL asks for a canonical response:
   - confirm;
   - clarify;
   - modify;
   - reject;
   - continue.
5. ACLI captures the raw response and maps it to the canonical UHCL response
   class.
6. Governance records advisory execution intent as blocked pending approval,
   authorization, worker readiness, and mutation certification.

No natural-language response from the human grants execution authority by
itself.

## 9. Certification Criteria

The use case is certified when:

- ACLI captures the human request without owning semantics;
- UBTR creates the canonical translation artifact;
- CSA creates the structured intent artifact;
- OCS creates an advisory proposal artifact;
- UHCL presents explanation and confirmation artifacts;
- ACLI renders UHCL output without creating communication semantics;
- human response is mapped to a canonical UHCL response class;
- governance checkpoints preserve approval, authorization, provider, worker,
  mutation, and replay boundaries;
- advisory execution intent is recorded as blocked pending governance;
- replay reconstructs the full path deterministically;
- repository mutation remains false;
- provider invocation remains false;
- worker execution remains false.

## 10. Success Metrics

| Metric | Target |
| --- | --- |
| Natural-language entry | One self-development request entered through ACLI. |
| Semantic ownership | 100 percent of semantic translation traced to UBTR. |
| Structured intent ownership | One CSA structured intent artifact created and hash-bound. |
| OCS proposal | One advisory OCS proposal artifact created. |
| UHCL communication | At least one UHCL communication artifact and one shared confirmation artifact created. |
| Human response | One canonical UHCL response class captured. |
| Replay reconstruction | Full loop reconstructs with all expected artifacts. |
| Provider execution | False. |
| Worker execution | False. |
| Repository mutation | False. |
| Deployment | False. |
| Governance result | Advisory-only checkpoint passed and execution intent blocked pending governance. |

## 11. Non-Goals

G4-03 does not:

- implement repository mutation;
- create approval evidence;
- create authorization evidence;
- invoke providers;
- execute workers;
- deploy software;
- replace the G4-02 scaffold;
- expand Platform Services.

## 12. Recommended Next Implementation Batch

Recommended next batch:

`G4_04_ACLI_SELF_DEVELOPMENT_USE_CASE_COMMAND_BINDING_V1`

Scope:

- bind the G4-02 scaffold to an ACLI command for the first self-development use
  case;
- use the G4-03 scenario as the fixture;
- emit replay evidence for the complete advisory loop;
- preserve advisory-only behavior;
- keep provider execution, worker execution, approval, authorization,
  repository mutation, and deployment disabled.

## 13. Final Determination

The first governed self-development use case is defined.

It directly validates the primary Generation 4 vision: AiGOL can evolve itself
through natural-language interaction mediated by ACLI, interpreted by UBTR,
structured by CSA, proposed by OCS, communicated by UHCL, constrained by
Governance, and reconstructed by Replay.

Final verdict: G4_03_READY
