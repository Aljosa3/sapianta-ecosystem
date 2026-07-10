# G18-06 Runtime Status Projection Source Audit

## Executive Summary

G18-06 audits the current Human Interface runtime projection source of truth after G18-03 and G18-05.

The audit confirms a projection source binding gap.

`_runtime_status_projection(...)` currently uses:

- flattened latest-turn fields;
- `universal_provider_worker/001_universal_provider_worker_result_recorded.json`, but only when the latest turn already exposes `universal_provider_worker_replay_reference`;
- `replay_certification/000_replay_certification_artifact_recorded.json`, but only when the latest turn already exposes `replay_certification_replay_reference`.

It does not discover replay artifacts from the turn replay directory. It does not inspect Universal Resource Selection replay, selected-provider OpenAI replay, Certified Provider Attachment replay, Worker lifecycle replay, or turn completion replay.

TURN-000023 contains Worker lifecycle, Universal Provider Worker, Universal Resource Selection, selected OpenAI provider adapter, and Certified Provider Attachment artifacts. Those artifacts are not used by `_runtime_status_projection(...)` unless the latest-turn summary already contains the narrow replay references that the helper expects.

Final verdict: `PROJECTION_SOURCE_BINDING_GAP_CONFIRMED`.

## Current Projection Source Review

Implementation source:

- `aigol/runtime/human_interface_runtime_entry_service.py`
- `_runtime_status_projection(conversation_result, latest_turn)`

The runtime entry path is:

1. `run_human_interface_runtime_entry(...)` calls the governed runtime and receives `conversation_result`.
2. `_latest_turn(conversation_result)` selects one flattened latest turn.
3. `_runtime_status_projection(...)` derives provider, Worker, and replay-certification status.
4. `_runtime_bound(...)` uses the derived projection.
5. The Reference UHI reports the canonical result.

The projection helper currently reads exactly two replay artifacts:

```python
_read_replay_artifact(
    latest_turn.get("universal_provider_worker_replay_reference"),
    "001_universal_provider_worker_result_recorded.json",
)
```

and:

```python
_read_replay_artifact(
    latest_turn.get("replay_certification_replay_reference"),
    "000_replay_certification_artifact_recorded.json",
)
```

If the latest turn does not contain those replay-reference fields, no replay search occurs.

## Replay Artifact Inventory

TURN-000023 local replay root:

```text
.runtime/aicli/AICLI-REFERENCE-SESSION/TURN-000023
```

Relevant artifacts present:

```text
governed_bridge_certified_development_continuation/
  worker_lifecycle_continuation/
    worker_invocation/
      003_invocation_result_recorded.json
    universal_provider_worker/
      000_universal_provider_worker_binding_recorded.json
      001_universal_provider_worker_result_recorded.json
      universal_resource_selection/
        000_resource_selection_recorded.json
        001_resource_selection_returned.json
      selected_provider_openai/
        000_openai_external_worker_task_recorded.json
        001_openai_provider_adapter_recorded.json
        002_openai_external_worker_result_recorded.json
        003_openai_external_worker_returned.json
        certified_provider_attachment/
          000_provider_proposal_created.json
          000_provider_readiness_recorded.json
          001_provider_proposal_returned.json
          002_certified_provider_attachment_recorded.json
```

TURN-000023 replay certification inventory:

```text
No replay_certification directory exists under TURN-000023.
```

This means TURN-000023 proves Worker lifecycle and selected-provider reachability, but does not prove replay certification completion for that turn.

## Used Projection Sources

`_runtime_status_projection(...)` currently uses the following latest-turn flattened fields:

- `universal_provider_worker_status`;
- `smart_provider_selection_executed`;
- `smart_provider_selection_reached`;
- `universal_provider_runtime_reached`;
- `openai_provider_reached`;
- `provider_invoked`;
- `provider_invocation_reached`;
- `worker_invoked`;
- `worker_invocation_reached`;
- `worker_execution_candidate_reached`;
- `external_task_package_reached`;
- `worker_invocation_status`;
- `replay_certification_reached`;
- `replay_certification_status`;
- `selected_provider_resource_id`;
- `universal_provider_worker_replay_reference`;
- `replay_certification_replay_reference`.

It uses the following Universal Provider Worker result artifact fields when the latest turn supplies `universal_provider_worker_replay_reference`:

- `universal_provider_worker_status`;
- `smart_selection_executed`;
- `provider_invocation_delegated`;
- `certified_provider_attachment_reused`;
- `selected_resource_id`.

It uses the following replay certification artifact field when the latest turn supplies `replay_certification_replay_reference`:

- `certification_status`.

## Ignored Projection Sources

The current helper does not inspect these existing TURN-000023 artifacts:

- `universal_provider_worker/000_universal_provider_worker_binding_recorded.json`;
- `universal_provider_worker/universal_resource_selection/000_resource_selection_recorded.json`;
- `universal_provider_worker/universal_resource_selection/001_resource_selection_returned.json`;
- `universal_provider_worker/selected_provider_openai/000_openai_external_worker_task_recorded.json`;
- `universal_provider_worker/selected_provider_openai/001_openai_provider_adapter_recorded.json`;
- `universal_provider_worker/selected_provider_openai/002_openai_external_worker_result_recorded.json`;
- `universal_provider_worker/selected_provider_openai/003_openai_external_worker_returned.json`;
- `universal_provider_worker/selected_provider_openai/certified_provider_attachment/*`;
- `worker_lifecycle_continuation/worker_invocation/*`;
- `worker_lifecycle_continuation/worker_assignment/*`;
- `worker_lifecycle_continuation/worker_dispatch/*`;
- `worker_lifecycle_continuation/worker_execution_candidate/*`;
- `turn_completion/000_turn_completed.json`;
- `turn_completion/001_result_delivered.json`.

It also does not derive a missing `universal_provider_worker_replay_reference` from `runtime_replay_reference`, `conversation_replay_reference`, `TURN-000023`, or the governed bridge continuation directory.

## Worker Execution Projection Analysis

TURN-000023 Worker lifecycle evidence:

```text
worker_lifecycle_continuation/worker_invocation/003_invocation_result_recorded.json
artifact_type: WORKER_INVOCATION_RESULT_ARTIFACT_V1
runtime_version: AIGOL_WORKER_INVOCATION_RUNTIME_V1
invocation_status: WORKER_INVOKED
worker_invoked: true
failure_reason: null
```

This is deterministic Worker lifecycle evidence.

Current projection logic can report Worker execution only from:

- latest-turn `worker_invoked`;
- latest-turn `worker_invocation_reached`;
- latest-turn `worker_execution_candidate_reached`;
- latest-turn `external_task_package_reached`;
- latest-turn `worker_invocation_status == WORKER_INVOKED`;
- Universal Provider Worker result status `UNIVERSAL_PROVIDER_WORKER_COMPLETED`.

It does not read `worker_invocation/003_invocation_result_recorded.json`.

TURN-000023 Universal Provider Worker result:

```text
universal_provider_worker_status: FAILED_CLOSED
failure_reason: OpenAI provider unavailable
```

Therefore, if the flattened latest turn does not expose Worker lifecycle fields, `_runtime_status_projection(...)` has no direct replay source to prove `worker_execution_reached = true`, even though Worker invocation replay exists.

## Provider Invocation Projection Analysis

TURN-000023 Universal Resource Selection evidence:

```text
selection_status: RESOURCE_SELECTION_SUCCEEDED
selected_resource_id: OPENAI
selected_role_type: PROVIDER_ROLE
```

TURN-000023 selected provider adapter evidence:

```text
artifact_type: OPENAI_EXTERNAL_WORKER_PROVIDER_CAPTURE_ARTIFACT_V1
runtime_version: AIGOL_OPENAI_EXTERNAL_WORKER_PROVIDER_ADAPTER_V1
provider_adapter_runtime: OPENAI_PROVIDER_ADAPTER_V1
provider_invoked_inside_adapter: true
provider_status: FAILED_CLOSED
failure_reason: OpenAI provider unavailable
```

TURN-000023 Certified Provider Attachment evidence:

```text
artifact_type: CERTIFIED_PROVIDER_ATTACHMENT_ARTIFACT_V1
runtime_version: G14_44_CERTIFIED_PROVIDER_ATTACHMENT_V1
provider_status: FAILED_CLOSED
provider_invoked: false
failure_reason: OpenAI provider unavailable
```

This proves:

- Universal Provider Runtime selected a provider.
- The selected provider adapter was reached.
- Certified Provider Attachment was reached.
- External provider transport did not successfully invoke; it failed closed.

Current projection logic does not inspect:

- `001_resource_selection_returned.json`;
- `001_openai_provider_adapter_recorded.json`;
- `002_openai_external_worker_result_recorded.json`;
- `certified_provider_attachment/002_certified_provider_attachment_recorded.json`.

The helper can infer provider reachability from `001_universal_provider_worker_result_recorded.json` if and only if the latest turn supplies `universal_provider_worker_replay_reference`. If the latest turn omits that field, the selected-provider replay present in TURN-000023 is invisible to the projection.

## Replay Certification Projection Analysis

Current projection logic can report replay certification from:

- latest-turn `replay_certification_reached`;
- latest-turn `replay_certification_status == REPLAY_CERTIFICATION_COMPLETED`;
- `replay_certification/000_replay_certification_artifact_recorded.json` when latest-turn `replay_certification_replay_reference` is present.

TURN-000023 has no replay certification directory.

Therefore, for TURN-000023, replay certification cannot be certified from local replay artifacts. The correct projection for replay certification for this turn is not proven by replay certification artifacts.

This does not invalidate Worker lifecycle or selected-provider reachability evidence. It means replay certification projection and Worker/provider reachability projection must remain distinct.

## Root Cause

The Human Interface still reports `worker_execution_reached = false` and `provider_invocation_reached = false` when replay contains Universal Provider Worker and selected-provider evidence because `_runtime_status_projection(...)` is not a turn-directory replay reconstructor.

The deterministic root causes are:

1. The helper only receives `conversation_result` and one flattened `latest_turn`.
2. The helper only reads replay files through replay-reference fields already present on `latest_turn`.
3. If `latest_turn` does not expose `universal_provider_worker_replay_reference`, the helper does not discover `TURN-000023/.../universal_provider_worker`.
4. If `latest_turn` does not expose Worker lifecycle booleans, the helper does not inspect `worker_invocation/003_invocation_result_recorded.json`.
5. The helper does not inspect selected-provider or Certified Provider Attachment artifacts, so selected-provider adapter reachability is not projected unless summarized elsewhere.
6. TURN-000023 Universal Provider Worker result is `FAILED_CLOSED`; the helper treats only `UNIVERSAL_PROVIDER_WORKER_COMPLETED` as Worker completion evidence.

In short:

```text
Replay evidence exists,
but the projection helper does not bind to the replay artifact paths that contain it.
```

## Minimal Binding Recommendation

Do not redesign Human Interface, Replay, Worker Platform, Provider Platform, Universal Provider Runtime, or Governance.

The smallest deterministic binding is to extend Human Interface projection source discovery so it can derive replay paths from the current turn replay root and inspect existing artifacts.

Recommended additions:

1. Derive a turn replay root from `latest_turn["runtime_replay_reference"]`, `latest_turn["replay_reference"]`, or `latest_turn["conversation_replay_reference"]`.
2. Probe the governed bridge continuation path:

```text
governed_bridge_certified_development_continuation/
  worker_lifecycle_continuation/
```

3. Bind Worker projection to:

```text
worker_invocation/003_invocation_result_recorded.json
```

4. Bind provider-stage projection to:

```text
universal_provider_worker/000_universal_provider_worker_binding_recorded.json
universal_provider_worker/universal_resource_selection/001_resource_selection_returned.json
universal_provider_worker/selected_provider_openai/001_openai_provider_adapter_recorded.json
universal_provider_worker/selected_provider_openai/certified_provider_attachment/002_certified_provider_attachment_recorded.json
```

5. Keep external provider transport invocation separate from selected-provider adapter reachability:

```text
selected provider reached != external provider transport succeeded
```

6. Continue to require replay certification artifacts for `replay_certification_reached = true`.

## Final Verdict

`PROJECTION_SOURCE_BINDING_GAP_CONFIRMED`
