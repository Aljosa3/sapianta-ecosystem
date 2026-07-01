# G8-02 ACLI Next MVP Specification V1

Status: ACLI Next MVP ready for implementation.

Final verdict: ACLI_NEXT_MVP_READY_FOR_IMPLEMENTATION

## 1. MVP Goals

The ACLI Next MVP defines the smallest operational runtime capable of replacing the first part of the current manual ChatGPT -> Codex -> Terminal -> Git workflow.

The MVP must replace:

- external prompt copying for session bootstrap;
- manual replay root selection;
- manual advisory session setup;
- manual human confirmation recording;
- manual completion summary composition.

The MVP must not attempt to replace the full workflow at once.

The MVP remains:

- governed;
- replay-visible;
- non-mutating by default;
- thin over certified Platform Core;
- fail-closed on missing evidence;
- compatible with legacy ACLI during transition.

## 2. MVP Scope

Mandatory MVP capabilities:

| Capability | MVP Status | Notes |
| --- | --- | --- |
| Human prompt entry | Mandatory | ACLI Next captures raw human request. |
| PGSP session lifecycle | Mandatory | ACLI Next starts a PGSP-governed session. |
| UBTR invocation | Mandatory through PGSP | ACLI Next does not translate. |
| CSA creation | Mandatory through Platform Core | ACLI Next does not create CSA directly. |
| OCS orchestration | Mandatory through Platform Core | OCS owns proposal and orchestration. |
| Governance confirmation | Mandatory | Governance checkpoint and human confirmation evidence must be visible. |
| Replay recording | Mandatory | Session, turn, request, response, confirmation, and summary must be replay-visible. |
| Execution summary | Mandatory | Rendered through UHCL-compatible output. |
| Error handling | Mandatory | Errors must produce fail-closed evidence. |
| Fail-closed behavior | Mandatory | Missing replay, governance, or PGSP evidence blocks completion claims. |
| Provider invocation | Optional/deferred | Only bounded read-only provider cognition through certified EPP/PGSP path. |
| Worker execution | Optional/deferred for MVP core | Only read-only Worker action may be allowed after explicit confirmation and certified authorization path. |

The MVP's default execution state is advisory and non-mutating.

## 3. End-To-End Workflow

First complete MVP scenario:

```text
Human
-> ACLI Next
-> PGSP session
-> UBTR translation
-> CSA intent artifact
-> OCS advisory proposal
-> Governance checkpoint
-> UHCL proposal summary
-> Human confirmation
-> Optional read-only Worker inspection or validation-summary action
-> Replay
-> Completion summary
```

The optional Worker step is allowed only when:

- the Worker action is read-only;
- no repository mutation occurs;
- no Git command is executed;
- authorization prerequisites are satisfied;
- replay evidence is produced;
- post-action summary remains human-reviewable.

If those conditions are not met, ACLI Next must stop at confirmed advisory output.

## 4. Interaction Sequence

MVP turn sequence:

1. Human starts `aigol next session`.
2. ACLI Next captures `operator_request`.
3. ACLI Next creates `session_id` and `turn_id`.
4. ACLI Next records input capture evidence.
5. ACLI Next invokes PGSP with the captured request.
6. PGSP routes through UBTR, CSA, OCS, Governance, UHCL, and Replay.
7. ACLI Next receives a structured session result.
8. ACLI Next renders UHCL-compatible summary.
9. Human chooses:
   - confirm advisory plan;
   - request modification;
   - reject;
   - answer clarification;
   - request read-only inspection if available.
10. ACLI Next records human response.
11. If read-only Worker action is requested and certified path exists, ACLI Next routes through PGSP/Governance/Worker handoff.
12. ACLI Next records final replay-visible completion summary.

ACLI Next must never bypass PGSP for semantic, orchestration, governance, replay, provider, or Worker behavior.

## 5. Confirmation Flow

Confirmation states:

| State | Meaning | MVP Behavior |
| --- | --- | --- |
| `proposal_presented` | UHCL-compatible proposal has been rendered. | Await human response. |
| `confirmed_advisory` | Human confirms advisory result. | Record confirmation; no execution authorization created. |
| `modification_requested` | Human asks for changes. | Continue PGSP session. |
| `clarification_required` | Platform Core requests clarification. | Capture human response and continue. |
| `rejected` | Human rejects proposal. | Record rejection and close turn. |
| `readonly_worker_requested` | Human asks for a read-only Worker step. | Validate certified path; fail closed if absent. |
| `readonly_worker_completed` | Read-only Worker step completed. | Render summary and replay reference. |
| `blocked` | Required evidence or authority is missing. | Emit fail-closed summary. |

MVP confirmation must not imply:

- approval for mutation;
- authorization for execution;
- Worker dispatch;
- provider invocation;
- Git operation.

## 6. Replay Expectations

ACLI Next MVP must record or reference replay evidence for:

- session creation;
- turn creation;
- human request capture;
- PGSP invocation;
- UBTR/CSA/OCS/Governance/UHCL session evidence returned by Platform Core;
- human confirmation or rejection;
- optional read-only Worker request and result;
- fail-closed state;
- completion summary.

Replay requirements:

- replay root is created or accepted deterministically;
- every turn has a replay reference;
- missing replay blocks `completed` status;
- replay evidence remains append-only;
- ACLI Next does not reconstruct replay independently;
- Replay remains reconstruction authority.

## 7. Governance Checkpoints

Required MVP governance checkpoints:

| Checkpoint | Requirement |
| --- | --- |
| Adapter boundary | ACLI Next captures and renders only. |
| Translation boundary | UBTR handles semantic translation. |
| Orchestration boundary | OCS owns proposal formation. |
| Human communication boundary | UHCL owns reusable communication. |
| Replay boundary | Replay owns evidence reconstruction. |
| Advisory non-mutation | MVP must not mutate repository by default. |
| Human confirmation | Human response must be replay-visible. |
| Provider boundary | Provider invocation is absent unless certified read-only path is explicitly used. |
| Worker boundary | Worker action is absent unless read-only, authorized, and replay-visible. |
| Conflict/fallback | G7-04 policy applies to missing, stale, partial, or conflicting evidence. |

## 8. Error Handling And Fail-Closed Behavior

Fail-closed triggers:

- PGSP invocation fails;
- UBTR/CSA/OCS evidence is missing from PGSP result;
- Governance checkpoint evidence is missing;
- UHCL-renderable output is missing;
- replay reference is missing;
- human confirmation is ambiguous;
- provider path is requested but not certified;
- Worker path is requested but not read-only or not authorized;
- any source or mapping evidence is stale, missing, partial, or conflicting.

Fail-closed output must include:

- error class;
- failed checkpoint;
- replay reference if available;
- governance route if review is required;
- recommended next safe action;
- explicit statement that no mutation occurred.

## 9. Provider Invocation

Provider invocation is not mandatory for MVP.

Allowed MVP provider mode:

- none by default;
- optional bounded read-only cognition only if certified PGSP/EPP path is available.

Provider invocation must remain:

- non-authoritative;
- replay-visible;
- credential-safe;
- governed by EPP and provider identity boundaries;
- summarized through UHCL.

ACLI Next must not directly call provider APIs.

## 10. Worker Execution

Worker execution is not mandatory for the MVP core.

Allowed MVP Worker mode:

- optional read-only inspection or validation-summary Worker after explicit human request and certified authorization path.

Examples of acceptable read-only Worker outputs:

- repository status summary;
- targeted validation recommendation;
- replay evidence inspection summary;
- canonical mapping lookup summary.

Deferred Worker actions:

- file edits;
- repository mutation;
- Git commit creation;
- deployment;
- shell command execution with side effects;
- autonomous retry or fallback.

## 11. Deferred Functionality

Deferred beyond MVP:

- repository mutation;
- patch application;
- commit creation;
- branch management;
- deployment;
- autonomous provider selection;
- autonomous Worker selection;
- mutating Worker execution;
- long-running multi-session execution authorization reuse;
- production rollback;
- full replacement of Terminal and Git.

These are future phases and require separate certification.

## 12. Manual Workflow Steps Eliminated

MVP eliminates:

| Manual Step | Replacement |
| --- | --- |
| Copying a development prompt into external chat | Human enters request directly into ACLI Next. |
| Manually starting an advisory governed session | ACLI Next starts PGSP session. |
| Manually choosing replay location | ACLI Next creates deterministic replay root or records caller-provided root. |
| Manually capturing human confirmation in chat prose | ACLI Next records structured confirmation. |
| Manually composing completion summary | ACLI Next renders replay-visible completion summary. |

## 13. Manual Workflow Steps Retained

MVP intentionally retains:

| Manual Step | Reason |
| --- | --- |
| Reviewing proposed changes | Human authority remains required. |
| Applying repository mutations | Mutation Worker certification is deferred. |
| Running arbitrary terminal commands | Side-effecting commands are out of MVP scope. |
| Creating commits | Commit Worker certification is deferred. |
| Selecting complex validation suites | Validation recommendation may exist, but execution is deferred unless read-only certified path exists. |
| Resolving missing canonical evidence | G7-04 fallback remains active. |

## 14. Acceptance Criteria

ACLI Next MVP is acceptable when:

1. `aigol next session` or equivalent entrypoint exists.
2. Human request is captured without external copy/paste.
3. PGSP session is invoked.
4. UBTR, CSA, OCS, Governance, UHCL, and Replay evidence are returned or referenced through PGSP.
5. Human confirmation is captured in structured form.
6. Replay evidence reconstructs the MVP turn.
7. Completion summary reports advisory/non-mutating state.
8. Fail-closed behavior occurs on missing replay or governance evidence.
9. Provider invocation is absent or certified read-only.
10. Worker execution is absent or certified read-only and authorized.
11. No repository mutation occurs.
12. Legacy ACLI remains compatible.

## 15. Implementation Readiness Assessment

| Area | Readiness | Notes |
| --- | --- | --- |
| ACLI Next program | Ready | G8-01 approved implementation program. |
| PGSP session contract | Ready enough for MVP | Existing G4 public API and G8 program define route. |
| Replay expectations | Ready | G7 and G8 define evidence boundaries. |
| Governance checkpoints | Ready | Existing Governance remains authority. |
| UHCL rendering | Mostly ready | ACLI Next rendering adapter must reuse existing communication output. |
| Provider invocation | Deferred optional | Read-only only after certified path is bound. |
| Worker execution | Deferred optional | Read-only only after authorization/replay path is bound. |
| Mutation and Git | Not ready for MVP | Requires later Worker certification. |

Implementation readiness: ready.

## 16. Validation Strategy

Documentation-only MVP specification validation:

```text
git diff --check
```

Future implementation validation:

- `git diff --check`;
- `python -m py_compile` for changed Python modules;
- targeted ACLI Next MVP tests;
- replay reconstruction test;
- fail-closed missing replay test;
- no-mutation assertion test;
- full pytest only if shared runtime behavior changes.

## 17. Final Determination

The ACLI Next MVP is ready for implementation.

The MVP should begin with non-mutating, replay-visible PGSP sessions and may include only bounded read-only Worker behavior when the certified authorization and replay path is available.

## 18. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: ACLI_NEXT_MVP_READY_FOR_IMPLEMENTATION
