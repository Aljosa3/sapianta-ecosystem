# G31-20D Protected Evidence Isolation and Validation Semantics Re-Audit

## Verdict

`G31_PROTECTED_EVIDENCE_ISOLATED_LIVE_TASK_OUTCOME_UNSATISFIED`

Protected default-runtime evidence is isolated: focused tests, G31 regressions,
governance validation, the complete suite, and the single permitted re-audit
left all nine protected hashes unchanged from the new task baseline.

The single re-audit did not reach CODEX activation. Platform Core routed the
request to read-only Platform Knowledge with `summary_admissible=false`, so no
AiCLI approval, process, transport, capture, or validation occurred. No retry
was performed.

## Baseline

- Parent HEAD: `127c6fcb4236e766a3c1adf3b4cf5791da1b233d`
- Parent subject: `fix(governance): preflight bounded Codex synthesis`
- Nested `sapianta_system` HEAD: `31522024b38bc08a60ea2152122bc2b399e1235e`
- Nested worktree: clean before and after
- Protected dirty files were not reverted, deleted, staged, or otherwise
  altered.

## Isolation Leak Cause and Repair

Exact former write path:

1. Provider-success and controlled-execution tests called
   `aigol.cli.commands.execution.run_execution_handoff` with a disposable
   `workspace_path` but no `runtime_root`.
2. `run_execution_handoff` used its default `persist_return=true` and passed
   `runtime_root=None` to the existing governed-return writer.
3. `aigol.cli.commands.return_continuity.persist_governed_return_artifact`
   called `_runtime_paths(runtime_root=None, ...)`.
4. `_runtime_paths` selected `DEFAULT_RUNTIME_ROOT`, equal to
   `.runtime/aigol`.
5. The existing writer overwrote the replay evidence directory and appended
   the default ledger with the unrelated `codex --version` Provider
   diagnostic.

The repair is at the existing persistence owner. A missing `runtime_root` now
returns `PERSISTENCE_FAILED`, `fail_closed=true`, and the reason
`explicit runtime_root is required; implicit default persistence is disabled`
before `_runtime_paths`, directory creation, or evidence writing.

Existing provider and controlled-execution tests now pass explicit
pytest-owned runtime roots. No parallel evidence writer, diagnostic family,
ledger, or Replay system was added.

## Canonical Meaning of `RESULT_VALIDATED`

Inspection of `aigol/runtime/worker_result_validation_runtime.py` proves that
`RESULT_VALIDATED` checks:

- authentic result-capture Replay lineage;
- invocation, dispatch, assignment, authorization, and execution-packet
  continuity;
- Worker identity and chain continuity;
- allowed/produced output scope;
- absence of forbidden operations;
- presence and continuity of validation requirements;
- result-capture and execution authority boundaries.

It does not compare Worker output bytes with the original requested outcome or
acceptance criteria. Its canonical meaning is therefore:

`GOVERNANCE_POLICY_AND_LINEAGE_VALIDATION_ONLY`

The canonical validation and G31 bridge now expose:

```text
task_outcome_satisfaction_evaluated = false
task_outcome_satisfied = false
```

These fields are bound into canonical validation/result artifacts, Replay
hashes, reconstruction, failed-closed captures, and rendering. Substitution of
the meaning or task-outcome authority fields fails canonical artifact
verification. `RESULT_VALIDATED` was not renamed or broadened. Task-specific
correctness remains a later human review/acceptance responsibility.

## Isolation Truth Table

| Operation | Runtime root | Evidence result | Protected hashes |
|---|---|---|---|
| `codex --version` diagnostic test | explicit pytest `/tmp` root | persisted under explicit root | unchanged |
| Governed-return persistence | missing | failed closed before evidence write | unchanged |
| Focused isolation/semantics tests | explicit pytest roots | isolated | unchanged |
| G31 regressions | explicit pytest roots | isolated | unchanged |
| Complete suite | explicit pytest roots or missing-root rejection | isolated | unchanged |
| Single re-audit | explicit `/tmp/g31-20d-live-lMNMZK/runtime` | pre-runtime evidence only | unchanged |

## Validation-Semantics Truth Table

| Captured result | Governance/policy validation | Task outcome evaluated | Task outcome satisfied |
|---|---|---|---|
| Authentic output containing an expected marker | `RESULT_VALIDATED` | false | false |
| Authentic but irrelevant output | `RESULT_VALIDATED` | false | false |
| Forbidden operation | `FAILED_CLOSED` | false | false |
| Substituted validation requirements | `FAILED_CLOSED` | false | false |
| Substituted output bytes/hash | `FAILED_CLOSED` through existing G31 binding | false | false |
| Duplicate validation | `FAILED_CLOSED` | false | false |
| Cross-session lineage | `FAILED_CLOSED` through existing canonical/G31 checks | false | false |

An authentic and policy-valid result must not be described as task-complete.

## Changed Surface

| Path | Change |
|---|---|
| `aigol/cli/commands/return_continuity.py` | Reject missing persistence root before any write |
| `aigol/runtime/worker_result_validation_runtime.py` | Bind and reconstruct canonical validation meaning and false task-outcome fields |
| `aigol/runtime/codex_worker_result_to_semantic_validation_binding_runtime.py` | Preserve/render canonical meaning for G31 success and failed-closed results |
| `tests/test_g31_20d_protected_evidence_isolation_and_validation_semantics.py` | Seven focused isolation and semantics cases |
| `tests/test_aigol_cli_foundation_v1.py` | Three explicit disposable runtime roots |
| `tests/test_cli_controlled_execution_runtime_v1.py` | Twelve explicit disposable runtime roots |
| `tests/test_cli_provider_success_stabilization_v1.py` | Eleven explicit disposable runtime-root call sites |
| `docs/governance/G31_20D_PROTECTED_EVIDENCE_ISOLATION_AND_VALIDATION_SEMANTICS_REAUDIT.md` | This report |

Production change count: **45 added, 0 removed** across three production
files. The focused G31-20D test module contains 198 lines. No nested-repository
file changed.

## Validation Results

| Validation | Result |
|---|---|
| Targeted `py_compile` | passed |
| Focused G31-20D isolation/semantics | `7 passed in 20.40s` |
| Canonical Worker validation plus G31-17B through G31-20D | `71 passed in 175.43s` |
| Explicit-root CLI/provider/continuity group | `72 passed in 0.68s` |
| Governance tests | `5 passed in 0.03s` |
| Governance engine | `PARTIALLY_CONFORMANT`; 18 passed, 2 known hook drifts, 0 critical violations |
| Complete suite | `6446 passed, 4 skipped in 447.36s` |
| Parent `git diff --check` | passed |
| Nested `git diff --check` | passed |

The two known governance hook drifts remain visible and were not reframed as
full conformance.

## Single Live Re-Audit

- Workspace: `/tmp/g31-20d-live-lMNMZK/workspace`
- Runtime root: `/tmp/g31-20d-live-lMNMZK/runtime`
- Known marker: `SAPIANTA_G31_20D_UNIQUE_MARKER_7F3A9C`
- Raw request characters: `165`
- Canonical prefix characters: `20`
- Direct canonical final request characters: `185`
- Maximum characters: `240`
- Direct canonical preflight: `SYNTHESIS_PREFLIGHT_READY`
- Direct preflight hash:
  `sha256:1dbaf546c1efa152222fb7ec76bc548a699354aa0b634d52f22790c2a28cef79`

AiCLI/Platform Core did not admit this request to the governed development
summary. Persisted routing evidence records:

- selected service: `PLATFORM_KNOWLEDGE_RUNTIME`;
- response mode: `INFORMATIONAL`;
- `summary_admissible=false`;
- `clarification_required=false`;
- pending approval: false;
- runtime result: absent.

The request wording was classified as architectural knowledge related to a
certified Human Interface capability. The G31 synthesis preflight integrated
into AiCLI occurs only after an admissible governed implementation summary, so
it was not entered during the session.

| Required report field | Observed value |
|---|---|
| `transport_successful` | false; transport not started |
| `semantic_worker_result_captured` | false |
| `canonical_result_validated` | false; validator not called |
| `canonical_validation_meaning` | `GOVERNANCE_POLICY_AND_LINEAGE_VALIDATION_ONLY` |
| `task_outcome_satisfaction_evaluated` | false |
| `task_outcome_satisfied` | false |
| `known_marker_present` | false; no authentic stdout existed |
| Human decisions | 0 |
| Process starts | 0 |
| Provider invoked | false |
| Automatic retry | false |
| Additional Worker process | false |
| `result_accepted` | false |
| `repository_mutated` | false |
| `commit_created` | false |
| `deployed` | false |
| `released` | false |

No activation, capture, or validation Replay family exists for this re-audit.
No CODEX process remained. No second re-audit or request rewrite was attempted.

## Disposable Source Hashes

| Path | Before | After |
|---|---|---|
| `aigol/runtime/human_interface.py` | `3692fbc6d8f9f76f5afbc65e8c5f46aa4fbae6f36849ba005293ba7b0ad89a75` | same |
| `tests/test_human_interface.py` | `6cb9728c57aa10f995cb6dcb1508c0e8ddb5897a94b4f7895872db47c7a743d4` | same |
| `KNOWN_INPUT.txt` | `e61f9f9580b349bd9df941737dafad697ef54549ce49d5a3e4cb04a9bfd0435d` | same |

## Protected Hash Comparison

Every protected hash matched before focused tests, after focused and
governance tests, after the complete suite, and after the live re-audit.

| Protected path | Task-start and final SHA-256 |
|---|---|
| `diagnostic_evidence.json` | `a626a69a8020bc730876119c52701a94de9ab6e4772cc64c1f5d017296650203` |
| `governed_return.json` | `e82f47c0c13678725993b21e2af2e0437edccaed324f861a7b58e77d7f8e787d` |
| `lineage.json` | `07b95505521e70f51cdddecc1057fd3a208b198445693c9a8da1e996df5799dd` |
| `provider_stderr.txt` | `d47a06d59aba2814c3fb7460049fc2ccbfc834196c956d6c6558e8be8b079e24` |
| `provider_stdout.txt` | `a73a499e2e9133c03d7babfd5c4dec7967f31e2bfb354ea9dd41df0a15c08cb3` |
| `.runtime/aigol/ledger/governed_returns.jsonl` | `dbc7b63f2a17c50c43bbb4fde4f44c1dbae8d25d550fb6b4d4daa14e17126161` |
| `WORKER_INVOCATION_ARTIFACT_V1` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `WORKER_INVOKED` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `invocation` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

## Git Status and Commit Handoff

- Parent HEAD remains `127c6fcb4236e766a3c1adf3b4cf5791da1b233d`.
- Nested HEAD remains clean at `31522024b38bc08a60ea2152122bc2b399e1235e`.
- Protected paths remain dirty/untracked exactly as found and are excluded.
- No commit was created.

Exact task-only commit commands, not executed:

```bash
git add aigol/cli/commands/return_continuity.py \
  aigol/runtime/worker_result_validation_runtime.py \
  aigol/runtime/codex_worker_result_to_semantic_validation_binding_runtime.py \
  tests/test_aigol_cli_foundation_v1.py \
  tests/test_cli_controlled_execution_runtime_v1.py \
  tests/test_cli_provider_success_stabilization_v1.py \
  tests/test_g31_20d_protected_evidence_isolation_and_validation_semantics.py \
  docs/governance/G31_20D_PROTECTED_EVIDENCE_ISOLATION_AND_VALIDATION_SEMANTICS_REAUDIT.md
git commit -m "fix(governance): isolate evidence and clarify result validation"
```

## Progress and Recommended Next State

Evidence-scoped whole-project progress is **91.0%**. Protected-evidence
isolation and canonical validation semantics are proven. A new live
transport/capture/validation result was not obtained because the sole re-audit
request was routed outside governed development before approval.

Recommended next state:

`G31_GOVERNED_DEVELOPMENT_REQUEST_ROUTING_REAUDIT_REQUIRED`

Any further live confirmation requires a new explicit authorization. It should
use a request proven by Platform Core routing tests to produce an admissible
governed implementation summary, without weakening the router or reusing this
attempt's evidence.
