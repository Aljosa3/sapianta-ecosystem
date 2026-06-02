# CLI_CHAIN_INSPECTION_RUNTIME_V1

## Status

Certified operator-facing runtime.

## Purpose

This runtime exposes unified replay reconstruction through AiGOL CLI chain inspection commands.

It uses:

```text
UNIFIED_REPLAY_RECONSTRUCTION_RUNTIME_V1
```

as the authoritative reconstruction source.

## Commands

Supported operator commands:

```text
show-latest-chain
show-chain <CHAIN_ID>
show-execution-lifecycle <CHAIN_ID>
show-learning-lifecycle <CHAIN_ID>
show-full-lineage <CHAIN_ID>
show-chain-summary <CHAIN_ID>
```

Each command supports:

```text
--replay-root
--report-root
--created-at
--json
```

## Runtime Implementation

The command adapter is implemented in:

```text
aigol/cli/commands/chain_inspection.py
```

The CLI parser and renderer are wired in:

```text
aigol/cli/aigol_cli.py
```

## Operator Semantics

The CLI displays:

- reconstruction status;
- canonical chain id;
- reconstruction scope;
- report id;
- replay root;
- report directory;
- conversation presence;
- source routing presence;
- execution lifecycle artifact count;
- governed learning lifecycle artifact count;
- bridge artifact count;
- worker evidence artifact count;
- replay evidence artifact count;
- fail-closed failure reason.

## Boundary Guarantees

The CLI chain inspection runtime is read-only with respect to source replay and governed state.

It does not:

- create execution requests;
- dispatch workers;
- invoke workers;
- start execution;
- mutate source replay;
- mutate governance;
- mutate execution state;
- mutate learning state;
- repair corrupt replay evidence.

The only writes performed by the underlying reconstruction runtime are append-only reconstruction report events in the caller-provided report directory.

## Fail-Closed Display

If unified reconstruction fails closed, the CLI returns and renders a fail-closed operator summary instead of exposing an unhandled traceback.

The summary preserves:

```text
execution_requests_created = false
workers_dispatched = false
workers_invoked = false
```

## Authority Boundary

The runtime preserves:

```text
LLM proposes
AiGOL governs
Human authorizes
Worker executes
Replay records
```

Chain inspection adds operator visibility only. It grants no execution authority.

## Final Classification

```text
CLI_CHAIN_INSPECTION_RUNTIME_STATUS = CERTIFIED
```
