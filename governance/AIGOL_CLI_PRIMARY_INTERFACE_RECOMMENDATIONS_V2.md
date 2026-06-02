# AIGOL_CLI_PRIMARY_INTERFACE_RECOMMENDATIONS_V2

## Status

Review-only recommendations.

## Recommendation 1: Certify As Ready With Gaps

Classify the primary CLI interface as:

```text
AIGOL_CLI_PRIMARY_INTERFACE_STATUS = READY_WITH_GAPS
```

This accurately reflects that the CLI can now replace most inspection and conversation copy/paste workflows, but cannot yet replace every governed operation workflow.

## Recommendation 2: Add A Conversation Inspection Shortcut

Add a future read-only shortcut inside conversation mode for safe inspection commands, such as:

```text
/chain
/lineage
/learning
/execution
```

These should call existing inspection commands and must not create execution authority.

## Recommendation 3: Add Approval CLI Surface

Implement a first-class approval command group:

```text
approval inbox
approval show <ID>
approval decide <ID>
approval history
```

This should preserve explicit human authorization and fail-closed semantics.

## Recommendation 4: Add Governed Learning CLI Surface

Implement a bounded learning command group:

```text
learning evaluate-result
learning propose-improvement
learning review-improvement
learning approve-improvement
learning plan-implementation
learning show-plan <PLAN_ID>
```

This should expose governed learning lifecycle operation without automatic execution.

## Recommendation 5: Add Bridge Authorization Command

Implement an explicit bridge authorization command:

```text
bridge authorize-execution-request <PLAN_ID>
```

This must preserve:

- separate human authorization;
- no automatic dispatch;
- no invocation;
- no execution.

## Recommendation 6: Add Session Dashboard

Conversation mode should expose a read-only session dashboard:

```text
current chain
latest chain
related chains
open proposals
pending approvals
implementation plans
execution requests
recent fail-closed events
safe next commands
```

## Recommendation 7: Preserve Review-Only Boundaries

Future work should remain bounded:

- do not add autonomous execution;
- do not infer authorization;
- do not repair replay silently;
- do not mutate governance through inspection commands;
- do not frame the CLI as unrestricted agent autonomy.

## Final Recommendation

Proceed with CLI as the primary operator entry point for inspection-centered daily operation, while retaining ChatGPT or manual artifact review for complex workflow interpretation until approval, learning, bridge, and dashboard surfaces are implemented.
