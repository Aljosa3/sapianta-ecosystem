# IMPLEMENTATION_PLAN_INSPECTION_COMMAND_GROUP_V1

## Status

Certified implementation plan inspection command group.

## Purpose

Provide a read-only AiGOL CLI surface for inspecting replay-visible implementation plan artifacts.

This closes the operator visibility gap for:

```text
IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1
```

## Commands

Implemented commands:

```text
plan list
plan show <PLAN_ID>
plan approved
plan chain <CHAIN_ID>
plan bridge <BRIDGE_ID>
plan execution-request <EXECUTION_REQUEST_ID>
plan latest
```

Each command supports:

```text
--replay-root
--json
```

## Runtime Surface

Implemented in:

```text
aigol/cli/commands/plan.py
```

Wired through:

```text
aigol/cli/aigol_cli.py
```

## Inspection Scope

The command group reconstructs implementation plan visibility from replay evidence:

- implementation plan artifacts;
- bridge link artifacts;
- implementation-plan-derived execution request artifacts.

It exposes:

- implementation plan id;
- canonical chain id;
- governed approval references;
- bridge id where present;
- execution request id where present;
- plan status;
- plan source;
- planned targets;
- planned validation;
- replay and artifact references.

## Replay And Hash Guarantees

The command group validates:

- replay wrapper hashes;
- artifact hashes;
- plan text hashes;
- plan scope hashes;
- plan constraint hashes;
- planned artifact target hashes;
- planned validation hashes.

Corrupt or invalid relevant replay evidence fails closed before display.

## Boundary Guarantees

The command group is read-only.

It does not:

- dispatch;
- invoke;
- execute;
- mutate governance;
- mutate replay;
- create execution requests;
- bypass approval runtimes;
- bypass bridge runtimes.

## Chain Continuity

The command group preserves canonical chain visibility through `canonical_chain_id` and supports direct chain-based filtering.

Bridge and execution request filters preserve continuity by resolving the implementation plan associated with the bridge or execution request evidence.

## Human-Readable Output

Human-readable summaries are deterministic and include:

- status;
- replay root;
- filter values;
- plan count;
- read-only authority flags;
- fail-closed status;
- plan summary rows.

## Final Classification

```text
IMPLEMENTATION_PLAN_INSPECTION_COMMAND_GROUP_STATUS = CERTIFIED
```
