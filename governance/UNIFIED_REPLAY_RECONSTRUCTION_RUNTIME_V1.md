# UNIFIED_REPLAY_RECONSTRUCTION_RUNTIME_V1

## Status

Certified runtime implementation.

## Purpose

This runtime implements deterministic, read-only replay reconstruction for AiGOL canonical chains.

It produces:

```text
UNIFIED_REPLAY_RECONSTRUCTION_REPORT_V1
```

The report reconstructs replay-visible evidence across:

- conversation;
- source routing;
- execution lifecycle;
- governed learning lifecycle;
- implementation-to-execution bridge;
- worker evidence;
- replay evidence.

## Runtime Surface

The runtime is implemented in:

```text
aigol/runtime/unified_replay_reconstruction_runtime.py
```

Supported reconstruction entrypoints:

```text
reconstruct_latest_chain
reconstruct_chain_by_id
reconstruct_execution_lifecycle
reconstruct_learning_lifecycle
reconstruct_full_lineage
reconstruct_unified_replay_reconstruction_report
```

## Reconstruction Inputs

The runtime reconstructs from replay-visible JSON wrapper artifacts under an explicit replay root.

It uses:

- `canonical_chain_id`;
- replay wrapper hashes;
- artifact hashes;
- runtime artifacts;
- worker evidence;
- bridge evidence;
- replay evidence.

Compatibility evidence without canonical chain identity is not written back as canonical identity.

## Fail-Closed Semantics

The runtime fails closed on:

- missing evidence;
- replay hash mismatch;
- artifact hash mismatch;
- invalid chain references;
- invalid hash continuity;
- ambiguous chain selection;
- multiple chain ownership.

Failed reconstruction attempts persist their own replay-visible failed report before raising a fail-closed runtime error.

## Mutation Boundary

The runtime does not:

- modify replay evidence under reconstruction;
- modify governance artifacts;
- modify execution state;
- modify learning state;
- create execution requests;
- dispatch workers;
- invoke workers;
- repair corrupt evidence.

It only writes append-only reconstruction report events to the caller-provided report directory.

## Authority Boundary

The runtime preserves:

```text
LLM proposes
AiGOL governs
Human authorizes
Worker executes
Replay records
```

Replay reconstruction is inspection-only. It does not create authority and does not infer missing authorization.

## Final Classification

```text
UNIFIED_REPLAY_RECONSTRUCTION_RUNTIME_STATUS = CERTIFIED
```
