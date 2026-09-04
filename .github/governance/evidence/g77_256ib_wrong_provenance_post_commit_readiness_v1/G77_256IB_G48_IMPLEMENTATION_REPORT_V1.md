# 1. Implementation Summary

G77-256IB completes one bounded, repository-only post-commit binding of the
already-certified IA `WRONG_PROVENANCE` route to exact committed IA identity.
The sole FM checkout owner now selects IA HEAD
`dfea5c58f400edb9472db37390de80a92eda2ad3` and TREE
`caf8feb24ed4c072dde6c6586fd7cf60d05c4c7d`. The existing IA cloud-init and
NoCloud projection bind the same pair. No Human authority, request, PRE,
operational FM invocation, QEMU process, VM, P11 entry, protected invocation,
protected effect, retry, repair retry, replay, or E05 credit occurred.

## Exact entry authentication

| Check | Authenticated value |
|---|---|
| worktree | `/home/pisarna/work/sapianta-fl` |
| branch | `g77-256fl-wrong-attempt-preboot-blocker` |
| HEAD | `dfea5c58f400edb9472db37390de80a92eda2ad3` |
| TREE | `caf8feb24ed4c072dde6c6586fd7cf60d05c4c7d` |
| subject | `G77-256IA extend single route for WRONG_PROVENANCE` |
| origin | `git@github.com:Aljosa3/sapianta-ecosystem.git` |
| remote branch HEAD | exact equality with local IA HEAD |
| entry worktree / index | clean / empty |
| ancestry | IA, HZ, HY, HX, HT, HV, HW, and stable anchor verified |
| nested origin | `git@github.com:Aljosa3/sapianta-core.git` |
| nested HEAD | `3183bab71f8f30397c0309dd2e6d846d14a11f66` |
| nested TREE | `7c32ec05efc2be43297849bc38ec8766514a523d` |
| nested state | clean, detached, immutable-tag pinned |

Committed IA G48, terminal reduction, adapter, and materializer were
authenticated from Git before rebind. Committed HZ specification, producer,
reducer, and terminal reduction were independently authenticated. IA proves
route support and repository/static binding for the exact four-vector set;
HZ proves the exact mutation and expected-denial semantics. The reconstructed
entry state is `E05_REQUIRED = 18`, `E05_SATISFIED = 9`, and
`E05_REMAINING = 9`.

`E05_BEFORE_IB = 9/18`, `E05_AFTER_IB = 9/18`, and `E05_CREDIT = 0`.

# 2. Code Evidence

## Checkout and bootstrap rebind

The existing FM checkout owner was changed in place from historical HT to
exact committed IA. No second checkout owner or route was created. IA's
existing cloud-init command was rebound to the same IA HEAD/TREE. Its NoCloud
image was regenerated from exactly:

- IA cloud-init user-data SHA-256
  `4725543bab299d1e153b2c40f9fcd0791ce9c2af318e88c41deeba9e6c69ed84`;
- unchanged FM meta-data SHA-256
  `081885fe7f51b064148db23dff5f4af40f58ae693879b5cb05fae24c8f23838a`;
- unchanged FM network-config SHA-256
  `639b6f419a9ac49312b218e12395dc7e7d623d96202c3315a92dcd19d6fa02ba`;
- `cloud-localds` with recorded `SOURCE_DATE_EPOCH=1788540000`;
- resulting NoCloud SHA-256
  `4154ec58b7ebf46299ccc495a0a1232b7e31f67221f987b6fe7959f8d5593c7c`.

`isoinfo` proves exact byte projection of all three canonical inputs. The IA
adapter hash remains
`e547af9b68f77fda94962abb6031445df5faba9ec43c68f40966473f83db8b23`.
The adapter continues to bind the exact committed HZ producer and reducer
hashes; neither HZ nor IA semantic code was rewritten.

The coherent chain is:

```text
committed IA HEAD/TREE
-> sole FM checkout
-> committed IA adapter
-> rebound IA cloud-init
-> regenerated IA NoCloud projection
-> existing guest consumer path
-> existing FM/GN constitutional route
```

## Current candidate, runtime projection, and context

The current canonical candidate and runtime projection are byte-identical at
SHA-256 `f399a9179054c1fee842a925dcc8be5f9799dee4cc28acb7c7c129ddd90d4ff5`.
The sealed context identity is
`651d58f1cc1701e334df65be023b58b74b40f05c6a2cb62f54a132aec564dda2`.
It binds committed IA repository identity, committed IA adapter identity,
current candidate identity, current bootstrap/NoCloud identity, the existing
canonical argv owner, an operation-scoped checkout under the transient root,
and no-network/zero-retry/zero-repair/zero-replay policy.

The HZ semantic firewall remains exact:

```text
INDEPENDENT_MUTATION_COUNT = 1
INDEPENDENT_MUTATED_COORDINATE = provenance_identity
DEPENDENT_RECOMPUTATION_COUNT = 1
DEPENDENT_RECOMPUTED_COORDINATE = record_identity
AUTHORITATIVE_PROVENANCE = existing protected custody owner-state
EXPECTED_DENIAL_REASON = operational Human act input_record_identity binding is invalid
PROVENANCE_SPECIFIC_COMPARISON_REACHED = false
```

The existing GN owner and IA materializer validate the deterministic
candidate/context/canonical-argv presentation binding. This is readiness
evidence only: `PRESENTATION_BINDING != HUMAN_AUTHORIZATION`. No presentation
was delivered to a Human and no live grant was created.

## DU / EB / EE and negative matrix

The existing DU, EB, and EE owners validate the current IA-bound candidate and
runtime projection. No vector-specific substitute was created.

The preauthorization matrix rejects wrong/unknown/malformed/cross-vector
values and substitutions of candidate, context, adapter, checkout HEAD,
checkout TREE, cloud-init, NoCloud projection, canonical argv, presentation,
historical HT identity, HZ producer, HZ reducer, missing provenance owner,
conflicting provenance owner, runtime projection, DU, EB, and EE. Every case
fails before operation; operational FM `main()` is never invoked.

The explicitly tested historical failure set is:

- GE/GF pre-commit or future-commit self-reference;
- HU/HV stale guest checkout;
- GS/GT checkout destination and transient-root lifecycle;
- HF/HG/HH/HI/HJ/HK/HN harness, adapter, bootstrap, checkout, and identity drift.

No claim is made for unrelated historical failure classes.

## Supported-vector and route proof

The sole context owner and the exact IA checkout both accept exactly
`WRONG_ATTEMPT`, `WRONG_INPUT`, `WRONG_CONTRACT`, and `WRONG_PROVENANCE`.
Unknown, empty, lowercase, alias, and malformed forms fail closed. AST
inspection proves one top-level FM `main()` and no IB launcher or operational
entry point.

```text
SUPPORTED_VECTOR_SET = [WRONG_ATTEMPT, WRONG_INPUT, WRONG_CONTRACT, WRONG_PROVENANCE]
PRODUCTION_ROUTE_BEFORE = 1
PRODUCTION_ROUTE_AFTER = 1
PRODUCTION_ROUTE_DELTA = 0
NEW_PRODUCTION_ROUTE_COUNT = 0
NEW_RUNTIME_OWNER_COUNT = 0
NEW_AUTHORITY_LAYER_COUNT = 0
NEW_GENERIC_FRAMEWORK_COUNT = 0
EX_REUSED = 17/17
EX_RECONSTRUCTED = 0
```

## Reuse Impact Assessment

1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo? HZ
   WRONG_PROVENANCE capability, IA route support, HT single route, HV checkout
   correction pattern, HW readiness pattern, HX operational architecture, FM,
   GN/GL, DU/EB/EE, P11/CHE/FK, EX 17/17, governance, and Layer 0.
2. Katere nove zmogljivosti (če sploh) nastanejo? Only current committed-IA
   live-binding and repository-only preoperational-readiness evidence.
3. Ali katera obstoječa zmogljivost postane nedosegljiva? Ne; the set is empty.
4. Ali implementacija ustvarja vzporedni tok? Ne.
5. Ali zmanjšuje ali povečuje število produkcijskih poti? Ne; one remains one.

```text
REUSED_CERTIFIED_CAPABILITY_SET = [HZ, IA, HT, HV, HW, HX, FM, GN, GL, DU, EB, EE, P11, CHE, FK, EX_17_OF_17, GOVERNANCE, LAYER_0]
NEW_CAPABILITY_SET = [IB_CURRENT_COMMITTED_IA_LIVE_BINDING_AND_PREOPERATIONAL_READINESS_EVIDENCE]
UNREACHABLE_PREEXISTING_CAPABILITY_SET = []
```

# 3. Constitutional Self-Assessment

IB preserves `CERTIFIED != AUTHORIZED`, `REPOSITORY_CAPABILITY !=
ROUTE_SUPPORT`, `ROUTE_SUPPORT != LIVE_BINDING`, `STATIC_BINDING !=
CURRENT_COMMITTED_BINDING`, `BOUND != READY`, `READY != AUTHORIZED`,
`AUTHORIZED != OPERATED`, `EXPECTED_DENIAL != OBSERVED_DENIAL`, `REQUEST !=
AUTHORIZATION`, and `REQUEST != ENTRY != INVOCATION != EFFECT`. Provider
capability is not execution authority. The protected boundary remains
unentered.

## Infrastructure Amortization

| Measurement | Result |
|---|---|
| DID_IB_REQUIRE_NEW_COMMON_INFRASTRUCTURE? | NO |
| DID_IB_REQUIRE_NEW_VECTOR_SPECIFIC_INFRASTRUCTURE? | YES — IB evidence only |
| DID_IB_REQUIRE_NEW_GENERIC_FRAMEWORK? | NO |
| DID_IB_REQUIRE_NEW_AUTHORITY_LAYER? | NO |
| DID_IB_REQUIRE_NEW_RUNTIME_OWNER? | NO |
| DID_IB_REQUIRE_NEW_PRODUCTION_ROUTE? | NO |
| DID_IB_REQUIRE_P11_CORE_CHANGE? | NO |
| DID_IB_REUSE_HZ_REPOSITORY_CAPABILITY? | YES |
| DID_IB_REUSE_IA_ROUTE_SUPPORT? | YES |
| DID_IB_REUSE_HT_SINGLE_ROUTE? | YES |
| DID_IB_REUSE_HV_POST_COMMIT_CHECKOUT_PATTERN? | YES |
| DID_IB_REUSE_HW_READINESS_PATTERN? | YES |
| DID_IB_REUSE_HX_OPERATIONAL_ARCHITECTURE? | YES |
| DID_IB_REUSE_FM_GN_GL? | YES |
| DID_IB_REUSE_DU_EB_EE? | YES |
| DID_IB_REUSE_P11_CHE_FK? | YES |
| DID_IB_REUSE_EX_17_OF_17? | YES |
| GENERATIONS_SINCE_E05_9_OF_18 | VERIFIED — 4 (HY, HZ, IA, IB) |
| E05_CREDITS_SINCE_9_OF_18 | VERIFIED — 0 |
| OPERATIONAL_ATTEMPTS_SINCE_E05_9_OF_18 | VERIFIED — 0 |
| NEW_CERTIFIED_COMPONENTS_SINCE_E05_9_OF_18 | VERIFIED — committed HZ and IA components; IB awaits review |
| REUSED_CERTIFIED_COMPONENTS_SINCE_E05_9_OF_18 | NOT_MEASURED — no governed denominator |
| MARGINAL_NEW_INFRASTRUCTURE_PER_E05_CREDIT | NOT_MEASURED — zero-new-credit denominator |
| INFRASTRUCTURE_AMORTIZATION_SIGNAL | ESTIMATED — positive reuse signal |

```text
E05_GENERATIONS_PER_CREDIT = NOT_MEASURED__ZERO_NEW_CREDIT_DENOMINATOR
OPERATIONAL_ATTEMPTS_PER_CREDIT = NOT_MEASURED__ZERO_NEW_CREDIT_DENOMINATOR
```

No LLM cost reduction is inferred from reuse.

## CCWIM

| Metric | Status | Result |
|---|---|---|
| CCWIM_MATURITY_LEVEL | ESTIMATED | L4-like; no L5 claim |
| CROSS_WORKER_STATE_RECOVERY_LEVEL | VERIFIED | repository-authenticated |
| REPOSITORY_DERIVED_CONTEXT_RATIO | ESTIMATED | dominant |
| HUMAN_HANDOFF_INFORMATION_REQUIRED | VERIFIED | checkpoint, scope, prohibitions, locators |
| PREVIOUS_WORKER_CONVERSATION_REQUIRED | VERIFIED | NO |
| PREVIOUS_WORKER_IDENTITY_REQUIRED | VERIFIED | NO |
| PREVIOUS_WORKER_MEMORY_REQUIRED | VERIFIED | NO |
| AUTHENTICATED_REPOSITORY_CONTINUATION | VERIFIED | YES |
| INTER_GENERATION_CROSS_WORKER_CONTINUATION | VERIFIED | IA to IB |
| INTRA_GENERATION_CROSS_WORKER_CONTINUATION | NOT_APPLICABLE | no worker transition |
| UNCOMMITTED_DELTA_RECOVERY | NOT_APPLICABLE | clean entry |
| AUTHORITY_STATE_RECOVERY | NOT_APPLICABLE | no authority exists |
| CROSS_WORKER_CONSTITUTIONAL_DRIFT | VERIFIED | 0 |
| HANDOFF_SUFFICIENCY_STATUS | VERIFIED | sufficient |
| HANDOFF_STATE_COMPLETENESS | VERIFIED | complete for bounded scope |
| HANDOFF_RECONSTRUCTION_REQUIRED | VERIFIED | YES |
| HANDOFF_RECONSTRUCTION_SUCCESS | VERIFIED | YES |
| HANDOFF_AMBIGUITY_COUNT | VERIFIED | 0 |
| UNAUTHENTICATED_HANDOFF_ASSUMPTION_COUNT | VERIFIED | 0 |

## Required metrics

| Metric | Status | Result |
|---|---|---|
| PROJECT_PROGRESS_ESTIMATE | ESTIMATED | WRONG_PROVENANCE preoperational readiness complete; no total-project percentage |
| CONSTITUTIONAL_HEALTH_EVIDENCE | VERIFIED | fail-closed, one route, zero operation |
| SHADOW_AUTOMATION_STATUS | VERIFIED | absent |
| CONSTITUTIONAL_FRONTIER_DISTANCE | ESTIMATED | one separately authorized operational generation |
| E05_FRONTIER_DISTANCE | VERIFIED | 9 of 18 remain |
| SELECTED_E05_LOCAL_FRONTIER_DISTANCE | ESTIMATED | one future Human-authorized operational generation |
| GOVERNANCE_EFFICIENCE | ESTIMATED | targeted affected frontier |
| ARCHITECTURAL_GOVERNANCE_EFFICIENCE | VERIFIED | one route retained |
| PROOF_REUSE_EFFICIENCY | VERIFIED | EX 17/17 reused |
| COGNITION_ASSISTED_HANDOFF | VERIFIED | replay-safe repository continuation |
| AIGOL_CODEX_WORK_SHARE | NOT_MEASURED | no governed attribution instrument |
| OVERENGINEERING_RISK | ESTIMATED | low |
| PROOF_PROCESS_OVERHEAD_RISK | ESTIMATED | moderate |
| COGNITION_PROVENANCE | VERIFIED | authenticated repository primary |
| CANDIDATE_CAPABILITY | VERIFIED | exact HZ semantics projected |
| WRONG_PROVENANCE_CANDIDATE_CAPABILITY | VERIFIED | current candidate |
| WRONG_PROVENANCE_REPOSITORY_CAPABILITY | VERIFIED | committed HZ + IA |
| WRONG_PROVENANCE_ROUTE_SUPPORT | VERIFIED | existing FM/GN route |
| WRONG_PROVENANCE_BINDING_STATUS | VERIFIED | current committed IA live binding |
| WRONG_PROVENANCE_PREOPERATIONAL_READINESS | VERIFIED | repository-only chain |
| WRONG_PROVENANCE_OPERATIONAL_CAPABILITY | NOT_PROVEN | zero operation |
| SHADOW_DESIGN_TARGET | VERIFIED | FORMALIZE / REUSE / BIND / VERIFY / STOP |
| CONSTITUTIONAL_CONTINUATION_PROGRESS | VERIFIED | readiness verified |
| PROMPT_CONTEXT_REUSE_RATIO | NOT_MEASURED | no formal token instrument |
| TOKEN_BENCHMARK | NOT_MEASURED | telemetry excluded |
| LLM_COST_REDUCTION_RATIO | NOT_MEASURED | no governed cost baseline |
| LCRR | NOT_MEASURED | no governed cost baseline |
| E05_GENERATIONS_PER_CREDIT | NOT_MEASURED | zero-new-credit denominator |
| OPERATIONAL_ATTEMPTS_PER_CREDIT | NOT_MEASURED | zero-new-credit denominator |
| MARGINAL_E05_GENERATION_COST | NOT_MEASURED | no governed cost instrument |
| MARGINAL_NEW_INFRASTRUCTURE_PER_E05_CREDIT | NOT_MEASURED | zero-new-credit denominator |
| INFRASTRUCTURE_AMORTIZATION_SIGNAL | ESTIMATED | positive reuse signal |
| EXPECTED_NEXT_CREDIT_GENERATION_COUNT | ESTIMATED | at least one separately authorized operational generation |

## Cognition Provenance

`COGNITION_PROVENANCE = VERIFIED` derives from authenticated Git; committed
IA/HZ/HY/HX and HT/HV/HW; P11/CHE/FK; EX; FM; GN/GL; DU/EB/EE; the IA
adapter/materializer/bootstrap; HZ producer/reducer; governance; Layer 0; and
the pinned nested authority. Previous-worker conversation, identity, and
memory are not evidence.

# 4. Validation Matrix

| Validation | Current result |
|---|---|
| exact IA HEAD/TREE/subject/origin/branch and local/remote equality | PASS |
| clean entry/index; terminal index empty | PASS |
| IA/HZ/HY/HX/HT/HV/HW/stable-anchor ancestry | PASS |
| nested authority clean/detached/tag-pinned | PASS |
| committed IA/HZ object authentication and seals | PASS |
| E05 reconstruction | PASS — 9/18, zero IB credit |
| checkout/bootstrap/NoCloud exact IA binding | PASS |
| candidate/runtime/context/presentation chain | PASS |
| DU / EB / EE | PASS / PASS / PASS |
| IB focused negative and historical firewall | PASS — 39/39 |
| committed IA/HZ current-applicable regression | PASS — 45/45; 3 historical snapshot assertions deselected |
| GN/GL affected regression | PASS — 52/52 |
| four-vector non-regression; unknown/malformed rejection | PASS |
| P11/CHE/FK affected regression | PASS — 33/33 |
| EX current validation | PASS — 12/12; 17/17 reused, 0 reconstructed |
| governance tests and conformance engine | PASS — 9/9; engine 20/20, CONFORMANT, zero warnings/violations |
| Layer 0 affected checks | PASS through conformance validation |
| canonical JSON / duplicate-key rejection / seals | PASS |
| Python syntax / AST / single-route count | PASS |
| G48 exact six top-level headings | PASS |
| `git diff --check` | PASS |

Validation invokes no operational FM `main()`, PRE, QEMU, VM, Human request,
P11 entry, protected invocation, or protected effect. Historical snapshot
assertions are reported separately when they are intentionally superseded by
the current IA checkout binding; historical artifacts remain unmodified.

# 5. Repository Mutation Summary

Modified canonical owners/assets:

- sole FM launcher: checkout HEAD/TREE and IA bootstrap hashes only;
- existing IA cloud-init: historical HT HEAD/TREE to committed IA HEAD/TREE;
- existing IA NoCloud image: regenerated projection of the rebound source.

Created IB repository-only evidence:

- post-IA binding/reduction owner;
- current candidate and byte-identical runtime projection;
- sealed current operation context;
- EB and EE receipts plus non-executable EE path fixture;
- focused tests;
- canonical sealed terminal reduction;
- this exact-six-heading G48 report.

No IA/HZ/HY/HX semantic evidence, P11 core, nested authority, or
historical/composite worktree was changed. No add, commit, or push occurred;
all IB changes remain unstaged.

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
E05_BEFORE_IB = 9/18
E05_AFTER_IB = 9/18
```

# 6. Certification Verdict

```text
CURRENT_E05_STATUS = 9/18
CURRENT_IA_COMMIT_IDENTITY_STATUS = VERIFIED
POST_COMMIT_LIVE_BINDING_STATUS = VERIFIED
CURRENT_WRONG_PROVENANCE_CANDIDATE_STATUS = VERIFIED
CURRENT_RUNTIME_PROJECTION_STATUS = VERIFIED
CURRENT_OPERATION_CONTEXT_STATUS = VERIFIED
GN_PRESENTATION_BINDING_STATUS = VERIFIED
CURRENT_DU_STATUS = PASS
CURRENT_EB_STATUS = PASS
CURRENT_EE_STATUS = PASS
PREAUTHORIZATION_NEGATIVE_MATRIX_STATUS = VERIFIED
KNOWN_HISTORICAL_FAILURE_CLASS_BLOCK_STATUS = VERIFIED__GE_GF__HU_HV__GS_GT__HF_HG_HH_HI_HJ_HK_HN
PREOPERATIONAL_READINESS_STATUS = VERIFIED
NEXT_OPERATIONAL_GENERATION_ELIGIBLE = VERIFIED

WRONG_PROVENANCE_FORMALIZATION_STATUS = VERIFIED
WRONG_PROVENANCE_REPOSITORY_CAPABILITY = VERIFIED
WRONG_PROVENANCE_ROUTE_SUPPORT = VERIFIED
WRONG_PROVENANCE_BINDING_STATUS = VERIFIED__CURRENT_COMMITTED_IA_LIVE_BINDING
WRONG_PROVENANCE_PREOPERATIONAL_READINESS = VERIFIED
WRONG_PROVENANCE_OPERATIONAL_CAPABILITY = NOT_PROVEN

SUPPORTED_VECTOR_SET = [WRONG_ATTEMPT, WRONG_INPUT, WRONG_CONTRACT, WRONG_PROVENANCE]
PRODUCTION_ROUTE_BEFORE = 1
PRODUCTION_ROUTE_AFTER = 1
PRODUCTION_ROUTE_DELTA = 0
POST_IB_COMMIT_REBIND_REQUIRED = NOT_APPLICABLE

LAST_VERIFIED_EDGE = CURRENT_COMMITTED_IA_WRONG_PROVENANCE_CANDIDATE_RUNTIME_CONTEXT_PRESENTATION_DU_EB_EE_PREAUTHORIZATION_CHAIN
FIRST_BROKEN_EDGE = NONE_KNOWN_IN_REPOSITORY_PREAUTHORIZATION_SCOPE
MINIMUM_MISSING_CAPABILITY = ONE_FRESH_SEPARATELY_HUMAN_AUTHORIZED_WRONG_PROVENANCE_OPERATIONAL_GENERATION
MINIMUM_LEGAL_NEXT_DELTA = AFTER_IB_HUMAN_REVIEW_AND_COMMIT_ONLY__ONE_SEPARATELY_COMMISSIONED_OPERATIONAL_GENERATION__FRESH_HUMAN_AUTHORITY_REQUIRED

EX_REUSED = 17/17
EX_RECONSTRUCTED = 0
NEW_GENERIC_FRAMEWORK_COUNT = 0
NEW_AUTHORITY_LAYER_COUNT = 0
NEW_PRODUCTION_ROUTE_COUNT = 0
NEW_RUNTIME_OWNER_COUNT = 0

AUTO_CONTINUABLE = NO
HUMAN_AUTHORIZATION_REQUIRED = NO
HUMAN_REVIEW_REQUIRED = YES
```

Verdict:
`VERIFIED__IB_POST_IA_WRONG_PROVENANCE_PREOPERATIONAL_READINESS__ONE_ROUTE_PRESERVED__OPERATIONAL_CAPABILITY_NOT_PROVEN__ZERO_OPERATION__E05_REMAINS_9_OF_18__HUMAN_REVIEW_REQUIRED`.
