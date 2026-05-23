# GOVERNED_TASK_PACKAGE_PREVIEW_V1

Status: implemented as replay-visible execution-boundary preview only.

## Purpose

`GOVERNED_TASK_PACKAGE_PREVIEW_V1` extends the ChatGPT ingress governance flow after admissibility acceptance. It creates the first governed task package preview state that shows execution-boundary continuity without crossing into execution.

Flow:

```text
CHATGPT_INGRESS_ARTIFACT_V1
-> import validation
-> semantic proposal candidate
-> semantic contract candidate
-> acceptance gate
-> governed task package PREVIEW
-> READY_FOR_HUMAN_APPROVAL
-> STOP
```

## Execution-Boundary Preview Model

The preview is not an executable task package. It is a canonical execution-boundary preview artifact that preserves cognition continuity, governance continuity, and execution-boundary continuity.

The required boundary state is:

```text
READY_FOR_HUMAN_APPROVAL
```

This means the system has reached the future human approval boundary. It does not mean approval has been granted.

## Non-Goals

This milestone does not add:

- Codex dispatch;
- Native Messaging execution;
- provider dispatch;
- executable runtime handoff;
- governance execution approval;
- automatic execution;
- autonomous continuation;
- orchestration;
- retry or fallback routing;
- semantic correctness verification.

Codex is not dispatched. Native Messaging is not called. Provider execution is not connected.

## Replay-Visible Continuity

The preview preserves:

- replay identity;
- ingress artifact hash;
- semantic proposal candidate hash;
- semantic contract candidate hash;
- admissibility gate hash;
- provenance lineage;
- normalized intent;
- expected artifacts;
- constraints;
- forbidden operations.

## Preview Hash Model

`preview_hash` is deterministic. It is computed from canonical JSON with sorted keys, deterministic separators, and stable encoding.

The hash input includes:

- source ingress artifact hash;
- semantic proposal candidate hash;
- semantic contract candidate hash;
- admissibility gate hash;
- replay identity;
- governance status;
- execution boundary state.

## Mandatory Boundary Flags

Every valid preview keeps these flags:

```text
preview_only: true
executable: false
dispatchable: false
governance_finalized: false
execution_authorized: false
codex_dispatch_authorized: false
provider_dispatch_authorized: false
governance_execution_approved: false
autonomous_continuation_authorized: false
human_approval_required: true
```

## Why This Is Not Execution

The artifact carries no authority token, no runnable provider envelope, no execution command, and no dispatch target. It only records that the preview has reached the future human approval boundary.

## Why This Is Not Dispatch

The preview module does not import or call Codex provider code, Native Messaging code, service worker execution paths, subprocess execution, or provider routing. It only consumes existing import and acceptance-gate evidence.

## Human Approval Requirement

Human approval is explicitly required because acceptance for governed preview is not execution approval. The cockpit labels the state as:

```text
PREVIEW ONLY
NO EXECUTION
NO CODEX DISPATCH
HUMAN APPROVAL REQUIRED
STRUCTURAL_ONLY / ADVISORY_ONLY
```

The STOP boundary remains visible after `READY_FOR_HUMAN_APPROVAL`.

## Governance Separation

ChatGPT-originated semantic content remains non-authoritative. AiGOL preserves governance separation by allowing preview-only continuity while withholding execution approval, provider dispatch, and autonomous continuation.
