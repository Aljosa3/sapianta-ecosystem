# EXTENSION_ORIGIN_NORMALIZATION_FIX_V1

## Purpose

This small stabilization fixes deterministic Chrome extension ID normalization for Native Messaging registration validation.

It changes only:

- extension ID normalization;
- expected `chrome-extension://.../` origin generation;
- `allowed_origins` comparison continuity.

It does not change execution topology, governance semantics, provider routing, retries, orchestration, or Native Messaging security boundaries.

## Root Cause

The workstation manifest already contained:

`chrome-extension://lolmjcbfjfoheleiohkjimoeioqagkcc/`

but validation reported:

- `extension_id_valid: false`
- `expected_allowed_origin: ""`

The validator was too narrow and rejected the installed Chrome extension ID before constructing the expected origin.

## Fix

The validator now normalizes extension input by:

- trimming whitespace;
- lowercasing;
- accepting either the bare extension ID or a full `chrome-extension://<id>/` origin;
- extracting the normalized extension ID before validation;
- generating `chrome-extension://lolmjcbfjfoheleiohkjimoeioqagkcc/` deterministically.

Malformed or empty IDs still fail closed.

## Expected Result

For:

`lolmjcbfjfoheleiohkjimoeioqagkcc`

the validator produces:

`chrome-extension://lolmjcbfjfoheleiohkjimoeioqagkcc/`

and can reach:

- `extension_id_valid: true`
- `native_host_allowed_origin_match: true`
- `native_host_registration_valid: true`
- `native_host_launch_ready: true`
- `chrome_runtime_launch_allowed: true`

when the manifest and executable continuity checks are otherwise valid.
