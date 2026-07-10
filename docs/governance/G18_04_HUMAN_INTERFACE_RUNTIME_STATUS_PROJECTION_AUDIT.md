# G18-04 Human Interface Runtime Status Projection Audit

## Executive Summary

The Human Interface runtime status mismatch is a projection binding issue.

The certified runtime path now reaches:

- Universal Provider Worker Runtime;
- Universal Resource Selection;
- selected provider execution;
- Certified Provider Attachment;
- result validation;
- replay certification.

However, the Reference Human Interface does not compute its rendered runtime summary by reconstructing or inspecting those replay artifacts. `run_human_interface_runtime_entry(...)` calls the governed runtime, selects one flattened latest turn, and projects `runtime_status`, `worker_execution_reached`, `provider_invocation_reached`, and `replay_certification_reached` from a small set of fields on that latest turn.

If the latest turn projection omits or misnames certified continuation evidence, the Human Interface reports partial binding even when deeper replay evidence proves the stages were reached.

Final verdict: `HUMAN_INTERFACE_RUNTIME_STATUS_PROJECTION_REUSE_WITH_MINOR_BINDING`.

## Current Runtime Projection

`aigol/cli/aicli.py` delegates runtime execution to `run_human_interface_runtime_entry(...)` and then renders whatever fields the canonical runtime entry returns.

Implementation evidence:

- Interactive approval computes `runtime_status = _reference_runtime_status(runtime_result)` after runtime entry returns.
- Submit-mode approval does the same.
- `_reference_runtime_status(...)` maps only canonical status:
  - `CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_BOUND` -> `REFERENCE_UHI_RUNTIME_BOUND`;
  - `CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_NOT_REQUIRED` -> `REFERENCE_UHI_RUNTIME_NOT_REQUIRED`;
  - anything else -> `REFERENCE_UHI_RUNTIME_PARTIALLY_BOUND`.
- `_render_runtime_result(...)` prints `provider_invocation_reached`, `worker_execution_reached`, and `replay_certification_reached` directly from `runtime_result`.

Therefore `aicli` does not independently inspect Worker, Provider, Universal Provider Runtime, or Replay evidence. It is a presenter for the canonical Human Interface runtime entry projection.

## Replay Evidence Review

G18-03 replay-producing implementation evidence:

- `_continue_worker_request_to_replay_certification(...)` now calls `run_universal_provider_worker_runtime(...)`.
- It stores the universal capture under `worker_lifecycle_continuation["universal_provider_worker"]`.
- It preserves a compatibility alias under `worker_lifecycle_continuation["openai_external_worker_provider"]`.
- It marks:
  - `universal_provider_runtime_reached: true`;
  - `smart_provider_selection_reached: true`;
  - `openai_provider_reached: true`;
  - `result_validation_reached: true`;
  - `replay_certification_reached: true`.

Universal Provider Runtime evidence:

- `run_universal_provider_worker_runtime(...)` calls `select_unified_resource(...)`.
- It records `000_universal_provider_worker_binding_recorded.json`.
- It records `001_universal_provider_worker_result_recorded.json`.
- It exposes `universal_provider_worker_status`, `smart_selection_executed`, `selected_resource_id`, and `universal_provider_worker_replay_reference`.
- It records nested Universal Resource Selection replay and selected-provider replay.

Replay certification evidence:

- `_continue_worker_request_to_replay_certification(...)` calls `certify_validated_replay(...)`.
- It returns `replay_certification_capture` under `worker_lifecycle_continuation["replay_certification"]`.
- Turn summaries expose `replay_certification_status`, `replay_certification_replay_reference`, and `replay_certification_reached`.

## Runtime Status Computation

The canonical Human Interface runtime entry computes status in `aigol/runtime/human_interface_runtime_entry_service.py`.

Implementation evidence:

- It invokes the governed runtime at lines 148-152.
- It selects a single latest turn with `_latest_turn(conversation_result)` at line 153.
- It computes `runtime_bound = _runtime_bound(conversation_result, latest_turn)` at line 154.
- `_runtime_bound(...)` requires only:
  - `conversation_result["failed_turns"] == 0`;
  - `latest_turn["worker_invoked"] is True`;
  - `latest_turn["replay_certification_reached"] is True`.
- It does not inspect replay directories, replay certification artifacts, Universal Provider Runtime artifacts, selected-provider artifacts, or Certified Provider Attachment artifacts.

The status namespace projection is therefore:

```text
latest_turn flat fields -> canonical_runtime_entry_status -> aicli runtime_status
```

It is not:

```text
certified replay artifacts -> reconstructed runtime state -> aicli runtime_status
```

## Worker Status Projection

The Human Interface projects worker execution with:

```python
"worker_execution_reached": latest_turn.get("worker_invoked") is True
```

This means the Human Interface treats `worker_invoked` as the only worker execution source of truth.

The governed development turn summary can produce richer Worker evidence:

- `worker_invocation_reached`;
- `worker_execution_candidate_reached`;
- `external_task_package_reached`;
- `universal_provider_worker_status`;
- `result_validation_status`;
- `replay_certification_status`.

But the canonical Human Interface runtime entry does not use those fields when computing `worker_execution_reached`. If `worker_invoked` is missing or false while downstream Worker lifecycle evidence is present, the Human Interface reports `worker_execution_reached: false`.

## Provider Status Projection

The Human Interface projects provider invocation with:

```python
"provider_invocation_reached": latest_turn.get("openai_provider_reached") is True
or latest_turn.get("provider_invoked") is True
```

This projection is still bound to the older OpenAI-specific flattened field and generic `provider_invoked` field.

It does not inspect:

- `universal_provider_runtime_reached`;
- `smart_provider_selection_reached`;
- `universal_provider_worker_status`;
- `selected_provider_resource_id`;
- `smart_provider_selection_executed`;
- `universal_provider_worker_replay_reference`;
- `resource_selection_replay_reference`;
- selected-provider replay;
- Certified Provider Attachment replay.

Therefore the Human Interface can under-report provider reachability after G18-03 if Universal Provider Runtime evidence exists but the old OpenAI-specific projection field is absent, stale, or not copied into the latest turn.

## Replay Certification Projection

The Human Interface projects replay certification with:

```python
"replay_certification_reached": latest_turn.get("replay_certification_reached") is True
```

It copies `replay_certification_status` and `replay_certification_replay_reference`, but it does not inspect either one.

Ignored replay evidence includes:

- the replay certification artifact at `replay_certification_replay_reference`;
- replay certification status value `REPLAY_CERTIFICATION_COMPLETED`;
- result validation artifact evidence;
- Universal Provider Worker result artifact evidence;
- Certified Provider Attachment replay evidence.

Thus replay certification can be present in replay and still be omitted from the Human Interface status if the flattened latest-turn boolean is missing or false.

## Missing Replay Bindings

No replay artifacts are reconstructed by the Human Interface status projection.

The following existing evidence is ignored for status computation:

- `universal_provider_worker_replay_reference`;
- `resource_selection_replay_reference`;
- `selected_provider_resource_id`;
- `smart_provider_selection_executed`;
- `universal_provider_worker_status`;
- `openai_external_worker_replay_reference`;
- selected-provider Certified Provider Attachment replay;
- `replay_certification_replay_reference`;
- `replay_certification_status`;
- nested `worker_lifecycle_continuation` evidence after it has been flattened into the turn.

The workspace state recorder also receives `turn_results=[result]`, where `result` is the Human Interface projection itself, not the raw governed-runtime `conversation_result["turns"]`. This preserves the projected status, but it does not add an independent replay reconstruction step.

## Timing Review

The mismatch is not caused by the Human Interface computing before the continuation completes in the canonical path.

Implementation evidence:

- `run_human_interface_runtime_entry(...)` calls the governed runtime and waits for `conversation_result`.
- The governed development bridge executes auto-continuation before appending the turn summary.
- Only after the governed runtime returns does the Human Interface select `_latest_turn(...)` and compute status.

Therefore the deterministic issue is projection coverage, not premature status computation.

## Minimal Binding Recommendation

The smallest deterministic binding is to add a Human Interface runtime projection helper that derives status from existing latest-turn and replay-reference evidence without changing Worker, Provider, Governance, or Replay runtimes.

The helper should:

- continue using `latest_turn` as the primary projection surface;
- treat `worker_invoked`, `worker_invocation_reached`, `worker_execution_candidate_reached`, or completed Worker lifecycle statuses as Worker-reached evidence;
- treat `universal_provider_runtime_reached`, `smart_provider_selection_reached`, `universal_provider_worker_status == UNIVERSAL_PROVIDER_WORKER_COMPLETED`, `openai_provider_reached`, or `provider_invoked` as Provider-reached evidence;
- treat `replay_certification_reached` or `replay_certification_status == REPLAY_CERTIFICATION_COMPLETED` as replay-certification evidence;
- optionally verify referenced replay artifacts when `replay_certification_replay_reference` or `universal_provider_worker_replay_reference` is present;
- leave `aicli` as a presenter and keep the canonical projection inside `human_interface_runtime_entry_service.py`.

This is a projection binding correction only. It does not require redesigning Platform Core, Universal Provider Runtime, Worker Platform, Provider Platform, Governance, or Replay.

## Architectural Conclusions

- The certified runtime path can reach Universal Provider Runtime and replay certification.
- The Human Interface status projection is narrower than the certified replay evidence now available.
- The Human Interface is still partially bound to the previous flattened provider projection, especially `openai_provider_reached`.
- Universal Provider Runtime replay is included in Worker continuation evidence, but not included in canonical Human Interface status computation.
- Worker lifecycle replay is flattened into turn summaries, but not independently reconstructed by Human Interface runtime entry.
- Replay certification replay is referenced, but not inspected.
- The observed `REFERENCE_UHI_RUNTIME_PARTIALLY_BOUND` follows from canonical status projection returning `CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_PARTIALLY_BOUND`.

## Final Recommendation

Implement a narrow Human Interface runtime status projection binding that reuses existing latest-turn fields and replay references.

Do not move orchestration, provider selection, Worker execution, governance authorization, or replay certification into the Human Interface. The Human Interface should only project already-certified evidence accurately.

## Final Verdict

`HUMAN_INTERFACE_RUNTIME_STATUS_PROJECTION_REUSE_WITH_MINOR_BINDING`
