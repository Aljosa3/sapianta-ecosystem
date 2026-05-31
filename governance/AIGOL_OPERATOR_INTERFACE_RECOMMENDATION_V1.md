# AIGOL_OPERATOR_INTERFACE_RECOMMENDATION_V1

## Recommendation

`AIGOL_OPERATOR_INTERFACE_STATUS = READY_FOR_EXTENSION`

## Direct Answers

### Can AiGOL already be operated today?

Yes.

Operators can use:

```text
python -m aigol.cli.aigol_cli status
python -m aigol.cli.aigol_cli ingress generate ...
python -m aigol.cli.aigol_cli governance validate ...
python -m aigol.cli.aigol_cli replay ledger ...
python -m aigol.cli.aigol_cli replay verify ...
python -m aigol.runtime.operator.runtime_execution_cli inspect-runtime-contract
python -m aigol.runtime.operator.runtime_execution_cli inspect-runtime
python -m aigol.runtime.operator.runtime_execution_cli inspect-replay ...
python -m aigol.runtime.operator.runtime_execution_cli list-replays
python -m aigol.runtime.operator.runtime_execution_cli latest-replay
python -m aigol.runtime.operator.runtime_execution_cli runtime-summary
python -m aigol.runtime.operator.runtime_cli --root <root> summary <runtime_id>
python -m aigol.runtime.operator.runtime_cli --root <root> goal <goal_id>
python -m aigol.runtime.operator.runtime_cli --root <root> retry <runtime_id>
python -m aigol.runtime.operator_cli "<prompt>"
```

Limitations:

- interfaces are fragmented;
- some commands target older read-only flows;
- the newest provider/authorization/domain-worker operation is not available as a single operator CLI command;
- new worker replay reconstruction is programmatic, not a user-facing replay summary.

### Is a new `AIGOL_OPERATOR_CLI_V1` required?

Not as a new standalone architecture.

Required capability:

```text
Expose the certified provider -> authorization -> domain-worker path through an existing operator CLI surface.
```

### Which component should be extended?

Preferred extension target:

```text
aigol.cli.aigol_cli
```

because it is already the canonical deterministic AiGOL governance CLI foundation.

Alternative extension target:

```text
aigol.runtime.operator.runtime_execution_cli
```

because it already exposes operational runtime and replay inspection commands.

## Smallest Next Step

Define a command contract before implementing:

```text
aigol operation github-issue-draft
aigol operation replay-summary
```

or equivalent, reusing:

- provider runtime;
- authorization runtime;
- GitHub issue-draft worker;
- existing replay reconstruction helpers.

No new runtime architecture is required.

