# 1. Implementation Summary

Generation: G77-256FY

Report identity: G77_256FY_ONE_BOUNDED_CLASS_A_RUNTIME_EXPORT_PREBOOT_VISIBILITY_COMPOSITION_CORRECTION_V1

Reporting date: 2026-08-30T07:19:35Z

Constitutional baseline: root commit `5b46fce41baede9b20adecf34b9119af2da9cca8`, tree `bdfc40c8466b923e4edc23e2bbafc387d78b47b5`, branch `g77-256fl-wrong-attempt-preboot-blocker`; nested commit `3183bab71f8f30397c0309dd2e6d846d14a11f66`, tree `7c32ec05efc2be43297849bc38ec8766514a523d`; G48 Constitutional Evidence Reporting Standard V1

Implementation contracts: the G77-256FY Human instruction; G77-256FX root-cause diagnosis; FM canonical candidate, runtime projection, materialization and launcher; FO final-admission authority binding; DU Canonical V1 continuation-manifest contract; EB candidate binding; EE runtime-consumer binding; EZ static path binding; FK CHE/reducer; and the certified EX P11/SPCE common substrate

Objective:

Apply the minimum Class-A correction that proves before QEMU that the FM harness-required guest manifest resolves through the actual exported host root to the intended canonical bytes, and make the existing FO final admission fail closed when that proof is absent or mismatched. Prepare only repository/preboot state; do not boot, enter P11, issue `WRONG_ATTEMPT`, retry, replay, repair, or claim E05 credit.

## Authenticated authority

| Identity | Required | Observed | Classification |
|---|---|---|---|
| worktree | `/home/pisarna/work/sapianta-fl` | exact | VERIFIED |
| branch | `g77-256fl-wrong-attempt-preboot-blocker` | exact | VERIFIED |
| root HEAD | `5b46fce41baede9b20adecf34b9119af2da9cca8` | exact | VERIFIED |
| root tree | `bdfc40c8466b923e4edc23e2bbafc387d78b47b5` | exact | VERIFIED |
| root subject | `G77-256FX diagnose FW manifest visibility root cause` | exact | VERIFIED |
| root worktree/index | clean/empty | clean/empty | VERIFIED |
| nested origin | `git@github.com:Aljosa3/sapianta-core.git` | exact | VERIFIED |
| nested immutable ref | `refs/tags/sapianta-system-nested-authority-3183bab-v1` | resolves to required commit | VERIFIED |
| nested HEAD/tree | `3183bab71f8f30397c0309dd2e6d846d14a11f66` / `7c32ec05efc2be43297849bc38ec8766514a523d` | exact | VERIFIED |
| nested state | clean, detached, pinned | exact | VERIFIED |

Authentication completed before mutation. No reset, clean, stash, stage, commit, nested mutation, or unrelated repair occurred.

## Root-cause mapping and exact delta

FX identified `FM_RUNTIME_PROJECTION_TO_QEMU_EXPORTED_G77_EVIDENCE_ROOT` as the first broken edge: FM validated `runtime/G77_256FM_CONTINUATION_MANIFEST_V1.json`, while the executed vector exported `raw/`, where that filename was absent. FY extends the existing owner chain:

```text
FM canonical runtime projection
  -> FY generation-specific writable runtime_export/
  -> exact harness-relative FM filename
  -> corrected canonical QEMU g77_evidence export
  -> unchanged cloud-init /mnt/g77-evidence mount
  -> unchanged FM wrapper guest path
  -> FM preboot visibility proof
  -> FO final admission
  -> sole QEMU call site
```

Implementation scope:

- projected the existing canonical FM manifest byte-for-byte into a fresh FY runtime export root;
- created one corrected canonical QEMU argv bound to that exact root;
- extended the existing FM launcher with sealed composition authentication, static wrapper-contract extraction, cloud-init mount authentication, unambiguous `-virtfs` parsing, mapped-host-file existence/safety/hash/byte checks, and a composed FO final-admission gate;
- allocated fresh FY host receipt paths and fresh guest evidence paths without creating them;
- prepared one fresh unbooted overlay from the unchanged base and one byte-identical FY seed instance; and
- added focused positive and negative repository-only tests.

Modified modules:

- `.github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py`: existing FM preboot and FO final-admission owner extended in place;
- `.github/governance/evidence/g77_256fy_runtime_export_preboot_visibility_v1/G77_256FY_RUNTIME_EXPORT_PREBOOT_COMPOSITION_V1.json`: sealed composition/materialization evidence;
- `.github/governance/evidence/g77_256fy_runtime_export_preboot_visibility_v1/qemu/G77_256FY_QEMU_ARGV_V1.json`: corrected vector;
- `.github/governance/evidence/g77_256fy_runtime_export_preboot_visibility_v1/runtime_export/G77_256FM_CONTINUATION_MANIFEST_V1.json`: byte-identical projection;
- `.github/governance/evidence/g77_256fy_runtime_export_preboot_visibility_v1/tests/test_g77_256fy_preboot_visibility_v1.py`: focused static verification; and
- this report.

Prepared non-repository state:

- `/tmp/g77_256fy/guest-overlay.qcow2`: fresh overlay, SHA-256 `6ea4eed169518c646774cfbe2c7b8c00646a9cdead8798f7c94c786c6b6ce8b2`, `qemu-img check` PASS, never booted; and
- `/tmp/g77_256fy/nocloud-seed.img`: byte-identical seed reuse, SHA-256 `b36a1aac42f687fe3d6b71200b5b65ec93a8a6de59b7dce31d3e6bf2c3b93c2f`.

Intentionally unchanged modules:

- canonical FM candidate and original `runtime/` projection bytes;
- FM/FW historical receipts, vectors, serial evidence, checkpoints, reductions, and consumed overlay;
- DU, EB, EE, EZ, EX 17/17, FK adapter/CHE/reducer, P11, providers, Trusted Access, P12, production routing, base image, guest mount contract, and FM wrapper;
- the nested authority repository.

Architectural boundaries preserved:

- `CERTIFIED != AUTHORIZED`: the checkpoint and tests are non-authority; fresh Human operational authorization remains absent;
- no protected machine effect without valid P11 authority;
- request, entry, invocation, and effect counters remain separate and zero;
- provider capability remains distinct from execution authority;
- no EN-specific semantic dependency was added;
- no second validator, manifest producer, launcher route, worker bypass, P11 path, or production path was created.

# 2. Code Evidence

## Public API

No production public API changed. The active generation-specific surface remains the existing launcher module. The new preboot proof entry point and composed gate are:

```python
def validate_preboot_visibility(
    repository_root: Path,
    argv: list[str],
    canonical_argv_sha256: str,
) -> dict[str, Any]:
    """Authenticate the certified FY checkpoint, then run the FM proof owner."""
```

```python
def validate_final_admission(
    *,
    repository_root: Path,
    authority: dict[str, Any],
    authority_file_sha256: str,
    supplied_authority_sha256: str,
    observed_head: str,
    observed_tree: str,
    anchor_is_ancestor: bool,
    repository_clean: bool,
    observed_asset_sha256: dict[str, str],
    argv: list[str],
    canonical_argv_sha256: str,
    receipt_namespace_consumed: bool,
) -> dict[str, str]:
    """FO final admission extended by the existing FM preboot composition gate."""
```

These are bounded launcher-local functions, not a new public runtime subsystem.

## Orchestration Entry Point

The existing `main()` now calls the combined gate before any receipt write or QEMU call. The excerpt is exact; unrelated argument preparation is omitted:

```python
    admission = validate_final_admission(
        repository_root=repository_root,
        authority=authority,
        authority_file_sha256=authority_file_sha,
        supplied_authority_sha256=arguments.execution_authority_sha256,
        observed_head=git(repository_root, "rev-parse", "HEAD"),
        observed_tree=git(repository_root, "rev-parse", "HEAD^{tree}"),
        anchor_is_ancestor=constitutional_anchor_is_ancestor(repository_root),
        repository_clean=git(repository_root, "status", "--porcelain") == "",
        observed_asset_sha256=asset_observations(repository_root),
        argv=argv,
        canonical_argv_sha256=digest,
        receipt_namespace_consumed=any(path.exists() for path in consumable_paths),
    )
```

The sole execution call remains later:

```python
        result = subprocess.run(argv, check=False)
```

AST validation proved exactly one `validate_final_admission` call and exactly one `subprocess.run(argv, check=False)` call, with the gate earlier in source order.

## Semantic Reductions

The visibility proof reduces the exact path/hash relation and fails closed on absence, symlinks, path escape, ambiguity, or byte mismatch. Representative exact excerpts:

```python
    if qemu_argument != visibility.get("qemu_virtfs_argument"):
        raise RuntimeError("validated runtime root differs from actual QEMU export root")
```

```python
    if mapped_host_path.is_symlink() or not mapped_host_path.is_file():
        raise RuntimeError("required guest manifest host projection absent or unsafe")
    if mapped_host_path.resolve().parent != export_root.resolve():
        raise RuntimeError("mapped manifest escapes certified runtime export root")
```

```python
    if source_path.read_bytes() != runtime_path.read_bytes():
        raise RuntimeError("canonical/runtime-export continuation manifest bytes differ")
```

The final reduction composes, rather than replaces, FO authority admission:

```python
    visibility = validate_preboot_visibility(
        repository_root,
        argv,
        canonical_argv_sha256,
    )
    admission = validate_execution_admission(
```

The excerpt ends before the unchanged FO arguments; no omitted line executes QEMU.

## Public Validators

No parallel public validator was introduced. `prove_visibility_composition` is a pure/read-only helper inside the existing launcher owner. `validate_preboot_visibility` authenticates the exact FY checkpoint file SHA-256 `bad42f1361aac5e45a773242fb6a00445282f8d996ad592d15d363019eaa6baf`, recomputes inner seal `e0452f63fbbf0cc890623b63a273973914852c7e24dad11b5b95f5ed0159a1d5`, and then invokes that helper. `validate_final_admission` invokes it before the unchanged FO pure authority validator.

DU/EB/EE were not rerun because the canonical manifest bytes, DU schema, EB candidate identity, EE wrapper-relative filename, guest mount root, and consumer semantics did not change. Their certified scope remains reusable; FY adds the previously missing QEMU export-root composition.

## Canonical Data Models

The sealed composition checkpoint binds:

| Binding | Exact value |
|---|---|
| host directory exported as `g77_evidence` | `/home/pisarna/work/sapianta-fl/.github/governance/evidence/g77_256fy_runtime_export_preboot_visibility_v1/runtime_export` |
| harness-relative filename | `G77_256FM_CONTINUATION_MANIFEST_V1.json` |
| guest mount destination | `/mnt/g77-evidence` |
| guest path read by harness | `/mnt/g77-evidence/G77_256FM_CONTINUATION_MANIFEST_V1.json` |
| corresponding host file | `/home/pisarna/work/sapianta-fl/.github/governance/evidence/g77_256fy_runtime_export_preboot_visibility_v1/runtime_export/G77_256FM_CONTINUATION_MANIFEST_V1.json` |
| host file preboot state | present, regular, non-symlink |
| host/canonical SHA-256 | `a28d2c6d903ed0abafd6fecdc1979f763de4c79127018655370975d52fc05fb4` / same |
| QEMU argv file SHA-256 | `d4e38fb7c6510cec380a95f66352b272a91b40753b199e6ee2ea9774a4bcf4a3` |
| canonical argv SHA-256 | `40a0c1382725a68f33beb0a351e2661cec5c1851041b4fb1058626a1d1da818e` |

The exact corrected QEMU binding is:

```text
local,path=/home/pisarna/work/sapianta-fl/.github/governance/evidence/g77_256fy_runtime_export_preboot_visibility_v1/runtime_export,mount_tag=g77_evidence,security_model=none
```

## Deterministic Algorithms

The existing ER canonical argv encoder remains hash-pinned at `00b2676f1c8360d7c1a3188095520f4592639e174f6b25e198e3036744d948ac`. FY reuses its length-delimited argv SHA-256 algorithm unchanged. The launcher additionally uses:

- duplicate-key-rejecting JSON parsing;
- canonical sorted-key JSON for inner checkpoint seal recomputation;
- AST-only extraction of one module-level `RAW_ROOT` and one `CONTINUATION_MANIFEST_PATH` declaration without importing guest code;
- exact single `g77_evidence` `-virtfs` selection and exact option-set enforcement;
- SHA-256 and exact byte comparison of source and runtime projection; and
- path resolution checks rejecting symlinks and export-root escape.

## Responsibility Boundaries

The responsibilities remain single-owner and conjunctive:

- DU owns canonical manifest schema/producer semantics;
- FM owns materialization, runtime projection, preboot visibility, and the one-shot launcher;
- FO owns final execution admission and Human authorization binding;
- cloud-init owns mounting the already-bound QEMU tag at the unchanged guest destination;
- the wrapper owns only the static guest-relative consumer declaration;
- FK owns CHE correlation and terminal reduction;
- P11 and Human Authority remain unchanged and were not entered or fabricated.

`PRODUCTION_ROUTE_DELTA = 0`; FY extends the existing path, replaces no path, and creates no parallel path.

# 3. Constitutional Self-Assessment

## Verified

- Starting root and nested identities authenticated exactly before mutation.
- FX root-cause assumptions reauthenticated; no wider architectural dependency was found.
- The runtime export contains the exact canonical manifest bytes at the harness-relative filename before QEMU.
- QEMU argv, export root, cloud-init mount, wrapper guest path, mapped host path, manifest SHA-256, and final admission are one deterministic composition.
- A validated/exported-root mismatch cannot reach the sole QEMU call.
- Missing and wrong-byte manifest fixtures fail closed without mutating historical evidence or invoking QEMU.
- FO’s 11/11 original admission tests remain PASS; FY’s 6/6 focused tests PASS.
- Python in-memory syntax compilation PASS.
- Governance conformance tests 9/9 PASS; conformance engine 20/20 PASS, status `CONFORMANT`, zero warnings and zero critical violations.
- `git diff --check` PASS before report creation.
- Historical FM/FW receipt and reduction paths are absent from the diff; their observed hashes remain `2148a476…`, `7589a409…`, and `dbf5f7a…` respectively.
- Fresh FY receipt, guest evidence/seal, and serial paths remain absent.
- No `qemu-system` process was observed; no VM boot, QEMU execution, P11 entry, request, invocation, effect, retry, repair, or replay occurred.
- EX remains reuse-only at 17/17 with zero reconstruction; E05 remains 6/18.

## Not Verified

- Operational behavior is NOT PROVEN: QEMU, VM boot, guest mount execution, P11, and `WRONG_ATTEMPT` were intentionally not run.
- A future Human operational authorization is absent and was not fabricated or inferred.
- A future operational generation is not guaranteed to pass; FY proves only repository/materialization/preboot composition readiness.
- Token usage, billed tokens, monetary cost, prompt-context reuse, and LLM cost reduction were not available and are NOT MEASURED.
- No new E05 operational credit is claimed.

## Seed, candidate, base, and P11 disposition

```text
SEED_REUSED_BYTE_FOR_BYTE = YES
SEED_REBUILD_REQUIRED = NO
REASON = GUEST_MOUNT_TAG_DESTINATION_WRAPPER_AND_CLOUD_INIT_CONTRACT_UNCHANGED; FY COPIED THE AUTHENTICATED FM SEED BYTES INTO A FRESH FY PATH
CANDIDATE_REBUILD = NO
VM_BASE_REBUILD = NO
P11_CHANGE = NO
FRESH_OVERLAY_CREATED = YES__UNBOOTED__UNCHANGED_BASE
```

## Frontier report

```text
GLOBAL_E05_FRONTIER = VERIFIED__E05_6_OF_18__REMAINING_12
WRONG_ATTEMPT_LOCAL_FRONTIER = VERIFIED__CORRECTED_REPOSITORY_AND_PREBOOT_COMPOSITION_READY_FOR_HUMAN_REVIEW
WRONG_ATTEMPT_LOCAL_FRONTIER_DISTANCE = NOT_MEASURED_NUMERICALLY__NEXT_REQUIRED GENERATION IS A SEPARATE FRESH HUMAN_AUTHORIZED OPERATIONAL COMMISSIONING; ITS OUTCOME IS NOT PROVEN
```

The next legal sequence is Human review, bounded commit, exact new HEAD/tree/subject with clean worktree and empty index, then a separately authorized operational generation. FY does not auto-continue.

## Reuse Impact Assessment

1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo? EX 17/17; DU Canonical V1 schema/producer; EB candidate binding; EE consumer binding; EZ static declaration semantics; FM candidate/runtime bytes, wrapper and cloud-init contract; ER argv canonicalizer; FK adapter/CHE/reducer; FO authority admission; unchanged base and read-only checkout.
2. Katere nove zmogljivosti, če sploh, nastanejo? One bounded ability inside the existing FM/FO path to prove end-to-end runtime-export visibility before final admission. No independent subsystem arises.
3. Ali katera obstoječa zmogljivost postane nedosegljiva? No certified capability is removed. Consumed FW state remains intentionally unusable as fresh state.
4. Ali implementacija ustvarja vzporedni tok? No.
5. Ali zmanjšuje ali povečuje število produkcijskih poti? Neither; `PRODUCTION_ROUTE_DELTA = 0`.
6. Is EX still reused 17/17 with zero reconstruction? Yes, VERIFIED: `EX_REUSED = 17`, `EX_RECONSTRUCTED = 0`.
7. Which FE DU/EB/EE proofs remain reusable? DU schema/semantic validity, EB exact FM candidate receipt, and EE candidate/runtime/consumer-path binding remain reusable without rerun; the guest contract did not change.
8. Is FK CHE/reducer reused unchanged? Yes.
9. Which FM candidate/materialization semantics are reused? Exact candidate and runtime-projection bytes, semantic identity, wrapper, cloud-init mount, no-network vector shape, seed bytes, base, checkout, and fresh-overlay derivation semantics. The stale export-root composition is replaced by FY evidence/vector.
10. Which FO authority/admission semantics are reused or extended? All FO Human authority, repository state, asset, no-network, one-shot, retry/repair/replay, and ancestry gates are reused. Final admission is extended conjunctively with the authenticated preboot visibility result.
11. Which FW assets remain permanently consumed? Historical FM pre/post QEMU receipts, FW runtime evidence/seals, FW serial/evidence reduction, and the boot-mutated FM overlay/one-shot namespace.
12. Which assets must be fresh for the next operational generation? Human authorization, exact post-commit HEAD/tree binding, FY receipt namespace, FY writable guest evidence paths, FY overlay, corrected argv/package identity, and any generation-specific finalization evidence.
13. Did FY introduce any EN-specific semantic dependency? No.
14. Can the FW failure now be detected before QEMU? Yes, VERIFIED statically for the corrected path.
15. Was an existing owner extended instead of creating a new validator? Yes: the active FM launcher and FO final admission were extended in place.

## Required metrics

| Metric | Classification | Evidence / value |
|---|---|---|
| `CONSTITUTIONAL_HEALTH_EVIDENCE` | VERIFIED | FY 6/6, FO 11/11, governance 9/9, engine 20/20; zero critical violations |
| `SHADOW_AUTOMATION_STATUS` | VERIFIED | disabled: `auto_continuable=false`, Human authorization absent, no operational call |
| `CONSTITUTIONAL_FRONTIER_DISTANCE` | NOT_MEASURED | qualitative frontier is verified as Human review -> commit -> exact clean identity -> fresh Human authorization -> separate operational generation |
| `WRONG_ATTEMPT_LOCAL_FRONTIER_DISTANCE` | NOT_MEASURED | one separate operational generation is next; outcome not proven |
| `GOVERNANCE_EFFICIENCE` | VERIFIED | EX reuse 17/17, reconstruction 0/17, DU/EB/EE reruns 0/3, operational executions 0 |
| `OPERATIONAL_PROOF_YIELD` | NOT_MEASURED | 0 operational proofs from 0 authorized operational attempts; ratio undefined |
| `COGNITION_ASSISTED_HANDOFF` | VERIFIED | sealed composition, deterministic tests, report, explicit next authority boundary |
| `AIGOL_CODEX_WORK_SHARE` | NOT_MEASURED | existing deterministic infrastructure: EX/DU/EB/EE/FM/FO/FK; fresh Codex cognition: trace interpretation, minimum-delta choice, composition implementation and explanation; no percentage telemetry |
| `OVERENGINEERING_RISK` | ESTIMATED | low: one existing launcher extended, zero route delta, no new subsystem; estimate is qualitative |
| `COGNITION_PROVENANCE` | VERIFIED | repository/deterministic facts, Codex reasoning, and Human authority are separated below |
| `CANDIDATE_CAPABILITY` | VERIFIED | canonical FM candidate unchanged; corrected static preboot admissibility proven; operational result not proven |
| `SHADOW_DESIGN_TARGET` | VERIFIED | one-shot, no-network, no provider, no auto-continuation, Human-gated |
| `CONSTITUTIONAL_CONTINUATION_PROGRESS` | VERIFIED | FY repository/preboot correction complete; E05 6/18 unchanged; operational phase not started |
| `PROMPT_CONTEXT_REUSE_RATIO` | NOT_MEASURED | no authoritative prompt-token telemetry |
| `TOKEN_BENCHMARK` | NOT_MEASURED | no authoritative token telemetry |
| `LLM_COST_REDUCTION_RATIO / LCRR` | NOT_MEASURED | no authoritative token or monetary baseline |

## Cognition provenance

- REPOSITORY / DETERMINISTIC FACTS: Git identities, immutable tag resolution, file and inner hashes, exact argv, AST/static path extraction, test results, physical file identities, absent receipt paths, conformance results, and counters.
- CODEX COGNITION: trace interpretation, Class-A minimum-delta selection, decision to extend the existing owner, negative-fixture design, architectural classification, and explanatory reasoning.
- HUMAN AUTHORITY: supplied starting identity, FY repository/preboot mutation authority, future commit decision, and any future operational authorization.

Codex reasoning and generated evidence are not Human operational authority.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| Exact starting root authority | Git HEAD/tree/branch/status/log | mandatory pre-mutation commands | PASS |
| Exact nested authority | origin, detached HEAD/tree, tag ref, clean status | nested Git authentication | PASS |
| FX Class-A root cause remains valid | FM runtime/raw/vector/wrapper/cloud-init trace and FX report | deterministic repository review | PASS |
| Fresh writable runtime export root | FY `runtime_export/` | directory and file observation | PASS |
| Exact FM manifest projection | source and FY runtime files | SHA-256 plus byte comparison | PASS |
| Exact harness guest path | unchanged FM wrapper AST | one static `RAW_ROOT` and one relative declaration | PASS |
| Exact guest mount destination | unchanged cloud-init | hash plus unique mount literal | PASS |
| Exact QEMU export root | FY argv and sealed composition | unique exact `g77_evidence` `-virtfs` parsing | PASS |
| Canonical argv identity | FY vector and ER canonicalizer | file SHA-256 and canonical argv SHA-256 | PASS |
| Host-to-guest composition | FM launcher `validate_preboot_visibility` | exact positive focused test | PASS |
| FO consumes same composition | `validate_final_admission` | exact synthetic-authority/read-only asset test | PASS |
| Mismatched exported root denied | mutated in-memory argv fixture | focused negative test | PASS |
| Absent manifest denied | bounded temporary empty export fixture | focused negative test | PASS |
| Wrong manifest bytes denied | bounded temporary wrong-byte fixture | focused negative test | PASS |
| QEMU not reachable before gates | launcher AST | gate/call count and source-order test | PASS |
| Existing FO semantics preserved | FO focused suite | 11/11 tests | PASS |
| Python syntax | launcher and FY test | in-memory `compile`, no bytecode | PASS |
| Fresh overlay/unchanged base | `/tmp/g77_256fy` and base | SHA-256, `qemu-img info/check` only | PASS |
| Seed byte reuse | FM and FY seed files | SHA-256 comparison | PASS |
| Historical evidence immutable | Git diff inventory and exact historical hashes | read-only comparison | PASS |
| EX/DU/EB/EE reuse-only | certified evidence and unchanged inputs | hash/reference reauthentication; no rerun | PASS |
| Governance conformance tests | `tests/test_governance_conformance.py` | 9/9 tests | PASS |
| Governance engine | deterministic read-only engine report | 20/20 checks, `CONFORMANT` | PASS |
| Whitespace integrity | repository diff | `git diff --check` | PASS |
| Operational commissioning | prohibited by FY | not executed by contract | NOT_APPLICABLE |
| E05 operational credit | requires operational evidence | none claimed | NOT_APPLICABLE |

# 5. Repository Mutation Summary

Modified files:

- existing launcher: FM preboot visibility and FO final-admission composition, fresh FY vector/receipt/evidence bindings;
- new FY composition JSON: sealed host/QEMU/guest/admission binding;
- new FY vector JSON: exact fresh export/overlay/seed paths;
- new FY runtime manifest: byte-identical canonical projection;
- new FY focused test: six repository-only positive/negative checks;
- new FY G48 report: this file.

Actual mutation set equals the intended repository mutation set. The separately declared physical preparation added only `/tmp/g77_256fy/guest-overlay.qcow2` and `/tmp/g77_256fy/nocloud-seed.img`. No unexpected modified file was observed.

Unchanged subsystems:

- constitutional L0/L1 artifacts, Product 1 runtime, P11, P12, provider and Trusted Access paths, production routing, DU/EB/EE/EZ, EX, FK CHE/reducer, canonical argv implementation, FM candidate/wrapper/cloud-init, nested authority, historical FM/FW receipts/vectors/checkpoints/serial/reductions, and base image.

API compatibility:

- no production API changed;
- original FO `validate_execution_admission` signature and behavior remain intact, proven by its unchanged 11-test suite;
- launcher `main()` remains the sole execution route and now requires the additional conjunctive preboot proof.

Boundary preservation:

```text
EX_REUSED = 17
EX_RECONSTRUCTED = 0
DU_RERUN = 0
EB_RERUN = 0
EE_RERUN = 0
PRODUCTION_ROUTE_DELTA = 0
PATH_CHANGE = EXTENDS_EXISTING_PATH
PARALLEL_PATH_CREATED = NO
SEED_REUSED_BYTE_FOR_BYTE = YES
SEED_REBUILD_REQUIRED = NO
CANDIDATE_REBUILD = NO
VM_BASE_REBUILD = NO
P11_CHANGE = NO
VM_BOOT_COUNT = 0
QEMU_EXECUTION_COUNT = 0
WRONG_ATTEMPT_EXECUTION_COUNT = 0
REQUEST_COUNT = 0
P11_ENTRY_COUNT = 0
PROTECTED_INVOCATION_COUNT = 0
PROTECTED_EFFECT_COUNT = 0
RETRY_COUNT = 0
REPAIR_EXECUTION_COUNT = 0
REPLAY_EXECUTION_COUNT = 0
E05_BEFORE = 6_OF_18
E05_AFTER = 6_OF_18
HUMAN_OPERATIONAL_AUTHORIZATION_PRESENT = NO
AUTO_CONTINUABLE = NO
HUMAN_REVIEW_REQUIRED = YES
```

Unrelated pre-existing changes:

- None observed. The authenticated entry worktree was clean and index empty.

# 6. Certification Verdict

PASS__G77_256FY_CLASS_A_RUNTIME_EXPORT_PREBOOT_VISIBILITY_COMPOSITION_CORRECTED__NO_QEMU_EXECUTION__E05_REMAINS_6_OF_18__HUMAN_REVIEW_REQUIRED
