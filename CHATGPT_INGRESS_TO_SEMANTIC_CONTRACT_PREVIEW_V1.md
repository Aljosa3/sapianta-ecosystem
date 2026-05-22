# CHATGPT_INGRESS_TO_SEMANTIC_CONTRACT_PREVIEW_V1

Status: implemented as cockpit preview only.

## Purpose

`CHATGPT_INGRESS_TO_SEMANTIC_CONTRACT_PREVIEW_V1` exposes the import-only ChatGPT ingress pipeline in the AiGOL cockpit as deterministic observability.

The visible preview flow is:

```text
ChatGPT ingress artifact
-> import validation
-> semantic proposal candidate
-> semantic contract candidate
-> governance acceptance report
-> STOP
```

## Preview-Only Scope

The preview is display and structural visibility only. It does not create execution envelopes, governed task packages, provider invocations, or runtime dispatch.

The preview cards are marked only as:

- `STRUCTURAL_ONLY`;
- `ADVISORY_ONLY`;
- `UI_ONLY`.

No preview card is real execution.

## Non-Goals

This milestone does not implement:

- live ChatGPT integration;
- live ChatGPT cognition;
- semantic correctness verification;
- governance approval;
- Codex dispatch;
- provider invocation;
- orchestration;
- autonomous continuation;
- retries;
- background execution;
- durable replay persistence.

## Why This Is Not Execution

The preview has no run or execute control. It does not call Native Messaging, the service worker execution path, the Python minimal bridge, or Codex provider modules.

The preview explicitly states:

- `execution_performed: false`;
- `codex_dispatch_performed: false`;
- `governance_approved: false`;
- `semantic_correctness_verified: false`;
- `autonomous_continuation_performed: false`.

## Governance Separation

ChatGPT-originated semantic content remains untrusted input. The preview may display candidate continuity, but it does not approve governance, authorize execution, dispatch providers, or verify semantic truth.

AiGOL remains the governance authority for any later admissibility and runtime boundary decisions.

## Structural Continuity Model

The preview deterministically renders:

- replay identity;
- ingress artifact hash;
- semantic output hash;
- proposal candidate hash;
- contract candidate hash;
- governance report hash;
- provenance lineage summary.

These are visibility values only. They are not durable replay persistence and not execution evidence.

## Isolation From Canonical Runtime

The preview section is visually separated from the canonical core flow and the governed execution observatory. It is labeled `ChatGPT Ingress Preview (Import-Only)` and contains no action buttons.

It does not attach to:

- Native Messaging;
- service worker runtime execution;
- Python minimal end-to-end bridge execution;
- Codex provider execution;
- governed task package creation.

The purpose is to demonstrate semantic ingress continuity without execution authority.

