# G31-24F Post-Acceptance Mutation Authorization Reachability Audit

Date: 2026-07-19
Baseline: master at 6e7c7ed7812ccccf8739f84c740d364e1b99887d
Primary verdict: EXISTING_POST_ACCEPTANCE_MUTATION_AUTHORIZATION_EXISTING_HUMAN_DECISION_REQUIRED

## Scope and conclusion

This is a documentation-only audit. It did not invoke a mutation-authorization owner, repository mutator, Worker, Provider, command runner, generated command, or patch application. It did not write an accepted G31 target path.

G31-24E correctly ends with result_accepted=true, mutation_authorized=false, and main_repository_mutated=false. Content acceptance is not mutation authority.

No production caller connects the G31-24E accepted result to mutation authorization. The historic authorize_filesystem_mutation contract is V1 / CREATE_ONLY and rejects the exact V2 REPLACE_CONTENT manifest before authorization. A separate certified existing-file replacement lifecycle supports one bounded replacement but requires its own candidate-hash-bound human approval before Governance authorization. The G31 execution, task-outcome, disposable-application, disposable-validation, and content-acceptance decisions cannot substitute.

The decisive first unbound boundary is therefore an existing distinct human mutation decision. A later evidence-only binding also needs a bounded projection from reconstructed G31 V2 evidence to the existing single-existing-file candidate. That projection does not grant authority. No current G31 path may apply the accepted source replacement.

## Baseline and status

The required tracked G31-24E report at this baseline contains G31_HUMAN_CONTENT_ACCEPTANCE_TO_EXISTING_ACCEPTANCE_BINDING_OPERATIONAL. Parent status initially and finally contains only the nine protected dirty paths: six modified .runtime/aigol evidence/ledger files and three untracked root markers. No files are staged. Nested repositories sapianta-domain-credit, sapianta_system, and sapianta-domain-trading are clean.

## Owner, caller, Replay, and stop-boundary inventory

| Public owner | Inputs -> output; authority and Replay | Production callers / stop |
| --- | --- | --- |
| generated_content_acceptance_runtime.accept_generated_content | Exact V1 or V2 manifest, matching validations, human content acceptance -> GENERATED_CONTENT_ACCEPTANCE_ARTIFACT_V1; evidence-only, no write. | Historic V1 callers: implementation_epoch.py, first_real_implementation_generation_epoch_runtime.py, and multi_provider_competitive_proposal_runtime.py. |
| accept_generated_content_from_content_acceptance_decision / reconstruct_generated_content_acceptance_from_decision_replay | Exact reconstructed G31 V2 CONTENT_ACCEPTANCE_ONLY/ACCEPTED decision plus G31-23B binding -> existing acceptance artifact and one ordered wrapper. | aigol/cli/aicli.py. It stops explicitly with authorization/mutation false. |
| filesystem_mutation_authorization_runtime.authorize_filesystem_mutation | V1 CREATE_ONLY manifest, V1 validations, acceptance, distinct exact AUTHORIZED human evidence -> FILESYSTEM_MUTATION_AUTHORIZATION_ARTIFACT_V1; read-only, no Replay directory. | Three historic V1 callers only; no G31 caller. _validate_manifest requires V1 and CREATE_ONLY. |
| filesystem_mutation_runtime.apply_filesystem_mutation | V1 create-only manifest + V1 authorization -> filesystem-mutation artifact. | Same historic callers; rejects V2/replacement. |
| create_existing_file_mutation_candidate; create_existing_file_mutation_approval; create_existing_file_mutation_authorization_record | One existing UTF-8 text file, pre-content hash, full replacement -> EXISTING_FILE_MUTATION_CANDIDATE_ARTIFACT_V1; exact confirmation -> approval; candidate -> authorization record. | existing_file_mutation_runtime only; no G31 caller. Required confirmation is confirm existing-file mutation <candidate_id> <candidate_hash>. |
| existing_file_mutation_runtime.execute_existing_file_mutation -> filesystem_replace_worker.execute_filesystem_replace_request | Candidate + approval -> authorization record, bounded request, one replacement, validation, rollback metadata, nine-step Replay. | No AiCLI/Human Interface G31 caller. It continues from its internal authorization record to Worker; no independent safe authorization stop. |
| governed_repository_mutation_runtime.execute_governed_repository_mutation -> repository_mutation_worker_runtime.apply_repository_mutation -> _apply_planned_mutations | Independently approved governed proposal -> patch proposal, mutation, validation command, nine-step Replay. Supports CREATE_OR_REPLACE and REPLACE_CONTENT. | codex_satisfied_outcome_disposable_validation_binding_runtime.py applies only a disposable copy; governed_development_workflow_runtime.py is separate. No G31-24E acceptance input/caller. |
| AiCLI presentation | Renders content decision and accepted content. | Transport/presentation only; no acceptance, authorization, Replay, or mutation authority. |

Other Platform Core authorization-looking owners use their own candidate families and have no G31 caller or compatible acceptance Replay. They are not substitutes.

## Accepted-result to authorization compatibility

Classifications are semantic. V2 raw byte SHA-256 differs from legacy replay_hash(text).

| Required evidence/state | Historic V1 authorization | Existing-file route | Finding |
| --- | --- | --- | --- |
| Session/repository identity | INCOMPATIBLE | AVAILABLE_BUT_NOT_BOUND | V1 has neither; candidate has session only, not repository grounding. |
| Repository root/grounding hash | MISSING | AVAILABLE_BUT_NOT_BOUND | Root is execution input, not candidate/authorization evidence. |
| Acceptance identity, status, hash, version, Replay | INCOMPATIBLE | AVAILABLE_BUT_NOT_BOUND | V1 binds acceptance but rejects V2 manifest; candidate has no acceptance provenance. |
| V2 human decision identity/hash/outcome/scope/actor/Replay | MISSING | MISSING | Neither owner consumes it; CONTENT_ACCEPTANCE_ONLY is not mutation authority. |
| G31-23B prerequisite/readiness/Replay | INCOMPATIBLE | AVAILABLE_BUT_NOT_BOUND | V1 cannot consume V2; projection must reconstruct it. |
| V2 manifest identity/version/Replay | INCOMPATIBLE | AVAILABLE_BUT_NOT_BOUND | V1 requires V1; candidate has no manifest field. |
| REPLACE_CONTENT | INCOMPATIBLE | COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION | Existing-file route performs one full replacement under different vocabulary. |
| One target path | INCOMPATIBLE | COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION | Candidate permits one relative path, not a V2 manifest directly. |
| Exact source/replacement bytes | INCOMPATIBLE | COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION | Verify V2 raw hashes first, then derive legacy text hashes. |
| Authentic preimage/postimage | INCOMPATIBLE | COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION | V2 byte SHA-256 and legacy serialized-text hash differ. |
| Regular file and modes | INCOMPATIBLE | AVAILABLE_BUT_NOT_BOUND | Existing route checks plaintext file but has no mode contract. |
| Content/test/disposable/Worker lineage | INCOMPATIBLE | AVAILABLE_BUT_NOT_BOUND | Present in V2 evidence, not authorization inputs. |
| Scope, path count, forbidden operations | INCOMPATIBLE | COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION | Existing candidate fixes one full replacement and prohibits create/delete/multi-file/Git/Provider. |
| Separate human mutation decision | MISSING | MISSING | V1 needs exact authorization statement; existing-file needs candidate-hash confirmation. Primary blocker. |
| Duplicate/idempotency state | AVAILABLE_BUT_NOT_BOUND | AVAILABLE_BUT_NOT_BOUND | V1 caller supplies keys; existing Replay collision is not G31 consumption registry. |
| Stop flags | INCOMPATIBLE | AVAILABLE_BUT_NOT_BOUND | Current G31 flags remain false and are not inputs. |

## Authorization to mutation compatibility

| Authorization | Mutation owner | Classification | Finding |
| --- | --- | --- | --- |
| FILESYSTEM_MUTATION_AUTHORIZATION_ARTIFACT_V1 | apply_filesystem_mutation | DIRECTLY_COMPATIBLE for V1 only; INCOMPATIBLE for G31 | Both require V1/CREATE_ONLY, matching manifest hashes, and create-only permissions. |
| Existing-file authorization record | Existing replace Worker through execute_existing_file_mutation | DIRECTLY_COMPATIBLE for existing candidate family | Coordinator creates exact record/request then immediately reaches Worker. |
| Governed repository approval / patch proposal | execute_governed_repository_mutation -> repository worker | DIRECTLY_COMPATIBLE for own proposal; AVAILABLE_BUT_NOT_BOUND for G31 | REPLACE_CONTENT supported but requires independent proposal, approval, context, validation, Replay. |
| G31 accepted artifact/wrapper | Any existing mutation owner | INCOMPATIBLE direct input | No public consumer or production call edge accepts it. |

Downstream classification: legacy authorization-to-Worker is operational only inside its separate coordinator; generic repository worker is a different proposal workflow. Neither is currently authorized for G31.

## Authority and current chain

G31-24E accepted result + reconstructed acceptance Replay
-> [unbound: distinct existing human mutation decision]
-> [unbound: reconstructed V2 evidence -> existing-file candidate projection]
-> existing candidate-hash-bound approval
-> existing Governance authorization record, not created
-> existing replace Worker / repository mutation owner, not invoked
-> first filesystem write.

Content acceptance, mutation authorization, and repository mutation are distinct constitutional authorities. AiCLI transports evidence only. CODEX remains WORKER_ROLE / WORKER_AUTHORIZED_TASK_ONLY; Provider authority and invocation are absent.

## V2 compatibility, first write, atomicity, and rollback

Historic authorization and mutation are conclusively V1/CREATE_ONLY: both _validate_manifest functions require IMPLEMENTATION_MANIFEST_ARTIFACT_V1 and CREATE_ONLY. Focused non-create-only tests prove rejection.

Existing-file route supports one full existing UTF-8 replacement, a pre-write content-hash check and post-write hash check, but not V2 manifest parsing, raw byte-hash semantics, acceptance Replay input, mode verification, or multi-file scope. It is reusable only through the bounded projection plus new mandatory approval.

Generic repository worker first source-changing instruction is repository_mutation_worker_runtime._apply_planned_mutations -> target.write_text(item[new_content], encoding=utf-8). Target is resolved root plus target path after proposal/hash, approved-path, relative-path, forbidden-prefix, and containment checks. Source Replay is persisted only after writes return; result/return evidence follows. It is non-atomic, has no rollback, and a multi-file failure can leave earlier files changed.

Existing-file first source-changing instruction is filesystem_replace_worker.execute_filesystem_replace_request -> target.write_text(request[replacement_content], encoding=utf-8). Immediately before it the request is validated/persisted, target resolved/read, plaintext checked, and legacy preimage matched. Post-write hash is checked; later validation and rollback metadata are recorded. It is non-atomic. Interruption or failed post-check can leave a changed file. Rollback is metadata only, separately authorized, and automatic rollback is disabled.

## Proven and absent protections

| Protection | Status |
| --- | --- |
| Decision/acceptance identity, validation lineage, cross-session evidence, Replay reordering/substitution, repeated acceptance consumption | Proven fail-closed by G31-24E fixtures. |
| V1 authorization duplicate lineage | Proven only when caller supplies prior keys; no G31 persisted projection exists. |
| Existing candidate approval, authorization/request, Replay linkage | Proven by existing-file fixtures and nine-step reconstruction. |
| Source drift / TOCTOU | Existing-file checks content immediately before write; no lock, compare-and-swap, dirty-worktree, or repository-grounding check. Generic worker snapshots but does not require expected preimage before write. |
| Absolute paths/traversal/root escape | Proven relative-path and resolved-root containment. |
| Symlink/hard-link/mode/case normalization | V2 evidence prohibits symlink and requires unchanged mode, but existing owners do not consume it. Existing-file resolves before testing is_symlink, so internal symlink is not reliably rejected; hard-link, mode, case-normalization protections absent. |
| Protected paths/nested repos | Generic worker blocks .git/, .github/governance/, runtime/finalization_evidence/; governed workflow also blocks docs/governance/. Existing-file candidate has no equivalent protected-prefix, nested-repo, or dirty-worktree enforcement. |
| Operation substitution | Existing-file is one full replacement and forbids create/delete/multi-file. Generic worker permits approved operations but does not bind V2 preimage/mode. |
| Duplicate mutation/completion/termination/rollback consumption | Replay destination collision fails closed; no global G31 authorization/mutation registry or prior completion/termination/rollback binding. |
| Partial write/rollback failure | No atomic staging, automatic rollback, rollback execution, or transaction. |

## External dependencies and presentation

Evidence-only V1 authorization and a future candidate/approval projection require no network, credentials, MCP, Provider, live CODEX Worker, shell, Git, or source write. Actual mutation requires filesystem write access and target root. Generic governed repository mutation additionally needs its allowlisted validation executable after a write. No route needs Provider access.

AiCLI currently presents the accepted stop state only. G31-24E isolated fixture covers AiCLI/Human decision presentation and confirms no authorization/mutation call. No presentation behavior changed.

## Validation and Governance

| Check | Result |
| --- | --- |
| G31-24E, acceptance V1/V2, V1 authorization/mutation, repository worker, governed repository, existing-file and first-mutating-worker fixtures | 61 passed, 61 collected; 0 skipped, 0 failed, 0 deselected; isolated temporary repositories. |
| Targeted py_compile of inspected acceptance, authorization, mutation, existing-file, Worker, and AiCLI modules | pass |
| tests/test_governance_conformance.py | 5 passed in 0.03s |
| Governance engine | PARTIALLY_CONFORMANT: 18 passed, 2 known hook mismatches, 0 critical; deterministic/read-only/fail-closed; hash 0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea. |
| Parent and all nested git diff --check | pass |
| Full suite / long PTY workflow | skipped: committed G31-24D/E evidence sufficient and focused evidence did not conflict. |

Known governance limitations remain visible: expected parent pre-commit hook absent; sapianta_system hook lacks promotion_gate_v02 and check_layer_freeze. These are non-critical hook findings.

## Minimal future transition, not implemented

Smallest safe G31-24G is evidence-only preparation binding:

1. Reconstruct G31-24E acceptance Replay before calling existing create_existing_file_mutation_candidate; only after exact candidate-hash confirmation call existing create_existing_file_mutation_approval.
2. Permit one V2 replacement entry only; verify raw preimage/postimage bytes, unchanged regular-file mode, G31-23B lineage, decisions, acceptance, and Replays before deriving legacy text hashes.
3. Bind acceptance identity/hash, session/repository grounding, path, both hash representations, and approval in ordered new Replay. Reuse existing candidate/approval families.
4. Do not create authorization record, Worker request, filesystem/repository mutation, command, Git action, or source write.
5. Maximum production surface: two production changes, one new binding module and existing AiCLI route/presentation; one production addition, one focused test module, and one report; no schema/new canonical family.
6. Stop state: candidate/approval Replay visible, result_accepted=true, mutation_authorized=false, main_repository_mutated=false. A later generation must assess whether non-atomic writing and missing mode/repository protections require owner extension before mutation.

### Bounded next prompt

Generation 31-24G — Post-Acceptance Existing-File Candidate and Distinct Human Mutation-Decision Binding

Repository: /home/pisarna/work/sapianta. Baseline must contain committed G31-24F.

Implement only an evidence-only binding from one reconstructed accepted G31-24E V2 REPLACE_CONTENT result to the existing EXISTING_FILE_MUTATION_CANDIDATE_ARTIFACT_V1 and, after one new exact candidate-hash-bound existing human confirmation, the existing EXISTING_FILE_MUTATION_APPROVAL_ARTIFACT_V1. Reconstruct and verify G31-24E acceptance Replay, V2 human decision Replay, and G31-23B evidence before projection. Permit one regular UTF-8 target with unchanged mode; verify V2 raw preimage/postimage SHA-256 before deriving legacy text hashes. Bind repository/session grounding, acceptance, decision, manifest, validation, target, hashes, confirmation in ordered new Replay evidence. Reuse public existing candidate/approval owners.

Do not create a Governance authorization record, authorized Worker request, filesystem/repository mutation artifact, source write, patch application, Worker/Provider invocation, command execution, Git action, schema, or new canonical family. Do not modify mutation owners/protected paths. Limit production changes to one new binding module and existing AiCLI route/presentation; add one focused test module and one report. Prove success, rejection/missing confirmation, identity/hash/Replay/path/mode/duplicate failures, no downstream calls, unchanged source in isolated fixtures. End result_accepted=true, mutation_authorized=false, main_repository_mutated=false. Do not commit.

Evidence-scoped progress remains G31 conversational reachability 99.5% and whole project 97.5%; this audit resolves post-acceptance reachability, not source-mutation reachability.

Next state (exactly one):

G31_24G_POST_ACCEPTANCE_EXISTING_FILE_CANDIDATE_AND_DISTINCT_HUMAN_MUTATION_DECISION_BINDING_REQUIRED

