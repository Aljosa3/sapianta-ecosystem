# AIGOL_CLI_PRIMARY_INTERFACE_RECOMMENDATIONS_V1

## Purpose

Recommend the next steps required for AiGOL CLI to become the primary operator interface.

## Recommendation 1: Add A Unified Operator Dashboard

Add a read-only CLI command that summarizes:

- latest prompts;
- latest proposals;
- pending approvals;
- latest execution requests;
- latest implementation plans;
- bridge-linked execution requests;
- latest replay failures;
- latest worker and execution status.

This should remain replay-backed and fail closed on corrupt evidence.

## Recommendation 2: Add Runtime Artifact Inspection Commands

Add dedicated inspection commands for certified runtime artifacts:

- proposal;
- approval;
- execution request;
- ready for dispatch;
- worker assignment;
- dispatch;
- invocation;
- execution;
- completion;
- result;
- evaluation;
- improvement proposal;
- improvement review;
- improvement approval;
- implementation plan;
- implementation-plan bridge.

## Recommendation 3: Add Approval Inbox And Decision Commands

Add a first-class approval workflow:

```text
list pending approvals
inspect approval target
approve
reject
expire
reconstruct approval
```

The workflow must preserve explicit human authorization and replay visibility.

## Recommendation 4: Add Governed Learning CLI Workflow

Expose the certified governed learning lifecycle through CLI commands:

```text
result evaluate
improvement propose
improvement review
improvement approve
implementation plan
implementation inspect
```

Each command should map to the certified runtime boundary and avoid hidden mutation or automatic approval.

## Recommendation 5: Add Bridge Authorization CLI

Expose `IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST_RUNTIME_V1` through a dedicated command requiring explicit human authorization:

```text
implementation request-execution
```

The command must not mark readiness, dispatch workers, invoke workers, execute code, or mutate governance.

## Recommendation 6: Add Unified Replay Reconstruction

Add a command that reconstructs the complete operator chain:

```text
conversation
-> proposal
-> approval
-> execution request
-> ready for dispatch
-> worker assignment
-> dispatch
-> invocation
-> execution
-> result
-> completion
-> evaluation
-> improvement proposal
-> review
-> approval
-> implementation plan
-> bridge execution request
```

## Recommendation 7: Keep Conversation As The Front Door

Keep:

```bash
python -m aigol.cli.aigol_cli conversation
```

as the human-facing entry point, but add explicit action prompts only after replay-backed governance evidence exists.

Conversation should suggest or route to governed actions. It should not silently approve, execute, dispatch, or self-apply.

## Final Recommendation

Promote AiGOL CLI from operational tool to primary interface only after workflow integration, approval management, learning inspection, bridge authorization, and unified replay reconstruction are implemented and certified.
