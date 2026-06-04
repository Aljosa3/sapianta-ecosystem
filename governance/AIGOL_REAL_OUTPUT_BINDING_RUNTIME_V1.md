# AIGOL_REAL_OUTPUT_BINDING_RUNTIME_V1

## Status

Certified narrow real-output binding runtime.

`AIGOL_REAL_OUTPUT_BINDING_RUNTIME_STATUS = CERTIFIED`

## Purpose

`AIGOL_REAL_OUTPUT_BINDING_RUNTIME_V1` binds one validated Worker output to one
real, create-only governance document.

The runtime closes the smallest missing gap between:

```text
RESULT_VALIDATED
-> Authorized Filesystem Mutation
-> Artifact Creation
-> Artifact Verification
-> Replay Recording
```

## Scope

The only supported target is:

`governance/MARKETING_DOMAIN_FOUNDATION_V1.md`

The only supported artifact type is:

`GOVERNANCE_DOCUMENT_MARKDOWN`

The content is deterministic and owned by the runtime. Callers cannot supply
arbitrary file content.

## Authorization Model

Filesystem mutation requires an
`EXACT_OUTPUT_MUTATION_AUTHORIZATION` artifact.

The authorization binds:

- Worker result validation reference and hash;
- canonical chain id;
- exact target path;
- exact artifact type;
- deterministic content hash;
- `CREATE_ONLY` permission;
- no overwrite, delete, rename, move, directory creation, recursive creation,
  or authority transfer.

The target must already appear in both the validated `allowed_outputs` and
`produced_outputs`.

## Filesystem Boundary

Allowed:

- one existing workspace root;
- one existing `governance/` directory;
- one exact Markdown target;
- create-only file open semantics.

Forbidden:

- overwrite;
- delete;
- rename;
- move;
- directory creation;
- nested target directories;
- runtime files;
- test files;
- arbitrary governance paths;
- caller-supplied content.

## Replay Model

The runtime persists:

1. mutation authorization;
2. output binding evidence;
3. real output binding artifact;
4. artifact verification result.

Replay reconstruction verifies authorization continuity, validation continuity,
chain continuity, target continuity, content hash continuity, and verification
status.

Post-execution replay review accepts the verified binding as an optional
lineage input. When present, review reconstruction verifies the binding before
governed termination may close the lifecycle.

## CLI Progression

Before:

```text
RESULT_VALIDATED
-> REVIEW_COMPLETED
-> TERMINATED
```

After, for the supported marketing-domain target:

```text
RESULT_VALIDATED
-> OUTPUT_BOUND
-> ARTIFACT_CREATED
-> ARTIFACT_VERIFIED
-> REVIEW_COMPLETED
-> TERMINATED
```

The conversation CLI exposes `--workspace` so the exact mutation workspace is
operator-visible and testable.

## Fail-Closed Conditions

The runtime fails closed when:

- mutation authorization is absent or invalid;
- validation replay is invalid or mismatched;
- target path or artifact type is unauthorized;
- target is outside validated outputs;
- target already exists;
- workspace or governance directory is missing;
- content hash authorization is mismatched;
- post-write verification fails;
- replay artifacts already exist or are corrupted.

## Non-Goals

This runtime does not support:

- multi-file bundles;
- recursive creation;
- directory creation;
- runtime implementation files;
- test generation;
- overwrite or update semantics;
- automatic retry;
- deletion, rename, or move;
- arbitrary content generation;
- general governance mutation authority.

## Remaining Gap

Multi-file domain creation remains unimplemented. It requires a content-bearing
manifest for each artifact, nested and multi-output policy, deterministic
partial-failure handling, and bundle-level replay verification.

