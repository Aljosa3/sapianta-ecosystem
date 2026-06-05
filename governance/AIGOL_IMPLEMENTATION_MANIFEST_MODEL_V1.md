# AIGOL_IMPLEMENTATION_MANIFEST_MODEL_V1

## Status

Contract-only implementation manifest model.

## Manifest Artifact

Required artifact:

```text
IMPLEMENTATION_MANIFEST_ARTIFACT_V1
```

The manifest represents the complete provider-generated implementation package.
It is content-bearing, hash-bound, replay-visible, and non-authoritative.

## Required Manifest Fields

```text
artifact_type
manifest_id
canonical_chain_id
source_candidate_reference
source_candidate_hash
implementation_handoff_reference
implementation_handoff_hash
provider_generation_authorization_reference
provider_generation_authorization_hash
provider_response_reference
provider_response_hash
target_domain
target_resource
target_worker
operation_mode
file_entries
test_entries
validation_requirements
forbidden_operations
known_gaps
manifest_hash
artifact_hash
```

## Operation Modes

Initial supported mode:

```text
CREATE_ONLY
```

Future modes require separate certification:

```text
UPDATE_ONLY
REPLACE_ONLY
DELETE
RENAME
MOVE
RECURSIVE_CREATE
DEPENDENCY_INSTALL
```

Only `CREATE_ONLY` should be eligible for the first real implementation
generation runtime.

## File Entry Model

Each file entry must contain:

```text
file_entry_id
target_path
artifact_type
operation
content_encoding
content_hash
content_size_bytes
source_segment_reference
preflight_target_state
validation_requirements
authority_flags
```

Requirements:

- `target_path` must be exact and workspace-relative;
- `operation` must be authorized explicitly;
- `content_hash` must be computed from canonical file bytes;
- `preflight_target_state` must be bound before mutation;
- authority flags must all be false.

## Test Entry Model

Each test entry must contain:

```text
test_entry_id
target_path
operation
content_hash
tests_file_entries
validation_command
expected_coverage_target
negative_case_requirement
fixture_references
authority_flags
```

Requirements:

- tests must be linked to implementation file entries;
- validation commands must be bounded and explicit;
- generated tests must not authorize implementation;
- generated tests must not weaken existing tests;
- generated tests must be replay-visible.

## Manifest Hash

`manifest_hash` must bind:

- source candidate;
- implementation handoff;
- provider generation authorization;
- provider response;
- ordered file entries;
- ordered test entries;
- validation requirements;
- forbidden operations;
- operation mode;
- known gaps.

## Content Hash Binding

Each file content hash must be computed before human content acceptance and
before filesystem mutation authorization.

The same hash must appear in:

- implementation manifest;
- generated content validation artifact;
- generated test validation artifact when applicable;
- content acceptance authorization;
- filesystem mutation authorization;
- post-application verification artifact.

## Multi-File Certification Model

Required artifact:

```text
IMPLEMENTATION_MANIFEST_CERTIFICATION_ARTIFACT_V1
```

Certification must verify:

- manifest hash continuity;
- every file entry hash;
- every test entry hash;
- validation command results;
- human content acceptance;
- filesystem mutation authorization;
- per-file application result;
- post-application file hashes;
- replay reconstruction;
- fail-closed absence of unauthorized operations.

## Replay Evidence Required

Minimum replay stages:

```text
000_candidate_selection_authorized.json
001_provider_generation_authorized.json
002_provider_implementation_request_recorded.json
003_provider_implementation_response_recorded.json
004_implementation_manifest_recorded.json
005_generated_code_validation_recorded.json
006_generated_test_validation_recorded.json
007_content_acceptance_authorized.json
008_filesystem_mutation_authorized.json
009_file_application_recorded.json
010_post_application_verification_recorded.json
011_implementation_certification_recorded.json
```

Future runtimes may split these stages, but they may not omit equivalent
evidence.

