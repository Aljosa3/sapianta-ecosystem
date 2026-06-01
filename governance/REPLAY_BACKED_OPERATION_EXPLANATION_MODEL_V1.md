# REPLAY_BACKED_OPERATION_EXPLANATION_MODEL_V1

## Model

Replay-backed operation explanation is a deterministic projection of existing replay evidence into human-readable form.

It is not:

- governance authority;
- authorization authority;
- execution authority;
- provider output;
- hidden reasoning;
- speculative analysis.

## Input

The explanation model accepts:

```text
operation_id
runtime_root
```

## Required Replay Evidence

The operation must have reconstructable replay evidence:

```text
provider/000_provider_proposal_created.json
provider/001_provider_proposal_returned.json
authorization/000_authorization_created.json
authorization/001_authorization_returned.json
worker/000_authorized_worker_request.json
worker/001_filesystem_worker_execution.json
```

## Output Fields

The explanation output contains:

- `status`;
- `operation_id`;
- `explanation_type`;
- `what_happened`;
- `why_it_happened`;
- `why_authorized`;
- `trust_explanation`;
- `human_readable_explanation`;
- `evidence`;
- `replay_backed`;
- `authority`;
- `fail_closed`;
- `explanation_hash`.

## Traceability

Every explanation statement must trace to one of:

- proposal id;
- authorization id;
- worker id;
- worker result;
- replay summary;
- replay verification status;
- replay hashes;
- supporting replay files.

## Authority Status

The explanation grants no authority.

It does not authorize, execute, govern, dispatch, plan, or correct.
