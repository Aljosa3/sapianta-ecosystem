# G12-01 ACLI Next Message Composer Specification V1

Status: ACLI Next message composer specified.

Final verdict: ACLI_NEXT_MESSAGE_COMPOSER_SPECIFIED

## 1. Problem Statement

Generation 11 certified ACLI Next as the primary operational interface for governed Platform Core development and implemented a persistent conversational REPL.

Operational use of `aigol next` revealed a usability limitation:

```text
each input line is processed as an independent conversational turn
```

This behavior preserves certified ownership boundaries, but it fragments normal development requests. A single logical human message can become many governed turns, causing multiple Replay records, execution plans, dashboard updates, and conversational summaries for what the operator intended as one request.

G12-01 specifies a message composition layer for `aigol next` so the human can compose a complete multi-line message before submitting it to the certified Governed Development Workflow.

This is a UX specification only. It does not redesign Platform Core, Governance, Replay, Worker Platform, Platform Digital Twin, Architectural Health, or ACLI Next ownership.

## 2. Governed Development Workflow Compliance

This specification follows the certified Governed Development Workflow:

```text
Capability Discovery
-> Existing Capability Audit
-> Reuse
-> Canonicalization
-> Minimal Extension
-> Specification
-> Architectural Health Review
-> Architecture Review
-> Certification
```

Capability discovery finding:

```text
persistent ACLI Next sessions exist, but multi-line message composition does not
```

The missing behavior is pre-turn human message composition, not Platform Core orchestration.

## 3. Capability Audit

| Required Capability | Existing Certified Capability | Audit Finding |
| --- | --- | --- |
| Conversational runtime | `aigol/acli_next/conversational.py` | Existing single-turn adapter accepts complete prompt strings and delegates to certified runtimes. |
| Persistent conversational session | `run_acli_next_persistent_conversational_session(...)` | Existing REPL stays open across turns but submits each input line immediately. |
| Session persistence | Deterministic session root and `RUN-000001`, `RUN-000002`, ... directories | Existing session and run persistence should be reused. |
| Turn persistence | Existing per-run conversational artifacts | Existing persistence should remain one turn per submitted complete message. |
| Execution-plan runtime | `run_acli_next_interactive_with_execution_plan(...)` | Existing runtime should receive one complete request per submitted message. |
| Dashboard runtime | `run_acli_next_daily_dashboard(...)` | Existing dashboard refresh should occur once per submitted message. |
| Replay | Existing replay-visible session and turn artifacts | Replay ownership remains unchanged; composer may record presentation metadata only if implemented. |
| Platform Core orchestration | Certified Platform Core / Governed Development Workflow | Platform Core should receive complete requests only; no orchestration moves into ACLI Next. |
| Governance | Certified approval and authorization ownership | No approval logic exists or should be added to the composer. |
| Worker Platform | Certified execution ownership | No Worker execution exists or should be added to the composer. |
| Platform Digital Twin | Canonical architectural evidence source | No PDT authority moves into the composer. |
| Architectural Health | Deterministic advisory-only capability | Composer may display findings but must not repair or compensate. |

Audit determination:

```text
message composition is objectively missing
```

Existing certified capabilities are sufficient after submission. The required extension is a bounded ACLI Next input buffer before the existing conversational turn path.

## 4. Reuse Assessment

The message composer shall reuse:

- the persistent conversational session lifecycle;
- deterministic session id handling;
- explicit exit handling;
- the existing single-turn conversational adapter;
- existing execution-plan runtime delegation;
- existing dashboard runtime delegation;
- existing Replay-visible artifact conventions;
- existing Governance and hybrid status presentation;
- existing Architectural Health presentation.

The composer shall not replace:

- session runtime;
- turn runtime;
- Platform Core workflow state;
- Governance authorization;
- Replay evidence ownership;
- Worker Platform execution;
- Architectural Health advisory analysis.

Reuse decision:

```text
compose before delegation; reuse everything after submission
```

## 5. Proposed UX Flow

Canonical interactive flow:

```text
aigol next

AiGOL compose>
We are beginning Generation 12.

Objective:

G12_01_ACLI_NEXT_MESSAGE_COMPOSER_SPECIFICATION_V1

Follow the Governed Development Workflow.
/send

AiGOL>
submitted as TURN-000001
```

The operator writes multiple lines into a local ACLI Next composition buffer. The buffer is not submitted to Platform Core until the operator explicitly submits it.

After submission:

1. ACLI Next joins the buffered lines into one complete message.
2. ACLI Next delegates the complete message to the existing conversational turn path.
3. Platform Core receives exactly one complete conversational request.
4. Existing execution-plan, dashboard, Replay, Governance, and Architectural Health presentation flows run once.
5. The persistent session remains active for the next composed message.

## 6. Submission Model

The canonical deterministic submission command should be:

```text
/send
```

Rationale:

- it is explicit;
- it is visible in tests;
- it is deterministic across terminals;
- it avoids ambiguous blank-line behavior;
- it does not depend on terminal-specific key handling.

Optional future aliases may be specified only if deterministic and tested:

- Ctrl+D as end-of-message when the buffer is non-empty;
- `/submit` as an alias for `/send`.

Blank lines inside the buffer are valid message content and shall not submit the message.

## 7. Composer Commands

The composer should support the following commands before submission:

| Command | Behavior | Governance Effect |
| --- | --- | --- |
| `/send` | Submit the current non-empty buffer as one conversational turn. | None inside ACLI Next; existing turn path delegates normally. |
| `/clear` | Clear the current buffer and continue composing. | None. |
| `/cancel` | Cancel the current buffer and return to empty composition state. | None. |
| `/preview` | Render the current buffer for human inspection without submission. | None; preview is presentation only. |
| `/exit` or `/quit` | Exit the persistent session only when buffer is empty, or require confirmation if buffer is non-empty. | None. |
| `/help` | Show composer commands. | None. |

If the buffer is empty and the human enters a certified persistent-session exit command, the session may terminate as in G11-03.

If the buffer is non-empty and the human enters an exit command, ACLI Next should fail safe by requiring the human to choose `/send`, `/clear`, `/cancel`, or a confirmed exit command.

## 8. Editing Before Submission

Minimum editing support:

- append entered lines to the current buffer;
- preserve blank lines;
- support `/clear`;
- support `/cancel`;
- support `/preview`.

Line-level editing may rely on the terminal's native input editing for the current line. Full multi-line cursor editing is not required for the first implementation.

This preserves minimal extension:

```text
buffered composition, not a text editor subsystem
```

## 9. Replay Behavior

Canonical Replay behavior:

```text
one logical user message
-> one conversational turn
-> one execution plan
-> one dashboard update
-> one Replay session/run record
```

The message composer shall not create a governed conversational turn for each line.

Composer presentation metadata may be recorded only as ACLI Next UX evidence, and only if it is clearly non-authoritative. Such metadata must not be treated as:

- Governance approval;
- Governance authorization;
- Worker execution evidence;
- Platform Core workflow progression;
- Architecture Review;
- certification.

The submitted message hash should be derived from the complete composed message, not from individual lines.

## 10. Platform Core Behavior

Platform Core shall continue receiving exactly one complete conversational request per submitted message.

Platform Core remains responsible for:

- workflow orchestration;
- capability discovery;
- workflow progression;
- operational state;
- execution coordination.

The composer shall not:

- inspect or modify Platform Core workflow state;
- decide workflow stage transitions;
- invoke execution plans directly except through the existing conversational session path;
- create a second orchestration path.

## 11. ACLI Next Behavior

ACLI Next remains:

- conversational UX;
- presentation layer;
- operator interaction layer;
- show-guide-delegate layer.

The message composer may own only:

- local text buffering;
- local composer command handling;
- local preview rendering;
- local cancellation and clearing;
- passing the complete submitted message into the existing conversational turn path.

ACLI Next shall not become:

- orchestration authority;
- Governance authority;
- Replay authority;
- Worker execution authority;
- Platform Digital Twin authority;
- Architectural Health authority.

## 12. Governance, Worker, PDT and Architectural Health Boundaries

Governance remains unchanged:

- no approval logic moves into ACLI Next;
- no authorization logic moves into ACLI Next;
- composer commands do not imply approval.

Worker Platform remains unchanged:

- no Worker execution logic moves into the composer;
- no shell execution is introduced by the composer;
- no Git, dependency, deployment, or environment operation is performed by the composer.

Platform Digital Twin remains unchanged:

- composer state is not architectural evidence authority;
- PDT remains the canonical architectural evidence source.

Architectural Health remains unchanged:

- advisory findings may be displayed after existing dashboard refresh;
- the composer does not repair, suppress, or compensate for findings.

## 13. Hybrid Behavior

If the submitted complete message exceeds certified Platform Core capability, existing hybrid guidance should be reused.

The composer shall:

- keep the persistent session active;
- preserve the composed message as one submitted turn;
- display existing hybrid-required guidance from the dashboard;
- identify the expected return point;
- avoid performing the external operation.

Hybrid behavior remains operational guidance only.

## 14. Responsibility Assessment

| Responsibility | Owner | Composer Effect |
| --- | --- | --- |
| Human message composition | ACLI Next UX | New bounded buffer only. |
| Workflow orchestration | Platform Core | Unchanged. |
| Capability discovery | Platform Core / certified workflow | Unchanged. |
| Approval and authorization | Governance | Unchanged. |
| Evidence and reconstruction | Replay | Unchanged. |
| Execution | Worker Platform | Unchanged. |
| Architectural evidence projection | Platform Digital Twin | Unchanged. |
| Advisory health findings | Architectural Health | Unchanged. |

Responsibility finding:

```text
no ownership migration is required
```

The extension is safe to specify because it only delays submission until the human has finished composing the message.

## 15. Implementation Readiness

Implementation is ready for a minimal UX extension.

Recommended first implementation scope:

1. Add a composer loop inside the persistent ACLI Next REPL.
2. Buffer lines until `/send`.
3. Submit the joined buffer through the existing `run_acli_next_conversational_session(...)` path.
4. Preserve existing explicit exit handling.
5. Add `/clear`, `/cancel`, `/preview`, and `/help`.
6. Add targeted tests proving multi-line input creates one turn and one run.
7. Preserve all non-authority flags already present in G11-03 artifacts.

Out of scope for first implementation:

- full-screen editor;
- hidden workflow commands;
- direct Worker invocation;
- Governance approvals from composer commands;
- Replay reconstruction redesign;
- Platform Core changes;
- Architectural Health repair behavior.

## 16. Certification Recommendation

The ACLI Next message composer should proceed to implementation as a minimal UX extension over certified capabilities.

Certification target:

```text
ACLI_NEXT_MESSAGE_COMPOSER_IMPLEMENTED
```

Architecture review after implementation must verify:

- one submitted message creates one governed conversational turn;
- line buffering does not duplicate Platform Core orchestration;
- composer commands remain presentation-only;
- Replay continuity is preserved;
- Governance continuity is preserved;
- Worker Platform execution remains unchanged;
- Architectural Health remains advisory only.

## 17. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: ACLI_NEXT_MESSAGE_COMPOSER_SPECIFIED
