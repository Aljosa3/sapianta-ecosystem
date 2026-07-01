# G7-00B Canonicalization Work Package Prioritization Review V1

Status: Generation 7 implementation plan optimized.

Final verdict: GENERATION_7_IMPLEMENTATION_PLAN_OPTIMIZED

## 1. Executive Summary

Generation 7 implementation scope was reduced by G7-00A after reuse review.

Certified input verdict:

```text
GENERATION_7_IMPLEMENTATION_SCOPE_REDUCED_AFTER_REUSE_REVIEW
```

This review prioritizes the remaining work before implementation begins.

The conclusion is that Generation 7 should not implement eleven separate canonicalization artifacts exactly as first listed in G7-00. Most items are tightly coupled and should be consolidated into fewer, stronger artifacts.

The optimized plan preserves:

- no Platform Core redesign;
- no new authority layer;
- no runtime implementation requirement;
- no replacement registry;
- no replay duplication;
- no governance duplication;
- deterministic canonicalization over existing certified assets.

The remaining work is best implemented as compact schema, vocabulary, manifest, mapping, lineage, policy, contract, and certification artifacts.

## 2. Review Methodology

Each G7 work package was evaluated against:

- implementation value;
- architectural impact;
- dependency on earlier artifacts;
- opportunity to merge with adjacent packages;
- opportunity to eliminate redundant scope;
- implementation effort;
- expected long-term maintenance cost;
- consistency with `Reuse -> Canonicalization -> Extension`.

Classification values:

| Classification | Meaning |
| --- | --- |
| Implement | Deliver as a remaining Generation 7 artifact. |
| Merge | Do not deliver as a standalone package; fold into a stronger adjacent artifact. |
| Defer | Keep in roadmap, but implement only after prerequisites exist. |
| Eliminate | Remove duplicated or unnecessary scope from Generation 7. |

## 3. Remaining Work Inventory

| Original Work Package | Existing Coverage | Remaining Value | Primary Remaining Work | Classification |
| --- | ---: | --- | --- | --- |
| G7-01 Platform Source Record Schema | 75% | High | Normalize canonical source fields, source classes, hash policy, authority flags. | Merge |
| G7-02 Platform State Reconstruction Manifest | 70% | High | Define ordered reconstruction manifest and missing/excluded source fields. | Merge |
| G7-03 Projection Output Envelope and Status Vocabulary | 65% | High | Normalize projection envelope and platform status fields. | Merge |
| G7-04 Certification Vocabulary | 85% | Medium-high | Normalize verdict, basis, inheritance, limitation, and known-gap terms. | Merge |
| G7-05 Deterministic Identifier Standard | 70% | High | Define deterministic id rules, aliases, collision policy. | Merge |
| G7-06 Public API / Entrypoint / Replay / Ownership Mapping | 80% | High | Create one consolidated mapping index over existing certified assets. | Implement |
| G7-07 Extension Lineage and Cross-Reference Standard | 70% | Medium-high | Normalize lineage and cross-reference links across milestones. | Implement |
| G7-08 Platform Reconstruction Conflict Policy | 60% | High | Define stale, missing, conflicting, partial evidence handling. | Merge |
| G7-09 PGSP Platform Projection Lookup Contract | 55% | Medium | Define PGSP consumption contract after projections exist. | Defer |
| G7-10 Capability Discovery Fallback Policy Review | 80% | Medium-high | Define fallback triggers after deterministic lookup is available. | Merge |
| G7-11 Generation 7 Canonicalization Certification Review | 45% | High | Certify completed canonicalization artifacts after implementation. | Defer |

No original work package requires runtime implementation at this stage.

## 4. Prioritization Matrix

| Item | Implementation Value | Architectural Impact | Dependencies | Merge / Eliminate Opportunity | Effort | Maintenance Cost | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Source record schema | High | Low, descriptive only | Existing governance docs, public API docs, runtime records | Merge with identifier rules | Low | Low | Merge |
| Deterministic identifiers | High | Low, descriptive only | Source record fields | Merge into source record schema | Low | Low | Merge |
| Reconstruction manifest | High | Low, projection only | Source records and identifiers | Merge with projection envelope | Low-medium | Medium | Merge |
| Projection envelope | High | Low, projection only | Manifest, status vocabulary | Merge with manifest fields where practical | Medium | Medium | Merge |
| Status vocabulary | High | Low, terminology only | Existing governance statuses and verdicts | Merge with certification vocabulary | Low | Low | Merge |
| Certification vocabulary | Medium-high | Low, terminology only | Governance lineage and final verdicts | Merge with status vocabulary | Low | Low | Merge |
| API / entrypoint / replay / ownership mapping | High | Low, index only | Source schema, identifiers, vocabularies | Implement as one consolidated index | Medium | Medium-high | Implement |
| Extension lineage and cross-reference standard | Medium-high | Low, lineage only | Mapping index, governance history | Implement as one lineage standard | Medium | Medium | Implement |
| Reconstruction conflict policy | High | Low, fail-closed policy only | Manifest, envelope, mapping, lineage | Merge with discovery fallback policy | Medium | Low-medium | Merge |
| Capability discovery fallback | Medium-high | Low, methodology policy only | Conflict policy, projection lookup readiness | Merge with conflict policy | Low | Low | Merge |
| PGSP projection lookup contract | Medium | Low, consumer contract only | At least one projection/index artifact | Defer until projections exist | Medium | Medium | Defer |
| Generation 7 certification review | High | Low, governance review only | All implemented artifacts | Defer until end | Medium | Low | Defer |

## 5. Merge Opportunities

### 5.1 Source Record And Identifier Standard

Merge original:

- G7-01 Platform Source Record Schema;
- G7-05 Deterministic Identifier Standard.

Recommended artifact:

```text
G7_01_PLATFORM_SOURCE_RECORD_AND_IDENTIFIER_STANDARD_V1
```

Rationale:

Identifier rules depend directly on source record fields. A standalone identifier standard would increase cross-reference overhead without adding authority or runtime value.

### 5.2 Manifest And Projection Envelope

Merge original:

- G7-02 Platform State Reconstruction Manifest;
- the envelope portion of G7-03 Projection Output Envelope and Status Vocabulary.

Recommended artifact:

```text
G7_02_PLATFORM_RECONSTRUCTION_MANIFEST_AND_PROJECTION_ENVELOPE_V1
```

Rationale:

Projection outputs must cite manifest scope, source records, excluded sources, replay visibility, known gaps, and conflict state. These are naturally one reconstruction/output contract.

### 5.3 Status And Certification Vocabulary

Merge original:

- the vocabulary portion of G7-03 Projection Output Envelope and Status Vocabulary;
- G7-04 Certification Vocabulary.

Recommended artifact:

```text
G7_03_PLATFORM_STATUS_AND_CERTIFICATION_VOCABULARY_V1
```

Rationale:

Platform status and certification language must remain consistent. Splitting them would risk certification inflation or divergent terminology.

### 5.4 Conflict And Discovery Fallback Policy

Merge original:

- G7-08 Platform Reconstruction Conflict Policy;
- G7-10 Capability Discovery Fallback Policy Review.

Recommended artifact:

```text
G7_06_RECONSTRUCTION_CONFLICT_AND_DISCOVERY_FALLBACK_POLICY_V1
```

Rationale:

Manual discovery should be triggered only by missing, stale, conflicting, or uncertified projection evidence. Conflict handling and fallback policy should therefore be one fail-closed policy.

## 6. Elimination Opportunities

The following scope should be eliminated from Generation 7 unless later evidence proves it necessary:

| Scope | Reason For Elimination |
| --- | --- |
| New reconstruction runtime | Reconstruction is a deterministic projection over existing certified assets. |
| New projection runtime | Projection envelopes and indexes are sufficient for current scope. |
| New Platform Knowledge subsystem | Certified Platform Knowledge already emerges from Platform Core. |
| New Digital Twin subsystem | Platform Digital Twin already emerges as a projection. |
| New runtime registry | Existing registries and public API records remain the sources. |
| New governance authority | Governance already owns certification and admissibility. |
| New replay authority | Replay already owns runtime evidence reconstruction. |
| Standalone identifier package | Identifier rules should live with source records. |
| Standalone certification vocabulary package | Certification terms should live with status vocabulary. |
| PGSP lookup runtime implementation | Current requirement is a contract only, after projection artifacts exist. |

No certified Platform Core component should be replaced or re-owned by Generation 7 canonicalization artifacts.

## 7. Recommended Implementation Sequence

### Phase 1: Foundation Canonicalization

1. `G7_01_PLATFORM_SOURCE_RECORD_AND_IDENTIFIER_STANDARD_V1`
2. `G7_02_PLATFORM_RECONSTRUCTION_MANIFEST_AND_PROJECTION_ENVELOPE_V1`
3. `G7_03_PLATFORM_STATUS_AND_CERTIFICATION_VOCABULARY_V1`

Purpose:

Create the minimum common language needed for all later mapping and projection work.

### Phase 2: Evidence Mapping

4. `G7_04_PUBLIC_API_ENTRYPOINT_REPLAY_OWNERSHIP_MAPPING_INDEX_V1`

Purpose:

Map existing Platform Core capabilities to public APIs, runtime entrypoints, replay evidence, and ownership without transferring authority.

### Phase 3: Lineage And Cross-Reference Integrity

5. `G7_05_EXTENSION_LINEAGE_AND_CROSS_REFERENCE_STANDARD_V1`

Purpose:

Normalize links from gap to recommendation, implementation, validation, and final verdict.

### Phase 4: Fail-Closed Policy

6. `G7_06_RECONSTRUCTION_CONFLICT_AND_DISCOVERY_FALLBACK_POLICY_V1`

Purpose:

Define deterministic handling of stale, missing, conflicting, partial, or uncertified evidence and preserve manual discovery only as fallback methodology.

### Phase 5: Consumer Contract

7. `G7_07_PGSP_PLATFORM_PROJECTION_LOOKUP_CONTRACT_V1`

Purpose:

Define how PGSP may consume canonical projections after projection and mapping artifacts exist. This remains contract-only and does not implement runtime lookup.

### Phase 6: Certification

8. `G7_08_GENERATION_7_CANONICALIZATION_CERTIFICATION_REVIEW_V1`

Purpose:

Certify the completed Generation 7 canonicalization implementation and verify no authority duplication was introduced.

## 8. Optimized Generation 7 Roadmap

| Optimized Package | Source Packages | Action | Priority | Completion Criteria |
| --- | --- | --- | --- | --- |
| G7-01 Source Record And Identifier Standard | G7-01 + G7-05 | Implement merged schema | P0 | Source records and ids are deterministic, descriptive, and non-authoritative. |
| G7-02 Reconstruction Manifest And Projection Envelope | G7-02 + G7-03 envelope | Implement merged contract | P0 | Reconstruction scope, sources, gaps, replay references, and projection outputs are normalized. |
| G7-03 Status And Certification Vocabulary | G7-03 vocabulary + G7-04 | Implement merged vocabulary | P0 | Status and certification terms prevent certification inflation and preserve final verdict text. |
| G7-04 Public API / Entrypoint / Replay / Ownership Mapping Index | G7-06 | Implement consolidated index | P1 | Capability mappings cite existing APIs, entrypoints, replay functions, artifacts, and owners. |
| G7-05 Extension Lineage And Cross-Reference Standard | G7-07 | Implement lineage standard | P2 | Cross-generation links are deterministic and unresolved links remain visible. |
| G7-06 Conflict And Discovery Fallback Policy | G7-08 + G7-10 | Implement merged fail-closed policy | P2 | Conflict and fallback triggers are explicit and route to Governance when required. |
| G7-07 PGSP Projection Lookup Contract | G7-09 | Defer until projection artifacts exist | P3 | PGSP can consume projection evidence without authority transfer or runtime mutation. |
| G7-08 Generation 7 Certification Review | G7-11 | Defer until end | P4 | Completed artifacts are certified against authority, replay, governance, and scope constraints. |

This reduces Generation 7 from eleven implementation work packages to eight optimized work packages.

## 9. Maintenance Assessment

| Optimized Package | Long-Term Maintenance Cost | Notes |
| --- | --- | --- |
| G7-01 Source Record And Identifier Standard | Low | Changes only when new source classes or id classes are added. |
| G7-02 Reconstruction Manifest And Projection Envelope | Medium | Must evolve with projection scope and reconstruction evidence classes. |
| G7-03 Status And Certification Vocabulary | Low | Should remain stable; changes require governance review. |
| G7-04 Mapping Index | Medium-high | Highest drift risk because APIs, entrypoints, replay records, and ownership can evolve. |
| G7-05 Lineage And Cross-Reference Standard | Medium | Requires consistent use across future milestones. |
| G7-06 Conflict And Discovery Fallback Policy | Low-medium | Stable policy, updated when new conflict classes appear. |
| G7-07 PGSP Projection Lookup Contract | Medium | Depends on future adapter and PGSP consumption patterns. |
| G7-08 Certification Review | Low recurring | One-time certification artifact with future lineage references. |

## 10. Updated Generation 7 Scope

Generation 7 implementation should now be scoped to:

- canonical schemas;
- deterministic identifiers;
- reconstruction and projection contracts;
- status and certification vocabulary;
- consolidated mapping indexes;
- lineage and cross-reference standards;
- fail-closed conflict and fallback policy;
- PGSP projection lookup contract;
- final certification review.

Generation 7 should not implement:

- runtime execution changes;
- new projection runtime;
- new reconstruction runtime;
- new Platform Knowledge subsystem;
- new governance authority;
- new replay authority;
- new public API facade;
- registry replacement;
- provider execution changes;
- Worker execution changes.

## 11. Readiness Assessment

The optimized Generation 7 plan is ready for implementation.

Readiness:

| Area | Assessment |
| --- | --- |
| Architecture | Ready; Generation 6 architecture remains unchanged. |
| Scope | Reduced; eleven packages become eight optimized artifacts. |
| Runtime impact | None currently required. |
| Governance impact | Preserved; no authority transfer. |
| Replay impact | Preserved; Replay is referenced and indexed, not duplicated. |
| Implementation risk | Low to medium; highest drift risk is the consolidated mapping index. |
| Maintenance risk | Acceptable; fewer artifacts reduce long-term overhead. |

## 12. Final Determination

Generation 7 implementation should proceed using the optimized roadmap.

The plan is reduced, consolidated, and aligned with:

```text
Reuse -> Canonicalization -> Extension
```

Final verdict: GENERATION_7_IMPLEMENTATION_PLAN_OPTIMIZED
