# READ_ONLY_ENVELOPE_VALIDATOR_PLAN_V1

## Status

Draft validation design.

## Purpose

This plan defines a read-only validator for operational loop envelopes. The
validator verifies envelope references without mutating task packages, result
packages, replay records, lifecycle state, sidepanel state, or any referenced
artifact.

This is plan, specification, and validation design only. It does not implement
runtime behavior, execution, orchestration, automatic dispatch, schema mutation,
semantic autonomy, or authority expansion.

## References

- `.github/governance/fixtures/OPERATIONAL_LOOP_ENVELOPE_FIXTURE_V1.json`
- `.github/governance/review/OPERATIONAL_LOOP_ENVELOPE_FIXTURE_REVIEW_V1.md`
- `.github/governance/specs/OPERATIONAL_LOOP_PACKAGE_MAPPING_V1.md`
- `.github/governance/specs/OPERATIONAL_LOOP_CONTRACT_V1.md`
- `.github/governance/finalize/FINALIZE_AGOL_BRIDGE_RUNTIME_FOUNDATION_V1.md`

## 1. Validator Purpose

The validator verifies:

- envelope references;
- package hashes;
- replay references;
- lifecycle references;
- authority boundary statement;
- semantic interpretation boundary;
- next-step reference is not approval;
- no referenced artifact is rewritten.

The validator produces a read-only validation report. It does not repair,
rewrite, normalize, dispatch, approve, execute, or persist changes.

## 2. Read-Only Validation Scope

The validator may read:

- envelope fixture or envelope package;
- referenced task package;
- referenced result package;
- replay records;
- lifecycle evidence;
- finalize or evidence artifacts if referenced.

The validator must not:

- write artifacts;
- mutate replay;
- mutate lifecycle;
- dispatch execution;
- approve execution;
- normalize results;
- call providers;
- update sidepanel state;
- create hidden persistence.

## 3. Validation Checks

Required checks:

1. Required envelope fields are present.
2. Envelope hash is deterministic and matches canonical envelope content.
3. Referenced task package exists.
4. Referenced result package exists when result reference is declared.
5. Referenced replay records exist.
6. Task and result package hashes match referenced hashes.
7. Lifecycle references are consistent with replay records and allowed states.
8. Authority boundary statement preserves cognition / governance / execution
   separation.
9. Semantic interpretation boundary states semantic reasoning is
   non-deterministic and non-authoritative.
10. Next-step synthesis is not marked as approval.
11. Provider boundary confirms provider executes only through governed transport.
12. Referenced artifacts are read without rewrite or mutation.

## 4. Failure Semantics

Validator status values:

- `VALID`
- `INVALID_SCHEMA`
- `MISSING_REFERENCE`
- `HASH_MISMATCH`
- `AUTHORITY_BOUNDARY_VIOLATION`
- `REPLAY_REFERENCE_INVALID`
- `LIFECYCLE_REFERENCE_INVALID`
- `SEMANTIC_REPLAY_OVERCLAIM`
- `NEXT_STEP_APPROVAL_CONFUSION`

Failure handling is report-only. A failed validation report may recommend
quarantine, repair review, or blocked implementation planning, but the validator
itself must not move or mutate artifacts.

## 5. Output Contract

The read-only validation report must include:

- `validation_id`
- `envelope_id`
- `status`
- `checks`
- `missing_references`
- `hash_mismatches`
- `authority_findings`
- `replay_findings`
- `lifecycle_findings`
- `semantic_findings`
- `recommended_action`

The report must be deterministic. If a future implementation writes reports,
that write must be governed by a separate milestone and must not mutate source
artifacts.

## 6. Governance Guarantees

The validator design certifies:

- no mutation;
- no execution;
- no approval;
- no dispatch;
- no provider calls;
- no replay rewrite;
- no lifecycle transition;
- no hidden persistence;
- no sidepanel mutation;
- no schema mutation;
- no authority expansion.

## Recommended Next Step

Create a bounded implementation review for a pure function validator that
accepts an envelope and an explicit read-only artifact map, then returns an
in-memory validation report. Do not add filesystem writes, runtime endpoints, or
sidepanel integration in the first implementation.
