# Execution Runtime Replay Model V1

Status: runtime replay model for minimal execution prototype.

## Purpose

This artifact defines the replay model for `MINIMAL_EXECUTION_RUNTIME_PROTOTYPE_V1`.

## Replay Chain

The replay chain is deterministic and append-only:

```text
request
validation
authorization
outcome
termination
```

Each replay artifact contains:

- replay index
- replay step
- artifact
- replay hash

Each inner artifact contains its own artifact hash.

## Replay Reconstruction

Replay reconstruction verifies:

- all expected replay artifacts exist
- replay ordering is correct
- replay wrapper hashes are valid
- inner artifact hashes are valid
- lifecycle states are valid
- terminal state is explicit

## Replay Failure Semantics

Replay reconstruction fails closed on:

- missing replay artifact
- replay ordering mismatch
- replay hash mismatch
- artifact hash mismatch
- invalid terminal state
- invalid lifecycle ordering

## Replay Centrality

The runtime does not create a continuity source outside replay.

Replay remains the constitutional source of truth for execution lifecycle evidence.

