# Generation 31-24G-R04-R04-R17B Filesystem Replace Worker Output to Result Capture Compatibility Audit

Status: completed audit-only constitutional compatibility determination.

Date: 2026-07-24

Deterministic verdict:

`G31_FILESYSTEM_REPLACE_WORKER_OUTPUT_TO_RESULT_CAPTURE_COMPATIBILITY_STRATEGY_DEFINED`

Exactly one next state:

`G31_24G_R04_R04_R17C_FILESYSTEM_REPLACE_WORKER_OUTPUT_TO_RESULT_CAPTURE_BINDING_IMPLEMENTATION_REQUIRED`

## Certified baseline and scope

G0-G30 and accepted Generation 31 evidence through R17A are treated as
constitutionally closed and immutable. The immediate baseline is:

- commit: `40d05eb837db60728501cf6883346a94818cd5d6`;
- subject:
  `docs(governance): audit worker result capture readiness`;
- R17A verdict:
  `G31_FILESYSTEM_REPLACE_WORKER_RESULT_CAPTURE_OPERATIONAL_BLOCKED`;
- R17A blocker:
  `R16C_FILESYSTEM_REPLACE_WORKER_TERMINAL_EVIDENCE_HAS_NO_CERTIFIED_RESULT_CAPTURE_OUTPUT_BINDING`.

This audit inspected only Worker output ownership, `artifact_hash` ownership,
completion and journal Replay ownership, execution-result ownership,
authority continuity, and fail-closed behavior at:

```text
Filesystem Replace Worker terminal output
-> Result Capture
```

No unrelated execution, result-validation, review, certification,
repository-mutation-certification, or termination phase was inspected.

No Worker, Provider, command, Result Capture, Replay, target, or repository
operation was executed.

## Constitutional compatibility determination

No additional constitutional blocker exists within the audited boundary.

The certified R16C path already retains every immutable input required to
authenticate and project the physical Worker outcome:

- the exact authenticated replacement request;
- the exact R14B Worker Invocation artifact and Replay;
- the exact Dispatch and Assignment lineage carried by Invocation;
- the exact request/execution-packet identity and hash;
- the exact R15F Execution artifact, returned Replay artifact,
  reconstruction, and Replay reference;
- the R16C Filesystem Replace Worker terminal capture and `capture_hash`; and
- the exact seven-event Worker reconstruction, Replay reference, Replay hash,
  artifact count, completion artifact, and completion wrapper hash.

The Invocation permits exactly the authenticated `target_path` as its output.
Its forbidden operations are:

- `PROVIDER_INVOCATION`;
- `SHELL_COMMAND_EXECUTION`; and
- `MUTATION_OUTSIDE_AUTHENTICATED_TARGET`.

The actual Worker operation, `REPLACE_EXISTING_TEXT_FILE`, is therefore
within the certified scope and does not collide with a forbidden operation.

The incompatibility found by R17A is localized to representation and
authentication. It does not reflect missing execution truth, missing lineage,
or missing authority.

## Minimum constitutional compatibility strategy

The minimum adaptation is one narrow
Filesystem-Replace-Worker-output-to-Result-Capture binding between the
unchanged R16C Worker continuation and the unchanged existing Result Capture
owner.

The binding must not become a second Worker, mutation owner, Replay owner, or
Result Capture owner. It may only:

1. authenticate the already-produced Worker terminal evidence;
2. project that evidence into the existing canonical `worker_output` input
   shape;
3. invoke existing Result Capture exactly once; and
4. reconstruct and verify the two unchanged evidence chains.

This is consistent with the repository's existing narrow
transport-to-Result-Capture binding pattern. It does not require a change to
the Filesystem Replace Worker, Result Capture, Execution Runtime, or either
Replay format.

## Worker-output artifact contract

The binding must create one deterministic, non-authoritative
`FILESYSTEM_REPLACE_WORKER_OUTPUT_ARTIFACT_V1` only after validating an exact
successful R16C terminal state.

The artifact must preserve the fields already required by
`worker_result_capture_runtime`:

- `worker_output_id`;
- Worker identity, family, and role;
- Worker Invocation reference;
- Dispatch reference;
- Authorization reference;
- execution-packet reference;
- canonical chain identity;
- `produced_outputs = [authenticated target_path]`;
- `operations = [REPLACE_EXISTING_TEXT_FILE]`;
- replay visibility;
- creation time; and
- a payload.

Its payload must bind, without copying ownership:

- authenticated request identity and hash;
- Authorization identity and hash;
- R15F Execution identity, artifact hash, Replay reference, and Replay hash;
- R16C terminal `capture_hash`;
- Worker Replay reference and full Replay hash;
- Worker Replay artifact count;
- exact event sequence;
- completion artifact hash;
- completion wrapper hash;
- expected postimage hash and replacement mode; and
- successful terminal flags, including Provider and command absence.

`artifact_hash` must be the canonical hash of the complete output artifact
body. The compatibility binding owns creation of this derived envelope and
its hash. It does not own or reinterpret the execution result: the immutable
Worker Replay and terminal capture remain the source of result truth.

The output identity must be deterministically bound to the exact Invocation
and completion wrapper so that a different execution, completion, or replay
cannot alias the same output.

## Completion, journal, and Replay ownership

Before creating the output artifact, the binding must use the existing
Filesystem Replace Worker reconstructor and require exactly:

```text
request
-> consumption
-> journal
-> started
-> atomic
-> result
-> completion
```

It must require:

- `latest_event = MUTATION_COMPLETED`;
- seven immutable artifacts;
- exact request and Authorization continuity;
- the terminal capture's Replay hash and count to equal reconstruction;
- `execution_status = COMPLETED`;
- `repository_mutated = true`;
- no restoration, recovery, or termination;
- no Provider invocation or command execution; and
- exact postimage and mode continuity with the authenticated request.

The Worker remains sole owner of the journal, post-write validation,
completion artifact, predecessor chain, and Worker Replay reconstruction.
The binding references their hashes and must never append, copy, rewrite, or
branch that Replay.

Result Capture remains sole owner of its existing four-step evidence,
classification, capture, and result Replay. It records the projected
`worker_output` hash and payload hash without acquiring Worker mutation or
journal authority.

## Invocation and Execution continuity

The binding must supply unchanged Result Capture with:

- the exact R14B Worker Invocation artifact;
- the exact Invocation Replay reference;
- the exact R15F Execution artifact;
- the exact Execution returned Replay artifact; and
- the exact Execution Replay reference.

Result Capture's existing validators then preserve Invocation, Dispatch,
Assignment, Authorization, execution-packet, Worker, canonical-chain,
Execution, Replay, and authority continuity.

The R15F Execution artifact remains `EXECUTING` and start-only. Capturing a
Worker result must not rewrite it, claim final Execution certification, or set
`completion_recorded` or `result_certified` in that artifact. Worker mutation
completion and final Execution certification remain distinct constitutional
states.

The existing generic `default_worker_output_for_invocation` is not admissible
for this path because it does not bind the physical Worker terminal capture
or mutation Replay.

## Fail-closed requirements

The compatibility binding must fail before Result Capture on:

- any terminal-capture or `capture_hash` mismatch;
- any request, Authorization, Worker, Invocation, Dispatch, Assignment,
  packet, capability, chain, or Execution mismatch;
- any Worker Replay shape, predecessor, hash, journal, result, or completion
  mismatch;
- termination, restoration, recovery, incomplete mutation, or an unexpected
  event;
- output outside the exact authenticated target;
- a forbidden operation;
- Provider or command authority;
- cross-session Replay or capture destinations; or
- reuse of the same completion wrapper, Worker Replay hash, output identity,
  or output payload.

After existing Result Capture returns, the binding must reconstruct its Replay
and require:

- `WORKER_RESULT_CAPTURED`;
- exact Worker-output artifact hash;
- exact Worker-output payload hash;
- exact Invocation and Execution identities;
- `result_created = true`;
- `result_validated = false`;
- no post-execution review or final certification; and
- no governance or Replay mutation.

Only then may Common Entry expose the Result Capture state. The physical
Worker must not execute again, Authorization must not be consumed again, and
the binding must not fall back to generic or synthetic output.

## Ownership summary

| Evidence or action | Constitutional owner |
| --- | --- |
| Physical replacement, journal, post-write validation, completion | Existing Filesystem Replace Worker |
| Worker mutation Replay and reconstruction | Existing Filesystem Replace Worker |
| Derived output envelope and `artifact_hash` | Narrow compatibility binding |
| Invocation, Dispatch, Assignment, packet, and Execution truth | Existing certified spine owners |
| Result Capture evidence and Replay | Existing Result Capture runtime |
| Result validation and final Execution certification | Out of R17B scope |

No owner is displaced, and no second execution or mutation path is required.

## Static validation

Targeted `python -m py_compile` passed for:

- `aigol/workers/filesystem_replace_worker.py`;
- `aigol/runtime/human_interface_runtime_entry_service.py`;
- `aigol/runtime/worker_result_capture_runtime.py`;
- `aigol/runtime/worker_invocation_runtime.py`;
- `aigol/runtime/execution_runtime.py`; and
- `aigol/runtime/codex_transport_to_worker_result_capture_binding_runtime.py`.

Parent `git diff --check` and all three nested-repository
`git diff --check` checks passed.

The nested repositories remain clean at:

- `sapianta-domain-credit`:
  `8615e1e290471a67e4e764c6ab2138340bc7936f`;
- `sapianta_system`:
  `3183bab71f8f30397c0309dd2e6d846d14a11f66`;
- `sapianta-domain-trading`:
  `d3038dc4ba36ffbaee9161172b4c852e8e6acbda`.

The six protected hashes equal the accepted R17A baseline:

| Protected path | SHA-256 |
| --- | --- |
| `diagnostic_evidence.json` | `21546ed151c165c6364aa914d892c34b117ef1ab664ae09d8e2c2a5327bcc8df` |
| `governed_return.json` | `ee57877ceea7d85bd9e3bb29aca64f3637384a7346a5b6a4c4f922c87cb2bcf7` |
| `lineage.json` | `8c47abb9a7c238c9f527e54dd88aa304edbca03b97ea630a4907b4ef139b3a08` |
| `provider_stderr.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `provider_stdout.txt` | `f2fec907b48e7162211f26bbe94352d40f4f6c4380ab3aa4256d072b7c602f30` |
| `governed_returns.jsonl` | `71b085174a274b870617c21810d9a496421985675ae0945f4b56bd3afe7b1118` |

No production, test, Replay, protected, or nested-repository file was changed.
Nothing was staged or committed. This governance report is the sole R17B
artifact.
