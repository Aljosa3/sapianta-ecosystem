# G17-HI-02L - Clarification Response Binding Reuse Audit

Status: governed audit artifact  
Date: 2026-07-10  
Scope: implementation evidence review only  
Final verdict: CLARIFICATION_BINDING_REUSABLE_WITH_MINOR_BINDING

## Executive Summary

Platform Core already contains the canonical mechanism needed to bind a Human Interface clarification response to an existing governed workflow.

The reusable mechanism is:

1. `prepare_unified_human_interface_project_context(...)` restores the latest Platform Core workspace state for the same `session_id` and `runtime_root`.
2. `replay_backed_uhi_clarification_state(...)` recovers an active clarification from `pending_clarification_request`.
3. `resolve_uhi_clarification_continuity(...)` binds the next submitted message to that active clarification, verifies satisfaction, preserves replay lineage, and marks `new_governed_request_created: False`.
4. `record_unified_human_interface_workspace_state(...)` records the pending clarification state that makes the next turn bindable.

The mechanism is not merely documentary. It is implemented in Platform Core project services and validated by tests that prove a submitted clarification answer binds to replay-backed active clarification instead of creating a new governed request.

The remaining issue is binding consistency in Human Interfaces. `./aicli` submit mode records workspace state between turns and therefore reuses the Platform Core mechanism. The interactive mode keeps pending clarification in local variables during the live loop, but does not record the pending clarification workspace state until session finalization. That can prevent Platform Core from seeing the replay-backed active clarification before the next same-process reply.

Therefore, new Platform Core clarification semantics are not required. The remaining work is a minor Human Interface binding repair: every Human Interface must persist or bind the Platform Core pending clarification state before accepting a clarification response, then submit the response through the same Platform Core project-services entry point.

## Observed Runtime Evidence

The reported operational failure was:

- Platform Core asked a clarification question.
- The user answered the clarification.
- The answer was interpreted as a new governed development request.

The implementation evidence indicates this is a binding-path failure, not absence of Platform Core capability.

`prepare_unified_human_interface_project_context(...)` restores prior state from the session root before resolving the new message (`aigol/runtime/platform_core_project_services.py:156-191`). If prior state contains a pending clarification, it does not treat the incoming message as an ordinary new request. It calls `resolve_uhi_clarification_continuity(...)` with the active clarification state (`aigol/runtime/platform_core_project_services.py:180-189`).

The continuity artifact explicitly records:

- `reply_bound_to_active_clarification: True`
- `clarification_continuity_status`
- `clarification_resolved`
- `new_governed_request_created: False`
- `semantic_lineage_preserved: True`
- `replay_lineage_preserved: True`
- `human_interface_authority: False`

These fields are produced in `aigol/runtime/platform_core_project_services.py:372-408`.

The enriched resolution also carries `clarification_reply_bound`, `clarification_resolved`, `clarification_reply_resolution_source`, `new_governed_request_created: False`, and `platform_core_resolves_clarification: True` (`aigol/runtime/platform_core_project_services.py:435-457`).

## Clarification Lifecycle Review

Platform Core owns the clarification lifecycle.

Clarification projection is produced by `human_conversation_experience_from_resolution(...)`. It creates the canonical human conversation response model and sets `response_mode: CLARIFICATION` when deterministic intent resolution requires clarification (`aigol/runtime/platform_core_project_services.py:1726-1770`). It also asks clarification for reuse, architecture, and vague-improvement cases (`aigol/runtime/platform_core_project_services.py:1771-1797`).

Clarification state is replay-backed. `latest_platform_core_workspace_state(...)` loads the latest `*_workspace_state_recorded.json` artifact from the session workspace state directory (`aigol/runtime/platform_core_project_services.py:290-302`). `replay_backed_uhi_clarification_state(...)` converts `pending_clarification_request` into `PLATFORM_CORE_UHI_ACTIVE_CLARIFICATION_STATE_V1` and marks `platform_core_authority: True` and `human_interface_authority: False` (`aigol/runtime/platform_core_project_services.py:305-329`).

Clarification questions receive deterministic identifiers and semantic slots through `deterministic_clarification_question_bindings(...)` (`aigol/runtime/platform_core_project_services.py:463-474`) and `semantic_slot_for_clarification_question(...)` (`aigol/runtime/platform_core_project_services.py:477-505`).

Clarification satisfaction is owned by Platform Core. `clarification_satisfaction_verification(...)` returns `PLATFORM_CORE_CLARIFICATION_SATISFACTION_VERIFICATION_V1`, including the active question, semantic slot, satisfied and pending slots, `platform_core_owns_satisfaction: True`, `human_interface_authority: False`, and `replay_visible: True` (`aigol/runtime/platform_core_project_services.py:508-566`).

## Runtime Continuation Review

Clarification response binding is part of the governed workflow continuation path before approval and runtime entry.

When the reply satisfies the active clarification, `resolve_uhi_clarification_continuity(...)` can switch the resolution source to `ORIGINAL_REQUEST_WITH_BOUND_CLARIFICATION_REPLY` and re-resolve the original request plus the bound clarification reply (`aigol/runtime/platform_core_project_services.py:352-363`). A resolved clarification requires both summary admissibility and satisfaction (`aigol/runtime/platform_core_project_services.py:364-368`).

After resolution, `human_conversation_experience_from_resolution(...)` can project `APPROVAL_PREPARATION` when `summary_admissible` is true (`aigol/runtime/platform_core_project_services.py:1753-1760`). `./aicli` then continues to approval and delegates to the certified runtime entry on `/approve` (`aigol/cli/aicli.py:191-240`).

This preserves the boundary: clarification continuation determines whether the governed workflow can reach approval; runtime entry remains separate and approval-gated.

## Existing Platform Core Binding Review

The canonical Platform Core binding mechanism already exists.

The entry point is `prepare_unified_human_interface_project_context(...)`, documented in code as the canonical Platform Core project-services context for any UHI (`aigol/runtime/platform_core_project_services.py:156-165`). It restores prior state, detects active replay-backed clarification, and binds the incoming message as a clarification response when active clarification exists (`aigol/runtime/platform_core_project_services.py:167-191`).

The persistence half of the mechanism is `record_unified_human_interface_workspace_state(...)`, documented as recording the canonical Platform Core project workspace state for any UHI (`aigol/runtime/platform_core_project_services.py:253-265`). The persistent artifact stores `pending_clarification_request`, `pending_implementation_summary`, `pending_approval`, and `resumable_conversational_context: True` (`aigol/runtime/platform_core_project_services.py:948-979`).

The project context artifact declares Platform Core authority for workspace, guidance, knowledge reuse, development intent resolution, and human conversation experience, while `interface_authority` is false (`aigol/runtime/platform_core_project_services.py:230-240`).

## Human Interface Binding Review

`./aicli` uses the Platform Core entry point for submitted user text. `_submit_composed_request(...)` always calls `prepare_unified_human_interface_project_context(...)` with `interface_name: "aicli"`, the current `session_id`, message, runtime root, workspace, and creation time (`aigol/cli/aicli.py:702-720`). It then renders the Platform Core conversation result and branches only on Platform Core fields: `development_intent_resolution` and `human_conversation_experience.response_mode` (`aigol/cli/aicli.py:723-749`).

`./aicli` submit mode already binds clarification replies through the reusable mechanism. After the initial submission, it records workspace state with `pending_clarification` and `pending_summary` (`aigol/cli/aicli.py:342-383`). While pending clarification exists, it reads a clarification reply and submits that reply through `_submit_composed_request(...)` (`aigol/cli/aicli.py:390-432`). It then records workspace state again with the updated pending state (`aigol/cli/aicli.py:433-457`).

Focused tests prove this path. `test_submit_clarification_reply_binds_to_replay_backed_active_clarification` asserts the continuity artifact has `reply_bound_to_active_clarification: True`, `clarification_continuity_status: CLARIFICATION_RESOLVED`, `new_governed_request_created: False`, and `human_interface_authority: False` (`tests/test_g15_hir_02_replay_backed_clarification_continuity.py:53-89`). The insufficient-answer test proves a non-satisfying reply remains replay-continuous instead of becoming a new request (`tests/test_g15_hir_02_replay_backed_clarification_continuity.py:92-134`).

`test_answered_clarification_is_consumed_and_not_reopened` proves a satisfying answer produces a bound resolution source of `ORIGINAL_REQUEST_WITH_BOUND_CLARIFICATION_REPLY`, clears the final pending clarification request, and enters runtime only after approval (`tests/test_g15_hir_07_clarification_resolution_state_management.py:62-117`).

`./aicli` interactive mode is weaker. It stores `pending_clarification` locally (`aigol/cli/aicli.py:65-80`), submits `/send` through `_submit_composed_request(...)` (`aigol/cli/aicli.py:165-190`), but records Platform Core workspace state only after the interactive session result is assembled (`aigol/cli/aicli.py:283-300`). Because the Platform Core binder discovers active clarification from recorded workspace replay, a same-process interactive reply can lack replay-backed pending clarification at the moment it is submitted. That is the likely path by which a clarification answer is interpreted as a new governed request.

This is not a license for `./aicli` to own clarification semantics. The correct repair is to bind to the existing Platform Core persistence and continuity mechanism consistently.

## Reuse Classification Matrix

| Capability | Classification | Evidence |
|---|---|---|
| Clarification projection | already implemented in Platform Core | `human_conversation_experience_from_resolution(...)` produces `CLARIFICATION` responses and questions (`aigol/runtime/platform_core_project_services.py:1726-1797`). |
| Pending clarification state | already implemented in Platform Core | Workspace artifacts store `pending_clarification_request` (`aigol/runtime/platform_core_project_services.py:948-963`). |
| Active clarification recovery | already implemented in Platform Core | `replay_backed_uhi_clarification_state(...)` restores active state from workspace replay (`aigol/runtime/platform_core_project_services.py:305-329`). |
| Clarification identifiers | already implemented in Platform Core | Deterministic question IDs and semantic slots are generated by Platform Core (`aigol/runtime/platform_core_project_services.py:463-505`). |
| Expected response semantics | already implemented in Platform Core | Satisfaction verification and explainability define open slot and deterministic continuation status (`aigol/runtime/platform_core_project_services.py:508-617`). |
| Clarification response binding | already implemented in Platform Core | `resolve_uhi_clarification_continuity(...)` binds reply to active clarification and records continuity (`aigol/runtime/platform_core_project_services.py:332-460`). |
| Replay evidence for response binding | already implemented in Platform Core | Continuity artifacts are written under `uhi_clarification_continuity` (`aigol/runtime/platform_core_project_services.py:409-415`). |
| Submit-mode Human Interface binding | reusable through existing binding | `run_reference_uhi_submit_session(...)` records pending state and resubmits replies through `_submit_composed_request(...)` (`aigol/cli/aicli.py:342-457`). |
| Interactive Human Interface binding | reusable with minor binding | Interactive mode records state at session finalization, not immediately after clarification projection (`aigol/cli/aicli.py:165-190`, `aigol/cli/aicli.py:283-300`). |
| Human Interface semantic classification of reply versus new request | duplicated if implemented in HI; should be avoided | Platform Core already makes this distinction from replay-backed active clarification (`aigol/runtime/platform_core_project_services.py:180-191`). |
| New Platform Core clarification engine | genuinely not required | Existing implementation and tests prove resolved and unresolved clarification continuity. |

## Canonical Clarification Response Mechanism

Every Human Interface should use this canonical mechanism:

1. Submit user text to `prepare_unified_human_interface_project_context(...)` with stable `interface_name`, `session_id`, `runtime_root`, `workspace`, and `created_at`.
2. Render the returned `human_conversation_experience`.
3. If Platform Core projects `response_mode: CLARIFICATION`, record the Platform Core workspace state with `record_unified_human_interface_workspace_state(...)`, preserving `pending_clarification`.
4. Collect the human clarification response as transport-only input.
5. Submit the response through the same `prepare_unified_human_interface_project_context(...)` path with the same session and runtime root.
6. Let Platform Core restore `pending_clarification_request`, bind the response through `resolve_uhi_clarification_continuity(...)`, verify satisfaction, and project the next conversation state.
7. If resolved, render approval preparation. If still required, render the next clarification. If approved, delegate to certified runtime entry.

The Human Interface distinction between a new governed development request and a clarification response is not semantic inference by the interface. It is the presence of replay-backed active clarification state in Platform Core workspace replay.

## Remaining Binding Work

The remaining work is minor binding work, not new Platform Core semantics.

Required binding alignment:

- Ensure every Human Interface records pending clarification workspace state immediately after Platform Core projects clarification, before accepting a clarification reply.
- Ensure clarification replies are submitted with the same `session_id` and `runtime_root` so `latest_platform_core_workspace_state(...)` can recover active clarification.
- Ensure Human Interfaces do not classify the reply as a new governed request based on local command parsing or local pending variables.
- Ensure interactive `./aicli` follows the submit-mode pattern: Platform Core state must be replay-visible before the next clarification response is submitted.

Optional hardening:

- Expose a thin named Human Interface action such as `SUBMIT_CLARIFICATION_REPLY` that still delegates to the existing Platform Core project-services mechanism.
- Include the active clarification replay reference and question ID in Human Interface projections so Web, Mobile, Voice, REST, and future clients can display and correlate the same Platform Core state without owning it.

These are binding refinements. They do not require moving clarification lifecycle, governance, replay, or runtime continuation into Human Interfaces.

## Architectural Findings

Platform Core already owns clarification state, clarification transitions, satisfaction verification, replay continuity, and the decision whether a reply resolves the governed workflow.

Human Interfaces are already capable of consuming this boundary. `./aicli` submit mode demonstrates the reusable path and the tests certify both resolved and unresolved clarification replies.

The observed failure is consistent with an interface binding gap: pending clarification was not made replay-visible before the next interactive reply was submitted. Since the Platform Core canonical mechanism discovers active clarification from replay-backed workspace state, local pending variables alone are insufficient.

This preserves the critical invariant:

- Platform Core owns the conversation and clarification lifecycle.
- Human Interfaces transport input, render Platform Core projection, collect user response, and call Platform Core services.
- Human Interfaces must not decide whether a message is a new governed request or a clarification response.

## Final Recommendation

Reuse the existing Platform Core clarification response binding mechanism.

Do not create a second clarification engine. Do not move semantic classification into `./aicli`, Web, Mobile, Voice, REST, or any future Human Interface.

The minimal repair is to standardize Human Interface binding around the existing stateful Platform Core sequence:

- record pending clarification state when Platform Core asks a question;
- submit the reply through the same project-services context entry;
- let Platform Core bind, verify, and continue the governed workflow.

`./aicli` interactive mode should be brought into parity with submit mode by ensuring active clarification state is persisted before the next reply is submitted.

## Final Verdict

CLARIFICATION_BINDING_REUSABLE_WITH_MINOR_BINDING

Platform Core already implements the canonical clarification response mechanism. The remaining work is minor Human Interface binding consistency, especially ensuring interactive sessions make pending clarification replay-visible before submitting the human's clarification response.
