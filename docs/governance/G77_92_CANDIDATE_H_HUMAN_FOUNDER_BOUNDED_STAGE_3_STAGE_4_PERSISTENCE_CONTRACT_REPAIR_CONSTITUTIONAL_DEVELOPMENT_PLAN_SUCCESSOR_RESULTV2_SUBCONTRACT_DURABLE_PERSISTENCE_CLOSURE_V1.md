# 1. Implementation Summary

Generation: G77-92

Report identity:
`G77_92_CANDIDATE_H_HUMAN_FOUNDER_BOUNDED_STAGE_3_STAGE_4_PERSISTENCE_CONTRACT_REPAIR_CONSTITUTIONAL_DEVELOPMENT_PLAN_SUCCESSOR_RESULTV2_SUBCONTRACT_DURABLE_PERSISTENCE_CLOSURE_V1`

Reporting date: 2026-08-10

Classification: `BOUNDED_CDP_SUCCESSOR / NON_IMPLEMENTING / NON_ACTIVATING`.

Authenticated repository baseline:

- HEAD: `edca85e683236ebfd473e12c28918cff34865957`
- tree: `cc18638ccb84add7ca3c4d8e729750d01df43814`
- initial worktree: clean

Implementation contracts: G77-73 authentication Revision 3, G77-77 exact
same-tuple continuation, G77-85 bounded CDP Revision 4, G77-86 independent
authorization of that predecessor CDP, committed Stage-3 evidence G77-89,
fail-closed Stage-4 attempt G77-90, and G77-91 Option-C repair assessment.

Objective:

Freeze the minimum successor development plan that permits a future,
separately authorized implementation to add closed ResultV2-subcontract
durability to the existing `CandidateHStore`, then resume only the originally
bounded fixture Stage 4. This plan closes the inventory and API mismatch that
caused `G77_90_B01_STAGE_3_CAS_CANNOT_PERSIST_G77_73_PRE_SIGN_ACCEPTANCE_SUBCONTRACT`.

Implementation scope authorized for a future assessment, but not by this
artifact itself:

- modify the existing Candidate store and its Stage-3 test;
- create the previously planned fixture authentication module and retry test;
- reuse one record directory, one slot-generation directory, one current-slot
  directory, one lock directory, and the existing immutable/CAS engines;
- persist nine closed, semantically prevalidated ResultV2 subcontracts;
- expose exact historical slot-generation read-back; and
- stop after complete durable ResultV2 construction/read-back, before
  HumanDecision, orchestration, BEGIN, root mutation, activation or production
  effect.

No runtime or test implementation is performed in G77-92. This CDP grants no
implementation authority. An independent implementation-authorization
assessment SHALL authenticate this artifact and authorize the exact inventory
before either MODIFY or CREATE path is touched.

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

G77-86 authorized the earlier G77-85 inventory; it does not authorize this
successor. G77-91 selected the repair model; it did not authorize code. The
future authorization subject is exactly this G77-92 plan.

## Exact Future File Inventory

| Path | Action | Closed responsibility |
|---|---|---|
| `aigol/runtime/candidate_h_founder/persistence.py` | `MODIFY` | closed nine-kind subcontract address/write/read/CAS, historical generation read, shared-engine refactor only |
| `tests/test_g77_candidate_h_founder_persistence.py` | `MODIFY` | persistence compatibility, exact address/bytes, closed-kind/mode rejection, shared-path, history, crash and corruption proofs |
| `aigol/runtime/candidate_h_founder/authentication.py` | `CREATE` | exact nine subcontract schemas/equality, fixture-only Ed25519, durable-before-signing order, G77-77 continuation, complete ResultV2 |
| `tests/test_g77_candidate_h_founder_retry.py` | `CREATE` | positive/negative cryptographic vectors, exact tuple, restart, non-multiplication, terminal read-only and ResultV2 proofs |

Future bounded count: `2 MODIFY`, `2 CREATE`, `0 DELETE`, `0 RENAME`.

The following remain `REUSE_UNCHANGED`:

- `aigol/runtime/candidate_h_founder/__init__.py`;
- `aigol/runtime/candidate_h_founder/cj1.py`;
- `aigol/runtime/candidate_h_founder/models.py`;
- `aigol/runtime/candidate_h_founder/validators.py`;
- `tests/test_g77_candidate_h_founder_cj1.py`;
- `tests/test_g77_candidate_h_founder_models.py`;
- `tests/test_g76_g77_candidate_h_identity_dag.py`;
- `tests/test_g77_candidate_h_founder_validators.py`; and
- all thirteen G77-85 `REUSE_UNCHANGED` runtime paths, including HIC/CHE,
  session/transport/presentation, both legacy governance CLIs, generic Replay,
  both non-Candidate serializers, CRO query and CRO topology.

No other runtime, test, package-export, orchestration, Replay, CRO, CLIA,
root, activation, deployment or production path may change. Discovery of an
unavoidable fifth path is a STOP condition, not implicit scope expansion.

# 2. Code Evidence

## Public API

The future `persistence.py` change SHALL add exactly these frozen operational
views and methods. Ellipses indicate implementation bodies only; parameters,
defaults and return types are fixed.

```python
@dataclass(frozen=True, slots=True)
class SubcontractAddress:
    subcontract_kind: str
    identity: str
    digest: str

@dataclass(frozen=True, slots=True)
class SubcontractReadBack:
    address: SubcontractAddress
    storage_digest: str
    canonical_bytes: bytes

@dataclass(frozen=True, slots=True)
class SubcontractWriteResult:
    outcome: str
    read_back: SubcontractReadBack

class CandidateHStore:
    def write_subcontract(
        self,
        address: SubcontractAddress,
        canonical_bytes: bytes,
        *,
        _fixture_crash_hook: CrashHook | None = None,
    ) -> SubcontractWriteResult: ...

    def read_subcontract(
        self,
        address: SubcontractAddress,
    ) -> SubcontractReadBack: ...

    def compare_and_swap_subcontract(
        self,
        *,
        owner: str,
        slot_identity: str,
        slot_epoch: object,
        expected_slot_digest: str | None,
        expected_status: str | None,
        successor_status: str,
        address: SubcontractAddress,
        canonical_bytes: bytes,
        logical_instant: str,
        _fixture_crash_hook: CrashHook | None = None,
    ) -> CompareAndSwapResult: ...

    def read_slot_generation(
        self,
        owner: str,
        slot_identity: str,
        slot_epoch: object,
        generation: int,
        slot_digest: str,
    ) -> SlotReadBack: ...
```

`CandidateHReadOnlyStore` SHALL add exactly:

```python
def read_subcontract(
    self,
    address: SubcontractAddress,
) -> SubcontractReadBack: ...

def read_slot_generation(
    self,
    owner: str,
    slot_identity: str,
    slot_epoch: object,
    generation: int,
    slot_digest: str,
) -> SlotReadBack: ...
```

Its existing `read_immutable` and `read_slot` methods remain. It SHALL expose
no write, CAS, validator callback, repair, signer, key, clock or orchestration
method.

The direct-module `persistence.__all__` SHALL add only
`SUBCONTRACT_KIND_SPECS`, `SubcontractAddress`, `SubcontractReadBack`, and
`SubcontractWriteResult`. Package `__init__.py` remains byte-unchanged; no
package-level export or alternate import surface is created.

## Orchestration Entry Point

This repair creates no orchestration entry point. The future authentication
module is called only by a separately authorized later Candidate fixture
orchestrator. Its sole forward reduction is:

```text
validated CapacityV2 + exact HFD act/review/manifest/P_auth_v2
-> operation immutable/read-back
-> outer OPEN -> AUTHENTICATING claim CAS/read-back
-> signer intent immutable/read-back
-> signer AVAILABLE -> ACCEPTED_IN_PROGRESS CAS/read-back
-> invocation receipt immutable/read-back
-> fixture signer-owned same-operation continuation
-> signer terminal outcome CAS/read-back
-> signer outcome read-back immutable/read-back
-> outer AUTHENTICATING -> terminal CAS/read-back
-> authoritative outer read-back immutable/read-back
-> complete Stage-2-validated ResultV2 immutable/read-back
-> STOP
```

There is no direct signer-call API. The authentication module SHALL obtain a
`CandidateHStore` explicitly, use only its public methods, and call the
fixture primitive only inside the accepted-receipt continuation. It SHALL not
construct a store, select a root, invoke a Human interface, or import
orchestration, Replay, CRO, CLIA, BEGIN or root machinery.

## Semantic Reductions

The closed storage reduction is exact:

```text
authentication semantic validator accepts exact body
-> B = cj1_encode(body)
-> H = SHA256(B), lowercase hexadecimal
-> SubcontractAddress(kind, prefix + ":" + H, "sha256:" + H)
-> store independently decodes B and requires cj1_encode(decoded) == B
-> store requires one object, closed kind/mode, exact prefix, identity and digest
-> existing _record_path(identity)
-> existing _publish_immutable_bytes
-> exact read_subcontract(address)
-> byte equality before success
```

`canonical_bytes` are the exact CJ1 encoding of the displayed subcontract
body, with no envelope, storage wrapper, retry tuple, callback-produced view,
normalization or second serializer. `storage_digest` equals
`sha256:SHA256(canonical_bytes)` and therefore equals `address.digest`; the
field is retained to match existing mechanical slot linkage.

CAS uses the same lock, generation, pointer and record publisher as
`compare_and_swap`. The refactor SHALL extract one private shared engine that
accepts only an already checked address and bytes. Both model CAS and
subcontract CAS enter that engine after their distinct public validation.
Neither public method may call the other through a fake model or opaque-byte
bypass.

Historical read reduction is exact:

```text
explicit owner + slot_identity + slot_epoch + generation + slot_digest
-> existing _slot_key and exact _generation_path
-> exact file read; no directory scan and no current-pointer inference
-> recompute slot_digest and bind all five supplied coordinates
-> resolve referenced record at exact artifact_identity
-> recompute artifact_storage_digest
-> return SlotReadBack even when current pointer has advanced
```

Missing, malformed, corrupt, misbound or digest-mismatched history fails
closed. An unreferenced generation file is not made authoritative merely by
existence; a caller must supply its exact digest from an already persisted
receipt/read-back predecessor.

## Public Validators

Authentication semantics and persistence mechanics remain separate.

`authentication.py` SHALL validate before every store call:

- exact ordered field set for the selected kind;
- all fixed constants and conditional null rules;
- all identity/digest pairs together and against resolved exact bytes;
- owner, actor, capacity, operation, claim, message, key, slot, epoch,
  sequence, status and logical-instant equality;
- the complete G77-77 accepted tuple by resolved-byte equality;
- Ed25519 pure direct-message mode, strict key/signature encoding and
  deterministic verification; and
- forward-only state and predecessor bindings.

`persistence.py` SHALL independently validate:

- `SubcontractAddress` exact type and three nonempty fields;
- bytes input, strict CJ1 decode, canonical re-encode equality and object root;
- membership in the closed kind map and correct IMMUTABLE/CAS use;
- exact prefix, lowercase 64-hex identity suffix and `sha256:` digest;
- equality of both address hashes to SHA-256 of the exact bytes; and
- immutable record/read-back or generation/address/storage-digest equality.

No callback-based validation, wildcard kind, caller prefix, inferred kind,
generic opaque bytes, unchecked private helper access, schema registration in
`models.py`, or weakening of Stage-2 `validate_artifact` is permitted.

Stable new persistence error allocation is exact:

| Condition | Code |
|---|---|
| unknown kind | `UNKNOWN_SUBCONTRACT_KIND` |
| immutable kind sent to CAS or CAS kind sent to immutable write | `SUBCONTRACT_MODE_MISMATCH` |
| wrong address type/field type, nonbytes, nonobject, invalid or noncanonical CJ1 | `INVALID_SUBCONTRACT_INPUT` |
| wrong prefix, suffix, digest format or content hash | `SUBCONTRACT_ADDRESS_MISMATCH` |

Existing errors remain authoritative for storage effects:
`IMMUTABLE_RECORD_CONFLICT`, `MISSING_IMMUTABLE_RECORD`,
`CORRUPT_IMMUTABLE_RECORD`, `INVALID_EXPECTED_SLOT`,
`CAS_CONFLICT_WITH_ABSENT_SLOT`, `CORRUPT_SLOT_POINTER`, `CORRUPT_SLOT`,
`PARTIAL_SLOT`, `SLOT_BINDING_MISMATCH`, `SLOT_ARTIFACT_MISMATCH`,
`WRITE_READ_BACK_MISMATCH`, `DURABLE_WRITE_FAILED`, and
`UNSAFE_STORE_PATH`.

The authentication module SHALL define one stable
`CandidateAuthenticationError(code, detail)` and use only:
`SUBCONTRACT_SCHEMA_MISMATCH`, `SUBCONTRACT_CONSTANT_MISMATCH`,
`SUBCONTRACT_PAIR_MISMATCH`, `SUBCONTRACT_STATE_MISMATCH`,
`RETRY_TUPLE_MISMATCH`, `DURABLE_ACCEPTANCE_REQUIRED`,
`FIXTURE_KEY_MISMATCH`, and `RESULTV2_CONSTRUCTION_MISMATCH`. None authorizes
retry, signing, Human selection or repair.

## Canonical Data Models

No new `FrozenCanonicalModel`, `MODEL_REGISTRY` row,
`NESTED_RECORD_SCHEMAS` row, artifact family, artifact version, owner,
metadata envelope or ResultV3 is permitted. The following ordered bodies are
subcontracts inside existing ResultV2 responsibility. Each `*_pair` below is
two adjacent fields named `*_identity`, `*_digest`.

| Kind / mode / prefix | Exact ordered semantic body |
|---|---|
| `AUTHENTICATION_OPERATION_V1` / IMMUTABLE / `human-founder-auth-operation-v1` | `external_premise_pair`; `human_founder_capacity_pair`; `human_actor_identity`; `human_authentication_slot_identity`; `human_authentication_epoch`; `authentication_sequence=1`; `authentication_commitment_pair`; `authenticated_message_representation=EXACT_UTF8_CJ1_P_AUTH_V2_BYTES`; `authenticated_message_digest`; `signature_scheme=ED25519_RFC8032_PURE`; `signature_key_identity`; `predecessor_authentication_slot_status=OPEN` |
| `AUTHENTICATION_CLAIM_CAS_V1` / CAS / `human-founder-auth-claim-cas-v1` | `authentication_operation_pair`; authentication slot/epoch; `authentication_sequence=1`; capacity pair; predecessor `OPEN`; successor `AUTHENTICATING`; `one_use_claim_token_pair`; `claim_logical_instant` |
| `SIGNER_INVOCATION_INTENT_V1` / IMMUTABLE / `human-founder-signer-intent-v1` | external Premise pair; CapacityV2 pair; actor; operation pair; claim pair; commitment pair; message representation/digest; scheme/key identity; signer slot/epoch; `authentication_sequence=1`; `maximum_logical_signer_invocations=1` |
| `SIGNER_ACCEPTANCE_CAS_V1` / CAS / `human-founder-signer-acceptance-cas-v1` | intent pair; operation pair; claim pair; capacity pair; message representation/digest; scheme/key identity; signer slot/epoch; predecessor `AVAILABLE`; successor `ACCEPTED_IN_PROGRESS`; `invocation_sequence=1`; `maximum_logical_signer_invocations=1`; `acceptance_logical_instant` |
| `SIGNER_INVOCATION_RECEIPT_V1` / IMMUTABLE / `human-founder-signer-invocation-receipt-v1` | acceptance pair; intent pair; operation pair; claim pair; signer slot/epoch; `invocation_sequence=1`; status `ACCEPTED_IN_PROGRESS`; `acceptance_logical_instant`; `accepted_slot_digest` |
| `SIGNER_OUTCOME_V1` / CAS / `human-founder-signer-outcome-v1` | intent pair; acceptance pair; receipt pair; operation pair; claim pair; capacity pair; commitment pair; message representation/digest; scheme/key identity; closed outcome status; conditional signature/signature digest; verification result; conditional closed failure code; `completion_logical_instant`; `terminal=true` |
| `SIGNER_OUTCOME_READ_BACK_V1` / IMMUTABLE / `human-founder-signer-outcome-readback-v1` | outcome pair; accepted receipt pair; signer slot/epoch; `invocation_sequence=1`; terminal signer status; conditional signature digest; `completion_logical_instant`; `terminal_signer_slot_digest` |
| `AUTHENTICATION_TERMINAL_CAS_V1` / CAS / `human-founder-auth-terminal-cas-v1` | operation pair; claim pair; signer outcome read-back pair; predecessor `AUTHENTICATING`; selected terminal authentication status/result; conditional signature/signature digest; verification result; one-use/non-equivocation proof pair; conflict status; `capacity_permanently_exhausted=true`; `completion_logical_instant` |
| `AUTHENTICATION_AUTHORITATIVE_READ_BACK_V1` / IMMUTABLE / `human-founder-auth-readback-v1` | terminal CAS pair; authentication slot/epoch; `authentication_sequence=1`; capacity pair; operation pair; terminal authentication status/result; conditional signature digest; `completion_logical_instant`; `read_back_authentication_slot_digest` |

This table is the closed `SUBCONTRACT_KIND_SPECS` map. It has exactly nine
entries and records mode and prefix. Field spelling in code SHALL use the
corresponding explicit snake-case names already present in ResultV2 and the
G77-71/G77-73 bodies; pair shorthand is prohibited in serialized bytes.

The normative ordered field expansion is exact:

```text
AUTHENTICATION_OPERATION_V1 = (
  external_premise_identity, external_premise_digest,
  human_founder_capacity_identity, human_founder_capacity_digest,
  human_actor_identity, human_authentication_slot_identity,
  human_authentication_epoch, authentication_sequence,
  authentication_commitment_identity, authentication_commitment_digest,
  authenticated_message_representation, authenticated_message_digest,
  signature_scheme, signature_key_identity,
  predecessor_authentication_slot_status
)

AUTHENTICATION_CLAIM_CAS_V1 = (
  authentication_operation_identity, authentication_operation_digest,
  human_authentication_slot_identity, human_authentication_epoch,
  authentication_sequence, human_founder_capacity_identity,
  human_founder_capacity_digest, predecessor_authentication_slot_status,
  claimed_authentication_slot_status, one_use_claim_token_identity,
  one_use_claim_token_digest, claim_logical_instant
)

SIGNER_INVOCATION_INTENT_V1 = (
  external_premise_identity, external_premise_digest,
  human_founder_capacity_identity, human_founder_capacity_digest,
  human_actor_identity, authentication_operation_identity,
  authentication_operation_digest, authentication_claim_cas_identity,
  authentication_claim_cas_digest, authentication_commitment_identity,
  authentication_commitment_digest, authenticated_message_representation,
  authenticated_message_digest, signature_scheme, signature_key_identity,
  signer_operation_slot_identity, signer_operation_slot_epoch,
  authentication_sequence, maximum_logical_signer_invocations
)

SIGNER_ACCEPTANCE_CAS_V1 = (
  signer_invocation_intent_identity, signer_invocation_intent_digest,
  authentication_operation_identity, authentication_operation_digest,
  authentication_claim_cas_identity, authentication_claim_cas_digest,
  human_founder_capacity_identity, human_founder_capacity_digest,
  authenticated_message_representation, authenticated_message_digest,
  signature_scheme, signature_key_identity, signer_operation_slot_identity,
  signer_operation_slot_epoch, predecessor_signer_slot_status,
  accepted_signer_slot_status, invocation_sequence,
  maximum_logical_signer_invocations, acceptance_logical_instant
)

SIGNER_INVOCATION_RECEIPT_V1 = (
  signer_acceptance_cas_identity, signer_acceptance_cas_digest,
  signer_invocation_intent_identity, signer_invocation_intent_digest,
  authentication_operation_identity, authentication_operation_digest,
  authentication_claim_cas_identity, authentication_claim_cas_digest,
  signer_operation_slot_identity, signer_operation_slot_epoch,
  invocation_sequence, signer_operation_status,
  acceptance_logical_instant, accepted_slot_digest
)

SIGNER_OUTCOME_V1 = (
  signer_invocation_intent_identity, signer_invocation_intent_digest,
  signer_acceptance_cas_identity, signer_acceptance_cas_digest,
  signer_invocation_receipt_identity, signer_invocation_receipt_digest,
  authentication_operation_identity, authentication_operation_digest,
  authentication_claim_cas_identity, authentication_claim_cas_digest,
  human_founder_capacity_identity, human_founder_capacity_digest,
  authentication_commitment_identity, authentication_commitment_digest,
  authenticated_message_representation, authenticated_message_digest,
  signature_scheme, signature_key_identity, outcome_status, signature,
  signature_digest, verification_result, failure_code,
  completion_logical_instant, terminal
)

SIGNER_OUTCOME_READ_BACK_V1 = (
  signer_outcome_identity, signer_outcome_digest,
  signer_invocation_receipt_identity, signer_invocation_receipt_digest,
  signer_operation_slot_identity, signer_operation_slot_epoch,
  invocation_sequence, signer_outcome_status, signature_digest,
  completion_logical_instant, terminal_signer_slot_digest
)

AUTHENTICATION_TERMINAL_CAS_V1 = (
  authentication_operation_identity, authentication_operation_digest,
  authentication_claim_cas_identity, authentication_claim_cas_digest,
  signer_outcome_read_back_identity, signer_outcome_read_back_digest,
  predecessor_authentication_slot_status,
  terminal_authentication_slot_status, authentication_result, signature,
  signature_verification_result,
  one_use_non_equivocation_proof_identity,
  one_use_non_equivocation_proof_digest, conflict_status,
  capacity_permanently_exhausted, completion_logical_instant
)

AUTHENTICATION_AUTHORITATIVE_READ_BACK_V1 = (
  authentication_terminal_cas_identity, authentication_terminal_cas_digest,
  human_authentication_slot_identity, human_authentication_epoch,
  authentication_sequence, human_founder_capacity_identity,
  human_founder_capacity_digest, authentication_operation_identity,
  authentication_operation_digest, terminal_authentication_slot_status,
  authentication_result, signature_digest, completion_logical_instant,
  read_back_authentication_slot_digest
)
```

Outcome combinations remain exactly:

| Signer outcome | Signature / digest | Verification | Failure code | Outer terminal/result |
|---|---|---|---|---|
| `VALID_SIGNATURE_FINAL` | exact non-null / exact non-null | `TRUE` | null | `AUTHENTICATED_FINAL` / `AUTHENTICATED_VALID` |
| `REJECTED_FINAL` | null / null | `FALSE` | `SIGNER_INPUT_OR_SIGNATURE_INVALID` | `INDETERMINATE_EXHAUSTED` / `AUTHENTICATION_REJECTED_FINAL` |
| `INDETERMINATE_FINAL` | null / null | `NOT_APPLICABLE` | `ACCEPTED_OPERATION_RECONSTRUCTION_UNAVAILABLE` | `INDETERMINATE_EXHAUSTED` / `INDETERMINATE_NO_VALID_RESULT` |

The displayed two tokens close the two failure categories already mandated by
G77-73; they do not add another outcome. The implementation SHALL derive the
applicable token from the validated input/signature or reconstruction
condition and SHALL NOT accept caller-supplied free text, timeout or outage
classification. The separately resolved existing one-use/non-equivocation
proof pair is an input to terminal construction; no body, formula or new
persistence kind is invented for it.

## Deterministic Algorithms

Exact future implementation sequence:

1. Refactor `persistence.py` so registered-model and subcontract operations
   converge only after their existing/new public validation at one addressed
   immutable publisher and one locked slot-CAS engine.
2. Add the frozen three subcontract views, exact closed map, immutable
   write/read, CAS, and historical generation read; retain every existing
   model API signature and behavior.
3. Extend the read-only view with only the two reads and freeze the direct
   module export list. Stop and run the complete persistence suite.
4. In `authentication.py`, encode the nine fixed schemas using the unchanged
   Candidate CJ1 implementation. Construct identities only from exact bytes.
5. Validate all registered predecessor models with unchanged Stage-2
   validators and resolve every referenced pair before the operation write.
6. Persist/read operation, claim, intent, acceptance and receipt in the exact
   forward order. A receipt is valid only when its `accepted_slot_digest`
   resolves the winning historical acceptance generation and exact bytes.
7. Only then permit the fixture-owned Ed25519 pure computation for the exact
   G77-77 tuple. A restart with the same accepted receipt continues the same
   logical invocation; it does not accept a second invocation.
8. CAS/read the complete signer outcome before exposing signature bytes. If a
   terminal signer outcome already exists, use read-only recovery and never
   invoke the primitive.
9. Persist/read signer outcome read-back, CAS/read the outer terminal, and
   persist/read the authoritative outer read-back.
10. Construct one complete ResultV2, run unchanged Stage-2 validation,
    persist/read it with existing model APIs, return only the durable result,
    and STOP before HumanDecision or orchestration.
11. Run the exact focused and regression inventory. Produce a G48
    implementation report and submit it to independent assessment.

No live clock, random value, process memory, directory order, timeout,
artifact resemblance or physical primitive-call count may determine a body,
identity, state, retry or result. Every logical instant is an explicit
persisted predecessor token.

Exact crash/restart checkpoints:

| # | Boundary | Authoritative restart state | Only allowed continuation |
|---:|---|---|---|
| 1 | subcontract temp fsynced before publish | final address absent | recompute identical bytes and publish |
| 2 | subcontract published before response | exact address/bytes readable | idempotent read-back |
| 3 | outer claim generation before pointer | `OPEN` current | retry same claim CAS |
| 4 | outer claim pointer replaced before response | exact `AUTHENTICATING` generation current | read same claim; no second operation |
| 5 | signer intent response lost | exact intent readable | read same intent |
| 6 | acceptance generation before pointer | `AVAILABLE` current | retry same acceptance CAS |
| 7 | acceptance pointer replaced before response | exact accepted generation current | derive same receipt; no second acceptance |
| 8 | receipt temp before publish | accepted generation authoritative; signing forbidden | persist same receipt |
| 9 | receipt published before response | exact receipt readable | continue the same signer-owned operation |
| 10 | signature computed before outcome CAS | receipt authoritative; signature unexposed | deterministic same-operation recomputation |
| 11 | outcome generation before pointer | `ACCEPTED_IN_PROGRESS` current | same outcome CAS only |
| 12 | outcome pointer replaced before response | one terminal signer outcome current | read only; no signing |
| 13 | outcome read-back before publish | terminal signer generation current; signature unexposed | persist same read-back |
| 14 | outer terminal generation before pointer | `AUTHENTICATING` current | same terminal CAS only |
| 15 | outer terminal pointer/read-back response lost | one terminal outer generation current | derive/read the same outer read-back and ResultV2 |
| 16 | ResultV2 publish response lost | exact complete ResultV2 readable | idempotent model read-back |

The six existing injection constants remain unchanged and are exercised for
each applicable immutable/CAS stage. No seventh storage mechanism or crash
hook is added.

## Responsibility Boundaries

| Responsibility | Exact owner | Prohibition |
|---|---|---|
| registered model schema/identity/P012 | unchanged Stage-1 models and Stage-2 validators | no subcontract registration or validation weakening |
| subcontract semantic construction/equality | new fixture authentication module under accepted external inputs | no Human choice, authority origination, arbitrary fields or storage bypass |
| canonical bytes/address/mode validation | existing Candidate store boundary | no semantic disposition, signing, key selection or wildcard bytes |
| immutable publication/CAS/history | same `CandidateHStore`, root and engines | no second store/root/path, no current-state inference |
| fixture Ed25519 continuation | signer-owned accepted receipt only | no genuine key, Human/client retry, physical counter or second logical operation |
| ResultV2 validation/persistence | unchanged model validator and existing model store API | no partial ResultV2 or ResultV3 |
| Replay | later limited read-only store consumer | no write, repair, signer call, current-pointer inference or CRO return edge |
| CRO | later passive projection only | no predecessor, execution, Human, constituent, Certification or root authority |
| Human/root/BEGIN/activation | retained external/later owners | absent and unreachable in this repair |

Dependency DAG after the future bounded implementation:

```text
models <- validators <- persistence
cj1 -------------------^
models + validators + cj1 + persistence -> authentication
authentication -X-> orchestration/Replay/CRO/CLIA/root
persistence    -X-> authentication/orchestration/Replay/CRO/CLIA/root
```

Identity DAG:

```text
validated Premise/Capacity/HFD/P_auth_v2
-> operation -> outer claim generation
-> signer intent -> acceptance generation -> receipt
-> signer outcome generation -> outcome read-back
-> existing one-use/non-equivocation proof
-> outer terminal generation -> authoritative read-back
-> complete ResultV2
```

Every arrow binds exact predecessor bytes/pairs or an exact supplied
generation digest. No node references a successor and no cycle or Human/root
return edge exists.

Authority DAG:

```text
genuine external Human Founder -> pre-existing act/authorization only
accepted external Premise/result custodian -> custody inputs
authentication code -> deterministic validation/construction only
CandidateHStore -> mechanical durability only
fixture signer -> one accepted same-operation continuation only
Replay/CRO -> later read-only/passive observation only
root/BEGIN/activation -> no incoming edge from this repair
```

## Repository Evidence

The committed Stage-3 store proves one existing path:

- `write_immutable` and `compare_and_swap` validate registered models;
- `_publish_immutable_bytes` performs fsynced no-overwrite publication;
- one `(owner, slot_identity, slot_epoch)` lock serializes CAS;
- generation records are immutable and content-addressed;
- a fsynced atomic current pointer selects the authoritative generation;
- `read_slot` validates the selected generation and referenced record; and
- the deterministic generation path already permits exact historical lookup.

The future repair changes public validation and factors shared mechanics; it
does not create another `_root`, records directory, slots directory,
generation directory, locks directory, publisher, pointer selector or lock
domain.

Baseline rollback hashes:

| Path | Baseline SHA-256 |
|---|---|
| `aigol/runtime/candidate_h_founder/persistence.py` | `0cac8fc4a0a52d9ca10eec69be3af1f93206b8e3e95d0ef95a6e67fe1afff0d5` |
| `tests/test_g77_candidate_h_founder_persistence.py` | `f36c69b81beb18a9ab0772c1d37eccb7fb2c3d685aae9f3e6127eaa49bff89cd` |
| `aigol/runtime/candidate_h_founder/__init__.py` | `93b7ed130b13d0eb32dfbd2ff873568c2ac1a0cfe2d13ca0d996571ecb0c858f` |
| `aigol/runtime/candidate_h_founder/cj1.py` | `8442f2c84b4bb95935f6a7c38e3ff12e54a8fd154f17e1bcc0c368831e00f0a3` |
| `aigol/runtime/candidate_h_founder/models.py` | `ae5ebacd647591f59bf85bf3bf6d4bd6817306fd0caa4c03b5c56f9bb5e6b79a` |
| `aigol/runtime/candidate_h_founder/validators.py` | `6b5ed7f676a8a1157731289629d941fbd867ff73caf7731813a607b5e04890ab` |

Rollback boundary for a future uncommitted implementation is exact: restore
the two MODIFY paths to their displayed baseline bytes and remove only the
two CREATE paths. Fixture stores exist only under test temporary directories;
no repository or external persistent state is migrated. If any authorized
baseline file differs before implementation begins, STOP and reassess rather
than applying this rollback recipe by resemblance.

# 3. Constitutional Self-Assessment

## Verified

- The clean baseline and all controlling predecessor hashes/ancestry were
  authenticated.
- G77-91 Option C is expressible using the committed Stage-3 publisher, lock,
  generation, pointer and read-back mechanics.
- The exact future inventory is two MODIFY and two CREATE paths; every other
  runtime/test path is closed as reuse-unchanged.
- The direct persistence and read-only APIs, nine-kind map, validation split,
  stable failure classes, implementation order, sixteen crash boundaries,
  historical read rule, tests, regressions, STOP conditions and rollback
  boundary are frozen.
- ResultV2, Stage-1 models, Stage-2 validators, G77-73, G77-77, one Human
  entry, one root, one production path and zero persistent Founder authority
  remain unchanged.
- No second persistence path or authentication path exists in the planned
  dependency graph.
- G77-92 performs no runtime/test mutation and grants no implementation,
  Human, signing, BEGIN, root, activation, deployment or production authority.

## Not Verified

- No future API, shared-engine refactor, subcontract validator, historical
  read, authentication continuation or test is implemented.
- Exact bytes, failure cases, crash recovery, concurrency, cryptographic
  vectors, cold restart, Replay reconstruction and complete ResultV2 remain
  unexecuted for the proposed repair.
- No fixture or genuine key, signature, subcontract instance, slot, ResultV2
  or production evidence is created.
- Independent implementation authorization is absent and mandatory.
- Repository-wide runtime regression for the future implementation is not
  run in this planning generation.
- Conformance outside the governance engine's defined rule set is not
  asserted; a conformant engine result does not validate future runtime work.

## Reuse Impact Assessment

1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?
   Ponovno se uporabijo en `CandidateHStore`, isti root in notranji
   record/slot/generation/lock prostori, nespremenljiva objava, enozmagovalni
   CAS, fsync/atomic replace, CJ1, Stage-1 modeli, Stage-2 validatorji ter
   G77-73/G77-77 identitete, vrstni red in Replay predhodniki.
2. Katere nove zmogljivosti (če sploh) nastanejo?
   Po ločeni odobritvi nastaneta samo zaprta mehanska zmožnost istega store-a
   za devet obstoječih ResultV2 podpogodb in eksplicitni zgodovinski read-back
   generacije ter prej načrtovana fixture Stage-4 avtentikacija. Ne nastane
   nova ustavna družina, owner, avtoriteta ali produkcijska pot.
3. Ali katera obstoječa zmogljivost postane nedosegljiva?
   Ne. Vsi obstoječi model write/read/CAS API-ji, modeli in validatorji
   ostanejo dosegljivi in semantično nespremenjeni.
4. Ali implementacija ustvarja vzporedni tok?
   Ne. Obe javni vrsti zapisa se po validaciji združita v istem notranjem
   publisher/CAS mehanizmu in istem root-u; drugi store ali zasebni bypass je
   prepovedan.
5. Ali zmanjšuje ali povečuje število produkcijskih poti?
   Ne. Število produkcijskih poti ostane `1 -> 1`.

Exact topology:

| Measure | Before | After bounded non-activated implementation | Delta |
|---|---:|---:|---:|
| production paths | 1 | 1 | 0 |
| parallel paths | 0 | 0 | 0 |
| persistent founding paths | 0 | 0 | 0 |
| Human entry points | 1 | 1 | 0 |
| root paths | 1 | 1 | 0 |
| persistent Founder authorities | 0 | 0 | 0 |

## Historical Replay and Non-Multiplication Proof

Replay begins from one complete persisted ResultV2 pair, resolves each
embedded subcontract with `read_subcontract`, recomputes each address from
exact bytes, follows only displayed predecessor pairs, and supplies recorded
slot generation/digest coordinates to `read_slot_generation`. Earlier claim
and acceptance remain verifiable after current pointers advance. Current
pointer state, live signer, process memory, directory scan, clock, repair
write and physical primitive-call count are not Replay inputs.

A crash after deterministic signature computation but before outcome
publication exposes no signature. The exact accepted receipt reconstructs the
same key/message/scheme tuple; Ed25519 pure recomputes identical bytes and one
outcome CAS admits one logical terminal value. A crash after the terminal
pointer is read-only. Thus multiple physical computations, if forced by a
pre-outcome crash, are observationally one accepted logical invocation and
cannot multiply Human acts, logical operations, admissible results, founding
effects, root transitions or activations.

## Exact Test Inventory

The modified persistence test SHALL retain all eighteen existing test
functions and add these exact focused tests:

| Test | Mandatory proof |
|---|---|
| `test_all_nine_subcontract_kinds_round_trip_exact_bytes_and_pairs` | nine map rows, exact CJ1/address/read-back |
| `test_unknown_kind_prefix_digest_and_noncanonical_bytes_fail_before_write` | closed input rejection and empty store |
| `test_subcontract_mode_is_closed` | four CAS kinds only in CAS; five immutable kinds only in write |
| `test_subcontract_identity_conflict_and_idempotence_share_record_path` | same `_record_path`, exact conflict/idempotence |
| `test_subcontract_cas_reuses_lock_generation_pointer_and_read_back` | no second path/root/engine |
| `test_historical_generation_read_survives_current_pointer_advance` | generation 1 and 2 exact reads after advance |
| `test_historical_generation_missing_corrupt_and_misbound_fail_closed` | no scan/inference/partial acceptance |
| `test_read_only_store_adds_only_subcontract_and_historical_reads` | no write/CAS/signing/repair capability |
| `test_subcontract_immutable_crash_points_have_deterministic_restart` | both existing immutable points for each immutable kind |
| `test_subcontract_cas_crash_points_have_zero_or_one_winner` | four existing slot points for each CAS kind |
| `test_registered_model_persistence_api_remains_byte_compatible` | all existing Stage-3 behavior unchanged |
| `test_persistence_dependency_boundary_remains_closed` | no authentication/orchestration/Replay/CRO/root import |

The created retry test SHALL contain exactly these focused test functions
(parameterization supplies the displayed variants without adding another
test module):

| Test | Mandatory proof |
|---|---|
| `test_nine_subcontract_schema_golden_vectors` | exact ordered fields/constants/identity bytes |
| `test_subcontract_schema_and_pair_negatives_fail_closed` | missing/extra/half-pair/wrong state/version/key/message/instant fail closed |
| `test_fixture_ed25519_uses_exact_rfc8032_pure_direct_bytes` | valid, malformed and invalid fixture vectors |
| `test_signer_is_never_called_before_durable_acceptance_receipt` | no primitive call before accepted receipt exact read-back |
| `test_g77_77_retry_tuple_requires_resolved_exact_byte_equality` | every equality row resolves bytes; any mismatch causes no signing |
| `test_same_accepted_operation_continues_after_pre_outcome_crash` | identical recomputation and one outcome |
| `test_competing_acceptances_have_one_winner_and_no_second_invocation` | one winner, identical idempotence, different intent conflict |
| `test_all_sixteen_lost_response_boundaries_converge` | every checkpoint reaches absent or the same durable state |
| `test_terminal_signer_outcome_makes_recovery_read_only` | no later primitive call |
| `test_rejected_and_indeterminate_outcomes_have_exact_closed_mapping` | exact failure tokens, conditional nulls and ResultV2 mapping |
| `test_only_complete_result_v2_validates_persists_and_reads_back` | no partial model or ResultV3 |
| `test_restart_histories_do_not_multiply_constitutional_effects` | one Human act, operation, acceptance, result and zero effects/root changes |
| `test_fixture_authentication_dependency_and_authority_boundary` | no genuine key, Human, orchestration, BEGIN, root, activation or deployment |

Mandatory regression command set after future implementation:

```text
pytest tests/test_g77_candidate_h_founder_cj1.py
       tests/test_g77_candidate_h_founder_models.py
       tests/test_g76_g77_candidate_h_identity_dag.py
       tests/test_g77_candidate_h_founder_validators.py
       tests/test_g77_candidate_h_founder_persistence.py
       tests/test_g77_candidate_h_founder_retry.py
pytest tests/test_governance_conformance.py
python -m runtime.governance.governance_conformance_engine
git diff --check
```

Any test collection outside these paths that demonstrates a dependency on a
changed public API SHALL be run but SHALL NOT be modified unless a new CDP
successor and authorization explicitly add its path.

## Fail-Closed STOP Conditions and Non-Goals

Implementation SHALL stop without signing or further mutation if:

- baseline hashes, predecessor ancestry or exact inventory differ;
- any fifth runtime/test path is required;
- the nine-kind map cannot remain closed or exact schemas cannot be derived;
- model/validator/ResultV2 changes become necessary;
- one-use/non-equivocation evidence would need an invented formula or kind;
- a second store/root/publisher/CAS/authentication path is required;
- any address, predecessor pair, historical generation or G77-77 tuple value
  is missing, unresolved, corrupt, noncanonical, inferred or unequal;
- durable acceptance receipt cannot be proven before fixture signing;
- a terminal outcome exists but recovery would invoke the primitive;
- any required focused test fails, is blocked or is not run; or
- implementation would reach HumanDecision, orchestration, BEGIN, root,
  activation, deployment or production effect.

Exact non-goals:

- no genuine Human act, key or signature;
- no physical signer exactly-once counter or G77-75 machinery;
- no generic persistence API, callback validator or unchecked helper;
- no new artifact family, owner, authority, model, version or serializer;
- no current-pointer inference for historical evidence;
- no retry object, client retry, alternate authentication flow or reset;
- no orchestration, Replay implementation, CRO, CLIA or topology work;
- no BEGIN, root mutation, adoption, activation, deployment or production
  authority; and
- no commit in G77-92.

## Constitutional Non-Effect Classification

| Classification | G77-92 result |
|---|---|
| `BOUNDED_CDP_SUCCESSOR_ESTABLISHED` | `YES` |
| `IMPLEMENTATION_AUTHORITY_GRANTED` | `NO` |
| `RUNTIME_OR_TEST_IMPLEMENTED` | `NO` |
| `RESULTV2_CHANGED` | `NO` |
| `NEW_ARTIFACT_FAMILY_OR_SERIALIZATION_DOMAIN` | `NO` |
| `SECOND_STORE_ROOT_OR_PERSISTENCE_PATH` | `NO` |
| `SECOND_AUTHENTICATION_OR_PRODUCTION_PATH` | `NO` |
| `HUMAN_ACT_OR_SIGNATURE_PERFORMED` | `NO` |
| `BEGIN_OR_ROOT_MUTATION_PERFORMED` | `NO` |
| `ADOPTION_OR_ACTIVATION_PERFORMED` | `NO` |
| `DEPLOYMENT_OR_PRODUCTION_AUTHORITY_GRANTED` | `NO` |
| `INDEPENDENT_IMPLEMENTATION_AUTHORIZATION_REQUIRED` | `YES` |

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| clean authenticated baseline | exact HEAD/tree and initial status | Git inspection | `PASS` |
| controlling predecessor authenticity | eight hashes, introducing commits and ancestry | SHA-256/Git inspection | `PASS` |
| G48 structure | six exact top-level sections and eight Code Evidence subsections | heading-count review | `PASS` |
| exact future file boundary | two MODIFY/two CREATE, no hidden path | repository and dependency review | `PASS` |
| exact persistence/read-only API | fixed signatures and exports in Section 2 | contract review | `PASS` |
| closed kind map | nine modes/prefixes and no wildcard | cardinality/content review | `PASS` |
| semantic/storage separation | authentication versus store responsibilities | boundary review | `PASS` |
| one persistence path | both operations converge after validation on existing engines/root | Stage-3 source comparison | `PASS` |
| one authentication path | only forward accepted-receipt continuation | dependency/order review | `PASS` |
| historical Replay | exact generation coordinates, no scan/current inference | deterministic reconstruction review | `PASS` |
| crash/restart closure | sixteen checkpoints and existing six injection points | state-transition review | `PASS` |
| G77-77 preservation | exact tuple and deterministic signer-owned continuation | predecessor comparison | `PASS` |
| ResultV2/model/validator preservation | unchanged files and complete-model boundary | inventory/schema review | `PASS` |
| authority/topology preservation | one/zero cardinality table and no originating edge | DAG review | `PASS` |
| rollback boundary | two baseline hashes plus two absent CREATE paths | repository review | `PASS` |
| documentation whitespace | sole G77-92 artifact | `git diff --no-index --check /dev/null <artifact>` | `PASS` |
| governance conformance tests | existing conformance suite | `pytest tests/test_governance_conformance.py` | `PASS` |
| governance conformance engine | `CONFORMANT`, 20 passed, zero failed/critical/warnings, deterministic/fail-closed/read-only | `python -m runtime.governance.governance_conformance_engine` | `PASS` |
| future runtime implementation | prohibited in G77-92 | no implementation/tests executed for repair | `NOT_RUN` |
| independent implementation authorization | required after CDP | no authorization inferred | `NOT_RUN` |
| Human/signing/BEGIN/root/activation/deployment | prohibited and outside scope | mutation/non-effect review | `NOT_APPLICABLE` |

The conformance-engine result applies only to its defined current rule set. It
does not validate the future repair and cannot support implementation or
activation authority.

# 5. Repository Mutation Summary

Created files:

- `docs/governance/G77_92_CANDIDATE_H_HUMAN_FOUNDER_BOUNDED_STAGE_3_STAGE_4_PERSISTENCE_CONTRACT_REPAIR_CONSTITUTIONAL_DEVELOPMENT_PLAN_SUCCESSOR_RESULTV2_SUBCONTRACT_DURABLE_PERSISTENCE_CLOSURE_V1.md`

Modified existing files: none.

Deleted or renamed files: none.

Runtime/test files changed in G77-92: none.

API compatibility:

- no API is changed by this planning artifact;
- the future plan preserves all existing Stage-3 method signatures and adds
  direct-module-only bounded methods/types;
- `__init__.py`, models and validators remain byte-unchanged.

Boundary preservation:

- no Human act, key, signature, subcontract, ResultV2, persistent slot,
  BEGIN, root state, adoption, activation, deployment or production evidence
  is created;
- no implementation authority is inferred from G77-91 or this plan; and
- the worktree mutation is this one governance artifact only.

Unrelated pre-existing changes: none observed at task start.

The next permitted action is an independent implementation-authorization
assessment of this exact CDP. Implementation SHALL not begin before that
assessment returns an authorizing verdict. G77-92 now stops.

# 6. Certification Verdict

G77_CANDIDATE_H_STAGE_3_STAGE_4_PERSISTENCE_REPAIR_BOUNDED_CDP_ESTABLISHED_INDEPENDENT_IMPLEMENTATION_AUTHORIZATION_REQUIRED
