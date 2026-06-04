# AIGOL_MULTI_ARTIFACT_DOMAIN_BUNDLE_RUNTIME_V1

## Status

Certified multi-artifact governance bundle runtime.

`AIGOL_MULTI_ARTIFACT_DOMAIN_BUNDLE_RUNTIME_STATUS = CERTIFIED`

## Purpose

`AIGOL_MULTI_ARTIFACT_DOMAIN_BUNDLE_RUNTIME_V1` extends governed real output
binding from one exact artifact to one exact related domain bundle.

## Certified Bundle

Bundle id:

`MARKETING_DOMAIN_BUNDLE_V1`

Bundle artifacts:

- `governance/MARKETING_DOMAIN_FOUNDATION_V1.md`
- `governance/MARKETING_DOMAIN_MODEL_V1.md`
- `governance/MARKETING_DOMAIN_CERTIFICATION.json`

The runtime does not accept arbitrary paths, artifact types, content, or bundle
membership.

## Authorization Model

Filesystem mutation requires `BUNDLE_MUTATION_AUTHORIZATION`.

The authorization binds:

- bundle id;
- Worker result validation reference and hash;
- canonical chain id;
- exact ordered artifact list;
- exact paths;
- exact artifact types;
- exact deterministic content hashes;
- `CREATE_ONLY` permission;
- no overwrite, delete, rename, move, recursive creation, directory creation,
  or authority transfer.

No artifact is created implicitly.

## Filesystem Semantics

Before the first write, the runtime validates:

- the workspace and existing `governance/` directory;
- exact validated output membership;
- exact authorization manifests;
- absence of every target path.

The runtime uses create-only file open semantics for each authorized target.
If any target already exists, the bundle fails closed before any bundle member
is created.

The runtime never reports partial bundle completion. Unexpected post-write I/O
failure is fail-closed and records any created paths in replay evidence. The
runtime does not erase evidence through rollback deletion because delete
authority is forbidden.

## Verification

Every artifact is verified after creation for:

- file existence;
- exact authorized path;
- exact artifact type;
- exact content hash.

The bundle reaches `BUNDLE_VERIFIED` only when every authorized artifact is
verified.

## Replay

Replay persists:

1. bundle authorization;
2. bundle creation evidence;
3. per-artifact verification;
4. bundle verification result.

Replay reconstruction verifies authorization continuity, validation
continuity, chain continuity, artifact membership, artifact hashes, current
file existence, and current content hashes.

Post-execution replay review accepts the verified bundle as an execution
lineage input before governed termination.

## CLI Progression

Before:

```text
RESULT_VALIDATED
-> OUTPUT_BOUND
-> ARTIFACT_CREATED
-> ARTIFACT_VERIFIED
-> REVIEW_COMPLETED
-> TERMINATED
```

After:

```text
RESULT_VALIDATED
-> BUNDLE_AUTHORIZED
-> ARTIFACTS_CREATED
-> BUNDLE_VERIFIED
-> REVIEW_COMPLETED
-> TERMINATED
```

## Non-Goals

This runtime does not support:

- runtime file generation;
- test generation;
- arbitrary domain bundles;
- overwrite or update semantics;
- delete, rename, move, or rollback mutation;
- directory creation;
- recursive creation;
- provider-generated content;
- implicit artifact creation.

## Remaining Gap

Runtime and test generation remain unimplemented. They require artifact-type
specific content production, bounded implementation execution, code and test
validation, and a broader authorization model without weakening exact-output
governance.

