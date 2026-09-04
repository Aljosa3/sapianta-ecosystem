# 1. Implementation Summary

Generation: G77-256HZ one bounded repository-only `WRONG_PROVENANCE`
formalization.

Mode: `FORMALIZE -> REUSE -> VERIFY -> STOP`; no route mutation, live binding,
readiness claim, Human operational authority, request, PRE, FM operational
invocation, QEMU, VM, P11 entry, protected invocation, protected effect, or E05
credit.

The exact committed and pushed HY checkpoint authenticated before mutation:

| Property | Authenticated value | Status |
|---|---|---|
| worktree | `/home/pisarna/work/sapianta-fl` | `VERIFIED` |
| branch | `g77-256fl-wrong-attempt-preboot-blocker` | `VERIFIED` |
| HEAD | `451fafdeafc935c352a27f75fbddb473423ce7b3` | `VERIFIED` |
| tree | `98a5f94880cae12e91ab3173fad36de8c90d0d23` | `VERIFIED` |
| subject | `G77-256HY select WRONG_PROVENANCE frontier` | `VERIFIED` |
| origin | `git@github.com:Aljosa3/sapianta-ecosystem.git` | `VERIFIED` |
| live remote branch | `451fafdeafc935c352a27f75fbddb473423ce7b3` | `VERIFIED` |
| tracked worktree at entry | clean | `VERIFIED` |
| index at entry | empty | `VERIFIED` |
| HY ancestry | present | `VERIFIED` |
| HX ancestry | present | `VERIFIED` |
| stable anchor `5c972e9...` | present | `VERIFIED` |
| nested origin | `git@github.com:Aljosa3/sapianta-core.git` | `VERIFIED` |
| nested immutable tag | `sapianta-system-nested-authority-3183bab-v1` | `VERIFIED` |
| nested HEAD | `3183bab71f8f30397c0309dd2e6d846d14a11f66` | `VERIFIED` |
| nested tree | `7c32ec05efc2be43297849bc38ec8766514a523d` | `VERIFIED` |
| nested state | clean, detached, pinned | `VERIFIED` |

The committed HY report and the HX terminal evidence independently reconstruct
the exact 18-row E05 set. Satisfied are `POSITIVE_AUTHORITY_BASELINE`,
`STATE_TRANSITION`, `CONCURRENCY`, `UNKNOWN`, `CONSUMED`, `WRONG_CALLER`,
`WRONG_ATTEMPT`, `WRONG_INPUT`, and `WRONG_CONTRACT`. Remaining are
`AMBIGUOUS`, `STALE`, `FUTURE`, `EXPIRED`, `REVOKED`, `SUPERSEDED`,
`WRONG_SCOPE`, `WRONG_PROVENANCE`, and `COHERENT_COPY`.

```text
E05_REQUIRED = 18
E05_SATISFIED = 9
E05_REMAINING = 9
E05_BEFORE_HZ = 9/18
E05_AFTER_HZ = 9/18
E05_CREDIT = 0
```

HZ implements only the minimum selected repository capability: one canonical
formal specification, deterministic producer, independently implemented
fail-closed reducer, focused negative tests, sealed terminal reduction, and
this report. The authorized baseline is recovered from committed HX evidence;
the supplied record changes exactly one independent coordinate,
`provenance_identity`, and deterministically recomputes exactly one dependent
coordinate, `record_identity`.

# 2. Code Evidence

## Formal semantics and producer

`G77_256HZ_WRONG_PROVENANCE_FORMAL_SPECIFICATION_V1.json` seals this exact
rule:

```text
INDEPENDENT_MUTATION_COUNT = 1
INDEPENDENT_MUTATED_COORDINATE = provenance_identity
DEPENDENT_RECOMPUTATION_COUNT = 1
DEPENDENT_RECOMPUTED_COORDINATE = record_identity
EXPECTED_DIFFERING_FIELDS = provenance_identity, record_identity
```

The producer authenticates the specification seal; exact P11 input substrate
hash; HX raw-evidence SHA-256 and Git blob; unique records 16, 17, and 18;
canonical Human Authority Act; canonical CHE correlation; Human-act digest and
payload digest; protected owner-state revision hash; source input canonical
bytes; and every relevant act/input/owner binding. It then copies the baseline,
changes only `provenance_identity`, clears and recomputes `record_identity`
through the existing P11 canonical identity mechanic, revalidates the result,
and emits canonical JSON.

The producer has no operational entry point. Direct execution exits with
`repository-only module; no operational entry point`.

## Authoritative provenance resolution

The authoritative provenance identity is not inferred from the adversarial
record. The existing P11 owner is reused:

```text
AUTHORITATIVE_OWNER = AUTHORITY_CUSTODY_PROCESS_PRINCIPAL
AUTHORITATIVE_SOURCE = EXISTING_P11_PROTECTED_OWNER_STATE_BINDING
AUTHORITATIVE_PROVENANCE_IDENTITY = G77_256HX_AUTHENTICATED_FA_EM_CD_PROVENANCE_V1
```

The raw HX evidence is authenticated as SHA-256
`ef68294aac53051396c5eac20c786bf914f42de9a4e628f07580591a797187f5`
and Git blob `4947ad5f128d8734cddb10b70cd7a3bfd72bd373`. Record 16 binds the
canonical act, CHE correlation, and authorized input. Record 17 is the
`AVAILABLE` protected custody owner-state revision. Record 18 independently
captures the same owner-state binding in the authority checkpoint. Both owner
observations agree on owner-state identity, act identity, owner identity, and
provenance identity. The resolver rejects zero observations, any non-protected
source role, and any conflicting material identity.

```text
AUTHORIZED_BASELINE_PROVENANCE_IDENTITY == AUTHORITATIVE_PROVENANCE_IDENTITY
SUPPLIED_PROVENANCE_IDENTITY != AUTHORITATIVE_PROVENANCE_IDENTITY
SUPPLIED_INPUT_IS_AUTHORITATIVE_SOURCE = NO
AUTHORITATIVE_PROVENANCE_RESOLUTION_STATUS = VERIFIED
```

This reuses one existing owner. It creates no provenance registry, authority
layer, runtime owner, generic provenance framework, or production route.

## Reducer and expected denial

The reducer independently parses duplicate-key-safe canonical JSON,
recalculates both record identities, reauthenticates the HX act/CHE/protected
owner source, resolves authoritative provenance, verifies exact HY base
binding, proves the mutation and preservation sets, and rejects operational or
credit overclaims.

The canonical P11 ordering determines the future denial. The changed
`provenance_identity` necessarily changes `record_identity`. The Human act
payload still binds the authorized baseline record identity. Therefore
`validate_operational_act_payload` rejects that earlier equality before a new
`AuthorityBinding` can be compared to protected custody:

```text
EXPECTED_DENIAL_STAGE = D2_PRECLAIM_AUTHORITY_BINDING_VALIDATION_BEFORE_PRECLAIM_LEDGER_APPEND_CLAIM_ENTRY_INVOCATION_OR_EFFECT
EXPECTED_DENIAL_REASON = operational Human act input_record_identity binding is invalid
EXPECTED_DENIAL_REACHABILITY_STATUS = VERIFIED__EARLIER_RECORD_IDENTITY_BINDING_DENIAL__PROVENANCE_SPECIFIC_COMPARISON_NOT_REACHED
EXPECTED_P11_ENTRY = 0
EXPECTED_PROTECTED_INVOCATION = 0
EXPECTED_PROTECTED_EFFECT = 0
```

HZ does not claim that a provenance-specific runtime comparison is reachable.
It formalizes the canonical wrong-provenance condition and the exact earlier
denial imposed by current P11 ordering.

## Focused fail-closed cases

The focused suite covers positive reduction; deterministic producer output;
no provenance mutation; wrong target coordinate; a second independent
mutation; stale record identity; missing authoritative source; conflicting
authoritative resolution; supplied input presented as authority; baseline
provenance mismatch; wrong generation, base, and vector; tampered resolution
proof; duplicate keys; noncanonical and malformed JSON; exact P11 ordering;
EX 17/17 reuse; single-route preservation; and absence of operational call
sites.

# 3. Constitutional Self-Assessment

The constitutional invariants remain intact:

```text
CERTIFIED != AUTHORIZED
REQUEST != AUTHORIZATION
PRESENTATION != AUTHORIZATION
REQUEST != ENTRY != INVOCATION != EFFECT
REPOSITORY_CAPABILITY != OPERATIONAL_CAPABILITY
FORMALIZED != BOUND
BOUND != READY
READY != AUTHORIZED
AUTHORIZED != OPERATED
EXPECTED_DENIAL != OBSERVED_DENIAL
PROVIDER_CAPABILITY != EXECUTION_AUTHORITY
NO_PROTECTED_MACHINE_EFFECT_WITHOUT_VALID_P11_AUTHORITY
```

EX remains the sole common substrate:

```text
EX_REUSED = 17/17
EX_RECONSTRUCTED = 0
```

Reuse Impact Assessment:

1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo? Ponovno
   se uporabijo P11 D2, canonical Human Act/CHE/FK validation pattern, EX
   17/17, canonical JSON and replay-hash identity mechanics, HX protected
   owner-state evidence, patterns GY/HA/HP/HR/HX, and unchanged FM/GN/GL/
   DU/EB/EE architecture.
2. Katere nove zmogljivosti nastanejo? Nastanejo samo vektorsko specifična
   formalna specifikacija, deterministični repository-only producer,
   fail-closed repository-only reducer in dokaz razrešitve avtoritativne
   provenance. Nobena od teh zmogljivosti ni operativna.
3. Ali katera obstoječa zmogljivost postane nedosegljiva? Ne; preverjeni niz je
   prazen.
4. Ali implementacija ustvarja vzporedni tok? Ne.
5. Ali zmanjšuje ali povečuje število produkcijskih poti? Ne; ena pot ostane
   ena.

```text
REUSED_CERTIFIED_CAPABILITY_SET = P11_D2__CHE__FK_VALIDATION_PATTERN__EX_17_OF_17__CANONICAL_JSON_REPLAY_HASH__HX_PROTECTED_OWNER_STATE__GY_HA_HP_HR_HX_PATTERNS__FM_GN_GL_DU_EB_EE_UNCHANGED
NEW_CAPABILITY_SET = WRONG_PROVENANCE_FORMAL_SPECIFICATION__DETERMINISTIC_REPOSITORY_PRODUCER__FAIL_CLOSED_REPOSITORY_REDUCER__AUTHORITATIVE_PROVENANCE_RESOLUTION_PROOF
UNREACHABLE_PREEXISTING_CAPABILITY_SET = EMPTY
PRODUCTION_ROUTE_BEFORE = 1
PRODUCTION_ROUTE_AFTER = 1
PRODUCTION_ROUTE_DELTA = 0
NEW_GENERIC_FRAMEWORK_COUNT = 0
NEW_AUTHORITY_LAYER_COUNT = 0
NEW_PRODUCTION_ROUTE_COUNT = 0
NEW_RUNTIME_OWNER_COUNT = 0
```

Infrastructure Amortization:

```text
DID_HZ_REQUIRE_NEW_COMMON_INFRASTRUCTURE? NO
DID_HZ_REQUIRE_NEW_VECTOR_SPECIFIC_INFRASTRUCTURE? YES
DID_HZ_REQUIRE_NEW_GENERIC_FRAMEWORK? NO
DID_HZ_REQUIRE_NEW_AUTHORITY_LAYER? NO
DID_HZ_REQUIRE_NEW_RUNTIME_OWNER? NO
DID_HZ_REQUIRE_NEW_PRODUCTION_ROUTE? NO
DID_HZ_REQUIRE_P11_CORE_CHANGE? NO
DID_HZ_REUSE_GY_WRONG_INPUT_PATTERN? YES
DID_HZ_REUSE_HR_WRONG_CONTRACT_PATTERN? YES
DID_HZ_REUSE_HX_REDUCER_PATTERN? YES
DID_HZ_REUSE_P11_CHE_FK? YES
DID_HZ_REUSE_EX_17_OF_17? YES
DID_HZ_REUSE_EXISTING_IDENTITY_MODEL? YES
DID_HZ_REUSE_EXISTING_PROVENANCE_OWNER? YES
DID_HZ_REUSE_EXISTING_CANONICAL_JSON_AND_SEAL_MECHANICS? YES
GENERATIONS_SINCE_E05_9_OF_18 = VERIFIED__2__HY_AND_HZ
OPERATIONAL_ATTEMPTS_SINCE_E05_9_OF_18 = VERIFIED__0
NEW_CERTIFIED_COMPONENTS_SINCE_E05_9_OF_18 = NOT_PROVEN__HZ_DELTA_UNCOMMITTED_AND_AWAITING_HUMAN_REVIEW
REUSED_CERTIFIED_COMPONENTS_SINCE_E05_9_OF_18 = NOT_MEASURED__EX_17_OF_17_PLUS_EXISTING_OWNERS_WITHOUT_GOVERNED_TOTAL_DENOMINATOR
MARGINAL_NEW_INFRASTRUCTURE_PER_E05_CREDIT = ESTIMATED__ONE_VECTOR_SPECIFIC_ARTIFACT_SET_TOWARD_A_POTENTIAL_TENTH_CREDIT__NO_NUMERIC_RATIO
```

CCWIM:

```text
CCWIM_MATURITY_LEVEL = ESTIMATED__L4_LIKE__NO_L5_CLAIM
CROSS_WORKER_STATE_RECOVERY_LEVEL = VERIFIED__REPOSITORY_AUTHENTICATED_CONTINUATION
REPOSITORY_DERIVED_CONTEXT_RATIO = ESTIMATED__DOMINANT__NO_FORMAL_RATIO
HUMAN_HANDOFF_INFORMATION_REQUIRED = VERIFIED__CHECKPOINT_SCOPE_AND_STOP_POLICY_ONLY
PREVIOUS_WORKER_CONVERSATION_REQUIRED = VERIFIED__NO
PREVIOUS_WORKER_IDENTITY_REQUIRED = VERIFIED__NO
PREVIOUS_WORKER_MEMORY_REQUIRED = VERIFIED__NO
AUTHENTICATED_REPOSITORY_CONTINUATION = VERIFIED__YES
INTER_GENERATION_CROSS_WORKER_CONTINUATION = VERIFIED__HY_TO_HZ_REPOSITORY_HANDOFF
INTRA_GENERATION_CROSS_WORKER_CONTINUATION = NOT_APPLICABLE__NO_WORKER_TRANSITION
UNCOMMITTED_DELTA_RECOVERY = NOT_APPLICABLE__CLEAN_ENTRY
AUTHORITY_STATE_RECOVERY = NOT_APPLICABLE__HISTORICAL_OWNER_STATE_READ_ONLY
CROSS_WORKER_CONSTITUTIONAL_DRIFT = VERIFIED__ZERO_DETECTED
HANDOFF_SUFFICIENCY_STATUS = VERIFIED__SUFFICIENT_AFTER_REPOSITORY_RECONSTRUCTION
HANDOFF_STATE_COMPLETENESS = VERIFIED__COMPLETE_FOR_BOUNDED_HZ_SCOPE
HANDOFF_RECONSTRUCTION_REQUIRED = VERIFIED__YES
HANDOFF_RECONSTRUCTION_SUCCESS = VERIFIED__YES
HANDOFF_AMBIGUITY_COUNT = VERIFIED__0
UNAUTHENTICATED_HANDOFF_ASSUMPTION_COUNT = VERIFIED__0
```

Cognition provenance is
`VERIFIED__AUTHENTICATED_GIT_PLUS_COMMITTED_HY_HX_EVIDENCE_PLUS_CANONICAL_P11_CHE_FK_PLUS_EX_PLUS_EXISTING_PROTECTED_PROVENANCE_OWNER_PLUS_GY_HA_HP_HR_HX_PLUS_INSPECTED_FM_GN_GL_DU_EB_EE_PLUS_GOVERNANCE_LAYER_0_AND_PINNED_NESTED_AUTHORITY`.
The prompt supplied checkpoint expectations and scope but no value was accepted
as system state without repository authentication.

Required metrics:

| Metric | Result |
|---|---|
| PROJECT_PROGRESS_ESTIMATE | `ESTIMATED__WRONG_PROVENANCE_REPOSITORY_FORMALIZATION_COMPLETE__NO_TOTAL_PROJECT_PERCENTAGE` |
| CONSTITUTIONAL_HEALTH_EVIDENCE | `VERIFIED__FAIL_CLOSED_LIMITATIONS_VISIBLE__ZERO_OPERATIONAL_DRIFT` |
| SHADOW_AUTOMATION_STATUS | `VERIFIED__DISABLED__AUTO_CONTINUABLE_FALSE` |
| CONSTITUTIONAL_FRONTIER_DISTANCE | `NOT_MEASURED__NO_FORMAL_UNIVERSAL_SCALAR` |
| E05_FRONTIER_DISTANCE | `VERIFIED__9_OF_18_REMAIN` |
| SELECTED_E05_LOCAL_FRONTIER_DISTANCE | `ESTIMATED__ROUTE_BINDING_READINESS_AUTHORITY_AND_OPERATION_REMAIN` |
| GOVERNANCE_EFFICIENCE | `ESTIMATED__ONE_SELECTED_VECTOR_WITHOUT_COMMON_OR_ROUTE_EXPANSION` |
| ARCHITECTURAL_GOVERNANCE_EFFICIENCE | `ESTIMATED__EX_17_OF_17__ZERO_COMMON_RECONSTRUCTION__ZERO_ROUTE_DELTA` |
| PROOF_REUSE_EFFICIENCY | `VERIFIED__EX_17_OF_17_REUSED__ZERO_RECONSTRUCTED` |
| COGNITION_ASSISTED_HANDOFF | `VERIFIED__DURABLE_SPEC_PRODUCER_REDUCER_TESTS_REDUCTION_REPORT` |
| AIGOL_CODEX_WORK_SHARE | `NOT_MEASURED__NO_FORMAL_ATTRIBUTION_INSTRUMENT` |
| OVERENGINEERING_RISK | `ESTIMATED__LOW__NO_GENERIC_FRAMEWORK_OR_NEW_OWNER` |
| PROOF_PROCESS_OVERHEAD_RISK | `ESTIMATED__MODERATE__DUAL_OWNER_OBSERVATION_AND_INDEPENDENT_REDUCTION` |
| COGNITION_PROVENANCE | `VERIFIED__AUTHENTICATED_REPOSITORY_PRIMARY` |
| CANDIDATE_CAPABILITY | `VERIFIED__ONE_BOUNDED_CANONICAL_FIXTURE` |
| WRONG_PROVENANCE_CANDIDATE_CAPABILITY | `VERIFIED__DETERMINISTIC_ISOLATED_COORDINATE_FIXTURE` |
| WRONG_PROVENANCE_REPOSITORY_CAPABILITY | `VERIFIED__SPEC_PRODUCER_REDUCER_AND_NEGATIVE_TESTS` |
| WRONG_PROVENANCE_ROUTE_SUPPORT | `NOT_PROVEN__CURRENT_FM_CLOSED_SET_EXCLUDES_VECTOR` |
| WRONG_PROVENANCE_BINDING_STATUS | `NOT_PROVEN__NO_LIVE_BINDING` |
| WRONG_PROVENANCE_PREOPERATIONAL_READINESS | `NOT_PROVEN__ROUTE_AND_PROJECTION_ABSENT` |
| WRONG_PROVENANCE_OPERATIONAL_CAPABILITY | `NOT_PROVEN__NO_OPERATION` |
| SHADOW_DESIGN_TARGET | `VERIFIED__FORMALIZE_REUSE_VERIFY_STOP` |
| CONSTITUTIONAL_CONTINUATION_PROGRESS | `VERIFIED__HZ_FORMALIZATION_COMPLETE` |
| PROMPT_CONTEXT_REUSE_RATIO | `NOT_MEASURED__NO_FORMAL_TOKEN_ATTRIBUTION` |
| TOKEN_BENCHMARK | `NOT_MEASURED__PROVIDER_TELEMETRY_EXCLUDED` |
| LLM_COST_REDUCTION_RATIO | `NOT_MEASURED__NO_FORMAL_COST_BASELINE` |
| LCRR | `NOT_MEASURED__NO_FORMAL_COST_BASELINE` |
| E05_GENERATIONS_PER_CREDIT | `VERIFIED__LATEST_CREDIT_USED_7_VECTOR_LIFECYCLE_GENERATIONS_HR_THROUGH_HX` |
| OPERATIONAL_ATTEMPTS_PER_CREDIT | `VERIFIED__LATEST_HX_CREDIT_USED_1__HZ_USED_0` |
| MARGINAL_E05_GENERATION_COST | `VERIFIED__ONE_REPOSITORY_GENERATION__ZERO_CREDIT` |
| MARGINAL_NEW_INFRASTRUCTURE_PER_E05_CREDIT | `ESTIMATED__ONE_VECTOR_SPECIFIC_ARTIFACT_SET__NO_GOVERNED_NUMERIC_DENOMINATOR` |
| INFRASTRUCTURE_AMORTIZATION_SIGNAL | `ESTIMATED__STRONG_REUSE__ONLY_VECTOR_SPECIFIC_INFRASTRUCTURE` |
| EXPECTED_NEXT_CREDIT_GENERATION_COUNT | `ESTIMATED__AT_LEAST_ROUTE_BINDING_READINESS_AND_OPERATIONAL_PHASES_REMAIN` |

# 4. Validation Matrix

All validation is repository-only. No test invokes PRE, FM operational main,
QEMU, a VM, Human authority creation or consumption, a custody request, P11
protected entry, or protected effect.

| Validation | Result |
|---|---|
| exact entry HEAD/tree/subject/origin/remote/clean/index | `PASS` |
| HY report, HX evidence, and E05 9/18 reconstruction | `PASS` |
| nested immutable authority clean/detached/pinned | `PASS` |
| canonical WRONG_PROVENANCE and P11 D2 semantics | `PASS` |
| producer determinism and identity recomputation | `PASS` |
| authoritative provenance owner/uniqueness | `PASS` |
| focused HZ positive and negative suite | `PASS — 22/22` |
| canonical JSON, duplicate-key, malformed input | `PASS` |
| focused P11/CHE/FK regressions | `PASS — 19/19` |
| EX regressions | `PASS — 12/12; 17/17 reused` |
| affected governance tests | `PASS — 9/9` |
| governance conformance engine | `PASS — 20/20; CONFORMANT; zero warnings/violations` |
| Layer 0 affected checks | `PASS — no Layer 0 delta` |
| Python syntax/AST and no operational call sites | `PASS` |
| `git diff --check` | `PASS` |
| index remains empty | `PASS` |

Terminal counters:

```text
HUMAN_OPERATIONAL_AUTHORITY = 0
AUTHORITY_CONSUMPTION = 0
PRE = 0
FM_OPERATIONAL_LAUNCHER_INVOCATION = 0
QEMU = 0
VM_CREATION = 0
VM_BOOT = 0
OPERATION_ATTEMPT = 0
REQUEST = 0
P11_ENTRY = 0
PROTECTED_INVOCATION = 0
PROTECTED_EFFECT = 0
RETRY = 0
REPAIR_RETRY = 0
REPLAY = 0
E05_CREDIT = 0
E05_BEFORE_HZ = 9/18
E05_AFTER_HZ = 9/18
```

# 5. Repository Mutation Summary

HZ adds only:

- one sealed formal specification;
- one repository-only deterministic producer;
- one independent fail-closed reducer;
- one focused repository-only test module;
- one sealed terminal reduction;
- this G48 report.

Prior certified evidence, P11/CHE/FK, EX, FM, context owners, adapters, GN/GL,
DU/EB/EE, checkout projection, governance implementation, Layer 0, nested
authority, and historical/composite worktree remain unchanged. All HZ changes
remain unstaged. No next-generation prompt or G77-256IA artifact is prepared.

# 6. Certification Verdict

```text
CURRENT_E05_STATUS = VERIFIED__9_OF_18
WRONG_PROVENANCE_FORMALIZATION_STATUS = VERIFIED
WRONG_PROVENANCE_PRODUCER_STATUS = VERIFIED
WRONG_PROVENANCE_REDUCER_STATUS = VERIFIED
AUTHORITATIVE_PROVENANCE_RESOLUTION_STATUS = VERIFIED__UNIQUE_EXISTING_PROTECTED_OWNER
WRONG_PROVENANCE_CANDIDATE_CAPABILITY = VERIFIED
WRONG_PROVENANCE_REPOSITORY_CAPABILITY = VERIFIED
WRONG_PROVENANCE_ROUTE_SUPPORT = NOT_PROVEN
WRONG_PROVENANCE_BINDING_STATUS = NOT_PROVEN
WRONG_PROVENANCE_PREOPERATIONAL_READINESS = NOT_PROVEN
WRONG_PROVENANCE_OPERATIONAL_CAPABILITY = NOT_PROVEN
EXPECTED_DENIAL_STAGE = D2_PRECLAIM_AUTHORITY_BINDING_VALIDATION_BEFORE_PRECLAIM_LEDGER_APPEND_CLAIM_ENTRY_INVOCATION_OR_EFFECT
EXPECTED_DENIAL_REASON = operational Human act input_record_identity binding is invalid
EXPECTED_DENIAL_REACHABILITY_STATUS = VERIFIED__EARLIER_RECORD_IDENTITY_BINDING_DENIAL__PROVENANCE_SPECIFIC_COMPARISON_NOT_REACHED
INDEPENDENT_MUTATION_COUNT = 1
INDEPENDENT_MUTATED_COORDINATE = provenance_identity
DEPENDENT_RECOMPUTATION_COUNT = 1
DEPENDENT_RECOMPUTED_COORDINATE = record_identity
LAST_VERIFIED_EDGE = WRONG_PROVENANCE_REPOSITORY_FORMAL_SPECIFICATION_PRODUCER_REDUCER_AUTHORITATIVE_PROVENANCE_RESOLUTION_AND_FAIL_CLOSED_TESTS
FIRST_BROKEN_EDGE = WRONG_PROVENANCE_EXISTING_SINGLE_ROUTE_SUPPORT_AND_LIVE_BINDING_ABSENT
MINIMUM_MISSING_CAPABILITY = HUMAN_REVIEW_AND_COMMIT_THEN_SEPARATELY_BOUNDED_EXISTING_ROUTE_EXTENSION_DECISION
MINIMUM_LEGAL_NEXT_DELTA = AFTER_HUMAN_REVIEW_AND_COMMIT_OF_HZ__ONE_SEPARATELY_BOUNDED_REPOSITORY_ONLY_EXISTING_SINGLE_ROUTE_EXTENSION_GENERATION_IF_STILL_SELECTED__NO_AUTHORITY__NO_OPERATION
EX_REUSED = 17/17
EX_RECONSTRUCTED = 0
PRODUCTION_ROUTE_BEFORE = 1
PRODUCTION_ROUTE_AFTER = 1
PRODUCTION_ROUTE_DELTA = 0
NEW_GENERIC_FRAMEWORK_COUNT = 0
NEW_AUTHORITY_LAYER_COUNT = 0
NEW_PRODUCTION_ROUTE_COUNT = 0
NEW_RUNTIME_OWNER_COUNT = 0
AUTO_CONTINUABLE = NO
HUMAN_AUTHORIZATION_REQUIRED = NO
HUMAN_REVIEW_REQUIRED = YES
```

VERIFIED__G77_256HZ_WRONG_PROVENANCE_REPOSITORY_ONLY_FORMALIZATION_COMPLETE__AUTHORITATIVE_PROVENANCE_UNIQUELY_RESOLVED_FROM_EXISTING_PROTECTED_CUSTODY_OWNER__ONE_INDEPENDENT_PROVENANCE_IDENTITY_MUTATION_AND_ONE_DEPENDENT_RECORD_IDENTITY_RECOMPUTATION__EXPECTED_EARLIER_RECORD_IDENTITY_DENIAL_FORMALIZED__NO_ROUTE_BINDING_AUTHORITY_OPERATION_OR_E05_CREDIT__E05_REMAINS_9_OF_18__HUMAN_REVIEW_REQUIRED
