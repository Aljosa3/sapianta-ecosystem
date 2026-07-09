# G17-HI-02A - Platform Core Conversation Ownership Reuse Audit

Status: AUDIT COMPLETE

Date: 2026-07-09

Final verdict: PARTIAL_REUSE_AVAILABLE

## Executive Summary

Platform Core already contains substantial reusable primitives for owning conversation semantics, runtime entry, Human Intent Resolution, clarification generation, clarification continuity, approval boundaries, session replay state, runtime progress, turn completion, and replay-backed conversation evidence.

However, those primitives are not yet assembled into a single shared Platform Core conversation lifecycle owner that every Human Interface can call. The current `./aicli` implementation still owns live session-loop mechanics, local pending-state variables, command interpretation, approval/clarification wait handling, and several session-status decisions.

The audit therefore certifies partial reuse availability, not reuse sufficiency. The next architecture-safe direction is to reuse and consolidate existing Platform Core primitives behind a shared conversation lifecycle/projection service rather than moving more workflow state into `./aicli`.

## Scope And Invariant

This audit reviewed existing repository evidence for:

- Runtime Entry
- Runtime Continuation
- Human Intent Resolution
- Clarification
- Approval lifecycle
- Session lifecycle
- Conversation state
- Platform UX projection
- AiCLI session handling
- Replay evidence for conversation steps

Critical invariant preserved by this audit:

Platform Core owns the conversation. Human Interfaces only transport, render, and collect interaction. Human Interfaces must not own workflow decisions, clarification semantics, approval semantics, runtime continuation, governance, replay, or certification.

## Reuse Findings

### Runtime Entry

Classification: already implemented in Platform Core.

Evidence:

- `aigol/runtime/human_interface_runtime_entry_service.py` defines the canonical Human Interface Runtime Entry Service.
- `run_human_interface_runtime_entry()` restores Platform Core project context, resolves development intent, builds runtime prompts, delegates governed runtime execution, and records workspace state.
- The result explicitly records `human_interface_runtime_entry_orchestrates: False`, `platform_core_project_services_delegated: True`, and `platform_core_runtime_delegated: True`.

Reuse conclusion:

Runtime Entry is reusable and Platform Core-owned.

### Runtime Continuation

Classification: partially implemented in Platform Core.

Evidence:

- `aigol/runtime/post_entry_continuation_gate_runtime.py` records replay-visible continuation gate decisions such as `CONTINUATION_ALLOWED`, `CLARIFICATION_REQUIRED`, `PROPOSAL_BOUNDARY_REACHED`, and `COGNITION_BOUNDARY_REACHED`.
- `aigol/runtime/context_assembled_to_ppp_routing_continuation.py` and related continuation modules provide deterministic continuation behavior for specific runtime paths.
- `aigol/runtime/human_interface_runtime_entry_service.py` enters the governed runtime using `auto_continue=True`, but it does not expose a reusable human conversation lifecycle loop.

Reuse conclusion:

Continuation primitives exist, but a shared UHI conversation continuation owner is not complete.

### Human Intent Resolution

Classification: already implemented in Platform Core.

Evidence:

- `aigol/runtime/platform_core_project_services.py` exposes `prepare_unified_human_interface_project_context()`.
- The returned artifact records `development_intent_resolution_authority: PLATFORM_CORE`, `human_conversation_experience_authority: PLATFORM_CORE`, and `interface_authority: False`.
- `aigol/runtime/human_intent_clarification_intake_runtime.py` classifies human intent and returns deterministic clarification or workflow routing results without provider, worker, or governance mutation.

Reuse conclusion:

Human Intent Resolution is Platform Core-owned and already reusable.

### Clarification

Classification: already implemented in Platform Core, with live input handling still implemented in `./aicli`.

Evidence:

- `platform_core_project_services.py` creates Platform Core human conversation experience and exposes `clarification_required`, `clarification_questions`, and replay-backed clarification continuity.
- `replay_backed_uhi_clarification_state()` recovers active clarification state from Platform Core workspace replay and marks `platform_core_authority: True`, `human_interface_authority: False`.
- `resolve_uhi_clarification_continuity()` binds replies to active clarification, verifies satisfaction, records continuity replay, and annotates `platform_core_resolves_clarification: True`.
- `aigol/runtime/clarification_lifecycle_resolution_runtime.py` reconstructs active/open/resolved/superseded clarification lifecycle from replay.
- `aigol/runtime/clarification_continuity_runtime.py` and `aigol/runtime/human_intent_clarification_continuity_runtime.py` provide replay-visible clarification response binding and workflow selection after clarification.

Adapter-local evidence:

- `aigol/cli/aicli.py` keeps `pending_clarification` in local variables and reads clarification replies through `_read_clarification_reply()`.

Reuse conclusion:

Clarification semantics and replay continuity are Platform Core-owned. Human-facing input collection is adapter-local, as allowed, but the live conversation lifecycle around active clarification is still not fully centralized.

### Approval Lifecycle

Classification: duplicated across layers.

Platform Core evidence:

- `aigol/runtime/approval/approval_engine.py` evaluates approval contracts and returns `PENDING_HUMAN_APPROVAL`, `APPROVED`, or `BLOCKED`.
- `aigol/runtime/approval/approval_request.py` creates immutable approval requests with replay hashes.

AiCLI evidence:

- `aigol/cli/aicli.py` stores `pending_summary`, waits for `/approve`, increments `approval_count`, extracts `canonical_runtime_prompt`, and then invokes runtime entry.
- `run_reference_uhi_submit_session()` implements approval prompting, `/approve`, `/cancel`, and EOF handling locally.

Reuse conclusion:

Platform Core owns approval boundary artifacts, but `./aicli` currently owns the human approval collection loop and maps local `/approve` into runtime entry. This is acceptable as transport/presentation only if the approval decision itself remains Platform Core-governed, but the lifecycle is not yet projected by a shared Platform UX service.

### Session Lifecycle

Classification: duplicated across layers.

Platform Core evidence:

- `aigol/runtime/conversation_session_resume_runtime.py` allocates append-only turn IDs and preserves replay-safe session resume semantics.
- `platform_core_project_services.py` records persistent workspace state through `record_unified_human_interface_workspace_state()`.
- `latest_platform_core_workspace_state()` restores replay-backed workspace/session state.

AiCLI evidence:

- `aigol/cli/aicli.py` owns `session_status`, `exit_reason`, `submitted_request_count`, `clarification_count`, `approval_count`, `pending_approval`, and local `transcript`.
- Interactive mode terminates on `/exit`, EOF, and KeyboardInterrupt.
- Submit mode sets statuses such as `REFERENCE_UHI_SUBMIT_AWAITING_HUMAN_INPUT`, `REFERENCE_UHI_SUBMIT_CONVERSATION_ACTIVE`, `REFERENCE_UHI_SUBMIT_CONVERSATION_COMPLETED`, and `REFERENCE_UHI_SUBMIT_CONVERSATION_CANCELED`.

Reuse conclusion:

Platform Core persists and reconstructs workspace/session evidence, but `./aicli` still owns live session lifecycle status interpretation. This is the main reuse gap.

### Conversation State

Classification: partially implemented in Platform Core and implemented only in `./aicli` for live adapter state.

Platform Core evidence:

- `record_unified_human_interface_workspace_state()` records pending clarification and pending summary into Platform Core workspace replay.
- `replay_backed_uhi_clarification_state()` reconstructs active clarification from prior workspace state.
- `clarification_lifecycle_resolution_runtime.py` reconstructs active clarification lifecycle from replay.

AiCLI evidence:

- `pending_summary`, `pending_clarification`, `runtime_result`, `runtime_status`, `last_resolution`, `last_project_context`, `compose_buffer`, `pending_input_lines`, and `transcript` are live local variables in `run_reference_uhi_session()` and `run_reference_uhi_submit_session()`.

Reuse conclusion:

Replay-backed state exists in Platform Core, but live state ownership is still adapter-local.

### Platform UX Projection

Classification: missing.

Evidence:

- `platform_core_project_services.py` returns `human_conversation_experience`, `user_headline`, `recommended_next_user_action`, clarification questions, fail-closed response, and approval summary data.
- `aigol/cli/aicli.py` renders these through local functions such as `_render_project_context()`, `_render_summary()`, `_render_clarification()`, `_render_non_development_response()`, `_render_runtime_result()`, and `_render_session_result()`.
- No shared Platform UX projection contract was found that normalizes conversation states, next actions, input mode, command affordances, and terminal/web/mobile presentation-independent response envelopes.

Reuse conclusion:

The data needed for UX projection is partly available in Platform Core, but the reusable projection layer is missing.

### AiCLI Session Handling

Classification: implemented only in `./aicli`.

Evidence:

- `run_reference_uhi_session()` owns the interactive loop, command recognition, compose buffer lifecycle, prompt rendering, local counts, local transcript, and local session termination.
- `run_reference_uhi_submit_session()` owns stdin submission, clarification reply collection, approval input, local session states, and cancellation behavior.
- `aicli` result fields assert that it does not authorize, execute, own replay, own workspace, own goal mapping, or own provider selection, but it still owns local session handling mechanics.

Reuse conclusion:

This is expected for transport and rendering, but current implementation goes beyond pure transport by interpreting conversation lifecycle states locally.

### Replay Evidence For Conversation Steps

Classification: already implemented in Platform Core.

Evidence:

- `aigol/runtime/conversational_progress_binding_runtime.py` binds conversation turns to runtime progress visibility replay.
- `aigol/runtime/conversational_turn_completion_runtime.py` records `TURN_COMPLETED` and `RESULT_DELIVERED` evidence.
- `aigol/runtime/conversational_cli_runtime.py` records conversational routing decisions, workflow selection, and routing return artifacts.
- `platform_core_project_services.py` writes UHI project context and workspace state artifacts with replay references and artifact hashes.

Reuse conclusion:

Replay evidence is strong and reusable. The gap is not replay; it is live lifecycle ownership/projection.

## Ownership Classification Matrix

| Capability | Classification | Evidence Summary |
| --- | --- | --- |
| Runtime Entry | already implemented in Platform Core | Canonical Human Interface Runtime Entry Service delegates project services and runtime execution. |
| Runtime Continuation | partially implemented in Platform Core | Continuation gates exist, but no shared UHI conversation lifecycle owner is exposed. |
| Human Intent Resolution | already implemented in Platform Core | Project services and HIR runtimes own intent resolution authority. |
| Clarification generation | already implemented in Platform Core | HIR and project services generate deterministic clarification questions. |
| Clarification reply binding | already implemented in Platform Core | Replay-backed UHI clarification continuity binds replies and verifies satisfaction. |
| Clarification live input | implemented only in `./aicli` | `_read_clarification_reply()` collects lines and local commands. |
| Approval boundary | already implemented in Platform Core | Approval engine and request/result artifacts exist. |
| Approval collection loop | implemented only in `./aicli` | `/approve`, approval prompt, and cancellation handling are local. |
| Session replay state | already implemented in Platform Core | Workspace state and conversation session resume primitives exist. |
| Live session lifecycle | implemented only in `./aicli` | `session_status`, `exit_reason`, pending state, counts, and transcript are local. |
| Conversation progress evidence | already implemented in Platform Core | Conversational progress binding and runtime progress snapshots exist. |
| Turn completion evidence | already implemented in Platform Core | Turn completion/result-delivered artifacts exist. |
| Platform UX projection | missing | No shared presentation-independent projection contract found. |
| AiCLI rendering | implemented only in `./aicli` | Local render helpers convert Platform Core artifacts into terminal text. |

## Duplication And Layering Analysis

The repository already avoids the worst ownership violation: `./aicli` does not perform semantic intent resolution, governance authorization, provider selection, worker execution, or replay certification.

The remaining duplication is lifecycle duplication:

- Platform Core records pending clarification and pending approval into replay.
- `./aicli` also keeps live `pending_clarification` and `pending_summary` values.
- Platform Core can reconstruct clarification lifecycle from replay.
- `./aicli` still decides when to prompt for clarification, when to wait for approval, when to terminate, and which local status string to emit.

This does not prove that `./aicli` owns conversation semantics, but it does prove that Platform Core conversation ownership is not yet fully reusable at the Human Interface boundary.

## Critical Invariant Review

No audited evidence shows `./aicli` owning:

- governance execution
- provider selection
- worker execution
- replay authority
- certification
- Human Intent Resolution semantics
- clarification satisfaction semantics

But audited evidence does show `./aicli` owning:

- live session loop
- local compose lifecycle
- command affordance interpretation
- local pending approval/clarification state variables
- local session status and exit reason
- terminal rendering and text projection

The invariant is therefore partially preserved: semantic ownership remains Platform Core-owned, but conversation lifecycle ownership is not yet fully centralized.

## Architectural Findings

1. Platform Core already owns the hard semantic primitives required for conversation lifecycle governance.

2. Platform Core already records replay evidence for UHI context, workspace state, clarification continuity, conversation routing, progress, and turn completion.

3. `./aicli` is correctly non-authoritative for governance, replay, provider, worker, and runtime execution.

4. `./aicli` still owns too much live conversation lifecycle mechanics to satisfy the strict target invariant that Platform Core owns the conversation.

5. The smallest missing reusable capability is not a new cognition or governance subsystem. It is a shared Platform Core conversation lifecycle/projection service that converts existing Platform Core state into explicit next-action envelopes for all Human Interfaces.

6. A Platform UX projection contract remains missing. Current render helpers are terminal-specific and local to `./aicli`.

## Reuse Recommendation

Do not implement additional workflow logic inside `./aicli`.

Recommended next architecture direction:

- Reuse `prepare_unified_human_interface_project_context()`.
- Reuse replay-backed UHI clarification continuity.
- Reuse `record_unified_human_interface_workspace_state()`.
- Reuse approval request/result primitives.
- Reuse conversation session resume and turn completion primitives.
- Add, only if later approved, a shared Platform Core conversation lifecycle/projection boundary that returns:
  - current conversation state
  - required input mode
  - admissible human actions
  - pending clarification or approval evidence
  - replay reference
  - terminal/web/mobile-neutral rendering payload

This would let `./aicli`, Web, Mobile, REST, Voice, Desktop, MCP, and future Human Interfaces remain thin adapters.

## Final Verdict

PARTIAL_REUSE_AVAILABLE

Platform Core already contains most deterministic primitives needed to own the conversation lifecycle, especially semantic resolution, clarification, continuation evidence, approval artifacts, session replay state, and replay evidence.

Reuse is not yet sufficient because the live Human Interface conversation lifecycle is still assembled inside `./aicli`. The missing element is a shared Platform Core conversation lifecycle/projection boundary, not a new governance engine, not a new replay service, and not a new runtime orchestration subsystem.
