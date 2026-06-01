# Governance Resolution Strategy V1

Status: first governance-artifact answer resolution strategy.

Final classification:

```text
GOVERNANCE_RESOLUTION_STRATEGY_STATUS = CERTIFIED
```

## Scope

`GOVERNANCE_RESOLUTION_STRATEGY_V1` implements governance-based answer resolution for governance-oriented human prompts.

It extends Resolution Strategy Runtime to support:

```text
GOVERNANCE
```

It does not implement execution, workers, provider authority, provider inference, approval changes, proposal mutation, or governance mutation.

## Runtime Surface

Implemented runtime file:

```text
aigol/runtime/governance_resolution_strategy.py
```

Updated runtime file:

```text
aigol/runtime/resolution_strategy_runtime.py
```

Implemented tests:

```text
tests/test_governance_resolution_strategy_v1.py
tests/test_resolution_strategy_runtime_v1.py
```

## Governance Prompt Detection

The runtime detects prompts including:

- `What governance exists?`
- `What was certified?`
- `Which milestone was completed?`
- `What governance guarantees exist?`
- `What ADRs define this capability?`
- `What is the status of a governance milestone?`

Detected prompts select:

```text
selected_strategy = GOVERNANCE
```

## Governance Answer Artifact

The runtime emits:

```text
GOVERNANCE_RESOLUTION_ARTIFACT_V1
```

It records:

- resolution id;
- strategy id and hash;
- selected strategy;
- human prompt reference;
- governance artifact references;
- evidence count;
- governance-backed answer text;
- non-authority, non-provider, non-worker, non-approval, and non-execution flags;
- artifact hash.

## Replay Events

The runtime records:

```text
GOVERNANCE_RESOLUTION_CREATED
GOVERNANCE_RESOLUTION_RETURNED
```

The nested strategy selection records:

```text
RESOLUTION_STRATEGY_SELECTED
RESOLUTION_STRATEGY_RETURNED
```

## Fail-Closed Cases

The runtime fails closed on:

- non-governance-oriented prompt;
- missing governance evidence;
- invalid governance references;
- corrupt governance artifacts;
- corrupt governance resolution replay;
- artifact hash mismatch;
- replay wrapper hash mismatch;
- invalid source references;
- invalid resolution references;
- replay ordering corruption.

## Boundary Guarantees

The runtime preserves:

```text
reference_only = true
authority = false
provider_used = false
worker_invoked = false
execution_requested = false
approval_created = false
```

No provider inference is used for governance truth.

No worker is invoked.

No approval is changed.

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
| LLM proposes | Provider inference is not required for governance answers |
| AiGOL governs | AiGOL selects `GOVERNANCE` and validates governance evidence |
| Worker executes | Worker execution is absent |
| Replay records | Replay records strategy selection and governance answer evidence |

## Validation

Focused validation:

```text
python -m pytest tests/test_resolution_strategy_runtime_v1.py tests/test_governance_resolution_strategy_v1.py
```

Result:

```text
38 passed
```

## Final Result

AiGOL can answer governance questions directly from governance artifacts.

```text
GOVERNANCE_RESOLUTION_STRATEGY_STATUS = CERTIFIED
```
