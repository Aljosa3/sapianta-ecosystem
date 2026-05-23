# REAL_EXECUTION_FAILURE_DIAGNOSIS_V1

Status: diagnosed and stabilized.

## Observed Failure

The browser cockpit reported:

```text
service_worker_called: true
native_messaging_called: true
provider_invoked: false
execution_status: EXECUTION_FAILED
native response status: SERVICE_WORKER_NATIVE_BRIDGE_FAILED
```

This means the service worker attempted the Native Messaging boundary, but did
not receive a valid `NATIVE_BRIDGE_ACCEPTED` / `NATIVE_BRIDGE_REJECTED`
response from the host.

## Exact Failing Layer

Failing layer:

```text
Native Messaging host bootstrap
```

## Exact Failing Function

The failure occurred before `handle_native_message()` could run.

The failing import was at module load time in:

```text
agol_bridge/native/native_messaging_host.py
```

## Exact Failing Condition

Launching the native host as Chrome does, by direct script path, set Python's
initial import path to:

```text
agol_bridge/native
```

That path did not include the repository root, so this import failed:

```python
from agol_bridge.runtime.minimal_end_to_end_bridge import ...
```

The direct reproduction before stabilization was:

```text
python agol_bridge/native/native_messaging_host.py
ModuleNotFoundError: No module named 'agol_bridge'
```

## Failure Timing

The failure occurred:

- before provider invocation;
- before bounded Codex CLI subprocess execution;
- before Native Messaging response serialization;
- during Native Messaging host process bootstrap.

It did not occur inside the bounded Codex provider.

## Stabilization Applied

`agol_bridge/native/native_messaging_host.py` now inserts the repository root
into `sys.path` before importing `agol_bridge.*` modules.

This preserves the existing topology:

```text
sidepanel
-> service_worker
-> Native Messaging host
-> Python runtime bridge
-> bounded Codex CLI provider
```

No provider routing, retry, orchestration, background worker, autonomous
continuation, or new governance layer was added.

## Diagnostic Instrumentation Added

Deterministic diagnostic evidence was added to:

- service worker native bridge failure/return objects;
- Native Messaging host accepted/rejected responses;
- bounded Codex CLI provider results.

The diagnostic evidence identifies:

- failing layer;
- failing function;
- failing condition;
- whether Python runtime bridge was called;
- whether provider invocation was reached;
- whether subprocess invocation was reached;
- whether response serialization was ready.

## Fail-Closed Preservation

Malformed Native Messaging requests still return `NATIVE_BRIDGE_REJECTED`.
Provider validation failures still return `REJECTED`.
Subprocess failures still return `FAILED`.
Timeouts still return `TIMEOUT`.
No successful execution is hardcoded or simulated in runtime code.

## Current Continuity Meaning

After this stabilization, if the service worker still reports
`SERVICE_WORKER_NATIVE_BRIDGE_FAILED`, the diagnostic evidence distinguishes
host lookup/permission/response handling failures from Python bridge/provider
failures.

If the native host returns successfully but `provider_invoked: false`, the
failure is now expected to be visible inside either:

- native response diagnostic evidence;
- bridge result diagnostic evidence;
- bounded Codex provider diagnostic evidence.
