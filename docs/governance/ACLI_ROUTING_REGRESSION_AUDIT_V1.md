# ACLI Routing Regression Audit V1

Status: COMPLETE

Verdict: ACLI_ROUTING_REGRESSION_AUDIT_COMPLETE

## 1. Objective

This audit determines why the prompt:

```text
Create governance artifact ACLI_USAGE_GUIDELINES_V1 documenting recommended operator practices for using ACLI as the primary development interface.
```

was reported to previously route to:

```text
GOVERNED_DEVELOPMENT_WORKFLOW
```

but later appeared to route to:

```text
NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
-> OCS_LLM_COGNITION
```

The audit reviews routing precedence, workflow selection order, governance artifact routing rules, development intent routing rules, recent routing-affecting changes, and whether proposal fidelity implementation changed routing behavior.

## 2. Audit Method

The audit inspected the current ACLI runtime implementation and executed the audited prompt through the shared conversational router.

The direct routing result in the current runtime is:

```text
routing_status: WORKFLOW_SELECTED
workflow_id: GOVERNED_DEVELOPMENT_WORKFLOW
operator_summary: Select the governed development orchestration workflow without mutation or approval bypass.
matched_terms: ['create', 'governance', 'artifact', 'governed-development']
```

This means the reported regression is not reproducible through the current fresh routing path.

## 3. Current Routing Decision Path

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

The governing code path is:

- `aigol/cli/aigol_cli.py:3128-3137`: calls `route_conversational_cli_intent()` when no stateful pre-routing gate is active.
- `aigol/runtime/conversational_cli_runtime.py:557-562`: routes governance artifact creation prompts to `GOVERNED_DEVELOPMENT_WORKFLOW`.
- `aigol/runtime/conversational_cli_runtime.py:906-930`: defines deterministic governance artifact creation matching.

## 4. Workflow Selection Order

The relevant current workflow selection order inside `_classify_workflow()` is:

```text
domain and worker entry checks
-> early HIRR clarification checks
-> proposal runtime checks
-> governance artifact creation check
-> governed repository mutation check
-> explicit governed development workflow check
-> development intent classification
-> native development intent routing
```

The governance artifact creation branch is evaluated before native development intent routing:

```text
_is_governance_artifact_creation_prompt()
-> GOVERNED_DEVELOPMENT_WORKFLOW

is_conversation_native_development_intent()
-> NATIVE_DEVELOPMENT_INTENT_ROUTING
```

Therefore, in the current router, the audited prompt should not fall through to native development routing when evaluated as a fresh prompt.

## 5. Governance Artifact Routing Rules

The audited prompt matches governance artifact routing for two independent reasons:

1. It contains the explicit phrase:

```text
Create governance artifact
```

2. It also satisfies the generic deterministic pattern:

```text
creation verb + governance subject + artifact kind
```

The current governance artifact phrase list includes:

```text
create governance artifact
add a governance artifact
prepare a governance artifact
create governed artifact
create certification artifact
create governance workflow artifact
create governance analysis artifact
```

The generic matcher includes:

```text
creation_verbs: create, add, define, draft, prepare, write, generate
governance_subjects: governance, governed, certification
artifact_terms: artifact, doc, document, markdown, specification
```

## 6. Development Intent Routing Rules

The current development intent routing is layered after explicit governance artifact routing.

If a prompt does not match governance artifact creation, the router may still select `GOVERNED_DEVELOPMENT_WORKFLOW` through:

```text
classify_development_intent_for_governed_routing()
```

Only after that does native development intent routing become eligible:

```text
is_conversation_native_development_intent()
```

This ordering preserves deterministic governed development routing for explicit repository-development prompts while keeping native context integration as a later fallback path.

## 7. Current Regression Test Coverage

Current tests already assert the expected route for the audited prompt:

- `tests/test_conversational_cli_runtime_v1.py`: verifies the audited `ACLI_USAGE_GUIDELINES_V1` governance artifact prompt routes to `GOVERNED_DEVELOPMENT_WORKFLOW`.
- `tests/test_acli_governed_development_execution_bridge_v1.py`: verifies the same prompt reaches the governed development bridge, displays the requested artifact name, produces the target path `docs/governance/ACLI_USAGE_GUIDELINES_V1.md`, and does not show the obsolete unsupported governance artifact workflow error.

The current test surface also covers related governance artifact phrasing:

```text
Add governance artifact TEST_ACLI_BRIDGE_V1 ...
Write governance artifact TEST_ACLI_BRIDGE_V1.
Draft governance artifact TEST_ACLI_BRIDGE_V1.
Prepare certification artifact TEST_ACLI_BRIDGE_V1.
Create governance doc TEST_ACLI_BRIDGE_V1.
```

## 8. Proposal Fidelity Impact

The proposal fidelity implementation did not change routing behavior.

The most recent proposal fidelity commit changed:

```text
aigol/runtime/acli_governed_development_execution_bridge.py
docs/governance/ACLI_PROPOSAL_CONTENT_FIDELITY_IMPLEMENTATION_V1.md
tests/test_acli_governed_development_execution_bridge_v1.py
```

It did not modify:

```text
aigol/runtime/conversational_cli_runtime.py
aigol/runtime/human_execution_intent_detection.py
aigol/cli/aigol_cli.py
```

The fidelity implementation runs after workflow selection. It affects proposal naming, target path generation, preview content, collision handling, and replayed proposal evidence. It does not select `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION`.

## 9. Mismatch Analysis

### Certified Expected Behavior

```text
Human prompt
-> HIRR / conversational routing
-> GOVERNED_DEVELOPMENT_WORKFLOW
-> proposal
-> approval
-> execution
-> validation
-> replay
```

### Current Fresh Runtime Behavior

```text
Human prompt
-> route_conversational_cli_intent()
-> _classify_workflow()
-> _is_governance_artifact_creation_prompt()
-> GOVERNED_DEVELOPMENT_WORKFLOW
```

Current fresh runtime behavior matches the certified expectation.

### Reported Operational Behavior

```text
Human prompt
-> NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
-> OCS_LLM_COGNITION
```

This behavior does not match the current fresh routing path.

## 10. Likely Regression Sources

Because the current fresh router selects `GOVERNED_DEVELOPMENT_WORKFLOW`, the reported behavior most likely came from one of the following operational conditions.

### 10.1 Stateful Native Context Continuation

`aigol/cli/aigol_cli.py:3108-3126` can activate a stateful pre-routing gate when pending state exists. If `pending_post_entry_continuation` is active and the prompt matches the continuation clarification pattern, fresh routing is skipped.

The continuation branch at `aigol/cli/aigol_cli.py:3203-3225` resumes `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION`.

This is the strongest current-code explanation for seeing a native context path despite a governance artifact prompt.

### 10.2 Existing Native Context Workflow State

If the authoritative workflow has already been set to `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION`, `aigol/cli/aigol_cli.py:5189-5258` runs the native context integration path and may request post-entry continuation.

In that state, operator-facing output can legitimately reference:

```text
NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
OCS_LLM_COGNITION
```

even though a fresh route for the same text would select governed development.

### 10.3 Stale Runtime Or Session

The repository currently contains the governance artifact unification and proposal fidelity changes. If the observed session used an older process, stale installed package, stale terminal process, or previous session state, it could have displayed older routing behavior.

### 10.4 Routing Visibility Versus Authoritative Route Confusion

The interactive CLI records routing visibility separately from universal intake and workflow execution. If a stateful turn bypasses fresh routing, the visible routing summary may describe the active stateful workflow rather than the fresh prompt's standalone route.

This is an operator-experience risk, not evidence that the shared router currently misclassifies the audited prompt.

## 11. Current ACLI Runtime Flow

For the audited prompt in a clean session:

```text
operator input
-> run_interactive_conversation()
-> stateful_pre_routing_gate: false
-> route_conversational_cli_intent()
-> _classify_workflow()
-> _is_governance_artifact_creation_prompt(): true
-> workflow_id: GOVERNED_DEVELOPMENT_WORKFLOW
-> governed development bridge
-> proposal visible to operator
-> approval required before mutation
```

## 12. Expected ACLI Runtime Flow

The expected runtime flow remains:

```text
operator input
-> HIRR / routing
-> DEVELOPMENT_INTENT or governance artifact creation recognition
-> GOVERNED_DEVELOPMENT_WORKFLOW
-> proposal generation
-> human-friendly explanation
-> explicit human approval
-> repository mutation through governed worker path
-> validation
-> replay persistence
```

## 13. Required Wiring Changes

No routing wiring change is required for the current fresh prompt path.

Recommended targeted hardening:

1. Preserve the existing regression tests for the audited prompt.
2. Add an explicit operational regression test, if absent in the desired test layer, that starts from the real interactive ACLI entrypoint and asserts the first turn selects `GOVERNED_DEVELOPMENT_WORKFLOW`.
3. Add a diagnostic distinction between:

```text
fresh_routing_decision
stateful_continuation_decision
```

so operator-facing routing output cannot be mistaken for a fresh classification result.

4. If the reported issue recurs in a stateful native context session, add a narrow pre-routing escape hatch that lets explicit governance artifact prompts start a new governed development route unless the operator is clearly answering a pending native-context clarification.

These are wiring-hardening recommendations. They are not new architecture, new workflow design, or governance redesign.

## 14. Final Finding

The current ACLI runtime does not reproduce the reported regression for the audited prompt in a fresh route.

The prompt currently routes to:

```text
GOVERNED_DEVELOPMENT_WORKFLOW
```

The proposal fidelity implementation did not change routing behavior.

The most plausible source of the reported native context route is stateful interactive session behavior, stale runtime state, or operator-facing routing visibility reflecting an active native context continuation rather than the fresh standalone route.

Final verdict:

```text
ACLI_ROUTING_REGRESSION_AUDIT_COMPLETE
```
