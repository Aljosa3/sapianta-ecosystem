# CODEX_STDIN_SEALING_FIX_V1

This milestone seals inherited stdin for bounded Codex execution.

The bounded runtime keeps the existing invocation contract:

```text
codex exec <bounded_prompt>
```

and launches it with `stdin=subprocess.DEVNULL`.

## Reason

Inherited open stdin allowed Codex CLI to enter supplemental stdin read mode and emit:

```text
Reading additional input from stdin...
```

Sealing stdin removes that implicit input channel without changing the provider contract, prompt source, execution gate, workspace boundary, timeout boundary, or result classifier.

## Boundary

- no orchestration
- no retries
- no fallback
- no provider routing
- no autonomous continuation
- no hidden prompt rewriting
- no unrestricted shell execution
- no arbitrary command execution

`stdin_sealed: true` is replay-visible evidence that bounded execution did not inherit an ambient stdin authority path.
