# LIVE_NATIVE_HOST_INSTRUMENTATION_V1

Status: implemented.

## Purpose

This milestone instruments the real Chrome Native Messaging host continuity
chain without adding architecture or changing execution topology.

The traced chain is:

```text
read_native_message()
-> handle_native_message()
-> run_minimal_end_to_end_bridge()
-> bounded Codex CLI provider
-> write_native_message()
```

## Continuity Stages

The native host now records deterministic stages:

```text
NATIVE_STAGE_READ_MESSAGE
NATIVE_STAGE_JSON_PARSED
NATIVE_STAGE_HANDLE_ENTERED
NATIVE_STAGE_RUNTIME_BRIDGE_ENTERED
NATIVE_STAGE_PROVIDER_ATTEMPT
NATIVE_STAGE_WRITE_RESPONSE
NATIVE_STAGE_RESPONSE_FLUSHED
```

These stages are stored in:

```text
diagnostic_evidence.native_bridge.stages
```

The latest reached stage is also stored as:

```text
diagnostic_evidence.native_bridge.stage_reached
diagnostic_evidence.native_bridge.last_successful_stage
diagnostic_evidence.native_bridge.failure_stage
```

## Trace Mode

When enabled:

```bash
AIGOL_NATIVE_TRACE=1
```

the native host writes stage markers to stderr only:

```text
[NATIVE_STAGE_READ_MESSAGE]
[NATIVE_STAGE_JSON_PARSED]
[NATIVE_STAGE_HANDLE_ENTERED]
...
```

stdout remains reserved for Chrome Native Messaging framing only.

## Stdout / Stderr Separation

Chrome Native Messaging stdout must contain only:

```text
[4-byte little-endian length][JSON payload]
```

No tracing, warnings, print output, traceback text, or debug logs are written to
stdout. Runtime stage tracing uses stderr. Structured diagnostics use JSON
response fields.

## Response Framing

`write_native_message()` records:

```text
NATIVE_STAGE_WRITE_RESPONSE
NATIVE_STAGE_RESPONSE_FLUSHED
response_written: true
response_flushed: true
```

before serializing the final JSON payload. If serialization or writing raises,
the host cannot truthfully emit a successful response, so fail-closed exception
handling remains in the native host main path.

## Real Runtime Observations

Automated local instrumentation proves:

- `read_native_message()` is reached;
- JSON parsing is reached for valid framed input;
- `handle_native_message()` is entered;
- runtime bridge entry is recorded;
- provider attempt stage is visible when the bridge reaches the provider;
- response write and flush stages are visible in structured diagnostics;
- stderr trace mode does not contaminate stdout;
- malformed requests fail closed with structured diagnostics.

## Exact Failing Stage

For malformed requests, the failure is:

```text
failure layer: native_message_validation
provider_invoked: false
```

For runtime bridge exceptions, the failure stage is the last reached runtime
stage, such as:

```text
NATIVE_STAGE_RUNTIME_BRIDGE_ENTERED
```

For successful mocked provider invocation, the stage chain reaches:

```text
NATIVE_STAGE_PROVIDER_ATTEMPT
NATIVE_STAGE_WRITE_RESPONSE
NATIVE_STAGE_RESPONSE_FLUSHED
```

## Boundary Preservation

This milestone does not add:

- governance layers;
- preview layers;
- retries;
- orchestration;
- fallback providers;
- autonomous continuation;
- execution topology changes;
- fake provider success.

Fail-closed behavior remains intact.
