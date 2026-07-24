# Generation 31-24G-R04-R04-R17C Filesystem Replace Worker Output to Result Capture Binding Implementation

Status: completed constitutional implementation.

Date: 2026-07-24

Deterministic verdict:

`G31_FILESYSTEM_REPLACE_WORKER_OUTPUT_TO_RESULT_CAPTURE_BINDING_IMPLEMENTED`

Exactly one next state:

`G31_24G_R04_R04_R18A_FILESYSTEM_REPLACE_WORKER_RESULT_VALIDATION_OPERATIONAL_READINESS_AUDIT_REQUIRED`

## Certified baseline and implementation scope

G0-G30 and accepted Generation 31 evidence through R17B are treated as
constitutionally closed and immutable. The immediate implementation baseline
is:

- commit: `410a27ab27718695e48c0aeef827f1fb498e0368`;
- subject:
  `docs(governance): define worker result capture compatibility`;
- R17B verdict:
  `G31_FILESYSTEM_REPLACE_WORKER_OUTPUT_TO_RESULT_CAPTURE_COMPATIBILITY_STRATEGY_DEFINED`;
- required R17C strategy:
  authenticate the completed Filesystem Replace Worker evidence, derive one
  non-authoritative Worker-output envelope, and invoke the existing Result
  Capture owner exactly once.

The implementation changes only the compatibility boundary after the
certified seven-event Filesystem Replace Worker terminal state and before the
existing Result Capture subsystem. It does not redesign the Worker, Result
Capture, Execution Runtime, Replay formats, authority model, or execution
protocol.

## Implementation

### Narrow Worker-output binding

`aigol.runtime.filesystem_replace_worker_output_to_result_capture_binding_runtime`
provides one capture entry and one reconstruction entry:

```text
capture_completed_filesystem_replace_worker_result
reconstruct_filesystem_replace_worker_result_capture_binding
```

Before creating output or invoking Result Capture, the capture entry
authenticates:

- the exact authenticated replacement request;
- the exact terminal Worker `capture_hash`;
- the exact seven-event Worker Replay and terminal completion;
- the exact journal, post-write result, and completion artifact and wrapper
  hashes;
- the exact Worker Invocation artifact and Replay;
- the exact Dispatch and Worker Assignment lineage;
- the Assignment-derived `REPLACE_EXISTING_TEXT_FILE` capability;
- the exact execution packet and canonical-chain identities;
- the exact R15F Execution artifact, returned artifact, Replay, and
  reconstruction; and
- the absence of Provider authority, command execution, final result
  validation, and final Execution certification.

The binding rejects cross-session Replay destinations, an existing Result
Capture destination, and reuse of an already-captured output or payload. Any
lineage, hash, event, ownership, terminal-state, or destination mismatch fails
before the existing Result Capture entry is called.

### Non-authoritative output artifact

After authentication, the binding constructs one deterministic
`FILESYSTEM_REPLACE_WORKER_OUTPUT_ARTIFACT_V1`. Its `artifact_hash` covers the
complete artifact body.

The envelope binds exactly:

- authenticated target and `REPLACE_EXISTING_TEXT_FILE` operation;
- request and Authorization identities and hashes;
- Worker Invocation identity and hash;
- Dispatch identity and hash;
- Worker Assignment identity, hash, and Assignment-derived capability;
- execution packet identity and hash;
- canonical chain identity;
- Execution identity, hash, Replay reference, and Replay hash;
- terminal Worker `capture_hash`;
- complete Worker Replay reference, hash, artifact count, and event sequence;
- journal artifact and wrapper hashes;
- post-write result artifact and wrapper hashes; and
- completion artifact and wrapper hashes.

The binding owns only this derived envelope and its hash. The existing Worker
remains the owner of mutation, journal, post-write validation, completion, and
the seven-event Worker Replay. The envelope does not create authority or
reinterpret the immutable Worker result.

### Existing Result Capture ownership

The binding invokes
`aigol.runtime.worker_result_capture_runtime.capture_worker_result` exactly
once with:

- the derived Worker-output envelope;
- the exact Worker Invocation artifact and Replay;
- the exact R15F Execution artifact and returned Replay; and
- a session-bounded Result Capture Replay destination.

The existing Result Capture subsystem remains the sole owner of its unchanged
four-event Replay and result-capture artifact. The binding reconstructs that
Replay and requires exact output artifact and payload hashes, Invocation,
Dispatch, Assignment, Authorization, execution-packet, Worker, chain, and
Execution continuity before exposing success.

The resulting state is deliberately bounded:

- `worker_result_captured = true`;
- `result_created = true`;
- `result_validated = false`;
- `post_execution_replay_reviewed = false`;
- `execution_certified = false`;
- `provider_invoked = false`;
- `command_executed = false`; and
- `repository_mutated = true`.

The certified R15F Execution artifact remains `EXECUTING` and start-only. R17C
does not rewrite it or claim final Execution certification.

### Immutable consumption-prefix compatibility

The existing Worker Invocation lineage loader previously required the entire
authenticated replacement Replay to equal the historical two-event
consumption state. After R16C, the authenticated Replay legitimately contains
seven immutable Worker events.

The loader now first authenticates the complete current Replay and then
reconstructs the immutable:

```text
request
-> consumption
```

prefix from the existing wrappers. It verifies both wrapper hashes, both
artifact hashes, predecessor continuity, request and Authorization
continuity, event types, and payloads. It does not write, truncate, branch, or
reinterpret Replay. This preserves the certified consumption evidence while
allowing existing Invocation and Result Capture reconstruction after later
Worker-owned appends.

### Common Entry continuation

Common Entry invokes the new compatibility capture exactly once after the
R16C Worker terminal capture and seven-event reconstruction succeed. It then
reconstructs the Result Capture binding and requires exact Worker capture,
Worker Replay, Execution, and bounded terminal truth before returning.

Common Entry does not invoke the Worker again, consume Authorization again,
use the generic synthetic Worker-output helper, invoke Provider, execute a
command, or certify the final Execution.

## Focused and regression evidence

The focused R17C module proves:

1. Common Entry invokes one binding and the binding invokes canonical Result
   Capture exactly once;
2. the output artifact hash covers the exact output body;
3. target, operation, Invocation, Dispatch, Assignment, capability, execution
   packet, chain, Execution, capture, journal, result, and completion hashes
   are preserved;
4. terminal-capture, Invocation, capability, Execution, journal, and
   completion substitution each fail before Result Capture;
5. duplicate completion and cross-session capture each fail before a second
   Result Capture; and
6. the Common Entry source contains one narrow binding call, no generic
   output path, and no Worker execution inside the binding.

Validation completed before the full-suite run:

- focused R17C tests: `9 passed`;
- Worker/Result Capture compatibility regressions: `53 passed`;
- R04-R17 execution-transition regressions: `203 passed`;
- focused Worker, Execution Runtime, and governance regressions: `55 passed`;
- targeted `py_compile`: passed; and
- parent `git diff --check`: passed.

Affected R13B, R14B, R15F, and R16C final-state regression assertions were
advanced from the certified Worker terminal state to the new captured-result
state. Their artifact-local historical boundary assertions remain unchanged.
The Invocation and Execution reconstruction counts and Result Capture Replay
directory expectations were updated to account for the one authentic
four-event capture.

Pre-full regression adaptation exposed three obsolete expectations concerning
the former no-result terminal state. Each affected node was updated and
validated before the complete-suite run.

## Complete repository suite

The complete repository suite was executed exactly once:

```text
6831 passed, 4 skipped in 4263.99s (1:11:03)
```

No failure occurred. No fixture repair or repaired-node validation was
required after the full-suite run, and the complete suite was not executed a
second time.

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
  `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea`.

The two existing accepted hook findings remain visible. R17C does not alter or
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

The six protected hashes equal the accepted R17B baseline after all focused,
regression, complete-suite, and final static validation:

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
