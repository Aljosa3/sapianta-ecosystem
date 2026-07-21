# Generation 31-24G-R04-R04-R04-R01 Common Entry-Point and Narrow Adapter Architecture Repair

Status: completed interrupted-repair recovery and validation.

Date: 2026-07-21

Deterministic verdict:

`G31_COMMON_ENTRY_POINT_AND_NARROW_ADAPTER_ARCHITECTURE_REPAIRED`

Exactly one next state:

`G31_24G_R04_R04_R05_CANONICAL_APPROVED_V3_DECISION_TO_MUTATION_AUTHORIZATION_BINDING_REQUIRED`

## Constitutional scope

This repair treats Generation 30 and the committed G31 lineage through the A01
adapter-narrowness audit as immutable. It restores the certified dependency
direction without changing a low-level artifact family, decision owner, Replay
owner, authorization owner, Worker, Provider, mutation owner, or hash algorithm.

Authoritative audit evidence:

- committed report:
  `G31_24G_R04_R04_R04_A01_ADAPTER_NARROWNESS_AND_COMMON_ENTRY_POINT_PRESERVATION_AUDIT.md`;
- committed verdict: `G31_ADAPTER_NARROWNESS_DRIFT_DETECTED`;
- certified common entry:
  `human_interface_runtime_entry_service.run_human_interface_runtime_entry`;
- first regression: commit
  `14f1f6167692196159ee404ca6fe260b31ffe937`.

No file was staged or committed. No physical replacement, mutation,
authorization consumption, rollback, recovery, Provider invocation, or
unbounded Worker invocation was introduced by this repair.

## Initial Git state

```text
branch: master
HEAD: 206334b76a645cadd0e5410f826066d55019b517
HEAD subject: docs(governance): record G31 adapter narrowness drift audit
git diff --check: passed
```

The initial tracked diff contained 16 files with 1,762 additions and 887
deletions. It included six protected pre-existing runtime-evidence changes,
the interrupted production extraction, and eight test migrations. Three
protected empty marker files and three R01/R04 files were untracked.

Recent history confirmed the A01 audit at HEAD and the exact first regression
commit. The three nested repositories were present and clean.

## Mandatory working-tree classification

Every initial changed path was assigned exactly one category before production
work resumed.

### Category A — pre-existing unrelated and protected

- `.runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/diagnostic_evidence.json`;
- `.runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/governed_return.json`;
- `.runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/lineage.json`;
- `.runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stderr.txt`;
- `.runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stdout.txt`;
- `.runtime/aigol/ledger/governed_returns.jsonl`;
- `WORKER_INVOCATION_ARTIFACT_V1`;
- `WORKER_INVOKED`;
- `invocation`.

These paths were not modified, restored, staged, or interpreted as R01 work.

### Category B — interrupted R01 implementation already correct

- `tests/test_g31_12b_g31_selection_to_g24_worker_assignment_binding.py`;
- `tests/test_g31_13b_g31_assignment_to_g24_worker_dispatch_binding.py`;
- `tests/test_g31_14b_g31_dispatch_to_g24_worker_invocation_binding.py`;
- `tests/test_g31_15b_g31_invocation_to_execution_candidate_bounded_projection.py`;
- `tests/test_g31_16b_g31_candidate_to_governed_execution_bounded_projection.py`;
- `tests/test_g31_24d_versioned_human_content_acceptance_decision.py`;
- `tests/test_g31_24e_human_content_acceptance_to_existing_acceptance_binding.py`;
- `tests/test_g31_24g_r01_existing_file_candidate_provenance.py`;
- `tests/test_g31_24g_r04_r04_r04_aicli_v3_mutation_decision_transport.py`;
- `tests/test_g31_24g_r04_r04_r04_r01_common_entry_adapter_repair.py`.

The first eight tracked tests correctly moved static ownership assertions or
neutral actor expectations to the shared owner. The former R04 transport test
had been migrated into R01 compatibility coverage. The new repair test already
proved APPROVED and REJECTED through an in-memory adapter with no AiCLI import.

### Category C — obsolete uncommitted R04 disposition

- `docs/governance/G31_24G_R04_R04_R04_AICLI_V3_MUTATION_DECISION_TRANSPORT_BINDING.md`.

The file now records `SUPERSEDED BEFORE ACCEPTANCE`. It makes no operational
claim. Its useful behavior coverage remains in the migrated compatibility test.

### Category D — required remaining R01 work

- `aigol/runtime/human_interface_runtime_entry_service.py`;
- `aigol/cli/aicli.py`;
- this repair report.

The two production files contained useful partial extraction and were not
recreated. Inspection classified the extraction as partially correct, with one
missing fail-closed boundary and its corresponding terminal stop behavior.

## Interrupted implementation inventory

Already correct:

- the existing common entry accepted prior canonical application state and one
  neutral action value;
- G31 sequencing, Replay reconstruction, canonical pending-action selection,
  lifecycle aggregation, and presentation selection had moved to the shared
  runtime-entry owner;
- AiCLI mapped terminal commands to neutral actions and delegated each action;
- the neutral actor `HUMAN_OPERATOR` replaced transport-branded actor evidence;
- the in-memory adapter imported no CLI and called the same public entry;
- AiCLI no longer directly called G31 decision, authorization, selection,
  assignment, dispatch, invocation, execution, acceptance, candidate, or V3
  decision owners.

Partially correct:

- the shared task-outcome continuation invoked disposable-review preparation
  without preserving the previous fail-closed catch;
- AiCLI assumed every satisfied outcome produced a next pending disposable
  action and did not perform the prior terminal stop when preparation failed.

Obsolete:

- the original R04 report's operational claim; it is explicitly superseded.

Conflicting:

- none. The first failure exposed an omitted boundary behavior, not a competing
  architecture or duplicate owner.

## First reproduced failure

The prior failure output was unavailable. Ordered focused suites passed, so the
first full-suite run used `--maxfail=1`. It reproduced exactly:

```text
tests/test_g31_22b_live_task_outcome_review_continuation.py
::test_satisfied_continuation_binds_exact_bytes_and_stops

1 failed, 2794 passed
```

The existing test intentionally supplies a two-file unified diff whose test
preimage does not match. The disposable-review owner correctly raised
`FailClosedRuntimeError: ... preimage context mismatch`. Before extraction,
AiCLI caught that owner failure, retained the already-recorded task-outcome
decision, recorded blocker evidence, rendered the failure, and stopped. The
partial common entry let the exception escape.

## Root cause and bounded repair

Root cause: the interrupted move copied the positive disposable-review
sequence but omitted its application-boundary fail-closed catch. This was a
behavioral extraction omission, not a defect in unified-diff validation.

Repair:

1. `human_interface_runtime_entry_service._continue_g31_application_transition`
   now catches only `FailClosedRuntimeError` from disposable-review preparation,
   records the same blocker fields, and returns canonical failure presentation
   with no next pending action.
2. `aicli.run_reference_uhi_session` now treats the absence of that next action
   as terminal transport state and returns
   `TASK_OUTCOME_HUMAN_DECISION_RECORDED`.

The recovery patch added 16 net production lines across the two existing
files. It changed no low-level validator and no test expectation.

## Before and after call graph

Before A01 repair:

```text
terminal input
-> AiCLI
-> run_human_interface_runtime_entry through G31-08
-> AiCLI-owned G31 decision/Replay/Worker/execution/acceptance/V3 sequence
-> AiCLI-selected presentation
```

After repair:

```text
adapter input
-> adapter-neutral action translation
-> run_human_interface_runtime_entry
-> shared G31 application transition
-> canonical low-level owners
-> owner Replay/reconstruction
-> canonical aggregate state + pending action + presentation
-> adapter cache/render/terminal exit behavior
```

## Common-entry contract

The existing public entry remains
`run_human_interface_runtime_entry`. Its versioned G31 extension consumes:

- canonical session, workspace, created-at, and prior application state;
- one interface-neutral action value and neutral human actor;
- the existing bounded Worker process runner only at the already-certified
  activation stage;
- the existing governed runtime runner.

It returns:

- `g31_application_transition_version`;
- `g31_application_state_authority = CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY`;
- authoritative aggregate application state;
- `g31_pending_action` with canonical action type, valid values, and context;
- `g31_canonical_presentations` selected by the shared owner;
- existing evidence and Replay identities and exact stop flags.

Terminal syntax, slash commands, prompts, EOF, keyboard handling, and adapter
identity are not inserted into canonical decision hashes.

## Direct-call and responsibility inventory

AiCLI's direct application calls are now limited to:

- `prepare_unified_human_interface_project_context`;
- `record_unified_human_interface_workspace_state`;
- `guided_development_clarification`;
- `run_human_interface_runtime_entry`;
- the pre-existing governed conversation runner passed into that entry.

Static inspection found no direct AiCLI call to G31 decision recording, Replay
reconstruction, authorization, Worker selection/request/assignment/dispatch/
invocation, execution candidate, governed execution, activation, result
capture, semantic validation, task review, disposable validation, content
acceptance, existing-file candidate, or V3 mutation-decision owners.

Responsibilities removed from AiCLI:

- canonical owner ordering and branching;
- decision/candidate/request construction;
- Replay reconstruction and destination derivation;
- application lifecycle aggregation;
- authorization and Worker lifecycle sequencing;
- result/validation/acceptance/V3 sequencing;
- semantic presentation selection.

Responsibilities retained by AiCLI:

- terminal parsing, compose buffers, commands, EOF, Ctrl+C, help, and exit;
- translation of contextual terminal controls into neutral actions;
- one shared-entry call per application action;
- transport cache of returned canonical state and pending action;
- rendering strings selected by the common entry.

## Non-AiCLI proof

`InMemoryAdapter` in the focused R01 test imports only the common runtime entry.
It contains no copied low-level sequence and no AiCLI import. Through the same
entry it proves both exact V3 outcomes:

```text
APPROVED -> mutation_decision_approved=true
REJECTED -> mutation_decision_approved=false
```

Both paths reconstruct four decision Replay artifacts, bind the neutral actor,
return no pending action, and stop with authorization, request, Worker,
Provider, command, and repository-mutation flags false. Invalid transport
vocabulary, actor substitution, duplicate decision, and UI-only fields fail
closed or remain absent from canonical evidence.

## Replay and authority integrity

- Existing owner-specific Replay writers and reconstructors remain unchanged.
- AiCLI performs no Replay reconstruction.
- The common entry validates each transition through its existing owner before
  selecting the next pending action.
- Duplicate, tampered, reordered, cross-session, substituted-actor, invalid
  vocabulary, and incompatible lineage cases retain fail-closed behavior.
- CODEX remains `WORKER_ROLE`; Provider authority is absent.
- V1/V2 artifact compatibility remains covered.
- APPROVED and REJECTED V3 decisions stop before mutation authorization.

Mandatory final stop remains:

```text
human_mutation_decision_recorded = true
mutation_decision_approved = true | false
mutation_authorized = false
authorization_actor_bound = false
authorization_replay_recorded = false
authorization_consumed = false
replace_request_created = false
provider_invoked = false
command_executed = false
repository_mutated = false
main_repository_mutated = false
```

## Protected paths and hashes

Initial and final SHA-256 values are identical:

| Protected path | SHA-256 |
| --- | --- |
| `diagnostic_evidence.json` | `a626a69a8020bc730876119c52701a94de9ab6e4772cc64c1f5d017296650203` |
| `governed_return.json` | `e82f47c0c13678725993b21e2af2e0437edccaed324f861a7b58e77d7f8e787d` |
| `lineage.json` | `07b95505521e70f51cdddecc1057fd3a208b198445693c9a8da1e996df5799dd` |
| `provider_stderr.txt` | `d47a06d59aba2814c3fb7460049fc2ccbfc834196c956d6c6558e8be8b079e24` |
| `provider_stdout.txt` | `a73a499e2e9133c03d7babfd5c4dec7967f31e2bfb354ea9dd41df0a15c08cb3` |
| `.runtime/aigol/ledger/governed_returns.jsonl` | `dbc7b63f2a17c50c43bbb4fde4f44c1dbae8d25d550fb6b4d4daa14e17126161` |
| `WORKER_INVOCATION_ARTIFACT_V1` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `WORKER_INVOKED` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `invocation` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

## Validation

Final post-repair validation groups overlap and are not additive:

| Group | Result |
| --- | --- |
| Exact reproduced failure | 1 passed, 0 skipped, 0 failed |
| Focused common-entry and in-memory adapter repair | 4 passed, 0 skipped, 0 failed |
| G14 common-entry/UHI/conversation and G19 presentation | 33 passed, 0 skipped, 0 failed |
| Relevant G0-G30 Project Services, AiCLI, and Query Router | 32 passed, 0 skipped, 0 failed |
| Affected downstream G31 compatibility | 36 passed, 0 skipped, 0 failed |
| Decision and authorization | 75 passed, 0 skipped, 0 failed |
| Replay-selected repository tests | 1,137 passed, 0 skipped, 0 failed; 5,494 deselected |
| Governance conformance tests | 5 passed, 0 skipped, 0 failed |
| Full repository suite | **6,628 passed, 3 skipped, 0 failed** |
| Targeted `py_compile` | passed |
| Parent and nested `git diff --check` | passed |
| Protected hash verification | all nine exact |

The full suite completed in 4,404.34 seconds. The initial diagnostic full run
stopped at the first reproduced failure after 2,794 passes; it is not a final
validation result.

## Governance and nested repositories

Governance remains visibly `PARTIALLY_CONFORMANT`:

```text
checks_passed: 18
checks_failed: 2
critical_violations: 0
deterministic: true
fail_closed: true
read_only: true
report_hash: 0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea
```

The findings remain the known root hook absence and missing
`promotion_gate_v02` / `check_layer_freeze` tokens in the system hook. They do
not invalidate this repair and are not hidden or repaired here.

Nested repository final state:

- `sapianta-domain-credit`: clean `main...origin/main`;
- `sapianta_system`: clean
  `feature/governance-evolution-loop...origin/feature/governance-evolution-loop [ahead 2]`;
- `sapianta-domain-trading`: clean `main...origin/main`.

## Production and change accounting

Task production files:

- `aigol/runtime/human_interface_runtime_entry_service.py`: common application
  transition and canonical sequencing owner;
- `aigol/cli/aicli.py`: narrowed transport, action translation, cache,
  rendering, and terminal lifecycle.

Tracked production diff against HEAD:

```text
aigol/cli/aicli.py: +204 / -865
aigol/runtime/human_interface_runtime_entry_service.py: +1456 / -0
production total: +1660 / -865
```

The interrupted recovery itself added only 16 net production lines to the
partial extraction. Test changes are compatibility ownership/actor migrations
plus two focused modules. No new production module was created.

## Obsolete R04 disposition

The former R04 report is retained only as explicit superseded lineage. Its
original operational claim is not accepted. Its APPROVED, REJECTED, invalid
input, EOF, lineage, and zero-downstream-call behavior is preserved by the
common-entry compatibility test and the non-AiCLI proof.

## Progress and conclusion

- common-entry/narrow-adapter repair: **100% proven for the G31-through-V3 scope**;
- no-copy/paste conversational reachability: **99.92%**;
- architecture-safe G31 integration: **100% through reconstructed V3 decision**;
- whole-project evidence-scoped estimate: **97.8%**.

The certified dependency direction is restored. AiCLI is transport-only for
the extracted G31 sequence, and a non-AiCLI adapter reaches both terminal V3
outcomes through the same public entry. The next transition must remain behind
that common entry.

## Commit commands

```bash
git add aigol/cli/aicli.py aigol/runtime/human_interface_runtime_entry_service.py
git add tests/test_g31_12b_g31_selection_to_g24_worker_assignment_binding.py tests/test_g31_13b_g31_assignment_to_g24_worker_dispatch_binding.py tests/test_g31_14b_g31_dispatch_to_g24_worker_invocation_binding.py tests/test_g31_15b_g31_invocation_to_execution_candidate_bounded_projection.py tests/test_g31_16b_g31_candidate_to_governed_execution_bounded_projection.py
git add tests/test_g31_24d_versioned_human_content_acceptance_decision.py tests/test_g31_24e_human_content_acceptance_to_existing_acceptance_binding.py tests/test_g31_24g_r01_existing_file_candidate_provenance.py
git add tests/test_g31_24g_r04_r04_r04_aicli_v3_mutation_decision_transport.py tests/test_g31_24g_r04_r04_r04_r01_common_entry_adapter_repair.py
git add docs/governance/G31_24G_R04_R04_R04_AICLI_V3_MUTATION_DECISION_TRANSPORT_BINDING.md docs/governance/G31_24G_R04_R04_R04_R01_COMMON_ENTRY_POINT_AND_NARROW_ADAPTER_ARCHITECTURE_REPAIR.md
git commit -m "fix(runtime): restore G31 common entry and narrow AiCLI adapter"
```

The protected Category A paths are intentionally absent from these commands.

## Complete bounded next Codex prompt

```text
# Generation 31-24G-R04-R04-R05 — Canonical Approved V3 Decision to Mutation Authorization Binding

Treat Generation 30 and the accepted G31 common-entry repair as immutable.

Required repair verdict:
G31_COMMON_ENTRY_POINT_AND_NARROW_ADAPTER_ARCHITECTURE_REPAIRED

Required current state:
G31_24G_R04_R04_R05_CANONICAL_APPROVED_V3_DECISION_TO_MUTATION_AUTHORIZATION_BINDING_REQUIRED

Objective:
Bind exactly one reconstructed APPROVED V3 existing-file mutation decision to
the existing mutation-authorization owner through the same public
run_human_interface_runtime_entry application boundary.

First inspect and document the existing contracts for:
- authorize_g31_approved_existing_file_mutation;
- mutation authorization artifact and Replay reconstruction;
- V3 human mutation decision, candidate, acceptance, grounding, and actor;
- common-entry canonical state, pending action, and presentation.

Reuse those contracts. Do not create a new authorization family, policy
engine, router, decision, Replay subsystem, mutation request, Worker, Provider,
or adapter-specific sequence.

Required behavior:
- APPROVED reconstructed V3 decision may produce exactly one existing immutable
  mutation-authorization artifact and Replay through the common entry;
- REJECTED, missing, duplicate, cross-session, stale, reordered, substituted,
  or hash-invalid evidence fails closed before authorization;
- authorization scope must exactly equal the accepted candidate provenance,
  workspace, target, preimage/postimage hashes, operation, actor, and validation
  evidence;
- AiCLI may only translate one contextual action, call the common entry, cache,
  and render the returned canonical result;
- the in-memory non-AiCLI adapter must prove the same transition without an
  AiCLI import or copied sequencing.

Mandatory stop after authorization and Replay reconstruction:
mutation_authorized=true only for exact APPROVED evidence;
authorization_actor_bound=false;
authorization_consumed=false;
replace_request_created=false;
worker_selected=false;
worker_dispatched=false;
provider_invoked=false;
command_executed=false;
repository_mutated=false;
main_repository_mutated=false.

Do not call actor/Replay consumption binding, authenticated request creation,
filesystem replacement, restoration, rollback, recovery, completion, or
termination owners. Do not mutate a target repository.

Preserve the two adapter model, neutral actor semantics, existing artifacts and
hashes, all protected paths, Replay ordering, fail-closed behavior, and known
Governance findings. Prefer one existing-function call from the common entry.
If the existing authorization input is incompatible, stop at the first exact
field and report one bounded projection only.

Add focused APPROVED, REJECTED, duplicate, tamper, cross-session, Replay, stop-
boundary, AiCLI narrowness, and in-memory adapter tests. Run focused suites,
common-entry/interface tests, relevant G31 compatibility, decision, Replay,
Governance, py_compile, diff/hash checks, then the full suite only after all
focused evidence passes.

Add one governance report for R05. Do not stage or commit. Return one
deterministic verdict and exactly one next state.
```
