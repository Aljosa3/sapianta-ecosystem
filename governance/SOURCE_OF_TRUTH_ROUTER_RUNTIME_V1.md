# Source Of Truth Router Runtime V1

Status: first replay-visible Source Of Truth Router Runtime implementation.

Final classification:

```text
SOURCE_OF_TRUTH_ROUTER_RUNTIME_STATUS = CERTIFIED
```

## Scope

`SOURCE_OF_TRUTH_ROUTER_RUNTIME_V1` implements deterministic source selection only.

It selects one source from:

```text
REPLAY
GOVERNANCE
CONSTITUTIONAL_MEMORY
SELF_RESOLUTION
PROVIDER
```

It does not invoke source resolvers, providers, workers, dispatch, execution, proposal creation, approval, or response generation.

## Runtime Surface

Implemented runtime file:

```text
aigol/runtime/source_of_truth_router_runtime.py
```

Implemented tests:

```text
tests/test_source_of_truth_router_runtime_v1.py
```

## Router Artifact

The runtime emits:

```text
SOURCE_OF_TRUTH_ROUTER_SELECTION_ARTIFACT_V1
```

Required fields:

- `router_id`
- `selected_source`
- `selection_reason`
- `human_prompt_reference`
- `created_at`

The runtime also records:

- `candidate_sources`
- `source_priority`
- `evidence_refs`
- `provider_required`
- `provider_used`
- `worker_required`
- `execution_required`
- `proposal_lifecycle_required`
- `selection_status`
- `created_by`
- `replay_reference`
- `artifact_hash`

## Source Priority

The runtime applies canonical priority:

```text
REPLAY
GOVERNANCE
CONSTITUTIONAL_MEMORY
SELF_RESOLUTION
PROVIDER
```

## Replay Events

The runtime records:

```text
SOURCE_OF_TRUTH_ROUTER_SELECTED
SOURCE_OF_TRUTH_ROUTER_RETURNED
```

Replay reconstructs:

- router identity;
- selected source;
- candidate sources;
- source priority;
- selection reason;
- prompt reference;
- non-provider, non-worker, non-execution boundary evidence;
- artifact hashes.

## Fail-Closed Cases

The runtime fails closed on:

- missing router id;
- missing human prompt reference;
- missing prompt;
- missing creation timestamp;
- invalid source;
- ambiguous routing;
- missing evidence references;
- duplicate replay artifacts;
- corrupt router artifact;
- corrupt replay wrapper;
- replay ordering corruption;
- router reference mismatch.

## Boundary Guarantees

The runtime preserves:

```text
provider_used = false
worker_required = false
execution_required = false
proposal_lifecycle_required = false
approval_created = false
execution_requested = false
worker_invoked = false
provider_authority = false
```

Provider may be selected as a source, but is not invoked by this runtime.

No worker is invoked.

No execution is requested.

No response is generated.

## Constitutional Invariant

The runtime preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Runtime mapping:

| Role | Runtime meaning |
| --- | --- |
| LLM proposes | Provider may be selected as fallback source but is not authority |
| AiGOL governs | AiGOL selects the source by deterministic priority |
| Worker executes | Worker execution is absent |
| Replay records | Replay records source selection and return artifacts |

## Validation

Focused validation:

```text
python -m pytest tests/test_source_of_truth_router_runtime_v1.py
```

Result:

```text
26 passed
```

Broader source strategy validation:

```text
python -m pytest tests/test_source_of_truth_router_runtime_v1.py tests/test_resolution_strategy_runtime_v1.py tests/test_replay_resolution_strategy_v1.py tests/test_constitutional_memory_resolution_strategy_v1.py tests/test_governance_resolution_strategy_v1.py
```

Result:

```text
93 passed
```

## Final Result

AiGOL can deterministically select and replay-record a source of truth for supported prompt classes.

```text
SOURCE_OF_TRUTH_ROUTER_RUNTIME_STATUS = CERTIFIED
```
