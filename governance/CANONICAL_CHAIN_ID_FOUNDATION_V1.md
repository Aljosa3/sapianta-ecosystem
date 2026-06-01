# CANONICAL_CHAIN_ID_FOUNDATION_V1

## Purpose

Define a single immutable chain identity spanning the AiGOL execution governance path:

```text
Human Prompt
  -> Proposal
  -> Approval
  -> Execution Request
  -> Ready For Dispatch
  -> Worker Assignment
```

This foundation closes the largest architectural gap identified by `END_TO_END_EXECUTION_CHAIN_VALIDATION_V1`: the absence of a canonical chain identity binding every stage into one replay-visible lineage.

## Scope

This is a review-only identity foundation.

It does not:

- modify runtime;
- modify replay;
- modify existing artifacts;
- implement chain id propagation;
- implement a chain reconstruction command;
- implement dispatch, invocation, execution, or completion.

## Definition

A canonical chain id is an immutable identifier for one governed execution chain.

It identifies the lineage that begins with a human prompt intent entering AiGOL and continues through governance artifacts until the chain terminates, is cancelled, expires, or proceeds to future execution stages.

## What Creates A Chain ID?

AiGOL governance creates the chain id.

It must not be created by:

- Provider;
- Worker;
- Replay;
- Human acting directly outside AiGOL governance;
- CLI transport alone;
- proposal artifact;
- approval artifact;
- execution request artifact;
- automatic retry logic.

The human prompt may trigger chain opening, but AiGOL creates the canonical identity.

## When Is It Created?

The chain id is created at chain opening.

Recommended creation point:

```text
Human Prompt Accepted
  -> Source Of Truth Router Selection
  -> CANONICAL_CHAIN_OPENED
  -> Proposal Creation
```

If a prompt never becomes proposal-eligible, no execution chain id is required.

If a conversation response does not create a proposal, it remains a conversation lineage, not an execution chain.

## Which Artifacts Must Contain It?

Future chain-aware artifacts must include:

- source router selection artifact when proposal lifecycle is selected;
- proposal artifact;
- approval artifact;
- execution request artifact;
- ready-for-dispatch artifact;
- worker artifact only when identity is created specifically for chain-scoped work;
- worker assignment artifact;
- future dispatch artifact;
- future worker invocation artifact;
- future execution result and termination artifacts.

Worker registration artifacts may remain global if workers are reusable. Worker assignment must contain the chain id because assignment binds a worker to a specific chain.

## Can It Ever Change?

No.

`canonical_chain_id` is immutable.

If a chain must be superseded, AiGOL must create a new chain id and record a replay-visible supersession relationship.

Allowed relationship:

```text
supersedes_chain_id
```

Forbidden behavior:

```text
mutating canonical_chain_id in place
reusing a chain id for unrelated prompt lineage
merging unrelated chains without replay-visible governance
splitting a chain without child chain evidence
```

## Reconstruction

Replay reconstructs the chain by:

1. locating the `CANONICAL_CHAIN_OPENED` event;
2. reading the immutable `canonical_chain_id`;
3. traversing all artifacts that carry the same id;
4. verifying each artifact hash;
5. verifying each replay wrapper hash;
6. verifying stage order;
7. verifying reference and hash continuity between adjacent stages;
8. rejecting any artifact with a mismatched, missing, or mutated chain id.

Replay may reconstruct chain history.

Replay may not create or repair a missing chain id.

## Corruption Detection

Corruption is detected when:

- an artifact in the chain omits `canonical_chain_id`;
- an artifact contains a different chain id;
- an artifact hash does not match;
- a replay wrapper hash does not match;
- stage order is invalid;
- a child artifact references a parent from a different chain;
- duplicate chain ids are used for unrelated human prompt references;
- a supersession or child-chain relationship is asserted without replay evidence;
- provider or worker attempts to create or mutate chain identity.

Any corruption must fail closed.

## Replay Interaction

The chain id must be replay-visible.

Replay records:

- chain opening;
- chain-bearing artifact creation;
- stage transitions;
- supersession relationships where applicable;
- terminal chain outcome when defined.

Replay remains read-only and does not own identity authority.

## Constitutional Preservation

The chain id preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Mapping:

| Role | Chain identity meaning |
| --- | --- |
| LLM proposes | Provider evidence may be linked to a chain but cannot create or mutate chain identity |
| AiGOL governs | AiGOL creates and validates canonical chain identity |
| Worker executes | Workers receive chain-scoped assignments only after governance boundaries |
| Replay records | Replay records chain opening, propagation, and reconstruction evidence |

## Foundation Classification

`CANONICAL_CHAIN_ID_FOUNDATION_STATUS = READY_WITH_GAPS`

The identity model is defined, but existing runtimes do not yet propagate `canonical_chain_id` and no chain reconstruction command exists.
