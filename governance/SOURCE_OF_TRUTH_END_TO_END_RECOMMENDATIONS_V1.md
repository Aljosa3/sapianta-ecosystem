# Source Of Truth End-To-End Recommendations V1

Status: recommendations.

## Recommendation 1: Implement A Unified Source Router

Create a narrow runtime:

```text
SOURCE_OF_TRUTH_ROUTER_V1
```

Responsibilities:

- detect source-of-truth category;
- select one supported strategy;
- persist strategy selection evidence;
- call the selected source resolver;
- normalize response shape;
- preserve replay visibility;
- fail closed on ambiguity.

## Recommendation 2: Canonicalize Source Precedence

Define runtime precedence before routing implementation.

Recommended default:

```text
REPLAY
GOVERNANCE
CONSTITUTIONAL_MEMORY
SELF_RESOLUTION
PROVIDER
```

Rationale:

- replay questions should use replay evidence;
- governance questions should use governance artifacts;
- constitutional questions should use constitutional memory;
- simple deterministic questions should self-resolve;
- open-ended synthesis should use provider fallback.

## Recommendation 3: Add Router-Level Prompt Suite Tests

Create tests for at least:

```text
Hello
Explain simply
What is AiGOL?
Explain worker boundaries
What was certified recently?
What governance exists?
What happened recently?
Show latest proposal
Explain AI alignment
Write a poem
```

Each test should assert:

- selected strategy;
- source resolver used;
- response status;
- replay visibility;
- fail-closed behavior when source evidence is absent.

## Recommendation 4: Normalize Source Response Shape

All source resolvers should return a common response envelope:

```text
response_id
selected_strategy
source_used
response_text
response_status
replay_reference
provider_used
worker_invoked
execution_requested
artifact_hash
```

This prevents the conversational runtime from needing source-specific response parsing.

## Recommendation 5: Make Replay Source Selection Explicit

For `REPLAY`, define how the router chooses:

- current prompt replay;
- current session replay;
- latest operational replay;
- explicit user-requested replay scope.

If replay source cannot be selected deterministically, fail closed.

## Recommendation 6: Preserve Provider As Last-Resort Synthesis

Provider should remain:

- proposal-only;
- validation-bound;
- replay-visible;
- non-authoritative;
- unavailable-safe.

Provider should not answer replay, governance, or constitutional questions when local evidence exists.

## Recommendation 7: Certify CLI Epoch After Router Implementation

After router implementation, run a new representative CLI validation epoch through:

```text
aigol prompt submit
```

The epoch should record:

- prompt;
- selected strategy;
- source used;
- response success;
- replay artifact paths;
- failure reason when failed closed.

## Final Recommendation

Proceed to router design or implementation before claiming full source-of-truth end-to-end certification.

Current status remains:

```text
SOURCE_OF_TRUTH_END_TO_END_STATUS = READY_WITH_GAPS
```
