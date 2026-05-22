# SIDEPANEL_CORE_FLOW_REORGANIZATION_V1

Status: implemented as sidepanel structure and usability cleanup only.

## New UI Hierarchy

The sidepanel is now organized into three visible hierarchy levels:

1. Core Flow
2. Advanced Debug
3. Legacy / Experimental

The Core Flow is visible by default and contains the daily operational path.

Advanced Debug and Legacy / Experimental are collapsed by default.

## Canonical Operator Flow

The default operator workflow is:

1. Enter Human Request.
2. Confirm session binding.
3. Run via Native Bridge.
4. Read Governed Return.
5. Inspect the Governed Execution Observatory.

The canonical topology is:

Human Request -> Semantic Contract -> AiGOL Governance Gateway -> Canonical Task Package -> Codex Execution -> Structural Verification -> Governed Return

This is the primary runtime view and the intended daily development cockpit.

## Advanced Debug Philosophy

Advanced Debug preserves inspection surfaces without allowing them to dominate the operator workflow.

It contains:

- semantic proposal file import;
- canonical result artifact import;
- local transport attach;
- chat-first governed flow;
- replay/lifecycle/audit evidence through the existing audit evidence section;
- raw JSON inspection.

Advanced Debug is for diagnosis and artifact review. It does not replace the canonical Native Bridge path.

## Legacy Isolation Strategy

Legacy / Experimental contains historical and non-canonical controls:

- preview/confirm/export/ingest controls;
- mock governed execution;
- legacy governed Codex execution control;
- invoke governed runtime;
- read-only continuity demo;
- imported semantic proposal textarea;
- JS demo bridge.

These surfaces are preserved for compatibility and migration review, but they are collapsed by default and labeled non-canonical.

## Observability Preservation Model

The reorganization preserves:

- Governance Chat Return;
- Governed Execution Observatory;
- semantic contract visibility;
- AiGOL governance gateway visibility;
- canonical task package visibility;
- Codex execution visibility;
- post-execution structural verification visibility;
- replay and lifecycle evidence;
- raw artifact inspection.

No runtime behavior, provider behavior, transport behavior, or governance enforcement was changed.

## Usability Goals

The reorganized sidepanel should make the daily task obvious:

- type a request;
- run the canonical bridge;
- read the governed return;
- inspect the execution topology;
- open debug only when needed.

This reduces:

- operator overload;
- duplicated governance narration;
- authority confusion;
- visible mock/demo clutter;
- competing execution buttons.

## Authority Clarity Principles

The UI continues to preserve:

- semantic cognition is not governance mediation;
- governance mediation is not execution;
- execution is bounded provider invocation;
- verification is structural unless explicitly upgraded;
- descriptive labels do not create authority.

The observatory classifications remain:

- `ENFORCED`
- `STRUCTURAL_ONLY`
- `ADVISORY_ONLY`
- `UI_ONLY`

## Explicit Non-Goals

This milestone does not add:

- new runtime capability;
- orchestration;
- autonomy;
- semantic AI review;
- new transport protocol;
- background execution;
- hidden continuation.
