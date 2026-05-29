# First Useful AiGOL Usage Guide V1

Status: first useful AiGOL operator guide.

This guide explains how a new operator can use the first useful AiGOL without reading the architecture documents.

## What AiGOL Is

AiGOL is a governed read-only operator runtime.

It lets a human submit one bounded request, runs that request through AiGOL governance, executes only an authorized read-only worker capability, records replay evidence, and returns a governed result summary.

## What AiGOL Is Not

AiGOL is not:

- an autonomous agent
- an orchestration runtime
- a shell runner
- a network executor
- a filesystem mutation tool
- a memory system
- an unrestricted LLM execution system

## Architecture Overview

```text
Human
-> LLM Proposal
-> AiGOL Governance
-> Worker
-> Replay
-> Governed Result
```

## Core Invariant

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

## Typical Operator Flow

1. Choose a supported read-only capability:
   - `READ_ONLY_RUNTIME_INSPECTION`
   - `FILESYSTEM_READ_ONLY_INSPECTION`

2. Submit one bounded request through the minimal operator entrypoint:

```python
from aigol.runtime.minimal_operator_entrypoint import run_minimal_operator_entrypoint

result = run_minimal_operator_entrypoint(
    operator_flow_id="OPERATOR-FLOW-000001",
    human_request="Inspect bounded runtime metadata.",
    target_capability="READ_ONLY_RUNTIME_INSPECTION",
    created_at="2026-05-29T00:00:00+00:00",
    replay_dir=".runtime/operator_replay/OPERATOR-FLOW-000001",
)
```

3. Read `result["operator_result_summary"]`.

4. Keep the replay reference for audit.

## Filesystem Read-Only Example

Filesystem inspection requires explicit bounded path scope:

```python
result = run_minimal_operator_entrypoint(
    operator_flow_id="OPERATOR-FLOW-000002",
    human_request="Inspect an allowed file.",
    target_capability="FILESYSTEM_READ_ONLY_INSPECTION",
    created_at="2026-05-29T00:00:00+00:00",
    replay_dir=".runtime/operator_replay/OPERATOR-FLOW-000002",
    root_path="/path/to/root",
    requested_path="/path/to/root/allowed/file.txt",
    allowed_paths=["/path/to/root/allowed"],
)
```

AiGOL rejects paths outside the allowed scope.

## Governed Result Interpretation

The governed result summary contains:

- `status`: `ACCEPTED` or `REJECTED`
- `reason`: why the request was accepted or rejected
- `capability_used`: capability used by the governed flow
- `replay_reference`: where replay evidence exists
- `replay_verification_status`: whether replay reconstruction verified
- `authority_boundary_reminder`: invariant reminder
- `evidence_summary`: concise replay-derived evidence
- `recommended_next_action`: what the operator should do next

If `status` is `ACCEPTED`, use the result and retain the replay reference.

If `status` is `REJECTED`, read `reason`, correct the request if appropriate, and retry as a new bounded invocation.

## Replay Inspection

Use the replay summary command to inspect replay without manually opening artifacts:

```python
from aigol.runtime.replay_summary_command import summarize_operator_replay, render_replay_summary

summary = summarize_operator_replay(
    replay_dir=".runtime/operator_replay/OPERATOR-FLOW-000001",
)

print(render_replay_summary(summary))
```

The replay summary shows:

- Replay ID
- Status
- Capability
- Authorization Status
- Verification Status
- Result Summary
- Timestamp / Ordering Information

## Evidence Interpretation

Replay evidence is the audit source of truth.

Operator summaries are human-readable views of replay evidence. They do not replace replay, authorize execution, or create new authority.

When inspecting evidence, verify:

- replay verification status is `VERIFIED`
- authorization status is visible
- capability is one of the supported read-only capabilities
- result status is clear
- failure reason is retained when rejected

## Known Boundaries

Current AiGOL is read-only only.

It does not support:

- filesystem write
- filesystem delete
- filesystem move
- shell execution
- network execution
- API execution
- agents
- orchestration
- persistent memory
- autonomous continuation

## Operator Rule

Use AiGOL for one bounded read-only request at a time.

When in doubt, stop, inspect replay, and submit a new bounded request rather than trying to continue implicitly.
