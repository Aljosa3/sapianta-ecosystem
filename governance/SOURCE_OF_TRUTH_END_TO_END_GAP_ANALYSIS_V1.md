# Source Of Truth End-To-End Gap Analysis V1

Status: gap analysis.

## Gap Summary

AiGOL supports all required source categories at the component level, but the complete conversational source-of-truth path is not yet implemented as one runtime.

## Gap 1: No Unified Source Router

Current state:

- strategy selection exists;
- source-specific resolvers exist;
- conversation runtimes exist.

Missing:

```text
SOURCE_OF_TRUTH_ROUTER_V1
```

The missing router should choose exactly one source strategy for a prompt and invoke the matching resolver.

Impact:

```text
High
```

## Gap 2: Resolution Strategy Does Not Dispatch

`RESOLUTION_STRATEGY_RUNTIME_V1` records source choice, but does not call:

- replay resolver;
- constitutional-memory resolver;
- governance resolver;
- provider-assisted conversation runtime;
- self-resolution response path.

Impact:

```text
High
```

## Gap 3: Conversational Runtime Does Not Use All Source Resolvers

`CONVERSATION_RUNTIME_V1` is bounded around constitutional memory consultation.

`PROVIDER_ASSISTED_CONVERSATION_RUNTIME_V1` supports self-resolution and provider fallback.

Neither path currently integrates all of:

```text
REPLAY
CONSTITUTIONAL_MEMORY
GOVERNANCE
PROVIDER
SELF_RESOLUTION
```

Impact:

```text
High
```

## Gap 4: Ambiguous Prompt Precedence Is Not Unified

Ambiguous prompts can match multiple source categories.

Examples:

| Prompt | Possible sources |
| --- | --- |
| `What is AiGOL?` | `SELF_RESOLUTION`, `CONSTITUTIONAL_MEMORY`, `PROVIDER` |
| `Explain worker boundaries` | `CONSTITUTIONAL_MEMORY`, `GOVERNANCE`, `PROVIDER` |
| `What happened recently?` | `REPLAY`, `PROVIDER` |

Missing:

- canonical source precedence;
- tie-breaking evidence;
- replay-visible ambiguity handling.

Impact:

```text
Medium
```

## Gap 5: Replay Resolver Requires Explicit Replay Source

`REPLAY_RESOLUTION_STRATEGY_V1` requires an explicit replay source directory.

The conversational runtime does not yet supply the current session or operational replay source automatically.

Impact:

```text
Medium
```

## Gap 6: Provider Availability Remains Runtime-Dependent

Provider prompts can be answered only when:

- provider is registered;
- provider is available;
- provider response validates;
- provider text does not introduce authority-bearing content.

This is correct fail-closed behavior, but it prevents unconditional end-to-end certification for provider-backed prompts.

Impact:

```text
Medium
```

## Gap 7: Prompt Suite Is Representative, Not Exhaustive

The validation suite covers representative prompts for each source category.

It does not certify:

- multilingual prompts for every source;
- adversarial prompt injection for every source;
- multi-turn source continuity;
- source switching across turns;
- provider outage during mixed-source sessions.

Impact:

```text
Medium
```

## Gap 8: CLI End-To-End Source Evidence Is Not Replayed In This Validation

Existing conversational certification covers `aigol prompt submit`.

This validation did not rerun a new CLI epoch through one integrated source-of-truth router because that router does not yet exist.

Impact:

```text
High
```

## Final Gap Classification

The component architecture is ready.

The full conversational source-of-truth runtime remains ready with gaps.

```text
SOURCE_OF_TRUTH_END_TO_END_STATUS = READY_WITH_GAPS
```
