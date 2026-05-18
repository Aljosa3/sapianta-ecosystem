# GOVERNED_LOCAL_PREVIEW_RUNTIME_V1

## Status

Certified.

This milestone exposes the existing governed runtime chain through the first minimal localhost operational surface. It adds local proving access only; it does not add orchestration, autonomous behavior, or a broader network runtime.

## Scope

- localhost-only binding: `127.0.0.1`
- synchronous `POST /governed-invoke`
- deterministic JSON request and response envelopes
- bounded runtime lifecycle and deterministic closure

## Guarantees

- deterministic localhost invocation handling
- replay-visible governed response return
- deterministic response identity
- localhost-only binding enforcement
- fail-closed rejection of malformed payloads, replay mismatch, hidden continuation, hidden routing, invalid lineage, and invalid execution surfaces

## Boundaries

No agents, orchestration, retries, fallback routing, websocket infrastructure, distributed coordination, hidden mutable state, hidden memory, autonomous continuation, `shell=True`, unrestricted subprocess execution, or background autonomous workers are introduced.
