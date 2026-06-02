# OPERATOR_WORKFLOW_GAP_CLOSURE_V1

## Status

Review-only gap closure analysis.

No runtime implementation, CLI modification, governance mutation, execution request creation, dispatch, invocation, or execution is introduced by this artifact.

## Purpose

Identify the minimum operator workflow capabilities required to move:

```text
AIGOL_CLI_PRIMARY_INTERFACE_STATUS = READY_WITH_GAPS
```

to:

```text
AIGOL_CLI_PRIMARY_INTERFACE_STATUS = CERTIFIED
```

## Current Position

AiGOL Core is effectively complete for the certified foundation:

- execution lifecycle;
- governed learning lifecycle;
- learning-to-execution bridge;
- replay reconstruction runtime;
- CLI chain inspection runtime;
- conversation chain continuity runtime;
- interactive conversation CLI.

The remaining gaps are operator-facing workflow gaps, not constitutional authority gaps.

## Direct Answers

### 1. Which operator workflows are still incomplete?

Incomplete workflows:

- approval inbox, approval decision, and approval history;
- governed learning workflow operation;
- implementation plan inspection;
- bridge execution-request authorization;
- source-aware readiness visibility;
- conversation session dashboard;
- in-conversation safe inspection shortcuts.

### 2. Which workflows still require ChatGPT mediation?

ChatGPT mediation remains useful for:

- selecting a next workflow step from ambiguous context;
- summarizing multi-artifact governance narratives;
- drafting approval rationale;
- drafting improvement or remediation proposals;
- explaining source-aware readiness failures;
- interpreting older compatibility replay evidence.

### 3. Which workflows still require manual artifact inspection?

Manual artifact inspection remains likely for:

- approval context;
- improvement proposal and review details;
- implementation plan contents;
- plan-to-execution-request bridge linkage;
- source-aware readiness mismatches;
- older replay evidence without `canonical_chain_id`;
- unusual fail-closed reconstruction causes.

### 4. Can approval management be performed from CLI?

Not as a first-class primary workflow.

The underlying approval runtimes exist, but the CLI does not yet provide a complete approval inbox, approval show, approval decide, or approval history flow.

### 5. Can governed learning be monitored from CLI?

Partially.

The CLI can inspect learning lifecycle evidence through chain reconstruction. It cannot yet operate or monitor governed learning as a dedicated workflow with first-class commands.

### 6. Can implementation plans be inspected from CLI?

Partially.

Full lineage can reveal plan evidence, but the CLI does not yet provide a plan-specific view that extracts plan status, scope, targets, validation requirements, authorization references, and bridge linkage.

### 7. Can bridge authorization be managed from CLI?

No.

The learning-to-execution bridge requires explicit human authorization. The CLI does not yet expose a first-class bridge authorization command.

### 8. What minimum dashboard/session visibility is required?

Minimum required visibility:

- current chain;
- latest chain;
- related chains;
- pending approvals;
- latest proposal;
- latest implementation plan;
- bridge authorization status;
- execution request status;
- latest fail-closed event;
- safe next commands.

### 9. Which gap has the highest impact on daily usability?

Highest impact:

```text
approval and bridge authorization workflow visibility
```

Without this, a human can inspect evidence but cannot comfortably move governed workflows forward from the CLI.

### 10. What is the smallest implementation set required for CERTIFIED?

Minimum implementation set:

1. Approval command group.
2. Learning workflow command group.
3. Plan inspection command.
4. Bridge authorization command.
5. Conversation/session dashboard.
6. Safe in-conversation inspection shortcuts.

This set should reuse existing governed runtimes and reconstruction evidence. It should not introduce new authority semantics.

## Minimum Certification Path

The shortest path to certification is not a broad redesign.

It is a bounded operator layer:

```text
approval
learning
plan
bridge
session
conversation shortcuts
```

implemented as CLI affordances over already certified runtimes.

## Final Classification

```text
OPERATOR_WORKFLOW_GAP_CLOSURE_STATUS = READY
```

The gap closure path is clear and bounded. Implementation remains future work.
