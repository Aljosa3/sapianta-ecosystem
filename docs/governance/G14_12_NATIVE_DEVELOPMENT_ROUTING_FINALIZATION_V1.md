# G14-12 Native Development Routing Finalization V1

Status: native development routing certified.

Final verdict: NATIVE_DEVELOPMENT_ROUTING_CERTIFIED

## 1. Executive Summary

G14-12 investigated the Generation 14 acceptance-test defect where a real implementation request completed natural-language understanding, workspace inspection, governed summary presentation, and human approval, but did not enter the certified Native Development Runtime after `/approve`.

The defect was implementation routing, not architecture.

Root cause:

- native development prompt detection did not include improvement and repair phrasing for provider availability and provider resilience work;
- Platform Core project guidance did not treat provider availability phrasing as sufficiently specific for a governed implementation summary;
- conversational CLI task-completion routing treated broad `improve provider` requests as provider-layer review, which allowed capability coverage to intercept genuine implementation work.

The repair preserves all certified ownership boundaries.

After correction, a live `aigol next` approval scenario with a genuine implementation request reached:

```text
AiGOL Next
-> PGSP / conversational routing evidence
-> UBTR / canonical semantic artifact evidence
-> CSA / native-development workflow selection
-> Platform Core / native development context integration
-> Governance / execution authorization
-> Provider / OpenAI proposal production
-> Worker Platform / worker invocation
-> Result validation
-> Replay certification
```

Final verdict: NATIVE_DEVELOPMENT_ROUTING_CERTIFIED

## 2. Investigation Scope

The investigation reviewed:

- conversational workflow approval transition;
- runtime binding after `/approve`;
- native development prompt detection;
- capability audit and task-completion routing;
- provider-layer routing;
- Platform Core project guidance specificity;
- post-entry continuation from native development context to PPP routing;
- provider handoff, worker invocation, result validation, and Replay certification evidence.

No Platform Core redesign was required.

## 3. Reproduction Evidence

The original acceptance-test symptom was reproduced with:

```text
prompt: Improve provider availability handling.
session_id: G14-12-REPRO-IMPROVE
runtime_root: /tmp/aigol_g14_12_repro_improve
```

Observed result before repair:

```text
runtime_binding_status: AIGOL_NEXT_RUNTIME_BINDING_NOT_REQUIRED
runtime_entered: false
current_stage: Classify Capability Coverage
next_expected_operation: Existing Capability Audit
```

This confirmed that the request was being classified as coverage/audit work instead of native development execution.

A later interactive validation showed the corrected native route but exposed provider availability under sandboxed network conditions:

```text
session_id: G14-12-APPROVAL-ROUTING-VALIDATION
workflow_id: NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
post_entry_gate_status: CONTINUATION_ALLOWED
post_context_continuation: FAILED_CLOSED
failure_reason: OpenAI provider unavailable
```

That second finding was operational availability, not routing.

## 4. Root Cause Analysis

### 4.1 Native Development Detection Gap

Implementation-oriented requests such as:

```text
Improve provider availability handling.
Fix provider resilience for native development routing.
```

were not consistently recognized as native development because the intake model emphasized create/build/add/implement phrasing and did not include provider availability or provider resilience as development subjects.

Repair:

- added improvement and repair verbs to native development prompt detection;
- added provider availability, availability handling, and provider resilience as native development subjects;
- preserved conservative exclusions for deployment and unrelated conversational prompts.

### 4.2 Project Guidance Specificity Gap

The guided development layer did not treat provider availability phrasing as sufficiently specific, which could prevent direct governed implementation summary flow.

Repair:

- added provider availability, provider resilience, and availability handling to the deterministic specificity terms used by Platform Core project services.

This keeps the decision in Platform Core project services and does not move guidance logic into AiGOL Next.

### 4.3 Provider-Layer Route Overmatch

Task-completion routing previously treated broad `improve provider` phrasing as provider-layer review.

This caused genuine implementation requests involving provider availability to be captured by an existing capability or provider-layer audit route.

Repair:

- narrowed the provider-layer route to explicit provider-layer, provider-boundary, provider-abstraction, provider-identity, or provider-authority phrasing;
- added provider availability and provider resilience subjects to the native development route;
- preserved the read-only provider-layer route for architecture-review prompts such as provider abstraction and authority separation.

## 5. Implementation Fix

Updated implementation surfaces:

| File | Change |
| --- | --- |
| `aigol/runtime/native_development_task_intake_runtime.py` | Recognizes improve/fix requests for provider availability, availability handling, and provider resilience as native development. |
| `aigol/runtime/platform_core_project_services.py` | Treats provider availability and resilience phrasing as specific enough for governed implementation summary generation. |
| `aigol/runtime/conversational_cli_runtime.py` | Narrows provider-layer read-only routing and routes provider availability improvement to native development context integration. |
| `tests/test_native_development_task_intake_and_session_resume_v1.py` | Adds regression coverage for provider availability and provider resilience native development detection. |
| `tests/test_conversational_cli_runtime_v1.py` | Adds routing regression coverage to keep implementation requests out of provider-layer audit routing. |
| `tests/test_g14_07_goal_oriented_development_experience_v1.py` | Adds interactive `/approve` regression coverage proving approved improvement requests enter the native runtime. |

The repair changes deterministic classification only.

It does not:

- redesign Platform Core;
- bypass PGSP, UBTR, CSA, Governance, Worker Platform, or Replay;
- move orchestration into AiGOL Next;
- authorize or execute inside AiGOL Next;
- change the certified runtime ownership model.

## 6. Updated Runtime Trace

Live validation command:

```text
python -m aigol.cli.aigol_cli next \
  --session-id G14-12-APPROVAL-ROUTING-VALIDATION-ESCALATED \
  --runtime-root /tmp/aigol_g14_12_approval_routing_validation_escalated \
  --workspace /home/pisarna/work/sapianta \
  --created-at 2026-07-03T00:00:00Z
```

Interactive transcript:

```text
AiGOL> Improve provider availability handling.
AiGOL> /send
Governed implementation summary
runtime_after_approval: CERTIFIED_PLATFORM_CORE_RUNTIME

AiGOL> /approve
Human confirmation recorded. Entering certified runtime.
runtime_binding_status: AIGOL_NEXT_RUNTIME_BOUND
runtime_entered: True
governance_authorization_reached: True
provider_invocation_reached: True
worker_execution_reached: True
replay_certification_reached: True
manual_chatgpt_codex_transfer_required: False
```

Runtime evidence root:

```text
/tmp/aigol_g14_12_approval_routing_validation_escalated/G14-12-APPROVAL-ROUTING-VALIDATION-ESCALATED/TURN-000001
```

## 7. Evidence Inventory

| Stage | Evidence |
| --- | --- |
| Native routing | `conversational_cli_routing/000_conversational_routing_decision_recorded.json` recorded `workflow_id: NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION`. |
| PGSP / interface routing | `conversational_cli_routing/` recorded universal translation and route selection for the submitted turn. |
| UBTR | `conversational_cli_routing/ubtr_semantic_cognition_orchestration/` and `canonical_semantic_artifact/` recorded semantic processing evidence. |
| CSA | `conversational_cli_routing/canonical_semantic_artifact/` supported native-development workflow selection. |
| Native context | `native_development_task_intake/` and `native_development_context_integration/` recorded native development intake and context assembly. |
| Continuation gate | `post_entry_continuation_gate/000_post_entry_continuation_gate_recorded.json` recorded `CONTINUATION_ALLOWED`. |
| Provider | `post_context_continuation/conversation_ppp_routing/provider_proposal_production/` recorded provider request, response artifact capture, and development proposal production. |
| Governance | `certified_development_continuation/execution_authorization/003_authorization_result_recorded.json` recorded `authorization_status: EXECUTION_AUTHORIZED`. |
| Worker | `certified_development_continuation/worker_lifecycle_continuation/worker_invocation/003_invocation_result_recorded.json` recorded `invocation_status: WORKER_INVOKED`. |
| Result validation | `certified_development_continuation/worker_lifecycle_continuation/result_validation/002_result_validation_returned.json` recorded `validation_status: RESULT_VALIDATION_COMPLETED`. |
| Replay certification | `certified_development_continuation/worker_lifecycle_continuation/replay_certification/001_replay_certification_returned.json` recorded `certification_status: REPLAY_CERTIFICATION_COMPLETED`. |

## 8. Responsibility Verification

| Component | G14-12 Finding |
| --- | --- |
| AiGOL Next | Presents conversation, collects `/send` and `/approve`, and delegates. It does not authorize, execute, or own Replay. |
| PGSP | Remains the governed interface/session invocation boundary. |
| UBTR | Remains semantic interpretation owner. |
| CSA | Remains structured semantic artifact owner for normalized intent. |
| Platform Core / OCS | Owns native development context, routing continuation, orchestration, and execution coordination. |
| Governance | Owns execution authorization. |
| Provider Platform | Owns provider invocation through the configured provider adapter. |
| Worker Platform | Owns worker assignment, dispatch, invocation, and result capture. |
| Replay | Owns evidence persistence and certification. |
| Architectural Health | Remains advisory only. |

No responsibility migration was detected.

## 9. Regression Coverage

Regression tests now verify:

- provider availability improvement requests are native development prompts;
- provider resilience repair requests are native development prompts;
- provider availability improvement routes to `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION`;
- provider abstraction and authority prompts still route to provider-layer review;
- interactive `/approve` enters the native runtime and reaches provider, worker, and Replay certification using the existing test adapter.

## 10. Operational Readiness Assessment

The G14-12 acceptance scenario now reaches the complete certified native development runtime after human approval.

The corrected route satisfies:

```text
/approve
-> Runtime Binding
-> Native Development Runtime
-> PGSP
-> UBTR
-> CSA
-> Platform Core
-> Governance
-> Provider
-> Worker
-> Result validation
-> Replay certification
```

The original capability coverage diversion is resolved.

## 11. Validation Evidence

Validation performed:

```text
python -m py_compile aigol/runtime/native_development_task_intake_runtime.py aigol/runtime/platform_core_project_services.py aigol/runtime/conversational_cli_runtime.py aigol/runtime/context_assembled_to_ppp_routing_continuation.py aigol/acli_next/conversational.py aigol/cli/aigol_cli.py
```

Focused regression validation performed:

```text
python -m pytest tests/test_native_development_task_intake_and_session_resume_v1.py tests/test_g14_07_goal_oriented_development_experience_v1.py tests/test_g14_04_conversational_development_workflow_v1.py tests/test_g14_03_aigol_next_runtime_binding_v1.py tests/test_conversational_cli_runtime_v1.py::test_task_completion_repair_routes_real_development_prompts_before_provider_fallback tests/test_conversational_cli_runtime_v1.py::test_conversational_intents_route_to_certified_workflows tests/test_conversational_cli_runtime_v1.py::test_interactive_conversation_routes_readonly_provider_layer_prompt
```

Interactive runtime validation performed with a real provider-enabled session:

```text
session_id: G14-12-APPROVAL-ROUTING-VALIDATION-ESCALATED
runtime_binding_status: AIGOL_NEXT_RUNTIME_BOUND
runtime_entered: True
governance_authorization_reached: True
provider_invocation_reached: True
worker_execution_reached: True
replay_certification_reached: True
manual_chatgpt_codex_transfer_required: False
```

Whitespace validation performed:

```text
git diff --check
```

## 12. Certification Summary

G14-12 resolves the native development routing implementation gap discovered during the real Generation 14 acceptance test.

Genuine implementation requests involving provider availability and resilience now deterministically enter the certified Native Development Runtime after human approval and are not intercepted by capability coverage or provider-layer audit routing.

All certified ownership boundaries remain intact.

Final verdict: NATIVE_DEVELOPMENT_ROUTING_CERTIFIED
