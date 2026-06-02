# BRIDGE_AUTHORIZATION_COMMAND_GROUP_V1

## Status

Certified operator command group.

## Purpose

Provide a dedicated AiGOL CLI bridge command group for inspecting bridge authorization and learning-to-execution transitions.

This closes the bridge authorization visibility gap identified by `OPERATOR_WORKFLOW_GAP_CLOSURE_V1`.

## Commands

Implemented command group:

```text
bridge list
bridge show <BRIDGE_ID>
bridge pending
bridge approved
bridge rejected
bridge chain <CHAIN_ID>
bridge execution-request <EXECUTION_REQUEST_ID>
```

Each command supports:

```text
--replay-root
--json
```

## Runtime Surface

Implemented in:

```text
aigol/cli/commands/bridge.py
```

Wired through:

```text
aigol/cli/aigol_cli.py
```

## Bridge Evidence Recognized

The command group inspects replay-visible bridge artifacts:

- `IMPLEMENTATION_PLAN_EXECUTION_REQUEST_LINK_ARTIFACT_V1`;
- implementation-plan-derived `EXECUTION_REQUEST_ARTIFACT_V1`.

The command group validates replay wrapper hashes and artifact hashes before displaying bridge evidence.

## Boundary Guarantees

The command group is read-only.

It does not:

- dispatch;
- invoke;
- execute;
- mutate governance;
- mutate replay;
- create execution requests;
- bypass authorization runtimes;
- infer human authorization.

## Chain Continuity

Where bridge artifacts include `canonical_chain_id`, the command group preserves and filters by canonical chain identity:

```text
bridge chain <CHAIN_ID>
```

## Human Authority Boundary

The command group displays `human_authorization_reference` where replay evidence contains it.

It does not create or replace human authorization.

## Fail-Closed Semantics

Corrupt bridge replay evidence fails closed in the command result and is displayed to the operator.

Missing bridge ids and missing execution request ids fail closed without authority expansion.

## Final Classification

```text
BRIDGE_AUTHORIZATION_COMMAND_GROUP_STATUS = CERTIFIED
```
