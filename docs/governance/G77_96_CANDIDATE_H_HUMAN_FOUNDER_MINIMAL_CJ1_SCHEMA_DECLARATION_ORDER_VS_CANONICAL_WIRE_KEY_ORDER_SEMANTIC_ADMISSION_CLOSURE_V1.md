# 1. Implementation Summary

Generation: G77-96

Report identity:
`G77_96_CANDIDATE_H_HUMAN_FOUNDER_MINIMAL_CJ1_SCHEMA_DECLARATION_ORDER_VS_CANONICAL_WIRE_KEY_ORDER_SEMANTIC_ADMISSION_CLOSURE_V1`

Reporting date: 2026-08-10

Classification: `DESIGN / SEMANTIC_CONTRACT_CLOSURE / NON_IMPLEMENTING / NON_ACTIVATING`.

Authenticated repository baseline:

- HEAD: `ce43635a8c025e17196602d8b9edd1af247a0b5b`
- tree: `e721bb5fde70a0ba5bf30eae9fde9323b939e558`
- initial worktree: clean

Controlling blocker:

`G77_95_B01_G77_94_FIELD_ORDER_ADMISSION_RULE_CONFLICTS_WITH_CJ1_SORTED_OBJECT_KEY_ORDER`

Objective:

Close only the ambiguity between G77-92 schema declaration order and the
canonical object-key order already fixed by Candidate CJ1. Preserve every
other G77-92/G77-94 admission, persistence, authentication, Replay, ResultV2,
authority, inventory and topology requirement unchanged.

Semantic determination:

- G77-92 `field_names` tuples define exact schema field membership.
- Tuple position is declaration-order metadata for review and deterministic
  schema definition. It has no independent identity, hashing, comparison or
  wire role.
- Candidate CJ1 remains the sole byte representation. Its committed
  `sort_keys=True` rule exclusively determines mapping key order on wire.
- Admission requires strict `cj1_decode` and byte-identical `cj1_encode`
  re-encoding before schema membership is considered.
- Admission compares the decoded canonical key tuple to
  `tuple(sorted(spec.field_names))`, never to `spec.field_names` directly.
- The sort operation is the same Python Unicode string ordering used by the
  committed CJ1 `json.dumps(sort_keys=True)` implementation.
- No unordered-membership check is sufficient without strict canonical CJ1;
  no input bypasses canonical decode/re-encode.

Selected model:

`OPTION_A_DECLARATION_METADATA_PLUS_DERIVED_CANONICAL_MEMBERSHIP_COMPARISON`.

`SUBCONTRACT_KIND_SPECS.field_names` preserves the G77-92 declaration tuples.
The store derives the expected canonical key tuple locally during validation;
it does not persist or separately configure `canonical_cj1_field_names`.

G77-95 B01 status: `CLOSED_AT_DESIGN_CONTRACT_LEVEL`.

G77-96 does not authorize implementation. A separate independent assessment
must authorize the combined G77-92/G77-94/G77-96 contract before any runtime
or test mutation.

## Authenticated Controlling Lineage

| Artifact | SHA-256 | Introducing commit | Ancestral to baseline |
|---|---|---|---|
| G48-00 | `16508d1a77c4b3f07d37861e74d85f77896be16da01ca26cbc07a658ddf2c0eb` | `2eaabb9e545b9c8d1e2fb1226a66f56973442607` | `YES` |
| G77-73 | `6a6c24bbb86344d76d1f38fa364462fd601e5313400564016dd39cc0b90af586` | `490dc06f577ef76fd93f2a6eccf0372925b5f2c1` | `YES` |
| G77-77 | `f64bdfbd07734a8decdad3cdb338a6c09602807d69f907af4377ca35508e7446` | `8f49d8be66f444e9e971ee6056e438af9279874c` | `YES` |
| G77-85 | `e86c819491ff3ace2a03a1fd6674ac215a1ba8035a756bbe3edc37c7dd34a286` | `1d07c0883b0e2580f90cdb9b030a2284917eb507` | `YES` |
| G77-86 | `df11f66fee97115baf9c884e7cac555b9feefc8c4de888adc721e0d37789228f` | `b851b083eadc7a59ff7fbc36d3cf961cc8afcdcc` | `YES` |
| G77-89 | `edd1fc8e47576c915fbc91b650218dd14f97b163f3b7c9b9bb1b24aeaabea296` | `45c955b2a8bde0008fbe410c6ad0a8bd83f58196` | `YES` |
| G77-90 | `865db7ee1415e321e9460eb780f8308ea0e09607fe43950d5aa2b9859eb3b60b` | `57cabd218fb152d1d53aa55bf2c79caf964170bb` | `YES` |
| G77-91 | `0a2b613c044937ae62edbf15506efa4b35c171dbb9658e5b81fc1300fe62da25` | `edca85e683236ebfd473e12c28918cff34865957` | `YES` |
| G77-92 | `b208ec3eed9b65792a6ba3f8045fc03bd9c7b208d9f144db454e672226ce3909` | `c44aea7c51969e7a4fa86414c876d49c5f1c9870` | `YES` |
| G77-93 | `96c10c406049489d73b55ce3f0c7a205f69546fb3e0dbfc4fb44f31f535e2eb7` | `0d78b3ee2dd55d20cedd636388a3e8bb2533d832` | `YES` |
| G77-94 | `1a57e2a2611123a8962e2ad6a8fe4637e2e4080ae26d24858cdcc285e2b618bd` | `5f6f51a5a6e50674bb3668fd1703507d367df91f` | `YES` |
| G77-95 | `05c3d983e33ffdade5dacacf9cae71c6fea89397a79aa87729939912229fb6cf` | `ce43635a8c025e17196602d8b9edd1af247a0b5b` | `YES` |

G77-95 is committed at the baseline HEAD. Its blocked assessment grants no
implementation authority. G77-96 is a narrow successor: where G77-94 says
“exact CJ1-key order from the G77-92 expanded tuple,” G77-96 replaces that
phrase with the exact derivation specified here. No other predecessor rule is
superseded.

## Option Determination

| Option | Decision | Constitutional assessment |
|---|---|---|
| A. Preserve declaration metadata; derive canonical tuple in admission | `SELECTED` | one source of schema membership, no duplicated tuple, exact alignment with existing CJ1 |
| B. Store both declaration and `canonical_cj1_field_names` tuples | `REJECTED_NOT_MINIMAL` | duplicates mechanically derivable data and creates a possible internal mismatch requiring another validator |

Option B produces no additional safety because
`canonical_cj1_field_names == tuple(sorted(field_names))` would itself need to
be enforced. Deriving it at use time is total, deterministic and smaller.

## Exact Future Inventory

| Path | Action | Combined controlling responsibility |
|---|---|---|
| `aigol/runtime/candidate_h_founder/persistence.py` | `MODIFY` | G77-92/G77-94 APIs and admission; G77-96 exact field-membership/wire-order rule |
| `tests/test_g77_candidate_h_founder_persistence.py` | `MODIFY` | all prior tests plus declaration/wire-order positive and negative proof |
| `aigol/runtime/candidate_h_founder/authentication.py` | `CREATE` | unchanged exact contextual construction, G77-77 continuation and complete ResultV2 |
| `tests/test_g77_candidate_h_founder_retry.py` | `CREATE` | unchanged contextual/cryptographic/restart/non-multiplication/ResultV2 proof |

The inventory remains `2 MODIFY`, `2 CREATE`, `0 DELETE`, `0 RENAME`. No fifth
runtime/test path is required. CJ1, package exports, models, validators and all
other G77-92 reuse paths remain byte-unchanged.

# 2. Code Evidence

## Public API

No G77-92 public signature changes. `write_subcontract`,
`compare_and_swap_subcontract` and `read_subcontract` all invoke the same
G77-94 private admission validator.

The exact G77-96 field rule inside that validator is:

```python
declared_field_names = spec.field_names
if (
    not isinstance(declared_field_names, tuple)
    or len(declared_field_names) != len(set(declared_field_names))
    or any(not isinstance(name, str) or not name for name in declared_field_names)
):
    _fail("SUBCONTRACT_SEMANTIC_ADMISSION_FAILED", "field_set:invalid_spec")

expected_canonical_keys = tuple(sorted(declared_field_names))
if tuple(body.keys()) != expected_canonical_keys:
    _fail("SUBCONTRACT_SEMANTIC_ADMISSION_FAILED", "field_set")
```

This excerpt freezes the required semantics, not implementation formatting.
`body` exists only after strict canonical CJ1 decode/re-encode and mapping-root
validation. `set` is used only to detect duplicate spec metadata; it is not the
admission comparison.

No `canonical_cj1_field_names` member, callback, validation flag, capability
object or second API is added.

## Orchestration Entry Point

No orchestration entry point is created. The one future flow remains:

```text
authentication contextual construction
-> public persistence call
-> strict CJ1 canonical validation
-> exact derived canonical-key membership comparison
-> remaining intrinsic admission
-> existing publisher/CAS/read-back
-> authentication contextual equality
-> complete ResultV2
```

A direct persistence caller cannot select declaration order, wire order or a
comparison mode. There is no algorithm selector. The committed CJ1 codec and
the immutable spec determine the one result.

## Semantic Reductions

Schema declaration semantics:

```text
spec.field_names
= ordered review metadata
+ exact field membership source
- no wire-order authority
- no identity/hash input as a tuple
```

Canonical byte semantics:

```text
candidate bytes B
-> cj1_decode(B)
-> reject unless mapping
-> reject unless cj1_encode(decoded) == B
-> canonical_body_keys = tuple(decoded.keys())
-> expected_keys = tuple(sorted(spec.field_names))
-> require canonical_body_keys == expected_keys
```

The strict re-encode check supplies canonical on-wire order and rejects
duplicate keys, alternative JSON whitespace, alternate escaping, non-NFC text
and every other non-CJ1 representation. The tuple comparison supplies exact
membership and rejects every missing, extra or misspelled field. Neither
predicate substitutes for the other.

For every candidate byte string `B`, acceptance is unique:

1. `cj1_decode(B)` either rejects or returns one decoded value.
2. Byte-identical re-encoding either rejects or proves the one canonical CJ1
   representation of that value.
3. A mapping has one canonical iteration order fixed by the encoded bytes.
4. `tuple(sorted(spec.field_names))` is a pure function of one immutable spec.
5. Tuple equality returns exactly one boolean.
6. All remaining G77-94 intrinsic checks are deterministic functions of the
   same body, address, mode and CAS arguments.

No implementation choice or inference remains.

## Public Validators

G77-96 replaces only the field-order wording. The complete persistence-owned
admission remains:

| Invariant | Exact rule after G77-96 |
|---|---|
| field membership | canonical decoded key tuple equals `tuple(sorted(spec.field_names))` |
| declaration order | retained as metadata; never compared to wire iteration |
| wire order | exclusively enforced by strict committed CJ1 decode/re-encode |
| fixed constants | unchanged G77-94 spec equality |
| conditional nulls | unchanged closed truth tables |
| kind/mode | unchanged nine-row IMMUTABLE/CAS gate |
| prefix/content digest | unchanged hash of exact canonical bytes |
| states/results | unchanged closed-value membership and CAS bindings |
| pair shape/domains | unchanged complete pair and frozen Candidate-domain rules |
| read-back | same complete intrinsic validator re-runs on exact stored bytes |

Authentication retains external predecessor resolution, authority equality,
G77-77 graph equality, signer/key/message custody, one-use proof resolution
and ResultV2 composition. Persistence gains no contextual, Replay, Human or
authority role.

The field failure code remains G77-94's
`SUBCONTRACT_SEMANTIC_ADMISSION_FAILED` with deterministic detail
`field_set` or `field_set:invalid_spec`. No new error domain is required.

## Canonical Data Models

The nine G77-92 tuples remain byte-for-byte unchanged as declaration metadata
and exact membership sources. Reordering those tuples is prohibited because
it is unnecessary and would mutate review metadata.

No existing contract gives tuple position another semantic role:

- subcontract identity and digest hash the CJ1 body, not `field_names`;
- CJ1 sorts mapping keys independently of dataclass/spec declaration order;
- G77-73/G77-77 equality resolves exact body bytes/pairs;
- ResultV2 contains subcontract pairs, not their schema declaration tuples;
  and
- Replay resolves canonical bytes and recomputes identities.

No model, validator, ResultV2 field/version, nested schema, artifact family,
owner, authority or serialization domain changes.

## Deterministic Algorithms

Exact future implementation order:

1. Validate `SubcontractAddress` and byte input without filesystem effects.
2. Call committed `cj1_decode`; require one mapping and byte-identical
   `cj1_encode`.
3. Load the exact closed kind row and validate its declaration tuple itself.
4. Derive `expected_canonical_keys = tuple(sorted(spec.field_names))`.
5. Compare `tuple(body.keys())` to that derived tuple.
6. Run G77-94 constants, null, state, pair, address, mode and CAS-binding
   checks.
7. Only after all admission succeeds derive any record/slot path or invoke
   lock, crash hook, publisher, generation or pointer mechanics.
8. Re-run steps 1-6 on `read_subcontract` before returning read-back.

Exact modified test responsibility in
`tests/test_g77_candidate_h_founder_persistence.py`:

```python
def test_schema_declaration_order_is_metadata_and_cj1_wire_order_is_canonical(
    tmp_path: Path,
) -> None: ...
```

The test SHALL use one G77-92 declaration tuple that is observably not sorted,
construct the mapping in declaration order, encode it with committed CJ1,
assert wire keys equal `tuple(sorted(spec.field_names))`, call the public
write, and prove exact durable read-back.

```python
def test_field_membership_cannot_bypass_strict_cj1_wire_order(
    tmp_path: Path,
) -> None: ...
```

The test SHALL manually encode the same exact field membership in noncanonical
declaration-key order and prove `INVALID_SUBCONTRACT_INPUT`, zero crash-hook
invocation and zero record/slot/generation/lock effect.

The G77-94 direct semantic-negative parameterization remains unchanged and
continues to cover wrong field membership, constant, conditional null, state
and pair shape through both public writes. No new test module is required.

## Responsibility Boundaries

| Responsibility | Exact owner | Effect of G77-96 |
|---|---|---|
| schema declaration tuple | immutable persistence admission spec | metadata/membership source only |
| CJ1 wire-key order | unchanged `candidate_h_founder.cj1` | sole canonical order; no modification |
| intrinsic admission | `persistence.py` | derives sorted expected tuple and compares after strict CJ1 |
| contextual graph validation | `authentication.py` | unchanged; no duplicated storage logic |
| immutable/CAS/history mechanics | existing Candidate store | unchanged single path |
| read-only Replay | later consumer | exact bytes plus contextual resolution; no write/repair |
| G77-77 signer continuation | authentication owner | unchanged same accepted tuple |
| ResultV2 | unchanged model/Stage-2 validator | unchanged complete result only |
| Human/root/activation | retained owners | absent and unreachable |

Dependency DAG remains:

```text
cj1 + models + validators -> persistence
cj1 + models + validators + persistence -> authentication
persistence -X-> authentication/Replay/orchestration/CRO/CLIA/root
```

Identity DAG gains no node or edge. Bodies retain identical CJ1 bytes and
pairs; G77-96 only fixes how schema membership is compared before admission.

Authority DAG gains no node or edge. Declaration metadata, sorting, storage,
validation and repository control originate no Human, Founder, signer-key,
root, BEGIN, activation, deployment or production authority.

## Repository Evidence

Committed `aigol/runtime/candidate_h_founder/cj1.py` calls
`json.dumps(..., sort_keys=True)` and rejects input unless re-encoding equals
the original bytes. It is the sole Candidate serializer and requires no
change.

Committed G77-92 supplies the exact nine declaration tuples. Committed G77-94
supplies store-owned admission before filesystem effects. G77-96 replaces the
single contradictory order comparison identified by G77-95 while retaining
both sources unchanged.

The existing store, CJ1, models, validators and tests remain unmodified in
this generation. No subcontract bytes or persistence state is created.

# 3. Constitutional Self-Assessment

## Verified

- The clean baseline and complete lineage through committed G77-95 were
  authenticated by SHA-256, introducing commit and ancestry.
- No predecessor assigns schema declaration position an identity, hash or
  byte-order role independent of Candidate CJ1.
- Option A is strictly smaller than storing duplicate canonical-key metadata.
- Exact membership plus strict CJ1 canonicality are independent mandatory
  predicates; neither is weakened.
- Every candidate byte string has one deterministic admission result.
- G77-95 B01 is closed at design-contract level without changing CJ1.
- G77-94 intrinsic admission, read-back, address, kind/mode, constants, null,
  state, pair and CAS-binding checks remain controlling.
- G77-77, ResultV2, historical Replay, all sixteen crash checkpoints,
  identity/authority DAGs and topology remain unchanged.
- The future inventory remains exactly two MODIFY and two CREATE paths.
- G77-96 creates only this governance artifact and performs no runtime/test
  mutation, authentication, signing, Human act, BEGIN, root mutation,
  adoption, activation, deployment, production effect or commit.

## Not Verified

- The repaired membership comparison and its two focused tests are not
  implemented.
- No future subcontract admission, read-back, crash/retry, G77-77
  continuation, Replay reconstruction or ResultV2 regression is executed.
- Independent implementation authorization remains absent and mandatory.

## Reuse Impact Assessment

1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?
   Ponovno se uporabijo obstoječi Candidate CJ1 z `sort_keys=True`, vseh devet
   G77-92 schema tuples, G77-94 admission model, en `CandidateHStore`, isti
   root/publisher/CAS/history/read-back, Stage-1 modeli, Stage-2 validatorji,
   ResultV2 ter G77-73/G77-77.
2. Katere nove zmogljivosti (če sploh) nastanejo?
   Po ločeni odobritvi nastane samo eksplicitna deterministična izpeljava
   canonical key tuple iz obstoječega `field_names`. Ne nastane nov serializer,
   model, artifact family, owner ali avtoriteta.
3. Ali katera obstoječa zmogljivost postane nedosegljiva?
   Ne. Deklaracijski tuple, CJ1 in vsi obstoječi API-ji ostanejo dosegljivi in
   nespremenjeni.
4. Ali implementacija ustvarja vzporedni tok?
   Ne. Primerjava je obvezni korak iste admission/persistence poti.
5. Ali zmanjšuje ali povečuje število produkcijskih poti?
   Ne. Produkcijske poti ostanejo `1 -> 1`.

Exact topology:

| Measure | Before | After proposed non-activated closure | Delta |
|---|---:|---:|---:|
| production paths | 1 | 1 | 0 |
| parallel paths | 0 | 0 | 0 |
| persistent founding paths | 0 | 0 | 0 |
| Human entry points | 1 | 1 | 0 |
| root paths | 1 | 1 | 0 |
| persistent Founder authorities | 0 | 0 | 0 |

## Crash, Replay, G77-77 and ResultV2 Reassessment

Semantic admission remains checkpoint zero. Noncanonical declaration-order
bytes reject before every G77-92 crash point. Canonical admitted bytes enter
the unchanged sixteen checkpoints and retain exactly the same recovery
classes: absent/safely retryable, identical durable read-back, same accepted
logical continuation or terminal read-only recovery.

`read_subcontract` applies strict CJ1 and the derived membership tuple again.
Historical Replay therefore receives only intrinsically admitted canonical
bytes, then performs unchanged external predecessor resolution. It does not
scan directories, infer from current pointers, repair, write, sign or acquire
authority.

G77-77 exact-tuple continuation uses canonical persisted bytes and is
unaffected by schema declaration metadata. It creates no second Human act,
logical operation, signer invocation, admissible result or founding effect.

ResultV2 remains byte/schema/version unchanged. Its embedded subcontract
pairs hash the same CJ1 bytes. Unchanged Stage-2 validation remains the final
complete-result boundary.

## STOP Conditions and Non-Effects

A future implementation SHALL stop if it requires:

- any CJ1 change or alternate serializer/domain;
- mutation/reordering of G77-92 `field_names` declaration tuples;
- stored or caller-supplied canonical-field-order metadata;
- set-only membership without strict CJ1 revalidation;
- direct comparison of body key order to declaration order;
- any fifth runtime/test path;
- model, validator or ResultV2 changes;
- a second store/root/publisher/CAS/authentication path;
- an authority, Human entry or topology change; or
- bypass of any G77-94 admission or test requirement.

G77-96 performs no implementation and grants no implementation, Human,
signing, founding, BEGIN, root, activation, deployment or production
authority.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| authenticated baseline | exact HEAD/tree/clean initial status | Git inspection | `PASS` |
| controlling lineage | twelve hashes, commits and ancestry | SHA-256/Git inspection | `PASS` |
| G48 structure | six top-level sections/eight Code Evidence subsections | heading review | `PASS` |
| declaration-order meaning | membership metadata only; no independent predecessor role | lineage comparison | `PASS` |
| canonical wire order | committed CJ1 `sort_keys=True` and strict re-encode | source review | `PASS` |
| Option A minimality | canonical tuple is pure derivation; no duplicate state | comparative review | `PASS` |
| unique acceptance result | total six-step byte reduction | determinism proof | `PASS` |
| exact intrinsic admission | G77-94 checks retained; only order comparison repaired | delta review | `PASS` |
| read-back closure | same strict CJ1/membership validator | algorithm review | `PASS` |
| address/kind/state/null/pair/CAS rules | unchanged G77-94 responsibilities | contract comparison | `PASS` |
| G77-77 | exact canonical bytes and same tuple unchanged | dependency review | `PASS` |
| ResultV2 | byte/schema/version and Stage-2 boundary unchanged | model review | `PASS` |
| historical Replay | admission plus contextual resolution; no effect edge | reconstruction review | `PASS` |
| crash/restart | checkpoint zero clarified; sixteen boundaries unchanged | failure review | `PASS` |
| identity/authority DAG | no node/edge added | DAG review | `PASS` |
| inventory | two MODIFY/two CREATE; no fifth path | repository review | `PASS` |
| topology | exact zero-delta cardinalities | topology review | `PASS` |
| future runtime/test implementation | prohibited in G77-96 | worktree review | `NOT_APPLICABLE` |
| future implementation verification | not implemented | no repair tests run | `NOT_RUN` |
| independent implementation authorization | required next | not inferred | `NOT_RUN` |
| governance conformance tests | current repository suite | `pytest tests/test_governance_conformance.py` | `PASS` |
| governance conformance engine | 20 passed, zero failed/critical/warnings; deterministic/fail-closed/read-only | `python -m runtime.governance.governance_conformance_engine` | `PASS` |
| Markdown fences | all fences balanced and closed | deterministic fence scan | `PASS` |
| trailing whitespace | no matching line | `rg -n '[[:blank:]]+$' <artifact>` | `PASS` |
| repository whitespace | sole G77-96 artifact | `git diff --no-index --check /dev/null <artifact>` and `git diff --check` | `PASS` |

The future implementation and authorization `NOT_RUN` rows appear under Not
Verified and prevent authority inference. They do not prevent this
design-only semantic closure.

# 5. Repository Mutation Summary

Created files:

- `docs/governance/G77_96_CANDIDATE_H_HUMAN_FOUNDER_MINIMAL_CJ1_SCHEMA_DECLARATION_ORDER_VS_CANONICAL_WIRE_KEY_ORDER_SEMANTIC_ADMISSION_CLOSURE_V1.md`

Modified existing files: none.

Deleted or renamed files: none.

Runtime/test mutations: none.

Predecessor mutations: none.

API compatibility:

- current APIs and runtime bytes are unchanged;
- future G77-92 public signatures remain unchanged; and
- G77-96 clarifies one internal admission comparison only.

Boundary preservation:

- no CJ1, serializer, store, root, persistence entry, authentication flow,
  key, signature, ResultV2, Human disposition, BEGIN, root state, adoption,
  activation, deployment or production evidence is created;
- HEAD/tree remain at the authenticated baseline; and
- this one uncommitted governance artifact is the complete worktree mutation.

Unrelated pre-existing changes: none observed at task start.

The next permitted action is an independent implementation-authorization
assessment of G77-92/G77-94 as clarified by G77-96. G77-96 now stops.

# 6. Certification Verdict

G77_CANDIDATE_H_CJ1_SCHEMA_DECLARATION_AND_CANONICAL_WIRE_ORDER_SEMANTIC_ADMISSION_CONTRACT_CLOSED
