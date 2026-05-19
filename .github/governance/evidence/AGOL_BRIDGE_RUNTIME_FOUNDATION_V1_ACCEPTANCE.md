# AGOL_BRIDGE_RUNTIME_FOUNDATION_V1_ACCEPTANCE

## Acceptance Status

Accepted for finalization.

## Accepted Capabilities

- filesystem task package transport
- deterministic task package schema validation
- deterministic result package schema validation
- bounded lifecycle transitions
- approval-gated dispatch
- immutable dispatched package writes
- quarantine behavior
- append-only replay logging
- SHA-256 package hashes
- result package return
- browser sidepanel observability support
- localhost-only interaction preservation
- explicit confirmation preservation

## Governance Acceptance

AGOL Bridge Runtime Foundation v1 preserves the AGOL Bridge Pivot and Semantic
Direction Governance boundaries:

- ChatGPT / LLMs = semantic cognition
- AiGOL / AGOL Bridge = semantic direction governance, replay, lifecycle, and transport
- Codex / workers = execution

The runtime does not create hidden execution authority. It does not implement
semantic autonomy, hidden orchestration, network transport, APIs, hidden
persistence, or unrestricted execution.

## Acceptance Evidence

- Invalid task schemas quarantine.
- Missing approval blocks dispatch and returns `WAITING_FOR_APPROVAL`.
- Approved tasks dispatch through filesystem handoff only.
- Dispatched task packages are immutable.
- Unexpected lifecycle transitions quarantine.
- Unknown lifecycle states block fail-closed.
- Replay records are JSONL and append-only.
- Browser sidepanel observability remains persistent, bounded, and read-only.

## Validation Commands

`python -B -m pytest agol_bridge/tests`

`python -m pytest tests/test_browser_companion_sidepanel.py tests/test_governed_browser_companion_runtime.py tests/test_governed_chatgpt_interpretation_bridge_v2.py tests/test_governed_intent_transfer_ingestion.py`

`git diff --check`
