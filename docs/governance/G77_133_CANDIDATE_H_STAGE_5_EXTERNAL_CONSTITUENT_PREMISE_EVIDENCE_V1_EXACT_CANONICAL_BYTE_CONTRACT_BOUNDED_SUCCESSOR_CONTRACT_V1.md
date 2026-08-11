# 1. Implementation Summary

Generation: G77-133

Report identity:
`G77_133_CANDIDATE_H_STAGE_5_EXTERNAL_CONSTITUENT_PREMISE_EVIDENCE_V1_EXACT_CANONICAL_BYTE_CONTRACT_BOUNDED_SUCCESSOR_CONTRACT_V1`

Reporting date: 2026-08-11

Contract kind: `BOUNDED_NORMATIVE_SUCCESSOR_CONTRACT`

Constitutional baseline: committed G77-132 HEAD
`9c97c6ca69badfdb0da6625eb1948bd76c30b6a1`, tree
`3c035ab20002e8a2051fefad3c461e35ba8c070a`, subject
`G77-132 establish grouped Stage 5 canonical predecessor closure strategy`.

The initial worktree was clean. Committed G77-132 has SHA-256
`abdf64cbba4069826f5a161e33da397611347ecc6dc20114ee03351e5c6ce96d`.
Committed G77-131 has SHA-256
`dfa6835f7b17c678b6937958c2b941cf0a7c4e7d067377c5538bf24da7dc38f8`.
Committed CJ1 has SHA-256
`8442f2c84b4bb95935f6a7c38e3ff12e54a8fd154f17e1bcc0c368831e00f0a3`.
Baseline authentication therefore passed.

Controlling evidence: G48-00; G77-34; G77-36; G77-37; G77-42;
G77-44; G77-46; G77-125; G77-127; G77-129; G77-130; G77-131;
G77-132; committed CJ1; and the G77-133 mandate.

Authenticated evidence:

| Evidence | SHA-256 |
|---|---|
| G77-133 mandate | `b180d713c876bdf8649116f735abf0d157af21689321d2c183aaaee2c63b8cf5` |
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
| committed CJ1 | `8442f2c84b4bb95935f6a7c38e3ff12e54a8fd154f17e1bcc0c368831e00f0a3` |

Objective: close Group P only by freezing one exact canonical byte contract
for `ExternalConstituentPremiseEvidenceV1` without redesigning its G77-42
semantics or authority boundary.

Normative result:

```text
artifact_type = ExternalConstituentPremiseEvidenceV1
artifact_version = V1
contract_version = G77_133_EXTERNAL_CONSTITUENT_PREMISE_EVIDENCE_V1_EXACT_CANONICAL_BYTE_CONTRACT_V1
identity_prefix = external-premise-v1
idempotency_prefix = external-premise-idem-v1
producing_owner = external_authority_identity
metadata = {}
```

This contract authenticates representation only. It neither creates nor
infers independently prior authority. The external fact, provenance,
anti-self-authorization proof, custody, signature, scope, and origin evidence
remain subject to G77-42 authentication. Caller supply, repository presence,
canonical validity, or a valid signature alone cannot create normative
authority.

Group P is closed by this successor contract. Groups D, S, and R identified
by G77-132 remain required. Stage-5 implementation remains unauthorized.

# 2. Code Evidence

## Public API

No public API is created or changed. A future separately authorized
implementation can reuse the existing read-only immutable surface:

```python
def read_immutable(
    self,
    model_type: type[FrozenCanonicalModel],
    address: ArtifactAddress,
    *,
    owner_bindings: Mapping[str, str] | None = None,
) -> tuple[FrozenCanonicalModel, ImmutableReadBack]:
```

The contract requires one immutable model/spec and the existing generic read
path only. It creates no current-slot operation, registry, scan, reader,
resolver, persistence family, or authority lookup.

## Orchestration Entry Point

The existing bounded dependency remains forward-only:

```text
independently prior external act supplies exact PremiseEvidenceV1 bytes
-> authenticate exact canonical bytes and referenced provenance/custody proof
-> require producing_owner == external_authority_identity
-> bind exact Premise pair into Universe / Manifest / G77-131 status contract
-> continue only through separately authenticated successors
```

Canonical validity is necessary but not sufficient. Orchestration must not
select an external authority, infer one from a caller, accept more than one
asserted premise, treat a signature as self-creating authority, or replace the
external premise with an internal artifact.

## Semantic Reductions

### Exact type, version, token, prefixes, and owner

| Property | Exact value/rule |
|---|---|
| artifact type | `ExternalConstituentPremiseEvidenceV1` |
| artifact version | `V1` |
| contract version | `G77_133_EXTERNAL_CONSTITUENT_PREMISE_EVIDENCE_V1_EXACT_CANONICAL_BYTE_CONTRACT_V1` |
| identity prefix | `external-premise-v1` |
| idempotency prefix | `external-premise-idem-v1` |
| producing owner | non-null NFC string exactly equal to `external_authority_identity` |
| metadata | present exact empty object `{}` |

The contract token is an identity-relevant family constant. It is not an
authority statement, deployment version, signature version, epoch, or
currentness marker.

### Complete declaration order

The exact declaration order is the G77-42 common envelope followed by the
exact Premise semantic row:

```text
01 artifact_type
02 artifact_version
03 artifact_identity
04 artifact_digest
05 contract_version
06 idempotency_identity
07 producing_owner
08 metadata
09 premise_kind
10 external_authority_identity
11 external_authority_identity_scheme
12 authority_origin_epoch
13 authority_origin_evidence_identity
14 authority_origin_evidence_digest
15 authority_predecessor_manifest_identity
16 authority_predecessor_manifest_digest
17 authority_predecessor_count
18 authority_predecessor_root
19 anti_self_authorization_proof_identity
20 anti_self_authorization_proof_digest
21 constituent_scope_identity
22 constituent_scope_digest
23 custody_evidence_identity
24 custody_evidence_digest
25 signature_scheme
26 signature_key_identity
27 signature
28 externally_supplied_at
29 normative_authority_derivation
```

### Exact CJ1 wire order

CJ1 key-sorts by unsigned UTF-8 key bytes, producing exactly:

```text
01 anti_self_authorization_proof_digest
02 anti_self_authorization_proof_identity
03 artifact_digest
04 artifact_identity
05 artifact_type
06 artifact_version
07 authority_origin_epoch
08 authority_origin_evidence_digest
09 authority_origin_evidence_identity
10 authority_predecessor_count
11 authority_predecessor_manifest_digest
12 authority_predecessor_manifest_identity
13 authority_predecessor_root
14 constituent_scope_digest
15 constituent_scope_identity
16 contract_version
17 custody_evidence_digest
18 custody_evidence_identity
19 external_authority_identity
20 external_authority_identity_scheme
21 externally_supplied_at
22 idempotency_identity
23 metadata
24 normative_authority_derivation
25 premise_kind
26 producing_owner
27 signature
28 signature_key_identity
29 signature_scheme
```

Declaration order does not permit alternate bytes. CJ1 wire order controls.

### Complete semantic fields, presence, nullability, and types

The 21 semantic fields are exactly:

```text
premise_kind
external_authority_identity
external_authority_identity_scheme
authority_origin_epoch
authority_origin_evidence_identity
authority_origin_evidence_digest
authority_predecessor_manifest_identity
authority_predecessor_manifest_digest
authority_predecessor_count
authority_predecessor_root
anti_self_authorization_proof_identity
anti_self_authorization_proof_digest
constituent_scope_identity
constituent_scope_digest
custody_evidence_identity
custody_evidence_digest
signature_scheme
signature_key_identity
signature
externally_supplied_at
normative_authority_derivation
```

Every envelope and semantic field is mandatory. No field is nullable.
Unknown, duplicate, omitted, additional, half-pair, wildcard, or alternate
field names fail closed.

| Field/group | Exact type and rule |
|---|---|
| `artifact_type` | non-null string; exact family constant |
| `artifact_version` | non-null string; exact `V1` |
| `contract_version` | non-null string; exact G77-133 token |
| all identity, scheme, epoch, signature, owner, and constant fields | non-empty Unicode NFC strings encoded strict UTF-8 |
| every `*_digest`, `artifact_digest`, and `authority_predecessor_root` | lowercase string `sha256:` plus exactly 64 lowercase hexadecimal characters |
| `authority_predecessor_count` | base-10 integer greater than or equal to zero; not boolean, float, or string |
| `externally_supplied_at` | uppercase UTC RFC3339 string `YYYY-MM-DDTHH:MM:SS.ffffffZ` |
| `premise_kind` | exact `INDEPENDENTLY_PRIOR_CONSTITUENT_AUTHORITY` |
| `normative_authority_derivation` | exact `EXTERNAL_FACT_NOT_MACHINE_DERIVED` |
| `producing_owner` | exact equality to `external_authority_identity` |
| `metadata` | exact empty object `{}` |

Identity scheme, epoch, signature scheme, signature encoding, and referenced
evidence identity strings remain values supplied and authenticated under the
G77-42 external contract. This byte contract fixes their type, presence, and
hash participation; it does not invent a new vocabulary or claim that any
particular value creates authority.

### Exact independently-prior authority provenance binding

The following conjunction is mandatory:

```text
producing_owner == external_authority_identity
premise_kind == INDEPENDENTLY_PRIOR_CONSTITUENT_AUTHORITY
normative_authority_derivation == EXTERNAL_FACT_NOT_MACHINE_DERIVED
origin evidence pair is complete and authenticated
predecessor manifest pair is complete and authenticated
authority_predecessor_count/root equal the resolved complete manifest
anti-self-authorization proof pair is complete and authenticated
proof excludes dependency on current/target/successor Constitution,
  G77-40 through G77-42, Governance, Certification, Human approval alone,
  repository, deployment, and administrator control
constituent scope and custody evidence pairs are complete and authenticated
signature key/scheme/signature authenticate under the external contract
```

The verifier recomputes and authenticates these relations but does not infer
normative authority from them. More than one asserted external premise is
ambiguity and fails closed. This closure adds no currentness rule: the Premise
is immutable external provenance, not a current-slot State.

### Non-alias rules

- V2 or any adjacent type/version is not V1.
- The same semantic row with another `contract_version` is invalid, not an
  alternate V1 representation.
- Universe, SourceCommitment, SourceEvidence, Capacity, StatusContract, and
  Human artifacts cannot alias PremiseEvidenceV1.
- A caller, repository artifact, signature, Certification, or Human approval
  cannot substitute for `external_authority_identity`.
- An empty or half evidence pair, alternate prefix, non-empty metadata,
  different owner, different field type, or byte-distinct JSON is invalid.

## Public Validators

A future independent authorization may admit exactly this model/spec through
the existing generic validation path:

```text
artifact_type = ExternalConstituentPremiseEvidenceV1
artifact_version = V1
identity_field = artifact_identity
digest_field = artifact_digest
identity_prefix = external-premise-v1
idempotency_prefix = external-premise-idem-v1
contract_version = G77_133_EXTERNAL_CONSTITUENT_PREMISE_EVIDENCE_V1_EXACT_CANONICAL_BYTE_CONTRACT_V1
owner_rule = producing_owner equals external_authority_identity
```

Generic validation authenticates the closed local bytes and owner equality.
Referenced evidence resolution, signature validation, anti-self-authorization
proof evaluation, uniqueness of the supplied premise, and normative external
fact admission remain authentication/orchestration responsibilities. No new
validator family is created or justified.

## Canonical Data Models

### Exact S/P/full projections and formulas

`S_premise_v1` contains exactly `artifact_type`, `artifact_version`,
`contract_version`, `producing_owner`, and all 21 semantic fields. It excludes
the three identity fields and metadata.

```text
idempotency_identity =
  cj1_identity(
    "external-premise-idem-v1",
    S_premise_v1
  )

P_premise_v1 = S_premise_v1 plus {
  "idempotency_identity": idempotency_identity
}

artifact_identity =
  cj1_identity(
    "external-premise-v1",
    P_premise_v1
  )

artifact_digest = cj1_digest(P_premise_v1)

full_artifact = P_premise_v1 plus {
  "artifact_identity": artifact_identity,
  "artifact_digest": artifact_digest,
  "metadata": {}
}
```

`cj1_identity(prefix, value)` is `prefix + ":" + lowercase
SHA256(cj1_encode(value))`. `cj1_digest(value)` is `"sha256:" + lowercase
SHA256(cj1_encode(value))`. No alternate identity algorithm exists.

### Complete canonical test vector

The vector uses conspicuous repeated hexadecimal digits solely for independent
reconstruction. Its evidence and signature strings are test placeholders, not
an external constituent act, valid signature, authority grant, or runtime
fixture.

Exact `S_premise_v1` CJ1 bytes:

```text
{"anti_self_authorization_proof_digest":"sha256:8888888888888888888888888888888888888888888888888888888888888888","anti_self_authorization_proof_identity":"anti-self-authorization-proof-v1:7777777777777777777777777777777777777777777777777777777777777777","artifact_type":"ExternalConstituentPremiseEvidenceV1","artifact_version":"V1","authority_origin_epoch":"external-authority-origin-epoch-v1:0000000000000001","authority_origin_evidence_digest":"sha256:3333333333333333333333333333333333333333333333333333333333333333","authority_origin_evidence_identity":"authority-origin-evidence-v1:2222222222222222222222222222222222222222222222222222222222222222","authority_predecessor_count":3,"authority_predecessor_manifest_digest":"sha256:5555555555555555555555555555555555555555555555555555555555555555","authority_predecessor_manifest_identity":"authority-predecessor-manifest-v1:4444444444444444444444444444444444444444444444444444444444444444","authority_predecessor_root":"sha256:6666666666666666666666666666666666666666666666666666666666666666","constituent_scope_digest":"sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","constituent_scope_identity":"constituent-scope-v1:9999999999999999999999999999999999999999999999999999999999999999","contract_version":"G77_133_EXTERNAL_CONSTITUENT_PREMISE_EVIDENCE_V1_EXACT_CANONICAL_BYTE_CONTRACT_V1","custody_evidence_digest":"sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","custody_evidence_identity":"custody-evidence-v1:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","external_authority_identity":"external-authority-v1:1111111111111111111111111111111111111111111111111111111111111111","external_authority_identity_scheme":"EXTERNAL_AUTHORITY_IDENTITY_SCHEME_V1","externally_supplied_at":"2026-08-11T00:00:00.000000Z","normative_authority_derivation":"EXTERNAL_FACT_NOT_MACHINE_DERIVED","premise_kind":"INDEPENDENTLY_PRIOR_CONSTITUENT_AUTHORITY","producing_owner":"external-authority-v1:1111111111111111111111111111111111111111111111111111111111111111","signature":"ed25519-signature-v1:eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee","signature_key_identity":"ed25519-public-key-v1:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","signature_scheme":"ED25519_RFC8032_PURE"}
```

Expected idempotency identity:

```text
external-premise-idem-v1:4ddeb181a6534abd2c631dd3cd3bfdf8289cf119154445455ca693e7c7c414f4
```

Exact `P_premise_v1` CJ1 bytes:

```text
{"anti_self_authorization_proof_digest":"sha256:8888888888888888888888888888888888888888888888888888888888888888","anti_self_authorization_proof_identity":"anti-self-authorization-proof-v1:7777777777777777777777777777777777777777777777777777777777777777","artifact_type":"ExternalConstituentPremiseEvidenceV1","artifact_version":"V1","authority_origin_epoch":"external-authority-origin-epoch-v1:0000000000000001","authority_origin_evidence_digest":"sha256:3333333333333333333333333333333333333333333333333333333333333333","authority_origin_evidence_identity":"authority-origin-evidence-v1:2222222222222222222222222222222222222222222222222222222222222222","authority_predecessor_count":3,"authority_predecessor_manifest_digest":"sha256:5555555555555555555555555555555555555555555555555555555555555555","authority_predecessor_manifest_identity":"authority-predecessor-manifest-v1:4444444444444444444444444444444444444444444444444444444444444444","authority_predecessor_root":"sha256:6666666666666666666666666666666666666666666666666666666666666666","constituent_scope_digest":"sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","constituent_scope_identity":"constituent-scope-v1:9999999999999999999999999999999999999999999999999999999999999999","contract_version":"G77_133_EXTERNAL_CONSTITUENT_PREMISE_EVIDENCE_V1_EXACT_CANONICAL_BYTE_CONTRACT_V1","custody_evidence_digest":"sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","custody_evidence_identity":"custody-evidence-v1:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","external_authority_identity":"external-authority-v1:1111111111111111111111111111111111111111111111111111111111111111","external_authority_identity_scheme":"EXTERNAL_AUTHORITY_IDENTITY_SCHEME_V1","externally_supplied_at":"2026-08-11T00:00:00.000000Z","idempotency_identity":"external-premise-idem-v1:4ddeb181a6534abd2c631dd3cd3bfdf8289cf119154445455ca693e7c7c414f4","normative_authority_derivation":"EXTERNAL_FACT_NOT_MACHINE_DERIVED","premise_kind":"INDEPENDENTLY_PRIOR_CONSTITUENT_AUTHORITY","producing_owner":"external-authority-v1:1111111111111111111111111111111111111111111111111111111111111111","signature":"ed25519-signature-v1:eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee","signature_key_identity":"ed25519-public-key-v1:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","signature_scheme":"ED25519_RFC8032_PURE"}
```

Expected artifact identity and digest:

```text
artifact_identity = external-premise-v1:6897ffbe0e7dcb144cee31671eb39329c214012771f691a0064f8d797a2733d4
artifact_digest = sha256:6897ffbe0e7dcb144cee31671eb39329c214012771f691a0064f8d797a2733d4
```

Exact full artifact CJ1 bytes:

```text
{"anti_self_authorization_proof_digest":"sha256:8888888888888888888888888888888888888888888888888888888888888888","anti_self_authorization_proof_identity":"anti-self-authorization-proof-v1:7777777777777777777777777777777777777777777777777777777777777777","artifact_digest":"sha256:6897ffbe0e7dcb144cee31671eb39329c214012771f691a0064f8d797a2733d4","artifact_identity":"external-premise-v1:6897ffbe0e7dcb144cee31671eb39329c214012771f691a0064f8d797a2733d4","artifact_type":"ExternalConstituentPremiseEvidenceV1","artifact_version":"V1","authority_origin_epoch":"external-authority-origin-epoch-v1:0000000000000001","authority_origin_evidence_digest":"sha256:3333333333333333333333333333333333333333333333333333333333333333","authority_origin_evidence_identity":"authority-origin-evidence-v1:2222222222222222222222222222222222222222222222222222222222222222","authority_predecessor_count":3,"authority_predecessor_manifest_digest":"sha256:5555555555555555555555555555555555555555555555555555555555555555","authority_predecessor_manifest_identity":"authority-predecessor-manifest-v1:4444444444444444444444444444444444444444444444444444444444444444","authority_predecessor_root":"sha256:6666666666666666666666666666666666666666666666666666666666666666","constituent_scope_digest":"sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","constituent_scope_identity":"constituent-scope-v1:9999999999999999999999999999999999999999999999999999999999999999","contract_version":"G77_133_EXTERNAL_CONSTITUENT_PREMISE_EVIDENCE_V1_EXACT_CANONICAL_BYTE_CONTRACT_V1","custody_evidence_digest":"sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","custody_evidence_identity":"custody-evidence-v1:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","external_authority_identity":"external-authority-v1:1111111111111111111111111111111111111111111111111111111111111111","external_authority_identity_scheme":"EXTERNAL_AUTHORITY_IDENTITY_SCHEME_V1","externally_supplied_at":"2026-08-11T00:00:00.000000Z","idempotency_identity":"external-premise-idem-v1:4ddeb181a6534abd2c631dd3cd3bfdf8289cf119154445455ca693e7c7c414f4","metadata":{},"normative_authority_derivation":"EXTERNAL_FACT_NOT_MACHINE_DERIVED","premise_kind":"INDEPENDENTLY_PRIOR_CONSTITUENT_AUTHORITY","producing_owner":"external-authority-v1:1111111111111111111111111111111111111111111111111111111111111111","signature":"ed25519-signature-v1:eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee","signature_key_identity":"ed25519-public-key-v1:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","signature_scheme":"ED25519_RFC8032_PURE"}
```

Canonical byte evidence:

| Projection | Fields | Bytes | SHA-256 |
|---|---:|---:|---|
| `S_premise_v1` | 25 | 2389 | `4ddeb181a6534abd2c631dd3cd3bfdf8289cf119154445455ca693e7c7c414f4` |
| `P_premise_v1` | 26 | 2504 | `6897ffbe0e7dcb144cee31671eb39329c214012771f691a0064f8d797a2733d4` |
| full artifact | 29 | 2717 | `633764f290ae82cd07cea88f32d59ae06810e99e8e9b0243ecb265e9c1fcfa13` |

Committed `cj1_encode` and `cj1_decode` independently reproduce every byte,
field count, identity, digest, byte count, and hash.

## Deterministic Algorithms

### Construction and validation algorithm

1. Receive one externally supplied candidate Premise object; do not select
   between multiple candidates.
2. Require the exact V1 type/version/token and closed 29-field set.
3. Require every field present and non-null, exact constants, exact types,
   exact `{}` metadata, and `producing_owner == external_authority_identity`.
4. Require strict UTF-8, Unicode NFC, exact timestamp form, digest forms, and
   complete evidence pairs.
5. Construct only the 25-field S projection and compute the exact V1
   idempotency identity over CJ1(S).
6. Construct P by adding only that idempotency identity; compute artifact
   identity and digest over CJ1(P).
7. Construct the full object by adding only identity/digest and `{}` metadata.
8. CJ1-encode; decode and re-encode; require byte equality.
9. Authenticate referenced origin/manifest/proof/scope/custody/signature
   evidence and the G77-42 independently-prior exclusion relation.
10. Reject every missing, extra, null, half-pair, wrong-owner, wrong-prefix,
    wrong-hash, noncanonical, ambiguous, or alternate representation.

Steps 1-8 authenticate representation. Step 9 authenticates the already
existing external provenance contract. Neither creates normative authority.

### Second-representation hostile falsification

| Case | Hostile alternate | Rejection boundary |
|---:|---|---|
| A | alternate `contract_version` | exact family token and all hashes fail |
| B | missing `contract_version` | closed field set fails |
| C | null `contract_version` | mandatory non-null string fails |
| D | wrong artifact type | exact family dispatch fails |
| E | wrong artifact version | exact V1 dispatch fails |
| F | wrong `producing_owner` | owner-to-external-authority equality fails |
| G | altered `external_authority_identity` | owner equality and content hashes fail |
| H | altered premise semantic constant | exact G77-42 constant fails |
| I | missing semantic field | closed field set fails |
| J | unknown/additional field | closed field set fails |
| K | null where prohibited | mandatory non-null rule fails |
| L | half identity/digest pair | complete-pair and field-set rules fail |
| M | alternate artifact identity prefix | prefix and recomputation fail |
| N | alternate idempotency prefix | prefix and recomputation fail |
| O | wrong artifact identity | recomputation fails |
| P | wrong artifact digest | recomputation fails |
| Q | non-empty metadata | exact `{}` rule fails |
| R | scalar replaced with array / reordered array attempt | Premise declares no arrays; exact scalar type rejects any array |
| S | non-NFC string | NFC rule fails |
| T | noncanonical JSON whitespace | exact decode/re-encode bytes fail |
| U | alternate object-key byte order | exact CJ1 bytes fail |
| V | adjacent family/version alias | exact type/version dispatch fails |

The independently executable hostile contract harness rejected all `22/22`
cases. No second valid V1 representation survives:

```text
DUPLICATE_CANONICAL_REPRESENTATION_COUNT = 0
```

## Responsibility Boundaries

- G77-133: exact PremiseEvidenceV1 bytes only;
- independently prior external authority: sole source of the external fact
  and evidence; no SAPIANTA substitute;
- G77-42 authentication: provenance, custody, signature, scope, uniqueness,
  and anti-self-authorization validation;
- generic validators: closed schema, identity, digest, constants, and local
  owner equality only;
- immutable persistence: unchanged content-addressed write/read-back only;
- orchestration: exact predecessor equality and ambiguity rejection only;
- Replay/CRO/CLIA: unchanged read-only/non-authoritative observation; and
- future independent assessments: Groups D/S/R closure and combined Stage-5
  implementation authorization remain separate.

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

- committed G77-132 baseline, HEAD/tree/subject, clean initial worktree,
  G77-132/G77-131/lineage hashes, mandate hash, and committed CJ1 hash;
- exact artifact type/version/token, declaration/wire order, closed field set,
  presence, nullability, types, constants, metadata, and owner equality;
- independently-prior authority provenance relation preserved without caller,
  repository, signature-only, Human-only, or internal authority inference;
- exact prefixes, S/P/full projections, formulas, 25/26/29 field counts,
  2389/2504/2717 byte counts, identities, digests, and SHA-256 values;
- committed CJ1 independently reconstructs all three exact byte sequences;
- 22/22 hostile alternates reject and duplicate representation count is zero;
- architecture, existing capability reachability, topology, validator/read/
  persistence families, and observation boundaries remain unchanged; and
- no runtime/test/predecessor mutation, Stage-5 implementation authorization,
  Stage 6, Human act, real signature, BEGIN, root mutation, activation,
  deployment, production authority, or commit occurred.

## Not Verified

- no runtime model/spec, validator registration, persistence call,
  authentication resolution, orchestration binding, or test is implemented;
- the canonical test vector contains placeholders and does not demonstrate a
  real external authority, valid signature, valid custody, or provenance act;
- Groups D, S, and R remain canonically incomplete and are not repaired here;
- no independent hostile successor certification or combined implementation-
  authorization assessment has followed G77-133; and
- Stage 5 remains implementation-unauthorized and uncertified.

## Constitutional Health Evidence

| Measure | Result |
|---|---|
| architecture stability | preserved; one governance-only family closure |
| canonical representation uniqueness | complete for PremiseEvidenceV1; duplicates `0` |
| authority provenance integrity | preserved; representation validity cannot create external authority |
| semantic completeness | unchanged and complete from G77-42/G77-132 |
| canonical-byte completeness | complete for Group P; Groups D/S/R incomplete |
| reuse integrity | committed CJ1, G77-42 semantics, owner model, generic mechanics, immutable store reused |
| duplicate representation pressure | removed for PremiseEvidenceV1; no alternate token/prefix/bytes admitted |
| new capability pressure | `0` |
| topology stability | production `1 -> 1`, parallel `0 -> 0`, authority `1 -> 1` |
| fail-closed effectiveness | effective; unknown/ambiguous/noncanonical/unauthenticated premise rejects |
| Stage-5 readiness | Group P closed only; implementation remains unauthorized pending D/S/R and combined assessment |

No synthetic health score is assigned.

## Reuse Impact Assessment

1. **Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?**
   Ponovno se uporabijo committed CJ1, G77-42 semantični in authority model,
   obstoječe identity/digest formule, generični validatorji, immutable
   persistence ter read-only Replay/CRO/CLIA meje.
2. **Katere nove zmogljivosti (če sploh) nastanejo?** Nobena runtime ali
   authority zmogljivost. Nastane samo en exact canonical-byte naslednik za
   obstoječo PremiseEvidenceV1 družino.
3. **Ali katera obstoječa zmogljivost postane nedosegljiva?** Ne. Zavržene so
   samo nekanonične ali dvoumne reprezentacije, ki niso certificirana
   zmogljivost.
4. **Ali implementacija ustvarja vzporedni tok?** Implementacije ni;
   vzporedni tok ostane `0 -> 0`.
5. **Ali zmanjšuje ali povečuje število produkcijskih poti?** Ne; ostane
   `1 -> 1`.

## Pattern Learning Evidence

Preserved without promotion:

- `AUTOMATED_INDEPENDENT_ADVERSARIAL_CERTIFICATION`;
- `CONSTITUTIONAL_PATTERN_LEARNING_AND_PROMOTION`;
- `TRANSITIVE_CANONICAL_PREDECESSOR_COMPLETENESS_CHECK`; and
- `UNDER_SPECIFIED_CANONICAL_PREDECESSOR_ADMISSION` as the G77-132
  `MATURE_RECURRING_CONSTITUTIONAL_DEVELOPMENT_PATTERN_CANDIDATE`.

G77-133 supplies another bounded instance: a semantically complete predecessor
is not admissible until its exact token, projections, bytes, and hostile
uniqueness are frozen. It does not promote, implement, or modify any
constitutional rule.

`PATTERN_DETECTED != CONSTITUTION_CHANGED`.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| committed G77-132 baseline | HEAD/tree/subject, clean status, hashes | Git and SHA-256 authentication | PASS |
| exact type/version/token | normative constants | literal and projection review | PASS |
| closed semantic/envelope fields | 21 semantic and 29 full fields | field-set reconstruction | PASS |
| declaration and CJ1 wire order | numbered orders and exact bytes | unsigned UTF-8 key-order review | PASS |
| presence/nullability/types/constants | exact rules table | deterministic schema harness | PASS |
| owner/provenance boundary | producing-owner equality and G77-42 conjunction | authority reduction | PASS |
| exact S/P/full formulas | 25/26/29 projections | committed CJ1 reconstruction | PASS |
| exact byte counts and hashes | complete vectors | independent SHA-256 computation | PASS |
| hostile second-representation rejection | A-V matrix | deterministic 22-case harness | PASS |
| duplicate representation count zero | no hostile alternate accepted | independent harness | PASS |
| no new capability/authority/path | anti-entropy counts | boundary and topology review | PASS |
| Group P only | G77-132 inventory | scope review | PASS |
| runtime/test implementation | prohibited and outside scope | no execution required | NOT_APPLICABLE |
| Stage-5 implementation authorization | prohibited | authority-boundary review | NOT_APPLICABLE |
| G48 six-section structure | this artifact | top-level heading count/order | PASS |
| whitespace integrity | sole new governance artifact | `git diff --check` plus untracked-file check | PASS |
| exact mutation scope | final Git status | one-created-file check | PASS |

# 5. Repository Mutation Summary

Modified files:

- CREATE
  `docs/governance/G77_133_CANDIDATE_H_STAGE_5_EXTERNAL_CONSTITUENT_PREMISE_EVIDENCE_V1_EXACT_CANONICAL_BYTE_CONTRACT_BOUNDED_SUCCESSOR_CONTRACT_V1.md`
  — Group P canonical-byte contract only.

Unchanged subsystems:

- all runtime modules and tests;
- G77-132, G77-131, G77-42, and every predecessor governance artifact;
- CJ1, models, validators, persistence, queries, authentication, and
  orchestration;
- ResultV2, Replay, CRO, CLIA, Human, Certification, Groups D/S/R, Stage 6,
  activation, deployment, and production.

API compatibility: unchanged; no API or implementation mutation.

Boundary preservation: no new authority, authority transfer, caller-derived
authority, internal substitute, currentness mechanism, reader, registry,
persistence family, production path, Human act, real signature, BEGIN, root
mutation, adoption, activation, deployment, Stage-5 implementation
authorization, Stage 6, or commit.

Unrelated pre-existing changes: none observed at baseline authentication.

Expected and final mutation inventory:
`1 CREATE / 0 MODIFY / 0 DELETE / 0 RENAME`.

The final artifact SHA-256 is reported externally after validation because a
file cannot contain its own stable ordinary SHA-256.

# 6. Certification Verdict

G77_PREMISE_EVIDENCE_V1_EXACT_CANONICAL_BYTE_CONTRACT_SUCCESSOR_CONTRACT_COMPLETE
