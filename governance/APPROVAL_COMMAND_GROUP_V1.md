# APPROVAL_COMMAND_GROUP_V1

## Status

Certified operator command group.

## Purpose

Provide a dedicated AiGOL CLI approval command group for inspecting governed approval artifacts.

This closes the highest-impact operator workflow visibility gap identified by `OPERATOR_WORKFLOW_GAP_CLOSURE_V1`.

## Commands

Implemented command group:

```text
approval list
approval show <APPROVAL_ID>
approval pending
approval approved
approval rejected
approval chain <CHAIN_ID>
```

Each command supports:

```text
--replay-root
--json
```

## Runtime Surface

Implemented in:

```text
aigol/cli/commands/approval.py
```

Wired through:

```text
aigol/cli/aigol_cli.py
```

## Approval Evidence Recognized

The command group inspects replay-visible approval artifacts:

- `PROPOSAL_APPROVAL_ARTIFACT_V1`;
- `IMPROVEMENT_APPROVAL_ARTIFACT_V1`.

The command group validates replay wrapper hashes and artifact hashes before displaying approval evidence.

## Boundary Guarantees

The command group is read-only.

It does not:

- dispatch;
- invoke;
- execute;
- mutate governance;
- mutate replay;
- create execution requests;
- bypass approval runtimes;
- infer approval decisions.

## Chain Continuity

Where approval artifacts include `canonical_chain_id`, the command group preserves and filters by canonical chain identity:

```text
approval chain <CHAIN_ID>
```

Older proposal approvals without `canonical_chain_id` remain visible in list/show/status views, but are not upgraded to canonical chain identity.

## Fail-Closed Semantics

Corrupt approval replay evidence fails closed in the command result and is displayed to the operator.

Missing approval ids fail closed without authority expansion.

## Final Classification

```text
APPROVAL_COMMAND_GROUP_STATUS = CERTIFIED
```
