# CANONICAL_CHAIN_ID_ADR_V1

## Status

Accepted as foundation review.

## Context

`END_TO_END_EXECUTION_CHAIN_VALIDATION_V1` found that the current execution governance chain is replay-safe and certified through worker assignment, with no authority leaks identified.

The largest remaining architecture gap is the absence of a single immutable chain identity spanning:

```text
Human Prompt
  -> Proposal
  -> Approval
  -> Execution Request
  -> Ready For Dispatch
  -> Worker Assignment
```

Current artifacts can be traversed by references and hashes, but no canonical `canonical_chain_id` binds all stages.

## Decision

AiGOL will define a canonical immutable chain identity:

```text
CANONICAL_CHAIN_ID_ARTIFACT_V1
canonical_chain_id
```

AiGOL governance creates the chain id at chain opening after human prompt ingress and source routing evidence are available.

Future chain-aware artifacts must carry `canonical_chain_id`.

The chain id must never change. Supersession, child chains, cancellation, expiry, completion, or failure must be recorded as new replay-visible relationships or status evidence, not as mutation of the id.

## Non-Goals

This ADR does not implement:

- runtime chain id creation;
- runtime chain id propagation;
- replay migration;
- artifact schema migration;
- chain reconstruction command;
- dispatch runtime;
- invocation runtime;
- execution runtime;
- completion runtime.

## Consequences

Future runtimes can validate end-to-end lineage by checking one immutable identity across all chain-aware artifacts.

Prompt-to-worker-assignment proof becomes simpler and less dependent on manual reference traversal.

Existing runtimes remain valid but not fully chain-id-aware until upgraded.

Full end-to-end execution certification should wait until chain id propagation and reconstruction are implemented.

## Known Gaps

- Existing runtime artifacts do not currently include `canonical_chain_id`.
- No `CANONICAL_CHAIN_ID_ARTIFACT_V1` runtime exists.
- No chain reconstruction command exists.
- No chain id migration or backfill plan is defined.
- Dispatch and invocation runtimes remain future work.

## Constitutional Alignment

The decision preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

AiGOL governs chain identity. Providers and workers cannot create or mutate identity. Replay records and reconstructs identity without becoming authority.
