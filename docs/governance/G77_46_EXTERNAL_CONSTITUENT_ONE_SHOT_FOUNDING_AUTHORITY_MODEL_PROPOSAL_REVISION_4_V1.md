# 1. Implementation Summary

Generation: G77-46

Report and proposal identity:
`G77_46_EXTERNAL_CONSTITUENT_ONE_SHOT_FOUNDING_AUTHORITY_MODEL_PROPOSAL_REVISION_4_V1`

Proposal revision: `4`

Proposal status: `PROPOSAL_ONLY_UNASSESSED`

Candidate: `H`

Amendment kind: `FOUNDING_MODEL_MINIMAL_REPAIR_PROPOSAL_REVISION_ONLY`

Constitutional baseline: authenticated G0 through committed G77-45. G77-36
is the immutable operational MetaRepair proposal, G77-37 independently
confirms it, G77-38 freezes it, G77-39 requires an external founding model,
G77-44 is immutable Candidate H Revision 3, and G77-45 is its sole
authoritative independent assessment. G77-45 classifies Revision 3 as
`UNRESOLVED_CONSTITUTIONAL_IMPACT`, retains G77-43 B03 as resolved at
proposal/design level, and establishes exactly three internal blockers.

Authenticated repository identity:

- Commit: `de71f443bee1b023a6f65a9101c07f51cae2981e`
- Tree: `bac9c0166d32835913c9e9577c1a114b5a9e6f3c`
- Subject: `G77-45: assess Candidate H founding model revision 3`
- Immediate parent: `522f061299d991b972e03c66fb584e29f1b5c10d`
- Revision-start worktree state: clean
- Authenticated G77-36 SHA-256:
  `5533ec8e597e0767f869daec8118ee3dec6c77af56b4d7c71bdc2d44cfdaba4a`
- Authenticated G77-37 SHA-256:
  `4ecd74ca986e56490bd72bd26d28ef01777be5780fe8596fcae992fbc6d59add`
- Authenticated G77-38 SHA-256:
  `b80ca33767deab09c3875f302ccee212a539291a12f454ef67e1bbca07133363`
- Authenticated G77-39 SHA-256:
  `71aafd80edfc4711adb037f00e265465ae525e9267ddafb3855890353f760592`
- Authenticated G77-40 SHA-256:
  `e36cb2584f46e3cf18cf4f83558df459b8036b552fa8b42a9338aaa1022e6154`
- Authenticated G77-41 SHA-256:
  `cbf180857ebd494f169d38b2d2465daf454ffc6e8399c54326e5df60cd275a25`
- Authenticated G77-42 SHA-256:
  `b379cb057282aaf7d10c6e6e3f8a55053a630b19a0a0ad80e8159a0222b316a6`
- Authenticated G77-43 SHA-256:
  `7f3687353a81b96a551b4ea6e0ae2c023dfa2b58a543b996eda3f944dc052a27`
- Authenticated G77-44 SHA-256:
  `03026b9ff5df38e05ffe08e0d834d0ac83d1b04efc3681f6ea2aff4165801c0a`
- Authenticated G77-45 SHA-256:
  `d3b07e92d0f7b96aea515d979118dcc65c65c4488563122272905d6219e21f38`

Revision predecessor binding:

| Field | Exact binding |
|---|---|
| previous proposal | `G77_44_EXTERNAL_CONSTITUENT_ONE_SHOT_FOUNDING_AUTHORITY_MODEL_PROPOSAL_REVISION_3_V1` |
| previous proposal digest | `sha256:03026b9ff5df38e05ffe08e0d834d0ac83d1b04efc3681f6ea2aff4165801c0a` |
| authoritative assessment | `G77_45_CONSTITUTIONAL_IMPACT_ASSESSMENT_EXTERNAL_CONSTITUENT_ONE_SHOT_FOUNDING_AUTHORITY_MODEL_REVISION_3_V1` |
| assessment digest | `sha256:d3b07e92d0f7b96aea515d979118dcc65c65c4488563122272905d6219e21f38` |
| assessment classification | `UNRESOLVED_CONSTITUTIONAL_IMPACT` |
| assessment verdict | `G77_CANDIDATE_H_FOUNDING_MODEL_REVISION_3_IMPACT_REQUIRES_REWORK` |
| exact repair scope | G77-45 B01 through B03 only |
| retained external-race result | G77-43 B03 `RESOLVED_AT_PROPOSAL_LEVEL` |
| G77-38 operational design | `IMMUTABLY_FROZEN` |

Reporting date: 2026-08-09.

Objective:

Create only Candidate H Revision 4 and minimally repair the three G77-45
internal blockers. Replace Revision 3's invented component-array/manifest and
Candidate-H-specific root CAS with the actual frozen direct root tuple and its
existing serialization lifecycle. Derive one successor Constitutional State
before the consuming root. Retain the externally owned dual-version
BEGIN_CONSUMPTION model unchanged. Do not implement, adopt, Ratify, Certify,
publish, activate, execute O01 or CDP, deploy, or mutate production.

Revision 4 reduction:

~~~text
actual frozen direct root tuple
-> allocation root changes coordinator only to ALLOCATED
-> consuming root changes exact business rows + coordinator CONSUMED
-> every other direct frozen row repeats byte-identically

current root + finalized Candidate H inputs
-> OperationSeed -> deterministic token -> AllocationIntent
-> ALLOCATED coordinator/root -> allocation CAS/read-back
-> ConsumeIntent -> successor Constitutional State
-> CONSUMED coordinator -> successor root -> terminal CAS/read-back/result
-> next_token_ordinal advances exactly once

same finalized lawful inputs
-> one successor Constitutional State -> one successor root
-> one read-back -> one terminal disposition -> one successful Receipt
~~~

This proposal remains:

~~~text
PROPOSAL_ONLY_UNASSESSED
~~~

Every repair below is a proposal claim. Only a later independent G70-03
Constitutional Impact Assessment may confirm it. No actual external premise,
Universe, Census, source, Instrument, Human Decision/Finality, status domain,
disposition, root, token, CAS, or Receipt is created. Founding eligibility
remains false.

Added artifact:

- `docs/governance/G77_46_EXTERNAL_CONSTITUENT_ONE_SHOT_FOUNDING_AUTHORITY_MODEL_PROPOSAL_REVISION_4_V1.md`
  — this proposal-only G48 artifact.

Intentionally unchanged:

- G77-36 through G77-45 and every predecessor artifact;
- the G77-38 frozen coordinator, SlotMap, root, pointer, token, logical-time,
  Replay, CRO, and topology contracts;
- the G77-44/G77-45 external status-vector and BEGIN linearization result;
- active Constitution, ordinary G70 CAP, Human Authority, HIC, CHE,
  Governance, Certification, runtime, release, deployment, persistence, and
  production; and
- all code, schemas, tests, configuration, credentials, external evidence,
  Human Acts, Instruments, states, roots, CAS records, Receipts, and runtime
  data.

## Exact G77-45 Blocker-Resolution Matrix

| G77-45 blocker | Revision 4 proposed closure | Proposal claim |
|---|---|---|
| `G77_45_B01_PREDECESSOR_ROOT_REPRESENTATION_AND_INHERITANCE_INCOMPATIBLE` | discard the generic predecessor array, discriminator, nested manifest, and Candidate H root family; reuse `ConstitutionalRootEvolutionSnapshotV2` and repeat every unchanged direct frozen row exactly | `ADDRESSED` |
| `G77_45_B02_FROZEN_ROOT_SERIALIZATION_TOKEN_LIFECYCLE_BYPASSED` | use the frozen Seed/token/AllocationIntent/ALLOCATED-root/ConsumeIntent/CONSUMED-root two-CAS lifecycle and advance the ordinal once | `ADDRESSED` |
| `G77_45_B03_SUCCESSOR_CONSTITUTIONAL_STATE_READ_BACK_UNDERIVED` | derive one closed `CandidateHSuccessorConstitutionalStateV1` before CONSUMED coordinator/root creation; the root and read-back bind that exact pair | `ADDRESSED` |

No G77-43 or G77-45 finding is repaired outside this artifact. G77-43 B03 is
not reopened.

## Retained External and Human Contracts

Revision 4 retains without semantic change:

- one genuinely external independently prior constituent premise;
- one externally supplied global Universe and complete Census with one
  eligible source and one eligible Instrument;
- Human as the sole semantic decision source and one non-equivocating Human
  Finality slot before HIC/CHE transport;
- predicate-only Certification;
- the external target-disposition domain and its terminal one-shot state;
- the atomic external status-subject/status-vector update contract;
- StatusCurrentVersion plus exact target predecessor -> Snapshot -> Fence ->
  dual-version BEGIN_CONSUMPTION CAS;
- irreversible no-reset/no-reissue/no-second-target dormancy;
- ordinary G70 CAP as the only normal amendment lifecycle; and
- one production path and zero parallel paths.

Revision 4 target, Instrument commitment, and Instrument lineage rows replace
the G77-44 proposal/assessment pairs with the exact G77-46 pair and a future
independent G77-46 assessment pair whose classification must be
`CONSTITUTIONAL_IMPACT_RESOLVED_AT_PROPOSAL_LEVEL`. Concrete evidence can only
be constructed after both artifacts finalize. This forward lineage update is
mechanical and changes no external authority semantic.

The Revision 4 Target/Instrument/Transition replacements are otherwise the
exact retained G77-44 schemas with these closed substitutions:

| Row | Exact Revision 4 substitution |
|---|---|
| Target/Instrument lineage | add exact G77-45 and G77-46 pairs plus future G77-46 assessment pair; the assessment must resolve Revision 4 |
| required root contract | `ConstitutionalRootEvolutionSnapshotV2` in the sole frozen domain |
| required success contract | `EXTERNAL_CONSTITUENT_CANDIDATE_H_SUCCESS_V4` |
| required allocation generation | predecessor root generation plus one |
| required terminal successor generation | predecessor root generation plus two |
| required operation kind | `EXTERNAL_CONSTITUENT_FIRST_ADOPTION` inside the frozen coordinator lifecycle |
| FoundingTransition reserved generation | terminal successor generation `G + 2`; allocation generation is not an effect result |

The fields `required_successor_root_contract =
CandidateHConstitutionalRootSnapshotV3`, Revision 3 success-contract token, and
`reserved_successor_root_generation = G + 1` are replaced, not retained.
No other external or Human field changes.

## B01 — Actual Frozen Root Representation Reuse

### Controlling representation

The controlling root is the existing
`ConstitutionalRootEvolutionSnapshotV2`, selected only by
`ConstitutionalRootEvolutionSnapshotCurrentPointerV1` in
`CONSTITUTIONAL_ROOT_EVOLUTION_SNAPSHOT_DOMAIN_V1`. It is not an ordered
generic component array. Every authoritative reader directly resolves the
following frozen logical rows:

1. active baseline identity/digest and logical active-baseline pointer value;
2. global `MetaRepairStateV1` identity/digest;
3. `OrdinaryCAPReachabilityStateV1` identity/digest, including exact-target
   status and reachability epoch;
4. current normative registry root and authority projection/manifest roots;
5. source/evidence registry roots and epochs determining reachability;
6. `ConstitutionalRootSerializationCoordinatorStateV2` identity/digest; and
7. `ConstitutionalEvolutionLivenessProofSlotMapStateV1` identity/digest.

Revision 4 introduces no root-reader expansion rule, component role/type,
component ordinal, recursive manifest, root pointer, or snapshot family. It
withdraws Revision 3's `ConstitutionalRootInheritedComponentManifestV1`,
`CandidateHOrdinaryCAPStatusComponentV1`,
`CandidateHMetaRepairStatusComponentV1`, `CandidateHTopologyComponentV1`, and
`CandidateHConstitutionalRootSnapshotV3` from the controlling Revision 4
model. Those Revision 3 proposal types remain immutable historical text but
have no Revision 4 effect.

### Exact allocation-root change set

Let `R0` be the exact current frozen root and `G` its generation. The prepared
allocation root `R1` is the existing root type at generation `G + 1`:

| Direct frozen row | R1 value |
|---|---|
| active baseline and logical State | exact R0 bytes |
| MetaRepairState pair | exact R0 pair |
| CAP reachability pair/epoch | exact R0 pair/epoch |
| registry/projection/manifest roots | exact R0 bytes |
| source/evidence roots/epochs | exact R0 bytes |
| coordinator pair | exact derived ALLOCATED V2 pair |
| SlotMap pair | exact R0 pair |

The changed-component bitmap has exactly the coordinator bit. Any other
change invalidates allocation.

### Exact consuming-root change set

Let `R1` be current and its exact coordinator be ALLOCATED. The consuming
successor `R2` is the same frozen root type at generation `G + 2`:

| Direct frozen row | R2 value |
|---|---|
| active baseline identity/digest | exact NormativeSuccessorPayload pair |
| logical active-baseline pointer value | exact Candidate H successor Constitutional State pair |
| MetaRepairState pair | exact derived successor DORMANT pair for the new baseline |
| CAP reachability pair/epoch | exact recomputation for the new baseline; result must be `REACHABLE` and `COMPLETE_CHAIN_EXISTS` |
| registry/projection/manifest roots | exact R1 bytes |
| source/evidence roots/epochs | exact R1 bytes |
| coordinator pair | exact derived CONSUMED V2 pair |
| SlotMap pair | exact R1 bytes, retained as immutable history |

The Candidate H operation is eligible only if the retained registry,
projection, manifest, and source/evidence roots are sufficient to recompute
the required reachable CAP State for the successor baseline. Candidate H
cannot assert reachability by status prose. If recomputation differs, the
operation cannot consume and follows the frozen deterministic abandonment
rules.

The consuming changed-component bitmap is exactly:

~~~text
ACTIVE_BASELINE
| ACTIVE_BASELINE_LOGICAL_STATE
| META_REPAIR_STATE
| ORDINARY_CAP_REACHABILITY_STATE
| SERIALIZATION_COORDINATOR
~~~

Every registry/projection/source/SlotMap bit is zero and its bytes must repeat
exactly. The topology tuple and terminal founding status are normative fields
of the exact NormativeSuccessorPayload and successor State; they do not become
invented root components.

### Existing capability reachability proof

Every pre-existing reader follows the same current-pointer identity and reads
the same direct field path before and after. Registry, projection, manifest,
source/evidence, and SlotMap pairs are byte-identical. The successor CAP and
MetaRepair States retain their existing artifact types and direct root paths.
The new active baseline contains the exact frozen G77-36 normative slice and
retains ordinary CAP as sole normal lifecycle.

~~~text
existing reader path before = current pointer -> direct frozen row
existing reader path after  = current pointer -> same direct frozen row

existing capability reachability before
= existing capability reachability after
~~~

The only intended reachability reduction is the external Candidate H founding
authority itself: BEGIN makes it one-shot CONSUMING and terminal success makes
it permanently `CONSUMED_DORMANT`. No previously reachable certified
capability is hidden behind a manifest or removed.

## B02 — Frozen Serialization Token Lifecycle Reuse

### Candidate H OperationSeed binding

Revision 4 reuses `ConstitutionalSerializationOperationSeedV1` without a new
seed, token, coordinator, pointer, owner, or serialization domain. Its generic
`operation_kind` field receives the minimum additive registered value:

~~~text
operation_kind = EXTERNAL_CONSTITUENT_FIRST_ADOPTION
producing_owner = CONSTITUTIONAL_ROOT_SERIALIZATION_CUSTODIAN
candidate_scope = exact Target founding_scope pair
predecessor root/pointer = exact R0/G pair
ordered immutable inputs = Target, Instrument, Human Decision/Finality,
  ProofSet, Certification, Transition, ConsumingDisposition,
  StatusSnapshot, Fence, NormativeSuccessorPayload,
  predecessor State/baseline/MetaRepair/CAP/registry/source/coordinator/SlotMap
expected_successor_component_mask = exact consuming bitmap above
operation_idempotency_identity = exact Candidate H finalized-input hash
~~~

`EXTERNAL_CONSTITUENT_FIRST_ADOPTION` names one business operation inside the
already generic frozen lifecycle. It adds no transition, pointer, lock,
coordinator status, domain, owner, or retry rule and is unreachable after the
external one-shot slot leaves CONSUMING.

### Exact allocation sequence

The sequence is the frozen sequence and no Candidate H alternative exists:

~~~text
R0 + immutable non-time inputs
-> ConstitutionalSerializationOperationSeedV1
-> deterministic constitutional-root-token identity at ordinal K
-> ConstitutionalSerializationTokenAllocationIntentV1 as replaced by G77-36
-> ConstitutionalRootSerializationCoordinatorStateV2 status ALLOCATED
-> prepared R1 containing that State and every other R0 row unchanged
-> ConstitutionalRootSnapshotPointerCASIntentV1
-> ConstitutionalRootSnapshotPointerCASV1 installs R1
-> ConstitutionalRootEvolutionCommitMarkerV2
-> ConstitutionalRootSnapshotReadBackV1
-> existing AllocationReceipt
~~~

The AllocationIntent binds R0, predecessor coordinator, Seed, token, owner,
ordinal K, allocation logical instant, and reserved `ALLOCATED`; it binds no
State/root/CAS/Receipt successor. The ALLOCATED State binds the finalized
Intent and has `next_token_ordinal = K`. The allocation CAS is the only
linearization. A losing prepared token has zero authority.

### Exact consumption sequence

After exact R1 read-back, Revision 4 reuses
`ConstitutionalSerializationTokenConsumeIntentV1`. For Candidate H its closed
binding is:

~~~text
predecessor root/pointer/generation = exact current R1/G+1
predecessor coordinator = exact ALLOCATED V2 pair
allocation Intent/Seed/token/owner/ordinal = exact retained pairs/values
allocation read-back/Receipt = exact finalized pairs
consuming operation kind = CONSUME_ALLOCATED_TOKEN
business operation kind = EXTERNAL_CONSTITUENT_FIRST_ADOPTION
business Transition/ConsumingDisposition = exact pairs
expected changed-component mask = exact consuming bitmap
expected terminal result = CANDIDATE_H_ADOPTION_COMMITTED
terminal logical instant = exact phase TERMINAL for R1/K
~~~

The Intent reserves content and result only. Under the frozen forward-only
rule it binds no successor State, CONSUMED State, root, CAS, marker,
read-back, terminal disposition, or Receipt.

From that finalized Intent, already finalized business inputs derive in order:

1. successor `MetaRepairStateV1` with status `DORMANT`, new baseline pair,
   exact Candidate H Transition as its one-shot founding predecessor, neutral
   repair fields, and no later root/CAS pair;
2. successor `OrdinaryCAPReachabilityStateV1` with epoch exactly predecessor
   plus one, new baseline/State inputs, unchanged registry/source inputs,
   result `REACHABLE` and `COMPLETE_CHAIN_EXISTS`, and no later root/CAS pair;
3. `CandidateHSuccessorConstitutionalStateV1` below;
4. `ConstitutionalRootSerializationCoordinatorStateV2` status `CONSUMED`,
   retaining Seed/token/owner/allocation facts, terminal result
   `CANDIDATE_H_ADOPTION_COMMITTED`, canonical-null failure evidence, and
   `next_token_ordinal = K + 1`; and
5. R2 from those finalized pairs and exact repeated unchanged rows.

The existing root CAS family installs R2 from exact R1. The CAS consumes token
K only through the exact ConsumeIntent and terminal coordinator successor.
Token K remains recorded terminally and cannot be reassigned or reused.

### Token idempotency and exclusion

~~~text
same R0 + same Seed inputs -> same token K -> same R1
same R1 + same ConsumeIntent inputs -> same States -> same R2

different content under Seed/token/operation idempotency -> fail closed
current coordinator CONSUMED or ordinal K+1 -> token K ineligible
external slot terminal -> second Candidate H BEGIN ineligible
~~~

The only other transition from ALLOCATED is the frozen deterministic
`ABANDON_ALLOCATED_TOKEN`. It changes no business row, installs ABANDONED,
records exact singleton failure evidence, and advances to K+1.

## B03 — Successor Constitutional State Derivation

### Minimum additive State artifact

The frozen root exposes the active baseline plus a logical active-baseline
pointer value but does not define a Candidate H aggregate successor State
artifact. Revision 3 required such a pair at read-back without deriving it.
The minimum additive artifact is
`CandidateHSuccessorConstitutionalStateV1`, version `V1`, with identity prefix
`candidate-h-constitutional-state-v1` and idempotency prefix
`candidate-h-constitutional-state-idem-v1`.

It uses the retained G77-44 CJ1 common envelope and has exactly these semantic
fields:

~~~text
predecessor_constitutional_state_identity
predecessor_constitutional_state_digest
predecessor_active_baseline_identity
predecessor_active_baseline_digest
successor_active_baseline_identity
successor_active_baseline_digest
target_identity
target_digest
normative_successor_payload_identity
normative_successor_payload_digest
transition_identity
transition_digest
consuming_disposition_identity
consuming_disposition_digest
consume_intent_identity
consume_intent_digest
successor_meta_repair_state_identity
successor_meta_repair_state_digest
successor_cap_reachability_state_identity
successor_cap_reachability_state_digest
normative_registry_root
authority_projection_identity
authority_projection_digest
authority_manifest_identity
authority_manifest_digest
source_evidence_registry_root
source_evidence_registry_epoch
proof_slot_map_state_identity
proof_slot_map_state_digest
founding_authority_status = CONSUMED_DORMANT
ordinary_amendment_lifecycle = G70_CAP_ONLY
canonical_hic_family_count = 1
canonical_human_entry_count = 1
production_owner_chain_count = 1
production_path_count = 1
parallel_production_path_count = 0
state_status = ACTIVE
effective_logical_instant
producing_owner = CONSTITUTIONAL_ROOT_SERIALIZATION_CUSTODIAN
metadata = {}
~~~

All fields are mandatory. Every pair and root comes from the exact R1,
NormativeSuccessorPayload, Transition, external CONSUMING read-back,
ConsumeIntent, or derived successor MetaRepair/CAP State. Registry,
projection, manifest, source/evidence, and SlotMap values must equal R1
byte-for-byte. The logical instant is the frozen terminal instant for token K;
no clock is sampled.

The successor active baseline pair equals the NormativeSuccessorPayload pair.
The predecessor State/baseline pairs equal Target, ProofSet, Transition, and
current R1 read-back. Unknown fields, half-pairs, alternate topology, supplied
successor values, or a mismatched direct root input reject.

Let `S_state` be the CJ1 object containing exactly those semantic fields plus
the retained common envelope constants except identity, digest, idempotency,
and metadata:

~~~text
state_idempotency_identity =
  candidate-h-constitutional-state-idem-v1:SHA256(CJ1(S_state))

P_state = S_state + state_idempotency_identity

successor_constitutional_state_identity =
  candidate-h-constitutional-state-v1-sha256:SHA256(CJ1(P_state))

successor_constitutional_state_digest = sha256:SHA256(CJ1(P_state))
~~~

The identity and digest prefixes distinguish namespace from byte digest; both
derive from the same one canonical payload. The State binds no coordinator
successor, R2, CAS, marker, read-back, external terminal disposition, or
Receipt.

### Root and read-back binding

R2 directly installs the State pair as its existing logical active-baseline
pointer value and installs the NormativeSuccessorPayload as active baseline.
The root identity hashes every direct frozen row, including that exact logical
State pair, successor MetaRepair/CAP pairs, CONSUMED coordinator, unchanged
registry/source rows, and unchanged SlotMap. Thus a different State changes
R2 and cannot pass the CAS.

The existing `ConstitutionalRootSnapshotReadBackV1` is reused. Its complete
logical successor-pair read-back includes:

~~~text
observed active baseline = exact NormativeSuccessorPayload pair
observed logical State = exact CandidateHSuccessorConstitutionalStateV1 pair
observed MetaRepair = exact successor DORMANT pair
observed CAP reachability = exact successor REACHABLE/COMPLETE pair
observed coordinator = exact CONSUMED pair
observed unchanged rows = exact R1 bytes
read_back_result = COMPLETE_SUCCESSOR_ROOT_CURRENT
~~~

Partial, mixed, supplied-only, or different State read-back produces no
successful artifact.

### Terminal propagation and uniqueness

`ExternalConstituentOneShotSuccessfulDispositionEvidenceV4` completely
replaces the V3 success row only. Version is `V4`; owner remains the external
disposition-domain owner. Its exact semantic fields are:

~~~text
universe_identity
universe_digest
census_identity
census_digest
source_evidence_identity
source_evidence_digest
instrument_identity
instrument_digest
target_identity
target_digest
consuming_disposition_identity
consuming_disposition_digest
predecessor_slot_status = CONSUMING
human_decision_identity
human_decision_digest
human_finality_identity
human_finality_digest
proof_set_identity
proof_set_digest
certification_identity
certification_digest
transition_identity
transition_digest
status_snapshot_identity
status_snapshot_digest
consumption_fence_identity
consumption_fence_digest
operation_seed_identity
operation_seed_digest
serialization_token_identity
serialization_token_digest
allocation_intent_identity
allocation_intent_digest
allocated_coordinator_state_identity
allocated_coordinator_state_digest
allocated_root_identity
allocated_root_digest
allocation_root_cas_identity
allocation_root_cas_digest
allocation_root_read_back_identity
allocation_root_read_back_digest
consume_intent_identity
consume_intent_digest
successor_constitutional_state_identity
successor_constitutional_state_digest
consumed_coordinator_state_identity
consumed_coordinator_state_digest
next_token_ordinal
dormancy_state_identity
dormancy_state_digest
successor_root_identity
successor_root_digest
root_cas_intent_identity
root_cas_intent_digest
root_cas_identity
root_cas_digest
commit_marker_identity
commit_marker_digest
root_read_back_identity
root_read_back_digest
target_disposition_current_pointer_identity
expected_consuming_slot_digest
expected_consuming_slot_generation
installed_terminal_slot_digest
installed_terminal_slot_generation
successful_disposition_cas_identity
read_back_terminal_slot_digest
terminalized_at
disposition_kind = ROOT_ADOPTION_COMMITTED
slot_status = CONSUMED_DORMANT
successful_effect_count = 1
founding_authority_reachable = false
reissue_permitted = false
reset_permitted = false
~~~

All identity/digest fields are complete pairs. Every root field equals the
R2/common frozen CAS chain; the Candidate-H-specific V3 CAS/marker/read-back
types are not used. The terminal external CAS still compares the exact
CONSUMING slot, installs
`CONSUMED_DORMANT`, reads it back, and contains no Receipt dependency.
`next_token_ordinal = token_ordinal + 1` and equals the CONSUMED coordinator.

`ExternalConstituentFoundingSuccessfulReceiptV4` completely replaces the V3
success Receipt only. Version is `V4`; owner remains the root custodian. Its
exact semantic fields are:

~~~text
universe_identity
universe_digest
census_identity
census_digest
source_evidence_identity
source_evidence_digest
recognition_proof_identity
recognition_proof_digest
target_identity
target_digest
instrument_identity
instrument_digest
human_decision_identity
human_decision_digest
human_finality_identity
human_finality_digest
decision_disposition_identity
decision_disposition_digest
consuming_disposition_identity
consuming_disposition_digest
terminal_disposition_identity
terminal_disposition_digest
status_snapshot_identity
status_snapshot_digest
proof_set_identity
proof_set_digest
certification_identity
certification_digest
transition_identity
transition_digest
operation_seed_identity
operation_seed_digest
serialization_token_identity
serialization_token_digest
allocation_intent_identity
allocation_intent_digest
allocated_coordinator_state_identity
allocated_coordinator_state_digest
allocated_root_identity
allocated_root_digest
allocation_root_cas_identity
allocation_root_cas_digest
allocation_root_read_back_identity
allocation_root_read_back_digest
consume_intent_identity
consume_intent_digest
successor_constitutional_state_identity
successor_constitutional_state_digest
consumed_coordinator_state_identity
consumed_coordinator_state_digest
next_token_ordinal
dormancy_state_identity
dormancy_state_digest
predecessor_root_identity
predecessor_root_digest
successor_root_identity
successor_root_digest
root_cas_intent_identity
root_cas_intent_digest
root_cas_identity
root_cas_digest
commit_marker_identity
commit_marker_digest
root_read_back_identity
root_read_back_digest
receipt_stage = SUCCESS
receipt_result = ADOPTION_COMMITTED
successful_effect_count = 1
founding_authority_reachable = false
ordinary_future_amendment_lifecycle = G70_CAP_ONLY
meta_repair_status = ADOPTED_DORMANT_EXACT_G77_38_ONLY
produced_at
~~~

All pairs equal the exact finalized predecessors, and the terminal disposition
pair resolves specifically to V4. All root pairs equal the R2/common frozen
CAS chain. `produced_at` equals the terminal token logical instant. No Receipt
field participates in a predecessor identity.

~~~text
same lawful finalized inputs
-> one successor MetaRepair State + one successor CAP State
-> one CandidateHSuccessorConstitutionalStateV1
-> one CONSUMED coordinator -> one R2
-> one root CAS/marker/read-back
-> one terminal disposition -> one successful Receipt
~~~

Same idempotency with different bytes fails closed. Identical retry returns
the already finalized artifact.

## Preserved External Revocation / BEGIN Linearization

G77-44's `ExternalConstituentAuthorityStatusCurrentVersionV1`, status snapshot,
fence, and external BEGIN CAS remain unchanged in fields, identity formulas,
owner, transaction domain, and ordering:

~~~text
current target slot = exact DECISION_BOUND_ADOPT pair/generation
AND
current StatusCurrentVersion = exact ALL_ACTIVE pair/generation
-> atomic BEGIN_CONSUMPTION compare-and-set
-> exact CONSUMING read-back
~~~

Subject invalidation and aggregate-vector movement remain one atomic external
operation. Invalidation first changes a compared version and stale BEGIN
fails. BEGIN first freezes the exact one-shot content; later revocation cannot
reinterpret it or create future authority. The only mechanical dependency
change is that CONSUMING now precedes OperationSeed and reserves final root
generation `G + 2`, accounting for the mandatory allocation root.

G77-43 B03 remains:

~~~text
RESOLVED_AT_PROPOSAL_LEVEL
~~~

## Complete Revision 4 Identity DAG

~~~text
external premise -> Universe -> Census -> SourceEvidence -> RecognitionProof
-> Instrument

Human Decision -> Human Finality
external status facts -> StatusCurrentVersion
Target slot + StatusCurrentVersion -> Snapshot -> Fence
ProofSet -> predicate-only Certification -> Founding Transition
Transition + Fence -> BEGIN CAS -> ConsumingDisposition

R0 + finalized Candidate H inputs -> OperationSeed -> token
-> AllocationIntent -> ALLOCATED coordinator State -> R1
-> allocation CAS intent -> allocation CAS -> marker -> allocation read-back
-> AllocationReceipt -> ConsumeIntent

ConsumeIntent + finalized business inputs
-> successor MetaRepair State + successor CAP State
-> CandidateHSuccessorConstitutionalStateV1
-> CONSUMED coordinator State -> R2
-> terminal root CAS intent -> root CAS -> marker -> root read-back
-> external terminal SuccessfulDispositionV4
-> SuccessfulReceiptV4
~~~

Every arrow begins at finalized predecessors. Seed binds no token; token binds
no Intent; AllocationIntent binds no State/root; State binds no root/CAS;
ConsumeIntent binds no successor; successor business State binds no
coordinator/root; root binds no CAS; CAS binds no marker; marker binds no
read-back; terminal disposition binds no Receipt. No Receipt is a predecessor
of State, root, CAS, disposition, or another Receipt.

The DAG is `FINITE_ACYCLIC_FORWARD_BYTE_DETERMINISTIC`.

## Complete Revision 4 Authority DAG

~~~text
genuinely external constituent premise
-> external source / Instrument / status / disposition authority
-> Human-only semantic decision + non-equivocating custody
-> predicate-only Certification
-> external one-shot BEGIN authorization
-> existing frozen root coordinator/token authority
-> mechanical exact R0 -> R1 -> R2 effect
-> external terminal CONSUMED_DORMANT
-> permanent founding-authority dormancy
~~~

The external authority does not operate the root. Human does not perform CAS.
Certification does not choose or mutate. Root custody cannot create the
external premise, select Human semantics, bypass BEGIN, mint an unallocated
token, or consume without exact ALLOCATED predecessor and ConsumeIntent. The
coordinator authorizes only the mechanical effect already fixed by external
and Human predecessors.

No Candidate H artifact, successor root, current Constitution, Governance,
Certification, repository, deployment, or Receipt authorizes itself. The
authority DAG is `FINITE_ACYCLIC_NO_NEW_OWNER_NO_SELF_AUTHORIZATION`.

## Crash, Retry, and Concurrency Closure

| Boundary/attack | Exact Revision 4 result |
|---|---|
| before token allocation | R0 current; no token authority |
| Seed/Intent preparation | R0 current; prepared bytes have zero effect |
| during allocation CAS | exact R0 or complete R1; never partial |
| concurrent allocation | one R0 CAS winner; loser token has zero authority |
| after R1 before read-back | current R1 reconstructs exact marker/read-back/Receipt |
| after R1 before ConsumeIntent | exact ALLOCATED coordinator blocks unrelated root operations |
| before consuming CAS | R1 remains current; identical State/coordinator/R2 bytes reconstruct |
| during consuming CAS | exact R1 or complete R2; no mixed business/coordinator state |
| competing root operation | ALLOCATED permits only consume or deterministic abandon; same R1 CAS has one winner |
| stale predecessor | pointer/root/generation/coordinator comparison fails; no committed CAS |
| after R2 before read-back | R2 and committed CAS reconstruct exact marker/read-back |
| after root read-back before terminal disposition | external slot remains CONSUMING; retry terminalizes from identical read-back |
| during terminal external CAS | exact CONSUMING or complete CONSUMED_DORMANT slot |
| after terminal disposition before Receipt | identical Receipt reconstructs from finalized predecessors |
| identical retry | return exact existing artifact at current phase |
| same idempotency different content | fail closed |
| token reuse | CONSUMED/ABANDONED predecessor and ordinal K+1 reject token K |
| second Candidate H success | external terminal slot, maximum effect count 1, and consumed token all reject |
| crash without reconstructable immutable input | frozen singleton failure reduction authorizes only exact ABANDONED R2 with no business changes |

Every atomic root boundary has predecessor-or-complete-successor semantics.
There is no duration, wall clock, partial row visibility, merge, or alternate
serialization domain.

## Minimum Change / Reuse Test

| Proposed artifact/field | Existing frozen reuse question | Exact result |
|---|---|---|
| root snapshot/current pointer/domain | can frozen root family be reused? | yes; reuse exactly, add none |
| root direct rows | can direct fields replace manifest abstraction? | yes; repeat exact frozen rows |
| OperationSeed/token/AllocationIntent | can frozen family bind Candidate H? | yes; reuse; only register business operation kind |
| ALLOCATED/CONSUMED coordinator | can frozen V2 lifecycle be reused? | yes; reuse exact statuses and ordinal rules |
| root CAS/marker/read-back | can frozen generic chain be reused? | yes; withdraw Candidate-H-specific chain |
| MetaRepairState | can existing V1 State be reused? | yes; derive one DORMANT successor with exact one-shot founding predecessor binding |
| CAP reachability State | can existing V1 State be reused? | yes; recompute epoch and results from successor baseline and unchanged roots |
| SlotMap | can it be reused unchanged? | yes; repeat exact pair/bytes |
| registry/projection/source rows | can they be reused unchanged? | yes, but only if successor CAP recomputation passes |
| aggregate successor Constitutional State | is there a frozen artifact producing the pair required by Candidate H read-back? | no; add only `CandidateHSuccessorConstitutionalStateV1` and install it in the existing logical active-baseline State slot |
| external status/BEGIN | can Revision 3 contract be reused? | yes; unchanged except reserved generation `G + 2` |
| terminal disposition/Receipt | can V3 rows carry frozen lifecycle/State proof? | no; V4 adds only direct lifecycle and successor-State bindings |

Architectural convenience, generic arrays, manifest nesting, duplicate root
families, new pointers, new domains, new owners, and new clocks are rejected
as justifications.

## Topology and Reuse Impact Assessment

Numerical topology remains:

| Metric | Before | After |
|---|---:|---:|
| canonical HIC families | 1 | 1 |
| Canonical Human Entries | 1 | 1 |
| production owner chains | 1 | 1 |
| `production_paths_before` / `production_paths_after` | 1 | 1 |
| `parallel_production_paths_before` / `parallel_production_paths_after` | 0 | 0 |
| `permanent_authority_owners_added` | 0 | 0 |
| `current_roots_added` | 0 | 0 |
| `permanent_serialization_domains_added` | 0 | 0 |
| `ordinary_amendment_lifecycles_added` | 0 | 0 |
| `reusable_founding_authorities_added` | 0 | 0 |

The intermediate R1 is a generation of the sole current root, not a second
root or path. The Candidate H operation kind is one transaction class inside
the existing root domain, not a lifecycle. External disposition remains prior
external authority, not a SAPIANTA production route.

Reuse Impact Assessment:

1. **Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?**

   Ponovno se uporabijo G48, G69 Human Authority/HIC/CHE meje, običajni G70
   CAP, G76 identity pravila, G77-36/G77-38 neposredni root, coordinator,
   token, SlotMap, CAS, Replay/CRO ter G77-44/G77-45 zunanji status/BEGIN
   model. Root, pointer, domain in owner se ne podvojijo.

2. **Katere nove zmogljivosti (če sploh) nastanejo?**

   Samo neaktivni predlog: minimalni Candidate H business-operation-kind,
   en deterministični `CandidateHSuccessorConstitutionalStateV1` in V4
   terminalna evidence/Receipt vezava. Nobena runtime zmogljivost ne nastane.

3. **Ali katera obstoječa zmogljivost postane nedosegljiva?**

   Ne. Vsaka prej dosegljiva zmogljivost ostane na isti neposredni root poti.
   Registry/projection/source/SlotMap vrstice ostanejo byte-identične. Samo
   enkratna ustanovna oblast namerno postane trajno nedosegljiva.

4. **Ali implementacija/proposed mechanism ustvarja vzporedni tok?**

   Ne. R0 -> R1 -> R2 uporablja isti pointer, domain, coordinator in owner.
   Zunanji BEGIN ni dodatni SAPIANTA execution tok.

5. **Ali zmanjšuje ali povečuje število produkcijskih poti?**

   Ne. Produkcijska pot ostane ena, vzporedne poti ostanejo nič.

Capability reachability result:

~~~text
all previously reachable certified capabilities: SAME DIRECT PATH
ordinary G70 CAP: SOLE NORMAL LIFECYCLE
Candidate H founding authority after success: PERMANENTLY UNREACHABLE
~~~

## External Prerequisites and Next Boundary

The following remain absent and are not repaired or fabricated here: the
genuinely external premise and Universe, concrete external status/disposition
domain, Census, source, Instrument, Human Decision/Finality, Certification,
BEGIN result, tokens, States, roots, CAS records, dispositions, and Receipts.
Their absence keeps eligibility false and is
`EXTERNAL_PREREQUISITE_NOT_MODEL_DEFECT`.

Revision 4 requires a later independent G70-03 assessment. Proposal presence
does not authorize Ratification, adoption, implementation, publication,
activation, O01, CDP, deployment, or production mutation.

# 2. Code Evidence

## Public API

No runtime API, model class, schema, validator, serializer, route, command,
pointer, provider, store, or persistence behavior is added or changed. Names
and payloads are proposal-only Constitutional contracts.

## Orchestration Entry Point

The only Human production entry remains:

~~~text
Human -> permitted HIC -> sole CHE -> exact eligible owner
-> sole CHE Response/Continuation -> same HIC
~~~

The external status domain is not a SAPIANTA ingress. Root custody is a
mechanical effect boundary and cannot produce Human or constituent semantics.

## Semantic Reductions

### Root representation

~~~text
same frozen pointer + same direct rows + changed bitmap
-> one lawful R1 or R2

generic array / nested manifest / alternate root type -> reject
~~~

### Serialization

~~~text
Seed -> token -> AllocationIntent -> ALLOCATED R1
-> ConsumeIntent -> State -> CONSUMED R2
-> next ordinal K+1; token K terminal
~~~

### Successor State

~~~text
finalized predecessor + exact business inputs
-> one State -> one R2 -> one read-back
-> one terminal disposition -> one Receipt
~~~

### External race

~~~text
invalidation first -> compared vector/slot changes -> BEGIN fails
BEGIN first -> exact one-shot content frozen -> later revocation non-retroactive
~~~

## Public Validators

No validator is implemented. A future separately authorized validator must
reject:

- a generic predecessor array, invented role/type, nested manifest, or
  alternate root family;
- any allocation-root change other than coordinator AVAILABLE -> ALLOCATED;
- a Candidate H consume lacking exact Seed/token/Intent/R1/read-back;
- a ConsumeIntent not bound to the current ALLOCATED coordinator/token;
- a terminal root lacking exact CONSUMED coordinator and ordinal K+1;
- token reuse, skipped generation, stale pointer, or changed unchanged row;
- a supplied or differently derived successor Constitutional State;
- a root/read-back/terminal disposition/Receipt State-pair mismatch;
- CAP successor results not recomputed from exact successor inputs;
- stale external target/status-vector versions at BEGIN;
- any internal substitute for external authority or Human semantic choice;
- any new owner, pointer, serialization domain, lifecycle, path, clock, reset,
  reissue, second target, or second success; and
- Replay/CRO mutation or authority expansion.

## Canonical Data Models

| Model | Exact owner/source | Revision 4 use |
|---|---|---|
| frozen RootSnapshotV2/current pointer | root custodian/domain | reused unchanged |
| OperationSeed/token/AllocationIntent | root custodian | reused unchanged with Candidate H operation kind |
| CoordinatorStateV2 | root custodian | ALLOCATED then CONSUMED |
| ConsumeIntentV1 | root custodian | exact business consume reservation |
| MetaRepairStateV1 | Governance state semantics/root custody | successor DORMANT pair |
| CAPReachabilityStateV1 | Governance evidence semantics/root custody | successor REACHABLE/COMPLETE pair |
| CandidateHSuccessorConstitutionalStateV1 | root custodian | one aggregate logical State pair |
| generic root CAS/marker/read-back | root custodian | both allocation and consume roots |
| SuccessfulDispositionV4 | external disposition owner | terminal external effect evidence |
| SuccessfulReceiptV4 | root custodian | terminal reconstruction only |
| Replay/CRO | owner-local/passive | read-only/passive |

## Deterministic Algorithms

1. Authenticate G77-36 through G77-45 and future G77-46 assessment.
2. Resolve one external Universe/Census/Instrument and one Human Finality.
3. Reapply unchanged status Snapshot/Fence/BEGIN dual comparison.
4. Resolve R0 and every direct frozen row; derive the exact Candidate H Seed.
5. Derive token K, AllocationIntent, ALLOCATED State, R1, and allocation CAS
   chain under the existing root domain.
6. Re-read R1 and derive one ConsumeIntent.
7. Recompute successor MetaRepair/CAP States and derive one successor
   Constitutional State without supplied values.
8. Derive CONSUMED coordinator K+1 and R2 with exact unchanged-row equality.
9. CAS R1 -> R2, read back every direct row, and require complete equality.
10. Terminalize the external slot and reconstruct one V4 Receipt.
11. On exact frozen failure, abandon without business changes.
12. Replay immutable predecessors without mutation or live-clock inference.

## Responsibility Boundaries

| Responsibility | Exact source/owner | Negative boundary |
|---|---|---|
| constituent premise/status/disposition | genuinely prior external authority/domain | no internal substitute |
| semantic choice | Human Authority | sole Human decision source |
| transport | HIC/CHE | no finality/authority/root decision |
| predicate verification | Certification owner | no choice or mutation |
| root serialization | existing root custodian/coordinator | no premise/Human/content choice |
| CAP/MetaRepair State semantics | existing Governance contracts | no second lifecycle |
| reconstruct | Replay | read-only; no repair |
| observe | CRO | passive |
| assess Revision 4 | later independent Constitutional Governance | not performed here |
| implement | separately authorized future CDP | not authorized |

## Repository Evidence

Evidence consists of authenticated committed G77-36 through G77-45, the
G77-32/G77-34 direct root and coordinator structures as finalized by
G77-36/G77-37 and frozen by G77-38, the exact G77-45 blocker set, retained
G77-44 external status model, G69/G70 boundaries, and G76 identity rules. No
self-assessment, runtime result, missing external instance, credential, or
test fixture supplies constituent authority.

# 3. Constitutional Self-Assessment

## Verified as Proposal Structure

- G77-36 through G77-45 lineage and digests are authenticated.
- Exactly the three G77-45 blockers receive explicit minimal repairs.
- Revision 4 uses direct frozen root rows and no generic array/manifest.
- Allocation and consumption use the existing two-CAS token lifecycle.
- Token K terminalizes and the next ordinal advances once.
- One successor Constitutional State is derived before coordinator/root.
- Root read-back binds that exact State and every direct successor row.
- Identity and authority DAGs are finite, acyclic, and forward-only.
- G77-43 B03 external race remains resolved at proposal/design level.
- Existing capability paths remain direct and unchanged.
- Human, external authority, CAP, Replay, CRO, and topology boundaries remain.
- No runtime, adoption, Ratification, Certification, publication, activation,
  O01, CDP, deployment, or production mutation occurs.

## Not Verified

- No independent G70-03 assessment of Revision 4 has occurred.
- No concrete external premise, Universe, status domain, source, Instrument,
  Human Finality, root, token, State, CAS, disposition, or Receipt exists.
- No schema, validator, transaction, persistence, recovery, or Replay reader
  is implemented.
- No concurrency, crash, cryptographic, custody, security, migration,
  rollback, deployment, or production behavior is tested.
- Proposal claims cannot serve as adoption or implementation authority.
- Existing hook, enforcement, privacy, custody, deployment, external-system,
  and partial-conformance limitations remain visible and unchanged.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| G48 structure | six sections and required Code Evidence subsections | heading review | `PASS` |
| committed lineage | HEAD/tree/parent and G77-36 through G77-45 digests | Git/SHA-256 | `PASS` |
| predecessor immutability | no G77-36 through G77-45 mutation | repository review | `PASS` |
| G77-45 B01 | direct frozen root tuple; no manifest/array | representation review | `ADDRESSED_PROPOSED` |
| allocation root | coordinator-only exact R0 -> R1 change | bitmap review | `PASS_PROPOSED` |
| consuming root | exact business rows plus CONSUMED coordinator | root review | `PASS_PROPOSED` |
| unchanged rows | exact direct byte equality | reachability review | `PASS_PROPOSED` |
| G77-45 B02 | complete frozen two-CAS token lifecycle | lifecycle review | `ADDRESSED_PROPOSED` |
| allocation identity order | Seed/token/Intent/State/root/CAS | DAG review | `PASS_PROPOSED` |
| consumption identity order | Intent/State/coordinator/root/CAS | DAG review | `PASS_PROPOSED` |
| ordinal/no reuse | K -> terminal K+1 | retry review | `PASS_PROPOSED` |
| G77-45 B03 | canonical successor State before root | derivation review | `ADDRESSED_PROPOSED` |
| State propagation | R2/read-back/disposition/Receipt exact equality | equality review | `PASS_PROPOSED` |
| identity DAG | finite, acyclic, forward, no Receipt predecessor | DAG review | `PASS_PROPOSED` |
| authority DAG | external -> Human -> Certification -> BEGIN -> coordinator -> effect | authority review | `PASS_PROPOSED` |
| G77-43 B03 | unchanged dual-version BEGIN model | concurrency review | `RESOLVED_AT_PROPOSAL_LEVEL` |
| crash boundaries | predecessor or complete successor | crash review | `PASS_PROPOSED` |
| identical retry | same phase returns same bytes | idempotency review | `PASS_PROPOSED` |
| capability reachability | same direct root paths; founding authority alone terminal | reuse review | `PASS_PROPOSED` |
| topology | 1 -> 1 paths; 0 -> 0 parallel; added counts zero | count review | `PASS_PROPOSED` |
| Minimum Change test | reuse first; three exact additive bindings only | scope review | `PASS` |
| external prerequisites | absent and eligibility false | evidence review | `EXTERNAL_PREREQUISITE_NOT_MODEL_DEFECT` |
| relevant unchanged G69/G70 tests | 326 focused tests | test execution | `PASS` |
| balanced Markdown fences | even fence-token count | static validation | `PASS` |
| trailing whitespace | zero lines | static validation | `PASS` |
| exactly one G77-46 artifact | one exact path | mutation review | `PASS` |
| runtime/test/config changes | none | mutation review | `PASS` |

# 5. Repository Mutation Summary

Modified files:

- added
  `docs/governance/G77_46_EXTERNAL_CONSTITUENT_ONE_SHOT_FOUNDING_AUTHORITY_MODEL_PROPOSAL_REVISION_4_V1.md`
  as the sole G77-46 artifact.

No existing file changed. G77-36 through G77-45 remain byte-identical.

Validation performed:

- 326 focused G69/G70 tests passed;
- G48 heading and required Code Evidence subsection counts passed;
- Markdown fence balance and trailing-whitespace checks passed; and
- `git diff --check` passed.

No API, runtime, schema implementation, validator, test, configuration,
credential, provider, route, pointer, root, token, Human Act, Instrument,
Certification, Ratification, publication, adoption, activation, O01, CDP,
deployment, persistence, production, or external evidence instance changed or
was created.

Boundary preservation:

- this artifact is a proposal only;
- G77-45 and every predecessor remain immutable;
- actual external authority/evidence remains absent;
- G77-38 remains immutably frozen and directly reused;
- ordinary G70 CAP remains the sole normal amendment lifecycle;
- Replay remains read-only and CRO passive; and
- production topology remains one path with zero parallel paths.

Unrelated pre-existing changes:

- None observed. The worktree was clean at proposal start.

# 6. Certification Verdict

G77_CANDIDATE_H_FOUNDING_MODEL_PROPOSAL_REVISION_4_ESTABLISHED
