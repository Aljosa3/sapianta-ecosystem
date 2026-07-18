# G31-21B CODEX Worker Prompt-Fidelity Repair

Date: 2026-07-18
Verdict: `G31_CODEX_WORKER_PROMPT_FIDELITY_AND_LIVE_TASK_OUTPUT_OPERATIONAL`

## Scope and constitutional boundary

This phase repairs only the proven `WORKER_PROMPT_FIDELITY_LOSS` boundary. It
does not add task-outcome acceptance, repository mutation, retry, Provider
authority, a new review system, or a new Replay family.

`RESULT_VALIDATED` continues to mean
`GOVERNANCE_POLICY_AND_LINEAGE_VALIDATION_ONLY`. The live result was not
accepted and its task outcome was not canonically evaluated.

The parent baseline was
`d411932993c7a0b29ec17a58a08ad75bbed645a6`, with subject
`docs(governance): audit G31 Worker task outcome ownership`. The nested
`sapianta_system` baseline was
`31522024b38bc08a60ea2152122bc2b399e1235e`; its worktree was clean before this
repair.

## Canonical owner and repaired transformation

The existing final prompt owner is
`sapianta_system/runtime/codex_synthesis/governed_codex_prompt_synthesizer.py`:
`synthesize_codex_prompt` and `_synthesize_worker_execution_prompt`. The parent
binding remains the lineage-aware caller in
`aigol/runtime/codex_worker_activation_binding_runtime.py`.

The repaired path is:

1. `preflight_codex_worker_synthesis` performs the unchanged early admission
   check over the exact `runtime validation: <raw request>` string. The 240
   Unicode-code-point maximum remains unchanged; no truncation occurs.
2. `_reconstruct_lineage` revalidates the governed result, execution candidate,
   invocation, authorization, two earlier human decisions, selected CODEX
   Worker identity, and current Repository Cognition grounding.
3. `_grounded_worker_execution_contract` projects the exact original request,
   the one `SOURCE` target, the one `FOCUSED_TEST` target, requested output
   type, CODEX Worker role, and immutable read-only constraints.
4. The same preflight owner synthesizes the final bounded activation prompt
   before the third review. `prepare_codex_worker_activation_review` binds its
   exact hash and contract into the approval identity.
5. `activate_bounded_codex_worker` deterministically reconstructs the same
   contract and prompt. The exact prompt becomes argument three of
   `['codex', 'exec', prompt]`; the parent launch remains `shell=False` with an
   exact 60-second timeout.
6. The prompt hash is carried through the synthesis response, handoff package,
   execution authority token, adapter request and validation, transport
   receipt, activation truth, and Replay reconstruction.
7. G31-18 captures authentic stdout, and G31-20 validates only canonical policy
   and lineage semantics.

The previous higher-precedence phrases were:

- `Prepare a bounded runtime validation task.`
- `Preview-only downstream Codex task formation within explicitly governed bounds.`
- the preview acceptance instruction that the task remain bounded and be
  approved before downstream handoff;
- the old final-response instruction to return files touched, validation,
  limitations, and prohibited-capability confirmation.

Those phrases remain available only for non-executing preview synthesis. They
are prohibited from the grounded Worker-execution prompt. The repaired prompt
precedence is Worker role, exact quoted task data, exact grounded pair,
requested output, and immutable constraints.

The 240-character contract continues to apply to the canonical synthesis input,
which was exactly 188 characters in the live run. The structured final prompt
was 1,740 characters and remained below the existing 2,400-character bounded
prompt validator. The exact structured prompt produced by preflight was the
approved and executed prompt; its SHA-256 was
`e041a406073da887f13dcb9d7fecf5ec99210de77d938e6915f22df6a7d8dfbc`.

## Prompt-fidelity and substitution truth table

| Boundary | Required truth | Result |
|---|---|---|
| Worker role | CODEX selected Worker; not Provider/planner/delegate | passed |
| Primary task | exact authorized request is primary quoted task data | passed |
| Grounding | one implementation and one focused-test target | passed |
| Output | `UNIFIED_DIFF`, stdout only, no plan/governance summary | passed |
| Mutation | `file_mutation_allowed=false`; explicit no-edit instruction | passed |
| Provider/retry/delegation | all remain false/prohibited | passed |
| Task substitution | natural-language/task mismatch blocks synthesis | passed |
| Target substitution | duplicate/invalid pair blocks; lineage changes fail before process | passed |
| Output substitution | unsupported result type blocks synthesis | passed |
| Role substitution | non-CODEX role blocks synthesis | passed |
| Constraint substitution | any changed immutable constraint blocks synthesis | passed |
| Post-review prompt change | changed prompt hash fails before runner | passed |
| Hash continuity | preflight/review/approval/request/token/receipt/Replay identical | passed |
| Over-bound request | fails before the first human decision | passed |
| Knowledge routing | remains non-executing Platform Knowledge routing | passed regression |

Task content is serialized as a JSON string and explicitly labeled bounded
data. It cannot replace the surrounding role or constraints. Exact target
evidence hashes are included in the Worker execution contract even though only
workspace-relative paths are rendered to CODEX.

## Changed surface

Parent production changes:

- `aigol/runtime/codex_worker_activation_binding_runtime.py`: grounded Worker
  contract construction, two-stage admission/final preflight reuse, prompt and
  contract approval binding, fail-closed reconstruction, and truthful live
  fields;
- `aigol/cli/aicli.py`: exposes the final activation preflight capture without
  acquiring authority.

Nested canonical changes:

- `runtime/codex_synthesis/`: Worker execution contract, deterministic primary
  prompt, contract validation, prompt hash, evidence, and Replay identity;
- `runtime/codex_handoff/`: carries and validates the exact contract and prompt
  hash;
- `runtime/execution_gate/` and `runtime/execution_consumer/`: bind the prompt
  hash to existing execution authority and consumption;
- `runtime/codex_execution_adapter/`: bind the same hash to the existing
  request, validation, receipt, and evidence.

Tests changed/added:

- `tests/test_g31_20c_codex_synthesis_preflight.py` now distinguishes admission
  preflight identity from the final grounded activation preflight;
- `tests/test_g31_21b_codex_worker_prompt_fidelity_repair.py` covers prompt
  precedence, exact grounding/output/constraints, substitutions, hash
  continuity, and pre-process rejection.

Production diff size is 454 added and 17 removed lines across 19 existing
production files. The size is dominated by explicit contract validation and
hash propagation through already-existing owners; no parallel architecture or
artifact family was created.

## Validation evidence

| Validation | Result |
|---|---|
| Focused G31-21B plus synthesis-bound tests | `17 passed in 22.53s` |
| G31-17B/G31-18/G31-20, Repository Cognition, protected-runtime isolation, knowledge routing, synthesis/handoff/gate/consumer/adapter regressions | `151 passed in 183.50s` |
| Directly affected nested canonical contract tests | `40 passed in 0.11s` |
| Parent complete configured suite | `6473 passed, 4 skipped in 453.64s` |
| Governance conformance tests | `5 passed in 0.03s` |
| Governance engine | `PARTIALLY_CONFORMANT`; 18 passed, 2 known hook drifts, 0 critical violations; report hash `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea` |
| Targeted `py_compile` | passed |
| Parent and nested `git diff --check` | passed |

The nested legacy suite was also attempted. The system interpreter could not
collect four unrelated trading/credit tests because it lacks `numpy`. The
existing nested virtual environment collected 231 tests and produced 206
passes, 1 skip, and 24 failures in untouched historical auto-fix, repair,
development-loop, and type-error subsystems. The directly affected nested
contract suite is 40/40 green, and none of the 24 failures is in the changed
dependency surface. Two tracked registries mutated by that legacy suite were
restored exactly; they are absent from the final diff.

The governance engine's two known hook drifts remain visible: the root
expected/installed pre-commit hooks are missing, and the nested installed hook
lacks `promotion_gate_v02` and `check_layer_freeze`. This phase did not create
or conceal them.

## Single live disposable confirmation

Disposable repository:
`/tmp/g31-21b-live-6Ub76G/repository`
Disposable runtime root:
`/tmp/g31-21b-live-6Ub76G/runtime`

Raw request (168 characters):

> Fix the focused human interface test by inspecting aigol/runtime/human_interface.py and tests/test_human_interface.py. Return a minimal unified diff; do not edit files.

Routing and prompt truth:

| Field | Live value |
|---|---|
| route | `GOVERNED_DEVELOPMENT_RUNTIME` |
| grounded implementation | `aigol/runtime/human_interface.py` |
| grounded focused test | `tests/test_human_interface.py` |
| `worker_prompt_fidelity_verified` | `true` |
| `authorized_task_is_primary` | `true` |
| `grounded_implementation_target_present` | `true` |
| `grounded_test_target_present` | `true` |
| `requested_output_type` | `UNIFIED_DIFF` |
| `file_mutation_allowed` | `false` |

Transport, capture, and validation truth:

| Field | Live value |
|---|---|
| human decisions | 3 |
| governed `codex exec` activations | 1 |
| `transport_status` | `EXECUTION_ACCEPTED` |
| return code | 0 |
| timed out | `false` |
| parent launch shell | `false` |
| timeout | 60 seconds |
| prompt SHA-256 in receipt | `e041a406073da887f13dcb9d7fecf5ec99210de77d938e6915f22df6a7d8dfbc` |
| stdout bytes / SHA-256 | 185 / `446108657440950bc73ed3e60af824af698d79b9020055c3e422dd3014ba8df7` |
| stderr bytes | 3,240 (transport diagnostics only) |
| `semantic_worker_result_captured` | `true` |
| capture count | 1, proven by the single reconstructed capture family |
| capture Replay | created; 4 artifacts |
| `semantic_validation_performed` | `true` |
| `validation_status` | `RESULT_VALIDATED` |
| validation count | 1 |
| validation Replay | created; 4 artifacts |
| `provider_invoked` | `false` |
| `automatic_retry_performed` | `false` |
| `additional_worker_process_started` | `false` |
| `repository_mutated` | `false` |
| `result_accepted` | `false` |
| `commit_created` | `false` |

The current G31-18 return contract does not expose scalar
`capture_count`/`capture_replay_created` aliases. The one capture is proved by
one capture ID, one Replay reference, successful reconstruction, and four
ordered canonical artifacts. No second capture or live process was used.

The CODEX diagnostic stream identifies its own model transport as
`provider: openai`; this is not a SAPIANTA Provider-role invocation or
substitution. The governed selection and runtime truth remained CODEX ->
`codex-execution`, with `provider_invoked=false`. CODEX used one read-only
sandbox tool command to inspect the two allowed files; it did not start another
Worker, retry, or mutate source.

### Replay identities

| Family | Identity/hash | Count |
|---|---|---:|
| Activation | `sha256:42036ab8c31e8388e8c5f705e74460056f3dd0d0f0d62de887b1295abfa76bfa` | 3 |
| Activation review | `sha256:4383a900b486c9b77141fd0e98afb891331044a224db6e1164e10bec4f8d887b` | 1 |
| Third approval | `sha256:ddd6f5926a627c4593872d62b45918e054743519c56780eaa9e3b896e26ff493` | 1 |
| Transport receipt | `CODEX-EXECUTION-RECEIPT-6583f49a4c2ecbfa30bf7db1`; replay identity `6583f49a4c2ecbfa30bf7db12d01426ea3a431f792c323298e96d7e30529ad7b` | 1 |
| Worker output | `sha256:1ce255c7840af7ae06929e89c4b0f6f5d1aa1f212b1b27213ebe64d3d1bfc233` | 1 |
| Worker output payload | `sha256:5f204576b531cd3731ce6a4dccc90ae6069acfdde49564522ba7a5b70727204f` | 1 |
| Capture Replay | capture ID ending `CODEX-EXECUTION-RECEIPT-6583f49a4c2ecbfa30bf7db1:RESULT-CAPTURE` | 4 |
| Validation Replay | `sha256:a0bc252f557a48bbc20cc56f7ecabb3a3c9227db663c9e8ccad67d1176805f0e` | 4 |

### Authentic stdout and unaccepted observation

```diff
--- a/aigol/runtime/human_interface.py
+++ b/aigol/runtime/human_interface.py
@@ -1,2 +1,2 @@
 def render_summary(value):
-    return f"Status: {value}"
+    return f"Summary: {value}"
```

Non-canonical observation only:

- stdout names the implementation file but not the unchanged focused-test
  file;
- the diagnostic inspection evidence names and reads both grounded files;
- stdout contains valid unified-diff markers;
- it proposes the expected bounded `Status:` -> `Summary:` change;
- it does not describe or delegate another downstream task.

`task_outcome_satisfaction_evaluated=false` and
`task_outcome_satisfied=false` remain authoritative because no compatible
canonical G31 task-outcome owner exists.

## Protected and disposable hash comparison

| Path | Before | After |
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
| disposable `aigol/runtime/human_interface.py` | `7f3c53747a6ad36e5b1e0f69a55ba3cd4425aea022e822554fbb0ce700e7467b` | same |
| disposable `tests/test_human_interface.py` | `6cb9728c57aa10f995cb6dcb1508c0e8ddb5897a94b4f7895872db47c7a743d4` | same |

No `codex exec` process remained at final inspection. The protected paths were
not modified, reverted, deleted, staged, or included in a commit command.

## Git status and commit commands

No commit was created and nothing is staged. Parent HEAD is unchanged. Parent
status contains the nine protected pre-existing paths plus the intended two
production files, one adjusted regression, the new focused test, and this
report. Nested HEAD is unchanged; its status contains only the intended 17
canonical runtime files.

Exact commands excluding all protected paths:

```bash
git -C sapianta_system add \
  runtime/codex_synthesis/__init__.py \
  runtime/codex_synthesis/governed_codex_evidence.py \
  runtime/codex_synthesis/governed_codex_prompt_synthesizer.py \
  runtime/codex_synthesis/governed_codex_prompt_validator.py \
  runtime/codex_synthesis/governed_codex_replay.py \
  runtime/codex_synthesis/governed_codex_task_request.py \
  runtime/codex_synthesis/governed_codex_task_response.py \
  runtime/codex_handoff/governed_codex_handoff_evidence.py \
  runtime/codex_handoff/governed_codex_handoff_package.py \
  runtime/codex_handoff/governed_codex_handoff_response.py \
  runtime/codex_handoff/governed_codex_handoff_validator.py \
  runtime/execution_gate/governed_execution_authority_token.py \
  runtime/execution_consumer/governed_execution_consumer_validator.py \
  runtime/codex_execution_adapter/governed_codex_execution_evidence.py \
  runtime/codex_execution_adapter/governed_codex_execution_receipt.py \
  runtime/codex_execution_adapter/governed_codex_execution_request.py \
  runtime/codex_execution_adapter/governed_codex_execution_validator.py
git -C sapianta_system commit -m "fix(governance): preserve Codex Worker prompt fidelity"

git add \
  aigol/cli/aicli.py \
  aigol/runtime/codex_worker_activation_binding_runtime.py \
  tests/test_g31_20c_codex_synthesis_preflight.py \
  tests/test_g31_21b_codex_worker_prompt_fidelity_repair.py \
  docs/governance/G31_21B_CODEX_WORKER_PROMPT_FIDELITY_REPAIR.md
git commit -m "fix(governance): bind exact grounded task to Codex Worker"
```

## Progress, non-goals, and next state

Evidence-scoped whole-project progress is revised from **91.5% to 92.0%**. The
previously proven prompt-fidelity defect is repaired and one authentic live
execution produced the requested bounded patch through capture and governance
validation. The remaining material governed-development gap is canonical
task-outcome review and acceptance ownership.

Explicit non-goals remain:

- do not reinterpret `RESULT_VALIDATED` as task satisfaction or acceptance;
- do not apply, repair, rewrite, accept, reject, commit, deploy, or release the
  live diff;
- do not add automatic retry, fallback, Provider authority, or another Worker;
- do not make AiCLI authoritative;
- do not add a parallel task reviewer, acceptance system, or Replay family.

Recommended next state:

`G31_CANONICAL_TASK_OUTCOME_OWNER_AND_ACCEPTANCE_BOUNDARY_REQUIRED`
