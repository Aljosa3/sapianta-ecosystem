# G9-01 ACLI Next Primary Development Readiness Review V1

Status: hybrid governed development recommended.

Final verdict: HYBRID_DEVELOPMENT_RECOMMENDED

## 1. Executive Summary

AiGOL Next is ready to become the canonical governed entrypoint for AiGOL development sessions, but it is not yet ready to become the exclusive primary day-to-day development interface.

Generation 8 and G9-00 certified the architecture needed for governed development:

- ACLI Next remains a thin human interface;
- Platform Core coordinates;
- PGSP governs session flow;
- UBTR, CSA, OCS, Governance, Replay, UHCL, and Worker Platform retain certified ownership;
- bounded new-file mutation is certified;
- bounded existing-file replacement is certified;
- governed validation execution is certified;
- governed local Git commit is certified;
- Architectural Health and platform evolution methodology are certified as projection-driven disciplines.

This means AiGOL Next can now replace significant parts of the historical workflow:

```text
ChatGPT
-> Codex
-> Terminal
```

with:

```text
Human
-> ACLI Next
-> PGSP
-> Platform Core
-> Governance
-> Worker Platform
-> Replay
-> Completion
```

However, ordinary day-to-day repository development still requires manual or external support for multi-file edits, patch-level edits, broader validation suites, rollback execution, Git push, branch management, remote repository interaction, deployment, package installation, and some complex implementation work currently performed through Codex or terminal tools.

Recommended posture:

```text
Use ACLI Next as the canonical governed development entrypoint.
Retain a hybrid workflow for unsupported implementation, terminal, Git remote, and deployment tasks.
Prioritize targeted runtime expansion before exclusive primary adoption.
```

## 2. Current Workflow Coverage

| Workflow Stage | Current Coverage | Readiness |
| --- | --- | --- |
| Human request capture | Supported by ACLI Next. | Ready. |
| Session governance | Supported through PGSP. | Ready. |
| Semantic translation | Owned by UBTR through Platform Core path. | Ready as boundary. |
| Intent representation | Owned by CSA. | Ready as boundary. |
| Proposal and candidate handling | Owned by OCS. | Ready for certified capability classes. |
| Approval and authorization | Owned by Governance. | Ready for certified capability classes. |
| New-file mutation | Certified for exactly one new plaintext file in allowlisted non-authority workspace. | Ready within scope. |
| Existing-file mutation | Certified for complete replacement of exactly one existing plaintext file in allowlisted non-authority workspace. | Ready within scope. |
| Validation execution | Certified for exactly one allowlisted non-shell validation command with bounded output and timeout. | Ready within scope. |
| Local Git commit | Certified for one governed local commit over the authorized file set after validation and approval. | Ready within scope. |
| Replay evidence | Required and certified for current governed execution paths. | Ready. |
| Completion summary | Replay-visible completion summaries are supported. | Ready. |
| Git push and remote workflow | Not certified. | Not ready. |
| Deployment | Not certified. | Not ready. |
| Rollback execution | Metadata exists; execution is not certified. | Not ready. |

## 3. Remaining Manual Copy/Paste Steps

| Manual Step | Current Status | Gap Class | Notes |
| --- | --- | --- | --- |
| Copying high-level development intent into external chat | Mostly replaceable | Workflow gap | ACLI Next can capture governed requests, but current operator practice may still begin in Codex until ACLI Next is used as the default session launcher. |
| Copying generated implementation text into files | Partially replaceable | Implementation gap | Existing-file replacement is certified, but multi-file and patch-level edits are not. |
| Copying validation output into summaries | Partially replaceable | Tooling gap | One governed validation command can be captured; broader suites and arbitrary output interpretation remain manual. |
| Copying Git state or commit information into governance artifacts | Partially replaceable | Implementation gap | Local governed commit metadata is certified; branch, push, remote, and release states remain manual. |
| Copying release or deployment evidence | Not replaceable | Implementation gap | Deployment and release automation are outside current certified scope. |

Copy/paste is no longer architecturally necessary for advisory session bootstrap, human confirmation, bounded mutation, bounded validation, or local commit evidence. It remains operationally present wherever certified runtime capability is missing.

## 4. Remaining Terminal Dependencies

| Terminal Dependency | Why It Remains | Gap Class | Priority |
| --- | --- | --- | --- |
| Multi-file editing | Current mutation scope is single-file only. | Implementation gap | P0 |
| Patch or hunk-level editing | Existing-file mutation replaces full file contents only. | Implementation gap | P0 |
| Arbitrary repository inspection | Read-only and validation paths are bounded; arbitrary shell remains prohibited. | Intentional manual step | P1 |
| Broader test suites | Only one allowlisted non-shell validation command is certified. | Implementation gap | P0 |
| Package installation | Explicitly outside governed validation scope. | Intentional manual step | P1 |
| Dependency updates | Usually require package manager execution and multi-file changes. | Implementation gap | P1 |
| Build commands outside allowlist | Not certified. | Tooling gap | P1 |
| Rollback execution | Rollback metadata exists, but execution is not certified. | Implementation gap | P0 |
| Release preparation | Requires branch, remote, registry, and release evidence integration. | Workflow gap | P1 |
| Deployment | Not certified and intentionally outside current runtime adoption. | Intentional manual step | Deferred |

Terminal usage remains necessary for unsupported commands and broad operational work. It should remain explicit and human-controlled until certified Workers exist.

## 5. Remaining Git Dependencies

| Git Task | Current Status | Gap Class | Priority |
| --- | --- | --- | --- |
| Local commit | Certified for one governed local commit. | Covered | Ready within scope. |
| Git status inspection | Partially covered by governed paths where evidence is produced. | Tooling gap | P1 |
| Git add/staging beyond authorized file set | Not certified. | Implementation gap | P0 |
| Branch creation | Not certified. | Implementation gap | P1 |
| Branch switching | Not certified. | Intentional manual step | P1 |
| Merge | Not certified. | Intentional manual step | P2 |
| Rebase | Not certified. | Intentional manual step | P2 |
| Push | Not certified. | Implementation gap | P0 |
| Pull/fetch | Not certified. | Workflow gap | P1 |
| Pull request creation | Not certified. | Workflow gap | P1 |
| Release tag creation | Not certified. | Workflow gap | P2 |

The governed local commit capability is a major milestone, but it is not enough to replace the full Git portion of day-to-day development.

## 6. Remaining Codex Dependencies

| Codex Dependency | Why It Remains | Gap Class | Priority |
| --- | --- | --- | --- |
| Complex code synthesis across multiple files | AiGOL mutation scope is still single-file and bounded. | Implementation gap | P0 |
| Local codebase exploration beyond certified read-only or validation Workers | Arbitrary tool use is not governed through ACLI Next. | Tooling gap | P1 |
| Applying patches incrementally | Patch-level mutation Worker is not certified. | Implementation gap | P0 |
| Running varied validation sequences | Only one allowlisted validation command is certified. | Implementation gap | P0 |
| Repairing test failures iteratively | Requires looped edit-validation cycles beyond current certified scope. | Workflow gap | P1 |
| Producing implementation documentation from broad code inspection | Partially possible through advisory paths; still often requires external analysis. | Tooling gap | P2 |
| Handling dependency installation or environment setup | Package installation is prohibited in current governed validation scope. | Intentional manual step | P1 |

Codex remains useful as a development assistant for tasks outside current AiGOL runtime certification. Its use should be governed by the platform evolution methodology rather than treated as the target long-term interface.

## 7. Platform Core Coverage

| Platform Core Component | Coverage | Readiness |
| --- | --- | --- |
| PGSP | Governs session lifecycle and routes ACLI Next into Platform Core. | Ready. |
| UBTR | Owns semantic translation. | Ready as certified boundary. |
| CSA | Owns canonical semantic intent representation. | Ready as certified boundary. |
| OCS | Owns proposal, candidate, and orchestration planning for certified paths. | Ready within current capability classes. |
| Governance | Owns approval, authorization, certification, and admissibility. | Ready within current capability classes. |
| Replay | Owns evidence persistence and reconstruction. | Ready within current capability classes. |
| UHCL | Owns reusable human communication output. | Ready as communication boundary. |
| Worker Platform | Owns read-only, mutation, validation, and Git execution boundaries where certified. | Ready within current capability classes. |
| Platform Digital Twin | Provides deterministic projection basis. | Ready as projection. |
| Architectural Health | Provides non-authoritative projection of boundary health. | Ready as projection. |

Platform Core coverage is architecturally strong. Remaining gaps are capability coverage gaps, not Platform Core redesign gaps.

## 8. ACLI Next Capability Assessment

ACLI Next is ready for:

- starting governed development sessions;
- capturing human intent;
- continuing clarification loops;
- presenting Platform Core proposals;
- capturing explicit human approval;
- routing certified execution requests through Platform Core;
- rendering replay-visible completion summaries;
- serving as the canonical human entrypoint for governed work.

ACLI Next is not ready for:

- owning planning logic;
- selecting Workers independently;
- authorizing mutations;
- interpreting validation output as authority;
- reconstructing replay;
- executing Git directly;
- replacing terminal workflows outside certified capability scope;
- replacing Codex for broad unsupported implementation tasks.

ACLI Next should become the default place to begin AiGOL development sessions, but not the exclusive tool for completing every development task.

## 9. Development Tasks Not Yet Complete Through AiGOL Next

| Development Task | Can Complete Through AiGOL Next? | Gap Class |
| --- | --- | --- |
| Advisory planning | Yes | Covered |
| Human clarification | Yes | Covered |
| Human approval capture | Yes | Covered |
| Read-only inspection where certified | Yes | Covered |
| Create one new plaintext file in allowlisted workspace | Yes | Covered |
| Replace one existing plaintext file in allowlisted workspace | Yes | Covered |
| Run one allowlisted validation command | Yes | Covered |
| Create one governed local commit | Yes | Covered |
| Multi-file implementation | No | Implementation gap |
| Patch or hunk-level implementation | No | Implementation gap |
| Iterative edit-test-repair loop | No | Workflow gap |
| Broad validation suite execution | No | Implementation gap |
| Package installation | No | Intentional manual step |
| Dependency update workflow | No | Implementation gap |
| Git branch workflow | No | Implementation gap |
| Git push | No | Implementation gap |
| Pull request creation | No | Workflow gap |
| Release tagging | No | Workflow gap |
| Deployment | No | Intentional manual step |
| Governed rollback execution | No | Implementation gap |
| Multi-interface operation through Web, REST, Mobile, or Voice | No | Tooling gap |

## 10. Readiness Determination

| Option | Finding |
| --- | --- |
| `PRIMARY_DEVELOPMENT_READY` | Not yet. Too many ordinary development tasks still require manual terminal, Git, or Codex support. |
| `HYBRID_DEVELOPMENT_RECOMMENDED` | Yes. ACLI Next should become the canonical governed starting point while manual/Codex/terminal support remains for unsupported tasks. |
| `TARGETED_DEVELOPMENT_GAPS_REMAIN` | Also true as supporting context, but the operational adoption posture is hybrid rather than blocked. |

The correct readiness posture is:

```text
HYBRID_DEVELOPMENT_RECOMMENDED
```

## 11. Recommended Adoption Policy

Adopt ACLI Next now for:

- governed development session bootstrap;
- advisory planning;
- clarification and confirmation;
- bounded certified mutation;
- bounded certified validation;
- governed local commit where the authorized file set and validation prerequisites are satisfied;
- replay-visible completion summaries.

Retain Codex and terminal use for:

- multi-file implementation;
- patch-level changes;
- arbitrary repository inspection;
- complex validation and test repair;
- dependency management;
- Git branch and remote workflows;
- release and deployment activities;
- rollback execution until certified.

Require future capability expansion to follow the G9-00 methodology:

```text
Need
-> Architecture Audit
-> Reuse
-> Canonical Projection Analysis
-> Minimal Canonicalization
-> Implementation
-> Architecture Review
-> Responsibility Realignment if needed
-> Certification
```

## 12. Recommended Next Priorities

Priority 0:

- governed multi-file mutation specification;
- governed patch or hunk-level mutation specification;
- governed rollback execution specification;
- governed validation suite expansion;
- ACLI Next end-to-end workflow for edit -> validate -> commit.

Priority 1:

- governed Git push specification;
- governed branch workflow specification;
- pull request or release registry integration review;
- deterministic status projection for current development session state.

Priority 2:

- package installation and dependency update governance audit;
- Web, REST, Mobile, and Voice thin-adapter reuse review;
- Architectural Health output envelope canonicalization if operational consumers require it.

Deferred:

- deployment automation;
- remote production mutation;
- autonomous broad Worker selection;
- unrestricted shell execution.

## 13. Final Determination

AiGOL Next is ready to become the canonical governed entrypoint for AiGOL development.

AiGOL Next is not yet ready to become the exclusive primary day-to-day development interface because important development capabilities still require manual terminal, Git, or Codex support.

The correct operational transition state is hybrid governed development:

```text
ACLI Next first for governed planning and certified execution.
Manual/Codex/Terminal fallback for unsupported tasks.
Targeted runtime expansion before exclusive primary adoption.
```

Final verdict: HYBRID_DEVELOPMENT_RECOMMENDED

## 14. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: HYBRID_DEVELOPMENT_RECOMMENDED
