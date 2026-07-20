# G31-24G-R04-R04-R02 — Existing Replace Owner Atomicity, Consumption, and Recovery Hardening

## Verdict

G31_EXISTING_REPLACE_OWNER_ATOMICITY_CONSUMPTION_AND_RECOVERY_HARDENING_OPERATIONAL

The existing filesystem replacement owner now has an additive authenticated V2 branch that reconstructs the exact R01 actor-bound authorization before constructing a request, durably consumes it once, validates an isolated Git repository and stable target descriptors, performs a same-directory atomic replacement, verifies exact bytes and mode, restores atomically after any caught post-replace failure, and supports explicit durable-journal recovery after process interruption. Legacy V1 is unchanged. No AiCLI or live G31 call edge exists.

## Baseline

- Branch: master.
- Immutable baseline HEAD: 3e62282859e4e6b621b977127bd831610c8b7d9b.
- Baseline subject: feat(governance): bind mutation authorization actor and replay.
- The committed R01 report contains G31_CANONICAL_MUTATION_AUTHORIZATION_ACTOR_AND_REPLAY_BINDING_OPERATIONAL.
- The committed R03/R04 safety evidence contains EXISTING_REPLACE_MUTATION_OWNER_SAFETY_HARDENING_REQUIRED.
- Initial parent dirt was limited to the nine protected paths.
- Nested repositories were clean.

Generation 30 and committed G31-02 through R01 remain immutable accepted baselines.

## Changed owners and scope

- aigol/runtime/platform_core_existing_file_governance.py: 72 additions.
- aigol/workers/filesystem_replace_worker.py: 370 additions and one import-line replacement.
- tests/test_g31_24g_r04_r04_r02_existing_replace_owner_hardening.py: isolated physical-write and failure-injection evidence.
- This report.

Production additions total 442 across two production files, within the maximum of 450 additions and five files. No top-level artifact family, router, authorization system, Replay subsystem, AiCLI behavior, or live caller was added.

## Authenticated request projection

create_g31_authenticated_replace_request accepts the R01 actor Replay capture and the already-required canonical evidence set. It independently calls reconstruct_g31_mutation_authorization_actor_and_replay, validates the V2 candidate, and derives the request from the accepted V2 implementation manifest.

Callers cannot supply actor, repository, target, operation, bytes, hashes, modes, or destinations separately.

AUTHORIZED_REPLACE_EXISTING_FILE_REQUEST_V2 hashes:

- canonical actor and exact unchanged GOVERNED_WORKER_AUTHORIZATION_RECORD_V1;
- authorization identity/hash/status/scope/Worker and authorization Replay reference/hash;
- actor-Replay and R02 binding hashes;
- V2 candidate identity/hash/Replay/provenance;
- V3 decision identity/hash/outcome/scope/actor/Replay;
- session identity and root;
- repository identity/root/grounding;
- manifest hash and exact REPLACE_CONTENT target;
- raw preimage/postimage SHA-256;
- source/replacement content hashes;
- exact base64-encoded preimage and replacement bytes;
- source and replacement modes;
- deterministic lifecycle, consumption, journal, result, rollback, recovery, completion, termination, and same-directory temporary destinations.

The only execution and recovery callers are the new non-live Platform Core functions:

- execute_g31_authenticated_replace;
- recover_g31_authenticated_replace.

They reconstruct and build the request internally before invoking the existing Worker's private V2 engine. No production caller reaches either function.

## Durable one-shot consumption and Replay

The deterministic lifecycle root is:

    <session-root>/G31_EXISTING_FILE_REPLACE_V2/<authorization-hash-payload>/

Lifecycle files use canonical serialization, mode 0600, exclusive O_CREAT | O_EXCL, file fsync, and containing-directory fsync.

The predecessor-hash Replay accepts only one non-branching sequence:

    request validated
    -> authorization consumption claimed
    -> pre-write journal persisted
    -> replacement started
    -> atomic replacement completed
    -> post-write validation
    -> completion

Failure branches record atomic restoration when applicable and terminate truthfully. Explicit recovery extends the predecessor chain after an interrupted or recovery-required terminal state. Missing, altered, duplicated, unexpected, reordered, or branched artifacts fail closed.

The consumption file is the durable authorization claim. Duplicate, concurrent, repeated, or retry execution cannot create a second claim or mutation. An unresolved recovery state cannot be retried through execution; only the explicit authenticated recovery entry point may use the journal.

## Repository and descriptor safety

Before consumption and before temporary-file creation, the V2 owner proves:

- canonical absolute repository root;
- exact Git top-level using a fixed read-only Git invocation;
- clean complete worktree;
- relative contained target;
- no nested repository in target path components;
- no symlinked path component;
- target opened with O_NOFOLLOW;
- regular-file type and link count exactly one;
- target name and stable descriptor device/inode/mode/link identity;
- exact raw preimage bytes, SHA-256, and mode.

The containing directory and target remain open through stable descriptors. The final drift check compares the original target descriptor and no-follow target name immediately before replacement. Temporary and restore files are created exclusively in the stable target directory.

## Atomic replacement and validation

The V2 algorithm:

1. opens stable parent and target descriptors;
2. durably records request, consumption, and original-byte/mode journal;
3. creates an exclusive same-directory regular temporary file;
4. writes the exact authenticated replacement bytes;
5. applies the exact replacement mode;
6. flushes and fsyncs the temporary descriptor;
7. revalidates device, inode, mode, links, size, and preimage through stable descriptors;
8. calls os.replace using the stable parent directory descriptor for both source and destination;
9. fsyncs the containing directory;
10. reopens with O_NOFOLLOW and verifies regular type, single link, exact bytes, and exact mode;
11. persists validation and completion.

The hardened branch does not use Path.write_text. The V1 branch remains byte-for-byte behaviorally compatible and retains its historical implementation.

## Restoration and crash recovery

The durable pre-write journal stores exact original bytes, mode, device, inode, link count, preimage hash, and request lineage.

For every caught failure after os.replace, the owner:

- verifies the current target is the exact authorized postimage before overwriting it;
- exclusively creates a same-directory restore temporary file;
- writes and fsyncs exact original bytes and mode;
- atomically replaces the target;
- fsyncs the directory;
- verifies restored type, single link, exact bytes, and mode.

repository_mutated=false after a post-replace failure is returned only after restoration verification. If restoration cannot be proved, the result records repository_mutated=true, recovery_required=true, and truthful termination evidence.

recover_g31_authenticated_replace reconstructs the same actor-bound request and durable lifecycle, cleans deterministic leftover temporary files, and restores only an exact authorized postimage. Unexpected target bytes fail without overwrite. Recovery is one-shot and persisted.

A simulated KeyboardInterrupt immediately after atomic replacement left the postimage in the isolated repository. The explicit recovery entry point reconstructed the durable journal, restored exact original bytes and mode atomically, and persisted RECOVERED.

## Failure and security evidence

Dedicated tests prove:

- authenticated public request construction and isolated execution;
- actor, manifest, authorization, candidate, decision, session, target, and scope substitution rejection;
- dirty worktree and nested repository rejection;
- target and path-component symlink rejection;
- hard-link rejection;
- mode and preimage drift rejection;
- drift injected immediately before final stable-descriptor validation;
- duplicate and concurrent consumption rejection;
- temporary creation, write, and fsync failure;
- replace and directory-fsync failure;
- Replay failure before and after replacement;
- byte/mode verification failure;
- restoration success and restoration failure;
- recovery-required truth, duplicate execution rejection, and later explicit recovery;
- process interruption and durable-journal recovery;
- Replay tamper rejection.

All source-changing tests used temporary Git repositories under pytest-managed temporary directories. No fixture, mutator, request, or recovery owner targeted /home/pisarna/work/sapianta.

## Compatibility and authority

- V1 request type, request hashes, caller signatures, replay, completion, and rollback metadata are unchanged.
- The exact R01 and R02 authorization artifacts and hashes are unchanged.
- Governance remains the canonical authorization owner.
- The V3 human actor remains the distinct mutation-decision owner.
- The Worker owns only bounded physical replacement.
- Replay records evidence and does not authorize.
- Git use is fixed read-only repository/status inspection; git_performed=false remains truthful for mutation.
- Provider, CODEX, generated commands, commits, deployment, and AiCLI remain absent.

## Validation

- Dedicated hardened-owner suite: 31 passed, 0 failed, 0 skipped, 0 deselected in 0.84s.
- Broader focused owner, R01/R02 authorization, generic authorization Replay, V1 replacement, rollback, multi-file, V3 decision, and Governance set: 93 passed, 0 failed, 0 skipped, 0 deselected in 1.44s.
- Real V2 candidate provenance/reconstruction and AiCLI stop-state suite: 4 passed, 0 failed, 0 skipped, 0 deselected in 374.31s.
- Distinct focused total: 97 passed, 0 failed, 0 skipped, 0 deselected.
- Complete suite, run exactly once after focused success: 6,621 passed, 4 skipped, 0 failed in 3377.60s (0:56:17).
- No live PTY workflow was run.

Governance remains deterministic, read-only, fail-closed PARTIALLY_CONFORMANT: 18 checks passed, two pre-existing hook mismatches, and zero critical violations. Report hash: 0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea. Partial conformance is not upgraded.

## Repository preservation and commit commands

No live or source repository mutation occurred. Only isolated temporary Git repositories were changed during physical-write tests. Protected paths were not staged, altered, restored, deleted, or normalized by this work. No commit was created.

Scoped commands:

    git add aigol/runtime/platform_core_existing_file_governance.py aigol/workers/filesystem_replace_worker.py tests/test_g31_24g_r04_r04_r02_existing_replace_owner_hardening.py docs/governance/G31_24G_R04_R04_R02_EXISTING_REPLACE_OWNER_ATOMICITY_CONSUMPTION_AND_RECOVERY_HARDENING.md
    git commit -m "feat(governance): harden atomic existing-file replacement"

Evidence-scoped G31 conversational reachability: 99.9%. Whole-project progress: 97.9%. Physical replacement is certified only through the non-live owner boundary.

Exactly one next state:

G31_24G_R04_R04_R03_HARDENED_REPLACE_OWNER_LIVE_REACHABILITY_AUDIT_REQUIRED

## Bounded next prompt

Audit, without adding a caller or performing a source mutation, whether the exact accepted G31 actor-bound authorization and authenticated V2 request can be connected to the hardened non-live Platform Core owner. Inventory all current callers and presentation boundaries; reconstruct authorization, request, consumption, completion, termination, restoration, and recovery Replay; verify AiCLI remains non-authoritative; determine the minimal explicit human and presentation transition, if any; and stop before adding live reachability. Use committed R02 evidence and isolated fixtures only. Do not invoke the hardened owner against /home/pisarna/work/sapianta, add AiCLI behavior, run a live mutation workflow, or commit.
