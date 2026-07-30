# Platform Core Capability Interaction Constitution V1

Status: CANONICAL GOVERNANCE SPECIFICATION

Version: V1

Generation: G52-01

Date: 2026-07-30

Authority: Development Governance under Human Constitutional Authority

Certified development baseline: `READY_FOR_CERTIFIED_DEVELOPMENT_BASELINE_V47`

Constitutional position: L3 governed specification defining the common
interaction model for Platform Core capabilities. It creates neither a new
constitutional layer nor an authority tier.

## 1. Purpose and scope

This specification establishes the normative, deterministic interaction model
for present and future Platform Core capabilities. It defines a bounded,
owner-preserving exchange of a declared request, contract, result,
disposition, observation, or immutable evidence reference between identified
constitutional owners.

It does not modify runtime behavior, PCBV31, Replay, Approval, Authorization,
Workers, Providers, Human Interface, or Conversation Boundary runtime; create
a runtime interaction bus, interaction-record loader, or registry-schema
field; grant authority; or certify a capability or interaction by itself.

The terms `MUST`, `MUST NOT`, `REQUIRED`, `SHALL`, `SHALL NOT`,
`SHOULD`, `SHOULD NOT`, and `MAY` are normative. Text explicitly marked
**Informational** is non-normative.

## 2. Authority and repository derivation

This specification is subordinate to the Constitution, Stable Constitutional
Substrate, Canonical Layer Model, Constitutional Invariants, Governance
Enforcement Hierarchy, independent protocol contracts, the authenticated
PCBV31 Baseline Identity Record, and Human Constitutional Authority. Conflicts
are resolved in that order, followed by the Platform Core Capability
Constitution, capability-specific authoritative evidence, this specification,
and implementation-local documentation.

| Repository evidence | Interaction rule derived |
|---|---|
| `docs/governance/PLATFORM_CORE_CAPABILITY_CONSTITUTION_V1.md`, Sections 8-11 | Dependencies and evidence do not delegate authority; Replay ownership remains independent; unknown or incomplete contracts fail closed. |
| `.github/governance/manifests/PLATFORM_CORE_CAPABILITY_REGISTRY_V1.json` | The registry supplies identity, owner, contract, dependency, Replay, evidence, and compatibility declarations for 47 governance profiles; it is not a runtime interaction loader or authority source. |
| `.github/governance/specs/PCBV31_BASELINE_IDENTITY_RECORD_V1.json` | Invocation, evidence exchange, and lifecycle dependency do not absorb an independent protocol owner; PCBV31 identity and spine remain closed. |
| `docs/specifications/G17_HI_02B_PLATFORM_CORE_CONVERSATION_BOUNDARY_SPECIFICATION.md` | Transport submits bounded events; Platform Core owns accepted state and response semantics; every accepted conversation transition is Replay-visible. |
| `docs/governance/G19_04_UNIFIED_PLATFORM_QUERY_ROUTER_IMPLEMENTATION.md` | Deterministic routing uses existing owned services, returns required-evidence-missing without invocation, and does not acquire composed-owner authority. |
| `docs/governance/G20_03_PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_RUNTIME_IMPLEMENTATION.md` | Composition is bounded and read-only, requires certified compatible records, preserves source ownership, and fails closed on ambiguity. |
| `docs/governance/G15_01_REPLAY_OBSERVATION_LAYER_V1.md` | Replay is source evidence; observation is read-only, deterministic, reconstructable, and does not modify source Replay. |

No repository evidence establishes a universal runtime interaction identifier,
cross-capability rollback mechanism, or transferable authority type. V1
therefore defines a governance interaction contract and fails closed where a
future interaction needs behavior beyond an existing owner contract.

## 3. Constitutional interaction definition and distinctions

A **Platform Core capability interaction** is a declared, bounded,
owner-preserving constitutional relation in which an initiating capability or
independent owner presents an identified contract input, request, evidence
reference, or disposition to a receiving capability or independent owner and
the receiver returns, records, or rejects the exact contract outcome.

An interaction exists only when both parties, the consumed or produced
contract, authority boundary, compatibility basis, and required evidence are
identifiable. It is not created merely by an import, shared file, data
presence, transitive dependency, or common implementation module.

| Construct | Constitutional distinction |
|---|---|
| Dependency | A declared prerequisite identity and compatible contract. It records what may be consumed; it does not prove an exchange occurred or transfer authority. |
| Interaction | A bounded contract exchange or evidence/disposition relation between identified owners. It preserves both parties' authority. |
| Coordination | An interaction category that selects, routes, composes, or binds existing owner contracts without duplicating their semantics. |
| Execution | Performance of a certified protocol by its existing execution owner. A request to an execution socket is an interaction; the request grants no execution authority. |
| Ownership | Enduring constitutional responsibility for a state, contract, decision, evidence artifact, or protocol. An interaction cannot change ownership. |
| Authority | Permission to make a constitutional decision or state change. An output, request, response, invocation, or data flow does not convey it. |
| Replay | Independent ownership of historical reconstruction. An interaction may bind Replay evidence but cannot replace, mutate, or delegate Replay. |
| Implementation detail | A local algorithm, import, storage choice, call stack, or module layout with no interaction status absent a declared contract. |

## 4. Canonical interaction contract model

Every new interaction type and every existing interaction at its next
constitutional lifecycle transition MUST have a deterministic interaction
contract. Existing certified behavior remains governed by current authoritative
evidence until that transition; this neither backfills a runtime record nor
alters existing behavior.

### 4.1 Request and response ownership

- The initiating owner owns request meaning, admissibility, and source
  evidence. Acceptance does not make the receiver owner of it.
- The receiver owns only its declared processing, result, disposition, and
  receiver-produced evidence. It MUST NOT rewrite source evidence.
- A wrapper retains source owner, immutable reference, and hash; it owns only
  its binding artifact.
- A response identifies producer, contract, status, and supporting evidence or
  reason. Possession does not make the initiator owner of receiver semantics.

### 4.2 Initiation, completion, and visibility

- Initiation MUST be permitted by initiator scope and receiver's published
  compatible contract, and deterministic from declared input, version, and
  ordering.
- The receiver MUST return a defined success, defined fail-closed outcome, or
  a record that the interaction was not accepted. Silent partial acceptance is
  forbidden.
- Completion is owned by the receiver for its bounded outcome, except where an
  independent protocol owns terminal state or decision. The initiator owns
  subsequent use.
- Visibility MUST state `REPLAY_VISIBLE`, `EVIDENCE_VISIBLE`, `BOTH`, or
  `NEITHER`. A non-visible interaction cannot be sole proof of a
  replay-relevant decision, governed state transition, approval,
  authorization, certification, or execution claim.
- Exact schemas, compatibility, status vocabulary, ordering, and fail-closed
  conditions are required. Unknown, ambiguous, duplicate, incompatible, or
  unverifiable input is rejected.

### 4.3 Authority preservation

Each contract MUST list initiator-owned, receiver-owned, consumed, and
excluded authority and declare `authority_delegated: false`. It MUST NOT
enlarge purpose, scope, or semantic authority boundary.

## 5. Authority propagation model

Constitutional authority does not propagate across an interaction edge. A
contract may communicate a bounded request, exact approved or authorized
artifact, evidence reference, result, or refusal; it cannot transfer the power
to create, amend, broaden, replace, or certify that thing.

| Authority | Interaction rule |
|---|---|
| Execution authority | Never transferable. An initiator may submit a certified request to an existing PCBV31 or independent execution socket; only the execution owner may execute its certified contract. |
| Replay authority | Never transferable. An interaction may provide references and hashes or require visibility; `PLATFORM_CORE_REPLAY` remains the Replay owner. |
| Approval authority | Never transferable. A capability may prepare a candidate or consume an exact Human Approval result where allowed; it cannot infer, issue, or bypass approval. |
| Authorization authority | Never transferable. A capability may request or consume exact bounded authorization; it cannot self-authorize, broaden scope, or continue past missing authorization. |
| Certification authority | Never transferable. Certification independently assesses exact scope and evidence; a capability cannot self-certify or certify a receiver by invoking it. |

Human Constitutional Authority, constitutional amendment authority, PCBV31
execution-spine ownership, Worker and Provider selection/lifecycle authority,
and Human Interface semantic, workflow, or governance authority are likewise
non-transferable. No cyclic authority propagation can exist because no edge
carries authority. A direct or multi-edge delegation graph is invalid and MUST
fail closed rather than be treated as coordination.

## 6. Dependency, interaction, coordination, and execution

- A dependency does **not** imply that an interaction occurred; it declares a
  compatible prerequisite that need not be used for a particular request.
- An interaction does **not** invariably require a capability dependency. An
  interaction with Replay, Approval, Authorization, Certification, a Worker, a
  Provider, or Human Interface is governed by that independent owner's
  authoritative contract.
- A reusable, selectable, or certified-availability interaction between two
  Platform Core capabilities MUST have an explicit direct dependency or
  composition contract. Hidden transitive interactions are forbidden.
- Coordination may deterministically choose or bind existing compatible
  contracts, but cannot execute, approve, authorize, certify, mutate Replay,
  or absorb source semantics.
- Execution is not a general coordination privilege. Interaction with a
  certified execution socket retains existing PCBV31 and independent-owner
  boundaries and cannot change execution behavior.

## 7. Repository-derived interaction categories

Only these categories are established by current repository evidence. An
interaction MUST declare exactly one primary category.

| Category | Bounded meaning | Repository support | Explicit exclusion |
|---|---|---|---|
| `COORDINATION` | Route, compose, select, bind, supervise, or preserve continuity across existing contracts. | Query Router, capability composition, continuity and supervisor capabilities. | Does not duplicate downstream semantics or acquire downstream authority. |
| `VALIDATION` | Submit bounded evidence for analysis or receive findings, plans, recommendations, or a fail-closed validation result. | IVE and validation planning profiles. | Does not execute repair, approve, authorize, or certify. |
| `OBSERVATION` | Read and normalize immutable evidence or produce reconstruction without modifying source. | Replay Observation Layer and root-cause trace. | Does not mutate Replay or make observation authorization. |
| `REPLAY_REFERENCE_PARTICIPATION` | Bind, preserve, validate, or expose immutable Replay reference/hash under Replay ownership. | Capability Constitution Replay model; Conversation Boundary; Observation Layer. | Does not create a Replay owner or modify source Replay. |
| `GOVERNANCE_DISPOSITION` | Obtain or provide deterministic classification, need, admissibility, or governance disposition evidence. | Constitutional Development Governance. | Does not approve, authorize, implement, execute, validate for a validator, or certify. |
| `REGISTRATION_OR_LOOKUP` | Register, discover, or retrieve immutable capability metadata and certification references. | Capability Registry and lookup. | Registry presence does not certify, activate, execute, or grant authority. |
| `BOUNDARY_PROJECTION` | Submit canonical ingress, restore owner-preserving state, or project presentation-neutral result state. | Conversation Boundary and canonical ingress/presentation profiles. | Does not transfer semantics to Human Interface or absorb independent services. |
| `CERTIFIED_EXECUTION_SOCKET_USE` | Present a bounded request to an existing execution socket and receive its existing outcome. | PCBV31 execution surface and baseline identity record. | Does not amend PCBV31, create execution authority, or alter a socket. |

Unsupported categories, or a proposed interaction that combines independent
authorities such that one category cannot be selected, MUST return to
Development Governance and fail closed.

## 8. Failure, cancellation, rollback, and recovery

An interaction failure is a contract-defined failure to initiate, validate,
accept, process, complete, verify compatibility, preserve evidence, or
reconstruct outcome. Missing identity, owner, contract, schema, reference or
hash, compatibility, authorization artifact, required dependency, ordering, or
required Replay binding are failures.

A required failed interaction MUST produce the receiver's existing
contract-defined fail-closed outcome. It MUST NOT invoke an alternate owner,
weaken a requirement, fabricate completion, or continue as accepted. Optional
interactions require deterministic no-interaction behavior and cannot provide
an undeclared authority path.

Cancellation may be initiated only by an actor and protocol authorized to
cancel the relevant interaction. The Conversation Boundary demonstrates that a
Human Interface submits cancellation while Platform Core owns accepted
resulting state. A receiver cannot infer cancellation authority from transport,
request possession, or timeout.

This constitution establishes no universal cross-capability rollback. An
interaction MAY invoke rollback only where the receiving owner's existing
certified contract defines it. A capability may roll back only its bounded
state or request the existing rollback owner through an exact contract; it
cannot roll back another capability, Replay, Approval, Authorization, Worker,
Provider, or PCBV31 by implication.

Recovery MUST use existing deterministic contracts and preserve original
request, known outcome, reason, owners, compatibility, and immutable evidence.
Retry requires an exact declared rule; otherwise the result remains failed
closed. A recovery attempt is a new occurrence and cannot overwrite history.

## 9. Replay and evidence model

An interaction MUST declare `NOT_APPLICABLE`, `OPTIONAL_REFERENCE`,
`REQUIRED_REFERENCE`, or `DERIVED_REQUIRED_REFERENCE` Replay mode,
visibility, Replay owner, source and derived evidence, ordering,
reconstruction owner, lineage, and behavior for missing or invalid evidence.

- `NOT_APPLICABLE` MUST NOT carry a Replay reference.
- Required modes MUST carry immutable references and hashes and fail closed on
  validation failure.
- A replay-relevant deterministic decision or governed state transition MUST
  be Replay-visible. The Conversation Boundary rule that every accepted event
  and transition is visible remains unchanged.
- Evidence is owned by its producer. A coordinator or wrapper owns only its
  binding record and preserves source owner, reference, hash, schema, scope,
  and version.
- Audit reconstruction identifies initiator, receiver, category, contract,
  ordering key, evidence, status, lineage, compatibility, and authority
  boundary.
- Missing source, hash mismatch, owner/scope mismatch, unsupported schema,
  ambiguous ordering, incompatible generation, or incomplete lineage fails
  closed. Replay evidence is never execution permission, approval,
  authorization, or certification.

## 10. Compatibility and evolution

Every interaction type MUST declare compatible Platform Core baseline(s),
protocol and schema versions, participant identities and versions, direct
dependency or independent-owner contract, Replay/evidence compatibility, and
predecessor/replacement relationship. Compatibility is proved by evidence,
never inferred from matching names, imports, or successful calls.

An interaction remains in one version line only when identity, participants,
request/response semantics, authority boundaries, Replay/evidence obligations,
failure behavior, and compatibility are identical. Any change to contract,
participants, dependency, evidence, Replay, compatibility, certified scope, or
failure behavior requires a new version and affected-scope recertification. A
change to constitutional owner, authority boundary, category, or immutable
purpose requires a new identity. A PCBV31 spine/socket or independent protocol
authority change requires constitutional review and, where approved, a new
Platform Core baseline. History is immutable; retirement preserves
reconstructable lineage and cannot transfer authority.

## 11. Canonical interaction template

Every new interaction type and every existing interaction at its next
constitutional lifecycle transition MUST provide an equivalent canonical
governance profile. This is not a runtime schema change.

```yaml
artifact_type: PLATFORM_CORE_CAPABILITY_INTERACTION_PROFILE_V1
profile_version: V1

interaction_identity:
  interaction_identifier: <globally unique stable identifier>
  identity_generation: <generation or baseline>
  primary_category: <one Section 7 category>
  constitutional_purpose: <one bounded exchange responsibility>
  immutable_identity_fields:
    - interaction_identifier
    - initiating_participant
    - receiving_participant
    - primary_category
    - semantic_authority_boundary
    - identity_generation

participants:
  initiating_participant:
    identifier: <capability or independent-owner identifier>
    constitutional_owner: <owner>
    request_ownership: <owned request meaning and source evidence>
  receiving_participant:
    identifier: <capability or independent-owner identifier>
    constitutional_owner: <owner>
    response_ownership: <owned bounded result/disposition evidence>

contract:
  initiation_condition: <deterministic admissibility condition>
  consumed_contract: <exact request, artifact, or socket contract>
  request_schema: <schema and version>
  response_schema: <schema and version>
  completion_statuses: [<success/fail-closed/canceled status>]
  ordering_key: <deterministic ordering or NOT_APPLICABLE>
  visibility: <REPLAY_VISIBLE|EVIDENCE_VISIBLE|BOTH|NEITHER>

authority:
  initiator_owned: [<bounded authority>]
  receiver_owned: [<bounded authority>]
  consumed: [<exact independent-owner authority artifact, if any>]
  excluded: [<non-owned authority>]
  authority_delegated: false
  semantic_authority_boundary: <stable boundary identity>

dependencies_and_compatibility:
  direct_dependency_or_independent_owner_contract: <exact identity>
  participant_versions: [<exact versions>]
  platform_baselines: [<exact baseline or range>]
  protocol_versions: [<applicable versions>]
  evidence_schema_versions: [<schema versions>]
  compatibility_evidence: <immutable reference and hash>

replay_and_evidence:
  replay_mode: <NOT_APPLICABLE|OPTIONAL_REFERENCE|REQUIRED_REFERENCE|DERIVED_REQUIRED_REFERENCE>
  replay_owner: PLATFORM_CORE_REPLAY
  replay_visible: <true|false>
  source_evidence: [<owner, reference, hash>]
  interaction_evidence_owner: <producer owner or NOT_APPLICABLE>
  reconstruction_owner: <owner or NOT_APPLICABLE>
  lineage_rule: <preserve source evidence by reference and hash>

failure_handling:
  rejection_conditions: [<exact fail-closed conditions>]
  cancellation_owner_and_contract: <owner/contract or NOT_APPLICABLE>
  rollback_owner_and_contract: <owner/contract or NOT_APPLICABLE>
  deterministic_recovery_rule: <rule>

evolution:
  recertification_triggers: [<trigger>]
  new_identity_triggers: [<trigger>]
  deprecation_and_retirement_rule: <lineage preservation rule>

interaction_identity_hash: <sha256 over canonical profile without this field>
```

The profile MUST be canonical JSON-serializable or equivalently canonicalized:
sorted keys, compact ASCII-safe UTF-8 JSON, normalized set-like arrays,
explicitly ordered sequences, and a `sha256:` identity hash. Duplicate
identifiers, participants, references, dependencies, or ambiguous ordering are
invalid.

## 12. Fail-closed conformance and non-goals

An interaction is not eligible for a new certification claim, lifecycle
transition, or governed availability claim when identity, participants,
ownership, authority boundary, contract, compatibility, required evidence,
Replay binding, ordering, failure behavior, or lineage is missing, ambiguous,
incompatible, or unverifiable. It MUST claim no authority transfer, execution,
approval, authorization, certification, availability, activation, or recovery
beyond existing authorized contracts.

This specification intentionally does not create a runtime interaction
validator, backfill the 47 capability profiles with interaction records, change
the Capability Registry schema, modify PCBV31 or its identity record, or
recertify current implementations. These are separate governed work; their
absence remains visible rather than inferred as completion.

## 13. Versioning

V1 is the canonical Platform Core capability interaction model established at
G52-01. A later version may clarify wording without semantic change. A change
to ownership preservation, authority isolation, deterministic contract
requirements, Replay ownership, failure behavior, compatibility, or PCBV31 and
independent-owner boundaries is a governed constitutional-policy revision and
requires explicit review. A later version MUST supersede V1 explicitly and
MUST NOT rewrite this historical artifact in place after certification.
