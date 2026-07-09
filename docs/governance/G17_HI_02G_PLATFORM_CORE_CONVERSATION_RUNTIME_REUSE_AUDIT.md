# G17-HI-02G — Platform Core Conversation Runtime Reuse Audit

Status: audit complete

Date: 2026-07-09

Final verdict: PLATFORM_CORE_REUSE_WITH_MINOR_BINDING

## Executive Summary

Platform Core already implements the substantive conversation runtime primitives required by Human Interfaces:

- shared Runtime Entry;
- project context preparation;
- Human Intent Resolution;
- Human Conversation Experience projection;
- replay-backed clarification continuity;
- pending clarification and pending approval workspace state;
- approval summary artifacts;
- certified runtime continuation after approval;
- replay-visible workspace restoration.

The remaining gap is not a missing semantic runtime. The remaining gap is binding: Human Interfaces, especially `./aicli`, still maintain local pending state, command interpretation, and local session status decisions instead of consuming one canonical Platform Core conversation event/projection boundary.

The canonical boundary is specified in `docs/specifications/G17_HI_02B_PLATFORM_CORE_CONVERSATION_BOUNDARY_SPECIFICATION.md`, but repository search shows its terms such as `conversation_projection`, `session_close_allowed`, `HUMAN_APPROVAL_SUBMITTED`, and `COLLECT_APPROVAL_DECISION` are specification-only, not implemented as a single runtime API.

## Existing Platform Core Conversation Runtime Review

`aigol/runtime/platform_core_project_services.py` provides the central reusable conversation-adjacent Platform Core service.

Evidence:

- `prepare_unified_human_interface_project_context(...)` is explicitly described as preparing canonical Platform Core project-services context for any UHI and accepts `interface_name`, `session_id`, `message`, `runtime_root`, `workspace`, and `created_at` as reusable interface-neutral inputs (`aigol/runtime/platform_core_project_services.py:156`).
- It restores prior workspace state through `latest_platform_core_workspace_state(session_root)` before resolving the next user message (`aigol/runtime/platform_core_project_services.py:167` to `aigol/runtime/platform_core_project_services.py:191`).
- It produces `development_intent_resolution` and `human_conversation_experience` in the same project context artifact (`aigol/runtime/platform_core_project_services.py:207` to `aigol/runtime/platform_core_project_services.py:232`).
- The returned artifact marks project workspace, guidance, knowledge reuse, development intent, and conversation experience authority as `PLATFORM_CORE` and marks `interface_authority: False` (`aigol/runtime/platform_core_project_services.py:233` onward).

This is a reusable Platform Core conversation preparation runtime, not an `aicli`-specific service.

## Runtime Continuation Review

Runtime Entry is already reusable.

Evidence:

- `run_human_interface_runtime_entry(...)` is the shared entrypoint for any Unified Human Interface (`aigol/runtime/human_interface_runtime_entry_service.py:41`).
- It delegates every human request to `prepare_unified_human_interface_project_context(...)` (`aigol/runtime/human_interface_runtime_entry_service.py:63` to `aigol/runtime/human_interface_runtime_entry_service.py:72`).
- It derives `runtime_prompts` only from Platform Core intent resolutions where `runtime_binding_admissible` is true (`aigol/runtime/human_interface_runtime_entry_service.py:79` to `aigol/runtime/human_interface_runtime_entry_service.py:83`).
- If no runtime prompt is admissible, it returns `CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_NOT_REQUIRED` without entering the runtime (`aigol/runtime/human_interface_runtime_entry_service.py:106` to `aigol/runtime/human_interface_runtime_entry_service.py:135`).
- If runtime prompts exist, it invokes the injected governed runtime runner with `auto_continue=True`, derives canonical runtime binding status, and records workspace state (`aigol/runtime/human_interface_runtime_entry_service.py:137` to `aigol/runtime/human_interface_runtime_entry_service.py:218`).

`./aicli` reuses this entry on approval, but it still owns the local decision to call it.

## Conversation Lifecycle Review

Platform Core has lifecycle state fragments, but not a single implemented canonical lifecycle state machine API.

Implemented in Platform Core:

- `human_conversation_experience_from_resolution(...)` builds a canonical response model (`aigol/runtime/platform_core_project_services.py:1726`).
- It returns `response_mode: APPROVAL_PREPARATION` when the intent is summary-admissible and `response_mode: CLARIFICATION` when clarification is required (`aigol/runtime/platform_core_project_services.py:1753` to `aigol/runtime/platform_core_project_services.py:1769`).
- The conversation artifact includes `conversation_authority: PLATFORM_CORE`, `interface_executes_conversation: False`, `recommended_next_user_action`, `progress_messages`, `approval_summary`, and `fail_closed_response` (`aigol/runtime/platform_core_project_services.py:1838` to `aigol/runtime/platform_core_project_services.py:1875`).

Missing as an implemented single runtime boundary:

- No implemented `conversation_projection` API was found outside the specification.
- No implemented `session_close_allowed` field was found outside the specification.
- No implemented canonical event names such as `HUMAN_APPROVAL_SUBMITTED` were found outside the specification.

Therefore, Platform Core owns the semantic lifecycle content, but Human Interfaces still bind that content into local loops.

## Clarification Lifecycle Review

Clarification lifecycle is strongly implemented in Platform Core.

Evidence:

- `latest_platform_core_workspace_state(...)` restores the latest workspace state artifact from the session replay (`aigol/runtime/platform_core_project_services.py:290` to `aigol/runtime/platform_core_project_services.py:302`).
- `replay_backed_uhi_clarification_state(...)` recovers active clarification state from `pending_clarification_request` and marks it `state_source: PLATFORM_CORE_WORKSPACE_REPLAY`, `replay_backed: True`, `platform_core_authority: True`, and `human_interface_authority: False` (`aigol/runtime/platform_core_project_services.py:305` to `aigol/runtime/platform_core_project_services.py:329`).
- `resolve_uhi_clarification_continuity(...)` binds a human reply to the active replay-backed clarification, verifies satisfaction, emits `CLARIFICATION_RESOLVED` or `CLARIFICATION_STILL_REQUIRED`, and records a continuity artifact (`aigol/runtime/platform_core_project_services.py:332` to `aigol/runtime/platform_core_project_services.py:390`).

`./aicli` partially reuses this by submitting replies back into `_submit_composed_request(...)`, but it still carries `pending_clarification` locally and decides local prompt/session behavior.

## Approval Lifecycle Review

Approval preparation is implemented in Platform Core. Approval collection is still bound by Human Interfaces.

Evidence:

- `_conversation_approval_summary(...)` emits `summary_authority: PLATFORM_CORE`, `canonical_runtime_prompt`, `requires_human_approval`, `runtime_after_approval: CERTIFIED_PLATFORM_CORE_RUNTIME`, and `approval_state: PENDING_HUMAN_APPROVAL` when summary-admissible (`aigol/runtime/platform_core_project_services.py:1881` to `aigol/runtime/platform_core_project_services.py:1904`).
- `build_persistent_workspace_state_artifact(...)` persists `pending_implementation_summary`, `pending_approval`, and `pending_approval_kind: IMPLEMENTATION_SUMMARY_APPROVAL` (`aigol/runtime/platform_core_project_services.py:948` to `aigol/runtime/platform_core_project_services.py:964`).
- `run_human_interface_runtime_entry(...)` handles the certified runtime entry after an approved prompt is submitted (`aigol/runtime/human_interface_runtime_entry_service.py:137` to `aigol/runtime/human_interface_runtime_entry_service.py:218`).

`./aicli` currently stores `pending_summary` locally, recognizes `/approve`, extracts `canonical_runtime_prompt`, and then calls Runtime Entry (`aigol/cli/aicli.py:191` to `aigol/cli/aicli.py:244`). This is thin compared to governance execution, but it is still local approval binding logic.

## Human Interface Binding Review

`./aicli` consumes Platform Core outputs but still performs local binding decisions.

Duplicated or interface-local state:

- `pending_summary`, `pending_clarification`, `session_status`, `runtime_status`, `last_resolution`, `last_project_context`, and `transcript` are local variables in interactive mode (`aigol/cli/aicli.py:65` to `aigol/cli/aicli.py:80`).
- `/send`, `.`, `/cancel`, `/approve`, `/exit`, EOF, and `KeyboardInterrupt` are interpreted locally (`aigol/cli/aicli.py:83` to `aigol/cli/aicli.py:247`).
- `_submit_composed_request(...)` renders Platform Core output but chooses the local return shape: pending clarification, pending summary, or non-development response (`aigol/cli/aicli.py:720` to `aigol/cli/aicli.py:749`).

Correct reuse:

- `_summary_from_conversation(...)` requires Platform Core `approval_summary`, so `./aicli` no longer authors the approval summary (`aigol/cli/aicli.py:752` to `aigol/cli/aicli.py:756`).
- `/approve` delegates to `run_human_interface_runtime_entry(...)` and does not execute or authorize work locally (`aigol/cli/aicli.py:219` to `aigol/cli/aicli.py:244`).
- Final results explicitly preserve `aicli_authorizes: False`, `aicli_executes: False`, `aicli_owns_replay: False`, and related boundary markers (`aigol/cli/aicli.py:271` to `aigol/cli/aicli.py:281`).

The G17-HI-02F hardening reduced one premature-termination issue by preserving pending approval on EOF, but it did not convert `./aicli` into a pure consumer of a canonical Platform Core conversation event runtime.

## Reuse Classification Matrix

| Capability | Classification | Evidence |
| --- | --- | --- |
| Runtime Entry | Already implemented in Platform Core | `run_human_interface_runtime_entry(...)` is interface-neutral and records workspace state. |
| Runtime Continuation After Approval | Already implemented in Platform Core, partially reused by `./aicli` | Platform Core approval summary returns `runtime_after_approval`; `./aicli` calls Runtime Entry on `/approve`. |
| Human Intent Resolution | Already implemented in Platform Core | `prepare_unified_human_interface_project_context(...)` returns `development_intent_resolution`. |
| Human Conversation Experience | Already implemented in Platform Core | Conversation artifact includes authority, response mode, headline, explanation, progress, approval summary, fail-closed response. |
| Clarification Questions | Already implemented in Platform Core | `response_mode: CLARIFICATION`, clarification planner, questions, and replay-backed continuity. |
| Clarification Continuity | Already implemented in Platform Core, partially reused by `./aicli` | Workspace replay restores active clarification and binds replies. |
| Approval Summary | Already implemented in Platform Core, partially reused by `./aicli` | `approval_summary` is Platform Core-authored; `./aicli` renders and stores it locally. |
| Pending Approval State | Already implemented in Platform Core, duplicated in `./aicli` | Workspace state persists `pending_approval`; `./aicli` also has local `pending_summary`. |
| Pending Clarification State | Already implemented in Platform Core, duplicated in `./aicli` | Workspace state persists `pending_clarification_request`; `./aicli` also has local `pending_clarification`. |
| Session Restoration | Already implemented in Platform Core | `latest_platform_core_workspace_state(...)` restores workspace state from replay. |
| Runtime Projection | Partially implemented in Platform Core | `human_conversation_experience` projects user-facing content but not a full canonical event/action/session-close projection API. |
| Conversation Event Runtime | Genuinely missing as an implemented canonical boundary | Boundary event names are present in the G17-HI-02B specification, not implementation. |
| Session Close Authority Field | Genuinely missing as implemented Platform Core field | `session_close_allowed` appears in the specification, not implementation. |
| Human Interface Binding | Implemented only in `./aicli` today | `./aicli` owns command mapping, loop state, EOF handling, and local session status strings. |

## Remaining Gaps

1. A single implemented canonical conversation boundary API is not present.

Existing Platform Core services provide semantic state and replay state, but Human Interfaces do not yet call one function that accepts canonical events and returns a canonical projection with `conversation_state`, `expected_action`, `pending_approval`, `pending_clarification`, `continuation_allowed`, and `session_close_allowed`.

2. `./aicli` still owns local command-to-transition binding.

The CLI maps `/send`, `/approve`, `/cancel`, EOF, and interrupt behavior locally. This is acceptable as transport handling, but some of it currently overlaps Platform Core conversation lifecycle ownership.

3. Platform Core approval persistence exists, but approval-event acceptance is not exposed as a reusable event boundary.

New interfaces can reuse the approval summary and Runtime Entry unchanged, but each interface would still need to decide how to convert a user approval gesture into the current Runtime Entry call.

## Architectural Findings

Platform Core reuse is substantial and should be maximized.

No new Human Intent Resolution, clarification planner, approval summary generator, runtime entry service, replay state model, or governance/runtime continuation mechanism should be created in any Human Interface.

The missing piece is not another semantic runtime. It is a binding layer that lets interfaces consume existing Platform Core artifacts through a canonical event/projection contract.

## Final Recommendation

Do not implement duplicate conversation logic in `./aicli`, Web, Mobile, Voice, REST, or AiGOL Next.

Prefer reusing:

- `prepare_unified_human_interface_project_context(...)`;
- `record_unified_human_interface_workspace_state(...)`;
- `run_human_interface_runtime_entry(...)`;
- replay-backed clarification continuity;
- Platform Core `human_conversation_experience`;
- Platform Core approval summaries.

If further implementation is pursued, keep it minor and binding-oriented: expose an implemented Platform Core conversation boundary that wraps the existing primitives and returns canonical conversation projection/action fields. That would let Human Interfaces become pure transport/render/input adapters without reimplementing state decisions.

## Final Verdict

PLATFORM_CORE_REUSE_WITH_MINOR_BINDING

The existing Platform Core implementation already provides the reusable semantic conversation runtime primitives. A new Human Interface could reuse those primitives unchanged, but it would still need local binding code unless the G17-HI-02B Platform Core Conversation Boundary is implemented as a single runtime API. Therefore, the remaining work is primarily Human Interface binding plus a small canonical boundary wrapper, not additional Platform Core semantic implementation.
