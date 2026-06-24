# REAL_WORLD_HUMAN_FRIENDLY_ACLI_VALIDATION_V1

Status: Completed With Findings

Purpose: Validate ACLI usability from a normal operator perspective after `HUMAN_FRIENDLY_ACLI_EXPLANATION_IMPLEMENTATION_V1`.

Target verdict requested:

```text
HUMAN_FRIENDLY_ACLI_VALIDATED
```

Observed verdict:

```text
HUMAN_FRIENDLY_ACLI_VALIDATION_BLOCKED_FOR_REQUESTED_SCENARIO
```

## 1. Validation Scope

Requested test scenario:

```text
Create governance artifact ACLI_USAGE_GUIDELINES_V1 documenting recommended operator practices for using ACLI as the primary development interface.
```

Validation questions:

1. Can a normal operator understand what ACLI understood, what ACLI will do, what ACLI will not do, why approval is required, and what to type next?
2. Does the explanation remain accurate?
3. Does explanation replay reconstruct correctly?
4. Does explanation preserve non-authoritative behavior?

## 2. Execution Environment

Requested scenario runtime:

```text
session_id: HUMAN-FRIENDLY-VALIDATION-001
runtime_root: /tmp/sapianta_hf_validation_runtime
workspace: /tmp/sapianta_hf_validation_repo
created_at: 2026-06-24T00:00:00Z
```

The workspace was a disposable git repository.

## 3. Operator Transcript: Requested Scenario

Operator input:

```text
Create governance artifact ACLI_USAGE_GUIDELINES_V1 documenting recommended operator practices for using ACLI as the primary development interface.
APPROVE
exit
```

Observed ACLI output excerpt:

```text
ROUTING DECISION
workflow: GOVERNANCE_ARTIFACT_CREATION
confidence: HIGH
matched:
- create
- governance
- artifact
reason:
Select the certified governance artifact creation workflow without mutation or approval bypass.
```

Observed failure:

```text
FAILED_CLOSED: unsupported conversational workflow selection: GOVERNANCE_ARTIFACT_CREATION
Workflow Name: UNAVAILABLE
Workflow State: FAILED_CLOSED
Current Lifecycle Stage: FAILED_CLOSED
Next Expected Action: Informational only: inspect fail-closed reason: unsupported conversational workflow selection: GOVERNANCE_ARTIFACT_CREATION
```

## 4. Requested Scenario Findings

### 4.1 What ACLI Understood

Partially understandable.

ACLI clearly selected:

```text
GOVERNANCE_ARTIFACT_CREATION
```

The routing reason was technically accurate. However, no human-friendly explanation was rendered for the requested scenario.

### 4.2 What ACLI Will Do

Not understandable enough for a normal operator.

The output says the workflow was selected, then immediately fails closed as unsupported. It does not explain whether ACLI can proceed through proposal, approval, mutation, validation, or replay for this routed workflow.

### 4.3 What ACLI Will Not Do

Partially visible only through failure.

No mutation occurred. No worker executed. However, the operator learns this indirectly from fail-closed behavior, not from a human-friendly explanation.

### 4.4 Why Approval Is Required

Not explained.

The requested scenario did not reach an approval-facing proposal stage.

### 4.5 What To Type Next

Not explained.

The operator typed `APPROVE`, but the workflow had already failed closed. The UI did not provide a clear recovery path beyond inspecting the fail-closed reason.

## 5. Replay Evidence: Requested Scenario

Replay artifacts were created for routing, progress, prompt capture, routing visibility, source routing, and universal intake.

Observed replay files include:

```text
/tmp/sapianta_hf_validation_runtime/HUMAN-FRIENDLY-VALIDATION-001/TURN-000001/conversational_cli_routing/000_conversational_routing_decision_recorded.json
/tmp/sapianta_hf_validation_runtime/HUMAN-FRIENDLY-VALIDATION-001/TURN-000001/conversational_cli_routing/001_conversational_workflow_selection_recorded.json
/tmp/sapianta_hf_validation_runtime/HUMAN-FRIENDLY-VALIDATION-001/TURN-000001/routing_visibility/000_conversational_routing_visibility_recorded.json
/tmp/sapianta_hf_validation_runtime/HUMAN-FRIENDLY-VALIDATION-001/TURN-000001/universal_intake/000_universal_intake_recorded.json
```

No human-friendly explanation replay artifact was created for the requested scenario.

Missing expected explanation replay:

```text
/tmp/sapianta_hf_validation_runtime/HUMAN-FRIENDLY-VALIDATION-001/TURN-000001/human_friendly_explanation/
```

Repository mutation status:

```text
No repository changes were produced in /tmp/sapianta_hf_validation_repo.
```

## 6. Control Validation: Governed Development Path

A control run was executed to verify the implemented explanation layer on the currently integrated governed development bridge.

Control prompt:

```text
Add replay validation
```

Control approval:

```text
APPROVE
```

Control runtime:

```text
session_id: HUMAN-FRIENDLY-CONTROL-002
runtime_root: /tmp/sapianta_hf_validation_control_runtime_2
workspace: /tmp/sapianta_hf_validation_control_repo_2
```

Observed explanation output:

```text
HUMAN-FRIENDLY EXPLANATION

WHAT I UNDERSTOOD

I understood that you want ACLI to handle this request: Add replay validation
Selected workflow: GOVERNED_DEVELOPMENT_WORKFLOW
Intake classification: INTAKE_NOT_APPLICABLE
Routing reason: Select the governed development orchestration workflow without mutation or approval bypass.
Proposal id: HUMAN-FRIENDLY-CONTROL-002:TURN-000001:ACLI-GOVERNED-DEVELOPMENT-BRIDGE:PROPOSAL
Target paths:
- docs/governance/ACLI_GOVERNED_DEVELOPMENT_E5BAAA6109EE2B3D_V1.md
- aigol/runtime/acli_governed_development_e5baaa6109ee2b3d.py
```

Observed approval guidance:

```text
WHAT TO TYPE NEXT

Type APPROVE to continue.
Type REJECT to cancel.
Type REQUEST_MODIFICATION to stop execution and request changes.
```

Observed boundary explanation:

```text
WHAT WILL NOT HAPPEN

- no worker will execute before approval
- no repository mutation will occur before approval
- no provider will be invoked unless required by the selected workflow
- ACLI will not treat provider output as authority
```

Observed execution after approval:

```text
Governed Development Execution
bridge_status: EXECUTION_COMPLETED
workflow_id: GOVERNED_DEVELOPMENT_WORKFLOW
approval_decision: APPROVED
approval_bypassed: false
mutation_performed: true
worker_invoked: true
validation_executed: true
workflow_execution_status: GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED
worker_protections_preserved: true
validation_allowlists_preserved: true
replay_lineage_preserved: true
```

## 7. Explanation Replay Verification

Control explanation replay path:

```text
/tmp/sapianta_hf_validation_control_runtime_2/HUMAN-FRIENDLY-CONTROL-002/TURN-000001/human_friendly_explanation
```

Replay reconstruction result:

```text
workflow_id: GOVERNED_DEVELOPMENT_WORKFLOW
visibility_only: True
authority_granted: False
rendered_explanation_hash: sha256:869936da105ef7b147ba4b31ad3e31f2c9659c7b8035aa12e9c7a42f9c093928
```

Conclusion:

The explanation replay reconstructs correctly for the governed development path where the explanation layer is integrated.

## 8. Accuracy Assessment

### Requested Scenario

The explanation could not be assessed because it was not rendered.

The routing output was accurate:

```text
GOVERNANCE_ARTIFACT_CREATION
```

The operator experience was incomplete because the interactive runtime did not support the selected workflow after routing.

### Control Scenario

The explanation was accurate:

- it identified the selected workflow;
- it listed target paths;
- it stated approval was required;
- it stated no worker or mutation would occur before approval;
- it stated replay evidence would be recorded;
- approval execution matched the explanation.

## 9. Non-Authoritative Behavior Assessment

Requested scenario:

- no explanation artifact was produced;
- no repository mutation occurred;
- fail-closed behavior was preserved.

Control scenario:

- explanation artifact had `visibility_only: true`;
- `authority_granted: false`;
- `provider_authority: false`;
- `approval_authority: false`;
- `execution_authority: false`;
- `worker_authority: false`;
- no mutation occurred before approval;
- mutation occurred only after explicit `APPROVE`.

## 10. Usability Findings

### Finding 1: Requested Governance Artifact Prompt Is Not End-To-End Operator Ready

The prompt routes correctly to `GOVERNANCE_ARTIFACT_CREATION`, but the interactive ACLI loop fails closed with:

```text
unsupported conversational workflow selection: GOVERNANCE_ARTIFACT_CREATION
```

This is a material usability blocker for the requested scenario.

### Finding 2: Explanation Layer Is Currently Integrated With Governed Development, Not All Routed Workflows

The explanation layer works for `GOVERNED_DEVELOPMENT_WORKFLOW` proposal turns.

It does not yet cover the routed `GOVERNANCE_ARTIFACT_CREATION` path.

### Finding 3: Multiline Mode Can Confuse Scripted Validation

The interactive CLI runs in multiline mode. Scripted input must terminate each prompt with:

```text
.
```

Without the terminator, subsequent lines such as `APPROVE` and `exit` can be captured as part of the original prompt.

### Finding 4: Control Path Is Understandable

For the governed development bridge, a normal operator can understand:

- what ACLI understood;
- what will happen;
- what will not happen;
- why approval is required;
- what to type next;
- where replay evidence is stored.

## 11. Confusion Points

- `GOVERNANCE_ARTIFACT_CREATION` appears certified in routing but unsupported in the interactive execution branch.
- The fail-closed message is technically correct but does not explain how to recover.
- No human-friendly explanation is rendered for the routed governance artifact creation scenario.
- Scripted demos require multiline prompt terminators.
- After control execution, sending `exit` as a multiline prompt can be interpreted as normal input rather than an exit command.

## 12. Remaining UX Gaps

P0 gaps:

- Add human-friendly explanation coverage for `GOVERNANCE_ARTIFACT_CREATION` routing or route this operator phrase through the governed development bridge when end-to-end execution is expected.
- Add an interactive ACLI execution branch for `GOVERNANCE_ARTIFACT_CREATION` if that workflow is intended to be directly executable from ACLI.
- Render a human-friendly fail-closed explanation when a workflow is routed but unsupported.

P1 gaps:

- Improve scripted/non-interactive demo handling for multiline mode.
- Explain how to recover from unsupported workflow selection.
- Surface whether a selected workflow is route-only, proposal-capable, or execution-capable before asking for approval.

## 13. Improvement Recommendations

1. Extend the explanation layer to route-only and fail-closed turns.
2. Add a supported operator path for `GOVERNANCE_ARTIFACT_CREATION`, or explicitly constrain it to routing-only until execution is wired.
3. Add regression coverage for the requested prompt:

```text
Create governance artifact ACLI_USAGE_GUIDELINES_V1 documenting recommended operator practices for using ACLI as the primary development interface.
```

4. Add a demo-mode or single-line mode option for scripted validation.
5. Add operator guidance when `APPROVE` is received without a pending approval-capable proposal.

## 14. Validation Commands

Runtime validation:

```bash
python -m pytest tests/test_acli_human_friendly_explanation_runtime_v1.py tests/test_acli_governed_development_execution_bridge_v1.py -q
```

Observed result:

```text
5 passed
```

Diff validation:

```bash
git diff --check
```

Observed result:

```text
passed
```

## 15. Final Verdict

The human-friendly explanation layer is validated for the currently integrated governed development bridge.

The requested governance artifact scenario is not validated because ACLI routes to `GOVERNANCE_ARTIFACT_CREATION` and then fails closed before producing an approval-facing proposal or explanation.

Final verdict:

```text
HUMAN_FRIENDLY_ACLI_VALIDATION_BLOCKED_FOR_REQUESTED_SCENARIO
```
