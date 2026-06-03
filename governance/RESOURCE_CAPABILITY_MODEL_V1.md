# RESOURCE_CAPABILITY_MODEL_V1

## Status

Resource capability model.

## Purpose

Resource capabilities define what a Resource role may be selected for.

Capabilities are eligibility metadata.

Capabilities do not grant authority.

## Capability Entry

Each capability entry should contain:

```text
capability_id
capability_family
eligible_resource_categories
eligible_role_types
domain_scope
workflow_scope
input_contract
output_contract
required_authority_profile
required_replay_contract
trust_requirement
cost_requirement
dependency_requirements
failure_modes
capability_hash
```

## Capability Families

Initial capability families:

```text
PROPOSAL_GENERATION
PROPOSAL_REPAIR
CLARIFICATION_ASSISTANCE
GOVERNANCE_REVIEW_ASSISTANCE
WORKER_EXECUTION
IMPLEMENTATION_ASSISTANCE
EVIDENCE_NORMALIZATION
REPLAY_INSPECTION
RISK_ANALYSIS
PORTFOLIO_CONTEXT
DECISION_EXPLANATION
OPERATOR_VISIBILITY
GOVERNANCE_VALIDATION
```

## Capability Requirements

Capability evaluation must validate:

- requested workflow;
- requested domain;
- resource category;
- active role;
- input contract;
- output contract;
- authority boundary;
- trust threshold;
- cost threshold;
- dependency availability;
- replay contract.

Mismatch fails closed.

## Provider Capabilities

Provider-role capabilities include:

- proposal generation;
- proposal repair;
- clarification assistance;
- governance review assistance;
- explanation-only response.

Provider capabilities remain proposal-only.

## Worker Capabilities

Worker-role capabilities include:

- authorized bounded execution;
- evidence normalization;
- replay inspection;
- domain-specific context processing;
- decision explanation;
- implementation assistance where separately authorized.

Worker capabilities require governed authorization before invocation.

## Hybrid Capabilities

Hybrid Resources may expose both provider and worker capabilities.

Each capability must be bound to exactly one role for the current selection.

Hybrid capability overlap must not create authority overlap.

## Trust Requirements

Trust levels:

```text
UNASSESSED
LOW
STANDARD
HIGH
RESTRICTED
SUSPENDED
```

Trust affects eligibility and validation burden.

Trust is not authority.

## Cost Requirements

Cost classes:

```text
UNKNOWN
LOW
MEDIUM
HIGH
RESTRICTED
```

Unknown cost may be allowed only for workflows that do not require bounded cost certainty.

Cost selection must be replay-visible.

