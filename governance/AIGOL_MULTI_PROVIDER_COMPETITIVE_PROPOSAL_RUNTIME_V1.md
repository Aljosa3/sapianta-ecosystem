# AIGOL_MULTI_PROVIDER_COMPETITIVE_PROPOSAL_RUNTIME_V1

## Status

Multi-provider competitive proposal runtime certified.

## Final Classification

```text
AIGOL_MULTI_PROVIDER_COMPETITIVE_PROPOSAL_RUNTIME_STATUS = CERTIFIED
```

## Purpose

This runtime allows multiple providers to produce competing implementation
proposals for the same request while preserving AiGOL governance.

Providers propose only. AiGOL validates each proposal, presents a comparative
review, records human selection, and authorizes materialization only for the
selected validated proposal.

## CLI Surface

Certified command:

```text
python -m aigol.cli.aigol_cli implementation compete \
  --request "Create competing governed implementation candidates for operator selection." \
  --runtime-root /tmp/aigol_multi_provider_competition_replay_v2 \
  --workspace /tmp/aigol_multi_provider_competition_workspace_v2 \
  --created-at 2026-06-05T23:00:00Z \
  --actor-id human.operator \
  --selection PROVIDER_B \
  --decision-reason "Operator selected provider B after comparative validation."
```

Observed result:

```text
status: MULTI_PROVIDER_COMPETITION_CERTIFIED
competition_hash: sha256:e3909cec3488a544632d252ac13c58788ad46c9b4f4e5d45b84e8373fba9d8f9
replay_files: 38
workspace_files: 3
```

## Required Flow

Certified flow:

```text
Request
-> Multiple Provider Proposals
-> Comparative Validation
-> Human Selection
-> Authorization
-> Materialization
-> Certification
-> Replay
```

## Providers

Supported providers:

- `PROVIDER_A`;
- `PROVIDER_B`;
- `PROVIDER_C`.

Each provider receives the same OCS-prepared request and produces an untrusted
implementation proposal. Each provider pipeline records:

- provider proposal replay;
- provider-generated candidate;
- implementation manifest;
- generated content validation;
- generated test validation;
- implementation summary;
- provider pipeline result.

## Comparative Review

The comparative review screen shows:

- provider id;
- proposal summary;
- validation status;
- affected paths.

Observed comparative validation hash:

```text
sha256:6fde75ee1a002366d5e10ca0dea60a41255a27f7f69fe7f7ebbee09de601871b
```

Observed selection decision:

```text
selected_provider_id: PROVIDER_B
selection_decision_hash: sha256:4fdc0994b49c34c6020a3fb6c7a587e29cb574897be78213dced55db0bcf5201
```

## Governance Guarantees

The runtime enforces:

- all provider outputs are untrusted until validated;
- all proposals and validation outcomes are replay-visible;
- authorization is allowed only for the selected provider;
- materialization is allowed only for the selected provider;
- no overwrite;
- no delete;
- no rename;
- no implicit mutation;
- `CREATE_ONLY` only.

Selected implementation certification:

```text
implementation_certification_hash: sha256:5d15691340e6b5a226be2753ac3921ca83ab6c687bc9b28d85f647cb641d7253
competitive_replay_hash: sha256:2c2964903a1f4373e4c0a4b05c6b921b608af04be834849d70dc86680f32c1ef
```

## Operator Outcomes

### SELECT Provider

`SELECT PROVIDER_B` reached:

```text
MULTI_PROVIDER_COMPETITION_CERTIFIED
```

Only the selected provider was authorized and materialized.

### REJECT All

Observed result:

```text
MULTI_PROVIDER_REJECTED_FAILED_CLOSED
workspace_files: 0
```

No authorization or materialization occurred.

### ABORT

Observed result:

```text
MULTI_PROVIDER_ABORTED
workspace_files: 0
```

No authorization or materialization occurred.

## Validation Failure Evidence

Test coverage injects a failing `PROVIDER_B` adapter with missing generated test
artifacts. The runtime records `PROVIDER_B` as `FAILED_VALIDATION` and allows a
validated provider (`PROVIDER_C`) to be selected and certified.

## Validation

Validation performed:

```text
python -m pytest tests/test_multi_provider_competitive_proposal_runtime_v1.py
python -m pytest tests/test_multi_provider_selected_worker.py
git diff --check
```

Downstream governance chain validation remains covered by:

```text
python -m pytest tests/test_implementation_certification_runtime_v1.py
python -m pytest tests/test_filesystem_mutation_runtime_v1.py
python -m pytest tests/test_filesystem_mutation_authorization_runtime_v1.py
python -m pytest tests/test_generated_content_acceptance_runtime_v1.py
python -m pytest tests/test_generated_test_validation_runtime_v1.py
python -m pytest tests/test_generated_content_validation_runtime_v1.py
python -m pytest tests/test_implementation_manifest_runtime_v1.py
```

## Certification Judgment

`AIGOL_MULTI_PROVIDER_COMPETITIVE_PROPOSAL_RUNTIME_V1` is certified.

The runtime supports competitive provider proposals under full governance and
prevents authorization or materialization of any non-selected proposal.
