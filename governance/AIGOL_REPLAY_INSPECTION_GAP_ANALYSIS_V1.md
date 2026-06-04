# AIGOL_REPLAY_INSPECTION_GAP_ANALYSIS_V1

## Status

Review-only gap analysis.

## Gap 1: Mandatory Report Persistence

Current behavior:

- every chain inspection command calls reconstruction with a report directory;
- reconstruction always persists report replay artifacts.

Required capability:

- pure read-only reconstruction mode;
- optional persisted report mode;
- explicit operator visibility when persistence occurs.

## Gap 2: Non-Repeatable show-latest-chain

Current behavior:

- report directory identity is deterministic for command, `LATEST`, and
  `created_at`;
- repeated invocation with the same inputs collides with append-only report
  files.

Required capability:

- repeated `show-latest-chain` must succeed by default;
- persisted mode must be idempotent or use a unique invocation id.

## Gap 3: Read-Only Semantics Are Ambiguous

Current behavior:

- result says `read_only: True`;
- source replay is not mutated;
- report artifacts are still created.

Required capability:

- separate `source_replay_read_only` from `inspection_report_persisted`;
- avoid claiming simple read-only when filesystem artifacts were written.

## Gap 4: Operator Failure Message Is Too Low-Level

Current behavior:

- operator sees append-only internal filename collision.

Required capability:

- human-facing collision message that explains repeated inspection and suggests
  a new report id, pure mode, or report-root selection.

## Gap 5: Report Artifacts And Source Evidence Are Entangled

Current behavior:

- reconstruction excludes the current report directory from scanning, but report
  roots can still sit near inspected replay roots.

Required capability:

- explicit report-root isolation;
- pure mode that creates no report artifacts;
- tests proving reports are not treated as source replay.

## Gap 6: OCS Transparency Contract Missing

Current behavior:

- inspection behavior is certified as source-replay read-only, not as
  repeatable operator transparency.

Required capability:

- OCS inspection contract covering repeatability, persistence mode, report
  identity, diagnostics, and operator display.
