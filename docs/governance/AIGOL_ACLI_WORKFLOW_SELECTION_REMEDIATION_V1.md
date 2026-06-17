# AIGOL ACLI Workflow Selection Remediation V1

Status: implemented remediation evidence.

Purpose: define, implement, and certify the minimal remediation for the confirmed ACLI workflow-selection defect.

This artifact is remediation-scoped.

It does not redesign ACLI.

It does not redesign HIRR.

It does not introduce new architecture.

It does not authorize worker execution from intake.

It does not bypass human approval.

It preserves clarification-first behavior.

It preserves fail-closed behavior.

## Governing Inputs

Failure analysis:

```text
docs/governance/AIGOL_ACLI_WORKFLOW_SELECTION_FAILURE_ANALYSIS_V1.md
```

Failed first real user session evidence package:

```text
runtime/acli_first_real_user_session/e2e_evidence/replay/certification/000_evidence_package.json
```

Failed first real user session replay package:

```text
runtime/acli_first_real_user_session/e2e_evidence/replay/certification/001_replay_package.json
```

Failed first real user session certification report:

```text
runtime/acli_first_real_user_session/e2e_evidence/replay/certification/002_certification_report.json
```

Confirmed defect:

```text
ACLI selected CREATE_DOMAIN_COMPLIANCE_CLARIFICATION instead of BOUNDED_FILE_WRITE_WORKER_USER_SESSION.
```

## Remediation Goal

Minimal goal:

```text
Expose the bounded FILE_WRITE worker workflow as a valid post-clarification target.
```

The target must be selectable through normal human language:

```text
Can you make a small proof note that shows this system really did something safely?
Yes.
```

Expected selection after remediation:

```text
BOUNDED_FILE_WRITE_WORKER_USER_SESSION
```

Expected safety state at selection time:

```text
provider_invoked = false
worker_invoked = false
authorization_created = false
execution_requested = false
approval_bypassed = false
```

## Implementation Scope

Changed runtime files:

```text
aigol/runtime/human_intent_clarification_intake_runtime.py
aigol/runtime/human_intent_clarification_continuity_runtime.py
aigol/runtime/conversational_cli_runtime.py
```

Changed test file:

```text
tests/test_conversational_cli_runtime_v1.py
```

No worker contracts were changed.

No ERR contracts were changed.

No authorization runtime was changed.

No replay runtime was changed.

No provider runtime was changed.

## Runtime Remediation

### Intake

Added a bounded proof-file intent family:

```text
BOUNDED_FILE_WRITE_PROOF_INTENT
```

Added a bounded workflow target:

```text
BOUNDED_FILE_WRITE_WORKER_USER_SESSION
```

The intake classifier now recognizes proof-note evidence prompts such as:

```text
proof note
evidence note
evidence file
proof file
write a small proof
create a small proof
make a small proof
did something safely
system really did something safely
```

The classification remains clarification-first.

Expected Turn 1 state:

```text
workflow_id = HUMAN_INTENT_CLARIFICATION_INTAKE
routing_status = CLARIFICATION_REQUIRED
intent_family = BOUNDED_FILE_WRITE_PROOF_INTENT
expected_workflow_targets = BOUNDED_FILE_WRITE_WORKER_USER_SESSION
worker_invoked = false
execution_requested = false
authorization_created = false
```

### Continuity

Added `BOUNDED_FILE_WRITE_WORKER_USER_SESSION` to supported post-clarification targets.

Natural confirmations may refine to the bounded file-write workflow only when the prior clarification context already established that target.

Recognized confirmation signals include:

```text
yes
approved
approve
go ahead
confirm
confirmed
that is correct
```

The confirmation rule does not grant execution authority.

Expected Turn 2 state:

```text
workflow_id = BOUNDED_FILE_WRITE_WORKER_USER_SESSION
routing_status = WORKFLOW_SELECTED
worker_invoked = false
execution_requested = false
authorization_created = false
approval_bypassed = false
```

### Conversational Registry

Registered:

```text
BOUNDED_FILE_WRITE_WORKER_USER_SESSION
```

as a deterministic conversational workflow target.

The registry entry is metadata for routing and replay visibility.

It does not execute the worker.

## Focused Tests

Added focused coverage proving:

- clarification still occurs first;
- continuity preserves prior context;
- `BOUNDED_FILE_WRITE_WORKER_USER_SESSION` can be selected after clarification;
- unsupported targets still fail closed;
- selection does not invoke a provider;
- selection does not invoke a worker;
- selection does not create authorization;
- selection does not request execution.

Focused test command:

```bash
python -m pytest tests/test_conversational_cli_runtime_v1.py tests/test_acli_human_prompt_regression_suite_runtime_v1.py
```

Focused test result:

```text
115 passed
```

## Rerun Evidence

Remediation rerun id:

```text
ACLI-WORKFLOW-SELECTION-REMEDIATION-000001
```

Rerun root:

```text
runtime/acli_workflow_selection_remediation_v1
```

Rerun session root:

```text
runtime/acli_workflow_selection_remediation_v1/session_runtime/ACLI-WORKFLOW-SELECTION-REMEDIATION-000001
```

Rerun prompt sequence:

```text
Can you make a small proof note that shows this system really did something safely?
Yes.
Approved.
exit
```

Turn 1 result:

```text
workflow = HUMAN_INTENT_CLARIFICATION_INTAKE
intent_family = BOUNDED_FILE_WRITE_PROOF_INTENT
expected_workflow_targets = BOUNDED_FILE_WRITE_WORKER_USER_SESSION
state = WAITING_FOR_OPERATOR
stage = CLARIFICATION
worker_invoked = false
execution_requested = false
authorization_created = false
```

Turn 2 result:

```text
workflow = BOUNDED_FILE_WRITE_WORKER_USER_SESSION
state = CONTINUATION_AVAILABLE
stage = APPROVAL
worker_invoked = false
execution_requested = false
authorization_created = false
```

Turn 3 result:

```text
workflow = HUMAN_INTENT_CLARIFICATION_INTAKE
state = WAITING_FOR_OPERATOR
stage = CLARIFICATION
```

Turn 3 shows that full approval-to-worker continuation remains a separate implementation concern.

It does not invalidate the workflow-selection remediation because this remediation is scoped to post-clarification target selection.

## Remediation Evidence Package

Initial package attempt:

```text
runtime/acli_workflow_selection_remediation_v1/replay/certification/000_remediation_evidence_package.json
```

Initial report attempt:

```text
runtime/acli_workflow_selection_remediation_v1/replay/certification/002_remediation_certification_report.json
```

The initial package attempt incorrectly required the confirmation signal list to equal only `["yes"]`.

Actual replay recorded:

```text
["yes", "yes."]
```

This packaging mistake was preserved append-only and superseded.

Corrected evidence package:

```text
runtime/acli_workflow_selection_remediation_v1/replay/certification/003_remediation_evidence_package_corrected.json
```

Corrected replay package:

```text
runtime/acli_workflow_selection_remediation_v1/replay/certification/004_remediation_replay_package_corrected.json
```

Corrected certification report:

```text
runtime/acli_workflow_selection_remediation_v1/replay/certification/005_remediation_certification_report_corrected.json
```

Corrected certification status:

```text
WORKFLOW_SELECTION_REMEDIATED
```

## Certification Checks

Corrected evidence checks:

```text
clarification_first_preserved = true
bounded_file_write_target_exposed = true
continuity_context_preserved = true
natural_confirmation_refined_target = true
file_write_workflow_selected_after_clarification = true
approval_not_bypassed = true
authorization_not_created_by_selection = true
worker_not_invoked_by_selection = true
execution_not_requested_by_selection = true
clarification_resolution_recorded = true
focused_tests_passed = true
```

Safety preservation:

```text
provider_invoked = false
worker_invoked = false
authorization_created = false
execution_requested = false
approval_bypassed = false
```

## Residual Boundary

This remediation fixes workflow selection only.

It does not certify:

- approval-to-worker continuation for this new workflow;
- automatic FILE_WRITE execution from ACLI;
- Product 1 UX;
- new worker contracts;
- new authorization semantics.

The next bounded validation may address approval-to-worker continuation for `BOUNDED_FILE_WRITE_WORKER_USER_SESSION`.

## Final Verdict

```text
WORKFLOW_SELECTION_REMEDIATED
```

The confirmed workflow-selection defect is remediated.

ACLI now preserves clarification-first behavior and can select the bounded FILE_WRITE worker workflow after natural confirmation, while preserving approval, authorization, worker, and execution boundaries.
