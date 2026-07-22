# Generation 31-24G-R04-R04-R08A Filesystem Replace Worker Selection Certification and Registry Compatibility Audit

Status: completed `AUDIT_ONLY` repository-evidence assessment; no runtime,
test, registry, or certification mutation.

Date: 2026-07-22

Deterministic verdict:

`READY_FOR_BOUNDED_SELECTION_CERTIFICATION`

Primary constitutional cause:

`missing registration`

First exact blocker:

`FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER_CERTIFIED_SELECTION_REGISTRATION_ABSENT`

Exactly one next state:

`G31_24G_R04_R04_R08B_BOUNDED_FILESYSTEM_REPLACE_WORKER_SELECTION_CERTIFICATION_REQUIRED`

## Constitutional scope

This audit treats Generation 30, accepted G31 common-entry, R05, R06, and R07
results, and the accepted R08 blocked report as immutable certified baselines.
It asks only whether the exact R07 Worker and operation can legally participate
in the existing certified Worker-selection lifecycle.

The audit changes no production file, runtime, test, registry, capability
vocabulary, alias, selection policy, certification artifact, Replay subsystem,
Worker identity, operation identity, authority model, adapter, or presentation
contract. It does not select, assign, dispatch, invoke, or execute a Worker. It
does not invoke a Provider, run a mutation workflow, open a mutation target, or
mutate a repository. No live PTY was run.

## Accepted baseline

The audit began from:

- branch: `master`;
- HEAD: `74829816a713ebd582cddcde2456784c9a61a8f0`;
- HEAD subject: `docs(governance): document R08 worker selection blocker`;
- accepted R08 verdict:
  `G31_CONSUMED_REPLACEMENT_REQUEST_TO_EXISTING_CERTIFIED_WORKER_SELECTION_BINDING_BLOCKED`;
- accepted R08 blocker:
  `R07_FIXED_REPLACEMENT_WORKER_AND_OPERATION_ABSENT_FROM_EXISTING_CERTIFIED_SELECTION_CONTRACT`.

The initial worktree contained only the nine previously declared protected
paths. The R08 report was committed and clean. This audit neither modified nor
normalized those protected paths.

## Plain-language determination

The R08 blocker is caused by a missing certified registry entry, not by an
architectural incompatibility between two Worker-selection models.

The hardened replacement Worker already has:

- one exact, stable Worker identity;
- one exact replacement operation and authorization scope;
- bounded existing-file replacement certification in the Generation 8
  certification chain;
- later G31 atomicity, single-use authorization, actor, request, and Replay
  hardening;
- an authority profile compatible with the existing
  `WORKER_AUTHORIZED_TASK_ONLY` selector profile;
- deterministic, fail-closed, reconstructable request and consumption Replay.

It does not have:

- an entry in `default_resource_registry()`;
- the exact `REPLACE_EXISTING_TEXT_FILE` capability in any selectable role
  binding;
- an exact scenario in the checked-in Worker-selection certification evidence;
- a selection-registry hash and certification report covering that entry.

An isolated temporary probe proved that the unchanged unified selector accepts
the exact Worker, operation, role, domain, and authority profile when supplied
as canonical-shaped registry metadata. The selector therefore needs no new
eligibility rule, alias, mapping, wrapper, or authority model. A bare registry
edit would nevertheless be constitutionally insufficient because the changed
registry and exact mutation-capability choice must be covered by existing
selection certification before R08 may bind live R07 evidence.

## Inspected contracts

### Hardened replacement Worker

The owner is `aigol.workers.filesystem_replace_worker`.

| Evidence | Exact value |
|---|---|
| Worker identity | `FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER` |
| Worker version | `G8_12_EXISTING_FILE_MUTATION_IMPLEMENTATION_V1` |
| operation | `REPLACE_EXISTING_TEXT_FILE` |
| authorization scope | `FILESYSTEM_REPLACE_EXISTING_TEXT_FILE` |
| current request family | `AUTHORIZED_REPLACE_EXISTING_FILE_REQUEST_V2` |
| current request state at R07 | authentic, reconstructed, authorization consumed exactly once |

The Worker accepts only its fixed identity, operation, authorization scope,
exact target and preimage, exact replacement bytes and mode, and exact upstream
lineage. It has no proposal, Governance, approval, authorization, Provider,
dispatch, or Worker-selection authority. R07 stops with Worker invocation,
command execution, target mutation, restoration, rollback, and recovery all
false.

### Certification status

The exact status is layered rather than absent:

1. G8-12 implemented bounded existing-file replacement.
2. G8-12A returned `EXISTING_FILE_MUTATION_ARCHITECTURE_CONFIRMED` and proved
   Worker Platform execution ownership, Governance authority, Replay ownership,
   and thin-interface neutrality.
3. G8-99 returned `GENERATION_8_RUNTIME_ADOPTION_CERTIFIED` and explicitly
   included bounded existing-file replacement in the certified workflow.
4. G31 R02 returned
   `G31_EXISTING_REPLACE_OWNER_ATOMICITY_CONSUMPTION_AND_RECOVERY_HARDENING_OPERATIONAL`
   with atomic replacement, stable descriptors, one-shot consumption,
   restoration, recovery, and complete focused/full-suite evidence.
5. R05-R07 subsequently certified the live common-entry authorization,
   authenticated request, and single-use consumption boundaries while stopping
   before selection.

This is sufficient evidence that the Worker and bounded replacement capability
are not uncertified implementation experiments. It is not selection
certification for the exact resource entry. G8-09C's
`FIRST_MUTATING_WORKER_CERTIFIED` verdict covers a different new-file Worker
and explicitly excludes existing-file modification and autonomous Worker
selection. It is not borrowed as evidence for this Worker.

### Worker and selection Replay

`reconstruct_authenticated_replace_replay_v2` is the current replacement
request/consumption reconstructor. It validates exact request identity, actor,
authorization, repository, session, decision, candidate, grounding,
provenance, target, preimage, replacement, mode, lifecycle destination,
predecessor ordering, immutable consumption identity, and artifact hashes.
Missing, reordered, duplicated, stale, substituted, or hash-invalid evidence
fails closed.

The existing selection owner is
`aigol.runtime.unified_resource_selection_runtime.select_unified_resource`.
It creates the existing `RESOURCE_SELECTION_ARTIFACT_V1`, diagnostics, status,
and returned artifact, then records two ordered immutable Replay wrappers.
`reconstruct_unified_resource_selection_replay` validates wrapper order,
wrapper and artifact hashes, registry hash, selection reference, returned hash,
selected resource, role, capability, domain, rationale, and failure state.

These Replay models have different stage-local payloads, as expected, but no
conflicting authority or ordering semantics. R07 Replay can be an immutable
parent context for selection Replay. No request or consumption event needs to
be rewritten or repeated.

### Canonical unified resource registry

`default_resource_registry()` is the canonical selectable resource registry.
Its current hash is:

`sha256:74ad406cfde8b5c8d19005d29d8d513a5eea88bbe45e3379d8972a2f8892de5a`

Its Worker-role choices are:

| Resource | Worker-role capabilities | Authority profile |
|---|---|---|
| `CODEX` | `IMPLEMENTATION_ASSISTANCE`, `FILESYSTEM_INSPECTION` | `WORKER_AUTHORIZED_TASK_ONLY` |
| `CLAUDE_CODE` | `IMPLEMENTATION_ASSISTANCE`, `FILESYSTEM_INSPECTION` | `WORKER_AUTHORIZED_TASK_ONLY` |
| `REPLAY_INSPECTOR_WORKER` | `REPLAY_INSPECTION` | `WORKER_AUTHORIZED_TASK_ONLY` |

No resource or role binding contains
`FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER` or
`REPLACE_EXISTING_TEXT_FILE`.

The registry's existing Worker authority profile already matches the hardened
Worker:

- authorized task execution allowed;
- proposing prohibited;
- dispatch and authorization prohibited;
- Provider and Worker invocation prohibited;
- Governance and Replay mutation prohibited.

The passive ERR registry contains only `mock_filesystem_worker`, not the exact
replacement Worker. The domain/Worker resolution registry has a future
`SERVER_MANAGEMENT / FILESYSTEM` family with read-only evidence authority. It
is not selectable mutation evidence. The capability, sandbox, Provider,
assignment, and Platform capability-certification registries likewise contain
no exact resource/operation pair. No alternative exact registry was found.

### Current capability and certification vocabulary

The current default unified registry uses broad capability tokens such as
`IMPLEMENTATION_ASSISTANCE`, `FILESYSTEM_INSPECTION`, and
`REPLAY_INSPECTION`. None is semantically equal to existing-file replacement.

The checked-in `WORKER_SELECTION_CERTIFICATION_REPORT_V1` is public-hash valid:

- final verdict: `WORKER_SELECTION_CERTIFIED`;
- artifact hash:
  `sha256:c38b21efede2314fb7cdb8f6bb8a74ee5f4a1d1c3adf46992471684734a94155`.

Its seven scenarios cover deterministic `file_create`, translation, static
summary, failover, validation failure, and capability mismatch. Neither the
exact replacement Worker nor `REPLACE_EXISTING_TEXT_FILE` is declared or
tested. Consequently, the report does not certify adding this mutation
capability to the selectable registry.

The Platform capability certification registry is governance metadata for
Platform Core capabilities and grants no runtime authority. It contains no
exact replacement operation. G8-99 remains the authoritative bounded
replacement-capability evidence; a later selection certification should cite
that lineage rather than manufacture a second capability certification model.

### Selector input and output contracts

`select_unified_resource` accepts:

- selection identity and timestamp;
- workflow type;
- required capability;
- requested role type;
- domain;
- Worker-authorization requirement;
- minimum trust;
- optional preferred resource identity;
- optional context identity/hash;
- one registry and Replay destination.

Eligibility requires exact lifecycle, trust, role, capability, domain, and
authority compatibility. Worker selection additionally requires existing
authorization. No eligible resource or equal leading priorities fail closed.

The output preserves selected resource identity, category, version, role,
authority profile, capability and domain matches, registry and diagnostics
hashes, context identity/hash, rationale, and explicit false invocation,
execution, dispatch, and authorization flags. It stops before assignment.

`select_authorized_grounded_worker` is not the reusable R07 input binding. It
accepts only the G31-10 execution-authorization capture and projects fixed
`NATIVE_DEVELOPMENT / IMPLEMENTATION_ASSISTANCE / WORKER_ROLE` vocabulary. It
also reconstructs the G31-10 execution-ready lineage. Supplying R07 evidence
would correctly fail before selection. R08 must eventually add a bounded R07
parent projection only after selection certification; it must not change this
existing G31-10 path.

### Assignment and dispatch contracts

`assign_worker_from_invocation_request` accepts an existing
`WORKER_INVOCATION_REQUEST_ARTIFACT_V1` plus compatible `WORKER_ARTIFACT_V1`
evidence, or the existing passive ERR lookup mode. It validates Worker family,
role, packet, allowed outputs, forbidden operations, availability, authority,
and nested request Replay before creating `WORKER_ASSIGNMENT_ARTIFACT_V1`.

The current G31-12B projection from selection to assignment is specifically
fixed to `CODEX / HYBRID_PROVIDER_WORKER / WORKER_ROLE`. It does not yet project
the replacement Worker. That is downstream compatibility debt and is not a
reason to broaden R08B beyond selection certification.

`dispatch_assigned_worker` accepts the existing assignment artifact and Replay,
preserves exact Worker and request identity, creates existing dispatch
artifacts and four-step Replay, and does not invoke the Worker. It is identity-
generic after a valid assignment.

`invoke_dispatched_worker` accepts the existing dispatch artifact and Replay,
preserves exact Worker identity, creates existing lifecycle-only invocation
artifacts and four-step Replay, and starts no process, Provider, command, or
mutation. Physical replacement remains a later separately governed owner.

## Compatibility matrix

| Transition | Classification | Exact owner | Evidence and limitation |
|---|---|---|---|
| Replacement Worker -> Worker certification | `SUPPORTED` | Worker Platform plus G8/G31 Governance | G8-12/A, G8-99, and R02 certify the bounded operation and hardened physical owner; R05-R07 certify live preselection lineage |
| Worker certification -> capability certification | `SUPPORTED` | Generation 8 certification chain | G8-99 explicitly certifies bounded existing-file replacement; it does not grant selection registration automatically |
| Capability certification -> registry | `BLOCKED` | Governance/Certification and `default_resource_registry` | Exact resource and exact capability are absent; checked selection certification does not cover their admission |
| Registry -> unified selector | `SUPPORTED` | `select_unified_resource` | Unchanged selector accepts exact temporary canonical metadata and applies existing role, trust, capability, domain, and authority checks |
| Unified selector -> Selection Replay | `SUPPORTED` | Unified Resource Selection / Replay | Existing artifact family and two-step reconstruction preserve exact registry, resource, role, capability, context, and failure evidence |
| Selection Replay -> assignment | `PARTIALLY_SUPPORTED` | Invocation-request and Worker-assignment owners | Generic contracts exist, but current G31 projection requires exact CODEX evidence; replacement compatibility is a later bounded stage |
| Assignment -> dispatch | `SUPPORTED` | `dispatch_assigned_worker` | Generic exact-identity artifact/Reconstruction contract; unreachable until a valid replacement assignment exists |
| Dispatch -> invocation | `SUPPORTED` | `invoke_dispatched_worker` | Generic lifecycle-only invocation evidence; no process or mutation; unreachable until prior stages exist |

The first non-supported transition is capability certification to certified
registry admission. Later partial assignment compatibility is downstream and
does not change the R08A root cause.

## Architectural lineage

The lineages diverged at G8-12, but not incompatibly.

The unified resource selector existed before the G8-12 replacement Worker. Its
original selection certification was committed in June 2026 and modeled
generic deterministic and LLM Worker declarations. G8-12, committed on
2026-07-01, implemented a fixed operation-specific Worker under a direct
Platform Core coordinator. G8-09C had explicitly left autonomous Worker
selection outside its mutating-Worker scope, and G8-12 preserved that direct
request/execution topology. G8-99 then certified the bounded replacement
workflow without enrolling its Worker in unified selection.

G31-11B, committed on 2026-07-16, later bound the new G31 authorization chain
to the existing selector using generic `IMPLEMENTATION_ASSISTANCE` and selected
`CODEX`. R05-R07 instead retained the G8 replacement Worker's exact fixed
identity through authorization, request, and single-use consumption. R08 is the
first point where those independently evolved paths meet.

The divergence is therefore missing enrollment, not a legal inability to
enroll. Both lineages preserve human/Governance authorization, passive
selection, immutable Replay, fail-closed validation, no self-authorization,
and stage-local authority. The temporary probe proves the selector can express
the exact Worker without changing either lineage.

## Read-only compatibility probe

Two isolated selector calls used temporary Replay directories under `/tmp`.
Neither called request, consumption, assignment, dispatch, invocation,
Provider, command, or mutation owners.

The exact current registry produced:

```text
selection_status = FAILED_CLOSED
selected_resource_id = None
failure_reason = resource selection failed closed: no eligible resource exists
```

A temporary copy of the registry received exactly one canonical-shaped Worker
resource with:

```text
resource_id = FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER
resource_category = WORKER
resource_version = G8_12_EXISTING_FILE_MUTATION_IMPLEMENTATION_V1
role_type = WORKER_ROLE
capability_ids = [REPLACE_EXISTING_TEXT_FILE]
authority_profile = WORKER_AUTHORIZED_TASK_ONLY
domain_scope = [NATIVE_DEVELOPMENT]
```

The unchanged selector produced:

```text
selection_status = RESOURCE_SELECTION_SUCCEEDED
selected_resource_id = FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER
selected_role_type = WORKER_ROLE
provider_invoked = false
worker_invoked = false
dispatch_requested = false
```

The temporary metadata was discarded. This is representational evidence only,
not registry admission or certification.

## Root-cause determination

Primary cause, exactly one:

`missing registration`

The exact constitutional blocker is not merely a missing line of Python. It is
the absence of a **certified** exact selection-registry entry. The existing
Worker and bounded capability are certified; the authority and Replay models
are compatible; and the selector can represent the entry unchanged. However,
the checked selection certification and registry hash do not cover it.

Downstream consequences are:

- missing exact selectable capability vocabulary;
- missing selection-certification scenario and regenerated checked evidence;
- missing new canonical registry hash;
- missing later R07-to-selection binding;
- missing later replacement-selection-to-assignment projection.

Those consequences are not independent root causes and must not be bundled
into R08B beyond selection certification and registry admission.

## Ranked legitimate repairs

| Rank | Repair | Constitutional impact | Determinism / Replay | Certification impact | Size / maintenance | Determination |
|---|---|---|---|---|---|---|
| 1 | Extend the existing selection certification and canonical registry with the exact Worker/capability | Low and bounded; no new owner | Existing exact selector and Replay remain unchanged; registry hash changes visibly | One existing-model certification extension and regenerated checked evidence | Small to moderate; one maintained identity | **Preferred** |
| 2 | Add only the exact registry entry | Superficially low but uncertified | Deterministic selection would work, but registry change lacks selection evidence | Invalidates confidence in current checked coverage | Small code, high governance debt | Rejected |
| 3 | Add a broad mutation capability family and map replacement into it | Broadens semantics and eligibility | Adds ambiguity and future mapping risk | Requires wider certification | Larger recurring maintenance | Rejected |
| 4 | Modify selector rules or add an R07-specific compatibility wrapper | Creates special-case policy outside registry | Duplicates eligibility and lineage decisions | Requires selector recertification | Larger and divergent | Rejected |
| 5 | Add another selector, registry, or certification model | New parallel architecture | Splits identity and Replay authority | Duplicates certification | Highest maintenance | Prohibited |

The preferred repair must use the existing exact identity and operation. It
should add one exact Worker resource/role binding to the existing canonical
registry and extend the existing Worker-selection certification evidence to
prove selection, no-match/tamper behavior, authority neutrality, registry-hash
continuity, and Replay reconstruction. It must stop before binding R07 or
creating a live selection.

## Rejected shortcuts

- `CODEX` is not the replacement Worker and cannot preserve R07 identity.
- `IMPLEMENTATION_ASSISTANCE` is broader than one exact full-content
  replacement and is not certified as semantically equivalent.
- `FILESYSTEM_INSPECTION` is read-only and cannot represent mutation.
- `SERVER_MANAGEMENT / FILESYSTEM` has read-only evidence authority and is a
  future domain family, not this Worker.
- The request's `worker_id` is evidence to validate, not a selection result.
- An alias would conceal rather than certify identity or operation continuity.
- A direct preferred-resource call against the current registry correctly
  fails closed and cannot substitute for registration.
- The passive ERR registry has no exact entry and cannot be used as a second
  selection path.

## Change size and production symbols

Production delta:

- 0 files;
- 0 insertions, 0 deletions;
- no new or modified production symbol.

Test delta:

- 0 files;
- 0 insertions, 0 deletions.

Documentation delta:

- exactly this one report.
- 728 insertions, 0 deletions.

No helper, alias, registry entry, capability token, selection artifact, Replay
writer, or compatibility layer was added or duplicated.

## Read-only validation

Validation was intentionally limited to read-only and temporary-directory
evidence. No full repository suite, PTY, mutation workflow, Worker execution,
or Provider execution was run.

Exact results:

- exact current/default versus temporary exact-entry selector probe:
  **2 cases; 1 expected fail-closed, 1 expected selection, 0 unexpected
  results**;
- unified selector, PPP integration, checked Worker-selection certification,
  and G31-11B binding: **43 passed, 0 skipped, 0 failed**;
- ERR, domain/Worker, Platform capability-certification, basic capability, and
  Worker registries: **49 passed, 0 skipped, 0 failed**;
- static certification, architecture, common-entry/import, Generation 30 thin
  adapter, and no-forbidden-surface checks: **9 passed, 0 skipped, 0 failed**;
- Replay binding, chain integrity, unified reconstruction, and Worker
  registration/assignment Replay: **42 passed, 0 skipped, 0 failed**;
- Governance conformance tests: **5 passed, 0 skipped, 0 failed**;
- targeted `py_compile`: passed for the replacement Worker, selector,
  G31 selection binding, certification/registry owners, assignment, dispatch,
  invocation, and common-entry service;
- parent `git diff --check`: passed;
- all three nested repository `git diff --check` checks: passed;
- complete repository suite: not run, as required for this `AUDIT_ONLY`
  generation;
- live PTY: not run;
- mutation workflow, Worker execution, Provider execution: not run.

The Replay group includes `test_worker_runtime_v1.py`, already present in the
registry group; counts are reported per executed command and are not summed as
a distinct-test total.

## Governance result

The deterministic read-only conformance engine remains:

`PARTIALLY_CONFORMANT`

- checks passed: 18;
- checks failed: 2;
- critical violations: 0;
- deterministic: true;
- fail-closed: true;
- read-only: true;
- report hash:
  `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea`.

The two known hook findings remain visible and unchanged: the root expected and
installed hooks are missing, and the system pre-commit hook lacks
`promotion_gate_v02` and `check_layer_freeze`. This audit neither repairs nor
reinterprets them.

## Protected state and nested repositories

The protected paths retained their exact pre-audit SHA-256 values:

| Protected path | SHA-256 |
|---|---|
| `diagnostic_evidence.json` | `a626a69a8020bc730876119c52701a94de9ab6e4772cc64c1f5d017296650203` |
| `governed_return.json` | `e82f47c0c13678725993b21e2af2e0437edccaed324f861a7b58e77d7f8e787d` |
| `lineage.json` | `07b95505521e70f51cdddecc1057fd3a208b198445693c9a8da1e996df5799dd` |
| `provider_stderr.txt` | `d47a06d59aba2814c3fb7460049fc2ccbfc834196c956d6c6558e8be8b079e24` |
| `provider_stdout.txt` | `a73a499e2e9133c03d7babfd5c4dec7967f31e2bfb354ea9dd41df0a15c08cb3` |
| `governed_returns.jsonl` | `dbc7b63f2a17c50c43bbb4fde4f44c1dbae8d25d550fb6b4d4daa14e17126161` |
| each protected marker | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

The nested repositories remain clean:

- `sapianta-domain-credit`: branch `main`, commit
  `8615e1e290471a67e4e764c6ab2138340bc7936f`;
- `sapianta_system`: branch `feature/governance-evolution-loop`, two commits
  ahead, commit `3183bab71f8f30397c0309dd2e6d846d14a11f66`;
- `sapianta-domain-trading`: branch `main`, commit
  `d3038dc4ba36ffbaee9161172b4c852e8e6acbda`.

No nested repository was modified.

## Exact Git status

At report creation, the pre-existing protected status was:

```text
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/diagnostic_evidence.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/governed_return.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/lineage.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stderr.txt
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stdout.txt
 M .runtime/aigol/ledger/governed_returns.jsonl
?? WORKER_INVOCATION_ARTIFACT_V1
?? WORKER_INVOKED
?? invocation
?? docs/governance/G31_24G_R04_R04_R08A_FILESYSTEM_REPLACE_WORKER_SELECTION_CERTIFICATION_AND_REGISTRY_COMPATIBILITY_AUDIT.md
```

Nothing is staged and no commit was created.

## Progress estimate

Evidence-scoped planning estimates remain:

- Generation 31 no-copy/paste governed-development lifecycle: **99.97%**;
- whole project toward the current bounded Product 1 and governed-development
  objective: **98.1%**.

These are not production-readiness or certification claims. R08A removes the
architectural-incompatibility uncertainty and narrows the next unit to one
existing-model selection certification and registry admission. R08 operational
binding, later assignment compatibility, physical execution, validation, and
product release remain separately governed.

## Deterministic verdict

`READY_FOR_BOUNDED_SELECTION_CERTIFICATION`

The existing hardened replacement Worker can legally participate in the
existing unified selector. Its exact certified selection-registry admission is
missing. The selector, authority model, and Replay model require no redesign.

Primary constitutional cause:

`missing registration`

Exactly one next state:

`G31_24G_R04_R04_R08B_BOUNDED_FILESYSTEM_REPLACE_WORKER_SELECTION_CERTIFICATION_REQUIRED`

## Complete bounded G31-24G-R04-R04-R08B prompt

```text
# Generation 31-24G-R04-R04-R08B
# Bounded Filesystem Replace Worker Selection Certification

Treat Generation 30, accepted G31 common-entry and R05-R07 results, the accepted
R08 blocked report, and the R08A audit as immutable certified baselines.

R08A verdict:

READY_FOR_BOUNDED_SELECTION_CERTIFICATION

Primary constitutional cause:

missing registration

Required state:

G31_24G_R04_R04_R08B_BOUNDED_FILESYSTEM_REPLACE_WORKER_SELECTION_CERTIFICATION_REQUIRED

## Objective

Certify and admit exactly one existing Worker identity and capability into the
existing unified Worker-selection lifecycle:

worker_id = FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER
capability = REPLACE_EXISTING_TEXT_FILE
role = WORKER_ROLE
authority_profile = WORKER_AUTHORIZED_TASK_ONLY
domain = NATIVE_DEVELOPMENT

Produce exact checked certification evidence and one canonical registry entry
using existing certification, registry, selector, serialization, hashing, and
Replay contracts.

Stop before binding any R07 request or consumption evidence, live Worker
selection, assignment, dispatch, invocation, command execution, target opening,
repository mutation, restoration, rollback, or recovery.

## Required reuse

Reuse:

- G8-12/A and G8-99 existing-file replacement implementation, architecture,
  and certification evidence;
- accepted G31 R02 hardened-owner evidence;
- unchanged R05-R07 identities and Replay evidence as lineage references only;
- default_resource_registry and its existing resource/role shape;
- WORKER_ROLE and WORKER_AUTHORIZED_TASK_ONLY;
- select_unified_resource and reconstruct_unified_resource_selection_replay;
- the existing Worker-selection certification generator, evidence layout,
  report family, and final-verdict contract;
- existing public serialization, hash, immutable-write, and validation helpers.

Do not create a new Worker, selector, registry, capability system,
certification model, Replay subsystem, authority profile, alias, adapter,
compatibility wrapper, or canonical artifact family.

## Required bounded change

1. Add exactly one canonical resource entry for the existing replacement
   Worker to default_resource_registry.
2. Give it exactly one selectable Worker-role capability:
   REPLACE_EXISTING_TEXT_FILE.
3. Reuse WORKER_AUTHORIZED_TASK_ONLY without changing its authority.
4. Bind the entry to the existing Worker version and bounded certification
   lineage.
5. Extend the existing Worker-selection certification coverage with an exact
   deterministic scenario proving that the canonical registry selects this
   Worker only for the exact capability, role, domain, and authorization
   requirement.
6. Regenerate only the affected existing checked certification evidence through
   the existing certification entrypoint.
7. Record and validate the new canonical registry hash and certification report
   hash.
8. Stop before adding the R07-to-selection application binding.

If the existing certification generator cannot certify the unified registry
entry without a new certification architecture, stop and report that exact
blocker. Do not build a parallel certification owner.

## Fail-closed requirements

Prove that selection fails closed for:

- changed Worker identity or version;
- changed operation/capability;
- missing Worker authorization;
- wrong role, domain, authority profile, lifecycle, or trust state;
- registry substitution, duplicate entry, or stale registry hash;
- CODEX, IMPLEMENTATION_ASSISTANCE, FILESYSTEM_INSPECTION, alias, or broad
  capability substitution;
- certification evidence absence, stale hash, false verdict, or lineage
  substitution;
- ambiguous competing exact candidates;
- reordered, removed, duplicated, or substituted selection Replay.

No invalid case may partially select a Worker or change any R05-R07 artifact.

## Authority and stage boundaries

Certification and temporary selector probes may state only that the exact
resource is selection-eligible. They must retain:

worker_assigned = false
worker_dispatched = false
provider_invoked = false
worker_invoked = false
execution_requested = false
command_executed = false
repository_mutated = false

Do not call the common-entry R07 continuation, assignment, dispatch,
invocation, Worker, Provider, command, or mutation owners. Do not run a live
PTY or mutation workflow.

## Minimal-change rule

Modify only the existing unified registry, existing selection-certification
owner/evidence, focused tests, and one governance report. Prefer data additions
over new production symbols. Add no production file. If more than three
production files or a new abstraction is required, stop and report why.

Report exact production, test, certification-evidence, and documentation line
counts; every modified symbol; the old and new registry/report hashes; and any
duplicated helper logic.

## Tests and validation

Run in order and report exact counts for:

1. focused exact replacement-Worker selection certification tests;
2. existing Worker-selection certification tests;
3. unified selector and registry tests;
4. replacement Worker static certification and architecture checks without
   executing mutation;
5. G31-11B selection regressions;
6. relevant selection Replay and tamper tests;
7. architecture and import-boundary tests;
8. Governance tests and the read-only conformance engine;
9. targeted py_compile;
10. parent and nested git diff --check;
11. protected-path SHA-256 comparison.

Do not run the full repository suite, live PTY, mutation workflow, Worker
execution, or Provider execution for this bounded certification generation.

## Documentation

Add exactly one report:

docs/governance/G31_24G_R04_R04_R08B_BOUNDED_FILESYSTEM_REPLACE_WORKER_SELECTION_CERTIFICATION.md

Document exact reuse, registry entry, certification scenario and evidence,
registry/report hashes, selector and Replay results, fail-closed coverage,
authority boundaries, change size, validation, Governance, protected state,
exact Git status, progress, one deterministic verdict, and exactly one next
state with a complete bounded prompt.

Do not stage or commit. Preserve all protected paths byte-for-byte.

## Required verdict

Return exactly one:

G31_FILESYSTEM_REPLACE_WORKER_SELECTION_CERTIFIED
G31_FILESYSTEM_REPLACE_WORKER_SELECTION_CERTIFICATION_BLOCKED

Do not report partial success.
```
