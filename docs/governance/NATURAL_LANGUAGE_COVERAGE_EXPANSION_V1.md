# NATURAL_LANGUAGE_COVERAGE_EXPANSION_V1

Status: Ready

Purpose: Analyze ACLI natural-language intent coverage and define deterministic classifier improvements for development and governance-artifact requests.

## 1. Scope

This artifact reviews the runtime classifiers involved in the operational ACLI path:

```text
stdin
-> aigol_cli.py
-> route_conversational_cli_intent()
-> conversational_cli_runtime.py
-> HIRR / workflow selection
```

Reviewed files:

- `aigol/runtime/human_intent_clarification_intake_runtime.py`
- `aigol/runtime/conversational_cli_runtime.py`
- `aigol/runtime/human_execution_intent_detection.py`

This is a coverage analysis and improvement plan. It does not redesign HIRR, create a new workflow, or loosen execution authority.

## 2. Current Phrase Inventory

### DEVELOPMENT_INTENT

Runtime:

```text
aigol/runtime/human_intent_clarification_intake_runtime.py
```

Current action terms:

```text
add
implement
create
build
```

Current subject pairs:

```text
replay + validation
replay + validator
worker + authorization
worker + auth
comparison + runtime
audit + export
```

Coverage behavior:

- `Add replay validation` matches.
- `Implement worker authorization` matches.
- `Create comparison runtime` matches.
- `Add audit export` matches.
- `Add governance artifact TEST_ACLI_BRIDGE_V1...` does not match.

### GOVERNANCE_ARTIFACT_CREATION

Runtime:

```text
aigol/runtime/conversational_cli_runtime.py
```

Current explicit phrases:

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

Coverage behavior:

- `Add a governance artifact ...` matches.
- `Add governance artifact ...` does not match because the exact phrase without article is missing.

### Human Execution Intent Detection

Runtime:

```text
aigol/runtime/human_execution_intent_detection.py
```

Current creation terms:

```text
create
new
add
build
make
```

Current generic artifact creation requirement:

```text
artifact + governed + creation term
```

Coverage behavior:

- `Create governed artifact ...` matches.
- `Add governance artifact ...` does not match because it uses `governance`, not `governed`.

## 3. Phrase-Based Matching Limitations

The current classifiers are deterministic but narrow.

Observed limitations:

- article sensitivity: `add a governance artifact` matches, `add governance artifact` misses;
- adjective sensitivity: `governed artifact` matches generic intent, `governance artifact` misses;
- subject-pair limitation: `DEVELOPMENT_INTENT` only recognizes a fixed small set of implementation subjects;
- no artifact-name extraction for direct artifact tokens such as `TEST_ACLI_BRIDGE_V1`;
- no deterministic synonym groups for governance artifact creation verbs;
- no fallback from explicit governance-artifact vocabulary to the certified governance artifact creation workflow before ambiguous clarification.

These are coverage gaps, not wiring failures.

## 4. Missed Intent Examples

The following should be recognized deterministically:

```text
Add governance artifact TEST_ACLI_BRIDGE_V1 documenting that ACLI execution bridge was successfully tested.
Add governance artifact for replay validation.
Create artifact TEST_ACLI_BRIDGE_V1 under governance.
Write governance artifact TEST_ACLI_BRIDGE_V1.
Draft governance artifact TEST_ACLI_BRIDGE_V1.
Prepare governance artifact TEST_ACLI_BRIDGE_V1.
Define governance artifact TEST_ACLI_BRIDGE_V1.
Add certification artifact TEST_ACLI_BRIDGE_V1.
Create governance doc TEST_ACLI_BRIDGE_V1.
Add governed development artifact TEST_ACLI_BRIDGE_V1.
```

The following should remain clarification-first or fail-closed:

```text
Make the platform better.
Add something useful.
Run everything.
Execute the workflow.
Change the constitution automatically.
Create hidden governance mutation.
```

## 5. Proposed Classifier Improvements

### A. Normalize Deterministic Verb Groups

Introduce shared deterministic verb groups:

```text
creation_verbs = create, add, define, draft, prepare, write, generate
implementation_verbs = add, implement, create, build, update, extend
execution_verbs = run, execute, start, trigger
```

These verbs should remain explicit lists. No probabilistic interpretation is required.

### B. Normalize Governance Artifact Subject Groups

Recognize governance artifact requests when a prompt contains:

```text
creation verb
+
governance/governed/certification
+
artifact/doc/document/markdown/specification
```

Optional artifact identifiers such as `TEST_ACLI_BRIDGE_V1` should increase confidence but must not grant execution authority.

### C. Expand DEVELOPMENT_INTENT Subjects Conservatively

Add deterministic subjects for certified development workflow routing:

```text
governance artifact
certification artifact
runtime wiring
execution bridge
validation runner
replay evidence
approval capture
proposal generation
repository mutation
```

Routing should still stop at proposal generation and require explicit approval before mutation.

### D. Preserve Workflow Specificity

Governance artifact requests should have an explicit routing policy:

```text
governance artifact only
-> GOVERNANCE_ARTIFACT_CREATION

governance artifact + repository/runtime change
-> GOVERNED_DEVELOPMENT_WORKFLOW

ambiguous artifact request
-> HUMAN_INTENT_CLARIFICATION_INTAKE
```

This preserves deterministic routing while avoiding accidental broad execution.

### E. Keep Unknowns Clarification-First

If the classifier lacks:

- clear creation verb;
- clear artifact/development subject;
- clear target kind;
- safe mutation scope;

then it should continue routing to clarification or fail closed.

## 6. Fail-Closed Preservation

The proposed expansion does not grant execution authority.

Preserved invariants:

- classifier output is routing only;
- provider output remains non-authoritative;
- worker execution is not invoked during routing;
- proposal generation is not approval;
- mutation requires explicit approval;
- validation allowlists remain unchanged;
- replay remains source of truth;
- ambiguous prompts remain clarification-first.

## 7. Regression Test Plan

Add routing tests for:

```text
Add governance artifact TEST_ACLI_BRIDGE_V1 documenting that ACLI execution bridge was successfully tested.
Add a governance artifact TEST_ACLI_BRIDGE_V1.
Create governance artifact TEST_ACLI_BRIDGE_V1.
Define governance artifact TEST_ACLI_BRIDGE_V1.
Write governance artifact TEST_ACLI_BRIDGE_V1.
Prepare certification artifact TEST_ACLI_BRIDGE_V1.
Add replay evidence validation.
Implement approval capture.
Add repository mutation validation.
```

Expected assertions:

- no provider invoked during routing;
- no worker invoked during routing;
- no execution requested during routing;
- approval bypass is false;
- governance and replay are not mutated by routing;
- governance-artifact-only prompts route to `GOVERNANCE_ARTIFACT_CREATION`;
- governed development prompts route to `GOVERNED_DEVELOPMENT_WORKFLOW`;
- unclear prompts route to `HUMAN_INTENT_CLARIFICATION_INTAKE`.

Add bridge tests for:

```text
Add governance artifact TEST_ACLI_BRIDGE_V1 documenting that ACLI execution bridge was successfully tested.
APPROVE
```

Expected assertions:

- proposal generated;
- explicit approval captured;
- mutation occurs only after approval;
- validation runs;
- replay reconstructs;
- rejection does not mutate;
- missing approval does not mutate.

## 8. Implementation Boundaries

Allowed changes:

- add deterministic phrase variants;
- add shared helper predicates for action/subject groups;
- add regression tests;
- reorder only where required to route explicit certified workflow requests before ambiguous fallback.

Forbidden changes:

- no probabilistic classifier;
- no LLM-based routing authority;
- no automatic approval;
- no worker invocation during HIRR;
- no new workflow family;
- no validation allowlist expansion unless separately certified.

## 9. Readiness Assessment

The runtime wiring is sufficient.

The execution bridge is reachable.

The remaining issue is deterministic natural-language coverage for certified development and governance-artifact intents.

Classification:

```text
COVERAGE_GAP
```

## 10. Final Verdict

```text
NATURAL_LANGUAGE_COVERAGE_READY
```
