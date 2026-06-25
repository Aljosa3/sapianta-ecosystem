# UNIVERSAL_PRODUCT_CONTRACT_V1

Status: Ready

Target verdict:

```text
UNIVERSAL_PRODUCT_CONTRACT_READY
```

## 1. Purpose

This contract defines how complete products are built on top of:

- Universal ACLI;
- Universal Domain Adapter Contract;
- governed workflows;
- replay-safe evidence;
- explicit human approval.

The product layer composes domains, workflows, workers, providers, replay strategy, deployment boundaries, and governance policies without redefining the operator interaction model.

Universal operator lifecycle:

```text
Human
-> Natural Language
-> HIRR
-> Domain Adapter
-> Product Workflow
-> Proposal
-> Explanation
-> Approval
-> Execution
-> Validation
-> Replay
```

## 2. Product Identity

Every product must define:

```text
product_id
product_name
product_version
product_category
primary_operator
primary_domains
deployment_context
governance_boundary
replay_boundary
certification_status
```

Product identity rules:

- product names must not override domain identities;
- product claims must remain consistent with certified capabilities;
- product positioning may not imply unrestricted autonomy;
- product identity must preserve replay and governance boundaries.

## 3. Product Lifecycle

Every product must pass through:

```text
Definition
-> Domain Composition
-> Workflow Binding
-> Worker Binding
-> Provider Binding
-> Replay Strategy
-> Approval Policy
-> Validation
-> Certification
-> Deployment
-> Operation
-> Review
```

A product may not be operator-exposed until certification and validation requirements are satisfied.

## 4. Product Domains

Each product must declare one or more compliant domains.

Domain declaration:

```text
domain_id
domain_adapter_version
domain_scope
domain_certification_status
domain_risk_classification
domain_replay_schema
```

Rules:

- every domain must conform to `UNIVERSAL_DOMAIN_ADAPTER_CONTRACT_V1`;
- multi-domain products must preserve domain boundaries;
- unsupported domain intents must clarify or fail closed;
- product workflows may compose domains but may not bypass domain certification.

## 5. Product Workflows

Product workflows coordinate domain workflows into product-level outcomes.

Required workflow fields:

```text
product_workflow_id
product_id
workflow_version
domain_workflows
operator_intents
proposal_required
approval_required
execution_allowed
validation_required
replay_required
failure_modes
```

Workflow composition rules:

- every product workflow must route through ACLI/HIRR;
- every executable workflow must produce a proposal before approval;
- approval must bind to the exact product proposal;
- domain workflow outputs must remain replay-visible;
- provider output may not determine product workflow authority.

## 6. Product Worker Sets

Each product must declare its worker set.

Required worker set fields:

```text
worker_set_id
worker_capabilities
domain_bindings
allowed_operations
blocked_operations
mutation_scope
validation_requirements
replay_evidence
```

Worker set rules:

- workers execute only after valid human approval;
- workers may not expand product or domain scope;
- workers may not bypass validation;
- workers must record execution evidence;
- high-risk workers require separate certification.

## 7. Product Cognition Provider Sets

Each product must declare whether cognition providers are used.

Provider set fields:

```text
provider_set_id
provider_roles
provider_tiers
domain_bindings
allowed_provider_tasks
blocked_provider_tasks
fallback_policy
replay_policy
```

Provider rules:

- providers remain non-authoritative;
- providers may explain, summarize, compare, or advise;
- providers may not approve;
- providers may not execute;
- providers may not alter replay;
- provider failure must fall back or fail closed according to product policy;
- provider participation must be replay-visible.

## 8. Product Replay Strategy

Every product must define a replay strategy.

Required replay strategy fields:

```text
product_replay_root
domain_replay_roots
workflow_replay_schema
approval_replay_schema
execution_replay_schema
validation_replay_schema
provider_replay_schema
operator_view_replay_schema
retention_policy
redaction_policy
reconstruction_requirements
```

Replay strategy rules:

- replay remains source of truth;
- replay must reconstruct the product decision chain;
- rendered operator views must be replay-visible;
- provider and worker participation must be visible;
- replay must preserve domain boundaries;
- secrets and uncontrolled sensitive content must not be exposed.

## 9. Product ERR Strategy

Products may use ERR as passive resource metadata and selection evidence.

Product ERR strategy fields:

```text
err_required_capabilities
err_resource_types
err_selection_policy
err_replay_policy
err_fail_closed_conditions
```

ERR rules:

- ERR may select metadata;
- ERR may record selection evidence;
- ERR may not invoke providers;
- ERR may not invoke workers;
- ERR may not approve;
- ERR may not authorize;
- ERR may not mutate replay;
- product workflows must fail closed when ERR cannot resolve a required active resource.

## 10. Product Governance Boundaries

Every product must declare:

```text
authority_boundary
approval_boundary
execution_boundary
provider_boundary
worker_boundary
replay_boundary
deployment_boundary
data_boundary
```

Product governance boundaries must preserve:

- Human = Authority Layer;
- AiGOL = Governance Layer;
- LLM = Cognition or Explanation Layer;
- Worker = Execution Layer;
- Replay = Evidence Layer.

No product may claim:

- autonomous governance replacement;
- unrestricted execution;
- hidden provider authority;
- hidden worker mutation;
- guaranteed legal compliance;
- perfect safety.

## 11. Product Approval Policies

Every product must define approval policies for:

- proposal approval;
- rejection;
- modification request;
- safe resume;
- high-risk actions;
- multi-domain proposals;
- provider-assisted outputs;
- worker execution.

Approval policy rules:

- approval must be explicit;
- approval must bind to proposal hash or product equivalent;
- approval may not be inherited across materially different proposals;
- provider confidence may not become approval;
- domain approval policies must be preserved inside product approval.

## 12. Product Deployment Model

Each product must define deployment model:

```text
local_development
governed_repository
stable_runtime
demo_runtime
production_runtime
release_registry
rollback_policy
operator_access_model
```

Deployment rules:

- deployment must preserve replay lineage;
- product release must be governed;
- stable runtime must not be mutated directly by uncontrolled development paths;
- production deployment requires product-specific certification;
- demo deployment must disclose known limitations.

## 13. Mandatory Product Interfaces

Every product must expose or bind to:

```text
ProductIdentityInterface
ProductDomainCompositionInterface
ProductWorkflowInterface
ProductProposalInterface
ProductExplanationInterface
ProductApprovalPolicyInterface
ProductWorkerSetInterface
ProductProviderSetInterface
ProductReplayInterface
ProductERRInterface
ProductValidationInterface
ProductDeploymentInterface
ProductOperatorExperienceInterface
```

## 14. Optional Capabilities

Optional capabilities include:

- provider-assisted explanation;
- multi-provider cognition comparison;
- guided replay viewer;
- executive console;
- operator console;
- audit export;
- evidence package generator;
- multi-domain workflow orchestration;
- adaptive explanation escalation;
- product-specific dashboards.

Optional capabilities must not alter authority boundaries.

## 15. Extension Mechanisms

Allowed product extensions:

- add certified domain adapter;
- add certified product workflow;
- add bounded worker capability;
- add non-authoritative provider role;
- add replay schema extension;
- add operator rendering extension;
- add deployment profile;
- add audit export format.

Forbidden product extensions:

- replace ACLI operator lifecycle;
- bypass domain adapter contract;
- bypass approval;
- hide replay evidence;
- introduce uncontrolled worker execution;
- make provider output authoritative;
- bypass ERR passivity;
- make product-specific governance incompatible with constitutional baseline.

## 16. Product Composition Rules

A product is a composition of:

```text
Universal ACLI
+ one or more Universal Domain Adapters
+ product workflows
+ product worker sets
+ product provider sets
+ product replay strategy
+ product approval policy
+ product deployment model
```

Composition rules:

1. Product workflow may call domain workflows.
2. Domain workflows may call approved workers.
3. Providers may support explanation or cognition only.
4. Replay must link product-level and domain-level evidence.
5. Operator interaction remains the same across products.
6. Product-specific UI may summarize, but may not change authority.

## 17. Multi-Domain Products

Multi-domain products must define:

```text
domain_order
domain_boundaries
cross_domain_context
cross_domain_approval_policy
cross_domain_replay_linkage
conflict_resolution_policy
```

Multi-domain rules:

- each domain must remain independently replay-visible;
- domain conflicts must clarify or fail closed;
- cross-domain execution requires approval for the full proposal;
- no domain may silently authorize another domain's worker;
- product-level summary must disclose all participating domains.

## 18. Versioning Strategy

Product versions must follow:

```text
<PRODUCT_ID>_PRODUCT_CONTRACT_V<N>
<PRODUCT_ID>_WORKFLOW_<NAME>_V<N>
<PRODUCT_ID>_REPLAY_SCHEMA_V<N>
<PRODUCT_ID>_DEPLOYMENT_PROFILE_V<N>
```

Version increments are required when:

- product domain composition changes;
- product workflow semantics change;
- approval policy changes;
- worker set changes;
- provider set changes;
- replay schema changes;
- deployment boundary changes;
- operator experience changes materially.

## 19. Backward Compatibility

New product versions must:

- reconstruct prior replay evidence;
- preserve approval evidence interpretation;
- preserve proposal hash interpretation;
- preserve domain evidence boundaries;
- preserve rendered operator view hashes where applicable;
- fail closed on unknown or unsupported versions;
- provide migration notes for replay schema changes.

## 20. Certification Requirements

Every product must certify:

```text
PRODUCT_IDENTITY_CERTIFIED
DOMAIN_COMPOSITION_CERTIFIED
WORKFLOW_CERTIFIED
PROPOSAL_CERTIFIED
EXPLANATION_CERTIFIED
APPROVAL_CERTIFIED
WORKER_SET_CERTIFIED
PROVIDER_SET_CERTIFIED
REPLAY_CERTIFIED
ERR_STRATEGY_CERTIFIED
VALIDATION_CERTIFIED
DEPLOYMENT_CERTIFIED
OPERATOR_EXPERIENCE_CERTIFIED
```

Minimum certification scenarios:

1. clear product intent;
2. ambiguous product intent;
3. unsupported unsafe intent;
4. proposal generation;
5. approval and execution;
6. rejection;
7. modification;
8. provider unavailable fallback;
9. ERR unavailable fail-closed when ERR is required;
10. replay reconstruction;
11. deployment boundary verification.

## 21. Validation Requirements

Product validation must include:

- product routing tests;
- domain adapter conformance tests;
- product workflow tests;
- approval policy tests;
- worker boundary tests;
- provider non-authority tests;
- ERR passivity tests;
- replay reconstruction tests;
- deployment boundary tests;
- operator experience tests.

Validation must prove:

```text
no execution before approval
no product workflow bypasses domain adapters
no provider authority
no ERR authority
no worker scope expansion
replay reconstructs product and domain chain
operator interaction remains Universal ACLI-compatible
```

## 22. Acceptance Checklist

A product is accepted only when:

- [ ] Product identity is declared.
- [ ] Product lifecycle is defined.
- [ ] Product domains are declared and domain-contract compliant.
- [ ] Product workflows are defined and certified.
- [ ] Product worker sets are declared and bounded.
- [ ] Product cognition provider sets are declared or explicitly absent.
- [ ] Product replay strategy is defined.
- [ ] Product ERR strategy is defined.
- [ ] Product governance boundaries are documented.
- [ ] Product approval policies are documented.
- [ ] Product deployment model is documented.
- [ ] Optional capabilities are authority-preserving.
- [ ] Multi-domain composition rules are satisfied when applicable.
- [ ] Versioning strategy is declared.
- [ ] Certification scenarios pass.
- [ ] Validation tests pass.
- [ ] Operator experience is certified.

## 23. Compliance Model: Product 1 AI PR Gate

Canonical Product 1 identity remains:

```text
AI Decision Validator
```

This contract models the requested `AI PR Gate` as a Product 1 deployment profile or productized use case:

```text
product_id: PRODUCT_1_AI_PR_GATE
canonical_product_family: AI Decision Validator
product_goal: validate AI-generated PR or change decisions before acceptance
```

### 23.1 Domains

```text
Development
Compliance
Replay Audit
```

### 23.2 Workflows

- PR/change request intake;
- governed proposal review;
- validation evidence review;
- replay audit packet generation;
- approval or rejection recommendation.

### 23.3 Workers

- repository inspection worker;
- validation runner;
- evidence package generator;
- replay reconstruction worker.

### 23.4 Providers

Optional:

- provider-assisted explanation;
- cognition comparison for complex PR risk analysis.

Provider output remains advisory.

### 23.5 Replay Strategy

Product 1 PR Gate replay must connect:

- PR or change request;
- AI output under review;
- validation evidence;
- approval decision;
- replay reconstruction;
- audit packet.

### 23.6 Compliance

| Contract Area | Status |
| --- | --- |
| Universal ACLI reuse | SATISFIED |
| Domain Adapter Contract reuse | SATISFIED |
| Product interaction redesign | NOT_REQUIRED |
| Product-specific workers | REQUIRED |
| Product replay strategy | REQUIRED |
| Product deployment profile | REQUIRED |

Product 1 AI PR Gate modeled status:

```text
PRODUCT_CONTRACT_COMPATIBLE
```

## 24. Compliance Model: Security Platform

Security Platform product identity:

```text
product_id: SECURITY_PLATFORM
product_name: Security Governance And Evidence Platform
```

### 24.1 Domains

```text
Security
Compliance
Infrastructure
Replay Audit
```

### 24.2 Workflows

- security artifact creation;
- control evidence package proposal;
- incident replay review;
- remediation plan proposal;
- security audit export.

### 24.3 Workers

Initial:

- document artifact worker;
- security validation worker;
- evidence package worker;
- replay reconstruction worker.

Blocked until separately certified:

- live remediation worker;
- network scan worker;
- credential rotation worker.

### 24.4 Providers

Optional:

- security advisory cognition provider;
- provider-assisted explanation;
- multi-provider comparison for ambiguous security analysis.

### 24.5 Replay Strategy

Security Platform replay must record:

- security intent;
- asset/control/incident context;
- sensitivity classification;
- proposal;
- approval;
- worker boundary;
- validation;
- provider participation;
- secret boundary evidence.

### 24.6 Compliance

| Contract Area | Status |
| --- | --- |
| Universal ACLI reuse | SATISFIED |
| Domain Adapter Contract reuse | SATISFIED_BY_MODEL |
| Product interaction redesign | NOT_REQUIRED |
| Product-specific workers | REQUIRED |
| Product replay strategy | REQUIRED |
| Live remediation | BLOCKED_UNTIL_CERTIFIED |

Security Platform modeled status:

```text
PRODUCT_CONTRACT_COMPATIBLE_WITH_DOMAIN_ADAPTERS_REQUIRED
```

## 25. Compliance Model: Future HR Platform

Future HR Platform product identity:

```text
product_id: FUTURE_HR_PLATFORM
product_name: HR Governance And Review Platform
```

### 25.1 Domains

```text
HR
Compliance
Business Processes
Replay Audit
```

### 25.2 Workflows

Initial safe workflows:

- HR policy artifact creation;
- HR process checklist proposal;
- review evidence packet;
- employee-impact review proposal;
- compliance gap summary.

Blocked until separately certified:

- employment decision execution;
- compensation changes;
- disciplinary action automation;
- autonomous candidate ranking.

### 25.3 Workers

Initial:

- HR documentation worker;
- evidence package worker;
- policy validation worker;
- replay audit worker.

High-risk workers require separate certification:

- HRIS mutation worker;
- compensation worker;
- disciplinary workflow worker.

### 25.4 Providers

Optional:

- HR policy explanation provider;
- compliance comparison provider;
- ambiguity clarification provider.

Providers must not make people-impacting decisions.

### 25.5 Replay Strategy

HR replay must record:

- HR intent;
- policy or process context;
- privacy and sensitivity flags;
- proposal;
- approval;
- execution boundary;
- validation result;
- provider participation;
- rendered operator view.

Raw personal data must be redacted or excluded according to certified HR policy.

### 25.6 Compliance

| Contract Area | Status |
| --- | --- |
| Universal ACLI reuse | SATISFIED_BY_MODEL |
| Domain Adapter Contract reuse | REQUIRED |
| Product interaction redesign | NOT_REQUIRED |
| HR privacy policy | REQUIRED |
| Product-specific workers | REQUIRED |
| People-impacting execution | BLOCKED_UNTIL_CERTIFIED |

Future HR Platform modeled status:

```text
PRODUCT_CONTRACT_COMPATIBLE_WITH_HIGH_RISK_DOMAIN_CONTROLS_REQUIRED
```

## 26. Reuse Conclusion

All three modeled products reuse:

```text
Universal ACLI
Universal Domain Adapter Contract
Proposal-before-approval lifecycle
Deterministic explanation
Optional non-authoritative provider assistance
Replay evidence
Explicit human approval
```

None require:

- new operator interaction model;
- provider authority;
- worker authority;
- replay bypass;
- approval redesign.

Product differences are expressed through:

- product identity;
- domain composition;
- workflow bindings;
- worker sets;
- provider sets;
- replay strategy;
- deployment model;
- certification scope.

## 27. Final Verdict

```text
UNIVERSAL_PRODUCT_CONTRACT_READY
```

The Universal Product Contract defines how complete AiGOL products are composed from Universal ACLI and Universal Domain Adapter Contract without redefining operator interaction. Product 1 AI PR Gate, Security Platform, and Future HR Platform can all be modeled through the same product contract while preserving governance boundaries, replay authority, provider non-authority, worker constraints, and explicit human approval.
