# GOVERNED_CHATGPT_RUNTIME_BRIDGE_V1

## Status

Certified.

This milestone introduces one bounded ChatGPT-style tool relay into the already-proven localhost governed runtime. The bridge is a relay surface, not an execution engine.

## Contract

Tool: `sapianta_governed_invoke`

Input:

- `artifact`
- `host`
- `port`

Output:

- `status`
- `closure`
- `request_id`
- `response_id`
- `replay_identity`
- `evidence`

## Guarantees

- localhost-only request validation
- deterministic bridge request identity
- reuse of the existing governed operator/runtime path
- concise replay-visible response return
- fail-closed rejection of malformed, blocked, or non-local requests

## Boundaries

No new execution authority, orchestration, agents, retries, fallback routing, hidden state, dynamic provider routing, public exposure, `shell=True`, or unrestricted subprocess execution are introduced.
