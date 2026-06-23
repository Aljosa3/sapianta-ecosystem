# GOVERNED_DEVELOPMENT_WORKFLOW_V1

Status: Defined

Scope: ACLI governed development orchestration workflow.

Composed runtimes:

- GOVERNANCE_ARTIFACT_CREATION_RUNTIME_V1
- GOVERNED_REPOSITORY_MUTATION_WORKFLOW_V1

Target flow:

```text
Human
-> ACLI
-> Development Intent
-> Proposal
-> Approval
-> Governance Artifact Creation
-> Governed Repository Mutation
-> Validation
-> Replay
```

Final workflow verdict:

```text
GOVERNED_DEVELOPMENT_WORKFLOW_READY
```

## 1. Workflow Design

This workflow composes the existing governance artifact creation and governed repository mutation workflows into one governed development lifecycle.

The workflow preserves:

```text
Human = Authority
Replay = Source Of Truth
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

The workflow is not a new mutation primitive. It orchestrates already governed primitives:

- governance artifact creation runtime creates approved governance documentation
- governed repository mutation runtime invokes the existing repository mutation worker
- validation remains allowlisted
- replay records the top-level orchestration and component workflow evidence

## 2. Runtime Design

The governed development runtime must:

- create one top-level development proposal
- bind one explicit human approval to the top-level proposal hash
- derive component approvals from the approved top-level scope
- invoke governance artifact creation first
- invoke governed repository mutation second
- preserve validation evidence from both component workflows
- persist top-level replay evidence linking both component replays
- fail closed when either component fails

Runtime boundaries:

- do not redesign HIRR
- do not redesign replay
- do not bypass component workflow approvals
- do not weaken repository mutation worker protections
- do not bypass validation command allowlists
- do not mutate before approval

## 3. Integration Points

Existing files to modify:

| File | Integration |
| --- | --- |
| `aigol/runtime/conversational_cli_runtime.py` | Register and route `GOVERNED_DEVELOPMENT_WORKFLOW`. |
| `tests/test_conversational_cli_runtime_v1.py` | Add registry and routing coverage. |

New files:

| File | Purpose |
| --- | --- |
| `aigol/runtime/governed_development_workflow_runtime.py` | Top-level governed development orchestration runtime. |
| `tests/test_governed_development_workflow_runtime_v1.py` | End-to-end composition, replay, approval, and fail-closed tests. |

Component runtimes reused:

- `aigol/runtime/governance_artifact_creation_runtime.py`
- `aigol/runtime/governed_repository_mutation_runtime.py`
- `aigol/runtime/repository_mutation_worker_runtime.py`
- `aigol/runtime/validation_command_runner_runtime.py`

## 4. Exact Code Changes

Add workflow id:

```text
GOVERNED_DEVELOPMENT_WORKFLOW
```

Add runtime:

```text
governed_development_workflow_runtime
```

Add public runtime functions:

```text
create_governed_development_proposal
create_governed_development_approval
execute_governed_development_workflow
reconstruct_governed_development_workflow_replay
```

Required replay stages:

```text
request
intent
workflow
context
proposal
approval
governance_artifact_creation
repository_mutation
outcome
```

## 5. Tests

Required tests:

- workflow registration
- explicit governed development prompt routes to `GOVERNED_DEVELOPMENT_WORKFLOW`
- proposal contains both component proposals
- approval binds to top-level proposal hash
- governance artifact creation executes first
- repository mutation executes second
- missing approval fails closed before mutation
- component failure fails closed
- replay reconstructs top-level continuity
- component replay references are preserved

## 6. Validation Plan

Required validation commands:

```bash
python -m py_compile aigol/runtime/governed_development_workflow_runtime.py aigol/runtime/conversational_cli_runtime.py
python -m pytest tests/test_governed_development_workflow_runtime_v1.py
python -m pytest tests/test_conversational_cli_runtime_v1.py -k "governed_development_workflow or governed_repository_mutation or governance_artifact_creation"
python -m pytest tests/test_governance_artifact_creation_runtime_v1.py
python -m pytest tests/test_governed_repository_mutation_runtime_v1.py
python -m pytest tests/test_repository_mutation_worker_runtime_v1.py
python -m pytest tests/test_validation_command_runner_runtime_v1.py
git diff --check
```

## 7. Acceptance Criteria

The workflow is ready only when:

- `GOVERNED_DEVELOPMENT_WORKFLOW` is registered
- routing selects the workflow without execution
- one top-level proposal and approval are required
- component approvals are hash-bound to the approved top-level proposal
- governance artifact creation replay is linked
- governed repository mutation replay is linked
- repository mutation worker protections remain intact
- validation allowlists remain intact
- replay reconstruction verifies top-level and component continuity

Final target verdict:

```text
GOVERNED_DEVELOPMENT_WORKFLOW_READY
```
