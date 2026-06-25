# PPP_CONTINUATION_ROUTING_AUDIT_V1

Status: COMPLETE

Target verdict:

```text
PPP_CONTINUATION_ROUTING_AUDIT_COMPLETE
```

## 1. Audit Purpose

This audit reviews PPP continuation after replay-safe lifecycle continuation restoration.

The audit is implementation-only. It does not redesign Platform Core architecture, governance, replay, approval, Human Intent Resolution, conversational routing, workflows, authority boundaries, or provider semantics.

Observed hardening behavior:

```text
operator prompt:
I need to create a Python script that reads a CSV file and generates a summary report. Help me do that.

-> NATIVE_DEVELOPMENT_CONTEXT_ASSEMBLY
-> WAITING_FOR_OPERATOR
-> continue ppp
-> lifecycle continuation restored
-> workflow identity preserved
-> replay identity preserved
-> continuation remained inside active workflow
-> FAILED_CLOSED

reason:
post-context continuation failed closed: PPP routing failed
```

Local audit reproduction confirmed the same isolation boundary:

```text
TURN 1
workflow: NATIVE_DEVELOPMENT_CONTEXT_ASSEMBLY
state: WAITING_FOR_OPERATOR
chain: CHAIN-EE1C02A3AF1442B6
post_entry_continuation_gate_status: CLARIFICATION_REQUIRED

TURN 2
input: continue ppp
workflow: NATIVE_DEVELOPMENT_CONTEXT_ASSEMBLY
chain: CHAIN-EE1C02A3AF1442B6
post_entry_continuation_gate_status: CONTINUATION_ALLOWED
post_context_continuation_status: FAILED_CLOSED
ppp_route_status: FAILED_CLOSED
failure_reason: OpenAI provider unavailable
```

The exact local failure reason differs because the local environment reached provider proposal production and failed closed on provider availability. The important audit finding is the same: lifecycle routing is no longer the defect. The continuation enters PPP-controlled runtime and fails inside PPP continuation or downstream PPP processing.

## 2. Execution Trace

Current operator path:

```text
stdin
-> aigol/cli/aigol_cli.py
-> run_interactive_conversation(...)
-> pending post-entry continuation restore or same-session pending state
-> _post_entry_continuation_clarification_matches(...)
-> evaluate_post_entry_continuation_gate(...)
-> continue_context_assembled_to_ppp_routing(...)
-> run_conversation_ppp_routing_integration(...)
-> run_conversation_native_development_context_integration(...)
-> resolve_domain_worker_milestone(...)
-> classify_provider_necessity(...)
-> create_conversation_to_implementation_handoff(...)
-> produce_provider_development_proposal(...)
-> failed closed inside PPP-controlled path
```

Relevant code locations:

- `aigol/cli/aigol_cli.py:3476-3578`: same-session or replay-restored post-entry continuation branch invokes PPP continuation.
- `aigol/cli/aigol_cli.py:5513-5578`: native development context entry can immediately create pending continuation and auto-continue when allowed.
- `aigol/cli/aigol_cli.py:732-744`: `_post_context_continuation_should_run(...)` accepts `continue` and `continue ppp` when pending context is valid.
- `aigol/cli/aigol_cli.py:747-751`: `_post_entry_continuation_clarification_matches(...)` accepts `continue` and `continue ppp`.
- `aigol/cli/aigol_cli.py:8168-8209`: `_restore_pending_post_entry_continuation_from_replay(...)` restores pending continuation state from replay.
- `aigol/runtime/context_assembled_to_ppp_routing_continuation.py:32-83`: `continue_context_assembled_to_ppp_routing(...)` hands the restored lifecycle continuation into PPP routing.
- `aigol/runtime/conversation_ppp_routing_integration.py:56-222`: `run_conversation_ppp_routing_integration(...)` performs PPP routing and downstream PPP proposal production.
- `aigol/runtime/domain_and_worker_resolution_registry.py:201-250`: `resolve_domain_worker_milestone(...)` performs deterministic domain, worker, and milestone resolution.

## 3. Current Runtime Sequence

### 3.1 Lifecycle Restoration

Replay restoration is functioning.

`_restore_pending_post_entry_continuation_from_replay(...)` searches prior turns for:

```text
post_entry_continuation_gate/000_post_entry_continuation_gate_recorded.json
```

It restores only gates for:

```text
workflow_id == NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
gate_status == CLARIFICATION_REQUIRED
```

It then loads and verifies the pending native context capture, records a replay-visible restore event, and returns:

```text
native_context_capture
original_human_prompt
current_chain_id
latest_chain_id
restored_from_replay: true
```

This is sufficient to prevent `continue ppp` from re-entering Human Intent Resolution or conversational routing.

### 3.2 Lifecycle Command Matching

Both commands are accepted by the same lifecycle matching rules:

```text
continue
continue ppp
```

The matcher is deterministic:

```text
normalized_prompt == "continue"
or
("continue" in normalized_prompt and "ppp" in normalized_prompt)
```

Conclusion:

```text
continue and continue ppp do not intentionally enter separate routing systems.
They both reach the same post-entry continuation gate when pending native context exists.
```

### 3.3 PPP Handoff

The CLI invokes:

```python
continue_context_assembled_to_ppp_routing(
    human_prompt=pending_post_entry_continuation["original_human_prompt"],
    current_chain_id=current_chain_id,
    latest_chain_id=latest_chain_id,
    ...
)
```

The restored native context capture itself is not passed into the PPP runtime.

### 3.4 PPP Runtime Entry

`continue_context_assembled_to_ppp_routing(...)` invokes:

```python
run_conversation_ppp_routing_integration(
    human_prompt=human_prompt,
    current_chain_id=current_chain_id,
    latest_chain_id=latest_chain_id,
    ...
)
```

`run_conversation_ppp_routing_integration(...)` then re-runs native development context integration:

```python
conversation = run_conversation_native_development_context_integration(...)
```

It does not consume the already restored `native_context_capture`, task intake artifact, development context assembly artifact, or post-entry gate artifact.

Conclusion:

```text
The lifecycle handoff is replay-restored, but PPP routing is prompt-based.
PPP receives original human text and chain ids, not the restored deterministic context artifact.
```

## 4. Expected Runtime Sequence

Expected Feature-Freeze-compliant sequence:

```text
operator prompt
-> NATIVE_DEVELOPMENT_CONTEXT_ASSEMBLY
-> WAITING_FOR_OPERATOR
-> replay records pending continuation gate and native context
-> continue or continue ppp
-> pending continuation restored from memory or replay
-> post-entry continuation gate validates continuation
-> PPP consumes the restored native context or a deterministic PPP entry context derived from it
-> PPP records route decision or fail-closed reason
-> PPP never re-enters Human Intent Resolution
-> PPP never re-enters conversational routing
```

This expected flow does not require new architecture. It requires PPP continuation to preserve the already restored deterministic workflow state across the immediate handoff.

## 5. PPP Entry Contract Review

The PPP entry contract exists for prompt-based PPP routing:

```text
run_conversation_ppp_routing_integration(
    prompt_id,
    human_prompt,
    provider_id,
    created_at,
    replay_dir,
    registry,
    adapter,
    governance_root,
    session_id,
    turn_id,
    current_chain_id,
    latest_chain_id,
)
```

It does not expose a restored-context entry contract.

Missing immediate handoff contract:

```text
restored native context capture
-> PPP entry context
-> PPP route
```

The absence of this contract is the core implementation gap. PPP continuation can preserve chain identity but cannot prove that PPP used the restored task intake and context assembly artifacts because it rebuilds them from text.

## 6. Required Workflow State Availability

Observed state availability:

| Field | Availability | Notes |
| --- | --- | --- |
| workflow id | Available | Restored gate is restricted to `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION`. |
| replay chain id | Available | Local replay preserved `CHAIN-EE1C02A3AF1442B6` across both turns. |
| task intake reference | Available in restored native context | Not passed directly into PPP continuation. |
| context assembly reference | Available in restored native context | Not passed directly into PPP continuation. |
| context hash | Available in restored native context | Local PPP rebuilt a new context under turn 2 and produced `sha256:a33505c9...`. |
| proposal contract | Not available at lifecycle handoff | Created later by PPP as seed proposal validation if PPP progresses. |
| lifecycle stage | Available | `WAITING_FOR_OPERATOR` followed by `CONTINUATION_ALLOWED`. |
| pending continuation metadata | Available | Restored from replay or same-session memory. |

Conclusion:

```text
Replay restoration restores enough state to continue the workflow.
PPP continuation does not consume all restored state.
```

## 7. Exact Failure Location

The observed operator-facing failure is produced through this chain:

```text
run_conversation_ppp_routing_integration(...)
-> returns capture with fail_closed true
-> continue_context_assembled_to_ppp_routing(...)
-> raises FailClosedRuntimeError(ppp_capture.failure_reason or generic PPP routing failure)
-> records POST_CONTEXT_CONTINUATION_ARTIFACT_V1 as FAILED_CLOSED
-> CLI renders FAILED_CLOSED
```

Code locations:

- `aigol/runtime/context_assembled_to_ppp_routing_continuation.py:64-70`: generic PPP fail-closed escalation.
- `aigol/runtime/context_assembled_to_ppp_routing_continuation.py:72-83`: post-context continuation failure artifact recording.
- `aigol/runtime/conversation_ppp_routing_integration.py:215-222`: failed PPP route artifact generation.
- `aigol/runtime/conversation_ppp_routing_integration.py:507-549`: `_failed_route_artifact(...)`.
- `aigol/runtime/conversation_ppp_routing_integration.py:654-657`: `_failure_reason(...)`.

Local replay showed PPP advanced through:

```text
native task intake
development context assembly
domain/worker/milestone resolution
provider necessity classification
seed proposal contract validation
provider request handoff
provider proposal production
```

and then failed closed because:

```text
OpenAI provider unavailable
```

The hardening report's generic:

```text
post-context continuation failed closed: PPP routing failed
```

is consistent with the same failure boundary when the nested PPP capture either lacks a more specific failure reason or the operator surface does not expose the nested stage.

## 8. Replay Verification

Replay correctly preserves:

- workflow identity;
- canonical chain id;
- post-entry continuation gate;
- restored pending continuation event;
- post-context continuation artifact;
- nested PPP replay subtree;
- fail-closed status;
- authority invariants.

Local replay references:

```text
TURN-000001/native_development_context_integration
TURN-000002/post_context_continuation
TURN-000002/post_context_continuation/conversation_ppp_routing
TURN-000002/post_context_continuation/conversation_ppp_routing/conversation_ppp_route
```

Replay restoration ends before PPP routing begins. PPP routing then creates a new nested `conversation_native_development` subtree beneath the continuation turn.

Important replay limitation:

```text
The post-context continuation artifact records null task/context/domain/worker references when the final PPP route is FAILED_CLOSED.
```

This occurs because the failed PPP route artifact collapses route fields to null, even if nested PPP replay contains successful intermediate context and resolution artifacts. Replay remains deterministic, but the top-level diagnostic summary is lossy.

## 9. Governance Verification

Governance behavior is correct.

Verified invariants:

- no Human Intent Resolution is invoked after lifecycle continuation is restored;
- no conversational routing is invoked after lifecycle continuation is restored;
- no worker is invoked;
- no execution is requested;
- no dispatch is requested;
- no governance mutation occurs;
- no replay mutation occurs outside append-only replay artifacts;
- provider remains non-authoritative;
- fail-closed behavior is preserved.

Conclusion:

```text
This is an implementation defect in PPP continuation handoff and diagnostics, not a governance defect.
```

## 10. UX Impact

Current operator-facing diagnostics are insufficient.

Observed hardening message:

```text
PPP routing failed
```

Local message:

```text
OpenAI provider unavailable
```

The second message is more specific but still does not explain that:

- lifecycle continuation succeeded;
- the active workflow was preserved;
- the failure occurred after PPP entry;
- no worker executed;
- no repository mutation occurred;
- the operator can inspect replay for the nested PPP stage.

Recommended diagnostic improvement:

```text
PPP continuation failed closed.

What succeeded:
- lifecycle continuation was restored
- workflow identity was preserved
- replay chain was preserved

Where it failed:
- PPP stage: <stage>
- reason: <specific nested failure reason>

What did not happen:
- no worker executed
- no repository mutation occurred
- no execution was authorized

Replay:
<post_context_continuation_replay_reference>
```

This is a message-quality repair only. It does not alter governance or routing.

## 11. Root Cause

Root cause:

```text
PPP continuation does not have a restored-context entry path.
```

The repaired lifecycle continuation correctly restores pending workflow state from replay. The immediate PPP continuation handoff then discards most of that restored state and calls the prompt-based PPP integration with only:

```text
original_human_prompt
current_chain_id
latest_chain_id
```

The PPP integration then rebuilds native context from the prompt:

```text
run_conversation_native_development_context_integration(...)
```

This creates a second nested context assembly instead of consuming the replay-restored task intake and context assembly artifacts.

Failure classification:

```text
implementation-only
isolated to PPP continuation / immediate handoff
not lifecycle routing
not HIRR
not conversational routing
not governance
not replay corruption
```

## 12. Affected Runtimes

Affected runtimes:

- `aigol/cli/aigol_cli.py`
  - lifecycle command interception and post-entry continuation invocation;
  - no routing defect remains;
  - current handoff passes prompt text rather than restored context.

- `aigol/runtime/context_assembled_to_ppp_routing_continuation.py`
  - immediate continuation-to-PPP adapter;
  - currently accepts prompt text only;
  - records top-level continuation failure.

- `aigol/runtime/conversation_ppp_routing_integration.py`
  - PPP routing runtime;
  - currently prompt-based;
  - re-runs native context integration;
  - top-level failed route artifact collapses intermediate references to null.

- `aigol/runtime/provider_proposal_production_runtime.py`
  - local reproduction reached this runtime and failed closed because provider was unavailable;
  - this is downstream of the PPP handoff defect and confirms fail-closed provider behavior.

## 13. Implementation Complexity

Complexity:

```text
MODERATE
```

Reason:

- lifecycle command routing is already repaired;
- replay restoration is already available;
- PPP routing logic already exists;
- the missing piece is a minimal restored-context handoff contract or compatibility adapter;
- diagnostics should expose nested PPP failure stage without changing authority semantics.

Risk:

```text
LOW_TO_MODERATE
```

The repair must avoid duplicating PPP semantics or introducing new workflow families. It should only allow the existing PPP continuation path to consume already verified replay state.

## 14. Repair Recommendation

Recommended minimal Feature-Freeze-compliant repair:

1. Preserve existing lifecycle continuation detection unchanged.

2. Extend the immediate PPP continuation handoff to pass a deterministic PPP entry context derived from restored native context:

```text
task intake artifact/reference
development context assembly artifact/reference
context hash
canonical chain id
post-entry gate artifact/reference
original prompt
```

3. Add an optional restored-context input path to the existing PPP integration runtime, or add a narrow adapter immediately before it, so PPP can consume verified native context without re-running native development context integration.

4. Preserve the existing prompt-based PPP path for fresh non-restored invocations.

5. Improve fail-closed diagnostics by preserving:

```text
ppp_failed_stage
nested_failure_reason
task_intake_reference if known
context_reference if known
context_hash if known
domain_reference if resolved
worker_reference if resolved
provider_stage if reached
```

6. If the real-world Python script prompt requires a provider and no provider is available, continue failing closed, but report:

```text
PPP continuation reached provider proposal production.
Provider unavailable.
No worker executed.
```

instead of a generic PPP routing failure.

This repair does not introduce new architecture. It preserves replay, governance, approval boundaries, and fail-closed behavior.

## 15. Regression Requirements

Required regression tests if repair proceeds:

1. `continue` same-session continuation:

```text
prompt -> WAITING_FOR_OPERATOR -> continue -> PPP continuation
```

2. `continue ppp` same-session continuation:

```text
prompt -> WAITING_FOR_OPERATOR -> continue ppp -> PPP continuation
```

3. Replay-restored `continue`:

```text
prompt -> WAITING_FOR_OPERATOR -> exit -> restart -> continue -> PPP continuation
```

4. Replay-restored `continue ppp`:

```text
prompt -> WAITING_FOR_OPERATOR -> exit -> restart -> continue ppp -> PPP continuation
```

5. Successful supported PPP continuation:

```text
restored context consumed
task intake reference preserved
context hash preserved
domain/worker/milestone resolved
```

6. Fail-closed PPP continuation:

```text
unsupported or provider-unavailable path fails closed
specific PPP stage recorded
no worker invoked
no execution requested
```

7. Workflow identity preservation:

```text
workflow id remains NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
```

8. Replay identity preservation:

```text
canonical chain id is unchanged across original prompt, restore, continuation, and PPP route
```

9. Routing bypass guarantee:

```text
continuation turn does not invoke Human Intent Resolution
continuation turn does not invoke conversational routing
continuation turn does not invoke provider routing unless PPP explicitly reaches provider proposal production
```

10. Diagnostic completeness:

```text
failed continuation records nested PPP stage and specific failure reason
```

## 16. Final Assessment

The audit confirms:

```text
Lifecycle Continuation is functioning correctly.
Human Intent Resolution is not involved.
Conversational Routing is not involved.
Replay restoration is successful.
Workflow identity is preserved.
Replay identity is preserved.
Fail-closed behavior is correct.
The remaining defect is isolated to PPP continuation or its immediate downstream PPP handoff/diagnostic path.
```

Final verdict:

```text
PPP_CONTINUATION_ROUTING_AUDIT_COMPLETE
```
