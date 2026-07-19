# G31-24D-R02 AiCLI Task-Outcome to G31-23A Review/Decision Binding

Date: 2026-07-18  
Verdict: `G31_AICLI_G31_23A_REVIEW_DECISION_BINDING_OPERATIONAL`

## Baseline and scope

Implemented only R01 Stage 1 from committed baseline `ae48ed33`
(`docs(governance): audit AiCLI ready-for-acceptance reachability`). G30 remains
constitutionally closed. G31-23A and G31-23B remain immutable owners.

After an exact valid `TASK_OUTCOME_SATISFIED` result, AiCLI now prepares and
reconstructs the existing G31-23A disposable-validation review, presents it,
records one distinct `APPROVE` or `REJECT` decision through the existing generic
human-decision family, reconstructs its Replay, and stops. It does not execute
the disposable operation or create G31-23B evidence.

## Changed surface

| File | Change |
|---|---|
| `aigol/cli/aicli.py` | thin contextual state, `/approve` and `/cancel` routing, exact public-owner calls, and truthful stop flags |
| `aigol/runtime/codex_satisfied_outcome_disposable_validation_binding_runtime.py` | existing-owner review renderer only |
| `tests/test_g31_24d_r02_aicli_task_outcome_to_disposable_review_binding.py` | six focused positive, pending, negative, command, tamper, and no-downstream-call regressions |
| this report | certification evidence |

Production additions are exactly **160 lines** across the two permitted files;
no production module, schema, artifact family, command runner, or mutation path
was added.

## Reused contracts and continuation

AiCLI reuses:

1. `record_codex_task_outcome_human_decision` and its reconstructor;
2. `prepare_disposable_patch_validation_review` and
   `reconstruct_disposable_patch_validation_review`;
3. `record_disposable_patch_validation_human_decision`;
4. `reconstruct_human_decision_replay` and its existing `APPROVE`/`REJECT`
   vocabulary; and
5. the G31-23A immutable two-step plan Replay and generic two-step
   human-decision Replay.

The existing seven upstream captures remain in `runtime_result`; no copies were
added. AiCLI retains only the G31-23A review while a decision is pending, then
the recorded decision capture and reconstruction. The G31-23A owner reconstructs
the upstream lineage before emitting plan evidence.

`/satisfied` records task satisfaction but does not authorize execution. On a
valid continuation it presents the exact Worker result, patch, target path,
disposable destination, focused command, and the source-only boundary. `/approve`
records `APPROVE`; `/cancel` records `REJECT`; both clear the pending review and
stop with `DISPOSABLE_PATCH_VALIDATION_HUMAN_DECISION_RECORDED`. Ambiguous or
out-of-context commands do not create disposable evidence. Unsatisfied/rework
behavior is unchanged.

## Truth and authority boundary

Before the decision:

```text
task_outcome_satisfied=true
disposable_patch_validation_review_pending=true
disposable_patch_validation_decision_recorded=false
disposable_patch_validation_executed=false
ready_for_acceptance=false
result_accepted=false
mutation_authorized=false
main_repository_mutated=false
```

After either recorded G31-23A decision, `review_pending=false` and
`decision_recorded=true`; every other displayed boundary truth above remains
false. An approved decision is compatible with the future
`execute_disposable_patch_validation` contract, but R02 does not call it.

The focused spies prove no call to `execute_disposable_patch_validation`,
`bind_codex_replacement_acceptance_prerequisites`, or
`accept_generated_content`. No validation command, patch application,
authorization, source write, content acceptance, or ready-for-acceptance state
occurred. The existing source-snapshot/reconstructor checks fail closed for
changed task decision, output/patch, scope, source hash, cross-session replay,
substitution, ordering, duplicate destination, and prior consumption.

## PTY evidence

One real PTY-backed `./aicli` run used a disposable Git repository, one
implementation file, one focused test, and a deterministic bounded `codex`
transport shim. It reached `TASK_OUTCOME_SATISFIED`, rendered
`Captured Disposable Patch Validation Review`, and recorded `APPROVE` with
approval scope `APPLY_REVIEWED_PATCH_AND_RUN_GROUNDED_TESTS_IN_DISPOSABLE_WORKSPACE_ONLY`.
Its generic human-decision Replay reconstructed to `APPROVE`.

The selected source SHA-256 was unchanged before and after:
`bd12492ff3e10bcc46c6bd0ab7bcc007224a00151367b02110942400718b0709`.
The disposable Git worktree stayed clean; no planned disposable workspace and
no G31-23B binding directory existed. The disposable repository and runtime
were removed after observation.

## Validation

| Scope | Result |
|---|---|
| R02 focused | `6 passed in 192.92s` |
| G31-22B plus G31-23A | `24 passed in 277.34s` |
| G31-23B, G31-22A, Human Interface | `33 passed in 624.76s` |
| complete repository suite | `6539 passed, 4 skipped in 1674.16s` |
| changed Python `py_compile` and `git diff --check` | passed |
| governance confirmation | `5 passed in 0.03s` |
| governance conformance engine | `PARTIALLY_CONFORMANT`: 18 passed, two pre-existing hook mismatches, zero critical violations; `0790499e...cbea` |

Parent and nested `git diff --check` passed. The nine protected hashes remained
exactly `a626a69a...0203`, `e82f47c0...e787`, `07b95505...99dd`,
`d47a06d5...9e24`, `a73a499e...8cb3`, `dbc7b63f...6161`, and three
`e3b0c442...b855` marker hashes. Runtime behavior outside the exact new G31
continuation is unchanged.

## Next state and commit commands

G31 reachability advances to **96.0%**; whole-project evidence-scoped progress
is **95.5%**.

Exactly one next state:

`G31_24D_R03_AICLI_G31_23A_DISPOSABLE_EXECUTION_BINDING_REQUIRED`

Do not implement R03 here. It may consume only a recorded approving decision,
call the existing G31-23A execution owner, and stop at its successful disposable
outcome before G31-23B binding.

```bash
git add \
  aigol/cli/aicli.py \
  aigol/runtime/codex_satisfied_outcome_disposable_validation_binding_runtime.py \
  tests/test_g31_24d_r02_aicli_task_outcome_to_disposable_review_binding.py \
  docs/governance/G31_24D_R02_AICLI_TASK_OUTCOME_TO_G31_23A_REVIEW_DECISION_BINDING.md
git commit -m "feat(governance): bind AiCLI disposable validation review"
```

These commands exclude all protected runtime evidence and root markers. No
commit was created by R02.
