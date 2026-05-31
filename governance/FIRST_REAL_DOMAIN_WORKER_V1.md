# FIRST_REAL_DOMAIN_WORKER_V1

## Status

`FIRST_REAL_DOMAIN_WORKER_STATUS = READY`

## Selected Domain

Selected worker:

```text
GITHUB_ISSUE_DRAFT_WORKER
```

Selected operation:

```text
CREATE_ISSUE_DRAFT
```

The worker creates a deterministic GitHub issue draft artifact for a known repository. It does not call the GitHub API, create a live GitHub issue, mutate a repository, create a branch, open a pull request, or perform autonomous coding.

## Why This Domain

GitHub issue intake is a practical domain operation because it turns unstructured provider output into reviewable project work. AiGOL adds value by requiring governed authorization, bounded scope, replay-visible evidence, and fail-closed validation before a domain artifact is created.

## Runtime Component

Implemented:

```text
aigol/workers/github_worker.py
```

Validation:

```text
tests/test_first_real_domain_worker_v1.py
```

## Governed Flow

```text
Human Request
↓
Provider Proposal
↓
Governed Authorization
↓
AUTHORIZED_WORKER_REQUEST_V1
↓
GITHUB_ISSUE_DRAFT_WORKER
↓
GitHub Issue Draft Artifact
↓
Replay
```

## Worker Requirements

The worker accepts only:

- `AUTHORIZED_WORKER_REQUEST_V1`
- `worker_id = GITHUB_ISSUE_DRAFT_WORKER`
- `authorized_scope = GITHUB_CREATE_ISSUE_DRAFT`
- `operation = CREATE_ISSUE_DRAFT`
- a known repository in `owner/name` form
- issue title, issue body, and bounded labels

## Explicit Non-Authority

The worker records:

```text
github_api_invoked = false
repository_mutated = false
authority = false
```

It never receives raw provider output, raw proposals, raw authorization artifacts, API tokens, API requests, network requests, dispatch requests, orchestration requests, memory mutation, or replay mutation.

## Replay Reconstruction

Replay reconstructs:

- proposal reference
- authorization identity
- authorized worker request
- target repository
- worker action
- issue draft artifact result
- domain boundary evidence

## Final Classification

```text
FIRST_REAL_DOMAIN_WORKER_STATUS = READY
```

