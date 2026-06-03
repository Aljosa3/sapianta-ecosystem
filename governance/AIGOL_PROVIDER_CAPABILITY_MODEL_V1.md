# AIGOL_PROVIDER_CAPABILITY_MODEL_V1

## Status

Provider capability model.

## Purpose

Provider capabilities define what a provider may be asked to propose.

Capabilities are eligibility metadata only.

Capabilities do not grant authority.

## Capability Entry

Each capability entry should contain:

```text
capability_id
capability_family
description
input_contract
output_contract
allowed_workflows
allowed_domains
proposal_contract
risk_class
requires_human_approval
requires_clarification_support
cost_class
trust_requirement
failure_modes
capability_hash
```

## Initial Capability Families

Initial capability families:

```text
NATIVE_DEVELOPMENT_PROPOSAL
GOVERNANCE_REVIEW_ASSISTANCE
DOMAIN_ARCHITECTURE_PROPOSAL
WORKER_FOUNDATION_PROPOSAL
PROPOSAL_REPAIR
CLARIFICATION_QUESTION_PROPOSAL
EXPLANATION_ONLY
```

## Provider Capability Mapping

Initial provider capability candidates:

| Provider | Candidate Capabilities | Status |
| --- | --- | --- |
| `OPENAI` | native development proposal, governance review, proposal repair, explanation | Existing proposal path partially implemented |
| `ANTHROPIC` | native development proposal, governance review, proposal repair, explanation | Architecture-compatible, not implemented here |
| `CODEX` | implementation-oriented proposal and handoff assistance | Provider identity candidate, no execution authority from this foundation |
| `CLAUDE_CODE` | implementation-oriented proposal and handoff assistance | Provider identity candidate, no execution authority from this foundation |

## Output Contracts

Provider output must be normalized into a governed artifact before use.

For native development, provider output must satisfy:

```text
DEVELOPMENT_PROPOSAL_ARTIFACT_V1
```

Provider output that cannot be normalized fails closed.

## Cost Classes

Cost classes:

```text
UNKNOWN
LOW
MEDIUM
HIGH
RESTRICTED
```

Cost class informs provider selection.

It does not alter governance validation.

## Risk Classes

Risk classes:

```text
LOW_RISK
STANDARD_RISK
HIGH_RISK
REGULATED_DOMAIN
CRITICAL_DOMAIN
```

Trading, healthcare, legal, public services, and critical infrastructure workflows require heightened approval or governance constraints.

## Trust Requirements

Capability use may require:

- minimum provider trust level;
- bounded response size;
- deterministic proposal schema;
- replay-visible provider identity;
- proposal contract validation;
- human approval for high-risk domains.

## Failure Modes

Capability failure modes include:

- provider unavailable;
- malformed response;
- ambiguous proposal;
- missing required fields;
- unknown references;
- authority-bearing output;
- oversized output;
- cost unknown for cost-bounded workflow;
- trust below threshold;
- replay mismatch.

All failure modes must fail closed or escalate to human clarification or approval.

## Provider Independence

Capabilities are generic.

Provider-specific adapters may differ, but provider output must converge into AiGOL-owned artifacts and validation contracts.

