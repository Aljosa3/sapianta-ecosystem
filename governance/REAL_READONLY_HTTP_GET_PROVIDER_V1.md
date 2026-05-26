# REAL_READONLY_HTTP_GET_PROVIDER_V1

## Scope

This milestone introduces the first bounded outbound HTTP execution provider for AiGOL.

The provider exposes only:

- `fetch(url, max_bytes, timeout_seconds)`

## Guarantees

- GET-only outbound access.
- HTTPS-only transport validation.
- Explicit hostname allowlist enforcement.
- Redirect rejection.
- Bounded response size.
- Timeout enforcement.
- Deterministic replay-visible request evidence.
- Fail-closed transport validation.

## Non-Goals

- POST, PUT, PATCH, or DELETE.
- Authentication flows.
- Cookies or session persistence.
- Streaming.
- Websocket support.
- Retries.
- Async orchestration.
- Concurrent execution.
- Crawling.
- Scraping frameworks.
- Browser automation.
- Cloud mutation.
- Shell or subprocess usage.

## Evidence Shape

Every request returns deterministic structured evidence with:

- operation;
- requested URL;
- normalized URL;
- hostname;
- allowlisted flag;
- status;
- HTTP status;
- bytes received;
- timeout seconds;
- content hash;
- evidence hash;
- reason.

Blocked requests return deterministic failure evidence.

## Boundary

This provider is not a general networking layer, orchestration system, agent runtime, queue, workflow engine, distributed abstraction, crawler, or scraping framework.

## Certification

`REAL_READONLY_HTTP_GET_PROVIDER_V1` certifies bounded read-only HTTP GET access with replay-visible evidence and fail-closed validation.
