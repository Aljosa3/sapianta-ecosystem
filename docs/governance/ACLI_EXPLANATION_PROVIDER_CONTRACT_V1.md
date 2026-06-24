# ACLI_EXPLANATION_PROVIDER_CONTRACT_V1

Status: Ready

Scope: ACLI explanation provider contract

Target verdict:

```text
ACLI_EXPLANATION_PROVIDER_CONTRACT_READY
```

## 1. Purpose

This artifact defines the provider contract for ACLI explanation providers.

Explanation providers may help produce human-facing explanations of technical ACLI runtime state. They do not participate in governance authority, workflow authority, approval authority, execution authority, validation authority, or replay authority.

The contract supports:

- deterministic fallback;
- optional provider-assisted explanation;
- adaptive explanation escalation;
- future multi-provider explanation comparison.

## 2. Authority Boundary

ACLI runtime state remains authoritative.

Authoritative state includes:

- HIRR result;
- routing decision;
- workflow selection;
- workflow state;
- proposal state;
- approval state;
- authorization state;
- mutation state;
- validation state;
- fail-closed state;
- replay references.

Explanation providers are non-authoritative.

Provider output must never:

- authorize execution;
- approve proposals;
- modify workflow state;
- modify replay state;
- modify repository state;
- modify governance artifacts;
- select workflows;
- change HIRR classification;
- suppress fail-closed status;
- invent validation success;
- bypass approval.

Provider output may only explain deterministic state in human-oriented language.

## 3. Explanation Artifact Schema

The canonical provider-assisted explanation artifact type is:

```text
ACLI_EXPLANATION_PROVIDER_ARTIFACT_V1
```

Required fields:

```text
artifact_type
contract_version
explanation_id
turn_id
prompt_id
workflow_id
source_runtime_state_reference
source_runtime_state_hash
deterministic_explanation_reference
deterministic_explanation_hash
provider_request_reference
provider_request_hash
provider_response_reference
provider_response_hash
provider_id
provider_tier
provider_role
rendered_explanation
rendered_explanation_hash
validation_status
display_status
fallback_available
fallback_used
created_at
replay_reference
authority_flags
artifact_hash
```

Required `authority_flags`:

```text
authoritative: false
workflow_authority: false
routing_authority: false
approval_authority: false
authorization_authority: false
execution_authority: false
mutation_authority: false
validation_authority: false
replay_authority: false
provider_authority: false
```

The artifact must fail validation if any authority flag is true.

## 4. Provider Input Contract

The canonical provider request artifact type is:

```text
ACLI_EXPLANATION_PROVIDER_REQUEST_V1
```

Required input fields:

```text
request_id
contract_version
turn_id
prompt_id
provider_id
provider_tier
explanation_goal
source_runtime_state
deterministic_explanation
allowed_operator_actions
forbidden_claims
required_boundaries
replay_context
created_at
```

### 4.1 Source Runtime State

`source_runtime_state` must be a bounded, replay-safe summary of ACLI state.

Allowed fields include:

- workflow id;
- workflow state;
- current lifecycle stage;
- approval required;
- approval granted;
- execution authorized;
- mutation performed;
- worker invoked;
- validation executed;
- validation status;
- fail-closed status;
- failure reason;
- replay locations;
- proposal target paths;
- operator next actions.

The provider must not receive uncontrolled secrets or unbounded repository content.

### 4.2 Deterministic Explanation

`deterministic_explanation` is required.

The provider must explain or improve this deterministic explanation, not replace ACLI state.

### 4.3 Allowed Operator Actions

Allowed actions must be supplied by ACLI, not invented by the provider.

Examples:

```text
APPROVE
REJECT
REQUEST_MODIFICATION
Describe the required proposal change
Inspect replay evidence
```

Provider output must not include unsupported actions.

### 4.4 Forbidden Claims

Every provider request must include forbidden claims.

Required forbidden claims:

- "Execution is authorized" unless ACLI state says execution is authorized.
- "Approval was granted" unless ACLI state says approval was granted.
- "Validation passed" unless ACLI state says validation passed.
- "Repository changes were made" unless ACLI state says mutation occurred.
- "Replay is optional."
- "Approval can be skipped."
- "Provider output is authoritative."

## 5. Provider Output Contract

The canonical provider response artifact type is:

```text
ACLI_EXPLANATION_PROVIDER_RESPONSE_V1
```

Required output fields:

```text
response_id
request_id
provider_id
provider_tier
explanation_text
summary
operator_next_step_text
uncertainty_notes
source_state_acknowledgement
authority_disclaimer
unsupported_claims
requested_operator_clarification
created_at
```

### 5.1 Explanation Text

`explanation_text` must be human-facing and plain language.

It must not include:

- execution authorization not present in ACLI state;
- approval not present in ACLI state;
- mutation not present in ACLI state;
- validation success not present in ACLI state;
- instructions outside ACLI allowed actions.

### 5.2 Authority Disclaimer

The response must include a non-authority disclaimer equivalent to:

```text
This explanation is non-authoritative. ACLI runtime state and replay remain the source of truth.
```

### 5.3 Unsupported Claims

`unsupported_claims` must be an array.

If the provider detects that it may have made an unsupported claim, it must include that claim here. ACLI must reject display when unsupported claims are non-empty unless a validator removes the unsupported text and records the removal.

### 5.4 Requested Operator Clarification

The provider may propose a clarification question only when ACLI permits clarification for the current state.

The clarification question is non-authoritative and must be replayed.

## 6. Replay Requirements

Replay must record:

- source runtime state reference and hash;
- deterministic explanation reference and hash;
- provider request artifact;
- provider response artifact;
- validation artifact;
- final displayed explanation artifact;
- fallback decision;
- escalation decision, if any;
- comparison references, if any.

Replay reconstruction must verify:

- deterministic explanation existed before provider request;
- provider request hash matches replay;
- provider response hash matches replay;
- final displayed text hash matches replay;
- authority flags are all false;
- provider output did not mutate ACLI runtime state;
- provider output did not alter approval, execution, validation, mutation, or replay state.

Replay remains the source of truth.

## 7. Fail-Closed Requirements

ACLI must reject provider output when:

- deterministic explanation is missing;
- source runtime state is missing;
- provider output claims authority;
- provider output changes workflow state;
- provider output authorizes execution;
- provider output implies approval was granted when it was not;
- provider output implies mutation occurred when it did not;
- provider output claims validation success without validation evidence;
- provider output hides approval requirements;
- provider output hides replay evidence;
- provider output suggests unsupported operator actions;
- provider output is malformed;
- provider output cannot be replayed;
- required hashes do not match.

Provider failure must not block deterministic ACLI operation unless policy explicitly requires explanation escalation for the current workflow state. The safe fallback is the deterministic explanation.

## 8. Deterministic Fallback

Deterministic explanation is always required before provider assistance.

Fallback must be available when:

- no provider is configured;
- provider is unavailable;
- provider output is malformed;
- provider output conflicts with ACLI state;
- provider output fails authority validation;
- provider budget is exhausted;
- escalation is disabled.

Fallback replay must record:

```text
fallback_available: true
fallback_used: true
fallback_reason
deterministic_explanation_hash
```

Fallback must not change workflow state or approval state.

## 9. Escalation Compatibility

This contract supports the escalation ladder defined by `ADAPTIVE_EXPLANATION_ESCALATION_V1`:

```text
Deterministic Explanation
-> Low-Cost Explanation Provider
-> High-Capability Explanation Provider
-> Multi-Provider Explanation Comparison
```

Every provider response must include:

- `provider_tier`;
- `provider_id`;
- request hash;
- response hash;
- authority flags;
- validation status.

These fields allow future comparison workflows to consume multiple explanation artifacts and compare:

- agreement;
- disagreement;
- unsupported claims;
- ambiguity;
- clarity;
- confidence.

Comparison output remains non-authoritative.

## 10. Provider Tier Compatibility

Allowed provider tiers:

```text
DETERMINISTIC_BASELINE
LOW_COST_EXPLANATION_PROVIDER
HIGH_CAPABILITY_EXPLANATION_PROVIDER
MULTI_PROVIDER_COMPARISON
```

Provider tier must be recorded in both request and response artifacts.

Tier selection must be replay-visible and must not be made by the provider itself.

## 11. Validation Requirements

Provider output validation must check:

- required fields exist;
- authority flags are false;
- output does not contradict source runtime state;
- output does not introduce unsupported operator actions;
- output includes replay and approval boundaries when relevant;
- output includes non-authority disclaimer;
- output hash matches replay;
- fallback remains available.

Validation statuses:

```text
EXPLANATION_PROVIDER_OUTPUT_ACCEPTED
EXPLANATION_PROVIDER_OUTPUT_REJECTED
EXPLANATION_PROVIDER_OUTPUT_FALLBACK_USED
FAILED_CLOSED
```

## 12. Implementation Recommendations

P0 implementation:

1. Define request, response, validation, and final explanation artifacts.
2. Add a validator that rejects authority claims and state contradictions.
3. Persist provider request and response under explanation replay.
4. Preserve deterministic fallback.
5. Add tests for successful explanation, provider failure, authority-claim rejection, unsupported-action rejection, and fallback use.

P1 implementation:

1. Add escalation decision artifacts.
2. Add low-cost and high-capability tier selection.
3. Add operator clarification request replay.

P2 implementation:

1. Add multi-provider explanation comparison support.
2. Integrate comparison output with audit review.

## 13. Non-Goals

This contract does not:

- implement provider calls;
- redesign ACLI;
- redesign governance;
- redesign workflows;
- authorize execution;
- modify workflow state;
- replace deterministic explanation;
- permit provider output to become source of truth.

## 14. Final Verdict

The ACLI explanation provider contract is ready.

It defines a bounded provider input and output contract that preserves deterministic ACLI authority, replay visibility, fail-closed behavior, deterministic fallback, and future multi-provider comparison compatibility.

```text
ACLI_EXPLANATION_PROVIDER_CONTRACT_READY
```
