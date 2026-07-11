# G18-08 Deterministic Root Cause Trace Reuse Audit

## Executive Summary

This audit determines whether Platform Core already contains the deterministic foundations required for a reusable replay-backed Root Cause Trace capability.

Conclusion: the required foundations already exist, but they are not exposed as one reusable root-cause trace service.

Existing capabilities can deterministically reconstruct replay, normalize replay observations, certify replay, preserve runtime projection evidence, explain governed operator operations, classify replay gaps, map replay-derived gaps to bounded improvement intent, preserve Platform Core workspace state, and record PCCL governing decisions.

The missing capability is a thin reusable binding that starts from an observed result field, discovers the producing replay artifact chain, and composes the existing reconstruction, observation, governance, runtime, knowledge-reuse, and explanation primitives into one deterministic trace output.

Final verdict: `DETERMINISTIC_ROOT_CAUSE_TRACE_REUSE_WITH_MINOR_BINDING`.

## Existing Replay Capabilities

Replay reconstruction already exists in multiple certified runtime paths.

Implementation evidence:

- `aigol/runtime/platform_core_existing_file_replay.py`
  - `load_existing_file_mutation_replay(...)` loads ordered replay wrappers.
  - `reconstruct_existing_file_mutation_replay(...)` validates artifact ordering, wrapper hashes, artifact hashes, and cross-artifact lineage before returning execution status, Worker identity, mutation hashes, validation status, and replay hash.
- `aigol/runtime/replay_certification_runtime.py`
  - `reconstruct_replay_certification_replay(...)` validates replay certification order, wrapper hashes, certification artifact hash, returned-artifact reference, and returned-artifact hash.
- `aigol/runtime/replay_observation_layer.py`
  - `observe_replay_directory(...)` reads existing replay wrappers from a directory.
  - `reconstruct_replay_observation_layer(...)` validates persisted observation replay and detects corruption.
- `aigol/cli/commands/replay.py`
  - `verify_replay(...)` verifies governed return replay.
  - `_verify_operator_runtime_replay(...)` verifies operator replay by reconstructing provider, authorization, and worker replay hashes.
  - `operator_operation_report(...)` summarizes replay-backed operation directories.

Replay evidence is not merely archival. Existing reconstruction functions enforce deterministic replay order and hash continuity, and they fail closed when replay is missing, malformed, corrupt, or mismatched.

## Existing Governance Capabilities

Governance decisions are already represented as deterministic artifacts.

Implementation evidence:

- `aigol/runtime/platform_core_cognition_layer.py`
  - `create_pccl_orchestration_decision_record(...)` creates a PCCL decision record.
  - `validate_pccl_orchestration_decision_record(...)` validates the record.
- `tests/test_g16_11_pccl_orchestration_decision_record.py`
  - proves admissible lifecycle transitions are selected without execution;
  - proves terminal states fail closed;
  - proves inadmissible transitions fail closed;
  - proves supporting evidence references are required and validated.

The PCCL decision record records:

- current lifecycle state;
- admissible next lifecycle transitions;
- selected next transition;
- supporting evidence references;
- authority flags;
- non-execution boundaries.

This is sufficient to locate a governing decision when a trace can bind a runtime result to a PCCL decision reference or supporting evidence hash.

## Existing Runtime Evidence

Runtime stages already emit deterministic artifacts and projection evidence.

Implementation evidence:

- `aigol/runtime/human_interface_runtime_entry_service.py`
  - `_runtime_status_projection(...)` projects runtime status from latest-turn fields and replay evidence.
  - `_discover_turn_replay_root(...)` discovers a current `TURN-*` replay root from existing replay references.
  - `_read_replay_artifact_path(...)` reads wrapped replay artifacts without mutating replay.
  - `runtime_status_projection_evidence` exposes inspected replay sources and projected status fields.
- `docs/governance/G18_07_RUNTIME_STATUS_REPLAY_DISCOVERY_BINDING_IMPLEMENTATION.md`
  - records the binding that lets Human Interface projection inspect Worker lifecycle, Universal Provider Worker, resource selection, selected provider, Certified Provider Attachment, and replay certification artifacts under a current turn tree.
- `aigol/cli/commands/run_governed.py`
  - `run_governed_operation_command(...)` preserves provider, authorization, and Worker replay references and hashes in the returned runtime result.
  - `_success_result(...)` returns provider, authorization, Worker identity, replay reference, and replay summary.

Runtime evidence can therefore answer “what stage was reached” when a trace can map the observed result to the relevant replay tree.

## Existing Observation Capabilities

The Replay Observation Layer is the strongest reusable observation foundation.

Implementation evidence:

- `aigol/runtime/replay_observation_layer.py`
  - `generate_replay_observation_layer(...)` persists deterministic normalized observations.
  - `replay_observation_artifact(...)` derives observation category, severity, execution stage, originating component, deterministic message, related artifact identifiers, source replay step, source replay index, source artifact hash, and source replay hash.
  - `observe_replay_directory(...)` reads existing replay without mutating it.
  - `reconstruct_replay_observation_layer(...)` validates observation replay and hash continuity.
- `tests/test_g15_01_replay_observation_layer_v1.py`
  - proves provider failure observation;
  - proves deterministic reconstruction;
  - proves source replay is not mutated;
  - proves corruption detection;
  - proves Replay Certification generates an observation layer before certification.

Observation categories already include:

- `SUCCESS`;
- `FAILURE`;
- `WARNING`;
- `VALIDATION`;
- `GOVERNANCE`;
- `PROVIDER`;
- `WORKER`;
- `CERTIFICATION`.

This is directly reusable for root-cause traces because it normalizes replay artifacts into deterministic observations without granting authority, invoking providers, invoking workers, creating proposals, or modifying source replay.

## Existing Improvement Analysis Reuse

Replay-derived improvement analysis already consumes replay evidence without executing changes.

Implementation evidence:

- `aigol/runtime/replay_gap_detection_runtime.py`
  - `detect_replay_gaps(...)` classifies replay-visible gaps.
  - `reconstruct_replay_gap_detection_replay(...)` validates evidence, classification, detection, returned artifact order, hashes, and references.
- `aigol/runtime/replay_to_improvement_intent_runtime.py`
  - `create_improvement_intent_from_replay_gap(...)` converts confirmed replay gaps to bounded improvement intent only.
  - `reconstruct_replay_to_improvement_intent_replay(...)` validates the replay-to-intent chain.
- `tests/test_replay_derived_improvement_certification_v1.py`
  - proves a failed replay validation can be classified as a deterministic validation gap;
  - proves improvement intent remains non-authoritative and does not invoke PPP, providers, workers, dispatch, or execution.
- `tests/test_replay_derived_improvement_operationalization_certification_v1.py`
  - proves replay-derived improvement operationalization packages preserve lineage, duplicate detection, priority, supersession, and proposal-only behavior.

These capabilities are reusable after root-cause tracing has identified the replay-backed condition. They should not replace root-cause trace, because they classify improvement eligibility rather than explain the originating runtime result.

## Existing Knowledge Reuse

Platform Core already records project workspace state and knowledge reuse evidence.

Implementation evidence:

- `aigol/runtime/platform_core_project_services.py`
  - `record_unified_human_interface_workspace_state(...)` records canonical Platform Core workspace state.
  - `latest_platform_core_workspace_state(...)` recovers the latest workspace state from replay.
  - `build_persistent_workspace_state_artifact(...)` stores completion references, runtime replay references, implementation history, recent governed decisions, project guidance, and project knowledge index.
  - `project_knowledge_context_from_workspace(...)` classifies whether a request relates to certified artifacts, existing capability, existing milestone, or new governed work.
- `docs/governance/G16_06_PCCL_CAPABILITY_RESOLUTION_AUDIT.md`
  - identifies `project_knowledge_context_from_workspace(...)` as an existing Platform Core capability PCCL should reuse rather than duplicate.

Knowledge reuse can locate certified artifacts and prior implementation history. This supports root-cause explanation by connecting the originating request and observed runtime result to existing certified capability families and prior governed decisions.

## Deterministic Trace Feasibility

Existing capabilities can already support the six required trace operations, but not through one reusable public service.

1. Starting from an observed result:
   - Supported in specific paths by `runtime_status_projection_evidence`, operator replay `operation_id`, `replay_reference`, `result_hash`, and workspace `completion_reference`.
   - Gap: there is no generic observed-result resolver for arbitrary fields such as `worker_execution_reached = false`.

2. Locating the replay artifact that produced it:
   - Supported by replay reconstruction functions, `observe_replay_directory(...)`, `_discover_turn_replay_root(...)`, and operator replay verification.
   - Gap: no generic artifact index maps result fields to replay artifact paths and source hashes.

3. Locating the runtime stage:
   - Supported by Replay Observation Layer fields such as `execution_stage`, `originating_component`, `source_replay_step`, and `source_replay_index`.
   - Supported by Human Interface projection evidence for Worker, provider, resource-selection, attachment, and replay-certification artifacts.
   - Gap: stage naming is available but not centralized across all runtime families.

4. Locating the governing decision:
   - Supported by PCCL orchestration decision records, authorization replay, Platform Core workspace `recent_governed_decisions`, and replay certification references.
   - Gap: no generic binding walks from an arbitrary runtime artifact to its governing decision record or authorization artifact.

5. Locating the originating request:
   - Supported by Human Interface project context `message_hash`, workspace `latest_prompt_hash`, source-router artifacts, multiline prompt capture artifacts, and operator replay request/proposal artifacts.
   - Gap: no single resolver links an observed result to the canonical originating request across all runtime families.

6. Producing a deterministic replay-backed explanation:
   - Supported in operator replay by `explain_operator_operation(...)`.
   - Supported generally in pieces by Replay Observation Layer deterministic messages, replay certification rationale, workspace guidance, and replay gap detection.
   - Gap: the explanation generator is domain-specific for operator operations and not a generic root-cause trace composer.

Therefore, deterministic root-cause trace is feasible by reuse, but not already reusable as a single capability.

## Reusable Capability Inventory

Reusable primitives already available:

- Replay loading and hashing:
  - `aigol.runtime.transport.serialization.load_json`;
  - `aigol.runtime.transport.serialization.replay_hash`;
  - `write_json_immutable`.
- Replay reconstruction:
  - `reconstruct_existing_file_mutation_replay(...)`;
  - `reconstruct_replay_certification_replay(...)`;
  - `reconstruct_replay_observation_layer(...)`;
  - `reconstruct_replay_gap_detection_replay(...)`;
  - `reconstruct_replay_to_improvement_intent_replay(...)`;
  - provider, authorization, and filesystem worker replay reconstruction used by `run_governed_operation_command(...)`.
- Replay observation:
  - `generate_replay_observation_layer(...)`;
  - `observe_replay_directory(...)`;
  - `replay_observation_artifact(...)`.
- Replay-backed explanation:
  - `explain_operator_operation(...)`;
  - `_explanation_evidence(...)`;
  - `_success_explanation_lines(...)`.
- Runtime projection:
  - `_runtime_status_projection(...)`;
  - `_discover_turn_replay_root(...)`;
  - `runtime_status_projection_evidence`.
- Governance decisions:
  - `create_pccl_orchestration_decision_record(...)`;
  - `validate_pccl_orchestration_decision_record(...)`;
  - authorization replay reconstruction.
- Improvement analysis:
  - `detect_replay_gaps(...)`;
  - `create_improvement_intent_from_replay_gap(...)`.
- Knowledge reuse:
  - `record_unified_human_interface_workspace_state(...)`;
  - `latest_platform_core_workspace_state(...)`;
  - `project_knowledge_context_from_workspace(...)`.

## Missing Bindings

The missing pieces are small reusable bindings, not a new architecture.

Minimal binding 1: observed result resolver.

- Input: observed result key/value, runtime result, and optional replay reference.
- Output: candidate replay root, candidate artifact paths, and candidate source fields.
- Reuse: `_discover_turn_replay_root(...)`, workspace state references, operator replay verification, and replay directory observation.

Minimal binding 2: artifact-to-stage index.

- Input: replay artifact wrapper or artifact path.
- Output: runtime stage, originating component, source replay index, source replay step, artifact hash, and replay hash.
- Reuse: `replay_observation_artifact(...)` and `observe_replay_directory(...)`.

Minimal binding 3: stage-to-governance/request linkage.

- Input: artifact hash, replay reference, stage classification.
- Output: governing decision reference and originating request reference when present.
- Reuse: PCCL decision records, authorization replay, Platform Core workspace state, source-router artifacts, multiline prompt capture artifacts, and Human Interface project context artifacts.

Minimal binding 4: generic explanation composer.

- Input: observed result, resolved artifact chain, observation layer, governance decision, originating request.
- Output: deterministic explanation with supporting hashes and missing-evidence list.
- Reuse: `explain_operator_operation(...)` structure and Replay Observation Layer deterministic messages.

These bindings should remain read-only and fail closed when references are missing or hashes do not validate.

## Architectural Conclusions

Platform Core already has the deterministic ingredients for root-cause tracing:

- replay reconstruction;
- replay observation;
- replay certification;
- governance decision records;
- runtime projection evidence;
- workspace state;
- knowledge reuse;
- replay-derived improvement analysis;
- replay-backed operation explanation.

The current limitation is compositional. Existing capabilities are scattered across specific runtime families and command surfaces. Manual investigations during G17 and G18 composed them by hand.

A reusable Root Cause Trace capability should therefore be a thin Platform Core composition layer over existing artifacts, not a new subsystem and not a redesign of Replay, Governance, Human Interface, Provider Platform, Worker Platform, or PCCL.

## Final Recommendation

Implement only a minimal read-only binding that composes existing Platform Core capabilities:

1. Resolve observed result to replay root and candidate artifacts.
2. Generate or reconstruct Replay Observation Layer evidence.
3. Locate runtime stage and originating component.
4. Attach governing decision or authorization evidence when present.
5. Attach originating request or workspace context when present.
6. Produce a deterministic explanation and explicit missing-evidence list.

Do not create new governance authority, provider authority, Worker authority, replay mutation semantics, or autonomous remediation behavior.

## Final Verdict

`DETERMINISTIC_ROOT_CAUSE_TRACE_REUSE_WITH_MINOR_BINDING`
