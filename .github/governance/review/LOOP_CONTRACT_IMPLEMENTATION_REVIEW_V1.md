# LOOP_CONTRACT_IMPLEMENTATION_REVIEW_V1

## Status

Review complete.

Decision: `CONTRACT_IMPLEMENTATION_PARTIAL`

This review maps `OPERATIONAL_LOOP_CONTRACT_V1` against the current AGOL Bridge
schemas, task packages, result packages, replay artifacts, lifecycle artifacts,
Browser Companion sidepanel labels, and governed preview runtime.

This review is documentation-only. It does not modify schemas, runtime behavior,
execution paths, orchestration behavior, semantic autonomy, or authority.

## 1. Canonical Stage Coverage

| Stage | Existing Artifact Support | Schema Support | Replay Support | Lifecycle Support | Sidepanel Visibility | Gap |
| --- | --- | --- | --- | --- | --- | --- |
| `HUMAN_REQUEST` | Browser Companion input and governed preview requests | partial via prompt/request fields | partial via downstream replay identity | partial starts as task creation | visible as sidepanel lifecycle entry | no canonical request artifact |
| `SEMANTIC_REASONING` | ChatGPT bridge and semantic direction labels | partial through normalized request fields | semantic context is not replay-complete | no lifecycle mutation expected | semantic direction view labels model reasoning | semantic replay intentionally limited |
| `GOVERNED_TASK_SYNTHESIS` | AGOL Bridge task package and Codex synthesis artifacts | partial; current schema uses `codex_prompt`, `metadata`, `approval_required` | task replay events exist | `CREATED`, `WAITING_FOR_APPROVAL`, `APPROVED` | task data can appear in lifecycle entries | contract fields not fully represented |
| `GOVERNANCE_ADMISSIBILITY` | task schema validation, approval gating, quarantine | partial through validator and metadata | validation outcomes indirectly replayed through lifecycle events | aligned for approval/quarantine paths | boundary and approval views visible | no standalone admissibility artifact |
| `EXECUTION_DISPATCH` | `dispatch_task` filesystem handoff | aligned for approved task packages | dispatch replay event exists | `APPROVED -> DISPATCHED` supported | dispatch status can render if returned | provider dispatch is filesystem-only |
| `EXECUTION_RESULT` | result writer accepts provider result package | partial; provider raw output boundary is not explicit | result return replay event exists | `DISPATCHED -> RETURNED` represented in replay event | result status can render | raw provider output artifact model is minimal |
| `GOVERNED_RESULT_NORMALIZATION` | result schema validation and writer | partial; schema lacks contract fields like `originating_task_id` | result hash and event recorded | returned/quarantine semantics supported | result summary can render | semantic interpretation boundary missing |
| `REPLAY_UPDATE` | `append_replay_event` JSONL logger | not schema-bound | aligned append-only JSONL | state fields recorded in replay | replay timeline view exists | replay record lacks explicit operational stage field |
| `LIFECYCLE_UPDATE` | lifecycle transition module | aligned state set | replay events include prior/next states | aligned for declared transitions | lifecycle view exists | lifecycle event id is replay event id, not separate field |
| `SEMANTIC_INTERPRETATION` | ChatGPT/semantic direction sidepanel labeling | partial through interpretation/bridge artifacts | semantic reasoning not deterministic replay | no lifecycle mutation expected | semantic direction view exists | no governed result interpretation package |
| `NEXT_STEP_SYNTHESIS` | not implemented as a loop artifact | missing | missing | no lifecycle mutation expected | not specifically visible | deferred pending loop contract implementation |

## 2. Task Package Mapping

| Contract Field | Existing Field / Support | Classification |
| --- | --- | --- |
| `task_id` | `task_id` | exact match |
| `lineage_id` | `metadata` may carry lineage | partial |
| `replay_hash` | `sha256_digest(package)` and replay `package_hash` | partial |
| `semantic_context_reference` | `metadata` or prompt context only | partial |
| `governance_state` | `metadata.lifecycle_state`, `governance_mode` | partial |
| `approval_requirement` | `approval_required` | naming mismatch but semantically aligned |
| `execution_provider` | implied by `codex_prompt`; no explicit field | missing |
| `mutation_scope` | `constraints` and metadata conventions | partial |
| `replay_visibility` | replay event generation | partial |
| `lifecycle_reference` | `metadata.lifecycle_state` | partial |

Task package mapping is safe but incomplete. The current schema is adequate for
foundation transport, approval gating, and dispatch, but it is not yet the full
canonical operational loop task contract.

## 3. Result Package Mapping

| Contract Field | Existing Field / Support | Classification |
| --- | --- | --- |
| `result_id` | generated as `RESULT-<hash>` by result writer | partial |
| `originating_task_id` | absent from result schema | missing |
| `replay_hash` | `sha256_digest(result_package)` and replay `package_hash` | partial |
| `execution_status` | `status` | naming mismatch but semantically aligned |
| `governance_status` | absent from result schema | missing |
| `lifecycle_state` | replay event uses `RETURNED`; package field absent | partial |
| `replay_references` | replay event returned by writer | partial |
| `semantic_interpretation_boundary` | absent from result schema | missing |
| `next_step_reference` | absent from result schema | missing |

Result package mapping is partial. Current result packages are sufficient for
basic return and validation evidence, but not yet sufficient for canonical loop
interpretation continuity.

## 4. Replay and Lifecycle Mapping

Replay implementation is aligned for foundation guarantees:

- append-only JSONL records;
- canonical JSON serialization;
- SHA-256 package hashes;
- event id, task id, event type, previous state, next state, actor, reason, and
  timestamp;
- no overwrite path for replay records.

Lifecycle implementation is aligned for current state transitions:

- declared lifecycle states match the contract;
- missing approval returns `WAITING_FOR_APPROVAL`;
- invalid schemas quarantine;
- unexpected transitions quarantine;
- unknown lifecycle states block;
- dispatched packages use exclusive writes to preserve immutability.

Remaining ambiguity:

- replay records do not include an explicit operational contract stage field;
- result return replay uses generated result id in the `task_id` slot;
- lifecycle event identity is represented by replay event id rather than a
  distinct lifecycle reference.

## 5. Sidepanel Observability Mapping

The Browser Companion sidepanel cockpit is aligned with the observability
contract for read-only visibility:

- Replay Timeline exists and is labeled as transport replay.
- Lifecycle View exists and labels lifecycle state as governed transport state.
- Approval Visibility exists and labels approval visibility as not an approval
  control.
- Governance Boundary View exists and labels observability as no hidden
  execution, no automatic dispatch, no hidden persistence, and localhost-only.
- Constitutional Layer View separates SAPIANTA, AGOL, AiGOL, ChatGPT / LLMs,
  and Codex / workers.
- Semantic Direction View labels semantic direction as not execution authority
  and sidepanel continuity as non-durable.

The sidepanel introduces no new fetch, storage, event listener, dispatch,
approval, validation, runtime write, or browser scraping path.

## 6. Provider Boundary Mapping

Codex/provider boundaries are partially represented:

- Provider execution is represented by existing Codex-oriented task prompt and
  result package flow.
- AGOL Bridge dispatch is filesystem handoff only.
- Provider output returns through result package writing.
- Provider does not govern approval, admissibility, lifecycle, or replay.

Gaps:

- task schema lacks explicit `execution_provider`;
- result schema lacks explicit `originating_task_id`;
- provider raw-output-to-normalized-result boundary is not yet formalized as a
  package contract;
- sidepanel does not yet present a dedicated provider boundary panel.

## 7. Gap Classification

| Gap | Classification | Reason |
| --- | --- | --- |
| Missing canonical task fields: `execution_provider`, explicit `lineage_id`, `semantic_context_reference`, `mutation_scope`, `replay_visibility`, `lifecycle_reference` | HIGH | Needed before full loop contract implementation |
| Missing canonical result fields: `originating_task_id`, `governance_status`, `semantic_interpretation_boundary`, `next_step_reference` | HIGH | Needed for result interpretation continuity |
| Replay records lack explicit operational stage field | MEDIUM | Current replay is safe, but contract-stage navigation is partial |
| No standalone governance admissibility artifact | MEDIUM | Existing validation is safe but not contract-addressable |
| No governed result interpretation package | MEDIUM | Semantic interpretation continuity remains partial |
| No next-step synthesis artifact | MEDIUM | Deliberately deferred until loop contract implementation |
| Sidepanel lacks dedicated provider boundary panel | LOW | Existing labels preserve authority; provider-specific visibility can improve |
| Historical schema names differ from canonical contract names | LOW | Safe naming mismatch, review-visible |

No critical gaps were found. Existing behavior preserves authority boundaries
and fails closed where implemented.

## 8. Implementation Recommendation

Recommended next implementation:

Create `OPERATIONAL_LOOP_PACKAGE_MAPPING_V1` as a narrow schema-mapping artifact
before code changes. It should map the canonical contract fields onto either:

1. a non-breaking extension of existing AGOL Bridge task/result schemas; or
2. a separate loop envelope that wraps current task/result packages without
   mutating the foundation schemas.

The narrowest safe path is a separate loop envelope, because it can add
contract-level lineage, provider, semantic boundary, and next-step references
without breaking existing AGOL Bridge Foundation tests or replay semantics.

## Decision

`CONTRACT_IMPLEMENTATION_PARTIAL`

The current implementation is constitutionally safe and aligned with the
foundation transport model, but it does not yet fully implement the canonical
operational loop contract fields or semantic interpretation continuity.
