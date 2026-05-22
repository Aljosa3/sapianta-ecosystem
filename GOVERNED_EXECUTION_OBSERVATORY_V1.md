# GOVERNED_EXECUTION_OBSERVATORY_V1

Status: implemented as observability-only Browser Companion sidepanel layer.

## Observability Model

The Governed Execution Observatory renders the current operational bridge as visible layers:

1. Human Request
2. Semantic Reasoning Layer
3. AiGOL Governance Gateway
4. Canonical Governed Task Package
5. Codex Execution Layer
6. AiGOL Post-Execution Verification
7. Governed Return Layer

Each layer exposes:

- input;
- output;
- authority;
- boundary;
- status.

The observatory does not add execution authority, orchestration, autonomy, background continuation, or a new transport protocol.

## Authority Semantics

The observatory uses explicit authority classifications:

- `ENFORCED`: runtime gate or provider boundary.
- `STRUCTURAL_ONLY`: schema, lineage, hash, package, or forbidden-flag verification.
- `ADVISORY_ONLY`: semantic context or operator return without authority.
- `UI_ONLY`: descriptive sidepanel narration.

These classifications are rendering labels only. They do not alter runtime behavior.

## Enforcement Classifications

Real enforcement currently includes:

- MV3 service worker mediation;
- Native Messaging host validation;
- canonical Python runtime invocation;
- local governed transport validation;
- task package schema validation;
- bounded Codex CLI provider invocation;
- result lineage and authority-flag validation.

Structural-only enforcement currently includes:

- task package shape;
- result package shape;
- artifact hash integrity;
- replay visibility references;
- lifecycle visibility references.

Advisory-only layers currently include:

- local deterministic semantic normalization;
- governed operator return;
- recommended next step.

UI-only layers include:

- operator event narration;
- compact authority summaries;
- constitutional role labels;
- descriptive replay/lifecycle summaries not backed by canonical runtime artifacts.

## Runtime Topology Visualization Rules

The observatory must show whether the current rendered path is:

- `CANONICAL_NATIVE_PYTHON_RUNTIME_PATH`;
- `JS_ONLY_DEMO_OR_MOCK_PATH`;
- `LOCAL_SEMANTIC_PROPOSAL_IMPORT_PATH`;
- `SIDEPANEL_VISIBILITY_PATH`;
- `NO_RUNTIME_PATH_RENDERED`.

The Codex execution card must explicitly show either:

- `REAL_CODEX_EXECUTION`;
- `MOCK_EXECUTION`;
- `NOT_STARTED`.

The semantic reasoning layer must state:

`LOCAL DETERMINISTIC NORMALIZATION; NON-AUTHORITATIVE; SEMANTIC ONLY`

until a separately governed live ChatGPT ingress is implemented.

The governed return layer must state:

`GOVERNED OPERATOR RETURN; NOT LIVE CHATGPT INTERPRETATION`

because current runtime does not send results back to live ChatGPT.

## Real vs Descriptive Governance

Real governance means a runtime function or provider boundary validates, rejects, constrains, or captures a result.

Descriptive governance means the sidepanel explains authority or status to an operator without changing runtime behavior.

The observatory must preserve that distinction visibly. It must not imply that semantic correctness is verified when only structural verification occurred.

## Explicit Non-Goals

This milestone does not implement:

- live ChatGPT invocation;
- semantic correctness verification;
- provider orchestration;
- autonomous continuation;
- background execution;
- new transport protocols;
- durable replay backend;
- architectural refactor.

## Remaining Gap Visibility

The observatory intentionally keeps the known gap visible:

Current runtime partially supports:

Human -> local deterministic semantic normalization -> AiGOL mediation -> Codex CLI -> AiGOL structural verification -> governed operator return

It does not yet fully support:

Human -> live ChatGPT semantic cognition -> AiGOL semantic mediation -> Codex bounded execution -> AiGOL semantic verification -> live ChatGPT interpretation
