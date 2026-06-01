# FIRST_REAL_WORKFLOW_DISCOVERY_EXPLANATION_ANALYSIS_V1

## Explanation Requirement

For every real workflow, AiGOL must be evaluated on whether it can explain:

- what occurred;
- why it occurred;
- which proposal was accepted;
- which authorization scope was used;
- which worker executed;
- what evidence supports the result.

## Explanation Readiness Matrix

| Workflow | Explanation Readiness | Justification | Missing Evidence To Improve |
| --- | --- | --- | --- |
| Governed milestone marker | HIGH | Replay shows proposal, authorization, worker, file path, content hash. | Human rationale for milestone timing. |
| Governance artifact skeleton | HIGH | File creation is bounded and replay-verifiable. | Artifact semantic intent summary. |
| ADR skeleton | HIGH | Proposal and authorization explain file creation. | Decision context references. |
| Usage log entry file | HIGH | Replay can explain creation and content hash. | Link to source operations summarized. |
| Acceptance JSON stub | HIGH | New file creation is explainable. | JSON schema validation evidence. |
| Replay certification JSON stub | HIGH | New file creation is explainable. | Certification source replay references. |
| Repository note/TODO marker | HIGH | Marker creation is bounded and auditable. | Human reason for note priority. |
| Release checklist file | HIGH | Checklist file creation is replayable. | Checklist source milestone references. |
| Replay verify by operation id | HIGH | Verification reports reconstructability and hashes. | Aggregate verification history. |
| Operation status summary | HIGH | Replay operation gives status and event summary. | Operation ledger for recent-history context. |
| Append governance artifact | MEDIUM | Future replay could explain target and diff. | Before/after diff, patch hash, approval reason. |
| Update certification JSON | MEDIUM | Future structured update could explain changed fields. | Schema validation and field-level diff. |
| Run tests and capture result | MEDIUM | Future worker could explain command and result. | stdout/stderr hashes, environment metadata. |
| Inspect git status | MEDIUM | Future worker could explain repository state. | File-level status snapshot and diff summary. |
| Create GitHub issue | MEDIUM | Future worker could explain issue payload. | API response, issue URL, repository identity. |
| Weekly usage summary | HIGH | Replay data can support high-quality summary. | Operation ledger and fail-closed replay persistence. |

## Current High-Quality Explanation Shape

For current supported workflows, AiGOL can say:

```text
The operator requested a bounded filesystem create-file operation.
The provider proposal identified a create-file action.
Governed authorization created an authorization record with FILESYSTEM_CREATE_FILE scope.
The filesystem worker received only an authorized worker request.
The worker created the target file.
Replay contains provider, authorization, and worker evidence.
Replay verification passed.
```

## Trust Explanation

Current trust explanations are strong when:

- operation replay reconstructs successfully;
- `aigol replay verify` returns `VERIFY_PASSED`;
- worker result contains a content hash;
- authorization id and scope are visible;
- proposal id is visible.

Trust explanations are weaker when:

- the operation failed before full replay persistence;
- the artifact content requires semantic validation;
- the result depends on external provider reliability;
- the workflow requires modifying existing files.

## Explanation Gap

The most important explanation gap is not natural-language generation.

The gap is evidence aggregation:

```text
operation ledger
success/fail-closed history
source operation references
semantic validation evidence
```

Better explanations require better evidence indexing, not more prose.
