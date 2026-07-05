# G14_35_DETERMINISTIC_ROUTING_PRECEDENCE_RESTORATION_V1

Status: Certified

Final verdict:

```text
DETERMINISTIC_ROUTING_PRECEDENCE_RESTORED
```

## Executive Summary

G14.35 restored deterministic routing precedence without redesigning Platform Core, Development Intent Resolution, Runtime Entry, Governance, Provider Platform, Worker Platform, or Replay.

The implementation preserves Native Development Context Integration as the canonical generic development fallback while preventing it from preempting stronger deterministic evidence for Product 1, OCS Cognition, Lifecycle Governance, Domain Proposal, and Session Continuity routes.

Repository validation improved from the G14.34 baseline of:

```text
5749 passed
4 skipped
18 failed
```

to:

```text
5770 passed
4 skipped
4 failed
```

The remaining four failures are not caused by deterministic routing precedence. They remain visible as separate clarification, freeform report, project guidance, and knowledge reuse gaps.

## Capability Discovery

The audit located deterministic routing ownership in:

- `aigol/runtime/conversational_cli_runtime.py`
- `aigol/cli/aigol_cli.py`

The canonical runtime entry, Project Services, Governance, Provider Platform, Worker Platform, and Replay were not modified.

The routing decision remained a single deterministic decision path. No additional classifier, adapter-specific route, interface-specific override, or runtime-entry change was introduced.

## Root Cause

Native Development Context Integration was evaluated before several more specific deterministic workflows.

This allowed generic implementation language to win before deterministic evidence could select:

- Product 1 workflows
- OCS Cognition / Advisory workflows
- Lifecycle activation workflows
- Domain Proposal workflows
- Session Continuity workflows

The root cause was routing priority, not Platform Core architecture.

## Implementation

The correction made Native Development Context Integration a fallback rather than a preemptive route.

Implemented changes:

- Product 1 and Lifecycle routes now execute before native development fallback routing.
- OCS Cognition and plain OCS intake now execute before generic task-completion native development fallback routing.
- Routing visibility now presents OCS Cognition before Native Development Context Integration when both are candidates.
- Explicit native-development context prompts remain supported by a narrow deterministic guard after Product 1 and Lifecycle routes.

No Platform Core service ownership was moved.

## Regression Coverage

Added:

```text
tests/test_g14_35_deterministic_routing_precedence_restoration_v1.py
```

Coverage verifies:

- Product 1 requests route to Product 1 workflows.
- OCS product cognition requests route to OCS Cognition.
- Domain lifecycle requests route to Domain Lifecycle Governance.
- Capability lifecycle requests route to Capability Lifecycle Governance.
- Domain proposal requests route to Domain Proposal clarification.
- Governed development requests route to Governed Development Workflow.
- Generic implementation requests route to Native Development Context Integration.

## Runtime Evidence

Focused routing validation:

```text
39 passed
```

Native development context validation:

```text
34 passed
```

Previously failing routing cluster validation:

```text
20 passed
3 failed
```

The remaining three failures in that slice are unrelated to routing precedence:

- freeform acceptance report count mismatch
- missing deployment goal target presentation
- missing knowledge reuse extension classification presentation

Full repository validation:

```text
4 failed
5770 passed
4 skipped
```

Real interface validation:

```text
./aicli
prompt: Implement governance validation utility.
runtime_status: REFERENCE_UHI_RUNTIME_PARTIALLY_BOUND
project services: delegated to Platform Core
interface authority: false
```

```text
python -m aigol.cli.aigol_cli next
prompt: Implement governance validation utility.
workflow: NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
runtime_entered: true
failure reason: OpenAI provider unavailable
```

```text
python -m aigol.cli.aigol_cli next
prompt: Create Product 1 AI Decision Validator capability model.
workflow: AI_DECISION_VALIDATOR_CAPABILITY_MODEL
status: COMPLETED
provider_invocation_reached: false
worker_execution_reached: false
```

The Product 1 runtime probe confirms that the specialized deterministic route wins over the generic native development fallback in the real `aigol next` entry path.

Remaining full-suite failures:

- `test_interactive_human_intent_clarification_response_selects_expected_workflow`
- `test_freeform_acceptance_report_matches_current_acli_behavior`
- `test_high_level_operational_goals_map_without_manual_workflow_prompts`
- `test_contextual_mapping_reuses_workspace_for_existing_modified_extended_and_new_goals`

These failures are retained as visible residual gaps and were not compensated for inside routing precedence.

## Ownership Verification

| Component | Ownership Status |
| --- | --- |
| Human Interfaces | Thin adapters only; no interface-specific routing added. |
| Canonical Runtime Entry | Unchanged. |
| Development Intent Resolution | Unchanged. |
| Platform Core | Remains owner of deterministic routing and orchestration. |
| Governance | Unchanged. |
| Provider Platform | Unchanged. |
| Worker Platform | Unchanged. |
| Replay | Unchanged. |

## Architectural Assessment

The correction restores the certified routing principle:

```text
most specific deterministic interpretation wins
```

Native Development Context Integration remains available, but only after stronger deterministic routes have had the opportunity to match.

No new authority layer was introduced.

No routing responsibility moved into a Human Interface.

No governance, provider, worker, or replay responsibility changed.

## Certification Summary

G14.35 successfully restores deterministic routing precedence and measurably reduces repository regressions from 18 failures to 4 failures.

The remaining failures are not part of the routing-precedence root cause and should be handled as separate governed implementation milestones.

Certified verdict:

```text
DETERMINISTIC_ROUTING_PRECEDENCE_RESTORED
```
