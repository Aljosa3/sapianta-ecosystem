# REPLAY_AND_LIFECYCLE_VISUALIZATION_SPEC_V1

## Status

Draft specification.

## Purpose

This specification defines bounded replay and lifecycle visualization semantics
for the Browser Companion sidepanel.

The visualization surface is observability-only. It may help operators inspect
replay, lifecycle, approval, lineage, constitutional layer, and semantic
direction state. It must not create orchestration, execution authority, semantic
autonomy, automatic dispatch, hidden persistence, or hidden networking.

## Scope

The Browser Companion sidepanel may visualize:

1. Replay Timeline Visualization
2. Lifecycle Graph Visualization
3. Approval State Visualization
4. Governance Boundary Visualization
5. Replay Lineage Navigation
6. Constitutional Layer Visibility
7. Semantic Direction Visibility
8. Bounded Session Continuity Semantics

The visualization scope is limited to rendering already-governed data returned
by localhost runtime responses, AGOL Bridge replay artifacts, lifecycle
artifacts, certification artifacts, and explicit operator-selected context.

## Non-Goals

This specification does not authorize:

- orchestration;
- execution authority;
- semantic autonomy;
- autonomous planning;
- automatic dispatch;
- hidden execution;
- hidden networking;
- hidden persistence;
- browser scraping;
- background workers;
- mutation of governance artifacts.

## 1. Replay Timeline Visualization

Replay timeline visualization presents ordered replay events with stable
identity, timestamp, event type, prior state, next state, actor, reason, and
package hash when available.

Rules:

- timeline entries must be read-only;
- timeline order must follow replay log order or explicit response order;
- missing timestamps must be displayed as unknown, not inferred;
- hidden or synthetic replay events must not be invented;
- append-only lineage visibility must be preserved.

## 2. Lifecycle Graph Visualization

Lifecycle graph visualization presents bounded state transitions across the
recognized lifecycle model:

- `CREATED`
- `NORMALIZED`
- `WAITING_FOR_APPROVAL`
- `APPROVED`
- `DISPATCHED`
- `EXECUTING`
- `RETURNED`
- `VALIDATED`
- `FINALIZED`
- `QUARANTINED`
- `FAILED`

Rules:

- unknown states must be visually marked as blocked or unknown;
- invalid transitions must be visibly marked as quarantine or fail-closed;
- visualization must not create new state transitions;
- graph rendering must not imply dispatch authority.

## 3. Approval State Visualization

Approval state visualization presents whether a task, transfer, handoff, or
execution request requires approval, has approval recorded, is waiting for
approval, or is blocked.

Rules:

- approval state must come from governed response or replay data;
- the sidepanel must not silently infer approval;
- approval visualization must preserve explicit approval boundaries;
- approval visibility must not trigger authorization or dispatch.

## 4. Governance Boundary Visualization

Governance boundary visualization presents explicit boundaries such as:

- localhost-only interaction;
- no hidden execution;
- no automatic dispatch;
- no hidden networking;
- no hidden persistence;
- read-only observability;
- bounded in-memory sidepanel continuity.

Rules:

- boundary indicators must be informational;
- boundary indicators must not relax validation;
- absent boundary evidence must be shown as unknown or blocked rather than
  assumed safe.

## 5. Replay Lineage Navigation

Replay lineage navigation allows operators to inspect relationships between
task packages, result packages, replay records, certification artifacts,
finalization artifacts, and ADR/spec references.

Rules:

- navigation must preserve historical filenames and alias references;
- migration aliases must be displayed as aliases, not replacements;
- navigation must not rewrite replay records;
- lineage traversal must remain read-only.

## 6. Constitutional Layer Visibility

Constitutional layer visibility presents the current layer separation:

- SAPIANTA = constitutional governance substrate;
- AGOL = governed operational layer family;
- AiGOL = semantic direction governance identity;
- ChatGPT / LLMs = semantic cognition;
- Codex / workers = execution through governed transport only.

Rules:

- layer visibility must not collapse cognition, governance, and execution;
- layer labels must not imply model execution authority;
- constitutional references must remain traceable to governance artifacts.

## 7. Semantic Direction Visibility

Semantic direction visibility presents model-proposed direction and governance
admissibility state.

Rules:

- LLM output may be shown as proposed semantic direction;
- AiGOL / AGOL admissibility must be shown separately from model cognition;
- proposed direction must not be rendered as execution approval;
- non-deterministic reasoning must not be presented as deterministic replay.

## 8. Bounded Session Continuity Semantics

The sidepanel may preserve visualization continuity in memory while the panel
remains open.

Rules:

- continuity is bounded to the active browser sidepanel session;
- continuity does not create hidden persistence;
- continuity does not scrape browser or conversation content;
- continuity does not survive as certified replay unless represented by
  governed runtime or bridge artifacts;
- the operator-visible log may append entries during the active session.

## Governance Guarantees

The visualization model preserves:

- no hidden execution;
- no automatic dispatch;
- localhost-only interaction;
- replay-safe observability;
- append-only lineage visibility;
- explicit approval boundaries;
- read-only inspection;
- fail-closed rendering for unknown or invalid states;
- separation of semantic cognition, semantic direction governance, and
  execution.

## Observability Guarantees

Visualization may improve readability of long lifecycle responses, replay
records, approval state, boundary state, and lineage references.

Observability must remain read-only. It may display governed runtime data and
AGOL Bridge artifacts, but it must not mutate lifecycle state, dispatch tasks,
authorize execution, or create new governance authority.

## Risks

- Operators may mistake visualization for authorization if approval labels are
  ambiguous.
- Timeline views may imply deterministic semantic replay where only transport
  replay exists.
- Alias navigation may obscure historical references if aliases are displayed as
  replacements.
- Bounded in-memory continuity may be mistaken for durable replay if not labeled.

## Boundedness Guarantees

- Visualization is UI-only and observability-only.
- Data must come from governed localhost responses, replay artifacts, lifecycle
  artifacts, certification artifacts, or explicit operator-selected context.
- Unknown data must remain unknown.
- Invalid data must remain blocked or quarantined.
- No visualization control may bypass approval, dispatch, validation, replay, or
  lifecycle boundaries.
