# CANONICAL_CHAIN_ID_MODEL_V1

## Artifact

The canonical chain identity artifact is:

`CANONICAL_CHAIN_ID_ARTIFACT_V1`

It records the immutable chain identity created by AiGOL governance at chain opening.

## Required Fields

```json
{
  "artifact_type": "CANONICAL_CHAIN_ID_ARTIFACT_V1",
  "canonical_chain_id": "string",
  "chain_opened_by": "AiGOL",
  "chain_opened_at": "RFC3339 timestamp",
  "human_prompt_reference": "string",
  "source_router_reference": "string",
  "source_router_hash": "string",
  "chain_scope": "EXECUTION_GOVERNANCE",
  "chain_status": "OPENED",
  "parent_chain_id": null,
  "supersedes_chain_id": null,
  "replay_reference": "string",
  "artifact_hash": "string"
}
```

## Chain ID Format

Recommended deterministic format:

```text
CHAIN-<DATE>-<STABLE_HASH_PREFIX>
```

The stable hash input should include:

- human prompt reference;
- source router reference;
- source router hash;
- chain opening timestamp;
- chain scope;
- AiGOL runtime identity;
- replay reference.

The hash input must not include provider secrets, API keys, hidden runtime state, or non-deterministic process identifiers.

## Required Propagation Field

Future chain-aware artifacts must include:

```json
{
  "canonical_chain_id": "string"
}
```

This field must match `CANONICAL_CHAIN_ID_ARTIFACT_V1.canonical_chain_id`.

## Required Future Chain-Aware Artifacts

The following future or upgraded artifacts must carry `canonical_chain_id`:

- `SOURCE_OF_TRUTH_ROUTER_SELECTION_ARTIFACT_V1` when proposal lifecycle is selected;
- `PROPOSAL_RUNTIME_ARTIFACT_V1`;
- `PROPOSAL_APPROVAL_ARTIFACT_V1`;
- `EXECUTION_REQUEST_ARTIFACT_V1`;
- `READY_FOR_DISPATCH_ARTIFACT_V1`;
- `WORKER_ASSIGNMENT_ARTIFACT_V1`;
- `DISPATCH_ARTIFACT_V1`;
- `WORKER_INVOCATION_ARTIFACT_V1`;
- future worker execution artifacts;
- future worker result artifacts;
- future worker termination artifacts;
- future chain reconstruction reports.

Reusable worker registration may remain outside a single chain. Chain-scoped worker assignments must carry the chain id.

## Valid Chain Statuses

The identity artifact recognizes:

- `OPENED`;
- `CANCELLED`;
- `EXPIRED`;
- `SUPERSEDED`;
- `COMPLETED`;
- `FAILED`.

The foundation defines the vocabulary only. Existing runtime does not implement these transitions.

## Parent And Supersession Semantics

`parent_chain_id` is used only when a governed child chain is intentionally created from an existing chain.

`supersedes_chain_id` is used only when a new chain replaces a prior chain.

Both relationships require replay-visible evidence.

Neither relationship may mutate the original chain id.

## Reconstruction Index

A future read-only chain reconstruction report may emit:

```json
{
  "canonical_chain_id": "string",
  "human_prompt_reference": "string",
  "router_reference": "string",
  "proposal_reference": "string",
  "approval_reference": "string",
  "execution_request_reference": "string",
  "readiness_reference": "string",
  "worker_assignment_reference": "string",
  "dispatch_reference": "string",
  "invocation_reference": "string",
  "terminal_reference": "string",
  "chain_reconstruction_hash": "string"
}
```

This report must be derived from replay. It must not create authority or repair missing artifacts.

## Invalid Models

AiGOL must reject:

- missing `canonical_chain_id`;
- empty chain id;
- chain id created by Provider;
- chain id created by Worker;
- chain id created by Replay;
- mismatched chain ids between parent and child artifacts;
- chain id mutation;
- chain id reuse across unrelated prompts;
- hidden chain relationships;
- chain reconstruction that ignores corrupt artifact hashes.

## Model Classification

The model is ready as a foundation for future runtime propagation and chain reconstruction.
