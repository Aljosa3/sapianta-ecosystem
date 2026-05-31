# AUTHORIZATION_LIFECYCLE_V1

## Status

Certified authorization lifecycle.

## Lifecycle States

```text
PROPOSED
REVIEWED
REQUESTED
VALIDATED
AUTHORIZED
REJECTED
FAILED
TERMINATED
```

## Transition Model

```text
PROPOSED
-> REVIEWED
-> REQUESTED
-> VALIDATED
-> AUTHORIZED
-> AUTHORIZED_WORKER_REQUEST
-> WORKER_EXECUTION
-> EXECUTION_REPLAY
-> TERMINATED
```

## Non-Executing Outcomes

```text
PROPOSED
-> REVIEWED
-> REJECTED
-> TERMINATED
```

```text
PROPOSED
-> REVIEWED
-> FAILED
-> TERMINATED
```

## Exact Authorization Point

Execution authority begins only at:

```text
AUTHORIZED
```

and only when that state is attached to replay-visible authorization evidence.

## Invalid Transitions

```text
PROPOSED -> AUTHORIZED_WORKER_REQUEST
PROVIDER_RESPONSE -> AUTHORIZED
PROPOSAL -> WORKER_EXECUTION
REPLAY -> AUTHORIZED
WORKER -> AUTHORIZED
COGNITION -> AUTHORIZED
```

Invalid transitions fail closed.
