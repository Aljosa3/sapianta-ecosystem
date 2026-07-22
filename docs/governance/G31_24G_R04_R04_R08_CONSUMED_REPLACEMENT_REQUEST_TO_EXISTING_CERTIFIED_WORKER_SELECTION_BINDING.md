# Generation 31-24G-R04-R04-R08 Consumed Replacement Request to Existing Certified Worker Selection Binding

Status: blocked before implementation by deterministic certified-registry
incompatibility; documentation-only report.

Date: 2026-07-22

Verdict:

`G31_CONSUMED_REPLACEMENT_REQUEST_TO_EXISTING_CERTIFIED_WORKER_SELECTION_BINDING_BLOCKED`

First exact deterministic blocker:

`R07_FIXED_REPLACEMENT_WORKER_AND_OPERATION_ABSENT_FROM_EXISTING_CERTIFIED_SELECTION_CONTRACT`

Exactly one next state:

`G31_24G_R04_R04_R08A_FILESYSTEM_REPLACE_WORKER_SELECTION_CERTIFICATION_AND_REGISTRY_COMPATIBILITY_AUDIT_REQUIRED`

## Constitutional scope

This report treats Generation 30 and accepted G31 common-entry, R05, R06, and
R07 results as immutable certified baselines. It evaluates whether the exact
consumed R07 request can be bound to the existing certified Worker-selection
owner without adding or changing a selector, registry, capability vocabulary,
certification, Replay subsystem, Worker, or mutation path.

The repository proves that it cannot. The exact R07 Worker and operation are not
represented by the existing certified selection contract. The prompt's
minimal-change stop rule therefore applies before implementation.

No production behavior, test, schema, registry, certification evidence, Replay,
authorization state, request state, consumption state, or runtime artifact was
changed. No Worker was selected, assigned, dispatched, or invoked. No Provider,
command, target-open, mutation, restoration, rollback, or recovery owner was
reached. No live PTY workflow was run.

## Accepted baseline evidence

The audit began from:

- branch: `master`;
- HEAD: `cf8737f5d2ef9ab149aa46c7de4665dcfaebbca3`;
- HEAD subject:
  `feat(runtime): bind authenticated request to single-use authorization consumption`;
- accepted R07 verdict:
  `G31_AUTHENTICATED_REPLACEMENT_REQUEST_TO_SINGLE_USE_AUTHORIZATION_CONSUMPTION_BINDING_OPERATIONAL`;
- accepted R07 next state:
  `G31_24G_R04_R04_R08_CONSUMED_REPLACEMENT_REQUEST_TO_EXISTING_CERTIFIED_WORKER_SELECTION_BINDING_REQUIRED`.

The initial parent worktree contained only the nine already-declared protected
paths. The accepted R07 production, tests, and report were committed and clean.

## Existing contracts inspected

### R07 request and consumption

The exact consumed request is owned by
`aigol.workers.filesystem_replace_worker` and fixes:

```text
worker_id = FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER
worker_operation = REPLACE_EXISTING_TEXT_FILE
authorization_consumed = true
consumption_identity = exact authorization_hash
```

`reconstruct_authenticated_replace_replay_v2` reconstructs the immutable
request and consumption chain and rejects identity, ordering, payload, and hash
substitution. This contract is operational and was not changed.

### Existing certified selection binding

`select_authorized_grounded_worker` in
`aigol.runtime.confirmed_grounded_execution_authorization_binding` is the
existing G31 certified Worker-selection binding. It accepts the G31-10
`execution_authorization_capture` family, reconstructs that authorization and
its execution-ready Replay, validates the checked-in Worker-selection
certification, and calls the existing unified selector.

Its projection is statically fixed to:

```text
workflow_type = NATIVE_DEVELOPMENT
required_capability = IMPLEMENTATION_ASSISTANCE
requested_role_type = WORKER_ROLE
domain_id = NATIVE_DEVELOPMENT
worker_authorization_required = true
```

It does not accept an `AUTHORIZED_REPLACE_EXISTING_FILE_REQUEST_V2`, R07
consumption reconstruction, or replacement-Worker authorization record. Calling
it with R07 evidence would fail its existing authorization-family validation
before selection.

### Existing certified registry and selector

The underlying selection owner is
`aigol.runtime.unified_resource_selection_runtime.select_unified_resource`. Its
canonical `default_resource_registry` has registry hash:

`sha256:74ad406cfde8b5c8d19005d29d8d513a5eea88bbe45e3379d8972a2f8892de5a`

The selectable resources are:

| Resource | Selectable Worker capabilities |
|---|---|
| `CODEX` | `IMPLEMENTATION_ASSISTANCE`, `FILESYSTEM_INSPECTION` |
| `CLAUDE_CODE` | `IMPLEMENTATION_ASSISTANCE`, `FILESYSTEM_INSPECTION` |
| `REPLAY_INSPECTOR_WORKER` | `REPLAY_INSPECTION` |

`OPENAI` and `ANTHROPIC` expose Provider roles only. The unified Replay
reconstruction runtime exposes a governance-runtime role only.

The registry contains neither:

- resource ID `FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER`; nor
- capability or operation `REPLACE_EXISTING_TEXT_FILE`.

The checked-in selection certification is public-hash valid:

- verdict: `WORKER_SELECTION_CERTIFIED`;
- artifact hash:
  `sha256:c38b21efede2314fb7cdb8f6bb8a74ee5f4a1d1c3adf46992471684734a94155`.

That certification covers deterministic `file_create`, translation, static
summary, failover, validation failure, and capability-mismatch scenarios. It
does not declare or certify the hardened replacement Worker or its replacement
operation.

### Other registries and Worker owners

Repository-wide inspection found no alternative certified selector containing
the exact R07 Worker and operation:

- the domain-and-worker resolution registry contains a future
  `SERVER_MANAGEMENT / FILESYSTEM` family with read-only evidence authority, not
  the hardened replacement Worker;
- Worker assignment registries operate after invocation-request creation and do
  not provide an R07 selection contract;
- the legacy worker-selection certification declarations include deterministic
  file creation but not existing-file replacement;
- the hardened replacement Worker validates its own fixed Worker identity but
  is not registered as a selectable resource.

Using any of these contracts would either select a different Worker, map a
mutation operation to an inspection or generic implementation capability, skip
the certified selector, or cross into assignment. Each would violate the R08
scope.

## Deterministic compatibility result

The exact direct probe used the canonical registry and existing unified
selector with:

```text
preferred_resource_id = FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER
required_capability = REPLACE_EXISTING_TEXT_FILE
requested_role_type = WORKER_ROLE
domain_id = NATIVE_DEVELOPMENT
worker_authorization_required = true
```

The deterministic result was:

```text
worker_present = false
operation_present = false
selection_status = FAILED_CLOSED
selected_resource_id = None
failure_reason = resource selection failed closed: no eligible resource exists
```

This is correct existing behavior. It proves that an exact selection cannot be
produced from the current registry.

Removing `preferred_resource_id` or projecting the request to
`IMPLEMENTATION_ASSISTANCE` would select `CODEX`, not the exact Worker named by
the consumed request. That would replace canonical Worker evidence with a
different resource identity and broaden the operation. Such a projection is
forbidden.

## Why no bounded binding was implemented

A successful R08 binding would require at least one of the following invalid
changes:

1. add the hardened replacement Worker to the canonical resource registry;
2. add and define a new `REPLACE_EXISTING_TEXT_FILE` selectable capability;
3. change the fixed vocabulary or input family of the existing certified G31
   selector;
4. map the replacement Worker to `CODEX` or `FILESYSTEM_INSPECTION` without
   deterministic certification evidence;
5. bypass the certified selector and manufacture a selection artifact from the
   request's `worker_id` field.

Options 1 through 3 change certified registry, capability, and selection
contracts and require new certification evidence. Options 4 and 5 violate exact
identity, operation compatibility, and selector ownership. None is an
existing-function binding.

The R08 prompt explicitly requires stopping when the existing certified
selector cannot consume R07 evidence without broad changes. Production
implementation, focused R08 success tests, common-entry binding, and
presentation changes were therefore prohibited.

## Fail-closed and authority result

The repository remains at the exact R07 boundary:

```text
exact APPROVED V3 decision
  -> exact mutation authorization
  -> exact authenticated replacement request
  -> exact single-use consumption claim
  -> STOP: no compatible certified selection entry
```

The direct selector probe returned no resource and wrote only temporary
fail-closed selection evidence under a disposable temporary directory. It did
not alter the R07 request or consumption chain.

Canonical authority remains:

```text
worker_selected = false
worker_assigned = false
worker_dispatched = false
provider_invoked = false
worker_invoked = false
command_executed = false
repository_mutated = false
```

AiCLI and the in-memory adapter remain unchanged and own no Worker identity,
capability mapping, registry, selection, authorization, or mutation semantics.

## Change size and symbols

Production delta:

- **0 files**;
- **0 insertions, 0 deletions**;
- no new or modified production symbol.

Test delta:

- **0 files**;
- **0 insertions, 0 deletions**.

Documentation delta:

- exactly this one report;
- **507 insertions, 0 deletions**.

No helper logic was added or duplicated. No registry entry, capability,
selection artifact, Replay writer, or runtime adapter was introduced.

## Validation performed

Because the deterministic blocker occurred before implementation, there is no
focused R08 success suite to pass. The instruction to run the complete
repository suite applies only after focused R08 suites pass; that condition was
not met. Running the complete suite would not make the absent Worker and
capability appear, so it was not run.

Read-only and predecessor evidence completed:

- direct exact-registry compatibility probe: **1 deterministic fail-closed
  result, 0 selections**;
- existing unified selector and G31 certified selection binding:
  **29 passed, 0 skipped, 0 failed**;
- accepted R07 request and consumption regression:
  **33 passed, 0 skipped, 0 failed**;
- Governance conformance tests: **5 passed, 0 skipped, 0 failed**;
- targeted `py_compile`: passed for the existing selector, unified registry,
  hardened replacement Worker, and common-entry service;
- parent `git diff --check`: passed before this report;
- all three nested repository `git diff --check` checks: passed;
- live PTY: not run, as required;
- complete repository suite: not run because the minimal-change blocker stopped
  R08 before implementation and before a focused R08 pass.

No validation count is presented as an R08 operational success result.

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

The two known hook findings remain unchanged and visible. R08 does not repair or
reinterpret them.

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

The nested repositories remain clean at their original commits:

- `sapianta-domain-credit`: `8615e1e290471a67e4e764c6ab2138340bc7936f`;
- `sapianta_system`: `3183bab71f8f30397c0309dd2e6d846d14a11f66`;
- `sapianta-domain-trading`: `d3038dc4ba36ffbaee9161172b4c852e8e6acbda`.

Nothing is staged and no commit was created.

## Exact Git status and scoped commit commands

Exact final `git status --short`:

```text
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/diagnostic_evidence.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/governed_return.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/lineage.json
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stderr.txt
 M .runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stdout.txt
 M .runtime/aigol/ledger/governed_returns.jsonl
?? WORKER_INVOCATION_ARTIFACT_V1
?? WORKER_INVOKED
?? docs/governance/G31_24G_R04_R04_R08_CONSUMED_REPLACEMENT_REQUEST_TO_EXISTING_CERTIFIED_WORKER_SELECTION_BINDING.md
?? invocation
```

The six modified paths and three marker paths predate this audit and are not
part of its documentation-only delta.

No command below was executed:

```bash
git add docs/governance/G31_24G_R04_R04_R08_CONSUMED_REPLACEMENT_REQUEST_TO_EXISTING_CERTIFIED_WORKER_SELECTION_BINDING.md
git commit -m "docs(governance): record replacement worker selection blocker"
```

## Progress estimate

Evidence-scoped planning estimates remain unchanged:

- Generation 31 no-copy/paste governed-development lifecycle: **99.97%**;
- whole project toward the current bounded Product 1 and governed-development
  objective: **98.1%**.

These are not production-readiness or certification claims. R07 consumption is
operational, but exact replacement-Worker selection is blocked by missing
certified selection compatibility.

## Deterministic verdict

`G31_CONSUMED_REPLACEMENT_REQUEST_TO_EXISTING_CERTIFIED_WORKER_SELECTION_BINDING_BLOCKED`

The exact consumed R07 request cannot reach an existing certified selection
without changing the certified registry, capability vocabulary, selection input
contract, or Worker identity. No partial or substituted selection was created.

First exact deterministic blocker:

`R07_FIXED_REPLACEMENT_WORKER_AND_OPERATION_ABSENT_FROM_EXISTING_CERTIFIED_SELECTION_CONTRACT`

Exactly one next state:

`G31_24G_R04_R04_R08A_FILESYSTEM_REPLACE_WORKER_SELECTION_CERTIFICATION_AND_REGISTRY_COMPATIBILITY_AUDIT_REQUIRED`

## Complete bounded G31-24G-R04-R04-R08A prompt

```text
# Generation 31-24G-R04-R04-R08A
# Filesystem Replace Worker Selection Certification and Registry Compatibility Audit

Treat Generation 30 and accepted G31 common-entry, R05, R06, and R07 results as
immutable certified baselines.

R08 verdict:

G31_CONSUMED_REPLACEMENT_REQUEST_TO_EXISTING_CERTIFIED_WORKER_SELECTION_BINDING_BLOCKED

First exact deterministic blocker:

R07_FIXED_REPLACEMENT_WORKER_AND_OPERATION_ABSENT_FROM_EXISTING_CERTIFIED_SELECTION_CONTRACT

Required state:

G31_24G_R04_R04_R08A_FILESYSTEM_REPLACE_WORKER_SELECTION_CERTIFICATION_AND_REGISTRY_COMPATIBILITY_AUDIT_REQUIRED

## Objective

Perform an AUDIT_ONLY repository-evidence assessment of the smallest legitimate
way to make `FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER` and
`REPLACE_EXISTING_TEXT_FILE` eligible for the existing certified unified Worker
selection lifecycle.

Determine whether existing Worker certification, registry, capability,
authorization, selection Replay, and assignment contracts can represent the
exact hardened replacement Worker without redesigning Platform Core or changing
R05-R07 evidence.

Do not implement or mutate runtime behavior.

## Required inspection

Inspect and compare:

- the complete hardened replacement Worker V2 contract and tests;
- R05 authorization, R06 request, and R07 consumption identity;
- `default_resource_registry` and all selectable role/capability entries;
- `select_unified_resource` eligibility and ambiguity behavior;
- `select_authorized_grounded_worker` input and continuity contracts;
- Worker-selection certification scenarios and checked-in evidence;
- Worker assignment registry contracts, without entering assignment;
- capability certification registries and existing Worker certification reports;
- Replay, Canonical Presentation, and common-entry boundaries.

Search all repository registries before declaring any capability or
certification absent.

## Required determinations

Classify each required element as:

- already implemented and directly reusable;
- present but requiring a bounded compatibility projection;
- absent and requiring new certification evidence;
- incompatible with the immutable R05-R07 identity;
- architectural work that is prohibited unless deterministic evidence proves it
  unavoidable.

Determine exactly:

1. whether the replacement Worker already has certification sufficient for
   selectable registration;
2. whether `REPLACE_EXISTING_TEXT_FILE` can reuse an existing canonical
   capability without semantic broadening;
3. the smallest registry entry and authority profile, if evidence supports one;
4. whether the existing Worker-selection certification must be extended or
   regenerated;
5. whether the selector can accept an R07 authorization/consumption context
   through a bounded public projection;
6. whether selected resource identity can equal the exact R07 Worker identity;
7. the exact Replay and tamper requirements for a later binding;
8. whether a successful selection can still stop before assignment and mutation.

## Fail-closed rules

Do not recommend:

- mapping the replacement Worker to `CODEX`, `CLAUDE_CODE`,
  `FILESYSTEM_INSPECTION`, or generic `IMPLEMENTATION_ASSISTANCE` without exact
  certified semantic equivalence;
- treating request `worker_id` as a selection artifact;
- bypassing `select_unified_resource`;
- changing the consumed authorization or request identity;
- creating a second registry, selector, capability system, certification system,
  or Replay subsystem;
- selecting, assigning, dispatching, or invoking any Worker;
- Provider invocation, command execution, target opening, or repository mutation.

If exact certification or registry evidence is absent, identify the first exact
missing artifact and propose one bounded certification generation only. Do not
bundle the later R08 binding.

## Validation

Use read-only repository inspection and temporary-directory selector probes.
Run relevant existing replacement-Worker, registry, selector, certification,
Replay, architecture, and Governance tests. Run `py_compile` and parent/nested
`git diff --check`. Do not run a live PTY or full repository suite for an
AUDIT_ONLY result unless repository evidence makes it necessary.

## Documentation

Add exactly one report:

docs/governance/G31_24G_R04_R04_R08A_FILESYSTEM_REPLACE_WORKER_SELECTION_CERTIFICATION_AND_REGISTRY_COMPATIBILITY_AUDIT.md

Document exact registry and certification evidence, compatibility matrix,
smallest safe change, explicit non-goals, validation, governance, protected
state, exact Git status, one deterministic verdict, and exactly one next state
with a complete bounded prompt.

Do not stage or commit. Preserve all protected paths byte-for-byte.

## Required verdict

Return exactly one:

READY_FOR_BOUNDED_FILESYSTEM_REPLACE_WORKER_SELECTION_CERTIFICATION
READY_FOR_DIRECT_EXISTING_SELECTION_BINDING
BLOCKED_BY_MISSING_FILESYSTEM_REPLACE_WORKER_CERTIFICATION
BLOCKED_BY_INCOMPATIBLE_CERTIFIED_SELECTION_ARCHITECTURE
```
