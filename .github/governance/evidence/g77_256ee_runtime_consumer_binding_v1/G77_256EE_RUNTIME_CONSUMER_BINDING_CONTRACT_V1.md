# G77-256EE Runtime Consumer Binding Contract V1

Status: BOUNDED REPOSITORY-SIDE HARDENING CANDIDATE

Generation: G77-256EE

Required baseline: `07057c4159ac6728bafde7618e1ad8f62f71ab0f`

## Purpose

This contract extends the existing DU Canonical V1 and EB candidate-bound validation chain with one pre-materialization adapter. It proves that the exact regular file exported to the path statically declared by an authenticated runtime harness is the same canonical manifest already admitted by the candidate-bound EB receipt.

It does not replace DU or EB, create a second continuation dialect, authorize materialization, or grant execution authority.

## Canonical Binding

The validator SHALL:

1. authenticate the required Git HEAD and tree;
2. independently reauthenticate the candidate-bound EB receipt;
3. require the candidate argument to equal the EB receipt candidate path;
4. statically extract `RAW_ROOT` and `CONTINUATION_MANIFEST_PATH` from the authenticated harness without importing or executing it;
5. derive the only admissible repository runtime path as `repository_export_root / relative(harness_expected_path, harness_runtime_root)`;
6. reject absent, alternate, symlinked, non-regular, or non-canonical runtime input;
7. require exact candidate/runtime byte equality;
8. require exact candidate/runtime canonical inner-manifest identity equality; and
9. issue a self-authenticating receipt binding candidate, EB receipt, runtime path and bytes, harness path and bytes, validator/schema identities, HEAD, and tree.

Receipt verification SHALL reread and reauthenticate every bound artifact. A changed, moved, renamed, substituted, or deleted candidate, runtime file, receipt, harness, validator, or schema cannot retain `PASS`.

## Fail-Closed Boundary

Any failure occurs before materialization. The validator performs no copy, rename, symlink, repair, substitution, fallback, materialization, VM operation, P11 entry, E05 execution, P12 entry, or production routing.

If architecture requires a deterministic projection to the runtime filename, the producer must complete that projection before this final binding receipt. The projected runtime file is then authenticated directly.

## Authority Semantics

The binding receipt is evidence, not authority. It is never auto-continuable. Human authorization remains required for any later materialization or execution generation.
