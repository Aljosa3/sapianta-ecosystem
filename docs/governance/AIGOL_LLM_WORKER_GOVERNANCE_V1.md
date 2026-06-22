# AIGOL_LLM_WORKER_GOVERNANCE_V1

Status: defined.

Purpose: define governance for LLM-based workers.

This artifact defines the canonical LLM worker model, role separation requirements, identity separation, worker contract, validation requirements, replay requirements, fail-closed requirements, worker selection policy, and certification requirements.

It does not implement LLM workers.

It does not grant authority to LLMs.

It does not bypass human approval.

It does not bypass worker authorization.

It does not redesign provider governance.

It does not redesign replay.

## Context

Certified inputs:

```text
HUMAN_INTENT_RESOLUTION_READY
ACLI_LIVE_OPERATOR_READY
PRODUCT1_END_TO_END_CERTIFIED
MULTI_PROVIDER_OPERATIONALLY_READY
ROLE_SEPARATED_LLM_IDENTITY_CERTIFIED
PRODUCT1_AUDIT_REVIEW_CERTIFIED
```

Core invariant:

```text
Human = authority
AiGOL = governance
LLM = proposal or bounded execution contributor
Worker = execution role
Replay = evidence
```

Most important question:

```text
Can an LLM safely participate as a worker while remaining non-authoritative and fully governed?
```

Answer:

```text
Yes, if each LLM worker has a role-separated identity, a bounded worker contract, deterministic validation, human approval, governed authorization, fail-closed execution rules, and replay-visible evidence proving that the LLM did not become authority.
```

## 1. Canonical LLM Worker Model

An LLM worker is:

```text
a governed worker identity that uses an LLM-backed capability to perform a bounded task after authorization.
```

An LLM worker is not:

```text
a cognition provider
an approval authority
an authorization authority
a governance authority
a replay authority
an autonomous decision maker
```

LLM workers may support:

```text
translation
repair suggestions
format conversion
draft generation
structured extraction
summarization
classification
test fixture generation
future bounded text or artifact operations
```

LLM workers must not:

```text
approve their own work
authorize their own execution
select themselves without governance
modify replay
hide uncertainty
silently continue after failed validation
execute side effects outside authorized scope
convert provider recommendations into authority
```

## 2. Role Separation Requirements

The same external LLM API may appear in multiple architectural roles only when each role is separately governed.

Canonical roles:

```text
cognition provider
translation worker
repair worker
future worker roles
```

### Cognition Provider

Purpose:

```text
proposal, interpretation, analysis, alternatives, risks, uncertainty
```

Authority:

```text
none
```

Execution:

```text
no worker side effect
```

### Translation Worker

Purpose:

```text
produce a bounded translation artifact under an approved worker contract
```

Authority:

```text
none
```

Execution:

```text
translation output only inside authorized target scope
```

### Repair Worker

Purpose:

```text
produce a bounded repair patch, repair proposal, or repair artifact under an approved worker contract
```

Authority:

```text
none
```

Execution:

```text
repair output only inside authorized target scope and subject to validation
```

### Future Worker Roles

Future roles must declare:

```text
role name
worker purpose
allowed inputs
allowed outputs
forbidden outputs
side-effect scope
validation method
replay artifacts
approval requirement
authorization requirement
failure behavior
```

## 3. Identity Separation

LLM worker identities must be distinct from cognition provider identities.

Canonical examples:

```text
vault://provider/openai-cognition
vault://worker/openai-translation
vault://worker/openai-repair
```

Each identity must have independent:

```text
credential reference
lifecycle state
enable/disable control
authorization policy
usage metrics
cost hooks
participation records
replay evidence
failure metrics
certification status
```

Identity separation rules:

```text
provider identity cannot be reused silently as worker identity
worker identity cannot be reused silently as cognition provider identity
translation worker identity cannot be reused silently as repair worker identity
role-specific enable/disable controls must not affect unrelated roles
metrics must not collapse across roles
cost tracking must preserve role identity
replay must show exact role identity
```

## 4. Worker Contract

Every LLM worker must have a canonical worker contract.

Required contract fields:

```text
worker_id
worker_role
worker_identity_reference
external_provider_family
credential_reference
allowed_task_types
forbidden_task_types
allowed_input_schema
allowed_output_schema
side_effect_scope
validation_method
approval_required
authorization_required
human_confirmation_required
replay_required
fail_closed_conditions
secret_handling_policy
cost_tracking_policy
authority_flags
```

Required authority flags:

```json
{
  "human_authority": true,
  "governance_authority": true,
  "llm_worker_authority": false,
  "provider_authority": false,
  "approval_authority": false,
  "authorization_authority": false,
  "replay_authority": false
}
```

The worker contract must be replay-visible and secret-free.

## 5. Worker Validation Requirements

LLM worker output must be validated before being accepted.

Validation must cover:

```text
schema validity
authorized task type
authorized target
authorized output location
side-effect boundary
content safety constraints
deterministic acceptance rules where possible
human-review requirement when deterministic validation is insufficient
replay completeness
secret absence
```

Examples:

### Translation Worker Validation

Required checks:

```text
input language and output language recorded
output present
output stored only in authorized target
output does not include credential material
translation was not treated as approval
human review required if translation quality is consequential
```

### Repair Worker Validation

Required checks:

```text
repair target authorized
patch or artifact schema valid
patch applies only to authorized files or sandbox
tests or static checks defined before acceptance
repair output does not self-approve
human approval required before applying consequential repair
```

## 6. Replay Requirements

Every LLM worker invocation must record replay-safe artifacts.

Required artifacts:

```text
LLM_WORKER_SELECTION_ARTIFACT_V1
LLM_WORKER_CONTRACT_ARTIFACT_V1
LLM_WORKER_APPROVAL_ARTIFACT_V1
LLM_WORKER_AUTHORIZATION_ARTIFACT_V1
LLM_WORKER_INVOCATION_ARTIFACT_V1
LLM_WORKER_OUTPUT_ARTIFACT_V1
LLM_WORKER_VALIDATION_ARTIFACT_V1
LLM_WORKER_RESULT_ARTIFACT_V1
LLM_WORKER_AUTHORITY_BOUNDARY_ARTIFACT_V1
LLM_WORKER_USAGE_METRIC_ARTIFACT_V1
```

Replay must show:

```text
human request
resolved intent
selected worker identity
why deterministic worker was or was not selected
LLM worker contract
approval evidence
authorization evidence
invocation input reference
output reference
validation result
side-effect result if any
provider family used
role identity used
authority flags
cost and usage hooks
failure reason if failed closed
```

Replay must never record:

```text
credential values
authorization headers
secret prompts
secret files
unredacted sensitive payloads
credential hashes
```

## 7. Fail-Closed Requirements

LLM worker execution must fail closed when:

```text
worker identity is missing
worker identity is disabled
credential is missing
credential is disabled
credential source is not approved
human approval is missing
authorization is missing
contract is missing
contract does not match requested task
input schema is invalid
output schema is invalid
target is outside authorized scope
deterministic validation fails
side-effect verification fails
replay artifact cannot be written
secret-like material would be recorded
authority flags indicate LLM authority
worker attempts to expand its own scope
```

Fail-closed output must include:

```text
failure classification
failed stage
impact
operator-safe remediation
replay reference
retry guidance
```

## 8. Worker Selection Policy

Canonical policy:

```text
deterministic worker preferred when available
LLM worker allowed when appropriate
governance remains authoritative
```

Selection order:

```text
1. Resolve human intent.
2. Identify candidate workflow.
3. Identify deterministic worker candidates.
4. Select deterministic worker if it satisfies task requirements.
5. Consider LLM worker only when deterministic worker is unavailable, insufficient, or inappropriate for the task type.
6. Require execution summary.
7. Require human approval.
8. Issue governed authorization.
9. Invoke selected worker only inside authorized scope.
10. Validate output.
11. Record replay.
```

LLM worker is appropriate for:

```text
language-dependent work
semantic transformation
draft generation
repair proposal generation
unstructured-to-structured conversion
tasks where deterministic validation can verify output boundaries
```

LLM worker is not appropriate for:

```text
final approval
authorization
credential handling
policy mutation
replay mutation
unbounded external action
high-impact decisions without human review
tasks requiring deterministic exactness when deterministic worker exists
```

## 9. Governance Authority Model

The LLM worker may produce output.

AiGOL governs:

```text
worker selection
contract validation
authorization scope
invocation boundary
output validation
side-effect verification
replay evidence
fail-closed behavior
```

Human approves:

```text
execution summary
scope
consequential action
acceptance when human judgment is required
```

The LLM worker never approves:

```text
its own task
its own output
its own authorization
its own replay
its own validation
```

## 10. Certification Requirements

`LLM_WORKER_GOVERNANCE_DEFINED` requires this artifact to define:

```text
canonical LLM worker model
role separation requirements
identity separation requirements
worker contract
worker validation requirements
replay requirements
fail-closed requirements
worker selection policy
certification requirements
```

Future executable certification must cover:

```text
role-separated LLM worker identity creation
worker contract generation
deterministic worker preferred path
LLM worker selected only when appropriate
human approval before LLM worker execution
authorization before LLM worker execution
LLM worker invocation
LLM worker output validation
side-effect verification where applicable
replay reconstruction
usage metrics
cost hooks
failure metrics
secret-free evidence
authority flags prove no LLM authority
fail-closed behavior for missing approval
fail-closed behavior for missing authorization
fail-closed behavior for invalid contract
fail-closed behavior for invalid output
fail-closed behavior for unauthorized target
```

Required future certification scenarios:

```text
LLM-WORKER-001: translation worker positive path
LLM-WORKER-002: repair worker proposal-only path
LLM-WORKER-003: deterministic worker preferred over LLM worker
LLM-WORKER-004: missing approval blocks LLM worker
LLM-WORKER-005: missing authorization blocks LLM worker
LLM-WORKER-006: invalid output fails closed
LLM-WORKER-007: role identity disable blocks only that worker role
LLM-WORKER-008: replay reconstructs worker role and authority boundary
```

## 11. Pass Criteria

An LLM worker governance certification may pass only if:

```text
role identity is distinct
worker contract exists
human approval is required
authorization is required
contract validation passes before invocation
output validation passes before acceptance
side effects remain inside authorized scope
replay reconstructs all stages
metrics preserve worker role identity
secret-free evidence is preserved
LLM worker authority remains false
governance remains authoritative
```

## 12. Failure Criteria

Certification must fail if:

```text
LLM worker identity is merged with cognition provider identity
LLM worker executes without approval
LLM worker executes without authorization
LLM worker selects itself
LLM worker expands scope
LLM worker output is accepted without validation
LLM worker side effect is not verified
provider output is treated as approval
worker output is treated as authority
replay cannot reconstruct the path
secrets appear in replay
```

## Final Verdict

```text
LLM_WORKER_GOVERNANCE_DEFINED
```
