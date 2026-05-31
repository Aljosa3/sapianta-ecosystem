# FIRST_USEFUL_AIGOL_V1

## Status

`FIRST_USEFUL_AIGOL_STATUS = READY`

## Purpose

This milestone answers the usefulness question:

```text
What can AiGOL do that is more valuable than a direct provider call?
```

The answer is not that AiGOL writes a file better than a provider can describe one. The value is that AiGOL turns an untrusted provider proposal into a bounded, authorized, replay-visible operation with audit evidence.

## Selected Minimal Domain

Selected domain:

```text
Configuration Management / Repository Operations
```

Operational form:

```text
Create one governed marker/configuration artifact.
```

The implementation uses the already-certified `FIRST_END_TO_END_GOVERNED_OPERATION_V1` path:

```text
Human
↓
Provider Proposal
↓
Governed Authorization
↓
Authorized Worker Request
↓
Filesystem Worker
↓
Replay
```

## Real User Request

Minimal real request:

```text
Create test.txt with FIRST_END_TO_END_GOVERNED_OPERATION_V1.
```

Useful interpretation:

```text
Create a small governed repository/configuration marker only after proposal, authorization, and replay evidence exist.
```

## Provider Alone

A direct provider call can:

- suggest creating the file;
- generate the intended content;
- explain why the file should exist.

A direct provider call does not by itself provide:

- governed authorization;
- bounded worker request formation;
- fail-closed scope enforcement;
- replay reconstruction of proposal, authorization, request, and execution;
- proof that the worker did not receive raw provider authority.

## AiGOL-Governed Execution

AiGOL adds:

- provider output remains proposal-only;
- authorization is explicit and governed;
- worker receives only `AUTHORIZED_WORKER_REQUEST_V1`;
- filesystem mutation is bounded to one relative filename;
- replay reconstructs the full chain;
- invalid, missing, ambiguous, or corrupted states fail closed.

## Candidate Domain Review

| Domain | Status | Reason |
| --- | --- | --- |
| Filesystem | Ready | Existing worker can create one bounded file after authorization. |
| Configuration Management | Selected | Uses filesystem execution to create a governed config/marker artifact with clear audit value. |
| Repository Operations | Partial | Current useful subset is marker/config artifact creation, not git operations. |
| Document Processing | Partial | Could benefit later, but no current document worker is needed for smallest proof. |
| Code Generation | Deferred | Would require generation/review semantics beyond the current minimal worker. |
| API Invocation | Deferred | Would add network/API execution and broader authorization scope. |

## Value Demonstrated

`FIRST_USEFUL_AIGOL_V1` demonstrates measurable value beyond direct provider use:

- one provider proposal becomes one governed authorization;
- one governed authorization becomes one authorized worker request;
- one worker executes one bounded operation;
- replay reconstructs human request, provider, proposal, authorization, request, worker execution, and result;
- fail-closed behavior is validated for missing proposal, missing authorization, invalid request, unknown worker, scope mismatch, append-only replay violation, and replay corruption.

## Final Classification

```text
FIRST_USEFUL_AIGOL_STATUS = READY
```

AiGOL is useful because it provides governed execution evidence, not because it replaces the provider.

