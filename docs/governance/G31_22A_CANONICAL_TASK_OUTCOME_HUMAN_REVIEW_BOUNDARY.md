# G31-22A Canonical Task-Outcome Human-Review Boundary

Date: 2026-07-18
Verdict: `G31_TASK_OUTCOME_REVIEW_IMPLEMENTED_LIVE_BYTES_UNAVAILABLE`

## Scope and baseline gate

This phase implements one review-only boundary for a human to classify whether
one exact, governance-valid captured CODEX result satisfies its pre-authorized
task. It does not accept the result, authorize or perform repository mutation,
apply a patch, execute rework, start CODEX, invoke a Provider, retry, commit,
deploy, or release.

The continuation gate passed before implementation resumed:

| Baseline check | Required | Observed |
|---|---|---|
| working directory | `/home/pisarna/work/sapianta` | exact match |
| parent top level | `/home/pisarna/work/sapianta` | exact match |
| parent HEAD | prefix `636458da` | `636458da2de71d7fd3d0c149d437d9ceb108f337` |
| parent subject | committed G31-21B parent repair | `fix(governance): bind exact grounded task to Codex Worker` |
| nested HEAD | prefix `3183bab` | `3183bab71f8f30397c0309dd2e6d846d14a11f66` |
| nested subject | committed G31-21B canonical repair | `fix(governance): preserve Codex Worker prompt fidelity` |
| nested worktree | clean | clean |
| parent pre-existing status | exactly nine protected paths | exact match |

Neither prerequisite commit was created, amended, reverted, or staged by this
phase.

## Canonical ownership finding

The G31-21A audit remains authoritative:

- Worker Result Validation owns policy and lineage validation only;
- Post-Execution Replay Review owns execution-chain integrity only;
- Result Evaluation consumes the incompatible legacy `RESULT_ARTIFACT_V1`
  family and does not record task satisfaction;
- Generated-Content Acceptance requires implementation-manifest, content-
  validation, and test-validation evidence and cannot accept raw G31 stdout;
- repository mutation requires a later, separate authorization.

No existing owner could truthfully represent G31 task-outcome satisfaction.
This phase therefore introduces the minimum new packet owner in
`aigol/runtime/codex_task_outcome_human_review_runtime.py`, while reusing the
existing generic human-decision owner in
`aigol/runtime/human_decision_runtime.py`. It does not add a second approval
system, semantic validator, execution owner, acceptance owner, mutation owner,
or generic Replay subsystem.

The new owner emits only:

- `TASK_OUTCOME_REVIEW_PACKET_ARTIFACT_V1`;
- `TASK_OUTCOME_REVIEW_REQUIRED_ARTIFACT_V1`;
- a task-outcome-specific approval-request envelope consumed by the existing
  append-only human-decision Replay.

The exact decision scope is:

`REVIEW_CAPTURED_WORKER_TASK_OUTCOME_ONLY`

The supported task-outcome decisions are:

- `TASK_OUTCOME_SATISFIED` -> existing human decision `APPROVE`;
- `TASK_OUTCOME_UNSATISFIED` -> existing human decision `REJECT`;
- `REWORK_REQUESTED` -> existing human decision `REQUEST_MODIFICATION`.

Those mappings reuse the mechanism, not its unrelated implementation authority.
The approval request sets `implementation_authorization_allowed=false`, so all
three decisions leave implementation authorization, result acceptance,
repository mutation, retry, and Worker execution false. Existing callers omit
that optional field and retain their previous identities and behavior.

## Exact lineage and boundary

The bounded path is:

```text
pre-existing contextual request and Repository Cognition grounding
  -> governed authorization and two pre-execution human decisions
  -> execution-ready Replay and G31 candidate
  -> governed-execution Replay
  -> third human activation decision
  -> CODEX activation receipt and Replay
  -> exact in-memory stdout
  -> G31-18 capture artifact and Replay
  -> G31-20 governance-validation artifact and Replay
  -> G31-22A task-outcome review packet
  -> existing human-decision Replay
  -> satisfied, unsatisfied, or rework-requested truth only
```

`prepare_codex_task_outcome_review` reconstructs the activation, capture, and
validation bindings before producing a packet. The packet binds:

- the original contextual request and grounded project objective;
- canonical implementation/test capability and exact target paths;
- required output type and exact authorized Worker task;
- exact final approved Worker prompt and hash;
- activation request, receipt, Replay reference, and Replay hash;
- exact UTF-8 Worker-output text, byte length, SHA-256, output identity, and
  output artifact hash;
- capture artifact, identity, Replay reference, Replay hash, and count;
- validation artifact, canonical status/meaning, Replay reference, Replay
  hash, and count;
- immutable pre-execution criteria and their hash;
- deterministic diff observations and missing acceptance evidence.

The activation owner now derives the task-outcome criteria while constructing
the grounded Worker execution contract, before the third human activation
decision and before Worker execution. The criteria bind the exact task and its
hash, requested output type, grounded targets, exact-output human review,
target confinement, unapplied-patch state, and the separation of satisfaction,
acceptance, and mutation. Their hash is preserved by activation review,
approval, execution request, and reconstruction.

## Canonical meaning and authority separation

`RESULT_VALIDATED` continues to mean exactly:

`GOVERNANCE_POLICY_AND_LINEAGE_VALIDATION_ONLY`

It does not mean that the task outcome is satisfied, that the result is
accepted, that the patch is safe, or that mutation is authorized.

| Human outcome | satisfaction evaluated | satisfied | rework requested | result accepted | mutation authorized | retry / additional Worker |
|---|---:|---:|---:|---:|---:|---:|
| `TASK_OUTCOME_SATISFIED` | true | true | false | false | false | false |
| `TASK_OUTCOME_UNSATISFIED` | true | false | false | false | false | false |
| `REWORK_REQUESTED` | true | false | true | false | false | false |

All three outcomes additionally preserve:

- `human_task_outcome_decision_recorded=true`;
- `governance_result_validated=true`;
- `repository_mutated=false`;
- `automatic_retry_performed=false`;
- `additional_worker_process_started=false`;
- `provider_invoked=false`;
- `commit_created=false`, `deployed=false`, and `released=false`.

A satisfied decision is human evidence about task outcome only. Canonical final
acceptance still requires its own admissible content/test evidence. Acceptance
does not itself imply filesystem authority, and this phase grants neither.
A rework request records a disposition but cannot launch CODEX; a future
execution requires a separate governed transition and new authority.

AiCLI remains presentation-only. The renderer can show the original task,
grounded targets, exact output, validation meaning, task criteria, missing
application/test evidence, and available decisions, while preserving:

- `aicli_reviews=false`;
- `aicli_accepts=false`;
- `aicli_authorizes_mutation=false`;
- `aicli_executes_rework=false`.

## Fail-closed coverage

| Boundary | Enforced result |
|---|---|
| exact output missing | review creation fails before a human request exists |
| output bytes/hash changed | output, transport, capture, and validation continuity fails |
| post-execution criteria changed | activation/contract/criteria reconstruction fails |
| grounded target changed | candidate and activation lineage reconstruction fails |
| capture or validation Replay substituted | canonical reconstructors or exact packet comparison fail |
| governance-invalid validation | review cannot be prepared, including as satisfied |
| cross-session destination/reference | path confinement fails closed |
| duplicate destination | immutable two-step review Replay rejects overwrite |
| duplicate review lineage | session-wide review identity reuse is rejected |
| repeated human decision | approval-required hash reuse is rejected |
| acceptance inferred from satisfaction | exact decision reconstruction rejects changed truth |
| mutation inferred from satisfaction | exact decision reconstruction rejects changed truth |
| rejection/rework triggers retry | no execution callback exists; stop flags remain false |

The review Replay contains two ordered immutable wrappers. The reused human-
decision Replay contains its existing two ordered wrappers. Both families are
reconstructed and hash-verified; task-outcome interpretation is then compared
against a fully regenerated expected capture.

## Retained live evidence and deterministic result

The retained G31-21B Replay does not contain the exact authentic Worker-output
bytes. It retains the 185-byte length and SHA-256, but those values are not the
bytes and cannot be reversed into them. The historic live result was therefore
not reviewed, and live task-outcome satisfaction remains unproven. No report
summary, hash, or remembered diff was substituted for the missing bytes, and
no new CODEX process was started.

Implementation evidence uses an exact deterministic UTF-8 fixture under
pytest-owned disposable runtime roots:

| Fixture property | Result |
|---|---|
| output type | unified diff |
| byte length | 185 |
| SHA-256 | `446108657440950bc73ed3e60af824af698d79b9020055c3e422dd3014ba8df7` |
| implementation target | `aigol/runtime/human_interface.py` |
| focused-test target | `tests/test_human_interface.py` |
| diff markers | present |
| proposed change | `Status:` -> `Summary:` |
| additional target | absent |
| patch applied | false |
| tests against applied patch | false |

The deterministic satisfied case reconstructs with
`task_outcome_satisfied=true` while acceptance and mutation remain false. The
unsatisfied and rework cases reconstruct with satisfaction false; the latter
sets only `rework_requested=true`. The recording runner proves no second call
is made by either disposition. These results prove implementation behavior,
not the unavailable historic live review.

## Changed surface and size

Production:

- `aigol/runtime/codex_worker_activation_binding_runtime.py`: establishes and
  binds immutable pre-execution task-outcome criteria;
- `aigol/runtime/human_decision_runtime.py`: admits an optional, fail-closed
  `implementation_authorization_allowed` boundary while preserving existing
  artifact behavior when the field is absent;
- `aigol/runtime/codex_task_outcome_human_review_runtime.py`: new thin G31
  packet/reconstruction/decision binding and non-authoritative renderer.

Tests:

- `tests/test_g31_22a_canonical_task_outcome_human_review_boundary.py` uses
  exact deterministic bytes and explicit disposable roots for all positive and
  negative cases.

Production diff size is 911 added and 3 removed lines across three production
files, net +908. The new owner is 848 physical lines; the focused test is 378
physical lines. The implementation size is driven by full upstream Replay
reconstruction, exact artifact regeneration, explicit authority truth, and
fail-closed substitution checks. No nested production file changed.

## Validation evidence

| Validation | Result |
|---|---|
| Initial existing human-decision, G31-21B, and synthesis compatibility | `24 passed in 23.01s` |
| New focused G31-22A suite | `12 passed in 89.08s` |
| Expanded human-decision/approval and G31-17B through G31-22A regression set | `128 passed in 277.87s` |
| Complete parent suite | `6485 passed, 4 skipped in 547.21s` |
| Governance conformance tests | `5 passed in 0.03s` |
| Governance engine | `PARTIALLY_CONFORMANT`; 18 passed, 2 known hook drifts, 0 critical violations; deterministic/read-only/fail-closed; report hash `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea` |
| Targeted `py_compile` | passed |
| Parent and nested `git diff --check` | passed |

The two known conformance gaps remain visible and unchanged: the root expected
and installed pre-commit hooks are missing, and the nested installed hook lacks
`promotion_gate_v02` and `check_layer_freeze`. This phase does not hide or
reframe partial conformance as full conformance.

## Protected-state comparison

| Protected path | Before SHA-256 | After SHA-256 |
|---|---|---|
| `.runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/diagnostic_evidence.json` | `a626a69a8020bc730876119c52701a94de9ab6e4772cc64c1f5d017296650203` | `a626a69a8020bc730876119c52701a94de9ab6e4772cc64c1f5d017296650203` |
| `.runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/governed_return.json` | `e82f47c0c13678725993b21e2af2e0437edccaed324f861a7b58e77d7f8e787d` | `e82f47c0c13678725993b21e2af2e0437edccaed324f861a7b58e77d7f8e787d` |
| `.runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/lineage.json` | `07b95505521e70f51cdddecc1057fd3a208b198445693c9a8da1e996df5799dd` | `07b95505521e70f51cdddecc1057fd3a208b198445693c9a8da1e996df5799dd` |
| `.runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stderr.txt` | `d47a06d59aba2814c3fb7460049fc2ccbfc834196c956d6c6558e8be8b079e24` | `d47a06d59aba2814c3fb7460049fc2ccbfc834196c956d6c6558e8be8b079e24` |
| `.runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stdout.txt` | `a73a499e2e9133c03d7babfd5c4dec7967f31e2bfb354ea9dd41df0a15c08cb3` | `a73a499e2e9133c03d7babfd5c4dec7967f31e2bfb354ea9dd41df0a15c08cb3` |
| `.runtime/aigol/ledger/governed_returns.jsonl` | `dbc7b63f2a17c50c43bbb4fde4f44c1dbae8d25d550fb6b4d4daa14e17126161` | `dbc7b63f2a17c50c43bbb4fde4f44c1dbae8d25d550fb6b4d4daa14e17126161` |
| `WORKER_INVOCATION_ARTIFACT_V1` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `WORKER_INVOKED` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `invocation` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

Final hashes were independently recomputed after implementation, validation,
and report creation. No protected path was modified, reverted, deleted, or
staged by this phase.

## Git status and commit command

No commit was created and nothing is staged. Parent HEAD remains
`636458da2de71d7fd3d0c149d437d9ceb108f337`. Parent status contains exactly the
nine protected paths plus the intended two modified production files, one new
production owner, one new focused test, and this report. Nested HEAD remains
`3183bab71f8f30397c0309dd2e6d846d14a11f66`; its worktree is clean.

Exact report-only future commands, excluding every protected path:

```bash
git add \
  aigol/runtime/codex_worker_activation_binding_runtime.py \
  aigol/runtime/human_decision_runtime.py \
  aigol/runtime/codex_task_outcome_human_review_runtime.py \
  tests/test_g31_22a_canonical_task_outcome_human_review_boundary.py \
  docs/governance/G31_22A_CANONICAL_TASK_OUTCOME_HUMAN_REVIEW_BOUNDARY.md
git commit -m "feat(governance): add canonical task-outcome human review"
```

These commands are reported only and were not executed.

## Progress, limitations, and next state

Evidence-scoped whole-project progress is revised from **92.0% to 92.5%**. The
canonical task-outcome review and human-decision boundary is implemented and
fully exercised with deterministic exact-byte evidence. The historic G31-21B
live outcome is not reviewed because its exact bytes were intentionally not
retained. Final acceptance, generated-content/test validation, and repository
mutation authority remain separate future boundaries.

Explicit non-goals remain:

- do not infer task satisfaction from governance validation;
- do not review historic output from hashes, summaries, or remembered text;
- do not infer final acceptance or mutation from task satisfaction;
- do not apply, repair, rewrite, stage, commit, deploy, or release a Worker
  result;
- do not execute automatic rework, retry, fallback, Provider substitution, or
  another Worker;
- do not make AiCLI authoritative;
- do not introduce a parallel approval, acceptance, execution, or Replay
  system.

Recommended next state:

`G31_LIVE_EXACT_BYTE_TASK_OUTCOME_HUMAN_REVIEW_CONFIRMATION_REQUIRED`
