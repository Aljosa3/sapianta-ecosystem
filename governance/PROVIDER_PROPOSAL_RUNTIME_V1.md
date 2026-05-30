# Provider Proposal Runtime V1

Status: first replay-visible Provider Proposal runtime.

This milestone implements advisory provider proposal creation:

```text
Human Prompt
-> Cognition Runtime
-> Intent Classification
-> Provider Proposal Runtime
-> Provider Proposal Artifact
-> Replay
```

It does not implement provider execution, provider orchestration, worker execution, authorization, planning, or multi-provider selection.

## Runtime Surface

Implemented runtime file:

```text
aigol/runtime/provider_proposal_runtime.py
```

Implemented tests:

```text
tests/test_provider_proposal_runtime_v1.py
```

Cognition Runtime now delegates `PROVIDER_PROPOSAL` intent to this runtime without invoking a provider.

## Provider Proposal Artifact

The runtime emits `PROVIDER_PROPOSAL_V1` containing:

- `proposal_id`
- `provider_type`
- `reason`
- `authority`
- `execution_capable`
- `created_at`
- `replay_visible`

The runtime also records prompt reference, intent reference, provider invocation status, worker invocation status, proposal status, and artifact hash.

## Replay Events

The runtime records:

- `PROVIDER_PROPOSAL_CREATED`
- `PROVIDER_PROPOSAL_RETURNED`

Replay reconstructs:

- prompt
- intent
- proposal

## Final Status

`PROVIDER_PROPOSAL_RUNTIME_STATUS`: `READY`

`PROVIDER_PROPOSAL_AUTHORITY_STATUS`: `PRESERVED`

`PROVIDER_PROPOSAL_REPLAY_STATUS`: `READY`
