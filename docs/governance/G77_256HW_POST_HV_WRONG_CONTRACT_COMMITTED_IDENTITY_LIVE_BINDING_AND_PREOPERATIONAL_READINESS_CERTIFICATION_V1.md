# 1. Implementation Summary

Status: repository-only G77-256HW certification for the committed G77-256HV
checkpoint. Implementation contracts: SPCE; G48 Constitutional Evidence
Reporting Standard V1; committed HV, HU, HT, and HR; the existing FM/GN/HG
architecture; DU/EB/EE; EX; P11/CHE/FK; Layer 0; and the pinned nested
constitutional authority.

The authenticated entry checkpoint is branch
`g77-256fl-wrong-attempt-preboot-blocker`, HEAD
`737ef550f02f6b65a7dd0d4e1ac5bc118599b32b`, tree
`212a36d807663b5c60927355bfb9fe1184bfc27c`, subject
`G77-256HV correct WRONG_CONTRACT guest checkout binding`, with live remote
branch equality to that HEAD and origin
`git@github.com:Aljosa3/sapianta-ecosystem.git`. The tracked entry worktree was
clean and the index empty. HU, HT, HR, and stable anchor ancestry are present.
The nested authority is clean, detached, and pinned at HEAD
`3183bab71f8f30397c0309dd2e6d846d14a11f66`, tree
`7c32ec05efc2be43297849bc38ec8766514a523d`, immutable tag
`sapianta-system-nested-authority-3183bab-v1`, and required origin.

HV terminal truth was reconstructed from committed Git bytes. It selects HT as
the first lineage commit with WRONG_CONTRACT FM-context support and the complete
guest dependency set:

```text
SELECTED_CHECKOUT_HEAD = af44f0afd02be7e21a24e962309e28f6edd17ae0
SELECTED_CHECKOUT_TREE = fc949a2bbaa0a507edbc25811563dc5e13d18315
SELECTION_REASON = HT_IS_THE_FIRST_LINEAGE_COMMIT_WITH_WRONG_CONTRACT_FM_CONTEXT_SUPPORT_AND_CONTAINS_THE_COMPLETE_GUEST_DEPENDENCY_SET
```

The committed HV correction is sufficient. The sole FM route and the
WRONG_CONTRACT bootstrap both bind HT. The NoCloud image is the byte-exact
projection of committed user-data, metadata, and network-config. The expected
harness recomputes to the committed adapter SHA-256
`bb9c917947d317319c9502e44c2d5dca6d423380e67f71a14db1b63eb11acc34`.
Host and selected guest checkout semantics agree for WRONG_ATTEMPT,
WRONG_INPUT, and WRONG_CONTRACT and fail closed for UNKNOWN and MALFORMED.

HW constructed one current candidate, identical runtime projection, sealed
readiness-only operation context, and fresh DU/EB/EE evidence. It created no
Human authority, operational request, or operational execution state.

```text
CURRENT_HV_COMMIT_IDENTITY_STATUS = VERIFIED
COMMITTED_FM_CHECKOUT_BINDING_STATUS = VERIFIED
COMMITTED_WRONG_CONTRACT_BOOTSTRAP_HEAD_TREE_STATUS = VERIFIED
COMMITTED_CHECKOUT_BOOTSTRAP_COHERENCE_STATUS = VERIFIED
COMMITTED_NOCLOUD_PROJECTION_STATUS = VERIFIED
EXPECTED_HARNESS_BINDING_STATUS = VERIFIED
HOST_GUEST_CONTEXT_VECTOR_SEMANTIC_EQUIVALENCE = VERIFIED
POST_COMMIT_LIVE_BINDING_STATUS = VERIFIED
```

# 2. Code Evidence

## Committed identity map

Every row was recomputed from `HV_HEAD:path`; worktree bytes were required to
match the committed object. Status is `VERIFIED` for every row.

| Identity / role | Git blob | SHA-256 |
|---|---|---|
| HV terminal reduction / terminal truth | `870e2c85c9d5ccaf69f7e7a329e81644fc3abf1c` | `112c99cdaf34e428f463139615557a23f72f96b3b615bedd040a6a0efeb3c08b` |
| HV G48 report / correction report | `af05c736c6c8ce21b655779cc711735e3a6efa03` | `c5c7a7a4045d463cff217b7e29dc6c3662279d58afbfdf3972881e5d7b13e4c3` |
| HV auditor / committed correction audit | `de5f745aa9cfd029ac53daeae9d8db616361587f` | `94b8cfa00590ed0e03261205d424759a623934f42e371fc80a0aafa90e330582` |
| HV reducer / terminal owner | `0d3504e87c78bb69fee0d758223c26468c59e506` | `b032939cdbe36f8efd53bcc87f6ef7325c561f9519d980cd12b529525d82d9bd` |
| FM context / operation-context owner | `282ea1d33d5c85d8ecb032d09a14a5b2f95885a7` | `3c24621ec9f0bd67e5e3468d728446069f54628f4150ee02b677a973f24972e4` |
| FM launcher / sole runtime and checkout owner | `e78458c5e60352ccfa1dcda6d6901fc3de097a27` | `614eb3ec76ef02aff1f47e0131b32da572de76173628e4de715ac0e83f3af76f` |
| GN / presentation owner | `edeb4ad23fa31dee5a6f9dce76193c0a50d26021` | `3d75bffb2f1e1302e2dfa7724b90403b93491419a40a002bdc59b2d2166a0ff6` |
| HT / WRONG_CONTRACT adapter | `a66b65a9940df7cd0b017fb74b7ee4658d99a765` | `bb9c917947d317319c9502e44c2d5dca6d423380e67f71a14db1b63eb11acc34` |
| HT / preauthorization coherence owner | `027a58f98ebe86c7384deb557bc82156690097ec` | `e1d02ae699c03e215400d87fe82fda2bfa09c8bf20333bec8f4c1af5bd8a58ba` |
| HT / cloud-init user-data | `1512668906a6a6e881244e1b230dcb155e1b36b8` | `c3f7f93a55f2c3a76fe73bccb9aa0b54fed2f5011c326c0f8774a8ca72c7442f` |
| HT / NoCloud seed | `32518d19fbd6d908c66263477140b99dd8bd4c4d` | `fc98a62a1b3bd813b7f570438fc48151c378aeba4389de13d4e532d3f7979b21` |
| HG / checkout-projection owner | `617fa8370200d7fef96f4c0955eb8fbed11a7803` | `d6e2366481ae01910b281775e5437506b6baef719a57e53a1e109e7d1ea0d141` |
| P11 / D2 custody owner | `d605c107359fbcf45a92ec1bf79468714d1045c5` | `ffd663e68b0efcb1c960bc513a7911372ab06d07971aea071e98f502764ffd9c` |
| HR / formal specification | `7cc60a76e97877159fc7e00677ab1a29e8181220` | `d0edaf1d9cbc384822ed3bf5184810341e4e127aa5f76c77cb392e9d72749b07` |
| HR / producer | `4f11ab683918fd04a0e6e76b8ee142786c8434be` | `3a8e6a0bed06d748b9df50bec7aaeb93c059ec36214c997c8675a488c46d27c5` |
| HR / reducer | `d108701ba8c2cac1d4d93de74401caf984ca4e17` | `0a59c9b5a501864ac8e6cac2f12f0ab317f0fcb54222b1783067b720ce4db3ae` |
| DU / manifest validator | `44b7138dcad33a70ab63f7b988857d04519986f6` | `27457993a4e6b778cc65356cd9b17a1bf2665f4e6147608d27dc233ff512304d` |
| EB / candidate receipt validator | `556f8576417b64b7ce4e8802045acce7b784709d` | `8e8171f757213f064cec463868408364175772e766615bd276ed7f0e28306b43` |
| EE / runtime binding validator | `4b67f5ea6260cdf24b1d0084ecaf6eebd5e49fd5` | `5e4b35b3c7e7e23e5b7209c5f56e8a70055eac9a3deef32bc288b210e80f9410` |
| EX / common certificate | `7d47e26712e5f183060c0764d433ac2a29bccd63` | `91c477171147c56516c0f473ab887c12173c4bab225f2733c274b32467824b2f` |

## Current chain

The current candidate and runtime projection are byte-identical with SHA-256
`ef7f28dd1a48a56b47d12003f159f665f55b390b4540eea0fe5b591b7da13cd8`.
The sealed context identity is
`ec00773f1a954238c5d5790a64e875c1b904310d4b1ea844d3ce7cafb0483791`;
its file SHA-256 is
`ebedd8704d20cf563de1dca95c7178a3d5d35cfcf1bf8df6e7745fe0623566d2`.
It binds committed HV HEAD/tree, HT checkout HEAD/tree, FM launcher and context
owner, HT adapter/bootstrap/seed, and current candidate and canonical argv.

The HR producer recomputed the candidate payload with exactly:

```text
TARGET_MUTATION = contract_identity
SEMANTIC_MUTATION_COUNT = 1
DEPENDENT_RECOMPUTATION = record_identity
UNRELATED_MUTATION_COUNT = 0
EXPECTED_P11_DENIAL = D2 input_record_identity binding failure
CONTRACT_SPECIFIC_COMPARISON_REACHED = false
```

No Human act field was changed to force a later comparison. WRONG_CONTRACT was
not relabeled as WRONG_INPUT. The GN/HT preauthorization validator proved the
candidate/context/argv/presentation tuple without producing an authorization
or operational request.

```text
CURRENT_WRONG_CONTRACT_CANDIDATE_STATUS = VERIFIED
CURRENT_CANDIDATE_IDENTITY = ef7f28dd1a48a56b47d12003f159f665f55b390b4540eea0fe5b591b7da13cd8
CURRENT_CANDIDATE_SEMANTIC_FIREWALL_STATUS = VERIFIED
CURRENT_RUNTIME_PROJECTION_STATUS = VERIFIED
CURRENT_OPERATION_CONTEXT_STATUS = VERIFIED
CURRENT_CONTEXT_IDENTITY = ec00773f1a954238c5d5790a64e875c1b904310d4b1ea844d3ce7cafb0483791
CHECKOUT_PROJECTION_COHERENCE_STATUS = VERIFIED
GN_PRESENTATION_BINDING_STATUS = VERIFIED
PREAUTHORIZATION_COHERENCE_STATUS = VERIFIED
CURRENT_DU_STATUS = PASS
CURRENT_EB_STATUS = PASS
CURRENT_EE_STATUS = PASS
```

# 3. Constitutional Self-Assessment

`CERTIFIED != AUTHORIZED`, `PRESENTATION != AUTHORIZATION`, and
`PROVIDER_CAPABILITY != EXECUTION_AUTHORITY`. The context and presentation
binding are readiness evidence only.

## Reuse Impact Assessment

1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo? EX 17/17,
   P11 D2, CHE, FK, DU, EB, EE, FM sole route, GN, GL, HG checkout projection,
   HT route extension, HV correction, governance, and Layer 0.
2. Katere nove zmogljivosti (če sploh) nastanejo? Only HW generation-specific
   committed-identity binding, current readiness evidence, and its tests.
3. Ali katera obstoječa zmogljivost postane nedosegljiva? No.
4. Ali implementacija ustvarja vzporedni tok? No.
5. Ali zmanjšuje ali povečuje število produkcijskih poti? Neither; it remains
   exactly one.

```text
REUSED_CERTIFIED_CAPABILITY_SET = EX_17_OF_17,P11_D2,CHE,FK,DU,EB,EE,FM,GN,GL,HG,HT,HV,GOVERNANCE,LAYER_0
NEW_CAPABILITY_SET = HW_GENERATION_SPECIFIC_LIVE_BINDING_AND_READINESS_EVIDENCE
UNREACHABLE_PREEXISTING_CAPABILITY_SET = EMPTY
EX_REUSED = 17/17
EX_RECONSTRUCTED = 0
PRODUCTION_ROUTE_BEFORE = 1
PRODUCTION_ROUTE_AFTER = 1
PRODUCTION_ROUTE_DELTA = 0
NEW_GENERIC_FRAMEWORK_COUNT = 0
NEW_AUTHORITY_LAYER_COUNT = 0
NEW_PRODUCTION_ROUTE_COUNT = 0
NEW_RUNTIME_OWNER_COUNT = 0
```

## CCWIM

```text
CCWIM_MATURITY_LEVEL = ESTIMATED__L4_LIKE
CROSS_WORKER_STATE_RECOVERY_LEVEL = VERIFIED__COMMITTED_HV_AND_PREDECESSOR_LINEAGE_RECONSTRUCTED
REPOSITORY_DERIVED_CONTEXT_RATIO = ESTIMATED__DOMINANT
HUMAN_HANDOFF_INFORMATION_REQUIRED = VERIFIED__BOUNDED_HW_COMMISSION_ONLY
PREVIOUS_WORKER_CONVERSATION_REQUIRED = NO
PREVIOUS_WORKER_IDENTITY_REQUIRED = NO
PREVIOUS_WORKER_MEMORY_REQUIRED = NO
AUTHENTICATED_REPOSITORY_CONTINUATION = YES
INTER_GENERATION_CROSS_WORKER_CONTINUATION = VERIFIED
INTRA_GENERATION_CROSS_WORKER_CONTINUATION = NOT_APPLICABLE
UNCOMMITTED_DELTA_RECOVERY = NOT_APPLICABLE
AUTHORITY_STATE_RECOVERY = VERIFIED__NO_HW_AUTHORITY_EXISTS
CROSS_WORKER_CONSTITUTIONAL_DRIFT = 0
HANDOFF_SUFFICIENCY_STATUS = VERIFIED
HANDOFF_STATE_COMPLETENESS = VERIFIED
HANDOFF_RECONSTRUCTION_REQUIRED = VERIFIED__YES
HANDOFF_RECONSTRUCTION_SUCCESS = VERIFIED__YES
HANDOFF_AMBIGUITY_COUNT = 0
UNAUTHENTICATED_HANDOFF_ASSUMPTION_COUNT = 0
```

## Cognition provenance and metrics

COGNITION_PROVENANCE = VERIFIED. Primary authority derives from authenticated
committed HV, HU, HT, HR, HP, P11, EX, FM, GN, HG, DU, EB, EE, CHE, FK,
governance, Layer 0, the pinned nested authority, and fresh deterministic HW
evidence. The prompt supplied scope, prohibitions, locators, and checkpoint
expectations; it was not accepted as system-state authority.

| Metric | Assessment |
|---|---|
| PROJECT_PROGRESS_ESTIMATE | `ESTIMATED__WRONG_CONTRACT_PREOPERATIONAL_READINESS_COMPLETE` |
| CONSTITUTIONAL_HEALTH_EVIDENCE | `VERIFIED` |
| SHADOW_AUTOMATION_STATUS | `VERIFIED__ABSENT` |
| CONSTITUTIONAL_FRONTIER_DISTANCE | `ESTIMATED__ONE_SEPARATELY_AUTHORIZED_OPERATIONAL_GENERATION` |
| E05_FRONTIER_DISTANCE | `VERIFIED__10_OF_18_OBLIGATIONS_REMAIN` |
| SELECTED_E05_LOCAL_FRONTIER_DISTANCE | `ESTIMATED__ONE_FUTURE_HUMAN_OPERATIONAL_GENERATION` |
| GOVERNANCE_EFFICIENCE | `ESTIMATED__TARGETED_AFFECTED_FRONTIER` |
| ARCHITECTURAL_GOVERNANCE_EFFICIENCE | `VERIFIED__ONE_ROUTE_RETAINED` |
| PROOF_REUSE_EFFICIENCY | `ESTIMATED__HIGH__EX_17_OF_17_AND_EXISTING_OWNERS_REUSED` |
| COGNITION_ASSISTED_HANDOFF | `VERIFIED` |
| AIGOL_CODEX_WORK_SHARE | `NOT_MEASURED` |
| OVERENGINEERING_RISK | `ESTIMATED__LOW` |
| PROOF_PROCESS_OVERHEAD_RISK | `ESTIMATED__MEDIUM` |
| COGNITION_PROVENANCE | `VERIFIED` |
| CANDIDATE_CAPABILITY | `VERIFIED` |
| WRONG_CONTRACT_CANDIDATE_CAPABILITY | `VERIFIED` |
| WRONG_CONTRACT_REPOSITORY_CAPABILITY | `VERIFIED` |
| WRONG_CONTRACT_ROUTE_SUPPORT | `VERIFIED` |
| WRONG_CONTRACT_BINDING_STATUS | `VERIFIED` |
| WRONG_CONTRACT_PREOPERATIONAL_READINESS | `VERIFIED` |
| WRONG_CONTRACT_OPERATIONAL_CAPABILITY | `NOT_PROVEN` |
| SHADOW_DESIGN_TARGET | `VERIFIED__FORMALIZE_REUSE_BIND_VERIFY` |
| CONSTITUTIONAL_CONTINUATION_PROGRESS | `VERIFIED__PREOPERATIONAL_READINESS_VERIFIED` |
| PROMPT_CONTEXT_REUSE_RATIO | `NOT_MEASURED` |
| TOKEN_BENCHMARK | `NOT_MEASURED` |
| LLM_COST_REDUCTION_RATIO | `NOT_MEASURED` |
| LCRR | `NOT_MEASURED` |
| E05_GENERATIONS_PER_CREDIT | `NOT_MEASURED` |
| OPERATIONAL_ATTEMPTS_PER_CREDIT | `NOT_APPLICABLE` |
| MARGINAL_E05_GENERATION_COST | `NOT_MEASURED` |
| INFRASTRUCTURE_AMORTIZATION_SIGNAL | `ESTIMATED__POSITIVE_REUSE_SIGNAL_WITH_ZERO_CREDIT` |

No total-project denominator or token count was invented.

## Infrastructure amortization

```text
DID_HW_REQUIRE_NEW_COMMON_INFRASTRUCTURE? = NO
DID_HW_REQUIRE_NEW_VECTOR_SPECIFIC_INFRASTRUCTURE? = YES__GENERATION_SPECIFIC_EVIDENCE_ONLY
DID_HW_REQUIRE_NEW_GENERIC_FRAMEWORK? = NO
DID_HW_REQUIRE_NEW_AUTHORITY_LAYER? = NO
DID_HW_REQUIRE_NEW_RUNTIME_OWNER? = NO
DID_HW_REQUIRE_NEW_PRODUCTION_ROUTE? = NO
DID_HW_REUSE_HV_CORRECTION? = YES
DID_HW_REUSE_HT_ROUTE_EXTENSION? = YES
DID_HW_REUSE_EXISTING_POST_COMMIT_BINDING_ARCHITECTURE? = YES
DID_HW_REUSE_EXISTING_CHECKOUT_PROJECTION_ARCHITECTURE? = YES
DID_HW_REUSE_GN_GL_DU_EB_EE? = YES
DID_HW_PRESERVE_WRONG_ATTEMPT? = YES
DID_HW_PRESERVE_WRONG_INPUT? = YES
WAS_EX_REUSED_17_OF_17? = YES
IS_8_TO_9_INFRASTRUCTURE_AMORTIZATION_SIGNAL_POSITIVE? = ESTIMATED__YES
```

This is a capability-reuse signal. Compute/cost reduction is `NOT_MEASURED`
and is not inferred from proof reuse.

# 4. Validation Matrix

The preauthorization negative matrix rejects stale HV HEAD/tree, FM launcher,
FM context owner, adapter, cloud-init, NoCloud seed, checkout HEAD/tree,
projection, candidate, runtime projection, operation context, context-candidate
binding, GN presentation, DU, EB, EE, and vector. Separate substitution cases
reject WRONG_ATTEMPT, WRONG_INPUT, UNKNOWN, and MALFORMED.

The historical failure firewall blocks missing operation context, stale context
owner, projection mismatch, stale checkout owner, stale bootstrap HEAD/tree,
stale expected harness, stale adapter identity, stale NoCloud seed, stale
candidate/runtime projection, stale post-commit binding, and cross-vector
substitution. HU is retained as authenticated historical failure evidence; HV
is the explicit later committed correction and is not deselected.

```text
PREAUTHORIZATION_NEGATIVE_MATRIX_STATUS = VERIFIED
KNOWN_HISTORICAL_FAILURE_CLASS_BLOCK_STATUS = VERIFIED
NO_KNOWN_REPOSITORY_PREAUTH_BLOCKER_STATUS = VERIFIED
```

| Validation | Result |
|---|---|
| Exact HV HEAD/tree/subject; live remote equality; clean tracked entry; empty entry index | `PASS` |
| HU/HT/HR/stable ancestry and nested clean/detached/pinned authority | `PASS` |
| Committed identity map and HV/HU frontier reconstruction | `PASS` |
| FM checkout, WC bootstrap, NoCloud projection, expected harness | `PASS` |
| Host/guest semantics and selected-checkout dependency closure | `PASS` |
| HW candidate semantic firewall; runtime/context; GN coherence; negative matrix; terminal/report | `PASS__33_OF_33` |
| Fresh DU | `PASS__ONE_POSITIVE__TEN_NEGATIVE` |
| Fresh EB | `PASS__ONE_POSITIVE__TWELVE_NEGATIVE` |
| Fresh EE | `PASS__ONE_POSITIVE__SIXTEEN_NEGATIVE` |
| Negative matrix and historical failure firewall | `PASS` |
| WRONG_ATTEMPT/WRONG_INPUT regression; WC support; UNKNOWN/MALFORMED rejection | `PASS` |
| HT current route suite | `PASS__15_OF_15` |
| HV current-applicable correction suite | `PASS__19_OF_19__TWO_HISTORICAL_ENTRY_OR_PRECOMMIT_ASSERTIONS_DESELECTED` |
| HU current-applicable historical-frontier subset | `PASS__5_OF_5__34_SUPERSEDED_CHECKPOINT_OR_FUTURE_FIXTURE_ASSERTIONS_DESELECTED` |
| HG current-applicable projection subset | `PASS__8_OF_8__TWO_SUPERSEDED_OWNER_ASSERTIONS_DESELECTED` |
| HK current-applicable bootstrap subset | `PASS__16_OF_16__FOUR_SUPERSEDED_BOOTSTRAP_ASSERTIONS_DESELECTED` |
| Cross-vector rejection and single production route | `PASS` |
| P11/disposable substrate/CHE/FK | `PASS__47_OF_47` |
| EX and Layer 0 | `PASS__EX_12_OF_12__LAYER_0_FREEZE_PASS` |
| Governance tests and governance conformance engine | `PASS__9_OF_9__ENGINE_20_OF_20__CONFORMANT__ZERO_WARNINGS__ZERO_VIOLATIONS` |
| Canonical JSON, duplicate keys, inner seals, Python AST/syntax | `PASS` |
| `git diff --check`; terminal empty index | `PASS` |

# 5. Repository Mutation Summary

The mutation is confined to one generation-specific HW evidence directory and
one G48 report. Production owners, P11, EX, the nested authority, and the
historical/composite worktree were not modified. No file was staged, committed,
or pushed.

Created artifacts:

- `binding/G77_256HW_POST_HV_LIVE_BINDING_V1.py`: repository-only auditor,
  binder, reducer, negative-chain validator, and artifact producer.
- `live_binding/candidate/G77_256HW_WRONG_CONTRACT_CURRENT_CANDIDATE_V1.json`:
  current committed-HV DU candidate.
- `live_binding/runtime_projection/G77_256HW_WRONG_CONTRACT_CURRENT_CANDIDATE_V1.json`:
  byte-identical runtime projection.
- `live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json`: readiness-only sealed
  context.
- `live_binding/bindings/G77_256HW_EB_RECEIPT_V1.json`: fresh EB receipt.
- `live_binding/bindings/G77_256HW_EE_RECEIPT_V1.json`: fresh EE receipt.
- `live_binding/bindings/G77_256HW_EE_PATH_PROJECTION_FIXTURE_V1.py`: static,
  non-executable EE projection fixture.
- `G77_256HW_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json`: canonical sealed
  terminal reduction.
- `tests/test_g77_256hw_post_hv_live_binding_readiness_v1.py`: focused tests.
- This six-heading G48 report.

Operational counters:

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
E05_CREDIT = 0
E05_BEFORE_HW = 8/18
E05_AFTER_HW = 8/18
```

# 6. Certification Verdict

The complete current repository preauthorization chain is proven. This is not
an operational result and supplies no authority.

```text
CURRENT_HV_COMMIT_IDENTITY_STATUS = VERIFIED
COMMITTED_FM_CHECKOUT_BINDING_STATUS = VERIFIED
COMMITTED_WRONG_CONTRACT_BOOTSTRAP_HEAD_TREE_STATUS = VERIFIED
COMMITTED_CHECKOUT_BOOTSTRAP_COHERENCE_STATUS = VERIFIED
COMMITTED_NOCLOUD_PROJECTION_STATUS = VERIFIED
EXPECTED_HARNESS_BINDING_STATUS = VERIFIED
HOST_GUEST_CONTEXT_VECTOR_SEMANTIC_EQUIVALENCE = VERIFIED
POST_COMMIT_LIVE_BINDING_STATUS = VERIFIED
CURRENT_WRONG_CONTRACT_CANDIDATE_STATUS = VERIFIED
CURRENT_RUNTIME_PROJECTION_STATUS = VERIFIED
CURRENT_OPERATION_CONTEXT_STATUS = VERIFIED
GN_PRESENTATION_BINDING_STATUS = VERIFIED
CURRENT_DU_STATUS = PASS
CURRENT_EB_STATUS = PASS
CURRENT_EE_STATUS = PASS
PREAUTHORIZATION_NEGATIVE_MATRIX_STATUS = VERIFIED
KNOWN_HISTORICAL_FAILURE_CLASS_BLOCK_STATUS = VERIFIED
NO_KNOWN_REPOSITORY_PREAUTH_BLOCKER_STATUS = VERIFIED
PREOPERATIONAL_READINESS_STATUS = VERIFIED
NEXT_OPERATIONAL_GENERATION_ELIGIBLE = VERIFIED
WRONG_CONTRACT_OPERATIONAL_CAPABILITY = NOT_PROVEN
E05_AFTER_HW = 8/18
```

```text
LAST_VERIFIED_EDGE = CURRENT_COMMITTED_HV_CANDIDATE_RUNTIME_CONTEXT_GN_DU_EB_EE_PREAUTHORIZATION_CHAIN
FIRST_BROKEN_EDGE = NONE_KNOWN_IN_REPOSITORY_PREAUTHORIZATION_SCOPE
MINIMUM_MISSING_CAPABILITY = ONE_FRESH_SEPARATELY_HUMAN_AUTHORIZED_WRONG_CONTRACT_OPERATIONAL_GENERATION
MINIMUM_LEGAL_NEXT_DELTA = AFTER_HUMAN_REVIEW_AND_COMMIT_ONLY__ONE_FRESH_SEPARATELY_HUMAN_AUTHORIZED_WRONG_CONTRACT_OPERATIONAL_GENERATION
AUTO_CONTINUABLE = NO
HUMAN_REVIEW_REQUIRED = YES
```

Stop for Human review. Do not insert another preparation generation unless the
committed HW identity introduces a concrete post-commit blocker.
