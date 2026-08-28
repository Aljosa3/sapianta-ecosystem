# 1. Implementation Summary

Generation: G77-256FC

Report identity: `G77_256FC_CROSS_ACCOUNT_ONE_SHOT_WRONG_ATTEMPT_OPERATIONAL_COMMISSIONING_V1`

Constitutional baseline: `constitutional-governance-finalize-v1`; Git commit `f2626906b9a95631d921e6bb9a6947400c03a028`; tree `977a5a5a43350dbe2270778a806dd20d6a31e87b`; subject `G77-256FA commission CONSUMED at E05`.

Human selection and authorization: `HUMAN_AUTHORIZATION` and `HUMAN_SELECTION` establish exactly one bounded generation for `P11-E05/NEGATIVE_AUTHORITY/WRONG_ATTEMPT`. This report, its checkpoints, candidate, and Codex interpretation are not authority.

Outcome:

`PROVEN — FAIL_CLOSED__FIRST_FRESH_CANDIDATE_REJECTED_BY_DU_BEFORE_EB_EE_MATERIALIZATION_OR_EXECUTION`

The exact entry gate passed. Repository evidence independently authenticated FA credit, E05 `6/18`, WRONG_ATTEMPT as unsatisfied and admissible, and EX as the sole certified common substrate with 17 certified components. EX, EW, and EU validators passed 12/12, 17/17, and 18/18 respectively. One fresh candidate and byte-identical runtime projection were then created.

The first authoritative candidate preflight failed. The committed DU validator rejected `selected_case` because it contained five fields outside the exact canonical schema: `authorized_attempt_identity`, `isolated_semantic_mutation_field`, `obligation_id`, `other_vector_mutation_count`, and `supplied_wrong_attempt_identity`. The candidate was not edited or replaced. EB and EE were not run. No materialization, VM, boot, QEMU execution, P11 request, E05 execution, retry, repair, P12 entry, or production route occurred.

Reduction:

```text
FINAL_VALIDATION = PASS__TRUTHFUL_FAIL_CLOSED_FINALIZATION__OPERATIONAL_OBJECTIVE_NOT_ACHIEVED
CONSTITUTIONAL_CREDIT_RESULT = NOT_AWARDED
E05_BEFORE = 6/18
E05_AFTER = 6/18
E05_REMAINING = 12
WRONG_ATTEMPT_STATE_AFTER = UNSATISFIED
AUTO_CONTINUABLE = NO
```

The failure is vector-candidate schema incompatibility, not a proven EX invalidation trigger and not a new common constitutional gap. The rejected fields have existing generation-specific evidence roles outside the fixed DU `selected_case` shape. Repair inside FC is prohibited by the Human one-candidate rule.

# 2. Code Evidence

No runtime public API, constitutional artifact, common validator, common manifest, production path, or shared execution infrastructure was changed.

The FC delta consists of:

- one generation-bound candidate builder;
- one WRONG_ATTEMPT adapter over exact ER harness SHA-256 `4a2a84ff83c61bfec013b4bcd20eb16905eeb240869182edd6c0d948444bae89`;
- three cloud-init inputs; and
- one candidate plus byte-identical runtime projection.

The adapter source statically defines exactly one `RAW_ROOT` and one `CONTINUATION_MANIFEST_PATH`. Its intended vector rule is to create one fresh valid act bound to `G77_256FC_E05_AUTHORIZED_ATTEMPT_001`, then present one otherwise-equal canonical request with `attempt_identity` changed to `G77_256FC_E05_SUPPLIED_WRONG_ATTEMPT_002`; canonical `record_identity` is the only dependent byte identity recomputed. Because DU failed first, these runtime semantics were not executed and receive no operational credit.

Exact principal artifact identities:

| Artifact | SHA-256 |
| --- | --- |
| Phase A checkpoint | `e631d583ee5a0fa1b47a4ccdd3977944f6f1c8d6a76444c236d0d109ca13e998` |
| Phase A inner checkpoint | `4244b56140bdcd94854edf1007c75d2ff3f0ad1e61f774efd41e25e77b813e99` |
| Builder | `e10defbfaf6303f5887f20316bfc2738e559d6769ccb146b62577d696f042db5` |
| Adapter | `ef564f54fc764ed3968d94365a56a09f06025ea1f534c4a08f818183ddef2e8d` |
| Candidate | `0b1133abee4dbd4a67755726096a46a09a7b0603d00ce855fb8ce997254ace7a` |
| Runtime projection | `0b1133abee4dbd4a67755726096a46a09a7b0603d00ce855fb8ce997254ace7a` |
| Phase B fail-closed checkpoint | `b73a44658f2cd601d721235d0d680e63ded33a7e48758dae5fb0086c66084a73` |
| Phase B inner checkpoint | `ce3664ab6a53945c1d1ba3a23b2bf7cf53b4aa65ec302bcec46cbd78d28917aa` |

Candidate and runtime projection are byte-identical. Their identical bytes remain sealed and unchanged after failure.

Deterministic preflight evidence:

```text
DU_RESULT = FAIL_CLOSED__UNKNOWN_FIELD
DU_FAILURE_STAGE = STRUCTURAL_SCHEMA_VALIDITY
EB_RESULT = NOT_RUN__DU_FAILED_FIRST
EE_RESULT = NOT_RUN__DU_FAILED_FIRST
B6_REPOSITORY_PRECONDITION = NOT_ESTABLISHED__DU_FAILED_BEFORE_EB_EE
```

The exact DU error is:

```text
UNKNOWN_FIELD: selected_case has unknown fields ['authorized_attempt_identity', 'isolated_semantic_mutation_field', 'obligation_id', 'other_vector_mutation_count', 'supplied_wrong_attempt_identity']
```

Evidence graph:

```text
FA committed 6/18 frontier
  -> EX/EW/EU authenticated common substrate
  -> Phase A repository checkpoint
  -> one FC builder invocation
  -> one candidate == one runtime projection
  -> DU structural schema rejection
  -> no EB / no EE / no materialization / no execution
  -> fail-closed independent reduction
```

# 3. Constitutional Self-Assessment

Verified and proven:

- exact FA HEAD, tree, subject, clean entry worktree, and empty entry index;
- fresh Human selection and one-generation authorization;
- FA final validation, CONSUMED credit, and current E05 `6/18` state;
- WRONG_ATTEMPT remains unsatisfied and repository-admissible;
- repository-mediated cross-account continuation required no prior conversation or full-history reconstruction;
- EX authenticity, 17 available certified components, zero common reconstruction, and no EX invalidation trigger;
- one candidate, zero replacement candidates, and byte-identical candidate/runtime projection;
- first authoritative failure at DU structural validation;
- zero materialization, VM, boot, QEMU, P11, E05 operational, P12, and production counts;
- zero retry and repair-and-continue; and
- protected committed lineage was not modified.

Not established:

- operational WRONG_ATTEMPT isolation, functional denial, or counter behavior;
- fresh B1 actual-executed-call evidence;
- fresh B2 physical base-image custody evidence;
- fresh B6 operational producer/consumer evidence;
- EB or EE candidate/runtime admission;
- SPCE operational resumability; and
- any E05 transition beyond 6/18.

Required metrics:

`PROJECT_PROGRESS_ESTIMATE = ESTIMATED__WHOLE_REPOSITORY_60_TO_70_PERCENT__NO_CERTIFIED_PROJECT_DENOMINATOR`

`ARCHITECTURAL_PROGRESS_ESTIMATE = ESTIMATED__85_TO_90_PERCENT__CANONICAL_GOVERNANCE_ARCHITECTURE_MATURE_WITH_VISIBLE_KNOWN_GAPS`

`IMPLEMENTATION_MATURITY_ESTIMATE = ESTIMATED__70_TO_80_PERCENT__REUSABLE_SUBSTRATE_EXISTS_BUT_FRONTIER_REMAINS_OPEN`

`OPERATIONAL_COMMISSIONING_MATURITY_ESTIMATE = ESTIMATED__35_TO_45_PERCENT__E05_REMAINS_6_OF_18__P12_AND_PRODUCTION_UNOPENED`

`AUTOMATION_MATURITY_ESTIMATE = ESTIMATED__45_TO_55_PERCENT__DETERMINISTIC_BUILD_AND_VALIDATION_EXIST__SELECTION_AUTHORIZATION_CREDIT_AND_COMMIT_REMAIN_HUMAN_CONTROLLED`

`CONSTITUTIONAL_HEALTH_EVIDENCE = PROVEN__EXACT_ENTRY__FAIL_CLOSED_FIRST_FAILURE__ONE_CANDIDATE__ZERO_OPERATIONAL_PROGRESSION__ZERO_RETRY__IMMUTABLE_LINEAGE__ZERO_P12_PRODUCTION`

`CONSTITUTIONAL_HEALTH = PASS__FAIL_CLOSED_BOUNDARIES_PRESERVED__FC_OPERATIONAL_OBJECTIVE_NOT_ACHIEVED`

`SHADOW_AUTOMATION_STATE = PARTIAL__CANDIDATE_BUILD_AND_DU_REJECTION_AUTOMATED__OPERATIONAL_CHAIN_NOT_ENTERED`

`SHADOW_AUTOMATION_READINESS = NOT_READY_FOR_WRONG_ATTEMPT_OPERATIONAL_EXECUTION__FRESH_CANDIDATE_MUST_FIRST_CONFORM_TO_DU`

Automatable common proof steps are exact Git authentication, EX/EW/EU regression, hashes, canonical candidate production, DU/EB/EE validation, evidence sealing, and deterministic reduction. Vector preparation can be automated only within the fixed DU schema. Operational evidence steps were not reached. Human selection, authorization, constitutional credit review, commit, P12 entry, and production promotion remain Human Authority steps. Automation is not authority.

`CONSTITUTIONAL_FRONTIER_DISTANCE = NOT_MEASURED__MULTIDIMENSIONAL_FRONTIER`

`CONSTITUTIONAL_FRONTIER_DISTANCE_E05 = FACT__12_CASES_REMAIN`

`CONSTITUTIONAL_FRONTIER_DISTANCE_SUBSTRATE = FACT__EX_COMMON_SUBSTRATE_CERTIFIED__FRESH_B1_B2_B6_AND_VECTOR_ADMISSION_REMAIN_PER_OPERATIONAL_GENERATION`

Broader boundaries remain: G2 open, G3 unauthorized, P12 entry zero, and production routes/effects zero.

`GOVERNANCE_EFFICIENCE = MEASURED__COMMON_SUBSTRATE_RECONSTRUCTION_0__NEW_COMMON_COMPONENTS_0__NEW_COMMON_INFRASTRUCTURE_0__VECTOR_SPECIFIC_COMPONENTS_2__FRESH_CANDIDATES_1__MATERIALIZATIONS_0__VMS_0__BOOTS_0__QEMU_EXECUTIONS_0__RETRIES_0__REPAIRS_0`

FC does not establish that 6/18 to 7/18 is cheaper than FA's 5/18 to 6/18 sequence because 7/18 was not achieved. It does show that repository authentication and early schema rejection avoided materialization and operational cost.

`COGNITION_ASSISTED_HANDOFF = PASS__COMMITTED_REPOSITORY_STATE_PLUS_CERTIFIED_EVIDENCE_PLUS_FRESH_HUMAN_AUTHORIZATION_WERE_SUFFICIENT_WITHOUT_PRIOR_CONVERSATION`

`AIGOL_CODEX_WORK_SHARE = NOT_MEASURED`

Qualitatively: Human Authority supplied intent, vector selection, authorization, credit review, and commit boundary. Certified AiGOL infrastructure supplied EX/EW/EU/EI/DU/EB/EE/ER/EZ/FA evidence and semantics. Deterministic systems supplied hashes, candidate bytes, and DU rejection. Codex supplied targeted authentication, orchestration, classification, and the non-authoritative reduction proposal. Codex is cognition, not authority.

`OVERENGINEERING_RISK = ESTIMATED_LOW_TO_MODERATE__ZERO_COMMON_DUPLICATION__ONE_ADAPTER_AND_ONE_BUILDER__CANDIDATE_PLACED_VECTOR_METADATA_IN_A_FIXED_COMMON_FIELD_AND_WAS_CORRECTLY_REJECTED`

Supporting counts: `NEW_COMMON_COMPONENT_COUNT=0`; `NEW_COMMON_INFRASTRUCTURE_COUNT=0`; `DUPLICATE_COMMON_VALIDATOR_COUNT=0`; `PARALLEL_COMMON_PROOF_STACK_COUNT=0`; `DUPLICATE_PROOF_PATH_CREATED=NO`; `VECTOR_SPECIFIC_COMPONENT_COUNT=2`; unnecessary artifact count is `NOT_ESTABLISHED`.

`COGNITION_PROVENANCE = HUMAN_AUTHORIZATION__HUMAN_VECTOR_SELECTION__COMMITTED_CONSTITUTIONAL_EVIDENCE__CERTIFIED_EX_COMMON_SUBSTRATE__DETERMINISTIC_VALIDATOR_EVIDENCE__CODEX_DERIVED_REASONING__CROSS_ACCOUNT_REPOSITORY_HANDOFF`

`PREVIOUS_CODEX_CONVERSATION = NOT_CONSTITUTIONAL_AUTHORITY`

`CANDIDATE_CAPABILITY = NOT_ADMITTED__INTENDED_NARROW_CAPABILITY_P11_NEGATIVE_AUTHORITY_WRONG_ATTEMPT_DENIAL`

`SHADOW_DESIGN_TARGET = HUMAN_SELECTION -> COMMITTED_REPOSITORY_STATE -> CERTIFIED_EX_SUBSTRATE -> SMALL_WRONG_ATTEMPT_DELTA -> DU_EB_EE -> FRESH_B1_B2_B6 -> ONE_CANDIDATE -> ONE_VM -> ONE_BOOT -> ONE_VECTOR -> FAIL_CLOSED_REDUCTION -> HUMAN_REVIEW`

`CONSTITUTIONAL_CONTINUATION_PROGRESS = ET_TO_EU_TO_EV_TO_EW_TO_EX_TO_EY_TO_EZ_TO_FA_TO_FB_ZERO_MUTATION_BOUNDARY_TO_FC__FA_MOVED_5_OF_18_TO_6_OF_18__FB_CREATED_NO_COMMIT__HUMAN_SELECTED_WRONG_ATTEMPT__FC_STOPPED_AT_FIRST_CANDIDATE_DU_FAILURE`

`PROMPT_CONTEXT_REUSE_RATIO = STRUCTURAL_CONTEXT_REUSE_PROVEN__TOKEN_LEVEL_CONTEXT_REUSE_NOT_MEASURED__REPOSITORY_EVIDENCE_SUFFICIENT__EX_NOT_RECONSTRUCTED__FULL_HISTORY_NOT_RECONSTRUCTED__MATERIALIZATION_AND_EXECUTION_NOT_REPLAYED`

`TOKEN_BENCHMARK = NOT_MEASURED__CODEX_STATUS_INTERFACE_UNAVAILABLE`

`CODEX_SESSION_ID = NOT_MEASURED`; `CONTEXT_TOTAL = NOT_MEASURED`; start/end context use and remaining, five-hour quota, seven-day quota, and deltas are all `NOT_MEASURED`; `ELAPSED_TIME = NOT_MEASURED`.

`LLM_COST_REDUCTION_RATIO = NOT_EXACTLY_MEASURABLE`

`LCRR = NOT_EXACTLY_MEASURABLE`

Directional evidence: common reconstruction, full-history reconstruction, conversation reconstruction, materialization replay, execution replay, and retry were avoided. Candidate reconstruction was not avoided because one fresh candidate was constitutionally required. These facts do not establish a numerical cost ratio.

`REPETITIVE_PROOF_LOAD = LOW_FOR_PHASE_A__STOPPED_EARLY_AT_DU`

`COMMON_PROOF_REUSE_RATIO = STRUCTURAL__17_OF_17_APPLICABLE_CERTIFIED_COMPONENT_ROLES_REUSED__NOT_TOKEN_TIME_LABOR_OR_COST_RATIO`

`VECTOR_SPECIFIC_PROOF_RATIO = NOT_NUMERICALLY_MEASURED__TWO_VECTOR_SPECIFIC_SOURCE_COMPONENTS_AND_ONE_CANDIDATE`

`FRESH_OPERATIONAL_PROOF_RATIO = ZERO_OPERATIONAL_COMPONENTS_CAPTURED__NO_OPERATIONAL_EXECUTION`

`EXPECTED_FUTURE_E05_COMPLEXITY_REDUCTION = DIRECTIONALLY_SUPPORTED_FOR_AUTHENTICATION__NOT_ESTABLISHED_FOR_OPERATIONAL_COMPLETION`

`EX_AMORTIZATION_RESULT = PARTIAL__COMMON_REUSE_DOMINATED_PHASE_A__SMALL_VECTOR_DELTA_REACHED_DU__VECTOR_CANDIDATE_SCHEMA_INCOMPATIBILITY_STOPPED_EXECUTION`

`SPCE_REPOSITORY_RESUMABILITY = PASS`; `SPCE_SAME_SESSION_RESUMABILITY = PASS__FINALIZATION_ONLY`; `SPCE_CROSS_ACCOUNT_RESUMABILITY = PASS__REPOSITORY_MEDIATED`; `SPCE_OPERATIONAL_RESUMABILITY = NOT_EXERCISED`.

`CONVERSATION_HISTORY_REQUIRED = NO`; `FULL_HISTORY_RECONSTRUCTION_REQUIRED = NO`; `EXECUTION_REPLAY_REQUIRED = NO`; `MATERIALIZATION_REPLAY_REQUIRED = NO`.

`CROSS_LLM_CONTINUATION_USED = NO`; `CROSS_LLM_CONTINUATION_READINESS = NOT_ESTABLISHED`; `CLREC_EMPIRICAL_SUPPORT = REPOSITORY_CONTINUATION_ONLY`; `CLREC_CONSTITUTIONALLY_CERTIFIED = NO`.

Reuse Impact Assessment:

1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo? EX, EW, EU, EI, DU, and the committed EB/EE/ER/EZ/FA contracts and identities are reused as the certified or committed chain; the current execution reached EX/EW/EU authentication, EI production, and DU validation.
2. Katere nove zmogljivosti, če sploh, nastanejo? One generation-bound builder and one intended WRONG_ATTEMPT adapter were created. The candidate was not admitted, so no new operational or common capability is established.
3. Ali katera obstoječa zmogljivost postane nedosegljiva? No. `CAPABILITY_REACHABILITY_LOSS = NONE`.
4. Ali implementacija ustvarja vzporedni tok? No. `PARALLEL_FLOW_CREATED = NO`.
5. Ali zmanjšuje ali povečuje število produkcijskih poti? Neither. `PRODUCTION_PATH_DELTA = 0`.

`CERTIFIED_COMPONENT_REUSE_COUNT = 17`; `NEW_COMMON_COMPONENT_COUNT = 0`; `VECTOR_SPECIFIC_COMPONENT_COUNT = 2`; `FRESH_OPERATIONAL_COMPONENT_COUNT = 0`; `DUPLICATE_PROOF_PATH_CREATED = NO`.

# 4. Validation Matrix

| Requirement | Evidence | Result |
| --- | --- | --- |
| Exact FA HEAD/tree/subject | Git entry gate | PASS |
| Clean entry worktree and empty index | Git entry gate | PASS |
| Human WRONG_ATTEMPT selection | Current authorization | PASS |
| FA E05 6/18 credit | FA Phase D and final seal | PASS |
| WRONG_ATTEMPT unsatisfied/admissible | EM matrix plus FA frontier | PASS |
| EX authentication | EX validator 12/12 | PASS |
| EW reusable substrate | EW validator 17/17 | PASS |
| EU counter semantics | EU validator 18/18 | PASS |
| Zero common reconstruction | mutation and artifact classification | PASS |
| One fresh candidate maximum | builder output inventory | PASS__1 |
| Candidate/runtime byte identity | `cmp` and SHA-256 | PASS |
| DU candidate preflight | committed DU validator | FAIL_CLOSED__UNKNOWN_FIELD |
| EB | stopped after DU | NOT_RUN |
| EE | stopped after DU | NOT_RUN |
| WRONG_ATTEMPT isolation | candidate not admitted/executed | NOT_ESTABLISHED |
| Fresh B1 | no execution | NOT_RUN |
| Fresh B2 | no materialization | NOT_RUN |
| Fresh B6 | DU failed before EB/EE/operation | NOT_RUN |
| One materialization/VM/boot/QEMU maximum | all counters zero | PASS |
| Zero retry/repair/replacement | checkpoints and inventory | PASS |
| P12 and production prohibition | all counters zero | PASS |
| Candidate unchanged after failure | post-failure SHA-256 | PASS |
| Historical lineage immutability | tracked diff review | PASS |
| JSON unique keys and inner hashes | final validation | FINAL_PASS_REQUIRED |
| G48 exact six sections | top-level heading inventory | PASS |
| Git diff check | final validation | FINAL_PASS_REQUIRED |

# 5. Repository Mutation Summary

The authorized mutation scope is one untracked FC evidence namespace plus this G48 report. No committed file was edited in place. Nothing was staged, committed, or pushed.

```text
FILES_CREATED = 12
FILES_MODIFIED = 0
LINES_ADDED = 1411
LINES_REMOVED = 0
```

Operational counts:

```text
FRESH_OPERATIONAL_CANDIDATE_COUNT = 1
SECOND_CANDIDATE_COUNT = 0
REPLACEMENT_CANDIDATE_COUNT = 0
MATERIALIZATION_COUNT = 0
VM_CREATION_COUNT = 0
VM_BOOT_COUNT = 0
QEMU_EXECUTION_COUNT = 0
SECOND_VM_COUNT = 0
SECOND_BOOT_COUNT = 0
E05_CASE_EXECUTION_COUNT = 0
AUTOMATIC_RETRY_COUNT = 0
REPAIR_AND_CONTINUE_COUNT = 0
P11_REQUEST_COUNT = 0
PRE_ATTEMPT_DENIAL_COUNT = 0
P11_ENTRY_COUNT = 0
P11_INVOCATION_COUNT = 0
PROTECTED_EFFECT_COUNT = 0
P12_ENTRY_COUNT = 0
PRODUCTION_ROUTE_COUNT = 0
PRODUCTION_EFFECT_COUNT = 0
```

No QEMU process, overlay, seed, VM root, or execution root was created. Therefore teardown is `NOT_APPLICABLE__OPERATIONAL_STATE_NEVER_CREATED`, and unauthorized operational residue is zero.

# 6. Certification Verdict

`FINAL_VALIDATION = PASS__TRUTHFUL_FAIL_CLOSED_FINALIZATION__DU_REJECTED_SO_OPERATIONAL_COMMISSIONING_NOT_PERFORMED`

`SUBSTRATE_AUTHENTICATION = PASS__EX_CERTIFIED_COMMON_REPOSITORY_SUBSTRATE__NO_INVALIDATION_TRIGGER`

`VECTOR_FUNCTIONAL_RESULT = NOT_RUN`

`WRONG_ATTEMPT_ISOLATION_RESULT = NOT_ESTABLISHED__CANDIDATE_NOT_ADMITTED_OR_EXECUTED`

`B1_RESULT = NOT_RUN`; `B2_RESULT = NOT_RUN`; `B6_REPOSITORY_PRECONDITION = NOT_ESTABLISHED`; `B6_OPERATIONAL_STATE = NOT_RUN`.

`CONSTITUTIONAL_CREDIT_RESULT = NOT_AWARDED`; `E05_BEFORE = 6/18`; `E05_AFTER = 6/18`; `E05_REMAINING = 12`; `WRONG_ATTEMPT_STATE_AFTER = UNSATISFIED`.

`FIRST_AUTHORITATIVE_FAILURE = DU_UNKNOWN_FIELD_IN_SELECTED_CASE`

`FAILURE_STAGE = PHASE_B_FIRST_CANDIDATE_DU_STRUCTURAL_SCHEMA_VALIDATION`

`FAILURE_CLASS = VECTOR_SPECIFIC_CANDIDATE_SCHEMA_INCOMPATIBILITY`

`EXACT_NEXT_CONSTITUTIONAL_FRONTIER = HUMAN_REVIEW_OF_FC_FAIL_CLOSED_EVIDENCE__THEN_SEPARATE_HUMAN_AUTHORIZATION_FOR_A_FRESH_GENERATION_THAT_PRESERVES_THE_FIXED_DU_SELECTED_CASE_SHAPE_AND_BINDS_WRONG_ATTEMPT_DETAILS_IN_EXISTING_EXTENSION_OR_OBSERVATION_ROLES__E05_REMAINS_6_OF_18__NO_P12_OR_PRODUCTION`

`RECOMMENDED_NEXT_GENERATION = G77_256FD_ONE_BOUNDED_REPOSITORY_ONLY_WRONG_ATTEMPT_CANDIDATE_SCHEMA_ALIGNMENT_AND_PREFLIGHT__NO_OPERATIONAL_EXECUTION_WITHOUT_SEPARATE_AUTHORIZATION`

`AUTO_CONTINUABLE = NO`
