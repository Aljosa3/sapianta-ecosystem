# COGNITION_OBSERVABILITY_V1

Status: governed read-only observability milestone.

## Purpose

`COGNITION_OBSERVABILITY_V1` adds a deterministic CLI inspection command:

```bash
aigol cognition inspect
```

The command reads existing governed artifacts, creates a bounded cognition state envelope, and renders a deterministic cognition summary.

## CLI Behavior

Supported options:

- `--input <artifact_or_directory>` reads existing JSON or JSONL artifacts.
- `--json` prints structured JSON output.
- `--output <path>` explicitly writes the generated envelope artifact.

The command performs no implicit persistence. Writing occurs only when `--output` is provided.

## Summary Sections

The human-readable summary shows:

1. Semantic State
2. Admissibility State
3. Authority Matrix
4. Replay / Lineage State
5. Boundary State
6. Reflection / Advisory State
7. Allowed Next Transitions
8. Forbidden Transitions
9. Continuity Status

## Explicit Non-Authority Guarantees

The command does not:

- execute anything;
- authorize anything;
- dispatch anything;
- invoke Codex;
- invoke providers;
- mutate governance state;
- repair missing artifacts;
- infer hidden context;
- certify semantic truth;
- orchestrate;
- retry;
- continue autonomously.

## Fail-Closed UNKNOWN Handling

Malformed or missing evidence remains absent from the envelope and is surfaced as `UNKNOWN`.

The command does not guess missing state and does not hide missing lineage.

## Replay Visibility

The generated envelope is deterministic and replay-visible. It is an observability artifact, not an execution artifact.

## Boundary

This milestone consolidates cognition visibility.

It does not create cognition agency.
