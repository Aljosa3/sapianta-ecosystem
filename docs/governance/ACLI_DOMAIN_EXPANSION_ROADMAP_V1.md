# ACLI_DOMAIN_EXPANSION_ROADMAP_V1

Status: Ready

Target verdict:

```text
ACLI_DOMAIN_EXPANSION_READY
```

## 1. Purpose

This roadmap defines how the certified ACLI operator experience can be reused across future AiGOL domains.

It extends the operator lifecycle:

```text
Human
-> Natural Language
-> HIRR
-> Workflow
-> Proposal
-> Explanation
-> Approval
-> Execution
-> Replay
```

The roadmap does not certify the listed domains as implemented.

It defines the reusable contract, extension points, and onboarding requirements that future domains must satisfy before entering the operator-facing ACLI path.

## 2. Universal ACLI Contract

Every ACLI-routable domain must obey the same operator contract.

### 2.1 Human Request

The operator may use normal language.

ACLI must:

- preserve the original request;
- detect ambiguity;
- ask clarification when required;
- avoid executing from unclear intent;
- record request evidence in replay.

### 2.2 HIRR

HIRR must produce a deterministic intake result.

HIRR must identify:

- domain candidate;
- intent family;
- ambiguity status;
- approval relevance;
- execution relevance;
- provider relevance;
- missing context.

HIRR must fail closed or ask clarification when confidence is insufficient.

### 2.3 Workflow Selection

Workflow selection must be deterministic.

Every selected workflow must have:

- workflow identifier;
- workflow purpose;
- supported intent family;
- required inputs;
- approval requirements;
- execution boundary;
- replay requirements.

### 2.4 Proposal

Every domain that may create, modify, execute, decide, validate, or report must produce a proposal before approval.

The proposal must show:

- what will happen;
- what will not happen;
- target objects;
- expected outputs;
- approval boundary;
- replay references;
- domain-specific risk labels;
- proposal hash or equivalent binding.

### 2.5 Explanation

Every domain must provide deterministic operator explanation.

The explanation must include:

- what ACLI understood;
- what will happen;
- what will not happen;
- what requires approval;
- what to type next;
- replay visibility;
- explanation source transparency.

Provider-assisted explanations may augment the deterministic explanation but must remain advisory only.

### 2.6 Approval

Approval must be explicit.

No domain may treat provider output, inferred consent, previous approval, or workflow confidence as execution approval.

Approval must bind to the exact proposal or domain equivalent.

### 2.7 Execution

Execution must occur only through a governed worker or domain execution adapter.

The execution layer must:

- preserve domain boundaries;
- preserve worker protections;
- execute only approved operations;
- record execution evidence;
- expose failure reasons.

### 2.8 Replay

Replay remains the source of truth.

Every domain must record:

- request;
- HIRR result;
- workflow selection;
- proposal;
- explanation;
- approval decision;
- execution result;
- validation result;
- provider participation if any;
- rendered operator view.

## 3. Reusable Components

The following components are domain-reusable:

| Component | Reuse Mode |
| --- | --- |
| Natural-language intake | Shared ACLI entrypoint |
| HIRR clarification | Shared ambiguity and clarification handling |
| Workflow routing shell | Shared deterministic routing interface |
| Proposal lifecycle | Shared proposal-before-approval contract |
| Human-friendly explanation | Shared explanation sections and source transparency |
| Optional LLM-assisted explanation | Shared advisory augmentation layer |
| Approval handling | Shared approval, rejection, modification, and resume semantics |
| Replay persistence | Shared replay evidence model |
| Safe resume | Shared pending proposal restoration and re-presentation |
| Operator language conventions | Shared plain-language summary plus diagnostics pattern |

## 4. Domain-Specific Components

Each domain must supply domain-specific definitions for:

- domain vocabulary;
- supported intents;
- required context;
- risk categories;
- proposal schema extensions;
- validation rules;
- execution adapter or worker boundary;
- replay evidence fields;
- fail-closed conditions;
- operator examples.

Domain-specific logic may not override:

- human authority;
- approval requirement;
- replay authority;
- provider non-authority;
- fail-closed behavior;
- deterministic workflow selection.

## 5. Required Extension Points

### 5.1 Domain Intent Classifier

Each domain must provide a deterministic classifier extension:

```text
input: normalized human request + HIRR context
output: domain intent candidate + confidence + required clarification
```

### 5.2 Domain Context Resolver

Each domain must define how required context is acquired.

Examples:

- HR: employee policy, role, review cycle, jurisdiction.
- Security: asset, threat, control, incident reference.
- Energy: site, meter, grid constraint, forecast period.
- Infrastructure: environment, service, deployment boundary.
- Compliance: regulation, control, evidence source.
- Business Processes: process owner, step, approval requirement.

### 5.3 Domain Workflow Adapter

Each domain workflow adapter must expose:

```text
workflow_id
domain_id
supported_intents
proposal_factory
approval_policy
execution_policy
validation_policy
replay_policy
```

### 5.4 Domain Proposal Renderer

Each domain must produce a proposal that a non-technical operator can review.

Required sections:

- operator summary;
- intended action;
- affected object;
- approval reason;
- risk label;
- expected result;
- replay evidence;
- diagnostics.

### 5.5 Domain Validation Adapter

Each domain must define validation rules before operator-facing execution is certified.

Validation may include:

- schema validation;
- policy validation;
- safety boundary validation;
- evidence completeness validation;
- output consistency validation.

### 5.6 Domain Replay Adapter

Each domain must bind all domain-specific evidence into replay without exposing secrets or uncontrolled sensitive content.

## 6. Provider-Independent Interfaces

Provider participation must remain optional and non-authoritative.

Provider-independent interface requirements:

```text
provider_input = authoritative_state + deterministic_explanation + bounded request
provider_output = advisory explanation or cognition artifact
provider_status = used / unavailable / malformed / rejected / fallback
```

Providers may:

- explain;
- summarize;
- compare;
- identify ambiguity;
- propose options.

Providers may not:

- select the authoritative workflow;
- approve execution;
- modify proposals;
- alter replay;
- execute workers;
- bypass validation.

## 7. Worker-Independent Interfaces

Execution must use a worker-independent contract.

Required fields:

```text
worker_family
worker_capability
approved_operation
bounded_inputs
expected_outputs
mutation_scope
validation_requirements
replay_reference
```

Workers may execute only approved operations.

Workers may not:

- reinterpret approval;
- expand mutation scope;
- bypass validation;
- create hidden side effects;
- treat provider output as authorization.

## 8. Domain Onboarding Requirements

### 8.1 HR

Required before operator exposure:

- HR intent taxonomy;
- employee-data sensitivity policy;
- jurisdiction and policy context resolver;
- redaction and privacy rules;
- approval policy for people-impacting actions;
- audit replay fields.

Initial safe use cases:

- policy artifact drafting;
- HR process explanation;
- review checklist proposal;
- non-executing advisory analysis.

Blocked until certified:

- autonomous employment decisions;
- compensation changes;
- disciplinary action execution.

### 8.2 Security

Required before operator exposure:

- asset and control context resolver;
- incident severity taxonomy;
- threat and vulnerability terminology;
- security evidence proposal schema;
- strict secret handling and credential redaction;
- execution boundaries for scanning or remediation workers.

Initial safe use cases:

- security control documentation;
- incident review proposal;
- audit evidence package creation;
- remediation plan proposal.

Blocked until certified:

- unapproved network scans;
- credential mutation;
- automatic production remediation.

### 8.3 Energy

Required before operator exposure:

- site, meter, grid, and forecast context model;
- operational safety constraints;
- regulatory context;
- domain validation rules;
- energy-specific replay evidence.

Initial safe use cases:

- energy report artifact creation;
- anomaly review proposal;
- forecast explanation;
- operational recommendation review.

Blocked until certified:

- live grid actuation;
- automatic consumption control;
- safety-critical operational decisions.

### 8.4 Infrastructure

Required before operator exposure:

- environment classification;
- service inventory context;
- deployment boundary model;
- change-risk labels;
- infrastructure worker adapters;
- rollback and validation evidence.

Initial safe use cases:

- change proposal creation;
- infrastructure documentation updates;
- deployment checklist generation;
- configuration review proposal.

Blocked until certified:

- production deployment;
- destructive infrastructure changes;
- credential or secret modification.

### 8.5 Compliance

Required before operator exposure:

- regulation and control mapping;
- evidence source resolver;
- claim limitation rules;
- compliance artifact schema;
- audit-ready replay package model.

Initial safe use cases:

- compliance evidence summaries;
- control documentation;
- audit packet proposals;
- gap analysis artifacts.

Blocked until certified:

- guaranteed compliance claims;
- legal determinations;
- evidence fabrication.

### 8.6 Business Processes

Required before operator exposure:

- process taxonomy;
- owner and approval mapping;
- process step context resolver;
- change impact model;
- business process validation rules.

Initial safe use cases:

- process documentation;
- checklist creation;
- approval workflow proposal;
- operational improvement artifact.

Blocked until certified:

- unapproved process changes;
- policy override;
- automated business decision execution.

### 8.7 Future Products

Required before operator exposure:

- product-specific operator intent model;
- product lifecycle boundaries;
- proposal schema;
- approval model;
- validation and replay model;
- demo and certification scenarios.

Future products must reuse the universal ACLI contract unless a documented governance exception is approved.

## 9. Domain Integration Checklist

Before a new domain may be exposed through ACLI:

1. Define domain intent taxonomy.
2. Define domain-specific ambiguity cases.
3. Define required context artifacts.
4. Define deterministic workflow routing rules.
5. Define proposal schema and operator renderer.
6. Define approval requirements.
7. Define worker or execution adapter boundary.
8. Define validation rules.
9. Define replay artifact fields.
10. Define provider-independent cognition or explanation contract if providers are used.
11. Define fail-closed conditions.
12. Add operator-facing examples.
13. Add regression tests for routing, proposal, approval, rejection, modification, execution, validation, replay, and resume.
14. Complete real-world operator validation.
15. Record certification verdict.

## 10. Required Runtime Interfaces

Every domain integration must provide or bind to these runtime interfaces:

```text
DomainIntentClassifier
DomainContextResolver
DomainWorkflowAdapter
DomainProposalFactory
DomainExplanationAdapter
DomainApprovalPolicy
DomainExecutionAdapter
DomainValidationAdapter
DomainReplayAdapter
DomainOperatorRenderer
```

Minimum interface contract:

| Interface | Required Output |
| --- | --- |
| `DomainIntentClassifier` | intent family, confidence, clarification need |
| `DomainContextResolver` | required context, missing context, sensitivity flags |
| `DomainWorkflowAdapter` | workflow id, lifecycle, approval requirement |
| `DomainProposalFactory` | proposal artifact, target objects, proposal hash |
| `DomainExplanationAdapter` | deterministic explanation and transparency |
| `DomainApprovalPolicy` | approval commands, hash binding, rejection and modification handling |
| `DomainExecutionAdapter` | bounded execution request and worker result |
| `DomainValidationAdapter` | validation status and failure reasons |
| `DomainReplayAdapter` | replay evidence and reconstruction metadata |
| `DomainOperatorRenderer` | plain-language summary and diagnostics |

## 11. Operator Consistency Rules

All domains must present the same operator rhythm:

```text
What I understood
What will happen
What will not happen
What requires approval
What to type next
Replay visibility
Explanation transparency
Proposal summary
Diagnostics
```

All domains must preserve:

- plain-language primary output;
- diagnostics as secondary output;
- explicit approval commands;
- rejection and modification commands;
- safe resume behavior;
- replay source-of-truth language;
- provider non-authority language;
- validation result visibility.

No domain may hide:

- approval requirement;
- mutation scope;
- replay evidence;
- provider participation;
- fallback or fail-closed status;
- validation failure.

## 12. Expansion Sequencing

Recommended domain expansion order:

1. Compliance.
2. Business Processes.
3. Infrastructure documentation.
4. Security documentation and review.
5. HR policy documentation.
6. Energy reporting and review.
7. Future products.

Rationale:

- start with documentation and evidence domains;
- avoid high-risk autonomous execution early;
- reuse existing governed development and replay surfaces;
- certify operator experience before adding domain-specific execution workers.

## 13. Readiness Gates

A domain is ACLI-ready only when:

```text
HIRR_DOMAIN_READY
WORKFLOW_ROUTING_READY
PROPOSAL_READY
EXPLANATION_READY
APPROVAL_READY
EXECUTION_BOUNDARY_READY
VALIDATION_READY
REPLAY_READY
OPERATOR_EXPERIENCE_VALIDATED
```

If any gate fails, the domain must remain:

```text
NOT_OPERATOR_EXPOSED
```

## 14. Final Verdict

```text
ACLI_DOMAIN_EXPANSION_READY
```

The certified ACLI operator lifecycle is reusable across future AiGOL domains when each domain implements the universal ACLI contract, supplies domain-specific context and validation, preserves provider-independent and worker-independent interfaces, and passes operator experience validation before exposure.
