# GOVERNED_EXECUTION_CONNECTORS_V1

## Status

Certified.

This milestone introduces deterministic governed execution connectors for bounded execution surfaces. Connectors are governed adapters, not autonomous providers or routing engines.

## Connector Scope

- local execution connector
- Codex execution connector
- Claude Code execution connector
- deterministic filesystem connector
- bounded tool execution connector

## Guarantees

- deterministic registration identity
- static allowed-surface binding
- replay-visible handoff evidence
- deterministic result return
- fail-closed validation for unregistered, unauthorized, mismatched, or malformed connector flows

## Boundaries

No orchestration, retries, fallback routing, autonomous provider selection, hidden execution, hidden state, websocket infrastructure, background daemons, `shell=True`, unrestricted subprocess execution, or distributed coordination is introduced.
