# 1. Implementation Summary

Generation: G77-116

Report identity:
`G77_116_CANDIDATE_H_STAGE_5_MANIFEST_FAILURE_OBSERVABILITY_PRECEDENCE_MINIMAL_CONSTITUTIONAL_CLOSURE_ALTERNATIVES_ASSESSMENT_V1`

Reporting date: 2026-08-11

Constitutional baseline: committed G77-115 HEAD
`6ddd7e1fdc37bba98c26ba43120deab5eae178f7`, tree
`7d1835eb30390bed77bd2c66a12a7a59ce4853ed`, subject
`G77-115 block Stage 5 repair on immutable-read observability`, with a clean
worktree before G77-116 evidence creation.

Implementation contracts and lineage: G48-00; HFD-04 Revision 2; G77-62;
G77-64; G77-85; G77-86; G77-99 through committed G77-115; committed
Candidate H models, validators, persistence, authentication, orchestration,
and relevant tests.

Objective:

Determine the minimum constitutional closure for:

`G77_115_B01_MANIFEST_CONTENT_ADDRESS_PRECEDENCE_NOT_OBSERVABLE_THROUGH_EXISTING_PUBLIC_IMMUTABLE_READ`

Selected minimum closure:

**Option A — contract-only observable precedence.**

The successor contract SHALL promise only the deterministic distinctions
that `CandidateHStore.read_immutable` exposes through its public return/error
surface. Any decode, model-construction, schema-constant, owner, or validation
failure collapsed by that surface remains one stable fail-closed corruption
class. A content-address mismatch retains a distinct token only when the
public reader reaches and exposes `ARTIFACT_ADDRESS_MISMATCH` after successful
construction and validation.

This closure changes diagnostic specificity, not safety semantics. It
preserves:

- every authority result independently verified by G77-115;
- exact immutable addressing and fail-closed rejection;
- the G77-114 validation/effect boundary;
- no raw-byte access or private persistence call from orchestration;
- no persistence, validator, model, authentication, ResultV2, Replay, or
  root-owner change;
- `NEW_CAPABILITY_COUNT = 0`; and
- the original intended future inventory of
  `0 CREATE / 3 MODIFY / 0 DELETE / 0 RENAME`.

Options assessed:

| Option | Classification | New capabilities | Minimum future inventory | Selection |
|---|---|---:|---|---|
| A. contract-only observable precedence | `SUFFICIENT_MINIMUM` | 0 | 0 create / 3 modify | selected |
| B. structured lower-layer observability | `SUFFICIENT_BUT_UNNECESSARY_BROADER` | 1 | 0 create / 5 modify | not selected |
| C. raw/private access from orchestration | `ARCHITECTURALLY_PROHIBITED` | at least 1 hidden duplicate | nominal 3 paths but responsibility expansion | rejected |

No implementation authority is granted. A new independent implementation-
authorization assessment remains required.

Modified modules:

- none. G77-116 creates only this governance artifact.

Intentionally unchanged modules and surfaces:

- all runtime and tests;
- G77-115 and every predecessor;
- Candidate H authority, authentication, persistence, validation, Replay,
  CRO, CLIA, root-owner, topology, and identity/hash semantics; and
- configuration, activation, deployment, and production.

# 2. Code Evidence

## Public API

The existing public immutable read remains the sole authorized read path:

```python
    def read_immutable(
        self,
        model_type: type[FrozenCanonicalModel],
        address: ArtifactAddress,
        *,
        owner_bindings: Mapping[str, str] | None = None,
    ) -> tuple[FrozenCanonicalModel, ImmutableReadBack]:
```

Option A does not change this API. Orchestration continues to supply one
declared model type and one exact `ArtifactAddress`; it receives either a
fully reconstructed and validated model/read-back or one existing stable
`CandidatePersistenceError`.

The orchestration API also remains unchanged:

```python
def orchestrate_fixture_candidate_h(
    store: CandidateHStore,
    *,
    capacity: HumanFounderExternalCapacityEvidenceV2,
    authentication_commitment: HumanFounderAuthenticationCommitmentV2,
    authentication: FixtureAuthenticationExecution,
    decision: ExternalConstituentHumanFirstAdoptionDecisionV2,
    composition: FixtureForwardComposition | None,
) -> FixtureOrchestrationExecution:
```

No manifest object, TargetV5 object, raw-byte reader, repository path,
resolver, registry, or fallback is added.

## Orchestration Entry Point

The existing accepted-tuple boundary derives the commitment pair from exact
bytes:

```python
    commitment_payload = commitment.to_cj1_object()
    commitment_pair = (
        cj1_identity("human-founder-auth-commitment-v2-sha256", commitment_payload),
        cj1_digest(commitment_payload),
    )
```

G77-116 preserves the G77-114 successful-path order:

```text
accepted tuple
-> exact manifest pair
-> public exact manifest read
-> exact TargetV5 pair
-> public exact TargetV5 read
-> authoritative origin P_root
-> five pointer bindings
-> C_root_v1
-> exact retained-root read/history
-> existing success/P012/DAG validation
-> immutable writes
-> CAS
-> terminal publication
```

Only failure-token classification at the two public immutable reads is
revised. Every read failure still terminates before forward immutable writes,
CAS, terminal publication, or fixture effect.

## Semantic Reductions

### Preserved G77-115 results

No contradictory evidence was found. The following remain frozen:

```text
T_fixture_v1 = (C_pair, K_pair, R_pair, D_pair)

K_pair -> exact CommitmentV2 -> exact M_pair
M_pair -> exact ManifestV2 -> exact A_pair
A_pair -> exact root-custodian TargetV5
TargetV5 -> authoritative founding-origin P_root
P_root -> five independent forward equalities
P_root -> C_root_v1
```

The manifest, Capacity, and HumanDecision continue to fix the same TargetV5.
`INITIAL_BEGIN` remains the sole bounded attempt row. Coherent five-source
substitution remains invalid. Caller authority over `P_root`, `C_root_v1`,
the logical CAS coordinate, root owner, root identity, and root epoch remains
zero.

### Safety requirement

The constitutional safety requirement is:

```text
IF exact immutable predecessor evidence is absent, malformed, invalid,
wrongly addressed, wrong-owner, wrong-contract, or otherwise inadmissible:

  reject before all forward effects
```

It does not require orchestration to identify every simultaneous internal
reason after the certified public reader has already rejected the record.

### Diagnostic specificity

The relative taxonomy:

```text
MANIFEST_CONTENT_ADDRESS_MISMATCH
before
MANIFEST_MAPPING_CONTRACT_MISMATCH
```

is diagnostic, not authority-bearing and not safety-critical. Neither token
authorizes a read, write, CAS, root, Human act, or retry. Both conditions
require the same zero-effect fail-closed disposition.

Collapsing an unobservable multi-violation history to `MANIFEST_CORRUPT`
preserves every safety and authority invariant. It avoids pretending that
orchestration knows a later condition that the public reader never reached.

## Public Validators

The local schema validator checks constants before content identity:

```python
    for name, expected in type(model).CONSTANTS.items():
        if getattr(model, name) != expected:
            code = "CONTRACT_VERSION_MISMATCH" if name == "contract_version" else "SCHEMA_CONSTANT_MISMATCH"
            _fail(code, f"{type(model).__name__}.{name}")
```

The public validation order is:

```python
    _validate_local_schema(model)
    _validate_owner(model, bindings)
    _validate_content_identity(model)
    _validate_nested_record(model)
    _validate_hfd_payload(model)
```

Option A treats the existing reader/validator composition as an opaque,
certified fail-closed phase whenever it does not return a model. It does not
parse nested error prose to manufacture a stronger orchestration distinction.

`validate_p012_structural_bindings`, `validate_identity_dag`, model owner
rules, and all identity formulas remain unchanged. Generic validators do not
gain Stage-5 diagnostic policy.

## Canonical Data Models

The manifest mapping contract is already a frozen model constant:

```python
_define(
    "CandidateHInputReferenceManifestV2",
    HFD_MANIFEST_FIELDS,
    constants={
        "manifest_artifact_type": "HUMAN_FOUNDER_CANDIDATE_H_INPUT_REFERENCE_MANIFEST",
        "manifest_artifact_version": "V2",
        "candidate_h_contract_lineage_count": 7,
        "mapping_contract": "DIRECT_RETAINED_PAIR_OR_EXACT_PROJECTION_V2",
        "metadata": {},
    },
)
```

The constructor checks it before returning a model:

```python
        for name, expected in self.CONSTANTS.items():
            if getattr(self, name) != expected:
                raise CanonicalModelError(
                    f"{type(self).__name__}.{name} must equal {expected!r}"
                )
```

Therefore a successfully returned manifest cannot carry the wrong mapping
contract. A separate post-return mapping-contract token is redundant for
safety and unreachable for the committed model. Wrong mapping bytes remain
rejected as corrupt by the public read.

TargetV5 type/version constants and its fixed root-custodian owner are also
validated before successful return. Its `root_binding_mode` remains an
orchestration semantic check after a valid exact read because that field is
not reduced to a separate public read error.

No model, field, version, Result family, owner rule, or identity/hash formula
changes under Option A.

## Deterministic Algorithms

### Exact public observability

The current reader exposes this phase order:

```python
        try:
            value = cj1_decode(canonical_bytes)
            if not isinstance(value, dict):
                _fail("CORRUPT_IMMUTABLE_RECORD", identity)
            model = model_type(**value)
            validate_artifact(model, owner_bindings=owner_bindings)
        except (CJ1Error, CandidateValidationError, TypeError, ValueError) as exc:
            if isinstance(exc, CandidatePersistenceError):
                raise
            _fail("CORRUPT_IMMUTABLE_RECORD", f"{identity}:{exc}")
        actual_address = self._artifact_address(
            model, address.artifact_identity, address.artifact_digest
        )
```

Publicly observable immutable-read outcomes are:

| Public outcome | Orchestration class |
|---|---|
| `MISSING_IMMUTABLE_RECORD` | exact predecessor missing |
| `CORRUPT_IMMUTABLE_RECORD` | decode, construction, constant, owner, schema, content validation, or other pre-return invalidity collapsed by the reader |
| `ARTIFACT_ADDRESS_MISMATCH` | supplied address differs after successful model construction/validation |
| successful `(model, read_back)` | orchestration may evaluate remaining semantic bindings |

Orchestration SHALL branch on stable public error codes, not nested error
text. Unknown immutable-read failure codes fail closed into the applicable
corrupt class; they never fall through to effects.

### Selected Option A precedence

This table replaces only the G77-114 31-entry token table. It preserves all
successful-path checks and relative post-read authority order.

| Precedence | Observable condition | Stable orchestration token |
|---:|---|---|
| 1 | existing accepted tuple/type/durable/signature/finality/decision relation fails | existing Stage-4 token; no remapping |
| 2 | manifest pair is half, malformed, wrong domain, or inconsistent with exact commitment bytes | `MANIFEST_PAIR_MISMATCH` |
| 3 | public manifest read returns `MISSING_IMMUTABLE_RECORD` | `MANIFEST_MISSING` |
| 4 | public manifest read returns `CORRUPT_IMMUTABLE_RECORD` or another non-address pre-return invalidity | `MANIFEST_CORRUPT` |
| 5 | public manifest read returns `ARTIFACT_ADDRESS_MISMATCH` | `MANIFEST_CONTENT_ADDRESS_MISMATCH` |
| 6 | successfully returned manifest producing Capacity pair differs from `C_pair` | `MANIFEST_PRODUCING_CAPACITY_MISMATCH` |
| 7 | TargetV5 pair is half, malformed, wrong domain, or not the exact manifest pair | `TARGET_V5_PAIR_MISMATCH` |
| 8 | Capacity target pair differs from manifest TargetV5 pair | `CAPACITY_TARGET_V5_MISMATCH` |
| 9 | HumanDecision target pair differs from manifest TargetV5 pair | `HUMAN_DECISION_TARGET_V5_MISMATCH` |
| 10 | public TargetV5 read returns `MISSING_IMMUTABLE_RECORD` | `TARGET_V5_MISSING` |
| 11 | public TargetV5 read returns `CORRUPT_IMMUTABLE_RECORD` or another non-address pre-return invalidity | `TARGET_V5_CORRUPT` |
| 12 | public TargetV5 read returns `ARTIFACT_ADDRESS_MISMATCH` | `TARGET_V5_CONTENT_ADDRESS_MISMATCH` |
| 13 | successfully returned TargetV5 root-binding mode differs | `TARGET_V5_ROOT_BINDING_MODE_MISMATCH` |
| 14 | attempt kind is not `INITIAL_BEGIN` | `INITIAL_BEGIN_KIND_MISMATCH` |
| 15 | attempt sequence is not exactly one | `INITIAL_BEGIN_SEQUENCE_MISMATCH` |
| 16 | first forbidden predecessor/retry field in canonical field order is non-null | `INITIAL_BEGIN_PREDECESSOR_PRESENT` with field detail |
| 17 | TargetV5 founding-origin pointer pair is malformed/null | `AUTHORITATIVE_P_ROOT_INVALID` |
| 18 | supplied origin root identity/digest/generation differs from TargetV5 | `AUTHORITATIVE_ORIGIN_ROOT_MISMATCH` |
| 19 | ProofSet pointer differs | `PROOF_SET_AUTHORITATIVE_P_ROOT_MISMATCH` |
| 20 | Certification pointer differs | `CERTIFICATION_AUTHORITATIVE_P_ROOT_MISMATCH` |
| 21 | Transition pointer differs | `TRANSITION_AUTHORITATIVE_P_ROOT_MISMATCH` |
| 22 | terminal commitment pointer differs | `TERMINAL_COMMITMENT_AUTHORITATIVE_P_ROOT_MISMATCH` |
| 23 | resulting-root predecessor pointer differs | `RESULTING_ROOT_AUTHORITATIVE_P_ROOT_MISMATCH` |
| 24 | supplied SlotReadBack owner differs | `RETAINED_ROOT_OWNER_MISMATCH` |
| 25 | supplied SlotReadBack slot identity differs | `RETAINED_ROOT_IDENTITY_MISMATCH` |
| 26 | supplied SlotReadBack slot epoch differs | `RETAINED_ROOT_EPOCH_MISMATCH` |
| 27 | exact slot is missing, stale outside exact idempotency, divergent, corrupt, or history/root/store state mismatches | `RETAINED_ROOT_STATE_HISTORY_MISMATCH` with stable public lower-layer detail |

Removed as independent orchestration obligations:

- `MANIFEST_TYPE_VERSION_MISMATCH`;
- `MANIFEST_MAPPING_CONTRACT_MISMATCH`;
- `TARGET_V5_TYPE_VERSION_MISMATCH`; and
- `TARGET_V5_OWNER_MISMATCH`.

Their conditions remain rejected. They are absorbed by `MANIFEST_CORRUPT` or
`TARGET_V5_CORRUPT` because the public reader does not return an invalid model
for post-read classification.

### Multi-violation matrix

| Hostile bytes/history | First public observation | Option A token | Option B possible token | Option C consequence |
|---|---|---|---|---|
| canonical ManifestV2 field set, wrong mapping contract, simultaneous address/digest mismatch | construction fails; address phase not reached | `MANIFEST_CORRUPT` | structured surface could expose both and impose chosen order | duplicate reader would inspect raw bytes; rejected |
| wrong manifest mapping contract with otherwise matching address | construction fails | `MANIFEST_CORRUPT` | mapping-specific structured token possible | rejected duplicate validation |
| valid manifest model with supplied address mismatch | public address failure | `MANIFEST_CONTENT_ADDRESS_MISMATCH` | same | unnecessary raw path |
| canonical TargetV5 fields, wrong owner, simultaneous address mismatch | owner validation fails; address phase not reached | `TARGET_V5_CORRUPT` | structured surface could expose owner plus computed relation | rejected duplicate validation |
| wrong TargetV5 type/version plus address mismatch | construction fails | `TARGET_V5_CORRUPT` | type/version-specific structured token possible | rejected duplicate validation |
| valid TargetV5 with wrong root-binding mode and supplied address mismatch | address phase fails before post-read mode check | `TARGET_V5_CONTENT_ADDRESS_MISMATCH` | same | unnecessary raw path |
| valid exact-address TargetV5 with wrong root-binding mode | successful read, then semantic mismatch | `TARGET_V5_ROOT_BINDING_MODE_MISMATCH` | same | unnecessary raw path |

For every row and every option, the required safety disposition is:

```text
fixture_effect_sum = 0
new forward immutable writes = 0
CAS attempts = 0
terminal publications = 0
```

Option A produces that disposition using the existing public reader and the
earliest publicly observable class.

## Responsibility Boundaries

### Option A — selected

Option A revises only the contract taxonomy. Future orchestration maps stable
public reader codes and retains all authority/effect checks. Persistence owns
decode, construction, validation, and address verification. Validators own
model admissibility. No layer duplicates another.

Exact selected future implementation inventory, subject to independent
authorization:

| Path | Action | Responsibility |
|---|---|---|
| `aigol/runtime/candidate_h_founder/orchestration.py` | MODIFY | authority chain plus 27-entry observable token mapping before effects |
| `tests/test_g77_candidate_h_founder_authority.py` | MODIFY | manifest/Target observable-token matrix, authority attacks, zero-write/CAS/publication assertions |
| `tests/test_g77_candidate_h_founder_exhaustion.py` | MODIFY | concurrency/restart/effect-sum and unrelated-coordinate obligations |

Count: `0 CREATE / 3 MODIFY / 0 DELETE / 0 RENAME`.

No persistence test change is required because the public reader behavior is
reused, not changed.

### Option B — not selected

Option B would add one structured lower-layer failure-observability
capability. Minimum responsibility:

- expose a stable phase/category rather than nested exception prose;
- expose enough pre-construction address relation to distinguish a
  simultaneous mapping-constant and manifest digest/address mismatch; and
- preserve exact read, canonical validation, and fail-closed behavior.

Minimum future inventory:

| Path | Action |
|---|---|
| `aigol/runtime/candidate_h_founder/persistence.py` | MODIFY |
| `tests/test_g77_candidate_h_founder_persistence.py` | MODIFY |
| `aigol/runtime/candidate_h_founder/orchestration.py` | MODIFY |
| `tests/test_g77_candidate_h_founder_authority.py` | MODIFY |
| `tests/test_g77_candidate_h_founder_exhaustion.py` | MODIFY |

Count: `0 CREATE / 5 MODIFY / 0 DELETE / 0 RENAME`.

It changes public error compatibility and creates `NEW_CAPABILITY_COUNT = 1`.
If implemented as an enhancement of the same `read_immutable` path it need
not create a parallel reader; a second method/path would create one and is
not acceptable. Option B is unnecessary because the additional distinction
is diagnostic only.

### Option C — rejected

Option C would have orchestration read store files or private
`CandidateHStore` paths, decode CJ1, reconstruct records, or calculate
addresses independently. Even if nominally confined to the original three
files, it would create:

- a second immutable-read path;
- a second validation/address path;
- private persistence coupling;
- duplicated safety logic and drift risk; and
- a hidden new capability outside the declared inventory.

Its architectural cost is greater than Option B and it violates the G77-114
responsibility boundary. Diagnostic token preservation cannot justify it.

### Dependency DAG impact

```text
Option A:

orchestration
  -> CandidateHStore.read_immutable
       -> decode / construct / validate / address
  <- stable public success or error class
  -> deterministic token

no raw bytes / no private path / no second validator / no fallback

Option B:

orchestration -> enhanced structured public read capability
              -> persistence + persistence-test expansion

Option C:

orchestration -> private/raw store path
              -> duplicated decode/validation/address path  [REJECTED]
```

### Authority DAG impact

All options leave the authority chain unchanged:

```text
authenticated CommitmentV2
  -> exact ManifestV2
  -> exact root-custodian TargetV5
  -> authoritative P_root
  -> C_root_v1
  -> existing CAS

failure token -X-> authority
Replay -X-> authority
adapter -X-> authority
```

Option C nevertheless creates a competing evidence-validation path and is
rejected before it can become an authority ambiguity.

### Topology by option

| Measure | Current | Option A | Option B | Option C |
|---|---:|---:|---:|---:|
| production paths | 1 | 1 | 1 | 1 claimed, but hidden read path added |
| parallel production paths | 0 | 0 | 0 if same public read is enhanced | read/validation path becomes 1 |
| Human entries | 1 | 1 | 1 | 1 |
| root paths | 1 | 1 | 1 | 1 |
| persistent Founder authorities | 0 | 0 | 0 | 0 |
| immutable-read paths | 1 | 1 | 1 if enhanced in place | 2 |
| validator paths | 1 | 1 | 1 | 2 |
| new capability count | 0 | 0 | 1 | at least 1 hidden duplicate |

No option requires an alternate authority path, fallback, adapter authority,
or Replay authority. Option C creates an impermissible parallel evidence
path and is not viable.

### Replay assessment

- Replay does not select, repair, reinterpret, or classify the live
  predecessor read;
- missing/invalid exact bytes fail closed rather than being recovered by
  resemblance or history;
- no Option A Replay change is required;
- Option B also cannot justify Replay involvement; and
- Option C may not use Replay as a raw-byte or fallback source.

### Authenticated repository evidence

| Evidence | Value |
|---|---|
| HEAD | `6ddd7e1fdc37bba98c26ba43120deab5eae178f7` |
| tree | `7d1835eb30390bed77bd2c66a12a7a59ce4853ed` |
| subject | `G77-115 block Stage 5 repair on immutable-read observability` |
| G77-115 tracked/current commit | `6ddd7e1fdc37bba98c26ba43120deab5eae178f7` |
| worktree before G77-116 | clean |
| required ancestry | G77-99 through G77-115 current commits are ancestors of HEAD |

Authenticated SHA-256 inventory:

| Artifact | SHA-256 |
|---|---|
| G48-00 | `16508d1a77c4b3f07d37861e74d85f77896be16da01ca26cbc07a658ddf2c0eb` |
| HFD-04 Revision 2 | `5030cd2d90cbb792fa3ee3ed2777057ad269619b091b344b390e8d6247d85eb5` |
| G77-62 | `661394be4e32b2e965f6a906e865a78128572084bbe52c5d0aad3bfdd5deca1e` |
| G77-64 | `ac3deaf40e7f06c04e3396b161194b258b7ae993b65d9ee719fb1170fc4ac0c6` |
| G77-85 | `e86c819491ff3ace2a03a1fd6674ac215a1ba8035a756bbe3edc37c7dd34a286` |
| G77-86 | `df11f66fee97115baf9c884e7cac555b9feefc8c4de888adc721e0d37789228f` |
| G77-99 | `a8a8c803e6c28310ee6536f11e5ae9163fbe5c4d853369e3e76fa50e4f473ca8` |
| G77-100 | `722a512a57532a116b7f106af1f741b802e67bc6bd89902f7e4beb917ecb7b4d` |
| G77-101 | `0915e645f87b8c1e39ce09f35d7c017a918dcbe8b6ef85cce69677640c9da3d6` |
| G77-102 | `8174631187dabfa29516b901fa85239601454cb5d25d124571adf267b4522b3e` |
| G77-103 | `6adbddc6b94ee38d67fa7d1df4d3cad81cc812b7d848e2918cdccc43f18c7286` |
| G77-104 | `c7bb28c0f4bb51a33c459c182b1c84ba5bc35b033f0bd4cdd38e1da9f3284756` |
| G77-105 | `852a8793746ac7a065872d2b5a7da31112cf3847213eb0d2c5e6bec471c320e2` |
| G77-106 | `07be4809f17431b73ef6bb790b722b27615e1b45274500da693a9c0d5d0084e9` |
| G77-107 | `15ffde9c34d03d8cbc65369b443957ace04fdf40d67daf87c48695a8227f8a4b` |
| G77-108 | `d59ddb65c7828cb15e70c5e3f93d96899c5cf56f40fce9b5d871023eaef42cab` |
| G77-109 | `4ad304e63823cb0ab3c9ae2c376f03d2b5da460d70029a9214affe3eb5f6255e` |
| G77-110 | `c8876243d7c6b7721d4b41f46fd6d9ff9876dbc456c9b3e6c1d3c75ec94a9a1d` |
| G77-111 | `b718585f50f10a683fe78336c773fbc7714426a1c7a1624201c71f736743f15f` |
| G77-112 | `6c691a53a1255c50a096e9a631e52bd89274beaa6f42ee47d3e7761ba4b777ae` |
| G77-113 | `6b63b850d4e591f26d5294ea6d8ffffd503f220f1dbee84facf622bfee868d0a` |
| G77-114 | `e9314b390b36fd9ebcda61e3981e188ce2d47dbd40b055f8f6d193b145024080` |
| G77-115 | `e803a11d92468e211db857cdb0231f89d9c0845de709c55ac7f05de3a271fdd2` |
| `models.py` | `ae5ebacd647591f59bf85bf3bf6d4bd6817306fd0caa4c03b5c56f9bb5e6b79a` |
| `validators.py` | `6b5ed7f676a8a1157731289629d941fbd867ff73caf7731813a607b5e04890ab` |
| `persistence.py` | `1a1b6d72c8d335c2151b904684a0dd5aed7b449e92fc07bb55363859264fe610` |
| `authentication.py` | `667a95c3c458a891b08ef49ece81469f540ec6b3903e26f9d8e0896e3163c0c5` |
| `orchestration.py` | `71000ca4e21616e13b7b8bb89f97c3ea7cd7ef6cf99ba2097c3f18526a11ed18` |
| authority test | `7b0eacf419e94ecabfd08adbc0725db5b129fc1ed8b7ad5458608e578fc5a0a2` |
| exhaustion test | `4f922a4834957660508a6f88ad0bdc1f71d5485b7b1cc4a5edc09015819b2bf8` |
| persistence test | `2005bc7dc7369eeb809426cca164650836819997176daab8b8d2b589cadc0517` |

The final SHA-256 of this G77-116 artifact cannot be embedded in its own
bytes without changing the hash. It is reported in the final handoff.

# 3. Constitutional Self-Assessment

## Verified

- G77-115 is committed and the pre-G77-116 worktree was clean.
- Required hashes and G77-99 through G77-115 ancestry authenticate.
- G77-115 B01 is reproduced directly from the current public reader/model
  order.
- The G77-114 authority chain remains independently sufficient and is not
  reopened.
- Failure-token specificity is diagnostic and does not carry authority.
- Every collapsed Option A class remains fail-closed before effects.
- Option A uses only public stable reader error codes.
- Option A does not require raw bytes, nested-error parsing, private calls,
  scan, fallback, Replay, adapter authority, or another validator path.
- Option A restores the future `0 CREATE / 3 MODIFY / 0 DELETE / 0 RENAME`
  inventory with `NEW_CAPABILITY_COUNT = 0`.
- Option B is technically possible but broader and unnecessary.
- Option C violates responsibility separation and is rejected.
- No runtime/test code, Human act, BEGIN, activation, deployment, Stage 6,
  production mutation, or commit occurred.

## Not Verified

- Option A is not implemented.
- The future 27-entry orchestration mapping and hostile tests have not run.
- No implementation authorization or post-implementation certification is
  granted by this alternatives assessment.
- Option B's exact API design is intentionally not frozen because Option B
  is not constitutionally necessary.
- Automated adversarial certification and constitutional pattern promotion
  remain deferred.

## Constitutional Health Evidence

| Measure | Assessment |
|---|---|
| originating defect | G77-114 promised manifest failure precedence not observable through the certified public read |
| fail-closed effectiveness | `YES`; every candidate history already rejects before effects |
| constitutional gap | `NO` |
| contract gap | `YES`; closed by selected Option A observable taxonomy model, pending successor implementation authorization |
| implementation defect | `NO_CURRENT_IMPLEMENTATION`; G77-114 remains unauthorized |
| architectural redesign required | `NO` |
| certified capability failure | `NO`; public immutable read behaves correctly and fail-closed |
| incorrect reuse binding | `YES` only in G77-114's diagnostic observability assumption |
| authority reuse integrity | `PASS` |
| failure-observability reuse integrity | `PASS` under selected Option A; only public outcomes are promised |
| diagnostic-specificity pressure | `YES`; rejected as insufficient reason for a new capability |
| topology expansion required | `NO` |
| authority expansion required | `NO` |
| Result-family expansion required | `NO` |
| persistence-family expansion required | Option A `NO`; Option B `YES`; Option C hidden duplicate `YES` |
| new capability count per option | A `0`; B `1`; C `>=1` hidden duplicate |
| production paths | `1 -> 1` |
| parallel production paths | `0 -> 0` under selected Option A |
| Human entries | `1 -> 1` |
| root paths | `1 -> 1` |
| persistent Founder authorities | `0 -> 0` |
| repeated defect class | `CONTRACT_REQUIRES_FAILURE_DISTINCTION_NOT_OBSERVABLE_THROUGH_CERTIFIED_PUBLIC_SURFACE` |
| constitutional pattern candidate status | recorded; not promoted |

No synthetic health score is created.

## Reuse Impact Assessment

1. **Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?**

   Existing CJ1 decoding, canonical model construction, validators, exact
   immutable read/address verification, stable persistence errors, Candidate
   H authority chain, Identity DAG, immutable writes, one-winner CAS, and the
   two Stage-5 test surfaces are reused.

2. **Katere nove zmogljivosti (če sploh) nastanejo?**

   Under selected Option A, none. Option B would create one structured public
   failure-observability capability. Option C would create at least one hidden
   duplicate reader/validator capability and is prohibited.

3. **Ali katera obstoječa zmogljivost postane nedosegljiva?**

   No. Specific unobservable diagnostic labels cease to be contractual
   obligations; the underlying invalid conditions remain rejected.

4. **Ali implementacija ustvarja vzporedni tok?**

   Option A does not. Option B need not if it enhances the same read path.
   Option C does and is rejected.

5. **Ali zmanjšuje ali povečuje število produkcijskih poti?**

   Neither. Production paths remain `1 -> 1`.

6. **Ali je authority reuse še vedno pravilno vezan?**

   Yes. It remains bound through CommitmentV2, ManifestV2, root-custodian
   TargetV5, authoritative `P_root`, and `C_root_v1` before effects.

7. **Ali B01 zahteva replacement capability?**

   No. B01 is closed by matching the token contract to the existing public
   surface. Replacement or expansion is unnecessary.

8. **Ali lahko contract-only closure ohrani NEW_CAPABILITY_COUNT = 0?**

   Yes. Selected Option A preserves `NEW_CAPABILITY_COUNT = 0`.

Controlling reuse-first answer:

`CAN B01 BE CLOSED WITHOUT A NEW CAPABILITY? YES.`

## Pattern Evidence

Candidate pattern:

`CONTRACT_REQUIRES_FAILURE_DISTINCTION_NOT_OBSERVABLE_THROUGH_CERTIFIED_PUBLIC_SURFACE`

G77-115 provides one verified instance. The pressure can recur whenever a
higher layer specifies semantic sub-failures hidden behind a fail-closed
public boundary, but recurrence sufficient for constitutional promotion is
not established here. The bounded lesson is evidence only: specify tokens at
the public capability boundary unless additional observability is itself a
justified capability.

```text
PATTERN_DETECTED != CONSTITUTION_CHANGED
```

No constitutional promotion occurs.

## Deferred Capability Evidence

The following remain deferred and unimplemented:

- `AUTOMATED_INDEPENDENT_ADVERSARIAL_CERTIFICATION`; and
- `CONSTITUTIONAL_PATTERN_LEARNING_AND_PROMOTION`.

No detected pattern changes the constitution, grants implementation
authority, or bypasses the future autonomous-domain fail-closed gate.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| committed G77-115 baseline | HEAD/tree/path log | repository authentication | `PASS` |
| clean pre-assessment worktree | empty porcelain status | repository authentication | `PASS` |
| required SHA-256 inventory | exact table above | `sha256sum` | `PASS` |
| G77-99 through G77-115 ancestry | per-path current commits | `git merge-base --is-ancestor` | `PASS` |
| exact B01 reconstruction | model constructor and public reader order | static code-path review | `PASS` |
| G77-115 verified authority results preserved | no contradictory code/contract evidence | bounded hostile review | `PASS` |
| safety distinguished from diagnostics | zero-effect disposition independent of specific token | constitutional analysis | `PASS` |
| Option A deterministic | stable public code-to-token mapping | phase analysis | `PASS` |
| Option A fail-closed | all read failures terminate before effects | effect-boundary review | `PASS` |
| manifest multi-violation closed | wrong mapping + address mismatch -> public corrupt | hostile trace | `PASS` |
| TargetV5 equivalents closed | owner/type/address and root-mode/address cases | hostile trace | `PASS` |
| Option A no private/raw access | public API and dependency DAG | boundary review | `PASS` |
| Option A no new capability | existing public read and same three consumers | reuse-first review | `PASS` |
| Option B necessity | safety already satisfied by Option A | alternatives review | `NOT_APPLICABLE` |
| Option C rejection | duplicate read/validation path is constitutionally prohibited | architecture review | `PASS` |
| selected inventory restored | exact three paths above | inventory review | `PASS` |
| topology/authority preserved | option and DAG tables | constitutional review | `PASS` |
| Replay remains non-authoritative | no Replay edge | dependency review | `PASS` |
| implementation | prohibited in G77-116 | not executed | `NOT_APPLICABLE` |
| whitespace and single mutation | G77-116 artifact | `git diff --no-index --check` and status review | `PASS` |

Option C's rejection is a passed alternatives-assessment requirement. No
mandatory selected-option criterion is failed, blocked, or not run.

# 5. Repository Mutation Summary

Created files:

- `docs/governance/G77_116_CANDIDATE_H_STAGE_5_MANIFEST_FAILURE_OBSERVABILITY_PRECEDENCE_MINIMAL_CONSTITUTIONAL_CLOSURE_ALTERNATIVES_ASSESSMENT_V1.md`
  — this alternatives assessment only.

Current G77-116 mutation count:

```text
1 CREATE
0 MODIFY
0 DELETE
0 RENAME
```

Selected future Option A inventory, subject to independent authorization:

```text
0 CREATE
3 MODIFY
0 DELETE
0 RENAME
```

MODIFY only:

- `aigol/runtime/candidate_h_founder/orchestration.py`;
- `tests/test_g77_candidate_h_founder_authority.py`; and
- `tests/test_g77_candidate_h_founder_exhaustion.py`.

No fourth path is required or authorized by selected Option A.

Unchanged subsystems:

- `models.py`, `validators.py`, `persistence.py`, `authentication.py`,
  `cj1.py`, and `__init__.py`;
- ResultV2, Replay, CRO, CLIA, root-owner families, identity/hash formulas,
  and all production surfaces; and
- every predecessor through committed G77-115.

API compatibility:

- Option A preserves the existing runtime API and public persistence error
  surface. It revises only the future orchestration token contract.

Boundary preservation:

- no runtime/test modification, implementation, Stage 6, Human act,
  signature, BEGIN, root mutation, adoption, activation, deployment,
  production authority, or production mutation;
- no pattern promotion or autonomous capability; and
- no commit.

Unrelated pre-existing changes:

- None. The worktree was clean before this artifact was created.

# 6. Certification Verdict

G77_STAGE_5_MANIFEST_FAILURE_OBSERVABILITY_MINIMAL_CLOSURE_MODEL_ESTABLISHED
