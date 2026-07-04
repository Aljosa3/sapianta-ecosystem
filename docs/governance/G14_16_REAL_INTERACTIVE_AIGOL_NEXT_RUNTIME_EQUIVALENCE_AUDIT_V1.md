# G14-16 Real Interactive AiGOL Next Runtime Equivalence Audit V1

Status: repository CLI runtime equivalence confirmed; literal external executable equivalence not fully confirmable in this workspace.

Final verdict: REAL_INTERACTIVE_RUNTIME_EQUIVALENCE_PARTIALLY_CONFIRMED

## 1. Executive Summary

G14-16 audited whether the real interactive `aigol next` CLI path used by a human operator is equivalent to the runtime path exercised during G14-15 acceptance certification.

The repository CLI path used in G14-15 was:

```text
python -m aigol.cli.aigol_cli next
```

In the current workspace, the literal executable:

```text
aigol
```

is not available on `PATH`.

Therefore, strict equivalence between an external installed `aigol` executable and the repository CLI module cannot be fully certified from this workspace.

However, the repository CLI interactive path itself was audited and validated:

```text
python -m aigol.cli.aigol_cli next
-> run_acli_next_persistent_conversational_session
-> /approve
-> _run_acli_next_runtime_bound_session
-> run_interactive_conversation
-> NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
-> Governance
-> Provider
-> Worker
-> Replay certification
```

The repository CLI path is equivalent to the G14-15 acceptance path and currently reaches the certified runtime.

Final verdict: REAL_INTERACTIVE_RUNTIME_EQUIVALENCE_PARTIALLY_CONFIRMED

## 2. Entry-Point Comparison

### 2.1 Literal Terminal Executable

Audit command:

```text
command -v aigol
```

Result:

```text
not found
```

Finding:

```text
The literal external `aigol` executable could not be inspected because it is not present on PATH in this workspace.
```

If a human terminal outside this workspace resolves `aigol`, that executable may be:

- an installed wrapper around `aigol.cli.aigol_cli:main`;
- an older installed package;
- a shell alias;
- a virtual-environment script;
- another entry point not represented by the current workspace.

That external binding must be inspected before literal executable equivalence can be fully certified.

### 2.2 G14-15 Acceptance Entry

G14-15 used:

```text
python -m aigol.cli.aigol_cli next
```

This is a CLI module entry, not direct invocation of internal runtime functions.

Evidence:

```text
aigol/cli/aigol_cli.py
if __name__ == "__main__":
    raise SystemExit(main())
```

The `main()` function dispatches `next` to the persistent conversational session when `_should_run_persistent_acli_next(args)` is true.

## 3. Repository CLI Call Graph

The audited repository CLI path is:

```text
python -m aigol.cli.aigol_cli next
-> main()
-> _should_run_persistent_acli_next(args)
-> run_acli_next_persistent_conversational_session(...)
-> /send
-> governed implementation summary
-> /approve
-> submit_turn(...)
-> _run_acli_next_runtime_bound_session(...)
-> run_acli_next_conversational_session(...)
-> is_native_development_prompt(...)
-> run_interactive_conversation(...)
-> route_conversational_cli_intent(...)
-> NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
-> post-entry continuation
-> PPP routing continuation
-> Governance authorization
-> Provider proposal production
-> Worker invocation
-> Result validation
-> Replay certification
```

Implementation evidence:

| Step | Location |
| --- | --- |
| CLI entry | `aigol/cli/aigol_cli.py::main` |
| Persistent session | `aigol/acli_next/conversational.py::run_acli_next_persistent_conversational_session` |
| Approval handling | `aigol/acli_next/conversational.py`, `/approve` branch |
| Runtime binding | `aigol/cli/aigol_cli.py::_run_acli_next_runtime_bound_session` |
| Binding acceptance gate | `is_native_development_prompt(prompt)` |
| Interactive runtime dispatcher | `aigol/cli/aigol_cli.py::run_interactive_conversation` |
| Conversational route | `aigol/runtime/conversational_cli_runtime.py::route_conversational_cli_intent` |

## 4. Approval Analysis

The `/approve` command is handled by:

```text
aigol/acli_next/conversational.py::run_acli_next_persistent_conversational_session
```

On approval, it calls:

```text
turn_result = submit_turn(
    session_id=conversation_id,
    prompts=[pending_summary["refined_message"]],
    created_at=created_at,
    replay_dir=replay_dir,
    workspace=workspace,
)
```

In the CLI entry path, `submit_turn` is:

```text
_run_acli_next_runtime_bound_session
```

because `main()` passes:

```text
turn_runner=_run_acli_next_runtime_bound_session
```

Therefore, approval handling in the repository CLI path is the same binding function used by G14-15 acceptance.

## 5. Runtime Binding Analysis

Runtime binding can return:

```text
AIGOL_NEXT_RUNTIME_BINDING_NOT_REQUIRED
```

only when the binding gate rejects the prompt:

```text
if not any(is_native_development_prompt(prompt) for prompt in prompts):
    runtime_binding_status = AIGOL_NEXT_RUNTIME_BINDING_NOT_REQUIRED
    runtime_entered = False
```

This means `NOT_REQUIRED` is not produced by Governance, Provider Platform, Worker Platform, Replay, or Capability Coverage.

It is produced before native runtime entry when the approved prompt is not classified as native development.

## 6. Dispatcher Analysis

When the binding gate accepts a prompt, `_run_acli_next_runtime_bound_session` invokes:

```text
run_interactive_conversation(...)
```

with:

```text
auto_continue=True
operator_context=AIGOL_NEXT_RUNTIME_BINDING
```

The dispatcher then records conversational routing evidence and selects:

```text
NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
```

for certified native development prompts.

The current repository CLI validation confirmed this route.

## 7. Runtime Evidence

Repository CLI equivalence validation command:

```text
python -m aigol.cli.aigol_cli next \
  --session-id G14-16-EQUIVALENCE-REPO-CLI \
  --runtime-root /tmp/aigol_g14_16_equivalence_repo_cli \
  --workspace /home/pisarna/work/sapianta \
  --created-at 2026-07-04T00:00:00Z
```

Interactive transcript:

```text
AiGOL> Implement a native validation helper for replay evidence summaries.
AiGOL> /send
Governed implementation summary

AiGOL> /approve
runtime_binding_status: AIGOL_NEXT_RUNTIME_BOUND
runtime_entered: True
governance_authorization_reached: True
provider_invocation_reached: True
worker_execution_reached: True
replay_certification_reached: True
manual_chatgpt_codex_transfer_required: False
```

Runtime evidence root:

```text
/tmp/aigol_g14_16_equivalence_repo_cli/G14-16-EQUIVALENCE-REPO-CLI/TURN-000001
```

Representative evidence:

```text
conversational_cli_routing/000_conversational_routing_decision_recorded.json
workflow_id: NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
```

```text
certified_development_continuation/execution_authorization/003_authorization_result_recorded.json
authorization_status: EXECUTION_AUTHORIZED
```

```text
certified_development_continuation/worker_lifecycle_continuation/worker_invocation/003_invocation_result_recorded.json
invocation_status: WORKER_INVOKED
worker_invoked: true
```

```text
certified_development_continuation/worker_lifecycle_continuation/replay_certification/001_replay_certification_returned.json
certification_status: REPLAY_CERTIFICATION_COMPLETED
```

## 8. Discrepancy Assessment

The reported real manual output:

```text
runtime_binding_status: AIGOL_NEXT_RUNTIME_BINDING_NOT_REQUIRED
runtime_entered: False
provider_invocation_reached: None
worker_execution_reached: None
Classify Capability Coverage
Existing Capability Audit
```

is explainable by the runtime binding gate:

```text
is_native_development_prompt(prompt) == False
```

or by a different/stale executable path that does not contain the G14-14/G14-15 deterministic coverage corrections.

In the current repository CLI path, the same prompt now produces:

```text
runtime_binding_status: AIGOL_NEXT_RUNTIME_BOUND
runtime_entered: True
```

## 9. Root Cause Classification

Classification:

```text
Other
```

Reason:

```text
The repository CLI path is equivalent and currently certified, but the literal external `aigol` executable cannot be inspected in this workspace because it is not on PATH.
```

If the human terminal still resolves `aigol next` to a runtime that returns `AIGOL_NEXT_RUNTIME_BINDING_NOT_REQUIRED` for the same prompt, the most likely evidence-based explanation is:

```text
Different Entry Point or Configuration Difference
```

Specifically, an installed executable or alias may point to stale code or a different environment from the repository CLI module validated by G14-15 and this audit.

That cannot be proven from this workspace without the resolved `aigol` executable path.

## 10. Acceptance Path Investigation

G14-15 did not invoke isolated internal runtime functions directly.

It invoked the repository CLI module:

```text
python -m aigol.cli.aigol_cli next
```

This path entered:

```text
main()
-> run_acli_next_persistent_conversational_session(...)
-> _run_acli_next_runtime_bound_session(...)
-> run_interactive_conversation(...)
```

Therefore G14-15 exercised the real repository CLI runtime path, but not a separate installed `aigol` console script.

## 11. Certification Summary

Repository CLI runtime equivalence is confirmed.

Strict literal executable equivalence is only partially confirmed because:

- `aigol` is not available on `PATH` in the audit workspace;
- the exact external executable used by the human terminal could not be inspected;
- the repository CLI module path is currently runtime-bound and certified.

Final verdict: REAL_INTERACTIVE_RUNTIME_EQUIVALENCE_PARTIALLY_CONFIRMED

## 12. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: REAL_INTERACTIVE_RUNTIME_EQUIVALENCE_PARTIALLY_CONFIRMED
