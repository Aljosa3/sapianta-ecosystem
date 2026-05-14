# CODEX_CLI_CONTRACT_DISCOVERY_V1

This milestone deterministically discovers the installed Codex CLI invocation contract after live validation was blocked by `codex run <prepared_task_artifact>` returning exit code 2.

## Discovery Result

Status: `DISCOVERED_PARTIAL`

The installed Codex CLI was detected and reports version:

```text
codex-cli 0.130.0-alpha.5
```

Safe help output advertises `exec` as the non-interactive subcommand. The safe probes do not confirm file-based prompt input or stdin prompt input. The safest bounded candidate discovered from allowed probes is:

```json
["codex", "exec", "<bounded_prompt>"]
```

## Boundary

Only safe introspection commands were used. No real task was executed, no shell was used, and no repository mutation was introduced.
