# REPLAY_AND_LIFECYCLE_VISUALIZATION_IMPLEMENTATION_PLAN_V1

## Status

Plan only.

## Purpose

This plan defines a bounded implementation path for read-only replay and
lifecycle visualization inside the Browser Companion sidepanel.

This plan does not implement code, modify runtime behavior, add execution
authority, add persistence, add automatic dispatch, add orchestration, or add
semantic autonomy.

## References

- `.github/governance/specs/REPLAY_AND_LIFECYCLE_VISUALIZATION_SPEC_V1.md`
- `.github/governance/review/AGOL_CONSTITUTIONAL_LINEAGE_NORMALIZATION_V1.md`
- `.github/governance/review/AGOL_CONSTITUTIONAL_FOUNDATION_REVIEW_V1.md`
- `.github/governance/finalize/FINALIZE_GOVERNED_BROWSER_SIDEPANEL_RUNTIME_V1.md`
- `.github/governance/finalize/FINALIZE_AGOL_BRIDGE_RUNTIME_FOUNDATION_V1.md`

## Implementation Scope

The implementation scope is limited to sidepanel-only UI changes that render
already-governed data. The visualization may read operator-visible sidepanel
session state and, if needed, localhost-only governed responses or explicit
operator-selected artifacts.

The plan excludes backend authority changes, new runtime endpoints, new
execution paths, automatic dispatch, approval actions, hidden persistence, and
semantic interpretation engines.

## 1. UI Sections

### Replay Timeline

Display replay events in append order with event id, task id, event type,
previous state, next state, actor, reason, timestamp, and package hash when
available.

Labels must state: `Transport replay timeline`.

### Lifecycle Graph

Display bounded lifecycle state progression:

`CREATED -> NORMALIZED -> WAITING_FOR_APPROVAL -> APPROVED -> DISPATCHED -> EXECUTING -> RETURNED -> VALIDATED -> FINALIZED`

Display `QUARANTINED` and `FAILED` as terminal exception states.

Labels must state: `Lifecycle state view`.

### Approval State

Display approval requirement, approval recorded status, waiting state, blocked
state, or unknown state.

Labels must state: `Approval visibility only - not an approval control`.

### Governance Boundary

Display boundary indicators for localhost-only interaction, no hidden execution,
no automatic dispatch, no hidden persistence, no hidden networking, and read-only
observability.

Labels must state: `Boundary evidence view`.

### Constitutional Layer View

Display the current layer separation:

- `SAPIANTA` = constitutional governance substrate
- `AGOL` = governed operational layer
- `AiGOL` = semantic direction governance
- `ChatGPT / LLMs` = semantic cognition
- `Codex / workers` = execution through governed transport only

Labels must state: `Constitutional layer reference`.

### Semantic Direction View

Display model-proposed direction separately from governance admissibility state.

Labels must state: `Semantic direction proposal - not execution authority`.

## 2. Data Sources

Permitted data sources:

- replay artifacts;
- lifecycle artifacts;
- finalize artifacts;
- evidence artifacts;
- browser sidepanel session state;
- governed localhost runtime responses when already available to the sidepanel;
- explicit operator-selected JSON artifacts.

Data source constraints:

- no browser scraping;
- no hidden background reads;
- no hidden persistence;
- no non-localhost network access;
- no mutation of source artifacts;
- unknown data remains unknown.

## 3. Read-Only Rules

Visualization must preserve:

- no mutation;
- no dispatch;
- no approval action;
- no validation trigger;
- no runtime write;
- no hidden persistence;
- no hidden execution;
- no lifecycle transition creation.

The visualization layer may format data already visible to the sidepanel. It may
not cause execution, authorization, ingestion, dispatch, validation, or replay
record creation.

## 4. Labeling Rules

Labels must prevent confusion between:

- transport replay and semantic replay;
- lifecycle state and approval state;
- approval visibility and approval authority;
- execution receipt and execution authority;
- sidepanel in-memory continuity and durable replay;
- historical aliases and canonical replacements.

Required labels:

- `Transport replay - deterministic package movement evidence`
- `Semantic reasoning - model-native and non-deterministic`
- `Lifecycle state - governed transport state`
- `Approval state - visibility only`
- `Execution authority - not granted by visualization`
- `In-memory sidepanel continuity - non-durable`
- `Alias - historical reference preserved`

## 5. Implementation Boundaries

Implementation must be sidepanel-only UI work.

Allowed:

- render new sidepanel sections;
- render already-returned governed runtime response data;
- render explicitly selected local JSON artifacts;
- render localhost-only governed read responses if such reads already exist;
- preserve active-session in-memory UI state.

Not allowed:

- new backend authority;
- new execution paths;
- new automatic dispatch;
- new approval actions;
- new runtime write operations;
- hidden persistence;
- hidden networking;
- browser scraping;
- orchestration;
- semantic autonomy.

## 6. Risk Controls

Risk: visualization may imply authorization.

Control: every approval and authority panel must state that visualization is
read-only and does not approve, authorize, or dispatch.

Risk: timeline may imply deterministic semantic replay.

Control: timeline must distinguish transport replay from semantic reasoning.
Semantic reasoning remains model-native and non-deterministic.

Risk: aliases may overwrite historical names.

Control: aliases must be rendered as alias relationships. Historical names must
remain visible.

Risk: in-memory continuity may be mistaken for durable replay.

Control: sidepanel session continuity must be labeled non-durable unless backed
by governed replay artifacts.

## Recommended Implementation Sequence

1. Add static sidepanel section containers with read-only labels.
2. Add formatting helpers for replay, lifecycle, approval, boundary, layer, and
   semantic direction views.
3. Render existing sidepanel session entries into the new sections without
   changing event handlers.
4. Add optional explicit local JSON artifact selection for operator-provided
   replay or lifecycle artifacts, if separately approved.
5. Add tests that assert no new fetch, dispatch, approval, storage, background,
   or execution paths are introduced.
6. Validate labels distinguish transport replay from semantic reasoning and
   approval visibility from approval authority.

## Completion Criteria

Implementation may be considered complete only when:

- visualization is read-only;
- no new execution authority exists;
- no hidden persistence exists;
- no automatic dispatch exists;
- no lifecycle mutation occurs from visualization;
- sidepanel continuity remains bounded and labeled;
- tests confirm existing governance controls are preserved.
