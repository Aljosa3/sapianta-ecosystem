# 1. Implementation Summary

Generation: G77-32

Report and proposal identity:
`G77_32_CONSTITUTIONAL_META_AUTHORITY_CONSTITUENT_REPAIR_MODEL_PROPOSAL_REVISION_3_V1`

Proposal revision: `3`

Proposal status: `META_CONSTITUTIONAL_DESIGN_PROPOSAL_ONLY`

Amendment kind: `META_CONSTITUTIONAL_REPAIR_DESIGN_ADDITION`

Constitutional baseline: authenticated G0 through committed G77-31. G77-30
is immutable Proposal Revision 2. G77-31 is its sole authoritative independent
Constitutional Impact Assessment and classifies Revision 2 as
`UNRESOLVED_CONSTITUTIONAL_IMPACT`. Every predecessor remains closed and
unchanged.

Authenticated repository identity:

- Commit: `c52fa15146930404413703cf943358259206c430`
- Tree: `fa26efba12c9ffe48f844b49ae91a2cbbe7035a7`
- Subject: `G77-31: assess constituent repair model revision 2`
- Immediate parent: `f74d3135f1abfe1d2401a3e1eb96e70ced7cb8a9`
- Revision-start worktree state: clean
- Authenticated G77-30 SHA-256:
  `3b2f48d3adbeac33f0085e4230c8999c1dba57557dc974312a59b526abe3a607`
- Authenticated G77-31 SHA-256:
  `a1713f46bbfcb5afaf19d1d5205c7093ecd97b6f4eb5d3c086036829e20ab6bb`

Revision predecessor binding:

| Field | Exact binding |
|---|---|
| previous proposal identity | `G77_30_CONSTITUTIONAL_META_AUTHORITY_CONSTITUENT_REPAIR_MODEL_PROPOSAL_REVISION_2_V1` |
| previous proposal revision | `2` |
| previous proposal digest | `sha256:3b2f48d3adbeac33f0085e4230c8999c1dba57557dc974312a59b526abe3a607` |
| previous proposal verdict | `G77_META_AUTHORITY_CONSTITUENT_REPAIR_MODEL_REVISION_2_ESTABLISHED` |
| authoritative assessment identity | `G77_31_CONSTITUTIONAL_IMPACT_ASSESSMENT_META_AUTHORITY_CONSTITUENT_REPAIR_MODEL_REVISION_2_V1` |
| authoritative assessment digest | `sha256:a1713f46bbfcb5afaf19d1d5205c7093ecd97b6f4eb5d3c086036829e20ab6bb` |
| authoritative assessment class | `UNRESOLVED_CONSTITUTIONAL_IMPACT` |
| authoritative assessment verdict | `G77_META_AUTHORITY_CONSTITUENT_REPAIR_MODEL_REVISION_2_IMPACT_REQUIRES_REWORK` |

Reporting date: 2026-08-09.

Objective:

Create only the immutable Revision 3 successor of G77-30 and resolve exactly
the five G77-31 blockers. Retain every accepted Revision 2 architecture and
boundary not directly contradicted by those findings. Do not implement,
instantiate evidence, create a Human Act, Ratify, Certify, publish, activate,
establish initial adoption, materialize O01, perform CDP, or modify production.

Revision result:

~~~text
sealed ACTIVE registry + complete baseline authority-edge projection
-> no unregistered Constitutional effect

EMPTY slot -> reserved serialization time -> one RESERVED winner
-> immutable proof -> one ISSUED winner

one ConstitutionalRootEvolutionSnapshotCurrentPointer
-> every baseline/reachability/meta-state mutation
-> one current Constitutional view

activation Transition -> prepared successor root -> CAS intent
-> root pointer CAS -> marker -> read-back -> AtomicCommit -> Receipt

failed requirement -> finite canonical value domain -> unique minimum
changed-unit count N -> exactly 2^N - 1 proper subsets
-> value-minimal and set-minimal repair
~~~

Revision 3 preserves:

- Human as the sole constituent decision source;
- separation of Human decision, owner identity, and effect authority;
- ordinary CAP as the sole normal Constitutional amendment lifecycle;
- meta-repair as exceptional, repair-only, and unavailable while ordinary CAP
  is reachable or an exact target ordinary chain exists;
- one canonical HIC family, one CHE, one production owner chain, one
  production path, and zero parallel production paths;
- read-only Replay and passive CRO; and
- initial adoption as a separate unresolved external boundary.

This artifact establishes proposal structure only. Every closure below is a
proposal claim subject to a later independent assessment. It supplies no
authority to operate or adopt the model.

Added artifact:

- `docs/governance/G77_32_CONSTITUTIONAL_META_AUTHORITY_CONSTITUENT_REPAIR_MODEL_PROPOSAL_REVISION_3_V1.md`
  — this proposal-only G48 artifact.

Intentionally unchanged:

- G77-30, G77-31, and every G0 through G77-29 artifact;
- active Constitution and every current Constitutional pointer;
- Human Authority, HIC, CHE, Governance, Certification, Replay, CRO, CAP,
  CDP, release, runtime, deployment, and production behavior; and
- all code, tests, schemas, configuration, credentials, persistence, machine
  evidence, Human Acts, and production state.

## G77-31 Finding Resolution Matrix

| G77-31 blocker | Revision 3 proposed closure | Proposal claim |
|---|---|---|
| `G77_31_B01_AUTHORITY_REGISTRY_SEALED_WORLD_RULE_ABSENT` | ACTIVE membership is necessary for effect authority; a complete baseline-edge projection and predecessor-only CoverageProof close every reachable effect edge | `ADDRESSED` |
| `G77_31_B02_PROOF_ISSUANCE_LINEARIZATION_TIME_UNDERCLOSED` | EMPTY -> RESERVED winner CAS fixes the immutable observation token; deterministic proof then RESERVED -> ISSUED CAS fixes commit time without post-hash mutation | `ADDRESSED` |
| `G77_31_B03_COORDINATION_AND_ROOT_SNAPSHOT_SERIALIZATION_DIVERGENCE` | the root snapshot pointer is the sole pointer-of-record; every relevant mutation advances it in one domain; subordinate pointers are non-authoritative derived indexes | `ADDRESSED` |
| `G77_31_B04_ACTIVATION_TRANSITION_AND_MARKER_CAS_IDENTITY_UNDERCLOSED` | activation binds old/new baselines; the pointer CAS installs the successor root and precedes the marker in one exact forward DAG | `ADDRESSED` |
| `G77_31_B05_VALUE_MINIMALITY_AND_SUBSET_ROOT_DERIVATION_UNDERCLOSED` | requirement-derived finite value domains and exhaustive canonical proper-subset enumeration close value and set minimality | `ADDRESSED` |

No unrelated Revision 2 capability is redesigned. In any conflict between a
retained Revision 2 sentence and an exact Revision 3 replacement below, this
Revision 3 proposal rule controls only for the proposed successor.

## B01 — Sealed Constitutional Authority Universe

### Necessary ACTIVE membership rule

Revision 3 adds this proposed Constitutional sealed-world rule:

~~~text
effect contract not present as exactly one ACTIVE member
of the exact current Constitutional normative registry
-> zero Constitutional state-changing authority
~~~

The rule applies to every contract that can originate, admit, constrain,
certify, publish, activate, mutate, select, or install Constitutional state or
an artifact necessary for such a transition. Owner name, repository presence,
historical use, Human expression, proposal text, runtime implementation, and
an unregistered edge cannot substitute for ACTIVE membership.

An effect target that is absent, inactive, duplicated, excluded as
non-normative, or reachable only through an invalid edge has no effect
authority. If the active baseline nevertheless references it as
state-changing, the baseline authority universe is invalid and all descendant
manifest, census, liveness, eligibility, and repair artifacts fail closed.

### Complete baseline authority-edge projection

Revision 3 adds
`ConstitutionalActiveBaselineAuthorityEdgeProjectionV1`. Its universe is every
direct and transitive state-changing reference reachable from the exact active
baseline under the closed
`CONSTITUTIONAL_AUTHORITY_REFERENCE_SCHEMA_V1`.

The schema enumerates every canonical field path whose value can reference a
Constitutional state-changing effect. Unknown fields are not silently ignored:
an unknown field in an authority-bearing artifact invalidates the projection.
Traversal begins with the active baseline and follows exact identity/digest
pairs only. Evidence-only references are recorded as non-effect edges but may
not terminate an effect edge.

Each ordered `ConstitutionalActiveBaselineAuthorityEdgeV1` contains:

~~~text
edge_ordinal
source_artifact_type
source_artifact_version
source_artifact_identity
source_artifact_digest
source_canonical_field_path
edge_kind
target_artifact_type
target_artifact_version
target_artifact_identity
target_artifact_digest
target_effect_contract_identity
target_effect_contract_digest
target_registry_entry_ordinal
target_registry_entry_identity
target_registry_entry_digest
target_registry_membership_proof
target_registry_status = ACTIVE
traversal_depth
predecessor_edge_ordinal
metadata = {}
~~~

`edge_kind` is exactly one of:

- `STATE_CHANGING_EFFECT_REFERENCE`;
- `AUTHORITY_PREREQUISITE_REFERENCE`;
- `AUTHORITY_DELEGATION_REFERENCE`;
- `AUTHORITY_CONSTRAINT_REFERENCE`; or
- `NON_EFFECT_EVIDENCE_REFERENCE`.

Ordering is lexicographic by source artifact tuple, canonical field path,
edge kind, and target artifact tuple. Traversal depth and predecessor ordinal
must reproduce the canonical breadth-first traversal; they do not select the
universe.

Every state-changing, prerequisite, delegation, or constraint edge must
resolve to exactly one ACTIVE registry entry and exactly one manifest-
qualifying effect contract. Missing pairs, half-present pairs, duplicate
source/path/target edges, unknown field paths, unknown edge kinds, dangling
targets, inactive targets, duplicate registry resolutions, and unregistered
targets fail closed.

Self-edges and back-edges among authority-bearing references are forbidden.
The traversal maintains a canonical visited-node set; encountering a target
already on the active traversal stack emits a deterministic cycle path and
invalidates the projection. A previously completed node may be referenced
again only when the repeated edge is separately enumerated and resolves to
the same registry entry. Thus traversal terminates over the finite registry
and cycles cannot be hidden by a visited-set shortcut.

The projection payload is:

~~~text
artifact_type
artifact_version
authority_edge_projection_identity
authority_edge_projection_digest
active_baseline_identity
active_baseline_digest
active_baseline_pointer_identity
active_baseline_pointer_digest
canonical_reference_schema_identity
canonical_reference_schema_digest
normative_registry_identity
normative_registry_digest
normative_registry_root
normative_registry_entry_count
projected_node_count
ordered_projected_nodes_root
projected_edge_count
ordered_projected_edges_root
ordered_projected_edges_digest
resolved_active_registry_ordinal_bitmap_digest
coverage_proof_identity
coverage_proof_digest
projection_result = COMPLETE_SEALED_AUTHORITY_PROJECTION
derived_at
producing_owner = CONSTITUTIONAL_GOVERNANCE_OWNER
metadata = {}
~~~

### Projection CoverageProof and identities

`ConstitutionalActiveBaselineAuthorityEdgeProjectionCoverageProofV1` is
finalized before the projection. It binds only already finalized inputs:

~~~text
artifact_type
artifact_version
projection_coverage_proof_identity
projection_coverage_proof_digest
active_baseline_identity
active_baseline_digest
canonical_reference_schema_identity
canonical_reference_schema_digest
normative_registry_identity
normative_registry_digest
normative_registry_root
normative_registry_entry_count
projected_node_count
ordered_projected_nodes_root
projected_edge_count
ordered_projected_edges_root
ordered_projected_edges_digest
root_reference_field_count
root_reference_field_bitmap_digest
resolved_effect_edge_count
resolved_effect_edge_bitmap_digest
resolved_active_registry_ordinal_bitmap_digest
missing_edge_count = 0
duplicate_edge_count = 0
unknown_edge_count = 0
dangling_edge_count = 0
cyclic_edge_count = 0
unregistered_effect_edge_count = 0
inactive_effect_edge_count = 0
ambiguous_registry_resolution_count = 0
coverage_result = COMPLETE
derived_at
producing_owner = CONSTITUTIONAL_GOVERNANCE_OWNER
metadata = {}
~~~

The root reference bitmap must contain every authority-reference field defined
by the closed schema for the active baseline. The effect-edge bitmap must
contain every authority-bearing edge ordinal exactly once. Recomputing the
canonical traversal from the baseline must yield the exact node/edge roots,
counts, bitmaps, and registry resolutions.

The CoverageProof identity hashes its complete canonical payload excluding
only its own identity/digest and metadata. It does not bind the later
projection identity. The projection identity is:

~~~text
authority_edge_projection_identity =
  constitutional-authority-edge-projection-sha256:SHA256(canonical({
    contract_version,
    active_baseline_identity, active_baseline_digest,
    active_baseline_pointer_identity, active_baseline_pointer_digest,
    canonical_reference_schema_identity,
    canonical_reference_schema_digest,
    normative_registry_identity, normative_registry_digest,
    normative_registry_root, normative_registry_entry_count,
    projected_node_count, ordered_projected_nodes_root,
    projected_edge_count, ordered_projected_edges_root,
    ordered_projected_edges_digest,
    resolved_active_registry_ordinal_bitmap_digest,
    coverage_proof_identity, coverage_proof_digest,
    projection_result, derived_at
  }))
~~~

This order is acyclic:

~~~text
baseline + reference schema + registry + ordered nodes/edges
-> ProjectionCoverageProof
-> AuthorityEdgeProjection
-> manifest CoverageProof
-> AuthorityManifest
-> censuses
~~~

Revision 3 completely replaces the Revision 2 manifest input closure by
adding the projection and projection-CoverageProof pairs to the manifest
CoverageProof and manifest payloads. Manifest qualifying ordinals must equal:

~~~text
ACTIVE registry effect ordinals
== projected authority-bearing target registry ordinals
== manifest authority-effect ordinals
~~~

An ACTIVE normative non-effect entry may remain in its explicit non-normative
partition; no authority-bearing projected target may. Registry membership is
necessary but does not create authority by itself: the active baseline must
also reach the registered contract through the valid projection.

### B01 adversarial reduction

~~~text
unregistered active-baseline effect
-> projection unregistered_effect_edge_count > 0
-> no COMPLETE CoverageProof
-> no manifest/census/liveness proof

missing/duplicate/unknown/dangling/cyclic edge
-> exact nonzero failure counter or root mismatch
-> fail closed

complete projection + exact ACTIVE registry resolution
-> finite sealed authority universe eligible for census derivation
~~~

The retained route census and proof-singleton subject semantics are unchanged
except that every descendant directly binds the new projection and CoverageProof
pairs.

## B02 — Proof Issuance Serialization and Immutable Time

Revision 3 replaces the two-state proof issuance slot with a forward-only
three-state protocol: `EMPTY`, `RESERVED`, and `ISSUED`. The stable slot
identity derivation from Revision 2 is unchanged.

### Serialization time-token contract

The shared domain is
`CONSTITUTIONAL_EVOLUTION_PROOF_ISSUANCE_SERIALIZATION_DOMAIN_V1`. It issues
monotonic, single-use `ConstitutionalSerializationTimeTokenV1` values. A token
contains the domain identity, slot identity, serialization generation,
predecessor domain generation, canonical UTC instant, and token digest. The
instant is fixed before dependent content is hashed. A CAS can consume only
the exact next unconsumed token for that slot and generation.

The CAS linearization instant is defined to equal its consumed token instant.
An unconsumed token has no authority, does not change the slot, and cannot be
reassigned. Recovery reads durable intent/token bytes and never samples a
clock.

### Reservation winner

`ConstitutionalEvolutionLivenessProofReservationIntentV1` binds the exact
EMPTY pointer/state, all proof input roots, the next serialization generation,
one observation time-token pair, and
`reserved_observation_at = observation_time_token.instant`.

The deterministic order is:

~~~text
EMPTY pointer/State + exact proof inputs
-> ReservationIntent + observation time token
-> RESERVED slot State
-> ReservationCAS
-> ReservationReceipt
~~~

The RESERVED state directly binds the intent, EMPTY predecessor, exact proof
inputs, token, generation, and `proof_observed_at`; proof and committed-proof
fields are null. It never binds its later CAS.

`ConstitutionalEvolutionLivenessProofReservationCASV1` binds the intent,
EMPTY pointer/state, RESERVED state, observation token, generation, and exact
installed RESERVED state pair. In one atomic action it consumes the token,
persists the CAS, and updates the slot pointer. Its `committed_at` and the
RESERVED `proof_observed_at` both equal the token instant.

Exactly one EMPTY-to-RESERVED CAS wins. Losing candidates do not persist a
RESERVED state, do not produce a proof, and do not establish another time.
They resolve the winner through the pointer.

### Deterministic proof and issuance commit

After reservation read-back, the liveness proof is deterministically derived
from the complete Revision 3 input closure plus:

~~~text
proof_issuance_slot_identity
reservation_intent_identity
reservation_intent_digest
reservation_cas_identity
reservation_cas_digest
reservation_receipt_identity
reservation_receipt_digest
observation_time_token_identity
observation_time_token_digest
proof_observed_at
~~~

`proof_observed_at` equals the reservation token instant. No proof field
depends on the later ISSUED CAS or issuance Receipt.

The issuance winner order is:

~~~text
ReservationReceipt + immutable proof
-> ProofIssuanceCommitIntent + commit time token
-> ISSUED slot State
-> ProofIssuanceCAS
-> ProofIssuanceReceipt
~~~

`ConstitutionalEvolutionLivenessProofIssuanceCommitIntentV1` binds the exact
RESERVED current pointer/state, reservation chain, proof pair, next generation,
one commit time-token pair, `proof_observed_at`, and
`committed_at = commit_time_token.instant`.

The ISSUED state directly binds the commit intent, RESERVED predecessor,
reservation chain, proof pair, both time-token pairs, `proof_observed_at`, and
`committed_at`. It does not bind its later CAS.

`ConstitutionalEvolutionLivenessProofIssuanceCASV2` binds the commit intent,
RESERVED pointer/state, immutable proof, ISSUED state, commit token, exact
installed ISSUED state pair, and both times. In one atomic action it consumes
the exact commit token, persists the CAS, and advances the slot pointer.

Presence is exact:

| Slot state | Proof pair | Observation chain | Commit chain | Authority result |
|---|---|---|---|---|
| `EMPTY` | null | null | null | no proof |
| `RESERVED` | null | exact | null | winner fixed; proof not yet authoritative |
| `ISSUED` | exact | exact | exact | exact proof authoritative |

Any custodian retry after RESERVED reconstructs the same proof from immutable
inputs and reservation time. Any retry after ISSUED returns the exact proof.
Same slot/generation with different content fails closed. Crash before the
reservation CAS leaves EMPTY. Crash after reservation CAS resumes from
RESERVED. Crash before issuance CAS leaves RESERVED. Crash after issuance CAS
reconstructs the same Receipt. No boundary invents time or modifies hashed
bytes.

### B02 adversarial reduction

~~~text
two candidate times
-> one EMPTY-to-RESERVED CAS winner
-> one durable observation token/time

winning ReservationReceipt + exact immutable inputs
-> one deterministic proof identity

different proof or commit time under winning reservation
-> content conflict

recovery
-> read winning tokens and bytes
-> no wall-clock resampling
~~~

## B03 — One Authoritative Root Snapshot Pointer

Revision 3 abolishes split current-state authority. The sole authoritative
pointer-of-record is:

`ConstitutionalRootEvolutionSnapshotCurrentPointerV1`

The sole serialization domain is:

`CONSTITUTIONAL_ROOT_EVOLUTION_SNAPSHOT_DOMAIN_V1`

Every authoritative reader resolves one committed root snapshot containing:

1. exact active baseline identity/digest and logical baseline pointer value;
2. exact global MetaRepairState identity/digest;
3. exact OrdinaryCAPReachabilityState identity/digest, including exact-target
   ordinary-chain status and reachability epoch;
4. exact current normative registry root and authority projection/manifest
   roots needed by those states; and
5. exact source/evidence registry epochs that determine reachability.

### Sole-pointer rule

Every authoritative mutation of any listed value must atomically advance the
same root pointer from one exact predecessor snapshot root to one exact
successor snapshot root. This includes:

- baseline or baseline logical-pointer replacement;
- normative registry, projection, or manifest root replacement;
- G70 entry/predecessor/evidence-root movement relevant to reachability;
- CAP entry `REACHABLE`/`UNREACHABLE` movement;
- exact-target `COMPLETE_CHAIN_EXISTS`/`NO_COMPLETE_CHAIN` movement;
- reachability epoch movement;
- every MetaRepairState transition, including OPEN, ADMIT, MARK_STALE, RESET,
  and post-activation DORMANT; and
- constituent-repair activation.

The retained `OrdinaryCAPReachabilityCurrentPointerV1`,
`MetaRepairCurrentPointerV1`, and logical active-baseline pointer are renamed
in authority semantics to derived snapshot indexes. They may cache the exact
pair already committed in the current root, but:

~~~text
subordinate index/cache value
-> zero independent Constitutional current-state authority
~~~

An index cannot establish an epoch, authorize a transition, satisfy freshness,
or defeat root comparison. Index mismatch causes cache rejection and root
resolution; it never changes the root. Cache repair is non-authoritative and
cannot be evidence of a Constitutional mutation.

### General root evolution mutation

Revision 3 adds `ConstitutionalRootEvolutionStateMutationV1` as the common
immutable mutation intent for non-activation changes:

~~~text
artifact_type
artifact_version
root_evolution_mutation_identity
root_evolution_mutation_digest
mutation_kind
transaction_domain_identity
predecessor_snapshot_pointer_identity
predecessor_snapshot_pointer_digest
predecessor_snapshot_root
predecessor_baseline_pair
predecessor_meta_repair_state_pair
predecessor_cap_reachability_state_pair
predecessor_registry_and_source_roots
changed_component_bitmap
successor_baseline_pair
successor_meta_repair_state_pair
successor_cap_reachability_state_pair
successor_registry_and_source_roots
successor_snapshot_root
authorizing_artifact_identity
authorizing_artifact_digest
serialization_intent_identity
serialization_intent_digest
mutation_idempotency_identity
prepared_at
producing_owner = CONSTITUTIONAL_GOVERNANCE_OWNER
metadata = {}
~~~

The changed-component bitmap is derived by byte comparison of all logical
pairs. Every unchanged pair must repeat exactly. Every changed pair must be
authorized by the exact mutation kind and authorizing predecessor. Unknown,
unlisted, or half-present changes fail closed.

The common serialization order is:

~~~text
current root + finalized state Transition/source mutation
-> prepared successor logical rows
-> RootEvolutionStateMutation
-> RootSnapshotPointerCASIntent
-> RootSnapshotPointerCAS
-> RootEvolutionCommitMarker
-> complete root read-back
-> mutation Receipt
~~~

In the common CAS payload, `root_evolution_transaction` means the exact
`ConstitutionalRootEvolutionStateMutationV1` pair for a non-activation change
and the exact `ConstitutionalRootRepairAtomicTransactionV2` pair for repair
activation. The two artifact types are mutually exclusive and the mutation
kind fixes which one is permitted.

The exact pointer-CAS construction is defined under B04 and applies equally to
non-activation and activation mutations. A non-root MetaRepairState Transition
still precedes its successor State, but no separate StateCAS updates an
authoritative MetaRepair pointer. Its successor is exposed only by the root
snapshot CAS.

### Freshness, races, crash, and recovery

Every proof, assessment, Human decision admission, Certification, state
transition, and activation reads the root pointer once at its linearization
predicate and directly binds the root pointer pair/root plus the contained
reachability/MetaRepair/baseline pairs. Any relevant mutation changes the root,
so an older predicate cannot commit.

~~~text
repair validates root R
+ ordinary CAP/reachability/meta mutation commits root R+1
-> repair CAS expects R
-> CAS loses
-> stale advancement impossible
~~~

Concurrent mutations of disjoint logical components still contend on the same
root. Exactly one wins; the loser re-resolves and recomputes. There is no merge
of stale prepared rows. Crash before CAS leaves the predecessor root; crash
after CAS makes the complete successor root authoritative. Recovery reads the
persisted CAS and root; it cannot expose one component separately.

CAP reachability and exact-target status remain distinct fields, but share one
state and root. Eligibility remains exactly:

~~~text
cap_entry_reachability = UNREACHABLE
AND exact_target_chain_status = NO_COMPLETE_CHAIN
AND exact bound root is still current
~~~

If ordinary CAP becomes reachable or an exact target chain becomes complete,
the same root mutation invalidates the repair read set. Therefore healthy CAP
and meta-repair cannot both remain advancement-eligible.

## B04 — Activation Bindings and Forward-Only Root CAS

### Complete activation Transition replacement

Revision 3 completely replaces the `ACTIVATE_AND_DORMANT` row of
`ConstitutionalMetaRepairStateTransitionV1`. Its complete activation-specific
payload adds distinct baseline pairs:

~~~text
predecessor_baseline_identity
predecessor_baseline_digest
successor_baseline_identity
successor_baseline_digest
~~~

For `ACTIVATE_AND_DORMANT`:

- predecessor baseline equals the exact baseline bound by the current
  CERTIFIED MetaRepairState and current predecessor root;
- successor baseline equals the exact candidate certified by the Human
  constituent decision and constituent Certification;
- the pairs must differ;
- reserved successor status is `DORMANT`;
- predecessor CERTIFIED State, successor DORMANT State, Diff, NecessityProof,
  decision, Certification, and transaction all repeat both pairs exactly; and
- the retained single `active_baseline` pair is canonical null for this row.

For every non-activation Transition, the two new baseline pairs are canonical
null and the retained current active-baseline pair remains exact. Unknown or
half-present baseline fields fail closed.

The activation Transition binds no successor State, transaction, CAS, marker,
AtomicCommit, or Receipt. The successor DORMANT State binds the finalized
Transition and both baselines, but no later artifact.

### Root pointer CAS intent and installed value

Revision 3 completely replaces the Revision 2 rule that the pointer CAS points
to a marker. The one authoritative root pointer CAS installs exactly:

~~~text
successor_snapshot_root
~~~

It does not install a CommitMarker identity. The marker is a later immutable
record of the completed CAS.

`ConstitutionalRootRepairAtomicTransactionV2` retains the complete Revision 2
predecessor read set, successor write set, authority chain, prepared rows,
serialization generation, idempotency, and successor-root validation. It adds
the exact activation Transition pair and distinct predecessor/successor
baseline pairs. It contains no CAS, marker, read-back, AtomicCommit, or Receipt
identity. Its identity hashes the complete finalized read/write closure and
prepared successor root, so it is fixed before the CAS intent.

`ConstitutionalRootSnapshotPointerCASIntentV1` contains:

~~~text
artifact_type
artifact_version
root_snapshot_cas_intent_identity
root_snapshot_cas_intent_digest
transaction_domain_identity
root_evolution_transaction_identity
root_evolution_transaction_digest
predecessor_snapshot_pointer_identity
predecessor_snapshot_pointer_digest
predecessor_snapshot_root
successor_snapshot_root
serialization_identity
serialization_generation
commit_time_token_identity
commit_time_token_digest
committed_at
installed_value_kind = SUCCESSOR_SNAPSHOT_ROOT
cas_intent_idempotency_identity
prepared_at
producing_owner = CONSTITUTIONAL_GOVERNANCE_OWNER
metadata = {}
~~~

The intent is finalized after every successor row and the successor root are
fully prepared. Its commit time-token is allocated once by the root domain;
`committed_at` equals the token instant. The token is consumed only by the
exact CAS intent and is never resampled.

`ConstitutionalRootSnapshotPointerCASV1` contains:

~~~text
artifact_type
artifact_version
root_snapshot_cas_identity
root_snapshot_cas_digest
root_snapshot_cas_intent_identity
root_snapshot_cas_intent_digest
transaction_domain_identity
root_evolution_transaction_identity
root_evolution_transaction_digest
predecessor_snapshot_pointer_identity
predecessor_snapshot_pointer_digest
predecessor_snapshot_root
installed_successor_snapshot_root
serialization_identity
serialization_generation
commit_time_token_identity
commit_time_token_digest
committed_at
cas_result = COMMITTED
producing_owner = CONSTITUTIONAL_GOVERNANCE_OWNER
metadata = {}
~~~

The CAS identity hashes this complete canonical payload except its own pair
and metadata. It binds the intent and installed root, but no later marker. In
one atomic action the domain consumes the time token, persists the CAS, and
changes the root pointer from the exact predecessor root to the exact
successor root. Pointer read-back must equal that root.

### Durable marker, read-back, AtomicCommit, and Receipt

`ConstitutionalRootEvolutionCommitMarkerV2` is a strict successor of the CAS:

~~~text
artifact_type
artifact_version
commit_marker_identity
commit_marker_digest
root_snapshot_cas_identity
root_snapshot_cas_digest
root_snapshot_cas_intent_identity
root_snapshot_cas_intent_digest
root_evolution_transaction_identity
root_evolution_transaction_digest
predecessor_snapshot_root
successor_snapshot_root
serialization_identity
serialization_generation
commit_time_token_identity
commit_time_token_digest
committed_at
commit_status = COMMITTED
producing_owner = CONSTITUTIONAL_GOVERNANCE_OWNER
metadata = {}
~~~

The marker identity hashes the complete payload excluding its own pair and
metadata. The CAS never binds the marker. Marker reconstruction from the CAS,
intent, transaction, token, and roots is unique.

`ConstitutionalRootSnapshotReadBackV1` follows the marker and binds the marker,
CAS, current root pointer, installed root, every logical successor pair, and
their exact digests. Result is `COMPLETE_SUCCESSOR_ROOT_CURRENT`; partial or
mixed read-back has no artifact identity and fails closed.

Revision 3 replaces AtomicCommit V2 and ActivationReceipt predecessor closure
only by adding the exact CAS-intent, CAS, V2 marker, and read-back pairs. Their
retained field equalities, authority chain, reason, false runtime flag, and
idempotency remain unchanged. `AtomicCommit.committed_at`,
`Receipt.activated_at`, marker time, CAS time, intent time, and token instant
are all equal.

### Complete forward-only identity DAG

~~~text
current predecessor root + CERTIFIED State + exact authority chain
-> ACTIVATE_AND_DORMANT Transition intent
-> successor baseline/reachability/DORMANT rows
-> prepared successor snapshot root
-> RootRepairAtomicTransactionV2
-> RootSnapshotPointerCASIntent + commit time token
-> RootSnapshotPointerCAS installs successor root
-> RootEvolutionCommitMarkerV2
-> RootSnapshotReadBack
-> ConstitutionalConstituentRepairAtomicCommitV2
-> ConstitutionalConstituentRepairActivationReceiptV1
~~~

No node binds a later successor. In particular:

- Transition does not bind successor State;
- successor State does not bind CAS;
- CAS intent does not bind CAS;
- CAS does not bind marker;
- marker does not bind read-back, AtomicCommit, or Receipt;
- AtomicCommit does not bind Receipt; and
- no predecessor identity includes a later time or identity.

### Crash and deterministic recovery

| Boundary | Exact result |
|---|---|
| before Transition | predecessor root remains current |
| after Transition/before complete preparation | predecessor root remains current; incomplete rows have no authority |
| after rows/before successor root | predecessor root remains current |
| after successor root/transaction before CAS intent | deterministic intent/token allocation may begin; no state change |
| after CAS intent/before CAS | predecessor root remains current; retry reuses exact intent/token |
| during CAS | predecessor or complete successor root is current; never partial |
| after CAS/before marker | successor root is authoritative; marker reconstructs from durable CAS inputs |
| after marker/before read-back | successor root remains authoritative; full read-back restarts |
| after partial read-back | no read-back artifact; full read-back restarts |
| after read-back/before AtomicCommit | identical AtomicCommit reconstructs |
| after AtomicCommit/before Receipt | identical Receipt reconstructs |
| after Receipt | identical retry returns it |

Recovery never changes prepared bytes, chooses a different root, resamples
time, infers Human intent, creates authority, or repairs an invalid root.
Missing successor content makes the root invalid and fails closed.

## B05 — Closed Normative Value and Set Minimality

Revision 3 retains the complete Canonical Normative Diff and replaces the
underderived minimal-value and strict-subset contracts.

### Category-specific canonical value domains

Every eligible failed G70-01 entry requirement must directly bind a finalized
`CanonicalRepairRequirementValueDomainV1`. A producer cannot provide or widen
the domain. It is a deterministic projection of the failed requirement under
`CONSTITUTIONAL_REPAIR_VALUE_DOMAIN_SCHEMA_V1`.

The domain payload is:

~~~text
artifact_type
artifact_version
value_domain_identity
value_domain_digest
failed_cap_transition_requirement_identity
failed_cap_transition_requirement_digest
normative_category
canonical_value_schema_identity
canonical_value_schema_digest
admissible_atom_count
ordered_admissible_atoms_root
required_atom_count
ordered_required_atoms_root
forbidden_atom_count
ordered_forbidden_atoms_root
narrowing_relation_kind
sufficiency_evaluator_identity
sufficiency_evaluator_digest
domain_result = FINITE_CLOSED_UNIQUE_MINIMUM_ELIGIBLE
derived_at
producing_owner = CONSTITUTIONAL_GOVERNANCE_OWNER
metadata = {}
~~~

The seven exact category domains are:

| Normative category | Canonical atoms | Narrowing relation |
|---|---|---|
| `MISSING_PREDECESSOR_IDENTITY_BINDING` | exact required predecessor type/version/identity/digest/field path | set containment over requirement-bound predecessor atoms |
| `MISSING_CALLER_RESPONSIBILITY_BINDING` | exact caller, responsibility, owner-effect-contract, and scope tuple | tuple-set containment; no wildcard or extra caller |
| `MISSING_DETERMINISTIC_DERIVATION_RULE` | exact function identity/version, ordered inputs, canonicalization, output rule | equality of the requirement-selected rule tuple |
| `MISSING_ENTRY_VALIDATION_RULE` | exact predicate code/version, subject, expected relation, fail action | predicate-set containment over required checks |
| `MISSING_ENTRY_STATE_TRANSITION_BINDING` | exact predecessor/status/successor/effect tuple | transition-tuple containment |
| `MISSING_ENTRY_IDEMPOTENCY_OR_CAS_BINDING` | exact idempotency inputs, pointer/predecessor predicate, CAS result, conflict rule | constraint-set containment |
| `MISSING_ENTRY_REPLAY_VALIDATION_BINDING` | exact read-only input and validation predicate tuple | predicate-set containment; mutation atoms forbidden |

Every atom is already named by the failed requirement or derived by its closed
schema. An atom not so derived is forbidden, not merely larger. Domain counts
and roots are recomputed from the requirement. Infinite/wildcard domains,
unknown atoms, multiple incomparable sufficient minima, or no sufficient value
make the requirement ineligible for meta-repair.

`ConstitutionalRepairMinimalRequiredValueV1` contains:

~~~text
artifact_type
artifact_version
minimal_required_value_identity
minimal_required_value_digest
failed_cap_transition_requirement_identity
failed_cap_transition_requirement_digest
value_domain_identity
value_domain_digest
normative_category
ordered_minimal_atoms_count
ordered_minimal_atoms_root
canonical_minimal_value_bytes_digest
sufficiency_evaluator_identity
sufficiency_evaluator_digest
minimum_result = UNIQUE_MINIMUM_SUFFICIENT_VALUE
derived_at
producing_owner = CONSTITUTIONAL_GOVERNANCE_OWNER
metadata = {}
~~~

The minimum is the unique least sufficient element under the category
relation. The validator evaluates every strictly narrower admissible value in
canonical domain order: all must fail the exact requirement. The minimum
identity is:

~~~text
minimal_required_value_identity =
  repair-minimal-value-sha256:SHA256(canonical({
    contract_version,
    failed_cap_transition_requirement_identity,
    failed_cap_transition_requirement_digest,
    value_domain_identity, value_domain_digest,
    normative_category,
    ordered_minimal_atoms_count, ordered_minimal_atoms_root,
    canonical_minimal_value_bytes_digest,
    sufficiency_evaluator_identity, sufficiency_evaluator_digest,
    minimum_result, derived_at
  }))
~~~

Each changed unit directly binds this value pair and its domain pair.
`new_value_digest` must equal its canonical minimum bytes digest. Extra caller,
owner, authority, policy, scope, alternate route, wildcard, optional bypass,
or unrelated atom makes equality fail.

### Exhaustive proper-subset universe

Let `N = changed_unit_count`. Revision 3 permits meta-repair only when:

~~~text
1 <= N <= 20
~~~

The bound makes exhaustive validation computationally finite. A repair needing
more than 20 changed units is not silently approximated; it is ineligible for
meta-repair and remains for a later Constitutional process.

Changed-unit ordinals are exactly `0` through `N - 1`. A subset is encoded as
an exact N-bit bitmap where bit `i = 1` means changed unit ordinal `i` is
applied. The full-set bitmap is excluded. The empty bitmap is included.

The required proper-subset count is exactly:

~~~text
expected_proper_subset_count = 2^N - 1
~~~

Subsets are ordered first by set-bit cardinality, then lexicographically by
their ascending included-ordinal tuple. This order is independent of producer
insertion order.

Each `ConstitutionalRepairProperSubsetEvaluationV1` contains:

~~~text
subset_ordinal
normative_diff_identity
normative_diff_digest
changed_unit_count
subset_bitmap
subset_bitmap_digest
included_unit_count
ordered_included_unit_ordinals
ordered_included_units_root
predecessor_baseline_identity
predecessor_baseline_digest
evaluated_candidate_bytes_digest
failed_cap_transition_requirement_identity
failed_cap_transition_requirement_digest
reachability_evaluator_identity
reachability_evaluator_digest
cap_entry_reachability = UNREACHABLE
exact_requirement_satisfied = false
evaluation_result = PROPER_SUBSET_INSUFFICIENT
metadata = {}
~~~

Its identity is the SHA-256 of the complete canonical payload excluding only
its own identity/digest and metadata. The candidate bytes are derived by
applying exactly the bitmap-selected changed units to the exact predecessor
bytes. It cannot be supplied independently.

### Proper-subset CoverageProof

`ConstitutionalRepairProperSubsetCoverageProofV1` is finalized after every
subset evaluation and before the NecessityProof:

~~~text
artifact_type
artifact_version
proper_subset_coverage_proof_identity
proper_subset_coverage_proof_digest
normative_diff_identity
normative_diff_digest
changed_unit_count
bitmap_width = N
full_set_bitmap_digest
expected_proper_subset_count
actual_proper_subset_count
canonical_subset_order = CARDINALITY_THEN_LEXICOGRAPHIC_ORDINALS
ordered_subset_evaluation_identities_root
ordered_subset_evaluation_digests_root
ordered_subset_bitmaps_root
bitmap_membership_coverage_digest
duplicate_bitmap_count = 0
missing_bitmap_count = 0
full_set_bitmap_count = 0
invalid_bitmap_count = 0
insufficient_result_count
coverage_result = COMPLETE_ALL_PROPER_SUBSETS_INSUFFICIENT
derived_at
producing_owner = CONSTITUTIONAL_GOVERNANCE_OWNER
metadata = {}
~~~

Required equalities are:

~~~text
actual_proper_subset_count
== expected_proper_subset_count
== insufficient_result_count
== 2^N - 1

set(ordered subset bitmaps)
== every N-bit value except the all-ones full set
~~~

The membership coverage digest is computed over the canonical full bitmap
domain with exactly the full-set bit absent and all other bits present.
Duplicate, omitted, malformed, reordered, or full-set entries fail closed.
The CoverageProof identity hashes its complete payload excluding its own pair
and metadata. It does not bind the later NecessityProof.

### Complete NecessityProof replacement

Revision 3 completely replaces
`ConstitutionalRepairNormativeNecessityProofV1` input closure. It directly
binds:

- exact Diff pair and all changed-unit/minimal-value/domain roots;
- exact failed requirement and evaluator pair;
- full-set candidate bytes and `REACHABLE` result;
- `N`, the exact expected subset count, and canonical subset order;
- ordered subset evaluation identity/digest/bitmap roots; and
- the exact ProperSubsetCoverageProof pair.

Its reduction is:

~~~text
all changed units with exact unique-minimum values
-> exact failed requirement satisfied
-> CAP entry REACHABLE

every one of exactly 2^N - 1 proper subsets
-> exact failed requirement not satisfied
-> CAP entry UNREACHABLE

any broader value, extra atom, omitted subset, duplicate subset,
unknown changed unit, or unrelated policy
-> proof invalid
~~~

The identity order is acyclic:

~~~text
failed requirement -> ValueDomain -> MinimalRequiredValue
-> ChangedUnit -> NormativeDiff
-> ProperSubsetEvaluations -> ProperSubsetCoverageProof
-> NecessityProof
-> assessment -> Human decision -> Certification
~~~

Diff never binds NecessityProof. No subset proof authorizes its Diff or failed
requirement. A value-minimal unit can still be set-redundant; exhaustive subset
evaluation rejects it. A set-minimal Diff can still contain a broad value;
unique-minimum equality rejects it. Both dimensions are mandatory.

## Complete Revision 3 Identity DAG

The complete proposed major dependency order is:

~~~text
active baseline + reference schema + normative registry
-> ordered authority nodes/edges
-> AuthorityEdgeProjectionCoverageProof
-> AuthorityEdgeProjection
-> AuthorityManifestCoverageProof
-> AuthorityManifest
-> route censuses -> CensusCoverageProof
-> reachability State candidate

failed requirement -> ValueDomain -> MinimalRequiredValue
-> ChangedUnits -> NormativeDiff
-> ProperSubsetEvaluations -> ProperSubsetCoverageProof
-> NecessityProof

EMPTY proof slot
-> ReservationIntent/time token -> RESERVED State -> ReservationCAS
-> ReservationReceipt -> immutable liveness proof
-> IssuanceCommitIntent/time token -> ISSUED State -> IssuanceCAS
-> IssuanceReceipt

current root + exact proof/diff/assessment/decision/Certification chain
-> MetaRepair Transition -> successor State rows
-> RootEvolution mutation/transaction -> RootSnapshotPointerCASIntent
-> RootSnapshotPointerCAS -> CommitMarker -> RootReadBack
-> AtomicCommit -> ActivationReceipt
~~~

Explicit cycle exclusions:

- no identity hashes itself;
- no CoverageProof binds its later projection, manifest, or NecessityProof;
- no proof binds an issuance CAS or Receipt that follows it;
- no State binds its later CAS;
- no CAS binds its later marker;
- no Diff binds its later NecessityProof;
- no Transition binds its successor State;
- no predecessor binds a later Receipt;
- no Human decision binds an artifact whose authority depends on that Human
  decision; and
- no candidate successor, marker, Receipt, or Replay output authorizes a
  predecessor.

Every time used in hashed content comes from an earlier finalized domain token.
Recovery reuses tokens and never creates a hidden time cycle.

## Ordinary CAP, Meta-Repair, and Second-CAP Exclusion

Ordinary CAP remains the sole normal Constitutional amendment lifecycle.
Meta-repair remains exceptional and admissible only when all of these are
current in one exact root snapshot:

~~~text
sealed authority projection COMPLETE
AND CAP entry UNREACHABLE for a Constitutional predecessor defect
AND exact target ordinary chain status = NO_COMPLETE_CHAIN
AND no alternative self/constituent/founding route
AND global MetaRepairState = DORMANT
AND exact value-minimal/set-minimal repair exists
~~~

Any healthy ordinary CAP entry makes meta-repair ineligible. Any exact target
ordinary chain makes it ineligible. Any current repair prevents another. Any
unrelated policy atom, category, changed unit, or redundant unit invalidates
the Diff/NecessityProof.

Successful root activation atomically installs:

- the exact successor baseline;
- `MetaRepairState = DORMANT` with no advancement-current repair; and
- `cap_entry_reachability = REACHABLE` for the repaired entry.

Therefore the exceptional mechanism does not remain available after repair;
ordinary CAP again remains the sole normal evolution path. Revision 3 creates
no standing second CAP and no alternate production path.

## Human Authority and Owner/Effect Boundary

Human remains the sole proposed constituent decision source. The distinct
Human constituent decision directly binds the current root, proof, assessment,
Diff, NecessityProof, exact predecessor/successor, and repair-only effect. It
cannot establish itself, mutate state, certify, activate, implement, or adopt
the meta-authority model.

Human expression alone has zero Constitutional effect. Governance may derive
and custody proposal evidence and execute only a separately established exact
effect contract. Certification may verify an exact chain but cannot choose the
repair or mutate the root. The independent assessor is an evidence gate only.
CHE and HIC transport only. Replay is deterministic and read-only. CRO is
passive. Repository control, historical founding, owner identity, inaccessible
CAP, candidate successor, and the proposed contract create no constituent
authority.

No owner identity is widened. Effect authority remains contract-specific,
registered, baseline-reachable, state-bound, and fail-closed.

## Initial Adoption Boundary

Revision 3 does not solve, propose, infer, or instantiate the authority by
which this operational model could first become Constitutional law. The model
cannot authorize its own adoption, and no proposed artifact may be used as a
founding source.

The exact boundary remains:

~~~text
META_AUTHORITY_OPERATIONAL_DESIGN_REVISED_BUT_INITIAL_ADOPTION_AUTHORITY_UNRESOLVED
~~~

This remains true even if a later independent assessment confirms all five
operational closure claims. Operational impact confirmation would not create
activation eligibility or initial-adoption authority.

## Reuse Impact Assessment

1. **Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?**

   Ponovno se uporabijo ena Human Authority, ena HIC družina, edini CHE,
   običajni G70 CAP, G76 identitetna pravila, obstoječe owner/effect ločitve,
   deterministični CAS kot mehanski gradnik, read-only Replay, pasivni CRO,
   ena production owner veriga in ena produkcijska pot. Obstoječi CAS ne
   predstavlja že certificirane root-snapshot ali meta-authority semantike.

2. **Katere nove zmogljivosti (če sploh) nastanejo?**

   Samo kot neaktivni predlog nastanejo sealed-world authority-edge projection,
   rezervirana proof-issuance časovna serializacija, enotna root-snapshot
   pointer semantika, aciklični root CAS/marker model ter zaprta value/set
   minimality dokazila. Nobena ni implementirana ali neodvisno potrjena.

3. **Ali katera obstoječa zmogljivost postane nedosegljiva?**

   Ne. Predlog je neaktiven. Obstoječe CAP, Governance, Human, Replay, CRO,
   runtime in produkcijske zmogljivosti ostanejo nespremenjene in dosegljive.

4. **Ali implementacija/predlog ustvarja vzporedni tok?**

   Ne. Predlog ne ustvarja produkcijskega toka. Meta-repair ostaja izključni
   repair-only Constitutional mehanizem, ki je nedosegljiv ob dosegljivem
   običajnem CAP in po popravilu vrne stanje v DORMANT.

5. **Ali zmanjšuje ali povečuje število produkcijskih poti?**

   Ne zmanjšuje in ne povečuje. Število ostane ena produkcijska pot in nič
   vzporednih produkcijskih poti.

Explicit topology counts:

| Metric | Count |
|---|---:|
| `production_paths_before` | 1 |
| `production_paths_after` | 1 |
| `parallel_production_paths_before` | 0 |
| `parallel_production_paths_after` | 0 |

## Production Topology Assessment

| Invariant | Count/status |
|---|---:|
| Human Authorities | 1 |
| canonical HIC families | 1 |
| Canonical Human Entries | 1 |
| production owner chains | 1 |
| production paths | 1 |
| parallel production paths | 0 |
| new production ingress | none |
| new runtime caller | none |
| HIC semantic authority | none |
| CHE constituent decision authority | none |
| Replay write authority | none |
| CRO control authority | none |

## Proposal-Level Adversarial Closure Review

| Attack | Revision 3 rejection point | Proposal result |
|---|---|---|
| unregistered baseline effect | sealed rule plus projection counter/root mismatch | `REJECTED_BY_DESIGN` |
| omitted/duplicate/dangling/cyclic edge | exact traversal, counts, bitmaps, zero counters | `REJECTED_BY_DESIGN` |
| two proof times/winners | one EMPTY-to-RESERVED token-consuming CAS | `REJECTED_BY_DESIGN` |
| crash resamples proof time | durable reservation/commit tokens | `REJECTED_BY_DESIGN` |
| CAP becomes reachable during repair | every mutation advances same root; stale CAS loses | `REJECTED_BY_DESIGN` |
| two live/CERTIFIED repairs | one MetaRepairState inside sole root pointer | `REJECTED_BY_DESIGN` |
| split baseline/meta/reachability view | one successor snapshot root installed atomically | `REJECTED_BY_DESIGN` |
| marker/CAS cycle | CAS installs root and precedes marker | `REJECTED_BY_DESIGN` |
| old/new baseline ambiguity | activation directly binds distinct pairs | `REJECTED_BY_DESIGN` |
| broad caller/owner/policy value | requirement-derived unique minimum equality | `REJECTED_BY_DESIGN` |
| producer omits a successful subset | exact `2^N - 1` bitmap CoverageProof | `REJECTED_BY_DESIGN` |
| unrelated policy unit | complete Diff plus value and set minimality | `REJECTED_BY_DESIGN` |
| proposal claims adoption | explicit unresolved boundary | `REJECTED_BY_DESIGN` |

These are proposal self-tests, not independent confirmation. A later assessor
must reconstruct and attempt to falsify every closure.

## Exact Next Boundary

The next permissible Constitutional step is an independent impact assessment
of Revision 3. It must authenticate G77-31/G77-32, adversarially reconstruct
B01-B05 and the complete identity DAG, and keep initial adoption separate.

No implementation, Human Act, Ratification, Certification, publication,
activation, initial adoption, O01, CDP, deployment, or production action is
authorized.

# 2. Code Evidence

## Public API

No runtime API is added or modified. All artifact names, payloads, roots,
tokens, pointers, CAS operations, state machines, and validators are proposed
Constitutional contracts only, not implemented models or schemas.

## Orchestration Entry Point

The sole Human production interaction remains:

~~~text
Human -> permitted HIC profile -> sole CHE -> exact eligible owner
-> sole CHE Response/Continuation -> same HIC
~~~

No proposal evidence creates another ingress, runtime caller, semantic route,
or Human decision source.

## Semantic Reductions

### Sealed authority

~~~text
ACTIVE registry membership
+ complete baseline-edge projection
-> finite Constitutional effect universe

not ACTIVE or not projected
-> zero state-changing authority
~~~

### Proof issuance

~~~text
one EMPTY slot + one consumed observation token
-> one RESERVED winner/time
-> immutable proof
-> one ISSUED authoritative proof
~~~

### Sole current state

~~~text
any relevant mutation
-> one successor root
-> one root pointer CAS
-> no split current view
~~~

### Root activation

~~~text
old/new baseline-bound Transition
-> prepared root -> CAS intent -> CAS installs root
-> marker -> read-back -> AtomicCommit -> Receipt
~~~

### Minimality

~~~text
requirement-derived finite value domain
-> unique minimum per changed unit

N changed units
-> exactly 2^N - 1 proper subset failures
-> set-minimal repair
~~~

### Initial adoption

~~~text
proposal structure
-> no founding authority
-> no Constitutional effect
~~~

## Public Validators

No validator is implemented. A future separately authorized implementation
must reject:

- any state-changing effect without exact ACTIVE registry membership and
  complete projection coverage;
- missing, duplicate, unknown, dangling, cyclic, inactive, ambiguous, or
  unregistered authority edges;
- a CoverageProof that binds its later successor or has nonzero failure count;
- proof time not equal to its exact consumed serialization token;
- post-hash proof mutation or recovery clock resampling;
- any subordinate index used as current-state authority;
- a relevant mutation that does not advance the one root snapshot pointer;
- stale root, split-view, mixed-root, or merged-stale-row advancement;
- activation without distinct exact predecessor/successor baselines;
- CAS/marker mutual identity dependence;
- a root CAS installing anything except the exact prepared successor root;
- partial successor root or partial read-back;
- a value domain not derived from the failed requirement;
- a non-unique or broader purported minimum;
- changed-unit count outside `1..20`;
- subset count other than `2^N - 1`;
- duplicate, missing, malformed, reordered, or full-set subset entries;
- any proper subset satisfying the exact failed requirement;
- unrelated caller, owner, policy, authority, scope, runtime, Replay-write, or
  CRO-control widening; and
- any artifact used to infer initial-adoption authority.

## Canonical Data Models

| Proposed model | Exact responsibility | Negative boundary |
|---|---|---|
| AuthorityEdgeProjection/CoverageProof | close baseline-reachable registered effect universe | no authority creation |
| AuthorityManifest/censuses | retained exact classification and route absence | no repository-search semantics |
| proof slot reservation/issuance | one immutable proof/time winner | no wall-clock recovery choice |
| root snapshot pointer | sole current Constitutional view | subordinate pointers have no authority |
| RootEvolutionStateMutation | prepare exact non-activation successor root | no independent state visibility |
| activation Transition | bind old/new baselines and exact authority | no successor authorization |
| root CAS intent/CAS | install exact successor snapshot root | no marker dependency |
| marker/read-back | durable evidence after CAS | no state mutation |
| AtomicCommit/Receipt | reconstruct committed result | no repair or reinterpretation |
| ValueDomain/MinimalValue | derive unique requirement minimum | no producer-selected atoms |
| subset evaluations/CoverageProof | enumerate every proper subset | no producer-selected universe |
| NecessityProof | combine full success and all subset failures | no Diff authorization |
| Replay | deterministic read-only reconstruction | no clock, CAS, repair, or inference |
| CRO | passive observation | no control or Certification |

## Deterministic Algorithms

1. Resolve the sole current root snapshot and all contained exact pairs.
2. Traverse every authority-reference field from the active baseline under the
   closed schema and resolve every effect edge to one ACTIVE registry entry.
3. Derive projection coverage, manifest, censuses, and census coverage in
   forward-only order.
4. Derive reachability and exact-target chain status inside one root snapshot.
5. Reserve one proof observation token through EMPTY-to-RESERVED CAS.
6. Derive the immutable proof, reserve its commit token, and install ISSUED.
7. Derive finite category value domains and unique minimum values from the
   exact failed requirement.
8. Compute the complete canonical Diff and reject every unknown change.
9. Enumerate all `2^N - 1` proper-subset bitmaps in cardinality/lexicographic
   order and evaluate the exact requirement.
10. Derive subset coverage then NecessityProof without a backward edge.
11. Admit assessment, exact Human decision, and Certification only against the
    current root and retained one-winner state sequence.
12. Prepare the successor logical rows, root, transaction, and CAS intent.
13. CAS the sole pointer from predecessor root to successor root.
14. Derive marker, complete read-back, AtomicCommit, and Receipt in order.
15. Replay the immutable chain without mutation, live clock, or inference.

## Responsibility Boundaries

| Responsibility | Exact owner/source | Negative boundary |
|---|---|---|
| constituent decision | Human | sole decision source; expression alone has no effect |
| authenticate/transport Human decision | Human Authority/HIC/CHE | no constituent choice or root mutation |
| evidence/state custody | Constitutional Governance owner | no Human choice, Certification, or founding authority |
| independent assessment | segregated assessor | no state, decision, Certification, or activation |
| constituent Certification | exact Certification owner | no Human choice or pointer mutation |
| root serialization | snapshot transaction domain | no candidate choice or authority creation |
| exact effect execution | registered contract-bound owner | no authority beyond exact effect |
| reconstruction | Replay custodian | read-only; no clock, repair, CAS, or inference |
| observation | CRO | passive; no control or Certification |
| initial adoption | unresolved external boundary | not provided by this proposal |
| implementation | later separately authorized CDP | not authorized here |

## Repository Evidence

The authenticated G77-30/G77-31 bytes, exact five G77-31 findings, G48
reporting discipline, G69 Human/CHE/HIC boundaries, complete G70 CAP, G76
identity rules, and unchanged focused tests are the evidence basis. No runtime
behavior, machine evidence instance, provider state, or proposal assertion is
treated as independent impact confirmation.

# 3. Constitutional Self-Assessment

## Verified as Proposal Structure

- G77-30 and G77-31 are bound by exact identities and SHA-256 digests.
- Exactly the five G77-31 blockers receive explicit proposed closures.
- ACTIVE registry membership is necessary and unregistered effects are void.
- Every baseline-reachable authority edge is in a finite deterministic
  projection with a predecessor-only CoverageProof.
- Proof observation and commit times derive from earlier immutable tokens.
- Exactly one proof reservation and one authoritative proof can win.
- One root snapshot pointer is the sole current-state authority.
- Every relevant mutation advances that same root in one domain.
- Activation binds distinct predecessor/successor baselines.
- Root CAS installs the successor root and precedes the marker.
- Every changed-unit value equals a requirement-derived unique minimum.
- Every one of exactly `2^N - 1` proper subsets is enumerated and fails.
- Identity edges are forward-only under the proposed construction.
- Human remains the sole constituent decision source.
- Ordinary CAP remains the sole normal amendment lifecycle.
- Meta-repair returns to DORMANT and cannot carry unrelated policy.
- Initial adoption remains expressly separate and unresolved.
- Production topology remains one path and zero parallel paths.
- No runtime, evidence instance, Human Act, Ratification, Certification,
  publication, activation, O01, CDP, or production action occurs.

## Not Verified

- No independent impact assessment of Revision 3 has occurred.
- No proposed registry projection, token domain, slot state, root pointer,
  transaction, CAS, value domain, subset proof, or Receipt exists.
- No implementation validates concurrency, crash, recovery, finite-domain,
  subset enumeration, performance, persistence, or security semantics.
- No Human decision, Certification, publication, or activation exists.
- No initial-adoption authority exists or is inferred.
- Proposal self-tests cannot establish Constitutional effectiveness or
  implementation authority.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| G48 structure | six exact top-level sections and Code Evidence subsections | heading review | `PASS` |
| authenticated lineage | commit/tree/parent and G77-30/G77-31 hashes | Git/hash review | `PASS` |
| predecessor immutability | no G0 through G77-31 mutation | repository review | `PASS` |
| exact finding scope | five-row G77-31 matrix | scope review | `PASS` |
| sealed-world authority | non-ACTIVE/non-projected effect has zero authority | rule review | `PASS_PROPOSED` |
| baseline edge projection | exact finite traversal and registry resolution | graph review | `PASS_PROPOSED` |
| missing/duplicate/unknown/dangling edges | zero counters and recomputed roots | adversarial review | `PASS_PROPOSED` |
| cyclic authority edges | active-stack cycle path invalidates projection | DAG review | `PASS_PROPOSED` |
| projection CoverageProof | predecessor inputs only; no projection self-cycle | identity review | `PASS_PROPOSED` |
| manifest/census equality | projection/registry/manifest ordinal equality | coverage review | `PASS_PROPOSED` |
| proof singleton | EMPTY-to-RESERVED one-winner CAS | concurrency review | `PASS_PROPOSED` |
| proof observation time | consumed reservation token instant | time review | `PASS_PROPOSED` |
| proof immutability | proof precedes issuance commit intent/CAS | identity review | `PASS_PROPOSED` |
| proof crash/retry | durable tokens; no resampling | recovery review | `PASS_PROPOSED` |
| sole pointer-of-record | root snapshot pointer only | authority review | `PASS_PROPOSED` |
| subordinate pointers | derived cache/index; no authority | boundary review | `PASS_PROPOSED` |
| every relevant mutation | same root domain/pointer CAS | mutation review | `PASS_PROPOSED` |
| stale/split race | predecessor-root CAS comparison | concurrency review | `PASS_PROPOSED` |
| two live repairs | one MetaRepairState in one root | state review | `PASS_PROPOSED` |
| CAP/meta exclusivity | current root has exact predicate | lifecycle review | `PASS_PROPOSED` |
| activation baselines | distinct predecessor/successor pairs | schema review | `PASS_PROPOSED` |
| CAS installed value | exact successor snapshot root | pointer review | `PASS_PROPOSED` |
| marker/CAS direction | CAS precedes marker and never binds it | identity review | `PASS_PROPOSED` |
| root crash boundaries | exact predecessor/successor result table | crash review | `PASS_PROPOSED` |
| AtomicCommit/Receipt recovery | durable CAS/marker/read-back inputs | recovery review | `PASS_PROPOSED` |
| finite value domains | requirement/schema-derived atoms | domain review | `PASS_PROPOSED` |
| unique value minimum | all narrower values insufficient | minimality review | `PASS_PROPOSED` |
| unrelated widening | atom/domain and exact-value equality rejection | adversarial review | `PASS_PROPOSED` |
| changed-unit bound | `1 <= N <= 20` | finiteness review | `PASS_PROPOSED` |
| exact subset encoding | N-bit bitmap | encoding review | `PASS_PROPOSED` |
| exact subset count | `2^N - 1` | arithmetic review | `PASS_PROPOSED` |
| subset order/coverage | cardinality/lexicographic roots and bitmap coverage | coverage review | `PASS_PROPOSED` |
| duplicate/omission attack | zero counters and full domain equality | adversarial review | `PASS_PROPOSED` |
| full/proper results | full REACHABLE; every proper subset UNREACHABLE | evaluator review | `PASS_PROPOSED` |
| complete identity DAG | explicit forward-only graph and cycle exclusions | G76 review | `PASS_PROPOSED` |
| Human boundary | sole decision source; no expression-only effect | authority review | `PASS` |
| second-CAP exclusion | reachability predicate plus exact minimality | semantic review | `PASS_PROPOSED` |
| post-repair lifecycle | DORMANT + REACHABLE in successor root | lifecycle review | `PASS_PROPOSED` |
| initial adoption | exact unresolved boundary retained | boundary review | `PASS_FAIL_CLOSED` |
| production topology | before 1/0; after 1/0 | topology review | `PASS` |
| focused G69/G70 regression | unchanged contracts | pytest: 140 passed | `PASS` |
| Markdown/whitespace | 88 balanced fences; no trailing whitespace | static validation | `PASS` |
| independent impact confirmation | later assessment required | governance review | `NOT_REACHED` |

# 5. Repository Mutation Summary

Modified files:

- added
  `docs/governance/G77_32_CONSTITUTIONAL_META_AUTHORITY_CONSTITUENT_REPAIR_MODEL_PROPOSAL_REVISION_3_V1.md`
  as the sole G77-32 artifact.

No existing file changed. G77-30, G77-31, and every G0 through G77-29 artifact
remain byte-identical.

No authority manifest, projection, census, proof, time token, slot state,
reachability state, MetaRepairState, Transition, root snapshot, CAS, marker,
Diff, value domain, subset proof, Human decision, Human Act, Certification,
AtomicCommit, Receipt, publication, activation, initial-adoption event, O01,
CDP artifact, runtime artifact, or production artifact was created.

Unchanged subsystems:

- active Constitution and every current pointer;
- Human Authority, HIC, CHE, Governance, CAP, Certification, Replay, CRO,
  Production, release, Conversation, Platform, Authorization, Workers,
  routing, workflow, deployment, configuration, schemas, credentials,
  providers, persistence, tests, and runtime; and
- all G0 through G77-31 artifacts.

Validation performed:

- authenticated repository commit/tree/parent and G77-30/G77-31 hashes;
- verified exactly six G48 top-level sections and all Code Evidence
  subsections;
- verified 88 balanced Markdown fences and no trailing whitespace;
- ran 140 focused unchanged G69-07 and G70-01 through G70-06 tests; all
  passed;
- recomputed predecessor hashes after work; and
- verified the worktree contains only this new G77-32 artifact.

Boundary preservation:

- this is Proposal Revision 3 only;
- no independent impact confirmation is claimed;
- ordinary CAP remains the sole active normal amendment lifecycle;
- initial adoption remains external and unresolved;
- Replay remains read-only and CRO passive;
- production topology remains one path with zero parallel paths; and
- no implementation or Constitutional effect is authorized.

Unrelated pre-existing changes:

- None observed. The worktree was clean at proposal start.

# 6. Certification Verdict

G77_META_AUTHORITY_CONSTITUENT_REPAIR_MODEL_REVISION_3_ESTABLISHED
