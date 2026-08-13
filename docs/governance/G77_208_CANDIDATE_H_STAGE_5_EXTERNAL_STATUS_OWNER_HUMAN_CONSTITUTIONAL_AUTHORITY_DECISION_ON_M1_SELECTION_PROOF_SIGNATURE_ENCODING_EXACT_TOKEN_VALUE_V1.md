# 1. Implementation Summary

Generation: G77-208

Report identity:
`G77_208_CANDIDATE_H_STAGE_5_EXTERNAL_STATUS_OWNER_HUMAN_CONSTITUTIONAL_AUTHORITY_DECISION_ON_M1_SELECTION_PROOF_SIGNATURE_ENCODING_EXACT_TOKEN_VALUE_V1`

Reporting date: 2026-08-13

Assessment kind:
`HUMAN_CONSTITUTIONAL_AUTHORITY_DECISION_ON_M1_SELECTION_PROOF_SIGNATURE_ENCODING_EXACT_TOKEN_VALUE`

Constitutional baseline: committed G77-207 HEAD
`cf4bd279ccee1f57909bff0ee8ab0892cb36cc5f`, tree
`e394febb84af1b9df7beeec4fe991dcf14481917`, parent
`c6667abe2c4f307aa6ecabc98a98c96cc8a055d2`, subject
`G77-207 select M1 proof detached signature wire field`.

The initial worktree was clean. G77-207 and every predecessor were treated as
immutable evidence and were not modified or repaired.

Authenticated evidence:

| Evidence | SHA-256 |
|---|---|
| G77-208 mandate | `6346abdae6dc58c7df904168f4da13f309db7eef6743aa3613e6bb179e2b7f2e` |
| G48-00 | `16508d1a77c4b3f07d37861e74d85f77896be16da01ca26cbc07a658ddf2c0eb` |
| committed CJ1 | `8442f2c84b4bb95935f6a7c38e3ff12e54a8fd154f17e1bcc0c368831e00f0a3` |
| G77-171 | `280628ee35e2309dc48f67438d34656dc3031991e5a155cf19729ff3a8304dad` |
| G77-173 | `0acb9f9e08684d699963594ac5b763b87ad6ddff61c63e8bec358a1d195aae90` |
| G77-184 | `a67f51839b421d45a1918b1fdceb25e8964c43f3804e864139309c642aa7ffeb` |
| G77-192 | `22b34efea7aff7e77e6eae0fcc1b6ec0fe3ed98cf670bf775339bdf197e78109` |
| G77-193 | `d4ddf51ab6706cfe2676a3ea24e56969841609bb1d27ee98ae19bec8f29607f7` |
| G77-198 | `da3a29cea5c3374badc400aa1a580e4c0c6047ba93c6195694b552a31006df3d` |
| G77-199 | `7797992a82a5bfb88c8078ef5d33f2fc89c9089710acec050196ed5f9ef39985` |
| G77-200 | `435552f360433fa521dedef56213afdf35fad6f2fcb9539296d6db5fe546c7e6` |
| G77-201 | `c4a6c8b6add411e58ad99fe683c9524d7d3349271c4acd6fe41f44c9fc0e2e5a` |
| G77-202 | `60fcd406f3eb753bc9b912c3974ee2f6a50154f943e9ecf834bcc5090bc26bbe` |
| G77-203 | `4aaad91bf7c7f3f6e00d45dc7fc7d107b833ae58f98172af636e5904d0cb8b9d` |
| G77-204 | `64a10577f658184953d776de3fa7f3a0cca8cd55746ecf87659e1f21beade37f` |
| G77-205 | `797c8fdb9b5e301a76a7400c60da2c7924f9cf47b068f68e6254ae5e7180b86b` |
| G77-206 | `058d6508437901f2103d59a56846382aacb2345fd114b5fe3255b9c3f6e3a674` |
| committed G77-207 | `53641306951197f1e1337e3eb33cedf044cb6f4cd768cebe9864b2158a54c87b` |

The exact G77-207 entry condition was authenticated:

```text
FIRST_REMAINING_G77_207_BLOCKER =
  G77_207_B01_HUMAN_CONSTITUTIONAL_AUTHORITY_M1_SELECTION_PROOF_SIGNATURE_ENCODING_EXACT_TOKEN_VALUE_DECISION_REQUIRED
```

The Human Constitutional Authority decision supplied by the G77-208 mandate
is recorded exactly:

```text
M1_SELECTION_PROOF_SIGNATURE_ENCODING_EXACT_TOKEN_VALUE =
  BASE64_RFC4648_PADDED
CLOSURE = NEW_HUMAN_CONTRACT
```

This decision selects the canonical M1 Selection Proof V1 signature transport
encoding only. It does not select another signature algorithm, key, trust
root, cryptographic authority, signed-message instance, proof instance,
signature instance, private-key behavior, runtime, deployment, or activation.

Certified convergence after that decision uniquely closes the exact padded
standard-Base64 representation, the 64-byte Ed25519 signature length, the
88-character canonical transport, the six-field CJ1 order, the exact
473-byte proof bound, and the exact 1,072-byte signed-message class. It also
closes the public verification, replay, duplicate, conflict, and hostile
validation rules without importing G77-171 purpose or authority.

```text
FIRST_REMAINING_BLOCKER = NONE
AUTHORIZED_NEXT_STEP =
  DETERMINISTIC_G77_178_M1_POST_CONTRACT_INTAKE_READINESS_RERUN_AFTER_G77_208
```

This result closes the bounded M1 Selection Proof V1 canonical contract. It
does not declare the complete operational protocol ready. In particular,
G77-199's optional same-source freshness retry behavior remains visibly
unselected and must be reconsidered by the separate post-contract readiness
rerun; it is not a proof-envelope coordinate and is not silently resolved by
G77-208.

Modified modules: none.

Created artifact: this one Human decision and mechanically continued
governance assessment only.

Intentionally unchanged: every predecessor; runtime; tests; cryptographic
implementation; keys; admitted Generation-1 anchor; D3/D4; private owner
boundary; Replay/currentness; persistence; deployment; activation; BEGIN;
root; and production paths.

# 2. Code Evidence

## Public API

No API, model, schema registry, parser, serializer, validator, verifier,
endpoint, Result, key resolver, reader, writer, RNG adapter, persistence path,
or orchestration API is created or changed. This artifact freezes governance
contract facts only.

## Orchestration Entry Point

No orchestration entry point is created. The completed bounded dependency
order is:

```text
G77-202 exact final 13-field / 1072-byte challenge
-> G77-204 proof type/version
-> G77-205 Shape A over exact final challenge
-> G77-206 exact M2 six-coordinate membership
-> G77-207 detached_signature and signature_encoding wire keys
-> G77-208 Human BASE64_RFC4648_PADDED token
-> certified strict encoding and Ed25519 representation mechanics
-> exact six-field CJ1 order and 473-byte proof bound
-> exact final challenge bytes as signed message
-> exact public verification/replay/conflict/hostile rules
-> STOP before instance creation or the separate readiness rerun
```

No proof, signature, nonce, challenge, identity, digest, or signed-message
instance is created by this dependency walk.

## Semantic Reductions

### Preserved proof contract

```text
M1_SELECTION_PROOF_ARTIFACT_TYPE =
  external-status-owner-m1-selection-proof-v1
M1_SELECTION_PROOF_ARTIFACT_VERSION = V1
M1_SELECTION_PROOF_EXACT_SEMANTIC_SHAPE =
  MINIMAL_DETACHED_SIGNATURE_ENVELOPE_OVER_EXACT_FINAL_CHALLENGE
SELECTED_G77_203_SHAPE = A
SELECTED_G77_205_MEMBERSHIP_FAMILY = M2
CANONICAL_M1_SELECTION_PROOF_V1_SEMANTIC_COORDINATE_COUNT = 6

M1_SELECTION_PROOF_EXACT_WIRE_KEYS =
  artifact_type
  artifact_version
  challenge_identity
  challenge_digest
  detached_signature
  signature_encoding

M1_SELECTION_PROOF_DETACHED_SIGNATURE_EXACT_WIRE_FIELD_NAME =
  detached_signature
M1_SELECTION_PROOF_SIGNATURE_ENCODING_EXACT_WIRE_FIELD_NAME =
  signature_encoding
SIGNATURE_VALUE_FIELD_NAME_ENCODING_COUPLING = NONE
PROOF_FACT_DUPLICATION_AUTHORITY = NONE
CANONICAL_CHALLENGE_FACT_SOURCE_COUNT = 1
```

### Exact encoding semantics

The token obtains M1 contract authority only from the G77-208 Human decision.
Its exact mechanics then converge from G77-171's padded RFC 4648/no-whitespace
contract and G77-173's independently certified strict decode, re-encode, and
64-byte length gates:

| Order | Encoding coordinate | Exact result | Closure |
|---:|---|---|---|
| 1 | alphabet | RFC 4648 standard Base64 alphabet `A-Z a-z 0-9 + /` | `MECHANICAL_REUSE` |
| 2 | padding | RFC 4648 `=` padding is mandatory | `MECHANICAL_REUSE` |
| 3 | unpadded form | prohibited | mechanically forced by padded token and canonical re-encode |
| 4 | base64url | prohibited; `-` and `_` are not standard-alphabet substitutes | mechanically forced |
| 5 | hexadecimal | prohibited | G77-208 selects Base64, not hex |
| 6 | canonical text | ASCII only, exact length, no whitespace, exact padding, no alternate spelling | `MECHANICAL_REUSE` |
| 7 | decoder strictness | reject non-alphabet text, whitespace, missing/excess/misplaced padding, noncanonical pad bits, wrong decoded length, or decode/re-encode inequality | `MECHANICAL_REUSE` |

The acceptance relation is exact:

```text
ENCODING_TOKEN = BASE64_RFC4648_PADDED
TEXT_UTF8_BYTE_LENGTH = 88
TEXT_ASCII_CHARACTER_LENGTH = 88
TEXT_GRAMMAR_PRECHECK = ^[A-Za-z0-9+/]{86}==$
DECODED_SIGNATURE_BYTE_LENGTH = 64
WHITESPACE_ALLOWED = NO
UNPADDED_ALLOWED = NO
BASE64URL_ALLOWED = NO
HEX_ALLOWED = NO

ACCEPT_BASE64_TEXT(T) iff
  ASCII(T)
  and len(T) = 88
  and T matches the standard-alphabet/padding precheck
  and STRICT_RFC4648_PADDED_DECODE(T) succeeds
  and len(DECODE(T)) = 64
  and RFC4648_STANDARD_PADDED_ENCODE(DECODE(T)) = T
```

The precheck alone is insufficient because it cannot prove zero canonical pad
bits. Decode/re-encode byte equality is therefore mandatory.

### Detached signature representation

Ed25519 under RFC 8032 yields exactly 64 signature bytes. Sixty-four modulo
three equals one, so canonical standard Base64 yields 22 four-character
quanta, 88 characters total, and exactly two final padding characters.

```text
SIGNATURE_MECHANISM = ED25519_RFC8032
UNDERLYING_SIGNATURE_BYTE_LENGTH = 64
BASE64_QUANTUM_COUNT = 22
DETACHED_SIGNATURE_ASCII_CHARACTER_LENGTH = 88
DETACHED_SIGNATURE_UTF8_BYTE_LENGTH = 88
DETACHED_SIGNATURE_DATA_CHARACTER_COUNT = 86
DETACHED_SIGNATURE_PADDING_CHARACTER_COUNT = 2
DETACHED_SIGNATURE_FINAL_PADDING = ==
DETACHED_SIGNATURE_CJ1_TYPE = string
DETACHED_SIGNATURE_CJ1_ESCAPING_REQUIRED = NO
```

The exact CJ1 representation is one JSON string primitive containing the 88
canonical ASCII characters. Its wire bytes are one opening quotation mark,
86 standard-Base64 data characters, two `=` bytes, and one closing quotation
mark. No example or placeholder signature value is instantiated.

`detached_signature_base64` remains valid only inside the G77-171 foreign
anchor-control proof contract. It is not an M1 Selection Proof V1 key.

### Ordered downstream closure

| Order | Coordinate | Exact result | Classification |
|---:|---|---|---|
| 1 | `challenge_identity` representation | exact 112-byte string `external-status-owner-m1-selection-challenge-v1:` plus 64 lowercase SHA-256 hex | `CONTRACT_REUSE` from G77-202 |
| 2 | `challenge_digest` representation | exact 71-byte string `sha256:` plus the same 64 lowercase core-hash hex | `CONTRACT_REUSE` from G77-202 |
| 3 | six-field schema | exactly the six G77-206 coordinates; no unknown, missing, or duplicate key | prior `NEW_HUMAN_CONTRACT` plus mechanical completion |
| 4 | CJ1 field order | `artifact_type`, `artifact_version`, `challenge_digest`, `challenge_identity`, `detached_signature`, `signature_encoding` | committed CJ1 mechanical derivation |
| 5 | signer/key representation | no direct proof coordinate; resolve only the admitted Generation-1 anchor bound by the authenticated exact challenge | exact M2 exclusion preserved |
| 6 | algorithm representation | no direct proof coordinate; exact challenge mechanism/version plus admitted anchor fix Ed25519 | exact M2 exclusion preserved |
| 7 | proof identity/digest/integrity | none; no independent coordinate authorized | exact M2 exclusion preserved |
| 8 | proof profile/contract | none; type/version already discriminate the proof family | exact M2 exclusion preserved |
| 9 | signed bytes | exact complete 1,072-byte final M1 Selection Challenge CJ1 bytes | Shape A and challenge responsibility |
| 10 | proof byte bound | exact 473 UTF-8 CJ1 bytes | symbolic mechanical derivation |
| 11 | verification/replay/conflict/hostile rules | exact fail-closed rules below | certified semantic/mechanical convergence |

Challenge pair requirements are:

```text
H = lowercase_hex(SHA256(EXACT_843_BYTE_CHALLENGE_CORE_CJ1))
challenge_identity =
  "external-status-owner-m1-selection-challenge-v1:" || H
challenge_digest = "sha256:" || H
IDENTITY_TO_DIGEST_RELATION =
  SAME_EXACT_CORE_SHA256_HEX__DISTINCT_SEMANTIC_PREFIXES
```

### Exact canonical proof model and byte accounting

The exact semantic values and lengths are:

| CJ1 key order | Value rule | UTF-8 value length |
|---:|---|---:|
| `artifact_type` | `external-status-owner-m1-selection-proof-v1` | 43 |
| `artifact_version` | `V1` | 2 |
| `challenge_digest` | exact authenticated G77-202 digest grammar | 71 |
| `challenge_identity` | exact authenticated G77-202 identity grammar | 112 |
| `detached_signature` | exact canonical padded Base64 representation | 88 |
| `signature_encoding` | `BASE64_RFC4648_PADDED` | 21 |

```text
KEY_TEXT_BYTE_COUNT = 99
VALUE_TEXT_BYTE_COUNT = 337
PAIR_FIXED_SYNTAX_BYTE_COUNT = 30
COMMA_BYTE_COUNT = 5
OBJECT_BRACE_BYTE_COUNT = 2
M1_SELECTION_PROOF_EXACT_CJ1_BYTE_LENGTH = 473
FINAL_NEWLINE = ABSENT
UTF8_BOM = ABSENT
```

The bound is invariant for every conforming proof because every value has an
exact fixed byte length and requires no CJ1 escape expansion.

### Exact signed message

```text
FINAL_M1_SELECTION_CHALLENGE =
  CANONICAL_STATEMENT_OF_AUTHENTICATED_FACTS
FINAL_M1_SELECTION_CHALLENGE_FIELD_COUNT = 13
FINAL_M1_SELECTION_CHALLENGE_CJ1_BYTE_LENGTH = 1072

SIGNED_MESSAGE =
  EXACT_COMPLETE_FINAL_M1_SELECTION_CHALLENGE_CJ1_BYTES
SIGNED_MESSAGE_BYTE_LENGTH = 1072
SIGNED_MESSAGE_INCLUDES_CHALLENGE_IDENTITY = YES
SIGNED_MESSAGE_INCLUDES_CHALLENGE_DIGEST = YES
SIGNED_MESSAGE_BOM = ABSENT
SIGNED_MESSAGE_TRAILING_NEWLINE = ABSENT
SIGNED_MESSAGE_RECONSTRUCTION_SUBSTITUTE = PROHIBITED
```

The proof pair addresses and authenticates the same exact final challenge.
The verifier must compare the supplied final challenge with its authenticated
issued challenge bytes and must verify the Ed25519 signature over those exact
bytes, not over a core, identity, digest, hash, reconstructed object, or
alternate serialization.

### Exact verification, replay, conflict, and hostile rules

The following rules are uniquely forced by the exact schemas, G77-199
freshness/single-attempt semantics, G77-202 pair contract, G77-205 Shape A,
G77-206 responsibility separation, and G77-173 certified public mechanics:

1. Require one exact proof input where an intake contract later authorizes
   input; reject alternate, fallback, or ambiguous proof candidates.
2. Require strict UTF-8, no BOM, no trailing newline, duplicate-key rejection,
   the exact six-key schema, exact value types/constants, and byte-identical
   CJ1 re-encoding.
3. Require the exact 473-byte bound.
4. Recompute and authenticate the complete challenge core, shared hash,
   identity, digest, 13-field final schema, and exact 1,072 bytes.
5. Require proof `challenge_identity` and `challenge_digest` to equal the
   authenticated final challenge pair and to share its exact hash hex.
6. Resolve only the admitted Generation-1 public anchor bound by that exact
   challenge; reject a caller key, alternate key, fallback key, second anchor,
   raw-key substitute, certificate substitute, or mutable lookup substitute.
7. Strictly decode and re-encode the detached signature as specified above;
   reject every noncanonical or non-64-byte result.
8. Perform one RFC 8032 Ed25519 verification against the admitted anchor over
   the exact complete 1,072 challenge bytes. Any invalid/error/ambiguous result
   fails closed.
9. The same byte-identical proof for the same challenge is the same historical
   evidence only. It is not a new owner selection, freshness event, credential,
   authority grant, or retry authorization.
10. A proof presented for a different, stale, unissued, already-consumed-as-
    fresh, or pair-mismatched challenge is rejected as a fresh selection act.
11. Two byte-distinct proofs claiming the same exact challenge pair constitute
    a permanent evidence conflict and fail closed; no ordering, first-seen,
    last-seen, scan, or possession rule selects a winner.
12. Unknown fields, missing fields, duplicate keys, alternate encodings,
    uppercase/case variants of fixed tokens, whitespace, aliases, extra
    challenge facts, independent algorithm/key/profile/integrity fields,
    secret/private markers, mutable references, and any fallback path are
    rejected.

These are governance-level validation rules. No validator or attempt is
created or executed here.

### G77-171 reuse boundary

| Coordinate | Classification | Exact boundary |
|---|---|---|
| `signature_encoding` key | `CONTRACT_REUSE` only for exact-key convergence already closed in G77-207 | no foreign purpose/authority transfer |
| `BASE64_RFC4648_PADDED` mechanics | `MECHANICAL_REUSE` | M1 value authority comes only from G77-208 `NEW_HUMAN_CONTRACT` |
| `detached_signature_base64` | foreign `CONTRACT_REUSE` prohibited | remains G77-171 key only |
| Ed25519 mechanism/64-byte signature | `MECHANICAL_REUSE` plus already admitted M1 cryptographic constraint | no new algorithm or root |
| strict decode/re-encode/no-whitespace | `MECHANICAL_REUSE` | validation mechanics only |
| G77-171 anchor-control proof purpose | `AUTHORITY_REUSE = NONE` | not M1 protocol-selection evidence authority |
| G77-171 private owner boundary | preserved, not transferred | SAPIANTA receives public material only |

```text
MECHANICAL_REUSE != CONTRACT_REUSE
CONTRACT_REUSE != AUTHORITY_REUSE
SCHEMA_SIMILARITY != AUTHORIZED_SCHEMA
```

## Public Validators

No public validator is implemented. The future validator contract is now
exact at governance level: strict file/input admission when separately
authorized; UTF-8/JSON/CJ1/schema/constants/bounds; challenge pair and issued-
bytes equality; strict padded Base64 decode/re-encode; exact 64-byte signature;
admitted-anchor resolution; one exact-message Ed25519 verification; secret
exclusion; and fail-closed replay/conflict/fallback handling.

## Canonical Data Models

No canonical instance or runtime model is created. The canonical governance
model is closed as one minimal six-field evidence envelope:

```text
M1_SELECTION_PROOF_CANONICAL_FAMILY_COUNT = 1
M1_SELECTION_PROOF_EXACT_SCHEMA = CLOSED_EXACT
M1_SELECTION_PROOF_EXACT_CJ1_ORDER = CLOSED_EXACT
M1_SELECTION_PROOF_EXACT_CJ1_BYTE_LENGTH = 473
M1_SELECTION_PROOF_EXACT_SIGNED_BYTES =
  EXACT_COMPLETE_1072_BYTE_FINAL_M1_SELECTION_CHALLENGE_CJ1
M1_SELECTION_PROOF_AUTHORITY_ROLE =
  HISTORICAL_EXTERNAL_STATUS_OWNER_CONTROL_EVIDENCE_ONLY
M1_SELECTION_PROOF_CURRENTNESS_ROLE = NONE
M1_SELECTION_PROOF_MUTATION_ROLE = NONE
DUPLICATE_CANONICAL_REPRESENTATION_COUNT = 0
```

No proof identity, proof digest, proof integrity, contract-version, profile,
key, algorithm, anchor, package, freshness, or mechanism coordinate is added.

## Deterministic Algorithms

Executed governance derivation:

```text
authenticate G77-207 HEAD/tree/subject and clean worktree
-> authenticate exact G77-207 B01
-> record Human BASE64_RFC4648_PADDED token
-> separate M1 authority from G77-171 mechanical evidence
-> derive strict standard padded Base64 semantics
-> derive 64 bytes -> 88 characters -> final == padding
-> preserve exact challenge identity/digest representations
-> confirm six keys and derive CJ1 order
-> confirm excluded signer/key/algorithm/integrity/profile coordinates
-> freeze exact complete 1072-byte final challenge as signed message
-> derive exact 473-byte proof bound
-> derive fail-closed verification/replay/conflict/hostile rules
-> find no remaining in-scope Human proof coordinate
-> STOP before every instance, private action, runtime change, or next task
```

No encoded signature text, decoded signature bytes, signed bytes, proof bytes,
random value, challenge value, or cryptographic operation is produced.

## Responsibility Boundaries

- Human Constitutional Authority: supplies only the exact G77-208 M1 encoding
  token and retains future constitutional decision authority;
- External Status Owner: retains exclusive private-key possession and every
  future signing action;
- admitted Generation-1 anchor: remains the sole bounded M1 public
  verification root inside exact D3/D4 scope;
- verifier: may later create and authenticate freshness and verify public
  evidence only under separately authorized execution/intake contracts;
- exact final challenge: remains the sole canonical fact statement and signed
  message;
- future M1 proof: remains minimal detached historical control evidence, never
  a command, credential, currentness source, or authority grant;
- Human protocol admission and Independent Certification: remain separate
  future acts; and
- Replay, currentness, durable-outcome, runtime, deployment, activation,
  BEGIN, root, and production authority remain unchanged.

```text
CRYPTOGRAPHIC_VERIFICATION != HUMAN_ADMISSION
HUMAN_ADMISSION != INDEPENDENT_CERTIFICATION
PROOF_POSSESSION != CURRENTNESS
PUBLIC_EVIDENCE != PRIVATE_AUTHORITY
```

Exact zero-instance and topology accounting:

```text
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

# 3. Constitutional Self-Assessment

## Verified

- committed G77-207 HEAD/tree/parent/subject, clean initial worktree, mandate,
  predecessor, G48, CJ1, and controlling-lineage hashes were authenticated;
- the exact G77-207 blocker matched the mandated entry condition;
- the exact Human token `BASE64_RFC4648_PADDED` is recorded as one
  `NEW_HUMAN_CONTRACT` without importing foreign purpose or authority;
- strict standard padded Base64 semantics and 64-byte Ed25519 representation
  close by certified mechanical reuse;
- the exact 88-character/`==` signature transport, six-field order, 473-byte
  proof, and exact 1,072-byte signed-message class are uniquely derived;
- signer/key, algorithm, proof-integrity, and proof-profile duplication remain
  absent exactly as selected by M2;
- exact verification/replay/duplicate/conflict/hostile rules close without a
  new Human proof coordinate;
- all instance, randomness, signature, private-action, key/root, and runtime
  counts remain zero; and
- authority and production topology remain unchanged.

## Not Verified

- any concrete nonce, challenge, identity, digest, proof, signature, signed
  message, owner private action, public verification event, or owner selection;
- G77-199 optional same-source retry count/trigger/failure aggregation;
- post-contract G77-178 intake readiness or any exact operational file/input
  delivery contract not already selected;
- Human admission of an actual owner protocol selection;
- Independent Certification of any actual selection evidence;
- runtime implementation, tests, deployment, activation, Stage-5 effects,
  BEGIN, or root mutation.

The same-source retry gap is not hidden or reclassified. It is outside the M1
proof-envelope coordinate order and remains input to the next readiness rerun.

## Constitutional Health Evidence

| Dimension | Evidence | Status |
|---|---|---|
| predecessor immutability | G77-207 and lineage unchanged | `PASS` |
| G77-198 core preservation | exact eleven-field contract unchanged | `PASS` |
| 843-byte preservation | exact challenge core bound | `PASS` |
| G77-199 freshness preservation | verifier/OS-CSPRNG/32-byte/fail-closed semantics unchanged | `PASS` |
| G77-200 identity-family preservation | single-stage class-prefixed core SHA-256 | `PASS` |
| G77-201 namespace preservation | exact 47-byte namespace | `PASS` |
| G77-202 separator preservation | exact one-byte colon | `PASS` |
| G77-203 proof-family isolation | anchor-control purpose not imported | `PASS` |
| G77-204 proof token/version preservation | exact type and `V1` | `PASS` |
| G77-205 Shape A preservation | exact final challenge remains signed object | `PASS` |
| G77-206 M2 membership preservation | exactly six coordinates | `PASS` |
| G77-207 `detached_signature` wire-key preservation | exact key unchanged | `PASS` |
| `signature_encoding` wire-key preservation | exact separate key unchanged | `PASS` |
| signature encoding exact token closure | G77-208 Human decision | `PASS` |
| encoding/value separation | coupling remains `NONE` | `PASS` |
| challenge/proof responsibility separation | challenge facts remain canonical once | `PASS` |
| proof duplication authority | remains `NONE` | `PASS` |
| 48-byte challenge prefix preservation | exact G77-202 value | `PASS` |
| 112-byte challenge identity preservation | exact fixed grammar/length | `PASS` |
| 13-field challenge preservation | no challenge mutation | `PASS` |
| 1072-byte challenge bound preservation | exact signed-message length | `PASS` |
| proof canonical closure | one six-field 473-byte representation | `PASS` |
| authority preservation | no new authority | `PASS` |
| zero-instance preservation | every required instance count zero | `PASS` |
| private-key separation | no private material/action | `PASS` |
| cryptographic-root preservation | no new/alternate key or root | `PASS` |
| Generation-1 anchor preservation | admitted anchor unchanged | `PASS` |
| D3/D4 preservation | exact scope/lineage unchanged | `PASS` |
| `SCOPE.EXTRA_AUTHORITY` preservation | remains `NONE` | `PASS` |
| Replay/currentness preservation | proof creates neither | `PASS` |
| same-source retry closure | optional operational contract remains unselected | `BLOCKED` |
| runtime mutation absence | all runtime/test counts zero | `PASS` |
| production-path conservation | `1 -> 1` | `PASS` |
| parallel-path conservation | `0 -> 0` | `PASS` |
| Stage-5 activation absence | activation count zero | `PASS` |

The `BLOCKED` same-source retry row is an explicit out-of-scope readiness gap,
not a remaining coordinate in the now-closed canonical proof envelope.

## Reuse Impact Assessment

1. **Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?**
   Mehansko se ponovno uporabijo CJ1, strogi UTF-8/JSON, G77-171/G77-173
   standardni padded-Base64 decode/re-encode in 64-bajtna Ed25519 mehanika.
   Pogodbeno se ponovno uporabijo G77-202 challenge pair, G77-204 do G77-207
   proof koordinate in priznano Generation-1 sidro. G77-171 authority se ne
   prenese.
2. **Katere nove zmogljivosti (če sploh) nastanejo?** Nobena runtime
   zmogljivost. Nastane samo omejen `NEW_HUMAN_CONTRACT` za natančno M1
   encoding vrednost; mehanske posledice zaprejo governance proof pogodbo.
3. **Ali katera obstoječa zmogljivost postane nedosegljiva?** Ne. Vsi
   certificirani artefakti, challenge pogodba, sidro in obstoječe bralne
   zmogljivosti ostanejo dosegljivi in nespremenjeni.
4. **Ali implementacija ustvarja vzporedni tok?** Ne; implementacije ni in
   `PARALLEL_PATHS = 0 -> 0`.
5. **Ali zmanjšuje ali povečuje število produkcijskih poti?** Ne;
   `PRODUCTION_PATHS = 1 -> 1`.

```text
MECHANICAL_REUSE = YES
CONTRACT_REUSE = YES_BOUNDED_TO_EXACT_PREDECESSOR_COORDINATES
AUTHORITY_REUSE_FROM_G77_171 = NONE
NEW_HUMAN_CONTRACT = EXACT_ENCODING_TOKEN_ONLY
```

## Pattern Learning Evidence

| Candidate observation | G77-208 evidence | Promotion |
|---|---|---|
| Human exact token as bounded constitutional act | one exact encoding value closes one coordinate | none |
| automatic downstream continuation | representation/order/bounds close only after token | none |
| certified representation derivation | 64 bytes mechanically yield 88 padded characters | none |
| semantic/wire/value separation | membership, key, and value remain distinct authorities | none |
| reuse versus authority isolation | G77-171 mechanics reused without purpose/authority | none |
| first-blocker refinement | no remaining in-scope proof blocker; readiness gap remains visible | none |
| constitutional hard stop | analysis stops before instances/runtime/next task | none |

`PATTERN_DETECTED != CONSTITUTION_CHANGED`. No pattern is promoted,
implemented, activated, generalized, or granted authority.

## Handoff Classification

```text
ARTIFACT_REVIEW_REQUIRED: YES
REASON:
The artifact records an exact Human Constitutional Authority encoding token
and closes the bounded canonical M1 Selection Proof contract by derivation.
AUTHORITY_CHANGE: NO
CRYPTOGRAPHIC_CHANGE: NO
NEW_OR_UNEXPECTED_BLOCKER: NO
RUNTIME_CHANGE: NO
FIRST_REMAINING_BLOCKER: NONE
NEXT_AUTHORIZED_STEP:
DETERMINISTIC_G77_178_M1_POST_CONTRACT_INTAKE_READINESS_RERUN_AFTER_G77_208
```

## Automation Classification — Shadow Mode Only

```text
AUTO_CONTINUABLE: YES
HUMAN_DECISION_REQUIRED: NO
HARD_STOP_TRIGGERED: NO
AUTOMATION_REASON:
The canonical proof contract is exact; the next bounded action is a
repository-first deterministic readiness reassessment, not owner action or
runtime execution.
PROPOSED_NEXT_TASK:
DETERMINISTIC_G77_178_M1_POST_CONTRACT_INTAKE_READINESS_RERUN_AFTER_G77_208
```

This classification grants zero execution authority. The proposed next task
is not executed by G77-208.

## Auto-Commit Shadow Observation

```text
AUTO_COMMIT_ELIGIBLE: YES
AUTO_COMMIT_REASON:
Exactly one expected governance artifact is created, validation passes,
operational/private/runtime counts are zero, and authority/topology are
unchanged.
AUTO_COMMIT_CLASSIFICATION != COMMIT_AUTHORITY
```

No commit is created.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| committed G77-207 baseline | HEAD/tree/parent/subject and clean status | Git authentication | `PASS` |
| exact predecessor blocker | committed G77-207 B01 | exact token comparison | `PASS` |
| Human encoding token | mandate exact value | decision audit | `PASS` |
| proof type/version/shape | G77-204/G77-205 | predecessor comparison | `PASS` |
| six semantic coordinates/keys | G77-206/G77-207 | schema audit | `PASS` |
| standard Base64 alphabet | G77-171/G77-173 | certified reuse audit | `PASS` |
| mandatory padding/variant exclusion | token plus strict precedent | encoding audit | `PASS` |
| canonical decoder | strict decode/re-encode/no-whitespace | validation-contract audit | `PASS` |
| Ed25519 signature length | G77-171/G77-173/G77-184 lineage | mechanism audit | `PASS` |
| 88-character/`==` derivation | 64-byte symbolic Base64 accounting | arithmetic audit | `PASS` |
| challenge identity representation | G77-202 exact grammar | contract comparison | `PASS` |
| challenge digest representation | G77-202 exact shared hash | contract comparison | `PASS` |
| exact CJ1 key order | committed CJ1 sorting | canonical-order derivation | `PASS` |
| excluded direct coordinates | G77-206 M2 exclusions | duplication audit | `PASS` |
| exact signed bytes | Shape A plus final challenge | responsibility audit | `PASS` |
| exact 473-byte proof bound | fixed key/value/syntax accounting | symbolic byte audit | `PASS` |
| verification rule | exact challenge/SPKI/signature bindings | dependency audit | `PASS` |
| replay/duplicate/conflict rules | freshness and historical-evidence semantics | fail-closed audit | `PASS` |
| hostile rules | exact schema/encoding/bounds/no-fallback | hostile-validation audit | `PASS` |
| G77-171 reuse boundary | mechanics/contract/authority split | reuse audit | `PASS` |
| optional same-source retry | G77-199 explicit non-selection | limitation visibility | `BLOCKED` |
| proof/signature/challenge instances | all counts zero | scope audit | `NOT_APPLICABLE` |
| private actions/material | all counts zero | boundary audit | `NOT_APPLICABLE` |
| runtime/tests/deployment/activation | all counts zero | mutation audit | `NOT_APPLICABLE` |
| topology | authority 1->1; production 1->1; parallel 0->0 | topology audit | `PASS` |
| handoff/automation/auto-commit | exact shadow classifications | control audit | `PASS` |
| G48 exact structure | six numbered sections and required subsections | heading audit | `PASS` |
| whitespace integrity | sole new artifact | diff/whitespace checks | `PASS` |
| exact mutation inventory | final Git status | one-file validation | `PASS` |
| verdict uniqueness/finality | Section 6 | token/final-content check | `PASS` |

The material M1 proof contract has no remaining in-scope blocker. The separate
same-source retry gap is declared under `Not Verified`, remains fail-closed,
and is delegated only to the authorized readiness reassessment.

# 5. Repository Mutation Summary

Modified files:

- CREATE
  `docs/governance/G77_208_CANDIDATE_H_STAGE_5_EXTERNAL_STATUS_OWNER_HUMAN_CONSTITUTIONAL_AUTHORITY_DECISION_ON_M1_SELECTION_PROOF_SIGNATURE_ENCODING_EXACT_TOKEN_VALUE_V1.md`
  — this one Human token decision and deterministic proof-contract closure
  assessment only.

No other file is modified, deleted, or renamed. No predecessor is repaired.

```text
REPOSITORY_MUTATION_COUNT = 1
GOVERNANCE_ARTIFACT_CREATED_COUNT = 1
RUNTIME_FILE_MUTATION_COUNT = 0
TEST_FILE_MUTATION_COUNT = 0
DEPLOYMENT_FILE_MUTATION_COUNT = 0
ACTIVATION_ARTIFACT_COUNT = 0
```

Unchanged subsystems include runtime APIs/models/serializers/validators,
cryptographic implementation, persistence, queries, orchestration, tests,
private owner systems, admitted anchor, D3/D4, Replay, currentness, Human,
constituent, Certification, BEGIN, root, deployment, activation, external
effects, and production authority.

API compatibility: unchanged; no M1 proof API or behavior exists.

Boundary preservation:

- no G77-171 purpose or authority enters the M1 contract;
- no sample/candidate/actual proof, signature, signed bytes, challenge, nonce,
  identity, digest, or private material is created;
- no next task is autonomously executed;
- no runtime/currentness/authority/persistence path is created; and
- no commit is created.

Validation performed:

```text
Git HEAD/tree/parent/subject and clean-worktree authentication
mandate, G48, CJ1, G77-171/G77-173, and controlling-lineage hash authentication
exact G77-207 blocker comparison
standard padded Base64 semantic and strict-decoder convergence audit
Ed25519 64-byte to Base64 88-character/padding arithmetic audit
challenge identity/digest representation preservation audit
six-field schema, CJ1 order, excluded-coordinate, and duplication audit
473-byte proof and 1072-byte signed-message symbolic bound audit
verification/replay/duplicate/conflict/hostile rule dependency audit
G77-171 mechanical/contract/authority reuse-boundary audit
zero-instance/private/root/runtime/topology accounting
same-source retry limitation-visibility audit
git diff --check and untracked-file whitespace validation
G48 heading/subsection and Validation Matrix vocabulary validation
verdict uniqueness/finality and exact one-file mutation validation
```

No commit was created.

# 6. Certification/Assessment Verdict

`G77_208_HUMAN_M1_SELECTION_PROOF_SIGNATURE_ENCODING_EXACT_TOKEN_VALUE_DECISION_RECORDED__CANONICAL_M1_SELECTION_PROOF_CONTRACT_CLOSED__READY_FOR_DETERMINISTIC_G77_178_M1_POST_CONTRACT_INTAKE_READINESS_RERUN`
