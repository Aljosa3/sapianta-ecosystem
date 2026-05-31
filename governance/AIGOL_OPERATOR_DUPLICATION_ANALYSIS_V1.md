# AIGOL_OPERATOR_DUPLICATION_ANALYSIS_V1

## Duplication Risk

A new standalone `AIGOL_OPERATOR_CLI_V1` would duplicate several existing surfaces if it is created as a parallel CLI.

## Feature Duplication Matrix

| Proposed Feature | Existing Coverage | Classification |
| --- | --- | --- |
| Status command | `aigol.cli.aigol_cli status` | ALREADY_EXISTS |
| Ingress command | `aigol.cli.aigol_cli ingress generate` | ALREADY_EXISTS |
| Governance validation | `aigol.cli.aigol_cli governance validate` | ALREADY_EXISTS |
| Replay verify | `aigol.cli.aigol_cli replay verify`, `runtime_execution_cli verify-replay` | ALREADY_EXISTS |
| Replay list/latest | `runtime_execution_cli list-replays`, `latest-replay` | ALREADY_EXISTS |
| Runtime summary | `runtime_execution_cli runtime-summary`, `runtime_cli summary` | ALREADY_EXISTS |
| Goal/retry inspection | `runtime_cli goal`, `runtime_cli retry` | ALREADY_EXISTS |
| Runtime contract inspection | `runtime_execution_cli inspect-runtime-contract` | ALREADY_EXISTS |
| Read-only operator prompt | `aigol.runtime.operator_cli` | ALREADY_EXISTS |
| Provider proposal command | Programmatic runtime only | PARTIALLY_EXISTS |
| Authorization command | Programmatic runtime only | PARTIALLY_EXISTS |
| Domain worker command | Programmatic runtime only | PARTIALLY_EXISTS |
| Unified governed operation command | Tests/programmatic composition only | MISSING |
| Unified evidence view for provider/authorization/worker replay | Programmatic reconstruction only | MISSING |

## Conclusion

Do not build a separate CLI that reimplements status, replay, runtime summary, governance validation, or read-only inspection.

The correct next step is an extension layer that reuses existing commands and adds only the missing governed operation and evidence-display commands.

