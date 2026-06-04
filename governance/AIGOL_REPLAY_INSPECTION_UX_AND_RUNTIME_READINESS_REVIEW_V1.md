# AIGOL_REPLAY_INSPECTION_UX_AND_RUNTIME_READINESS_V1

## Status

Review-only readiness assessment.

No runtime mutation, implementation change, authority change, governance model
change, or OCS transition is authorized by this artifact.

`AIGOL_REPLAY_INSPECTION_UX_AND_RUNTIME_READINESS_STATUS = NOT_READY_FOR_OCS_TRANSITION`

## Reviewed Surfaces

Reviewed:

- `aigol/cli/commands/chain_inspection.py`;
- `aigol/runtime/unified_replay_reconstruction_runtime.py`;
- `aigol/cli/aigol_cli.py`;
- `tests/test_cli_chain_inspection_runtime_v1.py`;
- `tests/test_unified_replay_reconstruction_runtime_v1.py`;
- `governance/CLI_CHAIN_INSPECTION_RUNTIME_V1.md`;
- `governance/UNIFIED_REPLAY_RECONSTRUCTION_RUNTIME_V1.md`.

## Readiness Finding

The chain inspection runtime is source-replay read-only, but it is not
operator-read-only in the normal CLI sense. `show-latest-chain` invokes unified
replay reconstruction with a deterministic report directory and the
reconstruction runtime writes append-only report artifacts into that directory.

Repeated invocation with the same command, `created_at`, and report root reuses
the same report directory. The second invocation fails before reconstruction
because append-only report artifacts already exist.

This behavior is deterministic, but it is not suitable for a governance
transparency command before OCS transition.

## Determinations

### Should show-latest-chain be strictly read-only?

Yes, by default. An operator command named `show-latest-chain` should not fail
because it previously showed the same chain. It should be pure inspection unless
the operator explicitly requests persisted inspection evidence.

### Should chain inspection create runtime artifacts at all?

Not by default. Persisted inspection reports are useful as audit evidence, but
they should be optional and clearly named as evidence creation, not hidden inside
a `show-*` command.

### If runtime artifacts are required, should they be ephemeral?

For default operator inspection, yes. A pure inspection path should return a
deterministic in-memory report without append-only writes. If persisted evidence
is required, it should use either an explicit `--persist-report` mode or a
unique invocation id/report id so repeated inspection is idempotent from the
operator perspective.

### Why does repeated execution fail closed?

`chain_inspection._report_dir` derives a deterministic report directory from:

- command name;
- canonical chain id or `LATEST`;
- `created_at`.

`unified_replay_reconstruction_runtime._ensure_report_replay_available` then
checks for:

- `000_unified_replay_reconstruction_recorded.json`;
- `001_unified_replay_reconstruction_returned.json`.

If those files already exist, it raises:

`append-only runtime artifact already exists: 000_unified_replay_reconstruction_recorded.json`

### Is the failure implementation or architectural design?

Both, but primarily architectural. The implementation behaves as designed for
append-only report persistence. The architectural problem is that a read-style
operator command is coupled to mandatory append-only report creation.

### Does current behavior violate replay inspection expectations?

Yes. It does not mutate source replay, but it violates the expected UX contract
of repeatable inspection. A read-only transparency command should be safe to run
multiple times without requiring a new timestamp or manual report-root cleanup.

### What operator UX improvements are required before OCS?

Required UX improvements:

- make default `show-*` commands repeatable;
- distinguish source replay from inspection report evidence;
- show whether a command persisted evidence;
- provide stable failure classes for missing root, missing chain, corrupted
  replay, ambiguous latest chain, and report artifact collision;
- offer explicit commands or flags for persisted reports.

### What runtime changes are required before OCS?

Required runtime changes:

- split pure reconstruction from persisted reconstruction;
- make report persistence optional;
- make repeated persisted inspection idempotent or uniquely identified;
- prevent report artifacts from being scanned as source evidence;
- add regression coverage for repeated `show-latest-chain` invocation.

## OCS Readiness Impact

The current runtime should not be used as an OCS transparency surface without
remediation. OCS operator trust depends on repeatable inspection commands that
do not surprise the operator with append-only artifact collisions.

## Final Classification

AIGOL_REPLAY_INSPECTION_UX_AND_RUNTIME_READINESS_STATUS = NOT_READY_FOR_OCS_TRANSITION
