# G31-23A Canonical Disposable Patch Application and Test Validation Boundary

Date: 2026-07-18  
Verdict: `G31_DISPOSABLE_PATCH_APPLICATION_REQUIRES_EXISTING_ACCEPTANCE_PREREQUISITE_BINDING`

## Scope and baseline

G31-23A implements the smallest canonical boundary from one exact V2
`TASK_OUTCOME_SATISFIED` unified diff to separately approved application,
content checking, and one focused test in a fresh disposable repository. It
does not reinterpret the historic G31-22B V1 result, mutate the main
repository, start CODEX or a Provider, install a package, use the network,
accept content, commit, deploy, or release.

| Baseline | Observed |
|---|---|
| parent HEAD | `406c41276d23bb5c7fab69f517a237555dc0c5e0` |
| parent subject | `fix(governance): align task outcome with unified diff contract` |
| nested `sapianta_system` HEAD | `3183bab71f8f30397c0309dd2e6d846d14a11f66` |
| nested worktree | clean |
| pre-existing non-protected changes | `aigol/runtime/human_decision_runtime.py`; one G31-22B fixture hunk-count correction |

The two pre-existing non-protected changes and all nine protected paths were
preserved and excluded from this phase.

## Canonical owner audit

| Concern | Existing canonical owner | G31-23A use or gap |
|---|---|---|
| unified-diff syntax and scope | `codex_task_outcome_human_review_runtime.py::_parse_unified_diff` | Extended in place to expose validated hunks and derive exact postimages against exact preimages. No second parser or patch engine was created. |
| repository preimage | `approved_durable_work_repository_scope_grounding.py::_observe_target` and activation reconstruction | Reconstructs the exact implementation/test pair and byte SHA-256 evidence. G31-23A additionally binds a complete non-`.git` source snapshot and rejects symlinks. |
| bounded existing-file application | `governed_repository_mutation_runtime.execute_governed_repository_mutation` and `repository_mutation_worker_runtime.apply_repository_mutation` | Applies only exact derived `REPLACE_CONTENT` postimages inside the approved `/tmp` copy. |
| content validation | governed repository mutation postimage verification plus its fixed `git diff --check` validation command | Reused. Content passes only when the existing mutation workflow completes and every changed postimage hash matches. |
| fixed test execution | `validation_command_runner_runtime` | Reused with `shell=False`, 30-second timeout, exact disposable cwd, exact grounded pytest target, no retry, and 4,096-byte stdout/stderr retention bounds. |
| test evidence | `VALIDATION_COMMAND_REQUEST_ARTIFACT_V1` / `VALIDATION_COMMAND_RESULT_ARTIFACT_V1` and three-step Replay | Reused. Exit code zero is required for G31 focused-test validation. |
| generated-content manifest | `implementation_manifest_runtime.create_implementation_manifest` | Exact gap: supports `CREATE_ONLY`, requires `MUST_NOT_EXIST`, and cannot truthfully represent an existing-file `REPLACE_CONTENT` patch. |
| generated-content validation | `generated_content_validation_runtime.validate_generated_content` | Exact gap: requires a `CREATE_ONLY` manifest and `CREATE_ONLY` entries. |
| generated-test validation | `generated_test_validation_runtime.validate_generated_tests` | Exact gap: structurally validates manifest test artifacts but does not bind this executed focused-test receipt; it also requires a `CREATE_ONLY` manifest. |
| result evaluation | `result_evaluation_runtime.evaluate_result` | Accepts canonical `RESULT_ARTIFACT_V1`; it is not an application/test owner and grants no acceptance or mutation authority. |
| generated-content acceptance | `generated_content_acceptance_runtime.accept_generated_content` | Requires the manifest plus generated-content and generated-test validation families, all bound to `CREATE_ONLY`, followed by separate human content acceptance. It was not called. |

The application and test boundary is operational. The selected verdict remains
prerequisite-limited because claiming `ready_for_generated_content_acceptance`
without an existing-file replacement manifest would be false. G31-23A records
that gap instead of creating a parallel manifest or weakening the existing
acceptance contract.

## Authority and decision boundary

`TASK_OUTCOME_SATISFIED` is eligibility evidence only. It still records
`repository_mutation_authorized=false` and cannot copy, mutate, or execute a
command.

G31-23A creates a new approval-required artifact and reuses
`human_decision_runtime.record_human_decision`. Only an exact `APPROVE` bound to
this plan, hash, disposable destination, changed paths, and test command grants
one-time authority under:

`APPLY_REVIEWED_PATCH_AND_RUN_GROUNDED_TESTS_IN_DISPOSABLE_WORKSPACE_ONLY`

The human-decision runtime continues to record
`implementation_authorized=false`; G31-23A interprets the decision solely
through the exact narrow scope. The plan and approval explicitly deny:

- main-repository mutation;
- arbitrary command or shell execution;
- package installation;
- network authority;
- Provider invocation;
- CODEX execution;
- commit, deployment, and release.

Rejection or modification cannot enter execution. The decision hash is
one-time: successful or failed consumption blocks reuse.

## Eligibility binding

Before a disposable directory is created, the boundary reconstructs and binds:

1. the original authorized request and repository grounding;
2. both exact grounded preimages and the complete source snapshot;
3. activation receipt and three-step Replay;
4. exact captured patch bytes, byte hash, capture Replay, and governance-
   validation Replay;
5. V2 criteria and their pre-execution activation identity;
6. the exact human `TASK_OUTCOME_SATISFIED` decision and two-step Replay;
7. the allowed grounded target set and actual changed-path subset;
8. exact in-memory derived postimages;
9. the one grounded test path and fixed pytest argv;
10. the exact `/tmp` destination and separate human application/test decision.

### Eligibility truth table

| Input state | Eligible |
|---|---:|
| V2, exact bytes, satisfaction eligible, human `TASK_OUTCOME_SATISFIED`, fresh preimages | yes, for separate review only |
| historic V1 G31-22B plus `TASK_OUTCOME_UNSATISFIED` | no |
| V1 regardless of later reinterpretation | no |
| `TASK_OUTCOME_UNSATISFIED` or `REWORK_REQUESTED` | no |
| missing/substituted bytes, output hash, criteria, Replay, or decision | no |
| malformed, empty, binary, creation/deletion, rename/substitution diff | no |
| ungrounded, absolute, traversal, duplicate, or unsupported target | no |
| hunk/context not matching grounded preimage | no |
| stale source or cross-session lineage | no |
| existing disposable destination or duplicate plan | no |
| missing/rejected/reused application authority | no |

All ineligible states fail before the disposable copy, mutation worker, or test
process.

## Deterministic execution sequence

The successful sequence is:

```text
complete G31 reconstruction
-> V2 satisfied eligibility
-> exact in-memory hunk/preimage validation
-> separate human approval
-> symlink-free source snapshot copy to exact /tmp destination
-> copied preimage verification
-> existing governed REPLACE_CONTENT mutation owner
-> exact postimage verification
-> existing git diff --check content validation
-> existing fixed focused-pytest validation owner
-> bounded result capture
-> STOP
```

The governed mutation owner writes complete postimages rather than executing
arbitrary `git apply`. In-memory hunk application plus exact context, hunk
count, preimage, and postimage verification is the canonical equivalent of
`git apply --check` for this existing-file text scope.

### Failure truth table

| Failure | Patch applied | Tests run | Retry/repair | Acceptance readiness |
|---|---:|---:|---:|---:|
| eligibility, path, criteria, hash, preimage, or hunk preflight | false | false | false | false |
| separate human rejection/modification | false | false | false | false |
| copy or mutation-owner failure | false | false | false | false |
| postimage or `git diff --check` content failure | may be true only in disposable copy | false | false | false |
| focused pytest nonzero | true in disposable copy | true once | false | false |
| all application/content/test checks pass | true in disposable copy | true once | false | still false pending manifest-family extension |

Every outcome preserves `main_repository_mutated=false`,
`result_accepted=false`, and `repository_mutation_authorized=false`.

## Deterministic confirmation

One explicit confirmation used only `/tmp` fixtures and a deterministic
recording adapter for the already-established upstream CODEX receipt.

| Item | Value |
|---|---|
| confirmation root | `/tmp/g31-23a-confirmation-p0nHUb` |
| source repository | `/tmp/g31-23a-confirmation-p0nHUb/G31-23A-CONFIRM-source` |
| disposable repository | `/tmp/g31-23a-confirmation-p0nHUb/G31-23A-CONFIRM-disposable` |
| changed path | `aigol/runtime/human_interface.py` |
| unchanged grounded test | `tests/test_human_interface.py` |
| patch SHA-256 | `sha256:78a8f292b3a243717f4375b6fbae99d0dcd51999dc1a1341ddbd5c7d2ce51a88` |
| fixed test command | `python -m pytest tests/test_human_interface.py` |
| test cwd | exact disposable repository |
| timeout | 30 seconds |
| shell | false |
| test exit code | 0 |
| stdout bytes / hash / truncated | 390 / `sha256:976e55c362c8c83a385a2f796d7452c35d38dffbebdc6ef45b738f7c61d21335` / false |
| stderr bytes / hash / truncated | 0 / `sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` / false |

### Artifact and Replay identities

| Family | Identity/hash | Count / Replay hash |
|---|---|---|
| application/test plan | `G31-DISPOSABLE-VALIDATION-45fcc0e34f32012f2da7bb45`; artifact `sha256:286dec109246ec7ceee9d43ee983e353c797017cd84dafea9eb74d40a44b4e2c` | 2 / `sha256:b8f5300692d145dd2c98a2230d0eb4ea2de356242ed18acf535255c81c3e884b` |
| separate human authority | decision `sha256:c8add719030e4e9233f26753987706cd6455a732c878a9717170469af0dbdf6f` | 2 / `sha256:c7fe08f67d9c7a76ab8646ccb6dd9925251de2b58c57b543bb333848f9518abf` |
| governed disposable mutation/content validation | outcome `sha256:842b044a5715b62b8a7d1f9f949cf0f8cc3fba1b65cb2ca34796c10878b03afc` | 9 / `sha256:f599242ad6a96164b9019a2451968e960e727805aff4a082bfac643ac6f2458d` |
| focused test validation | result `sha256:e67ae6d6008482d3e6d8b0612c7a3393e66884bcf78055833bdb888e69f3df27` | 3 / `sha256:c8d438cf8269874ab1901f7b99a5199365abb15026381a956691125cba807ca3` |
| G31-23A outcome | `G31-DISPOSABLE-VALIDATION-45fcc0e34f32012f2da7bb45:OUTCOME`; artifact `sha256:76f71c225197b1fe3cd8d532978f626d7322e4020ac7ba9b54f975a7a457d60e` | 1 / `sha256:386b7efc471831f677d0f1a1cb0f52d9096a3c58a95a6fa8acd335bfe1f7499e` |

Successful truth:

| Field | Value |
|---|---:|
| `task_outcome_satisfaction_evaluated` | true |
| `task_outcome_satisfied` | true |
| `task_outcome_criteria_version` | V2 |
| `disposable_patch_application_authorized` | true |
| `disposable_patch_applied` | true |
| `main_repository_mutated` | false |
| `content_validation_performed` / `passed` | true / true |
| `grounded_test_execution_performed` / `passed` | true / true |
| `generated_content_manifest_created` | false; truthful prerequisite gap |
| `ready_for_generated_content_acceptance` | false |
| `result_accepted` / `repository_mutation_authorized` | false / false |
| `provider_invoked` / `codex_process_started` | false / false |
| `commit_created` / `deployed` / `released` | false / false / false |

### Source and disposable hashes

| Path | Source before | Source after | Disposable after |
|---|---|---|---|
| `aigol/runtime/human_interface.py` | `bd12492ff3e10bcc46c6bd0ab7bcc007224a00151367b02110942400718b0709` | same | `5f2348364df38839f728dacf6a5ba20f8dee5b6ed2dd61a327f877e69f72d529` |
| `tests/test_human_interface.py` | `d1efbafd04fa1a851924e8b0b2159c27913a3d502de3bd4cbef3cbcd55b706e3` | same | same |

The source Git worktree remained clean. The disposable worktree contained only
the expected source change plus pytest `__pycache__` files. No `codex exec`
process remained or was started by this phase.

## Historic G31-22B exclusion

The boundary checks V2 before any satisfaction or application logic. Its
focused regression supplies the historic combination—V1 criteria plus
`TASK_OUTCOME_UNSATISFIED`—and proves it fails with `requires V2`.

The retained historic wrapper SHA-256 values remain:

| Wrapper | SHA-256 |
|---|---|
| review packet | `fd7a1ceade87d82bfa79207250602dd97abab2d9f8a19742c30fe8eeaebfa01e` |
| review required | `70678ab139079c5a8ed5b740fe605e8ec446822613de06bcba7ff72f577794b7` |
| decision recorded | `017cb1c1350cbce38da1f649c1b455df50f14caf8e9be35554b33e07a2b999c4` |
| decision returned | `8ac33e1fec77af092f6f95339e60793d0751b7ad39e668af252f12763f8b21ea` |

No historic output, criteria, decision, or identity was rewritten.

## Changed surface

| File | Purpose |
|---|---|
| `aigol/runtime/codex_satisfied_outcome_disposable_validation_binding_runtime.py` | new G31 lineage, separate authority, disposable-copy, existing-owner orchestration, outcome Replay, and reconstruction binding |
| `aigol/runtime/codex_task_outcome_human_review_runtime.py` | extends the existing canonical diff parser with validated hunk data and exact in-memory postimage derivation |
| `aigol/runtime/validation_command_runner_runtime.py` | bounds retained stdout/stderr to 4,096 bytes while preserving original lengths and hashes |
| `tests/test_g31_23a_canonical_disposable_patch_application_and_test_validation_boundary.py` | success, eligibility, authority, isolation, failure, output-bound, and acceptance-separation coverage |
| this report | audit and evidence record |

Production change is **1,235 added and 2 removed lines**: 1,125 lines in the
new complete lineage binding, 78 additions in the existing diff owner, and 32
additions/2 removals in the existing validation-command owner. The focused test
module is 564 physical lines. No nested production line changed.

## Validation

| Validation | Result |
|---|---|
| focused G31-23A application/content/test boundary | `20 passed in 215.88s` |
| directly affected mutation, validation, manifest, acceptance, and G31 review owners | `96 passed in 440.59s` |
| G31-17B through G31-23A, including isolation | `128 passed in 643.18s` |
| complete parent suite | `6521 passed, 4 skipped in 922.82s` |
| governance conformance tests | `5 passed in 0.03s` |
| governance engine | `PARTIALLY_CONFORMANT`; 18 passed, two known hook mismatches, zero critical violations; deterministic/read-only/fail-closed; report hash `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea` |
| targeted `py_compile` | passed |
| parent and nested `git diff --check` | passed |

The known root and nested pre-commit-hook drift remains visible and was not
introduced or concealed by G31-23A.

## Protected hashes

All protected SHA-256 values matched before and after:

| Protected path | Before | After |
|---|---|---|
| `diagnostic_evidence.json` | `a626a69a8020bc730876119c52701a94de9ab6e4772cc64c1f5d017296650203` | same |
| `governed_return.json` | `e82f47c0c13678725993b21e2af2e0437edccaed324f861a7b58e77d7f8e787d` | same |
| `lineage.json` | `07b95505521e70f51cdddecc1057fd3a208b198445693c9a8da1e996df5799dd` | same |
| `provider_stderr.txt` | `d47a06d59aba2814c3fb7460049fc2ccbfc834196c956d6c6558e8be8b079e24` | same |
| `provider_stdout.txt` | `a73a499e2e9133c03d7babfd5c4dec7967f31e2bfb354ea9dd41df0a15c08cb3` | same |
| `governed_returns.jsonl` | `dbc7b63f2a17c50c43bbb4fde4f44c1dbae8d25d550fb6b4d4daa14e17126161` | same |
| `WORKER_INVOCATION_ARTIFACT_V1` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | same |
| `WORKER_INVOKED` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | same |
| `invocation` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | same |

## Git status and report-only commit commands

No file is staged and no commit was created. Parent HEAD remains
`406c41276d23bb5c7fab69f517a237555dc0c5e0`. Nested HEAD remains
`3183bab71f8f30397c0309dd2e6d846d14a11f66`, and its worktree is clean.

Parent status contains the nine protected paths, the two pre-existing
non-protected changes, and the intended G31-23A files. Exact future commands
include only G31-23A:

```bash
git add \
  aigol/runtime/codex_satisfied_outcome_disposable_validation_binding_runtime.py \
  aigol/runtime/codex_task_outcome_human_review_runtime.py \
  aigol/runtime/validation_command_runner_runtime.py \
  tests/test_g31_23a_canonical_disposable_patch_application_and_test_validation_boundary.py \
  docs/governance/G31_23A_CANONICAL_DISPOSABLE_PATCH_APPLICATION_AND_TEST_VALIDATION_BOUNDARY.md
git commit -m "feat(governance): validate satisfied Codex patches in disposable workspace"
```

These commands are report-only. They exclude all protected paths,
`aigol/runtime/human_decision_runtime.py`, and the pre-existing G31-22B test
change.

## Progress and recommended next state

Evidence-scoped whole-project progress is revised from **93.5% to 94.0%**.
The exact V2 satisfied result can now be separately approved, applied, content-
checked, and focused-test-validated without changing its source repository.
The remaining gap is not application or test execution; it is truthful binding
of existing-file replacement outputs and executed-test receipts into the
existing canonical generated-content acceptance prerequisites.

Recommended next state:

`G31_EXISTING_FILE_REPLACEMENT_MANIFEST_AND_ACCEPTANCE_PREREQUISITE_BINDING_REQUIRED`
