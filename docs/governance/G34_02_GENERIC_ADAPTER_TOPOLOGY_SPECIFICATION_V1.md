# G34-02 Generic Adapter Topology Specification V1

Status: SPECIFIED — ADAPTER-INDEPENDENT CONSTITUTIONAL ARCHITECTURE  
Version: 1.0.0  
Authority: external Adapter Topology  
Platform dependency: PCBV31 certified external sockets  
Constitutional dependency: ECC → Evidence Manifest → Validator → Replay → Governance → Certification

## 1. Purpose and Scope

This specification defines the immutable architectural topology shared by
external AiGOL adapters. It defines stages, ownership, authority boundaries,
identity flow, artifact flow, Replay flow, Governance flow, and Certification
flow. It does not define an adapter implementation, an evidence schema, an
ECC, a Manifest, a Worker, or execution semantics.

An adapter is an external translation component. It converts an external
capability into one or more already-certified Platform Core contracts. The
Platform Core never depends on the adapter's internal implementation.

This specification does not activate an adapter, add a Platform Core socket,
or authorize execution. It does not alter PCBV31, the Human Interaction
Layer, the Validator, Replay, Governance, or Certification.

## 2. Normative Language

The terms **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**,
**MAY**, and **OPTIONAL** are normative.

## 3. Canonical Topology

```text
External Capability
        │  external request or result; no constitutional authority
        v
External Adapter Descriptor and Translation Layer
        │  normalized, bounded request through an existing socket
        v
Certified Platform Core Socket
        │
        v
Platform Core-owned Execution Lifecycle
        │  Core-owned selection, authorization, assignment, invocation,
        │  result handling, and any execution permitted by the socket
        v
Adapter-normalized Output and Immutable Evidence
        │
        ├─────────────── Adapter-specific ECC
        └─────────────── Adapter-specific Evidence Manifest
                              │  immutable references and hashes only
                              v
                     Read-only Constitutional Validator
                              │  immutable PASS / FAIL result
                              v
                     Platform Validator Replay
                              │  immutable recorded result
                              v
                     Read-only Constitutional Governance
                              │  immutable assessment
                              v
                     Deterministic Constitutional Certification
                              │  immutable certification record
                              v
       External Adapter Certification Attachment (optional publication)
```

The ECC and Evidence Manifest are constitutional inputs to validation. A
profile MAY prepare them before execution, but a completed lifecycle's
evidence MUST be bound before validation. Neither artifact authorizes or
executes the lifecycle it describes.

The External Adapter Certification Attachment is not a constitutional stage
inside PCBV31. It is an external, immutable correlation and publication
record, when one is required. It MUST reference constitutional records rather
than replace, append to, or reinterpret Platform Replay.

## 4. Ownership Matrix

| Stage | Owner | Authority | State | Permitted transition | Forbidden transition |
| --- | --- | --- | --- | --- | --- |
| External capability | External system or adapter operator | None in this topology | External / out of scope | Supply bounded input or output | Grant Platform authority or modify Core |
| Adapter descriptor and translation | Adapter owner | None | Adapter-owned; versioned and hashable when certified | Translate to/from an existing socket | Select Workers, authorize, assign, certify, or own Replay |
| Certified Platform Core socket | Platform Core | Core boundary only | Governed by its certified contract | Accept a conforming bounded request or result | Inspect or depend on adapter internals |
| Platform Core execution lifecycle | Platform Core | Only authority already established by Core | Core-owned runtime state and artifacts | Perform its certified lifecycle | Delegate Core authority to the adapter |
| Adapter-normalized output | Adapter owner, subject to Core result boundary | None | Immutable evidence once bound | Produce normalized output and evidence | Assert execution authorization or certification |
| Adapter-specific ECC | Adapter profile owner | None | Immutable, versioned constitutional artifact | Define adapter-specific validation requirements | Modify this topology or Core ownership |
| Adapter-specific Evidence Manifest | Adapter profile owner | None | Immutable after hashing | Bind exactly the profile's evidence to one ECC | Create authority, execute, or mutate Replay |
| Validator | Validator owner | Determines PASS / FAIL only | Read-only result | Validate authenticated ECC, Manifest, and evidence | Execute, record Replay, govern, certify, or authorize |
| Validator Replay | Platform Replay | Recorder only; no validation authority | Immutable recorded evidence | Record and reconstruct a completed Validator result | Validate, modify history, execute, or authorize |
| Governance | Governance owner | Constitutional interpretation only | Immutable read-only assessment | Read verified Replay and assess its result | Invoke Validator, modify Replay/evidence, or authorize |
| Certification | Certification owner | Certifies Governance conclusion only | Immutable deterministic record | Verify and certify Governance assessment | Invoke upstream stages, modify them, or authorize |
| External Attachment | External attachment publisher | None | Immutable external correlation record | Verify and publish references | Become Replay, change certification, or control execution |

## 5. Authority Boundaries

### 5.1 Authority is not transferred to an adapter

An adapter MUST NOT receive, infer, manufacture, upgrade, or transfer
Platform Core authority. Translation of an external request into a socket
input is not authorization. Translation of a Core result into an external
representation is not certification.

The only possible authority-bearing activity in this topology is a
Platform-Core-owned action already permitted by the certified socket and its
existing lifecycle. This topology neither defines nor expands that authority.

### 5.2 Independent constitutional stages

- Platform Core owns its sockets and execution lifecycle. It MUST NOT depend
  on adapter implementation details.
- The Validator determines only PASS / FAIL from immutable inputs. It MUST
  NOT execute or record Replay.
- Platform Replay records and reconstructs completed Validator results. It
  MUST NOT validate, authorize, or alter history.
- Governance consumes verified Replay only. It MUST NOT mutate Replay,
  evidence, or validation results.
- Certification consumes Governance only. It MUST NOT authorize execution or
  access upstream execution inputs as an authority source.
- An External Attachment remains outside all of those owners. It MUST NOT
  become a parallel recorder or certification authority.

## 6. Mandatory Adapter Interfaces

Every adapter certification profile MUST identify the following external
interfaces. This section names architectural interfaces only; it does not
define their concrete schemas.

| Interface | Required responsibility |
| --- | --- |
| Adapter Identity Interface | Supplies stable adapter identity, implementation version, descriptor version, and immutable descriptor reference or hash. |
| Capability Declaration Interface | Declares the bounded external capability and the certified Core socket contract it can translate to or from. |
| Translation Interface | Converts only between external representation and the named Core socket representation; it carries no decision authority. |
| Socket Binding Interface | Identifies the existing certified Platform Core integration boundary and its supported compatibility version. |
| Normalized Output Interface | Produces a bounded result representation suitable for the existing Core result boundary. |
| Evidence Production Interface | Produces the adapter-specific immutable evidence required by the profile, with identity, version, canonical hash, and applicable lineage bindings. |
| Constitutional Package Interface | Identifies the adapter-specific ECC and Evidence Manifest by ID, version, and hash. |
| Validator Result Interface | Carries the completed immutable Validator result to Platform Replay without causing a Validator side effect. |
| External Attachment Interface | When publication is required, correlates adapter identity with verified constitutional references without changing any upstream record. |

Every interface MUST be explicitly versioned. Unknown, incompatible, missing,
or ambiguous identity, version, socket, evidence, or lineage information MUST
fail closed at the consuming boundary.

## 7. Platform Core Interaction Rules

1. An adapter MUST use only an existing certified PCBV31 socket.
2. An adapter MUST treat the socket as a stable external contract and MUST
   NOT import, patch, subclass, replace, or re-own Platform Core behavior.
3. Platform Core MUST receive only the socket's normalized contract. It MUST
   NOT discover, inspect, select, or depend on an adapter implementation.
4. Adapter-specific routing, worker logic, protocol handling, data handling,
   and evidence production MUST remain outside PCBV31.
5. A socket MAY reject unsupported input or capability scope. An adapter MUST
   NOT treat rejection as permission to bypass the socket.
6. The Human Interaction Layer remains transport-only. It MUST NOT host
   adapter logic, constitutional validation, or attachment publication.
7. This topology does not make the constitutional chain a new Core execution
   gate. Any future Core use of adapter certification for selection,
   authorization, execution, or canonical status requires a new certified
   Platform Core baseline.

Existing sockets are sufficient only for adapters whose bounded translation
semantics fit those socket contracts. This specification does not claim that
every external capability is supported by every socket, and it creates no new
socket by implication.

## 8. Adapter Independence and Extensibility Rules

Adding an adapter MUST NOT require a PCBV31 change when the adapter can bind
to an existing socket and its constitutional records remain external.

Each future adapter reuses this topology by supplying its own:

- descriptor and capability declaration;
- translation implementation;
- normalized output and evidence producer;
- ECC and Evidence Manifest;
- certification-profile compatibility declaration; and
- optional external certification attachment.

The following adapter classes are topology-compatible when their profile
binds only the required external translation and evidence semantics: source
control, browser, REST, MCP, database, robot, speech, LLM, cloud, and future
external capabilities. Compatibility with this topology does not itself
certify an adapter or grant execution authority.

An adapter MUST NOT create a registry, mutable global routing state, or
implicit fallback that changes constitutional dependency selection. Any
adapter-specific dependency or compatibility resolver MUST be explicit and
bounded to the relevant invocation.

## 9. Normative Invariants

1. **Topology immutability.** A certification profile MUST extend this
   topology only through adapter-specific artifacts; it MUST NOT redefine a
   stage, owner, or authority boundary.
2. **External implementation.** Platform Core MUST NOT contain adapter
   implementation logic, and an adapter MUST NOT modify Platform Core.
3. **Socket exclusivity.** Adapter-to-Core communication MUST occur through
   an existing certified socket; no side channel may bypass it.
4. **No adapter authority.** An adapter MUST NOT select Workers, assign
   Workers, authorize execution, create Core authority, or certify itself.
5. **Evidence immutability.** Bound evidence, ECC, Manifest, Validator result,
   Replay record, Governance assessment, Certification record, and Attachment
   reference MUST be immutable and hash-verifiable according to their owners.
6. **Validator isolation.** A Validator MUST NOT execute, mutate evidence,
   own Replay, govern, certify, or authorize.
7. **Replay isolation.** Replay MUST NOT validate, mutate historical records,
   execute, govern, certify, or authorize.
8. **Governance isolation.** Governance MUST read Replay only and MUST NOT
   invoke Validator, modify Replay or evidence, certify, or authorize.
9. **Certification isolation.** Certification MUST consume Governance only
   and MUST NOT modify, invoke, or authorize upstream execution stages.
10. **Attachment non-authority.** An External Attachment MUST remain external
    and MUST NOT replace Replay, Governance, or Certification.
11. **Deterministic identity.** Constitutional records MUST use explicit
    identities, versions, canonical hashes, and ordered lineage where their
    certified contracts require them.
12. **Fail closed.** Missing, mismatched, substituted, unsupported, mutable,
    or ambiguous constitutional input MUST be rejected by the responsible
    consumer; it MUST NOT be repaired or inferred.
13. **No hidden activation.** A PASS, Governance assessment, Certification,
    or Attachment MUST NOT itself activate execution, authorization, or a
    Worker.
14. **Historical preservation.** A new adapter profile MUST NOT alter or
    reinterpret existing Core, Replay, Governance, or Certification history.

## 10. Relationship to Future Adapter Certification Profiles

An Adapter Certification Profile Specification is a subordinate,
adapter-specific instantiation of this topology. It MUST declare the topology
version it implements and MAY define only the concrete information omitted
here: adapter identity values, capability semantics, socket-compatible
translation, evidence schemas, ECC requirements, Manifest contents,
compatibility sets, and test evidence.

A profile MUST NOT:

- change topology ownership or authority rules;
- add authority to the adapter, Validator, Replay, Governance, Certification,
  or Attachment;
- redefine PCBV31 sockets;
- modify historical constitutional records; or
- treat profile certification as a Platform Core authorization.

If a proposed adapter requires a new Core socket, requires Platform Core to
recognize its certification, or requires a changed authority boundary, it is
not a profile-only change. It requires a separately governed architectural
decision and, where PCBV31 behavior changes, a new certified Platform Core
baseline.

## 11. Compatibility and Non-Goals

This specification is intentionally adapter-independent. It does not define
any adapter-specific behavior, Worker, protocol, evidence schema, ECC,
Manifest, routing rule, execution policy, or certification profile.

It is compatible with existing reference implementations only at the
topology level. It does not incorporate any reference implementation's
terminology or artifacts, and it does not retrospectively generalize an
existing adapter-specific Validator input profile.

## 12. Conclusion

Generic Adapter Topology V1 is the stable constitutional architecture for
external adapters. Future adapters reuse its ownership and evidence chain
unchanged while supplying only independently certified, adapter-specific
profiles. PCBV31 remains a closed Core throughout that evolution.
