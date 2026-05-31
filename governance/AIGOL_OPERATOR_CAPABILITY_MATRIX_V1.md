# AIGOL_OPERATOR_CAPABILITY_MATRIX_V1

## Capability Matrix

| Capability | Existing Surface | Status | Operator Usefulness | Notes |
| --- | --- | --- | --- | --- |
| Status inspection | `aigol.cli.aigol_cli status` | ALREADY_EXISTS | High | Deterministic governance status surface. |
| Ingress artifact generation | `aigol.cli.aigol_cli ingress generate` | ALREADY_EXISTS | Medium | Creates semantic input artifacts, not full runtime operation. |
| Governance validation | `aigol.cli.aigol_cli governance validate` | ALREADY_EXISTS | High | Useful for continuity/governance checks. |
| Continuity preview | `aigol.cli.aigol_cli continuity preview` | ALREADY_EXISTS | Medium | Preview only; not the newest domain-worker path. |
| Dispatch authorization preview/path | `aigol.cli.aigol_cli dispatch authorize`, `moc dispatch-*` | PARTIALLY_EXISTS | Medium | Existing controlled dispatch concepts; should not be duplicated blindly. |
| Controlled execution handoff | `aigol.cli.aigol_cli execution handoff` | PARTIALLY_EXISTS | Medium | Existing handoff path; not the new provider/authorization/domain-worker stack. |
| Return inspection | `aigol.cli.aigol_cli return inspect` | ALREADY_EXISTS | Medium | Replay/return inspection. |
| Replay ledger | `aigol.cli.aigol_cli replay ledger` | ALREADY_EXISTS | High | Operator can inspect replay ledger. |
| Replay verification | `aigol.cli.aigol_cli replay verify`, `runtime_execution_cli verify-replay` | ALREADY_EXISTS | High | Core audit utility already exists. |
| Runtime inspection | `runtime_execution_cli inspect-runtime` | ALREADY_EXISTS | High | Read-only runtime inspection through existing governed path. |
| Runtime replay inspection | `runtime_execution_cli inspect-replay` | ALREADY_EXISTS | High | Reconstructs persisted operational replay. |
| Runtime replay listing | `runtime_execution_cli list-replays`, `latest-replay` | ALREADY_EXISTS | High | Operator can browse replay evidence. |
| Runtime session view | `runtime_execution_cli show-runtime-session` | ALREADY_EXISTS | Medium | Useful session-level view. |
| Runtime summary | `runtime_execution_cli runtime-summary`, `runtime_cli summary` | ALREADY_EXISTS | High | Multiple summary surfaces exist. |
| Goal summary | `runtime_cli goal` | ALREADY_EXISTS | Medium | Available for persisted goal artifacts. |
| Retry summary | `runtime_cli retry` | ALREADY_EXISTS | Medium | Available for persisted retry artifacts. |
| Read-only prompt operation | `aigol.runtime.operator_cli` | ALREADY_EXISTS | Medium | Bound to existing read-only live governed runtime. |
| Provider proposal attachment | `aigol.provider.provider_runtime` | PARTIALLY_EXISTS | Medium | Runtime exists; operator-facing command is missing. |
| Provider registry inspection | `ProviderRegistry` programmatic API | PARTIALLY_EXISTS | Medium | Metadata exists; CLI inspection missing. |
| Authorization artifact creation | `aigol.authorization.authorization_runtime` | PARTIALLY_EXISTS | High | Runtime exists; operator-facing command missing. |
| Authorization validation | `authorization_record`, `authorization_validator` | PARTIALLY_EXISTS | High | Programmatic and tested; CLI missing. |
| Filesystem worker operation | `aigol.workers.filesystem_worker` | PARTIALLY_EXISTS | Medium | Runtime/tested; no operator command. |
| GitHub issue-draft worker | `aigol.workers.github_worker` | PARTIALLY_EXISTS | High | Useful domain worker exists; no operator command. |
| Full provider -> authorization -> worker operation | Tests/programmatic composition | PARTIALLY_EXISTS | High | Operational proof exists; operator-facing composition missing. |

## Summary

Operator capability is broad but fragmented. Inspection and replay are already strong. The missing surface is not architecture; it is a narrow operator command for the latest governed operation stack.

