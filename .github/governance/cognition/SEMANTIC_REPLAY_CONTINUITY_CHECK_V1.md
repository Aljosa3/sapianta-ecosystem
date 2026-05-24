# SEMANTIC_REPLAY_CONTINUITY_CHECK_V1

Status: governance cognition observability artifact.

Scope: read-only semantic replay continuity verification.

## Purpose

`SEMANTIC_REPLAY_CONTINUITY_CHECK_V1` verifies whether replay-visible semantic state remains structurally stable across governed lifecycle transitions.

It asks a bounded question:

Did semantic intent, authority boundaries, admissibility state, replay identity, lifecycle transitions, and ambiguity evidence remain governance-consistent across the provided artifacts?

## Non-Goals

This milestone does not implement:

- semantic truth certification
- autonomous reasoning
- orchestration
- autonomous continuation
- hidden cognition
- execution authority
- provider invocation
- mutation authority
- hidden context ingestion
- semantic correction
- replay repair

## Verification Model

The checker performs deterministic field-level continuity checks only:

- Intent Continuity
- Authority Continuity
- Admissibility Continuity
- Replay Identity Continuity
- Boundary Transition Continuity
- Ambiguity Continuity

It does not call an LLM, infer hidden meaning, score semantic truth, repair lineage, or rewrite evidence.

## Continuity Statuses

Allowed statuses are:

- `VERIFIED_STABLE`
- `VERIFIED_WITH_WARNINGS`
- `UNKNOWN_INSUFFICIENT_EVIDENCE`
- `DRIFT_DETECTED`
- `AUTHORITY_DRIFT_DETECTED`
- `REPLAY_DISCONTINUITY`
- `INVALID_TRANSITION_CHAIN`

The checker fails closed. Missing evidence becomes `UNKNOWN`, not guessed meaning.

## Governance Guarantees

The checker hard-codes and reports:

- `execution_authority = false`
- `orchestration_authority = false`
- `mutation_authority = false`
- `autonomous_continuation = false`

It never executes tasks, dispatches providers, mutates artifacts, repairs continuity, rewrites lineage, infers hidden context, or generates autonomous plans.

## Replay-Visible Behavior

The output artifact includes:

- continuity status
- semantic drift level
- authority drift state
- ambiguity growth state
- continuity confidence
- check results
- evidence references
- forbidden findings
- unknown areas
- governance boundary integrity
- deterministic `semantic_replay_check_hash`

The hash is computed from canonical JSON with sorted keys and deterministic separators.

## CLI Observability

The CLI command is:

```bash
aigol cognition continuity-check --input <artifact_or_directory>
```

Optional flags:

- `--json`
- `--output <path>`

Writing output is explicit only. The command remains read-only with respect to governed runtime, provider execution, replay repair, and governance state.
