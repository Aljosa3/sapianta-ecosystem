# G31-20F Disposable Repository-Scope Grounding Fixture Contract

## Verdict

`G31_DISPOSABLE_REPOSITORY_SCOPE_GROUNDING_AND_LIVE_WORKER_PATH_OPERATIONAL`

The smallest existing Repository Cognition fixture was identified, two general
fail-closed defects in its canonical owner were repaired, and one disposable
live AiCLI call completed the continuous governed-development, grounding,
CODEX activation, capture, and governance/policy/lineage-validation path.

The authentic Worker output did not contain the requested patch. It returned a
bounded downstream-task description and explicitly stated that it had not
inspected the files or generated a change. The output remains unaccepted;
canonical `RESULT_VALIDATED` does not evaluate or prove task-outcome
satisfaction.

## Baseline

- Parent HEAD: `c3dd9571f88e0c10dae738df865d039601091152`
- Parent subject: `test(governance): re-audit governed development routing`
- Nested `sapianta_system` HEAD:
  `31522024b38bc08a60ea2152122bc2b399e1235e`
- Nested worktree: clean before and after
- Protected hash baseline: unchanged G31-20E values

## Canonical Owners

| Responsibility | Existing owner | Canonical symbol |
|---|---|---|
| Project-goal/capability interpretation | Platform Core Project Services | `discover_candidate_capabilities`; `goal_mapping_from_workspace` |
| Capability vocabulary | Platform Core Project Services | `CAPABILITY_CATALOG` |
| Implementation discovery | Capability Audit / Repository Cognition | `capability_audit_runtime.detect_capabilities`; `_key_from_runtime` |
| Test discovery | Capability Audit / Repository Cognition | `detect_capabilities`; `_key_from_test` |
| Exact implementation/test pairing | Repository-Scope Grounding | `ground_approved_durable_work_repository_scope` |
| Grounding artifact validation | Repository-Scope Grounding | `validate_approved_durable_work_repository_scope_grounding` |
| Content/symbol/layer evidence | Repository-Scope Grounding | `_target_evidence`; `_observe_target`; `_validate_target_evidence` |
| Duplicate/ambiguity rejection | Repository-Scope Grounding | exact `matching` and `materially_ambiguous` checks |
| Grounded execution review | Existing G31-08 binding | `bind_grounded_worker_request_to_execution_authorization_review` |
| Approval and activation transport | AiCLI, non-authoritative | `run_reference_uhi_session` |

No new manifest, registry, artifact family, schema, approval mechanism, or
Repository Cognition path was introduced.

## Minimum Existing Fixture Contract

The successful G31-06 fixture establishes the minimum contract:

1. A workspace containing `.git`.
2. One parseable implementation under `aigol/runtime/**/*.py`.
3. One parseable focused test under `tests/**/test_*.py`.
4. Runtime and test filenames normalizing to the same capability key.
5. A request resolved by the existing capability catalog to that exact key.
6. Exactly one implementation path and exactly one test path for that key.
7. Targets inside the workspace and outside immutable L0/L1 layers.
8. Content, symbol, mutation-layer, payload, approval, and Replay hashes that
   reconstruct unchanged.

The minimum live fixture is:

```text
.git/
aigol/runtime/human_interface.py
tests/test_human_interface.py
```

The request phrase `human interface` resolves through the existing catalog to
`human_interface`. `_key_from_runtime` maps `human_interface.py` to the same
key, and `_key_from_test` removes `test_` from `test_human_interface.py`.
No additional metadata file is required.

Deterministic lineage:

```text
human-interface improvement goal
-> human_interface
-> aigol/runtime/human_interface.py
-> human_interface
-> tests/test_human_interface.py
-> bounded proposed-change request
```

## Previous Generic Rejection

The previous `calc.py` request correctly resolved to `general_project_goal`.
That key did not equal an exact Repository Cognition implementation/test key,
so the empty match set had to remain
`CANONICAL_REPOSITORY_SCOPE_UNRESOLVED_FAILED_CLOSED`.

The new tests preserve that behavior. No generic-goal fallback or filename
inference was added.

## Proven Production Defects and Repair

The existing owner already rejected more than one implementation path, but it
accepted more than one same-key test path. This contradicted its own exact-pair
contract and could broaden focused-test scope.

The validator also verified content in a supplied workspace without comparing
that workspace to the artifact's bound `workspace_root`. An identical second
workspace could therefore satisfy content validation across sessions.

The bounded repair:

- rejects a match unless it contains exactly one implementation and exactly
  one test;
- compares the supplied workspace path to the bound `workspace_root` and fails
  closed as cross-session before accepting the artifact.

No selection score, catalog entry, filename exception, or fixture-specific
production branch was added.

## Grounding Truth Table

| Fixture/evidence state | Canonical result |
|---|---|
| Generic `general_project_goal` | failed closed |
| One `human_interface` implementation and matching test | grounded |
| Missing implementation | failed closed |
| Missing test | failed closed |
| Multiple implementations | ambiguous; failed closed |
| Multiple same-key tests | ambiguous; failed closed |
| Implementation/test key mismatch | failed closed |
| Source content changed after grounding | stale/substituted; failed closed |
| Identical evidence supplied from another workspace | cross-session; failed closed |
| Capability substituted | failed closed |
| Target substituted | failed closed |
| Worker decision attempted before failed grounding | one proposal approval only; zero process starts |

## Changed Surface

| Path | Purpose |
|---|---|
| `aigol/runtime/approved_durable_work_repository_scope_grounding.py` | Exact-one-test ambiguity rejection and bound workspace-root validation |
| `tests/test_g31_20f_disposable_repository_scope_grounding_fixture_contract.py` | Twelve exact fixture, failure, tamper, session, and no-Worker tests |
| `docs/governance/G31_20F_DISPOSABLE_REPOSITORY_SCOPE_GROUNDING_FIXTURE_CONTRACT.md` | This report |

Production change count: **8 added, 1 removed, net +7 lines** in one existing
canonical owner. No nested-repository file changed.

## Validation

| Validation | Result |
|---|---|
| Targeted `py_compile` | passed |
| G31-20F focused fixture contract | `12 passed in 1.19s` |
| G31-20F plus canonical G31-06 grounding | `43 passed in 3.59s` |
| G31-17B through G31-20F regression | `72 passed in 173.67s` |
| Explicit-root CLI/provider/continuity group | `72 passed in 0.65s` |
| Governance conformance tests | `5 passed in 0.03s` |
| Governance engine | `PARTIALLY_CONFORMANT`; 18 passed, 2 known hook drifts, 0 critical violations |
| Complete suite | `6465 passed, 4 skipped in 448.84s` |
| Parent `git diff --check` | passed |
| Nested `git diff --check` | passed |

The known hook drifts remain visible and were not reframed as full conformance.

## Single Live Confirmation

### Disposable boundary and preflight

- Workspace: `/tmp/g31-20f-live-bRY3ZP/workspace`
- Runtime root: `/tmp/g31-20f-live-bRY3ZP/runtime`
- Raw request: `175` characters
- Canonical final request: `195/240` characters
- Selected route: `GOVERNED_DEVELOPMENT_RUNTIME`
- Development score: `71`; Platform Knowledge score: `55`
- `summary_admissible=true`
- Preflight: `SYNTHESIS_PREFLIGHT_READY`
- Preflight hash:
  `sha256:51a95fae29b4d900cf95bb7517c3e3c3afaaf29f129534458166d0cc9a1adf6c`
- Final request SHA-256:
  `9bfa3195d16ecdbf672fc7b30f65ab6afb5dd35122bb3f62e613cea45bcd676f`

### Routing and grounding

| Field | Value |
|---|---|
| Governed-development route selected | true |
| Grounding status | `CANONICAL_REPOSITORY_SCOPE_GROUNDED` |
| Canonical capability | `human_interface` |
| Implementation capability count | `1` |
| Test capability count | `1` |
| Implementation/test pair count | `1` |
| Implementation target | `aigol/runtime/human_interface.py` |
| Focused test target | `tests/test_human_interface.py` |
| Grounding artifact hash | `sha256:004d6d6ec768c72446e8e3ab889ba84bda2a3ed0a474c1f78013c1bd6cf24422` |
| Cognition snapshot hash | `sha256:6a1f824909eeee09d277e5cc80b985d85349233c2c63fc178ec65f23e34e6e04` |
| Grounding evidence hash | `sha256:ca0350af22bf7b949aec46003a5415b32c9f933bed8db37b7568c3c8193803b7` |

### Transport, capture, and validation

| Field | Value |
|---|---|
| Human decision count | `3` |
| Process start count | `1` |
| Transport status | `EXECUTION_ACCEPTED` |
| Return code | `0` |
| Timed out | false |
| Fixed command | `codex exec <bounded_prompt>` |
| Shell | false |
| Timeout | `60` seconds |
| Receipt | `CODEX-EXECUTION-RECEIPT-be1e891d6df91e721273ff84` |
| Duration | `16.706968` seconds |
| Stdout bytes | `1972` |
| Stdout SHA-256 | `2158195ca659923ba019414df89792025f24088cabc34796e3c09ca2df62d5f4` |
| Stdout truncated | false |
| Authentic Worker output | true |
| Semantic capture | true; count `1` |
| Validation performed | true; count `1` |
| Validation status | `RESULT_VALIDATED` |
| Canonical validation meaning | `GOVERNANCE_POLICY_AND_LINEAGE_VALIDATION_ONLY` |
| Task-outcome satisfaction evaluated | false |
| Task-outcome satisfied | false |
| Result accepted | false |
| Repository mutated | false |
| Provider invoked | false |
| Automatic retry | false |
| Additional Worker process | false |
| Commit created | false |

The adapter's canonical dispatch contract emits `EXECUTION_ACCEPTED` only for
`returncode == 0`; its timeout branch emits `EXECUTION_TIMEOUT`, return code
`124`, and `timed_out=true`. Therefore this accepted receipt proves return code
zero and no timeout without reconstructing raw output after the in-memory call.

### Replay families

| Family | Count | Replay identity/hash |
|---|---:|---|
| Operational turn | 1 | `sha256:3c923468da5e64dd3296c4596b1f366ed331d129b7d7f99b49ae3144b8cc4c9b` |
| Router response | 1 | `sha256:4e4c6f689fbf313faed58102522cd576c8e308d784849eb07d0886d533c060a8` |
| Grounding | 2 | returned wrapper `sha256:6e56bc355ccaef0e9c97b175e58dbe0d04b7396e5af20698ef34128e20e307c8` |
| Execution review | 2 | artifact `sha256:e03fbbc96867a072959814022dac3799c655bd0b08fadc74f1ebc26bd1fca42f` |
| CODEX activation | 3 | `sha256:248035284cb3a439d8be50d7a7af27ec28a4ff62d382ab2f63a78ceb1a6fdc82` |
| G31-18 capture | 4 | `sha256:7adf195249784ff38ef95a0adf420382b7ac237ac88af4bd35d643238e796053` |
| G31-20 validation | 4 | `sha256:0f0986bbf9eed5a0632b723250814650d6cbe4c025bfd8883b5057c1e41fe398` |

Capture bound Worker-output artifact hash:
`sha256:a8691b2f7cabdca63e6e6baf76b3f3bbe62c029e0572add7dce9f250a059960d`.
The validation semantic byte length and SHA-256 exactly equal the transport
stdout values.

### Observed but unaccepted Worker output

The authentic output began:

> Prepared a bounded downstream task for review; no handoff or execution occurred.

It described a bounded task and ended by stating that the files were not
accessed and a proposed change was not generated or tested. It therefore did
not satisfy the requested patch outcome. It was not rewritten, repaired,
applied, accepted, or described as task-complete. No retry was performed.

## Hash Preservation

All protected hashes were equal at task start, after focused tests, after the
complete suite, and after the live confirmation.

| Protected path | SHA-256 before and after |
|---|---|
| `diagnostic_evidence.json` | `a626a69a8020bc730876119c52701a94de9ab6e4772cc64c1f5d017296650203` |
| `governed_return.json` | `e82f47c0c13678725993b21e2af2e0437edccaed324f861a7b58e77d7f8e787d` |
| `lineage.json` | `07b95505521e70f51cdddecc1057fd3a208b198445693c9a8da1e996df5799dd` |
| `provider_stderr.txt` | `d47a06d59aba2814c3fb7460049fc2ccbfc834196c956d6c6558e8be8b079e24` |
| `provider_stdout.txt` | `a73a499e2e9133c03d7babfd5c4dec7967f31e2bfb354ea9dd41df0a15c08cb3` |
| `governed_returns.jsonl` | `dbc7b63f2a17c50c43bbb4fde4f44c1dbae8d25d550fb6b4d4daa14e17126161` |
| `WORKER_INVOCATION_ARTIFACT_V1` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `WORKER_INVOKED` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `invocation` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

Disposable source hashes were also unchanged:

| Source | SHA-256 before and after |
|---|---|
| `aigol/runtime/human_interface.py` | `8b2c7f9f90f055d8c327229e73e75ca12ad4b3befafd68ab529cbaf031dc5957` |
| `tests/test_human_interface.py` | `0b933e9887972a00dbc683266a76998a8e39faea3b172793f73df78b401ed946` |

No `codex exec` process remained after the call.

## Git Status and Commit Commands

The parent retains the six pre-existing modified evidence paths and three
pre-existing untracked root markers. G31-20F adds one production modification,
one focused test module, and this report. Nested status remains clean.

Exact staging and commit commands excluding every protected path:

```bash
git add \
  aigol/runtime/approved_durable_work_repository_scope_grounding.py \
  tests/test_g31_20f_disposable_repository_scope_grounding_fixture_contract.py \
  docs/governance/G31_20F_DISPOSABLE_REPOSITORY_SCOPE_GROUNDING_FIXTURE_CONTRACT.md
git commit -m "fix(governance): enforce exact repository cognition pairing"
```

No commit was created by this task.

## Progress and Recommended Next State

Evidence-scoped whole-project progress is **92.0%**. The complete governed path
from a genuine request through unique repository grounding, three decisions,
one real CODEX process, authentic in-memory capture, and canonical validation
is operational. The remaining semantic gap is now explicit: governance,
policy, and lineage validation does not determine whether Worker output
satisfies the requested engineering outcome.

Recommended next state:

`G31_WORKER_OUTPUT_TASK_OUTCOME_SATISFACTION_AUDIT_REQUIRED`

That phase should first identify an existing canonical owner for comparing
authentic Worker output with the approved objective and requested output
contract. It must not reinterpret `RESULT_VALIDATED`, accept this live output,
or add an AiCLI-owned result judge.
