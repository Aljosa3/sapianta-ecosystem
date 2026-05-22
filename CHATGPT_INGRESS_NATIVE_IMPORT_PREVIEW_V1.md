# CHATGPT_INGRESS_NATIVE_IMPORT_PREVIEW_V1

Status: implemented as cockpit import-preview only.

## Purpose

`CHATGPT_INGRESS_NATIVE_IMPORT_PREVIEW_V1` lets the AiGOL cockpit accept pasted `CHATGPT_INGRESS_ARTIFACT_V1` JSON and preview the import-only structural validation path.

The target flow is:

```text
CHATGPT_INGRESS_ARTIFACT_V1 JSON
-> cockpit import
-> parse JSON
-> validate ingress artifact
-> import-only structural continuity preview
-> preview cards
-> STOP
```

## Import-Only Scope

The cockpit control is labeled `Preview Import Only`. It parses JSON, validates the artifact shape and authority boundaries, renders accepted or rejected preview state, and stops.

The preview remains:

- import only;
- preview only;
- non-executing;
- observability only;
- structural continuity only.

## UI Behavior

The isolated `ChatGPT Ingress Preview (Import-Only)` cockpit section includes:

- a textarea for `CHATGPT_INGRESS_ARTIFACT_V1` JSON;
- a `Preview Import Only` button;
- visible import status;
- preview cards for ingress artifact, import validation, proposal candidate, contract candidate, governance report, and STOP.

The control does not use run, execute, dispatch, send-to-Codex, or authorize wording.

## JSON Artifact Import Model

Imported JSON is treated as untrusted semantic input. It must preserve the `CHATGPT_INGRESS_ARTIFACT_V1` schema, non-authority flags, replay identity, hashes, provenance, and required boundary statement.

Invalid JSON is rejected visibly as `INVALID_JSON`.

## Validation Path

The preview validates:

- artifact type;
- schema version;
- source;
- validation status;
- authority boundary flags;
- required boundary statement;
- replay identity presence;
- hash presence and format;
- provenance presence;
- forbidden provider dispatch, execution authorization, governance approval, autonomous continuation, semantic correctness, and governance bypass claims.

The preview renders:

- `ACCEPTED_FOR_STRUCTURAL_IMPORT`;
- `REJECTED`;
- rejection reason when rejected.

## Preview Result Model

The preview displays:

- replay identity;
- ingress artifact hash;
- semantic output hash;
- proposal candidate hash;
- contract candidate hash;
- governance report hash;
- provenance lineage summary;
- STOP state.

All preview cards remain classified as `STRUCTURAL_ONLY`, `ADVISORY_ONLY`, or `UI_ONLY`.

## Fail-Closed Rejection Model

The preview rejects when parsing fails, validation fails, authority boundary is violated, hashes are malformed, replay identity is missing, provenance is invalid, or forbidden authority/semantic correctness claims are detected.

Rejected preview imports produce no execution, no provider dispatch, no governance approval, and no semantic correctness proof.

## Why This Is Not Execution

The preview does not call Native Messaging, the service worker execution path, Python runtime execution, Codex providers, or minimal end-to-end bridge execution. It does not create execution envelopes or governed task packages.

It only updates preview cards in the cockpit.

## Why Codex Is Not Dispatched

Codex is not dispatched because the preview is not connected to any provider path. The preview status explicitly states:

- `codex_dispatch_performed: false`;
- `execution_performed: false`;
- `governance_approved: false`;
- `semantic_correctness_verified: false`;
- `autonomous_continuation_performed: false`.

## ChatGPT Authority Boundary

ChatGPT remains non-authoritative semantic input. Imported content cannot approve execution, authorize Codex, select providers, bypass AiGOL governance, verify semantic correctness, or continue autonomously.

## Future Gate Preparation

This prepares a future governed semantic ingress gate by making imported ChatGPT artifacts visible, structurally validated, and replay/hash traceable before any live adapter or runtime integration exists.

