# 1. Implementation Summary

Generation: G63-02

Report identity:
G63_02_CONSTITUTIONAL_REUSE_PROOF_FRAMEWORK_REPORT_V1

Reporting date: 2026-08-01

Constitutional baseline:
CONSTITUTIONAL_EVOLUTION_FRAMEWORK_CHARACTERIZED

Authenticated repository anchor:

- Commit: `92af533fc5f5281de0cbb30db73a2e06f359c71a`
- Direct parent: `7b4e77a94a2323500edf3720bc7e74427633eac5`
- Tree: `020112891bae387870b54a0696736eaf2ea50bb5`
- Subject: `G63-01: characterize constitutional evolution framework`

Implementation contracts:

- G48 Constitutional Evidence Reporting Standard V1
- G63-01 Constitutional Evolution Governance Framework Report V1
- G62-01 Complete Constitutional Architecture Reconstruction and Readiness
  Audit Report V1
- G61-01 Existing Central LLM Services Discovery and Constitutional
  Integration Audit Report V1
- G61-02 Central LLM Services Reuse and Integration Plan V1
- Constitutional Architecture Specification V1
- Canonical Layer Model
- Constitutional Invariants
- Governance Enforcement Hierarchy
- Governance Lineage Model
- Stable Substrate Declaration V1
- Governance Conformance System V1
- PCBV31 Baseline Identity Record V1
- AGENTS.md SAPIANTA Codex Orchestration Guide

Objective:

Characterize the mandatory Constitutional Reuse Proof Framework that must be
completed before any new architectural component, runtime, adapter, registry,
provider, capability, or subsystem may be proposed. The framework requires an
authenticated reconstruction of equivalent capabilities, ownership, usage,
compatibility, extension feasibility, and duplication risk before selecting
exactly one outcome: `REUSE`, `EXTEND`, `CONSOLIDATE`, or `CREATE_NEW`.

Implementation scope:

- Specialized the G63-01 EG-03 reuse-discovery gate into a deterministic,
  evidence-bearing pre-proposal process.
- Defined mandatory repository reconstruction, capability discovery,
  ownership proof, registry proof, implementation and usage inventories,
  compatibility analysis, extension feasibility, and duplicate detection.
- Defined one responsibility signature, one proof-record model, one ordered
  decision algorithm, and fail-closed completeness rules.
- Defined additive-versus-versioned rules while keeping the reuse decision
  separate from the G63-01 evolution class.
- Defined the additional negative-evidence burden for `CREATE_NEW` and the
  outputs required before governed implementation planning may begin.
- Defined integration with G63-01 checkpoints without creating a new runtime,
  registry, authority, or implementation authorization path.

Modified modules:

- `docs/governance/G63_02_CONSTITUTIONAL_REUSE_PROOF_FRAMEWORK_REPORT_V1.md`:
  this G48 architecture-only reuse proof framework.

Intentionally unchanged modules:

- All runtime and tests, including governance runtime.
- Platform Core, Conversation Layer, Human Interface, AiCLI, Central LLM
  Services/EPP, Development Governance, Capability Selection, Authorization,
  Worker, Completion, Replay, Evidence, and provider infrastructure.
- Every registry, manifest, provider adapter, capability declaration, PCBV31
  artifact, constitutional artifact, certification record, and prior report.
- Git history, hooks, runtime state, provider state, credentials, network state,
  and deployment state.

Architectural boundaries preserved:

- This is an L3 governed evidence and review contract subordinate to G63-01,
  L0/L1 stability, Replay safety, independent subsystem owners, and Human
  Authority.
- A reuse proof records what may proceed to G63-01 planning gates; it does not
  authorize design, mutation, implementation, migration, activation,
  deprecation, promotion, or execution.
- Registry membership, filenames, prose similarity, test fixtures, and
  historical presence do not by themselves prove runtime capability or
  constitutional ownership.
- An adapter cannot acquire the authority of the service it adapts. A
  coordinator cannot acquire the authority of the owners it sequences.
- The existing `PARTIALLY_CONFORMANT` hook status and the G62/G63-01
  limitations remain visible and unchanged.

## Framework Status

This report is the mandatory proof procedure for future architectural
proposals. It is not an executable gate and does not alter repository
enforcement. A future revision must be versioned, must preserve this report's
lineage, and must remain subordinate to higher constitutional sources.

A proof is always bounded to one normalized responsibility. If a request
contains responsibilities that produce different outcomes, the request MUST
be split into separate proof records. Combining outcomes in one record is
prohibited.

# 2. Code Evidence

No runtime code was added or changed. The evidence is the authenticated
repository architecture and the deterministic process characterized below.

## Authenticated Evidence Basis

| Evidence | Immutable identity | Use in this framework |
|---|---|---|
| G63-01 evolution framework | Commit `92af533fc5f5281de0cbb30db73a2e06f359c71a`; report SHA-256 `c449abb036763c87335518bec81eff114aba5f20a384a3526c3d327e3772afa3` | Governing evolution principles, classes, reuse gate, ownership, compatibility, review, and certification rules |
| G62-01 architecture reconstruction | Report SHA-256 `b8743d7575ff3db4d60798e19bb21d59498e1eab723e34e88561b2a0e029752c` | Post-G61 subsystem, owner, authority, dependency, integration, registry, and risk baseline |
| G61-01 Central LLM discovery audit | Report SHA-256 `5fdc5412e3fa74dcc26a5ccd2578bb6f65859d980caa10a457483063dff400c8` | Worked evidence that distributed provider surfaces must be reconstructed before a new service is proposed |
| G61-02 Central LLM reuse plan | Report SHA-256 `0dd7b0e909919c1d6d66732f1e5275f484ba42563e673ee0842c6128e994c6f7` | Worked evidence for reusing registries, routing, providers, and contracts through a bounded adapter |
| G48 reporting standard | SHA-256 `16508d1a77c4b3f07d37861e74d85f77896be16da01ca26cbc07a658ddf2c0eb` | Six-section evidence, validation, limitation, mutation, and single-verdict discipline |

The constitutional architecture, canonical layers, invariants, enforcement
hierarchy, lineage model, stable substrate, conformance system, and PCBV31
remain governing primary sources through G63-01. This report specializes their
reuse rule; it does not replace or broaden them.

## Constitutional Position and Gate Integration

```text
G63-01 EG-00  bounded objective
  -> EG-01    authenticated baseline
  -> EG-02    layer and evolution classification
  -> G63-02   Constitutional Reuse Proof
       RP-00 through RP-13
       exactly one: REUSE | EXTEND | CONSOLIDATE | CREATE_NEW
  -> EG-04    ownership and authority review
  -> EG-05    contract and compatibility review
  -> EG-06    migration, rollback, and deprecation review
  -> EG-07    implementation plan
  -> separate governed implementation authorization
```

G63-02 satisfies and strengthens EG-03. It may also supply evidence to later
gates, but it cannot pass them by implication. A repository discovery result
is not implementation authorization.

## Normalized Responsibility Signature

Before searching for an implementation, the requester MUST describe the need
without presupposing a component name. The canonical responsibility signature
contains:

| Field | Required characterization |
|---|---|
| `semantic_responsibility` | One observable responsibility stated independently of a proposed implementation |
| `inputs` | Accepted data, identities, versions, trust level, and source |
| `outputs` | Produced data, status, evidence, identities, and failure results |
| `state_and_persistence` | State read or written, ownership, serialization, and lifecycle |
| `authority` | Decisions or transitions the responsibility may perform |
| `non_authorities` | Adjacent decisions it must never perform |
| `boundary` | Layer, callers, dependencies, and external interfaces |
| `determinism` | Ordering, identity, repeatability, idempotency, and conflict rules |
| `evidence_and_replay` | Evidence producer, custody, reconstruction, and retention |
| `activation_and_lifecycle` | Registration, selection, default route, deprecation, and release behavior |

The signature is the comparison key. Product names, filenames, class names,
and provider labels are search hints, not proof of equivalence.

## Mandatory Reuse Proof Process

| Phase | Required action | Required evidence | Fail-closed condition |
|---|---|---|---|
| `RP-00 SCOPE` | Normalize one bounded responsibility and explicit non-goals | Responsibility signature and prohibited surfaces | Multiple inseparable responsibilities, assumed component, or ambiguous authority |
| `RP-01 AUTHENTICATE` | Bind the current repository and governing sources | Commit, parent, tree, source hashes, worktree status, known limitations | Dirty or unauthenticated baseline affects searched surfaces; source conflict unresolved |
| `RP-02 RECONSTRUCT` | Reconstruct all relevant current, alternate, historical, deprecated, experimental, and direct paths | Search manifest covering governance, PCBV31, runtime, tests, registries, callers, history, persistence, evidence, provider, Worker, CLI, and release paths | A required repository surface or dynamic path is omitted without a declared blocker |
| `RP-03 DISCOVER` | Locate capabilities by responsibility, inputs, outputs, effects, identifiers, synonyms, protocols, and evidence | Candidate capability inventory with exact paths and identities | Search relies only on proposed name or current filenames |
| `RP-04 OWNERSHIP` | Identify architectural, authority, implementation, state, evidence, lifecycle, and Human owners | Ownership matrix and source precedence | Owner is inferred, absent, contradictory, or shared without a governed split |
| `RP-05 REGISTRIES` | Inspect every relevant registry, manifest, catalog, selection rule, profile, and dynamic loader | Registry matrix including scope, owner, status, consumers, authority, and selection | Registration is mistaken for invocability, certification, or execution; registry overlap unresolved |
| `RP-06 INVENTORY` | Trace implementations and actual usage | Module/API inventory, imports, callers, entry routes, defaults, state writes, tests, and certificates | A candidate's reachability, status, or consumer set is unknown |
| `RP-07 EQUIVALENCE` | Compare each candidate with the responsibility signature | Field-by-field equivalence matrix and disposition | Equivalence is asserted from prose, name, or interface shape alone |
| `RP-08 COMPATIBILITY` | Evaluate direct use and representation/contract gaps | Multidimensional compatibility matrix | Any applicable compatibility dimension remains unknown |
| `RP-09 EXTENSION` | Exhaust the ordered extension ladder under the authenticated owner | Feasibility and rejection evidence for every rung reached | A feasible lower-impact rung is skipped |
| `RP-10 DUPLICATES` | Detect active, historical, registry, routing, authority, and evidence overlap | Duplicate matrix and consolidation feasibility | Scope-separated roles are collapsed, or duplicate authority remains unresolved |
| `RP-11 DECIDE` | Apply the ordered four-outcome algorithm | Exactly one outcome with selected target and rejected alternatives | Multiple outcomes, free-form outcome, unsupported `CREATE_NEW`, or unresolved evidence |
| `RP-12 PACKAGE` | Create the complete proof record | Evidence manifest, matrices, limitations, decision, next gates, content hash when finalized | Any mandatory field or supporting identity is absent |
| `RP-13 CHECKPOINT` | Review proof completeness against G63-01 | Checkpoint matrix and `PROOF_COMPLETE_FOR_EVOLUTION_PLANNING` or blocked disposition | Proof is treated as mutation, implementation, promotion, or execution authority |

Later evidence that changes a candidate, owner, registry, consumer, default,
or compatibility result invalidates RP-11 and requires the affected phases to
be repeated.

## Mandatory Repository Reconstruction

The RP-02 search manifest MUST cover all applicable evidence classes:

1. canonical constitutional, governance, baseline, certification, evidence,
   finalize, manifest, and supersession artifacts;
2. PCBV31 membership, spine, sockets, exclusions, independent owners, and
   baseline-trigger rules;
3. current runtime modules, public APIs, schemas, state stores, serializers,
   validators, protocols, adapters, orchestrators, and entry points;
4. registries, manifests, capability profiles, resource catalogs, provider and
   model metadata, routing tables, selection rules, status, and defaults;
5. static imports, callers, factory construction, dependency injection,
   callbacks, reflection, dynamic loading, environment selection, CLI modes,
   and Human-facing routes;
6. tests, fixtures, transcripts, replay/evidence reconstructors, migration
   utilities, release checks, and conformance rules;
7. direct-provider, bypass, compatibility, legacy, deprecated, dormant,
   experimental, duplicated, and alternate implementations;
8. Git history, prior names, relocations, deleted paths, supersession records,
   and authenticated historical evidence when current provenance is unclear;
9. provider, network, credential, privacy, persistence, deployment, Worker,
   Authorization, Replay, and evidence effects; and
10. documented external or dynamically retained sources that can affect
    architectural absence, reachability, or ownership.

Every search entry records the repository anchor, path or ref scope, exact
query or read method, observation, timestamp, and limitation. A negative search
is evidence only for its recorded scope. It cannot become a global absence
claim when dynamic loading, an external registry, an inaccessible archive, or
an unsearched historical source could change the result.

## Capability Discovery and Maturity

Each located candidate MUST be assigned every applicable maturity state:

| State | Meaning |
|---|---|
| `DECLARED` | Named or described in governance, a manifest, or metadata |
| `CERTIFIED_METADATA` | Certification covers the declared record or profile scope |
| `RUNTIME_BOUND` | An authenticated runtime binding exists |
| `INVOKABLE` | A current entry path can select and call it |
| `EXECUTABLE` | It can reach its certified execution owner under required gates |
| `EVIDENCE_PRODUCING` | Its owner emits the required evidence/replay identity |
| `TEST_ONLY` | Reachable only through test, fixture, or simulation support |
| `EXPERIMENTAL` | Bounded non-authoritative L4 surface |
| `DEPRECATED` | Retained for compatibility or migration; no new consumer assumed |
| `HISTORICAL_ONLY` | Evidence exists but the current runtime cannot select it |
| `UNVERIFIED` | Existence is observed but authority, binding, or behavior is not authenticated |

Maturity is not monotonic by inference. A certified declaration is not
necessarily runtime-bound; an invocable provider is not necessarily an
authorized capability; passing a test does not make a path a default route.

## Constitutional Ownership Proof

The ownership matrix MUST separate these roles:

| Ownership role | Required proof |
|---|---|
| Architectural owner | Canonical responsibility and layer from authenticated architecture or baseline evidence |
| Authority owner | Exact owner of each decision or state transition |
| Implementation owner | Runtime module/API implementing the bounded responsibility |
| State owner | Owner of mutable state, persistence, identity, and revision |
| Registry owner | Owner of record schema, lifecycle, status, and selection semantics |
| Evidence/Replay owner | Producer and reconstructor of immutable stage-local evidence |
| Lifecycle owner | Registration, activation, compatibility, migration, deprecation, and release responsibility |
| Human owner | Exact confirmation, approval, constitutional, or stop act where applicable |
| Consumers | Static and dynamic callers that constrain compatibility and retirement |

Evidence precedence is:

```text
canonical constitutional and baseline sources
  -> PCBV31 authenticated identity and independent-owner evidence
  -> scoped certification, registry, manifest, and supersession evidence
  -> public runtime contracts and state/evidence behavior
  -> current callers, routes, tests, and transcripts
  -> descriptive prose and names
```

Lower evidence cannot silently override higher evidence. A contradiction is a
blocker, not a reason to choose whichever source supports the proposal.

## Registry Verification

For each relevant registry, the proof record MUST capture:

- exact registry identity, version, owner, path, and responsibility scope;
- record schema, lifecycle statuses, authority flags, and certified scope;
- current records relevant to the responsibility signature;
- selection, ranking, fallback, default, activation, and removal behavior;
- writers, readers, loaders, caches, and static or dynamic consumers;
- runtime binding and evidence that a selected record is actually callable;
- relationship to other registries, manifests, profiles, and provider models;
- compatibility and migration behavior; and
- historical, superseded, direct, or unregistered paths.

Two registries are not duplicates merely because both contain similarly named
records. They are duplicates only when they claim materially equivalent
responsibility, authority, lifecycle, and selection scope. Conversely,
different schemas do not prevent a duplicate finding when both decide the
same architectural question.

## Implementation and Usage Inventory

Each candidate implementation record MUST include:

| Field | Evidence requirement |
|---|---|
| Identity | Exact module/path, symbol/API, version, content identity where material |
| Status | Active, default, opt-in, compatibility, experimental, deprecated, historical, or test-only |
| Contract | Inputs, outputs, validation, errors, ordering, idempotency, and canonical serialization |
| Ownership | Every ownership role from the ownership matrix |
| Reachability | Imports, callers, factories, registries, reflection, CLI/HIR route, defaults, and feature gates |
| Effects | State writes, evidence, replay, provider/network, credentials, privacy, Authorization, Worker, and release effects |
| Consumers | Exact current and migration consumers, including indirect and dynamic use |
| Assurance | Tests, certifications, known limitations, and unsupported paths |
| History | Predecessor, successor, compatibility route, and deprecation disposition |

Unused code is not automatically reusable, and active code is not
automatically canonical. Both require ownership, contract, and authority proof.

## Semantic Equivalence Model

Each candidate receives exactly one equivalence disposition relative to the
normalized responsibility:

| Disposition | Meaning |
|---|---|
| `EXACT_EQUIVALENT` | Same responsibility, authority, inputs, outputs, state, evidence, lifecycle, and boundary |
| `SEMANTIC_EQUIVALENT_DIFFERENT_INTERFACE` | Same owned responsibility and authority; representation or call contract differs |
| `PARTIAL_OVERLAP` | Candidate supplies only part of the responsibility or contains additional responsibility |
| `COMPLEMENTARY_FRAGMENT` | Candidate combines with other existing owned surfaces to cover the responsibility |
| `AUTHORITY_INCOMPATIBLE` | Function appears similar but owner or permitted decision differs |
| `DEPRECATED_ONLY` | Equivalent behavior exists only on a no-new-consumer or migration path |
| `UNAVAILABLE` | Candidate is declared or historical but not usable from the authenticated current baseline |
| `UNRELATED` | Responsibility signature does not materially match |
| `UNKNOWN_BLOCKED` | Evidence is insufficient for deterministic comparison |

`UNKNOWN_BLOCKED` prevents a certifying proof outcome. Similar text, an
identical provider name, shared data shapes, or common implementation language
cannot substitute for the signature comparison.

## Compatibility Analysis

Every potentially usable candidate MUST be evaluated across API, schema,
behavior, authority, ownership, dependency direction, registry/selection,
persistence, replay/evidence, provider/network/privacy, Worker/execution,
Human interaction, migration, release, and certification scope.

Each dimension receives exactly one result:

- `DIRECTLY_COMPATIBLE`;
- `ADAPTER_COMPATIBLE`;
- `VERSIONED_EXTENSION_REQUIRED`;
- `INCOMPATIBLE`; or
- `UNKNOWN_BLOCKED`.

Direct reuse requires every applicable dimension to be
`DIRECTLY_COMPATIBLE`. An adapter-compatible representation gap may support
`EXTEND`, but the adapter remains non-authoritative and must call the existing
owner. A required version change also supports `EXTEND` only when the existing
owner remains correct. Unknown compatibility blocks all four outcomes until
resolved or the proof itself is marked incomplete.

## Ordered Extension Feasibility Analysis

Before `CREATE_NEW`, the proof MUST exhaust this ladder in order:

1. existing configuration, profile, registry binding, or feature selection;
2. direct integration through an existing public API;
3. the smallest representation adapter that delegates to the existing owner;
4. an additive optional surface under the existing owner;
5. a versioned contract under the existing owner with coexistence and
   migration evidence; and
6. owner-scoped composition, migration, or consolidation of existing
   complementary or overlapping surfaces.

For each rung, record `FEASIBLE`, `INFEASIBLE`, or `UNKNOWN_BLOCKED`, with an
exact candidate, owner, compatibility reason, and evidence reference.
`FEASIBLE` stops the search for a higher-impact outcome. `UNKNOWN_BLOCKED`
cannot be converted into an `INFEASIBLE` result for the purpose of justifying
new architecture.

## Duplicate Detection and Consolidation

The proof compares full responsibility signatures and records these overlap
types:

| Type | Deterministic finding |
|---|---|
| Exact duplicate | Same responsibility, boundary, owner claim, and effects implemented twice |
| Functional duplicate | Different interfaces implement materially equivalent behavior |
| Authority duplicate | More than one surface claims the same constitutional decision |
| Registry duplicate | More than one registry governs the same record meaning, lifecycle, or selection |
| Routing duplicate | Multiple active/default routes independently decide how the same request reaches an owner |
| Evidence duplicate | Multiple surfaces claim custody or reconstruct the same stage evidence |
| Complementary fragmentation | Responsibility is split across existing surfaces without one sufficient public contract |
| Scoped non-duplicate | Similar mechanism has a distinct owner, authority, lifecycle, or responsibility scope |
| Historical overlap | Prior or compatibility implementation is retained but not an active new-consumer route |

Authority, registry, routing, or evidence duplication blocks `REUSE` and
`EXTEND` until ownership is unambiguous. When existing surfaces collectively
cover the responsibility and the constitutional task is to select, compose,
migrate, or retire them under an authenticated owner, the outcome is
`CONSOLIDATE`. Consolidation cannot be used to hide creation of a new
independent authority.

## Exactly-Four-Outcome Decision Model

Each complete proof MUST return exactly one of these tokens:

| Outcome | Required finding | Constitutional consequence |
|---|---|---|
| `REUSE` | One authenticated active owner and public contract directly satisfy the entire responsibility signature with no unresolved duplicate or compatibility gap | Use the existing contract; do not create architecture or copy logic |
| `EXTEND` | The existing owner is constitutionally correct, but a bounded configuration, binding, adapter, additive surface, or versioned contract is required | Plan the smallest change under that owner; adapter/orchestrator gains no owner authority |
| `CONSOLIDATE` | Existing overlapping or complementary surfaces collectively cover the responsibility, but ownership, routing, registry, evidence, migration, or lifecycle must be unified or retired | Plan consolidation under an authenticated owner with compatibility, migration, rollback, deprecation, and lineage evidence |
| `CREATE_NEW` | No authenticated existing owner or combination can satisfy the genuinely new responsibility, and reuse, extension, and consolidation have each been deterministically rejected | Propose a bounded new responsibility and owner for later G63-01 review; no implementation authority is granted |

No aliases, combined outcomes, confidence-weighted outcomes, or
`NO_CHANGE_REQUIRED` fifth outcome are permitted. When existing behavior
already satisfies the need, the outcome is `REUSE`, and the selected action is
to make no architectural change. When evidence cannot justify one token, the
proof is incomplete and produces no decision token.

## Deterministic Decision Algorithm

```text
INPUT: one normalized responsibility signature and authenticated proof record

1. If any mandatory phase, owner, candidate, registry, consumer,
   compatibility dimension, dynamic path, or duplicate disposition is
   UNKNOWN_BLOCKED, stop: PROOF_INCOMPLETE; return no outcome.

2. If one authenticated active existing owner/API directly satisfies the
   complete signature, all applicable compatibility is direct, and no
   conflicting active duplicate exists, return REUSE.

3. Otherwise, if the existing owner remains constitutionally correct and the
   first feasible extension-ladder rung among rungs 1 through 5 can satisfy
   the signature without creating duplicate authority, return EXTEND.

4. Otherwise, if existing overlapping or complementary surfaces collectively
   cover the signature and can be unified under an authenticated owner without
   inventing a new independent responsibility, return CONSOLIDATE.

5. Otherwise, verify the complete CREATE_NEW rejection package. Only when
   REUSE, EXTEND, and CONSOLIDATE are each rejected by candidate-specific,
   owner-specific, and contract-specific evidence, return CREATE_NEW.

6. Any contradiction or unsupported rejection stops fail closed:
   PROOF_INCOMPLETE; return no outcome.
```

The ordering is mandatory. A proposal cannot prefer a new component because
it is easier to implement, uses newer technology, has a cleaner name, avoids
migration work, or duplicates an existing contract more conveniently.

## Additive Versus Versioned Decision Rules

The four reuse outcomes and the G63-01 evolution classes are independent axes.
`EXTEND` and `CONSOLIDATE` therefore require a second classification:

| Condition | Additive disposition | Versioned or structural disposition |
|---|---|---|
| Existing consumers | All remain byte- and meaning-compatible | Any existing consumer requires new interpretation or migration |
| Activation | Explicit opt-in; defaults and selection unchanged | Default, ranking, fallback, or activation meaning changes |
| Schema/API | Separate optional surface; existing closed contract unchanged | Required field, enum, protocol, identity, or semantic meaning changes |
| Authority/owner | Same owner and authority; adapter is non-authoritative | Authority, owner, accepted evidence, or constitutional decision changes |
| State/replay | Existing state and replay remain readable unchanged | State transformation, new replay identity, or evidence meaning is required |
| Registry | Record is additive and does not affect existing selection | Registry schema, lifecycle, authority, or existing selection changes |
| Rollback | Disable new surface to recover prior route without evidence loss | Cutback requires migration, dual-read, supersession, or structural review |

If every additive condition holds, the corresponding G63-01 class may be
`ADDITIVE_EXTENSION`. A contract or state identity change requires
`VERSIONED_EXTENSION`. An owner, authority, default path, invariant, canonical
contract, or protected-boundary change is a
`CONSTITUTIONAL_MODIFICATION`, `SUBSYSTEM_REPLACEMENT`, or other applicable
G63-01 class even though the reuse outcome may remain `EXTEND` or
`CONSOLIDATE`.

## CREATE_NEW Burden of Proof

A `CREATE_NEW` record MUST include all of the following:

| Rejected outcome | Mandatory rejection evidence |
|---|---|
| `REUSE` | Every exact, semantic, partial, complementary, deprecated, historical, external, and dynamically discoverable candidate; the specific signature field or compatibility dimension that prevents direct reuse; authenticated owner and usage evidence |
| `EXTEND` | Result for every extension-ladder rung; why the existing owner's contract cannot safely express the need; why an adapter or versioned owner extension would violate responsibility, authority, dependency, replay, or compatibility boundaries |
| `CONSOLIDATE` | Why no combination of complementary or overlapping existing surfaces covers the responsibility; why consolidation cannot establish the missing semantic without creating a genuinely new responsibility; duplicate-disposition evidence |

It MUST also establish:

- the missing responsibility in positive terms and its non-overlap with every
  authenticated owner;
- why the absence claim is valid for current, historical, dynamic, external,
  registry, test, and deprecated search scopes;
- proposed architectural, authority, implementation, state, registry,
  evidence, lifecycle, and Human ownership, including explicit
  non-authorities;
- canonical dependency direction and proof that no existing owner must depend
  on the new convenience layer for its authority;
- contract, identity, schema, state, failure, determinism, evidence, replay,
  activation, migration, rollback, deprecation, and release plan;
- why no new registry or provider infrastructure is introduced unless that
  separate responsibility has its own complete reuse proof; and
- the G63-01 evolution class, layer gates, Human-review triggers, validation
  plan, and certification checkpoints.

`No file found`, `no similarly named class`, a proposal document, a model
recommendation, implementation convenience, performance preference, or an
unsearched external/dynamic surface is insufficient. Missing evidence produces
`PROOF_INCOMPLETE`, never `CREATE_NEW`.

## Constitutional Reuse Proof Record V1

Every completed study MUST create a governed documentation record containing:

| Field | Required value |
|---|---|
| `proof_id` | Stable identifier unique to the bounded responsibility |
| `authenticated_baseline` | Commit, parent, tree, worktree state, governing hashes, and limitations |
| `responsibility_signature` | All normalized responsibility fields and non-goals |
| `target_layers_and_class` | L0-L4 classification and preliminary G63-01 evolution class |
| `search_manifest` | Exact scopes, queries/methods, timestamps, findings, and limitations |
| `capability_inventory` | Candidate identities, maturity, bindings, reachability, and assurance |
| `ownership_matrix` | Architectural, authority, implementation, state, registry, evidence, lifecycle, Human, and consumer ownership |
| `registry_matrix` | Registry identities, scopes, status, selection, authority, bindings, and relationships |
| `implementation_usage_graph` | Modules, APIs, imports, callers, routes, defaults, effects, and history |
| `equivalence_matrix` | One canonical disposition per candidate and signature-field evidence |
| `compatibility_matrix` | One result per applicable dimension and candidate |
| `extension_ladder` | Ordered feasibility and rejection evidence |
| `duplicate_matrix` | Overlap type, scope, owner conflict, and consolidation feasibility |
| `negative_evidence` | Scope-bounded absence and rejected-alternative evidence |
| `decision` | Exactly one of `REUSE`, `EXTEND`, `CONSOLIDATE`, or `CREATE_NEW` |
| `selected_target` | Existing owner/API, consolidation target, or bounded proposed owner |
| `additive_or_versioned` | G63-01 semantic change classification and rationale |
| `authority_and_dependency_delta` | Before/after graphs, including explicit no-change evidence |
| `migration_rollback_deprecation` | Required, not applicable with reason, or blocked |
| `next_checkpoints` | G63-01 gates still required before implementation |
| `known_limitations` | Every partial, inaccessible, dynamic, external, or historical uncertainty |
| `proof_disposition` | `PROOF_COMPLETE_FOR_EVOLUTION_PLANNING` or `PROOF_INCOMPLETE` |
| `evidence_identity` | Immutable content hash when finalized and lineage references |

This is a documentation model only. G63-02 creates no runtime schema, database,
registry, service, validator, or automatic approval mechanism.

## Required Outputs Before Implementation Authorization

A proposal cannot enter G63-01 EG-07 until the following are present and
reviewed:

1. complete Constitutional Reuse Proof Record V1;
2. exactly one four-outcome decision and selected target;
3. authenticated source and search manifests;
4. capability, module/API, usage, owner, authority, registry, equivalence,
   compatibility, extension, duplicate, and negative-evidence matrices;
5. additive/versioned/structural classification and target layer analysis;
6. before/after ownership, authority, dependency, registry, state, replay, and
   default-route effects;
7. compatibility, migration, rollback, coexistence, deprecation, release, and
   evidence-preservation plan where applicable;
8. exact implementation boundaries, non-goals, forbidden imports/effects, and
   tests for the later implementation plan;
9. all remaining G63-01 checkpoints, required Human or subsystem-owner review,
   and certification scope; and
10. known limitations and `PROOF_COMPLETE_FOR_EVOLUTION_PLANNING`.

The last token authorizes only governed planning. Development Governance,
mutation enforcement, owner review, Human Authority where required, validation,
G48 certification, promotion, and activation remain separate.

## Certification Checkpoints

| Checkpoint | Acceptance evidence | Failure disposition |
|---|---|---|
| `CP-01 Scope` | One normalized responsibility and non-goals | Split or block ambiguous request |
| `CP-02 Baseline` | Authenticated clean baseline and governing hashes | `PROOF_INCOMPLETE` |
| `CP-03 Reconstruction` | All applicable repository/dynamic/historical scopes searched | `PROOF_INCOMPLETE` |
| `CP-04 Capability` | Candidate inventory and maturity separated from invocability/execution | `PROOF_INCOMPLETE` |
| `CP-05 Ownership` | One owner per responsibility and explicit adjacent non-authorities | Block conflicting or inferred ownership |
| `CP-06 Registry` | Registry scope, authority, selection, bindings, and overlaps proven | Block registry ambiguity or duplicate selection |
| `CP-07 Usage` | Static/dynamic consumers, defaults, effects, evidence, and history known | `PROOF_INCOMPLETE` |
| `CP-08 Equivalence` | Signature-field comparison for every candidate | `PROOF_INCOMPLETE` |
| `CP-09 Compatibility` | No applicable `UNKNOWN_BLOCKED` result | `PROOF_INCOMPLETE` |
| `CP-10 Extension` | Lower-impact ladder exhausted in order | Reject unsupported higher-impact outcome |
| `CP-11 Duplication` | All overlap classified; authority conflicts resolved or blocked | Block `REUSE`, `EXTEND`, and unjustified creation |
| `CP-12 Decision` | Exactly one authorized outcome; full CREATE_NEW rejection package if applicable | `PROOF_INCOMPLETE` |
| `CP-13 Evolution handoff` | G63-01 class, next gates, limits, migration/rollback/deprecation, and validation plan | No implementation-planning handoff |
| `CP-14 G48 evidence` | Exact scope, immutable references, validation matrix, mutations, limits, and one verdict | Fail closed under G48 |

## Illustrative Deterministic Applications

These examples explain the algorithm; they do not reopen or broaden prior
certifications.

| Situation | Outcome | Reason |
|---|---|---|
| An existing authenticated public API directly supplies the complete responsibility | `REUSE` | Existing owner and contract are sufficient; no architectural change is required |
| A Conversation Interpreter needs representation translation to existing Central LLM Services | `EXTEND` | G61 located the existing provider, registry, routing, and execution owners; a bounded non-authoritative adapter closes the interface gap |
| Multiple active provider or routing paths claim overlapping responsibility and require one owner, migration, and retirement plan | `CONSOLIDATE` | The capability exists, but duplicate routing/ownership must be resolved rather than copied |
| A capability appears in a manifest but has no authenticated runtime binding | No complete outcome until binding evidence is resolved | Declaration does not prove invocability; the record is `PROOF_INCOMPLETE`, not automatically `CREATE_NEW` |
| Full reconstruction proves a genuinely absent responsibility and rejects every reuse, extension, and consolidation route | `CREATE_NEW` | Only the complete rejection package permits a new bounded proposal |

## Responsibility and Non-Authority Boundaries

The Constitutional Reuse Proof owner may collect, authenticate, compare, and
classify evidence. It may not:

- create or transfer architectural authority;
- modify runtime, registries, providers, capabilities, evidence, or history;
- decide Platform Core admission, Development Governance, selection,
  Authorization, Worker execution, Completion, or Replay;
- convert provider/model output into governance truth;
- treat a proposal, proof, report, test, or registry entry as execution; or
- certify or promote the later implementation by inheritance.

Human Authority and existing owners remain responsible for their established
decisions. The proof framework governs proposal admissibility, not operational
execution.

# 3. Constitutional Self-Assessment

## Verified

- The framework is anchored to the committed G63-01 baseline and immutable
  evidence identities.
- The process normalizes a responsibility before searching, preventing a
  desired implementation name from controlling discovery.
- Repository reconstruction covers governance, PCBV31, runtime, APIs,
  registries, callers, dynamic routes, tests, history, providers, persistence,
  evidence, execution, and release surfaces.
- Capability maturity explicitly separates declaration, certification,
  binding, invocability, execution, evidence production, testing,
  experimentation, deprecation, and history.
- Ownership proof separates architecture, authority, implementation, state,
  registry, evidence, lifecycle, Human, and consumer roles with deterministic
  source precedence.
- Registry proof distinguishes similarly named scope-separated registries from
  duplicated responsibility and refuses to equate registration with execution.
- Implementation inventory requires current reachability, consumers, defaults,
  effects, assurance, and historical disposition.
- Equivalence and compatibility are evaluated against the full responsibility
  signature, not filenames or interface similarity.
- The ordered extension ladder ensures configuration, direct use, adapters,
  additive surfaces, versioning, and owner-scoped consolidation are evaluated
  before new creation.
- Duplicate detection covers function, authority, registry, routing, evidence,
  fragmentation, scoped separation, and historical overlap.
- Every complete proof returns exactly one of `REUSE`, `EXTEND`,
  `CONSOLIDATE`, or `CREATE_NEW`; incomplete evidence returns no outcome and
  fails closed.
- `CREATE_NEW` requires candidate-specific evidence rejecting all three
  lower-impact outcomes and defining bounded ownership, non-authority,
  lifecycle, migration, evidence, and certification.
- Additive/versioned classification remains separate from reuse disposition
  and follows the semantic and authority delta.
- The proof record, required outputs, and fourteen checkpoints integrate with
  G63-01 EG-00 through EG-07 without authorizing implementation.
- No runtime, tests, registry, provider, capability, governance runtime,
  PCBV31, historical artifact, or Git history was modified.

## Not Verified

- This framework is documentation-only. No runtime validator, repository
  scanner, proof registry, automatic classifier, enforcement hook, or
  implementation authorization mechanism was created or activated.
- No future architectural proposal has yet executed all RP-00 through RP-13
  phases under this framework, so operational use remains to be demonstrated
  by later bounded studies.
- Complete semantic equivalence for every repository component is not claimed;
  each future proof must reconstruct its own responsibility scope and baseline.
- External, dynamically loaded, archived, credentialed, or unavailable sources
  can limit an individual absence claim and must produce `PROOF_INCOMPLETE`
  when material.
- Repository-wide governance conformance remains partial. The read-only engine
  reported `18` checks passed, `2` checks failed, `0` critical violations, and
  `PARTIALLY_CONFORMANT` because of the known root and system pre-commit hook
  mismatches.
- MutationValidator physical path coverage, distributed approval evidence,
  cross-stage rollback uniformity, dormant governance memory, direct-provider
  compatibility surfaces, asserted Human identity, and bounded capability
  coverage remain the canonical pre-existing limitations.
- No live provider, network, credential, Worker execution, migration,
  deprecation, promotion, deployment, or production action was required or
  performed.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| Authenticate G63-01 baseline | Commit, parent, tree, subject, and G63-01 SHA-256 | `git show -s`; `sha256sum` | PASS |
| Integrate with G63-01 | Constitutional Position, RP phases, required handoff | Compared RP-00 through RP-13 with EG-00 through EG-07 | PASS |
| Define mandatory repository reconstruction | RP-02 and ten evidence classes | Checked governance, runtime, registries, consumers, dynamic/history/provider/evidence/release coverage | PASS |
| Define capability discovery | Responsibility signature and maturity model | Verified search is semantic and maturity does not infer invocability or execution | PASS |
| Define architectural ownership proof | Ownership roles and source precedence | Compared with G62/G63-01 one-responsibility/one-owner boundaries | PASS |
| Define registry verification | Registry evidence requirements and duplicate rule | Verified scope, authority, selection, binding, consumer, lifecycle, and overlap handling | PASS |
| Define implementation inventory | Implementation and Usage Inventory | Verified API, route, default, effects, consumers, assurance, and history fields | PASS |
| Define compatibility analysis | Equivalence and compatibility models | Verified multidimensional, owner-aware comparison and unknown-blocked behavior | PASS |
| Define extension feasibility | Ordered six-rung ladder | Confirmed every lower-impact route must be evaluated before creation | PASS |
| Define duplicate detection | Nine overlap types and consolidation rule | Verified scoped registries remain distinct while duplicate authority fails closed | PASS |
| Require exactly four outcomes | Outcome table and deterministic algorithm | Confirmed only `REUSE`, `EXTEND`, `CONSOLIDATE`, and `CREATE_NEW` are complete decisions | PASS |
| Define additive versus versioned rules | Semantic delta matrix | Compared consumer, activation, contract, authority, state/replay, registry, and rollback triggers with G63-01 | PASS |
| Enforce CREATE_NEW burden | Three-outcome rejection matrix and positive new-owner requirements | Confirmed incomplete/negative-name searches cannot justify creation | PASS |
| Define constitutional evidence model | Constitutional Reuse Proof Record V1 | Verified all required source, candidate, owner, registry, compatibility, decision, limitation, and lineage fields | PASS |
| Define outputs before authorization | Ten mandatory outputs and non-authorization rule | Confirmed proof permits planning only and preserves later governance gates | PASS |
| Define certification checkpoints | CP-01 through CP-14 | Verified every checkpoint has acceptance evidence and fail-closed disposition | PASS |
| Preserve constitutional ownership | Responsibility and Non-Authority Boundaries | Confirmed proof activity cannot inherit subsystem or execution authority | PASS |
| Preserve known limitations | Self-Assessment Not Verified | Existing conformance, path, approval, rollback, provider, identity, and capability limitations retained | PASS |
| Governance conformance tests | `tests/test_governance_conformance.py` | `python -m pytest tests/test_governance_conformance.py`: 5 passed | PASS |
| Governance conformance visibility | `python -m runtime.governance.governance_conformance_engine` | Read-only result: 18 passed, 2 failed, 0 critical, deterministic/fail-closed/read-only, `PARTIALLY_CONFORMANT`; known hook mismatches retained | PASS |
| G48 report structure | This report | Confirmed exactly six required top-level sections and one authorized final verdict | PASS |
| Runtime and registry mutation prohibition | Repository status and scope review | Requested governance report is the only new file | NOT_APPLICABLE |
| Diff hygiene | Complete G63-02 change | `git diff --no-index --check /dev/null docs/governance/G63_02_CONSTITUTIONAL_REUSE_PROOF_FRAMEWORK_REPORT_V1.md` (exit 1 for an added file; no whitespace diagnostics) | PASS |

# 5. Repository Mutation Summary

Modified files:

- `docs/governance/G63_02_CONSTITUTIONAL_REUSE_PROOF_FRAMEWORK_REPORT_V1.md`:
  added this read-only Constitutional Reuse Proof Framework.

Unchanged subsystems:

- All runtime and tests, including governance runtime.
- Platform Core, Conversation Layer, Human Interface, AiCLI, Central LLM
  Services/EPP, provider infrastructure, Development Governance, Capability
  Registry and Selection, Authorization, Worker, Completion, Replay, and
  Evidence.
- Every registry, manifest, provider adapter, capability, PCBV31 artifact,
  constitutional source, prior governance report, certification record, and
  historical artifact.
- Git history, hooks, runtime state, external services, credentials, network,
  deployment, and release state.

API compatibility:

- No API, schema, protocol, state, serializer, validator, registry record,
  selection rule, provider contract, capability, CLI route, replay identity,
  or runtime behavior changed.
- `Constitutional Reuse Proof Record V1` is documentation vocabulary inside
  this report only; it is not an importable schema or executable interface.

Boundary preservation:

- The report creates no new architectural component, runtime, adapter,
  registry, provider, capability, subsystem, governance authority, automatic
  mutation path, execution route, or deployment mechanism.
- A proof decision does not certify design, authorize mutation, inherit owner
  authority, or promote an implementation.
- Existing owners, evidence custody, replay lineage, Human Authority,
  certification scope, partial conformance, and historical limitations remain
  intact.

Unrelated pre-existing changes:

- None observed at audit start. The authenticated G63-01 baseline was clean.
- Known conformance hook drift, incomplete path coverage, distributed
  approval/rollback limitations, direct-provider compatibility surfaces,
  asserted Human identity, and bounded capability coverage pre-exist G63-02
  and were not modified.

# 6. Certification Verdict

CONSTITUTIONAL_REUSE_PROOF_FRAMEWORK_CHARACTERIZED
