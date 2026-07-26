# Generation 31-24G-R04-R04-R21C Adapter-Neutral Worker Selection Lineage Resolver Implementation

Status: completed constitutional implementation.

Date: 2026-07-26

Deterministic verdict:

`G31_ADAPTER_NEUTRAL_WORKER_SELECTION_LINEAGE_RESOLVER_IMPLEMENTED`

Exactly one next state:

`G31_24G_R04_R04_R21D_REPLAY_CAPABLE_WORKER_FAMILY_EXPANSION_OPERATIONAL_READINESS_AUDIT_REQUIRED`

## Certified baseline and blocker

Generation 30 and the accepted Generation 31 baseline through R21B are
treated as constitutionally closed. R21B identified the first blocker:
generic Worker Invocation Request and Worker Assignment interpreted the
Filesystem authenticated-replacement selection schema directly.

R21C removes that worker-specific knowledge from both generic owners without
changing their four-event Replay formats, authority, or lifecycle semantics.

## Implementation

Generic Worker Invocation Request now exposes one invocation-scoped
`WorkerSelectionLineageResolver` callable boundary. A supplied resolver must
return one immutable `WORKER_SELECTION_LINEAGE_PROJECTION_V1` artifact before
Invocation Request evidence can be created.

The generic boundary authenticates:

- the projection artifact hash;
- its opaque source-lineage commitment;
- Authorization, packet, handoff, chain, and selection commitments;
- the exact immutable selection Replay and Replay hash;
- worker identity, version, category, role, capability, authority profile,
  and domain;
- selection context and registry commitments;
- certification reference and hash presence;
- request/projection continuity;
- session containment; and
- false authority flags.

Unsupported projections, substituted selection evidence, cross-session
references, inconsistent hashes, and invalid resolver dependencies fail
before Invocation Request evidence.

The Filesystem-specific resolver now exclusively authenticates:

1. `AUTHENTICATED_REPLACE_REQUEST_V2`;
2. the immutable two-event Authorization-consumption prefix;
3. the certified Filesystem Worker selection Replay;
4. the consumed replacement selection context;
5. the accepted Worker selection certification; and
6. all request, Authorization, capability, registry, and session
   commitments.

Only after those checks does it produce the worker-neutral immutable
projection. The original Filesystem compatibility lineage remains an opaque,
hash-committed payload for Filesystem-specific downstream reconstruction;
generic owners do not interpret it.

Common Entry constructs a local resolver closure and supplies it to the
generic owner for exactly one invocation. No resolver registry, mutable
global, routing state, context manager, or constitutional-owner change was
introduced.

Worker Assignment now validates and consumes only the canonical neutral
projection. It no longer imports or interprets authenticated-replacement
schema constants or consumed-replacement fields.

## Constitutional ownership

| Property | R21C result |
| --- | --- |
| Worker selection authority | Unchanged and non-authoritative |
| Worker-specific lineage authentication | Filesystem adapter only |
| Invocation Request ownership | Unchanged |
| Invocation Request Replay | Existing four events unchanged |
| Assignment ownership | Unchanged |
| Assignment Replay | Existing four events unchanged |
| Authorization ownership and formats | Unchanged |
| Result Capture and Result Validation ownership | Unchanged |
| Replay Review and Governed Termination ownership | Unchanged |
| Replay and Certification ownership | Unchanged |
| Generic historical default | Unchanged |
| Resolver lifetime | One Common Entry invocation |
| Registry, mutable global, context manager, routing state | None introduced |
| Unsupported or substituted lineage | Fails before request evidence |

The boundary is non-authoritative. It does not select, assign, dispatch,
invoke, execute, validate, review, terminate, certify, or mutate. Those
operations remain with their existing owners.

## Focused and regression validation

Focused R21C tests prove:

1. one Filesystem resolver is supplied and called exactly once;
2. the canonical projection reconstructs through generic Invocation Request;
3. unsupported lineage fails before request evidence;
4. substituted selection evidence fails before request evidence;
5. cross-session lineage fails before request evidence;
6. Assignment retains its unchanged four-event Replay; and
7. historical generic Invocation Request and Assignment defaults remain
   unchanged.

Validation before the complete suite:

- focused R21C tests: `7 passed`;
- affected Invocation Request, Assignment, lifecycle, Replay Review,
  Governed Termination, and Certification regressions: `156 passed`;
- complete Generation 31 R04 transition group: `300 passed`;
- governance and protected-evidence regressions: `12 passed`;
- targeted `py_compile`: passed;
- protected hashes: unchanged;
- parent `git diff --check`: passed; and
- all nested repository `git diff --check` checks: passed.

One preliminary affected-test command named a nonexistent R20C test file and
therefore collected zero tests. The corrected affected group passed 156
tests. This was command classification only and required no implementation
repair.

## Complete repository suite

The complete repository suite was executed exactly once:

```text
6873 passed, 4 skipped in 4461.42s (1:14:21)
```

No failure occurred. No repaired-node validation was required, and the
complete suite was not executed a second time.

## Protected evidence and conformance

The protected hashes remain equal to the accepted R20B baseline:

| Protected path | SHA-256 |
| --- | --- |
| `diagnostic_evidence.json` | `21546ed151c165c6364aa914d892c34b117ef1ab664ae09d8e2c2a5327bcc8df` |
| `governed_return.json` | `ee57877ceea7d85bd9e3bb29aca64f3637384a7346a5b6a4c4f922c87cb2bcf7` |
| `lineage.json` | `8c47abb9a7c238c9f527e54dd88aa304edbca03b97ea630a4907b4ef139b3a08` |
| `provider_stderr.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `provider_stdout.txt` | `f2fec907b48e7162211f26bbe94352d40f4f6c4380ab3aa4256d072b7c602f30` |
| `governed_returns.jsonl` | `71b085174a274b870617c21810d9a496421985675ae0945f4b56bd3afe7b1118` |

No protected evidence file was modified. Governance regression validation
passed. Repository conformance remains partially conformant solely because
of the two previously accepted hook findings; R21C introduces no new
finding and does not conceal the existing limitation.

No file was staged or committed automatically.
