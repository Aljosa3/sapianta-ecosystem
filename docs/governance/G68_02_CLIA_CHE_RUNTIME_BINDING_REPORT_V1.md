# 1. Implementation Summary

Generation: G68-02

Report identity:
G68_02_CLIA_CHE_RUNTIME_BINDING_REPORT_V1

Constitutional baseline: G0 through G68-01, including the Human Interaction
Channel abstraction, Development CLIA, Canonical Human Entry, Human
Interaction Runtime, Conversation Layer, Platform Core, Governance,
Authorization, Replay, Certification, Constitutional Runtime Observatory, and
`CLIA_THIN_HIC_SKELETON_ESTABLISHED`.

Authenticated repository identity:

- Commit: `d1aee4a833fdaa8e1df8afbf917970815804bb72`
- Tree: `e11baddfd0e939c69f5358f1345e8225d145e389`
- Subject: `G68-01: establish CLIA thin Human Interaction Channel skeleton`

The authenticated worktree was clean before G68-02 implementation.

Implementation contracts: G48 Constitutional Evidence Reporting Standard V1;
Constitutional Architecture Specification V1; Canonical Layer Model;
Constitutional Flow Architecture; G31 Common Entry; G47 Development
Governance; G59/G60/G66 Conversation and Human Interaction contracts; G67
passive Constitutional Runtime Observatory; G68-00 Canonical CLIA Architecture
Specification V1; and G68-01 CLIA thin HIC implementation.

Reporting date: 2026-08-04.

Objective:

Replace the G68-01 fail-closed placeholder callback with the authenticated
governed runtime callable already supplied to Canonical Human Entry by the
current production adapters, while preserving CLIA as a Development Human
Interaction Channel and preserving CHE as its sole invoked runtime function.

Primary implementation result:

~~~text
Human exact act
-> CLIA transport
-> run_human_interface_runtime_entry(...)
   [governed_runtime_runner=authenticated_human_interaction_runtime]
-> canonical Human Interaction Runtime entry service
-> G66 Conversation composition
~~~

The authenticated callable is the existing
`aigol.cli.aigol_cli.run_interactive_conversation`. Current `./aicli` and
default `aigol next` CHE compositions already pass this same callable as
`governed_runtime_runner`. CLIA passes the callable as an opaque dependency to
CHE; CLIA never invokes it.

The exact Development classification remains:

~~~text
CLIA_IMPLEMENTED_AS_DEVELOPMENT_HIC_NOT_PRODUCTION_CUTOVER
~~~

No production cutover, launcher replacement, package entry-point change, or
production-route change occurred.

Modified modules:

- `aigol/cli/clia/transport.py` — replaces the refusing callback with the
  authenticated governed runtime callable passed to CHE.
- `tests/test_g68_01_clia_thin_hic_skeleton.py` — updates two superseded
  G68-01 isolation assertions to recognize the authorized G68-02 binding while
  retaining all transport regression coverage.
- `tests/test_g68_02_clia_che_runtime_binding.py` — focused binding, chain,
  direct-call isolation, determinism, no-mutation, and no-cutover evidence.
- `docs/governance/G68_02_CLIA_CHE_RUNTIME_BINDING_REPORT_V1.md` — this G48
  implementation report.

Intentionally unchanged modules:

- root `clia`, root `aicli`, `aigol/cli/aicli.py`,
  `aigol/cli/aigol_cli.py`, and `aigol/acli_next/`;
- Canonical Human Entry, Human Interaction Runtime, Conversation, CWM,
  Semantic Slot, proposal, Proposal Commit, readiness, Objective Commitment,
  Platform, Governance, Authorization, Worker, provider, execution, result,
  Replay, termination, and Certification owners;
- all G67 CRO core, query, transport, composition, visualization, catalog, and
  topology modules;
- package entry points, release/deployment configuration, schemas, policies,
  baselines, and PCBV31.

Architectural boundaries preserved:

- CLIA contains exactly one runtime call expression:
  `run_human_interface_runtime_entry(...)`.
- The authenticated Human Interaction Runtime callable appears only as the
  value of CHE's existing `governed_runtime_runner` parameter.
- CLIA contains no call to Conversation, Proposal Validation, Proposal Commit,
  Platform, Governance, Authorization, Worker, provider, Replay,
  Certification, or CRO.
- CHE retains all sequencing and runtime-admissibility decisions.
- The focused journey stops at an instrumented Conversation boundary before
  filesystem or repository mutation and before all execution/evidence owners.

# 2. Code Evidence

## Public API

The CLIA submission API remains unchanged:

~~~python
submit_clia_human_act_v1(
    *,
    session: CliaTransportSession,
    human_act: str,
) -> CliaSubmissionResult
~~~

The sole invoked runtime API remains unchanged:

~~~python
run_human_interface_runtime_entry(...)
~~~

No new CLIA API, CHE wrapper, Human Interaction Runtime API, Conversation API,
schema, model, or authority was introduced.

## Runtime Binding

`aigol/cli/clia/transport.py` now binds the existing authenticated runner:

~~~python
from aigol.cli.aigol_cli import (
    run_interactive_conversation as authenticated_human_interaction_runtime,
)

response = run_human_interface_runtime_entry(
    ...,
    governed_runtime_runner=authenticated_human_interaction_runtime,
    ...,
)
~~~

The G68-01 `_development_only_governed_runtime_runner(...)` function was
removed. No local replacement function calls or wraps HIR.

Authenticated caller evidence exists in current production adapter source:

- `aigol/cli/aicli.py` imports `run_interactive_conversation` and passes it to
  `run_human_interface_runtime_entry(...)` at each current CHE composition;
- `aigol/cli/aigol_cli.py` uses the same runner in the default `aigol next`
  CHE composition; and
- G66-15 classifies the default `./aicli` and default `aigol next`
  compositions as production adapters that delegate through canonical entry.

The callable's module also contains separately classified historical command
surfaces. G68-00 establishes that a shared helper's constitutional status is
composition-specific. G68-02 reuses only the runner callable through CHE and
does not expose or route to any `aigol` command.

## CHE Invocation Evidence

The transport has one exact CHE invocation. It supplies exact interface,
session, Human act, time, runtime-root, workspace, Human actor, and transport
presentation values. Focused tests capture that call and prove:

- one CLIA submission produces one CHE invocation;
- the exact Human act is carried in `human_requests`;
- `governed_runtime_runner` is the authenticated runner object; and
- unknown CHE delivery continues to fail closed without retry.

No launcher or parser calls the authenticated runner on CLIA's behalf. The
runtime call remains inside `submit_clia_human_act_v1(...)` and targets CHE
only.

## HIR Entry Evidence

`run_human_interface_runtime_entry(...)` is implemented by
`aigol/runtime/human_interface_runtime_entry_service.py`, whose authenticated
service identity is the Canonical Human Interface Runtime Entry Service. The
public CHE boundary and canonical HIR entry service are therefore adjacent
contract and implementation identities, not two adapter-callable functions.

CHE alone owns invocation of the supplied `governed_runtime_runner` when its
existing owner evidence produces an admissible runtime prompt. CLIA only
passes the callable reference. The focused chain test instruments CHE's use of
that reference and records exactly:

~~~text
CHE -> HIR -> Conversation
~~~

The instrumented HIR returns immediately from the Conversation-entry sentinel.
It cannot reach filesystem mutation, Worker, provider, Replay, or
Certification.

## Conversation Entry Evidence

Authenticated CHE source imports and calls
`compose_production_conversation_flow_binding_v1(...)` for an ordinary Human
request before Project Services and before any optional governed runner call.
G66 identifies this as the canonical Conversation composition boundary.

The focused chain test separately proves the required successor relation by
having the instrumented HIR invoke exactly one Conversation-entry sentinel.
The sentinel returns these closed boundary facts:

~~~text
repository_mutation_reached: false
worker_execution_reached: false
provider_execution_reached: false
replay_generation_reached: false
certification_reached: false
~~~

This test is runtime-binding evidence only. It creates no CWM, Semantic Slot,
proposal, Objective, admission, execution, Replay, or Certification artifact.

## Import Isolation

AST inspection of `transport.py` proves:

- one call to `run_human_interface_runtime_entry`;
- zero calls to `authenticated_human_interaction_runtime`;
- zero imports or calls to a Conversation, Proposal, Platform, Governance,
  Authorization, Worker, provider, Replay, Certification, or CRO owner; and
- one import of `aigol.cli.aigol_cli` solely for the authenticated runner
  symbol already used by current CHE-bound production adapters.

The existing `aicli`, `aigol` parser/default source, ACLI Next entrypoint, root
launchers, and package configuration are byte-identical to the authenticated
G68-01 commit.

## Orchestration Entry Point

The repository-local `clia` executable remains a thin call to
`aigol.cli.clia.main.main`. The call sequence is:

~~~text
./clia
-> main
-> run_clia_interactive_session_v1
-> submit_clia_human_act_v1
-> run_human_interface_runtime_entry
-> established owner sequence
~~~

The executable remains Development-only and its help still states “Sole
runtime successor: Canonical Human Entry. No production cutover.”

## Semantic Reductions

None. G68-02 does not classify, normalize, parse, or reinterpret Human text.
The exact CLIA buffer remains the exact CHE request. Any G66/G59 semantic
reduction remains downstream and unchanged.

## Public Validators

Existing G68-01 session, exact-act, response-envelope, submission identity,
unknown-delivery, and deterministic presentation validators are reused
unchanged. CHE and all downstream validators are unchanged. The new focused
tests validate runner identity and source-level call isolation; they create no
new runtime validator.

## Canonical Data Models

No canonical data model changed. `CliaTransportSession` and
`CliaSubmissionResult` remain transport-local Development models. CHE response
data is copied and rendered without acquiring semantic or authority-bearing
meaning.

## Deterministic Algorithms

For a submitted act, the binding algorithm is fixed:

1. validate exact local session and act;
2. allocate one monotonic submission identity;
3. invoke CHE once with the authenticated runner reference;
4. fail closed if delivery or response validity is unknown;
5. acknowledge only the validated CHE correlation; and
6. render deterministic sorted JSON presentation.

Repeated identical sessions, acts, and CHE responses remain byte-identical in
the focused G68-02 and G68-01 tests.

## Responsibility Boundaries

| Responsibility | Owner | G68-02 result |
|---|---|---|
| Human act | Human Authority | transported exactly; not interpreted by CLIA |
| terminal/session transport | CLIA | Development-only bounded local state |
| canonical admission and sequencing | CHE/HIR entry service | sole CLIA runtime successor |
| Conversation state and semantics | Conversation owners | reached only through CHE-owned composition |
| runtime admissibility | existing CHE/Platform evidence | unchanged; CLIA cannot decide it |
| Governance and Authorization | existing owners | not invoked by focused journey |
| Worker/provider execution | existing owners | not invoked or modified |
| Replay/Certification/CRO | existing passive or terminal owners | not invoked, generated, or modified |

## Reuse Impact Assessment

1. Which existing certified capabilities are reused?

   G68-02 reuses G68-01 exact Human-act collection, session identity,
   fail-closed delivery, CHE response validation, and deterministic
   presentation; the existing `run_human_interface_runtime_entry(...)`
   contract; the same `run_interactive_conversation` governed runner supplied
   by current CHE-bound production adapters; and unchanged G66 Conversation
   composition. Source identities, current callers, and focused regressions
   authenticate each reuse.

2. Which new capabilities, if any, are introduced?

   No new owner capability is introduced. G68-02 adds one bounded composition
   fact: Development CLIA now supplies CHE's authenticated runner instead of a
   local refusing placeholder. Focused tests and this report are new evidence,
   not runtime authorities.

3. Does any existing certified capability become unreachable?

   No. Root `aicli`, current `aigol next`, compatibility modes, G66 owners,
   G67 CRO, and all downstream execution owners remain byte-identical and
   their focused regressions pass. The removed G68-01 callback was an
   intentionally temporary refusal, not a certified production capability.

4. Does the implementation create a parallel production path?

   No. CLIA remains explicitly Development-only and calls the same CHE API
   used by existing production adapters. It does not bypass CHE and no
   launcher, package entry point, route classification, or production default
   changes.

5. Does the implementation decrease or increase the number of production paths?

   Neither. The count of production paths remains one. G68-02 increases
   Development CLIA's authenticated runtime-binding reachability without
   granting production status or adding a production ingress.

# 3. Constitutional Self-Assessment

## Verified

- The authenticated G68-01 commit, tree, subject, and clean initial worktree
  were recorded before mutation.
- The temporary refusing callback is removed from CLIA transport.
- CLIA passes the same governed runtime callable used by current CHE-bound
  production adapters.
- CLIA directly invokes exactly one runtime function:
  `run_human_interface_runtime_entry(...)`.
- CLIA does not directly invoke HIR, Conversation, Proposal Validation,
  Proposal Commit, Platform, Governance, Authorization, Worker, provider,
  Replay, Certification, or CRO.
- Instrumented runtime evidence records the exact `CHE -> HIR -> Conversation`
  successor order and stops at Conversation entry.
- The focused journey performs no repository/filesystem mutation and generates
  no Worker, provider, Replay, Certification, or CRO evidence.
- Existing transport ordering, idempotency, failure, and deterministic
  rendering behavior remains intact.
- The exact Development classification remains unchanged.
- Existing `./aicli`, current production routes, launchers, and package entry
  points remain unchanged.
- Focused G68-02 plus G68-01 tests pass: 31 passed.
- Current G66 CHE/HIC regression passes: 30 passed.
- G67 CRO regression passes: 72 passed.
- Governance regression and conformance pass.
- Python compilation and executable validation pass.

## Not Verified

- No production cutover or production CLIA certification was attempted.
- No live or persisted end-to-end CLIA runtime journey was executed; the
  focused entry journey uses instrumented HIR and Conversation boundaries so
  it can stop before mutation and Replay generation as required.
- No Natural Conversation, GUI, REST, Browser, Speech, or Agent-to-Agent
  adapter was implemented or tested.
- No Worker, provider, repository mutation, Replay generation, Certification,
  or CRO integration was invoked.
- No claim is made that unrestricted Human language produces G59 Objective
  slots or that a natural-language act constitutes confirmation, Commitment,
  Authorization, or acceptance.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| G48 structure | six exact top-level sections; required G68-02 topics nested under Code Evidence | deterministic heading review | `PASS` |
| authenticated baseline | commit/tree/subject and clean initial status | exact Git inspection | `PASS` |
| placeholder replacement | transport imports and passes authenticated runner; refusing callback absent | source and AST review | `PASS` |
| sole CLIA runtime call | one CHE call expression; runner has no call expression | G68-02 focused AST test | `PASS` |
| CHE invocation | exact act and authenticated runner captured once | focused dynamic test | `PASS` |
| HIR entry | CHE uses supplied runner; instrumented successor entered | focused chain test | `PASS` |
| Conversation entry | instrumented HIR invokes one Conversation sentinel; CHE source contains canonical G66 composer call | focused chain plus source review | `PASS` |
| stop before mutation | sentinel flags all mutation/execution/evidence owners false | focused chain test | `PASS` |
| direct downstream isolation | no CLIA call/import to named downstream owner modules | focused AST review | `PASS` |
| determinism | repeated identical input/response renders byte-identically | focused G68-02 test | `PASS` |
| Development classification | exact status token unchanged | focused source/runtime test | `PASS` |
| existing `./aicli` unchanged | authenticated source equals HEAD | focused byte comparison | `PASS` |
| production routes unchanged | `aigol` CLI and ACLI Next entry source equals HEAD | focused byte comparison | `PASS` |
| entry points unchanged | root launchers/config mutation absent | Git/source review | `PASS` |
| focused G68-02 tests | 8 tests | pytest | `PASS` |
| G68-01 regression | 23 transport tests with superseded assertions updated only for G68-02 binding | pytest | `PASS` |
| G67 regression | G67-02 through G67-06 | pytest: 72 passed | `PASS` |
| G66 Human Interaction regression | five current CHE/HIC suites | pytest: 30 passed | `PASS` |
| governance regression | `tests/test_governance_conformance.py` | pytest: 5 passed | `PASS` |
| governance conformance | read-only engine | 20 passed, 0 failed, 0 warnings, 0 critical violations, `CONFORMANT` | `PASS` |
| Python compilation | CLIA namespace and G68-02 tests | `python -m compileall -q` | `PASS` |
| import isolation review | direct imports/calls and forbidden owner fragments | AST and caller review | `PASS` |
| executable validation | `./clia --help` | exit 0, Development-only CHE text | `PASS` |
| document consistency | headings, exact five questions, exact classification, one verdict | deterministic review | `PASS` |
| whitespace integrity | complete tracked and untracked diff | `git diff --check` plus no-index check | `PASS` |

# 5. Repository Mutation Summary

Modified files:

- `aigol/cli/clia/transport.py`
- `tests/test_g68_01_clia_thin_hic_skeleton.py`

Added files:

- `tests/test_g68_02_clia_che_runtime_binding.py`
- `docs/governance/G68_02_CLIA_CHE_RUNTIME_BINDING_REPORT_V1.md`

Unchanged subsystems:

- CLIA session, presentation, main, public exports, and executable;
- all current production and compatibility CLI implementations;
- CHE, HIR, Conversation, Platform, Governance, Authorization, Worker,
  provider, Replay, Certification, and CRO implementations;
- all runtime schemas, policies, baselines, PCBV31, packaging, deployment, and
  release configuration.

API compatibility:

- No public signature or model changed. Existing G68-01 CLIA APIs and CHE's
  `governed_runtime_runner` contract are reused exactly.

Boundary preservation:

- CLIA's only runtime call remains CHE; runner selection is a parameter value,
  not a direct HIR invocation. No production path or owner authority was
  added.

Unrelated pre-existing changes:

- None observed. The worktree was clean at implementation start.

# 6. Certification Verdict

CLIA_CHE_RUNTIME_BINDING_ESTABLISHED
