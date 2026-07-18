# G31-22C Task-Outcome Criteria and Unified-Diff Contract Alignment

Date: 2026-07-18  
Verdict: `G31_TASK_OUTCOME_CRITERIA_AND_UNIFIED_DIFF_CONTRACT_ALIGNED`

## Scope and baseline

This phase aligns future pre-execution task-outcome criteria with the existing
`UNIFIED_DIFF` Worker-output contract. It does not reinterpret the completed
G31-22B review. No CODEX process, Provider, retry, patch application,
repository mutation, acceptance, commit, deployment, or release occurred.

| Baseline | Observed |
|---|---|
| parent HEAD | `c20a281790a1f483fd8333fa09ea3146d5af8027` |
| parent subject | `feat(governance): bind live Codex output to task outcome review` |
| nested `sapianta_system` HEAD | `3183bab71f8f30397c0309dd2e6d846d14a11f66` |
| nested worktree | clean |
| historic criteria | `G31_PRE_EXECUTION_TASK_OUTCOME_CRITERIA_V1` |
| future criteria | `G31_PRE_EXECUTION_TASK_OUTCOME_CRITERIA_V2` |

The parent worktree already contained the nine protected paths and an
unrelated unstaged `aigol/runtime/human_decision_runtime.py` change. They were
preserved and excluded from this phase.

## Canonical ownership audit

| Concern | Canonical owner | Finding |
|---|---|---|
| repository capability pair and grounding | `approved_durable_work_repository_scope_grounding.py::validate_approved_durable_work_repository_scope_grounding` and its reconstruction owner | Selects and binds the implementation/test capability pair and repository snapshot before activation. Grounding is scope evidence, not proof that the Worker read every file. |
| required output type | `codex_worker_activation_binding_runtime.py::_grounded_worker_execution_contract` | Projects `UNIFIED_DIFF` from the grounded request into the immutable Worker contract. |
| pre-execution task-outcome criteria | `codex_worker_activation_binding_runtime.py::_grounded_worker_execution_contract` | V2 criteria are generated before the third activation decision and included in the Worker-contract, prompt, review, approval, request, and activation identities. |
| activation reconstruction | `codex_worker_activation_binding_runtime.py::reconstruct_codex_worker_activation_binding` | Rebuilds the versioned contract and now rejects any supplied preflight or criteria substitution. |
| task-outcome review | `codex_task_outcome_human_review_runtime.py::prepare_codex_task_outcome_review`, `record_codex_task_outcome_human_decision` | Owns exact-output review, deterministic eligibility gates, and the narrow human satisfaction decision. |
| unified-diff structure | no pre-existing canonical structural validator | No suitable structural owner existed. The smallest parser is therefore private to the existing task-outcome review owner; no patch-application engine or parallel review system was added. |

Existing mutation runtimes consume already-authorized structured mutation
candidates. They are not lawful owners for evaluating a read-only proposed
diff and were not reused as a patch engine.

## Canonical relationship

Repository grounding has two relevant meanings:

1. `inspection_targets`: the files the governed prompt instructs the Worker to
   inspect;
2. `allowed_change_targets`: the maximum set of paths that a proposed patch may
   change.

Those sets are equal for the current implementation/test capability pair, but
their semantics are not. A valid unified diff:

- need not mention every grounded file;
- need not modify every grounded file;
- must change at least one grounded implementation target;
- may change only the grounded files actually needed by the repair;
- must keep every changed path inside the grounded allowed set;
- may leave a grounded focused-test target unchanged;
- must not contain a fake or empty section for an unchanged test.

A unified diff proves which paths it proposes to change. It does not prove
which unchanged paths the Worker inspected. The current canonical evidence
chain contains no structured, semantically bound file-read record. Provider or
adapter diagnostics are not a canonical task-result inspection envelope and
cannot truthfully fill that gap. V2 therefore records the inspection-evidence
gap and does not claim affirmative inspection proof. If that proof becomes a
requirement, it needs a separately audited structured execution-evidence
contract; it must not be inferred from a source-only diff.

## Exact future criteria

`G31_PRE_EXECUTION_TASK_OUTCOME_CRITERIA_V2` binds these requirements before
future execution:

1. output is a syntactically valid unified diff;
2. at least one grounded implementation target changes;
3. every changed path is within the grounded allowed target set;
4. no ungrounded path changes;
5. the requested semantic change is represented when the approved request has
   an explicit machine-checkable old-to-new form;
6. the Worker did not apply the patch;
7. task-outcome review does not claim tests passed;
8. technical quality remains subject to later patch application and test
   validation;
9. task satisfaction does not imply result acceptance;
10. task satisfaction does not authorize repository mutation.

The deterministic parser accepts ordinary `---`/`+++` unified-diff sections,
optional `diff --git` and `index` headers, valid hunks, context lines, and the
no-newline marker. It validates hunk counts and canonicalizes `a/` and `b/`
prefixes. It rejects malformed sections, no-change sections, creations or
deletions, absolute/non-POSIX/traversal paths, old/new target substitution,
and content outside the diff. Human semantic judgment remains necessary when
an authorized task does not express a conservative machine-readable
old-to-new transformation.

## Valid and invalid truth table

| Proposed result | Structural result | Future satisfaction eligibility |
|---|---:|---:|
| valid source-only diff changing the grounded implementation and leaving its grounded test unchanged | valid | eligible, subject to human review |
| valid diff legitimately changing both grounded implementation and test | valid | eligible, subject to human review |
| unchanged test represented by an empty/fake section | invalid | fail closed |
| valid hunk against an ungrounded path | structurally parseable, scope-invalid | fail closed |
| malformed header, hunk, hunk line, or count | invalid | fail closed |
| no changed file or no grounded implementation change | invalid/ineligible | fail closed |
| explicit requested semantic transformation absent | semantic-invalid | fail closed |
| absolute, traversal, backslash/non-POSIX path | path-invalid | fail closed |
| old and new headers name different targets | substituted/rename-invalid | fail closed |
| output claims tests passed before patch application | claim-invalid | fail closed |
| output claims the patch was applied | claim-invalid | fail closed |
| post-approval criteria or preflight substitution | identity-invalid | fail closed |

Output-type substitution, cross-session review, duplicate review destination,
duplicate result lineage, capture/validation/output hash substitution, and
repeated decision remain guarded by the existing activation and G31-22A
reconstruction boundaries.

## Historic G31-22B preservation

G31-22B remains governed by V1 criteria because that exact criteria version and
hash were bound before its execution. Reconstruction selects the version from
the captured preflight, while all new activations default to V2. V1 retains its
exact former field set and requirements; V2 adds new criteria and necessarily
produces new criteria, Worker-contract, prompt, request, review, approval, and
activation identities.

The retained historic evidence still records:

| Historic field | Value |
|---|---|
| criteria version | `G31_PRE_EXECUTION_TASK_OUTCOME_CRITERIA_V1` |
| criteria hash | `sha256:8ed5e586edfa7f3a523f3851c8ea0dba74349548980af2a0c4efe0a5c848067f` |
| review identity | `sha256:63d2025cd5823fa9c52d36f18489391cbc3ea39ed773600d5277e13809f33f3f` |
| review artifact hash | `sha256:6278c42378e9c5db2a5088b8270f7f43dc98858454b35a54a457a4b840683572` |
| generic human decision | `REJECT` |
| G31 task-outcome meaning | `TASK_OUTCOME_UNSATISFIED` |

Historic durable wrapper SHA-256 values were identical before and after this
phase:

| Wrapper | SHA-256 |
|---|---|
| review packet recorded | `fd7a1ceade87d82bfa79207250602dd97abab2d9f8a19742c30fe8eeaebfa01e` |
| review required recorded | `70678ab139079c5a8ed5b740fe605e8ec446822613de06bcba7ff72f577794b7` |
| human decision recorded | `017cb1c1350cbce38da1f649c1b455df50f14caf8e9be35554b33e07a2b999c4` |
| human decision returned | `8ac33e1fec77af092f6f95339e60793d0751b7ad39e668af252f12763f8b21ea` |

The historic output was not rerun, rewritten, re-reviewed, or reclassified.
The V2 source-only result would be eligible for a future human satisfaction
decision, but that prospective rule has no retroactive effect.

## Separate downstream meanings

| State | Meaning | Authority granted |
|---|---|---|
| task-outcome satisfaction | a human confirms the exact output satisfies the pre-bound proposed-diff task, after deterministic fail-closed checks | no acceptance; no mutation |
| test validation | later tests execute against an actually applied candidate patch in a separately governed transition | technical evidence only |
| final acceptance | a separate human accepts the generated content and required validation evidence | acceptance within its explicit scope only |
| repository mutation | a separately authorized mutation owner applies an approved candidate | only the exact authorized mutation |

`RESULT_VALIDATED` remains governance policy and lineage validation only. It is
not test success, technical quality, task satisfaction, acceptance, or
mutation authority.

## Changed surface

| File | Change |
|---|---|
| `aigol/runtime/codex_worker_activation_binding_runtime.py` | versioned V1/V2 pre-execution criteria, future V2 contract, exact preflight substitution rejection |
| `aigol/runtime/codex_task_outcome_human_review_runtime.py` | deterministic unified-diff observations and blockers inside the existing review owner |
| `tests/test_g31_22b_live_task_outcome_review_continuation.py` | corrected one fixture hunk count so it is a syntactically honest unified diff |
| `tests/test_g31_22c_task_outcome_criteria_unified_diff_alignment.py` | focused V2, fail-closed, identity, separation, and V1 compatibility coverage |
| this report | audit and evidence record |

Production change is **391 added and 21 removed lines** across the two existing
runtime owners. Test change is one added/one removed line in the G31-22B fixture
plus 301 physical lines in the new G31-22C test module. No nested production
line changed and no parallel artifact family, approval system, review system,
or patch engine was introduced.

## Validation

Every generated runtime in the focused tests used an explicit pytest `/tmp`
root. `RecordingRunner` supplied deterministic exact-byte fixtures; it did not
start a process.

| Validation | Result |
|---|---|
| focused G31-22C criteria/diff tests | `12 passed in 93.56s` |
| G31-22A and G31-22B focused regression during implementation | `16 passed in 140.64s` |
| aggregate G31-17B through G31-22C, including isolation and grounding | `108 passed in 428.03s` |
| complete parent suite | `6501 passed, 4 skipped in 708.50s` |
| governance conformance tests | `5 passed in 0.03s` |
| governance conformance engine | `PARTIALLY_CONFORMANT`; 18 passed, two known hook mismatches, zero critical violations; deterministic/read-only/fail-closed; report hash `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea` |
| targeted `py_compile` | passed |
| parent and nested `git diff --check` | passed |

The known root and nested pre-commit-hook drift remains visible and was neither
introduced nor concealed by this phase.

## Protected hashes

All protected SHA-256 values matched before and after:

| Protected path | Before | After |
|---|---|---|
| `diagnostic_evidence.json` | `a626a69a8020bc730876119c52701a94de9ab6e4772cc64c1f5d017296650203` | same |
| `governed_return.json` | `e82f47c0c13678725993b21e2af2e0437edccaed324f861a7b58e77d7f8e787d` | same |
| `lineage.json` | `07b95505521e70f51cdddecc1057fd3a208b198445693c9a8da1e996df5799dd` | same |
| `provider_stderr.txt` | `d47a06d59aba2814c3fb7460049fc2ccbfc834196c956d6c6558e8be8b079e24` | same |
| `provider_stdout.txt` | `a73a499e2e9133c03d7babfd5c4dec7967f31e2bfb354ea9dd41df0a15c08cb3` | same |
| `governed_returns.jsonl` | `dbc7b63f2a17c50c43bbb4fde4f44c1dbae8d25d550fb6b4d4daa14e17126161` | same |
| `WORKER_INVOCATION_ARTIFACT_V1` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | same |
| `WORKER_INVOKED` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | same |
| `invocation` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | same |

Final process inspection found no `codex exec` process.

## Git status and report-only commit commands

No file is staged and no commit was created. Parent HEAD remains
`c20a281790a1f483fd8333fa09ea3146d5af8027`. Nested HEAD remains
`3183bab71f8f30397c0309dd2e6d846d14a11f66`, and its worktree is clean.

Parent status contains the nine protected paths, the pre-existing unstaged
human-decision runtime change, and the intended G31-22C runtime/test/report
changes. Exact future commands include only G31-22C files:

```bash
git add \
  aigol/runtime/codex_worker_activation_binding_runtime.py \
  aigol/runtime/codex_task_outcome_human_review_runtime.py \
  tests/test_g31_22b_live_task_outcome_review_continuation.py \
  tests/test_g31_22c_task_outcome_criteria_unified_diff_alignment.py \
  docs/governance/G31_22C_TASK_OUTCOME_CRITERIA_AND_UNIFIED_DIFF_CONTRACT_ALIGNMENT.md
git commit -m "feat(governance): align task outcome criteria with unified diff"
```

These commands are report-only and were not executed. They exclude all nine
protected paths and the unrelated human-decision runtime change.

## Progress and recommended next state

Evidence-scoped whole-project progress is revised from **93.0% to 93.5%**.
Future proposed-diff tasks now have truthful, pre-bound, versioned criteria and
deterministic fail-closed structure/scope checks. This phase does not prove
Worker inspection of unchanged files, applied-patch correctness, test success,
final acceptance, or mutation safety.

Recommended next state:

`G31_CANONICAL_PATCH_APPLICATION_AND_TEST_VALIDATION_BOUNDARY_AUDIT_REQUIRED`
