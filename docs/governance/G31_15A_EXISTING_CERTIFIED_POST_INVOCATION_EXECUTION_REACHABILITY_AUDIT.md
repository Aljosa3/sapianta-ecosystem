# Generation 31-15A — Existing Certified Post-Invocation Execution Reachability Audit

Status: completed audit; no runtime behavior changed.

Date: 2026-07-17

Audit verdict:

`EXISTING_G24_POST_INVOCATION_EXECUTION_REUSABLE_BOUNDED_PROJECTION_REQUIRED`

Exactly one next state:

`G31_INVOCATION_TO_EXISTING_EXECUTION_CANDIDATE_BOUNDED_PROJECTION_REQUIRED`

## Scope and conclusion

This audit treats Generation 30 and accepted G31-02 through G31-14B evidence
as immutable baselines. It preserves the distinction established by G31-14B:
`WORKER_INVOKED` is immutable lifecycle evidence; it does not prove that a
Worker process, Provider, command, output, execution, or repository mutation
occurred.

The exact G31-14B invocation is not already connected to post-invocation
execution. The first constitutionally ordered downstream contract is the
existing invocation-to-execution-candidate bridge, not `start_execution`.
That bridge and its candidate-only Replay are reusable, but the exact G31
lineage needs one bounded projection because:

1. the bridge requires an existing `HUMAN_APPROVAL_ARTIFACT_V1` scoped only to
   `CREATE_WORKER_EXECUTION_CANDIDATE_FROM_INVOCATION_ONLY`, bound to the exact
   invocation identity and hash;
2. its legacy execution-ready input expects `upstream_lineage_reference` and
   `upstream_lineage_hash` directly, while G31 stores the authentic PPP
   candidate under the validated approved-payload and repository-grounding
   lineage;
3. direct `start_execution` would skip the required post-invocation candidate
   and would not consume the full G31 authorization, grounding, selected-role,
   and candidate-approval evidence.

All missing values exist in immutable G31 evidence. No executable, credential,
endpoint, network, MCP, Provider, or live Worker is needed to create and
reconstruct the candidate. The immediate blocker is therefore bounded
projection, not external runtime evidence.

## Constitutional evidence

The audit applied:

- `CONSTITUTIONAL_INVARIANTS.md`: proposal review is not execution and missing
  certification evidence must not be synthesized;
- `GOVERNANCE_ENFORCEMENT_HIERARCHY.md`: Replay, mutation scope, certification,
  and required human approval precede execution;
- `G30_FINAL_CONSTITUTIONAL_CLOSURE_REPORT.md`: AiCLI remains a thin transport
  and renderer; Worker, Provider, authorization, mutation, and Replay authority
  remain separate;
- G31-10 through G31-14B: two human decisions, exact grounded authorization,
  CODEX selected as `WORKER_ROLE`, assignment, dispatch, and invocation evidence
  are accepted and immutable.

## Contract and production-caller inventory

### Files inspected

The read-only trace covered `aigol/cli/aicli.py`, `aigol/cli/aigol_cli.py`, and
the runtime modules for Worker invocation, invocation-to-candidate bridging,
execution start, governed execution, external task adaptation, universal and
OpenAI Provider adaptation, result capture, validation-command execution,
repository mutation, confirmed grounded authorization, and approved-payload
binding. It also covered their focused tests; G24 and G31-10 through G31-14B
tests; Replay, Human Interface, AiCLI, authorization, selection, registry, and
Governance tests; the execution and result-capture certifications; and the
constitutional and accepted Generation reports cited above.

| Contract | Public symbol and canonical I/O | Production caller(s) | Authority, side effects, status, stop |
|---|---|---|---|
| Invocation validation | `worker_invocation_runtime.reconstruct_worker_invocation_replay(replay_dir)`; four invocation wrappers -> reconstructed `WORKER_INVOKED` | G31-14B and downstream validators | Replay-owned validation only; reads evidence; invocation runtime is accepted G24/G31 baseline; stops before execution |
| Invocation -> candidate | `worker_invocation_to_execution_candidate_bridge_runtime.bridge_worker_invocation_to_execution_candidate(...)`; exact invocation, invocation Replay, scoped `HUMAN_APPROVAL_ARTIFACT_V1` -> `WORKER_EXECUTION_CANDIDATE_ARTIFACT_V1` plus three wrappers | `aigol_cli._continue_worker_request_to_replay_certification` | Governance creates candidate-only evidence; immutable Replay writes only; implemented and focused-tested; no standalone certification JSON was located; stops before execution, Provider, result, command, or mutation |
| Older invocation-candidate governance | `worker_invocation_to_execution_governance_runtime.create_worker_execution_candidate(...)`; `WORKER_INVOCATION_CANDIDATE_ARTIFACT_V1` plus approval -> worker execution candidate | No production caller located | Different legacy source artifact; candidate-only Replay; not a truthful direct G31 input |
| Execution start | `execution_runtime.start_execution(...)`; invocation, invocation result, dispatch, assignment, chain, metadata/context -> `EXECUTION_ARTIFACT_V1` in `EXECUTING` | `aigol_cli._record_authorized_worker_execution_start`; `g5_pgsp_worker_runtime_orchestration._run_worker_stack` | AiGOL records execution-start evidence only; writes two Replay wrappers; explicitly certified by `governance/EXECUTION_RUNTIME_V1_CERTIFICATION.json`; no process, command, output, Provider, or mutation; stops before completion/result |
| Governed deterministic execution | `governed_worker_execution_runtime.run_governed_worker_execution(...)`; worker execution candidate plus separate `RUN_GOVERNED_WORKER_EXECUTION_ONLY` approval -> deterministic execution-result evidence | No production caller located | Requires another existing approval contract; synthesizes no subprocess or Provider work; no code mutation; not the immediate G31 callee |
| External task creation | `external_worker_adapter_runtime.create_external_worker_task_package(...)`; candidate plus `CREATE_EXTERNAL_WORKER_TASK_PACKAGE_ONLY` approval -> provider-neutral task package | `aigol_cli._continue_worker_request_to_replay_certification` | Candidate consumer; Replay writes only; stops before Provider selection/invocation |
| Provider activation | `universal_provider_worker_runtime.run_universal_provider_worker_runtime(...)` -> `openai_external_worker_provider_adapter.run_openai_external_worker_provider_adapter(...)` | `aigol_cli._continue_worker_request_to_replay_certification` | First existing downstream Provider boundary; selects `PROVIDER_ROLE` and can call a certified OpenAI attachment; requires client/key/model/endpoint availability; forbidden for the current CODEX `WORKER_ROLE` transition |
| Execution result capture | `worker_result_capture_runtime.capture_worker_result(...)`; invocation, bounded output, and optional execution binding -> `WORKER_RESULT_CAPTURE_ARTIFACT_V1` | `aigol_cli` result-capture continuations; G5 orchestration | Captures supplied output but does not produce it; certified by `governance/AIGOL_WORKER_RESULT_CAPTURE_RUNTIME_CERTIFICATION.json`; stops before semantic validation/review/termination |
| Command execution | `validation_command_runner_runtime.execute_validation_command(...)` -> `_execute_request` | No G31 post-invocation caller located | First inspected real process/command boundary: `subprocess.run(..., shell=False)`; requires an allowlisted command; not reachable from G31-14B |
| Repository mutation | `repository_mutation_worker_runtime.run_repository_mutation_worker(...)` -> `_apply_planned_mutations` | No G31 post-invocation caller located | First inspected repository-write boundary: `Path.write_text`; requires certified Worker result and approved mutation proposal; not reachable and expressly forbidden by current G31 scope |

Canonical Presentation already exists for invocation, execution start, and
result capture. AiCLI currently renders invocation and stops. Candidate bridge
presentation is not bound into AiCLI and is a bounded G31-15B concern.

## Compatibility matrix

| Required evidence | Classification | Deterministic reason |
|---|---|---|
| Session and Project Objective identity | `AVAILABLE_BUT_NOT_BOUND` | Present in G31 decision, scope, and Replay; the legacy bridge does not project session/objective fields |
| Durable Governed Work and approved plan | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Exact identities/hashes exist in `approved_work_lineage` and validated payload binding |
| Repository grounding and evidence hashes | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Exact grounding artifact is embedded beneath the G31 review/decision and has public validators/reconstructor |
| Execution summary and second human confirmation | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Exact summary/confirmation hashes are consumed by existing execution authorization; bridge needs a candidate-only approval view, not a third decision |
| Authorization identity, status, scope, expiry, hash, Replay | `DIRECTLY_COMPATIBLE` for lineage; `AVAILABLE_BUT_NOT_BOUND` for full candidate scope | Invocation carries authorization id/hash and request Replay reaches the exact authorization; candidate bridge only copies a narrower legacy scope |
| CODEX id, hash, family, `WORKER_ROLE` | `DIRECTLY_COMPATIBLE` | Invocation fields and hashes are native bridge inputs |
| CODEX version, `HYBRID_PROVIDER_WORKER`, `WORKER_AUTHORIZED_TASK_ONLY` | `AVAILABLE_BUT_NOT_BOUND` | Exact values are in selected-resource/assignment Replay and transitively hash-bound; legacy candidate exposes only id/hash/family/role |
| Request, assignment, dispatch, invocation lineage | `DIRECTLY_COMPATIBLE` | Exact references/hashes and ordered Replay are bridge inputs |
| Workspace, source paths, focused tests, mutation layers | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Exact G31 authorization scope contains them; invocation directly carries allowed paths and validations but not the full structured scope |
| Allowed outputs and forbidden operations | `DIRECTLY_COMPATIBLE` | Invocation carries exact lists; current scope forbids Provider invocation, command execution, and repository mutation |
| Authentic PPP candidate identity/hash | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Exists as `ppp_task_package_artifact` under the validated G31 payload; absent as the legacy direct `upstream_lineage_*` fields |
| Candidate approval | `MISSING` as a bridge input; source decision is available | No invocation-bound candidate-only `HUMAN_APPROVAL_ARTIFACT_V1` exists; it must be projected from the already approved G31 authorization without another human decision |
| Execution metadata/context and destination | `AVAILABLE_BUT_NOT_BOUND` | `start_execution` requires non-empty maps and a destination; no G31 binding exists and it is downstream of candidate creation |
| Command, output, result, mutation scope | `INCOMPATIBLE` with current execution authority | Current G31 forbidden operations include `EXECUTE_COMMAND` and `MUTATE_REPOSITORY`; no Worker output exists |
| Stop flags | `DIRECTLY_COMPATIBLE` | Invocation and outer runtime preserve Worker invoked true and execution/result/mutation false |

## Authority and human-decision assessment

The strict two-decision model remains intact:

```text
proposal approval
-> grounded execution confirmation
-> execution authorization
-> Worker selection/assignment/dispatch/invocation evidence
-> post-invocation candidate projection (missing)
```

The existing second human decision already confirmed the exact grounded scope,
and G31-10 created an `EXECUTION_AUTHORIZED`, non-transferable, non-recursive
authorization. Candidate creation itself neither executes nor broadens scope.
G31-15B must therefore project that existing decision into the bridge's
candidate-only approval family; it must not request or synthesize a third human
decision.

That authorization permits continued governed lifecycle preparation within the
exact scope. It does not permit Provider activation, command execution, or
repository mutation. The execution-ready packet explicitly lists
`INVOKE_PROVIDER`, `EXECUTE_COMMAND`, and `MUTATE_REPOSITORY` as forbidden.
`start_execution` records an evidence state only, but it is still not the
immediate callee because it would bypass post-invocation candidate governance.

The exact current call chain is:

```text
aigol.cli.aicli._record_contextual_execution_decision
-> worker_invocation_runtime.invoke_dispatched_worker
-> WORKER_INVOKED
-> stop
```

The first unbound transition is from that exact invocation artifact and Replay
to
`worker_invocation_to_execution_candidate_bridge_runtime.bridge_worker_invocation_to_execution_candidate`.
The mandatory intermediate is the bounded, non-authorizing projection of the
existing G31 decision and authentic nested PPP lineage into the bridge's
existing inputs.

## Side-effect and external boundaries

- Candidate bridge: immutable new Replay evidence only.
- `start_execution`: immutable new `EXECUTING` Replay evidence only; no Worker
  process is activated.
- Governed deterministic execution: deterministic result evidence only;
  `subprocess_invoked` and `provider_invoked` remain false.
- First Provider boundary: universal Provider Worker -> certified OpenAI
  attachment; not valid for current `WORKER_ROLE` and not needed for G31-15B.
- First real command/process boundary inspected: validation command runner's
  `subprocess.run`; no G31 caller exists.
- No CODEX `WORKER_ROLE` output-producing boundary is connected to G31. The
  OpenAI Provider adapter can receive external Provider output, but that is a
  different, forbidden role path. `capture_worker_result` is the first existing
  result-artifact boundary: it records supplied output and does not produce it.
- First repository-mutation boundary inspected: repository mutation Worker's
  `Path.write_text`; no G31 caller exists.
- No existing production contract was found that starts a CODEX Worker process
  from the G31-14B artifact. External CODEX availability is downstream and was
  not tested.

Hybrid-role continuity is exact:

```text
resource_category = HYBRID_PROVIDER_WORKER
selected_role_type = WORKER_ROLE
authority_profile = WORKER_AUTHORIZED_TASK_ONLY
provider_authority = false
provider_invoked = false
```

## Replay and fail-closed evidence

Existing reconstruction rejects missing, failed, duplicated, changed, or
cross-lineage invocation; invalid wrapper hashes/order; dispatch, assignment,
request, authorization, execution-packet, Worker, registry, certification, or
role substitution; Provider-role substitution; duplicate candidate or
execution destinations; invalid output scope; and stale/substituted execution
evidence. Candidate creation fails closed without exact explicit approval.

The G31 path additionally reconstructs authorization, selection, request,
assignment, dispatch, invocation, repository grounding, scope hashes, and the
two human decisions. No partial authorization or execution is produced after a
failed validation.

## PTY observation

A real PTY-backed `./aicli` session used a disposable Git repository containing
one implementation and one focused test. The operator supplied only:

```text
Improve the human interface terminal summary behavior.
Include focused tests and validation.
/send
/approve
/approve
/exit
```

It reached proposal approval, exact grounding, the distinct execution decision,
execution authorization, CODEX `WORKER_ROLE` selection, request, assignment,
dispatch, and `WORKER_INVOKED`. Terminal presentation truthfully reported no
Worker process/execution, command, result, or repository modification.

Observed outer state was:

```text
worker_invoked = true
provider_invoked = false
execution_started = false
command_executed = false
result_created = false
repository_mutated = false
```

Invocation Replay reconstructed four ordered artifacts with status
`WORKER_INVOKED`. No `WORKER_EXECUTION_CANDIDATE_ARTIFACT_V1`,
`EXECUTION_ARTIFACT_V1`, execution directory, or result directory existed.
The earlier G31-10 preparation artifact named `EXECUTION_CANDIDATE_ARTIFACT_V1`
remained distinguishable from the absent post-invocation Worker candidate.
Source Git object hashes were unchanged and Git status remained clean. The
disposable repository and runtime were removed.

## Validation and Governance

Focused validation (groups overlap and are not additive):

| Suite | Result |
|---|---|
| Candidate bridge, execution runtime, result capture | 38 passed, 0 skipped, 0 failed |
| G24 request through invocation | 53 passed, 0 skipped, 0 failed |
| G31-10 through G31-14B | 73 passed, 0 skipped, 0 failed |
| Approval and execution authorization boundaries | 84 passed, 0 skipped, 0 failed |
| Worker selection/registry/certification surface | 31 passed, 0 skipped, 0 failed |
| Replay-selected repository tests | 1,101 passed, 0 skipped, 0 failed; 5,284 deselected |
| Human Interface and AiCLI | 42 passed, 0 skipped, 0 failed |
| Governance tests | 96 passed, 0 skipped, 0 failed |

The full repository suite was not run because focused evidence agreed with the
checked-in certification evidence. `py_compile` and `git diff --check` passed.

Governance remains `PARTIALLY_CONFORMANT`: 18 checks passed, 2 failed, 0
critical violations; deterministic, fail-closed, and read-only. The two known
hook-drift findings remain visible and do not affect this audit verdict.

## Change and progress accounting

Only this report was added. No production code, tests, schemas, policy, Replay,
CLI behavior, Worker, Provider, execution, command, result, or target repository
was changed.

Evidence-scoped estimates remain unchanged by an audit-only generation:

- no-copy/paste conversational governed development: **99%**;
- whole-project progress: **88%**.

## Bounded G31-15B implementation prompt

```text
# Generation 31-15B — G31 Invocation to Existing Execution Candidate Bounded Projection

Treat Generation 30 and accepted G31-02 through G31-15A as immutable.

G31-15A verdict:
EXISTING_G24_POST_INVOCATION_EXECUTION_REUSABLE_BOUNDED_PROJECTION_REQUIRED

Objective: bind exactly one valid G31-14B WORKER_INVOCATION_ARTIFACT_V1 and
Replay into the existing bridge_worker_invocation_to_execution_candidate
contract, producing and reconstructing exactly one existing
WORKER_EXECUTION_CANDIDATE_ARTIFACT_V1. Stop before start_execution,
run_governed_worker_execution, external task creation, Provider/Worker adapter
activation, command execution, output/result creation, or repository mutation.

Exact caller:
aigol.cli.aicli._record_contextual_execution_decision, immediately after exact
WORKER_INVOKED.

Exact existing callee:
aigol.runtime.worker_invocation_to_execution_candidate_bridge_runtime.
bridge_worker_invocation_to_execution_candidate.

Required bounded projection:
1. reconstruct the exact G31 invocation, dispatch, assignment, request,
   execution authorization, execution-ready, second human confirmation,
   repository grounding, approved payload, and PPP task-package lineage using
   existing public validators/reconstructors;
2. project the already-approved G31 authorization into the existing
   HUMAN_APPROVAL_ARTIFACT_V1 with scope
   CREATE_WORKER_EXECUTION_CANDIDATE_FROM_INVOCATION_ONLY, exact invocation
   id/hash, worker_execution_allowed false, provider_invocation_allowed false,
   and result creation false; this is compatibility evidence, not a third
   decision;
3. supply the authentic nested PPP candidate id/hash as the legacy bridge
   upstream lineage without renaming or substituting another artifact;
4. preserve the full G31 scope and CODEX selection evidence through exact
   references/hashes and nested Replay; do not broaden the existing candidate
   schema;
5. use one deterministic same-session append-only candidate Replay destination;
6. render a truthful candidate-only summary through existing Platform Core
   presentation ownership.

Fail closed before candidate creation for missing/rejected/replayed/cross-session
authorization; changed invocation, dispatch, assignment, request, authorization,
scope, grounding, PPP, Worker id/version/category/role/authority, registry, or
certification evidence; invalid/reordered Replay; Provider-role substitution;
duplicate destination; or any projection that cannot bind an authentic source.

Do not add a new approval system, authorization system, candidate family,
router, selector, execution runtime, Worker/Provider adapter, command runner,
mutation path, clarification system, Replay subsystem, or AiCLI semantics.
Do not call start_execution. No external executable, credential, endpoint,
network, MCP, Provider, or live Worker is required.

Prefer one bounded public binding function and existing validators. Maximum
production additions: 180 lines. If truthful projection exceeds that size or
requires schema redesign, stop and report the deterministic blocker.

Focused tests must prove positive exact G31 candidate creation and
reconstruction; two-decision continuity with no third prompt; authentic PPP,
grounding, authorization, scope, CODEX hybrid-role, and invocation lineage;
all listed tamper/duplicate failures; no execution/process/command/output/result/
Provider/mutation; unchanged unrelated G24-G31 paths; and thin AiCLI authority.

Perform a real PTY-backed ./aicli observation in a disposable Git repository
using only an ordinary request and two contextual approvals. Confirm candidate
creation and Replay, truthful stop before execution start, unchanged source
hashes/Git status, and cleanup.

Run focused G31-15B, bridge, G24, G31-10 through G31-14B, authorization,
selection/certification, Replay, Human Interface/AiCLI, and Governance tests;
py_compile; git diff --check; and the full suite only after focused tests pass.

Add docs/governance/G31_15B_G31_INVOCATION_TO_EXISTING_EXECUTION_CANDIDATE_BOUNDED_PROJECTION.md.
Report exact changes, symbols, counts, PTY evidence, Replay/tamper evidence,
Governance status, Git status, commit commands, and exactly one next state.
Do not commit.
```
