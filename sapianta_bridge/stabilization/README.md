# Repo-Wide Test Collection Stabilization v1

This package documents and supports deterministic pytest collection stabilization for SAPIANTA.

The milestone exists because full repository pytest collection previously failed before governance milestones could be globally certified. The goal is honest collection stability, not making broken tests pass dishonestly.

## Blocker Classification

Collection blockers are classified as:

- `OPTIONAL_DEPENDENCY`: optional or domain-specific dependencies missing from the active environment.
- `STALE_GENERATED_ARTIFACT`: generated tests, cache files, or runtime quarantine artifacts collected accidentally.
- `NESTED_PROJECT_SURFACE`: virtualenvs or embedded project surfaces not intended for root collection.
- `IMPORT_TOPOLOGY`: package layout or import path issues.
- `REAL_TEST_FAILURE`: valid tests that fail during execution, not collection.
- `UNKNOWN`: anything uncertain; requires manual review.

## Optional Dependency Policy

Optional dependencies may be handled with source-specific import guards, explicit package paths, or documented markers. Core governance tests must not be skipped as optional, and broad skip strategies are forbidden.

## Stale Artifact Policy

Generated runtime artifacts and cache files are detected non-destructively. The guard reports candidates and requires human approval before removal. It does not delete files automatically.

## Passive Execution Entropy Observability

`entropy_observability.py` records deterministic passive metrics for future AGOL execution-efficiency analysis. It measures repo-wide scan frequency, collect-only loops, regeneration cycles, reasoning repetition, and token-heavy patterns.

This observability is passive-only. It does not optimize prompts, reroute providers, mutate memory, influence governance, or affect execution.

## Collection Failure vs Test Execution Failure

Collection failure means pytest cannot enumerate tests reliably. Test execution failure means tests collect but assertions or runtime dependencies fail during execution. This milestone stabilizes collection first so those failure types stay distinct.

## Future Maintenance

New generated runtime surfaces must be added to targeted collection ignores only when they are not source tests. Optional dependency guards must remain source-specific and documented.
