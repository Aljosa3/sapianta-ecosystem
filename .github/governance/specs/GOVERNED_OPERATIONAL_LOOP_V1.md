# GOVERNED_OPERATIONAL_LOOP_V1

## Status

Draft specification.

## Purpose

This specification defines the first bounded governed operational loop
connecting human request, ChatGPT semantic cognition, governed task packaging,
AGOL governance, execution provider dispatch, governed result normalization,
replay and lifecycle updates, ChatGPT semantic interpretation, and next-step
synthesis.

This specification is architectural and governance-only. It does not implement
autonomous execution, orchestration mesh, semantic autonomy, hidden execution,
automatic approvals, or unrestricted worker coordination.

## Core Principle

Semantic cognition may propose.

AiGOL / AGOL may govern admissibility, lifecycle, replay, and approval.

Execution providers may execute only through governed transport and explicit
authority boundaries.

## 1. Operational Loop Stages

The governed operational loop contains these stages:

1. Human request
2. Semantic reasoning
3. Governed task synthesis
4. Admissibility and governance checks
5. Execution dispatch
6. Governed result package
7. Replay and lifecycle update
8. Semantic interpretation
9. Next-step proposal

### Human Request

The human initiates a request, reviews proposed task direction, approves bounded
execution when required, and retains final authority over continuation.

### Semantic Reasoning

ChatGPT / LLMs generate candidate meaning, task framing, alternatives, and
semantic direction. This stage does not create execution authority.

### Governed Task Synthesis

The candidate task is normalized into a governed task package with replay-safe
identity, constraints, expected outputs, approval requirements, and lineage
references.

### Admissibility and Governance Checks

AiGOL / AGOL validates schema, lifecycle state, replay continuity, approval
requirements, mutation boundaries, and execution admissibility.

### Execution Dispatch

Dispatch may occur only through governed transport after required approval and
admissibility checks. Dispatch does not imply unrestricted orchestration.

### Governed Result Package

The execution provider returns a result package with status, tests, changed
files, artifacts, summary, failure state, and human review requirement.

### Replay and Lifecycle Update

Replay and lifecycle artifacts are updated through append-only records and
bounded state transitions.

### Semantic Interpretation

ChatGPT / LLMs may interpret the governed result package and propose meaning,
explanation, or next direction. Interpretation remains non-authoritative.

### Next-Step Proposal

The next step is proposed to the human and may become a new governed task only
through packaging, governance checks, and approval boundaries.

## 2. Constitutional Layer Responsibilities

### ChatGPT / LLM Role

ChatGPT / LLMs provide semantic cognition. They may propose task direction,
interpret results, explain implications, and synthesize next-step proposals.

They do not approve, dispatch, execute, mutate governance state, or grant
execution authority.

### AiGOL / AGOL Role

AiGOL / AGOL governs admissible semantic evolution, task packaging, replay,
lifecycle, approval gates, mutation boundaries, quarantine, and transport.

It does not own full semantic cognition and does not execute provider work.

### Execution Provider Role

Execution providers, beginning with Codex, execute bounded tasks only after
governed dispatch. Providers return result packages and must remain isolated
from governance authority.

### Observability Role

Observability surfaces display replay, lifecycle, approval, boundary, result,
and semantic direction state. Observability remains read-only and must not
trigger execution.

## 3. Task Package Semantics

Governed task packages must be deterministic JSON packages with:

- replay-safe task identifiers;
- governance mode;
- risk class;
- approval requirement;
- execution prompt or provider instruction;
- constraints;
- expected outputs;
- lineage references;
- mutation boundaries;
- metadata.

Task packages are proposals until admitted by governance. Task package mutation
after dispatch is prohibited.

## 4. Result Package Semantics

Governed result packages must normalize provider output into deterministic JSON
with:

- status;
- tests and outcomes;
- changed files;
- artifacts;
- summary;
- replay references;
- lifecycle references;
- failure state;
- human review requirement.

Result interpretation is separate from result authority. ChatGPT may interpret a
result package, but that interpretation does not mutate replay, approve
continuation, or dispatch follow-up work.

Failure semantics are fail-closed. Partial or malformed results remain visible
and require review or quarantine according to governance rules.

## 5. Replay and Lifecycle Integration

The operational loop must preserve:

- append-only replay updates;
- lifecycle transition visibility;
- replay-safe operational continuity;
- bounded session continuity;
- deterministic package hashes;
- lineage references across task and result packages.

Sidepanel continuity is active-session and in-memory unless backed by governed
replay artifacts.

Replay records must not be silently rewritten.

## 6. Execution Provider Abstraction

Codex is the first execution provider.

Future providers may be added only as isolated execution providers behind
governed transport, schema validation, approval gates, lifecycle boundaries, and
replay evidence.

Provider boundaries:

- providers do not govern themselves;
- providers do not approve tasks;
- providers do not mutate replay history;
- providers do not bypass lifecycle transitions;
- provider output returns as governed result packages.

## 7. Operational Safety Boundaries

The operational loop explicitly prohibits:

- hidden dispatch;
- hidden execution;
- automatic approval;
- unrestricted orchestration;
- semantic autonomy escalation;
- silent mutation;
- replay rewriting;
- hidden persistence;
- hidden networking;
- lifecycle bypass;
- approval bypass.

## Governance Guarantees

- constitutional separation of concerns is preserved;
- replay-safe governance is preserved;
- approval boundaries remain explicit;
- authority separation is explicit;
- append-only lineage semantics are required;
- execution semantics remain bounded;
- semantic cognition remains model-native;
- governance remains system-native.

## Completion Boundary

This specification defines the governed operational loop contract. It does not
authorize implementation until a separate bounded implementation milestone
defines file scope, tests, and authority-preserving acceptance criteria.
