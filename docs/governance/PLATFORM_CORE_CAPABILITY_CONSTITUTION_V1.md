# Platform Core Capability Constitution V1

Status: CANONICAL GOVERNANCE SPECIFICATION

Version: V1

Generation: G51-01

Date: 2026-07-30

Authority: Development Governance under Human Constitutional Authority

Certified development baseline: `READY_FOR_CERTIFIED_DEVELOPMENT_BASELINE_V47`

PCBV31 identity authority:
`.github/governance/specs/PCBV31_BASELINE_IDENTITY_RECORD_V1.json`

Constitutional position: L3 governed specification defining the common
capability model without creating a new layer or authority tier

## 1. Purpose

This specification defines the constitutional identity, classification,
authority, lifecycle, dependency, evidence, compatibility, and evolution
requirements of a Platform Core capability.

It consolidates existing repository rules into one governance model. It does
not:

- create a new constitutional layer or protocol family;
- convert a runtime module into constitutional authority;
- modify PCBV31 or its authenticated historical membership;
- replace Human Authority, Governance, Approval, Authorization, Replay,
  Certification, Worker, Provider, or Human Interface ownership;
- certify, register, activate, deprecate, replace, or retire a capability by
  itself; or
- change runtime behavior.

The terms `MUST`, `MUST NOT`, `REQUIRED`, `SHALL`, `SHALL NOT`, `SHOULD`,
`SHOULD NOT`, and `MAY` are normative. Text explicitly marked
**Informational** is non-normative.

## 2. Authority and precedence

This specification is subordinate to the Constitution, Stable Constitutional
Substrate, Canonical Layer Model, Constitutional Invariants, Governance
Enforcement Hierarchy, and Human Constitutional Authority.

Conflicts are resolved in this order:

1. Constitution and constitutional invariants;
2. Stable Constitutional Substrate and canonical layer definitions;
3. independent protocol and authority contracts;
4. authenticated baseline identity records;
5. capability-specific certification evidence;
6. this common capability model;
7. implementation-local documentation.

A capability-specific contract MAY narrow a capability's scope. It MUST NOT
weaken this specification or enlarge authority beyond an upstream
constitutional owner.

## 3. Repository derivation

This model derives from the following committed evidence:

| Repository evidence | Rule derived |
|---|---|
| `docs/governance/CONSTITUTIONAL_ARCHITECTURE_SPEC_V1.md` | Constitutional control, immutable definitions, deterministic enforcement, fail-closed behavior, and Replay precedence |
| `docs/governance/CANONICAL_LAYER_MODEL.md` | Layer identity and the prohibition on silent movement of responsibility between layers |
| `docs/governance/GOVERNANCE_ENFORCEMENT_HIERARCHY.md` | Human Authority remains final; Governance constrains admissibility without becoming execution authority |
| `docs/governance/G6_05_PLATFORM_CAPABILITY_DISCOVERY_AND_REUSE_POLICY_V1.md` | Reuse, ownership verification, and evidence review precede expansion |
| `docs/governance/G15_GOVERNANCE_01_PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY.md` | Deterministic metadata-only registration, certification states, owner fields, evidence references, and non-authority boundary flags |
| `aigol/runtime/platform_capability_certification_registry.py` | Current registry fields and `DRAFT`, `VERIFIED`, `CERTIFIED`, `SUPERSEDED`, and `DEPRECATED` certification states |
| `aigol/runtime/capability_lifecycle_governance_runtime.py` | Non-authoritative candidates, explicit Human Approval for governed activation and retirement, immutable lifecycle evidence, and no executor invocation |
| `docs/governance/G20_03_PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_RUNTIME_IMPLEMENTATION.md` | Composition preserves owners and requires non-superseded certification and explicit dependency bindings |
| `docs/governance/G30_02_FIRST_POST_G29_CERTIFIED_CAPABILITY_ONBOARDING.md` | Onboarding does not acquire lifecycle, registry, selection, execution, Worker, Provider, Human Interface, or mutation authority |
| `docs/governance/G32_10B_AUTOMATIC_CONSTITUTIONAL_VALIDATOR_CONFORMANCE_AUDIT.md` | Dependency schedules reject duplicates, unknown references, self-dependencies, and cycles and use deterministic ordering |
| `aigol/runtime/transport/serialization.py` | Canonical JSON serialization and SHA-256 identity construction |
| `aigol/constitutional_validator_kernel/loaders.py` | Existing Replay binding modes and preservation of `PLATFORM_CORE_REPLAY` ownership |
| `.github/governance/specs/PCBV31_BASELINE_IDENTITY_RECORD_V1.json` | PCBV31 identity, execution-spine distinction, post-V31 capability distinction, and independent owner boundaries |

No repository evidence establishes a universal capability-dependency type
enumeration. V1 therefore defines required dependency fields and constraints,
but does not invent a dependency-type vocabulary.

## 4. Constitutional definition

### 4.1 Platform Core capability

A **Platform Core capability** is an identity-bearing, constitutionally
bounded unit of Platform Core responsibility that:

- has one declared constitutional owner;
- has one declared purpose and bounded scope;
- has one primary constitutional category;
- exposes a stable contract independently of file or module layout;
- is supported by immutable governance and certification evidence;
- declares its authority exclusions and dependencies;
- can be deterministically identified and compatibility-evaluated; and
- progresses through the lifecycle defined by this specification.

A capability is a responsibility and contract, not a source file. One
capability MAY have multiple implementation modules. One module MAY implement
multiple capabilities only when every capability retains a distinct identity,
scope, evidence binding, and lifecycle.

### 4.2 Distinctions

| Construct | Constitutional distinction |
|---|---|
| Runtime module | An implementation location. It has no constitutional identity or authority merely because it exists. |
| Protocol | A realization-independent constitutional rule family. A capability consumes or realizes protocol contracts; it does not redefine them. |
| Protocol realization | A certified implementation of a protocol. PCBV31 is the current certified reference realization of the Constitutional Execution Protocol. |
| Adapter | External or boundary-specific translation and attachment logic. It does not become Platform Core merely by calling a capability. |
| Worker | An independently owned execution participant. Capability dependency never transfers Worker lifecycle or execution authority. |
| Provider | An independently owned external-service participant. Registration in a capability index does not make a Provider a Platform Core capability. |
| Service | An implementation form or callable exposure of a capability. A service name does not create a separate capability unless responsibility and lifecycle are independently certified. |
| Implementation detail | An internal algorithm, helper, storage choice, or module split with no independent constitutional contract. |
| PCBV31 execution-spine component | An authenticated constituent of PCBV31. It is not independently a capability unless separate identity and certification evidence say so. |
| Human Interface | A transport, input-collection, and rendering owner. It does not own Platform Core semantics, workflow, governance, or Replay. |

### 4.3 PCBV31 special identity

PCBV31 MUST retain its identity as the closed V31 certified reference
realization of the Constitutional Execution Protocol. This specification
governs the Platform Core execution-capability surface exposed by PCBV31; it
does not reduce PCBV31 to an ordinary post-V31 capability.

The authenticated PCBV31 source commit, source tree, execution spine,
baseline support, certified sockets, bound independent owners, and exclusions
remain controlled exclusively by the PCBV31 Baseline Identity Record.

Changing a PCBV31 socket, execution-spine responsibility, authority boundary,
or authenticated source identity requires a new constitutional baseline. It
is not an ordinary capability evolution.

## 5. Capability taxonomy

Every capability MUST declare exactly one primary category. Secondary
descriptive facets MAY be recorded but MUST NOT grant authority.

| Primary category | Bounded responsibility | Repository-supported examples | Explicit exclusion |
|---|---|---|---|
| `EXECUTION_CAPABILITY` | Expose or realize a certified execution contract | PCBV31 execution-capability surface; certified governed execution bindings | Does not absorb Approval, Authorization, Replay, Worker, Provider, or Certification |
| `GOVERNANCE_CAPABILITY` | Produce deterministic governance classification, disposition, or admissibility evidence | Constitutional Development Governance | Does not approve, authorize, mutate, execute, or certify |
| `VALIDATION_CAPABILITY` | Analyze evidence and produce validation findings, plans, or recommendations | IVE-0 through IVE-4 and validation planning | Does not execute validation, repair automatically, approve, or authorize |
| `BOUNDARY_CAPABILITY` | Validate canonical ingress/egress and project owner-preserving state | Conversation Boundary; canonical Human Interface runtime entry | Does not own the independent services it exposes or interface rendering |
| `COORDINATION_CAPABILITY` | Route, compose, bind, supervise, or preserve continuity across certified owners | Query Router, capability composition, G42 workflow integration, G43 Supervisor, G44 Continuity Manager | Does not duplicate composed semantics or acquire downstream authority |
| `REGISTRY_CAPABILITY` | Index immutable identity, ownership, certification, or discovery metadata | Platform Capability Certification Registry and Platform Core capability lookup | Registry presence does not certify, activate, execute, approve, or authorize |
| `OBSERVATION_CAPABILITY` | Observe, trace, or reconstruct immutable evidence without changing the observed state | Replay Observation Layer and deterministic root-cause trace | Does not mutate Replay or convert observation into authorization |

The **Capability Framework** is a subsystem, not one indivisible capability.
Its certification registry and lookup surfaces classify as
`REGISTRY_CAPABILITY`; its discovery, composition, selection, and invocation
bindings classify as `COORDINATION_CAPABILITY`.

If a proposed responsibility fits more than one category, its owner MUST
identify the single primary responsibility. If no primary category can be
selected without combining independent authorities, classification MUST fail
closed and the proposal MUST return to Development Governance.

## 6. Canonical capability identity

### 6.1 Mandatory identity fields

Every certified Platform Core capability MUST have the following fields,
whether contained in one canonical profile or hash-bound across authoritative
governance artifacts.

| Field | Requirement |
|---|---|
| `capability_identifier` | Globally unique, stable, non-empty canonical identifier |
| `constitutional_owner` | Owner of the capability responsibility |
| `architectural_owner` | Owner of architectural placement |
| `implementation_owner` | Exact implementation component or bounded component set |
| `constitutional_purpose` | One responsibility stated without implementation detail |
| `capability_scope` | Explicit in-scope and out-of-scope behavior |
| `primary_category` | Exactly one category from Section 5 |
| `lifecycle_classification` | Current stage from Section 7 |
| `version_identity` | Capability contract version, distinct from implementation build identity |
| `compatibility_identity` | Supported Platform baseline, protocols, schemas, and dependency versions |
| `certification_identity` | Status, scope, milestone, version, date, verification type, and authoritative evidence |
| `replay_identity` | Replay mode, Replay owner, visibility, artifact/reference obligations, and reconstruction responsibility |
| `evidence_identity` | Evidence owner, artifact types, immutable references, hashes, and known limitations |
| `dependency_identity` | Complete direct dependency records and deterministic dependency-set hash |
| `authority_classification` | Authority owned, authority consumed, and explicit authority exclusions |
| `supersession_identity` | Predecessor, replacement, deprecation, and retirement references when applicable |
| `immutable_identity_fields` | Exact declaration of the immutable identity tuple |
| `capability_identity_hash` | Canonical hash over the complete identity profile excluding this hash field |

### 6.2 Existing and newly formalized fields

The current certification registry already records:

- capability identifier and capability owner;
- certification state, scope, milestone, evidence, date, and version;
- architectural and implementation owners;
- verification type and supersession reference;
- deterministic certification record hash; and
- boundary flags denying runtime, Human Interface, Provider, Worker, Replay
  mutation, and Governance mutation authority.

This specification makes purpose, bounded scope, primary category, lifecycle
classification, compatibility, Replay, evidence, dependency, authority, and
immutable identity declarations mandatory governance requirements. These
requirements consolidate information already distributed across capability
governance reports and runtime contracts; they do not add runtime fields to
the current registry.

### 6.3 Immutable identity tuple

The following fields are immutable for one capability identity:

- `capability_identifier`;
- `constitutional_owner`;
- `constitutional_purpose`;
- `primary_category`;
- the semantic authority boundary;
- the initial certified scope boundary; and
- the identity-generation reference.

A change to any immutable field creates a new capability identity or, where a
constitutional protocol or baseline is affected, a constitutional fork or new
Platform Core baseline.

Versions, implementation locations, dependency versions, certification
evidence, compatibility ranges, deprecation state, and replacement references
MAY evolve only through Section 12. Their historical values MUST remain
recoverable.

### 6.4 Deterministic identity

Capability profiles MUST be JSON-serializable. Identity hashing MUST use the
existing canonical serialization rule:

- keys sorted lexicographically;
- compact separators;
- ASCII-safe JSON representation;
- UTF-8 encoding; and
- SHA-256 prefixed with `sha256:`.

Ordered semantic sequences MUST declare their order. Sets represented as
arrays MUST be normalized lexicographically before hashing. Duplicate fields,
identifiers, evidence references, and dependencies are invalid.

Identical canonical profiles MUST produce identical identity hashes. Missing,
unknown, ambiguous, or non-canonical identity input MUST fail closed.

## 7. Constitutional capability lifecycle

The canonical progression is:

```text
Creation
  -> Registration
  -> Certification
  -> Availability
  -> Evolution
  -> Deprecation
  -> Replacement
  -> Retirement
```

Evolution MAY return an evolved version to Certification. Deprecation MAY
proceed directly to Retirement when no replacement is constitutionally
necessary. No transition erases prior evidence.

The lifecycle stage is distinct from certification state. Current registry
states (`DRAFT`, `VERIFIED`, `CERTIFIED`, `SUPERSEDED`, `DEPRECATED`) remain
certification metadata. Existing lifecycle artifacts
(`CAPABILITY_CANDIDATE_CREATED`, `CAPABILITY_ACTIVE`, and
`CAPABILITY_RETIRED`) remain operational evidence. Neither vocabulary alone
replaces the constitutional lifecycle.

### 7.1 Lifecycle responsibility matrix

| Stage | Owner | Required evidence | Required validation | Constitutional constraints | Compatibility guarantee |
|---|---|---|---|---|---|
| Creation | Development Governance for classification; proposed constitutional owner for content; Human Authority where constitutional judgment is required | CDD classification, Need Assessment, owner, purpose, scope, category, authority exclusions, dependency proposal, and non-authoritative candidate | Reuse/duplication review, identity completeness, authority-conflict review, dependency review | Candidate is non-authoritative; no registration, certification, availability, execution, mutation, or self-approval | No effect on existing capabilities or baselines |
| Registration | Platform Core registry owner | Immutable draft identity profile and source evidence references | Unique identifier, canonical hash, owner existence, exact fields, evidence reference existence | Registration is metadata only; `DRAFT` is not certification or availability | Existing registry queries and records remain unchanged |
| Certification | Independent Certification owner for the certification disposition; Governance for assessment; Human Authority where required | Validation results, governance assessment, compatibility evidence, Replay/evidence profile, known limitations, certification report | Scope-appropriate deterministic tests, evidence authentication, authority and dependency conformance, fail-closed checks | Capability owner cannot self-certify; missing evidence fails closed | Certified scope and supported baselines are exact, not inferred |
| Availability | Capability lifecycle/selection owner using certification and any required Human activation evidence | Non-superseded certification, compatible dependency set, active/availability evidence where the governing contract requires it | Certification status, lifecycle status, dependency availability, compatibility, approval binding when required | Discovery does not imply availability; availability does not authorize a particular execution; no bypass of Approval or Authorization | Only declared compatible consumers may select the capability |
| Evolution | Existing constitutional owner under Development Governance | Change classification, preserved identity fields, version delta, compatibility and migration analysis, updated dependencies/evidence | Scope, authority, Replay, dependency, baseline, and regression impact review | No silent immutable-field change; no historical evidence rewrite; recertification rules apply | Compatible versions preserve certified contracts or declare exact break |
| Deprecation | Constitutional owner with Governance disposition | Deprecation reason, affected consumers, replacement status, migration window, availability restriction | Dependency and consumer impact analysis, evidence continuity, no-new-use enforcement where applicable | Deprecation does not delete or rewrite evidence and does not itself transfer authority | Existing supported use is explicit and time/version bounded |
| Replacement | New and predecessor owners with Governance; Human Authority where authority boundaries change | New identity/certification, predecessor link, `superseded_by`, migration and equivalence evidence, residual-gap record | Replacement certification, compatibility, dependency rewiring, authority non-transfer review | Replacement must be explicit; name reuse and implicit inheritance are forbidden | Consumers can deterministically distinguish predecessor and replacement |
| Retirement | Existing owner plus explicit Human Approval where the governing lifecycle contract requires it | Retirement candidate, approval when required, terminal lifecycle artifact, dependency clearance, final evidence index | No remaining required dependents, terminal hash/reconstruction, registry/availability consistency | No execution or new selection; evidence and identity remain immutable and discoverable | Historical Replay and certification remain reconstructable |

### 7.2 Transition rules

A transition MUST:

- consume the prior stage's immutable identity and hash;
- identify its actor and owner;
- declare the exact transition and timestamp;
- preserve prior evidence by reference rather than replacement;
- validate all mandatory inputs before producing the next state; and
- fail closed without side effects when validation is incomplete.

Stage skipping is prohibited except:

- a failed or rejected creation terminates without Registration;
- a deprecated capability with no justified replacement may proceed to
  Retirement; and
- a capability version may return from Evolution to Certification before
  renewed Availability.

## 8. Authority model

### 8.1 Authority a capability may own

A capability MAY own only the responsibility explicitly declared by its
purpose, scope, primary category, and certification. Examples include:

- deterministic semantic transformation;
- bounded governance classification;
- validation analysis or recommendation;
- canonical boundary projection;
- owner-preserving routing or composition;
- metadata registration and lookup; or
- read-only observation and reconstruction.

Possession of an output artifact does not grant downstream authority.

### 8.2 Authority that cannot be silently acquired

No ordinary capability may silently acquire:

- Human Constitutional Authority;
- constitutional amendment authority;
- Governance authority outside its declared scope;
- Human Approval decision authority;
- mutation or execution Authorization authority;
- Replay protocol ownership or Replay mutation authority;
- Certification authority over itself;
- Worker selection, assignment, dispatch, invocation, or lifecycle authority;
- Provider selection, credential, invocation, or lifecycle authority;
- Human Interface semantic, workflow, or governance authority;
- PCBV31 execution-spine ownership; or
- another capability's semantic responsibility.

Any proposed transfer of one of these responsibilities is a constitutional
change, not a dependency or implementation detail.

### 8.3 Owner interaction matrix

| Owner/boundary | Capability interaction rule |
|---|---|
| PCBV31 | A capability may use certified sockets and contracts. It MUST NOT alter the authenticated V31 identity, spine, or behavior through ordinary capability evolution. |
| Replay | Replay owns Replay protocol semantics. A capability produces or references Replay-visible evidence under an explicit binding; it cannot delegate, mutate, or replace Replay ownership. |
| Approval | A capability may prepare an approval candidate or consume an exact approved artifact where its contract permits. It cannot infer, create, or bypass Human Approval. |
| Authorization | A capability may request or consume exact bounded authorization. It cannot self-authorize or broaden an authorization scope. |
| Worker | A capability may produce a certified request for an existing Worker owner. Dependency or invocation does not transfer Worker lifecycle authority. |
| Provider | A capability may use a certified Provider contract. It does not own Provider selection, credentials, transport, or lifecycle unless independently classified under Provider authority, outside Platform Core capability ownership. |
| Human Interface | A capability may expose presentation-neutral state. Interfaces capture and render; they do not own capability semantics, governance, or Replay. |
| Conversation Boundary | The boundary validates events, restores Platform Core state, delegates to existing owners, and projects results. It does not absorb those owners. |
| Development Governance | Development Governance classifies work, assesses need, preserves ownership, and issues bounded dispositions. It does not approve, authorize, implement, execute, validate on behalf of validators, or certify. |
| Certification | Certification evaluates exact scope and evidence independently. Capability ownership and registry presence do not create certification authority. |

## 9. Dependency model

### 9.1 Mandatory dependency identity

Each direct dependency record MUST contain:

- dependency capability or independent-owner identifier;
- dependency constitutional owner;
- required or optional classification;
- exact purpose of the dependency;
- supported version or compatibility constraint;
- required certification/lifecycle state;
- consumed contract or artifact identity;
- immutable evidence reference and hash where applicable; and
- an explicit statement that authority is not delegated.

The complete direct dependency list MUST be normalized deterministically and
hash-bound into the capability identity. Transitive dependencies MUST be
derivable from direct profiles; they MUST NOT be hidden.

### 9.2 Allowed dependencies

A dependency is allowed only when:

- it references a known identity and owner;
- it is necessary to the declared purpose;
- its contract and compatibility are explicit;
- required dependencies are certified and available for the consuming use;
- ownership and authority remain with the dependency owner;
- evidence lineage is immutable and reconstructable where required; and
- removal or failure produces a declared fail-closed result.

Optional dependencies MUST have a deterministic no-dependency behavior and
MUST NOT become an undeclared authority path.

### 9.3 Forbidden dependencies

The following are forbidden:

- unknown, ambiguous, duplicate, or self dependencies;
- constitutional dependency cycles;
- dependency on a mutable branch, unversioned alias, or file path as the sole
  constitutional identity;
- dependency on uncertified behavior for certified availability;
- hidden transitive dependencies;
- authority transfer through invocation, data flow, import, composition, or
  shared storage;
- delegation of Replay or Certification authority;
- dependency-based bypass of Approval, Authorization, Governance, Worker,
  Provider, or Human Interface boundaries; and
- a dependency whose failure is silently ignored when it is required.

### 9.4 Acyclicity

The constitutional dependency graph MUST be a directed acyclic graph.
Validation MUST reject duplicate nodes or edges, unknown nodes,
self-dependencies, and cycles. Ready-node and dependent traversal MUST be
lexically deterministic.

Execution authority does not flow across a dependency edge. Replay authority
and Certification authority cannot be delegated. A dependency communicates
only the exact contract, evidence, or bounded service declared in its profile.

## 10. Replay model

Every capability MUST declare one existing Replay binding mode:

- `NOT_APPLICABLE`;
- `OPTIONAL_REFERENCE`;
- `REQUIRED_REFERENCE`; or
- `DERIVED_REQUIRED_REFERENCE`.

Every Replay binding MUST declare:

- `replay_visible`;
- `replay_owner`, which remains `PLATFORM_CORE_REPLAY`;
- required artifact/reference and hash fields;
- lineage relationship;
- deterministic reconstruction responsibility; and
- behavior when Replay evidence is missing or invalid.

Rules:

- `NOT_APPLICABLE` MUST NOT carry a Replay reference.
- `REQUIRED_REFERENCE` and `DERIVED_REQUIRED_REFERENCE` MUST carry an
  immutable Replay reference and hash.
- A capability that changes governed state or makes a replay-relevant
  deterministic decision MUST be Replay-visible.
- A capability that wraps evidence MUST preserve source evidence unchanged
  and bind by reference and hash.
- Reconstruction MUST validate hashes, ordering, identity, lineage, and
  compatibility before returning state.
- Replay evidence is historical evidence, not approval, authorization,
  certification, or execution permission.

## 11. Evidence and audit model

Every capability MUST define an evidence contract containing:

- evidence owner;
- supported artifact types and schema versions;
- immutable artifact identifiers, references, and hashes;
- source capability and version;
- source Platform baseline;
- certification scope and evidence references;
- validation performed and exact results;
- authority and boundary flags;
- dependency and compatibility evidence;
- known limitations and explicitly unverified requirements;
- supersession/deprecation/retirement lineage; and
- reconstruction or authentication procedure.

Evidence MUST be deterministic, audit-traceable, immutable where its layer
requires immutability, and owned by the component that produced it.

Capabilities MUST reference authoritative source artifacts rather than embed
duplicate copies. Composition evidence MAY bind multiple owners, but it MUST
not replace their source evidence.

Evidence absence, hash mismatch, unsupported schema, owner mismatch, scope
mismatch, ambiguous supersession, or incomplete lineage MUST fail closed.

## 12. Compatibility and evolution model

### 12.1 Compatibility identity

Every capability MUST declare compatibility with:

- exact Platform Core baseline or bounded baseline range;
- applicable constitutional protocol versions;
- input and output artifact schemas;
- direct dependency versions;
- certified sockets or integration contracts;
- Replay and evidence schema versions; and
- supported predecessor/replacement relationships.

Compatibility MUST be proved, not inferred from matching names or successful
imports. Unknown compatibility fails closed.

### 12.2 Evolution decisions

| Change | Required disposition |
|---|---|
| Internal implementation change with identical identity, contract, authority, dependencies, Replay, evidence, and compatibility | Same capability version line; validation proportionate to touched surface |
| Compatible contract or implementation evolution | New capability version and recertification of affected scope |
| Dependency, evidence, Replay, compatibility, or certified-scope change | New capability version and recertification |
| Constitutional owner, purpose, primary category, or semantic authority boundary change | New capability identity |
| Incompatible but legitimate continuation with preserved historical lineage | Explicit replacement or constitutional fork |
| Constitution, protocol-family semantics, cross-owner authority, PCBV31 spine/socket, or authenticated baseline identity change | Constitutional review and new Platform Core baseline where approved |

### 12.3 New capability test

A new capability is required when responsibility has:

- a constitutionally distinct purpose;
- an independently lifecycle-managed owner or scope;
- a distinct authority boundary;
- a separately selectable or composable contract; or
- evidence and compatibility obligations that cannot be represented as a
  version of the existing capability.

Module extraction, naming preference, alternate language, performance tuning,
and adapter-specific implementation do not by themselves create a capability.

### 12.4 Fork and baseline rules

A constitutional fork is required when two incompatible meanings or authority
models must coexist and neither can truthfully supersede the other.

A new Platform Core baseline is required only when approved evolution changes
a baseline-level constitutional identity, protocol realization, authority
boundary, PCBV31 certified socket or spine, or another foundational
cross-capability invariant. Adding or evolving a bounded post-V31 capability
does not by itself create a new PCBV31 or Platform Core baseline.

### 12.5 Deprecation, replacement, and retirement

Deprecation MUST identify affected consumers and whether a replacement exists.
Replacement MUST use a new identity when immutable identity fields differ and
MUST bind predecessor and replacement evidence in both directions where the
artifacts permit.

Retirement MUST:

- prevent new availability and selection;
- preserve all historical identity, evidence, certification, and Replay
  lineage;
- prove that no required active dependency remains; and
- retain a deterministic terminal record.

Retirement is not deletion.

## 13. Canonical capability template

Every new capability and every existing capability at its next constitutional
lifecycle transition MUST provide the following profile. Current certified
capabilities remain governed by their existing authoritative evidence until
such a transition; this compatibility rule does not expand their scope or
waive missing evidence.

```yaml
artifact_type: PLATFORM_CORE_CAPABILITY_PROFILE_V1
profile_version: V1

constitutional_identity:
  capability_identifier: <stable identifier>
  identity_generation: <generation or baseline>
  constitutional_owner: <owner>
  architectural_owner: <owner>
  implementation_owner:
    - <exact component>
  constitutional_purpose: <one bounded responsibility>
  primary_category: <one category from Section 5>
  immutable_identity_fields:
    - capability_identifier
    - constitutional_owner
    - constitutional_purpose
    - primary_category
    - semantic_authority_boundary
    - initial_certified_scope
    - identity_generation

scope:
  in_scope:
    - <responsibility>
  out_of_scope:
    - <explicit non-responsibility>
  initial_certified_scope: <scope identity>

authority:
  owned:
    - <bounded authority>
  consumed:
    - owner: <independent owner>
      contract: <exact contract>
  excluded:
    - <authority never owned>
  semantic_authority_boundary: <stable boundary identity>

lifecycle:
  lifecycle_classification: <Creation|Registration|Certification|Availability|Evolution|Deprecation|Replacement|Retirement>
  prior_state_reference: <immutable reference or NOT_APPLICABLE>
  prior_state_hash: <sha256 hash or NOT_APPLICABLE>
  transition_owner: <owner>
  transition_evidence: <immutable reference>
  replacement_identifier: <identifier or NOT_APPLICABLE>

version_identity:
  capability_version: <version>
  implementation_version: <version>
  schema_versions:
    - <schema>

compatibility_identity:
  platform_baselines:
    - <exact baseline or bounded range>
  protocol_versions:
    - <protocol and version>
  certified_sockets:
    - <socket identity or NOT_APPLICABLE>
  input_schemas:
    - <schema>
  output_schemas:
    - <schema>

certification_identity:
  certification_status: <registry-supported state>
  certification_scope: <registry-supported scope>
  certification_milestone: <milestone>
  certification_version: <version>
  certification_date: <date>
  verification_type: <type>
  authoritative_evidence:
    - reference: <immutable reference>
      hash: <sha256 hash>

replay_identity:
  mode: <NOT_APPLICABLE|OPTIONAL_REFERENCE|REQUIRED_REFERENCE|DERIVED_REQUIRED_REFERENCE>
  replay_visible: <true|false>
  replay_owner: PLATFORM_CORE_REPLAY
  artifact_types:
    - <type or NOT_APPLICABLE>
  reconstruction_owner: <owner or NOT_APPLICABLE>
  fail_closed_condition: <condition>

evidence_identity:
  evidence_owner: <owner>
  artifact_types:
    - <type>
  evidence_references:
    - reference: <immutable reference>
      hash: <sha256 hash>
  known_limitations:
    - <limitation or NONE>

dependencies:
  - dependency_identifier: <identifier>
    constitutional_owner: <owner>
    required: <true|false>
    purpose: <bounded purpose>
    compatibility: <exact version/range>
    required_state: <state>
    consumed_contract: <contract>
    evidence_reference: <reference>
    evidence_hash: <sha256 hash>
    authority_delegated: false

evolution:
  compatible_change_rule: <rule>
  recertification_triggers:
    - <trigger>
  new_identity_triggers:
    - <trigger>
  deprecation_rule: <rule>
  retirement_rule: <rule>

dependency_set_hash: <sha256 hash>
capability_identity_hash: <sha256 hash over the profile without this field>
```

An implementation MAY serialize this profile in JSON or another canonical
governance artifact, provided all fields, ordering, and hash semantics remain
equivalent. The template is not a runtime registry schema change.

## 14. Representative conformance assessment

| Capability or subsystem | Primary classification | Existing identity/evidence | Constitutional assessment |
|---|---|---|---|
| PCBV31 execution-capability surface | `EXECUTION_CAPABILITY` with separate protocol-realization identity | PCBV31 Baseline Identity Record; G31 governance chain | Conforms. This specification does not change PCBV31 membership, sockets, spine, or independent owners. |
| Conversation Boundary | `BOUNDARY_CAPABILITY` | G17-HI-02B certified specification; `aigol/runtime/platform_core_conversation_boundary.py`; G49-02 tests | Conforms in responsibility and boundary behavior. A current G15 registry record for the G49 realization was not located; registration-profile completion is required at its next lifecycle transition. |
| Constitutional Development Governance | `GOVERNANCE_CAPABILITY` | `CONSTITUTIONAL_DEVELOPMENT_GOVERNANCE` registry record; `docs/governance/G47_FINAL_CONSTITUTIONAL_CLOSURE_REPORT.md` | Conforms. It is a pre-planning barrier and does not absorb Planning, Approval, Authorization, Replay, or execution. |
| Intelligent Validation Engine | `VALIDATION_CAPABILITY` | IVE-0 through IVE-4 registry records and G36-G41 certification evidence | Conforms. It plans, recommends, analyzes, and reconstructs; it does not execute validation or repair. |
| Capability Framework registry and lookup | `REGISTRY_CAPABILITY` | G15 registry report and runtime; Platform Core capability lookup | Conforms. Metadata is deterministic and non-authoritative. |
| Capability Framework composition, selection, and invocation bindings | `COORDINATION_CAPABILITY` | G20, G28, and G29 registry/evidence chain | Conforms. Composition preserves source ownership and explicit certified dependencies. |
| Unified Platform Query Router | `COORDINATION_CAPABILITY` | `UNIFIED_PLATFORM_QUERY_ROUTER` registry record and G19-04 evidence | Conforms. Routing is deterministic and delegates to existing service owners. |
| G42 Workflow Integration | `COORDINATION_CAPABILITY` | G42 registry record and certification evidence | Conforms. It adopts IVE planning without changing validation execution or authority. |
| G43 Supervisor | `COORDINATION_CAPABILITY` | G43 registry record and certification evidence | Conforms. Diagnosis is read-only and does not repair or execute. |
| G44 Continuity Manager | `COORDINATION_CAPABILITY` | G44 registry record and certification evidence | Conforms. Checkpoint and resume evidence preserve owner boundaries. |
| Replay Observation Layer | `OBSERVATION_CAPABILITY` | `REPLAY_OBSERVATION_LAYER` registry record and G15-01 evidence | Conforms only under independent Replay ownership; observation does not delegate or replace Replay authority. |
| Provider Platform registry entry | Not a Platform Core capability when `architectural_owner` is `PROVIDER_PLATFORM` | `PROVIDER_PLATFORM_OPERATIONAL_COMPLETION` registry record | Correctly excluded from Platform Core capability ownership. The shared registry indexes bound certification metadata without changing Provider identity. |

The assessment demonstrates that the common model can classify representative
current capabilities without moving responsibility. It does not claim that
every historical capability already has one materialized V1 profile; current
identity fields remain distributed across authoritative registry and
governance evidence.

## 15. Fail-closed conformance policy

A capability is not eligible for new certification or a lifecycle transition
when any of the following is unresolved:

- identity, owner, purpose, scope, or category ambiguity;
- missing authoritative evidence;
- unknown or incompatible dependency;
- dependency cycle;
- authority overlap or silent transfer;
- unsupported Replay mode or incomplete Replay binding;
- missing compatibility declaration;
- hash, reference, ordering, or reconstruction mismatch;
- ambiguous supersession or retirement state;
- unverified required validation; or
- conflict with PCBV31 or an independent protocol owner.

Failure MUST produce no certification, availability, activation, execution,
mutation, replacement, or retirement claim.

## 16. Governance integration and non-goals

Development Governance owns classification and application of this
specification to proposed work. It does not acquire capability implementation,
Approval, Authorization, Replay, execution, or Certification authority.

The Platform Capability Certification Registry remains a metadata-only index.
This specification does not modify its schema or claim that registry presence
is sufficient for constitutional availability.

This specification intentionally does not:

- create a runtime profile validator;
- backfill registry records;
- register G49-02;
- bind the existing capability lifecycle runtime to the certification
  registry;
- add a `RETIRED` certification state;
- implement dependency-graph validation for every historical capability;
- recertify any current capability; or
- establish a new Platform Core baseline.

Those are separate governed implementation or certification questions. Their
absence does not authorize inferred state.

## 17. Versioning

V1 is the canonical capability-governance model derived at G51-01.

A revision MAY clarify wording without changing semantics. A change to
mandatory identity, lifecycle ordering, authority boundaries, dependency
acyclicity, Replay ownership, certification independence, or baseline rules is
a governed constitutional-policy revision and requires explicit review.

Historical capability evidence remains immutable. A later version of this
specification MUST reference and supersede V1 explicitly; it MUST NOT rewrite
V1 in place after certification.
