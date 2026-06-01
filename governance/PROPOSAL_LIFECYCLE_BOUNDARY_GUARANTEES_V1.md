# Proposal Lifecycle Boundary Guarantees V1

Status: boundary guarantees.

## Certified Guarantees

The proposal lifecycle foundation preserves constitutional authority separation.

## Proposal Boundary

A proposal is candidate intent only.

It cannot:

- execute;
- authorize;
- govern;
- dispatch;
- mutate replay;
- mutate workers;
- mutate providers;
- mutate constitutional artifacts.

## Conversation Boundary

Conversation may produce human-readable responses and proposal candidates.

Conversation does not become execution authority.

## Provider Boundary

Provider participation is proposal-only.

Provider may:

- suggest classification;
- suggest response content;
- contribute proposal evidence.

Provider may not:

- create authoritative proposal state;
- approve proposals;
- derive execution requests;
- dispatch workers;
- execute tasks;
- mutate replay;
- govern lifecycle transitions.

## AiGOL Governance Boundary

AiGOL governs the lifecycle by:

- creating proposal artifacts from bounded evidence;
- inspecting proposal validity;
- rejecting invalid or unsafe proposals;
- expiring stale proposals;
- verifying human approval evidence;
- deriving governed execution requests only when valid;
- preserving replay lineage.

AiGOL does not treat provider output as authority.

## Human Approval Boundary

Human approval is required for proposal approval.

Human approval does not replace:

- AiGOL inspection;
- constitutional validation;
- capability boundary validation;
- replay lineage validation;
- future execution request authorization.

## Worker Boundary

Worker execution is outside this foundation review.

Future workers may execute only after:

- inspected proposal;
- explicit human approval when required;
- AiGOL-governed execution request derivation;
- authorization evidence;
- replay lineage continuity.

Worker may not self-authorize from a proposal.

## Replay Boundary

Replay records lifecycle events and reconstructs history.

Replay may not:

- approve;
- reject;
- execute;
- change lifecycle truth;
- infer missing approval;
- repair invalid lineage.

## Fail-Closed Boundary

The lifecycle must fail closed on:

- missing prompt lineage;
- missing conversation lineage;
- malformed proposal fields;
- unsupported capability target;
- unknown risk class;
- missing approval;
- invalid actor transition;
- provider authority language;
- worker authority before execution request authorization;
- replay discontinuity;
- expired proposal use.

## Constitutional Invariant

The foundation preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Lifecycle mapping:

```text
LLM proposes = provider contribution remains proposal evidence
AiGOL governs = AiGOL creates, inspects, rejects, expires, and derives governed requests
Worker executes = worker acts only after authorized execution request
Replay records = replay records and reconstructs lifecycle evidence
```

## Boundary Result

```text
PROPOSAL_LIFECYCLE_BOUNDARY_STATUS = PRESERVED
```
