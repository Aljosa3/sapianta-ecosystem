# G27-09 — Platform Validation Plan-to-Candidate Composition

Status: IMPLEMENTED AND DETERMINISTICALLY VERIFIED

Date: 2026-07-13

## Purpose

G27-09 implements one bounded Platform Core transition:

`PLATFORM_VALIDATION_PLAN_ARTIFACT_V1 -> existing validation candidate artifact`

It constructs exactly one existing single-command candidate for one exact
allowlisted command reference or exactly one existing suite candidate for two
or more ordered references. It does not approve or execute either candidate.

## Runtime

- `aigol/runtime/platform_validation_plan_candidate_composition_runtime.py`
- composition evidence:
  `PLATFORM_VALIDATION_CANDIDATE_COMPOSITION_ARTIFACT_V1`
- registry capability:
  `PLATFORM_VALIDATION_PLAN_TO_CANDIDATE_COMPOSITION`

The runtime exposes composition, composition-artifact validation, and replay
reconstruction operations.

## Source Binding

Only a valid, non-failed `PLATFORM_VALIDATION_PLAN_ARTIFACT_V1` is accepted.
The runtime verifies:

- canonical plan validation and artifact identity;
- the supplied plan reference against `validation_plan_id`;
- the supplied artifact hash against the canonical plan artifact hash;
- the supplied plan hash against `platform_validation_plan_hash`;
- every requirement as mandatory and replay-hash bound;
- every command identifier, allowlist version, and command specification hash;
- the exact-mapping declaration produced by G27-07.

A plan with mandatory requirements and no exact allowlisted command reference
fails closed. The runtime never infers a command from requirement prose.

## Existing Candidate Reuse

For one reference, G27-09 delegates unchanged to
`create_governed_validation_candidate(...)`.

For two or more references, G27-09 delegates unchanged to
`create_governed_validation_suite_candidate(...)`. The plan reference order is
used as suite command order. The existing candidate validators then rebind the
constructed artifacts to the current Validation Allowlist.

No duplicate candidate implementation, command parser, Worker request, or
execution coordinator is introduced.

## Purpose and Lineage

Each candidate receives deterministic validation-purpose text derived from the
allowlisted command identifier and ordered mandatory requirement identifiers.
Its associated reference binds:

- plan identifier, artifact hash, and plan hash;
- source Platform Change Impact reference and hash;
- ordered requirement identifiers and hashes;
- the exact command reference and its deterministic hash.

The suite envelope also binds the same plan lineage.

## Replay and Hashing

One composition artifact is persisted under
`platform_validation_candidate_composition_recorded`. Reconstruction verifies
the wrapper hash, composition hash, embedded candidate hash, candidate type,
candidate cardinality, and all existing candidate invariants.

## Constitutional Boundary

G27-09 only constructs candidate artifacts. It does not:

- execute validation or invoke the Validation Command Worker;
- create human approval or Governance authorization;
- invoke Providers;
- mutate the repository;
- certify results;
- synthesize commands or argv;
- expand the Validation Allowlist.

The existing governed validation runtimes remain downstream and require their
existing approval and authorization artifacts.

## Known Limitation

Candidate construction is possible only where G27-07 produced at least one
exact allowlisted command reference. Semantic requirements without such a
reference remain visible but fail closed at this transition.
