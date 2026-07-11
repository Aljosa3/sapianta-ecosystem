# G19-HI-03 Clarification Completion Lifecycle Audit

Status: audit-only.

Final verdict: `CLARIFICATION_COMPLETION_REMEDIATION_REQUIRED`.

This audit examines the deterministic failure where Platform Core accepts an answer to an architecture clarification slot, emits acceptance explainability, and then asks for the same architecture outcome again.

No runtime behavior is modified by this artifact.

## Observed Evidence

Observed sequence:

```text
Question:
What outcome should the human interface architecture decision enable?

Answer received.

Platform Core:
Accepted for architecture outcome:
- Human Interface neutrality
- observable user-visible outcome
- reusable Platform Core behavior

Deterministic continuation can proceed.

Platform Core immediately asks:
I still need the architecture outcome for human interface.
```

This proves the answer reached satisfaction verification, but the lifecycle did not complete the active clarification.

## Clarification Lifecycle Map

| Lifecycle step | Owner | Current implementation evidence |
| --- | --- | --- |
| Question created | Platform Core | `deterministic_clarification_plan(...)` selects a missing slot and question. |
| Question registered | Platform Core | `deterministic_clarification_question_bindings(...)` binds question text to stable question ids and semantic slots. |
| Question presented | Human Interface renders Platform Core output | `aicli` renders `human_conversation_experience.clarification_questions`. |
| Answer received | Human Interface transport | `aicli` reads composed clarification reply and resubmits it through Platform Core. |
| Answer validation | Platform Core | `clarification_satisfaction_verification(...)` evaluates the active slot. |
| Question satisfied | Platform Core | Satisfaction artifact records `clarification_satisfied`, `satisfied_question_ids`, `satisfied_semantic_slots`, and `pending_semantic_slots`. |
| Question completion | Platform Core | Not represented as an independent state transition. Completion is inferred inside `resolve_uhi_clarification_continuity(...)`. |
| Pending clarification removal | Platform Core workspace recording, driven by returned pending state | `record_unified_human_interface_workspace_state(...)` stores `pending_clarification_request`. |
| Clarification completion | Platform Core | `clarification_continuity_status` is set from the inferred `resolved` boolean. |
| Approval preparation | Platform Core | `human_conversation_experience_from_resolution(...)` prepares approval only when the returned development intent is summary-admissible. |

## Ownership Map

Clarification completion belongs to Platform Core.

Primary owning components:

- `prepare_unified_human_interface_project_context(...)`
  - restores prior workspace state;
  - detects active pending clarification;
  - calls `resolve_uhi_clarification_continuity(...)`.
- `replay_backed_uhi_clarification_state(...)`
  - restores active clarification from `pending_clarification_request`.
- `resolve_uhi_clarification_continuity(...)`
  - binds reply to the active clarification;
  - verifies satisfaction;
  - determines `clarification_resolved`;
  - emits continuity replay.
- `human_conversation_experience_from_resolution(...)`
  - projects either clarification, fail-closed response, or approval preparation.
- `record_unified_human_interface_workspace_state(...)`
  - persists pending clarification or pending approval state.

Human Interfaces do not own completion. They only transport reply text, render Platform Core output, and record Platform Core-provided pending state.

## State Transition Map

Expected transition after a satisfied architecture outcome:

```text
CLARIFICATION_AWAITING_REPLY
-> CLARIFICATION_REPLY_RECEIVED
-> clarification_satisfied: true
-> pending_semantic_slots: []
-> answered_clarification_question_ids: populated
-> CLARIFICATION_RESOLVED
-> pending_clarification_request: null
-> response_mode: APPROVAL_PREPARATION or non-mutating completion/fail-closed projection
```

Observed transition:

```text
CLARIFICATION_AWAITING_REPLY
-> CLARIFICATION_REPLY_RECEIVED
-> clarification_satisfied: true
-> accepted semantic requirements emitted
-> clarification_resolved remains false or is not consumed as complete
-> pending clarification remains active or is regenerated
-> selected_missing_slot: architecture_outcome
-> follow-up question asks for architecture outcome again
```

## Accepted Answers Storage

Accepted answers are stored in the continuity and enriched resolution artifacts, not in a separate completed-clarification ledger.

Relevant fields:

- `clarification_satisfaction_verification`
- `answered_clarification_question_ids`
- `satisfied_semantic_slots`
- `pending_semantic_slots`
- `clarification_continuity_status`
- `clarification_resolved`
- `clarification_continuity_replay_reference`

The workspace state stores only the current `pending_clarification_request`. It does not independently store a durable `completed_clarifications` set. The planner can inspect `pending_clarification_request.answered_clarification_question_ids` or `workspace_state.clarification_continuity`, but completed clarification evidence is not a first-class workspace index.

## First Deterministic Failure Point

The first deterministic failure point is the completion predicate in:

`aigol/runtime/platform_core_project_services.py::resolve_uhi_clarification_continuity`

The function validates satisfaction first, then computes `resolved` from satisfaction plus downstream development-intent state.

Current shape:

```python
resolved = (
    satisfaction["clarification_satisfied"] is True
    and reply_resolution.get("clarification_required") is not True
)
```

Before G19-HI-02, the same position was coupled even more tightly to summary admissibility:

```python
resolved = (
    reply_resolution.get("summary_admissible") is True
    and satisfaction["clarification_satisfied"] is True
)
```

That coupling is the architectural defect under audit. Completion of the active clarification slot is not represented as its own authoritative transition. A satisfied slot can be prevented from completing because the downstream resolved request is not yet approval-admissible, runtime-admissible, or is still classified as clarification-required by a later intent/planner pass.

## Why The Same Question Reappears

The repeated question is generated by the planner, not by Human Interface logic.

The deterministic path is:

1. `clarification_satisfaction_verification(...)` accepts the reply and emits:
   - `clarification_satisfied: true`
   - `satisfied_semantic_slots: ["architecture_outcome"]`
   - `pending_semantic_slots: []`
2. `resolve_uhi_clarification_continuity(...)` does not treat satisfaction as sufficient to complete the active clarification.
3. The unresolved branch sets:
   - `clarification_required: true`
   - `clarification_reason: "clarification answer did not satisfy active semantic slot"`
   - `active_clarification_open_slot: "architecture_outcome"`
4. `_clarification_missing_slots(...)` sees that reason and re-adds the active slot as missing.
5. `_clarification_question_for_slot(...)` produces:
   - `I still need the architecture outcome for human interface. State the reusable behavior or interface outcome it should enable.`

The emitted acceptance text and the repeated question can therefore coexist because they come from different layers:

- acceptance comes from satisfaction explainability;
- repeated clarification comes from completion failing and the planner treating the same slot as still open.

## Pending Clarification Ownership

Pending clarification is owned by Platform Core workspace replay.

`build_persistent_workspace_state_artifact(...)` persists:

- `pending_clarification_request`
- `pending_implementation_summary`
- `pending_approval`

The Human Interface passes Platform Core state back into `record_unified_human_interface_workspace_state(...)`. It should not clear pending clarification based on local interpretation.

When completion fails, `pending_clarification_request` remains non-null or a new pending clarification is recorded. The next turn restores it through `replay_backed_uhi_clarification_state(...)`, so Platform Core legitimately believes the active clarification remains open.

## Clarification Completion Metadata Gap

Completion metadata exists partially but is not authoritative enough:

- `clarification_satisfied` exists.
- `satisfied_question_ids` exists.
- `satisfied_semantic_slots` exists.
- `pending_semantic_slots` exists.
- `clarification_resolved` exists.
- `clarification_continuity_status` exists.

Missing or weak:

- no independent `clarification_completion_status`;
- no explicit `completed_clarification_question_ids`;
- no workspace-level completed clarification index;
- no invariant that `clarification_satisfied: true` and `pending_semantic_slots: []` must close the active pending clarification before planner follow-up;
- no fail-closed conflict when satisfaction says `READY` but completion says `STILL_REQUIRED`.

## Root Cause

Root cause:

`CLARIFICATION_COMPLETION_COUPLED_TO_DOWNSTREAM_INTENT_ADMISSIBILITY`

The active clarification slot can be satisfaction-verified but not completion-consumed because `resolve_uhi_clarification_continuity(...)` derives completion from downstream intent state instead of committing the satisfied active slot as completed first.

Secondary contributing factors:

- `answered_clarification_question_ids` are included only when `resolved` is true, even though satisfaction may have already produced satisfied question ids.
- Planner suppression checks previous answers from pending clarification or workspace continuity, but completed-answer evidence is not persisted as a first-class workspace index.
- The unresolved branch uses the phrase `clarification answer did not satisfy active semantic slot` even for cases where satisfaction verification accepted the answer but downstream completion failed.
- Approval preparation reads the current returned development intent and workspace state. If pending clarification remains active, approval preparation is bypassed and the planner can ask again.

## Affected Artifacts And Functions

Primary affected functions:

- `aigol/runtime/platform_core_project_services.py::resolve_uhi_clarification_continuity`
- `aigol/runtime/platform_core_project_services.py::clarification_satisfaction_verification`
- `aigol/runtime/platform_core_project_services.py::deterministic_clarification_plan`
- `aigol/runtime/platform_core_project_services.py::_clarification_missing_slots`
- `aigol/runtime/platform_core_project_services.py::_previous_clarification_answer_ids`
- `aigol/runtime/platform_core_project_services.py::build_persistent_workspace_state_artifact`
- `aigol/runtime/platform_core_project_services.py::human_conversation_experience_from_resolution`

Human Interface affected surface:

- `aigol/cli/aicli.py::run_reference_uhi_submit_session`
- `aigol/cli/aicli.py::run_reference_uhi_session`

Human Interface role remains transport and rendering only. The remediation should not add local semantic clearing or local completion decisions.

## Minimal Remediation Plan

1. In Platform Core, split clarification satisfaction from clarification completion.
2. Introduce an explicit completion artifact or fields:
   - `clarification_completion_status`
   - `completed_clarification_question_ids`
   - `completed_semantic_slots`
   - `completion_blocks_remaining`
   - `completion_authority: PLATFORM_CORE`
3. Treat this condition as sufficient to close the active question:
   - `clarification_satisfied: true`
   - `pending_semantic_slots: []`
   - active question id in `satisfied_question_ids`
4. Persist completed clarification evidence into workspace state separately from `pending_clarification_request`.
5. Clear `pending_clarification_request` whenever the active clarification is completed, even if downstream approval/runtime preparation is blocked for another reason.
6. If downstream intent is not approval-admissible after a completed clarification, project a fail-closed or next-governed-action state, not the same clarification slot.
7. Add an invariant: Platform Core must not emit `deterministic_continuation_status: READY` and then re-add the same active slot as missing.
8. Keep Human Interfaces unchanged except for transporting any new Platform Core fields.

## Regression Scenarios

Required regression coverage:

1. Architecture outcome answer with all accepted semantic requirements produces:
   - `clarification_satisfied: true`
   - `pending_semantic_slots: []`
   - `clarification_completion_status: CLARIFICATION_COMPLETED`
   - no follow-up architecture outcome question.
2. Satisfied clarification with non-implementation work type clears pending clarification and does not enter implementation runtime.
3. Satisfied clarification with downstream approval blocked does not repeat the completed slot.
4. Insufficient architecture answer remains pending and asks the non-identical follow-up question.
5. Workspace state after satisfied clarification has `pending_clarification_request: null`.
6. Workspace state preserves completed clarification ids/slots for planner suppression.
7. Planner refuses to select a missing slot already present in completed clarification evidence.
8. Submit mode and interactive mode both use Platform Core completion state; neither performs local semantic clearing.
9. A stale pending clarification replay artifact with completed question ids fails closed or is superseded, rather than reopening the completed slot.

## Certification Readiness

Current status:

`NOT_CERTIFICATION_READY`

Reason:

The lifecycle has satisfaction evidence and continuity evidence, but completion is not a first-class Platform Core transition. A satisfied active slot can still be treated as pending when downstream intent/admissibility is not aligned.

Certification blockers:

- no independent clarification completion artifact or field;
- completion predicate coupled to downstream intent/admissibility;
- satisfied ids are gated by `resolved`;
- pending clarification removal depends on returned pending state instead of explicit completion state;
- planner can re-add a slot that satisfaction already marked ready;
- no regression proving accepted architecture outcome cannot be repeated under blocked approval/runtime conditions.

Certification can proceed after regression evidence proves:

- accepted clarification always completes the active question;
- completed clarification removes pending state;
- completed slots are not regenerated;
- approval or fail-closed projection occurs after completion without repeating already accepted answers.

## Final Determination

The first deterministic point where clarification completion fails is inside Platform Core clarification continuity, after satisfaction verification and before pending clarification removal.

The preferred correction is minimal and Platform Core-owned:

```text
accepted clarification
-> explicit clarification completion
-> pending clarification removed
-> approval preparation or fail-closed next state
```

Human Interfaces must not repair this locally.
