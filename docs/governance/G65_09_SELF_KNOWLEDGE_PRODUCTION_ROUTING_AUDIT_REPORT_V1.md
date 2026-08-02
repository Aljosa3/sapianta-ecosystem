# 1. Implementation Summary

Generation: G65-09

Report identity: G65_09_SELF_KNOWLEDGE_PRODUCTION_ROUTING_AUDIT_REPORT_V1

Constitutional baseline: `CONSTITUTIONAL_GOVERNANCE_CLOSED` and
`SELF_KNOWLEDGE_INTENT_ROUTING_ESTABLISHED`.

Implementation contracts: G48 Constitutional Evidence Reporting Standard V1
and the certified G65-01 through G65-07 Self Knowledge architecture,
manifest, snapshot, validation, query, integration, and intent-routing
contracts.

Audited repository identity: `bad94cc5` (`G65-07: establish Self Knowledge
intent routing`).

Reporting date: 2026-08-02.

Objective:

Perform a repository-wide, read-only trace of the production `./aicli` path
for the exact request `Show architecture.` and determine whether G65-07 is
active, which knowledge runtimes execute, which owner produces the final
response, and why an observed output could identify
`PLATFORM_KNOWLEDGE_RUNTIME`.

Audit scope:

- Trace the repository-local executable, CLI dispatch, request submission,
  Platform Core project-services boundary, G65-07 classifier, Platform Query
  Router, G65-06 integration, G65-05 query, presentation, and AiCLI renderer.
- Execute the current production launcher with a temporary runtime root and
  inspect its recorded project-context artifact.
- Compare the current path with the immediately preceding certified G65-06
  code identity `a7263f7a` in an isolated `/tmp` archive.
- Make no runtime, routing, classifier, knowledge, Conversation, governance,
  or execution modification.

Modified modules:

- `docs/governance/G65_09_SELF_KNOWLEDGE_PRODUCTION_ROUTING_AUDIT_REPORT_V1.md`
  — this read-only G48 audit report.

Intentionally unchanged modules:

- AiCLI; Conversation; Platform Core project services; G65-02 through G65-07
  runtimes; Platform Query Router; Platform Knowledge; canonical
  presentation; Development Governance; Reuse Proof; Authorization; Replay;
  Worker; provider selection; and execution owners.

Primary finding:

At audited HEAD, the certified G65-07 classifier is used by the default
repository-local production `./aicli` path. The exact request is classified
`SELF_KNOWLEDGE_QUERY`, invokes the G65-06 Platform Core response owner and
the G65-05 Self Knowledge Query Runtime, and renders with
`selected_service: SELF_KNOWLEDGE_QUERY_RUNTIME`. Platform Knowledge is not
invoked and does not wrap Self Knowledge.

The reported `selected_service: PLATFORM_KNOWLEDGE_RUNTIME` is the
deterministic result of the generic pre-G65-07 Platform Query Router branch.
It is not the result emitted by the audited current `./aicli` path. If that
line was observed after G65-07 certification, the executed process did not
use the audited classifier path or did not load the audited code identity.

# 2. Code Evidence

## Production Entry Point

The repository-local executable contains only:

```python
from aigol.cli.aicli import main

if __name__ == "__main__":
    raise SystemExit(main())
```

Source: `aicli`, lines 1-8.

With no mode argument, `aigol.cli.aicli.main` calls
`run_reference_uhi_session(...)`. A composed request reaches
`prepare_unified_human_interface_project_context(...)` with
`interface_name="aicli"`.

Sources: `aigol/cli/aicli.py`, lines 1918-1957 and 1473-1504.

No separate `aicli` executable is installed on the audited shell `PATH`.
Python import inspection resolved the CLI, project-services, and classifier
modules to this repository under `/home/pisarna/work/sapianta`.

## Complete Current Execution Path

The authenticated current path is:

```text
./aicli
  -> aigol.cli.aicli.main
  -> run_reference_uhi_session
  -> _submit_composed_request
  -> prepare_unified_human_interface_project_context
  -> classify_self_knowledge_request
  -> validate_self_knowledge_request_classification
  -> _classify_new_operational_turn
  -> route_platform_query
  -> _route_preclassified_self_knowledge_request
  -> route_explicit_self_knowledge_query
  -> run_platform_core_self_knowledge_query
  -> build and validate authenticated snapshot
  -> execute_self_knowledge_query
  -> validate_self_knowledge_query_response
  -> present_platform_response
  -> _self_knowledge_presentation
  -> AiCLI _render_read_only_result
```

At the project-services boundary, classification occurs before admission:

```python
request_classification = validate_self_knowledge_request_classification(
    classify_self_knowledge_request(message)
)
if request_classification["request_classification"] == DEVELOPMENT_OBJECTIVE:
    admission_precedence = determine_platform_core_admission_precedence(...)
```

For `Show architecture.`, the exact closed map returns
`SELF_KNOWLEDGE_QUERY`, `ARCHITECTURE`, and canonical request
`/self-knowledge ARCHITECTURE`. Project services binds the existing Platform
Query Router and leaves Project Objective inference unavailable.

Sources: `aigol/runtime/self_knowledge_request_classification.py`, lines
42-136; `aigol/runtime/platform_core_project_services.py`, lines 350-433 and
1080-1142.

## Query Router Precedence

`route_platform_query` validates or constructs the G65-07 classification at
the start of the function. Any classification other than
`DEVELOPMENT_OBJECTIVE` returns through
`_route_preclassified_self_knowledge_request`:

```python
if classification["request_classification"] != DEVELOPMENT_OBJECTIVE:
    return _route_preclassified_self_knowledge_request(...)
```

The generic Platform Knowledge probe appears only after that return:

```python
knowledge_probe = query_platform_knowledge(...)
```

It is therefore unreachable for the exact supported request when G65-07 is
loaded.

Source: `aigol/runtime/platform_query_router.py`, lines 457-510.

## Self Knowledge Invocation

The preclassified router calls the existing G65-06 exact entry. G65-06 loads
and validates the G65-02 manifest, builds the G65-03 snapshot, validates it
through G65-04, creates a G65-05 request, invokes
`execute_self_knowledge_query`, and validates the response.

The current recorded artifact proves these concrete identities:

| Field | Recorded value |
|---|---|
| classification | `SELF_KNOWLEDGE_QUERY` |
| selected query class | `SELF_KNOWLEDGE_QUERY` |
| selected service | `SELF_KNOWLEDGE_QUERY_RUNTIME` |
| service artifact | `SELF_KNOWLEDGE_PLATFORM_CORE_RESPONSE_V1` |
| query subject | `ARCHITECTURE` |
| nested query artifact | `SELF_KNOWLEDGE_QUERY_RESPONSE_V1` |
| presentation service | `SELF_KNOWLEDGE_QUERY_RUNTIME` |
| presentation source | `SELF_KNOWLEDGE_PLATFORM_CORE_RESPONSE_V1` |
| Project Objective | `null` |
| admission precedence | `null` |

The router classification evidence contains no
`platform_knowledge_query_classification` field on this early branch.

## Platform Knowledge Relationship

Platform Knowledge does not wrap Self Knowledge. The two response types have
separate presentation adapters and owners:

- Platform Knowledge returns `PLATFORM_KNOWLEDGE_RESPONSE_ARTIFACT_V1`.
- Self Knowledge integration returns
  `SELF_KNOWLEDGE_PLATFORM_CORE_RESPONSE_V1` containing a validated
  `SELF_KNOWLEDGE_QUERY_RESPONSE_V1`.

The canonical presentation layer dispatches the Self Knowledge artifact
directly to `_self_knowledge_presentation`. There is no Platform Knowledge
envelope inside the current service response and no call from Platform
Knowledge to the Self Knowledge Query Runtime.

## Final Response Ownership

Ownership is layered rather than transferred:

- G65-07 Request Classification owns the deterministic intent classification.
- Platform Query Router owns the selected service and router envelope.
- G65-06 Platform Core/Conversation integration owns manifest/snapshot/query
  orchestration and the Platform Core response envelope.
- G65-05 Self Knowledge Query Runtime owns the authenticated subject
  projection and facts.
- Canonical Platform Presentation Layer owns the final structured human-facing
  presentation.
- AiCLI only prints `selected_read_only_service`, presentation status, and
  presentation summary; it owns no semantic response, routing, or authority.

For the question “which runtime owns the final response,” the semantic answer
is owned by the Self Knowledge Query Runtime, while the final terminal
presentation is owned by the Canonical Platform Presentation Layer. Platform
Knowledge owns neither in the current path.

## Explanation of the Reported Platform Knowledge Service

An isolated call to the immediately preceding G65-06 generic router at commit
`a7263f7a` with the same exact text produced:

```text
selected_query_class: ARCHITECTURAL_KNOWLEDGE
selected_service: PLATFORM_KNOWLEDGE_RUNTIME
service_artifact_type: PLATFORM_KNOWLEDGE_RESPONSE_ARTIFACT_V1
```

That is the expected generic routing result before the G65-07 early
classification branch. The current commit diff adds the classifier at both
the project-services boundary and the top of `route_platform_query`, before
`query_platform_knowledge`.

The default G65-06 `./aicli` path itself treated the period-terminated request
as governed work requiring architectural clarification; it did not emit the
reported selected-service line. Therefore the line
`selected_service: PLATFORM_KNOWLEDGE_RUNTIME` proves use of the generic
router result, but does not by itself identify which external launcher or
process invoked that router.

At current audited HEAD, the same direct router call and the complete
production launcher both select `SELF_KNOWLEDGE_QUERY_RUNTIME`. A post-G65-07
observation of Platform Knowledge is consequently consistent with one of:

- a process started from a pre-G65-07 or partially updated code tree;
- an executable/import path different from repository-local `./aicli`;
- a caller that bypassed the certified new-turn project-services/classifier
  path; or
- request bytes different from the exact supported closed form.

The repository evidence proves the mismatch boundary but cannot determine the
identity or environment of an external process that was not supplied as
evidence.

# 3. Constitutional Self-Assessment

## Verified

- The current default repository-local AiCLI launcher invokes G65-07 before
  Project Objective inference.
- The exact request produces the hash-bound classification
  `SELF_KNOWLEDGE_QUERY` with subject `ARCHITECTURE`.
- The complete current launcher prints
  `selected_service: SELF_KNOWLEDGE_QUERY_RUNTIME`,
  `PRESENTATION_READY`, and the non-authoritative authenticated Architecture
  summary.
- The current recorded project context contains no Project Objective,
  admission precedence, Development Governance transition, provider call,
  Worker call, or repository mutation.
- G65-05 is invoked, as proven by the nested
  `SELF_KNOWLEDGE_QUERY_RESPONSE_V1` artifact.
- Platform Knowledge is not invoked on the supported branch; its generic probe
  occurs after the G65-07 early return and its classification evidence is
  absent from the trace.
- Platform Knowledge does not wrap Self Knowledge. The recorded service and
  presentation source are the G65-06 Self Knowledge integration artifact.
- The pre-G65-07 generic router independently reproduces the reported
  `PLATFORM_KNOWLEDGE_RUNTIME` selection and Platform Knowledge artifact.
- Selected G65-06, G65-07, router, presentation, and governance conformance
  regressions passed 71 tests.

## Not Verified

- No external deployment, long-running shell process, installed package,
  container image, or server filesystem was supplied for inspection. This
  audit cannot identify the exact process that emitted the reported output.
- The current shell has no `aicli` command on `PATH`; only repository-local
  `./aicli` was available and audited.
- This audit does not characterize `aicli conversation-v2`,
  `conversation-execute-v2`, or the separate `aigol conversation` command as
  aliases of the default production path. They are distinct entry modes.
- The G65-06 comparison was executed from an isolated Git archive in `/tmp`
  with the current non-versioned `sapianta_system` dependency supplied on
  `PYTHONPATH`; no repository file was changed.
- No implementation or deployment repair was authorized or performed.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| Complete default AiCLI path | Launcher, `main`, submission, project services, router, integration, query, presentation, renderer | Static call-chain trace | `PASS` |
| Request Classification invoked | Recorded classification artifact/hash and project-services source | Current `./aicli` production trace | `PASS` |
| Self Knowledge Query Runtime invoked | Nested `SELF_KNOWLEDGE_QUERY_RESPONSE_V1` | Recorded project-context inspection | `PASS` |
| Platform Knowledge invocation status | Early return precedes `query_platform_knowledge`; generic classification evidence absent | Source ordering and recorded artifact | `NOT_INVOKED` |
| Platform Knowledge wrapping status | Self Knowledge service/presentation source contain no Platform Knowledge response | Artifact-type inspection | `DOES_NOT_WRAP` |
| Final response ownership | G65-05 facts, G65-06 envelope, canonical presentation, thin AiCLI renderer | Owner-bound call-chain review | `CHARACTERIZED` |
| Current production selected service | `./aicli` with exact request and temporary runtime root | `SELF_KNOWLEDGE_QUERY_RUNTIME` and `PRESENTATION_READY` | `PASS` |
| Reported Platform Knowledge explanation | G65-06 generic router at `a7263f7a` | Reproduced `ARCHITECTURAL_KNOWLEDGE` / `PLATFORM_KNOWLEDGE_RUNTIME` | `CHARACTERIZED` |
| Current direct router | G65-07 early classification at `bad94cc5` | Exact direct route selects Self Knowledge | `PASS` |
| Regression compatibility | G65-06, G65-07, router, presentation, conformance suites | Selected pytest command — 71 passed | `PASS` |
| Governance conformance | Existing read-only conformance owner | `python -m runtime.governance.governance_conformance_engine` | `PASS` |
| Runtime implementation changes | None authorized | Git diff review | `NOT_APPLICABLE` |
| Report whitespace integrity | G65-09 report | `git diff --check` plus new-file check | `PASS` |

# 5. Repository Mutation Summary

Modified files:

- `docs/governance/G65_09_SELF_KNOWLEDGE_PRODUCTION_ROUTING_AUDIT_REPORT_V1.md`
  — read-only audit evidence only.

Unchanged subsystems:

- AiCLI; Conversation; Platform Core; Request Classification; Self Knowledge
  manifest, snapshot, validation, query, and integration owners; Platform
  Knowledge; presentation; Development Governance; Reuse Proof;
  Authorization; Replay; Worker; provider selection; and execution.

API compatibility:

- No API, schema, route, classifier, knowledge projection, presentation,
  provider, Worker, authorization, Replay, governance, or execution behavior
  changed.

Boundary preservation:

- Production and historical comparison runs wrote only temporary trace data
  below `/tmp`. They invoked no provider or Worker and made no repository
  runtime mutation.
- This generation characterizes the repository and observed routing mismatch;
  it does not repair, redesign, deploy, restart, or replace any owner.

Unrelated pre-existing changes:

- None observed at audit start.

# 6. Certification Verdict

SELF_KNOWLEDGE_PRODUCTION_ROUTING_CHARACTERIZED
