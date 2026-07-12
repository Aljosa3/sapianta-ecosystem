# G21-04 — Governed Development Plan to Durable Work Artifact Audit

Status: `AUDIT_ONLY`

Date: 2026-07-12

## Executive Summary

Platform Core contains the substantive capabilities required for the lifecycle after a Development Composition Plan: durable replay storage, proposal contracts, approval requests and decisions, governed implementation requests, implementation manifests, execution preparation, authorization, Worker invocation, result validation, replay reconstruction, and certification. A new proposal, approval, authorization, Worker, replay, or certification subsystem is not justified.

The lifecycle is nevertheless incomplete at one precise transition. `PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_RUNTIME` returns a validated, hashed, read-only advisory plan. The Unified Platform Query Router and Canonical Platform Presentation Layer expose it, and Unified Human Interface project services persist the containing project-context/workspace evidence. No existing transition converts that plan into a standalone, typed, durable governed work artifact accepted by the proposal and approval lifecycle.

Consequently, the plan has replay durability as nested evidence but no **lifecycle durability**: it has no governed work identity, review state, approval-request identity, supersession state, or downstream contract binding. The reference `./aicli` therefore closes the read-only turn. Its `/approve` command applies only to a pending governed implementation summary, not to a read-only Development Composition Plan result.

The exact missing capability is:

`CANONICAL_DEVELOPMENT_COMPOSITION_PLAN_TO_DURABLE_GOVERNED_WORK_ARTIFACT_BINDING`

This should be implemented, in a future authorized generation, as one bounded Platform Core composition and lifecycle transition. It should reuse the existing plan validator, proposal/work contracts, approval lifecycle, authorization chain, replay, and certification. Human Interface changes would only render and submit Platform Core state; Human Interface binding alone cannot create the missing authoritative artifact.

## Current End-to-End Lifecycle

The currently connected G21 path is:

1. Human request enters the thin `aicli` adapter.
2. Platform Core restores project workspace state.
3. Project Objective Inference produces canonical objective evidence.
4. Development Intent Resolution preserves `AUDIT_ONLY` and non-mutation.
5. Unified Platform Query Router selects `PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_RUNTIME`.
6. Capability Composition Coverage identifies reusable capabilities and residual gaps.
7. Development Composition Plan produces ordered work, dependencies, validation requirements, and the minimal implementation boundary.
8. Canonical Platform Presentation Layer returns `PRESENTATION_READY`.
9. Governed read-only binding returns `GOVERNED_READ_ONLY_WORK_BOUND` with Provider, Worker, and repository mutation all false.
10. Unified Human Interface project services persist the containing project context and workspace state.
11. The user-visible session has no pending approval object and no next governed work state.

The broader repository contains a separate downstream lifecycle:

1. durable proposal or improvement-intent candidate;
2. approval request and explicit human decision;
3. governed implementation request or execution-ready packet;
4. execution authorization;
5. Worker request, dispatch, invocation candidate, and execution candidate;
6. governed Worker execution;
7. result validation;
8. replay reconstruction and certification.

The two lifecycles do not share a canonical handoff from the Development Composition Plan artifact.

## Lifecycle Trace

| Lifecycle stage | Existing authority and artifact | Current connection from Development Composition Plan |
|---|---|---|
| Objective inference | `PLATFORM_CORE_PROJECT_OBJECTIVE_INFERENCE_ARTIFACT_V1` | Connected. |
| Capability coverage | `PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_ARTIFACT_V1` | Connected and hash-bound by the plan. |
| Development planning | `PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_ARTIFACT_V1` | Connected and validated. |
| Read-only presentation | `CANONICAL_PLATFORM_PRESENTATION_ARTIFACT_V1` and `PLATFORM_CORE_GOVERNED_READ_ONLY_WORK_RESULT_V1` | Connected. |
| Durable workspace evidence | Immutable Unified Human Interface project-context and workspace-state records | Connected as nested replay evidence. |
| Durable governed work identity | Existing proposal, PPP candidate, implementation-request, task-package, and manifest contracts | **Not connected.** None accepts the plan artifact as a canonical source. |
| Human review request | Approval Request and proposal-approval artifacts | **Not connected.** No approval request is generated for the plan. |
| Human approval | Proposal approval, conversational approval decision, and execution-summary confirmation artifacts | Available downstream, but no plan-derived subject exists to approve. |
| Runtime preparation | Context assembly, proposal validation, implementation request, dry run, execution packet, and execution-ready artifacts | Available downstream, but requires typed upstream artifacts and lineage absent from the plan result. |
| Execution authorization | `EXECUTION_AUTHORIZATION_*` artifacts | Available and correctly non-executing; requires execution-ready replay. |
| Worker execution | Worker request/assignment/dispatch/invocation/execution candidates and governed Worker execution | Available and correctly gated; cannot consume a presentation or advisory plan directly. |
| Replay and certification | Append-only replay wrappers, replay certification, implementation certification, generation certification, and finalize manifests | Available once a canonical chain exists; no plan-to-work chain currently begins. |

## Existing Reusable Artifacts

### Audit reports

The repository contains several forms of durable audit evidence:

- governance audit reports under `docs/governance/`;
- Product 1 audit packet artifacts;
- runtime diagnostic and replay reports;
- governance evidence, review, certification, and finalize artifacts under `.github/governance/`.

These prove that durable audit reporting is an established pattern. They do not provide a generic transition that materializes any Development Composition Plan into a governance report. The G20-05 plan remains a JSON runtime artifact rather than a generated repository audit document.

### Implementation specifications and work artifacts

Existing contracts include:

- Development Proposal artifacts and contract validation;
- conversational development proposal artifacts;
- Improvement Intent and PPP Candidate artifacts;
- `IMPLEMENTATION_REQUEST_ARTIFACT_V1`;
- governed task-package previews;
- execution plans, dry-run packets, and execution-ready artifacts;
- `IMPLEMENTATION_MANIFEST_ARTIFACT_V1`.

These artifacts are reusable, but they have strict input contracts. For example, the governed implementation request requires a certified PPP candidate and a matching human approval artifact. The implementation manifest requires candidate, handoff, provider-generation authorization, and provider-response lineage. A Development Composition Plan is not an accepted source artifact for either contract.

### Approval requests and decisions

The Approval Runtime and ACLI proposal/approval bridge already support:

- approval-request identities;
- risk classifications;
- proposal hashes and versions;
- explicit approve, reject, and clarification decisions;
- replay-visible human authority;
- separation of approval from authorization.

No new approval engine is needed. The missing prerequisite is a durable plan-derived review subject.

### Authorized execution

Execution Authorization already creates replay-visible request, decision, authorization, and result artifacts from validated execution-ready evidence and human confirmation. It explicitly does not invoke a Worker. This is the correct boundary and should remain unchanged.

### Replay

Replay capability is pervasive. The Development Composition Plan has an artifact hash, and the containing Unified Human Interface context is written immutably. Downstream proposal, approval, request, authorization, Worker, result-validation, and certification runtimes also persist ordered replay wrappers.

The missing property is not storage. It is canonical lineage between two otherwise replay-capable artifact families.

### Certification

Existing certification includes capability certification, Generation Certification composition, replay certification, implementation certification, Worker and provider certifications, and finalize manifests. These can certify a completed governed chain. They cannot infer a missing plan-to-work lineage after the fact.

## Durable Work Artifact Analysis

The Development Composition Plan already carries most semantic inputs needed to create a durable work artifact:

- source request and hash;
- capability-coverage type and hash;
- reusable certified capabilities and compositions;
- residual capability gaps;
- minimal required Platform extension;
- ordered implementation sequence;
- dependency graph;
- governance, certification, and replay dependencies;
- validation requirements;
- implementation boundary;
- whether implementation is required;
- requirement for future human approval and separate execution authorization;
- constitutional non-authority flags.

It deliberately lacks fields that only a durable lifecycle transition should assign:

- governed work artifact identifier and version;
- work-artifact status;
- source project-objective reference and hash through the complete lineage;
- review scope and approval subject hash;
- acceptance criteria normalized for the downstream proposal/work contract;
- allowed and forbidden operations for the proposed next phase;
- supersession and cancellation metadata;
- downstream contract selection;
- approval-request readiness status;
- separate execution-authorization readiness status.

The plan must not itself be reinterpreted as authorization. A new artifact must preserve it unchanged as source evidence and project only the fields required by existing downstream contracts.

## Approval and Authorization Analysis

The current reference `aicli` has two distinct outcomes:

- implementation work may produce `pending_summary`, after which `/approve` delegates to the certified runtime;
- read-only work produces `READ_ONLY_RESULT`, clears the turn without `pending_summary`, and closes or continues the session.

The Development Composition Plan follows the second branch. Although the plan may state `requires_future_human_approval: true`, this is descriptive metadata. It is not an Approval Request artifact, is not registered as pending approval, and is not a valid subject for `/approve`.

Approval and authorization must remain separate:

1. human review approves or rejects the durable governed work proposal;
2. Platform Core prepares and validates the implementation/execution package;
3. a later explicit human confirmation authorizes one bounded execution-ready packet;
4. only then may Worker dispatch and execution proceed.

The missing transition belongs before step 1. It must not collapse approval into authorization or permit the original `AUDIT_ONLY` request to mutate state.

## Worker Execution Analysis

Worker-stage execution is already governed by typed prerequisites. Governed Worker execution validates a certified Worker execution candidate, matching scoped human approval, replay lineage, execution constraints, and separate governance. Other runtimes provide Worker selection, request creation, assignment, dispatch, invocation candidates, and result validation.

These components should not consume the raw human request, canonical presentation, or Development Composition Plan directly. Doing so would bypass proposal review and authorization lineage.

The correct role separation is:

- **Early Platform Core-governed cognition:** an LLM may propose content, affected files, tests, assumptions, or refinements inside a proposal-only contract. It has no approval, authorization, dispatch, or mutation authority.
- **Platform Core governance:** validates the plan-derived work artifact, controls review state, records human approval, prepares execution, authorizes a bounded packet, selects the certified role path, and records replay.
- **Later Worker-stage execution:** Codex or another coding model may execute only the authorized Worker package and only within its declared constraints.

The same model implementation may be configured for different roles, but the artifacts, credentials, authorities, and lifecycle stages must remain distinct. A cognition response cannot be treated as Worker authorization.

## Manual Copy/Paste Root Cause

Manual copy/paste remains necessary because the read-only result is a terminal presentation branch rather than a resumable governed-work branch.

The exact discontinuity is:

1. `compose_platform_development_plan(...)` produces an advisory plan with `approval_created: false`, `execution_authorized: false`, `worker_invoked: false`, and `repository_mutated: false`.
2. Platform Presentation normalizes the plan for human consumption but does not invent semantic content or lifecycle authority.
3. Governed read-only binding returns the presentation and records it in project context.
4. No service creates a standalone work artifact from the validated plan.
5. No approval request is associated with the plan hash.
6. `aicli` has no pending plan-review state; `/approve` therefore cannot advance it.
7. The user must restate or paste the plan as a new implementation request, causing a new intent lineage instead of continuing the existing one.

This is not primarily a rendering defect. Adding another `aicli` command without the missing Platform Core artifact would move orchestration authority into the Human Interface and would not solve lineage.

## Exact Missing Capability

The first missing deterministic transition is:

`CANONICAL_DEVELOPMENT_COMPOSITION_PLAN_TO_DURABLE_GOVERNED_WORK_ARTIFACT_BINDING`

Its responsibility is narrowly defined:

> Validate a canonical Development Composition Plan and compose it, without approval or execution, into one immutable, reviewable, resumable governed work artifact whose hash and lineage are accepted by the existing proposal and approval lifecycle.

The missing capability is simultaneously:

- a **bounded Platform Core composition**, because it maps existing canonical evidence into existing downstream contract concepts;
- a **lifecycle transition**, because it changes the state from advisory plan ready to governed work ready for human review;
- followed by a **thin Human Interface binding**, because `aicli` must render, approve, reject, clarify, cancel, and resume Platform Core state.

It is not a new subsystem. Human Interface binding alone is insufficient.

## Minimal Canonical Binding Recommendation

In a future authorized implementation generation, introduce one minimal read-only transition that:

1. accepts only a validated `PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_ARTIFACT_V1` plus its project-objective and coverage lineage;
2. fails closed for a failed plan, invalid hashes, missing lineage, or contradictory work boundaries;
3. distinguishes:
   - no implementation required;
   - audit/report materialization only;
   - implementation proposal required;
4. emits one canonical durable work artifact, for example `PLATFORM_GOVERNED_WORK_ARTIFACT_V1`;
5. preserves the original work type and records the proposed next-phase work type separately—an `AUDIT_ONLY` plan must never silently become authorized implementation;
6. maps plan work items, dependency graph, validation requirements, residual gaps, and minimal extension into proposal/work acceptance criteria;
7. records review status, version, supersession, cancellation, approval readiness, and exact downstream contract target;
8. persists the artifact through existing immutable replay services;
9. generates or feeds an existing Approval Request without granting approval;
10. after explicit approval, delegates to existing proposal, implementation-request, preparation, authorization, Worker, replay, and certification services.

The transition should reuse existing proposal and approval contracts rather than create parallel “plan approval” semantics. If those contracts cannot accept the new source type directly, a small adapter should produce their existing canonical input while preserving the durable work artifact as the lineage root.

## `aicli` as Sole User-Facing Entry Point

`./aicli` can become the sole user-facing entry point without becoming the orchestrator. The repository already demonstrates that Platform Core can restore state, present summaries, accept decisions, delegate runtime work, and project replay status through Human Interfaces.

The required interface behavior is thin:

- display the Platform Core durable work artifact and current review state;
- submit human approve, reject, clarification, cancel, or resume actions;
- render authorization summaries before later execution authorization;
- render Worker/replay/certification progress returned by Platform Core.

`aicli` must not:

- translate the plan into a task itself;
- choose a cognition provider or Worker;
- create approval or authorization semantics;
- copy plan fields into Worker instructions;
- invoke a Worker before Platform Core records required approval and authorization.

Codex or another coding model can remain behind Platform Core as either a governed cognition provider during proposal refinement or a Worker during authorized implementation. Role selection and authority remain Platform Core decisions.

## Architectural Boundaries

The recommended binding must preserve:

- Platform Core ownership of orchestration, semantic transitions, approval state, authorization, and replay lineage;
- Human Interfaces as thin adapters;
- proposal-only cognition before approval;
- explicit human review before implementation preparation advances;
- separate human confirmation and execution authorization before Worker execution;
- fail-closed validation of every source hash and state transition;
- immutable, reconstructable replay and supersession evidence;
- certification only over actual completed evidence;
- no automatic conversion of `AUDIT_ONLY` into implementation authority;
- no Worker self-authorization, provider self-approval, or hidden repository mutation;
- visibility of known conformance limitations and existing hook drift.

## Audit Conclusion

Platform Core already has the downstream machinery needed for a no-copy/paste governed development lifecycle. The Development Composition Plan also already contains sufficient deterministic planning content. The lifecycle stops because there is no canonical artifact transition that gives the validated plan a durable governed work identity and binds it to the existing review/approval contracts.

The smallest correct remedy is one bounded composition plus lifecycle transition, followed by thin `aicli` presentation and decision binding. No new execution, approval, Worker, replay, certification, or Human Interface subsystem is required.

## Final Verdict

`GOVERNED_DEVELOPMENT_PLAN_TO_DURABLE_WORK_ARTIFACT_REUSE_WITH_MINIMAL_CANONICAL_LIFECYCLE_BINDING`

