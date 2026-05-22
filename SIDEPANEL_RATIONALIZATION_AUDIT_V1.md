# SIDEPANEL_RATIONALIZATION_AUDIT_V1

Status: analysis and reorganization plan only.

Scope: Browser Companion sidepanel structure, controls, observability cards, execution paths, lifecycle surfaces, governance narration, and debug evidence surfaces.

No runtime behavior was changed by this audit.

## CURRENT SIDEPANEL TOPOLOGY

The current sidepanel has accumulated multiple generations of runtime and governance UI:

1. General input and legacy mode controls:
   - `mode`
   - `artifact`
   - `governed-demo-request`
   - `chatgpt-semantic-proposal`
   - `semantic-proposal-file`
   - `bridge-result-artifact-file`
   - `local-transport-session-id`
   - `chat-first-human-request`
   - `chat-first-requested-mode`

2. Large flat control grid:
   - Preview intent
   - Confirm preview
   - Export governed intent transfer package
   - Ingest governed transfer package
   - Export governed handoff package
   - Request execution authorization
   - Run mock governed execution
   - Run governed Codex execution
   - Inspect governed execution
   - Invoke governed runtime
   - Run Governed Demo
   - Import Semantic Proposal
   - Import semantic_proposal.json
   - Import Canonical Bridge Result
   - Attach Governed Transport
   - Run Chat-first Governed Flow
   - Run End-to-End Bridge
   - Run via Native Bridge

3. Pre-observatory cockpit summaries:
   - Executive Governance Layer
   - Semantic Clarification
   - Compact Authority Statement
   - Executive Operational Layer
   - Operational Narrative
   - Local Bridge
   - Local Governed Transport Runtime
   - Chat-first Result Card
   - Latest Action Result
   - Operator Event Stream
   - Governance Chat Return

4. Current operational center:
   - Governed Execution Observatory
   - Human Request
   - Semantic Reasoning Layer
   - Semantic Contract
   - AiGOL Governance Gateway
   - Canonical Governed Task Package
   - Codex Execution Layer
   - AiGOL Post-Execution Verification
   - Governed Return Layer

5. Collapsed audit evidence:
   - Bridge Lifecycle Evidence
   - Governance
   - Replay
   - Lifecycle
   - Semantic
   - Authority
   - Inspection

The current UI is functionally rich but cognitively crowded. It still exposes legacy/demo pathways and transitional labels alongside the canonical native runtime path.

## REAL RUNTIME CRITICAL COMPONENTS

These components are critical to the current canonical operational flow:

- `chat-first-human-request`
  - Primary human request input.

- `local-transport-session-id`
  - Required session binding visibility and runtime parameter.

- `run-native-bridge`
  - Primary canonical execution trigger.
  - Routes through MV3 service worker, Native Messaging host, canonical Python runtime, bounded Codex CLI provider, and canonical result artifact return.

- Governance Chat Return
  - Primary operator-facing outcome.
  - Should remain visible near the top.

- Governed Execution Observatory
  - Current best representation of the real topology:
    Human Request -> Semantic Contract -> Governance Mediation -> Canonical Task Package -> Codex Execution -> Verification -> Governed Return.

- Canonical Bridge Result Artifact import
  - Useful for offline/manual canonical result inspection.
  - Not daily core if Native Messaging works, but important as fallback/debug.

- `browser_companion/service_worker.js` path visibility
  - Not a sidepanel control, but the sidepanel should continue to expose the fact that Native Messaging runs through the service worker.

## REDUNDANT / LEGACY COMPONENTS

These components are redundant, legacy, or now superseded by the observatory:

- Executive Governance Layer
  - Mostly duplicates Observatory classification and authority summaries.
  - Recommendation: fold into Observatory header or move to compact status strip.

- Semantic Clarification
  - Useful text, but duplicates Observatory authority/boundary labels.
  - Recommendation: keep as tooltip/help text or advanced reference, not a full card.

- Compact Authority Statement
  - Useful, but repeats labels now present in Observatory and Governance Chat Return.
  - Recommendation: merge into Observatory topology header.

- Executive Operational Layer
  - Duplicates Observatory status and Governance Chat Return.
  - Recommendation: remove from default view or compress to one-line status.

- Operational Narrative
  - Descriptive governance narration.
  - Recommendation: move to advanced/debug unless it becomes generated from canonical runtime result only.

- Local Bridge
  - Describes the earlier file handoff model.
  - Now superseded by Native Bridge path.
  - Recommendation: legacy/experimental.

- Local Governed Transport Runtime
  - Useful for transport debugging.
  - Superseded in daily use by Observatory AiGOL Governance Gateway.
  - Recommendation: advanced debug.

- Chat-first Result Card
  - Superseded by Governance Chat Return and Observatory Human/Semantic Contract layers.
  - Recommendation: legacy/experimental or remove after migration.

- Latest Action Result
  - Duplicates Governance Chat Return.
  - Recommendation: merge into Governance Chat Return or Observatory status.

- Operator Event Stream
  - Potentially useful, but currently narration-heavy and not canonical replay.
  - Recommendation: advanced debug or compact event trace below Observatory.

- Minimal End-to-End Bridge Lifecycle
  - Superseded by Observatory.
  - Recommendation: advanced debug only.

- Governance subsection inside audit evidence
  - Duplicates Observatory and continuity findings.
  - Recommendation: advanced debug.

- Replay/Lifecycle/Semantic/Authority subsections
  - Useful audit surfaces but too dense for core workflow.
  - Recommendation: advanced debug.

- Eight raw inspection panels
  - Required for auditability, but not daily operator flow.
  - Recommendation: advanced debug.

## DUPLICATED OBSERVABILITY

The sidepanel currently has multiple surfaces describing the same concepts:

- Human request:
  - `chat-first-human-request`
  - Continuity Human Request
  - Observatory Human Request
  - Minimal End-to-End Bridge Lifecycle

- Authority:
  - Compact Authority Statement
  - Governance Chat Return
  - Observatory classification cards
  - Authority section
  - Governance Boundary View
  - Raw authority artifact

- Replay:
  - Executive Governance Layer
  - Replay Timeline
  - Replay Sessions
  - Replay Entry Inspection
  - Replay Summary Artifact
  - Observatory topology/status references

- Semantic layer:
  - ChatGPT Semantic Proposal textarea
  - Semantic Proposal Artifact
  - Semantic Direction View
  - Semantic Reasoning Layer
  - Semantic Contract card

- Execution status:
  - Latest Action Result
  - Governance Chat Return
  - Minimal End-to-End Bridge Lifecycle
  - Codex Execution Layer
  - Canonical Bridge Result Artifact

The Observatory should become the canonical topology surface. Older duplicate cards should move behind debug or legacy gates.

## AUTHORITY CONFUSION RISKS

1. Too many execution-adjacent buttons.
   - `Run mock governed execution`, `Run governed Codex execution`, `Invoke governed runtime`, `Run End-to-End Bridge`, and `Run via Native Bridge` appear together.
   - This obscures which path is canonical.

2. Mixed real and mock paths.
   - Sidepanel still has JS-only mock/demo bridge functions and a real native Codex CLI path.
   - Both are visible as buttons.
   - This risks operators confusing demo narration with real execution.

3. Legacy "Request execution authorization" button.
   - It implies a separate approval model but is not the canonical current native execution flow.
   - This is especially confusing because current task packages set `approval_required: false`.

4. "ChatGPT Semantic Proposal" naming.
   - The sidepanel does not invoke live ChatGPT.
   - This should be renamed or placed in legacy/import mode unless actual ChatGPT provenance exists.

5. Repeated "semantic transport only" labels next to real Codex execution.
   - The phrase is true for transport authority, but may confuse operators when real bounded Codex execution occurs downstream.
   - Observatory wording helps, but core layout should separate transport authority from bounded provider invocation.

6. Replay terminology overload.
   - Replay entries, replay sessions, replay timeline, replay summary artifact, and replay visibility appear in several places.
   - These should be debug/audit by default.

## CANONICAL VS NON-CANONICAL EXECUTION PATHS

### Canonical path

`Run via Native Bridge`

Current canonical topology:

Human Request -> MV3 service worker -> Native Messaging host -> canonical Python runtime -> semantic contract -> AiGOL mediation -> governed task package -> bounded Codex CLI -> structural verification -> governed return.

This should be the only core execution path shown by default.

### Canonical fallback/debug path

`Import Canonical Bridge Result`

This renders canonical Python result artifacts. It is useful for inspection and troubleshooting, but not the primary daily flow if Native Messaging is available.

### Advanced/debug paths

- Attach Governed Transport
- Run Chat-first Governed Flow
- Import semantic_proposal.json
- Import Semantic Proposal
- Load Replay
- Inspect governed execution

These are useful for debugging sublayers, but should not be core daily controls.

### Legacy/experimental paths

- Run Governed Demo
- Run End-to-End Bridge
- Run mock governed execution
- Preview intent
- Confirm preview
- Export governed intent transfer package
- Ingest governed transfer package
- Export governed handoff package
- Request execution authorization
- Run governed Codex execution
- Invoke governed runtime

These reflect earlier milestones, preview runtime surfaces, or transitional models. They should be isolated from the core operator surface.

## DAILY OPERATOR FLOW ANALYSIS

The daily operator flow should be:

1. Enter Human Request.
2. Confirm/edit session if needed.
3. Click Run via Native Bridge.
4. Read Governance Chat Return.
5. Inspect Observatory cards:
   - Semantic Contract
   - AiGOL Governance Gateway
   - Canonical Task Package
   - Codex Execution
   - Post-Execution Verification
6. Open Advanced Debug only when something fails or needs audit detail.

Current friction:

- Too many input fields before the operator reaches the real request field.
- Too many buttons compete with the canonical native bridge.
- Multiple cards repeat similar authority/replay statements.
- Raw evidence is available, but the hierarchy still feels like an accumulated dashboard rather than an operational cockpit.

## CORE FLOW RECOMMENDATION

Default view should contain only:

1. Human Request input
   - `chat-first-human-request`
   - optional compact session field
   - `Run via Native Bridge`

2. Governed Return
   - primary result
   - status, reason, next step, authority disclaimer

3. Governed Execution Observatory
   - Human Request
   - Semantic Contract
   - AiGOL Governance Gateway
   - Canonical Governed Task Package
   - Codex Execution
   - AiGOL Post-Execution Verification
   - Governed Return

4. Single compact status strip
   - canonical path marker
   - real/mock marker
   - structural-only verification marker
   - no live ChatGPT marker

Default UI should not show:

- legacy mode selector;
- generic artifact input;
- governed demo request;
- ChatGPT semantic proposal textarea;
- semantic proposal file input;
- canonical result artifact input;
- full button grid;
- replay internals;
- raw JSON.

## ADVANCED DEBUG RECOMMENDATION

Move behind one collapsed `Advanced Debug` section:

- Canonical bridge result artifact file import.
- Semantic proposal file import.
- Local governed transport attach.
- Chat-first governed flow.
- Replay timeline.
- Replay sessions and load replay.
- Lifecycle view.
- Lineage summary.
- Governance boundary details.
- Semantic proposal validation/hash panels.
- Raw artifact JSON inspection.
- Provider metadata.
- Transport report.
- Full lifecycle event history.

Advanced Debug should be visibly non-core:

- "Debug only"
- "Does not replace canonical native bridge"
- "No execution authority granted by inspection"

## LEGACY / EXPERIMENTAL RECOMMENDATION

Move behind a separate collapsed `Legacy / Experimental` section or remove after migration:

- Preview intent.
- Confirm preview.
- Export governed intent transfer package.
- Ingest governed transfer package.
- Export governed handoff package.
- Request execution authorization.
- Run mock governed execution.
- Run governed Codex execution.
- Inspect governed execution.
- Invoke governed runtime.
- Run Governed Demo.
- Import Semantic Proposal textarea.
- Run End-to-End Bridge JS mirror.
- Mode selector.
- Generic artifact input.
- Governed demo request textarea.

Recommended labeling:

- `LEGACY_PREVIEW_RUNTIME`
- `JS_ONLY_DEMO`
- `MOCK_EXECUTION_ONLY`
- `NON_CANONICAL_PATH`
- `HISTORICAL_MILESTONE_SURFACE`

## PROPOSED SIMPLIFIED SIDEPANEL HIERARCHY

### CORE FLOW

1. Header:
   - SAPIANTA / AiGOL Governed Execution Observatory
   - Status strip:
     - `CANONICAL_NATIVE_PYTHON_RUNTIME_PATH`
     - `SEMANTIC_CONTRACT_SYNTHESIS_V1`
     - `REAL_CODEX_EXECUTION`
     - `STRUCTURAL_VERIFICATION_ONLY`

2. Request:
   - Human Request textarea
   - Session ID compact field
   - Run via Native Bridge button

3. Governed Return:
   - Primary operator answer
   - next recommended step
   - non-authority reminder

4. Observatory:
   - Human Request
   - Semantic Contract
   - Governance Mediation
   - Canonical Task Package
   - Codex Execution
   - Verification
   - Governed Return

### ADVANCED DEBUG

Collapsed by default:

- Canonical result artifact import.
- Semantic proposal artifact import.
- Transport details.
- Replay timeline.
- Lifecycle details.
- Lineage details.
- Provider result metadata.
- Raw JSON inspection.
- Hashes and artifact ids.
- Diagnostic event stream.

### LEGACY / EXPERIMENTAL

Collapsed by default, or hidden behind a developer flag:

- preview/confirm/export/ingest legacy controls;
- mock governed execution;
- JS-only end-to-end bridge;
- local demo runtime;
- legacy ChatGPT semantic proposal textarea;
- historical governance narration cards.

## PROPOSED CORE FLOW LAYOUT

```text
SAPIANTA / AiGOL Governed Execution Observatory

[Status strip]
CANONICAL_NATIVE_PYTHON_RUNTIME_PATH | REAL_CODEX_EXECUTION | STRUCTURAL_VERIFICATION_ONLY | NO_LIVE_CHATGPT

[Human Request]
textarea
session id
[Run via Native Bridge]

[Governed Return]
compact result, reason, next step, authority disclaimer

[Execution Observatory]
1 Human Request
2 Semantic Contract
3 AiGOL Governance Gateway
4 Canonical Governed Task Package
5 Codex Execution
6 AiGOL Post-Execution Verification
7 Governed Return

[Advanced Debug collapsed]
[Legacy / Experimental collapsed]
```

## PROPOSED ADVANCED DEBUG LAYOUT

```text
Advanced Debug

Transport
- local transport report
- native bridge response
- service worker status

Artifacts
- canonical result artifact import
- semantic proposal file import
- semantic contract JSON
- task package JSON
- raw result JSON

Replay / Lifecycle
- replay timeline
- replay sessions
- lifecycle view
- lineage summary

Provider
- Codex CLI provider result
- command summary
- stdout/stderr summary
- timeout status

Inspection
- raw envelope validation
- continuity report
- authority boundary artifact
- semantic boundary artifact
```

## PROPOSED LEGACY / EXPERIMENTAL ISOLATION STRATEGY

1. Group all legacy controls into one collapsed section.
2. Add a warning label:
   - "Legacy / experimental surfaces are not the canonical runtime path."
3. Mark each legacy control with one of:
   - `PREVIEW_ONLY`
   - `MOCK_ONLY`
   - `JS_ONLY`
   - `HISTORICAL`
   - `NON_CANONICAL`
4. Preserve tests for legacy behavior during migration.
5. After one stabilization milestone, remove or archive paths that no longer serve debugging.

## MINIMAL CLEANUP PATCH PLAN

1. Add a new top-level `Core Flow` wrapper.
   - Move Human Request, Session ID, Run via Native Bridge, Governance Chat Return, and Governed Execution Observatory into it.

2. Collapse all non-core inputs and controls.
   - Move generic mode/artifact/demo/proposal/file-import fields into Advanced Debug or Legacy / Experimental.

3. Replace the flat 18-button grid with three grouped areas:
   - Core: Run via Native Bridge.
   - Advanced Debug: import/render/transport/replay controls.
   - Legacy / Experimental: historical milestone controls.

4. Remove duplicate default cards.
   - Fold Executive Governance, Semantic Clarification, Compact Authority, Executive Operational, Operational Narrative, Local Bridge, Local Transport Runtime, Chat-first Result Card, Latest Action Result, and Operator Event Stream into Observatory or Advanced Debug.

5. Preserve all raw evidence.
   - Keep current audit evidence, but place it under Advanced Debug.

6. Rename misleading surfaces.
   - "ChatGPT Semantic Proposal" -> "Imported Semantic Proposal Artifact".
   - "Run End-to-End Bridge" -> "Run JS Demo Bridge".
   - "Run Governed Demo" -> "Run Read-Only Continuity Demo".

7. Make canonical path visually dominant.
   - The default page should answer: "What do I type, what ran, what did governance do, what did Codex do, what was verified?"

8. Do not change runtime semantics in cleanup patch.
   - DOM hierarchy and labels only.
   - No transport changes.
   - No provider changes.
   - No new execution paths.

## RATIONALIZATION DECISION

Decision: rationalization needed before adding further runtime capability.

Reason:

The core runtime path is now coherent enough to be the operator center, but the sidepanel still exposes too many milestone-era controls and duplicate explanations. This increases authority confusion and slows daily development.

Recommended next milestone:

`SIDEPANEL_CORE_FLOW_REORGANIZATION_V1`

Scope:

- sidepanel-only;
- DOM hierarchy and label changes;
- no runtime behavior changes;
- preserve observability and raw evidence;
- make `Run via Native Bridge` plus Governed Execution Observatory the default operational cockpit.
