# AIGOL_FIRST_REAL_OPERATION_V1

## Purpose

Formalize what qualifies as the **first real operational AiGOL flow**:
the canonical single end-to-end pass through the minimal governed
cognition runtime from human to memory.

This document is **descriptive and constitutive** — it freezes the
criteria for "first real AiGOL operation" against the runtime that is
already implemented. It introduces no new flow, no orchestration, and
no write capability.

## Canonical Flow

```
human
    -> cognition
        -> governance
            -> execution
                -> return
                    -> memory
```

Mapped to the live implementation:

| Stage | Artifact / Function |
| --- | --- |
| human | operator prompt to `python -m aigol.runtime.operator_cli "..."` |
| cognition | raw provider response captured into `RawProviderResponseEvidence`, then normalized through `extract_bounded_cognition_proposal` into `BoundedCognitionProposal` |
| governance | `review_translated_cognition_candidate` (`REVIEWED`), `authorize_governed_execution_contract` (`AUTHORIZED`), `route_authorized_contract` (`ROUTED`) |
| execution | `execute_minimal_governed_path` (`EXECUTED`), bounded readonly `metadata_inspection_provider.inspect_runtime` only |
| return | `validate_production_isolation` (`ISOLATED`), `interpret_governed_execution_return` (`ACCEPTED`) |
| memory | append-only replay lineage at every layer (see `AIGOL_MINIMAL_CONSTITUTIONAL_MEMORY_V1`) |

## What Qualifies as First Real AiGOL Operation

A flow qualifies as a **first real AiGOL operation** when **all** of the
following are simultaneously true:

1. A human operator submits a single textual request via the operator CLI surface.
2. The provider adapter receives a raw response and captures it into
   `RawProviderResponseEvidence` with `raw_response_present = True`.
3. The bounded extraction layer emits
   `BoundedExtractionEvidence(extraction_status = NORMALIZED,
   extraction_stage = BOUNDED_NORMALIZATION,
   normalization_failure_type = NONE, schema_failure_type = NONE)`.
4. A `BoundedCognitionProposal` is constructed for the
   `metadata_inspection_provider` capability with a
   `contract:`-prefixed `proposed_contract_reference`.
5. The governance review gate emits
   `GovernedCognitionReviewResult(review_status = REVIEWED)`.
6. The authorization gate emits
   `ContractAuthorizationResult(status = AUTHORIZED)` against an
   explicit session policy that allows only
   `metadata_inspection_provider` / `inspect_runtime`.
7. The router emits
   `ContractRoutingResult(status = ROUTED, attached = True)`.
8. The bounded execution path emits
   `MinimalGovernedExecutionPathResult(execution_status = EXECUTED)`
   for `metadata_inspection_provider.inspect_runtime`.
9. Production isolation emits
   `ProductionIsolationEvidence(isolation_status = ISOLATED)`.
10. The governed return interpreter emits
    `GovernedReturnInterpretationArtifact(return_status = ACCEPTED)`
    whose `normalized_return_summary` begins with
    `operation=inspect_runtime`.
11. The operator CLI evidence emits
    `RuntimeOperatorCLIEvidence(cli_status = SUCCESS)` and the rendered
    output contains `status=SUCCESS`.
12. Every artifact above carries a canonical `evidence_hash`, round-trips
    via `from_dict`/`to_dict`, and reconstructs into a deterministic
    append-only lineage with `lineage_valid = True` and
    `governance_authority_separated = True`.

## Required Evidence Chain

The first real operation produces, in deterministic order:

1. `RawProviderResponseEvidence` (provider-agnostic)
2. `BoundedExtractionEvidence`
3. `BoundedCognitionProposal`
4. `LiveOpenAIRuntimeConnectorEvidence` (provider adapter only)
5. `RealOpenAIAPIInvocationEvidence` (provider adapter only)
6. `GovernedProposalTranslationResult`
7. `GovernedCognitionReviewResult`
8. `GovernedExecutionContract` (validated, attached)
9. `ContractAuthorizationResult`
10. `ContractRoutingResult`
11. `GovernedExecutionSession` with provider evidence attached
12. `MinimalGovernedExecutionPathResult`
13. `ProductionIsolationEvidence`
14. `GovernedReturnInterpretationArtifact`
15. `LiveRuntimeUsageValidationEvidence`
16. `RealRuntimeActivationEvidence`
17. `FirstRealOperatorUsageEvidence`
18. `RuntimeOperatorCLIEvidence`

Every adjacent pair must be hash-linked. Every reconstructor over the
chain must return `append_only_valid = True`, `lineage_valid = True`,
`governance_authority_separated = True`.

## Success Criteria

The first real operation **succeeds** iff:

- the operator CLI prints `status=SUCCESS`;
- the CLI exit code is `0`;
- the rejection analyzer applied to the live runtime usage record
  reports `rejection_stage = NONE` and
  `bounded_extraction_status = NORMALIZED`;
- the governed return summary begins with `operation=inspect_runtime`;
- every evidence artifact round-trips and the lineage hash is stable
  across repeated reconstruction.

## Rejection Criteria

The first real operation **fails closed** (does NOT qualify) iff any of:

- raw provider response absent or not captured;
- bounded extraction rejected (any `normalization_failure_type` other
  than `NONE`, or any `schema_failure_type` other than `NONE`);
- proposal construction fails closed;
- review / authorization / routing / execution / isolation / return
  emits `REJECTED` at any stage;
- the operator CLI prints `status=REJECTED`;
- any evidence artifact's `evidence_hash` does not match the canonical
  hash of its inputs;
- any lineage reconstruction reports
  `append_only_valid = False` or `lineage_valid = False`;
- any stage attempts to mutate provider state, runtime state, the
  filesystem, the network, or any external surface beyond the bounded
  readonly `metadata_inspection_provider.inspect_runtime` operation.

## Readonly Bounded Operation Scope

The first real operation is strictly bounded to:

- exactly one operator prompt;
- exactly one provider invocation;
- exactly one bounded proposal;
- exactly one governed execution contract;
- exactly one provider operation: `metadata_inspection_provider.inspect_runtime`;
- exactly one governed return.

## No Write Capability

The first real operation has **no** write capability:

- no filesystem mutation;
- no network write;
- no provider state mutation;
- no runtime state mutation;
- no shell execution;
- no subprocess spawn;
- no async / threaded / multiprocess execution;
- no agent behavior;
- no planning system invocation.

## No Orchestration

The first real operation is strictly single-pass:

- no scheduler;
- no retry loop;
- no fallback path;
- no multi-step planner;
- no autonomous re-triggering;
- no parallel branch;
- no background work.

## Boundary

This document freezes the criteria for the first real AiGOL operation.
Any future "first real operation" claim must satisfy every condition
listed here without exception, must produce the entire evidence chain
above with stable hashes, and must remain inside the readonly bounded
operation scope.
