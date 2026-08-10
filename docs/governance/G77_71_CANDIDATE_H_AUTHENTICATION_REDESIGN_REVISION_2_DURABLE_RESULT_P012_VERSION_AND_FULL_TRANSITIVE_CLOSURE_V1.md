# 1. Implementation Summary

Generation: G77-71

Report and proposal identity:
`G77_71_CANDIDATE_H_AUTHENTICATION_REDESIGN_REVISION_2_DURABLE_RESULT_P012_VERSION_AND_FULL_TRANSITIVE_CLOSURE_V1`

Proposal revision: `2`

Proposal status: `PROPOSAL_ONLY_UNASSESSED`

Artifact class:
`CANDIDATE_H_CONSTITUTIONAL_DESIGN_PROPOSAL_NON_IMPLEMENTING_NON_ACTIVATING`

Constitutional baseline: authenticated committed G0 through G77-70. G77-69
is the immutable Revision 1 redesign assessment, and G77-70 is its controlling
independent assessment. G77-70 requires rework. Every predecessor remains
closed and unchanged.

Controlling verdict: `G77_69_CONSTITUTIONAL_IMPACT_REQUIRES_REWORK`

Controlling first blocker:
`G77_69_B01_AUTHENTICATION_RESULT_DURABLE_READ_BACK_CONTRACT_ABSENT`

Additional controlling blockers:

- `G77_69_B02_P012_V2_CONTRACT_NOT_BOUND_IN_PROOFSET_OR_REPLAY`;
- `G77_69_B03_CAPACITY_AND_VERIFICATION_PREDECESSOR_CONTRACTS_UNDERCLOSED`;
  and
- `G77_69_B04_TRANSITIVE_SUCCESSOR_SET_UNDERSTATED`.

Reporting date: 2026-08-10.

Objective:

Define the minimum proposal-only Candidate H successor that closes all four
G77-70 findings while retaining one Human disposition, one exact review, one
authenticated message, one external authentication operation, one-shot
finality/exhaustion, one HIC/CHE path, one Candidate H execution spine, one
root path, read-only Replay, passive CRO, and topology `1 / 0 / 0`.

This proposal does not implement, activate, instantiate, Ratify, sign, create
a Human act, create BEGIN, mutate a root, grant implementation or production
authority, deploy, or commit.

Authenticated repository identity at proposal start:

- Commit: `00973284b11af4dd458e0c5381459eb63b26dd50`
- Tree: `54b6d8a407cb807042f2e99209a5c1dfb333cac6`
- Branch: `master`
- Subject: `G77-70: identify Candidate H authentication redesign blockers`
- G77-70 status: committed at HEAD
- Proposal-start worktree state: clean

Authenticated redesign lineage:

| Artifact | SHA-256 | Role |
|---|---|---|
| G77-69 | `329f952e7514e6e932579d1df12823f4bad8eb948806fa096897c270dab1103f` | assessed Revision 1 redesign model |
| G77-70 | `5c6fe6138391fbb58a3bb20e047585a664d94f0a07e0be7ed3368a444f67563c` | controlling independent assessment |

Authenticated control hashes:

| Artifact | SHA-256 | Role |
|---|---|---|
| G48-00 | `16508d1a77c4b3f07d37861e74d85f77896be16da01ca26cbc07a658ddf2c0eb` | reporting standard |
| G69-07 | `ac8665d902abef943b12ee4198e99884930f888eb7d1d3387e686943ea80bd61` | Human Authority custody/transport boundary |
| G70-03 | `7006a1c03e654542ac7d77fd18fdee996c36e0e20de7425c94c8f3ac6c2bc00d` | assessment discipline |
| G76-06 | `29f06a93d5b7ce610c161487bc1e3a01f6d7d063b22393e0347b0da20b281dbc` | identity and DAG rules |
| G77-42 | `b379cb057282aaf7d10c6e6e3f8a55053a630b19a0a0ad80e8159a0222b316a6` | HumanDecisionV1/P012 origin |
| G77-44 | `03026b9ff5df38e05ffe08e0d834d0ac83d1b04efc3681f6ea2aff4165801c0a` | external-domain CAS/status/read-back precedent |
| G77-52 | `a55fe696c011d5edb6450f6b800925f8c5f33a1e9345a85adc20a0d0f358b18a` | Candidate H model |
| G77-53 | `3ca5bcd6a91005c5ef34b7ef4b6fd4cb01bc9b2ea2c76db8b35b187938706658` | model assessment |
| G77-62 | `661394be4e32b2e965f6a906e865a78128572084bbe52c5d0aad3bfdd5deca1e` | full transitive instantiation contract |
| G77-63 | `73190f6a7f919469b7d67f512cf955e9c5531b9f41170229061760f03c2ad7fe` | Revision 3 assessment |
| G77-64 | `ac3deaf40e7f06c04e3396b161194b258b7ae993b65d9ee719fb1170fc4ac0c6` | Certification-time closure |
| G77-65 | `9d5c40e861aa11d2f6ee173016f50dde57d4026fd85cf124b9c887b8e1449569` | design convergence |
| G77-66 | `9f33fade3019d5a3ddf4e1e286fccc011e812274af71076b4ddd0f96f601859d` | lifecycle boundary |
| G77-67 | `236c613844532fb44ba9aa473df46fccea75fc603271373b6d7bf0fd692eff2b` | adoption preparation |
| G77-68 | `4331fcbc3849f71b2f6c07a6f60c39af6c24697bccdf3ef0f5bf8d1411abe027` | external handoff boundary |

Authenticated HFD lineage:

| Artifact | SHA-256 | Role |
|---|---|---|
| HFD-01 | `f23c25a36a638961ffca25861576858e7a77c7f715c23e01783f66ad6743e982` | Human Founder model |
| HFD-02 | `d6c0f2b4f71c40b91d94e47c5d1b38ccd77518b33598b792aa7c7c7051e084a6` | protocol Revision 1 |
| HFD-03 | `1d8cceb4741bac022c82298db230e6fe8b6dce46eae32bf221de8cf14aa5b5e5` | Revision 1 assessment |
| HFD-04 | `5030cd2d90cbb792fa3ee3ed2777057ad269619b091b344b390e8d6247d85eb5` | protocol Revision 2 and `P_auth_v2` |
| HFD-05 | `e3c49ecd8824b53ff6bce5286e762fda020545745c11e28128d3a56d2ba2d5a0` | Revision 2 assessment |
| HFD-06 | `f9505f3beac9d9e43b2991421c78110eab1f1ff8cf6ca2a97df2ed4d79c8f886` | frozen compatibility stop |

## Closure Result

Revision 2 closes all four G77-70 findings at proposal level:

| Finding | Revision 2 closure | Proposal result |
|---|---|---|
| B01 durable result absent | one new external `HumanFounderAuthenticationResultReadBackEvidenceV1` family, with exact claim/terminal CAS and authoritative read-back | `ADDRESSED_PROPOSAL_ONLY` |
| B02 P012 version invisible | persisted ProofSetV3 `contract_version` token plus exact closed dispatch table | `ADDRESSED_PROPOSAL_ONLY` |
| B03 capacity/verification underclosed | one closed capacity family with complete nested actor/capacity/provenance/competence/scope/key/verification/status records | `ADDRESSED_PROPOSAL_ONLY` |
| B04 successor set understated | exact contract-version analysis proves 29 current groups reuse and only HumanDecision requires an artifact-version successor | `ADDRESSED_PROPOSAL_ONLY` |

The minimum structural result is:

~~~text
existing artifact-family version successors = 1
genuinely new artifact families = 2
current family/consumer groups reused at existing artifact version = 29
new internal owners = 0
new roots = 0
new root serialization domains = 0
new production paths = 0
~~~

The G77-70 conservative ten-successor set is not required because this
proposal completes its explicitly reserved option C: a persisted ProofSet
contract-version dispatch. The contract version participates in the common
identity payload, so old and new semantics cannot have the same bytes.

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

## Preserved G77-69 Results

Revision 2 retains without reopening:

- one Human disposition maximum;
- one exact Human review maximum;
- one authenticated message exactly equal to `UTF8(CJ1(P_auth_v2))`;
- one external authentication operation maximum;
- HumanDecision successor semantics;
- `HUMAN_AUTHORITY` as custody only;
- Human Founder authority as independently prior and external only;
- retained HumanFinality and permanent exhaustion;
- HIC/CHE transport only;
- one Candidate H execution spine and root path;
- read-only Replay and passive CRO; and
- topology `1 / 0 / 0`.

## Common Canonical Rules

The two new families and HumanDecisionV2 use the retained Candidate H common
envelope:

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

The exact Revision 2 contract-version token is:

~~~text
CANDIDATE_H_AUTHENTICATION_REDESIGN_REVISION_2_V1
~~~

CJ1 means UTF-8, Unicode NFC, object keys sorted by Unicode code point,
minimal JSON escaping, no whitespace, exact JSON booleans/null, integers with
no leading or negative zero, no floats/NaN/infinity, declared array order, and
no unknown keys.

For artifact A, `S_A` contains exact type, artifact version, contract version,
producing owner, and every semantic field, excluding only self identity, self
digest, idempotency identity, and metadata. `P_A = S_A + idempotency_identity`.

~~~text
A.idempotency_identity = <idem-prefix>:SHA256(CJ1(S_A))
A.artifact_identity = <identity-prefix>:SHA256(CJ1(P_A))
A.artifact_digest = sha256:SHA256(CJ1(P_A))
~~~

Same semantic bytes return one artifact. Same identity/idempotency with
different bytes, wrong contract version, unknown field, half-pair, invalid
null, or non-CJ1 content fails closed.

## Closed Human Founder Capacity Evidence

The new family is `HumanFounderExternalCapacityEvidenceV1`, artifact version
`V1`, contract version
`CANDIDATE_H_AUTHENTICATION_REDESIGN_REVISION_2_V1`, identity prefix
`human-founder-external-capacity-v1`, and idempotency prefix
`human-founder-external-capacity-idem-v1`.

Its producing owner is exactly:

~~~text
capacity.producing_owner
  == resolved ExternalConstituentPremiseEvidenceV1.external_authority_identity
~~~

That equality records the independently prior external source; it does not
create the source. `HUMAN_AUTHORITY`, Governance, Certification, repository
ownership, and key possession are ineligible producers.

The exact 32-field semantic payload is:

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
~~~

Every nested record is present in full inside the capacity artifact. It is not
an opaque pair or separately addressable artifact family. Each record has
exact `record_type`, `record_version = V1`, `producing_owner`, closed fields,
and `record_digest = sha256:SHA256(CJ1(record payload excluding its digest))`.
Every nested `producing_owner` equals the capacity producing owner.

### Human actor identity record

~~~text
record_type = HUMAN_FOUNDER_ACTOR_IDENTITY_RECORD
record_version = V1
producing_owner
human_actor_identity
human_actor_identity_scheme
subject_kind = HUMAN_NATURAL_PERSON
identity_assurance_profile = EXTERNAL_PREMISE_OWNER_ATTESTED_EXACT_SUBJECT_V1
identity_evidence_payload = {
  issuer_identity,
  subject_identity,
  subject_kind,
  identity_scheme,
  subject_assertion_digest,
  assurance_profile,
  issued_at
}
identity_evidence_payload_digest
issued_at
record_digest
~~~

The nested subject identity equals `human_actor_identity`, the issuer equals
the producing owner, and the payload digest recomputes. No repository, role
name, process, or key identity may populate the actor field.

### External capacity record

~~~text
record_type = HUMAN_FOUNDER_EXTERNAL_CAPACITY_RECORD
record_version = V1
producing_owner
external_capacity_identity
external_capacity_digest
human_actor_identity
external_premise_identity
external_premise_digest
external_constituent_model_identity
target_identity
target_digest
scope_digest
capacity_kind = INDEPENDENT_PRIOR_HUMAN_FOUNDER_ONE_SHOT
capacity_origin = EXTERNAL_FACT_NOT_MACHINE_DERIVED
issued_at
record_digest
~~~

`external_capacity_digest` hashes the displayed capacity content excluding its
own identity/digest. The capacity identity is
`human-founder-capacity-v1:SHA256(CJ1(capacity content excluding its pair))`.
Actor, Premise, Target, model, and scope equal the surrounding artifact.

### Authority provenance record

~~~text
record_type = HUMAN_FOUNDER_AUTHORITY_PROVENANCE_RECORD
record_version = V1
producing_owner
external_premise_identity
external_premise_digest
human_actor_identity
external_capacity_identity
external_capacity_digest
ordered_predecessor_rows
predecessor_count
predecessor_root
anti_self_authorization_result = TRUE
forbidden_dependency_count = 0
record_digest
~~~

Each predecessor row is exactly
`{ordinal, artifact_type, artifact_version, producing_owner,
artifact_identity, artifact_digest}`. Order is ascending ordinal; count/root
recompute. Rows may name only independently prior external evidence and the
authenticated HFD/G77 lineage. Current/target/successor Constitution,
Governance, Certification, Human approval alone, repository, administration,
deployment, and key possession are forbidden authority predecessors.

### Authority competence record

~~~text
record_type = HUMAN_FOUNDER_AUTHORITY_COMPETENCE_RECORD
record_version = V1
producing_owner
human_actor_identity
external_capacity_identity
external_capacity_digest
target_identity
target_digest
scope_digest
competence_kind = FIRST_ADOPTION_OF_EXACT_TARGET_ONLY
competence_result = COMPETENT_FOR_EXACT_TARGET
maximum_successful_effects = 1
ordinary_post_founding_authority = false
record_digest
~~~

### One-shot scope record

~~~text
record_type = HUMAN_FOUNDER_ONE_SHOT_SCOPE_RECORD
record_version = V1
producing_owner
target_identity
target_digest
maximum_dispositions = 1
maximum_reviews = 1
maximum_authentication_operations = 1
maximum_finality_events = 1
maximum_successful_effects = 1
delegation_permitted = false
transfer_permitted = false
reset_permitted = false
reissue_permitted = false
recurrence_permitted = false
revival_permitted = false
record_digest
~~~

### Authentication key-binding record

~~~text
record_type = HUMAN_FOUNDER_AUTHENTICATION_KEY_BINDING_RECORD
record_version = V1
producing_owner
human_actor_identity
external_capacity_identity
external_capacity_digest
authentication_algorithm = ED25519_RFC8032_PURE
public_key_encoding = BASE64URL_NO_PAD_RAW_32_OCTETS
authentication_public_key
authentication_key_identity
binding_method = EXTERNAL_PREMISE_OWNER_ATTESTED_CAPACITY_BINDING
binding_result = VALID_FOR_EXACT_CAPACITY
record_digest
~~~

Strict base64url decoding must yield exactly 32 octets. The key identity is:

~~~text
human-founder-ed25519-key-v1:SHA256(decoded_public_key_octets)
~~~

The actual future public key is external evidence. No key is selected here.

### Nested deterministic verification profile

Option A is selected: the complete verification contract is nested in the
capacity evidence. A separate verification family would add one retrieval,
identity, owner, lifecycle, and Replay dependency without adding authority or
determinism.

~~~text
record_type = HUMAN_FOUNDER_AUTHENTICATION_VERIFICATION_PROFILE
record_version = V1
producing_owner
algorithm_identifier = ED25519_RFC8032_PURE
algorithm_specification = RFC8032_ED25519_PURE
public_key_encoding = BASE64URL_NO_PAD_RAW_32_OCTETS
signature_encoding = BASE64URL_NO_PAD_RAW_64_OCTETS
message_representation = EXACT_UTF8_CJ1_P_AUTH_V2_BYTES
digest_before_signature = NONE
context_string = EMPTY
prehash_mode = NONE
key_identity_prefix = human-founder-ed25519-key-v1
trust_anchor_mode = PREMISE_ACTOR_CAPACITY_KEY_BINDING
trust_anchor_digest
domain_identity =
  HUMAN_FOUNDER_CANDIDATE_H_FIRST_ADOPTION_P_AUTH_V2_CJ1_UTF8
malformed_input_result = FALSE
unknown_algorithm_result = FALSE
noncanonical_encoding_result = FALSE
verification_true_result = TRUE
verification_false_result = FALSE
record_digest
~~~

`trust_anchor_digest` is SHA-256 of the CJ1 object containing the exact
Premise pair, actor identity-record digest, capacity-record digest, and
key-binding-record digest. The profile fields are fixed constants. A mismatch
rejects the entire capacity artifact; an external source cannot redefine the
algorithm while retaining the accepted profile type/version.

The deterministic verification reduction is:

~~~text
VERIFY(profile, key_record, message_bytes, signature_text):
  require every profile constant above
  require message_bytes == UTF8(CJ1(resolved P_auth_v2))
  require strict base64url-no-pad key decode length == 32
  require recomputed key identity == declared key identity
  require strict base64url-no-pad signature decode length == 64
  require RFC8032 Ed25519 pure verification over exact message_bytes
  return TRUE only for successful verification
  return FALSE for every malformed, unknown, noncanonical, or invalid input
~~~

There is no digest-to-sign adapter and no algorithm selector at runtime.
Replay uses the nested profile and persisted key/signature bytes only.

### Capacity status read-back record

~~~text
record_type = HUMAN_FOUNDER_CAPACITY_STATUS_READ_BACK_RECORD
record_version = V1
producing_owner
external_capacity_identity
external_capacity_digest
status_authority_identity
status_slot_identity
status_epoch
status_generation
predecessor_status
current_status = ACTIVE
status_cas_identity
status_cas_digest
authoritative_read_back_identity
authoritative_read_back_digest
read_back_status_digest
status_effective_logical_instant
read_back_result = EXACT_CAPACITY_STATUS_CURRENT
record_digest
~~~

Status authority equals producing owner. The CAS identity/digest is
source-issued under the exact capacity/status slot and must recompute from the
full nested CAS body. Read-back binds that CAS pair, slot/epoch/generation,
current ACTIVE status, and status digest. A missing/stale/revoked/expired/
conflicting read-back rejects capacity before authentication claim.

The surrounding Target, finality domain, authentication slot, decision slot,
epochs, limits, flags, and issued time must equal every corresponding nested
record value. No nested record may introduce a second actor, capacity, Target,
key, scope, owner, domain, slot, or epoch.

## Durable Authentication Result and State Machine

The second new family is
`HumanFounderAuthenticationResultReadBackEvidenceV1`, artifact version `V1`,
contract version `CANDIDATE_H_AUTHENTICATION_REDESIGN_REVISION_2_V1`, identity
prefix `human-founder-auth-result-readback-v1`, and idempotency prefix
`human-founder-auth-result-readback-idem-v1`.

Its producing owner and result custodian are exactly the capacity producing
owner/external Premise authority. This is persistence/read-back custody only.

The exact state machine is:

~~~text
OPEN
  -> AUTHENTICATING
  -> AUTHENTICATED_FINAL

AUTHENTICATING
  -> INDETERMINATE_EXHAUSTED
~~~

`AUTHENTICATED_FINAL` and `INDETERMINATE_EXHAUSTED` are terminal and have no
outgoing edge. OPEN-to-AUTHENTICATING claim occurs before invoking the signer.
Only the claimed operation identity may complete that slot. Recovery from
AUTHENTICATING may read an already produced result; it must never invoke the
signer again. If the exact result cannot be recovered, one terminal CAS moves
to INDETERMINATE_EXHAUSTED, permanently exhausting the capacity without a
valid HumanDecision or founding effect.

The exact 37-field semantic payload is:

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
24 one_use_non_equivocation_proof_identity
25 one_use_non_equivocation_proof_digest
26 authentication_terminal_cas_identity
27 authentication_terminal_cas_digest
28 authoritative_read_back_identity
29 authoritative_read_back_digest
30 read_back_authentication_slot_digest
31 signature_verification_result
32 conflict_status
33 retry_permitted = false
34 second_authentication_permitted = false
35 capacity_permanently_exhausted
36 completion_logical_instant
37 terminal = true
~~~

Presence is exact:

| Field/result | `AUTHENTICATED_FINAL` | `INDETERMINATE_EXHAUSTED` |
|---|---|---|
| signature | non-null exact 64-octet encoding | canonical null |
| authentication_result | `AUTHENTICATED_VALID` | `INDETERMINATE_NO_VALID_RESULT` |
| terminal slot | `AUTHENTICATED_FINAL` | `INDETERMINATE_EXHAUSTED` |
| verification result | `TRUE` | `NOT_APPLICABLE` |
| conflict status | `NONE` | `RESULT_UNRECOVERABLE_NO_RETRY` |
| capacity exhausted | true | true |

All other fields are mandatory and non-null.

### Pre-sign operation pair

`P_operation` contains exactly:

~~~text
external_premise pair
capacity pair
human_actor_identity
human_authentication_slot_identity
human_authentication_epoch
authentication_sequence = 1
authentication_commitment pair
authenticated_message_representation
authenticated_message_digest
signature_scheme
signature_key_identity
predecessor_slot_status = OPEN
~~~

~~~text
authentication_operation_identity =
  human-founder-auth-operation-v1:SHA256(CJ1(P_operation))

authentication_operation_digest = sha256:SHA256(CJ1(P_operation))
~~~

The operation pair exists before signing and contains no signature or
HumanDecision pair.

### Claim CAS

`P_claim_cas` contains the operation pair, authentication slot/epoch/sequence,
capacity pair, predecessor OPEN, successor AUTHENTICATING, one-use claim token
identity/digest, and claim logical instant. Its pair is:

~~~text
authentication_claim_cas_identity =
  human-founder-auth-claim-cas-v1:SHA256(CJ1(P_claim_cas))

authentication_claim_cas_digest = sha256:SHA256(CJ1(P_claim_cas))
~~~

Only one claim CAS may win for the slot. A different operation, message,
capacity, actor, key, or commitment loses and cannot invoke the signer.

### Terminal CAS and read-back

`P_terminal_cas` contains exact operation and claim-CAS pairs, predecessor
AUTHENTICATING, selected terminal status, result, conditional signature,
verification result, one-use/non-equivocation proof pair, conflict status,
capacity exhaustion true, and completion logical instant.

~~~text
authentication_terminal_cas_identity =
  human-founder-auth-terminal-cas-v1:SHA256(CJ1(P_terminal_cas))

authentication_terminal_cas_digest = sha256:SHA256(CJ1(P_terminal_cas))
~~~

`P_read_back` contains the terminal-CAS pair, slot/epoch/sequence, capacity and
operation pairs, terminal status/result, conditional signature digest,
completion instant, and exact terminal slot digest.

~~~text
authoritative_read_back_identity =
  human-founder-auth-readback-v1:SHA256(CJ1(P_read_back))

authoritative_read_back_digest = sha256:SHA256(CJ1(P_read_back))
~~~

The result artifact is derived only after exact read-back. Its completion
logical instant equals the external terminal-CAS token instant, never wall
time or serialization time.

### Persistence, retry, and conflict rules

The authoritative persistence point is the external terminal CAS plus exact
read-back. Success is not constitutionally established when a signature is
computed transiently; it is established only when AUTHENTICATED_FINAL and the
signature/result are durably committed and read back.

~~~text
same slot + same operation
-> same terminal CAS/read-back/result artifact

same slot + different operation/message/key/signature/result
-> conflict; no HumanDecision; no second signer invocation

AUTHENTICATING + recoverable exact signer result
-> persist that same result; never sign again

AUTHENTICATING + no recoverable exact result
-> INDETERMINATE_EXHAUSTED; never sign again
~~~

No retry may reopen a terminal slot, change disposition/review/message/key,
resample time, or request Human interaction. The state machine adds no internal
State family: the exact claim and terminal CAS/read-back bodies are closed
semantic subcontracts of this one external result family.

## HumanDecisionV2 Revision 2 Contract

`ExternalConstituentHumanFirstAdoptionDecisionV2` remains the sole existing
family version successor. It uses artifact version `V2`, contract version
`CANDIDATE_H_AUTHENTICATION_REDESIGN_REVISION_2_V1`, identity prefix
`human-founding-decision-v2`, idempotency prefix
`human-founding-decision-idem-v2`, and producing owner `HUMAN_AUTHORITY`.

Revision 2 adds the durable result pair to G77-69's V2 proposal. The exact
31-field semantic payload is:

~~~text
01 universe_identity
02 universe_digest
03 source_identity
04 source_digest
05 instrument_identity
06 instrument_digest
07 target_identity
08 target_digest
09 human_custody_owner_identity = HUMAN_AUTHORITY
10 human_actor_identity
11 human_founder_external_capacity_evidence_identity
12 human_founder_external_capacity_evidence_digest
13 human_finality_domain_identity
14 human_finality_domain_digest
15 human_decision_slot_identity
16 human_decision_epoch
17 human_decision_sequence = 1
18 decision = ADOPT_EXACT_TARGET | REFUSE_EXACT_TARGET
19 supersession_permitted = false
20 predecessor_finality_slot_status = OPEN
21 human_confirmation_identity
22 human_confirmation_digest
23 authentication_commitment_identity
24 authentication_commitment_digest
25 authentication_result_read_back_identity
26 authentication_result_read_back_digest
27 authenticated_message_representation = EXACT_UTF8_CJ1_P_AUTH_V2_BYTES
28 human_signature_scheme = ED25519_RFC8032_PURE
29 human_signature_key_identity
30 human_signature
31 decision_effective_at
~~~

Validation requires:

~~~text
human_custody_owner_identity == producing_owner == HUMAN_AUTHORITY
human_actor_identity == capacity actor record identity
capacity pair == exact resolved capacity artifact
authentication commitment pair == recomputed P_auth_v2 pair
authentication result pair == exact AUTHENTICATED_FINAL read-back artifact
scheme/key/signature == exact durable result fields
message representation/digest == exact durable result and P_auth_v2
decision/Target/confirmation/effective time == exact act/review/manifest values
~~~

An INDETERMINATE_EXHAUSTED result cannot produce HumanDecisionV2. The common
V2 identity formulas apply. The dependency is forward:

~~~text
P_auth_v2 -> claim -> one signer invocation -> durable terminal read-back
-> HumanDecisionV2
~~~

No HumanDecision field participates in `P_auth_v2`, operation, claim CAS, or
terminal result identities.

## Exact P_auth_v2 and One-Message Rule

Revision 2 retains the exact HFD-04 25-field `P_auth_v2`, its pair, the domain
token, and direct-byte mode confirmed by G77-70:

~~~text
authentication domain pair
canonical act pair
review projection pair
candidate common-base digest
Candidate H input-reference manifest pair
Human Founder external-capacity pair
external authority-evidence manifest pair
authority provenance-evidence pair
authority competence-evidence pair
Human finality-domain pair
Human finality slot and epoch
finality sequence = 1
permanent exhaustion required = true
~~~

~~~text
M = UTF8(CJ1(P_auth_v2))
authenticated_message_digest = sha256:SHA256(M)
~~~

HFD authentication bytes and Candidate H P012 bytes are exactly M. Capacity,
verification profile, actor, key, Target, finality, and one-shot semantics are
transitively bound through exact pairs and complete nested capacity content.
There is no second message, digest-to-sign adapter, or signature copy.

## Replay-Visible P012 Contract-Version Dispatch

Option C is selected because it is the smallest lawful persisted binding. The
existing ProofSetV3 common envelope already contains `contract_version`, and
that field participates in its identity. Revision 2 requires:

~~~text
ProofSetV3.contract_version =
  CANDIDATE_H_AUTHENTICATION_REDESIGN_REVISION_2_V1
~~~

The exact closed dispatch table for that contract version is:

| Rank | Persisted predicate token | Subject type | Subject version | Validation semantics |
|---:|---|---|---|---|
| 12 | `P012_HUMAN_DECISION_VALID` | `ExternalConstituentHumanFirstAdoptionDecisionV2` | `V2` | `P012_HUMAN_DECISION_VALID_V2` defined below |

Any other subject type/version at rank 12 is FALSE. Under every predecessor
ProofSet contract version, HumanDecisionV2 is unknown/ineligible. Under the
Revision 2 token, the displayed tuple has exactly one rule. Thus the same row
bytes cannot have two meanings because ProofSet contract-version bytes differ
and change ProofSet idempotency, identity, digest, predicate root context,
Certification pair, and Replay dispatch.

CertificationV3 and TransitionV3 retain artifact version V3 but require their
own common `contract_version` to equal the Revision 2 token and require the
resolved ProofSet pair to carry the same token. Certification recomputes the
twenty rows under that dispatch. Replay rejects an unknown/mismatched token.

The P012 V2 row remains:

~~~text
rank = 12
predicate_code = P012_HUMAN_DECISION_VALID
subject_artifact_type = ExternalConstituentHumanFirstAdoptionDecisionV2
subject_artifact_version = V2
subject_identity = exact HumanDecisionV2 identity
subject_digest = exact HumanDecisionV2 digest
expected_digest = HumanDecisionV2.authentication_commitment_digest
observed_digest = sha256:SHA256(CJ1(reconstructed P_auth_v2))
result = TRUE | FALSE
~~~

P012 is TRUE if and only if:

1. ProofSet contract version selects the exact dispatch row;
2. HumanDecisionV2 envelope/schema/formulas validate;
3. capacity artifact and all nested records validate under exact contracts;
4. capacity status is ACTIVE at the authentication claim;
5. exact act, review, manifest, Target, actor, custody, finality, slot, epoch,
   sequence, decision, no-supersession, and effective-time equalities hold;
6. exact `P_auth_v2`, message bytes, pair, and digest recompute;
7. durable result is AUTHENTICATED_FINAL for the exact operation/capacity/
   commitment/message/key and has one-use terminal read-back;
8. scheme/key/signature equal the durable result and capacity key record;
9. nested verification profile returns TRUE over exact M;
10. HumanDecision identity/digest include that exact result pair and signature;
    and
11. no conflict, ambiguity, alternate encoding/message, unknown field,
    half-pair, invalid null, or second operation exists.

Any failed condition yields FALSE. P012 cannot choose or create actor,
authority, capacity, key, decision, signature, result, or finality.

## Exact Transitive Successor and Reuse Closure

The current 30 consumer groups are reconstructed from G77-62/G77-64. Artifact
version is advanced only when schema or exact type/version semantics cannot
lawfully consume the Revision 2 pairs. The persisted common contract-version
dispatch is not an artifact-version successor.

| Current family or consumer group | Classification | Revision 2 disposition |
|---|---|---|
| External Premise | `UNCHANGED_REUSE` | exact existing pair and external owner |
| SourceCommitmentV1 | `UNCHANGED_REUSE` | Target pair only |
| InstrumentCommitmentV3 | `UNCHANGED_REUSE` | no HumanDecision/P012 dependency |
| UniverseV1 / CandidateCensusV1 | `UNCHANGED_REUSE` | candidate/pair closure only |
| SourceEvidenceV1 / RecognitionProofV1 | `UNCHANGED_REUSE` | exact external evidence pairs |
| NormativePayloadV1 / TargetV5 | `UNCHANGED_REUSE` | predecessors of Human decision |
| InstrumentV4 | `UNCHANGED_REUSE` | predecessor of Human decision |
| HumanDecisionV1 | `VERSION_SUCCESSOR_REQUIRED` | V2 has changed schema, identity domain, custody, capacity, and durable-result pair |
| HumanFinalityV1 | `UNCHANGED_REUSE` | decision pair is version-opaque; no fixed version field |
| DispositionEvidence V2/V3 | `UNCHANGED_REUSE` | exact decision/finality pair and status equality |
| external status/current version/snapshot | `UNCHANGED_REUSE` | resolved type/version rows already explicit |
| ProofSetV3 | `UNCHANGED_REUSE` | same schema/version; exact common contract-version dispatch is persisted |
| CertificationV3 | `UNCHANGED_REUSE` | same schema/version; validates ProofSet contract token and pair |
| FoundingTransitionV3 | `UNCHANGED_REUSE` | same schema/version; consumes exact Certification/ProofSet/decision pairs |
| FenceV1 / BEGIN CAS | `UNCHANGED_REUSE` | pair opaque and same Transition artifact version |
| OperationSeed/token/AllocationIntentV2 | `UNCHANGED_REUSE` | generic immutable pair inputs |
| ALLOCATED CoordinatorStateV2 | `UNCHANGED_REUSE` | allocation row unchanged |
| allocation CAS/marker/read-back/Receipt | `UNCHANGED_REUSE` | generic root-pair serialization |
| LogicalPointer/Projection/Manifest/route Censuses | `UNCHANGED_REUSE` | no predicate interpretation |
| ordinary-chain CensusV2 | `UNCHANGED_REUSE` | TargetV5/route closure unchanged |
| CAP Reachability StateV2 | `UNCHANGED_REUSE` | Census/Target closure unchanged |
| Dormancy Rebase GuardV2 | `UNCHANGED_REUSE` | consumes TransitionV3 pair; artifact version remains V3 |
| MetaRepairTransitionV3 | `UNCHANGED_REUSE` | Guard artifact version remains V2 |
| MetaRepairStateV3 | `UNCHANGED_REUSE` | Guard/Meta/Transition artifact versions unchanged |
| failure Census/FailureEvidenceV2 | `UNCHANGED_REUSE` | pair-opaque failure reduction |
| terminal CommitmentV3 | `UNCHANGED_REUSE` | exact TransitionV3/GuardV2/Meta V3 versions remain unchanged |
| consuming operation/ConsumeIntentV2 | `UNCHANGED_REUSE` | commitment pair opaque |
| terminal CoordinatorV4 / RootSnapshotV4 | `UNCHANGED_REUSE` | Commitment remains V3; Coordinator/Root versions unchanged |
| terminal CAS/read-back/AttemptTerminalReadBack | `UNCHANGED_REUSE` | compare/hash exact pairs only |
| ReceiptV3/DormancyV2/Replay/CRO | `UNCHANGED_REUSE` | pair opaque; Replay dispatches persisted contract version read-only |

Exact counts:

~~~text
current consumer groups = 30
unchanged reuse groups = 29
existing artifact-family version successors = 1
new artifact families = 2
new nested verification artifact families = 0
new internal State families = 0
new external CAS/read-back artifact families beyond result family = 0
~~~

## Identity DAG

~~~text
authenticated external Premise + HFD/G77 lineage + exact Target/finality domain
-> complete nested actor/capacity/provenance/competence/scope/key/profile/status
-> HumanFounderExternalCapacityEvidenceV1
-> HFD manifest/act/review -> P_auth_v2
-> pre-sign authentication operation pair
-> OPEN-to-AUTHENTICATING claim CAS
-> at most one signer invocation
-> terminal CAS -> authoritative read-back
-> HumanFounderAuthenticationResultReadBackEvidenceV1
-> HumanDecisionV2
-> retained HumanFinalityV1 -> decision Disposition
-> ProofSetV3 with persisted contract-version dispatch
-> CertificationV3 -> TransitionV3
-> retained Fence/BEGIN or retry-without-BEGIN
-> retained Census/CAP/Guard/Meta/Commitment/Coordinator/Root chain
-> terminal disposition/Receipt/Dormancy/exhaustion
-> read-only Replay -> passive CRO
~~~

Cycle tests:

| Candidate cycle | Result |
|---|---|
| signature inside P_auth | absent |
| HumanDecision pair inside operation/result | absent |
| result pair inside its claim/terminal CAS | absent; CAS binds pre-sign operation, result artifact derives after read-back |
| capacity depends on signature/result | absent |
| ProofSet/Certification/Transition backward edge | absent |
| root/Replay predecessor edge | absent |

The graph is finite, acyclic, forward-derived, byte-deterministic,
domain-separated, and Replay reconstructible. Every edge ends at a finalized
predecessor; no wall clock, repository order, conversation, or hidden adapter
supplies identity content.

## Authority DAG

~~~text
Human Founder
-> independently prior external identity/capacity/competence
-> one Human choice/review and at most one signer invocation

HUMAN_AUTHORITY
-> HumanDecision/Finality custody and producing ownership only

external authentication-result custodian
-> claim/terminal CAS persistence and read-back only

Candidate H -> deterministic validation only
Certification -> predicate evidence only
Governance -> already granted deterministic mechanics only
root custodian -> existing-domain mechanical serialization/CAS only
HIC/CHE -> transport only
Replay -> read-only reconstruction
CRO -> passive observation
~~~

The result custodian equals the independently prior external Premise owner and
is not a new internal owner. Capacity evidence, a valid signature, durable
result, P012 TRUE, Certification, persistence, key possession, Replay, or root
success cannot create external constituent authority. `HUMAN_AUTHORITY` cannot
populate actor, capacity, competence, key binding, or external ownership.

## Crash and Retry Matrix

| Boundary | Authoritative predecessor/read-back | Allowed retry | Forbidden Human action | Deterministic result |
|---|---|---|---|---|
| before review | exact act candidates/capacity evidence | redisplay same bytes | no machine choice/signature | same candidates or stop |
| after review | exact selected act/review pair | read same pair | no second review/disposition | identical review |
| before auth operation | exact P_auth/operation pair; auth slot OPEN | claim once | no new review/message/key | same claim candidate |
| after claim before signer | AUTHENTICATING claim read-back | continue claimed operation once | no second claim/Human input | same operation only |
| during authentication | AUTHENTICATING slot | recover existing signer outcome only | signer must not be invoked again | result or indeterminate exhaustion |
| signature produced before terminal CAS | claim plus owner-local claimed-operation outcome | persist exact existing outcome | no second signature | same terminal candidate |
| terminal CAS before read-back | terminal CAS pair | read slot | no signer/Human retry | exact terminal state |
| durable read-back before result artifact | terminal read-back pair | derive result artifact | no second signature | identical result identity |
| durable result before HumanDecision | exact AUTHENTICATED_FINAL result | derive HumanDecisionV2 | no Human/signature interaction | identical HumanDecision |
| indeterminate terminal result | exact INDETERMINATE_EXHAUSTED result | read only | no retry/review/signature | no HumanDecision/effect; permanent exhaustion |
| after HumanDecision before Finality | exact decision plus OPEN finality slot | retained finality CAS | no new decision/signature | OPEN or exact FINAL |
| after Finality before BEGIN | exact FINAL/Disposition/Proof/Certification/Transition | retained initial retry | no Human interaction | same BEGIN candidate |
| after BEGIN before root CAS | exact CONSUMING read-back | retained root recovery | no BEGIN/signature repeat | same consuming event |
| during/after root CAS | retained CAS/marker/current-root read-back | reconstruct same chain | no Human interaction | predecessor or exact successor |
| before terminal exhaustion | exact root and external disposition read-backs | derive terminal evidence | no Founder revival | one terminal candidate |
| after terminal exhaustion | exact Dormancy/Receipt/exhaustion | read only | no reset/reissue/review/signature | identical permanent terminal state |

No retry resamples time. Claim and completion logical instants are source-token
instants inside persisted CAS records. If an AUTHENTICATING operation cannot
recover the existing outcome, it terminalizes indeterminate and cannot revive.

## Replay Closure

Starting from persisted artifacts only, Replay:

1. authenticates Premise, HFD/G77 lineage, Target, and finality domain;
2. validates capacity owner equality and every complete nested record;
3. reconstructs actor, capacity, provenance, competence, scope, key material,
   fixed verification profile, status CAS/read-back, slots, epochs, and limits;
4. reconstructs act, exact ReviewProjectionV2, and exact `P_auth_v2`;
5. emits the authenticated bytes as `UTF8(CJ1(P_auth_v2))`;
6. recomputes operation, claim CAS, terminal CAS, read-back, and result pairs;
7. validates exact scheme/key/signature and deterministic Ed25519 result;
8. reads ProofSet contract version and selects exactly one P012 V2 dispatch;
9. recomputes HumanDecisionV2, Finality, Disposition, twenty ProofSet rows,
   Certification, and Transition;
10. reconstructs BEGIN/retry, root result, terminal evidence, and exhaustion;
    and
11. returns the same evidence without writing.

Replay needs no conversation, Human memory, external authenticator memory,
live clock, repository traversal order, hidden adapter, or off-payload
semantic choice. An unknown contract version/profile/algorithm or missing
read-back yields deterministic rejection.

## One-Shot Proof

| Maximum/effect | Exact ceiling/proof |
|---|---|
| Human dispositions | 1; act/capacity/scope sequence |
| Human reviews | 1; exact ReviewProjectionV2 pair |
| authentication operations | 1; one OPEN-to-AUTHENTICATING claim per slot |
| valid authentication results | 1; one terminal CAS/read-back |
| finality events | 1; retained one-use finality slot |
| successful founding effects | 1; retained external fence and root CAS |

ADOPT and REFUSE permanently exhaust the Human Founder capacity through the
retained finality/exhaustion rules. INDETERMINATE_EXHAUSTED also consumes the
authentication capacity with no decision or effect. No terminal state permits
Founder revival, reset, reissue, recurrence, target substitution, reusable
credential, second review/signature/finality, or post-founding override.
Ordinary G70 remains the sole later amendment lifecycle.

## Machinery Pressure

| Machinery | Classification | Minimality result |
|---|---|---|
| HumanFounderExternalCapacityEvidenceV1 | `STRICTLY_REQUIRED` | closes actor/capacity/verification/status predecessors without reinterpretation |
| nested verification profile | `STRICTLY_REQUIRED` | deterministic VERIFY; nesting avoids a third family |
| HumanFounderAuthenticationResultReadBackEvidenceV1 | `STRICTLY_REQUIRED` | closes crash after signature and before HumanDecision |
| AUTHENTICATING claim state | `STRICTLY_REQUIRED` | prevents a second signer invocation after crash |
| claim and terminal CAS/read-back subcontracts | `STRICTLY_REQUIRED` | one-winner persistence and deterministic recovery |
| HumanDecisionV2 result pair | `STRICTLY_REQUIRED` | binds final decision to durable authentication evidence |
| persisted ProofSet contract-version dispatch | `STRICTLY_REQUIRED` | makes P012 semantics Replay-visible |
| separate verification artifact family | `AVOIDABLE_CONSTITUTIONAL_MACHINERY` | exact profile is closed inside capacity evidence |
| ProofSetV4 through RootV5 cascade | `AVOIDABLE_CONSTITUTIONAL_MACHINERY` | persisted common contract version changes semantics without changing schemas/versions |
| separate claim/terminal State artifact families | `AVOIDABLE_CONSTITUTIONAL_MACHINERY` | exact external CAS/read-back subcontracts fit one result family |
| second message/signature/Human review | `AVOIDABLE_CONSTITUTIONAL_MACHINERY` | violates one-shot design |
| new internal owner/root/domain/path | `AVOIDABLE_CONSTITUTIONAL_MACHINERY` | retained spine and external owner suffice |

## Topology

| Measure | Before | After proposed design | Delta |
|---|---:|---:|---:|
| production paths | 1 | 1 | 0 |
| parallel production paths | 0 | 0 | 0 |
| persistent founding paths | 0 | 0 | 0 |
| Human entry points | 1 | 1 | 0 |
| HIC families | 1 | 1 | 0 |
| CHE definitions | 1 | 1 | 0 |
| root paths | 1 | 1 | 0 |
| internal owners | retained | retained | 0 |
| current roots | 1 | 1 | 0 |
| root serialization domains | retained | retained | 0 |
| persistent founding authorities | 0 | 0 | 0 |

The authentication slot and CAS/read-back are within the independently prior
external Human domain and add evidence on the existing spine. They are not a
new Human entry, HIC/CHE route, internal serialization domain, or root path.

## Reuse Impact Assessment

1. **Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?**

   Ponovno se uporabijo CJ1 in SHA-256, G76 usmerjeni identitetni graf,
   G69-07 meja skrbništva `HUMAN_AUTHORITY`, HFD-04 akt, pregled in isti
   `P_auth_v2`, G77-44 vzorec zunanjega CAS/read-back, obstoječi Candidate H
   Universe/Census/Target/Instrument, HumanFinality, Disposition, ProofSetV3,
   CertificationV3, TransitionV3, Fence/BEGIN, CAP/Guard/MetaRepair, korenska
   pot, HIC/CHE ter pasivni Replay/CRO.

2. **Katere nove zmogljivosti (če sploh) nastanejo?**

   Predlagani sta natanko dve novi dokazni družini: zaprta Human Founder
   capacity evidence in trajna authentication-result/read-back evidence.
   HumanDecision dobi eno verzijsko naslednico V2. Verifikacijski profil je
   natančno vgnezden in ne ustvari tretje družine.

3. **Ali katera obstoječa zmogljivost postane nedosegljiva?**

   Ne. HumanDecisionV1 ostane zgodovinski in nespremenjen, vendar je za novi
   contract-version P012 nedopusten. Vsi aktivni G69/G70, HIC/CHE, korenski in
   Replay tokovi ostanejo dosegljivi. Candidate H ostane neaktiviran.

4. **Ali implementacija ustvarja vzporedni tok?**

   Ne. Implementacije ni. Novi dokazni družini sta predhodnika na istem Human
   in Candidate H toku; ne ustvarita drugega sporočila, podpisa, Human vhoda,
   HIC/CHE poti ali korenske poti.

5. **Ali zmanjšuje ali povečuje število produkcijskih poti?**

   Ne. Ostane ena produkcijska pot, nič vzporednih poti in nič trajnih
   ustanovitvenih poti.

## Proposal Verdict Rationale

All four G77-70 blockers are closed at proposal level:

- durable result/read-back precedes HumanDecision and survives crashes;
- capacity and verification inputs are complete nested canonical content;
- P012 semantics are selected by persisted identity-bearing contract-version
  bytes; and
- full consumer review proves one version successor, two new families, and
  twenty-nine existing-version reuses without an implicit adapter.

This is not an independent assessment, implementation contract, activation,
or production-readiness claim. A later independent assessment remains
mandatory.

# 2. Code Evidence

## Public API

No API, runtime callable, schema implementation, validator, route, command,
store, credential, key, provider, configuration, deployment, or production
behavior is added or changed. All families and algorithms are proposal-only.

## Orchestration Entry Point

No entry point is created. The sole conceptual route remains:

~~~text
Human review -> exact P_auth_v2 -> one claimed authentication operation
-> durable result read-back -> HumanDecisionV2 -> retained HIC/CHE
-> Candidate H validation -> retained one-shot execution/root spine
~~~

## Semantic Reductions

~~~text
AUTHENTICATED_FINAL durable read-back
+ exact HumanDecision equality
+ persisted ProofSet contract-version dispatch
-> P012 TRUE may be derived

INDETERMINATE_EXHAUSTED OR missing/mismatched evidence
-> no HumanDecisionV2
-> P012 FALSE
-> no BEGIN
~~~

## Public Validators

No validator is implemented. The proposal defines exact capacity, state,
verification, HumanDecision, P012, conflict, retry, and Replay reductions. A
future validator must reject unknown contract versions, algorithms, fields,
encodings, owners, pairs, States, messages, or results.

## Canonical Data Models

Two new V1 evidence families and one HumanDecisionV2 successor are proposed.
All nested capacity records and authentication CAS/read-back bodies are closed
inside those families. All other current artifact versions are retained.

## Deterministic Algorithms

CJ1, SHA-256, strict base64url decoding, fixed RFC8032 Ed25519 pure
verification, one-winner external CAS/read-back, exact contract-version
dispatch, terminal reconstruction, and read-only Replay are deterministic.
No live clock, selector, repository order, second signer call, or adapter is
permitted.

## Responsibility Boundaries

The Human Founder supplies external identity/capacity/choice/authentication.
`HUMAN_AUTHORITY` supplies custody only. The result custodian persists and
reads back only. Candidate H validates, Certification records predicates,
Governance/root owners perform existing mechanics, HIC/CHE transport, Replay
reconstructs, and CRO observes.

## Repository Evidence

Evidence consists of authenticated G48, G69, G70, G76, G77-42/44/52/53/
62-70, HFD-01 through HFD-06, exact Git HEAD/tree/status, independent schema
and consumer inventories, focused G69/G70 tests, G48 structure checks, and
repository mutation/format validation. No Human, key, signature, external
fact, or runtime result supplies proposal content.

# 3. Constitutional Self-Assessment

## Verified at Proposal Level

- G77-69/G77-70 and controlling predecessor hashes are authenticated.
- G77-70's four findings are each addressed by an exact proposed contract.
- Capacity producing owner equals the external Premise authority identity.
- Actor, capacity, provenance, competence, scope, key, verification, and
  status evidence are complete nested canonical records, not opaque pairs.
- Verification uses one fixed deterministic profile and selects no actual key.
- Claim precedes signing and terminal read-back precedes HumanDecision.
- A crash cannot authorize a second signer invocation.
- Indeterminate recovery permanently exhausts without decision/effect.
- HumanDecisionV2 has exactly 31 semantic fields and binds the durable result.
- `P_auth_v2` remains the only authenticated message.
- ProofSetV3 contract-version bytes select exactly one P012 V2 rule.
- Certification and Replay validate the persisted dispatch.
- The exact current consumer inventory contains thirty groups.
- Twenty-nine groups retain existing artifact versions; HumanDecision alone
  advances artifact version; exactly two new families are proposed.
- The identity and authority DAGs are finite, acyclic, separated, and
  Replay-reconstructible.
- The crash matrix, one-shot ceilings, permanent exhaustion, and topology
  `1 / 0 / 0` are closed at proposal level.
- All actual effect classifications remain `NO`.
- Exactly one governance artifact is added and no predecessor is changed.

## Not Verified or Performed

- No independent assessment of G77-71 has occurred.
- No actual external Premise, Human identity, capacity evidence, status,
  public key, signature, operation, CAS, read-back, HumanDecision, Finality,
  ProofSet, Certification, Transition, BEGIN, root effect, or exhaustion
  instance exists.
- No runtime schema, serializer, Ed25519 verifier, P012 validator, persistence,
  retry, or Replay reader implements this proposal.
- No Human Ratification, implementation authorization, publication,
  activation, CLIA, deployment, or production authority exists.
- No Candidate H/G76-specific executable test module exists.
- Existing known hook drift and partial conformance remain visible and
  unchanged.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| repository HEAD/tree/branch | exact Git objects | Git inspection | `PASS` |
| clean proposal start | empty status | worktree inspection | `PASS` |
| G77-70 committed status | tracked HEAD subject | Git inspection | `PASS` |
| G77-69/G77-70 hashes | exact authenticated bytes | SHA-256 | `PASS` |
| controlling predecessor hashes | exact hash tables | SHA-256 | `PASS` |
| B01 durable result | claim/terminal CAS/read-back family | crash/state review | `PASS_PROPOSAL` |
| authentication state totality | OPEN/AUTHENTICATING/two terminal rows | state-machine review | `PASS_PROPOSAL` |
| no second signer call | claim before signer; recovery read-only or indeterminate | hostile retry review | `PASS_PROPOSAL` |
| capacity schema count | exact 32-field inventory | schema count | `PASS_32` |
| capacity owner | exact Premise authority equality | authority review | `PASS_PROPOSAL` |
| nested predecessor closure | eight complete record contracts | schema review | `PASS_PROPOSAL` |
| verification contract choice | complete nested option A | machinery review | `PASS_PROPOSAL` |
| deterministic verification | fixed Ed25519/encodings/message/failure rules | algorithm review | `PASS_PROPOSAL` |
| result schema count | exact 37-field inventory and presence rows | schema count | `PASS_37` |
| HumanDecision schema count | exact 31-field inventory | schema count | `PASS_31` |
| result equality | exact scheme/key/signature/result pair | field review | `PASS_PROPOSAL` |
| no identity cycle | operation/claim/result/decision forward order | DAG review | `PASS_PROPOSAL` |
| one authenticated message | exact UTF-8 CJ1 P_auth_v2 | byte-contract review | `PASS_PROPOSAL` |
| P012 version visibility | persisted ProofSet contract-version dispatch | Replay review | `PASS_PROPOSAL` |
| no same-byte/two-semantics | contract version is identity-bearing | identity review | `PASS_PROPOSAL` |
| Certification/Replay dispatch | exact token equality and unknown-token rejection | consumer review | `PASS_PROPOSAL` |
| transitive inventory | thirty current groups | repository-wide review | `PASS_30` |
| exact structural counts | 29 reused / 1 successor / 2 new | inventory count | `PASS` |
| identity DAG | finite/acyclic/forward/deterministic | DAG review | `PASS_PROPOSAL` |
| authority DAG | external/custody/result/validation/execution separation | authority review | `PASS_PROPOSAL` |
| crash/retry closure | sixteen explicit boundaries | deterministic review | `PASS_PROPOSAL` |
| Replay closure | persisted evidence only | reconstruction review | `PASS_PROPOSAL` |
| one-shot proof | all six maxima one; all terminal no-revival rules | lifecycle review | `PASS_PROPOSAL` |
| machinery pressure | no third family or ten-version cascade | minimality review | `PASS_PROPOSAL` |
| topology | exact unchanged count matrix | path review | `PASS` |
| Reuse Impact Assessment | five explicit Slovenian answers | completeness review | `PASS` |
| focused G69/G70 tests | 326 existing tests | pytest | `PASS` |
| Candidate H/G76 tests | no directly named module present | test inventory | `NOT_APPLICABLE` |
| six G48 top-level sections | exact H1 count/names/order | structure check | `PASS` |
| eight Code Evidence subsections | exact H2 count/names | structure check | `PASS` |
| balanced Markdown fences | fence-line count | format check | `PASS` |
| zero trailing whitespace | line scan | format check | `PASS` |
| repository whitespace | tracked and untracked diff checks | `git diff --check` | `PASS` |
| exact G77-71 artifact count | one new path | mutation inventory | `PASS` |
| predecessor immutability | no tracked predecessor diff | Git review | `PASS` |
| runtime/test/config/root/production mutation | no changed prohibited surface | mutation inventory | `PASS` |
| implementation/activation/signature | proposal-only prohibition | scope review | `NOT_APPLICABLE` |

# 5. Repository Mutation Summary

Modified files:

- added
  `docs/governance/G77_71_CANDIDATE_H_AUTHENTICATION_REDESIGN_REVISION_2_DURABLE_RESULT_P012_VERSION_AND_FULL_TRANSITIVE_CLOSURE_V1.md`
  as the sole G77-71 proposal artifact.

Unchanged subsystems:

- G77-70, G77-69, and every G48/G69/G70/G76/G77/HFD predecessor;
- Constitution, CAP/CDP/CLIA state, Candidate H runtime, Human Authority,
  external authority, HIC, CHE, Governance runtime, Certification runtime,
  Replay runtime, CRO, root persistence, release, deployment, routing,
  configuration, schemas, credentials, providers, production, and tests.

API compatibility:

- no API, runtime model, validator, serializer, route, command, workflow,
  owner, persistence primitive, deployment, or production contract is
  implemented or activated;
- all downstream public artifact versions except HumanDecision remain
  unchanged, selected by exact identity-bearing contract-version bytes.

Boundary preservation:

- this artifact is an unassessed proposal only;
- no Human act, signature, authority, implementation, activation, BEGIN,
  root mutation, deployment, or production effect occurs;
- Replay remains read-only and CRO remains passive; and
- topology remains one production path, zero parallel paths, and zero
  persistent founding paths.

Unrelated pre-existing changes:

- None observed. The worktree was clean at proposal start.

Worktree mutation count attributable to this task: `1` new governance file,
`0` modified existing files.

No commit is created.

# 6. Certification Verdict

G77_CANDIDATE_H_AUTHENTICATION_REDESIGN_REVISION_2_FULL_CLOSURE_ESTABLISHED
