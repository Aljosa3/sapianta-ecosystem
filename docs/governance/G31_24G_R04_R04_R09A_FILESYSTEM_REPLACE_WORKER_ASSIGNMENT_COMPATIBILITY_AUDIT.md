# Generation 31-24G-R04-R04-R09A Filesystem Replace Worker Assignment Compatibility Audit

Status: completed bounded architectural audit; documentation only.

Date: 2026-07-22

Architectural verdict:

`G31_FILESYSTEM_REPLACE_WORKER_ASSIGNMENT_ARCHITECTURE_BLOCKED`

First deterministic blocker:

`R08C_AUTHENTICATED_REPLACEMENT_LINEAGE_NOT_ACCEPTED_BY_CERTIFIED_WORKER_INVOCATION_REQUEST_CONTRACT`

## Constitutional scope

This audit treats G0-G30 and accepted G31 R05, R06, R07, R08, R08A, R08B,
and R08C as immutable certified baselines. The accepted execution spine is:

```text
Human
  -> Common Entry
  -> Canonical Decision
  -> Mutation Authorization
  -> Authenticated Replacement Request
  -> Single-Use Authorization Consumption
  -> Certified Existing Worker Selection
  -> Selection Replay reconstruction
  -> STOP before assignment
```

The audit asks whether the existing certified Worker-assignment architecture
can accept that exact selected Worker without adding a parallel execution
path, duplicating authority, weakening Replay, bypassing Common Entry, adding
Worker-specific assignment policy, duplicating a registry, or changing G30
constitutional ownership.

It cannot currently do so. The assignment selector and assignment Replay are
generic and reusable, but their mandatory certified predecessor is an existing
`WORKER_INVOCATION_REQUEST_ARTIFACT_V1`. The only public constructor and G31
selection bridge for that artifact reject the R05-R08C mutation lineage before
assignment can begin.

No production, runtime, test, registry, certification, Replay, adapter, or
constitutional artifact was changed. No operational R09A assignment,
dispatch, Provider or Worker invocation, execution, command, target opening,
repository mutation, restoration, rollback, or recovery was performed. No
runtime certification artifact was generated and no live PTY was run.

## Accepted baseline

The audit began from:

- branch: `master`;
- HEAD: `60f3485c0265b6e0f9fedea464e023a0b0bd0997`;
- HEAD subject:
  `feat(runtime): bind consumed replacement request to certified Worker selection`;
- R08C verdict:
  `G31_CONSUMED_REPLACEMENT_REQUEST_TO_CERTIFIED_EXISTING_WORKER_SELECTION_BINDING_OPERATIONAL`;
- selected Worker:
  `FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER`;
- selected Worker version:
  `G8_12_EXISTING_FILE_MUTATION_IMPLEMENTATION_V1`;
- selected capability: `REPLACE_EXISTING_TEXT_FILE`;
- selected role: `WORKER_ROLE`;
- selected category: `WORKER`;
- selected authority profile: `WORKER_AUTHORIZED_TASK_ONLY`;
- selected domain: `NATIVE_DEVELOPMENT`;
- certified registry hash:
  `sha256:74357af9a2ba666d73241381e5a4c24ac7687e41b67efe6746cb86d3ac6e7d64`;
- checked selection-certification report hash:
  `sha256:03cbf0fc4e8ae562ffe25235aff1c7a6fbd559c23fc8c4fad48e15a1c56b1b45`.

The only pre-audit worktree changes were the six previously declared runtime
evidence/ledger paths and three empty marker paths. Their exact hashes were
captured before inspection.

## Existing certified assignment architecture

The relevant certified lifecycle is:

```text
EXECUTION_AUTHORIZED
  -> create_worker_invocation_request
  -> WORKER_INVOCATION_REQUEST_CREATED
  -> assign_worker_from_invocation_request
  -> WORKER_ASSIGNED
  -> reconstruct_worker_assignment_runtime_replay
  -> stop before dispatch
```

Checked governance evidence reports:

- `AIGOL_WORKER_INVOCATION_REQUEST_RUNTIME_STATUS = CERTIFIED`;
- `AIGOL_WORKER_ASSIGNMENT_RUNTIME_STATUS = CERTIFIED`.

The existing certification covers invocation requests reconstructed from an
`EXECUTION_AUTHORIZATION_ARTIFACT_V1` and an execution-ready packet lineage.
It covers filesystem, monitoring, and trading flows in that older generic
model. It does not certify the exact R05 mutation authorization, R06/R07
authenticated replacement request and consumption, or the R08C filesystem-
replacement selection as an invocation-request input.

The word `filesystem` in the older acceptance evidence refers to the generic
filesystem Worker flow and, in the optional ERR path, the
`MOCK_FILESYSTEM_WORKER_ID / file_write` pair. It is not evidence for
`FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER / REPLACE_EXISTING_TEXT_FILE`.

## Contract inventory

### Worker invocation request

`create_worker_invocation_request` is the sole relevant public request owner.
It:

- requires an execution-authorization Replay reference;
- reconstructs `EXECUTION_AUTHORIZATION_ARTIFACT_V1`;
- requires `EXECUTION_AUTHORIZED`, unrevoked and unexpired authorization;
- reconstructs an existing execution-ready candidate, packet, validation, and
  ready-status chain;
- requires an `EXECUTION_PACKET_ARTIFACT_V1` identity and hash;
- optionally consumes a G31 resource-selection Replay through
  `_load_g31_selection_binding`;
- creates the existing four-artifact request Replay;
- stops before assignment.

`reconstruct_worker_invocation_request_replay` repeats the authorization,
packet, request, and optional G31-selection reconstruction. The assignment
owner therefore cannot accept a handcrafted request that was not produced and
reconstructed through this certified path.

### Current G31 selection bridge

The optional `_load_g31_selection_binding` bridge is not identity-generic. It
calls `reconstruct_authorized_grounded_worker_selection`, which is fixed to
the G31-10 execution-authorization lineage and then requires:

```text
selected_resource_id = CODEX
selected_resource_category = HYBRID_PROVIDER_WORKER
selected_role_type = WORKER_ROLE
selected_authority_profile = WORKER_AUTHORIZED_TASK_ONLY
required_capability = IMPLEMENTATION_ASSISTANCE
context_hash = execution_authorization artifact hash
```

The request artifact validator independently repeats the `CODEX` and
`HYBRID_PROVIDER_WORKER` requirements. This is accepted G31-12B behavior for
the earlier implementation Worker and was not changed by R08C.

R08C instead supplies:

```text
selected_resource_id = FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER
selected_resource_category = WORKER
required_capability = REPLACE_EXISTING_TEXT_FILE
context_hash = immutable R07 consumption/request selection-context hash
parent authorization = R05 mutation authorization record and Replay
parent work packet = R06/R07 authenticated replacement request and consumption
```

Those are exact, deliberate differences, not aliases.

### Worker artifact projection

`default_worker_registry_for_request` is the existing in-memory
`WORKER_ARTIFACT_V1` compatibility projection. The assignment selector later
consumes the resulting artifacts; the function is not a second persistent
resource registry.

For a G31-selected resource, however, it currently requires the same exact
`CODEX / HYBRID_PROVIDER_WORKER` selection and rejects R08C evidence. The
repository contains no existing `WORKER_ARTIFACT_V1` for the exact replacement
Worker carrying all mandatory assignment fields:

- exact Worker identity, type, version, and family;
- exact capability;
- Worker role;
- compatible invocation request/execution packet;
- allowed outputs;
- forbidden operations;
- availability;
- false Governance, approval, proposal, Provider, self-authorization, Replay-
  mutation, dispatch, invocation, execution, and completion authority.

R08B certifies selection registration, not assignment registration or a
`WORKER_ARTIFACT_V1` instance.

### Worker assignment

`assign_worker_from_invocation_request` itself is identity-generic. Given one
valid reconstructed invocation request and one valid compatible Worker
artifact, it already validates:

- append-only assignment destination;
- duplicate assignment rejection;
- request identity, artifact hash, and native Replay;
- Worker identity and artifact hash;
- Worker availability;
- Worker family and role;
- execution-packet compatibility;
- allowed-output coverage;
- forbidden-operation coverage;
- false authority fields;
- no-match and ambiguity behavior.

It creates the existing assignment evidence, classification, assignment, and
result artifacts and stops before dispatch. No replacement-Worker-specific
condition exists in this selector, and none is needed.

### Assignment Replay and presentation

`reconstruct_worker_assignment_runtime_replay` validates the four ordered
assignment wrappers, artifact and wrapper hashes, request lineage, Worker
identity, assignment identity, canonical chain, optional ERR evidence, and
post-assignment stop flags. It then reconstructs the nested invocation-request
Replay.

`render_worker_assignment_summary` is Worker-identity-neutral and truthfully
states that no Worker has been dispatched, invoked, or executed. Common Entry
already owns the earlier G31 request/assignment continuation and presentation
for the CODEX lineage. AiCLI transports that state and owns no assignment
semantics.

## Compatibility matrix

| Transition or contract | Classification | Deterministic finding |
|---|---|---|
| R08C Selection Replay reconstruction | `SUPPORTED` | Exact selection and R05-R08C parent context reconstruct through accepted R08C contracts |
| R05 mutation authorization -> invocation-request authorization input | `INCOMPATIBLE` | Existing request owner requires `EXECUTION_AUTHORIZATION_ARTIFACT_V1`; R05 owns a distinct mutation-authorization record and actor-bound Replay |
| R06/R07 authenticated request -> execution-packet input | `INCOMPATIBLE` | Existing request owner requires an execution-ready `EXECUTION_PACKET_ARTIFACT_V1`; R06/R07 provide a distinct authenticated replacement request and consumption chain |
| R08C selection -> existing G31 request selection bridge | `INCOMPATIBLE` | Bridge and reconstructor require CODEX, hybrid category, implementation capability, and G31-10 context hash |
| Existing request artifact family -> exact R08C lineage | `NOT_CERTIFIED` | Current certified constructor and reconstructor have no explicit authenticated-replacement lineage kind |
| R08C selection -> `WORKER_ARTIFACT_V1` | `ABSENT` | Existing projection is hard-coded to CODEX/hybrid; no exact compatible Worker artifact exists |
| Valid invocation request -> assignment selector | `SUPPORTED` | Generic existing selector validates exact Worker compatibility and ambiguity without invoking it |
| Assignment -> assignment Replay | `SUPPORTED` | Existing four-step Replay is identity-generic and nests request reconstruction |
| Assignment -> Canonical Presentation | `SUPPORTED` | Existing presentation is Worker-neutral and stops before dispatch |
| Common Entry ownership | `SUPPORTED_WITH_MISSING_EDGE` | Common Entry owns all existing transitions, but the R08C branch deliberately stops at selection |
| G30 constitutional authority | `SUPPORTED` | Human/Governance authorization, Platform Core orchestration, Replay ownership, and thin-adapter neutrality remain intact |

The first non-supported edge is the R08C mutation lineage to the existing
certified invocation-request contract. The missing exact Worker artifact is a
second downstream incompatibility and is not the first blocker.

## First deterministic blocker

The first exact blocker is:

`R08C_AUTHENTICATED_REPLACEMENT_LINEAGE_NOT_ACCEPTED_BY_CERTIFIED_WORKER_INVOCATION_REQUEST_CONTRACT`

It is proven by the existing public call graph and validators:

1. assignment cannot begin without a reconstructed
   `WORKER_INVOCATION_REQUEST_ARTIFACT_V1`;
2. its sole public constructor first calls the execution-authorization
   reconstructor;
3. that constructor then requires an execution-ready candidate and
   `EXECUTION_PACKET_ARTIFACT_V1` lineage;
4. its only G31 selection loader calls the G31-10/CODEX reconstructor;
5. both the loader and request validator reject the exact R08C Worker,
   category, capability, and context;
6. R05-R08C intentionally contain a mutation authorization, authenticated
   replacement request, single-use consumption, and exact replacement-Worker
   selection instead of those older artifacts.

Calling `assign_worker_from_invocation_request` directly would bypass the
certified mandatory predecessor and fail its native request/Replay validation.
Relabeling an authenticated replacement request as an execution packet would
create lifecycle ambiguity. Issuing another execution authorization would
duplicate authority after R07 has consumed the exact mutation authorization.

The existing architecture therefore cannot currently accept the exact R08C
selection under the audit constraints.

## Rejected shortcuts

- Mapping the selected Worker to `CODEX` or `CLAUDE_CODE` changes identity.
- Mapping `REPLACE_EXISTING_TEXT_FILE` to `IMPLEMENTATION_ASSISTANCE`,
  `FILESYSTEM_INSPECTION`, or generic `file_write` broadens or changes the
  certified operation.
- Using `MOCK_FILESYSTEM_WORKER_ID` through ERR reruns selection and substitutes
  a different Worker and capability.
- Calling assignment with a fabricated request bypasses the certified request
  and nested Replay owner.
- Treating the R07 request as an `EXECUTION_PACKET_ARTIFACT_V1` without an
  explicit versioned contract silently changes artifact semantics.
- Creating another execution authorization after R07 consumption duplicates
  authority and changes the accepted decision spine.
- Invoking the replacement Worker directly bypasses assignment and Common
  Entry.
- Adding a replacement-specific condition inside `_select_compatible_worker`
  duplicates selection policy and is unnecessary.
- Adding another Worker registry would duplicate the accepted R08B registry.

## Minimal bounded repair

The assignment selector, assignment artifact families, assignment Replay, and
presentation do not require redesign. The smallest constitutionally honest
repair must occur before assignment in the existing invocation-request and
Worker-artifact compatibility owners.

A later bounded generation must:

1. explicitly version and certify an authenticated-replacement lineage mode
   in the existing Worker invocation-request owner;
2. consume only reconstructed R05 authorization, R06/R07 request and
   consumption, R08B registry/certification, and R08C selection evidence;
3. give that lineage an explicit type rather than relabeling the R07 request as
   the older execution packet or issuing another authorization;
4. preserve request, authorization, consumption, selection, context, registry,
   certification, target, preimage, replacement content, and mode identities;
5. generalize the existing G31 selection validator so expected identity,
   category, version, role, profile, domain, and capability come from the
   checked certified selection, not CODEX literals;
6. project exactly one compatible `WORKER_ARTIFACT_V1` from that validated
   selection and authenticated request, without a second registry or Worker-
   specific assignment rule;
7. reconstruct the resulting invocation-request Replay and stop before
   assignment;
8. undergo bounded request-contract certification before any R09 assignment
   binding is attempted.

Only after that repair is accepted may a separate assignment binding call the
unchanged `assign_worker_from_invocation_request`, reconstruct existing
assignment Replay, present the result through Common Entry, and stop before
dispatch.

This sequencing prevents a request-contract compatibility change from being
bundled with assignment authority.

## Replay continuity assessment

Each existing chain reconstructs within its certified family:

- R05-R08C reconstruct mutation authorization, authenticated request,
  consumption, certified selection, and Selection Replay;
- the existing request runtime reconstructs execution-authorization/packet-
  based invocation requests;
- the existing assignment runtime reconstructs assignment plus its nested
  invocation request.

There is no accepted immutable parent-child binding between the first and
second chains for the exact replacement Worker. Consequently, no complete
R08C-to-assignment Replay claim can be made. The fail-closed stop at selection
is the truthful current state.

No existing Replay was changed, reordered, duplicated, or supplemented during
this audit.

## Authority continuity and stop state

The accepted state remains:

```text
worker_selected = true
worker_assigned = false
worker_dispatched = false
provider_invoked = false
worker_invoked = false
execution_requested = false
command_executed = false
target_opened = false
repository_mutated = false
restoration_started = false
rollback_started = false
recovery_started = false
```

The existing assignment runtime would set only `worker_assigned = true` for a
valid compatible request and Worker artifact while retaining dispatch,
invocation, execution, result, Governance mutation, and Replay mutation as
false. That later authority transition remains unreachable from R08C today.

Human authority and Governance authorization are not transferred to the
selected Worker. Common Entry remains the application owner. AiCLI and the
in-memory adapter remain transport and presentation surfaces only.

## G30 and Human Interface compatibility

The proposed repair does not require a new Human Interface, router, selector,
registry, assignment owner, Replay subsystem, or adapter path. Existing Common
Entry aggregation and `render_worker_assignment_summary` are sufficient after
a valid request/assignment exists.

The present blocker is correctly below Platform Core orchestration and above
assignment. G30 constitutional ownership remains unchanged:

- Human/Governance owns authorization;
- Platform Core owns application composition;
- the invocation-request runtime owns request semantics;
- the assignment runtime owns assignment;
- Replay owns reconstruction;
- adapters own no lifecycle decision.

## Read-only validation

Validation used existing tests and temporary pytest roots. Existing assignment
tests create only their already-certified temporary Replay fixtures; no R09A
assignment path, Worker execution, Provider execution, command, or repository
mutation was introduced.

| Validation group | Passed | Skipped/Deselected | Failed |
|---|---:|---:|---:|
| Accepted R08C selection and fail-closed evidence | 35 | 0 | 0 |
| Existing invocation-request, assignment, and Worker runtimes | 48 | 0 | 0 |
| Existing G31-12B request/assignment compatibility, downstream AiCLI dispatch test excluded | 13 | 1 deselected | 0 |
| Existing G31 selection, unified selector, and Common Entry adapter evidence | 33 | 0 | 0 |
| G30/Human Interface and architecture/import boundaries | 49 | 0 | 0 |
| Governance tests | 5 | 0 | 0 |

Targeted `py_compile` passed for the invocation-request, assignment, Worker,
R08C binding, and Common Entry modules. Parent `git diff --check` and all three
nested repository `git diff --check` checks passed.

The complete repository suite was not run. R08C's accepted baseline already
records one clean complete-suite run of **6753 passed, 4 skipped, 0 failed**,
and this audit changes no runtime or test behavior. No live PTY, assignment
continuation, dispatch, invocation, execution, mutation workflow, or
certification generator was run.

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

The known root and system pre-commit hook findings remain visible and
unchanged. This audit neither repairs nor reinterprets them.

## Protected and nested state

All protected SHA-256 values equal the pre-audit baseline:

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

## Change size and Git state

R09A changes exactly one governance report:

- production: 0 files, 0 insertions, 0 deletions;
- tests: 0 files, 0 insertions, 0 deletions;
- registry/certification evidence: 0 files, 0 insertions, 0 deletions;
- documentation: 1 new report, 498 insertions, 0 deletions.

No command below was executed:

```bash
git add docs/governance/G31_24G_R04_R04_R09A_FILESYSTEM_REPLACE_WORKER_ASSIGNMENT_COMPATIBILITY_AUDIT.md
git commit -m "docs(governance): audit filesystem replacement Worker assignment compatibility"
```

The six modified runtime-evidence/ledger paths and three marker paths predate
R09A and are not part of its documentation-only delta. Nothing is staged and
no commit was created.

## Architectural verdict

`G31_FILESYSTEM_REPLACE_WORKER_ASSIGNMENT_ARCHITECTURE_BLOCKED`

The certified assignment selector is reusable, but the complete existing
assignment architecture cannot accept the exact R08C selected Worker. Its
mandatory invocation-request predecessor rejects the mutation authorization,
authenticated request/consumption, replacement Worker identity/category,
replacement capability, and R08C context before assignment.

First deterministic blocker:

`R08C_AUTHENTICATED_REPLACEMENT_LINEAGE_NOT_ACCEPTED_BY_CERTIFIED_WORKER_INVOCATION_REQUEST_CONTRACT`

The minimal repair is a separately governed, explicitly versioned, certified
R08C-to-existing-invocation-request compatibility transition that stops before
assignment. R09A stops at this architectural verdict.
