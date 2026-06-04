# AIGOL_EXECUTABLE_DOMAIN_BUNDLE_RUNTIME_V1

## Status

Certified executable domain bundle runtime.

`AIGOL_EXECUTABLE_DOMAIN_BUNDLE_RUNTIME_STATUS = CERTIFIED`

## Purpose

`AIGOL_EXECUTABLE_DOMAIN_BUNDLE_RUNTIME_V1` extends governed domain bundle
creation from governance-only artifacts to one exact bundle containing
governance, runtime, and test artifacts.

## Certified Bundle

Bundle id:

`MARKETING_EXECUTABLE_DOMAIN_BUNDLE_V1`

Artifacts:

- `governance/MARKETING_DOMAIN_FOUNDATION_V1.md`
- `governance/MARKETING_DOMAIN_MODEL_V1.md`
- `governance/MARKETING_DOMAIN_CERTIFICATION.json`
- `aigol/runtime/marketing_domain_runtime.py`
- `tests/test_marketing_domain_runtime_v1.py`

The runtime and test artifacts are deterministic executable placeholders. This
milestone does not authorize or claim real Marketing implementation logic.

## Authorization Model

Filesystem mutation requires `EXECUTABLE_BUNDLE_MUTATION_AUTHORIZATION`.

The authorization binds:

- exact ordered artifact list;
- exact paths;
- exact artifact types;
- exact deterministic content hashes;
- Worker result validation reference and hash;
- canonical chain id;
- `CREATE_ONLY` permission;
- no overwrite, delete, rename, move, implicit creation, recursive creation,
  directory creation, or authority transfer.

## Filesystem And Verification Rules

The runtime validates the complete authorization and absence of all target
paths before the first write. It writes only exact authorized files using
create-only file open semantics.

Every artifact is verified for:

- file existence;
- authorized path;
- authorized artifact type;
- authorized content hash.

The bundle reaches `EXECUTABLE_BUNDLE_VERIFIED` only after all five artifacts
are verified.

Expected path and authorization failures are rejected before the first write.
Unexpected post-write I/O failure fails closed and remains replay-visible
without forbidden rollback deletion.

## Replay

Replay persists:

1. executable bundle authorization;
2. executable bundle creation evidence;
3. per-artifact verification;
4. executable bundle verification result.

Post-execution replay review verifies executable bundle lineage before governed
termination.

## CLI Progression

```text
RESULT_VALIDATED
-> EXECUTABLE_BUNDLE_AUTHORIZED
-> ARTIFACTS_CREATED
-> EXECUTABLE_BUNDLE_VERIFIED
-> REVIEW_COMPLETED
-> TERMINATED
```

## Non-Goals

This runtime does not support:

- real Marketing implementation logic;
- provider-generated code;
- arbitrary runtime or test files;
- overwrite or update semantics;
- delete, rename, move, or rollback mutation;
- implicit artifact creation;
- directory creation;
- recursive creation.

## Remaining Gap

Real implementation logic requires a bounded implementation contract,
domain-specific behavior specification, code validation, test adequacy
validation, and explicit authority for implementation content rather than
deterministic placeholders.

