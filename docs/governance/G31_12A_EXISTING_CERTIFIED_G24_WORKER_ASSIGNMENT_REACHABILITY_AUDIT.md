# Generation 31-12A Existing Certified G24 Worker Assignment Reachability Audit

Status: completed audit; documentation only.

Date: 2026-07-16

Verdict:

`EXISTING_G24_WORKER_ASSIGNMENT_REUSABLE_BOUNDED_PROJECTION_REQUIRED`

Next reachability state:

`G31_11B_TO_EXISTING_G24_ASSIGNMENT_BOUNDED_PROJECTION_REACHABILITY_CONFIRMED`

## Constitutional scope

This audit treats Generation 30, committed G31-02 through G31-11B, G31-11A,
and G31-R01 as immutable accepted baselines. It does not reopen or redesign
Worker assignment, Worker identity, Worker invocation requests, Worker
registration, Worker selection, authorization, dispatch, Provider or Worker
invocation, Replay, Governance, Canonical Presentation, or Human Interface
semantics.

The only repository change is this report. No runtime, CLI, test, schema,
artifact-family, registry, policy, Governance, or Replay behavior changed.

## Plain-language conclusion

G24 Worker assignment is implemented, tested, certified, Replay-visible, and
stops before dispatch. It is not directly reachable from the G31-11B state.

The first unbound edge is before assignment: the existing public
`create_worker_invocation_request` cannot reconstruct the G31-10 execution-
ready Replay and does not consume G31-11B selection evidence. The current
deterministic error is:

`OCS execution readiness replay lineage mismatch`

Even after that loader mismatch is resolved, the existing assignment API
requires a `WORKER_INVOCATION_REQUEST_ARTIFACT_V1` and a compatible
`WORKER_ARTIFACT_V1`. No existing public projection preserves the selected
`CODEX` identity, `WORKER_ROLE`, authority profile, registry hash, selection
context, and selection Replay into those two existing artifact families.

This is bounded compatibility and lifecycle integration debt. It is not a
missing Worker-assignment capability or architectural incompatibility.

## Certified G24 architecture

The certified lifecycle is:

```text
EXECUTION_AUTHORIZED
  -> create_worker_invocation_request
  -> WORKER_INVOCATION_REQUEST_CREATED
  -> assign_worker_from_invocation_request
  -> WORKER_ASSIGNED
  -> reconstruct_worker_assignment_runtime_replay
  -> stop before dispatch
```

The checked-in governance certifications report:

- `AIGOL_WORKER_INVOCATION_REQUEST_RUNTIME_STATUS = CERTIFIED`;
- `AIGOL_WORKER_ASSIGNMENT_RUNTIME_STATUS = CERTIFIED`.

Certification sources:

- `governance/AIGOL_WORKER_INVOCATION_REQUEST_RUNTIME_CERTIFICATION.json`;
- `governance/AIGOL_WORKER_INVOCATION_REQUEST_RUNTIME_ACCEPTANCE_EVIDENCE.json`;
- `governance/AIGOL_WORKER_ASSIGNMENT_RUNTIME_CERTIFICATION.json`;
- `governance/AIGOL_WORKER_ASSIGNMENT_RUNTIME_ACCEPTANCE_EVIDENCE.json`.

## Exact public contracts

| File and public symbol | Existing caller | Existing callee | Canonical input | Canonical output | Authority and Replay owner | Tests / certification |
|---|---|---|---|---|---|---|
| `worker_invocation_request_runtime.py::detect_domain_worker_request_entry_intent` | `run_interactive_conversation` | narrow prompt detector only | operator text | domain/action detection | conversational routing; no lifecycle mutation | invocation-request tests and CLI acceptance |
| `worker_invocation_request_runtime.py::find_latest_domain_execution_authorization` | `run_interactive_conversation` | authorization and domain-bridge reconstructors | session root and domain | latest unconsumed authorization evidence | Worker-request lifecycle finder | invocation-request and domain-bridge tests |
| `worker_invocation_request_runtime.py::create_worker_invocation_request` | interactive CLI, orchestration, tests | authorization and execution-ready reconstructors | authorization Replay, request identity, actor/time | four existing Worker-request artifacts and capture | Worker invocation-request runtime; four-step Replay | `test_worker_invocation_request_runtime_v1.py`; certified |
| `worker_invocation_request_runtime.py::reconstruct_worker_invocation_request_replay` | assignment runtime, finders, tests | authorization-lineage loader | request Replay directory | validated request identity, role, family, scopes, Replay hash | Worker invocation-request Replay | focused Replay/tamper tests; certified |
| `worker_invocation_request_runtime.py::render_worker_invocation_request_summary` | `aigol_cli.py` | none | canonical request capture | textual canonical summary | existing presentation owner | CLI acceptance tests |
| `worker_assignment_runtime.py::detect_domain_worker_assignment_entry_intent` | `run_interactive_conversation` | prompt detector only | operator text | domain/action detection | conversational routing | assignment CLI tests |
| `worker_assignment_runtime.py::find_latest_domain_worker_invocation_request` | `run_interactive_conversation` | request and domain-bridge reconstructors | session root and domain | latest unassigned invocation request | assignment lifecycle finder | assignment and bridge tests |
| `worker_assignment_runtime.py::assign_worker_from_invocation_request` | CLI, orchestration, tests | request validator/reconstructor and compatible-Worker selector | existing invocation request, request Replay, Worker artifacts, actor/time | evidence, classification, `WORKER_ASSIGNMENT_ARTIFACT_V1`, result, capture | G24 Worker Assignment; four-step Replay | `test_worker_assignment_runtime_v1.py`; certified |
| `worker_assignment_runtime.py::reconstruct_worker_assignment_runtime_replay` | finders, later dispatch consumers, tests | request Replay validator | assignment Replay directory | validated assignment and stop boundaries | G24 assignment Replay | corruption/order tests; certified |
| `worker_assignment_runtime.py::default_worker_registry_for_request` | CLI, orchestration, tests | request validator | existing invocation request | one deterministic compatible `WORKER_ARTIFACT_V1` | G24 assignment compatibility utility | positive/failure assignment tests |
| `worker_assignment_runtime.py::render_worker_assignment_summary` | `aigol_cli.py` | none | canonical assignment capture | existing assignment presentation | Canonical Presentation path | CLI acceptance tests |
| `worker_runtime.py::register_worker` | Worker-runtime callers/tests | Worker artifact constructor | explicit Worker identity, capabilities, request types, trust boundary | registered `WORKER_ARTIFACT_V1` | lower-level Worker registration | `test_worker_runtime_v1.py` |
| `worker_runtime.py::assign_worker` | lower-level Worker-runtime callers/tests | readiness and Worker validators | registered Worker plus `READY_FOR_DISPATCH_ARTIFACT_V1` | lower-level `WORKER_ASSIGNMENT_ARTIFACT_V1` | separate older readiness-based assignment path | `test_worker_runtime_v1.py` |

The lower-level `worker_runtime.assign_worker` is not the G24 invocation-
request consumer and does not solve the G31 edge. The relevant certified entry
point is `assign_worker_from_invocation_request`.

## Existing artifact families

Worker invocation-request runtime already owns:

- `WORKER_INVOCATION_REQUEST_EVIDENCE_ARTIFACT_V1`;
- `WORKER_INVOCATION_REQUEST_CLASSIFICATION_ARTIFACT_V1`;
- `WORKER_INVOCATION_REQUEST_ARTIFACT_V1`;
- `WORKER_INVOCATION_REQUEST_RESULT_ARTIFACT_V1`.

Worker assignment runtime already owns:

- `WORKER_ASSIGNMENT_EVIDENCE_ARTIFACT_V1`;
- `WORKER_ASSIGNMENT_CLASSIFICATION_ARTIFACT_V1`;
- `WORKER_ASSIGNMENT_ARTIFACT_V1` from `worker_runtime.py`;
- `WORKER_ASSIGNMENT_RESULT_ARTIFACT_V1`.

No new family is needed for G31 compatibility.

## Invocation-request relationship and first blocker

The existing request artifact can represent:

- authorization identity and hash;
- execution packet identity and hash;
- canonical chain identity;
- one Worker role and target Worker family;
- allowed outputs;
- forbidden operations;
- validation requirements;
- authorization, ready, candidate, packet, handoff, and approval Replay
  references.

However, the public constructor currently supports governed dry-run and OCS
execution-ready lineage only. Its `_load_execution_ready_lineage` tries:

1. `reconstruct_governed_implementation_dry_run_replay`;
2. `reconstruct_ocs_execution_readiness_replay`.

It does not try the public G31
`reconstruct_confirmed_grounded_execution_ready_replay` contract. A disposable
G31-10/G31-11B fixture therefore produced:

```text
AUTHORIZATION EXECUTION_AUTHORIZED
SELECTION RESOURCE_SELECTION_SUCCEEDED CODEX WORKER_ROLE
INVOCATION_REQUEST_REACHABILITY FailClosedRuntimeError OCS execution readiness replay lineage mismatch
INVOCATION_REQUEST_ARTIFACT_CREATED False
ASSIGNMENT_ARTIFACT_CREATED False
```

The G31 validation artifact also represents exact grounded-scope validation
without the older `validation.handoff_hash` field expected by
`_load_authorized_lineage`. The candidate still contains the exact grounded
Worker-request reference and hash, so the semantic evidence exists; its older
field-level projection is not compatible.

The existing request schema also lacks an explicit binding for:

- G31-11B selection identity and artifact hash;
- selection Replay reference;
- selected resource identity/category/version;
- selected `WORKER_ROLE` and `WORKER_AUTHORIZED_TASK_ONLY` profile;
- registry hash and Worker-selection certification hash.

Therefore the invocation-request family is semantically reusable but the
existing public constructor is not directly compatible with G31.

## Assignment input compatibility

Once a valid existing invocation request and compatible Worker artifact are
available, `assign_worker_from_invocation_request` already validates:

- request artifact and native Replay;
- assignment replay availability;
- Worker artifact identity and hash;
- Worker availability;
- Worker family and role;
- execution packet compatibility;
- allowed-output and forbidden-operation coverage;
- false governance, approval, proposal, Provider, self-authorization, Replay-
  mutation, dispatch, invocation, execution, and completion authority;
- ambiguity and no-match behavior.

The missing selected-resource projection is equally bounded. The existing
`default_worker_registry_for_request` creates a compatible Worker artifact but
uses a generated `AIGOL-WORKER-*` identity and does not consume G31-11B
selection, registry, context, or certification evidence. The public lower-
level `register_worker` creates a basic Worker artifact but does not populate
the G24 `worker_family`, `worker_roles`, `compatible_execution_packets`,
`allowed_outputs`, or `forbidden_operations` fields required by the assignment
validator.

No existing public function projects `RESOURCE_SELECTION_ARTIFACT_V1` into the
extended `WORKER_ARTIFACT_V1` expected by G24 while preserving `CODEX`.

## Field-by-field compatibility matrix

| Required evidence | G31 source | Existing G24 consumer field | Classification | Finding |
|---|---|---|---|---|
| session identity | nested G31 decision/review and session-root Replay | no request or assignment field | `AVAILABLE_BUT_NOT_BOUND` | Present and reconstructable, but not projected into G24 lineage |
| Project Objective | G31 authorization scope | no explicit request/assignment field | `AVAILABLE_BUT_NOT_BOUND` | Equivalent evidence exists upstream |
| approved Durable Governed Work | G31 scope and nested lineage | no explicit field | `AVAILABLE_BUT_NOT_BOUND` | Hashes exist but are not carried by G24 request |
| grounded Worker request | G31 scope; candidate handoff reference/hash | request `handoff_reference` Replay entry | `DIRECTLY_AVAILABLE` | Exact semantic source exists |
| execution summary | authorization request/artifact | authorization lineage reconstructed by request runtime | `DIRECTLY_AVAILABLE` | Existing authorization Replay owns it |
| human confirmation | authorization request/artifact | authorization lineage reconstructed by request runtime | `DIRECTLY_AVAILABLE` | Existing authorization Replay owns it |
| authorization request | G31-10 authorization Replay | request runtime authorization loader | `DIRECTLY_AVAILABLE` | Existing family and Replay |
| authorization decision | G31-10 authorization Replay | request runtime authorization loader | `DIRECTLY_AVAILABLE` | Existing family and Replay |
| execution-authorization artifact | G31-10 authorization Replay | request `authorization_reference/hash` | `DIRECTLY_AVAILABLE` | Status, revocation, expiry, scope are valid |
| authorization status | `EXECUTION_AUTHORIZED` | constructor requires same | `DIRECTLY_AVAILABLE` | Exact vocabulary match |
| selected resource identity | G31-11B `CODEX` | assignment Worker `worker_id` | `AVAILABLE_BUT_NOT_BOUND` | No selection-to-Worker projection |
| selected role | G31-11B `WORKER_ROLE` | request/Worker uses goal-faithful implementation role | `AVAILABLE_BUT_NOT_BOUND` | Role layers are compatible but require deterministic mapping |
| resource category | `HYBRID_PROVIDER_WORKER` | no assignment field | `AVAILABLE_BUT_NOT_BOUND` | Must retain Worker-role separation |
| authority profile | `WORKER_AUTHORIZED_TASK_ONLY` | Worker false-authority fields | `AVAILABLE_BUT_NOT_BOUND` | Semantics are compatible; no public projection |
| Worker capability | `IMPLEMENTATION_ASSISTANCE` | Worker `capability_id`; request Worker role | `AVAILABLE_BUT_NOT_BOUND` | Existing evidence requires mapping into G24 vocabulary |
| Worker certification | checked-in G31-11B certification hash | no assignment input | `AVAILABLE_BUT_NOT_BOUND` | Certified evidence exists but G24 does not consume it |
| registry hash | selection artifact | no request/assignment field | `AVAILABLE_BUT_NOT_BOUND` | Required to preserve selected identity lineage |
| selection context reference | authorization identity | no request field | `AVAILABLE_BUT_NOT_BOUND` | Exact identity already equals authorization identity |
| selection context hash | authorization artifact hash | request `authorization_hash` | `DIRECTLY_AVAILABLE` | Equivalent semantics and exact value |
| workspace | G31 authorization scope | no explicit request field | `AVAILABLE_BUT_NOT_BOUND` | Available through nested G31 Replay |
| source paths | G31 scope / allowed outputs | request `allowed_outputs` | `AVAILABLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | G24 request projects packet allowed outputs on supported lineages |
| focused-test paths | G31 scope and allowed outputs/validation | request outputs and validation requirements | `AVAILABLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Semantics are present but current G31 loader blocks projection |
| symbols | G31 target evidence | no explicit request/assignment field | `AVAILABLE_BUT_NOT_BOUND` | Nested scope retains them |
| evidence hashes | G31 scope | no explicit request/assignment field | `AVAILABLE_BUT_NOT_BOUND` | Nested scope retains them |
| mutation layers | G31 target evidence | no explicit request/assignment field | `AVAILABLE_BUT_NOT_BOUND` | Nested scope retains them |
| validation requirements | G31 packet `required_validations` | request/assignment `validation_requirements` | `AVAILABLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Exact existing projection on supported lineage |
| assignment identity | assigned by G24 call | `worker_assignment_id` | `ABSENT` | Correctly created only at assignment; not missing architecture |
| complete Replay lineage | separate G31 authorization/selection and G24 reconstructors | no cross-generation caller | `AVAILABLE_BUT_NOT_BOUND` | Existing subsystems reconstruct; lifecycle edge is absent |
| Worker invocation request | existing certified family | required assignment input | `INCOMPATIBLE` | Public constructor rejects G31 ready Replay and lacks selection binding |
| selected `WORKER_ARTIFACT_V1` | selected resource plus registry evidence | required assignment candidate | `AVAILABLE_BUT_NOT_BOUND` | Existing family is reusable; selected-resource projection is absent |

No required field is classified as genuinely absent product architecture.
`ABSENT` assignment identity is intentionally created by the existing
assignment operation.

## Hybrid Worker/Provider role separation

G31-11B selected:

```text
resource_id = CODEX
resource_category = HYBRID_PROVIDER_WORKER
selected_role_type = WORKER_ROLE
authority_profile = WORKER_AUTHORIZED_TASK_ONLY
```

The selection artifact reports `provider_invoked: false` and
`worker_invoked: false`. The selected authority profile permits execution of
an authorized task but denies proposal, dispatch, authorization, governance,
Replay mutation, Provider invocation, and Worker invocation authority.

G24 assignment independently requires the projected Worker artifact to state:

- `provider_authority: false`;
- `governance_authority: false`;
- `approval_authority: false`;
- `proposal_authority: false`;
- `self_authorization: false`;
- `replay_mutation_authority: false`;
- `worker_dispatched: false`;
- `worker_invoked: false`;
- `execution_performed: false`.

A bounded projection can therefore preserve Worker-only authority without
selecting the Provider role. Current reachability does not perform that
projection.

## Exact current and expected call chains

Current reference AiCLI chain:

```text
_record_contextual_execution_decision
  -> authorize_confirmed_grounded_execution_decision
  -> select_authorized_grounded_worker
  -> select_unified_resource
  -> reconstruct_authorized_grounded_worker_selection
  -> render_authorized_grounded_worker_selection
  -> stop
```

Smallest expected reuse-first continuation:

```text
reconstruct_execution_authorization_replay
  -> reconstruct_confirmed_grounded_execution_ready_replay
  -> reconstruct_authorized_grounded_worker_selection
  -> bounded projection into existing WORKER_INVOCATION_REQUEST_ARTIFACT_V1
  -> create/reconstruct existing Worker invocation-request Replay
  -> bounded CODEX Worker-role projection into existing WORKER_ARTIFACT_V1
  -> assign_worker_from_invocation_request
  -> reconstruct_worker_assignment_runtime_replay
  -> render_worker_assignment_summary
  -> stop before dispatch
```

Exact existing caller: AiCLI `_record_contextual_execution_decision`, after
successful `select_authorized_grounded_worker`.

Exact first existing callee: `create_worker_invocation_request`.

Exact assignment callee: `assign_worker_from_invocation_request`.

The missing edge is G31 selection/authorization compatibility into the
existing invocation-request and Worker-artifact inputs. Presentation already
exists through `render_worker_invocation_request_summary`,
`render_worker_assignment_summary`, operational turn summaries, and Human
Interface runtime-entry assignment fields.

## Existing behavioral evidence

Focused G24 tests prove:

- successful invocation-request construction and assignment;
- filesystem, monitoring, and trading assignment cases;
- native and OCS execution-ready lineage support;
- authorization expiry and authority rejection;
- unavailable or missing Worker rejection;
- Worker family, role, packet, output, and forbidden-operation mismatch;
- Worker authority violation rejection;
- ambiguous compatible Worker rejection;
- append-only Replay and replayed-request protection;
- assignment Replay corruption and ordering rejection;
- no dispatch, invocation, execution, Provider authority, or repository
  mutation at assignment.

G31-focused tests prove no-match, selection ambiguity, failed/expired/
broadened authorization, cross-session evidence, stale Repository Cognition,
replayed selection, selection context/registry/vocabulary substitution,
certification tampering, and Replay reordering fail closed before assignment.

## Real PTY-backed observation

A real `./aicli` PTY session used a disposable Git repository containing one
implementation and one focused test. The user supplied only this ordinary
request:

`Improve the human interface terminal summary behavior. Include focused tests
and validation.`

Observed:

1. G31-04 proposal and first contextual approval;
2. deterministic repository grounding;
3. G31-09 second contextual approval;
4. G31-10 `EXECUTION_AUTHORIZED`;
5. G31-11B `RESOURCE_SELECTION_SUCCEEDED`;
6. selected `CODEX` in `WORKER_ROLE`;
7. `worker_selected: True`;
8. `worker_assigned: False`;
9. `worker_dispatched: False`;
10. `provider_invoked: False`;
11. `worker_invoked: False`;
12. no command execution or repository mutation;
13. session closure with `aicli_authorizes: False`, `aicli_executes: False`,
    and `aicli_owns_replay: False`.

The PTY runtime contained:

```text
INVOCATION_REQUEST_ARTIFACTS 0
ASSIGNMENT_ARTIFACTS 0
DISPATCH_ARTIFACTS 0
FIRST_UNBOUND_TRANSITION OCS execution readiness replay lineage mismatch
```

The disposable source and test retained their original hashes. The disposable
repository and runtime were removed. No assignment was attempted or repaired.

## Replay and authority assessment

G31 authorization and selection Replay reconstruct successfully. G24 request
and assignment Replay reconstruct successfully for their certified input
families. The missing caller does not require a new Replay subsystem: it must
compose existing reconstructors and bind cross-lineage identities into
existing artifacts.

Existing G24 assignment output truthfully sets `worker_assigned: true` while
retaining:

```text
worker_dispatched = false
worker_invoked = false
execution_started = false
execution_performed = false
completion_recorded = false
provider_authority = false
```

The audit itself creates none of these lifecycle artifacts.

## Focused validation

| Validation group | Result |
|---|---:|
| Worker invocation-request, G24 assignment, and lower-level Worker runtime | 48 passed, 0 skipped, 0 failed |
| unified resource selection, PPP integration, ERR, and Worker-selection certification | 34 passed, 0 skipped, 0 failed |
| G31-10 and G31-11B | 29 passed, 0 skipped, 0 failed |
| execution summary, confirmation, and authorization | 30 passed, 0 skipped, 0 failed |
| Replay-focused repository tests | 245 passed, 0 skipped, 0 failed |
| Human Interface and AiCLI | 42 passed, 0 skipped, 0 failed |
| Governance tests | 96 passed, 0 skipped, 0 failed |
| inspected production `py_compile` | passed |
| audit-document whitespace and `git diff --check` | passed |

Focused counts overlap and are not a repository-suite total. They agree with
checked-in certification evidence, so the full suite was not run.

## Governance result

The deterministic read-only conformance engine remains:

- status: `PARTIALLY_CONFORMANT`;
- checks passed: 18;
- checks failed: 2;
- critical violations: 0;
- deterministic: true;
- fail-closed: true;
- read-only: true.

The two known hook-drift findings remain visible and unchanged. They do not
affect the assignment compatibility conclusion.

## Minimal bounded implementation projection

The assignment capability and all artifact families already exist. The
smallest justified future unit should:

1. extend the existing public Worker invocation-request constructor to accept
   and reconstruct G31 confirmed execution-ready Replay;
2. validate G31-11B selection Replay and bind its context, registry,
   certification, selected identity, and Worker role into the existing request
   evidence/replay references;
3. preserve the exact G31 authorized scope, packet outputs, forbidden
   operations, and validation requirements;
4. deterministically project selected `CODEX` Worker-role evidence into the
   existing extended `WORKER_ARTIFACT_V1` input required by G24;
5. call unchanged `assign_worker_from_invocation_request`;
6. reuse unchanged assignment Replay and presentation;
7. stop before dispatch.

Maximum justified production additions: **200 lines**. Prefer modifications
to existing `worker_invocation_request_runtime.py`,
`worker_assignment_runtime.py`, and the existing AiCLI continuation. No new
production file or canonical artifact family is necessary.

Required focused tests must cover the positive CODEX Worker-role assignment,
request and selection identity continuity, Provider-role substitution,
registry/certification substitution, authorization/scope/repository staleness,
unavailable/incompatible/ambiguous Worker evidence, replayed assignment,
cross-session evidence, Replay ordering, canonical presentation, and all
pre-dispatch authority boundaries.

## Verdict and progress

The deterministic verdict is:

`EXISTING_G24_WORKER_ASSIGNMENT_REUSABLE_BOUNDED_PROJECTION_REQUIRED`

The assignment runtime is certified and semantically compatible. Direct
reachability is disproven by the current invocation-request loader and absent
selection-to-Worker projection. Architectural incompatibility is not proven.

Evidence-scoped no-copy/paste conversational governed-development progress
remains **98%**, and whole-project progress remains **87%**. This audit changes
knowledge, not runtime capability, so the established denominators do not
change.

Exactly one next reachability state is:

`G31_11B_TO_EXISTING_G24_ASSIGNMENT_BOUNDED_PROJECTION_REACHABILITY_CONFIRMED`

## Bounded G31-12B implementation prompt

```text
# Generation 31-12B — G31 Authorization and Selection to Existing Certified G24 Worker Assignment Binding

Treat Generation 30, committed G31-02 through G31-11B, G31-11A, G31-R01, and
the G31-12A audit as immutable accepted baselines.

G31-12A verdict:

EXISTING_G24_WORKER_ASSIGNMENT_REUSABLE_BOUNDED_PROJECTION_REQUIRED

Reachability state:

G31_11B_TO_EXISTING_G24_ASSIGNMENT_BOUNDED_PROJECTION_REACHABILITY_CONFIRMED

## Objective

Implement exactly one bounded reuse transition:

valid G31-10 execution authorization
  -> valid G31-11B RESOURCE_SELECTION_ARTIFACT_V1 selecting CODEX/WORKER_ROLE
  -> existing WORKER_INVOCATION_REQUEST_ARTIFACT_V1 and Replay
  -> existing WORKER_ARTIFACT_V1 compatibility input
  -> unchanged assign_worker_from_invocation_request
  -> existing WORKER_ASSIGNMENT_ARTIFACT_V1 and Replay
  -> existing canonical assignment presentation
  -> stop before dispatch

Do not create or redesign Worker assignment, invocation requests, Worker
identity, registry, selection, eligibility, authorization, dispatch, Replay,
Governance, or Human Interface semantics.

## Required bounded repairs

Reuse and minimally extend existing owners so that:

1. create_worker_invocation_request recognizes the public G31 confirmed
   execution-ready reconstructor;
2. G31 exact grounded-scope validation is accepted without inventing the
   older validation.handoff_hash field;
3. the existing invocation-request artifacts bind the exact G31-11B selection
   identity/hash, Replay reference, registry hash, certification hash,
   selected CODEX identity, WORKER_ROLE, and authorization context;
4. the selected CODEX Worker role is projected deterministically into the
   existing extended WORKER_ARTIFACT_V1 fields required by G24 assignment;
5. provider_authority and every Provider-role semantic remain false;
6. unchanged assign_worker_from_invocation_request creates the existing
   assignment artifacts and Replay;
7. existing render_worker_invocation_request_summary and
   render_worker_assignment_summary present the result;
8. the lifecycle stops before dispatch, invocation, command execution, or
   repository mutation.

Do not create a new canonical artifact family or production module. Maximum
production additions: 200 lines. Do not copy G31-R01 helper observations.

## Fail-closed requirements

Reject failed, expired, revoked, replayed, substituted, broadened, stale, or
cross-session authorization; changed grounded scope, Project Objective,
Durable Work, paths, symbols, evidence hashes, mutation layers, validation
requirements, selection context, registry, certification, resource identity,
resource category, role, authority profile, capability, or Replay; unavailable
or incompatible Worker evidence; Provider-role substitution; multiple
compatible Workers; already-assigned work; and reordered assignment Replay.

Invalid evidence must not partially create a request or assignment.

## Required stop state

worker_selected = true
worker_assigned = true
worker_dispatched = false
provider_invoked = false
worker_invoked = false
command_executed = false
repository_mutated = false

Do not call dispatch_assigned_worker or any Provider, Worker, command, or
mutation runtime.

## Validation

Add focused G31-12B tests for the exact positive transition and every required
failure boundary. Run G24 request/assignment, G31-10/G31-11B, registry,
selection, authorization, Replay, Human Interface/AiCLI, Governance,
py_compile, and git diff --check suites. Run the full repository suite once
only after focused evidence passes.

Perform a real PTY-backed ./aicli validation in a disposable repository using
only an ordinary request and contextual approvals. Demonstrate CODEX Worker-
role assignment through existing artifacts, truthful stop before dispatch,
nested Replay, fail-closed substitution, and zero invocation or mutation.
Remove the disposable repository afterward.

## Documentation

Add:

docs/governance/G31_12B_G31_SELECTION_TO_EXISTING_CERTIFIED_G24_WORKER_ASSIGNMENT_BINDING.md

Report exact files and line counts, public symbols, existing contracts reused,
PTY and Replay evidence, validation and governance counts, authority
boundaries, progress, and exactly one next reachability state. Do not commit.
```

No commit was created by this audit.
