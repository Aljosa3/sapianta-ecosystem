# GOVERNED_MCP_RUNTIME_WRAPPER_V1

## Status

Certified.

This milestone adds an MCP-ready wrapper surface around the existing governed ChatGPT bridge. It exposes exactly one tool and does not add transport, execution, or authority beyond the already-proven bridge path.

## Tool

`sapianta_governed_invoke`

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

- exactly one exposed tool
- localhost-only validation
- direct reuse of `invoke_from_chatgpt_bridge(...)`
- deterministic response projection
- fail-closed rejection of malformed input or malformed bridge output

## Boundaries

No agents, orchestration, retries, fallback routing, hidden execution, hidden state, hidden memory, autonomous continuation, public exposure, `shell=True`, or unrestricted subprocess execution are introduced.
