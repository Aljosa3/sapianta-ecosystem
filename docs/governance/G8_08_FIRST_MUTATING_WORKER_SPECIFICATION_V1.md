# G8-08 First Mutating Worker Specification V1

Status: first mutating Worker specified.

Final verdict: FIRST_MUTATING_WORKER_SPECIFIED

## 1. Executive Summary

G8-08 specifies the smallest governed repository mutation that AiGOL may perform through Platform Core while preserving certified authority boundaries.

The first mutating Worker must be a create-only file Worker with a tightly bounded scope:

```text
Create exactly one new plaintext file in an allowlisted non-authority repository workspace.
```

This milestone is a specification only. It does not implement mutation, authorize runtime mutation, redesign ACLI Next, redesign Platform Core, or introduce a new execution mechanism.

The first mutating Worker must extend the certified Worker Platform and existing governed mutation lineage. It must not bypass:

- PGSP;
- OCS;
- Governance;
- Replay;
- Worker Platform;
- canonical capability lookup;
- human confirmation.

The first governed mutation operation should be:

```text
CREATE_SINGLE_FILE_IN_GOVERNED_MUTATION_WORKSPACE
```

This operation proves the controlled execution path without modifying code, governance artifacts, release metadata, deployment state, `.git/`, or existing files.

## 2. Mutation Scope

Allowed first mutation:

| Field | Requirement |
| --- | --- |
| Operation | Create one new file only. |
| Target directory | Dedicated allowlisted non-authority repository workspace. |
| Target path | Relative path under the allowlisted workspace only. |
| File count | Exactly one. |
| File type | Plaintext UTF-8 only. |
| Existing file behavior | Target must not already exist. |
| Content source | Deterministic content from authorized Worker request. |
| Content size | Small bounded payload suitable for replay inspection. |
| Side effects | No side effects outside target file creation. |
| Git behavior | No staging, commit, branch, tag, push, or checkout. |
| Deployment behavior | No deployment or server mutation. |

Recommended initial workspace:

```text
runtime/governed_mutation_workspace/
```

The workspace must be created by implementation setup or explicitly approved initialization. The first mutating Worker must fail closed if the workspace does not exist, unless workspace creation is itself separately authorized and replay-visible.

## 3. Prohibited Operations

The first mutating Worker must not:

- modify existing files;
- delete files;
- rename files;
- move files;
- create directories dynamically unless separately authorized;
- mutate `.git/`;
- mutate `.github/governance/`;
- mutate `docs/governance/`;
- mutate constitutional artifacts;
- mutate release manifests;
- run arbitrary shell commands;
- run Git commands;
- invoke providers;
- dispatch additional Workers;
- create commits;
- deploy;
- execute generated code;
- infer approval from request text;
- self-authorize;
- retry mutation automatically after failure.

Any request containing prohibited operations must fail closed before mutation.

## 4. Safety Model

The first mutating Worker safety model is fail-closed and precondition-based.

Required preconditions:

1. PGSP session exists.
2. Human request is replay-visible.
3. UBTR/CSA/OCS lineage is present or referenced through PGSP.
4. OCS produces an explicit mutation candidate.
5. Governance creates mutation authorization evidence.
6. Human confirmation is explicit and bound to the mutation candidate hash.
7. Worker Platform validates the target Worker capability.
8. Replay root is available and append-only.
9. Target workspace is allowlisted.
10. Target path remains inside the allowlisted workspace.
11. Target file does not exist.
12. Content hash is known before execution.
13. Rollback plan exists before execution.
14. Validation plan exists before execution.

Required non-goals:

- no general-purpose patch engine;
- no autonomous code editing;
- no multi-file mutation;
- no implicit escalation from advisory plan to mutation;
- no mutation from ACLI Next directly.

## 5. Governance Flow

Governance flow:

```text
ACLI Next
-> PGSP session
-> OCS mutation candidate
-> Governance mutation authorization request
-> human confirmation bound to candidate hash
-> Governance authorization artifact
-> Worker Platform mutation request
-> Worker precondition validation
-> Worker execution
-> Replay result capture
-> validation
-> completion summary
```

Governance authorization must include:

- authorization id;
- session id;
- candidate mutation id;
- candidate mutation hash;
- human confirmation hash;
- target workspace;
- target relative path;
- operation type;
- allowed Worker id or Worker family;
- explicit non-authorization for Git, deployment, provider invocation, and additional Workers;
- expiration or single-use policy;
- replay reference;
- fail-closed conditions.

Governance must not:

- execute the Worker;
- choose provider behavior;
- create a commit;
- certify success before Replay and validation evidence exist.

## 6. OCS Interaction

OCS owns mutation proposal formation.

OCS must produce a mutation candidate containing:

- candidate id;
- candidate purpose;
- requested operation;
- target path;
- proposed content;
- proposed content hash;
- expected postcondition;
- validation recommendation;
- rollback recommendation;
- known risks;
- prohibited operation declaration.

OCS must not execute mutation. OCS output becomes admissible only after Governance authorization and human confirmation.

## 7. Worker Platform Interaction

The Worker Platform owns execution.

The first Worker should be modeled as:

```text
GOVERNED_CREATE_FILE_WORKER_V1
```

Worker responsibilities:

- validate request schema;
- validate authorization hash;
- validate target workspace;
- validate relative path;
- validate target absence;
- write exactly one file;
- compute resulting file hash;
- record execution artifact;
- report success or fail-closed status.

Worker must not:

- call OCS;
- call Governance;
- call providers;
- choose its own scope;
- mutate multiple files;
- execute shell commands;
- create commits.

## 8. Replay Model

Replay must record enough evidence to reconstruct the mutation without trusting current repository state.

Required replay artifacts:

| Artifact | Purpose |
| --- | --- |
| Mutation candidate | OCS proposal and proposed content hash. |
| Human confirmation | Explicit confirmation bound to candidate hash. |
| Governance authorization | Authorization scope and constraints. |
| Worker request | Worker-facing bounded mutation request. |
| Pre-mutation state | Target absence proof and workspace boundary evidence. |
| Execution result | File path, content hash, and Worker status. |
| Post-mutation validation | File exists, content hash matches, and no extra mutation detected. |
| Rollback plan | Hash-bound rollback conditions. |
| Completion summary | Final status, replay reference, and non-goals preserved. |

Replay reconstruction must verify:

- artifact ordering;
- artifact hashes;
- candidate-to-authorization continuity;
- authorization-to-worker-request continuity;
- target path containment;
- target absence before execution;
- created file hash after execution;
- no prohibited operation flags;
- validation result;
- completion status.

Missing replay evidence must block success.

## 9. Rollback Model

Rollback must be specified before execution.

For the first create-only Worker, rollback is:

```text
Delete the created file only if the file still exists at the authorized path and its hash exactly matches the Worker-created hash.
```

Rollback rules:

- rollback is not automatic unless separately authorized;
- rollback requires replay-visible rollback authorization;
- rollback must fail closed if the file hash differs;
- rollback must fail closed if the target path is outside the allowlist;
- rollback must not delete directories;
- rollback must not delete pre-existing files;
- rollback must record replay evidence.

If rollback cannot safely execute, the system must preserve the created file and route to Governance review.

## 10. Validation Model

Minimum validation after mutation:

1. Target file exists.
2. Target file is inside allowlisted workspace.
3. File content hash equals authorized proposed content hash.
4. Exactly one file was created.
5. No prohibited path was touched.
6. Replay artifacts reconstruct.
7. Completion summary reports mutation status accurately.

The first validation should be deterministic and local. It should not invoke providers and should not require broad test execution.

Optional later validation may add targeted command execution after separate certification.

## 11. Approval Model

Human approval must be explicit and structured.

Acceptable approval content:

```text
confirm mutation <candidate_id> <candidate_hash>
```

or an equivalent structured confirmation captured by the interface adapter.

Approval must not be inferred from:

- previous advisory confirmation;
- natural-language enthusiasm;
- request wording;
- OCS recommendation;
- Worker availability;
- provider output.

Approval must bind to the exact mutation candidate hash. Any candidate change invalidates approval.

## 12. Repository Safety Rules

The first mutating Worker must enforce:

- allowlist-only target workspace;
- relative path only;
- no path traversal;
- no symlink traversal;
- target must not exist;
- single file only;
- deterministic content;
- bounded file size;
- no binary content;
- no executable permission changes;
- no `.git/` access;
- no governance artifact mutation;
- no generated commit;
- no deployment.

Repository safety is a Worker Platform and Governance responsibility, not an ACLI Next responsibility.

## 13. PGSP Interaction

PGSP remains the governed session protocol.

PGSP responsibilities:

- preserve session identity;
- route human request and confirmation;
- expose UBTR, CSA, OCS, Governance, and Replay evidence;
- return structured result to interface adapter;
- preserve fail-closed state.

PGSP must not become a mutation engine. It transports and coordinates governed session evidence.

## 14. Implementation Prerequisites

Before implementation begins, the following must exist or be created:

- mutation candidate schema;
- Governance mutation authorization schema;
- Worker request schema;
- Worker execution result schema;
- replay reconstruction function for the mutation flow;
- allowlisted workspace policy;
- rollback request and rollback result schema;
- targeted validation routine;
- fail-closed tests for every precondition;
- ACLI Next adapter route that delegates to Platform Core only.

Implementation should reuse:

- existing Worker Platform concepts;
- existing repository mutation/file write Worker evidence where compatible;
- existing replay serialization;
- existing Governance authorization patterns;
- G8-06D Platform Core owner-helper decomposition;
- ACLI Next thin-entrypoint model.

## 15. Acceptance Criteria

The first mutating Worker implementation is acceptable only when:

1. It creates exactly one new file in the allowlisted workspace.
2. It cannot modify, delete, rename, or move existing files.
3. It cannot mutate governance, `.git/`, release, deployment, or server state.
4. It requires explicit human mutation approval bound to candidate hash.
5. It requires Governance mutation authorization.
6. It validates Worker capability before execution.
7. It records pre-mutation target absence.
8. It records execution result and resulting content hash.
9. It validates post-mutation state.
10. It provides a hash-bound rollback plan.
11. Replay reconstructs the full mutation lifecycle.
12. Missing replay, missing authorization, path escape, target collision, content hash mismatch, or prohibited scope fails closed.
13. ACLI Next remains a thin adapter and does not construct mutation policy.
14. No provider invocation, Git command, commit, deployment, or additional Worker dispatch occurs.
15. Targeted tests and `git diff --check` pass.

## 16. Deferred Operations

Deferred beyond the first mutating Worker:

- modifying existing files;
- deleting files;
- multi-file patches;
- code generation writes;
- test execution as mutation gate;
- automatic rollback;
- Git staging;
- commit creation;
- branch management;
- deployment;
- provider-assisted mutation;
- autonomous Worker sequencing.

Each deferred operation requires separate certification.

## 17. Validation Strategy

Documentation-only specification validation:

```text
git diff --check
```

Future implementation validation should include:

- `python -m py_compile` for changed Python modules;
- targeted first mutating Worker tests;
- replay reconstruction tests;
- target collision fail-closed test;
- path traversal fail-closed test;
- missing authorization fail-closed test;
- missing replay fail-closed test;
- rollback eligibility test;
- no-Git/no-deployment assertions;
- no-governance-mutation assertion.

## 18. Final Determination

The first mutating Worker is specified as a governed, create-only, single-file repository mutation in an allowlisted non-authority workspace.

This is the smallest mutation that proves controlled execution while preserving all certified Platform Core authority boundaries.

Final verdict: FIRST_MUTATING_WORKER_SPECIFIED
