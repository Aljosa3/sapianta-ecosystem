# AIGOL_WORKER_INVOCATION_REPLAY_ARTIFACT_COMPATIBILITY_AUDIT_V1

## Status

Audit and certification milestone.

No fixes were implemented. No runtime changes were implemented. No ACLI changes were implemented. No replay changes were implemented. No worker changes were implemented. No architecture changes were implemented.

## Goal

Audit the replay compatibility contract between:

```text
WORKER_DISPATCHED
-> WORKER_INVOKED
```

## Observed Failure

Observed ACLI invocation:

```text
Invoke worker for FreshDomain.
```

routed correctly to:

```text
DOMAIN_WORKER_INVOCATION
```

and then failed closed:

```text
runtime artifact missing: 000_dispatch_evidence_recorded.json
```

The failed invocation replay recorded:

```text
worker_dispatch_replay_reference = MISSING_WORKER_DISPATCH_REPLAY
```

This means invocation did not receive a real worker-dispatch replay reference. The missing filename was looked up under the fallback sentinel path, not under an actual `worker_dispatch` replay directory.

## Dispatch Runtime Outputs

`AIGOL_WORKER_DISPATCH_RUNTIME_V1` produces replay under a `worker_dispatch` replay directory.

Required replay steps:

```text
000_dispatch_evidence_recorded.json
001_dispatch_classification_recorded.json
002_dispatch_artifact_recorded.json
003_dispatch_result_recorded.json
```

The dispatch runtime writes these files through:

```text
_persist_step(replay_path, 0, dispatch_evidence_recorded, ...)
_persist_step(replay_path, 1, dispatch_classification_recorded, ...)
_persist_step(replay_path, 2, dispatch_artifact_recorded, ...)
_persist_step(replay_path, 3, dispatch_result_recorded, ...)
```

Live replay inspection confirmed existing dispatch replay directories contain `000_dispatch_evidence_recorded.json`, for example:

```text
.aigol_conversation_runtime/AIGOL-INTERACTIVE-CONVERSATION-000001/TURN-000109/worker_dispatch/000_dispatch_evidence_recorded.json
```

## Invocation Runtime Inputs

`AIGOL_WORKER_INVOCATION_RUNTIME_V1` consumes:

```text
worker_dispatch_artifact
worker_dispatch_replay_reference
```

The invocation runtime reconstructs dispatch replay with:

```text
reconstruct_worker_dispatch_replay(worker_dispatch_replay_reference)
```

and then explicitly reads:

```text
000_dispatch_evidence_recorded.json
001_dispatch_classification_recorded.json
002_dispatch_artifact_recorded.json
003_dispatch_result_recorded.json
```

under the same dispatch replay reference.

## Compatibility Finding

The dispatch producer and invocation consumer agree on:

- replay directory type: `worker_dispatch`;
- evidence filename: `000_dispatch_evidence_recorded.json`;
- classification filename: `001_dispatch_classification_recorded.json`;
- dispatch artifact filename: `002_dispatch_artifact_recorded.json`;
- result filename: `003_dispatch_result_recorded.json`;
- reconstruction entry: `reconstruct_worker_dispatch_replay(...)`;
- status handoff: `WORKER_DISPATCHED` to `WORKER_INVOKED`.

Therefore the replay artifact contract is compatible when a real dispatch replay reference is supplied.

## Live Replay Finding

The live observed failure did not arise from a mismatch between dispatch output filenames and invocation expected filenames.

The failed invocation at:

```text
.aigol_conversation_runtime/AIGOL-INTERACTIVE-CONVERSATION-000001/TURN-000207/worker_invocation/003_invocation_result_recorded.json
```

recorded:

```text
worker_dispatch_replay_reference = MISSING_WORKER_DISPATCH_REPLAY
failure_reason = runtime artifact missing: 000_dispatch_evidence_recorded.json
```

The immediately preceding live turn inspected in the same session did not create a `worker_dispatch` replay directory. It routed through an older 19-workflow router snapshot:

```text
TURN-000206 workflow_id = DEFAULT_PROVIDER_ASSISTED_CONVERSATION
coverage_ratio = 19/19
```

No live `TURN-000206/worker_dispatch` replay artifact was present.

## Root Cause

The root cause is:

```text
missing consumable latest worker-dispatch replay for the observed FreshDomain session segment
```

The invocation ACLI branch failed to discover a matching dispatch replay and passed the fail-closed fallback reference:

```text
MISSING_WORKER_DISPATCH_REPLAY
```

The invocation runtime then correctly failed closed while trying to reconstruct dispatch lineage from that non-replay reference.

This is not an artifact naming mismatch. It is not a dispatch runtime output mismatch. It is not an invocation reconstruction contract mismatch when a real dispatch replay reference exists.

## Direct Runtime Reachability

Focused regression validation confirms direct runtime compatibility:

```text
python -m pytest tests/test_worker_dispatch_runtime_v1.py::test_worker_assigned_becomes_worker_dispatched tests/test_worker_invocation_runtime_v1.py::test_worker_dispatched_becomes_worker_invoked tests/test_domain_approval_entry_to_execution_ready_authorization_bridge_runtime_v1.py::test_find_latest_domain_worker_dispatch_excludes_invoked_entries tests/test_domain_approval_entry_to_execution_ready_authorization_bridge_runtime_v1.py::test_acli_worker_invocation_prompt_invokes_worker_without_execution_or_result_validation
```

Result:

```text
8 passed
```

## Certification

This audit certifies:

- dispatch replay artifacts are produced with the expected names;
- invocation expects the same artifact names;
- dispatch replay reconstruction is compatible with invocation runtime requirements;
- `WORKER_INVOKED` is reachable through direct runtime when supplied a real dispatch replay;
- the observed failure is caused by missing replay binding input, not by producer/consumer artifact naming incompatibility.

This audit does not certify:

- a new runtime;
- a new ACLI route;
- replay migration;
- worker execution;
- repair;
- retry;
- architecture redesign.

## Final Outputs

```text
DISPATCH_ARTIFACT_PRODUCED = TRUE
DISPATCH_ARTIFACT_EXPECTED = TRUE
ARTIFACT_NAME_MATCH = TRUE
ARTIFACT_LOCATION_MATCH = TRUE_WHEN_REAL_WORKER_DISPATCH_REPLAY_REFERENCE_SUPPLIED
REPLAY_REFERENCE_MATCH = FALSE_IN_OBSERVED_LIVE_FAILURE_TRUE_DIRECT_RUNTIME
REPLAY_RECONSTRUCTION_COMPATIBLE = TRUE_WHEN_REAL_WORKER_DISPATCH_REPLAY_REFERENCE_SUPPLIED
REPLAY_CONTRACT_COMPATIBLE = TRUE
WORKER_INVOKED_REACHABLE_DIRECT_RUNTIME = TRUE
ROOT_CAUSE_IDENTIFIED = TRUE
NEXT_BLOCKING_COMPONENT = LATEST_WORKER_DISPATCH_REPLAY_BINDING_FOR_OBSERVED_SESSION_STATE
RECOMMENDED_NEXT_MILESTONE = AIGOL_WORKER_INVOCATION_LATEST_DISPATCH_REPLAY_BINDING_FIX_V1
READY_FOR_REAL_WORKER_INVOCATION_ACCEPTANCE = FALSE_UNTIL_LIVE_SESSION_DISPATCH_REPLAY_BINDING_ACCEPTANCE_PASSES
```
