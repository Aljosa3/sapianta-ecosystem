# Generation 31-24G-R04-R04-R15D G31 Execution Capability Lineage Compatibility Transition

Status: completed bounded compatibility repair; stopped before Common Entry
execution binding and every live Worker-execution stage.

Date: 2026-07-24

Deterministic verdict:

`G31_EXECUTION_CAPABILITY_LINEAGE_COMPATIBILITY_OPERATIONAL`

Exactly one next state:

`G31_24G_R04_R04_R15E_WORKER_EXECUTION_OPERATIONAL_READINESS_REAUDIT_REQUIRED`

## Constitutional scope

This generation treats G0-G30, the accepted G31 Common Entry-to-Invocation
transition, the accepted R15B Invocation-origin compatibility repair, and the
R15C readiness audit as immutable certified baselines.

R15C identified exactly one first remaining blocker:

`R14B_CERTIFIED_CAPABILITY_NOT_PRESERVED_BY_EXECUTION_RUNTIME_NORMALIZATION`

R15D changes only the existing Execution Runtime capability source and its
existing Assignment validation. It preserves the exact certified Assignment
capability without changing the certified Invocation, Dispatch, Assignment,
Worker, request, authorization, execution-packet, chain, authority, or Replay
evidence.

The implementation and tests do not:

- call Common Entry;
- rewrite or regenerate a certified Invocation artifact;
- change certified artifact hashes;
- change Invocation or Assignment Replay ownership;
- add an Execution Runtime owner;
- execute a Worker;
- invoke a Provider;
- execute a command;
- open a mutation target;
- capture an execution result;
- change Worker or Provider execution;
- change repository-mutation behavior;
- stage files; or
- create a commit.

Tests use temporary pytest destinations only for the existing deterministic
execution-start construction boundary.

## Accepted baseline

The transition began from:

- branch: `master`;
- HEAD: `a82f272aa22889bdfc78b9728610ff40c6ef14e9`;
- HEAD subject:
  `docs(governance): re-audit worker execution readiness`;
- R15C verdict:
  `G31_WORKER_EXECUTION_OPERATIONAL_BLOCKED`;
- R15C blocker:
  `R14B_CERTIFIED_CAPABILITY_NOT_PRESERVED_BY_EXECUTION_RUNTIME_NORMALIZATION`;
- certified Worker:
  `FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER`;
- certified Worker role:
  `WORKER_ROLE`;
- certified capability:
  `REPLACE_EXISTING_TEXT_FILE`;
- direct Execution Runtime:
  `EXECUTION_RUNTIME_V1`.

The versioned worktree and all three nested repositories were clean at the
implementation boundary. The three historical zero-byte marker paths were
absent from the committed R15C baseline.

## Exact compatibility repair

Before R15D, current-family Invocation normalization supplied:

```text
capability_id = invocation.worker_role
```

and `EXECUTION_ARTIFACT_V1` copied:

```text
capability_id = invocation.capability_id
```

For the certified G31 chain that produced:

```text
WORKER_ROLE
```

instead of:

```text
REPLACE_EXISTING_TEXT_FILE
```

R15D removes the role-derived capability fallback. The current-family
Invocation remains valid without an invented `capability_id`.

The existing Assignment validator now:

1. requires the already-hashed Assignment artifact's exact non-empty
   `capability_id`; and
2. rejects a supplied Invocation `capability_id` if it contradicts the
   Assignment capability.

The existing execution artifact constructor now sources:

```text
capability_id = assignment.capability_id
```

The Assignment reference and hash are already required to match the
Invocation and Dispatch before the capability is accepted. Capability
therefore comes from existing certified lineage rather than a role alias,
Worker-name inference, new registry, or second runtime path.

## Immutable evidence preservation

The repair does not add `capability_id` to the R14B Invocation artifact.
Therefore it does not:

- change the Invocation body;
- recalculate the Invocation hash;
- change the Invocation result artifact;
- change the Invocation Replay;
- change the Dispatch artifact;
- change the Assignment artifact;
- change the Assignment hash;
- change the Worker artifact;
- change the execution-packet reference or hash;
- change authorization identity or hash; or
- change the canonical chain.

The exact Assignment artifact is a pre-existing required `start_execution`
input. R15D uses that existing evidence after its canonical hash, identity,
state, Worker, chain, and request-continuity checks.

## Fail-closed evidence

Focused tests use the deliberately unequal certified pair:

```text
worker_role = WORKER_ROLE
capability_id = REPLACE_EXISTING_TEXT_FILE
```

They prove:

1. the existing Execution Runtime constructs `EXECUTION_ARTIFACT_V1` with
   `REPLACE_EXISTING_TEXT_FILE`;
2. it does not substitute `WORKER_ROLE`;
3. the input Assignment mapping is not rewritten;
4. the input Invocation mapping is not rewritten;
5. the Invocation remains free of a manufactured `capability_id`;
6. an injected Invocation `capability_id = WORKER_ROLE` fails closed with a
   capability mismatch before Execution Replay write; and
7. a missing Assignment capability fails closed before Execution Replay
   write.

Existing R15B evidence continues to prove acceptance of the exact certified
Invocation origin and rejection of unrecognized origins.

## Minimality

The production delta is confined to:

```text
aigol.runtime.execution_runtime
```

It consists of:

- removing one role-derived normalization;
- removing one obsolete Invocation capability requirement;
- requiring and checking Assignment capability in the existing Assignment
  validator; and
- sourcing the execution artifact capability from the validated Assignment.

The production delta is five insertions and three deletions in one existing
file.

No new production file, helper, artifact family, Replay owner, registry,
Worker branch, alias table, execution path, Provider path, or mutation path was
added.

## Authority and stop boundary

The accepted application lifecycle boundary remains:

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
governance_mutated = false
replay_mutated = false
```

R15D is a compatibility repair only. It does not bind Common Entry to
`start_execution` and does not advance a live lifecycle flag.

Temporary focused-test execution artifacts are local compatibility evidence,
not certified Common Entry runtime evidence.

## Focused failure classification

The first focused implementation run returned:

```text
2 passed, 5 failed
```

Cause:

- the new Assignment capability check was initially placed in the preceding
  Dispatch validator;
- the current Dispatch artifact intentionally does not carry
  `capability_id`; and
- the five failures therefore closed at `capability_id is required` before
  reaching Assignment validation.

This was a local patch-placement error, not a certified-contract failure.

The check was moved to the existing Assignment validator required by R15C.
The exact focused R15B/R15D group then returned:

```text
7 passed, 0 skipped, 0 failed
```

No complete-suite failure occurred.

## Validation

| Validation group | Passed | Skipped | Failed |
|---|---:|---:|---:|
| Initial focused R15B/R15D run before placement correction | 2 | 0 | 5 |
| Corrected focused R15B/R15D run | 7 | 0 | 0 |
| Execution, R14B, architecture, and Governance regressions | 49 | 0 | 0 |
| Protected-evidence fixture preflight | 1 | 0 | 0 |
| Focused R15D final preflight | 3 | 0 | 0 |
| Complete repository suite, exactly once | 6809 | 4 | 0 |

The complete repository suite returned:

```text
6809 passed, 4 skipped, 0 failed in 4453.44s (1:14:13)
```

No complete-suite failure occurred. No complete-suite failure classification,
repair, exact repaired-node validation, or second complete-suite run was
required.

Targeted `py_compile` passed for:

```text
aigol/runtime/execution_runtime.py
tests/test_g31_24g_r04_r04_r15d_execution_capability_lineage_compatibility.py
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

R15D does not repair or reinterpret them.

## Protected and nested state

All six versioned protected SHA-256 values equal the accepted R15C baseline:

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

R15D rejects:

- adding capability to the R14B Invocation artifact;
- recomputing the R14B Invocation hash;
- changing Invocation or Assignment Replay;
- mapping `WORKER_ROLE` to `REPLACE_EXISTING_TEXT_FILE`;
- inferring capability from the Worker identity;
- accepting a contradictory Invocation capability;
- bypassing Assignment validation;
- adding a G31-specific Execution Runtime;
- adding a second execution path;
- modifying Worker or Provider execution; and
- bundling Common Entry-to-execution binding.

## Git state

Nothing is staged and no commit was created.

The scoped R15D delta consists of:

- one modified production file;
- one new focused test file;
- one new governance report; and
- three restored zero-byte protected marker paths required by the complete
  suite's protected-evidence contract.

The six versioned runtime-evidence paths remain byte-for-byte unchanged and do
not appear in the R15D Git delta.

Exact final `git status --short`:

```text
 M aigol/runtime/execution_runtime.py
?? WORKER_INVOCATION_ARTIFACT_V1
?? WORKER_INVOKED
?? docs/governance/G31_24G_R04_R04_R15D_G31_EXECUTION_CAPABILITY_LINEAGE_COMPATIBILITY_TRANSITION.md
?? invocation
?? tests/test_g31_24g_r04_r04_r15d_execution_capability_lineage_compatibility.py
```

## Verdict

The exact certified capability now comes from the already-validated Assignment
artifact and is preserved in the existing Execution artifact. Worker role is
no longer used as capability evidence, and contradictory or missing
capability evidence fails closed.

Deterministic verdict:

`G31_EXECUTION_CAPABILITY_LINEAGE_COMPATIBILITY_OPERATIONAL`

Exactly one next state:

`G31_24G_R04_R04_R15E_WORKER_EXECUTION_OPERATIONAL_READINESS_REAUDIT_REQUIRED`

## Complete bounded G31-24G-R04-R04-R15E prompt

```text
# Generation 31-24G-R04-R04-R15E
# G31 Worker Execution Operational Readiness Re-Audit

Certified baseline:

G0-G30 remain constitutionally closed.

Generation 31 has certified:

- Common Entry to Invocation;
- Execution Invocation-origin compatibility; and
- Execution capability-lineage compatibility.

R15D verdict:

G31_EXECUTION_CAPABILITY_LINEAGE_COMPATIBILITY_OPERATIONAL

Objective:

Repeat the bounded constitutional readiness audit for the existing direct
Worker Execution Runtime after R15D.

Rules:

- audit only;
- confirm the R15A origin blocker remains resolved;
- confirm the R15C capability-lineage blocker is resolved;
- inspect every remaining Execution Runtime contract in exact order;
- preserve the certified Invocation, Dispatch, Assignment, Worker, request,
  authorization, execution-packet, chain, capability, role, and authority
  lineage;
- identify only the first remaining deterministic blocker and stop if one
  exists;
- if no blocker remains, certify
  G31_WORKER_EXECUTION_OPERATIONAL_READY;
- do not bind Common Entry to Execution Runtime;
- do not execute a Worker;
- do not invoke a Provider;
- do not execute commands;
- do not open or mutate a repository target;
- do not capture an execution result;
- do not generate live Replay;
- do not change production or test code;
- do not stage; and
- do not commit.

Validation:

- static exact-contract inspection;
- existing certified R15B and R15D evidence;
- read-only Governance conformance;
- parent and nested git diff --check;
- protected hash verification; and
- no live execution workflow.

Deliver:

- architectural analysis;
- deterministic reasoning;
- confirmation of both repaired blockers;
- first remaining blocker, if any;
- governance report;
- one deterministic verdict; and
- exactly one next state.
```
