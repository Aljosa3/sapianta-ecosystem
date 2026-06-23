# AIGOL_REPLAY_EXPERIENCE_V1

Status: Defined  
Scope: Product experience specification  
Baseline: AIGOL_SYSTEM_READY_BASELINE_V1  
Final verdict: AIGOL_REPLAY_EXPERIENCE_V1_DEFINED

## 1. Purpose

This artifact defines the human replay experience for AiGOL.

It describes how a human explores replay evidence after a governed decision, execution, validation, audit review, or improvement proposal.

This is productization work. It does not define new governance, new authority, new replay mechanics, new cognition behavior, new worker behavior, or new approval boundaries.

## 2. Baseline Context

The current certified system baseline is:

```text
AIGOL_SYSTEM_READY
AIGOL_SYSTEM_READY_BASELINE_DEFINED
```

The replay experience uses the already certified architecture:

```text
Human
  -> HIRR
  -> Governance
  -> Cognition Providers
  -> Worker Selection
  -> Workers
  -> Validation
  -> Replay
  -> Decision Validation Packet
  -> Audit Review
  -> Executive Review
  -> Replay-Derived Improvement
  -> PPP
  -> Human Approval
```

The replay experience must preserve:

```text
Human = Authority Layer
OCS = Governance Layer
Providers = Cognition Layer
Workers = Execution Layer
Replay = Source Of Truth
No Authority Transfer
No Autonomous Modification
Human Approval Boundary Preserved
```

## 3. Non-Goals

This artifact does not:

- design UI screens;
- implement replay visualization;
- change replay architecture;
- change replay storage;
- change approval boundaries;
- change governance semantics;
- introduce new authority layers;
- introduce new cognition behavior;
- introduce new worker behavior;
- create new certification claims.

## 4. Replay User Personas

### 4.1 Operator

Goals:

- understand what happened in a governed workflow;
- confirm whether the requested action completed, failed closed, or needs follow-up;
- verify that approvals and authorization were recorded;
- identify the next operational action.

Questions:

- What did I ask AiGOL to do?
- Did AiGOL understand the request correctly?
- Was clarification needed?
- Was approval requested and recorded?
- Did execution happen?
- What should I do next?

Required visibility:

- decision summary;
- replay timeline;
- approval status;
- execution status;
- validation result;
- next-action recommendation;
- links to raw replay only when needed.

### 4.2 Auditor

Goals:

- independently verify the decision path;
- verify evidence integrity;
- verify approval and authorization;
- verify provider and worker participation;
- confirm that replay reconstructs the governed path.

Questions:

- Which evidence supports this decision?
- Who approved execution?
- Was the worker authorized before execution?
- Which providers participated?
- Did any provider become authoritative?
- Can the replay chain be reconstructed?
- Is any evidence missing?

Required visibility:

- evidence families;
- replay references;
- artifact hashes;
- approval and authorization chain;
- provider participation records;
- worker selection and execution records;
- validation evidence;
- audit review package;
- raw replay drill-down.

### 4.3 Executive

Goals:

- understand the decision outcome quickly;
- understand business risk;
- verify whether governance and approval were present;
- decide whether to accept, escalate, or request audit review.

Questions:

- What was requested?
- What was decided?
- Why was it decided?
- What risk remains?
- Was approval present?
- Was execution verified?
- Can this be trusted without trusting the LLM?

Required visibility:

- executive summary layer;
- decision status;
- plain-language reason;
- risk summary;
- approval summary;
- outcome summary;
- trust status;
- drill-down links to audit review and replay.

### 4.4 Developer

Goals:

- inspect replay artifacts for defects, regressions, and improvement candidates;
- reproduce failure paths;
- verify replay-derived improvement lineage;
- preserve certification compatibility.

Questions:

- Which runtime stage produced the artifact?
- Which artifact failed or diverged?
- Which replay reference proves the behavior?
- Which certification protects this behavior?
- Does this create a replay-derived improvement candidate?

Required visibility:

- technical replay timeline;
- raw artifacts;
- artifact hashes;
- runtime stage names;
- source file references when available;
- reconstruction status;
- failure and dependency diagnostics;
- replay-derived improvement links.

## 5. Replay Navigation Model

Replay navigation must be deterministic.

The user must be able to enter replay through stable identifiers:

- Replay ID;
- Decision ID;
- Workflow ID;
- Approval ID;
- Authorization ID;
- Provider Invocation ID;
- Worker Execution ID;
- Validation ID;
- Audit Review ID;
- Decision Validation Packet ID;
- Executive Review ID;
- Improvement Intent ID.

### 5.1 Replay Entry Points

Replay ID:

```text
opens the complete replay timeline
```

Decision ID:

```text
opens decision overview, then timeline
```

Workflow ID:

```text
opens selected workflow and surrounding intent-resolution context
```

Approval ID:

```text
opens approval boundary, approved scope, and linked authorization
```

Worker Execution ID:

```text
opens worker handoff, authorization, execution result, and validation
```

Provider Invocation ID:

```text
opens provider participation, request/response evidence, and proposal-only status
```

Audit Review ID:

```text
opens audit review package and linked replay evidence
```

Improvement Intent ID:

```text
opens replay-derived gap, proposal status, PPP routing, and human approval state
```

### 5.2 Navigation Rules

Navigation must:

- preserve append-only replay references;
- never hide source artifacts;
- distinguish summary from raw replay;
- show missing evidence as missing, not inferred;
- fail closed when an identifier cannot be resolved;
- preserve source hashes and replay lineage;
- avoid exposing secrets.

## 6. Replay Timeline Experience

The replay timeline presents the governed path in human order:

```text
Intent
  -> Clarification
  -> Approval
  -> Provider Cognition
  -> Worker Selection
  -> Execution
  -> Validation
  -> Replay Recording
```

The timeline must let a human reconstruct:

- what happened;
- why it happened;
- who approved it;
- which evidence was used;
- what executed;
- what was validated;
- what failed closed, if anything.

### 6.1 Timeline Event Fields

Each timeline event should expose:

- event label;
- event status;
- human-readable summary;
- timestamp when available;
- actor or layer;
- replay reference;
- artifact hash;
- linked evidence;
- next event;
- failure reason when applicable.

### 6.2 Timeline Statuses

Allowed replay timeline statuses:

- RECORDED;
- VERIFIED;
- APPROVED;
- REJECTED;
- EXECUTED;
- VALIDATED;
- FAILED_CLOSED;
- PROPOSAL_ONLY;
- REVIEW_REQUIRED;
- SUPERSEDED.

## 7. Replay Evidence View

Evidence must be grouped by human question, not by file tree.

### 7.1 Intent Evidence

Purpose:

```text
show what the human asked and how AiGOL resolved the intent
```

Contents:

- original request;
- clarification question;
- clarification response;
- resolved intent;
- workflow target;
- confidence or fail-closed reason.

Trust value:

```text
proves the workflow began from human intent rather than hidden execution
```

### 7.2 Governance Evidence

Purpose:

```text
show how AiGOL governed routing, workflow selection, and boundaries
```

Contents:

- workflow selection;
- governance checks;
- fail-closed decisions;
- authority boundary records;
- PPP routing when applicable.

Trust value:

```text
proves AiGOL governed the path before execution or proposal progression
```

### 7.3 Approval Evidence

Purpose:

```text
show whether the human approved the action and what scope was approved
```

Contents:

- approval request;
- approval decision;
- approval scope;
- authorization reference;
- rejection or modification evidence.

Trust value:

```text
proves execution did not bypass human authority
```

### 7.4 Provider Evidence

Purpose:

```text
show cognition-provider participation without treating provider output as authority
```

Contents:

- provider selected;
- provider invoked;
- response received;
- participation role;
- proposal-only status;
- credential source reference without secret values;
- usage or failure metrics.

Trust value:

```text
proves what providers contributed and confirms they did not become authoritative
```

### 7.5 Worker Evidence

Purpose:

```text
show worker selection, authorization, handoff, execution, and result
```

Contents:

- worker candidates;
- selection rationale;
- suitability score;
- authorization reference;
- handoff package;
- execution result;
- side-effect evidence when applicable.

Trust value:

```text
proves the worker executed only after governed authorization
```

### 7.6 Validation Evidence

Purpose:

```text
show whether the result was checked and whether it passed
```

Contents:

- validation inputs;
- expected result;
- observed result;
- validation outcome;
- verification method;
- failure reason.

Trust value:

```text
proves the outcome was verified rather than merely claimed
```

### 7.7 Outcome Evidence

Purpose:

```text
show the final decision, output, or fail-closed state
```

Contents:

- final status;
- result summary;
- residual risk;
- audit status;
- next action;
- improvement candidate link when applicable.

Trust value:

```text
proves the final state is traceable to replay evidence
```

## 8. Decision Validation Packet Integration

Replay and the Decision Validation Packet must be bidirectional.

### 8.1 Replay Opens Packet

From replay, the user must be able to open:

- decision summary;
- evidence references;
- provider participation summary;
- worker participation summary;
- approval summary;
- authorization summary;
- independent verification workflow.

Purpose:

```text
convert raw replay into reviewer-readable decision validation
```

### 8.2 Packet Opens Replay

From the Decision Validation Packet, the user must be able to open:

- source replay root;
- timeline event references;
- raw evidence artifacts;
- approval and authorization records;
- provider and worker participation records;
- validation artifacts.

Purpose:

```text
let a reviewer verify the packet without trusting the packet summary
```

### 8.3 Bidirectional Rule

Every packet summary claim must link back to replay evidence.

Every replay event that contributes to the decision must be represented in the packet or explicitly marked as non-decision-supporting context.

## 9. Audit Review Integration

Replay and Audit Review must be bidirectional.

### 9.1 Replay Opens Audit Review

From replay, the user must be able to open:

- audit review package;
- reviewer checkpoints;
- evidence verification status;
- approval verification status;
- execution verification status;
- escalation path.

### 9.2 Audit Review Opens Replay

From audit review, the user must be able to open:

- evidence artifacts;
- approval artifacts;
- authorization artifacts;
- worker execution artifacts;
- validation artifacts;
- raw replay chain.

### 9.3 Audit Verification Tasks

Audit review must support:

- evidence verification;
- approval verification;
- authorization verification;
- execution verification;
- replay reconstruction verification;
- missing evidence escalation.

## 10. Executive Review Experience

The executive review layer is a summary layer above audit and replay.

Executives must see:

- decision;
- reason;
- risk;
- approval;
- outcome.

They must not need to navigate full replay to understand the business state.

### 10.1 Executive Summary Fields

Required fields:

- what was requested;
- what was decided;
- why it was decided;
- approval status;
- execution status;
- verification status;
- provider trust status;
- residual risk;
- recommended next action.

### 10.2 Executive Drill-Down

The executive layer must support drill-down to:

- Decision Validation Packet;
- Audit Review Package;
- Replay Timeline;
- Evidence View;
- Raw Replay.

The drill-down path must preserve the distinction between plain-language summary and replay evidence.

## 11. Explainability Layers

Replay visibility must be layered.

### L1 Executive

Exposes:

- decision outcome;
- reason;
- risk;
- approval state;
- verification state;
- trust status;
- next action.

Does not expose:

- raw JSON;
- runtime internals;
- provider request details;
- worker internals unless needed for risk.

### L2 Audit

Exposes:

- evidence checklist;
- approval chain;
- authorization chain;
- provider participation;
- worker participation;
- validation status;
- audit conclusions;
- escalation path.

Does not require:

- source-code knowledge;
- runtime implementation knowledge.

### L3 Technical

Exposes:

- replay references;
- artifact hashes;
- runtime stage names;
- failure envelopes;
- reconstruction details;
- certification links;
- improvement lineage.

Used by:

- developers;
- technical auditors;
- certification reviewers.

### L4 Raw Replay

Exposes:

- raw replay artifacts;
- canonical JSON;
- replay hashes;
- artifact hashes;
- append-only file paths.

Purpose:

```text
provide source-of-truth evidence for independent reconstruction
```

## 12. Trust Verification Workflow

The core user question is:

```text
Can I trust this decision?
```

Replay must answer through three paths.

### 12.1 Trust Path

The trust path answers:

```text
Was the governed process followed?
```

Checks:

- human intent recorded;
- workflow selected;
- approval required;
- authorization recorded;
- worker or provider role recorded;
- validation completed;
- replay reconstructed.

### 12.2 Verification Path

The verification path answers:

```text
Can I independently verify the outcome?
```

Checks:

- evidence references are present;
- raw replay is available;
- artifact hashes match;
- validation evidence exists;
- audit review links to replay;
- Decision Validation Packet links to replay.

### 12.3 Evidence Path

The evidence path answers:

```text
Which artifacts prove the claim?
```

Checks:

- intent evidence;
- governance evidence;
- approval evidence;
- provider evidence;
- worker evidence;
- validation evidence;
- outcome evidence.

### 12.4 Trust Outcomes

Allowed trust outcomes:

- TRUST_VERIFIED;
- TRUST_REVIEW_REQUIRED;
- TRUST_FAILED_CLOSED;
- TRUST_INSUFFICIENT_EVIDENCE;
- TRUST_ESCALATE_TO_AUDIT.

## 13. Future Replay Visualization Candidates

This artifact does not design UI.

Future visualization candidates:

### Timeline View

Purpose:

```text
show chronological replay events from intent to outcome
```

### Graph View

Purpose:

```text
show linked artifacts, hashes, decisions, approvals, providers, workers, and outcomes
```

### Evidence Tree

Purpose:

```text
group replay artifacts by evidence family and reviewer question
```

### Approval Tree

Purpose:

```text
show approval requests, approval decisions, authorization scope, and execution boundaries
```

### Execution Tree

Purpose:

```text
show worker selection, handoff, execution, validation, and side-effect verification
```

### Improvement Lineage View

Purpose:

```text
show replay-derived gaps, improvement intents, PPP routing, human approval, supersession, and certification closure
```

## 14. Success Criteria

AIGOL_REPLAY_EXPERIENCE_V1 succeeds if it clearly defines:

- who uses replay;
- how replay is entered;
- how replay is navigated;
- how a timeline is consumed;
- how evidence is grouped;
- how Decision Validation Packets connect to replay;
- how Audit Review connects to replay;
- how Executive Review summarizes replay;
- how layered explainability works;
- how a human verifies trust using replay only.

It must remain a product experience foundation, not an implementation or governance redesign.

## 15. Baseline Preservation Statement

This artifact preserves the certified baseline:

```text
Human = Authority Layer
OCS = Governance Layer
Providers = Cognition Layer
Workers = Execution Layer
Replay = Source Of Truth
No Authority Transfer
No Autonomous Modification
Human Approval Boundary Preserved
```

## 16. Final Verdict

```text
AIGOL_REPLAY_EXPERIENCE_V1_DEFINED
```
