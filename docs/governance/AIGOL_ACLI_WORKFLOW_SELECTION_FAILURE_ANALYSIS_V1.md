# AIGOL ACLI Workflow Selection Failure Analysis V1

Status: empirical failure analysis.

Purpose: determine why the first real ACLI user session selected `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` instead of the expected bounded `FILE_WRITE` worker workflow.

This artifact is analysis only.

It does not redesign ACLI.

It does not redesign HIRR.

It does not introduce new architecture.

It does not authorize execution.

It does not weaken fail-closed behavior.

It does not remove clarification-first behavior.

## Governing Evidence

Primary execution artifact:

```text
AIGOL_ACLI_FIRST_REAL_USER_SESSION_V1
```

Certification report:

```text
runtime/acli_first_real_user_session/e2e_evidence/replay/certification/002_certification_report.json
```

Evidence package:

```text
runtime/acli_first_real_user_session/e2e_evidence/replay/certification/000_evidence_package.json
```

Replay package:

```text
runtime/acli_first_real_user_session/e2e_evidence/replay/certification/001_replay_package.json
```

Session runtime:

```text
runtime/acli_first_real_user_session/session_runtime/ACLI-FIRST-REAL-USER-SESSION-000001
```

Workflow evidence:

```text
runtime/acli_first_real_user_session/e2e_evidence/replay/workflow/000_workflow_selection_evidence.json
```

## Failure Summary

Expected workflow target:

```text
BOUNDED_FILE_WRITE_WORKER_USER_SESSION
```

Observed workflow target:

```text
CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
```

Observed certification result:

```text
ACLI_FIRST_REAL_USER_SESSION_FAILED
```

The FILE_WRITE worker continuation succeeded after governed authorization, ERR resolution, worker invocation, and replay reconstruction.

The end-to-end ACLI certification failed because ACLI did not select the bounded worker workflow from the normal-language session.

Fail-closed behavior was preserved:

- ACLI did not silently invoke a worker;
- ACLI did not bypass approval;
- ACLI did not mutate governance;
- ACLI did not mutate replay;
- the downstream worker path required explicit governed continuation.

## Reconstructed Human Session

Normal user prompt:

```text
Can you make a small proof note that shows this system really did something safely?
```

Normal user clarification response:

```text
Yes.
```

Normal user approval phrase:

```text
Approved.
```

The user did not name:

- workflows;
- domains;
- governance;
- ERR;
- workers;
- replay artifacts;
- internal commands.

This satisfies the normal-human input condition for the validation.

## Intent-Resolution Reconstruction

Turn 1 routing artifact:

```text
runtime/acli_first_real_user_session/session_runtime/ACLI-FIRST-REAL-USER-SESSION-000001/TURN-000001/conversational_cli_routing/000_conversational_routing_decision_recorded.json
```

Observed Turn 1 values:

```text
workflow_id = HUMAN_INTENT_CLARIFICATION_INTAKE
routing_status = CLARIFICATION_REQUIRED
intent_family = AMBIGUOUS_INTENT
confidence = LOW
matched_terms = unknown-human-intent
expected_workflow_targets = CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
worker_invoked = false
execution_requested = false
authorization_created = false
```

Interpretation:

The initial prompt was correctly treated as clarification-required, but the expected workflow target was seeded as `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION`.

The prompt did not receive a worker-capability interpretation at intake time.

## Clarification Reconstruction

Turn 1 clarification questions:

```text
What are you trying to improve or control?
Does this involve AI outputs, human approval, compliance evidence, or operational decisions?
Should we start with planning, clarification, or a governed workflow proposal?
```

Turn 2 clarification response artifact:

```text
runtime/acli_first_real_user_session/session_runtime/ACLI-FIRST-REAL-USER-SESSION-000001/TURN-000002/human_intent_clarification_continuity/001_human_intent_clarification_response_recorded.json
```

Observed Turn 2 response values:

```text
execution_requested = false
provider_invoked = false
worker_invoked = false
```

The response artifact records the reply binding and hashes, but it does not surface a semantic signal such as:

```text
file_write
proof note
bounded proof action
worker execution
create one file
```

The recorded response therefore provided no deterministic worker-routing signal to the continuity runtime.

## Continuity-State Reconstruction

Turn 2 target refinement artifact:

```text
runtime/acli_first_real_user_session/session_runtime/ACLI-FIRST-REAL-USER-SESSION-000001/TURN-000002/human_intent_clarification_continuity/002_human_intent_workflow_target_refinement_recorded.json
```

Observed target refinement values:

```text
original_intent_family = AMBIGUOUS_INTENT
original_expected_workflow_targets = CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
clarification_response_signals = []
refined_intent_family = AMBIGUOUS_INTENT
refined_workflow_targets = CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
selected_workflow_id = CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
refinement_status = TARGET_PRESERVED_LOW_CONFIDENCE
refinement_reason = clarification response did not contain deterministic target refinement signals
worker_invoked = false
```

Turn 2 resolution artifact:

```text
runtime/acli_first_real_user_session/session_runtime/ACLI-FIRST-REAL-USER-SESSION-000001/TURN-000002/human_intent_clarification_continuity/003_human_intent_clarification_resolution_recorded.json
```

Observed resolution values:

```text
resolution_status = INTENT_RESOLVED_AFTER_CLARIFICATION
selected_workflow_id = CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
worker_invoked = false
```

Interpretation:

Continuity preserved the original target because the clarification response was not interpreted as a deterministic worker execution request.

This was fail-closed and replay-visible, but not sufficient for the expected first real user session.

## Workflow-Selection Decision Reconstruction

Turn 2 workflow selection artifact:

```text
runtime/acli_first_real_user_session/session_runtime/ACLI-FIRST-REAL-USER-SESSION-000001/TURN-000002/human_intent_clarification_continuity/004_human_intent_workflow_selection_after_clarification_recorded.json
```

Observed workflow selection values:

```text
selection_status = WORKFLOW_SELECTION_AFTER_CLARIFICATION
routing_status = WORKFLOW_SELECTED
workflow_id = CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
worker_invoked = false
execution_requested = false
authorization_created = false
```

Session workflow evidence:

```text
runtime/acli_first_real_user_session/e2e_evidence/replay/workflow/000_workflow_selection_evidence.json
```

Observed validation values:

```text
expected_workflow_target = BOUNDED_FILE_WRITE_WORKER_USER_SESSION
turn1_expected_workflow_targets = CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
turn2_refined_workflow_targets = CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
turn2_selected_workflow_id = CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
workflow_selection_verified = false
workflow_gap = ACLI_WORKFLOW_SELECTION_GAP
```

## Exact Divergence Point

The decisive divergence occurred at:

```text
TURN-000002/human_intent_clarification_continuity/002_human_intent_workflow_target_refinement_recorded.json
```

The immediate cause was:

```text
clarification_response_signals = []
refinement_status = TARGET_PRESERVED_LOW_CONFIDENCE
selected_workflow_id = CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
```

The prior enabling condition occurred at Turn 1:

```text
expected_workflow_targets = CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
```

Because the original target was domain clarification and no later deterministic refinement signal was detected, continuity preserved the domain-clarification target.

## Code-Level Decision Context

The intake runtime currently maps all non-general-improvement intent families to `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION`:

```text
aigol/runtime/human_intent_clarification_intake_runtime.py
_expected_workflow_targets
```

Observed behavior:

```text
GENERAL_IMPROVEMENT_INTENT -> OCS_LLM_COGNITION
all other intent families -> CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
```

The continuity runtime currently supports only:

```text
CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
OCS_LLM_COGNITION
```

Code location:

```text
aigol/runtime/human_intent_clarification_continuity_runtime.py
SUPPORTED_TARGET_WORKFLOWS
```

The refinement logic recognizes advisory and governed-domain/evidence-planning signals, but it does not recognize a bounded file-write proof action as a supported workflow target.

If no deterministic signal is detected, it returns:

```text
selected_workflow_id = original_target
refinement_status = TARGET_PRESERVED_LOW_CONFIDENCE
```

This exactly matches the replay.

## Issue Classification

### Intake Classification

Status:

```text
CONTRIBUTING_FACTOR
```

The initial prompt was classified as `AMBIGUOUS_INTENT`, which is acceptable for clarification-first behavior.

However, the expected target set did not include a bounded worker-execution candidate.

This made `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` the only available initial target.

### Clarification Interpretation

Status:

```text
PRIMARY_DEFECT
```

The clarification response `Yes.` did not produce deterministic target-refinement signals.

Given the prior ACLI question, `Yes.` was a natural human answer, but it was semantically insufficient for the current continuity runtime.

The runtime preserved the previous target instead of asking a more specific approval-bound clarification or routing to a bounded worker candidate.

### Continuity Handling

Status:

```text
CONTRIBUTING_FACTOR
```

Continuity behaved deterministically and replay-safely.

The gap is that continuity can only refine toward currently supported targets and does not represent the certified bounded FILE_WRITE worker path as a selectable target.

### Workflow Routing

Status:

```text
PRIMARY_DEFECT
```

The expected worker workflow:

```text
BOUNDED_FILE_WRITE_WORKER_USER_SESSION
```

was not available as a supported post-clarification workflow target.

### Workflow Prioritization

Status:

```text
SECONDARY_DEFECT
```

Because only domain clarification and OCS cognition were available to the human-intent continuity layer, prioritization could not prefer the bounded worker path even after a proof-action scenario.

### Replay State Usage

Status:

```text
NO_DEFECT_FOUND
```

Replay state was preserved and accurately reconstructed the failure.

The issue is not replay loss or replay corruption.

## Root Cause

Root cause:

```text
ACLI human-intent clarification continuity does not yet expose the certified bounded FILE_WRITE worker path as a deterministic workflow-selection target.
```

The system handled ambiguity safely, but its routing vocabulary was narrower than the certified execution capability now available after FILE_WRITE worker certification.

The defect is therefore an implementation/routing coverage gap after the provider and worker execution certification phase.

It is not a constitutional architecture failure.

It is not an ERR failure.

It is not a FILE_WRITE worker failure.

It is not a replay runtime failure.

It is not a fail-closed failure.

## Minimal Remediation Proposal

Add the smallest routing capability needed for the already-certified path.

### Remediation Scope

Introduce or register a bounded workflow target:

```text
BOUNDED_FILE_WRITE_WORKER_USER_SESSION
```

The target must remain:

- clarification-first;
- approval-gated;
- ERR-resolved;
- authorization-gated;
- replay-visible;
- fail-closed before execution;
- limited to the certified FILE_WRITE worker path.

### Intake Remediation

For prompts containing normal-human proof-action signals such as:

```text
make a proof note
create a proof note
show this system did something safely
create one evidence file
write a small evidence note
```

intake may include:

```text
expected_workflow_targets = [
  CREATE_DOMAIN_COMPLIANCE_CLARIFICATION,
  BOUNDED_FILE_WRITE_WORKER_USER_SESSION
]
```

or, when sufficiently deterministic:

```text
expected_workflow_targets = [
  BOUNDED_FILE_WRITE_WORKER_USER_SESSION
]
```

### Clarification Remediation

When ACLI asks whether to create one bounded proof note and the user answers with plain confirmation such as:

```text
Yes.
Approved.
Go ahead.
```

the continuity runtime should bind the answer to the previous ACLI clarification context, not interpret it in isolation.

If the previous clarification proposed a bounded file-write proof action, then `Yes.` may refine to:

```text
selected_workflow_id = BOUNDED_FILE_WRITE_WORKER_USER_SESSION
```

only if the previous clarification context explicitly constrained:

- one file;
- fixed filename or user-confirmed filename;
- fixed content or user-confirmed content;
- certified FILE_WRITE worker path;
- no other filesystem changes;
- explicit approval before execution.

### Continuity Remediation

Extend supported target workflows minimally:

```text
SUPPORTED_TARGET_WORKFLOWS += BOUNDED_FILE_WRITE_WORKER_USER_SESSION
```

This must not imply worker invocation.

It should only permit workflow selection after clarification.

Execution must remain blocked until approval and authorization evidence exist.

### Workflow Routing Remediation

Add deterministic refinement signals for bounded proof-file execution:

```text
proof note
evidence file
create one file
fixed proof text
bounded file write
file-write worker
certified file-write path
```

The routing result should be:

```text
routing_status = WORKFLOW_SELECTED
workflow_id = BOUNDED_FILE_WRITE_WORKER_USER_SESSION
worker_invoked = false
authorization_created = false
execution_requested = false
```

Worker invocation must occur only in the later approval/authorization phase.

### Test Remediation

Add focused regression coverage for the first-real-user-session prompt:

```text
Can you make a small proof note that shows this system really did something safely?
Yes.
Approved.
```

Expected assertions:

```text
Turn 1 remains clarification-first.
Turn 2 selects BOUNDED_FILE_WRITE_WORKER_USER_SESSION.
No worker is invoked during clarification.
Approval is required before execution.
Replay records the selected workflow.
Unsupported or incomplete requests still fail closed.
```

## Preservation Requirements

Any remediation must preserve:

- human authority;
- explicit approval;
- authorization boundary;
- ERR boundary;
- worker capability boundary;
- replay evidence;
- fail-closed behavior;
- deterministic routing;
- clarification-first behavior;
- no provider self-authorization;
- no worker self-authorization;
- no automatic filesystem mutation from intake alone.

## Non-Goals

This analysis does not recommend:

- redesigning ACLI;
- redesigning HIRR;
- creating a new worker contract;
- broadening filesystem write authority;
- bypassing approval;
- replacing deterministic routing with unconstrained LLM routing;
- treating `Yes.` as approval without a bound prior proposal;
- invoking workers from clarification intake;
- hiding the failed certification result.

## Risk Analysis

Primary risk:

```text
Over-remediation could turn normal-language confirmation into unsafe execution authority.
```

Required mitigation:

```text
Workflow selection may recognize bounded worker intent, but execution must remain impossible until explicit approval and authorization evidence are recorded.
```

Secondary risk:

```text
Adding too many normal-language signals may over-route advisory requests to worker execution.
```

Required mitigation:

```text
Ambiguous or advisory prompts should remain clarification-first or advisory-routed unless the bounded action is explicit and confirmed.
```

Replay risk:

```text
No replay-state defect was found.
```

Required mitigation:

```text
Preserve the existing replay-visible target-refinement artifacts and add selected-worker-workflow evidence only as ordinary replay artifacts.
```

## Final Verdict

```text
WORKFLOW_SELECTION_DEFECT_CONFIRMED
```

The observed behavior is not expected for `AIGOL_ACLI_FIRST_REAL_USER_SESSION_V1`.

ACLI preserved safety, clarification-first behavior, and replay evidence, but failed to select the certified bounded FILE_WRITE worker workflow required by the first real user session scenario.
