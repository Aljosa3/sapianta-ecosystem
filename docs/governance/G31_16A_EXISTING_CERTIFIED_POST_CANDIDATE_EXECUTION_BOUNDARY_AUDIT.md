# G31-16A Existing Certified Post-Candidate Execution Boundary Audit

Status: completed audit; documentation only.

Date: 2026-07-17

Verdict:

`EXISTING_G24_POST_CANDIDATE_EXECUTION_REUSABLE_BOUNDED_PROJECTION_REQUIRED`

## 1. Scope and baseline

This audit treats Generation 30 and committed G31-02 through G31-15B as
immutable. G31-15B is committed at `e33f966d` with verdict
`G31_INVOCATION_TO_EXISTING_EXECUTION_CANDIDATE_BOUNDED_PROJECTION_OPERATIONAL`.
The audit changed no production, CLI, Human Interface, test, schema, approval,
authorization, Worker, Provider, Governance, Replay, or certification behavior.

The inspected G31 stop is one reconstructed
`WORKER_EXECUTION_CANDIDATE_ARTIFACT_V1`. It is candidate evidence only. Its
compatibility approval scope is
`CREATE_WORKER_EXECUTION_CANDIDATE_FROM_INVOCATION_ONLY` and explicitly denies
Worker execution, Provider invocation, execution start, commands, results, and
repository mutation.

## 2. Contract and production-caller inventory

| Boundary | Exact public contract | Production callers | Input -> output | Authority, Replay, side effects, certification |
|---|---|---|---|---|
| G31 candidate creation/reconstruction | `worker_invocation_to_execution_candidate_bridge_runtime.project_g31_invocation_to_execution_candidate`; `bridge_worker_invocation_to_execution_candidate`; `reconstruct_worker_invocation_to_execution_candidate_bridge_replay` | `aigol.cli.aicli._record_contextual_execution_decision`; legacy `aigol_cli._continue_worker_request_to_replay_certification` calls the bridge directly | G31 invocation plus lineage and candidate-only approval -> `WORKER_EXECUTION_CANDIDATE_ARTIFACT_V1` | Existing bridge owns three-step append-only Replay; candidate only; no process, Provider, command, output, result, or mutation |
| Deterministic governed execution | `governed_worker_execution_runtime.run_governed_worker_execution`; `reconstruct_governed_worker_execution_replay` | No production caller found | Worker execution candidate plus candidate-bound `HUMAN_APPROVAL_ARTIFACT_V1`, optional existing summary/confirmation -> `WORKER_EXECUTION_RESULT_ARTIFACT_V1` | Requires scope `RUN_GOVERNED_WORKER_EXECUTION_ONLY` and `worker_execution_allowed=true`; three-step Replay; deterministic evidence only; `subprocess_invoked=false`, `provider_invoked=false`, `implementation_result_created=false`, `code_modified=false` |
| G24 execution-start evidence | `execution_runtime.start_execution`; `reconstruct_execution_replay` | `aigol_cli._record_authorized_worker_execution_start`; `g5_pgsp_worker_runtime_orchestration._run_worker_stack` | Invocation/result, dispatch, assignment, chain, metadata/context -> `EXECUTION_ARTIFACT_V1` in `EXECUTING` | Certified by `governance/EXECUTION_RUNTIME_V1_CERTIFICATION.json`; two-step Replay; no candidate input and no approval/authorization input; records state only |
| External task preparation | `external_worker_adapter_runtime.create_external_worker_task_package` | legacy `aigol_cli._continue_worker_request_to_replay_certification` | Candidate plus `CREATE_EXTERNAL_WORKER_TASK_PACKAGE_ONLY` approval and capability declaration -> `EXTERNAL_WORKER_TASK_PACKAGE_V1` | Provider-neutral Replay evidence only; separate candidate-bound approval; no external activation |
| External result acceptance | `accept_external_worker_result_package`; `create_external_worker_result_package`; `reconstruct_external_worker_adapter_replay` | legacy `aigol_cli` continuation and tests | Supplied external task/result package -> `WORKER_EXECUTION_RESULT_ARTIFACT_V1` | Accepts or creates supplied evidence; does not itself activate CODEX |
| Provider activation | `universal_provider_worker_runtime.run_universal_provider_worker_runtime` -> `openai_external_worker_provider_adapter.run_openai_external_worker_provider_adapter` -> `run_certified_provider_attachment` | legacy `aigol_cli._continue_worker_request_to_replay_certification` | External task plus OpenAI client/key/model/timeout -> external Worker result package | Selects `OPENAI` as `PROVIDER_ROLE`; can invoke remote OpenAI; requires client/credential/network availability; incompatible with current CODEX `WORKER_ROLE` |
| CODEX registration | `codex_worker_platform_integration.register_codex_worker_provider_integration`; reconstructor | No G31 execution caller | Registration inputs -> distinct provider/worker registration evidence | Metadata and credential references only; module explicitly does not invoke CODEX, route work, authorize execution, or mutate a repository |
| Result capture | `worker_result_capture_runtime.capture_worker_result`; reconstructor | `aigol_cli` result-capture continuations; G5 orchestration | Invocation plus already-existing `worker_output`, optionally execution evidence -> `WORKER_RESULT_CAPTURE_ARTIFACT_V1` | Certified; four-step Replay; captures supplied output but does not produce it |
| Result validation | `worker_result_validation_runtime.validate_worker_result`; reconstructor | `aigol_cli`; G5 orchestration | Result-capture evidence -> `WORKER_RESULT_VALIDATION_ARTIFACT_V1` | Certified; validates allowed output, forbidden operations, chain, authority, and Replay; no output production or mutation |
| Post-execution review/termination | post-execution review and governed termination public runtimes/reconstructors | `aigol_cli` lifecycle continuations | Validated result -> review -> termination evidence | Both certified; evidence-only closure; no new work, retry, or mutation |
| Process/command | `validation_command_runner_runtime.execute_validation_command` -> `_execute_request` | governed repository-mutation and governance-artifact workflows | Certified allowlisted command request -> command result | First inspected local process/command boundary: `subprocess.run(..., shell=False)`; not reachable from G31-15B |
| Repository mutation | `repository_mutation_worker_runtime.apply_repository_mutation` -> `_apply_planned_mutations` | `governed_repository_mutation_runtime` | Certified patch proposal or certified Worker result -> mutation artifact | First selected-repository write boundary: `Path.write_text`; requires approved exact mutations; not reachable from G31-15B |
| Rollback/repair | governed rollback candidate, approval, authorization, execution, and Replay contracts | Separate rollback workflows | Existing mutation/replay evidence -> bounded rollback evidence/action | Separate human approval and authorization; not a post-candidate continuation |
| Presentation | existing stage renderers in candidate bridge, execution authorization/runtime, result capture/validation, review, termination | AiCLI/ACLI | Existing capture -> truthful text | Presentation only; no semantic, authority, or Replay ownership |

The execution-start runtime and result-capture/validation/review/termination
runtimes have committed certification evidence. Governed deterministic Worker
execution and the external adapter have focused passing tests but no standalone
certification JSON was located. Historical LLM Worker certification uses a
deterministic local fixture and explicitly does not perform live external LLM
invocation.

## 3. Exact semantics

`start_execution` validates invocation, invocation-result Replay, dispatch,
assignment, Worker identity, chain, metadata, and context. It creates only two
immutable wrappers containing `EXECUTION_ARTIFACT_V1` and the returned event.
It sets lifecycle state `EXECUTING`/`execution_started=true`; it does not accept
or validate the G31 candidate, consume a human approval or execution
authorization, call governed Worker execution, activate an adapter, launch a
process, run a command, create output, capture a result, or mutate a file.
Calling it directly from G31-15B would bypass the accepted candidate and its
separate-governance constraint, so it is not the correct immediate callee.

`run_governed_worker_execution` is the first existing contract that directly
accepts `WORKER_EXECUTION_CANDIDATE_ARTIFACT_V1`. It validates the candidate
and a second input approval scoped exactly to
`RUN_GOVERNED_WORKER_EXECUTION_ONLY`. It may reuse supplied execution-summary
and human-confirmation artifacts. It writes deterministic validation-input,
execution-result, and returned evidence; it marks `worker_executed=true` but
records `subprocess_invoked=false`, `provider_invoked=false`,
`implementation_result_created=false`, and no code/governance modification.
It therefore represents governed deterministic execution evidence, not CODEX
process activation or implementation output.

The current G31 path does not call this contract. Its candidate-only approval
is rejected because its source, scope, and `worker_execution_allowed=false`
cannot satisfy the execution validator.

## 4. Compatibility matrix

| Required evidence/input | Classification | Deterministic finding |
|---|---|---|
| Session identity | `AVAILABLE_BUT_NOT_BOUND` | Present in G31 decision/session Replay; candidate carries same-session Replay paths but no direct session field |
| Original natural-language goal and Project Objective | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Exact values/hashes exist in validated grounded authorization and nested approved-work lineage |
| Durable Governed Work | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Exact id/hash are nested beneath grounding and the second decision |
| Repository grounding/evidence hashes | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Public grounding validator reconstructs exact paths, evidence, symbols, tests, and layers |
| First proposal approval | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Preserved in approved-work lineage; not execution authority |
| Second grounded execution decision | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Exact decision, summary confirmation, and hashes are nested in G31 execution-ready Replay |
| Execution authorization identity/status/scope/expiry/hash/Replay | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Exact authorized, unrevoked, non-transferable G31 authorization is reachable through request Replay; candidate exposes only transitive hashes |
| CODEX identity/version/category/role/authority | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Selection/assignment Replay proves CODEX, certified version, `HYBRID_PROVIDER_WORKER`, `WORKER_ROLE`, `WORKER_AUTHORIZED_TASK_ONLY`; candidate exposes a narrower Worker identity |
| Selection/assignment/dispatch/invocation identities and Replay | `DIRECTLY_COMPATIBLE` | Candidate references/hashes and ordered Replay bind the exact lifecycle chain |
| Authentic PPP identity/hash | `DIRECTLY_COMPATIBLE` | G31-15B projected the validated nested PPP id/hash into candidate fields |
| Candidate-only approval | `INCOMPATIBLE` for execution | Scope authorizes candidate creation only and explicitly denies Worker execution |
| Candidate identity/hash/status/scope | `DIRECTLY_COMPATIBLE` | Governed execution and external-task validators accept the existing artifact family/status/schema |
| Candidate Replay reconstruction | `AVAILABLE_BUT_NOT_BOUND` | Public reconstructor exists; `run_governed_worker_execution` accepts the artifact but does not reconstruct its source Replay itself |
| Source/test paths, symbols, mutation layers | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Exact structured authorization scope exists upstream; candidate carries allowed outputs/forbidden operations only |
| Allowed outputs/forbidden operations | `DIRECTLY_COMPATIBLE` | Candidate copies exact invocation lists |
| `RUN_GOVERNED_WORKER_EXECUTION_ONLY` approval | `MISSING` | Required by existing validator; no G31 binding or public projection currently creates it |
| Existing second-decision summary/confirmation for execution | `AVAILABLE_BUT_NOT_BOUND` | These can be reused rather than synthesized; no third prompt is proven necessary for deterministic evidence-only execution |
| Execution identity/destination | `MISSING` | Deterministic id and same-session append-only destination are not yet bound |
| G24 execution metadata/context | `AVAILABLE_BUT_NOT_BOUND` | Required only by `start_execution`; not inputs to governed candidate execution |
| Local CODEX Worker adapter/process contract | `MISSING` | CODEX is registry/certification metadata; no G31-compatible `WORKER_ROLE` process/output producer was found |
| External task capability declaration | `AVAILABLE_BUT_NOT_BOUND` | Existing provider-neutral declaration targets universal external LLM Worker, not CODEX `WORKER_ROLE` |
| Provider client/key/model/network | `INCOMPATIBLE` with current role | Existing connected external-output route selects OpenAI `PROVIDER_ROLE`; current run forbids Provider authority/invocation |
| Command/process scope | `INCOMPATIBLE` with current authority | G31 scope forbids command execution; no certified command request is present |
| Worker output/result payload | `MISSING` | No CODEX process or output producer is connected; result capture requires supplied output |
| Repository mutation proposal/approval | `MISSING` | No certified patch proposal or mutation authorization exists |
| Stop-state flags | `DIRECTLY_COMPATIBLE` | Candidate proves no Worker process, Provider, command, result, or mutation |

## 5. Authority and human-decision finding

The first decision approved the plan. The second decision confirmed the exact
grounded execution summary and produced execution authorization. It is
available as authentic upstream evidence for a bounded execution-only
compatibility projection. Repository evidence does not prove that a third
human prompt is mandatory before the evidence-only deterministic governed
execution contract.

It does prove that a candidate-bound `HUMAN_APPROVAL_ARTIFACT_V1` is mandatory.
That artifact must be derived only if the existing second decision and
authorization truthfully support `RUN_GOVERNED_WORKER_EXECUTION_ONLY`; it must
bind the candidate id/hash, decision id/hash, authorization id/hash, exact
scope, and preserve result creation, Provider, command, and mutation as false.
The existing candidate-only compatibility approval must not be reused or
broadened.

No existing public G31 constructor performs this projection. The approval
validator is `_validate_human_approval` inside the governed execution owner;
AiCLI has no current post-candidate prompt or projection. Consequently the
first missing edge is a bounded Platform Core projection, not a direct call,
not `start_execution`, and not a newly proven third human decision.

## 6. CODEX and real side-effect boundaries

CODEX remains:

```text
resource_category = HYBRID_PROVIDER_WORKER
selected_role_type = WORKER_ROLE
authority_profile = WORKER_AUTHORIZED_TASK_ONLY
provider_authority = false
provider_invoked = false
```

The unified selection/Worker ecosystem is certified for role-specific
selection and authority. `codex_worker_platform_integration` registers
separate inactive/provider and Worker identities and credential references,
but explicitly performs no invocation. No certified adapter that starts a
CODEX `WORKER_ROLE` process or produces CODEX output from the G31 candidate was
found. Actual CODEX availability would require an executable/process manager
or external service contract and cannot be inferred from registry metadata.

The first mapped boundaries are:

1. process and validation command: `validation_command_runner_runtime._execute_request` using `subprocess.run`; not G31-reachable;
2. CODEX Worker activation: absent for selected `WORKER_ROLE`;
3. Provider activation: universal Provider Worker -> OpenAI adapter -> Certified Provider Attachment; requires Provider role/client/key/network and is incompatible/unreachable;
4. Worker output production: no G31-compatible producer; deterministic governed execution creates governance evidence only;
5. result capture: `capture_worker_result`, requiring already-supplied output; unreachable without a producer;
6. file/repository mutation: `repository_mutation_worker_runtime._apply_planned_mutations` using `Path.write_text`; requires certified exact mutation evidence and is unreachable;
7. result validation/review/termination: existing certified evidence consumers, unreachable until a result exists.

## 7. Existing and intended call chain

```text
aigol.cli.aicli._record_contextual_execution_decision
-> project_g31_invocation_to_execution_candidate
-> WORKER_EXECUTION_CANDIDATE_ARTIFACT_V1
-> stop

missing bounded projection:
candidate Replay + exact G31 decision/authorization
-> candidate-bound RUN_GOVERNED_WORKER_EXECUTION_ONLY compatibility approval
-> run_governed_worker_execution
-> deterministic WORKER_EXECUTION_RESULT_ARTIFACT_V1 evidence
-> stop before any CODEX process, Provider, command, implementation output,
   result capture, or repository mutation
```

The last existing evidence-only transition is candidate creation. The next
existing evidence-only owner is governed deterministic Worker execution. The
first actual process/command owner remains the validation command runner; the
first selected-repository write owner remains repository mutation. Neither is
reachable from this proposed next transition.

## 8. Replay and fail-closed evidence

Existing reconstructors reject missing, changed, duplicated, reordered, or
cross-lineage invocation/candidate/execution evidence; changed hashes/status;
duplicate destinations; changed assignment/dispatch/request/authorization;
Worker/registry/certification/role substitution; prior execution/result state;
and invalid execution metadata/context. Governed execution rejects a missing,
changed, rejected, wrongly scoped, or non-candidate-bound approval, including
reuse of G31-15B's candidate-only approval. External task, Provider, command,
result-capture, and mutation owners independently reject missing authority,
scope expansion, and invalid lineage.

## 9. PTY observation

A PTY-backed `./aicli` run used a disposable Git repository containing only
`aigol/runtime/human_interface.py` and `tests/test_human_interface.py`. One
ordinary request and exactly two `/approve` decisions reached
`WORKER_EXECUTION_CANDIDATE_CREATED`. No additional prompt occurred. Candidate
Replay reconstructed as its three expected wrappers. No execution-start,
governed-execution-result, command, Worker output, result-capture, Provider, or
mutation artifact existed.

Observed state remained:

```text
execution_candidate_created = true
worker_process_started = false
execution_started = false
provider_invoked = false
command_executed = false
result_created = false
repository_mutated = false
```

Source hashes remained `582eec37c9b9169f8cbf5b3f511ed4eaab898b3e` and
`74ad2f17f47f79462f3cd499a90ce8898bdadb02`; Git status remained clean. The
disposable repository and runtime were removed.

## 10. Validation and governance

Focused read-only groups passed:

- candidate, governed execution, execution runtime, external adapter, CODEX registration: 43 passed, 0 skipped, 0 failed, 0 deselected;
- G24 request through invocation and G31-10 through G31-15B: 126 passed, 0 skipped, 0 failed, 0 deselected;
- result capture/validation, post-execution review, termination: 66 passed, 0 skipped, 0 failed, 0 deselected;
- authorization, selection/certification, Human Interface/AiCLI, Governance: 45 passed, 0 skipped, 0 failed, 0 deselected.

Total: 280 passed, 0 skipped, 0 failed, 0 deselected. An initial mistyped test
path collected 0 tests and changed no state. Focused results agree with
committed certification evidence, so the complete suite was not rerun.

Governance remains `PARTIALLY_CONFORMANT`: 18 checks passed, 2 known hook-drift
checks failed, 0 critical violations; deterministic, fail-closed, and
read-only. `py_compile` and `git diff --check` passed.

## 11. Minimal future step

One bounded public binding in the existing governed-execution/candidate owner
should be called by `aigol.cli.aicli._record_contextual_execution_decision`
immediately after exact candidate reconstruction. It should reconstruct the
candidate Replay and complete G31 decision/authorization/grounding lineage;
derive a candidate-bound execution-only approval from the existing second
decision without a third prompt; reuse the existing summary/confirmation; call
`run_governed_worker_execution`; reconstruct its three-step Replay; render the
truthful deterministic-evidence boundary; and stop.

No new artifact family or authority owner is justified. Maximum production
additions: 180 lines. Focused tests must cover exact positive reconstruction,
two-decision continuity, candidate-only approval rejection, authorization and
scope tampering, duplicate destination, CODEX role continuity, and absence of
process/Provider/command/output/result-capture/mutation. The safe stop is the
deterministic governed execution evidence with implementation result creation
still false.

## 12. Progress and next state

Evidence-scoped estimates:

- no-copy/paste conversational governed development: 99.6%;
- whole-project progress: 88.6%.

Exactly one next state:

`G31_CANDIDATE_TO_EXISTING_GOVERNED_EXECUTION_BOUNDED_PROJECTION_REQUIRED`
