# G18-07 Runtime Status Replay Discovery Binding Implementation

## Executive Summary

G18-07 implements the smallest deterministic replay discovery binding for Human Interface runtime status projection.

The Human Interface no longer depends only on flattened latest-turn fields or explicit replay references for Worker and provider reachability. `_runtime_status_projection(...)` now discovers the current `TURN-*` replay root from existing turn references and inspects existing replay artifacts under the governed Worker lifecycle tree.

No replay structure, Platform Core behavior, Universal Provider Runtime behavior, Worker Platform behavior, Provider Platform behavior, Governance behavior, or Replay behavior was redesigned.

Final verdict: `REPLAY_DISCOVERY_BINDING_IMPLEMENTED`.

## Implemented Binding

Implementation source:

- `aigol/runtime/human_interface_runtime_entry_service.py`
- `_runtime_status_projection(...)`
- `_discover_turn_replay_root(...)`
- `_nearest_turn_replay_root(...)`
- `_read_replay_artifact_path(...)`

The projection now:

1. Preserves latest-turn flattened field projection.
2. Preserves explicit replay-reference projection.
3. Discovers the current turn replay root from existing replay reference fields.
4. Reads existing Worker lifecycle and Universal Provider Worker replay artifacts under the discovered turn root.
5. Projects runtime status from the complete discovered evidence set.

## Replay Discovery Sources

The binding derives the current turn root from existing latest-turn references:

- `replay_reference`;
- `conversation_replay_reference`;
- `runtime_replay_reference`;
- `universal_provider_worker_replay_reference`;
- `replay_certification_replay_reference`;
- `execution_summary_reference`;
- `human_confirmation_reference`.

The helper walks upward from each candidate until it finds a `TURN-*` directory or an existing directory that contains turn replay structure such as:

- `governed_bridge_certified_development_continuation`;
- `source_router`;
- `turn_completion`.

This is discovery only. It does not create or mutate replay artifacts.

## Inspected Replay Artifacts

When a current turn root is discovered, projection now inspects:

- `governed_bridge_certified_development_continuation/worker_lifecycle_continuation/worker_invocation/003_invocation_result_recorded.json`;
- `governed_bridge_certified_development_continuation/worker_lifecycle_continuation/universal_provider_worker/000_universal_provider_worker_binding_recorded.json`;
- `governed_bridge_certified_development_continuation/worker_lifecycle_continuation/universal_provider_worker/001_universal_provider_worker_result_recorded.json`;
- `governed_bridge_certified_development_continuation/worker_lifecycle_continuation/universal_provider_worker/universal_resource_selection/001_resource_selection_returned.json`;
- `governed_bridge_certified_development_continuation/worker_lifecycle_continuation/universal_provider_worker/selected_provider_openai/001_openai_provider_adapter_recorded.json`;
- `governed_bridge_certified_development_continuation/worker_lifecycle_continuation/universal_provider_worker/selected_provider_openai/002_openai_external_worker_result_recorded.json`;
- `governed_bridge_certified_development_continuation/worker_lifecycle_continuation/universal_provider_worker/selected_provider_openai/certified_provider_attachment/002_certified_provider_attachment_recorded.json`;
- `governed_bridge_certified_development_continuation/worker_lifecycle_continuation/replay_certification/000_replay_certification_artifact_recorded.json`.

## Runtime Projection Semantics

Worker execution is now projected from discovered Worker lifecycle replay when:

- `worker_invoked` is `true`; or
- `invocation_status` is `WORKER_INVOKED`.

Provider invocation is now projected from discovered Universal Provider replay when evidence shows:

- Universal Provider Worker binding;
- Universal Resource Selection success;
- selected provider adapter reachability;
- OpenAI external Worker provider result capture;
- Certified Provider Attachment reachability.

Replay certification remains projected only from existing replay certification evidence:

- flattened latest-turn replay certification fields;
- explicit replay certification reference;
- discovered replay certification artifact under the current Worker lifecycle replay tree.

If a turn contains Worker and provider evidence but no replay certification artifact, the projection can prove Worker and provider reachability while preserving a partial runtime binding for replay certification.

## Deterministic Evidence

The runtime result now exposes projection evidence fields, including:

- `turn_replay_discovery_used`;
- `turn_replay_root`;
- `worker_lifecycle_replay_root`;
- `worker_invocation_replay_inspected`;
- `universal_provider_worker_binding_replay_inspected`;
- `universal_provider_worker_replay_inspected`;
- `resource_selection_replay_inspected`;
- `selected_provider_replay_inspected`;
- `openai_worker_result_replay_inspected`;
- `certified_provider_attachment_replay_inspected`;
- `replay_certification_replay_inspected`;
- `worker_invocation_status`;
- `selected_provider_resource_id`;
- `resource_selection_status`;
- `selected_provider_status`;
- `certified_provider_attachment_status`;
- `replay_certification_status`.

This makes the Human Interface projection source auditable without changing replay layout.

## Validation

Regression test added:

- `tests/test_g14_30_canonical_human_interface_runtime_entry_service_v1.py::test_canonical_runtime_entry_discovers_status_from_current_turn_replay_tree`

The test withholds explicit Universal Provider Worker and replay certification references from the flattened latest turn, writes existing replay artifacts under a temporary `TURN-000023` tree, and verifies that Human Interface projection derives:

- `provider_invocation_reached = true`;
- `worker_execution_reached = true`;
- `replay_certification_reached = true`;
- `canonical_runtime_entry_status = CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_BOUND`;
- replay discovery evidence flags for Worker invocation, Universal Provider Worker, resource selection, selected provider, Certified Provider Attachment, and replay certification.

Validation command:

```bash
python -m pytest tests/test_g14_30_canonical_human_interface_runtime_entry_service_v1.py
```

Result:

```text
7 passed
```

Additional scoped validation:

```bash
python -m pytest tests/test_g14_30_canonical_human_interface_runtime_entry_service_v1.py tests/test_g15_runtime_06_governed_development_runtime_continuation.py tests/test_acli_certified_continuation_orchestration_v1.py tests/test_universal_provider_worker_runtime_v1.py
```

Result:

```text
14 passed
```

## Architectural Conclusions

The G18-06 root cause was replay discovery, not runtime execution.

G18-07 binds Human Interface runtime projection to the existing current-turn replay tree. The Human Interface remains a projection layer: it does not own provider selection, Worker execution, replay certification, or replay artifact shape.

The binding preserves fail-closed semantics because absent artifacts do not synthesize success. They only leave the corresponding projection field false.

## Final Recommendation

Retain this replay discovery binding as the Human Interface source-of-truth bridge for current-turn runtime projection.

Future provider additions should add equivalent selected-provider artifact discovery paths only when their replay shape is certified.

## Final Verdict

`REPLAY_DISCOVERY_BINDING_IMPLEMENTED`
