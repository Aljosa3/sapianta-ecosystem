# AIGOL_OPERATOR_INTERFACE_STATE_REVIEW_V1

## Status

`AIGOL_OPERATOR_INTERFACE_STATUS = READY_FOR_EXTENSION`

## Purpose

This review determines whether AiGOL already has operator-facing interfaces before creating `AIGOL_OPERATOR_CLI_V1`.

No runtime, CLI, worker, provider, authorization, or replay behavior is changed by this review.

## Finding

AiGOL can already be operated today for several bounded workflows, especially:

- governance/status inspection;
- semantic ingress and continuity preview;
- controlled execution handoff through the existing CLI substrate;
- read-only runtime inspection;
- replay inspection, replay verification, replay listing, and runtime summaries;
- first real operator usage through the live governed runtime path;
- programmatic provider, authorization, filesystem worker, and GitHub issue-draft worker execution.

However, the operator interface is fragmented. The newest provider -> authorization -> domain worker path exists as runtime/tests, not as a unified operator-facing command.

## Existing Operator Surfaces

### Canonical AiGOL CLI

Entrypoint:

```text
python -m aigol.cli.aigol_cli
```

Representative commands:

- `status`
- `ingress generate`
- `governance validate`
- `continuity preview`
- `dispatch authorize`
- `execution handoff`
- `return inspect`
- `replay ledger`
- `replay verify`
- `diagnostics runtime`
- `moc ...`
- `cognition ...`

Status: usable, broad, governance-oriented.

### Runtime Execution CLI

Entrypoint:

```text
python -m aigol.runtime.operator.runtime_execution_cli
```

Commands exposed by runtime contract:

- `inspect-runtime`
- `inspect-replay`
- `verify-replay`
- `list-replays`
- `latest-replay`
- `show-runtime-session`
- `runtime-summary`
- `inspect-runtime-contract`

Status: usable for read-only runtime/replay operations.

### Minimal Runtime Operator CLI

Entrypoint:

```text
python -m aigol.runtime.operator.runtime_cli
```

Commands:

- `summary`
- `goal`
- `retry`

Status: usable for persisted runtime artifact inspection.

### Live Readonly Operator CLI

Entrypoint:

```text
python -m aigol.runtime.operator_cli "<prompt>"
```

Status: usable for one bounded read-only operator prompt through the live governed runtime path.

## Programmatic Runtime Interfaces

The latest end-to-end and domain-worker paths are programmatic:

- `run_provider_attachment(...)`
- `authorize_worker_request(...)`
- `create_authorized_worker_request(...)`
- `execute_filesystem_create_request(...)`
- `create_github_issue_draft_request(...)`
- `execute_github_issue_draft_request(...)`
- replay reconstruction helpers for provider, authorization, filesystem worker, and GitHub worker.

Status: operational, tested, not yet exposed as a unified operator CLI.

## Can AiGOL Already Be Operated Today?

Yes.

AiGOL can be operated today through existing CLI commands for governance, replay, inspection, status, and read-only operator flows. The newest useful/domain-worker flow can be operated programmatically and is validated by tests, but lacks a first-class operator command.

## Is AIGOL_OPERATOR_CLI_V1 Required?

A completely new CLI architecture is not required.

What is required is a small extension of an existing operator CLI surface to expose the newly certified provider -> authorization -> domain-worker path.

## Recommendation

Do not create a duplicate operator CLI.

Extend the existing operator CLI family, preferably by adding a narrow command group to the canonical `aigol.cli.aigol_cli` or the operational `aigol.runtime.operator.runtime_execution_cli`, after defining the command contract.

