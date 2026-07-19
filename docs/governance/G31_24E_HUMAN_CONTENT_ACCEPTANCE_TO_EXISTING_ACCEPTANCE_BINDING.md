# G31-24E Human Content Acceptance to Existing Acceptance Binding

Status: implementation and certification report.

Verdict:

`G31_HUMAN_CONTENT_ACCEPTANCE_TO_EXISTING_ACCEPTANCE_BINDING_OPERATIONAL`

## Scope and committed baseline

This change implements exactly one transition:

```text
exact V2 CONTENT_ACCEPTANCE / ACCEPTED decision
  -> reconstruct four-step human-decision Replay
  -> existing accept_generated_content
  -> existing accepted-result artifact plus immutable binding Replay
  -> stop before mutation authorization
```

The committed baseline is
`a5d30c2a07a01689f65883fae5025363fb8cb3ca`
(`feat(cli): record versioned content acceptance decisions`). It contains the
committed G31-24D report and implementation. The historical
`c85453d3ecf858da408ebb874a1dc9f7f211ccc8` commit is correctly treated only
as the pre-G31-24D baseline.

The required G31-24A, G31-24C, G31-24D-R04, and G31-24D reports were tracked,
committed, and read completely. Their accepted verdicts establish that the V2
manifest and validations are directly compatible with the existing acceptance
owner and that the exact missing human decision now exists.

No new production module, acceptance artifact family, human-decision family,
authorization system, mutation system, Replay subsystem, workflow engine, or
parallel serializer/presenter was created. No mutation authorization or source
application is implemented. No commit was created.

## Changed files and line accounting

| File | Change | Purpose |
|---|---:|---|
| `aigol/runtime/generated_content_acceptance_runtime.py` | +160 / -1 | Existing-owner V2 decision bridge, one-wrapper acceptance Replay, reconstruction, and presentation |
| `aigol/cli/aicli.py` | +20 / -1 | Thin ACCEPTED-only bridge call, reconstruction, accepted presentation, and terminal state |
| `tests/test_g31_24e_human_content_acceptance_to_existing_acceptance_binding.py` | new, 225 lines | Exact binding, negative, duplicate, Replay, authority, source-integrity, and V1 evidence |
| `tests/test_g31_24d_versioned_human_content_acceptance_decision.py` | +19 / -5 | Later accepted-result continuation compatibility and one-call evidence |
| `tests/test_generated_content_acceptance_runtime_v1.py` | +1 / -1 | Scope the historic no-side-effect inspection to the unchanged core V1 function |
| `docs/governance/G31_24E_HUMAN_CONTENT_ACCEPTANCE_TO_EXISTING_ACCEPTANCE_BINDING.md` | new | This report |

Production insertions are exactly **180** across exactly two production files;
production deletions are two. The hard limit is satisfied. The core
`accept_generated_content` implementation and meaning are unchanged.

## Reused contracts and public symbols

The implementation reuses:

- `prepare_content_acceptance_decision_context`;
- `record_content_acceptance_decision`;
- `reconstruct_content_acceptance_decision_replay`;
- the exact V2 `HUMAN_DECISION_ARTIFACT_V2`;
- the G31-23B binding, V2 `REPLACE_CONTENT` manifest, validations, prerequisite,
  subject hashes, and Replay;
- `accept_generated_content` and
  `verify_generated_content_acceptance_artifact`;
- canonical `load_json`, `replay_hash`, and `write_json_immutable`;
- existing AiCLI and canonical presentation.

New public existing-owner symbols are:

- `accept_generated_content_from_content_acceptance_decision`;
- `reconstruct_generated_content_acceptance_from_decision_replay`;
- `render_generated_content_acceptance_from_decision`.

AiCLI supplies only issuance identity, timestamp, session root, Replay
destination, and the two canonical captures. It does not construct the human
acceptance dictionary, validate hashes, own Replay, infer acceptance, or invoke
mutation.

## Exact decision-to-acceptance projection

The bridge first reconstructs the four ordered V2 decision wrappers through
the existing human-decision owner. It then requires exactly:

```text
artifact_type = HUMAN_DECISION_ARTIFACT_V2
decision_type = CONTENT_ACCEPTANCE
decision_scope = CONTENT_ACCEPTANCE_ONLY
decision_outcome = ACCEPTED
```

It verifies decision and context hashes, context identity, exact actor,
subject-binding hash, and false result/mutation/execution/provider/worker/
command/patch/automatic-approval fields. Reconstruction freshly validates the
entire G31-23B subject: result and prerequisite identities/hashes, V2 manifest,
path/type/mode, source preimage, replacement postimage, content/test
validations, disposable evidence, repository/session/chain scope, nested G31
lineage, and Replay.

Only after those checks does the acceptance owner internally derive its
existing five-field human evidence:

```text
actor_id             <- V2 decided_by
decision             <- ACCEPTED
accepted_at          <- V2 decided_at
acceptance_scope     <- CONTENT_ACCEPTANCE_ONLY
acceptance_statement <- existing canonical ACCEPTANCE_STATEMENT
```

The exact V2 manifest, content validation, and test validation are passed
unchanged to `accept_generated_content`. Persisted prior acceptance wrappers
are reconstructed and their lineage keys are supplied to the existing reuse
guard. The core function is called exactly once. The returned existing
acceptance artifact is hash-verified and must report
`GENERATED_CONTENT_ACCEPTED` before any Replay write occurs.

The accepted artifact remains the canonical
`GENERATED_CONTENT_ACCEPTANCE_ARTIFACT_V1`. As G31-24A established, this is the
stable acceptance-evidence family even when its explicit implementation branch
consumes V2 `REPLACE_CONTENT` inputs; it is not V1 manifest substitution.

## ACCEPTED, REJECTED, and V1 behavior

For exact `ACCEPTED`, AiCLI records and reconstructs V2, calls the bounded
bridge, reconstructs the accepted-result Replay, presents accepted identity,
operation, target, preimage/postimage hashes, human decision identity/Replay,
acceptance Replay, and stops with:

```text
acceptance_prerequisites_satisfied = true
ready_for_acceptance = true
result_accepted = true
mutation_authorized = false
main_repository_mutated = false
```

`result_accepted=true` records governed-lifecycle acceptance only. The source
replacement is not applied.

For exact `REJECTED`, the existing four-step V2 decision reconstructs and is
presented truthfully. AiCLI does not call the acceptance bridge, creates no
acceptance artifact or acceptance Replay, performs no rework conversion, and
retains all mutation fields false. If REJECTED is supplied directly to the
bridge, it fails before the core acceptance call.

Generic `APPROVE`, `YES`, `SATISFIED`, caller booleans, and V1 decision evidence
cannot reach acceptance. V1 generated-content acceptance remains unchanged:
existing `CREATE_ONLY` manifest construction, human evidence, acceptance
artifact, hashing, validation, callers, authorization boundary, and tests all
remain compatible. V1 callers supply no V2 decision artifacts or Replay.

## Acceptance Replay and duplicate consumption

The only new runtime side effect is one immutable existing-owner Replay wrapper:

```text
000_generated_content_acceptance_from_decision_recorded.json
```

It contains the existing accepted-result artifact plus the exact human decision
identity/hash/Replay reference/Replay hash, exact subject-binding hash, and the
truthful acceptance/mutation stop state. Its wrapper hash covers all fields.

Reconstruction verifies wrapper order/hash, the existing acceptance artifact
and both of its hashes, exact manifest and validation artifact hashes, actor,
decision, timestamp, human-decision identity/hash/Replay hash, subject hash,
and false mutation state. It freshly reconstructs the V2 decision and G31-23B
subject rather than trusting copied values.

A pre-existing destination fails before the core call. A second destination
for an already-consumed human decision is rejected by scanning verified
acceptance wrappers. Existing acceptance lineage keys are passed to the core
reuse check, so the same manifest/content/test lineage cannot be accepted twice.

## Fail-closed and strict stop evidence

Focused tests reject before acceptance for:

- REJECTED, generic approval, and plain boolean evidence;
- changed decision actor or capture;
- changed source preimage or replacement postimage;
- changed manifest or test-validation evidence;
- changed readiness, already-accepted, mutation-authorized, or already-mutated
  state;
- cross-session decision or acceptance Replay;
- reordered four-step human-decision Replay;
- duplicate acceptance destination and repeated decision consumption;
- reordered or substituted accepted-result Replay.

Existing G31-23B and G31-24D coverage continues to reject changed result,
prerequisite, manifest version/operation/path/type/mode/hash, validations,
disposable/Worker/Provider/approval lineage, repository scope, session/chain,
and G31 Replay.

Direct spies placed only after the exact V2 decision had been prepared prove
one `accept_generated_content` call and zero calls to:

- `authorize_filesystem_mutation`;
- `apply_filesystem_mutation`;
- `execute_governed_repository_mutation`;
- `execute_disposable_patch_validation`;
- `execute_validation_command`;
- `bind_codex_replacement_acceptance_prerequisites`;
- `activate_bounded_codex_worker`;
- `invoke_provider_once`.

Source SHA-256 and source Git status remained unchanged. No mutation-
authorization, filesystem-mutation, repository-mutation, commit, deployment,
or release artifact was created.

## PTY evidence

Exactly one complete PTY-backed `/home/pisarna/work/sapianta/aicli` workflow ran
in an isolated Git repository and isolated runtime. It used one implementation
file, one focused test, one ordinary bounded request, the existing contextual
decisions through G31-24D, and literal `/accept`.

Canonical output included:

```text
Decision Type: CONTENT_ACCEPTANCE
Decision Scope: CONTENT_ACCEPTANCE_ONLY
Decision Outcome: ACCEPTED
Generated Content Accepted
Operation: REPLACE_CONTENT
Result Accepted: True
Mutation Authorized: False
Main Repository Mutated: False
The validated result is accepted; repository mutation has not occurred.
exit_reason: GENERATED_CONTENT_ACCEPTANCE_RECORDED
```

The accepted result was
`G31-GENERATED-CONTENT-ACCEPTANCE-fc0d7c12bbf52faf`. The human decision was
`G31-CONTENT-ACCEPTANCE-9bd01f1de73b1580:DECISION`. The source SHA-256 remained
`bd12492ff3e10bcc46c6bd0ab7bcc007224a00151367b02110942400718b0709`;
the validated replacement SHA-256 was
`5f2348364df38839f728dacf6a5ba20f8dee5b6ed2dd61a327f877e69f72d529`.
Source Git status remained clean.

Read-only inspection found exactly four V2 decision wrappers and one acceptance
wrapper. The acceptance wrapper reconstructed as
`GENERATED_CONTENT_ACCEPTANCE_ARTIFACT_V1`, `GENERATED_CONTENT_ACCEPTED`,
`REPLACE_CONTENT`, `result_accepted=true`, `mutation_authorized=false`, and
`main_repository_mutated=false`. No mutation-authorization or filesystem-
mutation artifact existed. No command, patch, Worker, or Provider operation ran
after the decision. The isolated source, runtime, shim, and disposable
repositories were removed afterward.

## Validation and Governance

| Scope | Exact result |
|---|---|
| New G31-24E focused | `4 passed, 0 skipped, 0 failed, 0 deselected in 294.66s` |
| G31-24D V2 and existing acceptance V1 | `13 passed, 0 skipped, 0 failed, 0 deselected in 353.57s` |
| R03/R04, G31-23B, manifests/validations, Replay, Human Interface/AiCLI, Governance | `128 passed, 0 skipped, 0 failed, 0 deselected in 1158.99s` |
| Focused aggregate | `145 passed, 0 skipped, 0 failed, 0 deselected` |
| Full repository suite, run exactly once | `6557 passed, 4 skipped, 0 failed, 0 deselected in 2994.20s (49:54)` |
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

All nine protected paths retained their preflight SHA-256 values. The six
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
Final Git status contains only those protected paths and the six implementation,
test, and report paths listed above. Nothing is staged and no commit was created.

Explicit commit commands excluding every protected path are:

```bash
git add \
  aigol/cli/aicli.py \
  aigol/runtime/generated_content_acceptance_runtime.py \
  tests/test_generated_content_acceptance_runtime_v1.py \
  tests/test_g31_24d_versioned_human_content_acceptance_decision.py \
  tests/test_g31_24e_human_content_acceptance_to_existing_acceptance_binding.py \
  docs/governance/G31_24E_HUMAN_CONTENT_ACCEPTANCE_TO_EXISTING_ACCEPTANCE_BINDING.md
git commit -m "feat(cli): bind human content decisions to acceptance"
```

## Progress and exactly one next state

Evidence-scoped G31 reachability is **99.5%**. Evidence-scoped whole-project
progress is **97.5%**. The validated replacement is now explicitly human-
accepted and Replay-bound, while mutation authorization and source application
remain deliberately absent.

Exactly one next state:

`G31_24F_POST_ACCEPTANCE_MUTATION_AUTHORIZATION_REACHABILITY_AUDIT_REQUIRED`

G31-24F must be audit-only. It is not implemented here.
