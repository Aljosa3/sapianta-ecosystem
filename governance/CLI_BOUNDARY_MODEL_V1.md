# CLI Boundary Model V1

Status: CLI boundary classification only.

## Purpose

This artifact classifies command-line interaction surfaces for future governed execution implementations. It does not implement shell runtime or command execution.

## CLI Capability Classification

### READ-ONLY

State: `RESTRICTED`.

Read-only CLI interaction may be considered only under explicit authorization, deterministic command scope, replay-visible output capture, and no mutation side effects.

Read-only CLI is not automatically allowed.

### MUTATING

State: `DENIED`.

Mutating CLI interaction is denied because it can modify files, runtime state, governance artifacts, replay evidence, environment configuration, or process state.

### PRIVILEGED

State: `DENIED`.

Privileged CLI interaction is denied because it can bypass constitutional isolation and mutate authority boundaries.

## CLI Fail-Closed Conditions

CLI interaction must fail closed on:

- ambiguous command semantics
- mutation possibility
- privilege escalation
- shell expansion ambiguity
- hidden state persistence
- missing replay output capture
- authorization mismatch

## Boundary Rule

No CLI capability may bypass authorization, replay visibility, bounded scope, or constitutional isolation.

