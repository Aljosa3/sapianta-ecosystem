# G17-HI-10 - Governed Development Execution Continuation Ownership Audit

## Executive Summary

The deterministic owner of canonical Human Interface execution continuation after an approved governed development proposal is the existing governed development bridge continuation in `aigol/cli/aigol_cli.py::_continue_governed_development_bridge_to_certified_runtime(...)`.

That component is already selected by `run_interactive_conversation(...)` when the runtime is entered through `run_human_interface_runtime_entry(...)` with `operator_context = CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY` and `auto_continue = true`. It consumes the approval-required proposal capture, assembles certified development context, continues through PPP routing, creates execution authorization, creates a Worker invocation request, enters the Worker lifecycle, and expects replay certification before reporting a bound runtime.

The proposal artifact is owned by `aigol.runtime.acli_governed_development_execution_bridge` and is intentionally pre-execution. It is not the owner of post-approval execution continuation and must not be interpreted as terminal runtime evidence.

## Current Runtime Chain

Current canonical Human Interface chain:

1. `./aicli` records human `/approve` and delegates to `run_human_interface_runtime_entry(...)`.
2. `run_human_interface_runtime_entry(...)` resolves Platform Core project context and calls the injected governed runtime runner with `auto_continue = true` and `operator_context = CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY` (`aigol/runtime/human_interface_runtime_entry_service.py:137-152`).
3. `run_interactive_conversation(...)` creates the governed development proposal.
4. When the proposal status is `APPROVAL_REQUIRED`, canonical Human Interface runtime entry auto-continuation invokes `_continue_governed_development_bridge_to_certified_runtime(...)` (`aigol/cli/aigol_cli.py:5448-5462`).
5. The bridge continuation records certified development context, post-context PPP routing, Worker request continuation, Worker lifecycle continuation, and replay certification evidence (`aigol/cli/aigol_cli.py:1290-1369`).
6. Runtime entry reports `CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_BOUND` only when failed turns are zero, the latest turn reports `worker_invoked = true`, and replay certification is reached (`aigol/runtime/human_interface_runtime_entry_service.py:243-248`).

## Proposal Ownership

Proposal ownership resides in `aigol.runtime.acli_governed_development_execution_bridge`.

`propose_acli_governed_development_execution(...)` creates an `ACLI_GOVERNED_DEVELOPMENT_BRIDGE_PROPOSAL_CAPTURE_V1` with:

- `workflow_id = WORKFLOW_ID`;
- `bridge_status = APPROVAL_REQUIRED`;
- `approval_required = true`;
- `mutation_performed = false`;
- `worker_invoked = false`;
- `validation_executed = false`.

Implementation evidence: `aigol/runtime/acli_governed_development_execution_bridge.py:146-164`.

Replay evidence from `.runtime/aicli/AICLI-REFERENCE-SESSION/TURN-000019/acli_governed_development_execution_bridge/000_acli_governed_development_proposal_recorded.json` confirms:

- `artifact_type = ACLI_GOVERNED_DEVELOPMENT_BRIDGE_PROPOSAL_CAPTURE_V1`;
- `bridge_status = APPROVAL_REQUIRED`;
- `approval_required = true`;
- `worker_invoked = false`;
- `validation_executed = false`;
- `mutation_performed = false`;
- `failure_reason = None`.

This is correct pre-execution proposal behavior.

## Execution Continuation Ownership

Execution continuation ownership for canonical Human Interface runtime entry resides in:

`aigol/cli/aigol_cli.py::_continue_governed_development_bridge_to_certified_runtime(...)`.

Deterministic evidence:

- The function requires an approval-required bridge proposal and fails closed if the bridge proposal is missing (`aigol/cli/aigol_cli.py:1305-1306`).
- It restores certified native development context (`aigol/cli/aigol_cli.py:1307-1321`).
- It continues the approved prompt through post-context PPP routing (`aigol/cli/aigol_cli.py:1322-1341`).
- It delegates implementation handoff into Worker request continuation through `_continue_ppp_handoff_to_worker_request(...)` (`aigol/cli/aigol_cli.py:1342-1347`).
- It returns `GOVERNED_DEVELOPMENT_BRIDGE_CONTINUED_TO_CERTIFIED_RUNTIME` and binds Worker/replay reached flags into the certified continuation result (`aigol/cli/aigol_cli.py:1348-1369`).

Invocation evidence:

- `run_interactive_conversation(...)` calls `_continue_governed_development_bridge_to_certified_runtime(...)` only when the proposal is approval-required, auto-continue is enabled, and the operator context is canonical Human Interface runtime entry (`aigol/cli/aigol_cli.py:5448-5462`).
- On success, it attaches `certified_development_continuation`, marks upstream human approval consumed, clears local approval-required state, and changes bridge status to `GOVERNED_DEVELOPMENT_BRIDGE_CERTIFIED_RUNTIME_COMPLETED` (`aigol/cli/aigol_cli.py:5471-5483`).

The explicit same-session bridge API has a sibling ownership path:

- `approve_and_execute_acli_governed_development(...)` binds explicit approval and invokes `execute_governed_development_workflow(...)` (`aigol/runtime/acli_governed_development_execution_bridge.py:190-239`).

This explicit API is not the canonical Human Interface auto-continuation owner. It remains an existing certified capability for direct approval/execution flows.

## Worker Invocation Ownership

Worker invocation ownership begins after execution authorization and Worker request creation.

The canonical bridge continuation delegates this segment to:

`aigol/cli/aigol_cli.py::_continue_ppp_handoff_to_worker_request(...)`.

Deterministic evidence:

- It requires a PPP handoff capture and fails closed if the implementation handoff is missing (`aigol/cli/aigol_cli.py:1118-1130`).
- It creates implementation handoff visibility and a governed implementation dry run (`aigol/cli/aigol_cli.py:1131-1150`).
- It authorizes execution readiness through `authorize_execution_ready(...)` (`aigol/cli/aigol_cli.py:1151-1159`).
- It creates a Worker invocation request through `create_worker_invocation_request(...)` (`aigol/cli/aigol_cli.py:1160-1168`).
- It enters `_continue_worker_request_to_replay_certification(...)` (`aigol/cli/aigol_cli.py:1169-1174`).

`create_worker_invocation_request(...)` owns the bounded Worker request artifact and explicitly does not assign or invoke a Worker (`aigol/runtime/worker_invocation_request_runtime.py:147-155`). Assignment and invocation are owned by the Worker lifecycle continuation.

`_continue_worker_request_to_replay_certification(...)` owns:

- Worker assignment (`aigol/cli/aigol_cli.py:960-970`);
- Worker dispatch (`aigol/cli/aigol_cli.py:972-981`);
- Worker invocation (`aigol/cli/aigol_cli.py:983-992`);
- Worker execution candidate creation (`aigol/cli/aigol_cli.py:994-1011`);
- External Worker task packaging (`aigol/cli/aigol_cli.py:1013-1028`);
- external Worker provider execution (`aigol/cli/aigol_cli.py:1030-1042`);
- external result acceptance (`aigol/cli/aigol_cli.py:1044-1052`);
- result validation (`aigol/cli/aigol_cli.py:1054-1062`);
- replay certification (`aigol/cli/aigol_cli.py:1064-1074`).

Replay evidence from TURN-000019 confirms Worker lifecycle entry:

- `worker_invocation_request/002_invocation_request_artifact_recorded.json` exists.
- `worker_assignment/002_assignment_artifact_recorded.json` exists.
- `worker_dispatch/002_dispatch_artifact_recorded.json` exists.
- `worker_invocation/002_invocation_artifact_recorded.json` exists and records `invocation_status = WORKER_INVOKED`, `worker_invoked = true`.
- `worker_execution_candidate/002_worker_invocation_execution_candidate_returned.json` exists.
- `external_worker_adapter/000_external_worker_task_package_recorded.json` exists.
- `openai_external_worker_provider/003_openai_external_worker_returned.json` exists.

Worker invocation is therefore not skipped in the observed replay.

## Replay Ownership

Replay certification ownership resides in `aigol.runtime.replay_certification_runtime.certify_validated_replay(...)`, invoked by `_continue_worker_request_to_replay_certification(...)` after result validation (`aigol/cli/aigol_cli.py:1064-1074`).

Human Interface runtime entry does not own replay certification. It only reads the latest turn summary and records Human Interface workspace state after the governed runtime runner returns (`aigol/runtime/human_interface_runtime_entry_service.py:160-205`).

Regression evidence in `tests/test_g15_runtime_06_governed_development_runtime_continuation.py` verifies the expected complete path:

- runtime status is `REFERENCE_UHI_BOUND`;
- response source is `ACLI_GOVERNED_DEVELOPMENT_EXECUTION_BRIDGE`;
- response status is `GOVERNED_DEVELOPMENT_BRIDGE_CERTIFIED_RUNTIME_COMPLETED`;
- `worker_execution_reached = true`;
- `worker_invocation_status = WORKER_INVOKED`;
- `replay_certification_reached = true`;
- replay certification status is `REPLAY_CERTIFICATION_COMPLETED`.

Implementation evidence: `tests/test_g15_runtime_06_governed_development_runtime_continuation.py:97-118`.

## Runtime Exit Analysis

Runtime entry reports partially bound when `_runtime_bound(...)` is false. `_runtime_bound(...)` requires:

- `failed_turns == 0`;
- latest turn `worker_invoked = true`;
- latest turn `replay_certification_reached = true`.

Implementation evidence: `aigol/runtime/human_interface_runtime_entry_service.py:243-248`.

The observed TURN-000019 replay did not fail at proposal ownership or Worker invocation ownership. It entered the Worker lifecycle and reached the external Worker provider boundary. The local replay evidence records:

- `worker_invocation/002_invocation_artifact_recorded.json`: `invocation_status = WORKER_INVOKED`, `worker_invoked = true`;
- `openai_external_worker_provider/003_openai_external_worker_returned.json`: `failure_reason = OpenAI provider unavailable`;
- no `worker_lifecycle_continuation/replay_certification/000_replay_certification_artifact_recorded.json` exists for that turn.

Therefore, the observed `REFERENCE_UHI_RUNTIME_PARTIALLY_BOUND` follows from runtime failure before replay certification, at the external Worker provider boundary. It is not evidence that execution continuation ownership is missing or that Worker invocation was skipped.

## Existing Capability Reuse Analysis

Existing reusable capabilities already cover each transition:

- Human Interface runtime entry: `run_human_interface_runtime_entry(...)`.
- Proposal creation: `propose_acli_governed_development_execution(...)`.
- Canonical Human Interface proposal-to-execution continuation: `_continue_governed_development_bridge_to_certified_runtime(...)`.
- PPP handoff to Worker request: `_continue_ppp_handoff_to_worker_request(...)`.
- Worker assignment, dispatch, invocation, execution candidate, external task package, external provider, result validation, and replay certification: `_continue_worker_request_to_replay_certification(...)`.
- Explicit same-session approval execution path: `approve_and_execute_acli_governed_development(...)` and `execute_governed_development_workflow(...)`.

No new runtime owner is needed.

## Root Cause

The remaining operational ambiguity is caused by reading pre-execution proposal evidence as if it were terminal execution evidence, combined with a local runtime failure at the external Worker provider boundary.

The deterministic continuation owner exists and is invoked in the canonical Human Interface path. The observed partial runtime state occurs after Worker invocation, because replay certification is not reached when the external Worker provider fails closed with `OpenAI provider unavailable`.

## Minimal Binding Recommendation

Do not introduce a new architecture, runtime, Worker model, Governance model, or Replay model.

Use the existing ownership chain:

1. `run_human_interface_runtime_entry(...)` owns Human Interface runtime entry delegation.
2. `_continue_governed_development_bridge_to_certified_runtime(...)` owns canonical Human Interface approved-proposal continuation.
3. `_continue_ppp_handoff_to_worker_request(...)` owns execution authorization to Worker request transition.
4. `_continue_worker_request_to_replay_certification(...)` owns Worker lifecycle and replay certification progression.

For diagnostics and future Human Interface bindings, classify proposal capture artifacts as pre-execution and classify certified continuation artifacts as post-approval execution evidence.

## Architectural Conclusions

Platform Core ownership remains preserved. The Human Interface does not own conversation, approval, execution, Worker invocation, or replay certification.

Governance ownership remains preserved. Execution authorization is created by the governed continuation, not by `./aicli`.

Worker ownership remains preserved. Worker request creation, assignment, dispatch, invocation, and provider execution are separate runtime stages.

Replay ownership remains preserved. Replay certification is attempted only after result validation and is not synthesized by the Human Interface.

No ownership transfer is required.

## Final Recommendation

Treat `_continue_governed_development_bridge_to_certified_runtime(...)` as the certified canonical Human Interface execution continuation owner for approved governed development proposals.

Treat `approve_and_execute_acli_governed_development(...)` as the explicit same-session approval/execution API, not as the canonical Human Interface auto-continuation owner.

Investigate provider availability separately when a runtime reaches Worker invocation but exits before replay certification. That is a runtime completion condition, not an execution continuation ownership defect.

## Final Verdict

EXECUTION_CONTINUATION_OWNER_CERTIFIED

