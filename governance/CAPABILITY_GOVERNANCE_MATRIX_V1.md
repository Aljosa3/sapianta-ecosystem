# CAPABILITY_GOVERNANCE_MATRIX_V1

## Purpose

The Capability Governance Matrix v1 defines constitutional governance for runtime capability eligibility, authority-scoped capability access, payload-aware restrictions, semantic-exposure-aware routing, approval-aware capability execution, replay-aware visibility, and local versus cloud capability constraints.

Runtime capability governance determines which capability may be eligible, against which payload class, under which exposure level, in which routing scope, with which approval requirements, and with which replay visibility constraints before execution eligibility is granted.

Capability eligibility is not capability execution authority.

This milestone is documentation and evidence only. It does not implement a policy engine, capability execution, provider orchestration, routing execution, local runtime execution, API endpoints, replay changes, or runtime enforcement.

## Capability Classes

Canonical capability categories:

### ANALYSIS

- Risk profile: low to moderate.
- Local/cloud eligibility: local, cloud, or hybrid depending on payload class and exposure level.
- Replay implications: metadata, classification, summary, and decision evidence may be replay-visible.
- Approval requirements: required for high exposure over confidential or regulated payloads.
- Payload restrictions: SECRET and REGULATED payloads default local-only or blocked.
- Authority requirements: `CAN_REQUEST_ANALYSIS` or stronger.

### SUMMARIZATION

- Risk profile: moderate because summaries may expose sensitive content.
- Local/cloud eligibility: cloud only for approved exposure levels.
- Replay implications: redacted or abstracted summaries may be retained; raw sensitive summaries may be restricted.
- Approval requirements: required for E4/E5 over non-public payloads.
- Payload restrictions: CONFIDENTIAL, REGULATED, and SECRET require exposure approval.
- Authority requirements: `CAN_REQUEST_ANALYSIS` with exposure authority where needed.

### CLASSIFICATION

- Risk profile: low to moderate.
- Local/cloud eligibility: local by default for sensitive payloads; cloud allowed for metadata or approved abstractions.
- Replay implications: classification labels and hashes should be replay-visible.
- Approval requirements: usually low unless classification requires payload exposure above E2.
- Payload restrictions: SECRET classification should avoid raw export.
- Authority requirements: `READ_ONLY` or `CAN_REQUEST_ANALYSIS` depending on scope.

### CODE_GENERATION

- Risk profile: moderate to high.
- Local/cloud eligibility: cloud eligible only when payload and provider policy allow.
- Replay implications: generated code, prompt classifications, and approval evidence may require retention.
- Approval requirements: required when based on confidential code, regulated systems, or deployment targets.
- Payload restrictions: source code secrets and proprietary repositories require local-only or redacted exposure.
- Authority requirements: `CAN_REQUEST_ANALYSIS` plus relevant capability entitlement.

### CODE_EXECUTION

- Risk profile: high.
- Local/cloud eligibility: local sandbox only unless explicitly governed.
- Replay implications: execution metadata, sandbox result, and lineage evidence must be replay-visible.
- Approval requirements: explicit approval required.
- Payload restrictions: REGULATED or SECRET plus cloud-routed execution is blocked by default.
- Authority requirements: `CAN_EXECUTE_MUTATION` or equivalent explicit execution authority.

### FILESYSTEM_READ

- Risk profile: moderate to high.
- Local/cloud eligibility: local-only by default.
- Replay implications: file metadata, hashes, and access decisions should be replay-visible; content replay may be redacted.
- Approval requirements: required for sensitive paths or non-user-owned scopes.
- Payload restrictions: credentials, secrets, and regulated files require strict local-only controls.
- Authority requirements: explicit filesystem scope and entitlement.

### FILESYSTEM_WRITE

- Risk profile: high.
- Local/cloud eligibility: local governed sandbox only.
- Replay implications: mutation intent, target path, approval, and result evidence must be replay-visible.
- Approval requirements: explicit approval required.
- Payload restrictions: blocked for unresolved or sensitive scopes.
- Authority requirements: `CAN_EXECUTE_MUTATION`.

### EXTERNAL_API

- Risk profile: high.
- Local/cloud eligibility: governed routing only.
- Replay implications: request metadata, endpoint class, approval, and response classification must be replay-visible.
- Approval requirements: explicit approval required.
- Payload restrictions: regulated, confidential, or secret data export requires high-risk authority.
- Authority requirements: explicit external API scope.

### PROVIDER_ROUTING

- Risk profile: moderate to high.
- Local/cloud eligibility: depends on payload class and exposure level.
- Replay implications: provider selection, routing category, exposure level, and approval evidence must be replay-visible.
- Approval requirements: required for cloud routing over sensitive payloads.
- Payload restrictions: SECRET and REGULATED default local-only or blocked.
- Authority requirements: `CAN_REGISTER_PROVIDER` for provider registration; routing eligibility for provider use.

### REPLAY_EXPORT

- Risk profile: high.
- Local/cloud eligibility: export path must be governed.
- Replay implications: export scope, redactions, recipient class, and approval evidence must be retained.
- Approval requirements: explicit export approval required.
- Payload restrictions: raw sensitive replay export blocked unless explicitly authorized.
- Authority requirements: `CAN_EXPORT_AUDIT_EVIDENCE` and matching replay visibility.

### POLICY_MUTATION

- Risk profile: critical.
- Local/cloud eligibility: governance-controlled only.
- Replay implications: policy change intent, authority, approval, and resulting scope must be replay-visible.
- Approval requirements: explicit governance admin approval required.
- Payload restrictions: not payload-driven but may affect payload exposure and capability scope.
- Authority requirements: `CAN_CREATE_POLICY`.

### DEPLOYMENT

- Risk profile: critical.
- Local/cloud eligibility: governed release boundary only.
- Replay implications: deployment intent, approval, artifact lineage, and target environment evidence must be replay-visible.
- Approval requirements: explicit high-risk approval required.
- Payload restrictions: deployment involving regulated or secret payloads requires additional controls.
- Authority requirements: explicit deployment authority.

### GOVERNANCE_ADMINISTRATION

- Risk profile: critical.
- Local/cloud eligibility: governance-controlled only.
- Replay implications: administrative actions must be replay-visible.
- Approval requirements: high-risk governance approval required.
- Payload restrictions: may impact all payload classes.
- Authority requirements: governance admin authority.

### AUDIT_EXPORT

- Risk profile: high.
- Local/cloud eligibility: export path must be authorized.
- Replay implications: exported evidence, redaction classes, recipient, and approval must be recorded.
- Approval requirements: auditor or governance admin approval required.
- Payload restrictions: raw confidential, regulated, or secret payload export requires explicit authority.
- Authority requirements: `CAN_EXPORT_AUDIT_EVIDENCE`.

### LOCAL_ONLY_EXECUTION

- Risk profile: varies by capability.
- Local/cloud eligibility: local only.
- Replay implications: local dispatch, sandbox, policy, and result metadata remain replay-visible.
- Approval requirements: depends on capability and payload class.
- Payload restrictions: used for sensitive payloads requiring sovereignty.
- Authority requirements: local execution scope.

### CLOUD_ROUTED_EXECUTION

- Risk profile: moderate to critical.
- Local/cloud eligibility: cloud only after classification, exposure, provider, approval, and replay constraints are resolved.
- Replay implications: provider, exposure level, routing decision, and approval evidence must be replay-visible.
- Approval requirements: required for sensitive payload classes.
- Payload restrictions: REGULATED and SECRET blocked by default unless explicit policy allows.
- Authority requirements: provider scope and exposure approval.

## Capability Eligibility Model

Capability eligibility dimensions:

- Identity scope.
- Authority scope.
- Organization scope.
- Payload classification.
- Exposure level.
- Replay visibility.
- Execution scope.
- Routing constraints.
- Approval requirements.

Capability eligibility must be resolved before execution eligibility.

Eligibility is the governance determination that a capability may proceed to later execution checks. It does not execute the capability, activate a provider, mutate files, export replay, or approve itself.

## Payload-Aware Capability Governance

Payload visibility does not imply capability execution authority.

### PUBLIC

- Allowed capabilities: analysis, summarization, classification, code generation, cloud-routed analysis when policy allows.
- Restricted capabilities: filesystem write, deployment, policy mutation.
- Approval-gated capabilities: replay export, deployment, provider registration.
- Prohibited capabilities: unrestricted mutation or ungoverned external API export.
- Local-only capabilities: not required by default.
- Replay restrictions: standard replay metadata and content may be eligible under policy.

### INTERNAL

- Allowed capabilities: analysis, classification, local summarization, governed cloud routing for approved exposure.
- Restricted capabilities: external API, deployment, filesystem write, replay export.
- Approval-gated capabilities: E4/E5 summarization, cloud routing, audit export.
- Prohibited capabilities: unapproved cross-organization export.
- Local-only capabilities: organization-designated internal material.
- Replay restrictions: replay partitioned by organization and role.

### CONFIDENTIAL

- Allowed capabilities: local analysis, local classification, E2/E3 abstraction.
- Restricted capabilities: cloud routing, code generation using raw content, replay export.
- Approval-gated capabilities: E4/E5 exposure, cloud semantic routing, audit export.
- Prohibited capabilities: unapproved external API transfer, unapproved filesystem mutation.
- Local-only capabilities: default for raw payload.
- Replay restrictions: metadata, hashes, classifications, redacted summaries, and approval evidence.

### REGULATED

- Allowed capabilities: local classification, local analysis, governed abstraction where policy permits.
- Restricted capabilities: summarization, provider routing, replay export.
- Approval-gated capabilities: regulated-domain overlays, E4/E5 exposure, audit export.
- Prohibited capabilities: `CODE_EXECUTION + CLOUD_ROUTED_EXECUTION`, unapproved external API, raw cloud transfer.
- Local-only capabilities: default for raw payload and high exposure.
- Replay restrictions: metadata, hashes, classifications, and redacted audit evidence.

### SECRET

- Allowed capabilities: metadata-only classification, local-only governance review.
- Restricted capabilities: local analysis only under explicit authority.
- Approval-gated capabilities: any exposure above E1.
- Prohibited capabilities: cloud routing by default, replay payload export, external API export, filesystem mutation without explicit authority.
- Local-only capabilities: required by default.
- Replay restrictions: metadata, hashes, classification, and routing decisions only.

Example decisions:

```text
CODE_EXECUTION + REGULATED + CLOUD_ROUTED_EXECUTION -> BLOCKED
ANALYSIS + CONFIDENTIAL + E3 + LOCAL_ONLY -> ALLOWED
REPLAY_EXPORT + SECRET + E5 -> BLOCKED unless explicit emergency authority exists
SUMMARIZATION + INTERNAL + E2 + CLOUD_ALLOWED -> APPROVAL_REQUIRED when organization policy requires it
```

## Exposure-Aware Capability Governance

### E0

- Capability limitations: metadata routing only.
- Replay restrictions: no payload, only metadata and hashes.
- Export restrictions: metadata export only when policy permits.
- Approval escalation requirements: minimal unless metadata is restricted.
- Cloud eligibility: metadata-only.
- Local-only requirements: required if organization blocks metadata export.

### E1

- Capability limitations: metadata inspection and classification.
- Replay restrictions: metadata, hashes, classifications.
- Export restrictions: scoped metadata export only.
- Approval escalation requirements: low unless sensitive metadata.
- Cloud eligibility: allowed by policy.
- Local-only requirements: required for SECRET or restricted organizations.

### E2

- Capability limitations: redacted summaries, no raw reconstruction.
- Replay restrictions: redacted summaries and redaction evidence.
- Export restrictions: restricted for CONFIDENTIAL, REGULATED, SECRET.
- Approval escalation requirements: required for sensitive classes.
- Cloud eligibility: allowed only after identity, exposure, and organization checks.
- Local-only requirements: default for SECRET.

### E3

- Capability limitations: structured abstraction only.
- Replay restrictions: abstraction, classifications, routing constraints.
- Export restrictions: organization-controlled.
- Approval escalation requirements: required for regulated or confidential cloud use.
- Cloud eligibility: possible when abstraction excludes forbidden content.
- Local-only requirements: required when abstraction cannot be safely exported.

### E4

- Capability limitations: partial redacted content only.
- Replay restrictions: partitioned, redacted, retention-bounded replay.
- Export restrictions: explicit export approval required.
- Approval escalation requirements: explicit high-risk approval.
- Cloud eligibility: explicit approval and provider scope required.
- Local-only requirements: default for REGULATED and SECRET.

### E5

- Capability limitations: full content only for explicitly authorized scope.
- Replay restrictions: strict retention, partitioning, redaction, and audit controls.
- Export restrictions: high-risk approval required.
- Approval escalation requirements: explicit high authority.
- Cloud eligibility: blocked by default for CONFIDENTIAL, REGULATED, SECRET.
- Local-only requirements: default for sensitive classes.

High exposure capability execution requires explicit authority.

## Routing Governance Model

Routing scopes:

- `LOCAL_ONLY`
- `CLOUD_ALLOWED`
- `HYBRID`
- `GOVERNANCE_RESTRICTED`
- `REPLAY_RESTRICTED`

Eligible capability classes by routing scope:

- `LOCAL_ONLY`: analysis, classification, local-only execution, filesystem read, sandboxed code execution when explicitly approved.
- `CLOUD_ALLOWED`: analysis, summarization, classification, code generation, provider routing for approved payload and exposure levels.
- `HYBRID`: local classification, redaction, abstraction, and cloud use of approved semantic abstractions.
- `GOVERNANCE_RESTRICTED`: filesystem write, external API, deployment, policy mutation, governance administration, replay export.
- `REPLAY_RESTRICTED`: audit export, replay export, regulated payload analysis, secret metadata handling.

Routing eligibility is resolved before provider execution.

Fail-closed routing behavior:

```text
if routing scope unresolved
or payload class unresolved
or authority unresolved
or exposure level unresolved
then BLOCK
```

## Approval-Aware Capability Governance

Approval dependencies apply to:

- high-risk capability execution;
- filesystem mutation;
- external API access;
- replay export;
- deployment;
- provider registration;
- policy mutation;
- cross-organization routing;
- cloud execution over regulated payloads.

Approval hierarchy depends on authority profile, governance scope, organization scope, replay visibility, risk class, payload classification, exposure level, and routing scope.

Approval eligibility is not automatic execution approval. Approval authority must be explicit and replay-visible.

## Replay-Aware Capability Governance

Capability execution affects:

- replay visibility;
- replay retention;
- replay export eligibility;
- replay redaction;
- lineage visibility;
- audit evidence visibility.

Some capabilities may produce:

- metadata-only replay;
- redacted replay;
- local-only replay.

Replay visibility is not replay export authority.

Replay export requires explicit authority, scope, redaction policy, retention policy, and approval evidence.

## Local vs Cloud Execution Governance

Cloud-eligible capability classes may include analysis, classification, summarization, code generation, and provider routing when payload class, exposure level, provider policy, and approval scope allow.

Local-only capability classes include local-only execution, sensitive filesystem read, filesystem write, code execution over sensitive data, and any capability involving SECRET or regulated raw payloads by default.

Hybrid-routable capability classes include classification, semantic abstraction, summarization of approved abstractions, and redacted analysis.

Organization-restricted capability classes include deployment, policy mutation, governance administration, provider registration, and external API.

Replay-restricted capability classes include replay export, audit export, regulated evidence analysis, and secret payload handling.

Regulated payloads may require local-only execution.

Local execution governance is determined before provider routing.

## Organization Policy Overlays

Organizations may restrict:

- capability classes;
- routing scopes;
- replay visibility;
- exposure eligibility;
- provider eligibility;
- deployment authority;
- filesystem authority;
- external API access.

Organization overlays cannot bypass fail-closed governance. They may only restrict, require approval, force local-only operation, or block.

## Capability Boundary Guarantees

- Capability eligibility is not execution authority.
- Payload visibility is not filesystem authority.
- Semantic routing is not provider execution.
- Replay visibility is not replay export authority.
- Approval eligibility is not approval execution.
- LLM cannot elevate capability authority.
- Codex cannot elevate capability authority.
- Unresolved capability eligibility fails closed.
- Unresolved routing eligibility fails closed.
- Unresolved identity, authority, payload class, exposure level, or replay visibility fails closed.

## Dependency Declaration

Upstream dependencies:

- `GOVERNED_IDENTITY_AND_AUTHORITY_MODEL_V1`
- `SEMANTIC_EXPOSURE_MODEL_V1`

Capability Governance Matrix requires:

- runtime identity;
- authority scopes;
- semantic exposure governance;
- replay visibility governance;
- approval hierarchy.

Downstream dependencies:

- `LOCAL_NODE_ARCHITECTURE_V1`
- `SOVEREIGN_REPLAY_ARCHITECTURE_V1`
- `PROVIDER_FEDERATION_GOVERNANCE_V1` future
- `EXECUTION_POLICY_ENGINE_V1` future

Future downstream milestones must preserve capability eligibility as separate from execution authority.
