# Constitutional Acceptance Criteria

Status: constitutional governance finalization artifact.

## Required Constitutional Guarantees

A constitutional governance state is acceptable only if:

- canonical constitutional artifacts exist;
- L0-L4 layer semantics are defined;
- Layer 0 is identified as immutable;
- Layer 1 artifact definitions are identified as immutable;
- Layer 2 is restricted;
- Layer 3 is governed;
- Layer 4 is bounded and evolvable only inside allowed scopes;
- historical safety authority semantics are preserved separately from mutation layers.

## Required Enforcement Guarantees

Acceptance requires evidence for:

- freeze manifest coverage;
- protected path enforcement;
- mutation boundary enforcement;
- mutation layer classification;
- promotion gate presence;
- development governance gate presence;
- certification gate presence;
- replay verification presence.

Enforcement may be distributed, but missing or partial enforcement must be visible in conformance evidence.

## Required Replay Guarantees

Acceptance requires:

- replay-critical artifacts identified;
- replay verification surfaces identified;
- hash-chain or deterministic hash evidence where implemented;
- replay read-only semantics documented;
- replay limitations documented.

Replay evidence must not be silently synthesized.

## Required Evidence Guarantees

Acceptance requires:

- governance audit evidence;
- constitutional specification evidence;
- conformance report evidence;
- finalization manifest evidence;
- milestone certification evidence;
- known limitation evidence.

Evidence must be deterministic, reviewable, and stable under repeated inspection.

## Required Fail-Closed Guarantees

Acceptance requires fail-closed treatment for:

- missing constitutional artifacts;
- missing freeze evidence;
- missing protected path enforcement;
- missing certification gates;
- missing replay verification;
- invalid or incomplete conformance evidence;
- ambiguous mutation authority.

Fail-closed means the condition must be reported and must not be silently interpreted as conformance.

