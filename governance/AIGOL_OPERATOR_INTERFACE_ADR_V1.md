# AIGOL_OPERATOR_INTERFACE_ADR_V1

## Decision

Do not create a duplicate operator CLI architecture.

Classify the operator interface state as:

```text
AIGOL_OPERATOR_INTERFACE_STATUS = READY_FOR_EXTENSION
```

## Context

AiGOL already contains several operator-facing surfaces:

- canonical governance CLI;
- runtime execution CLI;
- runtime summary CLI;
- live read-only operator CLI;
- replay summary and replay verification helpers;
- programmatic provider, authorization, filesystem worker, and GitHub worker paths.

The newest domain-worker path is certified but not operator-facing.

## Rationale

Creating a new standalone CLI would duplicate existing status, replay, runtime summary, governance validation, and read-only operation commands.

The missing capability is a narrow command surface for the latest governed operation stack, not a new CLI foundation.

## Consequences

Future implementation should extend an existing CLI and reuse existing runtime APIs.

The extension must remain:

- replay-visible;
- fail-closed;
- non-orchestrating;
- non-autonomous;
- provider/worker boundary preserving.

## Non-Goals

This ADR does not implement new CLI commands, runtime flows, provider calls, worker calls, authorization changes, replay changes, or governance activation.

