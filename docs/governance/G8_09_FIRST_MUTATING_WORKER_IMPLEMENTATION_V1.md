# G8-09 First Mutating Worker Implementation V1

Status: first mutating Worker implemented.

Final verdict: FIRST_MUTATING_WORKER_IMPLEMENTED

## 1. Executive Summary

G8-09 implements the first governed mutating Worker exactly within the scope specified by G8-08.

The implementation supports only:

```text
CREATE_SINGLE_FILE_IN_GOVERNED_MUTATION_WORKSPACE
```

The operation creates exactly one new plaintext file inside the allowlisted non-authority workspace:

```text
runtime/governed_mutation_workspace/
```

The implementation preserves:

- ACLI Next as thin adapter;
- Platform Core orchestration;
- Governance authorization;
- Worker Platform execution;
- Replay evidence;
- fail-closed behavior;
- hash-bound rollback metadata;
- no Git, no commit, no deployment, no provider invocation.

## 2. Runtime Deliverables

Files added:

| File | Purpose |
| --- | --- |
| `aigol/runtime/first_mutating_worker_runtime.py` | Platform Core runtime for the first governed create-only mutation. |
| `tests/test_g8_first_mutating_worker_runtime.py` | Targeted tests for success, approval binding, fail-closed behavior, and prohibited execution surfaces. |
| `docs/governance/G8_09_FIRST_MUTATING_WORKER_IMPLEMENTATION_V1.md` | Implementation evidence and governance summary. |

Existing runtime reused:

- `aigol/workers/filesystem_worker.py`;
- `aigol/authorization/authorization_record.py`;
- `aigol/runtime/transport/serialization.py`.

No new authority layer was introduced.

Local runtime setup:

- `runtime/governed_mutation_workspace/` was initialized as the allowlisted non-authority workspace.
- The `/runtime/` tree is ignored by repository hygiene rules and remains operational runtime state, not governed source.

## 3. Implemented Flow

Runtime flow:

```text
mutation candidate
-> explicit human approval bound to candidate hash
-> Governance authorization record
-> Worker Platform authorized request
-> pre-mutation target absence evidence
-> filesystem create Worker execution
-> post-mutation validation
-> rollback metadata
-> replay-visible completion
```

The Worker Platform performs the mutation through the existing filesystem Worker. Platform Core coordinates artifacts and validation. Governance remains the authority. Replay remains evidence system.

## 4. Mutation Scope

Allowed:

- create one new plaintext file;
- filename only, no path separators;
- target must be inside `runtime/governed_mutation_workspace/`;
- target must not already exist;
- content must be UTF-8 plaintext;
- content must be hash-bound before execution.

Prohibited:

- existing file modification;
- multi-file mutation;
- path traversal;
- `.git/` mutation;
- governance artifact mutation;
- shell execution;
- provider invocation;
- Git staging or commit creation;
- deployment;
- additional Worker dispatch.

## 5. Governance Integration

Governance integration uses the existing authorization record surface:

```text
aigol.authorization.authorization_record
```

The runtime creates and validates an authorization record with:

- worker id `FILESYSTEM_CREATE_WORKER`;
- authorization scope `FILESYSTEM_CREATE_FILE`;
- proposal id bound to the mutation candidate;
- replay-visible governed authorization flags;
- no worker self-authorization;
- no dispatch or execution performed by the authorization record.

Human approval is explicit and must match:

```text
confirm mutation <candidate_id> <candidate_hash>
```

Approval cannot be inferred from advisory confirmation or natural language request text.

## 6. Worker Platform Integration

Worker execution is delegated to:

```text
aigol.workers.filesystem_worker.execute_filesystem_create_request
```

The Worker receives only an authorized single-file create request. It validates:

- authorization scope;
- Worker id;
- operation;
- filename;
- target absence;
- replay availability.

The Platform Core runtime does not write the target file directly.

## 7. Replay Integration

Replay artifacts are written append-only for:

1. mutation candidate;
2. human approval;
3. Governance authorization;
4. Worker request;
5. pre-mutation state;
6. Worker result;
7. post-mutation validation;
8. rollback metadata;
9. completion.

The runtime also reconstructs the nested filesystem Worker replay.

Replay reconstruction verifies:

- artifact ordering;
- wrapper hashes;
- artifact hashes;
- candidate approval binding;
- authorization continuity;
- Worker request continuity;
- target absence before execution;
- validation status;
- rollback hash continuity;
- completion hash continuity.

## 8. Validation

Implemented validation verifies:

- target file exists after execution;
- target is created inside the allowlisted workspace;
- content hash matches the candidate hash;
- exactly one file is created;
- no Git, commit, deployment, provider, or additional Worker dispatch is performed;
- replay reconstructs.

Targeted tests cover:

- successful governed create-only mutation;
- missing approval fail-closed behavior;
- invalid confirmation rejection;
- existing target fail-closed behavior;
- path traversal rejection;
- source guardrails against provider, Git, and deployment surfaces.

## 9. Rollback Metadata

The runtime records rollback metadata:

```text
DELETE_CREATED_FILE_IF_HASH_MATCHES
```

Rollback is not automatic. It requires separate authorization. The metadata binds rollback eligibility to the exact created file hash and forbids deleting directories or pre-existing files.

## 10. Boundary Review

| Boundary | Result |
| --- | --- |
| ACLI Next thin entrypoint | Preserved; no ACLI mutation policy added. |
| Platform Core orchestration | Preserved; runtime coordinates artifacts and validation. |
| Governance authority | Preserved; authorization record required. |
| Worker Platform execution | Preserved; filesystem Worker performs file creation. |
| Replay authority | Preserved; replay artifacts are append-only and reconstructable. |
| Provider boundary | Preserved; no provider invocation. |
| Git boundary | Preserved; no Git operation or commit. |
| Deployment boundary | Preserved; no deployment. |

## 11. Validation Evidence

Validation performed:

```text
git diff --check
python -m py_compile aigol/runtime/first_mutating_worker_runtime.py tests/test_g8_first_mutating_worker_runtime.py
python -m pytest tests/test_g8_first_mutating_worker_runtime.py tests/test_repository_mutation_worker_runtime_v1.py
```

Validation result: clean.

## 12. Final Determination

The first governed mutating Worker has been implemented.

It performs only a create-only, single-file mutation inside the allowlisted governed mutation workspace and preserves Governance, Worker Platform, Replay, and thin-entrypoint boundaries.

Final verdict: FIRST_MUTATING_WORKER_IMPLEMENTED
