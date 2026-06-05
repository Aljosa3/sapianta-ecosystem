# AIGOL_GENERATED_CONTENT_VALIDATION_RUNTIME_V1

## Status

Runtime implementation certification.

## Final Classification

```text
AIGOL_GENERATED_CONTENT_VALIDATION_RUNTIME_STATUS = CERTIFIED
```

## Purpose

This runtime validates generated implementation content after an
`IMPLEMENTATION_MANIFEST_ARTIFACT_V1` exists and before any human content
acceptance or filesystem mutation authorization.

The runtime validates generated content. It does not generate content.

## Runtime Component

Implemented:

```text
aigol/runtime/generated_content_validation_runtime.py
```

## Output Artifact

Defined:

```text
GENERATED_CONTENT_VALIDATION_ARTIFACT_V1
```

The artifact includes:

- manifest reference and manifest hashes;
- file validation results;
- test validation results;
- validation checks;
- allowed artifact types;
- allowed target prefixes;
- forbidden operations;
- `generated_content_validation_hash`.

## Validation Responsibilities

The runtime verifies:

- manifest consistency;
- implementation manifest artifact hash;
- implementation manifest hash;
- generated file content hashes;
- generated test content hashes;
- artifact type allow-list membership;
- workspace-relative allowed paths;
- `CREATE_ONLY` operation mode and entry operations;
- `MUST_NOT_EXIST` preflight target state for generated files;
- test-to-file bundle references;
- target path uniqueness;
- bundle file and test counts;
- authority flags remain false.

## Authority Boundaries

The runtime is read-only and non-authoritative.

It does not:

- mutate the filesystem;
- invoke a provider;
- invoke a worker;
- create approval;
- authorize execution;
- authorize dispatch;
- authorize filesystem mutation;
- authorize governance mutation;
- authorize replay mutation.

## Fail-Closed Conditions

The runtime fails closed when:

- manifest artifact type is invalid;
- manifest status is not created;
- manifest hash or artifact hash mismatches;
- content hash or size mismatches;
- target path is absolute, escaping, malformed, or outside allowed prefixes;
- artifact type is not allowed;
- operation mode or entry operation is not `CREATE_ONLY`;
- generated file preflight state is not `MUST_NOT_EXIST`;
- tests reference unknown file entries;
- bundle counts or target paths are inconsistent;
- any authority flag is true.

## Determinism

Identical implementation manifests produce identical
`generated_content_validation_hash` values and identical
`GENERATED_CONTENT_VALIDATION_ARTIFACT_V1` outputs.

## Validation

Implemented tests:

```text
tests/test_generated_content_validation_runtime_v1.py
```

Validation performed:

```text
python -m pytest tests/test_generated_content_validation_runtime_v1.py
python -m pytest tests/test_implementation_manifest_runtime_v1.py
git diff --check
```
