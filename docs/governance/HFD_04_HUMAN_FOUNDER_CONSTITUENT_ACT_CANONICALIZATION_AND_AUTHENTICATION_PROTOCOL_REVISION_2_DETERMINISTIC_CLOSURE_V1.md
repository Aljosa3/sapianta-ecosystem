# 1. Implementation Summary

Proposal identity:
`HFD_04_HUMAN_FOUNDER_CONSTITUENT_ACT_CANONICALIZATION_AND_AUTHENTICATION_PROTOCOL_REVISION_2_DETERMINISTIC_CLOSURE_V1`

Proposal namespace: `HFD-04`

Proposal revision: `2`

Proposal status: `PROPOSAL_ONLY_UNASSESSED_NON_ACTIVATING`

Artifact class:
`HUMAN_FOUNDER_CONSTITUENT_ACT_PROTOCOL_REVISION_2_DETERMINISTIC_CLOSURE_PROPOSAL_PRE_ACT`

Authoritative design predecessor:
`HFD_02_HUMAN_FOUNDER_CONSTITUENT_ACT_CANONICALIZATION_AND_AUTHENTICATION_PROTOCOL_V1`

Authoritative independent assessment:
`HFD_03_INDEPENDENT_CONSTITUTIONAL_IMPACT_ASSESSMENT_HUMAN_FOUNDER_CONSTITUENT_ACT_PROTOCOL_V1`

Assessment verdict:
`HFD_02_CONSTITUTIONAL_IMPACT_REQUIRES_REWORK`

Reporting date: 2026-08-09.

Objective:

Propose only the minimum deterministic Revision 2 closure for the four HFD-03
findings: one byte-closed Human review object, complete proposal-level identity
and G76 boundaries, forward-only crash-safe finality/exhaustion semantics, and
one exact identity-preserving input mapping into frozen Candidate H. No Human,
disposition, identity, key, algorithm, signature, act, authentication result,
finality instance, adoption, activation, Candidate H instance, BEGIN, root
effect, implementation, deployment, or production authority is created.

Authenticated repository identity at proposal start:

- Commit: `55e7843432c56dbdd7a2fcfe24704ff88830a07f`
- Tree: `45fd48d7d1cf403c7419c928ccd2f12540271c17`
- Subject: `HFD-03: assess Human Founder constituent act protocol`
- Immediate parent: `125e3f8ee235b2bcbaa86513310ac7c899e13374`
- HFD-04-start worktree state: clean

Authenticated HFD lineage:

| Artifact | SHA-256 | Git blob | Role |
|---|---|---|---|
| `HFD_01_HUMAN_FOUNDER_EXTERNAL_CONSTITUENT_MODEL_DECISION_V1` | `f23c25a36a638961ffca25861576858e7a77c7f715c23e01783f66ad6743e982` | `bef75f0e86f84274db70bc3f0746bf942f5e920f` | immutable selected external model |
| `HFD_02_HUMAN_FOUNDER_CONSTITUENT_ACT_CANONICALIZATION_AND_AUTHENTICATION_PROTOCOL_V1` | `d6c0f2b4f71c40b91d94e47c5d1b38ccd77518b33598b792aa7c7c7051e084a6` | `48eeb5718b105ee49f6d5d982fccb958ad0e7502` | immutable Revision 1 design predecessor |
| `HFD_03_INDEPENDENT_CONSTITUTIONAL_IMPACT_ASSESSMENT_HUMAN_FOUNDER_CONSTITUENT_ACT_PROTOCOL_V1` | `1d8cceb4741bac022c82298db230e6fe8b6dce46eae32bf221de8cf14aa5b5e5` | `1f220c35c6df59f9653430927bd54a4322abe790` | immutable four-blocker assessment |

Authenticated G77 boundary lineage:

| Generation | SHA-256 | Role |
|---|---|---|
| G77-64 | `ac3deaf40e7f06c04e3396b161194b258b7ae993b65d9ee719fb1170fc4ac0c6` | frozen Candidate H Revision 4 subject |
| G77-65 | `9d5c40e861aa11d2f6ee173016f50dde57d4026fd85cf124b9c887b8e1449569` | independent Revision 4 convergence assessment |
| G77-66 | `9f33fade3019d5a3ddf4e1e286fccc011e812274af71076b4ddd0f96f601859d` | lifecycle transition audit |
| G77-67 | `236c613844532fb44ba9aa473df46fccea75fc603271373b6d7bf0fd692eff2b` | external adoption preparation package |
| G77-68 | `4331fcbc3849f71b2f6c07a6f60c39af6c24697bccdf3ef0f5bf8d1411abe027` | external handoff/internal-stop audit |

Relevant frozen Candidate H design lineage was also authenticated:

| Artifact | SHA-256 | Use |
|---|---|---|
| G77-42 | `b379cb057282aaf7d10c6e6e3f8a55053a630b19a0a0ad80e8159a0222b316a6` | exact CJ1, external evidence, HumanDecision/Finality families |
| G77-52 | `a55fe696c011d5edb6450f6b800925f8c5f33a1e9345a85adc20a0d0f358b18a` | converged one-shot founding model Revision 7 |
| G77-53 | `3ca5bcd6a91005c5ef34b7ef4b6fd4cb01bc9b2ea2c76db8b35b187938706658` | convergence confirmation |
| G77-62 | `661394be4e32b2e965f6a906e865a78128572084bbe52c5d0aad3bfdd5deca1e` | complete Candidate H Revision 3 schemas |
| G77-63 | `73190f6a7f919469b7d67f512cf955e9c5531b9f41170229061760f03c2ad7fe` | Revision 3 impact assessment |

## HFD-03 Blocker Disposition

| HFD-03 finding | Revision 2 disposition | Exact closure |
|---|---|---|
| B01 Human-review byte closure | `ADDRESSED_AT_PROPOSAL_LEVEL` | one nested exact `P_review_v2`, full payload commitment, 77-name inventory, semantic digest, and exact CJ1 byte display |
| B02 identity/G76 authorization | `ADDRESSED_AT_PROPOSAL_LEVEL` | exact protocol/predecessor pairs, common-base commitment, closed proposed namespaces/sources/formulas, and explicit non-activation rule |
| B03 finality/exhaustion crash recovery | `ADDRESSED_AT_PROPOSAL_LEVEL` | existing Candidate H FINAL evidence plus one derivable exhaustion record and forward-only derived state machine |
| B04 Candidate H input mapping | `ADDRESSED_AT_PROPOSAL_LEVEL` | one closed compatibility manifest, direct retained pairs, exact HumanDecision projection, existing HumanFinality/Disposition reuse, and no schema change |

Every disposition is a proposal claim requiring later independent assessment.
No blocker is silently repaired in runtime or by changing a predecessor.

## Required Effect Classifications

| Required classification | Exact result |
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

Topology remains exactly:

| Measure | Before | Revision 2 proposal |
|---|---:|---:|
| production paths | 1 | 1 |
| parallel production paths | 0 | 0 |
| persistent founding paths | 0 | 0 |

## Scope Preservation

Revision 2 does not reopen Human Founder model selection, Candidate H, G77-64
through G77-68, HFD-01, ordinary G70, root architecture, HIC/CHE, CLIA, or
production topology. It defines external message/evidence compatibility rules
only. The frozen Candidate H artifacts remain byte-identical and retain their
exact types, versions, owners, identities, predicates, and lifecycle.

~~~text
new HFD compatibility manifest and messages = proposed external predecessors

frozen Candidate H objects = existing exact families and bytes

mapping = direct pair reuse or closed deterministic projection

no mapping predicate satisfied
-> no Candidate H input set
-> no BEGIN eligibility
~~~

## Revision 2 Canonical Act Payload

Revision 2 completely replaces the HFD-02 act payload at proposal level with
`HumanFounderExternalConstituentActPayloadV2`. It has exactly 77 fields in the
following conceptual order; CJ1 still key-sorts object members:

~~~text
protocol_source_identity
protocol_source_digest
protocol_version
act_artifact_type
act_artifact_version
predecessor_protocol_identity
predecessor_protocol_digest
independent_assessment_identity
independent_assessment_digest
external_constituent_model_identity
human_founder_external_capacity_reference_identity
human_founder_external_capacity_reference_digest
external_authority_evidence_manifest_identity
external_authority_evidence_manifest_digest
authority_provenance_evidence_identity
authority_provenance_evidence_digest
authority_competence_evidence_identity
authority_competence_evidence_digest
candidate_h_input_reference_manifest_identity
candidate_h_input_reference_manifest_digest
g77_64_identity
g77_64_digest
g77_65_identity
g77_65_digest
g77_66_identity
g77_66_digest
g77_67_identity
g77_67_digest
g77_68_identity
g77_68_digest
hfd_01_identity
hfd_01_digest
founding_target_identity
founding_target_digest
disposition
disposition_sequence
maximum_authoritative_dispositions
exact_target_only
delegation_permitted
transfer_within_sapianta_permitted
reset_permitted
reissue_permitted
target_substitution_permitted
recurrence_permitted
post_terminal_revival_permitted
permanent_exhaustion_required
founder_post_founding_special_authority
ordinary_post_founding_governance_only
production_paths
parallel_production_paths
persistent_founding_paths
immediate_effect_ceiling
publication_authorized
normative_activation_authorized
g69_cdp_authorized
implementation_authorized
candidate_h_instantiation_authorized
begin_authorized
clia_validation_authorized
deployment_authorized
production_authorized
authentication_domain_identity
authentication_domain_digest
human_review_contract_identity
human_review_contract_source_identity
human_review_contract_source_digest
human_finality_domain_identity
human_finality_domain_digest
human_finality_slot_identity
human_finality_epoch
predecessor_finality_slot_status
finality_sequence
finality_required
non_equivocation_required
exhaustion_evidence_required
issued_at
candidate_common_base_digest
~~~

Constants are exact:

~~~text
protocol_source_identity =
  HFD_04_HUMAN_FOUNDER_CONSTITUENT_ACT_CANONICALIZATION_AND_AUTHENTICATION_PROTOCOL_REVISION_2_DETERMINISTIC_CLOSURE_V1
protocol_source_digest =
  sha256:SHA256(exact finalized HFD-04 file bytes)
protocol_version = V2
act_artifact_type = HUMAN_FOUNDER_EXTERNAL_CONSTITUENT_ACT
act_artifact_version = V2
predecessor_protocol_identity =
  HFD_02_HUMAN_FOUNDER_CONSTITUENT_ACT_CANONICALIZATION_AND_AUTHENTICATION_PROTOCOL_V1
predecessor_protocol_digest =
  sha256:d6c0f2b4f71c40b91d94e47c5d1b38ccd77518b33598b792aa7c7c7051e084a6
independent_assessment_identity =
  HFD_03_INDEPENDENT_CONSTITUTIONAL_IMPACT_ASSESSMENT_HUMAN_FOUNDER_CONSTITUENT_ACT_PROTOCOL_V1
independent_assessment_digest =
  sha256:1d8cceb4741bac022c82298db230e6fe8b6dce46eae32bf221de8cf14aa5b5e5
external_constituent_model_identity =
  HUMAN_FOUNDER_ONE_SHOT_EXTERNAL_CONSTITUENT_V1
human_review_contract_identity =
  HFD_04_HUMAN_FOUNDER_ACT_REVIEW_PROJECTION_V2
predecessor_finality_slot_status = OPEN
finality_sequence = 1
disposition_sequence = 1
maximum_authoritative_dispositions = 1
~~~

Every negative authority, topology, and effect field retains the exact HFD-02
value. Every pair is mandatory and non-null. Unknown, omitted, half-present,
wildcard, inferred, or extra fields fail closed.

The HFD-04 source digest is not embedded in HFD-04 itself. The future act is a
successor created only after this file is finalized and may bind its then
recomputed exact file digest. No self-reference exists.

## Frozen Common Base and Act Identity

Let `B_act_v2` be the CJ1 object formed from the 77-field act object by
excluding exactly `disposition` and `candidate_common_base_digest`. It contains
75 fields, including `issued_at` and every external/domain/reference value.

~~~text
candidate_common_base_digest = sha256:SHA256(CJ1(B_act_v2))

P_act_v2 = B_act_v2
  + disposition = ADOPT_EXACT_TARGET | REFUSE_EXACT_TARGET
  + candidate_common_base_digest

act_digest = sha256:SHA256(CJ1(P_act_v2))
act_identity =
  human-founder-constituent-act-v2-sha256:SHA256(CJ1(P_act_v2))
~~~

Two pre-selection candidates are valid only when:

1. both recompute the identical common-base digest;
2. all 75 common-base fields compare byte-for-byte equal;
3. one disposition is exactly `ADOPT_EXACT_TARGET` and the other exactly
   `REFUSE_EXACT_TARGET`; and
4. no other byte differs.

`issued_at` is fixed before candidate derivation as one externally supplied
source value under the future authenticated source contract. It is part of the
common base, so a preparation tool cannot resample it per candidate or retry.
No local, repository, Git, filesystem, network, serialization, or wall clock
may supply it. Candidate H `decision_effective_at` later copies these exact
timestamp bytes; it does not resample time.

Same base plus same disposition returns the identical act pair. Same base
digest with different base bytes, or same act identity with different bytes,
fails closed. The identity excludes only its own derived pair and contains no
successor evidence.

## B01 — Exact Human Review Projection V2

`HumanFounderActReviewProjectionV2` has one exact nested schema:

~~~text
review_artifact_type = HUMAN_FOUNDER_ACT_REVIEW_PROJECTION
review_artifact_version = V2
review_contract_source_identity
review_contract_source_digest
canonical_act_identity
canonical_act_digest
reviewed_field_count = 77
reviewed_field_names = [the exact 77 names in the displayed P_act_v2 order]
reviewed_field_name_root
reviewed_act_payload
reviewed_payload_digest
reviewed_semantic_root
review_completeness = COMPLETE_EXACT_NESTED_PAYLOAD
display_contract = EXACT_CJ1_UTF8_BYTE_VIEW
metadata = {}
~~~

The arrays and values are exact:

~~~text
reviewed_field_name_root =
  sha256:SHA256(CJ1(reviewed_field_names))

reviewed_act_payload = exact P_act_v2 object, nested without transformation

reviewed_payload_digest = sha256:SHA256(CJ1(reviewed_act_payload))

reviewed_semantic_root = sha256:SHA256(CJ1({
  reviewed_field_count,
  reviewed_field_names,
  reviewed_field_name_root,
  reviewed_act_payload,
  reviewed_payload_digest,
  canonical_act_identity,
  canonical_act_digest
}))

P_review_v2 = exact review schema above

review_projection_digest = sha256:SHA256(CJ1(P_review_v2))
review_projection_identity =
  human-founder-act-review-v2-sha256:SHA256(CJ1(P_review_v2))
~~~

Validation requires:

~~~text
reviewed_field_count == 77
reviewed_field_names == exact declared 77-name array
reviewed_field_name_root == recomputed name-array root
reviewed_act_payload == exact P_act_v2 bytes and structure
reviewed_payload_digest == canonical_act_digest
canonical_act_identity == recomputed act identity
canonical_act_digest == recomputed act digest
reviewed_semantic_root == recomputed semantic root
~~~

`reviewed_field_name_root` alone is insufficient because it commits only field
names. Revision 2 retains it as an audit inventory and supplements it with the
entire nested act payload, its digest, and the semantic root. Omitting,
aliasing, renesting, normalizing, hiding, or changing any value changes
`P_review_v2` and its pair.

CJ1 is the sole review serialization. The Human-readable view is the exact
UTF-8 decoding of `CJ1(P_review_v2)` within a visibly delimited byte-view
region. A user interface may add decoration outside that region, but may not
pretty-print, reorder, unescape, localize, abbreviate, link-substitute,
truncate, collapse false flags, or relabel content. The Human confirmation and
later authentication bind the review pair, not decoration. This is a
mechanical view of the one serialization, not a second serialization path.

The uniqueness reductions are:

~~~text
one finalized P_act_v2
-> one exact 77-name array
-> one exact nested reviewed_act_payload
-> one semantic root
-> one CJ1(P_review_v2)
-> one review pair

one valid P_review_v2
-> one exact nested P_act_v2
-> one recomputed act identity/digest pair
~~~

## B02 — Proposal-Level Identity and G76 Compatibility

G76 generic identity semantics are reused, but G76 does not authorize any new
family. Revision 2 defines exact proposal schemas and sources and leaves every
new family inactive pending later independent assessment, external source
facts, and separate lawful authorization.

| Identity or commitment | Normative source | Formula/class | G76 status |
|---|---|---|---|
| HFD-04 protocol source | exact finalized HFD-04 file bytes | fixed report identity plus `sha256:SHA256(file bytes)` | immutable predecessor pair; not content-derived artifact identity |
| HFD-02/HFD-03 references | committed exact file bytes | fixed identities plus authenticated SHA-256 | lawful finalized predecessor pairs |
| Candidate common base | 75-field `B_act_v2` | digest only, `sha256:SHA256(CJ1(B_act_v2))` | commitment scalar; no artifact family |
| Candidate H input reference manifest | exact closed manifest below | `human-founder-candidate-h-input-manifest-v2-sha256:SHA256(CJ1(P_manifest))` plus plain digest | proposed new external compatibility family; not active |
| Human Founder act V2 | exact `P_act_v2` | `human-founder-constituent-act-v2-sha256` plus plain digest | proposed new external message family; not active |
| review projection V2 | exact `P_review_v2` | `human-founder-act-review-v2-sha256` plus plain digest | proposed new deterministic review family; not active |
| authentication commitment V2 | exact closed commitment | `human-founder-auth-commitment-v2-sha256` plus plain digest | proposed new message family; not an authentication result |
| Candidate H HumanDecision/Finality | frozen Candidate H schemas and prefixes | exact retained G77 formulas | direct reuse; no new version or namespace |
| exhaustion evidence V2 | exact derived payload below | `human-founder-exhaustion-v2-sha256` plus plain digest | proposed new pre-BEGIN evidence family; not active |

Every proposed HFD family uses exact CJ1, excludes only its own derived
identity/digest fields, binds exact type/version/source and finalized
predecessors, and fails on unknown content. Its producing source is either the
genuine external Human Founder capacity pair or the exact external
finality/custody domain pair already carried in the payload. No repository
owner, Governance actor, validator, Replay reader, or hash function becomes a
producing authority.

The complete identity order is:

~~~text
finalized HFD/G77 protocol lineage
+ independently prior external evidence
+ frozen Candidate H predecessor pairs
-> Candidate H input reference manifest
-> common act base
-> one selected act pair
-> one review pair
-> one authentication commitment pair
-> source-defined authentication evidence pair
-> retained Candidate H HumanDecision pair
-> retained Candidate H HumanFinality pair
-> retained decision DispositionEvidence pair
-> derived exhaustion evidence pair
-> frozen Candidate H ProofSet/Certification/Transition chain
-> existing root/terminal/Replay successors
~~~

Every arrow points to a successor. No node includes its own pair or a later
node. Prefix/type/version provide domain separation. Replay reconstructs only
finalized exact bytes and does not activate the proposed families.

## Candidate H Input Reference Manifest V2

To avoid an inference adapter, Revision 2 adds one minimum external reference
manifest. Its exact semantic payload is:

~~~text
manifest_artifact_type = HUMAN_FOUNDER_CANDIDATE_H_INPUT_REFERENCE_MANIFEST
manifest_artifact_version = V2
protocol_source_identity
protocol_source_digest
producing_external_capacity_identity
producing_external_capacity_digest
external_premise_identity
external_premise_digest
source_commitment_identity
source_commitment_digest
instrument_commitment_v3_identity
instrument_commitment_v3_digest
universe_identity
universe_digest
census_identity
census_digest
source_evidence_identity
source_evidence_digest
recognition_proof_identity
recognition_proof_digest
normative_successor_payload_identity
normative_successor_payload_digest
target_v5_identity
target_v5_digest
instrument_v4_identity
instrument_v4_digest
authority_scope_identity
authority_scope_digest
validation_schema_identity
validation_schema_digest
target_disposition_domain_identity
target_disposition_domain_digest
target_disposition_slot_identity
target_disposition_epoch
human_finality_domain_identity
human_finality_domain_digest
human_decision_slot_identity
human_decision_epoch
candidate_h_contract_lineage = [
  exact G77-42, G77-52, G77-53, G77-62, G77-63, G77-64, G77-65 pairs
]
candidate_h_contract_lineage_count = 7
candidate_h_contract_lineage_root
mapping_contract = DIRECT_RETAINED_PAIR_OR_EXACT_PROJECTION_V2
metadata = {}
~~~

Each lineage row has exactly
`{generation, artifact_identity, artifact_digest}` and no other field. The
array order is exactly ascending generation number as displayed. Its root is
`sha256:SHA256(CJ1(candidate_h_contract_lineage))`. Every artifact pair must
validate under its exact retained Candidate H type, version, owner, schema,
identity, digest, predecessor, and presence rules before manifest construction.

Let `P_manifest` be the exact payload above. Then:

~~~text
candidate_h_input_reference_manifest_digest =
  sha256:SHA256(CJ1(P_manifest))

candidate_h_input_reference_manifest_identity =
  human-founder-candidate-h-input-manifest-v2-sha256:
  SHA256(CJ1(P_manifest))
~~~

The manifest neither transforms nor authorizes Candidate H artifacts. It
commits the exact pre-Human Candidate H pair set that the act and review bind.
More than one valid manifest for the same external capacity/Target is
ambiguity and makes the act ineligible; a validator cannot choose one.

## Authentication Commitment V2

The exact semantic commitment is:

~~~text
authentication_commitment_type =
  HUMAN_FOUNDER_EXTERNAL_CONSTITUENT_ACT_AUTHENTICATION_COMMITMENT
authentication_commitment_version = V2
authentication_domain_identity
authentication_domain_digest
canonical_act_identity
canonical_act_digest
review_projection_identity
review_projection_digest
candidate_common_base_digest
candidate_h_input_reference_manifest_identity
candidate_h_input_reference_manifest_digest
human_founder_external_capacity_reference_identity
human_founder_external_capacity_reference_digest
external_authority_evidence_manifest_identity
external_authority_evidence_manifest_digest
authority_provenance_evidence_identity
authority_provenance_evidence_digest
authority_competence_evidence_identity
authority_competence_evidence_digest
human_finality_domain_identity
human_finality_domain_digest
human_finality_slot_identity
human_finality_epoch
finality_sequence = 1
permanent_exhaustion_required = true
~~~

Let `P_auth_v2` be that exact CJ1 object:

~~~text
authentication_commitment_digest = sha256:SHA256(CJ1(P_auth_v2))
authentication_commitment_identity =
  human-founder-auth-commitment-v2-sha256:SHA256(CJ1(P_auth_v2))
~~~

The genuine external contract must authenticate this exact commitment pair
and define algorithm, authenticator/key, trust anchor, encoding, verification,
domain separation, and bytes-versus-digest input. Revision 2 selects none.
Authentication proves exact-source/exact-content authentication only; it does
not prove external constituent competence or create authority.

## B03 — Finality, Exhaustion, and Crash Closure

Revision 2 does not create a second finality family. The future external
mechanism must emit the exact retained Candidate H
`ExternalConstituentHumanDecisionFinalityEvidenceV1` pair. Its FINAL slot,
operation, non-equivocation proof, CAS/read-back, finalized time, and
equivocation status retain the frozen schema and identity formulas.

One additional HFD pre-BEGIN evidence record is necessary because Candidate H
does not itself prove that the external Founder capacity was permanently
exhausted before ingestion. Its exact semantic payload is:

~~~text
exhaustion_artifact_type = HUMAN_FOUNDER_ONE_SHOT_EXHAUSTION_EVIDENCE
exhaustion_artifact_version = V2
protocol_source_identity
protocol_source_digest
canonical_act_identity
canonical_act_digest
review_projection_identity
review_projection_digest
authentication_commitment_identity
authentication_commitment_digest
authentication_evidence_identity
authentication_evidence_digest
candidate_h_input_reference_manifest_identity
candidate_h_input_reference_manifest_digest
candidate_h_human_decision_identity
candidate_h_human_decision_digest
candidate_h_human_finality_identity
candidate_h_human_finality_digest
human_finality_domain_identity
human_finality_domain_digest
human_finality_slot_identity
human_finality_epoch
finality_sequence = 1
finality_operation_identity
finality_operation_digest
non_equivocation_proof_identity
non_equivocation_proof_digest
finality_domain_cas_identity
finality_domain_cas_digest
read_back_finality_slot_digest
final_disposition
founding_target_identity
founding_target_digest
human_founder_external_capacity_reference_identity
human_founder_external_capacity_reference_digest
authoritative_disposition_count = 1
authority_status = PERMANENTLY_EXHAUSTED
delegation_permitted = false
transfer_permitted = false
reset_permitted = false
reissue_permitted = false
recurrence_permitted = false
revival_permitted = false
post_founding_special_authority = false
ordinary_post_founding_governance_only = true
exhausted_at
metadata = {}
~~~

All finality fields copy exact bytes from the resolved retained HumanFinality
artifact. `final_disposition` equals both its final decision and the act
disposition. `exhausted_at` equals exact HumanFinality `finalized_at`; no new
clock exists.

Let `P_exhaust_v2` be the exact object above:

~~~text
exhaustion_evidence_digest = sha256:SHA256(CJ1(P_exhaust_v2))
exhaustion_evidence_identity =
  human-founder-exhaustion-v2-sha256:SHA256(CJ1(P_exhaust_v2))
~~~

The semantic state machine is a derived view of retained FINAL evidence plus
the exhaustion pair; it is not a new mutable SAPIANTA State:

~~~text
OPEN
  -> retained external finality operation
  -> FINAL_PENDING_EXHAUSTION

FINAL_PENDING_EXHAUSTION
  -> derive exact P_exhaust_v2 from finalized predecessors
  -> persist/read exact exhaustion pair
  -> FINAL_EXHAUSTED

OPEN + conflicting final candidates
  -> EQUIVOCATED_INVALID

FINAL_PENDING_EXHAUSTION has no edge to OPEN
FINAL_EXHAUSTED has no outgoing founding-authority edge
EQUIVOCATED_INVALID has no outgoing founding-authority edge
~~~

`FINAL_PENDING_EXHAUSTION` already means the Human disposition slot is FINAL
and the one Human authority use is irreversibly consumed. It does not permit
Candidate H ingestion until the deterministic exhaustion record is present,
but it can never authorize a second Human act, signature, choice, or finality
operation. The external mechanism may establish FINAL and exhaustion
atomically or persist the exact forward chain; no implementation primitive is
chosen here.

Crash/retry behavior is exact:

| Boundary | Observation | Required retry result |
|---|---|---|
| before finality | OPEN or no finality result | no act effect; repeat only the same prepared candidate review, never infer a choice |
| during finality operation | exact OPEN, FINAL, or external equivocation result | read external slot; do not use arrival/repository order |
| FINAL persisted, exhaustion not observed | exact HumanFinality pair and FINAL read-back | derive identical `P_exhaust_v2`; no Human/signature/authority reuse |
| exhaustion persisted, read-back interrupted | exact content-derived exhaustion pair | recompute and return identical pair |
| retry after FINAL | same HumanFinality pair | same exhaustion bytes and identity |
| retry after exhaustion | same finalized predecessors | return identical exhaustion evidence |
| conflicting retry | different act/review/auth/finality/content | reject; terminal equivocation or identity conflict, no winner choice |
| identical Replay | exact immutable pairs | read-only identical reconstruction |
| Candidate H retry after ABANDONED | same founding event, original HumanDecision/Finality/Disposition/exhaustion | retained retry chain only; no Human or finality recreation |

Idempotency follows because every exhaustion field is a constant or exact
copy from finalized predecessor pairs. Same predecessors yield one CJ1 object,
one digest, and one identity. Different content under the same identity fails
closed. Repository, machine, clock, CAS arrival, or Replay cannot choose a
value.

## B04 — Complete HFD to Frozen Candidate H Mapping

Revision 2 uses two mapping modes only:

- `DIRECT_PAIR`: the manifest supplies the exact existing Candidate H artifact
  pair; transformation is identity-preserving.
- `EXACT_PROJECTION`: the exact existing Candidate H artifact is constructed
  from enumerated finalized HFD/manifest fields under the retained Candidate H
  schema and identity formula; no field is inferred or defaulted.

The complete pre-BEGIN mapping is:

| Frozen Candidate H input | HFD source object/field | Binding/transformation | Validation and missing-input result |
|---|---|---|---|
| PremiseEvidenceV1 | manifest `external_premise` pair | `DIRECT_PAIR` | validate exact type/source/provenance/signature; missing -> no Universe |
| SourceCommitmentV1 | manifest `source_commitment` pair | `DIRECT_PAIR` | exact Premise/Target/scope/domain/status/signature equality; missing -> no source candidate |
| InstrumentCommitmentV3 | manifest `instrument_commitment_v3` pair | `DIRECT_PAIR` | exact retained V3/G77/Target/domain/owner/status equality; missing -> no Instrument |
| AdmissibilityUniverseV1 | manifest `universe` pair | `DIRECT_PAIR` | exact one Universe, closure roots, status, domains; missing/second -> no admissible Universe |
| CandidateCensusV1 | manifest `census` pair | `DIRECT_PAIR` | exact arrays/roots and eligible counts one/one; missing -> incomplete census |
| AuthoritySourceEvidenceV1 | manifest `source_evidence` pair | `DIRECT_PAIR` | must equal HFD external capacity, authority/provenance/authentication fields; missing -> no eligible source |
| AuthorityRecognitionProofV1 | manifest `recognition_proof` pair | `DIRECT_PAIR` | exact source/provenance/custody/signature/scope/anti-self-authorization results; missing -> no recognition |
| NormativeSuccessorPayloadV1 | manifest `normative_successor_payload` pair | `DIRECT_PAIR` | exact frozen bytes and root/status/topology content; missing -> no exact successor |
| InitialAdoptionTargetV5 | manifest `target_v5` pair and act `founding_target` pair | `DIRECT_PAIR`, pairs must be identical | validate exact origin/current root and G77 lineage; mismatch -> target substitution reject |
| OneShotFoundingInstrumentV4 | manifest `instrument_v4` pair | `DIRECT_PAIR` | exact commitment/source/recognition/Target/domain/scope/status equality; missing -> no Instrument |
| HumanFirstAdoptionDecisionV1 | act, review, authentication evidence, manifest | `EXACT_PROJECTION` below | any absent/mismatched field -> no HumanDecision |
| HumanDecisionFinalityEvidenceV1 | external finality result | exact retained artifact is the HFD finality evidence; `DIRECT_PAIR` | missing/non-FINAL/equivocation -> no authoritative disposition |
| decision DispositionEvidence | manifest target-disposition domain plus exact HumanDecision/HumanFinality | retained external-domain artifact; `DIRECT_PAIR` after domain CAS/read-back | missing/refusal/invalidation handled by retained row; no ADOPT BEGIN without DECISION_BOUND_ADOPT |
| exhaustion evidence | HFD derived exhaustion pair | pre-ingestion gate, not a new Candidate H field | missing -> package rejected before Candidate H validation |
| current root pointer/root/State | TargetV5 origin and exact validation-time current read-back | retained Candidate H predecessor resolution, not repository default | stale/missing/different -> P015 false; no BEGIN |
| initial consuming disposition | canonical null under retained INITIAL_BEGIN row | exact retained presence rule, not default | non-null -> invalid initial attempt |
| retry consuming disposition | prior exact same-event CONSUMING pair | retained `RETRY_AFTER_ABANDONED` predecessor | missing/wrong event -> retry ineligible |
| predecessor attempt/read-back/ABANDONED commitment | null for initial; exact immediate terminal chain for retry | retained presence rows | inference or non-immediate predecessor -> ineligible |
| founding event/attempt identities | exact retained formulas over mapped pairs and current/terminal predecessors | `EXACT_PROJECTION` by frozen formulas | formula mismatch -> no ProofSet |
| ProofSetV3 | all mapped pairs plus exact current/attempt facts | existing Candidate H deterministic derivation | any of 20 predicates false -> INELIGIBLE |
| CertificationV3 | exact eligible ProofSetV3 | existing deterministic derivation; time from G77-64 rule | missing/ineligible -> no Transition |
| TransitionV3 | exact Certification/ProofSet/mapped pairs | existing deterministic derivation | missing or wrong presence mode -> no BEGIN/root path |

The exact HumanDecision projection is:

~~~text
universe pair = manifest universe pair
source pair = manifest source_evidence pair
instrument pair = manifest instrument_v4 pair
target pair = manifest target_v5 pair = act founding_target pair
human_authority_identity = exact retained HUMAN_AUTHORITY custody identity
human_actor_identity = exact Human identity resolved by external capacity evidence
human_finality_domain pair = act/manifest exact equal pair
human_decision_slot_identity = act finality slot = manifest decision slot
human_decision_epoch = act finality epoch = manifest decision epoch
human_decision_sequence = 1
decision = act disposition
supersession_permitted = false
predecessor_finality_slot_status = OPEN
human_confirmation pair = review projection pair
human_signature_scheme = exact external authentication evidence scheme
human_signature_key_identity = exact external authentication evidence key
human_signature = exact external authentication evidence signature
decision_effective_at = act issued_at
producing_owner = HUMAN_AUTHORITY
~~~

The existing `HUMAN_AUTHORITY` role is used only as the frozen Candidate H
HumanDecision/Finality custody and producing owner required by G77-42. It does
not supply the external Human identity, constituent authority, provenance,
competence, disposition, authentication scheme, or signature. Absence of
genuine external evidence cannot be repaired by Human Authority. This is
custody reuse, not Human Authority substitution.

Applying the retained Candidate H common envelope and formulas to that exact
projection yields exactly one HumanDecision pair. The external finality
mechanism must then emit the exact retained HumanFinality pair over that
decision; no HFD-specific finality adapter exists.

Therefore:

~~~text
one finalized valid HFD package
+ one exact compatibility manifest
+ one valid source-defined authentication result
+ one FINAL retained HumanFinality result
+ one exhaustion pair
-> one exact frozen Candidate H input set

any missing, invalid, conflicting, stale, revoked, substituted,
non-current, or unmapped value
-> no Candidate H input set
-> no eligible ProofSet
-> no Certification/Transition
-> no BEGIN
~~~

No Candidate H field is populated from prose, default, repository state, local
clock, machine order, HIC/CHE interpretation, Human Authority substitution, or
inference. No Candidate H type, version, owner, namespace, predicate, presence
row, or schema changes.

## Complete Authority DAG

~~~text
independently prior Human Founder identity/provenance/competence
-> exact external Premise/Universe/Source/Instrument evidence
-> two exact common-base disposition candidates
-> Human review of both canonical review byte sequences
-> Human selects one exact act
-> source-defined authentication of act/review/manifest commitment
-> retained HUMAN_AUTHORITY custody projects exact HumanDecision bytes
-> external one-use domain emits retained FINAL HumanFinality evidence
-> deterministic permanent exhaustion evidence
-> external target domain emits retained decision DispositionEvidence
-> Candidate H predicate validation
-> existing root custody only after separately lawful authorization
~~~

Authority separation is exact:

- the external Founder supplies identity, authority, competence, and choice;
- authentication proves exact source/content only;
- `HUMAN_AUTHORITY` supplies retained custody/artifact production only;
- HIC/CHE transport only after finalization;
- Certification evaluates predicates only;
- root custody performs only the retained mechanical transition;
- Replay reconstructs read-only; and
- CRO remains passive.

No downstream node creates an upstream fact. No signature, hash, repository
owner, Human Authority artifact, Governance result, Certification, Candidate H
validation, CLIA result, or root operation creates constituent competence.

## Cross-Cutting Attack and Compatibility Review

| Attack | Revision 2 fail-closed result |
|---|---|
| circular identity | reject any predecessor referencing act/review/auth/finality/exhaustion successor |
| hidden free variable | every act/review/manifest field exact and mandatory; source facts must be finalized predecessors |
| producer-selected common field | base digest and byte equality reject resampling or per-candidate changes |
| timestamp nondeterminism | `issued_at` frozen in common base; Candidate Decision copies it; exhaustion copies `finalized_at` |
| off-payload dependency | compatibility manifest and exact pairs bind every required external predecessor |
| second Human decision | FINAL state has no OPEN edge; same act Replay only |
| authority revival | exhaustion and retained terminal states have no outgoing founding-authority edge |
| target substitution | act, manifest, TargetV5, InstrumentV4, HumanDecision, and disposition pairs must be equal |
| disposition substitution | act, review, auth commitment, HumanDecision, HumanFinality, exhaustion, and disposition evidence must agree |
| review substitution | nested exact act plus semantic root and review pair reject |
| authentication substitution | auth commitment directly binds act/review/base/manifest/capacity/authority/finality pairs |
| finality-slot substitution | act, manifest, HumanDecision, HumanFinality, and exhaustion slot/domain/epoch equal |
| topology substitution | exact 1/0/0 act fields plus frozen Candidate H topology predicates |
| Candidate H input ambiguity | one manifest only; direct pairs or exact projection; any second/mismatch rejects |
| second production path | no owner, route, ingress, root, or runtime path added |

The four closure models are mutually compatible because review contains the
exact act; the act contains the manifest and base commitment; authentication
binds act/review/manifest; finality binds the projected existing HumanDecision;
exhaustion binds all of them; and Candidate H consumes only existing exact
artifacts referenced or projected by those predecessors.

## Minimality and Machinery Classification

| Revision 2 item | Classification | Reason |
|---|---|---|
| protocol/predecessor source pairs | `REQUIRED_TO_CLOSE_HFD_03_BLOCKER` | removes unpaired protocol ambiguity |
| common-base digest | `REQUIRED_TO_CLOSE_HFD_03_BLOCKER` | proves candidates differ only by disposition |
| nested full review payload and semantic root | `REQUIRED_TO_CLOSE_HFD_03_BLOCKER` | field-name root alone cannot prove values |
| Candidate H input reference manifest | `REQUIRED_TO_CLOSE_HFD_03_BLOCKER` | closes all direct frozen-input references without an adapter |
| authentication commitment identity | `REQUIRED_TO_CLOSE_HFD_03_BLOCKER` | exact successor binding and Replay identity |
| exhaustion evidence V2 | `REQUIRED_TO_CLOSE_HFD_03_BLOCKER` | closes FINAL-before-exhaustion crash and pre-BEGIN exhaustion proof |
| new mutable finality State | `AVOIDABLE_CONSTITUTIONAL_MACHINERY` | derived view over retained FINAL plus exhaustion pair suffices; not introduced |
| new Candidate H family/version/field | `AVOIDABLE_CONSTITUTIONAL_MACHINERY` | direct retained pairs/projection suffice; not introduced |
| new HIC/CHE/CLIA route | `AVOIDABLE_CONSTITUTIONAL_MACHINERY` | existing boundaries suffice; not introduced |
| new clock, lock, CAS, key, algorithm, signer, owner | `AVOIDABLE_CONSTITUTIONAL_MACHINERY` | external mechanism and retained custody supply semantics; not introduced |

All proposed HFD families are inactive semantic contracts. None is a runtime
constructor, active owner, persistence service, or execution capability.

## Reuse Impact Assessment

1. **Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?**

   Ponovno se uporabijo G48 struktura, G76 identitetna/digest in DAG pravila,
   G69-07 nespremenljiva Human vsebina, G69-18 read-only Replay, Candidate H
   CJ1 ter obstoječe Premise, Universe, Census, Source, Instrument,
   HumanDecision, HumanFinality, Disposition, ProofSet, Certification in
   Transition družine. Nobena ponovna uporaba ne prenese zunanje oblasti.

2. **Katere nove zmogljivosti (če sploh) nastanejo?**

   Nobena aktivna zmogljivost ne nastane. Predlagani so samo V2 act/review,
   input-reference manifest, authentication commitment in exhaustion evidence
   kot neaktivne semantične pogodbe za razrešitev B01–B04.

3. **Ali katera obstoječa zmogljivost postane nedosegljiva?**

   Ne. Aktivne zmogljivosti ostanejo nespremenjene. Candidate H ostane
   nedosegljiv brez vseh veljavnih zunanjih dokazov, ločene avtorizacije in
   poznejše izvedbe.

4. **Ali implementacija ustvarja vzporedni tok?**

   Ne. Implementacije ni. Preslikava uporablja samo obstoječe Candidate H
   družine in obstoječo enotno HIC/CHE pot po zunanji finalizaciji.

5. **Ali zmanjšuje ali povečuje število produkcijskih poti?**

   Ne zmanjšuje in ne povečuje. Produkcijske poti ostanejo 1, vzporedne poti
   0 in trajne ustanovitvene poti 0.

# 2. Code Evidence

## Public API

No API, model, serializer, signer, verifier, key provider, State, pointer, CAS,
route, command, validator, or runtime schema is added or modified. Every V2
name is a proposal-only semantic contract.

## Orchestration Entry Point

No orchestration entry point is created. The proposed future sequence remains
external act/review/authentication/finality/exhaustion first, then exact
existing Candidate H artifacts through the retained HIC/CHE boundary only
after separate authorization. HFD-04 itself is never ingested as an act.

## Semantic Reductions

### Human review

~~~text
one P_act_v2
-> one nested P_review_v2
-> one CJ1 review byte sequence
-> one review pair
~~~

### Identity

~~~text
finalized predecessors
-> manifest -> base -> act -> review -> auth -> finality -> exhaustion
-> existing Candidate H chain
~~~

### Finality and exhaustion

~~~text
OPEN -> FINAL_PENDING_EXHAUSTION -> FINAL_EXHAUSTED

no reverse edge
no second Human use
~~~

### Candidate H

~~~text
valid complete HFD package
-> direct retained pairs + exact HumanDecision projection
-> existing Candidate H input set

otherwise -> no BEGIN
~~~

## Public Validators

No validator is implemented or authorized. A future validator must reject:

- a P_act field count other than 77 or any unknown/omitted/half field;
- candidates with different common-base bytes or digest;
- a review that does not contain the exact nested act and semantic root;
- any display other than the exact CJ1 UTF-8 byte view;
- an unapproved namespace or wrong type/version/source/prefix;
- an authentication result not binding the exact V2 commitment pair;
- HumanDecision content not equal to the closed projection;
- finality other than the exact retained FINAL pair;
- exhaustion content not exactly derived from finality predecessors;
- a second Human act, signature, disposition, target, slot, epoch, or authority
  use;
- any inferred/default/local-clock/repository-order Candidate H input;
- any mapping that changes a Candidate H schema, owner, version, or identity;
- missing exhaustion before Candidate H validation; and
- topology other than `1 / 0 / 0`.

## Canonical Data Models

| Proposed/reused model | Exact role | Status |
|---|---|---|
| `HumanFounderExternalConstituentActPayloadV2` | exact 77-field external act message | proposed inactive |
| `HumanFounderActReviewProjectionV2` | one exact nested Human review object | proposed inactive |
| `HumanFounderCandidateHInputReferenceManifestV2` | direct frozen-input pair commitment | proposed inactive |
| `HumanFounderAuthenticationCommitmentV2` | exact semantic authentication message | proposed inactive |
| `HumanFounderOneShotExhaustionEvidenceV2` | deterministic permanent exhaustion proof | proposed inactive |
| Candidate H retained families | exact consumer artifacts | unchanged inactive converged design |
| Replay/CRO | read-only reconstruction/passive observation | unchanged |

## Deterministic Algorithms

1. Authenticate HFD-01 through HFD-03 and exact G77 lineage.
2. Resolve one exact compatibility manifest and validate every retained pair.
3. Freeze one 75-field common base and its digest.
4. Construct exactly two candidates differing only in disposition.
5. CJ1-encode each exact 77-field act and derive its pair.
6. Embed each entire act in its exact review object and derive the review pair.
7. Permit the genuine Human Founder to select one; infer nothing.
8. Build the exact authentication commitment and validate only a
   source-defined external mechanism.
9. Project one existing Candidate H HumanDecision under retained custody.
10. Validate the retained FINAL HumanFinality and external disposition.
11. Derive one exhaustion object from finalized predecessor bytes.
12. Map direct retained pairs and exact projections into Candidate H.
13. Permit ProofSet/Certification/Transition only under frozen rules.
14. Replay immutable evidence read-only without choice, repair, or revival.

## Responsibility Boundaries

| Responsibility | Exact source/owner | Negative boundary |
|---|---|---|
| define Revision 2 proposal | HFD-04 record | no act, authority, or activation |
| supply external identity/authority/competence | genuine independently prior Human Founder source | no internal substitute |
| select disposition | genuine Human Founder | no machine or custody choice |
| authenticate | genuine external source-defined mechanism | no competence inference |
| produce Candidate HumanDecision/Finality artifacts | retained `HUMAN_AUTHORITY` custody | no external authority or disposition creation |
| establish finality/exhaustion | external one-use finality/custody domain | no rollback, second act, or revival |
| validate Candidate H | later separately authorized frozen machinery | no missing-field inference or schema change |
| certify | retained Certification owner | predicates only |
| execute root effect | retained root custodian | no semantic/founding choice |
| reconstruct/observe | Replay/CRO | read-only/passive |

## Repository Evidence

Evidence consists of committed HEAD `55e78434`, exact HFD-01 through HFD-03
bytes/blobs/digests, exact G77-42/52/53/62/63/64/65 design lineage, exact
G77-66 through G77-68 handoff lineage, G76 identity rules, and the focused
G69/G70 executable suite.

Repository search found no directly named Candidate H, G76,
external-constituent, or founding executable test module. No test or runtime
code is created to simulate the proposal.

# 3. Constitutional Self-Assessment

## Verified at Proposal Level

- HFD/G77 predecessors are authenticated and unchanged.
- B01 through B04 each have one explicit minimum proposal closure.
- P_act_v2 has exactly 77 fields and one 75-field common base.
- Exactly one CJ1 review object embeds the complete act and semantic root.
- Field-name root is explicitly insufficient alone and is supplemented.
- Every proposed identity has exact source, type/version, schema, formula,
  prefix, and activation boundary.
- The identity and authority DAGs are finite, forward, acyclic, and replayable.
- FINAL immediately consumes the one Human authority use.
- Exhaustion is deterministically derived without a Human, signature, or
  clock retry.
- Candidate H consumes only existing exact families through direct pairs or a
  closed retained-schema projection.
- `HUMAN_AUTHORITY` remains custody only and cannot replace external Founder
  identity, authority, competence, or choice.
- Invalid/incomplete HFD evidence produces no Candidate H BEGIN eligibility.
- No runtime, root, authority, activation, implementation, or production
  effect occurs.
- Topology remains `1 / 0 / 0`.

## Not Verified or Performed

- No independent assessment of HFD-04 exists.
- No proposed HFD V2 family or namespace is active or implemented.
- No Human Founder identity, provenance, competence, disposition, act,
  authentication mechanism, key, signature, finality, exhaustion, or
  Candidate H artifact instance exists.
- No external mechanism has accepted the semantic finality/exhaustion
  contract.
- No schema, serializer, validator, store, CAS, Replay reader, custody adapter,
  or mapping implementation exists.
- No adoption, Ratification, Certification, publication, activation,
  Candidate H instantiation, BEGIN, root mutation, CDP, CLIA validation,
  deployment, or production authority exists.
- Proposal-level blocker disposition cannot serve as execution evidence.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| repository identity | HEAD/tree/parent/subject and clean start | Git review | `PASS` |
| HFD-01 authentication | exact committed blob/SHA-256 | Git/digest review | `PASS` |
| HFD-02 authentication | exact committed blob/SHA-256 | Git/digest review | `PASS` |
| HFD-03 authentication | exact committed blob/SHA-256 | Git/digest review | `PASS` |
| G77-64 through G77-68 | exact SHA-256 values | digest review | `PASS` |
| predecessor preservation | no existing-file changes | Git/digest review | `PASS` |
| B01 disposition | exact nested review/semantic root/display rule | schema review | `ADDRESSED_AT_PROPOSAL_LEVEL` |
| review field count | exact 77-name array and full nested payload | field census | `PASS_PROPOSAL` |
| field-name root sufficiency | retained only with payload/semantic commitment | adversarial review | `PASS_SUPPLEMENTED` |
| B02 disposition | exact sources/formulas/family status | G76 review | `ADDRESSED_AT_PROPOSAL_LEVEL` |
| common base | exact 75-field exclusion formula | identity review | `PASS_PROPOSAL` |
| identity DAG | forward, acyclic, self-excluding | DAG review | `PASS_PROPOSAL` |
| namespace authority | all HFD families explicitly proposed inactive | authority review | `PASS_BOUNDARY` |
| B03 disposition | retained FINAL plus derived exhaustion | crash review | `ADDRESSED_AT_PROPOSAL_LEVEL` |
| FINAL no second choice | no FINAL-to-OPEN edge | state review | `PASS_PROPOSAL` |
| crash after FINAL | identical exhaustion derivation | retry review | `PASS_PROPOSAL` |
| ABANDONED retry | exact same founding event/evidence | lifecycle review | `PASS_REUSED` |
| B04 disposition | complete direct/projection mapping | compatibility review | `ADDRESSED_AT_PROPOSAL_LEVEL` |
| Candidate H schema preservation | no changed type/version/owner/field | diff/schema review | `PASS` |
| Human Authority boundary | custody only; external source facts mandatory | authority review | `PASS_PROPOSAL` |
| missing mapping input | no input set/ProofSet/BEGIN | fail-closed review | `PASS_PROPOSAL` |
| hidden/free values | common base/manifest/exact source rules | adversarial review | `PASS_PROPOSAL` |
| timestamp determinism | source-frozen/copy-only derivations | time review | `PASS_PROPOSAL` |
| substitution attacks | complete cross-object equality rules | adversarial review | `PASS_PROPOSAL` |
| machinery minimality | five necessary proposal contracts; avoided mutable machinery | entropy review | `PASS_PROPOSAL` |
| effect classifications | thirteen exact results all `NO` | scope review | `PASS` |
| topology | 1 to 1 / 0 to 0 / 0 to 0 | count review | `PASS` |
| focused G69/G70 tests | 326 tests | pytest | `PASS` |
| Candidate H/G76 tests | no directly named executable module found | test inventory | `NOT_APPLICABLE_MISSING` |
| G48 structure | exactly six top-level sections and eight Code Evidence subsections | heading review | `PASS` |
| Markdown fences | balanced pairs | structural scan | `PASS` |
| trailing whitespace | zero trailing-whitespace lines | whitespace scan | `PASS` |
| Git whitespace | repository diff | `git diff --check` | `PASS` |
| artifact count | exactly one HFD-04 artifact | status/path review | `PASS` |
| prohibited mutations | no runtime/test/config/root/production change | Git status review | `PASS` |

# 5. Repository Mutation Summary

Modified files:

- added
  `docs/governance/HFD_04_HUMAN_FOUNDER_CONSTITUENT_ACT_CANONICALIZATION_AND_AUTHENTICATION_PROTOCOL_REVISION_2_DETERMINISTIC_CLOSURE_V1.md`
  as the sole HFD-04 proposal artifact.

No existing file changed. HFD-01, HFD-02, HFD-03, G77-64 through G77-68,
and every Candidate H predecessor remain byte-identical.

Unchanged subsystems:

- Constitution, roots, G69/G70/G77, HFD-01 through HFD-03, Candidate H,
  Human Authority runtime, Governance, Certification, CLIA, HIC, CHE, Replay,
  CRO, runtime, tests, configuration, schemas, credentials, keys, providers,
  persistence, release, deployment, routing, workflow, and production state.

Boundary preservation:

- Revision 2 is unassessed proposal content only;
- no Human, disposition, authentication mechanism, key, signature, act,
  finality, exhaustion, adoption, activation, implementation, root, deployment,
  or production authority is selected or created;
- no Candidate H redesign, G77-69, new ingress, or second path is created;
- no active artifact family, namespace, owner, State, transition, or validator
  is created; and
- an independent HFD-04 Constitutional Impact Assessment is the next lawful
  internal boundary before any external mechanism or act package reliance.

Unrelated pre-existing changes:

- None observed. The worktree was clean at HFD-04 start.

# 6. Certification Verdict

HFD_04_HUMAN_FOUNDER_CONSTITUENT_ACT_PROTOCOL_REVISION_2_ESTABLISHED
