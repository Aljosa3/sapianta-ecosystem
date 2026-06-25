# LIFECYCLE_COMMAND_ROUTING_AUDIT_V1

Status: COMPLETE

Target verdict:

```text
LIFECYCLE_COMMAND_ROUTING_AUDIT_COMPLETE
```

## 1. Audit Purpose

This audit reviews how operator lifecycle commands are routed during Platform Core Generation 1 feature freeze.

The audit is implementation-only. It does not redesign ACLI, governance, replay, approval, worker execution, or Human Intent Resolution.

Observed behavior:

```text
NATIVE_DEVELOPMENT_CONTEXT_ASSEMBLY
-> WAITING_FOR_OPERATOR
-> operator enters: continue ppp
-> Human Intent Resolution / conversational routing path is entered
-> OCS_LLM_COGNITION is selected
-> provider unavailable failure occurs
```

Fail-closed behavior is correct. The suspected defect is lifecycle-command routing, not provider failure handling.

## 2. Current Implementation Flow

### 2.1 Operator Input Entry

All interactive ACLI input enters through `run_interactive_conversation(...)` in:

```text
aigol/cli/aigol_cli.py
```

Relevant flow:

```text
operator input
-> _read_interactive_prompt_capture(...)
-> resume_conversation_session(...)
-> record_multiline_prompt_capture(...)
-> create_conversational_progress_binding(...)
-> normalize_human_decision(...)
-> detect active clarification / approval / pending workflow state
-> stateful_pre_routing_gate
-> route_conversational_cli_intent(...) if no stateful gate matched
```

Code locations:

- `aigol/cli/aigol_cli.py:3138-3164`: interactive prompt intake.
- `aigol/cli/aigol_cli.py:3178-3185`: next turn allocation.
- `aigol/cli/aigol_cli.py:3203`: human decision normalization.
- `aigol/cli/aigol_cli.py:3224-3245`: active clarification and domain approval detection.
- `aigol/cli/aigol_cli.py:3246-3279`: stateful pre-routing gate.
- `aigol/cli/aigol_cli.py:3280-3289`: conversational routing is invoked when the stateful gate is false.

### 2.2 Native Development Context Entry

When routing selects:

```text
NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
```

the CLI executes:

```text
run_conversation_native_development_context_integration(...)
-> evaluate_post_entry_continuation_gate(...)
```

Code locations:

- `aigol/cli/aigol_cli.py:5417-5428`: native development context integration invocation.
- `aigol/cli/aigol_cli.py:5441-5454`: post-entry continuation gate evaluation.

If the native context is execution-capable and needs explicit operator confirmation, the gate returns:

```text
CLARIFICATION_REQUIRED
```

The CLI then stores in-memory pending state:

```text
pending_post_entry_continuation = {
    native_context_capture,
    original_human_prompt,
    current_chain_id,
    latest_chain_id,
}
```

Code locations:

- `aigol/cli/aigol_cli.py:5467-5479`: pending post-entry continuation is stored.

### 2.3 Same-Session `continue ppp`

For the next operator input, the stateful pre-routing gate checks:

```text
pending_post_entry_continuation is not None
and _post_entry_continuation_clarification_matches(human_prompt)
```

Code locations:

- `aigol/cli/aigol_cli.py:3275-3278`: pre-routing bypass condition.
- `aigol/cli/aigol_cli.py:3433-3436`: same-session continuation branch.
- `aigol/cli/aigol_cli.py:749-751`: `_post_entry_continuation_clarification_matches(...)`.

The command matcher is:

```text
return "continue" in normalized_prompt and "ppp" in normalized_prompt
```

If this state exists, `continue ppp` bypasses conversational routing and executes lifecycle continuation:

```text
evaluate_post_entry_continuation_gate(...)
-> continue_context_assembled_to_ppp_routing(...)
```

Code locations:

- `aigol/cli/aigol_cli.py:3447-3460`: continuation gate is re-evaluated with the preserved native context.
- `aigol/cli/aigol_cli.py:3473-3495`: post-context PPP continuation runtime is invoked.
- `aigol/runtime/context_assembled_to_ppp_routing_continuation.py:32-83`: replay-visible continuation to PPP routing.

Conclusion for same-session `continue ppp`:

```text
SAME_SESSION_CONTINUE_PPP_BYPASSES_HIRR
```

Same-session behavior is implemented and covered by existing tests.

## 3. Where Lifecycle Commands First Enter

Lifecycle commands first enter the system as ordinary operator text in the interactive loop.

They are then processed by two possible mechanisms.

### A. Workflow Lifecycle Logic

This path is used only when a matching pending state exists in memory:

- `pending_post_entry_continuation`;
- `pending_governed_development_bridge`;
- `pending_approval_required`;
- `pending_domain_proposal`;
- `pending_domain_review`;
- recommendation continuity state;
- active clarification state.

The pre-routing gate at `aigol/cli/aigol_cli.py:3246-3279` decides whether routing should be bypassed.

### B. Conversational Routing / HIRR

If no pending state matches, the input is treated as a new conversational prompt and routed through:

```text
route_conversational_cli_intent(...)
```

Code location:

- `aigol/cli/aigol_cli.py:3280-3289`.

That route can invoke:

- Universal Translation;
- HIRR-compatible classification;
- conversational workflow selection;
- provider necessity or OCS cognition routing.

Conclusion:

```text
Lifecycle commands are not globally intercepted.
They are intercepted only when a matching in-memory workflow state exists.
```

## 4. OCS Misrouting Source

The operator-visible reason:

```text
Prompt requests comparative strategic analysis.
```

comes from routing visibility candidate selection.

Code location:

- `aigol/cli/aigol_cli.py:2327-2350`.

The OCS candidate includes `"continue"` among matched strategic cognition terms:

```text
"continue"
```

This means a bare or semi-bare lifecycle command containing `continue` may be visible as an OCS candidate when no lifecycle state catches it first.

The authoritative workflow selection can also enter OCS through `route_conversational_cli_intent(...)`, whose fallback checks include OCS cognition routing after earlier workflow-specific checks.

Code location:

- `aigol/runtime/conversational_cli_runtime.py:654-710`.

Conclusion:

```text
OCS routing is not the root cause.
The root cause is missing lifecycle command interception when workflow state is unavailable.
```

## 5. WAITING_FOR_OPERATOR State Preservation

### 5.1 Preserved In Memory

During the same Python process, `WAITING_FOR_OPERATOR` for native development continuation preserves enough state in memory:

- workflow id;
- native context capture;
- original human prompt;
- current chain id;
- latest chain id.

Code location:

- `aigol/cli/aigol_cli.py:5474-5479`.

### 5.2 Preserved In Replay But Not Restored For This Path

The native context replay exists:

- native development context integration replay;
- post-entry continuation gate replay;
- hardening evidence after turn completion;
- turn completion replay.

However, this audit found no restore path equivalent to governed development approval resume for:

```text
pending_post_entry_continuation
```

Governed development has replay restore handling:

- `aigol/cli/aigol_cli.py:3205-3215`;
- `aigol/cli/aigol_cli.py:8070-8088`.

Native post-entry continuation does not have equivalent replay-backed restoration.

Conclusion:

```text
WAITING_FOR_OPERATOR native continuation context is same-process state.
It is not currently reconstructed from replay on ACLI restart.
```

## 6. Replay Correctness

### 6.1 Same-Session Correct Replay

When `pending_post_entry_continuation` exists and `continue ppp` matches, replay records lifecycle continuation:

```text
TURN-xxxxxx/post_entry_continuation_gate/
TURN-xxxxxx/post_context_continuation/
```

The replay path records workflow continuation, not a new conversational intent.

Relevant tests:

- `tests/test_conversation_native_development_context_integration_v1.py`
- `tests/test_acli_certified_continuation_orchestration_v1.py`

### 6.2 Missing-State Incorrect Replay Semantics

When `pending_post_entry_continuation` is absent, the same text is recorded as a new conversational turn:

```text
TURN-xxxxxx/conversational_cli_routing/
TURN-xxxxxx/source_router/
TURN-xxxxxx/universal_intake/
```

If routed to OCS and provider is unavailable, replay records a new cognition attempt and fail-closed provider path, not a lifecycle continuation attempt.

Fail-closed replay is still valid, but it is not semantically the intended workflow continuation lineage.

Conclusion:

```text
Replay is mechanically correct.
Replay lineage semantics are wrong when lifecycle state is not restored before routing.
```

## 7. Command Family Review

| Command | Current handling | Risk |
| --- | --- | --- |
| `continue` | No generic lifecycle interceptor. May route as new conversational input unless a workflow-specific matcher accepts it. | High |
| `continue ppp` | Same-session native continuation interceptor exists. Cross-session or missing pending state routes as new input. | Confirmed |
| `approve` | Normalized by `normalize_human_decision(...)`; intercepted only when pending approval/proposal state exists. | Medium |
| `resume` | Governed development approval has replay-backed resume detection; native post-entry continuation does not. | Medium |
| `cancel` | No centralized lifecycle command handling found. Likely routes as new conversational prompt unless workflow-specific logic exists elsewhere. | Medium |
| `retry` | No centralized ACLI lifecycle retry command found in interactive conversation path. Retry appears in other runtime/operator modules, not as a universal ACLI lifecycle command. | Medium |
| `clarify` | Active clarification reply handling exists, but generic `clarify` is not a universal lifecycle command. | Medium |
| `reject` | Normalized and intercepted when pending approval/proposal state exists. Otherwise may route as a new prompt. | Medium |
| `request modification` | Normalized and intercepted when pending approval/proposal state exists. Otherwise may route as a new prompt. | Medium |

Approval command normalization:

- `aigol/runtime/human_decision_runtime.py:134-149`.

Governed development resume command detection:

- `aigol/cli/aigol_cli.py:8070-8088`.

No comparable universal lifecycle command dispatcher exists for the full command family.

## 8. Root Cause

Root cause:

```text
Lifecycle command routing is stateful and fragmented.
```

More specifically:

1. `continue ppp` is recognized only when `pending_post_entry_continuation` exists in memory.
2. `pending_post_entry_continuation` is not restored from replay after ACLI restart.
3. There is no universal lifecycle-command pre-router that checks active workflow state before Human Intent Resolution.
4. If no stateful gate matches, lifecycle commands fall through to `route_conversational_cli_intent(...)`.
5. The routing visibility OCS classifier treats `"continue"` as a strategic-analysis signal.

Confirmed defect:

```text
Lifecycle continuation commands can incorrectly re-enter conversational routing when active lifecycle state is absent from memory.
```

Scope:

```text
The defect is not limited to continue ppp.
It affects any lifecycle command whose correct interpretation depends on pending workflow state that is not restored or centrally resolved before routing.
```

## 9. Affected Runtimes

Affected:

- `aigol/cli/aigol_cli.py`
  - interactive input loop;
  - stateful pre-routing gate;
  - native development continuation branch;
  - routing visibility analysis;
  - governed development approval resume path.

- `aigol/runtime/post_entry_continuation_gate_runtime.py`
  - valid continuation gate exists;
  - depends on being invoked with preserved lifecycle context.

- `aigol/runtime/context_assembled_to_ppp_routing_continuation.py`
  - valid continuation runtime exists;
  - not reached when pending state is absent.

- `aigol/runtime/conversational_cli_runtime.py`
  - invoked as fallback when stateful lifecycle command interception fails.

- `aigol/runtime/human_decision_runtime.py`
  - approval decision normalization exists, but only acts with pending approval state.

Not the root cause:

- provider unavailable handling;
- fail-closed behavior;
- worker execution protections;
- replay hash verification.

## 10. Governance Impact

Governance boundaries are preserved:

- provider failure fails closed;
- no worker is invoked unless governed continuation reaches worker path;
- no approval is inferred;
- no execution bypass was identified.

Governance issue:

```text
Operator lifecycle intent may be interpreted by the wrong governance path.
```

This is a workflow continuity defect, not an authority bypass.

## 11. UX Impact

Operator impact is significant:

- operator follows the displayed command exactly;
- system appears to ignore workflow context;
- provider failure appears unrelated to the operator’s intended continuation;
- replay shows a new cognition path instead of obvious workflow continuation;
- confidence in `WAITING_FOR_OPERATOR` prompts is reduced.

The message `continue ppp` is currently too dependent on hidden in-memory state.

## 12. Architectural Impact

No new architecture is required.

Existing architecture already contains:

- lifecycle state;
- replay evidence;
- continuation gates;
- approval resume patterns;
- fail-closed routing;
- stateful pre-routing gate.

Needed repair is wiring and persistence, not redesign.

## 13. Expected Implementation Flow

Expected lifecycle command handling:

```text
operator input
-> capture raw prompt
-> allocate turn
-> detect lifecycle command
-> inspect active workflow state from memory and replay
-> if active lifecycle state matches:
      continue inside workflow-specific lifecycle runtime
      bypass HIRR
      bypass conversational routing
      bypass provider necessity classification unless workflow explicitly requires it
   else:
      fail closed or route as new prompt only if it is not a lifecycle command
```

For `continue ppp` specifically:

```text
WAITING_FOR_OPERATOR from NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
-> continue ppp
-> restore pending native context from replay if needed
-> evaluate_post_entry_continuation_gate(...)
-> continue_context_assembled_to_ppp_routing(...)
-> record continuation replay
```

## 14. Recommended Repair Strategy

Minimal repair proposal:

1. Add a pre-routing lifecycle command resolver inside `run_interactive_conversation(...)`.
2. Before `stateful_pre_routing_gate`, reconstruct active lifecycle state from replay when possible.
3. Add replay-backed restore for `pending_post_entry_continuation`, modeled after governed development proposal restore.
4. Treat recognized lifecycle commands with no matching active lifecycle state as fail-closed or explicit clarification, not as ordinary new prompts.
5. Remove or deprioritize `"continue"` as an OCS routing signal unless paired with strategic-analysis terms and no lifecycle state exists.
6. Record replay evidence that a lifecycle command was recognized and either continued or failed closed due to missing active workflow state.

Feature-freeze compatibility:

- no new governance concept;
- no new workflow;
- no new authority model;
- no provider authority;
- no worker authority;
- no autonomous improvement.

Implementation complexity:

```text
MODERATE
```

Reason:

- the same-session continuation path already exists;
- repair mainly requires replay restore and pre-routing command precedence;
- regression coverage must cover multiple command families.

## 15. Regression Test Requirements

Required tests:

### continue

- pending native workflow exists;
- operator enters `continue`;
- system must not enter HIRR;
- expected outcome should be either workflow-specific clarification or fail-closed missing explicit `ppp`, not OCS routing.

### continue ppp

- same-session:
  - `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION`
  - `WAITING_FOR_OPERATOR`
  - `continue ppp`
  - reaches `post_entry_continuation_gate`
  - reaches `post_context_continuation`
  - no conversational routing replay for the continuation turn.

- cross-session:
  - first session reaches `WAITING_FOR_OPERATOR`;
  - restart ACLI;
  - enter `continue ppp`;
  - restored lifecycle state is used;
  - no HIRR or OCS route.

### approve

- pending approval exists;
- `approve` continues approval lifecycle;
- no Human Intent Resolution;
- no provider routing.

### resume

- resumable governed development proposal exists;
- `resume` or approved resume command re-presents proposal;
- no execution from bare approval after resume;
- no unrelated routing.

### cancel

- active workflow exists;
- `cancel` records cancellation or fails closed with explicit unsupported lifecycle command;
- no new conversational intent.

### retry

- active failed workflow exists;
- `retry` either enters certified retry path if one exists or fails closed as unsupported lifecycle command;
- no provider routing unless workflow explicitly requires it.

### clarify

- active clarification exists;
- `clarify` is treated as lifecycle clarification command or asks for clarification text;
- no unrelated HIRR rerouting.

### Replay Continuity

For every lifecycle command:

- workflow identity preserved;
- chain id preserved;
- originating turn reference preserved;
- lifecycle continuation replay recorded;
- absence of `conversational_cli_routing` replay on lifecycle continuation turns where routing is bypassed;
- no provider invocation unless selected workflow explicitly requires provider-backed continuation.

## 16. Validation Performed

Audit validation used code inspection of:

- `aigol/cli/aigol_cli.py`;
- `aigol/runtime/post_entry_continuation_gate_runtime.py`;
- `aigol/runtime/context_assembled_to_ppp_routing_continuation.py`;
- `aigol/runtime/conversational_cli_runtime.py`;
- `aigol/runtime/human_decision_runtime.py`;
- existing native context continuation tests.

Validation commands executed for this documentation-only audit:

```text
git diff --check
python -m pytest tests/test_conversation_native_development_context_integration_v1.py -q
python -m pytest tests/test_post_entry_continuation_gate_runtime_v1.py -q
python -m pytest tests/test_acli_certified_continuation_orchestration_v1.py -q
```

Observed validation results:

| Command | Result |
| --- | --- |
| `git diff --check` | PASS |
| `python -m pytest tests/test_post_entry_continuation_gate_runtime_v1.py -q` | PASS, 6 passed |
| `python -m pytest tests/test_conversation_native_development_context_integration_v1.py -q` | FAIL, 2 failed and 5 passed |
| `python -m pytest tests/test_acli_certified_continuation_orchestration_v1.py -q` | FAIL, 1 failed and 2 passed |

Observed failing assertions:

- `test_interactive_conversation_post_entry_clarification_resumes_continuation`: expected `failed_turns == 0`, observed `failed_turns == 1`.
- `test_interactive_conversation_auto_continues_context_assembled_to_ppp`: expected `turn["context_status"]`, observed missing key.
- `test_development_acli_auto_continue_reaches_replay_certification`: expected `turn["post_entry_continuation_gate_status"]`, observed missing key.

Validation interpretation:

```text
The focused continuation gate unit tests pass.
The interactive continuation tests currently fail around turn-level lifecycle continuation metadata and successful continuation completion.
These failures are consistent with the audit finding that lifecycle continuation state and replay-visible continuation metadata are fragile in the live ACLI interaction path.
```

## 17. Final Verdict

Defect confirmed.

`continue ppp` is correctly handled inside the same interactive process when `pending_post_entry_continuation` exists. However, lifecycle command handling is fragmented and not replay-restored for native post-entry continuation. When pending state is missing, lifecycle commands can re-enter Human Intent Resolution / conversational routing and may be routed to OCS cognition.

Final verdict:

```text
LIFECYCLE_COMMAND_ROUTING_AUDIT_COMPLETE
```
