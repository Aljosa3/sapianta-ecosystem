# Generation 31-24G-R04-R04-R15A G31 Worker Execution Operational Readiness Audit

Status: completed static constitutional audit; blocked at the first direct
Execution Runtime compatibility contract.

Date: 2026-07-24

Deterministic verdict:

`G31_WORKER_EXECUTION_OPERATIONAL_BLOCKED`

First deterministic constitutional blocker:

`R14B_CERTIFIED_INVOCATION_ORIGIN_NOT_ACCEPTED_BY_EXECUTION_RUNTIME`

Exactly one next state:

`G31_24G_R04_R04_R15B_EXECUTION_INVOCATION_ORIGIN_COMPATIBILITY_TRANSITION_REQUIRED`

## Constitutional scope

This generation treats G0-G30 Platform Core and the accepted G31 Common
Entry-to-Assignment, Common Entry-to-Dispatch, and Common Entry-to-Invocation
results as immutable certified baselines.

It performs only a static repository-evidence audit of whether the existing
direct Execution Runtime accepts the exact certified R14B Invocation artifact
and Replay without a new execution path.

The audit does not:

- call Common Entry;
- create or reconstruct a live Invocation;
- call `start_execution`;
- create an execution artifact;
- write an execution Replay;
- execute a Worker;
- invoke a Provider;
- execute a command;
- open a mutation target;
- capture an execution result;
- mutate a repository;
- change production or test code;
- stage files; or
- create a commit.

Exactly one governance report is added.

## Accepted baseline

The audit began from:

- branch: `master`;
- HEAD: `bc244a4284ef26523774998707847aadab510ce8`;
- HEAD subject:
  `feat(runtime): bind common entry to certified invocation transition`;
- R14B verdict:
  `G31_COMMON_ENTRY_TO_INVOCATION_OPERATIONAL`;
- R14B complete-suite result:
  `6802 passed, 4 skipped, 0 failed`;
- certified Invocation runtime:
  `AIGOL_WORKER_INVOCATION_RUNTIME_V1`;
- direct Execution Runtime:
  `EXECUTION_RUNTIME_V1`.

The worktree and all three nested repositories were clean at the audit
boundary.

## Direct Execution Runtime contract

The existing direct execution owner is:

```text
aigol.runtime.execution_runtime.start_execution
```

Its declared input includes:

```text
invocation_artifact
invocation_replay
dispatch_artifact
worker_assignment_artifact
canonical_chain_id
execution_metadata
execution_context
started_by
started_at
replay_reference
replay_dir
```

The owner therefore has an existing direct interface for an Invocation
artifact and Invocation Replay. No new execution owner or route is needed to
reach its validation boundary.

Before constructing an execution artifact, `start_execution` delegates the
Invocation body to `_validate_invocation_artifact`.

That validator first:

1. verifies the canonical artifact hash;
2. requires `WORKER_INVOCATION_ARTIFACT_V1`;
3. requires the canonical `WORKER_INVOKED`/`INVOKED` status; and
4. validates the Invocation origin.

The R14B artifact family and status are recognized by the direct Execution
Runtime. The first incompatible check is the origin check.

## Exact R14B Invocation origin

The accepted R14B Common Entry transition calls the existing Invocation owner
with:

```text
invoked_by = PLATFORM_CORE_G31_INVOCATION_BINDING
```

`invoke_dispatched_worker` copies that exact value into the immutable
`WORKER_INVOCATION_ARTIFACT_V1` body before computing its artifact hash.

R14B then reconstructs the Invocation Replay and certifies the resulting
artifact and Replay as the accepted Common Entry Invocation boundary.

Changing this field in the R14B artifact would change the artifact hash and
break the certified Invocation identity. The audit therefore treats the
origin value as immutable.

## First deterministic blocker

The direct Execution Runtime currently requires:

```text
invocation.invoked_by in {
    AIGOL,
    AIGOL_GOVERNANCE,
}
```

The exact R14B value is:

```text
PLATFORM_CORE_G31_INVOCATION_BINDING
```

Therefore the direct execution validator deterministically raises:

```text
execution failed closed: invocation must be AiGOL-created
```

This occurs after artifact-type and Invocation-status recognition but before
later chain, Worker, authority, Replay, execution-metadata, or
execution-context validation.

The existing direct Execution Runtime does not currently accept the certified
R14B Invocation artifact unchanged.

No later execution contract is classified in this audit because the
instructions require stopping immediately after the first deterministic
constitutional blocker.

## Deterministic reasoning

The incompatibility is independent of:

- repository contents;
- environment variables;
- filesystem timing;
- Worker availability;
- Provider availability;
- command execution;
- execution output;
- Replay destination contents; and
- mutation state.

It follows from two immutable source-level values:

```text
R14B artifact origin:
PLATFORM_CORE_G31_INVOCATION_BINDING

Execution Runtime accepted origins:
AIGOL
AIGOL_GOVERNANCE
```

The values are unequal, and the validator uses exact set membership.

No live probe is necessary to establish the result.

## Minimal constitutional repair

The smallest legitimate repair is a bounded, Worker-neutral compatibility
extension in the existing direct Execution Runtime origin validator.

It would add exactly the certified R14B Common Entry origin token:

```text
PLATFORM_CORE_G31_INVOCATION_BINDING
```

to the existing exact origin allowlist.

The bounded repair must:

- preserve `WORKER_INVOCATION_ARTIFACT_V1`;
- preserve the R14B Invocation identity and artifact hash;
- preserve the R14B Invocation Replay;
- preserve the existing Execution Runtime owner;
- preserve the existing execution artifact and Replay families;
- preserve all later Execution Runtime validation;
- remain Worker-neutral;
- reject every unrecognized origin;
- add no alias or synthetic Worker identity;
- add no second execution route; and
- stop before operational Common Entry execution binding.

The repair must not normalize the R14B origin to `AIGOL` or
`AIGOL_GOVERNANCE`, because doing so would reinterpret or rewrite certified
lineage.

No repair is implemented by R15A.

## Rejected shortcuts

The audit rejects:

- changing the certified R14B `invoked_by` field;
- recomputing the R14B Invocation artifact hash;
- rewriting the Invocation Replay;
- mapping the certified origin to a different origin token;
- bypassing `_validate_invocation_artifact`;
- calling a second execution owner;
- introducing a Common Entry-specific execution runtime;
- treating the selected Worker identity as execution authority;
- weakening the allowlist to accept arbitrary non-empty origins;
- executing a Worker to test compatibility; and
- proceeding to later execution checks before the first blocker is repaired.

## Authority and stop boundary

The accepted R14B state remains:

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

R15A does not advance any lifecycle flag.

## Static validation

Validation was limited to read-only evidence because the audit found the
first blocker before live Execution Runtime entry.

Completed checks:

- exact branch, HEAD, subject, and clean-worktree capture;
- exact R14B verdict and next-state inspection;
- source-level `start_execution` signature inspection;
- source-level R14B Invocation-origin inspection;
- source-level Execution Runtime origin-allowlist inspection;
- parent `git diff --check`;
- all three nested-repository `git diff --check` checks;
- nested-repository cleanliness and commit verification;
- protected-path SHA-256 verification; and
- the read-only Governance conformance engine.

No pytest group, live validation probe, Invocation reconstruction, or
execution Replay was run. This preserves the audit-only and no-live-Replay
boundary.

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

R15A does not repair or reinterpret them.

## Protected and nested state

All versioned protected SHA-256 values equal the accepted R14B baseline:

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

The historical zero-byte marker paths are absent from the committed R14B
baseline and remain absent. R15A does not recreate or reinterpret them.

## Git state

No production file or test file was changed. Nothing was staged and no commit
was created.

Exact final `git status --short`:

```text
?? docs/governance/G31_24G_R04_R04_R15A_G31_WORKER_EXECUTION_OPERATIONAL_READINESS_AUDIT.md
```

## Verdict

The direct Execution Runtime recognizes the certified R14B Invocation artifact
family and status but rejects its immutable Common Entry origin token.

The readiness certificate
`G31_WORKER_EXECUTION_OPERATIONAL_READY` is not issued.

Deterministic verdict:

`G31_WORKER_EXECUTION_OPERATIONAL_BLOCKED`

First deterministic constitutional blocker:

`R14B_CERTIFIED_INVOCATION_ORIGIN_NOT_ACCEPTED_BY_EXECUTION_RUNTIME`

Exactly one next state:

`G31_24G_R04_R04_R15B_EXECUTION_INVOCATION_ORIGIN_COMPATIBILITY_TRANSITION_REQUIRED`

## Complete bounded G31-24G-R04-R04-R15B prompt

```text
# Generation 31-24G-R04-R04-R15B
# G31 Execution Invocation-Origin Compatibility Transition

Certified baseline:

G0-G30 remain constitutionally closed.

Generation 31 has certified:

- Common Entry to Assignment;
- Common Entry to Dispatch; and
- Common Entry to Invocation.

R15A verdict:

G31_WORKER_EXECUTION_OPERATIONAL_BLOCKED

Verified blocker:

R14B_CERTIFIED_INVOCATION_ORIGIN_NOT_ACCEPTED_BY_EXECUTION_RUNTIME

Objective:

Implement the minimal Worker-neutral compatibility transition that permits
the existing direct Execution Runtime to recognize the exact certified R14B
Invocation origin without changing the R14B Invocation artifact, Replay,
identity, hash, or any parent lineage.

Requirements:

- modify only the existing exact Invocation-origin validation contract;
- accept `PLATFORM_CORE_G31_INVOCATION_BINDING` as a certified origin;
- retain the existing `AIGOL` and `AIGOL_GOVERNANCE` origins;
- reject every other origin;
- preserve all validation after the origin gate;
- preserve the existing Execution Runtime owner;
- preserve all artifact and Replay families;
- preserve Worker, Dispatch, Assignment, request, authorization,
  execution-packet, chain, and authority lineage;
- add no Worker-specific branch; and
- stop before Common Entry execution binding.

Do not:

- rewrite or regenerate R14B Invocation evidence;
- execute a Worker;
- invoke a Provider;
- execute commands;
- mutate a repository;
- capture execution results;
- introduce a second execution route;
- stage; or
- commit.

Validation:

- focused origin-contract tests;
- existing Execution Runtime regressions;
- R14B regressions;
- architecture and Governance checks;
- targeted py_compile;
- parent and nested git diff --check;
- protected hash verification.

Do not run a live Worker, Provider, command, or repository-mutation workflow.

Deliver:

- minimal implementation;
- focused tests;
- governance report;
- deterministic validation summary; and
- exactly one next state.
```
