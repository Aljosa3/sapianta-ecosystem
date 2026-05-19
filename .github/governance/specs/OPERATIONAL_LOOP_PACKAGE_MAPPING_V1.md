# OPERATIONAL_LOOP_PACKAGE_MAPPING_V1

## Status

Draft mapping specification.

## Purpose

This specification defines a bounded semantic continuity envelope between
`OPERATIONAL_LOOP_CONTRACT_V1` and the existing AGOL Bridge task and result
packages.

Core decision: do not mutate existing AGOL Bridge foundation schemas directly.
Define a separate loop envelope over existing task and result packages.

This is specification, mapping, and envelope design only. It does not implement
runtime behavior, mutate schemas, refactor foundation packages, add
orchestration, add semantic autonomy, or expand authority.

## 1. Loop Envelope Purpose

The loop envelope exists to:

- preserve foundation task and result schemas;
- add semantic continuity metadata above them;
- connect reasoning, governance, execution, replay, interpretation, and
  next-step synthesis;
- keep replay-safe lineage without rewriting existing artifacts;
- separate semantic interpretation continuity from execution authority.

The envelope references existing packages and replay records. It does not
replace, rewrite, or mutate them.

## 2. Loop Envelope Schema

Canonical envelope fields:

- `loop_id`
- `originating_human_request_ref`
- `semantic_context_ref`
- `task_package_ref`
- `result_package_ref`
- `lineage_id`
- `execution_provider_ref`
- `governance_state_ref`
- `replay_refs`
- `lifecycle_refs`
- `semantic_interpretation_boundary`
- `next_step_ref`
- `authority_boundary_statement`
- `created_at`
- `envelope_hash`

Serialization expectations:

- envelope JSON must use deterministic key ordering;
- `envelope_hash` must be calculated from canonical envelope content excluding
  the `envelope_hash` field itself;
- package references must be replay-safe identifiers, hashes, or historical
  artifact paths;
- missing referenced artifacts must block finalization of the envelope.

## 3. Mapping to Existing Task Package

Existing task package fields:

- `task_id`
- `governance_mode`
- `risk_class`
- `approval_required`
- `codex_prompt`
- `constraints`
- `expected_outputs`
- `metadata`

Mapping:

| Existing Task Field | Loop Envelope Field | Classification |
| --- | --- | --- |
| `task_id` | `task_package_ref.task_id` | exact |
| `governance_mode` | `governance_state_ref.governance_mode` | exact |
| `risk_class` | `governance_state_ref.risk_class` | exact |
| `approval_required` | `governance_state_ref.approval_required` | exact |
| `codex_prompt` | `semantic_context_ref.execution_prompt_ref` | partial |
| `constraints` | `governance_state_ref.constraints_ref` | partial |
| `expected_outputs` | `governance_state_ref.expected_outputs_ref` | partial |
| `metadata` | `lineage_id`, `semantic_context_ref`, `lifecycle_refs` | partial |

Missing semantic-continuity mappings:

- explicit `semantic_context_ref`;
- explicit `execution_provider_ref`;
- explicit immutable `lineage_id` if absent from metadata;
- explicit `task_package_ref.package_hash`;
- explicit `authority_boundary_statement`.

Deferred mappings:

- provider capability profile;
- semantic interpretation boundary;
- next-step synthesis reference.

## 4. Mapping to Existing Result Package

Expected result package fields for mapping review:

- `task_id`
- `status`
- `executor`
- `files_changed`
- `commands_run`
- `tests`
- `artifacts`
- `errors`
- `summary`
- `requires_human_review`

Current AGOL Bridge foundation result schema includes:

- `status`
- `tests`
- `files_changed`
- `artifacts`
- `summary`
- `requires_human_review`

Mapping:

| Existing / Expected Result Field | Loop Envelope Field | Classification |
| --- | --- | --- |
| `task_id` | `result_package_ref.originating_task_id` | missing in current schema |
| `status` | `governance_state_ref.result_status` | exact |
| `executor` | `execution_provider_ref.provider_id` | missing in current schema |
| `files_changed` | `result_package_ref.files_changed` | exact |
| `commands_run` | `result_package_ref.commands_run` | missing in current schema |
| `tests` | `result_package_ref.tests` | exact |
| `artifacts` | `result_package_ref.artifacts` | exact |
| `errors` | `result_package_ref.errors` | missing in current schema |
| `summary` | `result_package_ref.summary` | exact |
| `requires_human_review` | `governance_state_ref.requires_human_review` | exact |

Missing interpretation-continuity mappings:

- explicit `semantic_interpretation_boundary`;
- explicit `next_step_ref`;
- explicit result-to-task lineage if `task_id` is absent;
- explicit `result_package_ref.package_hash`;
- explicit provider identity if `executor` is absent.

Deferred mappings:

- normalized command transcript;
- provider capability constraints;
- result interpretation artifact;
- next-step proposal artifact.

## 5. Replay and Lifecycle Mapping

The envelope references:

- append-only replay records through `replay_refs`;
- lifecycle state transitions through `lifecycle_refs`;
- immutable dispatched packages through `task_package_ref.dispatched_path` or
  equivalent replay-safe reference;
- result package hashes through `result_package_ref.package_hash`;
- quarantine and failure states through `governance_state_ref.lifecycle_state`
  and `lifecycle_refs`.

Rules:

- the envelope must not mutate replay records;
- the envelope must not rewrite package hashes;
- the envelope must preserve historical artifact paths;
- quarantine and failure states must remain visible;
- lifecycle references must not imply transitions that did not occur.

## 6. Semantic Continuity Mapping

The envelope records:

- semantic cognition source in `semantic_context_ref.source`;
- semantic context reference in `semantic_context_ref.reference`;
- semantic interpretation boundary in `semantic_interpretation_boundary`;
- next-step synthesis reference in `next_step_ref`;
- non-deterministic semantic reasoning limitation in
  `semantic_interpretation_boundary.reasoning_determinism`;
- distinction between semantic interpretation and governance decision in
  `authority_boundary_statement`.

Rules:

- semantic interpretation is not governance approval;
- next-step synthesis is not approved continuation;
- semantic reasoning is model-native and non-deterministic;
- transport replay is deterministic, but semantic reasoning replay is limited.

## 7. Authority Boundaries

- ChatGPT may propose semantic direction.
- AiGOL / AGOL may admit, constrain, quarantine, or reject.
- Codex / providers may execute only through governed transport.
- The sidepanel may observe only.
- Next-step synthesis is not approval.

The envelope records these boundaries but does not create authority.

## 8. Safety Rules

The envelope must not:

- rewrite task packages;
- rewrite result packages;
- mutate replay records;
- create execution authority;
- bypass approval;
- imply semantic replay determinism;
- create autonomous continuation;
- dispatch work;
- execute provider work;
- approve next steps.

## Missing Fields

Missing or non-canonical fields that should be supplied by the envelope:

- `loop_id`
- `originating_human_request_ref`
- `semantic_context_ref`
- `lineage_id`
- `execution_provider_ref`
- `task_package_ref.package_hash`
- `result_package_ref.originating_task_id`
- `result_package_ref.package_hash`
- `semantic_interpretation_boundary`
- `next_step_ref`
- `authority_boundary_statement`

## Recommended Next Step

Create a review-only envelope example fixture that references existing task and
result packages without changing their schemas. After review, implement envelope
validation as a separate module that reads existing packages and emits a
deterministic envelope artifact without mutating source packages or replay logs.
