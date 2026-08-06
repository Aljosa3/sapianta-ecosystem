# 1. Implementation Summary

Generation: G76-04

Report and proposal identity:
G76_04_CONSTITUTIONAL_AMENDMENT_PROPOSAL_REVISION_3_RELEASE_DECISION_ARTIFACT_V1

Proposal revision: 3

Proposal status: `PROPOSAL_ONLY_UNASSESSED`

Amendment kind: `ADDITION`

Constitutional baseline: G0 through G76-03. G76-02 is immutable Proposal
Revision 2. G76-03 is its direct authenticated
`UNRESOLVED_CONSTITUTIONAL_IMPACT` assessment. Every predecessor remains
closed and unchanged.

Authenticated repository identity:

- Commit: `c0245a2d95fd73c4cbbb61908a39e0dd38763a6f`
- Tree: `ba4b730f7860f368311eeaa0f10c463257773a6f`
- Subject: `G76-03: assess revision 2 release decision CAP proposal`
- Immediate parent: `d47f5cb7084412d8255ab8654d20cb9a87afdacd`
- Revision-start worktree state: clean
- Authenticated G76-02 SHA-256:
  `994cce717fc36e07b3510cc988f04693613fe9636fad97735c5b95beb7b53463`
- Authenticated G76-03 SHA-256:
  `452c923f2ed5e71d87c9cb73f4940f72fda9d0ef2dda98487d9f98ec32a62e26`

Previous proposal and assessment binding:

| Field | Exact binding |
|---|---|
| previous proposal identity | `G76_02_CONSTITUTIONAL_AMENDMENT_PROPOSAL_REVISION_2_RELEASE_DECISION_ARTIFACT_V1` |
| previous proposal revision | `2` |
| previous proposal digest | `sha256:994cce717fc36e07b3510cc988f04693613fe9636fad97735c5b95beb7b53463` |
| previous assessment identity | `G76_03_CONSTITUTIONAL_IMPACT_ASSESSMENT_RELEASE_DECISION_ARTIFACT_REVISION_2_V1` |
| previous assessment digest | `sha256:452c923f2ed5e71d87c9cb73f4940f72fda9d0ef2dda98487d9f98ec32a62e26` |
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
evidence; G75-02 derivability audit; G76-00 through G76-03 proposal and impact
lineage.

Reporting date: 2026-08-06.

Objective:

Create the exact Revision 3 successor of G76-02. Resolve the complete G76-03
impact as one lifecycle model: active Human lifecycle control, V1-to-V2/V3
migration Human control, in-flight production exclusion, authoritative state
commit, deterministic receipt, retry, and Human acknowledgment. Preserve one
CLIA, one HIC family, one CHE, one owner chain, one production path, and zero
parallel production paths. Do not assess Revision 3, ratify, certify, publish,
activate, implement, deploy, or mutate runtime state.

Revision result:

Revision 3 retains Revision 2's Candidate, Decision, bounded owner, immutable
evidence, owner-local Replay, passive CRO, one authority-state head, exact
G69-19 successor, expiry prohibition, and rollback state model. It supersedes
the mutually exclusive two-phase ingress and incomplete migration/receipt
rules with one control-capable lifecycle:

1. Every authority state carries exactly one current owner-issued
   `CONSTITUTIONAL_LIFECYCLE_CONTROL_CHALLENGE_V3`. The same `clia` surface,
   same `CLIA_PRODUCTION_HIC_FAMILY`, and sole CHE can transport its exact
   structured Human act while inactive, active, suspended, rolled back, or in
   V1 migration. Active ordinary product transport and lifecycle control use
   one submission service and one CHE; control capability has deterministic
   priority but is not a second launcher, HIC, CHE, owner chain, or execution
   path.
2. Every active production call holds a shared lease on the exact authority
   generation from validation until the owner call completes. Every lifecycle
   transition obtains the exclusive generation barrier, blocks new shared
   leases, drains existing calls to zero, revalidates the predecessor, commits
   one state replacement, and then releases. A revocation acknowledgment
   therefore cannot coexist with an in-flight call under the revoked
   generation.
3. Human control authority becomes current only when the successor authority
   state commits. A deterministic receipt derives from the Human act,
   Challenge, Transition, and read-back successor state. HIC may acknowledge
   `COMMITTED` only after validating that receipt. A crash before commit yields
   no acknowledgment and leaves the predecessor current; a crash after commit
   permits exact idempotent receipt reconstruction and retry.
4. V1-active migration begins with certified zero-in-flight quiescence and a
   V1 restart/writer fence. The handover acquires both the legacy V1 lock and
   the V3 exclusive barrier before atomically replacing the same state path
   with `V1_MIGRATION_CONTROL_PENDING`. Production is then closed, the same
   CLIA/HIC/CHE carries the exact reaffirmation act, and only a complete V3
   package may reactivate production.

Proposed successor identity:

`AI_GOL_CONSTITUTIONAL_CORE_BASELINE_V1_1_RELEASE_DECISION_ARTIFACT_REVISION_3_PROPOSED`

Proposed successor version:

`V1.1-RELEASE-DECISION-ARTIFACT-R3`

Proposal target remains the one additive L1 canonical artifact-definition
successor of `AI_GOL_CONSTITUTIONAL_CORE_BASELINE_V1_ESTABLISHED` under
`CONSTITUTIONAL_GOVERNANCE_OWNER`.

Proposal boundary:

Revision 3 remains `PROPOSAL_ONLY_UNASSESSED`. It must receive a new complete
G70-03 Impact Assessment. G76-03 assesses Revision 2 only and cannot authorize
Ratification of changed content. No Human Ratification, amendment
Certification, Publication, Activation, CDP implementation, release act,
deployment, state transition, or runtime behavior is introduced.

Added artifact:

- `docs/governance/G76_04_CONSTITUTIONAL_AMENDMENT_PROPOSAL_REVISION_3_RELEASE_DECISION_ARTIFACT_V1.md`
  — this proposal-only G48 Revision 3 successor.

Intentionally unchanged modules and state:

- G76-00 through G76-03 bytes, identities, statuses, and verdicts;
- every active G0 through G75-02 Constitutional artifact;
- Human Authority, Production Cutover, production status, release, CLIA, HIC,
  CHE, Replay, CRO, CDP, CAP, Governance, routing, workflow, owner-chain,
  deployment, configuration, and runtime behavior;
- all Candidate, Challenge, Decision, Event, Transition, Receipt, Replay, CRO,
  Certification, migration, active-state, suspension, and rollback artifacts;
  and
- all code and tests.

Architectural boundaries preserved by the proposal stage:

- exactly one CLIA remains;
- exactly one canonical production HIC family remains;
- exactly one CHE remains;
- HIC remains transport only;
- exactly one production owner chain remains;
- exactly one production path remains;
- zero parallel production paths remain;
- Replay remains owner-local, deterministic, read-only, and
  non-authoritative;
- CRO remains passive and non-authoritative; and
- no proposal content is active authority.

# 2. Code Evidence

## Public API

G76-04 adds or changes no runtime API. After a complete CAP successor becomes
active, a later CDP generation would be bounded by Revision 2's proposed
surfaces plus these Revision 3 successor responsibilities:

~~~text
create_constitutional_lifecycle_control_challenge_v3(...)
validate_constitutional_lifecycle_control_admission_v3(...)
acquire_constitutional_authority_generation_shared_lease_v3(...)
acquire_constitutional_authority_generation_exclusive_barrier_v3(...)
commit_constitutional_lifecycle_control_transition_v3(...)
create_constitutional_lifecycle_control_receipt_v3(...)
reconstruct_constitutional_lifecycle_control_receipt_v3(...)
acknowledge_constitutional_lifecycle_control_receipt_v3(...)
create_constitutional_v1_runtime_quiescence_proof_v3(...)
create_constitutional_v1_writer_fence_proof_v3(...)
begin_constitutional_v1_to_v3_migration_control_v3(...)
validate_constitutional_v1_to_v3_migration_control_v3(...)
~~~

These names define proposed duties, not implemented functions.

The existing `CanonicalHumanAuthorityActV1` remains the only Human decision
carrier. Revision 3 adds no authority kind. It binds existing kinds to exact
Challenge actions:

| Lifecycle control action | Existing Human authority kind |
|---|---|
| initial or migration release approval/rejection | `AUTHORIZATION` |
| revoke current Release Decision | `CANCEL` |
| authorize Production Cutover rollback | `AUTHORIZATION` |
| cancel pending migration | `CANCEL` |
| retire eligible inactive Decision | `AUTHORIZATION` |

## Orchestration Entry Point

### One control-capable CLIA lifecycle

`CLIA_CONSTITUTIONAL_PRODUCTION_PROFILE_V3` retains interface identity `CLIA`,
family `CLIA_PRODUCTION_HIC_FAMILY`, the one repository `clia` launcher, one
submission service, and the sole CHE.

Every valid V3 authority state references one current Lifecycle Control
Challenge. CLIA mechanically presents that Challenge with its normal
presentation. A Human may supply either:

- one exact structured `HUMAN_AUTHORITY_ACT` targeting the current Challenge;
  or
- when and only when state is `CUTOVER_ACTIVE` and no exclusive control
  transition is pending, one ordinary exact product Human act.

Both forms follow:

~~~text
Human
-> same clia launcher
-> same CLIA HIC family
-> one submission service
-> sole CHE
-> exact expected owner in one certified owner chain
~~~

Capability discrimination is mechanical envelope validation at CHE. HIC does
not interpret `CANCEL`, `AUTHORIZATION`, release meaning, product meaning, or
transition semantics. A structured control act is handed to the exact
release/cutover owner; an ordinary product act follows the existing downstream
owner chain. Neither can be reinterpreted as the other.

### Deterministic control priority

The lifecycle status owner exposes one admission decision:

~~~text
invalid/corrupt/ambiguous state
-> admit nothing

exclusive transition requested or held
-> block new product leases
-> admit only the exact current lifecycle control transaction

state is inactive, pending, suspended, rolled back, or migration control
-> admit only exact Challenge-bound Human control act

state is CUTOVER_ACTIVE and no exclusive transition pending
-> admit exact Challenge-bound control act with priority
   OR ordinary product act under shared generation lease
~~~

“Priority” means a valid control transaction request prevents new shared
production leases before transition processing. It does not allow HIC to
choose the Human outcome or invoke the transition.

### Active revocation and rollback

At `CUTOVER_ACTIVE`, the current Challenge contains exact actions
`REVOKE_RELEASE_DECISION` and `ROLLBACK_PRODUCTION_CUTOVER`, each with fixed
kind, target, scope, actor, state identity/hash/revision, Decision identity,
environment, root, request, Continuation, and idempotency binding.

~~~text
exact active Challenge
-> same CLIA/HIC/CHE transports Human control act
-> release/cutover owner requests exclusive generation barrier
-> new product leases blocked
-> existing product leases drain to zero
-> predecessor state and Human act revalidated
-> immutable Event/Transition evidence prepared
-> one authority-state replacement
-> public read-back validation
-> deterministic COMMITTED receipt
-> CHE response
-> HIC acknowledgment
~~~

Revocation commits `CUTOVER_SUSPENDED_DECISION_REVOKED`. Rollback commits
`CUTOVER_ROLLED_BACK`. If revocation precedes rollback, the successor suspended
state carries a new exact rollback Challenge through the same path.

### V1-to-V3 migration control

Migration does not attempt to run V1 and V3 transition writers concurrently:

~~~text
valid V1 active state
-> deployment/release owner stops admission of new V1 sessions
-> wait for zero V1 HIC submissions, production owner calls, and transitions
-> create V1_RUNTIME_QUIESCENCE_PROOF_V3
-> stop all V1 writer processes and install exact restart fence
-> create V1_WRITER_FENCE_PROOF_V3
-> acquire legacy V1 .cutover.lock using V1 semantics
-> acquire V3 exclusive authority barrier
-> revalidate V1 state and both proofs
-> atomically replace same state path with V1_MIGRATION_CONTROL_PENDING
-> release legacy lock; retain restart fence
-> same clia/HIC/CHE transports exact migration reaffirmation act
-> commit Decision/Replay/CRO/Certification states through V3 barrier
-> CUTOVER_ACTIVE only after complete V3 read-back
~~~

Old V1 readers reject the new state. The restart fence prevents a V1 writer
from returning after handover. V3 never assumes its lock excludes a V1 writer;
the dual-lock, quiescence, and fence form the exact handover boundary.

## Semantic Reductions

### One lifecycle control reduction

~~~text
current authority state
+ current Challenge
+ exact same-CLIA/HIC/CHE Human Act
+ exact expected owner
+ exact control idempotency identity
-> one lifecycle control transaction

wrong Challenge, state, actor, target, kind, scope, request, Continuation,
root, revision, or idempotency identity
-> fail closed before exclusive barrier and before acknowledgment
~~~

### Generation barrier reduction

~~~text
ordinary active production call
-> validate CUTOVER_ACTIVE
-> acquire shared lease bound to state identity/hash/revision
-> hold lease through complete owner call
-> release

lifecycle control or migration transition
-> request exclusive barrier
-> block new shared leases
-> wait for shared lease count == 0
-> acquire exclusive generation
-> revalidate predecessor
-> commit or fail closed
~~~

No production call may begin under one generation and execute after a
successor generation commits. A barrier timeout produces no commit and no
Human success acknowledgment.

### Human authority effectiveness reduction

~~~text
Human control act issued
-> authorization input exists
-> current authority unchanged

successor state atomically committed and read back
-> control act becomes effective at successor committed_at
-> deterministic receipt may be acknowledged

no validated successor read-back
-> no COMMITTED acknowledgment
-> predecessor remains current or validation fails closed
~~~

The rule does not deny the Human act. It separates Human authorization from
the exact current-state transition it authorizes and makes that separation
visible to the Human.

### Idempotent retry reduction

~~~text
retry same act identity/digest + same control idempotency identity
AND successor state already binds exact act/transition
-> reconstruct and return same COMMITTED receipt
-> no second transition

retry same act and predecessor still current
-> repeat deterministic transition attempt

retry collides with different current act/state
-> CONFLICT; fail closed with exact current-state reference
-> no substitution or inferred success
~~~

### Migration safety reduction

~~~text
valid V1 state
AND zero-in-flight proof
AND V1 writer/restart fence
AND legacy lock held
AND V3 exclusive barrier held
AND exact predecessor equality
-> one atomic handover to V1_MIGRATION_CONTROL_PENDING

any proof stale, missing, mismatched, or unverifiable
-> no handover; V1 state unchanged or environment remains fail closed
~~~

## Public Validators

Revision 3 successor validators SHALL enforce:

- all Revision 2 identity, schema, owner, evidence, state, Replay, CRO,
  Certification, migration, rollback, and topology rules except where
  explicitly superseded here;
- exactly one current Lifecycle Control Challenge in every V3 authority state;
- exact allowed control actions per state;
- exact same `CLIA` identity, HIC family, submission service, and sole CHE;
- exclusive structured `HUMAN_AUTHORITY_ACT` capability for control;
- no HIC semantic interpretation or workflow invocation;
- control priority without a second route;
- shared production lease identity/hash/revision equality and full-call
  lifetime;
- exclusive barrier ownership, zero shared leases, predecessor revalidation,
  and exact transition;
- Human control act identity/digest and idempotency binding in successor state;
- deterministic receipt reconstruction from committed state;
- HIC success acknowledgment only for validated `COMMITTED` receipt;
- no acknowledgment on timeout, pre-commit crash, uncertain delivery, failed
  read-back, conflict, or rejected transition;
- exact V1 quiescence proof and writer-fence proof owners, identities, digests,
  root, V1 state, process generation, zero counts, and freshness;
- acquisition of both the legacy lock and V3 barrier during handover;
- persisted V1 restart fence until V3 handover is terminal or a governed V1
  rollback completes;
- no in-flight V1 call or writer across state replacement;
- exact 1/1/1/1/0 topology; and
- no direct-CHE caller, second CLIA, second HIC family, forwarding alias,
  compatibility mutation, Replay repair, CRO authority, or automatic state
  repair.

## Canonical Data Models

### Revision 3 format identities

Revision 3 retains Revision 2's V1 Candidate/Decision and V2 evidence/state
schemas except where these exact V3 successors coordinate the complete
lifecycle:

~~~text
CONSTITUTIONAL_LIFECYCLE_CONTROL_CHALLENGE_V3
CONSTITUTIONAL_AUTHORITY_GENERATION_LEASE_V3
CONSTITUTIONAL_AUTHORITY_GENERATION_BARRIER_V3
CONSTITUTIONAL_LIFECYCLE_CONTROL_TRANSITION_V3
CONSTITUTIONAL_LIFECYCLE_CONTROL_RECEIPT_V3
CONSTITUTIONAL_LIFECYCLE_CONTROL_ACKNOWLEDGMENT_V3
CONSTITUTIONAL_V1_RUNTIME_QUIESCENCE_PROOF_V3
CONSTITUTIONAL_V1_WRITER_FENCE_PROOF_V3
CONSTITUTIONAL_RELEASE_CUTOVER_AUTHORITY_STATE_V3
CLIA_CONSTITUTIONAL_PRODUCTION_PROFILE_V3
G69_19_CONSTITUTIONAL_PRODUCTION_CUTOVER_CERTIFICATION_V3
~~~

### Lifecycle Control Challenge

Every state contains a non-null Challenge reference. The immutable Challenge
contains exactly:

~~~text
challenge_version
challenge_identity
challenge_digest
authority_state_identity
authority_state_hash
authority_state_revision
target_environment_identity
target_runtime_root
release_candidate_identity
release_decision_identity
allowed_control_actions
action_to_authority_kind
action_to_authority_scope
expected_owner = RELEASE_CUTOVER_PRODUCTION_STATUS_OWNER
human_actor_identity
session_identity
request_identity
continuation_identity
next_act_identity
control_idempotency_identity
created_at
topology = 1/1/1/1/0
~~~

Allowed actions are closed by current state:

| Current state | Allowed Challenge actions |
|---|---|
| `RELEASE_CONTROL_PENDING` | `APPROVE_RELEASE`, `REJECT_RELEASE` |
| `DECISION_APPROVED_CUTOVER_INACTIVE` | `REVOKE_RELEASE_DECISION` |
| `CUTOVER_CERTIFIED_INACTIVE` | `REVOKE_RELEASE_DECISION` |
| `CUTOVER_ACTIVE` | `REVOKE_RELEASE_DECISION`, `ROLLBACK_PRODUCTION_CUTOVER` |
| `CUTOVER_SUSPENDED_DECISION_REVOKED` | `ROLLBACK_PRODUCTION_CUTOVER` |
| `CUTOVER_ROLLED_BACK` | `APPROVE_NEW_RELEASE`, `RETIRE_DECISION` |
| `V1_MIGRATION_CONTROL_PENDING` | `REAFFIRM_RELEASE`, `REJECT_REAFFIRMATION`, `CANCEL_MIGRATION` |
| other inactive lifecycle state | exact next action from the closed Revision 2 transition matrix |

An action absent from the current Challenge cannot be inferred from free text.

### Generation Lease and Barrier

A shared Lease contains state identity/hash/revision, owner call identity,
process generation, acquired time, and crash-released lease handle. It is
ephemeral authority evidence and cannot outlive the complete owner call.

The exclusive Barrier contains target state identity/hash/revision, control
transaction identity, process generation, request time, zero-shared-lease
proof, exclusive owner, and crash-released barrier handle. New shared leases
block once its request is registered. Barrier loss before commit yields no
transition authority.

Multi-process implementations SHALL use one operating-system-supported
shared/exclusive primitive whose lock lifetime is process-crash released. A
platform that cannot provide those semantics is not eligible for V3
deployment.

### Human Control Receipt

`CONSTITUTIONAL_LIFECYCLE_CONTROL_RECEIPT_V3` contains exactly:

~~~text
receipt_version
receipt_identity
receipt_digest
receipt_status = COMMITTED
human_authority_act_identity
human_authority_act_digest
challenge_identity
challenge_digest
control_idempotency_identity
transition_identity
transition_digest
predecessor_state_identity
predecessor_state_hash
successor_state_identity
successor_state_hash
successor_state_revision
effective_at = successor committed_at
readback_validated = true
producing_owner = RELEASE_CUTOVER_PRODUCTION_STATUS_OWNER
topology = 1/1/1/1/0
~~~

Receipt identity/digest derive canonically from the committed act, Challenge,
Transition, and successor state. The successor state already binds act,
Challenge, transition, and idempotency identities/digests, so the same Receipt
can be reconstructed after a post-commit crash without changing authority.

`CONSTITUTIONAL_LIFECYCLE_CONTROL_ACKNOWLEDGMENT_V3` binds the exact Receipt,
CHE response, CLIA session, Human actor, presentation result, and
acknowledgment identity. It proves presentation only. It cannot create or
change the committed transition.

### V1 migration proofs

`CONSTITUTIONAL_V1_RUNTIME_QUIESCENCE_PROOF_V3` contains exact V1 state
identity/hash, root, zero HIC submissions, zero production owner calls, zero
transitions, observed process generation, proof owner, time, identity, and
digest.

`CONSTITUTIONAL_V1_WRITER_FENCE_PROOF_V3` contains the same state/root binding,
complete stopped V1 writer set, disabled restart generation, absent legacy
lock holder, deployment/release owner, time, identity, and digest.

Both proofs are single-use, predecessor-bound, and invalid after any state,
process generation, writer set, restart fence, or root change.

### Lifecycle Revision Matrix

| G76-03 unresolved rule | Revision 2 | Revision 3 successor | Resolution |
|---|---|---|---|
| active control ingress | active selected product transport only | every active state carries Challenge; same CLIA/HIC/CHE accepts exact control capability with priority | `RESOLVED` |
| active revocation route | transition named, route absent | active Challenge -> same CHE -> exact owner -> exclusive barrier -> suspended state | `RESOLVED` |
| active rollback route | act required, route absent | active/suspended Challenge carries exact rollback `AUTHORIZATION` | `RESOLVED` |
| V1 reaffirmation ingress | migration act required, phase absent | atomic migration-pending state carries reaffirmation Challenge through same CLIA/HIC/CHE | `RESOLVED` |
| V1/V2 lock mismatch | proposed V2 lock assumed handover safety | zero-in-flight proof + writer fence + legacy lock + V3 barrier | `RESOLVED` |
| in-flight V1 calls | no quiescence boundary | exact zero-count proof and restart fence before replacement | `RESOLVED` |
| in-flight V3 calls during revoke | per-call validation only | shared full-call leases drained by exclusive transition barrier | `RESOLVED` |
| Human act effectiveness | artifact written before state; effect time unclear | act authorizes; current effect begins only at committed successor time | `RESOLVED` |
| acknowledgment ordering | not defined | only validated post-read-back Receipt may produce HIC acknowledgment | `RESOLVED` |
| pre-commit crash | predecessor active; retry unspecified | no acknowledgment; predecessor current; same idempotency retry allowed | `RESOLVED` |
| post-commit/pre-ack crash | committed state; receipt missing | reconstruct identical Receipt from committed bindings; no second transition | `RESOLVED` |
| conflicting retry | unspecified | fail closed with exact current-state reference; no inferred success | `RESOLVED` |
| one topology | initial route proven; lifecycle route incomplete | all control/product/migration acts use one CLIA/HIC/CHE and one owner chain | `RESOLVED` |

### Active Lifecycle State Diagram

~~~text
                            same CLIA / same HIC / sole CHE
                                         |
                              current control Challenge
                                         |
                     +-------------------+-------------------+
                     |                                       |
          ordinary product act                   structured Human control act
          (CUTOVER_ACTIVE only)                   (every lifecycle state)
                     |                                       |
             shared generation lease                 exclusive barrier request
                     |                                blocks new shared leases
             validate + owner call                    drains existing leases
                     |                                       |
                 release lease                         revalidate predecessor
                                                             |
                                             +---------------+---------------+
                                             |                               |
                                    CANCEL Decision                 rollback AUTHORIZATION
                                             |                               |
                              one atomic state commit             one atomic state commit
                                             |                               |
                         CUTOVER_SUSPENDED_DECISION_REVOKED       CUTOVER_ROLLED_BACK
                                             |                               |
                               new rollback Challenge             new inactive Challenge
                                             +---------------+---------------+
                                                             |
                                                read-back + COMMITTED Receipt
                                                             |
                                                   CHE response -> HIC ACK
~~~

At no point does a control act enter a product owner or a product act enter
the release/cutover transition owner.

### Migration Safety Matrix

| Migration condition | Mandatory evidence/control | Result |
|---|---|---|
| no state | create V3 Candidate/Challenge and first pending state | release control only; no implicit activation |
| V1 active, calls still in flight | quiescence proof impossible | `BLOCKED` |
| V1 active, writer restart enabled | writer-fence proof impossible | `BLOCKED` |
| V1 active, zero calls and writers fenced | acquire legacy lock plus V3 barrier; exact predecessor revalidation | eligible for atomic migration-pending handover |
| crash before handover replace | V1 state remains; proofs must be revalidated before retry | no V3 authority |
| crash after handover replace | V3 migration-pending state current; V1 readers fail closed | same CLIA/HIC/CHE reaffirmation only |
| Human reaffirms | deterministic commit/receipt model | V3 Decision approved; remains inactive until V3 Certification/activation |
| Human rejects/cancels migration | exact control act and Receipt | V3 migration rejected/aborted inactive; no implicit V1 reactivation |
| V1 malformed/corrupt | no valid predecessor proof | `BLOCKED` |
| V1 rolled back | exact preserved provenance, quiescence, and writer fence | V3 rolled-back inactive state; new Decision required |
| V3 active | old V1 process restart attempted | restart fence and unknown-state validation reject; no writer authority |
| Constitutional rollback to V1 | exact eligible preserved V1 state, Human rollback act, reverse quiescence/fence | governed inverse transition or inactive fail-closed result |

### Human Control Acknowledgment Model

The Human-visible outcomes are closed:

| Outcome | Required evidence | Human presentation meaning |
|---|---|---|
| `COMMITTED` | validated successor state plus deterministic Receipt | control act is effective at exact committed time |
| `ALREADY_COMMITTED` | same act/idempotency and reconstructed identical Receipt | prior commit confirmed; no new transition |
| `NOT_COMMITTED` | no validated successor Receipt | no success acknowledgment; predecessor remains current or system is fail closed |
| `CONFLICT` | different current state/act with exact reference | requested act not applied; no substitution |
| `DELIVERY_UNCERTAIN` | CHE/HIC cannot validate returned Receipt | no success acknowledgment; retry same idempotency identity |
| `REJECTED` | exact validation failure before commit | act not applied; exact reason presented mechanically |

Acknowledgment is transport evidence, not release authority. Absence of an
acknowledgment does not reverse an already committed state; idempotent retry
reveals the exact committed Receipt.

## Deterministic Algorithms

### Unified control transaction

1. Load and validate exact current authority state and Challenge.
2. Bind the Human act to the same CLIA Request, CHE Continuation, Challenge,
   expected owner, state generation, and idempotency identity.
3. Register exclusive barrier request; block new production shared leases.
4. Wait for all current shared leases to release. Timeout yields
   `NOT_COMMITTED` and no success acknowledgment.
5. Acquire exclusive barrier and re-read exact predecessor.
6. If the same act/idempotency already committed, reconstruct the same Receipt
   and skip mutation.
7. If current state conflicts, return `CONFLICT` without mutation.
8. Create and sync immutable Event/Transition/Replay/CRO/Certification evidence
   required by the exact transition.
9. Construct and validate successor state with the next current Challenge.
10. Atomically replace the one state file and sync its directory.
11. Read back and validate the complete successor and referenced evidence.
12. Derive/store the deterministic Receipt.
13. Release the exclusive barrier.
14. Return Receipt through CHE; HIC acknowledges only after exact validation.

### Production call lease algorithm

1. Reject if an exclusive transition request is registered.
2. Acquire shared lease.
3. Read and validate `CUTOVER_ACTIVE` state and bind lease to its generation.
4. Execute exactly one existing production owner call while holding lease.
5. Release lease in all success/failure paths.

No lease is an execution authorization by itself. Existing Authorization and
owner contracts remain mandatory.

### Receipt reconstruction algorithm

~~~text
current state binds exact Human act + Challenge + transition + idempotency
AND identities/digests reproduce exact successor state
-> derive canonical Receipt body
-> derive receipt identity/digest
-> return same Receipt

binding absent or mismatched
-> no Receipt; fail closed
~~~

### V1 handover algorithm

1. Validate active or rolled-back V1 state.
2. Stop new V1 session admission.
3. Drain V1 submissions, owner calls, and transitions to zero.
4. Produce exact quiescence proof.
5. Stop V1 writer processes and install restart fence.
6. Produce exact writer-fence proof.
7. Acquire legacy V1 lock using its exact create-exclusive semantics.
8. Acquire V3 exclusive barrier.
9. Revalidate V1 predecessor, proofs, process generation, zero counts, and
   restart fence.
10. Prepare V3 migration Challenge and migration-pending state.
11. Atomically replace the same G69-19 state path and validate read-back.
12. Release locks; retain writer fence.
13. Admit only the exact migration Challenge through same CLIA/HIC/CHE.
14. Apply unified control transaction and acknowledgment rules.

## Responsibility Boundaries

Revision 3 adds coordination responsibilities without transferring authority:

| Responsibility | Exact owner | Boundary |
|---|---|---|
| make lifecycle control decision | authenticated Human Authority | exact act only; no state mutation |
| mechanically present/transport control or product act | one CLIA HIC family | no interpretation or workflow |
| admit exact act/capability | sole CHE | no release or product semantics |
| issue current Challenge | release/cutover owner V3 | exact allowed next acts; no Human outcome |
| validate fixed control payload | release/cutover owner V3 | closed action/target/scope only |
| hold generation leases/barrier | production-status coordination sub-responsibility | synchronization only; no Human or execution authority |
| persist immutable evidence | release/cutover evidence custodian | no current authority without state |
| commit one current state | release/cutover production-status owner | exact authorized transition only |
| create/reconstruct Receipt | release/cutover owner-local evidence custodian | reports committed state only |
| acknowledge Receipt | canonical HIC transport | mechanical presentation only |
| reconstruct Decision/transition | owner-local Replay | read-only, non-authoritative |
| observe reconstruction | passive CRO | observation only |
| certify terminal package | independent release/HIC Certification owners | no activation |
| produce V1 quiescence proof | production-status owner | observed zero activity only |
| produce V1 writer fence | deployment/release owner | process/restart exclusion only |
| activate/deactivate production | production-status owner plus exact Human/release evidence | one state transition under barrier |

Generation barriers do not replace Worker Authorization, execution ownership,
or product validation. Receipts do not replace Human acts. HIC acknowledgment
does not create the transition it reports.

### Reuse Impact Assessment

1. **Which certified Constitutional capabilities are reused?**

   Human Authority; `CanonicalHumanAuthorityActV1`; `AUTHORIZATION` and
   `CANCEL`; the one `clia` surface; `CLIA_PRODUCTION_HIC_FAMILY`; sole CHE;
   exact Request/Continuation/next-act binding; deterministic serialization
   and SHA-256; owner-local Replay; passive CRO; G69-19 terminal Certification,
   active-state validation, atomic replacement, and rollback; release/cutover
   production-status ownership; existing execution Authorization and owner
   chain; fail-closed validation; deployment/release discipline; CDP; CAP;
   G70-03 assessment; and G48 reporting.

2. **Which lifecycle rules were revised?**

   Active control admission, active revocation, active rollback, migration
   reaffirmation admission, control priority, full-call authority leases,
   exclusive transition barriers, V1 quiescence, V1 writer fencing, dual-lock
   handover, Human-act effectiveness, atomic commit/receipt ordering,
   acknowledgment, delivery uncertainty, conflict, and idempotent retry.
   Revision 2's Candidate/Decision schemas, bounded owner, immutable evidence,
   one current state, Replay/CRO boundaries, expiry prohibition, and closed
   lifecycle outcomes remain.

3. **Does any certified capability become unreachable?**

   No. The proposal is inactive now. Under the proposed successor, ordinary
   production remains reachable only under exact `CUTOVER_ACTIVE`; active
   revocation and rollback become reachable through the same HIC/CHE route;
   inactive and migration control remain reachable through that route; and
   historical V1 evidence remains readable. Transition barriers may
   intentionally delay or stop new work while Human control commits, but do
   not remove any certified capability.

4. **Does the proposal create a parallel production path?**

   No. Product and lifecycle-control envelopes enter through one CLIA, one
   submission service, one HIC family, and sole CHE. Control capability is a
   Governance transition on the same owner chain, not an alternate production
   execution path. No direct-CHE caller, second launcher, forwarding alias,
   compatibility route, or second active-state path is permitted.

5. **Does it decrease or increase the number of production paths?**

   Neither. The proposed and current count remains exactly one production
   path with zero parallel production paths.

# 3. Constitutional Self-Assessment

## Verified

- G76-02 and G76-03 are authenticated and byte-identical to their committed
  forms.
- Revision 3 binds Revision 2 and its assessment by exact identity and digest.
- No earlier proposal or assessment is modified.
- Revision 3 remains `PROPOSAL_ONLY_UNASSESSED`.
- One Lifecycle Control Challenge is present in every proposed authority
  state, including active and migration states.
- Active control and ordinary production use one CLIA, HIC family, submission
  service, CHE, and owner chain.
- HIC capability discrimination and acknowledgment remain mechanical.
- Shared full-call leases and the exclusive barrier prevent production calls
  from crossing a committed authority generation.
- V1 handover requires zero-in-flight proof, restart/writer fence, legacy lock,
  and V3 barrier before one same-path replacement.
- Human control authority becomes current only at validated state commit.
- Success acknowledgment requires an exact deterministic post-read-back
  Receipt.
- Pre-commit and post-commit crash outcomes have exact retry semantics.
- Conflict and delivery uncertainty cannot become inferred success.
- Every G76-03 unresolved item maps to one exact proposed lifecycle rule.
- Human Authority, owner-local Replay, passive CRO, independent Certification,
  and production-status ownership remain separated.
- One CLIA, one HIC family, one CHE, one owner chain, one production path, and
  zero parallel production paths remain proposed.
- No runtime, production, Constitutional, workflow, Replay, CRO, release,
  deployment, or active-state mutation occurred.

## Not Verified

- Revision 3 has not received its own G70-03 Impact Assessment.
- No Human Ratification exists for Revision 3.
- No amendment Certification, Publication, or Activation exists.
- Revision 3 is not active Constitutional law and cannot authorize CDP.
- No V3 profile, Challenge, lease, barrier, Transition, Receipt,
  acknowledgment, quiescence proof, writer fence, migration, state,
  validator, Replay, CRO, Certification, or rollback is implemented.
- No platform filesystem/locking primitive has been validated against the
  proposed semantics.
- No Candidate, Decision, Event, state, receipt, runtime root, migration,
  suspension, or rollback is created.
- No implementation, runtime, deployment, migration, or live CLIA test is
  performed because this generation is proposal-only.
- Existing known hook drift, partial coverage, distributed approval
  enforcement, dormant governance memory, deployment, and rollback
  limitations remain visible and unchanged.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| G48 structure | six exact sections and seven required Code Evidence subsections | deterministic heading review | `PASS` |
| authenticated baseline | commit, tree, subject, parent, clean start | exact Git inspection | `PASS` |
| G76-02 immutability | committed/worktree SHA-256 equality | exact byte comparison | `PASS` |
| G76-03 immutability | committed/worktree SHA-256 equality | exact byte comparison | `PASS` |
| predecessor proposal/assessment binding | exact identities, revisions, digests, class | lineage review | `PASS` |
| proposal-only stage | fixed status; later CAP stages absent | stage review | `PASS` |
| active Human lifecycle ingress | current Challenge through same CLIA/HIC/CHE | lifecycle route review | `PASS` |
| active revocation/rollback | exact control actions, barrier, state, Receipt | transition review | `PASS` |
| V1 migration Human ingress | migration-pending state and same HIC/CHE Challenge | migration route review | `PASS` |
| V1/V3 writer exclusion | quiescence, restart fence, legacy lock, V3 barrier | handover review | `PASS` |
| in-flight production exclusion | shared full-call lease plus exclusive drain | generation review | `PASS` |
| Human effectiveness semantics | effective only at committed successor time | authority review | `PASS` |
| acknowledgment ordering | validated Receipt before HIC success acknowledgment | receipt review | `PASS` |
| pre/post-commit crash | predecessor or reconstructable Receipt | failure-outcome review | `PASS` |
| idempotent retry/conflict | exact identity/digest/state reductions | retry review | `PASS` |
| HIC transport-only | mechanical capability/presentation only | boundary review | `PASS` |
| owner consistency | coordination duties bounded; no authority transfer | owner matrix review | `PASS` |
| Replay/CRO consistency | read-only reconstruction and passive observation | boundary review | `PASS` |
| lifecycle revision matrix | every G76-03 item resolved | complete row comparison | `PASS` |
| topology | 1 CLIA / 1 HIC / 1 CHE / 1 chain / 1 path / 0 parallel | exact topology review | `PASS` |
| Ratification/Certification/Activation | prohibited and absent | scope review | `NOT_APPLICABLE` |
| implementation/runtime tests | proposal-only generation | scope review | `NOT_APPLICABLE` |
| no runtime/production/Constitutional mutation | report-only status inventory | Git and filesystem review | `PASS` |
| document consistency | G69-07/13/18/19, G70-02/03/04/07, G72-G76 | cross-document review | `PASS` |
| whitespace integrity | complete untracked report diff | `git diff --no-index --check` | `PASS` |

# 5. Repository Mutation Summary

Modified files:

- added
  `docs/governance/G76_04_CONSTITUTIONAL_AMENDMENT_PROPOSAL_REVISION_3_RELEASE_DECISION_ARTIFACT_V1.md`
  as the sole G76-04 artifact.

Runtime, operational, and active Constitutional artifacts created:

- None. No Impact Assessment, Ratification, amendment Certification,
  Publication, Activation, Candidate, Challenge, Lease, Barrier, Decision,
  Event, Transition, Receipt, acknowledgment, Replay, CRO observation,
  terminal Certification, migration, runtime root, active state, suspension,
  or rollback state was created.

Unchanged subsystems:

- active Constitution, G76-00 through G76-03, Human Authority, Governance,
  Production Cutover, production status, release, deployment, CDP, CAP, CLIA,
  HIC, CHE, Conversation, Platform, Authorization, Workers, execution,
  results, Replay, CRO, runtime, configuration, schema, policy, baseline, and
  PCBV31;
- all tests and historical/runtime evidence; and
- every G0 through G76-03 artifact, status, and verdict.

API compatibility:

- No current API, schema, model, validator, serializer, command, profile,
  owner, caller, workflow, route, production, activation, rollback,
  deployment, or Constitutional contract changed. Revision 3 specifies
  proposed successor responsibilities only.

Boundary preservation:

- This proposal grants no Human decision, Ratification, Certification,
  Publication, Activation, implementation, deployment, routing, Replay, CRO,
  or mutation authority.
- G76-02 remains immutable Proposal Revision 2 evidence; G76-03 remains its
  exact assessment.
- Revision 3 must receive a new Impact Assessment before Ratification.
- The one-CLIA, one-HIC-family, one-CHE, one-owner-chain,
  one-production-path topology remains unchanged, with zero parallel paths.

Unrelated pre-existing changes:

- None observed. The worktree was clean at revision start.

# 6. Certification Verdict

CONSTITUTIONAL_CAP_PROPOSAL_REVISION_3_ESTABLISHED
