# Generation 31-24G-R04-R04-R14A G31 Invocation Operational Readiness Audit

Status: completed static constitutional audit; no Invocation or later
execution stage was performed.

Date: 2026-07-23

Deterministic verdict:

`G31_INVOCATION_OPERATIONAL_READY`

First deterministic constitutional blocker:

`NONE`

Exactly one next state:

`G31_24G_R04_R04_R14B_COMMON_ENTRY_TO_INVOCATION_OPERATIONAL_TRANSITION_REQUIRED`

## Constitutional scope

This generation treats G0-G30 Platform Core and the accepted G31 Assignment,
Dispatch-readiness, and Common Entry-to-Dispatch results as immutable
certified baselines.

It performs only a static repository-evidence assessment of whether the exact
R13B `WORKER_DISPATCH_ARTIFACT_V1` and Dispatch Replay can be consumed by the
existing certified current-chain Invocation owner.

It does not:

- call `invoke_dispatched_worker`;
- create Invocation evidence;
- write or reconstruct a newly created Invocation Replay;
- start a Worker process;
- execute a Worker;
- invoke a Provider;
- execute a command;
- open a mutation target;
- mutate a repository;
- modify a registry or certification artifact;
- modify any production or test file;
- stage files; or
- create a commit.

Exactly one governance report is added.

## Accepted baseline

The audit began from:

- branch: `master`;
- HEAD: `acafdfc0f6b5e62fd76521457a6b5e37ec779f5b`;
- HEAD subject:
  `feat(runtime): bind common entry to certified dispatch transition`;
- R12B verdict:
  `G31_COMMON_ENTRY_TO_ASSIGNMENT_OPERATIONAL`;
- R13A verdict:
  `G31_DISPATCH_OPERATIONAL_READY`;
- R13B verdict:
  `G31_COMMON_ENTRY_TO_DISPATCH_OPERATIONAL`;
- certified Dispatch runtime:
  `AIGOL_WORKER_DISPATCH_RUNTIME_V1`;
- certified Invocation runtime:
  `AIGOL_WORKER_INVOCATION_RUNTIME_V1`.

The worktree was clean at the audit boundary. The R13B production and
regression delta is committed at the accepted HEAD.

## Plain determination

The existing current-chain Invocation owner is directly compatible with the
exact R13B Dispatch artifact and Replay.

The compatibility is direct because `invoke_dispatched_worker` already:

1. accepts `WORKER_DISPATCH_ARTIFACT_V1`;
2. accepts its exact Replay reference;
3. reconstructs the four-step Dispatch Replay;
4. validates the supplied Dispatch identity and artifact hash against Replay;
5. validates Assignment, request, authorization, packet, Worker, chain,
   Replay, and authority continuity;
6. propagates allowed outputs, forbidden operations, and validation
   requirements;
7. creates the existing Invocation artifact family; and
8. stops with Worker execution, result creation, Governance mutation, and
   existing-Replay mutation false.

No new Invocation runtime, entrypoint, adapter path, Worker-specific branch,
artifact family, Replay family, selector, registry, or authority owner is
required.

## Existing certified Invocation contract

The certified owner is:

```text
aigol.runtime.worker_invocation_runtime.invoke_dispatched_worker
```

Its canonical input is:

- one non-empty Invocation identity;
- one exact `WORKER_DISPATCH_ARTIFACT_V1`;
- the exact Dispatch Replay reference;
- one bounded invoking actor;
- one timestamp; and
- one unused Invocation Replay destination.

Its existing output family is:

```text
WORKER_INVOCATION_EVIDENCE_ARTIFACT_V1
WORKER_INVOCATION_CLASSIFICATION_ARTIFACT_V1
WORKER_INVOCATION_ARTIFACT_V1
WORKER_INVOCATION_RESULT_ARTIFACT_V1
```

Its successful state is:

```text
invocation_status = WORKER_INVOKED
worker_assigned = true
worker_dispatched = true
dispatch_requested = true
worker_invoked = true
execution_started = false
result_created = false
result_validated = false
post_execution_replay_reviewed = false
terminated = false
governance_mutated = false
replay_mutated = false
```

The runtime records invocation lifecycle evidence. Its canonical presentation
explicitly states that no Worker process or execution has started, no command
has executed, no result has been produced, and no repository has been
modified.

## Exact R13B Dispatch input

R13B returns the exact existing Dispatch capture and exposes:

```text
worker_dispatch_capture
worker_dispatch_reconstruction
worker_dispatch_status = WORKER_DISPATCHED
worker_dispatch_id
worker_dispatch_replay_reference
worker_dispatch_replay_hash
worker_assigned = true
worker_dispatched = true
dispatch_requested = true
worker_invoked = false
execution_started = false
result_created = false
governance_mutated = false
replay_mutated = false
```

The returned `worker_dispatch_artifact` contains every required Invocation
input:

- Dispatch identity and artifact hash;
- Dispatch evidence and classification references/hashes;
- exact Assignment identity and hash;
- exact invocation-request identity and hash;
- exact authorization identity and hash;
- exact execution-packet identity and hash;
- target domain;
- Worker identity and hash;
- Worker family and role;
- allowed outputs;
- forbidden operations;
- validation requirements;
- Dispatch actor and timestamp;
- Assignment status before Dispatch;
- Worker state before Dispatch;
- canonical chain identity;
- Replay reference; and
- exact pre-Invocation authority flags.

No required field is absent, aliased, synthesized, or incompatible.

## Exact compatibility matrix

| Invocation requirement | R13B source | Classification |
|---|---|---|
| Artifact type | `WORKER_DISPATCH_ARTIFACT_V1` | exact |
| Dispatch status | `WORKER_DISPATCHED` | exact |
| Assignment status | `WORKER_ASSIGNED` | exact |
| Worker state | `ASSIGNED` | exact |
| Dispatch identity | certified Dispatch artifact | exact |
| Dispatch hash | certified artifact hash | exact |
| Dispatch Replay | returned R13B Replay reference | exact |
| Assignment identity/hash | R12B lineage in Dispatch | preserved |
| Request identity/hash | R09B lineage in Dispatch | preserved |
| Authorization identity/hash | R05-R10 lineage in Dispatch | preserved |
| Packet identity/hash | authenticated request scope | preserved |
| Worker identity/hash | certified selected Worker | exact |
| Worker family/role | certified Worker artifact | exact |
| Allowed outputs | Assignment-to-Dispatch projection | present |
| Forbidden operations | Assignment-to-Dispatch projection | present |
| Validation requirements | Assignment-to-Dispatch projection | present |
| Canonical chain | request through Dispatch | exact |
| Worker already invoked | false | compatible |
| Execution started | false | compatible |
| Result created | false | compatible |
| Governance mutated | false | compatible |
| Existing Replay mutated | false | compatible |

## Dispatch Replay continuity

Before constructing Invocation evidence, `_load_dispatch_lineage` calls the
existing `reconstruct_worker_dispatch_replay`.

It then requires the exact four Dispatch wrappers:

```text
000_dispatch_evidence_recorded.json
001_dispatch_classification_recorded.json
002_dispatch_artifact_recorded.json
003_dispatch_result_recorded.json
```

For each wrapper it verifies:

- exact index and step order through the Dispatch reconstructor;
- wrapper hash;
- artifact type and artifact hash;
- evidence-to-classification continuity;
- classification-to-Dispatch continuity;
- Dispatch-to-result continuity;
- canonical chain agreement;
- Assignment identity/hash agreement; and
- complete nested Assignment and invocation-request Replay continuity.

The Invocation owner additionally compares the supplied Dispatch identity and
hash with the reconstructed Dispatch artifact. Substitution of either fails
closed.

The lineage checks require:

```text
dispatch_lineage = true
assignment_lineage = true
invocation_request_lineage = true
authorization_lineage = true
execution_packet_lineage = true
worker_identity_continuity = true
chain_continuity = true
replay_continuity = true
authority_continuity = true
```

No R05-R13B parent Replay event must be rewritten, repeated, consumed again,
or reauthorized.

## Invocation Replay continuity

The existing Invocation owner persists exactly:

```text
000_invocation_evidence_recorded.json
001_invocation_classification_recorded.json
002_invocation_artifact_recorded.json
003_invocation_result_recorded.json
```

`reconstruct_worker_invocation_replay` verifies:

- exact wrapper order;
- wrapper hashes;
- all four Invocation artifact hashes;
- evidence-to-classification continuity;
- classification-to-Invocation continuity;
- Invocation-to-result continuity;
- chain agreement;
- Dispatch identity/hash agreement;
- complete nested Dispatch Replay reconstruction;
- authority continuity; and
- the post-Invocation stop boundary.

This is the existing certified Replay family. R14A finds no need for a new
Replay subsystem or compatibility adapter.

## Authority continuity

The R13B Dispatch authority boundary is exactly the Invocation precondition:

```text
approval_created = false
worker_assigned = true
worker_dispatched = true
dispatch_requested = true
worker_invoked = false
execution_started = false
result_created = false
governance_mutated = false
replay_mutated = false
```

The Invocation transition changes only the lifecycle invocation state:

```text
worker_invoked: false -> true
```

It does not grant:

- Worker execution authority;
- Provider authority;
- command authority;
- result-validation authority;
- result-approval authority;
- post-execution Replay-review authority;
- termination authority;
- Governance mutation authority; or
- authority to modify an existing Replay.

Invocation evidence remains distinct from Worker execution. A later
operational generation must still stop before execution or result capture.

## Worker and capability neutrality

The current-chain `invoke_dispatched_worker` path has no branch for:

- `FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER`;
- `REPLACE_EXISTING_TEXT_FILE`;
- CODEX;
- CLAUDE_CODE; or
- any Provider identity.

It consumes the Worker identity, family, role, outputs, prohibitions, and
validation requirements already certified in Dispatch.

The certified Invocation architecture therefore accepts the exact filesystem
replacement Worker without mapping it to CODEX, a generic implementation
Worker, a Provider, or an alias.

## Common Entry and Human Interface compatibility

`run_human_interface_runtime_entry` remains the public application owner.

The R13B mutation continuation currently stops after verified Dispatch. That
stop is correct for the accepted baseline and was not changed by this audit.

The same Common Entry service already imports `worker_invocation_runtime` and
uses `invoke_dispatched_worker` in an older certified G31 lifecycle path. A
later bounded mutation-continuation binding can reuse that call pattern
without creating:

- an adapter-owned Invocation;
- a second Common Entry;
- a parallel Invocation owner;
- Worker-specific Invocation logic; or
- an additional execution path.

Because Common Entry already holds the exact Dispatch capture and Replay
reference, it must pass those values directly. It must not use
`find_latest_domain_worker_dispatch`, infer identity from presentation fields,
or search for a substitute Dispatch.

AiCLI remains transport and presentation only.

## Minimal later operational transition

No constitutional repair is required.

The smallest later operational generation should:

1. remain inside the existing Common Entry mutation continuation;
2. retain the exact verified R13B Dispatch capture and reconstruction;
3. call `invoke_dispatched_worker` once with:
   - `<worker_dispatch_id>:INVOCATION`;
   - the exact `worker_dispatch_artifact`;
   - the exact Dispatch Replay reference;
   - one bounded Governance actor;
   - the existing transition timestamp; and
   - one unused deterministic session-local Invocation Replay destination;
4. require `WORKER_INVOKED`;
5. call `reconstruct_worker_invocation_replay` once;
6. verify Invocation identity, Dispatch identity/hash, Assignment identity,
   request, authorization, packet, Worker, chain, Replay, and stop flags;
7. aggregate the exact Invocation capture through Common Entry;
8. render the existing Invocation summary; and
9. return immediately before Worker execution or result capture.

The later implementation must prove zero calls to Worker execution, Provider,
command, target-open, filesystem replacement, result capture, result
validation, restoration, rollback, and recovery owners.

It must not modify the Invocation runtime, Dispatch runtime, Worker Registry,
artifact families, Replay families, selection, authorization, or AiCLI.

## Rejected shortcuts

The audit rejects:

- invoking from AiCLI;
- treating `selected_resource_id` as Invocation authority;
- treating the Assignment artifact as a Dispatch artifact;
- bypassing Dispatch Replay reconstruction;
- using filesystem discovery when the exact Dispatch capture is available;
- mapping the Worker to CODEX, CLAUDE_CODE, a Provider, or an alias;
- adding replacement-Worker-specific Invocation logic;
- creating a second Invocation owner or Replay family;
- changing the certified Invocation runtime without an observed blocker;
- combining Invocation with Worker execution or result capture;
- rewriting upstream authorization, request, consumption, selection,
  Assignment, or Dispatch evidence; and
- treating readiness as evidence that Invocation already occurred.

## Static validation

Validation intentionally used only source-boundary, architecture, authority,
and Governance checks that do not call Invocation or write lifecycle Replay.

Exact result:

```text
20 passed, 0 skipped, 0 failed in 0.27s
```

The group covers:

- the Invocation source stop before result validation and termination;
- R13B Common Entry stop before Invocation;
- R12B Common Entry lifecycle neutrality;
- R10B and R11B Worker-neutral compatibility;
- canonical layer contracts;
- authority-boundary contracts; and
- Governance conformance tests.

Additional read-only checks:

- in-memory source compilation passed for Invocation, Dispatch, and Common
  Entry;
- both Invocation certification JSON files parse successfully;
- parent `git diff --check`: passed;
- all three nested repository `git diff --check` checks: passed;
- complete repository suite: not run for this static audit;
- live Invocation: not called;
- Invocation Replay or certification generation: not run;
- Worker, Provider, command, target-open, and mutation workflows: not run.

The accepted R13B report records its exactly-once complete-suite result and
targeted closure. R14A does not repeat that suite.

## Governance result

The read-only conformance engine remains:

`PARTIALLY_CONFORMANT`

- checks passed: 18;
- checks failed: 2;
- critical violations: 0;
- deterministic: true;
- fail-closed: true;
- read-only: true;
- report hash:
  `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea`.

The two known findings remain visible and unchanged:

1. the root expected and installed hooks are missing; and
2. the system pre-commit hook lacks `promotion_gate_v02` and
   `check_layer_freeze`.

R14A neither repairs nor reinterprets them.

## Protected and nested state

The six checked runtime evidence/ledger paths were not modified by this audit:

| Protected path | SHA-256 |
|---|---|
| `diagnostic_evidence.json` | `21546ed151c165c6364aa914d892c34b117ef1ab664ae09d8e2c2a5327bcc8df` |
| `governed_return.json` | `ee57877ceea7d85bd9e3bb29aca64f3637384a7346a5b6a4c4f922c87cb2bcf7` |
| `lineage.json` | `8c47abb9a7c238c9f527e54dd88aa304edbca03b97ea630a4907b4ef139b3a08` |
| `provider_stderr.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `provider_stdout.txt` | `f2fec907b48e7162211f26bbe94352d40f4f6c4380ab3aa4256d072b7c602f30` |
| `governed_returns.jsonl` | `71b085174a274b870617c21810d9a496421985675ae0945f4b56bd3afe7b1118` |

The three non-versioned zero-byte marker paths described in the R13B report
are absent from the clean committed R13B worktree. R14A is audit-only and did
not recreate or reinterpret them. Their absence is not an input to the
Dispatch-to-Invocation contract and therefore is not the first constitutional
Invocation blocker, but it remains explicitly visible as repository-state
context.

The nested repositories remain clean at:

- `sapianta-domain-credit`:
  `8615e1e290471a67e4e764c6ab2138340bc7936f`;
- `sapianta_system`:
  `3183bab71f8f30397c0309dd2e6d846d14a11f66`;
- `sapianta-domain-trading`:
  `d3038dc4ba36ffbaee9161172b4c852e8e6acbda`.

## Git state

Nothing was staged and no commit was created.

The only R14A path is:

```text
?? docs/governance/G31_24G_R04_R04_R14A_G31_INVOCATION_OPERATIONAL_READINESS_AUDIT.md
```

No production, test, registry, certification, runtime-evidence, ledger, or
nested-repository path was modified.

## Final determination

The exact R13B Dispatch artifact and Replay satisfy the existing certified
current-chain Invocation contract without a new execution path, authority
owner, Worker identity, compatibility adapter, or Replay subsystem.

No deterministic constitutional blocker exists before Invocation.

Deterministic verdict:

`G31_INVOCATION_OPERATIONAL_READY`

Exactly one next state:

`G31_24G_R04_R04_R14B_COMMON_ENTRY_TO_INVOCATION_OPERATIONAL_TRANSITION_REQUIRED`
