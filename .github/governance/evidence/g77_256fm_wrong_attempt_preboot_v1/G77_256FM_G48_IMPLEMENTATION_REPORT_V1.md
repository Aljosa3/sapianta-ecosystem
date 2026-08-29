# 1. Implementation Summary

Generation: G77-256FM

Report identity: G77_256FM_G48_IMPLEMENTATION_REPORT_V1

Reporting date: 2026-08-29

Constitutional baseline: committed G77-256FL HEAD
`7dce67ec18696ba0bad73130f3f7a84168f25277`, tree
`3cb61ec34e9593efb711dce61014dc8fdf0f6dd9`, subject
`G77-256FL fail closed incompatible WRONG_ATTEMPT asset`.

Implementation contracts: G77-256FM Human authorization; cross-account
same-generation continuation instruction SHA-256
`a40d9d1a577de5ccc83464e30d901c411e57c3eaba8df14a62257e20b7660a33`;
G48 Constitutional Evidence Reporting Standard V1; EX common-substrate
certificate; DU, EB, and EE contracts; committed FK CHE and terminal-reducer
hardening.

Objective:

Continue the same interrupted G77-256FM generation, authenticate and reuse its
sealed state, complete only the missing static materialization remainder, and
stop with one fresh FK-bound WRONG_ATTEMPT asset in a sealed preboot-ready state.
No operational execution, P11 entry, E05 credit, repository staging, commit, or
push was authorized or performed.

Implementation scope:

- reauthenticate the exact committed FL authority and the dirty FM mutation
  envelope without cleaning, resetting, stashing, or reconstructing it;
- reuse sealed Phase A, all 18 authority bindings, EX 17/17, the sole candidate,
  and the existing DU/EB/EE results;
- classify the interrupted materialization as Case B and reuse the detached
  checkout, overlay, and seed unchanged;
- complete the same materialization with one canonical local/no-network QEMU
  argv and one fresh one-shot launcher/receipt namespace;
- seal SPCE Phases B, C, and D and this implementation report; and
- preserve generation-wide counters across both accounts/sessions.

## Exact Authority / Baseline

The entry branch, HEAD, tree, and subject matched the required FL baseline.
The worktree had no tracked or staged delta and one untracked FM namespace.
Uncommitted FM bytes were treated as continuation state, never as committed
constitutional authority. The detached checkout at `/tmp/g77_256fm/checkout`
is clean and resolves to the exact FL HEAD/tree.

## Cross-Account Continuation Authentication

Previous session: `01a04c6a-fb29-7d22-ac29-1323bc0d0089`.

Continuation session: `01a04ca2-843d-7322-88b7-99763bc2be63`.

The account change and session change did not change the generation. Phase A's
inner seal recomputed to
`f17bac4da26b0d00a396a4117eb04b22b518f47714ac896c102928f5162065b0`.
The candidate, EB receipt, and EE receipt recomputed their canonical inner
hashes and remained mutually bound. The physical state was Case B: checkout,
overlay, and seed were complete and valid; argv, launcher, and final phase
evidence were missing and deterministically completable as the same
materialization.

## Human Authorization

The original Phase A records authorization source SHA-256
`fe90d8faaece20708cb7f328a70f59a4b623dca3672541f90a09e19e43ec1cd1`
for one candidate, one materialization, at most one VM preparation, and zero
boots or operational attempts. The continuation instruction authorized
reauthentication, reuse, completion of only the deterministic missing
remainder, and final evidence production. It explicitly withheld authority for
boot, QEMU system execution, WRONG_ATTEMPT execution, P11 entry, E05 credit,
network/provider use, staging, commit, and push.

## SPCE Phase A/B/C/D

- Phase A: reused unchanged; file SHA-256 `4f8e1d...bbd75`; reconstruction 0.
- Phase B: the sole materialization completed by deterministic resume; inner
  SHA-256 `ad3b2d...62c7`; no boot or execution.
- Phase C: 30/30 required static preboot gates passed; inner SHA-256
  `73dbe8...8959`; no DU/EB/EE rerun.
- Phase D: combined-generation final reduction; inner SHA-256
  `20d4f5...c255`; E05 remained 6/18.

## Candidate / Materialization / Preboot Evidence

- candidate file SHA-256: `a28d2c...5fb4`;
- candidate semantic identity: G77-256FM fresh FL/FK-bound WRONG_ATTEMPT case;
- detached checkout: exact FL HEAD/tree, clean, detached;
- base image SHA-256: `6e40c0...7333`;
- overlay SHA-256: `6ea4ee...e8b2`, qcow2 check passed, clean/not corrupt;
- NoCloud seed SHA-256: `b36a1a...93c2f`, all three inputs byte-identical;
- FM wrapper SHA-256: `b7d8f5...e866d7`;
- committed FK adapter SHA-256: `7ae104...b84c6`;
- argv canonical SHA-256: `5f2de5...c1d1`, exactly one `-nic none`;
- launcher SHA-256: `257fe9...046cc`, syntax validated but never invoked; and
- pre/post execution, raw execution, execution seal, and teardown seal paths
  are fresh and absent.

## Reuse Impact Assessment

1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?
   EX 17/17, FL authority, FK adapter/CHE/reducer, DU, EB, EE, canonical argv
   binding, and G48 reporting are reused by exact reference/hash.
2. Katere nove zmogljivosti, če sploh, nastanejo? One generation-specific FM
   preboot asset instance is created; no new common or operational capability.
3. Ali katera obstoječa zmogljivost postane nedosegljiva? No.
4. Ali implementacija ustvarja vzporedni tok? No.
5. Ali zmanjšuje ali povečuje število produkcijskih poti? Neither; delta 0.
6. Ali je FM asset vezan na en canonical committed source? Yes, exact FL.
7. Ali provider capability ostaja centralizirana? Yes; no provider was used.
8. Ali provider facts ostajajo ločeni od consumer-specific policy? Yes.
9. Ali canonical CHE ostaja en sam skupni contract? Yes.
10. Ali terminal reduction ostaja en sam skupni reducer? Yes.
11. Ali zgodovinski FF/FI/FJ assets ostajajo samo evidence? Yes.
12. Ali je Phase A ponovno uporabljen brez rekonstrukcije? Yes, reuse 1,
    reconstruction 0.
13. Ali je isti candidate ponovno uporabljen brez ustvarjanja drugega? Yes.
14. Ali so DU/EB/EE rezultati ponovno uporabljeni brez nepotrebnega reruna?
    Yes; rerun counts are 0/0/0.
15. Ali cross-account continuation zmanjša ali poveča orchestration overhead?
    It decreases overhead relative to reconstruction: one reauthentication pass
    reused all valid state and completed only the missing remainder.

Modified modules:

- `.github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/`: bounded FM
  candidate, adapter, materialization, validation, reduction, and reporting
  artifacts only.

Intentionally unchanged modules:

- committed runtime, canonical CHE, terminal reducer, DU/EB/EE validators,
  EX/EW substrate, historical FF/FI/FJ evidence, Product 1 runtime, P12,
  provider integration, and production routing.

Architectural boundaries preserved:

- committed authority and dirty continuation state remain distinct;
- preparation readiness is not execution authority;
- request is not entry, invocation, or effect;
- provider capability is not authority; and
- replay-safe evidence records explicit limitations and zero operational
  counters.

# 2. Code Evidence

## Public API

No production public API changed. The only new callable surface is the bounded,
generation-specific launcher entry point at
`.github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py`:

```python
def main() -> int:
    repository_root = Path.cwd().resolve()
    if git(repository_root, "HEAD") != REQUIRED_HEAD or git(repository_root, "HEAD^{tree}") != REQUIRED_TREE:
        raise RuntimeError("required Git baseline mismatch")
    pre_path = repository_root / PRE_RECEIPT
    post_path = repository_root / POST_RECEIPT
    if pre_path.exists() or post_path.exists():
        raise RuntimeError("FM launcher receipt already exists; retry prohibited")
```

## Orchestration Entry Point

The launcher binds one exact argv and a direct subprocess call. The following
excerpt is exact; unrelated receipt construction is omitted:

```python
    argv = json.loads((repository_root / VECTOR).read_text(encoding="utf-8"))
    if not isinstance(argv, list) or not argv or argv[0] != "/usr/bin/qemu-system-x86_64":
        raise RuntimeError("exact QEMU argv invalid")
    if argv.count("-nic") != 1 or argv[argv.index("-nic") + 1] != "none":
        raise RuntimeError("no-network QEMU vector invalid")
```

This entry point was syntax-checked but not invoked. Its future receipt paths
remain absent.

## Semantic Reductions

The committed FK reducer remains the single reducer. Exact excerpt from
`.github/governance/evidence/g77_256fc_wrong_attempt_operational_v1/harness/G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py`:

```python
    else:
        creation_count = corrected.get("human_operational_act_creation_count", 0)
        authority_state = (
            "NOT_CREATED__NO_AUTHORITY_SURVIVES"
            if creation_count == 0
            else "UNPROVEN_AUTHORITY_STATE__NO_SUCCESS_CREDIT"
        )
        supplied_failure = first_failure or first_failure_or_current_result or "UNKNOWN"
        result = (
            supplied_failure
            if supplied_failure.startswith("FAIL_CLOSED__")
            else "FAIL_CLOSED__WRONG_ATTEMPT_REQUIRED_SUCCESS_EVIDENCE_MISSING__"
            + supplied_failure
        )
    return {
        "execution_counters": corrected,
        "authority_lifecycle_state": authority_state,
        "first_failure_or_current_result": result,
        "success_evidence_complete": positive_evidence,
        "e05_credit": 1 if positive_evidence else 0,
    }
```

## Public Validators

No public validator was changed. Existing DU/EB/EE receipts were hash- and
seal-reauthenticated without rerunning their validators. Phase C independently
verified every candidate-declared binding and all physical/static preboot
bindings.

## Canonical Data Models

The candidate remains the canonical DU manifest envelope at
`raw/G77_256FM_CANONICAL_CONTINUATION_MANIFEST_PRE_MATERIALIZATION_V1.json`.
Its file and runtime projection are byte-identical at SHA-256 `a28d2c...5fb4`,
and its canonical manifest body is `52f125...e6bbf`. Phase checkpoints use the
established envelope/body-seal model and mark `checkpoint_is_authority: false`.

## Deterministic Algorithms

The committed canonical argv encoder remains unchanged. Exact excerpt from
`G77_256ER_CANONICAL_QEMU_ARGV_V1.py`:

```python
    return DOMAIN + U64.pack(len(encoded)) + b"".join(
        U64.pack(len(argument)) + argument for argument in encoded
    )


def argv_sha256(argv: Sequence[str]) -> str:
    return hashlib.sha256(canonical_argv_bytes(argv)).hexdigest()
```

The exact FM vector reduces to `5f2de525656cf8e107aeb3d094193b3cfacf1d8b8200d86cb0c5762f94bac1d1`.

## Responsibility Boundaries

The adapter binds committed FK bytes; the canonical CHE factory owns
correlation identity; the terminal reducer owns operational credit; the
launcher owns only a future one-shot call site and receipt namespace; Phase D
owns the preparation-only final reduction. None of those artifacts creates
Human execution authority.

# 3. Constitutional Self-Assessment

## Verified

- exact committed FL authority and clean detached runtime checkout;
- sealed Phase A reused once with zero reconstruction;
- EX 17/17 and 18 authority items reused by reference/hash;
- exactly one candidate, one materialization, and one VM preparation;
- existing DU/EB/EE PASS results authenticated with zero reruns;
- committed FK adapter, canonical CHE factory, and FK terminal reducer reachable;
- wrapper, seed, argv, launcher, continuation manifest, and fresh unconsumed
  receipt namespaces bound;
- historical pre-FK adapter, FF/FI/FJ receipts, and post-FJ VM not selected;
- base and overlay static image checks passed; NoCloud inputs are byte-identical;
- local/no-network vector contains exactly one `-nic none`;
- VM boot, QEMU execution, operational attempt, request, entry, invocation,
  effect, retry, repair, and replay counts all equal zero; and
- E05 remained 6/18; PREBOOT_READY did not become execution authority or credit.

## Not Verified

- Operational WRONG_ATTEMPT behavior was not verified because execution was
  expressly prohibited; it remains UNSATISFIED.
- Cloud-init guest behavior was not executed; only static seed identity and
  preboot non-consumption were verified.
- Current-session context, 5h/7d usage, billed tokens, monetary cost, and full
  elapsed time were unavailable and are `NOT_MEASURED`.
- Full-repository regression was not run because this generation changed only
  bounded evidence/preparation artifacts; targeted static validation and
  `git diff --check` are the applicable checks.
- Known governance hook drift remains visible and is not reclassified as full
  conformance by this generation.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| Exact FL authority | Git branch/HEAD/tree/subject | Direct Git reauthentication | PASS |
| Dirty envelope bounded to FM | status, untracked inventory, diff/index checks | Read-only mutation classification | PASS |
| Phase A canonical seal | Phase A checkpoint | Canonical sorted-body SHA-256 recomputation | PASS |
| EX 17/17, reconstruction 0 | EX certificate/final seal and Phase A ledger | File hashes and certificate matrix review | PASS |
| Sole candidate | candidate and runtime projection | File/inner SHA-256 and semantic binding | PASS |
| DU/EB/EE existing results | EB and EE receipts | Receipt body seal and cross-binding reauthentication; no rerun | PASS |
| Same materialization resume | Phase B and `/tmp/g77_256fm` | Checkout/image/seed identity and absence inventory | PASS |
| Detached checkout | `/tmp/g77_256fm/checkout` | Clean index/worktree, exact HEAD/tree | PASS |
| Base/overlay integrity | qcow2 files | `qemu-img info` and `qemu-img check` | PASS |
| NoCloud seed identity | seed plus three YAML inputs | ISO extraction and three SHA-256 comparisons | PASS |
| FM wrapper to FK adapter | FM and FC adapters | Exact hashes and pinned source-path review | PASS |
| Canonical CHE and reducer | committed CHE/FC source | Exact hash and reachable call/reducer review | PASS |
| Canonical argv | FM argv and ER canonicalizer | Canonical digest computation and token review | PASS |
| No network/provider | argv/network-config/Phase D | `-nic none`, empty ethernets, capability NONE | PASS |
| Launcher namespace | FM launcher | In-memory syntax compile; no invocation | PASS |
| Fresh receipt namespaces | FM raw namespace | Required future paths allocated and absent | PASS |
| No boot/execution | serial/process/mount/receipt observations | Static process, mount, file, and counter audit | PASS |
| E05 unchanged | Phase C/D | Counter reduction 6/18 to 6/18 | PASS |
| Operational WRONG_ATTEMPT result | Not produced by FM | Prohibited by authorization | NOT_APPLICABLE |
| Full repository regression | Outside the bounded evidence-only scope | Not run; targeted static checks are applicable | NOT_APPLICABLE |
| Whitespace integrity | complete FM namespace | `git diff --check` | PASS |

# 5. Repository Mutation Summary

Modified files:

- pre-interruption FM state: Phase A, candidate builder, FM wrapper, three
  cloud-init inputs, candidate, runtime projection, EB receipt, EE receipt, and
  two Python bytecode cache files attributable to candidate production;
- continuation FM state: canonical QEMU argv, one-shot launcher, Phase B,
  Phase C, Phase D, and this G48 report; and
- physical bounded state: `/tmp/g77_256fm/checkout`, one overlay, and one seed.

No tracked file was modified; the complete repository delta remains one
untracked FM evidence namespace. No file was staged, committed, pushed,
cleaned, reset, stashed, merged, or cherry-picked.

Unchanged subsystems:

- all committed source/runtime modules, constitutional artifacts, DU/EB/EE/EX
  validators, historical FF/FI/FJ evidence, provider integrations, P12, and
  production routing.

API compatibility:

- production API delta 0; common contract delta 0; parallel flow delta 0.

Boundary preservation:

- one candidate, one materialization, one VM preparation, zero boots,
  executions, operational effects, retries, repairs, replays, or E05 credit.

Unrelated pre-existing changes:

- None observed. The discovered bytecode cache files and all other untracked
  bytes are timestamp- and namespace-consistent with the interrupted FM work.

## Constitutional Metrics

- overall project progress: `ESTIMATED`, total 60-70%;
- constitutional health: `PASS`, evidence-bound and limitation-visible;
- shadow automation: Human-triggered preparation/validation only;
- frontier distance: PREBOOT_READY; separate Human operational authorization
  required; 12/18 E05 obligations remain;
- governance efficiency: EX 17/17 and authority 18 reused, reconstruction 0;
- candidate capability: static FK-bound WRONG_ATTEMPT preboot asset only;
- cross-account state reuse: PASS; reconstruction 0; generation restarts 0;
- preparation overhead: 1 candidate, 1 materialization, 1 VM preparation;
- worktree orchestration overhead: 1 FM namespace, 1 bounded tmp root, 1
  detached checkout; and
- overengineering risk: `ESTIMATED__LOW`, no duplicated common control plane.

## Token / Session Benchmark

Previous session reported 51,520/258K context used, 80% context remaining, 0%
5h remaining, 69% 7d remaining, and 12m25s observed work time. The continuation
session ID is `01a04ca2-843d-7322-88b7-99763bc2be63`; its `/status`, context
usage, 5h/7d usage, billed tokens, monetary cost, and total elapsed time were not
available and were not inferred. Consequently prompt-context reuse ratio,
LLM-cost reduction ratio/LCRR, and numeric SPCE handoff efficiency/SHER are
`NOT_MEASURED`; structural reuse is evidenced by zero reconstruction and zero
DU/EB/EE reruns.

# 6. Certification Verdict

PASS__G77_256FM_FRESH_FK_BOUND_WRONG_ATTEMPT_ASSET_PREBOOT_READY__CROSS_ACCOUNT_STATE_REUSED__NO_OPERATIONAL_EXECUTION__E05_UNCHANGED__HUMAN_REVIEW_REQUIRED
