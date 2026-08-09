# 1. Implementation Summary

Generation: G77-60

Report and proposal identity:
`G77_60_EXTERNAL_CONSTITUENT_CANDIDATE_H_INSTANTIATION_CONTRACT_CONSTITUTIONAL_DESIGN_PROPOSAL_REVISION_2_V1`

Proposal revision: `2`

Proposal status: `PROPOSAL_ONLY_UNASSESSED`

Amendment kind: `ADDITION`

Constitutional baseline: authenticated G0 through G77-59. G77-58 is the
immutable predecessor proposal. G77-59 is its sole authoritative independent
G70-03 Constitutional Impact Assessment and classifies G77-58 as
`UNRESOLVED_CONSTITUTIONAL_IMPACT`. No predecessor is reopened or rewritten.

Authenticated repository identity:

- Commit: `c5236218b609a215174d65b34309999b8685e052`
- Tree: `96c8710709f110f773d1a4452508c3ad8898b7a7`
- Subject: `G77-59: assess Candidate H instantiation contract`
- Immediate parent: `3d21fd574c7c0c0e4f19914e76ea0c0609c7df95`
- Proposal-start worktree state: clean
- Authenticated G77-58 SHA-256:
  `912997ee8327b5cc3bc7f4fb02b865c876d34aeb1105fb962864a3f990a301a5`
- Authenticated G77-59 SHA-256:
  `f33daeab4ec31bcd5d2ed6e47a3732a3d513b03e29136aa79dd1cb24e59f8511`

Predecessor binding:

| Field | Exact binding |
|---|---|
| predecessor proposal | `G77_58_EXTERNAL_CONSTITUENT_CANDIDATE_H_INSTANTIATION_CONTRACT_CONSTITUTIONAL_DESIGN_PROPOSAL_V1` |
| predecessor digest | `sha256:912997ee8327b5cc3bc7f4fb02b865c876d34aeb1105fb962864a3f990a301a5` |
| authoritative assessment | `G77_59_INDEPENDENT_CONSTITUTIONAL_IMPACT_ASSESSMENT_EXTERNAL_CONSTITUENT_CANDIDATE_H_INSTANTIATION_CONTRACT_V1` |
| assessment digest | `sha256:f33daeab4ec31bcd5d2ed6e47a3732a3d513b03e29136aa79dd1cb24e59f8511` |
| assessment class | `UNRESOLVED_CONSTITUTIONAL_IMPACT` |

Reporting date: 2026-08-09.

Objective:

Create only the proposal-only Revision 2 successor of G77-58 and close only
G77-59 blockers B01 through B04. The repair introduces no authority, no
receiver, no production route, no root mutation, and no instantiated artifact.

This proposal does not implement, Ratify, externally adopt, create a Human
Act, create a Target instance, create a Certification instance, publish,
activate, execute BEGIN, mutate a root, perform CDP or CLIA work, deploy, or
change production.

## Exact G77-59 Blocker Closure

| Blocker | Revision 2 closure | Claim |
|---|---|---|
| `G77_59_B01_TARGET_V4_REQUIRES_INELIGIBLE_TARGET_V3_PREDECESSOR` | add forward `ConstitutionalMetaRepairInitialAdoptionTargetV5`; bind the immutable G77-44/G77-45 and G77-58/G77-59 history directly; require the real unresolved classes; require neither a TargetV3 nor TargetV4 instance | `ADDRESSED_PROPOSAL_ONLY` |
| `G77_59_B02_TARGET_V4_DOWNSTREAM_EXACT_TARGET_V3_CONTRACTS_UNVERSIONED` | enumerate every target consumer; version the seven contracts whose validation meaning changes; retain only pair-opaque consumers under an explicit closed compatibility rule | `ADDRESSED_PROPOSAL_ONLY` |
| `G77_59_B03_P009_TARGET_EXACT_SEMANTICS_CHANGED_WITHOUT_PROOFSET_CERTIFICATION_VERSION_BINDING` | replace ProofSetV2/CertificationV2 for this contract with ProofSetV3/CertificationV3 and the unique code `P009_TARGET_V5_EXACT`; Certification remains predicate-only | `ADDRESSED_PROPOSAL_ONLY` |
| `G77_59_B04_ABANDONED_SAME_EVENT_RETRY_CONTRADICTS_IMMUTABLE_TARGET_V4_ROOT_BINDING` | separate one stable founding-event identity and TargetV5 origin root from a root-bound attempt identity; every ABANDONED retry uses the same event/Target, the new current root, a new attempt sequence, and the exact preceding ABANDONED commitment | `ADDRESSED_PROPOSAL_ONLY` |

These are proposal claims. Only a later independent assessment may confirm
them.

## Minimum Lawful Successor Target

TargetV4 remains immutable rejected proposal content and is never treated as
an eligible predecessor. TargetV3 remains immutable historical schema content;
because it requires a false resolved G77-45 class, no conforming TargetV3
instance is presumed or fabricated.

Revision 2 proposes the next forward version in the same target family:
`ConstitutionalMetaRepairInitialAdoptionTargetV5`. It has no predecessor-target
pair. It authenticates historical evidence directly:

- exact G77-36, G77-37, G77-38, and G77-39 pairs;
- exact G77-44 proposal pair and G77-45 assessment pair, with G77-45 class
  exactly `UNRESOLVED_CONSTITUTIONAL_IMPACT` and
  `historical_target_v3_status = INELIGIBLE_SCHEMA_HISTORY_ONLY`;
- exact G77-52 proposal pair and G77-53 assessment pair with the authoritative
  G77-53 class;
- exact G77-57 boundary-audit pair and classification;
- exact G77-58 proposal pair and G77-59 assessment pair, with G77-59 class
  exactly `UNRESOLVED_CONSTITUTIONAL_IMPACT`;
- this G77-60 proposal pair and a future independent G77-60 assessment pair,
  whose assessment class must be the exact eligible class required by G70
  before any later Ratification consideration; and
- the unchanged normative successor payload, scope, status, topology, root,
  success, dormancy, and ordinary-G70-exclusivity contracts.

The authenticated historical digests used by this proposal include:

| Artifact | SHA-256 |
|---|---|
| G77-44 | `03026b9ff5df38e05ffe08e0d834d0ac83d1b04efc3681f6ea2aff4165801c0a` |
| G77-45 | `d3b07e92d0f7b96aea515d979118dcc65c65c4488563122272905d6219e21f38` |
| G77-52 | `a55fe696c011d5edb6450f6b800925f8c5f33a1e9345a85adc20a0d0f358b18a` |
| G77-53 | `3ca5bcd6a91005c5ef34b7ef4b6fd4cb01bc9b2ea2c76db8b35b187938706658` |
| G77-57 | `e7f1b7b507d9e300342ecb905e3cc9b20c96b12c04b084056af6ab07988483c6` |
| G77-58 | `912997ee8327b5cc3bc7f4fb02b865c876d34aeb1105fb962864a3f990a301a5` |
| G77-59 | `f33daeab4ec31bcd5d2ed6e47a3732a3d513b03e29136aa79dd1cb24e59f8511` |

TargetV5 uses the following complete root-binding distinction:

~~~text
founding_event_origin_root_pointer_identity
founding_event_origin_root_pointer_digest
founding_event_origin_root_identity
founding_event_origin_root_digest
founding_event_origin_root_generation
founding_event_origin_constitutional_state_identity
founding_event_origin_constitutional_state_digest
founding_event_origin_active_constitution_identity
founding_event_origin_active_constitution_digest
root_binding_mode = STABLE_EVENT_ORIGIN_PLUS_PER_ATTEMPT_CURRENT_ROOT
~~~

These origin fields are immutable Target content. They identify the one
founding event's initial constitutional baseline; they are not asserted to be
the current serialization root after an ABANDONED attempt. Currentness belongs
only to the versioned per-attempt ProofSet/Certification/Transition chain.
Target substitution, origin rebinding, payload substitution, and scope
substitution all fail closed.

## Exact Consumer Closure and Minimality

Every discovered target consumer is classified below. `PAIR_OPAQUE` means the
retained contract hashes and compares an exact identity/digest pair but assigns
no TargetV3-specific predicate, lifecycle state, or authorization meaning. Its
meaning is unchanged; accepting the pair is legal only when TargetV5 itself,
this exact compatibility table, and a later confirming assessment all resolve.

| Consumer | Existing constraint | Revision 2 treatment | Reason |
|---|---|---|---|
| target artifact | invalid TargetV3 dependency in proposed TargetV4 | `TargetV5` | direct historical authentication without an invalid target predecessor |
| external SourceCommitment, Universe, external Candidate Census, SourceEvidence, RecognitionProof, InstrumentCommitment, Instrument, Human Decision/Finality, and decision disposition | exact `pair(target)` carrier | `PAIR_OPAQUE_DIRECT_REUSE` | no target version token or target-specific reduction is interpreted |
| exact-target ordinary-chain Census | exact TargetV3 semantics | retained family `artifact_version = V2` | target selection is semantic and must change visibly |
| `OrdinaryCAPReachabilityStateV1` | exact TargetV3 plus exact-target Census | `OrdinaryCAPReachabilityStateV2` | both target and Census version change |
| `ExternalConstituentFoundingEligibilityProofSetV2` | P009 means exact TargetV3 | `ExternalConstituentFoundingEligibilityProofSetV3` | P009 and retry attempt semantics change |
| `ExternalConstituentFoundingEligibilityCertificationV2` | certifies ProofSetV2 predicate root | `ExternalConstituentFoundingEligibilityCertificationV3` | exact ProofSet version/predicate vocabulary binding required |
| `ExternalConstituentFoundingAdoptionTransitionV2` | one current predecessor root and initial BEGIN path | `ExternalConstituentFoundingAdoptionTransitionV3` | must distinguish initial BEGIN from retry-after-ABANDONED without a second BEGIN |
| `CandidateHOneShotDormancyRebaseGuardV1` | exact TargetV3 closure | `CandidateHOneShotDormancyRebaseGuardV2` | target, attempt, Transition, and CAP State meanings change |
| Snapshot, Fence, BEGIN CAS, consuming disposition | initial-attempt exact pairs | `INITIAL_ATTEMPT_ONLY_DIRECT_REUSE` | their BEGIN ordering and CAS meaning are unchanged and are forbidden on retry |
| MetaRepairTransition, MetaRepairState, root token, R0/R1/R2 snapshots, CommitMarker, ReadBack, terminal commitment, Dormancy, successful disposition/Receipt | resolve exact predecessor pairs but do not independently interpret a target version | `PAIR_OPAQUE_EXPLICIT_COMPATIBILITY` | downstream identity changes mechanically; no local target predicate changes |
| Replay and CRO | read exact immutable pairs | `DIRECT_REUSE` | read-only/passive authority remains unchanged |

The compatibility rule is closed: an unlisted consumer, a consumer containing
a TargetV3 or TargetV4 constant, a half-present pair, an unknown version, or a
consumer that interprets Target semantics cannot use compatibility and must
fail closed. No retained V1/V2 contract is relabelled with new meaning.

Exactly seven schema-version successors are proposed:

1. `ConstitutionalMetaRepairInitialAdoptionTargetV5`;
2. retained exact-target ordinary-chain Census family V2;
3. `OrdinaryCAPReachabilityStateV2`;
4. `ExternalConstituentFoundingEligibilityProofSetV3`;
5. `ExternalConstituentFoundingEligibilityCertificationV3`;
6. `ExternalConstituentFoundingAdoptionTransitionV3`; and
7. `CandidateHOneShotDormancyRebaseGuardV2`.

No eighth version is justified: all remaining consumers are demonstrably
pair-opaque or initial-only. No new canonical artifact family is introduced.

## P009, ProofSet, and Predicate-Only Certification

ProofSetV3 has a new immutable predicate vocabulary. Ranks and meanings other
than the three explicit rows below remain byte-semantically identical to V2:

| Rank | ProofSetV3 code | Exact meaning |
|---:|---|---|
| 009 | `P009_TARGET_V5_EXACT` | resolved artifact is exact TargetV5 and every direct historical, origin, payload, scope, and successor-contract field validates |
| 014 | `P014_ATTEMPT_AUTHORIZATION_EXACT` | initial row has exact decision-bound ADOPT authorization; retry row has exact same-event CONSUMING disposition and immediately preceding ABANDONED commitment |
| 015 | `P015_ATTEMPT_PREDECESSOR_ROOT_CURRENT` | ProofSet attempt root pair/generation equals the one current root pointer read-back at proof finalization |
| 020 | `P020_NO_PRIOR_SUCCESS_OR_EXTERNAL_CONFLICT` | no successful disposition/Receipt exists; prior ABANDONED is eligible only under the retry row; any other terminal or external conflict rejects |

The string `P009_TARGET_EXACT` is not reused. ProofSetV2 keeps its one
historical TargetV3 meaning. ProofSetV3 contains the exact TargetV5 pair,
stable event identity, attempt identity, attempt sequence, attempt kind,
current attempt root pair/generation, and conditional preceding ABANDONED pair.

CertificationV3 binds exactly:

~~~text
exact ProofSetV3 identity/digest and predicate-root digest
exact TargetV5 identity/digest
exact founding_event_identity
exact attempt_identity, attempt_sequence, and attempt_kind
exact current attempt root identity/digest/generation
exact Instrument and Human Finality pairs
eligibility_result = ELIGIBLE only when every V3 predicate is PASS
~~~

CertificationV3 is predicate-only. It cannot create authority, choose a
Target, issue a Human decision, allocate a root token, execute BEGIN, perform
CAS, write a root, or authorize a later phase without the exact independent
predecessor contracts.

## Stable Event and Per-Attempt Root Model

One stable scalar identifies the single founding event:

~~~text
founding_event_identity = candidate-h-founding-event-sha256:SHA256(canonical({
  contract_version,
  target_v5_identity, target_v5_digest,
  instrument_identity, instrument_digest,
  human_finality_identity, human_finality_digest,
  decision_disposition_identity, decision_disposition_digest,
  target_disposition_domain_identity,
  target_disposition_slot_identity,
  target_disposition_epoch,
  instrument_sequence = 1
}))
~~~

It excludes current root, generation, token, attempt time, and failure reason.
Consequently retry cannot create another event or founding authority.

Each execution attempt has a distinct root-bound scalar:

~~~text
attempt_identity = candidate-h-founding-attempt-sha256:SHA256(canonical({
  contract_version,
  founding_event_identity,
  attempt_sequence,
  attempt_kind,
  attempt_predecessor_root_identity,
  attempt_predecessor_root_digest,
  attempt_predecessor_root_generation,
  predecessor_abandoned_commitment_identity,
  predecessor_abandoned_commitment_digest
}))
~~~

Presence is exact:

| Attempt row | Sequence | Current root | Prior ABANDONED pair | External authorization | BEGIN |
|---|---:|---|---|---|---|
| `INITIAL_BEGIN` | 1 | exact TargetV5 origin root and current read-back | canonical null | exact decision-bound ADOPT slot | exactly once under retained Fence/CAS |
| `RETRY_AFTER_ABANDONED` | previous + 1 | exact current R2-equivalent root produced/read back by immediately preceding ABANDONED commitment | exact immediately preceding commitment | exact same-event CONSUMING slot | forbidden; existing consuming disposition is reused |

For both rows, current root business content must equal the TargetV5 origin
active Constitution and retained R1 business image. Only the serialization
envelope, current root identity/generation, and the later allocated token
ordinal may advance. The target and event are byte-identical.

TransitionV3 repeats the V3 proof/certification/event/attempt/current-root
pairs. On the initial row it permits the unchanged Snapshot -> Fence -> BEGIN
chain. On a retry row it requires the exact old consuming disposition, exact
old ABANDONED commitment and terminal read-back, and forbids Snapshot, Fence,
BEGIN, a new decision disposition, and any external slot CAS.

The later root-token allocation remains inside the one existing serialization
domain. It binds `attempt_identity`; an ABANDONED token is terminal and never
reused. Retry allocates the next ordinal under the retained coordinator CAS.
Duplicate retry for the same current root and preceding ABANDONED pair returns
the same attempt identity. Different bytes under that identity fail closed.

## Identity DAG

~~~text
immutable G77-36..39 history
+ G77-44/G77-45 actual unresolved history
+ G77-52/G77-53 confirmed Revision 7 history
+ G77-57 audit
+ G77-58/G77-59 actual unresolved history
+ G77-60/future independent assessment
+ origin root/Constitution + payload/scope/success contracts
-> stable TargetV5

TargetV5 + Instrument + Human Finality + decision disposition + fixed slot
-> stable founding_event_identity

initial:
  founding event + origin/current root
  -> attempt 1 -> ProofSetV3 -> CertificationV3 -> TransitionV3
  -> retained Snapshot -> Fence -> BEGIN CAS -> CONSUMING disposition

retry:
  same founding event + immediately preceding ABANDONED commitment
  + its exact new current-root read-back
  -> attempt n+1 -> ProofSetV3 -> CertificationV3 -> TransitionV3
  -> no BEGIN and no external CAS

attempt -> exact-target CensusV2 -> CAP StateV2 -> GuardV2
-> retained one coordinator/token/root chain
-> CONSUMED success OR ABANDONED terminal commitment

CONSUMED -> successful disposition -> Receipt -> terminal Dormancy
ABANDONED -> same event may produce only the next root-bound attempt
~~~

All arrows point from finalized predecessor to successor. TargetV5 never binds
a TargetV3/V4 instance. The stable event never binds a later attempt. An
attempt never binds its later token or result. No identity cycle exists.

## Authority DAG

~~~text
External Constituent authority source
-> authenticated external evidence and one-shot Instrument

Human Authority
-> one exact Human decision and finality evidence

external source + Human finality + constitutional predicates
-> predicate-only CertificationV3
-> evidence eligibility only

existing root serialization owner
-> one coordinator/token/root mutation domain

ordinary G70 lifecycle
-> exclusive post-founding amendment path

HIC/CHE -> transport only
Replay -> read-only reconstruction only
CRO -> passive observation only
~~~

No arrow transfers external or Human authority into Certification, HIC, CHE,
Replay, CRO, or the serialization owner. BEGIN consumes the one external slot;
retry reads the same CONSUMING disposition and cannot perform BEGIN again.
TargetV5 is evidence, not an authority source. There is no self-authorization,
authority migration, reusable founding receiver, second Human decision source,
or persistent founding path.

## Crash, Retry, Concurrency, and Revocation

| Condition | Deterministic result |
|---|---|
| duplicate transport | exact correlation/idempotency returns the same evidence; different content rejects |
| duplicate Human evidence | exact Human decision/finality identity returns the same pair; a second or conflicting decision rejects |
| concurrent initial attempts | one current-root/slot/Fence/BEGIN CAS winner; losers read back the winner or reject |
| crash before ProofSet/Certification | no successor authority or mutation; reconstruct from immutable inputs |
| crash before BEGIN | slot remains decision-bound ADOPT; same attempt bytes may resume |
| crash during BEGIN | retained dual read-back distinguishes no commit from exact CONSUMING commit; no inferred state |
| crash after BEGIN | exact consuming disposition is reconstructed; BEGIN is not repeated |
| `CONSUMED` | success disposition/Receipt and terminal Dormancy; every retry is permanently rejected |
| `ABANDONED` before successful root commit | old token/attempt terminal; R2-equivalent root/read-back becomes current; only same-event next attempt is eligible |
| duplicate ABANDONED retry | same current root, sequence, and prior commitment derive the same attempt; competing next-root token uses retained CAS winner |
| target or event substitution on retry | event identity mismatch; reject before proof eligibility |
| stale root on retry | P015 fails; no CertificationV3, TransitionV3, or allocation |
| revocation before BEGIN | initial Fence/current status fails; no BEGIN |
| revocation concurrent with BEGIN | retained status/Fence/CAS ordering yields exactly one linearized result |
| revocation after BEGIN | cannot reinterpret the consumed founding event; it can constrain later ordinary authority only under existing rules |

## Machinery and Exact Counts

| Measure | Before | After proposal | Delta |
|---|---:|---:|---:|
| `production_paths` | 1 | 1 | 0 |
| `parallel_production_paths` | 0 | 0 | 0 |
| `persistent_founding_paths` | 0 | 0 | 0 |
| `permanent_authority_owners_added` | 0 | 0 | 0 |
| `canonical_artifact_families_added` | 0 | 0 | 0 |
| `schema_versions_added` | 0 | 7 | +7 |
| `root_fields_added` | 0 | 0 | 0 |
| `root_pointers_added` | 0 | 0 | 0 |
| `serialization_domains_added` | 0 | 0 | 0 |
| `HIC_families` | 1 | 1 | 0 |
| `CHE_definitions` | 1 | 1 | 0 |
| `Ratification_lifecycles` | 1 | 1 | 0 |

`root_fields_added = 0` means no field is added to the canonical root schema.
The versioned evidence schemas reuse existing root identity/digest/generation
bindings and assign them the explicit origin or current-attempt role.

Seven versions are the minimum closed repair: one for the target, two for the
ordinary exact-target closure, two for P009/Certification, one for the
initial-versus-retry transition, and one for the exact-target/root-bound Guard.
Fewer versions would silently give at least one immutable contract two
meanings. More versions would duplicate pair-opaque machinery without closing
an additional blocker.

## Reuse Impact Assessment

1. **Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?**

   Ponovno se uporabijo Human Authority, transportna HIC/CHE meja, zunanji
   dokazni izvor in enkratni Instrument, nespremenjena Fence/BEGIN CAS ureditev
   za prvi poskus, ena korenska serializacijska domena, R0/R1/R2 in terminalni
   commitment mehanizmi, običajni G70 življenjski cikel, Replay in CRO.

2. **Katere nove zmogljivosti (če sploh) nastanejo?**

   Nastaneta le predlagani dokazni ločitvi stabilnega ustanovitvenega dogodka
   od korensko vezanega poskusa ter sedem nujnih naslednikov shem. Ne nastane
   nova oblast, lastnik, pot, družina artefaktov ali izvajalna zmogljivost.

3. **Ali katera obstoječa zmogljivost postane nedosegljiva?**

   Ne. Neveljavna TargetV3 in predlagana TargetV4 nista aktivni certificirani
   zmogljivosti. Vse aktivne semantične, Governance, Replay, CRO, rollback in
   običajne G70 zmogljivosti ostanejo dosegljive po isti poti.

4. **Ali implementacija oziroma predlagani mehanizem ustvarja vzporedni tok?**

   Ne. Predlog uporablja isti zunanji dogodek, isto Human odločitev, isto
   serializacijsko domeno in isto produkcijsko pot. Ponovni poskus po ABANDONED
   ni druga ustanovitvena pot in ne izvede drugega BEGIN.

5. **Ali zmanjšuje ali povečuje število produkcijskih poti?**

   Ne zmanjšuje in ne povečuje. Število ostane ena produkcijska pot, nič
   vzporednih produkcijskih poti in nič trajnih ustanovitvenih poti.

# 2. Code Evidence

## Public API

No public or runtime API is added or modified. TargetV5, the stable event and
attempt identities, and the seven schema versions are Constitutional proposal
contracts only. No model, schema, validator, route, command, persistence
primitive, credential, provider, session, or runtime object is implemented.

## Orchestration Entry Point

The sole Human production entry remains:

~~~text
Human -> permitted HIC profile -> sole CHE -> exact eligible owner
-> sole CHE Response/Continuation -> same HIC
~~~

Candidate H evidence does not create another Human entry. Initial BEGIN and
same-event retry stay inside the retained one root-serialization owner. HIC
and CHE transport; neither chooses the Target, Human decision, proof result,
root, retry, or authority.

## Semantic Reductions

### Target lineage

~~~text
authoritative G77-45 class = UNRESOLVED
AND authoritative G77-59 class = UNRESOLVED
AND no TargetV3/V4 instance dependency
AND every required historical pair exact
AND future G77-60 assessment eligible under G70
-> TargetV5 may be considered by a later Ratification lifecycle

otherwise -> INELIGIBLE
~~~

### Exact target predicate

~~~text
ProofSet version = V3
AND code = P009_TARGET_V5_EXACT
AND exact TargetV5 resolves
AND all TargetV5 direct fields validate
-> P009 PASS

V2 code, TargetV3/V4, unknown target, or mismatch -> FAIL
~~~

### Same-event retry

~~~text
same founding_event_identity + same TargetV5
+ exact preceding ABANDONED commitment
+ exact new current root/read-back
+ sequence = previous + 1
+ no prior success
-> one deterministic retry attempt

new event, new Target, stale root, missing commitment,
reused token, second BEGIN, or prior success -> REJECT
~~~

## Public Validators

No validator is implemented. A future separately authorized CDP validator
must reject:

- any TargetV5 that binds a TargetV3 or TargetV4 instance;
- any false G77-45 or G77-59 classification;
- any historical, assessment, origin, payload, scope, or successor mismatch;
- an unlisted consumer or unversioned semantic target consumer;
- ProofSet other than V3 or P009 other than `P009_TARGET_V5_EXACT`;
- Certification that does not bind exact ProofSetV3 predicate results;
- Certification performing selection, mutation, or authority creation;
- an initial attempt not rooted at the exact TargetV5 origin/current root;
- a retry with a changed event, Target, Instrument, Human finality, slot, or
  origin;
- a retry missing the immediately preceding ABANDONED commitment/current
  read-back or using a non-successor sequence;
- any retry BEGIN, external status CAS, reused token, or stale root;
- any attempt after CONSUMED, successful disposition, Receipt, or Dormancy;
- half-present pairs, unknown fields, unknown versions, or different content
  under one identity;
- Replay/CRO mutation, HIC/CHE semantic authority, or a second authority path;
  and
- topology other than `1 / 0 / 0` for production, parallel, and persistent
  founding paths.

## Canonical Data Models

| Proposed or retained model | Owner/boundary | Function |
|---|---|---|
| TargetV5 | Constitutional evidence; no runtime owner | stable direct historical and origin binding |
| exact-target ordinary Census V2 | retained ordinary CAP evidence owner | exact TargetV5 ordinary G70 chain census |
| OrdinaryCAPReachabilityStateV2 | retained CAP state owner | closes both complete/no-complete exact-target cases |
| ProofSetV3 | retained evidence producer | deterministic predicates and attempt currentness |
| CertificationV3 | retained certification evidence owner | predicate-only result binding |
| TransitionV3 | retained founding transition owner | initial-versus-retry predecessor closure |
| GuardV2 | retained meta-repair guard owner | exact TargetV5/attempt/CAP/root authorization evidence |
| root/token/commit chain | existing serialization owner | one CAS domain; unchanged families |
| Replay | owner-local custodian | deterministic read-only reconstruction |
| CRO | passive Observatory | non-authoritative observation |

## Deterministic Algorithms

1. Authenticate exact repository, G77-58, G77-59, and required historical
   bytes and classifications.
2. Resolve TargetV5 directly; reject any target-predecessor dependency.
3. Resolve the consumer table; apply a new version to semantic consumers and
   exact pair compatibility only to listed pair-opaque consumers.
4. Derive the stable event identity without current-root or attempt inputs.
5. Read one current root and derive the root-bound attempt identity.
6. Evaluate ProofSetV3 in fixed rank order, including the unique TargetV5
   P009 and attempt-aware P014/P015/P020 rows.
7. Produce CertificationV3 only as an exact predicate result.
8. For sequence 1, execute retained Snapshot/Fence/BEGIN once. For retry,
   validate the existing CONSUMING disposition and forbid BEGIN.
9. Derive CensusV2, CAP StateV2, GuardV2, then use the retained one-token/root
   CAS and terminal commitment algorithms.
10. On ABANDONED, read back the new current root and permit only the same
    event's next sequence. On CONSUMED, terminalize permanently.
11. Replay the exact immutable DAG without live selection, repair, CAS, or
    mutation.

## Responsibility Boundaries

| Responsibility | Exact authority | Negative boundary |
|---|---|---|
| originate external constituent authority | authenticated external source | no runtime/root/Human authority |
| issue Human decision | Human Authority | sole Human decision source |
| transport | HIC/CHE | no semantic, certification, or mutation authority |
| define proposal contracts | G77-60 proposal | no instance or activation authority |
| assess G77-60 | future independent Governance | not performed here |
| evaluate predicates | ProofSetV3/CertificationV3 owner | no selection, BEGIN, CAS, or authority creation |
| serialize root/token | existing serialization owner | one existing domain only |
| authorize ordinary amendments | existing G70 lifecycle | exclusive after founding |
| reconstruct | Replay | read-only; no inference or repair |
| observe | CRO | passive; no control or certification |
| Ratify/activate/implement | later separately authorized actors | absent here |

## Repository Evidence

Evidence is limited to authenticated Git identity, immutable governance
artifacts through G77-59, exact SHA-256 predecessor bytes, the G77-59 four-row
blocking set, G48 structure, G69 Human/HIC/CHE boundaries, G70 CAP ordering,
G76 forward identity/DAG constraints, and retained Candidate H one-shot and
root-serialization contracts. No runtime result, external evidence, Human Act,
provider result, deployment state, or test fixture supplies Constitutional
semantics.

# 3. Constitutional Self-Assessment

## Verified as Proposal Structure

- The exact G77-58/G77-59 bytes and actual unresolved classes are preserved.
- B01 is closed without a TargetV3/V4 instance or fabricated assessment.
- B02 has a complete enumerated consumer rule and seven justified versions.
- B03 gives P009 one new immutable code and binds ProofSetV3/CertificationV3.
- Certification remains predicate-only.
- B04 separates stable event/Target identity from root-bound attempt identity.
- ABANDONED retry uses the next current root and ordinal without a second
  BEGIN, external CAS, event, Target, authority, or Human decision.
- Identity and Authority DAGs are finite, forward, and non-self-authorizing.
- Crash, duplicate, concurrency, CONSUMED, ABANDONED, and revocation cases are
  deterministic and fail closed.
- One production path, zero parallel paths, and zero persistent founding paths
  are preserved.
- Exactly one proposal artifact is added; no predecessor or runtime file is
  changed.

## Not Verified

- No independent G70-03 assessment of G77-60 has occurred.
- No TargetV5, event, attempt, ProofSet, Certification, Transition, Census,
  State, Guard, token, root, commitment, disposition, Receipt, or Dormancy
  instance exists.
- No Human Ratification, external adoption, publication, activation, BEGIN,
  root mutation, CDP, CLIA, deployment, or production action occurs.
- No runtime schema, validator, persistence, CAS, crash recovery, Replay
  reader, or enforcement is implemented or tested.
- Existing partial conformance, hook drift, custody, privacy, deployment, and
  external-system limitations remain visible and unchanged.
- Proposal self-assessment cannot substitute for independent assessment or
  grant implementation authority.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| G48 structure | exactly six top-level sections and required Code Evidence subsections | heading review | `PASS` |
| repository authentication | commit/tree/parent/subject | Git review | `PASS` |
| G77-58/G77-59 authentication | exact SHA-256 pairs | digest review | `PASS` |
| immutable predecessors | no prior artifact modified | repository review | `PASS` |
| exact blocker scope | B01-B04 matrix only | scope review | `PASS` |
| B01 actual history | G77-45/G77-59 remain unresolved | lineage review | `PASS_PROPOSAL` |
| B01 target successor | TargetV5 has no TargetV3/V4 instance edge | schema/DAG review | `PASS_PROPOSAL` |
| B02 consumers | complete semantic/pair-opaque/initial-only table | compatibility review | `PASS_PROPOSAL` |
| machinery minimum | seven versions; zero new families | count review | `PASS_PROPOSAL` |
| B03 P009 | unique V3 code and meaning | predicate review | `PASS_PROPOSAL` |
| B03 Certification | exact V3 predicate binding; no authority | boundary review | `PASS_PROPOSAL` |
| B04 stable event | current root excluded from event identity | derivation review | `PASS_PROPOSAL` |
| B04 retry attempt | new current root/sequence/prior ABANDONED exact | lifecycle review | `PASS_PROPOSAL` |
| no second BEGIN | retry row forbids Snapshot/Fence/BEGIN/external CAS | ordering review | `PASS_PROPOSAL` |
| no reusable receiver | same event only; success terminal | authority review | `PASS_PROPOSAL` |
| identity DAG | finalized predecessors; no backward edge/cycle | G76 review | `PASS_PROPOSAL` |
| authority DAG | no creation/migration/self-authorization | authority review | `PASS_PROPOSAL` |
| crash/concurrency | exact initial/retry/terminal matrix | recovery review | `PASS_PROPOSAL` |
| revocation | before/during/after BEGIN closed | lifecycle review | `PASS_PROPOSAL` |
| Human/HIC/CHE | one Human authority; transport only | G69 review | `PASS_PROPOSAL` |
| ordinary G70 | exclusive after founding | CAP review | `PASS_PROPOSAL` |
| production topology | `1 / 0 / 0` paths | topology review | `PASS_PROPOSAL` |
| Reuse Impact Assessment | all five Slovenian questions answered | completeness review | `PASS` |
| focused G69/G70 tests | 326 focused tests | test review | `PASS` |
| Candidate H/G76 tests | no directly named repository test module discovered | test search | `NOT_PRESENT` |
| balanced fences/trailing whitespace | 20 fences; zero trailing-whitespace matches | format review | `PASS` |
| diff integrity | `git diff --check` | Git review | `PASS` |
| artifact count | exactly one G77-60 file and no other mutation | repository review | `PASS` |
| runtime implementation | proposal-only work | scope review | `NOT_APPLICABLE` |
| independent assessment | required next | governance review | `NOT_REACHED` |

# 5. Repository Mutation Summary

Modified files:

- added
  `docs/governance/G77_60_EXTERNAL_CONSTITUENT_CANDIDATE_H_INSTANTIATION_CONTRACT_CONSTITUTIONAL_DESIGN_PROPOSAL_REVISION_2_V1.md`
  as the sole G77-60 proposal artifact.

No existing file is intentionally changed. G77-58, G77-59, and all prior
artifacts remain byte-identical. No code, test, schema, configuration,
credential, session, provider, persistence, runtime, route, deployment, root,
or external state is mutated.

Boundary preservation:

- proposal only and independently unassessed;
- no Human or external evidence created;
- no Target or Certification instance created;
- no Ratification, Publication, Activation, BEGIN, CDP, CLIA, deployment, or
  production authority exercised;
- Human Authority remains sole; HIC/CHE remain transport only;
- Certification remains predicate-only;
- ordinary G70 remains exclusive after a successful founding event; and
- one production path, zero parallel paths, and zero persistent founding paths
  remain unchanged.

# 6. Certification Verdict

G77_CANDIDATE_H_INSTANTIATION_CONTRACT_PROPOSAL_REVISION_2_ESTABLISHED
