# AIGOL_WORKER_CAPABILITY_MODEL_V1

## Status

Worker capability model.

## Purpose

Worker capabilities define what bounded work a Worker may perform after AiGOL governance and human authorization where required.

Capabilities are scope constraints.

Capabilities do not authorize execution by themselves.

## Capability Entry

Each Worker capability entry should contain:

```text
capability_id
capability_family
domain_scope
input_contract
output_contract
allowed_actions
forbidden_actions
authority_profile_id
required_authorization
required_replay_evidence
trust_requirement
dependency_requirements
failure_modes
capability_hash
```

## Capability Families

Initial Worker capability families:

```text
REPLAY_INSPECTION
EVIDENCE_NORMALIZATION
CONTEXT_ASSEMBLY
RISK_ANALYSIS
PORTFOLIO_CONTEXT
STRATEGY_EVALUATION
DECISION_EXPLANATION
FILESYSTEM_INSPECTION
IMPLEMENTATION_ASSISTANCE
GOVERNANCE_ARTIFACT_INSPECTION
```

## Generic Versus Domain-Specific

Generic capabilities may be reused across domains when domain policy is supplied.

Domain-specific capabilities are bound to a domain foundation and domain boundary guarantees.

Examples:

- replay inspection is generic;
- evidence normalization is generic with domain schema;
- portfolio context is trading-specific unless generalized by future review;
- implementation assistance is hybrid-sensitive and requires strict authority boundaries.

## Allowed Action Representation

Allowed actions must be explicit.

Examples:

- read replay artifact;
- validate hash;
- normalize evidence;
- summarize diagnostics;
- inspect approved task packet;
- produce bounded implementation evidence.

Allowed actions must not imply hidden authority.

## Forbidden Action Representation

Forbidden actions must be explicit.

Examples:

- self-authorize;
- self-dispatch;
- mutate governance;
- mutate replay;
- invoke providers unless separately authorized;
- create workers;
- create domains;
- place orders;
- use brokers;
- use exchanges;
- continue autonomously.

## Trust Levels

Worker trust levels:

```text
UNASSESSED
LOW
STANDARD
HIGH
RESTRICTED
SUSPENDED
```

Trust affects selection and validation intensity.

Trust is not authority.

## Capability Verification

Capability verification requires:

- registry identity;
- capability id;
- input contract match;
- output contract match;
- domain compatibility;
- dependency satisfaction;
- authorization evidence;
- replay contract match.

Mismatch fails closed.

## Capability Evolution

Capability additions, removals, or authority changes require PPP proposal, AiGOL validation, and human approval where risk or authority changes are material.

Silent capability expansion is prohibited.

