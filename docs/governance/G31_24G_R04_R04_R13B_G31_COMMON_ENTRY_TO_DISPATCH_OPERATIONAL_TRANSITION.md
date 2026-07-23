# Generation 31-24G-R04-R04-R13B G31 Common Entry to Dispatch Operational Transition

Status: completed bounded operational transition; stopped immediately after
successful Worker Dispatch construction and Replay reconstruction.

Date: 2026-07-23

Deterministic verdict:

`G31_COMMON_ENTRY_TO_DISPATCH_OPERATIONAL`

Exactly one next state:

`G31_24G_R04_R04_R14A_WORKER_INVOCATION_OPERATIONAL_READINESS_AUDIT_REQUIRED`

## Constitutional scope

This generation treats G0-G30 Platform Core and accepted G31 R05 through
R13A as immutable certified baselines.

It adds only the existing Common Entry mutation continuation from the exact
R12B Worker Assignment capture to the existing certified Dispatch owner. The
transition:

1. retains the exact certified Assignment artifact and Replay;
2. calls `dispatch_assigned_worker` once;
3. requires the existing `WORKER_DISPATCHED` result;
4. reconstructs the existing four-step Dispatch Replay once;
5. validates Assignment, request, chain, Worker, and authority continuity;
6. aggregates the Dispatch capture through Common Entry;
7. uses the existing canonical Dispatch presentation; and
8. stops before Worker Invocation or every later execution stage.

It does not change the Dispatch runtime, Assignment runtime, Worker Registry,
Worker identity, capability, artifact families, Replay families, selector,
authorization model, adapter authority, Invocation runtime, Worker runtime,
Provider runtime, or mutation owner.

No live user Dispatch, Invocation, Worker, Provider, command, target-open,
repository-mutation, restoration, rollback, or recovery workflow ran.
Successful Dispatch construction occurred only inside isolated temporary test
directories.

## Accepted baseline

The production work began from:

- branch: `master`;
- HEAD: `015182d55a938ec38da8c16a5623143cc0fb60c3`;
- HEAD subject:
  `docs(governance): certify dispatch operational readiness`;
- R12B verdict:
  `G31_COMMON_ENTRY_TO_ASSIGNMENT_OPERATIONAL`;
- R13A verdict:
  `G31_DISPATCH_OPERATIONAL_READY`;
- certified Worker:
  `FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER`;
- certified Assignment runtime:
  `AIGOL_WORKER_ASSIGNMENT_RUNTIME_V1`;
- certified Dispatch runtime:
  `AIGOL_WORKER_DISPATCH_RUNTIME_V1`.

The worktree resolved to a clean HEAD before production edits. The six checked
runtime evidence/ledger paths were not edited by R13B. Three certified
zero-byte marker paths that were present in the first observed state
disappeared during that baseline transition; they were restored as exact
zero-byte files after the complete-suite protected-evidence test identified
their absence.

## Minimal implementation

Only the existing
`aigol/runtime/human_interface_runtime_entry_service.py` production owner was
modified.

The existing `_authorize_g31_mutation_decision` continuation now performs:

```text
exact R12B WORKER_ASSIGNMENT_ARTIFACT_V1
  -> exact R12B Assignment Replay reference
  -> dispatch_assigned_worker
  -> existing four-step Dispatch Replay
  -> reconstruct_worker_dispatch_replay
  -> Common Entry aggregate and presentation
  -> stop before Worker Invocation
```

No helper, module, Worker-specific branch, registry, selector, Dispatch owner,
serializer, hasher, artifact family, Replay family, adapter entry, or
execution path was added.

The deterministic Dispatch inputs are:

```text
worker_dispatch_id =
  <worker_assignment_id>:DISPATCH

worker_assignment_artifact =
  exact returned R12B worker_assignment_artifact

worker_assignment_replay_reference =
  exact returned R12B worker_assignment_replay_reference

dispatched_by =
  PLATFORM_CORE_G31_DISPATCH_BINDING

Dispatch Replay destination =
  WORKER-DISPATCH-<Assignment artifact-hash suffix>
```

Common Entry does not search for an Assignment, infer one from presentation
fields, or select a Worker again.

## Existing Dispatch owner reuse

`dispatch_assigned_worker` remains solely responsible for:

- validating the Assignment artifact;
- reconstructing the complete Assignment Replay;
- reconstructing the nested invocation-request Replay;
- validating Assignment identity and hash;
- validating request, authorization, execution-packet, chain, Worker, family,
  and role continuity;
- rejecting an unavailable, already-dispatched, invoked, executing, or
  result-producing Worker;
- creating Dispatch evidence;
- creating Dispatch classification;
- creating the Dispatch artifact;
- creating the Dispatch result; and
- writing the ordered immutable Dispatch Replay.

Common Entry neither manufactures a Dispatch artifact nor treats the selected
resource identity as Dispatch authority.

## Dispatch Replay reconstruction

After successful Dispatch, Common Entry calls
`reconstruct_worker_dispatch_replay` on the exact returned Replay reference.

The reconstruction must prove:

```text
dispatch_status = WORKER_DISPATCHED
worker_dispatch_id = returned Dispatch reference
worker_assignment_reference = exact Assignment identity
worker_assignment_hash = exact Assignment artifact hash
worker_id = exact certified selected Worker
chain_id = exact invocation-request chain
worker_invocation_request_reference = exact invocation-request identity
worker_assigned = true
worker_dispatched = true
dispatch_requested = true
worker_invoked = false
execution_started = false
result_created = false
governance_mutated = false
replay_mutated = false
```

Any mismatch raises `FailClosedRuntimeError` before Common Entry can return a
successful Dispatch state.

The existing Dispatch Replay contains exactly:

```text
000_dispatch_evidence_recorded.json
001_dispatch_classification_recorded.json
002_dispatch_artifact_recorded.json
003_dispatch_result_recorded.json
```

The existing reconstructor revalidates wrapper ordering and hashes, every
artifact hash, evidence-to-classification continuity,
classification-to-Dispatch continuity, Dispatch-to-result continuity, chain
agreement, Assignment identity/hash agreement, the nested Assignment Replay,
and the nested invocation-request Replay.

No R05-R12B parent event is rewritten, repeated, consumed again, or
reauthorized.

## Exact continuity matrix

| Contract | R12B source | R13B requirement | Result |
|---|---|---|---|
| Assignment identity | Assignment artifact | Dispatch Assignment reference | exact |
| Assignment hash | Assignment artifact hash | Dispatch Assignment hash | exact |
| Assignment Replay | returned Replay reference | Dispatch evidence parent | exact |
| Worker identity | certified selected Worker | Dispatch Worker | exact |
| Request identity | R09B request | reconstructed Dispatch lineage | exact |
| Canonical chain | request `chain_id` | Dispatch `chain_id` | exact |
| Authorization | certified request lineage | reconstructed Dispatch lineage | preserved |
| Execution packet | certified request lineage | reconstructed Dispatch lineage | preserved |
| Dispatch authority | existing Dispatch owner | no Common Entry fabrication | preserved |
| Invocation authority | absent at Dispatch | must remain absent | preserved |

## Common Entry and Human Interface neutrality

`run_human_interface_runtime_entry` remains the only public application
transition.

The in-memory adapter and AiCLI receive the same canonical Dispatch state from
Common Entry. AiCLI contains no call to:

- `dispatch_assigned_worker`;
- `reconstruct_worker_dispatch_replay`; or
- any Dispatch artifact or Replay writer.

The lifecycle presentation now states:

```text
Worker Dispatch Reached: True
```

It then delegates detail rendering to the existing
`render_worker_dispatch_summary`, including:

```text
Dispatch Status: WORKER_DISPATCHED
No Worker has been invoked, executed, or produced results.
```

No adapter gained Assignment, Dispatch, Replay, Worker, or execution
authority.

## Authority and stop boundary

The successful R13B application state is:

```text
worker_selected = true
worker_assigned = true
worker_dispatched = true
dispatch_requested = true
provider_invoked = false
worker_invoked = false
execution_started = false
execution_requested = false
result_created = false
command_executed = false
target_opened = false
repository_mutated = false
main_repository_mutated = false
restoration_started = false
rollback_started = false
recovery_started = false
governance_mutated = false
replay_mutated = false
```

Focused spies remained zero for Worker Invocation, governed Worker execution,
existing-file replacement, target opening, restoration, rollback, and
recovery.

No `WORKER-INVOCATION-*` Replay was created by the R13B Common Entry
continuation.

## Fail-closed evidence

Focused tests prove:

- a failed Dispatch result is rejected before Invocation;
- a reconstructed Dispatch with `worker_invoked = true` is rejected before
  Invocation;
- exact Dispatch and reconstruction owners are each called once;
- the Dispatch artifact retains the exact Assignment identity and hash;
- the Dispatch artifact retains the exact request identity and canonical
  chain;
- the four expected Dispatch wrappers are present and reconstructible;
- in-memory and AiCLI adapters receive the same canonical Dispatch outcome;
- AiCLI contains no Dispatch authority;
- Common Entry contains no replacement-Worker name, capability, CODEX alias,
  Invocation call, governed-execution call, or mutation call; and
- the transition stops with Invocation and execution false.

Existing Dispatch-runtime tests retain tamper, duplicate, authority,
availability, Assignment-lineage, nested-selection, role, registry,
certification, and Replay fail-closed coverage.

## Regression adjustments

Five existing test files were adjusted only to acknowledge the newly
permitted Dispatch boundary:

- R07 now permits the later certified Assignment and Dispatch stages while
  continuing to forbid Invocation and mutation;
- R08C now permits later Assignment and Dispatch while continuing to assert
  that the immutable Selection capture itself remains pre-Assignment;
- R09B now proves its request lineage survives through Dispatch and stops
  before Invocation;
- R12B still proves exact Assignment construction, now followed by the
  certified Dispatch continuation; and
- the earlier G31 Dispatch source-count guard now permits the second
  constitutionally distinct Common Entry Dispatch call.

The older generic G31 execution lifecycle continues to use its existing
Dispatch call. R13B does not replace or alter that path.

## Change size

The scoped delta before this report is:

| Category | Files | Insertions | Deletions |
|---|---:|---:|---:|
| Production | 1 modified | 67 | 3 |
| Focused tests | 1 new | 225 | 0 |
| Regression tests | 5 modified | 20 | 18 |
| Dispatch/Assignment runtimes | 0 | 0 | 0 |
| Registries/certification evidence | 0 | 0 | 0 |
| Protected markers | 3 restored empty | 0 | 0 |

The production additions are limited to the Dispatch call, Replay
reconstruction, exact continuity checks, state aggregation, and existing
summary rendering.

## Validation

Validation ran in the required order.

| Validation group | Passed | Skipped | Failed |
|---|---:|---:|---:|
| Focused R13B and R12B boundary | 10 | 0 | 0 |
| R05-R13B Generation 31 regressions | 168 | 0 | 0 |
| Dispatch, Common Entry, architecture, authority, and Governance | 43 | 0 | 0 |
| Exact complete-suite failure closure | 2 | 0 | 0 |

Targeted `py_compile` passed for the modified production owner, the new R13B
test, and the R12B regression test.

Parent and all three nested `git diff --check` checks passed.

### Exactly-once complete repository suite

The complete repository suite ran exactly once:

```text
6795 passed, 4 skipped, 2 failed in 4473.76s (1:14:33)
```

The two failures were deterministic and fully classified:

1. `test_dispatch_stage_remains_non_invoking_before_later_invocation`
   retained an obsolete global source count of one Dispatch call. R13B
   legitimately adds the second call in the distinct existing-file mutation
   continuation.
2. `test_codex_version_diagnostic_persists_only_to_explicit_disposable_runtime`
   could not hash the three certified zero-byte protected marker paths because
   they had disappeared during the clean-baseline transition before R13B
   implementation.

After the bounded closure:

```text
2 passed in 2.62s
```

The marker paths again have the certified empty-file SHA-256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

No second complete-suite run was performed, preserving the exactly-once rule.
Therefore this report does not misstate the exactly-once complete suite as
green; it records the complete result and the exact targeted closure.

## Governance result

The read-only conformance engine remains:

`PARTIALLY_CONFORMANT`

- checks passed: 18;
- checks failed: 2;
- critical violations: 0;
- deterministic: true;
- fail-closed: true;
- read-only: true;
- report hash:
  `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea`.

The two known findings remain unchanged:

1. the root expected and installed pre-commit hooks are missing; and
2. the system pre-commit hook lacks `promotion_gate_v02` and
   `check_layer_freeze`.

R13B neither repairs nor reinterprets those findings.

## Protected and nested state

The six checked runtime evidence/ledger paths were not modified by R13B. Their
hashes at the clean production-edit baseline and final verification are:

| Protected path | SHA-256 |
|---|---|
| `diagnostic_evidence.json` | `21546ed151c165c6364aa914d892c34b117ef1ab664ae09d8e2c2a5327bcc8df` |
| `governed_return.json` | `ee57877ceea7d85bd9e3bb29aca64f3637384a7346a5b6a4c4f922c87cb2bcf7` |
| `lineage.json` | `8c47abb9a7c238c9f527e54dd88aa304edbca03b97ea630a4907b4ef139b3a08` |
| `provider_stderr.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `provider_stdout.txt` | `f2fec907b48e7162211f26bbe94352d40f4f6c4380ab3aa4256d072b7c602f30` |
| `governed_returns.jsonl` | `71b085174a274b870617c21810d9a496421985675ae0945f4b56bd3afe7b1118` |
| each restored protected marker | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

The nested repositories remain clean at:

- `sapianta-domain-credit`:
  `8615e1e290471a67e4e764c6ab2138340bc7936f`;
- `sapianta_system`:
  `3183bab71f8f30397c0309dd2e6d846d14a11f66`;
- `sapianta-domain-trading`:
  `d3038dc4ba36ffbaee9161172b4c852e8e6acbda`.

## Git state

Nothing was staged and no commit was created.

The intended R13B paths are:

```text
M  aigol/runtime/human_interface_runtime_entry_service.py
M  tests/test_g31_13b_g31_assignment_to_g24_worker_dispatch_binding.py
M  tests/test_g31_24g_r04_r04_r07_authenticated_request_consumption.py
M  tests/test_g31_24g_r04_r04_r08c_consumed_request_certified_worker_selection.py
M  tests/test_g31_24g_r04_r04_r09b_r08c_invocation_request_compatibility.py
M  tests/test_g31_24g_r04_r04_r12b_common_entry_assignment_operational_transition.py
?? tests/test_g31_24g_r04_r04_r13b_common_entry_dispatch_operational_transition.py
?? docs/governance/G31_24G_R04_R04_R13B_G31_COMMON_ENTRY_TO_DISPATCH_OPERATIONAL_TRANSITION.md
?? WORKER_INVOCATION_ARTIFACT_V1
?? WORKER_INVOKED
?? invocation
```

## Progress and verdict

R13B operationally reaches the existing certified Dispatch construction and
reconstructs its exact Replay through Common Entry.

It does not claim Worker Invocation, Worker execution, physical target
mutation, release readiness, regulatory compliance, or resolution of the two
known Governance hook findings.

Deterministic verdict:

`G31_COMMON_ENTRY_TO_DISPATCH_OPERATIONAL`

Exactly one next state:

`G31_24G_R04_R04_R14A_WORKER_INVOCATION_OPERATIONAL_READINESS_AUDIT_REQUIRED`
