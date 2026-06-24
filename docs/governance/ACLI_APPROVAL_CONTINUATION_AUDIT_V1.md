# ACLI Approval Continuation Audit V1

Status: COMPLETE

Verdict: ACLI_APPROVAL_CONTINUATION_AUDIT_COMPLETE

## 1. Objective

This audit determines why `APPROVE`, entered while a `GOVERNED_DEVELOPMENT_WORKFLOW` proposal is pending approval, can be routed as a new conversational request instead of continuing the active governed proposal.

Expected lifecycle:

```text
WAITING_FOR_APPROVAL
-> APPROVE
-> EXECUTION
```

Observed lifecycle:

```text
WAITING_FOR_APPROVAL
-> APPROVE
-> HUMAN_INTENT_CLARIFICATION_INTAKE
```

The audit reviews approval state persistence, pending proposal lookup, approval command interception, interactive conversation lifecycle, workflow continuation routing, and execution bridge integration.

## 2. Audit Finding

The governed development approval continuation works when the proposal and `APPROVE` command occur in the same interactive process.

The governed development approval continuation fails when the operator approves in a later invocation of the same conversation session.

The failure is not in approval binding, proposal hash binding, workflow execution, validation, or replay execution. The failure is in pending proposal state restoration.

## 3. Reproduced Current Behavior

The audited cross-invocation reproduction used this sequence:

```text
Invocation 1:
Create governance artifact ACLI_APPROVAL_CONTINUATION_TMP_V1 documenting approval continuation audit.
exit

Invocation 2:
APPROVE
exit
```

Observed result:

```text
FIRST  GOVERNED_DEVELOPMENT_WORKFLOW  APPROVAL_REQUIRED
SECOND HUMAN_INTENT_CLARIFICATION_INTAKE  CLARIFICATION_REQUIRED  CONVERSATIONAL_CLI_WORKFLOW
```

The second invocation rendered:

```text
HUMAN INTENT CLARIFICATION REQUIRED
Intent Family: AMBIGUOUS_INTENT
```

This matches the reported failure mode.

## 4. Same-Process Approval Path

The same-process path is currently correct.

The existing regression test `tests/test_acli_governed_development_execution_bridge_v1.py` runs:

```text
Add replay validation
APPROVE
exit
```

inside one `run_interactive_conversation()` call and asserts:

```text
proposal_turn.response_status: APPROVAL_REQUIRED
execution_turn.response_status: EXECUTION_COMPLETED
execution_turn.routing_visibility_workflow_id: GOVERNED_DEVELOPMENT_WORKFLOW
execution_turn.worker_invoked: true
execution_turn.validation_executed: true
```

That confirms the execution bridge can continue a pending proposal when in-memory pending state is present.

## 5. Exact Runtime Call Chain

For a same-process approval:

```text
stdin
-> aigol/cli/aigol_cli.py
-> run_interactive_conversation()
-> pending_governed_development_bridge is present
-> normalize_human_decision("APPROVE")
-> stateful_pre_routing_gate: true
-> authoritative_workflow_id: GOVERNED_DEVELOPMENT_WORKFLOW
-> approve_and_execute_acli_governed_development()
-> execute_governed_development_workflow()
-> repository mutation worker
-> validation
-> replay
```

For a cross-invocation approval:

```text
stdin
-> aigol/cli/aigol_cli.py
-> run_interactive_conversation()
-> pending_governed_development_bridge initialized to None
-> resume_conversation_session() allocates next turn only
-> no pending governed proposal lookup occurs
-> stateful_pre_routing_gate: false
-> route_conversational_cli_intent("APPROVE")
-> HUMAN_INTENT_CLARIFICATION_INTAKE
```

## 6. Approval State Persistence

Proposal evidence is persisted by the governed development execution bridge.

`aigol/runtime/acli_governed_development_execution_bridge.py:146-177` creates a proposal capture with:

```text
bridge_status: APPROVAL_REQUIRED
approval_required: true
approval_bypassed: false
mutation_performed: false
worker_invoked: false
validation_executed: false
operator_next_action: APPROVE, REJECT, or REQUEST_MODIFICATION
```

and writes:

```text
000_acli_governed_development_proposal_recorded.json
```

The persisted replay evidence is sufficient to identify a pending proposal.

However, the interactive CLI does not currently restore that persisted proposal into the runtime variable that controls continuation.

## 7. Pending Proposal Lookup

The interactive runtime initializes pending governed development state as in-memory only:

```text
aigol/cli/aigol_cli.py:2997
pending_governed_development_bridge: dict[str, Any] | None = None
```

Session resume is called at startup and each turn:

```text
aigol/cli/aigol_cli.py:2994
aigol/cli/aigol_cli.py:3045-3049
```

But `resume_conversation_session()` only discovers existing turn ids and allocates the next turn:

```text
aigol/runtime/conversation_session_resume_runtime.py:18-57
```

It returns:

```text
session_root
session_resumed
existing_turn_ids
next_turn_id
```

It does not inspect previous turn replay for `ACLI_GOVERNED_DEVELOPMENT_BRIDGE_PROPOSAL_CAPTURE_V1`.

Therefore, after process restart, the pending proposal is on disk but not in active continuation state.

## 8. Approval Command Interception

Approval command interception exists and is correct when pending state is present.

`aigol/cli/aigol_cli.py:3094-3127` sets `stateful_pre_routing_gate` when:

```text
pending_governed_development_bridge is not None
and human_decision in {APPROVE, REJECT, REQUEST_MODIFICATION}
```

`aigol/cli/aigol_cli.py:3141-3146` then forces:

```text
authoritative_workflow_id = GOVERNED_DEVELOPMENT_WORKFLOW
```

`aigol/cli/aigol_cli.py:3528-3562` then invokes:

```text
approve_and_execute_acli_governed_development()
```

The interception condition is correct, but it depends entirely on `pending_governed_development_bridge` being populated.

## 9. Interactive Conversation Lifecycle

The lifecycle currently has two different continuity models:

1. In-memory continuity for the active Python process.
2. Replay-visible evidence on disk.

For governed development approvals, these two models are not yet connected.

The proposal turn stores replay evidence and sets:

```text
aigol/cli/aigol_cli.py:4779-4780
pending_governed_development_bridge = bridge_capture
```

This enables the next input in the same process to continue.

But a later `run_interactive_conversation()` invocation starts with:

```text
pending_governed_development_bridge = None
```

and does not load the previous `APPROVAL_REQUIRED` bridge capture from replay.

## 10. Workflow Continuation Routing

The routing behavior for bare `APPROVE` without active pending proposal state is deterministic:

```text
routing_status: CLARIFICATION_REQUIRED
workflow_id: HUMAN_INTENT_CLARIFICATION_INTAKE
operator_summary: Ask deterministic clarification questions for normal human intent before provider fallback.
matched_terms: ['unknown-human-intent']
```

This behavior is appropriate if no active approval context exists.

The regression occurs because an active approval context exists in replay, but the interactive lifecycle does not restore it.

## 11. Execution Bridge Integration

The execution bridge is not the failure point.

`aigol/runtime/acli_governed_development_execution_bridge.py:190-282` correctly:

- verifies the pending proposal capture;
- rejects non-`APPROVED` decisions without mutation;
- creates approval evidence for `APPROVED`;
- executes the governed development workflow;
- preserves proposal hash binding;
- persists approval and execution replay.

The bridge is reachable only if the CLI passes the persisted proposal capture to:

```text
approve_and_execute_acli_governed_development()
```

In the failing path, the bridge is never reached.

## 12. Exact Failure Point

The exact failure point is:

```text
aigol/cli/aigol_cli.py:2997
```

where:

```text
pending_governed_development_bridge = None
```

is initialized, followed by session resume logic that does not restore pending governed development approval state from replay.

The decision gate at `aigol/cli/aigol_cli.py:3111-3112` then evaluates false:

```text
pending_governed_development_bridge is not None
and human_decision in {APPROVE, REJECT, REQUEST_MODIFICATION}
```

Because it evaluates false, `APPROVE` is routed as a fresh conversational request.

## 13. State Transition Failure

The missing transition is:

```text
REPLAYED_PROPOSAL_APPROVAL_REQUIRED
-> ACTIVE_PENDING_GOVERNED_DEVELOPMENT_BRIDGE
```

Current state transition:

```text
proposal generated
-> replay persisted
-> process exits
-> session resumes
-> next turn allocated
-> pending governed proposal not restored
```

Required state transition:

```text
proposal generated
-> replay persisted
-> process exits
-> session resumes
-> latest unconsumed governed development proposal loaded
-> APPROVE intercepted
-> execution bridge invoked
```

## 14. Continuation Detection Failure

Continuation detection fails because it only checks in-memory state:

```text
pending_governed_development_bridge is not None
```

It does not check replay for:

```text
TURN-*/acli_governed_development_execution_bridge/000_acli_governed_development_proposal_recorded.json
```

with:

```text
artifact_type: ACLI_GOVERNED_DEVELOPMENT_BRIDGE_PROPOSAL_CAPTURE_V1
bridge_status: APPROVAL_REQUIRED
approval_required: true
mutation_performed: false
```

and no later consumed approval, rejection, modification request, or execution capture.

## 15. Recommended Fix

Implement a narrow governed-development pending proposal resolver for interactive session resume.

The resolver should:

1. Scan the current session replay root for the latest governed development proposal capture.
2. Accept only proposal captures with:

```text
artifact_type: ACLI_GOVERNED_DEVELOPMENT_BRIDGE_PROPOSAL_CAPTURE_V1
bridge_status: APPROVAL_REQUIRED
approval_required: true
approval_bypassed: false
mutation_performed: false
worker_invoked: false
validation_executed: false
```

3. Reject captures that already have a later approval, rejection, modification request, execution, or fail-closed terminal decision.
4. Verify the proposal capture hash before using it.
5. Populate `pending_governed_development_bridge` before evaluating `stateful_pre_routing_gate`.
6. Record replay-visible continuation evidence that approval state was restored from replay.

This preserves the existing constitutional boundary:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

The resolver must not authorize execution by itself. It only restores the pending proposal context so explicit human `APPROVE`, `REJECT`, or `REQUEST_MODIFICATION` can be interpreted correctly.

## 16. Regression Tests Required

Add a cross-invocation regression test:

```text
run_interactive_conversation(prompt, exit)
run_interactive_conversation(APPROVE, exit) with same session id and runtime root
```

Expected assertions:

```text
first invocation:
  response_status == APPROVAL_REQUIRED
  mutation_performed == false

second invocation:
  routing_visibility_workflow_id == GOVERNED_DEVELOPMENT_WORKFLOW
  response_status == EXECUTION_COMPLETED
  worker_invoked == true
  validation_executed == true
  approval_bypassed == false
```

Add a negative test:

```text
APPROVE without any pending governed development proposal
```

Expected result:

```text
HUMAN_INTENT_CLARIFICATION_INTAKE
```

or another fail-closed non-execution response.

## 17. Final Verdict

The approval continuation regression is caused by missing replay-to-active-state restoration for pending governed development proposals.

Same-process approval continuation works.

Cross-invocation approval continuation fails because `APPROVE` is evaluated without restored pending proposal context and is therefore routed as a new ambiguous conversational request.

Final verdict:

```text
ACLI_APPROVAL_CONTINUATION_AUDIT_COMPLETE
```
