# Source Of Truth Router Foundation V1

Status: foundation review.

Final classification:

```text
SOURCE_OF_TRUTH_ROUTER_FOUNDATION_STATUS = READY_WITH_GAPS
```

## Scope

This artifact defines the global source-of-truth routing boundary for AiGOL.

It does not implement routing, source resolver dispatch, execution, workers, provider invocation, approval changes, proposal mutation, CLI integration, or governance mutation.

## Context

AiGOL now has certified source strategies:

```text
SELF_RESOLUTION
PROVIDER
REPLAY
CONSTITUTIONAL_MEMORY
GOVERNANCE
```

The missing component is a global router that selects exactly one source strategy for a human prompt before response generation.

## 1. How Source Selection Is Performed

Source selection is performed by AiGOL using deterministic prompt classification and source evidence availability.

The router must:

1. receive a human prompt reference;
2. inspect prompt content;
3. enumerate candidate source strategies;
4. apply canonical source priority;
5. verify required evidence for the selected source;
6. record replay-visible selection evidence;
7. fail closed if no safe source can be selected.

Provider output may assist later response drafting only after AiGOL selects `PROVIDER`.

Provider output may not select the source of truth.

## 2. How Competing Sources Are Resolved

When multiple sources match, AiGOL selects the highest-priority sufficient source.

The router must record:

- all candidate sources;
- selected source;
- precedence applied;
- selection reason;
- rejected candidates;
- evidence references;
- fail-closed reason when applicable.

Ambiguity fails closed if:

- precedence does not resolve the conflict;
- required evidence is missing;
- provider authority is implied;
- governance or replay truth would depend on provider output.

## 3. Source Priority

Canonical source priority:

```text
1. REPLAY
2. GOVERNANCE
3. CONSTITUTIONAL_MEMORY
4. SELF_RESOLUTION
5. PROVIDER
```

Future strategies remain outside V1 routing:

```text
WORKER
COMBINED
```

## 4. When REPLAY Is Preferred Over PROVIDER

`REPLAY` is preferred when the prompt asks about:

- what happened;
- recent activity;
- latest proposal;
- latest approval;
- last operation;
- replay reconstruction;
- recorded provider or worker events;
- evidence continuity.

Provider must not infer replay truth when replay evidence is available or required.

If replay evidence is missing or corrupt, the router fails closed rather than asking a provider to guess.

## 5. When CONSTITUTIONAL_MEMORY Is Preferred Over PROVIDER

`CONSTITUTIONAL_MEMORY` is preferred when the prompt asks about:

- AiGOL identity;
- constitutional guarantees;
- provider boundaries;
- worker boundaries;
- proposal approval;
- purpose of governance;
- constitutional or architectural definitions.

Provider may not replace missing constitutional citations.

If constitutional memory evidence is missing, invalid, or corrupt, the router fails closed.

## 6. When GOVERNANCE Is Preferred Over PROVIDER

`GOVERNANCE` is preferred when the prompt asks about:

- certification status;
- ADRs;
- milestone status;
- governance guarantees;
- governance artifact inventory;
- governance rules;
- boundary guarantees.

Provider may phrase a response only if later allowed by a governed response path, but provider cannot determine governance truth.

## 7. When SELF_RESOLUTION Is Preferred

`SELF_RESOLUTION` is preferred when AiGOL can answer deterministically from local runtime knowledge without requiring citations, governance artifacts, replay evidence, or provider synthesis.

Examples:

- greetings;
- simple operator-facing summaries;
- known capability descriptions;
- known non-authority explanations.

If self-resolution is insufficient, the router may fall through to `PROVIDER` only when no higher-priority evidence source applies.

## 8. Replay Recording

The router must emit:

```text
SOURCE_OF_TRUTH_ROUTER_SELECTION_ARTIFACT_V1
```

Required events:

```text
SOURCE_OF_TRUTH_ROUTER_SELECTED
SOURCE_OF_TRUTH_ROUTER_RETURNED
```

Selection replay must include:

- prompt reference;
- candidate sources;
- selected source;
- source priority;
- selection reason;
- source evidence references;
- provider required flag;
- worker required flag;
- proposal lifecycle required flag;
- fail-closed reason when applicable;
- artifact hash.

## 9. Reconstruction

Replay reconstructs source selection by validating:

- selection event order;
- returned event order;
- wrapper hashes;
- artifact hashes;
- selected source is in candidate set;
- selected source follows priority;
- evidence references exist for evidence-bound sources;
- provider is not marked required for replay, governance, or constitutional truth.

Replay reconstruction is read-only.

Replay may not select a source, repair missing evidence, or invoke a provider.

## 10. Constitutional Preservation

Source-of-truth routing preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Mapping:

| Role | Router meaning |
| --- | --- |
| LLM proposes | Provider is fallback source only, never source-selection authority |
| AiGOL governs | AiGOL selects and records the source of truth |
| Worker executes | Worker execution is not part of routing |
| Replay records | Replay records selected source and evidence references |

## Foundation Result

The source-of-truth router boundary is ready as a design artifact.

It remains ready with gaps because no router runtime, dispatch integration, CLI integration, source response normalization, or router tests are implemented by this review.

```text
SOURCE_OF_TRUTH_ROUTER_FOUNDATION_STATUS = READY_WITH_GAPS
```
