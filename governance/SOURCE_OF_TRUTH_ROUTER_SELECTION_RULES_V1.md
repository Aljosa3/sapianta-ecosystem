# Source Of Truth Router Selection Rules V1

Status: selection rule foundation.

## Selection Principle

AiGOL selects the narrowest sufficient replay-safe source of truth.

Provider assistance is fallback synthesis, not default truth.

## Canonical Priority

```text
1. REPLAY
2. GOVERNANCE
3. CONSTITUTIONAL_MEMORY
4. SELF_RESOLUTION
5. PROVIDER
```

## Rule 1: REPLAY

Select `REPLAY` when the prompt asks about recorded activity.

Prompt markers include:

- `What happened recently?`
- `What changed?`
- `Show latest proposal.`
- `Show latest approval.`
- `What was the last operation?`
- `Summarize recent activity.`

`REPLAY` wins over `PROVIDER` because provider output cannot reconstruct replay truth.

Fail closed if replay evidence is unavailable, corrupt, or ambiguous.

## Rule 2: GOVERNANCE

Select `GOVERNANCE` when the prompt asks about governance artifacts, milestones, certifications, ADRs, or guarantees.

Prompt markers include:

- `What governance exists?`
- `What was certified?`
- `Which milestone was completed?`
- `What governance guarantees exist?`
- `What ADRs define this capability?`
- `What is the status of a governance milestone?`

`GOVERNANCE` wins over `PROVIDER` because provider output cannot determine governance truth.

Fail closed if governance evidence is missing, invalid, or corrupt.

## Rule 3: CONSTITUTIONAL_MEMORY

Select `CONSTITUTIONAL_MEMORY` when the prompt asks for constitutional, architectural, or boundary memory.

Prompt markers include:

- `What is AiGOL?`
- `What is replay?`
- `What are provider boundaries?`
- `What are worker boundaries?`
- `What is proposal approval?`
- `What is the purpose of governance?`
- `What are constitutional guarantees?`

`CONSTITUTIONAL_MEMORY` wins over `PROVIDER` because provider output cannot replace citation-bound constitutional evidence.

Fail closed if constitutional evidence or citation replay is missing, invalid, or corrupt.

## Rule 4: SELF_RESOLUTION

Select `SELF_RESOLUTION` when AiGOL can answer deterministically without external source evidence.

Examples:

- greeting;
- simple explanation request;
- known runtime capability summary;
- known non-authority explanation.

`SELF_RESOLUTION` wins over `PROVIDER` when deterministic answer coverage is sufficient.

Fail closed or fall through to `PROVIDER` only if deterministic coverage is insufficient and no higher-priority source applies.

## Rule 5: PROVIDER

Select `PROVIDER` only when:

- replay does not apply;
- governance does not apply;
- constitutional memory does not apply;
- self-resolution is insufficient;
- provider use is allowed;
- provider availability can be established;
- provider output will be validated by AiGOL.

Provider is appropriate for:

- open-ended explanation;
- creative writing;
- semantic paraphrase;
- general-domain synthesis.

Provider output remains non-authoritative.

## Competing Source Resolution

If multiple sources match, apply priority.

Examples:

| Prompt | Candidates | Selected |
| --- | --- | --- |
| `What happened recently?` | `REPLAY`, `PROVIDER` | `REPLAY` |
| `What governance exists?` | `GOVERNANCE`, `PROVIDER` | `GOVERNANCE` |
| `What is AiGOL?` | `CONSTITUTIONAL_MEMORY`, `SELF_RESOLUTION`, `PROVIDER` | `CONSTITUTIONAL_MEMORY` |
| `Hello` | `SELF_RESOLUTION`, `PROVIDER` | `SELF_RESOLUTION` |
| `Write a poem` | `PROVIDER` | `PROVIDER` |

## Fail-Closed Conditions

Routing must fail closed if:

- no candidate source exists;
- selected source is unsupported;
- selected source lacks required evidence;
- priority cannot resolve competing sources;
- provider authority is implied;
- worker execution is implied;
- replay evidence cannot be reconstructed;
- governance truth depends on provider output;
- constitutional truth depends on provider output;
- prompt requests hidden autonomy or governance bypass.

## Replay Requirements

Every router selection must record:

- prompt reference;
- prompt hash;
- candidate sources;
- selected source;
- source priority applied;
- evidence refs;
- rejected candidates;
- provider required flag;
- worker required flag;
- execution required flag;
- selection status;
- fail-closed reason when present.
