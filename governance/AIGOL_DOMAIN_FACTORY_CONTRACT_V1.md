# AIGOL_DOMAIN_FACTORY_CONTRACT_V1

## Status

Review-only factory contract.

## Contract Inputs

A future generic factory runtime must consume:

- `WORKER_RESULT_VALIDATION_ARTIFACT_V1`;
- worker result validation replay reference;
- selected `DOMAIN_BUNDLE_REGISTRY` entry;
- registry hash;
- explicit domain id;
- explicit bundle id;
- authorized actor and timestamp;
- replay directory.

## Contract Outputs

A successful factory run must produce:

- `EXECUTABLE_BUNDLE_MUTATION_AUTHORIZATION`;
- `EXECUTABLE_BUNDLE_CREATION_EVIDENCE_ARTIFACT_V1`;
- `EXECUTABLE_BUNDLE_ARTIFACT_VERIFICATION_V1`;
- `EXECUTABLE_DOMAIN_BUNDLE_ARTIFACT_V1`;
- replay wrappers for all success steps.

A failed factory run must produce:

- terminal `EXECUTABLE_BUNDLE_VERIFICATION_RESULT_V1`;
- deterministic failure reason;
- no missing-artifact cascade.

## Domain Artifact Template Model

`DOMAIN_ARTIFACT_TEMPLATE_MODEL` defines governance artifacts.

Required fields:

- `role`;
- `path`;
- `artifact_type`;
- `template_id`;
- `template_version`;
- `content`;
- `canonical_content_hash`;
- `required`;
- `permission`;
- `overwrite_permitted`.

Required governance roles:

- `DOMAIN_FOUNDATION`;
- `DOMAIN_MODEL`;
- `DOMAIN_CERTIFICATION`.

Governance templates must not make perfect safety, guaranteed compliance, AGI,
or unrestricted autonomy claims.

## Domain Runtime Template Model

`DOMAIN_RUNTIME_TEMPLATE_MODEL` defines executable placeholder runtime
artifacts.

Required fields:

- `path`;
- `module_name`;
- `runtime_version_symbol`;
- `describe_function`;
- `domain_id`;
- `implementation_status`;
- `content`;
- `canonical_content_hash`.

The runtime template must be deterministic and side-effect free. It must expose
only bounded placeholder identity unless a later implementation contract
certifies real domain behavior.

## Domain Test Template Model

`DOMAIN_TEST_TEMPLATE_MODEL` defines the test artifact for the runtime
template.

Required fields:

- `path`;
- `imports`;
- `test_function`;
- `expected_domain_id`;
- `expected_runtime_version`;
- `expected_implementation_status`;
- `content`;
- `canonical_content_hash`.

The test template must verify the runtime identity and must not call external
services, mutate governance, or perform domain execution.

## Authorization Rules

The factory authorization must bind:

- registry version;
- registry hash;
- registry entry hash;
- domain id;
- bundle id;
- exact ordered artifact manifests;
- exact content hashes;
- validation reference and hash;
- chain id;
- `CREATE_ONLY` permission;
- all mutation prohibitions.

## Verification Rules

The future runtime must verify:

- selected registry entry hash;
- validation output list equals selected registry artifact paths;
- target paths are absent before first write;
- each written artifact exists;
- each content hash matches authorization;
- all artifacts are verified before bundle success;
- replay order and replay hashes are valid.

## Failure Rules

The future runtime must fail closed when:

- domain id is absent from the registry;
- domain id is ambiguous;
- bundle entry is not executable;
- registry hash mismatches;
- output list differs from registry artifact paths;
- any target exists;
- any path is outside allowed roots;
- any artifact content hash mismatches;
- any replay artifact collides.
