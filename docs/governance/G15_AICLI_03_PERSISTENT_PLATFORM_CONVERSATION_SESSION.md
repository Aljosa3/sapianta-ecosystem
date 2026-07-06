# G15-AICLI-03 Persistent Platform Conversation Session

## Status

Implemented.

## Knowledge Reuse Audit

Reusable certified surfaces were found and reused:

- `run_reference_uhi_session` already contains the approved runtime delegation pattern for `/approve`.
- `_submit_composed_request` already submits one complete human message into `prepare_unified_human_interface_project_context`.
- Platform Core project services already produce canonical `human_conversation_experience` artifacts with `response_mode`, clarification questions, approval summaries, and fail-closed responses.
- `record_unified_human_interface_workspace_state` already records pending clarification and pending approval state for replay-visible continuation.
- Runtime entry remains `run_human_interface_runtime_entry`.

No new conversation semantics, governance rules, approval rules, provider routing, or runtime orchestration were added to AiCLI.

## Architectural Review

The defect was in Human Interface session lifetime, not in Platform Core. `./aicli submit` could submit a large prompt and render the Platform Core clarification, but it exited immediately afterward. That prevented the human from answering the clarification inside the same Human Interface session.

The corrected flow keeps submit mode connected while Platform Core has a pending clarification or pending approval. AiCLI decides only whether there is a Platform Core response requiring more input by reading Platform Core-produced artifacts. It does not decide what the clarification means, whether approval is admissible, or how runtime execution should proceed.

## Implementation Summary

`run_reference_uhi_submit_session` now supports persistent conversation control:

- initial large prompt capture still uses `sys.stdin.read()`;
- non-empty input is submitted once through `_submit_composed_request`;
- pending clarification prompts are forwarded back into the same Platform Core project-context path;
- multiple clarification rounds are supported;
- pending approval waits for `/approve` or `/cancel`;
- `/approve` delegates to the certified runtime entry;
- `/cancel` clears pending conversation state and exits cleanly;
- non-interactive callers without a follow-up reader receive `REFERENCE_UHI_SUBMIT_AWAITING_HUMAN_INPUT`;
- intermediate pending states are recorded through Platform Core workspace-state recording so continuation remains replay-visible.

## Validation Summary

Focused validation:

```bash
python -m py_compile aigol/cli/aicli.py
python -m pytest tests/test_g15_aicli_02_submission_mode.py tests/test_g15_aicli_03_persistent_platform_conversation_session.py -q
```

Result:

```text
10 passed
```

Full repository validation was also run after implementation.

```text
5817 passed, 4 skipped
```

## Regression Test Summary

Regression coverage confirms:

- large submit-mode prompts still enter Platform Core;
- submit mode preserves line breaks;
- submit mode records awaiting-input status instead of falsely completing when follow-up input is unavailable;
- clarification can continue to governed summary;
- multiple Platform Core clarification rounds can continue;
- approval delegates to certified runtime;
- cancellation works for pending clarification;
- cancellation works for pending approval;
- AiCLI remains non-authoritative.

## Files Modified

- `aigol/cli/aicli.py`
- `tests/test_g15_aicli_02_submission_mode.py`
- `tests/test_g15_aicli_03_persistent_platform_conversation_session.py`
- `docs/governance/G15_AICLI_03_PERSISTENT_PLATFORM_CONVERSATION_SESSION.md`

## Boundary Confirmation

Platform Core remains owner of:

- conversation state;
- clarification semantics;
- approval summaries;
- governance;
- runtime orchestration;
- replay-visible workspace state;
- provider routing.

AiCLI remains owner only of:

- stdin capture;
- terminal prompts;
- stdout rendering;
- forwarding human replies into Platform Core;
- local session lifetime.

Confirmed non-authoritative flags remain false:

- `aicli_authorizes: False`
- `aicli_executes: False`
- `aicli_owns_replay: False`
- `aicli_owns_workspace: False`
- `aicli_owns_goal_mapping: False`
- `aicli_owns_provider_selection: False`

## Final Assessment

G15-AICLI-03 is certified at the Human Interface boundary. Submit mode can now participate in complete Platform Core-driven conversations without moving conversation ownership into AiCLI.
