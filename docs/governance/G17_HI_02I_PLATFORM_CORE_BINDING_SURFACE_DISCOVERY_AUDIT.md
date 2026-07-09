# G17-HI-02I — Platform Core Binding Surface Discovery Audit

Status: audit complete

Date: 2026-07-09

Final verdict: CANONICAL_BINDING_SURFACE_REUSABLE_WITH_MINOR_BINDING

## Executive Summary

The repository already exposes a reusable Platform Core Human Interface binding surface, but it is not yet packaged as a single explicit event/action projection API.

The strongest existing canonical binding surface is:

```text
prepare_unified_human_interface_project_context(...)
```

from:

```text
aigol/runtime/platform_core_project_services.py
```

This surface is already interface-neutral and returns the core data every Human Interface needs to render and continue a conversation:

- restored workspace state;
- project guidance;
- knowledge reuse;
- replay-backed clarification continuity;
- development intent resolution;
- Human Conversation Experience projection;
- approval summary;
- fail-closed response;
- progress messages;
- Platform Core authority flags;
- replay reference.

The companion runtime continuation surface is:

```text
run_human_interface_runtime_entry(...)
```

from:

```text
aigol/runtime/human_interface_runtime_entry_service.py
```

Together these services are sufficient to prevent Human Interfaces from implementing governance, replay, clarification semantics, approval summaries, runtime continuation, provider selection, worker execution, or certification.

The remaining work is minor binding: expose or consume an explicit projection of available user actions and terminal/session-close state from the existing Platform Core artifacts, so every interface can bind to the same fields without re-deriving them locally.

## Existing Platform Core Binding Candidates

### Candidate 1: Unified Human Interface Project Context

Surface:

```text
prepare_unified_human_interface_project_context(...)
```

Purpose:

Prepare a canonical Platform Core project-services context for any Unified Human Interface.

Implementation evidence:

- The function accepts generic `interface_name`, `session_id`, `message`, `runtime_root`, `workspace`, and `created_at` arguments, making it interface-neutral.
- It restores prior workspace state using `latest_platform_core_workspace_state(session_root)`.
- It resolves development intent and produces `human_conversation_experience`.
- It marks project workspace, guidance, knowledge reuse, development intent resolution, and human conversation experience authority as `PLATFORM_CORE`.

Suitability:

Canonical reusable binding surface, with minor binding extension recommended.

Reason:

It already exposes most required state and projection data, but it does not yet expose a single normalized `available_user_actions`, `conversation_state`, and `session_close_allowed` projection.

### Candidate 2: Canonical Human Interface Runtime Entry

Surface:

```text
run_human_interface_runtime_entry(...)
```

Purpose:

Enter the certified runtime from any Human Interface after Platform Core has admitted runtime continuation.

Implementation evidence:

- It prepares Platform Core project contexts for human requests.
- It derives `runtime_prompts` only when `runtime_binding_admissible` is true.
- It returns `CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_NOT_REQUIRED` when no runtime prompt is admissible.
- It invokes the injected governed runtime runner only after admissible runtime prompts exist.
- It records Platform Core workspace state after completion.

Suitability:

Canonical runtime continuation surface.

Reason:

It is not the whole conversation binding surface, but it is the correct reusable post-approval runtime continuation surface.

### Candidate 3: Platform Core Workspace State Recorder

Surface:

```text
record_unified_human_interface_workspace_state(...)
```

Purpose:

Persist replay-visible Platform Core workspace state, including pending clarification and pending approval.

Implementation evidence:

- `build_persistent_workspace_state_artifact(...)` stores `pending_clarification_request`, `pending_implementation_summary`, `pending_approval`, `pending_approval_kind`, implementation history, guidance, knowledge index, and replay metadata.
- It marks `resumable_conversational_context: True`.

Suitability:

Reusable persistence surface, not the primary binding surface.

Reason:

It records authoritative state, but interfaces should not directly construct lifecycle semantics from storage internals.

### Candidate 4: Human Conversation Experience Artifact

Surface:

```text
human_conversation_experience
```

inside the UHI project context.

Purpose:

Project Platform Core-owned user-facing conversation content.

Implementation evidence:

- `human_conversation_experience_from_resolution(...)` emits `response_mode`, `user_headline`, `user_explanation`, `clarification_questions`, `recommended_next_user_action`, `progress_messages`, `approval_summary`, and `fail_closed_response`.
- The artifact includes `conversation_authority: PLATFORM_CORE` and `interface_executes_conversation: False`.
- Approval summary includes `runtime_after_approval: CERTIFIED_PLATFORM_CORE_RUNTIME` and `approval_state: PENDING_HUMAN_APPROVAL` when summary-admissible.

Suitability:

Reusable projection component of the canonical binding surface.

Reason:

It already supplies presentation metadata and next-step guidance, but it is nested inside the project context rather than exposed as a standalone canonical binding object.

## Conversation Runtime Review

Platform Core owns conversation semantics through project services and conversation experience projection.

Existing evidence shows:

- `prepare_unified_human_interface_project_context(...)` returns `development_intent_resolution` and `human_conversation_experience`.
- `human_conversation_experience_from_resolution(...)` decides `APPROVAL_PREPARATION`, `CLARIFICATION`, or `INFORMATIONAL`.
- The G14.40 governance note certifies that approval summary composition and fail-closed explanation composition moved to Platform Core.

The older `aigol/runtime/conversation_runtime.py` is not the canonical Human Interface binding surface. It is a minimal deterministic conversation runtime over Constitutional Memory evidence and does not expose UHI workflow state, approval continuation, pending clarification, or Human Interface action projection.

## Projection Service Review

The projection service exists, but not as a single explicit binding envelope.

Already exposed:

- `response_mode`;
- `user_headline`;
- `user_explanation`;
- `clarification_questions`;
- `recommended_next_user_action`;
- `progress_messages`;
- `approval_summary`;
- `fail_closed_response`;
- `project_guidance`;
- `knowledge_reuse`;
- `development_intent_resolution`;
- replay reference.

Partially exposed:

- conversation state through `response_mode`, `approval_state`, and fail-closed `conversation_state`;
- available actions through `recommended_next_user_action`, pending approval, and pending clarification guidance.

Not yet explicitly exposed as a canonical field:

- normalized `available_user_actions`;
- normalized `conversation_state`;
- normalized `completion_state`;
- normalized `session_close_allowed`;
- normalized `expected_human_input`.

This means the Platform Core data is present, but Human Interfaces still translate it into local commands.

## Platform Service Review

Platform Core project services already expose the best canonical binding candidate.

Evidence:

- `project_guidance_model(...)` exposes `pending_approvals`, `unresolved_clarification`, `recommended_next_governed_action`, and `requires_explicit_human_approval`.
- `guidance_next_action(...)` maps pending clarification to “Answer the pending clarification, then type /send” and pending approval to “Review the pending implementation summary, then type /approve or /cancel.”
- `_conversation_approval_summary(...)` exposes approval authority and runtime continuation.
- `_conversation_fail_closed_response(...)` exposes fail-closed reason and recommended next action.

These fields are enough for a Human Interface to render and collect input without owning semantic logic. The weakness is that CLI-specific command wording appears in guidance strings, so Web/Mobile/Voice/REST should consume normalized action fields rather than parse command text.

## Human Interface Consumption Review

### `./aicli`

Consumes:

- `prepare_unified_human_interface_project_context(...)`;
- Platform Core `approval_summary`;
- Platform Core `fail_closed_response`;
- `run_human_interface_runtime_entry(...)`;
- `record_unified_human_interface_workspace_state(...)`.

Still owns locally:

- input loop;
- command interpretation;
- pending summary variable;
- pending clarification variable;
- session status strings;
- EOF and interrupt handling;
- mapping from `/approve` to Runtime Entry invocation.

Boundary status:

Partially bound. It is thin for execution and governance, but it still locally binds conversation-state transitions.

### AiGOL Next

Consumes:

- Canonical Runtime Entry through `_run_acli_next_runtime_bound_session(...)`.
- Platform Core approval summary and fail-closed response, as verified by G14.40 tests.

Still owns locally:

- presentation shell;
- conversational session wrapper;
- local runtime binding status mapping.

Boundary status:

Partially bound to the same surfaces as `./aicli`.

### Web, Mobile, Voice, REST

Should consume:

- UHI Project Context as the read/projection surface.
- Runtime Entry as the approval continuation surface.
- Workspace state replay references for continuity.

Should not implement:

- conversation state;
- runtime continuation;
- workflow logic;
- approval logic;
- clarification logic;
- replay logic.

Binding requirement:

They need a normalized action/projection adapter over existing Platform Core fields, especially for action names and session-close semantics.

## Reuse Matrix

| Capability | Existing Surface | Classification | Notes |
| --- | --- | --- | --- |
| Runtime Entry | `run_human_interface_runtime_entry(...)` | canonical reusable binding surface | Already shared by `./aicli` and AiGOL Next. |
| Runtime Continuation | `runtime_prompts` and canonical entry status | canonical reusable binding surface | Requires Human Interface approval event binding. |
| Human Intent Resolution | UHI Project Context | canonical reusable binding surface | Platform Core authority is explicit. |
| Conversation Experience Projection | `human_conversation_experience` | reusable with minor extension | Needs normalized action fields. |
| Clarification Requests | `response_mode: CLARIFICATION`, questions, planner | canonical reusable binding surface | Already Platform Core-owned. |
| Clarification Continuity | replay-backed active clarification state | canonical reusable binding surface | Already restored from workspace replay. |
| Approval Requests | `approval_summary` | canonical reusable binding surface | Already Platform Core-authored. |
| Pending Approval | workspace state and project guidance | reusable with minor extension | Existing state is authoritative; action projection should be normalized. |
| Pending Clarification | workspace state and project guidance | reusable with minor extension | Existing state is authoritative; action projection should be normalized. |
| Runtime Summaries | Runtime Entry result | canonical reusable binding surface | Already includes runtime status and replay references. |
| Completion State | local HI result plus runtime result | reusable with minor extension | Needs Platform Core `completion_state` or `session_close_allowed` projection. |
| Available User Actions | `recommended_next_user_action` and guidance text | reusable with minor extension | Needs structured action identifiers. |
| Presentation Metadata | `user_headline`, `user_explanation`, progress, summary/response | canonical reusable binding surface | Already suitable for interfaces. |
| Interface Command Parsing | `./aicli` local loop | duplicated | Should remain transport-only and map to canonical actions. |

## Canonical Binding Surface Recommendation

Use the existing UHI Project Context as the canonical Platform Core binding surface:

```text
prepare_unified_human_interface_project_context(...)
```

Use Canonical Human Interface Runtime Entry as the runtime continuation binding:

```text
run_human_interface_runtime_entry(...)
```

Do not create a separate semantic conversation runtime. Instead, add or standardize a thin projection envelope over the existing UHI Project Context fields:

```text
human_interface_binding_projection
  conversation_state
  runtime_state
  available_user_actions
  expected_human_input
  clarification_request
  approval_request
  completion_state
  session_close_allowed
  presentation
  replay_reference
```

This is a minor binding extension because the underlying data already exists in Platform Core artifacts.

## Remaining Binding Work

1. Normalize action identifiers.

Examples:

- `SUBMIT_REQUEST`;
- `SUBMIT_CLARIFICATION_REPLY`;
- `APPROVE`;
- `CANCEL`;
- `CLOSE`;
- `WAIT_FOR_HUMAN_INPUT`;
- `ENTER_CERTIFIED_RUNTIME`.

2. Normalize conversation and completion state.

Examples:

- `CLARIFICATION_AWAITING_REPLY`;
- `APPROVAL_AWAITING_HUMAN`;
- `RUNTIME_CONTINUATION_READY`;
- `CONVERSATION_COMPLETED`;
- `CONVERSATION_CANCELED`.

3. Expose session-close semantics explicitly.

Human Interfaces should not infer session close from EOF, local process termination, or runtime status alone.

4. Bind `./aicli`, AiGOL Next, Web, Mobile, Voice, and REST to the same projection.

Each interface should render and collect input differently, but consume the same Platform Core state and action model.

## Architectural Findings

1. The repository already contains the correct Platform Core ownership placement.

Human Intent Resolution, conversation projection, clarification, approval summaries, runtime continuation, and replay continuity live in Platform Core services.

2. The existing binding surface is real but distributed.

The UHI Project Context is the best single existing surface, but runtime continuation is performed by Runtime Entry and persistence by workspace state recording.

3. Human Interfaces still do too much local lifecycle binding.

`./aicli` still stores pending summary and pending clarification locally and maps commands to state transitions. That should be treated as current binding code, not canonical conversation ownership.

4. No new Platform Core semantic capability is required.

The extension needed is a deterministic projection envelope over existing Platform Core fields.

## Final Recommendation

Adopt the UHI Project Context as the canonical Human Interface binding surface.

Do not duplicate Platform Core logic in any Human Interface.

Implement only a minor binding projection, if needed, that packages existing Platform Core fields into structured action and state fields. This should be a wrapper over existing services, not a redesign of Runtime, Governance, Replay, PCCL, or Human Interface architecture.

## Final Verdict

CANONICAL_BINDING_SURFACE_REUSABLE_WITH_MINOR_BINDING

`./aicli`, AiGOL Next, Web, Mobile, Voice, and REST can all consume the same existing Platform Core binding surface if the UHI Project Context is treated as canonical and paired with Runtime Entry for approved continuation. The smallest deterministic extension is a normalized Platform Core binding projection over already-existing fields, especially `available_user_actions`, `conversation_state`, `completion_state`, and `session_close_allowed`.
