# G31-24G-R04-R04 — Existing Replace Owner Atomicity, Consumption, and Recovery Hardening

## Verdict

`G31_EXISTING_REPLACE_OWNER_HARDENING_BLOCKED`

No partial hardening was implemented. The mandatory scope gate found that the accepted R02 authorization cannot supply two required authenticated inputs: a canonical mutation-authorization actor and a canonical mutation-authorization Replay identity. R04 expressly forbids supplemental provenance claims. Atomic-write or consumption work performed without those inputs would create a partially hardened but unauthenticated write path, which this generation prohibits.

## Baseline

- Branch: `master`.
- Immutable baseline HEAD: `40b890e1c1e2f24e6288820cd5068e2d9b44e217` (`docs(governance): audit replace mutation owner safety`).
- Required R03 audit is tracked and committed.
- Required R03 verdict is present: `EXISTING_REPLACE_MUTATION_OWNER_SAFETY_HARDENING_REQUIRED`.
- Initial parent status contained only the nine declared protected paths.
- Nested repositories `sapianta-domain-credit`, `sapianta_system`, and `sapianta-domain-trading` were clean.

Generation 30 and committed G31-02 through G31-24G-R04-R03 remain immutable accepted baselines.

## Deterministic scope blocker

### 1. The accepted R02 authorization has no canonical authorizer

`authorize_g31_approved_existing_file_mutation` calls `create_authorization_record` directly. `GOVERNED_WORKER_AUTHORIZATION_RECORD_V1` contains authorization ID, proposal ID, Worker ID, scope, timestamp, status, hash, and false authority/execution flags. It has no `authorized_by`, authorization actor identity, or authority-owner identity.

The R02 authorization subject contains the V3 mutation-decision ID/hash/outcome, but not the V3 `decided_by` field. Even if the decision artifact is independently reconstructed, its human actor owns the distinct mutation decision; that actor is not the canonical mutation authorizer. Relabeling the human decision actor as the authorization actor would collapse two constitutionally separate authorities.

No caller-supplied actor may repair this gap because R04 requires exact reconstructed canonical evidence and forbids supplemental plain provenance claims.

### 2. The accepted R02 authorization has no canonical Replay identity

The R02 capture has `authorization_binding_hash` and upstream activation/candidate/decision Replay references. It has no authorization Replay reference, authorization Replay hash derived from persisted authorization wrappers, or public authorization Replay reconstructor. `replay_visible=true` on the generic record is a policy flag, not a Replay identity or proof of persistence.

`aigol.authorization.authorization_runtime.authorize_worker_request` owns a separate two-step generic authorization Replay, but R02 does not call it. That runtime creates a fresh authorization from a proposal and Worker target. It cannot reconstruct or wrap the already accepted R02 authorization without a new versioned boundary. Calling it now would create a second authorization generation rather than consume the exact R02 authorization.

The R04 request therefore cannot truthfully bind the mandated authorization actor and Replay while preserving the accepted R02 generation unchanged.

### 3. Durable consumption and crash recovery cannot be safely added first

The existing `write_json_immutable` persistence helper checks `Path.exists()` and then calls `Path.write_text`. It provides neither exclusive `O_EXCL` claiming nor file/directory fsync. Existing mutation Replay has no authorization-consumption, replacement-started, atomic-replace-completed, restoration-started, recovery-required, or termination stages. Existing rollback metadata is created only after successful mutation validation and retains hashes, not original bytes.

Those deficiencies are hardenable inside versioned existing owners, but only after the request can authenticate the exact authorization generation. Adding an exclusive journal, atomic replacement, or recovery branch now would be partial hardening attached to incomplete authorization evidence. The prompt explicitly requires stopping before such a partial path is created.

## Inspected contracts and exact finding

| Contract | Current semantics | R04 consequence |
|---|---|---|
| `platform_core_existing_file_governance.authorize_g31_approved_existing_file_mutation` | Creates canonical record directly; returns hash-bound in-memory capture | No canonical authorizer or authorization Replay reference |
| `reconstruct_g31_existing_file_mutation_authorization_binding` | Reconstructs upstream evidence and capture hash | Cannot return facts absent from the authorization generation |
| `authorization_record.create_authorization_record` / `validate_authorization_record` | Deterministic generic record, no actor/Replay reference | Insufficient for the required authenticated V2 request |
| `authorization_runtime.authorize_worker_request` / `reconstruct_authorization_replay` | Separate proposal-driven authorization generation and two-step Replay | Cannot be substituted without creating a second authorization |
| `filesystem_replace_worker.create_authorized_replace_request` | V1 request accepts record ID/hash but no R02 binding | Must not be extended until authorization lineage is complete |
| `filesystem_replace_worker.execute_filesystem_replace_request` | Direct non-atomic `Path.write_text` path | Remains unreachable from G31; unchanged |
| `platform_core_existing_file_replay` | Fixed successful V1 mutation sequence using non-exclusive persistence | Insufficient for consumption/crash/recovery truthfulness |
| `platform_core_existing_file_rollback` and governed rollback owners | Hash-only metadata for existing-file replacement; no original bytes | Existing-file automatic restoration remains unavailable |

## Why no approximation is acceptable

The following apparent substitutions are invalid:

- `decision.decided_by` cannot substitute for a distinct authorization actor.
- the module name or a constant such as `PLATFORM_CORE` cannot be invented after authorization and treated as authenticated evidence;
- `authorization_binding_hash` cannot substitute for a persisted Replay reference/hash;
- `replay_visible=true` cannot substitute for Replay persistence or reconstruction;
- invoking `authorize_worker_request` after R02 cannot substitute for reconstruction because it creates another authorization;
- a process-local set cannot substitute for durable one-shot consumption;
- exception handling cannot substitute for crash recovery;
- hash-only rollback metadata cannot substitute for authenticated original restoration bytes.

## Preserved runtime state

The certified G31 stop state remains unchanged:

```text
authorization_status = AUTHORIZED
mutation_authorized = true
patch_created = false
worker_invoked = false
command_executed = false
repository_mutated = false
main_repository_mutated = false
```

No authenticated hardened request was created. No authorization was consumed. No temporary file, journal, replacement, rollback, recovery, completion, or termination evidence was created. No AiCLI or production caller edge was added. No Worker, CODEX process, Provider, command, or live G31 workflow was invoked.

## Changes and production delta

- Created only this governance report.
- Production files changed: 0.
- Test files changed: 0.
- Production additions/deletions: 0/0.

The existing V1 request, mutation, Replay, rollback, and tests remain byte-for-byte compatible because they were not edited.

## Validation

Focused baseline evidence:

- R02 G31 authorization binding: 9 passed.
- Generic canonical authorization and Replay: 10 passed.
- Legacy V1 existing-file replacement: 7 passed.
- Governed rollback, including unavailable existing-file restoration content: 6 passed.
- Governance tests: 5 passed.
- Total: 37 passed, 0 failed, 0 skipped, 0 deselected in 0.39s.
- `py_compile`: passed for ten inspected authorization, Replay, replace Worker, validation, coordinator, and rollback modules.

The full suite was not run because the scope gate stopped before any shared physical-mutation owner changed. The instruction to run it applies only after focused tests pass for an implemented shared-owner change. No live PTY workflow was run.

Governance engine result remains deterministic, read-only, fail-closed `PARTIALLY_CONFORMANT`: 18 checks passed, 2 pre-existing hook mismatches, 0 critical violations. Report hash: `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea`. Partial conformance is not upgraded.

## Required predecessor transition

Before physical-owner hardening, add one evidence-only, versioned extension to the existing canonical G31 mutation-authorization owner. It must preserve the accepted R02 branch and canonical record while adding an authenticated authorization-owner identity and a standalone immutable authorization Replay that wraps and reconstructs the exact same authorization record and complete R02 subject. It must not create a second authorization, mutation request, consumption claim, Worker invocation, or source write.

The extension must resolve semantics explicitly:

1. identify the existing constitutional authority owner that performs canonical mutation authorization, distinct from the V3 human decision actor;
2. bind that owner identity into the authorization generation before hashing;
3. persist a versioned authorization context/authorized/returned Replay using exclusive append-only destinations;
4. expose public reconstruction returning authorization actor, reference, Replay hash, record identity/hash/status/scope, R02 binding hash, and upstream candidate/decision identities;
5. reject raw actor claims, absent/substituted/reordered Replay, changed record or R02 subject, duplicate destination, and cross-session evidence;
6. remain evidence-only and stop with all request, consumption, Worker, command, patch, and mutation flags false.

After that predecessor is certified, R04 hardening can safely resume against reconstructable authorization evidence.

## Repository preservation and commit commands

No runtime behavior or source target content changed. The only scoped path is this report. Protected paths were not staged, modified, restored, deleted, or normalized by this work. No commit was created.

Documentation-only commands:

```bash
git add docs/governance/G31_24G_R04_R04_EXISTING_REPLACE_OWNER_ATOMICITY_CONSUMPTION_AND_RECOVERY_HARDENING.md
git commit -m "docs(governance): record replace owner hardening blocker"
```

Evidence-scoped G31 conversational reachability remains 99.8%. Whole-project progress remains 97.8%. Physical mutation safety progress does not advance because fail-closed scope discipline prevented partial hardening.

Exactly one next state:

`G31_24G_R04_R04_R01_CANONICAL_MUTATION_AUTHORIZATION_ACTOR_AND_REPLAY_BINDING_REQUIRED`

## Bounded next prompt

Implement only `G31_24G_R04_R04_R01_CANONICAL_MUTATION_AUTHORIZATION_ACTOR_AND_REPLAY_BINDING_REQUIRED`. Begin from the committed R04 blocker report and stop if its verdict is absent. Audit the constitutional owner identity for canonical mutation authorization, distinct from the V3 human decision actor. Extend only the existing `platform_core_existing_file_governance` and existing authorization Replay owner with a versioned evidence-only branch that preserves R02 behavior and wraps the exact existing `GOVERNED_WORKER_AUTHORIZATION_RECORD_V1`; do not create a second authorization. Bind the canonical authorization-owner identity before hashing and persist an exclusive, ordered, standalone Replay whose reconstruction returns authorization actor, Replay reference/hash, authorization record identity/hash/status/scope, R02 binding hash, session, and candidate/decision identities. Reject caller-supplied actor claims, missing/substituted/reordered Replay, changed record or subject, duplicate destinations, and cross-session evidence. Add isolated focused tests and preserve all V1/R02 compatibility. Stop before request construction, authorization consumption, Worker dispatch, temporary-file creation, patching, or mutation. Do not change AiCLI, invoke the live G31 path, run a PTY workflow, or commit.
