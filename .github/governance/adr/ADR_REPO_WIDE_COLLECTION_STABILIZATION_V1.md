# ADR: Repo-Wide Collection Stabilization v1

## Context

Repo-wide pytest collection was failing before tests could be enumerated deterministically. That blocked global governance certification because the repository could not reliably distinguish collection topology failures from real test execution failures.

Before stabilization, the certification substrate was epistemically unstable: generated runtime artifacts, nested project surfaces, optional dependency gaps, and import topology issues could crash collection before governance evidence could be evaluated.

After stabilization, root collection topology is deterministic and certifiable:

- `python -m pytest --collect-only` collects `398` tests.
- One legacy optional credit constitutional flow is explicitly skipped because the old optional `sapianta_core` proposal API is absent.
- Collection crashes are `0`.

## Decision

Finalize `REPO_WIDE_TEST_COLLECTION_STABILIZATION_V1` as the first canonical AGOL certification substrate epoch.

The finalized scope is collection integrity only. This ADR does not certify full repo execution correctness.

## Collection Failure vs Execution Failure

Collection failure means pytest cannot enumerate tests reliably. It is a substrate problem.

Execution failure means tests collect and then fail during assertion or runtime artifact checks. It is not hidden by this milestone.

Full repo execution currently reports `51` `TEST_EXECUTION_FAILURES`, primarily in `sapianta-domain-trading` governance artifact checks. These remain visible and are not reclassified as collection failures or collection success.

## Optional Dependency Governance

Optional dependency absence must not crash unrelated governance collection. Optional handling must be source-specific, explicit, and documented.

Broad optional skips are forbidden because they hide certification scope and weaken governance evidence.

## Stale Artifact Governance

Generated runtime artifacts, quarantine surfaces, cache files, and nested virtualenvs are not source tests for root governance collection. They are excluded through targeted collection topology, not deleted or silently repaired.

The stale artifact guard remains non-destructive by default and requires human approval before removal.

## Entropy Observability Rationale

Passive entropy observability records deterministic baseline metrics for future AGOL execution-efficiency analysis, including repo-wide scan frequency, repeated collect-only loops, regeneration cycles, and reasoning repetition.

This observability is read-only and non-authoritative. It does not optimize prompts, route providers, alter execution, or influence governance decisions.

## Fail-Closed Philosophy

Unknown blockers are not silently ignored. Real execution failures are not hidden. Collection stabilization may certify only collection determinism.

Honest classification matters because future provider abstraction, execution envelopes, replay benchmarking, and entropy reduction claims must compare against a trustworthy baseline.

## Consequences

Positive:

- Repo-wide collection is deterministic.
- Governance certification can distinguish collection crashes from execution failures.
- Optional dependency and stale artifact surfaces are explicit.
- Passive entropy baseline evidence exists for future analysis.
- Future milestones have a stable replay-safe certification reference.

Tradeoffs:

- Full repo execution is still not green.
- Domain artifact failures remain visible.
- Certification language must remain precise.

## Explicit Non-Goals

- Provider abstraction.
- Execution envelopes.
- Runtime optimization.
- Token optimization.
- Execution routing.
- Orchestration.
- Bridge semantic changes.
- Governance behavior changes.
- Reclassifying execution failures as collection success.
