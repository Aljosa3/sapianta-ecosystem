# AIGOL_REPLAY_IMPROVEMENT_AUTHORIZATION_POLICY_BOUNDARY_V1

## Status

Certified policy boundary.

## Purpose

Define the authority boundary between canonical execution authorization and
replay-derived scoped improvement approvals.

This artifact does not implement runtime behavior, create approvals, authorize
execution, invoke providers, invoke workers, mutate replay, or mutate
governance.

## Certified Policy

Replay-derived scoped approvals may authorize candidate staging only.

Candidate staging includes:

- creating a governed implementation request;
- creating a worker request;
- creating a worker dispatch candidate;
- creating a worker invocation candidate;
- creating a worker execution candidate.

Candidate staging does not authorize final worker execution, provider
execution, repository mutation, governance mutation, or replay mutation.

## Final Execution Rule

Final worker or provider execution from a replay-derived improvement path
requires one of the following:

1. canonical `EXECUTION_AUTHORIZATION_ARTIFACT_V1`; or
2. an explicitly certified authorization-equivalent scoped execution boundary.

Scoped approvals must not silently replace canonical execution authorization.

## Authorization-Equivalent Scoped Execution Boundary

An authorization-equivalent scoped execution boundary must be explicit,
replay-visible, human-authorized, hash-bound, fail-closed, and limited to one
named execution candidate.

It must include or be bound to:

- source replay references and hashes;
- improvement intent reference and hash;
- PPP candidate reference and hash;
- implementation request reference and hash;
- worker request reference and hash;
- worker execution candidate reference and hash;
- human authorizing actor;
- approval or authorization timestamp;
- approval or authorization scope;
- execution capability allowed;
- forbidden operations;
- validity or expiration semantics;
- revocation or invalidation semantics;
- provider and worker authority constraints;
- replay certification requirement.

The minimum marker for certification is:

```text
authorization_boundary_class =
  CANONICAL_EXECUTION_AUTHORIZATION
  | AUTHORIZATION_EQUIVALENT_SCOPED_EXECUTION
  | CANDIDATE_STAGING_ONLY
```

An artifact with `authorization_boundary_class = CANDIDATE_STAGING_ONLY` must
not be consumed as final execution authority.

An artifact with
`authorization_boundary_class = AUTHORIZATION_EQUIVALENT_SCOPED_EXECUTION`
must also carry an explicit certification reference proving that the scoped
boundary preserves the canonical execution authority properties.

## Current Replay-Derived Approval Classification

Current replay-derived scoped approval artifacts are constitutionally valid for
candidate staging.

The final scoped approval used by the governed worker execution path is not
certified as authorization-equivalent by this policy boundary until it carries
an explicit authorization boundary marker or is replaced by canonical
`EXECUTION_AUTHORIZATION_ARTIFACT_V1`.

Therefore, current final execution approval remains a scoped runtime approval,
not a silent replacement for canonical execution authorization.

## Authority Guarantees

Replay may not authorize execution.

Improvement intent may not authorize execution.

PPP candidate evidence may not authorize execution.

Provider output may not authorize execution.

Worker identity may not authorize execution.

Human approval may authorize only the exact scope recorded in the approved
artifact.

Execution authority must remain explicit, bounded, replay-visible,
non-recursive, non-transferable, and fail-closed.

## Replay Guarantees

All replay-derived improvement authorization paths must preserve:

- append-only replay evidence;
- source replay references;
- source replay hashes;
- canonical chain continuity;
- approval or authorization lineage;
- worker target lineage;
- result validation lineage;
- replay certification lineage.

Missing or corrupt lineage must fail closed.

## Self-Authorization Prohibition

No replay-derived improvement path may self-authorize.

No provider, worker, replay artifact, improvement intent, proposal, candidate,
or runtime state may authorize itself or authorize future execution by
implication.

## Risk Disposition

Before this policy boundary, the governance risk was medium because scoped
approval and canonical execution authorization could be confused.

After this policy boundary, the governance risk is reduced to medium-low while
the final execution marker remains absent.

The remaining risk is resolved only when final worker/provider execution either
uses canonical `EXECUTION_AUTHORIZATION_ARTIFACT_V1` or emits an explicitly
certified authorization-equivalent scoped execution boundary marker.

## Constitutional Rule

```text
Scoped approval may stage candidates.
Scoped approval does not silently replace execution authorization.
Final execution requires canonical authorization or certified equivalence.
Replay observes.
Human authorizes.
AiGOL governs.
Worker executes only after explicit authority.
```
