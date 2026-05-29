# Filesystem Capability Replay V1

Status: filesystem capability replay model.

## Replay Chain

The filesystem read-only capability replay chain is:

```text
request
validation
authorization
execution
termination
```

## Replay Evidence

Replay evidence preserves:

- execution identifier
- capability identifier
- requested path
- allowed paths
- validation hash
- authorization hash
- execution evidence hash
- final status

## Execution Evidence

Execution evidence may include:

- path
- file or directory classification
- size metadata
- directory entry names
- bounded file text preview

Execution evidence must also certify:

- read-only
- no write
- no delete
- no move
- no execute
- no network
- no shell
- no API

## Replay Failure Semantics

Replay reconstruction fails closed on:

- missing replay artifact
- replay ordering mismatch
- replay hash mismatch
- artifact hash mismatch
- lifecycle corruption

