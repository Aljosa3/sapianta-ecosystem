# G31-23B Existing-File Replacement Manifest and Acceptance-Prerequisite Binding

Date: 2026-07-18  
Verdict: `G31_EXISTING_FILE_REPLACEMENT_MANIFEST_AND_ACCEPTANCE_PREREQUISITE_BINDING_OPERATIONAL`

## Scope and baseline

G31-23B extends the existing canonical implementation-manifest, generated-content
validation, generated-test validation, and generated-content acceptance families
with an explicit V2 `REPLACE_CONTENT` contract. It binds one successful G31-23A
disposable result to canonical acceptance prerequisites without accepting the
result, authorizing mutation, applying the Worker patch to the source repository,
starting CODEX or a Provider, committing, deploying, or releasing.

| Baseline | Observed |
|---|---|
| parent top level | `/home/pisarna/work/sapianta` |
| parent HEAD | `84a5e17c44c73ff927333997da2f0fe352418d22` |
| parent subject | `fix(governance): separate review from implementation authority` |
| committed G31-23A prerequisite | `8da4765a feat(governance): validate satisfied patch in disposable workspace` |
| nested `sapianta_system` HEAD | `3183bab71f8f30397c0309dd2e6d846d14a11f66` |
| nested worktree | clean |
| pre-existing parent changes | exactly the nine protected paths |
| staged paths | none |

Every pre-existing dirty path was classified as protected runtime evidence or a
protected root marker. No unrelated source change existed at baseline.

## Canonical owner audit

| Concern | Canonical owner reused or extended | G31-23B behavior |
|---|---|---|
| implementation manifest | `implementation_manifest_runtime.py` | Adds explicit `IMPLEMENTATION_MANIFEST_ARTIFACT_V2` and `REPLACE_CONTENT`; retains the V1 constructor, hash inputs, Replay steps, and reconstructed V1 shape. |
| unified-diff and postimage derivation | `codex_task_outcome_human_review_runtime.py` through G31-23A | Reconstructed, not reimplemented. Exact patch bytes, target paths, preimages, and derived postimages come from the authenticated G31-23A plan. |
| disposable content application/verification | G31-23A plus `governed_repository_mutation_runtime.py` | Reconstructed read-only. G31-23B does not call a mutation owner. |
| generated-content validation | `generated_content_validation_runtime.py` | Produces V2 validation only for exact replacement entries with matching bytes, SHA-256, path, regular-file type, mode, size, and denied operations. |
| focused-test validation | `generated_test_validation_runtime.py` | Produces V2 validation bound to the existing V1 validation-command result and Replay from G31-23A. It executes no command. |
| validation-command evidence | `validation_command_runner_runtime.py` | Reconstructed through its existing three-wrapper Replay; requires the exact fixed pytest command, exact disposable cwd, success status, and return code zero. |
| acceptance prerequisites | `generated_content_acceptance_runtime.py` | Adds a non-accepting V2 prerequisite binder and extends the same internal manifest/content/test prerequisite checks used by the canonical acceptance function. |
| generated-content acceptance | `generated_content_acceptance_runtime.accept_generated_content` | Remains the future human-acceptance owner. It was not called. |
| source repository mutation | canonical governed repository-mutation owners | Not imported or called by G31-23B. |
| Replay persistence | existing immutable JSON wrapper helpers and the existing manifest Replay family | Manifest keeps its two canonical steps; the G31 lineage binding records one immutable wrapper. No parallel Replay subsystem exists. |

Versioning the existing families is sufficient. No parallel manifest,
validation, acceptance, approval, mutation, or Replay architecture was added.

## Manifest compatibility

| Contract | V1 behavior | V2 behavior | Compatibility result |
|---|---|---|---|
| artifact | `IMPLEMENTATION_MANIFEST_ARTIFACT_V1` | `IMPLEMENTATION_MANIFEST_ARTIFACT_V2` | Explicit version; no reinterpretation |
| runtime | `AIGOL_IMPLEMENTATION_MANIFEST_RUNTIME_V1` | `AIGOL_IMPLEMENTATION_MANIFEST_RUNTIME_V2` | Separate deterministic hash domain |
| operation | `CREATE_ONLY` | `REPLACE_CONTENT` | Substitution fails closed |
| target state | `MUST_NOT_EXIST` | `MUST_EXIST_REGULAR_FILE` | Existing target is explicit |
| content | generated UTF-8 content | exact UTF-8 preimage, postimage, and patch bytes | All bytes and SHA-256 values are bound |
| path semantics | one newly created target | identical original/target/result path | Create, delete, rename, traversal, and duplicate targets denied |
| type/mode | new-file artifact type | regular-file type and unchanged numeric mode | Symlink, submodule, binary, type, and mode change denied |
| test semantics | generated test content | unchanged existing focused test plus authentic successful execution receipt | V2 test evidence binds execution rather than claiming a generated test |
| returned Replay | `IMPLEMENTATION_MANIFEST_RETURNED_V1` | `IMPLEMENTATION_MANIFEST_RETURNED_V2` | Same ordered two-wrapper family |
| reconstruction | historic V1 fields and hashes | V2 fields plus replacement lineage | V1 output shape and hash inputs preserved |

The historic V1 unit and full-suite tests pass without fixture or expected-hash
changes. Historic G31-22B remains V1 and `TASK_OUTCOME_UNSATISFIED`; it cannot
produce the required successful G31-23A outcome and therefore cannot enter this
boundary.

## Eligibility and authority

The binding reconstructs, rather than trusts, all of the following:

1. the original governed request, repository grounding, execution candidate,
   governed execution, activation, exact-byte capture, and governance validation;
2. one V2 task-outcome review and its exact `TASK_OUTCOME_SATISFIED` human
   decision and Replay;
3. the separate G31-23A bounded application/test approval and Replay;
4. one successful G31-23A outcome and Replay;
5. exact session root, source workspace, disposable workspace, changed paths,
   fixed test target, and fixed command;
6. exact patch, preimage, postimage, focused-test, and repository-snapshot bytes
   and hashes;
7. unchanged regular-file identity and mode;
8. the successful validation-command result and its complete Replay.

| Fact | Successful truth | Authority consequence |
|---|---:|---|
| V2 task outcome satisfied | true | eligibility only |
| disposable application approval consumed | true | prior disposable-only authority; grants nothing new |
| disposable patch applied once | true | evidence only |
| content validation passed | true | acceptance prerequisite only |
| grounded test validation passed | true | acceptance prerequisite only |
| replacement manifest created | true | read-only evidence |
| acceptance prerequisites satisfied | true | ready for a future acceptance decision |
| ready for acceptance | true | does not equal acceptance |
| result accepted | false | canonical acceptance owner not called |
| main repository mutated | false | Worker patch remains disposable |
| mutation authorized | false | no repository authority granted |
| CODEX/Provider started | false | no execution authority |
| commit/deploy/release | false | out of scope |

## V2 replacement semantics

Each replacement entry records and validates:

- `operation = REPLACE_CONTENT`;
- the exact unchanged `target_path`, `original_target_path`, and
  `resulting_target_path`;
- `existing_target = true` and `MUST_EXIST_REGULAR_FILE`;
- exact preimage and postimage UTF-8 bytes and SHA-256;
- the exact unified-diff bytes and SHA-256;
- exact expected postimage byte size;
- identical regular-file type and numeric mode before and after;
- explicit false values for create, delete, rename, binary patch, symlink,
  submodule, and path traversal;
- false authority flags.

The focused-test entry records the unchanged test bytes/hash/mode, exact
`["python", "-m", "pytest", <grounded-test>]` argv, exact disposable cwd,
validation result artifact, result hash, and Replay reference/hash. The receipt
must prove `VALIDATION_COMMAND_COMPLETED`, return code zero, `shell=False`, and
no Provider, Worker, or repair invocation.

## Acceptance prerequisites created

The deterministic `NO-OWNERS-CALLED` confirmation under `/tmp` produced:

| Evidence | Identity | Hash |
|---|---|---|
| G31-23A source outcome | `G31-DISPOSABLE-VALIDATION-8b1aef3878e403bb68a4326a:OUTCOME` | `sha256:a5a8978dc85118f6ad29d41450eea92896a552f58c718035adc6df40a3702d62` |
| V2 replacement manifest | `G31-REPLACEMENT-MANIFEST-a9c8bb633ee88bdc4004909a` | `sha256:ad3439f03d2330602bdd435d6199c61fbc48ee78aef73320fc95ccddbc9efe4a` |
| manifest artifact | same manifest | `sha256:a850278d72a6d383ac8468025ce71a1327b9bd561fd0d5166a8a297231f679ff` |
| manifest Replay | two canonical wrappers | `sha256:b397671e24d67238b0d44d38949982b978e88eb17989014acb8c7242e333dbdc` |
| V2 content validation | `G31-REPLACEMENT-CONTENT-VALIDATION-a9c8bb633ee88bdc4004909a` | `sha256:81dd8b45e9510a8c0e37930365900edc73534ad9590f61d77134a3e2212159c8` |
| V2 test validation | `G31-REPLACEMENT-TEST-VALIDATION-a9c8bb633ee88bdc4004909a` | `sha256:7189018a3626f08661c465f7cdc8859cf4306bf0d45019b3b5c089300eac48f8` |
| acceptance prerequisites | `G31-REPLACEMENT-ACCEPTANCE-PREREQUISITES-a9c8bb633ee88bdc4004909a` | `sha256:343e252de297253dbe066c16d179d15f8ae936cfb5cdcd71fff469738c8f562d` |
| G31-23B binding | `G31-REPLACEMENT-PREREQUISITE-BINDING-a9c8bb633ee88bdc4004909a` | `sha256:45d232a162e9496b1e19d309d7a0ec58ccfb13c4fd662dfb0570659755bef7c6` |
| binding Replay | one immutable wrapper | `sha256:212037303ba54e863ce8648d70f320506ff37cec853ff1b7bffc855cd5060c1d` |

The exact patch SHA-256 is
`sha256:78a8f292b3a243717f4375b6fbae99d0dcd51999dc1a1341ddbd5c7d2ce51a88`.
The source preimage is
`sha256:bd12492ff3e10bcc46c6bd0ab7bcc007224a00151367b02110942400718b0709`;
the disposable postimage is
`sha256:5f2348364df38839f728dacf6a5ba20f8dee5b6ed2dd61a327f877e69f72d529`.
The fixed focused test returned zero, and its result artifact hash is
`sha256:3ae19076e24f3e535bf69bed2ffb3ca3356b1b0e0fdb3eb12c972bad9e1d59af`.

## Fail-closed matrix

| Boundary | Rejected condition | Result before readiness |
|---|---|---|
| task review | V1, unsatisfied, rework, changed criteria or decision | rejected |
| G31-23A outcome | failed/incomplete/repeated application, failed content, failed test | rejected |
| exact bytes | missing or changed patch, preimage, postimage, or focused-test bytes/hash | rejected |
| repository | source snapshot/preimage drift or disposable postimage drift | rejected |
| paths | absolute, traversal, ungrounded, duplicate, changed identity | rejected |
| operation | `CREATE_ONLY` substitution, create, delete, rename, binary semantics | rejected |
| file identity | type/mode change, symlink, submodule | rejected |
| lineage | cross-session reference, review/decision/approval/outcome substitution | rejected |
| Replay | wrapper, manifest, validation, result, or prerequisite substitution | rejected |
| destination | existing Replay destination | rejected |
| consumption | previously consumed G31-23A outcome | rejected |
| authority | acceptance or source-mutation owner invocation | absent and explicitly false |

No failed path grants readiness, acceptance, mutation authority, retry, repair,
Provider/CODEX execution, commit, deployment, or release.

## Changed surface and production-line delta

| File | Purpose |
|---|---|
| `aigol/runtime/implementation_manifest_runtime.py` | V2 replacement manifest constructor, entries, hashing, and backward-compatible reconstruction |
| `aigol/runtime/generated_content_validation_runtime.py` | operation-version dispatch and exact replacement-content validation |
| `aigol/runtime/generated_test_validation_runtime.py` | V2 existing-test execution-receipt validation |
| `aigol/runtime/generated_content_acceptance_runtime.py` | V2-compatible canonical prerequisite checks and non-accepting prerequisite artifact |
| `aigol/runtime/codex_replacement_acceptance_prerequisite_binding_runtime.py` | complete G31-23A lineage reconstruction and canonical prerequisite orchestration |
| `tests/test_g31_23b_existing_file_replacement_manifest_and_acceptance_prerequisite_binding.py` | deterministic success, compatibility, tamper, isolation, and non-authority coverage |
| this report | evidence and handoff |

Production delta before this report is **1,463 added and 30 removed lines**:
899 additions/30 removals across the four extended owners and 564 lines in the
new G31 binding. The focused test module is 379 physical lines. No nested
production file changed.

## Validation

| Validation | Result |
|---|---|
| focused G31-23B | `12 passed in 535.14s` |
| historic manifest/content/test/acceptance owners | `34 passed in 0.15s` |
| G31-17B through G31-23B regression group | `140 passed in 1339.72s` |
| governance conformance tests | `5 passed in 0.03s` |
| complete parent suite | `6533 passed, 4 skipped in 1567.42s` |
| targeted `py_compile` | passed |
| parent and nested `git diff --check` | passed |
| governance engine | `PARTIALLY_CONFORMANT`; 18 passed, two known hook mismatches, zero critical violations; deterministic/read-only/fail-closed; report hash `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea` |

The known root and nested pre-commit-hook drift remains visible and was not
introduced, repaired, or reframed by G31-23B.

## Protected hashes

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

## Git status and task-only commit commands

No path is staged and no commit was created. Parent HEAD remains
`84a5e17c44c73ff927333997da2f0fe352418d22`; nested HEAD remains
`3183bab71f8f30397c0309dd2e6d846d14a11f66` with a clean worktree.

The exact future commands include only G31-23B:

```bash
git add \
  aigol/runtime/implementation_manifest_runtime.py \
  aigol/runtime/generated_content_validation_runtime.py \
  aigol/runtime/generated_test_validation_runtime.py \
  aigol/runtime/generated_content_acceptance_runtime.py \
  aigol/runtime/codex_replacement_acceptance_prerequisite_binding_runtime.py \
  tests/test_g31_23b_existing_file_replacement_manifest_and_acceptance_prerequisite_binding.py \
  docs/governance/G31_23B_EXISTING_FILE_REPLACEMENT_MANIFEST_AND_ACCEPTANCE_PREREQUISITE_BINDING.md
git commit -m "feat(governance): bind replacement acceptance prerequisites"
```

These commands are report-only and exclude all nine protected paths.

## Progress and recommended next state

Evidence-scoped whole-project progress advances from **94.0% to 94.5%**. One
exact V2 satisfied CODEX patch can now be applied and tested in a disposable
repository, represented as an explicit existing-file replacement manifest, and
bound to all canonical content/test acceptance prerequisites. Human result
acceptance and any later source-repository mutation remain separate, unperformed,
and unauthorized.

Recommended next state:

`G31_CANONICAL_VALIDATED_RESULT_ACCEPTANCE_BOUNDARY_REQUIRED`
