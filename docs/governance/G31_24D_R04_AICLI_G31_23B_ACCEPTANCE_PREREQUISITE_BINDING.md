# G31-24D-R04 AiCLI G31-23B Acceptance-Prerequisite Binding

Date: 2026-07-19  
Verdict: `G31_AICLI_G31_23B_ACCEPTANCE_PREREQUISITE_BINDING_OPERATIONAL`

## Baseline and bounded result

The implementation baseline is committed R03 commit
`7672cc2b077b013d96a51877510616bd8fe0c694`
(`feat(cli): bind approved disposable validation execution`). The older
`10b13103` commit is only the pre-R03 baseline. Committed R01, R02, and R03
reports and their accepted verdicts were verified before editing. G30 and G31
through R03 remain immutable.

AiCLI now connects one exact successful R03 disposable outcome to the existing
`bind_codex_replacement_acceptance_prerequisites` owner exactly once,
reconstructs its existing Replay, presents the V2 `REPLACE_CONTENT` readiness
evidence, and stops. Failed R03 outcomes preserve their existing recorded
outcome stop and never call the binder.

The endpoint is ready for a later human content-acceptance decision. It does
not collect such a decision, accept content, authorize mutation, apply the
replacement to the source, invoke another Worker/Provider, or run another
patch/test command.

## Changed surface and line accounting

| File | Change |
|---|---|
| `aigol/cli/aicli.py` | success-only R03 continuation, exact ten-capture binder call, reconstruction, state retention, and presentation; 57 insertions, one deletion |
| `aigol/runtime/codex_replacement_acceptance_prerequisite_binding_runtime.py` | existing-owner canonical readiness renderer only; 40 insertions |
| `tests/test_g31_24d_r02_aicli_task_outcome_to_disposable_review_binding.py` | later-stage compatibility controls; six insertions, three deletions |
| `tests/test_g31_24d_r03_aicli_disposable_execution_binding.py` | successful R03 continuation compatibility while failed R03 still stops; eight insertions, five deletions |
| `tests/test_g31_24d_r04_aicli_acceptance_prerequisite_binding.py` | five deterministic AiCLI binding, exact-input, failure, drift, Replay, and no-downstream regressions; 229 lines |
| this report | certification evidence |

The production delta is exactly **97 insertions** across the two permitted
production files. No production module, schema, artifact family, manifest
family, decision system, Replay subsystem, command runner, mutation path, or
workflow engine was added. G31-23B binder semantics are unchanged.

## Reused symbols and exact call chain

The only new production symbols are private AiCLI helper
`_bind_contextual_replacement_acceptance_prerequisites` and public existing-
owner renderer `render_codex_replacement_acceptance_prerequisites`.

```text
run_reference_uhi_session
  -> existing R03 outcome and reconstruction
  -> _bind_contextual_replacement_acceptance_prerequisites
  -> bind_codex_replacement_acceptance_prerequisites
     -> existing G31-23A review/outcome reconstructors
     -> create_replacement_implementation_manifest
     -> validate_generated_content
     -> validate_generated_tests
     -> bind_generated_content_acceptance_prerequisites
  -> reconstruct_codex_replacement_acceptance_prerequisite_binding
  -> render_codex_replacement_acceptance_prerequisites
  -> stop: REPLACEMENT_ACCEPTANCE_PREREQUISITES_BOUND
```

AiCLI contains no manifest, validation, hashing, serialization, Replay, patch,
subprocess, acceptance, or mutation implementation.

## Exact ten-capture binding

| G31-23B parameter | Existing AiCLI/R03 capture |
|---|---|
| `disposable_validation_outcome_capture` | `disposable_patch_validation_outcome_capture` |
| `disposable_validation_review_capture` | `disposable_patch_validation_review_capture` |
| `application_decision_capture` | `disposable_patch_validation_human_decision_capture` |
| `task_outcome_decision_capture` | `codex_task_outcome_human_decision_capture` |
| `task_outcome_review_capture` | `codex_task_outcome_review_capture` |
| `result_capture_binding_capture` | `codex_worker_result_capture_binding_capture` |
| `governance_validation_binding_capture` | `codex_worker_semantic_validation_binding_capture` |
| `activation_capture` | `codex_worker_activation_capture` |
| `governed_execution_capture` | `governed_worker_execution_capture` |
| `execution_candidate_capture` | `worker_execution_candidate_capture` |

The R04 call-spy captured these exact objects and proved one binder call, one
R03 disposable execution, and one approved focused command. The binder itself
reconstructs all review, decision, result, validation, activation, execution,
candidate, disposable-outcome, human-decision, and validation-command Replay.
No duplicate projection is retained. AiCLI retains only the canonical binding
capture and its public reconstruction for the future acceptance owner.

## V2 manifest, Replay, and readiness

Successful binding produced the existing V2 implementation manifest with
`operation_mode=REPLACE_CONTENT`, exact source-relative path, preimage hash,
postimage hash, unchanged regular-file type/mode, exact patch, and exact
focused-test receipt. Existing V2 generated-content, generated-test, and
acceptance-prerequisite artifacts validated successfully. The binding Replay
reconstructed to the exact binding hash with one artifact; the implementation
manifest Replay reconstructed with two artifacts.

The canonical presentation includes path, operation, original and replacement
hashes, content/test/disposable results, binding identity/hash, Replay
reference/hash, and the explicit boundary:

```text
acceptance_prerequisites_satisfied=true
ready_for_acceptance=true
result_accepted=false
mutation_authorized=false
main_repository_mutated=false
```

Readiness is evidence that an existing later human acceptance step may be
reached. It is not acceptance or mutation authority.

## Fail-closed and side-effect evidence

R04 focused tests prove that failed focused validation stops before the binder,
source drift is rejected by canonical upstream reconstruction before binding,
and changed disposable postimage or cross-session outcome Replay creates no
readiness or downstream authority. Existing G31-23A/B focused coverage proves
failed patch application, changed original/replacement bytes, path/type/mode/
operation drift, Worker/decision/grounding lineage substitution, Replay
reordering, duplicate destination/consumption, symlink/traversal/aliasing, and
V1/`CREATE_ONLY` substitution fail closed.

Explicit spies prove `accept_generated_content` and
`authorize_filesystem_mutation` were never called. Execution and validation
call counts prove there was no second disposable execution or test command.
The source file hash and source Git status remained unchanged. No acceptance
artifact, source mutation authorization, main-repository write, commit,
deployment, or release occurred.

## PTY observation

One complete PTY-backed `/home/pisarna/work/sapianta/aicli` workflow ran from
the exact approved isolated source workspace with an isolated runtime, one
implementation file, one focused test, an ordinary bounded request, the
existing contextual decisions, and exact G31-23A `APPROVE`. It completed one
disposable patch application, one focused command, and one G31-23B binding.

Canonical output reported:

```text
DISPOSABLE_PATCH_AND_TEST_VALIDATION_COMPLETED
REPLACE_CONTENT
Acceptance Prerequisites Satisfied: True
Ready For Human Acceptance: True
Result Accepted: False
Mutation Authorized: False
Main Repository Mutated: False
exit_reason: REPLACEMENT_ACCEPTANCE_PREREQUISITES_BOUND
```

The source SHA-256 remained
`bd12492ff3e10bcc46c6bd0ab7bcc007224a00151367b02110942400718b0709`
with clean source Git status. The disposable postimage SHA-256 was
`5f2348364df38839f728dacf6a5ba20f8dee5b6ed2dd61a327f877e69f72d529`.
Read-only reconstruction reported V2 `REPLACE_CONTENT`, manifest Replay count
two, binding Replay count one, validation-command Replay count three, and test
exit code zero. Exactly one binding wrapper and zero generated-content
acceptance or filesystem-mutation-authorization artifacts existed.

A preliminary harness invocation used the wrong current directory and failed
closed before Worker activation; it ran no command, patch, disposable
execution, binder, acceptance, or mutation. The corrected invocation above was
the sole complete PTY workflow. All temporary source, disposable, runtime, and
preflight resources were removed afterward.

## Validation and constitutional evidence

| Scope | Exact result |
|---|---|
| R04 focused | `5 passed, 0 skipped, 0 failed, 0 deselected in 349.54s` |
| R02/R03, G31-23A/B, manifest, content/test validation, Replay, Human Interface/AiCLI, Governance | `98 passed, 0 skipped, 0 failed, 0 deselected in 1213.10s` |
| complete repository suite, run once | `6548 passed, 4 skipped, 0 failed in 2326.02s (0:38:46)` |
| changed Python `py_compile` | passed |
| parent and three nested `git diff --check` | passed |
| governance confirmation | `5 passed in 0.03s` |
| governance conformance engine | `PARTIALLY_CONFORMANT`: 18 passed, two pre-existing hook mismatches, zero critical violations; report `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea` |

The nine protected hashes remain exactly `a626a69a...0203`,
`e82f47c0...e787`, `07b95505...99dd`, `d47a06d5...9e24`,
`a73a499e...8cb3`, `dbc7b63f...6161`, and three
`e3b0c442...b855` marker hashes. All nested repositories remain clean.

## Git status, progress, and next state

Final status contains only the nine protected pre-existing paths, the two
modified production files, two compatibility tests, the new R04 test, and this
report. Nothing is staged and no commit was created.

G31 evidence-scoped reachability advances to **98.0%**. Whole-project
evidence-scoped progress advances to **96.5%**.

Exactly one next state:

`G31_24D_VERSIONED_HUMAN_CONTENT_ACCEPTANCE_DECISION_IMPLEMENTATION_REQUIRED`

```bash
git add \
  aigol/cli/aicli.py \
  aigol/runtime/codex_replacement_acceptance_prerequisite_binding_runtime.py \
  tests/test_g31_24d_r02_aicli_task_outcome_to_disposable_review_binding.py \
  tests/test_g31_24d_r03_aicli_disposable_execution_binding.py \
  tests/test_g31_24d_r04_aicli_acceptance_prerequisite_binding.py \
  docs/governance/G31_24D_R04_AICLI_G31_23B_ACCEPTANCE_PREREQUISITE_BINDING.md
git commit -m "feat(cli): bind replacement acceptance prerequisites"
```

These commands exclude every protected path.
