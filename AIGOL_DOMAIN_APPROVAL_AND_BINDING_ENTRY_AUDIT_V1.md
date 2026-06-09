# AIGOL_DOMAIN_APPROVAL_AND_BINDING_ENTRY_AUDIT_V1

## Status

Audit completed.

No new runtime was implemented. No new worker was implemented. No repair runtime, retries, or architecture redesign were introduced.

## Goal

Determine how a clarified and reviewed domain is expected to enter the authorization and worker-request lifecycle.

Observed real ACLI path:

```text
Create Domain
-> Clarification
-> Reply
-> Resume
-> Handoff Review
-> WORKER_BINDING_APPROVED
-> AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW
```

Observed continuation attempt:

```text
Approve FreshDomain for domain artifact creation.
```

Actual route:

```text
DEFAULT_PROVIDER_ASSISTED_CONVERSATION
```

The request then fails closed through provider-assisted fallback behavior instead of entering a domain approval or binding workflow.

## Approval Entry Points Located

Approval-related entry points exist, but none currently bind FreshDomain handoff review into the execution lifecycle.

### Read-Only Approval Command Group

Located:

```text
aigol/cli/commands/approval.py
```

Commands:

```text
aigol approval list
aigol approval show
aigol approval pending
aigol approval approved
aigol approval rejected
aigol approval chain
```

This command group is read-only. It scans existing approval artifacts and does not create approval, authorization, worker request, dispatch, invocation, or execution.

Supported approval artifact types:

```text
PROPOSAL_APPROVAL_ARTIFACT_V1
IMPROVEMENT_APPROVAL_ARTIFACT_V1
```

It does not support:

```text
HANDOFF_REVIEW_DECISION_ARTIFACT_V1
DOMAIN_ARTIFACT_REQUEST_APPROVAL_ARTIFACT_V1
HUMAN_APPROVAL_BINDING_ARTIFACT_V1
```

### Generic Approval Engine

Located:

```text
aigol/runtime/approval/
```

Relevant files:

```text
approval_contract.py
approval_engine.py
approval_request.py
approval_result.py
approval_validator.py
```

This system can produce approval request/result semantics from routing contracts. It does not currently provide a FreshDomain ACLI entrypoint or a binding from `HANDOFF_REVIEW_DECISION_ARTIFACT_V1` to OCS handoff/readiness approval evidence.

### Proposal Approval Runtime

Located:

```text
aigol/runtime/proposal_approval_runtime.py
```

It consumes:

```text
PROPOSAL_RUNTIME_ARTIFACT_V1
```

It produces:

```text
PROPOSAL_APPROVAL_ARTIFACT_V1
```

It explicitly does not create execution request, worker request, provider invocation, or worker invocation.

This is not the FreshDomain approval path.

### Improvement Approval Runtime

Located:

```text
aigol/runtime/improvement_approval_runtime.py
```

It consumes improvement proposal and review artifacts.

It produces:

```text
IMPROVEMENT_APPROVAL_ARTIFACT_V1
```

This is not the FreshDomain approval path.

### Implementation Approval Resume

Located:

```text
aigol/runtime/implementation_approval_resume.py
```

This path is wired into ACLI stateful approval handling only when:

```text
pending_approval_required is not None
```

and the operator decision is:

```text
APPROVE
REJECT
REQUEST_MODIFICATION
```

FreshDomain handoff review does not currently create `pending_approval_required`, so this ACLI approval branch is not reachable for:

```text
Approve FreshDomain for domain artifact creation.
```

## Authorization Entry Points Located

Execution authorization entry point:

```text
aigol/runtime/execution_authorization_runtime.py
authorize_execution_ready(...)
```

Required input:

```text
execution_ready_replay_reference
```

Required replay terminal state:

```text
EXECUTION_READY_STATUS_ARTIFACT_V1
execution_status = EXECUTION_READY
```

FreshDomain does not currently have execution-ready replay, so it cannot directly enter authorization.

## Worker-Request Entry Points Located

Worker request entry point:

```text
aigol/runtime/worker_invocation_request_runtime.py
create_worker_invocation_request(...)
```

Required input:

```text
execution_authorization_replay_reference
```

Required replay terminal state:

```text
EXECUTION_AUTHORIZATION_ARTIFACT_V1
authorization_status = EXECUTION_AUTHORIZED
```

FreshDomain does not currently have execution authorization replay, so it cannot directly enter worker-request creation.

## Routing Analysis

The conversational router is located in:

```text
aigol/runtime/conversational_cli_runtime.py
```

The workflow registry contains no domain approval workflow and no handoff-review approval workflow.

Verified behavior for:

```text
Approve FreshDomain for domain artifact creation.
```

is:

```text
routing_status = WORKFLOW_SELECTED
workflow_id = DEFAULT_PROVIDER_ASSISTED_CONVERSATION
existing_runtime = prompt_to_conversation_integration
```

Reason:

- the prompt is not an active clarification reply;
- no `pending_approval_required` state exists;
- the prompt does not match OCS cognition routing;
- the prompt does not match known create-domain routing;
- the prompt does not match read-only approval command routing;
- the router has no certified domain approval predicate;
- fallback workflow is selected.

## Expected FreshDomain Path

The expected governed path is:

```text
FreshDomain handoff review
-> domain approval entry
-> approval binding to handoff review decision
-> OCS execution handoff or equivalent execution-intake candidate
-> execution readiness
-> execution authorization
-> worker invocation request
```

For the existing execution chain, the approval path must eventually provide readiness-compatible fields:

```text
approval_status = APPROVED
approval_reference = <non-empty human approval reference>
approval_hash = <non-empty approval hash>
approving_actor = <valid human/governance actor, not provider/LLM/OCS>
approved_at = <timestamp>
```

The approval must not broaden allowed outputs, weaken forbidden operations, bypass validation, select a worker outside review scope, dispatch, invoke, execute, repair, retry, or mutate replay.

## ACLI Continuation Capability

Current ACLI has no valid natural-language prompt capable of continuing FreshDomain from:

```text
WORKER_BINDING_APPROVED
```

to:

```text
approval binding
-> execution readiness
-> authorization
-> worker request
```

The existing stateful `APPROVE` branch is bound to pending implementation approval, not clarified domain handoff review.

The `aigol approval ...` command group is read-only and cannot create the missing approval.

Therefore ACLI cannot currently continue FreshDomain into authorization or worker-request creation.

## Missing Runtime

The exact missing runtime is:

```text
DOMAIN_HANDOFF_REVIEW_APPROVAL_AND_BINDING_ENTRY_RUNTIME
```

It must consume:

- `HANDOFF_REVIEW_DECISION_ARTIFACT_V1`;
- handoff review replay reference;
- clarified domain identity;
- worker binding decision;
- operator approval intent;
- approving actor;
- approval timestamp.

It must produce:

- replay-visible domain approval binding artifact;
- approval reference and approval hash usable by execution readiness;
- binding evidence preserving FreshDomain scope, allowed outputs, forbidden operations, validation requirements, and worker constraints;
- a next-stage packet or orchestration path into OCS handoff/readiness.

It must not create worker execution, repair, retries, autonomous approval, or architecture redesign.

## Recommendation

Recommended next milestone:

```text
AIGOL_DOMAIN_HANDOFF_REVIEW_APPROVAL_AND_BINDING_ENTRY_RUNTIME_V1
```

Scope:

1. Add certified ACLI routing for FreshDomain approval intent.
2. Bind the operator approval to the latest matching handoff review decision.
3. Emit a replay-visible approval binding artifact.
4. Preserve all handoff review constraints.
5. Stop before worker execution.

This milestone should precede worker request creation, because worker-request creation requires authorization replay, and authorization replay requires execution-ready replay with approval lineage.

## Final Outputs

```text
DOMAIN_APPROVAL_ENTRY_EXISTS = FALSE_FOR_FRESHDOMAIN_HANDOFF_REVIEW
DOMAIN_APPROVAL_ROUTING_EXISTS = FALSE
ACLI_CAN_CONTINUE_FRESHDOMAIN = FALSE
EXPECTED_APPROVAL_PATH_IDENTIFIED = TRUE
NEXT_BLOCKING_COMPONENT = DOMAIN_HANDOFF_REVIEW_APPROVAL_AND_BINDING_ENTRY_RUNTIME
RECOMMENDED_NEXT_MILESTONE = AIGOL_DOMAIN_HANDOFF_REVIEW_APPROVAL_AND_BINDING_ENTRY_RUNTIME_V1
```
