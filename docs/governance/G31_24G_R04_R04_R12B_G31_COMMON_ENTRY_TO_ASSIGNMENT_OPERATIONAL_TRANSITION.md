# Generation 31-24G-R04-R04-R12B G31 Common Entry to Assignment Operational Transition

Status: completed bounded operational transition; stopped immediately after
successful Worker Assignment.

Date: 2026-07-23

Deterministic verdict:

`G31_COMMON_ENTRY_TO_ASSIGNMENT_OPERATIONAL`

## Constitutional scope

This generation treats G0-G30 Platform Core and accepted G31 R05, R06, R07,
R08, R08A, R08B, R08C, R09A, R09B, R10A, R10B, R11A, R11B, and R12A as
immutable certified baselines.

It adds only the Common Entry application binding that:

1. takes the exact certified R09B invocation-request artifact;
2. calls the existing R11B Worker Registry projection;
3. submits the exact request, request Replay, and projected Worker artifact to
   the existing certified Assignment owner;
4. reconstructs the existing four-step Assignment Replay;
5. verifies identity, chain, request, Worker, and stop-state continuity;
6. aggregates the returned Assignment capture through Common Entry; and
7. stops before Dispatch or every later lifecycle stage.

It does not change the Worker Registry projection, Assignment runtime,
Assignment artifact families, Assignment Replay family, Worker identity,
Worker capability, request hash contract, selection lineage, authority model,
adapter authority, Dispatch, Invocation, execution, or mutation owners.

No live Dispatch, Invocation, Worker, Provider, command, target-open,
repository-mutation, restoration, rollback, or recovery workflow ran.

## Accepted baseline

The work began from:

- branch: `master`;
- HEAD: `4170998de319a0a903e1cb7f1fe1cafebd422acb`;
- HEAD subject:
  `docs(governance): certify worker assignment execution readiness`;
- R11B verdict:
  `G31_WORKER_ARTIFACT_PROJECTION_COMPATIBILITY_OPERATIONAL`;
- R12A verdict:
  `G31_WORKER_ASSIGNMENT_EXECUTION_READY`;
- certified Worker:
  `FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER`;
- certified Worker version:
  `G8_12_EXISTING_FILE_MUTATION_IMPLEMENTATION_V1`;
- certified capability: `REPLACE_EXISTING_TEXT_FILE`;
- certified Assignment runtime:
  `AIGOL_WORKER_ASSIGNMENT_RUNTIME_V1`.

The six modified runtime-evidence/ledger paths and three empty marker paths
predated R12B. Their hashes were recorded before implementation and remained
unchanged.

## Minimal implementation

The production change modifies only the existing
`human_interface_runtime_entry_service.py`.

The existing `_authorize_g31_mutation_decision` continuation now performs:

```text
exact R09B WORKER_INVOCATION_REQUEST_ARTIFACT_V1
  -> default_worker_registry_for_request
  -> exact R11B WORKER_ARTIFACT_V1
  -> assign_worker_from_invocation_request
  -> existing four-step Worker Assignment Replay
  -> reconstruct_worker_assignment_runtime_replay
  -> Common Entry aggregate
  -> stop before Dispatch
```

No helper, module, Worker-specific branch, registry, selector, Assignment
owner, serializer, hasher, artifact family, Replay family, or adapter entry
was added.

The transition uses deterministic existing identities:

```text
worker_assignment_id =
  <certified selection_id>:ASSIGNMENT

assigned_by =
  PLATFORM_CORE_G31_ASSIGNMENT_BINDING

assignment Replay destination =
  WORKER-ASSIGNMENT-<invocation-request artifact-hash suffix>
```

## Exact Worker Registry reuse

Common Entry calls `default_worker_registry_for_request` once with the exact
certified invocation-request artifact and the existing transition timestamp.

The existing R11B projection returns one `WORKER_ARTIFACT_V1` with:

```text
worker_id = FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER
worker_version = G8_12_EXISTING_FILE_MUTATION_IMPLEMENTATION_V1
worker_family = FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER
worker_role = WORKER_ROLE
capability_id = REPLACE_EXISTING_TEXT_FILE
state = AVAILABLE
selected_resource_category = WORKER
selected_authority_profile = WORKER_AUTHORIZED_TASK_ONLY
selected_domain_id = NATIVE_DEVELOPMENT
```

The artifact preserves the exact Selection artifact hash, Selection context
identity/hash, registry hash, certification hash, and Selection Replay
reference. It carries no Governance, approval, Provider, self-authorization,
Replay-mutation, Dispatch, Invocation, execution, or completion authority.

Common Entry does not inspect the Worker name or capability to select a
branch. All eligibility and compatibility checks remain owned by the existing
projection and Assignment runtime.

## Existing Assignment owner reuse

Common Entry calls `assign_worker_from_invocation_request` once with:

- the deterministic Assignment identity;
- the exact R09B request artifact;
- the exact request Replay reference;
- the one-element R11B Worker artifact list;
- the existing Common Entry timestamp;
- the existing bounded assigning actor; and
- one unused session-local Assignment Replay destination.

The Assignment owner remains solely responsible for:

- request artifact validation;
- R10B request-hash validation;
- invocation-request Replay reconstruction;
- duplicate-Assignment rejection;
- Worker artifact validation;
- family, role, packet, output, and prohibition compatibility;
- sole-candidate selection;
- Assignment evidence creation;
- Assignment classification;
- Assignment artifact creation;
- Assignment result creation; and
- ordered immutable Replay persistence.

Common Entry neither manufactures an Assignment result nor treats
`selected_resource_id` as an Assignment artifact.

## Assignment Replay reconstruction

After successful Assignment, Common Entry calls
`reconstruct_worker_assignment_runtime_replay` once on the returned Replay
reference.

The reconstructed Replay must match:

```text
assignment_status = WORKER_ASSIGNED
worker_assignment_id = returned Assignment reference
worker_id = certified selected_resource_id
canonical_chain_id = invocation-request chain_id
worker_invocation_request_reference = exact invocation-request identity
worker_assigned = true
worker_dispatched = false
worker_invoked = false
execution_started = false
governance_mutated = false
replay_mutated = false
```

Any mismatch raises `FailClosedRuntimeError` before Common Entry returns a
successful application state.

The existing Assignment Replay contains exactly:

```text
000_assignment_evidence_recorded.json
001_assignment_classification_recorded.json
002_assignment_artifact_recorded.json
003_assignment_result_recorded.json
```

The existing reconstructor verifies wrapper order and hashes, artifact hashes,
evidence-to-classification continuity, classification-to-Assignment
continuity, Assignment-to-result continuity, canonical chain agreement,
invocation-request identity/hash agreement, and nested request Replay
reconstruction.

No R05-R11B parent Replay event is rewritten, repeated, or reauthorized.

## Common Entry aggregation and presentation

`run_human_interface_runtime_entry` remains the only public application
transition.

The returned application state now includes:

- `worker_assignment_capture`;
- `worker_assignment_reconstruction`;
- `worker_assignment_status`;
- `worker_assignment_id`;
- `worker_assignment_replay_reference`;
- `worker_assignment_replay_hash`;
- `assigned_worker_id`;
- `worker_assigned = true`; and
- the Assignment Replay as `runtime_replay_reference`.

The existing lifecycle presentation now truthfully states:

```text
Worker Assignment Reached: True
```

It also delegates detail rendering to the existing
`render_worker_assignment_summary`, which states:

```text
No Worker has been dispatched, invoked, or executed.
```

AiCLI continues to call only Common Entry. It contains no call to the Worker
Registry projection or Assignment owner.

## Authority and stop boundary

The successful R12B transition reaches exactly:

```text
worker_selected = true
worker_invocation_request_created = true
worker_assigned = true
worker_dispatched = false
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

The selected-resource capture remains immutable at its own earlier boundary
with `worker_assigned = false`; the Common Entry aggregate advances to true
only from the existing Assignment result.

Focused spies remained zero for Dispatch, Invocation, governed execution,
authenticated replacement execution, filesystem replacement, target opening,
restoration, rollback, and recovery owners.

## Fail-closed evidence

Focused R12B tests prove:

- an empty projected Worker Registry causes Assignment to fail closed;
- no successful Assignment artifact is recorded for that invalid registry;
- a reconstructed Assignment Replay claiming Dispatch fails the Common Entry
  continuity check;
- neither invalid case calls Dispatch, Invocation, execution, target-open, or
  mutation owners;
- the exact projection, Assignment, and reconstruction owners are each called
  once on success;
- the exact Worker, request, chain, Selection, and Worker-artifact hashes
  remain connected;
- the Assignment Replay contains the exact four-file ordered set;
- in-memory and AiCLI continuations receive the same canonical Assignment
  state; and
- the Common Entry binding contains no filesystem-replacement Worker identity,
  replacement capability, CODEX identity, Dispatch, Invocation, governed
  execution, or physical replacement call.

## Baseline regression adjustments

Three earlier focused tests were advanced only at the newly permitted
Assignment boundary:

- R07 now permits the existing Assignment owner and asserts
  `worker_assigned = true`;
- R08C no longer spies Assignment as forbidden, while its immutable Selection
  capture still asserts `worker_assigned = false`;
- R09B now asserts that the exact invocation request continues through
  Assignment and stops before Dispatch.

Their existing prohibitions on Dispatch, Invocation, Worker execution,
Provider execution, command execution, target opening, repository mutation,
restoration, rollback, and recovery remain unchanged.

## Change size

The scoped R12B delta before this report is:

| Category | Files | Insertions | Deletions |
|---|---:|---:|---:|
| Production | 1 modified | 84 | 4 |
| Focused R12B tests | 1 new | 248 | 0 |
| Advanced baseline tests | 3 modified | 6 | 6 |
| Registry/certification evidence | 0 | 0 | 0 |

No Assignment runtime, Worker Registry runtime, invocation-request runtime,
selector, Worker implementation, adapter, or downstream lifecycle runtime was
modified.

## Validation

Validation ran before the complete suite.

| Validation group | Passed | Skipped | Failed |
|---|---:|---:|---:|
| Final R12B exact binding, fail-closed, Replay, adapter, and stop gate | 8 | 0 | 0 |
| R05-R11B certified-spine regressions | 158 | 0 | 0 |
| Invocation-request, Assignment, Assignment Replay, and existing binding regressions | 72 | 0 | 0 |
| Common Entry, Human Interface, authority, operational-entry, and layer boundaries | 32 | 0 | 0 |
| Governance tests | 5 | 0 | 0 |

The first focused attempt returned three test failures because a new
downstream spy named a nonexistent governed-execution symbol. The spy was
corrected to the existing `run_governed_worker_execution` owner; production
behavior was unchanged.

The next focused attempt returned one failure because the successful Common
Entry aggregate omitted an explicit `execution_requested = false`. The
aggregate was tightened to state every downstream boundary explicitly. The
final focused gate then passed 8 tests.

Targeted `py_compile` passed for:

- `aigol/runtime/human_interface_runtime_entry_service.py`;
- the three adjusted baseline test files; and
- the new R12B focused test file.

Parent and all three nested `git diff --check` checks passed.

The complete repository suite was invoked exactly once after all focused
groups were green:

```text
6791 passed, 3 skipped, 0 failed in 4180.08s (1:09:40)
```

No repair followed the complete suite, and no second complete-suite
invocation occurred.

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

The two known hook findings remain visible and unchanged: the root expected
and installed hooks are missing, and the system pre-commit hook lacks
`promotion_gate_v02` and `check_layer_freeze`. R12B neither repairs nor
reinterprets them.

## Protected and nested state

All protected SHA-256 values equal the pre-R12B baseline:

| Protected path | SHA-256 |
|---|---|
| `diagnostic_evidence.json` | `a626a69a8020bc730876119c52701a94de9ab6e4772cc64c1f5d017296650203` |
| `governed_return.json` | `e82f47c0c13678725993b21e2af2e0437edccaed324f861a7b58e77d7f8e787d` |
| `lineage.json` | `07b95505521e70f51cdddecc1057fd3a208b198445693c9a8da1e996df5799dd` |
| `provider_stderr.txt` | `d47a06d59aba2814c3fb7460049fc2ccbfc834196c956d6c6558e8be8b079e24` |
| `provider_stdout.txt` | `a73a499e2e9133c03d7babfd5c4dec7967f31e2bfb354ea9dd41df0a15c08cb3` |
| `governed_returns.jsonl` | `dbc7b63f2a17c50c43bbb4fde4f44c1dbae8d25d550fb6b4d4daa14e17126161` |
| each protected marker | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

The nested repositories remain clean at their accepted commits:

- `sapianta-domain-credit`:
  `8615e1e290471a67e4e764c6ab2138340bc7936f`;
- `sapianta_system`:
  `3183bab71f8f30397c0309dd2e6d846d14a11f66`;
- `sapianta-domain-trading`:
  `d3038dc4ba36ffbaee9161172b4c852e8e6acbda`.

## Git state

The six modified runtime-evidence/ledger paths and three empty marker paths
predate R12B and are excluded from its scoped delta.

The scoped R12B paths are:

```text
M  aigol/runtime/human_interface_runtime_entry_service.py
M  tests/test_g31_24g_r04_r04_r07_authenticated_request_consumption.py
M  tests/test_g31_24g_r04_r04_r08c_consumed_request_certified_worker_selection.py
M  tests/test_g31_24g_r04_r04_r09b_r08c_invocation_request_compatibility.py
?? tests/test_g31_24g_r04_r04_r12b_common_entry_assignment_operational_transition.py
?? docs/governance/G31_24G_R04_R04_R12B_G31_COMMON_ENTRY_TO_ASSIGNMENT_OPERATIONAL_TRANSITION.md
```

Nothing was staged and no commit was created.

## Deterministic verdict

`G31_COMMON_ENTRY_TO_ASSIGNMENT_OPERATIONAL`

The existing Common Entry now binds the exact certified invocation request to
the existing Worker Registry projection and certified Assignment owner,
reconstructs the exact Assignment Replay, returns the exact certified Worker
as assigned, and stops before Dispatch, Invocation, Worker execution,
Provider execution, command execution, target opening, or repository
mutation.
