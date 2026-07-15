# G29-08 Explicit Canonical Artifact Ingress Binding

Status: implemented bounded Platform Core integration.

## Purpose

G29-08 converts an explicitly supplied opaque Replay wrapper reference into a
validated immutable canonical artifact object before the reference can affect
semantic capability selection. It completes the ingress transition identified
by G29-07 without changing Project Objective, G29-02, Platform Knowledge,
G29-04, G28, Governance, Certification, Replay, or Canonical Presentation.

## Ownership

Platform Core exclusively owns reference resolution, wrapper verification,
canonical artifact validation, deterministic ordering, duplicate rejection,
and downstream binding evidence. A Human Interface transports reference text
or an opaque reference record. It does not open the referenced file, inspect
artifact contents, rank artifacts, determine compatibility, select a
capability, invoke a capability, or authorize execution.

The source runtime retains ownership of the canonical artifact's contents,
identity, hashes, and source Replay. G29-08 creates only an immutable evidence
snapshot; it does not construct or modify the source artifact.

## Ingress contract

The external contract accepts an ordered sequence whose entries are either:

- one opaque wrapper path; or
- an opaque record containing `artifact_reference` and optional
  `expected_artifact_hash` and `expected_wrapper_hash` pins.

Resolution is limited to the supplied reference. Relative paths are resolved
against the declared workspace. Absolute paths must remain inside either the
declared workspace or runtime root. Traversal, symlinks, non-regular files,
missing files, source changes during resolution, malformed wrappers, wrapper
hash mismatches, artifact hash mismatches, unsupported artifact families, and
duplicate or aliasing references fail closed.

Only canonical input families already accepted by certified G28 adapters are
admissible. G29-08 validates the canonical artifact before its type is exposed
to G29-02. It performs no semantic matching itself.

## Runtime composition

```text
Opaque Replay wrapper reference
        |
        v
G29-08 Platform Core resolution
        |
        v
wrapper, identity, hash and canonical-family validation
        |
        v
immutable ingress Replay snapshot
        |
        v
validated canonical artifact object
        |
        v
existing G29-06 explicit_canonical_artifacts contract
        |
        v
existing G29-02 -> Platform Knowledge -> G29-04 -> G28
        |
        v
Canonical Platform Presentation -> Human Interface rendering
```

Ingress failure is projected as a fail-closed Platform Core read-only result.
It cannot reach G29-02, G29-04, G28, a Provider, or a Worker.

## Replay continuity

The append-only ingress Replay contains three ordered, hash-bound records:

1. the opaque ingress request;
2. resolution and canonical validation evidence, including the validated
   immutable artifact snapshot;
3. the Project Context and downstream G29-06 linkage.

Reconstruction verifies wrapper ordering and hashes, artifact snapshot hashes,
the Project Context artifact and hash, and—when present—the complete G29-06
reconstruction and route hash/status. G29-06 then reconstructs G29-02,
G29-04, unchanged G28, and Canonical Presentation evidence.

## Authority boundaries

- Explicit artifact ingress is not semantic selection.
- Semantic selection is not authorization.
- The Human Interface remains presentation and opaque transport only.
- Platform Core remains the sole ingress validation and artifact-binding
  authority.
- G29-02 remains the sole deterministic semantic selection authority.
- G29-04 remains the lifecycle composition boundary.
- G28 remains the certified capability invocation authority.
- No Provider or Worker is invoked by ingress.
- No execution or repository mutation is authorized by ingress.
- Replay and Governance authorities are unchanged.

## Remaining limitation

G29-08 accepts only explicit existing canonical Replay artifacts from the
currently certified G28 input families. Natural-language text cannot replace,
create, discover, or repair a canonical artifact. Artifact production and any
later execution authorization remain separate governed responsibilities.
