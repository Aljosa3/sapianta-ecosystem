# Resolution Strategy Selection Rules V1

Status: selection rules.

## Selection Principle

AiGOL should select the narrowest sufficient replay-safe source category.

Provider assistance is a fallback for semantic assistance, not the default source of truth.

Worker evidence is future execution evidence, not a conversational shortcut.

## Default Selection Order

```text
1. REPLAY
2. GOVERNANCE
3. CONSTITUTIONAL_MEMORY
4. SELF_RESOLUTION
5. PROVIDER
6. WORKER
7. COMBINED
```

## `REPLAY`

Select `REPLAY` when the prompt asks about:

- what happened;
- why an operation failed;
- prior operation evidence;
- replay reconstruction;
- evidence continuity;
- recorded provider or worker events.

Provider assistance must not be required for replay truth.

## `GOVERNANCE`

Select `GOVERNANCE` when the prompt asks about:

- constitutional invariants;
- authority boundaries;
- certification status;
- ADR decisions;
- fail-closed rules;
- governance constraints.

Provider assistance must not be required to determine governance truth.

## `CONSTITUTIONAL_MEMORY`

Select `CONSTITUTIONAL_MEMORY` when the prompt requires:

- citation-backed constitutional memory;
- known governance artifact citations;
- memory consultation evidence;
- bounded explanation from cited artifacts.

Provider assistance must not replace missing citations.

## `SELF_RESOLUTION`

Select `SELF_RESOLUTION` when AiGOL can answer deterministically from:

- existing runtime knowledge;
- known capability descriptions;
- known non-authority explanations;
- local bounded response templates;
- simple operator-facing summaries.

Provider assistance is not required when self-resolution is sufficient.

## `PROVIDER`

Select `PROVIDER` only when:

- deterministic resolution is insufficient;
- semantic interpretation is needed;
- unsupported language or phrasing needs interpretation;
- open-ended response synthesis is needed;
- provider-assisted classification is needed after deterministic failure.

Provider output must be validated and may be rejected.

## `WORKER`

Select `WORKER` only as an evidence need, not as direct execution.

`WORKER` requires deferral to Proposal Lifecycle when future worker execution would be needed.

Worker evidence may be used only after authorized execution has occurred and replay records the result.

## `COMBINED`

Select `COMBINED` when more than one source category is necessary.

The record must state:

- included strategies;
- source precedence;
- conflict handling;
- provider role if any;
- whether proposal lifecycle is required.

`COMBINED` must fail closed if source precedence or authority boundaries are ambiguous.

## Provider Assistance Rules

Provider assistance may be used for:

- semantic classification;
- language normalization;
- bounded response drafting;
- proposal evidence generation;
- explanation phrasing after AiGOL has selected allowed evidence.

Provider assistance must never be required for:

- replay truth;
- governance truth;
- constitutional authority;
- approval decisions;
- authorization decisions;
- worker execution permission;
- fail-closed termination;
- secret handling.

## Fail-Closed Conditions

Strategy selection must fail closed if:

- no source category is sufficient;
- evidence references are missing;
- source categories conflict and precedence is undefined;
- provider authority is implied;
- worker execution is implied without proposal lifecycle;
- governance truth depends on provider output;
- replay evidence cannot be reconstructed;
- selected strategy is unsupported;
- prompt asks for hidden autonomy or governance bypass.

## Replay Requirements

Selection must record:

- prompt reference;
- candidate strategies;
- selected strategy;
- selection reason;
- source precedence;
- evidence references;
- provider required or not;
- worker required or not;
- proposal lifecycle required or not;
- fail-closed reason when applicable.
