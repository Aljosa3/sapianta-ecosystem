# Generation 31-24G-R04-R04-R19E Filesystem Replace Worker Schema-Aware Authorization Lineage Resolver Implementation

Status: completed constitutional implementation.

Date: 2026-07-25

Deterministic verdict:

`G31_FILESYSTEM_REPLACE_WORKER_SCHEMA_AWARE_AUTHORIZATION_LINEAGE_RESOLVER_IMPLEMENTED`

Exactly one next state:

`G31_24G_R04_R04_R19F_FILESYSTEM_REPLACE_WORKER_POST_EXECUTION_REPLAY_REVIEW_OPERATIONAL_READINESS_AUDIT_REQUIRED`

## Certified baseline and implementation scope

G0-G30 and accepted Generation 31 evidence through R19D are treated as
constitutionally closed and immutable. The immediate implementation baseline
is:

- commit: `88a45e16bf19e884c4dccee2ea900ae8e59e751c`;
- subject:
  `docs(governance): document replay review binding blocker`;
- R19D verdict:
  `G31_FILESYSTEM_REPLACE_WORKER_AUTHORIZATION_LINEAGE_TO_POST_EXECUTION_REPLAY_REVIEW_COMPATIBILITY_STRATEGY_DEFINED`; and
- R19D first mismatch:
  `AUTHENTICATED_REPLACEMENT_INVOCATION_REQUEST_REUSES_GENERIC_AUTHORIZATION_REFERENCE_WITH_DIFFERENT_REPLAY_SCHEMA_AND_HASH_SEMANTICS`.

The implementation changes only the compatibility boundary between the
certified authenticated-replacement Invocation Request lineage and the
unchanged generic Post-Execution Replay Review owner.

It does not redesign or modify either Authorization owner, Invocation,
Result Validation, Post-Execution Replay Review, Replay formats,
certification, authority, or the constitutional contract.

## Implementation

### Non-authoritative schema-aware resolver

`aigol.runtime.filesystem_replace_worker_schema_aware_authorization_lineage_resolver_runtime`
provides:

```text
resolve_authorization_lineage
review_validated_filesystem_replace_worker_result
reconstruct_filesystem_replace_worker_post_execution_replay_review_binding
```

The resolver reconstructs the immutable Worker Invocation Request before
selecting Authorization semantics. It does not select a schema by probing
filenames.

When no authenticated-replacement compatibility lineage exists, it preserves
the historical generic path:

- owner/schema: `AIGOL_EXECUTION_AUTHORIZATION_RUNTIME_V1`;
- Replay commitment: Authorization artifact hash; and
- typed commitment: `AUTHORIZATION_ARTIFACT_HASH`.

When the Invocation Request contains exactly
`AUTHENTICATED_REPLACEMENT_SELECTION_LINEAGE_V1`, it uses:

- the existing authenticated-replacement request validator;
- the existing three-event Authorization binding Replay reconstructor;
- owner/schema:
  `G31_EXISTING_MUTATION_AUTHORIZATION_BINDING_REPLAY_V1`;
- Replay commitment: Authorization record hash; and
- typed commitment: `AUTHORIZATION_RECORD_HASH`.

Unknown, malformed, incomplete, conflicting, substituted, or cross-session
lineage fails closed.

### Immutable compatibility-lineage authentication

For the authenticated-replacement path, the resolver authenticates:

- complete Invocation Request compatibility-lineage reconstruction;
- the authenticated replacement request and session root;
- exact Authorization identity, record hash, status, and scope;
- canonical Authorization actor;
- exact three-event Authorization Replay reference and Replay hash;
- consumed replacement selection-context chain;
- Invocation Request evidence and artifact continuity; and
- session-bounded Replay ownership.

The result is an in-memory, non-authoritative normalized view. The record
hash is exposed as a typed record commitment and is not reclassified as an
Authorization artifact hash.

The resolver writes no artifact, Replay event, ledger entry, target, or
repository state.

### Unchanged Replay Review ownership

The compatibility adapter reconstructs the complete certified R18C evidence
package before review admission. It verifies the immutable:

- validation evidence, classification, artifact, result, and four-event
  Replay;
- Result Capture identity and commitment;
- Worker-output artifact and payload commitments;
- terminal Worker capture and seven-event Worker Replay;
- journal, post-write result, and completion commitments;
- Authorization record and source Replay commitments; and
- historical repository mutation state.

After admission, it invokes
`post_execution_replay_review_runtime.review_validated_worker_result`
exactly once.

The existing generic Replay Review runtime remains solely responsible for:

- review admission and integrity classification;
- review evidence, classification, artifact, and result construction;
- `REVIEW_COMPLETED` or `FAILED_CLOSED`;
- writing its unchanged four-event Replay; and
- deterministic review reconstruction.

The source of `post_execution_replay_review_runtime` is unchanged.

For the duration of one admission or reconstruction call, the adapter
presents the resolver-backed lineage loader under a process-local reentrant
lock. The presentation:

- consumes only immutable certified evidence;
- grants no authority to the resolver;
- owns no persistent state;
- rejects a conflicting loader before review; and
- restores the exact original generic loader in `finally`.

Both Authorization Replay formats and both Authorization owners therefore
remain unchanged.

### Duplicate, substitution, and session protection

Before canonical review, the adapter requires an unused review destination
inside the certified session. It rejects an existing review associated with
the same:

- Result Validation identity or artifact hash; or
- Result Capture identity or artifact hash.

The adapter also fails before canonical review on substituted validation
evidence, Authorization Replay, compatibility lineage, Worker output,
terminal capture, Worker Replay, journal, completion evidence, or
cross-session references.

Canonical `FAILED_CLOSED` is preserved without a second generic review call.
Historical repository mutation remains visible on success and failure.

### Deterministic review reconstruction

After canonical success, the adapter reconstructs the unchanged review
Replay:

```text
review evidence
-> review classification
-> review artifact
-> review result
```

It requires:

- exactly four review artifacts;
- exact Result Validation and Result Capture identities and hashes;
- exact typed Authorization record commitment and source Replay hash;
- exact Worker-output, payload, capture, Worker Replay, validation Replay,
  and completion commitments;
- all generic review integrity assessments equal
  `INTEGRITY_VERIFIED`;
- `result_validated = true`;
- `post_execution_replay_reviewed = true`;
- no task-outcome satisfaction evaluation;
- no result acceptance;
- no final Execution certification;
- no Provider invocation or command execution; and
- no governance or Replay mutation.

Binding reconstruction repeats the complete R18C authentication and the same
schema-aware immutable-lineage resolution.

### Common Entry continuation

Common Entry invokes the compatibility adapter only after R18C validation and
reconstruction succeed. It invokes the adapter once, reconstructs the R19E
binding, and requires exact Authorization, validation, output, Worker,
journal, completion, and review continuity.

The resulting state advances only Post-Execution Replay Review:

- `result_validated = true`;
- `post_execution_replay_reviewed = true`;
- `task_outcome_satisfaction_evaluated = false`;
- `task_outcome_satisfied = false`;
- the review artifact and binding keep `result_accepted = false`;
- any pre-existing application-level acceptance state remains unchanged;
- `execution_certified = false`;
- `provider_invoked = false`;
- `command_executed = false`; and
- `repository_mutated = true`.

The Common Entry presentation records completed Replay Review and explicitly
states that no result acceptance has occurred. AiCLI remains
authority-neutral.

## Focused and regression evidence

The focused R19E tests prove:

1. immutable authenticated-replacement lineage resolves to the record-hash
   schema without changing either Authorization owner;
2. the unchanged generic Replay Review entry is invoked exactly once;
3. its unchanged four-event Replay reconstructs through the same resolver;
4. the temporary lineage presentation restores the exact original generic
   loader;
5. substituted Authorization Replay, compatibility lineage, validation
   artifact, or journal evidence fails closed;
6. duplicate and cross-session review fails closed;
7. canonical `FAILED_CLOSED` remains fail-closed; and
8. the resolver owns no Replay writer and cannot accept or certify results.

Validation completed before the full suite:

- focused R19E tests: `8 passed`;
- affected Authorization-lineage, compatibility, validation, and Replay
  Review regressions: `79 passed`;
- Generation 31 R04 transition regressions after repaired-node validation:
  `274 passed`;
- governance and protected-evidence regressions: `14 passed`;
- targeted `py_compile`: passed; and
- parent `git diff --check`: passed.

The first affected transition run exposed two obsolete read-only
reconstruction-count assertions. R19E performs one R18C authentication before
review and repeats that authentication during binding reconstruction,
increasing read-only Invocation and Execution reconstruction counts without
adding Invocation, execution, Worker, validation, or review calls.

Only the two affected assertions were updated. Their exact repaired nodes
passed, and the affected transition group then passed before the complete
suite.

Two initial focused failures were test-fixture construction issues in the new
R19E module. Only those new fixtures were corrected; the focused module then
passed.

## Complete repository suite

The complete repository suite was executed exactly once:

```text
6849 passed, 4 skipped in 4477.14s (1:14:37)
```

No failure occurred. No post-suite repair or repaired-node validation was
required, and the complete suite was not executed a second time.

## Constitutional preservation

| Evidence or action | Constitutional owner after R19E |
| --- | --- |
| Existing-record Authorization and three-event Replay | Existing G31 Authorization owner |
| Generic Execution Authorization and four-event Replay | Existing Execution Authorization owner |
| Schema discrimination and typed commitment verification | Non-authoritative R19E resolver |
| Invocation Request compatibility evidence | Existing Worker Invocation Request owner |
| Result Validation artifact and four-event Replay | Existing Result Validation owner |
| Review artifacts, status, and four-event Replay | Existing Post-Execution Replay Review owner |
| Historical filesystem mutation | Existing Filesystem Replace Worker lineage |
| Acceptance and final certification | Unchanged and outside R19E |

R19E introduces no second Authorization, Invocation, Worker, Result
Validation, Replay Review, Replay, mutation, acceptance, or certification
path.

## Final static validation

Final `py_compile` passed for every changed Python module and test. Parent
`git diff --check`, staged `git diff --cached --check`, and all three nested
repository `git diff --check` checks passed. The staging area is empty.

The nested repositories are clean at:

- `sapianta-domain-credit`:
  `8615e1e290471a67e4e764c6ab2138340bc7936f`;
- `sapianta_system`:
  `3183bab71f8f30397c0309dd2e6d846d14a11f66`; and
- `sapianta-domain-trading`:
  `d3038dc4ba36ffbaee9161172b4c852e8e6acbda`.

The six protected hashes equal the accepted R19D baseline after focused,
regression, complete-suite, and final static validation:

| Protected path | SHA-256 |
| --- | --- |
| `diagnostic_evidence.json` | `21546ed151c165c6364aa914d892c34b117ef1ab664ae09d8e2c2a5327bcc8df` |
| `governed_return.json` | `ee57877ceea7d85bd9e3bb29aca64f3637384a7346a5b6a4c4f922c87cb2bcf7` |
| `lineage.json` | `8c47abb9a7c238c9f527e54dd88aa304edbca03b97ea630a4907b4ef139b3a08` |
| `provider_stderr.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `provider_stdout.txt` | `f2fec907b48e7162211f26bbe94352d40f4f6c4380ab3aa4256d072b7c602f30` |
| `governed_returns.jsonl` | `71b085174a274b870617c21810d9a496421985675ae0945f4b56bd3afe7b1118` |

No protected file or nested repository was changed. No file was staged or
committed by this generation.
