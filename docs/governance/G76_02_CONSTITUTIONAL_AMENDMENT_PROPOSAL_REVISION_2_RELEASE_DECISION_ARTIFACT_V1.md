# 1. Implementation Summary

Generation: G76-02

Report and proposal identity:
G76_02_CONSTITUTIONAL_AMENDMENT_PROPOSAL_REVISION_2_RELEASE_DECISION_ARTIFACT_V1

Proposal revision: 2

Proposal status: `PROPOSAL_ONLY_UNASSESSED`

Amendment kind: `ADDITION`

Constitutional baseline: G0 through G76-01. G76-00 is immutable Proposal
Revision 1. G76-01 is the direct authenticated
`UNRESOLVED_CONSTITUTIONAL_IMPACT` assessment. Both predecessors remain closed
and unchanged.

Authenticated repository identity:

- Commit: `140b6c6b325de2c0ad1873683abae5b2367139e1`
- Tree: `e5ad0cccc9616f04d4d1d7be8a22983e67541f8c`
- Subject: `G76-01: assess CAP proposal for release decision artifact`
- Immediate parent: `8ba0d8f06a0d12be37174ba4758517d27550d914`
- Revision-start worktree state: clean
- Authenticated G76-00 SHA-256:
  `d6fe5668d2e74d467a25818fc461d29da55e5c6cd804eab06cfeafdc271df028`
- Authenticated G76-01 SHA-256:
  `45df6563a7dd2825c1a6c28c497b6941701cf1272daffbec4abcaad804aa466d`

Previous proposal binding:

| Field | Exact binding |
|---|---|
| previous proposal identity | `G76_00_CONSTITUTIONAL_AMENDMENT_PROPOSAL_FOR_RELEASE_DECISION_ARTIFACT_V1` |
| previous proposal revision | `1` |
| previous proposal digest | `sha256:d6fe5668d2e74d467a25818fc461d29da55e5c6cd804eab06cfeafdc271df028` |
| previous assessment identity | `G76_01_CONSTITUTIONAL_AMENDMENT_IMPACT_ASSESSMENT_RELEASE_DECISION_ARTIFACT_V1` |
| previous assessment digest | `sha256:45df6563a7dd2825c1a6c28c497b6941701cf1272daffbec4abcaad804aa466d` |
| previous assessment class | `UNRESOLVED_CONSTITUTIONAL_IMPACT` |

Implementation contracts: G48 Constitutional Evidence Reporting Standard V1;
Constitutional Architecture Specification V1; Canonical Layer Model;
Constitutional Invariants; Governance Enforcement Hierarchy; Governance
Lineage Model; G69-07 Canonical Human Authority Act Contract; G69-13 Complete
HIC Conformance and Historical Independence; G69-18 full-branch Replay and
CRO coverage; G69-19 Constitutional Production Cutover; G70-02 Constitutional
Amendment Proposal Contract; G70-03 Constitutional Impact Assessment Contract;
G70-04 Human Ratification Contract; G70-07 CAP Closure; G72-00 Constitutional
Core Baseline; G73-00 Human Constitution; G74-00 and G74-01 Production Cutover
evidence; G75-02 derivability audit; G76-00 Proposal Revision 1; and G76-01
Impact Assessment.

Reporting date: 2026-08-06.

Objective:

Create the exact Revision 2 successor of G76-00. Resolve every blocking impact
identified by G76-01 by defining one pre-cutover Human ingress phase, one
bounded release/cutover owner contract, one authoritative release/cutover
state, complete crash-consistent persistence, exact G69-19 successor and
migration rules, and exact production and Constitutional rollback rules. Do
not assess Revision 2, ratify, certify, publish, activate, implement, deploy,
or mutate runtime state.

Revision result:

Revision 2 preserves the Release Candidate, Human Release Decision, immutable
lifecycle evidence, owner-local Replay, passive CRO, and G69-19 binding
responsibilities from Revision 1. It supersedes Revision 1's incomplete
ingress, owner, mutable-head, active-state, expiry, migration, and rollback
rules with the following exact successor model:

1. The one canonical `clia` surface and the same
   `CLIA_PRODUCTION_HIC_FAMILY` have two mutually exclusive phases under one
   successor profile: `RELEASE_CONTROL_ONLY` while cutover is not active, and
   `ACTIVE_PRODUCTION_TRANSPORT` while cutover is active. Both phases invoke
   the sole CHE. No direct-CHE caller, second launcher, forwarding alias, or
   gate bypass is permitted.
2. The existing `RELEASE_CUTOVER_PRODUCTION_STATUS_OWNER` receives one closed
   successor contract. Candidate preparation, fixed-schema payload
   interpretation, evidence custody, Replay custody, Certification
   preparation, and atomic status transitions are separately named
   responsibilities with explicit negative capabilities. Human Authority,
   HIC, CHE, Certification owners, Replay, and CRO retain their independent
   boundaries.
3. Exactly one
   `CONSTITUTIONAL_RELEASE_CUTOVER_AUTHORITY_STATE_V2` record is the current
   authority for Release Decision and Production Cutover state. Immutable
   Candidate, Decision, Event, Replay, CRO, and Certification artifacts have
   evidence value but no current authority unless referenced by that one
   validated state.
4. Every current-state change serializes through one crash-released exclusive
   lock and one same-directory, flushed, atomically replaced, directory-synced
   authority-state file. There is no separate mutable Decision head.
   Pre-commit immutable artifacts may be orphaned by a crash, but are ignored
   by authority validation and cannot create a second head.
5. Revocation, supersession, Certification, activation, suspension, and
   rollback change current authority only through the same state transition.
   Every production gate revalidates the complete current Decision, Replay,
   CRO, Certification, and state binding.

Proposed successor identity:

`AI_GOL_CONSTITUTIONAL_CORE_BASELINE_V1_1_RELEASE_DECISION_ARTIFACT_REVISION_2_PROPOSED`

Proposed successor version:

`V1.1-RELEASE-DECISION-ARTIFACT-R2`

Proposal target remains:

| Field | Exact proposed binding |
|---|---|
| proposing owner | `CONSTITUTIONAL_GOVERNANCE_OWNER` |
| target Constitutional owner | `CONSTITUTIONAL_GOVERNANCE_OWNER` |
| target layer | `L1` canonical artifact definitions |
| target artifact | `AI_GOL_CONSTITUTIONAL_CORE_BASELINE_V1_ESTABLISHED` |
| target version | `V1` |
| amendment form | one additive successor with exact predecessor lineage |

Proposal boundary:

Revision 2 remains `PROPOSAL_ONLY_UNASSESSED`. It must receive a new complete
G70-03 Impact Assessment. G76-01 cannot be reused as the assessment of changed
normative content. No Human Ratification, amendment Certification,
Publication, Activation, CDP implementation, release decision, terminal
Certification, deployment, or Production Cutover transition is performed.

Added artifact:

- `docs/governance/G76_02_CONSTITUTIONAL_AMENDMENT_PROPOSAL_REVISION_2_RELEASE_DECISION_ARTIFACT_V1.md`
  — this proposal-only G48 Revision 2 successor.

Intentionally unchanged modules and state:

- G76-00 Proposal Revision 1 and G76-01 Impact Assessment;
- every active G0 through G75-02 Constitutional artifact;
- Human Authority, Production Cutover, production status, release, CLIA, HIC,
  CHE, Replay, CRO, CDP, CAP, Governance, routing, workflow, owner-chain,
  deployment, configuration, and runtime behavior;
- every Candidate, Decision, Event, Replay, CRO, terminal Certification,
  active-state, rollback-state, and runtime-root artifact; and
- all code and tests.

Architectural boundaries preserved by the proposal stage:

- one CHE remains;
- one canonical production HIC family remains;
- one canonical `clia` surface remains;
- HIC remains transport only;
- one production owner chain remains;
- one production path remains;
- zero parallel production paths remain;
- Replay remains owner-local, deterministic, read-only, and
  non-authoritative;
- CRO remains passive and non-authoritative;
- Human Authority remains the only release-decision authority; and
- the proposal has no active or runtime authority.

# 2. Code Evidence

## Public API

G76-02 adds or changes no runtime API. After a complete CAP successor becomes
active, a separately authorized CDP generation would be completely bounded by
these proposed responsibility surfaces:

~~~text
create_constitutional_release_candidate_evidence_v1(...)
create_constitutional_release_control_challenge_v2(...)
validate_pre_cutover_release_control_admission_v2(...)
create_constitutional_release_decision_artifact_v1(...)
create_constitutional_release_decision_event_v2(...)
reconstruct_constitutional_release_decision_replay_v2(...)
observe_constitutional_release_decision_for_cro_v2(...)
create_constitutional_production_cutover_certification_v2(...)
transition_constitutional_release_cutover_authority_state_v2(...)
validate_constitutional_release_cutover_authority_state_v2(...)
validate_production_hic_activation_v2(...)
rollback_constitutional_production_cutover_v2(...)
migrate_constitutional_production_cutover_v1_to_v2(...)
~~~

The names specify proposed ownership and behavior only. Revision 2 introduces
no executable symbol.

The existing `CanonicalHumanAuthorityActV1` remains the Human decision
carrier. It uses existing authority kinds:

- `AUTHORIZATION` for `APPROVED` or `REJECTED` initial release decisions;
- `CANCEL` for Release Decision revocation; and
- `AUTHORIZATION` with an exact rollback scope for Production Cutover
  rollback.

No authority kind, Human owner, HIC family, or CHE definition is added.

## Orchestration Entry Point

### One two-phase canonical ingress

The successor canonical profile is
`CLIA_CONSTITUTIONAL_PRODUCTION_PROFILE_V2`. Its interface identity remains
`CLIA`; its HIC family remains `CLIA_PRODUCTION_HIC_FAMILY`; its only entry is
the repository `clia` launcher; and its only runtime admission successor is
the sole CHE.

The current authority-state validator selects exactly one phase:

~~~text
authority state absent
OR RELEASE_CONTROL_PENDING
OR decision/certification/cutover state is inactive, suspended, or rolled back
-> RELEASE_CONTROL_ONLY

validated CUTOVER_ACTIVE state
-> ACTIVE_PRODUCTION_TRANSPORT

malformed, corrupt, conflicting, unsupported, or ambiguous state
-> FAIL CLOSED; no phase selected
~~~

`RELEASE_CONTROL_ONLY` permits exactly one structured transport capability:
`HUMAN_AUTHORITY_ACT`. It requires an exact immutable
`CONSTITUTIONAL_RELEASE_CONTROL_CHALLENGE_V2` already created by the
release/cutover owner and referenced by the current authority state. The
challenge binds Candidate identity/digest, target environment/root, Human
actor, session, owner-issued next act, authority kind, scope, target revision,
allowed decision states, CHE Request identity, and Continuation identity.

The HIC mechanically presents the challenge and transports the exact Human
act. It may validate transport shape and the challenge reference. It may not
interpret the decision, construct a Candidate, choose an outcome, invoke a
workflow, certify, deploy, activate, or mutate authority state. CHE validates
the structured act and hands it to the exact expected release/cutover owner.

The complete first-activation sequence becomes:

~~~text
release/cutover owner creates immutable Candidate and owner-issued challenge
-> one atomic authority-state transition to RELEASE_CONTROL_PENDING
-> same clia surface selects RELEASE_CONTROL_ONLY
-> same CLIA HIC family mechanically presents challenge
-> authenticated Human supplies exact CanonicalHumanAuthorityActV1
-> sole CHE validates and admits the act
-> bounded release-decision owner validates fixed payload
-> immutable Decision, Replay, and passive CRO evidence prepared
-> one atomic authority-state transition to DECISION_APPROVED_CUTOVER_INACTIVE
-> terminal G69-19 V2 Certification prepared
-> one atomic transition to CUTOVER_CERTIFIED_INACTIVE
-> existing activation authority performs one atomic transition
-> CUTOVER_ACTIVE
-> same clia surface selects ACTIVE_PRODUCTION_TRANSPORT
-> same HIC -> same CHE -> same downstream production owner chain
~~~

No release-control act can enter a Worker, product semantic owner, deployment,
or active production branch. No ordinary product act can enter while the
phase is `RELEASE_CONTROL_ONLY`.

## Semantic Reductions

### Owner-issued challenge reduction

~~~text
valid Candidate
AND exact target environment/root
AND exact owner-issued Human next-act binding
AND current state permits release control
-> exact Release Control Challenge

challenge absent, stale, substituted, mismatched, or not current
-> fail closed before CHE delivery
~~~

### Human decision reduction

~~~text
same CLIA family + sole CHE
AND valid current Challenge
AND exact authenticated Human Act
AND kind == AUTHORIZATION
AND payload decision_state in {APPROVED, REJECTED}
AND every Candidate/root/evidence/topology binding equal
-> immutable Release Decision evidence
-> atomic current authority-state transition

any mismatch or unsupported act
-> no Decision authority and no state transition
~~~

### Current authority reduction

~~~text
immutable evidence exists but is not referenced by authority-state
-> evidence only; no current authority

one valid authority-state references exact evidence and predecessor hash
-> one current release/cutover authority

multiple candidate heads, missing referenced evidence, corrupt state,
wrong predecessor, or invalid transition
-> fail closed
~~~

### Activation reduction

~~~text
DECISION_APPROVED_CUTOVER_INACTIVE
AND Decision has expires_at == null
AND exact Decision Replay is APPROVED and activation_eligibility == true
AND exact passive CRO observation matches
AND exact G69-19 V2 terminal Certification matches
AND exact 1/1/1/1/0 topology
-> CUTOVER_CERTIFIED_INACTIVE
-> separate Human/release activation authority
-> one atomic state transition to CUTOVER_ACTIVE

anything else
-> no activation
~~~

### Revocation and rollback reduction

~~~text
inactive APPROVED Decision + exact Human CANCEL
-> immutable REVOKED event
-> atomic DECISION_REVOKED_CUTOVER_INACTIVE state

CUTOVER_ACTIVE + exact Human CANCEL of Decision
-> immutable REVOKED event
-> atomic CUTOVER_SUSPENDED_DECISION_REVOKED state
-> production gate false immediately

CUTOVER_SUSPENDED_DECISION_REVOKED
+ exact separately scoped Human rollback AUTHORIZATION
+ valid rollback proof and exact predecessor
-> atomic CUTOVER_ROLLED_BACK_DECISION_REVOKED state

CUTOVER_ACTIVE + exact Human rollback AUTHORIZATION without revocation
-> atomic CUTOVER_ROLLED_BACK state
-> original Decision remains immutable but activation_consumed == true
-> a new Decision is required for any later activation
~~~

Revocation is never inferred from rollback, and rollback is never inferred
from revocation. Suspension is a valid inactive state, not a second current
head. Every production caller rejects suspended and rolled-back state.

### Supersession reduction

~~~text
current cutover inactive or rolled back
+ new APPROVED Decision B names exact Decision A identity/digest
+ A is not the authority for an active cutover
-> atomic state transition referencing B
-> A reconstructed as SUPERSEDED

current cutover active
-> supersession prohibited until atomic suspension/rollback
~~~

Approved Decisions eligible for Certification SHALL have `expires_at ==
null`. Time-bounded activation is outside Revision 2 and cannot be inferred.
This removes clock-driven authority changes that could occur without an atomic
state transition.

## Public Validators

The successor validators SHALL enforce:

- exact versions, closed schemas, identities, digests, predecessor hashes,
  transition kinds, and state vocabulary;
- one exact current authority-state file at the existing G69-19 state path;
- no separate mutable Decision head;
- exact same-root resolution for Candidate, Decision, Event, Replay, CRO, and
  Certification evidence;
- exact `CLIA` interface, `CLIA_PRODUCTION_HIC_FAMILY`, sole CHE, and mutually
  exclusive phase;
- release-control Challenge equality before pre-cutover transport;
- exclusive structured `HUMAN_AUTHORITY_ACT` capability in release-control
  phase;
- fixed Human kind, actor, target, revision, scope, request, Continuation,
  Candidate, environment, root, and payload bindings;
- exact owner contract and handoff at each boundary;
- Decision `expires_at == null` before terminal Certification;
- complete owner-local Replay and passive CRO equality;
- G69-19 V2 Certification equality with the current authority state;
- valid predecessor state and allowed transition;
- no active production in pending, rejected, revoked, suspended,
  superseded, retired, rolled-back, corrupt, or V1-unmigrated state;
- activation consumption after rollback;
- exact 1/1/1/1/0 topology; and
- no HIC semantics, direct CHE caller, compatibility forwarding, Replay
  mutation, CRO authority, implicit migration, or automatic repair.

The V2 production gate SHALL re-read and revalidate the complete authority
state and all referenced evidence on every production submission and every
production owner call. Cached success cannot outlive the validated call.

## Canonical Data Models

### Revision 2 format identities

Revision 2 retains the V1 Candidate and Decision identities and adds exact
successor coordination models:

~~~text
CONSTITUTIONAL_RELEASE_CANDIDATE_EVIDENCE_V1
CONSTITUTIONAL_RELEASE_DECISION_ARTIFACT_V1
CONSTITUTIONAL_RELEASE_CONTROL_CHALLENGE_V2
CONSTITUTIONAL_RELEASE_DECISION_LIFECYCLE_EVENT_V2
CONSTITUTIONAL_RELEASE_DECISION_REPLAY_V2
CONSTITUTIONAL_RELEASE_DECISION_CRO_OBSERVATION_V2
CONSTITUTIONAL_RELEASE_CUTOVER_OWNER_CONTRACT_V2
G69_19_CONSTITUTIONAL_PRODUCTION_CUTOVER_CERTIFICATION_V2
CONSTITUTIONAL_RELEASE_CUTOVER_AUTHORITY_STATE_V2
CONSTITUTIONAL_RELEASE_CUTOVER_TRANSITION_V2
CLIA_CONSTITUTIONAL_PRODUCTION_PROFILE_V2
~~~

Candidate and Decision fields remain as specified by Revision 1 except:

- a Decision that may become activation authority must set `expires_at` to
  null;
- no Decision or Event is a mutable head;
- lifecycle Event V2 binds exact authority-state predecessor identity, hash,
  revision, and transition identity; and
- current state and activation eligibility are derived only from the V2
  authority state plus referenced immutable evidence.

### Release Control Challenge schema

The immutable Challenge contains exactly:

~~~text
challenge_version
challenge_identity
challenge_digest
release_candidate_identity
release_candidate_digest
target_environment_identity
target_runtime_root
human_actor_identity
session_identity
request_identity
continuation_identity
next_act_identity
expected_owner = RELEASE_CUTOVER_PRODUCTION_STATUS_OWNER
authority_kind = AUTHORIZATION
authority_scope = CONSTITUTIONAL_PRODUCTION_CUTOVER_RELEASE_DECISION_V1
target_revision
allowed_decision_states = [APPROVED, REJECTED]
created_at
topology = 1/1/1/1/0
~~~

Identity and digest use canonical JSON and SHA-256 excluding only their own
fields. The Challenge is create-once and gains current presentation authority
only when the one authority state references it.

### Unified authority-state schema

The exact current-state file remains at:

~~~text
<runtime-root>/constitutional_production_cutover_v1/active-cutover.json
~~~

Revision 2 deliberately reuses the one existing current-state path. A V1 and
V2 current state cannot coexist at different authoritative paths. V1 readers
must reject the V2 version; V2 readers accept V2 only after exact migration.

`CONSTITUTIONAL_RELEASE_CUTOVER_AUTHORITY_STATE_V2` contains exactly:

~~~text
state_version
state_identity
state_hash
state_revision
predecessor_state_identity
predecessor_state_hash
transition_identity
transition_kind
authority_status
release_phase
target_environment_identity
target_runtime_root
release_candidate_reference
release_control_challenge_reference
release_decision_reference
release_decision_replay_reference
release_decision_cro_reference
terminal_certification_reference
activation_consumed
canonical_hic_family
surface_dispositions
rollback_decision_reference
v1_migration_provenance
topology
committed_at
~~~

Every optional reference is null exactly when the state vocabulary requires
it and otherwise contains exact artifact identity, digest, and same-root path.
State identity/hash cover every field except themselves. State revision is
one for first state and increments exactly one from its predecessor.

### Closed authority states

| Authority status | Production gate | Required current evidence |
|---|---|---|
| `RELEASE_CONTROL_PENDING` | closed; release control only | Candidate and Challenge |
| `DECISION_REJECTED_CUTOVER_INACTIVE` | closed; release control only | rejected Decision and Replay/CRO |
| `DECISION_APPROVED_CUTOVER_INACTIVE` | closed; release control only | approved Decision and Replay/CRO |
| `CUTOVER_CERTIFIED_INACTIVE` | closed; release control only | approved Decision, Replay/CRO, G69-19 V2 Certification |
| `CUTOVER_ACTIVE` | open for active production transport | complete certified package; unconsumed activation |
| `CUTOVER_SUSPENDED_DECISION_REVOKED` | closed; release control only | revoked Decision event; rollback pending |
| `CUTOVER_ROLLED_BACK` | closed; release control only | exact rollback act; activation consumed |
| `CUTOVER_ROLLED_BACK_DECISION_REVOKED` | closed; release control only | revocation plus exact rollback act |
| `DECISION_REVOKED_CUTOVER_INACTIVE` | closed; release control only | revoked Decision event |
| `DECISION_SUPERSEDED_CUTOVER_INACTIVE` | closed; release control only | exact successor Decision |
| `DECISION_RETIRED_CUTOVER_INACTIVE` | closed; release control only | retirement event and eligibility proof |

No unknown state is compatible. `CUTOVER_ACTIVE` is the only production-open
state.

### Immutable evidence storage

Evidence paths are:

~~~text
<runtime-root>/constitutional_release_decision_v2/
  candidates/<candidate-hex>.json
  challenges/<challenge-hex>.json
  decisions/<decision-hex>.json
  events/<event-hex>.json
  transitions/<transition-hex>.json
  replays/<replay-hex>.json
  cro/<observation-hex>.json
  certifications/<certification-hex>.json

<runtime-root>/constitutional_production_cutover_v1/
  .cutover.lock
~~~

All evidence files are content-addressed, create-once, immutable, flushed,
and directory-synced. They never determine the current head. The only current
head is the one G69-19 authority-state file.

### Revision Comparison Matrix

| Proposal area | Revision 1 | Revision 2 successor |
|---|---|---|
| predecessor | no prior proposal | exact G76-00 identity/digest and G76-01 assessment binding |
| pre-cutover ingress | unnamed Governance/release use of HIC/CHE | same `clia` surface, same HIC family, sole CHE, exact `RELEASE_CONTROL_ONLY` phase and Challenge |
| HIC profile | existing production profile assumed | one V2 profile with mutually exclusive release-control and active-production phases |
| release owner | activation owner also assigned new duties without exact successor contract | closed V2 owner contract with positive duties, handoffs, and negative capabilities |
| current Decision head | separate mutable candidate head file | no mutable Decision head; one unified authority state |
| active-state consistency | Decision and G69-19 state stored separately | one state references Decision, Replay/CRO, Certification, activation, and rollback |
| crash atomicity | Decision and head claimed atomic across files | immutable evidence first; exactly one same-directory authority-state replacement is the commit point |
| lock recovery | persistent lock semantics incomplete | crash-released exclusive lock; no stale lock authority or automatic state repair |
| expiry | optional expiry could invalidate active state without transition | activation-eligible Decision requires `expires_at == null` |
| active revocation | eligibility false while established state could remain | atomic suspended state closes production immediately; rollback follows separately |
| supersession | atomic head replacement underspecified | prohibited while active; exact atomic successor transition only when inactive/rolled back |
| rollback | retention described; operational/version rules absent | exact Human rollback act, one state transition, activation consumption, V1/V2 rules |
| G69-19 | future successor named without exact versions | exact Certification V2, authority-state V2, per-call revalidation |
| V1 migration | historical preservation only | closed no-state, active, rolled-back, invalid, and string-only dispositions |
| multi-root | root binding present, coordination unspecified | each environment/root has independent authority; no cross-root inference or replication authority |

### Resolution Matrix

| G76-01 impact or risk | Revision 2 disposition | Resolution |
|---|---|---|
| pre-cutover HIC/CHE circular dependency | exact release-control phase on same `clia`/HIC/CHE route | `RESOLVED` |
| HIC/CHE contract impact | V2 profile, exclusive capability, Challenge, and negative authority | `RESOLVED` |
| one CHE / one HIC family | exact counts and identities fixed; no direct caller | `RESOLVED` |
| one path / zero parallel | mutually exclusive phases on one route; no forwarding | `RESOLVED` |
| owner responsibility expansion | closed V2 owner contract and separate responsibility boundaries | `RESOLVED` |
| current Decision versus active cutover | one authoritative state and per-call evidence revalidation | `RESOLVED` |
| revocation while active | atomic suspension closes gate; separately authorized rollback | `RESOLVED` |
| expiry race | active-eligible Decisions cannot expire | `RESOLVED` |
| separate-file crash atomicity | immutable evidence is non-authoritative; one atomic state is commit point | `RESOLVED` |
| stale transition lock | crash-released lock; loss releases exclusion without changing state | `RESOLVED` |
| G69-19 version ambiguity | exact V2 Certification and state versions | `RESOLVED` |
| V1 active-state migration | exact reaffirmation and atomic same-path replacement | `RESOLVED` |
| V1 rolled-back/no-state/invalid dispositions | closed migration matrix below | `RESOLVED` |
| cross-version production rollback | exact V1 provenance and V2 rollback eligibility | `RESOLVED` |
| Constitutional rollback | V2 evidence retained; V1 runtime accepts only exact preserved eligible V1 state, otherwise inactive | `RESOLVED` |
| multi-root divergence | each exact root requires its own Human Decision and state; no shared authority | `RESOLVED` |
| evidence retention growth | indefinite safe retention; physical archival/deletion policy remains a future CAP concern | `EXPLICITLY_DEFERRED` — deletion is not needed for authority correctness and deferral preserves Replay |
| implementation choice and testing | separately authorized CDP after active successor | `EXPLICITLY_DEFERRED` — CAP defines behavior but cannot implement it |
| deployment scheduling | existing release discipline after CDP Certification | `EXPLICITLY_DEFERRED` — deployment is operational, not a missing Constitutional norm |

Every `CONTRACT_IMPACT_UNRESOLVED`, `INVARIANT_IMPACT_UNRESOLVED`,
`PRODUCTION_PATH_IMPACT_UNRESOLVED`, and `OWNER_IMPACT_UNRESOLVED` item from
G76-01 receives an exact proposed resolution. Deferrals do not affect
authority, topology, current-state consistency, migration safety, or rollback
correctness.

## Deterministic Algorithms

### Crash-consistent commit algorithm

1. Validate exact runtime root and current authority state.
2. Validate the requested transition against the closed state matrix.
3. Create required immutable Candidate, Challenge, Decision, Event, Replay,
   CRO, and Certification artifacts using content-derived names.
4. Flush each new artifact and sync its containing directory.
5. Construct the complete proposed authority state with exact predecessor
   identity/hash and incremented revision.
6. Validate the proposed state and all referenced evidence before mutation.
7. Acquire one operating-system-managed exclusive lock on the stable existing
   state-directory `.cutover.lock`; the lock must release automatically on
   process death.
8. Re-read current state under the lock and require exact predecessor equality.
9. Write the proposed state to a same-directory temporary file, flush it,
   atomically replace `active-cutover.json`, and sync the directory.
10. Read back through the public V2 validator.
11. Release the lock.

Crash outcomes are closed:

~~~text
crash before atomic replace
-> predecessor authority state remains current
-> any new immutable artifacts are unreferenced evidence only

crash after atomic replace and directory sync
-> successor authority state is current

corrupt/missing state or uncertain durability
-> fail closed; no automatic repair or inferred head
~~~

### Active-state validation algorithm

1. Resolve the exact runtime-root state path.
2. Require V2 version, identity, hash, revision, and predecessor lineage.
3. Validate the closed state and transition combination.
4. Resolve every non-null reference below the same runtime root.
5. Revalidate exact Candidate, Challenge, Decision, Event chain, Replay, CRO,
   terminal Certification, migration provenance, and rollback act.
6. Require every identity/digest/state/root/topology equality.
7. Require `CUTOVER_ACTIVE` and `activation_consumed == false` for production.
8. Return active only for the duration of the validated production call.

### Migration algorithm

Migration is performed only by later CDP implementation under the same exact
state-path lock:

| Existing root state | V2 transition |
|---|---|
| no state | no implicit state; owner may later create Candidate/Challenge and first `RELEASE_CONTROL_PENDING` state |
| valid V1 active | require exact new Human reaffirmation Decision, V2 Replay/CRO, V2 terminal Certification, and V1 state identity/hash; atomically replace same path with V2 `CUTOVER_ACTIVE` |
| valid V1 rolled back | preserve V1 provenance; atomically replace with V2 `CUTOVER_ROLLED_BACK`; new Decision required for activation |
| malformed/corrupt V1 | fail closed; no migration |
| unsupported version | fail closed |
| string-only release identity | historical evidence only; never sufficient for V2 |

Mixed active V1 and V2 current states are impossible at one root because the
same state path is replaced once. Old V1 validators reject V2 and therefore
fail closed after migration. V2 validators reject unmigrated V1 for active
production but may consume it only inside the exact migration transition.

### Constitutional rollback algorithm

If CAP later rolls back the active Constitutional successor, all V2 evidence
remains readable and immutable. A V1 runtime may become active only when an
exact preserved V1 state and Certification were previously eligible and an
exact Human rollback act authorizes the inverse transition. If no eligible V1
state exists, the predecessor runtime remains inactive. V2 state is never
silently translated into V1 authority.

## Responsibility Boundaries

### Release/cutover owner contract V2

The exact owner identity remains
`RELEASE_CUTOVER_PRODUCTION_STATUS_OWNER`. Revision 2 proposes these bounded
positive responsibilities:

| Sub-responsibility | Exact permitted act |
|---|---|
| Candidate preparation | bind governed release evidence, environment, root, and topology |
| Human challenge preparation | issue one exact next-act Challenge; no Human outcome |
| release payload interpretation | validate only the closed Decision or rollback payload against Challenge |
| immutable evidence custody | create-once persistence and read-back of exact artifacts |
| owner-local Replay custody | reconstruct only from referenced immutable evidence |
| Certification preparation | assemble inputs for independent release/HIC Certification owners |
| production-status transition | perform only a validated closed state transition under one lock |
| active-state custody | validate one current authority state at the exact root |

The same owner has these explicit negative capabilities:

- cannot produce or infer the Human act;
- cannot authenticate the Human actor;
- cannot act as HIC or CHE;
- cannot add HIC semantics or create a transport surface;
- cannot Ratify or amend the Constitution;
- cannot self-certify terminal evidence;
- cannot activate from Candidate, Decision, Replay, or CRO evidence alone;
- cannot deploy, invoke a Worker, execute product work, or mutate a repository;
- cannot make Replay authoritative or give CRO control;
- cannot create a second current head, path, owner chain, or HIC family; and
- cannot repair, infer, or automatically migrate corrupt state.

Sub-responsibilities are capabilities of one existing owner identity, not new
nodes in the production chain. Certification ownership remains separate even
when the release/cutover owner prepares its inputs.

### Complete owner sequence

| Responsibility | Exact owner | Revision 2 boundary |
|---|---|---|
| define proposal successor | Constitutional Governance | Revision 2 only; no active norm |
| assess Revision 2 | affected Constitutional owners through G70-03 | required next CAP stage |
| ratify | Human Authority | prohibited until resolved assessment |
| prepare Candidate/Challenge | release/cutover owner contract V2 | evidence and next-act only |
| transport/present exact act | same canonical CLIA HIC family | mechanical; phase-bound |
| admit exact act | sole CHE | no release semantics |
| decide release | authenticated Human Authority | exact non-transferable act |
| validate release payload | release/cutover owner contract V2 | closed schema only |
| persist immutable evidence | release/cutover evidence custody sub-responsibility | no current authority without state |
| reconstruct Decision | owner-local Replay custodian | read-only |
| observe Replay | passive CRO | non-authoritative |
| certify G69-19 V2 package | release and HIC Certification owners | independent terminal Certification |
| transition current status | release/cutover production-status owner | one atomic state only |
| deploy implementation | existing deployment discipline | only after CDP Certification |

### Residual Risks

| Residual risk | Disposition | Constitutional treatment |
|---|---|---|
| filesystem lacks required atomic replace, file sync, directory sync, or crash-released lock | bounded implementation risk | CDP preflight must prove primitives; otherwise fail closed and do not deploy |
| Human authentication provider unavailable | bounded operational availability risk | existing G69-07 authority contract fails closed; no alternate actor path |
| immutable evidence accumulates | deferred storage risk | retain evidence; future archival/deletion requires separate CAP because deletion is not necessary for V2 authority |
| an environment remains on V1 | explicit migration state | it cannot use V2 authority; upgrade is root-local and governed |
| multiple runtime roots require activation | explicit operational scope | each root needs its own Candidate, Human Decision, Certification, and state; no cross-root inference |
| CDP implementation defects | future implementation risk | focused validation, Governance conformance, Certification, and deployment cutover remain mandatory |
| release-control phase reduces availability while inactive | intentional fail-closed behavior | only release-control acts are admitted until exact active state exists |

No residual risk changes the proposed owner, authority, topology, lifecycle,
current-state, migration, or rollback norm. None authorizes a compatibility
bypass.

### Reuse Impact Assessment

1. **Which certified Constitutional capabilities are reused?**

   Human Authority; `CanonicalHumanAuthorityActV1`; `AUTHORIZATION` and
   `CANCEL`; the one `clia` surface; `CLIA_PRODUCTION_HIC_FAMILY`; sole CHE;
   owner-issued next-act and Continuation binding; canonical JSON and SHA-256;
   owner-local Replay; passive CRO; G69-19 terminal Certification, atomic
   single-state replacement, validation, and rollback; release/cutover
   production-status ownership; fail-closed validation; CDP; CAP; G70-03
   assessment; G75-02 Gap evidence; and G48 reporting.

2. **Which proposal sections were revised?**

   Orchestration Entry Point, Human ingress, Public Validators, Canonical Data
   Models, persistence, current-state lifecycle, G69-19 relationship,
   revocation, supersession, expiry, migration, production rollback,
   Constitutional rollback, Responsibility Boundaries, topology proof, and
   residual-risk treatment. Candidate and core Decision identity semantics,
   Human Authority, Replay read-only, CRO passive, and CAP/CDP separation are
   retained.

3. **Does any certified capability become unreachable?**

   No. Before Activation this proposal changes nothing. Under the proposed
   successor, inactive environments gain an exact route to create the missing
   Human Decision through the same HIC/CHE path. Active production remains
   reachable only from `CUTOVER_ACTIVE`. Historical V1 evidence remains
   readable, and invalid or unmigrated state fails closed rather than becoming
   a hidden route.

4. **Does the revision create a parallel production path?**

   No. Release-control and active-production are mutually exclusive phases of
   the same `clia` surface, same HIC family, sole CHE, and one ordered owner
   chain. No direct-CHE caller, second launcher, forwarding surface, Worker
   route, or alternate active-state path is permitted.

5. **Does it decrease or increase the number of production paths?**

   Neither. The proposed and current count is exactly one production path,
   with zero parallel production paths. The release-control phase is the
   pre-activation segment of that path, not a second execution path.

# 3. Constitutional Self-Assessment

## Verified

- G76-00 and G76-01 are authenticated and byte-identical to their committed
  forms.
- Revision 2 binds Revision 1 and its assessment by exact identity and digest.
- Revision 1 is not modified.
- Revision 2 remains `PROPOSAL_ONLY_UNASSESSED`.
- The pre-cutover Human act has one exact route through the same `clia`, HIC
  family, and sole CHE.
- The release-control phase is exclusive, structured, challenge-bound, and
  transport only.
- The release/cutover owner has a closed positive and negative successor
  contract.
- Human Authority, HIC, CHE, Certification, Replay, and CRO responsibilities
  remain separate.
- Exactly one V2 authority-state file is the current head for Decision,
  Certification, activation, suspension, and rollback.
- Immutable evidence has no current authority unless referenced by that state.
- Crash consistency has one exact commit point and deterministic pre/post
  crash outcomes.
- Revocation closes production atomically before separately authorized
  rollback.
- Supersession cannot race an active cutover.
- Activation-eligible Decisions cannot expire asynchronously.
- G69-19 Certification V2, state V2, V1 migration, production rollback, and
  Constitutional rollback rules are exact.
- Every unresolved G76-01 impact is marked `RESOLVED` or
  `EXPLICITLY_DEFERRED` with Constitutional justification.
- Deferred items are implementation, deployment, or non-authoritative storage
  concerns and do not leave a missing norm.
- One CHE, one HIC family, one owner chain, one production path, and zero
  parallel production paths remain proposed.
- No runtime, production, Constitutional, workflow, Replay, CRO, release,
  deployment, or active-state mutation occurred.

## Not Verified

- Revision 2 has not received its own G70-03 Impact Assessment.
- No Human Ratification exists for Revision 2.
- No amendment Certification, Publication, or Activation exists.
- Revision 2 is not active Constitutional law and does not authorize CDP.
- No V2 API, model, profile, owner contract, persistence, migration, Replay,
  CRO, Certification, validator, state transition, or deployment is
  implemented.
- No Candidate, Challenge, Decision, Event, Replay, CRO observation, terminal
  Certification, active state, suspension, migration, or rollback is created.
- Filesystem primitives, implementation feasibility, test behavior, and live
  CLIA behavior remain for a future CDP generation after the CAP successor is
  active.
- Existing known hook drift, partial coverage, distributed approval
  enforcement, dormant governance memory, deployment, and rollback
  limitations remain visible and unchanged.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| G48 structure | six exact sections and seven required Code Evidence subsections | deterministic heading review | `PASS` |
| authenticated baseline | commit, tree, subject, parent, clean start | exact Git inspection | `PASS` |
| G76-00 immutability | worktree and committed SHA-256 equality | exact byte comparison | `PASS` |
| G76-01 immutability | worktree and committed SHA-256 equality | exact byte comparison | `PASS` |
| predecessor proposal binding | exact identity, revision, digest | proposal-lineage review | `PASS` |
| predecessor assessment binding | exact identity, digest, classification | assessment-lineage review | `PASS` |
| proposal-only stage | fixed status; later CAP stages absent | stage review | `PASS` |
| pre-cutover Human ingress | one phase-bound `clia`/HIC/CHE route | deterministic route review | `PASS` |
| HIC transport-only boundary | Challenge presentation and exact transport; negative capabilities | boundary review | `PASS` |
| owner contract | closed positive duties, handoffs, and negative capabilities | owner matrix review | `PASS` |
| current authority | one exact V2 state; immutable evidence non-authoritative | state-model review | `PASS` |
| atomic consistency | Decision, Certification, activation, suspension, rollback in one head | transition review | `PASS` |
| crash consistency | artifact sync, single replace, directory sync, crash-released lock | failure-outcome review | `PASS` |
| revocation | atomic suspension closes active gate | lifecycle review | `PASS` |
| supersession | prohibited active; exact inactive successor | lifecycle review | `PASS` |
| expiry | null required for activation eligibility | time-authority review | `PASS` |
| G69-19 successor | exact V2 Certification/state and per-call validation | contract review | `PASS` |
| migration | closed no-state/V1-active/V1-rollback/invalid dispositions | migration matrix review | `PASS` |
| production rollback | separate exact Human act and atomic state transition | rollback review | `PASS` |
| Constitutional rollback | preserved V1 eligibility or inactive fail-closed result | rollback review | `PASS` |
| every G76-01 impact | Resolution Matrix | complete row comparison | `PASS` |
| explicit deferrals | retention, implementation, deployment only | authority-effect review | `PASS` |
| residual risks | bounded and fail-closed | risk review | `PASS` |
| one CHE / one HIC / one chain / one path / zero parallel | exact topology and prohibited alternatives | topology review | `PASS` |
| Ratification/Certification/Activation | prohibited and absent | scope review | `NOT_APPLICABLE` |
| implementation/runtime tests | proposal-only generation | scope review | `NOT_APPLICABLE` |
| no runtime/production/Constitutional mutation | report-only status inventory | Git and filesystem review | `PASS` |
| document consistency | G69-07/13/18/19, G70-02/03/04/07, G72-G76 | cross-document review | `PASS` |
| whitespace integrity | complete untracked report diff | `git diff --no-index --check` | `PASS` |

# 5. Repository Mutation Summary

Modified files:

- added
  `docs/governance/G76_02_CONSTITUTIONAL_AMENDMENT_PROPOSAL_REVISION_2_RELEASE_DECISION_ARTIFACT_V1.md`
  as the sole G76-02 artifact.

Runtime, operational, and active Constitutional artifacts created:

- None. No CAP assessment, Ratification, Certification, Publication,
  Activation, Candidate, Challenge, Decision, Event, Replay, CRO observation,
  terminal Certification, migration, runtime root, active state, suspension,
  or rollback state was created.

Unchanged subsystems:

- active Constitution, G76-00, G76-01, Human Authority, Governance,
  Production Cutover, production status, release, deployment, CDP, CAP, CLIA,
  HIC, CHE, Conversation, Platform, Authorization, Workers, execution,
  results, Replay, CRO, runtime, configuration, schema, policy, baseline, and
  PCBV31;
- all tests and historical/runtime evidence; and
- every G0 through G76-01 artifact, status, and verdict.

API compatibility:

- No current API, schema, model, validator, serializer, command, profile,
  owner, caller, workflow, route, production, activation, rollback, or
  Constitutional contract changed. Revision 2 specifies proposed successor
  responsibilities only.

Boundary preservation:

- This proposal grants no Human decision, Ratification, Certification,
  Publication, Activation, implementation, deployment, routing, Replay, CRO,
  or mutation authority.
- G76-00 remains immutable superseded proposal evidence; G76-01 remains its
  exact assessment.
- Revision 2 must receive a new Impact Assessment before Ratification.
- The one-CHE, one-HIC-family, one-owner-chain, one-production-path topology
  remains unchanged, with zero parallel production paths.

Unrelated pre-existing changes:

- None observed. The worktree was clean at revision start.

# 6. Certification Verdict

CONSTITUTIONAL_CAP_PROPOSAL_REVISION_2_ESTABLISHED
