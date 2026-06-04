# AIGOL_OCS_INPUT_MODEL_V1

## Status

Contract model.

## Input Principle

OCS may read only explicit, governed, replay-visible, or source-visible context.

No hidden memory, secret state, or live runtime state may become OCS authority.

## Conversation Memory Inputs

Allowed:

- operator prompt text;
- session id and turn id;
- conversation routing artifacts;
- clarification artifacts;
- operator-visible summaries;
- replay-visible conversation recommendations.

Forbidden:

- hidden memory not recorded as governed evidence;
- inferred approval from casual text;
- stale session state without replay reference;
- provider-private prompt traces.

## Replay-Derived Context Inputs

Allowed:

- chain inspection summaries;
- replay reconstruction artifacts;
- post-execution replay review artifacts;
- replay-derived improvement intent artifacts;
- governed termination artifacts;
- fail-closed evidence.

Forbidden:

- mutation of source replay;
- deterministic inspection artifacts as required input when inspection is
  operationally read-only;
- treating failed or terminated operations as resumable without new governed
  intake.

## Domain Context Inputs

Allowed:

- domain registry entries;
- domain bundle registry resolution artifacts;
- domain foundation artifacts;
- domain-specific boundary and certification artifacts;
- known domain gaps.

Forbidden:

- implicit domain creation;
- domain selection by provider text alone;
- domain-specific weakening of core governance;
- registry bypass by hardcoded filename.

## Approval Context Inputs

Allowed:

- `HUMAN_APPROVAL_REQUIRED` artifacts;
- approval resume artifacts;
- rejection artifacts;
- modification request artifacts;
- approval lineage records.

Forbidden:

- automatic approval;
- approval inference;
- modification of approval lineage;
- resurrection of rejected or terminated operations.

## Provider Context Inputs

Allowed:

- provider necessity policy classifications;
- governed provider proposal artifacts;
- provider validation and repair evidence;
- provider role metadata when selected through governed Resource Selection.

Forbidden:

- provider credentials;
- raw provider channels not captured as governed artifacts;
- provider authority to select context;
- provider authority to authorize implementation or execution.

## Worker Context Inputs

Allowed:

- worker registry references;
- worker assignment artifacts;
- invocation request artifacts;
- worker result capture artifacts;
- worker result validation artifacts;
- worker failure evidence.

Forbidden:

- direct worker invocation;
- live worker memory as canonical context;
- worker output not captured and validated through governed artifacts;
- role switching between provider and worker authority.

## Governance Context Inputs

Allowed:

- constitutional guidance artifacts;
- enforcement hierarchy artifacts;
- governance lineage artifacts;
- conformance status artifacts;
- known limitation artifacts.

Forbidden:

- silent reinterpretation of constitutional semantics;
- hidden governance mutation;
- replacing partial conformance visibility with full conformance claims.
