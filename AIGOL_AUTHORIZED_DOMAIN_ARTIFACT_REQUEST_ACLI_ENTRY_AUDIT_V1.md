# AIGOL_AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_ACLI_ENTRY_AUDIT_V1

## Status

Audit-only certification milestone.

No runtime, routing, worker, authorization, execution, repair, retry, or architecture changes were implemented.

## Goal

Determine why ACLI cannot continue after:

```text
WORKER_BINDING_APPROVED
```

even though the handoff review reports:

```text
Next Certified Stage: AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW
```

## Observed Operator Prompts

Prompts attempted:

```text
Approve FreshDomain for domain artifact creation.
Authorize FreshDomain domain artifact request.
```

Observed route:

```text
DEFAULT_PROVIDER_ASSISTED_CONVERSATION
```

## Located Stage

`AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW` is emitted by:

```text
aigol/runtime/clarified_domain_intent_handoff_review_runtime.py
```

It is emitted when:

```text
review_decision = WORKER_BINDING_APPROVED
```

The stage is consumed by the domain handoff review approval-entry runtime:

```text
aigol/runtime/domain_handoff_review_approval_binding_runtime.py
```

That runtime expects an operator approval prompt and binds it to the latest unbound matching reviewed domain handoff review.

## Expected Intent

The currently implemented expected intent is not a general authorization intent.

It is:

```text
DOMAIN_HANDOFF_REVIEW_APPROVAL_AND_BINDING_ENTRY
```

The supported prompt forms are exactly:

```text
Approve FreshDomain for domain artifact creation.
Approve reviewed FreshDomain workflow.
Continue FreshDomain to authorization.
```

The attempted prompt:

```text
Authorize FreshDomain domain artifact request.
```

is not currently recognized by the implemented detector.

## ACLI Routing Findings

There are two different routing surfaces:

1. The canonical conversational router:

```text
aigol/runtime/conversational_cli_runtime.py
```

2. The interactive conversation stateful pre-routing gate:

```text
aigol/cli/aigol_cli.py
```

The canonical conversational router does not include a workflow mapping for:

```text
AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW
DOMAIN_HANDOFF_REVIEW_APPROVAL_AND_BINDING_ENTRY
Authorize FreshDomain domain artifact request.
Approve FreshDomain for domain artifact creation.
```

Direct routing through `route_conversational_cli_intent(...)` sends both attempted prompts to:

```text
DEFAULT_PROVIDER_ASSISTED_CONVERSATION
```

The interactive conversation loop does contain a stateful pre-routing gate for `detect_domain_approval_entry_intent(...)`. In the current source, that detector recognizes:

```text
Approve FreshDomain for domain artifact creation.
Approve reviewed FreshDomain workflow.
Continue FreshDomain to authorization.
```

It does not recognize:

```text
Authorize FreshDomain domain artifact request.
```

## Reachability Finding

`AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW` is partly operator-accessible in the current source, but only through the interactive conversation loop's stateful pre-routing gate.

It is not fully registered as a canonical conversational workflow.

Therefore, an ACLI path that uses canonical conversational routing, a stale installed CLI, or a non-interactive routing path will still route the prompt to:

```text
DEFAULT_PROVIDER_ASSISTED_CONVERSATION
```

## Binding Finding

The binding runtime exists and is capable of binding a supported prompt to a reviewed FreshDomain handoff review when:

- the prompt matches one of the narrow supported forms;
- the operator is in the interactive conversation path that checks the stateful pre-routing gate;
- a matching unbound `WORKER_BINDING_APPROVED` handoff review exists in the session.

If no matching reviewed domain handoff review exists, the current interactive path should fail closed with a missing review condition, not route through default conversation.

## Root Cause

The root cause is:

```text
AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW_IS_NOT_REGISTERED_AS_A_CANONICAL_ACLI_ROUTING_WORKFLOW
```

Secondary issue:

```text
AUTHORIZE_DOMAIN_ARTIFACT_REQUEST_PROMPT_NOT_SUPPORTED
```

The stage is replay-visible and partially interactive, but not uniformly operator-accessible across ACLI routing surfaces.

## Certification Scope

This audit certifies:

- stage location;
- expected operator intent;
- expected supported prompts;
- canonical router behavior;
- interactive pre-routing behavior;
- reachability status;
- next blocking component.

This audit does not certify:

- new routing behavior;
- new prompt support;
- runtime changes;
- worker request creation;
- execution authorization;
- worker invocation;
- execution;
- repair;
- retry.

## Final Outputs

```text
AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_ACLI_ENTRY_EXISTS = PARTIAL_INTERACTIVE_PRE_ROUTING_ONLY
EXPECTED_OPERATOR_PROMPT = Approve FreshDomain for domain artifact creation. | Approve reviewed FreshDomain workflow. | Continue FreshDomain to authorization.
ACLI_ROUTING_EXISTS = PARTIAL_STATEFUL_INTERACTIVE_GATE_ONLY
ACLI_ROUTING_WORKING = FALSE_FOR_CANONICAL_ROUTER_AND_AUTHORIZE_PROMPT
NEXT_BLOCKING_COMPONENT = CANONICAL_ACLI_ROUTING_ENTRY_FOR_AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW
READY_FOR_REAL_AUTHORIZATION_ENTRY_ACCEPTANCE = FALSE_UNTIL_CANONICAL_ACLI_ENTRY_IS_REGISTERED_AND_ACCEPTED
```
