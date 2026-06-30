# G6-08 Platform Canonical Projection Architecture Audit V1

Status: canonical projection architecture audited.

Final verdict: PLATFORM_CANONICAL_PROJECTIONS_ALREADY_EMERGE_FROM_PLATFORM_CORE

## 1. Architectural Motivation

G6-07 established that Certified Platform Knowledge already emerges from Platform Core as a deterministic projection over certified assets.

G6-08 audits whether that principle generalizes across Platform Core. The question is whether AiGOL should expose multiple deterministic canonical projections over existing certified state instead of creating additional architectural subsystems.

This audit follows the Generation 6 principle:

```text
Reuse -> Canonicalization -> Extension
```

before considering any new architecture.

## 2. Audit Scope

Reviewed candidate projections:

- Certified Platform Knowledge View;
- Capability View;
- Governance View;
- Replay View;
- Public API View;
- Ownership View;
- Runtime Registry View;
- Extension Lineage View.

Reviewed source areas:

- UBTR;
- CSA;
- PGSP;
- OCS;
- UHCL;
- Replay;
- Governance;
- Worker Platform;
- External Provider Platform;
- public Platform API documents;
- runtime registries;
- governance certification artifacts;
- replay reconstruction entrypoints.

This audit does not redesign Platform Core, introduce a new projection runtime, create a framework, rename modules, mutate repositories, activate providers, activate Workers, create approvals, create authorizations, or change replay semantics.

## 3. Executive Determination

Platform canonical projections already emerge from Platform Core.

The existing architecture repeatedly exposes deterministic views over certified source assets:

- public API documents project runtime entrypoints and adapter contracts;
- governance documents project certification state, authority boundaries, and final verdicts;
- replay functions project reconstructable evidence;
- runtime registries project passive provider, resource, domain, Worker, and bundle metadata;
- ownership matrices project canonical responsibilities;
- reuse and implementation audits project extension lineage.

The missing work is canonicalization of projection schemas and lookup contracts, not a new authority layer or permanent projection subsystem.

## 4. Projection Model

A Platform canonical projection is:

```text
deterministic, replay-visible, non-authoritative view over certified Platform Core sources
```

Each projection must define:

- source records;
- deterministic reconstruction method;
- owner of the projection surface;
- owner of the underlying authority;
- replay visibility;
- governance status;
- schema expectations;
- conflict handling;
- known gaps.

A projection must not:

- create authority;
- mutate source records;
- override Governance;
- replace Replay;
- duplicate UBTR, OCS, EPP, Worker Platform, registries, or Public APIs;
- silently upgrade partial certification into full certification.

## 5. Projection Taxonomy

| Projection | Canonical Sources | Deterministic Reconstruction | Governance Authority | Replay Visibility | Projection Owner | Required Canonical Schema | Duplicated Authority |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Certified Platform Knowledge View | Governance docs, public API docs, runtime registries, replay functions, final verdicts. | Reconstruct by indexing source records and hashes. | Governance remains authority for certification. | Required. | Platform Core projection surface. | `CERTIFIED_PLATFORM_KNOWLEDGE_RECORD_V1`. | None if projection remains evidence-only. |
| Capability View | CPK records, G6-05 audits, public API indexes, registries. | Resolve capability id, aliases, owner, entrypoint, status, gaps. | Governance certifies status; owners retain responsibility. | Required. | Platform Core / PGSP consumer view. | `PLATFORM_CAPABILITY_RECORD_V1`. | None if it does not select or authorize execution. |
| Governance View | Governance lineage model, certification reviews, final verdicts, manifests. | Reconstruct chronology, verdict, authority, limitation, and lineage. | Governance. | Required where evidence is replay-bound; documentation lineage remains source-visible. | Governance. | `GOVERNANCE_CERTIFICATION_VIEW_V1`. | None. |
| Replay View | Replay packages, reconstruction functions, replay hashes, artifact hashes. | Invoke or reference `reconstruct_*_replay(...)` contracts. | Replay proves reconstruction only. | Native. | Replay. | `REPLAY_EVIDENCE_VIEW_V1`. | None if it does not certify governance meaning. |
| Public API View | PGSP public API docs, EPP public API docs, runtime entrypoints. | Index operations, callable entrypoints, adapter contracts, replay entrypoints. | Source docs and owning Platform Services. | Required for runtime integration evidence. | Platform Core API documentation. | `PUBLIC_PLATFORM_API_VIEW_V1`. | None if it does not wrap behavior. |
| Ownership View | Constitutional docs, ownership matrices, Generation audits. | Resolve owner by capability, layer, artifact type, and boundary. | Constitutional governance and certified architecture docs. | Source-visible; replay-visible where bound to runtime artifacts. | Governance / Platform Core. | `PLATFORM_OWNERSHIP_VIEW_V1`. | None if it does not transfer ownership. |
| Runtime Registry View | Provider registries, ERR, domain registries, Worker registries, bundle registries. | Validate registry hashes and resolve metadata by id/capability. | Registry owners for metadata only. | Required when selection evidence is produced. | Domain-specific registry owners. | `RUNTIME_REGISTRY_VIEW_V1`. | Risk exists if treated as routing authority; must remain passive unless certified selection owns policy. |
| Extension Lineage View | Reuse audits, canonicalization docs, implementation docs, validation reports. | Link gap -> recommendation -> implementation -> certification verdict. | Governance certifies lineage status. | Source-visible and replay-visible where runtime evidence exists. | Governance / Platform Core. | `EXTENSION_LINEAGE_VIEW_V1`. | None if partial gaps remain explicit. |

## 6. Authority Analysis

Canonical projections are not authorities. They expose authority-bearing source records.

| Concern | Authority Owner | Projection Role |
| --- | --- | --- |
| Semantic meaning | UBTR | Projection may expose known aliases; UBTR still translates. |
| Canonical representation | CSA | Projection may provide capability references; CSA still represents intent. |
| Session protocol | PGSP | Projection may inform session planning; PGSP still owns invocation model. |
| Orchestration | OCS | Projection may provide evidence; OCS still proposes. |
| Human communication | UHCL | Projection may supply source facts; UHCL still renders explanation. |
| Certification and admissibility | Governance | Projection exposes verdicts; Governance remains authority. |
| Replay reconstruction | Replay | Projection links replay entrypoints; Replay proves reconstruction. |
| Provider integration | EPP / Provider Services | Projection indexes EPP capabilities; EPP owns provider integration. |
| Worker execution | Worker Services | Projection indexes Worker capabilities; Worker Services owns execution. |
| Runtime metadata | Runtime registries | Projection reads metadata; registries remain passive unless a certified selection runtime applies policy. |

No projection may approve, authorize, execute, dispatch, mutate, deploy, or certify by itself.

## 7. Duplication Analysis

Creating independent subsystems for these views would duplicate existing Platform Core responsibilities.

| Proposed New Layer | Duplication Risk |
| --- | --- |
| Knowledge subsystem | Duplicates Governance verdicts, public APIs, registries, and replay evidence. |
| Capability subsystem | Duplicates CPK, public API indexes, ownership matrices, and registries. |
| Governance view runtime with authority | Duplicates Governance and could bypass certification boundaries. |
| Replay view runtime with authority | Duplicates Replay and could imply replay decides governance meaning. |
| Public API facade by default | Duplicates documented public APIs before integration pressure proves need. |
| Ownership registry as authority | Duplicates constitutional and generation architecture docs. |
| Global runtime registry | Risks merging passive registries with OCS/Governance selection authority. |
| Extension lineage engine | Duplicates governance lineage unless it remains a deterministic index. |

The safe model is projection, not replacement.

## 8. Deterministic Reconstruction Model

Each canonical projection should reconstruct from explicit source records:

1. Source discovery:
   - governance documents;
   - final verdict lines;
   - public API indexes;
   - runtime registry records;
   - replay reconstruction entrypoints;
   - ownership matrices;
   - validation reports.
2. Source validation:
   - path exists;
   - artifact type or document title matches expected class;
   - final verdict is preserved exactly;
   - hash is recorded where available;
   - replay reconstruction function is named where available.
3. Projection assembly:
   - normalize ids and aliases;
   - bind owner;
   - bind capability;
   - bind public API;
   - bind governance status;
   - bind replay support;
   - bind known gaps.
4. Conflict handling:
   - conflicting sources do not resolve silently;
   - stale or partial records remain visible;
   - Governance review is required for authoritative correction.
5. Replay visibility:
   - projection output should be hash-bound when runtime-produced;
   - documentation-only projections must cite source paths and verdict text.

This model preserves deterministic lookup without creating new source authority.

## 9. Long-Term Architecture

The long-term Platform Core architecture should expose canonical projections as views:

```text
Certified Platform Core sources
        |
        v
Deterministic projection views
        |
        +-- Certified Platform Knowledge View
        +-- Capability View
        +-- Governance View
        +-- Replay View
        +-- Public API View
        +-- Ownership View
        +-- Runtime Registry View
        +-- Extension Lineage View
        |
        v
PGSP / OCS / UHCL consumers
        |
        v
Human-visible governed interaction
```

Projection consumers:

- PGSP uses projections for session planning and capability reuse checks.
- UBTR uses projections for canonical names and aliases, without owning truth.
- OCS uses projections as evidence for proposals.
- Governance uses projections for review context, without losing authority.
- UHCL renders projection findings and limitations.
- Replay records runtime-produced projection results when projection lookup becomes executable.

## 10. Canonical Schema Need

Minimal canonical schemas are useful, but a framework is not yet justified.

Required future schemas:

- projection source record;
- projection output envelope;
- authority boundary flags;
- source path and hash references;
- final verdict field;
- owner field;
- replay reconstruction reference;
- known gaps field;
- conflict status field.

These schemas should be introduced incrementally as projection records, not as a new generalized runtime framework.

## 11. Architectural Risks

| Risk | Mitigation |
| --- | --- |
| Projection becomes authority | Include explicit non-authority flags and source authority references. |
| Projection hides uncertainty | Require known gaps, conflict status, and source references. |
| Projection duplicates runtime registries | Treat registries as sources; do not centralize metadata ownership. |
| Projection duplicates public APIs | Index public APIs; do not wrap behavior unless integration pressure proves need. |
| Projection duplicates Governance | Preserve exact verdicts and require Governance review for changes. |
| Projection duplicates Replay | Link to replay reconstruction; do not reconstruct independently unless delegated to Replay contracts. |
| Projection encourages adapter bypass | Make PGSP the canonical consumer for governed interactions. |

## 12. Implementation Recommendation

Do not implement a Platform Projection Framework now.

Recommended next batch:

1. `G6_09_CANONICAL_PROJECTION_SOURCE_RECORD_SCHEMA_V1`
2. `G6_10_CERTIFIED_PLATFORM_KNOWLEDGE_RECORD_SCHEMA_V1`
3. `G6_11_PUBLIC_API_AND_REPLAY_PROJECTION_INDEX_V1`
4. `G6_12_PGSP_CANONICAL_PROJECTION_LOOKUP_CONTRACT_V1`
5. `G6_13_CAPABILITY_DISCOVERY_FALLBACK_AND_PROJECTION_CONFLICT_POLICY_V1`

Each batch should reuse existing Governance, Replay, public API documents, runtime registries, and Platform Core ownership artifacts.

## 13. Final Determination

Platform canonical projections already emerge from Platform Core.

The architecture should canonicalize deterministic projection views over existing certified assets rather than introduce additional authority layers or duplicate subsystems.

Final verdict: PLATFORM_CANONICAL_PROJECTIONS_ALREADY_EMERGE_FROM_PLATFORM_CORE
