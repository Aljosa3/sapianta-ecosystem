# Generation 31-24G-R04-R04-R05 Canonical APPROVED V3 Decision to Mutation Authorization Binding

Status: operational, bounded, adapter-independent, and stopped before request construction.

Date: 2026-07-21

Deterministic verdict:

`G31_CANONICAL_APPROVED_V3_DECISION_TO_MUTATION_AUTHORIZATION_BINDING_OPERATIONAL`

Exactly one next state:

`G31_24G_R04_R04_R06_MUTATION_AUTHORIZATION_TO_AUTHENTICATED_REPLACEMENT_REQUEST_BINDING_REQUIRED`

## Constitutional scope

This generation treats Generation 30 and the accepted G31 common-entry repair
as immutable. It extends only the shared application sequence after the exact
reconstructed V3 mutation decision. It changes no V3 decision, authorization
record, authorization actor, Replay, candidate, grounding, Worker, Provider,
request, replacement, restoration, rollback, or recovery owner.

The certified dependency direction remains:

```text
adapter
-> run_human_interface_runtime_entry
-> shared G31 application transition
-> canonical runtime and domain owners
-> canonical Replay, lifecycle state, and presentation
-> adapter-specific rendering
```

AiCLI remains a narrow transport adapter. No live PTY workflow was run, as the
R05 specification explicitly prohibited it.

## Baseline and initial worktree

```text
branch: master
baseline HEAD: 8a9aa3e27873461ff87861968f4f36f2438ca41c
baseline subject: fix(runtime): restore certified common entry and narrow AiCLI adapter
git diff --check: passed
```

The committed authoritative report
`G31_24G_R04_R04_R04_R01_COMMON_ENTRY_POINT_AND_NARROW_ADAPTER_ARCHITECTURE_REPAIR.md`
was read completely before implementation. It contains both required markers:

- `G31_COMMON_ENTRY_POINT_AND_NARROW_ADAPTER_ARCHITECTURE_REPAIRED`;
- `G31_24G_R04_R04_R05_CANONICAL_APPROVED_V3_DECISION_TO_MUTATION_AUTHORIZATION_BINDING_REQUIRED`.

Initial parent dirt consisted only of the six protected tracked evidence paths
and three protected untracked empty markers listed below. The tracked initial
diff was 97 additions and 4 deletions across the six protected paths. No R05
production or test change existed initially.

Recent Git history placed the committed R01 repair directly at HEAD. No commit
was created during R05.

## Protected pre-existing state

The following paths remained untouched by R05:

| Protected path | Initial and final SHA-256 |
| --- | --- |
| `diagnostic_evidence.json` | `a626a69a8020bc730876119c52701a94de9ab6e4772cc64c1f5d017296650203` |
| `governed_return.json` | `e82f47c0c13678725993b21e2af2e0437edccaed324f861a7b58e77d7f8e787d` |
| `lineage.json` | `07b95505521e70f51cdddecc1057fd3a208b198445693c9a8da1e996df5799dd` |
| `provider_stderr.txt` | `d47a06d59aba2814c3fb7460049fc2ccbfc834196c956d6c6558e8be8b079e24` |
| `provider_stdout.txt` | `a73a499e2e9133c03d7babfd5c4dec7967f31e2bfb354ea9dd41df0a15c08cb3` |
| `.runtime/aigol/ledger/governed_returns.jsonl` | `dbc7b63f2a17c50c43bbb4fde4f44c1dbae8d25d550fb6b4d4daa14e17126161` |
| `WORKER_INVOCATION_ARTIFACT_V1` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `WORKER_INVOKED` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `invocation` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

The first five names above are under
`.runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/`.

## Prior and new lifecycle boundaries

The certified R01 boundary was:

```text
V2 existing-file candidate
-> pending V3 mutation-decision context
-> exact APPROVED or REJECTED
-> canonical V3 decision recording
-> four-step V3 Replay reconstruction
-> canonical presentation
-> stop before mutation authorization
```

R05 extends only exact `APPROVED`:

```text
exact reconstructed APPROVED V3 decision
-> existing R02 authorization binding owner
-> existing R02 authorization reconstruction
-> existing canonical actor and authorization-Replay binder
-> existing authorization-Replay reconstruction
-> canonical application-state projection and presentation
-> stop before authenticated replacement request construction
```

Exact `REJECTED` remains:

```text
exact reconstructed REJECTED V3 decision
-> canonical rejected decision and four-step Replay retained
-> terminal canonical presentation
-> zero authorization calls
```

## Existing canonical owners reused

No new authorization artifact family or framework was introduced.

| Responsibility | Existing owner reused |
| --- | --- |
| V3 decision recording, validation, and four-step Replay | `aigol.runtime.human_decision_runtime` |
| V2 candidate validation and reconstruction | `aigol.runtime.platform_core_existing_file_mutation_candidate` |
| Exact V3/V2/activation/grounding authorization subject | `platform_core_existing_file_governance._g31_authorization_subject` |
| Canonical authorization creation | `authorize_g31_approved_existing_file_mutation` using `create_authorization_record` and `validate_authorization_record` |
| R02 authorization reconstruction | `reconstruct_g31_existing_file_mutation_authorization_binding` |
| Canonical authorization actor and immutable Replay binding | `bind_g31_mutation_authorization_actor_and_replay` |
| Authorization Replay reconstruction | `reconstruct_g31_mutation_authorization_actor_and_replay` and `authorization_runtime.reconstruct_existing_authorization_binding_replay` |
| Application sequencing and canonical lifecycle projection | `run_human_interface_runtime_entry` and its existing shared G31 transition |
| Human-facing application presentation selection | existing common-entry canonical presentation output |
| Terminal translation, caching, and rendering | unchanged AiCLI adapter |

The common entry performs application ordering only. All authorization
authenticity, actor, policy, hashing, session, repository, grounding,
provenance, Replay, and duplicate-destination semantics remain in the existing
domain owners.

## Exact application transition symbol

The only public application transition remains:

`aigol.runtime.human_interface_runtime_entry_service.run_human_interface_runtime_entry`

One private sequencing symbol was added inside that existing owner:

`_authorize_g31_mutation_decision`

Its responsibility is limited to projecting already-retained canonical state
into the four existing public authorization calls, retaining the returned
captures and reconstructions, and projecting their lifecycle flags. It does
not validate a domain decision, create an authorization record directly,
write Replay directly, construct a request, consume authorization, or call a
Worker or Provider.

## Adapter-neutral input and output

The transition consumes the existing adapter-neutral inputs:

- session identity and canonical session root;
- workspace identity;
- creation timestamp;
- prior canonical G31 application state;
- exact neutral action `APPROVED` or `REJECTED`;
- neutral human mutation-decision actor.

It returns existing application fields plus, only for exact `APPROVED`:

- `mutation_authorization_capture`;
- `mutation_authorization_reconstruction`;
- `mutation_authorization_actor_replay_capture`;
- `mutation_authorization_actor_replay_reconstruction`;
- canonical authorization identity and hash;
- canonical lifecycle flags and Replay reference;
- one canonical authorization presentation.

Terminal prompt strings, slash commands, interface names, EOF behavior, and
rendering syntax do not enter the authorization record, R02 subject, actor
binding, or Replay hash.

## APPROVED evidence and bindings

The exact approved sequence consumes unchanged:

- activation capture and independent activation reconstruction;
- activation approval identity, artifact hash, and Replay hash;
- repository grounding artifact and hash;
- accepted V2 candidate, candidate Replay, and provenance binding;
- accepted-content and prerequisite lineage;
- exact V3 decision artifact and four-step decision Replay reconstruction;
- session root and workspace identity.

The R02 authorization subject retains:

- exact session;
- repository grounding hash;
- candidate ID, artifact hash, Replay reference/hash, and provenance hash;
- V3 decision ID, artifact hash, Replay reference/hash, and exact `APPROVED`;
- operation, target path, preimage SHA-256, and postimage SHA-256.

The unchanged canonical authorization record retains candidate ID as proposal
ID, the existing replace Worker, existing replace scope, `AUTHORIZED` status,
timestamp, and canonical authorization hash. Exactly one call to
`create_authorization_record` was observed.

The actor/Replay binding retains the unchanged record, canonical actor
`governed_authorization_runtime`, human V3 actor separately, activation,
candidate, decision, target, expected preimage, R02 binding hash, and false
downstream flags. Its deterministic three-step Replay is:

```text
<session>/G31_MUTATION_AUTHORIZATION_REPLAY_V1/
  000_authorization_owner_resolved.json
  001_authorization_binding_recorded.json
  002_authorization_returned.json
```

Public reconstruction recomputes all upstream evidence and validates those
three wrappers before the common entry projects the result.

## REJECTED zero-authorization evidence

Focused common-entry and AiCLI compatibility evidence proves that exact
`REJECTED`:

- records and reconstructs the authentic V3 decision;
- returns `mutation_decision_approved=false`;
- retains `mutation_authorized=false`;
- retains `authorization_actor_bound=false`;
- retains `authorization_replay_recorded=false`;
- invokes neither authorization nor actor/Replay binding owner;
- creates no authorization Replay directory;
- creates no request and performs no downstream call.

## Fail-closed and duplicate evidence

Focused public-entry evidence proves failure for:

- wrong human actor;
- changed workspace/repository identity;
- changed session identity;
- changed claimed V2 candidate reconstruction;
- changed activation reconstruction;
- changed repository grounding;
- V3 decision-Replay substitution between initial reconstruction and the
  authorization owner's independent reconstruction;
- repeated public transition using the same pending V3 context.

The duplicate transition fails at the immutable V3 decision destination before
a second authorization owner call. The existing authorization owner suites
additionally prove candidate, decision, candidate Replay, activation,
provenance, path, preimage, record, actor, Replay ordering, wrapper, and
cross-session substitution rejection, plus exclusive duplicate authorization
Replay rejection.

Invalid or legacy vocabulary remains rejected at the earlier V3 boundary and
cannot reach R05.

## UI-independent and non-AiCLI proof

The focused `InMemoryAdapter` calls only
`run_human_interface_runtime_entry`. It imports no AiCLI module and copies no
low-level sequence. Through the same public entry it proves:

- `APPROVED` reaches one canonical authorization and actor-bound Replay;
- `REJECTED` remains terminal with zero authorization calls;
- canonical authorization meaning and hashing are supplied by the same owners;
- injected `terminal_prompt` and `slash_command` fields are absent from all
  authorization and actor-Replay evidence.

Static checks confirm that AiCLI contains neither
`authorize_g31_approved_existing_file_mutation(` nor
`bind_g31_mutation_authorization_actor_and_replay(`. AiCLI continues to call
only the common application entry for this transition. Canonical runtime
modules import no `aigol.cli` module.

## Presentation and lifecycle ownership

The common entry first renders the existing V3 human-decision presentation.
For exact `APPROVED`, it then selects one bounded canonical authorization
presentation containing the reconstructed authorization ID, status, canonical
actor, target, Replay-recorded status, and truthful stop-state flags.

The aggregate state is projected from the existing actor/Replay reconstruction,
not independently reinterpreted:

```text
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

For `REJECTED`, the pre-existing decision presentation remains the terminal
presentation and every authorization flag remains false.

## Before-and-after call graph

Before R05:

```text
adapter action
-> run_human_interface_runtime_entry
-> record V3 decision
-> reconstruct four-step V3 Replay
-> canonical decision presentation
-> stop before authorization
```

After R05:

```text
adapter action
-> run_human_interface_runtime_entry
-> record and reconstruct V3 decision
-> if REJECTED: terminal presentation and stop
-> if APPROVED:
     authorize_g31_approved_existing_file_mutation
     -> reconstruct_g31_existing_file_mutation_authorization_binding
     -> bind_g31_mutation_authorization_actor_and_replay
     -> reconstruct_g31_mutation_authorization_actor_and_replay
     -> aggregate canonical state and presentation
     -> stop before create_g31_authenticated_replace_request
```

## Forbidden downstream zero-call evidence

Focused spies remain zero for:

- authenticated replacement request construction;
- hardened replace execution and recovery;
- public and private filesystem replace Worker entry points;
- authorization consumption;
- Provider invocation;
- command execution;
- repository mutation;
- restoration, rollback, and recovery.

The in-memory fixture invokes no Worker or Provider at any stage. The AiCLI
compatibility fixture retains its one pre-existing bounded CODEX activation
needed to produce the candidate, and R05 adds no Worker or Provider call.
Temporary Git workspace status remains clean, source bytes remain unchanged,
and no `G31_EXISTING_FILE_REPLACE_V2` destination is created.

## Changed files and size

Production:

- `aigol/runtime/human_interface_runtime_entry_service.py`: 127 additions,
  0 deletions. It adds one import, one APPROVED branch call and presentation,
  and one private application sequencer. No other production file changed.

Tests:

- `tests/test_g31_24g_r04_r04_r05_canonical_v3_to_mutation_authorization.py`:
  292 new lines for 11 focused cases;
- `tests/test_g31_24g_r04_r04_r04_r01_common_entry_adapter_repair.py`:
  53 additions, 4 deletions to extend the existing in-memory fixture and
  preserve its common-entry proof at the new boundary;
- `tests/test_g31_24g_r04_r04_r04_aicli_v3_mutation_decision_transport.py`:
  30 additions, 7 deletions to observe the newly permitted authorization calls
  while retaining zero downstream-call assertions.

Test delta: 375 additions and 11 deletions. No helper was copied into
production, no new production module was introduced, and no existing
authorization or Replay owner required modification.

Documentation:

- this single R05 report: 553 lines.

## Validation

Validation commands overlap and are not added together:

| Group | Result |
| --- | --- |
| New focused R05 suite | 11 passed, 0 skipped, 0 failed |
| Final post-minimality R05 plus R01 common-entry suite | 15 passed, 0 skipped, 0 failed |
| R01 common entry, R04 transport, R02 authorization, and actor-Replay compatibility | 34 passed, 0 skipped, 0 failed |
| V3 human decision and V2 candidate Replay | 11 passed, 0 skipped, 0 failed |
| G0-G30 UHI, common entry, conversation, AiCLI, and presentation | 53 passed, 0 skipped, 0 failed |
| Affected G31 assignment-through-acceptance compatibility | 61 passed, 0 skipped, 0 failed |
| Architecture and Governance conformance tests | 20 passed, 0 skipped, 0 failed |
| Full repository suite | **6,640 passed, 4 skipped, 0 failed** in 4,419.36 seconds |
| Targeted `py_compile` | passed |
| Parent and nested `git diff --check` | passed |
| Protected hash comparison | all nine exact |

The full repository suite was run exactly once after all focused suites passed.
No live PTY workflow was run.

## Governance result

Governance remains visibly `PARTIALLY_CONFORMANT`:

```text
checks_passed: 18
checks_failed: 2
critical_violations: 0
deterministic: true
fail_closed: true
read_only: true
report_hash: 0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea
```

The known missing root pre-commit hook and missing system-hook
`promotion_gate_v02` / `check_layer_freeze` tokens remain visible. R05 neither
repairs nor hides them.

## Nested repositories

Final nested status remains clean:

- `sapianta-domain-credit`: `main` at
  `8615e1e290471a67e4e764c6ab2138340bc7936f`;
- `sapianta_system`: `feature/governance-evolution-loop` at
  `3183bab71f8f30397c0309dd2e6d846d14a11f66`;
- `sapianta-domain-trading`: `main` at
  `d3038dc4ba36ffbaee9161172b4c852e8e6acbda`.

## Final parent Git status

The exact final parent status contains the nine protected paths plus exactly
five R05-scoped paths:

```text
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/diagnostic_evidence.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/governed_return.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/lineage.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stderr.txt
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stdout.txt
 M .runtime/aigol/ledger/governed_returns.jsonl
 M aigol/runtime/human_interface_runtime_entry_service.py
 M tests/test_g31_24g_r04_r04_r04_aicli_v3_mutation_decision_transport.py
 M tests/test_g31_24g_r04_r04_r04_r01_common_entry_adapter_repair.py
?? WORKER_INVOCATION_ARTIFACT_V1
?? WORKER_INVOKED
?? docs/governance/G31_24G_R04_R04_R05_CANONICAL_APPROVED_V3_DECISION_TO_MUTATION_AUTHORIZATION_BINDING.md
?? invocation
?? tests/test_g31_24g_r04_r04_r05_canonical_v3_to_mutation_authorization.py
```

The protected paths remain separately visible in `git status --short`. Nothing
is staged and no commit was created.

## Scoped commit commands

```bash
git add aigol/runtime/human_interface_runtime_entry_service.py
git add tests/test_g31_24g_r04_r04_r04_aicli_v3_mutation_decision_transport.py tests/test_g31_24g_r04_r04_r04_r01_common_entry_adapter_repair.py tests/test_g31_24g_r04_r04_r05_canonical_v3_to_mutation_authorization.py
git add docs/governance/G31_24G_R04_R04_R05_CANONICAL_APPROVED_V3_DECISION_TO_MUTATION_AUTHORIZATION_BINDING.md
git commit -m "feat(governance): bind V3 decision to mutation authorization"
```

The protected paths are intentionally absent.

## Progress and conclusion

- G31 no-copy/paste conversational reachability: **99.94%**;
- architecture-safe G31 integration: **100% through reconstructed mutation authorization**;
- whole-project evidence-scoped estimate: **97.9%**.

These are planning estimates, not certification claims. The exact remaining
boundary is authenticated replacement-request construction from the already
reconstructed authorization. Authorization consumption and physical mutation
remain deliberately unreachable.

`G31_CANONICAL_APPROVED_V3_DECISION_TO_MUTATION_AUTHORIZATION_BINDING_OPERATIONAL`

`G31_24G_R04_R04_R06_MUTATION_AUTHORIZATION_TO_AUTHENTICATED_REPLACEMENT_REQUEST_BINDING_REQUIRED`

## Complete bounded next Codex prompt

```text
# Generation 31-24G-R04-R04-R06
# Mutation Authorization to Authenticated Replacement Request Binding

Treat Generation 30, the accepted common-entry repair, and R05 as immutable.

Required R05 verdict:
G31_CANONICAL_APPROVED_V3_DECISION_TO_MUTATION_AUTHORIZATION_BINDING_OPERATIONAL

Required current state:
G31_24G_R04_R04_R06_MUTATION_AUTHORIZATION_TO_AUTHENTICATED_REPLACEMENT_REQUEST_BINDING_REQUIRED

Objective:
Consume only the exact reconstructed R05 mutation authorization context through
the same public run_human_interface_runtime_entry application boundary and
construct the existing canonical authenticated replacement request.

First inspect and document the existing contracts for:
- create_g31_authenticated_replace_request;
- validate_authenticated_replace_request_v2;
- the R05 authorization capture, actor-bound Replay, and reconstruction;
- accepted candidate provenance and implementation-manifest exact bytes;
- deterministic replace destinations;
- common-entry lifecycle state and canonical presentation.

Reuse those contracts. Do not create a new request family, authorization
system, Replay subsystem, router, Worker, Provider, mutation owner, adapter
sequence, or path/hash helper.

Required behavior:
- only exact reconstructed, actor-bound, unconsumed R05 authorization may
  create exactly one existing authenticated replacement request;
- request scope must exactly equal repository/session/grounding, candidate,
  provenance, decision, authorization, target, preimage/postimage bytes and
  hashes, operation, file modes, Worker, and deterministic destinations;
- REJECTED, absent, consumed, duplicated, stale, reordered, substituted,
  cross-session, broadened, or hash-invalid evidence fails closed;
- AiCLI remains transport-only and a non-AiCLI adapter reaches the same result
  through the common entry.

Mandatory stop after request validation and presentation:
mutation_authorized=true;
authorization_actor_bound=true;
authorization_replay_recorded=true;
replace_request_created=true;
authorization_consumed=false;
worker_invoked=false;
provider_invoked=false;
command_executed=false;
repository_mutated=false;
main_repository_mutated=false.

Do not call execute_g31_authenticated_replace,
_execute_authenticated_replace_v2, any authorization-consumption boundary,
filesystem replacement, restoration, rollback, recovery, completion, or
termination owner. Do not mutate any target repository. Do not run a live PTY
workflow unless a later prompt explicitly requires it.

Prefer one bounded call from the existing common-entry sequencer. If the
existing request contract cannot consume exact R05 evidence within at most
three production files and without architecture change, stop at the first
exact incompatibility and return a blocked verdict rather than partially
implementing.

Add focused exact-request, REJECTED, duplicate, tamper, cross-session,
byte/hash/mode/destination, Replay, stop-boundary, AiCLI narrowness, and
in-memory adapter tests. Use only pytest temporary session roots and disposable
Git repositories. Run focused suites, R05/common-entry/interface compatibility,
request-owner and Replay tests, Governance, py_compile, diff/hash checks, then
the full suite once after focused validation passes.

Create exactly one R06 governance report. Preserve all protected paths and the
known PARTIALLY_CONFORMANT findings. Do not stage or commit. Return one
deterministic verdict and exactly one next state.
```
