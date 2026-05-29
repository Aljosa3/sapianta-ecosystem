# Provider Authority Separation V1

Status: implemented provider authority boundary.

## Authority Principle

Provider is proposal source only.

Provider is never:

- execution authority
- authorization authority
- governance authority
- replay authority
- worker authority

## Separation Rules

Provider output may be forwarded only into the external response attachment path.

Provider output must remain untrusted until AiGOL governance validates and authorizes downstream execution.

Provider identity does not imply trust or authority.

Provider replay evidence does not replace replay authority.

## Downstream Governance

AiGOL remains responsible for:

- validation
- authorization
- rejection
- replay recording
- governed return

Worker execution remains downstream and occurs only after authorization.

## Forbidden Provider Behavior

The provider boundary must not:

- call provider APIs
- hold API credentials
- execute tools
- invoke network transport
- authorize execution
- mutate replay
- mutate governance
- create capabilities
- orchestrate workflows
- create memory
- continue autonomously

## Certification

The first provider boundary preserves role separation:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```
