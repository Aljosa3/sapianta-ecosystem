# Generation 31-07 — G31-06 Minimality and Non-Duplication Acceptance Audit

Status: completed audit; documentation only.

Date: 2026-07-16

Verdict:

`G31_06_MINIMALITY_ACCEPTED_WITH_OBSERVATIONS`

## Audit scope and method

This audit compares G31-06 commit `c04e811addae64d6131cf31b735d9b174fd85cbf`
directly with parent `c04e811a^`. Generation 30, G31-02, G31-04, and G31-05
remain immutable accepted baselines. No runtime, test, existing documentation,
Repository Cognition, Replay, Worker, Provider, authorization, or mutation
behavior was changed.

The audit examined:

- the complete committed diff and every added or materially changed runtime
  function;
- existing repository path, symbol, hashing, workspace, mutation-layer,
  source/test, immutable-artifact, Replay, and presentation contracts;
- the operational G31-06 artifact, Worker-request projection, terminal
  composition, and Human Interface projection;
- focused G31-06, capability-audit, and Platform Core project-service tests.

Raw line count was treated as supporting evidence, not as the minimality
criterion. The verdict is based on ownership, semantic duplication, lineage,
fail-closed necessity, and whether an existing contract could represent the
transition without losing required evidence.

## Exact direct-parent diff statistics

```text
8       0       aigol/cli/aicli.py
87      2       aigol/cli/aigol_cli.py
696     0       aigol/runtime/approved_durable_work_repository_scope_grounding.py
23      1       aigol/runtime/human_interface_runtime_entry_service.py
143     1       aigol/runtime/implementation_request_to_worker_request_bridge_runtime.py
514     0       docs/governance/G31_06_APPROVED_DURABLE_GOVERNED_WORK_CANONICAL_REPOSITORY_SCOPE_GROUNDING.md
7       2       tests/test_g15_runtime_06_governed_development_runtime_continuation.py
558     0       tests/test_g31_06_canonical_repository_scope_grounding.py
```

Totals:

- 8 files changed;
- 2,036 insertions;
- 6 deletions;
- runtime and CLI: 957 insertions, 4 deletions;
- tests: 565 insertions, 2 deletions;
- documentation: 514 insertions, 0 deletions.

The 696-line grounding module contains 63 lines of module declaration,
imports, constants, Replay-step declarations, and explicit false-authority
boundaries, plus 633 lines across 19 functions. No class was added.

## Runtime per-file and per-symbol audit

The classifications below use only the required classification vocabulary.
For newly added functions, “lines added” is the complete function span,
including its signature, docstring, and internal blank lines. For modified
functions it is the number of added diff lines.

### `approved_durable_work_repository_scope_grounding.py`

Canonical owner: Platform Core repository-scope grounding. The module owns
only the new evidence-binding transition and its artifact validation and
Replay. Existing capability detection remains owned by the capability audit;
mutation-layer classification remains owned by Platform Change Impact; Worker
request structure remains owned by the existing bridge.

| Symbol | Lines added | Responsibility | Existing contract reused | Necessity and equivalent search | Classification |
|---|---:|---|---|---|---|
| module declarations, constants, and false boundaries | 63 | Declare one artifact/version, two statuses, two Replay steps, and explicit non-authority flags | `FailClosedRuntimeError`, existing status and Replay conventions | Necessary artifact vocabulary; no competing G31-05-to-scope artifact existed | `ESSENTIAL_CANONICAL_CONTRACT` |
| `ground_approved_durable_work_repository_scope` | 115 | Validate G31-05, select one exact capability-audit entry, bind evidence, project the existing Worker request, and persist two ordered events | G31-05 validator/reconstructor, `detect_capabilities`, Worker projection, immutable transport | Necessary transition coordinator; no existing function consumes this exact lineage | `THIN_EXISTING_CAPABILITY_BINDING` |
| `validate_approved_durable_work_repository_scope_grounding` | 119 | Validate artifact identity, ten upstream hashes, target evidence, scope projection, and false authority boundaries | G31-05 validation, Worker-request validation, `replay_hash` | Necessary fail-closed consumer contract; no equivalent grounding validator existed | `ESSENTIAL_VALIDATION_OR_TAMPER_CHECK` |
| `reconstruct_approved_durable_work_repository_scope_grounding` | 31 | Reconstruct the two G31-06 wrappers and nested G31-05 Replay | `load_json`, G31-05 reconstruction | Necessary ordered lineage reconstruction; unified Replay does not know this artifact type or its field continuity | `ESSENTIAL_REPLAY_RECONSTRUCTION` |
| `render_approved_durable_work_repository_scope_grounding` | 24 | Render the canonical grounding result and authority boundary | Grounding validator | Required terminal projection; contains no target selection | `THIN_PRESENTATION_PROJECTION` |
| `_grounding_artifact` | 91 | Materialize the immutable grounding evidence and unchanged upstream identities | `replay_hash`, G31-05 fields, existing Worker artifact | Necessary separate evidence object; the pre-existing Worker request cannot carry target evidence, cognition identity, and complete upstream lineage without changing its responsibility | `ESSENTIAL_CANONICAL_CONTRACT` |
| `_required_capability_key` | 10 | Consume the already-decided PPP `affected_domain` key | G31-05 PPP task package | Necessary exact-key binding; it performs no natural-language inference | `THIN_EXISTING_CAPABILITY_BINDING` |
| `_target_evidence` | 18 | Convert only capability-audit implementation/test paths into ordered evidence requests | `detect_capabilities` entry contract | Necessary adapter; does not scan for additional paths | `THIN_EXISTING_CAPABILITY_BINDING` |
| `_observe_target` | 63 | Verify workspace containment and file existence, hash bytes, enumerate top-level Python symbols, and classify the mutation layer | `_constitutional_layer`, `replay_hash`; paths originate from `detect_capabilities` | Required because no symbol-rich immutable Repository Cognition artifact exists. It enriches selected paths but does not discover or choose targets | `ESSENTIAL_CANONICAL_CONTRACT` |
| `_validate_target_evidence` | 39 | Validate ordering, identity hashes, roles, layers, and optional current-workspace freshness | `_observe_target`, `replay_hash` | Required stale/substitution check; no generic read-only target-evidence validator accepts this contract | `ESSENTIAL_VALIDATION_OR_TAMPER_CHECK` |
| `_repository_cognition_snapshot_hash` | 21 | Bind capability-audit identity and selected evidence hashes | `AIGOL_CAPABILITY_AUDIT_RUNTIME_VERSION`, `replay_hash` | Necessary immutable snapshot identity; no existing capability-audit snapshot artifact covers this bounded selection | `ESSENTIAL_VALIDATION_OR_TAMPER_CHECK` |
| `_validate_projection_continuity` | 44 | Prove that only unresolved repository-scope fields changed in the Worker request | Existing G31-05 and Worker-request field contracts | Necessary goal, plan, approval, task-package, constraint, and objective continuity check | `ESSENTIAL_VALIDATION_OR_TAMPER_CHECK` |
| `_workspace_root` | 7 | Require an existing Git workspace for freshness reconstruction | `Path.resolve` | Necessary reconstruction precondition; analogous boundary checks exist but are coupled to other artifact contracts | `ESSENTIAL_VALIDATION_OR_TAMPER_CHECK` |
| `_existing_workspace_root` | 7 | Require the submitted workspace to exist while allowing deterministic non-Git unresolved output | `Path.resolve` | Necessary positive-versus-unresolved behavior | `ESSENTIAL_VALIDATION_OR_TAMPER_CHECK` |
| `_relative_path` | 8 | Normalize one safe workspace-relative POSIX path | `PurePosixPath` | Semantically overlaps public and private path validators elsewhere and the new bridge helper; no behavior-specific reason requires a second local form | `DUPLICATED_EXISTING_CAPABILITY` |
| `_verify_hash` | 7 | Verify a dictionary `artifact_hash` | `replay_hash` | Equivalent behavior already exists in public `transport.serialization.verify_replay_hash(..., hash_field="artifact_hash")` | `DUPLICATED_EXISTING_CAPABILITY` |
| `_ensure_replay_available` | 6 | Preflight both Replay filenames before writing either | immutable Replay convention | Prevents partial two-step persistence; `write_json_immutable` protects each file but not the pair | `ESSENTIAL_REPLAY_RECONSTRUCTION` |
| `_persist_step` | 10 | Persist an ordered immutable wrapper | `replay_hash`, `write_json_immutable` | Required artifact-specific step creation; generic transport primitives are reused | `ESSENTIAL_REPLAY_RECONSTRUCTION` |
| `_validate_wrapper` | 9 | Validate artifact-specific step order and wrapper hash | `replay_hash` | Order check is specific and necessary; its hash calculation could call `verify_replay_hash` but does not duplicate a Replay subsystem | `ESSENTIAL_REPLAY_RECONSTRUCTION` |
| `_require_string` | 4 | Enforce one non-empty string boundary | `FailClosedRuntimeError` convention | Local compatibility guard used by the artifact contract | `COMPATIBILITY_CODE` |

### `implementation_request_to_worker_request_bridge_runtime.py`

Canonical owner: existing Worker-request construction and validation.

| Symbol/change | Lines added | Responsibility | Existing contract reused | Necessity and equivalent search | Classification |
|---|---:|---|---|---|---|
| `project_worker_request_repository_scope` | 65 | Replace only unresolved repository-scope fields and bind grounding identity/hash | Existing `WORKER_REQUEST_ARTIFACT_V1` | Correct owner for the projection; creating a second Worker request type would be duplication | `THIN_EXISTING_CAPABILITY_BINDING` |
| `validate_worker_request_artifact` | 56 | Validate original and grounded Worker requests and preserve all false execution flags | Existing Worker request hash and status fields | Required public consumer validation; pre-G31-06 code had no public validator for the projected state | `ESSENTIAL_VALIDATION_OR_TAMPER_CHECK` |
| `_unique_relative_paths` | 21 | Normalize, deduplicate, and sort repository and focused-test paths | `PurePosixPath` | Overlaps `_relative_path` and existing repository-relative path validators; bounded low-level duplication | `DUPLICATED_EXISTING_CAPABILITY` |
| `Path` import changed to `Path, PurePosixPath` | 1 insertion, 1 deletion | Support local path normalization | Python path library | Supporting compatibility change only | `COMPATIBILITY_CODE` |

### `aigol_cli.py`

Canonical owner: operational runtime composition and canonical turn summary;
not repository semantics.

| Symbol/change | Lines added/deleted | Responsibility | Existing contract reused | Necessity and equivalent search | Classification |
|---|---:|---|---|---|---|
| grounding imports | 4/0 | Import the canonical transition and renderer | G31-06 public API | Required wiring, no logic | `THIN_EXISTING_CAPABILITY_BINDING` |
| `run_interactive_conversation` | 19/2 | Invoke grounding after G31-05 and stop or continue according to its canonical status | Existing G31-04/G31-05 branch and grounding API | Required real `./aicli` composition; no target decision is performed here | `THIN_EXISTING_CAPABILITY_BINDING` |
| `_interactive_approved_durable_work_worker_payload_turn_summary` | 3/0 | Preserve the source G31-05 failure reason after G31-06 supersedes the response status | Existing turn-summary contract | Required compatibility for truthful terminal lineage | `COMPATIBILITY_CODE` |
| `_interactive_approved_durable_work_repository_grounding_turn_summary` | 61/0 | Project canonical grounding fields into an operational turn summary | Existing G31-05 summary and grounding renderer | Required presentation mapping; no repository or authority semantics | `THIN_PRESENTATION_PROJECTION` |

### `human_interface_runtime_entry_service.py`

| Symbol | Lines added/deleted | Responsibility | Canonical owner and reuse | Necessity | Classification |
|---|---:|---|---|---|---|
| `run_human_interface_runtime_entry` | 23/1 | Copy canonical G31-06 fields from the latest Platform Core turn into the runtime-entry result | Platform Core owns values; Human Interface service transports them | Required so real AiCLI can render the result without owning semantics | `THIN_PRESENTATION_PROJECTION` |

### `aicli.py`

| Symbol | Lines added | Responsibility | Canonical owner and reuse | Necessity | Classification |
|---|---:|---|---|---|---|
| `_render_runtime_result` | 8 | Render already-projected grounding status, hashes, targets, Worker request hash, and dispatch boundary | Platform Core/runtime-entry result owns every value | Required terminal visibility; contains no binding, selection, or validation | `THIN_PRESENTATION_PROJECTION` |

## Non-runtime change classification

| Surface | Change | Classification and finding |
|---|---:|---|
| Focused G31-06 tests | 558 additions | Tests are not runtime architecture. Thirty-one cases cover positive grounding, identity continuity, ambiguity, stale/substituted/out-of-workspace evidence, mutation layers, Replay order, projection continuity, authority boundaries, and real AiCLI composition. The breadth is proportionate to a hash- and lineage-sensitive contract. |
| Superseded G15 expectation | 7 additions, 2 deletions | Compatibility-only test update: the same operational branch now truthfully ends at G31-06 rather than G31-05. |
| G31-06 governance report | 514 additions | Documentation and complete next-generation prompt; no runtime effect. |
| Serialization | No serialization file changed | G31-06 reused `load_json`, `replay_hash`, and `write_json_immutable`. It did not introduce a serializer or persistence subsystem. |

The committed focused-test file contains one extra blank line at EOF. A direct
`git diff --check c04e811a^ c04e811a` therefore reports:

```text
tests/test_g31_06_canonical_repository_scope_grounding.py:558: new blank line at EOF.
```

This contradicts the G31-06 report’s `git diff --check: passed` statement. It
is a repository-hygiene observation, not runtime duplication, and this audit
does not modify the test under its documentation-only constraint.

## Mandatory reuse comparison

| Required concern | Existing repository evidence | G31-06 behavior | Finding |
|---|---|---|---|
| Repository path discovery | `capability_audit_runtime.detect_capabilities` scans canonical runtime/test/governance locations and associates implementation and test files by capability key | Calls it directly and accepts only one exact already-decided key with one implementation and existing tests | Reused; no second index or broad scanner |
| Symbol discovery | No public Repository Cognition contract returns symbol identities for the selected source/test paths. `platform_capability_composition_coverage` does not provide symbols | Parses only files returned by `detect_capabilities` and records top-level class/function names and lines | New bounded evidence extraction, not duplicated discovery; ownership observation remains visible |
| AST inspection | Repository search found no reusable generic AST-symbol evidence function; the other AST usage is capability-specific | Uses one local `ast.parse` pass per already-selected file | Necessary for the requested symbol evidence; not a new general framework |
| Content hashing | `replay_hash` is canonical JSON hashing; generation/capability evidence modules independently hash raw file bytes with SHA-256 | Uses raw-byte SHA-256 for file identity and `replay_hash` for structured evidence | Algorithmic idiom repeats, but no public raw-file evidence contract exists |
| Symbol hashing | No existing public symbol-evidence hash contract | Binds symbol name, kind, line, path, and file hash through `replay_hash` | Necessary new field contract, not duplicated capability |
| Workspace boundary validation | Filesystem, ingress, mutation, and patch modules contain scope-specific containment/path helpers | Resolves only cognition-selected paths and verifies `relative_to(root)` | Semantics are necessary; low-level implementation is locally repeated |
| Stale-evidence detection | Mutation validation has candidate-specific before/after checks; no read-only grounding evidence validator exists | Re-observes the selected file and compares the complete evidence object during reconstruction | Necessary grounding-specific tamper check |
| Mutation-layer classification | `platform_change_impact_analysis_runtime._constitutional_layer` | Calls the existing function directly and fails closed for L0/L1 | Reused exactly; no new layer map |
| Source-to-test association | `detect_capabilities` owns filename-key association | Consumes its `implementation` and `tests` arrays unchanged | Reused exactly |
| Immutable artifact validation | Existing runtimes validate their own artifact types; transport exposes `verify_replay_hash` | G31-06 validates its new artifact and nested existing artifacts; local `_verify_hash` repeats the generic helper | Contract-specific validation is essential; one small generic helper is duplicated |
| Replay wrapper validation and reconstruction | `load_json`, `replay_hash`, `verify_replay_hash`, `write_json_immutable`; nested G31-05 reconstructor | Reuses transport and upstream reconstruction but implements its two artifact-specific steps and ordering | No new Replay subsystem; local hash call could use the public verifier |
| Canonical presentation projection | Existing Platform Core turn summaries, runtime-entry projection, and reference AiCLI renderer | Adds one summary projection, one transport projection, and eight rendered lines | Thin layer separation; no semantic duplication between CLI files |

## Direct architectural answers

1. **Does the new module only compose and bind existing Repository Cognition
   evidence?** No, not literally. It composes existing capability-audit path
   evidence and additionally materializes raw-file hashes and top-level symbol
   evidence because the repository exposes no existing immutable symbol-rich
   contract. The enrichment is restricted to already-selected paths.
2. **Does it perform new repository discovery that belongs to Repository
   Cognition?** It does not discover or select additional targets. It performs
   bounded evidence observation of target contents and symbols. That ownership
   distinction is the principal minimality observation.
3. **Does it duplicate generic hashing, validation, or Replay helpers?** It
   reuses canonical serialization/persistence but duplicates one public hash
   verification helper and repeats relative-path normalization. Artifact-
   specific validation and Replay ordering are necessary and are not a second
   subsystem.
4. **Is logic duplicated between `aigol_cli.py` and `aicli.py`?** No.
   `aigol_cli.py` invokes the runtime and projects a canonical turn summary;
   `aicli.py` only formats already-projected values.
5. **Could the same behavior be implemented substantially more simply using
   existing contracts?** No. A few low-level helpers could be consolidated,
   but the artifact, target evidence, ten upstream identities, projection
   continuity, freshness checks, and nested Replay would remain.
6. **Are all modified runtime files necessary?** Yes. They respectively own
   grounding, Worker-request projection, runtime composition, Human Interface
   transport, and terminal rendering. Removing one would either lose the
   certified transition or move responsibility into the wrong layer.
7. **Is the new canonical artifact justified?** Yes. The source G31-05 Worker
   request intentionally represents unresolved scope and lacks cognition
   snapshot, target/symbol evidence, mutation-layer evidence, and the full
   grounding lineage. Mutating it alone would erase the evidence-producing
   transition and weaken fail-closed reconstruction.
8. **Does code broaden G31-06 beyond repository-scope grounding?** No. It does
   not authorize, select, assign, dispatch, invoke, validate implementation
   output, certify, or mutate. `ready_for_separate_dispatch_governance` is a
   later-stage eligibility statement, not authorization or dispatch.

## Duplication and minimality finding

No duplicated Repository Cognition capability, repository index, planner,
router, selector, Worker payload, authorization system, Replay subsystem, or
presentation authority was introduced.

The G31-06 runtime is larger than a simple mapping because the required output
is an immutable, reconstructable evidence transition. Most of the size is the
canonical artifact, nested lineage checks, target freshness, projection
continuity, explicit false-authority boundaries, and two-step Replay. Removing
those sections would reduce lines while weakening the required contract.

Three low-level functions repeat available or equivalent validation idioms:

- `_verify_hash` duplicates `verify_replay_hash` with `hash_field="artifact_hash"`;
- `_relative_path` overlaps existing repository-relative path validators;
- `_unique_relative_paths` repeats the same path semantics for the existing
  Worker request.

This is bounded implementation duplication, not architectural duplication.
It does not change ownership or observed behavior and is too small to show
that G31-06 requires a separate reduction generation. A future consumer must
not copy these helpers again.

## Operational-preservation evidence

Focused validation command:

```bash
python -m pytest tests/test_g31_06_canonical_repository_scope_grounding.py tests/test_capability_audit_runtime_v1.py tests/test_g14_08a_platform_core_project_services_extraction_v1.py tests/test_g14_27_unified_human_interface_runtime_project_services_v1.py -q
```

Result:

```text
44 passed, 0 skipped, 0 failed in 2.73s
```

The passing evidence confirms:

- deterministic positive source/test grounding;
- material ambiguity and missing evidence fail closed;
- no invented target or command;
- stale, substituted, invalid, or out-of-workspace evidence rejection;
- exact G31-04/G31-05 identity continuity;
- grounding and nested Replay reconstruction and reordering rejection;
- thin AiCLI projection with no repository selection;
- no execution authorization;
- no Provider or Worker selection, assignment, dispatch, or invocation;
- no repository mutation.

The full suite was not rerun because the focused and relevant Repository
Cognition/project-service evidence passed and the audit changed documentation
only.

## Deterministic verdict

`G31_06_MINIMALITY_ACCEPTED_WITH_OBSERVATIONS`

The canonical artifact and all five modified runtime surfaces are justified.
The implementation does not duplicate an architectural capability and cannot
be substantially simplified without losing lineage, freshness, ambiguity,
tamper, Replay, or terminal-operability guarantees. The bounded low-level
helper duplication and committed trailing blank line remain visible
observations.

## Exactly one bounded recommendation

Accept G31-06 without runtime reduction and proceed to one G31-08 execution-
authorization binding that consumes the G31-06 artifact unchanged; G31-08
must reuse existing path and hash validators and must not copy the observed
local helper idioms into the authorization layer.

No-copy/paste progress remains **87%**, unchanged from G31-06. This is an
evidence-scoped planning estimate, not a production-readiness or certification
claim.

## Proposed Generation 31-08 prompt

```text
# Generation 31-08 — Canonically Grounded Worker Request Execution Authorization Binding

Treat Generation 30 and accepted G31-02, G31-04, G31-05, G31-06, and the
G31-07 minimality audit as immutable baselines.

G31-07 verdict:

G31_06_MINIMALITY_ACCEPTED_WITH_OBSERVATIONS

Accepted G31-06 verdict:

APPROVED_DURABLE_GOVERNED_WORK_CANONICAL_REPOSITORY_SCOPE_GROUNDING_OPERATIONAL

First true blocker:

CANONICALLY_GROUNDED_WORKER_REQUEST_EXECUTION_AUTHORIZATION_BINDING_ABSENT

Primary priority:

NO_COPY_PASTE_CONVERSATIONAL_GOVERNED_DEVELOPMENT_THROUGH_AICLI

## Objective

Implement exactly one transition.

Bind one valid G31-06 canonically grounded Worker request into the existing
separate execution-authorization review lifecycle.

Produce either:

1. one existing immutable execution-authorization request or candidate bound
   to the exact grounded scope and every upstream identity; or
2. an existing owner-specific clarification or explicit fail-closed state when
   authorization evidence is insufficient.

Do not select, assign, dispatch, or invoke a Worker. Do not invoke a Provider
or mutate the repository.

## Required reuse

Reuse existing:

- G31-04 approval identities and approval consumption;
- G31-05 task package and Worker payload lineage;
- G31-06 Repository Cognition evidence, grounding artifact, and grounded
  Worker-request projection;
- execution-authorization request, policy, validation, and Replay contracts;
- Governance and distinct human-authorization boundaries;
- Human Conversation Experience and Canonical Presentation;
- public transport hash validation and existing repository-relative path
  validation contracts.

Do not create another approval system, authorization system, Worker request,
policy engine, router, selector, clarification system, Repository Cognition
service, or Replay subsystem.

Do not copy the G31-06 local `_verify_hash`, `_relative_path`, or
`_unique_relative_paths` idioms into the new binding. Reuse existing public
validation contracts.

Before implementation, document the exact reusable authorization contracts
and the smallest required binding.

## Required behavior

For one valid G31-06 artifact:

approved G31-04 identities
  -> G31-05 goal-faithful Worker payload
  -> G31-06 exact repository grounding
  -> existing execution-authorization review/request contract
  -> immutable authorization decision evidence or fail-closed review state
  -> stop before Worker selection, assignment, dispatch, or invocation

The authorization scope must equal the grounded workspace-relative paths,
symbols, focused tests, mutation layers, validation requirements, objective,
and approved bounded work. It must not broaden targets, operations, commands,
authority, or lifecycle stage.

Proposal approval is not execution authorization. If the existing lifecycle
requires a distinct human authorization decision, preserve and present that
checkpoint instead of manufacturing authorization from `/approve`.

## Fail-closed requirements

Reject before authorization readiness if:

- any G31-04, G31-05, or G31-06 identity changes;
- Repository Cognition evidence is stale, missing, substituted, or reordered;
- grounded paths, symbols, focused tests, mutation layers, or hashes change;
- requested authority exceeds the approved and grounded scope;
- policy, approval, authorization, or Replay lineage is absent or invalid;
- a target is L0/L1 or otherwise incompatible;
- authorization would imply Worker/Provider invocation or repository mutation.

No invalid evidence may partially authorize work or influence later Worker
selection.

## Minimal-change constraint

Prefer one existing-function binding. Introduce at most one bounded binding
artifact only if the existing authorization contract cannot represent the
transition directly.

Do not add general authorization architecture or bundle Worker selection.
Stop and report deterministic evidence if broad changes are required.

In the final change-size report, distinguish canonical contract,
artifact-specific validation, Replay, compatibility, and presentation lines
from duplicated helper logic.

## Focused tests

Prove at minimum:

- all upstream identities and grounded targets are consumed unchanged;
- proposal approval remains distinct from execution authorization;
- authorization scope equals the G31-06 evidence exactly;
- missing or insufficient authorization evidence clarifies or fails closed;
- stale, substituted, reordered, broadened, or incompatible scope fails closed;
- no command, target, authority, Worker, or Provider is invented;
- no Worker selection, assignment, dispatch, invocation, or mutation occurs;
- AiCLI owns no authorization or policy semantics;
- complete Replay reconstructs and rejects tampering;
- unrelated G28-G31 paths remain unchanged.

## Real terminal validation

Use a disposable Git repository with one existing implementation and one
focused test. Through real PTY-backed `./aicli`, use one ordinary bounded
natural-language change request and demonstrate:

1. G31-04 proposal and approval;
2. G31-05 Worker payload;
3. G31-06 exact repository grounding;
4. the separate authorization review/request state;
5. one missing, tampered, or broadened authorization fail-closed case;
6. complete Replay reconstruction;
7. truthful stop before Worker selection and dispatch.

The user must not supply paths, internal JSON, capability names, prepared
artifacts, a Codex prompt, or shell bridges. Remove the disposable repository.

## Validation

Run and report exact pass, skip, and failure counts for:

- focused G31-08 tests;
- G31-04 through G31-06 regressions;
- execution authorization and human approval;
- Repository Cognition, PPP, and Worker-request tests;
- clarification, Human Interface, and AiCLI;
- G28, G29, G30, and G31-02;
- Replay and Governance;
- `py_compile`;
- `git diff --check`;
- full repository suite.

## Documentation

Add:

docs/governance/G31_08_CANONICALLY_GROUNDED_WORKER_REQUEST_EXECUTION_AUTHORIZATION_BINDING.md

Document reuse, exact authorization contract, identity and scope continuity,
human checkpoint semantics, Replay, authority boundaries, PTY evidence,
validation, change size, and exactly one next blocker or readiness verdict.

## Non-goals

Do not:

- redesign certified architecture;
- merge proposal approval with execution authorization;
- modify the accepted G31-06 artifact or its runtime behavior;
- select, assign, dispatch, or invoke a Worker;
- invoke a Provider;
- mutate the repository;
- implement Worker cognition, validation, repair, certification, or completion;
- repair Provider availability or governance hook drift;
- add products, domains, interfaces, dashboards, or deployment;
- bundle downstream blockers;
- claim complete no-copy/paste readiness.

## Required final report

Provide:

1. implementation verdict;
2. changed files and change-size report;
3. reused authorization capabilities;
4. exact authorization artifact and evidence contract;
5. positive and fail-closed PTY results;
6. Replay and tamper evidence;
7. approval-versus-authorization assessment;
8. authority confirmation;
9. exact validation and governance results;
10. exactly one next blocker or readiness verdict;
11. no-copy/paste progress using the G31-03-G31-07 denominator;
12. exact git status and commit commands;
13. complete bounded G31-09 prompt.

Architectural minimalism is mandatory.
```
