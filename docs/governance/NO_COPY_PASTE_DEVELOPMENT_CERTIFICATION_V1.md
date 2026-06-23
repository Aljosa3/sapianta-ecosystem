# NO_COPY_PASTE_DEVELOPMENT_CERTIFICATION_V1

Status: Defined

Purpose: Determine whether ACLI can function as the primary governed development interface without requiring an external ChatGPT to Codex copy/paste development loop.

## 1. Certification Scope

This certification evaluates the target flow:

```text
Human
-> ACLI
-> HIRR
-> Governed Development Workflow
-> Proposal
-> Approval
-> Repository Mutation
-> Validation
-> Replay
```

The review is limited to existing certified runtime paths. It does not introduce a new workflow family, redesign ACLI, or loosen governance boundaries.

## 2. Runtime Evidence Reviewed

Reviewed runtime paths:

- `aigol.runtime.conversational_cli_runtime`
- `aigol.runtime.human_intent_clarification_intake_runtime`
- `aigol.runtime.governed_development_workflow_runtime`
- `aigol.runtime.governance_artifact_creation_runtime`
- `aigol.runtime.governed_repository_mutation_runtime`
- `aigol.runtime.repository_mutation_worker_runtime`
- `aigol.runtime.validation_command_runner_runtime`

Reviewed tests and evidence:

- `tests/test_conversational_cli_runtime_v1.py`
- `tests/test_governed_development_end_to_end_certification_v1.py`
- `tests/test_cognition_to_governed_execution_certification_v1.py`
- `tests/test_acli_supervised_primary_development_mode_v1.py`
- `sapianta_bridge/no_copy_paste_loop/evidence/FIRST_NO_COPY_PASTE_LOOP_V1.md`
- `sapianta_bridge/no_copy_paste_validation/evidence/FIRST_NO_COPY_PASTE_USER_FLOW_VALIDATION_V1.md`

## 3. Workflow Review

Verified:

- natural development prompts route through ACLI routing;
- HIRR classifies natural development prompts as `DEVELOPMENT_INTENT`;
- `DEVELOPMENT_INTENT` resolves to `GOVERNED_DEVELOPMENT_WORKFLOW`;
- routing replay is persisted and reconstructable;
- routing does not invoke a provider, worker, approval, or repository mutation by itself;
- governed development execution composes governance artifact creation and governed repository mutation;
- governed repository mutation uses the protected repository mutation worker path;
- validation executes through allowlisted validation command runtime;
- replay reconstruction verifies proposal, approval, component, and outcome hashes;
- missing approval fails closed before mutation;
- proposal hash mismatch fails closed before mutation.

Code evidence:

- `route_conversational_cli_intent(...)` records conversational routing, workflow selection, and returned routing replay.
- `workflow_registry()` registers `GOVERNED_DEVELOPMENT_WORKFLOW` with `aigol conversation` and `governed_development_workflow_runtime`.
- `classify_development_intent_for_governed_routing(...)` classifies examples such as `Add replay validation` and `Implement worker authorization` as development intent.
- `execute_governed_development_workflow(...)` requires request, intent, workflow, repository context, proposal, and approval artifacts before mutation.
- `_validate_approval(...)` rejects missing approval and approval/proposal hash mismatches.
- `reconstruct_governed_development_workflow_replay(...)` verifies replay ordering, artifact hashes, proposal hash binding, approval hash binding, and component outcome hashes.

## 4. Certification Test Design

The primary certification test should prove one operator-facing no-copy-paste development cycle:

```text
Prompt: "Add replay validation"
-> ACLI conversation entrypoint
-> HIRR DEVELOPMENT_INTENT
-> GOVERNED_DEVELOPMENT_WORKFLOW selection
-> generated proposal artifact
-> explicit human approval artifact
-> governance artifact creation
-> repository mutation worker execution
-> git diff --check validation
-> governed development replay reconstruction
```

Required assertions:

- ACLI routing status is `WORKFLOW_SELECTED`;
- selected workflow is `GOVERNED_DEVELOPMENT_WORKFLOW`;
- routing replay states `worker_invoked == False` before approval;
- proposal contains governance artifact and repository mutation components;
- approval binds the top-level proposal hash and component proposal hashes;
- repository mutation does not occur before approval;
- repository mutation uses governed repository mutation runtime and worker protections;
- validation command status is completed;
- replay reconstruction succeeds;
- missing approval fails closed without mutation;
- tampered proposal fails closed without mutation.

Existing partial coverage:

- `tests/test_governed_development_end_to_end_certification_v1.py` proves the governed development runtime chain from natural language routing to repository mutation and replay.
- `tests/test_conversational_cli_runtime_v1.py` proves natural development intent routing without execution.
- `tests/test_cognition_to_governed_execution_certification_v1.py` proves cognition-to-governed-execution continuity.

Missing certification coverage:

- one direct ACLI operator test that starts at `aigol conversation` and completes proposal creation, approval capture, repository mutation, validation, and replay without a test harness manually assembling proposal and approval artifacts.

## 5. Gap Analysis

### Gap 1: ACLI Operator Execution Bridge

Observed state:

- ACLI can route natural development prompts to `GOVERNED_DEVELOPMENT_WORKFLOW`.
- The governed development workflow can execute when provided complete artifacts.
- The interactive `aigol conversation` path primarily records routing, visibility, intake, cognition, clarification, and selected workflow state.

Gap:

- No verified operator-facing ACLI path completes the transition from selected governed development workflow to proposal generation, approval capture, workflow execution, validation, and replay in one primary interface loop.

Impact:

- ACLI is not yet fully certified as the primary development interface.
- The current certified runtime still depends on a programmatic or test-harness artifact assembly step for governed development execution.

Classification:

```text
MATERIAL_HANDOFF_POINT
```

### Gap 2: Human Approval Capture UX

Observed state:

- approval artifacts are explicit, hash-bound, replay-visible, and required by runtime validation.

Gap:

- certification has not proven an ACLI operator approval prompt that captures approval for the generated governed development proposal and persists it as the approval artifact consumed by the runtime.

Impact:

- approval boundary is preserved, but not yet productized as a no-copy-paste operator step.

Classification:

```text
OPERATOR_SURFACE_GAP
```

### Gap 3: Proposal Derivation From Human Prompt

Observed state:

- proposal constructors exist and enforce hash binding.
- tests provide canonical proposal contents directly.

Gap:

- certification has not proven a deterministic ACLI proposal derivation stage from operator prompt plus repository context.

Impact:

- external drafting or manual artifact preparation may still be required.

Classification:

```text
PROPOSAL_ASSEMBLY_GAP
```

## 6. Manual Handoff Points

Remaining handoff points before full no-copy-paste readiness:

- operator prompt to complete governed development proposal artifact;
- proposal artifact to explicit approval artifact;
- approved proposal to governed development workflow execution;
- execution result to operator-facing replay summary.

These are not architecture blockers. They are operator-surface and integration-certification blockers.

## 7. Implementation Plan

P0 implementation required:

1. Add a bounded ACLI governed development execution bridge for `GOVERNED_DEVELOPMENT_WORKFLOW`.
2. Generate a deterministic proposal from routed development intent and repository context.
3. Present the proposal summary and target paths to the operator.
4. Capture explicit approval, rejection, or modification request.
5. Persist the approval artifact with proposal hash binding.
6. Invoke `execute_governed_development_workflow(...)` only after approval.
7. Return validation status and replay references in the ACLI response.
8. Add one end-to-end ACLI test that uses the conversation command path or `run_interactive_conversation(...)` without manually assembling artifacts outside the ACLI flow.

Implementation boundaries:

- do not allow provider output to authorize execution;
- do not mutate before approval;
- do not bypass repository mutation worker runtime;
- do not broaden validation command allowlists;
- do not introduce autonomous continuation beyond the approved workflow execution;
- do not claim Product 1 readiness or compliance readiness from this certification alone.

## 8. Certification Conditions

`NO_COPY_PASTE_DEVELOPMENT_READY` requires:

- natural language prompt enters ACLI;
- HIRR classifies development intent;
- governed development workflow is selected;
- proposal is generated without external ChatGPT to Codex relay;
- human approval is captured inside the ACLI-governed path;
- repository mutation executes through the existing worker path;
- validation executes through allowlisted validation runtime;
- replay evidence is persisted and reconstructable;
- missing approval fails closed;
- approval/proposal hash mismatch fails closed;
- operator receives a replay reference and validation result.

## 9. Current Certification Assessment

The runtime foundation is sufficient for governed no-copy-paste development, but the primary ACLI operator loop is not yet fully certified.

Readiness classification:

```text
PARTIALLY_READY
```

Reason:

```text
Governed development execution is certified, but ACLI does not yet have a verified one-loop operator path from natural prompt through proposal, approval, mutation, validation, and replay.
```

## 10. Final Verdict

```text
NO_COPY_PASTE_DEVELOPMENT_NOT_READY
```

Required next verdict after P0 bridge implementation and certification:

```text
NO_COPY_PASTE_DEVELOPMENT_READY
```
