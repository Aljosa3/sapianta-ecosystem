# G31-24A Existing Canonical Validated Result Acceptance Reachability Audit

Date: 2026-07-18  
Verdict: `EXISTING_CANONICAL_VALIDATED_RESULT_ACCEPTANCE_EXISTING_HUMAN_DECISION_REQUIRED`

## Scope, immutable baseline, and conclusion

This is an audit only. Generation 30 was not reopened. No acceptance, mutation
authorization, source mutation, patch application, CODEX, Provider, command
runner, or G31-23B binding was invoked. The only change made by this audit is
this report.

The exact G31-23B V2 `REPLACE_CONTENT` manifest plus its V2 content and
focused-test validations are direct inputs to the existing canonical function
`accept_generated_content`. The function explicitly branches V1 versus V2,
requires `REPLACE_CONTENT` for V2, and binds the exact manifest, content, test,
chain, bundle, and operation hashes. No projection or new acceptance owner is
needed for those three artifacts.

However, G31-23B intentionally supplies no `human_acceptance_evidence`. The
existing acceptance owner rejects that absence unless it receives the exact
existing `ACCEPTED` / `CONTENT_ACCEPTANCE_ONLY` decision and required statement.
The earlier G31 task-outcome and disposable-application human decisions are
authenticated lineage and eligibility evidence; they are not this decision and
cannot be substituted for it. Therefore the accepted result cannot become an
accepted result until that existing mandatory human content-acceptance decision
is supplied through an explicitly bound call.

Acceptance itself is evidence-only and non-authorizing. The currently existing
filesystem authorization and filesystem mutation families are V1/
`CREATE_ONLY` only, so they reject this V2 result. The separate governed
repository-mutation owner can apply `REPLACE_CONTENT`, but it requires its own
approved patch-proposal workflow and has no caller or contract binding from the
G31-23B acceptance result. This audit neither treats acceptance as mutation
authority nor proposes a bypass.

## Baseline and protected evidence

| Check | Evidence | Result |
|---|---|---|
| Required G31-23A report | tracked at `HEAD`; commit `8da4765a` | pass |
| Required G31-23B report/source | tracked at `HEAD`; source/report commit `a6a9e28a` | pass |
| Required G31-23B focused test | tracked at `HEAD`; test commit `3d7d1730` | pass |
| Parent branch / `HEAD` | `master` / `3d7d1730` | observed |
| Nested repositories | `sapianta-domain-credit`, `sapianta_system`, and `sapianta-domain-trading` status empty before and after audit work | clean, untouched |
| Protected artifacts | exact SHA-256 values below matched before and after | pass |

| Protected path | SHA-256 |
|---|---|
| `diagnostic_evidence.json` | `a626a69a8020bc730876119c52701a94de9ab6e4772cc64c1f5d017296650203` |
| `governed_return.json` | `e82f47c0c13678725993b21e2af2e0437edccaed324f861a7b58e77d7f8e787d` |
| `lineage.json` | `07b95505521e70f51cdddecc1057fd3a208b198445693c9a8da1e996df5799dd` |
| `provider_stderr.txt` | `d47a06d59aba2814c3fb7460049fc2ccbfc834196c956d6c6558e8be8b079e24` |
| `provider_stdout.txt` | `a73a499e2e9133c03d7babfd5c4dec7967f31e2bfb354ea9dd41df0a15c08cb3` |
| `governed_returns.jsonl` | `dbc7b63f2a17c50c43bbb4fde4f44c1dbae8d25d550fb6b4d4daa14e17126161` |
| `WORKER_INVOCATION_ARTIFACT_V1`, `WORKER_INVOKED`, `invocation` | empty-file SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

## Contract and caller inventory

| Public contract / owner | Canonical input and output | Callers / authority / Replay / downstream boundary |
|---|---|---|
| `aigol/runtime/generated_content_acceptance_runtime.py:accept_generated_content` | V1 or V2 implementation manifest; matching content and test validation; explicit human acceptance; issuance metadata; optional previous lineage keys -> `GENERATED_CONTENT_ACCEPTANCE_ARTIFACT_V1` | Production callers: `aigol/cli/commands/implementation_epoch.py`, `aigol/runtime/first_real_implementation_generation_epoch_runtime.py`, and `aigol/runtime/multi_provider_competitive_proposal_runtime.py`. All construct V1 bundles. Human content-acceptance owner; creates signed, replay-visible evidence only (not a Replay wrapper); marks accepted on success; no mutation authorization, patch application, or source write. |
| `generated_content_acceptance_runtime.py:bind_generated_content_acceptance_prerequisites` | exact V2 manifest plus V2 validations -> `GENERATED_CONTENT_ACCEPTANCE_PREREQUISITES_ARTIFACT_V2` | Used by G31-23B binding. Read-only prerequisite evidence, explicitly `ready_for_acceptance=true`, `result_accepted=false`; no human decision, acceptance, mutation, or write. |
| `aigol/runtime/codex_replacement_acceptance_prerequisite_binding_runtime.py:bind_codex_replacement_acceptance_prerequisites` | G31-23A lineage/captures, source/disposable roots -> V2 manifest, validations, prerequisite artifact, one binding Replay wrapper | G31-23B owner. Reconstructs source and disposable evidence; creates no acceptance or mutation. Its reconstruction returns the exact required five-state truth. |
| `aigol/runtime/result_evaluation_runtime.py:evaluate_result` | `RESULT_ARTIFACT_V1`, observations, evaluation metadata, Replay dir -> V1 evaluation plus two ordered Replay wrappers | No production caller. Evaluation is non-approval/non-certification evidence; it neither accepts G31-23B V2 manifests nor feeds acceptance. |
| `aigol/runtime/filesystem_mutation_authorization_runtime.py:authorize_filesystem_mutation` | V1 `CREATE_ONLY` manifest, V1 validations, acceptance, separate explicit human authorization -> authorization artifact | Three production callers listed above. It authorizes only V1 create-only paths, does not write, and rejects V2 / `REPLACE_CONTENT`. |
| `aigol/runtime/filesystem_mutation_runtime.py:apply_filesystem_mutation` | V1 create-only manifest and authorization -> mutation artifact | Same three production callers. It writes only after the distinct authorization and rejects V2. |
| `aigol/runtime/governed_repository_mutation_runtime.py:execute_governed_repository_mutation` and `repository_mutation_worker_runtime.py:apply_repository_mutation` | approved governed patch workflow / certified patch proposal -> mutation capture and ordered Replay | Mutating owner and patch applier; require an independent approved proposal. No G31-23B acceptance input or caller was found. |

The acceptance artifact is `GENERATED_CONTENT_ACCEPTANCE_ARTIFACT_V1` even when
its valid inputs are V2. That is a stable acceptance-evidence type, not V1
artifact substitution: its implementation explicitly selects V2 validation
types whenever the manifest operation is `REPLACE_CONTENT`.

## G31-23B compatibility matrix

Classification applies to the existing `accept_generated_content` call, unless
the row names another documented contract.

| Required evidence or state | Classification | Deterministic finding |
|---|---|---|
| V2 manifest identity, artifact hash, manifest hash, V2 version, `REPLACE_CONTENT` | DIRECTLY_COMPATIBLE | acceptance permits `IMPLEMENTATION_MANIFEST_ARTIFACT_V2`, requires created status, exact operation, artifact hash, and manifest hash. |
| V2 manifest Replay / one binding Replay | AVAILABLE_BUT_NOT_BOUND | acceptance receives signed artifacts but does not reconstruct their Replay; G31-23B reconstruction does so before readiness. |
| authentic patch, preimage, postimage, source path, regular-file type and mode | DIRECTLY_COMPATIBLE | represented inside the authenticated V2 manifest; V2 content validation has already rejected changed bytes, identity, type, mode, symlink, submodule, traversal, create/delete/rename, and binary semantics. |
| V2 content-validation artifact | DIRECTLY_COMPATIBLE | exact V2 type, validated status, manifest reference/artifact/hash, chain, bundle, and operation are required. |
| V2 focused-test-validation artifact | DIRECTLY_COMPATIBLE | same exact V2 binding is required. |
| G31-23A disposable application / fixed-test receipt | AVAILABLE_BUT_NOT_BOUND | authenticated through G31-23B manifest and prerequisite lineage; not a separate parameter of acceptance. |
| prerequisite artifact, satisfaction, readiness, and non-accepting state | AVAILABLE_BUT_NOT_BOUND | the binder proves these values, but acceptance recomputes its three direct prerequisites rather than consuming the summary artifact. |
| original G31 task/application human-decision and Worker-patch lineage | AVAILABLE_BUT_NOT_BOUND | V2 manifest carries references/hashes; acceptance binds the manifest but does not interpret those prior decisions as acceptance. |
| exact human content-acceptance evidence | MISSING | G31-23B deliberately leaves it absent; acceptance requires actor, `ACCEPTED`, timestamp, `CONTENT_ACCEPTANCE_ONLY`, and the exact acceptance statement. |
| acceptance ID and creation timestamp | MISSING | issuance metadata must be supplied at the future acceptance action; it is not a lineage substitute. |
| duplicate acceptance-consumption state | AVAILABLE_BUT_NOT_BOUND | optional `prior_acceptance_lineage_keys` rejects a supplied duplicate, but G31-23B tracks only one-time disposable-outcome consumption and no production caller supplies an acceptance registry. |
| result-evaluation evidence | INCOMPATIBLE | evaluation accepts `RESULT_ARTIFACT_V1`, not a replacement manifest; it is not part of acceptance and has no production caller. |
| acceptance Replay destination and ordering | MISSING | acceptance has no Replay-dir parameter or wrapper sequence; it returns a hash-bound replay-visible evidence artifact only. |
| V1 `CREATE_ONLY` compatibility | DIRECTLY_COMPATIBLE | acceptance retains V1 branch and the focused historic V1 tests pass. |
| source/nested repository identity | AVAILABLE_BUT_NOT_BOUND | G31-23B reconstructs and validates source workspace/snapshot; acceptance consumes the resulting signed manifest, not repository paths. |
| protected-artifact hashes | AVAILABLE_BUT_NOT_BOUND | audit integrity evidence only; no acceptance input contract consumes them. |

## Authority, Replay, and fail-closed assessment

The required separation is preserved:

```text
validated V2 replacement result
  -> explicit human content acceptance (not yet supplied)
  -> non-authorizing acceptance artifact
  -> separate mutation authorization, if a compatible owner exists
  -> separate repository mutation workflow, if independently approved
```

`accept_generated_content` has `CONTENT_ACCEPTANCE_ONLY` scope and false flags
for filesystem mutation, Provider/Worker invocation, execution, dispatch,
automatic approval, governance mutation, and Replay mutation. It never invokes
the patch owners and makes no source write. The V1 filesystem-authorization
path requires another exact human authorization statement and rejects V2;
therefore acceptance cannot cause source-repository application here.

Committed G31-23B tests fail closed before readiness for V1 substitution,
changed patch/preimage/postimage/test bytes, source drift, path/type/mode
changes, failed validation, changed decisions, cross-session evidence, Replay
substitution/order corruption, duplicate G31-23A consumption, and protected
authority-owner invocation. Existing acceptance tests reject missing explicit
human acceptance, invalid content/test bindings, artifact tampering, and a
caller-supplied duplicate lineage key. Existing result-evaluation tests reject
invalid/cross-chain result, duplicate destination, authority-bearing
observations, corrupted references, and Replay ordering/tampering.

The qualification on duplicate acceptance is important: the acceptance function
has a fail-closed `prior_acceptance_lineage_keys` check, but there is no current
G31-23B caller that projects persisted prior acceptance state into it. A future
binding must preserve that existing parameter rather than infer or omit a
duplicate-consumption decision.

## PTY observation

A PTY-backed `./aicli --help` observation was read-only and produced no Git or
source change. The public UHI launcher exposes only `submit`; its G31 path ends
at semantic validation/task-outcome routing and exposes no G31-23A/23B
prerequisite-binding or acceptance operation. Consequently, no truthful
read-only `./aicli` invocation exists that can reach the G31-23B ready state
without starting the unrelated workflow that this audit is forbidden to invoke.

The existing disposable-fixture G31-23B contract is the executable observation
for that state: it asserts `acceptance_prerequisites_satisfied=true`,
`ready_for_acceptance=true`, `result_accepted=false`,
`mutation_authorized=false`, and `main_repository_mutated=false`; it also
monkeypatches both acceptance and main mutation owners to prove they are not
called. No audit-time acceptance or mutation was attempted.

## Validation

| Validation | Current result |
|---|---|
| fast manifest/content/test/acceptance/result-evaluation/mutation/certification/Replay suite | `86 passed in 0.54s` |
| focused G31-17B through G31-23B collection | `226 tests collected in 0.26s` |
| current G31 long-fixture execution | runner ended before pytest completion summary after initial progress; not represented as a pass or failure. Committed G31-23B evidence remains `140 passed in 1339.72s`. |
| governance conformance tests | `5 passed in 0.03s` |
| governance engine | `PARTIALLY_CONFORMANT`: 18 passed, 2 known hook mismatches, 0 critical; deterministic/read-only/fail-closed; hash `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea` |
| targeted `py_compile` | pass |
| parent plus three nested `git diff --check` | pass |

No focused result conflicts with committed certification evidence, so the full
suite was not run. Runtime behavior did not change.

## Files, status, progress, and bounded next state

Inspected production files: `generated_content_acceptance_runtime.py`,
`result_evaluation_runtime.py`, `result_runtime.py`,
`implementation_manifest_runtime.py`, `generated_content_validation_runtime.py`,
`generated_test_validation_runtime.py`,
`codex_replacement_acceptance_prerequisite_binding_runtime.py`,
`filesystem_mutation_authorization_runtime.py`, `filesystem_mutation_runtime.py`,
`governed_repository_mutation_runtime.py`, `repository_mutation_worker_runtime.py`,
and the three production acceptance/mutation callers. Inspected tests include
the listed canonical, result-evaluation, mutation, certification, Replay,
Governance, and G31-17B--G31-23B modules. Inspected governance reports:
G31-23A and G31-23B. Created only this document.

Exact parent status before this documentation-only file consisted of the nine
protected artifacts listed above (six modified runtime-evidence paths and three
untracked root markers). After this report, the only additional path is this
untracked G31-24A document; nothing is staged. Documentation-only commit:

```bash
git add docs/governance/G31_24A_EXISTING_CANONICAL_VALIDATED_RESULT_ACCEPTANCE_REACHABILITY_AUDIT.md
git commit -m "docs(governance): audit validated result acceptance reachability"
```

Evidence-scoped progress: G31-23B established 94.5% for the bounded sequence.
This audit resolves the acceptance-reachability question (95.0%): the remaining
0.5% is an explicit human content decision plus a minimal caller binding that
projects the exact V2 artifacts and duplicate-consumption state into the
existing function. It is not mutation work.

Next state (exactly one):
`G31_24B_CANONICAL_V2_ACCEPTANCE_DIRECT_BINDING_AFTER_EXPLICIT_HUMAN_CONTENT_ACCEPTANCE`

### Bounded G31-24B implementation prompt

Implement only a direct binding to
`generated_content_acceptance_runtime.accept_generated_content` for one
reconstructed G31-23B capture, and only after receiving the existing explicit
`ACCEPTED` / `CONTENT_ACCEPTANCE_ONLY` human evidence with the exact canonical
statement. Reconstruct the G31-23B binding; pass its exact V2 manifest, V2
content validation, and V2 test validation unchanged; pass a persisted,
replay-verified `prior_acceptance_lineage_keys` projection; and record only the
existing acceptance artifact. Fail closed on any capture, hash, Replay, source
identity, prerequisite, duplicate, or human-evidence mismatch. Do not change
manifest/validation schemas, acceptance semantics, result evaluation, mutation
authorization, source mutation, patch application, CODEX, Provider, commands,
or the nested repository. Add focused tests for success, missing/substituted
human evidence, V1/V2 substitution, altered bytes/Replay, duplicate acceptance,
and no mutation. Keep source application explicitly absent.
