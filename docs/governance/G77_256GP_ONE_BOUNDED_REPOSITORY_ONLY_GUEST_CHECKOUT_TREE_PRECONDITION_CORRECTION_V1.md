# 1. Implementation Summary

G77-256GP completed one repository-only correction of the GO guest checkout/tree authentication precondition gap. It used no Human operational authority, did not invoke the governed launcher, did not execute QEMU, did not boot a VM, and did not perform a WRONG_ATTEMPT, request, P11 entry, protected invocation, protected effect, retry, repair, or replay.

The immutable entry checkpoint authenticated as follows:

| Property | Authenticated value |
|---|---|
| Repository | `/home/pisarna/work/sapianta-fl` |
| Branch | `g77-256fl-wrong-attempt-preboot-blocker` |
| Local HEAD | `a448ee30c787544e3cfbb628857e2fadda276dd9` |
| TREE | `8f085ebf7b031405ffaac4b293f294d6873332cd` |
| Subject | `G77-256GO fail closed on guest checkout tree authentication` |
| Remote HEAD | `a448ee30c787544e3cfbb628857e2fadda276dd9` |
| Local/remote equality | VERIFIED |
| Stable ancestry | `5c972e9960987ab27420395b54ace693df097e7b` ancestral |
| Index/worktree before mutation | empty/clean |
| Nested authority | clean, detached, pinned at `3183bab71f8f30397c0309dd2e6d846d14a11f66` |
| Nested TREE | `7c32ec05efc2be43297849bc38ec8766514a523d` |
| Nested ref | `refs/tags/sapianta-system-nested-authority-3183bab-v1` |
| Layer 0 freeze | PASS |

The five-hour account window had 97% remaining before mutation and 32% at terminal reduction. The required pre-mutation proceed gate was therefore satisfied. These values are resource-capacity telemetry only; they were not used as token, billing, LCRR, constitutional-authority, or operational-authority evidence. Context remaining percentage was not measured.

The committed GO terminal reduction was independently reauthenticated. Its file SHA-256 is `934981d45536369611a4a3a30cbf52d182b72a90194286054850aa8145e05467`; its canonical inner SHA-256 is `5b736a2e6428cd46b9deeb3f3db96059f0698a3c981a08e2a347ab59b66f413d`. Its terminal verdict remains:

`FAIL_CLOSED__G77_256GO_GUEST_CHECKOUT_TREE_AUTHENTICATION_FAILED_BEFORE_REQUEST__NO_RETRY_REPAIR_REPLAY__E05_REMAINS_6_OF_18__HUMAN_REVIEW_REQUIRED`

The GO Human authority remains consumed, terminal, non-reusable, and non-transferable. No authority survived and no historical authority was reused by GP.

## Root-cause reduction

The exact historical data path was:

```text
/tmp/g77_256fm/checkout
  -> QEMU -virtfs local,path=/tmp/g77_256fm/checkout,
       mount_tag=aigol_checkout,security_model=none,readonly=on
  -> guest 9p read-only mount at /mnt/aigol
  -> unchanged ER command-scoped Git consumer
  -> git -c safe.directory=/mnt/aigol rev-parse HEAD^{tree}
```

The guest mount existed: cloud-init printed the boot marker only after all four mounts succeeded. `/mnt/aigol` presented a `.git` directory and a readable detached `HEAD` containing `7dce67ec18696ba0bad73130f3f7a84168f25277`. No ref lookup was required for that detached HEAD. The historical expected TREE `3cb61ec34e9593efb711dce61014dc8fdf0f6dd9` was correct when resolved on the host.

The checkout was not, however, a guest-self-contained Git representation. Its local object count was zero and `.git/objects/info/alternates` contained:

```text
/home/pisarna/work/sapianta/.git/objects
```

That absolute object database was outside the sole checkout export. Host `rev-parse` succeeded by following this non-presented alternate; ER inside the guest could not reach the commit/tree objects required by `HEAD^{tree}`. Read-only presentation did not itself change Git semantics, Git metadata inside the root was preserved, and `safe.directory` was already supplied. The defect was the unproved external object dependency.

Therefore:

| Classification | Value |
|---|---|
| ROOT_CAUSE_CLASS | `GIT_OBJECT_DATABASE_ALTERNATE_ESCAPES_READ_ONLY_PRESENTATION_ROOT__HOST_TREE_FALSE_POSITIVE` |
| SOURCE_OWNER | `FM_SHARED_DETACHED_CHECKOUT_MATERIALIZATION` |
| PREPARATION_OWNER | `EXISTING_FM_CHECKOUT_PREBOOT_READINESS` |
| PRESENTATION_OWNER | `EXISTING_FM_CANONICAL_QEMU_CHECKOUT_VIRTFS_BINDING` |
| BINDING_OWNER | `EXISTING_FM_AUTHORITY_FREE_STATIC_READINESS` |
| GUEST_CONSUMER_OWNER | `EXISTING_ER_GUEST_CHECKOUT_IDENTITY_AUTHENTICATION` |
| REJECTING_OWNER | `EXISTING_ER_RUN_GIT_HEAD_TREE_CONSUMER` |
| FIRST_BROKEN_EDGE | `GO_GUEST_READ_ONLY_CHECKOUT_BINDING_TO_ER_PRECONDITION_TREE_AUTHENTICATION` |
| MINIMUM_SAFE_CORRECTION_OWNER_SET | existing FM readiness; existing FM/FY presentation binding; unchanged ER consumer |

The same failure was deterministically predictable before Human authority by checking the exported Git representation's gitdir, common directory, object database, alternates, required-object reachability, exact presentation root, and exact ER consumer semantics. No QEMU discovery was necessary.

## Exact correction

The existing FM authority-free readiness owner now calls `prove_guest_checkout_tree_precondition` from `validate_checkout_preboot_readiness`. The correction:

- resolves `.git` directory and gitfile forms without allowing escape from the presentation root;
- resolves `commondir` without allowing escape;
- requires readable HEAD and object metadata;
- recursively closes Git object alternates inside the presentation root and rejects external or HTTP alternates;
- rejects Git metadata symlink escape;
- re-runs ER-equivalent `rev-parse HEAD`, `rev-parse HEAD^{tree}`, `cat-file -t TREE`, and `status --porcelain` observations with host Git override variables removed;
- requires observed HEAD and TREE to equal the sealed expectations;
- binds exactly one read-only `aigol_checkout` QEMU 9p export of the same source root;
- binds the immutable cloud-init destination and unchanged ER consumer to `/mnt/aigol`;
- rejects caller-supplied readiness/destination overrides; and
- reobserves on every readiness call, so stale proof reuse cannot bridge later authority.

This call remains inside `authority_free_static_readiness`, which is invoked before `load_authority`, before FO final admission, before PRE, and before the sole QEMU call site. The historical shared checkout now fails at preauthorization. A future separately reviewed generation must materialize a self-contained checkout and regenerate fresh post-commit live bindings before any separately authorized operation.

`PREAUTH_GUEST_CHECKOUT_TREE_EQUIVALENCE = VERIFIED_WITHIN_EXACT_REVIEWED_BOUNDARY` for the deterministic boundary comprising host Git representation closure, the exact QEMU 9p argument, the exact immutable guest mount destination, and unchanged ER Git command semantics. Full runtime transport behavior without a VM is `NOT_PROVEN`; GP does not broaden the claim to a new operational or QEMU proof.

# 2. Code Evidence

The existing implementation owner was modified at:

- `.github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py`;
- corrected file SHA-256: `d84ab1a21b0a9c45083681a4a23d83bbc583da0c01fe1b58611205c6009796c8`.

The focused repository-only matrix was added at:

- `.github/governance/evidence/g77_256gp_guest_checkout_tree_precondition_v1/tests/test_g77_256gp_guest_checkout_tree_precondition_v1.py`;
- test file SHA-256: `f5cfe8b3685634987f619325ea58addba08d3e9ce7c0bcc0043bc5bf23014194`.

The earlier GD test that treated the historically shared checkout as a positive fixture now expects the corrected authority-free owner to reject its external alternate. It does not alter production flow.

The replay-safe terminal reduction is:

- `.github/governance/evidence/g77_256gp_guest_checkout_tree_precondition_v1/G77_256GP_SPCE_FINAL_REPOSITORY_ONLY_REDUCTION_V1.json`;
- canonical inner SHA-256: `f8948b4ecc0a07b865d06d404e830ba216b8aa4fd841e54cae18883561d3269b`.

Representative corrected control order remains:

```text
authority_free_static_readiness
  -> validate_checkout_preboot_readiness
  -> prove_guest_checkout_tree_precondition
  -> load_authority
  -> final reobservation
  -> FO final admission
  -> PRE
  -> sole subprocess.run(argv, check=False)
  -> POST
```

No new launcher, QEMU route, authorization model, receipt subsystem, P11 route, ER verifier, protected-effect route, repair path, retry path, replay path, or caller readiness boolean was introduced.

## GO historical counters

| Counter | GO value |
|---|---:|
| HUMAN_CONSTITUTIONAL_AUTHORIZATION_COUNT | 1 |
| PRE_COUNT | 1 |
| POST_COUNT | 1 |
| GOVERNED_LAUNCHER_ACTIVATIONS | 1 |
| QEMU_EXECUTION_COUNT | 1 |
| VM_BOOT_COUNT | 1 |
| OPERATION_ATTEMPT_COUNT | 1 |
| WRONG_ATTEMPT_EXECUTION_COUNT | 0 |
| REQUEST_COUNT | 0 |
| P11_ENTRY_COUNT | 0 |
| PROTECTED_INVOCATION_COUNT | 0 |
| PROTECTED_EFFECT_COUNT | 0 |
| RETRY_COUNT | 0 |
| REPAIR_EXECUTION_COUNT | 0 |
| REPLAY_EXECUTION_COUNT | 0 |

## GP operational counters

All GP operational counters are zero:

| Counter | GP value |
|---|---:|
| HUMAN_OPERATIONAL_AUTHORIZATION_COUNT | 0 |
| GOVERNED_LAUNCHER_ACTIVATIONS | 0 |
| QEMU_EXECUTION_COUNT | 0 |
| VM_BOOT_COUNT | 0 |
| WRONG_ATTEMPT_EXECUTION_COUNT | 0 |
| OPERATION_ATTEMPT_COUNT | 0 |
| REQUEST_COUNT | 0 |
| P11_ENTRY_COUNT | 0 |
| PROTECTED_INVOCATION_COUNT | 0 |
| PROTECTED_EFFECT_COUNT | 0 |
| RETRY_COUNT | 0 |
| REPAIR_EXECUTION_COUNT | 0 |
| REPLAY_EXECUTION_COUNT | 0 |

# 3. Constitutional Self-Assessment

GP followed `FORMALIZE -> REUSE -> BIND -> VERIFY`. It formalized the exact ER property, reused the FM/FY presentation and ER consumer owners, bound Git representation closure to the existing preauthorization gate, and verified both acceptance and fail-closed cases. It did not reconstruct or weaken EX, FO, P11, CHE, FK, GJ, GN, GL, or ER.

EX was reused `17/17`; `EX_RECONSTRUCTED = 0`. The unchanged EX validator passed 12/12, reported 17 certified components, and produced zero operational and credit effect.

`E05_BEFORE = 6/18`

`E05_CREDIT_AWARDED = 0`

`E05_AFTER = 6/18`

## Same-class review

`SAME_CLASS_REVIEW_COMPLETE = YES`

`SECOND_INDEPENDENT_INSTANCE_FOUND = NO`

`SYSTEMATIC_ARCHITECTURE_REVIEW_REQUIRED = NO`

The bounded neighboring review covered:

- GH/FM adapter source -> exact host projection -> `fm_harness` export -> `/mnt/dp-harness` consumer;
- FY runtime context -> exact runtime-export file -> `g77_evidence` export -> `/mnt/g77-evidence` consumer; and
- DN harness source -> exact `g77_harness` export -> `/mnt/g77-harness` consumer.

Those bindings already use exact regular-file byte hashes, exact host roots, exact unique mount tags, exact guest paths, immutable cloud-init commands, and exact consumers. No second independent external Git-object or equivalent producer/consumer precondition mismatch was found within the immediate reviewed boundary.

## Architecture counters

| Counter | Value |
|---|---:|
| NEW_LAUNCHERS | 0 |
| NEW_PRODUCTION_ROUTES | 0 |
| NEW_AUTHORIZATION_MODELS | 0 |
| NEW_RECEIPT_SUBSYSTEMS | 0 |
| NEW_VALIDATOR_ARCHITECTURES | 0 |
| PARALLEL_EXECUTION_FLOWS | 0 |
| PRODUCTION_ROUTE_DELTA | 0 |

## Required metrics

| Metric | Classification | Result |
|---|---|---|
| PROJECT_PROGRESS_ESTIMATE | ESTIMATED | GO guest tree gap now fails closed before authority within the reviewed boundary. |
| CONSTITUTIONAL_HEALTH_EVIDENCE | VERIFIED | External Git object dependencies are rejected before authority, FO, PRE, or execution. |
| SHADOW_AUTOMATION_STATUS | VERIFIED | Repository-only validation active; zero operational automation. |
| CONSTITUTIONAL_FRONTIER_DISTANCE | NOT_MEASURED | No canonical scalar; E05 remains 6/18. |
| WRONG_ATTEMPT_LOCAL_FRONTIER_DISTANCE | ESTIMATED | A future self-contained checkout and fresh live binding are required before separate authority. |
| GOVERNANCE_EFFICIENCE | ESTIMATED | One existing-owner extension blocks the historical false positive with zero machine execution. |
| OPERATIONAL_PROOF_YIELD | VERIFIED | Zero operational proof and zero E05 credit. |
| COGNITION_ASSISTED_HANDOFF | VERIFIED | Root cause, owner set, proof boundary, and validation are sealed. |
| AIGOL_CODEX_WORK_SHARE | NOT_MEASURED | No deterministic percentage instrument exists. |
| OVERENGINEERING_RISK | ESTIMATED | Low: existing owner only; zero route or architecture delta. |
| COGNITION_PROVENANCE | VERIFIED | Repository, Codex, Human, and provider provenance are separated. |
| CANDIDATE_CAPABILITY | NOT_PROVEN | No WRONG_ATTEMPT request or P11 operation occurred. |
| SHADOW_DESIGN_TARGET | VERIFIED | The exact known guest-precondition false positive now fails before authority. |
| CONSTITUTIONAL_CONTINUATION_PROGRESS | ESTIMATED | GO terminal finding reduced to one bounded repository correction. |
| PROMPT_CONTEXT_REUSE_RATIO | NOT_MEASURED | No token/context-ratio instrument exists. |
| TOKEN_BENCHMARK | NOT_MEASURED | Account-window telemetry is not token telemetry. |
| LLM_COST_REDUCTION_RATIO / LCRR | NOT_MEASURED | No comparable billable-cost baseline exists. |
| HUMAN_INTERVENTION_EFFICIENCY | NOT_APPLICABLE | GP used zero Human operational authorizations. |
| PREAUTH_GUEST_CHECKOUT_TREE_EQUIVALENCE | VERIFIED | `VERIFIED_WITHIN_EXACT_REVIEWED_BOUNDARY`. |
| SAME_CLASS_REVIEW_STATUS | VERIFIED | Complete; no second independent instance found. |
| FORMALIZE_REUSE_BIND_VERIFY_COMPLIANCE | VERIFIED | Existing FM/FY/ER owners reused and bound without a parallel flow. |

## Cognition provenance

- REPOSITORY / SEALED DETERMINISTIC EVIDENCE: Git identities, GO evidence and seals, checkout `.git` structure, alternates path, object count, QEMU argv, cloud-init mount, ER source, test results, EX output, conformance output, and GP inner seal.
- PREVIOUS CODEX COGNITION: nonauthoritative; not used as authority or proof.
- CURRENT CODEX COGNITION: root-cause classification, minimum-owner selection, implementation strategy, same-class classification, metrics, and conservative reduction.
- HUMAN AUTHORITY: historical GO authority only; consumed, terminal, non-reusable, non-transferable. GP authority count is zero.
- PROVIDER PERMISSION: infrastructure permission only; never constitutional execution authority.

## Reuse Impact Assessment

1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo? EX 17/17 and existing FM, FY, ER, GH, FO, generic P11, canonical CHE, and FK owners.
2. Katere nove zmogljivosti nastanejo? One bounded preauthorization checkout/tree presentation proof extension inside the existing FM owner. It is a strengthened binding proof, not a new validator architecture or execution route.
3. Ali katera obstoječa zmogljivost postane nedosegljiva? No. The historically invalid shared checkout representation becomes inadmissible; no valid capability becomes unreachable.
4. Ali implementacija ustvarja vzporedni tok? No.
5. Ali zmanjšuje ali povečuje število produkcijskih poti? Neither; production route delta is zero.

Candidate identity binding remains `VERIFIED`. Candidate capability remains `NOT_PROVEN`. `CANDIDATE_SEMANTICS_CHANGED = NO`. `CANDIDATE_BINDING_REGENERATION_REQUIRED = YES`, because a future committed generation must bind the new repository HEAD/TREE and corrected owner through the existing post-commit live-binding discipline.

# 4. Validation Matrix

| Requirement | Method | Result |
|---|---|---|
| Exact GP entry | direct Git path/branch/HEAD/TREE/subject/status | PASS |
| Remote equality | `git ls-remote` exact branch | PASS |
| Stable ancestry | `merge-base --is-ancestor` | PASS |
| Nested authority | origin/ref/HEAD/TREE/status/detached | PASS |
| Layer 0 freeze | existing nested freeze checker | PASS |
| GO terminal reduction | unique-key JSON, canonical inner SHA-256, counters/verdict | PASS |
| Historical root cause | `.git`, HEAD, object count, alternates, QEMU/cloud-init/ER audit | PASS |
| Positive self-contained checkout | exact HEAD/TREE/status and local object reachability | PASS |
| Missing checkout / `.git` | focused negative tests | PASS: rejected |
| Malformed/unreachable gitfile | focused negative tests | PASS: rejected |
| Unreachable common-dir | focused negative test | PASS: rejected |
| Missing HEAD / missing ref / unresolved HEAD | focused negative tests | PASS: rejected |
| Missing required tree object / wrong TREE | focused negative tests | PASS: rejected |
| External/HTTP/malformed alternates | focused negative tests | PASS: rejected |
| Git metadata symlink escape | focused negative test | PASS: rejected |
| Stale checkout / stale evidence reuse | mutate after a passing observation and reobserve | PASS: rejected |
| Wrong source/presentation/mount tag | focused negative tests | PASS: rejected |
| Wrong guest destination | tampered cloud-init contract test | PASS: rejected |
| Caller readiness override | focused negative test | PASS: rejected |
| Different HEAD/TREE evidence | exact expectation mismatch tests | PASS: rejected |
| GP focused suite | pytest | 12/12 PASS |
| Affected owner stack | GP, GD, FY, GH, GA, GF, GJ, GL, FO suites | 71/71 PASS |
| P11/CHE/FK regression | DI/P11 substrate/FK/canonical CHE tests | 47/47 PASS |
| EX common substrate | unchanged EX validator | 12/12 PASS; 17 certified |
| Governance conformance engine | canonical read-only engine | 20/20 PASS; CONFORMANT; zero warnings/violations |
| Governance conformance tests | pytest | 9/9 PASS |
| JSON unique keys and GP inner seal | duplicate-rejecting load plus canonical SHA-256 | PASS |
| QEMU | prohibited for GP | NOT_APPLICABLE; count 0 |
| Operational credit from tests | counter discipline | false; E05 credit 0 |

The only validation adjustment to a prior test is intentional: the GD fixture using `/tmp/g77_256fm/checkout` now proves that the corrected owner rejects the exact historical shared-object false positive. All other existing affected suites remain passing.

# 5. Repository Mutation Summary

The GP mutation set is bounded to:

- modified existing FM launcher/readiness owner;
- modified one prior GD expectation to recognize the newly inadmissible historical fixture;
- added one GP focused test matrix;
- added one GP sealed terminal reduction; and
- added this G48 report.

No runtime P11, CHE, FK, ER harness, cloud-init, QEMU argv builder, authorization model, receipt subsystem, constitutional Layer 0/1 artifact, nested authority, production route, or deployment file changed.

All mutations remain unstaged. No `git add`, commit, push, reset, clean, stash, checkout, restore, or history rewrite occurred. Terminal `git status --short` is:

```text
 M .github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py
 M .github/governance/evidence/g77_256gd_fresh_operation_context_v1/tests/test_sapianta_fresh_operation_context_v1.py
?? .github/governance/evidence/g77_256gp_guest_checkout_tree_precondition_v1/
?? docs/governance/G77_256GP_ONE_BOUNDED_REPOSITORY_ONLY_GUEST_CHECKOUT_TREE_PRECONDITION_CORRECTION_V1.md
```

Terminal `git diff --name-only` lists the two tracked modifications. Terminal tracked `git diff --stat` reports two files changed, 275 insertions, and 14 deletions. The three untracked GP files are enumerated above and in this mutation summary. `git diff --check` passed for tracked changes; no-index whitespace checks passed for each untracked file. Human review remains required.

# 6. Certification Verdict

`PASS__G77_256GP_GO_GUEST_CHECKOUT_TREE_PRECONDITION_GAP_CORRECTED__EXISTING_OWNER_PATH_REUSED__PREAUTH_GUEST_CHECKOUT_TREE_PROPERTY_VERIFIED_WITHIN_EXACT_REVIEWED_BOUNDARY__SAME_CLASS_REVIEW_COMPLETE__EX_17_OF_17_REUSED__NO_OPERATIONAL_AUTHORITY__NO_QEMU__PRODUCTION_ROUTE_DELTA_ZERO__E05_REMAINS_6_OF_18__HUMAN_REVIEW_REQUIRED`

This PASS is repository-only. It does not prove WRONG_ATTEMPT operational success, P11 entry, canonical CHE production, FK operational success, candidate operational capability, QEMU transport execution under GP, E05 credit, or future operational authority.

`AUTO_CONTINUABLE = NO`

`HUMAN_REVIEW_REQUIRED = YES`

`NEXT_LEGAL_ACTION = HUMAN_REVIEW_OF_UNSTAGED_GP_MUTATIONS`

G77-256GQ was not prepared or executed.
