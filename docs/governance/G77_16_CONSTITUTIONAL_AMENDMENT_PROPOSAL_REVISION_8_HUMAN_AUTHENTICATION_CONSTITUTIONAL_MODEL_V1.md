# 1. Implementation Summary

Generation: G77-16

Report and proposal identity:
`G77_16_CONSTITUTIONAL_AMENDMENT_PROPOSAL_REVISION_8_HUMAN_AUTHENTICATION_CONSTITUTIONAL_MODEL_V1`

Proposal revision: `8`

Proposal status: `PROPOSAL_ONLY_UNASSESSED`

Amendment kind: `ADDITION`

Constitutional baseline: authenticated G0 through G77-15. G77-14 is immutable
Proposal Revision 7. G77-15 is its sole authoritative G70-03 Constitutional
Impact Assessment and classifies Revision 7 as
`UNRESOLVED_CONSTITUTIONAL_IMPACT`. Every predecessor remains closed and
unchanged.

Authenticated repository identity:

- Commit: `d40209e00a9eb984bfacd67d6ae9642f834fccc3`
- Tree: `3ebff21353a519bced939eb82d6c1eed4e853ac5`
- Subject: `G77-15: assess human authentication CAP proposal revision 7`
- Immediate parent: `2f4984e27fe2fccb4e4b68a261c18b42dc400aea`
- Revision-start worktree state: clean
- Authenticated G77-14 SHA-256:
  `927fcd2f75a76986544e8d489dc7b45dc36e2824556d5461b631ee37a5117a60`
- Authenticated G77-15 SHA-256:
  `e7376c79ec85d403029596d42e5f93ca3d1eaa1197e16d273b6770faf5e1ee29`

Revision predecessor binding:

| Field | Exact binding |
|---|---|
| previous proposal identity | `G77_14_CONSTITUTIONAL_AMENDMENT_PROPOSAL_REVISION_7_HUMAN_AUTHENTICATION_CONSTITUTIONAL_MODEL_V1` |
| previous proposal revision | `7` |
| previous proposal digest | `sha256:927fcd2f75a76986544e8d489dc7b45dc36e2824556d5461b631ee37a5117a60` |
| previous proposal status | `PROPOSAL_ONLY_UNASSESSED` |
| authoritative assessment identity | `G77_15_CONSTITUTIONAL_IMPACT_ASSESSMENT_HUMAN_AUTHENTICATION_CONSTITUTIONAL_MODEL_REVISION_7_V1` |
| authoritative assessment digest | `sha256:e7376c79ec85d403029596d42e5f93ca3d1eaa1197e16d273b6770faf5e1ee29` |
| authoritative assessment class | `UNRESOLVED_CONSTITUTIONAL_IMPACT` |

Constitutional Gap identity:
`G77_01_GATE_0B_PRODUCTION_HUMAN_AUTHENTICATION_NORM_ABSENT`

Target Constitutional artifact:
`AI_GOL_CONSTITUTIONAL_CORE_BASELINE_V1_ESTABLISHED`

Target Constitutional version: `V1`

Proposed successor identity:
`AI_GOL_CONSTITUTIONAL_CORE_BASELINE_V1_1_HUMAN_AUTHENTICATION_REVISION_8_PROPOSED`

Proposed successor version:
`V1.1-HUMAN-AUTHENTICATION-R8-PROPOSED`

Proposed Constitutional capability identity:
`CANONICAL_PRODUCTION_HUMAN_IDENTITY_AUTHENTICATION_MODEL_V1`

Proposed Constitutional owner:
`CANONICAL_HUMAN_IDENTITY_AUTHENTICATION_OWNER`

Implementation contracts: G48 Constitutional Evidence Reporting Standard V1;
Constitutional Architecture Specification V1; Canonical Layer Model;
Constitutional Invariants; Governance Enforcement Hierarchy; Governance
Lineage Model; G69 canonical CHE/HIC/Human Authority contracts; G69-18 Replay
and CRO; G69-19 Production Cutover; complete G70 CAP; G72-00 core baseline;
G73-00 Human Constitution; G76-06 Constitutional Artifact Identity Model; the
closed G77 lineage through G77-14; and G77-15 only as the authoritative finding
source for this revision.

Reporting date: 2026-08-08.

Objective:

Create only the immutable Revision 8 successor of G77-14. Resolve only the
three G77-15 findings: direct terminal authorization for REOPEN, one
authoritative FailureEvidence identity per failed quiescence generation, and
a complete ActivationReceipt idempotency/equality/presence contract. Retain
every Revision 7 capability not expressly completed here. Do not implement,
Ratify, certify, publish, activate, deploy, or perform CDP work.

Revision result:

~~~text
terminal LOST or RELEASED State + terminal Receipt
-> directly bound by every REOPEN Transition
-> ordered CHE ledger recovery

one Request/lock/generation
-> one singleton retry identity
-> one ordered failure rule
-> one selected FailureEvidence identity
-> one terminal loss identity

AtomicCommit or fail-closed inactive state
-> exact ActivationReceipt result row
-> deterministic idempotency and read-back equality
~~~

AtomicCommit, native WRITE/QUIESCE serialization, and all retained topology and
authority rules are unchanged:

- one canonical production HIC family;
- one CHE;
- one production owner chain;
- one production path;
- zero parallel production paths;
- Human Authority alone produces Human decisions;
- HIC transports only;
- Replay remains owner-local, deterministic, read-only, and non-authoritative;
- CRO remains passive and non-authoritative; and
- CAP ordering remains proposal -> assessment -> possible Human Ratification
  -> Certification -> publication -> activation -> separately authorized CDP.

This proposal remains:

~~~text
PROPOSAL_ONLY_UNASSESSED
~~~

Every resolution below is a proposal claim. Only a later independent G70-03
Constitutional Impact Assessment may confirm it. No implementation authority
exists.

Added artifact:

- `docs/governance/G77_16_CONSTITUTIONAL_AMENDMENT_PROPOSAL_REVISION_8_HUMAN_AUTHENTICATION_CONSTITUTIONAL_MODEL_V1.md`
  — this proposal-only G48 artifact.

Intentionally unchanged:

- G77-14, G77-15, and every G0 through G77-13 artifact;
- `HumanAuthenticationCutoverQuiescenceAtomicCommitV1` and every AtomicCommit
  derivation, CAS, crash, conflict, and read-back rule;
- Native Ledger WRITE/QUIESCE CurrentPointer, head, State, CAS, generation,
  conflict, retry, crash, acknowledgement, and census contracts;
- active Constitution, CAP/CDP state, Human Authority, HIC, CHE, Replay, CRO,
  Production Cutover topology, release, deployment, routing, workflow, and
  runtime behavior; and
- all code, tests, schemas, credentials, sessions, providers, configuration,
  persistence, and runtime state.

## G77-15 Finding Resolution Matrix

| G77-15 blocking finding | Revision 8 proposed closure | Proposal claim |
|---|---|---|
| REOPEN lacks direct terminal authorization | every REOPEN Transition directly binds the exact terminal State/Receipt/status; WRITE/QUIESCE rows require canonical null | `ADDRESSED` |
| failure/retry identity is non-unique | one generation-derived singleton retry identity, one one-shot selection slot, canonical expiry observation, finite rule codes, and exact precedence | `ADDRESSED` |
| ActivationReceipt is not closed | deterministic idempotency formulas, complete AtomicCommit equality rules, and exact three-result presence/nullability matrix | `ADDRESSED` |

No G77-15 finding is silently repaired outside this artifact. No unrelated
Revision 7 capability is redesigned.

## Identity DAG Changes

Revision 8 adds only these finalized-predecessor edges:

~~~text
terminal QuiescenceState + terminal QuiescenceReceipt
-> REOPEN SerializationTransition
-> OPEN SerializationState
-> CurrentPointer CAS
-> SerializationReceipt

Request/lock/generation + canonical failure selection facts
-> FailureEvidence
-> FailureSelectionState CAS
-> LOSS TerminalTransition
-> LOST QuiescenceState
-> terminal QuiescenceReceipt

AtomicCommit + committed State read-backs
-> ACTIVATED or ALREADY_ACTIVE_IDENTICAL ActivationReceipt

inactive Cutover State + LOST Quiescence State read-backs
-> PRODUCTION_INACTIVE ActivationReceipt
~~~

The terminal State and Receipt already exist before REOPEN. FailureEvidence is
finalized before its selection State; the terminal Transition binds selected
evidence only. AtomicCommit remains earlier than either successful
ActivationReceipt. No predecessor binds its successor, no Transition binds a
later Receipt, and no new identity cycle exists.

## REOPEN Authorization Model

### Complete replacement Transition schema

Revision 8 completely replaces
`HumanAuthenticationNativeLedgerSerializationTransitionV1` with the Revision 7
closed schema plus the terminal authorization fields shown here in full:

~~~text
artifact_type
artifact_version
serialization_transition_identity
serialization_transition_digest
transition_kind
source_head_role
native_contract_identity
native_contract_version
predecessor_current_pointer_identity
predecessor_current_pointer_digest
predecessor_serialization_state_identity
predecessor_serialization_state_digest
predecessor_serialization_generation
predecessor_native_head_identity
predecessor_native_head_digest
predecessor_native_head_generation
reserved_serialization_generation
reserved_native_head_generation
committed_native_record_identity
committed_native_record_digest
quiescence_request_identity
quiescence_request_digest
quiescence_lock_identity
acquisition_generation
terminal_quiescence_state_identity
terminal_quiescence_state_digest
terminal_quiescence_receipt_identity
terminal_quiescence_receipt_digest
terminal_status
predecessor_recovery_receipt_identity
predecessor_recovery_receipt_digest
operation_idempotency_identity
cas_identity
effective_at
producing_owner = CANONICAL_HUMAN_ENTRY_OWNER
metadata = {}
~~~

Presence is exact:

| Transition kind | Request/lock/generation | Terminal State/Receipt/status | Prior recovery Receipt |
|---|---|---|---|
| `COMMIT_NATIVE_WRITE` | all canonical null | all canonical null | canonical null |
| `QUIESCE_NATIVE_LEDGER` | exact active Request/lock/generation | all canonical null | canonical null |
| `REOPEN_NATIVE_LEDGER` role 1 | exact terminal Request/lock/generation | all exact; status `LOST` or `RELEASED` | canonical null |
| `REOPEN_NATIVE_LEDGER` role 2 | exact terminal Request/lock/generation | all exact; status `LOST` or `RELEASED` | exact role-1 Receipt |
| `REOPEN_NATIVE_LEDGER` role 3 | exact terminal Request/lock/generation | all exact; status `LOST` or `RELEASED` | exact role-2 Receipt |

For every REOPEN, the terminal State must:

- have `current_status` exactly equal to `terminal_status`;
- be `LOST` or `RELEASED`, never REQUESTED or ACQUIRED;
- bind the same Request pair, lock identity, acquisition generation, and exact
  deployment/runtime/workspace scopes as the Transition;
- bind a finalized terminal Transition; and
- be the exact current quiescence state read back by its terminal Receipt.

The terminal Receipt must have `receipt_kind = TERMINAL`, result exactly equal
to `terminal_status`, bind the terminal State pair and same Request/lock/
generation, and contain its exact read-back state digest. `RELEASED` additionally
requires the unchanged Revision 7 AtomicCommit/dual-CAS/Cutover bindings;
`LOST` requires the exact selected FailureEvidence/retry binding and canonical-
null AtomicCommit fields.

No narrative or transitive Request reference can substitute for either direct
terminal pair.

### REOPEN identity and authorization

Only the REOPEN row changes the operation idempotency payload:

~~~text
operation_idempotency_identity = native-operation-sha256:SHA256(canonical({
  contract_version, transition_kind = REOPEN_NATIVE_LEDGER, source_head_role,
  deployment_scope_identity, runtime_scope_identity, workspace_scope_identity,
  committed_native_record_identity = null,
  committed_native_record_digest = null,
  quiescence_request_identity, quiescence_request_digest,
  quiescence_lock_identity, acquisition_generation,
  terminal_quiescence_state_identity, terminal_quiescence_state_digest,
  terminal_quiescence_receipt_identity, terminal_quiescence_receipt_digest,
  terminal_status,
  predecessor_recovery_receipt_identity, predecessor_recovery_receipt_digest,
  effective_at
}))
~~~

WRITE and QUIESCE retain their exact Revision 7 idempotency derivations. The
native CAS identity continues to bind this operation identity and the exact
current predecessor pointer/state/head/generations. No native serialization
generation, winner/loser, retry, crash, or read-back rule changes.

Authorization reduction:

~~~text
terminal State/Receipt absent, mismatched, non-current,
or status not in {LOST, RELEASED}
-> no REOPEN Transition
-> no OPEN successor
-> no CurrentPointer CAS
-> writes remain rejected

exact terminal State + exact terminal Receipt + correct recovery predecessor
-> eligible REOPEN CAS for the exact role only
~~~

Roles remain ordered source -> session -> Request/binding. Each later role
binds the preceding role's committed SerializationReceipt. A new acquisition
generation remains ineligible until role 3 is OPEN and its Receipt is read
back. Replay validates the direct terminal pairs, role order, CAS, OPEN State,
and read-back without inference or mutation.

## Failure Identity Derivation

### Singleton retry identity and selection authority

There is exactly one retry namespace per failed generation:

~~~text
singleton_retry_identity = quiescence-failure-singleton-sha256:SHA256(canonical({
  contract_version,
  quiescence_request_identity, quiescence_request_digest,
  quiescence_lock_identity, acquisition_generation,
  deployment_scope_identity, runtime_scope_identity, workspace_scope_identity
}))
~~~

Every FailureEvidence `retry_identity` for that generation must equal this
value. Failure reason, validation subject, code, expected/observed values, and
observation time do not create another retry namespace.

The existing production-status current Request/quiescence coordination record
has one durable failure-selection slot per exact Request/lock/generation. Its
initial value is `EMPTY`. Under the existing `PRODUCTION_STATUS_OWNER` lock,
one compare-and-set may change it exactly once to the identity/digest of one
`HumanAuthenticationCutoverQuiescenceFailureSelectionStateV1`:

~~~text
artifact_type
artifact_version
failure_selection_state_identity
failure_selection_state_digest
quiescence_request_identity
quiescence_request_digest
quiescence_lock_identity
acquisition_generation
predecessor_quiescence_state_identity
predecessor_quiescence_state_digest
predecessor_slot_status = EMPTY
selected_failure_evidence_identity
selected_failure_evidence_digest
singleton_retry_identity
selected_failure_reason
selected_validation_rule_code
deployment_scope_identity
runtime_scope_identity
workspace_scope_identity
selection_cas_identity
selected_at
slot_status = SELECTED
producing_owner = PRODUCTION_STATUS_OWNER
metadata = {}
~~~

For loss before acquisition, `predecessor_quiescence_state` equals the
Request's exact prior terminal State or is canonical null for generation 1.
For loss after acquisition, it equals the exact current ACQUIRED State.

~~~text
selection_cas_identity = quiescence-failure-selection-cas-sha256:SHA256(canonical({
  contract_version,
  quiescence_request_identity, quiescence_request_digest,
  quiescence_lock_identity, acquisition_generation,
  predecessor_quiescence_state_identity,
  predecessor_quiescence_state_digest,
  predecessor_slot_status = EMPTY,
  selected_failure_evidence_identity, selected_failure_evidence_digest,
  singleton_retry_identity, selected_failure_reason,
  selected_validation_rule_code,
  deployment_scope_identity, runtime_scope_identity, workspace_scope_identity,
  selected_at
}))
~~~

The CAS compares the exact EMPTY slot and the current Request/quiescence State
pair. In one atomic package it persists the already finalized selected
FailureEvidence, persists the derived SelectionState, and replaces the slot
with the SelectionState identity/digest. A losing candidate is not persisted,
published, returned, referenced, or treated as a Constitutional artifact.
After the CAS, only the selected FailureEvidence identity is authoritative for
the generation. Crash before CAS leaves EMPTY; crash after CAS reads the
selected State and reconstructs the same FailureEvidence/terminal chain. Retry
with the singleton identity returns the selected evidence. Different content
under that identity fails closed.

The terminal LOSS Transition must directly bind the selected FailureEvidence
and its SelectionState pair and must use `singleton_retry_identity`. No
unselected evidence can terminalize the generation.

### Canonical expiry observation

Expiry evidence is exact:

| Current acquisition status at expiry | Failure reason | Validation code | `observed_at` |
|---|---|---|---|
| not ACQUIRED | `REQUEST_EXPIRED_BEFORE_ACQUISITION` | `F001_REQUEST_EXPIRED_BEFORE_ACQUISITION` | exactly Request `expires_at` |
| ACQUIRED | `ACQUIRED_LEASE_EXPIRED_BEFORE_DUAL_COMMIT` | `F002_ACQUIRED_LEASE_EXPIRED_BEFORE_DUAL_COMMIT` | exactly Request/State `expires_at` |

For both rows, validation subject type/version/identity/digest and expected/
observed value digests are canonical null. Selection may be persisted after
expiry, but FailureEvidence `observed_at` remains exactly `expires_at`;
SelectionState `selected_at` records the later CAS time separately and does not
participate in FailureEvidence or terminal idempotency.

### Finite validation-rule vocabulary

The complete non-expiry vocabulary, reason mapping, and precedence are:

| Rank | `validation_rule_code` | Required `failure_reason` |
|---:|---|---|
| 003 | `F003_ACK_ROLE_MISMATCH` | `ACKNOWLEDGEMENT_CHAIN_INVALID` |
| 004 | `F004_ACK_SEQUENCE_MISMATCH` | `ACKNOWLEDGEMENT_CHAIN_INVALID` |
| 005 | `F005_ACK_OWNER_MISMATCH` | `ACKNOWLEDGEMENT_CHAIN_INVALID` |
| 006 | `F006_ACK_PREDECESSOR_MISMATCH` | `ACKNOWLEDGEMENT_CHAIN_INVALID` |
| 007 | `F007_ACK_SCOPE_MISMATCH` | `ACKNOWLEDGEMENT_CHAIN_INVALID` |
| 008 | `F008_ACK_GENERATION_MISMATCH` | `ACKNOWLEDGEMENT_CHAIN_INVALID` |
| 009 | `F009_ACK_EXPIRY_MISMATCH` | `ACKNOWLEDGEMENT_CHAIN_INVALID` |
| 010 | `F010_NATIVE_CURRENT_POINTER_MISMATCH` | `NATIVE_SERIALIZATION_READ_BACK_INVALID` |
| 011 | `F011_NATIVE_SERIALIZATION_STATE_MISMATCH` | `NATIVE_SERIALIZATION_READ_BACK_INVALID` |
| 012 | `F012_NATIVE_HEAD_MISMATCH` | `NATIVE_SERIALIZATION_READ_BACK_INVALID` |
| 013 | `F013_NATIVE_READ_BACK_DIGEST_MISMATCH` | `NATIVE_SERIALIZATION_READ_BACK_INVALID` |
| 014 | `F014_NATIVE_CENSUS_HEAD_MISMATCH` | `NATIVE_CENSUS_VALIDATION_FAILED` |
| 015 | `F015_NATIVE_CENSUS_TUPLE_MISMATCH` | `NATIVE_CENSUS_VALIDATION_FAILED` |
| 016 | `F016_NATIVE_CENSUS_COUNT_MISMATCH` | `NATIVE_CENSUS_VALIDATION_FAILED` |
| 017 | `F017_NATIVE_CENSUS_DIGEST_MISMATCH` | `NATIVE_CENSUS_VALIDATION_FAILED` |
| 018 | `F018_MIGRATION_FENCE_INVALID` | `MIGRATION_VALIDATION_FAILED` |
| 019 | `F019_MIGRATION_INVENTORY_INVALID` | `MIGRATION_VALIDATION_FAILED` |
| 020 | `F020_MIGRATION_MANIFEST_INVALID` | `MIGRATION_VALIDATION_FAILED` |
| 021 | `F021_MIGRATION_COMPLETENESS_PROOF_INVALID` | `MIGRATION_VALIDATION_FAILED` |
| 022 | `F022_MIGRATION_CLOSURE_INVALID` | `MIGRATION_VALIDATION_FAILED` |
| 023 | `F023_CUTOVER_CERTIFICATION_INVALID` | `CUTOVER_VALIDATION_FAILED` |
| 024 | `F024_CUTOVER_STATE_INVALID` | `CUTOVER_VALIDATION_FAILED` |
| 025 | `F025_DUAL_CAS_CUTOVER_PREDECESSOR_MISMATCH` | `DUAL_CAS_PRECONDITION_FAILED` |
| 026 | `F026_DUAL_CAS_QUIESCENCE_PREDECESSOR_MISMATCH` | `DUAL_CAS_PRECONDITION_FAILED` |

`F001` and `F002` from the expiry table plus `F003` through `F026` are the
entire vocabulary. Unknown codes fail closed.

### Exact selection precedence

Under the one coordinator lock, selection is deterministic:

1. Read the exact current Request/quiescence State and one selection slot.
2. If the slot is SELECTED, return its exact evidence; do not re-evaluate.
3. If the selection linearization time is at or after `expires_at`, choose
   exactly `F001` when no ACQUIRED State exists, otherwise exactly `F002`.
4. Before expiry, validate the exact artifact candidate submitted at the
   current ordered protocol stage. Evaluate codes `F003` through `F026` in
   ascending numeric order and select the first failed code.
5. If more than one candidate artifact exists for that stage, select the
   canonical minimum tuple
   `(artifact_type, artifact_version, artifact_identity, artifact_digest)`
   before applying code order. Other candidates have no generation authority.
6. Derive `failure_reason` only from the one-to-one table row. For non-expiry,
   `observed_at` equals the failure-selection CAS linearization time and
   SelectionState `selected_at`; the one-shot slot makes that value durable.
7. If no code fails before expiry, do not select failure and continue the
   current ordered protocol stage.
8. Otherwise construct FailureEvidence with `singleton_retry_identity`, CAS
   EMPTY -> SELECTED, then derive the LOSS Transition/State/Receipt only from
   the selected pair.

This ordering supplies one reason, one code, one subject, one observation, one
retry identity, and one authoritative FailureEvidence identity for one failed
generation. Replay reads the SelectionState and re-applies the same table; it
does not use a live clock or choose another candidate.

### Revised FailureEvidence and terminal bindings

The Revision 7 FailureEvidence schema is retained with these exact Revision 8
rules:

- `retry_identity` equals `singleton_retry_identity`;
- `validation_rule_code` is mandatory for every reason, including F001/F002;
- expiry subject/value fields are null and `observed_at = expires_at`;
- non-expiry subject/value fields are exact and `observed_at = selected_at`;
- `failure_reason` must equal the code mapping; and
- selected FailureEvidence identity/digest must equal SelectionState.

Revision 8 completely replaces
`HumanAuthenticationCutoverQuiescenceTerminalTransitionV1` with this closed
payload:

~~~text
artifact_type
artifact_version
quiescence_terminal_transition_identity
quiescence_terminal_transition_digest
predecessor_quiescence_state_identity
predecessor_quiescence_state_digest
quiescence_request_identity
quiescence_request_digest
quiescence_lock_identity
acquisition_generation
transition_kind
cutover_state_identity
cutover_state_digest
failure_evidence_artifact_type
failure_evidence_artifact_version
failure_evidence_identity
failure_evidence_digest
failure_selection_state_identity
failure_selection_state_digest
retry_identity
read_back_failure_selection_state_digest
read_back_failure_selection_slot_digest
effective_at
idempotency_identity
producing_owner = PRODUCTION_STATUS_OWNER
metadata = {}
~~~

Failure/selection/retry/read-back fields are mandatory for
`LOSS_BEFORE_ACQUISITION` and `LOSS_AFTER_ACQUISITION`, and canonical null for
`RELEASE_AFTER_CUTOVER`. RELEASE requires the exact Cutover State pair; both
LOSS rows require it null. LOSS idempotency replaces the Revision 7 retry input
with the exact singleton value, and Transition `retry_identity` must equal
SelectionState `singleton_retry_identity`:

~~~text
quiescence_terminal_transition_idempotency =
  quiescence-terminal-transition-sha256:SHA256(canonical({
    contract_version, transition_kind,
    exact predecessor QuiescenceState pair or Request predecessor pair,
    quiescence_request_identity, quiescence_request_digest,
    quiescence_lock_identity, acquisition_generation,
    failure_selection_state_identity, failure_selection_state_digest,
    selected_failure_evidence_identity, selected_failure_evidence_digest,
    singleton_retry_identity
  }))
~~~

The LOST State and terminal Receipt directly repeat the SelectionState pair,
selected FailureEvidence pair, and singleton retry identity. RELEASE remains
unchanged and all selection/failure fields are canonical null.

## ActivationReceipt Completion

### Complete replacement schema

Revision 8 completely replaces
`ConstitutionalProductionCutoverAuthenticationActivationReceiptV2` with this
closed payload:

~~~text
artifact_type
artifact_version
activation_receipt_identity
activation_receipt_digest
predecessor_state_identity
predecessor_state_digest
committed_state_identity
committed_state_digest
cutover_certification_identity
cutover_certification_digest
release_decision_identity
release_decision_digest
quiescence_request_identity
quiescence_request_digest
committed_quiescence_state_identity
committed_quiescence_state_digest
atomic_commit_identity
atomic_commit_digest
dual_cas_identity
idempotency_identity
runtime_scope_identity
read_back_committed_state_digest
read_back_committed_quiescence_state_digest
activation_result
activated_at
producing_owner = PRODUCTION_STATUS_OWNER
metadata = {}
~~~

All identity/digest fields are pairs. Unknown fields or half-present pairs fail
closed.

### Exact presence and nullability matrix

| Field group | `ACTIVATED` | `ALREADY_ACTIVE_IDENTICAL` | `PRODUCTION_INACTIVE` |
|---|---|---|---|
| predecessor Cutover State pair | exact AtomicCommit predecessor | exact AtomicCommit predecessor | exact predecessor of inactive State |
| committed Cutover State pair | exact active AtomicCommit successor | exact active AtomicCommit successor | exact current `PRODUCTION_INACTIVE` V2 State |
| Certification pair | exact and AtomicCommit-equal | exact and AtomicCommit-equal | exact inactive-State Certification |
| Release Decision pair | exact committed-State value | exact committed-State value | exact inactive-State value |
| Quiescence Request pair | exact and AtomicCommit-equal | exact and AtomicCommit-equal | exact terminal LOST generation Request |
| committed Quiescence State pair | exact `RELEASED` AtomicCommit successor | exact `RELEASED` AtomicCommit successor | exact current `LOST` State |
| AtomicCommit pair | exact | exact | both canonical null |
| dual CAS identity | exact AtomicCommit value | exact AtomicCommit value | canonical null |
| idempotency identity | exact successful formula | exact already-active formula | exact inactive formula |
| runtime scope | exact committed-State/Request scope | same | exact inactive-State/Request scope |
| Cutover State read-back digest | exact committed State digest | exact committed State digest | exact inactive State digest |
| quiescence read-back digest | exact RELEASED State digest | exact RELEASED State digest | exact LOST State digest |
| `activated_at` | exact AtomicCommit `committed_at` | exact AtomicCommit `committed_at` | exact inactive State `effective_at` |

No successful row permits a null AtomicCommit field. The inactive row forbids
AtomicCommit/dual-CAS content and requires the fail-closed inactive Cutover
State plus exact LOST quiescence read-back. `PRODUCTION_INACTIVE` never denotes
successful activation.

### Idempotency identities

Successful activation:

~~~text
idempotency_identity = activation-receipt-sha256:SHA256(canonical({
  contract_version, activation_result,
  atomic_commit_identity, atomic_commit_digest,
  atomic_commit.idempotency_identity,
  dual_cas_identity,
  predecessor_state_identity, predecessor_state_digest,
  committed_state_identity, committed_state_digest,
  committed_quiescence_state_identity, committed_quiescence_state_digest,
  cutover_certification_identity, cutover_certification_digest,
  release_decision_identity, release_decision_digest,
  quiescence_request_identity, quiescence_request_digest,
  runtime_scope_identity
}))
~~~

This formula applies to `ACTIVATED` and `ALREADY_ACTIVE_IDENTICAL`; the result
token intentionally distinguishes the two receipt identities. A retry of an
already produced Receipt returns that identical Receipt and result. It does
not convert an `ACTIVATED` Receipt into `ALREADY_ACTIVE_IDENTICAL`. The latter
is produced only when validation begins with both exact successors already
current and no Receipt exists for its own result/idempotency identity.

Fail-closed inactive result:

~~~text
idempotency_identity = activation-inactive-receipt-sha256:SHA256(canonical({
  contract_version, activation_result = PRODUCTION_INACTIVE,
  predecessor_state_identity, predecessor_state_digest,
  committed_state_identity, committed_state_digest,
  cutover_certification_identity, cutover_certification_digest,
  release_decision_identity, release_decision_digest,
  quiescence_request_identity, quiescence_request_digest,
  committed_quiescence_state_identity, committed_quiescence_state_digest,
  atomic_commit_identity = null, atomic_commit_digest = null,
  dual_cas_identity = null, runtime_scope_identity
}))
~~~

Same-idempotency different content fails closed. Crash before the committed
State read-backs produces no Receipt. Crash after read-back reconstructs the
same Receipt from the exact current states and, for successful rows, the exact
AtomicCommit.

### AtomicCommit equality rules

For either successful row, ActivationReceipt must equal the resolved immutable
AtomicCommit field-for-field as follows:

~~~text
Receipt.predecessor_state pair
  == AtomicCommit.predecessor_cutover_state pair

Receipt.committed_state pair
  == AtomicCommit.committed_cutover_state pair

Receipt.committed_quiescence_state pair
  == AtomicCommit.committed_quiescence_state pair

Receipt.cutover_certification pair
  == AtomicCommit.cutover_certification pair

Receipt.quiescence_request pair
  == AtomicCommit.quiescence_request pair

Receipt.dual_cas_identity
  == AtomicCommit.dual_cas_identity

Receipt.runtime_scope_identity
  == AtomicCommit.runtime_scope_identity

Receipt.read_back_committed_state_digest
  == AtomicCommit.read_back_cutover_state_digest

Receipt.read_back_committed_quiescence_state_digest
  == AtomicCommit.read_back_quiescence_state_digest

Receipt.activated_at
  == AtomicCommit.committed_at
~~~

It must also validate AtomicCommit idempotency, both current-pointer read-backs,
both exact successor states, RELEASE Transition, acquisition generation, lock,
and scopes under the unchanged Revision 7 contract. ActivationReceipt cannot
repair or reinterpret AtomicCommit.

For `PRODUCTION_INACTIVE`, AtomicCommit equality is inapplicable because its
fields are required null. Instead, Receipt fields must equal the committed
inactive Cutover State and exact terminal LOST QuiescenceState/Receipt. Replay
selects one matrix row from `activation_result`, recomputes idempotency, checks
all equalities/nulls/read-backs, and returns the recorded result without
inference or live state mutation.

## Complete Revision 8 Dependency Graph

~~~text
unchanged native WRITE/QUIESCE serialization
-> ordered acknowledgements -> ACQUIRED QuiescenceState
-> unchanged census/migration/Certification

success:
  unchanged CutoverState + RELEASE Transition + RELEASED State
  -> unchanged AtomicCommit
  -> exact successful ActivationReceipt row
  -> direct-terminal-bound ordered REOPEN chain

failure:
  one singleton retry identity + ordered rule
  -> selected FailureEvidence + FailureSelectionState
  -> LOSS Transition -> LOST State/Receipt
  -> exact inactive ActivationReceipt row when applicable
  -> direct-terminal-bound ordered REOPEN chain
~~~

Every arrow ends at a successor with direct identity/digest fields. No later
Receipt is hashed by its predecessor. The graph is finite and acyclic.

## Replay, CRO, CAP, and Topology Compatibility

Replay validates the selected failure slot/code/reason, terminal State/Receipt,
REOPEN direct predecessor pairs, recovery order, ActivationReceipt result row,
idempotency, AtomicCommit equality or nullability, and read-backs. Replay does
not use a live clock, select a different failure, acquire a lock, reopen a
ledger, perform CAS, repair evidence, or infer a field.

CRO remains passive and non-authoritative. It may observe finalized non-secret
identities, codes, statuses, results, counts, digests, and times. It cannot
select failure evidence, terminalize, reopen, certify, activate, or mutate.

CAP ordering is unchanged. G77-16 requires an independent G70-03 Impact
Assessment before Human Ratification can be considered. Proposal/report
presence supplies no activation or implementation authority.

Topology remains exactly:

| Invariant | Count/status |
|---|---:|
| canonical production HIC families | 1 |
| Canonical Human Entries | 1 |
| production owner chains | 1 |
| production paths | 1 |
| parallel production paths | 0 |
| HIC semantic authority | none |
| Replay write authority | none |
| CRO control authority | none |

## Reuse Impact Assessment

1. **Which certified Constitutional capabilities are reused?**

   Revision 8 reuses the active Constitution; G48; complete G70 CAP; G76-06
   identity/DAG rules; G69-07/G73 Human Authority; one HIC family; sole CHE and
   structured Request/Response/Continuation, owner transition, correlation,
   idempotency, delivery, and advancement; G69-18 owner-local Replay/passive
   CRO; G69-19 one Cutover owner/state path, lock, atomic replacement, and
   rollback discipline; and all resolved G77 capabilities, including identity,
   refusal, bootstrap, registry/fence/revocation, freshness, native ledger
   serialization, migration, Certification, and AtomicCommit.

2. **Which new capabilities are introduced?**

   Only G77-15 closures: terminal State/Receipt/status fields in REOPEN;
   generation-singleton failure retry/selection, canonical expiry observation,
   finite rule codes, exact precedence, and SelectionState binding; and a
   complete ActivationReceipt idempotency/equality/three-result presence model.
   All are inactive proposal-only capabilities.

3. **Does any certified capability become unreachable?**

   No active capability changes while this proposal is inactive. Under the
   proposed successor, semantic, Governance, Authorization, Worker, Replay,
   CRO, release, rollback, and Cutover capabilities remain reachable through
   the same owner chain after authentication. REOPEN is intentionally
   unreachable until terminal LOST or RELEASED evidence exists; this preserves
   the certified freeze boundary and removes no downstream capability.

4. **Does the proposal create a parallel production path?**

   No. Failure selection, direct REOPEN authorization, and ActivationReceipt
   validation are internal evidence/state contracts of existing owners. They
   create no HIC, CHE, ingress, semantic route, execution caller, Cutover path,
   Replay writer, or CRO controller.

5. **Does it decrease or increase the number of production paths?**

   Neither. The number remains exactly one production path and zero parallel
   production paths.

# 2. Code Evidence

## Public API

No runtime API is added or modified. The artifact names, selection slot, CAS,
rule codes, and responsibility labels are Constitutional proposal contracts,
not implemented functions, models, schemas, persistence primitives, stores,
transactions, routes, commands, or deployment changes.

## Orchestration Entry Point

The only Human production entry remains:

~~~text
Human -> permitted HIC profile -> sole CHE -> exact eligible owner
-> sole CHE Response/Continuation -> same HIC
~~~

REOPEN authorization stays inside the existing CHE owner. Failure selection
and ActivationReceipt remain production-status evidence/state operations. None
accepts Human input or creates another route.

## Semantic Reductions

### REOPEN

~~~text
terminal State.status in {LOST, RELEASED}
AND terminal Receipt reads back that exact State
AND Request/lock/generation/scope equal
AND recovery predecessor is exact
-> REOPEN eligible

otherwise -> remain QUIESCENT
~~~

### Failure identity

~~~text
one Request/lock/generation
-> one singleton_retry_identity
-> EMPTY-to-SELECTED CAS once
-> one ordered rule/code/subject
-> one authoritative FailureEvidence
~~~

### ActivationReceipt

~~~text
ACTIVATED or ALREADY_ACTIVE_IDENTICAL
-> AtomicCommit fields exact and equal; no nulls

PRODUCTION_INACTIVE
-> inactive State + LOST State exact;
   AtomicCommit/dual CAS null
~~~

## Public Validators

No validator is implemented. Future separately authorized CDP validators must
reject:

- REOPEN lacking either terminal pair or terminal status;
- REOPEN bound to non-current, REQUESTED, or ACQUIRED quiescence;
- a terminal State/Receipt/Request/lock/generation/scope mismatch;
- a second failure selection for one generation;
- retry identity differing from the singleton derivation;
- expiry `observed_at` differing from `expires_at`;
- an unknown code, wrong reason mapping, or non-minimal failed code;
- unselected FailureEvidence in a LOSS Transition;
- ActivationReceipt idempotency mismatch;
- a successful Receipt differing from AtomicCommit;
- an inactive Receipt containing AtomicCommit/dual-CAS fields;
- a missing required read-back or half-present pair;
- Replay/CRO mutation or authority expansion; and
- topology other than `1 / 1 / 1 / 1 / 0`.

## Canonical Data Models

| Proposed model | Exact owner | Purpose |
|---|---|---|
| REOPEN SerializationTransition | CHE owner | direct terminal authorization before OPEN |
| FailureSelectionState | production-status owner | one selected failure identity per generation |
| FailureEvidence/LOSS chain | production-status owner | canonical code/reason/retry terminalization |
| ActivationReceiptV2 | production-status owner | exact success/inactive Cutover evidence |
| AtomicCommit | production-status owner | unchanged dual-current-pointer proof |
| Replay | owner-local custodian | deterministic read-only reconstruction |
| CRO | passive Observatory | non-secret passive observation |

## Deterministic Algorithms

1. Validate exact type/version/owner/presence and finalized predecessors.
2. For REOPEN, resolve terminal State then terminal Receipt and compare every
   Request/lock/generation/scope/status/read-back field.
3. Derive one generation-only singleton retry identity.
4. Under the coordinator lock, return SELECTED or apply expiry then ascending
   code/canonical-subject precedence.
5. CAS the EMPTY failure slot exactly once and terminalize only selected
   evidence.
6. Select one ActivationReceipt result row.
7. Recompute its exact idempotency and AtomicCommit equalities or inactive
   nullability.
8. Flush/read back committed states before Receipt creation.
9. Replay immutable predecessor/state/Receipt chains without mutation.

## Responsibility Boundaries

| Responsibility | Exact owner | Negative boundary |
|---|---|---|
| issue Human decision | Human Authority | sole Human decision source |
| transport | HIC | no semantic/authentication authority |
| serialize/reopen native ledgers | sole CHE owner | no Human/authentication/Cutover decision |
| select/terminalize failure | production-status owner | no source ownership or Human authority |
| commit Cutover/Receipt | production-status owner | existing one Cutover path only |
| certify Cutover | release/cutover Certification owner | no state mutation |
| reconstruct | owner-local Replay | read-only; no repair/inference |
| observe | CRO | passive; no control/certification |
| assess proposal | later Constitutional Governance | not performed here |
| implement | later authorized CDP | not authorized |

## Repository Evidence

The authenticated G77-14/G77-15 digests, exact G77-15 three-finding set,
G76-06 closed identity rules, G70 CAP ordering, and certified G69 owner/topology
contracts are the evidence basis. No runtime behavior, deployment state,
provider result, or test fixture supplies Constitutional semantics.

# 3. Constitutional Self-Assessment

## Verified as Proposal Structure

- G77-14 and G77-15 are bound by exact immutable identities and digests.
- Every G77-15 finding has one explicit proposed closure.
- Every REOPEN directly binds terminal State, terminal Receipt, and status.
- WRITE and QUIESCE terminal fields are exactly null.
- One generation derives one singleton retry identity.
- Expiry observation is exactly `expires_at`.
- The validation-code vocabulary is finite and precedence is exact.
- One EMPTY-to-SELECTED CAS chooses one authoritative FailureEvidence.
- LOSS artifacts bind SelectionState and selected evidence directly.
- ActivationReceipt has exact idempotency formulas and a three-result presence
  matrix.
- Successful Receipt fields equal AtomicCommit; inactive atomic fields are
  null.
- Identity edges are forward-only and finite.
- AtomicCommit and native WRITE/QUIESCE serialization remain unchanged.
- Human Authority, HIC, CHE, Replay, CRO, CAP order, and `1 / 1 / 1 / 1 / 0`
  topology are preserved.
- No runtime, Ratification, Certification, publication, activation, deployment,
  or CDP action occurs.

## Not Verified

- No independent G70-03 assessment of Revision 8 has occurred.
- No Human Ratification, Certification, publication, or activation exists.
- No schema, selection slot, CAS, validator, Replay reader, persistence,
  recovery, or Receipt is implemented.
- No concurrency, crash, expiry, migration, rollback, deployment, security, or
  production behavior is tested.
- Existing enforcement, hook, privacy, custody, deployment, and external-system
  limitations remain visible and unchanged.
- Proposal claims cannot serve as production evidence or implementation
  authority.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| G48 structure | six top-level sections and evidence subsections | heading review | `PASS` |
| authenticated lineage | commit/tree/parent and exact predecessor digests | Git/SHA-256 review | `PASS` |
| immutable predecessors | no G77-14/G77-15 mutation | repository review | `PASS` |
| finding scope | exact three-row G77-15 matrix | scope review | `PASS` |
| REOPEN terminal State pair | mandatory direct fields | schema review | `PASS` |
| REOPEN terminal Receipt pair | mandatory direct fields | schema review | `PASS` |
| REOPEN terminal status | exact LOST/RELEASED | presence review | `PASS` |
| premature REOPEN | absent/mismatched/nonterminal evidence rejects | lifecycle review | `PASS` |
| recovery order | exact roles 1-3 and prior Receipts | lifecycle review | `PASS` |
| singleton retry identity | generation-only canonical hash | derivation review | `PASS` |
| canonical expiry observation | observed_at equals expires_at | time review | `PASS` |
| finite rule vocabulary | F001-F026 only | enumeration review | `PASS` |
| code/reason mapping | one exact table row | deterministic review | `PASS` |
| rule precedence | expiry then ascending code/canonical subject | reduction review | `PASS` |
| one failure identity | EMPTY-to-SELECTED CAS and non-authoritative losers | concurrency review | `PASS` |
| failure retry/crash | selected slot reconstructs identical evidence | recovery review | `PASS` |
| LOSS bindings | SelectionState/evidence/singleton direct | DAG review | `PASS` |
| ActivationReceipt schema | complete exact fields | schema review | `PASS` |
| success presence | AtomicCommit/quiescence/read-backs exact | matrix review | `PASS` |
| inactive presence | inactive/LOST exact; atomic fields null | matrix review | `PASS` |
| ActivationReceipt idempotency | exact success/inactive formulas | derivation review | `PASS` |
| AtomicCommit equality | ten exact successful equalities | comparison review | `PASS` |
| Replay reconstruction | result-row reduction without inference | Replay review | `PASS` |
| AtomicCommit unchanged | no schema/derivation/CAS change | scope review | `PASS` |
| native serialization unchanged | only REOPEN authorization fields added | scope review | `PASS` |
| identity DAG | transition/state/Receipt order; no cycle | G76-06 review | `PASS` |
| Human Authority | sole Human decision source | boundary review | `PASS` |
| Replay/CRO | read-only/passive | boundary review | `PASS` |
| CAP ordering | independent assessment mandatory next | lineage review | `PASS` |
| production topology | 1 HIC / 1 CHE / 1 chain / 1 path / 0 parallel | path review | `PASS` |
| Reuse Impact Assessment | all five questions answered | completeness review | `PASS` |
| runtime implementation | proposal-only generation | scope review | `NOT_APPLICABLE` |
| independent impact confirmation | later G70-03 required | governance review | `NOT_REACHED` |

# 5. Repository Mutation Summary

Modified files:

- added
  `docs/governance/G77_16_CONSTITUTIONAL_AMENDMENT_PROPOSAL_REVISION_8_HUMAN_AUTHENTICATION_CONSTITUTIONAL_MODEL_V1.md`
  as the sole G77-16 artifact.

No existing file changed. G77-14 and G77-15 remain byte-identical.

Unchanged subsystems:

- Constitution, prior CAP proposals/assessments, CDP, Human Authority, HIC,
  CHE runtime, Governance, Replay, CRO, Production Cutover runtime, production
  status, release, Conversation, Platform, Authorization, Workers, routing,
  workflow, deployment, configuration, schemas, credentials, providers,
  persistence, and tests; and
- all G0 through G77-15 artifacts.

API compatibility:

- no API, model, validator, serializer, command, route, profile, owner,
  workflow, deployment, or runtime contract is activated or implemented.

Boundary preservation:

- this artifact is an unassessed proposal only;
- it grants no Human, implementation, Ratification, Certification,
  publication, activation, deployment, or execution authority;
- Replay remains read-only and CRO remains passive;
- AtomicCommit and native WRITE/QUIESCE serialization remain unchanged; and
- production topology remains one path with zero parallel paths.

Unrelated pre-existing changes:

- None observed. The worktree was clean at proposal start.

# 6. Certification Verdict

CONSTITUTIONAL_HUMAN_AUTHENTICATION_CAP_PROPOSAL_REVISION_8_ESTABLISHED
