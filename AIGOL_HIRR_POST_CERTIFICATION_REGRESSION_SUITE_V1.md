# AIGOL_HIRR_POST_CERTIFICATION_REGRESSION_SUITE_V1

Status: proposed post-certification regression architecture.

Purpose: protect the `HUMAN_INTENT_RESOLUTION_READY = READY` certification from future regressions.

This artifact defines the regression suite structure, evidence model, CI strategy, and recertification triggers for HIRR after final certification.

No new runtime authority, provider invocation, worker invocation, governance mutation, dispatch, ELL runtime, or lifecycle engine is introduced by this suite.

## Certification-Critical Behaviors

The regression suite protects these certification-critical behaviors:

1. Clarification-first behavior.
2. Clarification continuity.
3. Workflow target refinement.
4. Advisory cognition routing.
5. ERR-backed cognition provider selection.
6. ERR-backed execution worker selection.
7. Replay-visible evidence.
8. Fail-closed behavior.

The protected final verdict is:

```text
HUMAN_INTENT_RESOLUTION_READY = READY
```

## Regression Architecture

The suite is a focused evidence gate over existing HIRR, OCS, ERR, and worker-assignment tests.

The suite does not create a new orchestration layer. It binds already-certified runtime surfaces into one named post-certification validation path:

```text
Human intent
-> HIRR clarification and continuity
-> workflow refinement
-> OCS cognition routing
-> ERR provider lookup
-> worker assignment ERR lookup
-> replay evidence reconstruction
-> fail-closed checks
```

The regression suite is successful only when every category passes.

Partial success must not preserve certification status.

## Regression Categories

### 1. Clarification-First Behavior

Protected behavior:

```text
unknown or underspecified human intent
-> CLARIFICATION_REQUIRED
-> no provider submission
-> no worker invocation
-> no execution request
```

Required evidence:

- ambiguous interactive prompt produces `CLARIFICATION_REQUIRED`;
- provider submission is not reached for that prompt;
- no provider-unavailable fallback replay branch is required for ambiguous intent;
- `failed_turns = 0` for clarification-required interactive turn.

Primary tests:

- `tests/test_conversational_cli_runtime_v1.py`
- `tests/test_conversation_provider_unavailable_clarification_fallback_v1.py`

### 2. Clarification Continuity

Protected behavior:

```text
clarification request
-> human clarification reply
-> original chain preserved
-> resolved continuation remains replay-visible
```

Required evidence:

- clarification state persists across turns;
- reply binds to the original chain;
- latest chain and current chain are consistent;
- invalid or mismatched chain state fails closed.

Primary tests:

- `tests/test_conversational_cli_runtime_v1.py`

### 3. Workflow Refinement

Protected behavior:

```text
clarified intent
-> workflow target recomputed
-> governed workflow selected
```

Required evidence:

- clarified advisory intent can refine into OCS cognition routing;
- clarified domain intent can refine into the expected governed workflow;
- refinement does not authorize, dispatch, invoke, or execute;
- unsupported refinement state fails closed.

Primary tests:

- `tests/test_conversational_cli_runtime_v1.py`
- `tests/test_universal_intake_layer_v1.py`

### 4. Advisory Cognition Routing

Protected behavior:

```text
advisory human intent
-> HIRR / Universal Intake
-> OCS_LLM_COGNITION
-> non-authoritative cognition path
```

Required evidence:

- advisory prompts route to OCS cognition;
- OCS cognition remains non-authoritative;
- no worker invocation is performed by advisory cognition;
- provider-unavailable cognition is classified downstream and fails closed before comparison.

Primary tests:

- `tests/test_conversational_cli_runtime_v1.py`
- `tests/test_universal_intake_layer_v1.py`
- `tests/test_ocs_llm_cognition_end_to_end_runtime_v1.py`

### 5. ERR-Backed Provider Selection

Protected behavior:

```text
OCS requests capability = reasoning
-> ERR resolves mock_provider
-> replay-visible selection evidence recorded
```

Required evidence:

- OCS does not hardcode provider identity for ERR-backed selection;
- `mock_provider` is resolved through capability lookup;
- inactive provider resources are excluded;
- missing provider capability fails closed;
- ERR does not invoke providers.

Primary tests:

- `tests/test_ocs_llm_cognition_end_to_end_runtime_v1.py`
- `tests/test_external_resource_registry_runtime_v0.py`

### 6. ERR-Backed Worker Selection

Protected behavior:

```text
worker assignment requests capability = file_write
-> ERR resolves mock_filesystem_worker
-> replay-visible selection evidence recorded
```

Required evidence:

- worker assignment does not hardcode worker identity for ERR-backed selection;
- `mock_filesystem_worker` is resolved through capability lookup;
- inactive worker resources are excluded;
- missing worker capability fails closed;
- ERR does not invoke workers;
- worker assignment compatibility checks remain outside ERR.

Primary tests:

- `tests/test_worker_assignment_runtime_v1.py`
- `tests/test_external_resource_registry_runtime_v0.py`

### 7. Replay Visibility

Protected behavior:

```text
selection and clarification evidence
-> immutable replay artifact
-> reconstruction verifies hashes and ordering
```

Required evidence:

- HIRR clarification evidence is replay-visible;
- workflow refinement evidence is replay-visible;
- OCS ERR selection evidence is replay-visible;
- worker ERR selection evidence is replay-visible;
- replay reconstruction detects corruption;
- ERR does not mutate replay history.

Primary tests:

- `tests/test_conversational_cli_runtime_v1.py`
- `tests/test_conversation_provider_unavailable_clarification_fallback_v1.py`
- `tests/test_ocs_llm_cognition_end_to_end_runtime_v1.py`
- `tests/test_external_resource_registry_runtime_v0.py`
- `tests/test_worker_assignment_runtime_v1.py`

### 8. Fail-Closed Behavior

Protected behavior:

```text
invalid, unavailable, unsupported, or corrupt state
-> FAILED_CLOSED
-> no silent fallback into execution
```

Required evidence:

- malformed clarification state fails closed;
- invalid HIRR continuation fails closed;
- OCS zero-provider availability fails closed before comparison;
- ERR missing capability fails closed;
- ERR inactive resources are excluded;
- invalid ERR schema fails closed;
- worker assignment cannot proceed through invalid ERR selection;
- corrupt replay reconstruction fails closed.

Primary tests:

- `tests/test_conversational_cli_runtime_v1.py`
- `tests/test_conversation_provider_unavailable_clarification_fallback_v1.py`
- `tests/test_ocs_llm_cognition_end_to_end_runtime_v1.py`
- `tests/test_external_resource_registry_runtime_v0.py`
- `tests/test_worker_assignment_runtime_v1.py`

## Regression Suite Structure

The post-certification suite is the following focused command:

```bash
python -m pytest \
  tests/test_conversational_cli_runtime_v1.py \
  tests/test_universal_intake_layer_v1.py \
  tests/test_conversation_provider_unavailable_clarification_fallback_v1.py \
  tests/test_ocs_llm_cognition_end_to_end_runtime_v1.py \
  tests/test_external_resource_registry_runtime_v0.py \
  tests/test_worker_assignment_runtime_v1.py
```

Current certification baseline:

```text
160 passed
```

The suite should remain small enough to run on every pull request that touches HIRR, ACLI conversation routing, Universal Intake, OCS cognition, ERR, replay serialization, or worker assignment.

## Certification Evidence Model

Every suite run intended to preserve certification must record:

- suite identifier: `AIGOL_HIRR_POST_CERTIFICATION_REGRESSION_SUITE_V1`;
- source revision or change reference;
- command executed;
- test files included;
- total tests collected;
- pass/fail result;
- failure list, if any;
- whether `HUMAN_INTENT_RESOLUTION_READY` remains `READY`;
- known limitations or stale artifact names observed;
- `git diff --check` result for whitespace and patch hygiene.

Minimum passing evidence:

```text
all selected tests pass
git diff --check clean
no new provider invocation from HIRR clarification
no new worker invocation from HIRR clarification or OCS advisory cognition
ERR remains passive
replay evidence remains reconstructable
fail-closed tests remain passing
```

Certification preservation output:

```text
HIRR_POST_CERTIFICATION_REGRESSION_SUITE = PASS
HUMAN_INTENT_RESOLUTION_READY = READY
```

Certification regression output:

```text
HIRR_POST_CERTIFICATION_REGRESSION_SUITE = FAIL
HUMAN_INTENT_RESOLUTION_READY = RECERTIFICATION_REQUIRED
```

## CI Integration Strategy

Recommended CI integration:

1. Add a named CI job:

```text
hirr-post-certification-regression-suite
```

2. Run the focused command on changes touching:

- `aigol/cli/`;
- `aigol/runtime/`;
- `tests/test_conversational_cli_runtime_v1.py`;
- `tests/test_universal_intake_layer_v1.py`;
- `tests/test_conversation_provider_unavailable_clarification_fallback_v1.py`;
- `tests/test_ocs_llm_cognition_end_to_end_runtime_v1.py`;
- `tests/test_external_resource_registry_runtime_v0.py`;
- `tests/test_worker_assignment_runtime_v1.py`;
- `docs/governance/` artifacts governing HIRR, ERR, OCS, replay, or ELL.

3. Always run on release-candidate branches.

4. Always run before updating any artifact that states:

```text
HUMAN_INTENT_RESOLUTION_READY = READY
```

5. Treat any failure as certification-blocking until investigated.

The CI job must not call real providers, invoke real workers, dispatch work, mutate governance, or perform autonomous resource discovery.

## Recertification Triggers

HIRR recertification is required if any of the following occur:

- clarification-first behavior changes;
- clarification continuity artifacts or chain semantics change;
- workflow target refinement behavior changes;
- advisory cognition routing behavior changes;
- provider availability classification changes;
- OCS ERR provider lookup changes;
- worker assignment ERR lookup changes;
- ERR resource schema, status semantics, resource types, or selection evidence changes;
- replay artifact shape, replay hashing, replay ordering, or reconstruction semantics change;
- fail-closed behavior changes for HIRR, OCS, ERR, or worker assignment;
- any test in the post-certification suite is removed, skipped, weakened, or reclassified;
- a real provider or real worker becomes reachable from HIRR clarification or advisory cognition paths;
- ELL is reactivated or proposed for runtime implementation;
- a new resource type, capability model, lifecycle state, ranking behavior, optimization behavior, or routing engine is introduced.

Recertification must produce a new governance artifact and must not silently amend this certification baseline.

## Implementation Plan

Phase 1: Scope Lock

- Keep this artifact as the canonical regression-suite definition.
- Link future HIRR certification updates to this suite.
- Preserve the focused test command as the minimum evidence gate.

Phase 2: CI Binding

- Add a CI job named `hirr-post-certification-regression-suite`.
- Use the focused pytest command from this artifact.
- Add `git diff --check` as a companion hygiene check.

Phase 3: Evidence Capture

- Store CI output or release evidence with:
  - command;
  - revision;
  - result;
  - collected test count;
  - pass count;
  - failure details if any.

Phase 4: Recertification Discipline

- Require explicit HIRR recertification when any recertification trigger fires.
- Preserve visible known limitations.
- Do not mark HIRR ready after a suite failure without a governed repair and rerun.

## Final Regression Recommendation

Adopt `AIGOL_HIRR_POST_CERTIFICATION_REGRESSION_SUITE_V1` as the minimum protected evidence gate for preserving:

```text
HUMAN_INTENT_RESOLUTION_READY = READY
```

The suite should remain focused, deterministic, replay-aware, fail-closed, and free of real provider or worker invocation.
