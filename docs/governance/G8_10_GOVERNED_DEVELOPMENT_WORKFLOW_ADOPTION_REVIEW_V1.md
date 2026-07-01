# G8-10 Governed Development Workflow Adoption Review V1

Status: targeted runtime capabilities remain.

Final verdict: TARGETED_RUNTIME_CAPABILITIES_REMAIN

## 1. Executive Summary

Generation 8 has moved AiGOL from architecture and advisory operation into certified bounded mutation.

Certified capabilities now include:

- ACLI Next as a thin human entrypoint;
- PGSP-governed advisory sessions;
- interactive multi-turn clarification;
- replay-visible human confirmation;
- read-only Worker handoff;
- Platform Core execution planning;
- Platform Core mutation runtime responsibility realignment;
- first governed mutating Worker;
- certification of the first mutation boundary.

The current platform can replace meaningful parts of the historical workflow:

```text
Human
-> ChatGPT
-> Copy / Paste
-> Codex
```

with:

```text
Human
-> ACLI Next
-> PGSP
-> Platform Core
-> Replay
-> Human
```

It can also perform one certified repository mutation:

```text
create exactly one new plaintext file
inside the allowlisted non-authority workspace
after explicit approval and Governance authorization
through the Worker Platform
with hash-bound Replay and rollback metadata
```

However, AiGOL is not yet ready to become the primary day-to-day development workflow for ordinary repository work. Existing-file edits, multi-file changes, patch application, validation command execution, Git staging, commit creation, and release operations still require manual terminal usage.

Recommended adoption posture: begin limited governed-development pilot usage, while prioritizing targeted runtime capabilities before declaring primary workflow adoption.

## 2. Complete Workflow Readiness Matrix

| Stage | Current status | Evidence | Adoption readiness |
| --- | --- | --- | --- |
| Human | Ready | Human request and explicit confirmation are captured through ACLI Next and governed artifacts. | Ready. |
| ACLI Next | Ready as thin entrypoint | Bootstrap, interactive session, read-only Worker handoff, and execution plan paths exist. | Ready for pilot use; not an authority layer. |
| PGSP | Mostly ready | ACLI Next routes through governed session lineage. | Ready for current advisory and bounded mutation paths. |
| UBTR | Architecture complete / implementation exposed through PGSP lineage | ACLI Next does not translate. | Ready as boundary; richer runtime evidence still useful. |
| CSA | Architecture complete / partially exposed | CSA remains Platform Core responsibility. | Ready as authority; explicit artifact exposure should improve. |
| OCS | Partially ready | Candidate ownership and execution planning are delegated outside ACLI Next and runtime coordinator. | Ready for first mutation; broader edit planning pending. |
| Governance | Partially ready | Approval and authorization ownership is certified for first mutation. | Ready for first mutation; broader authorization classes pending. |
| Worker Platform | Partially ready | Read-only Workers and first create-only mutating Worker are certified. | Ready for constrained mutation; not ready for general repository work. |
| Replay | Mostly ready | Session, Worker, mutation, validation, rollback, and completion evidence are hash-bound. | Ready for current surfaces; broader command and Git replay pending. |
| Completion | Ready for current surfaces | Advisory and first mutation completion summaries exist. | Ready for pilot use. |

## 3. Activities Fully Performable Through AiGOL Today

The following development activities can be performed entirely through the current AiGOL path:

| Activity | Current support | Boundary |
| --- | --- | --- |
| Start governed development session | Supported | ACLI Next over PGSP. |
| Capture human request without copy/paste | Supported | ACLI Next capture. |
| Multi-turn clarification and refinement | Supported | ACLI Next interactive session. |
| Record structured human confirmation | Supported | ACLI Next and Governance artifacts. |
| Produce advisory execution plan | Supported | Platform Core execution planning service. |
| Produce descriptive mutation preview | Supported | Advisory only. |
| Perform read-only Worker inspection | Supported where certified | Worker Platform, read-only only. |
| Create one new plaintext file | Supported with constraints | First mutating Worker, allowlisted workspace only. |
| Record replay-visible mutation evidence | Supported for first mutation | Replay mutation evidence helper. |
| Produce rollback metadata | Supported for first mutation | Metadata only; no rollback execution. |
| Render completion summary | Supported | ACLI Next/Platform Core result rendering. |

This is enough for governed pilot activities such as creating a small non-authority note, scratch artifact, or narrowly scoped generated plaintext evidence file in the governed mutation workspace.

## 4. Activities Still Requiring Manual Terminal Usage

| Activity | Why manual use remains | Canonical owner | Priority |
| --- | --- | --- | --- |
| Editing existing files | First mutation only permits creating one new plaintext file. | Worker Platform / Governance / Replay | P0 |
| Multi-file changes | Multi-file mutation remains prohibited. | OCS / Worker Platform / Governance | P0 |
| Patch application | No certified patch Worker exists. | Worker Platform | P0 |
| Running tests or validation commands | Governed command execution Worker is not certified. | Worker Platform / Replay / validation capability | P0 |
| Inspecting arbitrary command output | Read-only summaries exist, but arbitrary shell execution is not certified. | Worker Platform / Replay | P1 |
| Git status/staging | Git operations remain prohibited in the mutating Worker. | Worker Platform / Governance | P1 |
| Commit creation | Commit Worker and release discipline path are not certified. | Governance / Worker Platform / release discipline | P1 |
| Branch management | Not implemented and not certified. | Governance / Worker Platform | P2 |
| Deployment | Explicitly out of scope. | Governance / release discipline / Worker Platform | Deferred |
| Rollback execution | Rollback metadata exists, but automatic rollback is prohibited. | Governance / Worker Platform / Replay | P1 |
| Provider-assisted implementation planning | Provider invocation remains optional/deferred and must remain EPP/PGSP-governed. | EPP / PGSP / Governance | P2 |

## 5. Remaining Manual Dependency Inventory

| Manual dependency | Reason it remains | Interface or Platform Core? | Recommended next action |
| --- | --- | --- | --- |
| Manual code editing | No certified existing-file edit Worker. | Platform Core / Worker Platform | Specify and implement narrow existing-file patch Worker. |
| Manual validation execution | No governed command execution Worker. | Platform Core / Worker Platform / Replay | Implement allowlisted validation command Worker. |
| Manual interpretation of validation output | No certified validation evidence normalizer for command output. | Platform Core validation capability | Add validation artifact model and replay reconstruction. |
| Manual Git operations | Git operations are intentionally prohibited in first mutation scope. | Platform Core / Worker Platform / Governance | Specify Git status/stage/commit phases separately. |
| Manual commit message creation | Commit creation and release discipline are not yet runtime-bound. | Governance / release discipline | Define governed commit preparation model. |
| Manual rollback | Only rollback metadata exists. | Governance / Worker Platform | Specify governed rollback execution as a later phase. |
| Manual selection of broader Worker sequence | OCS only owns current constrained candidate flow. | OCS / Worker Platform | Extend OCS planning to certified edit and validation Workers. |
| Manual terminal fallback for unsupported cases | Current runtime intentionally fails closed outside certified scope. | Human interface fallback | Retain until target capabilities are certified. |

## 6. ACLI Next Adoption Assessment

ACLI Next is ready to become the canonical human interface for governed pilot sessions.

It is not yet ready to become the exclusive day-to-day development interface because ordinary development still needs capabilities outside the certified mutation envelope.

Recommended ACLI Next role now:

- primary entrypoint for advisory sessions;
- primary entrypoint for governed planning;
- primary entrypoint for read-only inspection where certified;
- primary entrypoint for the first constrained create-only mutation;
- not yet the sole interface for code editing, validation, Git, commits, or releases.

ACLI Next should remain thin. New development capability must continue to land in Platform Core and Worker Platform first, then be consumed by ACLI Next.

## 7. Adoption Recommendations

Recommended adoption policy:

| Adoption area | Recommendation |
| --- | --- |
| Advisory planning | Adopt immediately as default for new governed development sessions. |
| Clarification and confirmation | Adopt immediately where ACLI Next is available. |
| Read-only inspection | Adopt for certified read-only Worker cases. |
| First mutation | Adopt only for low-risk non-authority plaintext file creation in allowlisted workspace. |
| Existing-file edits | Do not adopt yet; use manual process until certified. |
| Validation execution | Do not adopt yet; use manual process until certified. |
| Git and commit | Do not adopt yet; use manual process until certified. |
| Deployment | Keep outside Generation 8 adoption. |

The migration should be incremental and evidence-driven, not a sudden replacement of the whole terminal workflow.

## 8. Phased Migration Plan

| Phase | Name | Scope | Adoption outcome |
| --- | --- | --- | --- |
| A0 | Governed Advisory Default | Use ACLI Next for planning, clarification, confirmation, read-only checks, and replay-visible summaries. | Replaces prompt-copy workflow for planning. |
| A1 | Certified Scratch Mutation | Use first mutating Worker for exactly one plaintext file in allowlisted workspace. | Proves governed mutation in low-risk area. |
| A2 | Governed Existing-File Patch | Add certified patch Worker for narrowly scoped existing-file edits. | Begins replacing manual editor/Codex file mutation. |
| A3 | Governed Validation Execution | Add allowlisted validation command Worker with replay-bound output. | Begins replacing manual terminal validation. |
| A4 | Governed Commit Preparation | Add Git status/stage/commit preparation under Governance and release discipline. | Begins replacing manual Git workflow. |
| A5 | Broader Interface Reuse | Demonstrate Web/REST consumption of same Platform Core services. | Confirms ACLI Next is one adapter, not the platform. |

## 9. Implementation Priorities

Priority 0:

- specify and implement a governed existing-file patch Worker;
- specify and implement allowlisted validation command execution;
- bind validation output to Replay reconstruction;
- extend OCS to select certified edit and validation Workers without moving logic into ACLI Next.

Priority 1:

- specify governed rollback execution;
- implement Git status and staging as read-only/controlled phases;
- define commit preparation and commit authorization;
- add end-to-end tests for advisory -> patch -> validation -> replay summary.

Priority 2:

- bind optional provider cognition through EPP/PGSP for complex planning;
- prove Web or REST interface reuse of the same Platform Core services;
- expand canonical capability lookup across Worker availability and governance status.

Deferred:

- deployment;
- production rollback;
- autonomous broad Worker selection;
- unrestricted shell command execution.

## 10. Strategic Determination

AiGOL is ready for governed development adoption in a limited pilot mode.

AiGOL is not yet ready to become the primary day-to-day replacement for the historical ChatGPT -> Codex -> Terminal process because most practical code changes require existing-file mutation, validation commands, Git operations, and commits.

The remaining gaps are targeted runtime capabilities, not architectural redesign gaps. Platform Core ownership is aligned, ACLI Next remains thin, and the first mutating Worker proves the governed execution path.

## 11. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: TARGETED_RUNTIME_CAPABILITIES_REMAIN
