# ACLI Operator Guide Routing Audit V1

Status: COMPLETE

Verdict: ACLI_OPERATOR_GUIDE_ROUTING_AUDIT_COMPLETE

## 1. Objective

This audit determines why the prompt:

```text
Create governance artifact ACLI_OPERATOR_GUIDE_V1 explaining ACLI approval, replay, validation, and execution behavior for a non-technical operator.
```

was reported to route to:

```text
NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
-> OCS_LLM_COGNITION
```

instead of:

```text
GOVERNED_DEVELOPMENT_WORKFLOW
```

The audit reviews governance artifact routing, native development milestone routing, development intent routing, workflow precedence, and whether operator-guide terminology changes the selected workflow.

## 2. Exact Prompt Reproduction

The exact prompt was executed through the current conversational router.

Observed current routing result:

```text
routing_status: WORKFLOW_SELECTED
workflow_id: GOVERNED_DEVELOPMENT_WORKFLOW
operator_summary: Select the governed development orchestration workflow without mutation or approval bypass.
matched_terms: ['create', 'governance', 'artifact', 'governed-development']
confidence: HIGH
provider_invoked: False
worker_invoked: False
```

The exact prompt was also executed through the interactive ACLI entrypoint in a fresh temporary workspace.

Observed current interactive result:

```text
routing_visibility_workflow_id: GOVERNED_DEVELOPMENT_WORKFLOW
conversational_workflow_id: GOVERNED_DEVELOPMENT_WORKFLOW
response_status: APPROVAL_REQUIRED
worker_invoked: False
repository_mutation_performed: False
rendered_contains_native: False
rendered_contains_ocs: False
```

The reported `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION -> OCS_LLM_COGNITION` route is not reproducible for the exact prompt through the current fresh router or fresh interactive ACLI entrypoint.

## 3. Current Runtime Call Path

For a fresh ACLI prompt, the current runtime path is:

```text
stdin
-> aigol/cli/aigol_cli.py
-> run_interactive_conversation()
-> route_conversational_cli_intent()
-> aigol/runtime/conversational_cli_runtime.py
-> _classify_workflow()
-> _is_governance_artifact_creation_prompt()
-> GOVERNED_DEVELOPMENT_WORKFLOW
```

The relevant routing code is:

```text
aigol/runtime/conversational_cli_runtime.py:557
if _is_governance_artifact_creation_prompt(normalized):
    return _analysis(
        GOVERNED_DEVELOPMENT_WORKFLOW,
        "HIGH",
        ["create", "governance", "artifact", "governed-development"],
    )
```

This means explicit governance artifact creation requests are normalized into the governed development lifecycle before native development context routing is considered.

## 4. Exact Matched Rule

The exact prompt matches `_is_governance_artifact_creation_prompt()`.

The explicit phrase inventory includes:

```text
create a governance artifact
create the governance artifact
create governance artifact
define a governance artifact
define the governance artifact
define governance artifact
add a governance artifact
prepare a governance artifact
create a governed artifact
create the governed artifact
create governed artifact
create a certification artifact
create a governance workflow artifact
create a governance analysis artifact
```

The prompt contains:

```text
Create governance artifact
```

The prompt also satisfies the generic governance artifact pattern:

```text
creation verb + governance subject + artifact term
```

where:

```text
creation verb: Create
governance subject: governance
artifact term: artifact
```

The exact matched workflow is therefore:

```text
GOVERNED_DEVELOPMENT_WORKFLOW
```

## 5. Workflow Precedence

The relevant current workflow selection order is:

```text
early domain and worker checks
-> HIRR clarification checks
-> proposal runtime checks
-> governance artifact creation check
-> governed repository mutation check
-> explicit governed development workflow check
-> development intent classification
-> native development intent routing
-> later native context and OCS fallback checks
```

The governance artifact creation check occurs before:

```text
classify_development_intent_for_governed_routing()
is_conversation_native_development_intent()
_is_task_completion_native_development_prompt()
is_plain_native_development_prompt()
_is_native_development_context_prompt()
_is_ocs_llm_cognition_prompt()
```

Therefore, the exact prompt should not reach native development or OCS cognition routing when processed as a fresh prompt.

## 6. Competing Rules

### 6.1 Development Intent Routing

The prompt includes development-adjacent terms:

```text
approval
replay
validation
execution
```

Those terms may be relevant to development intent classification, but the development intent classifier is evaluated after the explicit governance artifact matcher.

If reached, development intent classification would still be expected to select:

```text
GOVERNED_DEVELOPMENT_WORKFLOW
```

It is not a competing path to `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION` for this prompt.

### 6.2 Native Development Milestone Routing

Native development and milestone routing can be appropriate for prompts about integrating or summarizing existing development work.

The operator guide prompt contains words that may resemble native development context:

```text
approval
replay
validation
execution
operator
behavior
```

However, the phrase:

```text
Create governance artifact ACLI_OPERATOR_GUIDE_V1
```

is more specific and is evaluated earlier.

The native development context rule is therefore a lower-precedence competing rule, not the selected rule in the current fresh runtime.

### 6.3 OCS LLM Cognition Routing

OCS cognition routing is a cognition workflow selection. It does not authorize repository mutation and should not be selected for an explicit governance artifact creation request in a fresh routing pass.

In the current runtime, the exact prompt does not route to OCS cognition.

## 7. Operator Guide Terminology Impact

The phrase `operator guide` does not defeat governance artifact routing.

The potentially confusing terms are:

```text
approval
replay
validation
execution
non-technical operator
```

These terms describe the intended content of the artifact. They do not change the operator's requested action:

```text
Create governance artifact ACLI_OPERATOR_GUIDE_V1
```

The requested action remains governed repository artifact creation and should enter:

```text
GOVERNED_DEVELOPMENT_WORKFLOW
```

## 8. Mismatch Analysis

### 8.1 Certified Expected Flow

```text
Human prompt
-> HIRR / ACLI routing
-> GOVERNED_DEVELOPMENT_WORKFLOW
-> proposal
-> approval
-> execution
-> validation
-> replay
```

### 8.2 Current Reproducible Flow

```text
Human prompt
-> route_conversational_cli_intent()
-> _classify_workflow()
-> _is_governance_artifact_creation_prompt()
-> GOVERNED_DEVELOPMENT_WORKFLOW
-> proposal
-> approval required
```

Current reproducible behavior matches the expected governed development route.

### 8.3 Reported Flow

```text
Human prompt
-> NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
-> OCS_LLM_COGNITION
```

This reported flow does not match the current fresh routing path.

Likely causes are:

- a stale interactive process using an older routing implementation;
- a stateful continuation already active in the ACLI session;
- a native-context continuation consuming the prompt before fresh workflow routing;
- displayed routing visibility from a prior turn being mistaken for the current turn;
- an alternate entrypoint or wrapper not using the current `route_conversational_cli_intent()` path.

The audit did not find evidence that the current fresh router selects `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION` for the exact prompt.

## 9. Expected Workflow

The expected workflow for the exact prompt is:

```text
GOVERNED_DEVELOPMENT_WORKFLOW
```

Rationale:

- the prompt explicitly requests governance artifact creation;
- the requested artifact has a deterministic governance artifact identifier;
- the resulting repository mutation requires proposal, approval, validation, and replay;
- the governed development lifecycle is the complete operator-facing ACLI path for this class of request.

## 10. Recommended Routing Correction

No routing correction is required for the current fresh router.

Recommended hardening actions:

1. Add an exact regression test for:

```text
Create governance artifact ACLI_OPERATOR_GUIDE_V1 explaining ACLI approval, replay, validation, and execution behavior for a non-technical operator.
```

2. Ensure explicit governance artifact prompts take precedence over stateful native-context continuations unless the operator is clearly answering an active native-context clarification.

3. Add diagnostic output that distinguishes:

```text
fresh route
```

from:

```text
stateful continuation route
```

4. Preserve current normalization of standard operator governance artifact requests into:

```text
GOVERNED_DEVELOPMENT_WORKFLOW
```

5. Preserve `GOVERNANCE_ARTIFACT_CREATION` as an internal component workflow rather than an incomplete operator-facing conversational route.

## 11. Validation

Validation performed:

```text
Exact prompt reproduction through route_conversational_cli_intent(): PASS
Exact prompt reproduction through interactive ACLI entrypoint: PASS
```

Expected additional validation:

```text
python -m pytest tests/test_conversational_cli_runtime_v1.py -q
git diff --check
```

Governance artifact regression coverage currently includes the related `ACLI_USAGE_GUIDELINES_V1` prompt and should be extended with the exact `ACLI_OPERATOR_GUIDE_V1` prompt in a follow-up implementation change.

## 12. Final Verdict

```text
ACLI_OPERATOR_GUIDE_ROUTING_AUDIT_COMPLETE
```

The current ACLI runtime routes the exact operator guide governance artifact prompt to `GOVERNED_DEVELOPMENT_WORKFLOW` in fresh routing and fresh interactive execution. The reported native-context and OCS cognition route is not reproducible in the current routing path and is most likely caused by stale runtime state, stateful continuation precedence, or an alternate entrypoint display path.
