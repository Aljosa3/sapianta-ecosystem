# G6-11 Platform Canonicalization Roadmap Audit V1

Status: Generation 6 canonicalization roadmap defined.

Final verdict: GENERATION_6_CANONICALIZATION_ROADMAP_DEFINED

## 1. Motivation

G6-10 concluded that full reconstruction of every certified platform state requires minimal canonicalization.

Generation 6 has already established that:

- capability discovery is a temporary development methodology;
- Platform Memory is deterministic;
- Certified Platform Knowledge emerges from Platform Core;
- canonical projections emerge naturally;
- Platform Digital Twin emerges implicitly;
- Platform State Reconstruction emerges from existing architecture;
- remaining work is canonicalization over certified assets, not architectural expansion.

G6-11 consolidates the remaining standardization work into one roadmap.

## 2. Audit Scope

Reviewed sources:

- G6-06 deterministic Platform Memory alignment;
- G6-07 Certified Platform Knowledge architecture;
- G6-08 canonical projection architecture;
- G6-09 Platform Digital Twin architecture;
- G6-10 platform state reconstruction architecture;
- PGSP public API and adapter contract;
- EPP public API and index;
- Governance lineage model;
- Generation 5 execution pipeline certification.

This audit does not redesign Platform Core, introduce runtime components, create new subsystems, create new authority layers, rename modules, activate providers, activate Workers, mutate repositories, create approvals, create authorizations, or change replay semantics.

## 3. Executive Determination

Generation 6 canonicalization is ready to proceed.

The remaining work can be organized into a bounded roadmap:

1. source record normalization;
2. reconstruction manifests;
3. projection records and indexes;
4. status and certification vocabulary;
5. public API, entrypoint, artifact, and replay mapping;
6. ownership normalization;
7. extension lineage linking;
8. deterministic identifiers;
9. cross-reference standards;
10. conflict and fallback policy.

All items are canonicalization over existing certified assets. None should create new authority.

## 4. Consolidated Canonicalization Inventory

| Item | Why It Is Needed | Existing Assets It Builds Upon | New Authority? | Priority | Architectural Impact |
| --- | --- | --- | --- | --- | --- |
| Platform source record schema | Standardizes how docs, registries, replay functions, verdicts, and public APIs become reconstructable source records. | Governance docs, public API docs, runtime registries, replay functions. | No. | P0 | Enables all later reconstruction and projection work. |
| Reconstruction manifest | Defines the ordered source set for deterministic platform state reconstruction. | G6-09 Digital Twin model, G6-10 reconstruction model. | No. | P0 | Makes reconstruction repeatable and auditable. |
| Projection output envelope | Standardizes output for CPK, capability, governance, replay, API, ownership, registry, and lineage views. | G6-08 projection taxonomy. | No. | P0 | Prevents each projection from inventing its own shape. |
| Status vocabulary | Normalizes certified, partial, advisory, extension-required, blocked, documentation-only, runtime-enforced, and domain-scoped states. | Governance lineage classes, G6-10 status gap. | No. | P0 | Prevents accidental certification inflation. |
| Certification vocabulary | Normalizes final verdict, certification basis, certification inheritance, limitation, and known-gap fields. | Governance lineage model, G5-10 certification matrix, G6 verdicts. | No. | P1 | Makes final verdict history machine-indexable. |
| Public API and entrypoint mapping | Maps capability, owner, public API operation, runtime module, artifact type, and replay function. | G4-10 PGSP API, G6-03 EPP API, runtime modules. | No. | P1 | Makes adapters and PGSP capability lookup deterministic. |
| Replay mapping | Links each runtime capability to replay package, reconstruction function, hash evidence, and replay visibility class. | Replay functions, G5-10 replay verification, EPP replay list. | No. | P1 | Prevents duplicated replay interpretation. |
| Ownership normalization | Maps capability, layer, artifact type, runtime area, and canonical owner. | Ownership matrices, constitutional docs, PGSP/EPP/G5 docs. | No. | P1 | Prevents ownership drift and adapter/service conflation. |
| Extension lineage links | Links gap source, recommendation, successor milestone, validation evidence, and final verdict. | G3-G6 audits and implementation docs. | No. | P2 | Turns historical audit sequence into deterministic memory. |
| Deterministic identifiers | Defines stable ids for capability, owner, projection, source record, public API operation, replay evidence, and lineage link. | Existing artifact ids, milestone ids, runtime versions. | No. | P2 | Enables cross-document references without name drift. |
| Cross-reference standard | Defines source path, section, artifact id, runtime entrypoint, test evidence, and replay reference conventions. | Governance docs, public API docs, replay docs. | No. | P2 | Improves traceability and review ergonomics. |
| Conflict policy | Defines fail-closed behavior for conflicting ownership, stale entrypoints, missing replay, or partial certification. | G6-08 and G6-10 conflict requirements. | No. | P2 | Preserves governance integrity during reconstruction. |
| G6-05 fallback policy | Defines when manual capability discovery remains required after projection lookup. | G6-05, G6-06, G6-07. | No. | P3 | Keeps temporary methodology as exception path. |

## 5. Dependency Analysis

Canonicalization must proceed in order.

```text
Source Record Schema
        |
        v
Reconstruction Manifest
        |
        v
Projection Output Envelope
        |
        +--> Status Vocabulary
        +--> Certification Vocabulary
        +--> Deterministic Identifiers
        |
        v
API / Entrypoint / Replay / Ownership Mappings
        |
        v
Extension Lineage Links
        |
        v
Conflict Policy
        |
        v
PGSP Projection Lookup Contract
        |
        v
G6-05 Fallback Review
```

Rationale:

- source records must exist before manifests;
- manifests must exist before deterministic reconstruction;
- projection envelopes must exist before multiple views can be compared;
- vocabularies must exist before statuses can be normalized;
- mapping work must precede PGSP lookup;
- conflict policy must precede any claim of complete reconstruction.

## 6. Implementation Priorities

### P0: Reconstruction Foundation

P0 items:

1. `PLATFORM_SOURCE_RECORD_SCHEMA_V1`
2. `PLATFORM_STATE_RECONSTRUCTION_MANIFEST_V1`
3. `PLATFORM_PROJECTION_OUTPUT_ENVELOPE_V1`
4. `PLATFORM_STATUS_VOCABULARY_V1`

Purpose:

- make source records deterministic;
- make reconstruction repeatable;
- prevent projection shape drift;
- prevent status inflation.

### P1: Evidence And Responsibility Mapping

P1 items:

1. `PLATFORM_CERTIFICATION_VOCABULARY_V1`
2. `PUBLIC_API_ENTRYPOINT_MAPPING_V1`
3. `REPLAY_EVIDENCE_MAPPING_V1`
4. `PLATFORM_OWNERSHIP_MAPPING_V1`

Purpose:

- map capabilities to owners, APIs, entrypoints, replay functions, and certification state.

### P2: Historical Lineage And Integrity

P2 items:

1. `EXTENSION_LINEAGE_LINK_SCHEMA_V1`
2. `PLATFORM_DETERMINISTIC_IDENTIFIER_STANDARD_V1`
3. `PLATFORM_CROSS_REFERENCE_STANDARD_V1`
4. `PLATFORM_RECONSTRUCTION_CONFLICT_POLICY_V1`

Purpose:

- connect audit history to implementation history;
- stabilize identifiers;
- make stale or conflicting evidence visible.

### P3: Runtime Consumer Contract Review

P3 items:

1. `PGSP_PLATFORM_PROJECTION_LOOKUP_CONTRACT_V1`
2. `CAPABILITY_DISCOVERY_FALLBACK_POLICY_REVIEW_V1`

Purpose:

- allow PGSP to consume projections without owning them;
- retain G6-05 only for missing, stale, conflicting, or uncertified knowledge.

## 7. Architectural Risks

| Risk | Mitigation |
| --- | --- |
| Canonicalization becomes subsystem creation | Keep artifacts as schemas, mappings, manifests, and contracts over existing sources. |
| Projection becomes authority | Include non-authority flags and source authority references. |
| Governance verdicts are silently upgraded | Preserve exact final verdict text and known gaps. |
| Replay is duplicated | Link to Replay reconstruction functions instead of reimplementing replay logic. |
| Runtime registries become global routing authority | Treat registries as passive metadata unless certified selection policy applies. |
| PGSP bypasses Governance | PGSP consumes projection evidence; Governance remains checkpoint authority. |
| G6-05 is retired too early | Retain manual discovery as fallback until projection lookup is complete and conflict-safe. |
| Historical docs are over-normalized | Preserve source paths, original verdicts, and documentation-only classification. |

## 8. Completion Criteria

Generation 6 canonicalization is complete when:

- every canonical source record has a stable schema;
- platform reconstruction has an ordered manifest;
- projection outputs use a common envelope;
- status and certification vocabulary are normalized;
- public API operations map to runtime entrypoints, artifact types, and replay functions where available;
- ownership is normalized without transferring responsibility;
- replay evidence is linked without duplicating Replay;
- extension lineage connects gaps to successor milestones and verdicts;
- deterministic identifiers are stable across projections;
- cross-references are consistent;
- conflicts fail closed or require governance review;
- G6-05 manual discovery is explicitly retained only as fallback.

## 9. Recommended Generation 6 Completion Batch

Recommended next milestones:

1. `G6_12_PLATFORM_SOURCE_RECORD_SCHEMA_V1`
2. `G6_13_PLATFORM_STATE_RECONSTRUCTION_MANIFEST_V1`
3. `G6_14_PLATFORM_PROJECTION_OUTPUT_ENVELOPE_AND_STATUS_VOCABULARY_V1`
4. `G6_15_PUBLIC_API_ENTRYPOINT_REPLAY_AND_OWNERSHIP_MAPPING_V1`
5. `G6_16_EXTENSION_LINEAGE_AND_CROSS_REFERENCE_STANDARD_V1`
6. `G6_17_PLATFORM_RECONSTRUCTION_CONFLICT_AND_FALLBACK_POLICY_V1`
7. `G6_18_GENERATION_6_CANONICALIZATION_CERTIFICATION_REVIEW_V1`

No runtime implementation should precede these canonicalization artifacts unless a later audit proves that documentation-level canonicalization cannot satisfy the requirement.

## 10. Final Determination

The Generation 6 canonicalization roadmap is defined.

Remaining Generation 6 work is schema, manifest, vocabulary, mapping, lineage, cross-reference, and conflict-policy standardization over existing certified Platform Core assets.

No additional architectural audits are required before beginning canonicalization.

Final verdict: GENERATION_6_CANONICALIZATION_ROADMAP_DEFINED
