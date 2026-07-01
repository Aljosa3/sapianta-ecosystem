# G8-13 Governed Validation Execution Specification V1

Status: governed validation execution specified.

Final verdict: GOVERNED_VALIDATION_EXECUTION_SPECIFIED

## 1. Executive Summary

G8-13 specifies the smallest safe governed validation execution capability for AiGOL.

Generation 8 has already certified:

- advisory workflow;
- read-only Worker handoff;
- governed new-file mutation;
- governed existing-file mutation;
- Platform Core coordination boundaries;
- Worker Platform execution boundaries.

The next missing workflow bridge is validation execution. This specification defines a narrowly allowlisted validation Worker that can run approved validation commands and record replay-bound results without becoming a general terminal, Git, commit, deployment, or shell execution facility.

The first governed validation capability must support only:

```text
Run one allowlisted validation command
with fixed arguments
inside the repository root
under Governance authorization
with timeout and replay-bound output capture.
```

This is a specification only. It does not implement validation execution, redesign Platform Core, introduce a new authority layer, or authorize arbitrary commands.

## 2. Supported Validation Scope

Allowed operation:

```text
RUN_SINGLE_ALLOWLISTED_VALIDATION_COMMAND
```

Minimum supported validation command class:

| Field | Requirement |
| --- | --- |
| Command count | Exactly one command per Worker execution. |
| Command source | Static allowlist only. |
| Arguments | Fixed allowlisted argument vector only. |
| Working directory | Repository root or explicitly allowlisted subdirectory. |
| Shell | Prohibited. Command must execute without shell expansion. |
| Environment | Minimal deterministic environment. |
| Timeout | Required. |
| Output capture | stdout and stderr captured with bounded size. |
| Exit code | Captured exactly. |
| Repository mutation | Prohibited. |
| Git | Prohibited. |
| Commit | Prohibited. |
| Deployment | Prohibited. |
| Provider invocation | Prohibited. |

Recommended initial allowlist:

```text
python -m pytest tests/test_g8_existing_file_mutation_runtime.py
python -m pytest tests/test_g8_first_mutating_worker_runtime.py
python -m py_compile <explicit module list>
```

The implementation may begin with one validation command and expand only through separate certification.

## 3. Prohibited Operations

The governed validation Worker must not:

- run arbitrary shell commands;
- invoke a shell such as `sh`, `bash`, `zsh`, `cmd`, or PowerShell;
- use shell metacharacter parsing;
- accept free-form command strings;
- run Git commands;
- create commits;
- stage files;
- modify branches;
- deploy;
- invoke providers;
- mutate repository files intentionally;
- delete files;
- write generated artifacts outside an allowlisted temporary output area;
- run package installers;
- access network resources;
- execute nested Workers;
- retry automatically after failure;
- infer authorization from request prose.

Any validation request containing prohibited operations must fail closed before execution.

## 4. Validation Worker Responsibilities

The Worker Platform owns validation execution.

The first validation Worker should be modeled as:

```text
GOVERNED_VALIDATION_COMMAND_WORKER_V1
```

Worker responsibilities:

- validate Worker request schema;
- validate Governance authorization;
- validate command id against allowlist;
- resolve command id to exact argv vector;
- validate working directory containment;
- reject shell execution;
- execute the command with timeout;
- capture exit code;
- capture bounded stdout;
- capture bounded stderr;
- compute output hashes;
- report timeout status;
- report validation status;
- record Worker-side replay evidence.

Worker must not:

- choose validation commands autonomously;
- authorize itself;
- interpret validation meaning as Governance;
- mutate repository state as a goal;
- run Git;
- commit;
- deploy;
- call providers;
- dispatch additional Workers.

## 5. Platform Core Coordination

Platform Core coordinates validation execution.

The coordinator may:

1. receive an OCS validation candidate;
2. validate candidate scope;
3. request Governance authorization;
4. request Worker Platform command execution;
5. request Replay persistence;
6. request validation result normalization;
7. assemble completion summary.

The coordinator must not:

- construct arbitrary commands;
- bypass the allowlist;
- execute commands directly;
- own Governance authorization;
- own Replay reconstruction;
- decide certification status from command output.

## 6. OCS Validation Candidate

OCS owns validation proposal formation.

The validation candidate artifact must include:

- candidate id;
- session id;
- validation purpose;
- command id;
- exact allowlisted argv reference;
- expected working directory;
- timeout;
- output size limit;
- expected success exit code;
- associated mutation or advisory plan reference if any;
- known risks;
- prohibited operation declaration;
- replay visibility flag.

OCS must not execute validation or authorize validation.

## 7. Governance Authorization

Governance remains the authority.

Governance authorization must include:

- authorization id;
- session id;
- candidate id;
- candidate hash;
- human approval id and hash if required;
- command id;
- exact argv hash;
- working directory;
- timeout;
- output size limit;
- authorized Worker id;
- single-use policy;
- replay reference;
- explicit prohibition of Git, commit, deployment, provider invocation, installation, network access, and additional Worker dispatch.

Governance must not:

- execute validation;
- interpret validation output as final certification by itself;
- create commits;
- deploy;
- infer approval from request text.

## 8. Human Approval Model

For the first validation execution, explicit human approval is required unless a prior governed session policy separately certifies validation auto-approval.

Required confirmation phrase:

```text
confirm validation <candidate_id> <candidate_hash>
```

The approval artifact must bind:

- candidate id;
- candidate hash;
- command id;
- argv hash;
- working directory;
- timeout;
- approved by;
- approved at.

Human approval does not authorize execution by itself. It is evidence for Governance.

## 9. Replay Evidence Model

Replay remains the evidence system.

Required replay artifacts:

| Artifact | Purpose |
| --- | --- |
| Validation candidate | OCS validation proposal and command id. |
| Human approval | Explicit confirmation bound to candidate hash. |
| Governance authorization | Authorized command, Worker, timeout, and constraints. |
| Worker request | Worker-facing command request. |
| Pre-execution state | Working directory, allowlist match, timeout, output limits. |
| Worker result | Exit code, timeout flag, stdout/stderr hashes, and status. |
| Result normalization | Platform Core validation result artifact. |
| Completion summary | Final validation execution status and replay reference. |

Replay reconstruction must verify:

- artifact ordering;
- wrapper hashes;
- artifact hashes;
- candidate-to-approval continuity;
- approval-to-authorization continuity;
- authorization-to-Worker-request continuity;
- command id and argv hash continuity;
- timeout and output limit continuity;
- Worker result hash continuity;
- completion linkage.

Missing replay evidence must block success claims.

## 10. Validation Result Recording

The validation result artifact must record:

- command id;
- argv hash;
- working directory;
- exit code;
- timed out flag;
- stdout hash;
- stderr hash;
- stdout excerpt or bounded output reference;
- stderr excerpt or bounded output reference;
- output truncation flags;
- validation status;
- replay reference;
- associated mutation or plan reference;
- non-mutation declaration.

Validation status values:

| Status | Meaning |
| --- | --- |
| `VALIDATION_PASSED` | Command exited with expected success exit code and did not time out. |
| `VALIDATION_FAILED` | Command completed with non-success exit code. |
| `VALIDATION_TIMED_OUT` | Command exceeded authorized timeout. |
| `VALIDATION_BLOCKED` | Preconditions failed before command execution. |
| `VALIDATION_REPLAY_INCOMPLETE` | Required replay evidence is missing or invalid. |

Validation result recording does not certify release readiness by itself.

## 11. Failure Handling

Failures must be replay-visible and fail closed.

Failure classes:

| Failure | Required behavior |
| --- | --- |
| Command not allowlisted | Block before execution. |
| Argument mismatch | Block before execution. |
| Missing Governance authorization | Block before execution. |
| Missing human approval | Block before execution unless separately certified. |
| Working directory escape | Block before execution. |
| Timeout | Terminate process if possible and record timeout evidence. |
| Non-zero exit code | Record validation failure, not infrastructure failure. |
| Output limit exceeded | Truncate safely, record truncation flag and hashes. |
| Replay write failure | Block success claim. |
| Worker execution exception | Record fail-closed Worker result if replay is available. |

Non-zero validation exit code is not a Platform failure. It is an admissible validation result.

## 12. Timeout Handling

Timeout is mandatory.

Timeout rules:

- every validation candidate declares timeout seconds;
- Governance authorizes the timeout;
- Worker enforces the timeout;
- timeout must be small for the initial capability;
- timeout result is replay-visible;
- timeout cannot trigger automatic retry;
- timeout cannot escalate to broader shell access.

Recommended initial timeout:

```text
30 seconds
```

Future longer-running validation requires separate review.

## 13. Allowed Validation Tools

Initial allowed tools must be explicit and minimal.

Recommended initial allowlist:

| Command id | Argv | Purpose |
| --- | --- | --- |
| `PYTEST_G8_EXISTING_FILE_MUTATION` | `python -m pytest tests/test_g8_existing_file_mutation_runtime.py` | Validate G8-12 path. |
| `PYTEST_G8_FIRST_MUTATION` | `python -m pytest tests/test_g8_first_mutating_worker_runtime.py` | Regression for G8-09 path. |
| `PY_COMPILE_G8_VALIDATION_TARGETS` | `python -m py_compile <explicit files>` | Compile changed runtime modules. |

Allowlist entries must include:

- command id;
- exact argv;
- working directory policy;
- timeout;
- output limit;
- expected success exit code;
- mutation policy;
- network policy.

No validation Worker may accept a raw command string.

## 14. Repository Safety Rules

The validation Worker must preserve repository safety:

- no intentional repository mutation;
- no Git operations;
- no commits;
- no deployment;
- no package installation;
- no network access;
- no environment mutation beyond the Worker process;
- no writes outside approved temporary capture paths;
- no deletion of files;
- no execution of generated unreviewed scripts.

If a validation tool incidentally creates cache files, the implementation must either:

- run with cache-disabled options where available;
- use an allowlisted temporary directory;
- record incidental output explicitly; or
- fail closed until cache behavior is certified.

## 15. ACLI Next Boundary

ACLI Next remains a thin entrypoint.

ACLI Next may:

- request validation execution through Platform Core;
- display command id and purpose;
- capture confirmation;
- render result summary;
- present replay reference.

ACLI Next must not:

- build argv vectors;
- bypass the allowlist;
- execute commands directly;
- interpret validation as certification;
- own Replay persistence;
- own Governance authorization;
- run shell commands.

## 16. Acceptance Criteria

Governed validation execution implementation will be acceptable when:

1. One allowlisted validation command can be executed through Worker Platform.
2. Raw command strings are rejected.
3. Shell execution is absent.
4. Governance authorization is required.
5. Human approval is explicit and replay-visible.
6. Timeout is enforced and replay-visible.
7. stdout and stderr are captured or bounded with hashes.
8. Exit code is recorded exactly.
9. Non-zero exit code records `VALIDATION_FAILED`.
10. Timeout records `VALIDATION_TIMED_OUT`.
11. Replay reconstructs validation execution.
12. No Git, commit, deployment, provider invocation, package installation, or network access is introduced.
13. ACLI Next remains a thin adapter.
14. Targeted tests cover success, validation failure, timeout, disallowed command, missing authorization, missing approval, replay reconstruction, and no-prohibited-operation surfaces.

## 17. Implementation Prerequisites

Required before implementation:

- validation command allowlist model;
- OCS validation candidate helper;
- Governance validation approval and authorization helper;
- Worker Platform validation command Worker;
- Replay evidence helper;
- validation result normalizer;
- timeout and output-bound policy;
- targeted tests;
- architecture review after implementation.

## 18. Validation Strategy

Specification validation:

```text
git diff --check
```

Future implementation validation:

- `git diff --check`;
- `python -m py_compile` for changed Python modules;
- targeted governed validation tests;
- timeout test;
- disallowed command fail-closed test;
- replay reconstruction test;
- no-shell/no-Git/no-provider/no-deployment source-surface test.

## 19. Final Determination

The smallest governed validation execution capability is specified as one allowlisted, non-shell validation command executed by the Worker Platform under Governance authorization with Replay-bound evidence and timeout handling.

This preserves Platform Core coordination, Governance authority, Replay evidence ownership, Worker Platform execution ownership, and ACLI Next thin-entrypoint boundaries.

Final verdict: GOVERNED_VALIDATION_EXECUTION_SPECIFIED
