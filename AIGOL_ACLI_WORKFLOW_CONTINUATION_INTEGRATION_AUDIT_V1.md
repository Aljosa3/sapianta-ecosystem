# AIGOL_ACLI_WORKFLOW_CONTINUATION_INTEGRATION_AUDIT_V1

## Objective

Determine why ACLI reaches certified lifecycle entry points but does not continue into the already-certified continuation/runtime chain during real CLI usage.

This audit does not redesign architecture, governance, worker lifecycle, or runtime semantics.

## Runtime Evidence

Runtime command executed:

```bash
python -m aigol.cli.aigol_cli conversation \
  --session-id ACLI-AUDIT-TEMP \
  --runtime-root /tmp/aigol_acli_audit_runtime \
  --created-at 2026-06-15T00:00:00Z
```

Prompt:

```text
Create a validation capability for Product 1 AI Decision Validator.
```

Observed CLI result:

```text
workflow: NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
context_status: CONTEXT_ASSEMBLED
provider_necessity_classification: PROVIDER_REQUIRED_FOR_PROPOSAL
canonical_chain_id: CHAIN-77BF803E2A9B5FCB
Current Lifecycle Stage: CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATED
WORKFLOW COMPLETE: TRUE
```

Replay evidence created:

```text
TURN-000001/conversational_cli_routing/
TURN-000001/source_router/
TURN-000001/universal_intake/
TURN-000001/native_development_task_intake/
TURN-000001/development_context_assembly/
TURN-000001/native_development_context_integration/
TURN-000001/chain_continuity/
TURN-000001/post_entry_continuation_gate/
TURN-000001/turn_completion/
```

No normal-run replay evidence was created for:

```text
TURN-000001/post_context_continuation/
TURN-000001/certified_development_continuation/
TURN-000001/execution_authorization/
TURN-000001/worker_invocation_request/
TURN-000001/worker_lifecycle_continuation/
```

## Runtime Flow

Actual runtime chain executed from the real CLI path:

```text
Human Prompt
-> conversational CLI routing
-> source-of-truth router
-> universal intake
-> run_conversation_native_development_context_integration
-> native development task intake
-> development context assembly
-> conversation native development context integration
-> conversation chain continuity
-> evaluate_post_entry_continuation_gate
-> turn completion / replay
-> STOP
```

Source boundary:

- `aigol/cli/aigol_cli.py:4787` enters `CONVERSATIONAL_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION`.
- `aigol/cli/aigol_cli.py:4788` calls `run_conversation_native_development_context_integration(...)`.
- `aigol/cli/aigol_cli.py:4811` calls `evaluate_post_entry_continuation_gate(...)`.
- `aigol/cli/aigol_cli.py:4837` only calls downstream continuation if the gate status is `CONTINUATION_ALLOWED`.

## Certified Runtime Flow

Expected certified continuation chain:

```text
Human Prompt
-> Router
-> Lifecycle Entry
-> Post Entry Continuation Gate
-> Context Assembled to PPP Routing Continuation
-> Execution Summary / governed implementation dry run
-> Human Confirmation / authorization boundary
-> Execution Authorization
-> Worker Invocation Request
-> Worker Assignment
-> Worker Dispatch
-> Worker Invocation
-> Replay / result validation / certification
```

The downstream continuation path exists in the CLI:

- `aigol/cli/aigol_cli.py:4845` calls `continue_context_assembled_to_ppp_routing(...)`.
- The worker continuation helper proceeds through implementation handoff visibility, governed implementation dry run, execution authorization, worker invocation request, and worker lifecycle continuation.

## Post Entry Gate Finding

ACLI does invoke `POST_ENTRY_CONTINUATION_GATE_ARTIFACT_V1` in the normal real CLI path.

Recorded gate artifact:

```text
artifact_type: POST_ENTRY_CONTINUATION_GATE_ARTIFACT_V1
gate_status: CLARIFICATION_REQUIRED
continuation_allowed: false
execution_capable: true
continuation_runtime: context_assembled_to_ppp_routing_continuation
execution_summary_required: false
human_confirmation_required: false
authorization_required: false
decision_reason: execution-capable lifecycle entry requires explicit continuation approval
```

The gate behavior is defined in `aigol/runtime/post_entry_continuation_gate_runtime.py:174`. For native development context integration, continuation is allowed only when:

```text
auto_continue_enabled == true
OR
the human prompt explicitly contains both "continue" and "ppp"
```

The CLI repeats the same condition in `_post_context_continuation_should_run(...)` at `aigol/cli/aigol_cli.py:652`.

## Divergence Point

The divergence point is not before the post-entry gate.

The divergence point is:

```text
POST_ENTRY_CONTINUATION_GATE_ARTIFACT_V1
-> gate_status = CLARIFICATION_REQUIRED
-> continuation_allowed = false
-> no post_context_continuation runtime invoked
```

The first real runtime stop point is therefore:

```text
POST_ENTRY_CONTINUATION_GATE_RETURNED_WITH_CLARIFICATION_REQUIRED
```

The user-facing workflow status then reports:

```text
Current Lifecycle Stage: CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATED
WORKFLOW COMPLETE: TRUE
```

This hides the fact that the post-entry gate was reached but returned a non-continuing execution-capable state.

## Suggested Actions Finding

Suggested actions returned by the native context integration runtime:

```text
show-chain <chain-id>
show-full-lineage <chain-id>
prepare governed development proposal contract
```

Status:

| Suggested action | Status | Finding |
| --- | --- | --- |
| `show-chain <chain-id>` | Executable as top-level CLI subcommand | Registered at `aigol/cli/aigol_cli.py:2642` and dispatched at `aigol/cli/aigol_cli.py:7688`. |
| `show-full-lineage <chain-id>` | Executable as top-level CLI subcommand | Registered at `aigol/cli/aigol_cli.py:2663` and dispatched at `aigol/cli/aigol_cli.py:7709`. |
| `prepare governed development proposal contract` | Informational text only in ACLI conversation | No matching CLI subcommand or conversational route was found. |

Real command validation:

```bash
python -m aigol.cli.aigol_cli show-chain CHAIN-77BF803E2A9B5FCB \
  --replay-root /tmp/aigol_acli_audit_runtime/ACLI-AUDIT-TEMP
```

returned:

```text
status: READY
conversation: True
execution_lifecycle_artifacts: 0
workers_dispatched: False
workers_invoked: False
fail_closed: False
```

Entering `show-chain ...`, `show-full-lineage ...`, or `prepare governed development proposal contract` as freeform conversation text routes to:

```text
DEFAULT_PROVIDER_ASSISTED_CONVERSATION
FAILED_CLOSED
```

Thus the suggested actions are partly executable, but only outside the conversational prompt loop or through missing conversational command handling.

## Auto-Continue Comparison

Runtime command executed:

```bash
python -m aigol.cli.aigol_cli conversation \
  --session-id ACLI-AUDIT-AUTO \
  --runtime-root /tmp/aigol_acli_audit_runtime \
  --created-at 2026-06-15T00:00:00Z \
  --auto-continue
```

With the same prompt, the post-entry gate recorded:

```text
gate_status: CONTINUATION_ALLOWED
continuation_allowed: true
execution_summary_required: true
human_confirmation_required: true
authorization_required: true
```

The CLI then created:

```text
TURN-000001/post_context_continuation/
```

and failed closed at:

```text
OpenAI provider request prompt is required
```

This confirms that the CLI can reach the certified continuation branch when the gate allows continuation, but the ordinary real CLI prompt does not satisfy the gate's explicit continuation condition.

## Root Cause

Single most probable root cause:

```text
ACLI records the post-entry continuation gate, but the normal conversational lifecycle output treats CLARIFICATION_REQUIRED as a completed workflow and does not convert that gate state into an operator-facing continuation prompt, pending continuation state, or executable conversational continuation command.
```

Secondary contributing issue:

```text
Suggested action strings are not consistently ACLI-executable inside the conversation loop. Top-level inspection commands exist, but freeform conversational handling routes them to DEFAULT_PROVIDER_ASSISTED_CONVERSATION.
```

## Minimal Repair

Smallest governance-preserving repair:

```text
When NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION reaches POST_ENTRY_CONTINUATION_GATE_ARTIFACT_V1 with gate_status = CLARIFICATION_REQUIRED, ACLI should record and expose a pending continuation state instead of marking the workflow complete.
```

The pending state should accept a narrow deterministic follow-up such as:

```text
continue ppp
```

and then re-enter the existing `continue_context_assembled_to_ppp_routing(...)` path only if the recorded gate state, replay reference, provider necessity classification, and human continuation confirmation all validate.

This preserves:

- governance authority;
- replay evidence;
- execution summary enforcement;
- human confirmation;
- authorization;
- fail-closed behavior.

Optional adjacent repair:

```text
Register conversation-loop handling for read-only suggested commands:
show-chain <chain-id>
show-full-lineage <chain-id>
```

These should dispatch to existing read-only chain inspection commands rather than provider-assisted conversation.

## Final Fields

```text
ACLI_CONTINUATION_INTEGRATION_PRESENT = PARTIAL
POST_ENTRY_GATE_REACHED = YES
EXECUTION_SUMMARY_REACHED_FROM_CLI = NO_NORMAL_RUN_YES_GATE_REQUIRED_WITH_AUTO_CONTINUE
AUTHORIZATION_REACHED_FROM_CLI = NO
WORKER_LIFECYCLE_REACHED_FROM_CLI = NO
FIRST_RUNTIME_STOP_POINT = POST_ENTRY_CONTINUATION_GATE_RETURNED_WITH_CLARIFICATION_REQUIRED
CLI_CERTIFICATION_DIVERGENCE_IDENTIFIED = YES
ROOT_CAUSE = ACLI reaches the post-entry gate but treats CLARIFICATION_REQUIRED as workflow-complete output instead of exposing a pending continuation/confirmation path into the certified continuation runtime.
MINIMAL_REPAIR = Add deterministic conversational continuation handling for recorded post-entry CLARIFICATION_REQUIRED state, then invoke the existing certified continuation only after replay-bound human continuation confirmation.
PRIMARY_INTERFACE_OPERATIONALLY_READY = NO
```
