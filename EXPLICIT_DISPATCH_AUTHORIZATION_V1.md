# EXPLICIT_DISPATCH_AUTHORIZATION_V1

Status: implemented as dispatch authorization evidence only.

## Purpose

`EXPLICIT_DISPATCH_AUTHORIZATION_V1` creates the first formal dispatch authority layer after `GOVERNED_HANDOFF_PACKAGE_PREVIEW_V1`.

The flow is:

```text
CHATGPT_INGRESS_ARTIFACT_V1
-> import validation
-> semantic proposal candidate
-> semantic contract candidate
-> acceptance gate
-> governed task package preview
-> human approval gate
-> governed handoff package preview
-> READY_FOR_EXPLICIT_DISPATCH_AUTHORIZATION
-> EXPLICIT DISPATCH AUTHORIZATION
-> DISPATCH_AUTHORIZED / DISPATCH_REJECTED
-> STOP
```

No execution occurs. Codex is not dispatched. Native Messaging is not called. Provider execution remains disconnected.

## Dispatch-Authorization-Only Scope

This milestone proves dispatch authorization continuity without execution continuity.

It can create:

- `DISPATCH_AUTHORIZED`
- `DISPATCH_REJECTED`

It cannot create:

- provider execution;
- Codex dispatch;
- Native Messaging execution;
- runnable provider tasks;
- automatic runtime execution;
- autonomous continuation.

## Approval vs Dispatch Authorization

Human approval and dispatch authorization are separate boundaries.

Human approval means the operator approved the handoff preview for future governed handoff evidence.

Dispatch authorization means a later explicit governance boundary has authorized dispatch eligibility.

dispatch authorization != execution continuity.

Dispatch authorization still does not execute, dispatch Codex, call Native Messaging, invoke providers, or create a runnable provider task.

## Provider-Boundary Continuity

When accepted, the provider boundary state becomes:

```text
READY_FOR_CONTROLLED_EXECUTION_CONTINUITY
```

This state means controlled execution continuity may be considered by a later, separately governed milestone. It does not mean execution has occurred.

## Mandatory Non-Execution Flags

Every authorization or rejection artifact preserves:

```text
execution_performed: false
codex_dispatch_performed: false
provider_dispatch_performed: false
native_messaging_called: false
executable: false
dispatched: false
autonomous_continuation_performed: false
```

## Replay-Visible Authorization Evidence

`dispatch_authorization_hash` is deterministic. It is computed from canonical JSON with sorted keys, deterministic separators, and stable encoding.

The hash input includes:

- replay identity;
- ingress artifact hash;
- semantic contract candidate hash;
- admissibility gate hash;
- governed task package preview hash;
- human approval hash;
- governed handoff preview hash;
- dispatch authorization status;
- provider boundary state;
- authority boundary flags.

## Why This Is Not Execution

The authorization artifact has no executable payload, no provider command, no subprocess invocation, no service worker dispatch, no Native Messaging call, and no Codex call.

It explicitly preserves:

```text
DISPATCH AUTHORIZATION ONLY
NO EXECUTION
NO CODEX DISPATCH
NO PROVIDER EXECUTION
NATIVE MESSAGING NOT CALLED
STRUCTURAL_ONLY / ADVISORY_ONLY
```

## Why Native Messaging Is Not Called

This layer does not import or call Native Messaging code. The cockpit buttons create authorization evidence only and do not reach the service worker or native host.

## Why Codex Is Not Dispatched

This layer does not import or call Codex provider code, `codex`, provider wrappers, subprocesses, or runtime execution.

## Preparing Controlled Execution Continuity

This milestone prepares the next boundary by making controlled execution continuity explicit and separate.

The system may now show dispatch authorization continuity, but it still stops before execution continuity.

## Non-Goals

This milestone does not add:

- Codex dispatch;
- Native Messaging execution;
- provider execution;
- automatic dispatch;
- runtime execution;
- autonomous continuation;
- orchestration;
- retries;
- background workers.
