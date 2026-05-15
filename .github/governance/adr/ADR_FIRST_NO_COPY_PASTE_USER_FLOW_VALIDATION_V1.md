# ADR: FIRST_NO_COPY_PASTE_USER_FLOW_VALIDATION_V1

## Status

Accepted.

## Decision

Add one operational proof harness that validates a single local ingress artifact, executes exactly one human-approved bounded Codex invocation, captures one bounded result, and exports one deterministic egress artifact without manual prompt relay.

## Boundary

This is validation only. It adds no orchestration, retries, routing, daemons, async runtime, memory, polling, watchers, APIs, or broader execution authority.
