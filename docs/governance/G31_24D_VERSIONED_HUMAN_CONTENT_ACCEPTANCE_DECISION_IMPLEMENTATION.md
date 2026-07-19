# G31-24D Versioned Human Content-Acceptance Decision Implementation

Status: implementation and certification report.

Verdict:

`G31_VERSIONED_HUMAN_CONTENT_ACCEPTANCE_DECISION_OPERATIONAL`

## Scope and committed baseline

This change implements only the post-G31-23B human decision transition:

```text
exact ready_for_acceptance result
  -> contextual /accept or /reject
  -> existing human-decision family V2 artifact
  -> four-step immutable decision Replay
  -> canonical decision presentation
  -> stop before accept_generated_content
```

The committed implementation baseline is
`c85453d3ecf858da408ebb874a1dc9f7f211ccc8` (`feat(cli): bind
replacement acceptance prerequisites`). It contains the accepted R04 report.
The historical `7672cc2b077b013d96a51877510616bd8fe0c694` hash is correctly
treated only as the pre-R04 baseline.

The accepted audit and reachability verdicts were found in the committed
G31-24C and G31-24D-R01 through R04 reports. Generation 30 and all committed
G31 work through R04 remained immutable.

No new production module, artifact family, acceptance owner, authorization
owner, Replay subsystem, Human Interface, patch runner, or mutation path was
created. No commit was created.

## Changed files and line accounting

| File | Change | Purpose |
|---|---:|---|
| `aigol/runtime/human_decision_runtime.py` | +195 / -0 | Existing-owner V2 construction, exact subject projection, four-step Replay, reconstruction, and presentation |
| `aigol/cli/aicli.py` | +45 / -1 | Contextual `/accept` and `/reject` collection after R04 readiness |
| `tests/test_g31_24d_versioned_human_content_acceptance_decision.py` | new, 274 lines | V2 positive, negative, authority, Replay, and V1 regression evidence |
| `tests/test_g31_24d_r03_aicli_disposable_execution_binding.py` | +1 / -1 | Truthful continuation exit state compatibility |
| `tests/test_g31_24d_r04_aicli_acceptance_prerequisite_binding.py` | +2 / -1 | Truthful contextual decision continuation and presentation compatibility |
| `docs/governance/G31_24D_VERSIONED_HUMAN_CONTENT_ACCEPTANCE_DECISION_IMPLEMENTATION.md` | new | This certification report |

Production insertions are exactly 240 across two production files. Production
deletions are one. The hard limits of three production files, 240 production
insertions, no new module, and no new artifact family are satisfied.

## Existing owner and public contracts

The canonical owner remains `aigol/runtime/human_decision_runtime.py`.
Existing V1 public contracts and constants are unchanged. The additive public
V2 surface is:

- `prepare_content_acceptance_decision_context`;
- `record_content_acceptance_decision`;
- `reconstruct_content_acceptance_decision_replay`;
- `render_content_acceptance_decision_context`;
- `render_content_acceptance_decision`;
- `AIGOL_HUMAN_DECISION_RUNTIME_VERSION_V2`;
- `HUMAN_DECISION_ARTIFACT_V2` and `HUMAN_DECISION_RETURNED_V2`;
- `CONTENT_ACCEPTANCE` and `CONTENT_ACCEPTANCE_ONLY`;
- `ACCEPTED` and `REJECTED`;
- `CONTENT_DECISION_REPLAY_STEPS`.

`aigol/cli/aicli.py:run_reference_uhi_session` is changed only as the thin
contextual collector and presenter. Construction, validation, persistence,
hashing, reconstruction, and presentation remain owned by the existing human
decision runtime.

## V1 compatibility

V1 construction, artifact and returned types, two-wrapper Replay, hashing,
validation, reconstruction, rendering, callers, and vocabulary are unchanged.
V1 still records `APPROVE`, `REJECT`, or `REQUEST_MODIFICATION`, and its
historic normalizer still maps `YES` to `APPROVE`. V1 callers supply no V2
fields. No V1 generic approval is interpreted as V2 content acceptance.

Focused regression evidence reconstructed an unchanged
`HUMAN_DECISION_ARTIFACT_V1`, exact `APPROVE`, and exactly two Replay wrappers.
The existing generic decision, human approval, confirmation, R02, R03, and R04
tests all pass.

## Canonical V2 semantics and subject binding

The persisted V2 decision vocabulary is exactly:

```text
decision_type = CONTENT_ACCEPTANCE
decision_scope = CONTENT_ACCEPTANCE_ONLY
decision_outcome = ACCEPTED | REJECTED
```

Before a V2 decision can be recorded, the owner calls the existing
`reconstruct_codex_replacement_acceptance_prerequisite_binding`, verifies the
existing acceptance-prerequisite artifact, and requires:

- `acceptance_prerequisites_satisfied=true`;
- `ready_for_acceptance=true`;
- `result_accepted=false`;
- `mutation_authorized=false`;
- `main_repository_mutated=false`;
- exact `IMPLEMENTATION_MANIFEST_ARTIFACT_V2` and `REPLACE_CONTENT`;
- the manifest canonical session to equal the active session root.

The V2 subject is a hash-and-reference projection, not copied replacement
bytes. It binds the canonical session, chain/conversation lineage, source
workspace, operation, G31-23B binding identity/hash/Replay identity/hash,
acceptance-prerequisite identity/hash, manifest identity/artifact hash/manifest
hash/Replay hash, generated-content validation identity/hash, generated-test
validation identity/hash, G31-23A disposable-validation identity/hash, and for
each replaced file its target, artifact type, operation, authentic preimage and
postimage hashes, file types, file modes, and file-entry hash. The contextual
artifact separately binds the exact human actor.

Every subject is reduced to `subject_binding_hash`. Recording reprojects the
subject from reconstructed canonical evidence and requires byte-equal context,
request, actor, and subject bindings before persistence.

## AiCLI behavior and decision outcomes

Only the valid R04 continuation creates a pending content-decision context.
AiCLI first renders the existing ready-for-human-acceptance evidence, then
renders the target path, manifest, preimage and postimage hashes, exact result
identity, decision type and scope, and the explicit decision-only boundary.

In that context only:

- literal `/accept` records V2 `ACCEPTED`;
- literal `/reject` records V2 `REJECTED`;
- `/approve`, `/satisfied`, `/unsatisfied`, `YES`, and other text create no V2
  decision and leave the continuation awaiting `/accept` or `/reject`.

Both valid outcomes create exactly one decision, reconstruct Replay, render the
outcome and subject hash, then stop with
`HUMAN_CONTENT_ACCEPTANCE_DECISION_RECORDED`. Both retain
`result_accepted=false`, `mutation_authorized=false`, and
`main_repository_mutated=false`. REJECTED is never projected as accepted and
never reaches an acceptance owner.

AiCLI remains non-authoritative:

```text
aicli_authorizes = false
aicli_accepts_content = false
aicli_authorizes_mutation = false
aicli_executes_mutation = false
aicli_owns_replay = false
```

## Replay, fail-closed, and strict authority evidence

The existing-family V2 Replay is exactly four immutable, ordered wrappers:

1. `content_acceptance_context_presented`;
2. `content_acceptance_request_recorded`;
3. `content_acceptance_decision_recorded`;
4. `content_acceptance_decision_returned`.

Reconstruction verifies wrapper order and hashes, every artifact hash, exact
context/request/decision/return linkage, the recorded outcome, and a fresh
projection of the entire G31-23B subject. Context preparation writes no partial
Replay. Duplicate destination and repeated subject decision are rejected.

Focused negative evidence rejects generic V1 aliases, substituted actor,
changed readiness, changed generated-content validation, changed replacement
hash, changed manifest evidence, cross-session context, substituted Replay,
reordered Replay, duplicate destination, and repeated decision consumption.
Existing G31-23B tests retain their source, validation, manifest, prerequisite,
and lineage substitution defenses.

Direct spies around the already-prepared V2 transition prove zero calls to:

- `execute_disposable_patch_validation`;
- `execute_validation_command`;
- `execute_governed_repository_mutation`;
- `bind_codex_replacement_acceptance_prerequisites`;
- `accept_generated_content`;
- `authorize_filesystem_mutation`.

The complete AiCLI tests separately prove the upstream Worker activation,
single disposable application/test, and single G31-23B binder occurred only to
create the accepted readiness baseline. Recording V2 caused no additional
Worker, Provider, command, patch, binder, acceptance, authorization, or source
write. Upstream artifacts and truthful execution history were not rewritten.

## PTY evidence

Exactly one complete PTY-backed `/home/pisarna/work/sapianta/aicli` workflow ran
in an isolated Git repository and isolated runtime. It used one implementation
file, one focused test, one bounded natural-language request, the existing
contextual decisions through R04, and literal `/accept` only after the
ready-for-acceptance presentation.

Observed canonical evidence included:

```text
DISPOSABLE_PATCH_AND_TEST_VALIDATION_COMPLETED
Operation: REPLACE_CONTENT
Acceptance Prerequisites Satisfied: True
Ready For Human Acceptance: True
Decision Type: CONTENT_ACCEPTANCE
Decision Scope: CONTENT_ACCEPTANCE_ONLY
Decision Outcome: ACCEPTED
Result Accepted: False
Mutation Authorized: False
Main Repository Mutated: False
exit_reason: HUMAN_CONTENT_ACCEPTANCE_DECISION_RECORDED
```

The original source SHA-256 remained
`bd12492ff3e10bcc46c6bd0ab7bcc007224a00151367b02110942400718b0709`
and source Git status remained clean. The replacement SHA-256 was
`5f2348364df38839f728dacf6a5ba20f8dee5b6ed2dd61a327f877e69f72d529`.
The V2 decision directory contained exactly the four ordered wrappers above;
the decision and returned wrappers both recorded `ACCEPTED`. AiCLI's mandatory
reconstruction completed before presentation. No generated-content acceptance
or filesystem-mutation-authorization artifact existed. The isolated source,
runtime, shim, and disposable repositories were removed afterward.

## Validation and Governance

| Scope | Exact result |
|---|---|
| New G31-24D focused tests | `5 passed, 0 skipped, 0 failed, 0 deselected in 352.79s` |
| Strengthened tamper test rerun | `1 passed, 0 skipped, 0 failed, 0 deselected in 86.51s` |
| V1, approval/confirmation, R02-R04, G31-23B, manifest, generated acceptance/validation, Replay, Human Interface/AiCLI, Governance compatibility | `183 passed, 0 skipped, 0 failed, 0 deselected in 1368.06s` |
| Focused certification aggregate, excluding the intentional targeted rerun | `188 passed, 0 skipped, 0 failed, 0 deselected` |
| Full repository suite, run exactly once | `6553 passed, 4 skipped, 0 failed, 0 deselected in 2667.69s (44:27)` |
| Changed Python `py_compile` | passed |
| Governance confirmation | `5 passed, 0 failed in 0.03s` |

The governance conformance engine remains deterministically read-only,
fail-closed, and `PARTIALLY_CONFORMANT`: 18 checks passed, two pre-existing hook
mismatches remain visible, and there are zero critical violations. Report hash:
`0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea`.

Parent and all three nested `git diff --check` validations pass. The nested
repositories `sapianta-domain-credit`, `sapianta_system`, and
`sapianta-domain-trading` remain clean and untouched.

## Protected evidence, Git status, and commit commands

All nine protected paths retained their exact preflight hashes. The six
protected runtime hashes remain, in prompt order:

```text
a626a69a8020bc730876119c52701a94de9ab6e4772cc64c1f5d017296650203
e82f47c0c13678725993b21e2af2e0437edccaed324f861a7b58e77d7f8e787d
07b95505521e70f51cdddecc1057fd3a208b198445693c9a8da1e996df5799dd
d47a06d59aba2814c3fb7460049fc2ccbfc834196c956d6c6558e8be8b079e24
a73a499e2e9133c03d7babfd5c4dec7967f31e2bfb354ea9dd41df0a15c08cb3
dbc7b63f2a17c50c43bbb4fde4f44c1dbae8d25d550fb6b4d4daa14e17126161
```

The three protected marker files remain empty with SHA-256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
Final Git status contains only those nine protected pre-existing paths and the
six implementation/report paths listed in the changed-files table. Nothing is
staged and no commit was created.

Explicit commit commands, excluding every protected path, are:

```bash
git add \
  aigol/cli/aicli.py \
  aigol/runtime/human_decision_runtime.py \
  tests/test_g31_24d_r03_aicli_disposable_execution_binding.py \
  tests/test_g31_24d_r04_aicli_acceptance_prerequisite_binding.py \
  tests/test_g31_24d_versioned_human_content_acceptance_decision.py \
  docs/governance/G31_24D_VERSIONED_HUMAN_CONTENT_ACCEPTANCE_DECISION_IMPLEMENTATION.md
git commit -m "feat(cli): record versioned content acceptance decisions"
```

## Progress and exactly one next state

Evidence-scoped G31 reachability is **99.0%**. Evidence-scoped whole-project
progress is **97.0%**. These estimates mean the human content decision is now
operational and replayable, while consumption by the existing canonical
content-acceptance owner remains deliberately unimplemented.

Exactly one next state:

`G31_24E_HUMAN_CONTENT_ACCEPTANCE_TO_EXISTING_ACCEPTANCE_BINDING_REQUIRED`

G31-24E is not implemented here.
