# 1. Implementation Summary

Generation: G77-73

Report and proposal identity:
`G77_73_CANDIDATE_H_AUTHENTICATION_REDESIGN_REVISION_3_SIGNER_OUTCOME_DURABILITY_AND_EXTERNAL_CAPACITY_SOURCE_AUTHENTICATION_CLOSURE_V1`

Proposal revision: `3`

Proposal status: `PROPOSAL_ONLY_UNASSESSED`

Artifact class:
`BLOCKER_TARGETED_CANDIDATE_H_CONSTITUTIONAL_DESIGN_PROPOSAL_NON_IMPLEMENTING_NON_ACTIVATING`

Constitutional baseline: authenticated committed G0 through G77-72.

Controlling assessment verdict:
`G77_71_CONSTITUTIONAL_IMPACT_REQUIRES_REWORK`

Controlling blockers:

- `G77_71_B01_SIGNER_OUTCOME_DURABILITY_AND_RECOVERY_CONTRACT_ABSENT`; and
- `G77_71_B02_EXTERNAL_CAPACITY_SOURCE_AUTHENTICATION_UNDERCLOSED`.

Reporting date: 2026-08-10.

Objective:

Close only the two G77-72 blockers by versioning the two failed G77-71
evidence contracts. Preserve the independently surviving HumanDecisionV2,
P012 contract-version dispatch, thirty-group consumer graph, downstream
Candidate H spine, one-shot boundaries, owner separations, and topology.

Repository identity at proposal start:

- branch: `master`;
- commit: `149bc8f9518eb5353ab9a15187985b4671eb6678`;
- tree: `260d2ce8e72130e19c495ac6de10e3d2525fa144`;
- subject: `G77-72: assess Candidate H authentication redesign revision 2`;
- G77-72 status: committed and tracked at HEAD; and
- worktree status: clean.

This proposal does not implement, instantiate, activate, sign, create an
external evidence instance, perform a Human act, select a disposition, create
BEGIN, mutate a root, grant authority, deploy, produce an effect, or commit.

## Authenticated Predecessors

| Artifact | SHA-256 | Role |
|---|---|---|
| G48-00 | `16508d1a77c4b3f07d37861e74d85f77896be16da01ca26cbc07a658ddf2c0eb` | reporting standard |
| G69-07 | `ac8665d902abef943b12ee4198e99884930f888eb7d1d3387e686943ea80bd61` | `HUMAN_AUTHORITY` custody boundary |
| G70-03 | `7006a1c03e654542ac7d77fd18fdee996c36e0e20de7425c94c8f3ac6c2bc00d` | assessment discipline |
| G76-06 | `29f06a93d5b7ce610c161487bc1e3a01f6d7d063b22393e0347b0da20b281dbc` | identity and DAG rules |
| G77-42 | `b379cb057282aaf7d10c6e6e3f8a55053a630b19a0a0ad80e8159a0222b316a6` | accepted external Premise model and Candidate H origin |
| G77-44 | `03026b9ff5df38e05ffe08e0d834d0ac83d1b04efc3681f6ea2aff4165801c0a` | external CAS/read-back precedent |
| G77-52 | `a55fe696c011d5edb6450f6b800925f8c5f33a1e9345a85adc20a0d0f358b18a` | Candidate H model |
| G77-53 | `3ca5bcd6a91005c5ef34b7ef4b6fd4cb01bc9b2ea2c76db8b35b187938706658` | model assessment |
| G77-62 | `661394be4e32b2e965f6a906e865a78128572084bbe52c5d0aad3bfdd5deca1e` | full transitive consumer graph |
| G77-63 | `73190f6a7f919469b7d67f512cf955e9c5531b9f41170229061760f03c2ad7fe` | Revision 3 assessment |
| G77-64 | `ac3deaf40e7f06c04e3396b161194b258b7ae993b65d9ee719fb1170fc4ac0c6` | Certification-time closure |
| G77-65 | `9d5c40e861aa11d2f6ee173016f50dde57d4026fd85cf124b9c887b8e1449569` | convergence assessment |
| G77-66 | `9f33fade3019d5a3ddf4e1e286fccc011e812274af71076b4ddd0f96f601859d` | lifecycle boundary |
| G77-67 | `236c613844532fb44ba9aa473df46fccea75fc603271373b6d7bf0fd692eff2b` | adoption preparation |
| G77-68 | `4331fcbc3849f71b2f6c07a6f60c39af6c24697bccdf3ef0f5bf8d1411abe027` | external handoff boundary |
| G77-69 | `329f952e7514e6e932579d1df12823f4bad8eb948806fa096897c270dab1103f` | Revision 1 redesign assessment |
| G77-70 | `5c6fe6138391fbb58a3bb20e047585a664d94f0a07e0be7ed3368a444f67563c` | Revision 1 hostile assessment |
| G77-71 | `94f8117659cc000586cd8017a58a70254da0610e67c0d3c414cc093a316a4da9` | failed Revision 2 proposal |
| G77-72 | `90e990d95b5a855643fd032ccee2b7a6f7300496fc16fb0d3f2eb27825369639` | controlling Revision 2 assessment |

Authenticated HFD lineage:

| Artifact | SHA-256 | Role |
|---|---|---|
| HFD-01 | `f23c25a36a638961ffca25861576858e7a77c7f715c23e01783f66ad6743e982` | external Human Founder model |
| HFD-02 | `d6c0f2b4f71c40b91d94e47c5d1b38ccd77518b33598b792aa7c7c7051e084a6` | protocol Revision 1 |
| HFD-03 | `1d8cceb4741bac022c82298db230e6fe8b6dce46eae32bf221de8cf14aa5b5e5` | Revision 1 assessment |
| HFD-04 | `5030cd2d90cbb792fa3ee3ed2777057ad269619b091b344b390e8d6247d85eb5` | exact `P_auth_v2` |
| HFD-05 | `e3c49ecd8824b53ff6bce5286e762fda020545745c11e28128d3a56d2ba2d5a0` | Revision 2 assessment |
| HFD-06 | `f9505f3beac9d9e43b2991421c78110eab1f1ff8cf6ca2a97df2ed4d79c8f886` | frozen compatibility stop |

No predecessor mismatch is observed.

## Blocker-Targeted Closure Result

| G77-72 blocker | Revision 3 closure | Result |
|---|---|---|
| B01 signer outcome durability | `HumanFounderAuthenticationResultReadBackEvidenceV2` embeds an exact signer-owned operation slot, one-winner acceptance CAS, invocation receipt, atomic write-before-response outcome store, and authoritative outcome read-back | `ADDRESSED_PROPOSAL_ONLY` |
| B02 capacity source authentication | `HumanFounderExternalCapacityEvidenceV2` signs its exact 32-field authority-bearing core with the already authenticated Premise owner key and binds a source-owned custody/read-back record | `ADDRESSED_PROPOSAL_ONLY` |

No third top-level evidence family is required. Both missing responsibilities
fit their already proposed family boundaries. Because G77-71 V1 schemas are
immutable failed history, the corrected contracts advance to V2 rather than
silently changing V1.

The exact Revision 3 contract-version token is:

~~~text
CANDIDATE_H_AUTHENTICATION_REDESIGN_REVISION_3_V1
~~~

HumanDecision remains artifact version V2 with the same 31-field schema and
uses that identity-bearing contract token. ProofSetV3, CertificationV3, and
TransitionV3 use the same Revision 3 token and retain their artifact versions.

## Required Effect Classifications

| Required classification | Result |
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

## Common Canonical Rules

Revision 3 retains G77-71 CJ1 and common identity formulas. Each corrected
artifact uses this exact envelope:

~~~text
artifact_type
artifact_version
artifact_identity
artifact_digest
contract_version
idempotency_identity
producing_owner
metadata = {}
~~~

For artifact A, `S_A` contains exact type, artifact version, contract version,
producing owner, and every declared semantic field, excluding only self
identity, self digest, idempotency identity, and metadata. `P_A` adds the
idempotency identity.

~~~text
A.idempotency_identity = <idem-prefix>:SHA256(CJ1(S_A))
A.artifact_identity = <identity-prefix>:SHA256(CJ1(P_A))
A.artifact_digest = sha256:SHA256(CJ1(P_A))
~~~

Wrong type/version/contract/owner, unknown field, invalid null, half-pair,
non-CJ1 content, or identity/idempotency collision with different bytes fails
closed.

## B02 Closure — Authenticated Capacity Issuance V2

The corrected family is `HumanFounderExternalCapacityEvidenceV2`, artifact
version V2, identity prefix `human-founder-external-capacity-v2`, and
idempotency prefix `human-founder-external-capacity-idem-v2`. Its producing
owner remains exactly:

~~~text
capacity.producing_owner
  == resolved ExternalConstituentPremiseEvidenceV1.external_authority_identity
~~~

The V2 semantic payload has exactly 34 fields. Fields 01 through 32 are the
unchanged G77-71 authority-bearing core:

~~~text
01 external_premise_identity
02 external_premise_digest
03 external_constituent_model_identity =
     HUMAN_FOUNDER_ONE_SHOT_EXTERNAL_CONSTITUENT_V1
04 human_actor_identity_record
05 external_capacity_record
06 authority_provenance_record
07 authority_competence_record
08 one_shot_scope_record
09 authentication_key_binding_record
10 authentication_verification_profile
11 capacity_status_read_back_record
12 target_identity
13 target_digest
14 human_finality_domain_identity
15 human_finality_domain_digest
16 human_authentication_slot_identity
17 human_authentication_epoch
18 human_decision_slot_identity
19 human_decision_epoch
20 maximum_authoritative_dispositions = 1
21 maximum_human_reviews = 1
22 maximum_authentication_operations = 1
23 maximum_finality_events = 1
24 delegation_permitted = false
25 transfer_permitted = false
26 reset_permitted = false
27 reissue_permitted = false
28 recurrence_permitted = false
29 revival_permitted = false
30 post_founding_special_authority = false
31 ordinary_post_founding_governance_only = true
32 issued_at
33 capacity_issuance_authentication_record
34 capacity_issuance_custody_read_back_record
~~~

The eight core nested records retain their exact G77-71 schemas and equality
rules. The new records do not change actor, capacity, competence, scope, act
key, status, Target, slot, epoch, or one-shot meaning. They authenticate who
issued that exact closed core and prove its durable source custody.

### Exact capacity issuance bytes

`P_capacity_issue_v2` is the exact CJ1 object containing:

~~~text
issuance_domain_identity =
  HUMAN_FOUNDER_EXTERNAL_CAPACITY_ISSUANCE_V2
artifact_type = HumanFounderExternalCapacityEvidence
artifact_version = V2
contract_version =
  CANDIDATE_H_AUTHENTICATION_REDESIGN_REVISION_3_V1
producing_owner
core_field_01 through core_field_32 exactly as displayed
~~~

It excludes only the later issuance-authentication record, later custody
read-back record, final artifact identity/digest/idempotency, and metadata.
No authority-bearing core field is excluded.

~~~text
capacity_issuance_commitment_identity =
  human-founder-capacity-issuance-v2:SHA256(CJ1(P_capacity_issue_v2))
capacity_issuance_commitment_digest =
  sha256:SHA256(CJ1(P_capacity_issue_v2))
capacity_issuance_message = UTF8(CJ1(P_capacity_issue_v2))
~~~

### Capacity issuance authentication record

The complete nested record is:

~~~text
record_type = HUMAN_FOUNDER_CAPACITY_ISSUANCE_AUTHENTICATION_RECORD
record_version = V1
producing_owner
external_premise_identity
external_premise_digest
capacity_issuer_identity
capacity_issuer_identity_scheme
capacity_issuance_commitment_identity
capacity_issuance_commitment_digest
authenticated_message_representation = EXACT_UTF8_CJ1_CAPACITY_ISSUE_V2
authentication_algorithm = ED25519_RFC8032_PURE
public_key_encoding = BASE64URL_NO_PAD_RAW_32_OCTETS
capacity_issuer_public_key
capacity_issuer_key_identity
signature_encoding = BASE64URL_NO_PAD_RAW_64_OCTETS
capacity_issuer_signature
premise_owner_trust_binding_digest
signature_verification_result = TRUE
issued_at
record_digest
~~~

Exact equalities are mandatory:

~~~text
capacity_issuer_identity
  == producing_owner
  == resolved Premise.external_authority_identity

capacity_issuer_identity_scheme
  == resolved Premise.external_authority_identity_scheme

authentication_algorithm
  == resolved Premise.signature_scheme
  == ED25519_RFC8032_PURE

capacity_issuer_key_identity
  == resolved Premise.signature_key_identity
  == human-founder-ed25519-key-v1:SHA256(decoded public key octets)

issued_at == core field 32
~~~

The accepted Premise and its persisted custody/authentication evidence must
already validate before capacity construction. Strict base64url-no-pad decode
must yield 32 public-key octets and 64 signature octets. Verification is
RFC8032 Ed25519 pure over exactly
`UTF8(CJ1(P_capacity_issue_v2))`, with no prehash, context, digest adapter,
alternate encoding, or runtime algorithm selector.

`premise_owner_trust_binding_digest` is SHA-256 over the CJ1 object containing
the exact Premise pair, Premise custody-evidence pair, Premise owner identity
and identity scheme, Premise signature scheme/key identity, decoded public
key digest, and capacity issuance commitment pair. Replay resolves every
input from persisted evidence.

The record digest hashes the complete displayed record excluding only its own
digest. A malformed key/signature, wrong owner/key/premise/core pair,
noncanonical encoding, invalid signature, unknown field, substituted trust
binding, or failed Premise validation rejects CapacityV2.

### Capacity issuance custody read-back record

The second complete nested record is:

~~~text
record_type = HUMAN_FOUNDER_CAPACITY_ISSUANCE_CUSTODY_READ_BACK_RECORD
record_version = V1
producing_owner
external_premise_identity
external_premise_digest
capacity_issuance_commitment_identity
capacity_issuance_commitment_digest
capacity_issuance_authentication_record_digest
capacity_issuer_signature_digest
capacity_issuance_slot_identity
capacity_issuance_epoch
capacity_issuance_generation = 1
predecessor_issuance_status = AVAILABLE
current_issuance_status = ISSUED_FINAL
capacity_issuance_cas_identity
capacity_issuance_cas_digest
capacity_issuance_read_back_identity
capacity_issuance_read_back_digest
stored_core_digest
stored_authentication_record_digest
issuance_logical_instant
read_back_result = EXACT_SIGNED_CAPACITY_ISSUANCE_CURRENT
record_digest
~~~

The Premise owner/custodian atomically installs the exact commitment and
authentication-record digest into its source-owned issuance slot, then reads
them back. The CAS and read-back identities hash their complete displayed
subcontract bodies, excluding their own pairs. `stored_core_digest` equals
the capacity issuance commitment digest; stored authentication record and
signature digests recompute. No wall clock or repository order is used.

The capacity artifact identity binds both new records. The source signature
authenticates every authority-bearing core byte; the later source-owned
read-back authenticates durable custody of that signed issuance. The final
artifact does not sign its own signature or identity, so no cycle exists.

This is the positive edge:

~~~text
already accepted external Premise pair
-> authenticated Premise owner/key/custody
-> valid signature over exact P_capacity_issue_v2
-> source-owned issuance CAS/read-back
-> authenticated actor/capacity/competence/key/status core
-> HumanFounderExternalCapacityEvidenceV2
~~~

Cryptographic validity does not create the external Premise or constituent
authority. Without the independently accepted Premise, the same key and
signature are ineligible. Repository ownership, `HUMAN_AUTHORITY`,
Certification, Governance, deployment control, and key possession alone
cannot populate or approve this chain.

## B01 Closure — Atomic Signer-Owned Outcome V2

The corrected family is
`HumanFounderAuthenticationResultReadBackEvidenceV2`, artifact version V2,
identity prefix `human-founder-auth-result-readback-v2`, and idempotency
prefix `human-founder-auth-result-readback-idem-v2`.

The producing owner/result custodian remains the accepted Premise owner. The
signer operation registry is an exact subdomain of that already proposed
external authentication-result responsibility. It creates no internal owner,
root domain, top-level State family, or production path.

The external authentication slot retains:

~~~text
OPEN -> AUTHENTICATING
AUTHENTICATING -> AUTHENTICATED_FINAL
AUTHENTICATING -> INDETERMINATE_EXHAUSTED
~~~

The signer-owned operation slot is newly exact:

~~~text
AVAILABLE
  -> ACCEPTED_IN_PROGRESS
  -> VALID_SIGNATURE_FINAL

ACCEPTED_IN_PROGRESS
  -> REJECTED_FINAL

ACCEPTED_IN_PROGRESS
  -> INDETERMINATE_FINAL
~~~

All three signer outcomes are terminal. The only logical signer invocation is
the winning `AVAILABLE -> ACCEPTED_IN_PROGRESS` acceptance CAS. Identical
delivery of the same intent returns the same CAS/receipt and does not create
another invocation. A different operation, message, key, capacity, claim, or
intent loses.

The V2 result artifact has exactly 50 semantic fields:

~~~text
01 external_premise_identity
02 external_premise_digest
03 human_founder_capacity_identity
04 human_founder_capacity_digest
05 human_actor_identity
06 human_authentication_slot_identity
07 human_authentication_epoch
08 authentication_sequence = 1
09 authentication_operation_identity
10 authentication_operation_digest
11 authentication_commitment_identity
12 authentication_commitment_digest
13 authenticated_message_representation = EXACT_UTF8_CJ1_P_AUTH_V2_BYTES
14 authenticated_message_digest
15 signature_scheme = ED25519_RFC8032_PURE
16 signature_key_identity
17 signature
18 authentication_result
19 predecessor_authentication_slot_status = OPEN
20 claimed_authentication_slot_status = AUTHENTICATING
21 terminal_authentication_slot_status
22 authentication_claim_cas_identity
23 authentication_claim_cas_digest
24 signer_operation_slot_identity
25 signer_operation_slot_epoch
26 signer_invocation_intent_identity
27 signer_invocation_intent_digest
28 signer_acceptance_cas_identity
29 signer_acceptance_cas_digest
30 signer_invocation_receipt_identity
31 signer_invocation_receipt_digest
32 signer_outcome_identity
33 signer_outcome_digest
34 signer_outcome_read_back_identity
35 signer_outcome_read_back_digest
36 signer_outcome_status
37 one_use_non_equivocation_proof_identity
38 one_use_non_equivocation_proof_digest
39 authentication_terminal_cas_identity
40 authentication_terminal_cas_digest
41 authoritative_read_back_identity
42 authoritative_read_back_digest
43 read_back_authentication_slot_digest
44 signature_verification_result
45 conflict_status
46 retry_permitted = false
47 second_authentication_permitted = false
48 capacity_permanently_exhausted
49 completion_logical_instant
50 terminal = true
~~~

### Signer invocation intent

`P_signer_intent` contains exactly:

~~~text
external Premise pair
CapacityV2 pair
human actor identity
authentication operation pair
authentication claim CAS pair
authentication commitment pair
authenticated message representation and digest
signature scheme and key identity
signer operation slot identity and epoch
authentication sequence = 1
maximum_logical_signer_invocations = 1
~~~

~~~text
signer_invocation_intent_identity =
  human-founder-signer-intent-v1:SHA256(CJ1(P_signer_intent))
signer_invocation_intent_digest =
  sha256:SHA256(CJ1(P_signer_intent))
~~~

The intent is derived only after the outer authentication claim is durably
read back. It contains no signature, signer outcome, terminal CAS,
HumanDecision, Finality, ProofSet, or successor identity.

### Atomic signer acceptance and invocation receipt

`P_signer_acceptance` contains the exact intent, operation, claim, capacity,
message, and key pairs; signer slot/epoch; predecessor `AVAILABLE`; successor
`ACCEPTED_IN_PROGRESS`; invocation sequence 1; maximum logical invocations 1;
and a source-derived acceptance logical instant.

~~~text
signer_acceptance_cas_identity =
  human-founder-signer-acceptance-cas-v1:SHA256(CJ1(P_signer_acceptance))
signer_acceptance_cas_digest =
  sha256:SHA256(CJ1(P_signer_acceptance))
~~~

The signer-owned registry atomically persists that CAS before any signing
primitive may execute. Its authoritative receipt/read-back body contains the
acceptance pair, intent/operation/claim pairs, slot/epoch/sequence, exact
`ACCEPTED_IN_PROGRESS` state, acceptance logical instant, and current slot
digest.

~~~text
signer_invocation_receipt_identity =
  human-founder-signer-invocation-receipt-v1:SHA256(CJ1(P_receipt))
signer_invocation_receipt_digest = sha256:SHA256(CJ1(P_receipt))
~~~

No caller may request signing directly. The caller may submit the same
content-derived acceptance CAS intent and then read the slot. A lost CAS
response is resolved by authoritative read-back. `AVAILABLE` proves no
invocation was accepted; the machine may submit the same intent. An accepted
receipt proves the one invocation exists; the machine may only read it or its
outcome and may never submit another signer operation.

### Signer-owned durable outcome

Only the signer process responsible for the accepted receipt may continue the
same logical invocation. It uses the exact CapacityV2 key/profile and exact
`UTF8(CJ1(P_auth_v2))` message. The signer outcome body contains:

~~~text
intent pair
acceptance CAS pair
invocation receipt pair
operation/claim/capacity/commitment pairs
message representation and digest
signature scheme and key identity
outcome_status =
  VALID_SIGNATURE_FINAL |
  REJECTED_FINAL |
  INDETERMINATE_FINAL
signature = exact value | canonical null
signature_digest = exact digest | canonical null
verification_result = TRUE | FALSE | NOT_APPLICABLE
failure_code = canonical null | exact closed failure token
completion_logical_instant
terminal = true
~~~

~~~text
signer_outcome_identity =
  human-founder-signer-outcome-v1:SHA256(CJ1(P_signer_outcome))
signer_outcome_digest = sha256:SHA256(CJ1(P_signer_outcome))
~~~

The signer registry atomically stores the complete outcome before returning
or exposing a signature. Its read-back binds the outcome pair, accepted
receipt, exact slot/epoch/sequence, terminal status, signature digest or null,
completion instant, and current slot digest.

~~~text
signer_outcome_read_back_identity =
  human-founder-signer-outcome-readback-v1:SHA256(CJ1(P_outcome_read_back))
signer_outcome_read_back_digest =
  sha256:SHA256(CJ1(P_outcome_read_back))
~~~

If the signer crashes after computing a deterministic Ed25519 signature but
before the outcome store commits, the signature cannot be consumed or
returned. The same accepted logical invocation resumes from its persisted
receipt and deterministically recomputes the same Ed25519 result. This is
continuation of one accepted invocation, not a second invocation identity.
The client never calls the signer again.

If signing input is invalid, the signer persists `REJECTED_FINAL`. If the
accepted operation cannot be constitutionally completed or reconstructed,
the signer itself persists `INDETERMINATE_FINAL` with an exact closed failure
token. The client may not infer indeterminacy from timeout, clock, outage, or
missing response. While the signer slot is `ACCEPTED_IN_PROGRESS`, no
HumanDecision or effect is possible and no retry may sign.

### Outer terminal result

Only exact signer outcome read-back may drive the outer terminal CAS:

| Signer outcome | Outer terminal | Result/signature |
|---|---|---|
| `VALID_SIGNATURE_FINAL` and VERIFY TRUE | `AUTHENTICATED_FINAL` | `AUTHENTICATED_VALID`, exact non-null signature |
| `REJECTED_FINAL` | `INDETERMINATE_EXHAUSTED` | `AUTHENTICATION_REJECTED_FINAL`, canonical-null signature |
| `INDETERMINATE_FINAL` | `INDETERMINATE_EXHAUSTED` | `INDETERMINATE_NO_VALID_RESULT`, canonical-null signature |

The outer terminal CAS binds the exact signer outcome read-back. The final
result artifact derives only after outer authoritative read-back. A valid
result requires exact equality of scheme/key/signature/message across
CapacityV2, intent, signer outcome, outer terminal CAS/read-back, ResultV2,
and HumanDecisionV2.

### One-invocation proof

~~~text
one signer operation slot per authentication_operation_identity
+ predecessor state AVAILABLE
+ one atomic acceptance CAS winner
+ invocation_sequence = 1
+ maximum_logical_signer_invocations = 1
+ identical delivery returns same receipt
+ different delivery conflicts
+ accepted receipt permits only signer-owned continuation/read-back
+ all outcome states terminal
= MAX_SIGNER_INVOCATIONS_PER_OPERATION = 1
~~~

Process memory, conversation state, Human retry, client timeout, and hidden
authenticator memory supply no edge. The persisted signer registry is the
authoritative predecessor and outcome source.

## Crash and Retry Matrix

| Boundary | Persisted authoritative predecessor | Signer invocation status | Possible transient state | Allowed machine recovery | Forbidden action | Authoritative read-back source | Deterministic result |
|---|---|---|---|---|---|---|---|
| before outer claim | exact P_auth/operation; auth slot OPEN | not begun | none | submit exact outer claim | signer/Human action | external auth slot | OPEN or same claim |
| outer claim response lost | claim CAS may be committed | not begun | response absent | read auth slot | second claim/message/key | external auth slot | OPEN or AUTHENTICATING exact operation |
| after claim before signer acceptance | AUTHENTICATING claim read-back; signer slot AVAILABLE | not begun | intent derived | submit exact acceptance intent | direct signer call/Human retry | signer operation slot | AVAILABLE or accepted same intent |
| signer acceptance CAS response lost | exact intent; acceptance may be committed | not begun or accepted once | response absent | read signer slot | different/second intent | signer operation slot | AVAILABLE or exact accepted receipt |
| signer invocation accepted | acceptance CAS/receipt | durably in progress | signer not yet executing | read only; signer continues | client signer call | signer receipt/outcome store | ACCEPTED_IN_PROGRESS |
| signer executing | accepted receipt | durably in progress | computation only | signer resumes same accepted invocation | new invocation/key/message | signer outcome store | in progress or one terminal outcome |
| signer completed successfully before outcome commit | accepted receipt | same one invocation | deterministic signature transient and unusable | signer recomputes/commits same outcome | expose transient signature/client retry | signer outcome store | VALID_SIGNATURE_FINAL only after commit |
| signer completed unsuccessfully before outcome commit | accepted receipt | same one invocation | failure transient | signer commits exact failure outcome | client indeterminate inference | signer outcome store | REJECTED_FINAL or exact INDETERMINATE_FINAL |
| outcome persisted, response lost | terminal signer outcome | completed once | response absent | authoritative read-back | signer/client retry | signer outcome store | identical terminal signer result |
| before outer terminal CAS | signer outcome read-back | completed once | outer result absent | derive exact outer terminal candidate | signer/Human retry | signer outcome read-back | one exact outer terminal candidate |
| outer terminal CAS response lost | terminal CAS may be committed | completed once | response absent | read outer slot | second CAS with different result | external auth slot | AUTHENTICATING or exact terminal |
| outer terminal read-back before ResultV2 | terminal outer read-back | completed once | result artifact absent | derive identical ResultV2 | signer/Human retry | outer terminal store | identical result identity |
| restart with signer slot AVAILABLE | claim plus AVAILABLE read-back | not begun | none | submit same acceptance intent | different/second operation | signer operation slot | accepted once or safe no-progress |
| restart with ACCEPTED_IN_PROGRESS | accepted receipt | durably in progress | signer may be recovering | read only; signer resumes | caller invocation/Human action | signer operation/outcome store | in progress or one terminal outcome |
| restart with terminal signer outcome | outcome read-back | completed once | outer result may be absent | finish outer terminal/read-back/result | signer retry | signer and outer stores | identical result/exhaustion |
| permanent exhaustion | REJECTED/INDETERMINATE outer read-back | completed at most once | none | read only | reset/reissue/review/signature | outer result/exhaustion store | permanent no-decision exhaustion |

Every row is decided by persisted external evidence. A temporarily
unavailable store produces no new action; it does not authorize inference,
timeout terminalization, signing, or Human retry.

## Preserved HumanDecision and P012 Closure

`ExternalConstituentHumanFirstAdoptionDecisionV2` retains the exact G77-71
31-field semantic schema, identity/idempotency prefixes, and
`HUMAN_AUTHORITY` producing ownership/custody. Under the Revision 3 contract
token it requires:

~~~text
capacity pair -> exact validated CapacityV2
authentication result pair -> exact AUTHENTICATED_FINAL ResultV2
scheme/key/signature -> exact ResultV2 and CapacityV2 values
message -> exact UTF8(CJ1(P_auth_v2))
~~~

No field is added, removed, or reinterpreted off-payload. The signature and
result remain outside `P_auth_v2`; result precedes HumanDecision; and no
HumanDecision pair feeds operation, signer, or result identity.

The HFD-04 `P_auth_v2` field set and direct message representation remain
unchanged. The resolved capacity reference pair is now CapacityV2, so the
commitment bytes bind the corrected capacity without adding a second message.

ProofSetV3 uses:

~~~text
contract_version =
  CANDIDATE_H_AUTHENTICATION_REDESIGN_REVISION_3_V1
rank = 12
predicate_code = P012_HUMAN_DECISION_VALID
subject_artifact_type = ExternalConstituentHumanFirstAdoptionDecisionV2
subject_artifact_version = V2
validation_semantics = P012_HUMAN_DECISION_VALID_V2_REVISION_3
~~~

P012 adds exact validation of CapacityV2 issuance authentication/read-back
and ResultV2 signer acceptance/outcome/read-back. Every other G77-71 P012
condition is retained. Unknown/mismatched contract tokens, CapacityV1,
ResultV1, hidden signer outcome, or unauthenticated capacity yield FALSE.

ProofSetV3 contract version remains identity-bearing. CertificationV3 and
TransitionV3 carry the same token and exact resolved pairs. Their artifact
schemas and versions do not change.

## Transitive Consumer Closure and Minimality

The independently reconstructed current graph remains thirty groups:

| # | Current family or consumer group | Classification | Revision 3 reason |
|---:|---|---|---|
| 1 | External Premise | `UNCHANGED_REUSE` | exact accepted source/key/custody predecessor |
| 2 | SourceCommitmentV1 | `UNCHANGED_REUSE` | Target pair only |
| 3 | InstrumentCommitmentV3 | `UNCHANGED_REUSE` | no HumanDecision/P012 field |
| 4 | UniverseV1 / CandidateCensusV1 | `UNCHANGED_REUSE` | ordered pair closure only |
| 5 | SourceEvidenceV1 / RecognitionProofV1 | `UNCHANGED_REUSE` | supplies exact persisted external evidence |
| 6 | NormativePayloadV1 / TargetV5 | `UNCHANGED_REUSE` | predecessor of HumanDecision |
| 7 | InstrumentV4 | `UNCHANGED_REUSE` | predecessor of HumanDecision |
| 8 | HumanDecisionV1 | `VERSION_SUCCESSOR_REQUIRED` | retained redesign successor is HumanDecisionV2 |
| 9 | HumanFinalityV1 | `UNCHANGED_REUSE` | decision pair version-opaque |
| 10 | DispositionEvidence V2/V3 | `UNCHANGED_REUSE` | exact decision/finality pair and status equality |
| 11 | external status/current version/snapshot | `UNCHANGED_REUSE` | explicit resolved type/version rows |
| 12 | ProofSetV3 | `UNCHANGED_REUSE` | identity-bearing Revision 3 contract dispatch |
| 13 | CertificationV3 | `UNCHANGED_REUSE` | same schema/version and exact ProofSet pair/token |
| 14 | FoundingTransitionV3 | `UNCHANGED_REUSE` | same schema/version and exact Certification/ProofSet pairs |
| 15 | FenceV1 / BEGIN CAS | `UNCHANGED_REUSE` | pair-opaque; Transition remains V3 |
| 16 | OperationSeed/token/AllocationIntentV2 | `UNCHANGED_REUSE` | generic immutable pair inputs |
| 17 | ALLOCATED CoordinatorStateV2 | `UNCHANGED_REUSE` | allocation row unchanged |
| 18 | allocation CAS/marker/read-back/Receipt | `UNCHANGED_REUSE` | generic root-pair serialization |
| 19 | LogicalPointer/Projection/Manifest/route Censuses | `UNCHANGED_REUSE` | no authentication interpretation |
| 20 | ordinary-chain CensusV2 | `UNCHANGED_REUSE` | TargetV5/route closure unchanged |
| 21 | CAP Reachability StateV2 | `UNCHANGED_REUSE` | Census/Target closure unchanged |
| 22 | Dormancy Rebase GuardV2 | `UNCHANGED_REUSE` | Transition artifact version remains V3 |
| 23 | MetaRepairTransitionV3 | `UNCHANGED_REUSE` | Guard remains V2 |
| 24 | MetaRepairStateV3 | `UNCHANGED_REUSE` | Guard/Meta/Transition versions unchanged |
| 25 | failure Census/FailureEvidenceV2 | `UNCHANGED_REUSE` | pair-opaque failure reduction |
| 26 | terminal CommitmentV3 | `UNCHANGED_REUSE` | downstream fixed versions unchanged |
| 27 | consuming operation/ConsumeIntentV2 | `UNCHANGED_REUSE` | commitment pair opaque |
| 28 | terminal CoordinatorV4 / RootSnapshotV4 | `UNCHANGED_REUSE` | fixed terminal versions unchanged |
| 29 | terminal CAS/read-back/AttemptTerminalReadBack/Disposition/Receipt/Dormancy | `UNCHANGED_REUSE` | pair comparison only |
| 30 | Replay / CRO | `UNCHANGED_REUSE` | explicit contract dispatch; read-only/passive |

Blocker-targeted family disposition:

| Family | Classification | Exact result |
|---|---|---|
| HumanFounderExternalCapacityEvidenceV1 | `VERSION_SUCCESSOR_REQUIRED` | V2 adds authenticated core issuance and source custody read-back |
| HumanFounderAuthenticationResultReadBackEvidenceV1 | `VERSION_SUCCESSOR_REQUIRED` | V2 adds exact signer acceptance/outcome persistence |
| ExternalConstituentHumanFirstAdoptionDecisionV2 | `UNCHANGED_REUSE` | same 31 fields/version; Revision 3 contract token resolves V2 predecessors |
| separate invocation receipt family | `REMOVE` | exact receipt is a closed signer-registry subcontract inside ResultV2 responsibility |
| separate signer State family | `REMOVE` | operation-slot CAS/read-back is sufficient and already externally owned |
| separate capacity verification family | `REMOVE` | complete issuance profile is nested in CapacityV2 |
| new owner/authority/root family | `REMOVE` | forbidden and unnecessary |

Exact counts and deltas:

~~~text
current consumer groups = 30
unchanged current consumer groups = 29
pre-redesign existing family successors = 1  # HumanDecisionV2
blocker-targeted failed-proposal family successors = 2  # CapacityV2, ResultV2
total successor contracts in the complete Revision 3 redesign = 3
genuinely new family responsibilities relative to pre-redesign Candidate H = 2
new top-level artifact families introduced by G77-73 beyond G77-71 = 0
new State families = 0
new verification families = 0
new owners = 0
new authorities = 0
new root fields = 0
new root serialization domains = 0
new production paths = 0
new parallel paths = 0
new persistent founding paths = 0
~~~

The atomic signer subcontracts are necessary: removing acceptance CAS,
receipt, durable outcome, or read-back recreates G77-72 B01. They are
sufficient because every restart state is authoritative and at most one
acceptance wins. Capacity core signature and source custody read-back are
necessary: removing either leaves an unsigned assertion or non-durable source
issuance. They are sufficient because exact core bytes, accepted owner/key,
signature, custody, and failure rules are closed. Separate top-level families
would duplicate identity, owner, lifecycle, and Replay machinery without
adding a missing responsibility.

Machinery verdict: `NECESSARY_AND_SUFFICIENT_PROPOSAL_ONLY`.

## Identity DAG

~~~text
accepted external Premise + its authentication/custody evidence
-> exact 32-field capacity core P_capacity_issue_v2
-> Premise-owner capacity signature
-> source issuance CAS/read-back
-> CapacityV2
-> HFD manifest/act/review
-> exact P_auth_v2
-> pre-sign authentication operation
-> outer OPEN-to-AUTHENTICATING claim/read-back
-> signer invocation intent
-> signer AVAILABLE-to-ACCEPTED acceptance CAS/receipt
-> signer-owned deterministic continuation
-> durable signer outcome/read-back
-> outer terminal CAS/read-back
-> ResultV2
-> HumanDecisionV2
-> HumanFinality/Disposition
-> ProofSetV3(Revision 3 token)
-> CertificationV3 -> TransitionV3
-> retained Fence/BEGIN or retry path
-> retained CAP/Guard/Meta/Commitment/Coordinator/root chain
-> terminal evidence/exhaustion
-> read-only Replay -> passive CRO
~~~

Cycle exclusions:

- capacity issuance bytes exclude signature, post-sign read-back, and final
  CapacityV2 identity;
- acceptance intent excludes signer outcome and every later artifact;
- signer outcome binds only finalized intent/acceptance/receipt predecessors;
- outer terminal binds finalized signer outcome read-back, not ResultV2;
- ResultV2 precedes HumanDecisionV2;
- signature and HumanDecision remain outside `P_auth_v2`;
- no Finality, ProofSet, Certification, Transition, root, Replay, or CRO pair
  feeds backward; and
- source logical instants are persisted predecessor tokens, never live time.

| Required property | Proposal verdict |
|---|---|
| `FINITE` | `PASS_PROPOSAL` |
| `ACYCLIC` | `PASS_PROPOSAL` |
| `FORWARD_DERIVED` | `PASS_PROPOSAL` |
| `BYTE_DETERMINISTIC` | `PASS_PROPOSAL` |
| `DOMAIN_SEPARATED` | `PASS_PROPOSAL` |
| `REPLAY_RECONSTRUCTIBLE` | `PASS_PROPOSAL` |

No identity depends on itself, its own digest/signature, a successor, process
memory, conversation, repository order, live clock, or hidden authenticator
memory.

## Authority DAG

~~~text
genuinely external constituent authority
-> accepted external Premise fact
-> authenticated Premise owner/key/custody
-> authenticated issuance of exact CapacityV2 core
-> exact external actor/capacity/competence/act-key/status claims
-> Human Founder choice/review
-> one accepted signer operation

HUMAN_AUTHORITY
-> HumanDecisionV2 and HumanFinality custody only

external signer/result custodian
-> acceptance/outcome persistence only

Certification -> deterministic predicates only
Governance -> already granted deterministic mechanics only
root custodian -> existing-domain mechanical serialization only
HIC/CHE -> transport only
Replay -> read-only
CRO -> passive
~~~

The accepted Premise supplies normative authority; G77-73 does not prove or
create that external fact. The Premise owner's valid capacity signature proves
only that the already accepted owner issued the exact capacity core. The
capacity signature, act signature, key possession, result, P012 TRUE,
Certification, Governance, repository ownership, root success, Replay, and
CRO cannot originate constituent authority.

No edge flows from `HUMAN_AUTHORITY` custody into actor, competence, capacity,
key, or external ownership. No signer/result custodian may select disposition,
authority, Finality, P012 semantics, or root effect.

Authority DAG verdict: `PASS_PROPOSAL`.

## Replay and One-Shot Closure

Starting only from persisted evidence, Replay:

1. validates the accepted Premise, owner, key, custody, provenance, and scope;
2. reconstructs exact `P_capacity_issue_v2` bytes and commitment pair;
3. verifies the Premise-owner capacity signature and source issuance
   CAS/read-back;
4. validates CapacityV2's core nested actor/capacity/competence/scope/act-key/
   profile/status records;
5. reconstructs HFD act, review, and exact `P_auth_v2` message bytes;
6. recomputes operation, outer claim, signer intent, acceptance CAS, and
   invocation receipt;
7. reads exact signer in-progress or terminal outcome state without invoking
   the signer;
8. verifies terminal outcome/read-back, outer terminal/read-back, and ResultV2;
9. validates HumanDecisionV2, HumanFinality, Disposition, Revision 3 P012,
   ProofSetV3, CertificationV3, and TransitionV3;
10. reconstructs the retained BEGIN/retry, root, terminal evidence, and
    exhaustion chain; and
11. returns the same evidence without writing.

If the signer slot is `AVAILABLE`, Replay reports not invoked. If it is
`ACCEPTED_IN_PROGRESS`, Replay reports one accepted operation in progress. If
terminal, Replay returns the exact durable outcome. It never consults process
memory, signer cache, Human memory, conversation, wall clock, repository
order, or hidden dispatch.

| Ceiling | Exact proof |
|---|---|
| Human dispositions <= 1 | retained act/capacity/finality sequence |
| Human reviews <= 1 | exact one ReviewProjectionV2 pair |
| authentication operation identities <= 1 | one outer slot/epoch/sequence and operation pair |
| signer invocations <= 1 | one signer slot and one acceptance CAS winner |
| durable valid authentication results <= 1 | one terminal signer outcome and outer CAS |
| HumanDecisionV2 <= 1 | one valid ResultV2 plus retained decision slot |
| finality events <= 1 | retained one-use finality CAS/read-back |
| successful founding effects <= 1 | retained Fence/BEGIN and root CAS |

REFUSE finality permanently exhausts without a founding effect.
`INDETERMINATE_EXHAUSTED` permanently exhausts without HumanDecision or
effect. Successful ADOPT/founding effect terminates in retained Dormancy,
Receipt, and exhaustion. None permits revival, reset, reissue, recurrence,
second key/message/review/signature/finality/effect, target substitution, or
post-founding special authority. Ordinary G70 remains the only later
amendment lifecycle.

Crash/retry verdict: `PASS_PROPOSAL`.

Replay verdict: `PASS_PROPOSAL`.

One-shot verdict: `PASS_PROPOSAL`.

## Topology and Reuse Impact Assessment

Topology remains:

| Measure | Before | Revision 3 | Delta |
|---|---:|---:|---:|
| production paths | 1 | 1 | 0 |
| parallel paths | 0 | 0 | 0 |
| persistent founding paths | 0 | 0 | 0 |
| Human entry points | 1 | 1 | 0 |
| HIC families | 1 | 1 | 0 |
| CHE definitions | 1 | 1 | 0 |
| root paths | 1 | 1 | 0 |
| internal owners | retained | retained | 0 |
| current roots | 1 | 1 | 0 |
| root serialization domains | retained | retained | 0 |
| persistent founding authorities | 0 | 0 | 0 |

The capacity issuance slot and signer registry are external evidence custody
inside the existing Candidate H authentication spine. They do not authorize
BEGIN, serialize a root, create a Human entry, or persist reusable Founder
authority.

1. **Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?**

   Ponovno se uporabijo CJ1 in SHA-256, G76 identitetni/DAG model, G69-07
   meja skrbništva `HUMAN_AUTHORITY`, sprejeti zunanji Premise in njegova
   dokazila, HFD-04 akt, pregled in isti `P_auth_v2`, G77-44 zunanji
   CAS/read-back vzorec, HumanDecisionV2, HumanFinality, Disposition,
   ProofSetV3, CertificationV3, TransitionV3, Fence/BEGIN, CAP/Guard/
   MetaRepair, korenska pot, HIC/CHE ter pasivni Replay/CRO. Nespremenjeno se
   ponovno uporabi 29 trenutnih potrošniških skupin.

2. **Katere nove zmogljivosti (če sploh) nastanejo?**

   G77-73 ne dodaja nove vrhnje družine. Dve že predlagani novi odgovornosti
   dobita popravljeni V2 pogodbi: podpisano in trajno prebrano capacity
   issuance ter atomarni signer acceptance/outcome/read-back. Ne nastane nova
   State ali verification družina, lastnik, avtoriteta ali korenska domena.

3. **Ali katera obstoječa zmogljivost postane nedosegljiva?**

   Ne. CapacityV1 in ResultV1 ostaneta nespremenjena neuspešna zgodovina ter
   sta za Revision 3 neupravičena. HumanDecisionV2 in celoten nadaljnji tok
   ostaneta dosegljiva samo z veljavnima V2 predhodnikoma. Kandidat H ostaja
   neaktiviran.

4. **Ali implementacija ustvarja vzporedni tok?**

   Ne. Implementacije ni. Zunanja izdaja capacity in signer registry sta
   dokazni podpogodbi na istem toku, ne nov Human, HIC/CHE ali korenski tok.

5. **Ali zmanjšuje ali povečuje število produkcijskih poti?**

   Ne. Ostane ena produkcijska pot, nič vzporednih poti in nič trajnih
   ustanovitvenih poti.

# 2. Code Evidence

## Public API

No public API is implemented. The proposed public constitutional surface is
limited to `HumanFounderExternalCapacityEvidenceV2`,
`HumanFounderAuthenticationResultReadBackEvidenceV2`, retained
HumanDecisionV2, and the Revision 3 P012 contract token.

## Orchestration Entry Point

No runtime entry point is created. The exact proposed order is:

~~~text
accepted Premise -> signed/read-back CapacityV2 -> act/review/P_auth_v2
-> outer claim -> signer intent -> acceptance CAS/receipt
-> signer-owned outcome/read-back -> outer terminal/read-back/ResultV2
-> HumanDecisionV2 -> retained Candidate H spine
~~~

## Semantic Reductions

B01 closure:

~~~text
one content-derived signer intent
+ one signer-owned AVAILABLE slot
+ one atomic acceptance CAS winner
+ write-before-response terminal outcome
+ authoritative outcome read-back
-> one logical signer invocation and no hidden-memory recovery
~~~

B02 closure:

~~~text
accepted Premise owner/key
+ signature over exact 32-field CapacityV2 core bytes
+ source-owned issuance CAS/read-back
-> authenticated issuance, not authority creation
~~~

## Public Validators

No validator is implemented. A future validator must reject CapacityV1,
ResultV1, a non-Premise issuer/key, invalid capacity signature, missing source
read-back, missing signer acceptance receipt, non-durable outcome, caller
retry after acceptance, hidden-memory result, wrong contract token, and every
unknown/ambiguous field.

## Canonical Data Models

Exact Revision 3 model counts:

~~~text
CapacityV2 semantic fields = 34
CapacityV2 core fields = 32
CapacityV2 new nested issuance records = 2
ResultV2 semantic fields = 50
HumanDecisionV2 semantic fields = 31 unchanged
current consumer groups = 30
unchanged current consumer groups = 29
new top-level families beyond G77-71 = 0
new State families = 0
new verification families = 0
~~~

## Deterministic Algorithms

1. Validate accepted Premise and derive exact capacity core bytes.
2. Verify the exact Premise-owner Ed25519 capacity signature and custody
   read-back.
3. Derive one `P_auth_v2` and outer operation/claim.
4. Derive one signer intent and CAS it into one AVAILABLE signer slot.
5. After accepted receipt, permit only signer-owned continuation.
6. Persist signer outcome atomically before response or signature exposure.
7. Read the outcome and derive one outer terminal/result.
8. Continue only valid ResultV2 into HumanDecisionV2 and Revision 3 P012.
9. Replay reads every same persisted predecessor without mutation.

## Responsibility Boundaries

| Responsibility | Exact owner/source | Prohibited authority |
|---|---|---|
| external constituent premise | genuinely prior external authority | not machine-derived |
| capacity issuance | authenticated accepted Premise owner | source authentication only |
| Human choice/review | Human Founder | no signer/custodian choice |
| Human act signing | bound external signer key | no authority from key possession |
| signer acceptance/outcome persistence | external signer/result custodian | no Human/P012/root authority |
| HumanDecision/Finality custody | `HUMAN_AUTHORITY` | custody only |
| P012/Certification | deterministic verifier | no choice/authority creation |
| Governance/root | retained mechanics/custodian | no external/Human authority |
| Replay/CRO | read-only/passive | no repair/control |

## Repository Evidence

Evidence is the authenticated committed G48/G69/G70/G76/G77/HFD lineage,
G77-72's two exact blockers, G77-71's surviving contracts, independently
reconstructed schemas/graphs, focused G69/G70 tests, and repository mutation
checks. No runtime, key, signature, external evidence instance, Human act,
BEGIN, root effect, activation, or deployment supplies evidence.

# 3. Constitutional Self-Assessment

## Verified at Proposal Level

- G77-72 is committed and all controlling hashes match repository bytes.
- Both and only G77-72 blockers receive exact successor contracts.
- CapacityV2 authenticates every authority-bearing core byte with the
  already accepted Premise owner/key and durable source custody read-back.
- Capacity authentication proves source issuance but does not create external
  authority from signature or key possession.
- ResultV2 persists one signer acceptance before computation and one
  write-before-response outcome/read-back.
- Identical acceptance delivery is idempotent; different delivery conflicts.
- A signer crash resumes one accepted logical invocation and never permits a
  caller retry.
- Every successful signature has a defined durable recovery path.
- CapacityV2, ResultV2, and retained HumanDecisionV2 have exact 34, 50, and 31
  semantic fields.
- HFD-04 `P_auth_v2` remains the sole Human authentication message.
- HumanDecisionV2 remains acyclic and `HUMAN_AUTHORITY` remains custody-only.
- Revision 3 P012 dispatch is persisted and identity-bearing in ProofSetV3.
- Thirty current consumer groups remain: 29 unchanged and one pre-redesign
  successor; two failed-proposal family contracts advance to V2.
- No third new family, State family, verification family, owner, authority,
  root field/domain, production path, parallel path, or persistent founding
  path is required.
- Identity and authority DAGs are finite, acyclic, forward, deterministic,
  separated, and Replay-reconstructible at proposal level.
- Crash/retry, Replay, one-shot ceilings, permanent exhaustion, and topology
  are closed at proposal level.
- All actual effect classifications remain `NO`.

## Not Verified or Performed

- No independent constitutional assessment of G77-73 has occurred.
- No actual Premise, issuer key, capacity core, source signature, custody
  read-back, signer slot, acceptance, invocation, outcome, result,
  HumanDecision, Finality, ProofSet, Transition, root, or exhaustion instance
  exists.
- No runtime schema, signer registry, Ed25519 operation, validator, CAS store,
  serializer, P012 implementation, retry controller, or Replay reader exists.
- No physical signer/hardware crash behavior, durable storage guarantee,
  cryptographic custody, security, privacy, or operational liveness is tested.
- No Candidate H/G76-specific executable test module exists.
- No Human Ratification, implementation authorization, publication,
  activation, deployment, or production authority exists.
- Known hook drift and partial conformance remain visible and unchanged.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| repository HEAD/tree/clean start | exact Git objects/status | Git inspection | `PASS` |
| G77-72 committed immutability | tracked HEAD path | Git inspection | `PASS` |
| predecessor hashes | authenticated tables | SHA-256 | `PASS` |
| B01 exact source | G77-72 first blocker | predecessor review | `PASS` |
| B02 exact source | G77-72 second blocker | predecessor review | `PASS` |
| capacity core preservation | exact 32 retained fields | independent schema count | `PASS` |
| CapacityV2 schema | 34 exact fields/two complete records | schema review | `PASS` |
| exact capacity bytes | P_capacity_issue_v2 excludes only post-sign/self fields | byte-contract review | `PASS` |
| Premise owner/key binding | exact equality/trust digest | authority review | `PASS` |
| capacity signature | fixed Ed25519 direct-message profile | algorithm review | `PASS` |
| capacity custody | source CAS/read-back | persistence review | `PASS` |
| no authority from signature | accepted Premise precedes signature | authority DAG review | `PASS` |
| ResultV2 schema | 50 exact fields | schema count | `PASS` |
| signer not begun visibility | AVAILABLE authoritative slot | crash review | `PASS` |
| signer in-progress visibility | accepted receipt/status | crash review | `PASS` |
| signer outcome durability | atomic write-before-response outcome/read-back | crash review | `PASS` |
| successful transient recovery | deterministic same-invocation continuation | hostile crash review | `PASS` |
| maximum signer invocations | one slot/acceptance CAS winner | one-shot proof | `PASS` |
| no hidden authenticator memory | signer registry is persisted predecessor | Replay review | `PASS` |
| outer terminal closure | exact outcome read-back drives terminal CAS | state review | `PASS` |
| HumanDecisionV2 | unchanged 31 fields and forward result dependency | schema/DAG review | `PASS` |
| one authenticated message | exact UTF8 CJ1 P_auth_v2 | byte review | `PASS` |
| P012 version visibility | Revision 3 ProofSet contract token | Replay review | `PASS` |
| ProofSet/Certification/Transition reuse | same schemas/versions, identity token | transitive review | `PASS` |
| current consumer graph | thirty classified rows | independent count | `PASS` |
| current reuse/successor count | 29 reuse / 1 pre-redesign successor | count review | `PASS` |
| blocker-family successors | CapacityV2 and ResultV2 | schema immutability review | `PASS` |
| new top-level families | zero beyond two existing responsibilities | minimality review | `PASS` |
| new State/verification families | zero | minimality review | `PASS` |
| machinery necessity/sufficiency | removal and completeness attacks | hostile review | `PASS` |
| identity DAG six properties | exact forward graph/exclusions | DAG review | `PASS` |
| authority DAG | source issuance without authority creation | authority review | `PASS` |
| crash matrix | sixteen explicit boundaries | retry review | `PASS` |
| Replay persisted evidence only | complete reconstruction list | Replay attack | `PASS` |
| eight one-shot ceilings | exact CAS/finality/root proofs | lifecycle review | `PASS` |
| permanent non-revivability | REFUSE/indeterminate/success terminal rows | lifecycle review | `PASS` |
| topology | exact before/after matrix | graph review | `PASS` |
| Reuse Impact Assessment | five explicit Slovenian answers | completeness review | `PASS` |
| focused G69/G70 tests | 326 existing tests | pytest | `PASS` |
| Candidate H/G76 tests | no directly named module present | test inventory | `NOT_APPLICABLE` |
| six G48 top-level sections | exact names/order/count | structure validation | `PASS` |
| eight Code Evidence subsections | exact names/count | structure validation | `PASS` |
| Markdown fence balance | paired fence count | format validation | `PASS` |
| zero trailing whitespace | line scan | format validation | `PASS` |
| tracked/untracked whitespace | Git/no-index checks | diff validation | `PASS` |
| exact G77-73 mutation | one new governance file | mutation inventory | `PASS` |
| predecessor/runtime/test/config/root/production mutation | no changed prohibited path | mutation inventory | `PASS` |
| implementation/activation/act/signature/BEGIN/root/deployment/commit | proposal-only boundary | scope review | `NOT_APPLICABLE` |

# 5. Repository Mutation Summary

Modified files:

- added
  `docs/governance/G77_73_CANDIDATE_H_AUTHENTICATION_REDESIGN_REVISION_3_SIGNER_OUTCOME_DURABILITY_AND_EXTERNAL_CAPACITY_SOURCE_AUTHENTICATION_CLOSURE_V1.md`
  as the sole G77-73 design proposal.

Unchanged subsystems:

- G77-72, G77-71, and every G48/G69/G70/G76/G77/HFD predecessor;
- HumanDecisionV2 field schema, HFD-04 P_auth_v2, HumanFinality,
  Disposition, ProofSetV3, CertificationV3, TransitionV3, Fence/BEGIN,
  CAP/Guard/MetaRepair, root contracts, HIC/CHE, Replay, and CRO;
- Constitution, active CAP/CDP/CLIA state, Human Authority runtime,
  Governance runtime, Certification runtime, root persistence, release,
  deployment, production, tests, config, providers, and credentials.

API compatibility:

- no API, runtime model, validator, serializer, signer, store, route, command,
  workflow, owner, root schema, deployment, or production contract is
  implemented or activated;
- G77-71 failed V1 evidence contracts remain immutable history; and
- all surviving downstream artifact versions remain unchanged and select
  Revision 3 semantics only through persisted contract-version bytes.

Boundary preservation:

- proposal only and independently unassessed;
- no external evidence instance, capacity issuance, signer invocation,
  signature, Human act, disposition, HumanDecision, Finality, P012 result,
  BEGIN, root mutation, exhaustion, activation, authority grant, deployment,
  or production effect occurs;
- Replay remains read-only, CRO passive, HIC/CHE transport-only, and
  `HUMAN_AUTHORITY` custody-only; and
- topology remains one production path, zero parallel paths, and zero
  persistent founding paths.

Unrelated pre-existing changes:

- None observed. The worktree was clean at proposal start.

Worktree mutation count attributable to this task: `1` new governance file,
`0` modified existing files.

No commit is created.

# 6. Certification Verdict

G77_CANDIDATE_H_AUTHENTICATION_REDESIGN_REVISION_3_FULL_CLOSURE_ESTABLISHED
