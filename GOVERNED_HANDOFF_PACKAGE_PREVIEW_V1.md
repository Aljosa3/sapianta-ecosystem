# GOVERNED_HANDOFF_PACKAGE_PREVIEW_V1

Status: implemented as governed handoff package preview only.

## Purpose

`GOVERNED_HANDOFF_PACKAGE_PREVIEW_V1` creates the first canonical provider-boundary preview after `HUMAN_APPROVAL_GATE_V1` reaches `APPROVED_FOR_GOVERNED_HANDOFF`.

The flow is:

```text
CHATGPT_INGRESS_ARTIFACT_V1
-> import validation
-> semantic proposal candidate
-> semantic contract candidate
-> acceptance gate
-> governed task package preview
-> human approval gate
-> APPROVED_FOR_GOVERNED_HANDOFF
-> governed handoff package PREVIEW
-> STOP
```

No execution occurs. Codex is not dispatched. Native Messaging is not called. Provider execution is not connected.

## Handoff-Preview-Only Scope

The handoff preview is a sealed structural artifact. It proves the system can reach the provider boundary without crossing it.

It demonstrates:

- cognition continuity;
- governance continuity;
- human approval continuity;
- provider-boundary readiness.

It does not grant execution authority, dispatch authority, provider authority, runtime execution authority, or autonomous continuation authority.

## Provider-Boundary Readiness

The mandatory handoff boundary state is:

```text
READY_FOR_EXPLICIT_DISPATCH_AUTHORIZATION
```

This means the next possible boundary is a separately governed explicit dispatch authorization step. It does not mean dispatch is authorized.

## Human Approval Is Not Dispatch Authorization

Human approval confirms the operator accepted the preview for future governed handoff evidence.

Human approval is not dispatch authorization. It does not authorize Codex, provider dispatch, Native Messaging execution, runtime execution, or autonomous continuation.

## Mandatory Flags

Every accepted handoff preview preserves:

```text
preview_only: true
executable: false
dispatchable: false
execution_performed: false
codex_dispatch_performed: false
provider_dispatch_performed: false
autonomous_continuation_performed: false
explicit_dispatch_authorization_required: true
```

## Authority Boundary

The authority boundary explicitly preserves:

```text
human_approval_present: true
execution_authorized: false
dispatch_authorized: false
codex_dispatch_authorized: false
provider_dispatch_authorized: false
governance_execution_approved: false
autonomous_continuation_authorized: false
```

## Replay-Visible Handoff Hash

`handoff_preview_hash` is deterministic. It is computed from canonical JSON with sorted keys, deterministic separators, and stable encoding.

The hash input includes:

- replay identity;
- ingress artifact hash;
- semantic contract candidate hash;
- acceptance gate hash;
- governed task package preview hash;
- human approval hash;
- target provider boundary;
- allowed provider kind;
- workspace scope preview;
- timeout policy preview;
- handoff boundary state;
- authority boundary flags;
- handoff preview status.

## Why This Is Not Execution

The preview contains no executable payload, no runtime dispatch command, no provider invocation, no Native Messaging call, and no Codex call.

The artifact remains:

```text
HANDOFF PREVIEW ONLY
NO EXECUTION
NO CODEX DISPATCH
NO PROVIDER DISPATCH
EXPLICIT DISPATCH AUTHORIZATION REQUIRED
STRUCTURAL_ONLY / ADVISORY_ONLY
```

## Why Codex Is Not Dispatched

The handoff preview does not import or call Codex provider code. It does not invoke `codex`, provider wrappers, Native Messaging, service worker dispatch, subprocesses, or runtime execution.

## Preparing Explicit Governed Dispatch Authorization

This milestone prepares the next boundary by making dispatch authorization explicit and separate.

The next admissible step must be a distinct governed dispatch authorization layer. Until that exists and grants explicit dispatch authority, the system stops at provider-boundary preview.

## Non-Goals

This milestone does not add:

- Codex dispatch;
- provider execution;
- Native Messaging execution;
- automatic handoff;
- runtime execution;
- autonomous continuation;
- orchestration;
- retries;
- background workers.
