# 1. Implementation Summary

Generation: G77-64

Report and proposal identity:
`G77_64_EXTERNAL_CONSTITUENT_CANDIDATE_H_INSTANTIATION_CONTRACT_CONSTITUTIONAL_DESIGN_PROPOSAL_REVISION_4_CERTIFICATION_TIME_CLOSURE_V1`

Proposal revision: `4`

Proposal status: `PROPOSAL_ONLY_UNASSESSED`

Amendment kind: `ADDITION`

Constitutional baseline: authenticated committed G0 through G77-63. G77-62
is immutable Revision 3. G77-63 is its authoritative independent G70-03
assessment and classifies it as `UNRESOLVED_CONSTITUTIONAL_IMPACT` solely
because `CertificationV3.certified_at` has no persisted predecessor or
deterministic derivation. G77-61 B01, B02, B03, and B05 remain independently
resolved. Every predecessor remains closed and unchanged.

Authenticated repository identity:

- Commit: `321d2116260f4e9d17c5c14e05bebc405618fd4e`
- Tree: `35c4eaf246d08acccbda0b9980fbee0bfcf3db22`
- Subject: `G77-63: assess Candidate H instantiation contract revision 3`
- Immediate parent: `16f9eeb431092b70d082364c04f23a9b374bb6ce`
- Proposal-start worktree state: clean
- G77-62 SHA-256:
  `661394be4e32b2e965f6a906e865a78128572084bbe52c5d0aad3bfdd5deca1e`
- G77-63 SHA-256:
  `73190f6a7f919469b7d67f512cf955e9c5531b9f41170229061760f03c2ad7fe`

Revision predecessor binding:

| Field | Exact binding |
|---|---|
| previous proposal | `G77_62_EXTERNAL_CONSTITUENT_CANDIDATE_H_INSTANTIATION_CONTRACT_CONSTITUTIONAL_DESIGN_PROPOSAL_REVISION_3_FULL_TRANSITIVE_CLOSURE_V1` |
| previous proposal revision | `3` |
| previous proposal digest | `sha256:661394be4e32b2e965f6a906e865a78128572084bbe52c5d0aad3bfdd5deca1e` |
| authoritative assessment | `G77_63_INDEPENDENT_CONSTITUTIONAL_IMPACT_ASSESSMENT_EXTERNAL_CONSTITUENT_CANDIDATE_H_INSTANTIATION_CONTRACT_REVISION_3_FULL_TRANSITIVE_CLOSURE_V1` |
| authoritative assessment digest | `sha256:73190f6a7f919469b7d67f512cf955e9c5531b9f41170229061760f03c2ad7fe` |
| authoritative assessment class | `UNRESOLVED_CONSTITUTIONAL_IMPACT` |
| controlling finding | `G77_61_B04_PROOFSET_V3_CERTIFICATION_V3_AND_TRANSITION_V3_NOT_CLOSED` |

Reporting date: 2026-08-09.

Objective:

Create only the minimal proposal-only Revision 4 closure for the single
G77-63 defect. Derive `CertificationV3.certified_at` from finalized persisted
predecessor evidence, propagate that same derived instant through existing
downstream time fields, and restore deterministic crash/Replay reconstruction
without a clock, producer choice, new State, family, version, owner, pointer,
domain, or authority.

This proposal does not modify G77-63 or any predecessor, independently assess
Revision 4, Ratify, create a Human Act, instantiate any proposed artifact,
implement runtime code, change tests or configuration, publish, activate,
execute BEGIN, mutate a root, perform CDP or CLIA work, deploy, or create a
production effect.

## Exact Repair Result

~~~text
INITIAL_BEGIN:
  exact DECISION_BOUND_ADOPT disposition.linearized_at
  -> attempt_logical_instant

RETRY_AFTER_ABANDONED:
  exact immediately preceding ABANDONED
  AttemptTerminalReadBackV1.terminal_logical_instant
  -> attempt_logical_instant

CertificationV3.certified_at = attempt_logical_instant
TransitionV3.effective_at = CertificationV3.certified_at
pre-terminal derived-time fields = same attempt_logical_instant

same finalized ProofSetV3 + same event + same attempt + same root
-> one attempt_logical_instant
-> one CertificationV3 byte sequence
-> one TransitionV3 byte sequence
~~~

No live or wall clock participates. The rule allocates no timestamp and gives
no producer discretion. Later allocation, token, Commitment, Coordinator,
root, CAS, marker, read-back, and terminal logical instants retain their exact
G77-62 derivations and are not moved earlier.

## Finalized Logical-Instant Census

Every candidate time source was reconstructed before selecting the rule:

| Candidate value | Initial attempt | Retry attempt | Classification | Disposition |
|---|---|---|---|---|
| Human Decision `decision_effective_at` | present | present through original decision | `AVAILABLE_BEFORE_CERTIFICATION`, `SEMANTICALLY_WRONG` | Human choice effectiveness, not attempt boundary |
| Human Finality `finalized_at` | present | present through original finality | `AVAILABLE_BEFORE_CERTIFICATION`, `SEMANTICALLY_WRONG` | Human finality time; Certification cannot reinterpret it |
| decision disposition `linearized_at` | exact DECISION_BOUND_ADOPT predecessor | exact original disposition remains bound | `AVAILABLE_BEFORE_CERTIFICATION`, `REUSE_ELIGIBLE` for initial | authoritative external transition into the adopt-bound event |
| external status-row/status-version `status_effective_at` | reachable through current status version | may differ after later status changes | `AVAILABLE_BEFORE_CERTIFICATION`, `SEMANTICALLY_WRONG` | status freshness time, not stable attempt time |
| external status Snapshot time | no time field exists | no time field exists | `SEMANTICALLY_WRONG` | identity/digest only; no instant may be inferred |
| external Fence time | no time field exists | Fence not repeated | `SEMANTICALLY_WRONG` | Fence contains no instant and retry forbids another Fence |
| Target origin root `effective_logical_instant` | resolvable through origin root | stale for later attempts | `AVAILABLE_BEFORE_CERTIFICATION`, `SEMANTICALLY_WRONG` | founding origin, not current attempt |
| ProofSetV3 derivation time | no field exists | no field exists | `SEMANTICALLY_WRONG` | no value exists to reuse |
| founding event time | event formula deliberately excludes time | same | `SEMANTICALLY_WRONG` | no independent event-time scalar exists |
| attempt time | no stored scalar in event/attempt | no stored scalar in event/attempt | `SEMANTICALLY_WRONG` before this derivation | prose cannot create a value |
| predecessor AttemptTerminalReadBackV1 `terminal_logical_instant` | predecessor pair is null | exact and finalized | `AVAILABLE_BEFORE_CERTIFICATION`, `REUSE_ELIGIBLE` for retry | immutable boundary ending the immediately preceding attempt |
| CHE/HIC timestamps | transport evidence may exist | transport evidence may exist | `AVAILABLE_BEFORE_CERTIFICATION`, `SEMANTICALLY_WRONG` | transport cannot supply Certification semantics |
| current wall clock / producer time | callable but not persisted predecessor | same | `LIVE_NONDETERMINISTIC` | forbidden |
| token/allocation logical instant | not yet created | not yet created | `AFTER_CERTIFICATION_ONLY` | cannot be a predecessor |
| Guard/MetaRepair derived times | not yet created | not yet created | `AFTER_CERTIFICATION_ONLY` | successors, not sources |
| Commitment/Coordinator/root/CAS/marker/read-back times | not yet created | not yet created | `AFTER_CERTIFICATION_ONLY` | terminal successors, not sources |

No single existing instant is semantically correct for both presence rows.
The minimum rule is therefore deterministic option D: one exact two-row
predecessor formula. It reuses one finalized source per already-declared
attempt kind and creates no new artifact.

## Canonical Attempt Logical-Instant Derivation

`attempt_logical_instant` is a derived validation scalar only. It is not a new
artifact field, identity, State, clock reading, pointer, token, or authority.
Its complete derivation is:

~~~text
derive_attempt_logical_instant(proof_set):
  require exact ProofSetV3 type/version/identity/digest and ELIGIBLE result

  if proof_set.attempt_kind == INITIAL_BEGIN:
    require proof_set.attempt_sequence == 1
    require predecessor_attempt_identity == null
    require predecessor_attempt_terminal_read_back pair == null
    require predecessor_abandoned_commitment pair == null
    require consuming_disposition pair == null
    resolve exact decision_disposition_evidence pair
    require disposition_kind == ADOPTION_DECISION_BOUND
    require slot_status == DECISION_BOUND_ADOPT
    return decision_disposition_evidence.linearized_at

  if proof_set.attempt_kind == RETRY_AFTER_ABANDONED:
    require proof_set.attempt_sequence > 1
    require exact predecessor attempt identity
    resolve exact predecessor_attempt_terminal_read_back pair
    require terminal_result == ABANDONED
    require next_attempt_sequence == proof_set.attempt_sequence
    require terminal-evidence event == proof_set.founding_event_identity
    require terminal-evidence attempt == predecessor_attempt_identity
    require terminal-evidence resulting/read-back root == proof_set current root
    require exact predecessor ABANDONED commitment equality
    require exact same-event CONSUMING disposition
    return predecessor_attempt_terminal_read_back.terminal_logical_instant

  otherwise:
    fail closed
~~~

The selected source timestamp is already covered by its finalized source
artifact identity/digest. A missing, null, malformed, non-canonical,
substituted, cross-event, non-immediate, wrong-result, wrong-sequence, or stale
source fails before Certification construction.

## Complete CertificationV3 Time Closure

Revision 4 retains the G77-62 `ExternalConstituentFoundingEligibilityCertificationV3`
family, artifact version V3, complete common envelope, complete semantic field
set, owner, prefixes, CJ1 rules, nullability, identity/idempotency/digest
formulas, and predicate-only authority. It changes no field and creates no V4.

The one controlling replacement rule is:

~~~text
CertificationV3.certified_at =
  derive_attempt_logical_instant(exact resolved ProofSetV3)
~~~

`certified_at` is mandatory and non-null. It is a deterministic logical
instant, not the wall time at which a Certification object is serialized.
Certification creation must validate the source artifact and equality before
constructing its semantic object `S_C`. The unchanged G77-62 formulas then
apply:

~~~text
CertificationV3.idempotency_identity =
  founding-certification-idem-v3:SHA256(CJ1(S_C))

CertificationV3.identity =
  founding-certification-v3:SHA256(CJ1(S_C plus idempotency_identity))

CertificationV3.digest =
  sha256:SHA256(CJ1(S_C plus idempotency_identity))
~~~

The uniqueness proof is exact:

~~~text
same ProofSetV3 pair
-> same presence row
-> same exact timestamp-source artifact pair
-> same source timestamp bytes
-> same certified_at
-> same S_C
-> same idempotency identity
-> same CertificationV3 identity/digest/bytes
~~~

Different `certified_at` under the same ProofSet idempotency or identity fails
closed as different content. Certification still evaluates predicates only.
The time equality cannot choose a Target, Instrument, Human decision, attempt,
BEGIN, result, token, root, or external status.

## Transition and Downstream Time Propagation

Revision 4 adds exact equality rules to existing G77-62 fields; it adds no
field or schema version:

| Existing field | Exact Revision 4 value |
|---|---|
| `CertificationV3.certified_at` | derived attempt logical instant |
| `FoundingAdoptionTransitionV3.effective_at` | exact CertificationV3 `certified_at` |
| `ConstitutionalExistingOrdinaryRepairChainCensusV2.derived_at` | exact TransitionV3 `effective_at` |
| `OrdinaryCAPReachabilityStateV2.computed_at` | exact TransitionV3 `effective_at` |
| `OrdinaryCAPReachabilityStateV2.committed_at` | exact TransitionV3 `effective_at` |
| `CandidateHOneShotDormancyRebaseGuardV2.guarded_at` | exact TransitionV3 `effective_at` |
| `ConstitutionalMetaRepairTransitionV3.transition_prepared_at` | exact TransitionV3 `effective_at` |
| `ConstitutionalMetaRepairStateV3.effective_at` | exact TransitionV3 `effective_at` |

The equality chain is forward and finite:

~~~text
persisted disposition or preceding terminal read-back
-> derived attempt logical instant
-> CertificationV3.certified_at
-> TransitionV3.effective_at
-> Census/CAP/Guard/Meta derived-time fields
~~~

No downstream producer resamples or selects a time. Unique Certification plus
the unchanged exact predecessor closure yields one Transition semantic object,
idempotency identity, identity, digest, and byte sequence.

BEGIN eligibility remains determined only by Transition presence mode:

- `INITIAL_BEGIN` permits the retained Fence/BEGIN exactly once;
- `RETRY_AFTER_ABANDONED` forbids Snapshot, Fence, BEGIN, status CAS, Human
  decision, Target, Instrument, disposition, and founding-event recreation.

The propagated scalar does not authorize BEGIN. It is identity/audit content
only.

Later G77-62 times remain unchanged:

- allocation logical instant is the retained finalized root-domain allocation
  token instant;
- CommitmentV3 `terminal_logical_instant` is the retained finalized terminal
  token instant;
- CoordinatorV4 repeats the commitment terminal instant;
- RootV4 `effective_logical_instant`, CAS, marker, and read-back retain the
  exact root-domain token rules; and
- AttemptTerminalReadBackV1 repeats the terminal chain instant.

Those values are successors and never feed backward into Certification.

## Replay and Crash Reconstruction

Starting only from persisted predecessors, Replay performs:

1. validate and reconstruct ProofSetV3;
2. select its exact initial or retry presence row;
3. resolve the exact disposition or predecessor terminal-read-back pair;
4. read the exact persisted source timestamp;
5. derive `attempt_logical_instant` with the closed two-row formula;
6. set `CertificationV3.certified_at` exactly equal;
7. recompute Certification semantic bytes, idempotency, identity, and digest;
8. set TransitionV3 `effective_at` equal and reconstruct Transition;
9. validate the propagated Census/CAP/Guard/Meta equality chain; and
10. reconstruct the already confirmed Commitment/root/terminal chain.

Required result:

~~~text
COMPLETE_READ_ONLY_DETERMINISTIC_RECONSTRUCTION
~~~

Replay uses no live clock, wall time, producer timestamp, selector, repair,
CAS, lock, mutation, Human choice, external authority, or inferred value. CRO
may passively observe the finalized scalar but cannot produce or alter it.

The critical crash boundary is closed:

~~~text
crash after finalized ProofSetV3 and before CertificationV3
-> restart resolves the identical ProofSet and exact source predecessor
-> identical attempt_logical_instant
-> identical certified_at
-> identical CertificationV3 bytes
-> identical TransitionV3 bytes
~~~

No new state, time allocation, token, lock, or persistence slot is necessary.

## Minimality and Preserved Invariants

Revision 4 changes one missing equality derivation and its propagation rules.
Because CertificationV3 and every downstream successor remain proposal-only
and uninstantiated, the V3 schema is corrected before adoption. There is no
historical V3 instance to preserve and no need for CertificationV4 or a new
downstream version.

The independently confirmed structural set remains exactly:

~~~text
15 successor schema versions
14 successors of existing families
1 new AttemptTerminalReadBackV1 family
0 additional Revision 4 versions
0 additional Revision 4 families
~~~

Removing `certified_at` was rejected because the historical Certification
family uses it as audit content and existing Transition semantics retain an
`effective_at` field. Canonical null was rejected because it would erase that
audit value without closing downstream time equality. One exact branch formula
preserves the field, historical ordering role, and Replay while adding no
machinery.

Exact preserved counts:

| Measure | G77-63 confirmed value | Revision 4 proposed value | Delta |
|---|---:|---:|---:|
| production paths | 1 | 1 | 0 |
| parallel production paths | 0 | 0 | 0 |
| persistent founding paths | 0 | 0 | 0 |
| permanent authority owners added | 0 | 0 | 0 |
| canonical artifact families added | 1 | 1 | 0 |
| schema versions required | 15 | 15 | 0 |
| root fields added | 0 | 0 | 0 |
| root pointers added | 0 | 0 | 0 |
| serialization domains added | 0 | 0 | 0 |
| HIC families | 1 | 1 | 0 |
| CHE definitions | 1 | 1 | 0 |
| Ratification lifecycles | 1 | 1 | 0 |

Human Authority remains the sole Human decision source. Certification remains
predicate-only. HIC/CHE remain transport-only. Replay remains read-only. CRO
remains passive. The root custodian remains mechanical. Ordinary G70 remains
the exclusive post-founding amendment lifecycle.

## G77-63 Finding Disposition

| Controlling finding | Revision 4 proposal closure | Proposal claim |
|---|---|---|
| `G77_61_B04_PROOFSET_V3_CERTIFICATION_V3_AND_TRANSITION_V3_NOT_CLOSED` | exact two-row predecessor derivation fixes `certified_at`; Transition and downstream fields reuse the same scalar; crash/Replay are deterministic | `ADDRESSED_PROPOSAL_ONLY` |

G77-61 B01, B02, B03, and B05 are not reopened. The exact 15-successor set,
Target, Instrument, consumer classification, event/attempt, terminal DAG,
Authority DAG, topology, and Replay structure are retained. Only the missing
time derivation and equality propagation are added.

## Reuse Impact Assessment

1. **Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?**

   Ponovno se uporabijo dokončni čas linearizacije odločitvene dispozicije,
   terminalni logični čas prejšnjega ABANDONED poskusa, obstoječi ProofSetV3,
   CertificationV3, TransitionV3, Human Authority, HIC/CHE, Replay, CRO in
   običajni G70. Noben nov vir časa ni uveden.

2. **Katere nove zmogljivosti (če sploh) nastanejo?**

   Ne nastane nova zmogljivost ali družina artefaktov. Predlagana je samo
   deterministična dvovrstična izpeljava obstoječega polja `certified_at` in
   natančna propagacija iste vrednosti.

3. **Ali katera obstoječa zmogljivost postane nedosegljiva?**

   Ne. Zgodovinski artefakti ostanejo nespremenjeni, predlagana Candidate H
   veriga pa ostane nedosegljiva do neodvisne ocene in morebitnih poznejših
   ustavnih korakov.

4. **Ali implementacija ustvarja vzporedni tok?**

   Ne. Implementacije ni, časovna izpeljava pa ne ustvarja poti, lastnika,
   stanja, kazalca ali novega BEGIN.

5. **Ali zmanjšuje ali povečuje število produkcijskih poti?**

   Ne. Ostane ena produkcijska pot in nič vzporednih produkcijskih poti.

# 2. Code Evidence

## Public API

No runtime API, callable, route, model, serializer, validator, persistence
primitive, clock interface, or configuration value is added or modified. The
derivation is a proposal contract only.

## Orchestration Entry Point

The only Human production entry remains:

~~~text
Human -> permitted HIC -> sole CHE -> exact eligible owner
-> sole CHE Response/Continuation -> same HIC
~~~

Certification time is derived inside the proposed predicate-evidence chain.
It does not accept Human or transport input and creates no route.

## Semantic Reductions

### Initial

~~~text
INITIAL_BEGIN ProofSetV3
+ exact DECISION_BOUND_ADOPT disposition.linearized_at
-> one attempt_logical_instant
-> one certified_at
~~~

### Retry

~~~text
RETRY_AFTER_ABANDONED ProofSetV3
+ exact immediately preceding terminal-read-back.terminal_logical_instant
-> one attempt_logical_instant
-> one certified_at
~~~

### Reconstruction

~~~text
same ProofSet and predecessors
-> same certified_at
-> same Certification
-> same Transition
-> same downstream evidence
~~~

## Public Validators

No validator is implemented. A future separately authorized validator must
reject:

- an unknown attempt kind or mismatched initial/retry presence row;
- initial time not equal to exact decision disposition `linearized_at`;
- retry time not equal to exact preceding terminal `terminal_logical_instant`;
- missing, null, malformed, live, wall-clock, producer-selected, cross-event,
  stale, non-immediate, wrong-result, or wrong-sequence time evidence;
- Certification `certified_at` differing from the derivation;
- Transition, Census, CAP, Guard, or Meta time differing from Certification;
- a later token/root time used as a backward Certification predecessor;
- same idempotency/identity with different time or bytes;
- Replay/CRO mutation or authority expansion; and
- topology other than the preserved counts.

## Canonical Data Models

| Model | Revision 4 disposition |
|---|---|
| ProofSetV3 | unchanged; supplies attempt kind and exact predecessor pairs |
| attempt logical instant | derived scalar only; no artifact/field/State |
| CertificationV3 | same V3 schema; `certified_at` equality closed |
| TransitionV3 | same V3 schema; `effective_at` equals Certification |
| Census/CAP/Guard/Meta | same schemas; existing time fields equal Transition |
| Commitment/root/terminal chain | unchanged later token-derived times |
| Replay/CRO | read-only/passive reuse |

## Deterministic Algorithms

1. Validate ProofSetV3 and select exactly one presence row.
2. Resolve the exact row-specific finalized timestamp source.
3. Validate event, attempt, sequence, result, and current-root equalities.
4. Derive one `attempt_logical_instant` without a clock.
5. Set and validate CertificationV3 `certified_at`.
6. Recompute Certification idempotency, identity, digest, and bytes.
7. Set TransitionV3 `effective_at` equal and recompute Transition.
8. Validate exact downstream equality propagation.
9. Preserve later token/root time derivations and DAG direction.
10. Fail closed on any missing, ambiguous, selected, inferred, or conflicting
    value.

## Responsibility Boundaries

| Responsibility | Exact owner/source | Negative boundary |
|---|---|---|
| supply initial time predecessor | external disposition-domain owner | finalized disposition field only; no Certification authority |
| supply retry time predecessor | root custodian's finalized terminal evidence | prior result evidence only; no reusable founding authority |
| derive/validate Certification time | Certification owner | deterministic equality; no clock or semantic choice |
| bind Transition time | root custodian | exact Certification equality; no new BEGIN authority |
| derive downstream evidence | Governance/root owners | same scalar or retained later token time |
| issue Human meaning | Human Authority | sole Human decision source |
| transport | HIC/CHE | no time or semantic authority |
| reconstruct | owner-local Replay | read-only; no inference or clock |
| observe | CRO | passive; no control or time production |
| assess Revision 4 | later independent Governance assessment | not performed here |

## Repository Evidence

The evidence basis is authenticated G77-42 Human decision/finality and
disposition schemas; G77-44 external status/Snapshot/Fence contracts; G77-62
ProofSetV3, CertificationV3, TransitionV3, attempt, terminal-read-back, and
downstream contracts; G77-63's exact remaining finding; G76-06 forward DAG
rules; G70-03 assessment ordering; G48 reporting structure; and exact Git and
SHA-256 evidence. No runtime behavior supplies the proposal semantics.

# 3. Constitutional Self-Assessment

## Verified as Proposal Structure

- G77-62 and G77-63 are bound by exact immutable identities and digests.
- Every pre-Certification logical-instant candidate is explicitly classified.
- No generic attempt-time value is inferred from prose.
- Initial time derives exactly from finalized DECISION_BOUND_ADOPT
  `linearized_at`.
- Retry time derives exactly from the immediately preceding ABANDONED terminal
  evidence `terminal_logical_instant`.
- CertificationV3 `certified_at` has one mandatory non-null value.
- Same ProofSet/event/attempt/root yields one Certification byte sequence.
- Transition and pre-terminal downstream time fields reuse the same scalar.
- Later token, Commitment, root, CAS, read-back, and terminal times remain
  successor-derived and unchanged.
- Crash after ProofSet reconstructs identical Certification/Transition bytes.
- Replay uses persisted evidence only and remains read-only.
- Certification remains predicate-only; no timestamp producer authority is
  introduced.
- The structural set remains 15 versions and one new family.
- Human, HIC/CHE, CRO, ordinary G70, owner, path, root, pointer, domain, and
  topology invariants are preserved.
- No implementation, instantiation, Ratification, publication, activation,
  BEGIN, root mutation, CDP, CLIA, deployment, or production action occurs.

## Not Verified

- No independent G70-03 assessment of Revision 4 has occurred.
- No Human Ratification, Certification of an instance, publication, or
  activation exists.
- No proposed Target, Instrument, ProofSet, Certification, Transition, Guard,
  root, terminal evidence, disposition, Receipt, or Dormancy is instantiated.
- No runtime schema, validator, persistence slot, crash recovery, Replay
  reader, clock guard, or test implements this derivation.
- No Candidate H/G76-specific executable test module is present.
- Existing hook, privacy, custody, external-evidence, deployment, and partial
  conformance limitations remain visible and unchanged.
- Proposal claims cannot serve as implementation or lifecycle authority.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| G48 structure | six required top-level sections and evidence subsections | heading review | `PASS` |
| authenticated repository | HEAD/tree/parent/subject and clean start | Git review | `PASS` |
| predecessor integrity | exact G77-62/G77-63 SHA-256 | hash review | `PASS` |
| single finding scope | G77-63 B04 certified-at defect only | scope review | `PASS` |
| time-source census | all required predecessor/later/live candidates classified | completeness review | `PASS` |
| no inferred attempt time | nonexistent values rejected | hostile review | `PASS` |
| initial source | exact disposition `linearized_at` | predecessor review | `PASS` |
| retry source | exact prior terminal `terminal_logical_instant` | predecessor review | `PASS` |
| two-row totality | initial/retry exact; unknown kind rejects | presence review | `PASS` |
| Certification uniqueness | same ProofSet/presence/source derives same bytes | identity review | `PASS` |
| no producer clock | live/wall/serialization time forbidden | authority review | `PASS` |
| Transition uniqueness | `effective_at == certified_at` | propagation review | `PASS` |
| downstream time equality | Census/CAP/Guard/Meta exact same scalar | propagation review | `PASS` |
| later times | token/root times remain successor-only | DAG review | `PASS` |
| Replay | persisted predecessor reconstruction only | Replay review | `PASS` |
| crash after ProofSet | identical source yields identical Certification | crash review | `PASS` |
| schema minimality | V3 corrected pre-adoption; no V4/new family | version review | `PASS` |
| structural count | 15 versions / one new family retained | count review | `PASS` |
| Authority DAG | no source/Human/Governance/root/Replay/CRO expansion | authority review | `PASS` |
| topology | exact preserved count matrix | topology review | `PASS` |
| Reuse Impact Assessment | five explicit Slovenian answers | completeness review | `PASS` |
| focused G69/G70 tests | 326 focused tests | test review | `PASS` |
| Candidate H/G76 tests | no directly named test module exists | explicit repository search | `NOT_APPLICABLE` |
| balanced fences/trailing whitespace | 26 fences; zero trailing-whitespace lines | format review | `PASS` |
| diff integrity | `git diff --check` plus untracked-file whitespace review | Git review | `PASS` |
| artifact count | exactly one G77-64 artifact | repository review | `PASS` |
| runtime/instantiation | prohibited proposal-only scope | scope review | `NOT_APPLICABLE` |
| independent Revision 4 assessment | later lifecycle step; not performed by this proposal | governance review | `NOT_APPLICABLE` |

# 5. Repository Mutation Summary

Modified files:

- added
  `docs/governance/G77_64_EXTERNAL_CONSTITUENT_CANDIDATE_H_INSTANTIATION_CONTRACT_CONSTITUTIONAL_DESIGN_PROPOSAL_REVISION_4_CERTIFICATION_TIME_CLOSURE_V1.md`
  as the sole G77-64 proposal-only artifact.

Unchanged subsystems:

- G77-63 and every predecessor;
- Target, Instrument, consumer-count, retry, terminal DAG, Authority DAG,
  topology, Replay structure, and the confirmed 15-successor set;
- Constitution, CAP/CDP/CLIA state, Human Authority, external authority, HIC,
  CHE, Governance runtime, Replay runtime, CRO, root persistence, release,
  deployment, routing, configuration, schemas, credentials, providers,
  production, and tests.

API compatibility:

- no API, model, serializer, validator, clock, command, route, workflow,
  owner, persistence, deployment, or runtime contract is implemented or
  activated.

Boundary preservation:

- this artifact is an unassessed proposal only;
- it creates no Human, external, Certification-selection, Ratification,
  instantiation, implementation, publication, activation, BEGIN,
  root-mutation, deployment, or production authority;
- Replay remains read-only and CRO remains passive; and
- topology remains one production path and zero parallel paths.

Unrelated pre-existing changes:

- None observed. The worktree was clean at proposal start.

# 6. Certification Verdict

G77_CANDIDATE_H_INSTANTIATION_CONTRACT_REVISION_4_CERTIFICATION_TIME_CLOSURE_ESTABLISHED
