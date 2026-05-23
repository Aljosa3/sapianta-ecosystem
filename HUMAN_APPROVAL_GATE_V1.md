# HUMAN_APPROVAL_GATE_V1

Status: implemented as human approval evidence only.

## Purpose

`HUMAN_APPROVAL_GATE_V1` creates the first explicit human approval boundary after `GOVERNED_TASK_PACKAGE_PREVIEW_V1`.

The flow is:

```text
CHATGPT_INGRESS_ARTIFACT_V1
-> import validation
-> semantic proposal candidate
-> semantic contract candidate
-> acceptance gate
-> governed task package preview
-> READY_FOR_HUMAN_APPROVAL
-> HUMAN APPROVAL GATE
-> APPROVED_FOR_GOVERNED_HANDOFF / REJECTED_BY_HUMAN
-> STOP
```

No execution occurs. Codex is not dispatched. Native Messaging is not called. Provider execution is not connected.

## Approval Model

Only the human operator can approve crossing from execution-boundary preview toward a future governed handoff.

Allowed approval statuses are:

- `APPROVED_FOR_GOVERNED_HANDOFF`
- `REJECTED_BY_HUMAN`

Approval means evidence for future governed handoff readiness. It does not mean execution approval.

## Required Evidence

The approval artifact contains:

- artifact type and schema version;
- replay identity;
- source task package preview hash;
- explicit human decision;
- approval status;
- approval reason;
- operator label;
- creation timestamp;
- provenance;
- authority boundary;
- deterministic approval hash.

## Replay Hash Model

`approval_hash` is computed from canonical JSON with sorted keys, deterministic separators, and stable encoding.

The hash input includes:

- replay identity;
- source task package preview hash;
- human decision;
- approval status;
- approval reason;
- authority boundary flags;
- provenance.

## Mandatory Non-Execution Flags

Every approval or rejection evidence artifact preserves:

```text
execution_performed: false
codex_dispatch_performed: false
provider_dispatch_performed: false
autonomous_continuation_performed: false
semantic_correctness_verified: false
```

## Cockpit Boundary

The cockpit exposes:

- `Approve Preview`;
- `Reject Preview`;
- approval status;
- human decision;
- approval hash;
- STOP boundary.

These buttons create approval or rejection evidence only. They do not call Native Messaging, dispatch Codex, connect provider execution, create executable handoff, or trigger runtime execution.

## Mandatory Labels

The cockpit labels this boundary:

```text
HUMAN APPROVAL ONLY
NO EXECUTION
NO CODEX DISPATCH
APPROVAL EVIDENCE ONLY
STRUCTURAL_ONLY / ADVISORY_ONLY
```

## Non-Goals

This milestone does not add:

- Codex dispatch;
- provider execution;
- Native Messaging execution;
- autonomous continuation;
- automatic approval;
- orchestration;
- semantic correctness verification;
- retries or fallback routing.

Human approval evidence is replay-visible and deterministic, but the system still stops before execution.
