# G10-03 ACLI Next Daily Operational Exposure Specification V1

Status: ACLI Next daily operational exposure specified.

Final verdict: ACLI_NEXT_DAILY_OPERATIONAL_EXPOSURE_SPECIFIED

## 1. Executive Summary

G10-02 determined that the primary Generation 10 limitation is operational exposure, not Platform Core architecture.

Certified governed capabilities exist, but ordinary development still falls back to:

```text
ChatGPT
-> Codex
-> Terminal
-> manual copy/paste
```

for work that should naturally begin in ACLI Next.

This specification defines how ACLI Next should expose existing certified governed development capabilities during daily work.

Core principle:

```text
ACLI Next shows, guides, and delegates.
Platform Core coordinates.
Governance authorizes.
Replay owns evidence.
Worker Platform executes.
Architectural Health advises.
```

This specification does not create new Platform Core capabilities, new authority layers, new runtime subsystems, or new execution semantics.

## 2. Design Goals

The daily operational exposure model must:

- make ACLI Next the natural starting point for certified development work;
- reduce unnecessary ChatGPT, Codex, terminal, and manual copy/paste transitions;
- expose the current Governed Development Workflow stage;
- present available certified actions without taking ownership of them;
- guide the human toward required approval, validation, Replay, and certification steps;
- visibly classify unsupported operations as hybrid exceptions;
- preserve Governance, Replay, Worker Platform, Platform Digital Twin, and Architectural Health ownership;
- preserve deterministic `Reuse -> Canonicalization -> Extension`.

Non-goals:

- no Platform Core redesign;
- no new orchestration engine;
- no ACLI-owned authorization;
- no ACLI-owned execution;
- no ACLI-owned Replay;
- no ACLI-owned Architectural Health;
- no deployment, dependency, or Git remote implementation in this specification.

## 3. Canonical Daily Development Workflow

ACLI Next should present daily development as one canonical guided workflow:

```text
1. Capture Intent
2. Classify Capability Coverage
3. Show Workflow Stage
4. Form Candidate / Proposal
5. Request Human Approval if required
6. Request Governance Authorization if required
7. Delegate Worker Execution if required
8. Show Replay Evidence
9. Show Validation Result
10. Show Architectural Health Advisory
11. Prepare Review / Certification Artifact
12. Show Completion Or Hybrid Exception
```

Ownership remains unchanged:

| Stage | ACLI Next Role | Certified Owner |
| --- | --- | --- |
| Capture Intent | Human interface | Human / ACLI Next as thin entrypoint |
| Capability Coverage | Display result | Platform Core / capability discovery |
| Candidate / Proposal | Render candidate | OCS / Platform Core |
| Approval | Prompt and capture response | Human / Governance |
| Authorization | Display authorization state | Governance |
| Execution | Show progress | Worker Platform |
| Evidence | Show summary and links | Replay |
| Validation | Show commands and results | Worker Platform / Replay / Governance |
| Advisory Review | Show findings | Architectural Health |
| Certification | Render status and verdict | Governance |

ACLI Next must never become the source of truth for workflow state. It presents state derived from certified owners.

## 4. Development Workflow Visibility

ACLI Next should always display:

- current workflow stage;
- current operation;
- certified owner for the current operation;
- next expected human action;
- pending approvals;
- pending Governance authorization;
- completed stages;
- failed or blocked stages;
- Replay evidence availability;
- validation status;
- Architectural Health status;
- hybrid exception status.

Minimum stage states:

| State | Meaning |
| --- | --- |
| `not_started` | Stage has not begun. |
| `pending_human` | Human approval, clarification, or decision is required. |
| `pending_governance` | Governance authorization or certification is required. |
| `pending_worker` | Authorized Worker Platform execution is waiting or running. |
| `evidence_pending` | Replay evidence has not yet been recorded or surfaced. |
| `validation_pending` | Validation has not yet run or completed. |
| `advisory_pending` | Architectural Health advisory output is unavailable or pending. |
| `complete` | Stage completed with evidence. |
| `failed_closed` | Stage failed without unsafe continuation. |
| `hybrid_required` | Operation exceeds certified capability coverage. |

The display must clearly identify whether the current stage is:

- advisory;
- approval;
- authorization;
- execution;
- evidence;
- validation;
- certification;
- hybrid exception.

## 5. Governed Capability Exposure Model

ACLI Next should expose certified capabilities as guided actions, not as independent commands with their own authority.

Minimum daily action set:

| Action | Exposed Through ACLI Next As | Delegated Owner |
| --- | --- | --- |
| Create governance artifact | `start governed artifact` | Platform Core / Worker Platform / Replay |
| Create specification | `start specification` | Platform Core / OCS / Governance |
| Create implementation plan | `start implementation plan` | Platform Core / OCS |
| Start implementation | `start governed implementation` | Platform Core / Governance / Worker Platform |
| Create architecture review | `start architecture review` | Platform Core / Governance / Architectural Health |
| Create certification review | `start certification review` | Governance / Replay |
| Create new file | `create file` | Worker Platform after authorization |
| Replace file | `replace file` | Worker Platform after authorization |
| Apply patch | `apply patch` | Worker Platform after authorization |
| Multi-file mutation | `start transaction` | Platform Core / Worker Platform |
| Rollback | `start rollback` | Replay / Governance / Worker Platform |
| Run validation | `run validation` | Worker Platform / Replay |
| Run validation suite | `run validation suite` | Platform Core / Worker Platform / Replay |
| Local Git commit | `create governed commit` | Governance / Worker Platform / Replay |

Each action must show:

- capability name;
- certification status;
- required approvals;
- required authorization;
- expected evidence;
- rollback availability;
- validation requirements;
- unsupported boundary warnings.

## 6. Governed Artifact Creation

ACLI Next should allow a developer to initiate governed artifact creation by selecting or entering:

- artifact type;
- objective;
- latest certified verdict;
- scope;
- constraints;
- required validation;
- expected final verdict.

Supported artifact categories:

- readiness review;
- specification;
- implementation documentation;
- architecture review;
- certification review;
- operating guideline;
- governance audit;
- pilot review;
- roadmap review.

Canonical artifact flow:

```text
human intent
-> ACLI Next capture
-> Platform Core workflow binding
-> OCS candidate/proposal where applicable
-> human approval if required
-> Governance authorization if required
-> Worker Platform file creation or mutation
-> Replay evidence
-> validation
-> final verdict rendering
```

ACLI Next must present the artifact as governed work, not as a local editor shortcut.

## 7. Validation Exposure

ACLI Next should expose validation through certified validation capabilities only.

It should present:

- available validation commands;
- available validation suites;
- suite ordering;
- required Governance authorization;
- command allowlist status;
- running state;
- exit code;
- stdout/stderr summary;
- result classification;
- validation summary;
- Replay evidence link or identifier.

Validation exposure must not:

- execute shell commands directly inside ACLI Next;
- modify allowlists;
- invent validation authority;
- skip Governance authorization where required;
- treat terminal output as Replay evidence unless recorded by Replay.

Minimum display:

```text
Validation suite: <name>
Status: pending | running | passed | failed_closed
Commands: <ordered list>
Authorized by: <governance evidence>
Replay evidence: <artifact or unavailable>
Summary: <deterministic result>
```

## 8. Replay Presentation Model

ACLI Next should make Replay visible without becoming Replay.

It should present:

- evidence identifier;
- operation type;
- authorized scope;
- pre-state summary where applicable;
- post-state summary where applicable;
- command or mutation result;
- validation evidence;
- rollback metadata availability;
- reconstruction status;
- links or references to evidence artifacts.

Replay summaries must distinguish:

- complete Replay evidence;
- partial manual continuity notes;
- hybrid exception evidence;
- missing evidence;
- reconstruction failure.

Minimum display:

```text
Replay status: complete | partial | missing | failed_closed
Evidence: <identifier>
Reconstruction: available | unavailable
Rollback metadata: available | unavailable | not_applicable
Continuity note: <required only for hybrid exceptions>
```

ACLI Next must not treat its own display state as authoritative evidence.

## 9. Architectural Health Presentation Model

ACLI Next should present Architectural Health output as advisory-only.

It should show:

- finding identifier;
- severity;
- affected owner or boundary;
- evidence source;
- recommendation;
- advisory status;
- whether human review is required;
- whether certification should explicitly address the advisory.

Severity display:

| Severity | Meaning |
| --- | --- |
| `info` | Advisory context or non-blocking observation. |
| `low` | Minor drift or documentation clarity concern. |
| `medium` | Potential ownership ambiguity or evidence gap. |
| `high` | Strong responsibility leakage or architecture regression concern. |
| `critical` | Apparent violation of certified authority boundary requiring human and Governance review. |

Architectural Health must remain:

- deterministic;
- Replay-visible;
- derived from Platform Digital Twin evidence;
- advisory-only;
- non-authoritative.

ACLI Next must not render Architectural Health findings as automatic approvals, rejections, repairs, or certifications.

## 10. Hybrid Transition Model

ACLI Next should detect or classify operations that exceed certified capability coverage.

Hybrid-triggering examples:

- Git remote push, pull, fetch, merge, rebase, branch switching, or pull request creation;
- dependency installation or update;
- deployment or server activation;
- exceptional operating-system work;
- exceptional infrastructure administration;
- unsupported environment recovery;
- provider or network operation outside certified scope.

When hybrid execution is required, ACLI Next should display:

```text
Hybrid operation required.
Reason: <uncertified boundary>
Certified coverage ends at: <stage>
Recommended external tool: <tool or category>
Required continuity evidence: <list>
Return condition: <when ACLI Next should resume>
Governance note required: yes/no
Replay continuity note required: yes/no
```

Required continuity fields:

- external operation performed;
- reason ACLI Next could not perform it;
- scope of external action;
- files, repository state, environment, or remote target affected;
- validation performed afterward;
- evidence captured outside Replay;
- governed artifact that restores continuity.

ACLI Next should keep hybrid operation visible until continuity is restored.

## 11. Daily Dashboard Specification

ACLI Next should expose a compact daily development dashboard.

Minimum sections:

### 11.1 Current Governed Workflow

Fields:

- workflow identifier;
- current stage;
- current operation;
- certified owner;
- next action;
- blocked reason if any.

### 11.2 Active Task

Fields:

- task objective;
- artifact or file targets;
- capability classification;
- scope boundary;
- expected final verdict where applicable.

### 11.3 Pending Approvals

Fields:

- human approval required;
- Governance authorization required;
- approval scope;
- approval hash or evidence reference where applicable.

### 11.4 Validation Status

Fields:

- latest validation command or suite;
- status;
- result;
- Replay evidence reference;
- required next validation.

### 11.5 Replay Summary

Fields:

- latest evidence;
- reconstruction status;
- rollback metadata;
- continuity status.

### 11.6 Architectural Health Summary

Fields:

- finding count;
- highest severity;
- unresolved advisory findings;
- evidence source;
- recommendation summary.

### 11.7 Certification Status

Fields:

- current certification target;
- latest certified verdict;
- pending review artifact;
- final verdict if complete.

### 11.8 Hybrid Operation Status

Fields:

- hybrid mode active or inactive;
- reason;
- external tool;
- continuity evidence required;
- return condition.

The dashboard must expose existing evidence and certified capability state only.

## 12. Interface Behavior Requirements

ACLI Next should:

- use plain language for human-readable state;
- identify certified owner for each action;
- show why an action is available or unavailable;
- fail closed when capability coverage is absent;
- distinguish advisory findings from authorization decisions;
- distinguish validation failure from Governance rejection;
- distinguish manual continuity notes from Replay-owned evidence;
- keep unsupported operations visible until continuity is restored.

ACLI Next should not:

- silently downgrade governed work into local terminal work;
- hide hybrid exceptions;
- imply that advisory findings are authoritative;
- imply that validation success equals certification;
- imply that Replay summaries are the same as full reconstruction evidence;
- create a second development workflow.

## 13. Future Integration Principles

Future operational capabilities must plug into the certified Governed Development Workflow.

Integration rule:

```text
new operational capability
-> capability discovery
-> reuse evaluation
-> canonicalization decision
-> minimal extension if required
-> Governance authorization
-> Worker Platform execution
-> Replay evidence
-> Architectural Health advisory visibility
-> architecture review
-> certification
-> ACLI Next exposure
```

Future capabilities should add dashboard sections or actions only when backed by certified owners.

Examples:

- Git remote workflow should add remote target, branch state, authorization, command result, and Replay evidence fields.
- Dependency management should add package request, registry boundary, lockfile summary, validation suite, and Replay evidence fields.
- Deployment should add release target, environment authority, rollback readiness, deployment evidence, and certification status fields.

No future integration may bypass:

- Platform Core coordination;
- Governance authorization;
- Replay evidence ownership;
- Worker Platform execution-only boundary;
- Architectural Health advisory-only boundary.

## 14. Final Determination

ACLI Next daily operational exposure is specified.

The next implementation should expose certified governed development capabilities through ACLI Next as a guided, evidence-visible workflow.

This is an interface exposure and workflow visibility milestone, not an architecture redesign.

Final verdict: ACLI_NEXT_DAILY_OPERATIONAL_EXPOSURE_SPECIFIED

## 15. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: ACLI_NEXT_DAILY_OPERATIONAL_EXPOSURE_SPECIFIED
