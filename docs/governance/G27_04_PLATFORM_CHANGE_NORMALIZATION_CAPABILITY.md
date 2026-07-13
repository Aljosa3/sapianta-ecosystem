# G27-04 — Platform Change Normalization Capability

Status: IMPLEMENTED AND DETERMINISTICALLY VERIFIED

Date: 2026-07-13

## Purpose

G27-04 introduces one bounded Platform Core capability that converts an
allowlisted authoritative implementation-change artifact into one deterministic,
replay-visible normalized change description.

The capability implements only:

`Implementation Change -> Canonical Change Normalization -> Normalized Change Artifact`

It does not implement Platform Change Impact Analysis or validation orchestration.

## Reuse Assessment

The implementation reuses existing Platform Core primitives:

- canonical JSON serialization and deterministic `replay_hash` construction;
- immutable replay persistence;
- artifact and replay-wrapper hash verification patterns;
- repository-relative `PurePosixPath` validation;
- deterministic sorting and duplicate rejection;
- replay-safe source reference and hash lineage;
- `FailClosedRuntimeError` semantics;
- non-authoritative Platform Capability Certification Registry metadata.

OCS context assembly, canonical context envelopes, Product 1 audit packets, and
other bounded normalization services were not extended because their certified
ownership boundaries do not include repository-change semantics.

## Runtime and Canonical Artifact

Runtime:

- `aigol/runtime/platform_change_normalization_runtime.py`

Canonical artifact:

- `NORMALIZED_CHANGE_ARTIFACT_V1`

Runtime operation:

- `normalize_platform_change(...)`

Replay reconstruction:

- `reconstruct_platform_change_normalization_replay(...)`

Registry capability:

- `PLATFORM_CHANGE_NORMALIZATION`

## Allowlisted Source Families

The initial allowlist contains exactly:

- `IMPLEMENTATION_MANIFEST_ARTIFACT_V1`;
- `GOVERNED_REPOSITORY_MUTATION_PROPOSAL_ARTIFACT_V1`.

The governed repository mutation outcome is intentionally not allowlisted. Its
standalone schema contains target paths but omits the per-path operation and
content evidence needed for unambiguous normalization. Accepting it without its
proposal would require semantic inference and would violate fail-closed behavior.

Every accepted source must provide:

- an allowlisted artifact type;
- a matching authoritative source reference;
- a valid self-verifying artifact hash;
- a caller-supplied source hash equal to that artifact hash;
- replay visibility;
- a valid source lifecycle state and internally consistent entry evidence.

## Normalized Change Entry

Each normalized change entry records:

- source entry reference and hash;
- canonical repository-relative target path;
- original source operation;
- canonical operation type;
- canonical artifact type;
- authoritative before hash when available;
- authoritative after hash when available;
- entry-local unresolved mappings;
- deterministic change-entry hash.

Canonical operation mappings are:

| Source operation | Canonical operation |
| --- | --- |
| `CREATE_ONLY` | `CREATE` |
| `CREATE_OR_REPLACE` | `UPSERT` |
| `REPLACE_CONTENT` | `UPDATE` |

`UPSERT` preserves the source operation's intentional create-or-replace
semantics without inventing repository pre-state.

Implementation manifests retain their declared artifact classification. Governed
mutation proposals are normalized to `REPOSITORY_FILE` because their schema does
not declare a more specific artifact type. The missing detailed classification
is preserved as an unresolved mapping.

## Unresolved Mappings

Missing optional source evidence is never silently inferred. It is represented
in both the affected change entry and the artifact-level deterministic list.

The initial adapters preserve these known unresolved mappings:

- `before_hash` when the source contains no authoritative pre-change hash;
- `artifact_type_detail` when a mutation proposal supplies only file content and
  path evidence.

An unresolved optional mapping produces
`CHANGE_NORMALIZED_WITH_UNRESOLVED_MAPPINGS`. It does not grant downstream
admissibility and does not claim impact completeness.

## Fail-Closed Conditions

Normalization returns `FAILED_CLOSED` with no change entries when:

- the source family is unsupported;
- the source reference or source hash does not match;
- an artifact, entry, or content hash is invalid;
- the source is not replay-visible;
- source lifecycle or count evidence is inconsistent;
- a path is absolute, traversing, empty, or non-canonical;
- an operation cannot be mapped to the canonical vocabulary;
- duplicate target paths conflict;
- required source fields are missing or ambiguous.

Failure artifacts remain replay-visible and non-authoritative so the rejection
can be reconstructed without turning it into an accepted change description.

## Replay Contract

Exactly one normalized change artifact is persisted inside the
`normalized_change_recorded` replay wrapper. Reconstruction verifies:

- replay index and step;
- wrapper hash;
- normalized artifact hash;
- normalized change hash;
- replay-visible, read-only state;
- all non-authority flags.

The normalized change hash excludes normalization identity, timestamp, and replay
location. Identical authoritative source evidence and normalization policy
therefore produce an identical normalized change hash.

## Constitutional Boundary

The capability is read-only, non-authoritative, and metadata-producing. It does
not:

- perform Impact Analysis;
- resolve affected capabilities or constitutional layers;
- plan, select, or execute validation;
- invoke Providers or Workers;
- mutate the repository;
- authorize execution or dispatch;
- modify Governance or Replay;
- certify results.

Human Interfaces remain thin consumers. Governance, Replay, Certification,
Provider, Worker, and execution authority remain with their existing owners.

## Verification

Focused regression coverage is implemented in:

- `tests/test_g27_04_platform_change_normalization_runtime.py`

It verifies both allowlisted adapters, deterministic output, unresolved mapping
preservation, source binding, unsupported-family rejection, ambiguous-operation
rejection, path rejection, authority boundaries, replay reconstruction, and
tamper detection.

## Known Limitation

The initial capability supports two authoritative source families only. Adding a
new family requires an explicit adapter and allowlist change with deterministic
tests. No generic fallback adapter is permitted.
