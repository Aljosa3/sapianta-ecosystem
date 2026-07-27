# G34-03 Adapter Certification Profile Specification V1

Status: SPECIFIED — SUBORDINATE TO GENERIC ADAPTER TOPOLOGY V1  
Version: 1.0.0  
Authority: external Adapter Certification Profile  
Topology dependency: Generic Adapter Topology V1  
Platform dependency: PCBV31 certified external sockets

## 1. Purpose and Scope

This specification defines the canonical form of an Adapter Certification
Profile. A profile is the immutable, adapter-specific constitutional
declaration that instantiates Generic Adapter Topology V1 for one adapter
identity and capability boundary.

A profile declares the adapter's identity, capability, socket binding,
adapter-specific ECC, Evidence Manifest, evidence requirements, compatibility
rules, and Validator inputs. It does not implement an adapter, define a
Platform Core socket, modify Generic Adapter Topology V1, or add authority.

This specification is architecture-only. A profile certification is not
execution authorization, Worker assignment, Validator Replay ownership,
Governance authority, or Certification authority.

## 2. Normative Relationship to the Topology

Generic Adapter Topology V1 is the superior, immutable architectural
specification. Every Adapter Certification Profile:

- MUST declare the exact topology version it implements;
- MUST preserve every topology owner and authority boundary;
- MUST instantiate only adapter-specific information at topology-defined
  stages; and
- MUST NOT add a stage, bypass a socket, or redefine an upstream owner.

A profile extends the topology by supplying concrete constitutional artifacts.
It never modifies the topology. A change to a topology stage, owner,
transition, or invariant is a new topology version, not a profile revision.

## 3. Canonical Profile Structure

The following structure is normative. Field names identify architectural
information; they do not prescribe a serialized schema or evidence payload.

| Section | Mandatory contents |
| --- | --- |
| Profile identity | Profile identifier, profile version, schema version, topology version, canonical profile hash, and publication status. |
| Adapter identity | Adapter identifier, adapter kind, adapter implementation version, descriptor identity/version/hash, and adapter owner. |
| Capability boundary | Declared bounded capability identifiers, external input/output boundary, and the absence of adapter authority. |
| Platform Core binding | Existing certified socket identifier, supported socket compatibility version, and normalized contract identity. |
| ECC profile binding | ECC identifier, version, canonical hash, immutable reference, and declared constitutional scope. |
| Evidence Manifest binding | Manifest identifier, version, canonical hash, immutable reference, and binding to exactly one ECC instance. |
| Evidence requirements | Ordered evidence requirement identifiers, owners, classes, artifact/version/hash commitments, and applicable invocation, session, chain, lineage, wrapper, and Replay bindings. |
| Validation inputs | Exact ECC and Manifest instances, read-only authenticated evidence resolver, required trust anchors, and validation context identity. |
| Compatibility | Explicitly supported profile, adapter, descriptor, socket, ECC, Manifest, Validator, Replay, Governance, and Certification versions; historical support rule; unknown-version behavior. |
| Non-authority commitments | Explicit declarations that the profile, adapter, ECC, Manifest, evidence, and Validator submission create no execution authority. |
| External attachment binding | Optional external attachment contract/version and the immutable references it may publish after Certification. |

A profile MUST include all mandatory sections. It MUST have one stable profile
identity and MUST bind one adapter identity/version to one ECC and one Evidence
Manifest for a declared constitutional validation context.

## 4. Mandatory Profile Fields and Identity Rules

A profile MUST declare, at minimum:

- profile ID, profile version, profile-schema version, and topology version;
- adapter ID, adapter kind, adapter version, adapter owner, and adapter
  descriptor hash;
- bounded capability IDs and a normalized external boundary declaration;
- Platform Core socket ID, socket-contract version, and normalized input/output
  contract identities;
- ECC and Manifest identities, versions, immutable references, and hashes;
- a complete ordered evidence-requirement declaration;
- validation, invocation, session, and chain identity requirements where the
  profile's lifecycle evidence needs them;
- supported-version sets and explicit fail-closed behavior; and
- a canonical profile hash over the complete profile excluding that field.

The profile identity MUST be deterministic from the profile's canonical
content. Changing any identity, compatibility declaration, required evidence,
ECC binding, Manifest binding, or authority commitment produces a different
profile version and hash. A changed profile MUST NOT retain the prior profile
hash or be represented as historical evidence for the prior profile.

Profile identifiers are immutable names, not mutable registry entries. An
adapter may have multiple profiles only when every profile has a distinct
identity, version, evidence set, and compatibility declaration.

## 5. Adapter and Capability Declaration Rules

A profile MUST describe only a bounded external capability. It MUST identify
what external representation is translated and which existing Platform Core
socket receives or returns the normalized representation.

A profile MUST NOT:

- declare that an adapter selects or assigns Workers;
- declare that an adapter authorizes, approves, certifies, or executes by its
  own judgment;
- require Platform Core to inspect adapter implementation;
- make a provider, external system, or adapter result an authority source; or
- claim a new Platform Core capability merely because an adapter can translate
  an external protocol.

The descriptor hash commits the adapter identity and declared translation
boundary. It does not certify implementation behavior by assertion; the ECC,
Manifest, and evidence provide the constitutional validation inputs.

## 6. ECC Profile Requirements

Each profile MUST bind exactly one immutable adapter-specific ECC for the
validation instance. The ECC binding MUST provide its identity, version,
schema compatibility, immutable reference, and canonical hash.

The profile's ECC MUST:

- express requirements only for the adapter-specific instantiation of the
  topology;
- preserve the topology's non-authority, ownership, determinism, replay, and
  fail-closed invariants;
- identify required evidence by stable identifiers and expected ownership;
- require explicit compatibility and historical treatment; and
- reject missing, substituted, unknown, or incompatible inputs.

The ECC MUST NOT change Generic Adapter Topology V1, add Platform Core
authority, or redefine Validator, Replay, Governance, or Certification
responsibilities.

## 7. Evidence Manifest Profile Requirements

Each profile MUST bind exactly one immutable Evidence Manifest instance to its
ECC. The Manifest binding MUST include the Manifest identity, version, schema
compatibility, immutable reference, and canonical hash.

The Manifest MUST:

- bind the complete required evidence set to one ECC before rule evaluation;
- preserve the profile's declared order wherever order is constitutionally
  significant;
- bind artifact, wrapper, and Replay hashes wherever required by the ECC;
- bind invocation, session, chain, and lineage identities wherever required by
  the profile;
- preserve evidence ownership and state whether an artifact is
  adapter-produced, Platform-Core-produced, Replay-produced, or
  Certification-produced;
- resolve references read-only; and
- fail closed on missing, duplicate, extra, substituted, mutable, unordered,
  cross-context, or unauthenticated evidence.

A Manifest authenticates evidence. It MUST NOT create, transfer, upgrade, or
exercise authority.

## 8. Evidence Profile Rules

An evidence requirement in a profile MUST declare:

- a stable requirement identifier and the evidence identity it satisfies;
- the expected owner and non-authority or Core-only authority classification;
- evidence class and immutable artifact type/version identity;
- canonical artifact hash requirements;
- wrapper and Replay-reference requirements where applicable;
- whether invocation, session, chain, derived-chain, and lineage bindings are
  required, optional, or prohibited;
- ordering and predecessor requirements where applicable; and
- the condition under which absence or mismatch fails closed.

Profiles MAY use different evidence semantics for different adapter
capabilities. They MUST NOT reuse an evidence type with different ownership or
meaning under the same profile. Adapter evidence and Worker evidence MUST
remain non-authoritative. Core, Replay, Governance, and Certification evidence
MUST remain owned by their respective stages.

## 9. Constitutional Validation Inputs

A profile's Validator submission MUST contain only immutable, authenticated,
read-only constitutional inputs:

1. Exact ECC instance and canonical ECC hash.
2. Exact Evidence Manifest instance and canonical Manifest hash.
3. The profile identity, version, and canonical profile hash.
4. Read-only evidence and contract resolvers.
5. Required Platform Core/socket compatibility trust anchors.
6. Validation, invocation, session, and chain identities required by the
   profile.
7. The complete evidence set, in declared order.

The Validator consumes these inputs to produce an immutable PASS or FAIL
result. Validation MUST NOT execute an adapter, a Worker, a provider, or a
Platform Core operation, and MUST NOT mutate evidence, Replay, or a
repository.

The topology and this specification do not presume that every current
Validator input schema accepts every future profile. A future profile is
certifiable only when its declared Validator integration explicitly supports
the profile's ECC, Manifest, and evidence semantics. Extending such Validator
support is constitutional infrastructure work, not an adapter implementation
shortcut and not a PCBV31 change by itself.

## 10. Compatibility and Fail-Closed Rules

A profile MUST list explicit supported versions for:

- Generic Adapter Topology;
- profile schema and profile version;
- adapter implementation and descriptor;
- Platform Core socket contract;
- ECC and Evidence Manifest schema and version;
- Validator input and Validator result;
- Validator Replay;
- Governance assessment; and
- Constitutional Certification.

Compatibility is explicit only. Unknown, deprecated, missing, incompatible, or
ambiguous versions MUST fail closed unless the profile explicitly declares and
authenticates a historical compatibility path.

A consumer MUST verify every declared hash before relying on its referenced
artifact. Hash mismatch, identity mismatch, schema mismatch, ownership
mismatch, cross-context evidence, incorrect order, or an unsupported
compatibility path MUST produce no PASS result and no authority effect.

## 11. Separation of Topology and Profile

| Generic Adapter Topology V1 owns | Adapter Certification Profile owns |
| --- | --- |
| Stages, ordering, ownership, authority boundaries, and constitutional invariants | Adapter identity, capability boundary, descriptor, ECC, Manifest, evidence requirements, compatibility, and validation context |
| External adapter placement and socket-only Core interaction | Mapping of one adapter's normalized boundary to one existing socket |
| Validator → Replay → Governance → Certification separation | Required adapter-specific validation inputs and evidence semantics |
| External Attachment non-authority | Optional attachment compatibility and immutable reference set |

A profile MUST NOT promote an adapter-specific fact into topology, and the
topology MUST NOT absorb an adapter-specific evidence schema or execution
rule. Profile evolution is additive only within the profile boundary and
requires a new profile version when constitutional inputs change.

## 12. Illustrative Profile Differentiation

The following examples are illustrative only. They are not adapter
implementations, evidence schemas, ECCs, Manifests, or certifications. Each
reuses the same Generic Adapter Topology V1 and differs only in its profile
content.

| Adapter class | Bounded capability declaration | Distinct ECC/Manifest evidence focus |
| --- | --- | --- |
| Filesystem | A declared bounded storage operation through an existing socket | Target-scope integrity, before/after state commitments, operation receipt, and permitted recovery evidence. |
| Git | A declared source-control operation through an existing socket | Repository identity, ref/tree commitments, change-set evidence, and operation receipt. |
| REST | A declared remote service request/response translation | Endpoint/method scope, canonical request/response references, redaction commitments, and service identity. |
| Browser | A declared browser interaction translation | Navigation/action trace, browser identity, bounded rendered-state reference, and operation receipt. |
| MCP | A declared tool-protocol invocation translation | Server/tool descriptor identity, selected-tool schema commitment, normalized tool result, and invocation receipt. |
| LLM | A declared model interaction translation | Model/provider/version identity, input/output commitments, nondeterminism disclosure, and normalized result reference. |
| Robot | A declared physical-device command translation | Device identity, bounded safety envelope, command/telemetry references, and completion or fault receipt. |

None of these examples changes the topology or creates authority. Their
different evidence focuses demonstrate why each requires its own ECC and
Manifest rather than reuse of another adapter's certification profile.

## 13. External Attachment Relationship

An External Adapter Certification Attachment MAY be published only after it
has verified the profile identity/hash and immutable references to the
Validator Replay, Governance assessment, and Constitutional Certification.
It MAY also reference the adapter descriptor, ECC, Manifest, and evidence
commitments.

An attachment MUST remain an external correlation record. It MUST NOT mutate,
append to, or be presented as Platform Replay; it MUST NOT override Governance
or Certification; and it MUST NOT authorize execution or select an adapter.

## 14. Non-Goals

This specification does not:

- implement an adapter or adapter profile;
- define a serialized profile schema;
- define an ECC, Manifest, evidence payload, Worker, or execution policy;
- add or modify a PCBV31 socket;
- modify Generic Adapter Topology V1;
- alter Validator, Replay, Governance, Certification, or the Human Interaction
  Layer; or
- certify any adapter.

## 15. Conclusion

Adapter Certification Profile Specification V1 is the canonical
adapter-specific constitutional standard subordinate to Generic Adapter
Topology V1. Future adapters become independently certifiable by supplying a
profile conforming to this specification while reusing the topology unchanged.

