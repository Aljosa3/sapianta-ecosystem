# UX_SIMPLIFICATION_AND_EVIDENCE_CLARITY_V1

## Status

Draft specification.

## Purpose

This specification defines governance cognition compression for the Browser
Companion cockpit. It reduces operator cognition load while preserving
governance evidence, replay visibility, continuity semantics, lineage
visibility, artifact inspection, and authority boundaries.

This is operator clarity optimization, evidence hierarchy refinement, compact
governance state presentation, and progressive disclosure design. It is not
frontend redesign, visual polish, provider dispatch, execution runtime,
orchestration, durable replay backend, or semantic authority expansion.

## Design Principle

Compress first. Inspect second. Never erase evidence.

The cockpit should help an operator understand safety, integrity, replay scope,
continuity visibility, and authority scope within seconds, then allow deeper
inspection without changing behavior or hiding governance evidence.

## 1. Executive Governance Layer

The top-level operator layer must use compact governance states before detailed
artifact panels.

Preferred compact states:

- `SAFE_REVIEW_ONLY`
- `BLOCKED`
- `INTEGRITY_VERIFIED`
- `SESSION_REPLAY_ONLY`
- `CONTINUITY_VISIBLE`

The executive layer must answer:

- current safety state;
- artifact integrity state;
- replay scope;
- continuity visibility;
- authority scope.

The layer must remain deterministic, read-only, and non-authoritative. It must
not imply approval, dispatch, execution, semantic correctness, durable replay,
or autonomous continuation.

## 2. Evidence Hierarchy

Evidence must be disclosed progressively.

### Level 1: Compact Operator Summary

Level 1 presents:

- current governance state;
- hash/integrity state;
- replay scope;
- continuity visibility;
- authority statement;
- blocking reason when blocked.

The operator should not need raw JSON to understand the current state.

### Level 2: Governance Findings

Level 2 presents:

- validation findings;
- hash verification findings;
- continuity findings;
- replay/lifecycle findings;
- authority findings;
- recommended operator next step.

This level is still human-readable and should avoid raw artifact dumps unless
the operator expands them.

### Level 3: Full Artifact Inspection

Level 3 preserves:

- semantic proposal artifact;
- validation artifact;
- hash verification artifact;
- continuity report artifact;
- replay summary artifact;
- lifecycle summary artifact;
- lineage summary artifact;
- authority and semantic boundary artifacts.

This level may contain canonical JSON. It must remain available, deterministic,
and read-only.

## 3. Semantic Clarification Rules

The cockpit must prevent the following confusions:

`HASH_VERIFIED` means artifact integrity only. It does not mean semantic
correctness, truth, quality, safety, approval, or execution readiness.

`CERTIFIED_FOR_CONTINUITY_INGESTION` means the proposal is suitable for
continuity ingestion. It does not mean approval, dispatchability, execution
authorization, semantic authority, or autonomous continuation.

`CONTINUITY_VALID` means continuity evidence is visible and internally valid for
review. It does not mean execution authorization, provider dispatch, approval,
or next-step authorization.

`REPLAY_VISIBLE` means replay evidence is visible. In the current bridge
runtime, replay is session-local unless a future durable replay backend
milestone explicitly exists.

## 4. Replay Simplification

Replay language must be compressed into a single first-level statement:

`SESSION_REPLAY_ONLY`

Required meaning:

- replay is session-local;
- replay is read-only;
- replay is visibility-only;
- replay is not durable;
- replay is not a ledger write;
- replay is not mutation;
- replay is not repair.

Detailed replay timeline, replay session, and replay artifact views should move
behind progressive disclosure so the operator first sees scope, then evidence.

## 5. Authority Compression

Authority language must be compressed into one first-level statement:

`SEMANTIC_TRANSPORT_ONLY: no approval, no dispatch, no execution, no provider
call, no orchestration, no autonomous continuation.`

Detailed authority evidence remains available below the compact statement.
Repeated authority labels may remain in raw artifacts, but the operator should
not have to read every panel to understand authority scope.

## 6. UX Safety Constraints

The simplification must preserve:

- deterministic rendering;
- read-only rendering;
- replay-safe visibility;
- lineage visibility;
- artifact inspection;
- fail-closed semantics;
- explicit boundary labels;
- semantic cognition/governance/execution separation.

The simplification must not introduce:

- hidden abstraction;
- authority ambiguity;
- evidence removal;
- silent behavior;
- automatic continuation;
- semantic inference;
- inferred approval;
- inferred replay durability;
- lifecycle mutation;
- replay mutation.

## 7. Review Targets

The implementation review for this specification must evaluate:

- cockpit density;
- duplicated labels;
- cognitive overload;
- governance readability;
- operator trust clarity;
- evidence discoverability;
- whether compact states preserve the underlying evidence;
- whether raw artifacts remain accessible;
- whether authority labels are clearer, not weaker.

## Governance Clarity Improvements

Expected improvements:

- faster operator orientation;
- fewer competing "green check" concepts;
- clearer separation between integrity, certification, continuity, replay, and
  authority;
- less replay terminology overlap;
- one primary authority statement before expanded evidence;
- preserved audit-grade inspection path.

## Remaining Risks

- Compact states may hide nuance if implemented without expandable evidence.
- Operators may still over-trust `INTEGRITY_VERIFIED`.
- Session-local replay requires persistent labeling until durable replay exists.
- Too much compression could weaken constitutional visibility.

## Recommended Next Step

Implement a sidepanel-only `UX_SIMPLIFICATION_AND_EVIDENCE_CLARITY_V1` pass that
adds the executive governance layer and evidence hierarchy without removing raw
artifact inspection or changing runtime behavior.
