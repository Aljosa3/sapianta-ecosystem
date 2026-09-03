# 1. Implementation Summary

Generation: `G77-256HI`.

Report identity:
`G77_256HI_CURRENT_HG_FM_CHECKOUT_OWNER_BINDING_CORRECTION_V1`.

Reporting date: 2026-09-03.

Constitutional baseline: `constitutional-governance-finalize-v1`; exact
committed HH checkpoint `f784bb7afe1d1f8279ba9d58edbda92dc26329c8`, tree
`32bd68a38962f1b0e0d73dd40cb988ef398455f0`, subject
`G77-256HH fail closed stale HG checkout owner binding`, stable ancestry anchor
`5c972e9960987ab27420395b54ace693df097e7b`, and committed HG predecessor
`842a0f2cccd53222d11daa698bdeab17f0aac043`, tree
`414a5f940e3b5027b6dd86c38d7a134f5c8ab0c4`.

Implementation contracts: the G77-256HI commission, authenticated HH Branch B
terminal evidence, G48 Constitutional Evidence Reporting Standard V1, the
existing FM context/checkout/live-binding architecture, HG host/guest
projection semantics, GY/HA WRONG_INPUT semantics, DU/EB/EE, and EX common
certified proof substrate.

Objective: correct only the stale FM checkout HEAD/tree owner selection so the
existing checkout presents the exact committed HG context-owner bytes before
authority. No operational authority, PRE, FM operational launcher invocation,
QEMU, VM, request, P11 entry, protected invocation/effect, retry, repair,
replay, or E05 credit is in scope.

`ENTRY_CHECKPOINT_STATUS = VERIFIED`. The expected branch, HEAD, tree, subject,
live remote branch equality, stable ancestry, clean worktree, empty index, and
clean detached nested authority were independently authenticated before
mutation. The nested authority is pinned locally and remotely at
`3183bab71f8f30397c0309dd2e6d846d14a11f66`, tree
`7c32ec05efc2be43297849bc38ec8766514a523d`, under
`refs/tags/sapianta-system-nested-authority-3183bab-v1`.

`HH_TERMINAL_EVIDENCE_AUTHENTICATION_STATUS = VERIFIED`.
`HH_TERMINAL_REDUCTION_STATUS = VERIFIED__BRANCH_B`.
`HH_CURRENT_CANDIDATE_STATUS = PASS`.
`HH_DU_STATUS = PASS`.
`HH_EB_STATUS = PASS`.
`HH_EE_STATUS = PASS`.
`HH_REQUIRED_HG_OWNER_SHA256 = db8257ab2e693edf842ba8224792910eb77a32116bf61cd60290d6ca535c73bf`.
`HH_ACTUAL_CHECKOUT_OWNER_SHA256 = 45b97e99122146ec3aa95f45fe5ac71381ca1a11e83b7355438b988608f52fca`.
`HH_STALE_BINDING_MISMATCH_STATUS = VERIFIED`.
`HH_PREAUTHORIZATION_REJECTION_STATUS = VERIFIED`.

The HH report SHA-256 is
`1aceef11dc64eaf254c52349cbf416212206afc0b8e839d2bbd51c4cb2f07948`;
its sealed terminal reduction remains immutable Branch B. HH candidate and
runtime projection remain byte-identical at SHA-256
`7ab5997938bbb618b949930e1cd2e3be2f145175110a8ef6bccc0571eb39e194`.

The independently reconstructed frontier is:

```text
LAST_VERIFIED_EDGE = CURRENT_HG_CANDIDATE_AND_FRESH_DU_EB_EE_AUTHENTICATED_BEFORE_FM_CHECKOUT_OWNER_ADMISSION
FIRST_BROKEN_EDGE = FM_LAUNCHER_CHECKOUT_OWNER_IDENTITY_REMAINS_BOUND_TO_PRE_HG_OWNER_INSTEAD_OF_REQUIRED_COMMITTED_HG_OWNER
MINIMUM_MISSING_CAPABILITY = EXACT_CURRENT_HG_FM_CHECKOUT_OWNER_BINDING_WITHOUT_SEMANTIC_AUTHORITY_OR_ROUTE_EXPANSION
```

HI changes the two existing FM launcher constants `CHECKOUT_HEAD` and
`CHECKOUT_TREE` from the pre-HG checkout to exact committed HG. The existing
materializer, context builder, context owner, owner-hash key, preauthorization
validator, guest read-only projection, and one production route are reused
unchanged. This is a predecessor binding, not a future-HI self-reference: the
launcher selects immutable committed HG, whose owner bytes already have the
required authenticated identity.

`REUSE_SEARCH_STATUS = VERIFIED`.
`REUSED_BINDER_SET = [FM_CONTEXT_BUILDER, GQ_CHECKOUT_MATERIALIZER, GP_CHECKOUT_PREAUTHORIZATION, FM_OWNER_PREAUTHORIZATION, GY_PRODUCER, DU_VALIDATOR, EB_VALIDATOR, EE_VALIDATOR]`.
`REUSED_OWNER_SET = [FM_SOLE_LAUNCHER, FM_FRESH_OPERATION_CONTEXT_OWNER, HG_COMMITTED_CHECKOUT, GY_WRONG_INPUT_OWNERS, P11_CHE_FK, EX_COMMON_SUBSTRATE]`.
`REUSED_VALIDATOR_SET = [FM_IMMUTABLE_CONTEXT_VALIDATOR, FM_CHECKOUT_TREE_VALIDATOR, FM_CONTEXT_OWNER_VALIDATOR, HG_PROJECTION_VALIDATOR, GY_REDUCER, GOVERNANCE_CONFORMANCE]`.
`NEW_GENERIC_FRAMEWORK_REQUIRED = NO`.

## Reuse Impact Assessment

1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo? Existing
   FM context building, GQ self-contained checkout materialization, GP
   checkout preauthorization, FM exact owner verification, HG projection,
   GY/HA semantic firewall, DU/EB/EE, P11/CHE/FK, governance conformance, Layer
   0 freeze, and EX 17/17.
2. Katere nove zmogljivosti (če sploh) nastanejo? One bounded repository
   capability: the existing FM route can select committed HG as checkout owner.
   No new operational, authority, launcher, validator-architecture, context
   owner, candidate route, runtime route, or receipt capability is created.
3. Ali katera obstoječa zmogljivost postane nedosegljiva? No. Pre-HG bindings
   remain immutable historical evidence; current callers retain the same APIs.
4. Ali implementacija ustvarja vzporedni tok? No.
5. Ali zmanjšuje ali povečuje število produkcijskih poti? Neither.

`PRODUCTION_ROUTE_BEFORE = 1`.
`PRODUCTION_ROUTE_AFTER = 1`.
`PRODUCTION_ROUTE_DELTA = 0`.

## CCWIM

| Metric | Classification | Evidence-bounded result |
|---|---|---|
| `CCWIM_MATURITY_LEVEL` | ESTIMATED | L4-like repository-authenticated continuation; L5 not claimed |
| `CROSS_WORKER_STATE_RECOVERY_LEVEL` | NOT_APPLICABLE | HI began from a clean committed HH checkpoint |
| `REPOSITORY_DERIVED_CONTEXT_RATIO` | ESTIMATED | dominant; the prompt supplied scope and expected checkpoint, repository bytes proved identities and flow |
| `HUMAN_HANDOFF_INFORMATION_REQUIRED` | VERIFIED | bounded HI commission only; no operational grant |
| `PROMPT_CONTEXT_REUSE_RATIO` | NOT_MEASURED | no token-attribution instrument |
| `PREVIOUS_WORKER_CONVERSATION_REQUIRED` | VERIFIED | no |
| `AUTHENTICATED_REPOSITORY_CONTINUATION` | VERIFIED | exact committed HH continuation |
| `INTRA_TASK_CROSS_WORKER_CONTINUATION` | NOT_APPLICABLE | one HI worker |
| `UNCOMMITTED_DELTA_RECOVERY` | NOT_APPLICABLE | clean entry worktree |
| `CROSS_WORKER_CONSTITUTIONAL_DRIFT` | NOT_APPLICABLE | no HI worker handoff |
| `SAME_WORKER_PROVIDER_RESET_RESUME` | NOT_APPLICABLE | no reset/resume |
| `HANDOFF_SUFFICIENCY_STATUS` | VERIFIED | repository plus bounded commission were sufficient |
| `HANDOFF_PROMPT_ELIGIBILITY` | VERIFIED | repository-only correction eligible; operation ineligible |
| `HANDOFF_STATE_COMPLETENESS` | VERIFIED | exact base and frontier reconstructable |
| `HANDOFF_RECONSTRUCTION_REQUIRED` | VERIFIED | HH frontier independently reconstructed |
| `HANDOFF_RECONSTRUCTION_SUCCESS` | VERIFIED | report, reduction, hashes, checkout objects, and call chain agree |
| `HANDOFF_AMBIGUITY_COUNT` | VERIFIED | 0 |
| `UNAUTHENTICATED_HANDOFF_ASSUMPTION_COUNT` | VERIFIED | 0 |

Historical HF cross-worker evidence is not elevated into an HI-specific
cross-worker claim.

# 2. Code Evidence

## Exact owner authentication and producer/consumer chain

SHA-256 was recomputed from Git object bytes, not copied from the commission:

| Object | Authenticated identity | Result |
|---|---|---|
| `HG:sapianta_fresh_operation_context_v1.py` | `db8257ab2e693edf842ba8224792910eb77a32116bf61cd60290d6ca535c73bf` | exact required owner |
| `a5fde262:sapianta_fresh_operation_context_v1.py` | `45b97e99122146ec3aa95f45fe5ac71381ca1a11e83b7355438b988608f52fca` | exact stale owner |
| committed HG tree | `414a5f940e3b5027b6dd86c38d7a134f5c8ab0c4` | exact checkout tree |
| pre-HG checkout tree | `c265719bc048a9ab686e290d1952280d5584a43e` | exact stale checkout tree |

The binding flow is:

```text
FM launcher CHECKOUT_HEAD/CHECKOUT_TREE
-> FM build_operation_context checkout binding
-> existing GQ self-contained detached checkout materializer
-> exact repository object bytes at FM context-owner path
-> existing FM prove_guest_fresh_operation_context_owner_binding
-> read-only /mnt/aigol guest projection admission before authority
```

`STALE_BINDING_OWNER = FM_SOLE_LAUNCHER_CHECKOUT_HEAD_TREE_CONSTANTS`.
`STALE_BINDING_FIELD = qemu_executable_base_seed_checkout_bindings.checkout.{head,tree}`.
`STALE_OWNER_SHA256 = 45b97e99122146ec3aa95f45fe5ac71381ca1a11e83b7355438b988608f52fca`.
`REQUIRED_OWNER_SHA256 = db8257ab2e693edf842ba8224792910eb77a32116bf61cd60290d6ca535c73bf`.
`BINDING_PRODUCER = FM build_operation_context using launcher CHECKOUT_HEAD/CHECKOUT_TREE`.
`BINDING_CONSUMER = GQ materializer plus GP/FM preauthorization validators`.
`PREAUTHORIZATION_VALIDATOR = prove_guest_fresh_operation_context_owner_binding`.
`DEPENDENT_CONTEXT_OR_CHECKOUT_ARTIFACTS = future post-HI context, candidate launcher extension binding, runtime projection, and future DU/EB/EE receipts`.
`DEPENDENT_PROOF_SET = HI owner matrix, HG projection, FM checkout/context, WRONG_INPUT firewall, and post-HI live-binding readiness`.

The production change is exactly:

```python
CHECKOUT_HEAD = "842a0f2cccd53222d11daa698bdeab17f0aac043"
CHECKOUT_TREE = "414a5f940e3b5027b6dd86c38d7a134f5c8ab0c4"
```

No dynamic alias, generic translator, fallback, multiple-owner list, HEAD
shortcut, authority input, or new route is introduced. The corrected launcher
candidate SHA-256 is
`e03b583c9aff4c54cce803ac41ccecba44f3d3a41f850ea0cda71eae4ea8c90e`.

## Focused binding negative matrix

| Case | Result | Boundary |
|---|---|---|
| exact committed HG owner | VERIFIED | existing FM preauthorization returns PASS with byte/hash identity |
| stale pre-HG owner | VERIFIED | rejected by exact owner identity mismatch |
| arbitrary wrong owner bytes | VERIFIED | rejected by exact owner identity mismatch |
| missing checkout owner | VERIFIED | rejected as absent/unsafe |
| malformed context owner identity | VERIFIED | rejected by SHA-256 schema validation |
| wrong well-formed context owner identity | VERIFIED | rejected by immutable binding validation |
| missing context owner binding | VERIFIED | rejected by immutable binding validation |
| duplicate/multiple owner key | VERIFIED | structurally rejected by duplicate-key JSON loader |
| candidate/runtime owner substitution | VERIFIED | candidate identity and checkout owner occupy separate exact bindings; candidate mutation rejects |
| authority expansion | VERIFIED | none exists in correction or focused proof |
| operation expansion | VERIFIED | no operational entry point invoked; production call-site count unchanged |
| unrelated semantic fields | VERIFIED | production diff changes only two checkout identity constants |

`CURRENT_HG_OWNER_ACCEPTANCE_STATUS = VERIFIED`.
`STALE_OWNER_REJECTION_STATUS = VERIFIED`.
`WRONG_OWNER_REJECTION_STATUS = VERIFIED`.
`MISSING_OWNER_REJECTION_STATUS = VERIFIED`.
`MALFORMED_OWNER_REJECTION_STATUS = VERIFIED`.
`AMBIGUOUS_OWNER_REJECTION_STATUS = VERIFIED`.
`RUNTIME_PROJECTION_OWNER_EQUIVALENCE_STATUS = VERIFIED`.
`AUTHORITY_NON_EXPANSION_STATUS = VERIFIED`.
`OPERATION_NON_EXPANSION_STATUS = VERIFIED`.
`UNRELATED_FIELD_PRESERVATION_STATUS = VERIFIED`.
`HH_FAILURE_CLASS_STATIC_BLOCK_STATUS = VERIFIED`.

## HG projection preservation

The existing HG matrix passed 10/10 inside the 31-case
checkout/projection run. Exact guest view `/mnt/aigol` continues to select the
sealed host identity without rewriting supplied argv. Wrong view, missing or
ambiguous projection, host-path mutation, and non-path argv mutation remain
fail closed.

`HG_PROJECTION_CORRECTION_PRESERVATION_STATUS = VERIFIED`.
`HOST_CANONICAL_BINDING_STATUS = VERIFIED`.
`GUEST_PROJECTION_BINDING_STATUS = VERIFIED`.
`PROJECTION_EQUIVALENCE_STATUS = VERIFIED`.
`HOST_BINDING_PRESERVATION_STATUS = VERIFIED`.
`UNAUTHORIZED_MUTATION_REJECTION_STATUS = VERIFIED`.

## WRONG_INPUT semantic firewall

The GY reducer remains byte-identical at
`8a6e6081118a2c1d305260555ba1ad5a11d97a5d66516f9810beb87c5c39fbf7`.
The preserved semantic contract is:

```text
CASE = E05_NEGATIVE_AUTHORITY_WRONG_INPUT
TARGET_MUTATION = input_identity
DEPENDENT_RECOMPUTATION = record_identity
SEMANTIC_MUTATION_COUNT = 1
EXPECTED_DIFFERING_FIELDS = input_identity, record_identity
```

`WRONG_INPUT_SEMANTIC_FIREWALL_STATUS = VERIFIED`.
`SAME_CLASS_REVIEW_STATUS = VERIFIED`.
`GY_REDUCER_SEMANTICS_STATUS = VERIFIED`.

## Incremental proof-impact analysis

`CHANGED_OWNER_SET = [FM_SOLE_LAUNCHER_CHECKOUT_HEAD_TREE_BINDING]`.

`DEPENDENT_PROOF_SET = [FM_CHECKOUT_HEAD_TREE, FM_CHECKOUT_CONTEXT_OWNER_BYTES, FUTURE_CANDIDATE_LAUNCHER_HASH_BINDING, FUTURE_CONTEXT, FUTURE_RUNTIME_PROJECTION, FUTURE_DU_EB_EE, POST_HI_READINESS]`.

`INVALIDATED_PROOF_FRONTIER = [PRE_HG_CURRENT_CHECKOUT_BINDING, CURRENT_WORKTREE_REBUILD_OF_PREDECESSOR_STATIC_CONTEXTS, FUTURE_POST_HI_CANDIDATE_AND_RECEIPTS]`.

`REVALIDATED_PROOF_SET = [HI_FOCUSED_12, CURRENT_CHECKOUT_AND_HG_PROJECTION_31, GY_HA_APPLICABLE_29, HH_APPLICABLE_HISTORICAL_4, GOVERNANCE_9, GOVERNANCE_ENGINE_20, EX_12, LAYER0_1]`.

`REUSED_UNCHANGED_PROOF_SET = [HH_COMMITTED_CANDIDATE_AND_RUNTIME_BYTES, HH_COMMITTED_DU_EB_EE_RECEIPTS, HG_PROJECTION_OWNER, GY_REDUCER_AND_HA_ADAPTER, GP_GQ_GT_CHECKOUT_OWNERS, P11_CHE_FK, EX_17_OF_17]`.

| Proof family | Classification | Reason |
|---|---|---|
| HI focused binding matrix | `REQUIRED_REVALIDATION` | exact corrected edge |
| HG, GP, GQ, GT | `REQUIRED_REVALIDATION` | checkout/projection preservation |
| applicable GY/HA | `REQUIRED_REVALIDATION` | semantic firewall and route preservation |
| applicable HH | `REQUIRED_REVALIDATION` | immutable Branch B evidence and preserved claims |
| governance, engine, Layer 0 | `REQUIRED_REVALIDATION` | constitutional closing checks |
| EX | `REUSED_BY_AUTHENTICATED_IDENTITY` plus validator rerun | owner unchanged; 12 regressions pass |
| HH DU/EB/EE receipts | `REUSED_BY_AUTHENTICATED_IDENTITY` | committed bytes unchanged; correction is after their HG candidate boundary |
| predecessor exact HEAD/static-rebuild tests | `HISTORICAL_NON_APPLICABLE` | intentionally bind GX/GZ/HG or stale launcher identities |
| future post-HI candidate/context/receipts | `HISTORICAL_NON_APPLICABLE` | cannot exist until a Human commit creates HI HEAD/tree |

`EX_REUSED = 17/17`.
`EX_RECONSTRUCTED = 0`.

`DU_STATUS = PASS__REUSED_COMMITTED_HH_CURRENT_HG_RECEIPT`.
`EB_STATUS = PASS__REUSED_COMMITTED_HH_CURRENT_HG_RECEIPT`.
`EE_STATUS = PASS__REUSED_COMMITTED_HH_CURRENT_HG_RECEIPT`.
`DU_EB_EE_IMPACT_CLASSIFICATION = UNCHANGED_HISTORICAL_HG_RECEIPTS_REUSED_BY_AUTHENTICATED_IDENTITY__FUTURE_POST_HI_RECEIPTS_REQUIRED_FOR_READINESS`.

# 3. Constitutional Self-Assessment

## Verified

- Exact committed HH entry and remote equality, stable ancestry, empty index,
  clean worktree, and nested authority pin.
- HH Branch B frontier, full stale owner identity, required HG owner identity,
  and correct preauthorization rejection.
- Minimum two-constant correction in the existing checkout-binding owner.
- Exact committed HG owner acceptance and the complete focused negative matrix.
- HG host/guest projection and GY WRONG_INPUT semantic firewall preservation.
- One launcher `main`, one QEMU subprocess call site, and one production route.
- No authority or operation, no historical evidence rewrite, and E05 7/18.
- Governance conformance, EX reuse, Layer 0 freeze, deterministic JSON, Python
  syntax, and diff integrity.

## Not proven

- A future committed HI HEAD/tree and launcher-identity candidate rebind.
- Future post-HI live context, runtime projection, or fresh DU/EB/EE receipts.
- `POST_COMMIT_LIVE_BINDING_STATUS`, `PREOPERATIONAL_READINESS_STATUS`, or
  `NEXT_OPERATIONAL_GENERATION_ELIGIBLE`.
- Any operational projection-aware or WRONG_INPUT capability, request, P11
  entry, denial, protected invocation/effect, or E05 credit.
- Provider-capacity, token, billable-cost, or global project scalar metrics for
  which no repository instrument exists.

## Capability and readiness boundary

| Metric | Classification | Evidence-bounded result |
|---|---|---|
| `CANDIDATE_CAPABILITY` | VERIFIED | HI repository candidate correction and focused proof |
| `CURRENT_HG_CHECKOUT_OWNER_BINDING_CANDIDATE_CAPABILITY` | VERIFIED | existing FM builder selects HG and focused preauthorization accepts exact owner |
| `CURRENT_HG_CHECKOUT_OWNER_BINDING_REPOSITORY_CAPABILITY` | VERIFIED | local repository-only materialization and negative matrix pass |
| `CURRENT_HG_CHECKOUT_OWNER_BINDING_OPERATIONAL_CAPABILITY` | NOT_PROVEN | zero operation |
| `PROJECTION_AWARE_VALIDATION_CANDIDATE_CAPABILITY` | VERIFIED | unchanged HG validator passes |
| `PROJECTION_AWARE_VALIDATION_REPOSITORY_CAPABILITY` | VERIFIED | HG matrix passes |
| `PROJECTION_AWARE_VALIDATION_OPERATIONAL_CAPABILITY` | NOT_PROVEN | zero operation |
| `WRONG_INPUT_CANDIDATE_CAPABILITY` | VERIFIED | unchanged exact semantic mutation remains reachable in repository code |
| `WRONG_INPUT_REPOSITORY_CAPABILITY` | VERIFIED | applicable GY/HA and HI firewall checks pass |
| `WRONG_INPUT_OPERATIONAL_CAPABILITY` | NOT_PROVEN | no request/P11/denial operation |
| `POST_COMMIT_LIVE_BINDING_STATUS` | NOT_PROVEN | future committed HI identity required |
| `PREOPERATIONAL_READINESS_STATUS` | NOT_PROVEN | future post-HI live binding required |
| `NEXT_OPERATIONAL_GENERATION_ELIGIBLE` | NOT_PROVEN | HI creates no authority or readiness certification |

`CANDIDATE_OBLIGATION != CONSTITUTIONAL_OBLIGATION`.
`CONSTITUTIONAL_OBLIGATION != SATISFIED`.
`SATISFIED != OPERATIONALLY_PROVEN`.

## Zero-operation and E05 accounting

```text
HUMAN_OPERATIONAL_AUTHORITY = 0
AUTHORITY_CONSUMPTION = 0
PRE = 0
FM_OPERATIONAL_LAUNCHER_INVOCATION = 0
QEMU = 0
VM_CREATION = 0
VM_BOOT = 0
OPERATION_ATTEMPT = 0
WRONG_INPUT_OPERATION = 0
REQUEST = 0
P11_ENTRY = 0
PROTECTED_INVOCATION = 0
PROTECTED_EFFECT = 0
RETRY = 0
REPAIR_AND_CONTINUE = 0
OPERATIONAL_REPLAY = 0
E05_CREDIT = 0
E05_BEFORE = 7/18
E05_AFTER = 7/18
E05_FRONTIER_DISTANCE = 11 obligations
```

## Project, development, cost, token, and worker metrics

| Metric | Classification | Evidence-bounded result |
|---|---|---|
| `PROJECT_PROGRESS_ESTIMATE` | ESTIMATED | narrow HH blocker statically closed; post-HI readiness remains |
| `CONSTITUTIONAL_HEALTH_EVIDENCE` | VERIFIED | 20/20 conformant, deterministic, fail-closed, zero warnings/violations |
| `SHADOW_AUTOMATION_STATUS` | VERIFIED | absent in changed surface |
| `CONSTITUTIONAL_FRONTIER_DISTANCE` | NOT_MEASURED | no scalar instrument |
| `E05_FRONTIER_DISTANCE` | VERIFIED | 11 obligations |
| `SELECTED_E05_LOCAL_FRONTIER_DISTANCE` | NOT_PROVEN | future post-HI binding/readiness and Human-authorized operation remain |
| `GOVERNANCE_EFFICIENCE` | ESTIMATED | targeted affected-frontier validation with explicit exclusions |
| `ARCHITECTURAL_GOVERNANCE_EFFICIENCE` | VERIFIED | two production lines; one route retained |
| `PROOF_REUSE_EFFICIENCE` | ESTIMATED | EX 17/17 and unchanged receipts/owners reused |
| `COGNITION_ASSISTED_HANDOFF` | VERIFIED | repository-authenticated continuation |
| `AIGOL_CODEX_WORK_SHARE` | NOT_MEASURED | no attribution instrument |
| `OVERENGINEERING_RISK` | ESTIMATED | low; no generic framework or new owner |
| `PROOF_PROCESS_OVERHEAD_RISK` | ESTIMATED | medium; proof surface materially exceeds two-line production delta |
| `COGNITION_PROVENANCE` | VERIFIED | repository bytes, Git object identities, commission scope, and deterministic tests |
| `SHADOW_DESIGN_TARGET` | NOT_APPLICABLE | no shadow route designed |
| `CONSTITUTIONAL_CONTINUATION_PROGRESS` | VERIFIED | HH Branch B blocker becomes statically blocked in HI candidate |
| `PROMPT_CONTEXT_REUSE_RATIO` | NOT_MEASURED | no token attribution instrument |
| `TOKEN_BENCHMARK` | NOT_MEASURED | provider capacity is not token count |
| `LLM_COST_REDUCTION_RATIO_LCRR` | NOT_MEASURED | no cost instrument |
| `E05_GENERATIONS_PER_CREDIT` | NOT_MEASURED | no governed generation-cost series instrument |
| `OPERATIONAL_ATTEMPTS_PER_CREDIT` | NOT_APPLICABLE | zero attempt and zero credit in HI |
| `NEW_INFRASTRUCTURE_PER_CREDIT` | NOT_APPLICABLE | zero credit; no new infrastructure |
| `NEW_CODE_PER_CREDIT` | NOT_APPLICABLE | zero credit |
| `NEW_PROOF_PER_CREDIT` | NOT_APPLICABLE | zero credit |
| `REUSED_PROOF_PER_CREDIT` | NOT_APPLICABLE | zero credit |
| `MARGINAL_E05_GENERATION_COST` | ESTIMATED | one bounded repository correction generation; no operational credit |
| `INFRASTRUCTURE_AMORTIZATION_SIGNAL` | ESTIMATED | positive reuse signal from existing owner/materializer/validators |
| `WORKERS_USED` | VERIFIED | 1 |
| `PROVIDER_CAPACITY_START` | NOT_MEASURED | no current-worker telemetry supplied |
| `PROVIDER_CAPACITY_END` | NOT_MEASURED | no current-worker telemetry supplied |
| `PROVIDER_CAPACITY_CONSUMED` | NOT_MEASURED | percentages are not inferred |
| `WALL_TIME` | NOT_MEASURED | no authoritative whole-generation instrument |
| `LLM_EXECUTION_EFFICIENCY` | NOT_MEASURED | no token/time attribution instrument |
| `REVALIDATION_CASE_COUNT` | VERIFIED | 118 executable checks before mechanical JSON/AST/diff checks |
| `NEW_CODE` | VERIFIED | 2 production lines changed; 309-line focused proof module added |
| `REUSED_CODE` | NOT_MEASURED | owners enumerated, line denominator not instrumented |
| `NEW_PROOF` | VERIFIED | HI focused matrix, sealed reduction, and this G48 |
| `REUSED_PROOF` | VERIFIED | HH/HG/GY/HA/GP/GQ/GT, governance, Layer 0, and EX identities |
| `REVALIDATED_PROOF` | VERIFIED | affected sets listed in the validation matrix |
| `RECONSTRUCTED_PROOF` | VERIFIED | EX 0; HH frontier reconstructed from committed evidence without reconstructing EX |

`CAPABILITY_REUSE != COMPUTE_COST_REDUCTION`.
`PROOF_REUSE != AUTOMATICALLY_LOW_LLM_COST`.

# 4. Validation Matrix

| Requirement | Evidence / command | Classification | Result |
|---|---|---|---|
| Exact HH entry, remote, ancestry | Git read-only identity checks and live `ls-remote` | `REQUIRED_REVALIDATION` | PASS |
| Nested authority | detached status, tag HEAD/tree, remote tag | `REQUIRED_REVALIDATION` | PASS |
| HH report/reduction/frontier | committed hashes and duplicate-free canonical reduction | `REQUIRED_REVALIDATION` | PASS |
| Exact HG/stale owner bytes | `git show <commit>:<owner> \| sha256sum` | `REQUIRED_REVALIDATION` | PASS |
| HI owner matrix | focused HI pytest | `REQUIRED_REVALIDATION` | 12/12 PASS |
| Checkout and projection | HG + GP + GQ + GT pytest | `REQUIRED_REVALIDATION` | 31/31 PASS |
| WRONG_INPUT firewall | applicable GY + HA pytest | `REQUIRED_REVALIDATION` | 29/29 PASS; 5 predecessor snapshots deselected |
| HH preserved evidence | applicable HH pytest | `REQUIRED_REVALIDATION` | 4/4 PASS; 4 pre-correction/current-HG execution snapshots deselected |
| DU/EB/EE receipts | committed HH hashes and terminal reduction | `REUSED_BY_AUTHENTICATED_IDENTITY` | PASS; future post-HI receipts deferred |
| P11/CHE/FK | unchanged owner hashes and GY/HA reachability | `REUSED_BY_AUTHENTICATED_IDENTITY` | PASS |
| Governance tests | `pytest tests/test_governance_conformance.py` | `REQUIRED_REVALIDATION` | 9/9 PASS |
| Governance engine | `python -m runtime.governance.governance_conformance_engine` | `REQUIRED_REVALIDATION` | 20/20 CONFORMANT; zero warnings/violations |
| EX | deterministic EX validator `--json` | `REUSED_BY_AUTHENTICATED_IDENTITY` plus rerun | 12/12 PASS; 17/17 reused; 0 reconstructed |
| Layer 0 | nested `python scripts/check_layer_freeze.py` | `REQUIRED_REVALIDATION` | PASS |
| Python syntax/AST | in-memory `compile` over production and focused proof | `REQUIRED_REVALIDATION` | 2/2 PASS |
| Canonical/duplicate-key validation | focused duplicate-owner case plus sealed reduction check | `REQUIRED_REVALIDATION` | PASS |
| One production route | AST count of launcher `main` and QEMU subprocess call | `REQUIRED_REVALIDATION` | 1/1 PASS |
| Diff whitespace | `git diff --check` | `REQUIRED_REVALIDATION` | PASS |
| Exact predecessor HEAD/static rebuilds | GX/GZ/HG-bound test nodes | `HISTORICAL_NON_APPLICABLE` | explicitly excluded, not reported as current pass/failure |
| FM operational launcher/QEMU/VM | prohibited by HI | `HISTORICAL_NON_APPLICABLE` | not invoked |
| Post-HI live binding/readiness | requires future Human commit | `HISTORICAL_NON_APPLICABLE` | not fabricated |

The exploratory combined predecessor run exposed only the explicitly classified
old-HEAD, old-launcher-hash, current-HEAD receipt-gate, and pre-correction
static-rebuild expectations. Targeted reruns passed every legally applicable
node. No historical file was edited to turn those snapshots into current proof.

# 5. Repository Mutation Summary

Modified production file:

- `.github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py` — two constants now bind exact HG
  HEAD/tree; no other production line changed.

New HI evidence:

- `.github/governance/evidence/g77_256hi_current_hg_checkout_owner_binding_v1/tests/test_g77_256hi_current_hg_checkout_owner_binding_v1.py` — repository-only
  positive/negative matrix and preserved semantic/route proof.
- `.github/governance/evidence/g77_256hi_current_hg_checkout_owner_binding_v1/G77_256HI_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json` — canonical sealed
  terminal reduction.
- `docs/governance/G77_256HI_CURRENT_HG_FM_CHECKOUT_OWNER_BINDING_CORRECTION_V1.md`
  — this six-heading G48 report.

Historical HF, HG, and HH evidence is unchanged. The FM context owner,
candidate/runtime artifacts, GY/HA, DU/EB/EE, P11/CHE/FK, EX, governance
runtime, nested authority, authorization, receipt, and operational evidence
surfaces are unchanged.

All HI changes remain unstaged. No `git add`, commit, push, reset, clean,
stash, restore, checkout, switch, or history rewrite was used. The index
remains empty. Human review is required.

# 6. Certification Verdict

Terminal branch: `BRANCH_A__STALE_BINDING_CORRECTION_VERIFIED`.

The exact committed HG owner was independently authenticated. The exact stale
pre-HG owner was independently reconstructed from the HH checkout commit. The
existing FM checkout-binding producer now selects immutable committed HG, and
the existing preauthorization consumer accepts its exact owner while rejecting
stale, wrong, missing, malformed, and ambiguous identities. HG projection and
GY WRONG_INPUT semantics remain intact, one production route remains, and the
HH failure class is statically blocked without authority or operation.

`CURRENT_HG_CHECKOUT_OWNER_BINDING_CANDIDATE_CAPABILITY = VERIFIED`.
`CURRENT_HG_CHECKOUT_OWNER_BINDING_REPOSITORY_CAPABILITY = VERIFIED`.
`CURRENT_HG_CHECKOUT_OWNER_BINDING_OPERATIONAL_CAPABILITY = NOT_PROVEN`.

`POST_COMMIT_LIVE_BINDING_STATUS = NOT_PROVEN`.
`PREOPERATIONAL_READINESS_STATUS = NOT_PROVEN`.
`NEXT_OPERATIONAL_GENERATION_ELIGIBLE = NOT_PROVEN`.

`MINIMUM_MISSING_CAPABILITY = POST_HI_COMMITTED_IDENTITY_LIVE_BINDING_AND_READINESS_REAUTHENTICATION`.

`MINIMUM_LEGAL_NEXT_DEVELOPMENT_DELTA = AFTER_HUMAN_COMMIT_ONLY__ONE_BOUNDED_REPOSITORY_ONLY_POST_HI_LIVE_BINDING_AND_READINESS_REAUTHENTICATION__NO_OPERATION`.

`E05_AFTER = 7/18`. `AUTO_CONTINUABLE = NO`.
`HUMAN_REVIEW_REQUIRED = YES`.

PASS__G77_256HI_CURRENT_HG_FM_CHECKOUT_OWNER_BINDING_CORRECTION_VERIFIED__POST_COMMIT_LIVE_BINDING_NOT_PROVEN__ZERO_OPERATION__E05_7_OF_18__HUMAN_REVIEW_REQUIRED
