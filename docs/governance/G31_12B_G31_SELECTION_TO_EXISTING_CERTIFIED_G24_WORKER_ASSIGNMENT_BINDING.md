# Generation 31-12B — G31 Selection to Existing Certified G24 Worker Assignment Binding

Status: operational bounded reuse binding.

Date: 2026-07-16

Implementation verdict:

`G31_SELECTION_TO_EXISTING_CERTIFIED_G24_WORKER_ASSIGNMENT_BINDING_OPERATIONAL`

Next reachability state:

`EXISTING_G24_WORKER_DISPATCH_REACHABILITY_UNVERIFIED`

## Constitutional scope

This implementation treats Generation 30, committed G31-02 through G31-11B,
G31-11A, G31-R01, and the accepted G31-12A audit as immutable baselines.

It implements one transition only:

```text
valid G31-10 execution authorization
  -> valid G31-11B CODEX/WORKER_ROLE selection
  -> existing Worker invocation-request artifacts
  -> existing extended Worker compatibility artifact
  -> unchanged G24 assignment
  -> existing assignment artifacts and Replay
  -> existing canonical presentation
  -> stop before dispatch
```

No Worker dispatch, Provider invocation, Worker invocation, command execution,
repository mutation, new canonical artifact family, production module, selector,
registry, authorization system, Replay system, or Human Interface authority was
introduced.

## Accepted G31-12A evidence

G31-12A proved that G24 Worker assignment was certified and reusable, but the
G31 authorization and selection lineage was not accepted by the existing
invocation-request constructor. The first unbound transition was the request
runtime's older execution-ready lineage loader. The existing assignment runtime
also had no deterministic projection of selected CODEX in `WORKER_ROLE` into
its extended Worker compatibility fields.

G31-12B repairs only those compatibility edges.

## Existing contracts reused

The implementation reuses:

- `WORKER_INVOCATION_REQUEST_EVIDENCE_ARTIFACT_V1`;
- `WORKER_INVOCATION_REQUEST_CLASSIFICATION_ARTIFACT_V1`;
- `WORKER_INVOCATION_REQUEST_ARTIFACT_V1`;
- `WORKER_INVOCATION_REQUEST_RESULT_ARTIFACT_V1`;
- `create_worker_invocation_request`;
- `reconstruct_worker_invocation_request_replay`;
- `render_worker_invocation_request_summary`;
- `WORKER_ARTIFACT_V1`;
- `default_worker_registry_for_request` as the existing extended Worker
  compatibility constructor;
- `assign_worker_from_invocation_request` unchanged as the assignment decision
  function;
- `WORKER_ASSIGNMENT_EVIDENCE_ARTIFACT_V1`;
- `WORKER_ASSIGNMENT_CLASSIFICATION_ARTIFACT_V1`;
- `WORKER_ASSIGNMENT_ARTIFACT_V1`;
- `WORKER_ASSIGNMENT_RESULT_ARTIFACT_V1`;
- `reconstruct_worker_assignment_runtime_replay`;
- `render_worker_assignment_summary`;
- `reconstruct_confirmed_grounded_execution_ready_replay`;
- `reconstruct_authorized_grounded_worker_selection`;
- existing transport serialization, immutable writing, hash validation, and
  Replay ordering contracts.

## G31 lineage projection

`create_worker_invocation_request` now accepts one optional
`resource_selection_replay_reference`. Existing G24 callers omit it and retain
their previous artifact shapes and request-hash inputs.

For a G31 execution-ready lineage, the request runtime:

1. invokes the public confirmed-grounded execution-ready reconstructor;
2. validates the existing authorization Replay and expiry;
3. validates exact candidate, packet, validation, ready, approval, scope, and
   authority continuity;
4. requires the G31-11B selection Replay;
5. invokes the public authorized-grounded Worker-selection reconstructor;
6. verifies same-session selection;
7. binds the exact selection artifact, Replay reference, Worker-selection
   certification hash, Provider-authority denial, and complete authorized scope
   into the existing request artifact;
8. includes the binding in the existing request hash and artifact hash.

The bound authorization scope preserves:

- workspace root;
- original human goal and hash;
- canonical Project Objective and hash;
- approved bounded work and lineage;
- grounded Worker request identity and hash;
- repository cognition and scope-grounding identities and hashes;
- repository targets, source paths, focused tests, and symbols;
- target evidence and immutable hashes;
- mutation layers and validation requirements;
- Worker objective and scope hash.

The bound selection preserves:

- selection identity and artifact hash;
- selection Replay reference;
- authorization context identity and hash;
- registry identity and hash;
- Worker-selection certification hash;
- `CODEX` identity and version;
- `HYBRID_PROVIDER_WORKER` category;
- `WORKER_ROLE` role;
- `WORKER_AUTHORIZED_TASK_ONLY` authority profile;
- required capability and selection diagnostics.

## CODEX Worker compatibility evidence

The existing `default_worker_registry_for_request` constructor now recognizes
the bound selection artifact. It validates the immutable artifact hash and the
exact certified selection vocabulary before projecting the selected resource
into the existing extended `WORKER_ARTIFACT_V1` contract.

The projected Worker evidence contains:

```text
worker_id = CODEX
worker_type = GOAL_FAITHFUL_IMPLEMENTATION_WORKER
worker_version = selected CODEX version
selected_resource_category = HYBRID_PROVIDER_WORKER
selected_role_type = WORKER_ROLE
selected_authority_profile = WORKER_AUTHORIZED_TASK_ONLY
state = AVAILABLE
worker_roles = [GOAL_FAITHFUL_IMPLEMENTATION_WORKER]
compatible_execution_packets = [exact authorized packet]
allowed_outputs = exact grounded repository targets
forbidden_operations = exact authorized prohibitions
provider_authority = false
```

Legacy G24 requests receive the original generic Worker fields without new
`None` fields or changed request-hash inputs.

## Hybrid-role separation

The `HYBRID_PROVIDER_WORKER` category does not grant Provider authority.
The binding requires and preserves:

```text
selected_role_type = WORKER_ROLE
selected_authority_profile = WORKER_AUTHORIZED_TASK_ONLY
provider_authority = false
provider_invoked = false
worker_invoked = false
dispatch_requested = false
```

Provider-category or Provider-role substitution fails before request creation.

## Request and assignment lifecycle

The reference AiCLI continues to transport existing Platform Core results. On
successful G31-11B selection, the existing contextual continuation now calls:

```text
create_worker_invocation_request
  -> default_worker_registry_for_request
  -> assign_worker_from_invocation_request
```

AiCLI supplies only existing references already returned by Platform Core. It
does not choose the Worker, construct scope, decide compatibility, authorize
assignment, or invoke anything.

The unchanged assignment function validates:

- immutable request artifact and nested Replay;
- exact Worker hash and availability;
- Worker family and role;
- execution-packet compatibility;
- allowed-output and forbidden-operation coverage;
- false governance, approval, proposal, Provider, self-authorization, Replay
  mutation, dispatch, invocation, execution, and completion authority;
- ambiguity and duplicate assignment.

The successful stop state is:

```text
worker_selected = true
worker_assigned = true
worker_dispatched = false
provider_invoked = false
worker_invoked = false
command_executed = false
repository_mutated = false
```

An invocation-request artifact remains a prerequisite artifact. Its renderer
explicitly states that no Worker has yet been assigned, dispatched, invoked, or
executed. The following assignment renderer separately reports the assignment
and states that no Worker has been dispatched, invoked, or executed.

## Replay continuity

Request reconstruction now revalidates:

- ordered request Replay wrappers;
- authorization Replay;
- confirmed grounded execution-ready Replay;
- human execution decision lineage;
- complete grounded authorization scope;
- authorized Worker-selection Replay;
- registry and certification evidence;
- exact request selection binding.

Assignment reconstruction now calls the full invocation-request reconstructor
before validating the recorded request artifact. Therefore assignment Replay
reconstructs the complete nested G31 lineage rather than validating only the
request wrapper.

Replay and tamper evidence rejects:

- authorization, scope, Project Objective, Durable Work, path, test, symbol,
  mutation-layer, validation, summary, or confirmation substitution;
- selection identity, context, registry, certification, CODEX identity,
  category, role, profile, or capability substitution;
- Provider-role substitution;
- unavailable, incompatible, or authority-bearing Worker evidence;
- duplicate assignment in the same session;
- request or assignment Replay removal, substitution, or reordering.

Invalid evidence creates no partial request or assignment artifact. A
fail-closed result artifact may record the rejected attempt.

## Canonical presentation

The implementation reuses the existing renderers:

- `render_worker_invocation_request_summary` presents prerequisite request
  status, authorization, packet, and Replay evidence;
- `render_worker_assignment_summary` presents assignment status, CODEX Worker
  identity, family, role, and Replay evidence.

The existing G31 selection renderer remains selection-only and truthfully
reports `worker_assigned: False` at that stage. The final runtime result then
reports assignment completion. This preserves stage-specific truth rather than
rewriting the accepted G31-11B selection result.

## Fail-closed focused evidence

The focused G31-12B suite proves:

- exact G31-10 and G31-11B evidence creates the existing request;
- CODEX/WORKER_ROLE creates a compatible existing Worker artifact;
- unchanged G24 assignment creates the existing assignment artifact;
- nested G31 request and assignment Replay reconstruct;
- identity, category, role, authority-profile, registry, scope, and
  certification substitution fails;
- Provider-role substitution fails;
- unavailable, incompatible, or Provider-authority Worker evidence fails;
- duplicate assignment fails;
- reordered nested request Replay fails assignment reconstruction;
- AiCLI presents request and assignment distinctly;
- no dispatch, Provider invocation, Worker invocation, command, or mutation
  occurs;
- no copied G31-R01 helpers or dispatch caller exists in the binding.

## Real PTY evidence

A disposable Git repository contained exactly:

- `aigol/runtime/human_interface.py`;
- `tests/test_human_interface.py`.

The real PTY-backed `./aicli` conversation supplied only this ordinary request:

```text
Improve the human interface terminal summary behavior. Include focused tests
and validation.
```

The user supplied no paths, JSON, Worker identity, capability name, prepared
artifact, prompt bridge, or shell bridge.

Observed lifecycle:

1. Platform Core created the governed proposal;
2. the first `/approve` approved the proposal but did not authorize execution;
3. Repository Cognition grounded the existing source and focused test;
4. the second `/approve` confirmed the distinct execution decision;
5. G31-10 returned `EXECUTION_AUTHORIZED`;
6. G31-11B selected `CODEX` in `WORKER_ROLE`;
7. G24 returned `WORKER_INVOCATION_REQUEST_CREATED`;
8. G24 returned `WORKER_ASSIGNED` for CODEX;
9. both existing renderers presented their stage-specific results;
10. the session stopped before dispatch.

Observed final boundaries:

```text
worker_selected = true
worker_assigned = true
worker_dispatched = false
provider_invoked = false
worker_invoked = false
command_executed = false
repository_mutated = false
aicli_authorizes = false
aicli_executes = false
aicli_owns_replay = false
```

The source Git object hashes remained unchanged:

- implementation: `582eec37c9b9169f8cbf5b3f511ed4eaab898b3e`;
- focused test: `74ad2f17f47f79462f3cd499a90ce8898bdadb02`.

Post-session reconstruction returned complete G31 request lineage and assigned
Worker `CODEX`. A copied request Replay with an incompatible Worker role
returned `FAILED_CLOSED`, `worker role mismatch`, and no partial assignment.
The disposable repository and runtime evidence were removed.

## Validation results

Focused counts overlap and must not be added together:

- focused G31-12B: **14 passed, 0 skipped, 0 failed**;
- G31-10 and G31-11B: **29 passed, 0 skipped, 0 failed**;
- G24 invocation request and assignment: **25 passed, 0 skipped, 0 failed**;
- Worker runtime and Worker-selection certification: **28 passed, 0 skipped, 0 failed**;
- unified resource selection: **12 passed, 0 skipped, 0 failed**;
- execution authorization and G31-08/G31-09: **60 passed, 0 skipped, 0 failed**;
- Replay suites: **245 passed, 0 skipped, 0 failed**;
- Human Interface and AiCLI: **42 passed, 0 skipped, 0 failed**;
- Governance tests: **96 passed, 0 skipped, 0 failed**;
- final affected verification after legacy-shape consolidation:
  **68 passed, 0 skipped, 0 failed**;
- full repository suite, run exactly once: **6,353 passed, 4 skipped,
  0 failed**;
- `py_compile`: passed;
- `git diff --check`: passed.

The full suite wrote tracked runtime fixture evidence. Those six test-generated
fixture changes were restored to their verified-clean pre-test state; no user
change was overwritten.

## Governance result

Repository governance remains:

`PARTIALLY_CONFORMANT`

The deterministic conformance engine reports:

- checks passed: 18;
- checks failed: 2;
- critical violations: 0;
- deterministic: true;
- fail-closed: true;
- read-only: true;
- report hash:
  `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea`.

The two findings are the known pre-existing root and system pre-commit hook
drift. They do not invalidate G31-12B.

## Change-size and symbol accounting

Production changes before this document:

| File | Added | Removed | Responsibility |
|---|---:|---:|---|
| `aigol/runtime/worker_invocation_request_runtime.py` | 95 | 6 | Recognize confirmed G31 readiness, bind and reconstruct selection lineage. |
| `aigol/runtime/worker_assignment_runtime.py` | 44 | 7 | Project selected CODEX through the existing extended Worker constructor; reject duplicate assignment; reconstruct nested request Replay. |
| `aigol/cli/aicli.py` | 59 | 0 | Continue existing Platform Core results through request and assignment and render both; no semantic authority. |
| **Production total** | **198** | **13** | Below the 200-line gate. |

Test changes before this document:

| File | Added | Removed |
|---|---:|---:|
| `tests/test_g31_09_distinct_human_execution_decision_binding.py` | 2 | 1 |
| `tests/test_g31_11b_authorized_existing_worker_selection_binding.py` | 5 | 3 |
| `tests/test_g31_12b_g31_selection_to_g24_worker_assignment_binding.py` | 236 | 0 |
| **Test total** | **243** | **4** |

Exactly one new production symbol was introduced:

- `_load_g31_selection_binding`, called only by
  `_load_authorized_lineage`, validates and projects the existing public G31
  selection Replay into the existing request artifact.

Existing production symbols extended without transferring responsibility:

- `create_worker_invocation_request` accepts an optional selection Replay
  reference;
- `default_worker_registry_for_request` projects bound selected CODEX evidence;
- `reconstruct_worker_assignment_runtime_replay` reconstructs nested request
  Replay;
- `_worker_invocation_request_already_assigned` searches existing assignment
  artifacts within its supplied session root;
- `_record_contextual_execution_decision` continues successful selection into
  the existing request and assignment contracts.

No `_verify_hash`, `_relative_path`, or `_unique_relative_paths` helper was
copied. Existing serialization and validation contracts are reused.

## Progress estimates

Evidence-scoped planning estimates:

- no-copy/paste conversational governed development: **99%**;
- whole-project progress: **88%**.

These are not certification or production-readiness claims. Worker dispatch
reachability remains unverified and must be audited before any dispatch
implementation is considered.

## Exactly one next state

`EXISTING_G24_WORKER_DISPATCH_REACHABILITY_UNVERIFIED`

## G31-13A audit-only prompt

```text
# Generation 31-13A — Existing Certified G24 Worker Dispatch Reachability Audit

AUDIT_ONLY. Do not implement or modify runtime behavior.

Treat Generation 30, accepted G31-02 through G31-12B, G31-11A, G31-R01, and
the G31-12A audit as immutable baselines.

G31-12B verdict:

G31_SELECTION_TO_EXISTING_CERTIFIED_G24_WORKER_ASSIGNMENT_BINDING_OPERATIONAL

Current reachability state:

EXISTING_G24_WORKER_DISPATCH_REACHABILITY_UNVERIFIED

## Objective

Determine from deterministic repository evidence whether the existing
certified G24 Worker-dispatch lifecycle can consume the exact G31-12B
WORKER_ASSIGNMENT_ARTIFACT_V1 without redesign or new architecture.

Do not dispatch a Worker, invoke a Provider or Worker, execute a command, or
mutate a repository.

## Required audit

Locate and document:

1. every existing Worker-dispatch constructor, validator, artifact family,
   Replay reconstructor, certification report, presenter, and caller;
2. the exact public input contract consumed by the first dispatch transition;
3. whether it accepts the existing G31-12B assignment artifact and nested
   authorization, grounding, selection, request, Worker, and assignment Replay;
4. whether dispatch authorization is already distinct from proposal approval,
   execution authorization, selection, and assignment;
5. whether selected CODEX in WORKER_ROLE is compatible with the existing
   dispatch target and transport contract;
6. whether the hybrid Provider role remains inactive;
7. whether dispatch preparation can remain non-invoking and non-mutating;
8. the exact first unbound field, identity, hash, Replay edge, or policy if
   direct reachability fails;
9. whether any bounded projection can reuse an existing constructor without a
   new module or canonical artifact family;
10. whether existing presentation distinguishes assignment, dispatch,
    invocation, command execution, and repository mutation.

## Evidence matrix

Classify every required dispatch input as:

- DIRECTLY_COMPATIBLE;
- COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION;
- AVAILABLE_BUT_NOT_BOUND;
- INCOMPATIBLE;
- ABSENT_BY_DESIGN.

Trace at minimum:

- complete G31-04 through G31-12B lineage;
- authorization and confirmation identities;
- grounded workspace, paths, symbols, tests, hashes, mutation layers, and
  validations;
- selection identity, registry and certification hashes, CODEX identity,
  category, WORKER_ROLE, and authority profile;
- invocation-request identity and Replay;
- extended Worker identity and compatibility evidence;
- assignment identity, hash, status, and Replay;
- dispatch authorization, target, transport, and stop boundaries.

## Fail-closed audit

Determine whether existing dispatch contracts reject:

- missing, stale, substituted, replayed, or reordered assignment evidence;
- changed authorization, scope, request, Worker, or selection evidence;
- Provider-role substitution;
- unavailable or incompatible Worker;
- duplicate dispatch;
- dispatch without the required distinct authorization;
- dispatch that would implicitly invoke a Worker, execute a command, or mutate
  a repository.

## Real PTY observation

Use a disposable Git repository with one implementation and one focused test.
Through a real PTY-backed ./aicli session, submit only an ordinary bounded
natural-language request and contextual approvals. Observe the complete
G31-12B assignment lifecycle and verify the truthful stop before dispatch.

Do not supply paths, JSON, Worker identities, capability names, prepared
artifacts, prompts, or shell bridges. Do not dispatch anything. Remove the
disposable repository afterward.

## Validation

Run focused read-only tests for existing Worker dispatch, G24 request and
assignment, G31-10 through G31-12B, authorization, selection, Replay, Human
Interface/AiCLI, and Governance. Run py_compile and git diff --check. Do not run
the full suite unless deterministic inconsistency requires it.

## Documentation

Add only:

docs/governance/G31_13A_EXISTING_CERTIFIED_G24_WORKER_DISPATCH_REACHABILITY_AUDIT.md

## Required verdict

Return exactly one:

- EXISTING_G24_WORKER_DISPATCH_DIRECTLY_REACHABLE
- EXISTING_G24_WORKER_DISPATCH_REUSABLE_BOUNDED_PROJECTION_REQUIRED
- EXISTING_G24_WORKER_DISPATCH_INCOMPATIBLE
- EXISTING_G24_WORKER_DISPATCH_RUNTIME_EVIDENCE_BLOCKED

If a bounded projection is required, provide a minimal implementation prompt.
Otherwise do not provide an implementation prompt.

Report exact inspected contracts, evidence matrix, first unbound transition,
PTY observation, Replay and authority evidence, validation and Governance
results, exact git status, progress estimates, and exactly one next state.

Do not commit.
```

No commit was created by G31-12B.
