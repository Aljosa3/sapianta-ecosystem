# AIGOL Worker Execution Evidence V1

Status: worker execution evidence campaign.

Purpose: define the smallest empirical proof that the AiGOL execution path can operate end-to-end through a governance-approved worker invocation using existing architecture.

This artifact is evidence methodology and readiness analysis only.

It does not redesign AiGOL.

It does not introduce new architecture.

It does not authorize uncontrolled worker execution.

It does not authorize provider execution.

It does not authorize governance mutation.

It does not authorize replay mutation.

## Core Question

```text
Can AiGOL perform its first governance-approved worker invocation and produce replay evidence using the existing architecture?
```

Governing assumption:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

## Reviewed Baseline

This artifact reviews and uses:

- Human authority model;
- ACLI architecture;
- Universal Intake;
- workflow selection;
- approval boundaries;
- ERR architecture;
- worker architectural decisions;
- replay requirements;
- constitutional invariants;
- provider-program lessons.

Relevant existing worker surfaces:

```text
ERR-backed worker selection exists for file_write -> mock_filesystem_worker.
Worker registration and assignment runtimes exist.
Worker dispatch runtime exists.
Worker invocation runtime exists.
Governed worker execution runtime exists.
Filesystem worker execution runtime exists.
Authorization record and replay reconstruction exist.
Fail-closed worker tests exist.
Replay reconstruction tests exist.
```

Relevant boundary decisions:

```text
Human authority approves.
AiGOL governs authorization and admissibility.
ERR resolves passive resource metadata only.
Worker executes only after governance approval.
Replay records ordered evidence.
Provider output cannot authorize execution.
Worker cannot self-authorize.
Replay cannot authorize execution.
```

## Recommended First Worker

Recommended first worker:

```text
FILE_WRITE_WORKER
```

Concrete existing implementation:

```text
aigol.workers.filesystem_worker
FILESYSTEM_CREATE_WORKER
FILESYSTEM_CREATE_FILE
```

ERR-aligned worker identity:

```text
mock_filesystem_worker
resource_type = EXECUTION_WORKER
capability = file_write
```

## Candidate Comparison

| Candidate | Safety | Existing AiGOL implementation evidence | Replay evidence readiness | Recommendation |
| --- | --- | --- | --- | --- |
| `ECHO_WORKER` | Highest conceptual safety. | No canonical AiGOL worker runtime found for this candidate. | Not sufficient without new worker implementation. | Do not select for first evidence campaign. |
| `CALCULATOR_WORKER` | High conceptual safety. | No canonical AiGOL worker runtime found for this candidate. | Not sufficient without new worker implementation. | Do not select for first evidence campaign. |
| `FILE_WRITE_WORKER` | Medium operational risk, bounded by create-only temp workspace. | Existing filesystem worker, authorization, fail-closed, and replay reconstruction tests exist. | Strongest existing replay path. | Select with strict create-only constraints. |

Selection rationale:

`FILE_WRITE_WORKER` is the only candidate with an existing concrete worker execution surface, authorization model, fail-closed behavior, and replay reconstruction path. It should be used only for a harmless proof artifact in an isolated temporary governed workspace.

The first empirical proof should create one deterministic evidence file:

```text
worker_execution_evidence.txt
```

with deterministic content:

```text
AIGOL_WORKER_EXECUTION_EVIDENCE_V1
```

The campaign must not write outside the governed workspace.

## Smallest Possible Worker Evidence Campaign

Campaign name:

```text
AIGOL_WORKER_EXECUTION_EVIDENCE_V1
```

Smallest successful proof:

```text
Human request enters ACLI.
ACLI records intake and routes to worker execution evidence workflow.
Human approval is explicit.
ERR resolves file_write to mock_filesystem_worker.
Governance creates a bounded worker authorization.
FILE_WRITE_WORKER creates one file in an isolated workspace.
Execution result is recorded.
Replay reconstructs the full chain.
```

Permitted operation:

```text
CREATE_ONLY
single relative filename
single deterministic content string
single invocation
no overwrite
no retry
no fallback
no provider activation
no governance mutation
no replay mutation
```

Recommended human prompt:

```text
Create the first governed worker execution evidence file.
```

Required clarification if prompt is entered through normal ACLI:

```text
Confirm target worker evidence campaign.
Confirm create-only file operation.
Confirm filename worker_execution_evidence.txt.
Confirm content AIGOL_WORKER_EXECUTION_EVIDENCE_V1.
Confirm isolated governed workspace.
Confirm human approval for one worker invocation.
```

## Complete Execution Path

Required path:

```text
Human
-> ACLI
-> Intake
-> Workflow Selection
-> Approval
-> ERR Resolution
-> Worker Invocation
-> Execution Result
-> Replay
```

Expanded path:

```text
1. Human submits natural-language request.
2. ACLI records the prompt and preserves human authority.
3. Universal Intake records passive intake and routing visibility.
4. Workflow selection identifies bounded worker execution evidence campaign.
5. Clarification confirms exact file path, content, workspace, and one-time scope.
6. Human approval is recorded for worker execution evidence only.
7. ERR resolves capability file_write to an active EXECUTION_WORKER.
8. AiGOL creates or validates governed worker authorization.
9. AiGOL creates authorized worker request.
10. Worker invocation occurs once.
11. FILE_WRITE_WORKER executes create-only operation.
12. Execution result is recorded.
13. Replay reconstruction verifies intake, approval, ERR selection, authorization, request, worker execution, result, and boundary flags.
```

## Required Artifacts

Minimum campaign artifacts:

```text
AIGOL_WORKER_EXECUTION_EVIDENCE_CAMPAIGN_MANIFEST_V1
HUMAN_REQUEST_ARTIFACT_V1
ACLI_INTAKE_EVIDENCE_V1
UNIVERSAL_INTAKE_ARTIFACT_V1
WORKFLOW_SELECTION_EVIDENCE_V1
CLARIFICATION_EVIDENCE_V1
HUMAN_APPROVAL_ARTIFACT_V1
ERR_WORKER_SELECTION_EVIDENCE_V0
GOVERNED_WORKER_AUTHORIZATION_RECORD_V1
AUTHORIZED_WORKER_REQUEST_V1
FILESYSTEM_WORKER_EXECUTION_EVIDENCE_V1
WORKER_EXECUTION_RESULT_ARTIFACT_V1
WORKER_EXECUTION_REPLAY_RECONSTRUCTION_V1
AIGOL_WORKER_EXECUTION_EVIDENCE_CERTIFICATION_V1
```

Existing concrete artifacts may satisfy these roles where names differ, provided the replay evidence proves equivalent semantics.

## Required Replay Evidence

Replay must include:

- human request text hash;
- ACLI turn/session reference;
- intake classification;
- clarification questions and human confirmations;
- workflow target;
- human approval reference;
- approval hash;
- ERR selected worker id;
- ERR required capability;
- authorization record;
- authorization hash;
- authorized worker request;
- request hash;
- worker id;
- authorized scope;
- operation;
- file path;
- content hash;
- execution status;
- execution result;
- replay hash;
- artifact hashes;
- boundary flags.

Required boundary flags:

```text
provider_invoked = false
provider_can_authorize = false
proposal_can_authorize = false
cognition_can_authorize = false
worker_can_self_authorize = false
dispatch_performed = bounded_single_worker_path_only
worker_invoked = true only after authorization
execution_performed = true only for authorized create-only operation
governance_modified = false
replay_modified = false
orchestration_performed = false
multi_step_execution = false
automatic_retry = false
fallback = false
workspace_escape = false
secret_replayed = false
```

## Evidence Collection Structure

Campaign manifest:

```text
artifact_type = AIGOL_WORKER_EXECUTION_EVIDENCE_CAMPAIGN_MANIFEST_V1
campaign_id
campaign_name
selected_worker
selected_capability
governed_workspace
target_file
target_content_hash
created_at
governing_artifacts
expected_path
expected_artifacts
expected_replay_evidence
artifact_hash
```

Per-stage evidence:

```text
artifact_type = AIGOL_WORKER_EXECUTION_STAGE_EVIDENCE_V1
campaign_id
stage_name
stage_status
source_artifact_reference
source_artifact_hash
replay_reference
replay_hash
boundary_flags
failure_reason
artifact_hash
```

Final evidence packet:

```text
artifact_type = AIGOL_WORKER_EXECUTION_EVIDENCE_PACKET_V1
campaign_id
selected_worker
execution_path_completed
human_authority_preserved
approval_verified
err_resolution_verified
authorization_verified
worker_invoked
execution_completed
result_verified
replay_reconstructable
boundary_flags_verified
stage_evidence_hashes
known_gaps
artifact_hash
```

## Certification Structure

Certification artifact:

```text
artifact_type = AIGOL_WORKER_EXECUTION_EVIDENCE_CERTIFICATION_V1
campaign_id
selected_worker
certified_at
execution_path_status
human_authority_preserved
acli_intake_verified
workflow_selection_verified
approval_verified
err_resolution_verified
worker_authorization_verified
worker_invocation_verified
execution_result_verified
replay_reconstruction_verified
fail_closed_controls_verified
architecture_blockers
implementation_blockers
operational_blockers
certification_status
certification_rationale
evidence_packet_hash
artifact_hash
```

Allowed certification statuses:

```text
WORKER_EXECUTION_READY
WORKER_EXECUTION_GAPS_FOUND
WORKER_EXECUTION_FAILED_CLOSED
```

## Success Criteria

The campaign succeeds only if:

```text
Human request is recorded.
ACLI intake is replay-visible.
Workflow selection is replay-visible.
Human approval is explicit and hash-linked.
ERR resolves file_write to the selected worker.
Authorization scope is FILESYSTEM_CREATE_FILE or equivalent create-only scope.
Authorized request contains one relative filename only.
Worker writes exactly one file in the governed workspace.
File content hash matches expected content.
Worker execution result is recorded.
Replay reconstruction succeeds.
Provider invocation remains false.
Worker self-authorization remains false.
Governance mutation remains false.
Replay mutation remains false.
No retry or fallback occurs.
No workspace escape occurs.
```

Successful final verdict:

```text
WORKER_EXECUTION_READY
```

Meaning:

The existing architecture is sufficient for the first worker attachment evidence campaign, and empirical replay evidence confirms the path.

## Failure Criteria

The campaign fails closed if:

- human approval is missing;
- ACLI or intake evidence is missing;
- workflow selection is missing or ambiguous;
- ERR cannot resolve an active `EXECUTION_WORKER` for `file_write`;
- selected worker does not match authorization;
- authorization scope is missing or excessive;
- request path is absolute or contains traversal;
- target file already exists and overwrite would be required;
- worker writes more than one file;
- worker writes outside the governed workspace;
- provider is invoked;
- worker self-authorizes;
- replay evidence is missing or hash-invalid;
- governance is mutated;
- replay is mutated;
- execution retries automatically;
- fallback worker is used;
- result cannot be reconstructed.

Failed final verdict:

```text
WORKER_EXECUTION_GAPS_FOUND
```

or, when unsafe behavior occurred:

```text
WORKER_EXECUTION_FAILED_CLOSED
```

## Blocker Analysis

### Architecture Blockers

Current assessment:

```text
ARCHITECTURE_BLOCKERS = NONE_IDENTIFIED
```

Reason:

The repository already contains architecture for human authority, intake, workflow selection, approval, ERR worker resolution, worker authorization, invocation, execution, and replay reconstruction. ERR remains passive, and worker execution remains separated from provider cognition and governance authority.

### Implementation Blockers

Current assessment:

```text
IMPLEMENTATION_BLOCKERS = NONE_FOR_FILE_WRITE_WORKER_CAMPAIGN
```

Reason:

`FILE_WRITE_WORKER` has existing concrete implementation, create-only request validation, authorization validation, execution, fail-closed behavior, and replay reconstruction. `ECHO_WORKER` and `CALCULATOR_WORKER` would require new implementation and are therefore not selected.

Implementation gaps for non-selected workers:

```text
ECHO_WORKER = NOT_CANONICALLY_IMPLEMENTED_AS_AIGOL_WORKER
CALCULATOR_WORKER = NOT_CANONICALLY_IMPLEMENTED_AS_AIGOL_WORKER
```

### Operational Blockers

Current assessment:

```text
OPERATIONAL_BLOCKERS = CAMPAIGN_EXECUTION_REQUIRED
```

Operational prerequisites:

- create isolated governed workspace;
- choose unused target filename;
- ensure replay directories are empty;
- record human approval;
- run the bounded worker once;
- reconstruct replay;
- produce certification artifact.

These are not architecture blockers.

## Architecture Gaps, Implementation Gaps, Operational Gaps

Architecture gaps:

```text
NONE_IDENTIFIED_FOR_FIRST_FILE_WRITE_WORKER_ATTACHMENT
```

Implementation gaps:

```text
NONE_IDENTIFIED_FOR_FILE_WRITE_WORKER
ECHO_WORKER_AND_CALCULATOR_WORKER_NOT_SELECTED_BECAUSE_IMPLEMENTATION_EVIDENCE_IS_INSUFFICIENT
```

Operational gaps:

```text
FIRST_CAMPAIGN_EVIDENCE_NOT_YET_COLLECTED
FULL_ACLI_TO_WORKER_PROOF_REQUIRES_ACTUAL_RUN
CERTIFICATION_ARTIFACT_NOT_YET_INSTANTIATED
```

## Risk Analysis

Primary risk:

```text
FILESYSTEM_MUTATION_RISK
```

Mitigation:

Use an isolated governed workspace, one single relative filename, create-only semantics, no overwrite, no path traversal, and replay reconstruction.

Secondary risks:

- assuming worker execution readiness from assignment readiness only;
- bypassing human approval;
- treating provider proposal as authorization;
- confusing ERR lookup with dispatch or execution;
- losing replay lineage between approval, request, worker, and result;
- accidental workspace escape;
- replay artifact collision from a previous run;
- overclaiming that file-write proof certifies all worker families.

Residual risk:

```text
LOW_TO_MEDIUM
```

Reason:

The worker is deliberately state-changing, but the operation is highly bounded, local, deterministic, and already covered by fail-closed validation patterns.

## Evidence Methodology

Execution methodology:

1. Run the campaign in an empty isolated governed workspace.
2. Enter the human request through ACLI or an ACLI-equivalent governed operator path.
3. Record intake, routing, and clarification evidence.
4. Obtain explicit human approval for one create-only worker invocation.
5. Resolve `file_write` through ERR to `mock_filesystem_worker` or equivalent filesystem worker metadata.
6. Create governed authorization record.
7. Create authorized worker request.
8. Invoke `FILE_WRITE_WORKER` once.
9. Record worker result.
10. Reconstruct replay.
11. Produce evidence packet.
12. Produce certification artifact.

Minimum empirical proof:

```text
target_file_exists = true
target_file_content_hash = expected_content_hash
worker_execution_status = FILESYSTEM_WORKER_EXECUTED
replay_reconstruction_status = PASS
boundary_flags_verified = true
```

## Sufficiency Determination

Question:

```text
Is the existing architecture sufficient for the first worker attachment?
```

Determination:

```text
YES
```

Reason:

The existing architecture already separates human authority, AiGOL governance, ERR resource lookup, worker authorization, worker execution, and replay reconstruction. No new architecture is required for a bounded first worker execution evidence campaign using the existing file-write worker path.

Scope of determination:

```text
Sufficient for first bounded FILE_WRITE_WORKER evidence campaign.
Not a certification of unrestricted worker execution.
Not a certification of arbitrary filesystem mutation.
Not a certification of ECHO_WORKER or CALCULATOR_WORKER.
Not a certification of provider-to-worker autonomy.
```

## Final Verdict

```text
WORKER_EXECUTION_READY
```

Rationale:

No architecture blockers are identified for the first bounded worker attachment. The existing implementation surface is sufficient for a create-only `FILE_WRITE_WORKER` evidence campaign. Operational evidence still needs to be collected by executing the campaign and producing the certification artifact.

Protected conclusion:

```text
WORKER_EXECUTION_READY means ready to collect first empirical worker execution evidence.
It does not mean full worker ecosystem readiness.
It does not authorize uncontrolled execution.
It does not bypass human approval, ERR boundaries, replay requirements, or constitutional invariants.
```
