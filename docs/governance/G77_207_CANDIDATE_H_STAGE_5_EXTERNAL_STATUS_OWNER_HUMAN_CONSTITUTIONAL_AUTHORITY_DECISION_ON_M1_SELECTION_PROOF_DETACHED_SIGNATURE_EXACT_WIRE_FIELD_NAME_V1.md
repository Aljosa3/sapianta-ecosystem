# 1. Implementation Summary

Generation: G77-207

Report identity:
`G77_207_CANDIDATE_H_STAGE_5_EXTERNAL_STATUS_OWNER_HUMAN_CONSTITUTIONAL_AUTHORITY_DECISION_ON_M1_SELECTION_PROOF_DETACHED_SIGNATURE_EXACT_WIRE_FIELD_NAME_V1`

Reporting date: 2026-08-13

Assessment kind:
`HUMAN_CONSTITUTIONAL_AUTHORITY_DECISION_ON_M1_SELECTION_PROOF_DETACHED_SIGNATURE_EXACT_WIRE_FIELD_NAME`

Constitutional baseline: committed G77-206 HEAD
`c6667abe2c4f307aa6ecabc98a98c96cc8a055d2`, tree
`95fb2aa108a5ae0465f7197149d5c5a29b2b486f`, parent
`f3337de85418f94506184a46fc30db6c66d08095`, subject
`G77-206 select M1 proof field membership`.

The initial worktree was clean. G77-206 and every predecessor were treated as
immutable evidence and were not modified or repaired.

Implementation contracts: G77-207 Human Constitutional Authority mandate;
G48; committed CJ1; G77-131; G77-156; G77-171; G77-182; G77-184/G77-185;
G77-191 through committed G77-206; the admitted Generation-1 public anchor;
and the unchanged owner, D3, D4, Replay, currentness, Human, Certification,
runtime, deployment, activation, BEGIN, root, and production boundaries.

Authenticated evidence:

| Evidence | SHA-256 |
|---|---|
| G77-207 mandate | `c30d63d4929733b2fa9ba954813ca34eb1cc104b5329059020a9d33c6566814d` |
| G48 | `16508d1a77c4b3f07d37861e74d85f77896be16da01ca26cbc07a658ddf2c0eb` |
| committed CJ1 | `8442f2c84b4bb95935f6a7c38e3ff12e54a8fd154f17e1bcc0c368831e00f0a3` |
| G77-131 | `dfa6835f7b17c678b6937958c2b941cf0a7c4e7d067377c5538bf24da7dc38f8` |
| G77-156 | `3ccc8e6dc94c71d3a4997ea7a16e0191659989a8579f5440737cfffc6ea69c4d` |
| G77-171 | `280628ee35e2309dc48f67438d34656dc3031991e5a155cf19729ff3a8304dad` |
| G77-182 | `07460f6fa17b0898de0c98095b195c606caed47400638ecfb9f75499e0f101f5` |
| G77-184 | `a67f51839b421d45a1918b1fdceb25e8964c43f3804e864139309c642aa7ffeb` |
| G77-185 | `b4322481c919ac2ad288ffb3d5eb0298adc7c7331cce3127725258774dcea9d7` |
| G77-191 | `1104eb53e350350d528f56f990fdb1ed7cdeda5a82724075d2ee70829b7d4635` |
| G77-192 | `22b34efea7aff7e77e6eae0fcc1b6ec0fe3ed98cf670bf775339bdf197e78109` |
| G77-193 | `d4ddf51ab6706cfe2676a3ea24e56969841609bb1d27ee98ae19bec8f29607f7` |
| G77-194 | `4a58b560aef39ef4ebd060d465c321d140cee3edde0b04f8e02f8704350c7804` |
| G77-195 | `e6d8cdf9dbe224898fb2c023086f14cbfe314cd338e73603edcc7bb008db05bf` |
| G77-196 | `fd35b485eb343deacbb07adcdc893e4f2162d1c7ba951092b0082c0f7cb35d16` |
| G77-197 | `52d25d52c4800c1e017315c1dc749c9f07b7b6b6e54c97cd6491dbee664e68ca` |
| G77-198 | `da3a29cea5c3374badc400aa1a580e4c0c6047ba93c6195694b552a31006df3d` |
| G77-199 | `7797992a82a5bfb88c8078ef5d33f2fc89c9089710acec050196ed5f9ef39985` |
| G77-200 | `435552f360433fa521dedef56213afdf35fad6f2fcb9539296d6db5fe546c7e6` |
| G77-201 | `c4a6c8b6add411e58ad99fe683c9524d7d3349271c4acd6fe41f44c9fc0e2e5a` |
| G77-202 | `60fcd406f3eb753bc9b912c3974ee2f6a50154f943e9ecf834bcc5090bc26bbe` |
| G77-203 | `4aaad91bf7c7f3f6e00d45dc7fc7d107b833ae58f98172af636e5904d0cb8b9d` |
| G77-204 | `64a10577f658184953d776de3fa7f3a0cca8cd55746ecf87659e1f21beade37f` |
| G77-205 | `797c8fdb9b5e301a76a7400c60da2c7924f9cf47b068f68e6254ae5e7180b86b` |
| committed G77-206 | `058d6508437901f2103d59a56846382aacb2345fd114b5fe3255b9c3f6e3a674` |

The exact G77-206 first blocker was authenticated:

```text
FIRST_REMAINING_G77_206_BLOCKER =
  G77_206_B01_HUMAN_CONSTITUTIONAL_AUTHORITY_M1_SELECTION_PROOF_DETACHED_SIGNATURE_EXACT_WIRE_FIELD_NAME_DECISION_REQUIRED
```

The Human Constitutional Authority decision supplied by G77-207 is recorded
exactly:

```text
M1_SELECTION_PROOF_DETACHED_SIGNATURE_EXACT_WIRE_FIELD_NAME =
  detached_signature
CLOSURE = NEW_HUMAN_CONTRACT

SIGNATURE_VALUE_FIELD_NAME_ENCODING_COUPLING = NONE
SEMANTIC_TO_WIRE_COORDINATE =
  detached_signature -> detached_signature
```

`detached_signature_base64` is not the canonical M1 Selection Proof V1 wire
field name. This does not invalidate that field in the G77-171 anchor-control
contract; it prevents transport encoding from being coupled into the M1 value
field name.

All previously closed contracts remain exact:

```text
M1_SELECTION_PROOF_ARTIFACT_TYPE =
  external-status-owner-m1-selection-proof-v1
M1_SELECTION_PROOF_ARTIFACT_VERSION = V1
M1_SELECTION_PROOF_EXACT_SEMANTIC_SHAPE =
  MINIMAL_DETACHED_SIGNATURE_ENVELOPE_OVER_EXACT_FINAL_CHALLENGE
SELECTED_G77_203_SHAPE = A
SELECTED_G77_205_MEMBERSHIP_FAMILY = M2
CANONICAL_M1_SELECTION_PROOF_V1_SEMANTIC_COORDINATE_COUNT = 6
PROOF_FACT_DUPLICATION_AUTHORITY = NONE
CANONICAL_CHALLENGE_FACT_SOURCE_COUNT = 1
```

The exact wire keys now closed are:

```text
artifact_type
artifact_version
challenge_identity
challenge_digest
detached_signature
```

Encoding remains a separate semantic coordinate. The exact wire key
`signature_encoding` closes by certified mechanical/contract convergence:
G77-206 selects the semantic coordinate with that exact name, G77-171 uses
the exact same key in the closest proof envelope, and no competing applicable
key exists. This closure transfers no G77-171 contract or authority.

The next ordered coordinate is its exact value. G77-171 provides
`BASE64_RFC4648_PADDED`, but G77-203/G77-205/G77-206 consistently classify
that value as a mechanical candidate rather than an M1 contract. Other
transport representations remain possible, and the G77-207 Human decision
expressly grants no encoding-value authority.

First remaining blocker:

```text
G77_207_B01_HUMAN_CONSTITUTIONAL_AUTHORITY_M1_SELECTION_PROOF_SIGNATURE_ENCODING_EXACT_TOKEN_VALUE_DECISION_REQUIRED
```

Therefore:

```text
FIRST_REMAINING_BLOCKER =
  G77_207_B01_HUMAN_CONSTITUTIONAL_AUTHORITY_M1_SELECTION_PROOF_SIGNATURE_ENCODING_EXACT_TOKEN_VALUE_DECISION_REQUIRED
AUTHORIZED_NEXT_STEP =
  SEPARATE_HUMAN_CONSTITUTIONAL_AUTHORITY_M1_SELECTION_PROOF_SIGNATURE_ENCODING_EXACT_TOKEN_VALUE_DECISION
```

Construction stops before encoding value/variant/padding, signature byte
length/representation, complete CJ1 order, signed bytes, proof byte bound,
verification rules, proof, signature, private action, runtime behavior,
admission, Certification, deployment, activation, or commit.

# 2. Code Evidence

## Public API

No API, model, registry, parser, serializer, validator, verifier, endpoint,
Result, key resolver, reader, writer, or runtime path is created or modified.
This artifact records one Human wire-key decision and one mechanically forced
separate encoding key only.

## Orchestration Entry Point

No orchestration entry point is created. The exact dependency order is:

```text
G77-206 exact M2 semantic membership and first four wire keys
-> G77-207 Human detached_signature wire key
-> preserve value-field/encoding-coordinate separation
-> signature_encoding exact wire key by certified convergence
-> [G77-207 B01: signature_encoding exact token/value]
-> future detached-signature representation
-> future challenge-pair representations and complete CJ1 order
-> future signed bytes, proof byte bound, and validation rules
```

Every downstream step after the blocker remains unexecuted.

## Semantic Reductions

### Exact detached-signature wire decision

| Property | Exact value | Closure |
|---|---|---|
| semantic coordinate | `detached_signature` | G77-206 `NEW_HUMAN_CONTRACT` |
| exact M1 V1 wire field name | `detached_signature` | G77-207 `NEW_HUMAN_CONTRACT` |
| encoding coupled into key | `NONE` | G77-207 `NEW_HUMAN_CONTRACT` |
| rejected M1 V1 wire key | `detached_signature_base64` | bounded M1 decision only |
| G77-171 field validity | unchanged inside G77-171 | foreign contract preserved |

The decision is an exact wire-schema coordinate. It is not a signature value,
encoding, signature instance, key, algorithm, or verification rule.

### Encoding separation

```text
SIGNATURE_VALUE_COORDINATE = detached_signature
SIGNATURE_ENCODING_COORDINATE = signature_encoding
SIGNATURE_VALUE_FIELD_NAME_ENCODING_COUPLING = NONE
```

Changing the encoding in a future authorized version would not require
renaming the semantic signature-value key. G77-207 does not authorize such a
change or select any encoding.

### G77-171 reuse boundary

| G77-171 coordinate | Exact G77-171 meaning | M1 classification | G77-207 result |
|---|---|---|---|
| `detached_signature_base64` | encoding-coupled signature value field | `UNDER_SPECIFIED`/foreign field contract | explicitly not M1 V1 wire key |
| `signature_encoding` | separate encoding declaration key | `MECHANICAL_REUSE` and exact-key `CONTRACT_REUSE` convergence | M1 wire key closes as `signature_encoding` |
| `BASE64_RFC4648_PADDED` | G77-171 exact transport value | `MECHANICAL_REUSE` candidate | not M1 contract; first blocker |
| Ed25519 | admitted signature mechanism | `MECHANICAL_REUSE` and inherited cryptographic constraint | no independent M1 proof coordinate |
| anchor-control purpose/authority | prove candidate anchor control | no `CONTRACT_REUSE`; no `AUTHORITY_REUSE` | remains isolated |

```text
MECHANICAL_REUSE != CONTRACT_REUSE
CONTRACT_REUSE != AUTHORITY_REUSE
SCHEMA_SIMILARITY != AUTHORIZED_SCHEMA
```

Exact key convergence does not select the key's exact value.

### Canonical responsibility preservation

```text
FINAL_M1_SELECTION_CHALLENGE =
  CANONICAL_STATEMENT_OF_AUTHENTICATED_FACTS
M1_SELECTION_PROOF =
  DETACHED_EVIDENCE_OF_EXTERNAL_STATUS_OWNER_CONTROL_OVER_EXACT_FINAL_CHALLENGE
CANONICAL_CHALLENGE_FACT_SOURCE_COUNT = 1
PROOF_FACT_DUPLICATION_AUTHORITY = NONE
```

No anchor, selection-package, freshness, mechanism, algorithm,
`proof_integrity_digest`, `contract_version`, or `proof_profile` coordinate is
added to the canonical M1 V1 proof.

### Exact challenge preservation

```text
M1_SELECTION_CHALLENGE_EXACT_CORE_FIELD_COUNT = 11
M1_SELECTION_CHALLENGE_EXACT_CORE_CJ1_BYTE_LENGTH = 843
M1_SELECTION_CHALLENGE_IDENTITY_PREFIX =
  external-status-owner-m1-selection-challenge-v1:
M1_SELECTION_CHALLENGE_IDENTITY_PREFIX_UTF8_BYTE_LENGTH = 48
M1_SELECTION_CHALLENGE_IDENTITY_UTF8_BYTE_LENGTH = 112
M1_SELECTION_CHALLENGE_DIGEST_PREFIX = sha256:
M1_SELECTION_CHALLENGE_DIGEST_UTF8_BYTE_LENGTH = 71
FINAL_M1_SELECTION_CHALLENGE_FIELD_COUNT = 13
FINAL_M1_SELECTION_CHALLENGE_CJ1_BYTE_LENGTH = 1072
```

No challenge mutation occurs.

### Ordered downstream closure

| Order | Coordinate | Authenticated evidence | Classification | Result |
|---:|---|---|---|---|
| 1 | `signature_encoding` exact wire field name | G77-206 semantic name + exact G77-171 proof key; no competing applicable key | `MECHANICAL_REUSE`/`CONTRACT_REUSE` convergence | `signature_encoding` closed exact |
| 2 | `signature_encoding` exact token/value | G77-171 padded-base64 value only; prior M1 lineage calls it candidate | `UNDER_SPECIFIED_FIRST` | G77-207 B01 |
| 3 | exact `detached_signature` representation | depends on encoding value/variant/padding/length | `NOT_REACHED` | blocked by order 2 |
| 4 | exact `challenge_identity` representation in proof | challenge grammar known; complete proof schema not closed | `NOT_REACHED` | blocked by order 2 |
| 5 | exact `challenge_digest` representation in proof | challenge grammar known; complete proof schema not closed | `NOT_REACHED` | blocked by order 2 |
| 6 | complete six-field membership confirmation | semantics closed; exact values incomplete | `NOT_REACHED` | blocked by order 2 |
| 7 | exact CJ1 field order | exact keys converge; value contract incomplete | `NOT_REACHED` | blocked by order 2 |
| 8 | signer/key representation requirement | M2 excludes independent coordinate; final audit downstream | `NOT_REACHED` | blocked by order 2 |
| 9 | algorithm representation requirement | M2 excludes independent algorithm; final audit downstream | `NOT_REACHED` | blocked by order 2 |
| 10 | proof identity/digest/integrity requirement | M2 excludes coordinate; final audit downstream | `NOT_REACHED` | blocked by order 2 |
| 11 | proof profile/contract requirement | M2 excludes coordinate; final audit downstream | `NOT_REACHED` | blocked by order 2 |
| 12 | exact signed bytes | explicitly not inferred | `NOT_REACHED` | blocked by order 2 |
| 13 | exact proof byte bound | exact value sizes unavailable | `NOT_REACHED` | blocked by order 2 |
| 14 | verification/replay/conflict/hostile rules | exact artifact unavailable | `NOT_REACHED` | blocked by order 2 |

Possible transport choices remain materially distinct, including standard
padded base64, unpadded base64, base64url, lowercase hexadecimal, or another
future bounded representation. This list is diagnostic, not a proposal. Only
G77-171's padded base64 is committed, and its exactness is confined to that
foreign proof contract.

### Exact reuse classification

| Coordinate/fact | Classification | Authority consequence |
|---|---|---|
| `detached_signature` wire key | `NEW_HUMAN_CONTRACT` | exact M1 V1 key only |
| no encoding coupling | `NEW_HUMAN_CONTRACT` | keeps value and encoding coordinates separate |
| `signature_encoding` semantic membership | prior `NEW_HUMAN_CONTRACT` | preserved |
| `signature_encoding` wire key | `MECHANICAL_REUSE` + exact-key `CONTRACT_REUSE` | no value or foreign authority transfer |
| `BASE64_RFC4648_PADDED` | `MECHANICAL_REUSE` candidate | no M1 token authority |
| G77-171 proof contract | no `CONTRACT_REUSE` | anchor-control semantics remain foreign |
| G77-171 private authority | no `AUTHORITY_REUSE` into SAPIANTA | private boundary unchanged |
| signature encoding token/value | `UNDER_SPECIFIED` | separate Human decision required |
| all later coordinates | `NOT_REACHED` | zero decision or authority |

## Public Validators

No validator is created or changed. A future strict validator cannot decode,
length-check, or verify `detached_signature` until the exact encoding token,
variant, padding, byte length, and verification rules are closed.

## Canonical Data Models

No canonical proof wire model is created. All six exact wire keys are now
closed, but the value contract is incomplete:

```text
M1_SELECTION_PROOF_EXACT_WIRE_KEYS =
  artifact_type
  artifact_version
  challenge_identity
  challenge_digest
  detached_signature
  signature_encoding

M1_SELECTION_PROOF_SIGNATURE_ENCODING_VALUE = NOT_SELECTED
M1_SELECTION_PROOF_DETACHED_SIGNATURE_REPRESENTATION = NOT_REACHED
M1_SELECTION_PROOF_EXACT_CJ1_FIELD_ORDER = NOT_REACHED
M1_SELECTION_PROOF_EXACT_CJ1_BYTE_LENGTH = NOT_REACHED
M1_SELECTION_PROOF_EXACT_SIGNED_BYTES = NOT_REACHED
```

Wire-key membership does not instantiate an object.

## Deterministic Algorithms

Executed bounded procedure:

```text
authenticate clean committed G77-206 baseline and exact blocker
-> authenticate G77-207 Human mandate
-> preserve type/version/shape/M2/responsibility contracts
-> record exact detached_signature wire key
-> reject detached_signature_base64 only as M1 V1 key
-> preserve separate signature_encoding semantic coordinate
-> inspect exact signature_encoding key evidence
-> close signature_encoding key by exact certified convergence
-> inspect exact encoding value evidence
-> distinguish G77-171 mechanical candidate from M1 contract
-> find multiple possible representations and no selecting authority
-> declare G77_207_B01
-> STOP before representation/order/signed-byte construction
```

No operational or private algorithm is executed.

## Responsibility Boundaries

- Human Constitutional Authority: owns the `detached_signature` key and every
  later new exact encoding/schema coordinate;
- exact final M1 challenge: sole canonical source of authenticated facts;
- future M1 proof: six-key detached evidence envelope only;
- G77-171: exact mechanical precedent within its own anchor-control contract;
- External Status Owner: retains exclusive private-key possession and any
  future signing action;
- admitted Generation-1 public anchor: public verification material under
  exact D3/D4 and `SCOPE.EXTRA_AUTHORITY = NONE` only;
- SAPIANTA: performs no private action and receives no private material;
- Replay/currentness: unchanged; proof evidence is not currentness; and
- runtime, deployment, activation, BEGIN, root, Certification, and production
  authority: unchanged.

# 3. Constitutional Self-Assessment

## Verified

- committed G77-206 HEAD/tree/parent/subject and clean initial worktree;
- G77-207 mandate and controlling lineage hashes;
- exact G77-206 first blocker;
- exact type/version/shape/M2/responsibility preservation;
- exact Human wire key `detached_signature`;
- value-field/encoding-coordinate separation with coupling `NONE`;
- bounded rejection of `detached_signature_base64` as M1 V1 key only;
- exact `signature_encoding` wire key closure by certified convergence;
- G77-171 contract and authority isolation;
- exact challenge contract and one canonical fact source preservation;
- exact encoding token/value is the first remaining Human coordinate;
- no challenge/proof/signature/signed-byte/private/runtime instance or action;
  and
- authority and topology remain unchanged.

## Not Verified

- exact signature-encoding token/value, base64 variant, or padding policy;
- exact signature byte length and `detached_signature` value representation;
- exact challenge-pair proof representations and complete CJ1 field order;
- signer/key, algorithm, proof-integrity, and profile/contract absence rules;
- exact signed bytes, proof byte bound, or verification/replay/conflict/
  hostile rules;
- any proof, signature, challenge, identity, digest, or signed-byte instance;
- any private-owner behavior, runtime implementation, admission,
  Certification, deployment, activation, BEGIN, or root mutation.

## Constitutional Health Evidence

| Dimension | Evidence | Status |
|---|---|---|
| predecessor immutability | clean committed G77-206 baseline | `PASS` |
| G77-198 core preservation | exact 11-field core unchanged | `PASS` |
| 843-byte preservation | exact core bound unchanged | `PASS` |
| G77-199 freshness preservation | verifier freshness contract unchanged | `PASS` |
| G77-200 identity-family preservation | exact formula unchanged | `PASS` |
| G77-201 namespace preservation | exact namespace unchanged | `PASS` |
| G77-202 separator preservation | exact colon unchanged | `PASS` |
| G77-203 proof-family isolation | foreign contract remains isolated | `PASS` |
| G77-204 proof token/version preservation | exact values unchanged | `PASS` |
| G77-205 Shape A preservation | exact semantic shape unchanged | `PASS` |
| G77-206 M2 membership preservation | six semantic coordinates unchanged | `PASS` |
| canonical challenge/proof separation | fact statement versus evidence | `PASS` |
| proof duplication authority | exactly `NONE` | `PASS` |
| first four wire names | exact prior closure preserved | `PASS` |
| detached-signature wire name | exact `detached_signature` | `PASS` |
| encoding separation | value key contains no encoding coupling | `PASS` |
| signature-encoding wire name | exact `signature_encoding` reuse | `PASS` |
| signature-encoding token/value | no exact M1 contract | `BLOCKED` |
| 48-byte challenge prefix preservation | exact prefix unchanged | `PASS` |
| 112-byte challenge identity preservation | exact grammar/bound unchanged | `PASS` |
| 13-field challenge preservation | exact fields/order unchanged | `PASS` |
| 1072-byte challenge bound preservation | exact bound unchanged | `PASS` |
| authority preservation | no authority transfer/new path | `PASS` |
| zero-instance preservation | all exact counts zero | `PASS` |
| private-key separation | no private material/action | `PASS` |
| cryptographic-root preservation | no key/trust-root change | `PASS` |
| Generation-1 anchor preservation | admitted public anchor unchanged | `PASS` |
| D3/D4 preservation | exact scope/lineage unchanged | `PASS` |
| `SCOPE.EXTRA_AUTHORITY` preservation | remains `NONE` | `PASS` |
| Replay/currentness preservation | no new source or semantics | `PASS` |
| runtime mutation absence | runtime count zero | `PASS` |
| production-path conservation | `1 -> 1` | `PASS` |
| parallel-path conservation | `0 -> 0` | `PASS` |
| Stage-5 activation absence | activation count zero | `PASS` |

## Reuse Impact Assessment

1. **Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?**
   `MECHANICAL_REUSE`: committed CJ1/SHA-256, G77-171 proof-envelope,
   `signature_encoding`, Ed25519 in encoding kandidati. `CONTRACT_REUSE`:
   exact G77-204--G77-206 type/version/shape/M2 in challenge-pair wire keys.
   `AUTHORITY_REUSE`: nič v SAPIANTA in nič iz anchor-control proof družine.
   `NEW_HUMAN_CONTRACT`: samo exact `detached_signature` wire key in encoding
   coupling `NONE`.
2. **Katere nove zmogljivosti (če sploh) nastanejo?** Nobena runtime ali
   operativna zmogljivost. Nastane en governance zapis wire-key odločitve;
   value contract, proof in podpis ne nastanejo.
3. **Ali katera obstoječa zmogljivost postane nedosegljiva?** Ne. Challenge,
   package, anchor, D3/D4 in vsi certificirani bralni tokovi ostanejo
   dosegljivi in nespremenjeni.
4. **Ali implementacija ustvarja vzporedni tok?** Ne;
   `PARALLEL_PATHS = 0 -> 0`.
5. **Ali zmanjšuje ali povečuje število produkcijskih poti?** Ne;
   `PRODUCTION_PATHS = 1 -> 1`.

## Pattern Learning Evidence

| Candidate observation | G77-207 evidence | Promotion |
|---|---|---|
| Human exact wire-name decision | one exact `detached_signature` key | none |
| automatic downstream continuation | encoding key assessed immediately | none |
| semantic/wire separation | semantic coordinate maps to exact generic key | none |
| encoding/value separation | encoding absent from signature value key | none |
| canonical fact/evidence separation | challenge remains sole fact source | none |
| duplicate-state prevention | no excluded challenge fact added | none |
| first-blocker refinement | wire name closed; encoding value exposed | none |
| reuse versus authority isolation | G77-171 key/value analyzed independently | none |

`PATTERN_DETECTED != CONSTITUTION_CHANGED`. No pattern is promoted,
implemented, activated, or granted authority.

Exact mutation, instance, private-boundary, and topology accounting:

```text
REPOSITORY_MUTATION_COUNT = 1
GOVERNANCE_ARTIFACT_CREATED_COUNT = 1
RUNTIME_FILE_MUTATION_COUNT = 0
TEST_FILE_MUTATION_COUNT = 0
DEPLOYMENT_FILE_MUTATION_COUNT = 0
ACTIVATION_ARTIFACT_COUNT = 0

RANDOMNESS_OPERATION_COUNT = 0
NONCE_CREATED_COUNT = 0
FRESHNESS_VALUE_CREATED_COUNT = 0
CHALLENGE_CREATED_COUNT = 0
IDENTITY_INSTANCE_CREATED_COUNT = 0
DIGEST_INSTANCE_CREATED_COUNT = 0
PROOF_CREATED_COUNT = 0
SIGNATURE_CREATED_COUNT = 0
SIGNED_BYTES_CREATED_COUNT = 0

PRIVATE_KEY_OPERATION_COUNT = 0
PRIVATE_OWNER_ACTION_COUNT = 0
PRIVATE_KEY_MATERIAL_RECEIVED_BY_SAPIANTA = 0
PRIVATE_KEY_MATERIAL_CREATED_BY_SAPIANTA = 0
PRIVATE_KEY_MATERIAL_STORED_IN_REPOSITORY = 0

NEW_KEY_COUNT = 0
NEW_TRUST_ROOT_COUNT = 0
NEW_CRYPTOGRAPHIC_ROOT_COUNT = 0
NEW_BOUNDED_RUNTIME_CAPABILITY_COUNT = 0
NEW_READER_PATH_COUNT = 0
NEW_AUTHORITY_COUNT = 0
NEW_CRYPTO_AUTHORITY_COUNT = 0
NEW_OUTCOME_AUTHORITY_COUNT = 0

AUTHORITY_PATHS = 1 -> 1
PRODUCTION_PATHS = 1 -> 1
PARALLEL_PATHS = 0 -> 0
```

## Handoff Classification

```text
ARTIFACT_REVIEW_REQUIRED: YES
REASON:
This artifact records exact Human Constitutional Authority wire bytes and
stops at the next Human-owned signature-encoding token/value coordinate.
AUTHORITY_CHANGE: NO
CRYPTOGRAPHIC_CHANGE: NO
NEW_OR_UNEXPECTED_BLOCKER: NO
RUNTIME_CHANGE: NO
FIRST_REMAINING_BLOCKER:
G77_207_B01_HUMAN_CONSTITUTIONAL_AUTHORITY_M1_SELECTION_PROOF_SIGNATURE_ENCODING_EXACT_TOKEN_VALUE_DECISION_REQUIRED
NEXT_AUTHORIZED_STEP:
SEPARATE_HUMAN_CONSTITUTIONAL_AUTHORITY_M1_SELECTION_PROOF_SIGNATURE_ENCODING_EXACT_TOKEN_VALUE_DECISION
```

## Automation Classification — Shadow Mode Only

```text
AUTO_CONTINUABLE: NO
HUMAN_DECISION_REQUIRED: YES
HARD_STOP_TRIGGERED: YES
AUTOMATION_REASON:
The encoding wire key closes by certified convergence, but its exact token
and transport representation remain unselected for M1.
PROPOSED_NEXT_TASK:
SEPARATE_HUMAN_CONSTITUTIONAL_AUTHORITY_M1_SELECTION_PROOF_SIGNATURE_ENCODING_EXACT_TOKEN_VALUE_DECISION
```

Classification grants zero execution authority. The proposed task is not
executed.

## Auto-Commit Shadow Observation

```text
AUTO_COMMIT_ELIGIBLE: YES
AUTO_COMMIT_REASON:
Exactly one expected governance artifact is created; required validation
passes; operational, private, and runtime counts are zero; authority and
topology are unchanged; mutation scope is unambiguous.
AUTO_COMMIT_CLASSIFICATION != COMMIT_AUTHORITY
```

No commit is created.

# 4. Validation Matrix

| Gate/order | Requirement | Evidence | Validation | Result | First-blocker relevance |
|---:|---|---|---|---|---|
| 1 | clean committed G77-206 baseline | HEAD/tree/parent/subject/status | Git authentication | `PASS` | prerequisite |
| 2 | mandate/lineage authenticity | exact SHA-256 inventory | hash recomputation | `PASS` | prerequisite |
| 3 | exact G77-206 blocker | committed G77-206 | blocker comparison | `PASS` | authorizes Human act |
| 4 | closed proof contract | G77-204--G77-206 | exact comparison | `PASS` | prerequisite |
| 5 | detached-signature wire key | G77-207 mandate | Human decision audit | `PASS` | closes G77-206 B01 |
| 6 | encoding separation | exact coupling `NONE` | schema audit | `PASS` | prevents key coupling |
| 7 | G77-171 boundary | key/value/authority independent classification | reuse audit | `PASS` | prevents import |
| 8 | signature-encoding wire key | exact semantic/key convergence | reuse audit | `PASS` | next coordinate closed |
| 9 | signature-encoding token/value | only foreign mechanical candidate | authority audit | `BLOCKED` | first remaining blocker |
| 10 | representations/order | downstream of gate 9 | dependency audit | `NOT_REACHED` | blocked by gate 9 |
| 11 | signed bytes/bound/rules | downstream of exact schema | dependency audit | `NOT_REACHED` | blocked by gate 9 |
| 12 | challenge/responsibility preservation | exact lineage | predecessor audit | `PASS` | unchanged fact source |
| 13 | instance/private/crypto actions | exact zero counts | boundary audit | `NOT_APPLICABLE` | prohibited |
| 14 | runtime/tests/deployment/activation | exact zero counts | mutation audit | `NOT_APPLICABLE` | prohibited |
| 15 | authority/topology | 1->1 / 1->1 / 0->0 | inventory | `PASS` | preservation |
| 16 | health/reuse/pattern evidence | required subsections | report audit | `PASS` | G48 reporting |
| 17 | handoff/automation | Human hard stop | control audit | `PASS` | exact handoff |
| 18 | auto-commit shadow | one artifact/zero prohibited deltas | criteria audit | `PASS` | shadow only |
| 19 | G48 structure | six exact sections | heading audit | `PASS` | reporting |
| 20 | whitespace integrity | sole new artifact | diff checks | `PASS` | quality |
| 21 | exact mutation inventory | final Git status | one-file validation | `PASS` | boundary |
| 22 | verdict uniqueness/finality | Section 6 | finality audit | `PASS` | finality |

Gate 9 is the first remaining Human-owned coordinate. Gates 10 and 11 are
not reached.

# 5. Repository Mutation Summary

Modified files:

- CREATE
  `docs/governance/G77_207_CANDIDATE_H_STAGE_5_EXTERNAL_STATUS_OWNER_HUMAN_CONSTITUTIONAL_AUTHORITY_DECISION_ON_M1_SELECTION_PROOF_DETACHED_SIGNATURE_EXACT_WIRE_FIELD_NAME_V1.md`
  — this exact Human detached-signature wire-key decision, encoding-key reuse,
  and exact encoding-token blocker only.

No other file is modified, deleted, or renamed. All predecessors remain
unchanged.

Unchanged subsystems:

- runtime APIs, models, schemas, serializers, validators, cryptography,
  persistence, queries, package exports, orchestration, and tests;
- private-key and External Status Owner private boundaries;
- admitted Generation-1 public anchor and exact D3/D4 scope;
- exact M1 package/challenge/proof semantic contracts;
- signature encoding value, proof representations, instances, and signed
  bytes; and
- Replay, currentness, Human, constituent, Certification, BEGIN, root,
  deployment, activation, external effects, and production authority.

API compatibility: unchanged; no proof API or runtime behavior exists.

Boundary preservation:

- Human authority selects `detached_signature` only;
- encoding remains a separate coordinate;
- G77-171 signature value name/encoding value is not imported;
- no representation, signed bytes, proof, signature, or private action is
  invented; and
- no currentness, runtime, authority, production, or parallel path is added.

Unrelated pre-existing changes: none observed at task start.

Validation performed:

```text
Git HEAD/tree/parent/subject and clean-worktree authentication
mandate and predecessor SHA-256 authentication
exact G77-206 blocker comparison
proof type/version/shape/M2/responsibility preservation audit
exact detached_signature wire-key and encoding-decoupling audit
G77-171 field/key/value/authority independent reuse classification
signature_encoding exact wire-key convergence audit
encoding-token/value non-uniqueness and authority audit
exact M1 challenge preservation audit
ordered downstream dependency audit
zero-instance/private/cryptographic/runtime/topology inventory
git diff --check
untracked-file whitespace validation
G48 heading/subsection and Validation Matrix vocabulary validation
verdict uniqueness/finality and one-file mutation validation
```

No commit was created.

# 6. Certification Verdict

`G77_207_HUMAN_M1_SELECTION_PROOF_DETACHED_SIGNATURE_EXACT_WIRE_FIELD_NAME_RECORDED_AND_SIGNATURE_ENCODING_WIRE_KEY_CLOSED_BY_CERTIFIED_REUSE__G77_207_B01_HUMAN_CONSTITUTIONAL_AUTHORITY_M1_SELECTION_PROOF_SIGNATURE_ENCODING_EXACT_TOKEN_VALUE_DECISION_REQUIRED`
