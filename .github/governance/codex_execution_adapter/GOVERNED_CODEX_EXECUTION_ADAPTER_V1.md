# GOVERNED_CODEX_EXECUTION_ADAPTER_V1

This milestone introduces the first bounded real downstream Codex execution
adapter.

## Scope

- fixed `codex exec <bounded_prompt>` invocation contract
- explicit timeout
- `shell=False`
- bounded stdout/stderr capture
- replay-certified execution receipts

## Constitutional Statement

Bounded Codex execution remains governance-controlled and does not constitute autonomous execution.

## Boundary

The adapter is not a general agent runtime. It does not orchestrate, plan,
retry, recurse, escalate authority, or mutate governance state.
