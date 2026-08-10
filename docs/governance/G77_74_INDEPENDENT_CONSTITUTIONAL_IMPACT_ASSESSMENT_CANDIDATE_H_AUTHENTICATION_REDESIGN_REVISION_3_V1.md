# 1. Implementation Summary

Generation: G77-74

Report identity:
`G77_74_INDEPENDENT_CONSTITUTIONAL_IMPACT_ASSESSMENT_CANDIDATE_H_AUTHENTICATION_REDESIGN_REVISION_3_V1`

Artifact class:
`INDEPENDENT_HOSTILE_CONSTITUTIONAL_IMPACT_ASSESSMENT_NON_IMPLEMENTING_NON_ACTIVATING`

Assessed subject:
`G77_73_CANDIDATE_H_AUTHENTICATION_REDESIGN_REVISION_3_SIGNER_OUTCOME_DURABILITY_AND_EXTERNAL_CAPACITY_SOURCE_AUTHENTICATION_CLOSURE_V1`

Controlling predecessor:
`G77_72_INDEPENDENT_CONSTITUTIONAL_IMPACT_ASSESSMENT_CANDIDATE_H_AUTHENTICATION_REDESIGN_REVISION_2_V1`

Assessment posture: every G77-73 claim was treated as untrusted and
independently reconstructed.

Constitutional baseline: authenticated committed G0 through G77-73.

Reporting date: 2026-08-10.

Repository identity at assessment start:

- branch: `master`;
- commit: `490dc06f577ef76fd93f2a6eccf0372925b5f2c1`;
- tree: `9295c84caf82a561006d109fcfe360fdb65436ae`;
- subject: `G77-73: close Candidate H signer durability and capacity authentication`;
- G77-73 status: committed and tracked at HEAD; and
- worktree status: clean.

Objective:

Attempt to falsify G77-73 CapacityV2, ResultV2, signer durability,
HumanDecisionV2, P012, transitive counts, machinery, identity/authority DAGs,
Replay, crash/retry, one-shot ceilings, and topology. This artifact assesses
only and does not repair G77-73.

Assessment result: `REQUIRES_REWORK`.

The first exact blocker is:

`G77_73_B01_AUTHORITY_BEARING_PHYSICAL_SIGNER_USE_AT_MOST_ONCE_NOT_PROVED`

G77-73 proves exactly one content-derived signer intent and one winning
`AVAILABLE -> ACCEPTED_IN_PROGRESS` CAS. That establishes at most one logical
signer operation identity. It does not establish at most one physical use of
the authority-bearing signing primitive.

G77-73 expressly permits this recovery:

~~~text
accepted logical invocation
-> physical Ed25519 computation produces signature
-> crash before durable signer outcome commit
-> restart under same accepted invocation
-> deterministically recompute Ed25519 signature
~~~

The second computation uses the private-key signing primitive again. Equal
deterministic signature bytes do not make two physical authority uses one.
Repeated crashes at the same boundary permit an unbounded number of physical
signing computations while the persisted evidence continues to show one
logical acceptance receipt and no terminal outcome.

No G77-73 artifact records whether the physical primitive began, completed,
or was used how many times before outcome commit. The accepted receipt is a
predecessor to physical signing, not evidence of exactly-once physical use.
The terminal outcome is evidence only after persistence. Therefore
`MAX_SIGNER_OPERATION_IDENTITIES = 1` is proved, but
`MAX_AUTHORITY_BEARING_SIGNER_INVOCATIONS = 1` is not.

## Authenticated Lineage

| Artifact | SHA-256 | Role |
|---|---|---|
| G48-00 | `16508d1a77c4b3f07d37861e74d85f77896be16da01ca26cbc07a658ddf2c0eb` | reporting standard |
| G69-07 | `ac8665d902abef943b12ee4198e99884930f888eb7d1d3387e686943ea80bd61` | Human Authority custody boundary |
| G70-03 | `7006a1c03e654542ac7d77fd18fdee996c36e0e20de7425c94c8f3ac6c2bc00d` | assessment discipline |
| G76-06 | `29f06a93d5b7ce610c161487bc1e3a01f6d7d063b22393e0347b0da20b281dbc` | identity and DAG rules |
| G77-42 | `b379cb057282aaf7d10c6e6e3f8a55053a630b19a0a0ad80e8159a0222b316a6` | external Premise/key/custody model |
| G77-44 | `03026b9ff5df38e05ffe08e0d834d0ac83d1b04efc3681f6ea2aff4165801c0a` | external CAS/read-back precedent |
| G77-62 | `661394be4e32b2e965f6a906e865a78128572084bbe52c5d0aad3bfdd5deca1e` | thirty-group consumer graph |
| G77-64 | `ac3deaf40e7f06c04e3396b161194b258b7ae993b65d9ee719fb1170fc4ac0c6` | Certification-time closure |
| G77-69 | `329f952e7514e6e932579d1df12823f4bad8eb948806fa096897c270dab1103f` | Revision 1 redesign assessment |
| G77-70 | `5c6fe6138391fbb58a3bb20e047585a664d94f0a07e0be7ed3368a444f67563c` | Revision 1 hostile assessment |
| G77-71 | `94f8117659cc000586cd8017a58a70254da0610e67c0d3c414cc093a316a4da9` | failed Revision 2 proposal |
| G77-72 | `90e990d95b5a855643fd032ccee2b7a6f7300496fc16fb0d3f2eb27825369639` | controlling Revision 2 assessment |
| G77-73 | `6a6c24bbb86344d76d1f38fa364462fd601e5313400564016dd39cc0b90af586` | assessed Revision 3 proposal |
| HFD-01 | `f23c25a36a638961ffca25861576858e7a77c7f715c23e01783f66ad6743e982` | external Human Founder model |
| HFD-04 | `5030cd2d90cbb792fa3ee3ed2777057ad269619b091b344b390e8d6247d85eb5` | exact `P_auth_v2` |
| HFD-06 | `f9505f3beac9d9e43b2991421c78110eab1f1ff8cf6ca2a97df2ed4d79c8f886` | frozen P012 compatibility stop |

All hashes match independently recomputed repository bytes. Repository state
is consistent and G77-73 is eligible for assessment.

## Independent G77-72 Blocker Reconstruction

G77-72 B01 established that G77-71's `AUTHENTICATING` claim did not distinguish
not-invoked from invoked-result-lost and relied on hidden owner-local signer
memory. G77-73 repairs that logical ambiguity with a signer-owned acceptance
receipt and outcome registry. G77-72, however, required one signer invocation,
not merely one operation identity. G77-74 therefore reconstructs the physical
private-key operation as a distinct authority-bearing event.

G77-72 B02 established that owner-field equality did not authenticate exact
capacity bytes. G77-73 adds a Premise-owner signature over the exact capacity
core and a source issuance read-back. That positive source-authentication edge
is assessed separately below and survives.

## Required Effect Classifications

| Required classification | Assessment-only result |
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

## Hostile CapacityV2 Assessment

Independent counting confirms exactly 34 semantic fields. Fields 01 through
32 are the unchanged G77-71 authority-bearing core. Fields 33 and 34 are the
complete nested issuance-authentication and custody-read-back records.

`P_capacity_issue_v2` is independently reconstructed as the exact CJ1 object
containing:

~~~text
issuance_domain_identity =
  HUMAN_FOUNDER_EXTERNAL_CAPACITY_ISSUANCE_V2
artifact_type = HumanFounderExternalCapacityEvidence
artifact_version = V2
contract_version =
  CANDIDATE_H_AUTHENTICATION_REDESIGN_REVISION_3_V1
producing_owner
all exact core fields 01 through 32
~~~

It excludes the later signature-bearing authentication record, later custody
read-back record, final CapacityV2 identity/digest/idempotency, and metadata.
It does not exclude an authority-bearing core field. Therefore the capacity
signature does not sign itself or a successor and creates no identity cycle.

The positive edge is exact:

~~~text
accepted ExternalConstituentPremiseEvidenceV1
-> validate Premise owner, identity scheme, signature scheme/key identity,
   custody and authentication evidence
-> require CapacityV2 issuer/owner/scheme/key exact equality
-> recompute public-key identity from strict 32-octet key
-> verify Ed25519 RFC8032 pure signature over exact UTF8(CJ1(P_capacity_issue_v2))
-> verify source issuance CAS/read-back binds that signed core/auth record
-> admit CapacityV2
~~~

G77-42 already requires the accepted Premise to carry and validate its exact
signature scheme, key identity, signature, custody, provenance, and scope.
G77-73 narrows eligible Premises to the exact Ed25519 profile and binds the
resolved public key by key identity and trust digest. It does not ask a new
key to authenticate itself.

Hostile attacks:

| Attack | Result |
|---|---|
| claimant copies Premise owner text | cannot produce valid Premise-owner signature over exact core |
| claimant substitutes key | key identity, Premise equality, trust digest, and signature fail |
| issuer signs its own signature | excluded from P_capacity_issue_v2 |
| capacity identity signs itself | final identity is absent from signed core |
| circular capacity-to-Premise authority | Premise pair is finalized first and never depends on CapacityV2 |
| repository or `HUMAN_AUTHORITY` claims issuer role | exact owner/key equality rejects |
| valid key creates authority | rejected; accepted Premise must precede key use |
| claimant transports already signed bytes | does not alter issuer authenticity; bytes remain exact issuer-signed content |
| claimant fabricates different core under same read-back | signature/commitment/stored digests fail |

The issuance CAS/read-back alone would not authenticate a claimant-produced
core. In G77-73 it is not used alone: it binds the already verified issuer
signature and exact core/authentication-record digests. Consistent with the
G77-44 external-domain precedent, the source-owned read-back proves current
durable custody while the signature proves source issuance. Neither creates
the external Premise.

CapacityV2 verdict: `PASS_PROPOSAL`.

## Hostile ResultV2 and Signer Assessment

Independent counting confirms exactly 50 ResultV2 semantic fields. The
declared identity order is:

~~~text
P_auth_v2 and authentication operation
-> outer claim CAS/read-back
-> signer invocation intent
-> signer acceptance CAS
-> invocation receipt
-> physical signer execution
-> signer outcome
-> signer outcome read-back
-> outer terminal CAS/read-back
-> ResultV2
-> HumanDecisionV2
~~~

The intent binds exact Premise, CapacityV2, actor, operation, claim,
commitment, message, scheme/key, signer slot/epoch, sequence 1, and logical
maximum 1. The acceptance CAS binds `AVAILABLE -> ACCEPTED_IN_PROGRESS` and
has one winner. The receipt proves that winner. The outcome binds exact
intent/acceptance/receipt predecessors and one of three terminal results. Its
read-back binds the terminal signer slot. The outer terminal CAS binds that
read-back, and ResultV2 derives after outer read-back. No later pair appears
in a predecessor identity.

These subcontracts close logical operation identity and durable accepted
outcome reconstruction. They fail at the physical signing boundary.

### Logical versus physical signer result

| Property | Independent verdict | Reason |
|---|---|---|
| logical signer intents <= 1 | `PASS` | one content-derived intent |
| accepted logical operations <= 1 | `PASS` | one signer slot and acceptance CAS winner |
| durable signer outcomes <= 1 | `PASS` | one terminal outcome CAS/read-back |
| valid durable ResultV2 <= 1 | `PASS` | one outer terminal CAS/read-back |
| physical private-key computations <= 1 | `FAIL` | post-computation/pre-commit crash permits recomputation |
| authority-bearing signer uses <= 1 | `FAIL` | physical private-key use is not represented or counted |

G77-73's phrase “continuation of one accepted invocation” is a logical
classification. It cannot make a second physical private-key computation
disappear from authority history. The declared evidence contains no
`physical_signing_started`, `physical_signing_completed`, hardware operation
receipt, physical-use ordinal, or atomic compute-and-outcome persistence
proof.

### Signer implementation variance

For local deterministic software Ed25519, recomputation produces the same
signature bytes, but executes the private-key operation again. Artifact bytes
are deterministic; authority-use count is not one.

For an HSM or remote signer, the accepted G77-73 receipt may exist outside the
device/service that performs the physical operation. A crash or lost response
can cause the recovery process to submit the same sign command again. Unless
the HSM/remote signer itself implements a durable idempotent operation
identity and authoritative outcome read-back, a non-idempotent signer can
perform two real signing operations. G77-73 does not require such an interface
or exclude those implementations.

Different conforming implementation choices therefore have different crash
semantics:

~~~text
local software -> same bytes, potentially repeated private-key computations
idempotent HSM -> potentially one physical use if device contract proves it
non-idempotent HSM/remote signer -> potentially repeated physical uses
~~~

G77-73 claims implementation-neutral constitutional closure but specifies
only the logical registry. It neither confines the contract to a proven
atomic local signer nor requires device-level idempotency/read-back.

### Write-before-response attack

Write-before-response prevents a conforming caller from accepting signature
bytes before the outcome store commits. It does not make signature computation
atomic with outcome persistence. A signature may exist transiently in process
memory, an HSM response buffer, device audit state, transport buffers, crash
dumps, or remote signer state before the G77-73 outcome commit.

After crash, persisted G77-73 evidence can show only the accepted receipt and
`ACCEPTED_IN_PROGRESS`. It cannot prove whether physical signing never began,
completed once, or completed repeatedly. Deterministic recomputation gives a
recoverable byte result but constitutes another authority-bearing use. No
exact artifact proves otherwise.

ResultV2 verdict: `FAIL_PHYSICAL_SIGNER_USE_CLOSURE`.

## HumanDecisionV2 and P012 Reassessment

Independent counting confirms HumanDecisionV2 remains exactly 31 semantic
fields. Its capacity pair resolves CapacityV2; its result pair resolves
`AUTHENTICATED_FINAL` ResultV2; its scheme/key/signature equal both; and its
signature/result remain outside `P_auth_v2`. The result precedes the decision,
so the identity order remains acyclic. `HUMAN_AUTHORITY` remains custody-only.

The persisted Revision 3 token is exact:

~~~text
CANDIDATE_H_AUTHENTICATION_REDESIGN_REVISION_3_V1
~~~

ProofSetV3 includes `contract_version` in its identity-bearing common payload.
CertificationV3 and TransitionV3 carry the same token and exact predecessor
pairs. Old/unknown tokens reject. Same complete bytes cannot select two P012
meanings. Artifact-version reuse remains byte-visible and lawful.

P012's version dispatch therefore passes. Its substantive TRUE path does not:
P012 validates ResultV2's declared logical evidence but G77-73 has no field or
rule proving the physical authority-use ceiling. A history with two physical
signing computations and one final persisted signature can satisfy every
G77-73 P012 byte equality.

HumanDecisionV2 verdict: `PASS_CONDITIONAL_SCHEMA_AND_DAG`.

P012 contract-version verdict: `PASS`.

P012 Revision 3 one-shot authentication verdict: `FAIL_TRANSITIVE_RESULT_INPUT`.

## Independent Consumer Recount and Machinery Attack

The independently reconstructed current graph contains thirty groups:

| # | Current family or consumer group | Classification | Independent reason |
|---:|---|---|---|
| 1 | External Premise | `UNCHANGED_REUSE` | exact accepted owner/key/custody predecessor |
| 2 | SourceCommitmentV1 | `UNCHANGED_REUSE` | Target pair only |
| 3 | InstrumentCommitmentV3 | `UNCHANGED_REUSE` | no HumanDecision/P012 field |
| 4 | UniverseV1 / CandidateCensusV1 | `UNCHANGED_REUSE` | pair closure only |
| 5 | SourceEvidenceV1 / RecognitionProofV1 | `UNCHANGED_REUSE` | existing external evidence pairs |
| 6 | NormativePayloadV1 / TargetV5 | `UNCHANGED_REUSE` | predecessor of HumanDecision |
| 7 | InstrumentV4 | `UNCHANGED_REUSE` | predecessor of HumanDecision |
| 8 | HumanDecisionV1 | `VERSION_SUCCESSOR_REQUIRED` | redesign requires HumanDecisionV2 |
| 9 | HumanFinalityV1 | `UNCHANGED_REUSE` | decision pair version-opaque |
| 10 | DispositionEvidence V2/V3 | `UNCHANGED_REUSE` | exact pair/status equality |
| 11 | external status/current version/snapshot | `UNCHANGED_REUSE` | resolved type/version rows |
| 12 | ProofSetV3 | `UNCHANGED_REUSE` | identity-bearing Revision 3 dispatch |
| 13 | CertificationV3 | `UNCHANGED_REUSE` | same schema/version; exact ProofSet pair/token |
| 14 | FoundingTransitionV3 | `UNCHANGED_REUSE` | same schema/version; exact predecessor pairs |
| 15 | FenceV1 / BEGIN CAS | `UNCHANGED_REUSE` | pair-opaque; Transition remains V3 |
| 16 | OperationSeed/token/AllocationIntentV2 | `UNCHANGED_REUSE` | generic immutable pair inputs |
| 17 | ALLOCATED CoordinatorStateV2 | `UNCHANGED_REUSE` | allocation row unchanged |
| 18 | allocation CAS/marker/read-back/Receipt | `UNCHANGED_REUSE` | generic root serialization |
| 19 | LogicalPointer/Projection/Manifest/route Censuses | `UNCHANGED_REUSE` | no authentication interpretation |
| 20 | ordinary-chain CensusV2 | `UNCHANGED_REUSE` | Target/route closure unchanged |
| 21 | CAP Reachability StateV2 | `UNCHANGED_REUSE` | Census/Target closure unchanged |
| 22 | Dormancy Rebase GuardV2 | `UNCHANGED_REUSE` | Transition remains V3 |
| 23 | MetaRepairTransitionV3 | `UNCHANGED_REUSE` | Guard remains V2 |
| 24 | MetaRepairStateV3 | `UNCHANGED_REUSE` | Guard/Meta/Transition versions unchanged |
| 25 | failure Census/FailureEvidenceV2 | `UNCHANGED_REUSE` | pair-opaque failure reduction |
| 26 | terminal CommitmentV3 | `UNCHANGED_REUSE` | downstream fixed versions unchanged |
| 27 | consuming operation/ConsumeIntentV2 | `UNCHANGED_REUSE` | commitment pair opaque |
| 28 | terminal CoordinatorV4 / RootSnapshotV4 | `UNCHANGED_REUSE` | fixed terminal versions unchanged |
| 29 | terminal CAS/read-back/AttemptTerminalReadBack/Disposition/Receipt/Dormancy | `UNCHANGED_REUSE` | pair comparison only |
| 30 | Replay / CRO | `UNCHANGED_REUSE` | explicit token dispatch; read-only/passive |

Independent counts:

~~~text
current consumer groups = 30
unchanged current consumer groups = 29
pre-redesign existing successor contracts = 1
blocker-targeted failed-proposal successor contracts = 2
total declared successor contracts = 3
new top-level families beyond G77-71 = 0
new State families = 0
new verification families = 0
~~~

Those structural counts are accurate. Their claimed
`NECESSARY_AND_SUFFICIENT` conclusion is not. The physical authority-use
boundary is underprovisioned. This assessment does not determine whether the
missing responsibility requires a stronger existing Result contract, a
device-level receipt, an atomic signer primitive, or a new family; doing so
would repair G77-73 and is outside scope.

No current consumer requires a new family merely because the assessment
fails. The final correctness-preserving successor/new-family minimum remains
`UNRESOLVED`.

Machinery-minimality verdict: `FAIL_UNDERPROVISIONED`.

## Identity and Authority DAG Attack

The declared artifact identity DAG is finite and acyclic. Capacity signature
and signer/result pairs exclude their own identities/signatures and bind only
finalized predecessors. The complete authority-event graph is not closed:

~~~text
accepted receipt
-> physical sign use 1
-> crash before outcome commit
-> same accepted receipt
-> physical sign use 2
-> crash before outcome commit
-> ...
-> physical sign use N
-> one durable outcome
~~~

Every physical use maps to the same operation/message/key and may yield the
same signature bytes. None before the final persisted outcome is represented
by a durable identity/digest pair. Repeated crash/recompute makes the physical
authority-event sequence unbounded.

| Required property | Verdict | Reason |
|---|---|---|
| `FINITE` | `FAIL_COMPLETE_GRAPH` | physical uses are unbounded across repeated crash/recompute |
| `ACYCLIC` | `PARTIAL` | declared artifact graph is acyclic; recovery recurrence is absent from it |
| `FORWARD_DERIVED` | `FAIL_COMPLETE_GRAPH` | physical uses have no durable per-use predecessor/result evidence |
| `BYTE_DETERMINISTIC` | `PARTIAL` | final signature bytes are deterministic; physical-use history is not represented by bytes |
| `DOMAIN_SEPARATED` | `PASS` | capacity, Human custody, signer, Certification, root, Replay, and CRO roles remain distinct |
| `REPLAY_RECONSTRUCTIBLE` | `FAIL` | Replay cannot reconstruct physical use count/history |

The independently reconstructed authority DAG otherwise preserves:

~~~text
external constituent authority
-> accepted Premise
-> authenticated capacity issuance
-> Human choice and signer authorization

HUMAN_AUTHORITY -> decision/finality custody only
Certification -> predicates only
Governance/root custody -> retained mechanics only
Replay/CRO -> read-only/passive
~~~

Forbidden edges from owner equality alone, source signature, result custody,
`HUMAN_AUTHORITY`, key possession, valid signature, P012 TRUE,
Certification, Governance, repository ownership, root success, and Replay do
not create constituent authority. Capacity cryptography authenticates an
issuance from an already accepted external Premise only.

The authority DAG still fails one-shot completeness because the accepted
signer authorization may be physically exercised repeatedly without distinct
evidence. No new authority owner is created, but the one authorized use is
not bounded to one physical exercise.

Authority DAG verdict: `FAIL_PHYSICAL_USE_BOUNDARY`.

## Crash, Replay, and One-Shot Reconstruction

The sixteen G77-73 boundaries plus one independently isolated remote/HSM
boundary are:

| # | Boundary | Persisted predecessor | Logical signer state | Physical signer state | Allowed machine action | Forbidden Human/signer action | Read-back source | Deterministic result |
|---:|---|---|---|---|---|---|---|---|
| 1 | before outer claim | P_auth/operation; OPEN slot | not begun | not begun | submit exact claim | Human/signing action | auth slot | OPEN or same claim |
| 2 | outer claim response lost | claim may be committed | not begun | not begun | read auth slot | second claim/message/key | auth slot | OPEN or exact AUTHENTICATING |
| 3 | after claim before acceptance | claim; signer AVAILABLE | intent only | not begun | submit exact acceptance | direct signer/Human retry | signer slot | AVAILABLE or accepted |
| 4 | acceptance response lost | acceptance may be committed | none or accepted once | not begun | read signer slot | different intent | signer slot | AVAILABLE or exact receipt |
| 5 | invocation accepted | accepted receipt | in progress | not begun | signer may begin | caller signing/Human action | signer receipt | ACCEPTED_IN_PROGRESS |
| 6 | local signer executing | accepted receipt | in progress | physical use in progress | declared signer continues | caller retry | outcome store | unknown physical completion until outcome |
| 7 | local signature computed before outcome commit | accepted receipt only | in progress | completed at least once | G77-73 permits recomputation | second physical use should be forbidden but is not prevented | outcome store has none | physical count indeterminate |
| 8 | unsuccessful computation before commit | accepted receipt only | in progress | attempted at least once | persist/recompute failure path | caller/Human inference | outcome store | physical attempt count indeterminate |
| 9 | **added: HSM/remote command accepted, response lost** | accepted logical receipt | in progress | device may have signed | no safe generic action specified | second device command | absent device-level read-back contract | physical count/result indeterminate |
| 10 | signer outcome persisted, response lost | terminal signer outcome | completed logically | one or more physical uses | read outcome | signer retry | outcome store | identical terminal bytes |
| 11 | before outer terminal CAS | outcome read-back | completed logically | historical count unknown | derive terminal candidate | signer/Human retry | outcome read-back | one outer candidate |
| 12 | outer terminal response lost | terminal may be committed | completed logically | historical count unknown | read auth slot | different terminal | auth slot | AUTHENTICATING or exact terminal |
| 13 | outer read-back before ResultV2 | terminal outer read-back | completed logically | historical count unknown | derive ResultV2 | signer/Human retry | outer store | identical result |
| 14 | restart with AVAILABLE | claim and AVAILABLE | not begun | not begun | submit same acceptance | different operation | signer slot | accepted once or no progress |
| 15 | restart with ACCEPTED_IN_PROGRESS | accepted receipt | in progress | zero or more completed physical uses | G77-73 permits resume/recompute | second physical use cannot be detected | signer store | logical state deterministic, physical history not |
| 16 | restart with terminal outcome | outcome read-back | completed logically | one or more physical uses | finish outer result | signer retry | signer/outer stores | identical bytes, unknown physical count |
| 17 | permanent exhaustion | terminal outer evidence | completed at most one logical op | physical history unknown | read only | revival/reset/reissue | terminal store | permanent logical terminal state |

Starting from persisted evidence, Replay can reconstruct Premise, CapacityV2,
capacity issuance signature/read-back, HFD act/review, `P_auth_v2`, claim,
signer intent, acceptance, receipt, durable outcome/read-back, ResultV2,
HumanDecisionV2, P012 token/result, Finality, ProofSet, Certification,
Transition, BEGIN/root, and exhaustion artifacts.

Replay cannot reconstruct whether physical signing occurred zero, one, or
multiple times before a terminal outcome. The same accepted receipt and final
outcome bytes admit all those histories. No process memory, cache, device log,
or external signer state may fill the gap. Replay verdict: `FAIL`.

One-shot hostile results:

| Ceiling | Verdict |
|---|---|
| Human dispositions <= 1 | `PASS` |
| Human reviews <= 1 | `PASS` |
| authentication operation identities <= 1 | `PASS` |
| logical signer operations <= 1 | `PASS` |
| authority-bearing physical signer uses <= 1 | `FAIL` |
| valid durable results <= 1 | `PASS` |
| HumanDecisionV2 <= 1 | `PASS_CONDITIONAL` |
| Finality <= 1 | `PASS_CONDITIONAL` |
| founding effects <= 1 | `PASS_CONDITIONAL` |

REFUSE, persisted INDETERMINATE_EXHAUSTED, and successful ADOPT terminal
states remain non-revivable. The failure occurs before terminalization and can
repeat the authorized physical signing use. One-shot verdict:
`FAIL_AUTHORITY_BEARING_SIGNER_USE_CEILING`.

## Topology and Reuse Impact Assessment

Topology remains structurally unchanged despite the signer defect:

| Measure | Before | G77-73 | Verdict |
|---|---:|---:|---|
| production paths | 1 | 1 | `PASS` |
| parallel paths | 0 | 0 | `PASS` |
| persistent founding paths | 0 | 0 | `PASS` |
| Human entry points | 1 | 1 | `PASS` |
| root paths | 1 | 1 | `PASS` |
| persistent founding authorities | 0 | 0 | `PASS` |

Repeated physical signing is repeated use on one failed authentication path,
not a second root or production path. It remains constitutionally invalid.

1. **Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?**

   Ponovno se uporabijo CJ1/SHA-256, G76 identitetni model, G69-07 meja
   skrbništva `HUMAN_AUTHORITY`, sprejeti zunanji Premise, HFD-04
   `P_auth_v2`, G77-44 CAS/read-back, HumanDecisionV2, HumanFinality,
   Disposition, ProofSetV3, CertificationV3, TransitionV3, Fence/BEGIN,
   CAP/Guard/MetaRepair, korenska pot, HIC/CHE ter pasivni Replay/CRO.
   Neodvisni popis potrdi 29 nespremenjenih potrošniških skupin.

2. **Katere nove zmogljivosti (če sploh) nastanejo?**

   G77-73 predlaga popravljena CapacityV2 in ResultV2 znotraj dveh že
   predlaganih novih odgovornosti ter ne dodaja nove vrhnje družine. Fizično
   enkratna uporaba signerja ni dokazana; končni potrebni obseg mehanizma
   ostaja nerazrešen.

3. **Ali katera obstoječa zmogljivost postane nedosegljiva?**

   Ne zaradi verzij ali topologije. Uspešna P012/Candidate H pot mora ostati
   nedosegljiva, ker ResultV2 ne dokazuje enkratne fizične uporabe signerja.
   Predhodne V1 pogodbe ostanejo nespremenjena neuspešna zgodovina.

4. **Ali implementacija ustvarja vzporedni tok?**

   Ne. Implementacije ni. Defekt dovoljuje ponovljeno uporabo fizičnega
   signerja na istem logičnem toku, ne nove HIC/CHE ali korenske poti.

5. **Ali zmanjšuje ali povečuje število produkcijskih poti?**

   Ne. Ostane ena produkcijska pot, nič vzporednih in nič trajnih
   ustanovitvenih poti.

# 2. Code Evidence

## Public API

No public API is implemented. The assessed design surface is the committed
CapacityV2, ResultV2, retained HumanDecisionV2, and Revision 3 P012 contract.
G77-74 adds no callable interface.

## Orchestration Entry Point

No orchestration entry point is created. The hostile boundary is:

~~~text
accepted logical receipt -> physical signing -> outcome commit
~~~

G77-73 does not make physical signing and durable outcome commit one atomic
constitutional operation.

## Semantic Reductions

The decisive reduction is:

~~~text
one accepted logical signer operation
+ physical signature computed
+ crash before outcome commit
+ deterministic recomputation permitted
-> physical authority use count can exceed one
~~~

Equal signature bytes do not reduce multiple physical uses to one.

## Public Validators

No validator is implemented. A future G77-73-shaped validator can validate
one acceptance receipt and one final outcome but has no persisted input from
which to validate the maximum physical signer-use count. It must fail closed
rather than infer one physical use from one logical identity.

## Canonical Data Models

Independent counts:

~~~text
CapacityV2 fields = 34
preserved CapacityV2 core fields = 32
ResultV2 fields = 50
HumanDecisionV2 fields = 31
current consumer groups = 30
unchanged current groups = 29
declared total successor contracts = 3
new top-level families beyond G77-71 = 0
~~~

## Deterministic Algorithms

Ed25519 RFC8032 pure deterministically reproduces the same signature bytes for
the same key/message. That algorithmic determinism does not prove exactly one
execution. G77-73's restart algorithm can re-execute the primitive while
retaining the same logical operation and eventual bytes.

## Responsibility Boundaries

| Responsibility | Verified boundary | Missing boundary |
|---|---|---|
| capacity issuance | accepted Premise owner signature | none identified at proposal level |
| logical signer acceptance | signer registry CAS/receipt | none identified |
| physical signing use | accepted key/message authorization | exactly-once physical execution/persistence evidence |
| outcome durability | write-before-response outcome store | atomicity with physical signing absent |
| Human custody | `HUMAN_AUTHORITY` only | no external authority transfer |
| P012/Certification | deterministic validation | cannot infer physical-use count |
| Replay | persisted artifact reconstruction | cannot reconstruct physical history |

## Repository Evidence

Evidence consists of authenticated committed G77-71/G77-72/G77-73 and
controlling G48/G69/G70/G76/G77/HFD bytes, independent schema and graph
reconstruction, focused G69/G70 tests, and exact mutation checks. No signer,
HSM, remote service, key, signature, capacity instance, Human act, BEGIN,
root effect, activation, or deployment exists.

# 3. Constitutional Self-Assessment

## Verified

- G77-73 is committed and controlling hashes match repository bytes.
- CapacityV2 has exactly 34 fields with an exact preserved 32-field core.
- The capacity issuance message excludes signature and final self identity.
- CapacityV2 establishes authenticated issuance from an already accepted
  Premise owner/key without creating constituent authority.
- ResultV2 has exactly 50 fields and its declared artifact dependencies are
  forward and acyclic.
- G77-73 proves one logical signer intent, acceptance, and terminal outcome.
- HumanDecisionV2 retains exactly 31 fields and forward result dependency.
- The Revision 3 ProofSet contract token is identity-bearing and visible to
  CertificationV3, TransitionV3, and Replay.
- The current graph has 30 consumer groups: 29 unchanged and one current
  successor; G77-73 declares two failed-proposal successors.
- Negative authority boundaries and topology remain unchanged.
- All assessment-only effect classifications remain `NO`.

## Not Verified

- At most one physical authority-bearing signer use is not proved.
- A crash after physical signing but before outcome commit can cause another
  private-key computation on restart.
- Repeated crashes can produce an unbounded physical-use history.
- G77-73 does not define whether the signer is local software, an idempotent
  HSM, a non-idempotent HSM, or a remote service with durable operation IDs.
- No physical-start/completion receipt or atomic sign-and-persist proof exists.
- Write-before-response does not prove write-before-physical-signing or atomic
  physical-use persistence.
- Replay cannot reconstruct physical signing history from persisted evidence.
- The complete identity/authority event graph is not finite,
  forward-complete, or Replay-reconstructible.
- ResultV2 and P012 cannot validate the physical one-shot ceiling.
- Machinery necessity and sufficiency are not established.
- No Candidate H/G76-specific executable test module exists.
- No implementation, external instance, Human act, signature, activation,
  BEGIN, root mutation, deployment, or production effect was performed.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| repository HEAD/tree/clean start | exact Git state | Git inspection | `PASS` |
| G77-73 committed immutability | tracked HEAD subject | Git inspection | `PASS` |
| predecessor hashes | authenticated hash table | SHA-256 | `PASS` |
| G77-72 blocker reconstruction | exact B01/B02 | hostile predecessor review | `PASS` |
| CapacityV2 total fields | exact displayed schema | independent count | `PASS` |
| CapacityV2 preserved core | fields 01-32 | independent count | `PASS` |
| capacity issuance self-exclusion | P_capacity_issue_v2 | cycle review | `PASS` |
| Premise owner/key binding | exact equality/trust chain | authority review | `PASS` |
| capacity self-attestation attack | Premise-owner signature required | hostile signature review | `PASS` |
| capacity custody/read-back | signed core plus source read-back | persistence review | `PASS` |
| CapacityV2 positive authority edge | accepted Premise precedes source signature | authority DAG review | `PASS` |
| ResultV2 total fields | exact displayed schema | independent count | `PASS` |
| signer intent/acceptance/receipt | one logical operation slot | schema/state review | `PASS` |
| signer outcome/read-back | one durable terminal outcome | persistence review | `PASS` |
| outer terminal/result direction | finalized signer outcome precedes ResultV2 | DAG review | `PASS` |
| maximum logical signer identities | one acceptance CAS winner | one-shot review | `PASS` |
| maximum physical signer uses | recomputation after crash | physical signer attack | `FAIL` |
| local software crash semantics | repeated deterministic computation | hostile retry review | `FAIL` |
| HSM/remote signer semantics | no required device idempotency/read-back | implementation-neutral review | `FAIL` |
| write-before-response | prevents admissible early egress | contract review | `PASS` |
| atomic sign/outcome persistence | no such exact contract | crash review | `FAIL` |
| Replay physical history | same evidence admits multiple use counts | Replay attack | `FAIL` |
| HumanDecisionV2 fields/DAG | 31 fields and forward result pair | schema/DAG review | `PASS` |
| P012 contract-version visibility | exact Revision 3 token | byte/Replay review | `PASS` |
| P012 physical one-shot validation | no physical-use evidence field | transitive review | `FAIL` |
| current consumer inventory | thirty classified groups | independent recount | `PASS` |
| reuse/current successor counts | 29 reuse / 1 current successor | count review | `PASS` |
| declared blocker successors | CapacityV2 and ResultV2 | contract review | `PASS` |
| machinery necessity/sufficiency | physical boundary underprovisioned | minimality attack | `FAIL` |
| identity DAG finite/forward/Replay | unbounded unrecorded physical uses | complete-graph attack | `FAIL` |
| identity DAG declared acyclicity | artifact pairs remain forward | cycle review | `PASS` |
| authority DAG negative edges | no internal source substitution | authority attack | `PASS` |
| authority DAG physical-use ceiling | repeated authorized key use possible | authority attack | `FAIL` |
| crash boundaries | seventeen rows including HSM gap | crash reconstruction | `PASS` |
| one-shot signer-use ceiling | physical uses can exceed one | lifecycle attack | `FAIL` |
| terminal non-revivability | retained terminal states | lifecycle review | `PASS` |
| topology | exact before/after counts | graph review | `PASS` |
| Reuse Impact Assessment | five Slovenian answers | completeness review | `PASS` |
| focused G69/G70 tests | 326 existing tests | pytest | `PASS` |
| Candidate H/G76 tests | no directly named module present | test inventory | `NOT_APPLICABLE` |
| G48 six top-level sections | exact names/order/count | structure validation | `PASS` |
| eight Code Evidence subsections | exact names/count | structure validation | `PASS` |
| Markdown fence balance | paired fence count | format validation | `PASS` |
| trailing whitespace | zero matching lines | format validation | `PASS` |
| tracked/untracked whitespace | Git/no-index checks | diff validation | `PASS` |
| exact G77-74 mutation | one new governance artifact | mutation inventory | `PASS` |
| predecessor/runtime/test/config/root/production mutation | no changed prohibited path | mutation inventory | `PASS` |
| implementation/activation/act/signature/BEGIN/root/deployment/commit | assessment-only boundary | scope review | `NOT_APPLICABLE` |

# 5. Repository Mutation Summary

Modified files:

- added
  `docs/governance/G77_74_INDEPENDENT_CONSTITUTIONAL_IMPACT_ASSESSMENT_CANDIDATE_H_AUTHENTICATION_REDESIGN_REVISION_3_V1.md`
  as the sole G77-74 assessment artifact.

Unchanged subsystems:

- G77-73, G77-72, G77-71, and every controlling predecessor;
- CapacityV2, ResultV2, HumanDecisionV2, `P_auth_v2`, P012, HumanFinality,
  Disposition, ProofSetV3, CertificationV3, TransitionV3, Fence/BEGIN,
  CAP/Guard/MetaRepair, root contracts, HIC/CHE, Replay, and CRO;
- runtime, signer/HSM integrations, stores, schemas, validators, tests,
  config, credentials, providers, root persistence, release, deployment, and
  production.

API compatibility:

- no API, runtime model, validator, serializer, signer, store, route, command,
  workflow, owner, root schema, or deployment contract is added or changed;
- G77-73 is assessed but not repaired; and
- the failed assessment grants no implementation or production authority.

Boundary preservation:

- assessment only;
- no repair to G77-73;
- no external evidence instance, capacity issuance, signer invocation,
  cryptographic signature, Human act/disposition, HumanDecision, Finality,
  P012 result, BEGIN, root mutation, activation, authority grant, deployment,
  or production effect;
- Replay remains read-only, CRO passive, HIC/CHE transport-only, and
  `HUMAN_AUTHORITY` custody-only; and
- topology remains one production path, zero parallel paths, and zero
  persistent founding paths.

Unrelated pre-existing changes:

- None observed. The worktree was clean at assessment start.

Worktree mutation count attributable to this task: `1` new governance file,
`0` modified existing files.

No commit is created.

# 6. Certification Verdict

G77_73_CONSTITUTIONAL_IMPACT_REQUIRES_REWORK
