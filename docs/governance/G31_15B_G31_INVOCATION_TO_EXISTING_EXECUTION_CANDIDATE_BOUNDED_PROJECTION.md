# G31-15B G31 Invocation to Existing Execution Candidate Bounded Projection

Status: implemented and validated.

Date: 2026-07-17

Verdict:

`G31_INVOCATION_TO_EXISTING_EXECUTION_CANDIDATE_BOUNDED_PROJECTION_OPERATIONAL`

## Scope and exact projection

Generation 30 and accepted G31-10 through G31-15A remain immutable. The exact
G31-14B `WORKER_INVOKED` state now enters
`project_g31_invocation_to_execution_candidate`, which reconstructs the
existing invocation, dispatch, assignment, request, authorization,
execution-ready, second-decision, repository-grounding, approved-payload, and
PPP lineage. It then calls the existing
`bridge_worker_invocation_to_execution_candidate` contract and reconstructs
one existing `WORKER_EXECUTION_CANDIDATE_ARTIFACT_V1` from three ordered Replay
steps.

The bridge accepts an optional authentic PPP candidate input for the G31
compatibility path. The projected legacy `upstream_lineage_reference` and
`upstream_lineage_hash` are taken only from the validated nested
`ppp_task_package_artifact`; no candidate identity is renamed or synthesized.
The existing candidate schema and artifact family are unchanged.

## Human authority and authorization truthfulness

The compatibility `HUMAN_APPROVAL_ARTIFACT_V1` is derived evidence, not a new
prompt, response, or decision. It binds the exact second human decision,
confirmation hash, execution-authorization identity/hash, and invocation
identity/hash. Its scope is exactly
`CREATE_WORKER_EXECUTION_CANDIDATE_FROM_INVOCATION_ONLY` and its flags deny
Worker execution, Provider invocation, execution start, command execution,
result creation, and repository mutation. `third_human_decision_recorded` is
false and the observed decision count remains two.

Authorization must reconstruct as `EXECUTION_AUTHORIZED`, remain unrevoked,
non-transferable, and non-recursive, and match the invocation and exact
grounded scope. The second decision and execution-ready Replay must reconstruct
inside the same session. Invalid evidence fails before candidate creation.

## Replay, role, and authority boundaries

The candidate preserves exact invocation, dispatch, assignment, request,
authorization, execution-ready, implementation-request, and authentic PPP
references and hashes. Existing public reconstructors, validators, immutable
writes, serialization, and hash verification are reused.

CODEX remains `HYBRID_PROVIDER_WORKER`, selected as `WORKER_ROLE`, with
`WORKER_AUTHORIZED_TASK_ONLY`; Provider authority and invocation remain false.
AiCLI only sequences the existing owner and renders its result:
`aicli_authorizes = false`, `aicli_executes = false`, and
`aicli_owns_replay = false`.

Successful outer state:

```text
worker_selected = true
worker_assigned = true
worker_dispatched = true
worker_invoked = true
execution_candidate_created = true
provider_invoked = false
worker_process_started = false
execution_started = false
command_executed = false
result_created = false
repository_mutated = false
```

Earlier selection, assignment, dispatch, and invocation captures retain their
stage-local values. No historical evidence is rewritten.

## Fail-closed evidence

Focused tests cover exact creation and reconstruction, authentic PPP identity,
grounded authorization scope, CODEX selection/category/role/authority,
candidate-only approval, two-decision continuity, false execution boundaries,
changed invocation rejection, duplicate destination rejection without Replay
change, thin AiCLI ownership, and absence of forbidden execution imports.
Existing G24-G31 tests retain nested tamper coverage for dispatch, assignment,
request, authorization, grounding, Worker identity/version/category/role,
registry, certification, Replay ordering, and Provider-role substitution.

## PTY evidence

A real PTY-backed `./aicli` session used a disposable Git repository containing
only `aigol/runtime/human_interface.py` and
`tests/test_human_interface.py`. One ordinary request plus exactly two
`/approve` decisions reached `WORKER_INVOKED` and then
`WORKER_EXECUTION_CANDIDATE_CREATED`. Presentation stated that the candidate is
governance evidence, CODEX has not started, no adapter or command ran, no
output/result or repository change occurred, and another governed transition
is required.

The candidate Replay contained exactly its three expected JSON wrappers. The
source hashes remained `582eec37c9b9169f8cbf5b3f511ed4eaab898b3e` and
`74ad2f17f47f79462f3cd499a90ce8898bdadb02`; Git status remained clean. The
disposable repository and runtime were removed.

## Validation

- G31-15B focused: 4 passed, 0 skipped, 0 failed.
- Existing bridge, G24 request/assignment/dispatch/invocation, and G31-10
  through G31-14B focused group: 129 passed, 0 skipped, 0 failed.
- Complete repository suite: 6,387 passed, 4 skipped, 0 failed in 245.05s.
- Governance test: 5 passed, 0 skipped, 0 failed.
- Governance engine: `PARTIALLY_CONFORMANT`; 18 passed, 2 known hook-drift
  failures, 0 critical violations; deterministic, fail-closed, read-only.
- `compileall` and `git diff --check`: passed.

The full suite supplies the requested approval/authorization,
selection/registry/certification, execution-candidate Replay, Human
Interface/AiCLI, and Governance regression coverage. Known hook drift remains
visible and unchanged.

## Changed surface and stop boundary

Production changes are limited to the existing bridge owner and AiCLI and stay
within the 180-line production gate. One focused test module and this report
are added. No canonical artifact family, approval system, authorization
system, selector, router, execution runtime, adapter, command runner, mutation
path, or Replay subsystem is added.

The transition stops before `start_execution`, governed Worker execution,
external task creation, any Worker or Provider adapter, process launch, command
execution, output/result creation, and filesystem or repository mutation.

## Next state

`G31_POST_CANDIDATE_EXECUTION_BOUNDARY_AUDIT_REQUIRED`
