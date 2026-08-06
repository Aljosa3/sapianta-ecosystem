# 1. Implementation Summary

Generation: G76-07

Report and proposal identity:
G76_07_CONSTITUTIONAL_AMENDMENT_PROPOSAL_REVISION_4_RELEASE_DECISION_ARTIFACT_V1

Proposal revision: 4

Proposal status: `PROPOSAL_ONLY_UNASSESSED`

Amendment kind: `ADDITION`

Constitutional baseline: G0 through G76-06. G76-04 is immutable Proposal
Revision 3. G76-05 is its direct authenticated
`UNRESOLVED_CONSTITUTIONAL_IMPACT` assessment. G76-06 is the established
Constitutional Artifact Identity Model. Every predecessor remains closed and
unchanged.

Authenticated repository identity:

- Commit: `6d2f7cef480075bcaf144edf4caadc29a3864379`
- Tree: `0e474d190229540848ad383280291f6443f35e4e`
- Subject: `G76-06: establish constitutional artifact identity model`
- Immediate parent: `68f8c643e3daaba63f53512688f0cb090ed23e4b`
- Revision-start worktree state: clean
- Authenticated G76-04 SHA-256:
  `c62f1ecf1ba7985de6613bf44cb00d49384a0e3801f5a0a74ed912fac3a1f648`
- Authenticated G76-05 SHA-256:
  `f9fd5c08ea39504bc6815b3a3e872b62a49549fca15161be3b9214f68203ec38`
- Authenticated G76-06 SHA-256:
  `29f06a93d5b7ce610c161487bc1e3a01f6d7d063b22393e0347b0da20b281dbc`

Predecessor and identity-model binding:

| Field | Exact binding |
|---|---|
| previous proposal identity | `G76_04_CONSTITUTIONAL_AMENDMENT_PROPOSAL_REVISION_3_RELEASE_DECISION_ARTIFACT_V1` |
| previous proposal revision | `3` |
| previous proposal digest | `sha256:c62f1ecf1ba7985de6613bf44cb00d49384a0e3801f5a0a74ed912fac3a1f648` |
| previous assessment identity | `G76_05_CONSTITUTIONAL_IMPACT_ASSESSMENT_RELEASE_DECISION_ARTIFACT_REVISION_3_V1` |
| previous assessment digest | `sha256:f9fd5c08ea39504bc6815b3a3e872b62a49549fca15161be3b9214f68203ec38` |
| previous assessment class | `UNRESOLVED_CONSTITUTIONAL_IMPACT` |
| identity-model identity | `G76_06_CONSTITUTIONAL_ARTIFACT_IDENTITY_MODEL_RECONSTRUCTION_REPORT_V1` |
| identity-model digest | `sha256:29f06a93d5b7ce610c161487bc1e3a01f6d7d063b22393e0347b0da20b281dbc` |
| identity-model verdict | `CONSTITUTIONAL_ARTIFACT_IDENTITY_MODEL_ESTABLISHED` |

Implementation contracts: G48 Constitutional Evidence Reporting Standard V1;
Constitutional Architecture Specification V1; Canonical Layer Model;
Constitutional Invariants; Governance Enforcement Hierarchy; Governance
Lineage Model; G69-07 Canonical Human Authority Act Contract; G69-13 Complete
HIC Conformance and Historical Independence; G69-18 full-branch Replay and
CRO coverage; G69-19 Constitutional Production Cutover; G70-02 Constitutional
Amendment Proposal Contract; G70-03 Constitutional Impact Assessment Contract;
G70-04 Human Ratification Contract; G70-07 CAP Closure; G72-00 Constitutional
Core Baseline; G73-00 Human Constitution; G74-00 and G74-01 Production Cutover
evidence; G75-02 derivability audit; G76-00 through G76-05 proposal and impact
lineage; and G76-06 Constitutional Artifact Identity Model.

Reporting date: 2026-08-06.

Objective:

Create the exact Revision 4 successor of G76-04. Apply the generic identity
rules established by G76-06 to resolve only the three remaining G76-05
identity-model impacts:

1. non-circular Authority State and Challenge derivation;
2. a deterministic synthetic identity for an authenticated legacy G69-19 V1
   state; and
3. a complete canonical Lifecycle Transition artifact definition.

Retain every Revision 3 lifecycle, Human Authority, ingress, generation
barrier, migration, crash, retry, Receipt, acknowledgment, owner, Replay, CRO,
and topology rule that G76-05 did not identify as unresolved. Do not assess,
ratify, certify, publish, activate, implement, deploy, or mutate runtime state.

Revision result:

Revision 4 replaces the circular Revision 3 identity graph with one exact
forward-only construction:

~~~text
finalized predecessor state or exact initialization source
+ current Challenge where a Human control act is consumed
+ exact Human act or exact non-Human transition authority
+ exact idempotency and evidence bindings
-> PREPARED Lifecycle Transition V4
-> next Lifecycle Control Challenge V4
-> successor Authority State V4
-> atomic state commit and read-back
-> Human Control Receipt V4
-> Human acknowledgment presentation
-> owner-local Replay
-> passive CRO observation
~~~

`CONSTITUTIONAL_LIFECYCLE_CONTROL_CHALLENGE_V4` does not contain the identity
or hash of the successor state that will reference it. It binds the already
derived Transition, the exact predecessor basis, the intended subject status
and revision, and the fixed control context. The successor state then contains
the exact Challenge and Transition identity/digest references. This direction
has a deterministic first node and no self-edge or mutual hash dependency.

An authenticated legacy G69-19 V1 state receives no mutation and no invented
native field. After the existing V1 validator accepts its closed schema and
content-derived `state_hash`, Revision 4 deterministically derives one
compatibility identity from the V1 contract/version and exact validated state
hash:

~~~text
legacy-g69-19-state-sha256:<hex>
~~~

The synthetic identity is valid only as a migration predecessor reference.
It does not alter V1, activate V1, create a second current head, or grant
Replay repair authority. The exact runtime root remains separately bound in
the migration proofs and Transition scope; a path is never treated as content
identity.

`CONSTITUTIONAL_LIFECYCLE_CONTROL_TRANSITION_V4` is one immutable PREPARED
intent/evidence artifact. It binds the exact predecessor, consumed Challenge
and Human act when applicable, transition kind, authority basis, evidence,
intended successor status/revision, owner, environment, root, idempotency, and
topology. It intentionally contains no successor-state identity/hash, Receipt,
Replay, CRO, or acknowledgment reference. The authoritative commit occurs
only when the one current state atomically references the validated
Transition. A Receipt derived after read-back proves that commit.

Identity dependency result:

~~~text
Revision 3:
  state -> Challenge -> same state                         CYCLE
  Receipt -> undefined Transition                         INCOMPLETE
  migration proof -> nonexistent native V1 identity       INCOMPLETE

Revision 4:
  predecessor -> Transition -> Challenge -> state
                                      state -> Receipt -> Replay -> CRO
  validated V1 state_hash -> synthetic V1 identity -> migration Transition
                                                               DAG
~~~

Proposed successor identity:

`AI_GOL_CONSTITUTIONAL_CORE_BASELINE_V1_1_RELEASE_DECISION_ARTIFACT_REVISION_4_PROPOSED`

Proposed successor version:

`V1.1-RELEASE-DECISION-ARTIFACT-R4`

Proposal target remains the one additive L1 canonical artifact-definition
successor of `AI_GOL_CONSTITUTIONAL_CORE_BASELINE_V1_ESTABLISHED` under
`CONSTITUTIONAL_GOVERNANCE_OWNER`.

Proposal boundary:

Revision 4 remains `PROPOSAL_ONLY_UNASSESSED`. It must receive a new complete
G70-03 Impact Assessment. G76-05 assesses Revision 3 only, and G76-06 provides
generic identity rules but does not assess this application. No Human
Ratification, amendment Certification, Publication, Activation, CDP
implementation, release act, deployment, state transition, or runtime behavior
is introduced.

Added artifact:

- `docs/governance/G76_07_CONSTITUTIONAL_AMENDMENT_PROPOSAL_REVISION_4_RELEASE_DECISION_ARTIFACT_V1.md`
  — this proposal-only G48 Revision 4 successor.

Intentionally unchanged modules and state:

- G76-00 through G76-06 bytes, identities, statuses, verdicts, and limitations;
- every active G0 through G75-02 Constitutional artifact;
- every Revision 3 lifecycle, Human ingress, owner, barrier, acknowledgment,
  migration-safety, and topology rule except its three expressly superseded
  identity-model definitions;
- Human Authority, Production Cutover, production status, release, CLIA, HIC,
  CHE, Replay, CRO, CDP, CAP, Governance, routing, workflow, owner-chain,
  deployment, configuration, and runtime behavior;
- every Candidate, Challenge, Decision, Event, Transition, Receipt, Replay,
  CRO, Certification, migration, active-state, suspension, and rollback
  artifact; and
- all code and tests.

Architectural boundaries preserved by the proposal stage:

- exactly one CLIA remains;
- exactly one canonical production HIC family remains;
- exactly one CHE remains;
- HIC remains transport only;
- exactly one production owner chain remains;
- exactly one production path remains;
- zero parallel production paths remain;
- one current authority-state head remains at the existing G69-19 path;
- Replay remains owner-local, deterministic, read-only, and
  non-authoritative;
- CRO remains passive and non-authoritative; and
- no proposal content is active authority.

# 2. Code Evidence

## Public API

G76-07 adds or changes no runtime API. After a complete CAP successor becomes
active, a later CDP generation would remain bounded by Revision 3's proposed
surfaces, with only these exact V4 identity-model successors:

~~~text
derive_constitutional_legacy_g69_19_state_identity_v4(...)
create_constitutional_lifecycle_control_transition_v4(...)
validate_constitutional_lifecycle_control_transition_v4(...)
create_constitutional_lifecycle_control_challenge_v4(...)
validate_constitutional_lifecycle_control_challenge_v4(...)
create_constitutional_release_cutover_authority_state_v4(...)
validate_constitutional_release_cutover_authority_state_v4(...)
create_constitutional_lifecycle_control_receipt_v4(...)
reconstruct_constitutional_lifecycle_control_receipt_v4(...)
~~~

These names define proposed duties, not implemented functions. Every
unchanged Revision 3 proposed API responsibility is inherited by exact
reference to G76-04. Revision 4 introduces no new Human authority kind, HIC
capability, CHE route, owner, production caller, or activation function.

## Orchestration Entry Point

Revision 4 retains Revision 3's same-CLIA/HIC/CHE lifecycle. It changes only
the construction order inside the existing release/cutover owner boundary.

### Initial authority-state construction

~~~text
exact validated Release Candidate
+ exact canonical ingress Request/Continuation
+ exact owner-issued correlation/idempotency identities and payload digests
-> INITIALIZE_RELEASE_CONTROL Transition V4
-> initial RELEASE_CONTROL_PENDING Challenge V4
-> initial Authority State V4 revision 1
-> atomic write to the one existing authority-state path
~~~

The initial Transition has no same-type state predecessor. Its exact Candidate,
baseline, ingress, environment, root, owner, and topology are the certified
root evidence required by G76-06. No random identifier is used as artifact
integrity.

### Successor control construction

~~~text
validated current Authority State V4
+ exact current Challenge V4 referenced by that state
+ exact CanonicalHumanAuthorityActV1 and payload digest
+ exact control idempotency identity
+ exact immutable authorization/evidence references
-> PREPARED Transition V4
-> next Challenge V4 derived from the Transition
-> successor Authority State V4 references both
-> exclusive-barrier atomic replacement and read-back
-> COMMITTED Receipt V4
-> CHE response
-> mechanical HIC acknowledgment
~~~

The current Challenge consumed by the Human act and the next Challenge made
current by the successor are distinct artifacts. A state references exactly
one current Challenge. A Transition references the consumed Challenge only
when its authority-basis kind requires a Human act.

### Legacy V1 migration construction

~~~text
read exact G69-19 V1 state at selected runtime root
-> validate closed V1 schema, state_hash, Certification, topology, and status
-> derive deterministic synthetic V1 state identity in memory
-> bind identity + source state_hash + runtime root in quiescence/fence proofs
-> acquire legacy V1 lock and V4 exclusive barrier
-> revalidate exact V1 bytes, identity, hash, proofs, root, and process state
-> PREPARED V1_MIGRATION_HANDOVER Transition V4
-> V1_MIGRATION_CONTROL_PENDING Challenge V4
-> Authority State V4 revision 1 with exact legacy predecessor reference
-> atomic replacement of the same current-state path
~~~

The synthetic identity derivation writes nothing. It is repeated during
validation and Replay from the immutable preserved V1 source evidence. The
existing restart fence prevents a V1 writer from returning after handover.

## Semantic Reductions

### Non-circular state/Challenge reduction

~~~text
Transition identity/digest finalized first
-> Challenge identity payload may reference Transition
-> Challenge identity/digest finalized second
-> successor state identity payload may reference Transition and Challenge
-> state identity/hash finalized third

Challenge contains no successor state identity/hash
Transition contains no successor state identity/hash
-> no state -> Challenge -> state cycle
~~~

The Challenge still binds the intended subject state status, release phase,
revision, environment, root, Decision, owner, actor, session, request,
Continuation, next act, allowed actions, and idempotency scope. The current
state validator supplies the final binding by requiring exact equality with
the Challenge referenced by that state. A stale Challenge is not current
because the new state references a different exact Challenge.

### Transition authority reduction

~~~text
PREPARED Transition validates exact predecessor and authority basis
-> immutable intent/evidence only
-> no current authority change

one validated successor state atomically commits with exact Transition ref
-> Transition is applied by that state at committed_at

read-back state absent, invalid, mismatched, or uncertain
-> no COMMITTED Receipt
-> no Human success acknowledgment
~~~

The Transition does not claim `COMMITTED`. The state is the one mutable head
and sole authority commit point, preserving Revision 2/3 crash consistency.

### Legacy identity reduction

~~~text
exact G69-19 V1 state fails public V1 validation
-> no synthetic identity
-> migration blocked

exact G69-19 V1 state validates
AND its state_hash recomputes from every state field except state_hash
-> canonical legacy identity payload
-> SHA-256
-> legacy-g69-19-state-sha256:<hex>

same validated V1 bytes
-> same identity

different version or state_hash
-> different identity
~~~

The runtime root is excluded from artifact identity because it is a retrieval
and transition scope, not content. It remains mandatory in both migration
proofs and the Transition; moving or substituting content cannot pass because
the exact source hash, derived identity, and root must all match.

### Receipt reduction

~~~text
finalized Human act where applicable
+ consumed Challenge
+ applied Transition
+ read-back successor state
-> Receipt identity/digest

Transition or Challenge depends on Receipt
-> forbidden reverse dependency
~~~

Receipt reconstruction reads the committed state's Transition, consumed-act,
idempotency, and current-state bindings. It creates no new transition and does
not mutate the state.

## Public Validators

Revision 4 successor validators SHALL enforce every Revision 3 validator rule
except the superseded circular identity fields, plus:

- exact G76-06 type namespace, closed payload, SHA-256, self-exclusion,
  predecessor-finalization, identity/digest-pair, owner/type/version, DAG,
  forward-evidence, compatibility, Replay, CRO, and fail-closed rules;
- exact Transition -> next Challenge -> successor state derivation order;
- Challenge absence of successor/current subject state identity and hash;
- Transition absence of successor-state, Receipt, Replay, CRO, and
  acknowledgment identities or digests;
- exact predecessor basis and authority-basis presence rules per transition
  kind;
- state equality with the Transition's intended successor status, phase,
  revision, environment, root, activation-consumed value, and topology;
- state equality with the exact current Challenge subject status, phase,
  revision, environment, root, owner, Decision, and topology;
- initial-state predecessor nullability only for
  `INITIALIZE_RELEASE_CONTROL`;
- authenticated legacy V1 predecessor acceptance only for
  `V1_MIGRATION_HANDOVER` and eligible governed reverse migration;
- public G69-19 V1 validation before synthetic identity derivation;
- exact synthetic namespace and canonical identity payload;
- equality of repeated synthetic identity derivation during handover,
  validation, Receipt reconstruction, Replay, rollback, and audit;
- exact same-root V1 state hash, quiescence proof, writer-fence proof, locks,
  and process generation;
- identity dependency graph acyclicity and deterministic topological order;
- exact identity/digest recomputation for Transition, Challenge, state,
  Receipt, Replay, and CRO observation;
- no placeholder, path, timestamp, UUID, correlation key, or state filename
  used as artifact integrity;
- exact 1/1/1/1/0 topology; and
- no direct-CHE caller, second CLIA, second HIC family, compatibility
  forwarding route, Replay repair, CRO authority, or automatic state repair.

Any missing field, unknown transition kind, wrong presence combination,
unresolved reference, forward reference, self-edge, cycle, hash mismatch,
owner mismatch, stale predecessor, or root mismatch fails closed before state
replacement.

## Canonical Data Models

### Revision 4 format identities

Revision 4 retains every Revision 3 proposed format except these exact
successors:

~~~text
CONSTITUTIONAL_LEGACY_G69_19_STATE_IDENTITY_V4
CONSTITUTIONAL_LIFECYCLE_CONTROL_TRANSITION_V4
CONSTITUTIONAL_LIFECYCLE_CONTROL_CHALLENGE_V4
CONSTITUTIONAL_RELEASE_CUTOVER_AUTHORITY_STATE_V4
CONSTITUTIONAL_LIFECYCLE_CONTROL_RECEIPT_V4
CONSTITUTIONAL_RELEASE_DECISION_REPLAY_V4
CONSTITUTIONAL_RELEASE_DECISION_CRO_OBSERVATION_V4
G69_19_CONSTITUTIONAL_PRODUCTION_CUTOVER_CERTIFICATION_V4
~~~

Lease, Barrier, Candidate, Decision, Event, acknowledgment, quiescence proof,
writer-fence proof, CLIA profile, owner, route, lifecycle states, allowed
actions, and authority kinds remain as defined by Revision 3. Version changes
above exist only where the canonical identity graph or its downstream exact
references change.

### Identity Model Application Matrix

| G76-05 unresolved impact | G76-06 rule | Revision 4 application | Result |
|---|---|---|---|
| state and Challenge mutually hash each other | finalize predecessors first; require DAG; transition evidence forward-only | Transition -> next Challenge -> state; Challenge omits successor state identity/hash | `RESOLVED` |
| legacy V1 state has hash but no native identity | constrained synthetic compatibility identity | fixed namespace and payload over validated V1 contract/version/state hash | `RESOLVED` |
| Transition identity named without body | closed canonical payload; bind owner/role/type/version; exclude self only | exact Transition V4 schema, presence matrix, identity/digest, and validator rules | `RESOLVED` |
| Receipt blocked by state/Transition | commit precedes Receipt | Receipt depends only on finalized act/Challenge/Transition/read-back state | `RESOLVED` |
| Replay/CRO sources unresolved | Replay after source; CRO after Replay | exact V4 source graph, Replay, then passive CRO | `RESOLVED` |

Applied G76-06 generic rules are exactly:

1. separate artifact identity, content integrity, and correlation;
2. use one closed canonical payload;
3. exclude only the artifact's own derived identity/digest fields;
4. finalize predecessors first;
5. bind identity and digest/hash together;
6. bind owner, reference role, type, and version;
7. require a finite DAG;
8. order intent before commit, Receipt before Replay, and Replay before CRO;
9. constrain owner-issued correlation identities;
10. permit reference-only hashes only for closed, resolvable manifests;
11. constrain synthetic compatibility identity by exact namespace and payload;
12. prohibit Replay inference or repair;
13. keep CRO outside authority;
14. fail closed on identity ambiguity; and
15. apply the active schema and owner rules to this exact domain.

### Authority State Derivation Proof

#### Challenge V4 schema

`CONSTITUTIONAL_LIFECYCLE_CONTROL_CHALLENGE_V4` contains exactly:

~~~text
challenge_version
challenge_identity
challenge_digest
basis_transition_identity
basis_transition_digest
basis_predecessor_state_version
basis_predecessor_state_identity
basis_predecessor_state_hash
basis_predecessor_state_revision
subject_state_revision
subject_authority_status
subject_release_phase
target_environment_identity
target_runtime_root
release_candidate_identity
release_candidate_digest
release_decision_identity
release_decision_digest
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

The predecessor state fields are all null only when the basis Transition is
`INITIALIZE_RELEASE_CONTROL`. For a legacy handover they contain the V1
contract version, synthetic identity, source state hash, and source revision
`null` because V1 has no revision. For every V4 successor they contain the
exact V4 predecessor version, identity, hash, and revision.

`release_decision_identity` and `release_decision_digest` are both null only
when the inherited lifecycle state permits no current Decision. Every other
optional field follows the inherited closed state/action matrix.

The Challenge identity payload is every field above except
`challenge_identity` and `challenge_digest`:

~~~text
h = SHA256(canonical_json(challenge_identity_payload))
challenge_identity = "constitutional-lifecycle-challenge-v4-sha256:" + hex(h)
challenge_digest   = "sha256:" + hex(h)
~~~

The Challenge contains no `authority_state_identity` or
`authority_state_hash`. Its subject fields are semantic expectations, not a
forward artifact reference.

#### Authority State V4 identity surface

`CONSTITUTIONAL_RELEASE_CUTOVER_AUTHORITY_STATE_V4` retains the complete
Revision 2 unified state schema and Revision 3 lifecycle bindings, with these
exact fields:

~~~text
state_version
state_identity
state_hash
state_revision
predecessor_state_version
predecessor_state_identity
predecessor_state_hash
applied_transition_reference = {version, identity, digest, producing_owner}
transition_kind
consumed_challenge_reference = null | {version, identity, digest, producing_owner}
applied_human_authority_act_reference = null | {identity, payload_digest, producing_owner}
control_idempotency_identity
authority_status
release_phase
target_environment_identity
target_runtime_root
release_candidate_reference
current_challenge_reference = {version, identity, digest, producing_owner}
release_decision_reference
release_decision_replay_reference
release_decision_cro_reference
terminal_certification_reference
activation_consumed
canonical_hic_family
surface_dispositions
rollback_decision_reference
v1_migration_provenance
topology = 1/1/1/1/0
committed_at
~~~

Revision 4 replaces only Revision 2's scalar `transition_identity`, the
circular Revision 3 Challenge reference semantics, and the implicit
act/idempotency bindings with the closed references listed above. All other
field meanings and presence rules remain exactly as defined by Revision 2/3.

The state identity payload is the complete closed V4 state except
`state_identity` and `state_hash`:

~~~text
h = SHA256(canonical_json(state_identity_payload))
state_identity = "constitutional-release-cutover-state-v4-sha256:" + hex(h)
state_hash     = "sha256:" + hex(h)
~~~

The exact derivation graph is:

~~~text
Transition N -> Challenge N -> State N
                                  |
                                  + exact current Challenge N
                                  + exact act / authority evidence
                                  + exact idempotency identity
                                  |
                                  v
                            Transition N+1
                                  |
                                  v
                            Challenge N+1
                                  |
                                  v
                              State N+1
                                  |
                                  v
                               Receipt
                                  |
                                  v
                               Replay
                                  |
                                  v
                                 CRO
~~~

Every arrow advances to a later artifact. `State N+1` references Transition
N+1 and Challenge N+1; neither references `State N+1`. Topological derivation
therefore succeeds exactly once for every node.

### Legacy V1 Identity Derivation

The canonical synthetic identity payload is exactly:

~~~json
{
  "identity_rule_version": "G76_07_CONSTITUTIONAL_LEGACY_G69_19_STATE_IDENTITY_V1",
  "source_contract": "G69_19_CONSTITUTIONAL_PRODUCTION_CUTOVER_STATE_V1",
  "source_state_version": "<exact validated state_version>",
  "source_state_hash": "<exact validated sha256 state_hash>"
}
~~~

Derivation is:

~~~text
validated = validate existing G69-19 V1 closed state
payload = exact object above from validated
h = SHA256(canonical_json(payload))
synthetic_identity = "legacy-g69-19-state-sha256:" + hex(h)
~~~

The canonical legacy predecessor reference contains exactly:

~~~text
reference_role = LEGACY_CURRENT_STATE_PREDECESSOR
artifact_type = G69_19_CONSTITUTIONAL_PRODUCTION_CUTOVER_STATE_V1
artifact_identity = synthetic_identity
integrity_kind = STATE_HASH
integrity_value = validated.state_hash
producing_owner = RELEASE_CUTOVER_PRODUCTION_STATUS_OWNER
~~~

Both V1 migration proofs and the V4 Transition embed the canonical legacy
predecessor reference. Its rule version, source contract/version, and source
state hash supply the exact payload fields needed for recomputation. The
source V1 state is retained immutably as migration/rollback evidence before
the current path is replaced. Its preserved evidence reference includes exact
source bytes or an immutable same-hash content-addressed copy, exact source
hash, and exact custody owner. Replay reads that evidence and recomputes the
authorized identity; it does not invent or repair it.

The derivation does not include:

- runtime root or filesystem path;
- validation time;
- migration time;
- process identity;
- random UUID;
- current repository commit; or
- any V4 successor, Receipt, Replay, or CRO identity.

Those values either remain separately scoped evidence or occur later in the
graph. Two byte-identical, validator-accepted V1 states have the same
content-addressed identity. Their environments remain distinct through exact
root, deployment, proof, and transition bindings.

### Lifecycle Transition Specification

`CONSTITUTIONAL_LIFECYCLE_CONTROL_TRANSITION_V4` contains exactly:

~~~text
transition_version
transition_identity
transition_digest
transition_stage = PREPARED
transition_kind
authority_basis_kind
predecessor_state_version
predecessor_state_identity
predecessor_state_hash
predecessor_state_revision
consumed_challenge_identity
consumed_challenge_digest
human_authority_act_identity
human_authority_act_digest
control_idempotency_identity
target_environment_identity
target_runtime_root
canonical_ingress_reference
release_candidate_reference
release_decision_reference
lifecycle_event_references
terminal_certification_reference
rollback_decision_reference
legacy_v1_preserved_state_reference
legacy_v1_quiescence_proof_reference
legacy_v1_writer_fence_proof_reference
intended_successor_authority_status
intended_successor_release_phase
intended_successor_state_revision
intended_activation_consumed
producing_owner = RELEASE_CUTOVER_PRODUCTION_STATUS_OWNER
prepared_at
topology = 1/1/1/1/0
~~~

Every reference is either null, one exact closed object, or an explicitly
ordered tuple of those objects. The reference object contains exactly:

~~~text
reference_role
artifact_type_or_contract_version
artifact_identity
integrity_kind = ARTIFACT_DIGEST | STATE_HASH
integrity_value
producing_owner
~~~

`integrity_value` is `sha256:<hex>` and must equal the field named by
`integrity_kind` in the resolved artifact. Nullability is closed by
`authority_basis_kind` and `transition_kind`; unknown combinations fail
closed.

The authority-basis presence matrix is:

| Authority basis | Predecessor | Consumed Challenge | Human act | Mandatory additional evidence |
|---|---|---|---|---|
| `INITIAL_CANDIDATE` | all predecessor fields null | null | null | Candidate plus exact non-null canonical ingress Request/Continuation reference |
| `HUMAN_CONTROL_ACT` | exact V4 state | exact current Challenge | exact `CanonicalHumanAuthorityActV1` | Candidate/Decision/Event/rollback/retirement evidence required by inherited transition kind |
| `TERMINAL_CERTIFICATION` | exact V4 state | null | null | exact approved Decision, Replay/CRO, and terminal Certification |
| `ACTIVATION_AUTHORITY` | exact V4 certified-inactive state | null | null | terminal Certification plus exact inherited release/activation evidence |
| `LEGACY_V1_HANDOVER` | exact synthetic legacy V1 reference | null | null | exact preserved V1 source, quiescence proof, writer-fence proof, legacy lock, and V4 barrier |
| `GOVERNED_REVERSE_MIGRATION` | exact V4 state | exact current Challenge | exact rollback `AUTHORIZATION` | exact eligible preserved V1 state, reverse quiescence/fence, and rollback proof |

`transition_kind` is exactly one of:

~~~text
INITIALIZE_RELEASE_CONTROL
APPROVE_RELEASE
REJECT_RELEASE
CERTIFY_CUTOVER
ACTIVATE_CUTOVER
REVOKE_RELEASE_DECISION
ROLLBACK_PRODUCTION_CUTOVER
SUPERSEDE_RELEASE_DECISION
RETIRE_RELEASE_DECISION
V1_MIGRATION_HANDOVER
REAFFIRM_RELEASE
REJECT_REAFFIRMATION
CANCEL_MIGRATION
GOVERNED_REVERSE_MIGRATION
~~~

Each kind fixes the one or more exact predecessor/successor pairs already
defined by the closed Revision 2/3 state and action matrices, one authority
basis, reference presence, and `activation_consumed` result. No new lifecycle
state or transition pair is created here. Any unlisted kind or inherited
state pair is invalid.

The Transition identity payload is every Transition field except
`transition_identity` and `transition_digest`:

~~~text
h = SHA256(canonical_json(transition_identity_payload))
transition_identity = "constitutional-lifecycle-transition-v4-sha256:" + hex(h)
transition_digest   = "sha256:" + hex(h)
~~~

The Transition must never contain:

- successor state identity or state hash;
- next Challenge identity other than as a later state reference;
- Receipt identity or digest;
- acknowledgment identity;
- Replay identity or digest;
- CRO identity or digest; or
- a claim that state mutation has committed.

`PREPARED` means the exact transition inputs are immutable and admissible. It
does not mean applied. Exactly one valid current Authority State referencing
the Transition proves application; an exact post-read-back Receipt proves the
Human-visible committed result.

### Receipt V4 identity surface

Revision 4 retains every Revision 3 Receipt field and changes only versioned
references to V4. Its identity payload covers the finalized Human act where
applicable, consumed Challenge, applied Transition, predecessor state,
read-back successor state, idempotency identity, effective time, owner, and
topology. It excludes only `receipt_identity` and `receipt_digest`.

The Receipt has no authority until the public state validator confirms that
the current state references the same Transition and contains the same exact
identity/hash/revision. It cannot be precomputed as committed, and no source
artifact may depend on it.

### Compatibility Matrix

| Surface | Revision 4 compatibility rule | Result |
|---|---|---|
| active G69-19 V1 state | unchanged and valid under V1 until controlled handover | `PRESERVED` |
| native V1 schema | no `state_identity` field added or inferred into stored V1 bytes | `PRESERVED` |
| synthetic V1 identity | recomputable compatibility reference only after exact V1 validation | `ADDITIVE_PROPOSED` |
| V1 current-state path | same path; no parallel V4 head | `PRESERVED` |
| V1 readers after handover | reject V4 version; restart fence prevents writer return | `PRESERVED` |
| Revision 3 lifecycle behavior | all non-identity rules inherited unchanged | `PRESERVED` |
| Revision 3 identity formats | retained as proposal history only; no active runtime artifacts exist | `SUPERSEDED_IN_PROPOSAL` |
| Candidate/Decision/Event evidence | exact prior schemas and lineage retained | `PRESERVED` |
| Human Authority | same kinds, actor, target, scope, and payload bindings | `PRESERVED` |
| CLIA/HIC/CHE | same launcher, family, submission service, and CHE | `PRESERVED` |
| G69-19 terminal package | V4 successor references exact Decision/state/Replay/CRO graph | `VERSIONED_SUCCESSOR_PROPOSED` |
| Replay | reconstructs finalized V4 sources; recomputes but does not invent legacy identity | `PRESERVED` |
| CRO | observes finalized V4 Replay; no source authority | `PRESERVED` |
| rollback evidence | exact preserved V1 and V4 predecessor lineage retained | `PRESERVED` |
| production topology | 1 CLIA / 1 HIC / 1 CHE / 1 chain / 1 path / 0 parallel | `PRESERVED` |

## Deterministic Algorithms

### Unified V4 construction algorithm

1. Load and validate the exact predecessor and every applicable immutable
   source artifact.
2. For a legacy V1 predecessor, validate V1 first and derive the synthetic
   identity from the exact fixed payload. For V4, use the native identity and
   state hash. For initialization, require the exact root Candidate and ingress
   evidence with null state predecessor fields.
3. Bind the authority basis, current Challenge and Human act when required,
   idempotency identity, transition kind, intended successor status/phase/
   revision, environment, root, evidence, owner, and topology.
4. Construct the closed Transition identity payload; canonicalize; derive
   Transition identity and digest; validate; persist immutably; flush; and
   directory-sync.
5. Construct the next Challenge from the finalized Transition and predecessor
   basis. Canonicalize; derive identity/digest; validate; persist immutably;
   flush; and directory-sync.
6. Construct the successor state with exact predecessor, Transition, consumed
   act/Challenge, idempotency, and current Challenge references plus every
   inherited evidence field.
7. Require exact equality between state fields and the Transition's intended
   successor fields and Challenge subject fields.
8. Build the identity dependency graph and require a complete deterministic
   topological order with no self-edge or strongly connected component.
9. Derive and validate state identity/hash excluding only those two fields.
10. Under the inherited exclusive generation barrier, re-read and revalidate
    the predecessor and all transition inputs.
11. Atomically replace the one state file, sync its directory, and read back
    through the public V4 validator.
12. Only after successful read-back, derive and persist the Receipt; then
    permit CHE return and mechanical HIC acknowledgment.
13. Reconstruct owner-local Replay from finalized sources, then permit passive
    CRO observation.

### Identity graph validation algorithm

~~~text
nodes = predecessor sources + Transition + Challenge + state

edges:
  Transition -> predecessor / consumed Challenge / act / evidence
  next Challenge -> Transition / predecessor
  successor state -> Transition / next Challenge / predecessor / evidence

reject if:
  any target unresolved or not finalized
  any identity/digest/hash mismatch
  any self-edge
  any target is Receipt, Replay, CRO, or acknowledgment created later
  topological sort does not contain every node exactly once

after state commit:
  Receipt -> state / Transition / consumed Challenge / act
  Replay -> finalized source artifacts
  CRO -> finalized Replay
~~~

### Legacy V1 derivation algorithm

1. Read the exact legacy state from the selected root without mutation.
2. Require the closed G69-19 V1 field set and supported state version.
3. Recompute `state_hash` from every field except `state_hash`.
4. Revalidate the embedded terminal Certification, HIC family, surface
   dispositions, rollback provenance, and state status.
5. Build the four-field canonical synthetic identity payload.
6. Compute the namespaced SHA-256 identity.
7. Bind identity, source state hash, exact runtime root, and retained evidence
   reference in both migration proofs and the V4 Transition.
8. Recompute all values after locks/barrier are held and before replacement.
9. Preserve the exact V1 source evidence for Replay and eligible rollback.

No step writes a field into the V1 state or allows synthetic identity outside
the controlled compatibility boundary.

## Responsibility Boundaries

Revision 4 preserves Revision 3 owners and makes identity custody exact:

| Responsibility | Exact owner | Revision 4 boundary |
|---|---|---|
| make lifecycle control decision | authenticated Human Authority | exact act only; no identity or state mutation |
| transport/present control or product act | one CLIA HIC family | no interpretation, identity creation, or workflow |
| admit exact act/capability | sole CHE | validates ingress; no release semantics |
| derive Transition, next Challenge, and proposed state | release/cutover production-status owner | exact forward-only graph; no Human outcome |
| issue current Challenge | release/cutover production-status owner | exact allowed actions; gains presentation authority only through current state |
| derive legacy compatibility identity | release/cutover production-status owner at migration boundary | recomputation after V1 validation; no V1 mutation or authority expansion |
| produce V1 quiescence proof | production-status owner | binds synthetic identity, hash, root, and zero activity |
| produce V1 writer fence | deployment/release owner | binds same predecessor plus process/restart exclusion |
| hold generation leases/barrier | production-status coordination sub-responsibility | synchronization only |
| commit one current state | release/cutover production-status owner | sole authority commit point under exact barrier |
| create/reconstruct Receipt | release/cutover owner-local evidence custodian | only after exact committed state read-back |
| acknowledge Receipt | canonical HIC transport | mechanical presentation only |
| reconstruct lifecycle and legacy identity | owner-local Replay | read-only; exact authorized algorithm; no repair |
| observe reconstruction | passive CRO | observation only |
| certify terminal package | independent release/HIC Certification owners | no activation |
| assess this proposal | future G70-03 Impact Assessment owner | mandatory before Ratification |

Transition preparation does not activate production. Challenge creation does
not create Human authority. Synthetic legacy identity does not create a
second state. Receipt does not commit. Replay and CRO do not authorize.

### Reuse Impact Assessment

1. **Which certified Constitutional capabilities are reused?**

   Revision 4 reuses the certified Architecture; canonical L0/L1 mutation
   boundaries; canonical JSON and SHA-256; G76-06 Artifact Identity Model;
   Human Authority and `CanonicalHumanAuthorityActV1`; one canonical CLIA;
   `CLIA_PRODUCTION_HIC_FAMILY`; sole CHE; Request/Continuation/next-act
   binding; release/cutover owner; exact Candidate, Decision, Event,
   Certification, state, migration, rollback, and idempotency responsibilities;
   Revision 3 generation leases and exclusive barrier; G69-19 V1 validation
   and atomic state path; owner-local Replay; passive CRO; CDP; CAP;
   fail-closed validation; and G48 reporting.

2. **Which G76-06 identity rules are applied?**

   All fifteen generic rules are applied: separate identity/integrity/
   correlation; closed canonical payload; self-field-only exclusion;
   predecessor-first construction; paired identity and digest/hash; owner,
   role, type, and version binding; DAG enforcement; forward-only Transition,
   commit, Receipt, Replay, CRO ordering; constrained owner-issued identities;
   constrained reference-only hashing; exact synthetic compatibility identity;
   no Replay inference; passive CRO; fail-closed ambiguity; and exact
   domain-specific schema/owner application.

3. **Does any certified capability become unreachable?**

   No. Revision 4 changes no active capability. Under a future fully completed
   CAP and CDP successor, every Revision 3 lifecycle route remains reachable;
   authenticated V1 evidence gains an exact controlled migration predecessor
   identity; and state, Receipt, Replay, CRO, rollback, and audit become
   deterministically constructible without removing historical evidence.

4. **Does the proposal create a parallel production path?**

   No. It is proposal-only and introduces no runtime route. Its proposed model
   retains the same CLIA/HIC/CHE and the same single current-state path.

5. **Does it decrease or increase the number of production paths?**

   Neither. The count remains exactly one, with zero parallel paths.

# 3. Constitutional Self-Assessment

## Verified

- Revision 4 binds Revision 3, the G76-05 unresolved assessment, and the
  G76-06 identity model by exact identity and digest.
- G76-00 through G76-06 remain byte-unchanged.
- The proposal remains `PROPOSAL_ONLY_UNASSESSED` and performs no later CAP
  stage.
- Revision 4 modifies only the three unresolved identity-model surfaces named
  by G76-05.
- The Authority State/Challenge graph is acyclic: Transition precedes next
  Challenge, which precedes successor state.
- Challenge V4 contains no successor-state identity or hash.
- Transition V4 contains no successor-state, Receipt, Replay, CRO, or
  acknowledgment identity.
- The initial state has one exact predecessor-free root rule rather than an
  inferred or random identity.
- The legacy V1 synthetic identity has an exact namespace, four-field
  canonical payload, SHA-256 derivation, owner, validation prerequisite, and
  migration-only scope.
- Legacy V1 bytes, native schema, state hash, state path, and production
  authority are not modified by identity derivation.
- Runtime root remains transition scope and is not misclassified as content
  identity.
- Lifecycle Transition V4 has a closed field set, authority-basis presence
  matrix, closed inherited transition vocabulary, identity payload,
  self-exclusion rule, owner, persistence stage, and prohibited dependencies.
- The one state commit remains the authority transition; PREPARED Transition
  and Receipt cannot independently become current authority.
- Receipt, Replay, and CRO occur only after finalized source evidence.
- Every non-identity Revision 3 lifecycle, barrier, migration, crash, retry,
  acknowledgment, and owner rule remains unchanged.
- One CLIA, one HIC family, one CHE, one owner chain, one production path, and
  zero parallel production paths remain preserved.
- No runtime, production, Constitutional, workflow, Replay, CRO, deployment,
  or active-state mutation is performed.

## Not Verified

- Revision 4 has not received the mandatory new G70-03 Constitutional Impact
  Assessment.
- No Human Ratification, amendment Certification, Publication, or Activation
  exists for Revision 4.
- Revision 4 is not active Constitutional law and does not authorize CDP.
- No V4 Transition, Challenge, state, Receipt, Replay, CRO, Certification,
  validator, serializer, persistence, migration, rollback, profile, or
  deployment implementation exists.
- No legacy V1 state is read, assigned a synthetic identity, copied, migrated,
  rolled back, or otherwise mutated by this proposal.
- No Candidate, Decision, Event, Transition, Challenge, state, Receipt,
  acknowledgment, Replay, CRO observation, or terminal Certification artifact
  is created.
- No implementation, runtime, deployment, migration, or live CLIA test is
  executed because this generation is proposal-only.
- Implementation feasibility, filesystem primitives, process coordination,
  and live crash behavior remain for a future CDP generation only after the
  complete CAP lifecycle activates a successor.
- Existing known hook drift, partial conformance, distributed enforcement,
  dormant governance memory, deployment, and rollback limitations remain
  visible and unchanged.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| G48 structure | six exact top-level sections and required Code Evidence subsections | deterministic heading review | `PASS` |
| authenticated baseline | commit, tree, subject, parent, clean start, and exact G76-04/05/06 SHA-256 | exact Git and digest inspection | `PASS` |
| predecessor proposal binding | G76-04 identity, revision, and digest | lineage review | `PASS` |
| unresolved assessment binding | G76-05 identity, class, and digest | lineage review | `PASS` |
| identity model binding | G76-06 identity, verdict, and digest | lineage review | `PASS` |
| proposal-only stage | fixed status; assessment/Ratification/Certification/Activation absent | CAP stage review | `PASS` |
| identity-model application | all fifteen G76-06 rules mapped | rule-by-rule comparison | `PASS` |
| state/Challenge acyclicity | predecessor -> Transition -> next Challenge -> state | dependency graph and topological-order proof | `PASS` |
| initial-state derivation | exact Candidate/ingress root; null same-type predecessor | root rule review | `PASS` |
| Challenge V4 schema | closed fields, identity payload, namespace, digest, absence of successor ref | field and dependency review | `PASS` |
| Authority State V4 identity | exact inherited schema, explicit V4 refs, self-field exclusion | state model review | `PASS` |
| legacy V1 validation | existing G69-19 validator required before derivation | prerequisite review | `PASS` |
| synthetic V1 identity | exact namespace, four-field payload, SHA-256, migration-only scope | canonical derivation review | `PASS` |
| V1 non-mutation | recomputation only; source bytes/schema unchanged and preserved | compatibility review | `PASS` |
| runtime-root separation | root bound in proofs/Transition but excluded from content identity | identity-versus-scope review | `PASS` |
| Transition V4 schema | closed fields, authority-basis matrix, transition vocabulary, identity algorithm | specification completeness review | `PASS` |
| Transition commit semantics | PREPARED evidence; state is sole commit point | authority review | `PASS` |
| Receipt ordering | finalized state precedes Receipt; no reverse edge | dependency review | `PASS` |
| Replay/CRO ordering | finalized source -> owner-local Replay -> passive CRO | authority and graph review | `PASS` |
| Revision 3 preservation | only three G76-05 identity impacts superseded | before/after scope comparison | `PASS` |
| compatibility | V1/V4 state, evidence, path, reader, rollback, and profile matrix | compatibility review | `PASS` |
| topology | 1 CLIA / 1 HIC / 1 CHE / 1 chain / 1 path / 0 parallel | invariant review | `PASS` |
| public API mutation | proposal names future duties but changes no code | repository mutation review | `NOT_APPLICABLE` |
| runtime/production validation | prohibited for proposal-only generation | scope review | `NOT_APPLICABLE` |
| implementation tests | no implementation and none required | scope review | `NOT_APPLICABLE` |
| document consistency | G48, G69-19, G70, G76-04/05/06 | cross-document review | `PASS` |
| no runtime or Constitutional mutation | report-only repository inventory | Git status and scope review | `PASS` |
| whitespace integrity | complete new proposal report | `git diff --no-index --check /dev/null <report>` | `PASS` |

# 5. Repository Mutation Summary

Modified files:

- added
  `docs/governance/G76_07_CONSTITUTIONAL_AMENDMENT_PROPOSAL_REVISION_4_RELEASE_DECISION_ARTIFACT_V1.md`
  as the sole G76-07 artifact.

Runtime, operational, and active Constitutional artifacts created:

- None. No Impact Assessment, Ratification, Certification, Publication,
  Activation, Candidate, Challenge, Transition, Decision, Event, Receipt,
  acknowledgment, Replay, CRO observation, terminal Certification, migration,
  runtime root, state, suspension, rollback, or synthetic identity instance is
  created.

Unchanged subsystems:

- Constitution, CAP, CDP, Governance, Production Cutover, production status,
  release, deployment, CLIA, HIC, CHE, Conversation, Human Authority,
  Authorization, Workers, execution, results, Replay, CRO, runtime,
  configuration, schema, policy, baseline, and PCBV31;
- all tests and historical runtime evidence; and
- all G0 through G76-06 contracts, reports, proposals, assessments, statuses,
  verdicts, limitations, and evidence.

API compatibility:

- No API, schema, model, validator, serializer, command, profile, route, owner,
  caller, workflow, identity namespace, hash algorithm, persistence rule,
  production behavior, or active Constitutional contract changed. The V4
  models remain inactive proposal content.

Boundary preservation:

- Revision 4 changes no active Constitutional artifact.
- Revision 3 remains immutable proposal evidence and is not edited.
- CAP remains the sole Constitutional evolution mechanism and CDP remains the
  sole implementation mechanism.
- The proposed synthetic identity is migration evidence, not a second state or
  production route.
- HIC remains transport only, Replay remains read-only, and CRO remains
  passive.
- The one-CLIA, one-HIC-family, one-CHE, one-owner-chain,
  one-production-path topology remains unchanged, with zero parallel paths.

Unrelated pre-existing changes:

- None observed. The worktree was clean at proposal start.

# 6. Certification Verdict

CONSTITUTIONAL_CAP_PROPOSAL_REVISION_4_ESTABLISHED
