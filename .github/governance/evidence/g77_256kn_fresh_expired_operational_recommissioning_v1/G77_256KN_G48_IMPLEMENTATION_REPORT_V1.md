# 1. Implementation Summary

G77-256KN authenticated the exact committed and pushed KM checkpoint, stable
ancestry, and the clean detached pinned nested authority. It then performed
exactly one fresh EXPIRED SPCE Phase-A construction using KM's schema-preserving
KI-preflight binding and stopped successfully at the Human authority barrier.

KN did not reopen or retry KL. It created no Human authority, accepted no Human
decision, entered no Phase B, invoked no operational PRE/FM path, started no
QEMU or VM, created no operational request, entered no P11 boundary, and caused
no protected invocation or effect.

`TERMINAL = A__FRESH_KN_EXPIRED_PREAUTHORIZATION_PRESENTATION_READY_FOR_HUMAN_DECISION`

`AUTHENTICATED_HEAD = 1141f9f1dd2069e250c6ad44dc90164597366ffe`

`AUTHENTICATED_TREE = 70aa2a12af3d9806e0d6ddc73f7f751292413e52`

`AUTHENTICATED_SUBJECT = G77-256KM preserve GN schema for KI preflight binding`

`REMOTE_HEAD = 1141f9f1dd2069e250c6ad44dc90164597366ffe`

`REMOTE_EQUALITY = VERIFIED__DIRECT_BRANCH_LS_REMOTE`

`PROJECT_STATE = VERIFIED__KN_PHASE_A_READY_AT_HUMAN_BARRIER`

`PROJECT_PROGRESS = VERIFIED__FRESH_KN_COORDINATES_SCHEMA_EXACT_REQUEST_PRESENTATION_AND_SAFE_STOP_SEALED`

`PROJECT_PROGRESS_ESTIMATE = NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR`

`INFORMAL_PROJECT_PROGRESS_ESTIMATE = ESTIMATED__PHASE_A_COMPLETE__SEPARATE_HUMAN_DECISION_REQUIRED`

The pre-commit Layer 0 warning recorded at the KM checkpoint remains a known
warning only: `freeze_version=core_constitutional_v1.0` differs from the
repository describe value. The freeze manifest passed and no new evidence
promotes that warning into a blocker.

# 2. Code Evidence

## Fresh KN coordinates

`GENERATION = G77_256KN_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1`

`OPERATION = G77_256KN_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001`

`CANDIDATE_SHA256 = 8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a`

`CONTEXT = 37f5c7d46b305b6e6e6b912dd136917c96ad4c783341aa62cd1dc4994e6f5b4b`

`CONTEXT_FILE_SHA256 = adafd6cdc2bef25119e098e11a69a79cdc893656bc9471f72e4e6a85ca5e7695`

`CANONICAL_ARGV_SHA256 = 96480352c744c6feb9d743fafc7eae111a143ebde6b18cf67160e05ac1e93816`

`TEMPORAL_BINDING = cc46cded2aa3c294ad84c172619092889639fb74dda5f32ec68645508a2a1f56`

`REQUEST_IDENTITY = 9c5941b007e5939da928b7e1cc6cf0668a8e20b29f75bbe29964520645eb57d5`

`REQUEST_FILE_SHA256 = f980e8cd5ac48c97bbc61a0f891f103e8305f14847a59333b39912024609831d`

`AUTHORIZATION_PRESENTATION_SHA256 = 71cc222249ad75b2b420d749c2d4bd66cf0bd2d982f054102384ddb14993e2ac`

`HUMAN_DECISION_PRESENTATION_SHA256 = 9b95f4ad710b607b0c8607da4b2b720d5e8bf94929f4f39dc4e121cc5b5f2f12`

`READINESS_CHECKPOINT = d26523b800ec42a3b3d0036087eaf110bb1b786dba455e13edd97d115ab1eb39`

`READINESS_CHECKPOINT_FILE_SHA256 = a178e6621e9d232d48143e353660e6dba8ce524059a8ad69d0c908cd7aa07a5f`

`SAFE_STOP_CHECKPOINT = 965e892b39bfc3b1215a842703d186177ac39cf54565e51ad2147e2fd4742a1b`

`SAFE_STOP_CHECKPOINT_FILE_SHA256 = 5bc8f9a4b2c012cb45460a661aaf5642de222c1fbefc04b74ddb2abd159fc3f0`

The immutable candidate bytes are reused, as required by the established
route. Their KN binding is fresh because the KN generation, operation,
context, context file, canonical argv, temporal binding, request,
presentation, readiness, and safe-stop identities are all distinct from KL.

## KM and GN binding

The committed KM reduction file SHA-256 is
`b76a42cd95b5d227ba64fe5c7d8e777143f915d296d8d5811a3eec449e7751a4`;
its authenticated inner seal is
`73a8d430c1ffd51bbfd8e39b51c08f66a1cc6550038153e0a58d19163d6c691d`.
The corrected KJ binder SHA-256 is
`fcc1a60fdbc3fb246d918ac2e8143bd4888e3e65ebc2e3769298a039c5aeebbf`.

KN preserves the exact GN `PREAUTHORIZATION_FIELDS` set:

- `all_operational_counters_zero`;
- `checkpoint_file_sha256`;
- `checkpoint_inner_sha256`;
- `checkpoint_path`;
- `complete_deterministic_readiness`;
- `gk_receipt_parent_false_positive_blocked`;
- `preauth_final_admission_equivalence`;
- `preauth_final_admission_equivalence_file_sha256`;
- `receipt_parent_observation_file_sha256`;
- `static_readiness_file_sha256`.

`GN_EXACT_PREAUTHORIZATION_FIELD_COUNT = VERIFIED__10`

`GN_EXACT_PREAUTHORIZATION_SCHEMA = VERIFIED__UNCHANGED`

`GN_VALIDATION_WEAKENED = VERIFIED__NO`

`SECOND_ACCEPTED_GN_SCHEMA = VERIFIED__NO`

`FALLBACK = VERIFIED__ABSENT`

`ALIAS = VERIFIED__ABSENT`

`PARALLEL_AUTHORITY_PATH = VERIFIED__NO`

The generated KN request is accepted by the unchanged GN owner. Unknown-field
and missing-field negatives remain rejected with
`SEALED_REQUEST_PREAUTHORIZATION_INVALID`. Neither removed KI digest appears
directly in the request's GN-owned object.

The authenticated evidence chain is:

`KI preflight -> sealed readiness checkpoint -> checkpoint_file_sha256 + checkpoint_inner_sha256 -> sealed GN request`

The KM closure preflight is bound through the same surrounding checkpoint
pattern. This adds evidence metadata without altering GN authority semantics.

`KI_PREFLIGHT_BINDING = VERIFIED__KM_SCHEMA_PRESERVING_PATH_USED`

`FRESH_KN_PHASE_A_PRESENTATION_READY = VERIFIED`

`SAFE_STOP_CHECKPOINT = VERIFIED`

`HUMAN_DECISION_PRESENTATION = VERIFIED__FRESH_KN_EXACT_PRESENTATION_CREATED`

# 3. Constitutional Self-Assessment

## Failure novelty and convergence

`FAILURE_CLASS = PROOF_GAP`

`NOVELTY = VERIFIED__NOT_NEW__KM_CLOSED_GN_SCHEMA_EDGE__EXPIRED_OPERATIONAL_OBSERVATION_REMAINS`

`AFFECTED_INVARIANT = E05_EXPIRED_REQUIRES_FRESH_HUMAN_AUTHORIZED_DENIAL_BEFORE_P11_ENTRY`

`PREVIOUS_CLOSEST_EDGE = KM_GN_SCHEMA_PRESERVING_KI_PREFLIGHT_BINDING_REPOSITORY_VERIFIED`

`SEMANTIC_DIFFERENCE = VERIFIED__NO_NEW_CONSTITUTIONAL_SEMANTIC_AUTHORITY_PRODUCTION_PATH_OR_OPERATIONAL_DIFFERENCE`

`PRODUCTION_BEHAVIOR_IMPACT = VERIFIED__NONE__KN_PHASE_A_IS_NONOPERATIONAL`

`NEW_CAPABILITY_REQUIRED = NOT_PROVEN`

`NEW_PROOF_REQUIRED = VERIFIED__FRESH_OPERATIONAL_EXPIRED_OBSERVATION_REMAINS_AFTER_SEPARATE_HUMAN_AUTHORITY`

`CONVERGENCE_SIGNAL = VERIFIED__KM_LOCAL_EDGE_CLOSED__KN_REUSES_ONE_CONVERGED_PHASE_A_CHAIN__E05_UNCHANGED`

`REPETITION_PRESSURE = ESTIMATED__HIGH__MULTIPLE_PRIOR_PHASE_A_GENERATIONS_ZERO_E05_CREDIT`

`VERIFICATION_AMPLIFICATION_RISK = VERIFIED__HIGH_IF_PHASE_A_IS_REPEATED_AFTER_KN_WITHOUT_HUMAN_DECISION_OR_NEW_EVIDENCE`

`CLASSIFICATION_EVIDENCE = VERIFIED__KM_CANONICAL_SEAL__KI_FRONTIER__GN_EXACT_SCHEMA__EX_17_OF_17__KN_ZERO_OPERATION`

`CLASSIFICATION_CONFIDENCE = VERIFIED__HIGH`

`ACCEPTANCE_REQUIREMENT_FORCING_CONTINUATION = VERIFIED__E05_EXPIRED_REMAINS_NOT_PROVEN_OPERATIONALLY__KN_AUTHORIZED_ONLY_TO_HUMAN_BARRIER`

## Cross-vector reuse assessment

`CROSS_VECTOR_REUSE_SCOPE = VERIFIED__MULTI_VECTOR_REUSABLE`

`REUSABLE_COMPONENT = GN_EXACT_PREAUTHORIZATION_OWNER_AND_SEALED_CHECKPOINT_EVIDENCE_BINDING_PATTERN`

`REUSE_INVARIANT = OWNER_OWNED_EXACT_SEMANTIC_OBJECT_MUST_NOT_BE_EXPANDED_BY_EVIDENCE_ONLY_METADATA`

`APPLICABLE_VECTORS = EXPIRED__FUTURE__WRONG_ATTEMPT__WRONG_CONTRACT__WRONG_INPUT__WRONG_PROVENANCE`

`VECTOR_SPECIFIC_RESIDUE = EACH_VECTOR_PREFLIGHT_SEMANTICS__FRESH_AUTHORITY__OPERATIONAL_ACCEPTANCE__E05_CREDIT`

`REUSE_PRECONDITIONS = SAME_AUTHENTICATED_GN_OWNER__EXACT_TEN_FIELDS__SEALED_PREFLIGHT__SEALED_READINESS__EXISTING_CHECKPOINT_DIGEST_FIELDS`

`REVALIDATION_REQUIRED = VERIFIED__PER_GENERATION_BINDINGS_AND_PER_VECTOR_OPERATIONAL_REQUIREMENTS`

`EXPECTED_FUTURE_PROOF_REDUCTION = ESTIMATED__REUSE_COMMON_SCHEMA_PLACEMENT_PROOF__DO_NOT_REPROVE_OR_RECONSTRUCT__NO_VECTOR_OPERATIONAL_CREDIT`

GN's supported-vector set authenticates multi-vector reuse, but it does not
cover every E05 vector. KM is therefore not classified as universal common
E05 infrastructure. Common proof reuse is not vector operational proof, and
multi-vector reuse is not authority transfer.

## Governance, E05, and frontier

`CONSTITUTIONAL_HEALTH_EVIDENCE = VERIFIED__KM_SCHEMA_BINDING_USED__GN_STRICT__ALL_COUNTERS_ZERO__NO_AUTHORITY__ONE_ROUTE`

`SHADOW_AUTOMATION_STATUS = VERIFIED__ABSENT`

`CONSTITUTIONAL_FRONTIER_DISTANCE = NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR`

`GOVERNANCE_EFFICIENCE = ESTIMATED__HIGH__EX_17_OF_17_AND_MULTI_VECTOR_SCHEMA_BINDING_REUSED`

`OVERENGINEERING_RISK = ESTIMATED__HIGH_IF_PHASE_A_IS_REPEATED_AFTER_KN_WITHOUT_HUMAN_DECISION_OR_NEW_EVIDENCE`

`COGNITION_PROVENANCE = VERIFIED__COMMITTED_KM_KI_GN_EX_AND_DETERMINISTIC_KN_EVIDENCE_PRIMARY`

`COGNITION_ASSISTED_HANDOFF = VERIFIED__REPOSITORY_ONLY_REPLAY_SAFE_KN_PHASE_A`

`CANDIDATE_CAPABILITY = VERIFIED__FRESH_KN_PHASE_A_READINESS_ONLY__EXPIRED_DENIAL_NOT_PROVEN`

`SHADOW_DESIGN_TARGET = VERIFIED__SOLE_FM_ER_P11_ROUTE_WITH_KF_PERMISSION_AND_KM_SCHEMA_BINDING`

`CONSTITUTIONAL_CONTINUATION_PROGRESS = VERIFIED__KM_SCHEMA_EDGE_CLOSURE_TO_KN_HUMAN_BARRIER`

`LAST_VERIFIED_OPERATIONAL_EDGE = EXACT_HUMAN_AUTHORITY_AUTHENTICATED_JZ_BOUND_CONSUMED_ONCE_AND_ONE_NO_NETWORK_VM_BOOT_REACHED_GUEST_CUSTODY_LOAD`

`FIRST_UNVERIFIED_OPERATIONAL_EDGE = FRESH_HUMAN_AUTHORIZED_EXPIRED_DENIAL_BEFORE_P11_ENTRY_AFTER_KF_REPAIR`

`LAST_VERIFIED_EDGE = FRESH_KN_PHASE_A_PRESENTATION_AND_ALL_REQUIRED_PREFLIGHTS_READY_USING_KM_SCHEMA_PRESERVING_BINDING`

`FIRST_BROKEN_EDGE = EXACT_FRESH_KN_HUMAN_AUTHORIZATION_NOT_YET_SUPPLIED`

`CURRENT_REAL_BLOCKER = VERIFIED__EXACT_FRESH_KN_HUMAN_AUTHORIZATION_NOT_YET_SUPPLIED`

`MINIMUM_MISSING_CAPABILITY = EXACT_FRESH_HUMAN_AUTHORIZATION_FOR_BOUND_KN_EXPIRED_OPERATION`

`MINIMUM_LEGAL_NEXT_DELTA = ONLY_AFTER_SEPARATE_EXACT_HUMAN_AUTHORIZATION__SAME_G77_256KN_SPCE_PHASE_B_ONE_CONSUMPTION_ONE_OPERATION_ATTEMPT`

`E05_STATE = VERIFIED__11_OF_18`

`E05_FRONTIER = VERIFIED__7_UNSATISFIED_OF_18`

`E05_CREDIT = VERIFIED__0`

`KN_PHASE_A_E05_CREDIT = VERIFIED__0`

`EXPIRED = NOT_PROVEN_OPERATIONALLY`

`EX_REUSED = VERIFIED__17_OF_17`

`EX_RECONSTRUCTED = VERIFIED__0`

The legacy EX validator remains point-in-time. Committed JP evidence preserves
the known single `ER_OPERATIONAL_HARNESS` `REQUIRES_HARDENING` successor
distinction and all 17 certified common components; KN does not weaken or
rewrite that validator.

## Architectural delta, proof yield, and CCWIM

`ARCHITECTURAL_DELTA_BUDGET = VERIFIED__ZERO_PRODUCTION_P11_OWNER_ROUTE_REGISTRY_GENERIC_ABSTRACTION_AND_CONSTITUTIONAL_CONCEPT_MUTATIONS__GENERATION_LOCAL_PHASE_A_ONLY__ONE_ROUTE_PRESERVED`

`PRODUCTION_MUTATION_COUNT = 0`

`P11_IMPLEMENTATION_MUTATION_COUNT = 0`

`NEW_OWNER_COUNT = 0`

`NEW_ROUTE_COUNT = 0`

`NEW_REGISTRY_COUNT = 0`

`NEW_GENERIC_ABSTRACTION_COUNT = 0`

`NEW_CONSTITUTIONAL_CONCEPT_COUNT = 0`

`PRODUCTION_ROUTE_BEFORE = 1`

`PRODUCTION_ROUTE_AFTER = 1`

`PARALLEL_FLOW = NO`

`NEW_VERIFIED_CAPABILITY_COUNT = VERIFIED__1__FRESH_KN_PHASE_A_READINESS_ONLY`

`NEW_OPERATIONAL_CAPABILITY_COUNT = VERIFIED__0`

`NEW_BLOCKER_LOCALIZED_COUNT = VERIFIED__0`

`NEW_BLOCKER_CLOSED_COUNT = VERIFIED__0__HUMAN_BARRIER_EXPECTED`

`NEW_FALSE_OR_SUPERSEDED_BLOCKER_REMOVED_COUNT = VERIFIED__0`

`NEW_CLASSIFICATION_RESULT_COUNT = VERIFIED__1__PROOF_GAP_REAUTHENTICATED`

`PROOF_REUSE_COUNT = VERIFIED__17__EX_COMMON_COMPONENTS`

`CCWIM_MATURITY_LEVEL = ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION`

`AUTHENTICATED_REPOSITORY_CONTINUATION = VERIFIED__YES`

`PREVIOUS_WORKER_CONVERSATION_REQUIRED = VERIFIED__NO`

`PREVIOUS_WORKER_MEMORY_REQUIRED = VERIFIED__NO`

`HANDOFF_RECONSTRUCTION_SUCCESS = VERIFIED__YES`

`HANDOFF_AMBIGUITY_COUNT = VERIFIED__0`

`OBSERVED_ARTIFACT_LEVEL_CROSS_WORKER_DRIFT = VERIFIED__0`

`HAC_HAI_HAE = NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED`

Periodic work-share, prompt reuse, token, LCRR, and full-CCWIM metrics are not
reported because no governed measurement instruments or denominators exist.

## Reuse Impact Assessment

1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?

   `VERIFIED__EX_17_OF_17__KM__KI__KH__JZ__KB__KD__KF__KG_PHASE_A_PATTERN__GN__FM__ER__P11__SOLE_ROUTE`.

2. Katere nove zmogljivosti (če sploh) nastanejo?

   One fresh KN Phase-A readiness capability is verified; zero production or
   operational capabilities are created.

3. Ali katera obstoječa zmogljivost postane nedosegljiva?

   `VERIFIED__NO`.

4. Ali implementacija ustvarja vzporedni tok?

   `VERIFIED__NO`.

5. Ali zmanjšuje ali povečuje število produkcijskih poti?

   `VERIFIED__UNCHANGED__1_TO_1`.

# 4. Validation Matrix

| Validation | Result |
|---|---|
| Exact KM HEAD/tree/subject/origin and direct remote equality | PASS |
| Clean entry worktree, empty entry index, and stable ancestry | PASS |
| Nested clean, detached, pinned identity and remote-tag equality | PASS |
| Committed KM terminal, canonical seal, exact two-field correction, and unchanged GN owner | PASS |
| GN exact ten-field schema and canonical request seal | PASS |
| GN unknown-field and missing-field negatives | PASS: `SEALED_REQUEST_PREAUTHORIZATION_INVALID` |
| KI and KM evidence bound through sealed readiness and existing GN checkpoint fields | PASS |
| Fresh KN generation, operation, context, argv, temporal, request, presentation, readiness, and safe-stop identities | PASS |
| Immutable candidate reused under fresh KN bindings | PASS |
| Exact GN-derived authorization presentation and request equivalence | PASS |
| Exact Human decision presentation and safe-stop binding | PASS |
| No historical authority reuse, Phase B, operational artifact, P11 entry, or protected effect | PASS |
| All 15 operational counters and KN E05 credit zero | PASS |
| EX certificate/final seal and JP successor distinction; 17-of-17 reuse | PASS |
| Cross-vector reuse bounded to GN's six authenticated vectors | PASS |
| One Phase-A construction; materializer fresh-collision guards active; no retry | PASS |
| Focused KN tests | PASS |
| Governance conformance | PASS |
| Syntax/AST, canonical JSON, and seals | PASS |
| G48 exactly six H1 and RIA exactly five questions | PASS |
| `git diff --check` and final index empty | PASS |

Expected historical mismatch is kept visible: the KM point-in-time suite
reports `1 failed, 6 passed` because its deterministic reconstruction is pinned
to pre-KM HEAD `6f75d96a…`, whereas KN correctly entered at committed KM HEAD
`1141f9f1…`. No historical test or validator was rewritten.

# 5. Repository Mutation Summary

KN adds generation-local Phase-A orchestration, live binding, operation-state
materialization without operational invocation, repository preflights, an exact
GN request and presentation, a Human decision presentation, safe-stop evidence,
one success verifier, focused tests, and this report. No pre-KN file, production
owner, P11 implementation, route, registry, constitutional artifact, EX
artifact, or nested-authority file is changed.

All KN operational counters are zero:

`OPERATIONAL_AUTHORIZATION_COUNT = 0`

`AUTHORITY_CONSUMPTION_COUNT = 0`

`PRE_OPERATIONAL_INVOCATION_COUNT = 0`

`FM_OPERATIONAL_INVOCATION_COUNT = 0`

`QEMU_START_COUNT = 0`

`VM_START_COUNT = 0`

`OPERATION_ATTEMPT_COUNT = 0`

`OPERATION_REQUEST_COUNT = 0`

`EXPIRED_DENIAL_COUNT = 0`

`P11_ENTRY_COUNT = 0`

`PROTECTED_INVOCATION_COUNT = 0`

`PROTECTED_EFFECT_COUNT = 0`

`RETRY_COUNT = 0`

`REPAIR_RETRY_COUNT = 0`

`REPLAY_COUNT = 0`

# 6. Certification Verdict

KN certifies exactly one fresh nonauthority EXPIRED Phase-A construction and
the exact presentation/safe-stop handoff at the Human barrier. It does not
certify Human authority, Phase B, EXPIRED operational denial, E05 credit, or
any operational capability.

`HUMAN_AUTHORITY_PRESENT = NO`

`AUTHORITY_CONSUMPTION_COUNT = 0`

`PHASE_B_STARTED = NO`

`AUTO_CONTINUABLE = NO`

`HUMAN_REVIEW_REQUIRED = YES`

G48 exactly-six-H1 result: `VERIFIED__6_OF_6__NO_SEVENTH_H1`.

STOP AT THE HUMAN AUTHORITY BARRIER. DO NOT STAGE, COMMIT, PUSH, ACCEPT
AUTHORITY, START PHASE B, OR PERFORM AN OPERATION.
