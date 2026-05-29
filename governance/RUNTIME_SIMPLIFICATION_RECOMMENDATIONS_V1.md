# Runtime Simplification Recommendations V1

Status: bounded simplification guidance before capability expansion.

This artifact records simplification opportunities only. It does not authorize runtime refactoring, capability expansion, orchestration, or agent behavior.

## Recommendation 1: Keep Capability Surface Frozen

Do not add a third capability until the first operator flow has remained stable through review and pressure validation.

Rationale:

- current read-only capabilities already prove two useful surfaces
- expansion before consolidation risks capability sprawl
- replay and authorization behavior should remain the focus

## Recommendation 2: Consider Replay Helper Consolidation Later

Replay helper patterns are repeated across:

- operator flow
- proposal bridge
- execution prototype
- read-only runtime inspection
- filesystem read-only inspection

Candidate shared helpers:

- replay wrapper persistence
- artifact hash verification
- replay wrapper hash verification
- failure artifact shape
- lifecycle reconstruction checks

Constraint:

Do not consolidate until behavior is stable enough that helper extraction will reduce complexity rather than obscure the fail-closed path.

## Recommendation 3: Preserve Explicit Layers For Now

The architecture has more layers than a minimal script, but each layer currently proves a different constitutional boundary:

- operator intent boundary
- proposal-only cognition boundary
- AiGOL validation and authorization boundary
- worker execution boundary
- replay evidence boundary

These should remain explicit until capability expansion pressure makes consolidation safer than repetition.

## Recommendation 4: Prefer Terminology Compression In Future Artifacts

Future docs should prefer:

- proposal
- governed execution request
- worker execution
- replay evidence

Avoid adding new synonyms for the same concepts.

## Recommendation 5: Expand Only After Pressure Review

Before adding additional capabilities, run a pressure review against:

- unauthorized proposal attempts
- malformed replay artifacts
- filesystem boundary violations
- hidden continuation attempts
- capability classification ambiguity

## Summary

The runtime should remain as-is for now. The next improvement should be review or pressure validation, not capability expansion.
