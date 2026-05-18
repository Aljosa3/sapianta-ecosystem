# LIVE_MCP_HOST_REGISTRATION_V1

This milestone creates the first live MCP host registration surface for the
already-governed SAPIANTA runtime wrapper.

## Scope

- exposes exactly one MCP tool: `sapianta_governed_invoke`
- uses the official Python MCP SDK when present
- delegates every tool call to the existing governed bridge path
- preserves localhost-only downstream runtime invocation

## Non-goals

- no new runtime authority
- no orchestration, retry, fallback, routing, or hidden continuation
- no public execution surface
- no hand-built replacement MCP protocol stack

## Operational Boundary

The live host entrypoint is `python -m
sapianta_system.runtime.mcp_wrapper.live_mcp_server`. It requires the official
`mcp` Python package at launch time and fails closed if that dependency is not
installed.

The host is suitable for a local MCP client. ChatGPT connector registration
requires a separately approved remote MCP deployment decision because the
current milestone explicitly preserves local-only boundaries.
