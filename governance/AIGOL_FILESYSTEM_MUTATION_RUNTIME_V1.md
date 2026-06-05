# AIGOL_FILESYSTEM_MUTATION_RUNTIME_V1

## Status

Runtime implementation certification.

## Final Classification

```text
AIGOL_FILESYSTEM_MUTATION_RUNTIME_STATUS = CERTIFIED
```

## Purpose

This runtime is the first governed runtime that materializes an authorized
implementation bundle into real files.

The runtime creates only authorized `CREATE_ONLY` files. It does not overwrite,
delete, rename, move, invoke providers, or invoke workers.

## Runtime Component

Implemented:

```text
aigol/runtime/filesystem_mutation_runtime.py
```

## Output Artifact

Defined:

```text
FILESYSTEM_MUTATION_ARTIFACT_V1
```

The artifact includes:

- implementation manifest reference and hashes;
- filesystem mutation authorization reference and hashes;
- exact mutation results;
- exact created paths;
- exact materialized content hashes;
- collision and forbidden-operation boundary evidence;
- `filesystem_mutation_hash`.

## Validation Responsibilities

The runtime verifies:

- `FILESYSTEM_MUTATION_AUTHORIZATION_ARTIFACT_V1` is present, hash-valid, and successful;
- authorization lineage matches the implementation manifest;
- only authorized files are created;
- all target paths match manifest and authorization paths exactly;
- all operations are `CREATE_ONLY`;
- all content hashes match manifest content before and after materialization;
- target files do not already exist before any write occurs;
- collision handling fails closed before writing additional authorized files;
- mutation evidence is replay-visible and deterministic.

## Forbidden Operations

The runtime forbids:

- overwrite;
- delete;
- rename;
- move;
- implicit file creation;
- unauthorized files;
- provider invocation;
- worker invocation.

## Fail-Closed Conditions

The runtime fails closed when:

- authorization artifact is missing, invalid, unsuccessful, or mismatched;
- manifest artifact hash or manifest hash mismatches;
- authorized path set does not exactly equal manifest path set;
- any permission is not `CREATE_ONLY`;
- any target path is malformed or escapes the mutation root;
- any target file already exists;
- any manifest content hash mismatches generated content;
- any materialized file hash mismatches expected content hash.

## Determinism

Identical manifests and authorization artifacts produce identical
`filesystem_mutation_hash` values and identical
`FILESYSTEM_MUTATION_ARTIFACT_V1` evidence, independent of temporary mutation
root paths.

## Validation

Implemented tests:

```text
tests/test_filesystem_mutation_runtime_v1.py
```

Validation performed:

```text
python -m pytest tests/test_filesystem_mutation_runtime_v1.py
python -m pytest tests/test_filesystem_mutation_authorization_runtime_v1.py
python -m pytest tests/test_implementation_summary_runtime_v1.py
python -m pytest tests/test_generated_content_acceptance_runtime_v1.py
python -m pytest tests/test_generated_test_validation_runtime_v1.py
python -m pytest tests/test_generated_content_validation_runtime_v1.py
python -m pytest tests/test_implementation_manifest_runtime_v1.py
git diff --check
```
