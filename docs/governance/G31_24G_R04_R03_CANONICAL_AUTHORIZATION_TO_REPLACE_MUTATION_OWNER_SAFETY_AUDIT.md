# G31-24G-R04-R03 — Canonical Authorization to Replace Mutation Owner Safety Audit

## Verdict

`EXISTING_REPLACE_MUTATION_OWNER_SAFETY_HARDENING_REQUIRED`

Plain-language conclusion: the G31 authorization and accepted replacement evidence contain enough information to design a bounded request projection, but the existing physical replacement owner is not safe for direct connection to the source repository. It uses a non-atomic `Path.write_text`, does not consume the G31 authorization binding, lacks single-consumption and several repository/link/mode controls, cannot automatically restore an existing file, and can report `repository_mutated=false` after a partial or completed write followed by failure. Direct G31 binding is prohibited until the existing owner is hardened and tested.

## Baseline

- Branch: `master`.
- Immutable baseline HEAD: `b92138403a990e4c8fb7a6f8652fd9260dc9e9b4` (`feat(governance): bind approved mutation decision to authorization`).
- Required R02 report is tracked and committed.
- Required committed verdict is present: `G31_R02_EXACT_APPROVED_DECISION_TO_CANONICAL_MUTATION_AUTHORIZATION_BINDING_OPERATIONAL`.
- Parent status initially contained only the nine declared protected paths.
- Nested repositories `sapianta-domain-credit`, `sapianta_system`, and `sapianta-domain-trading` were clean.

Generation 30 and committed G31-02 through G31-24G-R04-R02 remain immutable accepted baselines.

## Contracts, owners, callers, and effects

| File and public symbol | Owner and canonical contract | Production caller/callee | Side effects and downstream boundary |
|---|---|---|---|
| `aigol/runtime/platform_core_existing_file_governance.py::authorize_g31_approved_existing_file_mutation` | Platform Core mutation authorization; reconstructs activation, V2 candidate, V3 decision, then creates `GOVERNED_WORKER_AUTHORIZATION_RECORD_V1` | No production caller located; focused R02 tests call it | Evidence-only; stops with `mutation_authorized=true`, all execution/mutation flags false |
| same file, `reconstruct_g31_existing_file_mutation_authorization_binding` | Read-only G31 authorization reconstruction | Focused R02 tests | Reconstructs exact authorization subject; no write |
| `aigol/authorization/authorization_record.py::validate_authorization_record` | Canonical generic authorization validator | G31 owner and replace request builder | Hash/status/Worker/scope/false-authority validation; no write |
| `aigol/workers/filesystem_replace_worker.py::create_authorized_replace_request` | Worker Platform request constructor, V1 | Legacy existing-file and multi-file coordinators | Creates in-memory request; requires canonical authorization record but not the G31 authorization binding |
| same file, `validate_authorized_replace_request` | V1 request validator | Request creation tests and Worker execution | Validates request/hash; authorization linkage is optional and is not supplied by `execute_filesystem_replace_request` |
| same file, `execute_filesystem_replace_request` | Physical replacement Worker | `execute_existing_file_mutation`; `_execute_one_operation` in multi-file runtime | Persists request Replay, reads/hash-checks target, then changes source bytes at `Path.write_text` |
| same file, `reconstruct_filesystem_replace_worker_replay` | Worker-side two-step Replay reconstructor | Both legacy coordinators | Requires ordered request/result wrappers; read-only |
| `aigol/runtime/existing_file_mutation_runtime.py::execute_existing_file_mutation` | Legacy V1 Platform Core coordinator | No production caller located | Accepts only V1 candidate/approval, creates a new authorization, creates request, invokes Worker, validates, records rollback metadata and completion |
| `aigol/runtime/multi_file_mutation_runtime.py::execute_governed_multi_file_mutation` and `_execute_one_operation` | Legacy multi-file coordinator | No additional production caller located | Reuses replace Worker for V1 per-file replace operations; not a G31 single-file projection |
| `aigol/runtime/platform_core_existing_file_validation.py` pre/post functions | Validation owner | Legacy existing-file coordinator | Reads pre/post content; post-validation occurs after source change |
| `aigol/runtime/platform_core_existing_file_rollback.py::existing_file_rollback_metadata_artifact` | Rollback metadata owner | Legacy coordinator after successful post-validation | Records hashes and explicitly disables automatic rollback; retains no original bytes |
| `aigol/runtime/platform_core_existing_file_replay.py` persistence/reconstruction | Nine-step legacy mutation Replay owner | Legacy coordinator | Writes evidence before and after mutation; reconstructs only a complete successful sequence |
| `aigol/runtime/governed_rollback_runtime.py` and `aigol/workers/filesystem_rollback_worker.py` | Separate governed rollback lifecycle | Explicit later rollback calls only | Existing-file rollback candidate creation fails when complete original content is absent; not automatic recovery |
| `aigol/runtime/human_decision_runtime.py` mutation renderers | Canonical presentation for V3 decision | Human decision lifecycle | Presents decision only; no G31 authorization, replace request, mutation result, recovery, or completion presentation exists |

No AiCLI call edge to the R02 authorization adapter or replace Worker was found. The current G31 production-visible conversational chain remains stopped before request construction.

## Exact current call chains

G31 chain:

```text
reconstructed V2 candidate
-> reconstructed V3 APPROVED decision
-> authorize_g31_approved_existing_file_mutation
-> create_authorization_record / validate_authorization_record
-> reconstruct_g31_existing_file_mutation_authorization_binding
-> STOP: no production caller constructs a replace request
```

Independent legacy V1 chain:

```text
execute_existing_file_mutation
-> validate V1 candidate and V1 approval
-> resolve legacy allowlisted workspace and target
-> pre_existing_file_mutation_artifact
-> create_existing_file_mutation_authorization_record (new V1 authorization)
-> create_authorized_replace_request
-> persist outer Replay steps 0..4
-> execute_filesystem_replace_request
-> persist Worker request Replay
-> read and hash-check target
-> Path.write_text                         FIRST SOURCE CHANGE
-> Worker post-write read/hash check
-> Worker result Replay
-> outer post validation
-> rollback metadata only
-> outer result/validation/rollback/completion Replay
```

The legacy coordinator cannot be used as a direct G31 bridge: it requires `EXISTING_FILE_MUTATION_CANDIDATE_ARTIFACT_V1`, a separate V1 approval, and the legacy `runtime/governed_mutation_workspace` allowlist; it also creates a new authorization rather than consuming the exact R02 authorization.

## Authorization-to-request compatibility

Classification is semantic and includes validation/hash behavior, not name similarity.

| Material field | Classification | Finding |
|---|---|---|
| Authorization ID/hash/status | `DIRECTLY_COMPATIBLE` | Present in the canonical record and accepted by request construction |
| Authorization scope | `DIRECTLY_COMPATIBLE` | Exact `FILESYSTEM_REPLACE_EXISTING_TEXT_FILE` |
| Authorization actor | `MISSING` | Generic authorization record and G31 authorization subject contain no authorizing actor field; V3 `decided_by` remains upstream |
| Authorization session | `AVAILABLE_BUT_NOT_BOUND` | G31 authorization evidence contains session; V1 request has no session field |
| Authorization Replay | `MISSING` | The binding is reconstructable and hash-bound, but there is no authorization Replay reference/consumer contract in the Worker request |
| Authorization binding hash | `AVAILABLE_BUT_NOT_BOUND` | Exists in the R02 capture; request accepts only record ID/hash and does not validate the binding |
| V3 decision ID/hash/outcome | `AVAILABLE_BUT_NOT_BOUND` | Present in G31 authorization evidence; absent from request semantics |
| V3 decision scope/actor/Replay | `AVAILABLE_BUT_NOT_BOUND` | Available through the reconstructed decision; not represented or validated by the request |
| V2 candidate ID | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Authorization `proposal_id` equals candidate ID; request `proposal_reference` could carry it but currently has no semantic validator |
| V2 candidate hash/Replay/provenance binding | `AVAILABLE_BUT_NOT_BOUND` | Present in authorization evidence; absent from request validation |
| Repository identity | `AVAILABLE_BUT_NOT_BOUND` | Candidate provenance has it; authorization/request do not bind `base_dir` to it |
| Repository root | `AVAILABLE_BUT_NOT_BOUND` | Candidate provenance has it; Worker receives an independent caller-supplied `base_dir` |
| Repository grounding | `AVAILABLE_BUT_NOT_BOUND` | G31 authorization binds grounding hash; request/Worker do not consume it |
| Target path | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | `target_path` can map to `file_path`, but exact authorization-to-request equality is not currently enforced |
| Operation `REPLACE_CONTENT` | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | Requires explicit mapping to `REPLACE_EXISTING_TEXT_FILE`; V1 validator does not accept the G31 vocabulary |
| Raw preimage SHA-256 | `INCOMPATIBLE` | Worker `expected_content_hash` uses canonical `replay_hash(text)`, not `sha256:` UTF-8 byte digest |
| Raw postimage SHA-256 | `INCOMPATIBLE` | Worker has no raw byte-SHA field or verifier |
| Source content hash | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | V2 provenance contains `source_content_hash` with the Worker's `replay_hash(text)` semantics, but R02 authorization evidence omits it |
| Replacement content hash | `COMPATIBLE_THROUGH_EXISTING_PUBLIC_PROJECTION` | V2 provenance uses the Worker's hash semantics; exact bytes must still be recovered from reconstructed manifest evidence |
| Replacement bytes | `AVAILABLE_BUT_NOT_BOUND` | Present in the accepted manifest, absent from V2 candidate and authorization outputs; no current public request projection reconstructs them |
| Source/replacement mode | `INCOMPATIBLE` | V2 binds equal modes; request, Worker, result, validation, and completion do not carry or verify them |
| Disposable validation evidence | `AVAILABLE_BUT_NOT_BOUND` | Bound into V2 provenance; absent from request/Worker contract |
| Worker identity | `DIRECTLY_COMPATIBLE` | Exact replace Worker ID matches |
| Worker role (`WORKER_ROLE`) | `AVAILABLE_BUT_NOT_BOUND` | Activation lineage proves the role; request knows only Worker ID |
| Authorization-consumption identity | `MISSING` | No consumption artifact, global lookup, or one-shot token exists |
| Request Replay destination | `AVAILABLE_BUT_NOT_BOUND` | Caller supplies arbitrary `replay_reference`/`replay_dir`; not constrained to G31 session or authorization |
| Mutation/result destination | `AVAILABLE_BUT_NOT_BOUND` | Caller chooses Replay directory; not bound to repository/session/authorization evidence |
| Rollback destination | `MISSING` | Existing-file metadata has no executable restore content; separate rollback cannot reconstruct it |
| Completion destination | `AVAILABLE_BUT_NOT_BOUND` | Legacy outer Replay supplies it, but that lifecycle is V1-only and creates a fresh authorization |
| Termination destination | `MISSING` | No termination artifact or call edge exists in this lifecycle |

Field projection is therefore possible only after a versioned request/binding contract is added, but projection alone would not make the write safe.

## Safety-control matrix

| Control | Classification | Current evidence |
|---|---|---|
| G31 authorization Replay/session substitution through authorization reconstruction | `PROVED_BY_CODE_AND_TEST` | R02 independently reconstructs activation, candidate, decision, and authorization binding |
| Preservation of that G31 evidence at Worker consumption | `INCOMPATIBLE_WITH_CURRENT_OWNER` | Worker consumes only a V1 request carrying authorization ID/hash |
| Candidate/decision/authorization linkage before authorization | `PROVED_BY_CODE_AND_TEST` | R02 focused suite covers exact linkage/tampering |
| Candidate/decision/authorization linkage at request/write | `INCOMPATIBLE_WITH_CURRENT_OWNER` | `proposal_reference` is only required to be any JSON object |
| Duplicate authorization consumption | `MISSING` | Same authorization can construct multiple requests/replay destinations |
| Duplicate mutation | `MISSING` | Replay collision is directory-local; same evidence may be retried elsewhere, and no global consumption identity exists |
| Source drift checked immediately before write | `PROVED_BY_CODE_AND_TEST` | Worker rereads and compares `replay_hash`; legacy stale-hash test passes |
| TOCTOU between final check and write | `MISSING` | Separate path resolve/stat/read/open operations; no stable descriptor/inode check |
| Repository-root and lexical target containment | `PROVED_BY_CODE_AND_TEST` | Resolve/relative containment and traversal rejection exist; traversal test passes |
| Absolute-path rejection | `CODE_ONLY_NOT_TESTED` | `_validate_relative_path` rejects absolute paths; focused replace tests do not exercise it |
| External symlink escape | `CODE_ONLY_NOT_TESTED` | Resolution outside base fails containment; no focused test |
| Internal symlink rejection | `INCOMPATIBLE_WITH_CURRENT_OWNER` | Code resolves first and checks `is_symlink()` on the resolved referent, so an internal symlink is accepted |
| Symlink substitution after validation | `MISSING` | Later `write_text` follows the current path object without no-follow/openat protection |
| Hard-link substitution or multi-link target | `MISSING` | No inode/link-count check; replacement can alter another hard-link name |
| Non-regular target | `CODE_ONLY_NOT_TESTED` | `exists/is_file` check exists, but no direct directory/device focused test |
| Dirty target worktree | `MISSING` | No Git/status/snapshot cleanliness check |
| Nested repository boundary | `MISSING` | No nested `.git` or repository-ownership check |
| Source/replacement mode validation | `INCOMPATIBLE_WITH_CURRENT_OWNER` | No `stat`, expected-mode field, post-mode check, or explicit mode restoration |
| Atomic temporary-file write | `MISSING` | No same-directory temporary file; direct truncating write |
| Same-filesystem atomic replace | `MISSING` | No `os.replace`/rename operation |
| File/directory flush or fsync | `MISSING` | No flush/fsync durability boundary |
| Partial-write failure safety | `MISSING` | Direct `write_text` can leave empty/partial/replaced bytes on exception/interruption |
| Truthful mutation status after post-write failure | `INCOMPATIBLE_WITH_CURRENT_OWNER` | Failure artifacts report Worker not invoked/repository not mutated even when the write may already have occurred |
| Post-write postimage verification | `CODE_ONLY_NOT_TESTED` | Worker and outer validator reread/hash; success is tested, injected post-write failure is not |
| Automatic rollback | `MISSING` | Explicitly disabled; only metadata is created after successful validation |
| Executable rollback for existing replacement | `INCOMPATIBLE_WITH_CURRENT_OWNER` | Original bytes are absent; focused rollback test proves candidate creation fails closed |
| Rollback failure evidence | `MISSING` | No automatic rollback attempt or failure branch exists |
| Worker Replay ordering/hash | `PROVED_BY_CODE_AND_TEST` | Two-step successful Replay reconstruction is exercised transitively |
| Outer result/validation/rollback/completion ordering | `PROVED_BY_CODE_AND_TEST` | Successful nine-step Replay reconstruction is tested |
| Failure Replay completeness | `INCOMPATIBLE_WITH_CURRENT_OWNER` | Failure may persist only Worker failure wrappers and outer step 8; nine-step reconstruction cannot represent the partial sequence |
| Termination Replay ordering | `MISSING` | No termination stage exists |

## Exact first source-changing boundary

- Public entry point: `aigol.workers.filesystem_replace_worker.execute_filesystem_replace_request`.
- Request: `AUTHORIZED_REPLACE_EXISTING_TEXT_FILE_REQUEST_V1` created by `create_authorized_replace_request`.
- Target calculation: `_resolve_existing_target` computes `(base_dir / relative_path).resolve()`, checks containment, existence, and regular-file status, then returns the resolved path.
- Checks immediately before write: read target as UTF-8, reject NUL content, compute `replay_hash(old_content)`, and compare it with `request["expected_content_hash"]`.
- Exact first source-changing instruction: `aigol/workers/filesystem_replace_worker.py:176`, `target.write_text(request["replacement_content"], encoding="utf-8")`.
- Evidence before write: outer candidate/approval/authorization/request/pre-state wrappers and Worker request wrapper are persisted.
- Evidence after write: the Worker rereads and hashes content, then writes its result wrapper; the outer coordinator later writes Worker result, post-validation, rollback metadata, and completion wrappers.

The write is non-atomic. `Path.write_text` opens/truncates the existing inode and writes directly. There is no temporary file, exclusive creation, stable descriptor, inode/link check, fsync, directory fsync, atomic replace, backup, or automatic restoration. A write exception, process interruption, post-write read failure, postimage mismatch, or evidence-write failure can leave the repository changed with incomplete or falsely negative failure evidence.

Post-write validation is real but occurs after the unsafe change. Rollback metadata is created only after validation succeeds and contains hashes, not original bytes. The separate governed rollback runtime explicitly cannot build an existing-file rollback from this Replay because complete original content is missing.

## Authority assessment

- The V3 human decision is a distinct human-owned `MUTATION_AUTHORIZATION / EXISTING_FILE_REPLACE_ONLY / APPROVED` decision and is not the canonical authorization record.
- Platform Core owns canonical mutation authorization; it remains distinct from Worker-owned physical mutation.
- AiCLI has no current authorization-to-request or mutation call edge and remains non-authoritative.
- CODEX remains `WORKER_ROLE`; neither the G31 authorization adapter nor the replace Worker grants Provider role or authority.
- Provider authority and invocation remain false/absent.
- The canonical record names only the replace Worker and exact replace scope, but the current request does not bind the complete G31 evidence or caller-supplied `base_dir`; therefore it does not yet prove that only the exact authorized repository target can consume the authorization.

## Focused validation

Established isolated temporary fixtures only:

- R02 exact authorization binding: 9 passed.
- Legacy V1 existing-file mutation: 7 passed.
- Governed rollback, including unavailable existing-file restore content: 6 passed.
- Multi-file composition/duplicate transaction target: 5 passed.
- Generic canonical authorization contract and Replay: 10 passed.
- Governance tests: 5 passed.
- Total: 42 passed, 0 failed, 0 skipped, 0 deselected in 0.41s.
- `py_compile`: passed for ten inspected authorization, mutation, validation, Replay, rollback, Worker, and coordinator modules.
- Full suite and live PTY workflow: intentionally not run.

Governance engine result: deterministic, read-only, fail-closed `PARTIALLY_CONFORMANT`; 18 checks passed, 2 pre-existing hook mismatches, 0 critical violations. Report hash: `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea`. Partial conformance is not upgraded.

## Smallest safe next transition

Do not connect G31 authorization to request construction yet. The smallest safe next generation is a versioned hardening of the existing replace Worker and its existing Platform Core validation/Replay owners, entirely in isolated temporary repositories. It must:

1. consume and reconstruct the exact G31 authorization binding at a versioned request boundary, including repository root, target, candidate/decision/authorization identities, raw byte hashes, content hashes, modes, and a one-shot consumption identity;
2. bind `base_dir`, Replay destination, request, and target to the reconstructed repository/session evidence;
3. reject dirty target worktrees, nested-repository targets, internal/external symlinks, hard-linked or non-regular targets, path/inode substitution, mode drift, and duplicate consumption;
4. use a same-directory exclusive temporary file, exact bytes, explicit mode, file fsync, atomic same-filesystem replace, directory fsync, and post-replace byte/mode/inode verification;
5. retain the original bytes/mode before replacement and perform/test atomic restoration when any post-write phase fails, with truthful partial-change and rollback-failure evidence;
6. version result, recovery, completion, and termination Replay so every interruption point is reconstructable and no failure may claim `repository_mutated=false` without proving restoration;
7. keep AiCLI non-authoritative and stop short of connecting the hardened owner to the real G31 source repository.

Maximum intended production surface: the existing `filesystem_replace_worker.py`, `platform_core_existing_file_validation.py`, `platform_core_existing_file_replay.py`, and `existing_file_mutation_runtime.py`; use the existing authorization, candidate, decision, rollback, and presentation families rather than parallel owners. Focused tests must inject failures before temp creation, during temp write, before/after atomic replace, during verification, during rollback, and during Replay persistence, and must cover links, modes, dirt, nesting, duplicate consumption, interruption recovery, and exact unchanged/fully-restored bytes.

## Repository preservation and commit commands

This audit changed no production behavior, tests, schemas, evidence, authorization state, or source target content. It created only this report. Existing tests mutated only established temporary fixtures. No G31 request was constructed, no G31 authorization was consumed, and no source-repository mutation owner was invoked.

No commit was created. Documentation-only commands:

```bash
git add docs/governance/G31_24G_R04_R03_CANONICAL_AUTHORIZATION_TO_REPLACE_MUTATION_OWNER_SAFETY_AUDIT.md
git commit -m "docs(governance): audit replace mutation owner safety"
```

Evidence-scoped G31 conversational reachability remains 99.8%. Whole-project progress remains 97.8%. Safety-qualified mutation reachability is deliberately lower than field reachability until hardening is certified.

Exactly one next state:

`G31_24G_R04_R04_EXISTING_REPLACE_OWNER_ATOMICITY_CONSUMPTION_AND_RECOVERY_HARDENING_REQUIRED`

## Bounded next implementation prompt

Implement only `G31_24G_R04_R04_EXISTING_REPLACE_OWNER_ATOMICITY_CONSUMPTION_AND_RECOVERY_HARDENING_REQUIRED`. Start from the committed R03 audit and stop if its verdict is absent. Extend the existing replace Worker and existing Platform Core validation/Replay/coordinator owners; do not create a parallel mutator, approval, authorization, Replay, rollback, completion, presentation, or command system. In isolated temporary Git repositories, add a versioned exact-G31 request validator that reconstructs the R02 authorization binding and binds repository root, session, target, candidate/decision/authorization identities, raw byte/content hashes, modes, Replay destination, and one-shot consumption identity. Reject dirt, nested repositories, path escape, all symlinks, hard links, non-regular targets, inode/mode/content drift, replay substitution, and duplicate consumption. Replace direct `Path.write_text` with same-directory exclusive temporary-file creation, exact-byte write, explicit mode, flush/fsync, stable precondition recheck, atomic same-filesystem replacement, directory fsync, and post-write byte/mode verification. Preserve original bytes/mode and implement deterministic atomic restoration for every post-replace failure; record truthful mutation/rollback/recovery/completion/termination evidence for all injected interruption points. Add focused tests for every control and failure phase. Do not invoke the hardened owner against `/home/pisarna/work/sapianta`, do not add an AiCLI mutation call edge, do not run a live G31 workflow, and do not commit.
