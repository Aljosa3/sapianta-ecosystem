# BOUNDED_RUNTIME_WRITABLE_STATE_V1

This milestone introduces an isolated writable runtime-state directory for bounded Codex execution.

The state directory exists only to support Codex CLI local state/app-server initialization without mutating the real user home, repository root, global config, or uncontrolled cache paths.

## Scope

The runtime state directory is:

- explicit
- isolated
- bounded
- deterministic
- lineage-bound
- provider-bound
- session-bound
- writable only inside the approved runtime-state root

Default root:

```text
/tmp/sapianta_codex_runtime/<session_id>
```

## Environment Boundary

The runtime may set only:

- `HOME=<bounded_runtime_state_dir>`
- `XDG_CACHE_HOME=<bounded_runtime_state_dir>/cache`
- `XDG_CONFIG_HOME=<bounded_runtime_state_dir>/config`
- `TMPDIR=<bounded_runtime_state_dir>/tmp`

No global user config is mutated. `shell=False` remains required.

## Non-Goals

This milestone does not introduce unrestricted filesystem access, workspace escape, orchestration, retries, fallback, provider routing, autonomous execution, background execution, network expansion, arbitrary shell execution, hidden prompt rewriting, or memory mutation.
