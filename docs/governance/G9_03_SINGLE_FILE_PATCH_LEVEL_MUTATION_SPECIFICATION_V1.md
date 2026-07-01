# G9-03 Single File Patch-Level Mutation Specification V1

Status: single-file patch-level mutation specified.

Final verdict: SINGLE_FILE_PATCH_LEVEL_MUTATION_SPECIFIED

## 1. Executive Summary

G9-03 specifies the smallest safe governed patch-level editing capability for AiGOL.

Generation 8 certified full replacement of exactly one existing plaintext file inside an allowlisted non-authority workspace. G9-02 identified patch-level editing as the highest-priority remaining capability for reducing hybrid Codex/Terminal dependence.

The certified next step is:

```text
Apply exactly one deterministic context-bound patch to exactly one existing plaintext file
inside an allowlisted non-authority workspace
only when the approved pre-hash and patch context both match.
```

This specification does not authorize multi-file patching, arbitrary search/replace, Git operations, deployment, package installation, provider invocation, authority artifact mutation, or autonomous retry.

The patch-level mutation capability must remain:

- governed;
- hash-bound;
- context-bound;
- replay-visible;
- rollback-aware;
- validation-aware;
- single-file only;
- plaintext only;
- fail-closed on conflict;
- coordinated by Platform Core;
- authorized by Governance;
- executed only by Worker Platform;
- rendered by ACLI Next only as a thin entrypoint.

## 2. Allowed Mutation Scope

Allowed operation:

```text
APPLY_SINGLE_CONTEXT_BOUND_PATCH_TO_EXISTING_TEXT_FILE
```

Scope requirements:

| Field | Requirement |
| --- | --- |
| File count | Exactly one existing file. |
| Patch count | Exactly one patch operation. |
| Patch shape | One contiguous context-bound replacement block. |
| File type | Plaintext UTF-8 only. |
| Target path | Relative path under an allowlisted non-authority workspace. |
| Existing file requirement | Target must exist and be a regular file before execution. |
| Mutation style | Replace one exact old text block with one exact new text block. |
| Precondition | Current file hash must match approved pre-mutation hash. |
| Context condition | Approved old text block must occur exactly once in current file. |
| Postcondition | Resulting file hash must match approved post-mutation hash. |
| Size bound | File, old block, new block, and resulting file must remain within replay-inspectable limits. |
| Encoding | UTF-8 text without null bytes. |
| Side effects | No side effects outside the one target file. |
| Git behavior | No Git status, staging, commit, branch, tag, push, checkout, or reset. |
| Deployment behavior | No deployment or server mutation. |

Recommended initial workspace remains:

```text
runtime/governed_mutation_workspace/
```

Mutation of governance documents, constitutional artifacts, runtime source files, tests, release manifests, `.github/governance/`, `.git/`, or any authority-bearing path remains prohibited until separately specified and certified.

## 3. Patch Request Model

The patch request is not authority. It is human or interface input that Platform Core routes into certified owners.

Required request fields:

| Field | Requirement |
| --- | --- |
| `session_id` | Existing PGSP-governed session id. |
| `turn_id` | Current governed turn id. |
| `requested_operation` | Must equal `APPLY_SINGLE_CONTEXT_BOUND_PATCH_TO_EXISTING_TEXT_FILE`. |
| `target_relative_path` | Relative path inside allowlisted workspace. |
| `old_text` | Exact plaintext block expected in current file. |
| `new_text` | Exact plaintext replacement block. |
| `operator_intent` | Human-readable reason for the patch. |
| `validation_request` | Optional validation preference; not execution authorization. |

The request must not include:

- multiple target files;
- multiple hunks;
- regular expressions;
- wildcard paths;
- glob paths;
- arbitrary search/replace rules;
- shell commands;
- Git commands;
- deployment instructions;
- provider invocation instructions;
- implied approval.

ACLI Next may capture the request and render summaries. It must not translate the patch into authority, authorize execution, apply the patch, reconstruct replay, or choose Workers independently.

## 4. Deterministic Patch Format

The canonical patch candidate must use a deterministic structured format, not an ad hoc prose diff.

Required candidate fields:

| Field | Requirement |
| --- | --- |
| `candidate_id` | Deterministic or replay-visible candidate identifier. |
| `candidate_hash` | Hash over the normalized candidate payload. |
| `operation` | `APPLY_SINGLE_CONTEXT_BOUND_PATCH_TO_EXISTING_TEXT_FILE`. |
| `target_relative_path` | Canonical relative path. |
| `target_workspace` | Allowlisted non-authority workspace id. |
| `pre_hash` | Hash of the target file observed during candidate creation. |
| `old_text` | Exact UTF-8 text block to replace. |
| `old_text_hash` | Hash of `old_text`. |
| `new_text` | Exact UTF-8 replacement text. |
| `new_text_hash` | Hash of `new_text`. |
| `occurrence_policy` | Must equal `exactly_once`. |
| `expected_post_hash` | Hash of the full target file after applying the patch. |
| `rollback_payload_hash` | Hash of rollback metadata. |
| `validation_plan_ref` | Reference to proposed validation evidence or plan. |
| `prohibited_operations` | Explicit declaration of excluded operations. |

Patch application semantics:

1. Read current file content.
2. Verify current file hash equals `pre_hash`.
3. Verify `old_text` occurs exactly once.
4. Replace that exact occurrence with `new_text`.
5. Verify resulting full file hash equals `expected_post_hash`.
6. Emit execution evidence for Replay.

No line-number-only patch is allowed in the first version. Line numbers may be included as advisory display metadata, but they must not be the execution authority.

## 5. Preconditions

Required preconditions:

1. PGSP session exists.
2. Human request is replay-visible.
3. OCS creates a single-file patch candidate.
4. Candidate hash is computed over deterministic normalized payload.
5. Candidate contains exactly one target path.
6. Candidate contains exactly one old text block and one new text block.
7. Candidate declares `occurrence_policy` as `exactly_once`.
8. Candidate includes approved `pre_hash`, `old_text_hash`, `new_text_hash`, and `expected_post_hash`.
9. Candidate includes rollback metadata hash.
10. Candidate includes validation interaction requirements.
11. Human approval is explicit and bound to `candidate_id` and `candidate_hash`.
12. Governance authorizes the candidate after validating approval and policy.
13. Replay root is available and append-only.
14. Worker Platform validates authorization before execution.
15. Target path is inside the allowlisted non-authority workspace.
16. Target exists and is a regular plaintext UTF-8 file.
17. Target file size is within configured bounds.
18. Current target hash matches `pre_hash`.
19. `old_text` occurs exactly once in current target content.

If any precondition fails, the operation must fail closed before mutation.

## 6. Conflict Detection

Conflict detection is mandatory and must occur before writing.

Conflict classes:

| Conflict | Detection Rule | Required Behavior |
| --- | --- | --- |
| Missing target | Target path does not exist. | Fail closed; no mutation. |
| Path escape | Canonical path is outside allowlisted workspace. | Fail closed; no mutation. |
| Prohibited path | Target is authority-bearing or prohibited. | Fail closed; no mutation. |
| Non-regular file | Target is symlink, directory, device, or special file. | Fail closed; no mutation. |
| Non-text file | Target is non-UTF-8 or contains null bytes. | Fail closed; no mutation. |
| Pre-hash mismatch | Current hash differs from approved `pre_hash`. | Fail closed; stale candidate. |
| Old block missing | `old_text` does not occur. | Fail closed; context mismatch. |
| Old block ambiguous | `old_text` occurs more than once. | Fail closed; ambiguous patch. |
| Post-hash mismatch | Resulting content hash differs from approved `expected_post_hash`. | Fail closed; restore pre-write content if any write occurred. |
| Replay failure | Required replay evidence cannot be persisted. | Fail closed; no completion claim. |
| Authorization mismatch | Governance authorization does not bind candidate. | Fail closed; no mutation. |

The Worker must not attempt fuzzy matching, approximate matching, whitespace-tolerant matching, regular expression matching, or automatic conflict resolution.

## 7. Pre-Hash And Post-Hash Verification

Hash verification is mandatory.

Required hashes:

- current file `pre_hash`;
- `old_text_hash`;
- `new_text_hash`;
- expected full-file `post_hash`;
- rollback metadata hash;
- candidate hash;
- approval hash;
- Governance authorization hash;
- Worker execution artifact hash;
- Replay evidence hash or reference.

Hash binding requirements:

- human approval must bind to candidate id and candidate hash;
- Governance authorization must bind to approval hash and candidate hash;
- Worker execution must bind to Governance authorization hash;
- Replay evidence must bind to Worker execution artifact and resulting post-hash;
- rollback metadata must bind to the pre-mutation content hash and post-mutation content hash.

Completion must not be claimed unless the post-hash matches the approved expected post-hash and Replay evidence exists.

## 8. Governance Approval

Human approval must be explicit and hash-bound.

Required approval phrase:

```text
confirm single-file patch mutation <candidate_id> <candidate_hash>
```

Approval artifact must include:

- approval id;
- session id;
- turn id;
- candidate id;
- candidate hash;
- target relative path;
- operation type;
- expected pre-hash;
- expected post-hash;
- approving human identity;
- approval timestamp;
- explicit statement that approval does not authorize Git, deployment, provider invocation, multi-file mutation, additional Workers, or arbitrary search/replace.

Governance remains the authority. Human approval is admissible evidence for Governance but does not by itself authorize execution.

Governance authorization must include:

- authorization id;
- authorization hash;
- session id;
- turn id;
- candidate id;
- candidate hash;
- approval id;
- approval hash;
- operation type;
- target workspace;
- target relative path;
- pre-hash;
- expected post-hash;
- authorized Worker id or Worker family;
- single-use policy;
- expiration or bounded validity;
- replay reference;
- prohibited operation declaration.

Governance must not execute the patch, construct the patch payload, persist Replay evidence directly, or certify success before Worker and Replay evidence exist.

## 9. OCS Candidate Ownership

OCS owns patch candidate formation and proposal.

OCS responsibilities:

- convert the governed request into one deterministic patch candidate;
- verify that the request is single-file and single-patch;
- compute or reference observed pre-hash;
- compute old text, new text, and expected post-hash evidence;
- declare risks and validation recommendations;
- declare rollback metadata requirements;
- reject prohibited requests before Governance authorization;
- produce UHCL-compatible proposal content through the certified communication path.

OCS must not:

- authorize execution;
- execute the patch;
- persist Replay evidence as the Replay owner;
- call Workers directly outside Platform Core coordination;
- infer human approval from request prose;
- expand one patch request into multi-file mutation.

## 10. Worker Platform Execution

Worker Platform owns patch application execution only.

The first patch Worker should be modeled as:

```text
GOVERNED_SINGLE_FILE_CONTEXT_PATCH_WORKER_V1
```

Worker responsibilities:

- validate request schema;
- validate Governance authorization hash;
- validate candidate hash binding;
- validate target workspace and canonical path containment;
- validate target existence and regular-file status;
- validate UTF-8 plaintext constraints;
- compute current file hash;
- verify current hash equals approved `pre_hash`;
- verify `old_text` occurs exactly once;
- construct resulting content deterministically;
- verify resulting content hash equals approved `expected_post_hash`;
- write resulting content exactly once;
- compute final file hash;
- emit Worker execution artifact;
- fail closed on mismatch.

Worker must not:

- choose target paths;
- create patch candidates;
- authorize itself;
- request human approval;
- call Governance as an authority substitute;
- reconstruct Replay;
- mutate more than one file;
- perform arbitrary search/replace;
- use regular expressions;
- run shell commands;
- run Git commands;
- invoke providers;
- deploy;
- retry with altered context.

## 11. Replay Evidence

Replay remains the evidence and reconstruction system.

Required replay-visible evidence:

- session id;
- turn id;
- human patch request reference;
- OCS candidate id and hash;
- target relative path;
- pre-hash;
- old text hash;
- new text hash;
- expected post-hash;
- human approval id and hash;
- Governance authorization id and hash;
- Worker execution request id;
- Worker execution result id;
- final post-hash;
- rollback metadata reference and hash;
- validation plan reference;
- validation result reference if validation is executed in the same workflow;
- conflict record if operation fails closed;
- completion summary.

Replay must support reconstruction of:

- why the patch was proposed;
- what exact old block was replaced;
- what exact new block was inserted;
- which authorization allowed execution;
- what hash-bound state existed before and after;
- whether validation was required, deferred, passed, or failed;
- whether rollback metadata exists.

Replay evidence must remain append-only. Missing Replay evidence blocks completion claims.

## 12. Rollback Interaction

Rollback metadata is mandatory before patch execution.

Rollback metadata must include:

- rollback id;
- rollback metadata hash;
- target relative path;
- pre-mutation content hash;
- post-mutation content hash;
- old text hash;
- new text hash;
- inverse patch payload or full pre-mutation content reference;
- candidate id;
- Governance authorization id;
- Worker execution id after execution;
- replay references.

Rollback execution is not authorized by this specification.

This specification only requires rollback-ready evidence. Actual rollback execution remains a separate governed mutation capability and must receive its own Governance authorization.

## 13. Validation Interaction

Validation remains governed by certified validation execution capabilities.

The patch candidate must include one of:

| Validation State | Meaning |
| --- | --- |
| `validation_required_before_completion` | A governed validation command must pass before final completion. |
| `validation_recommended` | Validation is recommended but not required by the candidate. |
| `validation_deferred` | Human and Governance accept no immediate validation for this patch class. |
| `validation_not_applicable` | No relevant validation exists for the target. |

If validation is required:

- OCS proposes the validation plan;
- Governance authorizes validation;
- Worker Platform executes validation;
- Replay records validation evidence;
- completion must remain blocked until validation result evidence exists.

Patch execution must not directly run validation unless routed through the certified governed validation execution path.

## 14. Fail-Closed Behavior

Fail-closed triggers:

- missing PGSP session;
- missing replay root;
- missing OCS candidate;
- candidate contains multiple files;
- candidate contains multiple patches;
- candidate uses regex, glob, wildcard, or fuzzy matching;
- missing candidate hash;
- missing explicit human approval;
- missing Governance authorization;
- approval/candidate/authorization hash mismatch;
- target path escape;
- prohibited path;
- target missing;
- target not regular plaintext UTF-8;
- file size exceeds configured bounds;
- old text missing;
- old text occurs more than once;
- pre-hash mismatch;
- post-hash mismatch;
- rollback metadata missing;
- replay persistence failure;
- validation-required evidence missing;
- Worker execution artifact missing.

Fail-closed output must include:

- error class;
- failed checkpoint;
- session id and turn id if available;
- candidate id if available;
- target path if safe to disclose;
- replay reference if available;
- explicit statement that no mutation occurred or that mutation was not completed;
- recommended next safe action.

## 15. Prohibited Operations

This specification does not permit:

- multi-file patching;
- multiple hunks;
- arbitrary search/replace;
- regular expression replacement;
- wildcard or glob path matching;
- fuzzy matching;
- automatic conflict resolution;
- binary file mutation;
- symlink mutation;
- file creation;
- file deletion;
- file rename or move;
- directory mutation;
- Git status, add, commit, branch, merge, rebase, push, pull, checkout, reset, or tag;
- deployment;
- package installation;
- provider invocation;
- mutation of governance, constitutional, release, or authority-bearing artifacts;
- autonomous retry;
- additional Worker dispatch outside certified Platform Core coordination.

## 16. Acceptance Criteria

Single-file patch-level mutation is acceptable when:

1. A deterministic single-file patch candidate format exists.
2. Only one existing plaintext file in an allowlisted non-authority workspace can be targeted.
3. Only one exact old text block can be replaced by one exact new text block.
4. Old text must occur exactly once.
5. Pre-hash verification is mandatory.
6. Post-hash verification is mandatory.
7. Human approval is explicit and hash-bound.
8. Governance authorization is required and single-use.
9. Worker Platform performs patch application only.
10. Replay evidence reconstructs request, candidate, approval, authorization, execution, hashes, rollback metadata, and completion.
11. Rollback metadata is generated before execution.
12. Validation interaction is recorded and enforced when required.
13. Missing evidence or conflict fails closed.
14. ACLI Next remains capture/render only.
15. No Git, deployment, provider invocation, multi-file mutation, or arbitrary search/replace occurs.

## 17. Implementation Readiness

This capability is ready for implementation after:

- OCS patch candidate schema is bound;
- Governance authorization policy is extended for single-file patch mutation;
- Worker Platform patch Worker contract is defined;
- Replay evidence schema is extended for patch artifacts;
- rollback metadata is bound to patch payloads;
- validation interaction status is integrated;
- targeted tests are defined for success, pre-hash mismatch, missing old block, ambiguous old block, prohibited path, missing authorization, replay failure, and post-hash mismatch.

## 18. Final Determination

Single-file patch-level mutation is specified as the next governed runtime capability for reducing hybrid Codex/Terminal dependence.

The capability remains a narrow extension of certified existing-file mutation and preserves Platform Core ownership boundaries.

Final verdict: SINGLE_FILE_PATCH_LEVEL_MUTATION_SPECIFIED

## 19. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: SINGLE_FILE_PATCH_LEVEL_MUTATION_SPECIFIED
