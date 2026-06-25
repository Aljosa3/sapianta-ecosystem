# ACLI_FIRST_DOMAIN_ONBOARDING_CERTIFICATION_V1

Status: Certified For Interaction-Model Reuse

Selected domain:

```text
Security
```

Target verdict:

```text
ACLI_FIRST_DOMAIN_ONBOARDING_CERTIFIED
```

## 1. Purpose

This artifact demonstrates that the existing ACLI operator experience can onboard a new non-development domain without redesigning the interaction model.

The selected domain is Security because initial Security use cases can be constrained to documentation, review, evidence packaging, and proposal generation before any live remediation or operational security action is exposed.

The certification evaluates reuse of the ACLI lifecycle:

```text
Natural Language
-> HIRR
-> Workflow
-> Proposal
-> Explanation
-> Approval
-> Execution
-> Replay
```

This artifact does not claim that Security runtime adapters are already implemented.

It certifies that the operator interaction model is sufficient and that onboarding requires domain adapters, not an ACLI interaction redesign.

## 2. Security Domain Scope

Initial Security scope:

- security governance artifact creation;
- security control documentation;
- incident review proposal;
- remediation plan proposal;
- audit evidence package proposal;
- security checklist creation;
- security policy update proposal.

Explicitly out of scope until separately certified:

- unapproved network scanning;
- live remediation;
- credential rotation;
- production firewall changes;
- vulnerability exploitation;
- autonomous incident response;
- secret capture or replay of sensitive credentials.

## 3. Domain Contract

Security must implement the Universal ACLI Contract.

### 3.1 Domain Identity

```text
domain_id: SECURITY
domain_label: Security Governance And Review
operator_scope: security documentation, evidence, review, and bounded proposals
authority_model: Human approval required before execution
provider_role: advisory explanation or security analysis only
worker_role: bounded execution adapter after approval only
```

### 3.2 Supported Security Intents

Initial supported intents:

| Intent | Example Prompt | Execution Allowed |
| --- | --- | --- |
| Security artifact creation | Create security artifact INCIDENT_REVIEW_GUIDE_V1 explaining incident replay review. | Yes, bounded document creation after approval |
| Security control documentation | Update the access control evidence checklist. | Yes, bounded document update after approval |
| Incident review proposal | Draft a proposal to review incident INC-001 evidence. | Proposal only unless a bounded worker is certified |
| Remediation plan proposal | Propose remediation steps for missing audit evidence. | Proposal only |
| Audit evidence package | Create a security audit packet for control AC-2. | Yes, if evidence sources are bounded and approved |

Unsupported intents must fail closed or clarify:

- execute remediation now;
- scan production;
- use or store secrets;
- bypass approval;
- make access changes;
- delete evidence.

### 3.3 Required Context

Security context resolver must identify:

- asset or system name;
- security control or incident reference;
- requested artifact or evidence output;
- sensitivity classification;
- whether credentials or secrets are present;
- intended execution boundary;
- required validation rules;
- replay evidence target.

If required context is missing, ACLI must ask clarification before proposal.

## 4. Workflow Mappings

### 4.1 Natural Language To HIRR

Example:

```text
Create security artifact INCIDENT_REPLAY_REVIEW_V1 explaining how operators inspect replay evidence after a security incident.
```

Expected HIRR result:

```text
domain_candidate: SECURITY
intent_family: SECURITY_ARTIFACT_CREATION
ambiguity_status: RESOLVED
approval_relevance: APPROVAL_REQUIRED
execution_relevance: BOUNDED_ARTIFACT_CREATION
provider_relevance: OPTIONAL_EXPLANATION_ONLY
```

### 4.2 HIRR To Workflow

Expected workflow mapping:

```text
SECURITY_ARTIFACT_CREATION
-> SECURITY_GOVERNED_ARTIFACT_WORKFLOW
```

For first onboarding, this may reuse the governed development lifecycle with a Security domain adapter:

```text
GOVERNED_DEVELOPMENT_WORKFLOW
+ SECURITY_DOMAIN_PROPOSAL_ADAPTER
+ SECURITY_DOMAIN_VALIDATION_ADAPTER
+ SECURITY_DOMAIN_REPLAY_ADAPTER
```

No new operator interaction is required.

### 4.3 Workflow To Proposal

Security proposal must show:

- requested security artifact;
- target document path;
- affected security control, asset, or incident reference;
- sensitivity classification;
- approval requirement;
- what will not happen;
- replay evidence that will be recorded;
- validation checks.

### 4.4 Proposal To Explanation

The existing explanation model is reused:

- what ACLI understood;
- what will happen;
- what will not happen;
- what requires approval;
- what to type next;
- replay visibility;
- explanation source transparency.

Security-specific explanation additions:

- no security action occurs before approval;
- no credential will be stored or replayed;
- provider analysis is advisory only;
- live remediation is not included unless separately proposed and approved.

### 4.5 Approval To Execution

Approval must bind to the exact Security proposal hash.

Approved execution may invoke only a bounded Security worker or existing document mutation worker.

Rejected or modification-requested proposals must not execute.

### 4.6 Execution To Replay

Replay must record:

- original request;
- HIRR result;
- Security workflow mapping;
- Security proposal;
- explanation and transparency;
- approval decision;
- bounded worker request;
- mutation or proposal result;
- validation outcome;
- provider participation if any;
- secret-handling evidence.

## 5. Required Workers

Initial required workers:

| Worker | Purpose | Required For First Security Onboarding |
| --- | --- | --- |
| Document artifact worker | Create or update Security governance artifacts | Yes |
| Evidence packet worker | Assemble bounded security evidence summaries | Optional P1 |
| Security validation worker | Validate Security proposal schema and sensitivity flags | Yes |
| Live remediation worker | Execute security remediation | No, blocked until separately certified |
| Secret scanning worker | Detect credential-like content before replay or mutation | Required before sensitive Security inputs are accepted |

For first onboarding, live remediation is not required.

The domain can certify with documentation and evidence workflows only.

## 6. Required Cognition Providers

Required providers:

```text
None.
```

Optional providers:

- explanation provider;
- security advisory cognition provider;
- multi-provider comparison for ambiguous security analysis.

Provider constraints:

- provider output is advisory;
- provider output may not select workflow authoritatively;
- provider output may not approve execution;
- provider output may not execute remediation;
- provider output may not store secrets;
- provider output must be replay-visible when used.

Initial Security onboarding can proceed with deterministic explanation only.

## 7. Approval Model

Security approval follows the existing ACLI model:

```text
Proposal shown
-> explanation shown
-> operator chooses APPROVE / REJECT / REQUEST_MODIFICATION
-> execution only after valid approval
```

Additional Security approval rules:

- high-sensitivity proposals require explicit confirmation of sensitivity scope;
- credential-like input must fail closed before proposal unless safely redacted;
- live remediation requires a separately certified workflow;
- approval does not authorize actions outside the proposal.

Safe resume remains unchanged:

```text
restart
-> restored proposal shown
-> bare APPROVE does not execute
-> APPROVE THIS PROPOSAL required
```

## 8. Replay Evidence

Security replay package must include:

```text
security_domain_id
security_intent_family
security_context_artifact
security_sensitivity_classification
security_secret_detection_status
security_workflow_id
security_proposal_hash
security_approval_decision
security_worker_boundary
security_validation_status
security_provider_participation
security_rendered_operator_view
```

Replay must not include:

- raw secrets;
- credentials;
- uncontrolled sensitive content;
- hidden remediation actions.

## 9. Onboarding Walkthrough

### Step 1: Operator Request

```text
Create security artifact INCIDENT_REPLAY_REVIEW_V1 explaining how operators inspect replay evidence after a security incident.
```

Expected operator experience:

```text
ACLI understands this as a Security artifact creation request.
```

### Step 2: HIRR

Expected result:

```text
domain: SECURITY
intent: SECURITY_ARTIFACT_CREATION
clarification_required: false
approval_required: true
execution_scope: bounded document creation
```

### Step 3: Workflow

Expected selected workflow:

```text
SECURITY_GOVERNED_ARTIFACT_WORKFLOW
```

or first implementation reuse:

```text
GOVERNED_DEVELOPMENT_WORKFLOW with SECURITY_DOMAIN_ADAPTER
```

### Step 4: Proposal

Expected proposal:

```text
artifact_identifier: INCIDENT_REPLAY_REVIEW_V1
target_path: docs/security/INCIDENT_REPLAY_REVIEW_V1.md
security_scope: incident replay review
sensitivity: low
approval_required: true
mutation_before_approval: false
```

### Step 5: Explanation

Expected explanation:

```text
WHAT I UNDERSTOOD
You want ACLI to create a Security artifact named INCIDENT_REPLAY_REVIEW_V1.

WHAT WILL HAPPEN
If approved, ACLI will create a bounded Security documentation artifact and record replay evidence.

WHAT WILL NOT HAPPEN
No remediation, scanning, credential use, or production security action will occur.
```

### Step 6: Approval

Operator options:

```text
APPROVE
REJECT
REQUEST_MODIFICATION
```

### Step 7: Execution

After approval:

```text
bounded document worker creates the Security artifact
validation runs
replay records evidence
```

### Step 8: Replay

Operator sees:

```text
Security artifact created.
Validation passed.
Replay evidence recorded.
No live remediation occurred.
No credentials were stored.
```

## 10. Reusable Components

The Security onboarding reuses:

- natural language ACLI entrypoint;
- HIRR intake and clarification pattern;
- governed workflow selection pattern;
- proposal-before-approval lifecycle;
- deterministic explanation layer;
- optional LLM-assisted explanation layer;
- explanation source transparency;
- approval, rejection, and modification commands;
- safe resume behavior;
- replay evidence model;
- operator summary plus diagnostics language model.

## 11. Required Extensions

Security requires new domain adapters:

1. `SecurityIntentClassifier`
2. `SecurityContextResolver`
3. `SecurityWorkflowAdapter`
4. `SecurityProposalFactory`
5. `SecurityValidationAdapter`
6. `SecurityReplayAdapter`
7. `SecurityOperatorRenderer`
8. `SecuritySecretBoundary`

These are domain adapters only.

No ACLI interaction redesign is required.

## 12. Identified Gaps

### P0 Before Security Operator Exposure

- Security intent taxonomy does not yet exist as a certified runtime adapter.
- Security context resolver does not yet exist.
- Security proposal schema does not yet exist.
- Security validation adapter does not yet exist.
- Security replay fields are not yet implemented.
- Secret detection and redaction policy must be bound before accepting Security evidence inputs.

### P1 Before Broader Security Use

- Security evidence packet worker.
- Security incident reference resolver.
- Security control mapping.
- Provider-assisted security explanation examples.
- Guided replay review for Security incidents.

### P2 Future Security Expansion

- Multi-provider security cognition comparison.
- Live remediation proposals.
- Change-management integration.
- Security dashboard.

## 13. Verification

### 13.1 No ACLI Interaction Redesign Required

Result:

```text
VERIFIED
```

Security can use the same operator rhythm:

```text
request
-> proposal
-> explanation
-> approval
-> execution
-> validation
-> replay
```

### 13.2 No Operator Retraining Required

Result:

```text
VERIFIED_WITH_DOMAIN_TERMINOLOGY_GUIDE
```

Operators do not need a new interaction model.

They need only Security-specific vocabulary:

- asset;
- incident;
- control;
- sensitivity;
- evidence packet;
- remediation proposal.

### 13.3 Only Domain Adapters Change

Result:

```text
VERIFIED
```

Required changes are domain adapters and domain evidence schemas.

Core ACLI interaction remains unchanged.

## 14. Certification Result

Certification finding:

```text
SECURITY_DOMAIN_ONBOARDING_MODEL_CERTIFIED
```

Meaning:

Security can be onboarded using the existing ACLI operator experience without redesigning the interaction model.

Limitations:

- Security is not yet runtime-implemented.
- Live remediation remains blocked.
- Domain adapters are required before operator exposure.
- Secret handling must be certified before Security evidence inputs are accepted.

## 15. Final Verdict

```text
ACLI_FIRST_DOMAIN_ONBOARDING_CERTIFIED
```

The first non-development domain onboarding certification demonstrates that ACLI's certified operator experience is reusable for Security. The interaction model remains unchanged; onboarding requires domain-specific adapters, validation, replay fields, and worker boundaries.
