# 1. Implementation Summary

Generation: `G77-256KZ`

Identity: `G77_256KZ_EXPIRED_ADAPTER_COMPLETE_CONTEXT_BINDING_V1`

Mode: `REPOSITORY_ONLY__NO_AUTHORITY__NO_OPERATION`

KZ preserves the already-authenticated complete sealed operation-context digest through the existing EXPIRED act-construction specialization. The existing JR specialization now adds `authorized_context_sha256` to canonical Human act metadata from exactly `gate.operation_context_sha256`. It does not compute, accept, or substitute another digest.

Proof separation:

- `REPOSITORY PROOF = VERIFIED`
- `REUSED HUMAN-AUTHORITY STRUCTURE = VERIFIED__NO_NEW_AUTHORITY`
- `ADAPTER/OWNER CONFORMANCE PROOF = VERIFIED`
- `UNCHANGED P11 GUARD PROOF = VERIFIED`
- `OPERATIONAL PROOF = NOT_PERFORMED`
- `E05 ACCEPTANCE PROOF = NOT_CREATED`

Failure classification remains `HARNESS_OR_TEST_ARTIFACT`. Novelty remains `VERIFIED__NEWLY_OBSERVED_EXPIRED_ADAPTER_BINDING_OMISSION__NOT_A_NEW_CONSTITUTIONAL_FAILURE_CLASS`. The affected invariant is `EVERY_OPERATIONAL_HUMAN_ACT_MUST_BIND_THE_COMPLETE_SEALED_OPERATION_CONTEXT`. No new capability is required; KZ supplies the missing repository conformance proof.

# 2. Code Evidence

## Authenticated ownership trace

- `SOURCE_OWNER = EXISTING_FM_SEALED_HANDOFF_AND_CONTEXT_OWNER`
- `SOURCE_FIELD = authorized_context_sha256`
- `FIRST_COMPONENT_WITH_FIELD = FM_CANONICAL_HUMAN_AUTHORIZATION_HANDOFF`
- `LAST_COMPONENT_WITH_FIELD = P11_COMMISSIONING_GATE_OPERATION_CONTEXT_SHA256`
- `FIRST_COMPONENT_WITHOUT_FIELD = FC_DERIVED_CANONICAL_HUMAN_ACT_METADATA__PRE_KZ`
- `LOSS_TRANSFORMATION = FC_CREATE_INPUT_AND_AUTHORITY_REPLACES_ORIGINAL_ACT_METADATA`
- `ACT_CONSTRUCTION_OWNER = .github/governance/evidence/g77_256fc_wrong_attempt_operational_v1/harness/G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py`
- `SPECIALIZATION_OWNER = .github/governance/evidence/g77_256jr_expired_human_authority_materialization_and_presentation_binding_v1/adapter/G77_256JR_EXPIRED_VECTOR_ADAPTER_V1.py`
- `SHARED_OR_VECTOR_SPECIFIC = SHARED_TEMPLATE_LOSS__EXPIRED_SPECIFIC_REQUIRED_DELTA`
- `EXISTING_SCHEMA_SUPPORT = VERIFIED__CANONICAL_METADATA_AND_P11_EQUALITY_GUARD`
- `EXISTING_CONTEXT_BINDING_PRECEDENT = VERIFIED__FM_HANDOFF_AND_JM_P11_COMPLETE_CONTEXT_BINDING`
- `MINIMUM_REPAIR_OWNER = EXISTING_JR_EXPIRED_SPECIALIZATION_AND_EXISTING_FM_EXPIRED_ADMISSION_HASH_BINDING`

The source chain is one-to-one:

`FM handoff authorized_context_sha256` → authenticated sealed context `context_sha256` → FC/ER commissioning gate `operation_context_sha256` → JR-specialized canonical act metadata `authorized_context_sha256` → unchanged P11 exact-equality guard.

The specialized AST contains exactly one binding value expression, `gate.operation_context_sha256`. No downstream hash calculation, caller field, provider field, alternate owner, or substitute digest is introduced.

## Failure novelty and convergence

- `FAILURE_CLASS = HARNESS_OR_TEST_ARTIFACT`
- `PREVIOUS_CLOSEST_EDGE = JM_COMPLETE_SEALED_CONTEXT_BINDING_GUARD_AND_JH_CONTEXT_BOUND_OPERATIONAL_PRECEDENT`
- `SEMANTIC_DIFFERENCE = HOST_HANDOFF_BINDS_CONTEXT_BUT_LEGACY_FC_DERIVED_GUEST_ADAPTER_RECREATES_ACT_WITHOUT_AUTHORIZED_CONTEXT_SHA256`
- `PRODUCTION_BEHAVIOR_IMPACT = VERIFIED__NONE__P11_FAILED_CLOSED_BEFORE_SUBMIT_ENTRY_INVOCATION_OR_EFFECT`
- `NEW_CAPABILITY_REQUIRED = VERIFIED__NO__EXISTING_CONTEXT_BINDING_MECHANISM_ALREADY_EXISTS`
- `NEW_PROOF_REQUIRED = KZ_ADAPTER_PROPAGATION_CONFORMANCE_PLUS_LATER_DISTINCT_FRESH_OPERATIONAL_PROOF`
- `CONVERGENCE_SIGNAL = VERIFIED__STATIC_BINDING_EDGE_CLOSED_WITHOUT_REPEATING_OPERATION`
- `REPETITION_PRESSURE = VERIFIED__REDUCED_BY_STATIC_EDGE_CLOSURE`
- `VERIFICATION_AMPLIFICATION_RISK = ESTIMATED__LOW_AFTER_FOCUSED_END_TO_END_REPOSITORY_PROOF`
- `CLASSIFICATION_CONFIDENCE = VERIFIED__HIGH`

## Cross-vector reuse assessment

`CROSS_VECTOR_REUSE_SCOPE = FC_DERIVED_ACT_CONSTRUCTION_TEMPLATE`. EXPIRED, FUTURE, WRONG_ATTEMPT, WRONG_CONTRACT, WRONG_INPUT, and WRONG_PROVENANCE reuse the FC-derived template. That establishes a shared owner relationship, but not a shared required KZ delta. The other five vector owners and the FC source remain byte-unchanged because changing the hash-bound shared template would broaden KZ and invalidate unrelated bindings. Vector-specific residue remains a distinct fresh EXPIRED operational proof.

`COMMON_PROOF_REUSE != VECTOR_OPERATIONAL_PROOF`

`COMMON_E05_INFRASTRUCTURE != VECTOR_E05_CREDIT`

`MULTI_VECTOR_REUSE != AUTHORITY_TRANSFER`

## Reuse Impact Assessment

1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?

   EX 17/17, FM sealed handoff/context ownership, FC/ER act construction, JM complete-context binding, the JR family-local EXPIRED specialization, canonical Human act metadata, and the P11 equality guard are reused.

2. Katere nove zmogljivosti (če sploh) nastanejo?

   No new constitutional or production capability arises. One existing EXPIRED specialization is brought into conformance with an already-required invariant.

3. Ali katera obstoječa zmogljivost postane nedosegljiva?

   No. FC and all non-EXPIRED vector owners remain byte-unchanged and reachable under their existing bindings.

4. Ali implementacija ustvarja vzporedni tok?

   No. The sole FM → ER → P11 route remains one-to-one.

5. Ali zmanjšuje ali povečuje število produkcijskih poti?

   Neither. The production path count remains one.

# 3. Constitutional Self-Assessment

## Repository conformance proof

The focused proof authenticates all required conditions:

- the complete-context digest exists upstream;
- the act path receives the exact gate digest;
- canonical Human act metadata contains `authorized_context_sha256` identically;
- no independent substitute digest exists;
- missing, wrong, different-context, stale-context, and malformed values fail closed at the unchanged P11 guard;
- the correct value passes the unchanged complete-context guard; validation then reaches and fail-closes at the next pre-existing FC input `authorization_reference` edge;
- `non_reusable`, `non_transferable`, and EXPIRED vector identity remain preserved;
- no new authority path or alternate production route exists.

`P11_MUTATION = 0`

`PRODUCTION_MUTATION = 2`

`NEW_OWNER = 0`

`NEW_ROUTE = 0`

`NEW_REGISTRY = 0`

`NEW_GENERIC_ABSTRACTION = 0`

`NEW_CONSTITUTIONAL_CONCEPT = 0`

`PARALLEL_FLOW = NO`

`PRODUCTION_ROUTE = 1_TO_1`

## Authority and operational firewall

KZ creates no Human authorization and consumes no authority. It invokes no launcher, QEMU, VM, operational request, P11 entry, protected invocation, or protected effect.

- `QEMU_START_COUNT = 0`
- `VM_START_COUNT = 0`
- `OPERATION_ATTEMPT_COUNT = 0`
- `AUTHORITY_CONSUMPTION_COUNT = 0`
- `E05_STATE = VERIFIED__11_OF_18`
- `E05_FRONTIER = VERIFIED__7_UNSATISFIED_OF_18`
- `KZ_E05_CREDIT = VERIFIED__0`
- `EXPIRED_STATUS = NOT_PROVEN_OPERATIONALLY`

`HAC_HAI_HAE = NOT_PROVEN__AUTHENTICATED_DEFINITIONS_NOT_LOCATED`

# 4. Validation Matrix

Repository-only validation covers:

- focused KZ construction, exact propagation, five negative bindings, correct binding, AST ownership, sealed reduction, and report structure;
- the existing JR EXPIRED specialization suite;
- JM context-binding precedent tests;
- P11 non-operational regression tests;
- governance conformance tests and deterministic conformance engine;
- canonical JSON, inner reduction seal, Python compilation, G48 structure, bounded mutation audit, and `git diff --check`.

No operational infrastructure is part of validation. Validation results are recorded in the terminal reduction and authenticated commit checkpoint; repository proof does not create EXPIRED operational acceptance.

Results:

- focused KZ: `12 passed`;
- JM complete-context precedent plus P11 consumer regression: `29 passed`, with one expected historical state-bound JM assertion that requires P11 to be dirty during the original JM generation; functional context/P11 failures: `0`;
- governance conformance tests: `9 passed`;
- deterministic conformance engine: `20/20`, `CONFORMANT`, zero warnings, zero violations;
- `git diff --check`: pass.

The historical JM state-bound assertion is retained as a visible limitation; KZ does not rewrite JM evidence or make P11 dirty to satisfy a past-generation worktree expectation.

## Proof yield

- `EX_REUSED = VERIFIED__17_OF_17`
- `EX_RECONSTRUCTED = VERIFIED__0`
- one static binding edge closed;
- zero operational observations created;
- zero E05 credit created.

# 5. Repository Mutation Summary

The live existing-owner mutations are the JR EXPIRED specialization and FM's existing EXPIRED admission digest pin. JR inserts the exact gate-owned context digest into transformed act metadata and adds a fail-closed specialization anchor; FM binds admission to those repaired JR bytes. KZ adds only its formalizer, focused tests, canonical sealed reduction, and this report. FC, P11, KY, and all non-EXPIRED vector sources are unchanged.

## Frontier movement

- `PRE_KZ_LAST_VERIFIED_EDGE = P11_CUSTODY_FAIL_CLOSED_ON_MISSING_COMPLETE_CONTEXT_BINDING`
- `POST_KZ_LAST_VERIFIED_EDGE = EXPIRED_ACT_REPOSITORY_CONFORMANCE_TO_COMPLETE_CONTEXT_BINDING`
- `PRE_KZ_FIRST_BROKEN_EDGE = EXPIRED_ADAPTER_OMITS_AUTHORIZED_CONTEXT_SHA256`
- `POST_KZ_FIRST_BROKEN_EDGE = FC_DERIVED_INPUT_AUTHORIZATION_REFERENCE_REMAINS_BOUND_TO_ER_ACT_IDENTITY_AFTER_FC_ACT_IDENTITY_REPLACEMENT`
- `FIRST_UNVERIFIED_OPERATIONAL_EDGE = CONTEXT_BOUND_ACT_WITH_ALIGNED_INPUT_AUTHORIZATION_REFERENCE_THEN_EXPIRED_DENIAL_BEFORE_P11_ENTRY`
- `CONSTITUTIONAL_FRONTIER_MOVEMENT = VERIFIED__REPOSITORY_BINDING_EDGE_CLOSED__OPERATIONAL_EDGE_UNCHANGED`
- `E05_FRONTIER_MOVEMENT = VERIFIED__NONE__11_OF_18_REMAINS`

## Compact CCWIM

- `AUTHENTICATED_REPOSITORY_CONTINUATION = VERIFIED__YES`
- `SAME_SESSION_CONTINUATION = VERIFIED__YES`
- `PREVIOUS_SESSION_CONTEXT_REUSED = VERIFIED__YES`
- `REPOSITORY_EVIDENCE_PRIMARY = VERIFIED__YES`
- `HANDOFF_AMBIGUITY_COUNT = 0`
- `BINDING_OWNER_AMBIGUITY_COUNT = 0`
- `AUTHORITY_STATE_AMBIGUITY_COUNT = 0`
- `OPERATIONAL_ATTEMPT_AMBIGUITY_COUNT = 0`

Periodic metrics are not fabricated: AIGOL/Codex work share, prompt-context reuse ratio, token benchmark, and LCRR are `NOT_MEASURED` because no governed attribution, token, cost, or denominator instrument exists. Full CCWIM is `NOT_APPLICABLE__COMPACT_CCWIM_SUFFICIENT`.

# 6. Certification Verdict

`PROJECT_STATE = VERIFIED__KZ_REPOSITORY_ONLY_TERMINAL`

`INFORMAL_PROJECT_PROGRESS_ESTIMATE = ESTIMATED__EXPIRED_STATIC_BINDING_READY__OPERATIONAL_PROOF_OPEN`

`CONSTITUTIONAL_HEALTH_EVIDENCE = VERIFIED__UNCHANGED_FAIL_CLOSED_P11__ZERO_AUTHORITY_AND_OPERATION`

`SHADOW_AUTOMATION_STATUS = VERIFIED__ABSENT`

`CONSTITUTIONAL_FRONTIER_DISTANCE = NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR`

`GOVERNANCE_EFFICIENCE = ESTIMATED__HIGH__ONE_EXISTING_OWNER_DELTA_AVOIDS_REPEATED_OPERATION`

`OVERENGINEERING_RISK = ESTIMATED__LOW__NO_GENERIC_OR_SHARED_BASE_CHANGE`

`COGNITION_PROVENANCE = VERIFIED__CURRENT_SESSION_AND_AUTHENTICATED_REPOSITORY_EVIDENCE_PRIMARY`

`COGNITION_ASSISTED_HANDOFF = VERIFIED__SAME_SESSION_CHECKPOINT_REUSED_WITH_TARGETED_REAUTHENTICATION`

`CANDIDATE_CAPABILITY = VERIFIED__REPOSITORY_CONFORMANT_EXPIRED_CONTEXT_BOUND_ACT_CONSTRUCTION`

`SHADOW_DESIGN_TARGET = VERIFIED__SOLE_FM_ER_P11_ROUTE`

`CONSTITUTIONAL_CONTINUATION_PROGRESS = VERIFIED__KY_FAILURE_LOCALIZATION_TO_KZ_STATIC_REPAIR`

`MINIMUM_MISSING_CAPABILITY = BOUNDED_EXISTING_FC_DERIVED_INPUT_AUTHORIZATION_REFERENCE_ALIGNMENT`

`MINIMUM_MISSING_PROOF = REPOSITORY_PROOF_OF_FC_DERIVED_INPUT_AUTHORIZATION_REFERENCE_ALIGNMENT__THEN_DISTINCT_FRESH_OPERATIONAL_OBSERVATION`

`MINIMUM_LEGAL_NEXT_DELTA = AFTER_HUMAN_REVIEW__SEPARATE_REPOSITORY_ONLY_FC_DERIVED_INPUT_AUTHORIZATION_REFERENCE_ALIGNMENT__NO_KZ_OPERATION`

KZ is terminal and not auto-continuable. The next repository-only repair generation, any later operational generation, any fresh Human authority, and any EXPIRED operation are outside KZ and were not started.

A__KZ_EXPIRED_ADAPTER_COMPLETE_CONTEXT_BINDING_REPOSITORY_CONFORMANCE_VERIFIED__NO_OPERATION__NO_E05_CREDIT
