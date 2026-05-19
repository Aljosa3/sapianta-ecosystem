# OPERATIONAL_LOOP_CONTRACT_V1

## Status

Draft contract specification.

## Purpose

This contract defines the canonical bounded operational protocol connecting
semantic reasoning, governed task packaging, governance lifecycle, execution
provider dispatch, governed result normalization, replay lineage, sidepanel
observability, and semantic interpretation continuity.

This is a specification and operational protocol design only. It does not
implement runtime behavior, orchestration runtime, autonomous execution,
semantic autonomy, hidden dispatch, or authority expansion.

## 1. Canonical Operational Stages

The canonical operational stages are:

1. `HUMAN_REQUEST`
2. `SEMANTIC_REASONING`
3. `GOVERNED_TASK_SYNTHESIS`
4. `GOVERNANCE_ADMISSIBILITY`
5. `EXECUTION_DISPATCH`
6. `EXECUTION_RESULT`
7. `GOVERNED_RESULT_NORMALIZATION`
8. `REPLAY_UPDATE`
9. `LIFECYCLE_UPDATE`
10. `SEMANTIC_INTERPRETATION`
11. `NEXT_STEP_SYNTHESIS`

## 2. Stage Contracts

### HUMAN_REQUEST

- Purpose: capture the operator request and intent boundary.
- Allowed actor: human.
- Allowed mutations: creation of an explicit request artifact.
- Replay references: request identity and operator-visible context reference.
- Lifecycle transitions: may begin `CREATED`.
- Authority boundaries: human retains continuation authority.
- Observability visibility: visible as initial request context.
- Failure semantics: absent or malformed request blocks task synthesis.

### SEMANTIC_REASONING

- Purpose: generate candidate meaning, task framing, and semantic direction.
- Allowed actor: ChatGPT / LLMs.
- Allowed mutations: none to governance state.
- Replay references: semantic context reference may be recorded.
- Lifecycle transitions: none.
- Authority boundaries: no execution authority, approval authority, or dispatch.
- Observability visibility: labeled as model-native semantic reasoning.
- Failure semantics: ambiguous reasoning requires human clarification or blocked
  task synthesis.

### GOVERNED_TASK_SYNTHESIS

- Purpose: convert proposed direction into deterministic governed task package.
- Allowed actor: AiGOL / AGOL governance tooling under human-visible workflow.
- Allowed mutations: creation of task package before dispatch.
- Replay references: task id, lineage id, replay hash, semantic context
  reference.
- Lifecycle transitions: `CREATED` or `NORMALIZED`.
- Authority boundaries: synthesis does not dispatch or approve execution.
- Observability visibility: task package summary and constraints visible.
- Failure semantics: invalid package fails closed or quarantines.

### GOVERNANCE_ADMISSIBILITY

- Purpose: validate schema, approval requirements, lifecycle state, replay
  continuity, mutation scope, and provider admissibility.
- Allowed actor: AiGOL / AGOL.
- Allowed mutations: governed lifecycle state and replay-visible validation
  result.
- Replay references: validation event and package hash.
- Lifecycle transitions: `NORMALIZED`, `WAITING_FOR_APPROVAL`, `APPROVED`, or
  `QUARANTINED`.
- Authority boundaries: may admit or block; may not execute provider work.
- Observability visibility: admissibility status and boundary evidence visible.
- Failure semantics: invalid or unknown state fails closed.

### EXECUTION_DISPATCH

- Purpose: hand off approved task package to isolated execution provider.
- Allowed actor: AGOL Bridge after approval and admissibility.
- Allowed mutations: immutable dispatch artifact and replay event.
- Replay references: dispatch event, task id, package hash.
- Lifecycle transitions: `APPROVED` to `DISPATCHED`.
- Authority boundaries: dispatch is bounded transport, not orchestration mesh.
- Observability visibility: dispatch state visible.
- Failure semantics: missing approval, invalid package, or duplicate dispatched
  package blocks dispatch.

### EXECUTION_RESULT

- Purpose: receive provider output from bounded execution.
- Allowed actor: execution provider.
- Allowed mutations: raw provider output artifact where allowed by transport.
- Replay references: provider result reference.
- Lifecycle transitions: may produce `RETURNED` or `FAILED` candidate.
- Authority boundaries: provider does not govern, approve, or mutate replay
  history.
- Observability visibility: provider status visible.
- Failure semantics: provider failure becomes visible failure output.

### GOVERNED_RESULT_NORMALIZATION

- Purpose: normalize provider output into deterministic governed result package.
- Allowed actor: AiGOL / AGOL governance tooling.
- Allowed mutations: result package creation and validation result.
- Replay references: result id, originating task id, replay hash.
- Lifecycle transitions: `RETURNED`, `FAILED`, or `QUARANTINED`.
- Authority boundaries: normalization does not approve continuation.
- Observability visibility: result package summary visible.
- Failure semantics: malformed result quarantines or requires human review.

### REPLAY_UPDATE

- Purpose: append replay event for task, lifecycle, dispatch, result, or
  failure.
- Allowed actor: AGOL replay layer.
- Allowed mutations: append-only replay record.
- Replay references: event id, task id, result id, package hash.
- Lifecycle transitions: none by itself.
- Authority boundaries: replay update is evidence, not execution authority.
- Observability visibility: replay timeline visible.
- Failure semantics: replay write failure blocks finalization.

### LIFECYCLE_UPDATE

- Purpose: record bounded lifecycle state transition.
- Allowed actor: AGOL lifecycle layer.
- Allowed mutations: lifecycle state record and append-only evidence.
- Replay references: lifecycle event id and package hash.
- Lifecycle transitions: only declared transitions.
- Authority boundaries: lifecycle update does not bypass approval or dispatch.
- Observability visibility: lifecycle state visible.
- Failure semantics: unknown or forbidden transitions fail closed.

### SEMANTIC_INTERPRETATION

- Purpose: interpret governed result and propose meaning or explanation.
- Allowed actor: ChatGPT / LLMs.
- Allowed mutations: none to governance state.
- Replay references: result context reference.
- Lifecycle transitions: none.
- Authority boundaries: interpretation is not approval, dispatch, or execution.
- Observability visibility: labeled as non-authoritative semantic reasoning.
- Failure semantics: ambiguity requires human review.

### NEXT_STEP_SYNTHESIS

- Purpose: propose follow-up direction for human review.
- Allowed actor: ChatGPT / LLMs with AGOL governance packaging if continued.
- Allowed mutations: proposed next-step artifact only.
- Replay references: originating result reference and semantic context reference.
- Lifecycle transitions: none unless converted into a new governed task package.
- Authority boundaries: proposal is not approved continuation.
- Observability visibility: next-step proposal visible as proposal.
- Failure semantics: unsafe or unclear proposal blocks continuation.

## 3. Task Package Contract

Canonical task package fields:

- `task_id`
- `lineage_id`
- `replay_hash`
- `semantic_context_reference`
- `governance_state`
- `approval_requirement`
- `execution_provider`
- `mutation_scope`
- `replay_visibility`
- `lifecycle_reference`

Task packages must use deterministic serialization with stable key ordering and
replay-safe hashes. Lineage references are immutable after creation. Dispatch
requires a valid task package, admissible governance state, and approval when
required.

## 4. Result Package Contract

Canonical result package fields:

- `result_id`
- `originating_task_id`
- `replay_hash`
- `execution_status`
- `governance_status`
- `lifecycle_state`
- `replay_references`
- `semantic_interpretation_boundary`
- `next_step_reference`

Result normalization converts provider output into deterministic governed result
packages. Result packages must preserve originating task lineage and append-only
replay references. Result interpretation is separated from result authority.

## 5. Replay Contract

Replay semantics are append-only. Replay records must preserve event identity,
stage, task or result identity, package hash, prior state, next state, actor,
reason, and timestamp when available.

Replay visibility must distinguish transport replay from semantic reasoning.

Transport replay boundaries cover package movement, lifecycle, dispatch, result
return, quarantine, and finalization. Semantic replay is limited because model
reasoning remains non-deterministic and model-native.

Replay records must not be silently rewritten, deleted, or replaced by aliases.

## 6. Lifecycle Contract

Canonical lifecycle states:

- `CREATED`
- `NORMALIZED`
- `WAITING_FOR_APPROVAL`
- `APPROVED`
- `DISPATCHED`
- `EXECUTING`
- `RETURNED`
- `VALIDATED`
- `FINALIZED`
- `QUARANTINED`
- `FAILED`

Transition guarantees:

- dispatch requires approval when required;
- dispatched task packages are immutable;
- returned results must preserve originating task lineage;
- failed and quarantined states remain replay-visible.

Forbidden transitions:

- unknown state to dispatch;
- waiting for approval to dispatch;
- finalized to mutation;
- quarantined to dispatch;
- provider result to approval without governance review.

Failure states are bounded by `QUARANTINED` and `FAILED`.

## 7. Observability Contract

Sidepanel visibility scope includes stage, replay reference, lifecycle state,
approval state, governance boundary, constitutional layer, semantic direction,
provider boundary, result package summary, and next-step proposal.

Read-only guarantees:

- observability does not approve;
- observability does not dispatch;
- observability does not execute;
- observability does not validate;
- observability does not mutate lifecycle;
- observability does not write runtime state.

Authority labels must distinguish:

- approval visibility from approval authority;
- execution result from execution authority;
- semantic interpretation from governance decision;
- in-memory continuity from durable replay.

## 8. Provider Contract

Execution providers are isolated execution surfaces. Codex is the first provider.

Provider capability boundaries:

- execute only dispatched governed task packages;
- return provider output for result normalization;
- do not approve tasks;
- do not govern admissibility;
- do not mutate replay history;
- do not rewrite lifecycle;
- do not dispatch follow-up tasks.

Provider replay obligations:

- preserve task identity in returned output;
- expose execution status;
- expose failure state;
- return output suitable for governed normalization.

## 9. Constitutional Guarantees

This contract preserves:

- ChatGPT / LLMs = semantic cognition only;
- AiGOL / AGOL = governance, replay, lifecycle, admissibility;
- Codex / providers = execution only;
- observability surfaces remain read-only;
- authority boundaries remain explicit;
- execution remains bounded;
- replay lineage remains append-only;
- deterministic governance semantics remain system-native.

## Operational Risks

- Semantic interpretation may be mistaken for governance decision.
- Next-step synthesis may be mistaken for approved continuation.
- Provider dispatch may be mistaken for orchestration runtime.
- Sidepanel observability may be mistaken for execution authority.
- Transport replay may be mistaken for deterministic semantic replay.

## Recommended Follow-Up

Create a bounded implementation review that maps this contract onto existing
AGOL Bridge package schemas and Browser Companion sidepanel labels before any
runtime code changes.
