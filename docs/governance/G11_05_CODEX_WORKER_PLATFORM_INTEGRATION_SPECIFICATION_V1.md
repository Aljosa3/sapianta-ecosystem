# G11-05 Codex Worker Platform Integration Specification V1

Status: Codex Worker Platform integration specified.

Final verdict: CODEX_WORKER_PLATFORM_INTEGRATION_SPECIFIED

## 1. Executive Summary

G11-04 determined that Codex should not remain an indefinite external development tool, but that it must not be integrated as a broad authority.

This specification defines Codex as a governed Platform capability only through already certified roles:

1. Codex as a non-authoritative cognition provider.
2. Codex as a bounded Worker Platform execution capability.

Codex is not a Governance authority, Replay authority, Platform Core orchestrator, ACLI Next interface authority, or Architectural Health authority.

The required integration is therefore not a new subsystem. It is a role-separated composition of existing certified Provider Platform, Worker Platform, Governance, Replay, Platform Core, Platform Digital Twin, and Architectural Health capabilities.

Final finding:

```text
Codex Worker Platform integration is ready for implementation after architectural review, provided provider and worker identities remain separate.
```

## 2. Governed Development Workflow Compliance

This specification applies the certified development sequence:

```text
Capability Discovery
->
Existing Capability Audit
->
Reuse
->
Canonicalization
->
Minimal Extension
->
Implementation
->
Architectural Health Review
->
Architecture Review
->
Certification
```

Current phase:

```text
Canonicalization and Minimal Extension specification
```

No implementation is performed by this artifact.

## 3. Capability Audit

| Capability | Existing Certified Role | Reuse Finding |
| --- | --- | --- |
| Worker Platform | Owns bounded authorized execution, worker dispatch, worker invocation, completion reporting, failure reporting, and worker replay evidence. | Reuse for Codex-as-worker. |
| Provider Platform | Owns provider identity, provider credential references, provider role declarations, and non-authoritative provider boundaries. | Reuse for Codex-as-cognition-provider. |
| Platform Core | Owns orchestration, capability routing, workflow progression, and coordination across Governance, Replay, Worker Platform, Provider Platform, and ACLI Next. | Reuse as the only orchestration authority. |
| Governance | Owns approval, authorization, policy admissibility, and certification decisions. | Reuse for both provider authorization and worker execution authorization. |
| Replay | Owns evidence, reconstruction, execution history, provider evidence, worker evidence, and linkage between governed operations. | Reuse as the only evidence authority. |
| Platform Digital Twin | Provides canonical architectural evidence projection. | Reuse for identity, integration, and responsibility boundary visibility. |
| Architectural Health | Provides deterministic advisory findings about drift, leakage, and architectural risks. | Reuse as advisory checkpoint only. |
| Governed Development Workflow | Defines the canonical development sequence. | Reuse for Codex-assisted development flow. |
| Worker identity model | Provides worker identity, assignment, dispatch, invocation, and result evidence. | Reuse for Codex execution identity. |
| Provider identity model | Provides provider identity, role separation, activation state, and non-authority flags. | Reuse for Codex cognition identity. |
| Vault identity model | Provides secret-free credential references and replay-safe vault references. | Reuse for Codex provider credentials. |
| Credential governance | Provides approval requirements for credential lifecycle operations and secret non-replay. | Reuse for any Codex provider credential. |
| Worker dispatch model | Provides replay-visible dispatch without direct ACLI Next execution. | Reuse for Codex worker dispatch. |

Audit conclusion:

```text
The platform already contains the architectural primitives required for Codex integration.
```

The missing work is Codex-specific identity, policy, evidence, and invocation specification, not a new Platform Core capability.

## 4. Existing Capability Reuse Assessment

Codex integration must reuse the existing identity and execution separation.

Required reuse:

- Provider identity for cognition and advisory output.
- Worker identity for bounded execution.
- Vault credential references for any provider credentials.
- Governance authorization for provider use and worker execution.
- Replay evidence for all provider and worker activity.
- Worker dispatch and invocation for execution activity.
- Platform Core coordination for routing and sequencing.
- ACLI Next presentation for human interaction.
- Architectural Health advisory checks for drift and responsibility leakage.

Forbidden duplication:

- no Codex-owned governance approval model;
- no Codex-owned replay ledger;
- no Codex-owned worker dispatch;
- no ACLI Next-owned Codex routing authority;
- no provider credential replay outside the vault reference model;
- no hidden provider or worker invocation.

## 5. Codex Architectural Position

Codex has two canonical positions.

### 5.1 Codex As Cognition Provider

Purpose:

```text
advisory reasoning, proposal generation, alternatives, uncertainty, recommendations, and candidate formation
```

Authority:

```text
non-authoritative
```

Codex-as-provider may produce:

- implementation proposals;
- specification drafts;
- architecture review drafts;
- certification review drafts;
- alternatives and tradeoff analysis;
- uncertainty statements;
- candidate patch descriptions;
- validation suggestions;
- replay summaries for human review.

Codex-as-provider must not:

- approve execution;
- authorize mutations;
- certify outcomes;
- invoke Workers;
- execute commands;
- mutate repository state;
- override Governance;
- create a separate evidence ledger.

### 5.2 Codex As Execution Worker

Purpose:

```text
bounded governed artifact production and development execution inside Worker Platform scope
```

Authority:

```text
execution only after Governance authorization
```

Codex-as-worker may perform only authorized operation classes, such as:

- read-only repository inspection;
- governed artifact drafting;
- governed file mutation through existing mutation envelopes;
- validation through existing validation workers or approved worker operations;
- evidence summarization from Replay-visible inputs.

Codex-as-worker must not:

- self-authorize;
- approve its own plan;
- bypass Governance;
- bypass Replay;
- bypass Worker Platform;
- invoke providers outside authorized provider policy;
- run broad shell access unless a separate governed capability certifies it;
- perform Git remote, dependency management, deployment, or environment operations unless those capabilities are separately certified.

## 6. Identity Separation Specification

Codex cognition and Codex execution require separate governed identities.

| Identity | Canonical Role | Required Separation |
| --- | --- | --- |
| Codex cognition provider identity | Provider Platform identity for advisory reasoning and candidate material. | Separate provider ID, provider role, credential reference, activation state, evidence chain, metrics, and certification. |
| Codex execution worker identity | Worker Platform identity for bounded authorized execution. | Separate worker ID, worker role, assignment, dispatch, invocation, result evidence, metrics, and certification. |

They must not share:

- authorization artifacts;
- Replay evidence records;
- credential references;
- lifecycle state;
- metrics records;
- cost accounting records;
- certification records.

They may be linked only through explicit Replay references when a provider output informs a later governed worker request.

## 7. Provider Identity Specification

Codex-as-provider must use the existing Provider Platform identity model.

Required provider identity fields:

- provider identity ID;
- external provider family;
- model or tool identity;
- provider role;
- capability declarations;
- credential reference artifact;
- activation status;
- replay lineage;
- rollback reference;
- creation timestamp;
- non-authority flags.

Required provider role:

```text
COGNITION_PROVIDER
```

or a certified Codex-specific provider role that remains advisory only.

Required provider evidence:

- prompt or request hash;
- provider identity;
- credential reference, never credential secret;
- model or tool identity where available;
- response hash;
- response classification;
- advisory-only flag;
- downstream use reference;
- cost and token metrics where available;
- failure reason when fail-closed.

Provider output classification must distinguish:

- proposal;
- explanation;
- recommendation;
- candidate artifact;
- uncertainty statement;
- validation suggestion;
- architecture advisory note.

No provider output may be treated as approval, authorization, execution, certification, or evidence ownership.

## 8. Worker Identity Specification

Codex-as-worker must use the existing Worker Platform identity model.

Required worker identity fields:

- worker identity ID;
- worker role;
- operation class;
- allowed workspace scope;
- allowed mutation scope;
- allowed command or operation class;
- assignment reference;
- dispatch reference;
- invocation reference;
- completion or failure result;
- Replay evidence reference;
- no self-authorization flag.

Required worker lifecycle:

```text
Registered
->
Eligible
->
Assigned
->
Governance-authorized
->
Dispatched
->
Invoked
->
Completed or failed closed
->
Replay reconstructed
->
Reviewed
```

Worker output must include:

- authorized request reference;
- worker identity;
- operation scope;
- pre-state hash where mutation occurs;
- execution or mutation intent;
- bounded result summary;
- bounded stdout and stderr where command execution is certified;
- post-state hash where mutation occurs;
- validation evidence where required;
- failure reason when fail-closed.

Codex worker execution is valid only through Worker Platform dispatch and invocation.

## 9. Platform Core Interaction Model

Platform Core remains the orchestration authority.

For a development request, Platform Core determines the required capability path:

| Request Need | Canonical Path |
| --- | --- |
| Deterministic local execution already certified | Platform Core routes to existing deterministic Worker capability. |
| Advisory reasoning, proposal generation, alternatives, or uncertainty | Platform Core routes to Codex-as-provider or another authorized cognition provider. |
| Bounded artifact production or repository work | Platform Core routes to authorized Worker Platform execution. |
| Both cognition and execution | Platform Core separates provider step from worker step and links them through Replay. |
| Unsupported operation | Platform Core returns governed hybrid guidance through ACLI Next. |

Platform Core must not:

- delegate orchestration to Codex;
- allow Codex to select its own role;
- allow provider output to become execution authorization;
- allow worker output to become certification;
- bypass Governance, Replay, or Worker Platform.

## 10. Governance Model

Governance remains the authorization authority.

Codex integration requires separate Governance decisions for:

- provider activation;
- provider credential use;
- provider request admissibility;
- worker registration;
- worker operation class;
- worker assignment;
- worker execution authorization;
- mutation scope;
- validation requirements;
- failure handling;
- certification.

Minimum Governance policy for Codex-as-provider:

- allowed provider role;
- allowed advisory outputs;
- credential reference authorization;
- input sensitivity policy;
- output classification requirements;
- cost and usage bounds;
- fail-closed conditions.

Minimum Governance policy for Codex-as-worker:

- allowed worker role;
- allowed operation class;
- workspace scope;
- mutation scope;
- command or operation allowlist;
- network policy;
- validation requirements;
- rollback requirements;
- fail-closed conditions.

Provider authorization never authorizes Worker execution.

Worker execution authorization never authorizes provider credential use unless separately authorized.

## 11. Replay Model

Replay remains the evidence authority.

Codex provider and worker evidence must be separate but linkable.

### 11.1 Provider Replay Evidence

Provider Replay must record:

- provider request reference;
- prompt or input hash;
- provider identity reference;
- credential reference, never credential secret;
- model or tool identity;
- response hash;
- advisory classification;
- non-authority flags;
- downstream use reference;
- cost and token metrics where available;
- completion or fail-closed status.

### 11.2 Worker Replay Evidence

Worker Replay must record:

- worker request reference;
- Governance authorization reference;
- worker identity reference;
- assignment reference;
- dispatch reference;
- invocation reference;
- operation scope;
- pre-state hash where applicable;
- execution intent;
- bounded output;
- post-state hash where applicable;
- validation result where applicable;
- completion or fail-closed status.

### 11.3 Linked Reconstruction

When Codex provider output informs Codex worker execution, Replay must record a link:

```text
provider evidence reference
->
human or Governance approval reference
->
worker authorization reference
->
worker execution evidence reference
```

This preserves role separation while allowing complete reconstruction.

## 12. Worker Platform Model

Worker Platform remains responsible for execution only.

Codex-as-worker execution must follow the existing Worker Platform lifecycle:

1. Worker identity is registered or made eligible under Governance policy.
2. Platform Core creates or selects a worker assignment.
3. Governance authorizes the assignment and execution scope.
4. Worker Platform dispatches the worker.
5. Worker Platform invokes the worker inside the authorized boundary.
6. Worker Platform records completion or fail-closed result.
7. Replay records evidence and reconstruction references.
8. ACLI Next displays the result.

Worker Platform must fail closed when:

- worker identity is ambiguous;
- authorization is missing;
- operation scope is unclear;
- output exceeds bounds;
- mutation scope is broader than authorized;
- command class is uncertified;
- provider credentials are requested without provider authorization;
- Replay cannot record evidence.

## 13. Architectural Health Integration

Architectural Health remains deterministic and advisory only.

Architectural Health should evaluate Codex integration for:

- provider and worker identity separation;
- credential reference safety;
- non-authority flags;
- Governance authorization continuity;
- Replay evidence completeness;
- Worker Platform execution boundaries;
- Platform Core orchestration preservation;
- ACLI Next presentation-only behavior;
- absence of hidden execution;
- absence of duplicated authority.

Architectural Health may recommend correction, but it must not authorize or execute correction.

## 14. ACLI Next Presentation Model

ACLI Next remains a thin human interface.

ACLI Next may present:

- whether Codex is proposed as provider or worker;
- required approvals;
- provider advisory output;
- worker execution status;
- Replay references;
- validation summaries;
- Architectural Health findings;
- hybrid guidance if the request exceeds certified capability.

ACLI Next must not:

- choose Codex role independently;
- authorize provider or worker use;
- invoke Codex directly outside Platform Core;
- execute Codex worker activity;
- treat Codex output as approval;
- maintain an alternate Codex session ledger.

## 15. Responsibility Verification

| Component | Certified Responsibility | Codex Integration Boundary |
| --- | --- | --- |
| ACLI Next | Human interaction, display, guidance, delegation. | Presents Codex role, status, approvals, evidence, and findings only. |
| Platform Core | Orchestration and workflow coordination. | Selects capability path and coordinates provider or worker delegation. |
| Governance | Authorization, approval, admissibility, certification. | Authorizes provider use and worker execution separately. |
| Replay | Evidence, reconstruction, execution history. | Records separate provider and worker evidence with explicit links. |
| Worker Platform | Bounded execution. | Executes Codex worker only after Governance authorization. |
| Provider Platform | Non-authoritative provider identity and provider request boundaries. | Hosts Codex cognition provider identity and credential reference. |
| Platform Digital Twin | Canonical architectural evidence projection. | Projects Codex identities, boundaries, and certified integration status. |
| Architectural Health | Deterministic advisory findings. | Reports drift, leakage, and separation risks only. |
| Codex | Provider or worker participant. | Never authoritative; role-limited by Provider Platform or Worker Platform. |

Responsibility verification result:

```text
No ownership movement is required.
```

## 16. Future Extensibility

Codex must not be special-cased as a privileged platform component.

The same integration pattern must support:

- OpenAI coding models;
- Anthropic coding models;
- Gemini coding models;
- local coding models;
- deterministic generators;
- future provider-backed workers.

Future integrations should add or certify identities, policies, and operation classes without changing Platform Core ownership boundaries.

## 17. Non-Goals

This specification does not:

- implement Codex integration;
- grant Codex execution authority;
- grant Codex provider authority;
- create a new orchestration engine;
- redesign Platform Core;
- redesign ACLI Next;
- replace Governance;
- replace Replay;
- expand Git remote workflows;
- expand dependency management;
- expand deployment;
- certify broad shell access.

## 18. Implementation Readiness Assessment

Codex Worker Platform integration is ready for implementation planning under the following conditions:

- Codex provider identity and Codex worker identity remain separate.
- Provider credential references are secret-free and Replay-safe.
- Provider output remains advisory.
- Worker execution occurs only through Worker Platform.
- Governance authorizes provider use and worker execution separately.
- Replay records provider evidence and worker evidence separately.
- Platform Core remains the only orchestration authority.
- ACLI Next remains presentation and guidance only.
- Architectural Health reviews responsibility boundaries before certification.

Recommended implementation sequence:

1. Codex cognition provider identity and evidence envelope.
2. Codex provider architecture review.
3. Narrow Codex execution worker identity and worker request envelope.
4. Codex worker architecture review.
5. Combined provider-worker Replay linkage review.
6. Certification of role-separated Codex integration.

## 19. Final Determination

Codex can be integrated into AiGOL without creating a new authority layer, provided it is treated as two role-separated governed capabilities:

- non-authoritative cognition provider;
- bounded Worker Platform execution worker.

The existing certified Provider Platform, Worker Platform, Governance, Replay, Platform Core, Platform Digital Twin, Architectural Health, and ACLI Next boundaries are sufficient for specification.

Final verdict: CODEX_WORKER_PLATFORM_INTEGRATION_SPECIFIED

## 20. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: CODEX_WORKER_PLATFORM_INTEGRATION_SPECIFIED
