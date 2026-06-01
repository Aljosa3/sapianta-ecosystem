# FIRST_REAL_WORKFLOW_DISCOVERY_FINDINGS_V1

## Findings Summary

AiGOL currently provides the most value when a workflow has these properties:

- bounded filesystem creation;
- clear authorization scope;
- replay-visible proposal, authorization, worker result, and verification;
- simple artifact output;
- high explanation value from replay evidence.

AiGOL is not yet strongest for workflows that require mutation of existing files, test execution, repository inspection, external issue management, or automatic aggregation.

## Workflow Findings

| Workflow | Can perform today? | Authorization scope | Useful replay evidence | AiGOL value |
| --- | --- | --- | --- | --- |
| Governed milestone marker | YES | `FILESYSTEM_CREATE_FILE` | Proposal, authorization, worker result, replay verify | High audit value for milestone markers. |
| Governance artifact skeleton | YES | `FILESYSTEM_CREATE_FILE` | Proposal, authorization, file path, content hash | Converts artifact creation into replayable evidence. |
| ADR skeleton | YES | `FILESYSTEM_CREATE_FILE` | Proposal reason, authorization scope, worker result | High because ADR creation should be explainable. |
| Usage log entry file | YES | `FILESYSTEM_CREATE_FILE` | Operation id, file path, content hash | Strong fit for repeated evidence collection. |
| Acceptance JSON stub | YES | `FILESYSTEM_CREATE_FILE` | Proposal, authorization, content hash | Good fit when file is new and bounded. |
| Replay certification JSON stub | YES | `FILESYSTEM_CREATE_FILE` | Same as acceptance JSON | Useful, though less frequent. |
| Repository note/TODO marker | YES | `FILESYSTEM_CREATE_FILE` | File path and replay verification | Useful for bounded notes. |
| Release checklist file | YES | `FILESYSTEM_CREATE_FILE` | File creation evidence | Useful when checklist is new. |
| Replay verify by operation id | YES | Replay inspection only | Verification status, replay hashes, lineage | Strong immediate value. |
| Operation status summary | YES | Replay inspection only | Operator status, execution status, replay summary | Strong immediate value. |
| Append governance artifact | NO | Future append/update scope | Before/after diff, target path, content hash | High value, but worker absent. |
| Update certification JSON | NO | Future structured update scope | JSON diff, schema validation, hash | High value, but worker absent. |
| Run tests and capture result | NO | Future test-runner scope | command, stdout/stderr hashes, exit code | High value, but worker absent. |
| Inspect git status | NO | Future read-only repo inspection | changed files, status hash | High value, but worker absent. |
| Create GitHub issue | NO | Future GitHub issue scope | issue id, payload, API result | Medium value, worker absent. |
| Weekly usage summary | NO | Future replay report scope | operation index, counts, rates | Very high future fit from observed usage. |

## Explanation Findings

Current successful operator replay can explain:

- what happened;
- which proposal existed;
- which authorization was created;
- which worker executed;
- what file was created;
- which replay evidence supports the result;
- whether replay verification passed.

Current replay is weaker at explaining:

- why a human selected a specific workflow;
- whether artifact content was semantically correct;
- aggregate usage patterns without manual counting;
- early fail-closed attempts as full operation replay chains.

## Worker Findings

The current filesystem create-file worker is enough for new governance artifacts and marker files.

The next worker should not be chosen until replay/operator reporting is improved, except where the workflow is already obviously repeated.

## Priority Finding

The next phase should prioritize:

```text
Replay/operator reporting
```

over:

- new provider;
- new worker;
- orchestration;
- planning;
- reflection.
