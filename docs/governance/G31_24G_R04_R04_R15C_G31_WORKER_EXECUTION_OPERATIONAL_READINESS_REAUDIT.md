# Generation 31-24G-R04-R04-R15C G31 Worker Execution Operational Readiness Re-Audit

Status: completed static constitutional re-audit; blocked at the first
remaining Execution Runtime capability-lineage contract.

Date: 2026-07-24

Deterministic verdict:

`G31_WORKER_EXECUTION_OPERATIONAL_BLOCKED`

Confirmation of R15A blocker resolution:

`R14B_CERTIFIED_INVOCATION_ORIGIN_ACCEPTED_BY_EXECUTION_RUNTIME`

First remaining deterministic constitutional blocker:

`R14B_CERTIFIED_CAPABILITY_NOT_PRESERVED_BY_EXECUTION_RUNTIME_NORMALIZATION`

Exactly one next state:

`G31_24G_R04_R04_R15D_EXECUTION_CAPABILITY_LINEAGE_COMPATIBILITY_TRANSITION_REQUIRED`

## Constitutional scope

This generation treats G0-G30, the accepted G31 Common Entry-to-Invocation
transition, and the accepted R15B Invocation-origin compatibility repair as
immutable certified baselines.

It repeats the static constitutional readiness audit for the existing direct
Execution Runtime after R15B. The inspection follows the runtime validation
order and stops at the first remaining deterministic constitutional blocker.

The audit does not:

- call Common Entry;
- call `start_execution`;
- construct an execution artifact;
- write or reconstruct live Replay;
- execute a Worker;
- invoke a Provider;
- execute a command;
- open a mutation target;
- capture an execution result;
- change production or test code;
- stage files; or
- create a commit.

Exactly one governance report is added.

## Accepted baseline

The audit began from:

- branch: `master`;
- HEAD: `ba1d3751716bb6993146f765b6c73746f6ac8d88`;
- HEAD subject:
  `feat(runtime): accept certified invocation binding origin`;
- R14B verdict:
  `G31_COMMON_ENTRY_TO_INVOCATION_OPERATIONAL`;
- R15B verdict:
  `G31_EXECUTION_INVOCATION_ORIGIN_COMPATIBILITY_OPERATIONAL`;
- direct Execution Runtime:
  `EXECUTION_RUNTIME_V1`;
- certified Worker:
  `FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER`;
- certified Worker role:
  `WORKER_ROLE`;
- certified capability:
  `REPLACE_EXISTING_TEXT_FILE`.

The parent worktree and all three nested repositories were clean at the R15C
audit boundary. The historical zero-byte marker paths were absent from the
committed R15B baseline and remain absent.

## R15A blocker resolution

R15A stopped at:

`R14B_CERTIFIED_INVOCATION_ORIGIN_NOT_ACCEPTED_BY_EXECUTION_RUNTIME`

The exact certified R14B Invocation origin is:

```text
PLATFORM_CORE_G31_INVOCATION_BINDING
```

The existing `_validate_invocation_artifact` allowlist now contains:

```text
AIGOL
AIGOL_GOVERNANCE
PLATFORM_CORE_G31_INVOCATION_BINDING
```

The immutable R14B value therefore passes the exact origin membership check
without normalization, aliasing, or artifact rewriting.

R15B also contains focused evidence that:

- the exact R14B origin reaches the existing execution-construction boundary;
- the Invocation reference and hash are preserved;
- the Invocation mapping is not rewritten;
- both pre-existing origins remain accepted; and
- an unknown origin still fails before an Execution Replay write.

The R15A blocker is resolved.

## Exact certified role and capability

The accepted G31 Assignment artifact distinguishes two independent identities:

```text
worker_role = WORKER_ROLE
capability_id = REPLACE_EXISTING_TEXT_FILE
```

The values are not aliases and are not interchangeable.

The Assignment runtime obtains:

- `worker_role` from the certified invocation request; and
- `capability_id` from the certified `WORKER_ARTIFACT_V1`.

The Assignment artifact preserves both values under separate fields before its
hash is computed.

The accepted Dispatch and Invocation families preserve `worker_role` but do
not copy `capability_id` into the immutable Invocation artifact. Capability
remains recoverable from the exact Assignment artifact that is already a
required direct input to `start_execution` and whose identity and hash are
carried through Dispatch and Invocation.

## First remaining deterministic blocker

Immediately after the repaired origin gate, Execution Runtime calls:

```text
_normalize_invocation_for_execution(invocation)
```

For the current Invocation family, that normalizer supplies:

```text
capability_id = invocation.worker_role
```

The exact R14B Invocation carries:

```text
worker_role = WORKER_ROLE
```

The exact certified Assignment carries:

```text
capability_id = REPLACE_EXISTING_TEXT_FILE
```

The resulting normalized execution input is therefore:

```text
capability_id = WORKER_ROLE
```

instead of:

```text
capability_id = REPLACE_EXISTING_TEXT_FILE
```

The execution artifact constructor then copies the normalized Invocation
`capability_id` directly into `EXECUTION_ARTIFACT_V1`.

No later Assignment validation compares the normalized Invocation capability
with `assignment.capability_id`. The current schema therefore accepts a
structurally valid chain while silently substituting the certified Worker role
for the certified capability.

This is a deterministic constitutional lineage blocker, even though the
runtime does not raise an exception. A successful structural return with the
wrong capability identity cannot certify Worker Execution readiness.

## Deterministic reasoning

The result follows from four source-level facts:

1. the certified Assignment capability is
   `REPLACE_EXISTING_TEXT_FILE`;
2. the certified Invocation role is `WORKER_ROLE`;
3. Execution Runtime derives absent Invocation capability from
   `invocation.worker_role`; and
4. `WORKER_ROLE != REPLACE_EXISTING_TEXT_FILE`.

The mismatch is independent of:

- filesystem state;
- Replay destination;
- timestamps;
- Worker availability;
- Provider availability;
- execution metadata;
- execution context;
- command behavior;
- execution result behavior; and
- repository contents.

No live validation probe is necessary to establish it.

The positive R15B compatibility test uses a synthetic current-family fixture
where the assignment capability and Worker role are both
`FILESYSTEM_MUTATION_WORKER`. That fixture correctly proves origin
compatibility, but equality in the fixture cannot prove preservation for the
certified G31 chain where role and capability are deliberately distinct.

## Why inspection stops here

The instructions require identifying only the first remaining deterministic
constitutional blocker and stopping immediately.

R15C therefore does not classify:

- later Invocation Replay checks;
- later Dispatch checks;
- later Assignment checks unrelated to capability;
- execution metadata projection;
- execution context projection;
- `started_by`;
- execution artifact reconstruction;
- Common Entry execution binding; or
- any downstream Worker, Provider, command, result, or mutation contract.

These contracts remain unclaimed rather than implicitly accepted.

## Minimal constitutional repair

The smallest legitimate repair is a bounded compatibility transition inside
the existing Execution Runtime.

It must use the exact already-required Assignment artifact as the capability
source because:

- the Assignment artifact contains the certified `capability_id`;
- its reference and hash are already carried by the Invocation;
- `start_execution` already requires the Assignment artifact;
- the existing Assignment validator already verifies assignment identity,
  hash, Worker identity, chain, request, state, and authority continuity; and
- this avoids rewriting the certified R14B Invocation artifact or Replay.

The repair should:

1. require a non-empty exact `assignment.capability_id`;
2. preserve it as the Execution artifact `capability_id`;
3. stop deriving capability from `invocation.worker_role`;
4. retain `worker_role` as role evidence rather than capability evidence;
5. preserve all existing origin, hash, Replay, Dispatch, Assignment, Worker,
   chain, authority, duplicate-execution, and stop-boundary checks;
6. prove the unequal certified pair
   `WORKER_ROLE / REPLACE_EXISTING_TEXT_FILE`;
7. prove role substitution fails closed or is impossible; and
8. stop before Common Entry-to-execution binding.

The repair must not:

- add `capability_id` to or recompute the R14B Invocation artifact;
- rewrite Invocation Replay;
- map `WORKER_ROLE` to `REPLACE_EXISTING_TEXT_FILE` through an alias table;
- infer capability from Worker name;
- add a Worker-specific execution branch;
- create a second Execution Runtime;
- weaken Assignment hash validation; or
- bundle operational Worker execution.

No repair is implemented by R15C.

## Authority and stop boundary

The accepted R14B/R15B lifecycle boundary remains:

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

R15C advances no lifecycle flag and generates no live artifact or Replay.

## Static validation

Validation was deliberately read-only and stopped at the first remaining
blocker.

Completed checks:

- exact branch, HEAD, subject, and clean-worktree capture;
- R14B and R15B verdict inspection;
- exact R15B origin-allowlist inspection;
- exact Assignment role/capability inspection;
- exact Invocation-field inspection;
- exact Execution Runtime normalization inspection;
- exact Execution artifact capability-source inspection;
- parent `git diff --check`;
- all three nested-repository `git diff --check` checks;
- nested-repository cleanliness and commit verification;
- protected-path SHA-256 verification; and
- the read-only Governance conformance engine.

No pytest group, `start_execution` call, live Invocation reconstruction,
execution artifact construction, execution Replay, Worker, Provider, command,
result, or mutation workflow was run.

The accepted R15B complete-suite evidence remains:

```text
6806 passed, 4 skipped, 0 failed in 4480.89s (1:14:40)
```

R15C does not rerun or reinterpret that suite.

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

R15C does not repair or reinterpret them.

## Protected and nested state

All versioned protected SHA-256 values equal the accepted R15B baseline:

| Protected path | SHA-256 |
|---|---|
| `diagnostic_evidence.json` | `21546ed151c165c6364aa914d892c34b117ef1ab664ae09d8e2c2a5327bcc8df` |
| `governed_return.json` | `ee57877ceea7d85bd9e3bb29aca64f3637384a7346a5b6a4c4f922c87cb2bcf7` |
| `lineage.json` | `8c47abb9a7c238c9f527e54dd88aa304edbca03b97ea630a4907b4ef139b3a08` |
| `provider_stderr.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `provider_stdout.txt` | `f2fec907b48e7162211f26bbe94352d40f4f6c4380ab3aa4256d072b7c602f30` |
| `governed_returns.jsonl` | `71b085174a274b870617c21810d9a496421985675ae0945f4b56bd3afe7b1118` |

The nested repositories remain clean at their accepted commits:

- `sapianta-domain-credit`:
  `8615e1e290471a67e4e764c6ab2138340bc7936f`;
- `sapianta_system`:
  `3183bab71f8f30397c0309dd2e6d846d14a11f66`;
- `sapianta-domain-trading`:
  `d3038dc4ba36ffbaee9161172b4c852e8e6acbda`.

The historical zero-byte marker paths remain absent. R15C does not recreate or
reinterpret them.

## Git state

No production file or test file was changed. Nothing is staged and no commit
was created.

The sole R15C delta is this governance report.

Exact final `git status --short`:

```text
?? docs/governance/G31_24G_R04_R04_R15C_G31_WORKER_EXECUTION_OPERATIONAL_READINESS_REAUDIT.md
```

## Verdict

The R15A Invocation-origin blocker is resolved.

Worker Execution is not yet constitutionally operationally ready because the
existing Execution Runtime substitutes the certified Worker role for the
certified capability when normalizing the exact R14B Invocation into the
Execution artifact.

The readiness certificate
`G31_WORKER_EXECUTION_OPERATIONAL_READY` is not issued.

Deterministic verdict:

`G31_WORKER_EXECUTION_OPERATIONAL_BLOCKED`

First remaining deterministic constitutional blocker:

`R14B_CERTIFIED_CAPABILITY_NOT_PRESERVED_BY_EXECUTION_RUNTIME_NORMALIZATION`

Exactly one next state:

`G31_24G_R04_R04_R15D_EXECUTION_CAPABILITY_LINEAGE_COMPATIBILITY_TRANSITION_REQUIRED`

## Complete bounded G31-24G-R04-R04-R15D prompt

```text
# Generation 31-24G-R04-R04-R15D
# G31 Execution Capability-Lineage Compatibility Transition

Certified baseline:

G0-G30 remain constitutionally closed.

Generation 31 has certified:

- Common Entry to Invocation; and
- Execution Invocation-origin compatibility.

R15C verdict:

G31_WORKER_EXECUTION_OPERATIONAL_BLOCKED

Verified blocker:

R14B_CERTIFIED_CAPABILITY_NOT_PRESERVED_BY_EXECUTION_RUNTIME_NORMALIZATION

Objective:

Implement the minimal Worker-neutral Execution Runtime compatibility repair
that preserves the exact certified Assignment capability in the existing
Execution artifact without changing the R14B Invocation artifact or Replay.

Requirements:

- reuse the existing direct `start_execution` owner;
- reuse the exact required `WORKER_ASSIGNMENT_ARTIFACT_V1`;
- require its exact non-empty `capability_id`;
- preserve that value as `EXECUTION_ARTIFACT_V1.capability_id`;
- stop deriving capability from `invocation.worker_role`;
- retain Worker role as role evidence, not capability evidence;
- preserve Assignment reference/hash continuity;
- preserve Invocation, Dispatch, Worker, request, authorization,
  execution-packet, chain, and authority lineage;
- retain every existing fail-closed validation;
- prove `WORKER_ROLE` remains distinct from
  `REPLACE_EXISTING_TEXT_FILE`;
- reject or make impossible role-for-capability substitution; and
- stop before Common Entry-to-execution binding.

Do not:

- modify or regenerate the certified R14B Invocation artifact;
- modify Invocation Replay;
- add a capability alias;
- infer capability from Worker name;
- add a Worker-specific branch;
- create a new Execution Runtime or path;
- execute a Worker;
- invoke a Provider;
- execute commands;
- mutate a repository target;
- capture execution results;
- stage; or
- commit.

Validation:

- focused unequal-role/capability tests;
- existing R15B origin regressions;
- existing Execution Runtime regressions;
- R14B regressions;
- architecture and Governance checks;
- targeted py_compile;
- parent and nested git diff --check;
- protected hash verification; and
- complete repository suite exactly once if required by the bounded
  implementation generation.

Deliver:

- minimal implementation;
- focused tests;
- governance report;
- deterministic validation summary;
- one deterministic verdict; and
- exactly one next state.
```
