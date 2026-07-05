# G14-29 Reference UHI Runtime Entrypoint Equivalence Audit V1

Status: reference UHI runtime entrypoint partially equivalent.

Final verdict: REFERENCE_UHI_RUNTIME_ENTRYPOINT_PARTIALLY_EQUIVALENT

## 1. Executive Summary

G14-29 audited whether the reference Unified Human Interface, `./aicli`, delegates to exactly the same canonical runtime entrypoint as:

```text
python -m aigol.cli.aigol_cli next
```

after the user issues:

```text
/approve
```

The answer is:

```text
No. ./aicli does not invoke the identical runtime binding entrypoint.
```

`./aicli` and `aigol next` are partially equivalent because both ultimately call the same governed runtime function:

```text
run_interactive_conversation
```

However, they do not use the same runtime binding wrapper:

- `./aicli` uses `aigol/cli/aicli.py::_run_certified_runtime`;
- `python -m aigol.cli.aigol_cli next` uses `aigol/cli/aigol_cli.py::_run_acli_next_runtime_bound_session`;
- real interactive `aigol next` uses `run_acli_next_persistent_conversational_session` with `_run_acli_next_runtime_bound_session` as its turn runner.

Therefore the lower governed runtime entry is shared, but the canonical runtime binding entrypoint is not identical.

No implementation change was made during this audit.

## 2. Runtime Call Graph: `./aicli`

Source:

```text
aigol/cli/aicli.py
```

Approval path:

```text
run_reference_uhi_session
↓
/approve branch
↓
runner(...)
↓
_run_certified_runtime
↓
run_interactive_conversation
↓
Governance / Provider Platform / Worker Platform / Replay
```

Implementation evidence:

- `/approve` is handled in `run_reference_uhi_session`.
- The pending summary prompt is extracted from `pending_summary["canonical_runtime_prompt"]`.
- The runtime is entered by calling `runner(...)`.
- The default runner is `_run_certified_runtime`.
- `_run_certified_runtime` constructs an `argparse.Namespace` with:

```text
operator_context="REFERENCE_UHI_RUNTIME"
auto_continue=True
```

- `_run_certified_runtime` invokes:

```text
run_interactive_conversation(
    conversation_args,
    input_func=_input_sequence([prompt, "exit"]),
    output_func=output.append,
)
```

Runtime status is derived by:

```text
_runtime_binding_status(conversation_result, latest_turn)
```

The status becomes `REFERENCE_UHI_RUNTIME_BOUND` only when:

```text
failed_turns == 0
worker_invoked is True
replay_certification_reached is True
```

Otherwise it returns:

```text
REFERENCE_UHI_RUNTIME_PARTIALLY_BOUND
```

## 3. Runtime Call Graph: `python -m aigol.cli.aigol_cli next`

Source:

```text
aigol/cli/aigol_cli.py
```

Non-interactive repository entrypoint:

```text
run_command
↓
args.command == "next" and args.next_command is None
↓
_run_acli_next_runtime_bound_session
↓
run_acli_next_conversational_session
↓
prepare_unified_human_interface_project_context
↓
run_interactive_conversation
↓
Governance / Provider Platform / Worker Platform / Replay
```

Implementation evidence:

```text
if args.command == "next" and args.next_command is None:
    return _run_acli_next_runtime_bound_session(...)
```

Inside `_run_acli_next_runtime_bound_session`, the runtime is entered by:

```text
run_interactive_conversation(
    conversation_args,
    input_func=_acli_next_input_sequence([*runtime_prompts, "exit"]),
    output_func=conversation_output.append,
)
```

Runtime status is derived by:

```text
_acli_next_runtime_binding_status(conversation_result, latest_turn)
```

The status becomes `AIGOL_NEXT_RUNTIME_BOUND` only when:

```text
failed_turns == 0
worker_invoked is True
replay_certification_reached is True
```

Otherwise it returns:

```text
AIGOL_NEXT_RUNTIME_PARTIALLY_BOUND
```

## 4. Runtime Call Graph: Real Interactive `aigol next`

When `aigol next` is run interactively, `main` selects the persistent session path:

```text
_should_run_persistent_acli_next(args)
↓
run_acli_next_persistent_conversational_session
↓
/approve inside persistent session
↓
turn_runner=_run_acli_next_runtime_bound_session
↓
run_interactive_conversation
↓
Governance / Provider Platform / Worker Platform / Replay
```

Implementation evidence:

```text
if _should_run_persistent_acli_next(args):
    result = run_acli_next_persistent_conversational_session(
        ...
        turn_runner=_run_acli_next_runtime_bound_session,
        guided_development_workflow=True,
    )
```

The persistent path therefore still uses the same `aigol next` runtime binding wrapper:

```text
_run_acli_next_runtime_bound_session
```

## 5. Entrypoint Comparison

| Runtime element | `./aicli` | `python -m aigol.cli.aigol_cli next` | Equivalent |
| --- | --- | --- | --- |
| Human interface | `aicli` | `aigol next` | Different |
| Approval handler | `aicli.run_reference_uhi_session` | `run_acli_next_persistent_conversational_session` or `run_command` path | Different |
| Runtime binding wrapper | `_run_certified_runtime` | `_run_acli_next_runtime_bound_session` | Different |
| Project context service | `prepare_unified_human_interface_project_context` | `prepare_unified_human_interface_project_context` | Same |
| Lower governed runtime function | `run_interactive_conversation` | `run_interactive_conversation` | Same |
| Governance entry | reached through `run_interactive_conversation` | reached through `run_interactive_conversation` | Same after lower runtime entry |
| Provider invocation entry | reached through `run_interactive_conversation` | reached through `run_interactive_conversation` | Same after lower runtime entry |
| Worker execution entry | reached through `run_interactive_conversation` | reached through `run_interactive_conversation` | Same after lower runtime entry |
| Replay entry | reached through `run_interactive_conversation` | reached through `run_interactive_conversation` | Same after lower runtime entry |
| Runtime status namespace | `REFERENCE_UHI_RUNTIME_*` | `AIGOL_NEXT_RUNTIME_*` | Different |

## 6. First Point of Divergence

The first point of divergence is the approval-to-runtime binding call.

For `./aicli`:

```text
/approve
↓
runner(...)
↓
_run_certified_runtime
```

For `aigol next`:

```text
/approve or approved runtime prompt
↓
_run_acli_next_runtime_bound_session
```

Both wrappers call `run_interactive_conversation`, but they are not the same canonical runtime binding entrypoint.

## 7. Early Exit Analysis

No source-level early return was found in `./aicli` before calling the governed runtime after approval.

When approval is present and a pending summary exists, `./aicli` calls:

```text
runtime_result = runner(...)
```

The default runner enters:

```text
run_interactive_conversation
```

The `REFERENCE_UHI_RUNTIME_PARTIALLY_BOUND` status is not caused by an early return in `aicli`. It is produced by `_runtime_binding_status` when the returned latest turn does not satisfy both:

```text
worker_invoked is True
replay_certification_reached is True
```

Therefore, a partial binding result means the lower runtime result did not report complete Worker and Replay certification evidence for that specific execution.

## 8. Implementation Evidence

Evidence from `aigol/cli/aicli.py`:

- `run_reference_uhi_session` handles `/approve`;
- `/approve` calls `runner(...)`;
- default runner is `_run_certified_runtime`;
- `_run_certified_runtime` calls `run_interactive_conversation`;
- `_runtime_binding_status` returns `REFERENCE_UHI_RUNTIME_PARTIALLY_BOUND` unless the latest turn includes `worker_invoked` and `replay_certification_reached`.

Evidence from `aigol/cli/aigol_cli.py`:

- `run_command` routes non-interactive `next` to `_run_acli_next_runtime_bound_session`;
- `main` routes real interactive `next` to `run_acli_next_persistent_conversational_session`;
- the persistent session uses `_run_acli_next_runtime_bound_session` as `turn_runner`;
- `_run_acli_next_runtime_bound_session` calls `run_interactive_conversation`;
- `_acli_next_runtime_binding_status` uses the same completion condition as `aicli`, but returns the `AIGOL_NEXT_RUNTIME_*` status namespace.

## 9. Recommended Minimal Correction

If runtime entrypoint identity is required, the minimal correction is:

```text
delegate ./aicli approval into the canonical runtime binding entrypoint used by aigol next
```

That means `aicli` should not maintain its own `_run_certified_runtime` wrapper as a separate runtime binding path. It should call a shared Platform Core or UHI runtime binding service, or directly reuse the same canonical binding currently represented by:

```text
_run_acli_next_runtime_bound_session
```

The correction should not:

- move business logic into `aicli`;
- duplicate runtime binding logic;
- introduce interface-specific Platform Core behavior;
- bypass Governance, Provider Platform, Worker Platform, or Replay.

## 10. Validation Evidence

Regression validation:

```text
python -m pytest tests/test_g14_22_reference_unified_human_interface_v1.py tests/test_g14_27_unified_human_interface_runtime_project_services_v1.py -q
```

Result:

```text
10 passed
```

Whitespace validation:

```text
git diff --check
```

Validation result: clean.

No implementation changes were made.

## 11. Certification Summary

`./aicli` and `python -m aigol.cli.aigol_cli next` are partially equivalent:

- they share Platform Core project services;
- they share the lower governed runtime function;
- they reach the same Governance, Provider, Worker, and Replay layers after `run_interactive_conversation`;
- they do not share the same runtime binding wrapper after approval.

The first divergence is:

```text
aicli._run_certified_runtime
```

versus:

```text
aigol_cli._run_acli_next_runtime_bound_session
```

Final verdict: REFERENCE_UHI_RUNTIME_ENTRYPOINT_PARTIALLY_EQUIVALENT
