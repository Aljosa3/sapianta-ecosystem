# AIGOL_ACLI_EXECUTION_PATH_CONTINUATION_ANALYSIS_V1

Status: continuation diagnosis.

Date: 2026-06-15

## Objective

Determine why ACLI reaches correct lifecycle entry points after the task-completion routing repair but does not continue into execution-request and worker lifecycle paths.

This analysis does not redesign ACLI, OCS, PPP, Worker Lifecycle, Replay, providers, or governance. It diagnoses continuation behavior after lifecycle entry selection.

## Context

Recent certified findings:

- `TASK_COMPLETION_IMPROVED = YES`
- `TASK_COMPLETION_RATE_AFTER = 100% lifecycle-entry selection`
- `WORKER_LIFECYCLE_REACHED = NO`
- `EXECUTION_REQUEST_CREATED = NO`
- `COPY_PASTE_REQUIRED = NO`

Routing ambiguity has been reduced. The remaining blocker is after lifecycle entry selection.

## Lifecycle Entry Inventory

Representative real-development prompt classes now route before generic provider fallback:

| Prompt class | Representative route | Lifecycle entry | Current behavior |
| --- | --- | --- | --- |
| governance-improvement prompt | `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION` | `conversation_native_development_context_integration` | assembles native context; stops unless post-context continuation condition is satisfied |
| replay-improvement prompt | `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION` | `conversation_native_development_context_integration` | assembles native context; no execution request by default |
| domain-improvement prompt | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `unknown_domain_clarification_runtime` or domain proposal path | clarification/proposal boundary only; does not self-authorize |
| product-foundation prompt | `OPERATOR_DECISION_SUPPORT` | `operator_decision_support_runtime` | recommendation only; no execution request |
| approved-domain continuation prompt | `AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW` | `domain_handoff_review_approval_binding_runtime` | approval-entry review; downstream authorization remains separate |
| provider-improvement prompt | `IMPROVE_PROVIDER_LAYER` | `provider_layer_review_guidance` | guidance/review route; explicitly non-executing |

The repaired route set successfully avoids generic provider-assisted conversation fallback. It does not imply automatic continuation across governance boundaries.

## Continuation Analysis

### Human Prompt -> Classification -> Lifecycle Entry -> Stopping Point

For native development prompts, the active path is:

```text
Human prompt
-> conversational routing
-> NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
-> native development task intake
-> development context assembly
-> stop unless post-context continuation predicate is true
```

The post-context continuation predicate requires:

- native context did not fail closed;
- `context_status = CONTEXT_ASSEMBLED`;
- provider necessity classification includes `PROVIDER_REQUIRED`;
- either ACLI `auto_continue` is enabled, or the prompt explicitly contains both `continue` and `ppp`.

When that predicate is false, the lifecycle entry has been reached and context has been assembled, but no PPP continuation, execution summary, human confirmation, authorization, execution request, or worker lifecycle artifact is created.

### Expected Next Artifact

The expected next artifact after successful native context assembly is:

```text
POST_CONTEXT_CONTINUATION_ARTIFACT_V1
```

That artifact is created by the existing post-context continuation runtime. It can reach PPP routing and implementation handoff evidence.

### Existing Continuation Logic

Existing logic is present:

```text
NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
-> continue_context_assembled_to_ppp_routing
-> conversation_ppp_routing_integration
-> implementation handoff visibility
-> governed implementation dry run
-> authorize_execution_ready
-> create_worker_invocation_request
-> worker lifecycle continuation
```

The continuation helper can produce:

- implementation handoff visibility;
- governed implementation dry run;
- execution authorization;
- worker invocation request;
- worker assignment;
- worker dispatch;
- worker invocation;
- execution candidate;
- external task package;
- result validation;
- replay certification.

The worker lifecycle is therefore reachable in code, but not reached during ordinary lifecycle-entry selection unless continuation conditions are explicitly satisfied.

### Missing Continuation Condition

The missing operational condition is not a worker runtime. It is a deterministic ACLI continuation decision after successful lifecycle entry selection.

Current lifecycle entry selection answers:

```text
Which certified lifecycle should receive this prompt?
```

It does not always answer:

```text
Should ACLI continue from this selected lifecycle entry into the next certified boundary now?
```

The consequence is a post-routing pause. This preserves governance, but depresses task completion.

### Authorization Dependency

Execution authorization is already implemented downstream of execution-ready evidence. It creates or validates execution summary and summary-bound human confirmation before authorization.

Authorization is not reached because the ordinary path stops before:

```text
POST_CONTEXT_CONTINUATION_ARTIFACT_V1
-> implementation handoff visibility
-> governed implementation dry run
```

Without an execution-ready replay reference, `authorize_execution_ready` cannot be invoked without weakening governance.

### Human Confirmation Dependency

Human confirmation exists as a summary-bound dependency of authorization. It is generated or validated inside the authorization boundary when an execution-ready replay reference exists.

For the failing ordinary ACLI adoption path, human confirmation is not the first blocker. It is downstream of the missing post-context continuation and execution-ready replay reference.

### Execution Summary Dependency

Execution summary support exists. The execution authorization runtime can create:

```text
EXECUTION_SUMMARY_ARTIFACT_V1
EXECUTION_SUMMARY_CONFIRMATION
EXECUTION_AUTHORIZATION_ARTIFACT_V1
```

The summary is not reached from ordinary repaired lifecycle selection because the path has not continued to an execution-ready artifact.

## Verification

Focused validation was run:

```bash
python -m pytest tests/test_conversational_cli_runtime_v1.py tests/test_context_assembled_to_ppp_routing_continuation_v1.py tests/test_execution_summary_enforcement_repair_v1.py tests/test_worker_invocation_request_runtime_v1.py
```

Result:

```text
106 passed
```

Validation evidence:

- conversational routing tests confirm the ten real development prompts route before generic provider fallback while preserving `provider_invoked = False`, `worker_invoked = False`, and `execution_requested = False`;
- post-context continuation tests confirm context-assembled prompts can reach PPP routing and implementation handoff evidence;
- execution summary enforcement tests confirm execution authorization generates execution summary and human confirmation before authorization;
- worker invocation request tests confirm authorized execution evidence can become `WORKER_INVOCATION_REQUEST_CREATED`;
- CLI acceptance tests confirm selected CLI flows can reach worker invocation request when the expected continuation/approval path is exercised.

## Can Lifecycle Entries Currently Produce Downstream Artifacts?

| Artifact | Reachable from existing code | Reached by ordinary repaired adoption prompt | Blocking stage |
| --- | --- | --- | --- |
| execution summary | yes | no | post-context continuation not entered |
| confirmation request | yes | no | post-context continuation not entered |
| authorization request/artifact | yes | no | execution-ready replay reference not produced |
| execution request / worker invocation request | yes | no | authorization not produced |
| worker lifecycle | yes | no | worker invocation request not produced |

## First Blocking Stage

The first blocking stage is:

```text
POST_LIFECYCLE_ENTRY_CONTINUATION_DECISION
```

More concretely:

```text
NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
-> CONTEXT_ASSEMBLED
-> no deterministic continuation into POST_CONTEXT_CONTINUATION_ARTIFACT_V1
```

## Root Cause

The root cause is missing deterministic continuation after lifecycle entry selection.

Routing now selects the correct certified lifecycle entry, but the selected entry is often a non-executing intake/context/review surface. Existing downstream runtimes require an explicit continuation condition before creating PPP handoff, execution-ready evidence, authorization, and worker request artifacts.

The present behavior is governance-preserving and fail-closed, but operationally incomplete for primary-interface task completion.

## Minimal Repair

Add a deterministic ACLI post-entry continuation decision for lifecycle entries that already have certified continuation paths.

Minimal repair shape:

```text
Lifecycle entry selected
-> lifecycle entry completes successfully
-> ACLI emits/records NEXT_CERTIFIED_CONTINUATION_AVAILABLE
-> if human prompt or session mode authorizes continuation, call existing continuation runtime
-> preserve execution summary, human confirmation, authorization, and worker lifecycle boundaries
```

For `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION`, the minimal concrete repair is:

```text
CONTEXT_ASSEMBLED + PROVIDER_REQUIRED
-> produce operator-visible continuation offer or deterministic continuation gate
-> continue_context_assembled_to_ppp_routing only after allowed continuation condition
```

This should reuse:

- `continue_context_assembled_to_ppp_routing`;
- `_continue_ppp_handoff_to_worker_request`;
- `authorize_execution_ready`;
- `create_worker_invocation_request`;
- existing worker lifecycle continuation helpers.

It should not add providers, governance layers, orchestration systems, or bypass authorization.

## Governance Impact

No governance weakening is recommended.

The continuation gap should be repaired by making the next certified boundary explicit and operator-visible, not by inferring authorization from route selection.

Required preserved boundaries:

- lifecycle selection is not authorization;
- context assembly is not execution readiness;
- PPP handoff is not execution authorization;
- execution summary and human confirmation remain before authorization;
- authorization remains before worker request;
- worker request remains before assignment, dispatch, invocation, and execution;
- replay remains append-only and reconstructable;
- missing or ambiguous continuation continues to fail closed.

## Final Fields

```text
LIFECYCLE_ENTRY_REACHED = YES
EXECUTION_SUMMARY_REACHED = NO
CONFIRMATION_REACHED = NO
AUTHORIZATION_REACHED = NO
EXECUTION_REQUEST_REACHED = NO
WORKER_LIFECYCLE_REACHED = NO
FIRST_BLOCKING_STAGE = POST_LIFECYCLE_ENTRY_CONTINUATION_DECISION
ROOT_CAUSE = missing deterministic continuation after successful lifecycle entry selection
MINIMAL_REPAIR = add a replay-visible ACLI post-entry continuation gate that invokes existing certified continuation runtimes only when continuation is explicitly allowed
CONTINUATION_PATH_UNDERSTOOD = YES
```
