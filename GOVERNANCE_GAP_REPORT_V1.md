# GOVERNANCE_GAP_REPORT_V1

Status: audit only.

Scope: Browser Companion sidepanel, MV3 service worker, Native Messaging host, AGOL Bridge Python runtime, bounded Codex CLI provider, and adjacent semantic proposal import paths.

Question audited:

Human -> ChatGPT semantic cognition -> AiGOL governance mediation -> Codex bounded execution -> AiGOL governance verification -> ChatGPT interpretation

Current conclusion:

The current runtime implements a real local governed execution path from Browser Companion to Python to Codex CLI, with pre-execution transport validation and post-execution structural validation. It does not currently implement real ChatGPT semantic cognition in the Browser Companion runtime path. The "ChatGPT" layer is represented by deterministic local normalization, explicit imported proposal artifacts, and UI/governance labels. Therefore the full architecture exists only partially as runtime enforcement; the ChatGPT semantic cognition and semantic interpretation stages remain advisory/imported/descriptive rather than live runtime cognition.

## REAL TOPOLOGY MAP

### Native bridge real execution path

1. Operator enters text in `#chat-first-human-request`.
2. `browser_companion/sidepanel.js:nativeBridgeMessageFromSidepanel()` reads that text and creates a native message:
   - `action: RUN_MINIMAL_END_TO_END_BRIDGE`
   - `human_request`
   - `session_id`
   - `operator_triggered: true`
   - `authority_boundary: SEMANTIC_TRANSPORT_ONLY`
3. `browser_companion/sidepanel.js:runNativeBridgeFromSidepanel()` sends the message to the MV3 service worker using `chrome.runtime.sendMessage`.
4. `browser_companion/service_worker.js` validates the wrapper message and invokes `chrome.runtime.sendNativeMessage`.
5. `agol_bridge/native/native_messaging_host.py:handle_native_message()` validates the native payload and invokes `run_minimal_end_to_end_bridge`.
6. `agol_bridge/runtime/minimal_end_to_end_bridge.py:run_minimal_end_to_end_bridge()`:
   - performs deterministic chat-first normalization;
   - validates local governed transport;
   - creates a governed task package;
   - invokes the bounded Codex CLI provider;
   - validates the result package;
   - creates a governed chat return and canonical result artifact.
7. `agol_bridge/providers/codex_cli_provider.py:run_bounded_codex_cli_task()` invokes `codex exec <bounded_prompt>` with captured stdout, stderr, return code, timeout handling, and no silent retry.
8. The native host returns a canonical result artifact to the service worker.
9. The sidepanel verifies and renders the result artifact.

### Non-native semantic proposal import path

1. Operator pastes or selects `semantic_proposal.json`.
2. `browser_companion/sidepanel.js` parses and validates the proposal locally.
3. Hash verification is performed for file import.
4. Accepted proposal is rendered through local continuity/demo cockpit surfaces.
5. This path does not invoke ChatGPT, Codex, the native host, or the canonical Python bridge runtime.

## EXISTING ENFORCEMENT

### Real runtime enforcement

- The sidepanel no longer invokes Native Messaging directly in the real native path. It calls the MV3 service worker via `chrome.runtime.sendMessage`; the service worker is the component that calls `chrome.runtime.sendNativeMessage`.
- The service worker enforces:
  - message object shape;
  - `operator_triggered === true`;
  - native response shape;
  - structured runtime errors for native host failures, malformed results, missing permission/API, and timeout.
- The native host enforces:
  - action must be `RUN_MINIMAL_END_TO_END_BRIDGE`;
  - non-empty `human_request`;
  - non-empty `session_id`;
  - `operator_triggered` must be true;
  - `authority_boundary` must be `SEMANTIC_TRANSPORT_ONLY`.
- The Python bridge runtime enforces:
  - fail-closed rejection for unsafe mode tokens in the raw request text;
  - deterministic semantic proposal normalization;
  - explicit session registry creation;
  - local governed transport validation;
  - task package schema validation;
  - result package schema validation;
  - lineage checks for task id, session id, and proposal id;
  - no execution authority, orchestration, autonomous continuation, or silent retry flags in the captured result wrapper.
- The local governed transport handler enforces:
  - required transport envelope fields;
  - required semantic proposal fields;
  - explicit known session;
  - allowed proposal modes only;
  - SHA-256 artifact hash verification;
  - authority claim rejection;
  - replay policy and lifecycle policy constraints.
- The Codex CLI provider enforces:
  - non-empty governed task package;
  - required `task_id` and `codex_prompt`;
  - no task metadata auto-approval;
  - explicit workspace path;
  - workspace must exist and be within allowed root;
  - timeout bounds;
  - no silent retry;
  - deterministic result package shape.

### Schema-only governance

- Task package validation checks package shape, but does not prove the package fully captures the user's semantic intent.
- Result package validation checks structure, lineage, bounded statuses, and forbidden authority flags. It does not prove the Codex output satisfies the original request.
- Canonical result artifact hashing verifies integrity of the returned artifact, not semantic correctness.

## PARTIAL ENFORCEMENT

### ChatGPT semantic preparation

Current Browser Companion native execution path does not call ChatGPT or an OpenAI API. It uses deterministic local normalization:

- `normalize_human_request_to_semantic_proposal(...)` in `agol_bridge/chat_first/chat_first_normalization.py`;
- JavaScript mirror `normalizeHumanRequestToSemanticProposal(...)` in `browser_companion/sidepanel.js`.

This creates a semantic proposal shaped object, but it is not produced by live ChatGPT semantic cognition. It is a deterministic local transformation of the operator's text.

### Governed canonical package creation

The runtime does create a governed task package before Codex CLI invocation. However, the current `codex_prompt` is generic:

`Run bounded governed Codex review for proposal <proposal_id>.`

The task package includes proposal/session/transport metadata, but it does not clearly embed the full human request or a rich semantic intent as Codex-facing instructions. This means Codex receives a governed package, but the package may be semantically under-specified for actual implementation work.

### AiGOL pre-execution mediation

Pre-execution mediation is real for schema, session, hash, authority text, replay/lifecycle policy, unsafe mode, task package shape, workspace boundary, and provider invocation contract.

It is partial for semantic admissibility. AiGOL does not deeply interpret whether the requested implementation is admissible beyond simple unsafe token/mode/authority checks.

### AiGOL post-execution verification

Post-execution verification is real for:

- result schema;
- task lineage;
- session linkage;
- proposal linkage;
- bounded status;
- forbidden authority flags;
- silent retry flag.

It is partial for semantic verification. AiGOL does not yet verify that Codex's actual changes satisfy the governed task, obey all constraints, or preserve repository governance beyond provider result structure.

### Execution authority boundary

Execution is now real through Codex CLI. The runtime labels this as bounded and operator-triggered. However, `approval_required` is currently `False` in the task package. The operator click is treated as the practical trigger. There is no separate explicit execution approval token distinct from native bridge invocation.

## DECLARED ONLY

### ChatGPT semantic cognition

Browser Companion labels say "ChatGPT = advisory cognition only", but the current real native runtime path does not invoke ChatGPT. ChatGPT is represented by:

- external human context;
- pasted/imported semantic proposal artifacts;
- deterministic local chat-first normalization;
- UI labels and governance summaries.

This is advisory-only/descriptive in the current runtime, not live semantic cognition.

### ChatGPT interpretation

The runtime creates a `governed_chat_return` summary intended to be ChatGPT-facing. It does not send the result back to ChatGPT or invoke ChatGPT to interpret it. Interpretation remains an operator-mediated or external step.

### Governance labels in sidepanel

The following are primarily UI-only governance visibility unless backed by the Python/native path result:

- executive governance labels such as `SAFE_REVIEW_ONLY`, `SESSION_REPLAY_ONLY`, and `CONTINUITY_VISIBLE`;
- constitutional layer text;
- compact authority statement text;
- semantic clarification labels;
- operator event stream narration;
- local bridge descriptive status;
- continuity and replay summaries rendered from sidepanel-local objects.

These labels help operator comprehension but do not themselves enforce runtime behavior.

### Legacy mock/demo sidepanel path

`browser_companion/sidepanel.js` still contains JS-side bridge task and mock result functions with `governance_mode: governed_execution_bridge_mock_only` and `execution_provider: MOCK_CODEX_ONLY`. These are not the canonical real native bridge path, but their presence is a clarity risk because UI code still contains older mock lifecycle machinery alongside the real Codex CLI path.

## MISSING COMPONENTS

1. Live ChatGPT semantic cognition invocation in the Browser Companion runtime path.
2. A canonical ChatGPT-generated semantic ingress artifact produced by actual ChatGPT runtime rather than local deterministic normalization or manual import.
3. A semantic admissibility validator that evaluates ambiguity, requested action type, authority leakage, and implementation risk beyond string/mode checks.
4. A task package that carries full governed semantic intent into the Codex prompt, including the original request and bounded expected output.
5. Separate explicit execution approval distinct from the operator's native bridge invocation.
6. Strong post-execution semantic verification against task intent, expected outputs, files changed, commands run, and governance constraints.
7. Enforced workspace allowlist independent of a task package value generated inside the same runtime call.
8. Durable replay ledger. Current replay visibility is session-local/in-memory/result-artifact visible, not a durable append-only backend.
9. A real ChatGPT return transport. Current governed return is generated for ChatGPT-facing use but is not delivered to ChatGPT by runtime.

## BYPASS RISKS

1. Native host workspace default:
   - `native_messaging_host.py` defaults missing `workspace_path` to `Path.cwd()`.
   - This can silently broaden execution scope if the host is launched from an unintended directory.
   - Minimal hardening: require explicit workspace path or a configured allowlist and fail closed when absent.

2. Provider prompt under-specification:
   - Codex receives a bounded task package, but the package currently has a generic `codex_prompt`.
   - The raw human request is not clearly embedded as the canonical task intent in the task package.
   - This risks execution that is governed in shape but weak in semantic direction.

3. UI mirror/demo paths:
   - Sidepanel contains JS-only mock/demo lifecycle functions.
   - If operators use these buttons instead of the native bridge, they may see governance narration without canonical Python/Codex execution.
   - Minimal hardening: visually mark demo-only paths and make the native bridge the only real execution surface.

4. Existing localhost popup path:
   - `browser_companion/popup.js` still references localhost preview bridge endpoints.
   - This is not the current native execution path but remains a separate Browser Companion runtime surface.
   - Minimal hardening: document or gate it as preview-only so it cannot be confused with canonical execution.

5. No independent post-execution repository validation:
   - The provider may run Codex CLI in the workspace.
   - The bridge validates returned result structure, not repository state, tests, or conformance.

6. Hash over-trust:
   - Artifact hash verification protects integrity, not truth, approval, correctness, or safety.
   - UI already labels this, but enforcement should continue to treat hash as integrity-only.

## AUTHORITY LEAK RISKS

1. "Semantic transport only" language coexists with real Codex CLI execution.
   - The transport boundary is semantic-only, but the full native bridge now invokes a real bounded provider after governance checks.
   - Operators may misread "no dispatch" while observing real execution.
   - Minimal hardening: distinguish "transport authority" from "bounded provider invocation after AiGOL gate".

2. `approval_required: False` in task package.
   - Real execution occurs after operator-triggered native bridge invocation.
   - There is no second approval checkpoint.
   - Minimal hardening: add explicit "execute bounded Codex task" confirmation or approval token before provider invocation.

3. AiGOL as governance gateway is real but shallow semantically.
   - Current checks can block malformed/unsafe structure and obvious authority claims.
   - They do not determine whether the proposed semantic direction is safe, necessary, or compliant with repository governance.

4. ChatGPT naming implies live cognition.
   - The current runtime uses "ChatGPT" in labels and artifact names, but does not invoke ChatGPT.
   - Minimal hardening: relabel deterministic local normalization as "local chat-first normalization" and reserve "ChatGPT semantic cognition" for actual ChatGPT-produced artifacts.

5. Workspace authority is runtime-generated.
   - The task package's allowed workspace root is set from the runtime argument or current working directory.
   - Minimal hardening: move workspace allowlist to explicit operator/native host configuration rather than task package self-declaration.

## ENFORCED VS DESCRIPTIVE GOVERNANCE

### Real runtime enforcement

- MV3 service worker mediates Native Messaging calls.
- Native host validates bridge message shape.
- Python runtime normalizes request deterministically and validates transport.
- Local transport handler enforces schema, session, hash, authority, unsafe modes, replay policy, and lifecycle policy.
- Task package is created and schema validated.
- Codex CLI provider requires governed task package and workspace boundary.
- Result wrapper is validated for lineage and forbidden authority flags.

### Schema-only governance

- Task package schema validation.
- Result package schema validation.
- Canonical artifact schema/hash validation.

### Advisory-only governance

- Deterministic "chat-first" semantic proposal generation.
- Imported ChatGPT semantic proposal artifacts.
- Governed chat return summary.
- Recommended next step.

### UI-only governance

- Executive governance layer labels.
- Compact authority statements.
- Constitutional role labels.
- Semantic clarification labels.
- Operator event stream narration.
- Replay/lifecycle summaries when not backed by canonical Python result artifact.
- Legacy mock/demo lifecycle rendering.

## CRITICAL INVESTIGATION ANSWERS

### A. Where does "Implement deterministic replay compaction for replay event visibility." go?

In the real native path:

1. The text is read from `#chat-first-human-request` by `nativeBridgeMessageFromSidepanel()`.
2. The sidepanel sends it as raw `human_request` inside a native bridge message to the service worker.
3. The service worker forwards it through Native Messaging.
4. The Python native host passes it to `run_minimal_end_to_end_bridge`.
5. The Python runtime transforms it into a deterministic local semantic proposal using `prepare_chat_first_transport_envelope`.
6. The local transport handler validates the envelope.
7. The runtime creates a governed task package.
8. Codex CLI receives a bounded prompt containing the task package JSON.

The text is not sent to ChatGPT by this runtime path.

### B. Is ChatGPT invoked anywhere?

No live ChatGPT/OpenAI invocation was found in the current Browser Companion native execution path.

There are OpenAI adapter modules elsewhere in `sapianta_system/runtime/llm`, but they are not part of the Browser Companion -> service worker -> native host -> AGOL Bridge -> Codex CLI path audited here.

There are ChatGPT-style bridge modules and preview endpoints elsewhere, but the current Browser Companion native bridge path uses deterministic local normalization, not a ChatGPT API call.

### C. What is the "ChatGPT Semantic Proposal" field?

It is an explicit local textarea/file import surface. It is not runtime-generated ChatGPT output. It can contain text that an operator copied from ChatGPT or loaded from `semantic_proposal.json`, but the sidepanel does not generate it by invoking ChatGPT.

### D. Exact real execution pipeline

Sidepanel payload:

```json
{
  "action": "RUN_MINIMAL_END_TO_END_BRIDGE",
  "request_id": "...",
  "human_request": "...",
  "session_id": "...",
  "operator_triggered": true,
  "authority_boundary": "SEMANTIC_TRANSPORT_ONLY",
  "labels": [
    "NATIVE_BRIDGE_LOCAL_ONLY",
    "OPERATOR_TRIGGERED",
    "CANONICAL_PYTHON_RUNTIME",
    "REAL_CODEX_EXECUTION",
    "BOUNDED_CODEX_CLI_PROVIDER",
    "NO_AUTONOMOUS_CONTINUATION"
  ]
}
```

Service worker transformation:

- validates wrapper;
- calls Native Messaging;
- wraps success/failure as structured service worker response.

Native host transformation:

- validates action/session/operator/authority;
- calls canonical Python bridge runtime;
- exports canonical result artifact.

Python runtime transformation:

- raw human request -> deterministic semantic proposal;
- semantic proposal -> local governed transport envelope;
- transport envelope -> transport report;
- transport report + proposal -> governed task package;
- task package -> Codex CLI bounded prompt;
- provider result -> Codex result wrapper;
- result wrapper -> result validation;
- result validation -> governed chat return and canonical result artifact.

### E. Does Codex receive raw operator text or governed canonical task package?

Codex receives a bounded prompt containing the governed task package JSON. It does not receive the raw operator text directly as the primary prompt. However, because the task package currently has a generic `codex_prompt` and proposal id reference, semantic intent may be under-specified.

### F. Where is governance narration only?

- Most sidepanel labels and summaries.
- The "ChatGPT Semantic Proposal" import heading when no real ChatGPT artifact provenance is attached.
- The constitutional layer display.
- Executive and compact authority summaries.
- Operator event stream narration.
- Demo/local JS mirror lifecycle.
- Continuity/replay visibility not backed by canonical Python result artifacts.

### G. Is AiGOL a real governance gateway?

Yes, for structural and transport enforcement in the native path. It gates session, hash, mode, authority statements, replay/lifecycle policies, task package validation, provider invocation shape, workspace boundary, and result lineage.

No, not yet for full semantic cognition or semantic correctness. AiGOL does not currently call ChatGPT, does not perform deep semantic admissibility review, and does not verify that Codex's actual work satisfies the original human request.

## CURRENT ARCHITECTURE STATUS

The current runtime partially supports:

Human -> local deterministic semantic normalization -> AiGOL mediation -> Codex CLI -> AiGOL structural verification -> governed return

The current runtime does not yet fully support:

Human -> ChatGPT semantic cognition -> AiGOL semantic mediation -> Codex bounded execution -> AiGOL semantic/governance verification -> ChatGPT interpretation

The latter architecture still exists mainly conceptually for the ChatGPT cognition and ChatGPT interpretation stages.

## NEXT MINIMAL GOVERNANCE PATCH

Recommended minimal patch path, in order:

1. Require explicit workspace path or configured workspace allowlist for native bridge execution.
   - Remove `Path.cwd()` fallback from the native host and runtime execution path.
   - Fail closed if workspace is missing or outside allowlist.

2. Carry full governed semantic intent into the task package.
   - Include `human_request`, `semantic_intent`, `requested_mode`, and authority boundary in the canonical task package.
   - Build the Codex prompt from that canonical task package.
   - Keep this as a targeted task package hardening, not a new architecture layer.

3. Add a distinct execution confirmation gate.
   - Separate "transport accepted" from "execute bounded Codex task".
   - Use an explicit operator confirmation token or boolean in the native message.

4. Add deterministic post-execution verification checks.
   - Verify provider output contains the completion marker.
   - Verify files changed / commands run / tests fields are present or explicitly empty.
   - Verify the result references the task id and proposal id.
   - Optionally run existing relevant repository tests only when explicitly authorized by the task package.

5. Relabel or constrain non-canonical sidepanel paths.
   - Keep mock/demo paths, but mark them unmistakably as demo-only.
   - Make the native bridge the only "real execution" surface.

6. Clarify ChatGPT boundary.
   - Current native path should be labeled "local deterministic normalization".
   - Reserve "ChatGPT semantic cognition" for imported/provenanced ChatGPT artifacts or a future explicit ChatGPT ingress contract.

These patches harden the existing path without introducing orchestration, autonomy, durable replay, new transport protocols, or large refactors.
