# Generation 31-14A — Existing Certified G24 Worker Invocation Reachability Audit

Status: completed `AUDIT_ONLY`; no runtime behavior changed.

Date: 2026-07-16

Audit verdict:

`EXISTING_G24_WORKER_INVOCATION_REUSABLE_DIRECT_BINDING_REQUIRED`

Exactly one next reachability state:

`G31_13B_TO_EXISTING_G24_WORKER_INVOCATION_DIRECT_BINDING_READY`

## Constitutional scope

This audit treats Generation 30, committed G31-02 through G31-13B, G31-11A,
G31-R01, G31-12A, and G31-13A as immutable accepted baselines.

The audit changed no production runtime, CLI, Human Interface, test, schema,
artifact family, Worker or Provider configuration, authorization policy,
Governance contract, or Replay contract. The only repository change is this
report.

No operational G31 Worker invocation, Provider invocation, Worker process,
command, result creation, execution start, external request, or repository
mutation was performed.

## Plain-language conclusion

The certified G24 Worker-invocation runtime already consumes the exact
`WORKER_DISPATCH_ARTIFACT_V1` and dispatch Replay produced by G31-13B. Its
existing read-only dispatch-lineage loader accepted the exact G31-13B capture
with every continuity check true.

Despite its name, `invoke_dispatched_worker` does not launch CODEX, a process,
a Provider, a command, a network request, or repository mutation. It records
the governed `WORKER_DISPATCHED -> WORKER_INVOKED` lifecycle boundary using
four immutable evidence artifacts and append-only Replay. Execution, Worker
output, result capture, validation, and mutation are separate downstream
contracts.

The reference `./aicli` currently stops after G31-13B dispatch and does not
import or call the existing invocation function. The first missing transition
is therefore one direct existing-function call:

```text
aigol.cli.aicli._record_contextual_execution_decision
  -> aigol.runtime.worker_invocation_runtime.invoke_dispatched_worker
```

No adapter, compatibility projection, external integration, additional human
decision, new authorization artifact, new Worker runtime, or new artifact
family is required.

## Certified invocation architecture

The current-chain certified lifecycle is:

```text
WORKER_DISPATCH_ARTIFACT_V1
  + dispatch Replay
  -> dispatch/request/assignment/authorization lineage reconstruction
  -> invocation eligibility classification
  -> WORKER_INVOCATION_EVIDENCE_ARTIFACT_V1
  -> WORKER_INVOCATION_CLASSIFICATION_ARTIFACT_V1
  -> WORKER_INVOCATION_ARTIFACT_V1
  -> WORKER_INVOCATION_RESULT_ARTIFACT_V1
  -> stop before execution and Worker result capture
```

Checked-in current-chain certification declares:

`AIGOL_WORKER_INVOCATION_RUNTIME_STATUS = CERTIFIED`

Older foundation documents remain lineage evidence. The earlier
`READY_WITH_GAPS` foundation classification predates the implemented and
certified current-chain runtime and does not override the later certification.

## Exact contract inventory

### Entry detection

| Contract | File | Canonical input | Canonical output | Authority | External action |
|---|---|---|---|---|---|
| `detect_domain_worker_invocation_entry_intent` | `aigol/runtime/worker_invocation_runtime.py` | narrow operator prompt | non-authoritative domain invocation intent | detection only | none |

The G31 direct path does not need this detector because it already holds the
exact successful dispatch capture.

### Existing dispatch discovery

| Contract | File | Canonical input | Canonical output | Authority | External action |
|---|---|---|---|---|---|
| `find_latest_domain_worker_dispatch` | `aigol/runtime/worker_invocation_runtime.py` | session root and domain | latest valid uninvoked domain dispatch | read-only discovery | none |

The G31 direct path does not need discovery. It must pass the exact dispatch
capture created in the same continuation.

### Current-chain invocation constructor

Public symbol:

`invoke_dispatched_worker`

Exact signature:

```python
invoke_dispatched_worker(
    *,
    worker_invocation_id: str,
    worker_dispatch_artifact: dict[str, Any],
    worker_dispatch_replay_reference: str,
    invoked_by: str,
    invoked_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]
```

Canonical input:

- one `WORKER_DISPATCH_ARTIFACT_V1`;
- its exact immutable dispatch Replay reference;
- deterministic invocation identity;
- existing AiGOL/Governance actor identity;
- deterministic timestamp;
- empty append-only invocation Replay destination.

Canonical output:

- invocation evidence;
- invocation classification;
- `WORKER_INVOCATION_ARTIFACT_V1`;
- invocation result;
- capture with Replay reference.

Authority owner: governed AiGOL Worker-invocation boundary.

Replay owner: existing append-only Worker-invocation Replay.

External action: none.

Code execution: none.

Repository mutation: none.

### Compatibility wrapper

Public symbol:

`invoke_worker`

It preserves current-chain and older legacy callers. When supplied the
current-chain `worker_dispatch_artifact` arguments, it delegates directly to
`invoke_dispatched_worker`. G31 does not need the wrapper because the exact
current-chain constructor is available.

### Invocation artifacts

The certified constructor emits unchanged:

- `WORKER_INVOCATION_EVIDENCE_ARTIFACT_V1`;
- `WORKER_INVOCATION_CLASSIFICATION_ARTIFACT_V1`;
- `WORKER_INVOCATION_ARTIFACT_V1`;
- `WORKER_INVOCATION_RESULT_ARTIFACT_V1`.

The evidence binds dispatch, assignment, invocation request, authorization,
execution packet, Worker identity, allowed output, forbidden operation,
validation, chain, authority, and Replay lineage.

### Invocation Replay reconstruction

Public symbol:

`reconstruct_worker_invocation_replay`

It reconstructs the four ordered invocation wrappers, validates wrapper and
artifact hashes, validates classification and result continuity, reloads the
dispatch Replay, and transitively reconstructs the complete assignment,
request, authorization, selection, registry, certification, Project Objective,
and repository-scope lineage.

Replay owner remains the invocation runtime. Replay creates no authority.

### Canonical Presentation

Public symbol:

`render_worker_invocation_summary`

It renders invocation status, invocation and dispatch references, Worker
identity, Replay reference, and the explicit downstream boundaries:

```text
No result validation yet.
No replay review yet.
No termination yet.
```

No new presentation semantic is required.

### Invocation eligibility and validation

Existing private validators used by the public constructor include:

- `_load_dispatch_lineage`;
- `_validate_dispatch_artifact`;
- `_dispatch_authority_continuity`;
- `_validate_invocation_artifact`;
- artifact and wrapper hash verification;
- ordered Replay validation;
- append-only destination validation;
- `_worker_dispatch_already_invoked` for domain discovery.

The exact G31-13B dispatch passed `_load_dispatch_lineage` without projection.
All nine checks were true:

```text
dispatch_lineage = true
assignment_lineage = true
invocation_request_lineage = true
authorization_lineage = true
execution_packet_lineage = true
worker_identity_continuity = true
chain_continuity = true
replay_continuity = true
authority_continuity = true
```

### Production callers

Existing production callers prove the constructor is operational:

- `_continue_worker_request_to_replay_certification` in
  `aigol/cli/aigol_cli.py`;
- legacy approval-resume continuation in `aigol/cli/aigol_cli.py`;
- legacy domain Worker-invocation workflow in `aigol/cli/aigol_cli.py`;
- fail-closed legacy invocation fallback in `aigol/cli/aigol_cli.py`;
- legacy domain execution continuation in `aigol/cli/aigol_cli.py`;
- additional certified continuation in `aigol/cli/aigol_cli.py`;
- `_run_worker_stack` in
  `aigol/runtime/g5_pgsp_worker_runtime_orchestration.py`.

Those callers either stop after invocation or explicitly call separate
downstream execution/result contracts. Invocation itself contains no hidden
continuation.

The reference `aigol/cli/aicli.py` is not a current caller.

### Downstream execution boundary

Separate public contracts consume invocation only after it exists:

- `bridge_worker_invocation_to_execution_candidate` creates a separately
  governed candidate and requires its own bounded approval contract;
- `start_execution` records execution start;
- `capture_worker_result` captures output only after a separate execution or
  output boundary supplies it;
- result validation, replay review, completion, and termination remain later
  contracts.

None of these contracts is imported or called by
`invoke_dispatched_worker`.

### Command, result, and mutation boundaries

`worker_invocation_runtime.py` imports no subprocess, shell, command runner,
Provider, network client, credential source, repository mutator, execution
runtime, or result runtime.

The constructor does not:

- launch a Worker process;
- execute code;
- execute a command;
- activate a Provider;
- create an execution candidate;
- start execution;
- create or validate Worker output;
- create completion or termination evidence;
- mutate the target repository;
- mutate Governance;
- mutate existing Replay.

It writes only new immutable invocation evidence to its supplied empty Replay
directory.

## Exact invocation semantics

| Behavior | Existing function behavior | Deterministic evidence |
|---|---|---|
| Invocation lifecycle evidence creation | Yes | Creates four current-chain invocation artifacts and ordered Replay. |
| Actual Worker process activation | No | No process, adapter, Worker executable, or transport call exists. |
| Provider activation | No | No Provider import/call; authority flags remain false. |
| Command execution | No | No subprocess, shell, command, or execution runtime call. |
| Worker result creation | No | `result_created = false`; result capture is a separate module. |
| Execution-governance candidate creation | No | Separate bridge contract is not called. |
| Execution start | No | `execution_started = false`; `start_execution` is separate. |
| Repository mutation | No | No repository writer or mutation contract. |
| External network/service dependency | No | No network/API/MCP/Provider dependency. |

The function name records the constitutional invocation boundary. It does not
mean that CODEX or another Worker process has executed work.

## Exhaustive compatibility matrix

| Required input or evidence | Classification | Deterministic evidence |
|---|---|---|
| Session identity | `AVAILABLE_BUT_NOT_BOUND` | Encoded in same-session Replay paths and caller context; G24 invocation artifact has no separate session field. |
| Original human goal | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Preserved inside G31 authorization scope reconstructed through request and dispatch Replay. |
| Project Objective | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Bound by the G31 authorization and nested request Replay. |
| Durable Governed Work | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Preserved in approved G31 lineage. |
| Repository grounding | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Reconstructed through authorization scope and request lineage. |
| Execution summary | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Bound by distinct human decision and authorization Replay. |
| Human confirmation | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Reconstructed through G31 execution authorization. |
| Execution-authorization identity/hash | `DIRECTLY_COMPATIBLE` | Dispatch contains exact authorization reference and hash; invocation copies both. |
| Execution-authorization Replay | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Dispatch -> assignment -> request Replay reconstructs the authorization. |
| G31 selection identity | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Invocation request Replay reconstructs exact selection. |
| Registry evidence | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Bound and validated in G31 request/selection Replay. |
| Worker-selection certification | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Bound and validated by the G31 selection reconstruction. |
| CODEX identity | `DIRECTLY_COMPATIBLE` | Dispatch and invocation input carry `worker_id = CODEX`. |
| CODEX version | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Preserved in nested selected-resource evidence. |
| `HYBRID_PROVIDER_WORKER` category | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Exact nested selection reconstruction requires this category. |
| `WORKER_ROLE` | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Selection requires `WORKER_ROLE`; dispatch carries concrete Worker role. |
| `WORKER_AUTHORIZED_TASK_ONLY` profile | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Exact nested selection reconstruction validates it. |
| `provider_authority = false` | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Selection and Worker evidence validate no Provider authority. |
| `provider_invoked = false` | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | G31 outer state and nested selection retain false. |
| Invocation-request identity/hash | `DIRECTLY_COMPATIBLE` | Dispatch carries both and invocation copies them. |
| Invocation-request Replay | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Dispatch Replay resolves assignment evidence, which resolves request Replay. |
| Assignment identity/hash | `DIRECTLY_COMPATIBLE` | Dispatch carries both and invocation binds them. |
| Assignment Replay | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Dispatch evidence contains the exact assignment Replay reference. |
| Dispatch evidence artifact | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Loaded from exact dispatch Replay by invocation lineage validation. |
| Dispatch classification artifact | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Loaded and hash-validated from exact dispatch Replay. |
| Dispatch artifact | `DIRECTLY_COMPATIBLE` | Exact canonical invocation input. |
| Dispatch result artifact | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Reconstructed and checked against dispatch hash. |
| Dispatch Replay | `DIRECTLY_COMPATIBLE` | Exact second canonical invocation input. |
| Workspace | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Preserved in authorization scope. |
| Source paths | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Preserved in exact grounded targets and allowed outputs. |
| Focused-test paths | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Preserved in repository grounding. |
| Symbols and code locations | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Preserved in repository target evidence. |
| Repository evidence hashes | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Revalidated through complete G31 nested reconstruction. |
| Mutation layers | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Preserved in exact authorization scope. |
| Allowed outputs | `DIRECTLY_COMPATIBLE` | Dispatch carries them; invocation copies and checks them. |
| Forbidden operations | `DIRECTLY_COMPATIBLE` | Dispatch carries exact constraints; invocation preserves them unchanged. |
| Validation requirements | `DIRECTLY_COMPATIBLE` | Dispatch carries exact requirements; invocation copies them. |
| Worker availability | `DIRECTLY_COMPATIBLE` | Dispatch must report assigned Worker state and valid authority continuity. |
| Invocation identity | `AVAILABLE_BUT_NOT_BOUND` | Existing caller must deterministically derive one from dispatch identity. |
| Invocation Replay destination | `AVAILABLE_BUT_NOT_BOUND` | Existing append-only contract; reference caller does not yet construct it. |
| Invocation evidence/classification/artifact/result | `AVAILABLE_BUT_NOT_BOUND` | Existing constructor creates them once the direct call is made. |
| Invocation stop-state flags | `DIRECTLY_COMPATIBLE` | Existing artifacts set invoked true and execution/result/mutation states false. |

No required field is `MISSING` or `INCOMPATIBLE`.

## Authorization assessment

Classification:

`AVAILABLE_THROUGH_EXISTING_PUBLIC_PROJECTION`

The existing invocation constructor accepts no separate invocation-
authorization artifact. It requires the exact G31 authorization reference and
hash already preserved in the dispatch artifact, and reconstructs authorization
lineage transitively through dispatch, assignment, and invocation-request
Replay.

The G31 execution packet's `forbidden_operations` list includes
`INVOKE_WORKER`. The existing current-chain contract deterministically treats
this list as the operations forbidden to the assigned Worker and preserves it
into invocation evidence. The governed AiGOL invocation boundary is a separate
lifecycle authority: the certified constitutional model explicitly permits
only AiGOL Governance to record invocation and prohibits Worker self-invocation.
This is existing runtime and certification behavior, not a new interpretation
introduced by this audit.

No additional human confirmation, approval, authorization artifact, policy
engine, or Provider authorization is required.

## Invocation versus execution boundary

The certified positive transition is:

```text
WORKER_DISPATCHED -> WORKER_INVOKED
```

The resulting isolated state is proven to be:

```text
worker_selected = true
worker_assigned = true
worker_dispatched = true
worker_invoked = true
provider_invoked = false
execution_started = false
command_executed = false
result_created = false
repository_mutated = false
```

Invocation is therefore separable from execution in the existing architecture.
`start_execution`, execution-candidate creation, Worker output capture, result
validation, replay review, completion, and termination require separate public
calls and are outside a future G31-14B binding.

## Hybrid-role separation

Read-only exact G31-13B evidence confirmed:

```text
resource_id = CODEX
resource_category = HYBRID_PROVIDER_WORKER
selected_role_type = WORKER_ROLE
authority_profile = WORKER_AUTHORIZED_TASK_ONLY
provider_invoked = false
```

The invocation constructor consumes the already-bound dispatch Worker identity
and role. It does not select a resource, resolve a Provider, inspect Provider
credentials, activate Provider authority, or reinterpret historical Provider
evidence.

Provider-role, category, authority-profile, registry, or certification
substitution invalidates nested request/selection Replay before invocation
eligibility succeeds.

## External dependency assessment

The existing current-chain invocation constructor requires none of:

- a locally installed Worker executable;
- CODEX CLI availability;
- an API credential;
- a Provider endpoint;
- network access;
- a Worker process;
- an MCP server;
- an external service runtime;
- a separate external authorization.

It requires only local immutable artifacts, their Replay, and an empty local
Replay destination. External availability is not a blocker and
`RUNTIME_EVIDENCE_BLOCKED` is not applicable.

## Fail-closed evidence

Existing focused tests and validators reject:

- missing or failed dispatch;
- changed dispatch identity or hash;
- changed assignment hash;
- changed authorization hash;
- changed execution packet;
- changed Worker identity;
- corrupt dispatch Replay;
- authority-boundary changes;
- canonical chain substitution;
- invalid invocation Replay hashes or ordering;
- append-only invocation destination reuse.

Nested dispatch reconstruction additionally rejects changed invocation request,
authorization scope, G31 selection, registry, certification, repository
grounding, source evidence, Worker category, role, authority profile, and
Provider-authority evidence.

Existing domain discovery excludes a dispatch already bound to a valid
invocation. The append-only constructor rejects a second use of the same
deterministic invocation destination.

The public constructor has no session-root parameter. As with G31-13B, a future
reference caller must eliminate cross-session input by passing the exact
same-continuation dispatch capture and deriving one deterministic invocation
destination beneath the active session root. No new discovery or persistence
framework is required.

Pre-invocation validation requires `worker_invoked = false`,
`execution_started = false`, `result_created = false`,
`governance_mutated = false`, and `replay_mutated = false`. Evidence of prior
execution or mutation fails authority continuity.

## Existing call-chain trace

Current reference lifecycle:

```text
G31-10 execution authorization
  -> G31-11B CODEX/WORKER_ROLE selection
  -> G31-12B invocation request
  -> G31-12B assignment
  -> G31-13B G24 dispatch
  -> stop
```

Expected existing lifecycle after one bounded binding:

```text
G31-13B dispatch capture
  -> existing dispatch lineage validation
  -> existing invoke_dispatched_worker
  -> existing invocation evidence/classification/artifact/result
  -> existing invocation Replay
  -> existing render_worker_invocation_summary
  -> stop before execution candidate, start_execution, command, output, or mutation
```

Exact existing caller for the missing reference edge:

`aigol.cli.aicli._record_contextual_execution_decision`

Exact existing callee:

`aigol.runtime.worker_invocation_runtime.invoke_dispatched_worker`

Current AiCLI invokes it: no.

Exact first unbound transition:

`G31_13B_DISPATCH_TO_EXISTING_G24_INVOCATION_CALL_ABSENT`

No field or compatibility projection is missing.

## Real PTY-backed observation

A disposable Git repository contained exactly:

- `aigol/runtime/human_interface.py`;
- `tests/test_human_interface.py`.

The ordinary user request was:

```text
Improve the human interface terminal summary behavior. Include focused tests
and validation.
```

The user supplied no path, JSON, Worker identity, artifact name, capability
name, technical prompt, prepared artifact, or shell bridge. Only contextual
approvals were used.

The real PTY-backed `./aicli` session reached:

1. governed proposal and proposal approval;
2. canonical repository grounding;
3. separate execution review and human decision;
4. G31-10 execution authorization;
5. CODEX in `WORKER_ROLE` selection;
6. invocation-request creation;
7. assignment;
8. G31-13B `WORKER_DISPATCHED`;
9. truthful stop before Worker invocation.

The terminal rendered:

```text
Dispatch Status: WORKER_DISPATCHED
No Worker has been invoked, executed, or produced results.
```

Read-only reconstruction returned:

```text
dispatch_status = WORKER_DISPATCHED
worker_id = CODEX
worker_invoked = false
execution_started = false
result_created = false
```

No invocation artifact and no execution artifact existed.

The disposable source Git object identities were unchanged:

```text
aigol/runtime/human_interface.py
  5969878c4d0cf265afe26c099abfde374fba9f57
tests/test_human_interface.py
  1a46b516c00579cf30a533a46798d78e7da445bc
```

Git status remained clean. The disposable repository, runtime, and transcript
were removed.

## Focused validation

Read-only and existing-fixture validation completed:

- existing G24 Worker invocation: **16 passed, 0 skipped, 0 failed**;
- G24 invocation request, assignment, and dispatch: **37 passed, 0 skipped,
  0 failed**;
- G31-10 through G31-13B: **58 passed, 0 skipped, 0 failed**;
- Worker registry, certification, and selection: **40 passed, 0 skipped,
  0 failed**;
- authorization: **60 passed, 0 skipped, 0 failed**;
- Replay: **245 passed, 0 skipped, 0 failed**;
- Human Interface and AiCLI: **42 passed, 0 skipped, 0 failed**;
- Governance: **96 passed, 0 skipped, 0 failed**.

Existing invocation fixtures exercise only the deterministic artifact-and-
Replay constructor. They launch no Worker or Provider and execute no command.

The complete repository suite was not run because focused evidence is
consistent with checked-in certification and the audit found no runtime
conflict.

Static validation:

- inspected production-module `py_compile`: passed;
- audit-document whitespace validation: passed;
- `git diff --check`: passed.

## Governance result

Repository Governance remains:

`PARTIALLY_CONFORMANT`

The deterministic read-only conformance engine reports:

- checks passed: 18;
- checks failed: 2;
- critical violations: 0;
- deterministic: true;
- fail-closed: true;
- read-only: true.

The two known hook-drift findings remain visible. They predate G31-14A, do not
invalidate the invocation reachability evidence, and were not repaired or
reinterpreted by this audit.

## Minimal future direct binding

No architecture or compatibility projection is required.

Smallest justified future implementation:

```text
exact G31-13B worker_dispatch_capture
  -> invoke_dispatched_worker
  -> existing invocation artifacts and Replay
  -> render_worker_invocation_summary
  -> stop before execution
```

Exact existing caller:

`aigol.cli.aicli._record_contextual_execution_decision`

Exact existing callee:

`aigol.runtime.worker_invocation_runtime.invoke_dispatched_worker`

Exact artifact families:

- input: `WORKER_DISPATCH_ARTIFACT_V1` and dispatch Replay;
- output: the four existing `WORKER_INVOCATION_*_ARTIFACT_V1` families.

Missing fields: none.

Missing edge:

`G31_13B_DISPATCH_TO_EXISTING_G24_INVOCATION_CALL_ABSENT`

External requirements: none.

Projected production files:

- modify `aigol/cli/aicli.py` only.

New production symbols: none expected.

Maximum justified production additions: **50 lines**.

Required presentation impact: call the existing invocation renderer after the
existing dispatch renderer and expose truthful outer invocation status.

Required downstream stop boundary:

```text
worker_invoked = true
provider_invoked = false
execution_started = false
command_executed = false
result_created = false
repository_mutated = false
```

The implementation must not call `bridge_worker_invocation_to_execution_candidate`,
`start_execution`, `capture_worker_result`, a Worker adapter, Provider runtime,
command runner, or repository mutator.

## Progress estimates

Evidence-scoped planning estimates remain:

- no-copy/paste conversational governed development: **99%**;
- whole-project progress: **88%**.

This audit changes evidence, not runtime reachability. The next bounded direct
binding would close the invocation-evidence edge but would not authorize
execution, commands, results, or repository mutation.

## Exactly one next reachability state

`G31_13B_TO_EXISTING_G24_WORKER_INVOCATION_DIRECT_BINDING_READY`

## Bounded G31-14B implementation prompt

```text
# Generation 31-14B — G31 Dispatch to Existing Certified G24 Worker Invocation Direct Binding

Treat Generation 30, committed G31-02 through G31-13B, G31-11A, G31-R01,
G31-12A, G31-13A, and the accepted G31-14A audit as immutable baselines.

G31-14A verdict:

EXISTING_G24_WORKER_INVOCATION_REUSABLE_DIRECT_BINDING_REQUIRED

Confirmed state:

G31_13B_TO_EXISTING_G24_WORKER_INVOCATION_DIRECT_BINDING_READY

Primary priority:

NO_COPY_PASTE_CONVERSATIONAL_GOVERNED_DEVELOPMENT_THROUGH_AICLI

## Certified premise

The existing certified current-chain invocation constructor accepts the exact
G31-13B WORKER_DISPATCH_ARTIFACT_V1 and dispatch Replay unchanged.

Reuse unchanged:

- invoke_dispatched_worker;
- reconstruct_worker_invocation_replay;
- render_worker_invocation_summary;
- WORKER_INVOCATION_EVIDENCE_ARTIFACT_V1;
- WORKER_INVOCATION_CLASSIFICATION_ARTIFACT_V1;
- WORKER_INVOCATION_ARTIFACT_V1;
- WORKER_INVOCATION_RESULT_ARTIFACT_V1;
- existing invocation validation;
- existing invocation Replay;
- existing duplicate-invocation protection.

Do not create or redesign invocation, execution authorization, dispatch,
assignment, Worker selection, Worker identity, Provider authority, Replay,
Governance, Human Interface semantics, or canonical artifact families.

## Objective

Implement exactly one direct existing-function transition:

valid G31-13B WORKER_DISPATCH_ARTIFACT_V1
  -> existing invoke_dispatched_worker
  -> existing invocation artifacts
  -> existing invocation Replay
  -> existing render_worker_invocation_summary
  -> stop before execution, command, result, or repository mutation

The existing constructor records invocation lifecycle evidence only. It does
not launch CODEX, a Worker process, a Provider, a command, or a network call.

## Mandatory pre-implementation check

Before editing:

1. inspect the exact public signature of invoke_dispatched_worker;
2. inspect every existing production caller;
3. confirm the existing AiGOL/Governance invoked-by identity;
4. confirm the exact dispatch artifact and Replay arguments;
5. confirm the deterministic append-only destination convention;
6. report the intended call edge;
7. report projected production files and additions.

The audit proved no compatibility projection or external dependency is
required. If implementation requires more than a direct lifecycle call,
deterministic destination construction, capture projection, and existing
presentation continuation, stop before expanding scope.

## Required direct binding

In the existing `_record_contextual_execution_decision` continuation only:

1. after exact successful `WORKER_DISPATCHED`, call
   `invoke_dispatched_worker`;
2. pass the exact G31-13B dispatch artifact;
3. pass the exact dispatch Replay reference;
4. use one deterministic same-session append-only destination derived from the
   dispatch artifact hash using existing conventions;
5. use `AIGOL_GOVERNANCE` as the existing governed actor identity;
6. preserve complete authorization, selection, request, assignment, dispatch,
   repository-scope, Worker, and Replay lineage;
7. expose the existing invocation capture and status;
8. call the existing invocation renderer after the dispatch renderer;
9. stop before execution candidate creation, `start_execution`, Worker output,
   result capture, validation, command execution, or mutation.

AiCLI may invoke the existing Platform Core continuation and render its result.
It must not decide invocation eligibility or own invocation policy.

## Required successful state

worker_selected = true
worker_assigned = true
worker_dispatched = true
worker_invoked = true
provider_invoked = false
execution_started = false
command_executed = false
result_created = false
repository_mutated = false

Preserve stage truthfulness:

- selection retains assignment and dispatch false at its stage;
- assignment retains dispatch and invocation false at its stage;
- dispatch retains invocation false at its stage;
- only the outer invocation continuation and invocation artifact record
  invocation true;
- no stage may claim execution, command, result, or mutation.

## Invocation versus execution

Invocation is the replay-visible governed lifecycle record that bounded work
was delivered to the dispatched Worker identity. In this certified runtime it
does not launch a process or execute work.

Do not call or import in the new path:

- bridge_worker_invocation_to_execution_candidate;
- start_execution;
- capture_worker_result;
- any Provider or Worker adapter;
- any command runner;
- any repository mutator.

## Authorization and hybrid-role boundaries

Reuse authorization lineage already reconstructed by the invocation runtime.
Do not create another human confirmation, approval, authorization artifact, or
policy engine.

Preserve:

resource_id = CODEX
resource_category = HYBRID_PROVIDER_WORKER
selected_role_type = WORKER_ROLE
authority_profile = WORKER_AUTHORIZED_TASK_ONLY
provider_authority = false
provider_invoked = false

The governed AiGOL invocation boundary must not activate CODEX's Provider role.
The exact forbidden-operation list remains Worker-scope evidence and must be
preserved unchanged.

## Replay boundary

Creation of new immutable invocation Replay is required and permitted.

Do not modify or replace selection, request, authorization, assignment,
dispatch, or pre-existing Replay evidence.

The invocation destination must be deterministic, same-session, append-only,
derived from the dispatch artifact hash, and stable for duplicate rejection.

Do not introduce Replay discovery or a persistence abstraction.

## Fail-closed requirements

Reject before partial invocation creation:

- missing or failed dispatch;
- changed dispatch identity, hash, status, artifact, result, or Replay;
- reordered dispatch Replay;
- changed assignment or invocation request;
- changed authorization, execution packet, or repository scope;
- changed selection, registry, or certification;
- changed Worker identity, version, category, role, or authority profile;
- Provider-role substitution;
- unavailable or incompatible Worker;
- duplicate invocation;
- cross-session dispatch reference or invocation destination;
- evidence of prior invocation, execution, command, result, mutation, or Replay
  mutation.

Invalid evidence must not partially invoke work.

## Minimal-change gate

Requirements:

- no new production module;
- no new canonical artifact family;
- no new public production symbol unless unavoidable;
- maximum production additions: 50 lines;
- reuse public validation, serialization, Replay, and presentation contracts;
- no copied helper logic;
- no downstream execution preparation.

If more than 50 production additions are required, stop and report the
deterministic reason before exceeding the limit.

## Focused tests

Prove:

1. exact G31-13B dispatch reaches existing WORKER_INVOKED;
2. existing invocation artifact families are used unchanged;
3. complete G31 lineage reconstructs through invocation Replay;
4. dispatch, assignment, request, authorization, scope, selection, registry,
   certification, Worker, role, profile, and Provider substitutions fail;
5. duplicate invocation fails without changing original Replay;
6. deterministic same-session destination is used;
7. existing G24 invocation callers remain unchanged;
8. presentation distinguishes request, assignment, dispatch, invocation, and
   execution;
9. AiCLI owns no invocation or authorization semantics;
10. no Provider/Worker process, command, execution, result, network request, or
    repository mutation occurs.

## PTY validation

Use a disposable Git repository with one implementation and one focused test.

Through real PTY-backed ./aicli, submit an ordinary bounded natural-language
request and use only contextual approvals. Demonstrate authorization, CODEX in
WORKER_ROLE selection, request, assignment, dispatch, invocation evidence,
canonical invocation presentation, complete Replay reconstruction, one
duplicate or tampered failure, and truthful stop before execution.

Do not provide paths, JSON, Worker identities, artifact names, technical
prompts, prepared artifacts, or shell bridges.

Confirm source hashes and Git status remain unchanged. Remove the disposable
repository afterward.

## Validation

Run focused suites first:

- focused G31-14B;
- G24 request, assignment, dispatch, and invocation;
- G31-10 through G31-13B;
- Worker registry, certification, and selection;
- authorization;
- Replay;
- Human Interface and AiCLI;
- Governance;
- py_compile;
- git diff --check.

After all focused evidence passes, run the complete repository suite exactly
once.

## Documentation

Add:

docs/governance/G31_14B_G31_DISPATCH_TO_EXISTING_CERTIFIED_G24_WORKER_INVOCATION_DIRECT_BINDING.md

Document exact reuse, call edge, invocation semantics, destination, artifacts,
Replay, presentation, tamper and duplicate evidence, invocation-versus-
execution separation, hybrid-role separation, PTY evidence, validation,
Governance, and exact change accounting.

## Required final report

Provide:

1. implementation verdict;
2. plain-language summary;
3. exact changed files and accounting;
4. confirmation of the 50-line production limit;
5. every new production symbol and justification;
6. exact invocation contracts reused;
7. PTY evidence;
8. Replay, duplicate, and tamper evidence;
9. Canonical Presentation evidence;
10. invocation-versus-execution proof;
11. hybrid-role and authority confirmation;
12. exact focused and full-suite validation counts;
13. Governance, py_compile, and git diff --check results;
14. exact Git status and commit commands;
15. evidence-scoped progress estimates;
16. exactly one next reachability state;
17. an AUDIT_ONLY prompt for the next boundary.

Do not create a commit.

Architectural minimalism and evidence-first reuse are mandatory.
```

## Audit conclusion

The existing certified G24 current-chain invocation runtime is fully compatible
with the exact G31-13B dispatch artifact and Replay. It creates deterministic
invocation lifecycle evidence without activating CODEX, a Provider, a process,
a command, execution, a result, or repository mutation. The reference AiCLI
requires only one direct existing-function binding and existing presentation
continuation.
