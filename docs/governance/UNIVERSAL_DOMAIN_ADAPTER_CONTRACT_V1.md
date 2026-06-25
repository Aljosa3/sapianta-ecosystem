# UNIVERSAL_DOMAIN_ADAPTER_CONTRACT_V1

Status: Ready

Target verdict:

```text
UNIVERSAL_DOMAIN_ADAPTER_CONTRACT_READY
```

## 1. Purpose

This contract defines the mandatory requirements every new AiGOL domain must satisfy before integrating with the Universal ACLI operator lifecycle.

Universal ACLI lifecycle:

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

The contract preserves:

- Human = Authority Layer;
- AiGOL = Governance Layer;
- LLM = Explanation or Cognition Layer;
- Workers = Execution Layer;
- Replay = Evidence Layer.

No domain adapter may redesign the ACLI interaction model.

## 2. Contract Scope

The contract governs:

- human intent entry;
- workflow integration;
- proposal generation;
- explanation rendering;
- approval handling;
- worker execution;
- replay evidence;
- ERR evidence;
- cognition provider participation;
- domain adapter responsibilities;
- certification and validation.

The contract applies to:

- Development;
- Security;
- HR;
- Energy;
- Infrastructure;
- Compliance;
- Business Processes;
- Future Products.

## 3. Mandatory Interfaces

Every domain must implement or bind to the following interfaces before operator exposure:

```text
HumanIntentEntryInterface
DomainIntentClassifier
DomainContextResolver
DomainWorkflowInterface
DomainProposalInterface
DomainExplanationInterface
DomainApprovalInterface
DomainWorkerInterface
DomainReplayInterface
DomainERREvidenceInterface
DomainValidationInterface
DomainOperatorRenderer
```

## 4. Optional Interfaces

Optional interfaces may be implemented when the domain needs them:

```text
DomainCognitionProviderInterface
DomainProviderComparisonInterface
DomainEvidencePackageInterface
DomainEscalationPolicy
DomainSafeResumeExtension
DomainSecretRedactionInterface
DomainAuditExportInterface
```

Optional interfaces remain subordinate to the mandatory contract.

## 5. Human Intent Entry Requirements

Each domain must accept natural-language requests through ACLI.

The domain adapter must provide:

- supported intent examples;
- unsupported intent examples;
- ambiguity triggers;
- required clarification questions;
- safety rejection conditions;
- domain vocabulary;
- sensitivity indicators.

Required output:

```text
domain_candidate
intent_family
confidence
clarification_required
approval_required
execution_requested
provider_relevance
worker_relevance
fail_closed_reason
```

Rules:

- unclear intent must clarify or fail closed;
- approval bypass requests must not execute;
- provider output must not resolve authority;
- missing domain context must not be fabricated.

## 6. Workflow Interface

Each domain workflow must expose:

```text
workflow_id
domain_id
workflow_version
supported_intents
required_context
proposal_required
approval_required
execution_allowed
validation_required
replay_required
failure_modes
```

Workflow selection must be deterministic.

The workflow interface may not:

- approve execution;
- mutate state before proposal and approval;
- invoke workers directly from routing;
- treat provider confidence as authority.

## 7. Proposal Interface

Each domain must produce a proposal before any execution or mutation.

Required proposal fields:

```text
proposal_id
domain_id
workflow_id
intent_summary
target_objects
expected_changes
what_will_happen
what_will_not_happen
approval_reason
risk_classification
validation_plan
replay_plan
proposal_hash
created_at
```

Domain-specific proposal extensions are allowed when namespaced:

```text
domain_extension.security.*
domain_extension.hr.*
domain_extension.compliance.*
```

Proposal rules:

- proposal hash must bind approval;
- target objects must be explicit;
- mutation scope must be bounded;
- domain risk must be visible to the operator;
- sensitive content must be redacted or rejected according to domain policy.

## 8. Explanation Interface

Each domain must provide deterministic operator explanation.

Required sections:

```text
WHAT I UNDERSTOOD
WHAT WILL HAPPEN
WHAT WILL NOT HAPPEN
WHAT REQUIRES YOUR APPROVAL
WHAT TO TYPE NEXT
REPLAY VISIBILITY
EXPLANATION TRANSPARENCY
```

Explanation output must include:

- authoritative state source;
- explanation source;
- explanation role;
- explanation confidence;
- explanation completeness;
- fallback status;
- replay status;
- provider participation when applicable.

Explanation rules:

- explanations are advisory;
- explanations may not approve;
- explanations may not alter workflow;
- provider-assisted explanation must preserve deterministic fallback;
- rendered operator view must be replay-visible.

## 9. Approval Interface

Each domain must support:

```text
APPROVE
REJECT
REQUEST_MODIFICATION
```

Domain approval interface must expose:

```text
approval_id
proposal_hash
approval_decision
approved_by
created_at
approval_replay_reference
authorization_created
execution_authorized
```

Rules:

- approval must bind to the proposal hash;
- approval may not be inferred;
- approval may not be supplied by provider output;
- restored proposals must be re-presented before execution approval;
- rejection and modification must prevent execution.

## 10. Worker Interface

Each domain worker adapter must expose:

```text
worker_family
worker_capability
worker_version
approved_operation
bounded_inputs
mutation_scope
expected_outputs
validation_requirements
replay_reference
```

Worker rules:

- workers execute only after valid approval;
- workers may not expand mutation scope;
- workers may not reinterpret approval;
- workers may not call providers as authority;
- workers must record execution evidence;
- worker failure must fail closed.

## 11. Replay Interface

Each domain must record replay evidence for:

```text
request
HIRR result
workflow selection
domain context
proposal
explanation
approval decision
worker assignment
execution result
validation result
provider participation
ERR selection
rendered operator view
```

Replay rules:

- replay is source of truth;
- replay artifacts must be hash-verifiable;
- replay must record fallback and fail-closed outcomes;
- replay may not silently omit provider or worker participation;
- replay must not expose uncontrolled secrets.

## 12. ERR Evidence Interface

ERR remains passive shared infrastructure.

Domain adapters may use ERR for capability-based resource metadata lookup.

Required ERR evidence fields:

```text
err_selection_id
required_capability
selected_resource_id
selected_resource_type
resource_status
selection_reason
provider_invoked
worker_invoked
approval_created
execution_authorized
replay_reference
```

ERR rules:

- ERR may select metadata;
- ERR may record selection evidence;
- ERR may not invoke providers;
- ERR may not invoke workers;
- ERR may not approve;
- ERR may not authorize;
- ERR may not rank provider outputs as governance;
- ERR may not mutate replay after selection.

If ERR cannot resolve a valid resource, the consuming workflow must fail closed or ask clarification.

## 13. Cognition Provider Interface

Cognition providers are optional and non-authoritative.

Provider input must include:

```text
authoritative_state
bounded_question
domain_context
preservation_requirements
replay_reference
```

Provider output must include:

```text
provider_id
provider_name
provider_role
provider_tier
response_status
advisory_output
preserved_identifiers
preserved_context
confidence
limitations
authority_granted=false
```

Provider rules:

- provider output may explain, summarize, compare, or propose;
- provider output may not approve or execute;
- provider output may not mutate proposals;
- provider output may not change workflow selection;
- malformed provider output must be discarded and recorded;
- deterministic fallback must remain available when provider output is used for explanation.

## 14. Domain Adapter Responsibilities

Each domain adapter is responsible for:

1. Defining domain vocabulary.
2. Defining supported and unsupported intents.
3. Resolving required context.
4. Mapping domain intent to certified workflow.
5. Producing a domain proposal.
6. Rendering domain-specific operator explanation.
7. Enforcing approval requirements.
8. Binding approved proposals to bounded workers.
9. Validating domain outputs.
10. Writing replay evidence.
11. Handling provider participation.
12. Handling ERR selection evidence.
13. Failing closed on ambiguity, missing context, unsafe content, or invalid provider/worker output.

## 15. Extension Points

Allowed extension points:

- domain intent classifiers;
- domain context resolvers;
- domain proposal schemas;
- domain validation policies;
- domain worker adapters;
- domain replay extensions;
- provider assistance;
- provider comparison;
- domain-specific operator examples;
- domain-specific audit exports.

Forbidden extension points:

- alternate approval semantics;
- hidden execution paths;
- replay bypass;
- provider-authoritative routing;
- worker-authoritative approval;
- autonomous domain mutation without approval;
- uncontrolled secret handling.

## 16. Compatibility Requirements

Every domain adapter must be compatible with:

- Universal ACLI natural-language entry;
- HIRR clarification behavior;
- governed workflow selection;
- proposal-before-approval lifecycle;
- deterministic explanation;
- optional provider-assisted explanation;
- approval, rejection, and modification commands;
- safe resume;
- replay reconstruction;
- fail-closed behavior.

Compatibility must be proven with tests and replay evidence.

## 17. Versioning Strategy

Domain adapters must use explicit versions:

```text
<DOMAIN>_DOMAIN_ADAPTER_V1
<DOMAIN>_WORKFLOW_<NAME>_V1
<DOMAIN>_PROPOSAL_SCHEMA_V1
<DOMAIN>_REPLAY_SCHEMA_V1
```

Version changes are required when:

- proposal schema changes;
- replay schema changes;
- approval semantics change;
- worker boundary changes;
- provider contract changes;
- validation policy changes;
- operator-rendered text changes materially.

Version changes must preserve replay reconstruction for prior versions.

## 18. Backward Compatibility Rules

New domain adapter versions must:

- reconstruct prior replay evidence;
- preserve prior proposal hash interpretation;
- preserve prior approval evidence;
- preserve prior rendered operator view hashes;
- maintain fail-closed behavior for unknown versions;
- provide migration documentation when replay schema evolves.

Breaking changes require:

- new adapter version;
- certification artifact;
- compatibility test;
- operator-facing release note.

## 19. Certification Requirements

Before operator exposure, each domain must produce:

```text
DOMAIN_ADAPTER_CONTRACT_CONFORMANCE
DOMAIN_ROUTING_CERTIFICATION
DOMAIN_PROPOSAL_CERTIFICATION
DOMAIN_APPROVAL_CERTIFICATION
DOMAIN_WORKER_BOUNDARY_CERTIFICATION
DOMAIN_REPLAY_CERTIFICATION
DOMAIN_OPERATOR_EXPERIENCE_VALIDATION
```

Minimum scenarios:

1. Clear supported intent.
2. Ambiguous intent requiring clarification.
3. Unsupported unsafe intent.
4. Proposal generation.
5. Approval execution.
6. Rejection without execution.
7. Modification without execution.
8. Provider unavailable fallback.
9. ERR resource unavailable fail-closed.
10. Replay reconstruction.

## 20. Validation Requirements

Validation must include:

- routing tests;
- proposal schema tests;
- approval hash binding tests;
- worker boundary tests;
- replay reconstruction tests;
- provider malformed-output tests;
- ERR passivity tests;
- fail-closed tests;
- operator-rendering tests;
- safe resume tests.

Validation command selection remains domain-specific, but each domain must at minimum prove:

```text
no execution before approval
no mutation outside scope
no provider authority
no ERR authority
replay reconstructs
operator output is understandable
```

## 21. Acceptance Checklist

A domain adapter is accepted only when every item is true:

- [ ] Domain intent taxonomy exists.
- [ ] Human intent entry requirements are defined.
- [ ] Workflow interface is implemented.
- [ ] Proposal interface is implemented.
- [ ] Explanation interface is implemented.
- [ ] Approval interface is implemented.
- [ ] Worker interface is implemented or explicitly blocked.
- [ ] Replay interface is implemented.
- [ ] ERR evidence interface is implemented or explicitly not required.
- [ ] Cognition provider interface is implemented or explicitly not required.
- [ ] Domain adapter responsibilities are documented.
- [ ] Extension points are bounded.
- [ ] Version identifiers are declared.
- [ ] Backward compatibility rules are satisfied.
- [ ] Certification scenarios pass.
- [ ] Validation tests pass.
- [ ] Operator experience validation passes.

## 22. Compliance Demonstration: Development

Development satisfies the Universal Domain Adapter Contract through the certified governed development lifecycle.

| Contract Area | Development Compliance |
| --- | --- |
| Human intent entry | Natural development prompts route through ACLI and HIRR. |
| Workflow interface | `GOVERNED_DEVELOPMENT_WORKFLOW` provides proposal, approval, execution, validation, and replay lifecycle. |
| Proposal interface | Governed development proposal captures target paths, expected changes, proposal hash, and approval boundary. |
| Explanation interface | Deterministic explanation and source transparency are available; optional provider explanation is advisory. |
| Approval interface | `APPROVE`, `REJECT`, and `REQUEST_MODIFICATION` are supported. |
| Worker interface | Repository mutation worker executes only after approval and within bounded scope. |
| Replay interface | Proposal, approval, execution, validation, explanation, and provider evidence are replay-visible. |
| ERR evidence interface | ERR is not required for core repository mutation path; future provider/worker selection may use passive ERR evidence. |
| Cognition provider interface | Optional explanation provider can augment operator explanation without authority. |
| Validation | Existing governed development and conversational tests verify lifecycle behavior. |

Development certification status:

```text
CONTRACT_CONFORMANT
```

## 23. Compliance Demonstration: Security

Security satisfies the contract as an onboarding model, not yet as an implemented runtime.

| Contract Area | Security Planned Compliance |
| --- | --- |
| Human intent entry | Security domain classifier must recognize security artifact, control, incident, and evidence intents. |
| Workflow interface | `SECURITY_GOVERNED_ARTIFACT_WORKFLOW` or `GOVERNED_DEVELOPMENT_WORKFLOW + SECURITY_DOMAIN_ADAPTER` required. |
| Proposal interface | Security proposal must include asset/control/incident context, sensitivity, target artifact, risk label, and proposal hash. |
| Explanation interface | Reuses deterministic explanation and source transparency; adds no-remediation and no-secret assurances. |
| Approval interface | Reuses explicit approval, rejection, modification, and safe resume. |
| Worker interface | Initial document/evidence workers allowed; live remediation worker blocked until separately certified. |
| Replay interface | Security replay fields required for domain, sensitivity, secret detection, workflow, proposal, approval, validation, and provider participation. |
| ERR evidence interface | Required when selecting Security evidence workers or cognition providers. ERR remains passive. |
| Cognition provider interface | Optional advisory Security explanation or analysis provider; no authority. |
| Validation | Security-specific validation adapter and secret boundary tests required before exposure. |

Security certification status:

```text
INTERACTION_MODEL_CONFORMANT
RUNTIME_ADAPTERS_REQUIRED
```

Security can satisfy the same Universal Domain Adapter Contract without ACLI interaction redesign.

## 24. Final Verdict

```text
UNIVERSAL_DOMAIN_ADAPTER_CONTRACT_READY
```

The Universal Domain Adapter Contract defines the mandatory interfaces, optional interfaces, extension points, compatibility requirements, versioning strategy, backward compatibility rules, certification requirements, validation requirements, and acceptance checklist required for new AiGOL domains. Development demonstrates implemented conformance, and Security demonstrates first-domain onboarding conformance through the same contract with domain adapters still required.
