# G10-01 Hybrid Primary Development Operating Guidelines V1

Status: hybrid primary development operating model canonicalized.

Final verdict: HYBRID_PRIMARY_DEVELOPMENT_OPERATING_MODEL_CANONICALIZED

## 1. Executive Summary

Generation 9 certified AiGOL as the canonical governed development foundation.

G10-00 established:

```text
HYBRID_PRIMARY_GOVERNED_DEVELOPMENT_RECOMMENDED
```

This document canonicalizes the day-to-day operating model for post-Generation 9 AiGOL development.

Canonical operating model:

```text
ACLI Next is the preferred development entrypoint for all certified governed repository development activities.
Hybrid external operation remains a temporary exception for uncertified operational boundaries.
```

This does not redesign Platform Core, introduce a new runtime subsystem, or change certified ownership boundaries. It formalizes how humans, ACLI Next, Platform Core, Governance, Replay, Worker Platform, and Architectural Health should interact during ordinary development.

Long-term direction:

```text
manual copy/paste should shrink as Generation 10 certifies operational extensions
without replacing the Governed Development Workflow
```

## 2. Operating Model Overview

The canonical post-Generation 9 development flow is:

```text
Human
-> ACLI Next
-> Governed Development Workflow
-> Platform Core
-> OCS
-> Governance
-> Worker Platform
-> Validation
-> Replay
-> Platform Digital Twin
-> Architectural Health
-> Human review
-> Architecture review
-> Certification
```

The hybrid exception flow is:

```text
Human
-> external operational tool
-> bounded manual execution
-> captured evidence
-> Replay continuity note
-> Governance continuity note
-> return to ACLI Next when certified workflow coverage resumes
```

The hybrid path is not a parallel development architecture. It is a temporary operational exception for capabilities not yet certified through Platform Core.

## 3. Mandatory ACLI Next Activities

The following activities shall normally begin inside ACLI Next when the capability is certified and available:

| Activity | Canonical Handling |
| --- | --- |
| Governed development requests | Start in ACLI Next and enter the Governed Development Workflow. |
| Architecture evolution | Start in ACLI Next as governed intent and route through Platform Core. |
| Capability readiness reviews | Create as governed artifacts through the canonical workflow. |
| Specifications | Create through governed artifact flow, preserving Replay and certification continuity. |
| Implementation planning | Route through Platform Core and OCS-owned candidate/proposal formation. |
| Governed file creation | Use certified governed mutation path. |
| Governed file replacement | Use certified existing-file mutation path. |
| Governed patch mutation | Use certified patch-level mutation path. |
| Governed multi-file mutation | Use certified transaction envelope. |
| Validation | Use governed validation execution or validation suites. |
| Rollback | Use certified governed rollback execution where rollback metadata exists. |
| Local Git commit | Use governed local Git commit path where available. |
| Architectural Health review | Use advisory projection from Platform Digital Twin evidence. |
| Architecture review | Create as governed review artifact after implementation. |
| Certification | Preserve Governance-owned certification verdicts and evidence. |

If a development action can be performed by certified AiGOL capability, it should not default to ChatGPT, Codex, direct terminal execution, or manual copy/paste.

## 4. Temporary Hybrid Activities

The following activities temporarily remain outside certified Platform Core coverage:

| Activity | Reason For Temporary Hybrid Status |
| --- | --- |
| Git remote workflows | Remote push, pull, fetch, branch switching, merge, rebase, and pull request creation cross repository and release boundaries not yet certified. |
| Dependency installation | Package manager execution may involve network access, registry trust, lockfile mutation, and transitive runtime changes. |
| Dependency updates | Requires package policy, lockfile integrity, validation suite policy, and Replay evidence model. |
| Deployment | Affects server/runtime activation, release discipline, environment authority, rollback readiness, and operational safety. |
| Exceptional operating-system work | Often involves local environment state outside certified Worker Platform scope. |
| Exceptional infrastructure administration | Crosses environment, credential, network, and deployment boundaries not yet governed. |
| Emergency investigation outside certified rollback | May require direct inspection before a governed recovery path exists. |

These are temporary exceptions because they are operational extensions, not architectural blockers.

They must not be reframed as:

- new authority layers;
- alternative development workflows;
- replacements for Platform Core;
- replacements for Governance;
- replacements for Replay.

## 5. Transition Rules

### 5.1 When Development Remains Entirely Inside AiGOL

Development remains inside AiGOL when:

- the requested action maps to a certified capability;
- required authorization can be obtained through Governance;
- execution can be performed through Worker Platform;
- evidence can be recorded by Replay;
- validation can be performed through governed validation;
- Architectural Health can observe deterministic evidence where applicable.

Examples:

- creating a governance artifact;
- editing an existing plaintext file;
- applying a patch-level mutation;
- performing a multi-file repository change;
- running a validation suite;
- executing supported rollback;
- preparing architecture review and certification evidence.

### 5.2 When External Tools Become Necessary

External tools become necessary only when:

- the capability is not certified;
- the action crosses a remote, deployment, package, credential, environment, or infrastructure boundary;
- the Worker Platform has no certified execution path;
- a failure requires investigation outside the governed runtime;
- the action would otherwise force Platform Core, ACLI Next, Governance, Replay, or Worker Platform to exceed certified ownership.

### 5.3 How The Transition Occurs

When external operation is required:

1. The human records that the activity is outside certified AiGOL coverage.
2. The scope of the external action is bounded before execution.
3. The external tool is used only for the unsupported operational step.
4. Evidence sufficient for continuity is captured after execution.
5. Replay continuity is restored through an explicit artifact, note, validation record, or subsequent governed workflow entry.
6. Governance continuity is restored by making the unsupported boundary visible in the next governed review or certification artifact.
7. Work returns to ACLI Next as soon as the certified workflow can resume.

### 5.4 Replay Continuity

Replay continuity must be preserved across hybrid execution by recording:

- what external action occurred;
- why ACLI Next could not perform it;
- which files, repository state, environment state, or external target were affected;
- what validation followed;
- what evidence remains outside Replay;
- what governed artifact restored continuity.

Hybrid work that cannot be replayed must remain visibly classified as an operational exception.

### 5.5 Governance Continuity

Governance continuity must be preserved by ensuring:

- external tools do not authorize themselves;
- external execution does not become certification evidence without review;
- unsupported boundaries remain visible;
- certification claims do not hide manual intervention;
- future capability requests are routed through `Reuse -> Canonicalization -> Extension`.

## 6. Copy/Paste Reduction Roadmap

### Stage 1: Current Hybrid-Primary Model

Current state:

```text
ACLI Next primary for certified governed repository development.
Manual copy/paste remains for uncertified operational boundaries.
```

Immediate reduction target:

- stop using manual copy/paste for ordinary governed mutation;
- stop using manual copy/paste for validation where suites are certified;
- stop using manual copy/paste for rollback where rollback metadata is certified;
- keep manual transfer only for unsupported operational exceptions.

### Stage 2: After Git Remote Support

Expected reduction:

- remote branch and push workflows move into governed execution;
- release-boundary Git evidence becomes Replay-visible;
- manual terminal Git usage shrinks to unsupported merge, rebase, emergency, or exceptional cases.

Remaining copy/paste:

- dependency management;
- deployment;
- exceptional environment operations.

### Stage 3: After Dependency Management

Expected reduction:

- package manager operations become governed;
- lockfile changes become Replay-visible;
- dependency validation suites become mandatory and governed;
- manual package-manager terminal work shrinks to unsupported package ecosystems or emergency repair.

Remaining copy/paste:

- deployment;
- exceptional infrastructure and environment operations.

### Stage 4: After Deployment Support

Expected reduction:

- release activation becomes governed;
- deployment evidence becomes Replay-visible;
- environment targeting and rollback readiness become governed;
- manual deployment copy/paste is eliminated for certified deployment targets.

Remaining copy/paste:

- exceptional operations outside certified environment scope;
- emergency recovery where no governed procedure exists.

### Long-Term Target Operating Model

Long-term target:

```text
Human
-> ACLI Next
-> Governed Development Workflow
-> Platform Core
-> Governance
-> Worker Platform
-> Replay
-> Architectural Health
-> Human review
```

External tools remain available, but only as governed operational integrations or visibly classified exceptions.

## 7. Human Interaction Model

### 7.1 Human Responsibilities

The human:

- expresses intent;
- approves scoped actions where required;
- retains final constitutional authority;
- decides whether to proceed after advisory findings;
- records exceptional hybrid operation honestly;
- does not treat convenience as authorization.

### 7.2 ACLI Next Responsibilities

ACLI Next:

- is the preferred human development entrypoint;
- captures intent;
- renders choices, evidence, and results;
- delegates to Platform Core;
- remains thin;
- does not authorize, execute, certify, or own workflow logic.

### 7.3 Platform Core Responsibilities

Platform Core:

- coordinates the Governed Development Workflow;
- routes to certified owners;
- preserves deterministic sequencing;
- coordinates capability discovery, reuse, canonicalization, and minimal extension;
- does not replace Governance, Replay, OCS, Worker Platform, or Architectural Health.

### 7.4 OCS Responsibilities

OCS:

- owns candidate and proposal formation;
- owns ordering where certified, including validation ordering;
- does not execute or authorize.

### 7.5 Governance Responsibilities

Governance:

- owns authorization;
- owns admissibility decisions;
- owns certification verdicts;
- does not execute work;
- does not become a Worker Platform substitute.

### 7.6 Worker Platform Responsibilities

Worker Platform:

- executes only authorized bounded actions;
- performs no Governance;
- performs no Replay ownership;
- performs no certification;
- performs no autonomous planning.

### 7.7 Replay Responsibilities

Replay:

- owns evidence;
- owns reconstruction;
- remains append-only where required;
- records governed activity and continuity evidence;
- does not authorize or execute.

### 7.8 Architectural Health Responsibilities

Architectural Health:

- consumes Platform Digital Twin and Replay-visible evidence;
- produces advisory findings;
- detects responsibility leakage and architectural drift;
- remains advisory-only;
- does not approve, reject, repair, execute, or certify.

## 8. Operational Principles

Canonical principles:

1. ACLI Next is the preferred development entrypoint.
2. Governed Development Workflow is the canonical development process.
3. External tools are operational extensions, not architectural authorities.
4. Replay continuity must be preserved across hybrid execution.
5. Governance continuity must be preserved across hybrid execution.
6. Architectural Health remains advisory-only.
7. Human approval remains mandatory where certified workflows require approval.
8. Human constitutional authority remains final.
9. Worker Platform executes only bounded authorized actions.
10. Platform Core coordinates only.
11. Certified ownership boundaries remain unchanged.
12. Future operational capabilities must integrate into the existing workflow.

## 9. Future Evolution Strategy

Future Generation 10 capabilities should progressively reduce manual copy/paste by certifying operational extensions in this order:

1. Git remote workflow.
2. Dependency management.
3. Deployment.
4. Exceptional environment operation patterns where repeated need is proven.

Each future capability must:

- begin with certified evidence review;
- reuse existing certified Platform Core capabilities;
- canonicalize behavior before extension;
- introduce only minimal necessary runtime expansion;
- preserve Governance authorization;
- preserve Replay evidence ownership;
- preserve Worker Platform execution-only boundaries;
- preserve Architectural Health advisory boundaries;
- enter the Governed Development Workflow rather than creating an alternative workflow.

No future capability should create:

- a new development authority;
- a new orchestration subsystem;
- an interface-owned execution path;
- a Replay bypass;
- a Governance bypass;
- uncontrolled deployment semantics.

## 10. Final Determination

The hybrid-primary operating model is now canonical.

Everyday AiGOL development should normally begin in ACLI Next and remain inside the Governed Development Workflow when certified capability coverage exists.

Manual ChatGPT, Codex, direct terminal, and copy/paste workflows remain valid only as visible operational exceptions for uncertified boundaries.

Final verdict: HYBRID_PRIMARY_DEVELOPMENT_OPERATING_MODEL_CANONICALIZED

## 11. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: HYBRID_PRIMARY_DEVELOPMENT_OPERATING_MODEL_CANONICALIZED
