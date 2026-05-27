# AIGOL_MINIMAL_RUNTIME_LOOP_V1

## Purpose

Formalize the minimal governed cognition runtime lifecycle that AiGOL now
operates. This document is **descriptive and constitutive** — it freezes
the lifecycle that is already implemented by existing milestones. It
introduces no new runtime feature, no new governance layer, and no new
execution authority.

## Minimal Runtime Loop

The minimal runtime loop is the single, bounded, deterministic, readonly
sequence:

```
human / operator request
    -> provider / raw cognition
        -> bounded extraction
            -> normalized cognition proposal
                -> governance review
                    -> authorization
                        -> routing
                            -> bounded execution
                                -> governed return
                                    -> replay evidence
```

Every stage produces immutable replay-visible evidence; every stage may
only progress to the next stage when the preceding stage has produced
deterministic evidence with a `NORMALIZED` / `REVIEWED` / `AUTHORIZED` /
`ROUTED` / `EXECUTED` / `ISOLATED` / `ACCEPTED` outcome, in that order.

## Lifecycle States

| Stage | Implementation | Allowed States |
| --- | --- | --- |
| operator request | [aigol/runtime/operator_cli.py](../aigol/runtime/operator_cli.py) — `RuntimeOperatorCLIEvidence` | `SUCCESS`, `REJECTED` |
| provider / raw cognition | [aigol/runtime/raw_provider_response_capture.py](../aigol/runtime/raw_provider_response_capture.py) — `RawProviderResponseEvidence` | `NORMALIZED`, `REJECTED`, `ABSENT` |
| bounded extraction | [aigol/runtime/bounded_extraction_layer.py](../aigol/runtime/bounded_extraction_layer.py) — `BoundedExtractionEvidence` | `NORMALIZED`, `REJECTED` |
| normalized cognition proposal | [aigol/runtime/bounded_llm_attachment_architecture.py](../aigol/runtime/bounded_llm_attachment_architecture.py) — `BoundedCognitionProposal` | constructed-or-fail-closed |
| governance review | [aigol/runtime/governed_cognition_review_gate.py](../aigol/runtime/governed_cognition_review_gate.py) — `GovernedCognitionReviewResult` | `REVIEWED`, `REJECTED` |
| authorization | [aigol/runtime/governed_contract_authorization_gate.py](../aigol/runtime/governed_contract_authorization_gate.py) — `ContractAuthorizationResult` | `AUTHORIZED`, `REJECTED` |
| routing | [aigol/runtime/governed_contract_router.py](../aigol/runtime/governed_contract_router.py) — `ContractRoutingResult` | `ROUTED`, `REJECTED` |
| bounded execution | [aigol/runtime/minimal_governed_execution_path.py](../aigol/runtime/minimal_governed_execution_path.py) — `MinimalGovernedExecutionPathResult` | `EXECUTED`, `REJECTED` |
| production isolation | [aigol/runtime/production_isolation_foundation.py](../aigol/runtime/production_isolation_foundation.py) — `ProductionIsolationEvidence` | `ISOLATED`, `REJECTED` |
| governed return | [aigol/runtime/governed_return_interpretation.py](../aigol/runtime/governed_return_interpretation.py) — `GovernedReturnInterpretationArtifact` | `ACCEPTED`, `REJECTED` |
| replay evidence | [aigol/runtime/transport/serialization.py](../aigol/runtime/transport/serialization.py) — canonical replay hashing | hashed, append-only |

## Allowed Transitions

Transitions are strictly linear and forward-only. The runtime allows
exactly the following progressions:

1. `operator request` → `raw cognition` (only if request is valid)
2. `raw cognition` → `bounded extraction` (always — even on raw rejection,
   evidence flows forward; only `NORMALIZED` raw evidence promotes a
   model-output dict)
3. `bounded extraction` → `normalized cognition proposal` (only on `NORMALIZED`)
4. `normalized cognition proposal` → `governance review` (only on successful construction)
5. `governance review` → `authorization` (only on `REVIEWED`)
6. `authorization` → `routing` (only on `AUTHORIZED`)
7. `routing` → `bounded execution` (only on `ROUTED`)
8. `bounded execution` → `production isolation` (only on `EXECUTED`)
9. `production isolation` → `governed return` (only on `ISOLATED`)
10. `governed return` → `replay evidence` (only on `ACCEPTED`)

Any deviation from this sequence — including backward jumps, re-entry,
re-tries, branching, or parallelism — is **disallowed** and a
fail-closed boundary violation.

## Fail-Closed Boundaries

- Any stage that fails for any reason emits a `REJECTED` evidence artifact
  and the loop terminates at that stage. No subsequent stage may
  fabricate evidence or recover state.
- Construction-time invariants (`__post_init__` validators) reject any
  malformed or mismatched-hash evidence at the type boundary.
- Hash continuity is enforced: every evidence artifact carries a
  `sha256:`-prefixed canonical hash that is verified on
  reconstruction (`from_dict`) and on lineage replay.
- The bounded extraction layer performs one-shot strict JSON + schema
  validation only; no permissive parsing of any kind is permitted.

## Replay Continuity

- Every stage's evidence is round-trippable via `to_dict()` / `from_dict()`
  with hash equality.
- Every stage exposes a `reconstruct_*_lineage(...)` function that
  produces a deterministic, append-only, duplicate-free, monotonically
  ordered lineage view with its own `lineage_hash`.
- The connector evidence carries `raw_response_evidence_hash` and
  `extraction_evidence_hash` linking the provider boundary into the
  bounded extraction lineage.
- The rejection analyzer
  ([aigol/runtime/live_cognition_rejection_analysis.py](../aigol/runtime/live_cognition_rejection_analysis.py))
  surfaces lineage continuity across every stage in a single
  replay-visible diagnostic artifact.

## Governance Authority Separation

- Every replay-visible evidence artifact carries
  `governance_authority_separated = True`.
- Provider adapters carry no governance authority; they only emit
  bounded normalized evidence.
- AiGOL core consumes only `BoundedCognitionProposal` artifacts past
  the extraction boundary.
- Authority is conferred only by the explicit governance gates
  (review, authorization, routing); no other stage may grant authority.

## No Autonomous Execution

- The runtime executes only when an operator request arrives.
- No stage is allowed to retry, retrigger, schedule, defer, or spawn
  any other invocation.
- No background loop, queue, scheduler, async task, thread, or
  subprocess is part of the minimal runtime loop.
- The only execution side effect is the bounded readonly
  `metadata_inspection_provider.inspect_runtime` operation.

## Boundary

This document freezes the minimal runtime loop in its current shape.
The loop is implemented, governed, replay-visible, fail-closed,
deterministic, readonly, single-pass, and provider-agnostic at its
core. It is the formal reference against which any future runtime
change must be measured.
