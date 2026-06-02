# SESSION_DASHBOARD_RUNTIME_V1

## Status

Certified operator dashboard runtime.

## Purpose

Provide a read-only AiGOL CLI dashboard summarizing current operator-visible state.

This closes the operator situational awareness gap identified after conversation continuity, chain inspection, approval commands, and bridge authorization commands were certified.

## Commands

Implemented commands:

```text
dashboard
dashboard summary
dashboard approvals
dashboard bridges
dashboard chains
dashboard learning
dashboard execution
```

Each command supports:

```text
--replay-root
--limit
--json
```

## Runtime Surface

Implemented in:

```text
aigol/cli/commands/dashboard.py
```

Wired through:

```text
aigol/cli/aigol_cli.py
```

## Dashboard Contents

The dashboard summarizes:

- latest chains;
- pending approvals;
- pending bridge authorizations;
- recent execution requests;
- recent learning artifacts;
- suggested safe next actions.

## Certified Runtime Reuse

The dashboard reuses existing certified command groups where appropriate:

- `APPROVAL_COMMAND_GROUP_V1`;
- `BRIDGE_AUTHORIZATION_COMMAND_GROUP_V1`.

It scans replay-visible chain, execution, and learning evidence directly without invoking reconstruction commands that persist report events.

## Boundary Guarantees

The dashboard is read-only.

It does not:

- dispatch;
- invoke;
- execute;
- mutate governance;
- mutate replay;
- create execution requests;
- infer authorization.

## Replay And Chain Guarantees

The dashboard validates replay wrapper hashes and artifact hashes for relevant replay-visible artifacts before summarizing them.

It preserves canonical chain continuity by grouping and displaying `canonical_chain_id`, `current_chain_id`, `latest_chain_id`, and `related_chain_id` where present.

## Safe Next Actions

Suggested actions are read-only operator commands such as:

```text
approval pending
bridge pending
show-chain <CHAIN_ID>
show-full-lineage <CHAIN_ID>
show-learning-lifecycle <CHAIN_ID>
show-execution-lifecycle <CHAIN_ID>
```

They do not create execution authority.

## Final Classification

```text
SESSION_DASHBOARD_RUNTIME_STATUS = CERTIFIED
```
