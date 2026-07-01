# G8-15 Governed Git Commit Specification V1

Status: governed Git commit specified.

Final verdict: GOVERNED_GIT_COMMIT_SPECIFIED

## 1. Executive Summary

G8-15 specifies the smallest safe governed local Git commit capability for AiGOL.

Generation 8 has already certified:

- ACLI Next as a thin human entrypoint;
- Platform Core responsibility boundaries;
- governed new-file mutation;
- governed existing-file mutation;
- governed validation execution;
- Worker Platform execution boundaries;
- Governance authorization boundaries;
- Replay evidence boundaries.

The next missing workflow bridge is local commit creation. This specification defines only the smallest governed Git commit operation:

```text
Create one local Git commit
from an explicitly approved set of already-present repository changes
after Governance authorization
through a Git Worker
with Replay-visible evidence.
```

This specification does not implement Git execution. It does not authorize Git push, branch management, merge, rebase, checkout, reset, remote interaction, deployment, provider invocation, or arbitrary shell execution.

The commit capability must remain:

- governed;
- local-only;
- hash-bound;
- replay-visible;
- single-commit only;
- fail-closed on conflict;
- executed only by the Worker Platform;
- coordinated by Platform Core;
- invisible to ACLI Next except as delegated request capture, approval capture, rendering, and Replay reference presentation.

## 2. Commit Scope

Allowed operation:

```text
CREATE_SINGLE_GOVERNED_LOCAL_GIT_COMMIT
```

Minimum supported commit class:

| Field | Requirement |
| --- | --- |
| Commit count | Exactly one local commit per Worker execution. |
| Repository | Current governed repository only. |
| Remote interaction | Prohibited. |
| Branch changes | Prohibited. Current branch must remain unchanged except for new commit pointer. |
| Commit source | Explicit OCS commit candidate only. |
| Staged content | Deterministic staged content model; no implicit broad staging. |
| Commit message | Governance-approved message only. |
| Author metadata | Explicitly recorded and approved. |
| Committer metadata | Explicitly recorded and approved or deterministically derived from runtime policy. |
| Precondition | Working tree and index state match the approved candidate. |
| Postcondition | New local commit hash is recorded in Replay. |
| Validation | Required validation evidence before commit authorization. |
| Rollback | Rollback recommendation and pre-commit reference required. |
| Push | Prohibited. |

The first implementation should support only content that has already been produced by certified governed mutation paths or explicitly approved as pre-existing local changes. It must not become a general-purpose Git terminal.

## 3. Staged Content Model

The first governed commit must use a deterministic staged content model.

Allowed staged content source:

```text
EXPLICIT_FILE_SET_STAGED_BY_COMMIT_WORKER
```

Requirements:

- OCS candidate lists every file path intended for the commit.
- Each file path is repository-relative.
- Each file path is inside the permitted commit scope.
- Each file has an expected content hash.
- Each file has a declared change type.
- Governance authorization binds the exact file set and hashes.
- Worker Platform stages only the authorized file set.
- Worker Platform verifies the index contains exactly the authorized staged content before committing.
- Replay records pre-stage state, post-stage state, commit result, and final repository state.

Allowed initial change types:

| Change Type | Requirement |
| --- | --- |
| `ADD_TEXT_FILE` | File was created through a certified governed mutation or explicitly approved local state. |
| `REPLACE_TEXT_FILE` | File was modified through a certified governed mutation or explicitly approved local state. |

Deferred change types:

- deletion;
- rename;
- mode change;
- symlink change;
- binary file addition;
- binary file modification;
- generated large artifacts;
- submodule changes.

The first commit Worker must not run `git add .`, `git add -A`, or any pathspec that can stage unapproved files.

## 4. Human Approval Model

Human approval must be explicit and hash-bound.

Required confirmation phrase:

```text
confirm governed git commit <candidate_id> <candidate_hash>
```

The approval artifact must bind:

- approval id;
- candidate id;
- candidate hash;
- repository identity;
- current branch name;
- current `HEAD` commit hash;
- staged content model;
- authorized file set;
- expected file hashes;
- validation evidence references;
- commit message;
- author metadata;
- committer metadata policy;
- approved operation;
- approving human identity;
- approval timestamp;
- explicit non-authorization for push, branch management, merge, rebase, checkout, reset, deployment, provider invocation, and additional Workers.

Human approval does not authorize commit execution by itself. It is evidence for Governance.

## 5. Governance Authorization

Governance remains the authority.

Governance authorization must include:

- authorization id;
- session id;
- candidate id;
- candidate hash;
- approval id;
- approval hash;
- operation type;
- repository identity;
- current branch name;
- expected pre-commit `HEAD`;
- authorized file set;
- expected file hashes;
- staged content model;
- commit message hash;
- author metadata hash;
- validation evidence references and hashes;
- rollback reference;
- authorized Worker id or Worker family;
- single-use policy;
- expiration or bounded validity;
- Replay reference;
- explicit prohibition of push, branch management, merge, rebase, checkout, reset, deployment, provider invocation, arbitrary shell execution, package installation, and additional Worker dispatch.

Governance must not:

- execute Git;
- stage files;
- create commits;
- mutate branches directly;
- infer approval from natural language;
- authorize a commit without candidate, approval, validation, and Replay prerequisites.

## 6. OCS Commit Candidate Ownership

OCS owns commit candidate formation.

The commit candidate artifact must include:

- candidate id;
- session id;
- requested operation;
- repository identity;
- current branch name;
- current `HEAD` commit hash;
- intended file set;
- declared change type per file;
- expected file content hash per file;
- source mutation evidence per file when available;
- validation evidence requirements;
- proposed commit message;
- proposed author metadata;
- committer metadata policy;
- rollback recommendation;
- known risks;
- prohibited operation declaration;
- Replay visibility flag.

OCS must not:

- execute Git;
- stage content;
- create commits;
- authorize the commit;
- persist Replay evidence directly;
- bypass Governance.

## 7. Platform Core Coordination

Platform Core coordinates governed commit execution.

The commit coordinator may:

1. receive an OCS commit candidate;
2. validate commit scope;
3. collect or reference validation evidence;
4. request Governance authorization;
5. request Worker Platform Git execution;
6. request Replay persistence;
7. assemble completion summary.

The coordinator must not:

- execute Git directly;
- construct unauthorized staged content;
- modify the index directly;
- create commit metadata outside the approved candidate;
- own Governance authorization;
- own Replay reconstruction;
- decide release readiness from commit existence alone.

The coordinator is not a second Git orchestration engine. It coordinates existing Platform Core components and delegates execution to the Worker Platform.

## 8. Git Worker Responsibilities

The Worker Platform owns Git execution.

The first Git Worker should be modeled as:

```text
GOVERNED_LOCAL_GIT_COMMIT_WORKER_V1
```

Worker responsibilities:

- validate Worker request schema;
- validate Governance authorization;
- validate repository root containment;
- validate current branch matches authorization;
- validate current `HEAD` matches authorization;
- validate working tree file hashes for authorized file set;
- inspect current index state;
- fail closed on unexpected staged content unless explicitly authorized;
- stage only the authorized file set;
- verify staged content hash matches authorization;
- create exactly one local commit with approved metadata;
- capture commit hash;
- capture post-commit `HEAD`;
- record Worker-side Replay evidence;
- report blocked, completed, or failed status.

Worker must not:

- choose files autonomously;
- run `git add .`;
- run `git add -A`;
- stage unapproved paths;
- amend commits;
- push;
- fetch;
- pull;
- clone;
- checkout branches;
- create branches;
- delete branches;
- merge;
- rebase;
- reset;
- tag;
- change remotes;
- deploy;
- invoke providers;
- run arbitrary shell commands;
- dispatch additional Workers.

## 9. Replay Evidence Model

Replay remains the evidence system.

Required Replay artifacts:

| Artifact | Purpose |
| --- | --- |
| Commit candidate | OCS commit proposal and authorized file set. |
| Human approval | Hash-bound approval for candidate and message. |
| Validation evidence reference | Validation result artifacts required before commit. |
| Governance authorization | Authorized Worker, file set, metadata, and constraints. |
| Pre-stage repository state | Current branch, `HEAD`, index state, and file hashes. |
| Worker request | Authorized Git Worker request. |
| Staging result | Exact paths staged and staged-content verification. |
| Commit result | Commit hash, parent hash, metadata hash, and status. |
| Post-commit repository state | Final `HEAD`, branch, and clean/dirty state summary. |
| Completion summary | Final governed commit outcome and Replay reference. |

Replay reconstruction must verify:

- candidate hash;
- approval-to-candidate binding;
- validation evidence hash references;
- authorization-to-candidate binding;
- authorization-to-approval binding;
- pre-commit `HEAD` continuity;
- staged file set equality;
- file hash continuity;
- commit parent equals expected pre-commit `HEAD`;
- post-commit `HEAD` equals created commit hash;
- no prohibited Git operation evidence exists;
- completion links to the commit result.

Missing, stale, partial, or conflicting Replay evidence must block completion claims.

## 10. Rollback Interaction

The first governed Git commit capability must be rollback-aware but must not execute rollback automatically.

Required rollback metadata:

- pre-commit `HEAD`;
- current branch name;
- created commit hash when available;
- authorized file set;
- validation evidence references;
- recommended rollback action;
- statement that rollback execution is deferred unless separately governed.

Recommended first rollback action:

```text
manual governed review before any revert or reset
```

The commit Worker must not run `git reset`, `git revert`, checkout, or branch manipulation as part of the first commit capability.

Rollback execution remains a future certified capability.

## 11. Commit Metadata Model

Commit metadata must be deterministic and approved.

Required metadata:

- commit message subject;
- optional commit message body;
- author name;
- author email;
- committer name policy;
- committer email policy;
- timestamp policy;
- candidate id;
- Replay reference;
- Governance authorization id;
- validation evidence reference.

Recommended commit message footer:

```text
AiGOL-Candidate: <candidate_id>
AiGOL-Authorization: <authorization_id>
AiGOL-Replay: <replay_reference>
```

The footer must not include secrets, credentials, provider output, or large Replay payloads.

## 12. Prohibited Git Operations

The first governed Git commit capability must not perform:

- `git push`;
- `git fetch`;
- `git pull`;
- `git clone`;
- `git remote`;
- `git branch`;
- `git checkout`;
- `git switch`;
- `git merge`;
- `git rebase`;
- `git reset`;
- `git revert`;
- `git tag`;
- `git stash`;
- `git cherry-pick`;
- `git clean`;
- `git submodule`;
- `git worktree`;
- `git config` mutation;
- commit amend;
- interactive commit;
- hook installation;
- deployment;
- server mutation.

Permitted Git operations for the first implementation may include only the minimum required local read/stage/commit sequence, such as:

- inspect repository state;
- inspect current branch;
- inspect current `HEAD`;
- inspect index state;
- stage exact authorized file paths;
- create one local commit.

The exact command allowlist must be certified during implementation.

## 13. Failure Handling

Fail-closed triggers:

- missing candidate;
- missing human approval;
- missing Governance authorization;
- missing validation evidence;
- missing Replay root;
- repository root mismatch;
- current branch mismatch;
- `HEAD` mismatch;
- authorized file missing;
- authorized file hash mismatch;
- unexpected staged content;
- unauthorized unstaged changes when policy requires clean working tree;
- path outside repository;
- path outside authorized file set;
- prohibited Git operation requested;
- commit message mismatch;
- author metadata mismatch;
- Git command failure;
- Replay write failure;
- post-commit verification failure.

Failure output must include:

- failure class;
- failed checkpoint;
- Replay reference if available;
- Governance review route if required;
- recommended next safe action;
- explicit statement whether a commit was created;
- commit hash if a commit was created before failure;
- explicit statement that no push, branch operation, deployment, provider invocation, or remote interaction occurred.

## 14. ACLI Next Boundary

ACLI Next remains a thin entrypoint.

ACLI Next may:

- capture a human request;
- present a Platform Core commit proposal;
- capture explicit approval text;
- delegate commit execution request to Platform Core;
- render completion summary;
- present Replay identifiers.

ACLI Next must not:

- run Git;
- select commit file sets autonomously;
- stage files;
- create commits;
- construct commit authorization;
- persist Replay evidence;
- reconstruct Replay evidence;
- infer approval;
- decide release readiness;
- push or deploy.

Every future human interface, including Web, REST, Mobile, and Voice, must consume the same Platform Core governed commit service rather than implementing local Git logic.

## 15. Acceptance Criteria

Governed Git commit implementation will be acceptable when:

1. Exactly one local commit can be created through Worker Platform.
2. Git push and remote interaction are absent.
3. Branch management is absent.
4. Merge, rebase, checkout, reset, and revert are absent.
5. OCS owns commit candidate artifacts.
6. Human approval is explicit and candidate-hash-bound.
7. Governance creates single-use commit authorization.
8. Platform Core coordinates without executing Git directly.
9. Worker Platform stages only the authorized file set.
10. Worker Platform creates exactly one local commit.
11. Commit message and metadata are approval-bound.
12. Validation evidence is required before commit authorization.
13. Replay records candidate, approval, validation reference, authorization, pre-stage state, staging result, commit result, post-commit state, and completion.
14. Replay reconstruction verifies commit continuity.
15. Rollback metadata records pre-commit `HEAD` and created commit hash.
16. Failure states are fail-closed and Replay-visible where possible.
17. ACLI Next remains a thin adapter.
18. Targeted tests cover success, missing approval, missing authorization, validation absence, `HEAD` mismatch, unexpected staged content, unauthorized file, prohibited Git operation, and Replay reconstruction.

## 16. Implementation Prerequisites

Before implementation, the platform must have or introduce narrowly scoped helpers for:

- commit candidate artifact creation;
- commit approval artifact creation;
- Governance commit authorization;
- Git command allowlist;
- Git Worker request validation;
- Worker-side Git execution evidence;
- Platform Core commit replay persistence;
- commit replay reconstruction;
- rollback metadata artifact creation;
- completion capture rendering.

These helpers must reuse existing Platform Core patterns and must not introduce new authority layers.

## 17. Validation Strategy

Specification validation:

```text
git diff --check
```

Future implementation validation:

- `git diff --check`;
- `python -m py_compile` for changed Python modules;
- targeted governed Git commit tests;
- Replay reconstruction test;
- missing approval fail-closed test;
- missing authorization fail-closed test;
- validation evidence prerequisite test;
- `HEAD` mismatch fail-closed test;
- unexpected staged content fail-closed test;
- prohibited Git operation rejection test;
- no-push/no-remote assertion test;
- ACLI Next thin-entrypoint assertion test.

## 18. Final Determination

The smallest governed Git commit capability is specified as one local commit created by the Worker Platform from an explicitly authorized file set, after hash-bound human approval, Governance authorization, validation evidence, and Replay-visible evidence generation.

This preserves Platform Core coordination, Governance authority, Replay evidence ownership, Worker Platform execution ownership, and ACLI Next thin-entrypoint boundaries.

Final verdict: GOVERNED_GIT_COMMIT_SPECIFIED

## 19. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: GOVERNED_GIT_COMMIT_SPECIFIED
