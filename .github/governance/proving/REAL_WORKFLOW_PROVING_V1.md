# REAL_WORKFLOW_PROVING_V1

## Status

Operational proving report.

## Purpose

This proving exercise assesses whether the current AiGOL Browser Companion
cockpit helps an operator understand, inspect, and trust a governed AI workflow.

This is operational proving, usability/governance validation, cockpit
comprehension testing, and replay/lifecycle/continuity usefulness assessment.
It is not new feature development, provider dispatch, execution runtime,
orchestration, durable backend work, or ChatGPT API integration.

## Proving Method

The proving method used the current sidepanel cockpit implementation and
supporting semantic proposal artifacts as the review surface:

- semantic proposal text import path;
- semantic proposal file import path;
- deterministic proposal validation;
- SHA-256 semantic proposal hash verification;
- continuity cockpit rendering;
- replay/lifecycle visibility panels;
- artifact inspection panels;
- authority and semantic boundary labels.

The proving is a structured operator review, not an automated browser session.
It evaluates expected operator comprehension from current UI labels,
validation behavior, fixture semantics, and test evidence.

## Scenario 1: ChatGPT Semantic Proposal For Governance Review

Input shape: a ChatGPT-authored proposal using `REVIEW_ONLY`, bounded risk,
explicit no-approval/no-dispatch/no-execution language, and semantic
non-authority language.

Observations:

- Operator clarity is good after the proposal is accepted because the cockpit
  shows semantic proposal validation, continuity status, authority boundaries,
  and semantic direction together.
- Authority boundary clarity is strong because accepted proposals are repeatedly
  labeled as not approval, not dispatch, not execution, and not continuation.
- Continuity report usefulness is medium-high: it gives an immediate governance
  posture but still reads like an internal report rather than an operator story.
- Replay/lifecycle visibility is useful for confirming read-only continuity, but
  the difference between in-memory replay visibility and durable replay remains
  easy to miss.
- Artifact inspection is useful for audit-minded operators but may overwhelm a
  first-time operator.
- UX friction is moderate because the operator must choose between text import,
  file import, demo trigger, replay load, and regular runtime controls.
- Duplicate concepts appear between continuity status, lifecycle view, replay
  sessions, replay timeline, and artifact inspection.

Assessment:

- governance clarity score: 8 / 10
- operational usefulness score: 7 / 10
- result: the system helps, but the operator needs a clearer recommended path.

## Scenario 2: ChatGPT Semantic Proposal With Unsafe Execution Wording

Input shape: a ChatGPT-authored proposal containing execution-like,
provider-like, orchestration-like, or autonomous continuation wording.

Observations:

- Operator clarity is good because rejected proposals produce blocked validation
  output and deterministic rejection errors.
- Authority boundary clarity is very strong because unsafe wording is rejected
  before continuity flow generation.
- Continuity report usefulness is medium: the blocked report explains rejection,
  but the operator may need a more compact "why this was blocked" summary.
- Replay/lifecycle visibility is less useful in this scenario because no
  governed continuity flow is admitted; the useful evidence is mostly validation
  and authority boundary evidence.
- Artifact inspection is useful if the operator wants to inspect the rejected
  payload, but it can feel like noise when the rejection reason is already
  enough.
- UX friction is low for rejection itself, but the language validator can be
  sensitive to denied claims and requires carefully phrased boundary text.
- Confusing labels: `CONTINUITY_BOUNDARY_VIOLATION` is precise but might sound
  more severe than a simple rejected semantic proposal.

Assessment:

- governance clarity score: 9 / 10
- operational usefulness score: 7 / 10
- result: the system clearly prevents unsafe semantic transport, but should add
  a concise rejection summary for operators.

## Scenario 3: Valid Semantic Proposal Imported From semantic_proposal.json With Hash Verification

Input shape: `.github/governance/fixtures/semantic_proposal_v1.json`, using
`REVIEW_ONLY`, explicit lineage and replay identity references, certification
metadata, and a valid SHA-256 `artifact_hash`.

Observations:

- Operator clarity is strong because file import makes the semantic proposal a
  tangible artifact rather than loose text.
- Authority boundary clarity is strong because hash verification is labeled as
  integrity only and not approval, dispatch, execution, or continuation.
- Continuity report usefulness is high because a valid artifact can be traced
  from proposal identity to continuity rendering.
- Replay/lifecycle visibility is useful because the proposal has explicit
  lineage and replay references, but current cockpit replay remains session-only
  and not a durable backend.
- Artifact inspection is highly useful in this scenario because the operator can
  inspect the exact validated artifact, hash status, and boundary statements.
- UX friction is moderate: file selection plus hash verification is clearer than
  paste import, but still requires the operator to understand fixture fields and
  canonical hash semantics.
- Missing evidence: there is no browser automation evidence showing actual file
  selection in Chrome; current assurance is static/test-based plus deterministic
  fixture validation.

Assessment:

- governance clarity score: 8 / 10
- operational usefulness score: 8 / 10
- result: this is the strongest current workflow for proving a non-copy/paste
  ChatGPT/AiGOL bridge, provided hash mismatch handling remains visible.

## Cross-Scenario Findings

The cockpit helps most when the operator needs to answer:

- Was this proposal accepted or rejected?
- Did it grant any authority?
- Was the imported artifact intact?
- What semantic direction was proposed?
- What continuity and replay/lifecycle evidence is visible?

The cockpit adds noise when the operator needs only:

- a plain-language reason for rejection;
- a single recommended next action;
- a compact distinction between proposal validation, hash verification,
  continuity validity, replay visibility, and lifecycle visibility.

## UX Issues

- The sidepanel now mixes operational runtime controls and read-only continuity
  proving controls in the same control grid.
- Multiple panels restate "not approval / not dispatch / not execution"; this
  is governance-safe but visually repetitive.
- `Replay Timeline`, `Replay Sessions`, and replay artifact inspection may feel
  duplicative without a simple "session-only, not durable replay" marker at the
  top.
- `Continuity Status`, `Envelope Validation Status`, `Validator Composition
  Status`, and `Semantic Proposal Validation Status` are all useful but need an
  operator-facing hierarchy.
- Hash verification is valuable, but the operator needs a short explanation
  that verified integrity does not certify truth, quality, approval, or safety.

## Risks

- Operators may confuse "certified for continuity ingestion" with approval if
  labels are compressed too aggressively.
- Operators may over-trust `HASH_VERIFIED` as semantic correctness rather than
  artifact integrity.
- Sidepanel complexity may slow real workflow adoption before the local bridge
  becomes useful.
- The current workflow lacks browser automation proving for actual file import.
- Current replay is session-local and must not be mistaken for durable replay.

## Scores

Overall governance clarity score: 8 / 10.

Overall operational usefulness score: 7 / 10.

Readiness for `CHATGPT_AIGOL_LOCAL_BRIDGE_V1`: conditionally ready for a bounded
local bridge planning milestone, but not ready for localhost ingress,
background import, provider dispatch, durable replay backend, or ChatGPT API
integration.

## Recommended Fixes Before CHATGPT_AIGOL_LOCAL_BRIDGE_V1

1. Add a compact "Recommended Operator Path" panel for semantic proposal import.
2. Add a short rejection summary above detailed artifacts.
3. Visually separate runtime execution controls from read-only proving controls.
4. Add an explicit top-level marker: "Replay is session-only; not durable."
5. Add browser automation or equivalent manual evidence for actual file import.
6. Keep localhost POST and extension background import deferred.

## Recommended Next Step

Prepare a narrow `CHATGPT_AIGOL_LOCAL_BRIDGE_V1` implementation review focused
only on explicit local file handoff and operator-selected import, using
`semantic_proposal_v1.json` and hash verification as the proving baseline.
