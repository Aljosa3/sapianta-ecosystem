# G11-01 ACLI Next Conversational Development Session Specification V1

Status: ACLI Next conversational session specified.

Final verdict: ACLI_NEXT_CONVERSATIONAL_SESSION_SPECIFIED

## 1. Executive Summary

Generation 10 certified ACLI Next as the canonical operational interface for governed Platform Core development.

Generation 11 begins by improving how that certified interface is used in daily development.

This review determines that the required runtime capabilities for conversational development largely already exist across certified ACLI Next, session, execution-plan, dashboard, Governance, Replay, Worker Platform, Platform Digital Twin, Architectural Health, and Governed Development Workflow components.

The remaining gap is primarily UX:

```text
the current ACLI Next interactive command exposes low-level session and turn machinery instead of a natural conversational development loop
```

Therefore, the recommended next capability is a thin conversational ACLI Next experience that composes existing certified capabilities and removes unnecessary manual parameters.

This is a UX evolution only.

It must not introduce a new authority layer, new orchestration engine, new Platform Core responsibility, duplicated Governance logic, duplicated Replay logic, duplicated Worker execution, or duplicated Architectural Health reasoning.

## 2. Governed Development Workflow Compliance

This specification follows the certified Governed Development Workflow:

```text
Capability Discovery
-> Existing Capability Audit
-> Reuse
-> Canonicalization
-> Minimal Extension
-> Implementation
-> Architectural Health Review
-> Architecture Review
-> Certification
```

Current task position:

| Workflow Stage | Result |
| --- | --- |
| Capability Discovery | Need identified: natural conversational ACLI Next development session. |
| Existing Capability Audit | Existing session, turn, execution-plan, dashboard, Governance, Replay, Worker, and workflow capabilities reviewed. |
| Reuse | Existing certified components are sufficient for the runtime foundation. |
| Canonicalization | Required now: define canonical conversational UX behavior. |
| Minimal Extension | Required later: thin ACLI Next wrapper that manages human-facing conversation ergonomics. |
| Implementation | Not performed in this artifact. |
| Architectural Health Review | Required after implementation. |
| Architecture Review | Required after implementation. |
| Certification | Required after architecture review. |

## 3. Existing Capability Audit

### 3.1 Interactive Runtime

Existing capability:

- `aigol/acli_next/interactive.py`
- command: `aigol next interactive`
- supports replay-visible multi-turn ACLI Next sessions;
- records session start, turn records, and completion;
- enforces continuation rules;
- delegates each turn to the ACLI Next session entrypoint;
- preserves non-authority flags such as no provider invocation, no worker invocation, no approval creation, no authorization creation, no repository mutation, and no deployment.

Finding:

The interactive runtime already provides deterministic turn recording, but it expects explicit session and turn input. This is a low-level runtime surface rather than a natural conversational operator experience.

### 3.2 Session Runtime

Existing capability:

- `aigol/acli_next/entrypoint.py`
- command: `aigol next session`
- creates non-mutating ACLI Next sessions;
- delegates to existing governed development session entrypoints;
- records replay-visible session artifacts.

Finding:

Session creation exists. The UX gap is automatic session creation, resume, naming, and context display when the human runs `aigol next` without explicit session parameters.

### 3.3 Development Session Lifecycle

Existing capability:

- `aigol/runtime/acli_development_session_lifecycle.py`
- creates replay-visible session lifecycle artifacts;
- records confirmation checkpoints;
- records recovery states;
- preserves governance checkpoints;
- explicitly avoids creating approvals, authorizations, or execution requests.

Finding:

Session lifecycle is already available and should be reused for conversational state continuity.

### 3.4 Conversational Development Session Runtime

Existing capability:

- `aigol/runtime/acli_conversational_development_session.py`
- starts conversational development context for an existing ACLI session;
- records deterministic turns;
- preserves parent-turn continuity;
- records clarification, proposal, confirmation, and continuation statuses;
- reconstructs and validates conversational session replay.

Finding:

Conversational turn processing already exists. The UX gap is making it the normal `aigol next` experience instead of a low-level artifact-oriented interface.

### 3.5 Execution-Plan Runtime

Existing capability:

- `aigol/acli_next/execution_plan.py`
- command: `aigol next execution-plan`
- runs interactive ACLI Next sessions and delegates advisory execution planning to Platform Core;
- exposes worker sequence, requested capabilities, expected artifacts, mutation preview, risk summary, and replay references;
- does not authorize execution or invoke workers.

Finding:

Execution planning already exists as a Platform Core-delegated preview. Conversational ACLI Next should surface this as the natural "proposed next step" view.

### 3.6 Dashboard

Existing capability:

- `aigol/acli_next/daily_dashboard.py`
- `aigol/runtime/platform_core_daily_operational_exposure.py`
- command: `aigol next dashboard`
- displays workflow, task, Governance, validation, Replay, Architectural Health, and hybrid status;
- consumes Platform Core operational snapshots;
- includes explicit non-authority flags.

Finding:

Dashboard presentation already exists and should become the default conversational context panel.

### 3.7 Governed Development Workflow

Existing capability:

- `aigol/runtime/governed_development_workflow_runtime.py`
- composes governance artifact creation and governed repository mutation;
- enforces proposal, approval, component ordering, Replay, and fail-closed behavior.

Finding:

The canonical development workflow already exists. Conversational ACLI Next must guide the human into this workflow rather than creating an alternate flow.

### 3.8 Governance, Replay, Worker Platform, Platform Digital Twin, Architectural Health

Existing certified capabilities:

- Governance authorizes, approves, admits, and certifies.
- Replay records evidence and supports reconstruction.
- Worker Platform executes bounded authorized operations.
- Platform Digital Twin projects canonical architectural evidence.
- Architectural Health produces deterministic advisory findings only.

Finding:

No ownership movement is required. Conversational ACLI Next should present and route to these capabilities only through Platform Core and existing certified interfaces.

## 4. Capability Reuse Analysis

| Required Capability | Existing Source | Reuse Finding |
| --- | --- | --- |
| Session lifecycle | ACLI development session lifecycle runtime | Reuse directly. |
| Natural session start | Existing session runtime plus new thin UX defaults | Minimal UX extension. |
| Session resume | Conversation/session continuity runtimes | Reuse; expose naturally. |
| Turn processing | Conversational development session runtime and interactive runtime | Reuse directly. |
| Workflow tracking | Platform Core operational snapshot and dashboard | Reuse directly. |
| Execution planning | ACLI Next execution-plan adapter and Platform Core planning service | Reuse directly. |
| Replay generation | Existing Replay-owning runtimes | Reuse; ACLI Next displays only. |
| Governance integration | Existing Governance artifacts and approval flows | Reuse; ACLI Next displays and guides only. |
| Worker execution | Existing Worker Platform paths | Reuse; no direct ACLI execution. |
| Dashboard updates | Daily operational dashboard | Reuse; refresh after turns. |
| Architectural Health | Existing advisory outputs and dashboard display | Reuse; advisory only. |
| Hybrid guidance | Platform Core daily operational exposure | Reuse; expand UX rendering only. |

Conclusion:

The conversational development session can be implemented by composing existing capabilities.

The missing behavior is not a Platform Core capability gap. It is a human-facing interaction gap.

## 5. Canonical Conversational UX Model

Canonical command:

```text
aigol next
```

Canonical interaction:

```text
AiGOL>
```

Example:

```text
Human
-> aigol next
-> AiGOL> Implement governed Git remote workflow.
-> Platform Core
-> Governed Development Workflow
-> Capability Discovery
-> Existing Capability Audit
-> Reuse Decision
-> Implementation Proposal
-> Governance
-> Replay
-> Architectural Health
-> Human Confirmation
```

The conversational shell must:

- create or resume a session automatically;
- accept plain development intent;
- display the current workflow stage;
- display the active task and next expected action;
- surface Governance, Replay, validation, and Architectural Health state;
- offer deterministic next actions;
- delegate all actual workflow state to Platform Core;
- preserve the ability to fail closed;
- return to the prompt after each completed turn or required human action.

The conversational shell must not:

- infer authorization;
- execute workers directly;
- mutate repository state directly;
- create hidden approvals;
- perform Replay ownership;
- classify Architectural Health findings independently;
- replace the Governed Development Workflow.

## 6. Session Lifecycle Specification

### 6.1 Session Start

When the human runs:

```text
aigol next
```

ACLI Next should:

1. request or derive a deterministic session identity through existing session lifecycle capability;
2. create a replay-visible session lifecycle artifact;
3. load the current Platform Core operational snapshot;
4. render the dashboard context;
5. present the `AiGOL>` prompt.

The human should not be required to provide:

- explicit `--session-id`;
- explicit `--turn`;
- manual replay directory;
- repetitive workspace arguments.

Defaults must be deterministic and replay-visible.

### 6.2 Session Resume

When a prior active session exists, ACLI Next should:

- present the latest active session;
- show current workflow state;
- show pending approvals or pending external operations;
- ask whether to continue or start a new session when ambiguity exists.

ACLI Next may guide the human, but Platform Core and Replay remain the authorities for state and evidence.

### 6.3 Session Completion

A session may complete when:

- the workflow reaches certification or terminal review;
- the human explicitly closes the session;
- a fail-closed condition blocks continuation;
- the workflow transitions to a documented hybrid exception.

Completion must produce replay-visible evidence through existing Replay-owned mechanisms.

## 7. Turn Lifecycle Specification

Each conversational turn should follow this deterministic lifecycle:

1. Capture human input.
2. Bind input to the active session.
3. Record turn metadata through existing conversational development session runtime.
4. Delegate intent/context evaluation to certified Platform Core workflow components.
5. Display current workflow stage and next expected action.
6. Display proposed reuse, canonicalization, or minimal extension decision where available.
7. Display Governance state when approval or authorization is required.
8. Display Replay references when evidence is created.
9. Display Architectural Health findings when available.
10. Return to `AiGOL>` or terminate fail-closed.

Turn output should be human-readable and operationally direct:

```text
Stage: Existing Capability Audit
Task: Governed Git remote workflow
Finding: local Git commit exists; remote push remains uncertified
Next: create readiness review
Governance: approval not yet required
Replay: turn recorded
Architectural Health: no advisory findings
```

ACLI Next may format this output.

ACLI Next may not become the authority for any field displayed.

## 8. Platform Core Interaction Model

Conversational ACLI Next interacts with Platform Core as a consumer.

Allowed interaction:

- request current operational snapshot;
- request workflow-stage display data;
- request execution-plan previews;
- request capability discovery and reuse evidence when exposed by Platform Core;
- present Governance, Replay, validation, and Architectural Health summaries already produced by certified owners.

Disallowed interaction:

- direct execution authorization;
- direct Worker invocation;
- direct Replay record ownership;
- direct Architectural Health reasoning;
- local duplicate workflow state;
- local duplicate approval state.

Platform Core remains the coordination authority.

## 9. Hybrid Transition Model

If a request exceeds certified Platform Core capability, ACLI Next should display:

```text
This operation is outside certified governed capability.
Reason: <specific boundary>
Required external operation: <tool/action>
Replay continuity requirement: <evidence to record>
Governance continuity requirement: <approval or disclosure requirement>
Return condition: <when to resume ACLI Next>
```

Examples:

| Boundary | ACLI Next Guidance |
| --- | --- |
| Git remote operation | Explain that remote Git is not yet certified; require explicit external command evidence; return after remote state is captured. |
| Dependency installation | Explain registry and lockfile boundary; require dependency intent, lockfile diff, and validation evidence. |
| Deployment | Explain release and environment authority boundary; require release evidence and rollback readiness. |
| Exceptional environment work | Explain OS or infrastructure boundary; require scope, result, and continuity record. |

ACLI Next must not perform the external operation.

ACLI Next must guide return to the governed workflow as soon as certified coverage resumes.

## 10. Ownership Verification

| Component | Required Conversational Role | Authority Preserved |
| --- | --- | --- |
| ACLI Next | Presents prompt, dashboard context, summaries, and next-action guidance. | No authorization, execution, Replay ownership, certification, or Architectural Health reasoning. |
| Platform Core | Coordinates workflow state and capability composition. | Remains orchestration authority. |
| OCS | Forms candidates and proposals. | Remains candidate authority. |
| Governance | Approves, authorizes, admits, and certifies. | Remains authorization authority. |
| Replay | Records evidence and reconstructs sessions. | Remains evidence authority. |
| Worker Platform | Executes bounded authorized operations. | Remains execution authority. |
| Platform Digital Twin | Projects canonical architectural evidence. | Remains evidence projection authority. |
| Architectural Health | Produces deterministic advisory findings. | Remains advisory only. |
| Human Authority | Reviews, confirms, and retains constitutional authority. | Remains final authority. |

No ownership movement is permitted.

## 11. Minimal Extension Requirements

The implementation should add only a thin ACLI Next conversational presentation wrapper.

Required minimal extension:

- `aigol next` conversational command;
- automatic deterministic session start or resume;
- natural prompt loop;
- turn capture without manual `--turn`;
- default replay location derived from session identity;
- dashboard refresh after each turn;
- clear display of current stage, next action, Governance, Replay, validation, Architectural Health, and hybrid status;
- graceful fail-closed termination;
- explicit return guidance for hybrid exceptions.

The implementation should reuse:

- ACLI Next session runtime;
- interactive runtime;
- conversational development session runtime;
- session lifecycle runtime;
- execution-plan runtime;
- daily dashboard runtime;
- Governed Development Workflow runtime;
- Platform Core operational snapshot;
- certified Governance, Replay, Worker, Platform Digital Twin, and Architectural Health capabilities.

## 12. Non-Goals

This specification does not authorize:

- provider invocation;
- autonomous transaction planning;
- Git remote execution;
- dependency installation;
- deployment;
- direct Worker execution from ACLI Next;
- direct file mutation from ACLI Next;
- new Platform Core services;
- new runtime authority layers;
- new orchestration engines.

## 13. Implementation Readiness

Implementation readiness finding:

```text
ready for minimal ACLI Next UX extension
```

Rationale:

- session lifecycle exists;
- turn processing exists;
- execution planning exists;
- Replay generation exists;
- Governance integration exists;
- dashboard exposure exists;
- Architectural Health presentation exists;
- hybrid guidance exists;
- the remaining gap is parameter-heavy CLI ergonomics and conversational continuity presentation.

Required next artifact:

```text
G11_02_ACLI_NEXT_CONVERSATIONAL_DEVELOPMENT_SESSION_IMPLEMENTATION_V1
```

Expected implementation verdict:

```text
ACLI_NEXT_CONVERSATIONAL_SESSION_IMPLEMENTED
```

## 14. Final Determination

The ACLI Next conversational development session is specified.

The capability should be implemented as a thin UX layer that composes existing certified Platform Core capabilities.

It should make `aigol next` the natural daily conversational entrypoint while preserving every certified ownership boundary.

Final verdict: ACLI_NEXT_CONVERSATIONAL_SESSION_SPECIFIED

## 15. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: ACLI_NEXT_CONVERSATIONAL_SESSION_SPECIFIED
