# AIGOL_REPLAY_INSPECTION_EXISTING_COMPONENTS_V1

## Status

Review-only existing components inventory.

## Chain Inspection CLI

`aigol/cli/commands/chain_inspection.py` provides operator commands:

- `show-latest-chain`;
- `show-chain`;
- `show-execution-lifecycle`;
- `show-learning-lifecycle`;
- `show-full-lineage`;
- `show-chain-summary`.

Reusable properties:

- common rendering;
- fail-closed operator result wrapper;
- authority flags;
- source replay read-only summary fields.

## Unified Replay Reconstruction Runtime

`aigol/runtime/unified_replay_reconstruction_runtime.py` performs canonical
chain reconstruction from replay-visible JSON wrappers.

Reusable properties:

- wrapper hash validation;
- artifact hash validation;
- chain id selection;
- reference continuity checks;
- failure reports;
- reconstruction report model.

## Existing Governance Artifacts

`CLI_CHAIN_INSPECTION_RUNTIME_V1.md` already documents that source replay is not
mutated and that reconstruction report events are written to the report
directory.

`UNIFIED_REPLAY_RECONSTRUCTION_RUNTIME_V1.md` similarly documents append-only
report persistence.

## Existing Tests

Existing tests validate:

- supported inspection commands;
- fail-closed display;
- source replay immutability;
- no execution authority imports;
- persisted report reconstruction.

Missing tests:

- repeated `show-latest-chain` with same arguments;
- repeated persisted report behavior;
- pure inspection without report writes;
- operator-facing report collision explanation.

## Reusable Conclusion

The reconstruction substrate is useful and should be reused. The mandatory
report persistence behavior should not remain coupled to default `show-*`
operator commands.
