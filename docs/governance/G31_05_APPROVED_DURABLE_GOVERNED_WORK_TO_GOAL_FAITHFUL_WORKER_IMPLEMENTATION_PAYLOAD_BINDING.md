# Generation 31-05 Approved Durable Governed Work to Goal-Faithful Worker Implementation Payload Binding

Status: bounded operational transition implemented and validated.

Date: 2026-07-15

Verdict:

`APPROVED_DURABLE_GOVERNED_WORK_TO_GOAL_FAITHFUL_WORKER_IMPLEMENTATION_PAYLOAD_BINDING_OPERATIONAL`

Next first blocker:

`APPROVED_DURABLE_GOVERNED_WORK_CANONICAL_REPOSITORY_SCOPE_GROUNDING_ABSENT`

## Constitutional scope

Generation 30 remains the immutable certified constitutional baseline. G31-02
remains the bounded Product 1 extension and G31-04 remains the canonical
implementation-turn proposal and exact-approval binding.

G31-05 adds one transition only. Once the Canonical Human Interface Runtime
Entry has validated and consumed the exact G31-04 approved identities, it
projects the immutable approved work into existing PPP candidate, governed
implementation-request, and Worker-request contracts. It does not classify,
plan, repropose, authorize execution, select a Provider or Worker, dispatch,
invoke, mutate, validate, or certify implementation.

## Mandatory reuse audit

The following contracts were inspected before the binding was implemented.

| Required responsibility | Existing owner and reusable contract | Canonical source or operational consumer | Pre-G31-05 state |
|---|---|---|---|
| G31-04 implementation-turn binding | `validate_implementation_turn_durable_work_binding` and `reconstruct_implementation_turn_durable_work_binding` | `PLATFORM_IMPLEMENTATION_TURN_DURABLE_WORK_BINDING_ARTIFACT_V1` | Fully bound through approval preparation |
| Exact approval consumption | `consume_approved_implementation_turn_binding`, validator, and reconstructor | `PLATFORM_IMPLEMENTATION_TURN_APPROVAL_CONSUMPTION_ARTIFACT_V1` | Fully bound at Canonical Human Interface Runtime Entry |
| Canonical Human Interface Runtime Entry | `run_human_interface_runtime_entry` | Consumes the exact plan, durable-work, preview, and ApprovalRequest hashes | Bound to G31-04; full downstream artifacts were not transported |
| Conversational continuation | `run_interactive_conversation` | `GOVERNED_DEVELOPMENT_WORKFLOW` turn | Historical generic bridge remained selected after approval |
| Native development-context restoration | `run_conversation_native_development_context_integration` | Existing native context artifact and Replay | Reusable; no new context subsystem required |
| PPP composition and routing | `PPP_CANDIDATE_ARTIFACT_V1`, `bridge_improvement_intent_to_ppp_candidate`, and `run_conversation_to_ppp_handoff_execution` | Existing PPP candidate and routing contracts | Format reusable; G31 approved-work source absent |
| Governed implementation task package | `create_governed_implementation_request` and its reconstructor | `IMPLEMENTATION_REQUEST_ARTIFACT_V1` | Reusable after bounded approved-source admission |
| Worker implementation payload | `bridge_implementation_request_to_worker_request` and its reconstructor | `WORKER_REQUEST_ARTIFACT_V1` | Reusable; approved field lineage and unresolved-scope dispatch boundary absent |
| Worker objective and scope | Existing `implementation_objective`, `worker_objective`, `implementation_scope`, and constraints fields | Implementation-request to Worker-request bridge | Present but not populated from G31-04 approved work |
| Repository context and scope | G31-04 `repository_context` and proposal-preview repository fields | Existing proposal preview | Explicitly unresolved; no grounded targets existed |
| Test, validation, governance, Replay, certification, and acceptance inputs | Existing plan, Durable Governed Work, and preview fields | Projected implementation scope | Present except acceptance requirements, which were not supplied by the approved artifacts |
| Execution authorization | Existing Governance authorization runtimes | Downstream of payload and dispatch governance | Deliberately unreached |
| Provider selection and invocation | Existing Provider Platform | Downstream and separately governed | Deliberately unreached |
| Worker selection, assignment, dispatch, and invocation | Existing Worker Platform runtimes | Downstream of dispatch governance | Deliberately unreached |
| Progress and failure presentation | Existing Platform Core turn summary and reference AiCLI rendering | Canonical terminal output | Reused with a bounded G31-05 payload projection |
| Replay | Existing immutable wrapper, hash, and reconstruction utilities plus native reconstructors | G31-04 binding, approval consumption, task package, implementation request, Worker request | Needed one composition root across the existing Replays |

The reusable non-executing artifact chain is therefore:

```text
PPP_CANDIDATE_ARTIFACT_V1
  -> IMPLEMENTATION_REQUEST_ARTIFACT_V1
  -> WORKER_REQUEST_ARTIFACT_V1
```

`EXTERNAL_WORKER_TASK_PACKAGE_V1` is post-authorization and was not created or
reached. No second task-package format, Worker-payload format, approval system,
Provider system, Worker system, presentation layer, or Replay implementation
was introduced.

## Minimal binding

`bind_approved_durable_work_to_worker_payload` performs the bounded transition:

1. validates the complete G31-04 binding with `require_ready=True`;
2. validates the approval-consumption artifact;
3. compares every approval-consumption identity with the approved binding;
4. projects one hash-bound implementation scope from approved artifacts;
5. creates an existing-type PPP candidate with source
   `APPROVED_DURABLE_GOVERNED_WORK`;
6. derives a compatibility `HUMAN_APPROVAL_ARTIFACT_V1` whose scope is only
   `CREATE_IMPLEMENTATION_REQUEST_ONLY` and explicitly excludes execution;
7. calls the existing governed implementation-request runtime;
8. calls the existing implementation-request-to-Worker-request bridge;
9. validates task, request, Worker payload, field lineage, repository scope,
   and boundary flags;
10. records one composition artifact and reconstructable ordered Replay.

The gate in `run_interactive_conversation` is active only when the canonical
runtime entry transports both a validated G31-04 binding and its exact
approval-consumption artifact. The historical bridge remains callable outside
that gate. The canonical approved path never calls
`propose_acli_governed_development_execution`.

## Approved identity continuity

The PPP task package, implementation request, Worker payload, and outer
binding carry the same immutable identities for:

- original human goal and hash;
- Project Objective and hash;
- Platform Knowledge identity and hash;
- Knowledge Reuse identity and hash;
- capability-composition coverage identity and hash;
- Development Composition Plan identity and hash;
- Durable Governed Work ID and hash;
- proposal-preview identity and hash;
- ApprovalRequest identity and hash;
- approval-consumption identity and hash.

The outer binding also compares the PPP candidate to the implementation
request, the implementation request to the Worker request, both downstream
artifacts to the approved-work lineage, and all three copies of the approved
implementation scope. A replacement objective, task package, request, Worker
payload, source hash, or scope cannot be accepted merely by changing one outer
reference.

## Goal-faithful Worker payload projection

The existing `implementation_scope` and `WORKER_REQUEST_ARTIFACT_V1` now
receive, without natural-language regeneration:

- the unchanged original human request;
- the unchanged canonical Project Objective;
- approved Knowledge, Reuse, coverage, plan, durable-work, proposal, approval,
  and consumption identities;
- bounded work scope and residual implementation gaps;
- the approved ordered implementation sequence;
- repository-scope status and only canonical repository targets;
- focused-test requirements;
- validation, governance, Replay, and certification requirements;
- acceptance requirements when present; none were present in the G31-04
  source artifacts, so the projection is truthfully empty;
- one field-lineage entry for every field group.

Each field-lineage entry records source artifact type, source identity, and
source hash. The Worker objective equals the implementation-request objective,
which equals the preserved Project Objective in the approved PPP package.

The canonical payload contains neither
`AIGOL_GENERIC_DEVELOPMENT_TASK_V1` nor `WORKER_FOUNDATION`. Both fallback flags
are false.

## Repository-grounding behavior

The real G31-05 request retained G31-04 status:

`UNRESOLVED_WITHIN_CANONICAL_CAPABILITY_BOUNDARY`

No file, module, function, test path, validation command, capability identity,
or implementation detail was invented. The Worker request was generated as a
non-executing implementation payload but reports:

- `ready_for_worker_dispatch_governance: false`;
- `dispatch_blocked_by_unresolved_repository_scope: true`;
- no repository targets;
- `APPROVED_DURABLE_WORK_WORKER_PAYLOAD_SCOPE_UNRESOLVED_FAILED_CLOSED`.

Focused evidence also proves that already canonically grounded paths are
preserved exactly and become eligible only for a separate dispatch-governance
step. G31-05 does not create that grounding.

## Approval and authority boundaries

Proposal approval remains distinct from execution authorization. The consumed
approval permits only canonical continuation and implementation-request
composition. It does not authorize Worker dispatch, Provider invocation,
Worker invocation, repository mutation, validation, certification, or
deployment.

The final binding records false for:

- execution authorization;
- Provider invocation;
- Worker selection, assignment, dispatch, and invocation;
- repository mutation;
- validation and certification;
- Human Interface semantic, planning, Provider, Worker, mutation, approval,
  authorization, and Replay authority.

Platform Core cognition remains responsible for the approved meaning and
plan. Worker cognition was not used to repair missing repository scope.

## Replay and tamper evidence

The G31-05 Replay order is:

```text
G31-04 implementation-turn binding
  -> G31-04 approval consumption
  -> approved-work PPP task package
  -> governed implementation request and returned artifact
  -> Worker request and returned artifact
  -> approved-work Worker-payload composition binding
```

Reconstruction invokes the native G31-04, implementation-request, and
Worker-request reconstructors. It then validates the G31-05 wrappers, ordering,
artifact hashes, copied identities, scope hash, task-to-request lineage,
request-to-Worker lineage, and boundary flags.

Focused tamper tests reject:

- original-goal replacement;
- Project Objective, Platform Knowledge, Knowledge Reuse, coverage, plan,
  Durable Governed Work, preview, ApprovalRequest, consumption, or binding
  identity substitution;
- a changed approval-consumption record;
- task-package objective substitution;
- Worker objective substitution;
- reordered or changed Replay wrappers.

All fail before dispatch, Provider invocation, Worker invocation, or mutation.

## Real PTY validation

A real `./aicli` PTY session ran in a disposable isolated Git repository. The
only user content was this ordinary goal:

```text
Improve the human interface runtime and canonical presentation for terminal development summaries.
Include focused tests and validation.
```

The terminal produced the G31-04 canonical proposal and accepted `/approve`.
It then displayed these exact identities:

- Development Composition Plan:
  `sha256:dc6b40930f56c2385ddd307b0910097ff260d809499250adbeea6a460714b7b5`;
- Durable Governed Work:
  `sha256:50cef5eebe07b4dbb6e29dcbdb2ad9c11d88a082501ee64c18d97a9aafc96242`;
- proposal preview:
  `sha256:fe3a602a2518e6bdf776ea1254f9cf4fbcd92ae3b9b0d88a4dcd744e1ebd0436`;
- ApprovalRequest:
  `sha256:10bae22142ed3d9160872e92fe706506f153713d9181435171478984b3caacab`;
- approval consumption:
  `sha256:0965d3fd222c4e7940adf70b2b05ad993689870b345da02c3af97871d77bc836`;
- PPP task package:
  `sha256:2322095245f4740f1721e3f25a5b99fb069c34d89a5666b10d9dd31d9bcc0042`;
- implementation request:
  `sha256:4598bdc888164ca7e29f513800a02c10cb2deb6f801f96c9f8fe8a6b2bf5c1ee`;
- Worker implementation payload:
  `sha256:469ed6dec7f0036ee4d864a95338e960f5e8d45a987af453d08411b8cd0070ac`.

Replay reconstruction returned the same ordered hashes. It confirmed both
generic-fallback flags false, Provider and Worker invocation false, repository
mutation false, and dispatch blocked true. The terminal truthfully stopped at
unresolved repository scope. The disposable repository contained only its
generated runtime evidence, was exited normally, and was removed after the
hashes and observations were recorded.

## Validation results

Final validation on 2026-07-15:

- focused G31-05 tests: **28 passed, 0 skipped, 0 failed**;
- G31-04 regressions: **24 passed, 0 skipped, 0 failed**;
- native development-context and PPP task-package tests: **42 passed, 0 skipped, 0 failed**;
- Worker payload, selection, assignment, and dispatch-boundary tests:
  **97 passed, 0 skipped, 0 failed**;
- repository-context and project-cognition tests:
  **31 passed, 0 skipped, 0 failed**;
- Human Interface and AiCLI tests: **55 passed, 0 skipped, 0 failed**;
- clarification, approval, and authorization tests:
  **59 passed, 0 skipped, 0 failed**;
- G28, G29, all G30, and G31-02 regressions:
  **117 passed, 0 skipped, 0 failed**;
- Replay reconstruction tests: **245 passed, 0 skipped, 0 failed**;
- Governance tests: **96 passed, 0 skipped, 0 failed**;
- targeted `py_compile`: passed;
- `git diff --check`: passed;
- full repository suite: **6,226 passed, 1 skipped, 0 failed**.

Focused counts overlap the full repository suite and must not be added.

One G15 regression had asserted that reference-AiCLI approval entered the
historical generic bridge and reached Provider/Worker execution. That
expectation conflicts with the G31-05 constitutional boundary for a valid
G31-04 approval-consumption artifact. The regression now verifies payload
composition, zero Provider/Worker calls, and the unresolved-scope stop. The
historical bridge remains available outside the validated G31 gate.

## Governance result

Repository governance remains:

`PARTIALLY_CONFORMANT`

The read-only deterministic engine reports:

- checks passed: 18;
- checks failed: 2;
- critical violations: 0;
- deterministic: true;
- fail-closed: true;
- read-only: true.

The two pre-existing findings remain visible: root pre-commit hook absence and
the system hook missing `promotion_gate_v02` and `check_layer_freeze`. G31-05
does not repair or reinterpret them.

## Remaining limitations, next blocker, and progress

Exactly one next first blocker is established by both repository and PTY
evidence:

`APPROVED_DURABLE_GOVERNED_WORK_CANONICAL_REPOSITORY_SCOPE_GROUNDING_ABSENT`

The approved work reaches a goal-faithful Worker implementation payload, but
the arbitrary request has no approved, canonical mapping to exact repository
targets. Dispatch must remain blocked until existing Repository Cognition can
produce an immutable, approval-bound, fail-closed grounding artifact or ask
owner-specific clarification. Provider availability, execution authorization,
Worker selection, mutation, validation, and certification are downstream and
were not repaired or reassessed beyond this blocker.

Evidence-scoped progress toward complete no-copy-paste governed development is
**80%**, using the same denominator as G31-03 (62%) and G31-04 (72%). This is a
planning estimate, not a certification claim. G31-05 closes the exact
approved-work-to-goal-faithful-payload transition; repository grounding and
all subsequent execution, mutation, validation, and certification remain
unproven through the complete reference-AiCLI lifecycle.

## Recommended Generation 31-06 prompt

```text
# Generation 31-06 — Approved Durable Governed Work Canonical Repository Scope Grounding

Treat Generation 30 as the immutable certified constitutional baseline.

Accept G31-02, G31-04, and G31-05 as bounded certified or operational
extensions. Do not reopen their responsibilities.

G31-05 concluded:

APPROVED_DURABLE_GOVERNED_WORK_TO_GOAL_FAITHFUL_WORKER_IMPLEMENTATION_PAYLOAD_BINDING_OPERATIONAL

The first true blocker is:

APPROVED_DURABLE_GOVERNED_WORK_CANONICAL_REPOSITORY_SCOPE_GROUNDING_ABSENT

The primary priority remains:

NO_COPY_PASTE_CONVERSATIONAL_GOVERNED_DEVELOPMENT_THROUGH_AICLI

## Objective

Implement exactly one bounded transition: use existing Repository Cognition
and project-context evidence to ground an approved G31-05 implementation
payload to exact existing repository targets, or fail closed with
owner-specific clarification when deterministic grounding is insufficient.

The grounding must remain bound to the unchanged original goal, Project
Objective, Platform Knowledge, Knowledge Reuse, capability coverage,
Development Composition Plan, Durable Governed Work, proposal preview,
ApprovalRequest, approval consumption, PPP task package, implementation
request, and Worker payload identities.

Do not authorize, select, assign, dispatch, or invoke a Worker. Stop at the
next first downstream blocker.

## Mandatory reuse audit

Before changing code, locate and verify existing contracts for:

- Repository Cognition and workspace inspection;
- project-context restoration;
- repository artifact and symbol evidence;
- source and focused-test path discovery;
- mutation-boundary and layer classification;
- clarification ownership and continuation;
- G31-04 proposal and approval identities;
- G31-05 implementation scope and field lineage;
- Worker-request dispatch readiness;
- execution authorization;
- Replay reconstruction and canonical presentation.

For every grounding field, document its owner, canonical evidence, hash, and
consumer. Reuse existing ownership. Do not create a second repository index,
router, planner, proposal, approval, Worker payload, or Replay subsystem.

## Required bounded behavior

For a valid G31-05 payload with unresolved repository scope:

1. consume the exact approved and payload identities;
2. inspect only the user-selected workspace through existing Repository
   Cognition;
3. produce one immutable repository-scope grounding artifact containing only
   deterministically supported existing paths, symbols, tests, and relevant
   validation evidence;
4. record source identity and hash for every grounded target;
5. bind the grounding artifact to the existing implementation scope without
   regenerating or replacing the approved goal, objective, plan, proposal, or
   payload;
6. preserve mutation-layer and constitutional boundaries;
7. mark the Worker request eligible only for a later, separate dispatch and
   execution-authorization decision;
8. reconstruct the complete G31-04 -> G31-05 -> grounding Replay chain.

If deterministic evidence cannot establish one exact compatible scope, use
the existing owner-specific clarification lifecycle or retain an explicit
fail-closed unresolved-scope state. Do not guess.

## Grounding and tamper requirements

Fail closed before dispatch readiness if:

- any upstream approved or G31-05 payload identity changes;
- a target is outside the selected workspace;
- a path, symbol, test, or command lacks canonical repository evidence;
- repository evidence is stale, missing, ambiguous, or hash-invalid;
- mutation-layer classification is absent or incompatible;
- grounding lineage, ordering, or Replay is substituted;
- clarification ownership or scope is changed.

Do not infer repository targets from natural language alone. Do not invoke a
Provider or Worker to choose paths. Do not create files to make a guessed
scope appear valid.

## Required terminal lifecycle

Demonstrate through a real PTY-backed `./aicli` session in a disposable Git
repository containing a small existing implementation and focused test:

ordinary bounded implementation goal
  -> G31-04 canonical proposal
  -> /approve and exact approval consumption
  -> G31-05 goal-faithful Worker payload
  -> existing Repository Cognition
  -> immutable canonical repository-scope grounding or owner-specific
     clarification
  -> truthful stop before authorization, Worker selection, dispatch,
     invocation, or mutation

The user must not provide capability identifiers, internal JSON, prepared
artifacts, a Codex prompt, shell bridges, task packages, Worker payloads, or
manually enumerated repository paths.

Prove a positive deterministic grounding case and an ambiguous or tampered
fail-closed case. Remove the disposable repository afterward.

## Authority boundaries

Preserve:

- Platform Core ownership of semantics and planning;
- Repository Cognition ownership of repository evidence;
- human approval distinct from execution authorization;
- Governance ownership of later authorization;
- Provider and Worker authority outside AiCLI;
- Worker-only repository mutation;
- Replay as source of truth;
- AiCLI neutrality;
- fail-closed behavior;
- no deployment or uncontrolled self-modification.

Repository grounding is evidence binding, not approval, authorization,
dispatch, invocation, mutation, validation, or certification.

## Non-goals

Do not:

- redesign Platform Core or any certified generation;
- add routing, classification, planning, proposal, approval, conversation,
  Provider, Worker, dispatch, or Replay subsystems;
- repair Provider availability;
- invoke Worker cognition;
- authorize execution;
- mutate the repository;
- implement validation or certification;
- invent paths, symbols, tests, commands, capabilities, or implementation
  details;
- bundle later Worker selection, dispatch, execution, mutation, or return-flow
  work;
- repair unrelated governance hook drift;
- claim complete no-copy-paste readiness.

## Focused tests

Prove:

1. exact upstream G31-04 and G31-05 identities are consumed;
2. grounded paths and symbols derive only from immutable Repository Cognition
   evidence;
3. the original goal, Project Objective, plan, durable work, and Worker
   objective remain unchanged;
4. canonically supported source and focused-test targets are preserved exactly;
5. ambiguity produces existing owner-specific clarification or explicit
   fail-closed state;
6. no target is invented;
7. stale, substituted, out-of-workspace, or hash-invalid evidence fails closed;
8. every upstream identity substitution fails closed;
9. payload and grounding substitution fails closed;
10. no execution authorization, Provider, Worker, dispatch, invocation, or
    mutation occurs;
11. AiCLI retains no semantic, repository-selection, approval,
    authorization, Worker, Provider, mutation, or Replay authority;
12. complete ordered Replay reconstructs and rejects reordering;
13. G28, G29, G30, G31-02, G31-04, G31-05, informational, and AUDIT_ONLY
    routes remain unchanged;
14. historical compatibility remains available outside the approved path.

## Validation

Run focused G31-06 tests; G31-04 and G31-05 regressions; Repository Cognition
and project-context tests; native PPP and Worker-payload tests; clarification,
approval, authorization, Human Interface, and AiCLI tests; G28 and G29; all
G30; G31-02; Replay; Governance; py_compile; git diff --check; and the full
repository suite. Report exact pass, skip, and failure counts.

## Documentation

Add:

docs/governance/G31_06_APPROVED_DURABLE_GOVERNED_WORK_CANONICAL_REPOSITORY_SCOPE_GROUNDING.md

Document exact reuse, repository evidence, grounding artifact, identity
continuity, clarification or fail-closed behavior, Replay, tamper evidence,
authority boundaries, PTY observations, validation, and exactly one next first
blocker or deterministic readiness verdict.

## Required final report

Provide implementation verdict, summary, changed files, reused capabilities,
grounding contract, identity continuity, PTY evidence, Replay/tamper evidence,
authority confirmation, exact validation and governance results, remaining
limitations, exactly one next blocker or readiness verdict, evidence-scoped
progress, exact git status, recommended commit commands, and the complete
bounded G31-07 prompt.
```

## Conclusion

G31-05 closes the exact approved-durable-work-to-goal-faithful-Worker-payload
gap without changing certified architecture. The reference AiCLI now transports
the immutable approved identities into existing native task and Worker payload
contracts, bypasses the generic marker fallback only on that path, reconstructs
the full prefix, and stops safely because repository scope is not yet
canonically grounded.
