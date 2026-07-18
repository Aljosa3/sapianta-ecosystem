# G31-22B Live Exact-Byte Task-Outcome Human-Review Confirmation

Date: 2026-07-18
Verdict: `G31_LIVE_TASK_OUTCOME_REVIEW_COMPLETED_UNSATISFIED`

## Scope and baseline

This phase wired the existing G31-22A canonical review owner into the
continuous AiCLI activation/capture/validation call and performed one bounded
live confirmation. The exact authentic CODEX stdout flowed directly from the
single process through G31-18, G31-20, the G31-22A review packet, and one
explicit human task-outcome decision.

The phase did not accept or apply the patch, mutate source, retry, start a
second Worker, invoke a SAPIANTA Provider, create a raw-output artifact family,
commit, deploy, or release.

| Baseline | Observed |
|---|---|
| parent HEAD | `1c2102681fe224d4fd44594b32e1747866b51fbf` |
| parent subject | `feat(governance): add canonical Codex task outcome review` |
| nested `sapianta_system` HEAD | `3183bab71f8f30397c0309dd2e6d846d14a11f66` |
| nested worktree | clean |
| pre-existing parent status | nine protected paths plus unstaged `aigol/runtime/human_decision_runtime.py` |
| pre-existing human-decision runtime SHA-256 | `caf44f50fd42ea6914080d6a448d6a829ae5e1c21cfecc6a1b2b155def15466d` |

The unstaged human-decision change was omitted from the prerequisite commit but
was already present before this phase. It is required by G31-22A to preserve
`implementation_authorization_allowed=false`; this phase preserved it exactly
and did not stage or commit it.

## Minimal AiCLI continuation

The committed G31-22A owner was not yet called by AiCLI. AiCLI previously
stopped after G31-20 rendering. The new continuation:

1. admits review only after `G31_CODEX_SEMANTIC_VALIDATION_OPERATIONAL`;
2. passes the same in-memory activation, exact capture, and validation objects
   directly to `prepare_codex_task_outcome_review`;
3. immediately reconstructs the two-artifact review Replay;
4. renders the exact output, original task, grounded pair, output type,
   pre-execution criteria, observations, capture identity/hash, validation
   identity/hash/status/limited meaning, and unapplied/untested state;
5. waits for one explicit `/satisfied`, `/unsatisfied`, or `/rework` command;
6. transports that choice to the existing G31-22A human-decision binding and
   reconstructs its existing two-artifact Replay;
7. stops without acceptance, mutation, retry, or another Worker.

Invalid G31-20 validation cannot create a review request. Byte or lineage
failure is displayed and retained as a blocker without a fourth decision.
`/cancel` records no task-outcome decision. AiCLI remains presentation and
transport only.

Production change attributable to G31-22B is 274 added and 1 removed line in
`aigol/cli/aicli.py`. The focused integration test is 196 physical lines. The
pre-existing unstaged G31-22A human-decision dependency remains a separate 27
added/2 removed-line worktree change. No nested production line changed.

## Disposable fixture and live request

| Item | Exact value |
|---|---|
| disposable repository | `/tmp/g31-22b-live-WxcphS/repository` |
| disposable runtime root | `/tmp/g31-22b-live-WxcphS/runtime` |
| implementation | `aigol/runtime/human_interface.py` |
| focused test | `tests/test_human_interface.py` |
| repository grounding | exactly one `human_interface` implementation/test pair |
| implementation defect | returns `Status: ready` |
| focused expectation | expects `Summary: ready` |

The exact 163-character request was:

> Fix Summary test: inspect aigol/runtime/human_interface.py and tests/test_human_interface.py; return a minimal Status:-to-Summary: unified diff; do not edit files.

Canonical synthesis prepended 20 characters, producing 183/240 characters.
The final grounded Worker prompt SHA-256 was
`39e5713a21926c1bf7ccf29302bf648ddad7c9a41a4fd79fc32cbcad28a31931`.
It made the exact request primary, named both grounded files, required
`UNIFIED_DIFF`, prohibited edits/retry/Provider/delegation/networking, and
required read-only inspection of the focused test.

## Live transport, capture, and validation truth

| Field | Live value |
|---|---|
| human execution decisions | 3 |
| task-outcome decisions | 1 |
| total human decisions | 4 |
| process start count | 1 |
| command | fixed `codex exec <bounded_prompt>` |
| `shell` | false |
| timeout contract | exactly 60 seconds |
| transport duration | 10.066906 seconds |
| `transport_status` | `EXECUTION_ACCEPTED` |
| return code | 0; the canonical adapter emits `EXECUTION_ACCEPTED` only for return code zero |
| timed out | false; timeout produces a distinct timeout status/124, while receipt diagnostics contain no exception |
| stdout bytes / characters | 185 / 185 |
| stdout SHA-256 | `446108657440950bc73ed3e60af824af698d79b9020055c3e422dd3014ba8df7` |
| stdout truncated | false |
| stderr bytes / characters | 3,196 / 3,196 |
| stderr SHA-256 | `be67dec412a727f2b21c6230b243ffa66c12175b1999ccef228b988907ddd6a4` |
| stderr substituted for stdout | false |
| capture status/count | `WORKER_RESULT_CAPTURED` / 1 |
| validation status/count | `RESULT_VALIDATED` / 1 |
| validation meaning | `GOVERNANCE_POLICY_AND_LINEAGE_VALIDATION_ONLY` |
| Provider / retry / fallback / additional Worker | false / false / false / false |

Exact authentic stdout:

```diff
--- a/aigol/runtime/human_interface.py
+++ b/aigol/runtime/human_interface.py
@@ -1,2 +1,2 @@
 def render_summary(value):
-    return f"Status: {value}"
+    return f"Summary: {value}"
```

The same 185 UTF-8 bytes and SHA-256 are bound in the transport receipt,
G31-18 Worker-output payload, G31-20 validation identity, and G31-22A review
packet. They were never reconstructed from a hash and were never replaced by
stderr. G31-22A stores them as part of its canonical review packet; no new raw-
output artifact family was introduced.

## Replay reconstruction

All four requested primary families reconstructed successfully after the live
call. The G31-22A review had also been reconstructed in the continuous call
before AiCLI requested the fourth decision.

| Family | Identity | Count | Replay hash |
|---|---|---:|---|
| activation | receipt `CODEX-EXECUTION-RECEIPT-28829814f8f84947ce090c16`; response identity `d10c15269a2f67455cd40fcf7791762e8f2fbd49a16e51e717363a5d9b5ca22d` | 3 | `sha256:0ed2d342a5a04c41581615b24c8e497435a2a2e19609bfed7c44f272293e0e84` |
| capture | receipt lineage ending `:RESULT-CAPTURE`; artifact `sha256:14205b10b0ffa54c66d67a3bb050b984433d1ebebc4ac03014d05acf0b1fd1e7` | 4 | `sha256:07e231e6a838ac83cc4c81442aa641884b804f841ba98f404def8500acc243bd` |
| validation | capture lineage ending `:SEMANTIC-VALIDATION:446108657440950bc73ed3e6`; artifact `sha256:1b86e899cbae6d44b7bd10fe878d80b0a8554a3aa5cf6b2eff87e4a89096c60c` | 4 | `sha256:b5f895348147edcf8a36049dfaede80d215ec473db2ffe71ac7c3aac39b4cc45` |
| task-outcome review | `G31-TASK-OUTCOME-REVIEW-d773600d5277e13809f33f3f`; identity `sha256:63d2025cd5823fa9c52d36f18489391cbc3ea39ed773600d5277e13809f33f3f` | 2 | `sha256:f94017a63a97bde4f785be707a6ead9b515825b9ca57dbaff539aaadf77c7f57` |

The separate reused human-decision Replay reconstructed with decision ID
`G31-TASK-OUTCOME-REVIEW-d773600d5277e13809f33f3f:HUMAN-TASK-OUTCOME-DECISION`,
2 artifacts, and Replay hash
`sha256:631e51b81c49233df4a24bcc4742fc8ddd97902f0f138e52d629808d6ee6c0c9`.

Capture also bound Worker-output hash
`sha256:b69c7d210442e6b7596088e761fe7fde462f41ee9ae70b0e8d45b88d6ddcc7bb`
and payload hash
`sha256:8a7d656d989f22146830067d52ba783e3cf1aecb3cb59bf27c5549cbe05d735c`.

## Human review outcome

AiCLI displayed the complete review packet and paused. The human then selected
`TASK_OUTCOME_UNSATISFIED`; production code did not predetermine the outcome.
The canonical generic decision is `REJECT` under the narrow scope
`REVIEW_CAPTURED_WORKER_TASK_OUTCOME_ONLY`.

| Pre-execution/live criterion | Observation |
|---|---|
| stdout references implementation target | true |
| stdout references focused-test target | false |
| both grounded filenames referenced | false |
| unified-diff markers present | true |
| `Status:` -> `Summary:` present | true |
| ungrounded target present | false |
| patch applied | false |
| tests run against applied patch | false |

The missing focused-test filename made the complete stated live criterion set
unsatisfied. The output was not rewritten, repaired, or rerun.

Final review truth:

| Field | Value |
|---|---:|
| `task_outcome_satisfaction_evaluated` | true |
| `task_outcome_satisfied` | false |
| `task_outcome_review_status` | `TASK_OUTCOME_UNSATISFIED` |
| `human_task_outcome_decision_recorded` | true |
| `task_outcome_review_replay_created` | true |
| `task_outcome_review_count` | 1 |
| `rework_requested` | false |
| `result_accepted` | false |
| `repository_mutation_authorized` | false |
| `repository_mutated` | false |
| `automatic_retry_performed` | false |
| `additional_worker_process_started` | false |
| `commit_created` / `deployed` / `released` | false / false / false |

The human-decision Replay explicitly records
`implementation_authorization_allowed=false`,
`implementation_authorized=false`, `execution_requested=false`,
`dispatch_requested=false`, and `worker_invoked=false`.

## Hash isolation and process proof

| Path | Before SHA-256 | After SHA-256 |
|---|---|---|
| disposable `aigol/runtime/human_interface.py` | `7f3c53747a6ad36e5b1e0f69a55ba3cd4425aea022e822554fbb0ce700e7467b` | same |
| disposable `tests/test_human_interface.py` | `6cb9728c57aa10f995cb6dcb1508c0e8ddb5897a94b4f7895872db47c7a743d4` | same |
| protected `diagnostic_evidence.json` | `a626a69a8020bc730876119c52701a94de9ab6e4772cc64c1f5d017296650203` | same |
| protected `governed_return.json` | `e82f47c0c13678725993b21e2af2e0437edccaed324f861a7b58e77d7f8e787d` | same |
| protected `lineage.json` | `07b95505521e70f51cdddecc1057fd3a208b198445693c9a8da1e996df5799dd` | same |
| protected `provider_stderr.txt` | `d47a06d59aba2814c3fb7460049fc2ccbfc834196c956d6c6558e8be8b079e24` | same |
| protected `provider_stdout.txt` | `a73a499e2e9133c03d7babfd5c4dec7967f31e2bfb354ea9dd41df0a15c08cb3` | same |
| protected `governed_returns.jsonl` | `dbc7b63f2a17c50c43bbb4fde4f44c1dbae8d25d550fb6b4d4daa14e17126161` | same |
| protected `WORKER_INVOCATION_ARTIFACT_V1` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | same |
| protected `WORKER_INVOKED` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | same |
| protected `invocation` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | same |

The activation repository snapshot was identical before and after:
`sha256:2c21d94e091853ad5c2e4a9ab8301b36550c164ffbe187a45eaac57e75031372`.
Final process inspection found no remaining `codex exec` process. The one live
AiCLI process exited normally immediately after the fourth decision.

## Validation

| Validation | Result |
|---|---|
| focused G31-22B continuation paths | `4 passed in 51.36s` |
| invalid-validation gate plus G31-22B | `5 passed in 55.64s` |
| human-decision and G31-17B through G31-22B aggregate | `103 passed in 351.73s` |
| complete parent suite | `6489 passed, 4 skipped in 611.68s` |
| governance conformance tests | `5 passed in 0.03s` |
| governance engine | `PARTIALLY_CONFORMANT`; 18 passed, 2 known hook mismatches, 0 critical violations; deterministic/read-only/fail-closed; report hash `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea` |
| targeted `py_compile` | passed |
| parent and nested `git diff --check` | passed |

The known root and nested pre-commit-hook mismatches remain visible and were not
introduced or concealed by this phase.

## Git status and report-only commit command

No file is staged and no commit was created. Parent HEAD remains
`1c2102681fe224d4fd44594b32e1747866b51fbf`. Nested HEAD remains
`3183bab71f8f30397c0309dd2e6d846d14a11f66`, and the nested worktree is clean.

Parent status contains the nine protected paths, the pre-existing unstaged
G31-22A human-decision dependency, and the intended G31-22B AiCLI/test/report
changes. Exact future commands excluding every protected path:

```bash
git add \
  aigol/runtime/human_decision_runtime.py \
  aigol/cli/aicli.py \
  tests/test_g31_22b_live_task_outcome_review_continuation.py \
  docs/governance/G31_22B_LIVE_EXACT_BYTE_TASK_OUTCOME_HUMAN_REVIEW_CONFIRMATION.md
git commit -m "feat(governance): bind live Codex output to human task review"
```

These commands are report-only and were not executed.

## Progress and next state

Evidence-scoped whole-project progress is revised from **92.5% to 93.0%**. The
complete exact-byte path through an explicit fourth human decision is live and
operational. This particular task outcome is truthfully unsatisfied; it does
not prove final acceptance, generated-content/test validation, or mutation.

The live result exposes a contract-alignment question: a minimal unified diff
for a source-only fix naturally names only the changed source, while the stated
review criterion required stdout to name the unchanged focused test too. The
Worker was instructed to inspect the test, but a diff-only stdout contract has
no canonical channel for proving that read without changing the test or adding
non-diff prose.

Recommended next state:

`G31_TASK_OUTCOME_CRITERIA_AND_UNIFIED_DIFF_OUTPUT_CONTRACT_ALIGNMENT_AUDIT_REQUIRED`
