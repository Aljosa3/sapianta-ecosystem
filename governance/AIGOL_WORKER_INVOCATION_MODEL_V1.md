# AIGOL_WORKER_INVOCATION_MODEL_V1

## Status

Certified constitutional invocation model.

## Purpose

Define the artifacts and transitions required to move from authorized execution
preparation to a replay-visible Worker invocation boundary.

## Invocation Request

`WORKER_INVOCATION_REQUEST_ARTIFACT_V1` requests invocation of one bounded Worker
role against one authorized execution packet.

It must contain:

- invocation request id;
- chain id;
- execution-ready status reference and hash;
- execution packet reference and hash;
- execution authorization reference and hash;
- requested Worker role;
- requested capability;
- bounded invocation parameter reference and hash;
- allowed outputs;
- forbidden operations;
- request timestamp;
- request hash.

The request is non-authoritative. It cannot invoke or dispatch a Worker.

## Worker Assignment And Dispatch

Before invocation:

- a Worker assignment must identify one eligible registered Worker;
- the assigned Worker must satisfy role, capability, trust, and authority boundaries;
- a dispatch artifact must bind the same Worker to the same authorization and packet;
- assignment and dispatch must remain replay-visible and independently valid.

No implicit Worker resolution or role switching is permitted.

Hybrid Provider-Workers must be assigned explicitly in `WORKER_ROLE`. Provider
role evidence cannot be reused as Worker invocation authority.

## Worker Invocation Artifact

`WORKER_INVOCATION_ARTIFACT_V1` records the governed delivery of bounded
invocation parameters to the dispatched Worker.

It must contain:

- invocation id;
- chain id;
- invocation request reference and hash;
- execution authorization reference and hash;
- execution packet reference and hash;
- Worker assignment reference and hash;
- dispatch reference and hash;
- Worker identity and Worker hash;
- Worker role and capability;
- invocation parameters and parameter hash;
- invoked-by identity;
- invocation timestamp;
- invocation status;
- boundary flags;
- replay reference;
- invocation artifact hash.

## Boundary Flags

The invocation artifact must preserve:

```json
{
  "provider_authority": false,
  "worker_self_invoked": false,
  "scope_expansion": false,
  "automatic_authorization": false,
  "automatic_retry": false,
  "governance_mutation": false,
  "replay_mutation": false,
  "execution_completed": false
}
```

## Invocation Preconditions

Invocation may occur only when:

- execution status is `EXECUTION_READY`;
- authorization status is active and `AUTHORIZED`;
- invocation request is valid;
- Worker assignment is valid;
- dispatch status is valid;
- all references resolve to the same chain, packet, Worker, role, and capability;
- invocation parameters exactly match authorized scope;
- no cancellation, expiry, revocation, duplicate invocation, or replay corruption exists;
- all pre-invocation validations pass.

## Invocation States

The invocation boundary recognizes:

- `REQUESTED`;
- `ASSIGNED`;
- `DISPATCHED`;
- `INVOKED`;
- `FAILED_INVOCATION`;
- `CANCELLED`;
- `EXPIRED`.

Only the ordered transition:

```text
REQUESTED -> ASSIGNED -> DISPATCHED -> INVOKED
```

is a positive invocation path.

## Invocation Prohibitions

Worker invocation must not:

- authorize execution;
- select an unregistered Worker;
- switch a hybrid resource role implicitly;
- expand execution scope;
- add outputs or effects;
- include credentials or secrets;
- create files or code by itself;
- record successful execution;
- record result acceptance;
- mutate governance;
- mutate existing replay;
- trigger hidden continuation.

## Worker Result

`WORKER_RESULT_ARTIFACT_V1` is produced only after a separately governed execution
boundary acts.

It must remain bound to:

- invocation reference and hash;
- execution packet reference and hash;
- Worker identity and hash;
- authorized output scope;
- execution evidence;
- result hash;
- termination state.

Worker result evidence is untrusted until result validation succeeds.

## Constitutional Rule

```text
Invocation delivers authority-bounded work.
Invocation does not create authority.
```
