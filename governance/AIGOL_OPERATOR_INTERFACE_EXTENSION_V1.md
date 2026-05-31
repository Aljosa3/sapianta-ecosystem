# AIGOL_OPERATOR_INTERFACE_EXTENSION_V1

## Status

`AIGOL_OPERATOR_INTERFACE_EXTENSION_STATUS = READY`

## Purpose

This milestone extends the existing AiGOL CLI surface. It does not create a new operator CLI framework.

The extension adds:

```text
python -m aigol.cli.aigol_cli run-governed \
  --worker filesystem \
  --operation create-file \
  --target test.txt
```

## Governed Flow

The command routes one operator request through the existing governed path:

```text
Human Request
↓
Provider
↓
Proposal
↓
Governed Authorization
↓
Authorized Worker Request
↓
Filesystem Worker
↓
Replay
```

## Runtime Reuse

The command reuses:

- `aigol.provider.provider_runtime`
- `aigol.authorization.authorization_runtime`
- `aigol.workers.filesystem_worker`
- existing replay reconstruction helpers

No new runtime framework, CLI framework, orchestration layer, planning layer, or autonomous behavior is introduced.

## Operator Output

The operator receives:

- proposal id
- authorization id
- worker id
- worker result
- replay id
- replay reference
- execution status
- fail-closed status

## Supported Scope

V1 supports only:

```text
worker = filesystem
operation = create-file
```

Unsupported workers and operations fail closed.

## Final Classification

```text
AIGOL_OPERATOR_INTERFACE_EXTENSION_STATUS = READY
```

