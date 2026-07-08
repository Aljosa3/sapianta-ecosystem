# G15-GOVERNANCE-01 - Platform Capability Certification Registry

Status: implemented.

Milestone: Generation 15 Platform Capability Certification Registry.

Scope: governance metadata registry over existing certification evidence. The registry does not replace governance reports, execute runtime, mutate replay, alter approval, alter Human Interfaces, or move ownership out of Platform Core.

## 1. Knowledge Reuse Audit

This milestone reused existing governance, certification, replay, and registry patterns.

Reused evidence:

- `docs/governance/G15_01_REPLAY_OBSERVATION_LAYER_V1.md`
- `docs/governance/G15_HIR_02_REPLAY_BACKED_CLARIFICATION_CONTINUITY.md`
- `docs/governance/G15_SEMANTICS_01_CANONICAL_SEMANTIC_ARTIFACT_TRANSITION_AUDIT.md`
- `docs/governance/G15_RUNTIME_04_DISPATCH_REPLAY_REFERENCE_RESOLUTION.md`
- `docs/governance/G15_REPLAY_01_REPLAY_CERTIFICATION_LINEAGE_AUDIT.md`
- `docs/governance/G15_RUNTIME_05_END_TO_END_RUNTIME_COMPLETION_VERIFICATION.md`
- `docs/governance/G14_41_REFERENCE_UHI_RUNTIME_COMPLETION_VALIDATION_V1.md`
- `docs/governance/G14_43_PROVIDER_PLATFORM_OPERATIONAL_COMPLETION_V1.md`

Reused implementation patterns:

- `aigol/provider/provider_registry.py`
  - Metadata-only registry shape.
  - Deterministic lookup.
  - Fail-closed unknown records.
  - No execution authority.
- `aigol/runtime/platform_core_capability_lookup.py`
  - Platform Core-owned capability lookup boundary.
- `aigol/runtime/capabilities/capability_registry.py`
  - Passive capability allowlist behavior.
- `runtime/governance/capability_registry.py`
  - Static governed capability registry with deterministic public query.
- `aigol/runtime/transport/serialization.py`
  - Existing `replay_hash` canonical hashing.

Reused certification surfaces:

- Replay Certification remains implemented by `aigol/runtime/replay_certification_runtime.py`.
- Runtime verification remains implemented through existing runtime tests.
- Governance reports remain immutable certification evidence.

No duplicate governance report, replay certification artifact, provider registry, worker registry, or runtime execution path was introduced.

## 2. Architectural Review

The Platform Capability Certification Registry is a canonical operational index over certification evidence.

It is not:

- a replacement for governance reports;
- a replay artifact;
- a runtime executor;
- a provider selector;
- a worker selector;
- an approval authority;
- a Human Interface responsibility;
- a governance mutation mechanism.

Ownership:

- Platform Core owns certification registry metadata.
- Governance reports remain authoritative evidence.
- Human Interfaces may query or render registry state but do not own or modify certification state.
- Replay Certification remains owned by Platform Core replay certification runtime.
- Provider Platform and Worker Platform retain their existing ownership boundaries.

The registry is intentionally read-only and deterministic.

## 3. Certification Registry Review

Implemented registry module:

- `aigol/runtime/platform_capability_certification_registry.py`

Canonical registry version:

`G15_GOVERNANCE_01_PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_V1`

Supported certification scopes:

- `AUDIT`
- `IMPLEMENTATION`
- `END_TO_END`
- `RUNTIME`
- `GOVERNANCE`

Supported certification states:

- `DRAFT`
- `VERIFIED`
- `CERTIFIED`
- `SUPERSEDED`
- `DEPRECATED`

Each record exposes deterministic metadata:

- capability identifier
- capability owner
- certification status
- certification scope
- certification milestone
- certification evidence
- certification date
- architectural owner
- implementation owner
- verification type
- certification version
- supersession status
- deterministic certification record hash
- boundary flags proving metadata-only behavior

Initial registered capabilities:

- `REPLAY_OBSERVATION_LAYER`
- `CLARIFICATION_CONTINUITY`
- `CANONICAL_SEMANTIC_ARTIFACT`
- `DISPATCH_REPLAY_REFERENCE_RESOLUTION`
- `REPLAY_CERTIFICATION_RUNTIME`
- `GOVERNED_DEVELOPMENT_RUNTIME_END_TO_END`
- `CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY`
- `PROVIDER_PLATFORM_OPERATIONAL_COMPLETION`

Deterministic lookup support:

- Is this capability certified?
- Which milestone certified it?
- Which governance report is the certification evidence?
- What certification scope applies?
- Has the certification been superseded?
- Which Platform Core component owns the capability?

## 4. Implementation Summary

Added:

- `CapabilityCertificationRecord`
  - Frozen metadata record for a single capability certification.
- `platform_capability_certification_registry()`
  - Returns the canonical deterministic registry.
- `list_platform_capability_certifications()`
  - Returns records in deterministic order.
- `lookup_platform_capability_certification(...)`
  - Fail-closed lookup by capability identifier.
- `is_platform_capability_certified(...)`
  - Returns whether a capability is currently `VERIFIED` or `CERTIFIED` and not superseded.
- `platform_capability_certification_milestone(...)`
  - Returns the certifying milestone.
- `platform_capability_certification_evidence(...)`
  - Returns governance report references.
- `platform_capability_certification_scope(...)`
  - Returns certification scope.
- `is_platform_capability_superseded(...)`
  - Returns supersession state.
- `platform_capability_owner(...)`
  - Returns the Platform capability owner.
- `platform_capability_component_owner(...)`
  - Returns the implementation component owner.

Boundary flags on every record assert:

- governance metadata only;
- governance report evidence remains authoritative;
- no runtime execution authority;
- no Human Interface authority;
- no provider invocation;
- no worker invocation;
- no replay mutation;
- no governance mutation.

## 5. Validation Summary

Validation commands required:

- `python -m py_compile`
- `python -m pytest -q`
- `git diff --check`

Validation results:

- Focused registry regression passed: `6 passed in 0.08s`.
- `python -m py_compile aigol/runtime/platform_capability_certification_registry.py tests/test_g15_governance_01_platform_capability_certification_registry.py` passed.
- `python -m pytest -q` passed: `5829 passed, 4 skipped in 139.27s`.
- `git diff --check` passed.

## 6. Regression Test Summary

Added:

- `tests/test_g15_governance_01_platform_capability_certification_registry.py`

Regression coverage:

- Registry exposes required Generation 15 certified capabilities.
- Registry ordering is deterministic.
- Lookup answers required certification questions.
- Governance report evidence references exist.
- Records are metadata-only and hash-stable.
- Unknown capabilities fail closed.
- Registry version is canonical for G15-GOVERNANCE-01.

## 7. Files Modified

Production:

- `aigol/runtime/platform_capability_certification_registry.py`

Tests:

- `tests/test_g15_governance_01_platform_capability_certification_registry.py`

Governance:

- `docs/governance/G15_GOVERNANCE_01_PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY.md`

## 8. Boundary Confirmation

No runtime execution was added.

No replay mutation was added.

No governance semantics changed.

No approval behavior changed.

No Human Interface behavior changed.

No ownership moved into AiCLI.

No governance report was duplicated or replaced.

The registry indexes certification evidence. Governance reports remain the evidence.

Platform Core owns the registry.

## 9. Governance Report

Governance classification:

`PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_IMPLEMENTED`

Certification registry verdict:

`CANONICAL_RUNTIME_READABLE_CERTIFICATION_INDEX_AVAILABLE`

Evidence preservation verdict:

`GOVERNANCE_REPORTS_REMAIN_AUTHORITATIVE_CERTIFICATION_EVIDENCE`

Ownership verdict:

`PLATFORM_CORE_OWNS_CERTIFICATION_REGISTRY_METADATA`

Boundary verdict:

`NO_RUNTIME_AUTHORITY_GRANTED_BY_REGISTRY`

Generation 14 architectural invariants remain unchanged.
