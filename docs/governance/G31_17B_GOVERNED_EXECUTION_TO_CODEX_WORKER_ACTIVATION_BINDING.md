# G31-17B Governed Execution to CODEX Worker Activation Binding

Status: implemented and validated.

Date: 2026-07-17

Verdict:

`G31_BOUNDED_CODEX_WORKER_PROCESS_ACTIVATION_BINDING_OPERATIONAL`

## Owner, caller, and bounded callee

The Worker-owned boundary is
`aigol.runtime.codex_worker_activation_binding_runtime`. AiCLI forms the review
with `prepare_codex_worker_activation_review` immediately after G31-16B and
transports the next exact `/approve` through
`_record_contextual_worker_activation_decision`. Only
`activate_bounded_codex_worker` owns activation semantics and Replay.

The bounded callee is the existing
`sapianta_system.runtime.codex_execution_adapter.execute_governed_codex`.
Its existing dispatch path forms exactly `["codex", "exec", bounded_prompt]`,
uses `shell=False`, applies a 30-second timeout, and bounds stdout and stderr to
4,096 characters. The binding supplies no arbitrary arguments, retry,
fallback, hidden continuation, Provider connector, or result-capture call.

## Lineage and identity binding

Before review and again before activation, the binding reconstructs the
G31-16B governed-execution Replay and G31-15B candidate Replay. Existing public
reconstructors transitively validate invocation, dispatch, assignment, Worker
request, execution authorization, and confirmed execution-ready lineage. The
binding additionally reconstructs the selected-resource Replay, the distinct
second human decision, its Replay, and the current repository grounding. The
grounding validator recursively preserves the original request, first human
approval, durable-work, payload, PPP, and repository evidence chain.

Every Replay path must resolve under the same session root. Candidate and
governed-result bodies are re-hashed independently of their supplied hash
fields and must equal their immutable Replay copies. The incoming
`WORKER_EXECUTION_RESULT_ARTIFACT_V1` must have status
`WORKER_EXECUTION_COMPLETED`, `provider_invoked = false`, and
`worker_evidence.subprocess_invoked = false`. This keeps G31-16B's name in its
existing evidence-transition meaning; it is not treated as process evidence or
CODEX output.

The exact identity mapping is:

| Evidence | Required identity | Required role/authority |
|---|---|---|
| Unified selection | `CODEX` | `WORKER_ROLE`, `WORKER_AUTHORIZED_TASK_ONLY` |
| Assignment/invocation | `CODEX` | goal-faithful implementation Worker |
| Registered process Worker | `codex-execution` | bounded execution Worker |
| Rejected identity | `codex-cognition` or any Provider | no execution authority |

The selected hybrid resource is accepted only through its Worker role.
`codex-cognition` remains a distinct Provider identity and is never imported as
an invocation path.

## Authority matrix

| Decision or authority | Scope | Process | Provider | Semantic result | Repository mutation |
|---|---|---:|---:|---:|---:|
| First implementation approval | approved durable work | no | no | no | no |
| Second execution decision | grounded authorization/selection lineage | no | no | no | no |
| G31-16B compatibility projection | `RUN_GOVERNED_WORKER_EXECUTION_ONLY` | no | no | no | no |
| Third activation approval | `RUN_BOUNDED_CODEX_WORKER_PROCESS_ONLY` | one | no | no | no |
| Existing execution-gate token | exact bounded handoff, 300-second validity | one adapter request | no Provider role | no | no |

The third `HUMAN_APPROVAL_ARTIFACT_V1` binds the exact review, candidate,
governed-execution identity/hash, `CODEX`, `codex-execution`, and these exact
flags:

```text
worker_process_activation_allowed = true
fixed_codex_exec_command_allowed = true
bounded_transport_receipt_allowed = true
provider_invocation_allowed = false
worker_result_capture_allowed = false
repository_mutation_allowed = false
```

The approval is consumed once. An existing destination fails before launch;
the same approval identity found in another activation Replay also fails before
launch.

## Replay and transport evidence

One successful activation owns three append-only wrappers:

1. `000_worker_activation_review_recorded.json` containing the existing
   `EXECUTION_SUMMARY_ARTIFACT_V1` family;
2. `001_worker_activation_approval_recorded.json` containing the existing
   `HUMAN_APPROVAL_ARTIFACT_V1` family;
3. `002_worker_activation_transport_receipt_recorded.json` containing the
   existing bounded Codex execution receipt.

`reconstruct_codex_worker_activation_replay` verifies wrapper ordering/hashes,
review and approval artifact hashes, review-to-approval continuity, receipt
identity, and activation truth. No new canonical artifact family or Replay
subsystem was introduced.

The receipt hashes bounded stdout/stderr and records command, shell, timeout,
and capture-limit metadata. It is transport evidence only. The binding does
not import or call `capture_worker_result`; it does not create an
implementation result, semantically validate output, accept a result, or enter
review, mutation, deployment, or release.

After a successful injected-runner activation the truthful outer state is:

```text
third_human_decision_recorded = true
worker_process_activation_allowed = true
worker_process_started = true
subprocess_invoked = true
fixed_codex_exec_command_used = true
transport_receipt_created = true
provider_invoked = false
semantic_worker_result_captured = false
result_accepted = false
command_authority_broadened = false
repository_mutated = false
```

## Fail-closed boundaries

Activation is rejected before the adapter for changed supplied artifacts,
candidate or governed Replay corruption, incomplete/reordered Replay,
cross-session paths, changed status or identity/hash, Provider-role or Worker
identity substitution, non-exact approval scope, duplicate destination,
approval reuse, substituted workspace, stale target evidence, or repository
drift. Immediately before launch, the grounding validator re-observes exact
approved targets and the binding snapshots repository content. The same
snapshot is taken after transport; observed mutation records
`repository_mutated = true` in Replay and fails closed.

Executable and timeout values are constants, not caller inputs. Adapter
validation and post-dispatch metadata must prove the exact command vector,
`shell=False`, and exact timeout. The process inherits only the exact approved
current workspace; activation fails if the current directory differs.

## Validation evidence

- G31-17B focused module: 8 passed.
- G31-10 through G31-16B regression: 81 passed after the final compatibility
  adjustment.
- Worker selection, assignment, dispatch, invocation, candidate, execution,
  result-capture, and result-validation regression: 90 passed.
- Governance tests: 5 passed. Governance engine: `PARTIALLY_CONFORMANT`, 18
  passed, two known hook-drift findings, zero critical violations;
  deterministic, fail-closed, and read-only.
- Targeted `py_compile` and final `git diff --check`: passed.

One disposable live PTY proof used exactly three `/approve` decisions and the
real `codex exec` boundary once. The process started and returned a truthful
`EXECUTION_FAILURE` transport status; no retry was attempted. Its three-step
activation Replay reconstructed completely and proved the fixed command,
`shell=False`, 30-second timeout, bounded receipt, process activation, and all
false Provider/result/mutation boundaries. Disposable source hashes remained
`3692fbc6d8f9f76f5afbc65e8c5f46aa4fbae6f36849ba005293ba7b0ad89a75`
and `6cb9728c57aa10f995cb6dcb1508c0e8ddb5897a94b4f7895872db47c7a743d4`
before and after. The disposable workspace and Replay were removed after
verification. No other live CODEX process was run.

## Changed surface and size

Production changes are limited to the Worker-owned activation binding and the
AiCLI continuation. The binding is 531 physical lines and AiCLI adds 107 lines,
for 638 production additions. This exceeds the audit estimate of 265–370 by
268 lines. The material deviation is explicit lineage reconstruction,
independent supplied-body hashing, pre/post repository observation, one-time
approval scanning, existing execution-gate/handoff composition, deterministic
receipt reconstruction, truthful failure/timeout handling, and compatibility
presentation required to keep all G31-10 through G31-16B tests intact. No
parallel execution, approval, authorization, Replay, or artifact architecture
was added; the excess is validation and composition code in the single bounded
owner.

Exact changed surface:

- `aigol/runtime/codex_worker_activation_binding_runtime.py`
- `aigol/cli/aicli.py`
- `tests/test_g31_17b_governed_execution_to_codex_worker_activation_binding.py`
- this governance report

## Progress and explicit non-goals

Evidence-scoped no-copy/paste conversational governed development is estimated
at **99.8%**, and whole-project progress at **89%**. These are planning
indicators, not production-readiness or conformance certification. The
remaining path includes semantic Worker result capture, validation, human
review/acceptance, any separately approved repository mutation, post-mutation
validation, and release governance.

This milestone does not grant Provider authority, capture or accept semantic
results, authorize commands other than the fixed Codex vector, mutate a source
repository, deploy, release, rename G31-16B artifacts, or change AiCLI into an
authority owner.

## Recommended next state

`G31_CODEX_TRANSPORT_RECEIPT_TO_SEMANTIC_WORKER_RESULT_CAPTURE_AUDIT_REQUIRED`
