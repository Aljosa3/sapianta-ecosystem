# 1. Implementation Summary

G77-256KA Phase B authenticated the committed JZ baseline and exact bounded KA Phase-A delta, reconstructed the Phase-A identities without prior worker conversation or memory, authenticated the exact Human act, derived the canonical authority handoff, passed JZ preconsumption invocation binding, consumed the authority once, and performed exactly one FM/no-network-QEMU/VM attempt.

The attempt failed closed before the EXPIRED check and before any operational request or P11 entry. The guest booted and started the existing adapter, but the guest context owner raised `ContextError: sealed operation projection is not namespace-bound`. The evaluated operation namespace was `g77_256ka_fresh_expired_operational_recommissioning_v1`; the existing owner requires the lead `g77_256ka_expired_`. The guest harness exited `1`; QEMU performed the requested shutdown and returned `0` to FM. EXPIRED denial was not observed, so E05 remains 11/18 with zero credit.

Terminal: `M__KA_AUTHORIZED_EXPIRED_OPERATION_FAILED_AT_GUEST_CONTEXT_NAMESPACE_BINDING_BEFORE_REQUEST`.

Authenticated committed baseline: repository `/home/pisarna/work/sapianta-fl`; branch `g77-256fl-wrong-attempt-preboot-blocker`; HEAD `128bb145969a7b9ccebb8812b24216e00c7db04c`; TREE `47d09bc1d2ecf0529601ba65085651d01c325a7c`; subject `G77-256JZ verify FM authority digest preconsumption binding`; origin `git@github.com:Aljosa3/sapianta-ecosystem.git`; remote HEAD `128bb145969a7b9ccebb8812b24216e00c7db04c`. Nested authority remained clean, detached, pinned, and remote-tag-equal at HEAD `3183bab71f8f30397c0309dd2e6d846d14a11f66`, TREE `7c32ec05efc2be43297849bc38ec8766514a523d`.

# 2. Code Evidence

## Authority and JZ binding

The Human source SHA-256 is `00e24b7c7692b140e292d5cc8cc567b0b7330d85669f62711cd11ce0eefa3fe5`. The canonical handoff file SHA-256 is `98e514ad177a85ca358cec0f4f053abcfe49c47aaf24f108d70fd11e5ff90283`; its inner authorization SHA-256 is `7da1eafd20b781bf40c03ea3397b92d7d1d5aa1be66c4118f97b29c3e4a952d0`.

Before consumption, the JZ-owned builder derived and the JZ-owned validator revalidated:

- authenticated canonical authority digest: `98e514ad177a85ca358cec0f4f053abcfe49c47aaf24f108d70fd11e5ff90283`;
- sealed invocation authority digest: `98e514ad177a85ca358cec0f4f053abcfe49c47aaf24f108d70fd11e5ff90283`;
- final FM argv authority digest: `98e514ad177a85ca358cec0f4f053abcfe49c47aaf24f108d70fd11e5ff90283`.

The sealed invocation inner SHA-256 is `9afb51fe36f94298db5a33efc3b784f23821bb667f48476fbc3788d52f5e6c00`; the complete final FM argv SHA-256 is `583beb7ed1de21dfc82b9380ec904d1c2a08af8859e0fcdc5d7b4be64ac5da8c`. Caller/provider digest inputs were absent. Thirteen negative categories were rejected: 63-character, 65-character, wrong nibble, nonhex, whitespace, prefix/suffix, wrong/unrelated, missing digest, handoff/seal mismatch, seal/argv mismatch, caller substitution, provider substitution, and JY-style manual reconstruction.

The preconsumption checkpoint file SHA-256 is `d4dac52eace114cdb055c6bf6e0285e56d72d9928182221f71921958c7c35479`; its inner SHA-256 is `16759a697fb95ba16f354d461a0c8b3d92415287b770347d3c612943e8f793e7`. It records one authenticated authorization, zero consumption, zero FM invocation, zero QEMU/VM, and zero retry/replay before the irreversible transition.

## Operation and failure

The authority-consumption checkpoint proves `GRANTED_UNCONSUMED → CONSUMED`, final admission `PASS`, and consumption count `1`. The FM invocation-attempt and result artifacts prove invocation count `1` and host process exit status `0`. The sole PRE/POST receipt pair has SHA-256 identities `d3f18157ff4ce5a77859c91e90ffc615b8b27d7729f553a4129882f6a32bd6ba` and `8910c0ddc56e7d25ee1c598404519ba8dbd1523d3b190f6693de31328d1d2c12`; both bind the exact authority, request context, candidate, canonical argv, repository HEAD/TREE, one execution attempt, and `-nic none`.

The durable serial log SHA-256 is `45aad40d946b489f421dfb8bd87081e24ab298ec25ddde0f22949ba2ffecfa79`. It proves boot marker `PASS`, the exact guest context exception, guest harness exit status `1`, and powered-off teardown. No expected guest operational output was emitted beyond the preexisting context and continuation manifest, and the exact denial `one-use Human act expired before PRECLAIM` is absent.

The authoritative corrected terminal reduction is `G77_256KA_SPCE_TERMINAL_FAILURE_REDUCTION_V2.json`, file SHA-256 `6cc30d4d9cebd239afcdab8e583c4f733d5017a867d2bd534a88889ff379bf75`. V1 is preserved as superseded audit evidence: it incorrectly labeled the evaluated namespace as `operation_state`; V2 transparently binds and corrects that reporting-only reduction defect without authority action, FM invocation, QEMU, retry, repair retry, or replay.

## Reuse Impact Assessment

1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?

   EX 17/17, JZ digest-preserving invocation binding, JX admission/runtime role separation, JR stable runtime checkout, JV/GN presentation binding, FM, GL, ER, and P11 were reused.

2. Katere nove zmogljivosti (če sploh) nastanejo?

   No new EXPIRED operational capability was proven. One guest namespace-binding blocker was durably localized.

3. Ali katera obstoječa zmogljivost postane nedosegljiva?

   No production capability became unreachable through mutation. The one-shot KA authority is consumed and cannot be reused.

4. Ali implementacija ustvarja vzporedni tok?

   No. The existing FM/QEMU/guest/P11 route remained the sole route.

5. Ali zmanjšuje ali povečuje število produkcijskih poti?

   Neither. The production route count remains `1 → 1`.

# 3. Constitutional Self-Assessment

PROJECT_PROGRESS = `VERIFIED__KA_ONE_SHOT_FAILURE_DURABLY_REDUCED`

PROJECT_PROGRESS_ESTIMATE = `NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR`

INFORMAL_PROJECT_PROGRESS_ESTIMATE = `ESTIMATED__EXPIRED_OPERATION_BLOCKED_AT_GUEST_CONTEXT_NAMESPACE_BINDING`

CONSTITUTIONAL_HEALTH_EVIDENCE = `VERIFIED__FAIL_CLOSED_NO_RETRY_NO_P11_ENTRY_NO_PROTECTED_EFFECT`

SHADOW_AUTOMATION_STATUS = `VERIFIED__ABSENT`

CONSTITUTIONAL_FRONTIER_DISTANCE = `NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR`

E05_STATE = `VERIFIED__11_OF_18`; E05_FRONTIER = `VERIFIED__7_UNSATISFIED_OF_18`; E05_CREDIT = `VERIFIED__0`; EXPIRED = `NOT_PROVEN_OPERATIONALLY`.

GOVERNANCE_EFFICIENCE = `ESTIMATED__MEDIUM__ONE_SHOT_FAILURE_LOCALIZED_WITH_DURABLE_EVIDENCE`

OVERENGINEERING_RISK = `ESTIMATED__LOW__EVIDENCE_ONLY_TERMINAL_REDUCTION`

COGNITION_PROVENANCE = `VERIFIED__AUTHENTICATED_REPOSITORY_RECEIPT_AND_SERIAL_EVIDENCE_PRIMARY`

COGNITION_ASSISTED_HANDOFF = `VERIFIED__CROSS_ACCOUNT_REPOSITORY_ONLY_PHASE_A_RECOVERY`

CANDIDATE_CAPABILITY = `NOT_PROVEN__FRESH_EXPIRED_OPERATIONAL_DENIAL`

SHADOW_DESIGN_TARGET = `VERIFIED__SOLE_FM_ER_P11_ROUTE_WITH_STABLE_JR_EXPIRED_CHECKOUT`

CONSTITUTIONAL_CONTINUATION_PROGRESS = `VERIFIED__JZ_TO_KA_PRECONSUMPTION_BINDING_TO_ONE_GUEST_FAILURE`

LAST_VERIFIED_EDGE = `EXACT_HUMAN_AUTHORITY_AUTHENTICATED_JZ_BOUND_CONSUMED_ONCE_AND_ONE_NO_NETWORK_VM_BOOT_REACHED_GUEST_ADAPTER`

FIRST_BROKEN_EDGE = `GUEST_CONTEXT_OWNER_REJECTED_SEALED_OPERATION_EVIDENCE_ROOT_NAMESPACE_BEFORE_EXPIRED_SPECIALIZATION`

MINIMUM_MISSING_CAPABILITY = `PREAUTHORIZATION_OPERATION_NAMESPACE_COMPATIBLE_WITH_EXISTING_GUEST_CONTEXT_OWNER_NAMESPACE_RULE`

MINIMUM_LEGAL_NEXT_DELTA = `AFTER_HUMAN_REVIEW__SEPARATE_REPOSITORY_ONLY_NAMESPACE_BINDING_GENERATION__NO_KA_RETRY_OR_REPLAY`

ARCHITECTURAL_DELTA_BUDGET = `VERIFIED__PRODUCTION_MUTATION_0__P11_MUTATION_0__NEW_OWNER_0__NEW_ROUTE_0__NEW_REGISTRY_0__NEW_GENERIC_ABSTRACTION_0__NEW_CONSTITUTIONAL_CONCEPT_0__PRODUCTION_ROUTE_1_TO_1`

PROOF_YIELD = `VERIFIED__0_OPERATIONAL_EXPIRED_CAPABILITY__1_BLOCKER_LOCALIZED__0_E05_CREDIT__17_REUSED`

EX_REUSED = `VERIFIED__17_OF_17`; EX_RECONSTRUCTED = `VERIFIED__0`.

HAC / HAI / HAE = `NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED`.

Compact CCWIM: CCWIM_MATURITY_LEVEL = `ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION`; AUTHENTICATED_REPOSITORY_CONTINUATION = `VERIFIED__YES`; PREVIOUS_WORKER_CONVERSATION_REQUIRED = `VERIFIED__NO`; PREVIOUS_WORKER_MEMORY_REQUIRED = `VERIFIED__NO`; HANDOFF_RECONSTRUCTION_SUCCESS = `VERIFIED__YES`; HANDOFF_AMBIGUITY_COUNT = `VERIFIED__0`; OBSERVED_ARTIFACT_LEVEL_CROSS_WORKER_DRIFT = `VERIFIED__0`; CROSS_ACCOUNT_RECOVERY = `VERIFIED__YES`; CROSS_ACCOUNT_RECOVERY_SOURCE = `AUTHENTICATED_REPOSITORY_PHASE_A_PLUS_EXACT_HUMAN_ACT`.

# 4. Validation Matrix

| Requirement | Result |
|---|---|
| Repository path/branch/HEAD/TREE/subject/origin/direct remote; empty index | PASS |
| Exact bounded KA Phase-A delta | PASS before Human-source materialization |
| Nested authority clean/detached/pinned/remote-tag-equal | PASS |
| Phase-A terminal and all-zero counters | PASS |
| Exact Human act/request/checkpoint/context/candidate/argv/JZ/JR equivalence | PASS |
| Canonical handoff source and inner/file identities | PASS |
| JZ preconsumption digest equality and complete sealed FM argv | PASS |
| Required digest/substitution negative matrix | PASS—13/13 categories rejected |
| Preconsumption final admission | PASS—`ADMIT_TO_BOOT_BOUNDARY_ONLY` |
| Authority consumption | PASS—exactly 1; now nonreusable |
| FM/PRE/QEMU/VM | EXECUTED—1/1/1/1 |
| Network | PASS—`-nic none`; only guest loopback observed during boot |
| Guest operation | FAIL CLOSED—context namespace binding before specialization/request |
| EXPIRED denial | NOT OBSERVED—0 |
| P11 entry/protected invocation/protected effect | PASS—0/0/0 |
| Retry/repair retry/replay | PASS—0/0/0 |
| Durable receipt/serial/failure/reduction evidence | PASS |
| V1 reduction defect transparency and V2 correction | PASS—no operational action |
| Focused KA Phase-B terminal validation | PASS—5/5 |
| Governance conformance | PASS—9/9 tests; engine 20/20, CONFORMANT, zero warnings/violations |
| Production/P11 mutation; route count | PASS—0/0; `1 → 1` |
| G48 six H1 and five exact RIA questions | PASS |
| `git diff --check`; index empty | PASS |

Historical Phase-A-only tests were green before Phase B. After Human source/handoff materialization, two assertions that intentionally require their absence become lifecycle-inapplicable. The committed JZ point-in-time artifact equality test also differs only in the Python executable path selected by this account; historical evidence was not rewritten.

Exact counters: OPERATIONAL_AUTHORIZATION_COUNT `1`; AUTHORITY_CONSUMPTION_COUNT `1`; PRE_OPERATIONAL_COUNT `1`; FM_OPERATIONAL_INVOCATION_COUNT `1`; QEMU_COUNT `1`; VM_COUNT `1`; OPERATION_ATTEMPT_COUNT `1`; OPERATIONAL_REQUEST_COUNT `0`; EXPIRED_DENIAL_COUNT `0`; P11_ENTRY_COUNT `0`; PROTECTED_INVOCATION_COUNT `0`; PROTECTED_EFFECT_COUNT `0`; RETRY_COUNT `0`; REPAIR_RETRY_COUNT `0`; REPLAY_COUNT `0`.

# 5. Repository Mutation Summary

All 40 KA files are contained in `.github/governance/evidence/g77_256ka_fresh_expired_operational_recommissioning_v1/`: 22 Phase-A paths (including this report, now updated for the terminal result) and 18 Phase-B authority/binding/controller/receipt/serial/reduction/correction/validation files. Production mutation count is `0`; P11 implementation mutation count is `0`; new owner, production route, registry, generic abstraction, and constitutional concept counts are `0`; the production route remains `1 → 1`.

The V1 observation and reduction remain present as superseded audit evidence; V2 is the authoritative corrected reduction. No file outside the KA evidence root changed. Nothing was staged, committed, or pushed.

# 6. Certification Verdict

`M__KA_AUTHORIZED_EXPIRED_OPERATION_FAILED_AT_GUEST_CONTEXT_NAMESPACE_BINDING_BEFORE_REQUEST`

The exact Human authority was authenticated, JZ-bound before consumption, consumed exactly once, and used for exactly one governed FM/no-network-QEMU/VM attempt. The guest context owner failed closed before the EXPIRED specialization, request, P11 entry, protected invocation, or protected effect. The required denial was not observed; therefore EXPIRED is `NOT_PROVEN_OPERATIONALLY`, E05 credit is `0`, and E05 remains `VERIFIED__11_OF_18` with `VERIFIED__7_UNSATISFIED_OF_18`.

Authority state: `CONSUMED__NONREUSABLE__NONTRANSFERABLE`. No retry, replay, replacement authority, second KA attempt, or successor generation was created.

`AUTO_CONTINUABLE: NO`

`HUMAN_REVIEW_REQUIRED: YES`
