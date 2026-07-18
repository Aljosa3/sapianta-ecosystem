# G31-20C Live Handoff Synthesis-Bound Repair and Validation Confirmation

## Verdict

`G31_HANDOFF_SYNTHESIS_PREFLIGHT_REPAIR_OPERATIONAL_LIVE_CONFIRMATION_FAILED`

The synthesis-bound repair is operational, and the single disposable CODEX
execution completed through authentic in-memory result capture and canonical
semantic validation. The combined confirmation nevertheless fails its complete
evidence boundary because six protected `.runtime` paths drifted during the
required complete-suite validation. They were not reverted or otherwise
modified after the drift was detected.

## Baseline

- Parent HEAD: `2c714de69d2383bf0843a577930c1166832dd83d`
- Parent subject: `docs(governance): record blocked live in-memory Codex validation`
- Required ancestor: `53945124d5b6f807398d894d099a126abf32d7e9 feat(governance): bind captured Codex output to semantic validation`
- Nested `sapianta_system` HEAD: `31522024b38bc08a60ea2152122bc2b399e1235e`
- Nested worktree: clean before and after

## Canonical Owner and Repair

The existing owners remain unchanged:

- Prefix owner and synthesis caller:
  `aigol/runtime/codex_worker_activation_binding_runtime.py`
- Canonical final-request owner:
  `sapianta_system.runtime.codex_synthesis.synthesize_governed_codex_task`
- Canonical 240-character admission contract:
  `sapianta_system/runtime/codex_synthesis/governed_codex_task_response.py`
- Non-authoritative rendering and approval orchestration:
  `aigol/cli/aicli.py`

The repair adds one activation-owned preflight that calls the existing
canonical task-request, task-synthesis, and handoff functions. It does not
truncate, summarize, rewrite, or independently synthesize the request. The
exact prefixed request, synthesis identities, handoff, character counts, and
SHA-256 are computed before the first approval summary is presented.

The preflight hash and exact final-request hash are bound into the activation
review. The third approval is bound to that review and repeats both hashes.
Activation reconstructs lineage, recomputes the same canonical preflight, and
rejects any difference before dispatch. The execution request then consumes
the exact handoff produced by that verified preflight.

Invalid preflight evidence reports zero human decisions and zero process
starts. AiCLI renders exact counts before any approval prompt and remains
non-authoritative. Injected runtime runners that cannot reach the production
G31 activation owner do not receive this activation-specific preflight.

## Changed Surface

| Path | Purpose | Added | Removed |
|---|---|---:|---:|
| `aigol/runtime/codex_worker_activation_binding_runtime.py` | Canonical synthesis preflight, verification, review/approval hash binding, exact handoff reuse | 112 | 11 |
| `aigol/cli/aicli.py` | Pre-approval orchestration, rendering, evidence propagation | 74 | 6 |
| `tests/test_g31_20c_codex_synthesis_preflight.py` | 220/221/234, substitution, no-process, and hash-binding coverage | 164 lines | new file |
| `docs/governance/G31_20C_LIVE_HANDOFF_SYNTHESIS_BOUND_REPAIR_AND_VALIDATION_CONFIRMATION.md` | This report | report | new file |

Production change count: **186 added, 17 removed, net +169 lines** across two
existing production files. No nested-repository file changed.

## Boundary Truth Table

| Raw characters | Prefix | Final characters | Maximum | Within bound | Approval eligibility | Process eligibility |
|---:|---:|---:|---:|---|---|---|
| 220 | 20 | 240 | 240 | true | eligible | eligible after all three decisions |
| 221 | 20 | 241 | 240 | false | blocked with zero decisions | blocked |
| 234 | 20 | 254 | 240 | false | blocked with zero decisions | blocked |

Focused tests also reject prefix substitution, limit substitution, raw/final
count substitution, post-preflight request substitution, and mismatched
preflight-to-review/approval/dispatch hashes. Existing cross-session and
duplicate-destination activation checks remain in force.

## Validation

| Validation | Result |
|---|---|
| Targeted `py_compile` | passed |
| New G31-20C boundary module | `9 passed in 15.21s` |
| G31-17B/18/20/20C regression | `46 passed in 155.43s` |
| Five compatibility regressions plus G31-20C | `14 passed in 15.32s` |
| Governance conformance tests | `5 passed in 0.03s` |
| Governance engine | `PARTIALLY_CONFORMANT`; 18 passed, 2 known hook drifts, 0 critical violations |
| Complete suite, first run | `5 failed, 6434 passed, 4 skipped`; compatibility scope identified |
| Complete suite after repair | `6439 passed, 4 skipped in 427.94s` |
| Parent `git diff --check` | passed |
| Nested `git diff --check` | passed |

The known governance-engine hook drift remains visible and was not changed or
reframed as full conformance.

## Disposable Live Confirmation

- Workspace: `/tmp/g31-20c-live-O1slLN/workspace`
- Runtime root: `/tmp/g31-20c-live-O1slLN/runtime`
- Raw request characters: `162`
- Prefix characters: `20`
- Final request characters: `182`
- Maximum characters: `240`
- Preflight: `SYNTHESIS_PREFLIGHT_READY`
- Preflight hash: `sha256:29562e66f9f3802ef8aaa6a0eb6861ccd9fa294fdf040e3d9c15a32627e11279`
- Final request SHA-256: `01ec9edea1f5aed5074d800df9527352dcf4af42847352dc98d107312be0a0dc`
- Review binding: true
- Approval binding: true
- Execution handoff exact match: true

| Live field | Result |
|---|---|
| Human decision count | `3` |
| Process start count | `1` |
| Transport status | `EXECUTION_ACCEPTED` |
| Return code | `0` |
| Timed out | `false` |
| Shell | `false` |
| Timeout | `60` seconds |
| Fixed command prefix | `codex exec` |
| stdout bytes | `1140` |
| stdout SHA-256 | `42b25e4ac566825fc7fe7772d9d5de9da1449fdabe93ab1087b47123af7ec11e` |
| stdout truncated | `false` |
| stderr bytes | `3136` |
| stderr SHA-256 | `8130c572bd3c383780f0ef7c4211355eeff3a97693dfb756c0f2fd27816d25d6` |
| stderr truncated | `false` |
| Authentic Worker output present | `true` |
| Semantic Worker result captured | `true` |
| Capture count | `1` |
| Exact transport-to-capture bytes/hash | `true` |
| Semantic validation performed | `true` |
| Canonical validation call count | `1` |
| Result validated | `true` |
| Canonical validation status | `RESULT_VALIDATED` |
| Validation count | `1` |
| Exact capture-to-validation bytes/hash | `true` |
| Provider invoked | `false` |
| Automatic retry | `false` |
| Additional Worker process | `false` |
| Result accepted | `false` |
| Repository mutated | `false` |
| Commit/deploy/release | `false` / `false` / `false` |

The authentic stdout did not contain the disposable known-file marker. This is
preserved as a visible task-specific limitation: the canonical semantic
contract validated the authentic bounded output, but this run does not prove
that CODEX echoed the known file's exact text. No output was rewritten, no
stderr was substituted, and no retry was performed.

## Replay Evidence

| Family | Count | Identity | Replay hash |
|---|---:|---|---|
| Activation | 3 | `CODEX-EXECUTION-RECEIPT-77fa59ac3a4596341a467596` | `sha256:26294a64785abe772a6d7b30e228d29adaaa03d8f9ed7c69de64a1098b55dff4` |
| Capture | 4 | `sha256:b7738d3330fa2b82ddfb2155e1b489a8e7dd189f5e01cc81560b7e0b1546f998:AUTHORIZATION:WORKER-SELECTION:ASSIGNMENT:DISPATCH:INVOCATION:CODEX-EXECUTION-RECEIPT-77fa59ac3a4596341a467596:RESULT-CAPTURE` | `sha256:777f7912dc88285c369294553547d91e86b811d56f3d4b09876b93fb71cec272` |
| Validation | 4 | `sha256:b7738d3330fa2b82ddfb2155e1b489a8e7dd189f5e01cc81560b7e0b1546f998:AUTHORIZATION:WORKER-SELECTION:ASSIGNMENT:DISPATCH:INVOCATION:CODEX-EXECUTION-RECEIPT-77fa59ac3a4596341a467596:RESULT-CAPTURE:SEMANTIC-VALIDATION:42b25e4ac566825fc7fe7772` | `sha256:13511633c0124bf35b2487f3c74e66e6c47f745b40500183727bca1425ee6c64` |

Capture artifact hash:
`sha256:1b5da004b604c5588abc6033f4a2a1fe3b40a4321224987765c80debb4709834`.
Worker-output hash:
`sha256:fc217bf5f4fc59a7893f1872c420f8bd67a76397f85cbc643589e43476675344`.
Worker-output payload hash:
`sha256:3713eabb54d9d8bb250e9d5a73eaa2112ec7ab872458dfd5afb98aa6e207f5cb`.
Validation artifact hash:
`sha256:4b2fc6fa92c7b19ee2123f8f2c3a3b58bc76844ff5b1ecdc05957c7fc0d31d1e`.

All three Replay families reconstructed successfully. No `codex exec` process
remained after reconstruction.

## Disposable Hashes

| Path | Before | After |
|---|---|---|
| `aigol/runtime/human_interface.py` | `3692fbc6d8f9f76f5afbc65e8c5f46aa4fbae6f36849ba005293ba7b0ad89a75` | same |
| `tests/test_human_interface.py` | `6cb9728c57aa10f995cb6dcb1508c0e8ddb5897a94b4f7895872db47c7a743d4` | same |
| `KNOWN_INPUT.txt` | `8a72cf1ca4a14e4ac2e6dd796fdd5dc06ac08b1b037dd2c5a927148edbe4271f` | same |

## Protected-Path Hash Audit

The three root markers remained unchanged. The six `.runtime` paths did not.

| Protected path | Before SHA-256 | After SHA-256 | Result |
|---|---|---|---|
| `diagnostic_evidence.json` | `881710ee8c0166769c83ec94e25a67961746a4613ec5206180c945e84b2a3283` | `a626a69a8020bc730876119c52701a94de9ab6e4772cc64c1f5d017296650203` | changed |
| `governed_return.json` | `1d73d6d78572de9f689e3e5e1b16b97332af6164cf458c13f5858ca70ed0a0c9` | `e82f47c0c13678725993b21e2af2e0437edccaed324f861a7b58e77d7f8e787d` | changed |
| `lineage.json` | `c5f6adff859182c28441fe4ea5fd3b361a94845130863a677eed3d45ccdd3c5e` | `07b95505521e70f51cdddecc1057fd3a208b198445693c9a8da1e996df5799dd` | changed |
| `provider_stderr.txt` | `0a2a0a25196af82e2dcbe1865d128df82b471515813352dbceaf0425f5be6f9f` | `d47a06d59aba2814c3fb7460049fc2ccbfc834196c956d6c6558e8be8b079e24` | changed |
| `provider_stdout.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | `a73a499e2e9133c03d7babfd5c4dec7967f31e2bfb354ea9dd41df0a15c08cb3` | changed |
| `.runtime/aigol/ledger/governed_returns.jsonl` | `bfa09ec044db2cfda7df97b236a826d4684e62a839a472202d8e5abda6c09c60` | `dbc7b63f2a17c50c43bbb4fde4f44c1dbae8d25d550fb6b4d4daa14e17126161` | changed |
| `WORKER_INVOCATION_ARTIFACT_V1` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | same | unchanged |
| `WORKER_INVOKED` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | same | unchanged |
| `invocation` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | same | unchanged |

All six changed paths have modification time `2026-07-18 05:11:48 +0200`.
Their content records an unrelated `codex --version` Provider diagnostic,
including a CODEX extension version change from `0.137.0-alpha.4` to
`0.144.0-alpha.4`. This is not the disposable G31 execution, whose Provider
flag is false and whose runtime root is under `/tmp`. The drift was observed
after the required full-suite run. No isolating rerun was performed because the
task permits exactly one live confirmation and prohibits altering these paths.

## Git Status and Commit Handoff

- Parent HEAD remains `2c714de69d2383bf0843a577930c1166832dd83d`.
- Nested HEAD remains clean at `31522024b38bc08a60ea2152122bc2b399e1235e`.
- Production task files: two modified parent files.
- Task tests: one new parent file.
- Task report: one new parent file.
- Protected modified/untracked paths remain unstaged and excluded.
- No commit was created.

Exact task-only commit commands, not executed:

```bash
git add aigol/cli/aicli.py \
  aigol/runtime/codex_worker_activation_binding_runtime.py \
  tests/test_g31_20c_codex_synthesis_preflight.py \
  docs/governance/G31_20C_LIVE_HANDOFF_SYNTHESIS_BOUND_REPAIR_AND_VALIDATION_CONFIRMATION.md
git commit -m "fix(governance): preflight bounded Codex synthesis"
```

## Progress and Recommended Next State

Evidence-scoped whole-project progress is **90.5%**. The preflight repair and
the complete live in-memory transport/capture/validation path are operational,
but protected-evidence isolation is not yet proven and the known-file marker
was absent from authentic stdout.

Recommended next state:

`G31_PROTECTED_EVIDENCE_ISOLATION_AND_LIVE_CONFIRMATION_REAUDIT_REQUIRED`

The next phase should identify and isolate the complete-suite path that writes
the default `.runtime/aigol` evidence destination, restore protected evidence
only under explicit human direction, and separately authorize any new live
confirmation. This report must not be upgraded to an unqualified operational
verdict without that evidence boundary.
