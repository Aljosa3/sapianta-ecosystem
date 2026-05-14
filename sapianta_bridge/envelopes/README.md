# Execution Envelope Model v1

This package defines the first canonical bounded execution transport model for AiGOL.

Execution envelopes are bounded authority transport contracts between governance and execution providers. They are not orchestration systems.

## Bounded Execution Philosophy

Execution providers must never receive unconstrained authority, unrestricted prompts, undefined execution scope, or implicit permissions.

Providers receive only deterministic, replay-safe, authority-bounded execution envelopes.

## Envelope Semantics

An envelope binds:

- provider identity;
- workspace scope;
- authority scope;
- allowed and forbidden actions;
- timeout;
- replay identity;
- validation requirements;
- constraints;
- replay binding hash.

## Authority Scope

Authority must be explicit. Undefined authority fails closed.

Supported authority scopes include:

- `READ_ONLY`
- `PATCH_EXISTING_FILES`
- `CREATE_NEW_FILES`
- `RUN_TESTS`
- `NO_NETWORK`
- `NO_RUNTIME_EXECUTION`
- `NO_PRIVILEGE_ESCALATION`

## Workspace Scope

Workspace scope defines allowed roots, forbidden roots, and generated artifact roots. Providers cannot escape scope or self-expand workspace authority.

## Replay-Safe Transport

Replay binding hashes provider identity, authority scope, workspace scope, replay identity, and validation requirements. The same envelope yields the same authority semantics.

## Provider Independence

Envelope semantics are provider-independent. Codex, Claude, local executors, and deterministic executors must interpret the same authority and workspace semantics.

## Non-Goals

This package does not implement runtime routing, orchestration, retries, fallback logic, real provider calls, scheduling, adaptive optimization, or autonomous task execution.
