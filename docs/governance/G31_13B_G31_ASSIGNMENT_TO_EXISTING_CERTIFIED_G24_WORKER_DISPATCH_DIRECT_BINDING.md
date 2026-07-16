# Generation 31-13B — G31 Assignment to Existing Certified G24 Worker Dispatch Direct Binding

Status: completed bounded implementation.

Date: 2026-07-16

Implementation verdict:

`G31_ASSIGNMENT_TO_EXISTING_CERTIFIED_G24_WORKER_DISPATCH_DIRECT_BINDING_OPERATIONAL`

Exactly one next state:

`EXISTING_G24_WORKER_INVOCATION_REACHABILITY_UNVERIFIED`

## Constitutional scope

This implementation treats Generation 30, committed G31-02 through G31-12B,
G31-11A, G31-R01, G31-12A, and G31-13A as immutable accepted baselines.

It closes exactly one transition:

```text
valid G31-12B WORKER_ASSIGNMENT_ARTIFACT_V1
  -> existing dispatch_assigned_worker
  -> existing Worker-dispatch artifacts
  -> existing Worker-dispatch Replay
  -> existing render_worker_dispatch_summary
  -> stop before Worker invocation
```

No dispatch runtime, dispatch authorization, assignment runtime, Worker
identity, registry, selector, Provider runtime, Worker invocation, Replay
subsystem, Governance system, Human Interface semantic owner, or canonical
artifact family was created or redesigned.

## Accepted audit evidence

G31-13A concluded:

`EXISTING_G24_WORKER_DISPATCH_REUSABLE_DIRECT_BINDING_REQUIRED`

and established:

`G31_12B_TO_EXISTING_G24_WORKER_DISPATCH_DIRECT_BINDING_READY`

The audit proved that the existing dispatcher accepts the exact
`WORKER_ASSIGNMENT_ARTIFACT_V1` and assignment Replay emitted by G31-12B. No
compatibility projection was required.

## Mandatory pre-implementation check

The implementation inspected the public dispatcher contract before editing.

Exact public signature:

```python
dispatch_assigned_worker(
    *,
    worker_dispatch_id: str,
    worker_assignment_artifact: dict[str, Any],
    worker_assignment_replay_reference: str,
    dispatched_by: str,
    dispatched_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]
```

Existing callers were found in:

- legacy interactive lifecycle continuations in `aigol/cli/aigol_cli.py`;
- `_continue_worker_request_to_replay_certification`;
- domain approval/resume flows;
- `aigol/runtime/g5_pgsp_worker_runtime_orchestration.py`;
- existing dispatch, invocation, result, and certification tests.

The existing Platform Core/Governance dispatcher identity is:

`AIGOL_GOVERNANCE`

The exact required inputs already existed in the G31-12B assignment capture:

- `worker_assignment_artifact`;
- `worker_assignment_replay_reference`.

The selected append-only destination convention is one lifecycle directory
under the active session root, derived from the assignment artifact hash:

```text
<runtime-root>/<session>/WORKER-DISPATCH-<last-16-assignment-hash-characters>
```

The intended and implemented call edge is:

```text
aigol.cli.aicli._record_contextual_execution_decision
  -> aigol.runtime.worker_dispatch_runtime.dispatch_assigned_worker
```

Projected production scope was one existing file and fewer than 50 added
lines. Actual production scope remained within that gate.

## Exact existing function reuse

The existing reference AiCLI continuation now calls:

`aigol.runtime.worker_dispatch_runtime.dispatch_assigned_worker`

only after the existing assignment capture reports exact `WORKER_ASSIGNED`.

The call passes:

- the exact assignment artifact returned in that continuation;
- the exact assignment Replay reference returned in that continuation;
- `AIGOL_GOVERNANCE` as the existing dispatcher identity;
- the existing deterministic timestamp;
- a deterministic same-session append-only path derived from the assignment
  hash.

AiCLI does not inspect dispatch eligibility, select a dispatch policy, modify
the assignment, synthesize lineage, choose a Worker, or authorize dispatch.
Eligibility and lineage validation remain inside the certified G24 dispatcher.

## Existing dispatch artifacts

The implementation reuses unchanged:

- `WORKER_DISPATCH_EVIDENCE_ARTIFACT_V1`;
- `WORKER_DISPATCH_CLASSIFICATION_ARTIFACT_V1`;
- `WORKER_DISPATCH_ARTIFACT_V1`;
- `WORKER_DISPATCH_RESULT_ARTIFACT_V1`.

No new artifact type, schema, version, or adapter was introduced.

The successful dispatch artifact binds the exact:

- assignment identity and hash;
- invocation-request identity and hash;
- authorization identity and hash;
- execution-packet identity and hash;
- Worker identity and hash;
- Worker family and role;
- allowed outputs;
- forbidden operations;
- validation requirements;
- canonical chain identity.

## Replay continuity

The dispatcher writes its existing four-step immutable Replay:

```text
000_dispatch_evidence_recorded.json
001_dispatch_classification_recorded.json
002_dispatch_artifact_recorded.json
003_dispatch_result_recorded.json
```

`reconstruct_worker_dispatch_replay` validates ordered wrapper hashes,
artifact hashes, classification lineage, dispatch lineage, assignment
identity, chain identity, authority flags, and the nested assignment Replay.

The nested assignment reconstruction reloads the invocation request, which in
turn reconstructs the G31 authorization, selection, registry, certification,
Project Objective, durable work, repository grounding, and evidence chain.

No pre-existing selection, request, authorization, assignment, or Replay
artifact is modified.

## Deterministic destination and duplicate behavior

The reference continuation constructs:

```text
WORKER-DISPATCH-<assignment-artifact-hash-suffix>
```

inside the same session directory that owns the assignment Replay. The caller
does not accept a user-supplied assignment reference or dispatch destination,
so a cross-session destination is not an interface input. Focused and PTY
evidence confirm that the assignment and dispatch Replay directories have the
same session parent.

The existing append-only dispatcher rejects reuse of the deterministic
destination. Duplicate validation produced `FAILED_CLOSED`, created no second
dispatch artifact, and left the original reconstructable Replay hash
unchanged.

## Stage truthfulness

The successful outer continuation reports:

```text
worker_selected = true
worker_assigned = true
worker_dispatched = true
provider_invoked = false
worker_invoked = false
command_executed = false
repository_mutated = false
```

Earlier stages retain their own truthful boundaries:

- the selection capture reports `worker_assigned = false` and
  `worker_dispatched = false`;
- the invocation-request capture reports no assignment, dispatch, invocation,
  or execution;
- the assignment capture reports `worker_assigned = true` and
  `worker_dispatched = false`;
- only the outer continuation and dispatch capture report
  `worker_dispatched = true`;
- no stage reports Provider or Worker invocation.

The operational presentation marker `authorization_dispatch_blocked` changes
to false only when the existing dispatcher returns exact `WORKER_DISPATCHED`.
It remains true for failed dispatch.

## Canonical Presentation

After the existing request and assignment renderers, AiCLI calls the existing:

`render_worker_dispatch_summary`

The observed order is:

```text
Worker Invocation Request
Worker Assignment
Worker Dispatch
```

The dispatch renderer reports the dispatch status, dispatch reference,
assignment reference, CODEX identity, and Replay reference. It also states:

```text
No Worker has been invoked, executed, or produced results.
```

No new presentation semantic or Human Interface decision was added.

## Dispatch versus invocation

Dispatch records delivery of an already assigned task into the certified
dispatch lifecycle. It is not Worker execution.

The implementation does not import or call:

`invoke_dispatched_worker`

It creates no Worker invocation artifact, execution artifact, command,
result, validation result, completion result, or mutation record.

Focused source inspection found exactly one new AiCLI dispatcher call and no
Worker-invocation call. PTY evidence found no Worker-invocation lifecycle
directory.

## Hybrid-role and authority separation

The nested certified selection remains:

```text
resource_id = CODEX
resource_category = HYBRID_PROVIDER_WORKER
selected_role_type = WORKER_ROLE
authority_profile = WORKER_AUTHORIZED_TASK_ONLY
provider_authority = false
provider_invoked = false
```

The dispatch transition consumes the resulting assignment. It does not
activate CODEX's Provider role, select a Provider, invoke a Provider, or alter
the selected authority profile.

Proposal approval, distinct execution confirmation, execution authorization,
selection, assignment, and dispatch remain separate lifecycle facts. G31-13B
creates no additional approval or authorization artifact.

AiCLI remains transport and rendering only:

- `aicli_authorizes = false`;
- `aicli_executes = false`;
- `aicli_owns_replay = false`.

## Fail-closed evidence

Focused tests proved rejection before successful dispatch creation for changes
to:

- assignment identity;
- invocation-request hash;
- authorization hash;
- execution-packet and repository-scope lineage;
- Worker identity;
- Worker family;
- Worker role;
- selected resource category;
- selected role type;
- selected authority profile;
- Worker registry hash;
- Worker-selection certification hash.

Existing G24 and G31 regressions additionally cover missing or failed
assignment, stale or reordered Replay, unavailable or incompatible Worker,
scope and source-evidence substitution, Provider-authority substitution,
wrapper/hash corruption, chain substitution, and authority-boundary changes.

Failed attempts create no dispatch evidence, classification, or dispatch
artifact. Existing failure-result behavior remains unchanged and does not
partially dispatch work.

## Real PTY-backed terminal evidence

A disposable Git repository was created with exactly:

- `aigol/runtime/human_interface.py`;
- `tests/test_human_interface.py`.

The ordinary request was:

```text
Improve the human interface terminal summary behavior. Include focused tests
and validation.
```

The user supplied no paths, JSON, Worker identity, capability name, prepared
artifact, technical prompt, or shell bridge. Only contextual `/approve`
decisions were used.

The real PTY-backed `./aicli` session observed:

1. G31-04 proposal and proposal approval;
2. G31-05 goal-faithful Worker payload;
3. G31-06 exact repository grounding;
4. G31-08 authorization review;
5. G31-09 distinct human execution decision;
6. G31-10 execution authorization;
7. G31-11B CODEX in `WORKER_ROLE` selection;
8. G31-12B invocation request and assignment;
9. G31-13B existing G24 `WORKER_DISPATCHED`;
10. canonical request, assignment, and dispatch presentation;
11. truthful stop before Worker invocation.

The disposable repository source object identities before and after were:

```text
aigol/runtime/human_interface.py
  15600200434f0ccc4f69df6b442e0022f2305205
tests/test_human_interface.py
  1a46b516c00579cf30a533a46798d78e7da445bc
```

Both remained unchanged. Git status remained clean.

Dispatch reconstruction returned:

```text
dispatch_status = WORKER_DISPATCHED
worker_id = CODEX
worker_invoked = false
execution_started = false
result_created = false
```

A duplicate call against the same deterministic destination returned:

```text
dispatch_status = FAILED_CLOSED
worker_dispatch_artifact = None
worker_dispatched = false
original_replay_unchanged = true
```

No Worker-invocation directory existed. The disposable repository, runtime,
and transcript were removed after validation.

## Validation results

Focused validation completed before the full suite:

- focused G31-13B: **15 passed, 0 skipped, 0 failed**;
- G24 invocation request, assignment, and dispatch: **37 passed, 0 skipped,
  0 failed**;
- G31-10 through G31-12B: **43 passed, 0 skipped, 0 failed**;
- Worker runtime, certification, and unified selection: **40 passed,
  0 skipped, 0 failed**;
- authorization: **60 passed, 0 skipped, 0 failed**;
- Replay: **245 passed, 0 skipped, 0 failed**;
- Human Interface and AiCLI: **42 passed, 0 skipped, 0 failed**;
- Governance: **96 passed, 0 skipped, 0 failed**.

The complete repository suite was run exactly once after focused suites passed:

- **6,368 passed, 4 skipped, 0 failed**.

Focused counts overlap the complete suite and must not be added together.

Static validation:

- targeted `py_compile`: passed;
- `git diff --check`: passed.

## Governance result

Repository governance remains:

`PARTIALLY_CONFORMANT`

The deterministic read-only conformance engine reports:

- checks passed: 18;
- checks failed: 2;
- critical violations: 0;
- deterministic: true;
- fail-closed: true;
- read-only: true.

The two pre-existing hook-drift findings remain visible. G31-13B neither
repairs nor obscures them, and they do not invalidate the bounded dispatch
transition.

## Change-size and minimality accounting

Production:

- modified `aigol/cli/aicli.py`;
- **32 insertions, 0 deletions**;
- no new production file;
- no new public or private production symbol;
- no duplicated validation helper.

The single production file is justified because it already owns the G31
contextual continuation. Its additions are limited to the existing runtime
module import, one existing renderer call, one existing dispatcher call, and
truthful capture/state projection.

Tests:

- modified two stage-boundary regression files;
- added one focused G31-13B test file;
- **195 insertions, 4 deletions**.

Documentation:

- added this governance report;
- **722 insertions, 0 deletions**.

The 32 production insertions are below the 50-line stop condition. No runtime
line was removed. No production module, canonical artifact family, public
symbol, dispatcher, adapter, selector, policy engine, authorization system,
Replay subsystem, or repository-discovery mechanism was added.

## Progress estimates

Evidence-scoped planning estimates are now:

- no-copy/paste conversational governed development: **99%**;
- whole-project progress: **88%**.

The dispatch edge is operational. These estimates do not claim complete
readiness because existing certified Worker-invocation reachability has not
yet been audited against the exact G31-13B dispatch artifact and boundaries.

## Exactly one next state

`EXISTING_G24_WORKER_INVOCATION_REACHABILITY_UNVERIFIED`

No Worker-invocation implementation is authorized by this report.

## Complete G31-14A AUDIT_ONLY prompt

```text
# Generation 31-14A — Existing Certified G24 Worker Invocation Reachability Audit

AUDIT_ONLY

Treat Generation 30, committed G31-02 through G31-13B, G31-11A, G31-R01,
G31-12A, and G31-13A as immutable accepted baselines.

G31-13B verdict:

G31_ASSIGNMENT_TO_EXISTING_CERTIFIED_G24_WORKER_DISPATCH_DIRECT_BINDING_OPERATIONAL

Current next state:

EXISTING_G24_WORKER_INVOCATION_REACHABILITY_UNVERIFIED

Primary priority:

NO_COPY_PASTE_CONVERSATIONAL_GOVERNED_DEVELOPMENT_THROUGH_AICLI

## Objective

Audit whether the exact G31-13B WORKER_DISPATCH_ARTIFACT_V1 and dispatch Replay
can reach an already certified G24 Worker-invocation lifecycle through direct
reuse, a bounded existing-contract projection, or not at all.

Do not implement Worker invocation.
Do not invoke a Worker or Provider.
Do not execute a command.
Do not mutate a repository.
Do not change runtime behavior.

The only permitted repository change is:

docs/governance/G31_14A_EXISTING_CERTIFIED_G24_WORKER_INVOCATION_REACHABILITY_AUDIT.md

## Required audit

Locate and document the exact existing contracts for:

- Worker-invocation entry and constructor;
- Worker-invocation evidence, classification, artifact, result, and Replay;
- Worker-dispatch artifact and Replay inputs;
- invocation eligibility and authorization validation;
- Worker identity, availability, role, and authority validation;
- duplicate-invocation prevention;
- invocation Replay reconstruction;
- Canonical Presentation;
- downstream execution, command, result, validation, and mutation boundaries.

Inspect the public signature and every production caller of the existing
Worker-invocation constructor. Determine whether the reference AiCLI is
already a caller.

## Compatibility matrix

Compare the exact G31-13B dispatch output with every existing invocation
input. Classify every required field as exactly one of:

- DIRECTLY_COMPATIBLE;
- COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION;
- AVAILABLE_BUT_NOT_BOUND;
- MISSING;
- INCOMPATIBLE.

At minimum compare:

- session identity;
- original goal and Project Objective;
- Durable Governed Work and repository grounding;
- execution summary and distinct human confirmation;
- execution-authorization identity, hash, and Replay;
- G31 Worker selection, registry, and certification evidence;
- CODEX identity and version;
- HYBRID_PROVIDER_WORKER category;
- WORKER_ROLE;
- WORKER_AUTHORIZED_TASK_ONLY authority profile;
- provider_authority and provider_invoked flags;
- invocation-request identity, hash, and Replay;
- assignment identity, hash, and Replay;
- dispatch identity, hash, status, and Replay;
- workspace, paths, symbols, tests, evidence hashes, and mutation layers;
- allowed outputs, forbidden operations, and validation requirements;
- invocation identity and deterministic Replay destination;
- invocation stop-state flags.

Do not infer compatibility from names. Prove it through public constructors,
validators, reconstructors, callers, certification evidence, and focused
tests.

## Required questions

Determine:

1. Does an existing certified Worker-invocation runtime exist?
2. Does it accept the exact G31-13B dispatch artifact and Replay unchanged?
3. Does invocation mean lifecycle evidence creation, actual Worker activation,
   command execution, or some combination?
4. Does it preserve the exact authorization, repository scope, selection,
   request, assignment, dispatch, and Worker lineage?
5. Does it preserve CODEX in WORKER_ROLE without activating Provider authority?
6. Does it stop before execution, command, result creation, and repository
   mutation?
7. Does it reject stale, substituted, reordered, duplicate, cross-session,
   unavailable, incompatible, or Provider-role evidence?
8. Is the existing invocation renderer sufficient for Canonical Presentation?
9. Is the reference ./aicli already operationally bound to it?
10. What is the exact first missing call edge, if any?

## Authority boundary

Audit and preserve the distinctions:

- proposal approval is not execution authorization;
- execution authorization is not Worker selection;
- selection is not assignment;
- assignment is not dispatch;
- dispatch is not Worker invocation;
- Worker invocation is not command execution or repository mutation unless
  deterministic existing evidence explicitly proves otherwise.

Do not reinterpret historical Provider/Worker evidence as current invocation.
Do not activate CODEX's Provider role.

## Fail-closed evidence

Inspect deterministic rejection for:

- changed G31-04 through G31-13B identities or hashes;
- missing or failed dispatch;
- changed dispatch identity, hash, status, or Replay;
- reordered assignment or dispatch Replay;
- changed authorization, scope, selection, registry, certification, request,
  assignment, Worker identity, version, category, role, or authority profile;
- unavailable or incompatible Worker;
- Provider-role substitution;
- duplicate invocation;
- cross-session dispatch or invocation destination;
- prior execution, command, result, validation, mutation, or Replay mutation.

Do not perform an actual Worker or Provider invocation during this audit.
Use read-only constructor inspection, existing fixtures, reconstruction, and
certification evidence.

## Minimality audit

Determine the smallest justified future binding, if one is required.

Prefer:

exact G31-13B dispatch capture
  -> existing public invocation function
  -> existing invocation artifacts and Replay
  -> existing renderer
  -> existing certified stop boundary

Do not propose a new invocation runtime, adapter, artifact family, selector,
authorization system, policy engine, Replay subsystem, or discovery framework
unless deterministic evidence proves the existing contract is incompatible.

Report the projected production files, new symbols, and maximum justified
line additions for any later implementation. Do not implement them.

## PTY observation

Use a disposable Git repository with one implementation and one focused test.

Through real PTY-backed ./aicli, submit one ordinary bounded natural-language
request and verify that the current accepted lifecycle reaches G31-13B
WORKER_DISPATCHED and stops before Worker invocation.

The user must not provide paths, JSON, Worker identities, artifact names,
technical prompts, prepared artifacts, or shell bridges.

Confirm source hashes and Git status remain unchanged. Remove the disposable
repository afterward.

Do not invoke the Worker merely to test reachability.

## Validation

Run read-only focused evidence for:

- existing G24 Worker invocation;
- Worker dispatch and assignment;
- G31-10 through G31-13B;
- Worker registry, certification, and selection;
- authorization;
- Replay;
- Human Interface and AiCLI;
- Governance;
- py_compile;
- git diff --check.

Run the full repository suite only if focused evidence is inconsistent or the
audit uncovers a deterministic runtime conflict.

Report exact pass, skip, and failure counts.

## Required verdict

Return exactly one:

- EXISTING_G24_WORKER_INVOCATION_ALREADY_OPERATIONALLY_REACHABLE
- EXISTING_G24_WORKER_INVOCATION_REUSABLE_DIRECT_BINDING_REQUIRED
- EXISTING_G24_WORKER_INVOCATION_REUSABLE_BOUNDED_PROJECTION_REQUIRED
- EXISTING_G24_WORKER_INVOCATION_INCOMPATIBLE
- EXISTING_G24_WORKER_INVOCATION_RUNTIME_EVIDENCE_BLOCKED

## Documentation

Add only:

docs/governance/G31_14A_EXISTING_CERTIFIED_G24_WORKER_INVOCATION_REACHABILITY_AUDIT.md

Document contracts, callers, certification evidence, compatibility matrix,
authority semantics, invocation-versus-execution boundaries, Replay,
fail-closed behavior, PTY observation, validation, governance, exact missing
edge, minimal future binding, and exactly one next readiness state.

## Required final report

Provide:

1. audit verdict;
2. plain-language conclusion;
3. exact files inspected and created;
4. existing invocation contracts and callers;
5. exhaustive compatibility matrix;
6. invocation semantics and stop boundary;
7. Replay and tamper evidence;
8. hybrid-role and authority assessment;
9. PTY observation;
10. exact validation and Governance results;
11. exact git status and documentation-only commit commands;
12. evidence-scoped progress estimates;
13. exactly one next readiness state;
14. a bounded implementation prompt only if the audit proves one is required.

Do not create a commit.

Architectural minimalism and evidence-first reuse are mandatory.
```

## Conclusion

G31-13B operationally binds the exact G31-12B assignment to the existing
certified G24 dispatch lifecycle with no projection and no authority expansion.
The dispatcher, artifacts, Replay, validation, duplicate protection, and
renderer remain unchanged. The reference AiCLI now truthfully reaches
`WORKER_DISPATCHED` and stops before Provider or Worker invocation, command
execution, result creation, or repository mutation.
