# FIRST_REAL_WORKFLOW_DISCOVERY_V1

## Status

`FIRST_REAL_WORKFLOW_DISCOVERY_STATUS = READY`

## Purpose

This milestone identifies real recurring workflows where AiGOL should be used instead of the current manual transport:

```text
Human
↓
ChatGPT
↓
Codex
↓
Terminal
```

The objective is workflow discovery only.

No runtime, governance model, replay model, authority model, provider, worker, or implementation change is introduced.

## Evidence Baseline

The current operational baseline includes:

- `aigol run-governed`;
- deterministic operator operation ids;
- filesystem create-file worker;
- governed authorization artifact;
- provider proposal envelope;
- operation replay summary;
- `aigol replay operation`;
- operator runtime support in `aigol replay verify`;
- weekly usage evidence showing 12 successful governed operations and 3 fail-closed attempts.

## Scoring Model

Each workflow is scored by:

- `EXECUTION_VALUE`;
- `EXPLANATION_READINESS`;
- `TRUST_EXPLANATION_SCORE`.

Values:

```text
LOW
MEDIUM
HIGH
```

## Workflow Candidate Matrix

| # | Workflow | Can AiGOL perform today? | Required worker | Execution Value | Explanation Readiness | Trust Explanation Score |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | Create governed milestone marker file | YES | Filesystem create-file | HIGH | HIGH | HIGH |
| 2 | Create governance evidence artifact skeleton | YES | Filesystem create-file | HIGH | HIGH | HIGH |
| 3 | Create ADR skeleton for a completed milestone | YES | Filesystem create-file | HIGH | HIGH | HIGH |
| 4 | Record operational usage log entry as file | YES | Filesystem create-file | HIGH | HIGH | HIGH |
| 5 | Create acceptance evidence JSON stub | YES | Filesystem create-file | HIGH | HIGH | HIGH |
| 6 | Create replay certification JSON stub | YES | Filesystem create-file | MEDIUM | HIGH | HIGH |
| 7 | Create bounded repository note or TODO marker | YES | Filesystem create-file | MEDIUM | HIGH | HIGH |
| 8 | Create release-readiness checklist file | YES | Filesystem create-file | MEDIUM | HIGH | HIGH |
| 9 | Verify existing operator replay by operation id | YES | Replay verification | HIGH | HIGH | HIGH |
| 10 | Summarize governed operation status | YES | Replay inspection | HIGH | HIGH | HIGH |
| 11 | Append to existing governance artifact | NO | Filesystem append/update | HIGH | MEDIUM | MEDIUM |
| 12 | Update existing certification JSON | NO | Structured JSON update | HIGH | MEDIUM | MEDIUM |
| 13 | Run test suite and capture result | NO | Test runner worker | HIGH | MEDIUM | MEDIUM |
| 14 | Inspect git status and summarize changes | NO | Repository inspection worker | HIGH | MEDIUM | MEDIUM |
| 15 | Create GitHub issue from governed evidence | NO | GitHub issue worker | MEDIUM | MEDIUM | MEDIUM |
| 16 | Generate weekly operation summary automatically | NO | Operation replay ledger/report worker | HIGH | HIGH | HIGH |

## Strongest Current Candidates

These workflows have:

```text
Execution Value = HIGH
Explanation Readiness = HIGH
```

and are usable today:

- create governed milestone marker file;
- create governance evidence artifact skeleton;
- create ADR skeleton for a completed milestone;
- record operational usage log entry as file;
- create acceptance evidence JSON stub;
- verify existing operator replay by operation id;
- summarize governed operation status.

## Key Finding

AiGOL should first be used for bounded governance and replay-evidence file creation, plus replay verification.

The strongest future candidate is:

```text
Operation replay ledger and weekly usage summary
```

because weekly usage already required manual counting and manual evidence aggregation.

## Final Classification

```text
FIRST_REAL_WORKFLOW_DISCOVERY_STATUS = READY
```
