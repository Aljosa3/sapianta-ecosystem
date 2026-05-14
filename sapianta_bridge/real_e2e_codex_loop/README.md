# FIRST_REAL_E2E_CODEX_LOOP_V1

This package defines the first real bounded operational Codex end-to-end loop for SAPIANTA / AiGOL.

The loop connects:

```text
ChatGPT request
-> ingress
-> natural language to envelope
-> governed session reference
-> execution gate
-> bounded Codex execution
-> result capture
-> governed result return
-> ChatGPT-facing response
```

The loop remains single-pass, single-provider, human-authorized, replay-safe, deterministic, and fail-closed.

The only allowed runtime command shape is:

```text
codex run <prepared_task_artifact>
```

The implementation does not introduce orchestration, retries, fallback, routing, adaptive provider selection, hidden prompt rewriting, memory mutation, background execution, concurrent execution, network execution, or unrestricted shell execution.
