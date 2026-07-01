# G8-11 Existing File Mutation Specification V1

Status: existing file mutation specified.

Final verdict: EXISTING_FILE_MUTATION_SPECIFIED

## 1. Executive Summary

G8-11 specifies the smallest safe governed mutation of an existing repository file.

The certified G8-09 mutation proved that AiGOL can create exactly one new plaintext file through Platform Core, Governance, Worker Platform, and Replay without introducing a new authority layer.

The next mutation must extend that capability conservatively:

```text
Replace the full contents of exactly one existing plaintext file
inside an allowlisted non-authority workspace
only when the pre-mutation file hash matches the approved candidate.
```

This specification is not an implementation task. It does not authorize arbitrary editing, patch application, Git operations, commit creation, deployment, provider invocation, or mutation of governance authority artifacts.

The existing-file mutation must remain:

- governed;
- hash-bound;
- replay-visible;
- rollback-aware;
- single-file only;
- plaintext only;
- fail-closed on conflict;
- executed only by the Worker Platform;
- coordinated by Platform Core;
- invisible to ACLI Next except as delegated capture and rendering.

## 2. Allowed Mutation Scope

Allowed operation:

```text
REPLACE_SINGLE_EXISTING_TEXT_FILE_IN_GOVERNED_WORKSPACE
```

Scope requirements:

| Field | Requirement |
| --- | --- |
| File count | Exactly one existing file. |
| File type | Plaintext UTF-8 only. |
| Target path | Relative path under an allowlisted non-authority workspace. |
| Existing file requirement | Target must exist and be a regular file before execution. |
| Mutation style | Full-file content replacement only. |
| Patch format | Deferred; no partial patch engine in this milestone. |
| Precondition | Current file hash must match the candidate's expected pre-mutation hash. |
| Postcondition | Resulting file hash must match the candidate's proposed content hash. |
| Size bound | File and replacement content must remain within a small replay-inspectable limit. |
| Encoding | UTF-8 text without null bytes. |
| Side effects | No side effects outside the one target file. |
| Git behavior | No Git status, staging, commit, branch, tag, push, checkout, or reset. |
| Deployment behavior | No deployment or server mutation. |

Recommended initial workspace:

```text
runtime/governed_mutation_workspace/
```

This workspace remains non-authority. Existing-file mutation of governance documents, constitutional artifacts, runtime source files, tests, release manifests, or `.github/governance/` is prohibited until separately specified and certified.

## 3. Prohibited Operations

The existing-file mutation Worker must not:

- create new files;
- delete files;
- rename or move files;
- mutate more than one file;
- mutate directories;
- mutate binary files;
- mutate symlinks;
- mutate files outside the allowlisted workspace;
- mutate `.git/`;
- mutate `.github/governance/`;
- mutate `docs/governance/`;
- mutate constitutional or release artifacts;
- run shell commands;
- run Git commands;
- invoke providers;
- dispatch additional Workers;
- infer approval from request prose;
- self-authorize;
- retry automatically after failure;
- create commits;
- deploy.

Any request containing prohibited operations must fail closed before mutation.

## 4. Safety Model

The safety model is hash-bound replacement with explicit conflict detection.

Required preconditions:

1. PGSP session exists.
2. Human request is replay-visible.
3. OCS creates an explicit existing-file mutation candidate.
4. Candidate includes the target path, expected pre-mutation hash, and proposed post-mutation hash.
5. Candidate declares a single-file full-replacement operation.
6. Governance validates the candidate and creates authorization evidence.
7. Human approval is explicit and bound to the candidate hash.
8. Worker Platform validates the authorization record.
9. Replay root is available and append-only.
10. Target path is inside the allowlisted workspace.
11. Target exists before execution.
12. Target is a regular plaintext UTF-8 file.
13. Current target hash matches the candidate's expected pre-mutation hash.
14. Proposed replacement content hash matches the candidate.
15. Rollback metadata is prepared before execution.
16. Validation plan is present before execution.

Fail-closed triggers:

- missing candidate;
- missing human approval;
- missing Governance authorization;
- missing replay root;
- target path escape;
- target missing;
- target not a regular file;
- target hash mismatch;
- binary or non-UTF-8 content;
- proposed content hash mismatch;
- prohibited path;
- prohibited operation flag;
- stale candidate;
- replay write failure;
- validation failure.

## 5. Human Approval Model

Human approval must be explicit and hash-bound.

Required approval phrase:

```text
confirm existing-file mutation <candidate_id> <candidate_hash>
```

The approval artifact must include:

- approval id;
- candidate id;
- candidate hash;
- target relative path;
- expected pre-mutation hash;
- proposed post-mutation hash;
- approved operation;
- approving human identity;
- approval timestamp;
- explicit non-authorization for Git, commit, deployment, provider invocation, and additional Workers.

Human approval does not authorize execution by itself. It is admissible evidence for Governance.

## 6. Governance Authorization

Governance remains the authority.

Governance authorization must include:

- authorization id;
- session id;
- candidate id;
- candidate hash;
- approval id;
- approval hash;
- operation type;
- target relative path;
- target workspace;
- expected pre-mutation hash;
- proposed post-mutation hash;
- authorized Worker id or Worker family;
- single-use policy;
- expiration or bounded validity;
- replay reference;
- explicit prohibition of Git, commit, deployment, provider invocation, and additional Worker dispatch.

Governance must not:

- execute the mutation;
- construct replacement content;
- bypass human approval;
- infer approval from natural language;
- certify success before Replay and validation evidence exist.

## 7. OCS Candidate Ownership

OCS owns mutation candidate formation.

The candidate artifact must include:

- candidate id;
- session id;
- requested operation;
- target workspace;
- target relative path;
- current file hash observed during planning;
- proposed replacement content;
- proposed replacement content hash;
- expected postcondition;
- validation recommendation;
- rollback recommendation;
- known risks;
- prohibited operation declaration;
- replay visibility flag.

OCS must not:

- authorize execution;
- execute the Worker;
- persist Replay evidence directly;
- mutate repository contents;
- call providers outside the certified EPP/PGSP path.

## 8. Worker Platform Execution

Worker Platform owns mutation execution.

The first existing-file mutation Worker should be modeled as:

```text
GOVERNED_REPLACE_EXISTING_TEXT_FILE_WORKER_V1
```

Worker responsibilities:

- validate request schema;
- validate Governance authorization hash;
- validate target workspace;
- validate relative path containment;
- validate target existence;
- validate target is a regular file;
- read current content;
- compute current hash;
- compare current hash to expected pre-mutation hash;
- write replacement content exactly once;
- compute resulting hash;
- emit execution artifact;
- fail closed on any mismatch.

Worker must not:

- choose target files;
- authorize itself;
- construct replacement content;
- run shell commands;
- call Git;
- invoke providers;
- dispatch Workers;
- mutate multiple files.

## 9. Replay Evidence Model

Replay remains the evidence system.

Required replay artifacts:

| Artifact | Purpose |
| --- | --- |
| Mutation candidate | OCS proposal, target path, pre-hash, and post-hash. |
| Human approval | Explicit hash-bound approval. |
| Governance authorization | Authorized scope and constraints. |
| Worker request | Worker-facing bounded mutation request. |
| Pre-mutation state | Target exists, path containment, pre-hash, file size, encoding check. |
| Worker result | Execution status, old hash, new hash, target path. |
| Post-mutation validation | File exists, new hash matches, one-file mutation scope preserved. |
| Rollback metadata | Original content hash and restoration conditions. |
| Completion summary | Final status, replay reference, and preserved non-goals. |

Replay reconstruction must verify:

- artifact ordering;
- wrapper hashes;
- artifact hashes;
- candidate-to-approval continuity;
- approval-to-authorization continuity;
- authorization-to-Worker-request continuity;
- pre-mutation hash matches candidate;
- Worker result old hash matches pre-mutation hash;
- Worker result new hash matches candidate post-hash;
- validation hash matches Worker result;
- rollback metadata preserves original hash;
- completion links all prior evidence.

Missing replay evidence must block success claims.

## 10. Rollback Requirements

Rollback metadata must be generated before or immediately after successful execution and must be replay-visible.

Rollback metadata must include:

- rollback id;
- candidate id;
- candidate hash;
- target relative path;
- pre-mutation content hash;
- post-mutation content hash;
- original content or a replay-bound restoration reference;
- rollback operation description;
- rollback authorization requirement;
- automatic rollback disabled;
- hash match requirement before rollback;
- prohibition on rollback if current file hash does not match the post-mutation hash.

Rollback operation:

```text
RESTORE_ORIGINAL_CONTENT_IF_CURRENT_HASH_MATCHES_AUTHORIZED_POST_HASH
```

Rollback execution is not part of this specification unless separately implemented and authorized.

## 11. Validation Requirements

Validation must be produced by Platform Core validation capability, not by ACLI Next.

Validation must confirm:

- target path stayed inside allowlisted workspace;
- target existed before mutation;
- target exists after mutation;
- target is a regular plaintext file;
- pre-mutation hash matched candidate expectation;
- post-mutation hash matches candidate proposed content;
- exactly one file was mutated;
- no Git operation occurred;
- no commit was created;
- no deployment occurred;
- no provider was invoked;
- no additional Worker was dispatched.

Validation failure must produce replay-visible fail-closed evidence.

## 12. File Integrity Protection

File integrity protection is mandatory.

Required hash checks:

| Checkpoint | Hash requirement |
| --- | --- |
| Candidate creation | Candidate records observed pre-mutation file hash and proposed replacement hash. |
| Approval | Approval binds candidate hash. |
| Authorization | Authorization binds candidate and approval hashes. |
| Worker request | Worker request binds authorization hash, pre-hash, and post-hash. |
| Pre-mutation validation | Current file hash must equal expected pre-hash. |
| Worker result | Old hash and new hash are recorded. |
| Post-mutation validation | Current file hash must equal proposed post-hash. |
| Rollback metadata | Original hash and post-mutation hash are preserved. |

Hash mismatch at any checkpoint must fail closed.

## 13. Conflict Detection

Conflict detection is required because existing files can change between planning and execution.

Conflict classes:

| Conflict | Required behavior |
| --- | --- |
| Target missing | Fail closed. |
| Target path changed | Fail closed. |
| Target hash differs from candidate pre-hash | Fail closed. |
| Target no longer plaintext UTF-8 | Fail closed. |
| Target is symlink or directory | Fail closed. |
| Workspace no longer allowlisted | Fail closed. |
| Candidate stale | Fail closed and route to new OCS candidate. |
| Replay artifact already exists | Fail closed. |

Conflict resolution belongs to OCS and Governance through a new candidate, not to the Worker.

## 14. ACLI Next Boundary

ACLI Next remains a thin entrypoint.

ACLI Next may:

- capture human request;
- render candidate summary;
- capture explicit confirmation;
- present replay identifiers;
- display completion summary.

ACLI Next must not:

- compute mutation candidates;
- authorize mutation;
- create Worker requests;
- execute file writes;
- persist Replay evidence as owner;
- validate file integrity as authority;
- perform rollback;
- run Git;
- call providers directly.

## 15. Acceptance Criteria

Existing-file mutation implementation will be acceptable when:

1. Exactly one existing plaintext file can be replaced through a governed Worker.
2. The target file must already exist.
3. The target path is restricted to an allowlisted non-authority workspace.
4. The candidate includes expected pre-mutation and proposed post-mutation hashes.
5. Human approval is explicit and bound to candidate hash.
6. Governance authorization is required and replay-visible.
7. Worker Platform performs the mutation.
8. Replay records candidate, approval, authorization, request, pre-state, result, validation, rollback metadata, and completion.
9. Hash mismatch fails closed before mutation.
10. Existing target conflict fails closed.
11. Post-mutation validation verifies the resulting hash.
12. Rollback metadata is hash-bound.
13. No Git, commit, deployment, provider invocation, or additional Worker dispatch occurs.
14. ACLI Next remains a thin adapter.
15. Targeted tests cover success, hash conflict, path escape, missing approval, missing authorization, replay reconstruction, and no-prohibited-operation surfaces.

## 16. Implementation Prerequisites

Required before implementation:

- OCS existing-file mutation candidate helper;
- Governance existing-file approval and authorization helper;
- Worker Platform replace-existing-text-file Worker;
- Replay evidence helper for existing-file mutation;
- validation helper for pre/post file integrity;
- rollback metadata helper for original content restoration;
- targeted tests;
- architecture review after implementation.

## 17. Validation Strategy

Specification validation:

```text
git diff --check
```

Future implementation validation:

- `git diff --check`;
- `python -m py_compile` for changed Python modules;
- targeted existing-file mutation tests;
- replay reconstruction test;
- hash-conflict fail-closed test;
- missing approval fail-closed test;
- missing authorization fail-closed test;
- no-Git/no-provider/no-deployment source-surface test.

## 18. Final Determination

The next governed mutation capability is specified as a single existing plaintext file full-content replacement under strict hash verification and conflict detection.

This specification preserves Platform Core ownership, Worker Platform execution, Governance authority, Replay evidence, and ACLI Next thin-entrypoint boundaries.

Final verdict: EXISTING_FILE_MUTATION_SPECIFIED
