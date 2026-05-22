# REAL_TRANSPORT_INTEGRATION_PLAN_V1

Status: plan-only. No implementation in this milestone.

Purpose: smallest-risk path from the current truthful state toward fuller transport continuity, without changing governance boundaries or inflating authority.

## Non-Negotiable Preservations

- ChatGPT remains non-authoritative.
- AiGOL retains governance authority over admissibility, boundaries, lineage, and structural validation.
- Codex remains a bounded execution provider, not governance, approval, orchestration, or continuation authority.
- Replayability remains deterministic and explicit.
- Observability remains deterministic and must distinguish real enforcement from narration.
- No hidden dispatch, no autonomous continuation, no provider routing, no background execution, no silent retry.

## Current Stable Base

The safest current base is:

```text
Human
-> sidepanel explicit operator action
-> MV3 service worker
-> Native Messaging host
-> Python minimal bridge
-> local deterministic normalization
-> AiGOL governed transport validation
-> canonical task package
-> bounded Codex CLI
-> structural result validation
-> governed operator return
```

This base should remain intact while gaps are closed incrementally.

## Minimal Integration Order

### 1. Truth Labels Before New Transport

Keep the observatory and audit matrix as the mandatory runtime truth reference. Any future UI or runtime artifact should explicitly declare:

- path marker;
- real/mock/structural/advisory/UI classification;
- provider involvement;
- persistence state;
- ChatGPT operational status;
- semantic correctness status.

No behavior change is required for this step.

### 2. Durable Replay Backend Candidate

Add a governed durable replay backend only after preserving the current in-memory artifact format. The first upgrade should be append-only, local, deterministic, and opt-in from the Python minimal bridge.

Smallest safe shape:

- append the exact current replay event objects without semantic enrichment;
- include artifact hash and previous event hash;
- preserve `mutation: false`;
- keep sidepanel as reader/importer, not writer of governance truth;
- fail closed if append fails when durable replay is required.

Do not add background replay repair, inference, or mutable replay editing.

### 3. Explicit ChatGPT Ingress Artifact

Before any live ChatGPT integration, define a non-authoritative ingress artifact contract that can carry model-produced semantic text into AiGOL.

Status: implemented by `CHATGPT_INGRESS_ARTIFACT_V1` as a schema and fail-closed validator only. This does not add a live ChatGPT adapter or change runtime behavior.

Smallest safe shape:

- ChatGPT output is input only;
- `chatgpt_authority: false`;
- `execution_authority: false`;
- required boundary statement;
- hash;
- source/session identifiers;
- no provider dispatch fields;
- no automatic execution fields.

AiGOL must still validate and may reject the artifact before task packaging.

### 4. Live ChatGPT Ingress Adapter

Only after the ingress artifact exists, add a governed adapter that imports live ChatGPT output into that artifact format.

Prerequisite status: `CHATGPT_INGRESS_IMPORT_VALIDATION_V1` now provides import-only structural validation from ingress artifact to proposal/contract candidates and a governance report. It stops before runtime execution and does not add a live adapter.

Safety constraints:

- no direct Codex call from ChatGPT;
- no execution authorization from ChatGPT;
- no automatic provider dispatch;
- deterministic canonicalization after receipt;
- full visibility of raw model output hash and normalized artifact hash;
- fail closed on missing boundary statements.

### 5. Semantic Continuity Without Semantic Authority

If semantic continuity is improved, it must remain evidence continuity, not semantic truth. The system may track:

Preview status: `CHATGPT_INGRESS_TO_SEMANTIC_CONTRACT_PREVIEW_V1` now exposes import-only ingress continuity in the cockpit as STRUCTURAL_ONLY / ADVISORY_ONLY observability. It does not connect execution, Codex dispatch, provider invocation, or governance approval.

- raw request hash;
- ChatGPT ingress artifact hash;
- AiGOL-normalized proposal hash;
- semantic contract hash;
- task package hash;
- result artifact hash.

It must not claim semantic correctness unless a separately governed semantic verifier exists and is explicitly classified.

### 6. Governed Return Export To ChatGPT

Add return-to-ChatGPT only as an explicit non-authoritative export artifact first.

Smallest safe shape:

- structural result validation summary;
- provider status;
- replay references;
- known limitations;
- `not_approval`;
- `not_semantic_certification`;
- `not_autonomous_continuation`;
- hash.

Live ChatGPT interpretation, if later connected, must consume this as context only and cannot mutate governance state.

### 7. Optional Live ChatGPT Return Adapter

Only after return artifact stabilization, add a live ChatGPT return adapter. It must:

- receive the governed return export;
- produce advisory interpretation only;
- never alter result validation;
- never create follow-up tasks automatically;
- never dispatch Codex;
- be visibly marked `ADVISORY_ONLY`.

## Smallest-Risk Transport Upgrades

1. Durable replay append for the existing minimal bridge result events.
2. Canonical import/export schemas for ChatGPT ingress and governed return.
3. Sidepanel display of durable replay proof versus session-local replay visibility.
4. Explicit environment check for Native Messaging host installation.
5. Provider result enrichment that captures commands/tests/files only from explicit Codex output or deterministic workspace inspection, with no semantic acceptance claim.

## Forbidden During Integration

- autonomous constitutional mutation;
- direct ChatGPT-to-Codex dispatch;
- automatic provider selection;
- hidden retry/fallback;
- background continuation;
- semantic correctness claims from structural validation;
- durable replay mutation or repair;
- using UI observability as governance authority;
- implying live ChatGPT cognition before adapter evidence exists.

## Acceptance Criteria For Future Implementation

Any future transport integration should pass these truth checks:

- every layer has one classification from `REAL`, `MOCK`, `STRUCTURAL_ONLY`, `ADVISORY_ONLY`, `UI_ONLY`;
- live ChatGPT presence is proven by explicit adapter evidence or labeled absent;
- Codex execution is proven by provider result evidence or labeled not started/mock;
- replay persistence is durable only when an append-only backend writes records;
- structural validation remains separate from semantic correctness;
- sidepanel rendering never creates authority;
- all failure states remain operator-visible and fail closed.
