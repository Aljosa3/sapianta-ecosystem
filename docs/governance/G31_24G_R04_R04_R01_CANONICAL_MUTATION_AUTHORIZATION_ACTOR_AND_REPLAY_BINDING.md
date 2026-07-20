# G31-24G-R04-R04-R01 — Canonical Mutation Authorization Actor and Replay Binding

## Verdict

`G31_CANONICAL_MUTATION_AUTHORIZATION_ACTOR_AND_REPLAY_BINDING_OPERATIONAL`

The exact existing R02 `GOVERNED_WORKER_AUTHORIZATION_RECORD_V1` now has a separate evidence-only binding to its proved canonical Governance actor and a standalone, reconstructible, same-session authorization Replay. The record itself and its R02 binding hash are unchanged. No second authorization, authorization consumption, replace request, Worker invocation, command, patch, or mutation occurs.

## Baseline

- Branch: `master`.
- Immutable baseline HEAD: `151c6442662a41b8d2d4c23e23fbfcf714cdf025` (`docs(governance): record replace owner hardening blocker`).
- The required R04 blocker report is tracked and committed.
- Required verdict: `G31_EXISTING_REPLACE_OWNER_HARDENING_BLOCKED`.
- Required next-state blocker: `G31_24G_R04_R04_R01_CANONICAL_MUTATION_AUTHORIZATION_ACTOR_AND_REPLAY_BINDING_REQUIRED`.
- Initial parent dirt was limited to the nine protected paths; all three nested repositories were clean.

Generation 30 and committed G31-02 through the R04 blocker remain immutable accepted baselines.

## Proved constitutional authorization owner

Canonical authorization actor:

`governed_authorization_runtime`

This identity was not inferred from a module name and is not supplied by a caller. The existing public `reconstruct_authorization_replay` contract already returns `who_authorized = "governed_authorization_runtime"`, and `test_valid_authorization_record_created_and_replay_visible` certifies that exact value. Canonical governance reports including G8-99, G13-02, and G14-33 assign authorization ownership to Governance while distinguishing Human Authority, Platform Core coordination, Worker execution, Provider activity, Replay, and interface transport.

The constant `CANONICAL_AUTHORIZATION_ACTOR` now names that pre-existing certified value. The generic Replay output remains byte-for-byte the same string. The V3 `decided_by` value remains the distinct human mutation-decision actor and is recorded separately; it cannot substitute for the authorizer.

## Changed files and scope

- `aigol/authorization/authorization_runtime.py` — versioned existing-record Replay persistence/reconstruction and canonical actor constant: 117 additions, 2 literal-to-constant replacements.
- `aigol/runtime/platform_core_existing_file_governance.py` — G31 actor/Replay binding and public reconstruction: 123 additions.
- `tests/test_g31_24g_r04_r04_r01_authorization_actor_replay_binding.py` — isolated evidence for 17 focused cases.
- This report.

Production additions: exactly 240 across exactly two production files, within the scope gate. No production module, authorization record family, Replay subsystem, router, AiCLI edge, or mutation path was added.

## Versioned contracts

`G31_24G_R04_R04_R01_AUTHORIZATION_BINDING_V1` is an additive branch in the existing authorization Replay owner.

Public Platform Core contracts:

- `bind_g31_mutation_authorization_actor_and_replay` independently reconstructs the accepted R02 authorization and all activation/candidate/decision evidence, validates the unchanged canonical record, resolves the canonical actor without an actor parameter, builds the binding, and persists the existing-record Replay.
- `reconstruct_g31_mutation_authorization_actor_and_replay` reloads all wrappers, reconstructs R02 and every upstream generation again, validates every cross-reference and stop-state flag, and returns the complete public identity projection.

Existing authorization Replay-owner contracts:

- `persist_existing_authorization_binding_replay` accepts only the already-hashed binding from the canonical owner and persists three ordered wrappers.
- `reconstruct_existing_authorization_binding_replay` validates wrapper order/hash, artifact type/version/hash, actor, session, authorization identity/hash/status, R02 binding, and false consumption/execution/mutation state.

The deterministic Replay destination is:

```text
<canonical session root>/G31_MUTATION_AUTHORIZATION_REPLAY_V1
```

Ordered steps:

```text
000_authorization_owner_resolved.json
001_authorization_binding_recorded.json
002_authorization_returned.json
```

Each wrapper is created with `O_CREAT | O_EXCL`, canonical serialization, mode `0600`, flush, and file fsync. Duplicate or concurrent destination claims fail closed. A session scan rejects a repeated binding for the same authorization hash even if another destination is attempted.

The persisted binding hashes:

- canonical authorization actor;
- complete unchanged authorization record and every policy field;
- authorization ID/hash/status/scope/Worker;
- R02 `authorization_binding_hash`;
- session and activation Replay reference/hash;
- V2 candidate ID/artifact hash/Replay hash/provenance-binding hash;
- V3 decision ID/artifact hash/outcome/scope/human actor/Replay hash;
- target path and expected preimage SHA-256;
- deterministic Replay destination;
- false consumption/request/Worker/Provider/command/mutation flags.

The outer actor/Replay capture includes and hashes the final three-wrapper authorization Replay hash, avoiding any self-referential artifact hash.

## Public reconstruction result

Successful reconstruction returns:

```text
canonical_authorization_actor = governed_authorization_runtime
authorization_status = AUTHORIZED
mutation_authorized = true
authorization_actor_bound = true
authorization_replay_recorded = true
authorization_consumed = false
replace_request_created = false
worker_invoked = false
provider_invoked = false
command_executed = false
repository_mutated = false
main_repository_mutated = false
```

It also returns authorization Replay reference/hash; the exact unchanged record and its identity/hash/status/scope/Worker; R02 binding hash; session; activation identity/hash/Replay; V2 candidate identity/hash/Replay/provenance; V3 decision identity/hash/outcome/scope/actor/Replay; target path; and expected preimage.

## No second authorization and compatibility

The additive binder calls only R02 reconstruction, canonical record validation, and existing-record Replay persistence. It never calls `create_authorization_record` or proposal-driven `authorize_worker_request`. The positive focused test replaces `create_authorization_record` with a function that raises and still completes binding/reconstruction successfully.

The exact pre-binding authorization record is deep-compared after binding, including its original `authorization_hash`. R02 construction and `authorization_binding_hash` logic were not edited. `GOVERNED_WORKER_AUTHORIZATION_RECORD_V1`, `create_authorization_record`, and `validate_authorization_record` are unchanged. The generic authorization Replay replaces its literal actor value with the equal certified constant, and all ten generic tests pass. Legacy V1 replacement, V2 candidate, and V3 decision suites pass unchanged.

## Fail-closed and duplicate evidence

Focused evidence proves failure for:

- caller-supplied actor argument;
- substitution of the V3 human actor as authorizer;
- missing/rejected record or changed authorization identity, hash, status, scope, Worker, proposal, or policy;
- changed candidate, decision, activation, repository grounding, target, preimage, or R02 binding;
- prior authorization consumption, request creation, or rollback state;
- downstream stop-state substitution at the public Replay owner before any wrapper is written;
- missing, duplicated, hash-tampered, validly rehashed/reordered, or cross-session Replay;
- duplicate deterministic destination and repeated authorization binding.

Repeated reconstruction returns identical evidence and creates no new wrapper. Duplicate binding leaves the existing three-wrapper Replay unchanged. The exclusive writer closes the concurrent check/write gap present in the older generic persistence helper for this branch.

## Validation

- New actor/Replay binding suite: 17 passed, 0 failed, 0 skipped, 0 deselected in 0.48s.
- Combined new binding, R02 authorization, generic authorization Replay, V1 replacement, V3 decision, and Governance suites: 51 passed, 0 failed, 0 skipped, 0 deselected in 0.73s.
- V2 candidate provenance/reconstruction and AiCLI stop-state suite: 4 passed, 0 failed, 0 skipped, 0 deselected in 370.54s.
- Distinct total: 55 passed, 0 failed, 0 skipped, 0 deselected.
- `py_compile`: passed for both changed production modules and the new focused test.
- Parent and three nested `git diff --check`: passed.

No focused compatibility conflict appeared in shared authorization behavior, so the full suite was not triggered for this evidence-only additive branch. No PTY workflow was run.

Governance remains deterministic, read-only, fail-closed `PARTIALLY_CONFORMANT`: 18 checks passed, 2 pre-existing hook mismatches, 0 critical violations. Report hash: `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea`. Partial conformance is not upgraded.

## Authority and side-effect boundary

- Governance owns canonical authorization through the certified `governed_authorization_runtime` identity.
- The human actor owns only the distinct V3 decision.
- Replay records and reconstructs evidence but cannot authorize.
- AiCLI remains transport/presentation-only and was not changed.
- CODEX and the replace Worker receive no new call edge or authority.
- Provider authority and invocation remain absent.

Only isolated test runtime directories receive the three immutable authorization Replay files. Source fixtures remain byte-identical and temporary Git worktrees remain unchanged. No authorization consumption, replace request, dispatch, patch, command, temporary source file, mutation, rollback, recovery, or mutation completion is reachable from this branch.

## Commit commands, progress, and next state

No commit was created. Exact scoped commands:

```bash
git add aigol/authorization/authorization_runtime.py aigol/runtime/platform_core_existing_file_governance.py tests/test_g31_24g_r04_r04_r01_authorization_actor_replay_binding.py docs/governance/G31_24G_R04_R04_R01_CANONICAL_MUTATION_AUTHORIZATION_ACTOR_AND_REPLAY_BINDING.md
git commit -m "feat(governance): bind mutation authorization actor and replay"
```

These commands exclude every protected path.

Evidence-scoped G31 conversational reachability: 99.85%. Whole-project progress: 97.85%. Physical mutation remains deliberately unreachable.

Exactly one next state:

`G31_24G_R04_R04_EXISTING_REPLACE_OWNER_ATOMICITY_CONSUMPTION_AND_RECOVERY_HARDENING_REQUIRED`

## Bounded next prompt

Resume only `G31_24G_R04_R04_EXISTING_REPLACE_OWNER_ATOMICITY_CONSUMPTION_AND_RECOVERY_HARDENING_REQUIRED` from the committed R01 actor/Replay binding. Preserve the exact R02 record and reconstruct the new canonical actor-bound authorization Replay before accepting any request. Extend only existing replace Worker, validation, Replay, rollback/recovery, and coordinator owners within the previously certified production scope. Add a versioned authenticated request that binds repository/session/grounding, candidate/decision/authorization identities, actor and authorization Replay, target, exact pre/post bytes and hashes, modes, deterministic destinations, and durable one-shot consumption. Use exclusive pre-write journaling, no-follow stable-descriptor checks, clean-worktree/nested-repository/link/mode/drift rejection, same-directory temp write, fsync, atomic replace, post-verification, and deterministic atomic restoration with truthful recovery-required and termination evidence. Test all failure/interruption points only in isolated temporary Git repositories. Preserve V1, do not add AiCLI/live G31 mutation reachability, do not invoke `/home/pisarna/work/sapianta`, and do not commit.
