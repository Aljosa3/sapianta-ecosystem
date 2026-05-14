# CODEX_CLI_CONTRACT_DISCOVERY_V1

This package safely discovers the installed Codex CLI invocation contract after live validation showed that `codex run <prepared_task_artifact>` is not accepted by the local CLI.

The harness only runs safe introspection probes:

- `codex --help`
- `codex -h`
- `codex run --help`
- `codex run -h`
- `codex --version`

It does not execute a task, use `shell=True`, mutate repository files, route providers, retry, fallback, or introduce orchestration.

Discovery is partial when non-interactive execution can be identified but file/stdin input support cannot be confirmed from the allowed probes.
