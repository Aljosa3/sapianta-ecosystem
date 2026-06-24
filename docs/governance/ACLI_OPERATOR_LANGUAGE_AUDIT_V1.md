# ACLI_OPERATOR_LANGUAGE_AUDIT_V1

Status: Complete

Scope: Operator-facing ACLI language audit

Target verdict:

```text
ACLI_OPERATOR_LANGUAGE_AUDIT_COMPLETE
```

## 1. Purpose

This artifact audits operator-facing ACLI output language for the governed development approval and execution path.

The audit focuses only on language and presentation. It does not redesign governance, workflows, HIRR, approval, execution, validation, replay, or provider behavior.

The reviewed operator stages are:

- proposal generation;
- approval requests;
- approval decisions;
- `REQUEST_MODIFICATION`;
- rejection;
- execution;
- validation;
- replay review.

## 2. Audit Standard

Operator-facing output should answer four questions before showing diagnostics:

1. What did ACLI understand?
2. What will happen next?
3. What requires my decision?
4. Where can I inspect evidence?

Runtime fields may remain visible, but fields such as hashes, internal workflow constants, replay directory paths, validation flags, and invariant flags should be grouped under a diagnostic or evidence section.

The audit classifies each message as:

- `HUMAN_ORIENTED`: understandable by a normal non-technical operator.
- `MIXED`: partly understandable, but contains runtime-oriented fields.
- `RUNTIME_ORIENTED`: useful for diagnostics or audit review, but not suitable as primary operator language.

## 3. Current Operator Message Inventory

### 3.1 Human-Friendly Explanation

Current output source:

```text
aigol/runtime/acli_human_friendly_explanation_runtime.py
```

Current headings:

```text
HUMAN-FRIENDLY EXPLANATION
WHAT I UNDERSTOOD
WHAT WILL HAPPEN
WHAT WILL NOT HAPPEN
WHAT REQUIRES YOUR APPROVAL
WHAT TO TYPE NEXT
REPLAY VISIBILITY
```

Assessment: `HUMAN_ORIENTED`

This is the strongest current operator-facing surface. It explains approval, mutation boundaries, next commands, and replay visibility in plain language.

Remaining language issues:

- It still includes raw workflow identifiers such as `GOVERNED_DEVELOPMENT_WORKFLOW`.
- It may include raw intake classifications and routing reasons.
- It names replay paths directly without first explaining that they are evidence locations.

Recommended treatment:

- Keep this as the primary operator explanation.
- Translate workflow identifiers into plain language first.
- Move raw identifiers into diagnostics.

### 3.2 Routing Decision

Current output pattern:

```text
ROUTING DECISION
workflow: GOVERNED_DEVELOPMENT_WORKFLOW
confidence: HIGH
matched:
- governed-development-pending-approval
- APPROVE
reason:
Stateful governed development approval decision detected; continuing the pending proposal without rerouting.
```

Assessment: `MIXED`

Understandable parts:

- The selected workflow is visible.
- The reason can explain why approval did not reroute.

Confusing or runtime-oriented fields:

- `workflow`;
- `confidence`;
- `matched`;
- internal signal names such as `governed-development-pending-approval`;
- uppercase workflow constants.

Human-friendly replacement:

```text
ACLI recognized this as a continuation of the proposal you were already reviewing.

It will use the existing governed development proposal instead of starting a new workflow.
```

Diagnostic section:

```text
Diagnostics
- workflow: GOVERNED_DEVELOPMENT_WORKFLOW
- confidence: HIGH
- matched signals: governed-development-pending-approval, APPROVE
```

### 3.3 Workflow Status Block

Current output source:

```text
aigol/cli/aigol_cli.py
```

Current output pattern:

```text
Workflow Name: GOVERNED_DEVELOPMENT_WORKFLOW
Workflow State: WAITING_FOR_APPROVAL
Current Lifecycle Stage: APPROVAL
Next Expected Action: Informational only: provide an explicit operator approval or rejection decision.
WORKFLOW COMPLETE: FALSE
Lifecycle Progress:
Completed Stages: CLARIFICATION
Current Stage: APPROVAL
Remaining Stages: EXECUTION_READY -> EXECUTION_AUTHORIZED -> WORKER_REQUESTED -> ...
```

Assessment: `RUNTIME_ORIENTED`

Confusing fields:

- `Workflow State`;
- `Current Lifecycle Stage`;
- `WORKFLOW COMPLETE`;
- full lifecycle stage list;
- stage constants such as `EXECUTION_AUTHORIZED` and `WORKER_REQUESTED`.

Human-friendly replacement:

```text
Current status: Waiting for your decision.

Nothing will be changed until you approve the proposal.
```

Diagnostic section:

```text
Diagnostics
- workflow_state: WAITING_FOR_APPROVAL
- current_lifecycle_stage: APPROVAL
- workflow_complete: false
- remaining_stages: ...
```

### 3.4 Governed Development Proposal

Current output source:

```text
aigol/runtime/acli_governed_development_execution_bridge.py
```

Current output pattern:

```text
Governed Development Proposal

bridge_status: APPROVAL_REQUIRED
workflow_id: GOVERNED_DEVELOPMENT_WORKFLOW
proposal_id: ...
proposal_hash: sha256:...
target_paths:
- docs/governance/...
approval_required: true
approval_boundary: explicit human APPROVE required before mutation
mutation_performed: false
worker_invoked: false
validation_executed: false
replay_lineage_preserved: true
replay_reference: ...
next_action: APPROVE, REJECT, or REQUEST_MODIFICATION
```

Assessment: `MIXED`

Understandable parts:

- `target_paths`;
- approval boundary;
- mutation and worker flags;
- next action.

Runtime-oriented fields:

- `bridge_status`;
- `workflow_id`;
- `proposal_id`;
- `proposal_hash`;
- boolean field names;
- `replay_lineage_preserved`;
- raw replay path.

Human-friendly replacement:

```text
Proposal ready for review.

ACLI proposes to change:
- docs/governance/...

Before anything changes, you must choose:
- APPROVE to continue
- REJECT to cancel
- REQUEST_MODIFICATION to ask for a changed proposal

No repository changes have been made yet.
No worker has run yet.
Validation has not run yet because execution has not been approved.
```

Diagnostic section:

```text
Diagnostics
- bridge_status: APPROVAL_REQUIRED
- workflow_id: GOVERNED_DEVELOPMENT_WORKFLOW
- proposal_id: ...
- proposal_hash: sha256:...
- replay_reference: ...
```

### 3.5 Approval Decision: APPROVE

Current output pattern:

```text
Governed Development Execution

bridge_status: EXECUTION_COMPLETED
workflow_id: GOVERNED_DEVELOPMENT_WORKFLOW
approval_decision: APPROVED
approval_bypassed: false
proposal_hash: sha256:...
approval_hash: sha256:...
mutation_performed: true
worker_invoked: true
validation_executed: true
workflow_execution_status: GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED
worker_protections_preserved: true
validation_allowlists_preserved: true
replay_lineage_preserved: true
workflow_replay_reference: ...
bridge_replay_reference: ...
failure_reason:
```

Assessment: `MIXED`

Understandable parts:

- approval decision;
- mutation performed;
- worker invoked;
- validation executed.

Runtime-oriented fields:

- `bridge_status`;
- `workflow_id`;
- hashes;
- `workflow_execution_status`;
- invariant flags;
- empty `failure_reason`;
- replay reference names.

Human-friendly replacement:

```text
Approved and executed.

ACLI used your approval to run the governed development workflow.

What happened:
- the approved repository changes were applied
- the repository mutation worker path was used
- validation ran successfully
- replay evidence was recorded

Safety checks:
- approval was not bypassed
- worker protections remained active
- validation allowlists remained active
```

Diagnostic section:

```text
Diagnostics
- bridge_status: EXECUTION_COMPLETED
- workflow_execution_status: GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED
- proposal_hash: sha256:...
- approval_hash: sha256:...
- workflow_replay_reference: ...
- bridge_replay_reference: ...
```

### 3.6 Approval Decision: REQUEST_MODIFICATION

Current output pattern:

```text
Governed Development Modification Requested

bridge_status: MODIFICATION_REQUESTED
workflow_state: WAITING_FOR_OPERATOR_REVISION
workflow_id: GOVERNED_DEVELOPMENT_WORKFLOW
approval_decision: REQUEST_MODIFICATION
approval_bypassed: false
approval_granted: false
approval_hash:
execution_authorized: false
proposal_hash: sha256:...
mutation_performed: false
worker_invoked: false
validation_executed: false
replay_lineage_preserved: true
bridge_replay_reference: ...
next_action: Describe the required proposal change.
failure_reason:
```

Assessment: `MIXED`

Understandable parts:

- modification requested;
- approval was not granted;
- execution was not authorized;
- no mutation, worker, or validation occurred;
- next action asks for revision details.

Runtime-oriented fields:

- `bridge_status`;
- `workflow_state`;
- `workflow_id`;
- `approval_hash`;
- `proposal_hash`;
- `replay_lineage_preserved`;
- empty `failure_reason`.

Human-friendly replacement:

```text
Modification requested.

The current proposal has been stopped.

Nothing was approved.
No repository changes were made.
No worker ran.

Please describe what you want changed in the proposal.
```

Diagnostic section:

```text
Diagnostics
- bridge_status: MODIFICATION_REQUESTED
- workflow_state: WAITING_FOR_OPERATOR_REVISION
- proposal_hash: sha256:...
- bridge_replay_reference: ...
```

### 3.7 Approval Decision: REJECT

Current output pattern:

```text
Governed Development Rejected

bridge_status: REJECTED
workflow_id: GOVERNED_DEVELOPMENT_WORKFLOW
approval_decision: REJECT
approval_bypassed: false
approval_granted: false
approval_hash:
execution_authorized: false
proposal_hash: sha256:...
mutation_performed: false
worker_invoked: false
validation_executed: false
replay_lineage_preserved: true
bridge_replay_reference: ...
failure_reason:
```

Assessment: `MIXED`

Understandable parts:

- rejected;
- approval was not granted;
- no mutation, worker, or validation occurred.

Runtime-oriented fields:

- status constants;
- hashes;
- empty fields;
- replay lineage flags.

Human-friendly replacement:

```text
Proposal rejected.

The current proposal is canceled.

Nothing was approved.
No repository changes were made.
No worker ran.
Replay evidence records the rejection.
```

Diagnostic section:

```text
Diagnostics
- bridge_status: REJECTED
- proposal_hash: sha256:...
- bridge_replay_reference: ...
```

### 3.8 Validation Output

Current governed development bridge output summarizes validation as:

```text
validation_executed: true
workflow_execution_status: GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED
validation_allowlists_preserved: true
```

Other validation renderers use patterns such as:

```text
Validation Status: RESULT_VALIDATED
Replay Reference: ...
```

Assessment: `RUNTIME_ORIENTED`

Confusing fields:

- `validation_executed`;
- `validation_allowlists_preserved`;
- `RESULT_VALIDATED`;
- command status constants.

Human-friendly replacement:

```text
Validation completed successfully.

ACLI ran the approved validation checks and they passed.
```

Diagnostic section:

```text
Diagnostics
- validation_executed: true
- validation_status: RESULT_VALIDATED
- validation_allowlists_preserved: true
- replay_reference: ...
```

For validation failure:

```text
Validation failed.

ACLI stopped the workflow and did not mark the execution as successful.
Review the diagnostics below for the failing check.
```

### 3.9 Replay Review Output

Current output patterns include:

```text
Replay Reference: ...
workflow_replay_reference: ...
bridge_replay_reference: ...
replay_lineage_preserved: true
```

Assessment: `MIXED`

Understandable parts:

- replay location is visible.

Runtime-oriented fields:

- distinction between bridge replay and workflow replay;
- lineage flag;
- raw paths without explanation.

Human-friendly replacement:

```text
Replay evidence recorded.

You can inspect the evidence for this operation here:
- proposal and approval evidence: ...
- workflow execution evidence: ...
```

Diagnostic section:

```text
Diagnostics
- replay_lineage_preserved: true
- bridge_replay_reference: ...
- workflow_replay_reference: ...
```

## 4. Confusing Messages

The most confusing current messages are:

| Current message | Issue | Recommended treatment |
| --- | --- | --- |
| `bridge_status: APPROVAL_REQUIRED` | Runtime constant, not plain language. | Replace primary text with `Proposal ready for review.` |
| `workflow_id: GOVERNED_DEVELOPMENT_WORKFLOW` | Internal workflow identifier. | Show `Governed development workflow` in plain text; move ID to diagnostics. |
| `proposal_hash: sha256:...` | Important evidence but not primary operator language. | Move to diagnostics/evidence. |
| `approval_bypassed: false` | Boolean field requires interpretation. | Say `Approval was not bypassed.` |
| `mutation_performed: false` | Understandable but mechanical. | Say `No repository changes have been made.` |
| `worker_invoked: false` | Technical worker concept. | Say `No worker has run.` |
| `validation_executed: false` | Mechanical status. | Say `Validation has not run yet because execution has not been approved.` |
| `workflow_execution_status: GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED` | Runtime constant. | Say `The governed development workflow completed successfully.` |
| `validation_allowlists_preserved: true` | Governance diagnostic. | Say `Validation ran only through approved checks.` |
| `replay_lineage_preserved: true` | Audit diagnostic. | Say `Replay evidence was recorded and linked.` |
| `failure_reason:` | Empty field looks broken. | Hide when empty; show only on failure. |
| `Current Lifecycle Stage: EXECUTION_AUTHORIZED` | Can imply action is needed even after rejection/modification if state is wrong. | Keep only in diagnostics; primary text should say whether the operator must act. |

## 5. Human-Friendly Replacement Pattern

Every ACLI operator response should follow this order:

```text
1. Plain-language status
2. What happened or will happen
3. What did not happen
4. What the operator can type next
5. Evidence locations
6. Diagnostics
```

Example proposal response:

```text
Proposal ready for review.

ACLI prepared a governed development proposal for your request.

If you approve it:
- repository files may be changed
- validation will run
- replay evidence will be recorded

Nothing has changed yet.

Type APPROVE to continue.
Type REJECT to cancel.
Type REQUEST_MODIFICATION to ask for changes.

Evidence:
- proposal replay: ...

Diagnostics:
- bridge_status: APPROVAL_REQUIRED
- workflow_id: GOVERNED_DEVELOPMENT_WORKFLOW
- proposal_hash: sha256:...
```

## 6. Replay Impact

The language changes should not alter replay authority.

Replay must continue to preserve:

- raw runtime status fields;
- workflow identifiers;
- proposal hashes;
- approval hashes;
- validation statuses;
- replay references;
- fail-closed evidence;
- rendered operator text.

Recommended replay model:

- Keep technical artifacts unchanged.
- Add or update rendered operator message artifacts when text changes.
- Preserve a hash of the rendered operator text.
- Record whether a message section is `operator_summary` or `diagnostics`.

This allows auditors to compare:

- technical truth;
- operator-facing explanation;
- diagnostic evidence.

## 7. Implementation Recommendations

### P0: Separate Operator Summary From Diagnostics

Update governed development bridge rendering so each output has:

- an operator summary;
- next action;
- evidence locations;
- diagnostics.

Affected runtime:

```text
aigol/runtime/acli_governed_development_execution_bridge.py
```

### P0: Hide Empty Fields

Do not render empty `failure_reason`, empty `approval_hash`, or unavailable workflow replay references in the primary operator view.

Show unavailable values only in diagnostics when needed.

### P0: Rewrite Proposal, Rejection, Modification, and Execution Summaries

Rewrite primary messages for:

- proposal ready;
- approved and executed;
- modification requested;
- proposal rejected.

Do not change capture fields or replay semantics.

### P1: Simplify Workflow Status Block

Keep the current detailed workflow status available, but move it under a diagnostic heading for normal ACLI operation.

Primary status should be one sentence:

```text
Current status: Waiting for your approval.
```

### P1: Clarify Replay Paths

Label replay locations by purpose:

- proposal evidence;
- approval evidence;
- execution evidence;
- validation evidence;
- explanation evidence.

### P2: Optional LLM-Assisted Explanation

If deterministic text still proves confusing, use the optional non-authoritative LLM-assisted explanation layer defined by `ACLI_LLM_ASSISTED_EXPLANATION_LAYER_V1`.

Provider output must remain optional, replay-visible, and subordinate to deterministic state.

## 8. Non-Goals

This audit does not recommend:

- changing workflow selection;
- changing HIRR;
- changing approval requirements;
- changing repository mutation behavior;
- changing validation allowlists;
- changing replay authority;
- hiding technical evidence from auditors;
- replacing deterministic output with provider-generated output.

## 9. Final Verdict

The ACLI governed development path is operationally understandable when the human-friendly explanation appears, but several subsequent summaries still expose runtime fields as primary operator language.

The required improvement is presentation separation, not governance redesign:

- primary operator messages should be plain language;
- technical runtime fields should remain available as diagnostics;
- replay should preserve both.

```text
ACLI_OPERATOR_LANGUAGE_AUDIT_COMPLETE
```
