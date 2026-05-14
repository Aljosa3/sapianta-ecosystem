# FIRST_REAL_E2E_CODEX_LOOP_V1

This milestone introduces the first real bounded operational end-to-end Codex loop using the governed execution substrate.

The loop proves:

- real deterministic bounded Codex execution works
- governance lineage survives the full loop
- result return continuity is preserved
- no manual internal copy/paste is required
- replay evidence is generated for the full loop
- runtime remains bounded and fail-closed

## Flow

```text
ChatGPT request
-> ingress
-> natural-language-to-envelope
-> governed session reference
-> execution gate
-> bounded Codex execution
-> result capture
-> governed return
-> ChatGPT-facing response
```

## Boundaries

This milestone does not introduce orchestration, retries, fallback logic, provider routing, adaptive provider selection, hidden execution, hidden prompt rewriting, memory mutation, scheduling, concurrent execution, background execution, unrestricted shell execution, arbitrary subprocess execution, unrestricted filesystem access, network execution, external APIs, or autonomous continuation.

The only allowed runtime command shape remains:

```text
codex run <prepared_task_artifact>
```
