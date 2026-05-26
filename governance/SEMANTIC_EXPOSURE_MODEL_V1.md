# SEMANTIC_EXPOSURE_MODEL_V1

## Purpose

The Semantic Exposure Model v1 defines constitutional governance for payload sovereignty, privacy-preserving cognition, governed semantic visibility, semantic routing, replay payload governance, and fail-closed semantic exposure control.

AiGOL/SAPIANTA must support enterprise confidentiality, regulated-domain semantic governance, zero-trust semantic routing, and sovereign cognition architecture without requiring centralized ownership of sensitive payloads.

AiGOL governs semantic exposure without requiring unrestricted access to sensitive payloads.

This model defines:

- Semantic visibility governance: who may see which semantic representation under which authority scope.
- Payload governance: how payload classes constrain exposure, routing, replay, export, and approval.
- Cognition routing governance: whether cognition remains local, may use cloud providers, or must be blocked.
- Replay payload governance: how replay can preserve governance evidence without unrestricted raw payload storage.

This milestone is documentation and evidence only. It does not implement redaction, payload processing, local inference, authentication, API endpoints, runtime enforcement, replay mutation, provider behavior changes, or capability behavior changes.

## Payload Classification Model

Canonical payload classes:

### PUBLIC

- Semantic sensitivity: low.
- Export eligibility: generally eligible when organization policy allows.
- Replay eligibility: metadata, hashes, classifications, routing decisions, and content may be eligible when policy allows.
- Cloud eligibility: generally eligible when provider policy allows.
- Local-only requirements: not required by default.
- Approval requirements: usually low or none, unless organization policy requires review.

Examples: public product documentation, public release notes, public website text, published governance summaries.

### INTERNAL

- Semantic sensitivity: moderate.
- Export eligibility: limited to organization-approved scopes.
- Replay eligibility: metadata, hashes, classifications, routing decisions, and approved summaries.
- Cloud eligibility: allowed only if identity, organization policy, and exposure level permit it.
- Local-only requirements: may be required by organization overlay.
- Approval requirements: may require reviewer or approver authority for E4 or E5.

Examples: internal process notes, operational lineage summaries, non-sensitive source code architecture notes, internal roadmap fragments.

### CONFIDENTIAL

- Semantic sensitivity: high.
- Export eligibility: restricted.
- Replay eligibility: metadata, hashes, classifications, routing decisions, approvals, and redacted summaries only unless explicitly approved.
- Cloud eligibility: blocked unless explicit authority and organization policy allow.
- Local-only requirements: default local-only unless governance allows otherwise.
- Approval requirements: explicit approval required for E4, E5, cloud export, replay payload export, or cross-organization exposure.

Examples: strategic internal documents, private source code, sensitive governance artifacts, internal execution lineage, enterprise customer context.

### REGULATED

- Semantic sensitivity: very high.
- Export eligibility: restricted by regulatory and organization overlays.
- Replay eligibility: governance metadata, hashes, classifications, approval evidence, and redacted summaries.
- Cloud eligibility: blocked unless regulatory basis, organization policy, and approval authority explicitly permit it.
- Local-only requirements: default local-only.
- Approval requirements: high-risk approval required for broad exposure or export.

Examples: healthcare records, financial account records, regulated operational data, audit-sensitive personal data, compliance evidence.

### SECRET

- Semantic sensitivity: critical.
- Export eligibility: prohibited by default.
- Replay eligibility: metadata, hashes, classifications, and routing decisions only, with redacted or no payload content.
- Cloud eligibility: prohibited by default.
- Local-only requirements: required by default.
- Approval requirements: emergency override or explicit high authority required for any exposure beyond E1.

Examples: credentials, private keys, source code secrets, unreleased security findings, strategic governance override materials.

## Exposure Level Model

Exposure level is not execution authority.

### E0 = NO_PAYLOAD

- Allowed cognition scope: classification-free routing metadata only.
- Prohibited use cases: semantic interpretation, summarization, extraction, raw payload review.
- Replay restrictions: replay may contain no payload, only governance metadata and hashes.
- Local vs cloud eligibility: local or cloud routing may evaluate metadata only.
- Approval requirements: usually none, unless metadata itself is restricted.
- Organization policy dependencies: organization may require E0 for SECRET or regulated payload references.

### E1 = METADATA_ONLY

- Allowed cognition scope: file type, size, source boundary, owner scope, hashes, classification labels.
- Prohibited use cases: content interpretation, content summarization, entity extraction.
- Replay restrictions: metadata, hashes, classifications, routing decisions, and approval evidence only.
- Local vs cloud eligibility: cloud eligible only when metadata export is permitted.
- Approval requirements: low or none unless organization overlay restricts metadata.
- Organization policy dependencies: metadata fields may be partitioned by organization and replay scope.

### E2 = REDACTED_SUMMARY

- Allowed cognition scope: bounded summary with mandatory sensitive fields removed.
- Prohibited use cases: reconstructing raw payload, extracting hidden identifiers, inferring secrets.
- Replay restrictions: redacted summary and redaction class evidence only.
- Local vs cloud eligibility: cloud eligible only when classification, identity, and approval allow.
- Approval requirements: required for CONFIDENTIAL, REGULATED, or SECRET unless policy explicitly allows.
- Organization policy dependencies: redaction and retention policies apply.

### E3 = STRUCTURED_SEMANTIC_ABSTRACTION

- Allowed cognition scope: typed abstraction fields that preserve governance utility while limiting sensitive exposure.
- Prohibited use cases: raw payload reconstruction, secret extraction, personal identifier expansion.
- Replay restrictions: semantic abstraction, hashes, classifications, routing constraints, and approval evidence.
- Local vs cloud eligibility: cloud eligible only when abstraction is approved for export.
- Approval requirements: based on payload class and organization policy.
- Organization policy dependencies: abstraction schema and forbidden content classes are organization-governed.

### E4 = PARTIAL_REDACTED_CONTENT

- Allowed cognition scope: limited content visibility with mandatory redactions.
- Prohibited use cases: unrestricted raw payload analysis, credential review, unauthorized cross-organization sharing.
- Replay restrictions: payload fragments must be redacted, partitioned, and retention-bounded.
- Local vs cloud eligibility: cloud eligible only with explicit exposure approval and provider scope.
- Approval requirements: explicit approval required.
- Organization policy dependencies: high-risk overlays may force local-only or block.

### E5 = FULL_CONTENT

- Allowed cognition scope: full payload visibility for explicitly authorized humans or governed systems.
- Prohibited use cases: unapproved cloud export, unrestricted LLM visibility, replay export without authority.
- Replay restrictions: strict partitioning, retention controls, audit evidence, and export controls.
- Local vs cloud eligibility: local by default; cloud only with explicit high authority and policy approval.
- Approval requirements: explicit high authority required for CONFIDENTIAL, REGULATED, or SECRET payloads.
- Organization policy dependencies: organization may prohibit E5 cloud exposure entirely.

## Semantic Routing Model

Routing categories:

- `LOCAL_ONLY`: semantic processing must remain inside a governed local node or approved local boundary.
- `CLOUD_ALLOWED`: semantic processing may use approved cloud cognition providers under identity, policy, approval, and replay constraints.
- `HYBRID_ROUTING`: semantic abstraction or redacted summary may route to cloud while raw payload remains local.
- `GOVERNANCE_RESTRICTED`: semantic routing requires approval or must be blocked.
- `REPLAY_RESTRICTED`: replay may store only constrained metadata, hashes, classifications, and approval evidence.

Local semantic execution means cognition over payloads within an organization-controlled or user-controlled governed environment.

Cloud semantic execution means cognition over approved exposure levels through governed provider activation, without provider authority.

Hybrid cognition routing means local classification, redaction, or abstraction controls may produce approved semantic artifacts for cloud evaluation while raw payload remains sovereign.

Sovereign local cognition means the organization preserves payload custody and permits governance decisions without centralized raw payload ownership.

Fail-closed routing behavior:

```text
if payload classification unresolved
or organization scope unresolved
or exposure eligibility unresolved
or replay visibility unresolved
then BLOCK
```

## Semantic Abstraction Contract

Canonical semantic abstraction structure:

```json
{
  "document_type": "...",
  "payload_classification": "...",
  "semantic_topics": [],
  "sensitivity": "...",
  "organization_scope": "...",
  "replay_visibility": "...",
  "allowed_exposure": "...",
  "approval_requirements": [],
  "local_only_required": false,
  "forbidden_content": [],
  "routing_constraints": []
}
```

Semantic abstraction is not raw payload.

Semantic abstraction must preserve governance utility while limiting sensitive exposure. It must not contain credentials, regulated identifiers, source code secrets, or payload fragments prohibited by policy.

## Redaction Governance Model

Redaction governance defines what must be removed, transformed, blocked, retained locally, or excluded from replay. Redaction governance is not implementation.

Governance rules apply to:

- Personal identifiers.
- Financial identifiers.
- Credentials.
- Strategic governance information.
- Regulated operational data.
- Source code secrets.
- Internal execution lineage.
- Audit-sensitive information.

Mandatory redaction classes:

- personal identifiers;
- financial identifiers;
- credentials;
- regulated identifiers;
- source code secrets;
- audit-sensitive identifiers;
- cross-organization sensitive references.

Local-only classes:

- credentials;
- private keys;
- regulated raw records;
- SECRET payloads;
- high-risk internal execution lineage.

Prohibited export classes:

- credentials;
- source code secrets;
- unauthorized regulated payloads;
- raw SECRET payloads;
- unapproved cross-organization replay evidence.

Replay-redacted classes:

- personal identifiers;
- financial identifiers;
- credentials;
- internal execution lineage when policy requires redaction;
- audit-sensitive information outside auditor scope.

## Replay Payload Governance

Replay payload governance defines how replay remains useful without requiring unrestricted raw payload storage.

Replay may contain:

- governance metadata;
- hashes;
- classifications;
- routing decisions;
- approval evidence;
- exposure level decisions;
- redaction class evidence;
- lineage-safe references;
- retention and export decisions.

Replay does not require unrestricted raw payload storage.

Replay governance must support:

- replay metadata visibility;
- replay payload redaction;
- payload hashing;
- lineage-safe replay;
- organization replay partitioning;
- auditor visibility;
- replay retention restrictions;
- replay export restrictions.

Replay export requires explicit replay visibility and export authority. Replay visibility is not export authority.

## Exposure Approval Authority

Approval authority depends on authority profile, governance scope, organization scope, replay visibility scope, payload class, exposure level, and routing category.

Approval is required for:

- E4 exposure;
- E5 exposure;
- cloud export of CONFIDENTIAL, REGULATED, or SECRET payloads;
- replay payload export;
- cross-organization exposure;
- external semantic routing;
- high-risk exposure.

High-risk exposure requires explicit authority.

E4 and E5 exposure may be approved only by identities with matching approval authority, organization scope, replay visibility scope, and policy scope. Approval authority is not automatic approval and does not execute capabilities.

## Organization Policy Overlays

Organizations may define:

- payload restrictions;
- replay retention policies;
- local-only cognition requirements;
- cloud provider restrictions;
- semantic export restrictions;
- regulated-domain overlays;
- approval escalation requirements.

Organization overlays cannot bypass fail-closed governance. An overlay may restrict exposure, require approval, require local-only processing, or block export, but it cannot authorize unresolved identity, unresolved classification, unresolved exposure eligibility, or unresolved replay visibility.

## Semantic Boundary Guarantees

- Semantic visibility is not execution authority.
- Payload visibility is not mutation authority.
- Replay visibility is not export authority.
- Semantic routing is not capability execution.
- Semantic abstraction is not unrestricted payload access.
- LLM cannot elevate exposure level.
- Codex cannot elevate payload authority.
- Unresolved classification fails closed.
- Unresolved exposure eligibility fails closed.
- Unresolved organization scope fails closed.
- Unresolved replay visibility fails closed.
- Human governance authority remains explicit.
- Codex execution authority remains bounded and governed.

## Dependency Declaration

Upstream dependency:

- `GOVERNED_IDENTITY_AND_AUTHORITY_MODEL_V1`

Semantic Exposure Model requires:

- runtime identity;
- authority scopes;
- replay visibility governance;
- approval hierarchy;
- capability entitlement substrate.

Downstream dependencies:

- `CAPABILITY_GOVERNANCE_MATRIX_V1`
- `LOCAL_NODE_ARCHITECTURE_V1`
- `SOVEREIGN_REPLAY_ARCHITECTURE_V1`

Future downstream milestones must preserve payload sovereignty, semantic exposure partitioning, fail-closed semantic resolution, LLM non-authority, and human governance boundaries.
