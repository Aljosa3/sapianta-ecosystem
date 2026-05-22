# REAL_TRANSPORT_GAP_AUDIT_V1

Status: audit-only runtime truth stabilization.

Scope: browser companion, sidepanel runtime, service worker, Native Messaging host, Python minimal bridge, local governed transport, semantic contract synthesis, governance gateway, Codex invocation path, observability cards, lifecycle/replay handling, artifact generation, governed return, and structural verification.

This audit does not modify runtime behavior, add autonomy, add orchestration, add agents, add dispatch, add semantic authority, or change governance guarantees.

## Executive Finding

The full aspirational topology is not currently real end to end:

```text
Human
-> ChatGPT semantic cognition
-> AiGOL governance mediation
-> Canonical task package
-> Codex execution
-> Structural verification
-> Governed return
-> ChatGPT interpretation
```

The truthful current canonical path is:

```text
Human
-> local deterministic normalization
-> AiGOL governance mediation
-> canonical task package
-> bounded Codex CLI provider
-> structural verification
-> governed operator return
```

Live ChatGPT cognition is not operationally present in the audited browser companion/native path. Live ChatGPT interpretation is not operationally present on return. Codex execution is real only on the canonical Native Messaging/Python minimal bridge path, where the bounded provider wrapper invokes `codex exec <bounded_prompt>`. JS-only sidepanel/demo paths remain non-canonical and must be treated as mock or visibility-only.

## REAL vs MOCK Matrix

| Runtime stage | Classification | Reality |
| --- | --- | --- |
| Human request sidepanel input | REAL | Operator enters text and explicitly clicks `Run via Native Bridge`. |
| MV3 service worker mediation | REAL | Validates message shape and calls `chrome.runtime.sendNativeMessage`. |
| Native Messaging host | REAL | One-shot local stdio host validates request and invokes Python minimal bridge. |
| Local deterministic semantic normalization | ADVISORY_ONLY | Deterministic local proposal, not live ChatGPT cognition. |
| Semantic contract synthesis | STRUCTURAL_ONLY | Deterministic local contract with hash and forbidden-authority validation. |
| AiGOL local governed transport | REAL | Enforces envelope/session/hash/authority/replay/lifecycle policy. |
| Canonical governed task package | STRUCTURAL_ONLY | Provider input contract; not semantic correctness proof or approval. |
| Codex CLI provider | REAL | Bounded `codex exec` subprocess when canonical Python path runs and `codex` is available. |
| Post-execution verification | STRUCTURAL_ONLY | Schema, lineage, status, session/proposal, and forbidden authority checks only. |
| Governed return layer | ADVISORY_ONLY | Operator-facing summary, not live ChatGPT interpretation. |
| Observatory cards | UI_ONLY | Rendering/narration only; no enforcement. |
| JS-only demo/mock bridge | MOCK | Legacy/experimental sidepanel path; does not invoke Native Messaging host or Codex. |
| Durable replay backend for minimal native path | MOCK | Replay events are visible and deterministic but not durably persisted. |

## Architecture Analysis

### Browser Companion

`browser_companion/manifest.json` declares MV3, `nativeMessaging`, `sidePanel`, `service_worker.js`, and a sidepanel entrypoint. This is real browser-extension wiring, but host registration remains environmental.

`browser_companion/sidepanel.html` defines the canonical core flow with `Run via Native Bridge`. It also contains legacy/experimental controls explicitly marked non-canonical. The presence of both means operators can see both real and mock/demo pathways in one UI.

`browser_companion/sidepanel.js` maintains `lifecycleEntries` and `replaySessionEntries` in memory. It does not use `localStorage`, `sessionStorage`, `indexedDB`, or `chrome.storage`. Its observatory cards are deterministic rendering helpers, not authority. It correctly states that semantic reasoning is local deterministic normalization and that governed return is not live ChatGPT interpretation.

### Service Worker Runtime

`browser_companion/service_worker.js` is real mediation. It validates the sidepanel request, requires `operator_triggered: true`, calls `chrome.runtime.sendNativeMessage`, handles timeouts/errors, and validates accepted native responses contain a `result_artifact`.

The service worker does not provide governance authority by itself. It is a browser transport gate and error-normalization boundary. Its authority guarantee labels are descriptive unless backed by the native host/Python result.

### Native Messaging Host

`agol_bridge/native/native_messaging_host.py` is a real local one-shot Native Messaging host. It reads one Chrome-native length-prefixed message, validates action, request text, session, operator trigger, and `SEMANTIC_TRANSPORT_ONLY`, then calls `run_minimal_end_to_end_bridge`.

It does not start a server, listener, daemon, retry loop, orchestration loop, or background continuation.

### Python Minimal Bridge

`agol_bridge/runtime/minimal_end_to_end_bridge.py` is the current canonical Python runtime path. It composes:

- local deterministic semantic proposal preparation;
- deterministic semantic contract synthesis;
- local governed transport validation;
- task package construction and validation;
- bounded Codex CLI provider invocation;
- structural result validation;
- governed operator return;
- deterministic in-memory replay event generation.

It is not live ChatGPT. It is not semantic correctness verification. Its replay records explicitly mark `durable_persistence: false`.

### Runtime Transport Layer

`agol_bridge/transport/local_governed_transport.py` is real governance mediation for local semantic transport. It validates envelope shape, session attachment, unsafe modes, proposal hash, authority claims, replay policy, and lifecycle policy. It returns a transport event with `SESSION_LOCAL_APPEND_CANDIDATE_ONLY`, not a durable append.

The older `sapianta_bridge/transport/` stack exists as bounded transport infrastructure, but it is not the canonical browser companion Native Messaging path audited here. It should not be used to imply live ChatGPT cockpit continuity.

### Semantic Contract Synthesis

`agol_bridge/semantic_contract/semantic_contract_synthesis.py` is structural only. It deterministically derives a contract from request text and proposal fields, sets `chatgpt_api_invoked: false`, and validates hash/provenance/authority boundaries.

This is useful canonical structure, but it is not ChatGPT cognition and not semantic truth.

### Codex Invocation Path

`agol_bridge/providers/codex_cli_provider.py` is a real bounded provider boundary. It validates task package, workspace path, allowed roots, timeout bounds, and then invokes:

```text
codex exec <bounded_prompt>
```

via `subprocess.run`.

Codex execution is therefore real on the canonical Python/native path if the environment has the `codex` executable available and the native host is installed. It is not real on JS-only demo/mock paths.

Provider execution is bounded but not semantically certified. A completed Codex process means the provider process returned zero. It does not prove the requested change is correct, complete, safe, or compliant.

## Authority Map

| Authority | Current holder | Enforced facts |
| --- | --- | --- |
| Operator authority | Human operator | Explicit sidepanel click/input initiates path. |
| Browser transport authority | MV3 service worker | Native Messaging invocation and response/error normalization. |
| Local host boundary authority | Native Messaging host | Message shape, operator trigger, authority boundary, one-shot local process. |
| Governance authority | AiGOL local governed transport and validators | Envelope, session, hash, authority claims, replay/lifecycle policy, result lineage. |
| Execution authority | Bounded Codex CLI provider only | `codex exec` subprocess within allowed workspace and timeout. |
| Semantic authority | None | Semantic layer is local deterministic/advisory and non-authoritative. |
| UI authority | None | Observatory cards render only. |
| ChatGPT authority | None in current operational path | No live ChatGPT call or live ChatGPT result interpretation exists. |

## Transport Continuity Map

| Boundary | Continuity status |
| --- | --- |
| Human input -> sidepanel message | REAL when operator clicks canonical native bridge button. |
| Sidepanel -> service worker | REAL via `chrome.runtime.sendMessage`. |
| Service worker -> native host | REAL if Chrome Native Messaging host is installed and permitted. |
| Native host -> Python minimal bridge | REAL local function invocation. |
| Python bridge -> semantic proposal | ADVISORY_ONLY deterministic local normalization. |
| Semantic proposal -> semantic contract | STRUCTURAL_ONLY deterministic contract synthesis. |
| Semantic contract -> local governed transport | REAL governance validation. |
| Transport accepted -> task package | STRUCTURAL_ONLY canonical provider input. |
| Task package -> Codex CLI | REAL bounded subprocess provider invocation. |
| Codex result -> result validation | STRUCTURAL_ONLY schema/lineage/non-authority checks. |
| Result validation -> governed return | ADVISORY_ONLY operator summary. |
| Governed return -> live ChatGPT | Not present. Continuity breaks here. |
| Replay events -> durable backend | Not present. Events remain returned artifact/in-memory visibility. |

## Persistence Analysis

Durable:

- File-based replay logging exists in `agol_bridge/replay_logger.py` for older task dispatcher surfaces, where `append_replay_event` writes JSONL.

Not durable in the current canonical Native Messaging/Python minimal bridge path:

- semantic proposal;
- semantic contract;
- transport report;
- task package;
- Codex result;
- result validation;
- governed return;
- minimal bridge replay events;
- sidepanel lifecycle/replay session arrays;
- observatory card state.

Reconstructable:

- A returned canonical result artifact can be hash-verified and rendered.
- Deterministic replay event IDs can be recomputed from returned payloads.

Not reconstructable after reload unless separately retained:

- sidepanel in-memory lifecycle history;
- service worker transient invocation state;
- native host process state;
- Codex subprocess environment/output if the returned artifact is not preserved.

Replay lineage is visible, deterministic, and artifact-carried. It is not a durable replay backend in the minimal native path.

## Semantic Continuity Analysis

Semantic continuity breaks at both ends of the aspirational ChatGPT topology:

- inbound: there is no live ChatGPT semantic cognition in the browser companion/native runtime path;
- outbound: the governed return is not sent to live ChatGPT for interpretation.

The actual semantic path is:

```text
human_request text
-> deterministic local semantic_proposal
-> deterministic local semantic_contract
-> structured task package
```

This preserves structural continuity, not cognitive continuity. It can carry intent-like fields, but it cannot claim live model understanding, semantic correctness, or semantic verification.

## Provider Invocation Analysis

Codex is actually invoked by `agol_bridge/providers/codex_cli_provider.py` through `subprocess.run(["codex", "exec", bounded_prompt], ...)` after:

- task package validation;
- workspace existence check;
- allowed root check;
- timeout validation;
- no auto-approval;
- no retry;
- no orchestration.

Provider invocation is canonical in the Native Messaging/Python minimal bridge path. It is indirect from the sidepanel: sidepanel -> service worker -> native host -> Python bridge -> provider wrapper -> `codex exec`.

Provider invocation is not present in:

- imported semantic proposal flow;
- local sidepanel-only transport visualization;
- JS-only demo/mock bridge;
- observatory rendering itself.

## Replay Analysis

The current minimal bridge creates deterministic replay events for:

- `SEMANTIC_PROPOSAL_NORMALIZED`;
- `SEMANTIC_CONTRACT_SYNTHESIZED`;
- `LOCAL_GOVERNED_TRANSPORT_VALIDATED`;
- `GOVERNED_TASK_PACKAGE_CREATED`;
- `BOUNDED_CODEX_CLI_RESULT_CAPTURED`;
- `GOVERNED_RESULT_VALIDATED`.

These events are replay-visible and included in the result artifact. They explicitly carry `mutation: false` and `durable_persistence: false`. Therefore, they are evidence objects, not durable replay storage.

Sidepanel replay/lifecycle cards are UI-only and ephemeral.

## Observability Risks

The observatory is valuable because it exposes reality. It remains risky where wording could inflate capability:

- `REAL_CODEX_EXECUTION` must be shown only when canonical native/Python artifact or provider result proves it.
- `CANONICAL_NATIVE_PYTHON_RUNTIME_PATH` must not be inferred from JS demo entries.
- hash verification must remain labeled as integrity only.
- structural verification must not imply semantic correctness.
- governed return must not be called live ChatGPT interpretation.
- replay visibility must not imply durable replay persistence.

## Canonical Artifacts

Canonical for current native/Python path:

- Native bridge request message with `RUN_MINIMAL_END_TO_END_BRIDGE`;
- semantic proposal produced by deterministic normalization;
- semantic contract produced by `synthesize_semantic_contract`;
- local governed transport report;
- governed task package;
- Codex CLI result package;
- structural result validation;
- governed operator return;
- `MINIMAL_END_TO_END_BRIDGE_RESULT` artifact with hash.

Non-canonical for real transport truth:

- JS-only mock Codex result;
- legacy experimental sidepanel mock execution;
- observatory card summaries alone;
- imported semantic proposal without canonical Python runtime artifact;
- sidepanel replay arrays.

## Single Source of Truth

For the current operational state, the single source of truth is:

```text
Native Messaging accepted response
-> canonical Python MINIMAL_END_TO_END_BRIDGE_RESULT artifact
-> hash-verified sidepanel rendering
```

If that artifact is absent, the sidepanel must be treated as visibility, demo, import, mock, or not-started state depending on the rendered path marker.

