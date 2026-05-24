# GOVERNED_RETURN_CONTINUITY_HARDENING_V1

## Purpose

This milestone hardens CLI governed return continuity into persistent, replay-visible operating records.

It introduces:

- standardized `GOVERNED_RETURN_ARTIFACT_V1`;
- append-only local governed return ledger;
- evidence bundles per replay identity;
- read-only return inspection;
- read-only replay ledger and verification commands.

It does not add orchestration, retries, autonomous continuation, alternate providers, browser redesign, governance bypass, or semantic correctness verification.

## Governed Return Artifact Model

`GOVERNED_RETURN_ARTIFACT_V1` contains:

- `artifact_type`
- `schema_version`
- `replay_identity`
- `lineage`
- `execution_status`
- `provider_invoked`
- `provider_command`
- `provider_exit_code`
- `provider_stdout_hash`
- `provider_stderr_hash`
- `execution_result_hash`
- `execution_governance_hash`
- `governed_return_hash`
- `continuity_verified`
- `fail_closed`
- `diagnostic_evidence`
- `created_at`

Allowed execution statuses remain:

- `EXECUTION_COMPLETED`
- `EXECUTION_FAILED`
- `EXECUTION_BLOCKED`

## Ledger Model

The default append-only ledger path is:

`.runtime/aigol/ledger/governed_returns.jsonl`

Each line is one canonical JSON governed return artifact with sorted keys. Existing lines are not overwritten.

## Evidence Persistence Model

Evidence is persisted under:

`.runtime/aigol/evidence/<replay_identity>/`

Files:

- `governed_return.json`
- `provider_stdout.txt`
- `provider_stderr.txt`
- `diagnostic_evidence.json`
- `lineage.json`

Empty stdout/stderr are still persisted as deterministic empty files.

## Lineage Continuity Model

Lineage preserves:

- ingress artifact hash;
- proposal candidate hash;
- contract candidate hash;
- acceptance gate hash;
- task package preview hash;
- human approval hash;
- handoff preview hash;
- dispatch authorization hash;
- execution governance hash;
- governed return hash.

Unavailable upstream hashes are recorded as `UNKNOWN`, not omitted.

## Replay Verification Model

`aigol replay verify --replay-identity <id>` verifies:

- governed return hash;
- execution result hash presence;
- evidence files exist;
- ledger entry exists;
- lineage continuity exists.

Verification fails closed if required evidence is missing.

## CLI Commands

Added:

- `aigol return inspect --replay-identity <id>`
- `aigol replay ledger`
- `aigol replay verify --replay-identity <id>`

These commands inspect persisted evidence and do not execute providers.

## Fail-Closed Guarantees

Persistence rejects invalid execution status, missing replay identity, missing governed return hash, serialization failures, ledger write failures, and evidence write failures with structured diagnostics.

Failed executions are persisted and remain visible. No failed execution is converted into success.
