# ACLI Same-Session Approval Audit V1

Status: COMPLETE

Verdict: ACLI_SAME_SESSION_APPROVAL_AUDIT_COMPLETE

## 1. Objective

This audit determines why governed development approval can succeed after ACLI restart but fail in the same interactive session.

Observed same-session failure:

```text
Create governance artifact ...
-> proposal shown
-> approve
-> HUMAN_INTENT_CLARIFICATION_INTAKE
```

Observed replay-restored success:

```text
Create governance artifact ...
-> proposal shown
-> exit ACLI
-> restart ACLI
-> approve
-> execution succeeds
```

The audit reviews routing path differences, state differences, approval gate differences, workflow continuation ordering, and the exact failure point.

## 2. Summary Finding

The same-session failure is caused by continuation branch precedence.

ACLI can correctly detect:

```text
workflow: GOVERNED_DEVELOPMENT_WORKFLOW
matched:
- governed-development-pending-approval
- APPROVE
```

but if clarification continuity is also active, the post-routing execution branch may enter clarification handling before it reaches the governed development execution bridge.

The issue is not proposal generation, proposal hash binding, approval normalization, or the governed development execution bridge itself.

The issue is that a detected governed-development approval must be treated as the highest-priority stateful continuation once a valid pending governed proposal exists.

## 3. Expected Same-Session Flow

Expected:

```text
Prompt
-> Governed development proposal
-> pending_governed_development_bridge stored in memory
-> APPROVE
-> stateful governed development decision detected
-> approve_and_execute_acli_governed_development()
-> repository mutation worker
-> validation
-> replay
```

The same-process regression test exercises this expected path:

```text
Add replay validation
APPROVE
exit
```

and asserts:

```text
proposal_turn.response_status: APPROVAL_REQUIRED
execution_turn.response_status: EXECUTION_COMPLETED
execution_turn.routing_visibility_workflow_id: GOVERNED_DEVELOPMENT_WORKFLOW
execution_turn.worker_invoked: true
execution_turn.validation_executed: true
```

## 4. Expected Replay-Restored Flow

Expected after restart:

```text
Prompt
-> proposal replay persisted
-> exit ACLI
-> restart ACLI
-> APPROVE
-> pending proposal restored from replay
-> stateful governed development decision detected
-> approve_and_execute_acli_governed_development()
-> execution
```

The replay-restored path depends on:

```text
_restore_pending_governed_development_bridge_from_replay()
```

which verifies the pending proposal capture, proposal hash, unconsumed status, and non-execution state before returning it as active pending bridge state.

## 5. Same-Session Runtime State

In the same interactive process, pending proposal state is memory-resident:

```text
pending_governed_development_bridge = bridge_capture
```

That assignment occurs when the proposal bridge returns:

```text
bridge_status: APPROVAL_REQUIRED
approval_required: true
approval_bypassed: false
mutation_performed: false
worker_invoked: false
validation_executed: false
```

The approval turn then computes:

```text
human_decision = normalize_human_decision(human_prompt)
```

`approve`, `APPROVE`, `approved`, and `YES` normalize to:

```text
APPROVE
```

## 6. Replay-Restored Runtime State

In the replay-restored path, the process starts with:

```text
pending_governed_development_bridge = None
```

On explicit approval commands, ACLI scans prior turn replay for:

```text
TURN-*/acli_governed_development_execution_bridge/
000_acli_governed_development_proposal_recorded.json
```

The restore path accepts only valid unconsumed proposal captures and records replay-visible restoration evidence:

```text
ACLI_GOVERNED_DEVELOPMENT_PENDING_PROPOSAL_RESTORED_V1
```

This path can succeed because the restored pending proposal is available before stateful approval routing is evaluated.

## 7. Routing Path Difference

Both same-session and replay-restored approval paths should converge at the same decision:

```text
pending_governed_development_bridge is not None
and human_decision in {APPROVE, REJECT, REQUEST_MODIFICATION}
```

When this condition is true, ACLI records routing visibility as:

```text
GOVERNED_DEVELOPMENT_WORKFLOW
governed-development-pending-approval
APPROVE
```

The observed bug occurs after this detection, not before it.

## 8. Approval Gate Difference

The governed development approval gate is proposal-specific.

It requires:

- active pending proposal capture;
- proposal hash preserved;
- explicit operator decision;
- approval not bypassed;
- no prior mutation;
- no prior worker invocation;
- no prior validation;
- unconsumed proposal replay.

The replay-restored path explicitly reconstructs this gate from replay.

The same-session path already has the gate in memory, but the approval turn can still be intercepted by unrelated continuation logic if branch precedence is wrong.

## 9. Exact Failure Point

The exact failure point is post-routing branch ordering inside the interactive conversation lifecycle.

The relevant pre-routing and routing detection occurs before branch execution:

```text
aigol/cli/aigol_cli.py
stateful_pre_routing_gate
stateful_governed_development_decision
_record_interactive_routing_visibility()
```

The failure occurs when an active clarification branch executes before the governed-development approval branch.

Problem shape:

```text
pending_governed_development_bridge exists
human_decision == APPROVE
active_clarification_reply_detected == true
```

If clarification handling is ordered first:

```text
active clarification continuity
-> HUMAN_INTENT_CLARIFICATION_INTAKE or CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
```

instead of:

```text
approve_and_execute_acli_governed_development()
```

then the operator sees clarification output even though routing visibility says governed development approval was detected.

## 10. Why Restart Can Succeed While Same-Session Fails

Restart changes the active session state.

After restart:

- the pending governed proposal is restored from replay;
- transient in-memory clarification signals may no longer be present;
- the approval turn is more likely to reach the governed development bridge.

In the same process:

- the pending governed proposal exists in memory;
- active clarification lifecycle state may also exist;
- if clarification branches are evaluated first, they can consume the approval turn.

This explains the apparent contradiction:

```text
replay-restored approval succeeds
same-session approval falls through to clarification
```

## 11. Required Fix

When a valid pending governed development proposal exists and the operator enters:

```text
APPROVE
REJECT
REQUEST_MODIFICATION
```

ACLI must execute the governed development approval continuation before any clarification, domain, native-context, or recommendation continuation branch.

Required branch priority:

```text
pending governed development approval decision
-> governed development execution bridge
-> other stateful continuations
```

The bridge must still fail closed if:

- the pending proposal is missing;
- the replay proposal is consumed;
- the replay proposal is invalid;
- the proposal hash is tampered;
- the proposal state indicates prior mutation, worker invocation, validation, or approval bypass.

## 12. Regression Coverage Required

Required same-session regression:

```text
Prompt
-> proposal
-> APPROVE
-> execution
```

Assertions:

```text
routing_visibility_workflow_id == GOVERNED_DEVELOPMENT_WORKFLOW
response_status == EXECUTION_COMPLETED
worker_invoked == true
validation_executed == true
HUMAN_INTENT_CLARIFICATION_INTAKE not rendered
CREATE_DOMAIN_COMPLIANCE_CLARIFICATION not rendered
```

Required competing-state regression:

```text
pending governed proposal exists
active clarification state exists
operator enters APPROVE
```

Expected:

```text
GOVERNED_DEVELOPMENT_WORKFLOW
-> execution bridge
```

Not:

```text
HUMAN_INTENT_CLARIFICATION_INTAKE
CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
```

## 13. Current Verification Evidence

Current focused tests verify:

```text
same-process approval executes after explicit approval
replay-restored approval executes after session resume
restored approval bypasses clarification continuity
approval without pending proposal does not execute
invalid pending replay fails closed
```

The branch-order regression test explicitly simulates active clarification continuity while a governed development proposal is pending and verifies the approval turn enters the governed development execution bridge instead of clarification handling.

## 14. Final Recommendation

Treat explicit operator approval decisions for a valid pending governed development proposal as the highest-priority interactive continuation.

Do not route or continue those turns through:

```text
HUMAN_INTENT_CLARIFICATION_INTAKE
CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
OCS_LLM_COGNITION
```

The approval decision is not a new request. It is a continuation of an existing proposal-bound approval gate.

## 15. Final Verdict

The same-session approval failure is caused by branch precedence, not by missing proposal state or broken approval binding.

Final verdict:

```text
ACLI_SAME_SESSION_APPROVAL_AUDIT_COMPLETE
```
