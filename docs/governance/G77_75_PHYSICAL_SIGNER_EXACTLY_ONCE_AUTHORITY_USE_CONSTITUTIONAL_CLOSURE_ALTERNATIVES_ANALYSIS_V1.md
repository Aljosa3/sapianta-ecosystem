# 1. Implementation Summary

Generation: G77-75

Report identity:
`G77_75_PHYSICAL_SIGNER_EXACTLY_ONCE_AUTHORITY_USE_CONSTITUTIONAL_CLOSURE_ALTERNATIVES_ANALYSIS_V1`

Artifact class:
`CONSTITUTIONAL_CLOSURE_ALTERNATIVES_ANALYSIS_AND_DESIGN_SELECTION_NON_IMPLEMENTING_NON_ACTIVATING`

Controlling assessment:
`G77_74_INDEPENDENT_CONSTITUTIONAL_IMPACT_ASSESSMENT_CANDIDATE_H_AUTHENTICATION_REDESIGN_REVISION_3_V1`

Controlling blocker:
`G77_73_B01_AUTHORITY_BEARING_PHYSICAL_SIGNER_USE_AT_MOST_ONCE_NOT_PROVED`

Analysis status: `DESIGN_SELECTION_ONLY_UNASSESSED`

Constitutional baseline: authenticated committed G0 through G77-74.

Reporting date: 2026-08-10.

Repository identity at analysis start:

- branch: `master`;
- commit: `d4e90ca1977edb8033cd1f02e556b134fb5d72d4`;
- tree: `b35f7bc053d5490d0673cb3a7cd4bbeb7691d494`;
- subject: `G77-74: assess Candidate H authentication redesign revision 3`;
- G77-74 status: committed and tracked at HEAD; and
- worktree status: clean.

Objective:

Analyze independent closure alternatives and select, if possible, the
minimum constitutionally sufficient trusted boundary proving
`MAX_AUTHORITY_BEARING_PHYSICAL_SIGNER_USES_PER_OPERATION <= 1` under crash,
restart, lost response, local software, HSM, and remote-signer conditions.

This analysis does not repair G77-73, define a final ResultV3 schema,
implement a signer, perform a signature, create a Human act, activate
Candidate H, execute BEGIN, mutate a root, deploy, grant authority, or commit.

## Authenticated Predecessors

| Artifact | SHA-256 | Role |
|---|---|---|
| G48-00 | `16508d1a77c4b3f07d37861e74d85f77896be16da01ca26cbc07a658ddf2c0eb` | reporting standard |
| G76-06 | `29f06a93d5b7ce610c161487bc1e3a01f6d7d063b22393e0347b0da20b281dbc` | identity/DAG control |
| G77-72 | `90e990d95b5a855643fd032ccee2b7a6f7300496fc16fb0d3f2eb27825369639` | Revision 2 hostile assessment |
| G77-73 | `6a6c24bbb86344d76d1f38fa364462fd601e5313400564016dd39cc0b90af586` | Revision 3 logical signer proposal |
| G77-74 | `490107bac26ce2baa356f75ca3a32a1e1c302b25b5773054ddd40cd913b529cd` | controlling physical-use blocker |

The hashes match independently recomputed repository bytes. Repository state
is consistent.

## Exact Constitutional Authority Units

The following units are distinct:

| Unit | Exact meaning | Required ceiling |
|---|---|---:|
| logical signer operation identity | one content-derived message/key/capacity/slot operation | <= 1 |
| logical signer invocation | one accepted signer-owned execution authorization | <= 1 |
| physical private-key primitive execution | one actual invocation of the signing primitive with the private key | <= 1 |
| authority-bearing signer use | one physical exercise of the one-shot signing authority | <= 1 |
| signature-byte production | one physical production of the signature result | <= 1 |
| constitutional signature exposure | one durable publication identity for an admissible signature | <= 1 |
| durable outcome persistence | one terminal outcome identity/read-back | <= 1 |
| admissible signature result | one Result/HumanDecision-consumable signature | <= 1 |

Repeated read-only delivery of the same finalized exposure artifact is Replay,
not a new constitutional exposure. It does not authorize a new result or
private-key use. A distinct publication identity, different signature bytes,
or a new signing operation would be a second exposure and is forbidden.

G77-74's physical-use unit remains constitutionally correct. The one-shot
Founder key is an authority-bearing capability, not merely a deterministic
function. Exercising that capability twice is repeated authority use even
when Ed25519 produces the same bytes. Defining the invariant only over one
accepted authorization or one admissible result would hide repeated key use,
weaken auditability, admit non-idempotent HSM/remote behavior, and make Replay
unable to account for actual authority exercise.

This result is not selected merely to keep G77-74 controlling. It follows
from the distinct responsibilities of Human intent, authorization, physical
key custody, result evidence, and publication. One Human intent may authorize
at most one physical exercise and at most one admissible result.

Authority-unit verdict:
`PHYSICAL_PRIVATE_KEY_USE_REMAINS_REQUIRED_CONSTITUTIONAL_UNIT`.

## Ordinary Sign-Then-Store Impossibility Result

Consider ordinary software with two non-atomic operations:

~~~text
signature = private_key_operation(message)
durable_store(operation_id, signature)
~~~

Let persisted state before both histories be the same accepted signer receipt
with no outcome:

~~~text
H0: crash immediately before private_key_operation
H1: private_key_operation completes; crash immediately before durable_store
~~~

After restart, H0 and H1 have identical persisted bytes. Any deterministic
recovery must choose the same action for both:

- retry signing: correct for H0, but performs a second physical use in H1;
- do not retry: preserves at-most-once in H1, but cannot complete H0; or
- infer success/failure: invents evidence absent from both histories.

No algorithm reading only that persisted state can both recover completion
and prove at-most-once physical use. Repeating the crash after every physical
computation permits unbounded physical uses under one logical operation.

Therefore ordinary `private_key_operation(); durable_store()` cannot prove
exactly-once physical private-key use across an arbitrary crash between those
operations. At-most-once safety is possible only by consuming/fencing the
one-use authority before the primitive and forbidding every recovery retry,
or by moving computation and durable outcome into a stronger trusted atomic
boundary.

Deterministic Ed25519 changes only output equality:

~~~text
same key + same message -> same signature bytes
~~~

It does not change:

~~~text
physical private-key executions: 1 != 2
authority-bearing signer uses: 1 != 2
~~~

Impossibility verdict:
`ORDINARY_SIGN_THEN_STORE_EXACTLY_ONCE_PHYSICAL_USE_IMPOSSIBLE`.

## Candidate Closure Comparison

High-level result:

| Candidate | Physical-use proof | Crash closure | Replay | Machinery/trust | Verdict |
|---|---|---|---|---|---|
| A atomic sign-and-persist | sufficient only inside certified indivisible boundary | complete if atomicity includes power loss | exact | strongest transactional signer boundary | sufficient but larger than necessary |
| B device-owned idempotent operation | insufficient unless device also prevents internal recomputation | conditional | conditional | device operation registry | reject alone |
| C durable execution receipt | insufficient if merely started/completed; sufficient only when pre-use consumption is fail-stop | conditional | conditional | signer-owned receipt/state | useful component, not selected alone |
| D one-use key/destruction | sufficient when nonduplicable key capability is atomically consumed before use | fail-stop complete | exact maximum | certified one-use key boundary | sufficient but hardware mechanism is one implementation of selected G |
| E precommitted signature material | cannot bind unknown Human decision without pre-exercising authority or new cryptography | underclosed | underclosed | new cryptographic protocol | reject |
| F restrict signer class | necessary to enforce any physical-use invariant but not a complete protocol alone | depends on admitted class | conditional | certification profile | necessary constraint, not standalone selection |
| G certified fail-stop pre-use authority consumption | sufficient for <= 1; sacrifices retry liveness | complete and fail-closed | exact maximum/outcome | smallest exclusive key-custody boundary | selected |

### Candidate A — Atomic sign-and-persist

The physical primitive and terminal outcome persistence would be one
indivisible operation. Crash before the atomic boundary yields no use; crash
after yields one durable result. Response loss reads the result. Repeated
delivery returns it without another use.

This is sufficient only if atomicity is enforced inside the same trusted
boundary that owns the private key and survives power/process/device failure.
A database transaction outside the signer is insufficient. TPM/HSM/remote
services qualify only through an exact certified atomic contract. Ordinary
local software does not.

Required evidence: atomic operation identity, device identity/profile,
predecessor state, exact message/key, terminal outcome, atomicity
certification, and authoritative read-back. It needs no new constituent
authority or production path but adds a stronger transactional signer
boundary. It preserves liveness but is stronger and more implementation-heavy
than at-most-once safety requires.

### Candidate B — Device-owned idempotent signer operation

A device/service accepting an operation identity and returning the same stored
outcome on repeated delivery closes response loss only if the device never
re-executes the physical primitive internally. A logical idempotency table
outside the crypto engine recreates G77-73. An internal crash after physical
use but before the device outcome store recreates the same impossibility.

Therefore B is conditionally sufficient only when it incorporates A or G
inside the device. Idempotent API behavior alone does not prove physical-use
cardinality. No separate family is justified for an insufficient abstraction.

### Candidate C — Signer-owned durable execution receipt

A `STARTED` receipt written before physical use distinguishes unaccepted from
accepted execution but does not by itself prevent retry after crash. A
`COMPLETED` receipt written after physical use has the sign-then-store gap.

C becomes sufficient only if the pre-use receipt consumes the authorization,
the signer has exclusive key access, only the CAS-winning live execution
context can receive a nonduplicable capability, and restart is prohibited
from obtaining another capability. That strengthened C is the selected G
model. A receipt without enforcement is evidence prose, not a ceiling.

### Candidate D — One-use key or key destruction

A dedicated one-shot key can be atomically disabled for future grants before
one volatile execution capability is released. Crash before physical use may
waste the key; crash during/after use loses liveness but no second capability
can be issued. A terminal consumed/abandoned receipt makes Replay safe.

This is sufficient when key non-exportability, exclusive custody, atomic
disablement, and nonduplicable capability release are certified. Simple
software deletion is not proof because copies may exist. D is a valid HSM/TPM
realization of G, not a required separate constitutional family.

### Candidate E — Precommitted or deterministic material

The exact message includes the Human act/review and `P_auth_v2`; it does not
exist before Human choice. Precomputing a complete signature would either
pre-exercise authority over an unknown message, introduce a new threshold/
adaptor-signature protocol, or leave a later authority-bearing completion
step with the same crash problem. Deterministic Ed25519 supplies repeatable
output, not recoverable non-authority-bearing signature material.

E adds new cryptographic assumptions, verification semantics, and likely
families without proving a smaller safe boundary. It is rejected.

### Candidate F — Narrow certified signer class

Implementation neutrality cannot include ordinary sign-then-store software,
an HSM exposing only non-idempotent `sign`, or a remote service without
device-owned durable consumption/outcome evidence. The admissible signer class
must be narrowed to a certified exactly-once-authority-use profile.

F is necessary but not sufficient alone: the admitted profile still needs an
exact state/evidence protocol. G supplies that protocol. No machine, device,
or service gains constituent authority by meeting the profile; it receives
only one bounded execution capability for the exact already-authorized act.

### Candidate G — Certified fail-stop pre-use authority consumption

G is the strictly smaller sufficient model selected by this analysis.

The minimum trusted boundary is one signer-owned exclusive key-custody
enforcement boundary with:

1. no alternate private-key access or export path;
2. one exact operation/key/message/slot identity;
3. one durable atomic `AVAILABLE -> USE_GRANTED_ACTIVE` consumption CAS;
4. one authoritative consumption receipt/read-back before physical signing;
5. one nonduplicable, nonpersistent execution capability released only to the
   CAS-winning live signer context;
6. at most one physical primitive call through that capability;
7. capability invalidation after use, process loss, device restart, or
   terminal outcome;
8. no recovery grant, recomputation, or second device command;
9. write-before-exposure terminal outcome/read-back when success persists;
10. signer-owned `USE_ABANDONED_FINAL` read-back when the active capability is
    irrecoverably gone without a durable outcome; and
11. caller read-only recovery throughout.

The signer-owned slot is:

~~~text
AVAILABLE
  -> USE_GRANTED_ACTIVE
  -> USE_COMPLETED_FINAL

USE_GRANTED_ACTIVE
  -> USE_ABANDONED_FINAL
~~~

`USE_COMPLETED_FINAL` and `USE_ABANDONED_FINAL` are terminal. No transition
returns to AVAILABLE. Only the trusted signer boundary may determine that its
nonduplicable active capability is destroyed and persist ABANDONED. Caller
timeout, response loss, wall clock, process guess, or missing outcome cannot
terminalize it.

Crash behavior is exact:

| Boundary | Persisted state | Physical-use maximum | Recovery |
|---|---|---:|---|
| before consumption CAS | AVAILABLE | 0 | same CAS may be submitted |
| CAS response lost | AVAILABLE or USE_GRANTED_ACTIVE | 0 or 1 permitted | authoritative signer-slot read-back |
| after grant before physical use | USE_GRANTED_ACTIVE | <= 1 | original live capability may continue; restart never receives another |
| during physical use | USE_GRANTED_ACTIVE | <= 1 | no retry; await device finalization or ABANDONED |
| after physical use before outcome | USE_GRANTED_ACTIVE | 1 | no retry; persist existing outcome if same live context can, otherwise ABANDONED |
| outcome persisted, response lost | USE_COMPLETED_FINAL | 1 | return identical outcome/read-back |
| process/device restart without outcome | USE_GRANTED_ACTIVE then signer-owned ABANDONED | 0 or 1 | terminal indeterminate/exhausted; never sign |
| repeated restart | terminal COMPLETED or ABANDONED | <= 1 | read only |
| HSM/remote response loss | device-owned state is authoritative | <= 1 | caller reads; never reissues sign command |

The model proves a maximum, not guaranteed liveness. If the one-use capability
is consumed but no durable signature outcome survives, the only lawful result
is indeterminate permanent exhaustion. Wasting the one-shot opportunity is a
deliberate fail-closed tradeoff and is smaller than atomic sign-and-persist.

## Selected Constitutional Model and Contract Impact

Selected model token:

`CERTIFIED_FAIL_STOP_PRE_USE_AUTHORITY_CONSUMPTION_V1`

Selection verdict:
`PHYSICAL_SIGNER_EXACTLY_ONCE_CLOSURE_MODEL_SELECTED`.

The selected trusted boundary is not an ordinary process plus database. It is
the exclusive signer/key-custody enforcement boundary that owns both the
one-use slot and access to the private-key primitive. A local implementation
is eligible only if it can certify exclusive key access and nonduplicable
capability semantics; ordinary exportable-key software is ineligible. A TPM,
HSM, remote signer, or Human-controlled signing device is eligible only if its
certified contract implements the exact G state machine and read-back.

Projected contract impact for a later repair generation:

| Contract | Impact | Exact reason |
|---|---|---|
| CapacityV2 | unchanged | already binds exact key, one-shot scope, owner, and verification profile |
| ResultV2 | `VERSION_SUCCESSOR_REQUIRED` as future ResultV3 | must bind consumption CAS/receipt, certified signer profile, capability terminal status, and no-retry outcome |
| HumanDecisionV2 | unchanged schema/version | result pair is version-opaque and remains forward |
| HFD-04 P_auth_v2 | unchanged | same exact Human-authenticated message |
| P012 | contract-token successor semantics only | require exact ResultV3 consumption/outcome proof |
| ProofSetV3 | unchanged artifact version | existing identity-bearing contract_version dispatch |
| CertificationV3 | unchanged artifact version | consumes exact ProofSet pair/token |
| TransitionV3 | unchanged artifact version | consumes exact Certification/ProofSet pairs |
| Replay | validator/dispatch extension only | reconstruct consumption, completion/abandonment, and maximum proof |
| CRO | unchanged | passive observation only |

The future ResultV3 responsibility can contain one complete nested
`SignerAuthorityUseConsumptionReceiptV1` subcontract. It is not independently
selected as a new top-level family because it has no authority, lifecycle, or
consumer outside the one Result operation. The signer slot is an external
CAS/read-back subcontract, not a new internal State family. The exact ResultV3
field schema is deliberately not designed here because G77-75 selects an
architecture and does not repair G77-73.

Projected machinery delta relative to G77-73:

~~~text
new artifact-version successors = 1  # future ResultV3
new top-level artifact families = 0
new nested signer execution evidence subcontracts = 1
new State families = 0
new verification families = 0
new owners = 0
new constituent authorities = 0
new root fields = 0
new root serialization domains = 0
new production paths = 0
new parallel paths = 0
new persistent founding paths = 0
new certified signer implementation profiles = 1
~~~

The complete redesign lineage would contain four successor contracts when a
future ResultV3 is defined: HumanDecisionV2, CapacityV2, ResultV2 history, and
ResultV3. Only the latest eligible versions would be admitted by the future
contract token; failed predecessors remain immutable history.

## Consumer, Identity, Authority, Replay, and One-Shot Impact

The current thirty-group consumer graph remains independently unchanged:

| # | Current consumer group | Selected-model classification | Reason |
|---:|---|---|---|
| 1 | External Premise | `UNCHANGED_REUSE` | predecessor of capacity/signer authority only |
| 2 | SourceCommitmentV1 | `UNCHANGED_REUSE` | Target pair only |
| 3 | InstrumentCommitmentV3 | `UNCHANGED_REUSE` | no signer-result field |
| 4 | UniverseV1 / CandidateCensusV1 | `UNCHANGED_REUSE` | pair closure only |
| 5 | SourceEvidenceV1 / RecognitionProofV1 | `UNCHANGED_REUSE` | external evidence pairs unchanged |
| 6 | NormativePayloadV1 / TargetV5 | `UNCHANGED_REUSE` | predecessor of HumanDecision |
| 7 | InstrumentV4 | `UNCHANGED_REUSE` | predecessor of HumanDecision |
| 8 | HumanDecisionV1 | `VERSION_SUCCESSOR_REQUIRED` | retained current redesign successor is HumanDecisionV2 |
| 9 | HumanFinalityV1 | `UNCHANGED_REUSE` | decision pair version-opaque |
| 10 | DispositionEvidence V2/V3 | `UNCHANGED_REUSE` | exact pair/status equality |
| 11 | external status/current version/snapshot | `UNCHANGED_REUSE` | explicit resolved rows |
| 12 | ProofSetV3 | `UNCHANGED_REUSE` | identity-bearing contract token |
| 13 | CertificationV3 | `UNCHANGED_REUSE` | exact ProofSet pair/token |
| 14 | FoundingTransitionV3 | `UNCHANGED_REUSE` | exact predecessor pairs |
| 15 | FenceV1 / BEGIN CAS | `UNCHANGED_REUSE` | pair-opaque |
| 16 | OperationSeed/token/AllocationIntentV2 | `UNCHANGED_REUSE` | generic immutable inputs |
| 17 | ALLOCATED CoordinatorStateV2 | `UNCHANGED_REUSE` | allocation unchanged |
| 18 | allocation CAS/marker/read-back/Receipt | `UNCHANGED_REUSE` | generic root serialization |
| 19 | LogicalPointer/Projection/Manifest/route Censuses | `UNCHANGED_REUSE` | no signer interpretation |
| 20 | ordinary-chain CensusV2 | `UNCHANGED_REUSE` | Target/route closure unchanged |
| 21 | CAP Reachability StateV2 | `UNCHANGED_REUSE` | Census/Target unchanged |
| 22 | Dormancy Rebase GuardV2 | `UNCHANGED_REUSE` | Transition remains V3 |
| 23 | MetaRepairTransitionV3 | `UNCHANGED_REUSE` | Guard remains V2 |
| 24 | MetaRepairStateV3 | `UNCHANGED_REUSE` | fixed versions unchanged |
| 25 | failure Census/FailureEvidenceV2 | `UNCHANGED_REUSE` | pair-opaque failure reduction |
| 26 | terminal CommitmentV3 | `UNCHANGED_REUSE` | downstream versions unchanged |
| 27 | consuming operation/ConsumeIntentV2 | `UNCHANGED_REUSE` | commitment pair opaque |
| 28 | terminal CoordinatorV4 / RootSnapshotV4 | `UNCHANGED_REUSE` | fixed terminal versions unchanged |
| 29 | terminal CAS/read-back/AttemptTerminalReadBack/Disposition/Receipt/Dormancy | `UNCHANGED_REUSE` | pair comparison only |
| 30 | Replay / CRO | `UNCHANGED_REUSE` | read-only/passive with explicit dispatch |

Exact current counts remain:

~~~text
current consumer groups = 30
unchanged current consumer groups = 29
current consumer-family successors = 1
~~~

The selected future ResultV3 is a predecessor correction inside the
authentication result responsibility and does not force a consumer-group
schema successor because HumanDecisionV2 carries an exact version-opaque
result pair and P012 uses identity-bearing contract dispatch.

Selected identity DAG:

~~~text
accepted Premise -> CapacityV2 -> HFD act/review -> P_auth_v2
-> logical operation/claim/acceptance
-> certified signer profile + exact use-consumption intent
-> signer-owned AVAILABLE-to-USE_GRANTED_ACTIVE CAS/read-back
-> at most one nonduplicable physical-use capability
-> one physical signer use or no use
-> USE_COMPLETED_FINAL outcome/read-back
   OR USE_ABANDONED_FINAL indeterminate read-back
-> future ResultV3 -> HumanDecisionV2 -> P012/ProofSetV3
-> CertificationV3 -> TransitionV3 -> retained root/terminal chain
-> Replay -> CRO
~~~

The use-consumption intent excludes its CAS, capability, physical result,
outcome, ResultV3, HumanDecision, and successors. The CAS binds only finalized
intent/predecessors. Outcome or abandonment binds the consumption receipt.
ResultV3 derives afterward. No capability bytes are persisted or exposed.

| Identity property | Selected-model verdict |
|---|---|
| `FINITE` | `PASS_SELECTION` |
| `ACYCLIC` | `PASS_SELECTION` |
| `FORWARD_DERIVED` | `PASS_SELECTION` |
| `BYTE_DETERMINISTIC` | `PASS_SELECTION` |
| `DOMAIN_SEPARATED` | `PASS_SELECTION` |
| `REPLAY_RECONSTRUCTIBLE` | `PASS_SELECTION` |

Replay reconstructs the maximum proof, not an unknowable exact 0/1 physical
count after abandonment. The consumption receipt plus exclusive non-regrant
contract proves the set of possible histories is `{0, 1}`, never greater than
1. A completed outcome proves one use and exact bytes. An abandoned receipt
proves permanent consumption with no admissible signature, whether the
physical primitive ran zero or one time before loss. That is sufficient for
the constitutional ceiling and Replay.

Selected authority DAG:

~~~text
external constituent authority -> accepted Premise -> CapacityV2
-> Human one-shot choice -> exact physical-use authorization
-> certified signer boundary consumes one capability
-> at most one physical key use

HUMAN_AUTHORITY -> HumanDecision/Finality custody only
Certification -> predicates only
Governance/root -> retained mechanics only
Replay/CRO -> read-only/passive
~~~

The signer boundary does not receive constituent authority. It receives one
nontransferable execution capability for the exact already-authorized
message/key/operation. HSM status, device ownership, valid signature, key
possession, repository ownership, Governance, Certification, Replay, or root
success cannot select a disposition or create a new authority edge. Abandoned
consumption permanently destroys the capability; it does not create persistent
Founder authority.

Authority DAG verdict: `PASS_SELECTION`.

Crash/retry verdict: `PASS_SELECTION_FAIL_STOP_NO_RETRY`.

Replay verdict: `PASS_SELECTION`.

One-shot verdict: `PASS_SELECTION` for all required ceilings, conditional on
a future exact ResultV3 contract and independent assessment.

## Machinery Minimality, Topology, and Reuse Impact Assessment

The selected G model is smaller than A because it does not require successful
signing and outcome persistence to be atomic. It is stronger than bare B/C/F
because the trusted boundary actually consumes a nonduplicable capability and
forbids restart grants. D is a valid realization but not required as a
separate family or a universally fixed hardware technology. E is unnecessary.

Removing exclusive key custody permits bypass. Removing pre-use consumption
recreates sign-then-store ambiguity. Removing nonduplicable capability
semantics permits concurrent/restart use. Removing terminal completion/
abandonment read-back breaks Replay. Allowing retry after consumption breaks
the physical ceiling. Adding atomic sign-and-persist, a new top-level family,
State family, verification family, owner, authority, or root domain would not
close an additional requirement. The selected model is therefore the minimum
safe architecture found.

Topology:

| Measure | Before | Selected future model | Delta |
|---|---:|---:|---:|
| production paths | 1 | 1 | 0 |
| parallel paths | 0 | 0 | 0 |
| persistent founding paths | 0 | 0 | 0 |
| Human entry points | 1 | 1 | 0 |
| HIC families | 1 | 1 | 0 |
| CHE definitions | 1 | 1 | 0 |
| root paths | 1 | 1 | 0 |
| persistent founding authorities | 0 | 0 | 0 |

1. **Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?**

   Ponovno se uporabijo sprejeti Premise in CapacityV2, HFD-04
   `P_auth_v2`, logična operation/claim/acceptance evidenca, zunanji
   CAS/read-back vzorec, HumanDecisionV2, HumanFinality, P012 contract-version
   dispatch, ProofSetV3, CertificationV3, TransitionV3, Fence/BEGIN,
   CAP/Guard/MetaRepair, korenska pot, HIC/CHE ter pasivni Replay/CRO.
   Nespremenjeno ostane 29 trenutnih potrošniških skupin.

2. **Katere nove zmogljivosti (če sploh) nastanejo?**

   Izbrana je ena nova certificirana signer implementacijska pogodba:
   ekskluzivna hramba ključa, trajna poraba pred uporabo, nedvojljiva enkratna
   zmožnost ter dokončni completed/abandoned read-back. Prihodnji ResultV3 bi
   vseboval eno vgnezdeno execution-evidence podpogodbo. Nova vrhnja, State ali
   verification družina ni potrebna.

3. **Ali katera obstoječa zmogljivost postane nedosegljiva?**

   Generični exportable-key sign-then-store signer, ne-idempotentni HSM in
   oddaljeni signer brez device-owned consumption/read-back pogodbe postanejo
   namenoma neupravičeni. Obstoječe ustavne zmogljivosti in Candidate H
   potrošniki ne postanejo nedosegljivi; Candidate H ostaja neaktiviran do
   prihodnjega popravka in neodvisne presoje.

4. **Ali implementacija ustvarja vzporedni tok?**

   Ne. Implementacije ni. Izbrani signer boundary je dokazni predhodnik na
   istem authentication/Candidate H toku, ne nov Human, HIC/CHE ali korenski
   tok.

5. **Ali zmanjšuje ali povečuje število produkcijskih poti?**

   Ne. Ostane ena produkcijska pot, nič vzporednih in nič trajnih
   ustanovitvenih poti.

## Required Effect Classifications

| Required classification | Analysis-only result |
|---|---|
| `INTERNAL_CONSTITUTIONAL_DESIGN_MUTATION` | `NO` |
| `CONSTITUENT_AUTHORITY_CREATED` | `NO` |
| `EXTERNAL_CONSTITUENT_ACT_PERFORMED` | `NO` |
| `HUMAN_DISPOSITION_SELECTED` | `NO` |
| `CRYPTOGRAPHIC_SIGNATURE_PERFORMED` | `NO` |
| `CONSTITUTION_ADOPTED` | `NO` |
| `CONSTITUTION_ACTIVATED` | `NO` |
| `IMPLEMENTATION_AUTHORITY_GRANTED` | `NO` |
| `PRODUCTION_AUTHORITY_GRANTED` | `NO` |
| `FOUNDER_POST_FOUNDING_SPECIAL_AUTHORITY` | `NO` |
| `NEW_PRODUCTION_PATHS` | `NO` |
| `NEW_PARALLEL_PATHS` | `NO` |
| `NEW_PERSISTENT_FOUNDING_PATHS` | `NO` |

# 2. Code Evidence

## Public API

No API is implemented. The selected future constitutional surface is one
certified signer profile, one nested physical-use consumption receipt inside
a future ResultV3 responsibility, and retained version-opaque consumers.

## Orchestration Entry Point

No runtime entry point is created. The selected order is:

~~~text
logical acceptance -> signer-owned pre-use consumption/read-back
-> at most one nonduplicable physical capability
-> durable outcome OR terminal abandonment
-> future ResultV3
~~~

## Semantic Reductions

Impossibility:

~~~text
sign then store + crash between -> identical persisted histories
-> retry can repeat physical use
~~~

Selected reduction:

~~~text
consume/fence authority before sign
+ release one nonduplicable live capability
+ never regrant after crash
-> physical signer uses in {0, 1}
~~~

## Public Validators

No validator is implemented. A future validator must reject ordinary
sign-then-store, exportable alternate key paths, non-device-owned idempotency,
missing consumption receipt/read-back, restart capability grants, caller
terminalization, missing completion/abandonment, ResultV2, and an unknown
future P012 contract token.

## Canonical Data Models

Selection-level models:

~~~text
certified signer profile = CERTIFIED_FAIL_STOP_PRE_USE_AUTHORITY_CONSUMPTION_V1
future artifact successor = ResultV3
nested execution-evidence subcontract = 1
new top-level families = 0
new State families = 0
new verification families = 0
current consumer groups = 30
unchanged current consumer groups = 29
current consumer-family successors = 1
~~~

## Deterministic Algorithms

1. Resolve one accepted logical signer operation.
2. Validate exclusive key custody and certified signer profile.
3. CAS AVAILABLE to USE_GRANTED_ACTIVE and read it back.
4. Release one nonduplicable capability to the winning live context.
5. Permit at most one physical private-key execution.
6. Persist and read one completed outcome before exposure, or have the signer
   boundary finalize ABANDONED after capability destruction.
7. Never grant, invoke, or recompute after consumption.
8. Replay validates the terminal maximum proof read-only.

## Responsibility Boundaries

| Responsibility | Exact boundary | Prohibited substitution |
|---|---|---|
| Human authority use | exact one-shot Human act/capacity | no signer choice |
| logical acceptance | existing external registry | no physical-use inference |
| physical-use enforcement | certified exclusive key-custody signer | no caller/database-only claim |
| outcome/abandonment | same signer boundary | no timeout/Human inference |
| Result/P012 validation | future ResultV3/P012 contract | no authority creation |
| Replay/CRO | read-only/passive | no capability grant or repair |

## Repository Evidence

Evidence consists of committed G77-72/G77-73/G77-74 bytes, controlling
identity/reporting artifacts, the concrete indistinguishable-history crash
counterexample, seven explicit candidate analyses, independently reconstructed
consumer counts, focused tests, and exact mutation checks. No signer, key,
signature, external instance, Human act, root effect, or implementation
exists.

# 3. Constitutional Self-Assessment

## Verified in Alternatives Analysis

- G77-74 is committed and controlling hashes match repository bytes.
- Logical operation, physical use, byte production/exposure, and outcome
  persistence are explicitly distinct.
- All required constitutional ceilings are retained at one.
- Ordinary sign-then-store exactly-once physical use has a concrete crash
  impossibility proof.
- Deterministic Ed25519 output equality does not collapse physical uses.
- Physical key use remains the correct one-shot authority unit.
- Candidates A through G are independently compared.
- A, strengthened D, and selected G can enforce the ceiling under exact trusted
  boundaries; B/C/F alone and E do not.
- G is the smallest sufficient model because it permits fail-stop abandonment
  instead of requiring atomic successful sign-and-persist.
- The selected boundary excludes generic local software and non-idempotent
  external signers unless they satisfy the certified profile.
- CapacityV2, HumanDecisionV2, P_auth_v2, ProofSetV3, CertificationV3,
  TransitionV3, Replay role, and CRO role retain their schemas/versions.
- A future ResultV3 and future identity-bearing P012 contract token are the
  only projected contract changes.
- Current consumer counts remain 30 / 29 / 1.
- The selected identity and authority DAGs are finite, acyclic, forward,
  deterministic, separated, and Replay-reconstructible at selection level.
- No new top-level family, State family, verification family, owner,
  authority, root field/domain, or path is selected.
- Topology remains 1 / 0 / 0.
- Every analysis-only effect classification remains `NO`.

## Not Verified or Performed

- No future ResultV3 exact field schema, identity formulas, P012 contract
  token, or complete crash matrix is proposed in this alternatives analysis.
- No independent assessment of the selected model has occurred.
- No local process, TPM, HSM, remote signer, or Human-controlled device has
  demonstrated exclusive key custody, atomic consumption, nonduplicable
  capability, completion, or abandonment behavior.
- No runtime schema, validator, signer adapter, storage primitive, device
  certification, Replay implementation, or test implements the model.
- No operational liveness is promised after capability consumption.
- No Candidate H/G76-specific executable test module exists.
- No Human Ratification, implementation authorization, publication,
  activation, deployment, or production authority exists.
- Known hook drift and partial conformance remain visible and unchanged.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| repository HEAD/tree/clean start | exact Git objects/status | Git inspection | `PASS` |
| G77-74 committed immutability | tracked HEAD subject | Git inspection | `PASS` |
| G77-72/G77-73/G77-74 hashes | exact repository bytes | SHA-256 | `PASS` |
| controlling blocker retained | G77-74 physical-use finding | predecessor review | `PASS` |
| seven units distinguished | exact responsibility table | semantic review | `PASS` |
| four minimum ceilings | explicit <= 1 requirements | invariant review | `PASS` |
| physical authority-unit challenge | Human/key/audit consequences | hostile review | `PASS` |
| ordinary sign-then-store impossibility | H0/H1 indistinguishable histories | crash counterexample | `PASS` |
| deterministic Ed25519 distinction | same bytes versus repeated use | algorithm review | `PASS` |
| candidate A | atomic boundary analysis | alternatives review | `PASS` |
| candidate B | device idempotency limitation | alternatives review | `PASS` |
| candidate C | receipt limitation/strengthening | alternatives review | `PASS` |
| candidate D | one-use key realization | alternatives review | `PASS` |
| candidate E | precommit rejection | alternatives review | `PASS` |
| candidate F | signer-class restriction | alternatives review | `PASS` |
| candidate G | fail-stop pre-use model | alternatives review | `PASS` |
| selected model correctness | physical-use set {0,1} | hostile crash review | `PASS` |
| selected model Replay | completed/abandoned read-back | Replay review | `PASS` |
| selected model one-shot | no regrant/recompute | lifecycle review | `PASS` |
| exact trusted boundary | exclusive key custody plus one-use capability | trust review | `PASS` |
| Result contract impact | future ResultV3 required | transitive review | `PASS` |
| P012 impact | future contract-token semantics only | version review | `PASS` |
| current consumer graph | thirty classified rows | independent count | `PASS` |
| current reuse/successor counts | 29 unchanged / 1 current successor | count review | `PASS` |
| identity DAG six properties | selected forward graph | DAG review | `PASS` |
| authority DAG | bounded execution without authority creation | authority review | `PASS` |
| machinery delta | one successor/profile/subcontract, no new family/path | minimality review | `PASS` |
| topology | exact before/after matrix | graph review | `PASS` |
| Reuse Impact Assessment | five Slovenian answers | completeness review | `PASS` |
| focused G69/G70 tests | 326 existing tests | pytest | `PASS` |
| Candidate H/G76 tests | no directly named module present | test inventory | `NOT_APPLICABLE` |
| G48 six top-level sections | exact names/order/count | structure validation | `PASS` |
| eight Code Evidence subsections | exact names/count | structure validation | `PASS` |
| Markdown fence balance | paired fence count | format validation | `PASS` |
| zero trailing whitespace | line scan | format validation | `PASS` |
| tracked/untracked whitespace | Git/no-index checks | diff validation | `PASS` |
| exact G77-75 mutation | one new governance artifact | mutation inventory | `PASS` |
| predecessor/runtime/test/config/root/production mutation | no changed prohibited path | mutation inventory | `PASS` |
| implementation/activation/act/signature/BEGIN/root/deployment/commit | analysis-only boundary | scope review | `NOT_APPLICABLE` |

# 5. Repository Mutation Summary

Modified files:

- added
  `docs/governance/G77_75_PHYSICAL_SIGNER_EXACTLY_ONCE_AUTHORITY_USE_CONSTITUTIONAL_CLOSURE_ALTERNATIVES_ANALYSIS_V1.md`
  as the sole alternatives-analysis artifact.

Unchanged subsystems:

- G77-74, G77-73, G77-72, and every controlling predecessor;
- CapacityV2, ResultV2, HumanDecisionV2, HFD-04 `P_auth_v2`, P012,
  HumanFinality, ProofSetV3, CertificationV3, TransitionV3, Fence/BEGIN,
  CAP/Guard/MetaRepair, root contracts, HIC/CHE, Replay, and CRO;
- runtime, signer/HSM integrations, schemas, validators, tests, config,
  credentials, providers, root persistence, release, deployment, and
  production.

API compatibility:

- no API, ResultV3 schema, P012 token, runtime model, validator, serializer,
  signer profile implementation, device integration, store, route, command,
  workflow, owner, root schema, or deployment contract is created or changed;
- the selected model is an input to a later proposal, not a repair; and
- selection grants no implementation or production authority.

Boundary preservation:

- alternatives analysis/design selection only;
- no repair to G77-73;
- no key, signature, external evidence instance, Human act/disposition,
  HumanDecision, Finality, P012 result, BEGIN, root mutation, activation,
  authority grant, deployment, or production effect;
- Replay remains read-only, CRO passive, HIC/CHE transport-only, and
  `HUMAN_AUTHORITY` custody-only; and
- topology remains one production path, zero parallel paths, and zero
  persistent founding paths.

Unrelated pre-existing changes:

- None observed. The worktree was clean at analysis start.

Worktree mutation count attributable to this task: `1` new governance file,
`0` modified existing files.

No commit is created.

# 6. Certification Verdict

PHYSICAL_SIGNER_EXACTLY_ONCE_CLOSURE_MODEL_SELECTED
