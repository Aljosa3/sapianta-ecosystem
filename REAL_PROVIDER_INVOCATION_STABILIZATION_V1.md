# REAL_PROVIDER_INVOCATION_STABILIZATION_V1

Status: implemented.

## Purpose

This stabilization verifies that the real governed execution path reaches the
bounded Codex CLI provider invocation point.

The path remains:

```text
sidepanel
-> service_worker
-> Native Messaging host
-> Python runtime bridge
-> bounded Codex CLI provider
-> subprocess.run(["codex", "exec", ...])
```

## Root Cause

Two operational continuity gaps were present:

1. The Native Messaging host script was not executable on disk, which can block
   Chrome from launching the host as a real Native Messaging executable.
2. Provider diagnostics did not explicitly report whether the `codex`
   executable was discoverable before subprocess invocation.

The prior bootstrap issue was already diagnosed separately:

```text
agol_bridge/native/native_messaging_host.py
```

needed to add the repository root to `sys.path` before importing
`agol_bridge.*` when launched by direct script path.

## Exact Fix

- Marked `agol_bridge/native/native_messaging_host.py` executable for real
  Native Messaging launch.
- Added `codex_executable` and `codex_executable_found` fields to bounded
  provider diagnostic evidence.
- Propagated provider/native/service-worker diagnostic evidence into the
  controlled handoff cockpit summary.

No provider abstraction, fallback provider, retry loop, orchestration layer, or
new governance layer was introduced.

## Codex Executable Detection

On this machine, `codex` was found at:

```text
/home/pisarna/.vscode/extensions/openai.chatgpt-26.519.32039-linux-x64/bin/linux-x86_64/codex
```

Runtime provider evidence now records whether this executable is found in the
environment used by the Native Messaging host.

## Provider Invocation

Provider invocation is considered reached when:

```text
codex_cli_result.provider_invoked == true
provider_result.diagnostic_evidence.provider_invoked == true
provider_result.diagnostic_evidence.subprocess_invoked == true
```

If `codex` succeeds, the controlled handoff reports:

```text
execution_status: EXECUTION_COMPLETED
provider_invoked: true
```

If `codex` is missing or fails, the controlled handoff reports:

```text
execution_status: EXECUTION_FAILED
provider_invoked: true
```

That distinction proves the provider boundary was reached while preserving
fail-closed execution semantics.

## Boundary Preservation

This stabilization does not add:

- retries;
- orchestration;
- autonomous continuation;
- background workers;
- fallback providers;
- provider routing;
- hardcoded success;
- governance bypasses.

Invalid continuity still blocks before provider invocation.
