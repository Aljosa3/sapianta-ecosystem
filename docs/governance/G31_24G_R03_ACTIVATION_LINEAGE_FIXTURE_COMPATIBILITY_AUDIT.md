# G31-24G-R03 — Activation-Lineage Fixture and Candidate Compatibility Audit

## Baseline and classification

Baseline branch: `master`.

Baseline HEAD: `ba787435b2a6bd04b5e892b55d600519ca070053` (`feat(governance): bind accepted result to replayed candidate`).

The tracked, committed R01 report contains:

`G31_V2_ACCEPTED_RESULT_TO_EXISTING_FILE_CANDIDATE_PROVENANCE_BINDING_OPERATIONAL`

Root-cause classification:

`R01_CANDIDATE_RUNTIME_CONTRACT_DRIFT`

Plain-language conclusion: R01's candidate integration reads `.lineage` from the raw result of `activate_bounded_codex_worker`.  That producer does not, and at the R01 baseline did not, return a `lineage` field.  The canonical activation binding reconstructor is the owner that reconstructs and returns lineage.  Therefore the R01 caller and test fixture use an unavailable shape; this is not a missing fixture setup and not an R02 regression.  The R01 operational certification is inconsistent with the committed call path.

## Exact failure

All three tests in `tests/test_g31_24g_r01_existing_file_candidate_provenance.py` fail before candidate construction:

```text
KeyError: 'lineage'
runtime["codex_worker_activation_capture"]["lineage"]["grounding"]
```

The same raw-capture access appears in the committed R01 AiCLI production edge at `aigol/cli/aicli.py:296` and `:302`.  The candidate owner is not entered, no V3 decision is entered, and no authorization, Worker request, command, patch, or source mutation is reached.

## Contract and caller trace

1. `aigol/cli/aicli.py:_record_contextual_worker_activation_decision` calls `activate_bounded_codex_worker` and stores its raw return as `runtime_result["codex_worker_activation_capture"]`.
2. `aigol/runtime/codex_worker_activation_binding_runtime.py:activate_bounded_codex_worker` reconstructs lineage privately for validation, then returns an activation capture containing review, approval, authority, request, receipt, dispatch, Replay reference, workspace, and truth fields.  It does not return `lineage`.
3. `reconstruct_codex_worker_activation_binding` is the public revalidation owner.  It reconstructs the same lineage and returns `{ "lineage": ... }` only in its reconstruction result.
4. Downstream established owners, including disposable validation and task-outcome review, call that reconstruction owner before reading `activation["lineage"]["grounding"]`.
5. R01 instead added direct raw-capture accesses in AiCLI and the three-test fixture before it calls `create_g31_accepted_existing_file_mutation_candidate`.

The committed baseline activation source and blame show the raw return shape predates R01; R01 did not add `lineage` to the activation producer.  R01 therefore introduced an incompatible caller assumption in the candidate integration rather than observing a new runtime requirement.

## R02 comparison

The uncommitted R02 diff changes only `aigol/runtime/human_decision_runtime.py` and adds its isolated V3 test/report.  It does not change AiCLI, the candidate owner, activation production code, the R01 fixture, activation hashes, activation Replay, or activation state.  V3 invokes the candidate reconstructor only when its own new public function is called; AiCLI has no V3 caller.  R02 cannot cause this pre-candidate failure.

R02 may be committed unchanged with respect to this failure.  It truthfully documents the R01 fixture failure and does not broaden authority or make mutation reachable.  R01 must be separately corrected and re-certified before relying on its conversational candidate path as operational evidence.

## Smallest safe next action

Implement a separate, bounded R01 compatibility repair: at the candidate call edge, obtain repository grounding only through `reconstruct_codex_worker_activation_binding` using the exact existing activation capture, governed execution capture, execution candidate capture, session root, and workspace.  Use its reconstructed `lineage["grounding"]`; do not add optional lineage, manufacture a dictionary, or alter activation/candidate authority.  Update only the R01 caller/fixture evidence necessary for that canonical reconstruction, then rerun the R01 candidate suite.  Keep R02 unchanged and stop before V3 is bound to authorization.

## Validation and governance

Already-run complete R01 focused file at this same HEAD and R02 worktree state: 3 failed, 0 passed, all with the exact pre-candidate `KeyError` above (287.68s).  That one complete file run covers the three exact failing tests.

Current audit validation:

- `tests/test_g31_24g_r02_human_mutation_decision.py` — 3 passed.
- `tests/test_g31_17b_governed_execution_to_codex_worker_activation_binding.py::test_transport_diagnostics_are_reconstructed_and_tamper_evident` — 1 passed; it proves the reconstruction owner reconstitutes activation lineage and detects tampering.
- `py_compile` passed for candidate, human-decision, AiCLI, and activation modules.
- Parent and all nested `git diff --check` checks passed.

The prior R02 Governance result remains: `PARTIALLY_CONFORMANT`, 18 checks passed, 2 pre-existing hook mismatches, and 0 critical violations.

No runtime behavior, tests, production code, source repository content, authorization, Worker, Provider, command, patch owner, or mutator was changed or invoked by this audit.  The only audit change is this document; R02 files remain unmodified evidence.

## Git status and next state

Parent status retains the protected pre-existing runtime dirt plus uncommitted R02 files and this untracked audit document.  `sapianta-domain-credit`, `sapianta_system`, and `sapianta-domain-trading` are clean.

Next state:

`G31_24G_R03_R01_ACTIVATION_RECONSTRUCTION_COMPATIBILITY_REPAIR_REQUIRED`
