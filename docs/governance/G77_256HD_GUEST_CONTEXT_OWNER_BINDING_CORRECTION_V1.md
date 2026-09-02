# 1. Implementation Summary

Generation: G77-256HD.

Report identity: `G77_256HD_GUEST_CONTEXT_OWNER_BINDING_CORRECTION_V1`.

Reporting date: 2026-09-02.

Constitutional baseline: `constitutional-governance-finalize-v1`; committed HC
checkpoint `a5fde262c8833922375a10e79c745c0ff19e698e`, tree
`c265719bc048a9ab686e290d1952280d5584a43e`; stable ancestry anchor
`5c972e9960987ab27420395b54ace693df097e7b`.

Implementation contracts: G48 Constitutional Evidence Reporting Standard V1,
HC terminal failure reduction, HB repository preoperational readiness, HA
WRONG_INPUT route binding, GP guest checkout-tree precondition, GQ
self-contained checkout materialization, GT operation-scoped checkout
lifecycle, FM one-shot launcher and fresh-operation-context owner, and EX
common certified proof substrate.

Objective: authenticate and safely continue the recovered uncommitted HD delta,
bind the exact FM fresh-operation-context owner into the self-contained guest
checkout before any future Human operational authority request, complete the
same-class and proof-impact reviews, validate the bounded repository-only
correction, and stop for Human review.

The recovered launcher and focused-test paths were authenticated as HD work.
Broad validation then found one defect in that recovered implementation: it
advanced the checkout HEAD/tree while the hash-bound NoCloud bootstrap still
supplied the historical checkout identity to the guest adapter. The bounded HD
correction therefore adds one versioned cloud-init source and its exact NoCloud
seed. Historical GH/FM bootstrap assets remain byte-identical and are selected
only for legacy unbound contexts. No generic packaging system or second owner
was created.

Modified modules and assets:

- `.github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py`: existing context-builder,
  materialization-binding, asset-observation, and authority-free readiness
  owner extended in place;
- `.github/governance/evidence/g77_256hd_guest_context_owner_binding_v1/static/G77_256HD_CLOUD_INIT_USER_DATA_V1.yaml`: versioned current bootstrap source
  carrying the HC checkout HEAD/tree;
- `.github/governance/evidence/g77_256hd_guest_context_owner_binding_v1/static/SAPIANTA_WRONG_ATTEMPT_NOCLOUD_SEED_V1.img`: immutable NoCloud projection of
  the current user-data plus unchanged FM meta-data and network-config;
- `.github/governance/evidence/g77_256hd_guest_context_owner_binding_v1/tests/test_g77_256hd_guest_context_owner_binding_v1.py`: eight-case repository-only
  positive, negative, same-class, semantic-firewall, and static-readiness proof;
- this G48 report.

Intentionally unchanged modules include the FM fresh-operation-context owner,
GY reducer and producer, HA adapter, GN presentation, GP/GQ/GT owners, P11 D2,
canonical CHE, FK, ER/GW checkpoint semantics, DU/EB/EE implementations,
governance conformance, Layer 0, and all historical HC operational evidence.

Architectural boundaries preserved:

- FM `build_operation_context -> materialize_operation_state ->`
  GQ `materialize_guest_self_contained_checkout` remains the one legal chain;
- GP/FМ authority-free readiness remains the preauthorization verifier;
- `main()` remains the sole operational launcher entry point with one QEMU
  `subprocess.run` call;
- Human authority, PRE, QEMU, VM, P11, request construction, protected
  invocation/effect, retry, replay, repair-and-continue, and E05 credit were not
  entered during HD.

# 2. Code Evidence

## Public API and canonical bindings

The current and legacy checkout identities and the exact owner binding are
declared by the existing FM owner. The excerpt is exact; unrelated constants
are omitted:

```python
LEGACY_CHECKOUT_HEAD = "7dce67ec18696ba0bad73130f3f7a84168f25277"
LEGACY_CHECKOUT_TREE = "3cb61ec34e9593efb711dce61014dc8fdf0f6dd9"
CHECKOUT_HEAD = "a5fde262c8833922375a10e79c745c0ff19e698e"
CHECKOUT_TREE = "c265719bc048a9ab686e290d1952280d5584a43e"
GUEST_CHECKOUT_DESTINATION = "/mnt/aigol"
GUEST_CHECKOUT_MOUNT_TAG = "aigol_checkout"
FRESH_OPERATION_CONTEXT_OWNER = (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "sapianta_fresh_operation_context_v1.py"
)
FRESH_OPERATION_CONTEXT_OWNER_HASH_KEY = "fresh_operation_context_owner"
FRESH_OPERATION_CONTEXT_OWNER_SHA256 = (
    "45b97e99122146ec3aa95f45fe5ac71381ca1a11e83b7355438b988608f52fca"
)
```

The owner SHA-256 was independently recomputed from current source bytes. Git
object inspection proves the path absent from legacy checkout commit
`7dce67ec18696ba0bad73130f3f7a84168f25277` and present in HC.

## Orchestration entry point and bootstrap compatibility

No new orchestration entry point exists. `build_operation_context` remains the
one builder and seals the current owner, bootstrap, and checkout identities.
Legacy compatibility is a deterministic selection inside the same owner:

```python
def bootstrap_asset_bindings(context: dict[str, Any]) -> dict[str, str]:
    """Select the immutable bootstrap pair bound by this context revision."""

    hashes = context.get("wrapper_fc_er_che_schema_hashes", {})
    if FRESH_OPERATION_CONTEXT_OWNER_HASH_KEY in hashes:
        return {
            "cloud_init_path": CLOUD_INIT,
            "cloud_init_sha256": CLOUD_INIT_SHA256,
            "seed_path": SEED,
            "seed_sha256": EXPECTED_ASSET_SHA256[SEED],
        }
    return {
        "cloud_init_path": LEGACY_CLOUD_INIT,
        "cloud_init_sha256": LEGACY_CLOUD_INIT_SHA256,
        "seed_path": LEGACY_SEED,
        "seed_sha256": EXPECTED_ASSET_SHA256[LEGACY_SEED],
    }
```

This selection does not permit caller override. Current contexts contain the
owner binding and must use the HD bootstrap pair; historical contexts without
that key remain bound to their exact committed legacy pair.

## Semantic reductions and public validators

The owner proof rejects missing, unsafe, wrong-hash, wrong-byte, noncanonical,
and wrong guest-presentation state. The excerpt is exact; the returned evidence
mapping is omitted:

```python
def prove_guest_fresh_operation_context_owner_binding(
    repository_root: Path,
    context: dict[str, Any],
) -> dict[str, Any]:
    """Prove one source -> checkout -> read-only guest owner identity."""

    hashes = context["wrapper_fc_er_che_schema_hashes"]
    expected_sha256 = hashes.get(FRESH_OPERATION_CONTEXT_OWNER_HASH_KEY)
    if expected_sha256 != FRESH_OPERATION_CONTEXT_OWNER_SHA256:
        raise RuntimeError("FM context owner hash binding missing or invalid")

    source = repository_root.resolve() / FRESH_OPERATION_CONTEXT_OWNER
    if source.is_symlink() or not source.is_file():
        raise RuntimeError("authoritative FM context owner absent or unsafe")
    source_sha256 = sha256_path(source)
    if source_sha256 != expected_sha256:
        raise RuntimeError("authoritative FM context owner SHA-256 mismatch")

    checkout = Path(
        context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["path"]
    )
    try:
        resolved_checkout = checkout.resolve(strict=True)
    except (FileNotFoundError, RuntimeError) as exc:
        raise RuntimeError("FM context owner checkout root is not canonical") from exc
    if checkout.absolute() != resolved_checkout:
        raise RuntimeError("FM context owner checkout root is not canonical")
    projected = checkout / FRESH_OPERATION_CONTEXT_OWNER
    if projected.is_symlink() or not projected.is_file():
        raise RuntimeError("materialized checkout FM context owner absent or unsafe")
    if projected.resolve() != projected.absolute():
        raise RuntimeError("materialized checkout FM context owner path is not canonical")
    checkout_sha256 = sha256_path(projected)
    if checkout_sha256 != expected_sha256 or projected.read_bytes() != source.read_bytes():
        raise RuntimeError("materialized checkout FM context owner identity mismatch")
```

`validate_checkout_preboot_readiness` composes the existing GP tree proof with
the owner proof, and `authority_free_static_readiness` calls that composite
before `main()` loads any Human authority. Current contexts without the owner
key fail in `validate_immutable_context_bindings`.

## Canonical data and deterministic algorithms

The current cloud-init source SHA-256 is
`95038a31879b3654607ae82533e9b043fee47e7cc157efdad1b7654a11664421`.
The current NoCloud seed SHA-256 is
`15910599577a84545d79d49383747ce22e630d1cb3f1228509b307487a2261cf`.
`isoinfo` extraction proves `/user-data` byte-identical to the bound HD source;
the existing adapter proof also verifies `/meta-data` and `/network-config`
byte-for-byte. The guest adapter command binds checkout HEAD
`a5fde262c8833922375a10e79c745c0ff19e698e` and tree
`c265719bc048a9ab686e290d1952280d5584a43e`.

The self-contained checkout continues to be a clean detached direct Git
directory with one local object database and no alternates. It is presented
read-only at `/mnt/aigol`; the required owner guest projection is:

`/mnt/aigol/.github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/sapianta_fresh_operation_context_v1.py`.

## Responsibility boundaries and same-class review

| Dependency before request construction | Classification | Evidence |
|---|---|---|
| FM fresh-operation-context owner | `ALREADY_SELF_CONTAINED_AND_HASH_BOUND` after HD | source, checkout, guest path, bytes, and SHA proof |
| GY WRONG_INPUT producer | `ALREADY_SELF_CONTAINED_AND_HASH_BOUND` | HC checkout path and SHA `643de4aa...` |
| FK adapter | `ALREADY_SELF_CONTAINED_AND_HASH_BOUND` | HC checkout path and SHA `7ae10480...` |
| canonical CHE | `ALREADY_SELF_CONTAINED_AND_HASH_BOUND` | HC checkout path and SHA `75801995...` |
| ER harness | `ALREADY_SELF_CONTAINED_AND_HASH_BOUND` | HC checkout path and SHA `4a2a84ff...` |
| HA adapter projection | `NOT_APPLICABLE` | separately projected, byte/hash-bound, read-only guest mount |
| cloud-init/NoCloud bootstrap | `NOT_APPLICABLE` | separate immutable seed drive; current source/member identity revalidated |
| DN harness | `NOT_APPLICABLE` | separate hash-bound read-only guest projection |
| host-only reports and reductions | `HOST_ONLY_BUT_NOT_GUEST_REQUIRED` | not imported before request construction |
| another missing checkout dependency | `MISSING_FROM_SELF_CONTAINED_CHECKOUT` count = 0 | bounded closure review and focused test |

`SAME_CLASS_REVIEW_STATUS = VERIFIED`.

# 3. Constitutional Self-Assessment

## Verified

- exact local and remote HC HEAD, tree, subject, branch, stable ancestry, empty
  index, and clean/detached/pinned nested authority;
- complete initial HD delta inventory: one modified launcher and one untracked
  focused test, both attributable to HD and reused rather than recreated;
- HC serial SHA and Git-object root cause: guest adapter bootstrap entered, then
  the missing owner raised `FileNotFoundError` before request construction;
- authoritative owner SHA, checkout/source/guest byte identity, guest hash
  identity, exact read-only mount projection, clean detached checkout, and
  guest-local Git object reachability;
- fail-closed rejection of missing binding, missing owner, wrong hash, wrong
  bytes, dirty checkout, host-only state, legacy stale checkout, wrong mount,
  and adapter/context disagreement;
- complete current authority-free static readiness under a test-only clean
  repository observation with zero Human authority and zero QEMU execution;
- semantic firewall: `CASE = E05_NEGATIVE_AUTHORITY_WRONG_INPUT`,
  `TARGET_MUTATION = input_identity`,
  `DEPENDENT_RECOMPUTATION = record_identity`, mutation count one, differing
  fields `input_identity, record_identity`;
- one FM launcher, one QEMU call site, one production route, no second checkout
  builder, materializer, lifecycle owner, authority owner, P11 owner, or CHE
  owner;
- EX reused `17/17`, EX reconstructed `0`.

## Not Verified

- post-commit live binding of the HD launcher, new bootstrap assets, and final
  committed HEAD/tree;
- current DU/EB/EE receipts for a future committed HD identity;
- repository-clean operational preauthorization against a future committed HD
  checkpoint;
- any Human operational authorization, PRE, FM operational launch, QEMU/VM
  boot, WRONG_INPUT request, P11 entry, denial, invocation, effect, or E05
  credit; these were intentionally prohibited and not run;
- absolute external-host history beyond repository/test evidence.

## Preauthorization safety property and readiness frontier

| Measurement | Status | Result |
|---|---|---|
| `FM_CONTEXT_OWNER_CHECKOUT_BINDING_STATUS` | VERIFIED | exact owner in HC-pinned self-contained checkout |
| `HOST_CHECKOUT_GUEST_BYTE_IDENTITY_STATUS` | VERIFIED | identical source and checkout bytes; read-only direct guest projection |
| `HOST_CHECKOUT_GUEST_HASH_IDENTITY_STATUS` | VERIFIED | SHA-256 `45b97e99...f52fca` across source, checkout, and sealed expectation |
| `HC_FAILURE_CLASS_STATIC_BLOCK_STATUS` | VERIFIED | historical missing-owner class rejected before authority |
| `PREAUTHORITY_MISSING_OWNER_REJECTION_STATUS` | VERIFIED | focused negative matrix |
| `PREAUTHORITY_WRONG_HASH_REJECTION_STATUS` | VERIFIED | focused negative matrix |
| `PREAUTHORITY_STALE_CHECKOUT_REJECTION_STATUS` | VERIFIED | historical checkout and dirty-state fixtures |
| `SAME_CLASS_REVIEW_STATUS` | VERIFIED | no second missing checkout dependency found |
| `DU_STATUS` | VERIFIED | committed HB baseline reused; HD rebind not yet created |
| `EB_STATUS` | VERIFIED | committed HB baseline reused; HD rebind not yet created |
| `EE_STATUS` | VERIFIED | committed HB baseline reused; HD rebind not yet created |
| `NO_KNOWN_REPOSITORY_PREAUTHORIZATION_BLOCKER` | VERIFIED | complete current static-readiness test passes |
| `POST_COMMIT_LIVE_BINDING_STATUS` | NOT_PROVEN | required after Human commit |
| `PREOPERATIONAL_READINESS_STATUS` | NOT_PROVEN | post-commit DU/EB/EE and clean-checkpoint authentication remain |
| `NEXT_OPERATIONAL_GENERATION_ELIGIBLE` | NOT_PROVEN | no authority may be requested from this uncommitted delta |

The repository-only invariant is established for generated current contexts:
no Human operational authority request is admissible unless the
self-contained checkout contains the exact hash-bound FM context owner. The
terminal disposition is Branch B.

`LAST_VERIFIED_EDGE = UNCOMMITTED_HD_OWNER_BOUND_CONTEXT__SELF_CONTAINED_HC_CHECKOUT__CURRENT_NOCLOUD_BOOTSTRAP__COMPLETE_AUTHORITY_FREE_STATIC_READINESS_PASS`.

`FIRST_BROKEN_EDGE = POST_COMMIT_HD_HEAD_TREE_AND_DU_EB_EE_LIVE_BINDING_ABSENT`.

`MINIMUM_MISSING_CAPABILITY = ONE_POST_COMMIT_HD_LIVE_BINDING_AND_REPOSITORY_READINESS_REAUTHENTICATION`.

`MINIMUM_LEGAL_NEXT_DEVELOPMENT_DELTA = AFTER_HUMAN_COMMIT_ONLY__ONE_BOUNDED_REPOSITORY_ONLY_POST_COMMIT_LIVE_BINDING_AND_DU_EB_EE_READINESS_CERTIFICATION__NO_OPERATION`.

## Proof-impact analysis

`CHANGED_OWNER_SET` is the existing FM context-builder/static-readiness owner
only. The versioned HD user-data and seed are bound dependencies, not new
owners.

`DEPENDENT_PROOF_SET` comprises FM immutable-asset observation and final
admission, GP checkout-tree proof, GQ materialization, GT lifecycle, GH adapter
projection, FY visibility, HA/HB context binding, and the HC failure frontier.

`INVALIDATED_PROOF_FRONTIER` comprises live contexts/candidates/DU/EB/EE
receipts that bind the pre-HD launcher/bootstrap/checkout identity. It also
includes 17 historical snapshot test nodes whose exact predecessor HEAD,
pre-HA frontier, or historical bootstrap reconstruction is intentionally
superseded. They were reproduced and deselected, not counted as passes.

`REUSED_UNCHANGED_PROOF_SET` comprises EX 17/17, GY semantic mutation/reducer,
GN presentation semantics, P11 D2, canonical CHE, FK, ER/GW checkpointing,
Human authority semantics, receipt namespace, governance/layer semantics, and
Layer 0 freeze.

`REVALIDATED_PROOF_SET` comprises focused HD 8/8, applicable lineage 60/60,
owner/materialization/lifecycle 122/122, P11/CHE/FK 33/33, governance/layers
23/23, conformance tests 9/9, conformance engine 20/20, EX 12/12, Layer 0
freeze, source/seed SHA identity, AST route count, and repository whitespace.

## Reuse Impact Assessment

1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo? EX 17/17,
   GY WRONG_INPUT semantics/reducer, HA adapter, GN presentation, FM builder and
   sole launcher, GP verification, GQ materialization, GT lifecycle, FY
   visibility, GL receipt-parent binding, ER/GW checkpointing, DU/EB/EE, P11
   D2, canonical CHE, FK, governance conformance, and Layer 0 freeze.
2. Katere nove zmogljivosti (če sploh) nastanejo? One bounded reusable
   repository capability: exact owner plus bootstrap identity is proven before
   authority for current contexts. It is implemented inside existing owners.
3. Ali katera obstoječa zmogljivost postane nedosegljiva? No. Legacy contexts
   retain their exact legacy bootstrap selection; historical evidence is not
   rewritten.
4. Ali implementacija ustvarja vzporedni tok? No.
5. Ali zmanjšuje ali povečuje število produkcijskih poti? Neither.

`PRODUCTION_ROUTE_BEFORE = 1`, `PRODUCTION_ROUTE_AFTER = 1`,
`PRODUCTION_ROUTE_DELTA = 0`.

## Cost and reuse metrics

| Metric | Status | Evidence-bounded result |
|---|---|---|
| `NEW_CAPABILITY_WORK` | VERIFIED | one preauthority owner/bootstrap dependency-binding correction |
| `REUSED_CAPABILITY_WORK` | VERIFIED | existing FM/GQ/GP/GT/GH/HA/P11 chain and EX 17/17 |
| `NEW_PROOF_WORK` | VERIFIED | eight-case HD suite and G48 reduction |
| `REUSED_PROOF_WORK` | VERIFIED | unchanged certified proof set above |
| `REVALIDATED_PROOF_WORK` | VERIFIED | affected owner, lifecycle, lineage, P11, governance, and EX matrices |
| `RECONSTRUCTED_PROOF_WORK` | VERIFIED | zero |
| `EX_REUSED` | VERIFIED | 17/17 |
| `EX_RECONSTRUCTED` | VERIFIED | 0 |
| `FILES_CHANGED` | VERIFIED | 5 material paths; terminal non-material inventory classified separately |
| `LINES_CHANGED` | VERIFIED | terminal text add/delete count reported in Section 5; binary seed/cache paths are not line-countable |
| `FOCUSED_TEST_COUNT` | VERIFIED | 8 |
| `APPLICABLE_REGRESSION_TEST_COUNT` | VERIFIED | 259 test/check cases excluding focused HD and 20 engine checks |
| `NUMBER_OF_PRODUCTION_ROUTES_BEFORE` | VERIFIED | 1 |
| `NUMBER_OF_PRODUCTION_ROUTES_AFTER` | VERIFIED | 1 |

## CCWIM

| Metric | Status | Evidence-bounded result |
|---|---|---|
| `CCWIM_MATURITY_LEVEL` | ESTIMATED | L4-like repository-authenticated continuation; L5 not claimed |
| `CROSS_WORKER_STATE_RECOVERY_LEVEL` | VERIFIED | exact base and recovered two-path HD delta authenticated |
| `REPOSITORY_DERIVED_CONTEXT_RATIO` | ESTIMATED | repository evidence dominant; prompt supplied boundaries and hypotheses |
| `HUMAN_HANDOFF_INFORMATION_REQUIRED` | VERIFIED | bounded continuation commission required; no operational grant requested |
| `PROMPT_CONTEXT_REUSE_RATIO` | NOT_MEASURED | no token-attribution instrument |
| `PREVIOUS_WORKER_CONVERSATION_REQUIRED` | VERIFIED | no |
| `AUTHENTICATED_REPOSITORY_CONTINUATION` | VERIFIED | exact HC base, remote, nested authority, and delta |
| `INTRA_TASK_CROSS_WORKER_CONTINUATION` | VERIFIED | same HD generation continued after provider exhaustion |
| `UNCOMMITTED_DELTA_RECOVERY` | VERIFIED | recovered work reused and corrected without discard |
| `CROSS_WORKER_CONSTITUTIONAL_DRIFT` | VERIFIED | zero detected after bounded correction and applicable validation |
| `SAME_WORKER_PROVIDER_RESET_RESUME` | NOT_APPLICABLE | fresh-worker cross-account continuation |

## Required project metrics

| Metric | Status | Evidence-bounded result |
|---|---|---|
| `PROJECT_PROGRESS_ESTIMATE` | ESTIMATED | HD repository correction complete; product-wide denominator unavailable |
| `CONSTITUTIONAL_HEALTH_EVIDENCE` | VERIFIED | fail-closed preauthority proof, zero operation, one route |
| `SHADOW_AUTOMATION_STATUS` | VERIFIED | disabled; auto-continuable no |
| `CONSTITUTIONAL_FRONTIER_DISTANCE` | NOT_MEASURED | no global scalar instrument |
| `E05_FRONTIER_DISTANCE` | VERIFIED | 11 of 18 obligations remain |
| `SELECTED_E05_LOCAL_FRONTIER_DISTANCE` | ESTIMATED | one post-commit binding/readiness certification before operational review |
| `GOVERNANCE_EFFICIENCE` | ESTIMATED | EX 17/17 reused, zero reconstruction, localized owner extension |
| `COGNITION_ASSISTED_HANDOFF` | VERIFIED | repository evidence enabled independent cross-worker recovery |
| `AIGOL_CODEX_WORK_SHARE` | NOT_MEASURED | no attribution instrument |
| `OVERENGINEERING_RISK` | ESTIMATED | contained; no generic packaging framework or parallel route |
| `COGNITION_PROVENANCE` | VERIFIED | repository evidence, Codex reasoning, and Human authority remain distinct |
| `CANDIDATE_CAPABILITY` | VERIFIED | committed HB candidate capability reused unchanged |
| `WRONG_INPUT_CANDIDATE_CAPABILITY` | VERIFIED | GY/HB candidate semantics unchanged |
| `WRONG_INPUT_REPOSITORY_CAPABILITY` | VERIFIED | current owner-bound static readiness passes repository-only |
| `WRONG_INPUT_OPERATIONAL_CAPABILITY` | NOT_PROVEN | no operation authorized or performed |
| `SHADOW_DESIGN_TARGET` | VERIFIED | FORMALIZE_REUSE_BIND_VERIFY |
| `CONSTITUTIONAL_CONTINUATION_PROGRESS` | VERIFIED | HD phases A-H complete at Branch B safe stop |
| `PROMPT_CONTEXT_REUSE_RATIO` | NOT_MEASURED | no formal measurement |
| `TOKEN_BENCHMARK` | NOT_MEASURED | no repository instrument |
| `LLM_COST_REDUCTION_RATIO / LCRR` | NOT_MEASURED | no cost baseline |
| `CAOR` | NOT_MEASURED | no formal CAOR instrument |
| `FORMALIZE_REUSE_BIND_VERIFY_COMPLIANCE` | VERIFIED | owner formalized, existing chain reused, hashes bound, affected frontier verified |

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| Exact committed HC base | local HEAD/tree/subject/branch and remote ref | Git authentication and remote `ls-remote` | PASS |
| Stable ancestry and nested authority | anchor; nested HEAD/tree/tag/status | Git ancestry, local/remote tag, clean detached checks | PASS |
| Recovered HD delta | initial launcher/test inventory and content audit | status, diff, attribution, semantic review | PASS |
| HC failure reproduction | serial SHA, terminal reduction, Git objects | focused HD test and independent inspection | PASS |
| Exact owner SHA | current owner source | independent `sha256sum` | PASS |
| Focused HD matrix | HD test module | `8 passed` | PASS |
| Current complete static readiness | materialized checkout/adapter/context/overlay in temporary roots | focused HD positive test | PASS |
| Missing/wrong/stale/dirty negative matrix | HD fixtures | focused HD tests | PASS |
| Same-class dependency closure | checkout dependency hashes and bootstrap projections | focused HD test and source review | PASS |
| HC/HB/HA/GZ/GY/GX/GW/GV applicable lineage | 8 committed suites | `60 passed, 17 deselected` | PASS |
| Historical exact snapshot nodes | superseded predecessor/frontier/bootstrap assertions | raw run reproduced 17 failures | NOT_APPLICABLE |
| Existing owners/materialization/lifecycle | GD/GF/GN/GP/GQ/GT/GH/GJ/GL/FO/FY/GA | `122 passed` | PASS |
| P11/CHE/FK | disposable P11, operational consumer, FK hardening | `33 passed` | PASS |
| EX common substrate | EX validator | 12/12 regressions; 17 certified reused | PASS |
| Governance and layer behavior | governance decisions/risk/failure plus layer tests | `23 passed` | PASS |
| Governance conformance tests | conformance test module | `9 passed` | PASS |
| Governance conformance engine | deterministic read-only engine | 20/20, zero warning/violation | PASS |
| Layer 0 freeze | nested canonical checker | manifest present and enforced | PASS |
| Canonical JSON and duplicate keys | unchanged lineage/evidence suites | applicable matrices | PASS |
| New canonical JSON artifact | no JSON added by HD | artifact-type review | NOT_APPLICABLE |
| Inner seals and cross-file SHA identity | historical suites plus current source/seed/checkout assets | pytest, `sha256sum`, `isoinfo` | PASS |
| Python syntax and AST | launcher and HD test | AST parse | PASS |
| Single production route | launcher `main()` AST | one `main`, one QEMU `subprocess.run` | PASS |
| Semantic firewall | GY/HA sources and focused test | hashes, AST, exact mutation assertions | PASS |
| Repository whitespace | complete text delta | `git diff --check` | PASS |
| Human authority/PRE/FM operation/QEMU/VM/P11 operation | prohibited boundary | intentionally not executed | NOT_APPLICABLE |
| WRONG_INPUT operational capability | no fresh authority or operation | intentionally not run | NOT_RUN |

The 17 deselections are explicit and are not passes: HB four stale exact-HA
entry/rebind nodes; HA one stale GZ entry plus one pre-HD static-context
reconstruction; GZ five superseded GY/live-binding/pre-HA-frontier nodes; GY
three superseded GX/candidate/uncommitted-GY nodes; GX two superseded GW/vector
frontier nodes; and GV one stale predecessor node. The new HD focused proof and
122-case owner matrix revalidate the affected current bootstrap/checkout path.

# 5. Repository Mutation Summary

Material path classification:

- `AUTHENTICATED_HD_DELTA`: the five material paths listed in Section 1;
- `UNTRUSTED_HD_DELTA`: none;
- `UNRELATED_DELTA`: none;
- `GENERATED_NON_MATERIAL_CACHE`: 738 terminal path entries: 731 bytecode
  files (728 ignored plus 3 tracked validation modifications), six pytest-cache
  files, and one ignored clean pinned nested-authority checkout. They are
  separate from material HD work and were not deleted or restored because the
  commission prohibits clean/restore operations.

The initial recovered two-path delta was authenticated. Two versioned static
assets and this report were added only after the owner/lifecycle matrix exposed
the bootstrap HEAD/tree mismatch. Historical FM user-data, GH seed, HC raw
evidence, contexts, receipts, serial, seals, and reductions remain unchanged.

API compatibility: existing function signatures and operation entrypoint are
unchanged. Legacy contexts select their historical bootstrap pair; current
owner-bound contexts select the exact HD pair.

Boundary preservation: no new launcher, QEMU route, checkout builder,
materialization route, lifecycle owner, Human authority mechanism, P11 owner,
CHE owner, production route, generic packaging framework, retry, replay, or
repair path exists.

Terminal text accounting is `1,042 additions and 21 deletions` across the four
text material paths. The new binary seed and three bytecode-cache changes have
no meaningful line count. The index remains empty. No staging, commit, push,
reset, clean, stash, restore, checkout, switch, or history rewrite occurred.

# 6. Certification Verdict

`HUMAN_OPERATIONAL_AUTHORITY = PRE = FM_OPERATIONAL_LAUNCHER_INVOCATION = QEMU = VM_BOOT = OPERATION_ATTEMPT = REQUEST = P11_ENTRY = PROTECTED_INVOCATION = PROTECTED_EFFECT = RETRY = REPAIR_AND_CONTINUE = OPERATIONAL_REPLAY = E05_CREDIT = 0`.

`E05_BEFORE = E05_AFTER = 7/18`. `EX_REUSED = 17/17`.
`EX_RECONSTRUCTED = 0`. `PRODUCTION_ROUTE_DELTA = 0`.

`AUTO_CONTINUABLE = NO`. `HUMAN_REVIEW_REQUIRED = YES`.

CERTIFIED__G77_256HD_GUEST_CONTEXT_OWNER_AND_BOOTSTRAP_BINDING_CORRECTED__POST_COMMIT_LIVE_BINDING_REQUIRED__PREOPERATIONAL_READINESS_NOT_PROVEN__E05_7_OF_18__ZERO_OPERATION__HUMAN_REVIEW_REQUIRED
