# Generation 31-24G-R04-R04-R15B G31 Execution Invocation Origin Compatibility Transition

Status: completed bounded compatibility repair; stopped before Common Entry
execution binding and every live Worker-execution stage.

Date: 2026-07-24

Deterministic verdict:

`G31_EXECUTION_INVOCATION_ORIGIN_COMPATIBILITY_OPERATIONAL`

Exactly one next state:

`G31_24G_R04_R04_R15C_WORKER_EXECUTION_OPERATIONAL_READINESS_REAUDIT_REQUIRED`

## Constitutional scope

This generation treats G0-G30 and the accepted G31 Common Entry-to-Assignment,
Common Entry-to-Dispatch, Common Entry-to-Invocation, and R15A audit results as
immutable certified baselines.

R15A identified exactly one first blocker:

`R14B_CERTIFIED_INVOCATION_ORIGIN_NOT_ACCEPTED_BY_EXECUTION_RUNTIME`

R15B changes only the existing exact Invocation-origin allowlist in the
existing direct Execution Runtime. It adds the immutable R14B Common Entry
origin without changing any Invocation artifact, hash, Replay, lineage,
Worker, Provider, command, mutation, result-capture, or execution path.

The source and test changes do not:

- call Common Entry;
- rewrite or regenerate certified R14B evidence;
- change `WORKER_INVOCATION_ARTIFACT_V1`;
- change Invocation Replay ownership or reconstruction;
- add an Execution Runtime owner;
- execute a Worker;
- invoke a Provider;
- execute a command;
- open a mutation target;
- capture an execution result;
- mutate runtime repository content;
- stage files; or
- create a commit.

Tests use only temporary pytest destinations for existing Execution Runtime
validation and Replay construction.

## Accepted baseline

The transition began from:

- branch: `master`;
- HEAD: `0509eb950509e17aec291286f8bd0419ee239ead`;
- HEAD subject:
  `docs(governance): audit worker execution operational readiness`;
- R15A verdict:
  `G31_WORKER_EXECUTION_OPERATIONAL_BLOCKED`;
- R15A blocker:
  `R14B_CERTIFIED_INVOCATION_ORIGIN_NOT_ACCEPTED_BY_EXECUTION_RUNTIME`;
- certified R14B Invocation origin:
  `PLATFORM_CORE_G31_INVOCATION_BINDING`;
- existing direct Execution Runtime:
  `EXECUTION_RUNTIME_V1`.

The versioned worktree and all three nested repositories were clean at the
implementation boundary. The three historical zero-byte marker paths were
absent at that committed boundary.

## Minimal compatibility repair

The only modified production contract is:

```text
aigol.runtime.execution_runtime._validate_invocation_artifact
```

Before R15B, the exact allowlist was:

```text
AIGOL
AIGOL_GOVERNANCE
```

R15B extends that same allowlist to:

```text
AIGOL
AIGOL_GOVERNANCE
PLATFORM_CORE_G31_INVOCATION_BINDING
```

No predicate was weakened. Membership remains exact, and every unrecognized
origin still fails closed with:

```text
execution failed closed: invocation must be AiGOL-created
```

The existing artifact-hash, artifact-type, Invocation-status, chain, Worker,
Replay-visibility, authority, duplicate-execution, scope, reference, and
lineage checks remain in their original order after the origin gate.

The bounded production delta is five insertions and one deletion in one
existing file. It adds no helper, normalization rule, artifact family,
registry, Replay owner, runtime owner, or Common Entry route.

## Certified evidence preservation

The repair accepts the exact immutable R14B value as written by the existing
Invocation owner:

```text
invoked_by = PLATFORM_CORE_G31_INVOCATION_BINDING
```

It does not map that value to `AIGOL` or `AIGOL_GOVERNANCE`. Therefore it does
not require:

- changing the Invocation body;
- recalculating the Invocation artifact hash;
- changing the Invocation Replay;
- changing the Dispatch reference or hash;
- changing the Assignment reference or hash;
- changing the execution-request or packet reference;
- changing the Worker reference or hash;
- changing the canonical chain; or
- changing authority lineage.

The positive focused test takes an exact current-family Invocation artifact
with the R14B origin, preserves a deep copy, enters the existing
`start_execution` validation path, and proves that the input Invocation body
is byte-semantically unchanged as a Python mapping after validation.

## Fail-closed evidence

The focused R15B evidence proves:

1. `PLATFORM_CORE_G31_INVOCATION_BINDING` reaches the existing Execution
   Runtime construction boundary;
2. the exact Invocation reference and hash are preserved;
3. the Invocation artifact is not rewritten;
4. the pre-existing `AIGOL` origin remains accepted;
5. the pre-existing `AIGOL_GOVERNANCE` origin remains accepted; and
6. an unrecognized origin is rejected before an execution Replay destination
   is created.

The focused test file contains four tests and no Worker, Provider, command,
target-open, repository-mutation, or result-capture call.

R15B does not certify later R15A contracts that were intentionally not
classified after its first blocker. Those remaining direct Execution Runtime
contracts require a bounded readiness re-audit.

## Authority and stop boundary

The certified R14B lifecycle boundary remains the operational application
boundary for this generation:

```text
worker_selected = true
worker_assigned = true
worker_dispatched = true
dispatch_requested = true
worker_invoked = true
provider_invoked = false
execution_started = false
execution_requested = false
result_created = false
command_executed = false
target_opened = false
repository_mutated = false
```

R15B changes validation compatibility only. It does not bind Common Entry to
`start_execution` and does not advance a live lifecycle flag.

Temporary test captures demonstrate contract acceptance but are not certified
Common Entry runtime evidence and do not alter the accepted lifecycle state.

## Production and test responsibilities

Modified production symbol:

- `_validate_invocation_artifact`: recognizes the exact certified R14B origin
  through the existing allowlist while preserving every later check.

New focused test responsibilities:

- exact R14B-origin acceptance;
- exact Invocation reference/hash continuity;
- proof that the Invocation mapping is not rewritten;
- regression coverage for both prior certified origins; and
- fail-closed rejection before Replay write for an unknown origin.

No Common Entry, Invocation, Dispatch, Assignment, Worker, Provider,
repository-mutation, or canonical artifact implementation was changed.

## Validation

Validation ran after the bounded production and focused-test changes.

| Validation group | Passed | Skipped | Failed |
|---|---:|---:|---:|
| Focused R15B origin compatibility | 4 | 0 | 0 |
| Execution, R14B, architecture, and Governance regressions | 57 | 0 | 0 |
| Protected-evidence fixture preflight | 1 | 0 | 0 |
| Focused R15B final preflight | 4 | 0 | 0 |
| Complete repository suite, exactly once | 6806 | 4 | 0 |

The complete repository suite returned:

```text
6806 passed, 4 skipped, 0 failed in 4480.89s (1:14:40)
```

No complete-suite failure occurred. No failure classification, repair, exact
repaired-node validation, or second complete-suite run was required.

Targeted `py_compile` passed for:

```text
aigol/runtime/execution_runtime.py
tests/test_g31_24g_r04_r04_r15b_execution_invocation_origin_compatibility.py
```

Parent `git diff --check` and all three nested-repository
`git diff --check` checks passed before the complete suite. They are repeated
at final handoff after this report is added.

## Governance result

The read-only conformance engine remains:

`PARTIALLY_CONFORMANT`

- checks passed: 18;
- checks failed: 2;
- critical violations: 0;
- deterministic: true;
- fail-closed: true;
- read-only: true;
- report hash:
  `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea`.

The two known hook findings remain visible and unchanged:

1. the root expected and installed pre-commit hooks are missing; and
2. the system pre-commit hook lacks `promotion_gate_v02` and
   `check_layer_freeze`.

R15B does not repair or reinterpret these findings.

## Protected and nested state

All six versioned protected SHA-256 values equal the accepted R15A baseline:

| Protected path | SHA-256 |
|---|---|
| `diagnostic_evidence.json` | `21546ed151c165c6364aa914d892c34b117ef1ab664ae09d8e2c2a5327bcc8df` |
| `governed_return.json` | `ee57877ceea7d85bd9e3bb29aca64f3637384a7346a5b6a4c4f922c87cb2bcf7` |
| `lineage.json` | `8c47abb9a7c238c9f527e54dd88aa304edbca03b97ea630a4907b4ef139b3a08` |
| `provider_stderr.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `provider_stdout.txt` | `f2fec907b48e7162211f26bbe94352d40f4f6c4380ab3aa4256d072b7c602f30` |
| `governed_returns.jsonl` | `71b085174a274b870617c21810d9a496421985675ae0945f4b56bd3afe7b1118` |

The complete suite's protected-evidence contract also requires the three
historically certified marker paths. They were restored as exact zero-byte
files before the suite and each has the canonical empty-file hash:

```text
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

No evidence content was generated in those paths.

The nested repositories remain clean at their accepted commits:

- `sapianta-domain-credit`:
  `8615e1e290471a67e4e764c6ab2138340bc7936f`;
- `sapianta_system`:
  `3183bab71f8f30397c0309dd2e6d846d14a11f66`;
- `sapianta-domain-trading`:
  `d3038dc4ba36ffbaee9161172b4c852e8e6acbda`.

## Rejected alternatives

R15B rejects:

- rewriting the R14B `invoked_by` field;
- regenerating an Invocation artifact hash;
- normalizing the R14B origin to an older origin;
- accepting arbitrary non-empty origins;
- bypassing `_validate_invocation_artifact`;
- moving the origin check to Common Entry;
- adding a G31-specific Execution Runtime;
- adding a second execution path;
- changing Worker or Provider execution;
- changing repository-mutation behavior; and
- bundling the later operational Common Entry-to-execution transition.

## Git state

Nothing is staged and no commit was created.

The scoped R15B source delta consists of:

- one modified production file;
- one new focused test file;
- one new governance report; and
- three restored zero-byte protected marker paths required by the complete
  suite's protected-evidence contract.

The six versioned runtime-evidence paths remain byte-for-byte unchanged and do
not appear in the R15B Git delta.

Exact final `git status --short`:

```text
 M aigol/runtime/execution_runtime.py
?? WORKER_INVOCATION_ARTIFACT_V1
?? WORKER_INVOKED
?? docs/governance/G31_24G_R04_R04_R15B_G31_EXECUTION_INVOCATION_ORIGIN_COMPATIBILITY_TRANSITION.md
?? invocation
?? tests/test_g31_24g_r04_r04_r15b_execution_invocation_origin_compatibility.py
```

## Verdict

The first deterministic R15A blocker is repaired through the existing exact
origin validation mechanism. The certified R14B Invocation origin is accepted
without changing its artifact or lineage, both pre-existing origins remain
accepted, and unknown origins remain fail-closed.

Deterministic verdict:

`G31_EXECUTION_INVOCATION_ORIGIN_COMPATIBILITY_OPERATIONAL`

Exactly one next state:

`G31_24G_R04_R04_R15C_WORKER_EXECUTION_OPERATIONAL_READINESS_REAUDIT_REQUIRED`

## Complete bounded G31-24G-R04-R04-R15C prompt

```text
# Generation 31-24G-R04-R04-R15C
# G31 Worker Execution Operational Readiness Re-audit

Certified baseline:

G0-G30 remain constitutionally closed.

Generation 31 has certified:

- Common Entry to Assignment;
- Common Entry to Dispatch;
- Common Entry to Invocation; and
- R15B Execution Invocation-origin compatibility.

R15B verdict:

G31_EXECUTION_INVOCATION_ORIGIN_COMPATIBILITY_OPERATIONAL

Objective:

Perform a bounded constitutional re-audit of whether the existing direct
Execution Runtime now accepts the exact certified R14B Invocation artifact and
Replay through every remaining execution-construction contract without
introducing a new execution path.

Rules:

- audit only;
- preserve the exact R14B Invocation artifact, hash, and Replay;
- preserve Dispatch, Assignment, request, authorization, execution-packet,
  Worker, chain, and authority lineage;
- inspect all remaining Execution Runtime gates in their exact order;
- identify only the first deterministic blocker and stop if one exists;
- if no blocker exists, certify
  G31_WORKER_EXECUTION_OPERATIONAL_READY;
- do not bind Common Entry to Execution Runtime;
- do not execute a Worker;
- do not invoke a Provider;
- do not execute commands;
- do not open or mutate a repository target;
- do not capture an execution result;
- do not change production or test code;
- do not stage; and
- do not commit.

Validation:

- static exact-contract inspection;
- read-only or temporary compatibility probes only where necessary;
- existing Execution Runtime regressions;
- R14B and R15B regressions;
- architecture and Governance checks;
- targeted py_compile;
- parent and nested git diff --check; and
- protected hash verification.

Deliver:

- architectural analysis;
- deterministic reasoning;
- first blocking contract, if any;
- minimal constitutional repair, if required;
- governance report;
- one deterministic verdict; and
- exactly one next state.
```
