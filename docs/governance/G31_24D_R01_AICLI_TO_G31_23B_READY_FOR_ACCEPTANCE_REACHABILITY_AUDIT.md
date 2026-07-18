# G31-24D-R01 AiCLI to G31-23B Ready-for-Acceptance Reachability Audit

Date: 2026-07-18  
Verdict: `AICLI_G31_23B_READY_FOR_ACCEPTANCE_MULTISTAGE_INTEGRATION_REQUIRED`

## Scope, baseline, and conclusion

This is an audit-only continuation from committed baseline `1d2f3d6e`
(`docs(governance): audit content acceptance decision minimality`).  G31-23A
is tracked at `8da4765a`; G31-23B source/report is committed at `a6a9e28a`
and its tracked focused test at `3d7d1730`.  Generation 30 remains closed.

The certified owners can take one exact satisfied G31 Worker unified diff to a
V2 `REPLACE_CONTENT` manifest and `ready_for_acceptance=true`, but no current
production caller connects AiCLI to that sequence.  This is neither a data
incompatibility nor a missing owner.  It is a sequence of independently
governed integrations:

1. AiCLI must continue a `TASK_OUTCOME_SATISFIED` decision to the existing
   non-mutating G31-23A disposable-validation review and distinct application
   decision.
2. A separately authorized continuation must call G31-23A disposable execution
   (the first command boundary) and then G31-23B's non-accepting binder.

The second stage creates only a disposable worktree and immutable evidence;
it never writes the selected source repository.  The endpoint stops before
G31-24D's future human content acceptance, and does not authorize mutation.

## Current actual production path and stop state

`aigol/cli/aicli.py` owns the thin interactive continuation.  After the normal
G31 request path it calls, in order:

| Caller | Existing callee and output | Replay / authority / side effect |
|---|---|---|
| AiCLI request handling | invocation -> `project_g31_invocation_to_execution_candidate` -> `project_g31_candidate_to_governed_execution` | each existing owner writes its own immutable Replay; no result yet |
| `_record_contextual_worker_activation_decision` | `activate_bounded_codex_worker` -> `capture_successful_codex_worker_result` -> `validate_captured_codex_worker_result` | existing Worker activation owns Worker transport; result capture and semantic validation own their Replay |
| `_prepare_contextual_task_outcome_review` | `prepare_codex_task_outcome_review`, then reconstruction | task-review owner persists the review packet/replay; presentation is `render_codex_task_outcome_review` |
| `/satisfied`, `/unsatisfied`, or `/rework` | `_record_contextual_task_outcome_decision` -> `record_codex_task_outcome_human_decision`, then reconstruction and rendering | generic human-decision Replay; decision is result review only |

At `aigol/cli/aicli.py:465-491`, `/satisfied` stores
`codex_task_outcome_human_decision_capture`, clears
`pending_task_outcome_review`, sets `REFERENCE_UHI_SESSION_COMPLETED`, and
breaks.  It has no import, state, command, or call to
`prepare_disposable_patch_validation_review`,
`record_disposable_patch_validation_human_decision`,
`execute_disposable_patch_validation`, or
`bind_codex_replacement_acceptance_prerequisites`.

Thus the current operational stop is a recorded satisfied result-review
decision, not a ready-for-acceptance replacement result.

## Existing unbound path and boundaries

| Transition | Existing public callee / output | Current caller | Side effect and authority | Missing edge |
|---|---|---|---|---|
| satisfied task decision -> plan | `prepare_disposable_patch_validation_review` -> `DISPOSABLE_PATCH_VALIDATION_PLAN_ARTIFACT_V1` and approval-required artifact | none; unit fixture only | immutable two-step plan Replay; no application, command, acceptance, or source write | AiCLI post-`/satisfied` continuation |
| plan -> distinct application decision | `record_disposable_patch_validation_human_decision` -> existing `HUMAN_DECISION_ARTIFACT_V1` | none; unit fixture only | generic human-decision Replay; grants only disposable application scope | pending presentation/decision continuation |
| decision -> certified disposable outcome | `execute_disposable_patch_validation` -> `DISPOSABLE_PATCH_VALIDATION_OUTCOME_ARTIFACT_V1` | none; unit fixture only | copies a disposable workspace, applies the exact patch there, invokes the fixed focused test command, writes outcome Replay; source snapshot is checked unchanged | separately authorized execution continuation |
| successful outcome -> ready state | `bind_codex_replacement_acceptance_prerequisites` -> `CODEX_REPLACEMENT_ACCEPTANCE_PREREQUISITE_BINDING_ARTIFACT_V1`, V2 manifest/content/test/prerequisite captures | none; unit fixture only | immutable binding/manifest Replay; reconstructs all predecessors, no command, acceptance, or source write | call after successful G31-23A outcome |

`execute_disposable_patch_validation` is the first real process boundary:
`execute_validation_command` runs the fixed grounded test in the disposable
workspace.  Its governed repository mutation applies only there.  The first
possible selected-source write is a later, separate mutation owner; it is not
called by G31-23A, G31-23B, or this proposed connection.  Neither stage invokes
a Worker or Provider.  `accept_generated_content` remains uncalled, and
`authorize_filesystem_mutation` remains a distinct later owner.

No existing composite public function spans the two missing stages.  The
G31-23A and G31-23B binding owners are already the appropriate policy,
validation, Replay, patch, and manifest owners.  AiCLI should only retain
captures, present their existing review/decision artifacts, and call a bounded
post-result continuation; it must not recreate policy, manifest construction,
patching, testing, Replay mechanics, or mutation authority.

## Ten-capture inventory for the G31-23B binder

All captures below are parameters of
`bind_codex_replacement_acceptance_prerequisites`.  Its sole production caller
is absent; existing calls are focused-test fixtures.

| Capture parameter | Family / producing public function / Replay owner | AiCLI state and exact classification | Missing edge / effects |
|---|---|---|---|
| `disposable_validation_outcome_capture` | `DISPOSABLE_PATCH_VALIDATION_OUTCOME_ARTIFACT_V1`; `execute_disposable_patch_validation`; outcome Replay | not created or retained | `EXISTING_PRODUCER_NOT_CALLED`; disposable copy, patch, content check and focused command |
| `disposable_validation_review_capture` | G31-23A plan + approval-required V1; `prepare_disposable_patch_validation_review`; plan Replay | not created; all seven upstream inputs are retained | `EXISTING_PRODUCER_NOT_CALLED`; immutable plan only |
| `application_decision_capture` | `HUMAN_DECISION_ARTIFACT_V1`; `record_disposable_patch_validation_human_decision`; human-decision Replay | no pending disposable review/decision state | `EXISTING_PRODUCER_NOT_CALLED`; distinct human disposable-only authority |
| `task_outcome_decision_capture` | task-outcome human decision V1; `record_codex_task_outcome_human_decision`; human-decision Replay | created and retained as `codex_task_outcome_human_decision_capture` | `ALREADY_AVAILABLE_IN_AICLI`; no new effect |
| `task_outcome_review_capture` | task-review packet/required V1; `prepare_codex_task_outcome_review`; task-review Replay | created and retained as `codex_task_outcome_review_capture` before the decision | `ALREADY_AVAILABLE_IN_AICLI`; reconstruction also available |
| `result_capture_binding_capture` | G31 result-capture binding V1; `capture_successful_codex_worker_result`; result-capture Replay | retained as `codex_worker_result_capture_binding_capture` | `ALREADY_AVAILABLE_IN_AICLI` |
| `governance_validation_binding_capture` | G31 semantic-validation binding V1; `validate_captured_codex_worker_result`; validation Replay | retained as `codex_worker_semantic_validation_binding_capture` | `ALREADY_AVAILABLE_IN_AICLI` |
| `activation_capture` | G31 Codex activation capture; `activate_bounded_codex_worker`; activation Replay | retained as `codex_worker_activation_capture` | `ALREADY_AVAILABLE_IN_AICLI`; historic Worker invocation already completed |
| `governed_execution_capture` | governed Worker-execution capture; `project_g31_candidate_to_governed_execution`; its Replay | retained as `governed_worker_execution_capture` | `ALREADY_AVAILABLE_IN_AICLI` |
| `execution_candidate_capture` | execution-candidate capture; `project_g31_invocation_to_execution_candidate`; its Replay | retained as `worker_execution_candidate_capture` | `ALREADY_AVAILABLE_IN_AICLI` |

The seven current lineage captures are deliberately retained in `runtime_result`
and are also deterministically reconstructable through their public
reconstructors.  No duplicate persistent AiCLI state is justified for them.
The first three are not absent contracts: their exact certified producers have
simply never been called in production.

## Compatibility with G31-23A inputs

| Required evidence | Classification | Deterministic basis |
|---|---|---|
| session/conversation identity; original goal; Project Objective; Durable Governed Work; repository grounding | `COMPATIBLE_THROUGH_EXISTING_RECONSTRUCTION` | task review reconstructs the governed request and grounding from the retained lineage |
| selected Worker role; assignment, dispatch, invocation, candidate, execution, and activation | `DIRECTLY_COMPATIBLE` | retained G31 captures above and their Replay identities |
| Worker result identity and exact bytes; semantic result validation | `DIRECTLY_COMPATIBLE` | retained result-capture and semantic-validation captures |
| V2 satisfied result-review decision and its Replay | `DIRECTLY_COMPATIBLE` after `/satisfied` | retained task decision and review; V1/unsatisfied/rework fails closed |
| target relative path, original-file hash, exact unified diff/replacement bytes, permitted replacement type | `COMPATIBLE_THROUGH_EXISTING_RECONSTRUCTION` | G31-23A reconstructs the exact V2 review and derives the bounded patch plan |
| focused-test path and fixed validation command | `COMPATIBLE_THROUGH_EXISTING_RECONSTRUCTION` | G31-23A criteria/plan derive and bind them before execution |
| distinct application decision and outcome | `AVAILABLE_BUT_NOT_BOUND` | public producer contracts exist, but AiCLI has no continuation state/call |
| V2 manifest/content validation/test validation/prerequisite evidence | `AVAILABLE_BUT_NOT_BOUND` | G31-23B builds them only after successful G31-23A outcome |
| Replay references and hashes | `DIRECTLY_COMPATIBLE` for current lineage; `AVAILABLE_BUT_NOT_BOUND` for the three later stages | each canonical owner owns ordered immutable Replay |

There is no `MISSING` or `INCOMPATIBLE` required input.  The old D finding that
AiCLI did not retain ten captures is refined: it retains seven, while the three
remaining captures must truthfully be produced after the two distinct G31-23A
transitions.  They cannot be reconstructed before their owner has run.

## Fail-closed and Replay evidence

Each reconstructor rejects cross-session Replay, substituted lineage/bytes,
changed patch/preimage/postimage/path/mode, source drift, reordered wrappers,
duplicate plan/decision/outcome consumption, and failed test evidence.
G31-23B additionally rejects unsuccessful/repeated G31-23A outcome, V1 or
`CREATE_ONLY` substitution, changed test receipt/cwd/command, and source or
disposable drift.  It returns only:

`acceptance_prerequisites_satisfied=true`, `ready_for_acceptance=true`,
`result_accepted=false`, `mutation_authorized=false`, and
`main_repository_mutated=false`.

That state is evidence-only readiness.  It is not content acceptance, source
mutation authorization, source application, commit, deployment, or release.

## Minimal staged future plan

| Independently commit-ready stage | Exact bounded change | Reused contracts / projected files | Tests, side effects, and stop state |
|---|---|---|---|
| 1. G31-24D-R02 post-task review to G31-23A review | after a satisfied task decision, prepare/reconstruct the disposable-validation review, retain the capture, render its canonical presentation, and collect only its distinct human decision | `aigol/cli/aicli.py` plus focused AiCLI test; reuse G31-23A prepare/record/reconstruct and existing Human Interface presentation support | plan/decision Replay only; no patch, command, Worker, Provider, acceptance or source write; stop with a recorded disposable application decision |
| 2. G31-24D-R03 certified disposable execution continuation | consume only Stage-1 approval and invoke/reconstruct G31-23A execution | thin AiCLI continuation plus focused test; reuse `execute_disposable_patch_validation` | disposable copy, disposable patch, fixed test command, outcome Replay; source remains unchanged; independently commit-ready |
| 3. G31-24D-R04 ready-for-acceptance binding | consume only the successful Stage-2 outcome and invoke/reconstruct G31-23B binder | thin continuation plus focused test; reuse `bind_codex_replacement_acceptance_prerequisites` | immutable V2 evidence/Replays only; stop `ready_for_acceptance=true` before content acceptance; independently commit-ready |

The first missing transition is Stage 1, not a direct V2 decision implementation.
Stages 2 and 3 must not be folded into its prompt because Stage 2 crosses the
first command/disposable-write boundary and Stage 3 consumes its exact result.

## Validation and protected baseline

Focused read-only fixture tests completed with no conflict against certification
evidence:

| Command scope | Result |
|---|---|
| G31-23A disposable boundary | `20 passed in 216.09s` |
| G31-23B prerequisite binding | `12 passed in 540.83s` |
| AiCLI/G31 result-review/manifest/content-test/acceptance/mutation focused group | `134 passed in 395.67s` |
| targeted `py_compile` for every inspected runtime and AiCLI module | passed |
| governance confirmation | `5 passed in 0.03s` |
| parent and three nested `git diff --check` checks | passed |
| governance conformance engine | `PARTIALLY_CONFORMANT`: 18 passed, two known hook mismatches, zero critical violations; report `0790499e...cbea` |

No full suite was needed.  The pre-audit protected hashes were:

`a626a69a...0203`, `e82f47c0...e787`, `07b95505...99dd`,
`d47a06d5...9e24`, `a73a499e...8cb3`, `dbc7b63f...6161`, and the three
empty-marker hashes `e3b0c442...b855`.  Parent protected state and all three
nested repository worktrees were unchanged at baseline.

## Progress and next state

Evidence-scoped G31 reachability is **95.0%**: the exact certified path and
every input are known, but its first three production calls remain unbound.
Whole-project evidence-scoped progress is **95.0%**.  Runtime behavior did not
change in this audit.

Exactly one next state:

`G31_24D_R02_AICLI_POST_TASK_OUTCOME_TO_DISPOSABLE_VALIDATION_REVIEW_REQUIRED`

### Bounded G31-24D-R02 implementation prompt

Implement only the AiCLI continuation from an already recorded
`TASK_OUTCOME_SATISFIED` decision to existing
`prepare_disposable_patch_validation_review`, its reconstruction, canonical
presentation, and one distinct existing disposable-application human decision
via `record_disposable_patch_validation_human_decision`.  Retain only the two
new captures needed for that pending flow; reuse existing upstream captures and
Replay.  Touch only `aigol/cli/aicli.py`, its focused test(s), and one G31-24D-R02
governance report.  Do not call `execute_disposable_patch_validation` or the
G31-23B binder; do not create a disposable worktree, apply a patch, run a
command, invoke Worker/Provider, accept content, authorize source mutation, or
write the selected source repository.  Require exact V2 satisfied lineage and
fail closed otherwise.  Add focused happy-path, unsatisfied/rework, duplicate,
cross-session, and no-authority tests; do not commit protected paths.

## Documentation-only commit commands

```bash
git add docs/governance/G31_24D_R01_AICLI_TO_G31_23B_READY_FOR_ACCEPTANCE_REACHABILITY_AUDIT.md
git commit -m "docs(governance): audit AiCLI replacement readiness reachability"
```

These commands intentionally exclude every protected runtime-evidence path and
root marker.
