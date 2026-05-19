# VALIDATOR_COMPOSITION_LAYER_V1

## Status

Draft composition specification and implementation plan.

## Purpose

This specification defines a bounded deterministic composition layer over
existing pure-function governance validators.

The layer composes explicitly declared validators in deterministic order and
returns an aggregate in-memory report. It preserves read-only semantics,
no-authority guarantees, replay-safe behavior, and validator isolation.

This is specification, planning, and constitutional boundary definition only.
It does not implement an orchestration runtime, autonomous execution, provider
routing, plugin runtime, dynamic loading, dispatch system, or approval engine.

## References

- `.github/governance/specs/READ_ONLY_ENVELOPE_VALIDATOR_PLAN_V1.md`
- `.github/governance/review/READ_ONLY_ENVELOPE_VALIDATOR_IMPLEMENTATION_REVIEW_V1.md`
- `.github/governance/finalize/FINALIZE_PURE_FUNCTION_ENVELOPE_VALIDATOR_V1.md`
- `.github/governance/specs/OPERATIONAL_LOOP_CONTRACT_V1.md`
- `.github/governance/specs/OPERATIONAL_LOOP_PACKAGE_MAPPING_V1.md`

## 1. Composition Model

The validator composition layer accepts:

- an envelope object;
- an explicit artifact map;
- an explicitly declared ordered validator list;
- optional read-only composition metadata.

The layer returns:

- an in-memory aggregate validation report;
- ordered per-validator validation reports;
- aggregate failure status;
- report-only recommended action.

Validators are invoked as pure functions. Each validator receives the same
read-only validation input or an explicitly declared projection of that input.
The composition layer does not discover validators, load validators dynamically,
repair artifacts, normalize results, dispatch execution, approve continuation,
or persist reports.

## 2. Validator Composition Contract

Each validator declaration must include:

- `validator_id`
- `validator_version`
- `validator_purpose`
- `validator_function_ref`
- `input_contract`
- `output_contract`
- `failure_statuses`
- `read_only_guarantee`
- `authority_boundary_guarantee`

The declaration is a governance-visible contract. It does not grant authority
to the validator or allow discovery outside the declared list.

Validator functions must:

- accept explicit in-memory inputs;
- return deterministic in-memory reports;
- avoid mutating inputs;
- avoid IO, provider calls, dispatch, approval, and runtime side effects;
- expose failure semantics as report data.

## 3. Validator Ordering Rules

Composition order is deterministic and explicit:

1. The caller provides a validator declaration list.
2. The composition layer preserves the declared order.
3. Duplicate `validator_id` values are invalid.
4. Missing validator declarations are invalid.
5. Unknown or undeclared validators are blocked.
6. Validators may not reorder themselves or request additional validators.

No auto-discovery, dynamic loading, plugin enumeration, filesystem scanning, or
runtime registry lookup is permitted.

## 4. Failure Aggregation Semantics

The aggregate report must preserve every validator report in declared order.

Aggregate status rules:

- If every validator returns `VALID`, aggregate status is `VALID`.
- If any validator returns an invalid schema status, aggregate status is
  `INVALID_SCHEMA`.
- If any validator reports missing references, aggregate status may be
  `MISSING_REFERENCE`.
- If multiple failures occur, the first highest-precedence failure determines
  aggregate status.
- Per-validator failures are never discarded or rewritten.
- The aggregate recommendation is report-only.

Failure aggregation must not trigger quarantine, lifecycle transition, approval,
dispatch, execution, repair, persistence, or provider calls.

## 5. Deterministic Reporting Semantics

The aggregate report must include:

- `composition_id`
- `composition_status`
- `validator_order`
- `validator_reports`
- `aggregate_status`
- `failure_summary`
- `authority_findings`
- `replay_findings`
- `lifecycle_findings`
- `semantic_findings`
- `recommended_action`

The report must be deterministic for the same envelope, artifact map, validator
declarations, and validator outputs.

Report identifiers must be derived from canonical validation inputs and ordered
validator results. They must not depend on wall-clock time, process state,
filesystem state, random values, network state, or hidden persistence.

## 6. Validator Isolation Guarantees

Each validator is isolated by contract:

- validators receive explicit inputs only;
- validators may not mutate envelope data;
- validators may not mutate artifact maps;
- validators may not mutate each other;
- validator results are captured independently;
- a validator failure does not authorize another validator to repair or mutate;
- composition does not share hidden mutable state between validators.

If a validator declaration cannot certify read-only behavior, it is not
admissible for this composition layer.

## 7. Bounded Composition Guarantees

The composition layer preserves:

- read-only validation;
- deterministic ordering;
- deterministic aggregation;
- explicit validator declaration;
- explicit artifact map input;
- replay-safe report construction;
- no runtime authority expansion;
- no semantic autonomy expansion.

The composition layer must not:

- auto-discover validators;
- dynamically load validators;
- mutate envelopes;
- mutate artifact maps;
- dispatch execution;
- trigger approval;
- create lifecycle transitions;
- perform IO;
- call providers;
- create hidden persistence;
- create orchestration behavior.

## 8. Composition Lifecycle Boundaries

Composition has a report lifecycle only:

1. `DECLARED`
2. `VALIDATING`
3. `REPORTED`
4. `BLOCKED`

These states describe the composition report process. They are not AGOL Bridge
task lifecycle states and must not transition task packages, result packages,
replay records, or operational lifecycle evidence.

Unknown composition states fail closed as `BLOCKED`.

## 9. Composition Replay Guarantees

Composition replay is report-oriented and append-safe by design:

- validator ordering is visible in the report;
- validator identifiers are visible in the report;
- aggregate status is reproducible from ordered validator reports;
- replay references are observed, not rewritten;
- reports may reference replay records without mutating them.

Any future persistent report writing must be governed by a separate milestone.
This specification does not authorize persistence.

## 10. Composition Authority Guarantees

Composition has no authority to:

- approve execution;
- dispatch execution;
- execute provider work;
- create runtime authority;
- create lifecycle transitions;
- mutate replay;
- mutate task or result packages;
- interpret semantic meaning as authoritative governance;
- continue operational loops automatically.

Composition may only report validation outcomes from declared validators.

## 11. Recommended Implementation Plan

1. Create a bounded implementation review for a pure-function composition
   primitive.
2. Require explicit validator declarations as function references supplied by
   the caller.
3. Accept envelope and artifact map as explicit in-memory inputs.
4. Invoke validators in declared order.
5. Return aggregate in-memory report only.
6. Add tests proving deterministic order, aggregate failure precedence,
   validator isolation, no input mutation, no IO, no dynamic loading, and no
   authority behavior.

## Recommended Next Step

Prepare `VALIDATOR_COMPOSITION_LAYER_IMPLEMENTATION_REVIEW_V1` before writing
code. The review should verify that a pure-function composition primitive can
be implemented without IO, dynamic loading, artifact discovery, authority
expansion, orchestration, or persistence.
