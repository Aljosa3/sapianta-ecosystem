# 1. Implementation Summary

Generation: `G77_256IC_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_PROVENANCE_OPERATIONAL_COMMISSIONING_V1`

Report identity: `G77_256IC_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_PROVENANCE_OPERATIONAL_COMMISSIONING_REPORT_V1`

Reporting date: `2026-09-05`

Constitutional baseline: `constitutional-governance-finalize-v1`, stable ancestry
anchor `5c972e9960987ab27420395b54ace693df097e7b`, and exact committed IB
entry HEAD `ec2c4997ba62fbaa5e774fc9ba010f6319926c73` / tree
`887f329b030582f01a49f6c0c97f54ed4f55a818`.

Implementation contracts: G77-256HZ WRONG_PROVENANCE semantics, G77-256IA
single-route extension, G77-256IB post-IA live binding and readiness,
G77-256HX/HP split-phase one-shot patterns, G77-256FM sole launcher,
G77-256GN presentation binding, G77-256GL final admission, G77-256DU/EB/EE,
P11/CHE/FK, EX 17/17, and G48 Constitutional Evidence Reporting Standard
V1.d.

Objective:

Recover the prior worker's uncommitted G77-256IC preauthorization delta,
continue the same generation without duplicating any identity, stop at the
Human barrier, and—after the exact fresh grant—consume one authority and run
exactly one no-network WRONG_PROVENANCE operation before reducing and stopping
for Human review.

Outcome:

The recovered phase contained only the IC materializer and its focused test;
no grant, consumption, PRE receipt, FM receipt, QEMU/VM evidence, operation
record, or reduction existed. The inherited delta was authenticated, repaired
in place where stale HP/HO/GY locators remained, and completed without
restarting IC. One candidate, runtime projection, context, sealed request, and
GN presentation were materialized. Their stable identities are:

- request inner SHA-256:
  `1a3486563fc2c650561f872e9639e28ad11d5e090e57ec36e39afc8db98400f7`;
- operation: `G77_256IC_E05_WRONG_PROVENANCE_DENIAL_BEFORE_ENTRY_001`;
- candidate file SHA-256:
  `f3b89e5c87a867e025f63b82150c580823454fb88b0fa6a082fa4ddaa02f1533`;
- context inner SHA-256:
  `4837e55e8354c44b209d0bd411b6b3b07c3111a1411285c8b91f145e267414de`;
- canonical argv SHA-256:
  `b2be4c56b989dbfde79cdfdcc86354b23c3d4d3d8c3b80b06aaead99336d4bf9`;
- GN presentation file SHA-256:
  `1e1df925922dbde924c17f46189b40ed3e39968b772c4536d081fa48d1c79051`.

The Human supplied the exact grant in this same IC generation. Its source
SHA-256 is
`9b89281f3d32786146f635ef00ea926c5ce4689c75b55f4d3e24a4a42d5b383b`.
The authority transitioned `NOT_GRANTED -> GRANTED_UNCONSUMED -> CONSUMED`
exactly once. The FM launcher then produced one PRE/POST receipt pair for one
QEMU process, one VM creation, one VM boot, and one operation attempt with
`-nic none` and exit status zero.

After that sole operation and its initial terminal reduction, a second Codex
worker recovered this same IC generation following provider interruption. The
continuing worker authenticated the already-consumed authority, unique receipt
chain, raw records, reductions, seals, teardown, and terminal delta from
durable repository evidence. It invoked no authority controller, PRE, FM,
QEMU, VM, or operation path and performed no retry, repair, or replay.

The operation emitted 31 contiguous raw records. The request was denied at
`D2_PRECLAIM_AUTHORITY_BINDING_VALIDATION_BEFORE_PRECLAIM_LEDGER_APPEND_CLAIM_ENTRY_INVOCATION_OR_EFFECT`
with `operational Human act input_record_identity binding is invalid`. The
only independent mutation was `provenance_identity`; `record_identity` was the
dependent recomputation; all other bounded input dimensions were preserved.
No P11 entry, claim, protected invocation, protected effect, retry, repair, or
replay occurred.

The HZ-owned and independently reconstructed reducers both accepted. Guest
and host teardown are complete, the exact transient IC root is absent, and the
base image remains byte-identical. E05 receives one credit: `9/18 -> 10/18`.

The repository remains on branch
`g77-256fl-wrong-attempt-preboot-blocker` at the exact IB HEAD/tree and subject
`G77-256IB certify WRONG_PROVENANCE preoperational readiness`; the live remote
branch matches. HX -> HY -> HZ -> IA -> IB ancestry and the stable anchor are
verified. The nested authority remains clean, detached, and tag-pinned at HEAD
`3183bab71f8f30397c0309dd2e6d846d14a11f66`, tree
`7c32ec05efc2be43297849bc38ec8766514a523d`.

Intentionally unchanged modules:

- P11, CHE, FK, the FM launcher, HZ semantics, IA route, IB readiness, GN/GL,
  DU/EB/EE, EX, runtime governance, and Layer 0;
- the production route topology, which remains one route;
- `/home/pisarna/work/sapianta`, which was not mutated.

Architectural boundaries preserved:

- request and presentation remained non-authority until the exact Human act;
- the consumed grant is non-reusable and authorizes no second attempt;
- no new production route, generic framework, authority layer, runtime owner,
  P11 path, or parallel flow was introduced;
- all IC changes remain unstaged for Human review.

# 2. Code Evidence

## Public API

`NOT_APPLICABLE`: IC adds no public runtime API. It composes committed owners
through operation-scoped orchestration and replay-safe evidence.

## Orchestration Entry Point

The authority controller rejects occupied one-shot state and requires an exact
grant after the certified underscore normalization:

```python
    for path in (HANDOFF_PATH, SAFE_STOP_PATH, CONSUMPTION_PATH):
        if path.exists() or path.is_symlink():
            raise RuntimeError("authority namespace is not fresh")

    grant = GRANT_PATH.read_text(encoding="utf-8")
    if grant.replace("\\_", "_") != EXPECTED_NORMALIZED_GRANT:
        raise RuntimeError("Human grant does not exactly match the presented IC request")
```

Repository reference:
`.github/governance/evidence/g77_256ic_wrong_provenance_operational_v1/orchestration/G77_256IC_AUTHORITY_CONSUMPTION_CONTROLLER_V1.py`.

The finalization-only terminalizer refuses any prior terminal artifact and
authenticates the unique no-network receipt pair:

```python
    if any(path.exists() or path.is_symlink() for path in targets):
        raise RuntimeError("terminal IC namespace is not fresh")

    if not (
        pre["started_unix_ns"] == post["started_unix_ns"]
        and pre["execution_attempt_count"] == post["execution_attempt_count"] == 1
        and pre["automatic_retry_count"] == post["automatic_retry_count"] == 0
        and post["process_exit_status"] == 0
        and pre["vector"] == post["vector"]
        and argv.count("-nic") == 1
        and argv[argv.index("-nic") + 1] == "none"
    ):
        raise RuntimeError("single no-network receipt pair invalid")
```

Repository reference:
`.github/governance/evidence/g77_256ic_wrong_provenance_operational_v1/orchestration/G77_256IC_POSTOP_TERMINALIZER_V1.py`.

## Semantic Reductions

The terminalizer authenticates the committed HZ reducer identity and calls
its input-record validator and semantic constants:

```python
    if sha256(HZ_REDUCER_PATH) != HZ_REDUCER_SHA256:
        raise RuntimeError("authenticated HZ reducer identity drift")
    hz = load_module(HZ_REDUCER_PATH)
    hz._validate_input_record(authorized, prefix="AUTHORIZED_OPERATIONAL")
    hz._validate_input_record(supplied, prefix="SUPPLIED_OPERATIONAL")
    if not (
        differing == hz.EXPECTED_DIFFERING_FIELDS
        and facts["denial_point"] == hz.EXPECTED_DENIAL_BOUNDARY
        and facts["denial_error_type"] == hz.EXPECTED_ERROR_TYPE
        and facts["denial_error"] == hz.EXPECTED_ERROR_REASON
    ):
        raise RuntimeError("HZ authoritative semantic owner rejected operational packet")
```

The second reducer reconstructs directly from raw records and the POST
receipt; the authoritative result is not an input:

```python
    independent_accept = (
        len(independent_records) == 31
        and independent_differing == ["provenance_identity", "record_identity"]
        and independent_denial["denial_point"] == EXPECTED_DENIAL
        and independent_denial["denial_error"] == EXPECTED_REASON
        and one(independent_records, "b6_boundary_request_counter")["facts"]["value"] == 1
        and one(independent_records, "b6_p11_entry_counter")["facts"]["value"] == 0
        and one(independent_records, "b6_invocation_counter")["facts"]["value"] == 0
        and one(independent_records, "b6_protected_effect_counter")["facts"]["value"] == 0
        and post["process_exit_status"] == 0
    )
```

Authenticated reductions:

```text
AUTHORITATIVE_REDUCER_RESULT = ACCEPT
INDEPENDENT_REDUCER_RESULT = ACCEPT
REDUCER_AGREEMENT_STATUS = VERIFIED
EXPECTED_DENIAL_STAGE_STATUS = VERIFIED
EXPECTED_DENIAL_REASON_STATUS = VERIFIED
PROVENANCE_SPECIFIC_COMPARISON_REACHED = false
```

Observed and expected denial evidence remained separately authenticated:

```text
EXPECTED_DENIAL_STAGE = VERIFIED__D2 preclaim authority-binding validation before preclaim ledger append, claim, P11 entry, protected invocation, or protected effect
OBSERVED_DENIAL_STAGE = VERIFIED__D2_PRECLAIM_AUTHORITY_BINDING_VALIDATION_BEFORE_PRECLAIM_LEDGER_APPEND_CLAIM_ENTRY_INVOCATION_OR_EFFECT
EXPECTED_DENIAL_REASON = VERIFIED__operational Human act input_record_identity binding is invalid
OBSERVED_DENIAL_REASON = VERIFIED__operational Human act input_record_identity binding is invalid
PROVENANCE_SPECIFIC_COMPARISON_REACHED = false
```

## Public Validators

The IC test surface independently reconstructs canonical JSON, envelope
hashes, exact Git state, authority cardinality, receipt pairing, raw counter
records, HZ ownership, reducer independence/agreement, final artifact bindings,
teardown, and G48 structure.

Repository references:

- `.github/governance/evidence/g77_256ic_wrong_provenance_operational_v1/tests/test_g77_256ic_preauthorization_barrier_v1.py`;
- `.github/governance/evidence/g77_256ic_wrong_provenance_operational_v1/tests/test_g77_256ic_terminal_evidence_reduction_v1.py`.

## Canonical Data Models

- authority handoff file SHA-256:
  `36e67a6845ff6ad1637af66ab27ff1d17380a9a978fcd96641949380bf916ee1`;
- PRE receipt SHA-256:
  `a11a6be95f69d843df2b1f4936011530c27cd3c719ce4b95009a402d4caf72ae`;
- POST receipt SHA-256:
  `f14cdddf61db4518f3f5de9a46c0b2f0d62509e3f88fd81b89ca702d2a6c3143`;
- raw evidence SHA-256:
  `0369cf40d063a1d87c93fa2ff499eb3dd4573973485f88eb22234d4cd5062a5f`;
- guest execution seal SHA-256:
  `c4d1a395a274a6a41f6952806a49a63d99c6e38fae083282503eafe699266acf`;
- guest teardown seal SHA-256:
  `3f4b87184879309ecf7454f1f9a5e42dcc303592c1ac87c96948efd471bcb1f7`;
- terminal continuation manifest SHA-256:
  `87f65ecfdc4483feac30d694aff78b94478c280ba6ca9823a7e86a1ecc780a05`;
- HZ normalization SHA-256:
  `74b6197cca34f1dd0490c2f9a85a4cf3dbd4412667386df46acf587d63d268e8`;
- authoritative reduction SHA-256:
  `e58407b6077dc596965b2eb2f17e69081df87f5c7b5d690bd462e0e3d551ce3c`;
- independent reduction SHA-256:
  `0810272c1202c6f0c2c90aa000f6608c9c41cb0393c4018443ebadb79f8a3582`;
- agreement SHA-256:
  `2a2ddcffe2f6fa6db64c8cab7242bf7c86f0d086d91f0c349945297fc53a0e47`;
- serial SHA-256:
  `16b435fc2f2b6b47d2e705ba8e5f22d223c831b85d4adc63197703ed7ce05406`;
- final execution seal inner SHA-256:
  `9254882313d24fb1efa12da857d8e0447ec281aa5acc8da2e03215f851d94bb8`.

All 34 IC JSON files are unique-key canonical JSON. Raw records are contiguous
from sequence 0 through 30. The final seal binds all 19 durable authority,
request, receipt, raw, guest, serial, reduction, teardown, and context inputs.

## Deterministic Algorithms

Candidate/runtime byte equality, context inner hashing, length-delimited argv
hashing, JSON inner-envelope seals, input `record_identity` recomputation,
receipt start-identity equality, raw record cardinality, and final artifact
hash binding are deterministically reconstructed. The operation ran from
`started_unix_ns = 1788581840166166091` to
`completed_unix_ns = 1788582174961977511` with one attempt and no retry.

## Responsibility Boundaries

`PROCESS_SUCCESS != CONSTITUTIONAL_ACCEPTANCE`: process exit status zero was
only one observation. E05 credit additionally required the exact consumed
grant, canonical bindings, HZ acceptance, independent acceptance, reducer
agreement, zero protected effect, and completed guest/host teardown.

# 3. Constitutional Self-Assessment

## Verified

- `CERTIFIED != AUTHORIZED`, `REQUEST != AUTHORIZATION`, and
  `PRESENTATION != AUTHORIZATION` were preserved.
- The pregrant recovery proved all authority and operational counters zero.
- One exact Human grant was created and consumed once; it is non-reusable,
  non-transferable, and does not survive the operation.
- Exactly one PRE, FM invocation, no-network QEMU, VM creation, VM boot,
  operation attempt, WRONG_PROVENANCE operation, and boundary request occurred.
- The request was denied at the expected D2 stage and for the exact expected
  reason before P11 entry, claim, protected invocation, or protected effect.
- Retry, repair/retry, replay, second VM, and second operation are zero.
- Guest and host teardown are complete; the transient IC root is absent; the
  immutable base image hash remains
  `6e40c07ae715f744f84af0bec76415cc1987dd115b4b8de437818561f01a3733`.
- HZ and independent reducers agree; operational capability is `VERIFIED`;
  E05 is `10/18` with eight obligations remaining.
- `EX_REUSED = 17/17`; `EX_RECONSTRUCTED = 0`.

Recovered phase and authority state:

```text
IC_OPERATION_ID_STATUS = VERIFIED__ONE
IC_CANDIDATE_STATUS = VERIFIED__ONE
IC_RUNTIME_PROJECTION_STATUS = VERIFIED__BYTE_IDENTICAL_TO_CANDIDATE
IC_CONTEXT_STATUS = VERIFIED__ONE_SEALED
IC_REQUEST_STATUS = VERIFIED__ONE_SEALED
IC_GN_PRESENTATION_STATUS = VERIFIED__ONE_BOUND
HUMAN_OPERATIONAL_AUTHORITY_STATUS = VERIFIED__ONE_EXACT_GRANT
AUTHORITY_CONSUMPTION_STATUS = VERIFIED__CONSUMED_EXACTLY_ONCE
PRE_STATUS = VERIFIED__ONE
FM_OPERATIONAL_STATUS = VERIFIED__ONE
QEMU_STATUS = VERIFIED__ONE_NO_NETWORK
VM_STATUS = VERIFIED__ONE_CREATION_AND_ONE_BOOT
OPERATION_ATTEMPT_STATUS = VERIFIED__ONE_TERMINAL
REDUCTION_STATUS = VERIFIED__AUTHORITATIVE_AND_INDEPENDENT_AGREE
IC_TERMINAL_VALIDATION = VERIFIED__11_OF_11
GRANT_COUNT = VERIFIED__1
CONSUMPTION_COUNT = VERIFIED__1
AUTHORITY_REUSE = VERIFIED__0
SECOND_GRANT = VERIFIED__0
SECOND_CONSUMPTION = VERIFIED__0
QEMU_INVOCATION_COUNT = VERIFIED__1
NETWORK_ENABLED_INVOCATION_COUNT = VERIFIED__0
NO_NETWORK_POLICY_STATUS = VERIFIED
```

Reuse Impact Assessment:

1. Existing HZ, IA, IB, HX/HP, FM, GN/GL, DU/EB/EE, P11/CHE/FK, EX,
   governance, and Layer 0 capabilities were reused.
2. Only IC-scoped operational evidence and the resulting demonstrated
   WRONG_PROVENANCE operational capability were added.
3. No pre-existing capability became unreachable.
4. No parallel flow was created.
5. Production routes remained one before and after.

```text
REUSED_CERTIFIED_CAPABILITY_SET = VERIFIED__IB_IA_HZ_HX_HP_FM_GN_GL_DU_EB_EE_P11_CHE_FK_EX_17_OF_17_GOVERNANCE_LAYER_0
NEW_CAPABILITY_SET = VERIFIED__IC_WRONG_PROVENANCE_OPERATIONAL_EVIDENCE_ONLY
UNREACHABLE_PREEXISTING_CAPABILITY_SET = VERIFIED__EMPTY
PRODUCTION_ROUTE_BEFORE = VERIFIED__1
PRODUCTION_ROUTE_AFTER = VERIFIED__1
PRODUCTION_ROUTE_DELTA = VERIFIED__0
NEW_GENERIC_FRAMEWORK_COUNT = VERIFIED__0
NEW_AUTHORITY_LAYER_COUNT = VERIFIED__0
NEW_PRODUCTION_ROUTE_COUNT = VERIFIED__0
NEW_RUNTIME_OWNER_COUNT = VERIFIED__0
```

Infrastructure Amortization:

```text
DID_IC_REQUIRE_NEW_COMMON_INFRASTRUCTURE = VERIFIED__NO
DID_IC_REQUIRE_NEW_VECTOR_SPECIFIC_INFRASTRUCTURE = VERIFIED__NO
DID_IC_REQUIRE_NEW_GENERIC_FRAMEWORK = VERIFIED__NO
DID_IC_REQUIRE_NEW_AUTHORITY_LAYER = VERIFIED__NO
DID_IC_REQUIRE_NEW_RUNTIME_OWNER = VERIFIED__NO
DID_IC_REQUIRE_NEW_PRODUCTION_ROUTE = VERIFIED__NO
DID_IC_REQUIRE_P11_CORE_CHANGE = VERIFIED__NO
DID_IC_REUSE_HZ_REPOSITORY_CAPABILITY = VERIFIED__YES
DID_IC_REUSE_IA_ROUTE_SUPPORT = VERIFIED__YES
DID_IC_REUSE_IB_READINESS = VERIFIED__YES
DID_IC_REUSE_HX_OPERATIONAL_PATTERN = VERIFIED__YES
DID_IC_REUSE_FM_GN_GL = VERIFIED__YES
DID_IC_REUSE_DU_EB_EE = VERIFIED__YES
DID_IC_REUSE_P11_CHE_FK = VERIFIED__YES
DID_IC_REUSE_EX_17_OF_17 = VERIFIED__YES
GENERATIONS_SINCE_E05_9_OF_18 = VERIFIED__5
E05_CREDITS_SINCE_9_OF_18 = VERIFIED__1
OPERATIONAL_ATTEMPTS_SINCE_E05_9_OF_18 = VERIFIED__1
E05_GENERATIONS_PER_CREDIT = VERIFIED__5
OPERATIONAL_ATTEMPTS_PER_CREDIT = VERIFIED__1
MARGINAL_E05_GENERATION_COST = NOT_MEASURED__NO_GOVERNED_COST_INSTRUMENT
MARGINAL_NEW_INFRASTRUCTURE_PER_E05_CREDIT = VERIFIED__ZERO_NEW_COMMON_INFRASTRUCTURE_FOR_ONE_CREDIT
INFRASTRUCTURE_AMORTIZATION_SIGNAL = ESTIMATED__POSITIVE_REUSE_SIGNAL__NO_TOKEN_OR_MONETARY_INFERENCE
```

CCWIM:

```text
CCWIM_MATURITY_LEVEL = ESTIMATED__L4_LIKE__NO_L5_CLAIM
CROSS_WORKER_STATE_RECOVERY_LEVEL = VERIFIED__REPOSITORY_AUTHENTICATED_UNCOMMITTED_DELTA_THROUGH_TERMINAL_STATE
REPOSITORY_DERIVED_CONTEXT_RATIO = ESTIMATED__DOMINANT
HUMAN_HANDOFF_INFORMATION_REQUIRED = VERIFIED__CHECKPOINT_SCOPE_PROHIBITIONS_AND_REPOSITORY_LOCATORS
PREVIOUS_WORKER_CONVERSATION_REQUIRED = VERIFIED__NO
PREVIOUS_WORKER_IDENTITY_REQUIRED = VERIFIED__NO
PREVIOUS_WORKER_MEMORY_REQUIRED = VERIFIED__NO
AUTHENTICATED_REPOSITORY_CONTINUATION = VERIFIED__YES
INTER_GENERATION_CROSS_WORKER_CONTINUATION = NOT_APPLICABLE__SAME_IC_GENERATION
INTRA_GENERATION_CROSS_WORKER_CONTINUATION = VERIFIED__YES
UNCOMMITTED_DELTA_RECOVERY = VERIFIED__YES
AUTHORITY_STATE_RECOVERY = VERIFIED__CONSUMED_AT_SECOND_WORKER_RECOVERY
CONSUMED_AUTHORITY_RECOVERY = VERIFIED__YES
POST_OPERATION_STATE_RECOVERY = VERIFIED__YES
OPERATION_REPLAY_PREVENTION = VERIFIED__ABSOLUTE_BARRIER_ENFORCED__ZERO_OPERATIONAL_INVOCATIONS_BY_CONTINUING_WORKER
CROSS_WORKER_CONSTITUTIONAL_DRIFT = VERIFIED__0
HANDOFF_SUFFICIENCY_STATUS = VERIFIED
HANDOFF_STATE_COMPLETENESS = VERIFIED__COMPLETE_FOR_IC_TERMINAL_CERTIFICATION
HANDOFF_RECONSTRUCTION_REQUIRED = VERIFIED__YES
HANDOFF_RECONSTRUCTION_SUCCESS = VERIFIED__YES
HANDOFF_AMBIGUITY_COUNT = VERIFIED__0
UNAUTHENTICATED_HANDOFF_ASSUMPTION_COUNT = VERIFIED__0
```

Required Metrics and Cognition Provenance:

| Metric | Classification |
|---|---|
| PROJECT_PROGRESS_ESTIMATE | `NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR` |
| CONSTITUTIONAL_HEALTH_EVIDENCE | `VERIFIED__FAIL_CLOSED_D2_DENIAL_AND_ZERO_PROTECTED_EFFECT` |
| SHADOW_AUTOMATION_STATUS | `VERIFIED__ABSENT` |
| CONSTITUTIONAL_FRONTIER_DISTANCE | `NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR` |
| E05_FRONTIER_DISTANCE | `VERIFIED__8_OF_18_OBLIGATIONS_REMAIN` |
| SELECTED_E05_LOCAL_FRONTIER_DISTANCE | `NOT_APPLICABLE__WRONG_PROVENANCE_OPERATIONALLY_CERTIFIED` |
| GOVERNANCE_EFFICIENCE | `ESTIMATED__TARGETED_AFFECTED_FRONTIER` |
| ARCHITECTURAL_GOVERNANCE_EFFICIENCE | `VERIFIED__ONE_ROUTE_RETAINED` |
| PROOF_REUSE_EFFICIENCY | `VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED` |
| COGNITION_ASSISTED_HANDOFF | `VERIFIED__REPOSITORY_AUTHENTICATED_SAME_GENERATION_CONTINUATION` |
| AIGOL_CODEX_WORK_SHARE | `NOT_MEASURED` |
| OVERENGINEERING_RISK | `ESTIMATED__LOW` |
| PROOF_PROCESS_OVERHEAD_RISK | `ESTIMATED__MODERATE` |
| COGNITION_PROVENANCE | `VERIFIED__GIT_IB_RECOVERED_IC_DELTA_HZ_IA_IB_HX_HP_HT_HV_HW_FM_GN_GL_DU_EB_EE_P11_CHE_FK_EX_GOVERNANCE_LAYER_0_PINNED_NESTED_AUTHORITY_AND_FRESH_IC_EVIDENCE` |
| CANDIDATE_CAPABILITY | `VERIFIED__EXACT_IB_HEAD_TREE_REBIND` |
| WRONG_PROVENANCE_CANDIDATE_CAPABILITY | `VERIFIED` |
| WRONG_PROVENANCE_REPOSITORY_CAPABILITY | `VERIFIED` |
| WRONG_PROVENANCE_ROUTE_SUPPORT | `VERIFIED` |
| WRONG_PROVENANCE_BINDING_STATUS | `VERIFIED__CURRENT_COMMITTED_IA_LIVE_BINDING` |
| WRONG_PROVENANCE_PREOPERATIONAL_READINESS | `VERIFIED` |
| WRONG_PROVENANCE_OPERATIONAL_CAPABILITY | `VERIFIED` |
| SHADOW_DESIGN_TARGET | `VERIFIED__FORMALIZE_REUSE_BIND_VERIFY_AUTHORIZE_OPERATE_REDUCE_STOP` |
| CONSTITUTIONAL_CONTINUATION_PROGRESS | `VERIFIED__IC_TERMINAL_HUMAN_REVIEW_BARRIER` |
| PROMPT_CONTEXT_REUSE_RATIO | `NOT_MEASURED` |
| TOKEN_BENCHMARK | `NOT_MEASURED` |
| LLM_COST_REDUCTION_RATIO | `NOT_MEASURED` |
| LCRR | `NOT_MEASURED` |
| E05_GENERATIONS_PER_CREDIT | `VERIFIED__5` |
| OPERATIONAL_ATTEMPTS_PER_CREDIT | `VERIFIED__1` |
| MARGINAL_E05_GENERATION_COST | `NOT_MEASURED__NO_GOVERNED_COST_INSTRUMENT` |
| MARGINAL_NEW_INFRASTRUCTURE_PER_E05_CREDIT | `VERIFIED__ZERO_NEW_COMMON_INFRASTRUCTURE_FOR_ONE_CREDIT` |
| INFRASTRUCTURE_AMORTIZATION_SIGNAL | `ESTIMATED__POSITIVE_REUSE_SIGNAL__NO_COST_INFERENCE` |
| EXPECTED_NEXT_CREDIT_GENERATION_COUNT | `NOT_MEASURED__NEXT_OBLIGATION_REQUIRES_SEPARATE_HUMAN_REVIEW` |

Previous-worker prose served only as a locator. Git objects, the recovered
delta, canonical evidence, receipts, seals, raw records, and reducer outputs
are the proof sources.

## Not Verified

- Total-project progress, universal constitutional-frontier distance, token
  usage, LLM cost reduction, LCRR, and marginal generation cost are not
  measured and are not inferred from provider capacity, elapsed time, reuse,
  or first-attempt success.
- L5 CCWIM maturity is not proven and is not claimed.
- No next E05 operation, vector, generation, or authorization is selected or
  authorized.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| Exact IB local/remote base | Git HEAD/tree/subject/origin and live branch | exact comparison and `ls-remote` | PASS |
| Stable ancestry and nested authority | HX/HY/HZ/IA/IB lineage; pinned nested tag | ancestry and nested HEAD/tree/status/tag checks | PASS |
| Same-generation delta recovery | initial two-file IC delta and completed namespace | full enumeration and identity uniqueness review | PASS |
| Pregrant zero state and barrier | IC preauthorization checkpoint/report | forbidden-artifact scan, canonical seals, focused tests | PASS |
| Exact grant and one consumption | source, handoff, postgrant and consumption checkpoints | normalized exact-sentence binding and cardinality reconstruction | PASS |
| Candidate/runtime/context/request/presentation | canonical IC live binding | byte equality, hashes, GN/GL, DU/EB/EE validation | PASS |
| PRE/FM/QEMU one-shot no-network route | PRE/POST receipt pair and serial | shared start identity, attempt 1, retry 0, `-nic none`, exit 0 | PASS |
| Raw evidence and denial semantics | 31 raw records and guest seals | sequence, record identity, field delta, stage/reason, counter checks | PASS |
| HZ authoritative reduction | authenticated HZ SHA-256 and normalization | HZ input validation and semantic constants | PASS |
| Independent reduction and agreement | direct raw/receipt reconstruction | no authoritative-output input; both reducers accept | PASS |
| Teardown and base preservation | guest/host teardown seals | transient absence and base SHA-256 equality | PASS |
| IC focused validation | both IC focused suites | pytest | PASS__11_OF_11 |
| Current HZ/IA/IB/GN/GL affected frontier | current-applicable suites | pytest; four historical entry assertions deselected | PASS__135_OF_135 |
| HX/HP operational-pattern reuse | current-applicable suites | pytest; four superseded entry/pregrant assertions deselected | PASS__14_OF_14 |
| P11/CHE/FK affected regressions | focused construction/consumer/runtime suites | pytest | PASS__33_OF_33 |
| EX common proof substrate | certified read-only EX validator | direct validator | PASS__12_OF_12__17_REUSED__0_RECONSTRUCTED |
| Governance conformance tests | `tests/test_governance_conformance.py` | pytest | PASS__9_OF_9 |
| Layer 0 contracts and model | `tests/test_layer_contracts.py`; `tests/test_layer_model.py` | pytest | PASS__7_OF_7 |
| Governance conformance engine | runtime conformance owner | direct execution | PASS__20_OF_20__CONFORMANT |
| Canonical JSON, seals, and Python structure | 34 IC JSON files and orchestration/tests | unique-key canonical load, inner hashes, AST/literal-key checks | PASS |
| Worktree whitespace and empty index | complete delta | `git diff --check`; cached-name check | PASS__INDEX_EMPTY |
| No second operation during validation | commands and process/filesystem state | read-only command review; no FM invocation | PASS |

Validation accounting for this continuation:

```text
CURRENT_APPLICABLE_PYTEST_PASSED = 209
CURRENT_APPLICABLE_PYTEST_FAILED = 0
CURRENT_APPLICABLE_PYTEST_DESELECTED = 8
PYTEST_WARNINGS = 0
EX_REGRESSION_PASSED = 12
EX_REGRESSION_FAILED = 0
CONFORMANCE_CHECKS_PASSED = 20
CONFORMANCE_CHECKS_FAILED = 0
CONFORMANCE_WARNINGS = 0
```

The two historical-inclusive diagnostic invocations each exposed four
superseded assertions before their current-applicable reruns: HZ/IA/IB had one
HY-era HEAD assertion, one pre-current-IA launcher-checkout assertion, and two
pre-IB entry/materialization assertions; HX/HP had two old committed-entry
assertions, one old-base terminal assertion, and one pregrant-absence assertion
that is superseded by HX's completed historical operation. Thus the diagnostic
invocations observed `8` historical/superseded failures in total; the terminal
current-applicable matrix has `0` failures and `8` explicit deselections.
Historical evidence was not modified. The current exact IB base and IC
terminal state were independently authenticated.

# 5. Repository Mutation Summary

Modified files:

- one untracked IC evidence namespace containing the repaired inherited
  materializer/test, operation-scoped orchestration, candidate/runtime/context,
  request/presentation/barrier records, authority records, PRE/POST receipts,
  guest/raw/serial evidence, HZ and independent reductions, agreement,
  teardown checkpoints, final seal, terminal reduction, and focused tests;
- this G48-compliant terminal report.

No tracked pre-existing file was modified. No file was staged. No commit,
push, reset, clean, stash, restore, checkout, switch, merge, rebase, or tag was
performed.

Terminal counters:

```text
HUMAN_OPERATIONAL_AUTHORITY = 1
AUTHORITY_CONSUMPTION = 1
PRE = 1
FM_OPERATIONAL_LAUNCHER_INVOCATION = 1
QEMU = 1
VM_CREATION = 1
VM_BOOT = 1
OPERATION_ATTEMPT = 1
WRONG_PROVENANCE_OPERATION = 1
REQUEST = 1
P11_ENTRY = 0
PROTECTED_INVOCATION = 0
PROTECTED_EFFECT = 0
RETRY = 0
REPAIR_RETRY = 0
REPLAY = 0
E05_CREDIT = 1
E05_BEFORE_IC = 9/18
E05_AFTER_IC = 10/18
```

API compatibility: no public API or P11 core changed. Existing four-vector
support and the sole FM production route remain intact.

Boundary preservation: the protected boundary failed closed before P11 entry,
the Human act was consumed exactly once, and neither success nor failure
creates residual authority. `AUTO_CONTINUABLE = NO`; `HUMAN_REVIEW_REQUIRED =
YES`; `NEXT_GENERATION_STARTED = NO`.

Unrelated pre-existing changes: none observed in the canonical worktree. The
historical/composite worktree was not mutated and is outside this report.

# 6. Certification Verdict

Terminal frontier:

```text
CURRENT_E05_STATUS = VERIFIED__10_OF_18
WRONG_PROVENANCE_OPERATIONAL_CAPABILITY = VERIFIED
E05_CREDIT = VERIFIED__1
E05_BEFORE_IC = VERIFIED__9_OF_18
E05_AFTER_IC = VERIFIED__10_OF_18
E05_FRONTIER_DISTANCE = VERIFIED__8_OF_18_OBLIGATIONS_REMAIN
SELECTED_E05_LOCAL_FRONTIER_DISTANCE = NOT_APPLICABLE__WRONG_PROVENANCE_OPERATIONALLY_CERTIFIED
LAST_VERIFIED_EDGE = VERIFIED__AFFECTED_FRONTIER_AND_GOVERNANCE_CONFORMANCE_COMPLETE
FIRST_BROKEN_EDGE = NOT_APPLICABLE__NO_CURRENT_IC_BROKEN_EDGE
MINIMUM_MISSING_CAPABILITY = NOT_APPLICABLE__IC_TERMINAL_CERTIFICATION_COMPLETE
MINIMUM_LEGAL_NEXT_DELTA = VERIFIED__HUMAN_REVIEW_ONLY__NO_AUTO_CONTINUATION
AUTO_CONTINUABLE = NO
HUMAN_REVIEW_REQUIRED = YES
```

VERIFIED__G77_256IC_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_PROVENANCE_OPERATIONAL_COMMISSIONING__ONE_AUTHORITY__ONE_PRE__ONE_FM__ONE_NO_NETWORK_QEMU__ONE_VM_CREATION__ONE_VM_BOOT__WRONG_PROVENANCE_REQUEST_DENIED_AT_D2_BEFORE_P11_ENTRY_INVOCATION_OR_EFFECT__ZERO_RETRY__AUTHORITATIVE_AND_INDEPENDENT_REDUCERS_AGREE__E05_10_OF_18__HUMAN_REVIEW_REQUIRED
