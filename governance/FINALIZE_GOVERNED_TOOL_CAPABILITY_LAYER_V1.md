# FINALIZE_GOVERNED_TOOL_CAPABILITY_LAYER_V1

## Scope

This milestone introduces the first governed capability execution layer for AiGOL.

It adds deterministic capability requests, an immutable capability registry, sandbox-aware capability policy and validation, bounded capability execution, replay-visible capability persistence, and capability replay reconstruction.

Governed tool capability layer introduces bounded capability execution only. It does not introduce unrestricted execution, orchestration authority, autonomous execution, filesystem mutation, shell execution, subprocess execution, or unrestricted runtime behavior.

## Architectural Principles

- Capability is not authority.
- Provider is not executor.
- Cognition is not execution.
- Capability execution remains sandbox-bound.
- Capability requests remain governance-visible.
- Capability execution remains replay-visible.
- Capability execution fails closed.

## Capability Registry

Allowed V1 capabilities are:

- `read_text`
- `inspect_json`
- `analyze_text`
- `mock_write_preview`

Forbidden capabilities are:

- `shell_execution`
- `subprocess_spawn`
- `filesystem_write`
- `unrestricted_network`
- `delete_file`
- `worker_spawn`
- `recursive_dispatch`
- `orchestration`

Unknown capabilities and wildcard permissions fail closed.

## Capability Execution Boundary

The executor supports only bounded operations:

- `read_text`: reads from explicitly approved safe paths only.
- `inspect_json`: inspects JSON payloads only.
- `analyze_text`: performs deterministic local text analysis only.
- `mock_write_preview`: generates preview evidence only and performs no filesystem mutation.

The executor does not spawn subprocesses, execute shell commands, write files, access unrestricted network, spawn workers, recursively dispatch runtime tasks, or orchestrate flows.

## Replay Guarantees

Capability requests, validations, and results use canonical JSON with sorted keys, stable separators, UTF-8 persistence, and SHA-256 replay hashes.

Capability persistence is append-only and immutable. Replay reconstruction restores the capability request, validation, result, ledger entries, and replay chain.

## Mutation Boundary

This milestone adds `aigol.runtime.capabilities`, capability artifact persistence methods, a narrow explicit `RuntimeEngine` capability branch, focused tests, and governance evidence.

It does not add dynamic capability mutation, unrestricted capability registration, shell execution, subprocess execution, filesystem mutation, orchestration, autonomous retries, background tasks, worker spawning, or self-modifying runtime behavior.

## Deterministic Acceptance Evidence

Acceptance requires tests for:

- valid capability request;
- unknown capability blocking;
- forbidden capability blocking;
- malformed request blocking;
- invalid replay hash blocking;
- unauthorized governance state blocking;
- sandbox capability mismatch blocking;
- deterministic replay hashing;
- append-only capability persistence;
- replay reconstruction;
- safe-path read enforcement;
- path traversal blocking;
- preview-only write behavior;
- subprocess prevention;
- shell prevention;
- immutable capability guarantees;
- fail-closed behavior.

## Certification

`FINALIZE_GOVERNED_TOOL_CAPABILITY_LAYER_V1` certifies the first governance-controlled operational capability substrate inside AiGOL while preserving sandbox boundaries, replay visibility, fail-closed semantics, and non-orchestrating runtime behavior.
