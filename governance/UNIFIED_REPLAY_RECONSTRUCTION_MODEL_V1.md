# UNIFIED_REPLAY_RECONSTRUCTION_MODEL_V1

## Reconstruction Artifact

Future runtime should create a read-only report artifact:

```text
UNIFIED_REPLAY_RECONSTRUCTION_REPORT_V1
```

This report is an inspection artifact only.

It must not create, approve, mutate, dispatch, invoke, execute, complete, repair, or self-apply any runtime artifact.

## Required Report Fields

```text
artifact_type
reconstruction_report_version
reconstruction_id
requested_view
canonical_chain_id
compatibility_lineage_id
root_reference
created_at
created_by
chain_status
reconstruction_status
chain_segments
artifact_index
replay_event_index
missing_evidence
corruption_findings
authority_boundary_findings
stage_order_findings
hash_findings
operator_summary
replay_reference
replay_visible
artifact_hash
```

## Requested Views

Allowed requested views:

```text
LATEST_CHAIN
CHAIN_BY_ID
EXECUTION_CHAIN
LEARNING_CHAIN
BRIDGE_CHAIN
FULL_CHAIN_LINEAGE
CORRUPTION_REPORT
MISSING_EVIDENCE_REPORT
AUTHORITY_BOUNDARY_REPORT
```

## Reconstruction Status

Allowed status values:

```text
VALID
INCOMPLETE
CORRUPT
AMBIGUOUS
FAILED_CLOSED
```

Status meanings:

| Status | Meaning |
| --- | --- |
| `VALID` | Required evidence exists, hashes match, references match, and boundaries hold |
| `INCOMPLETE` | Required evidence is missing but no corruption is proven |
| `CORRUPT` | Evidence exists but hashes, references, chain ids, or stage order fail |
| `AMBIGUOUS` | Multiple candidate chains match without deterministic tie-break evidence |
| `FAILED_CLOSED` | Reconstruction cannot safely continue |

## Segment Model

Each segment must record:

```text
segment_id
segment_type
stage_name
artifact_type
artifact_reference
artifact_hash
replay_reference
replay_hash
parent_reference
parent_hash
canonical_chain_id
status
authority_flags
boundary_result
```

Segment types:

```text
CONVERSATION
SOURCE_ROUTING
PROPOSAL
APPROVAL
EXECUTION_REQUEST
READY_FOR_DISPATCH
WORKER_ASSIGNMENT
DISPATCH
INVOCATION
EXECUTION
COMPLETION
RESULT
EVALUATION
IMPROVEMENT_PROPOSAL
IMPROVEMENT_REVIEW
IMPROVEMENT_APPROVAL
IMPLEMENTATION_PLAN
BRIDGE
WORKER_EVIDENCE
REPLAY_EVIDENCE
```

## Merge Rules

Replay fragments may merge only when at least one deterministic relationship exists:

- same `canonical_chain_id`;
- direct parent reference and hash;
- explicit replay reference;
- explicit bridge link;
- explicit result-to-evaluation reference;
- explicit implementation plan to bridge reference;
- certified supersession or child-chain relationship.

Timestamp adjacency is not enough to merge chains.

## Compatibility Lineage

When older artifacts do not carry `canonical_chain_id`, reconstruction may create:

```text
compatibility_lineage_id
```

This id is a report-local reconstruction aid.

It is not a canonical chain id and must not be written back to runtime artifacts.

Compatibility lineage is valid only when references and hashes prove continuity.

## Required Ordering

Execution ordering:

```text
PROPOSAL
APPROVAL
EXECUTION_REQUEST
READY_FOR_DISPATCH
WORKER_ASSIGNMENT
DISPATCH
INVOCATION
EXECUTION
COMPLETION
RESULT
```

Learning ordering:

```text
RESULT
EVALUATION
IMPROVEMENT_PROPOSAL
IMPROVEMENT_REVIEW
IMPROVEMENT_APPROVAL
IMPLEMENTATION_PLAN
BRIDGE
EXECUTION_REQUEST
```

Conversation ordering:

```text
HUMAN_PROMPT
SOURCE_ROUTING
CONVERSATION_RESPONSE
OPTIONAL_PROPOSAL
```

## Mandatory Hash Checks

Each artifact must pass:

- artifact hash check;
- replay wrapper hash check;
- parent hash check;
- payload hash check where present;
- plan text/scope/constraint hash checks where present;
- decision reason hash checks where present;
- worker output hash checks where present.

## Mandatory Authority Checks

Unified reconstruction must verify absence of unauthorized:

- provider authority;
- worker authority;
- replay authority;
- automatic approval;
- automatic authorization;
- governance mutation;
- replay mutation;
- code mutation;
- self-approval;
- self-authorization;
- self-implementation;
- hidden dispatch;
- hidden invocation;
- hidden execution.

## Operator Output Model

Human-readable output should include:

- chain summary;
- current terminal stage;
- latest action;
- pending authorization;
- failed-closed events;
- missing evidence;
- corruption findings;
- authority boundary status;
- replay references;
- recommended next safe action.

The output must not recommend execution when authorization evidence is missing.
