# GOVERNANCE_ARTIFACT_CREATION_RUNTIME_IMPLEMENTATION_PLAN_V1

Status: Defined

Scope: Concrete implementation plan for `GOVERNANCE_ARTIFACT_CREATION_RUNTIME_V1`.

Governing artifacts:

- GOVERNANCE_ARTIFACT_CREATION_WORKFLOW_V1
- GOVERNANCE_ARTIFACT_CREATION_RUNTIME_V1
- ACLI_WORKFLOW_INVOCATION_RUNTIME_V1
- ACLI_REPOSITORY_CONTEXT_RUNTIME_V1
- ACLI_VALIDATION_RUNTIME_V1
- ACLI_DEVELOPMENT_REPLAY_RUNTIME_V1

Implementation plan verdict:

```text
IMPLEMENTATION_PLAN_READY
```

Final artifact verdict:

```text
GOVERNANCE_ARTIFACT_CREATION_RUNTIME_IMPLEMENTATION_PLAN_V1_DEFINED
```

## 1. Purpose

This artifact translates the `GOVERNANCE_ARTIFACT_CREATION` runtime design into concrete code implementation work.

This is an implementation plan. It does not redesign ACLI, HIRR, replay, repository mutation, governance, or Product 1.

The plan preserves:

```text
Human = Authority
Replay = Source Of Truth
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

## 2. Runtime Components

Implementation should touch the smallest necessary runtime surface.

Required code modifications:

| File | Required change |
| --- | --- |
| `aigol/runtime/conversational_cli_runtime.py` | Register `GOVERNANCE_ARTIFACT_CREATION` and route governed artifact creation intent to it. |
| `aigol/runtime/human_execution_intent_detection.py` | Update generic governed artifact creation routing action from fail-closed no-entrypoint to certified workflow candidate when the workflow is registered. |
| `aigol/runtime/governance_artifact_creation_runtime.py` | New narrow runtime module for proposal, approval binding, bounded artifact creation, validation orchestration, and replay package persistence. |
| `aigol/runtime/validation_command_runner_runtime.py` | Reuse existing allowlisted `git diff --check` runner; no redesign expected. |
| `aigol/runtime/repository_mutation_worker_runtime.py` | Do not silently relax current governance artifact mutation prevention. Modify only if a separate explicit governance-artifact creation path is introduced and tested. |
| `aigol/runtime/transport/serialization.py` | Reuse existing immutable JSON and replay hash helpers; no redesign expected. |

Required tests:

| Test file | Required coverage |
| --- | --- |
| `tests/test_conversational_cli_runtime_v1.py` | Registry and routing selection for `GOVERNANCE_ARTIFACT_CREATION`. |
| `tests/test_governance_artifact_creation_runtime_v1.py` | New runtime lifecycle, fail-closed cases, replay, and validation behavior. |
| `tests/test_repository_mutation_worker_runtime_v1.py` | Preserve existing prevention of generic governance artifact mutation unless explicitly changed by a new scoped pathway. |
| `tests/test_validation_command_runner_runtime_v1.py` | Existing allowlisted validation coverage should remain passing. Add coverage only if integration shape changes. |

Implementation note:

The existing repository mutation worker currently rejects governance artifact mutation through its generic patch proposal scope. The implementation must either:

- keep that worker unchanged and implement a dedicated `governance_artifact_creation_runtime.py` bounded writer, or
- introduce a new explicit artifact type and validation path that allows only approved governance artifact creation without weakening generic repository mutation protections.

The preferred minimal footprint is a dedicated narrow runtime module.

## 3. Workflow Registration

Add a workflow constant:

```text
GOVERNANCE_ARTIFACT_CREATION = "GOVERNANCE_ARTIFACT_CREATION"
```

Register it in:

```text
aigol/runtime/conversational_cli_runtime.py::workflow_registry
```

Required registry entry:

```text
_workflow(
    GOVERNANCE_ARTIFACT_CREATION,
    "aigol conversation",
    "governance_artifact_creation_runtime",
)
```

Registration acceptance criteria:

- `workflow_registry()` contains exactly one `GOVERNANCE_ARTIFACT_CREATION` entry.
- `_workflow_by_id("GOVERNANCE_ARTIFACT_CREATION")` resolves the entry.
- registry coverage count increases deterministically.
- no existing workflow id is renamed or removed.
- routing remains fail-closed for unsupported generic execution.

## 4. Workflow Selection

Update selection in:

```text
aigol/runtime/conversational_cli_runtime.py::_classify_workflow
```

Current behavior:

```text
GENERIC_GOVERNED_ARTIFACT_CREATION
-> FailClosedRuntimeError
```

Required behavior:

```text
GENERIC_GOVERNED_ARTIFACT_CREATION
-> GOVERNANCE_ARTIFACT_CREATION
```

Selection must remain deterministic and narrow.

Supported routing terms should include governance artifact creation prompts containing:

- governed artifact
- governance artifact
- create artifact
- define governance artifact
- certification artifact
- governance workflow artifact
- governance analysis artifact

Selection must not route broad code, test, deployment, release, or generic execution prompts into this workflow.

Routing acceptance criteria:

- supported governance artifact creation prompts select `GOVERNANCE_ARTIFACT_CREATION`.
- generic governed execution requests without artifact creation continue to fail closed.
- native development prompts that are not governance artifact creation continue to route through existing native development context behavior.
- replay-visible workflow selection artifact records selected workflow and confidence.
- routing does not invoke provider, worker, authorization, execution, or mutation.

## 5. Proposal Stage

Implement proposal creation in:

```text
aigol/runtime/governance_artifact_creation_runtime.py
```

Recommended public function:

```text
create_governance_artifact_proposal(...)
```

Minimum proposal artifact fields:

- artifact type
- runtime version
- proposal id
- original request reference
- resolved intent reference
- workflow id
- target path
- artifact title
- artifact purpose
- expected sections
- mutation summary
- validation plan
- replay references
- replay hashes
- human approval required
- mutation allowed before approval: false
- provider authority: false
- artifact hash

Proposal persistence:

```text
replay/governance_artifact_creation/proposal.json
```

Proposal acceptance criteria:

- proposal is hashable and replay-visible.
- proposal does not write the target artifact.
- proposal rejects target paths outside `docs/governance/`.
- proposal rejects non-markdown target paths.
- proposal rejects empty or ambiguous artifact content.
- proposal records validation requirement `git diff --check`.

## 6. Approval Stage

Implement explicit approval binding in:

```text
aigol/runtime/governance_artifact_creation_runtime.py
```

Recommended public function:

```text
create_governance_artifact_approval(...)
```

Approval artifact fields:

- approval id
- proposal id
- proposal hash
- human decision
- approved target path
- approved scope
- approved validation plan
- approved mutation limits
- approved by
- approved at
- replay references
- replay hashes
- artifact hash

Allowed decisions:

```text
APPROVED
REJECTED
NEEDS_CLARIFICATION
```

Approval acceptance criteria:

- only `APPROVED` permits artifact creation.
- approval must reference the proposal id and proposal hash.
- approval target path must match proposal target path.
- approval scope must not exceed proposal scope.
- missing, rejected, ambiguous, stale, or mismatched approval fails closed.

## 7. Repository Mutation

Implement bounded artifact creation in:

```text
aigol/runtime/governance_artifact_creation_runtime.py
```

Recommended public function:

```text
create_governance_artifact(...)
```

Mutation preconditions:

- proposal artifact is valid.
- approval artifact is valid.
- approval references proposal hash.
- target path is under `docs/governance/`.
- target file does not already exist unless replacement is explicitly allowed by a later workflow version.
- target content matches approved proposal scope.
- replay directory is available.

Allowed mutation:

```text
CREATE_ONE_GOVERNANCE_MARKDOWN_ARTIFACT
```

Preferred implementation:

- use direct bounded file write inside the dedicated runtime module
- create parent directories only when they are within `docs/governance/`
- preserve before-state evidence
- persist mutation artifact before returning success

Do not implement broad generic repository mutation in this tranche.

Do not weaken:

```text
repository_mutation_worker_runtime.py::_validate_patch_proposal
```

unless the implementation introduces a separate explicit artifact type and tests preserving generic protections.

Mutation acceptance criteria:

- writes exactly one approved file.
- refuses target path escape.
- refuses `.git`, replay, `.github/governance`, runtime, tests, release, and server paths.
- refuses unapproved content or path mismatch.
- records before and after hashes.
- records mutated file list.
- records whether governance artifact creation occurred.
- does not claim generic repository mutation readiness.

## 8. Validation

Use existing validation command runner:

```text
aigol/runtime/validation_command_runner_runtime.py
```

Required validation request:

```text
command: ["git", "diff", "--check"]
cwd: repository_root
```

Recommended integration function:

```text
validate_governance_artifact_creation(...)
```

Validation acceptance criteria:

- validation command request is certified.
- command is allowlisted.
- shell remains disabled.
- validation result is persisted.
- non-zero exit code fails closed.
- validation result hash is linked in final replay outcome.

No arbitrary validation command execution is permitted.

## 9. Replay

Replay must be implemented inside the new runtime module using existing serialization helpers.

Required replay package:

```text
replay/governance_artifact_creation/
  000_request_recorded.json
  001_intent_recorded.json
  002_workflow_invocation_recorded.json
  003_repository_context_recorded.json
  004_proposal_recorded.json
  005_approval_recorded.json
  006_artifact_creation_recorded.json
  007_validation_recorded.json
  008_outcome_recorded.json
```

Recommended public function:

```text
reconstruct_governance_artifact_creation_replay(replay_dir)
```

Replay acceptance criteria:

- all replay wrappers include index, step, artifact, and wrapper hash.
- artifact hashes are verified during reconstruction.
- source-to-result hashes are checked.
- replay ordering mismatch fails closed.
- missing approval, mutation, validation, or outcome artifact fails closed.
- reconstruction reports final status and evidence completeness.

## 10. Failure Handling

Implement fail-closed statuses defined by `GOVERNANCE_ARTIFACT_CREATION_RUNTIME_V1`:

```text
FAIL_CLOSED_UNRESOLVED_INTENT
FAIL_CLOSED_NO_WORKFLOW_SELECTION
FAIL_CLOSED_WORKFLOW_NOT_REGISTERED
FAIL_CLOSED_INSUFFICIENT_REPOSITORY_CONTEXT
FAIL_CLOSED_NO_PROPOSAL
FAIL_CLOSED_NO_APPROVAL
FAIL_CLOSED_APPROVAL_SCOPE_MISMATCH
FAIL_CLOSED_SCOPE_VIOLATION
FAIL_CLOSED_MUTATION_FAILED
FAIL_CLOSED_VALIDATION_FAILED
FAIL_CLOSED_REPLAY_INCOMPLETE
```

Failure acceptance criteria:

- failure artifact is persisted when replay directory is writable.
- failed mutation does not leave unapproved files behind.
- validation failure is visible in returned capture.
- no failure is converted to success by retry logic.
- final capture exposes `fail_closed_preserved: true`.

## 11. Tests

Required test coverage:

### 11.1 Workflow Registry Tests

Test file:

```text
tests/test_conversational_cli_runtime_v1.py
```

Required assertions:

- registry includes `GOVERNANCE_ARTIFACT_CREATION`.
- routing a governed artifact creation prompt selects that workflow.
- routing artifact preserves no provider invocation, no worker invocation, no execution request, and no mutation.
- generic governed execution prompt without artifact creation still fails closed.

### 11.2 Runtime Positive Path Tests

Test file:

```text
tests/test_governance_artifact_creation_runtime_v1.py
```

Required assertions:

- proposal artifact is generated.
- approval artifact is bound to proposal hash.
- approved artifact is created under `docs/governance/`.
- exactly one file is written.
- `git diff --check` validation is requested and passes.
- replay package reconstructs successfully.
- final capture reports workflow completed.

### 11.3 Runtime Fail-Closed Tests

Required fail-closed cases:

- missing approval
- rejected approval
- approval path mismatch
- target path escape
- non-markdown target path
- target outside `docs/governance/`
- validation failure
- replay corruption

### 11.4 Regression Tests

Required regression assertions:

- existing repository mutation worker still prevents generic governance artifact mutation unless intentionally replaced by a scoped artifact type.
- validation command runner still blocks non-allowlisted commands.
- conversational routing coverage remains deterministic.

Recommended validation commands:

```bash
python -m pytest tests/test_conversational_cli_runtime_v1.py
python -m pytest tests/test_governance_artifact_creation_runtime_v1.py
python -m pytest tests/test_repository_mutation_worker_runtime_v1.py
python -m pytest tests/test_validation_command_runner_runtime_v1.py
git diff --check
```

## 12. Acceptance Criteria

Implementation is complete only when:

- `GOVERNANCE_ARTIFACT_CREATION` is registered in ACLI workflow registry.
- governed artifact creation prompts route deterministically to the workflow.
- unsupported generic execution remains fail-closed.
- new runtime module creates proposal, approval, mutation, validation, replay, and outcome artifacts.
- no repository mutation occurs before explicit approval.
- artifact creation is limited to one approved markdown file under `docs/governance/`.
- validation runs through the allowlisted validation command runner.
- replay reconstruction proves request, intent, workflow, context, proposal, approval, mutation, validation, and outcome.
- all required tests pass.
- `git diff --check` passes.
- no artifact claims `ACLI_GOVERNED_DEVELOPMENT_READY`.

Objective completion status:

```text
GOVERNANCE_ARTIFACT_CREATION_RUNTIME_IMPLEMENTED
```

## 13. Final Verdict

Final implementation plan verdict:

```text
IMPLEMENTATION_PLAN_READY
```

Rationale:

The implementation plan identifies concrete runtime files, workflow registry changes, routing changes, a minimal new runtime module, approval and proposal artifacts, bounded repository mutation, validation integration, replay persistence, and required tests. It preserves current ACLI architecture and explicitly avoids weakening the existing generic repository mutation worker.

Final artifact verdict:

```text
GOVERNANCE_ARTIFACT_CREATION_RUNTIME_IMPLEMENTATION_PLAN_V1_DEFINED
```
