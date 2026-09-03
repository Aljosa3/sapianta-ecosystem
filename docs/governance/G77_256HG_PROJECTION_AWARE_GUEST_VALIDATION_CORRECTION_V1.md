# 1. Implementation Summary

Generation: `G77-256HG`.

Report identity:
`G77_256HG_PROJECTION_AWARE_GUEST_VALIDATION_CORRECTION_V1`.

Reporting date: 2026-09-03.

Constitutional baseline: `constitutional-governance-finalize-v1`; exact HF
commit `37e818d2ed9f6ff7ead3a8466253b582003c4b0f`, tree
`2dbb677d1d1ec209a56401b115184879fbb6a547`, stable ancestry anchor
`5c972e9960987ab27420395b54ace693df097e7b`, and nested authority
`3183bab71f8f30397c0309dd2e6d846d14a11f66` with tree
`7c32ec05efc2be43297849bc38ec8766514a523d`.

Implementation contracts: G48 Constitutional Evidence Reporting Standard V1,
the committed HF terminal report and reductions, FM fresh-operation-context
owner and sole launcher, HD guest context-owner binding, HE readiness, GY
WRONG_INPUT formalization/reducer, HA guest adapter, GP/GQ/GT checkout
lifecycle, and EX common certified proof substrate.

Objective: correct only the HF host/guest repository-path projection defect in
the existing FM context validator, prove the correction statically without
authority or operation, preserve the sealed host QEMU argv and all WRONG_INPUT
semantics, and stop with the delta unstaged for Human review.

`ENTRY_CHECKPOINT_STATUS = VERIFIED`. Local branch, HEAD, tree, subject, clean
worktree, empty index, stable ancestry, remote branch equality, and clean
detached pinned nested authority matched the exact commission before mutation.

The HF evidence was independently authenticated. The committed serial SHA-256
is `401ce0a9d244e5b77bce6ee89f72b800d7804c54b3483e69f8b72260796821be`;
the live context file SHA-256 is
`2da900cb4206d5365d97b76f7ea5b9f099968401ad2ebbf6db80fd29468e99ef`;
the terminal reduction file SHA-256 is
`eb344bfbd3823d95fa7d0112e4380b983f9a12581ec66cacb08f874708ff03c8`.
The serial and reductions agree that failure occurred in
`load_context -> validate_context` before runtime specialization,
`namespace["main"]()`, request construction, P11 entry, protected invocation,
or protected effect.

`FRONTIER_RECONSTRUCTION_STATUS = VERIFIED`.

`LAST_VERIFIED_EDGE = ONE_AUTHORIZED_FM_INVOCATION__ONE_NO_NETWORK_QEMU_BOOT__GUEST_CONTEXT_OWNER_LOADED__SEALED_CONTEXT_VALIDATION_ENTERED`.

`FIRST_BROKEN_EDGE = GUEST_CONTEXT_VALIDATION_REDERIVED_HOST_BOUND_DN_HARNESS_ARGV_PATH_FROM_GUEST_REPOSITORY_ROOT`.

`ROOT_CAUSE_CLASSIFICATION = VALIDATION_VIEW_CONFLATED_WITH_HOST_CANONICAL_IDENTITY_AT_AN_EXISTING_SEALED_PATH_PROJECTION_BOUNDARY`.

`IMPLICATED_OWNER_SET = [FM_FRESH_OPERATION_CONTEXT_OWNER, FM_SOLE_LAUNCHER_HASH_BINDING, HA_GUEST_CALLER]`; HA is a caller and remains unchanged.

`MINIMUM_MISSING_CAPABILITY = PROJECTION_AWARE_GUEST_VALIDATION_OF_SEALED_HOST_QEMU_ARGV_WITHOUT_WEAKENING_HOST_BINDING`.

`MINIMUM_LEGAL_NEXT_DEVELOPMENT_DELTA = AFTER_HUMAN_COMMIT_ONLY__ONE_BOUNDED_REPOSITORY_ONLY_POST_COMMIT_LIVE_BINDING_AND_READINESS_REAUTHENTICATION__NO_OPERATION`.

Modified modules and proof artifacts:

- the existing FM fresh-operation-context owner now derives one sealed host
  repository root and validates the unchanged canonical argv through either
  the exact host identity or `/mnt/aigol` guest view;
- the existing FM sole launcher binds the new owner SHA-256
  `db8257ab2e693edf842ba8224792910eb77a32116bf61cd60290d6ca535c73bf`;
- one HG test-only, non-authority projection fixture records the exact HF
  host/guest identities; and
- one focused HG regression module and this report provide repository evidence.

Intentionally unchanged: historical HF authority, context, argv, receipts,
serial, reductions, and report; HA/GY WRONG_INPUT owners; P11/CHE/FK; EX;
governance conformance; Layer 0; launcher entry point; and production routing.

# 2. Code Evidence

## Frontier owners, callers, and canonical fields

The exact owner is
`.github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/sapianta_fresh_operation_context_v1.py`.
Its `load_context` calls `validate_context`; HA
`load_guest_runtime_namespace` calls that loader with guest repository root
`/mnt/aigol`. FM host callers pass `/home/pisarna/work/sapianta-fl`.

The decisive fields are `operation_evidence_root`, `canonical_argv`,
`canonical_argv_sha256`, `guest_adapter_binding.projection_root`, and
`qemu_executable_base_seed_checkout_bindings`. The existing `aigol_checkout`
read-only mount binds the checkout presentation to `/mnt/aigol`; the existing
sealed operation root binds the host repository identity. No new context field,
schema, validator, launcher, or runtime route was introduced.

## Formal projection semantics

The formal identities are:

| Identity | Exact meaning |
|---|---|
| `HOST_CANONICAL_IDENTITY` | `/home/pisarna/work/sapianta-fl`, uniquely recovered from the sealed operation evidence path |
| `GUEST_PROJECTED_PATH` | `/mnt/aigol`, the existing read-only checkout presentation |
| `SEALED_HOST_QEMU_ARGV` | HF canonical argv retained byte-for-byte with host mount paths |
| `GUEST_VALIDATION_VIEW` | exact `/mnt/aigol` caller view selecting the sealed host identity for expectation reconstruction |
| `RUNTIME_EXECUTION_IDENTITY` | `/usr/bin/qemu-system-x86_64`, unchanged and still sealed |

The narrow allowed transformation is selection only:

`EXACT_GUEST_VIEW(/mnt/aigol) -> USE_UNIQUE_SEALED_HOST_ROOT_FOR_EXPECTED_ARGV`.

It does not transform, normalize, substitute, or rewrite any supplied argv
element. Therefore `VALID_PATH_PROJECTION != CANONICAL_ARGV_MUTATION`.

## Existing-owner correction

Exact representative excerpt; only the final evidence mapping is omitted:

```python
def validate_sealed_canonical_argv(
    context: dict[str, Any],
    *,
    validation_repository_root: Path,
) -> dict[str, str]:
    """Validate sealed host argv through either its host or exact guest view.

    Projection selects the host identity used to reconstruct the expectation;
    it never transforms the supplied argv.  Consequently the full canonical
    argv, including every non-path field, remains equality-checked and sealed.
    """

    view_root = validation_repository_root.resolve()
    operation_root = _absolute_canonical_path(
        context["operation_evidence_root"], "operation_evidence_root"
    )
    try:
        sealed_host_root = _derive_sealed_host_repository_root(
            context, operation_root
        )
    except ContextError:
        if view_root == GUEST_REPOSITORY_ROOT:
            raise
        sealed_host_root = view_root
        projection_status = "HOST_VALIDATION_WITHOUT_GUEST_PROJECTION"
    else:
        if view_root not in {sealed_host_root, GUEST_REPOSITORY_ROOT}:
            raise ContextError("repository validation view is not projection-bound")
```

The public validator reconstructs the expected argv with
`sealed_host_root / DN_HARNESS_RELATIVE_PATH`, then retains the exact existing
checks:

```python
    if context["canonical_argv"] != expected_argv:
        raise ContextError("canonical argv changed outside approved operation slots")
    digest = argv_sha256(expected_argv)
    if context["canonical_argv_sha256"] != digest:
        raise ContextError("canonical argv seal mismatch")
```

`validate_context` delegates to this function once. The HA caller requires no
change because its existing guest root is already the exact certified view.

## Projection binding and rejection boundaries

The sealed host root is accepted only when the operation root contains exactly
one `.github/governance/evidence` marker, ends in the exact
`<identity_namespace_prefix>_*/operation_state` namespace, and the sealed seed
is repository-resident under the same host root. Zero markers are missing
binding; two markers are ambiguity. A view other than the recovered host root
or `/mnt/aigol` is rejected. The whole argv equality check rejects both a DN
host path mutation and a non-path CPU mutation even when the attacker
recomputes `canonical_argv_sha256` and `context_sha256`.

The HG fixture is explicitly
`TEST_ONLY__NON_AUTHORITY__NON_OPERATIONAL__NON_EXECUTABLE`. The validator
returns identity evidence only, mutates no context, invokes no subprocess, and
contains no authority, request, P11, or effect path.

## Reuse analysis

`REUSED_CAPABILITY_SET = [HF_TERMINAL_FRONTIER, HE_READINESS, GY_WRONG_INPUT_FORMALIZATION_AND_REDUCER, HA_GUEST_ADAPTER, HD_SELF_CONTAINED_CONTEXT_OWNER_CHECKOUT, FM_CONTEXT_AND_SOLE_LAUNCHER, GP_GQ_GT_CHECKOUT_LIFECYCLE, GN_PRESENTATION, GL_RECEIPT_BOUNDARY, ER_CHECKPOINT_OWNER, DU_EB_EE, P11_CHE_FK, GOVERNANCE_CONFORMANCE, EX_COMMON_SUBSTRATE]`.

`REUSED_OWNER_SET = [FM_CONTEXT_OWNER, FM_SOLE_LAUNCHER, HA_CALLER, GY_MUTATION_OWNER, GP_GQ_GT_CHECKOUT_OWNERS, P11_CHE_FK_OWNERS, EX_VALIDATOR]`.

`REUSED_PROOF_SET = [HF_SERIAL_AND_TERMINAL_REDUCTIONS, HE_STATIC_READINESS, HD_OWNER_BINDING, GY_SEMANTIC_FIREWALL, GP_GQ_GT_GH_PROJECTION_TESTS, P11_CHE_FK_TESTS, GOVERNANCE_AND_LAYER_TESTS, EX_17_OF_17]`.

`NEW_CAPABILITY_REQUIRED = YES__ONE_NARROW_PROJECTION_AWARE_VALIDATION_RULE_INSIDE_EXISTING_OWNER`.

`NEW_OWNER_REQUIRED = NO`.

## Static host/guest equivalence proof

`HOST_CANONICAL_BINDING_STATUS = VERIFIED`.

`GUEST_PROJECTION_BINDING_STATUS = VERIFIED`.

`PROJECTION_EQUIVALENCE_STATUS = VERIFIED`.

`HOST_BINDING_PRESERVATION_STATUS = VERIFIED`.

`UNAUTHORIZED_MUTATION_REJECTION_STATUS = VERIFIED`.

`HF_FAILURE_CLASS_STATIC_BLOCK_STATUS = VERIFIED`.

The committed HF context produces `EXACT_GUEST_PROJECTION`, the original
canonical argv SHA-256 `60027a7424727fcc6af40e819fde27df5c4f4d8884ea1f5aedec5a1007062b49`,
and the original host identity while validation is viewed from `/mnt/aigol`.
No QEMU or VM was used.

# 3. Constitutional Self-Assessment

## Verified

- exact entry checkpoint, remote equality, stable ancestry, empty index, and
  clean detached pinned nested authority;
- HF frontier and counters directly from immutable serial/context/reductions;
- exact valid host-to-guest projection acceptance;
- rejection of unauthorized host canonical argv mutation, wrong guest view,
  missing projection, ambiguous projection, and non-path argv mutation;
- sealed argv and context remain unmodified by validation;
- projection adds no Human authority, operation authority, request, P11 entry,
  invocation, effect, retry, repair, replay, or E05 credit;
- historical HF material is unchanged;
- WRONG_INPUT semantic firewall remains
  `CASE = E05_NEGATIVE_AUTHORITY_WRONG_INPUT`,
  `TARGET_MUTATION = input_identity`,
  `DEPENDENT_RECOMPUTATION = record_identity`, mutation count one, differing
  fields `input_identity, record_identity`;
- one existing launcher `main`, one QEMU call site, and one production route;
- governance conformance remains deterministic, read-only, fail-closed, and
  conformant; and
- `EX_REUSED = 17/17`, `EX_RECONSTRUCTED = 0`.

## Not Verified

- post-commit binding of the new owner SHA into a clean detached checkout at a
  future committed HG HEAD/tree;
- future DU/EB/EE live receipts and preoperational readiness against that
  committed identity;
- any operational guest execution of the corrected owner;
- WRONG_INPUT request construction, P11 entry, denial, protected invocation,
  protected effect, operational capability, or E05 credit in HG; and
- provider capacity, token, cost, or global project-progress measurements not
  supported by repository instrumentation.

## Capability and readiness boundary

| Metric | Classification | Evidence-bounded result |
|---|---|---|
| `CANDIDATE_CAPABILITY` | VERIFIED | HG repository candidate correction and focused proof |
| `PROJECTION_AWARE_VALIDATION_CANDIDATE_CAPABILITY` | VERIFIED | exact rule implemented in existing owner |
| `PROJECTION_AWARE_VALIDATION_REPOSITORY_CAPABILITY` | VERIFIED | focused positive/negative static matrix passes |
| `PROJECTION_AWARE_VALIDATION_OPERATIONAL_CAPABILITY` | NOT_PROVEN | zero operation |
| `WRONG_INPUT_CANDIDATE_CAPABILITY` | VERIFIED | unchanged GY/HA semantics and hashes |
| `WRONG_INPUT_REPOSITORY_CAPABILITY` | VERIFIED | existing repository path remains reachable after corrected validation |
| `WRONG_INPUT_OPERATIONAL_CAPABILITY` | NOT_PROVEN | no request/P11/denial operation |
| `POST_COMMIT_LIVE_BINDING_STATUS` | NOT_PROVEN | future committed HG HEAD/tree required |
| `PREOPERATIONAL_READINESS_STATUS` | NOT_PROVEN | post-commit binding/readiness remains |
| `NEXT_OPERATIONAL_GENERATION_ELIGIBLE` | NOT_PROVEN | HG creates no future authority |

E05 is unchanged: `E05_BEFORE = 7/18`, `E05_AFTER = 7/18`,
`E05_CREDIT = 0`.

## Incremental proof-impact analysis

`CHANGED_OWNER_SET = [FM_FRESH_OPERATION_CONTEXT_OWNER, FM_SOLE_LAUNCHER_OWNER_HASH_BINDING]`.

`DEPENDENT_PROOF_SET = [FM_CONTEXT_VALIDATION_AND_IMMUTABLE_BINDING, HA_GUEST_CONTEXT_CALL, HD_HE_OWNER_CHECKOUT_BINDINGS, GP_GQ_GT_GH_PROJECTION_AND_CHECKOUT, GY_WRONG_INPUT_REACHABILITY, FUTURE_DU_EB_EE_LIVE_BINDING]`.

`INVALIDATED_PROOF_FRONTIER = [PRE_HG_FM_CONTEXT_OWNER_HASH, PRE_HG_COMMITTED_CHECKOUT_HEAD_TREE, PRE_HG_DU_EB_EE_LIVE_RECEIPTS, PREDECESSOR_EXACT_SNAPSHOT_REBUILD_ASSERTIONS]`.

`REVALIDATED_PROOF_SET = [HG_10_CASE_FOCUSED_MATRIX, GD_CURRENT_CONTEXT_BEHAVIOR, HA_UNAFFECTED_SEMANTICS, HD_HE_UNAFFECTED_FIREWALL_AND_REPORT_STRUCTURE, GY_UNAFFECTED_SEMANTICS, GP_GQ_GT_GH, P11_CHE_FK, GOVERNANCE_AND_LAYERS, GOVERNANCE_CONFORMANCE, EX, LAYER0, PYTHON_AST, DIFF_WHITESPACE]`.

`REUSED_UNCHANGED_PROOF_SET = [HF_IMMUTABLE_HISTORY, GY_MUTATION_AND_REDUCER, HA_SPECIALIZATION, GP_GQ_GT_GH_CHECKOUT_SEMANTICS, P11_CHE_FK, GOVERNANCE_CONFORMANCE, EX_17_OF_17]`.

`REQUIRED_REVALIDATION` covers the new HG matrix, the FM owner/launcher
binding, guest/host projection owners, semantic firewall, and constitutional
conformance. `REUSED_BY_AUTHENTICATED_IDENTITY` covers unchanged HF, GY/HA,
P11/CHE/FK, governance, and EX bytes. `HISTORICAL_NON_APPLICABLE` covers 20
raw-suite nodes that intentionally require GX/GZ/HC/HD predecessor HEADs,
pre-HG candidates, or the old FM owner hash; these were reproduced and not
counted as current passes.

## Reuse Impact Assessment

1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo? HF
   terminal evidence, FM sealed context and one-shot route, existing checkout
   and guest projection bindings, HE/HD readiness, GY/HA WRONG_INPUT semantics,
   GP/GQ/GT/GH, GN/GL/ER, DU/EB/EE, P11/CHE/FK, governance, and EX 17/17.
2. Katere nove zmogljivosti (če sploh) nastanejo? One bounded repository
   capability: projection-aware validation of sealed host argv through the
   exact guest checkout view, implemented in the existing owner.
3. Ali katera obstoječa zmogljivost postane nedosegljiva? No. Pre-HG live
   bindings are historical identities, while future current binding awaits a
   post-commit generation.
4. Ali implementacija ustvarja vzporedni tok? No.
5. Ali zmanjšuje ali povečuje število produkcijskih poti? Neither.

`PRODUCTION_ROUTE_BEFORE = 1`, `PRODUCTION_ROUTE_AFTER = 1`,
`PRODUCTION_ROUTE_DELTA = 0`.

## CCWIM

The historical HF report demonstrated a prior cross-worker continuation. HG
itself used one worker and does not elevate that historical fact to HG L5.

| Metric | Classification | Evidence-bounded result |
|---|---|---|
| `CCWIM_MATURITY_LEVEL` | ESTIMATED | L4-like repository-authenticated continuation; L5 not claimed |
| `CROSS_WORKER_STATE_RECOVERY_LEVEL` | NOT_APPLICABLE | HG did not continue an uncommitted cross-worker delta |
| `REPOSITORY_DERIVED_CONTEXT_RATIO` | ESTIMATED | dominant; prompt supplied scope/checkpoint, repository proved facts |
| `HUMAN_HANDOFF_INFORMATION_REQUIRED` | VERIFIED | bounded HG commission only; no operational grant |
| `PROMPT_CONTEXT_REUSE_RATIO` | NOT_MEASURED | no token attribution instrument |
| `PREVIOUS_WORKER_CONVERSATION_REQUIRED` | VERIFIED | no |
| `AUTHENTICATED_REPOSITORY_CONTINUATION` | VERIFIED | exact committed HF continuation |
| `INTRA_TASK_CROSS_WORKER_CONTINUATION` | NOT_APPLICABLE | one HG worker |
| `UNCOMMITTED_DELTA_RECOVERY` | NOT_APPLICABLE | entry worktree was clean |
| `CROSS_WORKER_CONSTITUTIONAL_DRIFT` | NOT_APPLICABLE | no HG worker handoff |
| `SAME_WORKER_PROVIDER_RESET_RESUME` | NOT_APPLICABLE | no reset/resume |
| `HANDOFF_SUFFICIENCY_STATUS` | VERIFIED | repository plus commission sufficient |
| `HANDOFF_PROMPT_ELIGIBILITY` | VERIFIED | repository-only HG eligible; operation ineligible |
| `HANDOFF_STATE_COMPLETENESS` | VERIFIED | exact base/frontier reconstructable |
| `HANDOFF_RECONSTRUCTION_REQUIRED` | VERIFIED | HF frontier independently reconstructed |
| `HANDOFF_RECONSTRUCTION_SUCCESS` | VERIFIED | hashes, serial, reductions, and call chain agree |
| `HANDOFF_AMBIGUITY_COUNT` | VERIFIED | 0 |
| `UNAUTHENTICATED_HANDOFF_ASSUMPTION_COUNT` | VERIFIED | 0 |

## Cost, reuse, token, and project metrics

| Metric | Classification | Evidence-bounded result |
|---|---|---|
| `WORKERS_USED` | VERIFIED | 1 for HG; HF historical worker count not attributed to HG |
| `PROVIDER_CAPACITY_START` | NOT_MEASURED | no provider-capacity instrument exposed |
| `PROVIDER_CAPACITY_END` | NOT_MEASURED | no provider-capacity instrument exposed |
| `PROVIDER_CAPACITY_CONSUMED` | NOT_MEASURED | percentages are not token counts |
| `WALL_TIME` | NOT_MEASURED | no generation wall-clock instrument |
| `LLM_EXECUTION_EFFICIENCY` | NOT_MEASURED | no calibrated denominator |
| `REVALIDATION_CASE_COUNT` | VERIFIED | exact family counts in Section 4; no blind historical-universe count |
| `NEW_CODE` | VERIFIED | one in-place validator helper/rule, one hash binding, one test fixture |
| `REUSED_CODE` | VERIFIED | existing FM/HA/GY/checkout/P11/governance route |
| `NEW_PROOF` | VERIFIED | ten focused HG nodes plus this G48 evidence |
| `REUSED_PROOF` | VERIFIED | authenticated unchanged proof families above |
| `REVALIDATED_PROOF` | VERIFIED | affected families in Section 4 |
| `RECONSTRUCTED_PROOF` | VERIFIED | 0 EX proofs; HF frontier reconstructed, not rebuilt |
| `TOKEN_BENCHMARK` | NOT_MEASURED | no token telemetry |
| `LLM_COST_REDUCTION_RATIO / LCRR` | NOT_MEASURED | no comparable cost baseline |
| `PROJECT_PROGRESS_ESTIMATE` | ESTIMATED | HG repository correction complete; product-wide denominator unavailable |
| `CONSTITUTIONAL_HEALTH_EVIDENCE` | VERIFIED | fail-closed negatives, one route, zero operation, conformant engine |
| `SHADOW_AUTOMATION_STATUS` | VERIFIED | disabled; auto-continuable no |
| `CONSTITUTIONAL_FRONTIER_DISTANCE` | NOT_MEASURED | no global scalar instrument |
| `E05_FRONTIER_DISTANCE` | VERIFIED | 11 of 18 obligations remain |
| `SELECTED_E05_LOCAL_FRONTIER_DISTANCE` | ESTIMATED | one post-commit live-binding/readiness generation before operational review |
| `GOVERNANCE_EFFICIENCE` | ESTIMATED | EX 17/17 reused; affected frontier only revalidated |
| `ARCHITECTURAL_GOVERNANCE_EFFICIENCE` | ESTIMATED | existing owner/route reused; no parallel architecture |
| `PROOF_REUSE_EFFICIENCE` | ESTIMATED | unchanged proof families reused by identity; no reliable percentage denominator |
| `COGNITION_ASSISTED_HANDOFF` | VERIFIED | repository evidence enabled independent HF reconstruction |
| `AIGOL_CODEX_WORK_SHARE` | NOT_MEASURED | no attribution instrument |
| `OVERENGINEERING_RISK` | ESTIMATED | low/contained; no schema or generic projection framework added |
| `PROOF_PROCESS_OVERHEAD_RISK` | ESTIMATED | moderate; predecessor snapshots explicitly isolated |
| `COGNITION_PROVENANCE` | VERIFIED | Human commission, repository evidence, and Codex reasoning remain distinct |
| `SHADOW_DESIGN_TARGET` | VERIFIED | FORMALIZE_REUSE_BIND_VERIFY |
| `CONSTITUTIONAL_CONTINUATION_PROGRESS` | VERIFIED | HG repository Branch A proof complete; operational frontier unchanged |

`CAPABILITY_REUSE != COMPUTE_COST_REDUCTION` and
`PROOF_REUSE != AUTOMATICALLY_LOW_LLM_COST`; no contrary cost claim is made.

## Zero-operation counters

| Counter | Value |
|---|---:|
| `HUMAN_OPERATIONAL_AUTHORITY` | 0 |
| `AUTHORITY_CONSUMPTION` | 0 |
| `PRE` | 0 |
| `FM_OPERATIONAL_LAUNCHER_INVOCATION` | 0 |
| `QEMU` | 0 |
| `VM_CREATION` | 0 |
| `VM_BOOT` | 0 |
| `OPERATION_ATTEMPT` | 0 |
| `WRONG_INPUT_OPERATION` | 0 |
| `REQUEST` | 0 |
| `P11_ENTRY` | 0 |
| `PROTECTED_INVOCATION` | 0 |
| `PROTECTED_EFFECT` | 0 |
| `RETRY` | 0 |
| `REPAIR_AND_CONTINUE` | 0 |
| `OPERATIONAL_REPLAY` | 0 |
| `E05_CREDIT` | 0 |

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| Exact HG entry | branch/HEAD/tree/subject/status/index/remote/ancestry | local Git plus `git ls-remote` | PASS |
| Nested authority | tag/HEAD/tree/detached/clean | nested Git inspection | PASS |
| HF frontier authentication | serial, context, terminal and independent reductions | SHA-256, canonical JSON load, focused HG proof | PASS |
| Focused HG semantics | HG test module | `10 passed` | PASS |
| Exact projection acceptance | committed HF context and HG fixture | public projection validator | PASS |
| Host canonical argv mutation rejection | resealed hostile fixture | focused HG negative | PASS |
| Wrong/missing/ambiguous projection rejection | three hostile fixtures | focused HG negatives | PASS |
| Non-path mutation rejection | resealed CPU mutation | focused HG negative | PASS |
| No authority/request/effect expansion | non-mutating result/API/AST | focused HG negative | PASS |
| Historical HF immutability | HF namespace and report | Git diff plus known SHA-256 identities | PASS |
| WRONG_INPUT firewall | GY/HA hashes and constants | focused HG plus applicable HA/GY tests | PASS |
| FM/GD and applicable HA behavior | GD and HA suites | `25 passed, 2 deselected` | PASS |
| Applicable HD behavior | same-class and semantic-firewall nodes | `2 passed, 6 deselected` | PASS |
| Applicable HE behavior | semantic-firewall and G48 nodes | `2 passed, 9 deselected` | PASS |
| GY current semantic nodes | GY suite | `21 passed, 3 historical nodes excluded` | PASS |
| Raw HA/HD/HE impact audit | all nodes before selection | `29 passed, 17 expected predecessor/binding failures` | NOT_APPLICABLE |
| Raw GY predecessor audit | all GY nodes | `21 passed, 3 expected predecessor/candidate failures` | NOT_APPLICABLE |
| GP/GQ/GT/GH projection and checkout | four owner suites | `26 passed` | PASS |
| P11/CHE/FK non-regression | four directly named suites | `47 passed` | PASS |
| Governance/layer behavior | decision, risk, failure, layer tests | `23 passed` | PASS |
| Governance conformance tests | conformance module | `9 passed` | PASS |
| Governance conformance engine | deterministic engine | 20/20, zero warnings/violations | PASS |
| EX common substrate | EX validator | 12/12; certified 17 reused | PASS |
| Layer 0 freeze | nested checker | manifest present and enforced | PASS |
| Python syntax/AST | owner, launcher, fixture, tests | compile and AST parsing | PASS |
| Canonical/duplicate-key validation | unchanged HF JSON and test loader | duplicate-key rejecting canonical load | PASS |
| Repository whitespace/index | complete delta | `git diff --check`; cached diff empty | PASS |
| Human authority/PRE/FM operation/QEMU/VM/P11 operation | prohibited boundary | intentionally not executed | NOT_APPLICABLE |
| Operational projection/WRONG_INPUT capability | requires future authority and operation | intentionally not run | NOT_RUN |

The `NOT_APPLICABLE` raw snapshot failures are evidence of correct incremental
impact classification, not current passes and not hidden failures. They bind
predecessor HEADs, previously sealed candidates/contexts, or the old FM owner
SHA. The current selected frontier and new HG negatives establish the
repository claim. `NOT_RUN` operational capability is preserved under Not
Verified and prevents any operational certification.

# 5. Repository Mutation Summary

Material HG paths:

- `.github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/sapianta_fresh_operation_context_v1.py` — in-place projection-aware argv validation;
- `.github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py` — exact new owner hash binding only;
- `.github/governance/evidence/g77_256hg_guest_projection_validation_v1/static/G77_256HG_GUEST_HOST_PATH_PROJECTION_FIXTURE_V1.py` — test-only exact projection fixture;
- `.github/governance/evidence/g77_256hg_guest_projection_validation_v1/tests/test_g77_256hg_guest_projection_validation_v1.py` — focused proof matrix; and
- this G48 report.

Unchanged subsystems: HF historical evidence; Human authority; GY/HA; P11;
canonical CHE; FK; EX; governance conformance; Layer 0; production entry point;
and all non-projection runtime semantics.

API compatibility: `load_context` and `validate_context` signatures are
unchanged. `validate_sealed_canonical_argv` is an additive validator. Existing
host contexts without a repository-resident operation projection preserve the
legacy host validation path; exact guest validation fails closed when the
projection binding is missing.

Boundary preservation: the launcher still has one `main()` and one QEMU call
site. No operational command was invoked. No historical artifact was edited.
No generic translator, parallel validator, parallel context owner, parallel
launcher, new runtime route, or production effect path exists.

All HG changes remain unstaged. The final terminal inventory, name-only diff,
stat, whitespace check, and cached-diff emptiness were re-read after report
completion. `AUTO_CONTINUABLE = NO`. `HUMAN_REVIEW_REQUIRED = YES`.

# 6. Certification Verdict

VERIFIED__G77_256HG_PROJECTION_AWARE_VALIDATION_REPOSITORY_CAPABILITY__HF_FAILURE_CLASS_STATIC_BLOCKED__ZERO_OPERATION__E05_7_OF_18__POST_COMMIT_LIVE_BINDING_NOT_PROVEN__HUMAN_REVIEW_REQUIRED
