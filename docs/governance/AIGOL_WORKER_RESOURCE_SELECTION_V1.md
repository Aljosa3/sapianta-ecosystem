# AIGOL_WORKER_RESOURCE_SELECTION_V1

Status: implemented integration milestone.

Purpose: validate that ERR_V0 can resolve execution workers through capability lookup in a real worker assignment workflow.

## Worker Selection Point

The selected integration point is:

- `aigol/runtime/worker_assignment_runtime.py`

The worker assignment runtime previously selected a compatible worker from direct `worker_registry_artifacts`. That legacy path remains available. The new ERR path is activated explicitly with:

- `use_err_worker_lookup=True`
- `err_required_capability="file_write"`
- optional `err_registry`

## Runtime Flow

The ERR-backed worker selection flow is:

```text
Worker invocation request
-> worker assignment runtime
-> required_capability = file_write
-> ERR_V0 lookup for EXECUTION_WORKER
-> mock_filesystem_worker selected
-> worker assignment compatibility checks
-> assignment replay evidence recorded
```

ERR does not dispatch, invoke, execute, authorize, schedule, rank, or optimize the worker. It only resolves passive metadata and records replay-visible selection evidence.

## Replay Evidence

The worker assignment replay directory now includes an optional nested stage when ERR lookup is enabled:

```text
stages/err_worker_selection/
```

Worker assignment reconstruction exposes:

- `err_worker_selection_enabled`
- `err_selected_resource_id`
- `err_required_capability`
- `err_worker_selection_replay`

The replay proves that `file_write` resolved to `mock_filesystem_worker` while provider invocation, worker invocation, orchestration, governance mutation, and replay mutation remained false.

## Boundary Preservation

This milestone preserves:

- OCS and worker assignment as orchestration/assignment surfaces;
- ERR as passive resource metadata and selection evidence;
- workers as execution-only resources;
- no provider-to-worker invocation;
- no worker-to-provider invocation;
- fail-closed behavior;
- replay visibility;
- no lifecycle engines or ELL.

## Evidence

Validation proves:

- a real worker assignment workflow can request `file_write`;
- ERR resolves `mock_filesystem_worker`;
- the existing worker compatibility validator still gates assignment;
- replay records ERR worker selection;
- assignment fails closed when no active execution worker matches the capability.

## Recommendation

ERR is becoming shared infrastructure, but only in a narrow sense: it is a shared passive resource lookup and replay-evidence substrate for both cognition providers and execution workers.

ERR should not become orchestration, lifecycle management, ELL, marketplace logic, ranking, dispatch, or execution. The safe direction is to keep ERR as a common resource metadata boundary while preserving separate OCS cognition orchestration and worker execution governance.
