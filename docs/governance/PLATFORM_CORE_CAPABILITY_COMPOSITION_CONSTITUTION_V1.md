# Platform Core Capability Composition Constitution V1

Status: CANONICAL GOVERNANCE SPECIFICATION

Version: V1

Generation: G52-02

Date: 2026-07-30

Authority: Development Governance under Human Constitutional Authority

Certified development baseline: `READY_FOR_CERTIFIED_DEVELOPMENT_BASELINE_V47`

Prerequisites:

- `PLATFORM_CORE_CAPABILITY_CONSTITUTION_ESTABLISHED`
- `PLATFORM_CORE_CAPABILITY_REGISTRY_ESTABLISHED`
- `PLATFORM_CORE_CAPABILITY_INTERACTION_CONSTITUTION_ESTABLISHED`

Constitutional position: L3 governed specification defining the common
composition model for Platform Core capabilities. It creates neither a
constitutional layer, authority tier, protocol family, nor execution path.

## 1. Purpose and scope

This specification establishes the canonical, deterministic, owner-preserving
model for composing multiple Platform Core capabilities into a higher-level
Platform Core service or workflow.

It does not modify runtime behavior, PCBV31, Replay, Approval, Authorization,
Workers, Providers, Human Interface, or Conversation Boundary runtime; create
a runtime composition engine or composition registry schema; grant authority;
or certify a capability or composition by itself.

The terms `MUST`, `MUST NOT`, `REQUIRED`, `SHALL`, `SHALL NOT`,
`SHOULD`, `SHOULD NOT`, and `MAY` are normative. Text explicitly marked
**Informational** is non-normative.

## 2. Authority and repository derivation

This specification is subordinate to the Constitution, Stable Constitutional
Substrate, Canonical Layer Model, Constitutional Invariants, Governance
Enforcement Hierarchy, independent protocol contracts, authenticated PCBV31
identity, and Human Constitutional Authority. Conflicts are resolved in that
order, then by the Capability Constitution, Interaction Constitution,
capability-specific authoritative evidence, this specification, and local
implementation documentation.

| Repository evidence | Composition rule derived |
|---|---|
| `docs/governance/PLATFORM_CORE_CAPABILITY_CONSTITUTION_V1.md`, Sections 5, 8-12 | Coordination preserves source owners; dependencies are explicit, acyclic, compatible, evidence-bound, and non-delegating; compatibility and Replay changes require recertification. |
| `docs/governance/PLATFORM_CORE_CAPABILITY_INTERACTION_CONSTITUTION_V1.md` | Composition uses owner-preserving interactions; no interaction edge transfers execution, Replay, approval, authorization, certification, or other constitutional authority. |
| `docs/governance/G20_02_PLATFORM_CAPABILITY_COMPOSITION_DISCOVERY_AUDIT.md` | A composition must identify the complete set of certified capabilities, dependencies, evidence requirements, remaining gaps, and smallest bounded extension; manual assembly alone is not a canonical composition. |
| `docs/governance/G20_03_PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_RUNTIME_IMPLEMENTATION.md` | Composition is bounded and read-only, requires non-superseded certification and explicit dependency bindings, produces deterministic coverage/evidence/hashes, and preserves ownership. |
| `docs/governance/G19_04_UNIFIED_PLATFORM_QUERY_ROUTER_IMPLEMENTATION.md` | Router composition selects and exposes existing owners through deterministic descriptors; missing required evidence yields no invocation and no authority acquisition. |
| `docs/governance/G15_01_REPLAY_OBSERVATION_LAYER_V1.md` | Replay remains source evidence; composition or observation does not modify source Replay. |
| `.github/governance/specs/PCBV31_BASELINE_IDENTITY_RECORD_V1.json` | Bound independent owners and later capabilities are not absorbed into PCBV31 by invocation, evidence exchange, or lifecycle dependency. |

No reviewed evidence establishes a universal runtime composition registry,
composition lifecycle runtime, cross-composition rollback protocol, or a rule
that every capability group is a separately certified service. V1 makes these
gaps explicit and does not invent them.

## 3. Constitutional composition definition and distinctions

A **Platform Core capability composition** is a declared, deterministic,
bounded arrangement of two or more identified capabilities and/or independent
owner contracts that provides one higher-level service or workflow contract
while preserving every constituent's constitutional identity, owner, evidence,
authority boundary, lifecycle, and Replay ownership.

A composition owns only its arrangement: selection/order, declared composition
contract, binding evidence, compatibility disposition, and composition-produced
result or gap evidence. It never owns constituent semantic results, source
evidence, protocol state, or authority merely because it composes them.

| Construct | Constitutional distinction |
|---|---|
| Capability | An identity-bearing bounded responsibility with its own owner, lifecycle, authority, evidence, and compatibility profile. A composition does not merge its constituents into one capability. |
| Interaction | One bounded exchange between identified owners. A composition declares a compatible set and deterministic arrangement of interactions; an interaction alone is not a composition. |
| Composition | A higher-level owner-preserving arrangement of multiple participants to satisfy one bounded service or workflow contract. |
| Coordination | A primary capability category. A composition may be realized by a separately certified `COORDINATION_CAPABILITY` only when it satisfies the Capability Constitution new-capability test. |
| Workflow | A declared ordered or conditionally ordered use of contracts. It is a composition only when it has multiple identified participants and a composition contract. |
| Service | A callable or exposed form. A service name does not create a composition identity without independently certified composition responsibility and evidence. |
| Dependency graph | The declared prerequisite graph. It constrains admissible composition but does not prove that a composition occurred. |
| Execution | Existing protocol-owned execution. A composition may bind a certified execution socket only through its existing contract; it does not become execution authority or change PCBV31. |
| Implementation detail | Module layout, helper call, orchestration code, or storage with no independently declared composition contract. |

## 4. Composition ownership and authority boundaries

### 4.1 Ownership

A composition MUST identify a composition owner responsible only for the
composition contract, participant binding, deterministic arrangement,
composition evidence, compatibility evaluation, and declared outcome or gap.
Every constituent retains ownership of its own purpose, data semantics,
decisions, evidence, lifecycle, state, and authority.

The composition MUST reference constituent evidence by immutable reference and
hash. It MUST NOT rewrite, embed as replacement, relabel, or claim ownership
of constituent source evidence. It owns only a newly produced binding,
coverage, routing, workflow, or residual-gap artifact.

A composition may consume an exact independent-owner contract where declared.
It MUST NOT make an independent owner—including Replay, Approval,
Authorization, Certification, a Worker, a Provider, or Human Interface—a
constituent Platform Core capability by composition alone.

### 4.2 Authority

A composition is authority-preserving coordination. It MUST declare
`authority_delegated: false` for every participant relationship. It cannot
transfer or silently acquire Human Constitutional Authority, constitutional
amendment authority, execution authority, Replay ownership or mutation,
Approval decision authority, Authorization authority, Certification authority,
PCBV31 execution-spine ownership, Worker or Provider selection/lifecycle
authority, or Human Interface semantic/workflow/governance authority.

A composition request, result, composition artifact, successful routing, or
shared data flow does not confer authority. No cyclic authority propagation can
exist: an authority-delegation edge, whether direct or multi-composition, is
invalid and MUST fail closed.

## 5. Composition contract and determinism

Every new composition type and every existing composition at its next
constitutional lifecycle transition MUST have a deterministic composition
contract. It MUST declare:

- one stable composition identifier, purpose, category, owner, scope, and
  explicit non-goals;
- the ordered participant set, each participant's identity/version/owner, and
  direct dependency or independent-owner contract;
- each interaction or workflow binding, its initiating and receiving owners,
  request/response contract, admissibility condition, and success/fail-closed
  outcome;
- deterministic selection, ordering, branching, duplicate handling, and
  no-participant/no-coverage behavior;
- composition result ownership, source evidence references/hashes, residual-gap
  ownership, and visibility;
- compatibility, certification/lifecycle requirements, Replay mode, evidence
  schemas, failure, cancellation, and recovery constraints; and
- the exact canonicalization and identity-hash rule.

Participant order is semantically significant only where declared. Independent
or set-like participant collections MUST be normalized lexically before
hashing. Unknown, duplicate, self-referential, unavailable, superseded,
uncertified, incompatible, cyclic, or ambiguous required participants or
bindings MUST fail closed.

A composition may be a separately selectable service only if it meets the
Capability Constitution new-capability test: a distinct purpose, independently
lifecycle-managed scope or owner, distinct authority boundary, separately
selectable/composable contract, or evidence/compatibility obligations not
representable as a version of an existing capability. A mere convenience
wrapper, route alias, module extraction, or call sequence is not a new
capability or composition identity.

## 6. Composition lifecycle and identity

Composition lifecycle uses the canonical Capability Constitution progression:
Creation, Registration, Certification, Availability, Evolution, Deprecation,
Replacement, and Retirement. This does not create a parallel lifecycle.

- At Creation, Development Governance classifies the proposed composition,
  confirms reuse and non-duplication, identifies owner, scope, participants,
  authorities excluded, and residual gaps. It is non-authoritative.
- At Registration, a composition identity/profile may be indexed as metadata;
  registration is not certification, availability, execution, or authority.
- At Certification and Availability, every required participant and binding
  must be compatible, available where required, non-superseded, evidence-bound,
  and independently certified to the required scope. Composition certification
  assesses only the arrangement and outcome contract; it does not recertify or
  replace constituents.
- Evolution, deprecation, replacement, and retirement preserve all historical
  constituent, composition, certification, and Replay lineage. Replacement
  must be explicit and cannot inherit authority by name reuse.

A composition identity is immutable for its identifier, constitutional purpose,
composition owner, primary category, semantic authority boundary, initial
certified scope, identity generation, and declared participant-role meaning.
A participant version, compatible binding, evidence, Replay binding, or scope
change requires a new composition version and affected-scope recertification.
A change to immutable identity requires a new composition identity. PCBV31
spine/socket or independent protocol authority changes require constitutional
review and, where approved, a new Platform Core baseline.

## 7. Evidence, Replay, and compatibility

Every composition MUST define immutable, audit-traceable evidence for its
identity, participants, source precedence, dependency/binding graph,
deterministic arrangement, compatibility disposition, outcome/gap status,
source and produced artifact references/hashes, validation results, known
limitations, supersession, and reconstruction procedure.

Composition evidence is a binding layer. It may bind multiple source owners but
MUST NOT replace their authoritative source artifacts. Evidence absence, hash
mismatch, schema/owner/scope mismatch, incomplete lineage, or ambiguity fails
closed.

Every composition MUST declare one existing Replay mode:
`NOT_APPLICABLE`, `OPTIONAL_REFERENCE`, `REQUIRED_REFERENCE`, or
`DERIVED_REQUIRED_REFERENCE`; its Replay visibility; source/derived
references and hashes; ordering; reconstruction owner; and missing/invalid
evidence behavior. A composition that makes a replay-relevant deterministic
decision or governed state transition MUST be Replay-visible.
`PLATFORM_CORE_REPLAY` remains the sole Replay owner. Composition evidence is
not execution permission, approval, authorization, or certification.

Compatibility must be proved, never inferred from matching names, successful
imports, or a completed call. It includes Platform Core baseline, applicable
protocols, participant identities/versions, direct dependencies, input/output
and evidence schemas, certified sockets, certification/lifecycle states,
Replay/evidence schema versions, and predecessor/replacement relations.

## 8. Failure, cancellation, rollback, and recovery

A composition fails when any required participant, binding, evidence, schema,
compatibility, ordering, certification/lifecycle state, Replay obligation, or
authority boundary is missing, invalid, ambiguous, or incompatible. A failed
required composition MUST return its defined fail-closed outcome or residual
gap; it MUST NOT select an alternate participant, degrade a required binding,
or claim full coverage without an explicit certified composition contract.

Cancellation may be initiated only by an actor and owner contract authorized to
cancel the relevant composition/workflow. A composition cannot infer
cancellation authority from transport, request possession, timeout, or a
constituent response.

This specification establishes no universal composition rollback. A composition
may invoke rollback only through an existing certified owner contract and may
roll back only composition-owned binding state. It cannot roll back constituent,
Replay, Approval, Authorization, Worker, Provider, or PCBV31 state by
implication. Recovery preserves original evidence and uses a declared
deterministic retry/reconstruction rule; a retry creates a new occurrence and
does not overwrite historical lineage.

## 9. Prohibited composition patterns

The following are constitutionally forbidden:

- absorbing or relabeling constituent ownership, evidence, lifecycle, or
  semantic responsibility;
- authority transfer by composition, interaction, invocation, data flow,
  routing, shared storage, or result possession;
- treating registry presence, discovery, a successful import, or a route match
  as certification, availability, compatibility, or authority;
- hidden, duplicate, self, cyclic, superseded, uncertified, or incompatible
  required participants or dependencies;
- nondeterministic participant selection, order, branching, fallback, or
  residual-gap handling;
- silently substituting a Provider, Worker, Approval, Authorization, Replay,
  Certification, Human Interface, or execution owner;
- creating a general execution, Approval, Authorization, Certification, or
  Replay authority through coordination;
- changing PCBV31 identity, socket, spine, behavior, or independent owners;
- treating composition evidence as a substitute for source evidence or as
  execution permission; and
- declaring a new service/capability merely to duplicate an existing certified
  composition or implementation detail.

## 10. Canonical composition template

Every new composition type and every existing composition at its next
constitutional lifecycle transition MUST provide an equivalent canonical
governance profile. This template is not a runtime registry schema change.

```yaml
artifact_type: PLATFORM_CORE_CAPABILITY_COMPOSITION_PROFILE_V1
profile_version: V1

composition_identity:
  composition_identifier: <globally unique stable identifier>
  identity_generation: <generation or baseline>
  composition_owner: <owner>
  constitutional_purpose: <one bounded higher-level responsibility>
  primary_category: COORDINATION_CAPABILITY
  immutable_identity_fields:
    - composition_identifier
    - composition_owner
    - constitutional_purpose
    - primary_category
    - semantic_authority_boundary
    - initial_certified_scope
    - identity_generation
    - participant_role_meanings

scope:
  in_scope: [<bounded responsibility>]
  out_of_scope: [<explicit non-responsibility>]
  initial_certified_scope: <scope identity>

participants:
  ordered_bindings:
    - participant_identifier: <capability or independent owner>
      participant_version: <exact version>
      constitutional_owner: <owner>
      role: <bounded role>
      required: <true|false>
      dependency_or_owner_contract: <exact identity>
      interaction_contract: <exact identity or NOT_APPLICABLE>
      certification_lifecycle_requirement: <state>
      source_evidence: <reference and sha256 hash>
      authority_delegated: false

arrangement:
  selection_rule: <deterministic rule>
  ordering_rule: <deterministic rule>
  branching_rule: <deterministic rule or NOT_APPLICABLE>
  no_coverage_behavior: <fail-closed/residual-gap rule>
  composition_result_owner: <owner>
  residual_gap_owner: <owner or NOT_APPLICABLE>

authority:
  owned: [<composition-only authority>]
  consumed: [<exact independent-owner contract if any>]
  excluded: [<non-owned authority>]
  semantic_authority_boundary: <stable identity>
  authority_delegated: false

lifecycle_and_compatibility:
  lifecycle_classification: <canonical lifecycle stage>
  certification_status: <registry-supported status>
  platform_baselines: [<baseline/range>]
  protocol_versions: [<protocol/version>]
  input_output_schemas: [<schema/version>]
  evidence_schema_versions: [<schema/version>]
  certified_sockets: [<socket or NOT_APPLICABLE>]
  compatibility_evidence: <reference and sha256 hash>

replay_and_evidence:
  replay_mode: <NOT_APPLICABLE|OPTIONAL_REFERENCE|REQUIRED_REFERENCE|DERIVED_REQUIRED_REFERENCE>
  replay_owner: PLATFORM_CORE_REPLAY
  replay_visible: <true|false>
  source_evidence: [<owner, reference, hash>]
  composition_evidence_owner: <owner>
  reconstruction_owner: <owner or NOT_APPLICABLE>
  lineage_rule: <preserve all source evidence by reference and hash>

failure_handling:
  fail_closed_conditions: [<exact conditions>]
  cancellation_owner_contract: <owner/contract or NOT_APPLICABLE>
  rollback_owner_contract: <owner/contract or NOT_APPLICABLE>
  deterministic_recovery_rule: <rule>

evolution:
  recertification_triggers: [<trigger>]
  new_identity_triggers: [<trigger>]
  deprecation_replacement_retirement_rule: <lineage preservation rule>

composition_identity_hash: <sha256 over canonical profile without this field>
```

Canonicalization uses lexically sorted keys, compact ASCII-safe UTF-8 JSON,
normalized set-like arrays, explicit sequence order, and a `sha256:` hash.
Duplicate identifiers, bindings, evidence references, or ambiguous ordering are
invalid.

## 11. Fail-closed conformance and non-goals

A composition is ineligible for certification, availability, activation, or
execution-related claims when any required identity, owner, participant,
contract, evidence, compatibility, authority boundary, Replay binding,
deterministic rule, failure behavior, or lineage is unresolved. Failure makes
no claim beyond an existing authorized contract.

This specification intentionally does not create a runtime composition
validator, runtime composition registry/loader, historical-profile backfill,
universal rollback mechanism, or recertification of current G20 composition
implementations. It does not alter the registry or PCBV31. These omissions are
explicit gaps, not inferred completion.

## 12. Versioning

V1 is the canonical Platform Core capability composition model established at
G52-02. A later version may clarify wording without semantic change. A change
to ownership preservation, authority isolation, deterministic arrangement,
Replay ownership, lifecycle, evidence, compatibility, or PCBV31/independent
owner boundaries is a governed constitutional-policy revision requiring
explicit review. A later version MUST explicitly supersede V1 and MUST NOT
rewrite this historical artifact in place after certification.
