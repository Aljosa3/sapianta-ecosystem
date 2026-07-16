# Generation 31-06 Approved Durable Governed Work Canonical Repository Scope Grounding

Status: implemented and operationally verified.

Date: 2026-07-15

Verdict:

`APPROVED_DURABLE_GOVERNED_WORK_CANONICAL_REPOSITORY_SCOPE_GROUNDING_OPERATIONAL`

Exactly one next blocker:

`CANONICALLY_GROUNDED_WORKER_REQUEST_EXECUTION_AUTHORIZATION_BINDING_ABSENT`

## Constitutional scope

This generation accepts Generation 30 and G31-02, G31-04, and G31-05 as
immutable baselines. It implements only this transition:

```text
approved G31-04 identities
  -> G31-05 goal-faithful Worker payload with unresolved scope
  -> existing Repository Cognition evidence
  -> immutable repository-scope grounding
  -> existing Worker-request scope projection
  -> stop before authorization, Worker selection, assignment, dispatch, or invocation
```

It creates no repository index, discovery framework, planner, router,
proposal, Worker payload family, clarification system, Replay subsystem,
Provider path, Worker path, mutation path, validation path, or certification
path.

## Pre-implementation reuse audit

The exact existing contracts inspected before implementation were:

| Existing contract | Reused behavior | G31-06 use |
|---|---|---|
| `platform_core_project_services` | Project Objective, exact canonical capability target, Knowledge Reuse, workspace continuity, and Human Interface-neutral context | Supplies the already-decided capability key; G31-06 does not reclassify the request |
| `platform_implementation_turn_durable_work_binding` | G31-04 plan, durable work, preview, approval request, approval consumption, and immutable identity validation | Every approved identity is consumed unchanged |
| `approved_durable_work_worker_payload_binding` | G31-05 PPP task package, implementation request, goal-faithful Worker request, field lineage, and unresolved-scope stop | Supplies the only admissible source payload and reconstructs its native Replay |
| `capability_audit_runtime.detect_capabilities` | Existing read-only Repository Cognition scan of `aigol/runtime`, `tests`, and governance evidence | Supplies existing implementation and focused-test paths; no second scanner or index was added |
| `platform_change_impact_analysis_runtime._constitutional_layer` | Existing canonical L0-L4 path classification | Classifies every selected target; L0/L1 targets fail closed |
| `implementation_request_to_worker_request_bridge_runtime` | Existing `WORKER_REQUEST_ARTIFACT_V1` and governance flags | Receives a bounded scope projection; no new Worker-payload type was created |
| existing Replay serialization | Immutable ordered wrappers and deterministic hashes | Records the source G31-05 artifact and one grounding artifact |
| existing Human Interface entry and Canonical Presentation | Platform Core result transport and terminal rendering | Renders identities, targets, hashes, failure, and stop state without selecting targets |

The smallest required binding was therefore one G31-06 grounding artifact and
one bounded projection function on the existing Worker-request contract.

## Grounding contract

The only new artifact type is:

`CANONICAL_REPOSITORY_SCOPE_GROUNDING_ARTIFACT_V1`

Its successful status is:

`CANONICAL_REPOSITORY_SCOPE_GROUNDED`

Its insufficient-evidence status is:

`CANONICAL_REPOSITORY_SCOPE_UNRESOLVED_FAILED_CLOSED`

The selection rule is deliberately narrow:

1. read the canonical capability target already present in the approved G31-05
   task package;
2. call the existing Repository Cognition capability audit;
3. require exactly one matching capability key with exactly one existing
   implementation target and at least one existing focused test;
4. observe only those paths returned by Repository Cognition;
5. require each resolved path to remain inside the selected workspace;
6. record byte-level content hash, top-level symbol locations, target role,
   canonical mutation layer, mapping rule, and per-target evidence hash;
7. bind the ordered evidence snapshot to the G31-05 artifact hash;
8. project only repository-scope fields into the existing Worker request.

Natural-language text never becomes a path. The implementation does not glob
for request terms, derive a filename convention, invent a test, select a shell
command, create a placeholder, or ask a Provider or Worker to choose targets.

## Evidence and identity continuity

Every successful artifact binds:

- G31-04 implementation-turn binding hash;
- approval-consumption hash;
- Development Composition Plan hash;
- Durable Governed Work hash;
- proposal-preview hash;
- approval-request hash;
- G31-05 PPP task-package hash;
- implementation-request hash;
- original Worker-request hash;
- Repository Cognition runtime identity;
- exact capability entry and snapshot hash;
- each workspace-relative source and focused-test path;
- each source byte hash;
- each observed symbol name, kind, line, and evidence hash;
- each canonical L0-L4 mutation classification;
- grounded Worker-request hash.

The projection is validated field by field. The original goal, Project
Objective, Platform Knowledge and Knowledge Reuse, capability coverage, plan,
Durable Governed Work, preview, approval, PPP task package, implementation
request lineage, Worker objective, requirements, constraints, and every
non-repository field remain byte-for-byte unchanged.

The grounded Worker request becomes ready only for a later, separate dispatch
governance transition. It does not request dispatch and creates no execution
authorization.

## Ambiguity and fail-closed behavior

Grounding remains explicitly unresolved when:

- the workspace is not a Git repository;
- the canonical capability target is unresolved;
- Repository Cognition has no exact implementation-and-test match;
- more than one materially different implementation target exists;
- required test evidence is absent.

Validation or reconstruction fails closed when:

- any G31-04 or G31-05 identity changes;
- a target is absolute, traverses outside the workspace, or resolves outside it;
- a target is missing, substituted, stale, or content-hash invalid;
- symbol or per-target evidence changes;
- mutation-layer evidence is missing, substituted, L0, or L1;
- Repository Cognition snapshot or grounding evidence changes;
- the grounded Worker objective, approval lineage, plan, or non-scope fields change;
- source or grounding Replay wrappers are removed, reordered, or substituted.

Insufficient evidence creates no partial target selection and no grounded
Worker request. Dispatch remains blocked.

## Replay

G31-06 records two ordered wrappers:

1. `approved_worker_payload_source_recorded`;
2. `canonical_repository_scope_grounding_recorded`.

Reconstruction first reconstructs the complete G31-05 chain, including its
G31-04 approval consumption and native PPP/implementation/Worker-request
Replay. It then validates the grounding wrapper, Repository Cognition
snapshot, every target and symbol hash, the grounded Worker projection, and
all cross-artifact identities. Optional workspace-backed reconstruction also
re-observes the files and rejects stale evidence.

## Authority boundaries

Both positive and unresolved artifacts report:

- `execution_authorized: false`;
- `provider_invoked: false`;
- `worker_selected: false`;
- `worker_assigned: false`;
- `worker_dispatched: false`;
- `worker_invoked: false`;
- `repository_mutated: false`;
- `validation_executed: false`;
- `certification_reached: false`;
- `human_interface_authority: false`;
- `human_interface_semantic_authority: false`;
- `human_interface_repository_selection_authority: false`.

Repository grounding is evidence binding. It is not approval, authorization,
selection, assignment, dispatch, invocation, mutation, validation, or
certification.

## Real PTY validation

A disposable Git repository contained only:

- `aigol/runtime/human_interface.py`, with one `render_summary` function;
- `tests/test_human_interface.py`, with one focused test.

The user entered only:

```text
Improve the human interface terminal summary behavior. Include focused tests and validation.
/send
/approve
```

The user supplied no paths, JSON, capability identifiers, prepared artifacts,
Codex prompt, or shell bridge. The real `./aicli` terminal displayed the
G31-04 proposal and approval identities, the G31-05 payload identities, and:

```text
grounding_status: CANONICAL_REPOSITORY_SCOPE_GROUNDED
grounded_repository_targets: ['aigol/runtime/human_interface.py', 'tests/test_human_interface.py']
grounded_focused_test_targets: ['tests/test_human_interface.py']
repository_scope_dispatch_blocked: False
```

Recorded PTY identities:

| Evidence | Hash |
|---|---|
| Development Composition Plan | `sha256:d2d2b2cd6941302188384003d3f1d8e85ff441dffb37678bb7a48cf3f4351d04` |
| Durable Governed Work | `sha256:6c582e1f22e609f974a6aca172daac3798a34fb32fa316dcdfa736b10c5fd992` |
| Proposal preview | `sha256:de7fe5281aa147a802dccd1048435748ddebb19de16f42c84844637fede6f472` |
| Approval request | `sha256:b41304808c5d76908f0b4ece544a00befe4ef1cf6dc34a9a29ddd6a9741470e9` |
| Approval consumption | `sha256:581b506019e11ca86a202e4bfd82273669c8d8f55b9d9cbdbda87735270df485` |
| PPP task package | `sha256:971d11988194f7075b7304d5d295eed7e9b6c92dafa0efa6a52209b14d663003` |
| Implementation request | `sha256:15d21083f074b7d1cfedcc0c42d6a56d5e6491d5edf0e3111106424bad5bb762` |
| G31-05 Worker payload | `sha256:70c6b0d410dcc12d9c649f9b37d79340118ec3d436516554997288b606c02a52` |
| Repository Cognition snapshot | `sha256:cf6b2cb42dba6f1de109e5ed751462257cdfb2762328bc9ec9df5383dd949580` |
| Grounded Worker request | `sha256:e1313fe6452d35fa93fcfb1a1d93b0c296fde073e3738a57e409c6b05884f202` |
| G31-06 grounding artifact | `sha256:e31af83f7689a5ce3bc7525a2f004526990f5232f1a51bbbd610918c99123082` |

Reconstruction returned the same grounding and Worker-request hashes with
authorization, dispatch, Worker invocation, and mutation false. After the
test harness changed the observed implementation file, reconstruction failed
closed with:

`repository target evidence is stale or substituted`

The disposable repository was removed after validation.

## Focused validation

All listed commands ran on 2026-07-15. Groups overlap and must not be added.

| Validation group | Result |
|---|---|
| Focused G31-06 | 31 passed, 0 skipped, 0 failed |
| G31-04 and G31-05 | 52 passed, 0 skipped, 0 failed |
| Repository Cognition and project context | 24 passed, 0 skipped, 0 failed |
| PPP and Worker payload | 49 passed, 0 skipped, 0 failed |
| Clarification, approval, authorization, Human Interface, and AiCLI | 163 passed, 0 skipped, 0 failed |
| G28, G29, G30, and G31-02 | 117 passed, 0 skipped, 0 failed |
| Replay | 245 passed, 0 skipped, 0 failed |
| Governance-named tests | 187 passed, 0 skipped, 0 failed |
| Targeted `py_compile` | passed |
| `git diff --check` | passed |
| Full repository suite | 6,256 passed, 4 skipped, 0 failed |

## Governance result

Repository governance remains `PARTIALLY_CONFORMANT`:

- checks passed: 18;
- checks failed: 2;
- critical violations: 0;
- deterministic: true;
- fail-closed: true;
- read-only: true.

The two findings are the visible pre-existing hook drift: the root expected
and installed pre-commit hooks are absent, and the system pre-commit hook lacks
`promotion_gate_v02` and `check_layer_freeze`. G31-06 does not repair, hide,
or reinterpret them.

## Change size and justification

The equivalent complete working-tree change stat, including the three
untracked new files, is:

```text
8 files changed, 2036 insertions(+), 6 deletions(-)
```

Runtime and CLI code: **957 lines added, 4 removed**.

Test code: **565 lines added, 2 removed**.

Documentation: **514 lines added, 0 removed**.

The implementation adds one bounded runtime artifact module and one focused
test module. Runtime integration changes are limited to the existing scope
projection, canonical runtime continuation, Platform Core result projection,
and terminal rendering.

New files:

- `aigol/runtime/approved_durable_work_repository_scope_grounding.py` — the
  single permitted grounding artifact, validator, renderer, and Replay
  reconstructor;
- `tests/test_g31_06_canonical_repository_scope_grounding.py` — focused
  identity, evidence, ambiguity, freshness, authority, Replay, and real-AiCLI
  regressions;
- this report — constitutional lineage, operational evidence, and bounded next
  work.

Modified runtime files:

- `implementation_request_to_worker_request_bridge_runtime.py` — projects
  only validated repository-scope evidence into the existing Worker-request
  type and validates that projection;
- `aigol_cli.py` — invokes the Platform Core grounding binding after G31-05 and
  records a non-executing turn summary;
- `human_interface_runtime_entry_service.py` — transports the resulting
  Platform Core identities and state without acquiring authority;
- `aicli.py` — renders the canonical grounding fields without inspecting or
  selecting repository targets.

The G15 regression is updated because the accepted G31 path now stops at
repository grounding rather than the superseded G31-05 unresolved-scope
status. Historical non-G31 behavior remains available outside the canonical
approval gate.

## Progress and next blocker

Evidence-scoped progress toward complete no-copy/paste conversational governed
development is **87%**, using the same denominator as G31-03 (62%), G31-04
(72%), and G31-05 (80%). This is a planning estimate, not a certification
claim.

The exact next blocker is:

`CANONICALLY_GROUNDED_WORKER_REQUEST_EXECUTION_AUTHORIZATION_BINDING_ABSENT`

G31-06 proves exact repository scope and stops. It does not prove that the
grounded request can enter the existing separate execution-authorization
lifecycle. Worker selection, assignment, dispatch, Provider availability,
implementation cognition, mutation, validation, repair, and certification are
downstream and remain unbundled.

## Proposed Generation 31-07 prompt

```text
# Generation 31-07 — Canonically Grounded Worker Request Execution Authorization Binding

Treat Generation 30 and accepted G31-02, G31-04, G31-05, and G31-06 results as
immutable baselines.

G31-06 verdict:

APPROVED_DURABLE_GOVERNED_WORK_CANONICAL_REPOSITORY_SCOPE_GROUNDING_OPERATIONAL

First true blocker:

CANONICALLY_GROUNDED_WORKER_REQUEST_EXECUTION_AUTHORIZATION_BINDING_ABSENT

Primary priority:

NO_COPY_PASTE_CONVERSATIONAL_GOVERNED_DEVELOPMENT_THROUGH_AICLI

## Objective

Implement exactly one transition.

Bind one valid G31-06 canonically grounded Worker request into the existing
separate execution-authorization review lifecycle.

Produce either:

1. one existing, immutable execution-authorization request or candidate bound
   to the exact grounded scope and all upstream identities; or
2. an existing owner-specific clarification or explicit fail-closed state when
   authorization evidence is insufficient.

Do not select, assign, dispatch, or invoke a Worker. Do not invoke a Provider
or mutate the repository.

## Required reuse

Reuse existing:

- G31-04 approval identities and approval consumption;
- G31-05 task package and Worker payload lineage;
- G31-06 Repository Cognition evidence, grounding artifact, and grounded
  Worker-request projection;
- execution-authorization request, policy, validation, and Replay contracts;
- Governance and human-approval boundaries;
- Human Conversation Experience and Canonical Presentation.

Do not create another approval system, authorization system, Worker request,
policy engine, router, selector, clarification system, or Replay subsystem.

Before implementation, document the exact reusable authorization contracts
and the smallest required binding.

## Required behavior

For one valid G31-06 artifact:

approved G31-04 identities
  -> G31-05 goal-faithful Worker payload
  -> G31-06 exact repository grounding
  -> existing execution-authorization review/request contract
  -> immutable authorization decision evidence or fail-closed review state
  -> stop before Worker selection, assignment, dispatch, or invocation

The authorization scope must be exactly the grounded workspace-relative paths,
symbols, tests, mutation layers, validation requirements, objective, and
approved bounded work. It must not broaden targets, operations, commands,
authority, or lifecycle stage.

Proposal approval is not execution authorization. If the existing lifecycle
requires a distinct human authorization decision, preserve and present that
checkpoint instead of manufacturing authorization from `/approve`.

## Fail-closed requirements

Reject before authorization readiness if:

- any G31-04, G31-05, or G31-06 identity changes;
- Repository Cognition evidence is stale, missing, substituted, or reordered;
- grounded paths, symbols, focused tests, mutation layers, or hashes change;
- requested authority exceeds the approved and grounded scope;
- policy, approval, authorization, or Replay lineage is absent or invalid;
- a target is L0/L1 or otherwise incompatible;
- authorization would imply Worker/Provider invocation or repository mutation.

No invalid evidence may partially authorize work or influence later Worker
selection.

## Minimal-change constraint

Prefer one existing-function binding. Introduce at most one bounded binding
artifact only if the existing authorization contract cannot represent the
transition directly.

Do not add general authorization architecture or bundle Worker selection.
Stop and report deterministic evidence if broad changes are required.

## Focused tests

Prove at minimum:

- all upstream identities and grounded targets are consumed unchanged;
- proposal approval remains distinct from execution authorization;
- authorization scope equals the G31-06 evidence exactly;
- missing or insufficient authorization evidence clarifies or fails closed;
- stale, substituted, reordered, broadened, or incompatible scope fails closed;
- no command, target, authority, Worker, or Provider is invented;
- no Worker selection, assignment, dispatch, invocation, or mutation occurs;
- AiCLI owns no authorization or policy semantics;
- complete Replay reconstructs and rejects tampering;
- unrelated G28-G31 paths remain unchanged.

## Real terminal validation

Use a disposable Git repository with one existing implementation and one
focused test. Through real PTY-backed `./aicli`, use one ordinary bounded
natural-language change request and demonstrate:

1. G31-04 proposal and approval;
2. G31-05 Worker payload;
3. G31-06 exact repository grounding;
4. the separate authorization review/request state;
5. one missing, tampered, or broadened authorization fail-closed case;
6. complete Replay reconstruction;
7. truthful stop before Worker selection and dispatch.

The user must not supply paths, internal JSON, capability names, prepared
artifacts, a Codex prompt, or shell bridges. Remove the disposable repository.

## Validation

Run and report exact pass, skip, and failure counts for:

- focused G31-07 tests;
- G31-04 through G31-06 regressions;
- execution authorization and human approval;
- Repository Cognition, PPP, and Worker-request tests;
- clarification, Human Interface, and AiCLI;
- G28, G29, G30, and G31-02;
- Replay and Governance;
- `py_compile`;
- `git diff --check`;
- full repository suite.

## Documentation

Add:

docs/governance/G31_07_CANONICALLY_GROUNDED_WORKER_REQUEST_EXECUTION_AUTHORIZATION_BINDING.md

Document reuse, exact authorization contract, identity and scope continuity,
human checkpoint semantics, Replay, authority boundaries, PTY evidence,
validation, change size, and exactly one next blocker or readiness verdict.

## Non-goals

Do not:

- redesign certified architecture;
- merge proposal approval with execution authorization;
- select, assign, dispatch, or invoke a Worker;
- invoke a Provider;
- mutate the repository;
- implement Worker cognition, validation, repair, certification, or completion;
- repair Provider availability or governance hook drift;
- add products, domains, interfaces, dashboards, or deployment;
- bundle downstream blockers;
- claim complete no-copy/paste readiness.

## Required final report

Provide:

1. implementation verdict;
2. changed files and change-size report;
3. reused authorization capabilities;
4. exact authorization artifact and evidence contract;
5. positive and fail-closed PTY results;
6. Replay and tamper evidence;
7. approval-versus-authorization assessment;
8. authority confirmation;
9. exact validation and governance results;
10. exactly one next blocker or readiness verdict;
11. no-copy/paste progress using the G31-03-G31-06 denominator;
12. exact git status and commit commands;
13. complete bounded G31-08 prompt.

Architectural minimalism is mandatory.
```
