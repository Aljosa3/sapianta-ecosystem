# NATIVE_MESSAGING_RESPONSE_CONTINUITY_FIX_V1

Status: implemented.

## Purpose

This stabilization fixes the low-level IPC continuity path:

```text
handle_native_message()
-> write_native_message()
-> service_worker response normalization
-> sidepanel execution result
```

## Root Cause

The Native Messaging response path exposed flat diagnostic fields only. The
service worker and sidepanel could therefore receive a failure state while the
operator-visible diagnostic buckets appeared empty:

```text
diagnostic_evidence: {"native_bridge":{},"provider":{},"service_worker":{}}
```

The host also did not catch unexpected exceptions around
`handle_native_message()`, so an exception could terminate the host before one
structured framed JSON response was written to stdout.

## Exact Failing Layer

The failing layer was the response continuity seam:

```text
Native Messaging host structured response
-> service_worker diagnostic normalization
-> sidepanel diagnostic rendering
```

## Stdout Purity Requirement

Chrome Native Messaging requires stdout to contain only:

```text
4-byte little-endian JSON length
JSON payload bytes
```

No `print()`, warning text, traceback text, or debug logging may be written to
stdout. Diagnostics must be carried in structured JSON fields or stderr.

## Response Framing Model

`write_native_message()` writes exactly one length-prefixed JSON object using
canonical JSON options:

```text
sort_keys=True
separators=(",", ":")
```

Non-native JSON objects are stringified rather than allowing serialization to
break the framed response.

## Diagnostic Evidence Model

Native responses now include:

```text
diagnostic_evidence.native_bridge
diagnostic_evidence.provider
```

Flat compatibility fields remain present:

```text
diagnostic_evidence.python_runtime_bridge_called
diagnostic_evidence.provider_invoked
diagnostic_evidence.subprocess_invoked
diagnostic_evidence.response_serialization_ready
```

The service worker preserves nested diagnostics, and the sidepanel renders
service-worker, native-bridge, and provider diagnostics in the controlled
execution handoff result.

## Fix Applied

- Added structured `NATIVE_BRIDGE_ERROR` responses for unexpected host
  exceptions.
- Wrapped native host main handling so handled requests produce one framed
  response instead of an uncaught traceback.
- Added nested native/provider diagnostic evidence.
- Extended service worker validation to accept structured native error
  responses.
- Preserved nested diagnostics into sidepanel result summaries.

## Boundary Preservation

This does not add governance layers, preview layers, retries, orchestration,
fallback providers, autonomous continuation, or alternate execution paths.

Provider success is not faked. Provider failures remain visible and fail closed.
