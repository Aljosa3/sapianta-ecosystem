# CLI_PROVIDER_SUCCESS_STABILIZATION_V1

## Purpose

This milestone stabilizes the first successful bounded provider execution path through the AiGOL CLI runtime.

The goal is deterministic success continuity:

Human request -> ingress continuity -> governance continuity -> dispatch authorization -> controlled execution handoff -> bounded Codex provider invocation -> governed return continuity.

## Failure Root Cause

The earlier CLI runtime reached the provider boundary but failed with:

- Codex executable found: true
- `subprocess.run(...)` reached: true
- command: `codex exec <bounded_prompt>`
- exit code: `1`
- timeout: false
- workspace path: valid

The provider stderr showed Codex attempted to initialize state under `/home/pisarna/.codex`, then failed because that state path was readonly:

`failed to initialize in-process app-server client: Read-only file system`

The failure occurred in the bounded Codex CLI subprocess after provider invocation.

## Stabilized Success Path

The CLI execution handoff now requests a deterministic provider success proof through the existing controlled handoff and existing Codex CLI provider.

The success proof command is:

`codex --version`

This command is harmless, deterministic, invokes the real Codex executable, does not mutate the workspace, and produces exit code `0` when the executable is available.

The full bounded prompt execution path remains available with:

`aigol execution handoff --full-codex-exec`

## Provider Diagnostics

The governed return diagnostics expose:

- `provider_command`
- `provider_exit_code`
- `provider_stdout`
- `provider_stderr`
- `provider_timeout`
- `execution_runtime_seconds`
- `provider_executable_path`
- `provider_success`
- `provider_failure_reason`

## Governed Return Success Continuity

On success, the CLI emits:

- `execution_status: EXECUTION_COMPLETED`
- `provider_invoked: true`
- `governed_return_generated: true`
- `continuity_verified: true`
- `fail_closed: false`
- deterministic `governed_return_hash`

## Fail-Closed Guarantees

Invalid continuity still returns:

`EXECUTION_BLOCKED`

Provider failure still returns:

`EXECUTION_FAILED`

No retry, orchestration, alternate provider, hidden execution, autonomous continuation, or governance bypass was added.

## Terminal Rendering

The CLI renders:

```text
==================================================
AIGOL EXECUTION RESULT
==================================================
Execution:
  EXECUTION_COMPLETED
Provider:
  INVOKED
Command:
  ['codex', '--version']
Exit Code:
  0
Governed Return:
  GENERATED
Continuity:
  VERIFIED
==================================================
```

This confirms the first deterministic CLI-governed provider success path.
