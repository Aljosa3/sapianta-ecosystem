# 1. Implementation Summary

Generation: `G77_256KX_EXISTING_FM_RUNTIME_EXPORT_CUSTODY_PERMISSION_BINDING_REPAIR_V1`.

KX is a repository-only repair. The authenticated entry is branch `g77-256fl-wrong-attempt-preboot-blocker`, HEAD `e691b568c0136d3079b5a546e5f8536f1805f7ee`, tree `70416c1ea4e1a2fc0cb0c065e8243d12545000e7`, subject `G77-256KW localize runtime export custody edge`, with equal origin branch and stable ancestry anchor `5c972e9960987ab27420395b54ace693df097e7b`. The nested authority remains clean, detached, pinned, and remote-tag-equal at `3183bab71f8f30397c0309dd2e6d846d14a11f66` / tree `7c32ec05efc2be43297849bc38ec8766514a523d`.

The committed KW terminal is authenticated as `I__KW_PROVIDER_RECOVERY__NEW_RUNTIME_EXPORT_CUSTODY_EDGE_FOUND__CLASSIFIED__FAIL_CLOSED__NO_RETRY`. Its one Human authority was consumed exactly once and is nonreusable and nontransferable. KW performed one FM/QEMU/VM attempt, passed guest commissioning P01–P12, and failed before an EXPIRED request or P11 entry with `PermissionError` at `/mnt/g77-evidence/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json`. Request, EXPIRED denial, P11 entry, protected invocation, protected effect, retry, repair retry, and replay counts are all zero.

Failure class is `NEW_SEMANTIC_EDGE`. This is distinct from KE/KF: KF repaired the guest-harness projection root, while KW authenticated a separate FM runtime-export root at `0700`, owned by UID/GID `1000/1000`, presented to custody UID/GID `3/3`; its direct sealed-context child was `0664`. The sole production route was blocked before the vector request, without protected effect. KW’s frontier movement past KF and P01–P12 is operational-frontier movement, not E05 credit movement.

SPCE Phase A authenticated one unique owner, `G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py:materialize_operation_state`, and the complete relevant pre-request traversal set: the intact KF guest-harness root plus the FM runtime-export root. The legal candidate preserves private `0700` construction, materializes the initial manifest and sealed context, then presents only the runtime-export root as `0701`. For an unrelated custody principal, this adds the one required search bit; it adds neither directory listing nor directory write. The existing `0664` context grants other-read and denies other-write. No Human operational ceremony applies to KX.

`REPOSITORY_ONLY_PROOF != OPERATIONAL_PROOF`

# 2. Code Evidence

The existing FM owner now declares `RUNTIME_EXPORT_ROOT_CONSTRUCTION_MODE = 0o700` and `RUNTIME_EXPORT_ROOT_PRESENTATION_MODE = 0o701`. `materialize_operation_state` creates the exact existing root with the construction mode, writes the existing runtime manifest and context projection, applies the presentation mode only after both writes, and fails closed if the observed final mode differs.

The delta changes no mount tag, guest path, adapter, serializer, registry, authority owner, route owner, P11 implementation, or teardown owner. The existing `g77_evidence` 9p mapping to `/mnt/g77-evidence` remains unique. The operation evidence root, transient root, guest-harness projection root, checkout, receipts, and unrelated evidence roots are unchanged.

The deterministic formalizer authenticates committed KW bytes and seals, exact counters, authority terminality, P01–P12 records, the KW observation, unique FM owner, source ordering, the one-bit POSIX contract, unique mount presentation, KF integrity, P11 identity, EX reuse, and bounded mutation inventory. Focused tests additionally materialize local filesystem modes and reject permission widening.

Failure novelty and convergence:

- `AFFECTED_INVARIANT = GUEST_CUSTODY_MUST_LOAD_SEALED_OPERATION_CONTEXT_BEFORE_GATE_WITHOUT_WRITE_AUTHORITY`.
- `PREVIOUS_CLOSEST_EDGE = KE_GUEST_HARNESS_ROOT_TRAVERSAL_DENIAL`.
- `SEMANTIC_DIFFERENCE = KF_REPAIRED_GUEST_HARNESS_ROOT__DISTINCT_FM_RUNTIME_EXPORT_ROOT_REMAINED_0700`.
- `NEW_CAPABILITY_REQUIRED = VERIFIED__BOUNDED_EXISTING_FM_RUNTIME_EXPORT_PRESENTATION_BINDING`.
- `NEW_PROOF_REQUIRED = VERIFIED__REPOSITORY_ONLY_SEARCH_TRAVERSAL_AND_CONTEXT_READ_WITHOUT_WRITE`.
- `REPETITION_PRESSURE = VERIFIED__HIGH__E05_REMAINS_11_OF_18_ACROSS_MULTIPLE_GENERATIONS`.
- `VERIFICATION_AMPLIFICATION_RISK = ESTIMATED__LOW_AFTER_COMPLETE_PRE_REQUEST_TRAVERSAL_CONTRACT_AUTHENTICATION`.
- `OVERENGINEERING_RISK = ESTIMATED__LOW__ONE_EXISTING_OWNER_ONE_BIT_PRESENTATION_DELTA`.
- `CLASSIFICATION_CONFIDENCE = VERIFIED__HIGH`.
- `ACCEPTANCE_REQUIREMENT_FORCING_CONTINUATION = VERIFIED__KX_REPOSITORY_REPAIR_AND_DETERMINISTIC_PROOF_ONLY`.

Cross-vector reuse assessment separates two domains. Authority lifecycle remains `MULTI_VECTOR_REUSABLE`: the reusable component is the direct Human UTF-8 source bytes → derived digest → canonical handoff → one-shot consumption pattern; exact Human source and generation/vector bindings require revalidation, with no authority or E05-credit transfer. Runtime-export presentation is `COMMON_E05_INFRASTRUCTURE`: all authenticated existing FM vector contexts use the same direct runtime-export root and sealed-context layout. Vector adapter semantics and each operational outcome remain vector-specific, and common reuse provides no vector operational proof.

# 3. Constitutional Self-Assessment

Project state is `VERIFIED__KX_REPOSITORY_PERMISSION_BINDING_REPAIRED_PENDING_HUMAN_REVIEW`. Project progress is `VERIFIED__KW_RUNTIME_EXPORT_BLOCKER_CLOSED_IN_REPOSITORY_ONLY_PROOF__E05_UNCHANGED`. A scalar project-progress estimate is `NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR`; the informal estimate is `ESTIMATED__ONE_PRE_REQUEST_REPOSITORY_BLOCKER_CLOSED__OPERATIONAL_FRONTIER_NOT_RETESTED`.

Constitutional health is `VERIFIED__MINIMUM_ONE_BIT_OWNER_DELTA__NO_AUTHORITY_OR_ROUTE_EXPANSION`. Shadow automation is `VERIFIED__ABSENT`. Constitutional frontier distance is `NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR`. Governance efficiency is `ESTIMATED__HIGH__AUTHENTICATED_OWNER_AND_KF_PATTERN_REUSED`; overengineering risk is `ESTIMATED__LOW`. Cognition provenance is `VERIFIED__AUTHENTICATED_REPOSITORY_EVIDENCE_PRIMARY`, and the assisted handoff is `VERIFIED__KW_TO_KX_REPOSITORY_CONTINUATION`.

Candidate capability is `VERIFIED__REPOSITORY_ONLY_RUNTIME_EXPORT_SEARCH_AND_CONTEXT_READ_CONTRACT`; the shadow design target remains the sole FM→ER→P11 route. Constitutional continuation progress is `VERIFIED__FORMALIZE_REUSE_BIND_VERIFY_COMPLETE_FOR_KX`. The last verified operational edge remains KW’s one attempt through P01–P12 and the context permission failure. The first unverified operational edge is repaired context load followed by EXPIRED request and denial. No post-repair operation was performed. Human review and a later commit/push are the current continuation boundary; a separate future operational generation would require fresh Human authority.

E05 remains `VERIFIED__11_OF_18`; the frontier remains `VERIFIED__7_UNSATISFIED_OF_18`; KX credit is `VERIFIED__0`; EXPIRED is `NOT_PROVEN_OPERATIONALLY`. EX is reused `VERIFIED__17_OF_17` and reconstructed `VERIFIED__0`. `HAC_HAI_HAE = NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED`.

Architectural delta budget and observed use: one existing FM production file, zero new owner, zero new route, zero new registry, zero new generic abstraction, zero new constitutional concept, zero P11 implementation mutation, production route `1 → 1`, and `PARALLEL_FLOW = NO`.

Proof yield: one new repository-verified capability, zero new operational capability, zero new operational observation, zero new E05 credit, zero newly localized blocker, one repository blocker closed, 17 EX proofs reused, and zero EX reconstruction.

Compact CCWIM: authenticated repository continuation `VERIFIED__YES`; previous worker conversation required `VERIFIED__NO`; previous worker memory required `VERIFIED__NO`; handoff ambiguity count `VERIFIED__0`; binding-owner ambiguity count `VERIFIED__0`; authority-state ambiguity count `VERIFIED__0`; operational-attempt ambiguity count `VERIFIED__0`.

Reuse Impact Assessment:

1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?

   Reused: the existing FM materialization and export owner, KF search-only final-presentation pattern, committed KW failure and terminal evidence, unchanged P11 identity, and EX `17/17` common proof substrate.

2. Katere nove zmogljivosti (če sploh) nastanejo?

   One repository-only capability: the existing FM runtime-export root is finally presented with search-only custody traversal so the already-readable sealed context can be loaded. No operational capability or E05 credit is created.

3. Ali katera obstoječa zmogljivost postane nedosegljiva?

   No. Existing materialization, KF presentation, authority lifecycle, mount, cleanup, and the sole route remain reachable and unchanged in identity.

4. Ali implementacija ustvarja vzporedni tok?

   No. It changes the final permission presentation inside the existing FM owner only.

5. Ali zmanjšuje ali povečuje število produkcijskih poti?

   Neither. The production-path count remains `1 → 1` through FM→ER→P11.

# 4. Validation Matrix

| Evidence | Result |
|---|---|
| Starting branch, HEAD, tree, subject, origin, remote equality, stable ancestry, clean index/worktree | PASS |
| Nested authority clean, detached, pinned, tree/origin/tag and remote tag equality | PASS |
| Committed KW terminal, canonical seals, Human source hash, one consumption/attempt, zero retry/replay | PASS |
| KW FM/QEMU/VM path, guest P01–P12, exact runtime-export permission failure | PASS |
| Existing FM owner/materialization/mount and KF comparison | PASS |
| One-bit `0700 → 0701` search-only contract; context `0664` read/no-write | PASS |
| Focused KX deterministic mode, AST/order, negative widening, G48/reduction tests | PASS__10_OF_10 |
| KW Phase-B committed recovery-terminal tests | PASS__6_OF_6 |
| Existing FO launcher admission tests | PASS__5_OF_5 |
| Governance conformance tests | PASS__9_OF_9 |
| Governance conformance engine | PASS__20_CHECKS__CONFORMANT |
| Python compile/AST, canonical KX JSON and inner seals | PASS |
| G48 exactly six H1 and exactly five required Slovenian questions | PASS |
| Bounded mutation inventory and `git diff --check` | PASS |
| QEMU, VM, P11 operational route, EXPIRED operation | NOT_APPLICABLE__PROHIBITED_FOR_KX |

Historical self-replay limitation: suites whose contract is to require their own former live entry or exact former post-generation launcher bytes are not successor-working-tree tests. The audit run observed KW Phase A `2/10` (eight expected former-KV-entry mismatches), KF `5/11` (six expected exact post-KF launcher/current-untracked-state mismatches), FY `1/3`, and GD `14/17` (the five FY/GD failures use placeholder identities rejected by the later current-head route guard). These failures pre-existed the KX permission predicate or are necessarily caused by advancing the exact launcher identity; KX does not rewrite historical evidence to make it self-certify a successor. Current KX tests instead reauthenticate committed KW and KF identities, replay their required semantics, and prove the successor launcher contract directly. This limitation does not expand KX proof scope.

# 5. Repository Mutation Summary

Tracked production mutation: `.github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py`, with 12 insertions and 1 deletion. Generation-local additions are this report, one formalizer, one focused test module, and one canonical sealed terminal reduction. There are no unrelated mutations.

The index is empty. Nothing is staged, committed, or pushed. `AUTO_CONTINUABLE = FALSE`; `HUMAN_REVIEW_REQUIRED = TRUE`. KX created no operational Human authority, consumed no authority, performed no operation, and did not retry or replay KW.

# 6. Certification Verdict

`A__KX_EXISTING_FM_RUNTIME_EXPORT_PERMISSION_BINDING_REPAIR_VERIFIED__REPOSITORY_ONLY__NO_OPERATION`
