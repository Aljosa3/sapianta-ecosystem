# G31-21A Worker Output Task-Outcome Satisfaction Audit

## Verdict

`G31_WORKER_PROMPT_FIDELITY_DEFECT_IDENTIFIED`

The historic G31-20F live cause is classified exactly as:

`WORKER_PROMPT_FIDELITY_LOSS`

The exact command-bound prompt made downstream task preparation the primary
goal and retained the original request only as nested context. The authentic
CODEX stdout then returned the requested downstream task description. The
adapter captured the complete, untruncated stdout as the final Worker answer;
it did not select an intermediate message, parse structured events, or replace
stdout with stderr. Worker noncompliance is therefore not proven.

No existing canonical runtime is already compatible with G31 task-outcome
satisfaction. The post-execution review owner verifies chain integrity only;
the Result Evaluation owner consumes a different result family and records
observations without satisfaction or disposition; generated-content acceptance
requires an implementation manifest plus content and test validations. No
binding was implemented and no new reviewer, validator, acceptance system,
artifact family, CODEX process, retry, result acceptance, or mutation occurred.

## Baseline and audit boundary

- Parent HEAD: `2d2bb10833a75f5dc5311c5534690d23e116d628`
- Parent subject: `fix(governance): enforce exact repository cognition pairing`
- Nested `sapianta_system` HEAD:
  `31522024b38bc08a60ea2152122bc2b399e1235e`
- Nested worktree: clean before the audit
- Live evidence root inspected read-only:
  `/tmp/g31-20f-live-bRY3ZP/runtime/G31-20F-LIVE`
- Live disposable workspace inspected read-only:
  `/tmp/g31-20f-live-bRY3ZP/workspace`
- New CODEX processes: `0`
- Production changes: `0` lines
- Test changes: `0` lines
- Documentation changes: this report only

The prompt is durably present in the activation receipt. Exact stdout bytes
were observed directly during the continuous G31-20F activation/capture/
validation call and were not inferred from a hash. In accordance with the
G31-20 in-memory-only contract, raw stdout was not durably retained; the
durable Replay retains its byte length, character length, truncation state,
hash, and semantic bindings. This audit quotes only directly observed content
and does not reconstruct missing text from hashes.

## Exact live lineage

| Stage | Exact or canonical value | Evidence/owner |
|---|---|---|
| Original request | `Improve the human interface summary by proposing a change to aigol/runtime/human_interface.py for tests/test_human_interface.py. Return a unified diff only; do not edit files.` | Operational-turn, durable-work, grounding, and activation review Replay |
| Route | `GOVERNED_DEVELOPMENT_RUNTIME` | Operational-turn binding |
| Project objective | `Resolve the human interface summary by proposing a change to aigol/runtime/human_interface as IMPLEMENTATION.` | Approved durable-work implementation scope |
| Canonical capability | `human_interface` | Repository Cognition / repository-scope grounding |
| Implementation target | `aigol/runtime/human_interface.py`; symbol `render_summary`; content hash `sha256:8b2c7f9f90f055d8c327229e73e75ca12ad4b3befafd68ab529cbaf031dc5957` | Grounding target evidence |
| Focused-test target | `tests/test_human_interface.py`; symbol `test_render_summary`; content hash `sha256:0b933e9887972a00dbc683266a76998a8e39faea3b172793f73df78b401ed946` | Grounding target evidence |
| Grounding artifact | Exactly one implementation/test pair; `sha256:004d6d6ec768c72446e8e3ab889ba84bda2a3ed0a474c1f78013c1bd6cf24422` | `approved_durable_work_repository_scope_grounding` |
| Worker identity | `CODEX`; `GOAL_FAITHFUL_IMPLEMENTATION_WORKER` | Selection, assignment, dispatch, invocation, and candidate Replay |
| Candidate objective | `Create a governed external worker task package ... assigned to CODEX.` | `WORKER_EXECUTION_CANDIDATE_ARTIFACT_V1` |
| Candidate scope | Allowed outputs are the exact source/test paths; Provider and repository mutation prohibited | Candidate Replay |
| Preflight request | `runtime validation: ` plus the exact original request; 195 characters | `preflight_codex_worker_synthesis`, `aigol/runtime/codex_worker_activation_binding_runtime.py:106` |
| Final command | `codex exec <canonical bounded prompt>`; `shell=false`; timeout `60` | Activation receipt |
| Transport | `EXECUTION_ACCEPTED`; return code `0`; timeout false; one process | Activation receipt and adapter contract |
| Authentic stdout | 1,972 bytes; 1,970 characters; untruncated; SHA-256 `2158195ca659923ba019414df89792025f24088cabc34796e3c09ca2df62d5f4` | Live in-memory dispatch plus activation receipt |
| Capture | One capture; Worker-output hash `sha256:a8691b2f7cabdca63e6e6baf76b3f3bbe62c029e0572add7dce9f250a059960d` | G31-18 Replay |
| Validation | One `RESULT_VALIDATED`; meaning `GOVERNANCE_POLICY_AND_LINEAGE_VALIDATION_ONLY` | G31-20 Replay |
| Outcome/acceptance | satisfaction not evaluated; satisfied false; accepted false | Canonical validation and G31 stop flags |

The upstream lineage preserved the original goal and exact grounded pair, but
neither the candidate objective nor the final synthesis promoted them to the
primary executable goal. Candidate `allowed_outputs` are scope constraints,
not instructions to inspect the two files or return a patch.

## Prompt-fidelity analysis

The final prompt is owned by
`sapianta_system/runtime/codex_synthesis/governed_codex_prompt_synthesizer.py`.
`synthesize_governed_codex_task` selects that owner at
`governed_codex_task_response.py:44-68`. For the synthetic prefix
`runtime validation:`, the classifier selects `VALIDATION_TASK`; the owner then
sets:

```text
GOAL:
Prepare a bounded runtime validation task.

CURRENT CONTEXT:
...
Original governed request: runtime validation: Improve ... Return a unified diff only; do not edit files.

ALLOWED SCOPE:
Preview-only downstream Codex task formation within explicitly governed bounds.
...
ACCEPTANCE CRITERIA:
Task remains bounded, non-executing at synthesis time, and explicitly approved before any handoff.

FINAL RESPONSE REQUIREMENTS:
Return the files touched, validation performed, limitations, and confirmation that prohibited capabilities were not introduced.
```

The defect is at
`governed_codex_prompt_synthesizer.py:5-43`:

- the task-class goal replaces the authorized engineering outcome;
- the original request is labelled context rather than the task to perform;
- preview-only task formation conflicts with inspecting the repository and
  producing the requested patch;
- non-execution at synthesis time is incorrectly carried into the later,
  separately approved live Worker prompt;
- final-response requirements conflict with `unified diff only`;
- exact grounding evidence, implementation/test roles, and the requested
  output contract are not promoted into authoritative prompt sections.

| Required outcome | Original/grounded evidence | Final prompt result |
|---|---|---|
| Inspect implementation file | Exact grounded source exists and inspection is necessary to propose a change | Not instructed; preview-only formation is primary |
| Inspect focused test | Exact grounded test exists and inspection is necessary to make the change test-aware | Not instructed; target appears only inside nested request text |
| Propose a minimal unified diff | Exact request says `Return a unified diff only` | Present only as nested context and contradicted by outer goal/final-response contract |
| Do not apply the patch | Exact request says `do not edit files`; activation also rejects repository drift | Faithfully retained and reinforced |

The prompt therefore preserved the request bytes but lost their authority and
operational fidelity. Byte preservation alone is not task fidelity.

## Authentic stdout and extraction analysis

The directly observed final stdout began:

> Prepared a bounded downstream task for review; no handoff or execution occurred.

It then supplied a fenced downstream task containing the exact two allowed
files and an `OUTPUT CONTRACT` asking a future Worker to return only a unified
diff. After the fence it reported:

- files touched: none;
- validation: the synthesized task was checked for boundedness;
- limitation: repository baseline and file contents were not accessed;
- limitation: a proposed change was not generated or tested;
- no handoff occurred and approval remained required.

This was the final Worker answer, not an intermediate transport event. It
matches the outer bounded prompt closely and fails the nested engineering
request. It is therefore evidence of prompt-fidelity loss, not CODEX Worker
noncompliance.

The extraction owner is
`sapianta_system/runtime/codex_execution_adapter/governed_codex_execution_dispatch.py`:

1. `dispatch_bounded_codex` calls the runner with `capture_output=true`,
   `text=true`, and `shell=false` (`:47-66`).
2. `_diagnostics` passes `completed.stdout` and `completed.stderr` through
   independent `_capture` calls (`:24-44`).
3. `_capture` returns the complete text when it is at most 4,096 characters
   (`:10-21`). The live stdout was 1,970 characters and `stdout_truncated=false`.
4. The dispatch response assigns that value directly to `stdout` (`:67-80`).
5. `execute_governed_codex` returns the dispatch unchanged and hashes its
   stdout in the receipt (`governed_codex_execution_response.py:28-68` and
   `governed_codex_execution_receipt.py`).
6. G31-18 consumes the in-memory dispatch stdout and G31-20 proves the same
   byte length/hash. Stderr was separate, 4,187 bytes, and never substituted.

The command used ordinary `codex exec`, not structured JSON output. The
adapter has no event list, message selector, assistant-message parser, or
fallback to stderr. No extraction fix is indicated.

## Canonical ownership audit

| Concern | Existing owner | Contract finding | G31 compatibility |
|---|---|---|---|
| Governance/policy/lineage validation | `worker_result_validation_runtime.validate_worker_result` | Explicitly excludes approval and binds both task-outcome flags false (`:151-160`, `:600-658`, `:802-815`) | Compatible and already used; must not own satisfaction |
| Post-execution Worker result review | `post_execution_replay_review_runtime.review_validated_worker_result` | Reconstructs validation/output lineage and classifies `EXECUTION_CHAIN_INTEGRITY_VERIFIED`; `reviewed_by` is attribution, not an accept/reject decision (`:144-228`, `:696-739`) | Artifact input is close, but semantics contain no original criteria, output bytes, satisfaction, disposition, or human decision |
| Result evaluation | `result_evaluation_runtime.evaluate_result` | Canonical evaluation owner for observations; explicitly has no approval authority | Requires legacy `RESULT_ARTIFACT_V1`, not G31 `WORKER_RESULT_CAPTURE/VALIDATION`; no satisfaction boolean or disposition |
| External result-package acceptance | `external_worker_adapter_runtime.accept_external_worker_result_package` | Validates package identity, hashes, Worker interface, and completion; `accepted_by` records package ingestion | Structural acceptance before result validation, not human task acceptance |
| Human generated-content acceptance | `generated_content_acceptance_runtime.accept_generated_content` | Explicit human `ACCEPTED`, content-only, read-only, no mutation authority | Requires `IMPLEMENTATION_MANIFEST_ARTIFACT_V1`, generated-content validation, and generated-test validation; cannot accept raw G31 stdout and cannot represent rejection/rework |
| Rework/improvement | Result Evaluation -> Improvement Proposal -> Improvement Review/Approval runtimes | Governed improvement lifecycle exists only after its own canonical result/evaluation lineage | G31 validation is not an admissible input; no automatic retry is authorized |
| Termination | `governed_termination_runtime` | Closes reviewed execution evidence | No satisfaction, acceptance, rejection, rework, or retry authority |
| Repository mutation | generated-content acceptance plus separate filesystem-mutation authorization/runtime | Mutation requires its own exact manifest/content/test/authorization lineage | Correctly separate and unavailable for this live result |

Canonical finding: task-outcome satisfaction is a human-review responsibility,
potentially aided by deterministic format checks, but the repository has no
already-compatible canonical contract that binds the G31 original request,
grounding pair, exact stdout, capture Replay, and validation Replay to an
explicit satisfied/unsatisfied decision. Human acceptance is a later and
separate disposition. AiCLI is presentation only and cannot fill either gap.

## Authority and human-decision matrix

| State | Current G31-20F truth | Required owner/decision |
|---|---|---|
| `governance_validated` | true | Existing deterministic Worker Result Validation; no human decision |
| `task_outcome_satisfaction_evaluated` | false | New explicit, lineage-bound human review is required |
| `task_outcome_satisfied` | false/unevaluated | The same review must explicitly choose satisfied or unsatisfied; never infer from `RESULT_VALIDATED` |
| `result_accepted` | false | Separate explicit acceptance disposition is required after satisfaction; rejection must also be explicit |
| `result_rejected` | not represented | A compatible disposition contract is missing; do not encode rejection as validation failure |
| `rework_requested` | false/not represented | Explicit human rework request is required; it must create no retry itself |
| `repository_mutation_authorized` | false | Separate existing mutation authorization after canonical generated-content lineage; never implied by acceptance |

At least a fourth human decision is required for task-outcome review. Result
acceptance/rejection is a separately scoped human disposition and must not be
inferred from that review; a future contract may collect both in one human
interaction only if it records two distinct, independently validated scopes.
Rework is another explicit disposition and must stop before any new activation.

## Fail-closed boundary assessment

| Boundary | Current coverage | Required future task-review behavior |
|---|---|---|
| Governance-valid but task-irrelevant output | Safely remains unaccepted; G31-20 binds outcome flags false | Review must permit only explicit `UNSATISFIED`, never silent acceptance |
| Missing exact output bytes | G31-20 fails before canonical validation; durable Replay intentionally has hashes only | Review must require the authentic in-memory bytes or a separately authorized canonical retention contract |
| Changed request or grounding | Existing G31 reconstruction and grounding hashes fail closed | Criteria must bind the same request, capability, targets, content hashes, workspace, and session |
| Changed criteria | No task-review criteria artifact exists | Criteria must be derived before review from authorized request/grounding/output type and hash-bound; no post-execution invention |
| Output substitution | Existing transport/capture/validation binding fails closed | Review must bind stdout byte length/SHA, Worker-output hash, capture hash, and validation hash |
| Replay tampering | Existing reconstructors verify wrapper/artifact hashes and ordering | Review must reconstruct all upstream families before decision |
| Cross-session review | Existing G31 destinations and grounding reject cross-session use | Review destination and every replay reference must remain under one session root |
| Duplicate destination/review | Existing validation/review owners protect append-only destinations; no task-review owner exists | One review per exact request/criteria/output/validation lineage key |
| Duplicate acceptance | Generated-content acceptance has a lineage reuse key, but is incompatible | Future disposition must reject a reused review/result lineage |
| Rejection/rework retry | Current G31 performs no retry/fallback | Rejection or rework records state only; a later activation needs new governed authorization and human approval |
| Acceptance to mutation | Existing generated-content acceptance explicitly grants no filesystem authority | Preserve a separate mutation authorization; acceptance alone must leave mutation false |

## Smallest bounded future candidates

### 1. Prompt-fidelity repair — prerequisite

Repair the existing canonical synthesis owner; do not alter activation
approval identities, command bounds, timeout, process count, Replay families,
or Provider prohibitions.

Exact caller/callee:

```text
aigol.runtime.codex_worker_activation_binding_runtime.preflight_codex_worker_synthesis
  -> sapianta_system.runtime.codex_synthesis.synthesize_governed_codex_task
  -> governed_codex_prompt_synthesizer.synthesize_codex_prompt
```

The callee must make the exact authorized request the primary Worker goal and
bind the grounded implementation/test targets and requested output contract.
Safety constraints remain top-level, including read-only/no-apply. Preview-only
task formation and synthesis-time non-execution must not be sent as the live
Worker's requested outcome. Expected surface: the existing nested synthesizer,
its validator/classifier only if structurally necessary, parent activation
preflight binding, and focused synthesis/activation tests. Evidence-scoped
estimate: 25-45 production lines and 70-110 test lines.

### 2. Task-outcome review ownership — separate architectural decision

No implementation is lawful under the “already compatible” rule. The smallest
future direction is to version/extend the existing canonical Result Evaluation
owner, not create a parallel semantic validator. A separately certified G31
binding would have to admit the existing Worker Result Validation family and
bind, without copying authority:

- original authorized request and its hash;
- pre-execution criteria derived from the request;
- grounding identity, exact capability pair, paths, content hashes, workspace,
  and session;
- exact in-memory stdout bytes plus transport/Worker-output/payload hashes;
- capture and validation identities, hashes, and Replay references;
- one explicit human satisfied/unsatisfied decision;
- stop flags for acceptance, retry, Provider, process, and mutation.

Only after that review may a distinct existing or deliberately versioned human
disposition owner record accept, reject, or request-rework. A unified diff that
is later considered for mutation must first enter the existing manifest,
generated-content validation, generated-test validation, human acceptance, and
filesystem-mutation authorization path; raw stdout must not bypass it.

Expected future surface for a canonical-owner extension and thin G31 binding:
90-150 production lines, 180-260 focused test lines, AiCLI rendering only, and
one governance report. This is an estimate, not authorization to modify L1/L2
contracts.

## Validation results

The following focused/regression group used pytest-owned disposable runtime
roots and performed no real CODEX execution:

```text
tests/test_governed_codex_task_synthesis.py
tests/test_governed_codex_handoff_package.py
tests/test_governed_codex_execution_adapter.py
tests/test_g31_17b_governed_execution_to_codex_worker_activation_binding.py
tests/test_g31_18_codex_transport_to_worker_result_capture_binding.py
tests/test_g31_20_codex_result_to_semantic_validation_binding.py
tests/test_g31_20c_codex_synthesis_preflight.py
tests/test_g31_20d_protected_evidence_isolation_and_validation_semantics.py
tests/test_g31_20e_governed_development_request_routing_reaudit.py
tests/test_g31_20f_disposable_repository_scope_grounding_fixture_contract.py
tests/test_post_execution_replay_review_runtime_v1.py
tests/test_result_evaluation_runtime_v1.py
tests/test_generated_content_acceptance_runtime_v1.py
```

Result: `130 passed in 177.01s`.

This proves current synthesis determinism/bounds, exact command transport,
G31-17B through G31-20F regressions, irrelevant-output non-acceptance,
substitution/duplicate/cross-session failures, post-execution integrity review,
Result Evaluation regressions, and generated-content acceptance isolation.
It does not prove satisfied/unsatisfied G31 task review, rejection, or rework:
those contracts are the audited canonical gap. No full suite was required
because production code did not change.

| Validation | Result |
|---|---|
| Targeted `py_compile` for activation, capture, validation, review, evaluation, acceptance, synthesis, and adapter owners | passed |
| Focused/owner/G31-17B through G31-20F group | `130 passed in 177.01s` |
| Governance conformance tests | `5 passed in 0.03s` |
| Governance engine | `PARTIALLY_CONFORMANT`; 18 passed, 2 known hook drifts, 0 critical violations; report hash `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea` |
| Complete suite | not run; documentation-only audit with zero production/test changes |
| Parent `git diff --check` | passed |
| Nested `git diff --check` | passed |

The two known hook drifts remain visible: the root expected/installed
pre-commit hooks are missing, and the nested installed hook lacks
`promotion_gate_v02` and `check_layer_freeze`. They were not introduced by
this audit and are not reframed as full conformance.

## Protected state

| Protected path | SHA-256 before | SHA-256 after |
|---|---|---|
| `diagnostic_evidence.json` | `a626a69a8020bc730876119c52701a94de9ab6e4772cc64c1f5d017296650203` | `a626a69a8020bc730876119c52701a94de9ab6e4772cc64c1f5d017296650203` |
| `governed_return.json` | `e82f47c0c13678725993b21e2af2e0437edccaed324f861a7b58e77d7f8e787d` | `e82f47c0c13678725993b21e2af2e0437edccaed324f861a7b58e77d7f8e787d` |
| `lineage.json` | `07b95505521e70f51cdddecc1057fd3a208b198445693c9a8da1e996df5799dd` | `07b95505521e70f51cdddecc1057fd3a208b198445693c9a8da1e996df5799dd` |
| `provider_stderr.txt` | `d47a06d59aba2814c3fb7460049fc2ccbfc834196c956d6c6558e8be8b079e24` | `d47a06d59aba2814c3fb7460049fc2ccbfc834196c956d6c6558e8be8b079e24` |
| `provider_stdout.txt` | `a73a499e2e9133c03d7babfd5c4dec7967f31e2bfb354ea9dd41df0a15c08cb3` | `a73a499e2e9133c03d7babfd5c4dec7967f31e2bfb354ea9dd41df0a15c08cb3` |
| `governed_returns.jsonl` | `dbc7b63f2a17c50c43bbb4fde4f44c1dbae8d25d550fb6b4d4daa14e17126161` | `dbc7b63f2a17c50c43bbb4fde4f44c1dbae8d25d550fb6b4d4daa14e17126161` |
| `WORKER_INVOCATION_ARTIFACT_V1` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `WORKER_INVOKED` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `invocation` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

The disposable source hashes also remained equal to the live baseline:
`aigol/runtime/human_interface.py` is
`8b2c7f9f90f055d8c327229e73e75ca12ad4b3befafd68ab529cbaf031dc5957`
and `tests/test_human_interface.py` is
`0b933e9887972a00dbc683266a76998a8e39faea3b172793f73df78b401ed946`.
No `codex exec` process was present at final inspection.

## Git status and report-only commit command

Parent status contains only the six protected modified evidence paths, the
three protected untracked root markers, and this new untracked report. No path
is staged. Parent HEAD and subject are unchanged. Nested HEAD remains
`31522024b38bc08a60ea2152122bc2b399e1235e`, its worktree is clean, and both
diff checks pass.

Exact report-only commands excluding every protected path:

```bash
git add docs/governance/G31_21A_WORKER_OUTPUT_TASK_OUTCOME_SATISFACTION_AUDIT.md
git commit -m "docs(governance): audit G31 Worker task outcome ownership"
```

No commit was created.

## Progress, non-goals, and next state

Evidence-scoped whole-project progress is revised from **92.0% to 91.5%**.
The governed request, unique grounding, three decisions, one real Worker
process, authentic in-memory capture, and policy/lineage validation are
operational. The live confirmation also proves two unresolved completion gaps:
the execution prompt is not goal-faithful, and task-outcome review/acceptance
has no compatible canonical G31 owner.

Explicit non-goals:

- do not reinterpret `RESULT_VALIDATED` as task completion;
- do not blame the Worker for obeying a conflicting outer prompt;
- do not parse fixture-specific CODEX output;
- do not durably retain raw stdout in this phase;
- do not create another Worker/Provider process, retry, or fallback;
- do not accept, reject, repair, rewrite, apply, commit, deploy, or release the
  live result;
- do not make AiCLI authoritative;
- do not introduce a parallel validator, reviewer, acceptance system, Replay
  subsystem, or canonical artifact family.

Recommended next state:

`G31_CODEX_WORKER_PROMPT_FIDELITY_REPAIR_REQUIRED`

Prompt fidelity must be repaired and deterministically tested before another
live Worker attempt. The separate task-outcome owner decision remains required
before any future result may be described as satisfied or accepted.
