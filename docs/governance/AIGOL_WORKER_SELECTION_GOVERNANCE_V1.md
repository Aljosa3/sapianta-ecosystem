# AIGOL_WORKER_SELECTION_GOVERNANCE_V1

Status: defined.

Purpose: define governed worker selection across deterministic and LLM workers.

This artifact defines worker selection hierarchy, deterministic-first policy, LLM worker eligibility, worker capability declarations, suitability scoring, failover policy, replay requirements, validation requirements, and certification scenarios.

It does not implement worker selection.

It does not invoke workers.

It does not grant authority to workers.

It does not grant authority to LLMs.

It does not bypass human approval or authorization.

## Context

Certified inputs:

```text
LLM_WORKER_EXECUTION_CERTIFIED
ROLE_SEPARATED_LLM_IDENTITY_CERTIFIED
MULTI_PROVIDER_OPERATIONALLY_READY
HUMAN_INTENT_RESOLUTION_READY
PRODUCT1_END_TO_END_CERTIFIED
```

Core question:

```text
Can AiGOL select between deterministic and LLM workers while preserving governance authority and minimizing unnecessary LLM usage?
```

Answer:

```text
Yes, if worker selection is deterministic-first, capability-driven, replay-visible, validation-bound, fail-closed, and never treats worker or LLM output as authority.
```

## 1. Worker Selection Hierarchy

Canonical hierarchy:

```text
Human Intent
  -> Intent Resolution
  -> Workflow Selection
  -> Worker Capability Requirement
  -> Candidate Worker Discovery
  -> Capability Declaration Review
  -> Suitability Scoring
  -> Deterministic-First Selection
  -> Execution Summary
  -> Human Approval
  -> Authorization
  -> Worker Handoff
  -> Worker Execution
  -> Validation
  -> Replay
```

Selection is not execution.

Selection does not authorize execution.

Selection must produce replay-visible evidence before approval and authorization.

## 2. Deterministic-First Policy

Policy:

```text
deterministic worker preferred when available
LLM worker allowed only when justified
governance remains authoritative
```

Deterministic worker must be selected when:

```text
it satisfies the required capability
it supports the required input and output schema
it can operate inside the authorized target scope
it has deterministic validation
it is enabled
it is certified or explicitly approved for the workflow
```

LLM worker must not be selected merely because it is available.

LLM worker selection requires a positive reason:

```text
semantic transformation required
language-dependent work required
summarization or translation required
repair proposal required
deterministic worker unavailable
deterministic worker insufficient
human explicitly approves LLM worker use after summary
```

## 3. When LLM Workers Are Allowed

LLM workers are allowed for:

```text
translation
summarization
semantic extraction
classification
draft generation
repair proposal generation
operator-facing explanation
structured conversion when validation exists
```

LLM workers are not allowed for:

```text
approval
authorization
credential handling
replay mutation
governance mutation
unbounded external action
hidden side effects
self-selection
self-validation as sole validator
high-impact execution without human review
tasks requiring exact deterministic behavior when deterministic worker exists
```

Required preconditions for LLM worker selection:

```text
role-separated LLM worker identity
worker contract
enabled lifecycle state
credential boundary satisfied
human approval required
authorization required
validation method declared
fail-closed conditions declared
replay requirements declared
```

## 4. Worker Capability Declarations

Every worker candidate must declare capabilities before selection.

Required declaration fields:

```text
worker_id
worker_type
worker_class
role_identity_reference
capability_ids
task_types
input_schema
output_schema
side_effect_types
allowed_target_scopes
forbidden_target_scopes
validation_methods
deterministic_validation_available
requires_llm
requires_external_service
requires_credential
approval_required
authorization_required
replay_required
certification_status
cost_profile
latency_profile
failure_modes
authority_flags
```

Worker classes:

```text
DETERMINISTIC_WORKER
LLM_WORKER
HYBRID_WORKER
MANUAL_REVIEW_WORKER
```

Required authority flags:

```json
{
  "human_authority": true,
  "governance_authority": true,
  "worker_authority": false,
  "llm_worker_authority": false,
  "provider_authority": false,
  "approval_authority": false,
  "authorization_authority": false,
  "replay_authority": false
}
```

## 5. Worker Suitability Scoring

Worker suitability scoring is governance evidence, not final authority.

Scoring must be deterministic and replay-visible.

Canonical scoring dimensions:

```text
capability_match
schema_match
scope_match
validation_strength
certification_status
deterministic_preference
llm_necessity
side_effect_risk
credential_dependency
cost_risk
latency_risk
failure_isolation
human_review_need
```

Recommended score model:

```text
score = capability_match
      + schema_match
      + scope_match
      + validation_strength
      + certification_status
      + deterministic_preference
      - llm_unnecessary_penalty
      - side_effect_risk_penalty
      - credential_dependency_penalty
      - cost_risk_penalty
      - latency_risk_penalty
```

Required qualitative result:

```text
SELECT
REJECT
REVIEW_REQUIRED
FAIL_CLOSED
```

Scoring must explain:

```text
why selected
why rejected
why deterministic worker was preferred
why LLM worker was allowed
why failover was or was not allowed
```

## 6. Failover Policy

Worker failover is not automatic retry.

Failover is allowed only when:

```text
original worker failed before irreversible side effect
failure is isolated
candidate failover worker satisfies the same capability and scope
candidate failover worker has equal or stronger validation
human approval covers failover or new approval is obtained
authorization covers failover or new authorization is issued
replay records original failure and failover selection
```

Failover is forbidden when:

```text
side effect may have partially occurred
verification is inconclusive
failover would expand scope
failover would change worker class from deterministic to LLM without approval
failover would use a disabled identity
failover would hide the original failure
failover would bypass validation
```

If deterministic worker fails and LLM worker is considered as failover, the execution summary must explicitly say:

```text
deterministic worker failed
LLM worker is being considered
LLM worker output is non-authoritative
human approval is required
authorization will be scoped to the failover task
```

## 7. Replay Requirements

Worker selection must produce replay-safe artifacts.

Required artifacts:

```text
WORKER_CAPABILITY_DECLARATION_ARTIFACT_V1
WORKER_CANDIDATE_SET_ARTIFACT_V1
WORKER_SUITABILITY_SCORE_ARTIFACT_V1
WORKER_SELECTION_DECISION_ARTIFACT_V1
WORKER_SELECTION_RATIONALE_ARTIFACT_V1
WORKER_FAILOVER_DECISION_ARTIFACT_V1
WORKER_SELECTION_AUTHORITY_BOUNDARY_ARTIFACT_V1
```

Replay must show:

```text
required capability
candidate workers
worker class for each candidate
deterministic worker availability
LLM worker availability
suitability score per candidate
selected worker
selection rationale
why LLM worker was or was not used
approval requirement
authorization requirement
validation requirement
failover eligibility
authority flags
```

Replay must never record:

```text
credential values
authorization headers
secret payloads
hidden prompts
private input contents unless explicitly approved for replay
```

## 8. Validation Requirements

Worker selection validation must occur before execution.

Validation stages:

```text
candidate declaration validation
capability match validation
schema compatibility validation
target scope validation
certification status validation
lifecycle state validation
authorization requirement validation
approval requirement validation
output validation plan validation
replay artifact validation
```

For LLM workers, additional validation is required:

```text
role-separated identity validation
LLM necessity validation
non-authority flag validation
credential boundary validation
provider/worker identity separation validation
output validation method validation
human-review requirement validation when deterministic validation is insufficient
```

Selection must fail closed if validation cannot prove the selected worker is eligible.

## 9. Certification Scenarios

### WSG-001: Deterministic Worker Available

Expected:

```text
deterministic worker selected
LLM worker not selected
selection rationale records deterministic-first policy
approval still required before execution
authorization still required before execution
replay reconstructs selection
```

### WSG-002: Deterministic Worker Unavailable

Expected:

```text
deterministic worker absence recorded
LLM worker eligibility evaluated
LLM worker selected only if task is appropriate
human approval required
authorization required
validation plan required
replay records why LLM worker was allowed
```

### WSG-003: Multiple LLM Workers Available

Expected:

```text
all LLM candidates scored
role identity separation preserved
best suitable worker selected
non-selected workers recorded with rationale
cost and validation differences visible
human approval required
```

### WSG-004: Worker Failover

Expected:

```text
original worker failure recorded
failure isolation verified
failover eligibility evaluated
approval and authorization coverage verified
failover selection recorded
replay reconstructs both failure and failover
```

### WSG-005: Worker Validation Failure

Expected:

```text
selected worker output fails validation
execution result fails closed or review required
no silent fallback
no hidden retry
failure reason replayed
operator remediation guidance recorded
```

## 10. Certification Requirements

Future executable certification must verify:

```text
deterministic-first policy
LLM worker eligibility
worker capability declaration parsing
worker suitability scoring
selection rationale generation
approval boundary preservation
authorization boundary preservation
failover governance
validation failure fail-closed behavior
replay reconstruction
secret-free evidence
no worker authority transfer
no LLM authority transfer
```

## 11. Pass Criteria

Worker selection governance may certify only if:

```text
deterministic worker is selected when suitable
LLM worker is selected only when justified
all candidates have capability declarations
all candidate scores are replay-visible
selection rationale is replay-visible
approval remains required before execution
authorization remains required before execution
failover is bounded and replay-visible
validation failure fails closed
governance authority is preserved
worker authority remains false
LLM worker authority remains false
```

## 12. Failure Criteria

Certification must fail if:

```text
LLM worker is selected when suitable deterministic worker exists without justification
worker executes from selection alone
approval is bypassed
authorization is bypassed
candidate capability is not declared
suitability scoring is absent
selection rationale is absent
failover hides original failure
failover expands scope without approval
validation failure silently continues
worker or LLM becomes authority
replay cannot reconstruct selection
```

## Final Verdict

```text
WORKER_SELECTION_GOVERNANCE_DEFINED
```
