# G31-24D-R03 AiCLI G31-23A Disposable Execution Binding

Date: 2026-07-19  
Verdict: `G31_AICLI_G31_23A_DISPOSABLE_EXECUTION_BINDING_OPERATIONAL`

## Baseline and bounded result

Implemented only R01 Stage 2 from committed baseline `10b13103`
(`feat(cli): bind satisfied outcomes to disposable validation review`). The
committed R01 and R02 reports were verified before editing. G30 and accepted
G31 work through R02 remain immutable.

After an exact positive R02 G31-23A decision, AiCLI now calls the existing
`execute_disposable_patch_validation` owner exactly once, reconstructs its
immutable outcome Replay, presents the canonical outcome, retains the evidence
needed by the later G31-23B binder, and stops. It does not perform G31-23B
binding, content acceptance, mutation authorization, or source mutation.

## Changed surface and line accounting

| File | Change |
|---|---|
| `aigol/cli/aicli.py` | thin approved-decision continuation and existing-owner call; 49 insertions, one deletion |
| `aigol/runtime/codex_satisfied_outcome_disposable_validation_binding_runtime.py` | canonical outcome renderer in the existing owner; 23 insertions |
| `tests/test_g31_24d_r02_aicli_task_outcome_to_disposable_review_binding.py` | R02 positive-path compatibility with the now-completed R03 continuation; seven insertions, six deletions |
| `tests/test_g31_24d_r03_aicli_disposable_execution_binding.py` | deterministic success, rejection, decision-substitution, failure, Replay, source-isolation, and downstream-spy evidence |
| this report | certification evidence |

The production delta is exactly **72 insertions** across the two permitted
production files. No module, schema, artifact family, runner, patch engine,
authorization system, Replay system, or orchestration framework was added.

## Symbols, contracts, and call chain

New production symbols are private AiCLI helper
`_execute_contextual_disposable_patch_validation` and public existing-owner
renderer `render_disposable_patch_validation_outcome`. The positive branch of
`run_reference_uhi_session` is the only changed caller.

The exact chain is:

```text
run_reference_uhi_session
  -> existing R02 review and exact APPROVE decision capture
  -> _execute_contextual_disposable_patch_validation
  -> execute_disposable_patch_validation
     -> existing governed disposable repository mutation owner
     -> existing generated-content validation owner
     -> existing certified validation-command runner
     -> existing generated-test validation owner
  -> reconstruct_disposable_patch_validation_outcome
  -> render_disposable_patch_validation_outcome
  -> stop: DISPOSABLE_PATCH_VALIDATION_OUTCOME_RECORDED
```

The continuation reuses the R02 review and decision captures, the existing
generic human-decision reconstruction, all seven upstream lineage captures,
the G31-23A two-step plan, `execute_disposable_patch_validation`, governed
repository mutation, content and focused-test validation, validation-command
execution, immutable serialization/hashing/writing, and the existing outcome
reconstructor. AiCLI contains no patch, subprocess, hashing, or validation
implementation.

## Approval, command, and isolation boundary

`/satisfied` alone remains insufficient. Only the exact unused `APPROVE`
decision bound to the exact review subject and scope reaches execution. R02
`REJECT` still creates no disposable destination and invokes no execution.
Decision substitution fails before command execution.

The existing owner verifies source identity and preimage, approved patch,
target path/type/mode, plan and decision lineage, deterministic destination,
source/disposable separation, destination containment, Replay ordering, and
single-use state. It applies only inside the disposable Git repository. The
existing command runner receives the approved argument vector, disposable
working directory, timeout, and bounded environment; `shell_execution_used`
is false.

The focused success captured exactly:

```text
command = ["python", "-m", "pytest", "tests/test_human_interface.py"]
cwd = <deterministic disposable workspace>
exit_code = 0
shell_execution_used = false
```

Existing G31-23A tests supply the broader fail-closed coverage for changed
patch/source/command, traversal, symlink, alias, cross-session and reordered
Replay, duplicate destination/consumption, and mutation/test failure. R03 adds
the exact AiCLI-bound positive, negative, substituted-decision, no-retry, and
no-downstream-call evidence.

## Successful and failed outcomes

The successful continuation preserves:

```text
task_outcome_satisfied=true
disposable_patch_validation_decision_recorded=true
disposable_patch_validation_approved=true
disposable_patch_validation_executed=true
disposable_patch_application_succeeded=true
focused_validation_executed=true
focused_validation_succeeded=true
ready_for_acceptance=false
result_accepted=false
mutation_authorized=false
main_repository_mutated=false
```

A deterministic failing focused-test fixture produced the existing
`FAILED_CLOSED` outcome after disposable patch application, recorded command
failure and Replay, performed no automatic retry, left acceptance and mutation
false, and preserved the source repository. A substituted decision raised the
existing fail-closed error before the validation command ran.

The outcome reconstructor returned one matching immutable outcome artifact.
Required upstream review, decision, task-outcome, Worker result, validation,
activation, governed-execution, and candidate captures remain available in
`runtime_result` for the later G31-23B owner.

Explicit spies remained zero for
`bind_codex_replacement_acceptance_prerequisites`,
`accept_generated_content`, and `authorize_filesystem_mutation`. No CODEX,
Worker, Provider, acceptance, authorization, source patch, or G31-23B evidence
was created by this continuation.

## PTY observation

One PTY-backed `./aicli` run used an isolated runtime and disposable source Git
repository, one implementation file, one focused test, a bounded natural
language request, and the existing contextual decisions through exact G31-23A
`APPROVE`. The canonical presentation reported
`DISPOSABLE_PATCH_AND_TEST_VALIDATION_COMPLETED`, patch/content/test success,
`Source Repository Unchanged: True`, and all acceptance/mutation truths false.

The exact focused command reconstructed with exit code zero; the governed
mutation Replay reconstructed with nine artifacts. The source file SHA-256
remained
`bd12492ff3e10bcc46c6bd0ab7bcc007224a00151367b02110942400718b0709`;
the disposable postimage was
`5f2348364df38839f728dacf6a5ba20f8dee5b6ed2dd61a327f877e69f72d529`.
Source `git status --short` remained empty. No G31-23B or acceptance evidence
existed. The isolated runtime and both disposable repositories were removed.

## Validation and constitutional evidence

| Scope | Exact result |
|---|---|
| R03 focused | `4 passed, 0 skipped, 0 failed, 0 deselected in 216.61s` |
| R02, G31-23A, validation runner, G31-22A, Human Interface focused | `53 passed, 0 skipped, 0 failed, 0 deselected in 523.45s` |
| complete repository suite | `6543 passed, 4 skipped, 0 failed in 1924.13s (0:32:04)` |
| changed Python `py_compile` | passed |
| parent and nested `git diff --check` | passed |
| governance confirmation | `5 passed in 0.03s` |
| governance conformance engine | `PARTIALLY_CONFORMANT`: 18 passed, two pre-existing hook mismatches, zero critical violations; report `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea` |

The protected artifact hashes remained exactly `a626a69a...0203`,
`e82f47c0...e787`, `07b95505...99dd`, `d47a06d5...9e24`,
`a73a499e...8cb3`, `dbc7b63f...6161`, and three
`e3b0c442...b855` marker hashes. All nested repositories remained clean.
Runtime behavior outside the exact positive G31 continuation is unchanged.

## Git status, progress, and next state

The final status contains only the nine protected pre-existing paths, the two
modified production files, the R02 compatibility test, the new R03 test, and
this report. Nothing is staged and no commit was created.

G31 reachability advances to **97.0%**. Whole-project evidence-scoped progress
is **96.0%**.

Exactly one next state:

`G31_24D_R04_AICLI_G31_23B_ACCEPTANCE_PREREQUISITE_BINDING_REQUIRED`

R04 may bind this successful reconstructed outcome to the existing G31-23B
prerequisite owner only. It must not imply content acceptance, mutation
authorization, or source application.

```bash
git add \
  aigol/cli/aicli.py \
  aigol/runtime/codex_satisfied_outcome_disposable_validation_binding_runtime.py \
  tests/test_g31_24d_r02_aicli_task_outcome_to_disposable_review_binding.py \
  tests/test_g31_24d_r03_aicli_disposable_execution_binding.py \
  docs/governance/G31_24D_R03_AICLI_G31_23A_DISPOSABLE_EXECUTION_BINDING.md
git commit -m "feat(cli): bind approved disposable validation execution"
```

These commands exclude every protected path.
