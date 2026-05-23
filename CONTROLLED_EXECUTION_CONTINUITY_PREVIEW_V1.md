# CONTROLLED_EXECUTION_CONTINUITY_PREVIEW_V1

Status: implemented as execution continuity preview only.

## Purpose

`CONTROLLED_EXECUTION_CONTINUITY_PREVIEW_V1` creates a non-executing preview of the controlled execution continuity path after `EXPLICIT_DISPATCH_AUTHORIZATION_V1` reaches `DISPATCH_AUTHORIZED`.

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
-> explicit dispatch authorization
-> DISPATCH_AUTHORIZED
-> controlled execution continuity PREVIEW
-> READY_FOR_CONTROLLED_EXECUTION_HANDOFF
-> STOP
```

No execution occurs. Native Messaging is not called. Codex is not dispatched. Provider invocation remains disconnected.

## Continuity-Preview-Only Scope

This milestone shows which execution path would be used without using it.

It creates visibility for:

- sidepanel candidate;
- service worker candidate;
- Native Messaging host candidate;
- Python runtime bridge candidate;
- bounded Codex CLI provider candidate;
- workspace scope candidate;
- timeout policy candidate;
- replay lineage continuity.

Every execution path stage is marked `PREVIEW_ONLY` or `NOT_CALLED`.

## Execution Path Candidate Model

The path candidate is:

```text
sidepanel
-> service_worker
-> Native Messaging host
-> Python runtime bridge
-> bounded Codex CLI provider
```

The candidate is structural visibility only. It is not a runtime call chain.

## Dispatch Authorization Is Not Execution

Dispatch authorization is prerequisite visibility only. It does not itself execute, dispatch Codex, call Native Messaging, call a service worker, or invoke a provider.

The preview may reach:

```text
READY_FOR_CONTROLLED_EXECUTION_HANDOFF
```

That state means actual controlled execution handoff remains future work.

## Mandatory Non-Execution Flags

Every accepted continuity preview preserves:

```text
preview_only: true
execution_performed: false
codex_dispatch_performed: false
native_messaging_called: false
provider_invoked: false
provider_dispatch_performed: false
service_worker_called: false
executable: false
dispatched: false
autonomous_continuation_performed: false
```

## Authority Boundary

The preview explicitly preserves:

```text
dispatch_authorized: true
execution_authorized: false
execution_performed: false
codex_dispatch_performed: false
native_messaging_called: false
provider_invoked: false
autonomous_continuation_authorized: false
```

## Replay-Visible Continuity Preview Hash

`continuity_preview_hash` is deterministic. It is computed from canonical JSON with sorted keys, deterministic separators, and stable encoding.

The hash input includes:

- replay identity;
- dispatch authorization hash;
- handoff preview hash;
- human approval hash;
- task package preview hash;
- semantic contract candidate hash;
- admissibility gate hash;
- execution path candidate;
- authority boundary flags;
- execution continuity status.

## Why Native Messaging Is Not Called

The preview module does not import or call Native Messaging code, service worker code, browser runtime messaging, or native host execution. It only records a candidate path with `NOT_CALLED` stages.

## Why Codex Is Not Dispatched

The preview module does not import or call Codex provider code, provider wrappers, subprocesses, or runtime execution. The bounded Codex CLI provider appears only as a candidate stage marked `NOT_CALLED`.

## Preparing Actual Controlled Execution Handoff

This milestone prepares the future controlled execution handoff by making the intended path visible before it is used.

Actual controlled execution handoff must be a separate governed milestone with its own validation, replay evidence, and execution boundary.

## Non-Goals

This milestone does not add:

- Codex execution;
- Native Messaging execution;
- provider invocation;
- runtime dispatch;
- automatic execution;
- autonomous continuation;
- orchestration;
- retries;
- background workers.
