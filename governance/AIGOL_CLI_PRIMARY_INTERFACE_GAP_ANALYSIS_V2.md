# AIGOL_CLI_PRIMARY_INTERFACE_GAP_ANALYSIS_V2

## Status

Review-only gap analysis.

## Closed Since V1

### Gap: No Unified Chain Reconstruction CLI

Status:

```text
CLOSED
```

`CLI_CHAIN_INSPECTION_RUNTIME_V1` exposes operator-facing reconstruction commands backed by `UNIFIED_REPLAY_RECONSTRUCTION_RUNTIME_V1`.

### Gap: Conversation Does Not Link To Chains

Status:

```text
CLOSED_WITH_LIMITS
```

`CONVERSATION_CHAIN_CONTINUITY_RUNTIME_V1` exposes canonical chain ids and suggested inspection commands from conversation outputs.

Limit:

Conversation mode suggests inspection commands but does not automatically run inspection views inside the loop.

## Remaining Gaps

### Gap 1: Approval Management Is Not First-Class

Status:

```text
OPEN
```

The CLI still lacks a primary approval inbox, approval decision command, approval history command, and bridge-specific authorization command.

### Gap 2: Governed Learning Workflow Operation Is Missing

Status:

```text
OPEN
```

The CLI can inspect learning lifecycle evidence, but does not yet operate the learning workflow as a first-class command group.

Missing:

- result evaluation command;
- improvement proposal command;
- improvement review command;
- improvement approval command;
- implementation planning command.

### Gap 3: Implementation Plan Inspection Is Too Shallow

Status:

```text
OPEN
```

Full lineage can reveal plan artifacts, but operators still need a dedicated plan view for:

- plan status;
- plan scope;
- planned targets;
- validation requirements;
- authorization relationship;
- plan-to-request linkage.

### Gap 4: Bridge Authorization CLI Is Missing

Status:

```text
OPEN
```

The learning-to-execution bridge requires explicit human execution-request authorization.

The CLI does not yet provide an ergonomic command for that authorization.

### Gap 5: Source-Aware Readiness Needs Operator Surface

Status:

```text
OPEN
```

Source-aware execution requests need clear operator display before readiness and dispatch workflows can be treated as primary CLI workflows.

### Gap 6: Session Dashboard Is Missing

Status:

```text
OPEN
```

Conversation mode does not yet provide a dashboard of:

- current chain;
- latest chain;
- related chains;
- proposals;
- approvals;
- implementation plans;
- execution requests;
- workers;
- failures;
- recommended next safe commands.

### Gap 7: Compatibility Replay Requires Manual Interpretation

Status:

```text
OPEN
```

Older replay artifacts without `canonical_chain_id` remain compatibility evidence and may require manual interpretation.

## Gap Classification

```text
AIGOL_CLI_PRIMARY_INTERFACE_GAPS = WORKFLOW_AND_OPERATOR_ERGONOMICS_REMAINING
```

The remaining gaps are not constitutional authority gaps.
