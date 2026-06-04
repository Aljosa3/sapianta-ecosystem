# AIGOL_REPLAY_INSPECTION_ROOT_CAUSE_ANALYSIS_V1

## Status

Review-only root cause analysis.

## Observed Failure

Command:

```text
python -m aigol.cli.aigol_cli show-latest-chain
```

Observed result:

```text
FAILED_CLOSED
failure_reason:
append-only runtime artifact already exists:
000_unified_replay_reconstruction_recorded.json
```

## Root Cause

The failure is caused by deterministic report directory reuse combined with
mandatory append-only report persistence.

The chain inspection command computes a report directory using:

- command name;
- chain identity or `LATEST`;
- `created_at`.

For default CLI invocation, `created_at` is stable unless the operator supplies
a different value. Therefore repeated `show-latest-chain` calls target the same
report directory.

Before reconstruction, unified replay reconstruction checks whether its report
step artifacts already exist. If they do, it fail-closes to preserve
append-only semantics.

## Architectural Cause

The architecture conflates two different operations:

- inspect replay and show the latest chain;
- persist a replay-visible reconstruction report.

Both are valuable, but they should not be the same default operation.

## Correctness Assessment

The append-only check is correct for a runtime that is creating durable report
artifacts.

The CLI behavior is incorrect for a repeatable read-style operator command.

## Replay Safety Assessment

Source replay safety is preserved. The command does not mutate inspected replay
evidence.

Operator inspection safety is incomplete because repeated inspection produces a
new failure state instead of a stable view.

## OCS Risk

If carried into OCS unchanged, this behavior would make the primary transparency
surface appear brittle. Operators would need to understand internal report-root
identity and append-only filenames to recover from an ordinary repeated view
command.
