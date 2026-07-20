# G31-24G-R04-R04-R03 — Hardened Replace Owner Live Reachability Audit

## Verdict

`G31_HARDENED_REPLACE_OWNER_LIVE_BINDING_REQUIRED`

Plain-language conclusion: the committed contracts form a compatible evidence chain from an accepted V2 result through the hardened replacement owner, but the production conversational path is not connected to that chain. AiCLI currently creates and presents the replayed V2 existing-file candidate, records `human_mutation_decision_recorded=false`, and terminates. It does not present or record the V3 mutation decision, create canonical mutation authorization, bind its canonical actor and Replay, construct an authenticated V2 request, consume authorization, invoke the hardened Worker, or route recovery.

The exact first missing production edge is from the accepted candidate branch in `aigol/cli/aicli.py` to `human_decision_runtime.prepare_existing_file_mutation_decision_context`. The exact last reachable state is therefore the accepted, replay-reconstructed V2 candidate. The hardened owner is operational only through isolated fixtures and remains non-live.

## Baseline

- Branch: `master`.
- Accepted immutable HEAD: `4c3493dc4c79f9cb6f7d54e16985107913852a9d`.
- HEAD subject: `feat(governance): harden atomic existing-file replacement`.
- Recent commits:
  - `4c3493dc feat(governance): harden atomic existing-file replacement`
  - `3e622828 feat(governance): bind mutation authorization actor and replay`
  - `151c6442 docs(governance): record replace owner hardening blocker`
  - `40b890e1 docs(governance): audit replace mutation owner safety`
  - `b9213840 feat(governance): bind approved mutation decision to authorization`
- The committed R02 hardening report contains `G31_EXISTING_REPLACE_OWNER_ATOMICITY_CONSUMPTION_AND_RECOVERY_HARDENING_OPERATIONAL`.
- The committed R01 actor/Replay report contains `G31_CANONICAL_MUTATION_AUTHORIZATION_ACTOR_AND_REPLAY_BINDING_OPERATIONAL`.
- Initial parent status contained only the nine protected paths. No path was staged.
- `sapianta-domain-credit`, `sapianta_system`, and `sapianta-domain-trading` were clean.

Generation 30 and committed G31-02 through G31-24G-R04-R04-R02 were treated as immutable accepted baselines.

## Audit boundary and repository preservation

This generation is documentation-only. It did not change production code, tests, schemas, AiCLI behavior, authorization behavior, Worker behavior, or source content. It did not construct or consume a real authorization, invoke a Worker or Provider, run a generated command, apply a patch, start a PTY workflow, or call the hardened execute or recovery entry point against `/home/pisarna/work/sapianta`.

Existing physical-write tests used only their committed pytest temporary-Git-repository fixtures. The complete suite was not rerun because the committed R02 full-suite certification and current focused evidence agree.

## Inspected files and public symbols

### Production contracts

| File | Public symbols and semantics inspected |
| --- | --- |
| `aigol/cli/aicli.py` | `run_reference_uhi_session`; content decision, generated-content acceptance, activation reconstruction, V2 candidate creation/reconstruction/presentation, session stop, runtime-result persistence |
| `aigol/runtime/human_decision_runtime.py` | `prepare_existing_file_mutation_decision_context`; `record_existing_file_mutation_decision`; `reconstruct_existing_file_mutation_decision_replay`; V3 context/decision renderers |
| `aigol/runtime/platform_core_existing_file_mutation_candidate.py` | `create_g31_accepted_existing_file_mutation_candidate`; `validate_g31_accepted_existing_file_mutation_candidate`; `reconstruct_g31_accepted_existing_file_mutation_candidate_replay`; candidate presentation and duplicate handling |
| `aigol/runtime/platform_core_existing_file_governance.py` | `authorize_g31_approved_existing_file_mutation`; `reconstruct_g31_existing_file_mutation_authorization_binding`; `bind_g31_mutation_authorization_actor_and_replay`; `reconstruct_g31_mutation_authorization_actor_and_replay`; `create_g31_authenticated_replace_request`; `execute_g31_authenticated_replace`; `recover_g31_authenticated_replace` |
| `aigol/authorization/authorization_runtime.py` | generic authorization Replay reconstruction and the versioned existing-record actor/Replay persistence/reconstruction owners |
| `aigol/authorization/authorization_record.py` | canonical `GOVERNED_WORKER_AUTHORIZATION_RECORD_V1` creation and validation as consumed by the inspected owners |
| `aigol/workers/filesystem_replace_worker.py` | V1 request/execute/reconstruction compatibility; V2 request validation, lifecycle reconstruction, durable consumption, execution, restoration, recovery, completion and termination |
| `aigol/runtime/existing_file_mutation_runtime.py` | legacy V1 existing-file coordinator and its request/Worker/validation/Replay call chain |
| `aigol/runtime/multi_file_mutation_runtime.py` | legacy per-operation V1 replacement coordinator and Worker calls |
| `aigol/runtime/platform_core_existing_file_validation.py` | legacy pre/post validation owners |
| `aigol/runtime/platform_core_existing_file_replay.py` | legacy nine-step Replay persistence and reconstruction |
| `aigol/runtime/platform_core_existing_file_rollback.py` | legacy rollback metadata owner |

### G31-24G reports inspected

- `G31_24G_R01_VERSIONED_EXISTING_FILE_MUTATION_CANDIDATE_PROVENANCE_REPLAY_BINDING.md`
- `G31_24G_R02_VERSIONED_HUMAN_MUTATION_DECISION_CONTRACT_ON_REPLAYED_V2_CANDIDATE.md`
- `G31_24G_R03_ACTIVATION_LINEAGE_FIXTURE_COMPATIBILITY_AUDIT.md`
- `G31_24G_R04_R01_ACTIVATION_RECONSTRUCTION_COMPATIBILITY_REPAIR.md`
- `G31_24G_R04_R02_EXACT_APPROVED_MUTATION_DECISION_TO_CANONICAL_MUTATION_AUTHORIZATION_BINDING.md`
- `G31_24G_R04_R03_CANONICAL_AUTHORIZATION_TO_REPLACE_MUTATION_OWNER_SAFETY_AUDIT.md`
- `G31_24G_R04_R04_EXISTING_REPLACE_OWNER_ATOMICITY_CONSUMPTION_AND_RECOVERY_HARDENING.md`
- `G31_24G_R04_R04_R01_CANONICAL_MUTATION_AUTHORIZATION_ACTOR_AND_REPLAY_BINDING.md`
- `G31_24G_R04_R04_R02_EXISTING_REPLACE_OWNER_ATOMICITY_CONSUMPTION_AND_RECOVERY_HARDENING.md`

The earlier G31-24F post-acceptance authorization audit and canonical constitutional/layer guidance were also inspected for authority separation. No repository evidence establishes a mandatory additional human decision after the V3 mutation decision and canonical Governance authorization.

### Focused tests inspected and executed

- `tests/test_g31_24g_r01_existing_file_candidate_provenance.py`
- `tests/test_g31_24g_r02_human_mutation_decision.py`
- `tests/test_g31_24g_r04_r02_mutation_authorization_binding.py`
- `tests/test_g31_24g_r04_r04_r01_authorization_actor_replay_binding.py`
- `tests/test_g31_24g_r04_r04_r02_existing_replace_owner_hardening.py`
- `tests/test_governance_conformance.py`

## Exact production call graph

### Currently reachable conversational chain

```text
AiCLI accepted content
-> record_content_acceptance_decision
-> reconstruct_content_acceptance_decision_replay
-> accept_generated_content_from_content_acceptance_decision
-> reconstruct_generated_content_acceptance_from_decision_replay
-> reconstruct_codex_worker_activation_binding
-> create_g31_accepted_existing_file_mutation_candidate
-> reconstruct_g31_accepted_existing_file_mutation_candidate_replay
-> render_g31_accepted_existing_file_mutation_candidate
-> session_status = REFERENCE_UHI_SESSION_COMPLETED
-> exit_reason = GENERATED_CONTENT_ACCEPTANCE_RECORDED
-> STOP
```

The stop-state fields are:

```text
result_accepted = true
existing_file_mutation_candidate_created = true
human_mutation_decision_recorded = false
mutation_authorized = false
main_repository_mutated = false
```

AiCLI clears the content-acceptance context and breaks the session loop immediately after candidate presentation. There is no pending mutation-decision context variable, EOF state, command handling, presentation, recording, or runtime-result update.

### Compatible but non-live continuation

```text
prepare_existing_file_mutation_decision_context                 NO PRODUCTION CALLER
-> record_existing_file_mutation_decision                       NO PRODUCTION CALLER
-> reconstruct_existing_file_mutation_decision_replay           internal reconstruction consumer only
-> authorize_g31_approved_existing_file_mutation                NO PRODUCTION CALLER
-> reconstruct_g31_existing_file_mutation_authorization_binding internal reconstruction consumer only
-> bind_g31_mutation_authorization_actor_and_replay              NO PRODUCTION CALLER
-> reconstruct_g31_mutation_authorization_actor_and_replay       request builder only
-> create_g31_authenticated_replace_request                      execute/recover wrappers only
-> execute_g31_authenticated_replace                             NO PRODUCTION CALLER
-> durable V2 consumption and hardened replacement
```

`recover_g31_authenticated_replace` also has no production caller.

The only non-test production calls involving the hardened public entry points are internal composition edges: `execute_g31_authenticated_replace` and `recover_g31_authenticated_replace` each call `create_g31_authenticated_replace_request`; that builder calls actor/Replay reconstruction and V2 validation. No coordinator, router, Human Interface, AiCLI, or Worker dispatcher calls any of these three entry points.

### Separate legacy V1 callers

`existing_file_mutation_runtime.execute_existing_file_mutation` and `multi_file_mutation_runtime._execute_one_operation` call the legacy V1 request builder and `execute_filesystem_replace_request`. They do not accept the G31 V2 candidate, V3 decision, R02 authorization binding, R01 actor/Replay binding, or authenticated V2 request, and they are not a valid live bridge.

## Authentic evidence mapping

At the current AiCLI stop, every antecedent needed to reconstruct the V2 candidate remains available in `runtime_result` or is deterministically reconstructible from its retained captures. Evidence that belongs to later generations is absent because those generations are never called.

| Required material | Current authentic source | Current status |
| --- | --- | --- |
| Session ID/root and workspace | AiCLI session arguments and persisted runtime state | Available |
| Activation capture | `codex_worker_activation_capture` | Available |
| Governed execution and execution candidate | retained runtime-result captures | Available |
| Repository grounding | public activation reconstruction `lineage.grounding` | Reconstructible; not caller-supplied |
| G31-23B binding/manifest/validations | `codex_replacement_acceptance_prerequisite_binding_capture` and bound manifest captures | Available |
| V2 content decision and Replay | `human_content_acceptance_decision_capture` plus Replay reference | Available |
| Generated-content acceptance and Replay | `generated_content_acceptance_capture` plus Replay reference | Available |
| V2 existing-file candidate and Replay | `existing_file_mutation_candidate_capture` plus reconstruction | Available and last live state |
| V3 mutation decision and Replay | No AiCLI context or decision call | Not created |
| Canonical authorization record/binding | Authorization owner has no production caller | Not created |
| Canonical actor-bound authorization Replay | Binder has no production caller | Not created |
| Authenticated V2 replace request | Builder has no production caller outside execute/recover wrappers | Not created |
| Consumption/journal/completion/recovery Replay | Execute/recover have no production caller | Not created |

The existing request builder accepts the exact evidence set required by the public reconstructors: authorization capture, candidate capture/reconstruction, V3 decision capture/reconstruction, acceptance capture, content-decision capture, G31-23B binding, repository grounding, activation capture/reconstruction, governed execution, execution candidate, session root, and workspace. It rejects caller-supplied actor, repository, target, operation, bytes, hashes, modes, and destinations by deriving them from reconstructed evidence.

## Compatibility findings

| Transition | Classification | Finding |
| --- | --- | --- |
| AiCLI accepted result -> V2 candidate | Operational | Production caller, reconstruction, presentation, and stop state exist |
| V2 candidate -> V3 context/decision | Compatible contract; missing production binding | All authentic inputs are retained/reconstructible, but AiCLI never calls the V3 owner |
| V3 APPROVED -> canonical authorization | Compatible contract; missing production binding | R02 owner reconstructs candidate/decision/activation before creating the unchanged canonical record |
| Canonical authorization -> actor/Replay binding | Compatible contract; missing production binding | R01 owner preserves the record and persists independent actor-bound Replay |
| Actor-bound authorization -> authenticated request | Compatible contract; missing production binding/presentation | Pure builder independently reconstructs evidence and returns a validated in-memory request |
| Authenticated request -> durable consumption/replace | Compatible hardened owner; missing explicit production invocation owner | Execute immediately enters durable lifecycle; it must not be hidden behind presentation or authorization creation |
| Interrupted lifecycle -> recovery | Compatible hardened owner; missing production recovery route | Same evidence reconstructs the same request/destinations; recovery requires existing consumption+journal and creates no second authorization or claim |

The deterministic verdict is binding-required rather than blocked because the required artifact contracts, public reconstructors, projections, one-shot consumption, replacement, restoration, and recovery already exist and agree. The missing elements are production orchestration and presentation edges. The current dirty source worktree would independently fail the hardened owner's clean-worktree check before consumption; that is a correct runtime precondition, not a contract incompatibility.

## First missing edge and bounded stages

Exact first missing caller:

`aigol/cli/aicli.py::run_reference_uhi_session`, immediately after successful V2 candidate reconstruction/presentation.

Exact first missing callee:

`aigol/runtime/human_decision_runtime.py::prepare_existing_file_mutation_decision_context`.

The caller already has or can reconstruct every callee input: candidate capture, acceptance capture, content-decision capture, prerequisite binding, repository grounding, human actor identity, session root, timestamp, and deterministic Replay destination.

The stages can and should remain separate:

1. V3 context presentation and exact human `APPROVED | REJECTED` recording;
2. evidence-only canonical authorization and actor/Replay binding;
3. evidence-only authenticated request construction and truthful presentation;
4. explicit Platform Core execution invocation policy;
5. isolated end-to-end lifecycle certification;
6. separately approved live-source reachability.

This audit proves no current mandatory contract for an additional human-decision artifact after V3. It therefore does not invent one. It also does not infer that V3 `APPROVED` or Governance `AUTHORIZED` self-executes. A future explicit Platform Core production coordinator must own the call to the physical Worker under whatever separately certified invocation policy is adopted; AiCLI may transport/present that action but may not own authority, and the Worker may not self-authorize or self-dispatch.

## Consumption and first source-changing instructions

Request construction is evidence-only. `create_g31_authenticated_replace_request` reconstructs and validates evidence, calculates deterministic destinations, and returns an in-memory hash-bound request. It performs no consumption, Worker invocation, or source write.

The first possible durable authorization-consumption point is:

```text
filesystem_replace_worker._execute_authenticated_replace_v2
-> _persist_v2_event(..., "consumption", "AUTHORIZATION_CONSUMPTION_CLAIMED", ...)
```

This exclusive `O_CREAT | O_EXCL` lifecycle event is written before any target-directory temporary file and is the durable one-shot claim.

The first instruction that changes the target repository namespace is the exclusive same-directory temporary-file `os.open(... O_CREAT | O_EXCL | O_NOFOLLOW ...)` in `_write_v2_temporary`.

The first instruction that changes the authenticated target path/content is:

```text
aigol/workers/filesystem_replace_worker.py
_execute_authenticated_replace_v2
os.replace(temporary_name, context["name"],
           src_dir_fd=context["parent_fd"],
           dst_dir_fd=context["parent_fd"])
```

That target replacement occurs only after request validation, clean Git/top-level checks, stable no-follow descriptor checks, durable consumption, durable original-byte/mode journal, exclusive temporary write, file fsync, and final preimage/device/inode/mode/link/size revalidation.

## Authority separation

- The human operator owns content acceptance and the distinct V3 mutation-intent decision.
- `governed_authorization_runtime` owns canonical mutation authorization.
- Authorization Replay records and reconstructs authority evidence; it cannot authorize.
- Platform Core must explicitly coordinate any future request construction and Worker invocation.
- The filesystem replacement Worker owns only the bounded physical operation after exact authorization and request validation; it cannot authorize or dispatch itself.
- AiCLI is non-authoritative transport/presentation and currently stops before the V3 decision.
- CODEX remains restricted to its earlier bounded Worker role. It receives no replacement-owner call edge or mutation authority.
- Provider authority and invocation remain absent.

Content acceptance, V3 `APPROVED`, canonical `AUTHORIZED`, authenticated request construction, durable authorization consumption, and physical replacement are distinct events. No earlier proposal approval, execution confirmation for the CODEX Worker, task satisfaction, disposable-validation approval, or content acceptance can substitute for the V3 mutation decision or Governance authorization.

## Recovery reachability

The recovery contract is deterministic but non-live. `recover_g31_authenticated_replace` reconstructs the same actor-bound evidence and therefore rebuilds the same request identity and destinations. `_recover_authenticated_replace_v2` requires an existing valid consumption event and pre-write journal, rejects completion or prior recovery, removes only deterministic temporary names, and restores only when the current target is either already the exact original or the exact authorized postimage accepted by the restoration owner. It creates neither a second authorization nor a second consumption claim.

No production owner presents a recovery-required result or calls recovery. A future recovery coordinator must be bound separately from normal execution and must use the original evidence; retrying normal execution after consumption remains fail-closed.

## Fail-closed and remaining unbound findings

### Proven by code and focused tests once the hardened path is called

- exact authorization actor, record/status/scope/Worker, R02 hash, and authorization Replay;
- exact V2 candidate identity/hash/Replay/provenance and V3 decision identity/hash/outcome/scope/actor/Replay;
- session, repository identity/root/grounding, manifest, target, raw hashes, content hashes, exact bytes, and modes;
- deterministic destinations and request hash;
- canonical Git top-level, complete clean worktree, nested-repository rejection, containment, no symlinked component, no-follow target open, regular single-link file, device/inode/mode/link identity, and preimage drift checks;
- exclusive durable consumption, duplicate/concurrent rejection, non-branching Replay, journal, atomic same-directory replace, directory fsync, postimage verification, truthful restoration, recovery-required, completion, and termination states;
- recovery from durable journal without second authorization or consumption.

### Not live-bound

- V3 decision context/recording/presentation in AiCLI;
- canonical authorization creation from the conversational path;
- canonical actor/Replay binding from the conversational path;
- authenticated request construction and presentation;
- explicit production execution invocation;
- completion, termination, recovery-required, and recovery presentation/routing.

No authentic safety field is missing from the hardened request or Worker contract. The remaining gaps are production call edges and authority-aware presentation/orchestration. They must not be collapsed into one command.

## External dependencies

| Stage | Requirements |
| --- | --- |
| V3 context/decision, canonical authorization, actor Replay, request construction | Local Python and session-evidence filesystem access; no network, credentials, MCP, Provider, CODEX Worker, generated shell command, or source write |
| Hardened preflight/execute | Local filesystem read/write and fixed read-only Git executable calls for top-level and complete-clean-worktree proof; no network, credentials, MCP, Provider, CODEX, generated command, commit, or deployment |
| Recovery | Local filesystem read/write plus the original session evidence and durable journal; no new authorization, network, Provider, CODEX, or generated command |

## Validation

- Focused V2 candidate, V3 decision, R02 authorization, R01 actor/Replay, R02 hardened-owner, and Governance tests: **69 passed, 0 failed, 0 skipped, 0 deselected in 374.77 seconds**.
- All physical-write and recovery cases used existing pytest-managed temporary Git repositories.
- Targeted `py_compile`: passed for the six mandatory production modules plus the legacy existing-file/multi-file coordinators and validation/Replay/rollback modules.
- Governance engine: deterministic, read-only, fail-closed `PARTIALLY_CONFORMANT`; 18 checks passed, 2 known hook mismatches, 0 critical violations; report hash `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea`.
- The known findings remain visible: missing expected/installed root pre-commit hooks, and missing `promotion_gate_v02` / `check_layer_freeze` tokens in the `sapianta_system` hook.
- Full suite: not rerun. The committed R02 result remains 6,621 passed and 4 skipped; current focused evidence is consistent with it.
- Live PTY workflow: not run.

## Governance result

Governance remains `PARTIALLY_CONFORMANT`. This audit does not upgrade the repository to full conformance and does not hide the two pre-existing hook mismatches. The result preserves replay safety, authority separation, fail-closed behavior, mutation boundaries, and the non-live source-repository boundary.

## Git status and protected paths

Exact final parent status:

```text
## master...origin/master [ahead 64]
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/diagnostic_evidence.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/governed_return.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/lineage.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stderr.txt
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stdout.txt
 M .runtime/aigol/ledger/governed_returns.jsonl
?? WORKER_INVOCATION_ARTIFACT_V1
?? WORKER_INVOKED
?? docs/governance/G31_24G_R04_R04_R03_HARDENED_REPLACE_OWNER_LIVE_REACHABILITY_AUDIT.md
?? invocation
```

No file is staged. All three nested repositories remain clean: `sapianta-domain-credit` is `main...origin/main`; `sapianta_system` is `feature/governance-evolution-loop...origin/feature/governance-evolution-loop [ahead 2]`; and `sapianta-domain-trading` is `main...origin/main`.

The nine protected paths were not modified, staged, restored, normalized, deleted, or cleaned by this task. Their closing SHA-256 values exactly equal the values recorded before analysis. No authorization, consumption, Worker, command, mutation, restoration, recovery, completion, or termination evidence was created in the source repository; no `G31_EXISTING_FILE_REPLACE_V2` or `G31_MUTATION_AUTHORIZATION_REPLAY_V1` directory exists under `.runtime/aigol`.

## Documentation-only commit commands

No commit was created. If accepted, the exact scoped commands are:

```bash
git add docs/governance/G31_24G_R04_R04_R03_HARDENED_REPLACE_OWNER_LIVE_REACHABILITY_AUDIT.md
git commit -m "docs(governance): audit hardened replace live reachability"
```

These commands exclude every protected path.

## Evidence-scoped progress

- G31 conversational reachability: 99.9%.
- Whole-project progress: 97.9%.

The physical owner is certified but non-live. This audit resolves the exact reachability boundary; it does not advance physical mutation reachability.

## Exactly one next state

`G31_24G_R04_R04_R04_AICLI_V3_MUTATION_DECISION_TRANSPORT_BINDING_REQUIRED`

## Complete bounded next prompt

```text
# Generation 31-24G-R04-R04-R04 — AiCLI V3 Mutation Decision Transport Binding

Repository: /home/pisarna/work/sapianta

Required committed baseline:
- docs/governance/G31_24G_R04_R04_R03_HARDENED_REPLACE_OWNER_LIVE_REACHABILITY_AUDIT.md
- required verdict: G31_HARDENED_REPLACE_OWNER_LIVE_BINDING_REQUIRED

Stop without changing files if the report or verdict is not committed. Record branch, HEAD, status, recent log, protected hashes, and nested-repository cleanliness. Preserve Generation 30 and committed G31-02 through R03 as immutable accepted baselines.

Objective:
Bind only the existing AiCLI accepted-V2-candidate stop to the existing public V3 human mutation-decision owner. After exact accepted content and exact replay-reconstructed V2 candidate creation, prepare and present one HUMAN_MUTATION_DECISION_CONTEXT_PRESENTED_V3; collect exactly one APPROVED or REJECTED decision for decision_type=MUTATION_AUTHORIZATION and decision_scope=EXISTING_FILE_REPLACE_ONLY; record and independently reconstruct the existing four-step V3 Replay; render the truthful result; retain all authentic captures in runtime_result; and stop.

Required production call edge:
aigol/cli/aicli.py::run_reference_uhi_session
-> aigol/runtime/human_decision_runtime.py::prepare_existing_file_mutation_decision_context
-> record_existing_file_mutation_decision
-> reconstruct_existing_file_mutation_decision_replay
-> existing V3 renderers

Use only the already-retained candidate, acceptance, content-decision, prerequisite-binding, activation, governed-execution, execution-candidate, session, workspace, and publicly reconstructed repository-grounding evidence. Do not accept supplemental plain provenance dictionaries. AiCLI remains transport/presentation only and must not infer, normalize, own, or automatically approve the decision.

Success stop state for APPROVED:
result_accepted=true
existing_file_mutation_candidate_created=true
human_mutation_decision_recorded=true
mutation_decision_approved=true
mutation_authorized=false
authorization_actor_bound=false
authorization_replay_recorded=false
authorization_consumed=false
replace_request_created=false
worker_invoked=false
provider_invoked=false
command_executed=false
repository_mutated=false
main_repository_mutated=false

REJECTED must record and reconstruct the exact rejected V3 decision and create no authorization or downstream evidence.

Do not call authorize_g31_approved_existing_file_mutation, bind_g31_mutation_authorization_actor_and_replay, create_g31_authenticated_replace_request, execute_g31_authenticated_replace, recover_g31_authenticated_replace, any Worker/Provider/command owner, or any mutation/recovery owner. Do not add an execution trigger, authorization presentation, request presentation, live caller, router, parallel decision/Replay system, or new canonical artifact family. Do not mutate /home/pisarna/work/sapianta or run a live PTY workflow.

Limit production changes to aigol/cli/aicli.py unless an existing presentation-only owner requires one additional bounded production file. Add focused tests for APPROVED, REJECTED, invalid vocabulary, wrong actor, changed candidate/Replay/repository/session evidence, duplicate decision, EOF/pending state, authentic runtime_result retention, exact presentation, and proof that all authorization/request/Worker/mutation/recovery callables remain uncalled. Reuse existing fixtures; all writes must be session Replay under pytest temporary directories. Preserve V1/V2 decisions and prior AiCLI behavior.

Run the focused R01 candidate/AiCLI suite, V3 decision suite, new transport suite, Governance tests, targeted py_compile, parent/nested git diff --check, protected-hash comparison, and nested statuses. Do not rerun the full suite unless focused evidence conflicts with committed certification. Create one governance report, do not stage or commit, and return exactly one next state that keeps evidence-only canonical authorization separate from authenticated request construction and physical execution.
```
