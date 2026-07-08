# G16-05 - PCCL Provider Integration Audit

Status: CERTIFIED

Date: 2026-07-08

Milestone: G16-05

Scope: Architectural audit of how PCCL should integrate with the existing Platform Core Provider subsystem. This milestone is audit-only. It does not implement Provider Runtime, Provider Selection, Provider Registry, Provider Orchestration, Prompt Generation, Proposal Pipeline, Cognitive Loop, provider invocation, worker execution, replay mutation, governance execution, or AiCLI behavior.

## Knowledge Reuse Audit

G16-05 reviewed existing provider-related Platform Core capabilities before any provider capability was added to PCCL.

Reviewed implementation surfaces:

- `aigol/provider/provider_registry.py`
- `aigol/provider/certified_provider_attachment.py`
- `aigol/provider/provider_runtime.py`
- `aigol/provider/provider_adapter.py`
- `aigol/provider/provider_proposal_envelope.py`
- `aigol/runtime/provider_necessity_policy_runtime.py`
- `aigol/runtime/unified_resource_selection_runtime.py`
- `aigol/runtime/conversation_ppp_resource_selection_routing.py`
- `aigol/runtime/provider_proposal_production_runtime.py`
- `aigol/runtime/provider_proposal_repair_and_retry_runtime.py`
- `aigol/runtime/provider_identity_boundaries.py`
- `aigol/runtime/provider_attachment.py`

Reviewed governance evidence:

- `docs/governance/G14_43_PROVIDER_PLATFORM_OPERATIONAL_COMPLETION_V1.md`
- `docs/governance/G14_44_CERTIFIED_PROVIDER_ATTACHMENT_V1.md`
- `docs/governance/G14_20_PROVIDER_PLATFORM_CANONICAL_RUNTIME_AUDIT_V1.md`
- `docs/governance/AIGOL_PROVIDER_CONTRACT_MIGRATION_AUDIT_V1.md`
- `docs/governance/AIGOL_FIRST_REAL_PROVIDER_RUNTIME_V1.md`
- `docs/governance/AIGOL_PROVIDER_CREDENTIAL_VAULT_V1.md`
- `docs/governance/AIGOL_PROVIDER_CREDENTIAL_GOVERNANCE_REVIEW_V1.md`
- `docs/governance/G16_03_CANONICAL_CONTEXT_ENVELOPE.md`
- `docs/governance/G16_04_CANONICAL_POLICY_ENVELOPE.md`

Existing provider-related capabilities identified:

- metadata-only Provider Registry;
- certified provider attachment boundary;
- provider attachment runtime;
- provider adapter contract;
- provider proposal envelope validation;
- provider readiness and diagnostics;
- provider replay reconstruction;
- provider necessity policy classification;
- unified resource selection;
- provider proposal production;
- provider repair and retry;
- provider identity and credential boundaries;
- canonical provider contract migration audit;
- legacy provider attachment replay compatibility.

## Architecture Review

Canonical ownership boundaries are already defined:

- PCCL owns cognition orchestration state, session lifecycle, context envelope references, and policy envelope references.
- Provider Platform owns provider registry lookup, readiness, adapter validation, transport invocation, diagnostics, fail-closed provider capture, and provider replay evidence.
- Certified Provider Attachment owns the stable production-facing provider access boundary.
- Governance owns policy and authorization decisions.
- Replay owns replay reconstruction and certification.
- Worker Platform owns execution.
- Human Interfaces remain thin adapters.

PCCL must not become a second Provider Platform.

PCCL must not:

- own provider registry metadata;
- select providers independently;
- invoke provider transport directly;
- validate provider adapters independently;
- manage credentials;
- authorize provider invocation;
- evaluate provider policy;
- normalize raw provider responses outside the certified boundary;
- certify provider replay evidence;
- execute workers.

Generation 14 ownership boundaries remain unchanged.

## Existing Capability Discovery

### Provider Registry

Existing implementation:

- `aigol.provider.provider_registry.ProviderRegistry`
- `aigol.provider.provider_registry.ProviderMetadata`

Capabilities:

- deterministic provider metadata registration;
- provider lookup by identifier;
- metadata hashing;
- explicit `execution_capable = False`;
- explicit `dispatch_capable = False`;
- explicit `authority = False`.

PCCL decision:

- Reuse existing Provider Registry.
- Do not create a PCCL provider registry.

### Provider Selection

Existing implementations:

- `aigol.runtime.provider_necessity_policy_runtime.classify_provider_necessity(...)`
- `aigol.runtime.unified_resource_selection_runtime.select_unified_resource(...)`
- `aigol.runtime.conversation_ppp_resource_selection_routing.run_conversation_ppp_resource_selection_routing(...)`

Capabilities:

- deterministic provider necessity classification;
- deterministic resource selection;
- provider role selection without invocation;
- authority profiles that keep providers proposal-only;
- replay-visible selection evidence.

PCCL decision:

- Reuse existing provider necessity and resource selection services.
- PCCL may carry provider selection references in future artifacts, but must not become selection authority.

### Capability Resolution

Existing implementations:

- unified resource selection capability matching;
- provider identity boundary capability declarations;
- provider contract migration audit mapping existing cognition-provider dialects to canonical provider contracts.

Capabilities:

- provider capability declarations;
- role-scoped capability matching;
- proposal-only authority profiles;
- canonical provider contract migration path.

PCCL decision:

- Reuse capability resolution metadata and canonical provider contract adapters.
- Do not create PCCL-specific capability semantics.

### Provider Orchestration

Existing implementations:

- `aigol.runtime.conversation_ppp_resource_selection_routing`
- `aigol.runtime.provider_proposal_production_runtime`
- `aigol.runtime.provider_proposal_repair_and_retry_runtime`

Capabilities:

- provider necessity check before provider proposal production;
- request packet preparation;
- bounded repair and retry;
- high-risk human approval escalation;
- proposal contract validation;
- replay-visible orchestration evidence.

PCCL decision:

- Reuse existing orchestration once PCCL has a certified integration artifact.
- Do not add PCCL provider orchestration.

### Provider Invocation

Existing implementations:

- `aigol.provider.certified_provider_attachment.run_certified_provider_attachment(...)`
- `aigol.provider.provider_runtime.run_provider_attachment(...)`

Certified governance evidence:

- `G14_44_CERTIFIED_PROVIDER_ATTACHMENT_V1`
- `G14_43_PROVIDER_PLATFORM_OPERATIONAL_COMPLETION_V1`

Capabilities:

- certified production-facing provider access boundary;
- Provider Platform registry lookup;
- provider readiness;
- adapter validation;
- request validation;
- adapter invocation;
- transport diagnostics;
- fail-closed capture;
- replay evidence;
- certified attachment artifact persistence.

PCCL decision:

- Reuse Certified Provider Attachment exclusively.
- PCCL must never call provider transport directly.
- PCCL must not implement a new Provider Runtime.

### Provider Attachment

Existing implementations:

- production: `aigol.provider.certified_provider_attachment`
- internal provider platform engine: `aigol.provider.provider_runtime`
- legacy compatibility: `aigol.runtime.provider_attachment`

Capabilities:

- production-safe certified provider attachment;
- fail-closed provider capture;
- historical replay reconstruction for legacy attachment evidence.

PCCL decision:

- Use only Certified Provider Attachment for future production invocation.
- Treat `aigol.runtime.provider_attachment` as legacy replay compatibility and out of scope for new PCCL work.

### Provider Contracts

Existing implementations and evidence:

- `aigol.provider.provider_adapter.ProviderAdapter`
- `aigol.provider.provider_proposal_envelope.ProviderProposalEnvelope`
- `AIGOL_PROVIDER_CONTRACT_MIGRATION_AUDIT_V1`
- `AIGOL_FIRST_REAL_PROVIDER_RUNTIME_V1`

Capabilities:

- minimal adapter contract;
- deterministic provider proposal envelope;
- forbidden authority-bearing fields;
- replay-visible proposal output;
- canonical provider contract migration path.

PCCL decision:

- Reuse existing provider contracts and canonical contract adapters.
- Future PCCL provider integration should add only a deterministic mapping from PCCL envelopes to canonical provider input references.

## Gap Analysis

### Capabilities Already Reusable By PCCL

PCCL can already reuse:

- Provider Registry.
- Provider Metadata.
- Provider Necessity Policy.
- Unified Resource Selection.
- Provider Identity and Credential Boundary artifacts.
- ProviderAdapter contract.
- ProviderProposalEnvelope validation.
- Certified Provider Attachment.
- Provider Platform runtime.
- Provider Proposal Production.
- Provider Repair and Retry.
- Provider replay reconstruction.
- Canonical provider contract migration strategy.

### Capabilities Requiring Only Integration

PCCL requires integration with:

- Canonical Context Envelope;
- Canonical Policy Envelope;
- provider necessity policy;
- resource selection;
- provider contract adapter;
- certified provider attachment;
- provider replay evidence;
- capability certification registry.

These require deterministic handoff and reference binding, not new provider runtime behavior.

### Capabilities Requiring Genuinely New Deterministic Implementation

No new provider runtime capability is justified.

No new provider registry is justified.

No new provider selection runtime is justified.

No new provider orchestration runtime is justified.

No new provider invocation runtime is justified.

The only missing deterministic PCCL capability is an integration artifact for a future milestone:

```text
PCCL_PROVIDER_INTEGRATION_BOUNDARY
```

This future integration boundary should:

- accept a validated PCCL Session;
- accept a validated Canonical Context Envelope;
- accept a validated Canonical Policy Envelope;
- reference existing provider necessity/resource selection evidence;
- reference a canonical provider contract;
- create a provider handoff record for Certified Provider Attachment;
- remain non-authoritative;
- not generate prompts unless a separately certified prompt/projection milestone exists;
- not invoke the provider itself unless routed through Certified Provider Attachment;
- preserve replay-visible lineage from PCCL envelopes to provider evidence.

This is an integration milestone, not a Provider Runtime milestone.

## Recommended Implementation Sequence

1. `G16-06 - PCCL Provider Integration Boundary`

   Implement a deterministic reference artifact that binds PCCL Session, Context Envelope, Policy Envelope, provider selection evidence, and canonical provider contract references. No provider invocation.

2. `G16-07 - PCCL Provider Handoff To Certified Attachment`

   Implement the smallest deterministic handoff from the PCCL integration artifact to `run_certified_provider_attachment(...)`. The Certified Provider Attachment remains the only provider invocation boundary.

3. `G16-08 - PCCL Provider Replay Binding`

   Bind provider attachment replay evidence back to PCCL session lineage without changing Replay ownership.

4. `G16-09 - PCCL Provider Proposal Intake`

   Accept provider proposal evidence as non-authoritative proposal input for later proposal pipeline milestones. No worker execution.

5. Later milestones only after separate audits:

   - proposal pipeline;
   - proposal comparison;
   - cognitive loop controller;
   - provider retry policy integration.

## Architectural Health Assessment

Duplication assessment:

- No duplicate Provider Registry should be created.
- No duplicate Provider Selection should be created.
- No duplicate provider invocation boundary should be created.
- No duplicate Provider Platform runtime should be created.
- No duplicate credential boundary should be created.
- No duplicate provider contract family should be created.

Ownership assessment:

- PCCL should orchestrate cognition lifecycle references only.
- Provider Platform should remain owner of provider mechanics.
- Certified Provider Attachment should remain the production provider access boundary.
- Governance should remain owner of authorization and policy.
- Replay should remain owner of reconstruction and certification.
- Workers should remain execution only.
- Human Interfaces should remain thin.

Current health verdict:

`ARCHITECTURALLY_HEALTHY_REUSE_PROVIDER_PLATFORM`

## Architectural Decision

PCCL does not require a new Provider Runtime.

PCCL should exclusively reuse the certified Platform Core Provider subsystem.

The next milestone should be a Provider Integration Boundary, not a Provider Runtime.

Decision:

```text
PCCL_PROVIDER_RUNTIME_REQUIRED = NO
CERTIFIED_PROVIDER_ATTACHMENT_REUSE_REQUIRED = YES
NEXT_MILESTONE = PCCL_PROVIDER_INTEGRATION_BOUNDARY
```

## Validation Summary

Validation required:

- `git diff --check`

Validation result:

- `git diff --check` passed.

## Boundary Confirmation

G16-05 did not modify AiCLI.

G16-05 did not modify provider runtime code.

G16-05 did not modify provider registry code.

G16-05 did not modify provider selection code.

G16-05 did not invoke providers.

G16-05 did not generate prompts.

G16-05 did not implement a proposal pipeline.

G16-05 did not implement a cognitive loop.

G16-05 did not change Generation 14 ownership boundaries.

## Certification Verdict

CERTIFIED
