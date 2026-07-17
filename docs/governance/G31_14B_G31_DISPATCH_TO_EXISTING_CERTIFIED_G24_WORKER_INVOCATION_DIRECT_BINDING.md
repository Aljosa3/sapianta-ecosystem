# Generation 31-14B — G31 Dispatch to Existing Certified G24 Worker Invocation Direct Binding

Status: completed bounded implementation.

Date: 2026-07-16

Implementation verdict:

`G31_DISPATCH_TO_EXISTING_CERTIFIED_G24_WORKER_INVOCATION_DIRECT_BINDING_OPERATIONAL`

Exactly one next state:

`EXISTING_G24_POST_INVOCATION_EXECUTION_REACHABILITY_UNVERIFIED`

## Constitutional scope

This implementation treats Generation 30, committed G31-02 through G31-13B,
G31-11A, G31-R01, G31-12A, G31-13A, and G31-14A as immutable accepted
baselines.

It closes exactly one transition:

```text
valid G31-13B WORKER_DISPATCH_ARTIFACT_V1
  -> existing invoke_dispatched_worker
  -> existing invocation artifacts
  -> existing invocation Replay
  -> existing render_worker_invocation_summary
  -> stop before execution candidate, execution, command, result, or mutation
```

No invocation runtime, authorization system, dispatch runtime, assignment
runtime, Worker selector, Worker identity, Provider authority, Replay
subsystem, Governance system, Human Interface semantic owner, or canonical
artifact family was created or redesigned.

## Accepted audit evidence

G31-14A concluded:

`EXISTING_G24_WORKER_INVOCATION_REUSABLE_DIRECT_BINDING_REQUIRED`

and established:

`G31_13B_TO_EXISTING_G24_WORKER_INVOCATION_DIRECT_BINDING_READY`

The audit proved that the exact G31-13B `WORKER_DISPATCH_ARTIFACT_V1` and
dispatch Replay are the native inputs of the existing certified current-chain
invocation constructor. No compatibility projection or external dependency was
required.

## Mandatory pre-implementation check

Exact public signature inspected:

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

Existing production callers were confirmed in:

- `aigol/cli/aigol_cli.py` lifecycle continuations;
- `aigol/runtime/g5_pgsp_worker_runtime_orchestration.py`.

The existing governed actor identity is:

`AIGOL_GOVERNANCE`

The required exact inputs already existed in the G31-13B dispatch capture:

- `worker_dispatch_artifact`;
- `worker_dispatch_replay_reference`.

The selected append-only destination convention is one lifecycle directory
under the active session root, derived from the dispatch artifact hash:

```text
<runtime-root>/<session>/WORKER-INVOCATION-<last-16-dispatch-hash-characters>
```

The intended and implemented call edge is:

```text
aigol.cli.aicli._record_contextual_execution_decision
  -> aigol.runtime.worker_invocation_runtime.invoke_dispatched_worker
```

Projected production scope was approximately 30–35 insertions with no new
symbol. Actual production scope remained within the 50-line gate.

## Direct binding

After exact successful `WORKER_DISPATCHED`, the existing reference continuation
now passes the exact dispatch artifact and Replay reference to
`invoke_dispatched_worker`.

The call uses:

- exact same-continuation G31-13B dispatch evidence;
- `AIGOL_GOVERNANCE` as governed actor;
- the existing deterministic timestamp;
- one deterministic same-session destination derived from the dispatch hash.

AiCLI does not inspect invocation eligibility, reinterpret authorization,
select a Worker, activate a Provider role, synthesize lineage, or own
invocation policy. The existing certified runtime performs all validation.

## Existing invocation artifacts

The implementation reuses unchanged:

- `WORKER_INVOCATION_EVIDENCE_ARTIFACT_V1`;
- `WORKER_INVOCATION_CLASSIFICATION_ARTIFACT_V1`;
- `WORKER_INVOCATION_ARTIFACT_V1`;
- `WORKER_INVOCATION_RESULT_ARTIFACT_V1`.

No artifact type, schema, version, adapter, or compatibility artifact was
added.

The invocation artifact binds exact:

- dispatch identity and hash;
- assignment identity and hash;
- invocation-request identity and hash;
- authorization identity and hash;
- execution-packet identity and hash;
- Worker identity, hash, family, and role;
- allowed outputs;
- forbidden operations;
- validation requirements;
- canonical chain identity.

## Invocation semantics

For this certified runtime, `WORKER_INVOKED` means immutable governed
invocation lifecycle evidence exists.

It does not mean:

```text
CODEX_PROCESS_STARTED
PROVIDER_INVOKED
COMMAND_EXECUTED
EXECUTION_STARTED
WORKER_RESULT_CREATED
REPOSITORY_MUTATED
```

`invoke_dispatched_worker` contains no subprocess, shell, command runner,
Provider, network client, credentials, Worker adapter, execution runtime,
result runtime, or repository mutator.

It records only the transition:

```text
WORKER_DISPATCHED -> WORKER_INVOKED
```

The implementation does not import or call:

- `bridge_worker_invocation_to_execution_candidate`;
- `start_execution`;
- `capture_worker_result`;
- any Provider or Worker adapter;
- any command runner;
- any repository mutator.

## Replay continuity

The existing invocation runtime writes four immutable ordered wrappers:

```text
000_invocation_evidence_recorded.json
001_invocation_classification_recorded.json
002_invocation_artifact_recorded.json
003_invocation_result_recorded.json
```

`reconstruct_worker_invocation_replay` validates:

- wrapper ordering and wrapper hashes;
- artifact hashes;
- evidence-to-classification continuity;
- classification-to-invocation continuity;
- invocation-to-result continuity;
- dispatch identity and hash;
- chain identity;
- authority flags;
- exact nested dispatch Replay.

Dispatch reconstruction transitively validates assignment, request,
authorization, selection, registry, certification, Project Objective, durable
work, repository grounding, and source-evidence lineage.

No selection, request, authorization, assignment, dispatch, or pre-existing
Replay artifact is modified.

## Deterministic destination and duplicate behavior

The reference continuation constructs:

```text
WORKER-INVOCATION-<dispatch-artifact-hash-suffix>
```

under the same session parent as dispatch Replay. No user-supplied invocation
path or alternate dispatch reference enters the continuation.

The existing append-only runtime rejects destination reuse. Focused and PTY
evidence proved a duplicate invocation returns `FAILED_CLOSED`, creates no
second invocation artifact, and leaves the original reconstructable Replay
hash unchanged.

## Stage-local truth

The successful outer continuation reports:

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

Earlier captures remain truthful for their own stage:

- selection reports assignment, dispatch, and invocation false;
- request reports no assignment, dispatch, invocation, or execution;
- assignment reports assigned true, dispatch and invocation false;
- dispatch reports dispatched true and invocation false;
- only invocation artifacts and the outer continuation report invocation true;
- no stage reports execution, command, result, Provider activation, or
  repository mutation.

## Canonical Presentation

The terminal uses the existing `render_worker_invocation_summary` after the
existing request, assignment, and dispatch renderers.

Observed presentation order:

```text
Certified Worker Selection
Worker Invocation Request
Worker Assignment
Worker Dispatch
Worker Invocation
```

The existing invocation renderer received a bounded wording refinement so it
does not imply that CODEX executed the requested change. It now states:

```text
Worker invocation lifecycle evidence has been recorded.
No Worker process or execution has started.
No command has executed.
No Worker result has been produced.
No repository has been modified.
```

This modifies the existing renderer rather than creating a parallel
presentation system. It adds no semantic decision, route, state transition, or
Human Interface authority.

The earlier selection presentation continues to show:

`selected_role_type: WORKER_ROLE`

## Hybrid-role and authority separation

The complete nested lineage preserves:

```text
resource_id = CODEX
resource_category = HYBRID_PROVIDER_WORKER
selected_role_type = WORKER_ROLE
authority_profile = WORKER_AUTHORIZED_TASK_ONLY
provider_authority = false
provider_invoked = false
```

The existing invocation runtime consumes the already validated Worker identity
and role. It does not resolve CODEX as a Provider, activate Provider authority,
read credentials, or convert historical Provider evidence into current
Provider invocation.

No additional human confirmation, approval, authorization artifact, or policy
engine was created.

AiCLI remains transport and rendering only:

- `aicli_authorizes = false`;
- `aicli_executes = false`;
- `aicli_owns_replay = false`.

## Fail-closed evidence

Focused G31-14B tests prove failure before successful invocation evidence for
changes to:

- dispatch identity;
- assignment hash;
- invocation-request hash;
- authorization hash;
- execution-packet and scope hash;
- Worker identity;
- Worker role;
- selected resource category;
- selected role type;
- selected authority profile;
- registry hash;
- Worker-selection certification hash.

Existing G24 and G31 regressions additionally cover missing/failed dispatch,
reordered or corrupt Replay, unavailable Worker, incompatible Worker,
repository-scope substitution, evidence substitution, Provider-authority
substitution, chain mismatch, prior authority-boundary change, and hash drift.

Failed attempts create no invocation evidence, classification, or invocation
artifact. Existing failure-result behavior remains unchanged and does not
partially invoke work.

The public invocation constructor has no session-root parameter. The reference
continuation eliminates cross-session input by using the exact same-
continuation dispatch capture and constructing one destination beneath the
active session root. No discovery or persistence system was added.

## Real PTY-backed terminal evidence

A disposable Git repository contained exactly:

- `aigol/runtime/human_interface.py`;
- `tests/test_human_interface.py`.

The ordinary request was:

```text
Improve the human interface terminal summary behavior. Include focused tests
and validation.
```

The user supplied no path, JSON, Worker identity, artifact name, capability
name, technical prompt, prepared artifact, or shell bridge. Only contextual
approvals were used.

The real PTY-backed `./aicli` session observed:

1. governed proposal and proposal approval;
2. repository grounding;
3. separate execution review and human decision;
4. execution authorization;
5. CODEX in `WORKER_ROLE` selection;
6. invocation-request creation;
7. assignment;
8. dispatch;
9. invocation lifecycle evidence;
10. truthful stop before process activation or execution.

Invocation reconstruction returned:

```text
invocation_status = WORKER_INVOKED
worker_id = CODEX
worker_invoked = true
execution_started = false
result_created = false
```

A duplicate invocation returned:

```text
invocation_status = FAILED_CLOSED
worker_invocation_artifact = None
worker_invoked = false
original_replay_unchanged = true
```

No execution artifact or Worker-result directory existed.

The disposable source Git object identities remained unchanged:

```text
aigol/runtime/human_interface.py
  1530c8bfa12900ae8f37410cec433026f878979a
tests/test_human_interface.py
  1a46b516c00579cf30a533a46798d78e7da445bc
```

Git status remained clean. The disposable repository, runtime, and transcript
were removed.

## Validation results

Focused validation completed before the full suite:

- focused G31-14B: **15 passed, 0 skipped, 0 failed**;
- G24 invocation request, assignment, dispatch, and invocation: **53 passed,
  0 skipped, 0 failed**;
- G31-10 through G31-13B: **58 passed, 0 skipped, 0 failed**;
- Worker registry, certification, and selection: **40 passed, 0 skipped,
  0 failed**;
- authorization: **60 passed, 0 skipped, 0 failed**;
- Replay: **245 passed, 0 skipped, 0 failed**;
- Human Interface and AiCLI: **42 passed, 0 skipped, 0 failed**;
- Governance: **96 passed, 0 skipped, 0 failed**.

One initial combined focused run produced **60 passed and 1 failed** because a
test searched for the substring `requests` and matched the unrelated variable
name `submitted_requests`. The test was narrowed to actual imports; the same
combined group then passed **61 passed, 0 skipped, 0 failed**. No runtime defect
was involved.

The complete repository suite was run exactly once after focused validation:

- **6,383 passed, 4 skipped, 0 failed**.

Focused counts overlap the complete suite and must not be added together.

Static validation:

- targeted `py_compile`: passed;
- `git diff --check`: passed;
- new-file whitespace checks: passed.

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

The two known hook-drift findings remain visible. G31-14B neither repairs nor
obscures them, and they do not invalidate the bounded invocation-evidence
transition.

## Change-size and minimality accounting

Production:

- modified `aigol/cli/aicli.py`: **30 insertions, 0 deletions**;
- modified `aigol/runtime/worker_invocation_runtime.py`: **5 insertions,
  0 deletions**;
- total: **35 insertions, 0 deletions**;
- no new production file;
- no new public or private production symbol;
- no duplicated validation helper.

`aicli.py` is justified because it already owns the G31 contextual
continuation. Its additions are one existing runtime import, one existing
renderer call, one existing constructor call, deterministic destination
construction, and truthful outer state projection.

`worker_invocation_runtime.py` is justified solely by the explicit terminal
truthfulness requirement. Five wording lines extend the existing canonical
renderer; no invocation logic, validation, state, or authority changed.

Tests:

- added one focused G31-14B file;
- updated three stage-boundary regression files;
- **204 insertions, 5 deletions**.

Documentation:

- added this governance report;
- **885 insertions, 0 deletions**.

The 35 production insertions remain below the 50-line stop condition.

No production module, artifact family, adapter, invocation runtime, execution
bridge, selector, policy engine, authorization system, Replay subsystem,
Worker adapter, Provider integration, command runner, or mutation path was
added.

## Pre-existing unrelated worktree entries

Three empty untracked root files existed before G31-14B began and were
preserved unchanged:

- `WORKER_INVOCATION_ARTIFACT_V1`;
- `WORKER_INVOKED`;
- `invocation`.

They are not part of this implementation or its proposed commit.

## Progress estimates

Evidence-scoped planning estimates remain:

- no-copy/paste conversational governed development: **99%**;
- whole-project progress: **88%**.

The invocation-evidence edge is operational. Complete readiness is not claimed
because post-invocation execution reachability, command boundaries, and
repository-mutation authority have not yet been audited against the exact G31
lineage.

## Exactly one next state

`EXISTING_G24_POST_INVOCATION_EXECUTION_REACHABILITY_UNVERIFIED`

No execution implementation is authorized by this report.

## Complete G31-15A AUDIT_ONLY prompt

```text
# Generation 31-15A — Existing Certified Post-Invocation Execution Reachability Audit

AUDIT_ONLY

Treat Generation 30, committed G31-02 through G31-14B, G31-11A, G31-R01,
G31-12A, G31-13A, and G31-14A as immutable accepted baselines.

G31-14B verdict:

G31_DISPATCH_TO_EXISTING_CERTIFIED_G24_WORKER_INVOCATION_DIRECT_BINDING_OPERATIONAL

Current state:

EXISTING_G24_POST_INVOCATION_EXECUTION_REACHABILITY_UNVERIFIED

Primary priority:

NO_COPY_PASTE_CONVERSATIONAL_GOVERNED_DEVELOPMENT_THROUGH_AICLI

## Safety premise

G31-14B records deterministic `WORKER_INVOKED` lifecycle evidence but starts no
process, command, execution, result, Provider, Worker adapter, or repository
mutation.

This audit is the boundary between invocation evidence and potential execution
or side effects.

Do not:

- create an execution candidate;
- start execution;
- launch CODEX or another Worker process;
- invoke a Provider;
- execute a command;
- create Worker output or results;
- mutate a repository;
- change runtime behavior;
- test external availability through real execution.

Use static inspection, existing fixtures, reconstruction, certification
evidence, and read-only PTY observation only.

## Objective

Determine whether the exact G31-14B `WORKER_INVOCATION_ARTIFACT_V1` and
invocation Replay can enter an existing certified post-invocation execution
lifecycle through:

1. an already operational connection;
2. a direct existing-function binding;
3. a bounded existing-contract projection;
4. no compatible path;
5. unavailable runtime evidence.

Do not assume the next step is `start_execution`. First determine whether the
constitutional path requires
`bridge_worker_invocation_to_execution_candidate`, another execution-
governance entry, an additional bounded human checkpoint, or an explicit
fail-closed stop.

Do not implement execution.

## Audit-only restriction

Do not modify production code, CLI, Human Interface, tests, schemas, canonical
artifact families, authorization policy, Worker/Provider configuration,
Governance, or Replay.

The only permitted repository change is:

docs/governance/G31_15A_EXISTING_CERTIFIED_POST_INVOCATION_EXECUTION_REACHABILITY_AUDIT.md

## Required contract inventory

Locate and document all existing public contracts for:

- invocation-to-execution-candidate bridge;
- `bridge_worker_invocation_to_execution_candidate`;
- candidate approval or authorization requirements;
- execution-governance entry;
- `start_execution`;
- execution evidence, status, result, and Replay;
- Worker process or adapter activation;
- command execution;
- Worker output and result capture;
- filesystem/repository mutation;
- result validation;
- post-execution Replay review;
- completion and termination;
- Canonical Presentation;
- production callers;
- certification evidence and focused tests.

Inspect at minimum:

- `worker_invocation_to_execution_candidate_bridge_runtime.py`;
- `execution_runtime.py`;
- `worker_result_capture_runtime.py`;
- every production caller of `bridge_worker_invocation_to_execution_candidate`;
- every production caller of `start_execution`;
- existing execution and bridge certification evidence;
- existing execution Replay tests.

For each contract report exact input, output, authority owner, Replay owner,
side effects, external dependencies, callers, certification status, and
downstream boundary.

## Required semantic analysis

Determine independently whether each existing contract:

- creates lifecycle evidence only;
- creates an execution candidate;
- requires another human approval;
- grants or consumes execution authority;
- starts a process;
- activates CODEX or another Worker adapter;
- activates a Provider;
- executes a command;
- creates Worker output;
- mutates the target repository;
- depends on an executable, credential, endpoint, network, MCP, or external
  service.

Do not infer semantics from function names.

## Compatibility matrix

Compare the exact G31-14B invocation artifact and Replay against every input of
the existing post-invocation contracts.

Classify every field as exactly one of:

- DIRECTLY_COMPATIBLE;
- COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION;
- AVAILABLE_BUT_NOT_BOUND;
- MISSING;
- INCOMPATIBLE.

Include:

- session identity;
- original goal and Project Objective;
- Durable Governed Work;
- repository grounding and evidence hashes;
- execution summary and human confirmation;
- authorization identity, hash, scope, status, expiry, and Replay;
- G31 selection, registry, and certification;
- CODEX identity, version, category, role, and authority profile;
- request, assignment, dispatch, and invocation identities/hashes/Replays;
- workspace, source paths, test paths, symbols, and mutation layers;
- allowed outputs, forbidden operations, and validation requirements;
- execution-candidate identity and approval requirements;
- execution identity and Replay destination;
- process, command, result, and mutation scope;
- stop-state flags.

## Governance and authorization assessment

Determine whether G31 execution authorization already covers creation of an
execution candidate or execution start, or whether an existing separate
governance/human contract must be consumed.

Do not create or recommend another approval, confirmation, authorization
artifact, or policy engine unless deterministic repository evidence proves an
existing mandatory contract is required.

Distinguish:

- proposal approval;
- distinct execution confirmation;
- execution authorization;
- Worker selection;
- assignment;
- dispatch;
- invocation evidence;
- execution-candidate creation;
- execution start;
- command execution;
- repository mutation.

## Command and mutation boundaries

Determine the exact first point at which any existing path can:

- launch a process;
- run a shell or command;
- activate an external Worker adapter;
- create or modify a file;
- mutate the selected repository;
- create Worker output.

If `start_execution` is evidence-only, prove it. If it necessarily executes a
command or activates a Worker, report that fact. If repository mutation is a
separate downstream runtime, identify it precisely.

Do not cross any of these boundaries during the audit.

## Hybrid-role boundary

Verify whether the existing post-invocation path preserves CODEX exclusively
in `WORKER_ROLE` with `WORKER_AUTHORIZED_TASK_ONLY` and no Provider authority.

Do not activate Provider semantics or convert historical Provider evidence into
current Provider invocation.

## Fail-closed evidence

Inspect existing rejection for:

- missing or failed invocation;
- changed invocation identity, hash, status, artifact, result, or Replay;
- reordered invocation Replay;
- changed dispatch, assignment, request, authorization, or repository scope;
- changed selection, registry, certification, Worker identity, version,
  category, role, or authority profile;
- Provider-role substitution;
- unavailable or incompatible Worker;
- duplicate candidate or execution start;
- cross-session invocation or destination;
- missing required candidate approval;
- command or mutation scope beyond authorization;
- evidence of prior execution, result, mutation, completion, termination, or
  Replay modification.

Do not generate failure evidence through real execution when existing fixtures
already prove it.

## Existing call-chain trace

Trace:

```text
G31-14B invocation capture
  -> invocation validation
  -> candidate bridge, if constitutionally required
  -> execution-governance entry
  -> start_execution, if compatible
  -> exact certified stop boundary
```

Identify exact existing caller, callee, missing call edge or missing field,
whether a direct binding or projection is required, and the first point of
actual process, command, output, or mutation behavior.

## PTY observation

Use a disposable Git repository with one implementation and one focused test.

Through real PTY-backed `./aicli`, submit an ordinary bounded natural-language
request and use only contextual approvals. Verify the accepted lifecycle
reaches G31-14B `WORKER_INVOKED` evidence and stops before execution.

Confirm no execution candidate, execution artifact, command, output, Provider,
Worker process, or repository mutation exists. Confirm source hashes and Git
status remain unchanged. Remove the disposable repository afterward.

Do not execute the Worker merely to test reachability.

## Required verdict

Return exactly one:

- EXISTING_G24_POST_INVOCATION_EXECUTION_ALREADY_OPERATIONALLY_REACHABLE
- EXISTING_G24_POST_INVOCATION_EXECUTION_REUSABLE_DIRECT_BINDING_REQUIRED
- EXISTING_G24_POST_INVOCATION_EXECUTION_REUSABLE_BOUNDED_PROJECTION_REQUIRED
- EXISTING_G24_POST_INVOCATION_EXECUTION_INCOMPATIBLE
- EXISTING_G24_POST_INVOCATION_EXECUTION_RUNTIME_EVIDENCE_BLOCKED

Use `RUNTIME_EVIDENCE_BLOCKED` when contracts are compatible but required
process, executable, credential, Provider, network, or Worker availability
cannot be proven without crossing the audit boundary.

## Minimal future binding

Only if direct binding or projection is proven necessary, provide without
implementing:

- exact caller and callee;
- required intermediate contracts;
- exact artifact families;
- missing fields;
- external requirements;
- projected production files and maximum additions;
- focused tests;
- presentation impact;
- exact stop boundary.

Do not propose an execution implementation until the audit proves whether
execution is evidence-only or side-effecting.

## Validation

Run read-only focused evidence for:

- invocation-to-execution candidate bridge;
- execution runtime;
- G24 request through invocation;
- G31-10 through G31-14B;
- authorization and approval boundaries;
- Worker registry/certification/selection;
- Replay;
- Human Interface and AiCLI;
- Governance;
- py_compile;
- git diff --check.

Run the complete repository suite only if focused evidence conflicts with
certification evidence.

Report exact pass, skip, and failure counts.

## Documentation

Add only:

docs/governance/G31_15A_EXISTING_CERTIFIED_POST_INVOCATION_EXECUTION_REACHABILITY_AUDIT.md

Document contracts, callers, compatibility, authority, candidate requirements,
execution semantics, command/mutation boundaries, external dependencies,
Replay, fail-closed evidence, PTY observation, validation, Governance, exact
first unbound transition, and exactly one next state.

## Required final report

Provide:

1. audit verdict;
2. plain-language conclusion;
3. exact files inspected and created;
4. contract inventory and production callers;
5. exhaustive compatibility matrix;
6. governance and authorization assessment;
7. execution, command, output, and mutation semantics;
8. hybrid-role assessment;
9. external dependency assessment;
10. exact first unbound transition;
11. PTY observation;
12. Replay and fail-closed evidence;
13. exact validation and Governance results;
14. confirmation that runtime behavior did not change;
15. exact Git status and documentation-only commit commands;
16. evidence-scoped progress estimates;
17. exactly one next state;
18. a bounded implementation prompt only if the audit proves one is required.

Do not create a commit.

Architectural minimalism and evidence-first reuse are mandatory.
```

## Conclusion

G31-14B binds exact G31 dispatch to the existing certified invocation-
evidence lifecycle without projection or authority expansion. It truthfully
records `WORKER_INVOKED` while leaving process activation, execution, commands,
Worker output, results, and repository mutation untouched and unclaimed.
