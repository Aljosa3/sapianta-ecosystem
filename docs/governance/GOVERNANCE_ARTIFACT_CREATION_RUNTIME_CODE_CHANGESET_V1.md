# GOVERNANCE_ARTIFACT_CREATION_RUNTIME_CODE_CHANGESET_V1

Status: Defined

Scope: Exact repository code changes required to implement the first ACLI governed development workflow.

Input artifacts:

- GOVERNANCE_ARTIFACT_CREATION_WORKFLOW_V1
- GOVERNANCE_ARTIFACT_CREATION_RUNTIME_V1
- GOVERNANCE_ARTIFACT_CREATION_RUNTIME_IMPLEMENTATION_PLAN_V1

Verified runtime basis:

```text
workflow registry exists in aigol/runtime/conversational_cli_runtime.py
workflow routing exists in aigol/runtime/conversational_cli_runtime.py
generic governed artifact detection exists in aigol/runtime/human_execution_intent_detection.py
validation command runner exists in aigol/runtime/validation_command_runner_runtime.py
repository mutation worker exists in aigol/runtime/repository_mutation_worker_runtime.py
generic repository mutation currently rejects governance artifact mutation
```

Code changeset verdict:

```text
CODE_CHANGESET_READY
```

Final artifact verdict:

```text
GOVERNANCE_ARTIFACT_CREATION_RUNTIME_CODE_CHANGESET_V1_DEFINED
```

## 1. Existing Files To Modify

Required existing file modifications:

| File | Exact purpose |
| --- | --- |
| `aigol/runtime/conversational_cli_runtime.py` | Add workflow constant, register workflow, route governed artifact creation intent to workflow. |
| `aigol/runtime/human_execution_intent_detection.py` | Update routing action for generic governed artifact creation now that a certified workflow entrypoint is being introduced. |
| `tests/test_conversational_cli_runtime_v1.py` | Add registry and routing tests for `GOVERNANCE_ARTIFACT_CREATION`. |

Existing files expected to be reused without redesign:

| File | Reuse purpose |
| --- | --- |
| `aigol/runtime/validation_command_runner_runtime.py` | Execute allowlisted `git diff --check` validation. |
| `aigol/runtime/transport/serialization.py` | Persist immutable replay artifacts and compute replay hashes. |
| `aigol/runtime/models.py` | Reuse `FailClosedRuntimeError`. |

Existing file that should not be weakened:

| File | Constraint |
| --- | --- |
| `aigol/runtime/repository_mutation_worker_runtime.py` | Preserve current generic prevention of governance artifact mutation unless a separately certified scoped artifact type is introduced. |

## 2. New Files To Create

Required new runtime file:

```text
aigol/runtime/governance_artifact_creation_runtime.py
```

Required new test file:

```text
tests/test_governance_artifact_creation_runtime_v1.py
```

No new CLI command file is required for the first implementation tranche. The workflow is invoked through the existing ACLI conversation routing surface.

No new provider, worker, transport, server, release, or deployment file is required.

## 3. Registry Changes

File:

```text
aigol/runtime/conversational_cli_runtime.py
```

Add constant near existing workflow id constants:

```python
GOVERNANCE_ARTIFACT_CREATION = "GOVERNANCE_ARTIFACT_CREATION"
```

Add registry entry in `workflow_registry()`:

```python
_workflow(
    GOVERNANCE_ARTIFACT_CREATION,
    "aigol conversation",
    "governance_artifact_creation_runtime",
)
```

Required registry behavior:

- workflow id appears exactly once
- workflow has `existing_cli_command` set to `aigol conversation`
- workflow has `existing_runtime` set to `governance_artifact_creation_runtime`
- coverage count increases by one
- no existing workflow id is renamed
- no existing workflow id is removed

Required import surface for tests:

```python
from aigol.runtime.conversational_cli_runtime import GOVERNANCE_ARTIFACT_CREATION
```

## 4. Routing Changes

File:

```text
aigol/runtime/conversational_cli_runtime.py
```

Current behavior:

```python
if execution_intent["intent_class"] in {
    GENERIC_GOVERNED_ARTIFACT_CREATION,
    GENERIC_GOVERNED_EXECUTION_REQUEST,
}:
    raise FailClosedRuntimeError(...)
```

Required behavior:

```python
if execution_intent["intent_class"] == GENERIC_GOVERNED_ARTIFACT_CREATION:
    return _analysis(
        GOVERNANCE_ARTIFACT_CREATION,
        execution_intent["confidence"],
        execution_intent["matched_terms"] or ["create", "governed", "artifact"],
    )

if execution_intent["intent_class"] == GENERIC_GOVERNED_EXECUTION_REQUEST:
    raise FailClosedRuntimeError(...)
```

Additional routing helper may be added only if needed:

```python
def _is_governance_artifact_creation_prompt(normalized: str) -> bool:
    ...
```

Supported routing phrases:

- `create governed artifact`
- `create governance artifact`
- `define governance artifact`
- `create certification artifact`
- `create governance workflow artifact`
- `create governance analysis artifact`

Forbidden routing:

- runtime implementation prompts
- test implementation prompts
- release prompts
- deployment prompts
- broad generic governed execution prompts
- repository mutation prompts without governance artifact creation scope

## 5. Intent Detection Changes

File:

```text
aigol/runtime/human_execution_intent_detection.py
```

Current generic governed artifact creation routing action:

```text
FAIL_CLOSED_NO_CERTIFIED_ARTIFACT_CREATION_ENTRYPOINT
```

Required routing action:

```text
ROUTE_TO_GOVERNANCE_ARTIFACT_CREATION_WORKFLOW
```

Required preservation:

- `execution_authority_granted` remains `False`
- `requires_clarification` remains `True` unless deterministic workflow invocation has enough context
- intent detection does not grant approval
- intent detection does not authorize mutation

This file should not become a workflow executor.

## 6. Runtime Module Changes

New file:

```text
aigol/runtime/governance_artifact_creation_runtime.py
```

Required constants:

```python
AIGOL_GOVERNANCE_ARTIFACT_CREATION_RUNTIME_VERSION
GOVERNANCE_ARTIFACT_PROPOSAL_ARTIFACT_V1
GOVERNANCE_ARTIFACT_APPROVAL_ARTIFACT_V1
GOVERNANCE_ARTIFACT_CREATION_ARTIFACT_V1
GOVERNANCE_ARTIFACT_CREATION_COMPLETED
FAILED_CLOSED
APPROVED
REJECTED
NEEDS_CLARIFICATION
```

Required public functions:

```python
create_governance_artifact_proposal(...)
create_governance_artifact_approval(...)
create_governance_artifact(...)
reconstruct_governance_artifact_creation_replay(...)
```

Optional orchestration function:

```python
execute_governance_artifact_creation(...)
```

Required internal responsibilities:

- validate target path is under `docs/governance/`
- validate target path is markdown
- validate proposal hash
- validate approval decision
- validate approval-to-proposal binding
- validate approved path matches proposed path
- write exactly one approved artifact
- persist replay wrappers in deterministic order
- call validation command runner for `git diff --check`
- fail closed on missing evidence, invalid scope, validation failure, or replay failure

Required non-responsibilities:

- no provider invocation
- no generic repository mutation
- no runtime code modification
- no test modification
- no deployment
- no replay history mutation
- no certification readiness claim

## 7. Proposal Artifact Changes

Proposal artifact type:

```text
GOVERNANCE_ARTIFACT_PROPOSAL_ARTIFACT_V1
```

Minimum structure:

```json
{
  "artifact_type": "GOVERNANCE_ARTIFACT_PROPOSAL_ARTIFACT_V1",
  "runtime_version": "AIGOL_GOVERNANCE_ARTIFACT_CREATION_RUNTIME_V1",
  "proposal_id": "...",
  "workflow_id": "GOVERNANCE_ARTIFACT_CREATION",
  "original_request_reference": "...",
  "resolved_intent_reference": "...",
  "target_path": "docs/governance/...",
  "artifact_title": "...",
  "artifact_purpose": "...",
  "expected_sections": [],
  "mutation_summary": "...",
  "validation_plan": {
    "required_commands": [["git", "diff", "--check"]]
  },
  "human_approval_required": true,
  "mutation_allowed_before_approval": false,
  "provider_authority_granted": false,
  "replay_references": [],
  "replay_hashes": [],
  "artifact_hash": "..."
}
```

Proposal validation rules:

- target path must start with `docs/governance/`
- target path must end with `.md`
- target path must not contain path traversal
- proposal must require human approval
- proposal must not permit mutation before approval
- proposal must include validation plan

## 8. Approval Artifact Changes

Approval artifact type:

```text
GOVERNANCE_ARTIFACT_APPROVAL_ARTIFACT_V1
```

Minimum structure:

```json
{
  "artifact_type": "GOVERNANCE_ARTIFACT_APPROVAL_ARTIFACT_V1",
  "runtime_version": "AIGOL_GOVERNANCE_ARTIFACT_CREATION_RUNTIME_V1",
  "approval_id": "...",
  "proposal_id": "...",
  "proposal_hash": "...",
  "decision": "APPROVED",
  "approved_target_path": "docs/governance/...",
  "approved_scope": "...",
  "approved_mutation_limits": {
    "allowed_file_count": 1,
    "allowed_operation": "CREATE_ONE_GOVERNANCE_MARKDOWN_ARTIFACT"
  },
  "approved_validation_plan": {
    "required_commands": [["git", "diff", "--check"]]
  },
  "approved_by": "HUMAN_OPERATOR",
  "approved_at": "...",
  "replay_references": [],
  "replay_hashes": [],
  "artifact_hash": "..."
}
```

Approval validation rules:

- decision must be one of `APPROVED`, `REJECTED`, or `NEEDS_CLARIFICATION`
- only `APPROVED` permits artifact creation
- approval must reference proposal id
- approval must reference proposal hash
- approval target path must match proposal target path
- approval validation plan must include `git diff --check`
- approval must not broaden proposal scope

## 9. Replay Changes

New replay integration in:

```text
aigol/runtime/governance_artifact_creation_runtime.py
```

Required replay step constants:

```python
REPLAY_STEPS = (
    "governance_artifact_creation_request_recorded",
    "governance_artifact_creation_intent_recorded",
    "governance_artifact_creation_workflow_recorded",
    "governance_artifact_creation_context_recorded",
    "governance_artifact_creation_proposal_recorded",
    "governance_artifact_creation_approval_recorded",
    "governance_artifact_creation_mutation_recorded",
    "governance_artifact_creation_validation_recorded",
    "governance_artifact_creation_outcome_recorded",
)
```

Required replay files:

```text
000_governance_artifact_creation_request_recorded.json
001_governance_artifact_creation_intent_recorded.json
002_governance_artifact_creation_workflow_recorded.json
003_governance_artifact_creation_context_recorded.json
004_governance_artifact_creation_proposal_recorded.json
005_governance_artifact_creation_approval_recorded.json
006_governance_artifact_creation_mutation_recorded.json
007_governance_artifact_creation_validation_recorded.json
008_governance_artifact_creation_outcome_recorded.json
```

Replay integration points:

- use `write_json_immutable` for persisted wrappers
- use `replay_hash` for artifacts and wrapper verification
- reconstruct by loading all wrappers in order
- verify wrapper hashes
- verify artifact hashes
- verify proposal-to-approval hash continuity
- verify approval-to-mutation scope continuity
- verify validation-to-outcome continuity

Replay failure must raise `FailClosedRuntimeError` or return a failed-closed capture.

## 10. Test Files

Modify:

```text
tests/test_conversational_cli_runtime_v1.py
```

Add assertions:

- import `GOVERNANCE_ARTIFACT_CREATION`
- `workflow_registry()` contains the new workflow
- route prompt: `"Create a governed artifact named ExampleArtifact"` selects `GOVERNANCE_ARTIFACT_CREATION`
- route prompt: `"Create a governance artifact for the new runtime"` selects `GOVERNANCE_ARTIFACT_CREATION`
- routed capture keeps `provider_invoked is False`
- routed capture keeps `worker_invoked is False`
- routed capture keeps `execution_requested is False`
- unsupported generic governed execution still raises `FailClosedRuntimeError`

Create:

```text
tests/test_governance_artifact_creation_runtime_v1.py
```

Required tests:

- proposal creation produces `GOVERNANCE_ARTIFACT_PROPOSAL_ARTIFACT_V1`
- proposal rejects path outside `docs/governance/`
- proposal rejects non-markdown path
- approval binds to proposal id and hash
- rejected approval fails closed
- missing approval fails closed
- approved creation writes exactly one markdown file under `docs/governance/`
- path traversal fails closed
- validation via `git diff --check` is recorded
- replay reconstructs successful creation
- corrupted replay fails closed

Run existing regression tests:

```text
tests/test_repository_mutation_worker_runtime_v1.py
tests/test_validation_command_runner_runtime_v1.py
```

Regression expectations:

- generic repository mutation worker still prevents governance artifact mutation
- validation runner still enforces allowlist

## 11. Acceptance Criteria

Code changeset is complete only when:

- `GOVERNANCE_ARTIFACT_CREATION` constant exists.
- `workflow_registry()` registers the workflow exactly once.
- governed artifact creation prompts route to `GOVERNANCE_ARTIFACT_CREATION`.
- generic governed execution prompts without artifact creation remain fail-closed.
- `governance_artifact_creation_runtime.py` exists.
- proposal artifact creation is implemented and validated.
- approval artifact creation is implemented and validated.
- approved artifact creation writes exactly one file under `docs/governance/`.
- missing or invalid approval fails closed.
- invalid target path fails closed.
- validation uses allowlisted `git diff --check`.
- replay artifacts are persisted in deterministic order.
- replay reconstruction verifies hashes and continuity.
- generic repository mutation worker protections remain intact.
- focused tests pass.
- `git diff --check` passes.

Recommended validation commands:

```bash
python -m pytest tests/test_conversational_cli_runtime_v1.py
python -m pytest tests/test_governance_artifact_creation_runtime_v1.py
python -m pytest tests/test_repository_mutation_worker_runtime_v1.py
python -m pytest tests/test_validation_command_runner_runtime_v1.py
git diff --check
```

## 12. Final Verdict

Final code changeset verdict:

```text
CODE_CHANGESET_READY
```

Rationale:

The required code changes are concrete and bounded. The changeset modifies ACLI registry and routing, introduces one narrow runtime module, adds focused tests, reuses existing validation and serialization helpers, and preserves the existing repository mutation worker protections.

Final artifact verdict:

```text
GOVERNANCE_ARTIFACT_CREATION_RUNTIME_CODE_CHANGESET_V1_DEFINED
```
