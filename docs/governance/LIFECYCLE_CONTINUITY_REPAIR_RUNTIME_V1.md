# LIFECYCLE_CONTINUITY_REPAIR_RUNTIME_V1

Status: IMPLEMENTED

Target verdict:

```text
LIFECYCLE_CONTINUITY_REPAIR_RUNTIME_READY
```

## 1. Purpose

This artifact records the Platform Core Generation 1 feature-freeze repair for lifecycle continuation commands.

The repair addresses the defect confirmed by `LIFECYCLE_COMMAND_ROUTING_AUDIT_V1`: lifecycle commands such as `continue ppp` could continue the active native development context workflow only while `pending_post_entry_continuation` remained in process memory.

When process memory was unavailable, the command could fall through into Human Intent Resolution, conversational routing, provider necessity classification, and OCS cognition routing.

## 2. Scope

Implemented scope:

- replay-backed restoration of pending native post-entry continuation state;
- pre-routing lifecycle command detection for restored continuation;
- lifecycle command precedence over conversational routing while a workflow is waiting;
- operator routing visibility aligned with lifecycle continuation state;
- focused regression coverage for same-session and cross-session continuation.

Out of scope:

- new architecture;
- new workflows;
- new approval semantics;
- new replay model;
- changes to Human Intent Resolution;
- provider invocation changes;
- worker execution changes.

## 3. Runtime Changes

Modified:

- `aigol/cli/aigol_cli.py`
- `aigol/runtime/conversational_cli_runtime.py`
- `tests/test_conversation_native_development_context_integration_v1.py`

The repair remains in the ACLI interactive lifecycle wiring layer.

## 4. Replay Restoration

ACLI now restores pending native post-entry continuation state from replay before conversational routing when the operator enters:

```text
continue
continue ppp
```

Restoration uses existing replay evidence:

- native development context integration replay;
- post-entry continuation gate replay;
- chain continuity replay.

The restored state preserves:

- workflow id;
- context status;
- context hash;
- canonical chain id;
- current chain id;
- latest chain id;
- pending continuation status.

The restore writes replay-visible evidence:

```text
pending_post_entry_continuation_restore/
000_pending_post_entry_continuation_restored.json
```

## 5. Lifecycle Command Precedence

Lifecycle commands are detected before conversational routing while a workflow is waiting.

Covered commands:

- `continue`
- `continue ppp`
- `approve`
- `resume`
- `retry`
- `cancel`
- `clarify`

When a valid pending native continuation exists:

```text
continue / continue ppp
-> restore lifecycle state if needed
-> evaluate post-entry continuation gate
-> continue context assembled to PPP routing
```

When an unsupported lifecycle command is entered while native continuation is pending:

```text
lifecycle command
-> remain in lifecycle path
-> fail closed or require explicit workflow-supported continuation
-> do not route as a new conversational prompt
```

## 6. Routing Protection

Lifecycle commands no longer create `conversational_cli_routing` replay evidence while a pending lifecycle workflow is being continued.

This prevents accidental entry into:

- Human Intent Resolution;
- conversational routing;
- provider necessity classification;
- OCS LLM cognition routing.

Provider routing may still occur only after the certified continuation runtime explicitly enters the provider-backed PPP preparation path.

## 7. Governance Impact

Governance boundaries are preserved:

- no approval is inferred;
- no execution is authorized by continuation restoration;
- no worker is invoked by restoration;
- no provider is invoked by restoration;
- unsupported lifecycle commands fail closed rather than rerouting.

Human authority remains unchanged.

## 8. Replay Impact

Replay continuity is improved.

The repaired flow records:

- restored lifecycle continuation evidence;
- preserved chain identity;
- post-entry continuation gate evidence;
- post-context continuation evidence when continuation is allowed.

Replay remains the source of truth.

## 9. Feature-Freeze Compliance

The repair is feature-freeze compliant because it:

- fixes an implementation defect;
- uses existing workflow identifiers;
- uses existing replay evidence;
- preserves existing governance semantics;
- introduces no new authority model;
- introduces no new architectural concept.

## 10. Regression Coverage

Regression coverage verifies:

- same-session `continue ppp`;
- cross-session `continue`;
- cross-session `continue ppp`;
- lifecycle command family interception while native continuation is pending;
- no conversational routing replay is created for lifecycle continuation commands;
- workflow identity is preserved;
- replay restoration evidence is recorded.

## 11. Final Verdict

The lifecycle continuity repair is implemented.

Final verdict:

```text
LIFECYCLE_CONTINUITY_REPAIR_RUNTIME_READY
```
