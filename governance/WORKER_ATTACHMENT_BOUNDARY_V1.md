# Worker Attachment Boundary V1

Status: model-only worker boundary definition.

## Boundary Principle

The worker receives only authorized execution requests.

The worker cannot self-authorize, bypass governance, bypass replay, mutate replay, mutate governance, or expand capability scope.

## Authorized Request To Worker Execution Request

`AUTHORIZED_REQUEST` may become `WORKER_EXECUTION_REQUEST` only when:

- AiGOL authorization evidence is present
- replay lineage is intact
- target capability is within the frozen read-only capability set
- worker identity is explicit
- capability binding is deterministic
- no hidden continuation is requested
- no mutation surface is requested

## Capability Binding Model

Capability binding links an authorized request to one worker-executable capability.

The binding does not grant new authority. It narrows the authorized request to a specific permitted worker action.

First worker attachment bindings are limited to:

- `READ_ONLY_RUNTIME_INSPECTION`
- `FILESYSTEM_READ_ONLY_INSPECTION`

## Worker Prohibitions

The worker must not:

- create authorization evidence
- modify authorization evidence
- reinterpret governance
- mutate replay artifacts
- invoke unsupported capabilities
- call shell
- call network
- call APIs
- write, delete, move, or modify files
- continue after termination
- persist hidden state

## Boundary Failure

If boundary validation fails, the worker attachment must fail closed before execution.

No partial worker execution may continue after boundary failure.
