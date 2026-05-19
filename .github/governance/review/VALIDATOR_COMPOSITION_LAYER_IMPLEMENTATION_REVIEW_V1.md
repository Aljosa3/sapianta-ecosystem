# VALIDATOR_COMPOSITION_LAYER_IMPLEMENTATION_REVIEW_V1

## Status

Review complete.

Decision: `COMPOSITION_IMPLEMENTATION_SAFE`

## Scope

This review evaluates whether a minimal deterministic validator composition
implementation is safe to implement.

This review does not implement code, modify runtime behavior, add IO, add
dynamic loading, add validator auto-discovery, add execution authority, add
orchestration, call providers, trigger approval, create lifecycle transitions,
or add semantic autonomy.

## Proposed Implementation Model

The reviewed model is a pure function composition primitive that accepts:

- an envelope object;
- an explicit read-only artifact map;
- an explicit validator registry supplied by the caller;
- an ordered list of validator ids supplied by the caller.

The primitive returns:

- an in-memory aggregate validation report.

The composition primitive may call only validator functions explicitly supplied
in the registry and explicitly named in the ordered validator id list. It must
not discover validators, dynamically load validators, read from the filesystem,
write reports, call providers, dispatch execution, approve continuation, create
lifecycle transitions, update sidepanel state, mutate runtime state, or create
hidden persistence.

## 1. Input Model

Allowed inputs:

- `envelope`: explicit in-memory envelope object.
- `artifact_map`: explicit read-only in-memory artifact map.
- `validator_registry`: explicit in-memory mapping of validator ids to
  validator declarations and function references.
- `ordered_validator_ids`: explicit ordered list of validator ids.

The registry is not a runtime discovery mechanism. It is caller-supplied
composition input. Unknown ids, missing declarations, duplicate ids, or
non-callable validator references must fail closed.

## 2. Output Model

The aggregate report must include:

- `composition_id`
- `aggregate_status`
- `ordered_validator_reports`
- `failures`
- `authority_findings`
- `determinism_findings`
- `recommended_action`

The report is in-memory only. The composition primitive must not persist it.

## 3. Determinism Rules

The implementation is safe only if it preserves:

- stable validator ordering from `ordered_validator_ids`;
- stable duplicate-validator detection;
- stable unknown-validator detection;
- stable status precedence;
- stable report field ordering;
- stable aggregation of failures and findings;
- stable deterministic composition id derivation.

The implementation must not depend on:

- current time;
- random values;
- filesystem state;
- environment variables;
- network state;
- process-global mutable state;
- hidden persistence.

## 4. Safety Rules

The implementation must:

- treat the envelope as read-only;
- treat the artifact map as read-only;
- treat validator outputs as read-only after capture;
- return a new aggregate report object;
- avoid IO;
- avoid provider calls;
- avoid runtime mutation;
- avoid authority expansion;
- avoid orchestration behavior;
- avoid dynamic loading;
- avoid auto-discovery.

## 5. Failure Semantics

Composition failure statuses:

- `VALID`
- `INVALID_COMPOSITION`
- `UNKNOWN_VALIDATOR`
- `DUPLICATE_VALIDATOR`
- `VALIDATOR_FAILED`
- `NON_DETERMINISTIC_REPORT`
- `AUTHORITY_BOUNDARY_VIOLATION`

Failure semantics are report-only. They must not trigger repair, quarantine,
approval, dispatch, execution, persistence, lifecycle transition, replay
mutation, or provider calls.

## 6. Authority Guarantees

The composition primitive may report validation outcomes. It must not convert
validation success into approval, dispatch, execution, lifecycle transition, or
continuation authority.

Validator composition is not an orchestration runtime. It is deterministic
aggregation of declared read-only validators.

## Risks

- A future implementation could blur explicit registry input into dynamic
  loading or discovery.
- A future implementation could persist aggregate reports as a side effect.
- A validator could return non-deterministic output unless tests compare
  repeated composition runs.
- A caller could mistake aggregate `VALID` for approval unless labels remain
  explicit.
- A future implementation could mutate validator outputs while aggregating
  unless copied or treated immutably.

## Recommended Next Step

Implement a small pure-function composition primitive only after preserving the
reviewed boundaries. Tests should prove:

- declared validator order is preserved;
- duplicate validators fail as `DUPLICATE_VALIDATOR`;
- unknown validators fail as `UNKNOWN_VALIDATOR`;
- only supplied validator functions are called;
- aggregation is deterministic;
- validator outputs are not mutated;
- envelope and artifact map are not mutated;
- source contains no filesystem, network, provider, dispatch, approval,
  sidepanel, runtime, dynamic loading, or orchestration calls.
