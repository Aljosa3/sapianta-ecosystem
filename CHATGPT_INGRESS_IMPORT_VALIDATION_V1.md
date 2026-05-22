# CHATGPT_INGRESS_IMPORT_VALIDATION_V1

Status: implemented as import-only structural validation.

## Purpose

`CHATGPT_INGRESS_IMPORT_VALIDATION_V1` creates a governed import path for `CHATGPT_INGRESS_ARTIFACT_V1`.

The path accepts an ingress artifact, validates it, derives structural candidates, emits a governance acceptance or rejection report, and stops.

## Non-Goals

This milestone does not implement:

- live ChatGPT integration;
- semantic correctness verification;
- Codex execution;
- provider dispatch;
- provider routing;
- autonomous continuation;
- orchestration;
- background workers;
- retries;
- durable replay persistence;
- governance mutation.

## Import-Only Boundary

The import pipeline is:

```text
ChatGPT ingress artifact
-> ingress validator
-> semantic proposal candidate
-> semantic contract candidate
-> governance validation report
-> STOP
```

No downstream runtime is connected. The imported artifact remains untrusted semantic input.

## Structural Continuity Model

The import path preserves structural continuity across:

- ingress artifact hash;
- human request hash;
- semantic output hash;
- replay identity;
- provenance lineage;
- proposal candidate hash;
- contract candidate hash;
- governance acceptance report hash.

This continuity is replay-ready identity only. It is not durable replay persistence.

## Semantic Proposal Candidate

The semantic proposal candidate is deterministic and marked:

- `proposal_candidate_only: true`;
- `classification: STRUCTURAL_ONLY`;
- `execution_authority: false`;
- `governance_authority: false`;
- `codex_dispatch_allowed: false`;
- `autonomous_continuation_allowed: false`.

It carries normalized intent, expected artifacts, constraints, forbidden operations, provenance references, replay identity, and hashes.

## Semantic Contract Candidate

The semantic contract candidate is not a live semantic contract. It is structurally derived candidate state only.

It is marked:

- `contract_candidate_only: true`;
- `classification: STRUCTURAL_ONLY`;
- `semantic_correctness_verified: false`;
- `governance_approved: false`;
- `execution_authorized: false`;
- `provider_dispatch_authorized: false`.

## Governance Acceptance Report

Allowed report statuses:

- `ACCEPTED_FOR_STRUCTURAL_IMPORT`;
- `REJECTED`.

The report always states:

- `import_only: true`;
- `execution_performed: false`;
- `codex_dispatch_performed: false`;
- `autonomous_continuation_performed: false`;
- `semantic_correctness_verified: false`.

Rejected imports do not produce proposal or contract candidates.

## Fail-Closed Rules

The import rejects when the ingress artifact validator rejects, including:

- invalid artifact type or schema version;
- missing required fields;
- authority boundary violation;
- forbidden provider dispatch fields;
- execution authorization fields;
- autonomous continuation fields;
- hidden approval or governance approval language;
- semantic correctness claims;
- AiGOL governance bypass claims;
- invalid replay identity;
- invalid hashes;
- invalid provenance.

## Why This Is Not Execution

This module does not import Codex provider modules, service worker paths, Native Messaging runtime paths, or minimal end-to-end bridge execution. It does not call subprocesses, providers, or runtime dispatch functions.

It proves semantic ingress continuity without execution authority.

## Governance Separation

ChatGPT-originated content remains untrusted semantic input. The import layer may structure it into candidates, but candidates are not approval, not execution authorization, not provider dispatch, and not semantic correctness proof.

AiGOL remains the governance authority for any later admissibility, task packaging, execution gating, and structural verification.

