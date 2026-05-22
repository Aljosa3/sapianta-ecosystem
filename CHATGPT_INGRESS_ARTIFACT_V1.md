# CHATGPT_INGRESS_ARTIFACT_V1

Status: implemented as a schema and fail-closed validator only.

## Purpose

`CHATGPT_INGRESS_ARTIFACT_V1` is a canonical, non-authoritative artifact for future ChatGPT semantic transport into AiGOL.

It represents model-produced semantic input that AiGOL may later import as untrusted context. It does not make ChatGPT part of the runtime execution path.

## Non-Goals

This milestone does not implement:

- live ChatGPT invocation;
- ChatGPT API calls;
- live ingress adapter;
- Codex dispatch from ChatGPT;
- provider selection;
- execution authorization;
- approval authority;
- autonomous continuation;
- background workers;
- durable replay persistence;
- semantic correctness verification.

## Authority Boundary

ChatGPT output is semantic input only.

Required boundary statement:

```text
ChatGPT output is semantic input only and cannot authorize execution.
```

The artifact authority boundary must set every authority flag to `false`:

- `chatgpt_authority`;
- `execution_authority`;
- `governance_authority`;
- `approval_authority`;
- `provider_dispatch_authority`;
- `autonomous_continuation_authority`.

AiGOL remains the governance authority. Codex remains a bounded execution provider only after AiGOL validation.

## Schema Fields

Required fields:

- `artifact_type`: must be `CHATGPT_INGRESS_ARTIFACT_V1`;
- `schema_version`: must be `1.0`;
- `source`: must be `chatgpt`;
- `created_at`;
- `session_id`;
- `human_request`;
- `chatgpt_semantic_output`;
- `normalized_intent`;
- `expected_artifacts`;
- `constraints`;
- `forbidden_operations`;
- `authority_boundary`;
- `provenance`;
- `replay_identity`;
- `hashes`;
- `validation_status`.

Allowed validation statuses:

- `ACCEPTED_AS_SEMANTIC_INPUT`;
- `REJECTED`.

## Validation Rules

Validation is deterministic and fails closed. The validator rejects artifacts when:

- required fields are missing;
- `artifact_type`, `schema_version`, or `source` are unsupported;
- any authority flag is anything other than `false`;
- the required boundary statement is missing;
- provider dispatch fields are present;
- execution authorization fields are present;
- autonomous continuation fields are present;
- hidden approval or dispatch language is present;
- semantic correctness is claimed;
- AiGOL governance bypass is claimed;
- provenance is missing;
- replay identity is missing or mismatched;
- hashes are missing, malformed, or mismatched.

## Replay Identity Rules

The artifact includes:

- `human_request_hash`;
- `semantic_output_hash`;
- `artifact_hash`;
- `replay_identity`.

Hashes use canonical JSON with sorted keys, deterministic separators, and stable UTF-8 encoding through the existing AiGOL canonical hash helper.

`replay_identity` is deterministically derived from:

- `session_id`;
- `human_request_hash`;
- `semantic_output_hash`;
- `schema_version`.

This milestone creates replay-ready identity only. It does not add durable replay persistence.

## Live ChatGPT Boundary

This artifact does not prove live ChatGPT participation. It can represent ChatGPT-originated semantic text in a future adapter, but this milestone only defines construction and validation primitives.

Future live ingress must first produce this artifact, then submit it to AiGOL as untrusted input. AiGOL may accept or reject it before task packaging. ChatGPT cannot authorize execution, dispatch Codex, approve governance, or continue autonomously.

