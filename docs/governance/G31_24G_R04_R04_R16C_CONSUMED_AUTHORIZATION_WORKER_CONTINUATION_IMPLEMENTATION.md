# Generation 31-24G-R04-R04-R16C Consumed Authorization Worker Continuation Implementation

Status: completed constitutional implementation.

Date: 2026-07-24

Deterministic verdict:

`G31_CONSUMED_AUTHORIZATION_WORKER_CONTINUATION_IMPLEMENTED`

Exactly one next state:

`G31_24G_R04_R04_R17A_FILESYSTEM_REPLACE_WORKER_RESULT_CAPTURE_OPERATIONAL_READINESS_AUDIT_REQUIRED`

## Certified baseline and implementation scope

G0-G30 and accepted Generation 31 evidence through R16B are treated as
constitutionally closed and immutable. The immediate implementation baseline
is:

- commit: `f362edb3472a9caca88f506ec792389352f0fbbd`;
- subject:
  `docs(governance): define worker consumption compatibility`;
- R16B verdict:
  `G31_CONSUMED_AUTHORIZATION_TO_WORKER_IMPLEMENTATION_COMPATIBILITY_STRATEGY_DEFINED`;
- required R16C strategy:
  resume the existing Filesystem Replace Worker from the immutable certified
  consumption event without consuming Authorization again.

The implementation changes only the boundary after the certified R15F
Execution start and before physical Filesystem Replace Worker execution. It
does not change Platform Core, Execution Runtime, Replay format, Assignment,
Dispatch, Invocation, Provider ownership, or Result Runtime.

## Implementation

### Consumed-authorization continuation

`aigol.workers.filesystem_replace_worker` now exposes one Worker-owned
continuation entry:

```text
execute_consumed_authenticated_replace_v2
```

The entry accepts:

- the exact authenticated replacement request;
- the exact consumed-Authorization reconstruction;
- the exact Worker invocation request artifact;
- the exact Worker Assignment artifact;
- the exact R15F Execution artifact; and
- the exact R15F Execution reconstruction.

Before target access, it validates:

- the authenticated request and each supplied artifact hash;
- exact `request -> consumption` Replay shape;
- request, Authorization, consumption, and Replay identities and hashes;
- the existing consumption wrapper hash;
- the certified Filesystem Replace Worker identity;
- the Assignment-derived `REPLACE_EXISTING_TEXT_FILE` capability;
- request-to-execution-packet identity and hash continuity;
- invocation request, Assignment, canonical-chain, and Execution continuity;
- the exact R15F `EXECUTING` start-only state;
- absence of Provider authority, completion, result certification, governance
  mutation, and Replay mutation; and
- unchanged fail-closed execution reconstruction.

Any mismatch fails before the target is opened or journal evidence is
appended.

### Single consumption and Replay continuation

The continuation reconstructs and requires the immutable existing prefix:

```text
REQUEST_VALIDATED
-> AUTHORIZATION_CONSUMPTION_CLAIMED
```

It does not invoke the consumption owner and does not write either predecessor
again. The existing Replay continues at `journal`, whose
`previous_replay_hash` is the exact existing consumption
`last_wrapper_hash`.

The successful Worker-owned chain is therefore:

```text
request
-> consumption
-> journal
-> started
-> atomic
-> result
-> completion
```

The existing immutable event writer and existing reconstruction format are
unchanged. A second continuation sees a non-prefix Replay and fails closed
without creating another consumption event.

If the continuation loses the immutable journal append race before journal
persistence, it fails closed without adding a competing termination branch.
After journal persistence, the existing Worker restoration, rollback,
recovery, and terminal semantics remain authoritative.

### Existing Worker ownership

The fresh-lifecycle Worker entry and the consumed-Authorization continuation
both call one shared physical replacement body. The body retains the existing:

- descriptor-bound target opening;
- clean-repository and preimage validation;
- durable pre-write journal;
- same-directory temporary-file write;
- atomic replacement;
- postimage and mode verification;
- rollback and recovery; and
- completion or termination evidence.

No second physical execution path, mutation owner, command runner, Provider
path, or Replay family was introduced.

### Common Entry activation

The existing Common Entry invokes the consumed continuation exactly once
after validating the certified R15F Execution artifact and reconstruction.
It requires the exact seven-event Worker Replay and successful terminal
capture before returning the updated state.

The resulting state records:

- `authorization_consumed = true`;
- `worker_execution_performed = true`;
- `repository_mutated = true`;
- `main_repository_mutated = true`;
- `provider_invoked = false`;
- `command_executed = false`; and
- `result_created = false`.

`result_created = false` is preserved because the Worker's own verification
and terminal Replay event are not a canonical Result Runtime capture. Result
capture remains outside R16C.

The certified R15F Execution artifact remains `EXECUTING`; R16C neither
rewrites it nor modifies Execution Runtime.

## Focused and regression evidence

A new focused R16C test module proves:

1. Common Entry consumes Authorization once and invokes one Worker
   continuation;
2. the journal is chained to the existing consumption wrapper;
3. physical content replacement completes in an isolated clean Git
   repository;
4. consumption, invocation-request, Assignment-capability,
   Execution-authority, and Execution-reconstruction substitutions each fail
   before target access or journal creation;
5. a second continuation fails without duplicate consumption; and
6. Common Entry has one continuation call and no legacy physical execution
   call.

Historical Common Entry regression fixtures now use isolated clean Git
repositories with real target files because an approved Common Entry
transition reaches physical Worker execution. Their artifact-local stop
assertions remain unchanged; only final Common Entry expectations advance
from execution-start evidence to the certified Worker mutation outcome.

Validation completed before the full-suite run:

- focused R16C tests: `8 passed`;
- existing hardened replace Worker regressions: `31 passed`;
- R15F transition regressions: `5 passed`;
- slow approved AiCLI transition regression: `1 passed`;
- combined focused Worker, execution, and governance group: `75 passed`;
- targeted `py_compile`: passed.

Two R05-R09 fixture assertions and one R12 fixture assertion initially exposed
the old final-stop expectation during pre-full regression adaptation. Their
repaired nodes passed before the full-suite run.

## Complete-suite classification and repair

The complete repository suite was executed exactly once:

```text
1 failed, 6821 passed, 4 skipped in 4421.77s (1:13:41)
```

The sole failure was:

```text
tests/test_g31_20d_protected_evidence_isolation_and_validation_semantics.py::
test_codex_version_diagnostic_persists_only_to_explicit_disposable_runtime
```

Classification: obsolete protected-evidence fixture assumption.

The test unconditionally read all nine historical protected paths. The current
accepted baseline contains six versioned protected files while the three
legacy empty sentinel paths are absent. This caused `FileNotFoundError` before
the diagnostic under test executed and was unrelated to R16C runtime
behavior.

The exact fixture helper was repaired to snapshot each protected path as
either its SHA-256 or `None`. This preserves a stronger invariant: both
content changes and absent-path creation are detected.

Only the repaired node was then validated:

```text
1 passed in 0.22s
```

The complete repository suite was not rerun.

## Governance and preservation

The governance regression group passed. The deterministic conformance engine
remains:

- status: `PARTIALLY_CONFORMANT`;
- passing rules: `18`;
- failing rules: `2`;
- critical failures: `0`;
- deterministic: `true`;
- read-only: `true`;
- fail-closed: `true`;
- report hash:
  `0790499e25d2e036759b71a533fb2876bdaea1da4c44914fec682205c3dfca56`.

The two existing accepted hook findings remain visible. R16C does not alter or
hide them.

Final `py_compile` passed for every changed Python module and test. Parent
`git diff --check` and all three nested-repository `git diff --check` checks
passed.

The nested repositories are clean at:

- `sapianta-domain-credit`:
  `8615e1e290471a67e4e764c6ab2138340bc7936f`;
- `sapianta_system`:
  `3183bab71f8f30397c0309dd2e6d846d14a11f66`;
- `sapianta-domain-trading`:
  `d3038dc4ba36ffbaee9161172b4c852e8e6acbda`.

The six protected hashes equal the accepted R16B baseline after focused
validation, the single full-suite run, exact-node repair validation, and final
static checks:

| Protected path | SHA-256 |
| --- | --- |
| `diagnostic_evidence.json` | `21546ed151c165c6364aa914d892c34b117ef1ab664ae09d8e2c2a5327bcc8df` |
| `governed_return.json` | `ee57877ceea7d85bd9e3bb29aca64f3637384a7346a5b6a4c4f922c87cb2bcf7` |
| `lineage.json` | `8c47abb9a7c238c9f527e54dd88aa304edbca03b97ea630a4907b4ef139b3a08` |
| `provider_stderr.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `provider_stdout.txt` | `f2fec907b48e7162211f26bbe94352d40f4f6c4380ab3aa4256d072b7c602f30` |
| `governed_returns.jsonl` | `71b085174a274b870617c21810d9a496421985675ae0945f4b56bd3afe7b1118` |

No protected file or nested repository was changed. No file was staged or
committed.
