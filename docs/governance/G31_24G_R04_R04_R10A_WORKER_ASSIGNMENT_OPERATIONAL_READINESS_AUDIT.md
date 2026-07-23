# Generation 31-24G-R04-R04-R10A Worker Assignment Operational Readiness Audit

Status: completed bounded architectural audit; documentation only.

Date: 2026-07-23

Architectural verdict:

`G31_WORKER_ASSIGNMENT_ARCHITECTURE_BLOCKED`

First deterministic blocker:

`R09B_COMPATIBILITY_LINEAGE_OMITTED_FROM_ASSIGNMENT_REQUEST_HASH_CONTRACT`

Minimal bounded repair:

`G31_24G_R04_R04_R10B_R09B_INVOCATION_REQUEST_TO_EXISTING_WORKER_ASSIGNMENT_COMPATIBILITY_REPAIR_REQUIRED`

## Constitutional scope

This audit treats G0-G30 Platform Core and accepted G31 R05, R06, R07, R08,
R08A, R08B, R08C, R09A, and R09B as immutable certified baselines.

The accepted execution spine is:

```text
Human
  -> Common Entry
  -> Canonical Decision
  -> Mutation Authorization
  -> Authenticated Replacement Request
  -> Single-Use Authorization Consumption
  -> Certified Existing Worker Selection
  -> Certified Worker Invocation Request
  -> STOP before Worker Assignment
```

The audit asks whether the existing certified Worker Assignment architecture
can directly accept the exact R09B
`WORKER_INVOCATION_REQUEST_ARTIFACT_V1` without a new execution path,
duplicated authority, Replay discontinuity, lifecycle ambiguity, Common Entry
bypass, Worker-specific assignment policy, registry duplication, or
Governance regression.

It cannot directly accept that artifact in the current repository. The first
failure is an exact request-hash contract mismatch between the R09B request
owner and the assignment owner. No production, test, registry, certification,
Replay, adapter, or constitutional artifact was changed. No new assignment
transition was implemented. No dispatch, Provider invocation, Worker
invocation, command execution, target opening, repository mutation,
restoration, rollback, or recovery occurred. No certification generator or
live PTY was run.

## Accepted baseline

The audit began from:

- branch: `master`;
- HEAD: `5ebad5c13ad3b3d0bf4e857ac7fdb3ab90da9028`;
- HEAD subject:
  `feat(runtime): bridge R08C lineage to invocation request contract`;
- R09B verdict:
  `G31_R08C_TO_EXISTING_INVOCATION_REQUEST_COMPATIBILITY_OPERATIONAL`;
- invocation-request family:
  `WORKER_INVOCATION_REQUEST_ARTIFACT_V1`;
- typed parent lineage:
  `AUTHENTICATED_REPLACEMENT_SELECTION_LINEAGE_V1`;
- selected Worker:
  `FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER`;
- selected Worker version:
  `G8_12_EXISTING_FILE_MUTATION_IMPLEMENTATION_V1`;
- selected capability:
  `REPLACE_EXISTING_TEXT_FILE`;
- selected role:
  `WORKER_ROLE`;
- selected category:
  `WORKER`;
- selected authority profile:
  `WORKER_AUTHORIZED_TASK_ONLY`;
- selected domain:
  `NATIVE_DEVELOPMENT`.

The only initial worktree changes were the six previously declared runtime
evidence/ledger paths and three empty marker paths. Their hashes were captured
before inspection.

## Plain-language determination

The assignment architecture is not fundamentally incompatible with the R09B
lineage. Its selector, authority checks, four-stage Replay, reconstruction,
presentation, and pre-dispatch stop boundary remain generic and reusable.

The direct transition is nevertheless blocked at its first validation step.
R09B correctly added its complete typed compatibility lineage to the canonical
invocation-request hash. The assignment owner maintains a second local copy of
that hash projection and was not advanced with R09B. It recomputes a different
hash and rejects the authentic request before it reconstructs the parent
Replay or evaluates any Worker.

A later compatibility gap is also visible: the existing default in-memory
Worker projection reads only the older `g31_lineage`. If the first hash
mismatch were bypassed, the R09B artifact would take the legacy fallback and
produce a synthetic Worker identity and `WORKER_ROLE` capability instead of
preserving the exact certified selected Worker and
`REPLACE_EXISTING_TEXT_FILE`. This later gap does not replace the first
blocker, but it proves that a hash-only patch would not be an operational
assignment binding.

## Existing certified Assignment contract

### Public owner

`assign_worker_from_invocation_request` is the existing certified application
owner for the relevant Assignment stage. It accepts:

- one existing `WORKER_INVOCATION_REQUEST_ARTIFACT_V1`;
- the exact invocation-request Replay reference;
- a list of existing `WORKER_ARTIFACT_V1` candidates;
- assignment identity, actor, timestamp, and Replay destination.

It does not choose an authorization, approve execution, select a Provider,
dispatch a Worker, invoke a Worker, execute a command, or mutate a repository.

### Request validation

Before candidate evaluation, `_validate_invocation_request`:

1. invokes the assignment-local `_validate_request_artifact`;
2. reconstructs the existing invocation-request Replay;
3. requires `WORKER_INVOCATION_REQUEST_CREATED`;
4. compares request identity and request hash;
5. validates the recorded request wrapper and artifact hash.

This order makes the local hash mirror the first gate.

### Candidate validation and selection

Given a valid request, `_select_compatible_worker` is identity-generic. It
requires exactly one compatible, available `WORKER_ARTIFACT_V1` and rejects
zero or ambiguous candidates.

The existing Worker validator requires:

- immutable artifact hash;
- available state;
- Worker identity, type, version, capability, and family;
- Worker role coverage;
- exact or wildcard packet compatibility;
- allowed-output coverage;
- forbidden-operation coverage;
- Replay visibility;
- false Governance, approval, proposal, Provider, self-authorization,
  Replay-mutation, dispatch, invocation, execution, and completion authority.

No condition in this selector names the filesystem replacement Worker. No new
selector is required.

### Assignment result and stop boundary

On success, the owner creates the existing:

- `WORKER_ASSIGNMENT_EVIDENCE_ARTIFACT_V1`;
- `WORKER_ASSIGNMENT_CLASSIFICATION_ARTIFACT_V1`;
- `WORKER_ASSIGNMENT_ARTIFACT_V1`;
- `WORKER_ASSIGNMENT_RESULT_ARTIFACT_V1`.

The post-assignment boundary remains:

```text
worker_assigned = true
worker_dispatched = false
worker_invoked = false
execution_started = false
result_created = false
governance_mutated = false
replay_mutated = false
```

Assignment changes lifecycle state from `AVAILABLE` to `ASSIGNED`; it does not
perform execution.

## Exact first blocker

The R09B invocation-request owner computes `request_hash` over:

```text
base invocation-request identity and scope
  + optional g31_lineage
  + optional compatibility_lineage
```

The assignment owner recomputes it over:

```text
base invocation-request identity and scope
  + optional g31_lineage
```

It omits `compatibility_lineage`.

The accepted R09B request necessarily contains:

```text
compatibility_lineage.lineage_type =
  AUTHENTICATED_REPLACEMENT_SELECTION_LINEAGE_V1
```

and its canonical request hash necessarily covers the complete R05-R08C
lineage stored there. The assignment-local recomputation therefore cannot
equal the accepted R09B `request_hash`.

A pure, no-write hash probe using the same request fields returned:

```text
upstream_hash =
  sha256:bda9d1456f00d3e93a706b993683ad9b7b789df2590834293b86414e169eb937
assignment_hash =
  sha256:595e0c6f88036de6fa2dccc98460161faf1d77ac738165d7478138959af72452
hashes_equal = false
```

The same probe returned equality for both the legacy request and the older
`g31_lineage` request. The drift is isolated to the new accepted R09B lineage.

A second pure probe supplied an artifact whose `request_hash` and
`artifact_hash` were valid under the R09B request owner. The existing
assignment validator deterministically returned:

```text
worker assignment failed closed: invocation request hash mismatch
```

The failure occurs before:

- invocation-request Replay reconstruction by the assignment owner;
- Worker artifact projection;
- candidate selection;
- assignment evidence;
- Assignment Replay;
- dispatch or any later lifecycle owner.

This is correct fail-closed behavior for the current code, but it proves direct
operational readiness is absent.

## Downstream compatibility observation

`default_worker_registry_for_request` is the existing in-memory compatibility
projection used by Common Entry and the accepted G31-12B path. It is not a
second persistent registry.

The function currently reads only:

```text
request.g31_lineage.resource_selection_artifact
```

and validates that older selection as exact `CODEX`,
`HYBRID_PROVIDER_WORKER`, `WORKER_ROLE`, and
`WORKER_AUTHORIZED_TASK_ONLY`.

R09B intentionally stores the exact selection under:

```text
request.compatibility_lineage.resource_selection_capture
  .resource_selection_artifact
```

and has no `g31_lineage`. The current fallback would therefore derive:

```text
worker_id =
  AIGOL-WORKER-FILESYSTEM-REPLACE-EXISTING-TEXT-FILE-WORKER
capability_id = WORKER_ROLE
```

instead of:

```text
worker_id = FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER
capability_id = REPLACE_EXISTING_TEXT_FILE
```

That substitution would break certified selection identity and capability
continuity. It must not be used as a shortcut.

Repository-wide tracked-source inspection found the exact replacement Worker
in the certified unified selection registry and replacement Worker owner, but
no pre-existing exact `WORKER_ARTIFACT_V1` assignment candidate. R08B
certifies selection admission; it does not silently grant Assignment or create
an Assignment candidate.

## Replay continuity

The R09B request Replay is already suitable as the immutable Assignment
parent. Its reconstructor:

- requires the exact four-file request Replay set;
- validates ordered wrappers and all wrapper/artifact hashes;
- reconstructs the R06/R07 request and consumption;
- reconstructs the R08C Selection Replay;
- validates the unchanged R08B certification and registry;
- rebuilds and compares the typed compatibility lineage;
- returns with Assignment and all later stages false.

The existing Assignment Replay then records four ordered wrappers and validates:

- evidence-to-classification continuity;
- classification-to-assignment continuity;
- assignment-to-result continuity;
- canonical chain continuity;
- request identity and hash continuity;
- nested invocation-request Replay reconstruction;
- Worker identity and authority boundaries.

No R05-R09B event needs to be repeated, rewritten, or reauthorized. A bounded
compatibility repair can preserve the accepted request Replay as the sole
Assignment predecessor.

The current Assignment reconstructor validates the four expected wrappers but
does not independently reject unrelated extra JSON files in its Replay
directory. That is an existing accepted Assignment behavior, not the first
R10A blocker, and this audit does not alter or recertify it.

## Authority continuity

The R09B request is explicitly non-authoritative and preserves:

```text
worker_selected = true
worker_invocation_request_created = true
worker_assigned = false
worker_dispatched = false
provider_invoked = false
worker_invoked = false
execution_started = false
command_executed = false
repository_mutated = false
```

The existing Assignment owner alone may create `worker_assigned = true`. It
does not acquire authorization, selection, dispatch, invocation, command, or
mutation authority. The exact selected authority profile remains
`WORKER_AUTHORIZED_TASK_ONLY`, whose dispatch, authorization, Governance,
Provider-invocation, and Worker-invocation authority fields are false.

No duplicate authority model is required. The compatibility repair must only
validate and project already-certified evidence.

## Common Entry and Human Interface compatibility

`run_human_interface_runtime_entry` remains the public application
transition. The accepted R09B mutation continuation creates the invocation
request through its existing owner and returns immediately with
`worker_assigned = false`.

Canonical Presentation uses the existing invocation-request summary and states
that no Worker has been assigned, dispatched, invoked, or executed. AiCLI
calls Common Entry and owns no request, Worker artifact, Assignment, registry,
Replay, dispatch, invocation, command, or mutation semantics.

The existing G31-12B Common Entry path proves that the application service can
call the existing assignment owner and render the existing Assignment summary
without transferring authority to AiCLI. R10B can reuse that topology only
after exact R09B request and Worker evidence validation.

## G30 constitutional compatibility

The reusable architecture preserves:

- Human and Governance ownership of decisions and authorization;
- Platform Core ownership of application sequencing;
- Worker Layer ownership of Assignment;
- Replay ownership of reconstruction;
- thin Human Interface and AiCLI transport;
- separate selection, Assignment, dispatch, invocation, and mutation stages;
- fail-closed evidence validation;
- explicit no-execution boundaries.

The blocker is contract drift at an existing stage boundary, not a reason to
redesign Platform Core, add a parallel Assignment path, duplicate a registry,
or add Worker-specific policy.

## Minimal bounded repair

The smallest safe R10B repair is an existing-owner compatibility change:

1. establish one canonical invocation-request artifact validator/hash contract
   in the existing request owner and make Assignment reuse it, eliminating the
   stale local hash projection;
2. extend only `default_worker_registry_for_request` to recognize the existing
   typed compatibility lineage and project the reconstructed selected resource
   into the existing `WORKER_ARTIFACT_V1`;
3. derive Worker identity, version, category, role, authority profile,
   capability, domain, selection Replay, allowed outputs, forbidden
   operations, and packet compatibility from reconstructed evidence;
4. do not branch on
   `FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER`,
   `REPLACE_EXISTING_TEXT_FILE`, or another Worker-specific literal;
5. call the unchanged `assign_worker_from_invocation_request` from the existing
   R09B Common Entry continuation;
6. reconstruct both nested request Replay and existing Assignment Replay;
7. stop with Assignment true and dispatch, invocation, command, target-open,
   mutation, restoration, rollback, and recovery false.

The repair must not:

- change R05-R09B artifacts or Replay;
- modify the certified unified selection registry;
- generate or replace certification evidence;
- manufacture Assignment from `selected_resource_id` alone;
- use the legacy synthetic fallback for the R09B lineage;
- add another validator, registry, selector, Assignment owner, Replay family,
  Worker, Provider, adapter route, or execution path;
- dispatch or invoke any Worker or Provider;
- execute a command or mutate a repository.

The minimal implementation surface is expected to be:

- `worker_invocation_request_runtime.py` only if a public canonical validator
  must be exposed rather than reusing an existing public reconstruction
  result;
- `worker_assignment_runtime.py` for canonical request validation and generic
  typed-lineage Worker projection;
- `human_interface_runtime_entry_service.py` for the existing Common Entry
  transition and stop-before-dispatch aggregation;
- focused tests and one later implementation report.

No registry or certification file is required by the architectural evidence.
If exact Worker projection cannot be derived without changing the accepted
R08B registry or certification, R10B must stop rather than invent a candidate.

## Rejected shortcuts

- Omitting `compatibility_lineage` from the request hash would break R09B
  tamper evidence.
- Rehashing the accepted request under Assignment semantics would create two
  canonical identities.
- Mapping the request to `CODEX`, `CLAUDE_CODE`,
  `IMPLEMENTATION_ASSISTANCE`, or `FILESYSTEM_INSPECTION` would substitute
  Worker identity or capability.
- Using the legacy `AIGOL-WORKER-*` fallback would discard the certified
  selected identity.
- Treating `selected_resource_id` alone as a `WORKER_ARTIFACT_V1` would bypass
  role, authority, capability, Replay, availability, output, and forbidden
  operation validation.
- Calling the lower-level readiness-based `worker_runtime.assign_worker` would
  bypass the certified invocation-request Assignment owner.
- Adding a special filesystem-replacement branch would introduce
  Worker-specific Assignment policy.
- Modifying a registry or generating new certification evidence would exceed
  this audit and is unnecessary to resolve the first blocker.

## Validation

Validation was bounded to existing tests, read-only inspection, pure no-write
contract probes, and temporary pytest roots. No complete repository suite,
live PTY, certification generator, Worker, Provider, command, or mutation
workflow was run.

| Validation group | Passed | Skipped/Deselected | Failed |
|---|---:|---:|---:|
| Accepted R09B compatibility and zero-downstream regression | 13 | 0 | 0 |
| Existing invocation-request regression | 11 | 0 | 0 |
| Existing Worker Assignment regression | 14 | 0 | 0 |
| Existing G31-12B request-to-Assignment regression, live downstream test excluded | 13 | 1 deselected | 0 |
| R05-R08C certified-spine regression | 124 | 0 | 0 |
| Common Entry, Human Interface, operational-entry, and layer boundaries | 25 | 0 | 0 |
| Governance conformance tests | 5 | 0 | 0 |

Additional deterministic results:

- R09B-versus-Assignment request-hash probe:
  **1 mismatch reproduced, 0 unexpected results**;
- legacy and older G31 hash compatibility probe:
  **2 equal cases, 0 unexpected results**;
- assignment-local validation probe:
  **1 expected fail-closed result, 0 Assignment artifacts**;
- targeted `py_compile`: passed for the request, Assignment, Common Entry, and
  relevant test modules;
- parent `git diff --check`: passed before this report;
- all three nested repository `git diff --check` checks: passed;
- complete repository suite: not run for this audit-only generation;
- live PTY: not run;
- certification generation: not run;
- dispatch, Worker/Provider invocation, command execution, and repository
  mutation: not run.

Existing Assignment tests write only their established temporary pytest Replay
fixtures. They do not dispatch, invoke, execute, or mutate the repository.

## Governance result

The deterministic read-only conformance engine remains:

`PARTIALLY_CONFORMANT`

- checks passed: 18;
- checks failed: 2;
- critical violations: 0;
- deterministic: true;
- fail-closed: true;
- read-only: true;
- report hash:
  `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea`.

The two known hook findings remain visible and unchanged:

- the root expected and installed pre-commit hooks are missing;
- the system pre-commit hook lacks `promotion_gate_v02` and
  `check_layer_freeze`.

R10A neither repairs nor reinterprets them.

## Protected and nested state

The protected paths retained their pre-audit SHA-256 values:

| Protected path | SHA-256 |
|---|---|
| `diagnostic_evidence.json` | `a626a69a8020bc730876119c52701a94de9ab6e4772cc64c1f5d017296650203` |
| `governed_return.json` | `e82f47c0c13678725993b21e2af2e0437edccaed324f861a7b58e77d7f8e787d` |
| `lineage.json` | `07b95505521e70f51cdddecc1057fd3a208b198445693c9a8da1e996df5799dd` |
| `provider_stderr.txt` | `d47a06d59aba2814c3fb7460049fc2ccbfc834196c956d6c6558e8be8b079e24` |
| `provider_stdout.txt` | `a73a499e2e9133c03d7babfd5c4dec7967f31e2bfb354ea9dd41df0a15c08cb3` |
| `governed_returns.jsonl` | `dbc7b63f2a17c50c43bbb4fde4f44c1dbae8d25d550fb6b4d4daa14e17126161` |
| each protected marker | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

The nested repositories remained clean at their accepted commits:

- `sapianta-domain-credit`:
  `8615e1e290471a67e4e764c6ab2138340bc7936f`;
- `sapianta_system`:
  `3183bab71f8f30397c0309dd2e6d846d14a11f66`;
- `sapianta-domain-trading`:
  `d3038dc4ba36ffbaee9161172b4c852e8e6acbda`.

No nested repository was modified.

## Change size and Git state

Scoped R10A delta:

| Category | Files | Insertions | Deletions |
|---|---:|---:|---:|
| Production | 0 | 0 | 0 |
| Tests | 0 | 0 | 0 |
| Registries and certification evidence | 0 | 0 | 0 |
| Documentation | 1 new | 574 | 0 |

No production symbol was added or modified. No helper logic was copied. No
artifact, registry entry, Assignment Replay, certification evidence, or
runtime execution state was created by the R10A change.

Nothing was staged and no commit was created. The six modified runtime
evidence paths and three empty marker paths predate R10A and are excluded from
its scoped delta.

## Architectural verdict

`G31_WORKER_ASSIGNMENT_ARCHITECTURE_BLOCKED`

The certified Assignment owner cannot directly accept the exact R09B
invocation-request artifact because its local canonical hash contract omits
the required typed compatibility lineage. The underlying selector, authority,
Replay, presentation, and Common Entry topology remain reusable, so the
blocker is bounded compatibility drift rather than architectural redesign.

First deterministic blocker:

`R09B_COMPATIBILITY_LINEAGE_OMITTED_FROM_ASSIGNMENT_REQUEST_HASH_CONTRACT`

Minimal bounded repair:

`G31_24G_R04_R04_R10B_R09B_INVOCATION_REQUEST_TO_EXISTING_WORKER_ASSIGNMENT_COMPATIBILITY_REPAIR_REQUIRED`
