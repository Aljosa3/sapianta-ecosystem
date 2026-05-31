# AIGOL_OPERATOR_GAP_ANALYSIS_V1

## What Operators Can Do Today

Operators can:

- inspect AiGOL status;
- generate ingress artifacts;
- validate governance continuity;
- preview continuity;
- inspect controlled execution handoff paths;
- inspect runtime contracts;
- run read-only runtime inspection;
- verify replay;
- inspect replay;
- list/latest replay;
- show runtime session summaries;
- inspect runtime, goal, and retry summaries;
- run a bounded read-only prompt flow through `aigol.runtime.operator_cli`;
- exercise provider, authorization, filesystem worker, and GitHub issue-draft worker paths programmatically.

## What Operators Cannot Do Today

Operators cannot yet invoke one canonical command such as:

```text
aigol operate github issue-draft ...
```

for the newest path:

```text
Provider Proposal
↓
Governed Authorization
↓
Authorized Worker Request
↓
GitHub Issue Draft Worker
↓
Replay
```

Operators also lack a single command that displays unified evidence across:

- provider proposal envelope;
- authorization record;
- authorized worker request;
- worker replay;
- final domain artifact.

## Minimum Missing Capability

The minimum missing capability is:

```text
operator-facing command contract for certified governed operation execution and evidence display
```

This should expose existing runtime components rather than create a new runtime.

## Important Gaps

| Gap | Severity | Impact |
| --- | --- | --- |
| No unified command for first real domain worker | High | Useful GitHub issue-draft operation is tested but not operator-friendly. |
| Fragmented CLI surfaces | Medium | Operators must know which CLI surface applies to status, runtime, replay, or live prompt. |
| Provider registry not operator-visible | Medium | Provider metadata exists, but no first-class CLI view. |
| Authorization runtime not operator-visible | Medium | Authorization evidence exists, but no first-class command to create/inspect it. |
| New replay chain not surfaced in existing replay CLIs | Medium | Provider/authorization/domain-worker replay is reconstructable programmatically but not yet summarized by operator replay CLI. |

## Non-Gaps

These do not require new architecture:

- governance validation;
- replay verification concepts;
- read-only runtime inspection;
- runtime summaries;
- fail-closed handling;
- provider proposal envelope model;
- authorization artifact model;
- authorized worker request model;
- domain worker replay model.

