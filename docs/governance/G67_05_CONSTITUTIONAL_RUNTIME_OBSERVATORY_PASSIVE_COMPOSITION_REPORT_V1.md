# 1. Implementation Summary

Generation: G67-05

Report identity:
G67_05_CONSTITUTIONAL_RUNTIME_OBSERVATORY_PASSIVE_COMPOSITION_REPORT_V1

Constitutional baseline: `CONSTITUTIONAL_GOVERNANCE_CLOSED`,
`CONSTITUTIONAL_RUNTIME_OBSERVATORY_ARCHITECTURE_ESTABLISHED`,
`CONSTITUTIONAL_RUNTIME_OBSERVATORY_CORE_ESTABLISHED`,
`CONSTITUTIONAL_RUNTIME_OBSERVATORY_QUERY_INTERFACE_ESTABLISHED`, and
`CONSTITUTIONAL_RUNTIME_OBSERVATORY_CLI_TRANSPORT_ADAPTER_ESTABLISHED`.

Authenticated repository identity:

- Commit: `aafb19eaee77f9f87f3dff562cf4525d4c465fdd`
- Tree: `e4a30d1d8466fdec6f9d5b6f9c13b57a798e963b`
- Subject: `G67-04: establish constitutional runtime observatory CLI transport adapter`

Implementation contracts: G48 Constitutional Evidence Reporting Standard V1;
Constitutional Architecture Specification V1; Canonical Layer Model;
Constitutional Flow Architecture; G67-00 CRO discovery; G67-01 CRO
architecture; G67-02 passive CRO core; G67-03 canonical Query Interface; and
G67-04 CLI Transport Adapter.

Reporting date: 2026-08-04.

Objective:

Compose the three already-certified Constitutional Runtime Observatory layers
into one executable passive observation pipeline. The composition accepts only
explicit bounded evidence input, delegates Journey construction to G67-02,
delegates immutable query construction to G67-03, delegates command parsing and
rendering to G67-04, and returns the terminal status. It introduces no Journey,
correlation, evidence parsing, query, rendering, production, or authority
logic.

Implemented composition:

~~~text
explicit absolute evidence scope
+ explicit ADAPTER_ID=ABSOLUTE_PATH roots
+ exact session/Commitment/Human selectors
+ one command token
-> G67-02 build_constitutional_human_intent_journey_v1
-> G67-03 build_journey
-> G67-04 run_cro_cli_transport
-> deterministic terminal output
-> exit
~~~

The repository-local invocation is:

~~~text
./cro \
  --evidence-scope-root /absolute/authenticated/scope \
  --evidence-root G66_FLOW_BINDING=/absolute/authenticated/scope/flow \
  --evidence-root G60_EXECUTION_PREPARATION=/absolute/authenticated/scope/prepared.json \
  ...one explicit root per selected G67-02 adapter... \
  --selector session_id=SESSION-IDENTITY \
  --selector commitment_identity=COMMITMENT-IDENTITY \
  --selector human_actor=HUMAN_OPERATOR \
  summary
~~~

No default scope, current directory, environment root, glob, directory scan,
session lookup, latest-artifact rule, or automatic selector exists. Relative
paths, wildcard syntax, missing roots, duplicate adapter identities, missing or
extra selectors, duplicate selector names, and empty values fail closed.

The focused real-path trace builds the authenticated G67-02 test evidence under
a pytest temporary root before beginning observation. Two G67-05 invocations
over the same explicit inputs then produce the same G67-02 projection hash, the
same G67-03 source-projection identity, and byte-identical G67-04 output. The
evidence-root byte snapshot is identical before and after both invocations.

Modified modules:

- `aigol/runtime/constitutional_runtime_observatory/composition.py` — adds the
  explicit passive input boundary and exact G67-02/G67-03/G67-04 orchestration.
- `cro` — adds the repository-local passive observation launcher.
- `tests/test_g67_05_constitutional_runtime_observatory_passive_composition.py`
  — focused composition, determinism, passivity, input, and launcher tests.
- `docs/governance/G67_05_CONSTITUTIONAL_RUNTIME_OBSERVATORY_PASSIVE_COMPOSITION_REPORT_V1.md`
  — this G48 implementation report.

Intentionally unchanged modules:

- G67-02 `core.py`, `catalog.py`, and `topology.py`.
- G67-03 `query.py` and package exports.
- G67-04 `cli_transport.py` and command/rendering contracts.
- All `aicli`, `aigol`, `sapianta`, Canonical Human Entry, HIC, Conversation,
  Semantic Slot, CWM, Objective, Platform Core, Governance, Authorization,
  Worker, provider, execution, result, Replay Review, termination,
  Certification, mutation, persistence, schema, policy, baseline, PCBV31,
  deployment, GUI, Browser, REST, Speech, and Agent-to-Agent behavior.

Architectural boundaries preserved:

- The new `cro` launcher is a passive observation entry, not a production
  Human or execution entry.
- Composition contains only explicit input validation and certified-layer
  orchestration.
- G67-02 remains the sole Journey/evidence/correlation owner.
- G67-03 remains the sole query-construction and data-access owner.
- G67-04 remains the sole command and text-rendering owner.
- No CRO value is persisted or made admissible as a runtime predecessor.
- No existing workflow, route, owner, authority, or public API is changed.

# 2. Code Evidence

## Composition Architecture

The composition module imports exactly one public operation from each
certified CRO layer:

~~~python
from .core import build_constitutional_human_intent_journey_v1
from .query import build_journey
from .cli_transport import run_cro_cli_transport
~~~

It imports no source-owner reconstructor, adapter catalog, topology loader,
Replay transport, CHE, Conversation, Platform Core, Governance, Authorization,
Worker, provider, Certification, or persistence API. The composition does not
inspect the returned projection, query object, or rendered output.

Its version identity is:

~~~text
G67_05_CONSTITUTIONAL_RUNTIME_OBSERVATORY_PASSIVE_COMPOSITION_V1
~~~

## Public API

The bounded library entry is:

~~~python
compose_passive_cro_observation(
    *,
    evidence_scope_root: str | Path,
    evidence_roots: Sequence[Mapping[str, Any]],
    selector: Mapping[str, Any],
    command: str,
    output: TextIO | None = None,
) -> int
~~~

The terminal entries are:

~~~python
build_cro_composition_parser() -> argparse.ArgumentParser
main(argv: Sequence[str] | None = None, *, output: TextIO | None = None) -> int
~~~

These are additive G67-05 APIs. No G67-02, G67-03, or G67-04 signature, export,
default, return type, or behavior changes.

## Composition Flow

After bounded syntax validation, the implementation executes only:

~~~python
journey_projection = build_constitutional_human_intent_journey_v1(
    evidence_scope_root=scope,
    evidence_roots=roots,
    selector=exact_selector,
)
journey = build_journey(journey_projection=journey_projection)
return run_cro_cli_transport(
    journey=journey,
    argv=[exact_command],
    output=output,
)
~~~

Focused spies authenticate the exact call order `G67-02`, `G67-03`, `G67-04`
and exact predecessor/result handoff. No branch can call G67-03 with evidence
input, call G67-04 with a raw projection, or render without G67-04.

The executable `cro` file contains only a shebang, import of G67-05 `main`, and
`SystemExit(main())`. It is executable mode `755` and has no alternate route.

## Evidence Boundary

The terminal grammar requires:

- one `--evidence-scope-root` absolute path;
- one or more `--evidence-root ADAPTER_ID=ABSOLUTE_PATH` descriptors;
- exactly one `session_id` selector;
- exactly one `commitment_identity` selector;
- exactly one `human_actor` selector; and
- one G67-04 command token.

The three selector keys are the exact G67-02 authenticated anchor predicates
used by its certified fixture and source contract. G67-05 does not derive them
from filenames, current sessions, stored state, timestamps, or evidence
content.

G67-05 validates only explicitness and syntax. G67-02 still owns scope
containment, existence, root kind, adapter identity/version, overlap,
source-artifact validation, owner reconstruction, correlation, selector match,
gap classification, and immutable Journey projection.

No `glob`, `rglob`, `os.walk`, directory enumeration, environment-variable
lookup, implicit current directory, or default evidence source exists in the
composition module.

## Passivity Proof

The composition has no write call, output path, cache, store, database,
telemetry, runtime root, refresh, mutation, action, approval, Authorization,
Worker, provider, Replay creation, or Certification API.

The real focused trace records SHA-256 for every file under the explicit
evidence scope before two observations and confirms the same file set and
hashes afterward. G67-02 returns `persisted: false`; G67-03 retains an immutable
private snapshot and reports no query reconstruction or runtime invocation;
G67-04 writes only its deterministic query presentation to the selected stream.

G67-02 internally invokes its previously certified pure owner-local
reconstructors over existing Replay evidence because that is the mandatory
G67-02 Journey-building contract. G67-05 neither imports nor invokes a Replay
runtime directly, creates no Replay artifact, and gives reconstruction no new
authority. This is passive reuse of G67-02, not a new Replay path.

The focused production-like evidence is created only during fixture setup in a
pytest temporary root through the existing G67-02 test helper. The passivity
snapshot begins after setup and covers the complete G67-05 pipeline. No
repository evidence store or external runtime is used.

## Orchestration Entry Point

`./cro` invokes `composition.main(...)`. The parser constructs only explicit
descriptor and selector values. `main(...)` then delegates to
`compose_passive_cro_observation(...)`; all output rendering and command status
come from G67-04.

Malformed `NAME=VALUE` syntax terminates under argparse. Bounded-input
violations and downstream passive validation errors terminate status `2` with
`FAIL_CLOSED`. Successful observation returns the G67-04 status unchanged.

No existing `aicli`, `aigol`, `sapianta`, operator CLI, CHE, or HIC command is
modified or called.

## Semantic Reductions

G67-05 performs no semantic reduction over evidence, Journey, Query, or output
content. Its only input reductions are syntactic:

~~~text
ADAPTER_ID=ABSOLUTE_PATH -> {adapter_id, path}
NAME=VALUE -> exact selector mapping
explicit command token -> one-element argv passed to G67-04
~~~

It does not inspect a file, select an artifact, classify an owner, order an
event, correlate an identity, calculate a state, select a query method, or
format output. Each responsibility remains with G67-02, G67-03, or G67-04.

## Public Validators

G67-05 validates only composition inputs:

- required non-empty text;
- absolute evidence scope and root paths;
- absence of wildcard markers `*`, `?`, `[` and `]`;
- exact descriptor keys `adapter_id` and `path`;
- unique adapter identities;
- exact selector-key closure;
- unique terminal selector assignments; and
- one non-empty command passed onward to G67-04 validation.

It deliberately does not validate adapter catalog membership, evidence type,
artifact version, path containment, owner state, Journey hash, query contract,
or command membership. Those remain certified downstream responsibilities.

## Canonical Data Models

No constitutional model is introduced. G67-05 creates temporary ordinary
descriptor and selector containers solely to call G67-02. It does not create a
composition artifact, Journey variant, Query wrapper, CLI response envelope,
Replay record, authority token, audit record, or persistent state.

The projection remains the G67-02 `FrozenDict`; the query remains the G67-03
`Journey`; the terminal presentation remains the G67-04 deterministic text.

## Deterministic Algorithms

One invocation executes:

1. Parse one explicit evidence scope, explicit roots, exact selectors, and one
   command.
2. Reject relative paths, wildcard syntax, missing values, duplicate adapters,
   or non-exact selector closure.
3. Preserve root order and selector values exactly.
4. Call the G67-02 builder once.
5. Pass its exact immutable projection to G67-03 once.
6. Pass the resulting exact `Journey` and command to G67-04 once.
7. Return the G67-04 exit status without interpreting its output.

No clock, randomness, environment discovery, filesystem enumeration, default
session, latest-record selection, network, locale, cache, or background work
participates. The real repeated trace proves identical intermediate response
identities and final bytes for identical explicit inputs.

## Responsibility Boundaries

| Responsibility | Preserved owner | G67-05 behavior |
|---|---|---|
| explicit terminal evidence input | Human/operator caller | requires exact scope, roots and selectors |
| input syntax/explicitness | G67-05 composition | rejects implicit, wildcard and ambiguous forms |
| evidence loading and owner reconstruction | G67-02 core/catalog | invoked once through the public builder only |
| correlation/Journey/gaps | G67-02 core | exact immutable projection reused |
| query snapshot/data access | G67-03 Query Interface | exact projection passed once |
| command validation/query selection/rendering | G67-04 CLI transport | exact Journey and command passed once |
| terminal output | G67-04 plus stdout/caller stream | no G67-05 inspection or persistence |
| production/runtime authority | existing constitutional owners | absent and never invoked by composition |

## Compatibility

G67-02, G67-03, and G67-04 files and exports are unchanged. Their complete
focused suites pass with `14 passed`, `13 passed`, and `21 passed`
respectively. The `cro` executable is additive and separate from all existing
production and compatibility CLIs.

No existing public API becomes unreachable. Direct G67-02 building, G67-03
query construction, and G67-04 injected-Journey transport remain usable under
their certified boundaries.

## Validation

The focused G67-05 suite covers explicit parser syntax, exact three-layer call
order, relative/wildcard/missing/duplicate input rejection before G67-02,
repeated real composition, intermediate identity determinism, byte-for-byte
evidence preservation, in-process `main`, the executable `./cro` launcher, and
closed source imports.

The focused suite passes with `14 passed`. Governance regression, conformance,
Python compilation, executable mode, document structure, caller isolation, and
tracked/new-file whitespace are separately validated.

## Reuse Impact Assessment

1. Which existing certified capabilities are reused?

   G67-05 reuses G67-02 explicit bounded roots, closed evidence adapters, pure
   owner reconstruction, exact correlation, gap classification, deterministic
   Journey projection, and passivity flags; G67-03 immutable query construction
   and stable data-access contracts; and G67-04 closed commands, query dispatch,
   deterministic ASCII JSON, stdout, and exit semantics. The unchanged complete
   suites pass with 14, 13, and 21 tests respectively, and the focused real
   trace exercises all three in order.

2. Which new capabilities, if any, are introduced?

   One passive composition capability and repository-local launcher are
   introduced. They validate explicit terminal input and orchestrate the three
   certified CRO calls without implementing their logic. No new evidence
   adapter, reconstructor, correlation, Journey, query, renderer, persistence,
   runtime, workflow, owner, or authority capability is introduced.

3. Does any existing certified capability become unreachable?

   No. No existing file, signature, export, command, or route is removed or
   redirected. G67-02, G67-03, and G67-04 remain independently callable and
   their complete focused regressions pass unchanged. Existing production and
   compatibility CLIs are untouched.

4. Does the implementation create a parallel production path?

   No. `cro` is a passive observation launcher over already-persisted evidence.
   It does not accept a Human production act or invoke CHE, Conversation,
   Platform, Governance, Authorization, Worker, provider, execution, mutation,
   or Certification. Its Journey, Query, and text cannot be runtime
   predecessors or authority artifacts.

5. Does the implementation decrease or increase the number of production paths?

   Neither. Production path count is unchanged. G67-05 composes one passive
   observation route outside production, using the already-certified CRO
   stack. It adds no production entry, branch, workflow transition, owner
   handoff, or execution spine.

# 3. Constitutional Self-Assessment

## Verified

- `./cro` executes one bounded passive observation composition.
- The composition order is exactly G67-02, G67-03, then G67-04.
- The adapter accepts only explicit absolute evidence scope/root paths.
- Wildcards, relative paths, missing roots, duplicate adapter identities, and
  non-exact selectors fail before G67-02.
- No implicit discovery, filesystem scan, session guess, latest selection, or
  automatic evidence selection exists.
- G67-02 retains all evidence, reconstruction, correlation, Journey, topology,
  and gap ownership.
- G67-03 retains all Query Interface and immutable access ownership.
- G67-04 retains all command validation, query selection, and rendering
  ownership.
- The same explicit evidence input produces the same G67-02 projection hash,
  G67-03 source-projection identity, and G67-04 output.
- Two complete observations leave every evidence file byte-identical.
- No Journey, Query, CRO state, output, Replay, or evidence is persisted by the
  composition.
- No production CLI, entry, workflow, owner, or public API changes.
- No GUI, Browser, REST, Speech, Natural Conversation, or Agent-to-Agent
  adapter is introduced.

## Not Verified

- G67-05 supports only the exact G67-02 non-mutating Human Intent Journey and
  its current closed adapter/topology versions.
- No implicit selector convenience, evidence manifest, discovery, filtering,
  pagination, export, cache, database, streaming, telemetry, or live
  observation is implemented.
- No malformed or incomplete evidence set is made queryable when G67-02/G67-03
  fail closed; G67-05 does not repair or reinterpret downstream rejection.
- The focused fixture setup uses existing certified runtimes only to create
  disposable source evidence before the passivity snapshot; it is not part of
  the G67-05 composition under test.
- No external provider, Worker, deployed runtime, server, container, GUI,
  Browser, REST endpoint, Speech system, or Agent-to-Agent transport was
  invoked by the composition.
- A repository-wide pytest run was not performed; validation covers G67-05
  through G67-02 and governance conformance.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| G48 structure | six exact top-level sections and mandatory Code Evidence subsections | deterministic heading review | `PASS` |
| authenticated baseline | commit, tree, subject and clean initial worktree | exact Git inspection | `PASS` |
| Composition Architecture | imports one public function from each certified layer | source inspection | `PASS` |
| Composition Flow | G67-02 -> G67-03 -> G67-04 | ordered spy trace | `PASS` |
| Evidence Boundary | absolute scope, explicit roots, exact selectors | focused positive and negatives | `PASS` |
| no implicit discovery | no defaults, globs, scans, guessing or automatic selection | source inspection and negatives | `PASS` |
| relative path rejection | scope/path explicitness validator | focused negative | `PASS` |
| wildcard rejection | four wildcard markers | focused negatives | `PASS` |
| ambiguous input rejection | duplicate adapter/selector and exact selector closure | focused negatives | `PASS` |
| real Journey | current G67-02 fixture through composition | 35 Runtime Events and 14 Decisions | `PASS` |
| immutable Query Interface | G67-03 metadata source hash | repeated exact identity | `PASS` |
| deterministic output | repeated G67-04 Summary | byte equality | `PASS` |
| evidence immutability | every evidence file before/after two invocations | SHA-256 snapshot equality | `PASS` |
| in-process CLI | `composition.main(...)` | current final-Certification state | `PASS` |
| repository launcher | executable `./cro` | validation query, status 0 | `PASS` |
| passivity/source isolation | no forbidden imports/writes | static and dynamic checks | `PASS` |
| focused G67-05 tests | new test module | pytest | `14 passed` |
| G67-04 regression | complete CLI adapter module | pytest | `21 passed` |
| G67-03 regression | complete Query Interface module | pytest | `13 passed` |
| G67-02 regression | complete passive core module | pytest | `14 passed` |
| governance regression | `tests/test_governance_conformance.py` | pytest | `5 passed` |
| governance conformance | read-only engine | 20 passed, 0 failed, 0 warnings, 0 critical violations, `CONFORMANT` | `PASS` |
| Python compilation | composition, launcher and focused test | `py_compile` | `PASS` |
| executable mode | repository `cro` | filesystem mode inspection | `755` |
| document consistency | required sections, five Reuse answers and one verdict | deterministic review | `PASS` |
| whitespace integrity | tracked and new-file checks | `git diff --check` and no-index checks | `PASS` |

# 5. Repository Mutation Summary

Added files:

- `aigol/runtime/constitutional_runtime_observatory/composition.py` — bounded
  explicit-input orchestration of G67-02, G67-03, and G67-04.
- `cro` — executable repository-local passive observation launcher.
- `tests/test_g67_05_constitutional_runtime_observatory_passive_composition.py`
  — focused evidence-boundary, composition, passivity, determinism, and
  launcher tests.
- `docs/governance/G67_05_CONSTITUTIONAL_RUNTIME_OBSERVATORY_PASSIVE_COMPOSITION_REPORT_V1.md`
  — G48 implementation evidence and verdict.

Unchanged subsystems:

- G67-02 core/catalog/topology and every source-owner reconstructor.
- G67-03 Query Interface and public contracts.
- G67-04 CLI Transport Adapter and rendering.
- All existing production/compatibility CLI, CHE, HIC, Conversation, Semantic
  Slot, CWM, Objective, Platform, Governance, Authorization, Worker, provider,
  execution, result, Replay, termination, Certification, mutation, persistence,
  schema, policy, baseline, PCBV31, deployment, and external adapter behavior.

API compatibility:

- Existing APIs and exports are byte-unchanged.
- G67-05 adds a separate module and launcher without changing package-root
  imports.
- Complete G67-02, G67-03, and G67-04 focused regressions pass.

Boundary preservation:

- The passive launcher is not a Human or production entry.
- Only explicit authenticated evidence references enter G67-02.
- No output or internal CRO value is persisted or authority-bearing.
- Fixture creation and all dynamic observation use pytest temporary roots.

Unrelated pre-existing changes:

- None. The worktree was clean at implementation start.

# 6. Certification Verdict

CONSTITUTIONAL_RUNTIME_OBSERVATORY_PASSIVE_COMPOSITION_ESTABLISHED
