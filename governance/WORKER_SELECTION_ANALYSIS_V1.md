# Worker Selection Analysis V1

Status: reconstruction-only selection analysis.

## Classification

`WORKER_SELECTION_STATUS`: `PARTIAL`

## Existing Selection Basis

AiGOL already defines capability-bound execution.

Evidence:

- Worker attachment binds to frozen read-only capabilities.
- Capability authorization mapping requires capability class, risk level, boundary state, authorization evidence, replay lineage, and fail-closed conditions.

This implies that a Worker may be selected by authorized capability binding.

## Not Yet Defined

AiGOL does not define:

- Worker selection algorithm
- domain-based Worker selection
- worker scoring
- worker preference
- worker fallback
- worker replacement
- multi-worker conflict resolution

## Capability-Based Selection

Capability-based selection is partially implied but not canonicalized.

Current artifacts allow this interpretation:

```text
authorized capability -> compatible Worker attachment
```

They do not define a general selection system.

## Finding

Worker selection is partial: capability binding exists, but multi-worker selection does not.

## Genuine Gap

If more than one Worker can satisfy a capability, AiGOL needs a canonical deterministic selection rule before implementation.
