# Generation 31-24G-R04-R04-R21E Historical Worker Selection Identity Neutralization

Status: completed constitutional implementation.

Date: 2026-07-26

Deterministic verdict:

`G31_HISTORICAL_WORKER_SELECTION_IDENTITY_NEUTRALIZATION_IMPLEMENTED`

Exactly one next state:

`G31_24G_R04_R04_R21F_REPLAY_CAPABLE_WORKER_FAMILY_EXPANSION_OPERATIONAL_READINESS_AUDIT_REQUIRED`

## Certified baseline and blocker

Generation 30 and the accepted Generation 31 baseline through R21D are
treated as constitutionally closed. R21D identified one remaining worker
family expansion blocker: the historical G31 Invocation Request and
Assignment compatibility path required the literal worker identity
`CODEX`.

The historical execution candidate carries a task-role family, while the
authenticated Resource Selection evidence carries the concrete selected
worker identity. R21E preserves those distinct meanings and removes the
literal identity assumption.

## Implementation

The historical G31 selection loader continues to reconstruct and
authenticate the existing Worker Selection Replay and its Authorization
context before any Invocation Request evidence is created. It now requires:

- a non-empty selected worker identity;
- an eligible `WORKER` or `HYBRID_PROVIDER_WORKER` resource category;
- the canonical `WORKER_ROLE`;
- the non-authoritative `WORKER_AUTHORIZED_TASK_ONLY` profile;
- successful authenticated selection;
- exact Authorization-context continuity; and
- false Provider, Worker-invocation, and Dispatch flags.

For historical G31 lineage, Invocation Request now projects
`target_worker_family` from that authenticated selected worker identity.
The execution candidate remains authenticated through the unchanged
Authorization, candidate, packet, handoff, and chain checks; its task role
remains the unchanged `worker_role`.

Invocation Request validates relational continuity between
`target_worker_family` and the nested authenticated
`selected_resource_id`. Worker Assignment invokes the same validation and
constructs its Worker artifact from that same immutable request-bound
identity.

No worker registry, mutable global, routing state, context manager, Replay
format, or constitutional owner was added or changed.

## Historical compatibility

The existing authenticated G31 selection still chooses `CODEX`; therefore
historical behavior remains valid under the worker-neutral rules. The
historical `g31_lineage` object is unchanged. Invocation Request Replay and
Assignment Replay retain their existing ordered four-event formats.

New Invocation Request evidence now records the authenticated selected
worker identity as `target_worker_family`, rather than reusing the
candidate's task-role family. Artifact and wrapper hashes remain
deterministic and correctly commit this constitutional correction. Replay
Review, Governed Termination, and Certification formats and owners are
unchanged.

## Fail-closed boundaries

Before successful Invocation Request evidence can exist, the implementation
rejects:

- an empty selected identity;
- a selected identity substituted against the request target;
- an unsupported resource category;
- a non-canonical worker role;
- an authoritative or unsupported worker profile;
- a cross-family request target; and
- a cross-session selection Replay.

Assignment independently rechecks the same request-bound identity before
constructing a Worker candidate. Unsupported evidence therefore cannot be
converted into Assignment evidence.

## Constitutional ownership

| Property | R21E result |
| --- | --- |
| Resource Selection ownership | Unchanged |
| Authorization ownership | Unchanged |
| Candidate and packet ownership | Unchanged |
| Invocation Request ownership | Unchanged |
| Worker Assignment ownership | Unchanged |
| Replay ownership and formats | Unchanged |
| Replay Review ownership | Unchanged |
| Governed Termination ownership | Unchanged |
| Certification ownership | Unchanged |
| Worker identity interpretation | Relational and worker-neutral |
| Resolver or adapter lifetime | Existing invocation scope unchanged |
| Registry, mutable global, routing state | None introduced |

The validation helper is non-authoritative. It authenticates continuity but
does not select, assign, dispatch, invoke, execute, review, terminate,
certify, or mutate.

## Validation

Validation completed before the one-time complete repository suite:

- focused R21E tests: `10 passed`;
- affected historical selection, Invocation Request, Assignment, Dispatch,
  Invocation, artifact-projection, and R21C compatibility regressions:
  `89 passed`;
- complete Generation 31 transition suite: `714 passed`;
- governance and protected-evidence regressions: `12 passed`;
- repository `py_compile`: passed;
- governance conformance engine: deterministic, read-only,
  `PARTIALLY_CONFORMANT`, 18 checks passed, 2 accepted hook findings,
  0 critical violations;
- protected hashes: unchanged;
- parent `git diff --check`: passed;
- all nested repository `git diff --check` checks: passed; and
- all nested repositories: clean.

The first focused execution exposed that the historical execution candidate
contains a task-role family rather than the concrete selected identity. The
implementation was corrected to source the request target from authenticated
selection evidence; no historical fixture was weakened. The corrected
focused suite passed.

The initial protected-hash command used an incorrect evidence directory and
found no files. The exact tracked protected paths were then resolved and
verified against the accepted baseline. No evidence file was modified.

## Complete repository suite

The complete repository suite was executed exactly once:

```text
6883 passed, 4 skipped in 4491.46s (1:14:51)
```

No failure occurred. No repaired-node validation was required, and the
complete suite was not executed a second time.

## Protected evidence and conformance

The protected hashes remain equal to the accepted baseline:

| Protected path | SHA-256 |
| --- | --- |
| `diagnostic_evidence.json` | `21546ed151c165c6364aa914d892c34b117ef1ab664ae09d8e2c2a5327bcc8df` |
| `governed_return.json` | `ee57877ceea7d85bd9e3bb29aca64f3637384a7346a5b6a4c4f922c87cb2bcf7` |
| `lineage.json` | `8c47abb9a7c238c9f527e54dd88aa304edbca03b97ea630a4907b4ef139b3a08` |
| `provider_stderr.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `provider_stdout.txt` | `f2fec907b48e7162211f26bbe94352d40f4f6c4380ab3aa4256d072b7c602f30` |
| `governed_returns.jsonl` | `71b085174a274b870617c21810d9a496421985675ae0945f4b56bd3afe7b1118` |

No protected evidence file was modified. Repository conformance remains
partially conformant solely because of the two previously accepted hook
findings. R21E introduces no new conformance finding and does not conceal
the existing limitation.

No file was staged or committed automatically.
