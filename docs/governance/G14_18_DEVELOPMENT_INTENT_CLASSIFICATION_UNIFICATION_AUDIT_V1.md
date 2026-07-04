# G14-18 Development Intent Classification Unification Audit V1

Status: development intent classification fragmentation detected.

Final verdict: DEVELOPMENT_INTENT_CLASSIFICATION_FRAGMENTATION_DETECTED

## 1. Executive Summary

G14-18 audited the deterministic native development intent pipeline from human prompt through governed summary and runtime binding.

The audit found that multiple deterministic development-intent decisions coexist:

- Platform Core Project Services decide whether `/send` should produce a governed implementation summary.
- ACLI Next approval handling submits the summary `refined_message`.
- Runtime binding independently decides whether the submitted message is native development by calling `is_native_development_prompt(...)`.
- Conversational runtime routing also contains compatibility and CSA comparison paths for native development workflow selection.

These decisions are not currently one unified classifier. They have different consumers and slightly different term sets.

The discrepancy is reproducible in the repository runtime with:

```text
Implement governed policy.
```

Observed behavior:

```text
/send -> Governed implementation summary presented
/approve -> AIGOL_NEXT_RUNTIME_BINDING_NOT_REQUIRED
```

Root cause:

```text
Classifier fragmentation between guided summary admission and runtime binding admission.
```

The smallest correction should unify existing deterministic decisions by making governed summary admission depend on the same native-development eligibility used by runtime binding, or by moving both decisions behind one Platform Core development intent service. The audit does not recommend adding another classifier.

Final verdict: DEVELOPMENT_INTENT_CLASSIFICATION_FRAGMENTATION_DETECTED

## 2. Complete Intent Pipeline Trace

### 2.1 Human Prompt

Input source:

```text
aigol next persistent REPL
```

Implementation:

```text
aigol/acli_next/conversational.py
run_acli_next_persistent_conversational_session(...)
```

The message composer buffers lines until `/send`.

Consumer:

```text
ACLI Next conversational UX loop
```

### 2.2 Project Workspace

Implementation:

```text
aigol/runtime/platform_core_project_services.py
build_persistent_workspace_state_artifact(...)
project_guidance_from_workspace_state(...)
```

Owner:

```text
Platform Core Project Services
```

Consumer:

```text
ACLI Next renders restored workspace and guidance.
```

### 2.3 Project Guidance

Implementation:

```text
aigol/runtime/platform_core_project_services.py
project_guidance_model(...)
```

Output:

```text
guidance_source: deterministic_workspace_state
guidance_authority: PLATFORM_CORE
```

Consumer:

```text
ACLI Next presentation only.
```

### 2.4 Goal Mapping

Implementation:

```text
aigol/runtime/platform_core_project_services.py
goal_oriented_request_detected(...)
goal_mapping_from_workspace(...)
```

Decision:

```text
goal_oriented_request_detected(message)
```

Current deterministic trigger:

```text
i want ...
i want aigol ...
let's ...
lets ...
continue ...
```

Consumer:

```text
_guided_development_summary(...)
```

When goal mapping is present, the summary `refined_message` becomes:

```text
goal_mapping["governed_request"]
```

### 2.5 Contextual Task Mapping

Implementation:

```text
aigol/runtime/platform_core_project_services.py
project_knowledge_context_from_workspace(...)
```

Output:

```text
contextual_task_mapping
workspace_inspected: True
contextual_task_mapping_authority: PLATFORM_CORE
```

Consumer:

```text
ACLI Next summary rendering.
```

### 2.6 Governed Summary

Implementation:

```text
aigol/acli_next/conversational.py
_guided_development_summary(...)
```

Inputs:

- `original_message`;
- optional `clarification_response`;
- optional `goal_mapping`.

Output:

```text
pending_summary["refined_message"]
runtime_after_approval: CERTIFIED_PLATFORM_CORE_RUNTIME
requires_human_confirmation: True
```

Decision producer:

```text
guided_development_request_detected(...)
goal_oriented_request_detected(...)
guided_development_clarification_required(...)
```

### 2.7 Approval

Implementation:

```text
aigol/acli_next/conversational.py
/approve branch
```

Approval action:

```text
submit_turn(
    session_id=conversation_id,
    prompts=[pending_summary["refined_message"]],
    created_at=created_at,
    replay_dir=replay_dir,
    workspace=workspace,
)
```

In the CLI path, `submit_turn` is:

```text
aigol/cli/aigol_cli.py::_run_acli_next_runtime_bound_session
```

### 2.8 Runtime Binding

Implementation:

```text
aigol/cli/aigol_cli.py
_run_acli_next_runtime_bound_session(...)
```

Decision:

```text
if not any(is_native_development_prompt(prompt) for prompt in prompts):
    runtime_binding_status = AIGOL_NEXT_RUNTIME_BINDING_NOT_REQUIRED
    runtime_entered = False
```

Classifier owner:

```text
aigol/runtime/native_development_task_intake_runtime.py
is_native_development_prompt(...)
is_plain_native_development_prompt(...)
```

### 2.9 Platform Core Runtime

When runtime binding accepts the prompt, it invokes:

```text
run_interactive_conversation(...)
```

with:

```text
operator_context: AIGOL_NEXT_RUNTIME_BINDING
auto_continue: True
```

When runtime binding rejects the prompt, Platform Core native continuation is not entered.

## 3. Refined Message Investigation

### 3.1 G14-15 Prompt

Raw prompt:

```text
Implement a native validation helper for replay evidence summaries.
```

Classifier results:

```text
goal_oriented_request_detected(raw_prompt): False
guided_development_request_detected(raw_prompt): True
is_native_development_prompt(raw_prompt): True
```

Pending summary:

```text
original_message: Implement a native validation helper for replay evidence summaries.
clarification_response: None
goal_mapping: None
refined_message: Implement a native validation helper for replay evidence summaries.
summary_status: IMPLEMENTATION_SUMMARY_PRESENTED
runtime_after_approval: CERTIFIED_PLATFORM_CORE_RUNTIME
```

String evaluated by `is_native_development_prompt(...)` after `/approve`:

```text
Implement a native validation helper for replay evidence summaries.
```

Result:

```text
is_native_development_prompt(refined_message): True
```

### 3.2 Reproducible Divergent Prompt

Raw prompt:

```text
Implement governed policy.
```

Classifier results:

```text
guided_development_request_detected(raw_prompt): True
guided_development_clarification_required(raw_prompt): False
is_native_development_prompt(raw_prompt): False
```

Pending summary:

```text
original_message: Implement governed policy.
clarification_response: None
goal_mapping: None
refined_message: Implement governed policy.
summary_status: IMPLEMENTATION_SUMMARY_PRESENTED
runtime_after_approval: CERTIFIED_PLATFORM_CORE_RUNTIME
```

String evaluated by `is_native_development_prompt(...)` after `/approve`:

```text
Implement governed policy.
```

Result:

```text
is_native_development_prompt(refined_message): False
```

This reproduces the observed class of failure:

```text
runtime_binding_status: AIGOL_NEXT_RUNTIME_BINDING_NOT_REQUIRED
runtime_entered: False
```

## 4. Classifier Consistency

| Classifier | Implementation | Purpose | Example Result |
| --- | --- | --- | --- |
| `goal_oriented_request_detected(raw_prompt)` | `platform_core_project_services.py` | Detect high-level project goals for deterministic workspace mapping. | `I want AiGOL Next to support GitHub Actions.` -> true |
| `guided_development_request_detected(raw_prompt)` | `platform_core_project_services.py` | Detect whether `/send` should present a governed implementation summary. | `Implement governed policy.` -> true |
| `guided_development_clarification_required(raw_prompt)` | `platform_core_project_services.py` | Decide whether summary should wait for clarification. | `Implement governed policy.` -> false because `governed` is treated as specificity. |
| `is_native_development_prompt(raw_prompt)` | `native_development_task_intake_runtime.py` | Decide whether runtime binding may enter native development. | `Implement governed policy.` -> false |
| Conversational workflow classifier | `conversational_cli_runtime.py` | Select workflow after runtime entry. | Uses compatibility routing, CSA comparison, and fallback paths. |
| Resource-catalog native classifier | `conversation_native_development_intent_routing.py` | Route known domain/resource native development intents. | Narrow catalog; not the same as generic task-intake detection. |

These classifiers are related, but they are not currently one canonical implementation.

They do not represent exactly the same responsibility:

- goal-oriented detection maps goals to governed requests;
- guided detection creates summaries;
- runtime binding gates native execution;
- conversational routing chooses a workflow after binding;
- resource-catalog routing handles structured native resource intents.

However, the summary admission and runtime binding decisions are sequential gates for the same user expectation:

```text
If AiGOL Next presents "runtime_after_approval: CERTIFIED_PLATFORM_CORE_RUNTIME", /approve should not immediately decide that runtime binding is not required for the same refined message.
```

That specific pair is inconsistent.

## 5. Historical Implementation Inventory

| Capability | Implementation | Current Consumer | Classification |
| --- | --- | --- | --- |
| Project goal detection | `platform_core_project_services.py::goal_oriented_request_detected` | ACLI Next `/send` | Canonical for workspace goal mapping |
| Goal mapping | `platform_core_project_services.py::goal_mapping_from_workspace` | ACLI Next summary | Canonical Platform Core Project Service |
| Contextual task mapping | `platform_core_project_services.py::project_knowledge_context_from_workspace` | ACLI Next summary | Canonical Platform Core Project Service |
| Guided development detection | `platform_core_project_services.py::guided_development_request_detected` | ACLI Next `/send` | Transitional summary admission gate |
| Guided clarification detection | `platform_core_project_services.py::guided_development_clarification_required` | ACLI Next `/send` | Transitional summary admission gate |
| Runtime native task intake gate | `native_development_task_intake_runtime.py::is_native_development_prompt` | Runtime binding, native task intake | Canonical runtime binding gate |
| Plain native development detector | `native_development_task_intake_runtime.py::is_plain_native_development_prompt` | Runtime binding, conversational routing fallback | Canonical compatibility detector for low-risk plain development |
| Conversational workflow routing | `conversational_cli_runtime.py` local compatibility routing | Runtime conversation | Canonical conversational routing path with compatibility fallback |
| CSA native-development comparison | `conversational_cli_runtime.py::_classify_native_development_from_canonical_semantic_artifact` | Runtime conversation | Transitional CSA migration path |
| Resource-catalog native development routing | `conversation_native_development_intent_routing.py` | Runtime conversation for specific catalog intents | Compatibility/catalog-specific, not broad native gate |

No dead code classification is made by this audit. The implementations are reachable.

The duplicated responsibility is narrower:

```text
summary admission and runtime binding both answer "is this development request ready for native runtime continuation?" but use different predicates.
```

## 6. Canonical Ownership Audit

There is not currently exactly one canonical owner for development-intent resolution across the complete `/send` -> `/approve` path.

Current ownership split:

| Decision | Owner | Evidence |
| --- | --- | --- |
| Workspace and project mapping | Platform Core Project Services | Artifacts state `goal_mapping_authority: PLATFORM_CORE`. |
| Summary presentation | ACLI Next rendering over Platform Core service result | `acli_next_executes: False`; presentation only. |
| Summary admission | Platform Core Project Services | `guided_development_request_detected(...)`. |
| Native runtime binding | Runtime binding / native task intake | `is_native_development_prompt(...)`. |
| Workflow selection after binding | Conversational runtime / CSA compatibility path | `conversational_cli_runtime.py`. |

Ownership boundary is not architecturally violated, because AiGOL Next remains presentation/delegation only.

Operationally, responsibility is fragmented because Platform Core Project Services and Native Development Task Intake maintain overlapping term-based readiness decisions.

## 7. Runtime Divergence

First divergence point:

```text
aigol/acli_next/conversational.py
/send branch
```

For `Implement governed policy.`:

```text
guided_development_request_detected(message) == True
guided_development_clarification_required(message) == False
```

Therefore `/send` creates:

```text
pending_summary["refined_message"] = "Implement governed policy."
```

Second decision point:

```text
aigol/cli/aigol_cli.py::_run_acli_next_runtime_bound_session
```

For the same refined message:

```text
is_native_development_prompt("Implement governed policy.") == False
```

Therefore `/approve` returns:

```text
runtime_binding_status: AIGOL_NEXT_RUNTIME_BINDING_NOT_REQUIRED
runtime_entered: False
```

The divergence is not caused by provider availability, Governance, Replay, Worker Platform, PGSP, UBTR, CSA, or Platform Core execution.

It occurs before runtime entry.

## 8. Runtime Evidence

Reproduction command:

```text
python -m aigol.cli.aigol_cli next \
  --session-id G14-18-DIVERGENCE-PROBE \
  --runtime-root /tmp/aigol_g14_18_divergence_probe \
  --workspace /home/pisarna/work/sapianta \
  --created-at 2026-07-04T00:00:00Z
```

Interactive transcript:

```text
AiGOL> Implement governed policy.
AiGOL> /send
Governed implementation summary
original_request: Implement governed policy.
runtime_after_approval: CERTIFIED_PLATFORM_CORE_RUNTIME
Type /approve to continue into the certified runtime, or /cancel to discard.

AiGOL> /approve
runtime_binding_status: AIGOL_NEXT_RUNTIME_BINDING_NOT_REQUIRED
runtime_entered: False
governance_authorization_reached: None
provider_invocation_reached: None
worker_execution_reached: None
replay_certification_reached: None
```

Replay evidence:

```text
/tmp/aigol_g14_18_divergence_probe/G14-18-DIVERGENCE-PROBE/RUN-000001/000_acli_next_conversational_session_presented.json
latest_prompt: Implement governed policy.
current_stage: Classify Capability Coverage
next_expected_operation: Existing Capability Audit
```

Session completion evidence:

```text
/tmp/aigol_g14_18_divergence_probe/G14-18-DIVERGENCE-PROBE/001_acli_next_persistent_session_completed.json
execution_summary_count: 1
approval_count: 1
runtime_bound_count: 0
```

## 9. Architectural Health Assessment

Finding:

```text
Classifier inconsistency and responsibility fragmentation are present in the development intent path.
```

Supported causes:

- summary admission uses `guided_development_request_detected(...)` and `guided_development_clarification_required(...)`;
- runtime binding uses `is_native_development_prompt(...)`;
- the term `governed` is sufficient to avoid clarification in the summary gate;
- the same term is not sufficient to satisfy native-development runtime binding;
- `/approve` evaluates `pending_summary["refined_message"]`, not a separately normalized canonical development intent artifact.

Rejected causes:

| Cause | Assessment |
| --- | --- |
| Provider availability | Rejected for this failure class; runtime is never entered. |
| Governance defect | Rejected; Governance is not reached. |
| Replay defect | Rejected; Replay records the presentation and session completion. |
| Worker Platform defect | Rejected; Worker Platform is not reached. |
| Production CLI entrypoint | Not required to reproduce; repository module path reproduces the divergence. |

## 10. Recommended Minimal Correction

Because this milestone is an audit, no code change is made here.

The recommended minimal correction is:

```text
Unify summary admission and runtime binding around one deterministic Platform Core development intent decision.
```

Acceptable minimal implementation approaches:

1. Make governed summary creation require the same native runtime eligibility predicate used by runtime binding before presenting `runtime_after_approval: CERTIFIED_PLATFORM_CORE_RUNTIME`.
2. Or expose a single Platform Core development intent service that returns both:

```text
summary_admissible
runtime_binding_admissible
clarification_required
refined_message
```

and make both `/send` and `/approve` consume that same artifact.

Do not add a third classifier.

Do not move interpretation authority into ACLI Next.

Do not bypass Governance, Replay, Worker Platform, PGSP, UBTR, or CSA.

## 11. Certification Summary

The deterministic development intent pipeline is not fully unified.

The observed `AIGOL_NEXT_RUNTIME_BINDING_NOT_REQUIRED` behavior can be explained with implementation evidence:

```text
/send and /approve use different deterministic development-intent gates.
```

The architecture boundaries remain intact, but operational classifier fragmentation remains.

Final verdict: DEVELOPMENT_INTENT_CLASSIFICATION_FRAGMENTATION_DETECTED

## 12. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: DEVELOPMENT_INTENT_CLASSIFICATION_FRAGMENTATION_DETECTED
