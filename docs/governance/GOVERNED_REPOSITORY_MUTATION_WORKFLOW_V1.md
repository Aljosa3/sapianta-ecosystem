# GOVERNED_REPOSITORY_MUTATION_WORKFLOW_V1

Status: Defined

Scope: First ACLI governed repository mutation workflow using the existing repository mutation worker.

Runtime target:

```text
Human
-> ACLI
-> Governed Repository Mutation
-> Repository Mutation Worker
-> Validation
-> Replay
```

Final workflow verdict:

```text
GOVERNED_REPOSITORY_MUTATION_READY
```

## 1. Workflow Definition

This workflow enables ACLI to execute a bounded repository mutation after explicit human approval.

The workflow preserves:

```text
Human = Authority
Replay = Source Of Truth
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

The workflow is not a generic autonomous development executor. It is a governed bridge from approved repository mutation intent to the existing repository mutation worker.

Lifecycle:

```text
Natural Language
-> HIRR / resolved intent
-> workflow selection: GOVERNED_REPOSITORY_MUTATION
-> mutation proposal
-> explicit human approval
-> repository mutation worker
-> validation command runner
-> replay reconstruction
-> final outcome
```

## 2. Runtime Design

Runtime responsibilities:

- accept resolved repository mutation intent
- create a replay-visible mutation request
- create a proposal containing approved file mutation candidates
- require explicit approval bound to proposal hash
- convert approved proposal into existing `PATCH_PROPOSAL_ARTIFACT_V1`
- invoke `apply_repository_mutation`
- run allowlisted validation
- persist full workflow replay
- fail closed on missing approval, scope mismatch, worker failure, validation failure, or replay corruption

Runtime boundaries:

- do not redesign HIRR
- do not redesign replay
- do not weaken repository mutation worker protections
- do not permit governance artifact creation
- do not mutate `.git/`, `.github/governance/`, `runtime/finalization_evidence/`, or `docs/governance/`
- do not infer approval from intent
- do not bypass validation

## 3. Exact Code Changes

Existing files to modify:

| File | Change |
| --- | --- |
| `aigol/runtime/conversational_cli_runtime.py` | Add `GOVERNED_REPOSITORY_MUTATION` workflow id, registry entry, routing helper, and operator summary. |
| `tests/test_conversational_cli_runtime_v1.py` | Add routing and registry assertions. |

New files to create:

| File | Purpose |
| --- | --- |
| `aigol/runtime/governed_repository_mutation_runtime.py` | ACLI governed repository mutation orchestration runtime. |
| `tests/test_governed_repository_mutation_runtime_v1.py` | Positive path, fail-closed behavior, replay, validation, and worker-protection tests. |

Existing runtime reused:

- `aigol/runtime/repository_mutation_worker_runtime.py`
- `aigol/runtime/validation_command_runner_runtime.py`
- `aigol/runtime/transport/serialization.py`

## 4. Tests

Required tests:

- workflow is registered
- explicit governed repository mutation prompt routes to `GOVERNED_REPOSITORY_MUTATION`
- routing does not invoke provider, worker, execution, approval bypass, or mutation
- proposal requires approved file mutations
- approval binds to proposal hash
- missing approval fails closed
- path escape fails closed
- `docs/governance/` mutation fails closed in this workflow
- approved mutation invokes repository mutation worker
- validation runs through allowlisted command runner
- replay reconstructs request, proposal, approval, worker mutation, validation, and outcome
- existing repository mutation worker tests still pass
- existing validation runner tests still pass

## 5. Validation Plan

Required validation commands:

```bash
python -m py_compile aigol/runtime/governed_repository_mutation_runtime.py aigol/runtime/conversational_cli_runtime.py
python -m pytest tests/test_governed_repository_mutation_runtime_v1.py
python -m pytest tests/test_conversational_cli_runtime_v1.py -k "governed_repository_mutation or governance_artifact_creation or generic_governed_execution"
python -m pytest tests/test_repository_mutation_worker_runtime_v1.py
python -m pytest tests/test_validation_command_runner_runtime_v1.py
git diff --check
```

## 6. Acceptance Criteria

The workflow is ready only when:

- `GOVERNED_REPOSITORY_MUTATION` is registered
- explicit governed repository mutation prompts route to the workflow
- a mutation proposal artifact is generated
- explicit approval is required and bound to proposal hash
- approved mutations are converted to existing repository mutation worker proposals
- repository mutation worker protections remain intact
- validation evidence is persisted
- replay reconstruction verifies continuity
- fail-closed behavior is tested
- focused tests and `git diff --check` pass

Final target verdict:

```text
GOVERNED_REPOSITORY_MUTATION_READY
```
