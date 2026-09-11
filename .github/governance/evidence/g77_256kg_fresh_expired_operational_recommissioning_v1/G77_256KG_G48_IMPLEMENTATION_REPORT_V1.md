# 1. Implementation Summary

Generation: `G77_256KG_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1`

Operation: `G77_256KG_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001`

Report identity: `G77_256KG_G48_IMPLEMENTATION_REPORT_V1`

Reporting date: `2026-09-10`

Terminal: `M__KG_PHASE_B_HUMAN_SOURCE_TO_CANONICAL_HANDOFF_DIGEST_MISMATCH_BEFORE_AUTHORITY_CONSUMPTION`

Mode: `PHASE_B_PRECONSUMPTION_FAIL_CLOSED__NO_AUTHORITY_CONSUMPTION__NO_OPERATION`.

Phase B authenticated the exact Human-supplied act and reached the unconsumed JZ binding gate. It then stopped before authority consumption because the commission requires the digest derived from exact Human-source bytes to equal the canonical handoff, sealed invocation, and final FM argv authority digests. The Human-source SHA-256 is `d11850611c8c1273dbd1484af40d1d38533f95d8f0665da418885947b32a9484`; the other three values are `1e6c6fec12e064dffa2bd69873664e5a236dde812eb47853c1b7f1c056e8020c`. No operational route was invoked.

KG Phase A was reconstructed from the exact committed KF checkpoint after a provider-limit interruption. The entry is HEAD `3bcc78deaeb6821dd71ecdbc9de18628d3ff07de`, tree `eb06ab5d18fc99d648b7ba20d40269ccf3d0de40`, subject `G77-256KF verify guest harness permission binding repair`, branch `g77-256fl-wrong-attempt-preboot-blocker`, origin `git@github.com:Aljosa3/sapianta-ecosystem.git`, and equal remote branch tip. The initial worktree was clean and the index empty. No previous KG artifact delta existed.

Nested authority is clean, detached, and pinned at HEAD `3183bab71f8f30397c0309dd2e6d846d14a11f66`, tree `7c32ec05efc2be43297849bc38ec8766514a523d`, origin `git@github.com:Aljosa3/sapianta-core.git`, and immutable tag `sapianta-system-nested-authority-3183bab-v1`; the remote tag equals the local nested HEAD.

The materializer reuses the authenticated KE commissioning convention, explicitly rebinds its three inherited pre-KF launcher expectations to committed KF launcher SHA-256 `e1db7e6d59d81a85ee025b27c3145abe697c1097822694498a4ad686d2406c51`, authenticates KD/KB/JZ/JX/JR/GN/FM/ER/P11 and EX 17/17, and adds one KF permission preflight before the Human-decision presentation. No production or P11 implementation file changed.

Fresh KG coordinates:

| Coordinate | Value |
|---|---|
| `CANDIDATE_SHA256` | `8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a` |
| `CONTEXT` | `72b9480fa22513f01cfd8d935efbfe44bed15c246f9d54ee5c0b3c78ed53c0bd` |
| `CONTEXT_FILE_SHA256` | `8010391eae9d00175159549d9c1079ebf8a9cbb78213f089dc0120f34bed017b` |
| `CANONICAL_ARGV_SHA256` | `0bf7f3fda2af5dffab173baccee2dd683b737d871d69e9858d0bfa55cae8f786` |
| `TEMPORAL_BINDING` | `52ecdbbb6c1b89a16f9b93d602686c231d67788331031c177643c4a35f6a866b` |
| `REQUEST_IDENTITY` | `339986a25c10c17eac02527372563f132eebb501c440ea5e49f14af17ab9dad0` |
| `REQUEST_FILE_SHA256` | `03d46552fd2e7478c536b32abfd373185fc7b9af7ab27d9d064ba90d5fb8c56b` |
| `PRESENTATION_SHA256` | `ce52477b12c222182d6be5879e35728292a76022a36fbbedde0d9805d5e875ae` |
| `READINESS_CHECKPOINT` | `de2036904c44cd5452df4e2d2aef3ffa49264f6b127392ba7cf8bd9aa129c22e` |
| `SAFE_STOP_CHECKPOINT` | `49484c90bcf86c3d57e665fffea463d89ff36c27251abee74d21db21e364f292` |

The canonical candidate payload remains byte-identical to KC and KE by design; its fresh KG-local candidate/runtime projections, context, temporal binding, argv, request, presentation, readiness, and safe-stop identities are distinct. This preserves the authenticated commissioning convention and does not misclassify the reused canonical payload as a new semantic candidate.

# 2. Code Evidence

The repository-only owner is `orchestration/G77_256KG_PREAUTHORIZATION_MATERIALIZER_V1.py`. It authenticates the committed KE materializer bytes before adapting only the generation namespace and exact KF entry coordinates. The inherited launcher identity is changed only in the three known proof maps, and all three must initially equal the authenticated pre-KF digest. The inert `G77_256KG_POSTHUMAN_INVOCATION_BINDER_V1.py` accepts only the context, candidate, and future authority paths; it accepts no digest parameter and delegates derivation and validation to the sole FM/JZ owner without starting a process.

The KF preflight authenticates canonical bytes and the inner seal of `G77_256KF_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json`, requires terminal `A__GUEST_HARNESS_PERMISSION_BINDING_REPOSITORY_VERIFIED`, and verifies:

- authoritative owner `G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py:materialize_operation_state`;
- private construction mode `0700` and final presentation mode `0701`;
- exact one-bit other-search delta;
- committed context-owner source mode `0644` and custody effective projected permissions `0004`;
- no source execute requirement;
- read-only guest projection;
- zero new owner and route; and
- unchanged P11 with production route `1 -> 1`.

The projected context owner is observed as `0664` under the existing repository umask, as are committed KC and KE materializations in this checkout. This adds group write for the host group only; custody UID/GID `3/3` still receives exactly other-read and no write/execute permission. The governed source Git mode remains `100644`. This observed umask variance is explicit and is not promoted to operational guest success.

JZ Phase-A evidence remains structural: `HUMAN_SOURCE_SHA256` and authenticated Human authority digest are not applicable because no Human act exists. The reused post-Human contract derives the digest from exact Human-source bytes, requires HEX64, carries the same digest through canonical handoff, sealed invocation, and final FM argv, checks three-way equality before consumption, and rejects caller-supplied substitution.

Deterministic EXPIRED semantics are unchanged: `valid_from = 100`, `valid_until = 1000`, governed preclaim `1000`, truth table `999 = CURRENT`, `1000 = EXPIRED`, `1001 = EXPIRED`, and denial reason `one-use Human act expired before PRECLAIM`. Wall clock is not governed EXPIRED truth.

The exact KE terminal `M__KE_AUTHORIZED_EXPIRED_OPERATION_FAILED_AT_GUEST_CUSTODY_IMPORT_BEFORE_OPERATION_REQUEST` is reused as immutable history. KE authority remains consumed exactly once, nonreusable, nontransferable, and unavailable for KG. Historical KE counters are one authorization, one consumption, one PRE operational invocation, one FM invocation, one QEMU/VM attempt, and one operation attempt; request, EXPIRED denial, P11 entry, protected invocation/effect, retry, repair-retry, and replay are zero.

The exact KG Human-source bytes were preserved in `G77_256KG_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt` and semantically matched every sealed Phase-A coordinate and limit. The derived source digest is HEX64 and authority reached `AUTHENTICATED__UNCONSUMED`. The canonical handoff and sealed invocation were then materialized through the existing JZ/FM path. Their internal handoff/invocation/argv equality is verified, and all 13 substitution negatives were rejected. The stronger equality required by the Phase-B commission failed because the canonical handoff is a JSON envelope whose file digest differs from the digest of the Human-source text it binds. This discrepancy was not repaired or reinterpreted.

# 3. Constitutional Self-Assessment

Verified governance reporting:

- `PROJECT_PROGRESS = VERIFIED__KG_PHASE_B_EXACT_HUMAN_AUTHORITY_AUTHENTICATED_AND_PRECONSUMPTION_DIGEST_MISMATCH_LOCALIZED`.
- `PROJECT_PROGRESS_ESTIMATE = NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR`.
- `INFORMAL_PROJECT_PROGRESS_ESTIMATE = ESTIMATED__PHASE_B_STOPPED_BEFORE_CONSUMPTION_AT_EXACT_SOURCE_TO_HANDOFF_DIGEST_BOUNDARY`.
- `CONSTITUTIONAL_HEALTH_EVIDENCE = VERIFIED__ONE_AUTHENTICATED_UNCONSUMED_AUTHORITY_ZERO_CONSUMPTION_ZERO_OPERATION_ZERO_RETRY`.
- `SHADOW_AUTOMATION_STATUS = VERIFIED__ABSENT`.
- `CONSTITUTIONAL_FRONTIER_DISTANCE = NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR`.
- `E05_STATE = VERIFIED__11_OF_18`; `E05_FRONTIER = VERIFIED__7_UNSATISFIED_OF_18`; `E05_CREDIT = VERIFIED__0`; `EXPIRED = NOT_PROVEN_OPERATIONALLY`.
- `GOVERNANCE_EFFICIENCE = ESTIMATED__HIGH__MISMATCH_CAUGHT_BEFORE_IRREVERSIBLE_CONSUMPTION`.
- `OVERENGINEERING_RISK = ESTIMATED__LOW__EVIDENCE_ONLY_FAIL_CLOSED_REDUCTION`.
- `COGNITION_PROVENANCE = VERIFIED__EXACT_HUMAN_SOURCE_CANONICAL_HANDOFF_AND_SEALED_INVOCATION_BYTES_PRIMARY`.
- `COGNITION_ASSISTED_HANDOFF = VERIFIED__DURABLE_REPOSITORY_PHASE_A_AND_EXACT_HUMAN_ACT`.
- `CANDIDATE_CAPABILITY = NOT_PROVEN__FRESH_EXPIRED_OPERATIONAL_DENIAL`.
- `SHADOW_DESIGN_TARGET = VERIFIED__SOLE_FM_ER_P11_ROUTE_WITH_KF_PERMISSION_BINDING_AND_STABLE_JR_EXPIRED_CHECKOUT`.
- `CONSTITUTIONAL_CONTINUATION_PROGRESS = VERIFIED__PHASE_A_TO_AUTHENTICATED_UNCONSUMED_PHASE_B_FAIL_CLOSED_GATE`.
- `LAST_VERIFIED_EDGE = EXACT_HUMAN_ACT_AUTHENTICATED_AND_CANONICAL_HANDOFF_INVOCATION_ARGV_INTERNAL_EQUALITY_VERIFIED`.
- `FIRST_BROKEN_EDGE = DERIVED_HUMAN_SOURCE_SHA256_DOES_NOT_EQUAL_CANONICAL_HANDOFF_AUTHORITY_DIGEST`.
- `MINIMUM_MISSING_CAPABILITY = ONE_AUTHENTICATED_DIGEST_CONTRACT_RECONCILING_EXACT_HUMAN_SOURCE_AUTHORITY_WITH_CANONICAL_HANDOFF_BINDING`.
- `MINIMUM_LEGAL_NEXT_DELTA = AFTER_HUMAN_REVIEW__SEPARATE_REPOSITORY_ONLY_JZ_DIGEST_SEMANTICS_ASSESSMENT__NO_KG_CONSUMPTION_OR_OPERATION`.
- `EX_REUSED = VERIFIED__17_OF_17`; `EX_RECONSTRUCTED = VERIFIED__0`.
- `HAC_HAI_HAE = NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED`.

Compact CCWIM: `CCWIM_MATURITY_LEVEL = ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION`; `AUTHENTICATED_REPOSITORY_CONTINUATION = VERIFIED__YES`; `PREVIOUS_WORKER_CONVERSATION_REQUIRED = VERIFIED__NO`; `PREVIOUS_WORKER_MEMORY_REQUIRED = VERIFIED__NO`; `HANDOFF_RECONSTRUCTION_SUCCESS = VERIFIED__YES`; `HANDOFF_AMBIGUITY_COUNT = VERIFIED__0`; `OBSERVED_ARTIFACT_LEVEL_CROSS_WORKER_DRIFT = VERIFIED__0`; `CROSS_ACCOUNT_RECOVERY = VERIFIED`; `PROVIDER_INTERRUPTION_RECOVERY = VERIFIED`.

Reuse Impact Assessment:

1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?

   `VERIFIED`: EX 17/17 plus JR, JX, JZ, KB, KD, KE, KF, GN, FM, ER, P11, the sole production route, stable checkout, and pinned nested authority.

2. Katere nove zmogljivosti (če sploh) nastanejo?

   `VERIFIED__0_OPERATIONAL_CAPABILITY`; one preconsumption digest-semantics blocker is newly localized.

3. Ali katera obstoječa zmogljivost postane nedosegljiva?

   `VERIFIED__NO`.

4. Ali implementacija ustvarja vzporedni tok?

   `VERIFIED__NO`.

5. Ali zmanjšuje ali povečuje število produkcijskih poti?

   `VERIFIED__NEITHER`; production paths remain `1 -> 1`.

# 4. Validation Matrix

| Requirement | Evidence / method | Result |
|---|---|---|
| Exact KF entry and remote equality | direct Git object queries and `git ls-remote` | PASS |
| Clean initial entry and empty index | status, tracked, untracked, and staged inventory | PASS |
| Nested authority | local detached/pinned state and direct remote tag lookup | PASS |
| KF terminal and permission contract | canonical sealed KF reduction plus committed launcher source | PASS |
| KE terminal lifecycle | committed terminal reduction and Phase-B evidence | PASS |
| EX common proof applicability | certificate/seal authentication and KF invalidation count | PASS, 17/17 reused, 0 reconstructed |
| JR deterministic EXPIRED contract | repository formalization through reused owner | PASS |
| JX roles, JZ digest readiness, KB namespace, KD interface | preflight artifacts and focused regressions | PASS; 118 passed, 17 historical lifecycle-bound cases deselected |
| GN/FM/ER/P11 and sole route | materializer/static readiness and identity bindings | PASS |
| Fresh identity/collision firewall | KC/KE comparison | PASS for generation-local identities; canonical payload intentionally reused |
| Request/presentation/readiness/safe-stop consistency | exact hashes, seals, and Human-decision projection | PASS |
| Exact Human-source authentication | byte identity and semantic comparison to all sealed coordinates | PASS; `d1185061...9484` |
| JZ internal handoff/invocation/argv equality | canonical handoff and sealed invocation | PASS; all equal `1e6c6fec...020c` |
| Commission-required Human-source equality | source digest compared to JZ authority digest | FAIL CLOSED before consumption |
| Authority and operation barrier | absence of consumption/invocation/result artifacts | PASS; consumption and attempt remain zero |
| Phase-A operational firewall | all KG counters | PASS, all zero |
| Provider-recovery delta firewall | all recovery counters | PASS, all zero |
| Canonical JSON and seals | dedicated KG test | PASS |
| AST/compile | in-memory compilation and test AST inspection | PASS |
| G48 exactly six H1 and RIA exactly five questions | structural test | PASS |
| Dedicated KG Phase-A and fail-closed Phase-B suites | KG tests | PASS, 15 passed |
| Governance conformance | governance suite and conformance engine | PASS, 9 tests; 20/20 checks, CONFORMANT |
| Canonical JSON and seals after Phase B | all KG JSON envelopes | PASS, 21 canonical files and 19 inner seals |
| AST and in-memory compilation | every KG Python artifact | PASS, 9 files |
| Whitespace and empty index | `git diff --check` and cached diff | PASS |

No QEMU system process was started, no VM was booted, and neither PRE nor FM was invoked operationally. Repository-only materialization used the existing authority-free preauthorization owner; it did not authenticate or consume Human authority.

# 5. Repository Mutation Summary

All mutations are under `.github/governance/evidence/g77_256kg_fresh_expired_operational_recommissioning_v1/`. Phase B adds the exact Human-source file, a same-generation controller adapter, canonical Human handoff, sealed invocation, preconsumption checkpoint, an evidence-only failure reducer, and the canonical fail-closed reduction. No consumption, FM invocation, QEMU receipt, VM/serial, request, denial, P11 entry, or protected-effect artifact exists.

Architectural delta budget: `PRODUCTION_MUTATION_COUNT = 0`; `P11_IMPLEMENTATION_MUTATION_COUNT = 0`; `NEW_OWNER_COUNT = 0`; `NEW_ROUTE_COUNT = 0`; `NEW_REGISTRY_COUNT = 0`; `NEW_GENERIC_ABSTRACTION_COUNT = 0`; `NEW_CONSTITUTIONAL_CONCEPT_COUNT = 0`; `PRODUCTION_ROUTE_BEFORE = 1`; `PRODUCTION_ROUTE_AFTER = 1`. KF’s historical one existing-owner production mutation is not counted as KG mutation.

Proof yield: `NEW_VERIFIED_CAPABILITY_COUNT = VERIFIED__0_OPERATIONAL_EXPIRED_CAPABILITY`; `NEW_BLOCKER_LOCALIZED_COUNT = VERIFIED__1_PRECONSUMPTION_DIGEST_SEMANTICS_BLOCKER`; `E05_CREDIT = VERIFIED__0`; `PROOF_REUSE_COUNT = VERIFIED__17`.

No files were staged, committed, or pushed. The index remains empty.

# 6. Certification Verdict

`M__KG_PHASE_B_HUMAN_SOURCE_TO_CANONICAL_HANDOFF_DIGEST_MISMATCH_BEFORE_AUTHORITY_CONSUMPTION`

The exact Human authority is authenticated and remains unconsumed. The commission-required source-to-handoff digest equality is not proven, so the authority consumption barrier remains closed and no operation occurred. `OPERATIONAL_AUTHORIZATION_COUNT = 1`; `AUTHORITY_CONSUMPTION_COUNT = 0`; `PRE_OPERATIONAL_COUNT = 0`; `FM_OPERATIONAL_INVOCATION_COUNT = 0`; `QEMU_COUNT = 0`; `VM_COUNT = 0`; `OPERATION_ATTEMPT_COUNT = 0`; `OPERATIONAL_REQUEST_COUNT = 0`; `EXPIRED_DENIAL_COUNT = 0`; `P11_ENTRY_COUNT = 0`; `PROTECTED_INVOCATION_COUNT = 0`; `PROTECTED_EFFECT_COUNT = 0`; `RETRY_COUNT = 0`; `REPAIR_RETRY_COUNT = 0`; `REPLAY_COUNT = 0`.

`AUTO_CONTINUABLE = NO`. `HUMAN_REVIEW_REQUIRED = YES`. Do not consume, retry, repair-retry, replay, operate KG, transfer KG authority, or start KH. A separate repository-only JZ digest-semantics assessment requires Human review.
