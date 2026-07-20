# G31-24G-R04 — R01 Activation Reconstruction Compatibility Repair

## Verdict and baseline

Implementation verdict:

`G31_R01_ACTIVATION_RECONSTRUCTION_COMPATIBILITY_REPAIR_OPERATIONAL`

Baseline branch: `master`.

Baseline HEAD: `8924a6469e28fe888d33e81f48d108d02d275077` (`feat(governance): record replayed mutation decisions`).

The committed R03 classification is `R01_CANDIDATE_RUNTIME_CONTRACT_DRIFT`.

## Exact repair

The R01 candidate path previously read `lineage` from the raw `codex_worker_activation_capture`.  The raw result of `activate_bounded_codex_worker` deliberately has no such field.  The repair leaves that raw capture unchanged and calls the existing public `reconstruct_codex_worker_activation_binding` once, with the exact raw activation capture, governed execution capture, execution candidate capture, same session root, and workspace.  Only the validated reconstruction supplies `lineage["grounding"]` to both existing V2 candidate create/reconstruct calls.

No activation producer, artifact family, candidate schema, candidate hash, candidate Replay, decision contract, or mutation contract changed.  There is no remaining raw activation-lineage access in the repaired AiCLI candidate path or its focused fixture.

## Changed files

- `aigol/cli/aicli.py` — one local activation-binding reconstruction and one grounding projection, reused by the existing candidate create/reconstruct calls (8 additions, 2 direct-access replacements).
- `tests/test_g31_24g_r01_existing_file_candidate_provenance.py` — fixture uses the same public reconstruction and adds an explicit reconstruction-failure fail-closed case.
- This report.

The raw activation capture remains historical evidence; the passing AiCLI test explicitly verifies it still lacks `lineage`.  Reconstruction failure raises before candidate construction.  No synthetic or optional lineage is used.

## Result and authority boundary

The repaired successful state is unchanged:

```text
result_accepted = true
existing_file_mutation_candidate_created = true
human_mutation_decision_recorded = false
mutation_authorized = false
main_repository_mutated = false
```

The V3 mutation-decision owner remains uncalled.  The repair does not call filesystem-mutation authorization, a repository mutator, a patch owner, a disposable executor, a Provider, or a mutation decision.  The isolated conversational fixture retains its pre-existing single bounded Worker invocation (`runner.calls == 1`); reconstruction creates no second activation, Worker/Provider execution, command, authorization, or source write.  Source-file hashes and temporary source-worktree Git status remain unchanged in the focused R01 cases.

## Validation

- `tests/test_g31_24g_r01_existing_file_candidate_provenance.py` — 4 passed in 376.87s:
  exact candidate/reconstruction, tamper/reuse failures, AiCLI transport, and reconstruction-failure fail-closed.
- `tests/test_g31_24g_r02_human_mutation_decision.py` — 3 passed.
- Direct activation reconstruction/tamper test — 1 passed.
- Governance conformance tests — 5 passed.
- `py_compile` passed for AiCLI, activation, candidate, and R01 test modules.
- Parent and all nested `git diff --check` checks passed.

Governance engine result: deterministic, read-only, fail-closed `PARTIALLY_CONFORMANT`; 18 checks passed, 2 pre-existing hook mismatches, 0 critical violations.

No PTY workflow or source-repository mutation was run.  All focused conversational evidence used isolated temporary repositories.

## Next state

`G31_24G_R04_R01_CANDIDATE_PATH_RECERTIFIED_MUTATION_DECISION_BINDING_REQUIRED`
