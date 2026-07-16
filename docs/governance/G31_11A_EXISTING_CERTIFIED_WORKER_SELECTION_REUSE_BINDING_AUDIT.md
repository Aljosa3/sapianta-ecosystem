# G31-11A Existing Certified Worker Selection Reuse and Binding Audit

Status: completed `AUDIT_ONLY` assessment.

Date: 2026-07-16

Verdict:

`EXISTING_CERTIFIED_WORKER_SELECTION_REUSABLE_BOUNDED_PROJECTION_REQUIRED`

## Scope and baseline

This audit treats committed G31-10 and its verdict as accepted baseline:

`CONFIRMED_GROUNDED_EXECUTION_DECISION_EXECUTION_AUTHORIZATION_BINDING_OPERATIONAL`

It also accepts the certified premise that Generation 24 established Worker
registration, discovery, certification, eligibility, deterministic selection,
assignment, dispatch, invocation, execution governance, and Replay.

The audit does not reopen or redesign those responsibilities. It changes no
runtime, CLI, Human Interface, test, schema, registry, selection-policy,
Governance, or Replay behavior. This document is the only repository change.

## Plain-language conclusion

Worker selection is not missing.

The repository contains:

- replay-visible Worker identity and registration;
- passive ERR capability discovery and selection evidence;
- a richer unified resource registry with Worker roles, lifecycle, trust,
  capability, domain, authority, priority, ambiguity, and no-match checks;
- deterministic selection that creates `RESOURCE_SELECTION_ARTIFACT_V1` and
  never invokes or dispatches the selected Worker;
- certified deterministic-first Worker-selection scenarios and checked-in
  certification evidence with verdict `WORKER_SELECTION_CERTIFIED`;
- authorization-to-Worker-request and Worker-assignment entrypoints;
- Replay reconstruction and tamper rejection for each stage.

The current G31 path stops after authorization because no caller projects the
G31-10 authorization and grounded role vocabulary into the existing unified
selector. The selector expects canonical selection scalars such as
`required_capability=IMPLEMENTATION_ASSISTANCE`, `requested_role_type=WORKER_ROLE`,
and `domain_id=NATIVE_DEVELOPMENT`. G31-10 instead carries the exact grounded
scope and `GOAL_FAITHFUL_IMPLEMENTATION_WORKER` role. Equivalent native-
development Worker mappings already exist, but no public G31 continuation
binds them.

That is bounded projection debt, not a Worker-selection capability gap.

## Existing public contracts

| Responsibility | Exact public contract | Canonical input | Canonical output | Authority owner | Replay and evidence |
|---|---|---|---|---|---|
| Worker registration and identity | `aigol/runtime/worker_runtime.py` — `register_worker` | Worker identity, type, version, declared capabilities, supported request types, trust boundary, state, timestamps, Replay references | `WORKER_ARTIFACT_V1` plus registration-returned evidence | Worker Layer | `reconstruct_worker_registration_replay`; two ordered append-only records; `tests/test_worker_runtime_v1.py` |
| Worker registry metadata | `aigol/runtime/external_resource_registry_runtime.py` — `create_err_v0_registry`, `register_resource`, `default_err_v0_registry` | Passive normalized resource metadata: identity, `EXECUTION_WORKER` type, capabilities, active state | Normalized registry entry; no authority or invocation | ERR passive metadata boundary | Registry hash is embedded in selection evidence; `tests/test_external_resource_registry_runtime_v0.py` |
| Worker certification | `aigol/runtime/worker_selection_certification_v1.py` — `run_worker_selection_certification_v1` | Certification replay root and seven fixed governed scenarios | Coverage, evidence, Replay, and certification reports; final verdict `WORKER_SELECTION_CERTIFIED` | Governance/Certification | `reconstruct_worker_selection_replay`; checked-in `runtime/worker_selection_certification_v1/CERT-000001`; `tests/test_worker_selection_certification_v1.py` |
| Worker discovery | `aigol/runtime/external_resource_registry_runtime.py` — `get_resource_by_id`, `find_resources_by_capability` | Registry, resource identity or capability, optional `EXECUTION_WORKER` type | Exact resource or ordered active compatible resources | ERR | Read-only metadata lookup; selected registry hash becomes Replay evidence; external-registry tests |
| Passive ERR selection | `aigol/runtime/external_resource_registry_runtime.py` — `select_resource_for_capability` | Capability, resource type, registry, optional Human Intent/HIRR evidence | `ERR_RESOURCE_SELECTION_EVIDENCE_V0` and returned artifact | ERR | `reconstruct_err_v0_selection_replay`; no orchestration, assignment, dispatch, or invocation |
| Worker eligibility | `aigol/runtime/unified_resource_selection_runtime.py` — `select_unified_resource` | Workflow, required capability, `WORKER_ROLE`, domain, authorization-required flag, trust, optional preferred resource, registry and context identity | Eligibility diagnostics with accepted/rejected resources | Platform Core Resource Selection using Worker/ERR metadata | Diagnostics hash and registry hash are Replay-visible; `tests/test_unified_resource_selection_runtime_v1.py` |
| Deterministic Worker selection | Same `select_unified_resource` public entrypoint | Eligible Worker-role candidates | `RESOURCE_SELECTION_ARTIFACT_V1`, status artifact, diagnostics, and returned artifact | Platform Core Resource Selection | Priority then resource identity/role ordering; equal leading priorities fail closed as ambiguous; two-step Replay |
| No compatible or ambiguous handling | Same `select_unified_resource` public entrypoint | Empty eligible set or tied leading candidates | Existing `FAILED_CLOSED` selection artifact with diagnostics and failure reason | Platform Core Resource Selection | Reconstructable failed result; focused no-match, trust, duplicate-registry, and ambiguity tests |
| Selection result | `RESOURCE_SELECTION_ARTIFACT_V1` from `select_unified_resource` | Validated registry and selection constraints | Selected resource identity, category, version, active role, authority profile, rationale, diagnostics, context reference/hash | Platform Core Resource Selection | Artifact hash, registry hash, diagnostics hash, returned-artifact hash |
| Selection Replay reconstruction | `aigol/runtime/unified_resource_selection_runtime.py` — `reconstruct_unified_resource_selection_replay` | Selection Replay directory | Selected resource, role, capability, rationale, registry/diagnostics hashes, failure state, authority flags | Replay | Rejects wrapper ordering, artifact-hash, selection-reference, and returned-hash substitution |
| Authorization-to-Worker-request projection | `aigol/runtime/worker_invocation_request_runtime.py` — `create_worker_invocation_request` | Execution-authorization Replay | `WORKER_INVOCATION_REQUEST_ARTIFACT_V1` with role, family, outputs, prohibitions, validation requirements, and authorization lineage | Platform Core execution lifecycle | `reconstruct_worker_invocation_request_replay`; validates authorization, expiry, packet, candidate, approval, chain, authority, and Replay |
| Worker-assignment entry | `aigol/runtime/worker_assignment_runtime.py` — `assign_worker_from_invocation_request` | Valid invocation request plus Worker artifacts, or explicit ERR lookup configuration | Assignment evidence, classification, `WORKER_ASSIGNMENT_ARTIFACT_V1`, and result | Worker Layer | `reconstruct_worker_assignment_runtime_replay`; optional nested ERR selection; stops before dispatch and invocation |
| Basic assignment contract | `aigol/runtime/worker_runtime.py` — `assign_worker` | Available `WORKER_ARTIFACT_V1` and `READY_FOR_DISPATCH_ARTIFACT_V1` with Replay | `WORKER_ASSIGNMENT_ARTIFACT_V1` | Worker Layer | `reconstruct_worker_assignment_replay`; no self-assignment, dispatch, invocation, or execution |
| Authorization validation | `aigol/runtime/execution_authorization_runtime.py` — `reconstruct_execution_authorization_replay` | Existing authorization Replay | Validated authorization identity/status, summary/confirmation lineage, packet lineage, and authority boundaries | Governance/Execution Authorization | Four ordered artifacts; rejects request, decision, authorization, scope, packet, and Replay substitution |

The checked-in Worker-selection certification report has artifact hash
`sha256:c38b21efede2314fb7cdb8f6bb8a74ee5f4a1d1c3adf46992471684734a94155`.
All recorded certification assertions are true, including deterministic-first
selection, capability mismatch fail-closed behavior, rationale, suitability
scores, alternative rejection, Replay reconstruction, and governance-authority
preservation.

## G31-10 compatibility matrix

The matrix compares the committed G31-10 capture and its exact authorization
scope with the existing selection and authorization-to-Worker-request inputs.

| Required evidence | G31-10 location | Classification | Deterministic assessment |
|---|---|---|---|
| Authorization request | `authorization_request_artifact` | `DIRECTLY_AVAILABLE` | Existing canonical request with packet, candidate, summary, confirmation, approval, exact requested scope, and Replay identity |
| Authorization decision | `authorization_decision_artifact` | `DIRECTLY_AVAILABLE` | Existing approved decision linked to request, summary, confirmation, packet, and validation checks |
| Execution-authorization artifact | `execution_authorization_artifact` | `DIRECTLY_AVAILABLE` | Existing `EXECUTION_AUTHORIZATION_ARTIFACT_V1`, `EXECUTION_AUTHORIZED`, non-revoked, non-transferable, non-recursive |
| Session identity | Nested G31-09 decision inside the execution-ready candidate | `AVAILABLE_BUT_NOT_BOUND` | G31 validation and Replay prove the session, but unified selection accepts no session field |
| Workspace | `authorized_scope.workspace_root` | `DIRECTLY_AVAILABLE` | Exact workspace is immutable in authorization scope; selector does not currently consume it |
| Source paths | `authorized_scope.source_paths` and `repository_targets` | `DIRECTLY_AVAILABLE` | Exact workspace-relative paths and hashes are present; not currently bound to selection eligibility |
| Focused-test paths | `authorized_scope.focused_test_paths` | `DIRECTLY_AVAILABLE` | Exact focused tests are present; not currently bound to selection eligibility |
| Symbols | `authorized_scope.symbols_by_path` | `DIRECTLY_AVAILABLE` | Symbols and source-content hashes are present; not currently bound to selection eligibility |
| Evidence hashes | Scope grounding, cognition snapshot, target evidence, source content, and lineage hashes | `DIRECTLY_AVAILABLE` | Complete evidence exists and reconstructs; selector accepts only one context reference/hash |
| Mutation layers | `authorized_scope.mutation_layers` | `DIRECTLY_AVAILABLE` | Exact layer classifications exist; unified registry role bindings do not directly evaluate them |
| Validation requirements | Scope `validation_requirements` and packet `required_validations` | `DIRECTLY_AVAILABLE` | Existing Worker-request projection preserves them; selector does not directly evaluate them |
| Worker capability requirements | Packet `worker_role_requirements=[GOAL_FAITHFUL_IMPLEMENTATION_WORKER]` | `INCOMPATIBLE` for direct invocation, but not an architectural gap | Unified selection expects a capability such as `IMPLEMENTATION_ASSISTANCE` and `WORKER_ROLE`; the equivalent native-development mapping already exists in `EXPLICIT_RESOURCE_ROLES`, but no public G31 projection applies it |
| Project Objective | `authorized_scope.canonical_project_objective` and `project_objective_hash` | `DIRECTLY_AVAILABLE` | Exact objective is preserved and hashed; not currently used as selector input |
| Approved Durable Governed Work | `approved_bounded_work` and `approved_work_lineage` | `DIRECTLY_AVAILABLE` | Complete approved-work evidence is inside exact authorization scope |
| Grounded Worker request | `grounded_worker_request_reference` and hash | `DIRECTLY_AVAILABLE` | Grounded request and repository evidence are part of authorization scope |
| Replay lineage | Authorization Replay, execution-ready Replay, G31-09 decision Replay, and nested G31-04 through G31-08 hashes | `DIRECTLY_AVAILABLE` | Full lineage reconstructs; selection Replay has no current caller binding its context to this lineage |

No required G31 evidence is architecturally absent. The direct vocabulary for
Worker capability and domain selection is incompatible without the existing
native-development mapping, and the remaining exact evidence is available but
not consumed by eligibility. This is why the verdict is bounded projection,
not capability gap and not direct reachability.

## Existing call-chain trace

The smallest reuse-first call chain is:

```text
reconstruct_execution_authorization_replay
  -> reconstruct_confirmed_grounded_execution_ready_replay
  -> bounded G31 authorization-to-selection input projection
       workflow_type = NATIVE_DEVELOPMENT
       required_capability = IMPLEMENTATION_ASSISTANCE
       requested_role_type = WORKER_ROLE
       domain_id = NATIVE_DEVELOPMENT
       worker_authorization_required = true
       context_reference = exact authorization_id
       context_hash = exact authorization artifact_hash
  -> default_resource_registry
  -> select_unified_resource
  -> RESOURCE_SELECTION_ARTIFACT_V1
  -> reconstruct_unified_resource_selection_replay
  -> stop before assign_worker_from_invocation_request
```

Exact reusable callee:

`aigol.runtime.unified_resource_selection_runtime.select_unified_resource`

Current G31 caller boundary:

`aigol.runtime.confirmed_grounded_execution_authorization_binding.authorize_confirmed_grounded_execution_decision`

Exact missing invocation edge:

```text
successful authorize_confirmed_grounded_execution_decision return
  -X-> authorization-aware bounded input projection
  -X-> select_unified_resource
```

Repository search finds no call from the G31-10 binding, Platform Core project
services, or AiCLI continuation to `select_unified_resource`. Existing callers
are pre-G31 conversation/PPP and universal-provider workflows with different
source contracts.

The existing `create_worker_invocation_request` is an authorization-aware
public projection, but it is not directly reusable by G31-10 today. Its private
execution-ready loader recognizes only governed-implementation dry-run and OCS
Replay. A direct read-only compatibility attempt against exact G31-10 evidence
returned:

```text
authorization_status: EXECUTION_AUTHORIZED
request_status: FAILED_CLOSED
failure_reason: OCS execution readiness replay lineage mismatch
```

It also expects `validation.handoff_hash`, while the G31-10 validation artifact
expresses its source continuity through the exact grounded-scope and decision
hashes. Reusing that projection therefore requires bounded G31 lineage support;
fabricating an OCS or legacy handoff would be incorrect.

## Human Interface and presentation assessment

No Human Interface semantic decision is required. Worker eligibility,
capability mapping, registry use, and selection must remain Platform Core and
Worker/ERR responsibilities. AiCLI may only render a returned selection.

`human_interface_runtime_entry_service` can already inspect a
`universal_resource_selection` Replay and project selection status and selected
resource identity. However, current AiCLI G31 continuation stops after rendering
execution authorization.

The Canonical Platform Presentation Layer does not currently accept
`RESOURCE_SELECTION_ARTIFACT_V1`; unsupported source types fail closed. A
future operational binding therefore needs a bounded existing-presentation
projection if the selection must be shown canonically through `./aicli`. It
must not add selection semantics to AiCLI.

## PTY-backed operational observation

A disposable Git repository contained one implementation and one focused test.
A real PTY-backed `./aicli` session received only:

- one ordinary bounded natural-language change request;
- `/send`;
- first `/approve`;
- second `/approve`;
- `/exit`.

Observed positive state:

- G31-04 through G31-09 completed;
- G31-10 rendered `EXECUTION_AUTHORIZED`;
- authorization Replay reconstructed successfully;
- Worker assignment, dispatch, and invocation were false;
- Provider invocation was false;
- command execution and repository mutation were false;
- AiCLI authorization, execution, and Replay authority remained false.

Observed stop state:

- no `resource_selection` or Worker-selection Replay directory existed;
- no Worker-invocation request was created by the terminal lifecycle;
- no Worker assignment, dispatch, or invocation artifact existed;
- terminal output ended with “No Worker has been assigned, dispatched,
  invoked, or executed.”

The first missing operational transition is the authorization-aware bounded
projection and call to `select_unified_resource`.

A read-only attempt to pass the PTY authorization into the existing
authorization-to-Worker-request projection failed closed before selection with
the same G31 execution-ready lineage mismatch. No repair was applied. The
disposable repository, runtime, and PTY transcript were removed.

## Replay and authority boundaries

Existing selection Replay provides:

- ordered selection and returned artifacts;
- registry and diagnostics hashes;
- selected resource identity, category, role, capability, and rationale;
- accepted and rejected candidate diagnostics;
- fail-closed no-match and ambiguity evidence;
- wrapper, artifact, reference, and returned-hash verification;
- Provider/Worker invocation, execution request, dispatch request, and
  authorization creation all false.

G31-10 separately provides complete authorization and grounded-scope Replay.
The bounded projection must bind the selection artifact’s context reference and
hash to the exact G31 authorization and reconstruct both chains. Existing
selection Replay alone cannot infer or discover that parent lineage.

Selection remains distinct from assignment, dispatch, invocation, execution,
validation, and certification. The audit invoked none of them.

## Focused validation

Exact results:

- Worker registry and selection certification: **36 passed, 0 skipped, 0
  failed**;
- Worker eligibility and unified selection: **21 passed, 0 skipped, 0
  failed**;
- Worker assignment boundary: **14 passed, 0 skipped, 0 failed**;
- execution authorization, authorization-to-Worker-request, and G31-10:
  **35 passed, 0 skipped, 0 failed**;
- Replay tests: **245 passed, 0 skipped, 0 failed**;
- Human Interface and AiCLI: **41 passed, 0 skipped, 0 failed**;
- Governance tests: **96 passed, 0 skipped, 0 failed**.

Focused evidence was consistent, so the full repository suite was not run.

The inspected runtime modules passed targeted `py_compile`. Audit-document
whitespace validation and `git diff --check` passed.

Repository governance remains `PARTIALLY_CONFORMANT`:

- checks passed: 18;
- checks failed: 2;
- critical violations: 0;
- deterministic: true;
- fail-closed: true;
- read-only: true;
- report hash:
  `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea`.

The failures are the two known hook-drift findings: missing root expected and
installed pre-commit hooks, and missing `promotion_gate_v02` plus
`check_layer_freeze` in the system pre-commit hook. This audit does not hide or
repair them. They do not invalidate the Worker-selection reuse evidence.

## Minimal non-executed implementation projection

Because the binding is deterministically absent, the maximum justified future
production surface is **200 added lines**, with no new canonical artifact
family, registry, selector, policy engine, or Replay subsystem.

Preferred placement requires no new production file: add one bounded public
continuation beside the existing G31-10 authorization binding and a small
Platform Core presentation adapter only if canonical terminal presentation is
required.

Exact existing caller:

`authorize_confirmed_grounded_execution_decision` successful result, consumed
by its Platform Core continuation owner.

Exact existing callee:

`select_unified_resource`.

Exact artifacts passed and validated:

- G31-10 authorization request, decision, authorization, and result;
- exact authorization Replay reference;
- exact G31 execution-ready packet and Replay;
- exact authorized scope, Worker role, Project Objective, grounded Worker
  request, Repository Cognition hashes, and G31-04 through G31-09 lineage;
- selector context reference equal to authorization identity;
- selector context hash equal to authorization artifact hash.

Required validation before selection:

1. reconstruct authorization Replay;
2. reject failed, revoked, expired, replayed, substituted, or cross-session
   authorization;
3. reconstruct G31 execution-ready Replay and require exact scope equality;
4. project only the existing native-development Worker-role mapping;
5. call `select_unified_resource` with `worker_authorization_required=true`;
6. require one successful selection or retain its existing fail-closed result;
7. reconstruct selection Replay and verify context identity/hash;
8. stop with assignment, dispatch, invocation, command, and mutation false.

Required focused tests must cover positive selection, no-match, ambiguity,
authorization substitution, scope or role substitution, stale evidence,
context-lineage substitution, Replay ordering, no assignment, no dispatch, no
invocation, no mutation, and thin-AiCLI ownership.

## Progress and next blocker

The evidence-adjusted no-copy/paste conversational governed-development
estimate remains **97%**. Overall project progress remains **86%**. Existing
Worker selection was already part of the denominator; this audit corrects the
next unit from “build Worker selection” to “bind G31 authorization to existing
selection.” These estimates are planning indicators, not certification claims.

Exactly one next blocker is:

`G31_10_AUTHORIZATION_EXISTING_WORKER_SELECTION_BOUNDED_PROJECTION_ABSENT`

## Bounded implementation prompt

```text
# Generation 31-11B — G31-10 Authorization to Existing Certified Worker Selection Binding

Treat Generation 30, committed G31-02 through G31-10, and the G31-11A audit as
immutable accepted baselines.

G31-11A verdict:

EXISTING_CERTIFIED_WORKER_SELECTION_REUSABLE_BOUNDED_PROJECTION_REQUIRED

First true blocker:

G31_10_AUTHORIZATION_EXISTING_WORKER_SELECTION_BOUNDED_PROJECTION_ABSENT

## Objective

Implement exactly one reuse binding:

valid G31-10 execution authorization
  -> exact existing native-development Worker selection input
  -> select_unified_resource
  -> existing RESOURCE_SELECTION_ARTIFACT_V1 and Replay
  -> stop before Worker assignment

Do not create or redesign a Worker registry, selector, eligibility policy,
Worker identity, authorization system, assignment runtime, or Replay subsystem.

## Required reuse

Reuse:

- reconstruct_execution_authorization_replay;
- reconstruct_confirmed_grounded_execution_ready_replay;
- the exact G31-10 authorization request, decision, artifact, result, scope,
  packet, and nested G31 lineage;
- default_resource_registry;
- select_unified_resource;
- reconstruct_unified_resource_selection_replay;
- existing WORKER_ROLE, IMPLEMENTATION_ASSISTANCE, and NATIVE_DEVELOPMENT
  vocabulary;
- existing Human Conversation Experience and presentation contracts.

## Required behavior

Validate the exact authorization and project only:

- workflow_type: NATIVE_DEVELOPMENT;
- required_capability: IMPLEMENTATION_ASSISTANCE;
- requested_role_type: WORKER_ROLE;
- domain_id: NATIVE_DEVELOPMENT;
- worker_authorization_required: true;
- context_reference: exact execution-authorization identity;
- context_hash: exact execution-authorization artifact hash.

Select exactly one existing eligible resource or preserve the selector’s
existing fail-closed no-match or ambiguity result. Bind selection Replay to the
complete G31 authorization lineage.

Required stop state:

worker_selected = true only on successful existing selection
worker_assigned = false
worker_dispatched = false
provider_invoked = false
worker_invoked = false
command_executed = false
repository_mutated = false

Do not call assign_worker_from_invocation_request, dispatch, Provider or Worker
invocation, command execution, or repository mutation.

## Fail-closed requirements

Reject failed, revoked, expired, replayed, substituted, broadened,
cross-session, or Replay-invalid authorization; changed summary or confirmation;
changed grounded scope, role, Project Objective, Repository Cognition evidence,
or G31 identity; unsupported capability/domain projection; changed registry or
selection context; and reordered or substituted selection Replay.

Invalid evidence must not partially select or assign a Worker.

## Minimal-change gate

Use no new canonical artifact family and preferably no new production file.
Maximum production additions: 200 lines. Use public hash, serialization,
validation, and Replay contracts; copy no helpers. Stop and report if the
existing selector cannot represent the transition within this bound.

## Validation

Add focused G31-11B tests for exact authorization consumption, positive existing
selection, no-match, ambiguity, tampering, Replay, context lineage, authority
boundaries, and no assignment. Run G31-10, unified selection, ERR, Worker
registry/certification, authorization, Replay, Human Interface/AiCLI,
Governance, py_compile, and git diff --check. Run the full suite once only after
focused evidence passes.

Perform a real PTY-backed ./aicli validation in a disposable repository using
only an ordinary request and contextual approvals. Demonstrate existing Worker
selection, truthful stop before assignment, fail-closed tampering, nested
Replay reconstruction, and no dispatch, invocation, command, or mutation.
Remove the disposable repository afterward.

## Documentation

Add:

docs/governance/G31_11B_G31_10_AUTHORIZATION_EXISTING_CERTIFIED_WORKER_SELECTION_BINDING.md

Report exact files, size, symbols, reused contracts, PTY and Replay evidence,
validation/governance counts, authority boundaries, progress, one next blocker
or readiness verdict, git status, and commit commands. Do not commit.
```
