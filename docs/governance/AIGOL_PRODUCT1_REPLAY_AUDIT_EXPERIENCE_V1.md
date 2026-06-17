# AIGOL Product 1 Replay Audit Experience V1

Status: Product 1 UX architecture.

Purpose: design the first enterprise replay and audit experience for Product 1, the AI Decision Validator.

This artifact is design only.

It does not redesign governance.

It does not redesign replay.

It does not invoke providers.

It does not activate workers.

It uses existing replay, audit, evidence, summary, reconstruction, and improvement-intent infrastructure.

## Context

Provider program status:

```text
COMPLETE
```

Post-provider roadmap recommendation:

```text
AIGOL_PRODUCT1_REPLAY_AUDIT_EXPERIENCE_V1
```

Product 1 identity:

```text
AI Decision Validator
```

Enterprise value focus:

```text
explainability
traceability
auditability
evidence usability
```

## 1. Current Replay Artifact Review

Existing replay infrastructure already provides ordered, immutable, hash-checked evidence.

Core replay patterns:

```text
numbered replay files
replay_index
replay_step
artifact
artifact_hash
replay_hash
reconstruct_* functions
fail-closed replay validation
```

Relevant replay surfaces:

```text
operator replay
ACLI conversation replay
OCS stage replay
ERR selection replay
worker assignment replay
provider boundary replay
execution runtime replay
post-dispatch replay
post-execution replay review
replay gap detection
replay-to-improvement intent
unified replay reconstruction
```

Existing navigation primitives:

```text
replay_reference
source_replay_reference
execution_replay_reference
operator_replay_reference
conversation_replay_reference
stage_replay
canonical_chain_id
artifact_hash
replay_hash
```

Product 1 implication:

Replay already contains the evidence needed for enterprise inspection. The missing Product 1 layer is an enterprise-readable navigation and explanation model.

## 2. Current Audit Artifact Review

Existing audit artifacts include:

```text
post-dispatch audit packet
post-dispatch recertification packet
rollback execution artifact
post-execution replay review artifacts
governed result summary
operator summary
capability audit artifacts
semantic context audit bundles
governance conformance evidence
provider boundary audit artifacts
live provider runtime boundary audit
```

Representative audit statuses:

```text
PASS
FAILED_CLOSED
REVIEW_COMPLETED
INTEGRITY_VERIFIED
ROLLBACK_NOT_REQUIRED
ROLLBACK_EXECUTED
OPERATOR_SUMMARY_CREATED
```

Product 1 implication:

Audit evidence should be presented as a decision review packet, not as a file tree. The reviewer needs to see status, reason, lineage, and proof points first, with raw artifacts available underneath.

## 3. Evidence Artifact Review

Evidence artifacts already capture:

```text
who or what requested action
which capability was requested
which resource was selected
which authority boundaries were preserved
which replay references were created
which hashes bind artifacts together
whether execution completed or failed closed
whether provider or worker invocation occurred
whether governance or replay mutation occurred
whether secrets or authorization headers were replayed
```

Evidence families relevant to Product 1:

```text
intent evidence
route selection evidence
provider selection evidence
worker selection evidence
credential evidence
request envelope evidence
response envelope evidence
error envelope evidence
cognition artifact evidence
execution evidence
audit packet evidence
recertification evidence
rollback evidence
gap detection evidence
improvement intent evidence
```

Product 1 implication:

Evidence should be grouped by reviewer question:

```text
What was requested?
What did AiGOL decide?
What evidence supports that decision?
What boundaries were preserved?
What failed closed, if anything?
What should a human review next?
```

## 4. Enterprise Reviewer Information Needs

An enterprise reviewer needs a readable answer to ten questions:

```text
1. What decision or request entered the system?
2. What route or workflow did AiGOL select?
3. Was clarification required?
4. Which provider or worker resource was selected, if any?
5. Was any provider or worker actually invoked?
6. What was the final decision status?
7. Why did the decision complete or fail closed?
8. Which replay evidence proves the outcome?
9. Were secrets, authority, governance, and replay boundaries preserved?
10. Is a human follow-up, audit, rollback, or improvement intent required?
```

The reviewer does not initially need raw JSON.

The reviewer needs:

```text
decision status
plain-language reason
evidence chain
boundary guarantees
verification status
drill-down replay references
next required human action
```

## UX Architecture

The first Product 1 replay/audit experience should be a read-only evidence cockpit.

Primary screens:

```text
Decision Overview
Replay Timeline
Audit Packet
Evidence Inspector
Boundary Guarantees
Improvement Candidates
Raw Replay
```

### Decision Overview

Purpose:

```text
answer what happened
```

Fields:

```text
decision/request summary
final status
workflow selected
capability requested
provider/worker selection summary
completion or fail-closed reason
recommended next action
replay verification status
```

Existing infrastructure:

```text
GOVERNED_RESULT_SUMMARY_V1
OPERATOR_SUMMARY_ARTIFACT_V1
REPLAY_SUMMARY_COMMAND_V1
```

### Replay Timeline

Purpose:

```text
show the chain of events in order
```

Timeline groups:

```text
human input
intent clarification
routing
OCS cognition
ERR resource selection
provider boundary
worker assignment
execution or fail-closed event
audit
recertification
rollback
improvement intent
```

Existing infrastructure:

```text
UNIFIED_REPLAY_RECONSTRUCTION_RUNTIME_V1
canonical_chain_id
replay_index
replay_step
stage_replay
```

### Audit Packet

Purpose:

```text
show whether the decision is audit-ready
```

Sections:

```text
audit verdict
post-dispatch audit status
recertification status
rollback status
replay hash status
artifact count
lineage continuity
known limitations
```

Existing infrastructure:

```text
POST_EXECUTION_REPLAY_REVIEW_ARTIFACT_V1
FIRST_LIVE_PROVIDER_POST_DISPATCH_AUDIT_PACKET_ARTIFACT_V1
FIRST_LIVE_PROVIDER_POST_DISPATCH_RECERTIFICATION_PACKET_ARTIFACT_V1
FIRST_LIVE_PROVIDER_ROLLBACK_EXECUTION_ARTIFACT_V1
```

### Evidence Inspector

Purpose:

```text
show proof without overwhelming the reviewer
```

Default view:

```text
evidence card
artifact type
artifact status
source replay reference
artifact hash
boundary flags
human-readable summary
```

Drill-down view:

```text
raw artifact JSON
wrapper hash
artifact hash
linked references
reconstruction result
```

### Boundary Guarantees

Purpose:

```text
show why the system remained governed
```

Required indicators:

```text
provider authority = false
worker self-authorization = false
governance mutation = false
replay mutation = false
secret replay = false
authorization header replay = false
automatic retry = false
fallback = false
provider routing = false unless explicitly part of a governed route
human review required where applicable
```

### Improvement Candidates

Purpose:

```text
show governed learning opportunities without autonomous mutation
```

Sources:

```text
GAP_DETECTION_ARTIFACT_V1
GAP_CLASSIFICATION_ARTIFACT_V1
GAP_EVIDENCE_ARTIFACT_V1
IMPROVEMENT_INTENT_ARTIFACT_V1
```

Rules:

```text
proposal_created = false unless explicitly created elsewhere
ppp_invoked = false unless explicitly invoked elsewhere
provider_invoked = false
worker_invoked = false
execution_requested = false
human_review_required = true when improvement is possible
```

### Raw Replay

Purpose:

```text
support technical audit and regulator-style inspection
```

Capabilities:

```text
open raw artifact
view artifact hash
view replay wrapper hash
copy replay reference
compare artifact linkage
show reconstruction errors
```

This is a drill-down layer, not the default enterprise view.

## Reviewer Journey

### Journey 1: Completed Governed Decision

```text
1. Reviewer opens Decision Overview.
2. Reviewer sees COMPLETED status and short reason.
3. Reviewer opens Replay Timeline.
4. Reviewer verifies route, provider/worker selection, and audit steps.
5. Reviewer opens Boundary Guarantees.
6. Reviewer verifies no secret replay, no worker self-authorization, no governance mutation, and no replay mutation.
7. Reviewer opens Audit Packet.
8. Reviewer confirms audit and recertification status.
9. Reviewer exports or records replay reference.
```

### Journey 2: Fail-Closed Decision

```text
1. Reviewer opens Decision Overview.
2. Reviewer sees FAILED_CLOSED status and failure reason.
3. Reviewer opens Replay Timeline.
4. Reviewer locates first failed stage.
5. Reviewer opens Evidence Inspector for the failed artifact.
6. Reviewer verifies no retry, no fallback, and no hidden execution.
7. Reviewer opens Improvement Candidates.
8. Reviewer determines whether human-reviewed improvement intent is appropriate.
```

### Journey 3: Unknown Governance Coverage

```text
1. Reviewer opens Decision Overview.
2. Reviewer sees coverage unknown or clarification required.
3. Reviewer opens Replay Timeline.
4. Reviewer verifies where certainty stopped.
5. Reviewer opens Improvement Candidates.
6. Reviewer confirms that no automatic governance expansion occurred.
7. Reviewer routes follow-up through human-reviewed planning only.
```

## Replay Navigation Model

Replay navigation should use four levels.

### Level 1: Decision

Identifier:

```text
operator_flow_id or canonical_chain_id
```

User question:

```text
What happened?
```

### Level 2: Stage

Examples:

```text
intent
routing
OCS
ERR
provider
worker
execution
audit
rollback
improvement
```

User question:

```text
Where did it happen?
```

### Level 3: Artifact

Examples:

```text
request envelope
response envelope
error envelope
resource selection evidence
audit packet
recertification packet
rollback artifact
gap evidence
improvement intent
```

User question:

```text
What is the proof?
```

### Level 4: Hash And Raw Evidence

Examples:

```text
artifact_hash
replay_hash
source artifact hash
linked artifact hash
raw JSON
```

User question:

```text
Can this be verified?
```

## Audit Navigation Model

Audit navigation should use six stable review checks.

```text
1. Outcome
2. Authority
3. Evidence
4. Boundary
5. Replay Integrity
6. Next Action
```

### Outcome

Show:

```text
completed
failed closed
waiting for human
review completed
rollback executed
```

### Authority

Show:

```text
human authority retained
provider non-authoritative
worker non-authoritative
governance not mutated
replay not mutated
```

### Evidence

Show:

```text
artifact count
critical artifact list
replay references
hash status
missing evidence warnings
```

### Boundary

Show:

```text
secret replay status
authorization header replay status
retry/fallback status
provider invocation status
worker invocation status
dispatch status
```

### Replay Integrity

Show:

```text
ordering verification
wrapper hash verification
artifact hash verification
lineage link verification
reconstruction status
```

### Next Action

Show:

```text
retain replay reference
review failure reason
perform rollback review
request clarification
create human-reviewed improvement intent
do not retry without new authorization
```

## Explainability Model

Explainability should be layered.

### Plain Explanation

Purpose:

```text
tell an enterprise reviewer what happened in one paragraph
```

Source:

```text
governed result summary
operator summary
audit packet
```

### Structured Explanation

Purpose:

```text
show why AiGOL reached the outcome
```

Fields:

```text
input
route
capability
selected resource
critical checks
final status
failure reason
next action
```

### Technical Explanation

Purpose:

```text
support engineering audit
```

Fields:

```text
artifact ids
artifact hashes
replay hashes
reconstruction results
lineage references
raw artifact links
```

### Governance Explanation

Purpose:

```text
show why the decision remained bounded
```

Fields:

```text
authority boundary reminder
provider non-authority
worker non-authority
human review requirement
fail-closed status
no mutation guarantees
```

## Evidence Presentation Model

Evidence should be presented as cards grouped by role.

### Input Evidence

Cards:

```text
human request
clarification state
routing decision
capability requested
```

### Resource Evidence

Cards:

```text
ERR provider selection
ERR worker selection
provider metadata
worker metadata
selection replay hash
```

### Execution Evidence

Cards:

```text
request envelope
credential boundary
response envelope
error envelope
worker assignment
dispatch packet
completion or fail-closed artifact
```

### Audit Evidence

Cards:

```text
audit packet
recertification packet
rollback artifact
post-execution review
governed result summary
operator summary
```

### Improvement Evidence

Cards:

```text
gap evidence
gap classification
gap detection
improvement intent
human review requirement
```

## Trust And Verification Workflow

The reviewer workflow should be deterministic:

```text
1. Confirm replay reference exists.
2. Reconstruct replay using existing reconstruction runtime.
3. Verify ordered replay steps.
4. Verify wrapper hashes.
5. Verify artifact hashes.
6. Verify lineage references.
7. Verify boundary flags.
8. Verify audit packet and recertification packet.
9. Verify rollback state.
10. Verify no prohibited evidence exists.
11. Record trusted, failed-closed, or review-required status.
```

Trust states:

```text
TRUSTED_REPLAY_VERIFIED
FAILED_CLOSED_VERIFIED
HUMAN_REVIEW_REQUIRED
REPLAY_INTEGRITY_WARNING
EVIDENCE_MISSING
```

Prohibited trust claims:

```text
automatic legal compliance
perfect safety
provider authority
worker self-authorization
autonomous governance improvement
silent replay repair
```

## Product 1 UX Milestones

### Milestone 1: Product 1 Audit Information Architecture

Goal:

```text
define read-only view model for existing replay and audit artifacts
```

Deliverables:

```text
view schema
navigation map
artifact grouping rules
reviewer labels
acceptance criteria
```

### Milestone 2: Read-Only Replay Summary Adapter

Goal:

```text
normalize existing summaries into one Product 1 decision overview
```

Use existing:

```text
GOVERNED_RESULT_SUMMARY_V1
OPERATOR_SUMMARY_ARTIFACT_V1
REPLAY_SUMMARY_COMMAND_V1
UNIFIED_REPLAY_RECONSTRUCTION_REPORT_V1
```

### Milestone 3: Audit Evidence Inventory View

Goal:

```text
show artifact cards for evidence, boundary guarantees, and replay references
```

No runtime mutation.

No new governance semantics.

### Milestone 4: Fail-Closed Explanation View

Goal:

```text
make failure reason, first failed stage, rollback evidence, and next action obvious
```

### Milestone 5: Replay-Derived Improvement View

Goal:

```text
show confirmed gaps and human-reviewed improvement intent candidates without autonomous mutation
```

### Milestone 6: Enterprise Demo Integration

Goal:

```text
integrate the read-only audit experience into the Product 1 enterprise demo flow
```

Required constraints:

```text
demo-only presentation
read-only replay inspection
no production compliance claims
known limitations visible
```

## Recommended Implementation Roadmap

### Step 1: Define Product 1 Audit View Schema

Priority:

```text
VERY HIGH
```

Reason:

All later UX work needs a stable read-only view model.

### Step 2: Build Read-Only Aggregation Runtime

Priority:

```text
HIGH
```

Scope:

```text
read existing replay references
call existing reconstructors
produce Product 1 view artifact
write optional replay-visible summary
no mutation of source replay
```

### Step 3: Create Evidence Card Renderer

Priority:

```text
HIGH
```

Scope:

```text
render artifact role
render status
render boundary flags
render replay reference
render hash status
render raw artifact link
```

### Step 4: Create Fail-Closed Review Mode

Priority:

```text
HIGH
```

Scope:

```text
first failed stage
failure reason
rollback status
no retry/fallback proof
recommended next action
```

### Step 5: Add Replay-Derived Improvement Panel

Priority:

```text
MEDIUM_HIGH
```

Scope:

```text
gap categories
confidence
human review requirement
improvement intent eligibility
no autonomous mutation proof
```

### Step 6: Integrate With Enterprise Demo UX

Priority:

```text
MEDIUM_HIGH
```

Scope:

```text
decision overview
timeline
audit packet
evidence inspector
boundary guarantees
raw replay
```

## Acceptance Criteria

The Product 1 replay/audit experience is acceptable when:

```text
enterprise reviewer can understand what happened
enterprise reviewer can inspect why it happened
enterprise reviewer can verify replay evidence exists
enterprise reviewer can verify boundary guarantees
enterprise reviewer can identify missing or failed evidence
enterprise reviewer can see next required human action
enterprise reviewer can drill down into raw replay
the experience remains read-only
the experience does not create governance authority
the experience does not imply automatic legal compliance
```

## Non-Goals

Do not implement:

```text
new governance semantics
new replay model
new provider execution
new worker execution
new authorization flow
replay repair
automatic improvement implementation
compliance certification engine
multi-provider comparison UX expansion
production deployment automation
```

## Final Recommendation

Proceed next with:

```text
AIGOL_PRODUCT1_AUDIT_VIEW_SCHEMA_V1
```

This should define the concrete read-only Product 1 audit view artifact before any UI implementation.

The first implementation should aggregate existing evidence rather than creating new governance behavior.
