# AIGOL_CLI_PRIMARY_INTERFACE_GAP_ANALYSIS_V1

## Purpose

Identify gaps that prevent AiGOL CLI from becoming the primary operational interface.

## Gap 1: Conversation Does Not Manage Runtime Actions

Status:

```text
OPEN
```

The interactive conversation CLI answers prompts and records replay evidence. It does not yet present governed actions such as proposal creation, approval, execution request creation, learning workflow creation, or bridge authorization.

## Gap 2: No Unified Chain Reconstruction CLI

Status:

```text
OPEN
```

Existing replay commands inspect operator operations, but no single CLI command reconstructs:

```text
Conversation
-> Execution Lifecycle
-> Result
-> Governed Learning
-> Implementation Plan
-> Bridge Execution Request
```

## Gap 3: Runtime Approval Management Is Not First-Class

Status:

```text
OPEN
```

Certified proposal approval and improvement approval runtimes exist. The CLI does not yet provide a primary approval inbox, approval decision command, approval history command, or explicit bridge authorization command.

## Gap 4: Governed Learning Workflow CLI Is Missing

Status:

```text
OPEN
```

The CLI does not yet manage:

- result evaluation;
- improvement proposal creation;
- improvement review;
- improvement approval;
- implementation planning;
- learning chain inspection.

## Gap 5: Implementation Plan Inspection Is Missing

Status:

```text
OPEN
```

Implementation plans can be created and reconstructed through runtime code, but there is no dedicated CLI command for plan inspection, plan lineage, plan authorization status, or plan-to-request linkage.

## Gap 6: Bridge Authorization CLI Is Missing

Status:

```text
OPEN
```

The bridge runtime requires explicit human execution-request authorization. The CLI does not yet expose an ergonomic command for that authorization.

## Gap 7: Source-Aware Readiness Integration Remains Future Work

Status:

```text
OPEN
```

The implementation-plan-to-execution-request bridge creates source-aware execution requests. Existing readiness runtime remains proposal-derived. The primary CLI cannot be complete until this source-aware path is managed or clearly surfaced as pending.

## Gap 8: Operator Session Context Is Limited

Status:

```text
OPEN
```

The interactive CLI does not implement durable conversational memory or a session dashboard that tracks current proposals, approvals, execution requests, plans, workers, failures, and replay chains.

## Gap Classification

```text
AIGOL_CLI_PRIMARY_INTERFACE_GAPS = OPERATOR_WORKFLOW_INTEGRATION_REQUIRED
```

The gaps are usability and orchestration-surface gaps, not constitutional authority gaps.
