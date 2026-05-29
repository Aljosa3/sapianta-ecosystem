# Replay-Visible Cognition Execution Bridge V1

Status: bridge replay model.

## Replay Chain

The bridge replay chain is:

```text
contribution
normalized_request
validation
authorization
execution
return
```

## Replay Evidence

Replay evidence preserves:

- bridge identifier
- execution identifier
- target capability
- normalized request hash
- validation hash
- authorization hash
- capability result hash
- final governed return

## Capability Replay

The bridge preserves the nested capability replay result.

Capability execution remains independently replay-visible and append-only.

## Reconstruction

Bridge replay reconstruction fails closed on:

- missing artifact
- replay ordering mismatch
- replay hash mismatch
- artifact hash mismatch
- invalid lifecycle order

