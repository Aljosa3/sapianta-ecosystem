# GOVERNED_RUNTIME_OPERATOR_CLI_V1

## Status

Certified.

This milestone adds the first practical local operator command for the governed runtime. It converts a human operator request into the same deterministic localhost preview request already accepted by the governed runtime and returns a concise replay-visible summary.

## Scope

- local-only target: `127.0.0.1`
- minimal `invoke` command
- optional `validate-response` command
- deterministic governed request construction
- concise governed response summary

## Guarantees

- deterministic operator payloads
- localhost-only target enforcement
- fail-closed handling for invalid artifacts, blocked responses, malformed responses, missing evidence, and unavailable runtime
- replay-visible response summaries

## Boundaries

No new runtime authority, orchestration, agents, retries, fallback routing, background workers, hidden memory, hidden continuation, dynamic provider selection, `shell=True`, or unrestricted subprocess execution are introduced.
