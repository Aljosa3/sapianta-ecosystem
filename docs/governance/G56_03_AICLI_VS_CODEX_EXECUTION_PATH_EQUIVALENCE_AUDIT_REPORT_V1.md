# 1. Implementation Summary

Generation: G56-03

Report identity:
G56_03_AICLI_VS_CODEX_EXECUTION_PATH_EQUIVALENCE_AUDIT_REPORT_V1

Reporting date: 2026-07-31

Constitutional baseline:
REAL_TERMINAL_MULTI_TURN_WORKFLOW_CHARACTERIZED

Authenticated repository anchor:
bc85641eb9a49bdde5a6fc902a85adc11d8ce894

Implementation contracts:

- G48 Constitutional Evidence Reporting Standard V1
- G11-05A Codex Worker Platform Integration Architecture Review V1
- G11-06 Codex Worker Platform Integration Implementation V1
- G14-30 Canonical Human Interface Runtime Entry Service V1
- G54-09 Platform Core Admission Precedence Implementation Report V1
- G56-01 End-to-End AiCLI Development Flow Validation Report V1
- G56-02 Real Terminal Multi-Turn Development Characterization Report V1

Objective:

Determine whether a real terminal AiCLI request and a Codex-driven development
request enter and traverse the same certified Platform Core pipeline, identify
the earliest divergence, and assess its constitutional effect without changing
either path.

Implementation scope:

- Traced the real AiCLI terminal entry from argument parsing and stdin through
  Platform Core project services, Objective inference, Development Governance,
  Human Interface Runtime, approval, Worker activation, completion, and Replay.
- Distinguished the external Codex development surface from the separately
  certified `codex-execution` Worker and `codex-cognition` Provider identities.
- Traced the governed Codex Worker from existing approved execution lineage to
  downstream Authorization, fixed subprocess dispatch, transport receipt, and
  Replay.
- Executed one real PTY-backed AiCLI request in an isolated runtime root,
  exercised the same request through the bounded Codex synthesis preflight,
  and re-executed 52 adjacent deterministic tests.
- Compared transport, multiline handling, normalization, session state,
  workspace initialization, configuration, approval, permissions, evidence,
  and runtime ownership.

Modified modules:

- `docs/governance/G56_03_AICLI_VS_CODEX_EXECUTION_PATH_EQUIVALENCE_AUDIT_REPORT_V1.md`:
  this evidence-only constitutional audit.

Intentionally unchanged modules:

- AiCLI, Human Interface Runtime, and Platform Core.
- Objective inference, Development Governance, capability resolution, and
  admission precedence.
- Conversation Boundary and Conversation Working Memory.
- Authorization, Worker lifecycle, completion adapters, and Replay.
- PCBV31 and all constitutional specifications.
- Codex Provider and Worker registration and activation contracts.

Architectural boundaries preserved:

- The external Codex development surface is not reclassified as a certified
  Unified Human Interface or as the registered Codex Worker.
- The registered Codex Worker remains downstream of Platform Core,
  Development Governance, human approval, and Authorization.
- AiCLI remains transport and presentation; observed output states
  `aicli_authorizes: False`, `aicli_executes: False`, and
  `aicli_owns_replay: False`.
- The dynamic terminal request was canceled before approval, and the injected
  Worker runner used by tests performed no real Codex process or repository
  mutation.

# 2. Code Evidence

No runtime code was added or changed. Exact existing excerpts and the bounded
execution evidence follow. Unrelated source lines are omitted.

## Public API

The real terminal AiCLI entry is `aigol/cli/aicli.py:1892`. It parses a
versioned set of terminal inputs and enters the reference UHI session:

```python
def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.mode == "submit":
        run_reference_uhi_submit_session(
            session_id=args.session_id,
            created_at=args.created_at,
            runtime_root=args.runtime_root,
            workspace=args.workspace,
            input_reader=input,
            artifact_references=args.artifact_reference,
        )
        return 0
    run_reference_uhi_session(
        session_id=args.session_id,
        created_at=args.created_at,
        runtime_root=args.runtime_root,
        workspace=args.workspace,
        artifact_references=args.artifact_reference,
    )
    return 0
```

`aigol/cli/aicli.py:944` reads the complete submit payload from stdin, while
`aigol/cli/aicli.py:1456` normalizes line endings and removes only leading and
trailing blank lines:

```python
    reader = sys.stdin.read if stdin_reader is None else stdin_reader
```

```python
def _normalize_submit_request(raw_request: Any) -> str:
    text = str(raw_request).replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)
```

No repository function was found that registers an external Codex
conversation as a peer `interface_name="codex"` UHI entry. The repository's
Codex public runtime entry is instead the downstream
`activate_bounded_codex_worker` function described below.

## Orchestration Entry Point

The actual AiCLI order begins with Platform Core project services. At
`aigol/cli/aicli.py:1487`, `_submit_composed_request` calls Platform Core
directly before the later Human Interface Runtime preflight and approval calls:

```python
    message = "\n".join(compose_buffer)
    project_context = prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id=session,
        message=message,
        runtime_root=root,
        workspace=workspace_path,
        created_at=created,
        explicit_canonical_artifact_references=artifact_references,
    )
```

The common certified Human Interface entry at
`aigol/runtime/human_interface_runtime_entry_service.py:139` is callable by a
UHI only when that interface explicitly invokes it:

```python
def run_human_interface_runtime_entry(
    *,
    interface_name: str,
    session_id: str,
    human_requests: list[str],
    created_at: str,
    runtime_root: str | Path,
    workspace: str | Path,
    governed_runtime_runner: GovernedRuntimeRunner,
```

The repository-certified Codex Worker enters at
`aigol/runtime/codex_worker_activation_binding_runtime.py:362`, after governed
execution and execution-candidate captures already exist:

```python
def activate_bounded_codex_worker(
    *,
    activation_review_artifact: dict[str, Any],
    governed_execution_capture: dict[str, Any],
    execution_candidate_capture: dict[str, Any],
    human_decision: str,
    decided_by: str,
    decided_at: str,
    session_root: str | Path,
    workspace: str | Path,
    replay_dir: str | Path,
    runner: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    """Consume one exact third approval and invoke the existing Codex adapter once."""
```

These entrypoints are neither identical nor peers. AiCLI creates upstream
governed context; the Codex Worker consumes already-governed downstream
lineage.

## Semantic Reductions

Platform Core Objective inference is a repository-owned semantic reduction.
`aigol/runtime/platform_project_objective_inference.py:55` normalizes the
request, derives the subject, outcomes, work type, ambiguity, and sufficiency,
then emits a replay-visible Objective artifact:

```python
    prompt = _require_string(request, "request")
    normalized = " ".join(prompt.split())
    lowered = normalized.lower()
    intent = development_intent if isinstance(development_intent, dict) else {}
    workspace = workspace_state if isinstance(workspace_state, dict) else {}
    guidance = project_guidance if isinstance(project_guidance, dict) else {}
```

```python
    artifact = {
        "artifact_type": PLATFORM_PROJECT_OBJECTIVE_INFERENCE_ARTIFACT_V1,
        "runtime_version": PLATFORM_PROJECT_OBJECTIVE_INFERENCE_VERSION,
        "source_request": prompt,
        "source_request_hash": replay_hash(prompt),
        "canonical_project_objective": canonical_objective,
        "objective_status": status,
        "objective_sufficient": sufficient,
        "clarification_required": not sufficient,
```

By contrast, the Codex Worker preflight at
`aigol/runtime/codex_worker_activation_binding_runtime.py:112` performs a
bounded transport transformation, not Objective inference:

```python
    raw = _required(original_request, "original_request")
    final = f"{CODEX_SYNTHESIS_PREFIX}{raw}"
    within_bound = len(final) <= CODEX_SYNTHESIS_MAXIMUM_CHARACTER_COUNT
```

The fixed values are `CODEX_SYNTHESIS_PREFIX = "runtime validation: "` and
`CODEX_SYNTHESIS_MAXIMUM_CHARACTER_COUNT = 240`. The preflight then constructs
a bounded Codex handoff prompt. It does not call Objective inference,
Development Governance, or capability selection.

## Public Validators

The Codex Worker does not receive execution authority from selection or from
its prompt. At `aigol/runtime/codex_worker_activation_binding_runtime.py:398`,
activation requires the exact third approval, reconstructs lineage, performs
separate downstream Authorization, and rejects any non-authorized result:

```python
    if str(human_decision).strip().upper() != "APPROVE":
        raise FailClosedRuntimeError("Codex activation requires an exact third APPROVE decision")
```

```python
    authority = authorize_downstream_execution(
        create_execution_authorization_request(
            handoff_package=handoff,
            approved_by="human",
            approval_timestamp=_required(decided_at, "decided_at"),
        )
    )
    if authority.get("status") != "AUTHORIZED":
        raise FailClosedRuntimeError("bounded Codex execution authorization was rejected")
```

The bounded dispatch at
`sapianta_system/runtime/codex_execution_adapter/governed_codex_execution_dispatch.py:47`
uses one fixed argument vector, captured pipes, no shell, and a finite timeout:

```python
        completed = runner(
            list(command),
            capture_output=True,
            text=True,
            shell=False,
            timeout=timeout_seconds,
        )
```

The activation binding independently verifies the exact command
`["codex", "exec", handoff["codex_prompt"]]`, `shell=False`, and the 60-second
timeout. These are Worker dispatch controls, not an external Codex human-entry
contract.

## Canonical Data Models

The AiCLI execution created these repository-owned evidence classes before
approval:

- `PLATFORM_CORE_ADMISSION_PRECEDENCE_ARTIFACT_V1`;
- `PLATFORM_CORE_OPERATIONAL_TURN_BINDING_ARTIFACT_V1`;
- `PLATFORM_CORE_PROJECT_OBJECTIVE_INFERENCE_ARTIFACT_V1`;
- Development Governance integration and implementation-turn artifacts;
- durable governed-work evidence;
- UHI project-services context and workspace-state artifacts;
- G31 synthesis preflight evidence presented to the human.

The governed Codex Worker uses distinct downstream models:

- bounded Codex synthesis preflight and handoff package;
- Codex Worker activation review and approval;
- execution-authorization request and authority token;
- Codex execution request;
- bounded dispatch response and transport receipt;
- activation Replay reference and reconstruction result.

The external Codex product conversation and tool-approval records are not
instances of these SAPIANTA models and are not accepted as substitutes for
them.

## Deterministic Algorithms

### Interpretation boundary

The term “Codex execution path” has two materially different meanings in this
repository:

1. **External Codex development surface** — the human sends a prompt to Codex,
   which operates through its product-managed conversation and tool transport.
   No repository entry adapter automatically turns that message into a
   SAPIANTA Objective, Development Governance bundle, Authorization artifact,
   Worker request, or Replay record.
2. **Certified Codex Worker** — `codex-execution` is a registered downstream
   Worker. It may be activated only after Platform Core and Development
   Governance have produced approved execution lineage.

The audit compares AiCLI to both so that an external development session is
not mistaken for certified Worker activation.

### AiCLI sequence

```text
Human
  -> terminal PTY / stdin
  -> argparse: aigol.cli.aicli.main
  -> run_reference_uhi_submit_session
  -> line-ending and edge-blank normalization
  -> _submit_composed_request
  -> Platform Core project services
       -> admission precedence
       -> development-intent resolution
       -> Objective inference
       -> capability discovery/composition
       -> Development Governance
       -> durable governed work
       -> replay-visible project/workspace evidence
  -> Human Interface Runtime for G31 preflight and approval
  -> separate human decisions
  -> governed execution and Worker candidate
  -> separate Authorization
  -> Worker dispatch and execution
  -> completion/result capture
  -> Replay reconstruction
  -> HIR return
  -> AiCLI stdout presentation
```

The observed G56-03 terminal run stopped at human `/cancel`; the downstream
half is demonstrated by the adjacent deterministic activation and
end-to-end tests.

### External Codex development sequence

```text
Human
  -> Codex product/API conversation transport
  -> product-managed prompt and workspace context
  -> Codex agent
  -> product-managed tool permission checks
  -> direct workspace tools / commands
  -> product conversation result
```

There is no automatic transition from this path into
`prepare_unified_human_interface_project_context` or
`run_human_interface_runtime_entry`. Product conversation history and tool
logs therefore do not constitute SAPIANTA Objective, Authorization, Worker, or
Replay evidence.

### Certified Codex Worker sequence

```text
Existing approved governed-execution lineage
  -> Human Interface Runtime activation review
  -> exact third APPROVE
  -> activate_bounded_codex_worker
  -> lineage and workspace reconstruction
  -> bounded synthesis preflight and handoff
  -> downstream execution Authorization
  -> fixed ["codex", "exec", bounded_prompt] request
  -> captured stdout/stderr; shell=False; 60-second timeout
  -> transport receipt and result validation
  -> activation Replay reconstruction
  -> later completion/outcome review
```

This path does not accept an ungoverned human/Codex conversation as its input.

### Complete execution-path comparison

| Stage | Real terminal AiCLI | External Codex development | Certified Codex Worker | Finding |
|---|---|---|---|---|
| Human / prompt | Human request read from terminal | Human message received by the Codex product | No new human prompt; consumes approved lineage | Different input ownership |
| Transport | PTY/stdin, CLI arguments, stdout | Product/API conversation and tool transport | Fixed subprocess argv with captured stdout/stderr; no stdin conversation | Different |
| Entry | `aigol.cli.aicli.main` | No SAPIANTA repository entrypoint | `activate_bounded_codex_worker` after HIR review | Different |
| HIR | Explicitly invoked for G31 preflight/decisions and return | Not automatically invoked | Invoked upstream; Worker does not own it | Different roles |
| Platform Core | Project services called directly by AiCLI | Not automatically invoked | Prior output is consumed as lineage | Not identical |
| Objective inference | `infer_platform_project_objective` | No SAPIANTA Objective artifact | Does not infer Objective | Not identical |
| Development Governance | Produces pre-planning and durable-work evidence | Not automatically invoked | Consumes governed evidence | Not identical |
| Capability selection | Platform Core discovery/composition | No certified selection artifact | Worker identity/candidate already selected | Not identical |
| Authorization | AiCLI does not authorize; later runtime owner does | Product tool approval is not SAPIANTA Authorization | Separate downstream Authorization required | Constitutionally distinct |
| Worker dispatch | Delegated to Worker runtime | Direct product tools are not a SAPIANTA Worker dispatch | Fixed `codex exec` dispatch | Not identical |
| Completion | HIR/AiCLI presents governed result | Product conversation response | Transport/result evidence feeds later completion review | Different |
| Replay | Session-root immutable SAPIANTA evidence | Product history is not SAPIANTA Replay | Activation/transport Replay under governed session | Not identical |

### Entrypoint inventory

| Surface | Exact entrypoint | Input artifact | Output artifact |
|---|---|---|---|
| AiCLI terminal | `aigol.cli.aicli.main` -> `run_reference_uhi_submit_session` | CLI args plus complete stdin request | Platform Core session evidence and terminal presentation |
| Platform Core project services | `prepare_unified_human_interface_project_context` | Interface, session, message, runtime root, workspace, time, optional artifact references | Project context, Objective, admission, governance, and workspace Replay |
| Certified HIR | `run_human_interface_runtime_entry` | Explicit UHI identity plus request/evidence/action | Runtime binding, approval, completion, and presentation captures |
| Codex synthesis | `preflight_codex_worker_synthesis` | Original governed request and optional Worker contract | Non-executing bounded handoff capture |
| Codex Worker | `activate_bounded_codex_worker` | Approved governed lineage, candidate, exact human decision | Authorized dispatch, receipt, activation Replay |
| External Codex conversation | Not repository-owned or registered as a SAPIANTA entrypoint | Product conversation message/context | Product-managed agent/tool result |

### Runtime ownership inventory

| Responsibility | Constitutional owner | AiCLI role | External Codex role | Certified Codex role |
|---|---|---|---|---|
| Transport/presentation | UHI surface | Owns terminal transport only | Own product surface | None |
| Admission, Objective, capability | Platform Core | Calls owner | No automatic call | Consumes result only |
| Development gating | Development Governance | Presents result | No automatic call | Consumes approved result |
| Execution authority | Authorization/Governance | No authority | Product approval is separate and non-equivalent | Must present valid authority token |
| Worker lifecycle/dispatch | Worker Platform | Delegates | Direct product tools are outside this owner | Registered Worker instance |
| Cognition | Provider Platform when governed | No provider authority | Product model outside SAPIANTA evidence | `codex-cognition` only when separately invoked as Provider |
| Completion | Worker/HIR completion owners | Presents | Product response | Supplies bounded Worker evidence |
| Replay | Replay owner | No ownership | Product logs do not replace Replay | Supplies replay-bound downstream evidence |

### Transport and context comparison

| Concern | AiCLI | External Codex | Certified Codex Worker |
|---|---|---|---|
| PTY/stdin | Real PTY and `sys.stdin.read` were exercised | Product-managed; not the AiCLI PTY | No interactive stdin; prompt is one argv element |
| Multiline input | Internal newlines preserved after CRLF normalization and edge-blank removal | Product message semantics are external | Synthesized multiline canonical prompt |
| CLI parsing | `argparse` owns session, time, runtime root, workspace, and artifact references | No AiCLI parsing | Fixed executable, `exec`, prompt, and timeout |
| Context preparation | Platform Core reads workspace/replay context | Product prepares its own conversation/workspace context | Receives an explicit governed Worker contract and lineage |
| Session lifecycle | Explicit session ID and runtime-root evidence | Product conversation lifecycle is separate | Bound to existing SAPIANTA session root and one-time approval |
| Workspace | Explicit CLI workspace; project state replayed | Product sandbox/workspace permissions | Exact approved current workspace is verified |
| Runtime configuration | Explicit CLI arguments; no relevant environment-variable reads found in audited modules | Product configuration is external | Constants: executable `codex`, timeout 60, prefix 20, limit 240 |
| Approval | Human `/approve` sequence; AiCLI itself does not authorize | Product tool permission is not SAPIANTA Authorization | Exact third approval plus downstream Authorization |
| Permissions | Constitutional runtime gates later execution | Product sandbox/tool permissions | No shell, fixed command, bounded capture, finite timeout, repository snapshot check |
| Persistence | Replay-visible JSON under session root | Product conversation history is not SAPIANTA Replay | Three activation Replay artifacts in the successful injected-runner test |

### Same-request dynamic evidence

Request:

```text
Implement a deterministic status summary in aigol/cli/aicli.py with focused tests.
```

AiCLI real-terminal observations:

- input size: 82 Unicode code points;
- G31 canonical prefix: 20;
- final preflight size: 102 of 240;
- Objective status: `PROJECT_OBJECTIVE_SUFFICIENT`;
- canonical Objective: `Resolve a deterministic status summary in
  aigol/cli/aicli through implementation as IMPLEMENTATION.`;
- Development Governance: `BOUNDED_PLANNING_PERMITTED`;
- human decision: `/cancel`;
- Worker execution: none;
- repository mutation: none;
- temporary evidence: eight JSON files, approximately 1.1 MiB, beneath
  `/tmp/g56_03_equivalence.dSITmv/runtime/G56-03-AICLI`.

Direct bounded Codex preflight observations for the same text:

- raw size: 82;
- fixed prefix: 20;
- final request size: 102 of 240;
- bounded Codex prompt size: 1,184;
- status: `SYNTHESIS_PREFLIGHT_READY`;
- process starts: 0;
- provider invoked: false;
- repository mutated: false;
- SAPIANTA Objective, Development Governance, capability-selection, and
  execution-authorization artifacts: absent; the handoff instead records that
  downstream execution authority is false.

The matching 82/102 character measurements show reuse of the same G31
preflight transformation. They do not show path equivalence: AiCLI reached the
preflight only after producing upstream Platform Core evidence, while direct
preflight began at the downstream synthesis boundary.

### Earliest divergence and root cause

The earliest divergence occurs at the first transport/entry boundary, before
Human Interface Runtime and before Objective creation:

- AiCLI binds terminal bytes to explicit SAPIANTA session, workspace, time,
  and Replay coordinates and calls Platform Core project services.
- An external Codex conversation is received through a separate product
  transport and has no repository adapter that calls those services.
- The certified Codex Worker is intentionally later still: it accepts only a
  bounded prompt derived from authenticated, already-approved execution
  lineage.

The architectural cause is role separation, not a different implementation of
the same entry. AiCLI is a UHI transport/presentation surface. Codex is
registered inside SAPIANTA as a downstream Provider and Worker, while the
external Codex development surface remains outside the certified UHI path.

### Constitutional impact and recommended corrective action

The certified AiCLI-to-Codex-Worker flow is constitutionally consistent: it
preserves Platform Core, Development Governance, Authorization, Worker, and
Replay ownership. The non-equivalence becomes constitutionally material only
if work performed through the external Codex surface is represented as though
it had traversed that pipeline. Such work lacks the required SAPIANTA
Objective, approval, Authorization, Worker, and Replay lineage.

No correction to the downstream Codex Worker is recommended. If future
constitutional equivalence is required for Codex-originated human
conversations, use one of these bounded approaches in a separately authorized
generation:

1. require the human to submit the work through AiCLI before Codex execution;
   or
2. add a certified Codex UHI admission adapter that records explicit interface,
   session, workspace, transport provenance, and message evidence, then invokes
   the existing Platform Core and HIR services before any tool execution.

Such an adapter must remain transport-only and must not move Objective,
Development Governance, Authorization, Worker, or Replay responsibility into
Codex. External Codex product logs must not be imported as authenticated
SAPIANTA evidence without a separate provenance and validation contract.

## Responsibility Boundaries

`docs/governance/G11_05A_CODEX_WORKER_PLATFORM_INTEGRATION_ARCHITECTURE_REVIEW_V1.md`
defines Codex as role-separated composition:

```text
1. Codex as non-authoritative cognition provider.
2. Codex as bounded Worker Platform execution worker.
```

It also defines the required Worker path as:

```text
Worker identity
->
Worker eligibility
->
Worker assignment
->
Governance authorization
->
Worker dispatch
->
Worker invocation
->
Completion or fail-closed result
->
Replay evidence
```

`docs/governance/G11_06_CODEX_WORKER_PLATFORM_INTEGRATION_IMPLEMENTATION_V1.md`
registers the distinct identities `codex-cognition` and `codex-execution` and
states that registration alone does not authorize dispatch or invocation.

The older repository-context specification also explicitly contrasts the
manual `Human -> ChatGPT -> Prompt -> Codex -> Copy/Paste -> Repository` path
with the replay-visible `Human -> ACLI -> Repository Context Runtime ->
Governed Development Workflow -> Replay` path. The current audit confirms
that this distinction still exists at the external Codex entry boundary.

# 3. Constitutional Self-Assessment

## Verified

- AiCLI and external Codex do not expose identical SAPIANTA entrypoints.
- AiCLI deterministically entered Platform Core project services and created
  Objective, Development Governance, durable-work, workspace, and Replay
  evidence before approval.
- The repository-certified Codex Worker begins after governed execution and
  Worker-candidate evidence already exists; it does not infer an Objective.
- Codex Worker execution requires a separate exact human decision and separate
  downstream Authorization.
- Terminal stdin, multiline normalization, CLI context, subprocess argv,
  stdout/stderr capture, shell prohibition, timeout, workspace, session,
  approval, and permission differences are characterized.
- The earliest divergence is the transport/entry boundary before HIR and
  Objective inference.
- The divergence is constitutionally expected role separation unless external
  Codex work is incorrectly claimed as certified Platform Core execution.
- The same-request terminal and synthesis-preflight measurements are
  deterministic and agree on the 82 raw, 20 prefix, and 102 final character
  counts.
- Fifty-two focused tests passed, including AiCLI submission, HIR entry,
  Objective inference, Development Governance integration, Codex registration,
  synthesis preflight, activation, Authorization, transport receipt, and Replay
  reconstruction behavior.
- No runtime or constitutional module changed.

## Not Verified

- The proprietary internal implementation of the external Codex product/API
  transport, conversation store, and backend approval service is not present
  in this repository. Its observable boundary is sufficient to establish that
  it is not the SAPIANTA AiCLI/HIR entry, but its private internals were not
  audited.
- A real network-backed `codex exec` process was not launched. The certified
  adapter was dynamically exercised with its injected deterministic runner so
  that the evidence-only audit could not mutate the repository or depend on an
  external service.
- No mutation-capable end-to-end development request was approved. Downstream
  behavior was validated through existing deterministic tests rather than by
  authorizing a real change.
- No constitutional equivalence adapter was designed or implemented.
- The repository conformance engine remains `PARTIALLY_CONFORMANT`: 18 checks
  passed and two pre-existing hook checks failed. It reports no critical
  violation, but the root pre-commit hook is missing and the system pre-commit
  hook lacks `promotion_gate_v02` and `check_layer_freeze`. This audit did not
  repair or hide that baseline drift.

# 4. Validation Matrix

Executed validation:

```text
python -m pytest -q \
  tests/test_g15_aicli_02_submission_mode.py \
  tests/test_g14_30_canonical_human_interface_runtime_entry_service_v1.py \
  tests/test_g21_02_platform_project_objective_inference.py \
  tests/test_g47_01d_development_governance_operational_integration.py \
  tests/test_g31_17b_governed_execution_to_codex_worker_activation_binding.py \
  tests/test_g11_codex_worker_platform_integration.py \
  tests/test_g31_20c_codex_synthesis_preflight.py
python -m pytest -q tests/test_governance_conformance.py
python -m runtime.governance.governance_conformance_engine
git diff --check
```

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| Complete AiCLI execution path | `aigol/cli/aicli.py`; Platform Core/HIR runtime; isolated terminal transcript | Executed real `python -m aigol.cli.aicli submit`; reviewed eight generated evidence files | PASS |
| Complete Codex path distinction | Codex activation runtime; execution adapter; G11-05A/G11-06 | Traced external surface boundary and certified downstream Worker separately | PASS |
| Identical runtime entrypoint determination | AiCLI `main`; HIR entry; Codex Worker activation | Repository search found no Codex peer UHI entry; exact functions inventoried | PASS |
| Platform Core service equivalence | `_submit_composed_request`; `activate_bounded_codex_worker` | Compared callers and required inputs | PASS |
| Objective-generation equivalence | Objective inference artifact versus Codex preflight capture | Same request produced Objective only through AiCLI/Platform Core | PASS |
| Development Governance equivalence | Development Governance replay files; Codex Worker lineage inputs | Same request produced governance evidence only on AiCLI path | PASS |
| Capability-selection equivalence | Platform Core project context; Codex Worker candidate input | Verified selection occurs upstream and is consumed, not repeated, by Worker | PASS |
| Authorization equivalence | activation binding exact approval and `authorize_downstream_execution` | Static review plus focused activation tests | PASS |
| Worker dispatch equivalence | fixed `codex exec` adapter and test runner capture | Verified external tool execution is not the same SAPIANTA Worker dispatch | PASS |
| Completion and Replay equivalence | AiCLI session artifacts; Codex receipt/reconstruction tests | Compared evidence owners and reconstructed downstream activation Replay | PASS |
| PTY, stdin/stdout, and multiline handling | AiCLI normalization; Codex dispatch code | Real PTY run plus exact static comparison | PASS |
| Context, session, workspace, configuration, and environment | CLI arguments; session root; fixed Codex constants; environment-read search | Reviewed audited modules; no relevant environment-variable reads found | PASS |
| Conversation persistence and approval workflow | AiCLI session model; product boundary; one-time Worker approval | Compared lifecycle and authority evidence | PASS |
| Earliest divergence | Sequence diagrams and entrypoint inventory | Determined divergence before HIR/Objective at transport entry | PASS |
| Constitutional impact | G11 role separation and runtime ownership inventory | Confirmed expected separation; identified false-certification risk | PASS |
| Corrective action | Bounded UHI-adapter/re-submit recommendations | Reviewed against existing owner boundaries; no implementation performed | PASS |
| Adjacent regression validation | Seven focused test modules and exact command above | 52 passed in 78.51 seconds | PASS |
| Governance conformance diagnostic and limitation visibility | Governance conformance tests and engine | 5 tests passed; engine remained deterministic/read-only/fail-closed with 18 passed checks, 2 known hook mismatches, and 0 critical violations | PASS |
| No repository mutation outside report | Git status and diff review | Runtime evidence isolated under `/tmp`; source tree unchanged | PASS |
| External Codex proprietary internals | Not repository-owned | Not required to establish repository entrypoint non-equivalence; limitation declared | NOT_APPLICABLE |

# 5. Repository Mutation Summary

Modified files:

- `docs/governance/G56_03_AICLI_VS_CODEX_EXECUTION_PATH_EQUIVALENCE_AUDIT_REPORT_V1.md`:
  added this evidence-only G48 report.

Unchanged subsystems:

- AiCLI, HIR, Platform Core, Objective, Development Governance, capability
  selection, Conversation Boundary, CWM, Authorization, Worker, completion,
  Replay, PCBV31, and Codex runtime integration.

API compatibility:

- No API, CLI option, schema, runtime configuration, transport, dispatch,
  Authorization, Worker, completion, or Replay contract changed.

Boundary preservation:

- External Codex remains outside the certified UHI path.
- The registered Codex identities remain non-authoritative Provider and
  downstream Worker roles.
- The report grants no execution authority and creates no evidence-import
  shortcut.
- Temporary execution evidence remains outside the repository under
  `/tmp/g56_03_equivalence.dSITmv`.

Unrelated pre-existing changes:

- None observed in the Git worktree. The conformance engine continues to expose
  the pre-existing root and system pre-commit hook drift declared under
  `Not Verified`.

# 6. Certification Verdict

AICLI_CODEX_EXECUTION_PATH_DIVERGENCE_CHARACTERIZED
