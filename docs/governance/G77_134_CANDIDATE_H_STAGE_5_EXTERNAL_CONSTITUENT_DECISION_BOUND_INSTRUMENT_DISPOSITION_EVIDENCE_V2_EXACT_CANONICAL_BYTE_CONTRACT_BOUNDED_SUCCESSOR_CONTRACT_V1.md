# 1. Implementation Summary

Generation: G77-134

Report identity:
`G77_134_CANDIDATE_H_STAGE_5_EXTERNAL_CONSTITUENT_DECISION_BOUND_INSTRUMENT_DISPOSITION_EVIDENCE_V2_EXACT_CANONICAL_BYTE_CONTRACT_BOUNDED_SUCCESSOR_CONTRACT_V1`

Reporting date: 2026-08-11

Contract kind: `BOUNDED_NORMATIVE_SUCCESSOR_CONTRACT`

Constitutional baseline: committed G77-133 HEAD
`42beade90edc7aaac26b6da025007195015a2b54`, tree
`5f1f1568fc35cb5352433765f2a6d0cd15f198cf`, subject
`G77-133 freeze PremiseEvidenceV1 canonical byte contract`.

The initial worktree was clean. Committed G77-133 has SHA-256
`abf98d1f91c4057d9ff3ba1a31065c89d6c8598f04f1c2325bc3b12c24211b1e`.
Committed G77-132 has SHA-256
`abdf64cbba4069826f5a161e33da397611347ecc6dc20114ee03351e5c6ce96d`.
Committed CJ1 has SHA-256
`8442f2c84b4bb95935f6a7c38e3ff12e54a8fd154f17e1bcc0c368831e00f0a3`.
Baseline authentication therefore passed. Group P is committed, closed, and
unchanged.

Controlling evidence: G48-00; G77-34; G77-36; G77-37; G77-42;
G77-44; G77-46; G77-125; G77-127; G77-129; G77-130; G77-131;
G77-132; G77-133; committed CJ1; and the G77-134 mandate.

Authenticated evidence:

| Evidence | SHA-256 |
|---|---|
| G77-134 mandate | `2d610859583e68eee339156fe07e278e42fe51401fda524742e6f367d96f90bf` |
| G48-00 | `16508d1a77c4b3f07d37861e74d85f77896be16da01ca26cbc07a658ddf2c0eb` |
| G77-34 | `f1282ce92246fafa8cae593dd2c9c117ebd18064e28602357793a775a3938db7` |
| G77-36 | `5533ec8e597e0767f869daec8118ee3dec6c77af56b4d7c71bdc2d44cfdaba4a` |
| G77-37 | `4ecd74ca986e56490bd72bd26d28ef01777be5780fe8596fcae992fbc6d59add` |
| G77-42 | `b379cb057282aaf7d10c6e6e3f8a55053a630b19a0a0ad80e8159a0222b316a6` |
| G77-44 | `03026b9ff5df38e05ffe08e0d834d0ac83d1b04efc3681f6ea2aff4165801c0a` |
| G77-46 | `cc8d2cc171ae05efc54fdbf05261cd591012a0ff9d87270ab0bc75565c3564ed` |
| G77-125 | `78d3f10b0a8082415e9b0232199e1fa3668a7fe535b8ea72b20ca7266ba5a927` |
| G77-127 | `5c4361e50aaa86a04b9ad3c009a7456b8effd74818d52edad6a314c6518d4c88` |
| G77-129 | `abeed0ce1992616b9e2e388ff9341d180af89aa25d9935fc484375baf8291eab` |
| G77-130 | `0cb299738f3eb8e927ac67fc2e1f767c0245af93a8e346162b0cef5841d40f9e` |
| G77-131 | `dfa6835f7b17c678b6937958c2b941cf0a7c4e7d067377c5538bf24da7dc38f8` |
| G77-132 | `abdf64cbba4069826f5a161e33da397611347ecc6dc20114ee03351e5c6ce96d` |
| G77-133 / Group P | `abf98d1f91c4057d9ff3ba1a31065c89d6c8598f04f1c2325bc3b12c24211b1e` |
| committed CJ1 | `8442f2c84b4bb95935f6a7c38e3ff12e54a8fd154f17e1bcc0c368831e00f0a3` |

Objective: close Group D only by freezing one exact canonical-byte
representation for the G77-42
`ExternalConstituentOneShotInstrumentDispositionEvidenceV2`
`ADOPTION_DECISION_BOUND` / `DECISION_BOUND_ADOPT` predecessor branch.

Normative result:

```text
artifact_type = ExternalConstituentOneShotInstrumentDispositionEvidenceV2
artifact_version = V2
contract_version = G77_134_EXTERNAL_CONSTITUENT_DECISION_BOUND_INSTRUMENT_DISPOSITION_EVIDENCE_V2_EXACT_CANONICAL_BYTE_CONTRACT_V1
disposition_kind = ADOPTION_DECISION_BOUND
predecessor_slot_status = UNUSED
slot_status = DECISION_BOUND_ADOPT
identity_prefix = founding-disposition-v2
idempotency_prefix = founding-disposition-idem-v2
producing_owner = resolved external Universe custody owner
reissue_permitted = false
reset_permitted = false
metadata = {}
```

This contract authenticates one historical predecessor representation only.
It does not create disposition authority, select a target slot, establish an
owner, create currentness, advance a pointer, perform consumption or BEGIN,
or add a state transition.

Group P remains closed. Group D is closed by this successor contract. Groups
S and R remain required. Stage-5 implementation remains unauthorized.

# 2. Code Evidence

## Public API

No public API is created or changed. A future separately authorized
implementation can reuse the existing immutable and current-slot read shapes:

```python
def read_immutable(
    self,
    model_type: type[FrozenCanonicalModel],
    address: ArtifactAddress,
    *,
    owner_bindings: Mapping[str, str] | None = None,
) -> tuple[FrozenCanonicalModel, ImmutableReadBack]:

def read_slot(self, owner: str, slot_identity: str, slot_epoch: object) -> SlotReadBack:
```

Canonical validation uses the immutable surface. The external domain's
existing current-slot read-back establishes currentness. No reader, registry,
scan, resolver, persistence family, or pointer API is created.

## Orchestration Entry Point

The existing forward-only branch remains:

```text
authenticated Universe/Census/Source/Instrument/Target
+ exact HumanDecision/HumanFinality
+ external target slot predecessor UNUSED
-> external Universe custody domain CAS
-> ADOPTION_DECISION_BOUND disposition
-> exact read-back DECISION_BOUND_ADOPT
-> later ProofSet/Certification/Transition/Fence remain absent here
-> separately authorized future BEGIN may compare this exact predecessor
```

The target pair must equal the already authenticated Candidate H target. The
`target_disposition_domain_identity` must equal the domain bound by the
authenticated Universe and Instrument. `producing_owner` must equal the
resolved external Universe custody owner. The exact external CAS/read-back,
not canonical validity or caller supply, makes the slot State authoritative.

## Semantic Reductions

### Exact family and branch constants

| Property | Exact value/rule |
|---|---|
| artifact type | `ExternalConstituentOneShotInstrumentDispositionEvidenceV2` |
| artifact version | `V2` |
| contract version | `G77_134_EXTERNAL_CONSTITUENT_DECISION_BOUND_INSTRUMENT_DISPOSITION_EVIDENCE_V2_EXACT_CANONICAL_BYTE_CONTRACT_V1` |
| disposition kind | `ADOPTION_DECISION_BOUND` |
| predecessor slot status | `UNUSED` |
| installed/read-back slot status | `DECISION_BOUND_ADOPT` |
| identity prefix | `founding-disposition-v2` |
| idempotency prefix | `founding-disposition-idem-v2` |
| producing owner | resolved external Universe custody owner |
| reissue/reset | exact boolean `false` / `false` |
| metadata | exact empty object `{}` |

The contract token is identity-relevant but non-authoritative. The branch is
the sole G77-42 edge `UNUSED -> DECISION_BOUND_ADOPT`; it binds the finalized
Human choice but does not confer consumption or root-effect eligibility.

### Complete declaration order

The exact declaration order is the G77-42 common envelope followed by the
complete 42-field disposition row:

```text
01 artifact_type
02 artifact_version
03 artifact_identity
04 artifact_digest
05 contract_version
06 idempotency_identity
07 producing_owner
08 metadata
09 universe_identity
10 universe_digest
11 census_identity
12 census_digest
13 source_evidence_identity
14 source_evidence_digest
15 instrument_identity
16 instrument_digest
17 target_identity
18 target_digest
19 predecessor_disposition_state_identity
20 predecessor_disposition_state_digest
21 predecessor_slot_status
22 human_decision_identity
23 human_decision_digest
24 human_finality_identity
25 human_finality_digest
26 proof_set_identity
27 proof_set_digest
28 certification_identity
29 certification_digest
30 transition_identity
31 transition_digest
32 consumption_fence_identity
33 consumption_fence_digest
34 reserved_successor_root_generation
35 disposition_kind
36 invalidation_reason_code
37 invalidation_proof_identity
38 invalidation_proof_digest
39 committed_successor_root_identity
40 committed_successor_root_digest
41 root_cas_identity
42 root_cas_digest
43 target_disposition_domain_identity
44 disposition_cas_identity
45 disposition_cas_digest
46 read_back_disposition_state_digest
47 linearized_at
48 slot_status
49 reissue_permitted
50 reset_permitted
```

### Exact CJ1 wire order

CJ1 key-sorts the full artifact by unsigned UTF-8 key bytes:

```text
01 artifact_digest
02 artifact_identity
03 artifact_type
04 artifact_version
05 census_digest
06 census_identity
07 certification_digest
08 certification_identity
09 committed_successor_root_digest
10 committed_successor_root_identity
11 consumption_fence_digest
12 consumption_fence_identity
13 contract_version
14 disposition_cas_digest
15 disposition_cas_identity
16 disposition_kind
17 human_decision_digest
18 human_decision_identity
19 human_finality_digest
20 human_finality_identity
21 idempotency_identity
22 instrument_digest
23 instrument_identity
24 invalidation_proof_digest
25 invalidation_proof_identity
26 invalidation_reason_code
27 linearized_at
28 metadata
29 predecessor_disposition_state_digest
30 predecessor_disposition_state_identity
31 predecessor_slot_status
32 producing_owner
33 proof_set_digest
34 proof_set_identity
35 read_back_disposition_state_digest
36 reissue_permitted
37 reserved_successor_root_generation
38 reset_permitted
39 root_cas_digest
40 root_cas_identity
41 slot_status
42 source_evidence_digest
43 source_evidence_identity
44 target_digest
45 target_disposition_domain_identity
46 target_identity
47 transition_digest
48 transition_identity
49 universe_digest
50 universe_identity
```

Declaration order never creates alternate bytes; CJ1 wire order controls.

### Complete semantic field set and branch nullability

The semantic field set is exactly the 42 fields numbered 09-50 in the
declaration order. Every field is present. Exactly these 16 fields are
canonical null for `ADOPTION_DECISION_BOUND`:

```text
proof_set_identity
proof_set_digest
certification_identity
certification_digest
transition_identity
transition_digest
consumption_fence_identity
consumption_fence_digest
reserved_successor_root_generation
invalidation_reason_code
invalidation_proof_identity
invalidation_proof_digest
committed_successor_root_identity
committed_successor_root_digest
root_cas_identity
root_cas_digest
```

Every other envelope and semantic field is mandatory and non-null. A
null-required field must still be present with the JSON value `null`. Omitting
it, supplying a value, supplying one half of a pair, or adding an alternate
field fails closed.

### Exact types, pairs, and bindings

| Field/group | Exact type and rule |
|---|---|
| non-null identity/status/kind/owner/domain fields | non-empty NFC strings in strict UTF-8 |
| every non-null `*_digest` and `artifact_digest` | lowercase `sha256:` plus exactly 64 lowercase hexadecimal characters |
| branch-required absent evidence | canonical JSON null in every exact field listed above |
| `linearized_at` | uppercase UTC RFC3339 `YYYY-MM-DDTHH:MM:SS.ffffffZ` |
| `reissue_permitted`, `reset_permitted` | booleans, both exact `false` |
| `metadata` | exact empty object `{}` |
| all non-null identity/digest pairs | both present and authenticated; no half-pair |
| Universe/custody owner | `producing_owner == resolved Universe.producing_owner` |
| target | exact equality to the authenticated Target pair |
| target disposition domain | exact equality to the domain identity bound by Universe and Instrument |
| predecessor disposition | exact external target-slot State pair read at status `UNUSED` |
| Human pair | exact authenticated Decision and Finality pairs |
| CAS/read-back | exact external-domain operation pair and resulting State digest |

The external CAS/read-back binding and current pointer remain external-domain
facts. G77-134 neither defines a new current pointer nor computes authority
from content identity.

### Non-alias rules

- `ADOPTION_DECISION_BOUND` is not refusal, invalidation, consuming, consumed,
  success, or terminal disposition.
- `DECISION_BOUND_ADOPT` is not `UNUSED`, `CONSUMING`,
  `INVALIDATED_DORMANT`, `REFUSED_DORMANT`, or `CONSUMED_DORMANT`.
- V1, V3, or another family/version cannot alias this V2 branch.
- Present ProofSet, Certification, Transition, Fence, successor-root, root-CAS,
  invalidation evidence, reason, or reserved generation changes the branch and
  is invalid here.
- Missing Human/Finality, target, predecessor, CAS/read-back, Universe,
  Census, Source, or Instrument evidence is invalid.
- Alternate owner, target/domain binding, prefix, token, metadata, field type,
  key order, or bytes is invalid, not a second representation.

## Public Validators

A future independent authorization may admit exactly this branch model/spec
through the existing generic validation path:

```text
artifact_type = ExternalConstituentOneShotInstrumentDispositionEvidenceV2
artifact_version = V2
identity_field = artifact_identity
digest_field = artifact_digest
identity_prefix = founding-disposition-v2
idempotency_prefix = founding-disposition-idem-v2
contract_version = G77_134_EXTERNAL_CONSTITUENT_DECISION_BOUND_INSTRUMENT_DISPOSITION_EVIDENCE_V2_EXACT_CANONICAL_BYTE_CONTRACT_V1
branch = ADOPTION_DECISION_BOUND / UNUSED -> DECISION_BOUND_ADOPT
owner_binding = resolved external Universe custody owner
```

Generic validation checks the closed bytes, exact nullability, constants,
identities, digests, and supplied owner binding. Target/domain equality,
external CAS/read-back authority, currentness, and branch ordering remain
authentication/orchestration/persistence responsibilities. No new validator
family is created.

## Canonical Data Models

### Exact S/P/full projections and formulas

`S_decision_bound_v2` contains exactly `artifact_type`, `artifact_version`,
`contract_version`, `producing_owner`, and all 42 semantic fields, including
all 16 canonical-null fields. It excludes the three identity fields and
metadata.

```text
idempotency_identity =
  cj1_identity(
    "founding-disposition-idem-v2",
    S_decision_bound_v2
  )

P_decision_bound_v2 = S_decision_bound_v2 plus {
  "idempotency_identity": idempotency_identity
}

artifact_identity =
  cj1_identity(
    "founding-disposition-v2",
    P_decision_bound_v2
  )

artifact_digest = cj1_digest(P_decision_bound_v2)

full_artifact = P_decision_bound_v2 plus {
  "artifact_identity": artifact_identity,
  "artifact_digest": artifact_digest,
  "metadata": {}
}
```

`cj1_identity(prefix, value)` is `prefix + ":" + lowercase
SHA256(cj1_encode(value))`. `cj1_digest(value)` is `"sha256:" + lowercase
SHA256(cj1_encode(value))`. No alternate identity algorithm exists.

### Complete canonical test vector

The vector uses repeated hexadecimal digits for transparent independent
reconstruction. All pairs and CAS values are canonicalization placeholders;
the vector does not perform a Human act, external CAS, disposition, BEGIN,
consumption, root mutation, or authority grant.

Exact `S_decision_bound_v2` CJ1 bytes:

```text
{"artifact_type":"ExternalConstituentOneShotInstrumentDispositionEvidenceV2","artifact_version":"V2","census_digest":"sha256:3333333333333333333333333333333333333333333333333333333333333333","census_identity":"external-census-v1:2222222222222222222222222222222222222222222222222222222222222222","certification_digest":null,"certification_identity":null,"committed_successor_root_digest":null,"committed_successor_root_identity":null,"consumption_fence_digest":null,"consumption_fence_identity":null,"contract_version":"G77_134_EXTERNAL_CONSTITUENT_DECISION_BOUND_INSTRUMENT_DISPOSITION_EVIDENCE_V2_EXACT_CANONICAL_BYTE_CONTRACT_V1","disposition_cas_digest":"sha256:3333333333333333333333333333333333333333333333333333333333333333","disposition_cas_identity":"external-disposition-cas-v1:2222222222222222222222222222222222222222222222222222222222222222","disposition_kind":"ADOPTION_DECISION_BOUND","human_decision_digest":"sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","human_decision_identity":"human-founding-decision-v1:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","human_finality_digest":"sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff","human_finality_identity":"human-finality-v1:eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee","instrument_digest":"sha256:7777777777777777777777777777777777777777777777777777777777777777","instrument_identity":"founding-instrument-v2:6666666666666666666666666666666666666666666666666666666666666666","invalidation_proof_digest":null,"invalidation_proof_identity":null,"invalidation_reason_code":null,"linearized_at":"2026-08-11T00:00:00.000000Z","predecessor_disposition_state_digest":"sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","predecessor_disposition_state_identity":"founding-disposition-state-v1:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","predecessor_slot_status":"UNUSED","producing_owner":"external-universe-custody-owner-v1:1515151515151515151515151515151515151515151515151515151515151515","proof_set_digest":null,"proof_set_identity":null,"read_back_disposition_state_digest":"sha256:4444444444444444444444444444444444444444444444444444444444444444","reissue_permitted":false,"reserved_successor_root_generation":null,"reset_permitted":false,"root_cas_digest":null,"root_cas_identity":null,"slot_status":"DECISION_BOUND_ADOPT","source_evidence_digest":"sha256:5555555555555555555555555555555555555555555555555555555555555555","source_evidence_identity":"external-source-v2:4444444444444444444444444444444444444444444444444444444444444444","target_digest":"sha256:9999999999999999999999999999999999999999999999999999999999999999","target_disposition_domain_identity":"external-target-disposition-domain-v1:1111111111111111111111111111111111111111111111111111111111111111","target_identity":"founding-target-v2:8888888888888888888888888888888888888888888888888888888888888888","transition_digest":null,"transition_identity":null,"universe_digest":"sha256:1111111111111111111111111111111111111111111111111111111111111111","universe_identity":"external-universe-v1:0000000000000000000000000000000000000000000000000000000000000000"}
```

Expected idempotency identity:

```text
founding-disposition-idem-v2:e89ad9aeecb1f071bee24c1cb16105ec1dd558f0b378c8f382771325c8616df7
```

Exact `P_decision_bound_v2` CJ1 bytes:

```text
{"artifact_type":"ExternalConstituentOneShotInstrumentDispositionEvidenceV2","artifact_version":"V2","census_digest":"sha256:3333333333333333333333333333333333333333333333333333333333333333","census_identity":"external-census-v1:2222222222222222222222222222222222222222222222222222222222222222","certification_digest":null,"certification_identity":null,"committed_successor_root_digest":null,"committed_successor_root_identity":null,"consumption_fence_digest":null,"consumption_fence_identity":null,"contract_version":"G77_134_EXTERNAL_CONSTITUENT_DECISION_BOUND_INSTRUMENT_DISPOSITION_EVIDENCE_V2_EXACT_CANONICAL_BYTE_CONTRACT_V1","disposition_cas_digest":"sha256:3333333333333333333333333333333333333333333333333333333333333333","disposition_cas_identity":"external-disposition-cas-v1:2222222222222222222222222222222222222222222222222222222222222222","disposition_kind":"ADOPTION_DECISION_BOUND","human_decision_digest":"sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","human_decision_identity":"human-founding-decision-v1:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","human_finality_digest":"sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff","human_finality_identity":"human-finality-v1:eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee","idempotency_identity":"founding-disposition-idem-v2:e89ad9aeecb1f071bee24c1cb16105ec1dd558f0b378c8f382771325c8616df7","instrument_digest":"sha256:7777777777777777777777777777777777777777777777777777777777777777","instrument_identity":"founding-instrument-v2:6666666666666666666666666666666666666666666666666666666666666666","invalidation_proof_digest":null,"invalidation_proof_identity":null,"invalidation_reason_code":null,"linearized_at":"2026-08-11T00:00:00.000000Z","predecessor_disposition_state_digest":"sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","predecessor_disposition_state_identity":"founding-disposition-state-v1:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","predecessor_slot_status":"UNUSED","producing_owner":"external-universe-custody-owner-v1:1515151515151515151515151515151515151515151515151515151515151515","proof_set_digest":null,"proof_set_identity":null,"read_back_disposition_state_digest":"sha256:4444444444444444444444444444444444444444444444444444444444444444","reissue_permitted":false,"reserved_successor_root_generation":null,"reset_permitted":false,"root_cas_digest":null,"root_cas_identity":null,"slot_status":"DECISION_BOUND_ADOPT","source_evidence_digest":"sha256:5555555555555555555555555555555555555555555555555555555555555555","source_evidence_identity":"external-source-v2:4444444444444444444444444444444444444444444444444444444444444444","target_digest":"sha256:9999999999999999999999999999999999999999999999999999999999999999","target_disposition_domain_identity":"external-target-disposition-domain-v1:1111111111111111111111111111111111111111111111111111111111111111","target_identity":"founding-target-v2:8888888888888888888888888888888888888888888888888888888888888888","transition_digest":null,"transition_identity":null,"universe_digest":"sha256:1111111111111111111111111111111111111111111111111111111111111111","universe_identity":"external-universe-v1:0000000000000000000000000000000000000000000000000000000000000000"}
```

Expected artifact identity and digest:

```text
artifact_identity = founding-disposition-v2:44bbe59821cd4c62bc730e71ce9c042b0236fc542de81589095415abcea2263d
artifact_digest = sha256:44bbe59821cd4c62bc730e71ce9c042b0236fc542de81589095415abcea2263d
```

Exact full artifact CJ1 bytes:

```text
{"artifact_digest":"sha256:44bbe59821cd4c62bc730e71ce9c042b0236fc542de81589095415abcea2263d","artifact_identity":"founding-disposition-v2:44bbe59821cd4c62bc730e71ce9c042b0236fc542de81589095415abcea2263d","artifact_type":"ExternalConstituentOneShotInstrumentDispositionEvidenceV2","artifact_version":"V2","census_digest":"sha256:3333333333333333333333333333333333333333333333333333333333333333","census_identity":"external-census-v1:2222222222222222222222222222222222222222222222222222222222222222","certification_digest":null,"certification_identity":null,"committed_successor_root_digest":null,"committed_successor_root_identity":null,"consumption_fence_digest":null,"consumption_fence_identity":null,"contract_version":"G77_134_EXTERNAL_CONSTITUENT_DECISION_BOUND_INSTRUMENT_DISPOSITION_EVIDENCE_V2_EXACT_CANONICAL_BYTE_CONTRACT_V1","disposition_cas_digest":"sha256:3333333333333333333333333333333333333333333333333333333333333333","disposition_cas_identity":"external-disposition-cas-v1:2222222222222222222222222222222222222222222222222222222222222222","disposition_kind":"ADOPTION_DECISION_BOUND","human_decision_digest":"sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","human_decision_identity":"human-founding-decision-v1:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","human_finality_digest":"sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff","human_finality_identity":"human-finality-v1:eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee","idempotency_identity":"founding-disposition-idem-v2:e89ad9aeecb1f071bee24c1cb16105ec1dd558f0b378c8f382771325c8616df7","instrument_digest":"sha256:7777777777777777777777777777777777777777777777777777777777777777","instrument_identity":"founding-instrument-v2:6666666666666666666666666666666666666666666666666666666666666666","invalidation_proof_digest":null,"invalidation_proof_identity":null,"invalidation_reason_code":null,"linearized_at":"2026-08-11T00:00:00.000000Z","metadata":{},"predecessor_disposition_state_digest":"sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","predecessor_disposition_state_identity":"founding-disposition-state-v1:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","predecessor_slot_status":"UNUSED","producing_owner":"external-universe-custody-owner-v1:1515151515151515151515151515151515151515151515151515151515151515","proof_set_digest":null,"proof_set_identity":null,"read_back_disposition_state_digest":"sha256:4444444444444444444444444444444444444444444444444444444444444444","reissue_permitted":false,"reserved_successor_root_generation":null,"reset_permitted":false,"root_cas_digest":null,"root_cas_identity":null,"slot_status":"DECISION_BOUND_ADOPT","source_evidence_digest":"sha256:5555555555555555555555555555555555555555555555555555555555555555","source_evidence_identity":"external-source-v2:4444444444444444444444444444444444444444444444444444444444444444","target_digest":"sha256:9999999999999999999999999999999999999999999999999999999999999999","target_disposition_domain_identity":"external-target-disposition-domain-v1:1111111111111111111111111111111111111111111111111111111111111111","target_identity":"founding-target-v2:8888888888888888888888888888888888888888888888888888888888888888","transition_digest":null,"transition_identity":null,"universe_digest":"sha256:1111111111111111111111111111111111111111111111111111111111111111","universe_identity":"external-universe-v1:0000000000000000000000000000000000000000000000000000000000000000"}
```

Canonical byte evidence:

| Projection | Fields | Bytes | SHA-256 |
|---|---:|---:|---|
| `S_decision_bound_v2` | 46 | 3221 | `e89ad9aeecb1f071bee24c1cb16105ec1dd558f0b378c8f382771325c8616df7` |
| `P_decision_bound_v2` | 47 | 3340 | `44bbe59821cd4c62bc730e71ce9c042b0236fc542de81589095415abcea2263d` |
| full artifact | 50 | 3557 | `889ae6b8bb4162ed71a161712c79a5d6d13c8f859895de8991e5674bae019a64` |

Committed `cj1_encode` and `cj1_decode` independently reproduce all bytes,
field counts, null fields, identities, digests, byte counts, and hashes.

## Deterministic Algorithms

### Construction and validation algorithm

1. Resolve and authenticate the exact Universe custody owner, Universe,
   Census, SourceEvidence, Instrument, Target, HumanDecision, HumanFinality,
   target disposition domain, and current predecessor State.
2. Require the predecessor external slot status `UNUSED` and exact target/
   domain/owner equality.
3. Require the exact V2 type/version/token and closed 50-field set.
4. Require exactly the 16 branch fields above to be present canonical null;
   require every other field present and non-null.
5. Require exact branch constants, false flags, types, pairs, timestamp,
   metadata, NFC, and strict UTF-8.
6. Construct the 46-field S projection including all null fields and compute
   the exact V2 idempotency identity over CJ1(S).
7. Construct P by adding only that idempotency identity; compute artifact
   identity and digest over CJ1(P).
8. Construct the full object by adding only identity/digest and `{}` metadata;
   require exact CJ1 decode/re-encode byte equality.
9. Separately require the existing external CAS/read-back to authenticate the
   `UNUSED -> DECISION_BOUND_ADOPT` effect.
10. Reject every mismatch, ambiguity, alternate branch, or alternate bytes.

Steps 3-8 authenticate representation. Steps 1-2 and 9 preserve the existing
external authority/currentness boundary. Canonical bytes alone have no state
transition effect.

### Second-representation hostile falsification

| Case | Hostile alternate | Rejection boundary |
|---:|---|---|
| A | alternate `contract_version` | exact token and hashes fail |
| B | missing `contract_version` | closed field set fails |
| C | null `contract_version` | non-null constant fails |
| D | wrong artifact type | exact dispatch fails |
| E | wrong artifact version | exact V2 dispatch fails |
| F | wrong disposition branch | exact `ADOPTION_DECISION_BOUND` fails |
| G | wrong decision-bound slot constant | exact `DECISION_BOUND_ADOPT` fails |
| H | wrong predecessor status | exact `UNUSED` fails |
| I | wrong producing owner | resolved custody-owner binding fails |
| J | wrong external Universe custody binding | cross-artifact owner equality fails |
| K | wrong target pair | authenticated Target equality fails |
| L | wrong target disposition domain | Universe/Instrument domain equality fails |
| M | missing field | closed 50-field set fails |
| N | extra field | closed 50-field set fails |
| O | null where branch requires value | branch presence rule fails |
| P | value where branch requires null | exact null row fails |
| Q | absent null-required field | presence and field-set rules fail |
| R | half identity/digest pair | pair rule fails |
| S | alternate identity prefix | prefix/recomputation fail |
| T | alternate idempotency prefix | prefix/recomputation fail |
| U | wrong idempotency identity | recomputation fails |
| V | wrong artifact identity | recomputation fails |
| W | wrong artifact digest | recomputation fails |
| X | non-empty metadata | exact `{}` fails |
| Y | non-NFC value | NFC rule fails |
| Z | noncanonical JSON whitespace | exact CJ1 bytes fail |
| AA | alternate key order | exact CJ1 bytes fail |
| AB | adjacent branch alias | branch constants/nullability fail |
| AC | V1/V3 or adjacent-family alias | exact type/version dispatch fails |

The independently executable hostile contract harness rejected all `29/29`
cases. No second valid decision-bound V2 representation survives:

```text
DUPLICATE_CANONICAL_REPRESENTATION_COUNT = 0
```

## Responsibility Boundaries

- G77-134: exact decision-bound V2 bytes only;
- external Universe custody owner/domain: sole disposition producer and
  target-slot authority;
- HumanDecision/Finality: already authenticated exact Human choice; no new
  Human act here;
- generic validators: local schema/nullability/identity/digest/owner checks;
- immutable persistence: unchanged content-addressed read/write mechanics;
- external slot/currentness: existing CAS and read-back only;
- orchestration: exact owner/target/domain/predecessor equality and ordering;
- Replay/CRO/CLIA: unchanged read-only/non-authoritative observation; and
- future contracts/assessment: Groups S/R and combined Stage-5 authorization
  remain separate.

Anti-entropy and topology evidence:

```text
NEW_CAPABILITY_COUNT = 0
NEW_AUTHORITY_COUNT = 0
NEW_PERSISTENCE_FAMILY_COUNT = 0
NEW_READER_PATH_COUNT = 0
NEW_VALIDATOR_FAMILY_COUNT = 0
NEW_RESULT_FAMILY_COUNT = 0

PRODUCTION_PATHS_BEFORE_AFTER = 1 -> 1
PARALLEL_PATHS_BEFORE_AFTER = 0 -> 0
AUTHORITY_PATHS_BEFORE_AFTER = 1 -> 1
```

# 3. Constitutional Self-Assessment

## Verified

- committed G77-133 baseline, HEAD/tree/subject, clean initial worktree,
  G77-133/G77-132/lineage hashes, mandate hash, and committed CJ1 hash;
- Group P is committed, closed, hash-stable, and unmodified;
- exact V2 family token, branch constants, owner/target/domain bindings,
  declaration/wire orders, 42 semantic fields, 16 canonical nulls, types,
  pair rules, false flags, metadata, NFC, and strict UTF-8;
- exact prefixes, S/P/full formulas, 46/47/50 fields, 3221/3340/3557 bytes,
  identities, digests, and SHA-256 values;
- committed CJ1 independently reconstructs all three exact byte sequences;
- 29/29 hostile alternates reject and duplicate representation count is zero;
- branch isolation and external authority/currentness boundaries are preserved;
- architecture, existing reachability, topology, validator/read/persistence
  families, and observation boundaries remain unchanged; and
- no runtime/test/predecessor mutation, Stage-5 implementation authorization,
  Stage 6, Human act, signature, disposition CAS, BEGIN, consumption, root
  mutation, activation, deployment, production authority, or commit occurred.

## Not Verified

- no runtime model/spec, validator registration, persistence call,
  authentication resolution, orchestration binding, slot CAS/read-back, or
  test is implemented;
- vector pairs are placeholders and do not prove a real Human act, external
  owner, current slot, CAS, or authoritative disposition;
- unrelated refusal, invalidation, consuming, success, and terminal V2/V3
  branches are deliberately not canonicalized by G77-134;
- Groups S and R remain canonically incomplete and unrepaired;
- no independent hostile successor certification or combined implementation-
  authorization assessment has followed; and
- Stage 5 remains implementation-unauthorized and uncertified.

## Constitutional Health Evidence

| Measure | Result |
|---|---|
| architecture stability | preserved; one governance-only branch closure |
| canonical representation uniqueness | complete for decision-bound V2; duplicates `0` |
| branch isolation | exact ADOPTION_DECISION_BOUND only; adjacent branches excluded |
| authority integrity | preserved; bytes cannot create owner, slot authority, currentness, or transition |
| semantic completeness | unchanged and complete from G77-42/G77-132 |
| canonical-byte completeness | Groups P and D complete; Groups S and R incomplete |
| reuse integrity | committed CJ1, G77-42 state machine, custody owner, generic mechanics, immutable/current-slot readers reused |
| duplicate representation pressure | removed for this exact branch |
| new capability pressure | `0` |
| topology stability | production `1 -> 1`, parallel `0 -> 0`, authority `1 -> 1` |
| fail-closed effectiveness | effective; wrong branch/nullability/owner/target/bytes reject |
| Group P preservation | committed hash unchanged; no predecessor mutation |
| Stage-5 readiness | Groups P/D closed only; implementation unauthorized pending S/R and combined assessment |

No synthetic health score is assigned.

## Reuse Impact Assessment

1. **Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?**
   Ponovno se uporabijo committed CJ1, G77-42 disposition state machine,
   zunanji Universe custody owner, obstoječe identity/digest formule,
   generični validatorji, immutable persistence, target-slot/currentness CAS
   ter read-only Replay/CRO/CLIA meje.
2. **Katere nove zmogljivosti (če sploh) nastanejo?** Nobena runtime ali
   authority zmogljivost. Nastane samo exact canonical-byte pogodba za eno
   obstoječo decision-bound V2 vejo.
3. **Ali katera obstoječa zmogljivost postane nedosegljiva?** Ne. Zavrnjene so
   samo druge veje in nekanonične reprezentacije v tem ozkem pogodbenem
   kontekstu; njihove obstoječe semantike niso spremenjene.
4. **Ali implementacija ustvarja vzporedni tok?** Implementacije ni;
   vzporedni tok ostane `0 -> 0`.
5. **Ali zmanjšuje ali povečuje število produkcijskih poti?** Ne; ostane
   `1 -> 1`.

## Pattern Learning Evidence

Preserved without promotion:

- `AUTOMATED_INDEPENDENT_ADVERSARIAL_CERTIFICATION`;
- `CONSTITUTIONAL_PATTERN_LEARNING_AND_PROMOTION`;
- `TRANSITIVE_CANONICAL_PREDECESSOR_COMPLETENESS_CHECK`; and
- `UNDER_SPECIFIED_CANONICAL_PREDECESSOR_ADMISSION` as a mature recurring
  constitutional-development pattern candidate.

G77-134 demonstrates branch-specific canonical closure: a family-level schema
is insufficient where nullability and constants change by state-machine
branch. This is evidence only and changes no constitutional text, validator,
hook, or promotion status.

`PATTERN_DETECTED != CONSTITUTION_CHANGED`.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| committed G77-133 baseline | HEAD/tree/subject, clean status, hashes | Git and SHA-256 authentication | PASS |
| Group P preservation | committed G77-133 hash | predecessor hash comparison | PASS |
| exact family/token/branch | normative constants | literal and state-machine review | PASS |
| closed semantic/envelope fields | 42 semantic and 50 full fields | field-set reconstruction | PASS |
| exact branch nullability | 16 mandatory null fields | deterministic schema harness | PASS |
| declaration and CJ1 wire order | numbered orders and exact bytes | unsigned UTF-8 order review | PASS |
| types/constants/pairs | exact rules table | deterministic validation | PASS |
| owner/target/domain boundary | resolved bindings | authority reduction | PASS |
| exact S/P/full formulas | 46/47/50 projections | committed CJ1 reconstruction | PASS |
| exact byte counts and hashes | complete vectors | independent SHA-256 computation | PASS |
| hostile second representation | A-AC matrix | deterministic 29-case harness | PASS |
| duplicate representation zero | no hostile alternate accepted | independent harness | PASS |
| no new capability/authority/path | exact anti-entropy counts | topology and boundary review | PASS |
| Group D only | G77-132 inventory and branch scope | scope review | PASS |
| runtime/test implementation | prohibited and outside scope | no execution required | NOT_APPLICABLE |
| Stage-5 implementation authorization | prohibited | authority-boundary review | NOT_APPLICABLE |
| G48 six-section structure | this artifact | top-level heading count/order | PASS |
| whitespace integrity | sole new governance artifact | `git diff --check` plus untracked-file check | PASS |
| exact mutation scope | final Git status | one-created-file check | PASS |

# 5. Repository Mutation Summary

Modified files:

- CREATE
  `docs/governance/G77_134_CANDIDATE_H_STAGE_5_EXTERNAL_CONSTITUENT_DECISION_BOUND_INSTRUMENT_DISPOSITION_EVIDENCE_V2_EXACT_CANONICAL_BYTE_CONTRACT_BOUNDED_SUCCESSOR_CONTRACT_V1.md`
  — Group D decision-bound branch canonical-byte contract only.

Unchanged subsystems:

- all runtime modules and tests;
- G77-133/Group P, G77-132, G77-42, and every predecessor governance artifact;
- CJ1, models, validators, persistence, queries, authentication, and
  orchestration;
- other disposition branches, ResultV2, Replay, CRO, CLIA, Human,
  Certification, Groups S/R, Stage 6, activation, deployment, and production.

API compatibility: unchanged; no API or implementation mutation.

Boundary preservation: no authority creation/transfer, target-slot selection,
external or internal owner creation, currentness mechanism, pointer advance,
disposition operation, consumption, BEGIN, new state transition, new reader,
registry, persistence family, production path, root mutation, adoption,
activation, deployment, Stage-5 implementation authorization, Stage 6, or
commit.

Unrelated pre-existing changes: none observed at baseline authentication.

Expected and final mutation inventory:
`1 CREATE / 0 MODIFY / 0 DELETE / 0 RENAME`.

The final artifact SHA-256 is reported externally after validation because a
file cannot contain its own stable ordinary SHA-256.

# 6. Certification Verdict

G77_DECISION_BOUND_INSTRUMENT_DISPOSITION_EVIDENCE_V2_EXACT_CANONICAL_BYTE_CONTRACT_SUCCESSOR_CONTRACT_COMPLETE
