# Worker Runtime Transitions V1

Status: transition foundation.

## Transition Principle

Worker transitions are downstream execution states.

They may occur only after AiGOL validates a replay-visible execution request and assigns a capability-bound Worker.

## Worker State Set

```text
AVAILABLE
ASSIGNED
EXECUTING
COMPLETED
FAILED
```

## Transition Table

| From | To | Actor | Human approval required | Rule |
| --- | --- | --- | --- | --- |
| worker identity created | `AVAILABLE` | AiGOL | No | AiGOL records worker identity and capability envelope |
| `READY_FOR_DISPATCH` execution request | `ASSIGNED` | AiGOL | Already present upstream | AiGOL assigns a capability-compatible worker |
| `ASSIGNED` | `EXECUTING` | Worker | No | Worker begins only assigned bounded work |
| `EXECUTING` | `COMPLETED` | Worker | No | Worker returns bounded result evidence |
| `EXECUTING` | `FAILED` | Worker | No | Worker returns deterministic failure evidence |
| `ASSIGNED` | `FAILED` | AiGOL or Worker | No | Assignment fails before execution starts |
| Any recorded state | replay reconstruction | Replay | No | Replay reconstructs read-only worker history |

## Execution Request Preconditions

Worker assignment requires:

```text
execution_request.status = READY_FOR_DISPATCH
```

Assignment is forbidden for:

```text
execution_request.status = CREATED
execution_request.status = CANCELLED
execution_request.status = COMPLETED
execution_request.status = FAILED
```

## Actor Rules

AiGOL may:

- validate execution request lineage;
- validate dispatch readiness;
- select a compatible worker;
- record worker identity;
- record capability binding;
- assign a worker;
- record assignment failure.

Worker may:

- accept assigned bounded work;
- execute only the assigned request;
- record result evidence;
- record failure evidence;
- terminate.

Worker may not:

- self-assign;
- self-authorize;
- approve proposals;
- derive execution requests;
- expand request payload;
- mutate governance;
- mutate replay history;
- invoke providers;
- create hidden continuation.

Provider may not:

- assign workers;
- select workers;
- command workers;
- approve worker execution;
- receive a direct provider-to-worker path.

Human may not:

- directly dispatch workers through this foundation;
- bypass AiGOL validation;
- create worker result evidence manually.

Replay may:

- reconstruct Worker identity and activity.

Replay may not:

- assign workers;
- execute work;
- infer missing dispatch;
- repair missing result evidence.

## Terminal States

Terminal Worker states:

```text
COMPLETED
FAILED
```

Terminal states require termination evidence.

## Fail-Closed Rules

Transitions fail closed if:

- execution request is not `READY_FOR_DISPATCH`;
- execution request replay reconstruction fails;
- worker identity is missing;
- capability binding is missing;
- requested capability is unsupported;
- assignment is not AiGOL-created;
- worker self-assignment is detected;
- provider command is detected;
- request payload expands beyond approved scope;
- replay lineage is missing;
- result evidence is missing;
- termination evidence is missing;
- duplicate terminal results exist;
- state ordering is invalid.
