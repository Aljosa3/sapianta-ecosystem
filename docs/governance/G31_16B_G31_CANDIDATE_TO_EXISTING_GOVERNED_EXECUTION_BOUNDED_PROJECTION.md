# G31-16B G31 Candidate to Existing Governed Execution Bounded Projection

Status: implemented and validated.

Date: 2026-07-17

Verdict:

`G31_CANDIDATE_TO_EXISTING_GOVERNED_EXECUTION_BOUNDED_PROJECTION_OPERATIONAL`

## Exact caller, callee, and projection

The exact caller is
`aigol.cli.aicli._record_contextual_execution_decision`. Immediately after a
successful G31-15B candidate creation, it calls the bounded public owner
`aigol.runtime.governed_worker_execution_runtime.project_g31_candidate_to_governed_execution`.
That owner validates the complete candidate lineage and calls the existing
`run_governed_worker_execution` contract. AiCLI then renders the owner's
evidence-only presentation.

The projection reconstructs the existing G31-15B candidate Replay and exact
candidate wrapper, then reconstructs the referenced G31 invocation,
execution authorization, confirmed execution-ready evidence, distinct second
human decision, repository grounding, approved payload, and authentic PPP
lineage. All paths must be unique and inside the same session. Public
reconstructors, validators, Replay hash verification, canonical hashing, and
the existing governed-execution runtime are reused.

The existing runtime creates one deterministic three-step Replay:

1. `000_worker_execution_validation_inputs_recorded.json`
2. `001_worker_execution_result_recorded.json`
3. `002_worker_execution_returned.json`

Complete reconstruction returns the existing canonical evidence status
`WORKER_EXECUTION_COMPLETED`. This vocabulary means that the bounded
governed-execution evidence transition completed; it does not mean that an
operating-system process, Worker adapter, or command started.

## Execution-scoped approval truthfulness

The projection constructs a candidate-bound `HUMAN_APPROVAL_ARTIFACT_V1` with
exact scope `RUN_GOVERNED_WORKER_EXECUTION_ONLY`. It is independently derived
from the authentic original second human execution decision, confirmation,
and execution authorization and binds the exact G31-15B candidate identity and
hash. The artifact records the source decision hash, human confirmation hash,
authorization identity/hash, original decider, and original decision time.

It grants only the existing evidence-only governed-execution transition.
Worker execution compatibility is true only in the existing runtime's
evidence semantics. The explicit downstream fields remain false for actual
Worker process activation, Provider invocation, command execution, Worker
output creation, implementation-result creation, result capture, and
repository mutation.

The G31-15B compatibility approval is neither changed nor used as execution
authority. It remains scoped to
`CREATE_WORKER_EXECUTION_CANDIDATE_FROM_INVOCATION_ONLY` with
`worker_execution_allowed = false`, and the existing execution runtime rejects
it before writing even the validation-input wrapper.

The new compatibility artifact records
`derived_compatibility_projection = true` and
`third_human_decision_recorded = false`. The capture records exactly two source
human decisions. No prompt, response, decision, or authorization was added.

## Replay, role, and authority boundaries

The successful outer state is:

```text
worker_selected = true
worker_assigned = true
worker_dispatched = true
worker_invoked = true
execution_candidate_created = true
governed_execution_evidence_created = true
provider_invoked = false
worker_process_started = false
execution_started = false
command_executed = false
worker_output_created = false
result_created = false
repository_mutated = false
```

Earlier stage-local selection, assignment, dispatch, invocation, and candidate
captures remain unchanged. The existing governed-execution result artifact
also records `implementation_result_created = false`,
`provider_invoked = false`, and `worker_evidence.subprocess_invoked = false`.
No Worker output or result is captured.

CODEX remains the selected `HYBRID_PROVIDER_WORKER` resource in `WORKER_ROLE`
with `WORKER_AUTHORIZED_TASK_ONLY`. It receives no Provider authority and is
not activated. The OpenAI `PROVIDER_ROLE` path remains disconnected.

AiCLI sequences public owners and presents their output only:

```text
aicli_authorizes = false
aicli_executes = false
aicli_owns_replay = false
```

It does not construct execution authority, own Replay semantics, or execute a
Worker.

## Fail-closed evidence

The bounded owner validates the immutable candidate wrapper and hash, supplied
capture identity, candidate-only approval, unique same-session lineage
references, invocation identity, authorization status/scope/revocation,
second-decision reconstruction, confirmation binding, and authentic PPP
identity/hash before calling the existing execution runtime.

Focused tests prove that a changed candidate fails before a new destination is
created. Reusing the successful destination returns `FAILED_CLOSED` without
changing the valid Replay. The candidate-only approval is rejected before
partial execution evidence. Static boundary evidence proves that the new
projection contains no call to `start_execution`, an external Worker adapter,
OpenAI execution, `subprocess.run`, result capture, repository mutation worker,
or `Path.write_text`.

Existing G24-G31 and full-suite coverage preserves fail-closed validation for
invocation, dispatch, assignment, request, Worker registry/certification,
selection identity/version/category/role/authority, authorization, grounding,
payload/PPP lineage, Replay ordering/substitution, Provider-role substitution,
and governed-execution result/Replay tampering.

## PTY evidence

A real PTY-backed `./aicli` session used a disposable Git repository containing
one implementation file, `aigol/runtime/human_interface.py`, and one focused
test, `tests/test_human_interface.py`. One ordinary bounded request and exactly
two existing `/approve` decisions reached the G31 execution candidate and one
governed-execution evidence state. Presentation reported
`WORKER_EXECUTION_COMPLETED` while stating that CODEX did not start and that no
adapter, Provider, subprocess, command, Worker output, result capture, or
mutation occurred.

The governed-execution Replay contained exactly the three expected JSON
wrappers and reconstructed completely. No third prompt appeared. Source hashes
remained `582eec37c9b9169f8cbf5b3f511ed4eaab898b3e` and
`74ad2f17f47f79462f3cd499a90ce8898bdadb02`; disposable Git status remained
clean. The disposable repository and runtime were removed.

## Validation

- G31-16B plus existing governed-execution, candidate bridge, and G31-15B
  focused group: 17 passed, 0 skipped, 0 failed, 0 deselected.
- Requested selected G24-G31, approval/authorization, Worker
  selection/certification, execution, Human Interface/AiCLI, and Governance
  regression group: 207 passed, 0 skipped, 0 failed, 0 deselected.
- Complete repository suite: 6,391 passed, 4 skipped, 0 failed, 0 deselected in
  262.77 seconds.
- G31-16B focused module: 4 passed, 0 skipped, 0 failed, 0 deselected.
- Governance test: 5 passed, 0 skipped, 0 failed, 0 deselected.
- Governance engine: `PARTIALLY_CONFORMANT`; 18 passed, 2 known hook-drift
  failures, 0 critical violations; deterministic, fail-closed, and read-only.
- Targeted `py_compile` and final `git diff --check`: passed.

## Changed surface and minimality

Production changes are limited to the existing governed-execution owner and
AiCLI. They add 179 production lines and delete one production line, within the
180-line additions gate. The new production symbols are:

- `project_g31_candidate_to_governed_execution`
- `render_governed_worker_execution_summary`

No production module, canonical artifact family, approval system,
authorization system, execution architecture, Worker/Provider adapter, command
runner, mutation path, or Replay subsystem was added.

Exact changed surface:

- `aigol/cli/aicli.py`: 32 insertions, 0 deletions.
- `aigol/runtime/governed_worker_execution_runtime.py`: 147 insertions, 1 deletion.
- `tests/test_g31_16b_g31_candidate_to_governed_execution_bounded_projection.py`: 112 insertions, 0 deletions.
- This governance report: 192 insertions, 0 deletions.

## Stop boundary

The transition stops after deterministic governed-execution evidence and
complete Replay reconstruction. No actual CODEX or Worker process, adapter,
Provider, subprocess, external executable, command, Worker output,
implementation result, result capture, filesystem write, repository mutation,
deployment, or release operation is reachable through the new path.

## Next state

`G31_GOVERNED_EXECUTION_TO_ACTUAL_WORKER_ACTIVATION_AUDIT_REQUIRED`
