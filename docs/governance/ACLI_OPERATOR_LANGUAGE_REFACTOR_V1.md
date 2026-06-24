# ACLI_OPERATOR_LANGUAGE_REFACTOR_V1

Status: Ready

Scope: Operator-facing ACLI language refactor

Target verdict:

```text
ACLI_OPERATOR_LANGUAGE_REFACTOR_READY
```

## 1. Purpose

This artifact records implementation of the P0 recommendations from `ACLI_OPERATOR_LANGUAGE_AUDIT_V1`.

The refactor changes operator-facing message presentation only. It does not redesign governance, workflows, HIRR, approval, execution, validation, replay, provider behavior, or repository mutation behavior.

## 2. Modified Files

Runtime modified:

```text
aigol/runtime/acli_governed_development_execution_bridge.py
```

Tests modified:

```text
tests/test_acli_governed_development_execution_bridge_v1.py
```

Governance artifact added:

```text
docs/governance/ACLI_OPERATOR_LANGUAGE_REFACTOR_V1.md
```

## 3. Implemented P0 Recommendations

### 3.1 Operator Summary And Diagnostics Separation

Governed development bridge output now separates:

```text
Operator Summary
Evidence
Diagnostics
```

The operator summary contains plain-language status and next steps.

The diagnostics section preserves technical fields needed for audit and replay review.

### 3.2 Plain-Language Proposal Message

Proposal output now starts with:

```text
Proposal ready for review.

ACLI prepared a governed development proposal for your request.
```

It explains:

- proposed repository changes;
- that nothing has changed yet;
- that no worker has run;
- that validation has not run because approval has not occurred;
- what the operator can type next.

Runtime fields such as `bridge_status`, `workflow_id`, `proposal_hash`, and replay references remain available under diagnostics.

### 3.3 Plain-Language Approval Execution Message

Execution output now starts with:

```text
Approved and executed.

ACLI used your approval to run the governed development workflow.
```

It explains:

- approved repository changes were applied;
- the repository mutation worker path was used;
- validation ran successfully;
- replay evidence was recorded;
- approval was not bypassed;
- worker protections and validation allowlists remained active.

Technical fields remain under diagnostics.

### 3.4 Plain-Language REQUEST_MODIFICATION Message

`REQUEST_MODIFICATION` output now starts with:

```text
Modification requested.

The current proposal has been stopped.
Nothing was approved.
No repository changes were made.
No worker ran.

Please describe what you want changed in the proposal.
```

The output preserves diagnostics proving:

- `bridge_status: MODIFICATION_REQUESTED`;
- `workflow_state: WAITING_FOR_OPERATOR_REVISION`;
- `approval_granted: false`;
- `execution_authorized: false`;
- `mutation_performed: false`;
- `worker_invoked: false`;
- `validation_executed: false`.

### 3.5 Plain-Language Rejection Message

Rejection output now starts with:

```text
Proposal rejected.

The current proposal is canceled.
Nothing was approved.
No repository changes were made.
No worker ran.
Replay evidence records the rejection.
```

Technical rejection evidence remains under diagnostics.

### 3.6 Empty Field Suppression

Empty `approval_hash` and `failure_reason` fields are no longer shown in operator summaries for rejection or modification paths.

When these values exist, they remain available in diagnostics.

## 4. Governance Preservation

The refactor preserves:

- deterministic routing;
- workflow state tracking;
- explicit approval boundaries;
- proposal hash binding;
- repository mutation worker protections;
- validation allowlists;
- fail-closed behavior;
- replay evidence;
- Human = Authority;
- Replay = Source Of Truth.

The refactor does not change capture schemas or replay authority. It changes only the rendered operator text.

## 5. Replay Impact

Replay behavior is preserved.

The underlying replay captures continue to record:

- bridge status;
- workflow id;
- proposal hash;
- approval hash when approval occurs;
- approval decision;
- mutation status;
- worker invocation status;
- validation status;
- replay references;
- fail-closed evidence when present.

The rendered text now makes the evidence easier to read while keeping raw diagnostic values visible for audit.

## 6. Regression Coverage

Regression coverage verifies:

- proposal messages contain `Operator Summary`, `Evidence`, and `Diagnostics`;
- proposal messages state that no changes have occurred before approval;
- approval execution messages use plain language and preserve diagnostic evidence;
- rejection messages state that nothing was approved or mutated;
- `REQUEST_MODIFICATION` messages ask for a proposal revision;
- `REQUEST_MODIFICATION` does not show blank `approval_hash` or `failure_reason`;
- `REQUEST_MODIFICATION` does not show `EXECUTION_AUTHORIZED`;
- repository mutation does not occur for rejection or modification.

## 7. Validation Results

Executed validation:

```text
python -m py_compile aigol/runtime/acli_governed_development_execution_bridge.py
python -m pytest tests/test_acli_governed_development_execution_bridge_v1.py -q
git diff --check
```

Expected result:

```text
all pass
```

## 8. Final Verdict

The P0 operator-language refactor is ready.

Plain-language operator messages are now separated from technical diagnostics while preserving governance behavior, replay behavior, workflow state tracking, approval boundaries, and fail-closed semantics.

```text
ACLI_OPERATOR_LANGUAGE_REFACTOR_READY
```
