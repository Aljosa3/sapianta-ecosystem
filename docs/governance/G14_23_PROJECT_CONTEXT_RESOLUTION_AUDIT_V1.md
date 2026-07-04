# G14-23 Project Context Resolution Audit V1

Status: project context resolution partially supported.

Final verdict: PROJECT_CONTEXT_RESOLUTION_PARTIALLY_SUPPORTED

## 1. Executive Summary

G14-23 audited the Native Development Intake workflow to determine whether an explicit milestone identifier is a canonical Platform Core requirement or a legacy implementation artifact.

The audit found:

- explicit milestone identifiers are not universally required by the current implementation;
- plain deterministic native-development requests can be accepted without a human-provided milestone;
- the current intake runtime deterministically assigns `AIGOL_GENERIC_DEVELOPMENT_TASK_V1` for recognized plain native-development prompts;
- the exact audit example, `Implement a governance documentation validator.`, is accepted by current Native Development Intake;
- the live `aicli` runtime reached Native Development Intake, context assembly, and PPP routing before failing closed at OpenAI provider availability under the restricted environment;
- richer Project Workspace, Project Guidance, Goal Mapping, Contextual Task Mapping, Knowledge Reuse, and Replay history exist as Platform Core capabilities, but they are not currently passed into Native Development Intake.

Conclusion:

The old hard requirement for a human-supplied milestone identifier is not canonical for plain deterministic development requests. It remains present as a fallback branch in Native Development Intake for prompts that are not recognized as plain native-development requests and do not contain exactly one explicit milestone id.

Project context resolution is therefore partially supported, not complete.

Final verdict: PROJECT_CONTEXT_RESOLUTION_PARTIALLY_SUPPORTED

## 2. Audit Scope

The audit reviewed:

- `aicli` reference UHI approval path;
- AiGOL Next runtime binding;
- Development Intent Resolution;
- Native Development Intake;
- Native Development Context Integration;
- Development Context Assembly;
- PPP routing continuation;
- Platform Core Project Services;
- Project Workspace / Guidance / Knowledge Reuse;
- runtime evidence from a real `aicli` session.

No architecture redesign was performed.

No implementation changes were made.

## 3. Runtime Call Graph

The audited path after human approval is:

```text
aicli
-> resolve_development_intent(...)
-> /approve
-> run_interactive_conversation(...)
-> conversational routing
-> run_conversation_native_development_context_integration(...)
-> run_native_development_task_intake(...)
-> assemble_development_context(...)
-> evaluate_post_entry_continuation_gate(...)
-> continue_context_assembled_to_ppp_routing(...)
-> run_conversation_ppp_routing_integration(...)
-> provider proposal production
```

Implementation evidence:

| Stage | Implementation |
| --- | --- |
| Reference UHI delegation | `aigol/cli/aicli.py` calls `resolve_development_intent(...)` and delegates approved requests to `run_interactive_conversation(...)`. |
| Runtime binding | `aigol/cli/aigol_cli.py` calls `run_interactive_conversation(...)` for runtime-bound prompts. |
| Native context path | `aigol/cli/aigol_cli.py` calls `run_conversation_native_development_context_integration(...)` for `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION`. |
| Native intake | `aigol/runtime/conversation_native_development_context_integration.py` calls `run_native_development_task_intake(...)`. |
| Milestone analysis | `aigol/runtime/native_development_task_intake_runtime.py` implements `_analyze_prompt(...)`. |
| Context assembly | `aigol/runtime/conversation_native_development_context_integration.py` calls `assemble_development_context(...)`. |
| PPP continuation | `aigol/runtime/context_assembled_to_ppp_routing_continuation.py` calls `run_conversation_ppp_routing_integration(...)`. |

## 4. Milestone Resolution Analysis

Native Development Intake analyzes the prompt in `_analyze_prompt(...)`.

The implementation first extracts explicit milestone ids:

```text
MILESTONE_PATTERN.findall(prompt)
```

It then has two branches:

| Branch | Condition | Result |
| --- | --- | --- |
| Plain native-development prompt | no explicit milestone and `is_plain_native_development_prompt(prompt)` is true | assigns `AIGOL_GENERIC_DEVELOPMENT_TASK_V1`. |
| Explicit milestone prompt | exactly one milestone id present | uses that milestone id. |
| Fail-closed fallback | zero or multiple milestone ids and not plain native-development | fails closed: `milestone id cannot be identified`. |

Implementation evidence:

```text
GENERIC_DEVELOPMENT_MILESTONE_ID = "AIGOL_GENERIC_DEVELOPMENT_TASK_V1"
```

For plain prompts, the runtime sets:

```text
requested_milestone_id: AIGOL_GENERIC_DEVELOPMENT_TASK_V1
requested_domain: AIGOL
requested_worker_family: CLAUDE_EXTERNAL
task_kind: WORKER
```

Finding:

The milestone id requirement is not canonical for all human requests. It is a remaining fallback assumption for prompts that the deterministic plain-native classifier does not accept.

## 5. Runtime Evidence

Command:

```text
./aicli --session-id G14-23-CONTEXT-AUDIT --runtime-root /tmp/aigol_g14_23_context_audit --workspace /home/pisarna/work/sapianta --created-at 2026-07-04T00:00:00Z
```

Submitted request:

```text
Implement a governance documentation validator.
```

The reference UHI rendered a governed implementation summary and accepted `/approve`.

Runtime result:

```text
runtime_status: REFERENCE_UHI_RUNTIME_PARTIALLY_BOUND
governance_authorization_reached: False
provider_invocation_reached: False
worker_execution_reached: False
replay_certification_reached: False
runtime_replay_reference: /tmp/aigol_g14_23_context_audit/G14-23-CONTEXT-AUDIT/TURN-000001
```

The partial result was caused by provider availability, not milestone identification.

## 6. Native Intake Evidence

Replay evidence:

```text
/tmp/aigol_g14_23_context_audit/G14-23-CONTEXT-AUDIT/TURN-000001/native_development_task_intake/000_native_development_task_intake_recorded.json
```

Observed values:

```text
intake_status: NATIVE_DEVELOPMENT_TASK_INTAKE_ACCEPTED
requested_milestone_id: AIGOL_GENERIC_DEVELOPMENT_TASK_V1
requested_domain: AIGOL
requested_worker_family: CLAUDE_EXTERNAL
requested_output_scope: ["AIGOL_GENERIC_DEVELOPMENT_TASK_V1", "WORKER_FOUNDATION"]
task_kind: WORKER
safe_for_native_development: true
failure_reason: null
```

Finding:

The exact audited natural-language prompt did not fail milestone resolution in the current implementation. It was accepted using deterministic generic project context.

## 7. Context Assembly Evidence

Replay evidence:

```text
/tmp/aigol_g14_23_context_audit/G14-23-CONTEXT-AUDIT/TURN-000001/native_development_context_integration/000_conversation_native_development_context_integrated.json
/tmp/aigol_g14_23_context_audit/G14-23-CONTEXT-AUDIT/TURN-000001/development_context_assembly/004_development_context_assembly_returned.json
```

Observed values:

```text
integration_status: CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATED
context_status: CONTEXT_ASSEMBLED
missing_context: []
ambiguous_context: []
provider_necessity_classification: PROVIDER_REQUIRED_FOR_PROPOSAL
failure_reason: null
```

Finding:

Platform Core assembled native development context after generic milestone resolution. Fail-closed did not occur in Native Development Intake or Development Context Assembly.

## 8. PPP Continuation Evidence

Replay evidence:

```text
/tmp/aigol_g14_23_context_audit/G14-23-CONTEXT-AUDIT/TURN-000001/post_context_continuation/000_post_context_continuation_recorded.json
/tmp/aigol_g14_23_context_audit/G14-23-CONTEXT-AUDIT/TURN-000001/post_context_continuation/conversation_ppp_routing/provider_proposal_production/003_provider_proposal_production_returned.json
```

Observed values:

```text
continuation_status: FAILED_CLOSED
failure_reason: OpenAI provider unavailable
operational_failure_classification: PROVIDER_AVAILABILITY
provider_resilience_status: PROVIDER_UNAVAILABLE_FAIL_CLOSED
production_status: FAILED_CLOSED
provider_invocation_status: PROVIDER_NOT_INVOKED
```

Finding:

The runtime failure happened after successful project context intake and assembly. It is unrelated to milestone lookup.

## 9. Project Context Evidence Map

| Context source | Implemented | Invoked in audited path | Available to Native Intake | Finding |
| --- | --- | --- | --- | --- |
| Project Workspace | Yes | Available in AiGOL Next workspace flows | No direct parameter into `run_native_development_task_intake(...)` | Implemented but not consumed by intake. |
| Project Guidance | Yes | Available through Platform Core project services | No direct parameter into intake | Implemented but not consumed by intake. |
| Knowledge Reuse | Yes | Available through `project_knowledge_context_from_workspace(...)` | No direct parameter into intake | Implemented but not consumed by intake. |
| Development Intent Resolution | Yes | `aicli` and runtime binding call `resolve_development_intent(...)` | Canonical prompt only reaches intake | Partially used. |
| Contextual Task Mapping | Yes | Available for goal-oriented requests | No direct parameter into intake | Implemented but not consumed by intake. |
| Goal Mapping | Yes | Available through `goal_mapping_from_workspace(...)` | No direct parameter into intake | Implemented but not consumed by intake. |
| Replay history | Yes | Workspace state records implementation history | No direct parameter into intake | Available but not directly used by intake. |
| Certified implementation history | Yes | Reflected in workspace state / knowledge index | No direct parameter into intake | Available but not directly used by intake. |

Evidence:

- `platform_core_project_services.py` defines workspace, guidance, goal mapping, contextual task mapping, knowledge reuse, and development intent resolution.
- `resolve_development_intent(...)` accepts `workspace_state`.
- Current `aicli` calls `resolve_development_intent(message=message, workspace_state=None)`.
- Native context integration calls `run_native_development_task_intake(...)` with prompt, session, turn, and replay metadata only.

## 10. Deterministic Evidence Analysis

Current Platform Core can deterministically derive:

| Derivation | Current support |
| --- | --- |
| Current project | Partial, via workspace/session context outside intake. |
| Current generation | Partial, via Project Guidance defaults and milestone parsing. |
| Existing milestone | Partial, through explicit milestone ids and knowledge index references. |
| Related milestone | Partial, through goal mapping and contextual task mapping. |
| Extension of existing capability | Partial, through Project Knowledge Reuse. |
| New milestone candidate | Partial, via generic `AIGOL_GENERIC_DEVELOPMENT_TASK_V1`; not yet a true candidate creation flow. |
| Clarification question | Supported for guided requests that lack deterministic specificity. |

Finding:

Deterministic project evidence exists, but Native Development Intake does not yet receive the full project context model. It can resolve plain implementation requests generically, but it cannot yet use workspace history to choose a more specific project/milestone context.

## 11. Legacy Analysis

The explicit milestone requirement is best classified as:

```text
historical implementation artifact / compatibility path
```

It is not proven to be:

- a Governance requirement;
- a Replay requirement;
- a canonical Platform Core requirement for all development requests.

Rationale:

- current runtime accepts plain native-development requests without explicit milestone identifiers;
- generic milestone support exists in Native Development Intake;
- fail-closed milestone-id logic remains only after the generic plain-native path is rejected;
- Platform Core project services already define deterministic context sources outside the explicit milestone branch.

## 12. Human Interaction Assessment

For:

```text
Implement a governance documentation validator.
```

Current Platform Core can:

- identify the request as guided native development;
- produce a governed implementation summary;
- accept the request as native development after approval;
- assign `AIGOL_GENERIC_DEVELOPMENT_TASK_V1`;
- resolve domain `AIGOL`;
- assemble development context;
- continue toward provider proposal production.

Current Platform Core cannot yet fully:

- select a more specific active generation from workspace state inside Native Development Intake;
- choose a related certified milestone from Project Knowledge Reuse inside Native Development Intake;
- propose a new milestone candidate as an explicit Platform Core context-resolution artifact;
- pass the full workspace-derived project context into intake and context assembly.

Fail-closed behavior remains architecturally justified only when deterministic context cannot be derived and no clarification has been requested. It is not justified for plain deterministic implementation requests that Platform Core can already classify, and the current implementation no longer fails for the audited example.

## 13. Minimal Correction Recommendation

No implementation change was made in this audit.

If Generation 14 continues project-context refinement, the smallest correction is:

```text
Extend Platform Core Native Development Intake to accept a Platform Core project context resolution artifact produced from existing Project Workspace, Project Guidance, Goal Mapping, Contextual Task Mapping, Knowledge Reuse, and Replay history.
```

The correction should:

- remain inside Platform Core;
- reuse `resolve_development_intent(...)`;
- reuse `goal_mapping_from_workspace(...)`;
- reuse `project_knowledge_context_from_workspace(...)`;
- avoid adding another intent classifier;
- avoid adding interface-specific logic;
- preserve `aicli` and future UHIs as thin adapters;
- preserve Governance, Replay, Provider Platform, and Worker Platform boundaries.

Suggested minimal lifecycle:

```text
human prompt
-> Development Intent Resolution
-> Project Context Resolution Artifact
-> Native Development Intake
-> Development Context Assembly
```

## 14. Architectural Assessment

Ownership remains certified:

| Component | Finding |
| --- | --- |
| `aicli` | Thin interface; does not resolve project context. |
| Platform Core Project Services | Own workspace, guidance, goal mapping, contextual task mapping, knowledge reuse, and intent resolution. |
| Native Development Intake | Owns current prompt-level intake and generic milestone fallback. |
| Governance | Not bypassed. |
| Provider Platform | Preserved; failure was provider availability. |
| Worker Platform | Not reached in restricted runtime because provider proposal failed. |
| Replay | Preserved all intake, context, and PPP evidence. |

No responsibility migration was detected.

No architectural redesign is recommended.

## 15. Validation Evidence

Direct probe:

```text
resolve_development_intent("Implement a governance documentation validator.")
summary_admissible: True
runtime_binding_admissible: True
native_development_prompt_detected: True

run_native_development_task_intake(...)
intake_status: NATIVE_DEVELOPMENT_TASK_INTAKE_ACCEPTED
requested_milestone_id: AIGOL_GENERIC_DEVELOPMENT_TASK_V1
failure_reason: None
```

Runtime probe:

```text
./aicli --session-id G14-23-CONTEXT-AUDIT --runtime-root /tmp/aigol_g14_23_context_audit --workspace /home/pisarna/work/sapianta --created-at 2026-07-04T00:00:00Z
```

Result:

```text
Native Development Intake: accepted
Development Context Assembly: CONTEXT_ASSEMBLED
PPP continuation: reached
Provider proposal production: FAILED_CLOSED
Failure reason: OpenAI provider unavailable
Failure classification: PROVIDER_AVAILABILITY
```

Regression validation:

```text
python -m pytest tests/test_g14_19_development_intent_resolution_unification_v1.py tests/test_g14_08a_platform_core_project_services_extraction_v1.py tests/test_g14_22_reference_unified_human_interface_v1.py -q
```

Result:

```text
10 passed
```

Whitespace validation:

```text
git diff --check
```

Result:

```text
clean
```

## 16. Final Determination

Project context resolution is partially supported.

The audited natural-language prompt no longer requires a human-supplied milestone identifier in the current implementation. Platform Core can resolve it to a deterministic generic native-development milestone and proceed to context assembly.

However, Native Development Intake does not yet consume the full deterministic Project Workspace / Knowledge Reuse context model. Rich project-context resolution therefore remains incomplete and should be addressed as a Platform Core enhancement, not an interface responsibility.

Final verdict: PROJECT_CONTEXT_RESOLUTION_PARTIALLY_SUPPORTED
