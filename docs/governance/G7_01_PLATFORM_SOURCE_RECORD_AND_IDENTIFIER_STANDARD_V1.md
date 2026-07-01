# G7-01 Platform Source Record And Identifier Standard V1

Status: first Generation 7 canonicalization package implemented.

Final verdict: FIRST_GENERATION_7_CANONICALIZATION_PACKAGE_IMPLEMENTED

## 1. Implementation Summary

This artifact implements the first optimized Generation 7 canonicalization work package:

```text
G7_01_PLATFORM_SOURCE_RECORD_AND_IDENTIFIER_STANDARD_V1
```

It merges the original G7-01 and G7-05 work packages:

- Platform Source Record Schema;
- Deterministic Identifier Standard.

This is a documentation-first canonicalization artifact. It introduces no runtime subsystem, no registry, no authority layer, and no mutation path.

The purpose is to define a stable way to describe existing certified Platform Core assets as canonical source records and to derive deterministic identifiers from those records.

## 2. Reused Platform Core Assets

This package reuses existing certified Platform Core assets as source material:

| Source Asset | Reused For | Authority Preserved |
| --- | --- | --- |
| `docs/governance/CONSTITUTIONAL_ARCHITECTURE_SPEC_V1.md` | Constitutional source boundary and architectural constraints. | Constitutional governance remains authoritative. |
| `docs/governance/CANONICAL_LAYER_MODEL.md` | Layer ownership and mutation boundary references. | Layer model remains authoritative. |
| `docs/governance/CONSTITUTIONAL_INVARIANTS.md` | Invariant preservation fields and authority flags. | Invariants remain authoritative. |
| `docs/governance/GOVERNANCE_LINEAGE_MODEL.md` | Lineage source class and certification lineage references. | Governance lineage remains authoritative. |
| `docs/governance/STABLE_SUBSTRATE_DECLARATION_V1.md` | Stable substrate source class and substrate status references. | Stable substrate declaration remains authoritative. |
| `docs/governance/G4_10_PGSP_PUBLIC_API_DOCUMENTATION_AND_ADAPTER_CONTRACT_V1.md` | Public API source class examples. | PGSP public API contract remains authoritative. |
| `docs/governance/G5_10_EXECUTION_PIPELINE_CERTIFICATION_REVIEW_V1.md` | Certification review source class examples. | Governance certification remains authoritative. |
| `docs/governance/G6_12_GENERATION_6_ARCHITECTURAL_CONSOLIDATION_AND_CLOSURE_AUDIT_V1.md` | Generation 6 closure and certified architecture baseline. | Generation 6 closure verdict remains authoritative. |
| `docs/governance/G7_00_CANONICALIZATION_IMPLEMENTATION_PROGRAM_V1.md` | Generation 7 implementation program. | Program approval remains authoritative. |
| `docs/governance/G7_00A_CANONICALIZATION_IMPLEMENTATION_READINESS_REVIEW_V1.md` | Reduced implementation scope. | Reuse review verdict remains authoritative. |
| `docs/governance/G7_00B_CANONICALIZATION_WORK_PACKAGE_PRIORITIZATION_REVIEW_V1.md` | Optimized G7 package ordering and merge decision. | Prioritization verdict remains authoritative. |

This artifact indexes and normalizes those sources. It does not replace them.

## 3. Canonicalization Performed

This package canonicalizes:

- source record field names;
- source record required fields;
- source classes;
- evidence classes;
- authority boundary fields;
- hash policy fields;
- deterministic identifier construction rules;
- alias rules;
- collision handling;
- example records.

It does not:

- certify new truth;
- change any source artifact;
- mutate replay evidence;
- approve work;
- authorize execution;
- create a runtime registry;
- replace Governance, Replay, public APIs, or runtime registries.

## 4. Platform Source Record Schema

A Platform Source Record is a deterministic reference to an existing Platform Core asset.

It is descriptive and non-authoritative unless the referenced source is itself authoritative.

### 4.1 Required Fields

| Field | Required | Type | Purpose |
| --- | --- | --- | --- |
| `source_record_id` | Yes | string | Deterministic identifier for this source record. |
| `source_class` | Yes | enum | Category of source being referenced. |
| `source_path` | Yes | string | Repository path or stable source locator. |
| `source_title` | Yes | string | Human-readable source title. |
| `source_version` | Yes | string | Version or milestone identifier. |
| `owner` | Yes | string | Existing Platform Core owner of the referenced source. |
| `evidence_class` | Yes | enum | Kind of evidence provided by the source. |
| `authority_boundary` | Yes | enum list | Authorities the record must not assume. |
| `status` | Yes | string | Current known status of the referenced source. |
| `final_verdict` | Conditional | string | Exact final verdict when the source has one. |
| `source_hash_policy` | Yes | enum | Hashing expectation for source integrity. |
| `replay_visibility` | Yes | enum | Whether the source is replay-visible, documentation-only, or runtime-derived. |
| `governance_reference` | Conditional | string | Governance source or verdict reference. |
| `known_gaps` | Yes | string list | Known limitations or missing evidence. |
| `created_by_package` | Yes | string | Canonicalization package that created the record. |

### 4.2 Optional Fields

| Field | Type | Purpose |
| --- | --- | --- |
| `section_reference` | string | Stable section heading or anchor inside the source. |
| `runtime_module` | string | Runtime module referenced by the source. |
| `public_api_operation` | string | Public API operation referenced by the source. |
| `replay_reference` | string | Replay artifact, replay function, or replay evidence reference. |
| `lineage_predecessor` | string list | Prior source records or milestones. |
| `lineage_successor` | string list | Later source records or milestones. |
| `compatibility_aliases` | string list | Non-owning aliases for compatibility. |
| `notes` | string | Additional descriptive context. |

## 5. Source Classes

Canonical source classes:

| Source Class | Description | Example |
| --- | --- | --- |
| `constitutional_artifact` | Constitutional or invariant source. | `CONSTITUTIONAL_INVARIANTS.md` |
| `layer_model` | Canonical layer or ownership model. | `CANONICAL_LAYER_MODEL.md` |
| `governance_lineage` | Governance lineage or certification lineage source. | `GOVERNANCE_LINEAGE_MODEL.md` |
| `governance_audit` | Architectural or certification audit with final verdict. | `G6_12_..._AUDIT_V1.md` |
| `public_api_contract` | Public Platform Core API or adapter contract. | `G4_10_..._CONTRACT_V1.md` |
| `implementation_program` | Approved implementation roadmap or program. | `G7_00_..._PROGRAM_V1.md` |
| `readiness_review` | Scope, readiness, or prioritization review. | `G7_00A_..._REVIEW_V1.md` |
| `runtime_registry` | Existing runtime registry or module index. | Existing runtime registry record. |
| `replay_contract` | Replay reconstruction contract or replay evidence source. | Replay reconstruction function or artifact. |
| `ownership_matrix` | Ownership or responsibility mapping source. | Governance ownership matrix. |
| `lineage_record` | Extension, successor, or cross-reference lineage source. | Future G7 lineage index. |

New source classes may be added only when an existing source cannot be represented by one of these classes.

## 6. Evidence Classes

Canonical evidence classes:

| Evidence Class | Description |
| --- | --- |
| `constitutional_constraint` | Defines constitutional or invariant constraints. |
| `ownership_boundary` | Defines ownership or responsibility boundaries. |
| `public_api_definition` | Defines public API or adapter contract. |
| `runtime_entrypoint_reference` | References a runtime entrypoint without owning it. |
| `replay_evidence_reference` | References replay evidence or reconstruction capability. |
| `governance_certification` | Contains governance certification or final verdict. |
| `implementation_scope` | Defines implementation scope or roadmap. |
| `readiness_assessment` | Defines readiness, reuse, or prioritization conclusions. |
| `lineage_evidence` | Connects predecessor and successor milestones. |
| `documentation_only_evidence` | Provides architectural documentation without runtime evidence. |

Evidence classes describe what the source provides. They do not create new authority.

## 7. Authority Boundary Values

Every source record must declare what authority it does not possess.

Canonical authority boundary values:

| Boundary | Meaning |
| --- | --- |
| `no_governance_authority` | Record does not certify or decide admissibility. |
| `no_replay_authority` | Record does not reconstruct or mutate replay evidence. |
| `no_runtime_authority` | Record does not invoke runtime behavior. |
| `no_execution_authority` | Record does not approve, authorize, or execute work. |
| `no_registry_authority` | Record does not replace runtime registries. |
| `no_public_api_authority` | Record does not replace public API contracts. |
| `no_ownership_transfer` | Record indexes ownership without transferring it. |

Most Generation 7 canonicalization records should include all applicable non-authority boundaries.

## 8. Source Hash Policy

Canonical hash policy values:

| Policy | Meaning |
| --- | --- |
| `hash_required_for_runtime_source` | Runtime-produced or runtime-consumed source records must be hash-bound. |
| `hash_recommended_for_documentation_source` | Documentation sources should be hashable when tooling exists. |
| `path_and_verdict_reference_only` | Documentation-only sources may be referenced by stable path and exact verdict. |
| `external_hash_not_available` | External or non-repository sources must explicitly report missing hash evidence. |

Hash policy is an integrity aid. It does not certify truth or replace Governance.

## 9. Deterministic Identifier Standard

Identifiers must be deterministic, descriptive, and non-authoritative.

### 9.1 Identifier Grammar

Canonical identifier format:

```text
<namespace>:<source_class>:<normalized_source_version>:<normalized_source_name>
```

Rules:

- use lowercase ASCII;
- replace spaces and punctuation with `_`;
- collapse repeated underscores;
- trim leading and trailing underscores;
- preserve milestone numbers where present;
- do not include timestamps unless the source itself is time-versioned;
- do not include mutable line numbers;
- do not encode certification status into the identifier.

### 9.2 Namespaces

Canonical namespaces:

| Namespace | Use |
| --- | --- |
| `platform` | Platform Core architectural and governance sources. |
| `pgsp` | PGSP-specific public API or session protocol sources. |
| `epp` | External Provider Platform sources. |
| `worker` | Worker Platform sources. |
| `provider` | Provider identity or cognition sources. |
| `replay` | Replay evidence and reconstruction sources. |
| `governance` | Governance certification and lineage sources. |
| `product` | Product lifecycle or enterprise product sources. |

Namespace selection is descriptive and does not transfer ownership.

### 9.3 Identifier Examples

| Source | Identifier |
| --- | --- |
| `G7_00_CANONICALIZATION_IMPLEMENTATION_PROGRAM_V1.md` | `platform:implementation_program:g7_00:g7_00_canonicalization_implementation_program_v1` |
| `G7_00B_CANONICALIZATION_WORK_PACKAGE_PRIORITIZATION_REVIEW_V1.md` | `platform:readiness_review:g7_00b:g7_00b_canonicalization_work_package_prioritization_review_v1` |
| `G6_12_GENERATION_6_ARCHITECTURAL_CONSOLIDATION_AND_CLOSURE_AUDIT_V1.md` | `governance:governance_audit:g6_12:g6_12_generation_6_architectural_consolidation_and_closure_audit_v1` |
| `G4_10_PGSP_PUBLIC_API_DOCUMENTATION_AND_ADAPTER_CONTRACT_V1.md` | `pgsp:public_api_contract:g4_10:g4_10_pgsp_public_api_documentation_and_adapter_contract_v1` |
| `CONSTITUTIONAL_INVARIANTS.md` | `platform:constitutional_artifact:constitutional_invariants:constitutional_invariants` |

## 10. Alias Policy

Aliases are allowed for compatibility and human readability.

Aliases must not:

- become new owners;
- imply new certification state;
- hide the canonical identifier;
- replace source paths;
- collapse distinct architectural identities.

Required alias fields:

| Field | Meaning |
| --- | --- |
| `alias_value` | Compatibility or human-readable alias. |
| `canonical_id` | Canonical identifier being aliased. |
| `alias_reason` | Reason the alias exists. |
| `authority_boundary` | Must include `no_ownership_transfer`. |

## 11. Collision Policy

Identifier collisions must fail closed.

When two records resolve to the same canonical identifier:

1. Do not merge automatically.
2. Mark both records as `conflict`.
3. Preserve both source paths.
4. Route the conflict to Governance review if the sources are authoritative.
5. Route the conflict to canonicalization review if the issue is naming-only.
6. Do not infer ownership, replay evidence, certification, or implementation status.

## 12. Canonical Source Record Examples

### 12.1 Generation 7 Program Source

```yaml
source_record_id: platform:implementation_program:g7_00:g7_00_canonicalization_implementation_program_v1
source_class: implementation_program
source_path: docs/governance/G7_00_CANONICALIZATION_IMPLEMENTATION_PROGRAM_V1.md
source_title: G7-00 Canonicalization Implementation Program V1
source_version: G7_00
owner: Governance
evidence_class: implementation_scope
authority_boundary:
  - no_governance_authority
  - no_replay_authority
  - no_runtime_authority
  - no_execution_authority
  - no_registry_authority
  - no_ownership_transfer
status: approved
final_verdict: GENERATION_7_IMPLEMENTATION_PROGRAM_APPROVED
source_hash_policy: path_and_verdict_reference_only
replay_visibility: documentation_only
governance_reference: GENERATION_7_IMPLEMENTATION_PROGRAM_APPROVED
known_gaps: []
created_by_package: G7_01_PLATFORM_SOURCE_RECORD_AND_IDENTIFIER_STANDARD_V1
```

### 12.2 Generation 7 Prioritization Source

```yaml
source_record_id: platform:readiness_review:g7_00b:g7_00b_canonicalization_work_package_prioritization_review_v1
source_class: readiness_review
source_path: docs/governance/G7_00B_CANONICALIZATION_WORK_PACKAGE_PRIORITIZATION_REVIEW_V1.md
source_title: G7-00B Canonicalization Work Package Prioritization Review V1
source_version: G7_00B
owner: Governance
evidence_class: readiness_assessment
authority_boundary:
  - no_governance_authority
  - no_replay_authority
  - no_runtime_authority
  - no_execution_authority
  - no_registry_authority
  - no_ownership_transfer
status: optimized
final_verdict: GENERATION_7_IMPLEMENTATION_PLAN_OPTIMIZED
source_hash_policy: path_and_verdict_reference_only
replay_visibility: documentation_only
governance_reference: GENERATION_7_IMPLEMENTATION_PLAN_OPTIMIZED
known_gaps:
  - Runtime lookup remains out of scope until later PGSP projection contract work.
created_by_package: G7_01_PLATFORM_SOURCE_RECORD_AND_IDENTIFIER_STANDARD_V1
```

### 12.3 PGSP Public API Source

```yaml
source_record_id: pgsp:public_api_contract:g4_10:g4_10_pgsp_public_api_documentation_and_adapter_contract_v1
source_class: public_api_contract
source_path: docs/governance/G4_10_PGSP_PUBLIC_API_DOCUMENTATION_AND_ADAPTER_CONTRACT_V1.md
source_title: G4-10 PGSP Public API Documentation And Adapter Contract V1
source_version: G4_10
owner: PGSP
evidence_class: public_api_definition
authority_boundary:
  - no_governance_authority
  - no_replay_authority
  - no_runtime_authority
  - no_execution_authority
  - no_ownership_transfer
status: certified
final_verdict: PGSP_PUBLIC_API_READY
source_hash_policy: path_and_verdict_reference_only
replay_visibility: documentation_only
governance_reference: PGSP_PUBLIC_API_READY
known_gaps: []
created_by_package: G7_01_PLATFORM_SOURCE_RECORD_AND_IDENTIFIER_STANDARD_V1
```

## 13. Governance Impact

Governance remains the certification and admissibility authority.

This package:

- exposes source references;
- preserves final verdict text;
- marks non-authority boundaries explicitly;
- prevents source records from silently upgrading certification state;
- routes identifier collisions and authority conflicts to later conflict policy work.

This package does not:

- certify sources;
- resolve governance conflicts;
- decide admissibility;
- approve implementation;
- authorize execution.

## 14. Replay Impact

Replay remains the runtime evidence reconstruction authority.

This package:

- records replay visibility as a field;
- distinguishes documentation-only sources from runtime-derived sources;
- requires runtime-produced source records to be hash-bound when such records exist;
- allows replay evidence references in later mapping work.

This package does not:

- reconstruct replay;
- mutate replay;
- replace replay contracts;
- infer replay evidence when missing.

## 15. Completion Criteria

This package is complete when:

- canonical source record fields are defined;
- source classes are defined;
- evidence classes are defined;
- authority boundaries are defined;
- source hash policy is defined;
- deterministic identifier grammar is defined;
- namespace rules are defined;
- alias policy is defined;
- collision policy is defined;
- examples cite existing certified Platform Core assets;
- no runtime subsystem is introduced.

Completion status: complete.

## 16. Remaining Gaps

Remaining Generation 7 work:

- reconstruction manifest and projection envelope;
- status and certification vocabulary;
- consolidated public API, entrypoint, replay, and ownership mapping index;
- extension lineage and cross-reference standard;
- reconstruction conflict and discovery fallback policy;
- PGSP projection lookup contract;
- Generation 7 certification review.

Known limitation:

- This package defines schema and identifier rules but does not generate machine-readable source records. That remains optional and should be introduced only if later mapping or projection work proves it necessary.

## 17. Validation Evidence

Validation for this documentation-first package:

```text
git diff --check
```

Validation status: passed.

Validation result:

```text
git diff --check
```

Result: clean.

## 18. Final Determination

The first optimized Generation 7 canonicalization package is implemented.

It reuses certified Platform Core assets, defines canonical source records and deterministic identifiers, and preserves all existing authority boundaries.

Final verdict: FIRST_GENERATION_7_CANONICALIZATION_PACKAGE_IMPLEMENTED
