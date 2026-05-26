# LOCAL_NODE_ARCHITECTURE_V1

## Purpose

The Local Node Architecture v1 defines constitutional governance for sovereign local execution, payload sovereignty, privacy-preserving cognition, local semantic processing, regulated execution boundaries, enterprise local runtime governance, local replay sovereignty, and local/cloud execution separation.

The Local Node Architecture enables governed execution without centralized payload ownership.

Sensitive execution may occur locally, inside organization boundaries, or inside sovereign runtime environments while governance remains replay-safe, fail-closed, observable, authority-scoped, and capability-governed.

This milestone is documentation and evidence only. It does not implement a local runtime, local model execution, provider federation, confidential computing, encrypted storage, execution engine behavior, replay persistence changes, API endpoints, or runtime enforcement.

## Local Node Definition

A Local Node is a governed runtime boundary controlled by a user, organization, or sovereign environment where payloads, semantic processing, capability execution, memory, replay, policy cache, and approval evidence may remain local under explicit governance.

Canonical local node boundaries:

- Local runtime boundary: the local execution surface in which governed work may occur.
- Organization-owned execution boundary: organization-controlled compute, storage, approval, and replay environment.
- Sovereign execution environment: a runtime area where sensitive payloads can be processed without centralized payload transfer.
- Local governance scope: the identity, authority, organization, payload, and capability scope applied locally.
- Local replay boundary: partition where replay artifacts can remain local, redacted, hashed, or metadata-only externally.
- Local semantic processing boundary: local summarization, classification, abstraction, filtering, or redaction preparation without raw payload export.

The local node may execute governed capabilities locally without exporting raw payload externally.

The local node is not a trusted bypass, unrestricted execution environment, or governance escape hatch. It remains governed, replay-aware, fail-closed, capability-scoped, and authority-constrained.

## Local Execution Domains

### LOCAL_SEMANTIC_PROCESSING

- Payload sensitivity expectations: CONFIDENTIAL, REGULATED, and SECRET payloads may require local semantic processing.
- Replay implications: metadata, hashes, classification, abstraction evidence, and approval decisions may be replay-visible; raw semantic outputs may remain local.
- Authority requirements: semantic exposure and capability authority must be resolved.
- Export restrictions: raw payload and sensitive semantic outputs may be blocked.
- Local-only constraints: required when exposure or routing policy disallows cloud cognition.

### LOCAL_CAPABILITY_EXECUTION

- Payload sensitivity expectations: high-risk payloads and mutation-capable operations default to local governance.
- Replay implications: capability eligibility, routing decisions, sandbox evidence, approval, and results must be replay-visible.
- Authority requirements: capability entitlement, approval, and execution scope.
- Export restrictions: capability outputs may be metadata-only or redacted outside the node.
- Local-only constraints: required for regulated or secret raw payload operations by default.

### LOCAL_MEMORY_STORAGE

- Payload sensitivity expectations: memory may include governed semantic continuity, local summaries, or operational checkpoints.
- Replay implications: memory hashes, retention policy, and lineage references may be visible while contents remain local.
- Authority requirements: memory visibility and retention authority.
- Export restrictions: local memory contents require explicit authority to export.
- Local-only constraints: required for SECRET and organization-restricted memory.

### LOCAL_REPLAY_STORAGE

- Payload sensitivity expectations: replay may reference sensitive execution, approvals, lineage, and classifications.
- Replay implications: local replay partitioning and export policy must be explicit.
- Authority requirements: replay visibility, audit authority, and export authority.
- Export restrictions: raw replay payload may be blocked; metadata-only export may be allowed.
- Local-only constraints: required for local-only payload and secret replay artifacts.

### LOCAL_PROVIDER_EXECUTION

- Payload sensitivity expectations: provider execution may occur locally when cloud providers are blocked.
- Replay implications: provider identity, invocation metadata, approval evidence, and response classification must be replay-visible.
- Authority requirements: provider scope and capability eligibility.
- Export restrictions: provider outputs may be local-only.
- Local-only constraints: required when provider routing is local-only.

### LOCAL_POLICY_ENFORCEMENT

- Payload sensitivity expectations: policy decisions may depend on local payload classification and organization overlays.
- Replay implications: policy inputs, decisions, and denials should be replay-visible.
- Authority requirements: policy authority and governance scope.
- Export restrictions: policy evidence may be metadata-only outside the node.
- Local-only constraints: required where policies reference sensitive local-only data.

### LOCAL_GOVERNANCE_CACHE

- Payload sensitivity expectations: cache may include local policy, identity, authority, and routing references.
- Replay implications: cache version, hashes, and lineage may be replay-visible.
- Authority requirements: governance admin or local node authority.
- Export restrictions: cache contents may be restricted to local node.
- Local-only constraints: required for organization-private governance configuration.

### LOCAL_APPROVAL_STORAGE

- Payload sensitivity expectations: approvals may contain sensitive rationale, payload references, or audit evidence.
- Replay implications: approval state, scope, hash, and lineage should be replay-visible.
- Authority requirements: approval authority and replay visibility.
- Export restrictions: approval rationale may be redacted outside local scope.
- Local-only constraints: required for regulated or secret approval evidence.

## Local vs Cloud Execution Model

Execution separation categories:

- `LOCAL_ONLY`: payload, cognition, capability execution, or replay remains inside local node boundaries.
- `HYBRID`: local node performs classification, redaction preparation, abstraction, or filtering, while approved metadata or abstractions may route externally.
- `CLOUD_ALLOWED`: cloud cognition or provider use may occur after identity, authority, payload, exposure, routing, approval, and replay checks.
- `GOVERNANCE_RESTRICTED`: execution is blocked or approval-gated until governance requirements are resolved.

Payload classes may require:

- local-only execution for SECRET and raw REGULATED payloads;
- hybrid routing for CONFIDENTIAL or REGULATED abstractions;
- metadata-only cloud routing for high-sensitivity payloads;
- replay-restricted execution for audit-sensitive or local-only evidence.

Routing eligibility must be resolved before provider execution.

## Local Semantic Processing Model

Semantic processing may remain local through:

- local summarization;
- local classification;
- local abstraction generation;
- local embedding generation;
- local semantic filtering;
- local payload redaction preparation.

Local semantic processing is not unrestricted execution authority.

Local semantic processing must remain governed by identity, authority, payload classification, exposure level, capability eligibility, organization overlays, replay visibility, and approval requirements.

## Local Memory Governance

Local memory categories:

- `LOCAL_SEMANTIC_MEMORY`
- `LOCAL_RUNTIME_MEMORY`
- `LOCAL_REPLAY_MEMORY`
- `LOCAL_POLICY_MEMORY`
- `LOCAL_GOVERNANCE_MEMORY`

Local memory governance must define:

- visibility restrictions;
- export restrictions;
- replay implications;
- organization scope restrictions;
- retention constraints.

Local memory does not imply unrestricted replay export.

Local memory export requires explicit authority, retention eligibility, replay visibility, and organization policy approval.

## Local Replay Governance

Local replay governance includes:

- local replay partitioning;
- replay visibility separation;
- metadata-only replay export;
- local-only replay artifacts;
- replay hashing;
- replay lineage synchronization;
- replay export restrictions.

Some replay artifacts may never leave the local node.

Replay synchronization is not raw payload synchronization.

Replay synchronization may export hashes, lineage references, classifications, routing decisions, approval evidence, and metadata while raw payloads, local memory contents, and secret replay artifacts remain local.

## Local Capability Execution

Capability classes may execute:

- locally only: filesystem write, code execution over sensitive data, local-only execution, secret payload analysis, regulated raw payload operations;
- hybrid: analysis, classification, summarization, semantic abstraction, redaction preparation;
- cloud eligible: public or approved internal analysis, approved semantic abstraction, approved summarization;
- organization restricted: deployment, policy mutation, provider registration, governance administration, external API access.

Examples:

```text
REGULATED + FILESYSTEM_WRITE -> LOCAL_ONLY
SECRET + CODE_EXECUTION -> LOCAL_ONLY + APPROVAL_REQUIRED
CONFIDENTIAL + ANALYSIS -> HYBRID_ELIGIBLE
```

Capability eligibility remains governed locally. Local eligibility does not bypass identity, authority, approval, policy, replay, or organization scope.

## Governance Metadata Export Model

Governance artifacts that may leave the local node when policy permits:

- hashes;
- classifications;
- routing decisions;
- replay metadata;
- approval evidence;
- execution lineage metadata.

Restricted examples:

- raw payload;
- local memory contents;
- secret replay artifacts;
- local-only semantic outputs.

Governance metadata export is not payload export.

Metadata export must remain scoped, replay-visible, and fail-closed when authority, replay visibility, organization scope, or payload classification cannot be resolved.

## Organization Sovereignty Model

Organizations may require:

- local-only cognition;
- local replay retention;
- local provider restrictions;
- local execution enforcement;
- sovereign replay governance;
- cloud prohibition;
- export approval escalation.

Organization overlays cannot bypass fail-closed governance. They may restrict, block, force local-only behavior, require approval, or reduce exposure, but cannot grant unresolved authority.

## Fail-Closed Local Governance

If unresolved:

- payload classification;
- routing eligibility;
- replay eligibility;
- authority scope;
- capability eligibility;
- organization scope;

then block.

The local node may deny execution even if cloud execution would otherwise be possible.

Local denial is valid governance behavior and must be replay-visible where replay scope permits.

## Local Node Boundary Guarantees

- Local execution is not unrestricted execution authority.
- Local payload visibility is not export authority.
- Local replay visibility is not replay export authority.
- Local semantic processing is not provider execution authority.
- Local routing eligibility is not execution authorization.
- LLM cannot elevate local authority.
- Codex cannot elevate local authority.
- Unresolved local governance fails closed.
- Human governance authority remains explicit.
- Codex execution authority remains bounded and governed.

## Dependency Declaration

Upstream dependencies:

- `GOVERNED_IDENTITY_AND_AUTHORITY_MODEL_V1`
- `SEMANTIC_EXPOSURE_MODEL_V1`
- `CAPABILITY_GOVERNANCE_MATRIX_V1`

Local Node Architecture requires:

- runtime identity;
- semantic exposure governance;
- capability governance;
- replay visibility governance;
- approval hierarchy;
- routing governance.

Downstream dependencies:

- `SOVEREIGN_REPLAY_ARCHITECTURE_V1`
- `PROVIDER_FEDERATION_GOVERNANCE_V1`
- `EXECUTION_POLICY_ENGINE_V1`
- `CONFIDENTIAL_EXECUTION_GOVERNANCE_V1` future

Future downstream milestones must preserve local governance as separate from execution authority and local custody as separate from unrestricted payload export.
