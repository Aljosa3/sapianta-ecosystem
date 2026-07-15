# Generation 31-04 Canonical Implementation Turn to Durable Governed Work Proposal Binding

Status: implemented and validated as one bounded lifecycle transition.

Date: 2026-07-15

Implementation verdict:

`CANONICAL_IMPLEMENTATION_TURN_TO_DURABLE_GOVERNED_WORK_PROPOSAL_BINDING_OPERATIONAL`

Next first blocker:

`APPROVED_DURABLE_GOVERNED_WORK_TO_GOAL_FAITHFUL_WORKER_IMPLEMENTATION_PAYLOAD_BINDING_ABSENT`

## Constitutional scope

This milestone treats Generation 30 as the immutable certified constitutional
baseline and accepts G31-02 as a bounded certified Product 1 extension. It
implements the first integration identified by G31-03 without reopening
Platform Core, G28, G29, G30, G31-02, Replay, Governance, Certification,
Human Interface neutrality, Provider authority, Worker authority, or
repository-mutation authority.

Exactly one transition is added:

```text
ordinary IMPLEMENTATION turn
  -> existing capability-composition coverage
  -> existing Development Composition Plan
  -> existing Durable Governed Work
  -> canonical proposal preview
  -> approval bound to exact immutable identities
  -> existing Canonical Human Interface Runtime Entry consumes those identities
```

The milestone does not claim that the downstream Worker implementation
payload, execution authorization, Provider selection, Worker invocation,
repository mutation, validation, Replay certification, or canonical completion
is operationally bound.

## Mandatory reuse audit

The implementation reuses the following repository capabilities and contracts
before adding any binding logic.

| Existing responsibility | Exact reused implementation or artifact |
|---|---|
| Development-intent and work-type resolution | `resolve_development_intent`, `resolve_governed_work_type`, and `prepare_unified_human_interface_project_context` in `platform_core_project_services.py` |
| Project Objective | `infer_platform_project_objective` and `validate_platform_project_objective`; `PLATFORM_PROJECT_OBJECTIVE_ARTIFACT_V1` |
| Platform Knowledge | `query_platform_knowledge` through coverage discovery and `validate_platform_knowledge_response`; `PLATFORM_KNOWLEDGE_RESPONSE_ARTIFACT_V1` |
| Knowledge Reuse and repository state | existing Project Services knowledge-reuse evidence, persistent workspace state, project knowledge index, and repository context projection |
| Clarification continuity | existing operational clarification envelope, owner/slot continuity, attachment retry, and Human Conversation Experience clarification response |
| Capability composition | `discover_platform_capability_composition_coverage` and `validate_platform_capability_composition_coverage`; `PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_ARTIFACT_V1` and the certified `PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_RUNTIME` |
| Development plan | `compose_platform_development_plan` and `validate_platform_development_composition_plan`; `PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_ARTIFACT_V1` |
| Durable governed work | `compose_durable_governed_work`, `validate_durable_governed_work`, and `reconstruct_durable_governed_work`; `PLATFORM_DURABLE_GOVERNED_WORK_ARTIFACT_V1` |
| Proposal and approval contract | the Durable Governed Work `approval_request`, `approval_request_id`, and `approval_request_hash`; existing approval-required Human Conversation Experience |
| Canonical continuation | `run_human_interface_runtime_entry` and the existing governed conversation runner |
| Human Conversation Experience | `human_conversation_experience_from_resolution`, `_conversation_experience_artifact`, and `_conversation_approval_summary` |
| Canonical Platform Presentation | existing governed-development, Development Composition Plan, and Durable Governed Work presentation contracts; AiCLI only renders supplied Platform Core fields |
| Replay | existing immutable JSON wrapper, `replay_hash`, nested artifact validators, and runtime/workspace Replay recording |

No second planner, Durable Governed Work runtime, approval engine,
clarification system, conversation layer, presentation layer, or Replay system
was created.

## Minimal binding implementation

The new
`platform_implementation_turn_durable_work_binding.py` module is a narrow
composition and identity-validation adapter. It provides three new binding
artifacts, not new constitutional responsibilities:

- `PLATFORM_IMPLEMENTATION_TURN_DURABLE_WORK_BINDING_ARTIFACT_V1` binds the
  original turn and every canonical source identity;
- `PLATFORM_IMPLEMENTATION_TURN_PROPOSAL_PREVIEW_ARTIFACT_V1` projects only
  facts present in the existing source artifacts;
- `PLATFORM_IMPLEMENTATION_TURN_APPROVAL_CONSUMPTION_ARTIFACT_V1` records that
  the Canonical Human Interface Runtime Entry consumed the exact four approved
  hashes.

The principal functions are:

- `compose_implementation_turn_durable_work_binding`;
- `validate_implementation_turn_durable_work_binding`;
- `validate_implementation_turn_proposal_preview`;
- `consume_approved_implementation_turn_binding`;
- `validate_implementation_turn_approval_consumption`;
- `reconstruct_implementation_turn_durable_work_binding`;
- `reconstruct_implementation_turn_approval_consumption`.

Project Services invokes the binding only for a sufficiently clear,
summary-admissible `IMPLEMENTATION` turn. Existing informational, read-only,
AUDIT_ONLY, G29 clarification, and artifact-ingress routes remain outside this
branch.

The existing candidate-capability result is projected into the existing
coverage-gap contract only when Project Services has already determined that
new work or a bounded extension is required. This projection supplies no new
classifier, selector, or planner and is validated by the unchanged capability
coverage validator before the existing plan composer runs.

## Canonical artifact transition

The resulting lifecycle is:

```text
natural-language implementation goal
  -> prepare_unified_human_interface_project_context
  -> canonical Project Objective
  -> Platform Knowledge and Knowledge Reuse
  -> PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_ARTIFACT_V1
  -> PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_ARTIFACT_V1
  -> PLATFORM_DURABLE_GOVERNED_WORK_ARTIFACT_V1
  -> PLATFORM_IMPLEMENTATION_TURN_PROPOSAL_PREVIEW_ARTIFACT_V1
  -> pending ApprovalRequest with exact immutable identities
  -> /approve
  -> PLATFORM_IMPLEMENTATION_TURN_APPROVAL_CONSUMPTION_ARTIFACT_V1
  -> Canonical Human Interface Runtime Entry
  -> unchanged governed continuation
```

Project Services stores the complete binding in the governed development
resolution and approval summary. AiCLI renders that summary and transports the
binding plus the four exact hashes back to
`run_human_interface_runtime_entry`. The entry validates the complete nested
binding, records immutable approval consumption, and supplies the consumed
identities to the existing continuation namespace. It does not recompose the
proposal after approval.

## Proposal projection

The pre-approval projection truthfully exposes source-backed fields for:

- the original human goal and canonical Project Objective;
- Platform Knowledge and Knowledge Reuse summaries and identities;
- reusable certified capabilities and compositions;
- residual capability gaps and the minimal bounded extension;
- ordered implementation work;
- repository-scope status;
- focused tests and validation requirements present in the plan;
- governance, Replay, and certification dependencies;
- the meaning and limits of human approval;
- the immutable plan, Durable Governed Work, preview, and ApprovalRequest
  identities and hashes.

The preview is `proposal_only`. It explicitly records that approval is not
execution authorization. AiCLI does not calculate, infer, repair, or enrich
any proposal field.

## Repository grounding

The existing evidence can bound the capability gap and ordered governed work,
but it cannot deterministically name exact target files for an arbitrary
ordinary implementation request. G31-04 therefore records:

`UNRESOLVED_WITHIN_CANONICAL_CAPABILITY_BOUNDARY`

and an empty `proposed_repository_paths` list. The explanation states that
exact paths are deferred and were not invented by Platform Core or AiCLI.

This is an explicit unresolved-scope state permitted by the milestone. It
does not fall back to generated marker files, module names, test names,
validation commands, or external prompt completion. If the existing coverage,
plan, or Durable Governed Work contracts cannot establish even the bounded
capability scope, the binding is not approval-admissible and fails closed.

## Immutable approval identity

Approval is accepted only when all nested source artifacts validate and the
supplied pending state exactly matches:

- `development_composition_plan_hash`;
- `durable_governed_work_hash`;
- `proposal_preview_hash`;
- `approval_request_hash`.

The outer binding also locks:

- original request hash;
- Project Objective hash;
- Knowledge Reuse snapshot hash;
- Platform Knowledge hash;
- capability-composition coverage hash;
- Durable Governed Work ID;
- ApprovalRequest ID;
- the outer binding hash.

A bare textual `/approve` without a matching pending canonical summary cannot
enter the runtime. A changed nested artifact, changed identity, or substituted
hash raises a fail-closed runtime error before canonical continuation.

Human approval records consent to continue with this exact immutable proposal.
It does not authorize execution.

## Replay and tamper evidence

The transition records ordered immutable wrappers:

1. `000_implementation_turn_binding_recorded.json`;
2. `001_implementation_turn_approval_consumed.json`.

Reconstruction validates wrapper index, step, artifact type, artifact hash,
and the nested Project Objective, Knowledge Reuse, Platform Knowledge,
coverage, plan, Durable Governed Work, preview, and ApprovalRequest lineage.

Focused tests prove fail-closed behavior for substitution or mutation of:

- Project Objective;
- Knowledge Reuse or Platform Knowledge evidence;
- capability-composition coverage;
- Development Composition Plan;
- Durable Governed Work;
- proposal preview;
- ApprovalRequest;
- each of the four approval hashes;
- wrapper identity, order, or artifact hash.

Replay reconstruction succeeds for the untouched binding and approval
consumption and rejects tampered evidence.

## Authority boundaries

Before approval, the binding and preview explicitly record:

- Provider invoked for Worker execution: `false`;
- Worker invoked: `false`;
- execution authorized: `false`;
- repository mutated: `false`;
- validation executed: `false`;
- certification reached: `false`;
- Human Interface semantic authority: `false`;
- Human Interface planning authority: `false`;
- Human Interface approval authority: `false`;
- Human Interface execution authority: `false`.

After approval, the consumption artifact preserves the same false authority
and execution flags. The only new fact is that human approval was recorded and
the exact identities may enter canonical continuation. Governance,
authorization, Provider, Worker, mutation, validation, and certification
boundaries remain separate.

## Real PTY validation

A real PTY-backed `./aicli` run was performed in a disposable isolated Git
repository at `/tmp/g31-04-durable-work-fixture`. The repository contained a
small existing Python module, its focused test, and a README. Its baseline
commit was:

`5a2441272e9a50a5fb6ba055f1c36e2c0098bc6e`

The user supplied only this ordinary goal:

```text
Add a small documented function that normalizes a user-visible label by
trimming surrounding whitespace and collapsing internal whitespace.
Include focused tests, run the relevant validation, and report completion.
```

No capability identifier, internal JSON, prepared proposal, Codex prompt,
Worker payload, shell bridge, or manually constructed artifact was supplied.

Before approval the terminal displayed:

- the canonical Project Objective;
- `NEW_GOVERNED_WORK` Knowledge Reuse classification;
- no reuse recommendation;
- a genuinely new capability gap;
- the existing Development Composition Plan and ordered work;
- the existing Durable Governed Work ID;
- an explicit unresolved-but-bounded repository scope with no invented paths;
- focused and relevant validation requirements from canonical evidence;
- all immutable identities;
- `approval_is_execution_authorization: False`.

The exact approval identities were:

| Identity | PTY value |
|---|---|
| Development Composition Plan hash | `sha256:05fedbefb5f76623f00f303136fb9bfda73a2b5b3aa6874984707b2e001db03a` |
| Durable Governed Work ID | `PLATFORM-GOVERNED-WORK-05FEDBEFB5F76623F00F3031` |
| Durable Governed Work hash | `sha256:347d9e53d32d979466b7bc3535ca5975a8c1a8b57a782cf306974964d7a50bda` |
| Proposal preview hash | `sha256:7f15549c4bb6caeafb3b0e8ea69f23a302ea3fb389551dedd47ec26f8dab4ac9` |
| ApprovalRequest hash | `sha256:a9042436cfcc3573c798bf85f033dc637dfba6802f6e0b6f5bb3f6fa58338697` |

After `/approve`, the Canonical Human Interface Runtime Entry reconstructed
and consumed the same four hashes. The immutable PTY Replay wrapper file
digests were:

- binding wrapper:
  `c7ed26a1c95db6ad331e5945c9277826188dafa7ec93eb133318b62429c2749d`;
- Durable Governed Work wrapper:
  `9c311d0c87788fd74023707826623b8ad39d34e9a35d8f8022350a1287a1c55c`;
- approval-consumption wrapper:
  `fcb3b44a490f48f0fff9ecb807bd829dfd1d168c58b7b179289f61a09f0a1f07`.

All reconstructed identity comparisons were true. The run remained partially
bound after entering the downstream runtime: governance authorization,
Provider invocation, Worker execution, and Replay certification were not
reached. The fixture's tracked files remained identical to the baseline. The
disposable repository and runtime evidence were removed after these hashes and
observations were recorded.

## Exact validation results

Validation completed on 2026-07-15:

| Validation surface | Result |
|---|---|
| Focused G31-04 tests | 24 passed, 0 skipped, 0 failed |
| G20/G21/G22 planning and Durable Governed Work regressions | 52 passed, 0 skipped, 0 failed |
| Project Services, Platform Knowledge, repository context, and repository cognition | 25 passed, 0 skipped, 0 failed |
| Human Interface and AiCLI clean rerun | 41 passed, 0 skipped, 0 failed |
| Clarification, continuation, and approval clean rerun | 28 passed, 0 skipped, 0 failed |
| G28 and G29 regressions | 73 passed, 0 skipped, 0 failed |
| All Generation 30 tests | 38 passed, 0 skipped, 0 failed |
| G31-02 Product 1 onboarding | 6 passed, 0 skipped, 0 failed |
| Replay reconstruction focused set | 44 passed, 0 skipped, 0 failed |
| Governance pytest | 5 passed, 0 skipped, 0 failed |
| Targeted `py_compile` | passed |
| `git diff --check` | passed |
| Full repository suite | **6,197 passed, 4 skipped, 0 failed** |

Focused groups overlap the full suite and must not be added together.

## Governance result

Governance remains:

`PARTIALLY_CONFORMANT`

The deterministic conformance engine reported:

- checks passed: 18;
- checks failed: 2;
- critical violations: 0;
- deterministic: true;
- fail-closed: true;
- read-only: true;
- report hash:
  `sha256:0790499b2233c7e7437fe8110674eef1efaf990a455fc99f1f9200b8d8c2e508`.

The two failures are the known pre-existing hook-drift findings: missing
expected/installed root pre-commit hooks and a system pre-commit hook missing
`promotion_gate_v02` and `check_layer_freeze`. G31-04 does not hide or repair
them. No new critical governance violation was introduced.

## Remaining bounded limitations

The approved plan, Durable Governed Work, preview, and ApprovalRequest
identities now reach and are consumed by the Canonical Human Interface Runtime
Entry. The unchanged inner development continuation does not yet use that
Durable Governed Work as the goal-faithful implementation payload.

In the PTY run, the downstream runtime regenerated the historical generic
marker proposal:

- `docs/governance/ACLI_GOVERNED_DEVELOPMENT_01F38D2195FADEB2_V1.md`;
- `aigol/runtime/acli_governed_development_01f38d2195fadeb2.py`;
- only `git diff --check` as validation.

The PPP handoff remained the generic
`AIGOL_GENERIC_DEVELOPMENT_TASK_V1` / `WORKER_FOUNDATION` prompt and retained
the known statement `Seed proposal is not an implementation proposal.` The
Provider then failed closed as unavailable. Provider availability is a later
downstream observation, not the first causal blocker.

G31-04 intentionally stops here. It does not manually bridge, authorize,
invoke, mutate, validate, or certify the requested repository work.

## Next first blocker and progress

Exactly one next first blocker remains:

`APPROVED_DURABLE_GOVERNED_WORK_TO_GOAL_FAITHFUL_WORKER_IMPLEMENTATION_PAYLOAD_BINDING_ABSENT`

This is bounded integration debt between the consumed approved identities and
the existing native development/PPP Worker payload. It is not evidence of a
missing Platform Core planner, approval system, Worker, Provider, Replay
system, or Human Interface responsibility.

Evidence-scoped progress toward complete no-copy-paste governed development
through the reference AiCLI is **72%**. This is a planning estimate, not a
certification claim. Canonical proposal composition, immutable pre-approval
presentation, exact approval consumption, and Replay continuity are now
operational. Goal-faithful downstream Worker payload binding, execution,
mutation, validation, and certification remain unproven.

## Recommended Generation 31-05 prompt

```text
# Generation 31-05 — Approved Durable Governed Work to Goal-Faithful Worker Implementation Payload Binding

Treat Generation 30 as the immutable certified constitutional baseline.

Accept G31-02 as the bounded certified Product 1 extension.

Accept G31-04 as the bounded operational implementation-turn proposal binding.

G31-04 concluded:

CANONICAL_IMPLEMENTATION_TURN_TO_DURABLE_GOVERNED_WORK_PROPOSAL_BINDING_OPERATIONAL

The first true blocker is:

APPROVED_DURABLE_GOVERNED_WORK_TO_GOAL_FAITHFUL_WORKER_IMPLEMENTATION_PAYLOAD_BINDING_ABSENT

The restored primary development priority remains:

NO_COPY_PASTE_CONVERSATIONAL_GOVERNED_DEVELOPMENT_THROUGH_AICLI

## Objective

Implement exactly one bounded downstream transition.

After the Canonical Human Interface Runtime Entry has validated and consumed
the exact approved G31-04 Development Composition Plan, Durable Governed Work,
proposal preview, and ApprovalRequest identities, bind that same immutable
Durable Governed Work to the existing native development/PPP Worker
implementation payload.

The payload must remain goal-faithful to the preserved Project Objective,
capability-composition evidence, Development Composition Plan, Durable
Governed Work, and approved proposal. It must not regenerate or substitute the
historical generic marker-module proposal.

Implement only this payload-binding transition. Stop at the next first
downstream blocker.

## Mandatory reuse audit

Before changing code, locate and verify the existing contracts for:

- G31-04 implementation-turn binding and approval consumption;
- Canonical Human Interface Runtime Entry;
- conversational development proposal and approval continuation;
- native development context restoration;
- PPP task-package composition and routing;
- Worker task, objective, repository-context, file-scope, test, validation,
  and acceptance payload fields;
- Provider and Worker selection;
- execution authorization;
- Worker mutation boundaries;
- progress and failure presentation;
- Replay recording and reconstruction.

Reuse existing ownership. Do not create a second proposal, task-package,
Worker-payload, Provider, Worker, approval, presentation, or Replay system.

Document the exact reused functions and artifacts before describing any new
binding.

## Required lifecycle

Demonstrate through real `./aicli` operation:

ordinary natural-language IMPLEMENTATION goal
  -> G31-04 canonical Project Objective, coverage, plan, Durable Governed Work,
     preview, and exact approval identities
  -> /approve
  -> G31-04 approval consumption
  -> existing canonical continuation
  -> existing native development/PPP task-package contract
  -> goal-faithful Worker implementation payload bound to the exact approved
     Durable Governed Work and source-plan identities

The transition must use the same approved hashes. It must not reclassify,
replan, or create a replacement proposal after approval.

## Payload requirements

The existing Worker implementation payload must receive, where present in the
approved canonical artifacts:

- the original human goal;
- canonical Project Objective and hash;
- Knowledge Reuse and Platform Knowledge identities;
- capability-composition coverage identity;
- Development Composition Plan identity and hash;
- Durable Governed Work ID and hash;
- proposal-preview hash;
- ApprovalRequest identity and hash;
- bounded work scope and residual gaps;
- ordered implementation sequence;
- repository-scope status and only canonically grounded paths;
- focused tests and validation requirements;
- governance, Replay, certification, and acceptance requirements.

Every field must be traceable to the approved immutable source. Do not invent
file paths, module names, tests, validation commands, or implementation details.

If exact repository targets remain unresolved, use the existing owner-specific
clarification or fail closed before Worker dispatch. Do not use a generic
marker module or an external prompt to fill missing scope.

## Approval and tamper boundary

Fail closed before task-package or Worker dispatch if any approved G31-04
identity changes, including:

- Project Objective;
- Knowledge Reuse or Platform Knowledge;
- capability-composition coverage;
- Development Composition Plan;
- Durable Governed Work;
- proposal preview;
- ApprovalRequest;
- approval-consumption record;
- task-package lineage;
- Worker-payload lineage.

A textual approval or a replacement proposal must not satisfy this boundary.

## Authority boundary

Preserve:

- Platform Core ownership of semantics, planning, and state;
- human approval distinct from execution authorization;
- existing Governance ownership of authorization;
- Provider selection outside AiCLI;
- Worker-only implementation and repository mutation;
- Replay as source of truth;
- AiCLI neutrality and opaque transport;
- fail-closed behavior;
- no production deployment or uncontrolled self-modification.

Do not use Worker cognition before the approved identities are consumed and
the existing authorization boundary permits dispatch.

Do not repair Provider availability in this milestone.

## Generic fallback correction

For the G31-04-approved canonical implementation path, bypass the historical
generic marker proposal and generic
`AIGOL_GENERIC_DEVELOPMENT_TASK_V1` / `WORKER_FOUNDATION` payload.

Do not delete historical compatibility behavior unless deterministic
regression evidence proves retirement is required. Keep the correction scoped
to continuation carrying a validated G31-04 approval-consumption artifact.

## Required focused tests

Add focused G31-05 tests proving:

1. exact G31-04 approved identities enter the existing native task-package;
2. the Worker implementation payload is derived from the approved plan and
   Durable Governed Work;
3. the generic marker fallback is not used on this path;
4. the payload remains goal-faithful to the original request and Project
   Objective;
5. grounded repository scope is preserved and unresolved scope fails closed or
   clarifies without invented paths;
6. each approved identity substitution fails closed before dispatch;
7. task-package or Worker-payload substitution fails closed;
8. approval remains distinct from execution authorization;
9. AiCLI has no semantic, planning, Provider, Worker, mutation, approval, or
   authorization authority;
10. Replay reconstructs binding, approval consumption, task package, and Worker
    payload in order;
11. unrelated informational, AUDIT_ONLY, G28, G29, G30, and G31-02 routes are
    unchanged;
12. historical compatibility behavior remains available outside the
    G31-04-approved path.

## Required terminal validation

Perform a real PTY-backed `./aicli` experiment in a disposable isolated Git
repository using an ordinary bounded implementation goal.

Do not provide capability identifiers, internal JSON, prepared proposals,
Codex prompts, shell bridges, or manually constructed Worker payloads.

Demonstrate:

1. G31-04 canonical proposal and exact identities;
2. `/approve` and exact approval consumption;
3. goal-faithful native task-package and Worker payload composition;
4. absence of the generic marker fallback;
5. complete Replay reconstruction through the payload boundary;
6. truthful stop at the next downstream blocker.

Do not repair Provider availability, force execution authorization, manually
invoke a Worker, mutate the fixture, or bridge the next blocker. Remove the
disposable repository and temporary evidence after recording hashes and
observations.

## Validation

Run and report exact pass, skip, and failure counts for:

- focused G31-05 tests;
- G31-04 regressions;
- native development context and PPP task-package tests;
- Worker payload and dispatch-boundary tests;
- Human Interface and AiCLI tests;
- clarification, approval, and authorization tests;
- G28 and G29 regressions;
- all Generation 30 tests;
- G31-02 Product 1 onboarding tests;
- Replay reconstruction;
- Governance;
- `py_compile`;
- `git diff --check`;
- full repository suite.

## Documentation

Add:

docs/governance/G31_05_APPROVED_DURABLE_GOVERNED_WORK_TO_GOAL_FAITHFUL_WORKER_IMPLEMENTATION_PAYLOAD_BINDING.md

Document exact reuse, the minimal binding, payload projection, repository
grounding, approval identity continuity, Replay and tamper evidence, authority
boundaries, real PTY observations, validation results, and the next first
blocker if one remains.

## Non-goals

Do not:

- redesign Platform Core or any certified generation;
- create a planner, router, classifier, clarification, approval, conversation,
  presentation, Provider, Worker, task-package, or Replay subsystem;
- repair Provider availability;
- authorize execution merely because a human approved the proposal;
- implement repository mutation, validation, or certification unless the
  unchanged existing lifecycle already reaches them after the bounded binding;
- invent repository scope or implementation details;
- add a product, domain, UI, dashboard, deployment, or release pipeline;
- repair unrelated governance hook drift;
- bundle later downstream blockers;
- claim complete no-copy-paste readiness.

## Required final report

Provide:

1. implementation verdict;
2. implementation summary;
3. changed files;
4. exact reused capabilities;
5. approved identity to task-package transition;
6. Worker payload and goal-faithfulness evidence;
7. repository-grounding behavior;
8. real PTY observations;
9. Replay and tamper evidence;
10. authority-boundary confirmation;
11. exact validation and governance results;
12. remaining bounded limitations;
13. exactly one next first blocker or deterministic readiness verdict;
14. evidence-scoped no-copy-paste progress estimate;
15. exact git status;
16. recommended commit commands;
17. the complete bounded G31-06 prompt.

Architectural minimalism is mandatory.
The restored no-copy-paste development priority remains binding.
```

## Conclusion

G31-04 closes the first post-G31-03 blocker. An ordinary sufficiently clear
implementation request now produces the existing canonical plan and Durable
Governed Work proposal before approval, exposes exact immutable identities,
and makes approval consumable only for those identities. The Human Interface
remains a thin renderer and transport.

The milestone does not claim complete no-copy-paste development readiness.
The next bounded work is the single approved-identity-to-goal-faithful-Worker-
payload binding identified above.
