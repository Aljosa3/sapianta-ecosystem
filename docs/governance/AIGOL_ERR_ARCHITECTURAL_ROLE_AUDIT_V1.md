# AIGOL ERR Architectural Role Audit V1

Status: architecture audit.

Purpose: determine the true architectural role of ERR after provider and worker integration.

This artifact is an audit only.

It does not change ERR runtime behavior.

It does not add resource types.

It does not authorize invocation, routing, ranking, dispatch, governance, lifecycle management, or ELL.

## Audited Scope

The audit reviews ERR after:

```text
AIGOL_ERR_V0
AIGOL_ERR_OCS_INTEGRATION_V1
AIGOL_WORKER_RESOURCE_SELECTION_V1
AIGOL_REAL_PROVIDER_REGISTRATION_V1
AIGOL_ERR_SHARED_INFRASTRUCTURE_SCOPE_LOCK_V1
```

The implemented ERR runtime supports only:

```text
COGNITION_PROVIDER
EXECUTION_WORKER
```

The implemented ERR schema remains:

```text
resource_id
resource_type
capabilities
status
```

## Current ERR Runtime Surface

Runtime:

- `aigol/runtime/external_resource_registry_runtime.py`

Core functions:

- `create_err_v0_registry`
- `register_resource`
- `get_resource_by_id`
- `find_resources_by_capability`
- `select_resource_for_capability`
- `reconstruct_err_v0_selection_replay`
- `default_err_v0_registry`
- `real_provider_err_v1_registry`
- `register_real_cognition_providers`

Supported resource types:

- `COGNITION_PROVIDER`
- `EXECUTION_WORKER`

Supported statuses:

- `ACTIVE`
- `INACTIVE`

Supported selection semantics:

```text
required_capability
optional resource_type
ACTIVE filtering
first active matching resource
replay-visible selection evidence
```

Unsupported semantics:

- provider invocation;
- worker invocation;
- dispatch;
- authorization;
- governance;
- ranking;
- optimization;
- scheduling;
- orchestration;
- lifecycle management;
- marketplace behavior;
- ELL runtime behavior.

## Current ERR Consumers

### 1. HIRR Demonstration Path

Runtime:

- `demonstrate_err_v0_hirr_to_resource_selection(...)`

Pattern:

```text
Human Intent
-> HIRR output
-> required_capability
-> ERR capability lookup
-> replay-visible selection evidence
```

Resource type:

- supplied by HIRR output when present.

Architectural role:

- passive capability-to-resource evidence.

### 2. OCS Cognition Workflow

Runtime:

- `aigol/runtime/ocs_llm_cognition_end_to_end_runtime.py`

Integration controls:

- `use_err_resource_lookup=True`
- `err_required_capability="reasoning"`
- optional `err_registry`

Pattern:

```text
OCS requests reasoning
-> ERR selects active COGNITION_PROVIDER
-> OCS derives provider contract
-> OCS continues cognition workflow
-> replay records ERR selection
```

Evidence:

- `tests/test_ocs_llm_cognition_end_to_end_runtime_v1.py`
- `docs/governance/AIGOL_ERR_OCS_INTEGRATION_V1.md`

Resource type:

- `COGNITION_PROVIDER`

Selected test resource:

- `mock_provider`

Real-provider path:

- `real_provider_err_v1_registry()` registers `openai`, `claude`, `gemini`, and `mistral` as `COGNITION_PROVIDER`.

Architectural role:

- provider metadata lookup for cognition workflows.

Boundary:

- OCS remains orchestration.
- ERR does not invoke providers.

### 3. First Real Provider Runtime Validation

Runtime:

- `aigol/runtime/first_real_provider_runtime.py`

Pattern:

```text
required_capability = reasoning
-> ERR selects openai
-> canonical provider contract
-> deterministic mock provider response
-> LLM_COGNITION_ARTIFACT_V1
-> replay evidence
```

Resource type:

- `COGNITION_PROVIDER`

Selected resource:

- `openai`

Architectural role:

- real provider metadata lookup before governed provider-runtime validation.

Boundary:

- ERR selection is not approval.
- ERR selection is not invocation.
- OpenAI is not called by ERR.

### 4. Worker Assignment Workflow

Runtime:

- `aigol/runtime/worker_assignment_runtime.py`

Integration controls:

- `use_err_worker_lookup=True`
- `err_required_capability="file_write"`
- optional `err_registry`

Pattern:

```text
Worker invocation request
-> worker assignment runtime
-> required_capability = file_write
-> ERR selects active EXECUTION_WORKER
-> worker assignment compatibility checks
-> assignment replay evidence
```

Evidence:

- `tests/test_worker_assignment_runtime_v1.py`
- `docs/governance/AIGOL_WORKER_RESOURCE_SELECTION_V1.md`

Resource type:

- `EXECUTION_WORKER`

Selected test resource:

- `mock_filesystem_worker`

Architectural role:

- worker metadata lookup for assignment workflows.

Boundary:

- worker assignment remains the assignment surface.
- ERR does not dispatch, invoke, execute, or authorize workers.

## Provider Use Cases

Provider-facing ERR use cases are:

1. register mock cognition provider metadata;
2. register real cognition provider metadata;
3. look up provider by `resource_id`;
4. search providers by capability;
5. filter inactive providers;
6. select a provider with replay-visible evidence;
7. allow OCS to replace hardcoded provider contract selection with capability lookup;
8. allow the first real provider runtime to select `openai` metadata through ERR.

Provider capabilities currently include:

- `reasoning`
- `planning`
- `summarization`
- `analysis`
- `generation`

Provider selection pattern:

```text
required_capability
resource_type = COGNITION_PROVIDER
status = ACTIVE
```

## Worker Use Cases

Worker-facing ERR use cases are:

1. register mock execution worker metadata;
2. search workers by capability;
3. filter inactive workers;
4. select a worker with replay-visible evidence;
5. let worker assignment resolve `mock_filesystem_worker` without hardcoded worker references.

Worker capabilities currently include:

- `file_write`

Worker selection pattern:

```text
required_capability
resource_type = EXECUTION_WORKER
status = ACTIVE
```

## Capability-Selection Patterns

Current common pattern:

```text
consumer workflow
-> required_capability
-> resource_type fence
-> ERR ACTIVE filtering
-> selected resource metadata
-> replay-visible selection evidence
-> consumer-specific governance continues outside ERR
```

Observed provider example:

```text
reasoning
-> COGNITION_PROVIDER
-> mock_provider or openai
```

Observed worker example:

```text
file_write
-> EXECUTION_WORKER
-> mock_filesystem_worker
```

Architectural interpretation:

The common abstraction is not "provider" and not "worker".

The common abstraction is:

```text
resource metadata selected by capability under a resource-type boundary
```

## Candidate Role Evaluation

### PROVIDER_REGISTRY

Fit:

- ERR registers and selects cognition providers.
- Real providers are registered as metadata.
- OCS cognition and first-provider runtime use ERR for provider metadata selection.

Insufficient because:

- ERR also registers and selects execution workers.
- Worker assignment uses ERR with `resource_type = EXECUTION_WORKER`.
- The schema and selection functions are not provider-specific.

Verdict:

```text
PROVIDER_REGISTRY = TOO_NARROW
```

### WORKER_REGISTRY

Fit:

- ERR registers and selects execution workers.
- Worker assignment uses ERR for `file_write`.

Insufficient because:

- ERR also registers and selects cognition providers.
- OCS cognition and first real provider validation depend on provider capability lookup.
- Real provider registration is an implemented milestone.

Verdict:

```text
WORKER_REGISTRY = TOO_NARROW
```

### UNIVERSAL_RESOURCE_REGISTRY

Fit:

- ERR supports multiple resource types.
- ERR has a neutral resource schema.
- ERR selection is capability-based rather than provider-specific or worker-specific.
- ERR consumers include HIRR path, OCS cognition, first real provider validation, and worker assignment.
- ERR records replay-visible evidence independent of the consumer workflow.

Required constraint:

`UNIVERSAL_RESOURCE_REGISTRY` must be interpreted narrowly.

It means:

```text
passive registry for currently governed resource metadata classes
```

It does not mean:

```text
unbounded resource marketplace
universal runtime dispatcher
universal lifecycle manager
universal execution fabric
ELL
```

Verdict:

```text
UNIVERSAL_RESOURCE_REGISTRY = BEST_FIT_WITH_SCOPE_LOCK
```

## Architectural Implications

ERR is no longer accurately described as only a provider registry or only a worker registry.

The implemented architecture shows ERR as a shared resource lookup substrate.

Implications:

1. Consumers should pass an explicit `resource_type`.
2. Capabilities should remain simple strings unless a governed extension proves otherwise.
3. Provider and worker semantics must remain outside ERR.
4. OCS remains responsible for cognition orchestration.
5. Worker assignment remains responsible for worker compatibility and assignment.
6. ERR selection remains metadata selection only.
7. Replay evidence remains selection evidence, not execution evidence.

The safe architecture is:

```text
ERR = passive universal resource metadata registry
OCS = cognition orchestration
Worker assignment = execution-worker assignment gate
Provider runtimes = governed cognition invocation surfaces
Replay = evidence continuity
Governance = authority and validation
```

## Governance Implications

The universal role increases the importance of the scope lock.

Governance requirements:

- every ERR consumer must declare intended `resource_type`;
- ERR must fail closed on invalid resource types;
- inactive resources must remain excluded;
- ERR must not infer authority from selection;
- ERR must not invoke providers;
- ERR must not invoke workers;
- ERR must not rank, optimize, dispatch, schedule, or govern;
- ERR must not mutate replay history;
- ERR must not become ELL.

Selection evidence must continue to record:

- selected resource id;
- selected resource type;
- required capability;
- active match count;
- active resource ids;
- registry hash;
- provider invoked false;
- worker invoked false;
- orchestration performed false;
- governance modified false;
- replay visible true.

Governance interpretation:

```text
ERR selection = admissible metadata evidence
ERR selection != approval
ERR selection != authorization
ERR selection != invocation
ERR selection != dispatch
ERR selection != execution
```

## Future Extensibility Implications

ERR can safely remain extensible only if future changes are governed.

Allowed future direction:

- additional capabilities for existing resource types;
- additional provider metadata only if schema expansion is approved;
- additional worker metadata only if schema expansion is approved;
- additional consumers only if they preserve passive lookup and fail-closed behavior.

High-risk future direction:

- adding new resource types without governance;
- adding status values beyond `ACTIVE` and `INACTIVE`;
- adding ranking or scoring;
- adding provider comparison;
- adding cost or latency optimization;
- adding routing;
- adding autonomous discovery;
- adding lifecycle state machines;
- adding invocation handles;
- adding credential or transport fields;
- merging ERR with ELL.

Future extension rule:

Any new ERR capability, resource type, field, status, consumer, selection rule, or replay evidence expansion must pass governance review and tests proving:

- existing provider lookup remains replay-visible;
- existing worker lookup remains replay-visible;
- inactive resources remain excluded;
- ERR remains passive;
- no invocation, dispatch, authorization, governance mutation, ranking, optimization, lifecycle management, or replay mutation is introduced.

## Evidence Summary

Runtime evidence:

- `aigol/runtime/external_resource_registry_runtime.py` defines both `COGNITION_PROVIDER` and `EXECUTION_WORKER`.
- `default_err_v0_registry()` registers both `mock_provider` and `mock_filesystem_worker`.
- `real_provider_err_v1_registry()` registers real cognition provider metadata.
- `select_resource_for_capability(...)` is resource-type neutral.
- OCS cognition calls ERR with `resource_type=COGNITION_PROVIDER`.
- worker assignment calls ERR with `resource_type=EXECUTION_WORKER`.
- first real provider validation calls ERR with `resource_type=COGNITION_PROVIDER`.

Test evidence:

- `tests/test_external_resource_registry_runtime_v0.py`
- `tests/test_ocs_llm_cognition_end_to_end_runtime_v1.py`
- `tests/test_worker_assignment_runtime_v1.py`
- `tests/test_real_provider_registration_v1.py`
- `tests/test_first_real_provider_runtime_v1.py`

Validation:

```text
python -m pytest \
  tests/test_external_resource_registry_runtime_v0.py \
  tests/test_ocs_llm_cognition_end_to_end_runtime_v1.py \
  tests/test_worker_assignment_runtime_v1.py \
  tests/test_real_provider_registration_v1.py \
  tests/test_first_real_provider_runtime_v1.py

56 passed
```

Governance evidence:

- `AIGOL_ERR_OCS_INTEGRATION_V1`
- `AIGOL_WORKER_RESOURCE_SELECTION_V1`
- `AIGOL_REAL_PROVIDER_REGISTRATION_V1`
- `AIGOL_ERR_SHARED_INFRASTRUCTURE_SCOPE_LOCK_V1`
- `AIGOL_ELL_DEFERRED_V1`

## Final Verdict

ERR's true architectural role is:

```text
ERR_ROLE = UNIVERSAL_RESOURCE_REGISTRY
```

Bounded interpretation:

```text
UNIVERSAL_RESOURCE_REGISTRY =
passive capability-based registry for governed resource metadata,
currently limited to COGNITION_PROVIDER and EXECUTION_WORKER.
```

Rejected interpretations:

```text
ERR_ROLE = PROVIDER_REGISTRY
ERR_ROLE = WORKER_REGISTRY
```

Reason:

Provider registry and worker registry are both valid sub-roles, but neither fully describes the implemented shared abstraction.

## Recommendation

Adopt `UNIVERSAL_RESOURCE_REGISTRY` as the architectural role label for ERR, with an explicit bounded qualifier:

```text
PASSIVE UNIVERSAL RESOURCE REGISTRY
```

Do not broaden ERR runtime authority.

Do not add resource types or lifecycle semantics without a governed milestone.

Keep provider and worker governance separate:

```text
ERR resolves metadata.
OCS orchestrates cognition.
Worker assignment gates workers.
Governance authorizes.
Replay records.
```
