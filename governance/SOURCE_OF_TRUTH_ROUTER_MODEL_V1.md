# Source Of Truth Router Model V1

Status: model foundation.

## Model Purpose

The Source Of Truth Router model defines how AiGOL records the selected source category for a human prompt.

It is a routing artifact.

It is not:

- a response artifact;
- a provider request;
- a worker task;
- an execution request;
- an approval decision;
- a governance mutation.

## Router Artifact

The minimal router artifact is:

```text
SOURCE_OF_TRUTH_ROUTER_SELECTION_ARTIFACT_V1
```

## Required Fields

```text
router_selection_id
source_prompt_id
source_conversation_id optional
candidate_sources
selected_source
source_priority
selection_reason
evidence_refs
provider_required
provider_used
worker_required
execution_required
proposal_lifecycle_required
selection_status
created_by
created_at
replay_reference
artifact_hash
```

## Valid Sources

V1 router-supported sources:

```text
REPLAY
GOVERNANCE
CONSTITUTIONAL_MEMORY
SELF_RESOLUTION
PROVIDER
```

Defined but not router-supported in V1:

```text
WORKER
COMBINED
```

## Selection Statuses

```text
SELECTED
FAILED_CLOSED
REPLAY_RECONSTRUCTED
```

## Source Priority

```text
REPLAY
GOVERNANCE
CONSTITUTIONAL_MEMORY
SELF_RESOLUTION
PROVIDER
```

## Evidence Reference Requirements

| Source | Evidence refs required | Provider required |
| --- | --- | --- |
| `REPLAY` | Replay source reference | No |
| `GOVERNANCE` | Governance artifact reference | No |
| `CONSTITUTIONAL_MEMORY` | Citation or memory retrieval reference | No |
| `SELF_RESOLUTION` | Deterministic rule or template reference | No |
| `PROVIDER` | Provider availability and validation path reference | Yes or possibly required |

## Router Events

Required replay events:

```text
SOURCE_OF_TRUTH_ROUTER_SELECTED
SOURCE_OF_TRUTH_ROUTER_RETURNED
```

## Selection Record

The selected record must prove:

- the prompt was known;
- the candidate set was known;
- the selected source was in the candidate set;
- the selected source obeyed priority;
- required evidence existed;
- provider was not used for higher-priority truth;
- no worker or execution authority was created.

## Invalid Router Artifacts

A router artifact is invalid if:

- selected source is not supported;
- selected source is missing from candidate sources;
- priority is missing;
- evidence refs are missing for evidence-bound source;
- provider is required for replay truth;
- provider is required for governance truth;
- provider is required for constitutional truth;
- worker execution is implied;
- proposal lifecycle is silently created;
- `created_by` is not `AIGOL`;
- replay visibility is absent.

Invalid artifacts must fail closed.

## Reconstruction

Router reconstruction returns:

```text
router_selection_id
source_prompt_id
candidate_sources
selected_source
source_priority
selection_reason
selection_status
provider_required
worker_required
execution_required
proposal_lifecycle_required
replay_visible
replay_hash
```

Reconstruction is read-only and cannot change selected source.
