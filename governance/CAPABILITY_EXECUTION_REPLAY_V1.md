# Capability Execution Replay V1

Status: capability replay model.

## Replay Chain

The read-only capability replay chain is:

```text
request
validation
authorization
execution
termination
```

Each replay artifact contains:

- replay index
- replay step
- artifact
- replay hash

Each inner artifact contains an artifact hash.

## Replay Evidence

Execution evidence includes:

- execution identifier
- capability identifier
- authorization hash
- provider evidence hash
- read-only confirmation
- mutation flags set to false

## Reconstruction

Replay reconstruction verifies:

- all expected artifacts exist
- replay ordering is correct
- wrapper hashes are valid
- inner artifact hashes are valid
- lifecycle states are valid
- terminal state is explicit

## Fail-Closed Replay Conditions

Replay reconstruction fails closed on:

- missing replay artifact
- replay ordering mismatch
- replay hash mismatch
- artifact hash mismatch
- invalid lifecycle ordering
- invalid terminal status

