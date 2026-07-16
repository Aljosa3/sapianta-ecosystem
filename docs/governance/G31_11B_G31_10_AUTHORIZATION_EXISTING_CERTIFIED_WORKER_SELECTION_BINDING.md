# Generation 31-11B G31-10 Authorization to Existing Certified Worker Selection Binding

Status: implemented and operationally validated.

Date: 2026-07-16

Implementation verdict:

`G31_10_AUTHORIZATION_TO_EXISTING_CERTIFIED_WORKER_SELECTION_OPERATIONAL`

Next reachability state:

`EXISTING_G24_WORKER_ASSIGNMENT_REACHABILITY_UNVERIFIED`

## Constitutional scope

This implementation treats Generation 30, committed G31-02 through G31-10,
G31-11A, and G31-R01 as immutable accepted baselines.

Accepted G31-11A verdict:

`EXISTING_CERTIFIED_WORKER_SELECTION_REUSABLE_BOUNDED_PROJECTION_REQUIRED`

Accepted G31-R01 verdicts:

- `G31_BINDINGS_ACCEPTED_WITH_CONSOLIDATION_OBSERVATIONS`;
- `READY_FOR_G31_11B_WITH_DEFERRED_CONSOLIDATION`.

G31-11B implements one compatibility edge only:

```text
valid G31-10 execution authorization
  -> exact native-development selection vocabulary
  -> existing default_resource_registry
  -> existing select_unified_resource
  -> existing RESOURCE_SELECTION_ARTIFACT_V1
  -> existing selection Replay
  -> canonical presentation
  -> stop before Worker assignment
```

No Worker registry, Worker identity, selector, eligibility policy,
authorization system, assignment runtime, state store, router, Replay
subsystem, or canonical artifact family was added or redesigned.

## Existing contracts reused

| Responsibility | Existing public contract | G31-11B use |
|---|---|---|
| G31-10 authorization | `reconstruct_execution_authorization_replay` | Reconstructs the four existing authorization artifacts and rejects invalid ordering, identity, scope, confirmation, packet, or status evidence |
| G31 execution-ready lineage | `reconstruct_confirmed_grounded_execution_ready_replay` | Reconstructs G31-04 through G31-09 and revalidates repository evidence through the existing nested validators |
| Canonical registry | `default_resource_registry` | Supplies the existing deterministic resources, roles, priorities, authority profiles, and registry hash |
| Deterministic selection | `select_unified_resource` | Performs the existing eligibility evaluation and deterministic priority selection without invocation |
| Selection artifact | `RESOURCE_SELECTION_ARTIFACT_V1` | Records exact vocabulary, registry hash, context identity/hash, selected resource/role, diagnostics, and non-invocation flags |
| Selection Replay | `reconstruct_unified_resource_selection_replay` | Reconstructs existing recorded/returned wrappers and rejects ordering, hash, and reference substitution |
| Worker role vocabulary | `WORKER_ROLE` and existing registry role bindings | Requests an already-defined authorized-task-only Worker role |
| Worker-selection certification | checked-in `WORKER_SELECTION_CERTIFICATION_REPORT_V1` | Requires a public-hash-valid report with final verdict `WORKER_SELECTION_CERTIFIED` |
| Serialization and hashes | `load_json`, `replay_hash`, `verify_replay_hash` | Reuses canonical reading and validation without local hash or wrapper helpers |
| Human Interface | existing contextual `/approve` transport in `aicli.py` | Calls the Platform Core binding and renders supplied canonical evidence; it does not select or authorize |

The existing selector remains the only eligibility and tie-break owner. The
binding neither asks the human for an internal resource identity nor supplies
`preferred_resource_id`.

## Exact vocabulary projection

After complete authorization validation, the binding projects exactly:

| Field | Value |
|---|---|
| `workflow_type` | `NATIVE_DEVELOPMENT` |
| `required_capability` | `IMPLEMENTATION_ASSISTANCE` |
| `requested_role_type` | `WORKER_ROLE` |
| `domain_id` | `NATIVE_DEVELOPMENT` |
| `worker_authorization_required` | `true` |
| `context_reference` | exact execution-authorization identity |
| `context_hash` | exact execution-authorization artifact hash |

No target, operation, command, path, scope, role, capability, domain, policy,
or authority is inferred from terminal text at this stage.

## Authorization and scope continuity

`select_authorized_grounded_worker` validates before selection:

1. selection and authorization Replay destinations are inside the active
   session root;
2. request, decision, authorization, and result artifacts are present and
   public-hash valid;
3. native authorization Replay reconstructs as `EXECUTION_AUTHORIZED`;
4. request-to-decision-to-authorization-to-result hashes are exact;
5. authorization is not revoked and uses the G31-10 non-expiring `NEVER`
   boundary;
6. requested and authorized scopes are equal;
7. G31 execution-ready Replay reconstructs;
8. reconstructed grounded scope equals authorized scope;
9. Worker-selection certification is hash valid and certified;
10. the same authorization has not already produced a selection Replay.

The G31-10 scope retains the original goal, Project Objective, approved
Durable Governed Work, G31-04 through G31-09 hashes, workspace, grounded
Worker request, Repository Cognition snapshot, source and focused-test paths,
symbols, content hashes, mutation layers, and validation requirements.

Repository freshness remains owned by nested G31-06 validation. A changed
source file causes reconstruction to fail before the selector is called.

## Existing selected resource evidence

The default certified registry contains two compatible
`IMPLEMENTATION_ASSISTANCE` Worker-role candidates. Existing priority ordering
selects:

| Field | Selected evidence |
|---|---|
| resource identity | `CODEX` |
| resource category | `HYBRID_PROVIDER_WORKER` |
| resource version | `codex-hybrid-candidate-v1` |
| selected role | `WORKER_ROLE` |
| authority profile | `WORKER_AUTHORIZED_TASK_ONLY` |
| required capability | `IMPLEMENTATION_ASSISTANCE` |
| domain | `NATIVE_DEVELOPMENT` |
| lifecycle status | `AVAILABLE` |
| selection priority | `30` |

Selecting the Worker role does not invoke the Provider role of the hybrid
resource. The selection artifact and result retain `provider_invoked: false`
and `worker_invoked: false`.

## Existing no-match and ambiguity behavior

Focused evidence passes a valid registry with no compatible
`IMPLEMENTATION_ASSISTANCE` Worker role through the existing selector. It
returns its existing `FAILED_CLOSED` result and `no eligible resource`
diagnostic.

Focused ambiguity evidence gives the two compatible Worker-role resources the
same leading priority. The existing selector returns its existing
`FAILED_CLOSED` result and `ambiguous resource resolution` diagnostic. G31-11B
adds no tie-break policy and does not request a human resource choice.

## Canonical presentation

`render_authorized_grounded_worker_selection` is a bounded presentation
projection beside the G31-10 Platform Core binding. It renders only canonical
selection fields and the required stop state:

- selection status;
- selected resource identity;
- selected role;
- selection Replay reference;
- selected/not-selected state;
- assignment, dispatch, Provider, Worker, and mutation boundaries.

The reference AiCLI calls the binding after successful G31-10 authorization,
stores the returned canonical capture, and renders this projection. AiCLI does
not inspect the registry, evaluate eligibility, choose a candidate, validate
certification, authorize execution, or create Replay.

## Replay reconstruction and tamper rejection

The successful chain is reconstructable through existing artifacts:

```text
G31-04 binding and approval consumption
  -> G31-05 PPP, implementation request, Worker request, payload binding
  -> G31-06 Repository Cognition grounding and grounded Worker request
  -> G31-08 authorization review and execution summary
  -> G31-09 distinct human confirmation
  -> G31-10 execution-ready projection
  -> existing authorization request, decision, artifact, result
  -> existing RESOURCE_SELECTION_ARTIFACT_V1 and returned artifact
```

`reconstruct_authorized_grounded_worker_selection` composes the existing
authorization and selection reconstructors, validates the authorization
artifact with public hashing, and proves:

- exact authorization identity and hash in selection context;
- exact native-development vocabulary;
- exact default-registry hash;
- certified Worker-selection evidence;
- successful or existing fail-closed selector status;
- no dispatch or invocation;
- complete upstream G31 reconstruction.

Focused tests reject failed or expired authorization, scope broadening,
cross-session Replay, stale repository evidence, repeated authorization use,
context identity/hash substitution, registry substitution, capability/domain/
role substitution, hash-invalid certification, and reordered selection
Replay. Invalid evidence does not partially select or assign a Worker.

## Authority boundaries

A successful G31-11B result may state only:

```text
worker_selected = true
```

It always states:

```text
worker_assigned = false
worker_dispatched = false
provider_invoked = false
worker_invoked = false
command_executed = false
repository_mutated = false
```

The implementation does not import or call
`assign_worker_from_invocation_request`, Worker dispatch, Provider invocation,
Worker invocation, command execution, or repository mutation.

## Real PTY-backed terminal evidence

A real `./aicli` process ran in a PTY with:

- session: `G31-11B-PTY`;
- one disposable Git repository;
- one existing implementation file;
- one existing focused test;
- ordinary request: `Improve the human interface terminal summary behavior.
  Include focused tests and validation.`

The user supplied no path, JSON, Worker identity, capability name, prepared
artifact, prompt bridge, or shell bridge. The observed lifecycle was:

1. Platform Core produced the G31-04 proposal;
2. the first `/approve` consumed proposal approval;
3. Repository Cognition grounded exactly
   `aigol/runtime/human_interface.py` and
   `tests/test_human_interface.py`;
4. Platform Core presented the distinct execution review;
5. the second `/approve` created the G31-09 confirmation;
6. G31-10 returned `EXECUTION_AUTHORIZED`;
7. existing selection returned `RESOURCE_SELECTION_SUCCEEDED`;
8. existing selection chose `CODEX` with `WORKER_ROLE`;
9. canonical presentation reported the selected resource and all stop flags;
10. the session closed with `aicli_authorizes: False`,
    `aicli_executes: False`, and `aicli_owns_replay: False`.

Positive nested reconstruction reported:

```text
RESOURCE_SELECTION_SUCCEEDED CODEX True False False False False False False
```

The fields represent selection status, resource, complete lineage, assignment,
dispatch, Provider invocation, Worker invocation, command execution, and
repository mutation.

A copied PTY selection Replay was reordered. Reconstruction failed closed with
`resource selection replay ordering mismatch`. The disposable repository and
runtime were removed after validation. Source and focused-test contents
retained their original hashes during the run.

## Change size and minimality

Final direct-worktree accounting before this document:

| Category | Insertions | Deletions |
|---|---:|---:|
| production | 200 | 0 |
| tests | 273 | 2 |
| documentation | 449 | 0 |
| **total** | **922** | **2** |

Production changes are exactly at, and do not exceed, the 200-line mandatory
gate:

- `aigol/runtime/confirmed_grounded_execution_authorization_binding.py`:
  180 additions;
- `aigol/cli/aicli.py`: 20 additions.

No production file was added. The existing G31-10 module is the correct owner
for the authorization-to-selection compatibility edge. The existing AiCLI
file receives transport and rendering changes only.

The G31-09 regression now distinguishes the immutable G31-09 artifact's
pre-selection stop from the later operational session state. The G31-10
minimality assertion is extended from the accepted 300-line module to the
final 480-line module while retaining all copied-helper prohibitions.

## New production symbols

| Symbol | Current span | Caller | Responsibility and justification |
|---|---:|---|---|
| `WORKER_SELECTION_CERTIFICATION_PATH` | lines 59–61 | both new binding functions | Identifies the existing checked-in immutable certification report; no certification family or loader is created |
| `select_authorized_grounded_worker` | lines 310–401, 92 lines | AiCLI contextual second-approval continuation and focused tests | Validates exact authorization/scope/certification, calls the existing selector, reconstructs continuity, and returns canonical stop fields; no existing function owned this edge |
| `reconstruct_authorized_grounded_worker_selection` | lines 404–464, 61 lines | binding and independent Replay consumers | Composes existing authorization and selection reconstructors and checks context, registry, vocabulary, certification, and stop continuity |
| `render_authorized_grounded_worker_selection` | lines 467–480, 14 lines | reference AiCLI | Smallest Platform Core-owned projection because existing Canonical Presentation does not accept `RESOURCE_SELECTION_ARTIFACT_V1` directly |

Modified existing symbol `_record_contextual_execution_decision` invokes the
binding only after G31-10 succeeds. `run_reference_uhi_session` only renders
the returned projection.

## Duplicate-helper confirmation

G31-11B adds none of the G31-R01 consolidation observations:

- no local artifact-hash verifier;
- no required-string helper;
- no path normalizer;
- no Replay-preflight helper;
- no wrapper validator;
- no false-boundary abstraction.

Public `verify_replay_hash` and existing reconstructors are used directly.
Deferred consolidation remains deferred.

## Validation results

Focused results in the final production state:

| Suite | Result |
|---|---:|
| focused G31-11B | 17 passed, 0 skipped, 0 failed |
| G31-04 through G31-10 | 149 passed, 0 skipped, 0 failed |
| unified selection, ERR, Worker registry/certification, and assignment compatibility | 71 passed, 0 skipped, 0 failed |
| execution summary, confirmation, and authorization | 30 passed, 0 skipped, 0 failed |
| Replay-focused tests | 245 passed, 0 skipped, 0 failed |
| Human Interface and AiCLI | 42 passed, 0 skipped, 0 failed |
| Governance tests | 96 passed, 0 skipped, 0 failed |
| modified-production `py_compile` | passed |
| `git diff --check` | passed |
| full repository suite | 6,339 passed, 4 skipped, 0 failed |

Focused counts overlap and must not be added together as a repository total.

## Governance result

The deterministic read-only conformance engine remains:

- status: `PARTIALLY_CONFORMANT`;
- checks passed: 18;
- checks failed: 2;
- critical violations: 0;
- deterministic: true;
- fail-closed: true;
- read-only: true.

The two known hook-drift findings remain visible and unchanged. G31-11B does
not repair or reinterpret them.

## Progress and next state

Evidence-scoped no-copy/paste conversational governed-development progress is
now **98%**. Whole-project progress is **87%**. These are planning estimates,
not certification or production-readiness claims.

G31-11B proves Worker selection and stops. It does not establish whether the
existing certified G24 Worker-assignment contracts already accept the exact
G31-11B selection and G31-10 authorization lineage. Therefore the one next
state is deliberately reachability-oriented:

`EXISTING_G24_WORKER_ASSIGNMENT_REACHABILITY_UNVERIFIED`

No assignment implementation prompt is justified before that audit.

## Complete G31-12A AUDIT_ONLY prompt

```text
# Generation 31-12A — Existing Certified G24 Worker Assignment Reachability Audit

AUDIT_ONLY. Do not implement, modify runtime behavior, or create assignment,
dispatch, invocation, mutation, policy, registry, selector, or Replay code.

Treat Generation 30, committed G31-02 through G31-11B, G31-11A, and G31-R01
as immutable accepted baselines.

G31-11B verdict:

G31_10_AUTHORIZATION_TO_EXISTING_CERTIFIED_WORKER_SELECTION_OPERATIONAL

Next reachability state:

EXISTING_G24_WORKER_ASSIGNMENT_REACHABILITY_UNVERIFIED

## Objective

Determine from deterministic repository evidence whether existing certified
G24 Worker-assignment contracts can already consume:

- the exact G31-10 execution authorization;
- the existing G31-11B RESOURCE_SELECTION_ARTIFACT_V1 result;
- the selected existing Worker/resource identity and WORKER_ROLE;
- the complete grounded scope and G31-04 through G31-11B lineage;
- existing selection and authorization Replay;

and produce an assignment artifact while stopping before dispatch,
invocation, command execution, or repository mutation.

Do not assume assignment binding is absent. Prove reachability, bounded
projection need, incompatibility, or a deterministic blocker.

## Required inspection

Locate and document:

- all G24 Worker assignment entrypoints and artifact families;
- assign_worker_from_invocation_request and any lower-level assignment APIs;
- Worker identity, role, capability, availability, and trust validation;
- authorization, readiness, request, and selection inputs;
- assignment Replay and reconstructors;
- no-dispatch and no-invocation boundaries;
- existing Human Conversation Experience and presentation support;
- certification evidence and focused assignment tests.

Trace exact callers and callees. Compare every required G31-11B field with
existing G24 input fields. Distinguish directly available evidence, bounded
projection, incompatible semantics, and genuinely missing capability.

## Required behavioral evidence

Use read-only tests and disposable fixtures only. Verify existing positive,
unavailable, incompatible, stale, ambiguous, authorization-invalid, selection-
invalid, Replay-tampered, and already-assigned behavior. Do not dispatch or
invoke a Worker and do not mutate a repository.

Run focused G24 assignment, G31-10/G31-11B, Worker registry, selection,
authorization, Replay, Human Interface, Governance, py_compile, and
git diff --check validation. Do not run the full repository suite unless
focused evidence conflicts with certification evidence.

## Required verdict

Return exactly one:

- EXISTING_G24_WORKER_ASSIGNMENT_DIRECTLY_REACHABLE
- EXISTING_G24_WORKER_ASSIGNMENT_REUSABLE_BOUNDED_PROJECTION_REQUIRED
- EXISTING_G24_WORKER_ASSIGNMENT_INCOMPATIBLE
- EXISTING_G24_WORKER_ASSIGNMENT_RUNTIME_EVIDENCE_BLOCKED

## Documentation

Add only:

docs/governance/G31_12A_EXISTING_CERTIFIED_G24_WORKER_ASSIGNMENT_REACHABILITY_AUDIT.md

Document exact contracts, compatibility matrix, call-chain trace, Replay,
authority boundaries, focused evidence, verdict, and one next state.

Do not provide an assignment implementation prompt unless the audit proves a
bounded projection is required. Do not create a commit.
```

No commit was created by G31-11B.
