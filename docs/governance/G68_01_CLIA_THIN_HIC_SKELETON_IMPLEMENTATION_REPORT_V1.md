# 1. Implementation Summary

Generation: G68-01

Report identity:
G68_01_CLIA_THIN_HIC_SKELETON_IMPLEMENTATION_REPORT_V1

Constitutional baseline: G0 through G68-00, including Canonical Human Entry,
Human Interaction Runtime, Conversation Runtime, G59 Semantic Slot/CWM and
proposal owners, G60 Human Interface integration, G66 production flow and
entry classifications, G67 Constitutional Runtime Observatory, and
`CANONICAL_CLIA_ARCHITECTURE_SPECIFICATION_ESTABLISHED`.

Authenticated repository identity:

- Commit: `5ff48e49f91b673e44db1a92d6f2c9cd2cdbde64`
- Tree: `3ee0abda2cd10b333455158159439ee789a28f48`
- Subject: `G68-00: establish canonical CLIA architecture specification`
- Immediate parent: `f1b903239be0f15779795c02d34c76f053a0ffd9`
- Parent subject: `G67-06: establish constitutional runtime observatory visualization`

Implementation contracts: G48 Constitutional Evidence Reporting Standard V1;
Constitutional Architecture Specification V1; Canonical Layer Model;
Constitutional Flow Architecture; G31 Common Entry; G47 Development
Governance; G59/G60/G66 Conversation and Human Interaction contracts; G67
passive CRO; and G68-00 Canonical CLIA Architecture Specification V1.

Reporting date: 2026-08-04.

Objective:

Implement the minimum independently callable CLIA skeleton as a new thin CLI
Human Interaction Channel. CLIA collects exact line-oriented Human input,
maintains only bounded transport-local state, submits one exact Human act to
the existing Canonical Human Entry, and deterministically presents the exact
CHE response data.

Primary implementation result:

~~~text
terminal input/output
-> bounded CLIA transport session
-> exact Human act + transport submission identity
-> run_human_interface_runtime_entry(...)
-> validated exact CHE response data
-> deterministic terminal presentation
~~~

The exact development classification is:

~~~text
CLIA_IMPLEMENTED_AS_DEVELOPMENT_HIC_NOT_PRODUCTION_CUTOVER
~~~

CLIA is repository-callable but is not a certified production path. The
existing `./aicli`, default `aigol next`, compatibility surfaces, and all
production classifications remain unchanged.

Modified modules:

- `aigol/cli/clia/__init__.py` — narrow CLIA exports.
- `aigol/cli/clia/session.py` — bounded transport-only session lifecycle and
  submission identity state.
- `aigol/cli/clia/transport.py` — exact Human-act collection, CHE-only
  delegation, interruption, and idempotency boundaries.
- `aigol/cli/clia/presentation.py` — exact CHE response validation and
  deterministic JSON presentation.
- `aigol/cli/clia/main.py` — transport-only parser and interactive entry.
- `clia` — repository-local executable.
- `tests/test_g68_01_clia_thin_hic_skeleton.py` — focused boundary,
  fail-closed, determinism, isolation, and no-cutover tests.
- `docs/governance/G68_01_CLIA_THIN_HIC_SKELETON_IMPLEMENTATION_REPORT_V1.md`
  — this G48 implementation report.

Intentionally unchanged modules:

- root `aicli`, `aigol/cli/aicli.py`, `aigol/cli/aigol_cli.py`, and all
  `aigol/acli_next/` implementations;
- Canonical Human Entry and all HIR, Conversation, Semantic Slot, CWM,
  Proposal, Commitment, Platform, Governance, Authorization, Worker,
  provider, execution, result, Replay, termination, and Certification owners;
- all G67 CRO modules, adapters, queries, composition, visualization, and
  `cro` launcher;
- package entry points, deployment, release manifests, compatibility routes,
  schemas, baselines, PCBV31, and existing tests.

Architectural boundaries preserved:

- CLIA directly imports one production-runtime operation only:
  `run_human_interface_runtime_entry(...)`.
- CLIA imports no historical CLI, ACLI Next, bridge, Conversation, Platform,
  Governance, Authorization, Worker, provider, Replay, Certification, or CRO
  module.
- The default governed-runner callback fails closed because production binding
  and cutover are not authorized in G68-01.
- No CLIA value creates semantic, workflow, admission, execution, Replay, CRO,
  or Certification authority.
- One explicit submission starts at most one CHE invocation and is never
  silently retried.

# 2. Code Evidence

## Public API

The new narrow surface is:

~~~python
create_clia_transport_session_v1(
    *,
    transport_session_identity: str,
    human_actor_reference: str,
    workspace_reference: str,
    runtime_root_reference: str,
    created_at: str,
) -> CliaTransportSession

submit_clia_human_act_v1(
    *,
    session: CliaTransportSession,
    human_act: str,
) -> CliaSubmissionResult

run_clia_interactive_session_v1(
    *,
    session: CliaTransportSession,
    input_reader: Callable[[str], str] = input,
    output_writer: Callable[[str], None] = print,
) -> CliaTransportSession

main(
    argv: Sequence[str] | None = None,
    *,
    input_reader: Callable[[str], str] = input,
    output_writer: Callable[[str], None] = print,
) -> int
~~~

The surface exposes session transport, submission, presentation, and terminal
entry only. It exports no downstream owner API or production authority.

## Orchestration Entry Point

The repository-local executable contains only:

~~~python
from aigol.cli.clia.main import main


if __name__ == "__main__":
    raise SystemExit(main())
~~~

`./clia --help` succeeds and labels the executable development-only, names CHE
as its sole runtime successor, and declares that no production cutover has
occurred. The file is executable with repository mode `775`, consistent with
the current repository-local `aicli` launcher mode.

## CLIA Transport Architecture

The implementation is isolated under `aigol/cli/clia/`:

~~~text
main.py
-> session.py for local lifecycle
-> transport.py for exact submission and CHE delegation
-> presentation.py for response validation/rendering
-> STOP
~~~

There is no compatibility subparser, historical adapter, provider binding,
direct Conversation terminal, CRO command, attachment flow, or workflow
command. The local grammar is exactly `/send`, `/cancel`, `/exit`, and `/help`.
Any other input, including an unrecognized slash-prefixed string, remains
ordinary buffered data and receives no local semantic meaning.

## Transport Session Model

The exact permitted states are implemented by `CliaTransportStatus`:

~~~python
class CliaTransportStatus(str, Enum):
    CREATED = "CREATED"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    TRANSPORT_FAILED_CLOSED = "TRANSPORT_FAILED_CLOSED"
    INTERRUPTED = "INTERRUPTED"
~~~

`CliaTransportSession` retains only transport identity, Human actor reference,
workspace/runtime-root references required by CHE, creation time, fixed adapter
and channel identity, status, bounded pending lines, a monotonic submission
sequence, active/last submission identity, the last acknowledged CHE session
correlation, and failure text.

The pending buffer is bounded to 128 lines and 65,536 characters. It carries
no readiness, Proposal, Commitment, admission, Governance, Authorization,
execution, Replay, CRO, or Certification state.

## Exact Human Act Boundary

Ordinary lines are appended without stripping or normalization. Submission
uses the selected newline contract:

~~~python
human_act = "\n".join(session.pending_input_lines)
if not human_act.strip():
    raise FailClosedRuntimeError("CLIA cannot submit an empty Human act")
return human_act
~~~

The focused trace proves that the terminal sequence:

~~~text
action: create
/send
~~~

reaches CHE as exactly `human_requests=["action: create"]`. The `clia> ` and
`... ` prompts and `/send` control are absent. A three-line case preserves
ordering, embedded leading spaces, trailing spaces, punctuation, and exact
`\n` separators.

CLIA never translates, summarizes, classifies, aliases, merges, or prepends
terminal content. Empty or whitespace-only submissions fail before CHE.

## CHE Invocation Boundary

The only production-runtime call in the namespace is the authenticated CHE
operation:

~~~python
response = run_human_interface_runtime_entry(
    interface_name=CLIA_INTERFACE_NAME,
    session_id=session.transport_session_identity,
    human_requests=[exact_act],
    created_at=session.created_at,
    runtime_root=session.runtime_root_reference,
    workspace=session.workspace_reference,
    governed_runtime_runner=_development_only_governed_runtime_runner,
    presentation=transport_presentation,
    g31_human_actor_id=session.human_actor_reference,
)
~~~

The presentation metadata binds the G68-01 version, adapter, channel, session,
submission, and development status. CHE returns that metadata with its own
service, interface, session, and status fields. CLIA validates exact identity
equality before acknowledging delivery.

The local `_development_only_governed_runtime_runner` raises
`FailClosedRuntimeError`. This callback satisfies the existing required CHE
signature without importing or invoking the historical `aigol` runner or a
downstream owner. If CHE determines that a downstream runtime call would be
required, the G68-01 Development surface fails closed; it does not claim an
uncertified production binding.

## Deterministic Presentation

The response owner remains CHE. CLIA requires one mapping with exact CHE and
CLIA correlation strings, verifies deterministic JSON serializability, and
renders:

~~~python
return f"{CLIA_RESPONSE_HEADING}\n{body}"
~~~

`body` is `json.dumps(...)` with lexical keys, compact separators, and ASCII
escaping. A focused response containing exact refusal text, Boolean pending
state, nested lists, and `null` is recovered byte-for-data from the rendered
JSON. Two identical sessions, acts, submission identities, and CHE responses
produce byte-identical presentation.

CLIA adds only the fixed heading. It does not select fields, hide refusals,
rewrite messages, convert pending to success, infer next state, diagnose the
runtime, or add a recommendation.

## Failure and Idempotency Boundaries

Before CHE, malformed session state, invalid transitions, buffer limits, empty
acts, buffer/act mismatch, and duplicate active delivery raise
`FailClosedRuntimeError` without runtime invocation.

`begin_clia_submission_v1(...)` creates exactly one identity:

~~~text
<transport-session>:CLIA-SUBMISSION:<six-digit sequence>
~~~

It marks the submission active before CHE. A returned response must contain
the same identity. Only then does acknowledgement increment the sequence,
clear the exact buffer, and remove the active marker.

Any exception after CHE invocation begins produces
`CliaDeliveryUncertainError`, records `TRANSPORT_FAILED_CLOSED`, retains the
active submission identity, and performs no retry. A malformed CHE response
also closes the transport without acknowledgement. Focused tests invoke the
uncertain CHE sentinel once, attempt another submission, and prove the call
count remains one.

The executable returns `2` for `TRANSPORT_FAILED_CLOSED`, `130` for
`INTERRUPTED`, and `0` only for a clean close or EOF. It therefore does not
translate transport failure into terminal success.

`/cancel` clears only an unsent buffer. `/exit` closes without runtime
invocation. `KeyboardInterrupt` sets `INTERRUPTED`; EOF sets `CLOSED`; neither
submits pending content or manufactures a runtime result.

## Import and Owner Isolation

AST inspection finds exactly two `aigol.runtime` imports across the namespace:

~~~text
aigol.runtime.human_interface_runtime_entry_service
aigol.runtime.models
~~~

The first supplies exact CHE; the second supplies the neutral fail-closed
exception. Source inspection finds exactly one CHE call. No CLIA source imports
or calls `aicli`, `aigol_cli`, `acli_next`, `sapianta_bridge`, direct
Conversation, Platform, Governance, Authorization, Worker, provider, Replay,
Certification, or CRO modules.

The unchanged `aicli`, `aigol/cli/aicli.py`, and `aigol/cli/aigol_cli.py`
contain no CLIA import or redirect. No current package entry point or default
route references `clia`.

## Development-Only Status

The implementation constant and help output state:

~~~text
CLIA_IMPLEMENTED_AS_DEVELOPMENT_HIC_NOT_PRODUCTION_CUTOVER
~~~

G68-01 adds one repository-callable Development HIC executable. It does not
change the number of certified production paths. It does not implement Natural
Conversation, exact Candidate controls beyond generic act transport,
Commitment, Authorization, execution, attachments, Replay, Certification,
CRO, GUI, Web, REST, Browser, Speech, Agent-to-Agent, deployment, or packaging.

## Semantic Reductions

There are none. Exact line joining is a declared transport encoding, not a
semantic reduction. Control recognition is closed to four local transport
commands and does not interpret the submitted act. All source meaning and
authority remain outside CLIA.

## Public Validators

Public validation is limited to:

- `validate_clia_transport_session_v1(...)` for transport identities, state,
  sequence, buffer, and bounds;
- `validate_clia_che_response_v1(...)` for exact returned CHE/CLIA identities
  and deterministic serializability; and
- existing CHE validation after the exact call.

CLIA introduces no validator for semantic meaning, owner readiness, proposal
admissibility, authority, execution, or evidence.

## Canonical Data Models

`CliaTransportSession` and `CliaSubmissionResult` are transport-local Python
models, not canonical runtime artifacts. They are not persisted, hashed as
Replay, admitted as owner predecessors, or indexed by CRO. The CHE response is
deep-copied for the returned in-memory result and deterministic presentation;
CLIA never mutates the owner mapping.

## Deterministic Algorithms

The implemented turn sequence is:

1. validate/open one CREATED or OPEN transport session;
2. collect exact ordinary lines;
3. reject empty submission;
4. create one monotonic submission identity and mark delivery active;
5. call CHE exactly once with one exact Human request;
6. fail closed on unknown delivery or malformed response;
7. validate exact returned identities;
8. acknowledge once and clear the local buffer; and
9. render the complete response deterministically.

No branch retries, invokes another runtime owner, or reconstructs missing data.

## Responsibility Boundaries

| Responsibility | Owner | G68-01 result |
|---|---|---|
| exact Human source act | Human Authority | collected without semantic interpretation |
| terminal and transport session | CLIA | bounded local ownership |
| canonical entry and downstream composition | CHE | sole permitted CLIA runtime successor |
| semantic state/proposals/Commitment | established Conversation/G59 owners | no CLIA dependency |
| Platform/Governance/Authorization | established owners | no CLIA dependency |
| Worker/provider/execution | established owners | no CLIA dependency or invocation |
| Replay/Certification | established owners | no CLIA artifact or invocation |
| CRO Journey/query/presentation | G67 owners | unchanged and not integrated |
| production classification/cutover | later constitutional generation | not authorized |

## Reuse Impact Assessment

1. Which existing certified capabilities are reused?

   CLIA reuses the exact
   `aigol.runtime.human_interface_runtime_entry_service.run_human_interface_runtime_entry(...)`
   contract and the neutral `FailClosedRuntimeError`. Through CHE only, future
   authorized composition can reuse HIR, G59/G60/G66, Platform, Governance,
   Authorization, Worker/execution, Replay, and Certification. G68-01 directly
   imports or invokes none of those downstream owners. G67 remains unchanged
   and passive.

2. Which new capabilities, if any, are introduced?

   G68-01 introduces one isolated Development-class CLI HIC skeleton: bounded
   session state, exact multiline buffering, four local transport controls,
   monotonic submission identity, one-call CHE transport, unknown-delivery
   refusal, exact response validation, deterministic presentation, and the
   repository-local `clia` executable. No new semantic, workflow, authority,
   evidence, CRO, or production capability is introduced.

3. Does any existing certified capability become unreachable?

   No. The implementation adds new files only. Source and focused tests prove
   that `./aicli`, default `aigol next`, G66 CHE/HIC behavior, G67 CRO, and all
   existing public routes remain unchanged. No API is removed, redirected, or
   shadowed.

4. Does the implementation create a parallel production path?

   No. `clia` is explicitly Development-only and its default downstream runner
   refuses production activation. It is not referenced by any existing
   production launcher, parser, package entry point, deployment artifact, or
   release manifest. Its sole permitted runtime call is CHE.

5. Does the implementation decrease or increase the number of production paths?

   The repository-callable Development surface count increases by one through
   the new `./clia` executable. The certified production path count neither
   decreases nor increases: current `./aicli` and default `aigol next` remain
   unchanged, and no atomic cutover occurs.

# 3. Constitutional Self-Assessment

## Verified

- CLIA is independently callable and its help is transport-only.
- The new namespace does not copy, subclass, import, wrap, forward to, or
  depend on any prohibited historical or compatibility CLI.
- One exact `action: create` submission reaches a CHE sentinel exactly once.
- Prompts and `/send` are absent from the Human act.
- Multiline ordering, leading/trailing spaces, and newline encoding are exact.
- Empty send, cancel, exit, KeyboardInterrupt, and EOF invoke no runtime.
- One send produces one CHE invocation; a second empty send does not.
- Unknown delivery records failed-closed state and cannot retry.
- Complete CHE response data is rendered without semantic reinterpretation.
- Malformed response and malformed local state fail closed.
- Identical input/response pairs produce byte-identical presentation.
- Import review proves CHE plus the neutral exception are the only runtime
  imports and CHE is the only runtime call.
- Existing CLI defaults have no CLIA import or redirect.
- Current G66 CHE/HIC regressions pass: 30 passed.
- G67 CRO regressions pass unchanged: 72 passed.
- Governance regression passes: 5 passed.
- Governance conformance passes: 20 passed, 0 failed, 0 warnings, 0 critical
  violations, `CONFORMANT`.
- Python compilation, executable mode, document consistency, and whitespace
  validation pass.

## Not Verified

- CLIA is not production certified and no atomic cutover was performed.
- The repository-local executable was not used to submit to live CHE, a live
  provider, Worker, mutable repository runtime, deployed process, or external
  system. CHE delegation was verified with an exact injected sentinel.
- The default governed runtime callback intentionally refuses downstream
  activation. Full HIR/Conversation/Platform execution through CLIA requires a
  separately authorized binding and end-to-end certification.
- No Natural Conversation, Candidate-specific control grammar, Objective
  Commitment, execution Authorization, attachment, Replay, Certification, or
  CRO integration was implemented.
- The superseded G14-30 CHE regression module has six passing and six failing
  tests because six cases expect pre-G66 immediate runtime binding. Current
  G66 tests authenticate the later typed-composition/`NOT_REQUIRED` behavior
  and all 30 pass. G68-01 neither modifies nor claims to repair the legacy test
  contract.
- No GUI, Web, REST, Browser, Speech, API, or Agent-to-Agent adapter was
  implemented or exercised.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| G48 report structure | six exact top-level sections and mandatory Code Evidence subsections | deterministic heading review | `PASS` |
| authenticated baseline | Git commit/tree/subject/parent and clean initial worktree | exact Git inspection | `PASS` |
| executable identity | root `clia`, mode `775`, transport-only parser | `./clia --help`; mode inspection | `PASS` |
| CHE-only delegation | one exact call in `transport.py` and focused spy | G68-01 focused tests | `PASS` |
| no downstream shortcut | AST import set equals CHE plus neutral exception | focused import isolation and caller review | `PASS` |
| exact act preservation | `action: create` received exactly, without prompt/control | focused transport test | `PASS` |
| multiline preservation | exact `\n` join with spaces/order retained | focused multiline test | `PASS` |
| empty rejection | empty buffer never reaches CHE | focused empty-send test | `PASS` |
| cancel behavior | unsent buffer only; no CHE call | focused cancel test | `PASS` |
| exit behavior | CLOSED; no CHE call | focused exit/EOF tests | `PASS` |
| interruption | INTERRUPTED; no fabricated result | focused KeyboardInterrupt test | `PASS` |
| one submission/one invocation | one `/send`, one CHE call, monotonic identity | focused idempotency test | `PASS` |
| unknown delivery | one sentinel call, failed closed, no retry | focused uncertain-delivery test | `PASS` |
| response fidelity | complete CHE mapping round-trips from rendered JSON | focused response test | `PASS` |
| malformed response | non-mapping/missing identities rejected | four focused malformed cases | `PASS` |
| determinism | byte-identical presentation | focused repeated-input test | `PASS` |
| malformed local state | rejected before CHE and state failed closed | focused local-state test | `PASS` |
| no production cutover | existing launcher/parser sources contain no CLIA redirect | focused source test and Git diff | `PASS` |
| production path count | one new Development executable; zero new certified paths | source/caller review | `PASS` |
| focused G68-01 suite | 23 focused tests | pytest | `PASS` |
| current CHE/HIC regression | five G66 suites directly call CHE | pytest: 30 passed | `PASS` |
| G67 CRO isolation regression | G67-02 through G67-06 | pytest: 72 passed | `PASS` |
| superseded G14 immediate-binding expectations | legacy module predates G66 typed-composition behavior | pytest: 6 passed, 6 failed; outside current G68 acceptance semantics | `NOT_APPLICABLE` |
| governance regression | `tests/test_governance_conformance.py` | pytest: 5 passed | `PASS` |
| governance conformance | read-only conformance engine | 20 passed, 0 failed, 0 warnings, 0 critical violations, `CONFORMANT` | `PASS` |
| Python compilation | CLIA namespace and focused test | `python -m compileall -q` | `PASS` |
| document consistency | headings, required topics, exact questions, one verdict | deterministic review | `PASS` |
| whitespace integrity | tracked and added files | `git diff --check`; no-index checks | `PASS` |

# 5. Repository Mutation Summary

Added files:

- `aigol/cli/clia/__init__.py`
- `aigol/cli/clia/session.py`
- `aigol/cli/clia/transport.py`
- `aigol/cli/clia/presentation.py`
- `aigol/cli/clia/main.py`
- `clia`
- `tests/test_g68_01_clia_thin_hic_skeleton.py`
- `docs/governance/G68_01_CLIA_THIN_HIC_SKELETON_IMPLEMENTATION_REPORT_V1.md`

Existing files modified:

- None.

Unchanged subsystems:

- current production and compatibility CLI implementations;
- CHE, HIR, Conversation, CWM, Semantic Slots, proposals, Commitments,
  Platform, Governance, Authorization, Worker, provider, execution, results,
  Replay, termination, Certification, and CRO;
- packaging, deployment, releases, schemas, policies, baselines, and PCBV31.

API compatibility:

- The implementation is additive. No current public API, executable default,
  parser route, import, schema, or return behavior changes.

Boundary preservation:

- CLIA is a Development HIC, has one permitted runtime successor, imports no
  downstream owner, creates no evidence or authority, and does not increase
  certified production paths.

Unrelated pre-existing changes:

- None observed. The worktree was clean before G68-01 files were added.

# 6. Certification Verdict

CLIA_THIN_HIC_SKELETON_ESTABLISHED
