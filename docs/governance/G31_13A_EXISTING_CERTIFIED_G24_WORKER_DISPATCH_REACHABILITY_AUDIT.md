# Generation 31-13A — Existing Certified G24 Worker Dispatch Reachability Audit

Status: completed `AUDIT_ONLY`; no runtime behavior changed.

Date: 2026-07-16

Audit verdict:

`EXISTING_G24_WORKER_DISPATCH_REUSABLE_DIRECT_BINDING_REQUIRED`

Next reachability state:

`G31_12B_TO_EXISTING_G24_WORKER_DISPATCH_DIRECT_BINDING_READY`

## Constitutional scope

This audit treats Generation 30, committed G31-02 through G31-12B, G31-11A,
G31-R01, and G31-12A as immutable accepted baselines.

The audit changed no production code, test, schema, artifact family, dispatch
policy, Governance contract, Replay contract, CLI, or Human Interface
semantics. The only repository change is this report.

No dispatch, Provider invocation, Worker invocation, command execution, or
repository mutation was performed.

## Plain-language conclusion

The certified G24 Worker-dispatch runtime already accepts the exact canonical
artifact family produced by G31-12B. Its existing assignment-lineage validator
successfully reconstructs the G31-12B assignment, request, G31 authorization,
selection, registry, certification, Project Objective, grounded repository
scope, and Replay lineage.

The reference AiCLI currently stops after assignment and does not import or
call the dispatch constructor. The first missing transition is therefore one
direct existing-function call:

```text
aicli._record_contextual_execution_decision
  -> dispatch_assigned_worker
```

No compatibility adapter, new authorization artifact, new dispatcher, new
artifact family, or new production module is required.

## Certified G24 dispatch architecture

The certified lifecycle is:

```text
WORKER_ASSIGNMENT_ARTIFACT_V1
  + assignment Replay
  -> assignment/request/authorization lineage reconstruction
  -> dispatch eligibility classification
  -> WORKER_DISPATCH_EVIDENCE_ARTIFACT_V1
  -> WORKER_DISPATCH_CLASSIFICATION_ARTIFACT_V1
  -> WORKER_DISPATCH_ARTIFACT_V1
  -> WORKER_DISPATCH_RESULT_ARTIFACT_V1
  -> stop before Worker invocation
```

The runtime is a delivery-evidence boundary. It does not run the Worker or
perform transport, command, execution, result, or mutation work.

Certification evidence declares:

`AIGOL_WORKER_DISPATCH_RUNTIME_STATUS = CERTIFIED`

## Exact contract inventory

### Entry and discovery

| Contract | File | Input | Output | Caller | Authority |
|---|---|---|---|---|---|
| `detect_domain_worker_dispatch_entry_intent` | `aigol/runtime/worker_dispatch_runtime.py` | narrow domain dispatch prompt | non-authoritative entry classification | legacy interactive AiGOL CLI | detection only |
| `find_latest_domain_worker_assignment` | same | session root and domain | latest valid undispatched assignment reference | legacy domain lifecycle | read-only discovery |

The G31 direct path does not need either contract because it already holds the
exact assignment capture returned in the same continuation.

### Dispatch constructor

Public symbol:

`dispatch_assigned_worker`

Canonical input:

- `worker_dispatch_id`;
- `WORKER_ASSIGNMENT_ARTIFACT_V1`;
- assignment Replay reference;
- `dispatched_by`;
- `dispatched_at`;
- append-only dispatch Replay destination.

Canonical output:

- dispatch evidence;
- dispatch classification;
- `WORKER_DISPATCH_ARTIFACT_V1`;
- dispatch result;
- capture and Replay reference.

Authority owner: certified G24 Worker-dispatch runtime.

Replay owner: existing append-only Worker-dispatch Replay.

### Validators

Existing validators include:

- `_load_assignment_lineage`;
- `_validate_assignment_artifact`;
- `_assignment_authority_continuity`;
- `_validate_dispatch_artifact`;
- artifact and wrapper hash verification;
- Replay ordering and chain validation;
- `_worker_assignment_already_dispatched` for domain discovery;
- append-only replay-path enforcement in `_ensure_replay_available`.

The exact G31-12B assignment passed `_load_assignment_lineage` without
projection. All seven checks were true:

```text
assignment_lineage = true
invocation_request_lineage = true
authorization_lineage = true
execution_packet_lineage = true
chain_continuity = true
replay_continuity = true
authority_continuity = true
```

### Replay reconstruction

Public symbol:

`reconstruct_worker_dispatch_replay`

It reconstructs the four ordered dispatch wrappers, validates hashes and
chain identity, then reloads the assignment lineage. Because the committed
G31-12B assignment reconstructor invokes the full request reconstructor, the
dispatch replay transitively validates complete G31 lineage.

### Presentation

Public symbol:

`render_worker_dispatch_summary`

It presents dispatch status, dispatch and assignment references, Worker
identity, Replay reference, and the explicit statement:

```text
No Worker has been invoked, executed, or produced results.
```

### Existing callers

Existing callers prove the public contract is operational:

- legacy interactive flows in `aigol/cli/aigol_cli.py`;
- `_continue_worker_request_to_replay_certification`;
- domain approval/resume continuations;
- `g5_pgsp_worker_runtime_orchestration.py`;
- certified focused and acceptance fixtures.

The reference `aigol/cli/aicli.py` is not currently a caller.

### Dispatch-to-invocation boundary

Worker invocation is a separate public runtime:

`invoke_dispatched_worker`

in `aigol/runtime/worker_invocation_runtime.py`. It consumes the dispatch
artifact and dispatch Replay only after dispatch has completed. The dispatch
module neither imports nor calls this function.

### Certification evidence

Canonical evidence inspected:

- `governance/AIGOL_WORKER_DISPATCH_RUNTIME_V1.md`;
- `governance/AIGOL_WORKER_DISPATCH_RUNTIME_ACCEPTANCE_EVIDENCE.json`;
- `governance/AIGOL_WORKER_DISPATCH_RUNTIME_CERTIFICATION.json`;
- `tests/test_worker_dispatch_runtime_v1.py`.

The certification records 12 focused passing scenarios and explicitly
excludes Worker invocation, execution, result creation, code generation,
planned-output creation, approval creation, governance mutation, and Replay
mutation.

## Compatibility matrix

| Required input or evidence | Classification | Deterministic evidence |
|---|---|---|
| Session identity | `AVAILABLE_BUT_NOT_BOUND` | Encoded in same-session Replay paths and caller context; G24 artifact has no separate session field. |
| Original human goal | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Preserved inside G31 authorization scope reconstructed through request Replay. |
| Project Objective | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Bound by hash in G31 authorization scope and nested request Replay. |
| Approved Durable Governed Work | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Present in authorization scope and upstream lineage. |
| Grounded Worker request | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Exact identity/hash preserved through authorization and request reconstruction. |
| Execution summary | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Validated by execution-authorization Replay. |
| Human confirmation | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Validated by distinct decision and authorization Replay. |
| Authorization request | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Reconstructed transitively from assignment -> request -> authorization. |
| Authorization decision | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Same nested authorization Replay. |
| Execution-authorization artifact | `DIRECTLY_COMPATIBLE` | Assignment binds authorization reference/hash; dispatch checks authorization lineage. |
| G31-11B selection artifact | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Request Replay invokes the public authorized-selection reconstructor. |
| Registry hash | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Bound inside request G31 lineage and revalidated. |
| Worker-selection certification hash | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Bound and revalidated with selection Replay. |
| CODEX identity | `DIRECTLY_COMPATIBLE` | Assignment and dispatch input contain `worker_id = CODEX`. |
| CODEX version | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Available in nested selection/Worker evidence; G24 dispatch does not duplicate version. |
| `HYBRID_PROVIDER_WORKER` category | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Nested selection reconstruction requires exact category. |
| `WORKER_ROLE` | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Selection reconstruction validates it; assignment carries the concrete Worker role. |
| `WORKER_AUTHORIZED_TASK_ONLY` profile | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Required by nested selection reconstruction. |
| Invocation-request identity/hash | `DIRECTLY_COMPATIBLE` | Assignment artifact contains both. |
| Invocation-request Replay | `DIRECTLY_COMPATIBLE` | Assignment evidence contains the reference; dispatch reconstructs it. |
| Extended Worker artifact | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Assignment binds Worker identity/hash and compatibility result; dispatch consumes assignment evidence rather than the source Worker artifact. |
| Worker availability | `DIRECTLY_COMPATIBLE` | Assignment must report `worker_state_after = ASSIGNED`. |
| Assignment identity/hash/status | `DIRECTLY_COMPATIBLE` | Exact canonical dispatch input. |
| Assignment Replay | `DIRECTLY_COMPATIBLE` | Exact second dispatch input. |
| Workspace | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Preserved in G31 authorization scope and reconstructed upstream evidence. |
| Source paths | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Preserved in authorization scope and request allowed outputs. |
| Focused-test paths | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Preserved in grounded scope. |
| Symbols | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Preserved in grounded scope and target evidence. |
| Repository evidence hashes | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Revalidated by G31 nested reconstruction. |
| Mutation layers | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Preserved in exact authorization scope. |
| Validation requirements | `DIRECTLY_COMPATIBLE` | Assignment carries them and dispatch copies them unchanged. |
| Allowed outputs | `DIRECTLY_COMPATIBLE` | Assignment carries them and dispatch copies them unchanged. |
| Forbidden operations | `DIRECTLY_COMPATIBLE` | Assignment carries them and dispatch preserves them unchanged. |
| Dispatch authorization | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Certified G24 dispatch derives eligibility from assignment plus exact authorization/request Replay; it accepts no separate dispatch-authorization artifact. |
| Dispatch target | `DIRECTLY_COMPATIBLE` | Assigned Worker identity is CODEX. |
| Live transport identity | `ABSENT_BY_DESIGN` | G24 dispatch records delivery evidence only; no external transport is performed. |
| Dispatch Replay destination | `DIRECTLY_COMPATIBLE` | Existing append-only Replay contract; caller supplies deterministic same-session path. |
| Dispatch stop boundaries | `DIRECTLY_COMPATIBLE` | Existing artifact reports dispatched true and invocation/execution/result/mutation false. |

No field requires a new compatibility artifact or adapter.

## Dispatch-authorization assessment

The certified G24 `dispatch_assigned_worker` contract does not accept a
separate dispatch-authorization artifact. Its authorization contract is the
reconstructed chain:

```text
execution authorization
  -> invocation request
  -> Worker assignment
  -> dispatch eligibility
```

The exact G31-10 authorization reference and hash are present in the G31-12B
assignment and validated during dispatch lineage loading. Repository evidence
therefore classifies dispatch authorization as deterministically derived
through the existing public lineage contracts.

The reference AiCLI field `authorization_dispatch_blocked = True` is the
current operational stop marker. It is not a canonical authorization artifact
consumed by G24 dispatch. A later direct binding must update presentation state
only after `WORKER_DISPATCHED`; it must not create another human confirmation
or authorization system.

The G31 packet preserves `DISPATCH_WORKER` among forbidden operations. Source
behavior shows that G24 treats the list as downstream Worker-scope evidence:
it copies the list into the dispatch artifact while Platform Governance records
the delivery transition. This is an inference from the certified constructor
and its validation policy. It does not grant CODEX authority to dispatch itself
or invoke anything.

Adjacent MOC and live-Provider dispatch authorizations use different artifact
families, products, and authority models. They are not compatible projections
for this Worker-assignment lifecycle and must not be introduced here.

## Dispatch versus invocation

The existing G24 dispatch operation:

- records one assigned Worker delivery transition;
- creates immutable dispatch evidence and Replay;
- sets `worker_dispatched = true`;
- does not call Worker invocation;
- does not activate Provider semantics;
- does not execute a command;
- does not execute the Worker;
- does not create results;
- does not mutate a repository or governance;
- does not mutate existing Replay.

Successful dispatch stops at:

```text
worker_selected = true
worker_assigned = true
worker_dispatched = true
provider_invoked = false
worker_invoked = false
command_executed = false
repository_mutated = false
```

Actual Worker invocation is owned separately by
`invoke_dispatched_worker` and is outside G31-13B scope.

## Hybrid-role separation

The nested selection validator requires:

```text
resource_id = CODEX
resource_category = HYBRID_PROVIDER_WORKER
selected_role_type = WORKER_ROLE
authority_profile = WORKER_AUTHORIZED_TASK_ONLY
provider_authority = false
provider_invoked = false
```

Dispatch consumes the assignment produced from that validated selection. It
does not select a Provider, call a Provider runtime, or reinterpret the hybrid
category. Provider-role or authority substitution invalidates nested request
Replay before dispatch eligibility is accepted.

## Current operational reachability

Current reference lifecycle:

```text
G31-10 authorization
  -> G31-11B CODEX/WORKER_ROLE selection
  -> G31-12B invocation request
  -> G31-12B assignment
  -> stop
```

Current exact caller:

`aigol.cli.aicli._record_contextual_execution_decision`

Existing exact callee:

`aigol.runtime.worker_dispatch_runtime.dispatch_assigned_worker`

The caller currently does not import or invoke the callee. No dispatch capture,
artifact, Replay, or presentation is created.

## Exact first unbound transition

`G31_12B_ASSIGNMENT_TO_EXISTING_G24_DISPATCH_CALL_ABSENT`

This is a direct lifecycle call gap. Artifact, Replay, authority, and
presentation contracts already exist and are compatible.

## Fail-closed audit

Existing contracts reject:

- missing, malformed, non-assigned, or hash-invalid assignment artifacts;
- mismatched assignment identity or hash;
- reordered or substituted assignment Replay;
- changed invocation request or request Replay;
- changed authorization or execution packet identity/hash;
- broken chain or authority continuity;
- Worker identity drift;
- unavailable Worker state;
- pre-existing dispatch, invocation, execution, result, approval, Governance
  mutation, or Replay mutation markers;
- reordered or substituted dispatch Replay;
- invocation input that does not contain a valid dispatch artifact.

Nested G31 reconstruction additionally rejects stale repository evidence,
changed scope, selection, registry, certification, CODEX identity, category,
role, profile, and Provider-role substitution.

Duplicate prevention has two existing layers:

1. deterministic append-only dispatch Replay rejects reuse of the same G31
   dispatch destination;
2. legacy domain discovery excludes assignments already represented by a
   standard dispatch Replay.

Bounded observation: the public constructor does not accept a session-root
parameter and can be called with another empty Replay destination. The G31
direct caller must use one deterministic same-session destination derived from
the assignment hash. No runtime redesign is required for that bounded call.

## Real PTY observation

A disposable Git repository contained exactly one implementation and one
focused test. Through real PTY-backed `./aicli`, the user supplied only:

```text
Improve the human interface terminal summary behavior. Include focused tests
and validation.
```

Two contextual approvals produced:

- governed proposal approval;
- exact repository grounding;
- distinct human execution confirmation;
- `EXECUTION_AUTHORIZED`;
- CODEX selected in `WORKER_ROLE`;
- `WORKER_INVOCATION_REQUEST_CREATED`;
- `WORKER_ASSIGNED`;
- canonical assignment presentation;
- truthful stop before dispatch.

Observed filesystem evidence:

- one execution authorization Replay;
- one Worker selection Replay;
- one invocation-request Replay;
- one Worker-assignment Replay;
- zero Worker-dispatch artifacts or directories;
- zero Worker-invocation artifacts or directories.

Observed boundaries:

```text
worker_dispatched = false
provider_invoked = false
worker_invoked = false
command_executed = false
repository_mutated = false
aicli_authorizes = false
aicli_executes = false
aicli_owns_replay = false
```

The disposable source Git hashes remained unchanged:

- implementation: `582eec37c9b9169f8cbf5b3f511ed4eaab898b3e`;
- focused test: `74ad2f17f47f79462f3cd499a90ce8898bdadb02`.

The disposable repository and runtime evidence were removed.

## Focused validation

Focused counts overlap and must not be added together:

- existing G24 Worker dispatch: **12 passed, 0 skipped, 0 failed**;
- Worker invocation request and assignment: **25 passed, 0 skipped,
  0 failed**;
- G31-10 through G31-12B: **43 passed, 0 skipped, 0 failed**;
- Worker runtime, selection certification, and unified selection:
  **40 passed, 0 skipped, 0 failed**;
- execution authorization and G31-08/G31-09:
  **60 passed, 0 skipped, 0 failed**;
- Replay suites: **245 passed, 0 skipped, 0 failed**;
- Human Interface and AiCLI: **42 passed, 0 skipped, 0 failed**;
- Governance tests: **96 passed, 0 skipped, 0 failed**;
- inspected production-module `py_compile`: passed;
- audit-document whitespace validation: passed;
- `git diff --check`: passed.

No full repository suite was run because focused evidence and certification
evidence were consistent.

## Governance result

Repository governance remains:

`PARTIALLY_CONFORMANT`

The deterministic read-only conformance engine reports:

- checks passed: 18;
- checks failed: 2;
- critical violations: 0;
- deterministic: true;
- fail-closed: true;
- read-only: true;
- report hash:
  `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea`.

The two findings are the known pre-existing root and system pre-commit hook
drift. They do not invalidate dispatch reachability.

## Minimal direct-binding projection

Exact existing caller:

`aigol.cli.aicli._record_contextual_execution_decision`

Exact existing callee:

`aigol.runtime.worker_dispatch_runtime.dispatch_assigned_worker`

Existing artifact families:

- `WORKER_ASSIGNMENT_ARTIFACT_V1`;
- `WORKER_DISPATCH_EVIDENCE_ARTIFACT_V1`;
- `WORKER_DISPATCH_CLASSIFICATION_ARTIFACT_V1`;
- `WORKER_DISPATCH_ARTIFACT_V1`;
- `WORKER_DISPATCH_RESULT_ARTIFACT_V1`.

Exact missing edge:

After `assignment_status == WORKER_ASSIGNED`, call the existing dispatch
constructor with the exact assignment artifact and Replay reference, using one
deterministic same-session Replay destination derived from the assignment hash.

No missing field or compatibility projection exists.

Maximum justified production additions: **50 lines**.

New production file necessary: **no**.

Presentation impact: call the existing dispatch renderer after the existing
assignment renderer and expose truthful stage flags.

Required stop boundary: do not import or call `invoke_dispatched_worker` or any
Provider, command, execution, result, or mutation runtime.

## Progress estimates

Evidence-scoped planning estimates remain unchanged by this audit:

- no-copy/paste conversational governed development: **99%**;
- whole-project progress: **88%**.

These are not certification or production-readiness claims.

## Exactly one next reachability state

`G31_12B_TO_EXISTING_G24_WORKER_DISPATCH_DIRECT_BINDING_READY`

## Bounded G31-13B implementation prompt

```text
# Generation 31-13B — G31 Assignment to Existing Certified G24 Worker Dispatch Direct Binding

Treat Generation 30, committed G31-02 through G31-12B, G31-11A, G31-R01,
G31-12A, and the G31-13A audit as immutable accepted baselines.

G31-13A verdict:

EXISTING_G24_WORKER_DISPATCH_REUSABLE_DIRECT_BINDING_REQUIRED

Confirmed reachability state:

G31_12B_TO_EXISTING_G24_WORKER_DISPATCH_DIRECT_BINDING_READY

## Objective

Implement exactly one direct existing-function transition:

valid G31-12B WORKER_ASSIGNMENT_ARTIFACT_V1
  -> existing dispatch_assigned_worker
  -> existing WORKER_DISPATCH_ARTIFACT_V1 and Replay
  -> existing render_worker_dispatch_summary
  -> stop before Worker invocation

Do not create or redesign dispatch, dispatch authorization, assignment,
selection, Worker identity, registry, Replay, Governance, or Human Interface
semantics.

## Required direct binding

In the existing `_record_contextual_execution_decision` continuation only:

1. after exact `WORKER_ASSIGNED`, call `dispatch_assigned_worker`;
2. pass the exact assignment artifact and assignment Replay reference;
3. use one deterministic same-session Replay destination derived from the
   assignment artifact hash;
4. use an existing Platform Core/Governance dispatcher identity;
5. retain the existing assignment, request, authorization, selection,
   repository-scope, and Replay lineage unchanged;
6. expose the existing dispatch capture and status;
7. call the existing dispatch renderer after the assignment renderer;
8. stop before `invoke_dispatched_worker`.

No new production module or canonical artifact family is permitted. Maximum
production additions: 50 lines.

## Required successful stop state

worker_selected = true
worker_assigned = true
worker_dispatched = true
provider_invoked = false
worker_invoked = false
command_executed = false
repository_mutated = false

An invocation-request artifact is not invocation. Assignment is not dispatch.
Dispatch is not Worker invocation or command execution.

## Authorization and hybrid-role boundaries

Reuse the existing dispatch contract's reconstructed authorization lineage. Do
not create another approval, human confirmation, authorization artifact, or
policy engine.

Preserve:

resource_id = CODEX
resource_category = HYBRID_PROVIDER_WORKER
selected_role_type = WORKER_ROLE
authority_profile = WORKER_AUTHORIZED_TASK_ONLY
provider_authority = false
provider_invoked = false

Do not activate the Provider role.

## Fail-closed requirements

Reject before partial dispatch creation:

- missing, failed, substituted, stale, or reordered assignment evidence;
- changed assignment identity or hash;
- changed request, authorization, packet, scope, selection, registry,
  certification, Worker identity, category, role, profile, or evidence hash;
- unavailable or incompatible Worker;
- Provider-role substitution;
- duplicate dispatch;
- cross-session Replay destination or assignment reference;
- any evidence that indicates Worker invocation, execution, result creation,
  command execution, repository mutation, Governance mutation, or Replay
  mutation.

Use the deterministic same-session path to preserve duplicate and
cross-session boundaries. Do not add a discovery framework.

## Explicit non-goals

Do not:

- call `invoke_dispatched_worker`;
- invoke a Provider or Worker;
- execute a command;
- mutate the repository;
- create Worker results;
- implement later execution, validation, certification, completion, or
  termination stages;
- bind MOC or live-Provider dispatch authorization artifacts;
- repair governance hook drift;
- bundle downstream blockers.

## Focused tests

Prove:

1. exact G31-12B assignment reaches existing `WORKER_DISPATCHED`;
2. existing dispatch artifact and Replay are used unchanged;
3. complete G31 lineage reconstructs through dispatch Replay;
4. selection, assignment, authorization, scope, request, Worker and evidence
   substitutions fail closed;
5. Provider-role substitution fails;
6. duplicate or cross-session dispatch fails;
7. existing G24 dispatch callers remain unchanged;
8. canonical presentation distinguishes request, assignment, dispatch, and
   invocation;
9. AiCLI owns no dispatch semantics;
10. no Provider or Worker invocation, command, result, or repository mutation
    occurs.

## PTY validation

Use a disposable Git repository with one implementation and one focused test.
Through real PTY-backed `./aicli`, use only an ordinary bounded request and
contextual approvals. Demonstrate authorization, CODEX selection, request,
assignment, existing G24 dispatch, canonical dispatch presentation, complete
nested Replay, one tampered fail-closed case, and the truthful stop before
Worker invocation.

Do not supply paths, JSON, Worker identities, capability names, prepared
artifacts, technical prompts, or shell bridges. Remove the disposable
repository afterward.

## Validation

Run focused G31-13B, G24 request/assignment/dispatch, G31-10 through G31-12B,
Worker registry/certification/selection, authorization, Replay, Human
Interface/AiCLI, and Governance tests. Run py_compile and git diff --check.
Run the full repository suite once only after all focused evidence passes.

## Documentation

Add:

docs/governance/G31_13B_G31_ASSIGNMENT_TO_EXISTING_CERTIFIED_G24_WORKER_DISPATCH_DIRECT_BINDING.md

Document exact reuse, call edge, dispatch artifacts, Replay, presentation,
authority boundaries, PTY evidence, validation, change size, progress, and
exactly one next reachability state.

## Required final report

Provide implementation verdict, exact changed files and line counts, every new
production symbol, reused contracts, PTY and Replay evidence, fail-closed
evidence, authority boundaries, focused and full validation counts, Governance
status, exact git status and commit commands, progress estimates, and exactly
one next state for Worker-invocation reachability audit.

Do not commit.
```

No commit was created by this audit.
