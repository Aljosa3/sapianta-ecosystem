# Architectural Simplification Recommendations V1

Status: simplification recommendations only.

## Recommendation 1: Canonicalize Repeated Guarantees

Repeated guarantees should be reduced to references where possible:

- no execution authority
- no hidden continuation
- no autonomous mutation
- no orchestration activation
- fail-closed ambiguity
- replay-visible lineage
- explicit termination

Future artifacts should cite canonical guarantees instead of restating them unless the new layer changes the failure mode.

## Recommendation 2: Preserve Replay as the Only Continuity Spine

Do not create separate continuity engines for:

- semantic continuity
- identity continuity
- LLM participation
- orchestration lifecycle

These should remain interpretations of replay-visible lineage, not independent continuity substrates.

## Recommendation 3: Keep Orchestration Conceptual Until Runtime Need Is Proven

The orchestration boundary and lifecycle are constitutional models only.

Do not implement orchestration runtime, workers, agents, dispatch, or adaptive coordination without a separate pressure review and explicit replay-safe implementation gate.

## Recommendation 4: Compress Future Reviews

Future governance reviews should prefer concise findings over expanded doctrinal restatement.

Recommended structure:

- reviewed scope
- pass/fail/watchpoint findings
- simplification candidates
- replay centrality status
- non-activation certification

## Recommendation 5: Introduce Deprecation Language Before Adding Replacement Layers

If terminology becomes redundant, future work should mark concepts as:

- canonical
- alias
- deprecated
- superseded

This avoids parallel terminology inflation.

## Recommendation 6: Treat Evidence Volume as a Design Constraint

More artifacts are not automatically better governance.

Future governance work should justify:

- why a new artifact is needed
- what ambiguity it resolves
- why an existing artifact cannot carry the meaning
- how replay centrality is preserved

## Consolidation Recommendation

Proceed with caution.

The substrate remains coherent, but the next healthy move is semantic compression and canonical referencing before capability expansion.

