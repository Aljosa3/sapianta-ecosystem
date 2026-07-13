# G27-05 — Platform Change Impact Analysis

Status: IMPLEMENTED AND DETERMINISTICALLY VERIFIED

Date: 2026-07-13

## Purpose

G27-05 implements one bounded Platform Core capability:

`Normalized Change -> Platform Change Impact Artifact`

It consumes the canonical G27-04 normalized change artifact and projects the
affected Platform capabilities, constitutional layers, Governance surfaces,
Replay surfaces, and Certification surfaces. It does not plan or execute
validation and does not certify the changed implementation.

## Reused Platform Core Authorities

The runtime reuses:

- `NORMALIZED_CHANGE_ARTIFACT_V1` and its public fail-closed validator;
- Platform Capability Certification Registry identifiers, owners,
  implementation owners, certification evidence, and record hashes;
- Platform Knowledge ownership vocabulary exposed by the same registry records;
- capability composition coverage's registry-based dependency discipline;
- the canonical L0-L4 mutation model;
- Governance enforcement surface definitions;
- Replay lineage and reconstruction patterns;
- Certification ownership metadata;
- canonical serialization, deterministic hashing, and immutable replay writing;
- `FailClosedRuntimeError` semantics.

No duplicate capability registry, constitutional layer model, Governance engine,
Replay service, or Certification service is introduced.

## Runtime and Artifact

Runtime:

- `aigol/runtime/platform_change_impact_analysis_runtime.py`

Canonical artifact:

- `PLATFORM_CHANGE_IMPACT_ARTIFACT_V1`

Operations:

- `analyze_platform_change_impact(...)`;
- `validate_platform_change_impact_artifact(...)`;
- `reconstruct_platform_change_impact_replay(...)`.

Registry capability:

- `PLATFORM_CHANGE_IMPACT_ANALYSIS`.

## Ingress Contract

The only accepted semantic input is a valid `NORMALIZED_CHANGE_ARTIFACT_V1`.

The runtime verifies:

- the normalized artifact and entry hashes;
- successful normalization status;
- replay-visible, read-only, non-authoritative state;
- source normalization reference;
- normalized change hash;
- entry counts, unique paths, operations, artifact types, and unresolved mappings.

Implementation manifests, mutation proposals, mutation outcomes, diffs, raw file
lists, Human Interface requests, and runtime results cannot bypass G27-04.

## Capability Mapping

Capability mapping is derived exclusively from the Platform Capability
Certification Registry.

A changed path must match exactly one of:

1. the repository module path derived from a registry `implementation_owner`; or
2. a registry `certification_evidence` path.

Fuzzy names, natural-language similarity, file-extension inference, and local
Human Interface mappings are not used.

No match is unsupported and fails closed. Multiple registry records matching the
same path are ambiguous and fail closed. Shared implementation modules therefore
require future explicit ownership refinement before impact analysis can claim a
single affected capability.

## Constitutional Layer Mapping

The deterministic mapping policy follows the canonical L0-L4 model:

- L0: exact constitutional and Layer 0 freeze paths;
- L1: canonical manifest paths or explicitly declared schema/canonical artifact
  definition/ledger-definition artifacts;
- L2: deterministic runtime, CLI runtime-entry, and protocol decision paths;
- L3: Governance implementation, evidence, and governance-document paths;
- L4: tests, research, scripts, product lifecycle, and presentation development
  paths.

Every impact entry records both its layer and the rule that selected it.
Unsupported paths fail closed rather than defaulting to L4.

## Surface Projection

Governance surfaces are projected from the canonical constitutional layer. They
identify affected enforcement responsibilities such as Layer 0 freeze,
canonical artifact stability, Decision Spine governance, Governance System
review, and bounded development governance.

Replay surfaces are projected from the constitutional layer and capability
ownership. They identify affected replay identity, lineage, reconstruction, and
Governance evidence continuity. Replay-owned capabilities receive an additional
explicit replay-owner projection.

Certification surfaces identify:

- the Platform Capability Certification Registry; and
- the certification record and evidence for each affected capability.

These are impact projections only. They do not perform Governance evaluation,
Replay certification, or implementation certification.

## Unresolved Mappings

Valid unresolved mappings produced by G27-04 are preserved verbatim and tagged
with `mapping_stage = CHANGE_NORMALIZATION`.

An otherwise complete analysis containing inherited optional gaps receives
`CHANGE_IMPACT_ANALYZED_WITH_UNRESOLVED_MAPPINGS`. Missing or ambiguous
capability/layer mappings are not downgraded to optional gaps; they fail closed.

## Replay Contract

One `PLATFORM_CHANGE_IMPACT_ARTIFACT_V1` is persisted in the
`platform_change_impact_recorded` wrapper.

Replay reconstruction verifies:

- replay ordering and wrapper hash;
- impact artifact and impact-entry hashes;
- deterministic platform change impact hash;
- status/count consistency;
- replay-visible, read-only, non-authoritative state;
- absence of authority grants.

The impact hash excludes the analysis identifier, timestamp, and replay
location. The same normalized change and registry/layer projection therefore
produce the same deterministic impact hash.

## Constitutional Boundary

The capability performs deterministic read-only Impact Analysis only. It does
not:

- create validation plans;
- select tests;
- execute validation;
- invoke Providers or Workers;
- mutate the repository;
- authorize execution or dispatch;
- modify Governance or Replay;
- certify implementation results.

Human Interfaces remain thin. Governance, Replay, Certification, Provider,
Worker, execution, and validation responsibilities remain with their existing
owners.

## Verification

Focused coverage is implemented in:

- `tests/test_g27_05_platform_change_impact_analysis_runtime.py`;
- `tests/test_g27_04_platform_change_normalization_runtime.py`.

Coverage verifies exact registry mapping, L2/L3 mapping, all three surface
families, unresolved mapping preservation, deterministic output, strict source
binding, unsupported mapping rejection, ambiguous shared-owner rejection,
non-authority flags, registry integration, replay reconstruction, and tamper
detection.

## Known Limitations

- Capability impact requires an exact registry owner or evidence path.
- Shared implementation-owner paths fail closed until ownership metadata becomes
  path-specific.
- Dependency propagation beyond the directly mapped certified capability is not
  claimed unless it exists in authoritative composition metadata.
- This milestone intentionally stops before Validation Planning.
