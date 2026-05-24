# COGNITION_AUTHORITY_PROPAGATION_VERIFIER_V1

Status: read-only authority continuity and propagation verifier.

Scope: deterministic authority boundary verification across cognition artifacts.

## Purpose

`COGNITION_AUTHORITY_PROPAGATION_VERIFIER_V1` checks whether authority boundaries remain stable across replay-visible cognition lifecycle artifacts.

It verifies:

- ChatGPT semantic input never gains authority.
- Human approval does not equal dispatch authorization.
- Dispatch authorization does not equal execution.
- Reflection never gains execution authority.
- Registry, topology, lifecycle, and integrity reports never gain runtime authority.
- Provider authority exists only at the bounded execution boundary.
- Mutation authority remains false.
- Autonomous continuation remains false.
- Unknown evidence becomes `UNKNOWN`, not guessed.
- Unexpected authority escalation is reported as `AUTHORITY_PROPAGATION_RISK` or `HIDDEN_AUTHORITY_ESCALATION`.

## Statuses

Supported statuses:

- `AUTHORITY_STABLE`
- `AUTHORITY_STABLE_WITH_WARNINGS`
- `UNKNOWN_INSUFFICIENT_EVIDENCE`
- `AUTHORITY_PROPAGATION_RISK`
- `HIDDEN_AUTHORITY_ESCALATION`
- `INVALID_AUTHORITY_CHAIN`

## Non-Goals

This verifier does not create:

- execution authority
- orchestration
- autonomous cognition
- planning
- semantic reasoning
- runtime activation
- provider routing
- hidden inference
- authority issuance
- authority repair
- mutation authority

## CLI Observability

The CLI command is:

```bash
aigol cognition authority
```

Optional flags:

- `--input <artifact_or_directory>`
- `--json`
- `--output <path>`
- `--validate`

Writing output is explicit only.

## Governance Guarantees

The verifier is:

- read-only
- deterministic
- replay-visible
- governance-safe
- fail-closed for unknown evidence

It never executes, dispatches, activates providers, mutates artifacts, repairs authority, infers hidden context, or issues authority.
