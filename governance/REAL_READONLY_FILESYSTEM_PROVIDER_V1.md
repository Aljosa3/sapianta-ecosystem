# REAL_READONLY_FILESYSTEM_PROVIDER_V1

## Scope

This milestone introduces the first real bounded read-only filesystem provider for AiGOL Phase 3.

The provider exposes only:

- `inspect_metadata(path)`
- `read_file(path, max_bytes)`
- `list_allowed_directory(path, max_entries)`

## Guarantees

- Read-only file access only.
- Explicit safe path allowlist enforcement.
- Fail-closed path validation.
- Symlink traversal rejection.
- Path traversal rejection.
- Outside-allowlist rejection.
- Bounded file reads.
- Non-recursive directory listing.
- Deterministic replay-visible evidence.
- Bounded metadata inspection.

## Non-Goals

- Writes.
- Deletes.
- Directory creation.
- Permission mutation.
- Ownership mutation.
- Subprocess or shell execution.
- Docker or CI/CD.
- Cloud mutation.
- Unrestricted filesystem access.
- Recursive directory crawling.
- Orchestration.
- Autonomous planning.

## Evidence Shape

Every operation returns structured evidence with:

- operation;
- requested path;
- normalized path when allowed;
- allowed flag;
- status;
- reason;
- bytes read or entries returned;
- deterministic evidence hash.

## Boundary

The provider is not a runtime orchestration layer, not a capability planner, and not a general filesystem authority. It is a bounded read-only provider that fails closed on unsafe paths.

## Certification

`REAL_READONLY_FILESYSTEM_PROVIDER_V1` certifies that AiGOL has a minimal real filesystem read provider while preserving bounded, deterministic, replay-visible, fail-closed, non-orchestrating runtime semantics.
