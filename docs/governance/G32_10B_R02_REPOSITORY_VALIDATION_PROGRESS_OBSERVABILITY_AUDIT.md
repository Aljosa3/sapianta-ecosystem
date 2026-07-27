# Generation 32-10B-R02 Repository Validation Progress Observability Audit

Status: completed `AUDIT_ONLY` observability and developer-experience assessment.

Date: 2026-07-27

Certified baseline preserved:

- Platform Core Baseline V31;
- Certified Filesystem Adapter Executable Constitutional Contract V1;
- Immutable Constitutional Evidence Manifest V1;
- Automatic Constitutional Validator Kernel V1;
- G32-10B Validator Constitutional Conformance Audit;
- G32-10B-R01 Repository Regression Runtime Investigation.

Deterministic assessment:

`PASSIVE_REPOSITORY_VALIDATION_PROGRESS_OBSERVABILITY_IS_ARCHITECTURALLY_ADMISSIBLE_AS_DEVELOPER_TOOLING`

This audit changes no runtime behavior, Validator behavior, Replay semantics,
Governance, Certification, evidence, test, configuration, or constitutional
artifact. It creates no progress instrumentation and does not issue a
Certification determination.

## Executive determination

Passive progress reporting for a developer-launched repository validation is
architecturally admissible, provided it remains outside constitutional
execution and does not become evidence, authority, a validation input, or a
test-selection mechanism.

The completed regression (`6,897 passed`, `4 skipped`, `01:19:24`) establishes
that long-running validation is normal for this repository. G32-10B-R01
established that the dominant prior cost was duplicate external orchestration,
not the Validator Kernel. Progress visibility should therefore observe the
external pytest process rather than add behavior to the Validator, Replay,
Governance, Certification, Workers, or test subjects.

## Current execution observability assessment

| Surface | Existing visibility | Limitation for repository regression |
| --- | --- | --- |
| Root pytest | Native terminal dots/percentages and final summary. | No stable current test name, completed/remaining count API, elapsed display, ETA, heartbeat, or phase model in the repository. |
| Root pytest configuration | `pytest.ini` declares the two collection paths and ignored generated roots. | No plugin, hook, parallel runner, reporter, or progress observer is configured. |
| Validation command runner | Captures command, exit code, stdout/stderr hashes and bounded excerpts after `subprocess.run` returns. | `capture_output=True` and a 4,096-byte result limit mean it cannot expose live pytest output or the currently running node. |
| Governed validation suite | Reports planned/executed command counts and terminal command results. | It is command-granular, not test-granular; status is persisted only after each bounded command returns. |
| AiCLI runtime progress | Existing runtime-progress artifacts expose stage, current activity, elapsed time, progress percentage, ETA, and watch rendering. | It is for interactive runtime workflows, not pytest; it deliberately writes replay-visible immutable snapshots. |
| AiCLI conversational progress | Emits stage lines for routing, cognition, provider, comparison, continuity, clarification, result assembly, and Replay. | It is bound to a conversational turn and also produces replay-visible progress evidence. |
| Read-only runtime observability | Inspectors can read persisted runtime, capability, policy, continuity, and lineage artifacts. | It is post/persisted-runtime inspection, not a live repository-test process monitor. |
| AiCLI `status` | Displays current readiness states. | It is a static readiness summary, not a live execution status source. |
| Logging | CLI and runtime modules use explicit result rendering and output callbacks. | No repository-wide structured logging bus or live validation event stream exists. |

## Existing available signals

The following signals already exist, but they have distinct ownership and
must not be conflated:

| Signal | Available now | Owner/boundary |
| --- | --- | --- |
| Repository command and terminal exit status | Yes | External shell or governed validation command result. |
| Native pytest aggregate progress | Yes, through pytest terminal output. | Pytest presentation only. |
| Validation command count and terminal pass/fail | Yes, for governed validation suites. | Existing validation-suite artifacts. |
| Runtime stage, activity, elapsed time and ETA | Yes. | AiCLI runtime-progress subsystem; replay-visible. |
| Active runtime/capability/policy/continuity/lineage state | Yes, after its artifacts exist. | Read-only runtime observability inspectors. |
| Worker execution status | Yes, in Worker result/capture artifacts. | Worker lifecycle and replay boundaries. |
| Replay and certification stages | Yes, only where each runtime emits its own artifacts. | Existing stage-local Replay/Certification ownership. |

None of these sources supplies a generic, live mapping from a pytest node to
an active Worker, capability, Replay stage, or Certification stage. Such a
mapping cannot be inferred safely from a test filename or test function name.

## Missing repository-validation information

The root repository regression currently lacks a passive, process-local source
for:

- collection start/complete and collected-node count;
- current pytest node identifier and its current phase (setup, call, teardown);
- completed, skipped, failed, and remaining node counts;
- elapsed wall-clock time and time since the last completed node;
- an explicitly advisory estimated remaining time;
- process-alive/last-event health indication;
- a clear distinction between collection, test execution, and final summary.

Active Worker, capability, Replay, and Certification stage are also unavailable
for a generic repository validation. Those are absent by design, rather than
missing constitutional data: many tests are unit/static tests and have no
runtime capability or Worker lifecycle. Reporting them as a guessed status
would violate the evidence and authority boundaries.

## Candidate passive architecture

The recommended future shape is an **external validation-progress observer**,
enabled only by a developer or release operator for one explicit pytest command.
It is not a Platform Core capability and must not be invoked by the Validator.

```text
developer terminal
  └─ validation-progress observer (developer tooling only)
       ├─ launches or attaches to one explicit pytest command
       ├─ receives pytest lifecycle events
       │    collection → node start → node report → session finish
       ├─ holds ephemeral counters and monotonic elapsed time
       └─ renders terminal/IDE status only

pytest/test execution ─────────────── unchanged
constitutional runtime/replay ─────── unchanged and not consulted
governance/certification ──────────── unchanged and not consulted
```

If implemented later, the observer may use a narrowly scoped pytest reporting
plugin or a compatible event adapter. Its only permitted event fields should
be the externally observable node id, pytest phase, outcome, collected count,
monotonic timestamps, process exit code, and explicit command identity. It
must not import AiGOL runtime code, construct constitutional artifacts, select
tests, retry tests, suppress failures, change fixtures, mutate the repository,
or write under a Replay/evidence root.

Recommended display model:

| Developer signal | Passive derivation | Status |
| --- | --- | --- |
| Validation phase | Pytest session lifecycle: `COLLECTING`, `EXECUTING`, `FINISHING`, `TERMINAL`. | Feasible. |
| Current test | Latest `pytest_runtest_logstart` node id; phase can be refined from report events. | Feasible. |
| Completed/remaining | Terminal reports divided by collected node count. | Feasible after collection completes. |
| Elapsed runtime | Observer monotonic clock from explicit process start. | Feasible. |
| ETA | Rolling completed-node duration estimate. | Feasible only as non-deterministic, explicitly advisory UX. |
| Health/stall indication | Child process remains alive plus time since last test event. | Feasible as advisory process telemetry, never as a correctness conclusion. |
| Active Worker/capability | No generic derivation. | Not recommended without separately authorized runtime-specific instrumentation. |
| Replay/certification stage | Existing persisted artifacts can be inspected only for a known runtime. | Do not add to generic pytest progress. |

The observer should maintain state in memory and render to the terminal or IDE.
If an operator needs a diagnostic export, it must be outside the repository and
explicitly labelled non-authoritative, non-replay, ephemeral developer
telemetry. An ETA must never enter a test assertion, hash, decision, evidence
artifact, or release/certification conclusion because wall-clock duration is
not deterministic.

## Required separation of concerns

| Layer | Responsibility | Must not receive progress-observer state |
| --- | --- | --- |
| Constitutional execution | Authenticate, validate, and enforce existing bounded semantics. | Current test, ETA, CPU usage, heartbeat, terminal rendering. |
| Execution orchestration | Start exactly authorized validation commands and preserve existing result/replay boundaries. | Any implicit retry, selection, cancellation, or result reinterpretation. |
| Observability | Read existing terminal/process lifecycle information. | Authority, validation outcome control, Replay mutation, evidence issuance. |
| Developer UX | Render progress and advisory health to a human. | Constitutional decisions, Governance conclusions, Certification claims. |

This separation is essential. The existing `runtime_progress_visibility` system
is correctly marked `visibility_only`, but it remains replay-visible and writes
immutable snapshots. Reusing it for pytest progress would be a Replay-surface
change and is therefore outside this audit's constraints. The future repository
observer must instead be a separate developer-tooling surface.

## Recommended future architecture

**Recommendation: external, opt-in, ephemeral pytest lifecycle observer.**

1. The developer selects one exact validation command.
2. The observer records only an in-memory run identity and monotonic start
   time, then observes collection and per-node lifecycle events.
3. It renders a single unambiguous panel: command, phase, current node,
   `completed / collected`, outcome counts, elapsed time, advisory ETA, and
   last-event age.
4. It returns the unmodified pytest exit code and must not alter stdout/stderr
   semantics used by existing evidence capture.
5. It is disabled by default and absent from certified execution paths unless a
   future, separately authorized developer-tooling adoption explicitly adds it.

For the present completed regression, the truthful final display would be
`6,897 passed; 4 skipped; 01:19:24`, while intermediate ETA would be labelled
an estimate rather than an execution or Certification fact.

## Classification

| Dimension | Classification |
| --- | --- |
| Constitutional | Not constitutional; must remain outside L0-L2 constitutional decision semantics. |
| Runtime | Not a production/runtime behavior change. Existing runtime-progress facilities are informative precedent only. |
| Orchestration | Optional external process observation; it must not schedule, retry, or authorize commands. |
| Developer tooling | Primary classification. |
| Future enhancement | Yes; requires separate authorization, design, implementation, and validation. |

## Constitutional impact assessment

The proposed passive observer has no constitutional impact when bounded as
above. It preserves deterministic test execution because it observes events
without becoming an input to pytest, the Validator, or a governed runtime. It
preserves replay correctness and evidence integrity by creating no Replay or
evidence artifact and by not modifying any existing artifact. It is neutral to
Governance and Certification because it neither changes a result nor asserts
that a run is admissible, certified, or healthy.

The only immediate correctness rule is negative: no progress display may be
treated as proof of completion, liveness, conformance, or certification. The
pytest exit status and existing certified evidence remain authoritative.

## Validation performed

Only read-only static inspection was performed:

- root pytest collection configuration and absence of repository pytest hooks;
- validation command runner and governed validation-suite lifecycle;
- AiCLI status, runtime-progress, and conversational-progress surfaces;
- read-only runtime observability inspectors;
- Worker lifecycle and existing Replay/Cerification status surfaces.

No pytest command, runtime command, profile, benchmark, patch, configuration
change, Replay write, or commit was performed.
