# 1. Implementation Summary

Generation: G77-40

Report and proposal identity:
`G77_40_EXTERNAL_CONSTITUENT_ONE_SHOT_FOUNDING_AUTHORITY_MODEL_PROPOSAL_V1`

Proposal status: `PROPOSAL_ONLY_UNASSESSED`

Candidate: `H`

Candidate class:
`EXTERNAL_HUMAN_DECIDED_EXACT_TARGET_PROOF_BOUND_ONE_SHOT_CONSTITUENT_FOUNDING_AUTHORITY_WITH_PERMANENT_DORMANCY`

Amendment kind: `FOUNDING_MODEL_PROPOSAL_ONLY`

Constitutional baseline: authenticated G0 through committed G77-39. G77-36
is the immutable converged operational MetaRepair proposal, G77-37 is its
independent design-level impact confirmation, G77-38 freezes that operational
design, and G77-39 establishes that no admissible internal initial-adoption
path exists and selects Candidate H as the preferred minimal external model.

Authenticated repository identity:

- Commit: `fe4a34a54d10fe23bd8b737105a87ac17eb1b369`
- Tree: `25022b6f8b88332dce40722f21a9576a6c8909b5`
- Subject: `G77-39: establish external constituent founding requirement`
- Immediate parent: `b1181dd98821ae0194ea7f4558ffb5e55f118f3d`
- Proposal-start worktree state: clean
- Authenticated G77-36 SHA-256:
  `5533ec8e597e0767f869daec8118ee3dec6c77af56b4d7c71bdc2d44cfdaba4a`
- Authenticated G77-37 SHA-256:
  `4ecd74ca986e56490bd72bd26d28ef01777be5780fe8596fcae992fbc6d59add`
- Authenticated G77-38 SHA-256:
  `b80ca33767deab09c3875f302ccee212a539291a12f454ef67e1bbca07133363`
- Authenticated G77-39 SHA-256:
  `71aafd80edfc4711adb037f00e265465ae525e9267ddafb3855890353f760592`

Primary predecessor binding:

| Field | Exact authenticated value |
|---|---|
| predecessor | `G77_39_INITIAL_ADOPTION_FOUNDING_AUTHORITY_CONSTITUTIONAL_SOLUTION_SPACE_AND_REACHABILITY_AUDIT_REPORT_V1` |
| predecessor digest | `sha256:71aafd80edfc4711adb037f00e265465ae525e9267ddafb3855890353f760592` |
| operational MetaRepair design | `CONSTITUTIONALLY_CONVERGED_AT_DESIGN_LEVEL` |
| internal adoption path | `NONE_ADMISSIBLE` |
| solution space | `EXTERNAL_CONSTITUENT_FOUNDING_MODEL_REQUIRED` |
| current authority evidence | `INITIAL_ADOPTION_AUTHORITY_EVIDENCE_ABSENT` |
| preferred minimal candidate | `H` |
| predecessor verdict | `G77_INITIAL_ADOPTION_EXTERNAL_CONSTITUENT_FOUNDING_MODEL_REQUIRED` |

Reporting date: 2026-08-09.

Objective:

Propose only the minimum closed Constitutional contract by which a genuinely
prior external constituent source, if independently evidenced in the future,
could issue one exact founding instrument under which one authenticated Human
decision can authorize exactly one first-adoption effect for the frozen
G77-36 through G77-39 target. The mechanism permanently loses reachability
after success, refusal, invalidation, expiry, or target staleness.

The model is:

~~~text
independently prior external source evidence
+ exact one-shot founding instrument
+ exact Human constituent decision
+ complete machine-verifiable proof set
-> one exact predecessor-root CAS
-> one exact successor Constitutional root
-> terminal Receipt
-> founding_authority_reachable = FALSE permanently
~~~

This artifact distinguishes two facts that must not be collapsed:

| Boundary | G77-40 result |
|---|---|
| model for recognizing a valid external constituent source | proposed |
| actual external constituent source identity/evidence | absent and not fabricated |
| actual founding instrument | absent |
| actual Human constituent decision | absent |
| adoption authority | absent |
| adoption performed | false |

Candidate H is not MetaRepair Revision 6, a second CAP, an ordinary or
emergency amendment mechanism, a reusable Human bypass, a persistent
constituent authority, a new root, or a production execution path. Every
contract below is inactive proposal content pending an independent impact
assessment and separately lawful future stages.

Added artifact:

- `docs/governance/G77_40_EXTERNAL_CONSTITUENT_ONE_SHOT_FOUNDING_AUTHORITY_MODEL_PROPOSAL_V1.md`
  — this proposal-only G48 artifact.

Intentionally unchanged:

- G77-36, G77-37, G77-38, G77-39, and every predecessor artifact;
- token allocation, Failure Census, proof freshness, root-contained SlotMap,
  ValueDomain/minimum, MetaRepair root CAS, Replay, CRO, and production
  topology frozen by G77-38;
- active Constitution, ordinary G70 CAP, Human Authority, HIC, CHE,
  Governance, Certification, current roots/pointers, release, runtime,
  deployment, persistence, and configuration; and
- all code, schemas, tests, credentials, sessions, Human Acts, external
  evidence, runtime state, and production behavior.

## Predecessor Authentication and Freeze Preservation

The four required artifacts match their exact committed digests. Their
lineage is forward and continuous:

~~~text
G77-36 converged operational proposal
-> G77-37 independent impact confirmation
-> G77-38 operational convergence and freeze
-> G77-39 external founding requirement and Candidate H selection
-> G77-40 Candidate H model proposal only
~~~

G77-40 changes none of the G77-38 frozen operational contracts. Candidate H
has exactly one purpose: install the already-converged initial MetaRepair
design as exact Constitutional content. It cannot allocate a token, select a
failure, issue a repair proof, choose a minimum, run MetaRepair, change Replay
or CRO, or create an additional production or amendment path.

## External Constituent Source Recognition Model

### Evidence requirements

`ExternalConstituentAuthoritySourceEvidenceV1` is the proposed closed evidence
class for a future concrete source. G77-40 creates the class only; it creates
no instance. A valid instance must contain:

~~~text
artifact_type
artifact_version
external_source_identity
external_source_identity_scheme
external_source_authority_provenance_identity
external_source_authority_provenance_digest
independently_prior_authority_root_identity
independently_prior_authority_root_digest
source_custody_evidence_identity
source_custody_evidence_digest
source_authentication_evidence_identity
source_authentication_evidence_digest
source_signature_scheme
source_signature
authority_scope_identity
authority_scope_digest
authority_status_epoch
authority_not_before
authority_expires_at
authority_revocation_status
authority_uniqueness_commitment_identity
authority_uniqueness_commitment_digest
source_one_shot_disposition_domain_identity
source_one_shot_disposition_domain_digest
issued_at
metadata = {}
~~~

The evidence is recognizable only when all of these predicates are true:

1. the source and authority provenance exist independently before G77-40,
   the proposed target, and the successor Constitution;
2. neither the current Constitution, G77 lineage, repository possession,
   Governance, Certification, nor the proposed successor creates or confirms
   the source's authority;
3. custody, authentication, signature, provenance root, and source identity
   validate under the independently prior source's own evidence system;
4. authority scope is exactly the one Candidate H first-adoption target and
   contains no wildcard, equivalence, substitution, rebase, future amendment,
   production, deployment, or runtime power;
5. the source supplies a verifiable singleton commitment proving that exactly
   one source and one instrument may be eligible for the target;
6. the independently prior source has one authoritative, linearizable,
   irreversible one-shot disposition domain able to bind exactly one Human
   decision to the Instrument without deriving authority from the target;
7. status is active and not revoked at the canonical source-issued evaluation
   instant, which must fall in the closed interval from `authority_not_before`
   through `authority_expires_at` when those bounds exist; and
8. unknown fields, half-present pairs, unverifiable clocks, ambient consent,
   administrative control, inferred authority, or multiple eligible sources
   fail closed.

If the independently prior evidence system has no temporal model, the three
temporal fields must be canonical null and the source must instead provide an
immutable, signed, non-revoked status epoch. A machine custodian cannot choose
which freshness model applies. The source evidence schema and founding
instrument must select exactly one row.

`ExternalConstituentAuthorityRecognitionProofV1` binds the complete source
evidence, validation schema, provenance-chain root, custody/signature results,
status/freshness result, singleton-source count exactly one, and result
`INDEPENDENTLY_PRIOR_EXACT_SCOPE_SOURCE_RECOGNIZED`. Its validator may prove
predicates but gains no founding or Human decision authority.

### Evidence absence

No concrete source identity, provenance, custody proof, signature, uniqueness
commitment, recognition proof, or external instrument is present in the
authenticated repository state. Therefore the current reduction is exactly:

~~~text
recognition model = SPECIFIED_AS_PROPOSAL
actual recognized external source = ABSENT
founding eligibility = FALSE
adoption transition = FORBIDDEN
~~~

## Exact Target Contract

`ConstitutionalMetaRepairInitialAdoptionTargetV1` binds exactly:

~~~text
artifact_type
artifact_version
founding_target_identity
founding_target_digest
g77_36_identity
g77_36_digest
g77_37_identity
g77_37_digest
g77_38_identity
g77_38_digest
g77_39_identity
g77_39_digest
predecessor_constitutional_root_pointer_identity
predecessor_constitutional_root_pointer_digest
predecessor_constitutional_root_identity
predecessor_constitutional_root_digest
predecessor_root_generation
predecessor_constitutional_state_identity
predecessor_constitutional_state_digest
predecessor_active_constitution_identity
predecessor_active_constitution_digest
normative_successor_payload_identity
normative_successor_payload_digest
founding_scope_identity
founding_scope_digest
required_successor_meta_repair_status
required_successor_cap_status
required_production_topology
metadata = {}
~~~

The four lineage pairs are fixed to the authenticated identities and digests
above. The root/pointer/generation/State values must equal the exact authoritative
Constitutional root when a future instrument is issued and again when the
effect attempts to linearize. The target becomes terminally stale if that
root changes; no rebasing or replacement target is permitted.

The `normative_successor_payload` is derived before the founding instrument
from only the exact predecessor Constitution, the four G77 pairs, the complete
frozen G77-36 operational content, the fixed incorporation rule, ordinary CAP
primacy, MetaRepair's frozen exceptional scope, and topology `1 / 1 / 0`. It
contains no external source, instrument, Human decision, proof, transition,
successor-root, CAS, marker, read-back, Receipt, or dormancy identity. This
separation allows the exact target content to be fixed without making it hash
an artifact that depends on the target.

The later successor root contains the exact normative payload plus finalized
founding dormancy evidence. Equality is byte-exact. “Equivalent,” compatible,
semantically similar, wildcard, partial, future, substituted, or reformulated
successors are ineligible.

~~~text
founding_target_identity = founding-target-v1-sha256:SHA256(canonical({
  contract_version,
  exact G77-36, G77-37, G77-38, and G77-39 pairs,
  exact predecessor root pointer/root/generation/State/active Constitution pairs,
  normative_successor_payload_identity,
  normative_successor_payload_digest,
  founding_scope_identity, founding_scope_digest,
  required_successor_meta_repair_status,
  required_successor_cap_status,
  required_production_topology
}))
~~~

## Founding Instrument and Human Decision Boundary

`ExternalConstituentOneShotFoundingInstrumentV1` is an independently issued,
source-signed exact effect assignment. It binds:

- SourceEvidence and RecognitionProof pairs;
- the exact Target pair;
- the exact finalized G77-40 proposal pair and a later independently resolved
  G77-40 impact-assessment pair;
- one `instrument_sequence = 1` and `maximum_successful_effects = 1`;
- `reissuance_permitted = false`, `target_substitution_permitted = false`, and
  `reset_permitted = false`;
- the exact Human decision receiver and closed choice vocabulary;
- `CONSTITUTIONAL_CERTIFICATION_OWNER` as predicate-verification custodian
  only;
- `CONSTITUTIONAL_ROOT_SERIALIZATION_CUSTODIAN` as the exact mutation and
  publication/activation custodian only;
- the existing authoritative Constitutional root serialization domain;
- the exact terminal-state table and dormancy requirement; and
- source signature, issue/status epoch, temporal row, and source-defined
  revocation check.

The instrument supplies the proposed external founding effect authority. The
named internal owners supply technical custody only. Neither owner may choose
the target, Human result, predecessor, successor, scope, or effect.

Human remains the sole decision source. The exact proposed decision is
`ExternalConstituentHumanFirstAdoptionDecisionV1`, derived from one
authenticated `CanonicalHumanAuthorityActV1` delivered by the existing HIC
and sole CHE. Its closed payload binds the SourceEvidence, RecognitionProof,
Instrument, Target, Human actor, CHE delivery/continuity evidence, and exactly
one decision:

| Human decision | Effect |
|---|---|
| `ADOPT_EXACT_TARGET` | permits proof evaluation and, if every predicate passes, one exact root CAS |
| `REFUSE_EXACT_TARGET` | forbids adoption and permanently consumes the instrument into `REFUSED_DORMANT` |

G69-07 `APPROVAL` or `REFUSAL` may carry the closed act only because the
external instrument preassigns the exact receiver and semantics. A generic
approval, statement, repository action, administrator action, Governance
assertion, Certification result, HIC event, or CHE delivery has no founding
effect. There is no automatic adoption, inferred consent, second decision,
machine decision, or direct Human root mutation.

Before either decision has model authority, the independently prior source's
one-shot disposition domain must atomically record an
`ExternalConstituentOneShotInstrumentDispositionEvidenceV1`. It binds the
SourceEvidence, Instrument, Target, exact Human Act/Decision, prior disposition
`UNUSED`, and exactly one terminal disposition:

| Disposition | Exact consequence |
|---|---|
| `ADOPTION_DECISION_BOUND` | the external slot is permanently consumed and may authorize retries of only that exact adoption effect |
| `REFUSAL_DECISION_BOUND` | the external slot is permanently consumed and no adoption effect is eligible |

The disposition evidence includes the source-domain predecessor/current
state pairs, source CAS or equivalent linearization evidence, read-back,
signature, and `reissue_permitted = false`. A losing Human decision is not
recognized, published, or usable. Same decision and content returns identical
evidence; different content under the consumed slot fails closed. The source
records the Human's decision; it does not choose or reinterpret it. A source
unable to provide this irreversible singleton record is not recognizable for
Candidate H.

## Exact Proof Set and Verification Contract

`ExternalConstituentFoundingEligibilityProofSetV1` is a complete immutable
proof set derived from already finalized inputs. It binds exact identities and
digests for:

- SourceEvidence and RecognitionProof;
- FoundingInstrument and Target;
- Human Act, CHE delivery, HumanDecision, and exact terminal external
  InstrumentDispositionEvidence;
- the current authoritative root pointer/root/generation and read-back;
- the exact predecessor Constitutional State pair;
- G77-36 through G77-39 and the normative successor payload;
- the exact G77-40 proposal pair and independently resolved impact-assessment
  pair required after this proposal;
- source status, freshness or immutable status epoch, and non-revocation;
- singleton eligible-source count = 1 and eligible-instrument count = 1;
- instrument sequence = 1 and prior-use count = 0;
- exact-target, exact-scope, exact-predecessor, and no-rebase results;
- G77-38 freeze preservation;
- ordinary G70 CAP entry unreachability for this initial adoption;
- no self-authorization, no second CAP, no alternate root, no new current
  pointer/domain, no topology expansion, and no production-path change;
- exact effect/mutation/custody owner assignments; and
- permanent dormancy derivability for success, refusal, invalidation, expiry,
  or stale predecessor.

The candidate universe and predicate vocabulary are closed. Unknown,
omitted, conflicting, half-present, non-current, stale, revoked, duplicated,
or non-verifiable evidence produces no ARMED state.

`ExternalConstituentFoundingEligibilityCertificationV1` may be produced in a
future separately authorized process only when every proof-set predicate is
true. Its sole result is
`EXACT_ONE_SHOT_FOUNDING_EFFECT_ELIGIBLE`. Certification verifies the
instrument's predicates; it neither supplies external authority nor decides,
mutates, publishes, or activates.

No Certification is performed by G77-40.

## One-Shot State Machine

The closed model is:

~~~text
UNAVAILABLE
  -> ARMED
  -> CONSUMING
  -> CONSUMED_DORMANT

UNAVAILABLE or ARMED
  -> REFUSED_DORMANT

UNAVAILABLE or ARMED or CONSUMING-before-root-CAS
  -> INVALIDATED_DORMANT
~~~

| State | Exact meaning | Permitted successor |
|---|---|---|
| `UNAVAILABLE` | no complete recognized source/instrument/Human/proof package | `ARMED`, `REFUSED_DORMANT`, or `INVALIDATED_DORMANT` |
| `ARMED` | exact source, instrument, affirmative Human decision, proof set, and eligibility Certification are complete; no root effect exists | `CONSUMING` or `INVALIDATED_DORMANT` |
| `CONSUMING` | exact immutable Transition and successor candidate are prepared against one predecessor; they remain non-authoritative before CAS | identical retry, `CONSUMED_DORMANT`, or `INVALIDATED_DORMANT` only if CAS has not committed |
| `CONSUMED_DORMANT` | exact successor root is current and terminal Receipt is reconstructable | none |
| `REFUSED_DORMANT` | exact Human refusal is recorded; instrument has zero future authority | none |
| `INVALIDATED_DORMANT` | source/instrument invalid, revoked, expired, duplicated, conflicting, or target predecessor stale before commit | none |

`UNAVAILABLE` is not a mutable current pointer. ARMED and CONSUMING are
immutable evidence projections over the exact instrument and authoritative
root, not new serialization domains. Terminal state is represented by
`ExternalConstituentFoundingDormancyStateV1`. It binds the exact source,
instrument, target, Human decision, prior state, terminal reason/result,
use-count, root-effect count, and these required constants:

~~~text
founding_authority_reachable = false
reset_permitted = false
reissuance_permitted = false
second_human_decision_permitted = false
second_target_permitted = false
ordinary_amendment_authority = false
terminal = true
~~~

For successful adoption, the dormancy State is finalized from the exact
Transition before successor-root preparation, and the successor root embeds
that State pair. It contains no successor-root, CAS, marker, read-back, or
Receipt pair. Once the root CAS wins, the authoritative Constitution itself
therefore records `founding_authority_reachable = false`. No transition exits
a terminal row, and the proposed validator rejects any root or evidence chain
that purports to reset, replace, reissue, or reuse it.

Refusal is a Human outcome, not a failed affirmative attempt. It consumes the
one external disposition slot and permits no second Human decision. The exact
`REFUSAL_DECISION_BOUND` evidence is the authoritative terminal predecessor of
the local `REFUSED_DORMANT` projection; no new internal pointer is required.
Expiry, revocation, conflict, multiple eligible instruments, or predecessor-
root change consumes or has already consumed the unique instrument into
`INVALIDATED_DORMANT`. For an affirmative decision, the external disposition
slot remains consumed even if the local root later becomes stale. Candidate H
supplies no retry with a new decision, source, target, or root.

## Authority DAG

The proposed authority/effect DAG is:

~~~text
independently prior external authority evidence
-> exact recognized source
-> exact one-shot founding instrument
-> exact Human constituent decision
-> irreversible external one-shot disposition evidence
-> exact eligibility proof set
-> predicate-only eligibility Certification
-> exact mechanical first-adoption Transition
-> exact authoritative root CAS
-> exact successor root
-> terminal Receipt
-> permanent dormancy
~~~

Authority and mechanics are separated:

| Function | Exact source/owner | Forbidden interpretation |
|---|---|---|
| founding authority | independently prior source through exact Instrument | not created by target, successor, G77-40, Governance, or repository control |
| decide whether | Human only | no machine, inferred, administrator, Governance, or Certification choice |
| transport | existing HIC and sole CHE | no Constitutional semantics |
| verify predicates | existing Certification owner | no authority source or decision |
| execute root effect | existing root serialization custodian | no target/content choice |
| publication/activation custody | same exact root custodian in the single CAS/read-back chain | no independent activation discretion |
| reconstruct | owner-local Replay | no trigger, repair, or repeat |
| observe | CRO | passive only |

The external source is genuinely prior or no edge begins. The adopted
MetaRepair contract never authorizes its predecessor. CAP never creates its
own missing entry prerequisite. Human expression does not mutate the root.
Technical custody never becomes constituent authority.

## Identity DAG

The exact forward identity order is:

~~~text
exact predecessor root + G77-36/37/38/39 + frozen incorporation rule
-> NormativeSuccessorPayload
-> FoundingTarget

independently prior source facts
-> SourceEvidence
-> RecognitionProof

SourceEvidence + RecognitionProof + FoundingTarget
+ finalized G77-40 + independently resolved G77-40 assessment
-> FoundingInstrument

Human Act + CHE delivery + Instrument + Target
-> HumanDecision

HumanDecision + UNUSED external disposition slot
-> terminal InstrumentDispositionEvidence

all finalized inputs + InstrumentDispositionEvidence
+ current-root equality/status/exclusivity facts
-> EligibilityProofSet
-> EligibilityCertification
-> ARMED package

ARMED package + exact predecessor root
-> FoundingAdoptionTransition
-> CONSUMED_DORMANT DormancyState
-> exact SuccessorRoot
-> existing RootSnapshotPointerCASIntent
-> existing RootSnapshotPointerCAS
-> commit marker
-> root read-back
-> FoundingReceipt
~~~

The identities are canonical SHA-256 digests of their complete payloads
excluding their own identity/digest and `metadata`. The Transition reserves
the exact normative payload and terminal status but contains no DormancyState,
successor root, CAS, marker, read-back, or Receipt pair. DormancyState binds
the finalized Transition but contains no later pair. The successor root binds
the normative payload and DormancyState. CAS evidence and Receipt follow.
No predecessor hashes its successor; no artifact requires its own descendant;
the graph is finite and acyclic.

## Founding Effect, Atomicity, and Serialization

`ExternalConstituentFoundingAdoptionTransitionV1` is the proposed exact
effect contract. Preconditions are:

1. one recognized independently prior SourceEvidence/RecognitionProof pair;
2. one unrevoked, fresh, singleton FoundingInstrument with no prior use;
3. one exact affirmative HumanDecision and CHE delivery chain;
4. one source-linearized `ADOPTION_DECISION_BOUND`
   InstrumentDispositionEvidence for that exact decision;
5. one complete ProofSet and eligibility Certification;
6. exact G77 lineage, this finalized proposal, an independently resolved
   impact assessment, and the frozen normative successor payload;
7. exact authoritative predecessor pointer/root/generation/State remains
   current;
8. no terminal State already exists except an identical committed success;
9. the ordinary CAP entry remains unreachable for this initial adoption; and
10. all authority, topology, non-circularity, and dormancy predicates pass.

The effect reuses the existing authoritative Constitutional root serialization
domain and `CONSTITUTIONAL_ROOT_SERIALIZATION_CUSTODIAN`. It adds no current
pointer, alternate root, lock, coordinator, owner, or permanent serialization
domain. The exact mutation is one compare-and-set:

~~~text
CAS(
  expected = exact predecessor root pointer/root/generation,
  successor = exact root containing NormativeSuccessorPayload
              + CONSUMED_DORMANT DormancyState
)
~~~

The Transition operation idempotency binds every SourceEvidence,
RecognitionProof, Instrument, Target, HumanDecision,
InstrumentDispositionEvidence, ProofSet, Certification,
predecessor-root, normative-payload, owner, and terminal-status pair. Identical
inputs derive identical Transition, DormancyState, successor root, CAS intent,
and CAS bytes. Same identity with different content fails closed.

Concurrency and crash results are exact:

| Boundary | Deterministic result |
|---|---|
| multiple source/instrument candidates | singleton counts differ from one; no ARMED state |
| concurrent different Human decisions | external UNUSED-slot linearization recognizes one; the losing decision has zero authority |
| identical concurrent candidates | identical bytes; one root CAS wins and all retries read the same successor |
| different target/content | exact target or identity equality fails; no eligible CAS |
| crash before CAS | predecessor remains current; retry reconstructs identical candidate or terminally invalidates on source/root change |
| crash during CAS | authoritative pointer exposes exactly predecessor or successor |
| crash after CAS before marker/Receipt | read back exact successor and reconstruct identical later evidence |
| exact successor already current | return the identical successful Receipt after full read-back validation |
| another root is current | fail closed; no rebase, rollback, substitute, or second attempt |

`ExternalConstituentFoundingReceiptV1` follows marker and read-back. It binds
the exact source, recognition, instrument, target, Human Act/decision,
InstrumentDispositionEvidence, ProofSet, Certification, Transition,
DormancyState, predecessor root,
successor root, CAS intent/CAS, marker, read-back, executing owner, and result:

`FIRST_ADOPTION_COMMITTED_AND_FOUNDING_AUTHORITY_PERMANENTLY_DORMANT`.

It also records `successful_effect_count = 1`,
`founding_authority_reachable = false`, ordinary future evolution
`G70_CAP_ONLY`, and the separately adopted MetaRepair exception only under the
exact G77-38 frozen conditions. The Receipt is evidence after the effect and
cannot authorize or participate in its predecessors.

## Replay Evidence and Terminal Dormancy

Minimum immutable replay evidence is:

1. exact authenticated G77-36 through G77-40 lineage;
2. SourceEvidence, provenance, custody, signature, status, revocation,
   freshness, singleton, and RecognitionProof pairs;
3. Target and normative successor payload pairs;
4. FoundingInstrument and its external signature/status pairs;
5. Human Act, HIC/CHE continuity/delivery, HumanDecision, and irreversible
   InstrumentDispositionEvidence pairs;
6. ProofSet and eligibility Certification pairs;
7. exact predecessor pointer/root/generation read-back;
8. Transition, DormancyState, successor root, CAS intent/CAS, marker, and root
   read-back pairs; and
9. terminal Receipt and permanent-dormancy constants.

Replay resolves immutable evidence in that order and recomputes every identity,
predicate, equality, state transition, root, CAS, read-back, and Receipt. It
may report why eligibility existed, which Human decided, what exact target and
roots were involved, who mechanically executed the effect, whether CAS won,
and why authority is dormant. Replay cannot use a live clock, create evidence,
choose a source/decision, acquire authority, mutate a root, trigger adoption,
repair a chain, reset dormancy, or repeat the effect. CRO remains passive.

## Topology and Anti-Entropy Assessment

| Invariant | Before G77-40 | Proposal artifact | Hypothetical exact adoption |
|---|---:|---:|---:|
| production paths | 1 | 1 | 1 |
| parallel production paths | 0 | 0 | 0 |
| runtime capabilities added | 0 | 0 | 0 |
| permanent Human decision sources added | 0 | 0 | 0 |
| permanent authority owners added | 0 | 0 | 0 |
| ordinary amendment lifecycles added | 0 | 0 | 0 |
| current Constitutional roots added | 0 | 0 | 0 |
| permanent serialization domains added | 0 | 0 | 0 |
| reusable founding authorities added | 0 | 0 | 0 |

The proposal creates only inactive artifact classes. A hypothetical lawful
adoption would temporarily make one externally authorized exact effect
eligible within the existing root domain; its only successful transition
installs its own terminal dormancy. There is no new owner because Certification
and root custody retain their existing mechanical roles. There is no temporary
internal current pointer or coordination service to delete. The required
external disposition domain must already belong to the independently prior
source; Candidate H neither creates it nor treats it as a Constitutional root,
amendment lifecycle, production path, or reusable founding authority.

After success, ordinary G70 CAP is again the sole normal Constitutional
amendment lifecycle. The adopted MetaRepair design remains a separate narrow
exception only under its already-frozen unreachable-CAP, exact-target,
proof-bound conditions. Candidate H itself has no future amendment or repair
authority.

## Reuse Impact Assessment

1. **Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?**

   Proposal impact: authenticated governance lineage, G48 reporting, G69-07
   Human Authority Act transport, one HIC family, the sole CHE, owner/effect
   separation, existing Certification predicate custody, G76 forward identity
   rules, the authoritative root serialization/CAS domain, read-only Replay,
   passive CRO, and ordinary G70 CAP primacy are reused as design inputs only.
   Hypothetical adoption impact: the same owners perform only instrument-bound
   transport, verification, root CAS, read-back, and evidence recording; none
   gains constituent choice.

2. **Katere nove zmogljivosti (če sploh) nastanejo?**

   Proposal impact: only an inactive recognition and one-shot founding model
   is introduced; runtime capabilities added = 0. Hypothetical adoption impact:
   one exact initial-adoption effect could exist if independently prior source
   evidence and every later lawful stage existed. That effect terminates into
   permanent dormancy and is not reusable.

3. **Ali katera obstoječa zmogljivost postane nedosegljiva?**

   Proposal impact: no. Hypothetical adoption impact: no certified capability
   becomes unreachable. The founding mechanism itself intentionally becomes
   unreachable; ordinary CAP and the frozen conditional MetaRepair model remain
   reachable only under their own exact rules.

4. **Ali proposal ali proposed model ustvarja vzporedni tok?**

   No. The proposal performs no effect. The proposed model reuses the single
   authoritative root serialization domain for one exact founding transition
   and then becomes dormant. It creates no second CAP, root, pointer, Human
   channel, production ingress, execution path, Replay writer, or CRO control
   path.

5. **Ali zmanjšuje ali povečuje število produkcijskih poti?**

   Neither. For G77-40 itself, `production_paths_before = 1`,
   `production_paths_after = 1`, `parallel_production_paths_before = 0`, and
   `parallel_production_paths_after = 0`. A hypothetical adoption preserves
   the same counts.

## Fail-Closed Questions and Proposal Blockers

| Question | Exact answer | Consequence |
|---|---|---|
| 1. Can Candidate H be specified without identifying a concrete external constituent source? | Yes, as a recognition/effect model only. | No source instance, eligibility, or adoption authority exists now. |
| 2. What can be designed now and what requires external evidence? | Schemas, identities, target, owners, predicates, DAGs, state machine, CAS, replay, and dormancy can be proposed now. Concrete source identity/provenance/custody/signature/status/uniqueness, an existing one-shot disposition domain and read-back, an issued Instrument, and a Human Act must arrive as independent future evidence. | Missing external evidence fails closed. |
| 3. Is a new temporary authority owner required? | No. | Existing owners may perform only exact assigned mechanical functions. |
| 4. Can existing root custody execute without constituent decision authority? | Yes. | It executes one byte-exact CAS or no effect; it cannot choose content. |
| 5. Can Certification verify without becoming the authority source? | Yes. | Certification proves predicates only; source Instrument plus Human decision supply authority. |
| 6. Can HIC/CHE transport without gaining semantics? | Yes. | They bind identity/continuity/delivery and forward to the exact receiver only. |
| 7. Can the mechanism become permanently unreachable after success? | Yes. | The external disposition slot is irreversibly consumed and terminal DormancyState is embedded in the successor root with no outgoing/reset edge. |
| 8. Is ordinary G70 CAP again the sole normal lifecycle after adoption? | Yes. | Candidate H terminates; MetaRepair remains only the already-frozen narrow exception. |

Proposal-level blocker result: `NONE_DISCOVERED_IN_MODEL_STRUCTURE`.

External prerequisite result:
`ACTUAL_EXTERNAL_CONSTITUENT_AUTHORITY_EVIDENCE_ABSENT`.

The absence is not repaired or hidden. It prevents ARMED state and all
adoption. An independent Constitutional Impact Assessment of G77-40 is the
exact next boundary. Even a favorable assessment would not supply a source,
Instrument, Human Act, Ratification, Certification, publication, activation,
implementation authority, CDP authority, or adoption.

# 2. Code Evidence

## Public API

No public or runtime API is added or modified. Every named schema, identity,
predicate, State, Transition, CAS, and Receipt is a proposal-only
Constitutional contract, not an implemented model, validator, route, command,
store, transaction, lock, provider, credential, session, or deployment change.

## Orchestration Entry Point

The only Human transport path remains:

~~~text
Human -> permitted HIC profile -> sole CHE
-> exact externally assigned founding receiver
-> predicate verification
-> existing root serialization custodian
~~~

The path is unavailable unless a recognized independently prior instrument
assigns the exact receiver/effect. HIC and CHE transport only. The root
custodian receives an already-decided exact candidate and may perform only the
single current-root CAS.

## Semantic Reductions

### Eligibility

~~~text
independently prior authenticated source
AND singleton exact Instrument
AND exact affirmative Human decision
AND complete current ProofSet and eligibility Certification
AND exact predecessor root remains current
-> ARMED

otherwise -> no root mutation
~~~

### Effect

~~~text
ARMED + exact immutable candidate
-> CONSUMING
-> one existing-domain root CAS
-> exact successor + embedded CONSUMED_DORMANT State
-> terminal Receipt
~~~

### Refusal or invalidity

~~~text
Human refusal -> REFUSED_DORMANT -> no second decision

revoked/expired/duplicated/conflicting source or stale target
-> INVALIDATED_DORMANT -> no reissue/rebase/reuse
~~~

### Permanent boundary

~~~text
any terminal State
-> founding_authority_reachable = false
-> no outgoing transition
-> ordinary future amendment = G70 CAP only
~~~

## Public Validators

No validator is implemented. A future separately authorized validator must
reject:

- absent, self-derived, ambient, administrator-derived, or unverifiable
  external authority evidence;
- source evidence not independently prior to the target and successor;
- invalid custody, provenance, signature, freshness/status, or revocation;
- source or eligible-instrument count other than exactly one;
- an absent, mutable, non-linearizable, reusable, or non-read-back external
  disposition record, or more than one recognized Human decision;
- a wildcard, substitute, equivalent, partial, rebased, stale, or future
  target;
- any G77-36 through G77-39 or G77-38 freeze mismatch;
- missing or non-current predecessor pointer/root/generation;
- inferred, generic, machine, Governance, Certification, HIC, CHE,
  administrator, repository, or deployment consent;
- a Human decision not bound to the exact Instrument and Target;
- a second Human decision, second effect, prior use, reissue, reset, or
  nonterminal dormancy row;
- a backward identity edge or self-authorizing authority edge;
- altered effect, mutation, publication, or activation custody;
- a second CAP, root, current pointer, serialization domain, amendment
  lifecycle, production path, or parallel path;
- CAS/idempotency/read-back/Receipt mismatch; or
- Replay/CRO mutation, trigger, repair, or authority expansion.

## Canonical Data Models

| Proposed model | Exact source/owner | Purpose | Authority boundary |
|---|---|---|---|
| SourceEvidenceV1 | independently prior external source | authenticate actual prior source facts | absent in G77-40; cannot be self-derived |
| RecognitionProofV1 | predicate validator | prove source recognition requirements | verification only |
| InitialAdoptionTargetV1 | canonical derivation | bind exact lineage, predecessor, successor payload, scope | no wildcard/rebase |
| OneShotFoundingInstrumentV1 | recognized external source | assign one exact effect | maximum one; no reissue/reset |
| HumanFirstAdoptionDecisionV1 | Human Authority via HIC/CHE | decide adopt or refuse exact target | Human sole decision source |
| InstrumentDispositionEvidenceV1 | independently prior source custody | irreversibly bind the single Human decision in the source's existing domain | records but does not choose the decision |
| EligibilityProofSetV1 | canonical verifier | bind all complete predicates | no decision/effect |
| EligibilityCertificationV1 | Certification owner | attest predicate result | not founding authority |
| AdoptionTransitionV1 | exact effect contract | reserve one exact root effect | no later identity bindings |
| DormancyStateV1 | canonical derivation | make founding authority terminally unreachable | no outgoing edge |
| Root CAS/marker/read-back | existing root serialization custodian | atomically install and confirm exact successor | custody only |
| FoundingReceiptV1 | existing root serialization custodian | record exact result and permanent dormancy | evidence only |
| Replay | owner-local custodian | reconstruct immutable chain | read-only |
| CRO | passive Observatory | observe non-secret finalized evidence | no control |

## Deterministic Algorithms

1. Authenticate G77-36 through G77-39 and exact repository lineage.
2. Derive the normative successor payload and exact Target without any later
   founding artifact.
3. Authenticate an independently supplied SourceEvidence instance under its
   own provenance, custody, signature, status, and uniqueness system.
4. Validate exactly one eligible source and one exact one-shot Instrument.
5. Resolve one exact Human Act through HIC/CHE and reduce it to adopt or refuse.
6. Linearize the exact decision once in the independently prior source's
   UNUSED disposition slot and read back identical terminal evidence.
7. On refusal, derive terminal `REFUSED_DORMANT` and stop permanently.
8. On adoption, derive the complete ProofSet and verify every closed predicate.
9. Re-read the authoritative root; any mismatch derives
   `INVALIDATED_DORMANT` and forbids rebase.
10. Derive Transition, `CONSUMED_DORMANT` State, exact successor root, and
   existing root CAS bytes in forward order.
11. Compare-and-set the exact predecessor once, then flush and read back the
    exact successor.
12. Reconstruct or create the identical marker and Receipt only after read-back.
13. Replay validates the recorded chain without a live choice or mutation.

## Responsibility Boundaries

| Responsibility | Exact source/owner | Negative boundary |
|---|---|---|
| supply prior founding authority | future concrete external constituent source | not current Constitution, target, successor, or repository |
| decide adopt/refuse | Human Authority | sole decision source; no direct root mutation |
| transport decision | existing HIC and sole CHE | no semantic or constituent authority |
| verify predicates | existing Certification owner | no decision, mutation, or founding authority |
| execute exact effect | existing Constitutional root serialization custodian | no content/scope/target choice |
| publish/activate exact successor | same root CAS/marker/read-back custody | no separate lifecycle or discretion |
| govern future normal amendments | ordinary G70 CAP owners | no power to bootstrap this predecessor |
| perform later frozen MetaRepair | exact frozen G77-38 owners, only if separately adopted and eligible | no founding authority |
| reconstruct | owner-local Replay | read-only; no repeat/repair |
| observe | CRO | passive; no control/Certification |
| assess G77-40 | later independent Constitutional Governance | not performed here |
| implement | later separately authorized CDP | not authorized |

## Repository Evidence

The authenticated Git commit/tree/parent, exact G77-36 through G77-39 hashes,
G77-38 frozen operational design, G77-39 exhaustive authority audit, active
G69 Human/HIC/CHE boundaries, G70 CAP order, G76 forward identity rules, and
the existing root serialization custody model are the repository evidence
basis. No runtime observation, external assertion, credential, administrator,
deployment, test fixture, or proposal claim supplies constituent authority.

# 3. Constitutional Self-Assessment

## Verified as Proposal Structure

- Candidate H is specified as an inactive recognition/effect model only.
- No concrete external source identity or evidence is fabricated.
- Human remains the sole decision source; transport, verification, and
  execution remain mechanical.
- The target binds exact G77-36 through G77-39 pairs, predecessor root, and
  byte-exact normative successor payload.
- Source uniqueness and one-instrument exclusivity precede ARMED state.
- An independently prior irreversible disposition record linearizes the one
  Human decision without adding an internal pointer or authority owner.
- The authority and identity DAGs are forward-only and non-circular.
- The adopted MetaRepair contract does not authorize its predecessor.
- One exact existing-domain root CAS supplies atomicity and serialization.
- No new current pointer, root domain, owner, CAP, lifecycle, or path exists.
- Success, refusal, invalidation, expiry, and target staleness have terminal
  non-resettable results.
- The successful successor embeds `founding_authority_reachable = false`.
- Crash, concurrency, retry, read-back, Receipt, and Replay reductions are
  deterministic.
- Replay remains read-only and CRO passive.
- G77-38 frozen mechanics and topology remain unchanged.
- Ordinary G70 CAP is the sole normal future amendment lifecycle.
- The proposal performs no adoption, Human Act, Certification, publication,
  activation, implementation, deployment, O01, or CDP.

## Not Verified

- No actual independently prior constituent source, provenance, custody,
  signature, status, freshness, revocation, or uniqueness evidence exists.
- No actual founding Instrument or Human constituent decision exists.
- No independent Constitutional Impact Assessment of G77-40 has occurred.
- No Ratification, Certification, publication, activation, adoption, or CDP
  authority exists.
- No schema, validator, state, transition, root, CAS, marker, read-back,
  Receipt, persistence primitive, route, or runtime behavior is implemented.
- No external evidence system, concurrency, crash, recovery, cryptography,
  custody, migration, rollback, security, deployment, or production behavior
  is tested by this documentation-only proposal.
- Existing enforcement, hook, external-system, privacy, custody, deployment,
  and partial-conformance limitations remain visible and unchanged.

## Exact Next Boundary

The only next permissible boundary is an independent Constitutional Impact
Assessment of this exact G77-40 artifact. It must test external-priority
recognition, Human/effect separation, exact-target completeness, identity DAG,
source/instrument uniqueness, root serialization, permanent dormancy, Replay,
topology, and all fail-closed cases without supplying missing external evidence
or performing adoption.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| G48 structure | exactly six top-level sections and all Code Evidence subsections | heading review | `PASS` |
| authenticated repository | commit/tree/parent and clean proposal start | Git review | `PASS` |
| predecessor hashes | exact G77-36 through G77-39 SHA-256 values | SHA-256 review | `PASS` |
| immutable predecessors | no G77-36 through G77-39 mutation | repository review | `PASS` |
| G77-38 freeze | all frozen mechanics expressly unchanged | scope review | `PASS` |
| Candidate H only | one external Human-decided exact-target one-shot model | scope review | `PASS` |
| source non-fabrication | recognition schema separated from actual absent evidence | evidence review | `PASS` |
| independently prior source | explicit provenance/non-self-derivation predicates | authority review | `PASS` |
| source/instrument uniqueness | exactly-one counts and singleton commitment | concurrency review | `PASS` |
| one Human decision | external UNUSED-to-terminal disposition linearization | concurrency review | `PASS` |
| Human sole decision | exact adopt/refuse decision; no inferred consent | authority review | `PASS` |
| HIC/CHE boundary | transport/continuity only | boundary review | `PASS` |
| Certification boundary | predicate verification only | boundary review | `PASS` |
| exact target | exact lineage, predecessor, payload, scope; no equivalence/rebase | target review | `PASS` |
| no successor/predecessor cycle | normative payload separated from later dormancy/root evidence | DAG review | `PASS` |
| authority DAG | independently prior source precedes every effect | DAG review | `PASS` |
| identity DAG | every identity uses finalized predecessors only | DAG review | `PASS` |
| one-shot state machine | closed success/refusal/invalidity terminal rows | lifecycle review | `PASS` |
| permanent dormancy | embedded terminal State; no reset/outgoing edge | reachability review | `PASS` |
| exact effect custody | existing owners, mechanically constrained | owner review | `PASS` |
| atomicity | one exact authoritative root CAS | serialization review | `PASS` |
| concurrency/idempotency | singleton eligibility and identical-byte retry | deterministic review | `PASS` |
| crash/read-back/Receipt | predecessor-or-successor and reconstructable evidence | recovery review | `PASS` |
| Replay/CRO | read-only/passive and cannot trigger effect | boundary review | `PASS` |
| ordinary CAP primacy | sole normal lifecycle after founding | lifecycle review | `PASS` |
| topology | 1 production path; 0 parallel paths | topology review | `PASS` |
| anti-entropy | zero permanent owners/roots/domains/lifecycles/reusable authority | count review | `PASS` |
| fail-closed questions | all eight answered explicitly | completeness review | `PASS` |
| actual external evidence | explicitly absent | evidence review | `NOT_REACHED` |
| independent assessment | required next | governance review | `NOT_REACHED` |
| relevant unchanged G69/G70 tests | 140 targeted tests | repository validation | `PASS` |
| balanced Markdown fences | 32 fence tokens | static validation | `PASS` |
| trailing whitespace | `git diff --check` | static validation | `PASS` |
| exactly one G77-40 artifact | one exact repository path | mutation review | `PASS` |
| runtime/test/config changes | sole untracked path is the G77-40 governance artifact | mutation review | `PASS` |

# 5. Repository Mutation Summary

Modified files:

- added
  `docs/governance/G77_40_EXTERNAL_CONSTITUENT_ONE_SHOT_FOUNDING_AUTHORITY_MODEL_PROPOSAL_V1.md`
  as the sole G77-40 artifact.

No existing file changed. G77-36 through G77-39 remain byte-identical.

API compatibility:

- no API, code, model, validator, serializer, command, route, owner, workflow,
  test, configuration, persistence, release, deployment, or runtime contract
  is activated or implemented.

Boundary preservation:

- this artifact is proposal-only and independently unassessed;
- actual external constituent evidence remains absent;
- no Human Act, approval, authority, adoption, Ratification, Certification,
  publication, activation, implementation, deployment, O01, or CDP occurs;
- G77-38 operational mechanics remain frozen;
- ordinary G70 CAP, Replay, CRO, current-root, and production topology
  boundaries remain unchanged; and
- production paths remain one with zero parallel paths.

Unrelated pre-existing changes:

- None observed. The worktree was clean at proposal start.

# 6. Certification Verdict

CANDIDATE_H_FOUNDING_MODEL_PROPOSED
