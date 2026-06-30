# G4-10 PGSP Public API Documentation And Adapter Contract V1

Status: PGSP public API contract defined.

Final verdict: PGSP_PUBLIC_API_READY

## 1. Purpose

This milestone defines the canonical public API contract for the Platform Governed Session Protocol, PGSP.

It is a documentation and contract-definition milestone only. It does not introduce a new runtime, facade, alias module, adapter framework, provider execution path, worker execution path, approval mechanism, authorization mechanism, repository mutation path, or deployment path.

Generation 4 has already established:

- PGSP as the canonical Platform Core session protocol.
- LGDS as the governed development-session specialization of PGSP.
- G4-04 as the reusable governed session API for the current development-session runtime.
- G4-05 as the current ACLI adapter entrypoint over the reusable session runtime.
- G4-09 as the decision that the existing public API is sufficient and no new facade runtime is currently required.

The purpose of this document is to make the existing public API contract explicit so future ACLI, Web, REST, Voice, Mobile, diagnostics, governance review, and replay review adapters can integrate without duplicating protocol ownership.

## 2. Non-Goals

This milestone does not:

- modify runtime behavior;
- introduce a new PGSP facade;
- rename existing runtime modules;
- change G4-02, G4-04, or G4-05 execution semantics;
- add provider execution;
- add worker execution;
- create approvals;
- create authorization;
- mutate repositories;
- deploy software;
- change replay artifact semantics.

PGSP is a canonical public contract over the existing governed session runtime lineage. It is not a new execution engine.

## 3. Canonical Public API Definition

The current canonical PGSP public API is the existing G4-04 governed session runtime.

### 3.1 Core PGSP Session Entrypoint

Canonical session execution API:

```text
run_g4_first_executable_governed_self_development_session(
    *,
    session_id: str,
    operator_request: str,
    operator_response: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]
```

Architectural role:

- reusable PGSP session execution API for the current LGDS specialization;
- invokes the existing G4-02 governed development loop scaffold;
- preserves UBTR, CSA, OCS, Governance, UHCL, and Replay ownership;
- returns deterministic advisory-only session evidence.

### 3.2 Core PGSP Replay Entrypoint

Canonical session replay API:

```text
reconstruct_g4_first_executable_self_development_session_replay(
    replay_dir: str | Path,
) -> dict[str, Any]
```

Architectural role:

- reconstructs the PGSP/LGDS session from replay artifacts;
- preserves deterministic evidence continuity;
- allows adapters and governance reviewers to inspect session evidence without rerunning semantic execution.

### 3.3 Development Loop Substrate

Substrate execution API:

```text
run_g4_governed_development_loop_scaffold(...)
```

Substrate replay API:

```text
reconstruct_g4_governed_development_loop_scaffold_replay(...)
```

Architectural role:

- executable governed development loop scaffold;
- lower-level protocol substrate used by the G4-04 session runtime;
- not the preferred public API for future interface adapters.

Adapters should call the canonical session API unless they are implementing a governed Platform Core internal runtime.

### 3.4 Current ACLI Adapter Entrypoint

Current ACLI adapter API:

```text
run_g4_live_acli_governed_development_session_entrypoint(
    *,
    session_id: str,
    operator_request: str,
    operator_response: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]
```

Current operator command:

```text
aigol g4-live-session
```

Architectural role:

- captures live ACLI request and response values;
- creates adapter-level replay evidence;
- routes into the existing G4-04 session runtime;
- renders adapter-specific terminal output;
- does not own semantic translation, governance, replay, UHCL communication, providers, workers, or execution authorization.

## 4. Session Lifecycle

The canonical PGSP session lifecycle is:

1. Interface adapter captures human input.
2. Adapter creates or receives a session identifier.
3. Adapter invokes the canonical PGSP session API.
4. UBTR translates the captured natural-language request into canonical semantic meaning.
5. CSA preserves structured intent artifacts.
6. OCS produces governed advisory orchestration proposals.
7. Governance evaluates checkpoints and admissibility constraints.
8. UHCL produces reusable human-facing communication.
9. Interface adapter renders UHCL output without generating reusable communication itself.
10. Human response is captured by the adapter.
11. Replay records deterministic evidence for session reconstruction.
12. Advisory execution intent is emitted without repository mutation, provider execution, worker execution, authorization, approval creation, or deployment.

The current G4-04/G4-05 runtime remains advisory-only and deterministic.

## 5. Input Contract

The canonical PGSP input contract for the current LGDS specialization consists of:

- `session_id`: stable caller-provided session identifier.
- `operator_request`: raw human natural-language request captured by an adapter.
- `operator_response`: human response to the governed communication loop.
- `created_at`: caller-provided timestamp string used for deterministic session evidence.
- `replay_dir`: caller-provided replay artifact directory.

Adapters may maintain adapter-local metadata, but they must not use metadata to bypass PGSP ownership boundaries.

Allowed future additive inputs include:

- `adapter_id`;
- `adapter_version`;
- `session_specialization`;
- `communication_level`;
- `session_context`;
- `request_origin`;
- `display_capabilities`.

These future inputs must remain additive and replay-visible. They must not transfer UBTR, CSA, OCS, Governance, UHCL, Replay, provider, or worker ownership into an interface adapter.

## 6. Output Contract

PGSP-compatible session outputs must provide enough structured evidence for:

- adapter rendering;
- replay reconstruction;
- governance review;
- certification review;
- deterministic audit continuity.

The current output model includes or preserves:

- session identifier;
- runtime version;
- session status;
- replay reference;
- replay hash or artifact hash evidence where available;
- governed development-loop scaffold evidence;
- CSA structured intent evidence;
- OCS advisory proposal evidence;
- governance checkpoint evidence;
- UHCL communication evidence;
- human response evidence;
- advisory execution intent;
- explicit non-execution state.

The current non-execution state must remain explicit:

- provider execution is not invoked;
- worker execution is not invoked;
- repository mutation is not performed;
- deployment is not performed;
- approval creation is not performed;
- authorization creation is not performed.

## 7. Replay Contract

PGSP replay evidence must be:

- deterministic;
- reconstructable from persisted artifacts;
- ordered according to the governed session lifecycle;
- visible to governance review;
- preserved across adapter types;
- independent of terminal rendering details.

Adapters must:

- preserve replay references returned by PGSP;
- avoid rewriting replay artifacts;
- avoid hiding nested replay evidence;
- avoid generating semantic replay substitutes;
- expose replay identifiers or paths in adapter-appropriate form.

The current replay lineage is:

```text
G4-05 adapter replay
  -> G4-04 governed session replay
    -> G4-02 governed development loop scaffold replay
```

Future adapters should preserve the same conceptual layering even when their transport or rendering model differs from ACLI.

## 8. Governance Contract

PGSP sessions must preserve governance constraints before any execution intent can be considered admissible.

The current Generation 4 governance contract is advisory-only:

- governance checkpoints are recorded;
- execution remains non-mutating;
- providers are not executed;
- workers are not executed;
- approvals are not created;
- authorizations are not created;
- deployments are not performed;
- repository mutation is prohibited.

Failure modes must remain fail-closed. Missing replay evidence, unmapped human responses, invalid session evidence, or governance checkpoint failures must not silently produce executable authority.

## 9. Adapter Contract

Interface adapters own:

- input capture;
- adapter-local session initiation;
- adapter-local transport concerns;
- rendering of PGSP/UHCL output;
- response capture;
- adapter-local display formatting;
- adapter-level replay references.

Interface adapters must not own:

- semantic interpretation;
- reusable explanations;
- reusable confirmations;
- recommendations;
- transparency semantics;
- recovery guidance;
- UBTR translation;
- CSA artifacts;
- OCS orchestration;
- governance checkpoints;
- replay semantics;
- provider logic;
- worker logic;
- execution authorization.

Adapters invoke PGSP. They do not become PGSP.

## 10. Platform Service Responsibilities

Platform Services remain reusable and adapter-independent.

| Capability | Owner | Adapter Role |
| --- | --- | --- |
| Human input capture | Interface Adapter | Capture raw input |
| Terminal, web, mobile, voice, or REST rendering | Interface Adapter | Render returned communication |
| Semantic translation | UBTR | No ownership |
| Structured intent | CSA | No ownership |
| Orchestration proposal | OCS | No ownership |
| Governance checkpointing | Governance | No ownership |
| Human communication | UHCL | Render only |
| Replay evidence | Replay | Preserve references |
| Provider cognition | Provider Services | No execution in G4-10 |
| Worker execution | Worker Services | No execution in G4-10 |
| Session protocol | PGSP | Invoke public API |

## 11. Ownership Matrix

| Concern | PGSP | LGDS | ACLI | Future Adapters | Platform Services |
| --- | --- | --- | --- | --- | --- |
| Canonical session protocol | Owns | Specializes | Invokes | Invoke | Support |
| Development session semantics | Defines contract | Owns specialization | Invokes | Invoke when development-focused | Support |
| Adapter input capture | Excludes | Excludes | Owns | Own | Exclude |
| Semantic translation | Uses UBTR | Uses UBTR | Excludes | Exclude | UBTR owns |
| Communication generation | Uses UHCL | Uses UHCL | Excludes | Exclude | UHCL owns |
| Governance checkpoints | Uses Governance | Uses Governance | Excludes | Exclude | Governance owns |
| Replay reconstruction | Requires | Requires | Preserves adapter evidence | Preserve adapter evidence | Replay owns |
| Provider execution | Excludes in current scope | Excludes in current scope | Excludes | Exclude unless future governed scope permits | Provider Services own |
| Worker execution | Excludes in current scope | Excludes in current scope | Excludes | Exclude unless future governed scope permits | Worker Services own |

## 12. Compatibility Guarantees

The PGSP public contract provides the following compatibility guarantees for Generation 4:

- G4-02, G4-04, and G4-05 runtime behavior remains unchanged.
- Existing replay artifacts remain valid.
- Existing runtime version identifiers remain authoritative.
- Existing ACLI command semantics remain valid.
- Future adapter contracts must be additive unless a later governance milestone explicitly certifies migration.
- PGSP naming does not require immediate module renaming.
- LGDS remains the current governed development-session specialization.
- Platform Service ownership is not changed by adapter integration.

No compatibility guarantee permits bypassing governance, replay, UBTR, UHCL, providers, workers, or Platform Core ownership boundaries.

## 13. Extension Model

PGSP extensions should follow these rules:

- add adapter metadata without changing canonical semantics;
- add session specializations without duplicating protocol runtime;
- add communication-level options through UHCL-owned semantics;
- add replay fields only when deterministic and reconstructable;
- add governance checkpoints through Governance-owned mechanisms;
- add provider or worker capabilities only through later governed milestones.

Future session specializations may include:

- governed product workflow sessions;
- governed business process sessions;
- governed diagnostics sessions;
- governed administration sessions;
- governed replay review sessions;
- governed governance review sessions;
- governed domain workflow sessions.

Each specialization should reuse PGSP and declare only specialization-specific constraints.

## 14. Versioning Strategy

Current runtime versions remain unchanged:

- `G4_GOVERNED_DEVELOPMENT_LOOP_EXECUTION_SCAFFOLD_V1`
- `G4_FIRST_EXECUTABLE_GOVERNED_SELF_DEVELOPMENT_SESSION_V1`
- `G4_05_LIVE_ACLI_GOVERNED_DEVELOPMENT_SESSION_ENTRYPOINT_V1`

This document defines the Generation 4 PGSP public API contract as:

```text
G4_10_PGSP_PUBLIC_API_DOCUMENTATION_AND_ADAPTER_CONTRACT_V1
```

Recommended future versioning rules:

- version adapter contracts independently from runtime modules;
- prefer additive fields for request and response models;
- preserve replay compatibility across minor adapter additions;
- require governance certification for breaking API changes;
- retain old replay readers when session artifacts are still in circulation;
- document deprecations before removing any public entrypoint.

## 15. Certification Criteria

A future adapter is PGSP-compatible only if it:

- invokes the canonical PGSP session API or a governance-certified successor;
- preserves raw human input as adapter-captured evidence;
- does not perform semantic translation locally;
- renders UHCL-owned communication without replacing it;
- preserves replay references and reconstruction paths;
- preserves governance checkpoint evidence;
- does not execute providers or workers unless a later governed milestone authorizes that scope;
- does not mutate repositories unless a later governed milestone authorizes that scope;
- does not create approvals or authorizations in the current Generation 4 scope;
- remains deterministic for the certified session mode.

Failure to satisfy any criterion requires adapter alignment before certification.

## 16. Recommended Next Implementation Batch

Recommended next batch:

```text
G4_11_PGSP_ADAPTER_CONTRACT_CONFORMANCE_CHECKLIST_V1
```

Recommended scope:

- create a certification checklist for future PGSP adapters;
- define evidence required for adapter conformance;
- identify the first non-ACLI adapter readiness criteria;
- preserve the current runtime unchanged unless a second adapter reveals a concrete contract gap.

The next batch should remain documentation and conformance oriented unless the user explicitly requests a second adapter implementation.

## 17. Final Determination

The canonical PGSP public API already exists through the G4-04 governed session runtime, with G4-05 serving as the current ACLI adapter.

The contract required for future adapters is now documented. No new runtime, facade, or adapter abstraction is required for G4-10.

Final verdict:

```text
PGSP_PUBLIC_API_READY
```
