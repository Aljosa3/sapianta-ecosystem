# Resolution Strategy Runtime V1

Status: first replay-visible Resolution Strategy Runtime implementation.

Final classification:

```text
RESOLUTION_STRATEGY_RUNTIME_STATUS = CERTIFIED
```

## Scope

`RESOLUTION_STRATEGY_RUNTIME_V1` implements deterministic strategy selection evidence only.

Implemented strategies:

```text
SELF_RESOLUTION
REPLAY
CONSTITUTIONAL_MEMORY
GOVERNANCE
PROVIDER
```

Future strategies remain foundation-defined but are not implemented in V1:

```text
WORKER
COMBINED
```

## Runtime Surface

Implemented runtime file:

```text
aigol/runtime/resolution_strategy_runtime.py
```

Implemented tests:

```text
tests/test_resolution_strategy_runtime_v1.py
```

## Strategy Selection Artifact

The runtime emits:

```text
RESOLUTION_STRATEGY_SELECTION_ARTIFACT_V1
```

Required fields:

- `strategy_id`
- `selected_strategy`
- `selection_reason`
- `human_prompt_reference`
- `created_at`

The runtime also records:

- `candidate_strategies`
- `source_precedence`
- `provider_required`
- `provider_used`
- `worker_required`
- `proposal_lifecycle_required`
- `selection_status`
- `created_by`
- `artifact_hash`
- non-authority and non-execution flags.

## Replay Events

The runtime records:

```text
RESOLUTION_STRATEGY_SELECTED
RESOLUTION_STRATEGY_RETURNED
```

Replay reconstructs:

- strategy identity;
- selected strategy;
- selection reason;
- human prompt reference;
- provider requirement;
- non-execution boundary evidence;
- artifact hashes.

## Strategy Semantics

`SELF_RESOLUTION` means AiGOL will attempt deterministic local resolution before provider response generation.

`REPLAY` means replay-backed operational evidence is required.

`CONSTITUTIONAL_MEMORY` means citation-bound constitutional memory is required.

`GOVERNANCE` means governance artifact evidence is required.

`PROVIDER` means provider assistance is required for a later bounded provider-assisted path.

V1 records selection only. It does not invoke a provider.

## Fail-Closed Cases

The runtime fails closed on:

- missing strategy id;
- missing human prompt reference;
- missing selected strategy;
- missing selection reason;
- missing creation timestamp;
- invalid strategy;
- non-AiGOL creator;
- duplicate replay artifacts;
- corrupt strategy artifact;
- corrupt replay wrapper;
- replay ordering corruption;
- strategy reference mismatch.

## Boundary Guarantees

The runtime preserves:

```text
authority = false
approval_created = false
execution_requested = false
provider_authority = false
provider_used = false
worker_required = false
worker_invoked = false
proposal_lifecycle_required = false
```

No provider is invoked.

No worker is invoked.

No approval is created.

No execution request is created.

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
| LLM proposes | Provider strategy may be selected but provider is not authoritative |
| AiGOL governs | AiGOL records deterministic strategy selection |
| Worker executes | Worker runtime is absent |
| Replay records | Replay records strategy selection and return artifacts |

## Validation

Focused validation:

```text
python -m pytest tests/test_resolution_strategy_runtime_v1.py
```

Result:

```text
18 passed
```

## Final Result

AiGOL can explicitly choose and record `SELF_RESOLUTION`, `REPLAY`, `CONSTITUTIONAL_MEMORY`, `GOVERNANCE`, or `PROVIDER` before response generation.

```text
RESOLUTION_STRATEGY_RUNTIME_STATUS = CERTIFIED
```
