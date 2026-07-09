# G17-HI-01 - Human Interface Runtime Hardening Boundary Audit

Status: CERTIFIED WITH OBSERVATIONS

Date: 2026-07-09

Milestone: G17-HI-01

Scope: Audit-only architectural boundary review for Human Interface runtime hardening after recent end-to-end `./aicli` validation. This milestone does not implement code, redesign Platform Core, redesign PCCL, move runtime behavior into Human Interfaces, introduce governance layers, or create interface-specific business logic.

## Executive Summary

Recent `./aicli` validation surfaced real user-workflow friction in compose mode, multiline paste behavior, session-state visibility, approval presentation, and completion feedback.

The issues are valid, but they must be corrected without moving Platform Core authority into `./aicli`.

Certified boundary conclusion:

```text
HUMAN_INTERFACES_REMAIN_THIN_ADAPTERS
```

Preferred remediation posture:

- semantic content, clarification wording, approval summary content, next-step guidance, workflow status semantics, governance status, replay status, and certification status belong in Platform Core or reusable Platform Core artifacts;
- reusable user-facing projection of those artifacts should belong in a Shared Platform UX layer when multiple Human Interfaces need the same presentation contract;
- terminal input capture, local compose buffers, command delimiters, stdin handling, and terminal prompt rendering belong to the Human Interface runtime;
- prompt text, spacing, echo suppression, and command hints unique to `./aicli` belong to `./aicli` presentation.

Final verdict:

```text
CERTIFIED WITH OBSERVATIONS
```

The observation is that user workflow can be improved, but implementation must be layered. Most hardening should reuse Platform Core and shared UX projection rather than adding logic to `./aicli`.

## Current Human Interface Observations

Observed or previously certified Human Interface facts:

- `./aicli` is a reference Unified Human Interface that captures terminal input, renders Platform Core decisions, collects approval, and delegates execution to the canonical runtime entry.
- `run_human_interface_runtime_entry(...)` is the shared Platform Core runtime entry used by current Human Interfaces.
- `prepare_unified_human_interface_project_context(...)` owns Human Intent Resolution, knowledge reuse, clarification continuity, project guidance, and the Platform Core Human Conversation Experience.
- `record_unified_human_interface_workspace_state(...)` owns replay-visible workspace/session state recording.
- `./aicli submit` exists because large pasted prompts are terminal transport concerns and should be captured as one stdin request before Platform Core submission.
- Clarification compose prompt rendering was already hardened so line-by-line paste does not repeatedly print the clarification prompt.
- Approval summary and fail-closed explanation rendering have prior ownership observations: interfaces still assemble some wording locally instead of always rendering Platform Core conversation artifact fields.

Current usability issues requiring boundary classification:

- compose mode presentation can be noisy for multiline input;
- multiline paste behavior is terminal-dependent;
- submit mode Ctrl+D is useful but can be opaque to users;
- session-state visibility can expose internal authority/runtime terms or fail to summarize what the human should do next;
- approval mode can be unclear about the exact approval boundary;
- `/send`, `/approve`, and `/cancel` command hints need consistent presentation;
- prompt rendering should be calm and non-repetitive;
- workflow completion feedback should explain completion, fail-closed state, replay reference, and next action without moving runtime interpretation into the interface.

## Architectural Boundary Review

Constitutional invariant:

```text
Human Interfaces collect, render, transport, and present.
Platform Core decides, governs, executes, records, replays, and certifies.
```

Allowed Human Interface responsibilities:

- input collection;
- local compose buffering;
- command delimiter capture;
- terminal prompt rendering;
- transport normalization;
- interface-specific presentation;
- forwarding complete human input to Platform Core;
- collecting explicit human approval and delegating it to Platform Core runtime entry.

Forbidden Human Interface responsibilities:

- semantic interpretation;
- Human Intent Resolution;
- clarification logic;
- knowledge reuse;
- governance;
- replay;
- certification;
- runtime orchestration;
- workflow decisions;
- provider selection;
- capability discovery;
- PCCL session, envelope, lifecycle, or decision authority.

Architecture rule for hardening:

```text
If the improvement changes meaning, ownership, admissibility, state, governance, replay, certification, or workflow progression, it belongs outside ./aicli.
```

## Ownership Classification Matrix

Classifications:

- A. Platform Core responsibility
- B. Shared Platform UX responsibility
- C. Human Interface responsibility
- D. `./aicli`-specific presentation responsibility

| Finding | Classification | Responsibility owner | Justification |
| --- | --- | --- | --- |
| Clarification question content | A. Platform Core responsibility | Platform Core Project Services / HIR | Questions are semantic artifacts derived from Human Intent Resolution and must be reusable across all interfaces. |
| Knowledge reuse summary and recommended governed action | A. Platform Core responsibility | Platform Core Project Services | Reuse classification and governed action recommendations are Platform Core decisions, not presentation choices. |
| Approval summary content and approval explanation | A. Platform Core responsibility | Platform Core Human Conversation Experience / Governance boundary | Approval wording defines what the human is approving. Interfaces may render it, but must not assemble approval semantics. |
| Fail-closed reason and next-step semantics | A. Platform Core responsibility | Platform Core Runtime / Project Services / Governance | Fail-closed explanation is a deterministic runtime or project-services outcome. Interfaces must not invent reasons. |
| Runtime status meaning, workflow completion, replay certification status | A. Platform Core responsibility | Platform Core Runtime / Replay / Certification | Completion and certification are behavioral facts owned by runtime and replay services. |
| Session semantic state: pending clarification, pending approval, runtime entered, replay reference | A. Platform Core responsibility | Platform Core workspace state and runtime entry | State is replay-visible Platform Core evidence. Interfaces render it only. |
| PCCL sidecar state and proposal lifecycle evidence | A. Platform Core responsibility | PCCL as Platform Core reference layer | PCCL remains deterministic reference evidence and must not be recreated in interfaces. |
| Cross-interface status projection such as "waiting for clarification", "waiting for approval", "completed", "failed closed" | B. Shared Platform UX responsibility | Shared Platform UX over Platform Core artifacts | Multiple interfaces need a human-readable projection of Platform Core status without duplicating interpretation in each adapter. |
| Cross-interface command/action vocabulary such as submit, cancel, approve, continue | B. Shared Platform UX responsibility | Shared Platform UX | Interfaces may map actions to local controls, but the reusable action model should be shared. |
| Friendly rendering templates for Platform Core conversation artifacts | B. Shared Platform UX responsibility | Shared Platform UX | The wording should be reusable by CLI, Web, REST, Voice, Desktop, and future interfaces while preserving Platform Core semantics. |
| Default workflow completion summary view | B. Shared Platform UX responsibility | Shared Platform UX | Completion feedback should consistently render runtime, replay, and next action fields across interfaces. |
| Terminal line collection, local compose buffer, `/send` delimiter capture | C. Human Interface responsibility | Human Interface runtime | This is input capture and local interaction state, not semantic interpretation. |
| Stdin submit mode and Ctrl+D capture | C. Human Interface responsibility | Human Interface runtime | Reading until EOF is transport capture. Platform Core should not know whether input was typed, pasted, piped, or read until EOF. |
| Paste normalization and preservation of internal line breaks | C. Human Interface responsibility | Human Interface runtime | Transport normalization preserves human input before submission and does not decide meaning. |
| Local cancellation of compose buffer before Platform Core submission | C. Human Interface responsibility | Human Interface runtime | Cancelling unsubmitted local text is interface state. Cancelling pending Platform Core state must render Platform Core state and record workspace evidence. |
| Prompt rendering cadence during compose and clarification | D. `./aicli`-specific presentation responsibility | `./aicli` terminal presentation | Terminal prompt noise is specific to line-oriented CLI presentation. |
| Exact strings such as `aicli>`, `aicli compose>`, `aicli approval>` | D. `./aicli`-specific presentation responsibility | `./aicli` terminal presentation | These are terminal labels, not shared workflow semantics. |
| Help text wording for `/send`, `.`, `/approve`, `/cancel`, `/exit` | D. `./aicli`-specific presentation responsibility | `./aicli` terminal presentation | Command names are terminal-specific; their semantic effect must remain delegated. |
| Spacing, grouping, and ordering of terminal output | D. `./aicli`-specific presentation responsibility | `./aicli` terminal presentation | This is display polish as long as it only renders existing artifacts. |

## Platform Core Reuse Analysis

Existing Platform Core functionality should be reused for:

- Human Intent Resolution;
- clarification generation and satisfaction evidence;
- knowledge reuse;
- project guidance;
- conversation response mode;
- approval summary content;
- fail-closed explanation;
- runtime entry status;
- runtime completion status;
- replay reference and certification status;
- workspace-state continuity;
- PCCL sidecar evidence.

Required boundary discipline:

- `./aicli` should continue calling `prepare_unified_human_interface_project_context(...)` for project context and conversation artifacts.
- `./aicli` should continue calling `run_human_interface_runtime_entry(...)` after explicit approval.
- `./aicli` should continue calling `record_unified_human_interface_workspace_state(...)` for session closure and pending-state evidence.
- Any improvement to approval summary semantics or fail-closed explanation semantics should be made in Platform Core once, then rendered by all interfaces.

## Shared Platform UX Analysis

Shared Platform UX is the preferred owner for reusable presentation projection that sits between Platform Core artifacts and concrete interfaces.

Candidate shared UX responsibilities:

- convert Platform Core conversation artifacts into a stable user-facing view model;
- convert runtime completion and fail-closed results into a stable user-facing view model;
- expose an interface-neutral action set, such as `SUBMIT_REQUEST`, `ANSWER_CLARIFICATION`, `APPROVE`, `CANCEL`, `EXIT`;
- hide internal authority flags by default while preserving replay references for inspectable evidence views;
- provide consistent labels for pending clarification, pending approval, runtime complete, failed closed, and awaiting human input.

Shared UX must not:

- decide whether clarification is required;
- decide whether approval is admissible;
- select runtime;
- classify capability;
- evaluate governance;
- certify replay;
- alter PCCL lifecycle state.

This layer should be projection-only:

```text
Platform Core artifact -> reusable human-facing view model
```

## Interface-Specific Analysis

Human Interface runtime responsibilities remain valid for:

- interactive compose session lifetime;
- submit-mode stdin capture;
- line splitting when terminal input returns multiple lines at once;
- preserving multiline request text;
- recognizing local command delimiters;
- detecting EOF and reporting `AWAITING_HUMAN_INPUT` when Platform Core has pending clarification or approval;
- forwarding the complete composed message to Platform Core exactly once;
- collecting `/approve` and delegating to runtime entry.

Human Interface runtime must not inspect message content to infer:

- whether the request is development work;
- whether a clarification answer is sufficient;
- whether a summary is safe to approve;
- which provider, worker, or runtime should be used;
- whether replay certification is complete.

## `./aicli` Presentation Analysis

`./aicli` may own terminal presentation improvements such as:

- reducing repeated prompts during paste;
- clarifying that `/send` and `.` submit the current buffer;
- clarifying that Ctrl+D ends stdin capture in submit mode;
- showing a compact local banner for compose, clarification, approval, and completed states;
- grouping Platform Core output in a more readable order;
- suppressing repeated terminal prompts after the first physical line of a multiline paste;
- showing command help without adding semantic rules.

`./aicli` must not own:

- what clarification questions say;
- what the approval summary means;
- why a request failed closed;
- whether runtime should continue;
- whether replay certification succeeded;
- what PCCL lifecycle transition is admissible.

Presentation hardening should consume Platform Core and shared UX artifacts rather than reconstructing them.

## Remaining User Workflow Gaps

| Gap | Classification | Correct remediation path |
| --- | --- | --- |
| Compose mode prompt noise for large pasted prompts | D. `./aicli`-specific presentation responsibility | Improve terminal prompt cadence or steer users to submit mode; do not change Platform Core. |
| Multiline input transport variability | C. Human Interface responsibility | Preserve submit mode and deterministic chunk splitting; do not add semantic parsing. |
| Ctrl+D behavior is not obvious | D. `./aicli`-specific presentation responsibility | Improve terminal help text and banners. |
| Session-state visibility exposes internal terms or is hard to scan | B. Shared Platform UX responsibility | Add reusable view model over Platform Core status artifacts. |
| Approval presentation partly assembled in adapters | A. Platform Core responsibility | Move or keep approval semantics in Platform Core conversation artifact and render it directly. |
| Fail-closed presentation partly adapter-authored | A. Platform Core responsibility | Render Platform Core fail-closed explanation and reason fields consistently. |
| Workflow completion feedback is too internal or incomplete | B. Shared Platform UX responsibility | Create shared projection of runtime, replay, certification, and next action. |
| `./aicli` command hints are terse | D. `./aicli`-specific presentation responsibility | Improve local terminal help and labels only. |
| Pending clarification and pending approval continuity across sessions | A. Platform Core responsibility | Reuse workspace state and project context continuity; interfaces render pending state. |
| Cross-interface consistency for Web, Mobile, REST, Voice, Desktop, MCP | B. Shared Platform UX responsibility | Define shared interface-neutral view models and action names. |

## Critical Validation

No proposed improvement may migrate business logic, governance, runtime, cognition, replay, or certification into `./aicli`.

Validation results:

- Business logic migration: not permitted. All semantic and workflow meaning remains Platform Core-owned.
- Governance migration: not permitted. Approval semantics and authorization remain Platform Core / Human Authority.
- Runtime migration: not permitted. Runtime entry and continuation remain existing Platform Core services.
- Cognition migration: not permitted. PCCL remains Platform Core reference evidence; Human Interfaces do not own cognition or proposal lifecycle.
- Replay migration: not permitted. Replay evidence remains Platform Core-owned and replay-visible.
- Certification migration: not permitted. Certification Registry and replay certification remain Platform Core-owned.

Boundary verdict:

```text
NO_PLATFORM_CORE_RESPONSIBILITY_MAY_MOVE_INTO_AICLI
```

## Architectural Findings

1. The observed usability issues are mostly presentation, transport, and reusable view-model issues, not runtime architecture defects.

2. `./aicli` may be hardened only where behavior is terminal-specific presentation or input capture.

3. Approval summary content and fail-closed explanation content should remain Platform Core-owned because they define semantic and governance-adjacent meaning.

4. Reusable workflow status presentation should be shared across Human Interfaces rather than copied into `./aicli`.

5. Submit mode remains architecturally correct for large pasted prompts because stdin capture is a Human Interface transport concern.

6. Compose mode remains useful for short interactive sessions, but terminal prompt rendering should not become a semantic state machine.

7. The safest improvement path is Platform Core artifact reuse plus shared UX projection plus minimal `./aicli` terminal polish.

8. No evidence supports moving Human Intent Resolution, clarification logic, knowledge reuse, governance, runtime orchestration, replay, certification, provider selection, capability discovery, PCCL, or proposal lifecycle into `./aicli`.

## Final Verdict

G17-HI-01 is certified with observations.

Human Interface hardening is justified, but it must preserve thin-interface architecture. User workflow improvements should maximize Platform Core reuse, introduce shared Platform UX projection where multiple interfaces need the same human-facing status model, and limit `./aicli` changes to terminal-specific input capture and presentation.

Final certification:

```text
CERTIFIED_WITH_OBSERVATIONS_HUMAN_INTERFACE_HARDENING_MUST_REMAIN_PRESENTATION_AND_TRANSPORT_BOUND_WITH_PLATFORM_CORE_REUSE
```
