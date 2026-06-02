# OPERATOR_WORKFLOW_RECOMMENDATIONS_V1

## Status

Review-only recommendations.

## Recommendation 1: Implement Approval First

Priority:

```text
HIGHEST
```

Implement:

```text
approval inbox
approval show <APPROVAL_ID>
approval decide <APPROVAL_ID>
approval history
```

This should preserve explicit human authorization and fail-closed semantics.

## Recommendation 2: Implement Bridge Authorization Second

Priority:

```text
HIGH
```

Implement:

```text
bridge show <BRIDGE_ID>
bridge authorize-execution-request <PLAN_ID>
```

Boundary requirements:

- no automatic execution request inference;
- no dispatch;
- no invocation;
- no execution;
- replay-visible authorization evidence.

## Recommendation 3: Implement Plan Inspection Third

Priority:

```text
HIGH
```

Implement:

```text
plan show <PLAN_ID>
plan lineage <PLAN_ID>
plan bridge-status <PLAN_ID>
```

The plan view should extract:

- plan status;
- plan scope;
- planned targets;
- planned validation;
- approval reference;
- bridge reference;
- execution-request linkage.

## Recommendation 4: Implement Governed Learning Commands Fourth

Priority:

```text
MEDIUM_HIGH
```

Implement:

```text
learning evaluate-result
learning propose-improvement
learning review-improvement
learning approve-improvement
learning plan-implementation
learning status <CHAIN_ID>
```

These commands should expose workflow state without automatic bridge or execution transition.

## Recommendation 5: Implement Session Dashboard Fifth

Priority:

```text
MEDIUM_HIGH
```

Implement:

```text
session dashboard
session current-chain
session next-actions
```

Minimum display:

- current chain;
- latest chain;
- related chains;
- pending approvals;
- latest proposal;
- latest plan;
- bridge authorization status;
- execution request status;
- latest fail-closed event;
- safe next commands.

## Recommendation 6: Add Conversation Shortcuts Last

Priority:

```text
MEDIUM
```

Add read-only conversation shortcuts:

```text
/chain
/lineage
/learning
/execution
/next
```

These should call inspection/dashboard surfaces and must not create execution authority.

## Minimum Implementation Set For Certification

Required:

- approval command group;
- bridge authorization command;
- implementation plan inspection;
- governed learning command group;
- session dashboard;
- read-only conversation inspection shortcuts.

## Certification Target

After the minimum set is implemented and tested, AiGOL may be reviewed for:

```text
AIGOL_CLI_PRIMARY_INTERFACE_STATUS = CERTIFIED
```
