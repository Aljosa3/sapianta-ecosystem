# AIGOL_DEVELOPMENT_ENTRYPOINT_DISCOVERY_AUDIT_V1

## Objective

Determine whether ACLI currently routes development requests to the correct canonical development entrypoints.

This is an audit only. No ACLI, routing, PPP, governance, replay, provider, authorization, execution summary, or worker lifecycle code was modified.

## Scope

The audit inspected:

- `aigol/runtime/conversational_cli_runtime.py`
- `aigol/cli/aigol_cli.py`
- certified runtime tests for conversational routing, native development, domain lifecycle, capability lifecycle, and execution continuation
- Product 1 governance artifacts under `governance/`

The term "development entrypoint" is used here for source/runtime surfaces that initiate or continue governed development, proposal, domain, capability, implementation, or Product 1 planning work. General inspection/status workflows are excluded from the count.

## Entrypoint Inventory

Certified development entrypoints discovered:

| Entrypoint | Source | Certification / Evidence | ACLI Reachable? | Notes |
|---|---|---|---|---|
| `NATIVE_DEVELOPMENT_INTENT_ROUTING` | `conversation_native_development_intent_routing` | `AIGOL_CONVERSATION_NATIVE_DEVELOPMENT_INTENT_ROUTING_CERTIFICATION.json` | YES | Registered workflow. Used for explicit native development intent and some domain creation prompts. |
| `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION` | `conversation_native_development_context_integration` | `AIGOL_CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION_CERTIFICATION.json` | YES | Registered workflow. Main currently certified freeform development entrypoint. |
| `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `unknown_domain_clarification_runtime` / `domain_proposal_governance_runtime` | `AIGOL_DOMAIN_PROPOSAL_GOVERNANCE_CERTIFICATION_V1.json` | YES, predicate-limited | Registered workflow. Creates a domain proposal only when `_is_plain_domain_proposal_prompt` matches; otherwise clarification only. |
| `AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW` | `domain_handoff_review_approval_binding_runtime` | covered by domain approval/bridge tests | YES | Registered continuation after reviewed domain proposal. |
| `DOMAIN_EXECUTION_READY_AUTHORIZATION_BRIDGE` | `domain_approval_entry_to_execution_ready_authorization_bridge_runtime` | covered by bridge tests | YES | Registered continuation to execution-ready packet. |
| `DOMAIN_EXECUTION_AUTHORIZATION` | `execution_authorization_runtime` | `AIGOL_EXECUTION_AUTHORIZATION_RUNTIME_CERTIFICATION.json` | YES | Registered continuation to authorization. |
| `DOMAIN_WORKER_REQUEST` | `worker_invocation_request_runtime` | worker request certifications/tests | YES | Registered continuation to worker request. |
| `DOMAIN_WORKER_ASSIGNMENT` | `worker_assignment_runtime` | worker assignment tests/certification | YES | Registered continuation after request. |
| `DOMAIN_WORKER_DISPATCH` | `worker_dispatch_runtime` | dispatch tests/certification | YES | Registered continuation after assignment. |
| `DOMAIN_WORKER_INVOCATION` | `worker_invocation_runtime` | invocation tests/certification | YES | Registered continuation after dispatch. |
| `DOMAIN_WORKER_EXECUTION` | `execution_runtime` | domain worker execution tests | YES | Registered continuation after invocation. |
| `DOMAIN_WORKER_RESULT_CAPTURE` | `worker_result_capture_runtime` | result capture tests/certification | YES | Registered continuation after execution. |
| `DOMAIN_WORKER_RESULT_VALIDATION` | `worker_result_validation_runtime` | result validation tests/certification | YES | Registered continuation after capture. |
| `DOMAIN_POST_EXECUTION_REPLAY_REVIEW` | `post_execution_replay_review_runtime` | post-execution replay tests/certification | YES | Registered continuation after validation. |
| `DOMAIN_GOVERNED_TERMINATION` | `governed_termination_runtime` | governed termination tests/certification | YES | Registered terminal continuation. |
| `OPERATOR_DECISION_SUPPORT` | `operator_decision_support_runtime` | `test_operator_decision_support_runtime_v1.py` | YES | Registered advisory/planning path for Product 1 evidence-presentation/roadmap decisions. |
| `OCS_LLM_COGNITION` | `ocs_llm_cognition_end_to_end_runtime` | OCS certifications/tests | YES | Registered cognition path, not a canonical Product 1 development entrypoint. |
| `DOMAIN_PROPOSAL_GOVERNANCE_RUNTIME` | `domain_proposal_governance_runtime` | `AIGOL_DOMAIN_PROPOSAL_GOVERNANCE_CERTIFICATION_V1.json` | INDIRECT | Invoked by `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` only for recognized plain domain proposal prompts. No direct ACLI workflow id. |
| `DOMAIN_LIFECYCLE_GOVERNANCE_RUNTIME` | `domain_lifecycle_governance_runtime` | `AIGOL_DOMAIN_LIFECYCLE_GOVERNANCE_CERTIFICATION_V1.json` | NO direct route found | Certified runtime exists, but no ACLI workflow id maps directly to lifecycle candidate/activation/retirement creation. |
| `CAPABILITY_LIFECYCLE_GOVERNANCE_RUNTIME` | `capability_lifecycle_governance_runtime` | `AIGOL_CAPABILITY_LIFECYCLE_GOVERNANCE_CERTIFICATION_V1.json` | NO direct route found | Certified runtime exists, but ACLI currently routes "Add a capability candidate..." to native development, not capability lifecycle governance. |
| `PROPOSAL_RUNTIME` | `proposal_runtime` | `PROPOSAL_RUNTIME_V1_CERTIFICATION.json` | NO direct route found | Certified proposal primitive, not exposed as ACLI conversational workflow. |
| `IMPROVEMENT_PROPOSAL_RUNTIME` | `improvement_proposal_runtime` | `IMPROVEMENT_PROPOSAL_RUNTIME_V1_CERTIFICATION.json` | NO direct route found | Certified improvement proposal primitive, not exposed as ACLI conversational workflow. |
| `DEVELOPMENT_CONTEXT_ASSEMBLY_RUNTIME` | `development_context_assembly_runtime` | `AIGOL_DEVELOPMENT_CONTEXT_ASSEMBLY_CERTIFICATION.json` | INDIRECT | Used inside `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION`, not an ACLI workflow id. |
| `DEVELOPMENT_PROPOSAL_CONTRACT_RUNTIME` | `development_proposal_contract_runtime` | `AIGOL_DEVELOPMENT_PROPOSAL_CONTRACT_RUNTIME_CERTIFICATION.json` | INDIRECT | Used inside PPP development path, not an ACLI workflow id. |
| `PROVIDER_PROPOSAL_PRODUCTION_RUNTIME` | `provider_proposal_production_runtime` | `AIGOL_PROVIDER_PROPOSAL_PRODUCTION_RUNTIME_CERTIFICATION.json` | INDIRECT | Reached through `continue ppp`/native development path. |
| `FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH` | `first_real_implementation_generation_epoch_runtime` | `AIGOL_FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH_CERTIFICATION.json` | NO conversational route found | CLI command exists outside conversational router; not selected by natural-language ACLI routing. |
| `IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST_RUNTIME` | `implementation_plan_to_execution_request_runtime` | `IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST_RUNTIME_V1_CERTIFICATION.json` | NO conversational route found | Certified bridge exists, but not an ACLI conversational workflow id. |
| `AI_DECISION_VALIDATOR_DOMAIN_FOUNDATION` | `AI_DECISION_VALIDATOR_DOMAIN_FOUNDATION_V1.md` | artifact status: `PRODUCT_1_FOUNDATION_READY = YES` | NO dedicated route | Canonical Product 1 domain artifact exists; no dedicated ACLI workflow id. |
| `AI_DECISION_VALIDATOR_CAPABILITY_MODEL` | `AI_DECISION_VALIDATOR_CAPABILITY_MODEL_V1.md` | artifact status: `PRODUCT_1_CAPABILITY_MODEL_READY = YES` | NO dedicated route | Canonical Product 1 capability model exists; no dedicated ACLI workflow id. |
| `AI_DECISION_VALIDATOR_CAPABILITY_LIFECYCLE` | `AI_DECISION_VALIDATOR_CAPABILITY_LIFECYCLE_V1.md` | artifact status: `PRODUCT_1_CAPABILITY_LIFECYCLE_READY = YES` | NO dedicated route | Canonical Product 1 capability lifecycle model exists; no dedicated ACLI workflow id. |

Count:

```text
CERTIFIED_DEVELOPMENT_ENTRYPOINTS_DISCOVERED = 30
```

## ACLI Routing Inventory

`workflow_registry()` currently exposes 26 conversational workflow ids:

```text
CREATE_DOMAIN_TRADING
CREATE_DOMAIN_MARKETING
CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
DOMAIN_ADAPTATION_REFERENCE
OPERATOR_DECISION_SUPPORT
SHOW_LATEST_REPLAY_CHAIN
REVIEW_LATEST_AUDIT
IMPROVE_PROVIDER_LAYER
SHOW_STATUS
SHOW_DASHBOARD
NATIVE_DEVELOPMENT_INTENT_ROUTING
NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
OCS_LLM_COGNITION
AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW
DOMAIN_EXECUTION_READY_AUTHORIZATION_BRIDGE
DOMAIN_EXECUTION_AUTHORIZATION
DOMAIN_WORKER_REQUEST
DOMAIN_WORKER_ASSIGNMENT
DOMAIN_WORKER_DISPATCH
DOMAIN_WORKER_INVOCATION
DOMAIN_WORKER_EXECUTION
DOMAIN_WORKER_RESULT_CAPTURE
DOMAIN_WORKER_RESULT_VALIDATION
DOMAIN_POST_EXECUTION_REPLAY_REVIEW
DOMAIN_GOVERNED_TERMINATION
DEFAULT_PROVIDER_ASSISTED_CONVERSATION
```

Development-relevant ACLI routes counted as reachable:

```text
CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
NATIVE_DEVELOPMENT_INTENT_ROUTING
NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
OCS_LLM_COGNITION
AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW
DOMAIN_EXECUTION_READY_AUTHORIZATION_BRIDGE
DOMAIN_EXECUTION_AUTHORIZATION
DOMAIN_WORKER_REQUEST
DOMAIN_WORKER_ASSIGNMENT
DOMAIN_WORKER_DISPATCH
DOMAIN_WORKER_INVOCATION
DOMAIN_WORKER_EXECUTION
DOMAIN_WORKER_RESULT_CAPTURE
DOMAIN_WORKER_RESULT_VALIDATION
DOMAIN_POST_EXECUTION_REPLAY_REVIEW
DOMAIN_GOVERNED_TERMINATION
OPERATOR_DECISION_SUPPORT
DOMAIN_PROPOSAL_GOVERNANCE_RUNTIME (indirect)
DEVELOPMENT_CONTEXT_ASSEMBLY_RUNTIME (indirect)
DEVELOPMENT_PROPOSAL_CONTRACT_RUNTIME (indirect)
PROVIDER_PROPOSAL_PRODUCTION_RUNTIME (indirect)
```

Count:

```text
ACLI_REACHABLE_ENTRYPOINTS = 21
UNREACHABLE_CERTIFIED_ENTRYPOINTS = 9
```

## Placeholder Entrypoint Inventory

Placeholder, historical, or generic entrypoints still present:

| Entrypoint | Runtime | In Use? | Evidence |
|---|---|---|---|
| `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | `prompt_to_conversation_integration` | YES | Final fallback in `_classify_workflow`; exact Product 1 decision-model prompt routes here. |
| `CREATE_DOMAIN_TRADING` | `conversation_native_development_intent_routing` | YES | Registered as a named domain route, but uses generic native development intent routing. |
| `CREATE_DOMAIN_MARKETING` | `conversation_native_development_intent_routing` | YES | Registered as a named domain route, but uses generic native development intent routing. |
| `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `unknown_domain_clarification_runtime` | YES | Generic compliance/unknown-domain path; also conditionally invokes domain proposal governance for recognized prompts. |
| `IMPROVE_PROVIDER_LAYER` | `provider_layer_review_guidance` | YES | Static guidance path for provider layer improvements, not a full development lifecycle entrypoint. |
| `REVIEW_LATEST_AUDIT` | `capability_audit_artifact_review` | YES | Static audit-review route, not a full development lifecycle entrypoint. |

## Product 1 Routing Analysis

Exact prompt tested:

```text
Define the decision model for Product 1 AI Decision Validator.
```

Actual route:

```text
workflow_id: DEFAULT_PROVIDER_ASSISTED_CONVERSATION
routing_status: WORKFLOW_SELECTED
existing_runtime: prompt_to_conversation_integration
confidence: LOW
matched_terms: provider, conversation, fallback
```

Expected canonical target:

```text
AI_DECISION_VALIDATOR_DOMAIN_FOUNDATION / AI_DECISION_VALIDATOR_CAPABILITY_MODEL
or NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION as the generic governed development path
```

The strongest existing Product 1 canonical artifacts are:

```text
AI_DECISION_VALIDATOR_DOMAIN_FOUNDATION_V1.md
AI_DECISION_VALIDATOR_CAPABILITY_MODEL_V1.md
AI_DECISION_VALIDATOR_CAPABILITY_LIFECYCLE_V1.md
```

Their statuses include:

```text
PRODUCT_1_FOUNDATION_READY = YES
PRODUCT_1_CAPABILITY_MODEL_READY = YES
PRODUCT_1_CAPABILITY_LIFECYCLE_READY = YES
```

However, none of these appears in `workflow_registry()` as a dedicated ACLI workflow id.

## Route Predicate Findings

The exact Product 1 prompt does not match current Product 1/development predicates:

- `_is_task_completion_product_foundation_prompt` requires Product 1 / AI Decision Validator plus one of `evidence`, `presentation`, `demo`, `eu ai act`, or `approach`.
- `_is_task_completion_domain_prompt` requires `domain` plus one of `proposal`, `foundation`, `demo preparation`, or `product 1` plus one of `create`, `prepare`, or `add`.
- `_is_task_completion_native_development_prompt` requires action terms such as `prepare`, `improve`, `identify`, `add`, or `create`, and a narrow development subject list.
- `_is_plain_domain_proposal_prompt` requires `domain` plus `create`, `need`, `want`, or `prepare`; `define` is not accepted.
- `_is_native_development_context_prompt` requires an `aigol_` or `v1` marker.

Therefore:

```text
Define the decision model for Product 1 AI Decision Validator.
```

falls through to:

```text
DEFAULT_PROVIDER_ASSISTED_CONVERSATION
```

## Prompt Trace Matrix

Observed routing from live source:

| Prompt | Actual Workflow | Runtime | Assessment |
|---|---|---|---|
| `Define the decision model for Product 1 AI Decision Validator.` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | `prompt_to_conversation_integration` | Mismatch |
| `Define the AI Decision Validator domain foundation for Product 1.` | `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | `prompt_to_conversation_integration` | Mismatch |
| `Create a supplier evaluation domain proposal for Product 1 demo preparation.` | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `unknown_domain_clarification_runtime` / domain proposal path | Expected by existing regression |
| `Add a capability candidate for document validation evidence extraction.` | `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION` | `conversation_native_development_context_integration` | Reachable, but generic |
| `What is the best approach for EU AI Act aligned AI Decision Validator evidence presentation?` | `OPERATOR_DECISION_SUPPORT` | `operator_decision_support_runtime` | Expected by existing regression |
| `Prepare a proposal for improving replay lineage validation visibility in ACLI.` | `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION` | `conversation_native_development_context_integration` | Expected by existing regression |

## Gap Analysis

1. Product 1 canonical artifacts exist, but Product 1 canonical conversational entrypoints do not.

   The Product 1 domain foundation, capability model, and capability lifecycle are present and marked ready. ACLI does not expose dedicated workflow ids for Product 1 domain/capability/decision-model work.

2. ACLI routes Product 1 by narrow phrase families.

   Product 1 evidence-presentation prompts route to `OPERATOR_DECISION_SUPPORT`. Product 1 domain proposal prompts route only if they include accepted proposal/create/prepare vocabulary. Product 1 decision-model prompts using `define` do not route to native development or domain/capability governance.

3. Capability lifecycle governance is certified but not reachable as a conversational development entrypoint.

   `CAPABILITY_LIFECYCLE_GOVERNANCE_RUNTIME` is certified. ACLI currently routes "Add a capability candidate..." to generic `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION`, not to capability lifecycle governance.

4. Domain lifecycle governance is certified but not directly reachable as a conversational development entrypoint.

   ACLI can enter domain proposal and post-approval lifecycle continuations, but the domain lifecycle governance candidate/activation runtime does not appear as a direct conversational workflow id.

5. Historical/generic placeholders remain active and absorb unmatched Product 1 development prompts.

   The fallback route is still `DEFAULT_PROVIDER_ASSISTED_CONVERSATION`. The exact Product 1 decision-model prompt reaches that fallback with LOW confidence.

## Root Cause

The current ACLI router is predicate-based and phrase-specific. It knows a set of certified workflows and several Product 1-adjacent prompt patterns, but it does not have a canonical Product 1 development entrypoint model. Product 1 domain/capability artifacts emerged as governance artifacts after earlier generic routing patterns, and ACLI has not been linked to those artifacts as first-class route targets.

## Highest-Leverage Repair

Introduce an explicit Product 1 development routing layer that maps Product 1 domain/capability/decision-model prompts to existing certified governance paths without changing PPP, governance, replay, authorization, or worker lifecycle semantics.

The likely minimal route target is:

```text
Product 1 domain/capability/decision-model prompt
-> NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
```

with a later, more canonical option:

```text
Product 1 domain/capability prompt
-> dedicated Product 1 domain/capability entrypoint
-> existing domain/capability governance runtimes
```

No repair is implemented in this audit.

## Final Fields

```text
CERTIFIED_DEVELOPMENT_ENTRYPOINTS_DISCOVERED = 30
ACLI_REACHABLE_ENTRYPOINTS = 21
UNREACHABLE_CERTIFIED_ENTRYPOINTS = 9
PLACEHOLDER_ENTRYPOINTS_PRESENT = YES
PLACEHOLDER_ENTRYPOINTS_IN_USE = YES
PRODUCT_1_CANONICAL_ENTRYPOINT_EXISTS = YES
PRODUCT_1_ENTRYPOINT_REACHABLE_FROM_ACLI = NO
ROUTING_MISMATCH_IDENTIFIED = YES
ROOT_CAUSE = ACLI predicate routing lacks a canonical Product 1 domain/capability/decision-model entrypoint and falls back to DEFAULT_PROVIDER_ASSISTED_CONVERSATION for unrecognized Product 1 development phrasing.
HIGHEST_LEVERAGE_REPAIR = Add explicit Product 1 development routing to existing certified native-development/domain/capability governance paths, preserving current governance and authorization boundaries.
ACLI_DEVELOPMENT_ENTRYPOINT_MODEL_UNDERSTOOD = YES
```
