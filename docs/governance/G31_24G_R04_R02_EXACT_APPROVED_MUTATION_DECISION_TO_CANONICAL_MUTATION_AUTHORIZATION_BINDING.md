# G31-24G-R04-R02 — Exact Approved Mutation Decision to Canonical Mutation Authorization Binding

## Verdict and baseline

Implementation verdict:

`G31_R02_EXACT_APPROVED_DECISION_TO_CANONICAL_MUTATION_AUTHORIZATION_BINDING_OPERATIONAL`

Baseline branch: `master`.

Immutable baseline HEAD: `8069f65eeaa15270c420dbeedb31e9084683ec67` (`fix(governance): reconstruct activation lineage for R01 candidate`).

The committed baseline contains `G31_24G_R04_R01_ACTIVATION_RECONSTRUCTION_COMPATIBILITY_REPAIR.md` with accepted verdict `G31_R01_ACTIVATION_RECONSTRUCTION_COMPATIBILITY_REPAIR_OPERATIONAL`. The three nested repositories were clean before implementation. The nine declared parent-repository paths were pre-existing protected dirt and were not modified, staged, restored, or normalized by this work.

## Audit result and canonical owner

The existing canonical existing-file mutation-authorization owner is `aigol/runtime/platform_core_existing_file_governance.py`. Its pre-existing public `create_existing_file_mutation_authorization_record` composes the canonical `create_authorization_record` and `validate_authorization_record` boundaries in `aigol/authorization/authorization_record.py` for `FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER` and scope `FILESYSTEM_REPLACE_EXISTING_TEXT_FILE`.

The pre-existing entry point validates the historical V1 candidate and therefore cannot directly consume the accepted G31 V2 candidate. A bounded adapter was necessary. `authorize_g31_approved_existing_file_mutation` now lives in the same canonical owner, reconstructs and binds the exact G31 evidence, and reuses the same canonical authorization-record creation and validation functions. `reconstruct_g31_existing_file_mutation_authorization_binding` independently reconstructs that binding. No approval owner, authorization authority, candidate, human decision, Worker, Provider, Replay writer, patch owner, or source-write owner was duplicated.

AiCLI was not changed. The new public authorization boundary is callable by a future transport composition, but AiCLI does not approve, authorize, infer approval, own Replay, dispatch, or mutate in this generation.

## Changed files and delta

- `aigol/runtime/platform_core_existing_file_governance.py` — bounded V2/V3 evidence adapter and read-only reconstruction boundary; 187 production additions and 0 deletions.
- `tests/test_g31_24g_r04_r02_mutation_authorization_binding.py` — 249 lines of isolated focused evidence.
- This report.

No accepted artifact generation was overwritten. The binding capture has a version and hash but does not introduce a competing authorization artifact family: the authorization itself remains `GOVERNED_WORKER_AUTHORIZATION_RECORD_V1`.

## Preserved identities and hashes

| Generation | Exact identity retained | Exact hash retained |
|---|---|---|
| Activation | `activation_replay_reference` from the independently reconstructed activation binding | `activation_replay_hash` |
| Accepted V2 candidate | `candidate_id`, `candidate_replay_reference`, session, operation, target, and provenance | candidate `artifact_hash`, candidate Replay hash, and `candidate_provenance_binding_hash` |
| V3 human mutation decision | `human_decision_id`, V3 artifact type, `APPROVED`, and decision Replay reference | decision `artifact_hash` and reconstructed four-step decision Replay hash |
| Mutation authorization | caller-supplied `authorization_id`, candidate ID as `proposal_id`, replace Worker, replace scope, `AUTHORIZED` status | canonical `authorization_hash`, exact evidence `binding_hash`, and outer `authorization_binding_hash` |

The focused fixture uses distinct stable identities `G31-R04-R02-CANDIDATE`, `G31-R04-R02-DECISION`, and `G31-R04-R02-AUTHORIZATION`. Hash values remain content-derived rather than copied constants.

## Reconstructed-evidence proof

Authorization receives both historical captures and claimed reconstructions, but trusts neither claim directly:

1. It calls `reconstruct_codex_worker_activation_binding` and requires exact equality with the supplied activation reconstruction. Only reconstructed `lineage["grounding"]` is projected downstream; the raw activation capture cannot substitute for it.
2. It calls `reconstruct_g31_accepted_existing_file_mutation_candidate_replay`, requires exact equality with the supplied V2 reconstruction, validates `EXISTING_FILE_MUTATION_CANDIDATE_ARTIFACT_V2`, and rejects stale runtime versions.
3. It calls `reconstruct_existing_file_mutation_decision_replay`, requires exact equality with the supplied V3 reconstruction, and requires `HUMAN_DECISION_ARTIFACT_V3`, exact outcome `APPROVED`, `mutation_decision_approved=true`, and pre-authorization `mutation_authorized=false`.
4. It requires the V3 decision's candidate ID, candidate artifact hash, candidate Replay hash, and provenance-binding hash to equal the exact reconstructed V2 candidate.
5. It requires candidate repository root and grounding hash to equal the reconstructed activation grounding, then binds operation, target path, preimage hash, and postimage hash into the authorization evidence hash.

The V3 Replay subject already contains the candidate provenance and independently checks target path and pre/postimage hashes. Consequently, path, expected-source-hash, cross-session, cross-turn, or decision-to-candidate substitution changes the candidate, provenance, Replay, decision, or binding hash and fails closed. Cross-turn identity is not inferred from conversational text; it is represented by exact candidate and decision generations.

## Authorization result and authority boundary

For the exact reconstructed V2 candidate plus its exact replayed V3 `APPROVED` decision, the canonical result is:

```text
authorization_status = AUTHORIZED
mutation_authorized = true
worker_id = FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER
authorization_scope = FILESYSTEM_REPLACE_EXISTING_TEXT_FILE
patch_created = false
disposable_execution_performed = false
worker_invoked = false
provider_invoked = false
command_executed = false
repository_mutated = false
main_repository_mutated = false
```

Human authority owns the distinct V3 decision. The existing Platform Core authorization owner validates that decision and creates the governed authorization record. The replace Worker remains the later mutation executor and cannot self-authorize. Provider, proposal, cognition, Replay, AiCLI, and the Worker have no authorization authority. Content acceptance remains necessary lineage but is not mutation authorization.

The authorization function is evidence-only. It imports no patch or mutation primitive, performs no command, writes no Replay file, dispatches no Worker, and calls no Provider. The first possible source-changing boundary remains downstream in the existing replace Worker and was not called.

## Fail-closed and duplicate behavior

Focused evidence proves rejection of absent or non-`APPROVED` decisions, a decision for another candidate, candidate or decision artifact-hash tampering, claimed Replay substitution, raw candidate/decision inputs in place of reconstruction, raw activation capture in place of reconstructed lineage, cross-session substitution, target-path substitution, and expected-preimage-hash substitution. The V3 contract admits only `APPROVED` or `REJECTED`; cancelled, expired, or unknown vocabulary is invalid rather than silently mapped.

Repeated authorization reconstruction recomputes all three upstream reconstructions and the canonical authorization hash, returns the same result, creates no new JSON evidence, and creates no activation, candidate, decision, Worker invocation, Provider invocation, patch, or mutation. Existing V2 candidate and V3 decision Replay owners retain their immutable-destination and duplicate-consumption protections. This generation does not consume or apply the authorization, so repository-mutation idempotency remains a downstream responsibility.

## Source and Git preservation

The successful isolated fixture recorded `b"original bytes\n"` and a clean temporary Git status before authorization. Both were byte-for-byte identical after authorization and reconstruction. The only Worker invocation in the full R01 fixture remains its single pre-existing bounded activation; the R02 authorization fixture invokes zero Workers and zero Providers.

The parent repository retains only the nine protected pre-existing paths plus the three scoped R02 files. All nested repositories remain clean. No full upstream PTY run, complete repository suite, source mutation, patch creation, disposable execution, Git mutation, or commit was performed.

## Focused validation

- R02 authorization binding: 9 passed, 0 failed, 0 skipped, 0 deselected in 0.30s.
- R01 candidate provenance/reconstruction (completed against this implementation session without rerun): 4 passed, 0 failed, 0 skipped, 0 deselected in 377.99s.
- V3 mutation decision, activation reconstruction/tamper, existing first-mutating-owner, and Governance tests: 16 passed, 0 failed, 0 skipped, 0 deselected in 3.61s.
- Generic governed authorization contract: 10 passed, 0 failed, 0 skipped, 0 deselected in 0.10s.
- `py_compile`: passed for the changed production and focused-test modules.
- Parent and three nested `git diff --check`: passed.
- Parent and nested status checks: passed; nested repositories clean and protected parent dirt preserved.

The complete 6,557-test suite and long PTY workflow were intentionally not run because focused evidence did not conflict with committed certification.

## Governance

The Governance engine remains deterministic, read-only, fail-closed `PARTIALLY_CONFORMANT`: 18 checks passed, 2 pre-existing hook mismatches remain visible, and there are 0 critical violations. This result is not upgraded to full conformance.

## Scoped commit commands

No commit was created. If the human operator accepts this generation, the exact documentation-safe scope is:

```bash
git add aigol/runtime/platform_core_existing_file_governance.py tests/test_g31_24g_r04_r02_mutation_authorization_binding.py docs/governance/G31_24G_R04_R02_EXACT_APPROVED_MUTATION_DECISION_TO_CANONICAL_MUTATION_AUTHORIZATION_BINDING.md
git commit -m "feat(governance): bind approved mutation decision to authorization"
```

These commands exclude every protected path.

## Progress and next state

Evidence-scoped G31 conversational reachability: 99.8%.

Whole-project progress: 97.8%.

Exactly one next state:

`G31_24G_R04_R03_CANONICAL_MUTATION_AUTHORIZATION_TO_EXISTING_REPLACE_MUTATION_OWNER_BINDING_REQUIRED`
